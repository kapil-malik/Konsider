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
    InvalidTopKError,
    InvalidProfileContextError,
    InvalidOpportunityFilterSelectionError,
    InvalidWeightError,
    OpportunityFilterNotActiveError,
    PreferencePresetNotFoundError,
    TfcCandidateUnavailableError,
    TfcFilterNotAllowedError,
    UnknownTfcError,
    UnsupportedTaxonomyVersionError,
    UnknownCriterionError,
    UnknownOpportunityFilterError,
)
from konsider.ingestion.current_release import CurrentReleaseError

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
        locations = [tuple(str(part) for part in item["loc"]) for item in exc.errors()]
        if any("feasibility" in location and location[-1] == "mode" for location in locations):
            code = "unsupported_feasibility_mode"
            message = "The requested feasibility mode is unsupported."
        elif any("feasibility" in location for location in locations):
            code = "invalid_profile_field"
            message = "One or more feasibility profile fields are invalid."
        else:
            code = "request_validation_failed"
            message = "The request payload is invalid."
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
        return error_response(request, 422, code, message, details)

    @app.exception_handler(UnknownTfcError)
    async def unknown_tfc_handler(request: Request, exc: UnknownTfcError):
        return error_response(
            request,
            422,
            "selected_tfc_unavailable",
            "One or more selected feasibility checks are unavailable.",
            {"tfc_ids": exc.tfc_ids},
        )

    @app.exception_handler(TfcFilterNotAllowedError)
    async def tfc_filter_not_allowed_handler(request: Request, exc: TfcFilterNotAllowedError):
        return error_response(
            request,
            422,
            "feasibility_filter_not_allowed",
            "The selected feasibility checks are assessment-only.",
            {"tfc_ids": exc.tfc_ids},
        )

    @app.exception_handler(UnsupportedTaxonomyVersionError)
    async def unsupported_taxonomy_handler(request: Request, exc: UnsupportedTaxonomyVersionError):
        return error_response(
            request,
            422,
            "unsupported_taxonomy_version",
            "A mapped profile field uses an unsupported taxonomy version.",
            {"field_ids": exc.field_ids},
        )

    @app.exception_handler(InvalidProfileContextError)
    async def invalid_profile_handler(request: Request, exc: InvalidProfileContextError):
        return error_response(
            request,
            422,
            "invalid_profile_context",
            "The supplied profile context cannot be assessed.",
        )

    @app.exception_handler(TfcCandidateUnavailableError)
    async def tfc_candidate_unavailable_handler(
        request: Request, exc: TfcCandidateUnavailableError
    ):
        LOGGER.error("TFC candidate unavailable")
        return error_response(
            request,
            503,
            "tfc_candidate_unavailable",
            "The staged feasibility evidence is unavailable.",
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

    @app.exception_handler(UnknownOpportunityFilterError)
    async def unknown_opportunity_filter_handler(
        request: Request, exc: UnknownOpportunityFilterError
    ):
        return error_response(
            request,
            422,
            "unknown_opportunity_filter",
            "One or more Opportunity Filter IDs are unknown.",
            {"filter_ids": exc.filter_ids},
        )

    @app.exception_handler(OpportunityFilterNotActiveError)
    async def inactive_opportunity_filter_handler(
        request: Request, exc: OpportunityFilterNotActiveError
    ):
        return error_response(
            request,
            422,
            "opportunity_filter_not_active",
            "One or more Opportunity Filters are not active in the selected release.",
            {"filter_ids": exc.filter_ids},
        )

    @app.exception_handler(InvalidOpportunityFilterSelectionError)
    async def invalid_opportunity_filter_selection_handler(
        request: Request, exc: InvalidOpportunityFilterSelectionError
    ):
        return error_response(request, 422, "invalid_opportunity_filter_selection", str(exc))

    @app.exception_handler(InvalidTopKError)
    async def invalid_top_k_handler(request: Request, exc: InvalidTopKError):
        return error_response(
            request,
            422,
            "invalid_top_k",
            str(exc),
            {"top_k": exc.top_k, "eligible_country_count": exc.eligible_count},
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
