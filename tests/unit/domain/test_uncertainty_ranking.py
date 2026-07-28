import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from konsider.domain.uncertainty_models import CoverageBand, UncertaintyStatus
from konsider.domain.uncertainty_ranking import rank_release_with_uncertainty
from konsider.exceptions import InvalidTopKError, RankingIntegrityError
from konsider.ingestion.countries import COUNTRY_RECORDS
from konsider.repositories.published_release_repository import PublishedMetricRecord

FCC_ID = "fcc"
ROOT = Path(__file__).resolve().parents[3]
GOLDEN = json.loads(
    (ROOT / "tests" / "fixtures" / "phase4d" / "golden-scenarios.json").read_text(encoding="utf-8")
)


def _criterion(criterion_id: str, mode: str) -> dict:
    source_id = f"{criterion_id}-source"
    return {
        "id": criterion_id,
        "display_name": criterion_id.upper(),
        "category": "fixture",
        "description": "Synthetic ranking fixture.",
        "direction": "higher_is_better",
        "raw_unit": "fixture",
        "interpretation": "Synthetic only.",
        "caveats": [],
        "quality_limitations": [],
        "ready": True,
        "default_enabled": True,
        "experimental": mode != "GLOBAL_CORE",
        "scoring_method_version": f"{criterion_id}-score-v1",
        "coverage": {
            "criterion_id": criterion_id,
            "mode": mode,
            "stable_universe_id": "stable_supported_v1",
            "stable_country_count": 91,
            "valid_country_count": 91,
            "minimum_valid_country_count": (91 if mode == "GLOBAL_CORE" else 82),
            "outcome_counts": {
                "valid": 91,
                "missing": 0,
                "stale": 0,
                "invalid": 0,
                "rejected": 0,
            },
            "activation_threshold": (None if mode == "GLOBAL_CORE" else 0.6),
            "experimental": mode != "GLOBAL_CORE",
            "source_versions": {source_id: f"{source_id}-v1"},
            "scoring_method_version": f"{criterion_id}-score-v1",
            "score_min": 1,
            "score_max": 10,
        },
    }


def _record(country: dict, criterion: dict, score: float) -> PublishedMetricRecord:
    criterion_id = criterion["id"]
    source_id = f"{criterion_id}-source"
    observation_id = f"{criterion_id}-{country['code']}"
    return PublishedMetricRecord(
        country=country,
        criterion=criterion,
        score={
            "country_code": country["code"],
            "criterion_id": criterion_id,
            "score": score,
            "input_observation_ids": [observation_id],
            "method_version": f"{criterion_id}-score-v1",
            "transform": "fixture",
            "direction": "higher_is_better",
        },
        observations=(
            {
                "observation_id": observation_id,
                "country_code": country["code"],
                "metric_id": criterion_id,
                "value": score,
                "unit": "fixture",
                "reference_start": "2025-01-01",
                "reference_end": "2025-12-31",
                "source_id": source_id,
                "method_version": f"{criterion_id}-score-v1",
                "parser_version": "phase4d-fixture-parser-v1",
            },
        ),
        source={
            "source_id": source_id,
            "publisher": "Phase 4D fixture",
            "source_version": f"{source_id}-v1",
            "dataset_version": "phase4d-fixture-v1",
            "canonical_page_url": "https://example.invalid/phase4d",
            "attribution": "Synthetic fixture.",
        },
    )


def _release(
    missing_sets: list[set[str]],
    *,
    fcc_score=None,
    pcc_score=None,
    fcc_count: int = 1,
):
    pcc_ids = [f"pcc_{index + 1}" for index in range(len(missing_sets))]
    fcc_ids = [FCC_ID, *[f"fcc_{index + 2}" for index in range(fcc_count - 1)]]
    criteria = [
        *[_criterion(criterion_id, "GLOBAL_CORE") for criterion_id in fcc_ids],
        *[_criterion(criterion_id, "CONDITIONAL_COMPLETE_CASE") for criterion_id in pcc_ids],
    ]
    criterion_by_id = {item["id"]: item for item in criteria}
    union = set().union(*missing_sets) if missing_sets else set()
    records = []
    outcomes = []
    for country_index, country in enumerate(COUNTRY_RECORDS):
        country_code = country["code"]
        for criterion_id in fcc_ids:
            score = (
                fcc_score(country_code, union)
                if fcc_score
                else (1.0 if country_code in union else 10.0)
            )
            records.append(_record(country, criterion_by_id[criterion_id], score))
        for criterion_id, missing in zip(pcc_ids, missing_sets, strict=True):
            if country_code in missing:
                outcomes.append(
                    {
                        "criterion_id": criterion_id,
                        "country_code": country_code,
                        "outcome": "stale" if country_index % 2 else "missing",
                        "source_id": f"{criterion_id}-source",
                        "attempted_at": "2026-07-27T00:00:00+00:00",
                        "observation_id": None,
                        "reason_codes": (
                            ["FRS_STALE"] if country_index % 2 else ["COV_SOURCE_RECORD_MISSING"]
                        ),
                    }
                )
            else:
                score = pcc_score(country_code, union) if pcc_score else 10.0
                record = _record(country, criterion_by_id[criterion_id], score)
                records.append(record)
                outcomes.append(
                    {
                        "criterion_id": criterion_id,
                        "country_code": country_code,
                        "outcome": "valid",
                        "source_id": f"{criterion_id}-source",
                        "attempted_at": "2026-07-27T00:00:00+00:00",
                        "observation_id": record.observations[0]["observation_id"],
                        "reason_codes": [],
                    }
                )
    return SimpleNamespace(
        release_id="phase4d-synthetic",
        manifest={"schema_version": "konsider-release-4.0"},
        catalog={
            "schema_version": "consumer-catalog-2.0",
            "coverage_policy_version": "uncertainty-aware-ranking-policy-1.0",
            "stable_universe_id": "stable_supported_v1",
            "countries": list(COUNTRY_RECORDS),
            "criteria": criteria,
            "profiles": [],
        },
        records=tuple(records),
        outcomes=tuple(outcomes),
    )


def _codes(start: int, count: int) -> set[str]:
    return {item["code"] for item in COUNTRY_RECORDS[start : start + count]}


@pytest.mark.parametrize(
    "scenario",
    GOLDEN["missing_union_scenarios"],
    ids=lambda item: item["id"],
)
def test_golden_missing_union_scenarios(scenario) -> None:
    missing_count = scenario["missing_count"]
    release = _release([_codes(0, missing_count)])

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=5,
    )

    assert result.status == UncertaintyStatus(scenario["expected_status"])
    assert result.coverage_band == CoverageBand(scenario["expected_band"])
    assert result.excluded_country_count == missing_count
    assert result.eligible_country_count == 91 - missing_count
    if missing_count == 10:
        assert result.active_pcc_ids == ("pcc_1",)
        assert result.r1_top_k is None
        assert result.r1_kth_score is None
        assert "ACTIVE_MISSING_UNION_EXCEEDS_HARD_LIMIT" in result.reason_codes
        assert "ELIGIBLE_UNIVERSE_BELOW_MINIMUM" in result.reason_codes
        assert all(item.optimistic_upper_bound is None for item in result.excluded_countries)
        assert all(item.could_enter_top_k is None for item in result.excluded_countries)
    else:
        assert result.r1_top_k is not None


def test_multiple_pcc_missing_union_is_deduplicated() -> None:
    release = _release([_codes(0, 3), _codes(3, 3)])

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6, "pcc_2": 0.6},
        top_k=10,
    )

    assert result.active_pcc_ids == ("pcc_1", "pcc_2")
    assert result.excluded_country_count == 6
    assert result.eligible_country_count == 85
    assert result.coverage_band == CoverageBand.ELEVATED
    assert result.status == UncertaintyStatus.ROBUST_TOP_K


@pytest.mark.parametrize(
    "scenario",
    GOLDEN["optimistic_bound_scenarios"],
    ids=lambda item: item["id"],
)
def test_optimistic_bound_below_equal_and_above_boundary(scenario) -> None:
    excluded_fcc_score = scenario["excluded_fcc_score"]
    missing = _codes(0, 1)
    release = _release(
        [missing],
        fcc_score=lambda code, _union: (excluded_fcc_score if code in missing else 3.0),
        pcc_score=lambda _code, _union: 25 / 3,
    )

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=5,
    )

    diagnostic = result.excluded_countries[0]
    assert result.status == UncertaintyStatus(scenario["expected_status"])
    assert result.r1_kth_score == 5.0
    assert diagnostic.could_enter_top_k is scenario["could_enter"]
    expected = round(excluded_fcc_score * 0.625 + 10 * 0.375, 8)
    assert diagnostic.optimistic_upper_bound == expected


def test_r0_boundary_tie_triggers_strongest_warning() -> None:
    missing = _codes(0, 1)
    release = _release(
        [missing],
        fcc_score=lambda _code, _union: 3.0,
        pcc_score=lambda _code, _union: 25 / 3,
    )

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=5,
    )

    assert result.status == UncertaintyStatus.BASELINE_TOP_K_EXCLUDED
    assert result.r0_top_k.returned_result_count == 91
    assert "TOP_K_BOUNDARY_INCLUDES_TIES" in result.reason_codes


def test_r1_boundary_ties_can_return_more_than_k() -> None:
    release = _release(
        [_codes(0, 1)],
        fcc_score=lambda code, union: 2.0 if code in union else 3.0,
        pcc_score=lambda _code, _union: 25 / 3,
    )

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=10,
    )

    assert result.r1_top_k is not None
    assert result.r1_top_k.returned_result_count == 90
    assert result.r1_top_k.boundary_tie_count == 90
    assert [item.country_code for item in result.rankings] == sorted(
        item.country_code for item in result.rankings
    )


@pytest.mark.parametrize("top_k", GOLDEN["top_k_values"])
def test_requested_k_is_used_for_robustness_and_is_deterministic(top_k) -> None:
    release = _release([_codes(0, 3)])
    weights = {FCC_ID: 1.0, "pcc_1": 0.6}

    first = rank_release_with_uncertainty(release, weights, top_k=top_k)
    second = rank_release_with_uncertainty(release, weights, top_k=top_k)

    assert first.requested_top_k == top_k
    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(), sort_keys=True
    )


def test_all_zero_fcc_fallback_and_pcc_only_final_weights() -> None:
    release = _release([set()], fcc_count=2)

    baseline = rank_release_with_uncertainty(release, {}, top_k=10)
    pcc_only = rank_release_with_uncertainty(
        release,
        {"pcc_1": 0.6},
        top_k=10,
    )

    assert baseline.status == UncertaintyStatus.NO_PARTIAL_CRITERIA_ACTIVE
    assert set(baseline.baseline_normalized_weights.values()) == {0.5}
    assert "FCC_ALL_ZERO_EQUAL_WEIGHT_FALLBACK" in baseline.reason_codes
    assert pcc_only.status == UncertaintyStatus.FULL_COVERAGE
    assert pcc_only.active_fcc_ids == ()
    assert pcc_only.final_normalized_weights == {"pcc_1": 1.0}
    assert set(pcc_only.baseline_normalized_weights.values()) == {0.5}


def test_no_partial_scoring_and_contributions_reconcile() -> None:
    release = _release([_codes(0, 3)])

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=10,
    )

    excluded = {item.country_code for item in result.excluded_countries}
    assert excluded.isdisjoint(item.country_code for item in result.rankings)
    for row in result.rankings:
        assert len(row.contributions) == 2
        assert (
            abs(sum(item.contribution for item in row.contributions) - row.total_score)
            <= result.policy.rounding_tolerance
        )


def test_missing_score_for_valid_active_criterion_is_integrity_error() -> None:
    release = _release([_codes(0, 1)])
    eligible_code = COUNTRY_RECORDS[-1]["code"]
    release.records = tuple(
        record
        for record in release.records
        if not (record.country["code"] == eligible_code and record.criterion["id"] == "pcc_1")
    )

    with pytest.raises(RankingIntegrityError, match="lacks a score"):
        rank_release_with_uncertainty(
            release,
            {FCC_ID: 1.0, "pcc_1": 0.6},
            top_k=10,
        )


def test_top_k_uses_eligible_universe_after_pcc_activation() -> None:
    release = _release([_codes(0, 9)])

    with pytest.raises(InvalidTopKError) as error:
        rank_release_with_uncertainty(
            release,
            {FCC_ID: 1.0, "pcc_1": 0.6},
            top_k=83,
        )

    assert error.value.eligible_count == 82


def test_coverage_limit_validates_top_k_against_returned_r0() -> None:
    release = _release([_codes(0, 10)])

    result = rank_release_with_uncertainty(
        release,
        {FCC_ID: 1.0, "pcc_1": 0.6},
        top_k=91,
    )

    assert result.status == UncertaintyStatus.COVERAGE_LIMIT_EXCEEDED
    assert len(result.rankings) == 91
