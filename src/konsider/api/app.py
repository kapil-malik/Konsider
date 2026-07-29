"""FastAPI application factory for the structured Konsider API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from konsider.api.dependencies import get_recommendation_service
from konsider.api.errors import register_exception_handlers
from konsider.api.models.common import ErrorResponse
from konsider.api.models.v2 import (
    CatalogV2Response,
    ComparisonV2Response,
    CountryDetailsV2Response,
    HealthV2Response,
    RankingV2Response,
    V2ComparisonRequest,
    V2RankingRequest,
    V2WeightSelection,
)
from konsider.api.settings import ApiSettings
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseError, CurrentReleaseRepository

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
    return RecommendationService(release)


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
        version="2.0.0",
        description="Structured API over one immutable schema-current recommendation snapshot.",
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
        "/api/v2/health",
        response_model=HealthV2Response,
        responses={503: ERROR_RESPONSES[503]},
        summary="Check API and active-release readiness",
    )
    def health(current: RecommendationService = Depends(get_recommendation_service)):
        return HealthV2Response.model_validate(current.health())

    @application.get(
        "/api/v2/catalog",
        response_model=CatalogV2Response,
        responses=ERROR_RESPONSES,
        summary="Retrieve orthogonal criterion metadata and preference presets",
    )
    def catalog(current: RecommendationService = Depends(get_recommendation_service)):
        return CatalogV2Response.model_validate(current.catalog())

    @application.post(
        "/api/v2/rankings",
        response_model=RankingV2Response,
        responses=ERROR_RESPONSES,
        summary="Rank countries with structured coverage, locality, and profile assessments",
    )
    def rankings(
        payload: V2RankingRequest,
        current: RecommendationService = Depends(get_recommendation_service),
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
    def comparisons(
        payload: V2ComparisonRequest,
        current: RecommendationService = Depends(get_recommendation_service),
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
    def country_details(
        country_code: str,
        payload: V2WeightSelection,
        current: RecommendationService = Depends(get_recommendation_service),
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
