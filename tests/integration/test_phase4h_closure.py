import json
from pathlib import Path

import pytest

from konsider.application import RecommendationService
from konsider.domain.uncertainty_models import CoverageBand, UncertaintyStatus
from konsider.repositories.published_release_repository import PublishedReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = ROOT / "data" / "releases"
PCC_IDS = {
    "overall_job_market_opportunity",
    "school_education_quality",
    "research_innovation_ecosystem",
}


def _active_release():
    return PublishedReleaseRepository(release_id="2026-07-28.2").load_active(
        diagnostic_read_only=True
    )


def _historical_service() -> RecommendationService:
    return RecommendationService(PublishedReleaseRepository(release_id="2026-07-28.2"))


def test_active_release_proves_phase4_structural_invariants() -> None:
    release = _active_release()
    countries = {item["code"] for item in release.catalog["countries"]}
    criteria = {item["id"]: item for item in release.catalog["criteria"]}
    outcomes = {(item["country_code"], item["criterion_id"]): item for item in release.outcomes}
    score_pairs = {(record.country["code"], record.criterion["id"]) for record in release.records}

    assert release.release_id == "2026-07-28.2"
    assert len(countries) == 91
    assert len(outcomes) == 91 * len(criteria)
    assert set(outcomes) == {
        (country_code, criterion_id) for country_code in countries for criterion_id in criteria
    }

    for criterion_id, criterion in criteria.items():
        coverage = criterion["coverage"]
        assert coverage["stable_country_count"] == 91
        if coverage["mode"] == "GLOBAL_CORE":
            assert coverage["valid_country_count"] == 91
        elif coverage["mode"] == "CONDITIONAL_COMPLETE_CASE":
            assert coverage["valid_country_count"] >= 82

    valid_pairs = {pair for pair, outcome in outcomes.items() if outcome["outcome"] == "valid"}
    assert score_pairs == valid_pairs


@pytest.mark.parametrize("top_k", [5, 10, 20])
def test_active_release_complete_case_runtime_invariants(top_k: int) -> None:
    result = _historical_service().rank_with_uncertainty(
        profile_id="equal_weight_mvp",
        top_k=top_k,
    )
    active_ids = set(result.active_fcc_ids) | set(result.active_pcc_ids)
    excluded = {item.country_code for item in result.excluded_countries}

    assert result.active_pcc_ids == tuple(sorted(PCC_IDS))
    assert result.status == UncertaintyStatus.ROBUST_TOP_K
    assert result.coverage_band == CoverageBand.ELEVATED
    assert result.eligible_country_count == 83
    assert result.excluded_country_count == 8
    assert set(result.final_normalized_weights or {}) == active_ids
    assert sum((result.final_normalized_weights or {}).values()) == pytest.approx(1)
    assert excluded.isdisjoint(item.country_code for item in result.rankings)

    for row in result.rankings:
        assert {item.criterion_id for item in row.contributions} == active_ids
        assert {
            item.criterion_id: item.normalized_weight for item in row.contributions
        } == result.final_normalized_weights
        assert sum(item.contribution for item in row.contributions) == pytest.approx(
            row.total_score,
            abs=result.policy.rounding_tolerance,
        )

    for item in result.excluded_countries:
        assert item.optimistic_upper_bound is not None
        assert item.r0_rank > 0
        assert item.country_code not in {row.country_code for row in result.rankings}


def test_fcc_only_and_below_threshold_requests_preserve_full_catalog() -> None:
    service = _historical_service()
    weights = {"intentional_homicide_rate": 1.0}
    baseline = service.rank_with_uncertainty(weights, top_k=91)
    ignored = service.rank_with_uncertainty(
        {**weights, "school_education_quality": 0.4},
        top_k=91,
    )

    assert baseline.status == UncertaintyStatus.NO_PARTIAL_CRITERIA_ACTIVE
    assert baseline.stable_country_count == baseline.eligible_country_count == 91
    assert len(baseline.rankings) == 91
    assert [item.to_dict() for item in baseline.rankings] == [
        item.to_dict() for item in ignored.rankings
    ]
    assert ignored.status == UncertaintyStatus.NO_PARTIAL_CRITERIA_ACTIVE
    assert [item.criterion_id for item in ignored.ignored_pcc] == ["school_education_quality"]


@pytest.mark.parametrize(
    ("release_id", "schema_version"),
    [
        ("2026-07-27.1", "konsider-release-3.0"),
        ("2026-07-28.1", "konsider-release-4.0"),
        ("2026-07-28.2", "konsider-release-4.0"),
    ],
)
def test_release_scoped_catalog_snapshots_keep_history_loadable(
    tmp_path: Path,
    release_id: str,
    schema_version: str,
) -> None:
    pointer = tmp_path / "active.json"
    pointer.write_text(
        json.dumps({"release_id": release_id, "schema_version": schema_version}) + "\n",
        encoding="utf-8",
    )
    release = PublishedReleaseRepository(
        release_root=RELEASE_ROOT,
        active_release_path=pointer,
    ).load_active(diagnostic_read_only=True)

    assert release.release_id == release_id
    assert set(release.manifest["criteria"]) == {item["id"] for item in release.catalog["criteria"]}


def test_phase_workspaces_are_archived_below_one_history_root() -> None:
    assert not list(ROOT.glob("konsider_phase*"))
    assert (ROOT / "project-history" / "phases" / "phase-3" / "prompts").is_dir()
    assert (ROOT / "project-history" / "phases" / "phase-4" / "prompts").is_dir()
