"""FastAPI dependency seams."""

from __future__ import annotations

from fastapi import Request

from konsider.application import RecommendationService


def get_recommendation_service(request: Request) -> RecommendationService:
    error = getattr(request.app.state, "initialization_error", None)
    if error is not None:
        raise error
    return request.app.state.recommendation_service
