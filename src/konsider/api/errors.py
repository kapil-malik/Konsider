"""Stable exception-to-HTTP mappings."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from konsider.api.models.common import ErrorResponse
from konsider.exceptions import (
    CountryNotFoundError,
    CriterionNotReadyError,
    InvalidComparisonError,
    InvalidProfileSelectionError,
    InvalidTopKError,
    InvalidWeightError,
    PreferencePresetNotFoundError,
    ProfileNotFoundError,
    UnknownCriterionError,
)
from konsider.ingestion.current_release import CurrentReleaseError
from konsider.repositories.published_release_repository import (
    PublishedReleaseError,
    UnsupportedReleaseContractError,
)

LOGGER = logging.getLogger("konsider.api")


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    body = ErrorResponse.model_validate(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "request_id": request.headers.get("x-request-id"),
            }
        }
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        details = {
            "errors": [
                {
                    "type": item["type"],
                    "location": list(item["loc"]),
                    "message": item["msg"],
                }
                for item in exc.errors()
            ]
        }
        return error_response(
            request, 422, "request_validation_failed", "The request payload is invalid.", details
        )

    @app.exception_handler(UnknownCriterionError)
    async def unknown_criterion_handler(request: Request, exc: UnknownCriterionError):
        return error_response(
            request,
            422,
            "unknown_criterion",
            "One or more criterion IDs are unknown.",
            {"criterion_ids": exc.criterion_ids},
        )

    @app.exception_handler(CriterionNotReadyError)
    async def criterion_not_ready_handler(request: Request, exc: CriterionNotReadyError):
        return error_response(
            request,
            422,
            "criterion_not_ready",
            "One or more criteria are not available for ranking.",
            {"criterion_ids": exc.criterion_ids},
        )

    @app.exception_handler(InvalidWeightError)
    async def invalid_weight_handler(request: Request, exc: InvalidWeightError):
        return error_response(request, 422, "invalid_weight", str(exc))

    @app.exception_handler(InvalidTopKError)
    async def invalid_top_k_handler(request: Request, exc: InvalidTopKError):
        return error_response(
            request,
            422,
            "invalid_top_k",
            str(exc),
            {"top_k": exc.top_k, "eligible_country_count": exc.eligible_count},
        )

    @app.exception_handler(InvalidProfileSelectionError)
    async def invalid_profile_selection_handler(
        request: Request, exc: InvalidProfileSelectionError
    ):
        return error_response(request, 422, "invalid_profile_selection", str(exc))

    @app.exception_handler(ProfileNotFoundError)
    async def profile_not_found_handler(request: Request, exc: ProfileNotFoundError):
        return error_response(
            request,
            422,
            "profile_not_found",
            "The requested profile does not exist.",
            {"profile_id": exc.profile_id},
        )

    @app.exception_handler(PreferencePresetNotFoundError)
    async def preference_preset_not_found_handler(
        request: Request, exc: PreferencePresetNotFoundError
    ):
        return error_response(
            request,
            422,
            "preference_preset_not_found",
            "The requested preference preset does not exist.",
            {"preference_preset_id": exc.preference_preset_id},
        )

    @app.exception_handler(CountryNotFoundError)
    async def country_not_found_handler(request: Request, exc: CountryNotFoundError):
        return error_response(
            request,
            404,
            "country_not_found",
            "One or more country codes are unknown.",
            {"country_codes": exc.country_codes},
        )

    @app.exception_handler(InvalidComparisonError)
    async def invalid_comparison_handler(request: Request, exc: InvalidComparisonError):
        return error_response(request, 422, "invalid_comparison", str(exc))

    @app.exception_handler(UnsupportedReleaseContractError)
    async def unsupported_release_handler(request: Request, exc: UnsupportedReleaseContractError):
        LOGGER.error("Unsupported release contract", exc_info=exc)
        return error_response(
            request,
            503,
            "unsupported_release_contract",
            "The active release uses an unsupported contract.",
        )

    @app.exception_handler(PublishedReleaseError)
    async def release_unavailable_handler(request: Request, exc: PublishedReleaseError):
        LOGGER.error("Published release unavailable", exc_info=exc)
        return error_response(
            request,
            503,
            "release_unavailable",
            "A validated active release is unavailable.",
        )

    @app.exception_handler(CurrentReleaseError)
    async def current_release_unavailable_handler(request: Request, exc: CurrentReleaseError):
        LOGGER.error("Current release unavailable", exc_info=exc)
        return error_response(
            request,
            503,
            "release_unavailable",
            "A validated active release is unavailable.",
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception):
        LOGGER.exception("Unexpected API error", exc_info=exc)
        return error_response(request, 500, "internal_error", "An unexpected error occurred.")
