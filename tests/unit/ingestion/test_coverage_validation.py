from dataclasses import replace

from konsider.ingestion.countries import COUNTRIES
from konsider.ingestion.coverage_validation import validate_coverage_release
from konsider.ingestion.models import (
    CoverageMode,
    CriterionCoverage,
    CriterionOutcome,
    MetricObservation,
    MetricScore,
    SourceRecordReference,
)

UNIVERSE_ID = "stable_supported_v1"


def _criterion(
    criterion_id: str,
    mode: CoverageMode,
    valid_count: int,
) -> CriterionCoverage:
    non_valid = 91 - valid_count
    return CriterionCoverage(
        criterion_id=criterion_id,
        mode=mode,
        stable_universe_id=UNIVERSE_ID,
        stable_country_count=91,
        valid_country_count=valid_count,
        minimum_valid_country_count=(91 if mode == CoverageMode.GLOBAL_CORE else 82),
        outcome_counts={
            "invalid": 1 if non_valid >= 3 else 0,
            "missing": max(0, non_valid - 2),
            "rejected": 0,
            "stale": min(non_valid, 1),
            "valid": valid_count,
        },
        activation_threshold=(0.6 if mode == CoverageMode.CONDITIONAL_COMPLETE_CASE else None),
        experimental=mode != CoverageMode.GLOBAL_CORE,
        source_versions={f"{criterion_id}-source": "fixture-v1"},
        scoring_method_version=f"{criterion_id}-score-v1",
    )


def _rows(policy: CriterionCoverage):
    observations = []
    scores = []
    outcomes = []
    for index, country_code in enumerate(COUNTRIES):
        if index < policy.valid_country_count:
            observation_id = f"{policy.criterion_id}-{country_code}"
            observations.append(
                MetricObservation(
                    observation_id=observation_id,
                    country_code=country_code,
                    metric_id=policy.criterion_id,
                    value=50,
                    unit="fixture",
                    reference_start="2025-01-01",
                    reference_end="2025-12-31",
                    source_id=f"{policy.criterion_id}-source",
                    raw_artifact_ids=("sha256:fixture",),
                    source_records=(
                        SourceRecordReference(
                            "sha256:fixture",
                            f"$[{index}]",
                            country_code,
                        ),
                    ),
                    observation_type="fixture",
                    geographic_scope="national",
                    parser_version="fixture-parser-v1",
                    method_version=policy.scoring_method_version,
                )
            )
            scores.append(
                MetricScore(
                    country_code=country_code,
                    criterion_id=policy.criterion_id,
                    score=5,
                    input_observation_ids=(observation_id,),
                    method_version=policy.scoring_method_version,
                    transform="fixture",
                    direction="higher_is_better",
                )
            )
            outcome = "valid"
            reasons = ()
        else:
            offset = index - policy.valid_country_count
            outcome = ("stale", "missing", "invalid")[min(offset, 2)]
            reasons = {
                "stale": ("FRS_STALE",),
                "missing": ("COV_SOURCE_RECORD_MISSING",),
                "invalid": ("VAL_COMPONENT_MISSING:fixture",),
            }[outcome]
            observation_id = None
        outcomes.append(
            CriterionOutcome(
                criterion_id=policy.criterion_id,
                country_code=country_code,
                outcome=outcome,
                source_id=f"{policy.criterion_id}-source",
                attempted_at="2026-07-27T00:00:00+00:00",
                observation_id=observation_id,
                reason_codes=reasons,
            )
        )
    return observations, scores, outcomes


def _validate(policies):
    observations = []
    scores = []
    outcomes = []
    for policy in policies:
        criterion_observations, criterion_scores, criterion_outcomes = _rows(policy)
        observations.extend(criterion_observations)
        scores.extend(criterion_scores)
        outcomes.extend(criterion_outcomes)
    return validate_coverage_release(
        stable_country_codes=COUNTRIES,
        stable_universe_id=UNIVERSE_ID,
        coverage=policies,
        outcomes=outcomes,
        observations=observations,
        scores=scores,
        minimum_global_core_count=1,
    )


def test_91_fcc_and_88_pcc_pass_with_mixed_outcomes() -> None:
    report = _validate(
        [
            _criterion("fcc", CoverageMode.GLOBAL_CORE, 91),
            _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 88),
        ]
    )

    assert report.structural_passed
    assert report.product_ready
    assert report.criterion_coverage == {"fcc": 91, "pcc": 88}
    assert report.status_counts["stale"] == 1
    assert report.status_counts["missing"] == 1
    assert report.status_counts["invalid"] == 1


def test_81_of_91_pcc_fails() -> None:
    pcc = _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 81)
    pcc = replace(
        pcc,
        outcome_counts={
            "invalid": 8,
            "missing": 1,
            "rejected": 0,
            "stale": 1,
            "valid": 81,
        },
    )

    report = _validate([_criterion("fcc", CoverageMode.GLOBAL_CORE, 91), pcc])

    assert not report.structural_passed
    assert "pcc_coverage_insufficient" in {issue.code for issue in report.issues}


def test_score_and_attempt_mismatch_fails() -> None:
    policy = _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 88)
    observations, scores, outcomes = _rows(policy)

    report = validate_coverage_release(
        stable_country_codes=COUNTRIES,
        stable_universe_id=UNIVERSE_ID,
        coverage=[policy],
        outcomes=outcomes,
        observations=observations,
        scores=scores[:-1],
        minimum_global_core_count=0,
    )

    assert not report.structural_passed
    assert "valid_score_count_mismatch" in {issue.code for issue in report.issues}


def test_stale_and_missing_reason_codes_are_preserved() -> None:
    policy = _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 88)
    _, _, outcomes = _rows(policy)

    non_valid = {item.outcome: item.reason_codes for item in outcomes if item.outcome != "valid"}

    assert non_valid["stale"] == ("FRS_STALE",)
    assert non_valid["missing"] == ("COV_SOURCE_RECORD_MISSING",)


def test_missing_country_outcome_fails() -> None:
    policy = _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 88)
    observations, scores, outcomes = _rows(policy)

    report = validate_coverage_release(
        stable_country_codes=COUNTRIES,
        stable_universe_id=UNIVERSE_ID,
        coverage=[policy],
        outcomes=outcomes[:-1],
        observations=observations,
        scores=scores,
        minimum_global_core_count=0,
    )

    assert not report.structural_passed
    assert "attempt_matrix_incomplete" in {issue.code for issue in report.issues}


def test_activation_threshold_outside_range_fails() -> None:
    policy = replace(
        _criterion("pcc", CoverageMode.CONDITIONAL_COMPLETE_CASE, 88),
        activation_threshold=1.1,
    )

    report = _validate([policy])

    assert not report.structural_passed
    assert "invalid_activation_threshold" in {issue.code for issue in report.issues}
