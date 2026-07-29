"""Deterministic schema-5 ranking with orthogonal coverage/locality/profile assessments."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_EVEN
from itertools import combinations
from math import isfinite
from typing import Any, Protocol

from konsider.domain.locality_aggregation import (
    DISQUALIFYING_INVALID_FLAGS,
    DISQUALIFYING_STALE_FLAGS,
)
from konsider.domain.locality_models import (
    AssessmentReason,
    CountryLocalityAssessment,
    CoverageAssessment,
    CoverageStatus,
    CriterionLocalityEvidence,
    LocalityStatus,
    Phase5Contribution,
    Phase5RankedCountry,
    Phase5RankingResult,
    ProfileAssessment,
    ProfileStatus,
    ReasonEffect,
    ReasonSeverity,
    ResponseLocalityAssessment,
)
from konsider.domain.scoring import normalize_weights


class Schema5Release(Protocol):
    """Minimal immutable-release view required by the Phase 5 domain engine."""

    manifest: dict[str, Any]
    validation: dict[str, Any]
    artifacts: Any


SCORE_PRECISION = 8
LOCALITY_ASSESSMENT_POLICY_VERSION = "locality-assessment-policy-1.0"


class Phase5RankingError(ValueError):
    """Raised when schema-5 release inputs cannot produce a complete ranking."""


def _reason(
    code: str,
    *,
    severity: ReasonSeverity = ReasonSeverity.INFO,
    effect: ReasonEffect = ReasonEffect.NONE,
) -> AssessmentReason:
    return AssessmentReason(code, severity, effect)


def _round(value: Decimal) -> float:
    return float(
        value.quantize(
            Decimal(1).scaleb(-SCORE_PRECISION),
            rounding=ROUND_HALF_EVEN,
        )
    )


def _validated_raw_weights(
    weights: Mapping[str, float],
    criteria: dict[str, dict[str, Any]],
) -> dict[str, float]:
    unknown = sorted(set(weights) - set(criteria))
    if unknown:
        raise Phase5RankingError(f"Unknown criterion weights: {unknown}")
    non_ready = sorted(
        criterion_id
        for criterion_id, value in weights.items()
        if value and not criteria[criterion_id]["ready"]
    )
    if non_ready:
        raise Phase5RankingError(f"Non-ready criteria cannot be weighted: {non_ready}")
    result: dict[str, float] = {}
    for criterion_id, criterion in sorted(criteria.items()):
        value = weights.get(criterion_id, 0.0)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Phase5RankingError(f"Weight for {criterion_id} must be numeric.")
        value = float(value)
        if not isfinite(value) or value < 0:
            raise Phase5RankingError(f"Weight for {criterion_id} must be finite and non-negative.")
        if criterion["ready"]:
            result[criterion_id] = value
    if not any(result.values()):
        result = {criterion_id: 1.0 for criterion_id in result}
    return result


def _activate_coverage(
    *,
    criteria: dict[str, dict[str, Any]],
    raw_weights: dict[str, float],
    countries: tuple[str, ...],
    outcomes: dict[tuple[str, str], dict[str, Any]],
    coverage_policy_version: str,
) -> tuple[CoverageAssessment, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    fcc = tuple(
        criterion_id
        for criterion_id, criterion in sorted(criteria.items())
        if criterion["ready"]
        and raw_weights[criterion_id] > 0
        and criterion["coverage"]["mode"] == "GLOBAL_CORE"
    )
    pcc = tuple(
        criterion_id
        for criterion_id, criterion in sorted(criteria.items())
        if criterion["ready"]
        and criterion["coverage"]["mode"] == "CONDITIONAL_COMPLETE_CASE"
        and raw_weights[criterion_id] >= criterion["coverage"]["activation_threshold"]
    )
    below_pcc = tuple(
        criterion_id
        for criterion_id, criterion in sorted(criteria.items())
        if criterion["ready"]
        and criterion["coverage"]["mode"] == "CONDITIONAL_COMPLETE_CASE"
        and 0 < raw_weights[criterion_id] < criterion["coverage"]["activation_threshold"]
    )
    active = (*fcc, *pcc)
    if not active:
        raise Phase5RankingError("No ready criterion is active under the coverage policy.")

    eligible = tuple(
        country_id
        for country_id in countries
        if all(
            outcomes.get((criterion_id, country_id), {}).get("outcome") == "valid"
            for criterion_id in active
        )
    )
    reasons = [_reason(f"PCC_BELOW_ACTIVATION:{criterion_id}") for criterion_id in below_pcc]
    if not pcc:
        status = CoverageStatus.NO_PARTIAL_CRITERIA_ACTIVE
        reasons.append(_reason("NO_PARTIAL_CRITERIA_ACTIVE"))
    else:
        minimum = max(
            criteria[criterion_id]["coverage"]["minimum_valid_country_count"]
            for criterion_id in pcc
        )
        if len(eligible) < minimum:
            status = CoverageStatus.COVERAGE_LIMIT_FALLBACK
            reasons.append(
                _reason(
                    "PCC_COMPLETE_CASE_BELOW_LIMIT",
                    severity=ReasonSeverity.WARNING,
                    effect=ReasonEffect.RANKING_FALLBACK,
                )
            )
            pcc = ()
            active = fcc
            if not active:
                raise Phase5RankingError(
                    "Coverage fallback removed every active ranking criterion."
                )
            eligible = tuple(
                country_id
                for country_id in countries
                if all(
                    outcomes.get((criterion_id, country_id), {}).get("outcome") == "valid"
                    for criterion_id in active
                )
            )
        elif len(eligible) == len(countries):
            status = CoverageStatus.FULL_COVERAGE
            reasons.extend(_reason(f"PCC_ACTIVE:{criterion_id}") for criterion_id in pcc)
        else:
            status = CoverageStatus.PARTIAL_COMPLETE_CASE
            reasons.extend(_reason(f"PCC_ACTIVE:{criterion_id}") for criterion_id in pcc)
    excluded = tuple(sorted(set(countries) - set(eligible)))
    reasons.extend(
        _reason(
            f"COUNTRY_EXCLUDED:{country_id.removeprefix('country:')}",
            severity=ReasonSeverity.WARNING,
            effect=ReasonEffect.COUNTRY_EXCLUDED,
        )
        for country_id in excluded
    )
    assessment = CoverageAssessment(
        status=status,
        policy_version=coverage_policy_version,
        active_global_core_criterion_ids=fcc,
        active_conditional_criterion_ids=pcc,
        excluded_country_entity_ids=excluded,
        reasons=tuple(reasons),
    )
    return assessment, fcc, pcc, eligible


def _locality_score_maps(
    release: Schema5Release,
    criterion: dict[str, Any],
    country_id: str,
) -> tuple[tuple[str, ...], dict[str, float]]:
    artifacts = release.artifacts
    universes = {row["locality_universe_id"]: row for row in artifacts.locality_universes}
    entities = {row["entity_id"]: row for row in artifacts.geographic_entities}
    universe = universes[criterion["scope"]["locality_universe_id"]]
    aggregation_policies = {row["policy_id"]: row for row in artifacts.aggregation_policies}
    source_criterion_id = aggregation_policies[criterion["scope"]["aggregation_policy_id"]][
        "source_criterion_id"
    ]
    country_code = country_id.removeprefix("country:")
    observations = {row["observation_id"]: row for row in artifacts.observations}
    eligible = tuple(
        sorted(
            entity_id
            for entity_id in universe["entity_ids"]
            if country_code in entities[entity_id]["country_codes"]
        )
    )
    scores: dict[str, float] = {}
    for row in artifacts.scores:
        entity_id = row["subject"]["entity_id"]
        if (
            row["criterion_id"] != source_criterion_id
            or row["subject"]["entity_type"] == "COUNTRY"
            or entity_id not in eligible
        ):
            continue
        flags = set(row.get("quality_flags", []))
        for observation_id in row["observation_ids"]:
            observation = observations.get(observation_id)
            if (
                observation is None
                or observation["criterion_id"] != row["criterion_id"]
                or observation["subject"] != row["subject"]
            ):
                raise Phase5RankingError(
                    f"Locality score {row['score_id']} has broken observation lineage."
                )
            flags.update(observation.get("quality_flags", []))
        if flags & (DISQUALIFYING_STALE_FLAGS | DISQUALIFYING_INVALID_FLAGS):
            continue
        if entity_id in scores:
            raise Phase5RankingError(f"Criterion has duplicate locality scores for {entity_id}.")
        scores[entity_id] = row["score"]
    return eligible, scores


def _best_common_locality(
    *,
    common_ids: set[str],
    scores_by_criterion: dict[str, dict[str, float]],
    normalized_weights: dict[str, float],
) -> str:
    total_weight = sum(
        Decimal(str(normalized_weights[criterion_id])) for criterion_id in scores_by_criterion
    )
    ranked = []
    for entity_id in common_ids:
        weighted_score = (
            sum(
                Decimal(str(scores[entity_id])) * Decimal(str(normalized_weights[criterion_id]))
                for criterion_id, scores in scores_by_criterion.items()
            )
            / total_weight
        )
        ranked.append((-weighted_score, entity_id))
    return min(ranked)[1]


def _country_locality_assessment(
    *,
    release: Schema5Release,
    country_id: str,
    contributing_ids: tuple[str, ...],
    triggered_ids: tuple[str, ...],
    criteria: dict[str, dict[str, Any]],
    normalized_weights: dict[str, float],
    evidence_by_key: dict[tuple[str, str], dict[str, Any]],
) -> CountryLocalityAssessment:
    criterion_evidence = []
    scores_by_criterion: dict[str, dict[str, float]] = {}
    contributing_union: set[str] = set()
    eligible_union: set[str] = set()
    valid_union: set[str] = set()
    for criterion_id in contributing_ids:
        eligible, valid_scores = _locality_score_maps(release, criteria[criterion_id], country_id)
        evidence = evidence_by_key.get((criterion_id, country_id))
        contributing = tuple(
            sorted(
                row["locality"]["entity_id"]
                for row in (evidence or {}).get("contributing_localities", [])
            )
        )
        eligible_union.update(eligible)
        valid_union.update(valid_scores)
        contributing_union.update(contributing)
        criterion_evidence.append(
            CriterionLocalityEvidence(
                criterion_id=criterion_id,
                eligible_locality_entity_ids=eligible,
                valid_locality_entity_ids=tuple(sorted(valid_scores)),
                contributing_locality_entity_ids=contributing,
            )
        )
        if criterion_id in triggered_ids:
            scores_by_criterion[criterion_id] = valid_scores

    common: set[str] = set()
    best_common = None
    if not contributing_ids:
        status = LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA
        reasons = (_reason("NO_LOCALITY_CRITERIA_CONTRIBUTING"),)
    elif not triggered_ids:
        status = LocalityStatus.BELOW_ANALYSIS_THRESHOLD
        reasons = (
            _reason(
                "LOCALITY_ANALYSIS_BELOW_THRESHOLD",
                effect=ReasonEffect.ADVISORY,
            ),
        )
    elif len(triggered_ids) == 1:
        if not next(iter(scores_by_criterion.values())):
            status = LocalityStatus.INSUFFICIENT_LOCALITY_EVIDENCE
            reasons = (
                _reason(
                    "ACTIVE_LOCALITY_CRITERION_HAS_NO_VALID_LOCALITY",
                    severity=ReasonSeverity.WARNING,
                    effect=ReasonEffect.ADVISORY,
                ),
            )
        else:
            status = LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION
            reasons = (
                _reason(
                    "COMMON_LOCALITY_NOT_APPLICABLE_SINGLE_CRITERION",
                    effect=ReasonEffect.NONE,
                ),
            )
    elif any(not values for values in scores_by_criterion.values()):
        status = LocalityStatus.INSUFFICIENT_LOCALITY_EVIDENCE
        reasons = (
            _reason(
                "INSUFFICIENT_VALID_LOCALITY_EVIDENCE",
                severity=ReasonSeverity.WARNING,
                effect=ReasonEffect.ADVISORY,
            ),
        )
    else:
        valid_sets = [set(values) for values in scores_by_criterion.values()]
        common = set.intersection(*valid_sets)
        if common:
            status = LocalityStatus.COMMON_LOCALITY_AVAILABLE
            best_common = _best_common_locality(
                common_ids=common,
                scores_by_criterion=scores_by_criterion,
                normalized_weights=normalized_weights,
            )
            reasons = (_reason(f"BEST_COMMON_LOCALITY:{best_common.replace(':', '.')}"),)
        elif any(left & right for left, right in combinations(valid_sets, 2)):
            status = LocalityStatus.PARTIAL_OVERLAP
            reasons = (
                _reason(
                    "PAIRWISE_LOCALITY_OVERLAP_ONLY",
                    severity=ReasonSeverity.WARNING,
                    effect=ReasonEffect.ADVISORY,
                ),
            )
        else:
            status = LocalityStatus.NO_COMMON_LOCALITY
            reasons = (
                _reason(
                    "NO_COMMON_VALID_LOCALITY",
                    severity=ReasonSeverity.WARNING,
                    effect=ReasonEffect.ADVISORY,
                ),
            )
    return CountryLocalityAssessment(
        status=status,
        eligible_locality_entity_ids=tuple(sorted(eligible_union)),
        valid_locality_entity_ids=tuple(sorted(valid_union)),
        contributing_locality_entity_ids=tuple(sorted(contributing_union)),
        common_locality_entity_ids=tuple(sorted(common)),
        best_common_locality_entity_id=best_common,
        criterion_evidence=tuple(criterion_evidence),
        reasons=reasons,
    )


def _response_locality_assessment(
    *,
    contributing_ids: tuple[str, ...],
    triggered_ids: tuple[str, ...],
    criteria: dict[str, dict[str, Any]],
    country_assessments: dict[str, CountryLocalityAssessment],
) -> ResponseLocalityAssessment:
    below = tuple(sorted(set(contributing_ids) - set(triggered_ids)))
    thresholds = {
        criterion_id: criteria[criterion_id]["scope"]["locality_analysis_threshold"]
        for criterion_id in contributing_ids
    }
    policies = tuple(
        sorted(
            {
                criteria[criterion_id]["scope"]["aggregation_policy_id"]
                for criterion_id in contributing_ids
            }
        )
    )
    if not contributing_ids:
        status = LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA
    elif not triggered_ids:
        status = LocalityStatus.BELOW_ANALYSIS_THRESHOLD
    elif len(triggered_ids) == 1:
        status = LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION
    else:
        statuses = {item.status for item in country_assessments.values()}
        status = (
            next(iter(statuses)) if len(statuses) == 1 else LocalityStatus.MIXED_COUNTRY_RESULTS
        )
    reason_by_status = {
        LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA: "NO_LOCALITY_CRITERIA_CONTRIBUTING",
        LocalityStatus.BELOW_ANALYSIS_THRESHOLD: "LOCALITY_ANALYSIS_BELOW_THRESHOLD",
        LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION: "LOCALITY_ANALYSIS_SINGLE_CRITERION",
        LocalityStatus.COMMON_LOCALITY_AVAILABLE: "COMMON_LOCALITY_AVAILABLE_ALL_COUNTRIES",
        LocalityStatus.PARTIAL_OVERLAP: "PARTIAL_LOCALITY_OVERLAP_ALL_COUNTRIES",
        LocalityStatus.NO_COMMON_LOCALITY: "NO_COMMON_LOCALITY_ALL_COUNTRIES",
        LocalityStatus.INSUFFICIENT_LOCALITY_EVIDENCE: (
            "INSUFFICIENT_LOCALITY_EVIDENCE_ALL_COUNTRIES"
        ),
        LocalityStatus.MIXED_COUNTRY_RESULTS: "MIXED_COUNTRY_LOCALITY_RESULTS",
    }
    severity = (
        ReasonSeverity.WARNING
        if status
        in {
            LocalityStatus.PARTIAL_OVERLAP,
            LocalityStatus.NO_COMMON_LOCALITY,
            LocalityStatus.INSUFFICIENT_LOCALITY_EVIDENCE,
            LocalityStatus.MIXED_COUNTRY_RESULTS,
        }
        else ReasonSeverity.INFO
    )
    effect = (
        ReasonEffect.ADVISORY
        if status != LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA
        else ReasonEffect.NONE
    )
    return ResponseLocalityAssessment(
        status=status,
        policy_version=LOCALITY_ASSESSMENT_POLICY_VERSION,
        contributing_criterion_ids=contributing_ids,
        analysis_triggered_criterion_ids=triggered_ids,
        below_threshold_criterion_ids=below,
        analysis_thresholds=thresholds,
        aggregation_policy_ids=policies,
        reasons=(_reason(reason_by_status[status], severity=severity, effect=effect),),
    )


def rank_schema5_release(
    release: Schema5Release,
    weights: Mapping[str, float],
    *,
    resolved_preference_preset_id: str | None = None,
    top_k: int | None = None,
) -> Phase5RankingResult:
    """Rank a validated schema-5 release without coupling locality advice to coverage."""

    if not release.validation["structural_passed"]:
        raise Phase5RankingError("A structurally invalid schema-5 release cannot be ranked.")
    artifacts = release.artifacts
    criteria = {row["id"]: row for row in artifacts.consumer_catalog["criteria"]}
    raw_weights = _validated_raw_weights(weights, criteria)
    countries = tuple(
        sorted(
            row["entity_id"]
            for row in artifacts.geographic_entities
            if row["entity_type"] == "COUNTRY"
        )
    )
    outcomes = {
        (row["criterion_id"], row["subject"]["entity_id"]): row
        for row in artifacts.criterion_outcomes
    }
    coverage, fcc, pcc, eligible = _activate_coverage(
        criteria=criteria,
        raw_weights=raw_weights,
        countries=countries,
        outcomes=outcomes,
        coverage_policy_version=artifacts.consumer_catalog["coverage_policy_version"],
    )
    active_ids = tuple(sorted((*fcc, *pcc)))
    normalized = normalize_weights(
        {criterion_id: raw_weights[criterion_id] for criterion_id in active_ids},
        active_ids,
    )

    contributing_lsc = tuple(
        criterion_id
        for criterion_id in active_ids
        if criteria[criterion_id]["scope"]["derivation"] == "AGGREGATED_FROM_LOCALITIES"
        and raw_weights[criterion_id] > 0
    )
    triggered_lsc = tuple(
        criterion_id
        for criterion_id in contributing_lsc
        if raw_weights[criterion_id]
        >= criteria[criterion_id]["scope"]["locality_analysis_threshold"]
    )
    evidence_by_key = {
        (row["result_criterion_id"], row["country"]["entity_id"]): row
        for row in artifacts.derived_country_evidence
    }
    country_locality = {
        country_id: _country_locality_assessment(
            release=release,
            country_id=country_id,
            contributing_ids=contributing_lsc,
            triggered_ids=triggered_lsc,
            criteria=criteria,
            normalized_weights=normalized,
            evidence_by_key=evidence_by_key,
        )
        for country_id in countries
    }
    locality = _response_locality_assessment(
        contributing_ids=contributing_lsc,
        triggered_ids=triggered_lsc,
        criteria=criteria,
        country_assessments=country_locality,
    )
    profile = ProfileAssessment(
        status=ProfileStatus.NO_PROFILE_CONTEXT,
        evaluated_dimensions=(),
        reasons=(
            _reason(
                "PROFILE_CONTEXT_NOT_SUPPLIED",
                effect=ReasonEffect.NOT_EVALUATED,
            ),
        ),
    )

    scores = {
        (row["criterion_id"], row["subject"]["entity_id"]): row
        for row in artifacts.scores
        if row["subject"]["entity_type"] == "COUNTRY"
    }
    ranked: list[Phase5RankedCountry] = []
    for country_id in eligible:
        contributions = []
        for criterion_id in active_ids:
            outcome = outcomes[(criterion_id, country_id)]
            score = scores.get((criterion_id, country_id))
            if outcome["outcome"] != "valid" or score is None:
                raise Phase5RankingError(
                    f"Eligible country lacks a complete result for {country_id}/{criterion_id}."
                )
            if score["score_id"] != outcome["score_id"]:
                raise Phase5RankingError("Country score and outcome lineage disagree.")
            contribution = _round(
                Decimal(str(score["score"])) * Decimal(str(normalized[criterion_id]))
            )
            contributions.append(
                Phase5Contribution(
                    criterion_id=criterion_id,
                    score=score["score"],
                    normalized_weight=normalized[criterion_id],
                    contribution=contribution,
                    observation_id=outcome["observation_id"],
                    score_id=outcome["score_id"],
                    evidence_kind=outcome["evidence_kind"],
                    derived_evidence_id=outcome["derived_evidence_id"],
                )
            )
        total = _round(sum((Decimal(str(row.contribution)) for row in contributions), Decimal()))
        ranked.append(
            Phase5RankedCountry(
                rank=0,
                country={"entity_id": country_id, "entity_type": "COUNTRY"},
                total_score=total,
                contributions=tuple(contributions),
                locality_assessment=country_locality[country_id],
                profile_assessment=profile,
            )
        )
    ranked.sort(key=lambda row: (-row.total_score, row.country["entity_id"]))
    ranked = [
        Phase5RankedCountry(
            rank=index,
            country=row.country,
            total_score=row.total_score,
            contributions=row.contributions,
            locality_assessment=row.locality_assessment,
            profile_assessment=row.profile_assessment,
        )
        for index, row in enumerate(ranked, 1)
    ]
    if top_k is not None:
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise Phase5RankingError("top_k must be a positive integer.")
        ranked = ranked[:top_k]
    return Phase5RankingResult(
        release_id=release.manifest["release_id"],
        release_schema_version=release.manifest["schema_version"],
        catalog_schema_version=artifacts.consumer_catalog["schema_version"],
        resolved_preference_preset_id=resolved_preference_preset_id,
        normalized_weights=normalized,
        coverage_assessment=coverage,
        locality_assessment=locality,
        profile_assessment=profile,
        rankings=tuple(ranked),
        country_locality_assessments=country_locality,
    )
