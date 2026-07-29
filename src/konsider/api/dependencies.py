"""FastAPI dependency seam for the schema-current recommendation service."""

from __future__ import annotations

from fastapi import Request

from konsider.api.v2_service import RecommendationService


def get_recommendation_service(request: Request) -> RecommendationService:
    error = getattr(request.app.state, "initialization_error", None)
    if error is not None:
        raise error
    return request.app.state.recommendation_service
