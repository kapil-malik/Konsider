"""Typed Phase 5 locality aggregation and assessment results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class LocalityAggregationStatus(StrEnum):
    VALID = "valid"
    MISSING = "missing"
    STALE = "stale"
    INVALID = "invalid"
    REJECTED = "rejected"


class LocalityStatus(StrEnum):
    NO_ACTIVE_LOCALITY_CRITERIA = "NO_ACTIVE_LOCALITY_CRITERIA"
    BELOW_ANALYSIS_THRESHOLD = "BELOW_ANALYSIS_THRESHOLD"
    ONE_ACTIVE_LOCALITY_CRITERION = "ONE_ACTIVE_LOCALITY_CRITERION"
    COMMON_LOCALITY_AVAILABLE = "COMMON_LOCALITY_AVAILABLE"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    NO_COMMON_LOCALITY = "NO_COMMON_LOCALITY"
    INSUFFICIENT_LOCALITY_EVIDENCE = "INSUFFICIENT_LOCALITY_EVIDENCE"
    MIXED_COUNTRY_RESULTS = "MIXED_COUNTRY_RESULTS"


class CoverageStatus(StrEnum):
    NO_PARTIAL_CRITERIA_ACTIVE = "NO_PARTIAL_CRITERIA_ACTIVE"
    FULL_COVERAGE = "FULL_COVERAGE"
    PARTIAL_COMPLETE_CASE = "PARTIAL_COMPLETE_CASE"
    COVERAGE_LIMIT_FALLBACK = "COVERAGE_LIMIT_FALLBACK"


class ProfileStatus(StrEnum):
    NO_PROFILE_CONTEXT = "NO_PROFILE_CONTEXT"


class ReasonSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"


class ReasonEffect(StrEnum):
    NONE = "NONE"
    ADVISORY = "ADVISORY"
    COUNTRY_EXCLUDED = "COUNTRY_EXCLUDED"
    RANKING_FALLBACK = "RANKING_FALLBACK"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class AssessmentReason:
    code: str
    severity: ReasonSeverity
    effect: ReasonEffect

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "effect": self.effect.value,
        }


@dataclass(frozen=True)
class LocalityAggregationResult:
    criterion_id: str
    country_entity_id: str
    status: LocalityAggregationStatus
    reason_codes: tuple[str, ...]
    quality_flags: tuple[str, ...]
    eligible_locality_entity_ids: tuple[str, ...]
    valid_locality_entity_ids: tuple[str, ...]
    ignored_locality_entity_ids: tuple[str, ...]
    observation: dict[str, Any] | None
    score: dict[str, Any] | None
    evidence: dict[str, Any] | None
    outcome: dict[str, Any]


@dataclass(frozen=True)
class CriterionLocalityEvidence:
    criterion_id: str
    eligible_locality_entity_ids: tuple[str, ...]
    valid_locality_entity_ids: tuple[str, ...]
    contributing_locality_entity_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "eligible_locality_entity_ids": list(self.eligible_locality_entity_ids),
            "valid_locality_entity_ids": list(self.valid_locality_entity_ids),
            "contributing_locality_entity_ids": list(self.contributing_locality_entity_ids),
        }


@dataclass(frozen=True)
class CountryLocalityAssessment:
    status: LocalityStatus
    eligible_locality_entity_ids: tuple[str, ...]
    valid_locality_entity_ids: tuple[str, ...]
    contributing_locality_entity_ids: tuple[str, ...]
    common_locality_entity_ids: tuple[str, ...]
    best_common_locality_entity_id: str | None
    criterion_evidence: tuple[CriterionLocalityEvidence, ...]
    reasons: tuple[AssessmentReason, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "eligible_locality_entity_ids": list(self.eligible_locality_entity_ids),
            "valid_locality_entity_ids": list(self.valid_locality_entity_ids),
            "contributing_locality_entity_ids": list(self.contributing_locality_entity_ids),
            "common_locality_entity_ids": list(self.common_locality_entity_ids),
            "best_common_locality_entity_id": self.best_common_locality_entity_id,
            "criterion_evidence": [item.to_dict() for item in self.criterion_evidence],
            "reasons": [item.to_dict() for item in self.reasons],
        }


@dataclass(frozen=True)
class ResponseLocalityAssessment:
    status: LocalityStatus
    policy_version: str
    contributing_criterion_ids: tuple[str, ...]
    analysis_triggered_criterion_ids: tuple[str, ...]
    below_threshold_criterion_ids: tuple[str, ...]
    analysis_thresholds: dict[str, float]
    aggregation_policy_ids: tuple[str, ...]
    reasons: tuple[AssessmentReason, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "policy_version": self.policy_version,
            "contributing_criterion_ids": list(self.contributing_criterion_ids),
            "analysis_triggered_criterion_ids": list(self.analysis_triggered_criterion_ids),
            "below_threshold_criterion_ids": list(self.below_threshold_criterion_ids),
            "analysis_thresholds": dict(sorted(self.analysis_thresholds.items())),
            "aggregation_policy_ids": list(self.aggregation_policy_ids),
            "reasons": [item.to_dict() for item in self.reasons],
        }


@dataclass(frozen=True)
class CoverageAssessment:
    status: CoverageStatus
    policy_version: str
    active_global_core_criterion_ids: tuple[str, ...]
    active_conditional_criterion_ids: tuple[str, ...]
    excluded_country_entity_ids: tuple[str, ...]
    reasons: tuple[AssessmentReason, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "policy_version": self.policy_version,
            "active_global_core_criterion_ids": list(self.active_global_core_criterion_ids),
            "active_conditional_criterion_ids": list(self.active_conditional_criterion_ids),
            "excluded_country_entity_ids": list(self.excluded_country_entity_ids),
            "reasons": [item.to_dict() for item in self.reasons],
        }


@dataclass(frozen=True)
class ProfileAssessment:
    status: ProfileStatus
    evaluated_dimensions: tuple[str, ...]
    reasons: tuple[AssessmentReason, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "evaluated_dimensions": list(self.evaluated_dimensions),
            "reasons": [item.to_dict() for item in self.reasons],
        }


@dataclass(frozen=True)
class Phase5Contribution:
    criterion_id: str
    score: float
    normalized_weight: float
    contribution: float
    observation_id: str
    score_id: str
    evidence_kind: str
    derived_evidence_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Phase5RankedCountry:
    rank: int
    country: dict[str, str]
    total_score: float
    contributions: tuple[Phase5Contribution, ...]
    locality_assessment: CountryLocalityAssessment
    profile_assessment: ProfileAssessment

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "country": dict(self.country),
            "total_score": self.total_score,
            "contributions": [item.to_dict() for item in self.contributions],
            "assessments": {
                "locality": self.locality_assessment.to_dict(),
                "profile": self.profile_assessment.to_dict(),
            },
        }


@dataclass(frozen=True)
class Phase5RankingResult:
    release_id: str
    release_schema_version: str
    catalog_schema_version: str
    resolved_preference_preset_id: str | None
    normalized_weights: dict[str, float]
    coverage_assessment: CoverageAssessment
    locality_assessment: ResponseLocalityAssessment
    profile_assessment: ProfileAssessment
    rankings: tuple[Phase5RankedCountry, ...]
    country_locality_assessments: dict[str, CountryLocalityAssessment]

    def to_dict(self) -> dict[str, Any]:
        excluded_ids = set(self.coverage_assessment.excluded_country_entity_ids)
        excluded_locality = [
            {
                "country": {"entity_id": entity_id, "entity_type": "COUNTRY"},
                "assessment": assessment.to_dict(),
            }
            for entity_id, assessment in sorted(self.country_locality_assessments.items())
            if entity_id in excluded_ids
        ]
        locality = self.locality_assessment.to_dict()
        locality["excluded_country_assessments"] = excluded_locality
        return {
            "api_contract_version": "konsider-api-2.0",
            "release_id": self.release_id,
            "release_schema_version": self.release_schema_version,
            "catalog_schema_version": self.catalog_schema_version,
            "resolved_preference_preset_id": self.resolved_preference_preset_id,
            "normalized_weights": dict(sorted(self.normalized_weights.items())),
            "assessments": {
                "coverage": self.coverage_assessment.to_dict(),
                "locality": locality,
                "profile": self.profile_assessment.to_dict(),
            },
            "rankings": [row.to_dict() for row in self.rankings],
        }
