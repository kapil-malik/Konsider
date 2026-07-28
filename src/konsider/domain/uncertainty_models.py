"""Typed domain results for uncertainty-aware complete-case ranking."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class UncertaintyStatus(StrEnum):
    NO_PARTIAL_CRITERIA_ACTIVE = "NO_PARTIAL_CRITERIA_ACTIVE"
    COVERAGE_LIMIT_EXCEEDED = "COVERAGE_LIMIT_EXCEEDED"
    FULL_COVERAGE = "FULL_COVERAGE"
    BASELINE_TOP_K_EXCLUDED = "BASELINE_TOP_K_EXCLUDED"
    POTENTIALLY_AFFECTED = "POTENTIALLY_AFFECTED"
    ROBUST_TOP_K = "ROBUST_TOP_K"


class CoverageBand(StrEnum):
    PREFERRED = "PREFERRED"
    ELEVATED = "ELEVATED"
    BLOCKED = "BLOCKED"


class ComparisonAvailability(StrEnum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    STALE = "STALE"
    INVALID = "INVALID"
    REJECTED = "REJECTED"


class ComparisonAggregateKind(StrEnum):
    FINAL = "FINAL"
    FCC_BASELINE = "FCC_BASELINE"
    NONE = "NONE"


class ComparisonRankingStatus(StrEnum):
    RANKED = "RANKED"
    NOT_RANKED_ACTIVE_DATA_GAP = "NOT_RANKED_ACTIVE_DATA_GAP"
    FCC_BASELINE_ONLY = "FCC_BASELINE_ONLY"


@dataclass(frozen=True)
class UncertaintyPolicy:
    policy_version: str = "uncertainty-aware-ranking-policy-1.0"
    stable_universe_id: str = "stable_supported_v1"
    stable_country_count: int = 91
    pcc_min_valid_country_count: int = 82
    preferred_missing_union_max: int = 5
    hard_missing_union_max: int = 9
    min_eligible_country_count: int = 82
    pcc_activation_raw_weight_min: float = 0.6
    default_top_k: int = 10
    diagnostic_score_max: float = 10.0
    canonical_score_min: float = 1.0
    canonical_score_max: float = 10.0
    country_tie_breaker: str = "ascending_iso3_country_code"
    rounding_tolerance: float = 1e-8
    score_precision: int = 8

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


POLICY = UncertaintyPolicy()


@dataclass(frozen=True)
class ContributionSource:
    source_id: str
    publisher: str
    source_version: str
    dataset_version: str
    canonical_page_url: str
    attribution: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RankingContribution:
    criterion_id: str
    criterion_name: str
    score: float
    normalized_weight: float
    contribution: float
    raw_observation: float
    raw_unit: str
    reference_start: str
    reference_end: str
    observation_id: str
    observation_method_version: str
    parser_version: str
    scoring_method_version: str
    source: ContributionSource
    caveats: tuple[str, ...]
    quality_limitations: tuple[str, ...]
    experimental: bool
    input_observations: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["source"] = self.source.to_dict()
        value["caveats"] = list(self.caveats)
        value["quality_limitations"] = list(self.quality_limitations)
        value["input_observations"] = [dict(item) for item in self.input_observations]
        return value


@dataclass(frozen=True)
class UncertaintyRankingRow:
    rank: int
    country_code: str
    country_name: str
    region: str
    total_score: float
    eligible_country_count: int
    contributions: tuple[RankingContribution, ...]
    strengths: tuple[str, ...]
    tradeoffs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["contributions"] = [item.to_dict() for item in self.contributions]
        value["strengths"] = list(self.strengths)
        value["tradeoffs"] = list(self.tradeoffs)
        return value


@dataclass(frozen=True)
class TopKBoundary:
    requested_k: int
    kth_score: float
    boundary_tie_count: int
    returned_result_count: int
    rankings: tuple[UncertaintyRankingRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_k": self.requested_k,
            "kth_score": self.kth_score,
            "boundary_tie_count": self.boundary_tie_count,
            "returned_result_count": self.returned_result_count,
            "rankings": [item.to_dict() for item in self.rankings],
        }


@dataclass(frozen=True)
class IgnoredPartialCriterion:
    criterion_id: str
    raw_weight: float
    reason_code: str
    activation_threshold: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NonReadyCriterion:
    criterion_id: str
    outcome: str
    reason_codes: tuple[str, ...]
    source_id: str
    source_versions: dict[str, str]
    scoring_method_version: str
    observation_id: str | None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["reason_codes"] = list(self.reason_codes)
        return value


@dataclass(frozen=True)
class ExcludedCountryDiagnostic:
    country_code: str
    country_name: str
    r0_rank: int
    r0_score: float
    non_ready_criteria: tuple[NonReadyCriterion, ...]
    optimistic_upper_bound: float | None
    could_enter_top_k: bool | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "r0_rank": self.r0_rank,
            "r0_score": self.r0_score,
            "non_ready_criteria": [item.to_dict() for item in self.non_ready_criteria],
            "optimistic_upper_bound": self.optimistic_upper_bound,
            "could_enter_top_k": self.could_enter_top_k,
        }


@dataclass(frozen=True)
class UncertaintyRankingResult:
    release_id: str
    release_schema_version: str
    catalog_schema_version: str
    scoring_method_versions: tuple[str, ...]
    resolved_profile_id: str | None
    policy: UncertaintyPolicy
    status: UncertaintyStatus
    reason_codes: tuple[str, ...]
    coverage_band: CoverageBand
    requested_top_k: int
    stable_country_count: int
    eligible_country_count: int
    excluded_country_count: int
    active_fcc_ids: tuple[str, ...]
    active_pcc_ids: tuple[str, ...]
    ignored_pcc: tuple[IgnoredPartialCriterion, ...]
    baseline_normalized_weights: dict[str, float]
    final_normalized_weights: dict[str, float] | None
    excluded_countries: tuple[ExcludedCountryDiagnostic, ...]
    r0_top_k: TopKBoundary
    r1_top_k: TopKBoundary | None
    r1_kth_score: float | None
    rankings: tuple[UncertaintyRankingRow, ...]
    _r0_rankings: tuple[UncertaintyRankingRow, ...] = field(repr=False)
    _r1_rankings: tuple[UncertaintyRankingRow, ...] | None = field(repr=False)

    @property
    def r0_rankings_by_country(self) -> dict[str, UncertaintyRankingRow]:
        return {item.country_code: item for item in self._r0_rankings}

    @property
    def r1_rankings_by_country(self) -> dict[str, UncertaintyRankingRow]:
        return {item.country_code: item for item in (self._r1_rankings or ())}

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_id": self.release_id,
            "release_schema_version": self.release_schema_version,
            "catalog_schema_version": self.catalog_schema_version,
            "scoring_method_versions": list(self.scoring_method_versions),
            "resolved_profile_id": self.resolved_profile_id,
            "policy": self.policy.to_dict(),
            "uncertainty_status": self.status.value,
            "reason_codes": list(self.reason_codes),
            "coverage_band": self.coverage_band.value,
            "requested_top_k": self.requested_top_k,
            "stable_country_count": self.stable_country_count,
            "eligible_country_count": self.eligible_country_count,
            "excluded_country_count": self.excluded_country_count,
            "active_fcc_ids": list(self.active_fcc_ids),
            "active_pcc_ids": list(self.active_pcc_ids),
            "ignored_pcc": [item.to_dict() for item in self.ignored_pcc],
            "baseline_normalized_weights": dict(sorted(self.baseline_normalized_weights.items())),
            "final_normalized_weights": (
                dict(sorted(self.final_normalized_weights.items()))
                if self.final_normalized_weights is not None
                else None
            ),
            "excluded_countries": [item.to_dict() for item in self.excluded_countries],
            "r0_top_k": self.r0_top_k.to_dict(),
            "r1_top_k": self.r1_top_k.to_dict() if self.r1_top_k else None,
            "r1_kth_score": self.r1_kth_score,
            "returned_result_count": len(self.rankings),
            "rankings": [item.to_dict() for item in self.rankings],
        }


@dataclass(frozen=True)
class ComparisonCell:
    country_code: str
    availability: ComparisonAvailability
    message_code: str
    active_for_ranking: bool
    normalized_score: float | None
    raw_observation: float | None
    raw_unit: str | None
    reference_start: str | None
    reference_end: str | None
    source: ContributionSource
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "country_code": self.country_code,
            "availability": self.availability.value,
            "message_code": self.message_code,
            "active_for_ranking": self.active_for_ranking,
            "normalized_score": self.normalized_score,
            "raw_observation": self.raw_observation,
            "raw_unit": self.raw_unit,
            "reference_start": self.reference_start,
            "reference_end": self.reference_end,
            "source": self.source.to_dict(),
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class ComparisonCriterionRow:
    criterion_id: str
    criterion_name: str
    coverage_mode: str
    experimental: bool
    cells: tuple[ComparisonCell, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "criterion_name": self.criterion_name,
            "coverage_mode": self.coverage_mode,
            "experimental": self.experimental,
            "cells": [item.to_dict() for item in self.cells],
        }


@dataclass(frozen=True)
class ComparisonCountrySummary:
    country_code: str
    country_name: str
    comparison_data_complete: bool
    ranking_eligible: bool
    unavailable_displayed_criterion_count: int
    unavailable_active_criterion_count: int
    aggregate_kind: ComparisonAggregateKind
    ranking_status: ComparisonRankingStatus
    message_code: str
    total_score: float | None
    rank: int | None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["aggregate_kind"] = self.aggregate_kind.value
        value["ranking_status"] = self.ranking_status.value
        return value


@dataclass(frozen=True)
class UncertaintyComparisonResult:
    ranking_result: UncertaintyRankingResult
    requested_country_codes: tuple[str, ...]
    country_summaries: tuple[ComparisonCountrySummary, ...]
    criterion_rows: tuple[ComparisonCriterionRow, ...]
    countries: tuple[UncertaintyRankingRow, ...]
    excluded_countries: tuple[ExcludedCountryDiagnostic, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ranking": self.ranking_result.to_dict(),
            "requested_country_codes": list(self.requested_country_codes),
            "country_summaries": [item.to_dict() for item in self.country_summaries],
            "criterion_rows": [item.to_dict() for item in self.criterion_rows],
            "countries": [item.to_dict() for item in self.countries],
            "excluded_countries": [item.to_dict() for item in self.excluded_countries],
        }
