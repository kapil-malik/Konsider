"""Structural validation for schema-4 mixed-coverage releases."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
import re

from konsider.ingestion.models import (
    CoverageMode,
    CriterionCoverage,
    CriterionOutcome,
    MetricObservation,
    MetricScore,
    ValidationIssue,
    ValidationReport,
)

COVERAGE_POLICY_VERSION = "uncertainty-aware-ranking-policy-1.0"
VALID_OUTCOMES = frozenset({"valid", "missing", "stale", "invalid", "rejected"})
MINIMUM_PCC_COUNTRIES = 82


def validate_coverage_release(
    *,
    stable_country_codes: Iterable[str],
    stable_universe_id: str,
    coverage: Iterable[CriterionCoverage],
    outcomes: Iterable[CriterionOutcome],
    observations: Iterable[MetricObservation],
    scores: Iterable[MetricScore],
    minimum_global_core_count: int,
    policy_version: str = COVERAGE_POLICY_VERSION,
) -> ValidationReport:
    """Validate exact country outcomes and score reconciliation without source I/O."""

    countries = tuple(stable_country_codes)
    country_set = set(countries)
    policies = {item.criterion_id: item for item in coverage}
    outcome_rows = tuple(outcomes)
    observation_rows = tuple(observations)
    score_rows = tuple(scores)
    issues: list[ValidationIssue] = []

    def error(code: str, message: str, criterion_id: str | None = None) -> None:
        issues.append(
            ValidationIssue(
                code,
                "error",
                message,
                metric_id=criterion_id,
            )
        )

    if len(country_set) != len(countries):
        error("stable_universe_duplicate_country", "Stable country universe contains duplicates.")
    if len(countries) != 91:
        error("stable_universe_size", "Schema-4 releases require the stable 91-country universe.")
    if minimum_global_core_count < 0:
        error(
            "invalid_global_core_minimum",
            "Minimum global-core criterion count cannot be negative.",
        )
    if policy_version != COVERAGE_POLICY_VERSION:
        error(
            "unsupported_coverage_policy",
            f"Coverage policy must be {COVERAGE_POLICY_VERSION}.",
        )
    if len(policies) == 0:
        error("criterion_coverage_missing", "At least one criterion coverage policy is required.")

    outcome_by_pair: dict[tuple[str, str], CriterionOutcome] = {}
    for row in outcome_rows:
        pair = (row.criterion_id, row.country_code)
        if pair in outcome_by_pair:
            error(
                "duplicate_country_outcome",
                f"Duplicate country outcome for {pair}.",
                row.criterion_id,
            )
            continue
        outcome_by_pair[pair] = row
        if row.criterion_id not in policies or row.country_code not in country_set:
            error(
                "unknown_country_outcome",
                f"Outcome references unknown pair {pair}.",
                row.criterion_id,
            )
        if row.outcome not in VALID_OUTCOMES:
            error(
                "invalid_country_outcome", f"Unsupported outcome {row.outcome!r}.", row.criterion_id
            )
        if row.outcome == "valid":
            if not row.observation_id or row.reason_codes:
                error(
                    "valid_outcome_malformed",
                    f"Valid outcome {pair} requires an observation and no reason codes.",
                    row.criterion_id,
                )
        elif row.observation_id or not row.reason_codes:
            error(
                "non_valid_outcome_malformed",
                f"Non-valid outcome {pair} requires reason codes and no observation.",
                row.criterion_id,
            )
        elif any(
            re.fullmatch(r"[A-Z][A-Z0-9_]*(?::[A-Za-z0-9_.-]+)?", code) is None
            for code in row.reason_codes
        ):
            error(
                "invalid_outcome_reason_code",
                f"Outcome {pair} contains a non-normalized reason code.",
                row.criterion_id,
            )

    expected_pairs = {(criterion, country) for criterion in policies for country in countries}
    missing_pairs = sorted(expected_pairs - set(outcome_by_pair))
    if missing_pairs:
        error(
            "attempt_matrix_incomplete",
            f"Every criterion requires one outcome for every stable country; missing {missing_pairs[:3]}.",
        )
    extra_pairs = sorted(set(outcome_by_pair) - expected_pairs)
    if extra_pairs:
        error("attempt_matrix_extra", f"Unexpected country outcomes {extra_pairs[:3]}.")

    observation_by_id = {item.observation_id: item for item in observation_rows}
    if len(observation_by_id) != len(observation_rows):
        error("duplicate_observation_id", "Observation IDs must be unique.")
    for pair, outcome in outcome_by_pair.items():
        if outcome.outcome != "valid":
            continue
        observation = observation_by_id.get(outcome.observation_id or "")
        expected_pair = (outcome.criterion_id, outcome.country_code)
        if observation is None:
            error(
                "valid_outcome_observation_missing",
                f"Valid outcome {pair} references a missing observation.",
                outcome.criterion_id,
            )
        elif (observation.metric_id, observation.country_code) != expected_pair:
            error(
                "outcome_observation_mismatch",
                f"Valid outcome {pair} references an inconsistent observation.",
                outcome.criterion_id,
            )
    score_by_pair: dict[tuple[str, str], MetricScore] = {}
    for score in score_rows:
        pair = (score.criterion_id, score.country_code)
        if pair in score_by_pair:
            error("duplicate_score_pair", f"Duplicate score for {pair}.", score.criterion_id)
            continue
        score_by_pair[pair] = score
        policy = policies.get(score.criterion_id)
        outcome = outcome_by_pair.get(pair)
        if not policy or score.country_code not in country_set:
            error(
                "unknown_score_pair", f"Score references unknown pair {pair}.", score.criterion_id
            )
            continue
        if outcome is None or outcome.outcome != "valid":
            error(
                "score_for_non_valid_outcome",
                f"Score exists for non-valid outcome {pair}.",
                score.criterion_id,
            )
        if not policy.score_min <= score.score <= policy.score_max:
            error(
                "score_out_of_allowed_range",
                f"Score for {pair} is outside the criterion range.",
                score.criterion_id,
            )
        if score.method_version != policy.scoring_method_version:
            error(
                "scoring_version_mismatch",
                f"Scoring version disagrees for {pair}.",
                score.criterion_id,
            )
        for observation_id in score.input_observation_ids:
            observation = observation_by_id.get(observation_id)
            if observation is None:
                error(
                    "missing_input_observation",
                    f"Score {pair} references {observation_id}.",
                    score.criterion_id,
                )
            elif (observation.metric_id, observation.country_code) != pair:
                error(
                    "observation_score_mismatch",
                    f"Observation {observation_id} disagrees with {pair}.",
                    score.criterion_id,
                )

    readiness: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, CriterionCoverage] = {}
    for criterion_id, policy in policies.items():
        rows = [
            row
            for pair, row in outcome_by_pair.items()
            if pair[0] == criterion_id and pair in expected_pairs
        ]
        outcome_counts = Counter(row.outcome for row in rows)
        valid_pairs = {
            (row.criterion_id, row.country_code) for row in rows if row.outcome == "valid"
        }
        valid_count = len(valid_pairs)
        counts[criterion_id] = valid_count
        details[criterion_id] = policy

        if policy.stable_universe_id != stable_universe_id or policy.stable_country_count != len(
            countries
        ):
            error(
                "stable_universe_mismatch",
                f"Stable universe metadata disagrees for {criterion_id}.",
                criterion_id,
            )
        if policy.valid_country_count != valid_count or policy.outcome_counts != {
            key: outcome_counts.get(key, 0) for key in sorted(VALID_OUTCOMES)
        }:
            error(
                "coverage_count_mismatch",
                f"Coverage counts disagree for {criterion_id}.",
                criterion_id,
            )
        if policy.score_min > policy.score_max:
            error(
                "invalid_allowed_score_range",
                f"Allowed score range is inverted for {criterion_id}.",
                criterion_id,
            )
        if set(score_by_pair).intersection(valid_pairs) != valid_pairs or any(
            pair[0] == criterion_id and pair not in valid_pairs for pair in score_by_pair
        ):
            error(
                "valid_score_count_mismatch",
                f"Valid outcomes and scores do not reconcile for {criterion_id}.",
                criterion_id,
            )

        mode_ready = False
        if policy.mode == CoverageMode.GLOBAL_CORE:
            if valid_count != len(countries) or policy.minimum_valid_country_count != len(
                countries
            ):
                error(
                    "global_core_incomplete",
                    f"GLOBAL_CORE {criterion_id} must be complete.",
                    criterion_id,
                )
            if policy.activation_threshold is not None:
                error(
                    "global_core_activation_threshold",
                    f"GLOBAL_CORE {criterion_id} cannot have a PCC threshold.",
                    criterion_id,
                )
            mode_ready = valid_count == len(countries)
        elif policy.mode == CoverageMode.CONDITIONAL_COMPLETE_CASE:
            if policy.minimum_valid_country_count < MINIMUM_PCC_COUNTRIES:
                error(
                    "pcc_minimum_too_low",
                    f"PCC {criterion_id} minimum must be at least 82.",
                    criterion_id,
                )
            if not (
                policy.activation_threshold is not None
                and 0.0 <= policy.activation_threshold <= 1.0
            ):
                error(
                    "invalid_activation_threshold",
                    f"PCC {criterion_id} threshold must be in [0, 1].",
                    criterion_id,
                )
            if valid_count < policy.minimum_valid_country_count:
                error(
                    "pcc_coverage_insufficient",
                    f"PCC {criterion_id} is below its coverage minimum.",
                    criterion_id,
                )
            mode_ready = valid_count >= policy.minimum_valid_country_count
        elif policy.mode == CoverageMode.DIAGNOSTIC_ONLY:
            mode_ready = False
        else:
            error(
                "invalid_coverage_mode", f"Unknown coverage mode for {criterion_id}.", criterion_id
            )
        readiness[criterion_id] = mode_ready

    structural_passed = not any(item.severity == "error" for item in issues)
    global_core_ready_count = sum(
        readiness.get(key, False) and item.mode == CoverageMode.GLOBAL_CORE
        for key, item in policies.items()
    )
    product_ready = structural_passed and global_core_ready_count >= minimum_global_core_count
    return ValidationReport(
        structural_passed=structural_passed,
        product_ready=product_ready,
        observation_count=len(observation_rows),
        score_count=len(score_rows),
        attempt_count=len(outcome_rows),
        criterion_coverage=counts,
        criterion_readiness=readiness,
        ready_criterion_count=sum(readiness.values()),
        status_counts=dict(Counter(row.outcome for row in outcome_rows)),
        issues=tuple(issues),
        schema_version="validation-4.0",
        coverage_policy_version=policy_version,
        stable_universe_id=stable_universe_id,
        stable_country_count=len(countries),
        criterion_coverage_details=details,
        global_core_ready_count=global_core_ready_count,
        minimum_global_core_count=minimum_global_core_count,
    )
