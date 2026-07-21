"""Ranking and comparison transport contracts."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from konsider.api.models.common import (
    ApiModel,
    ObservationResponse,
    SourceResponse,
    VersionedResponse,
)


def _validate_weights(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, dict):
        raise ValueError("weights must be an object")
    for criterion_id, weight in value.items():
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError(f"weight for {criterion_id!r} must be a JSON number")
    return value


class WeightSelection(ApiModel):
    weights: dict[str, float] | None = None
    profile_id: str | None = Field(default=None, min_length=1)

    _strict_weights = field_validator("weights", mode="before")(_validate_weights)


class RankingRequest(WeightSelection):
    top_k: int | None = Field(default=None, strict=True)


class ComparisonRequest(WeightSelection):
    country_codes: list[str]

    @field_validator("country_codes")
    @classmethod
    def normalize_and_validate_countries(cls, value: list[str]) -> list[str]:
        normalized = [item.upper() for item in value]
        return normalized


class ContributionResponse(ApiModel):
    criterion_id: str
    criterion_name: str
    score: float
    normalized_weight: float
    contribution: float
    scoring_method_version: str
    caveats: list[str]
    quality_limitations: list[str]
    experimental: bool
    observations: list[ObservationResponse]
    source: SourceResponse


class RankedCountryResponse(ApiModel):
    rank: int
    country_code: str
    country_name: str
    region: str
    total_score: float
    contributions: list[ContributionResponse]
    strengths: list[str]
    tradeoffs: list[str]


class RankingResponse(VersionedResponse):
    resolved_profile_id: str | None
    normalized_weights: dict[str, float]
    all_zero_behavior: str
    country_tie_breaker: str
    rounding_tolerance: float
    total_eligible_country_count: int
    returned_result_count: int
    rankings: list[RankedCountryResponse]


class ComparisonResponse(VersionedResponse):
    resolved_profile_id: str | None
    normalized_weights: dict[str, float]
    all_zero_behavior: str
    country_tie_breaker: str
    rounding_tolerance: float
    total_eligible_country_count: int
    returned_result_count: int
    countries: list[RankedCountryResponse]
