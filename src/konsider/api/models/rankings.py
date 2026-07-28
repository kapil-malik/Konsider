"""Ranking and comparison transport contracts."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

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
    top_k: int = Field(default=10, strict=True)


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
    eligible_country_count: int
    contributions: list[ContributionResponse]
    strengths: list[str]
    tradeoffs: list[str]


class PolicyThresholdsResponse(ApiModel):
    stable_universe_id: str
    stable_country_count: int
    pcc_min_valid_country_count: int
    preferred_missing_union_max: int
    hard_missing_union_max: int
    min_eligible_country_count: int
    pcc_activation_raw_weight_min: float
    diagnostic_score_max: float
    rounding_tolerance: float


class IgnoredPccResponse(ApiModel):
    criterion_id: str
    raw_weight: float
    reason_code: str
    activation_threshold: float


class NonReadyCriterionResponse(ApiModel):
    criterion_id: str
    outcome: Literal["missing", "stale", "invalid", "rejected"]
    reason_codes: list[str]
    source_id: str
    source_versions: dict[str, str]
    scoring_method_version: str
    observation_id: str | None


class ExcludedCountryResponse(ApiModel):
    country_code: str
    country_name: str
    r0_rank: int
    r0_score: float
    baseline_top_k_member: bool
    non_ready_criteria: list[NonReadyCriterionResponse]
    optimistic_upper_bound: float | None
    could_enter_top_k: bool | None


class UncertaintyMetadataResponse(VersionedResponse):
    resolved_profile_id: str | None
    normalized_weights: dict[str, float]
    all_zero_behavior: str
    country_tie_breaker: str
    rounding_tolerance: float
    total_eligible_country_count: int
    returned_result_count: int
    stable_universe_size: int
    eligible_universe_size: int
    excluded_country_count: int
    ranking_coverage_mode: Literal[
        "GLOBAL_CORE",
        "CONDITIONAL_COMPLETE_CASE",
    ]
    uncertainty_status: Literal[
        "NO_PARTIAL_CRITERIA_ACTIVE",
        "COVERAGE_LIMIT_EXCEEDED",
        "FULL_COVERAGE",
        "BASELINE_TOP_K_EXCLUDED",
        "POTENTIALLY_AFFECTED",
        "ROBUST_TOP_K",
    ]
    coverage_band: Literal["PREFERRED", "ELEVATED", "BLOCKED"]
    reason_codes: list[str]
    message_code: str
    active_fcc_ids: list[str]
    active_pcc_ids: list[str]
    ignored_pcc: list[IgnoredPccResponse]
    robustness_k: int
    kth_eligible_score: float | None
    potential_excluded_entrants: list[str]
    baseline_top_k_country_codes: list[str]
    baseline_kth_score: float
    baseline_boundary_tie_count: int
    baseline_returned_result_count: int
    policy_version: str
    policy_thresholds: PolicyThresholdsResponse
    excluded_countries: list[ExcludedCountryResponse]


class RankingResponse(UncertaintyMetadataResponse):
    rankings: list[RankedCountryResponse]


class ComparisonCellResponse(ApiModel):
    country_code: str
    availability: Literal[
        "AVAILABLE",
        "MISSING",
        "STALE",
        "INVALID",
        "REJECTED",
    ]
    message_code: str
    active_for_ranking: bool
    normalized_score: float | None
    raw_observation: float | None
    raw_unit: str | None
    reference_start: date | None
    reference_end: date | None
    source: SourceResponse
    reason_codes: list[str]


class ComparisonCriterionRowResponse(ApiModel):
    criterion_id: str
    criterion_name: str
    coverage_mode: Literal[
        "GLOBAL_CORE",
        "CONDITIONAL_COMPLETE_CASE",
        "DIAGNOSTIC_ONLY",
    ]
    experimental: bool
    cells: list[ComparisonCellResponse]


class ComparisonCountrySummaryResponse(ApiModel):
    country_code: str
    country_name: str
    comparison_data_complete: bool
    ranking_eligible: bool
    unavailable_displayed_criterion_count: int
    unavailable_active_criterion_count: int
    aggregate_kind: Literal["FINAL", "FCC_BASELINE", "NONE"]
    ranking_status: Literal[
        "RANKED",
        "NOT_RANKED_ACTIVE_DATA_GAP",
        "FCC_BASELINE_ONLY",
    ]
    message_code: str
    total_score: float | None
    rank: int | None


class ComparisonResponse(UncertaintyMetadataResponse):
    requested_country_codes: list[str]
    comparison_country_count: int
    country_summaries: list[ComparisonCountrySummaryResponse]
    criterion_rows: list[ComparisonCriterionRowResponse]
    requested_excluded_countries: list[ExcludedCountryResponse]
    countries: list[RankedCountryResponse]
