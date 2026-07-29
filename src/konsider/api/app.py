"""FastAPI application factory for the versioned Konsider API."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from konsider.api.dependencies import (
    get_recommendation_service,
    get_v2_recommendation_service,
)
from konsider.api.errors import error_response, register_exception_handlers
from konsider.api.mappers import (
    catalog_response,
    comparison_response,
    country_metric_response,
    ranking_response,
)
from konsider.api.models.catalog import CatalogResponse, HealthResponse
from konsider.api.models.common import ErrorResponse
from konsider.api.models.countries import CountryMetricResponse
from konsider.api.models.rankings import (
    ComparisonRequest,
    ComparisonResponse,
    RankingRequest,
    RankingResponse,
)
from konsider.api.models.v2 import (
    CatalogV2Response,
    ComparisonV2Response,
    CountryDetailsV2Response,
    HealthV2Response,
    V2ComparisonRequest,
    V2RankingRequest,
    V2WeightSelection,
    RankingV2Response,
)
from konsider.api.settings import ApiSettings
from konsider.api.v2_service import V2RecommendationService
from konsider.application import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseError, CurrentReleaseRepository
from konsider.repositories.published_release_repository import (
    PublishedReleaseRepository,
    UnsupportedReleaseContractError,
)

ERROR_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Invalid request"},
    500: {"model": ErrorResponse, "description": "Unexpected internal failure"},
    503: {"model": ErrorResponse, "description": "Active release unavailable"},
}


def _default_service_factory(settings: ApiSettings) -> RecommendationService:
    repository = PublishedReleaseRepository(
        settings.release_root,
        settings.catalog_path,
        active_release_path=settings.active_release_path,
    )
    return RecommendationService(repository)


def _default_v2_service_factory(
    settings: ApiSettings,
    legacy_service: RecommendationService | None,
) -> V2RecommendationService:
    pointer = json.loads(settings.active_release_path.read_text(encoding="utf-8"))
    schema_version = pointer.get("schema_version", "")
    if schema_version.startswith("konsider-release-5."):
        repository = CurrentReleaseRepository(settings.release_root)
        release = repository.load(settings.release_root / pointer["release_id"])
        if release.manifest["status"] != "published":
            raise CurrentReleaseError("The active schema-5 release is not published.")
        if not release.validation["product_ready"]:
            raise CurrentReleaseError("The active schema-5 release is not product-ready.")
        return V2RecommendationService(release)
    return V2RecommendationService(legacy_service or _default_service_factory(settings))


def create_app(
    settings: ApiSettings | None = None,
    service: RecommendationService | None = None,
    service_factory: Callable[[ApiSettings], RecommendationService] | None = None,
    v2_service: V2RecommendationService | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    factory = service_factory or _default_service_factory

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.recommendation_service = None
        application.state.v2_recommendation_service = None
        application.state.initialization_error = None
        application.state.v2_initialization_error = None
        try:
            application.state.recommendation_service = service or factory(resolved_settings)
        except Exception as exc:  # A degraded app reports a controlled 503 from every endpoint.
            application.state.initialization_error = exc
        try:
            application.state.v2_recommendation_service = v2_service or _default_v2_service_factory(
                resolved_settings,
                application.state.recommendation_service,
            )
        except Exception as exc:
            application.state.v2_initialization_error = exc
        yield

    logging.getLogger("konsider.api").setLevel(resolved_settings.log_level)
    application = FastAPI(
        title="Konsider API",
        version="2.0.0",
        description=(
            "Versioned API over one immutable recommendation snapshot. "
            "API v1 is transitional and scheduled for Phase 5H removal."
        ),
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    register_exception_handlers(application)
    if resolved_settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @application.get(
        "/api/v1/health",
        response_model=HealthResponse,
        responses={503: ERROR_RESPONSES[503]},
        summary="Check API and active-release readiness",
    )
    def health(request: Request):
        initialization_error = request.app.state.initialization_error
        if initialization_error is not None:
            code = (
                "unsupported_release_contract"
                if isinstance(initialization_error, UnsupportedReleaseContractError)
                else "release_unavailable"
            )
            return error_response(
                request,
                503,
                code,
                "A validated active release is unavailable.",
            )
        current = request.app.state.recommendation_service
        release = current.release
        return HealthResponse(
            status="ok",
            release_id=release.release_id,
            release_schema_version=release.manifest["schema_version"],
            catalog_schema_version=release.catalog["schema_version"],
            scoring_method_versions=sorted(
                item["scoring_method_version"]
                for item in release.catalog["criteria"]
                if item["ready"]
            ),
            country_count=len(release.catalog["countries"]),
            enabled_criterion_count=len(release.enabled_criterion_ids),
            ready_for_rankings=bool(release.validation["product_ready"]),
        )

    @application.get(
        "/api/v1/catalog",
        response_model=CatalogResponse,
        responses=ERROR_RESPONSES,
        summary="Retrieve countries, criteria, readiness, and provisional profiles",
    )
    def catalog(current: RecommendationService = Depends(get_recommendation_service)):
        return catalog_response(current.get_catalog())

    @application.post(
        "/api/v1/rankings",
        response_model=RankingResponse,
        responses=ERROR_RESPONSES,
        summary="Rank eligible countries using a profile or explicit weights",
    )
    def rankings(
        payload: RankingRequest,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        return ranking_response(
            current.rank_with_uncertainty(
                payload.weights,
                profile_id=payload.profile_id,
                top_k=payload.top_k,
            )
        )

    @application.get(
        "/api/v1/countries/{country_code}/metrics",
        response_model=CountryMetricResponse,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Retrieve the enabled-criterion breakdown for one country",
    )
    def country_metrics(
        country_code: str,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        return country_metric_response(current.country_breakdown(country_code.upper()))

    @application.post(
        "/api/v1/comparisons",
        response_model=ComparisonResponse,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Compare 2–10 unique countries with consistent ranking semantics",
    )
    def comparisons(
        payload: ComparisonRequest,
        current: RecommendationService = Depends(get_recommendation_service),
    ):
        return comparison_response(
            current.compare_with_uncertainty(
                payload.country_codes,
                payload.weights,
                profile_id=payload.profile_id,
            )
        )

    @application.get(
        "/api/v2/health",
        response_model=HealthV2Response,
        responses={503: ERROR_RESPONSES[503]},
        summary="Check API v2 and active-release readiness",
    )
    def health_v2(
        current: V2RecommendationService = Depends(get_v2_recommendation_service),
    ):
        return HealthV2Response.model_validate(current.health())

    @application.get(
        "/api/v2/catalog",
        response_model=CatalogV2Response,
        responses=ERROR_RESPONSES,
        summary="Retrieve orthogonal criterion metadata and preference presets",
    )
    def catalog_v2(
        current: V2RecommendationService = Depends(get_v2_recommendation_service),
    ):
        return CatalogV2Response.model_validate(current.catalog())

    @application.post(
        "/api/v2/rankings",
        response_model=RankingV2Response,
        responses=ERROR_RESPONSES,
        summary="Rank countries with structured coverage, locality, and profile assessments",
    )
    def rankings_v2(
        payload: V2RankingRequest,
        current: V2RecommendationService = Depends(get_v2_recommendation_service),
    ):
        return RankingV2Response.model_validate(
            current.rank(
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
                top_k=payload.top_k,
            )
        )

    @application.post(
        "/api/v2/comparisons",
        response_model=ComparisonV2Response,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Compare countries without client-side coverage or locality logic",
    )
    def comparisons_v2(
        payload: V2ComparisonRequest,
        current: V2RecommendationService = Depends(get_v2_recommendation_service),
    ):
        return ComparisonV2Response.model_validate(
            current.compare(
                payload.country_codes,
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
            )
        )

    @application.post(
        "/api/v2/countries/{country_code}/details",
        response_model=CountryDetailsV2Response,
        responses={404: {"model": ErrorResponse}, **ERROR_RESPONSES},
        summary="Retrieve country evidence in the context of one weight selection",
    )
    def country_details_v2(
        country_code: str,
        payload: V2WeightSelection,
        current: V2RecommendationService = Depends(get_v2_recommendation_service),
    ):
        return CountryDetailsV2Response.model_validate(
            current.country_details(
                country_code.upper(),
                payload.weights,
                preference_preset_id=payload.preference_preset_id,
            )
        )

    return application


app = create_app()
