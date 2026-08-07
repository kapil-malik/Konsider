"""FastAPI application factory for the structured Konsider API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from konsider.api.dependencies import get_recommendation_service
from konsider.api.errors import register_exception_handlers
from konsider.api.models.common import ErrorResponse
from konsider.api.models.v2 import (
    CatalogV2Response,
    ComparisonV2Response,
    CountryDetailsV2Response,
    HealthV2Response,
    OpportunityFilterCatalogV2Response,
    RankingV2Response,
    TfcCatalogV2Response,
    TfcAssessmentSelectionRequest,
    V2ComparisonRequest,
    V2RankingRequest,
    V2WeightSelection,
)
from konsider.api.models.v3 import (
    CatalogV3Response,
    ComparisonV3Response,
    CountryDetailsV3Response,
    HealthV3Response,
    OpportunityFilterCatalogV3Response,
    RankingV3Response,
    TfcCatalogV3Response,
    V3RankingRequest,
)
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.settings import ApiSettings
from konsider.api.tfc_service import TfcApiService
from konsider.api.v2_service import RecommendationService
from konsider.api.v3_service import RecommendationServiceV3
from konsider.ingestion.current_release import CurrentReleaseError, CurrentReleaseRepository
from konsider.ingestion.phase7_release_publication import load_active_tfc_release

ERROR_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Invalid request"},
    500: {"model": ErrorResponse, "description": "Unexpected internal failure"},
    503: {"model": ErrorResponse, "description": "Active release unavailable"},
}


def _default_service_factory(settings: ApiSettings) -> RecommendationService:
    repository = CurrentReleaseRepository(settings.release_root)
    release = repository.load_active(settings.active_release_path)
    if release.manifest["status"] != "published":
        raise CurrentReleaseError("The active schema-5 release is not published.")
    if not release.validation["product_ready"]:
        raise CurrentReleaseError("The active schema-5 release is not product-ready.")
    opportunity_filters = (
        OpportunityFilterService.from_release(release.path, release.manifest)
        if "opportunity_filters" in release.manifest
        else OpportunityFilterService.empty()
    )
    try:
        tfc_release = load_active_tfc_release(settings.release_root, settings.active_release_path)
        tfc_service = (
            TfcApiService.from_published(tfc_release, release.manifest)
            if tfc_release is not None
            else TfcApiService.unavailable()
        )
    except Exception as exc:
        tfc_service = TfcApiService.unavailable(str(exc))
    return RecommendationService(release, opportunity_filters, tfc_service)


def _opportunity_filter_ids(payload: V2WeightSelection) -> list[str]:
    return (
        payload.opportunity_filters.required_filter_ids
        if payload.opportunity_filters is not None
        else []
    )


def _feasibility(payload: V2WeightSelection) -> dict | None:
    selection = payload.feasibility
    if selection is None or not selection.tfc_ids:
        return None
    context = {}
    for request_name, engine_name in (
        ("profile_context", "applicant"),
        ("household_context", "household"),
        ("scenario_context", "scenario"),
    ):
        layer = getattr(selection, request_name)
        if layer is not None:
            context[engine_name] = layer.model_dump(mode="json", exclude_unset=True)
    return {
        "tfc_ids": selection.tfc_ids,
        "mode": selection.mode,
        "context": context or None,
    }


def _protect_profile_response(response: Response, selection: TfcAssessmentSelectionRequest | None):
    if selection is not None and selection.tfc_ids:
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"


def create_app(
    settings: ApiSettings | None = None,
    service: RecommendationService | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.recommendation_service = None
        application.state.initialization_error = None
        try:
            application.state.recommendation_service = service or _default_service_factory(
                resolved_settings
            )
        except Exception as exc:
            application.state.initialization_error = exc
        yield

    logging.getLogger("konsider.api").setLevel(resolved_settings.log_level)
    application = FastAPI(
        title="Konsider API",
        version="3.0.0",
        description="Structured API over one immutable schema-current recommendation snapshot.",
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    register_exception_handlers(application)

    @application.middleware("http")
    async def private_post_responses(request, call_next):
        response = await call_next(request)
        if request.method == "POST" and request.url.path.startswith(("/api/v2/", "/api/v3/")):
            response.headers["Cache-Control"] = "private, no-store"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    if resolved_settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @application.get("/api/v2/health", response_model=HealthV2Response, include_in_schema=False)
    def health(current: RecommendationService = Depends(get_recommendation_service)):
        return HealthV2Response.model_validate(current.health())

    @application.get("/api/v2/catalog", response_model=CatalogV2Response, include_in_schema=False)
    def catalog(current: RecommendationService = Depends(get_recommendation_service)):
        return CatalogV2Response.model_validate(current.catalog())

    @application.get(
        "/api/v2/opportunity-filters",
        response_model=OpportunityFilterCatalogV2Response,
        include_in_schema=False,
    )
    def opportunity_filters(
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        return OpportunityFilterCatalogV2Response.model_validate(
            current.opportunity_filter_catalog()
        )

    @application.get("/api/v2/tfcs", response_model=TfcCatalogV2Response, include_in_schema=False)
    def tfcs(current: RecommendationService = Depends(get_recommendation_service)):
        return TfcCatalogV2Response.model_validate(current.tfc_catalog())

    @application.post(
        "/api/v2/rankings",
        response_model=RankingV2Response,
        response_model_exclude_unset=True,
        include_in_schema=False,
    )
    def rankings(
        payload: V2RankingRequest,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return RankingV2Response.model_validate(
            current.rank(
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                top_k=payload.top_k,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    @application.post(
        "/api/v2/comparisons",
        response_model=ComparisonV2Response,
        response_model_exclude_unset=True,
        include_in_schema=False,
    )
    def comparisons(
        payload: V2ComparisonRequest,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return ComparisonV2Response.model_validate(
            current.compare(
                payload.country_codes,
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    @application.post(
        "/api/v2/countries/{country_code}/details",
        response_model=CountryDetailsV2Response,
        response_model_exclude_unset=True,
        include_in_schema=False,
    )
    def country_details(
        country_code: str,
        payload: V2WeightSelection,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return CountryDetailsV2Response.model_validate(
            current.country_details(
                country_code.upper(),
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    @application.get(
        "/api/v3/health",
        response_model=HealthV3Response,
        responses={503: ERROR_RESPONSES[503]},
        summary="Check API v3 and active-release readiness",
    )
    def health_v3(current: RecommendationService = Depends(get_recommendation_service)):
        return HealthV3Response.model_validate(RecommendationServiceV3(current).health())

    @application.get(
        "/api/v3/catalog",
        response_model=CatalogV3Response,
        responses=ERROR_RESPONSES,
        summary="Retrieve criteria with uniform display metadata",
    )
    def catalog_v3(current: RecommendationService = Depends(get_recommendation_service)):
        return CatalogV3Response.model_validate(RecommendationServiceV3(current).catalog())

    @application.get(
        "/api/v3/opportunity-filters",
        response_model=OpportunityFilterCatalogV3Response,
        responses=ERROR_RESPONSES,
        summary="Retrieve catalog-grouped filters with uniform display metadata",
    )
    def opportunity_filters_v3(
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        return OpportunityFilterCatalogV3Response.model_validate(
            RecommendationServiceV3(current).opportunity_filter_catalog()
        )

    @application.get(
        "/api/v3/tfcs",
        response_model=TfcCatalogV3Response,
        responses=ERROR_RESPONSES,
        summary="Retrieve feasibility checks with uniform display metadata",
    )
    def tfcs_v3(current: RecommendationService = Depends(get_recommendation_service)):
        return TfcCatalogV3Response.model_validate(RecommendationServiceV3(current).tfc_catalog())

    @application.post(
        "/api/v3/rankings",
        response_model=RankingV3Response,
        response_model_exclude_unset=True,
        responses=ERROR_RESPONSES,
        summary="Rank countries using the API v3 display contract",
    )
    def rankings_v3(
        payload: V3RankingRequest,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return RankingV3Response.model_validate(
            RecommendationServiceV3(current).rank(
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                top_k=payload.top_k,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    @application.post(
        "/api/v3/comparisons",
        response_model=ComparisonV3Response,
        response_model_exclude_unset=True,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Compare countries using the API v3 display contract",
    )
    def comparisons_v3(
        payload: V2ComparisonRequest,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return ComparisonV3Response.model_validate(
            RecommendationServiceV3(current).compare(
                payload.country_codes,
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    @application.post(
        "/api/v3/countries/{country_code}/details",
        response_model=CountryDetailsV3Response,
        response_model_exclude_unset=True,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Retrieve country evidence using the API v3 display contract",
    )
    def country_details_v3(
        country_code: str,
        payload: V2WeightSelection,
        response: Response,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        _protect_profile_response(response, payload.feasibility)
        return CountryDetailsV3Response.model_validate(
            RecommendationServiceV3(current).country_details(
                country_code.upper(),
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                opportunity_filter_ids=_opportunity_filter_ids(payload),
                feasibility=_feasibility(payload),
            )
        )

    return application


app = create_app()
