"""FastAPI application factory for the versioned Konsider API."""

from __future__ import annotations

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from konsider.api.dependencies import get_recommendation_service
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
from konsider.api.settings import ApiSettings
from konsider.application import RecommendationService
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


def create_app(
    settings: ApiSettings | None = None,
    service: RecommendationService | None = None,
    service_factory: Callable[[ApiSettings], RecommendationService] | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    factory = service_factory or _default_service_factory

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.recommendation_service = None
        application.state.initialization_error = None
        try:
            application.state.recommendation_service = service or factory(resolved_settings)
        except Exception as exc:  # A degraded app reports a controlled 503 from every endpoint.
            application.state.initialization_error = exc
        yield

    logging.getLogger("konsider.api").setLevel(resolved_settings.log_level)
    application = FastAPI(
        title="Konsider API",
        version="1.0.0",
        description="Thin versioned API over one immutable published recommendation snapshot.",
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

    return application


app = create_app()
