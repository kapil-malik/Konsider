from pathlib import Path

from konsider.repositories.published_release_repository import PublishedReleaseRepository
from scripts.build_phase4c_fixture_release import build

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests" / "fixtures" / "phase4c"
RELEASE_ID = "phase4c-fixture-4.0"
PCC_ID = "overall_job_market_opportunity_fixture"


def _repository(root: Path = FIXTURE) -> PublishedReleaseRepository:
    return PublishedReleaseRepository(
        root / "releases",
        root / "consumer-catalog-2.0.json",
        active_release_path=root / "releases" / "active.json",
    )


def test_schema_4_fixture_loads_partial_score_matrix() -> None:
    release = _repository().load_active()

    assert release.release_id == RELEASE_ID
    assert len(release.catalog["countries"]) == 91
    assert len(release.outcomes) == 182
    assert len(release.records) == 179
    assert release.validation["criterion_coverage"][PCC_ID] == 88
    assert release.catalog["criteria"][1]["coverage"]["mode"] == "CONDITIONAL_COMPLETE_CASE"


def test_schema_4_preserves_missing_and_stale_reasons() -> None:
    release = _repository().load_active()
    non_valid = {
        row["country_code"]: (row["outcome"], row["reason_codes"])
        for row in release.outcomes
        if row["criterion_id"] == PCC_ID and row["outcome"] != "valid"
    }

    assert non_valid == {
        "ATG": ("missing", ["COV_SOURCE_RECORD_MISSING"]),
        "GRD": ("missing", ["COV_SOURCE_RECORD_MISSING"]),
        "UKR": ("stale", ["FRS_STALE"]),
    }


def test_fixture_replay_is_byte_identical_and_lf_normalized(tmp_path: Path) -> None:
    regenerated = tmp_path / "phase4c"
    build(regenerated)

    committed_files = sorted(
        path.relative_to(FIXTURE) for path in FIXTURE.rglob("*") if path.is_file()
    )
    regenerated_files = sorted(
        path.relative_to(regenerated) for path in regenerated.rglob("*") if path.is_file()
    )
    assert regenerated_files == committed_files
    for relative_path in committed_files:
        committed = (FIXTURE / relative_path).read_bytes()
        replayed = (regenerated / relative_path).read_bytes()
        assert replayed == committed
        assert b"\r\n" not in replayed

    assert _repository(regenerated).load_active().release_id == RELEASE_ID
