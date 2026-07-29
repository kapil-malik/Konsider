import json
from pathlib import Path

import pytest

from konsider.ingestion.phase4f import build_c11_release
from konsider.ingestion.worker import replay
from konsider.repositories.published_release_repository import PublishedReleaseRepository

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASE_RELEASE = PROJECT_ROOT / "data" / "releases" / "2026-07-27.1"
PROBE_ARTIFACT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "feasibility-probes"
    / "phase3e-2026-07-26-c11-online"
    / "raw-artifacts.json"
)


@pytest.fixture(autouse=True)
def _require_production_raw_artifacts(require_local_raw_artifacts):
    require_local_raw_artifacts(
        PROJECT_ROOT,
        manifests=(BASE_RELEASE / "raw-artifacts.json", PROBE_ARTIFACT_MANIFEST),
    )


def _build(root: Path, release_id: str):
    return build_c11_release(
        release_id=release_id,
        base_release_path=BASE_RELEASE,
        base_catalog_path=(PROJECT_ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json"),
        catalog_v2_path=root / "consumer-catalog-2.0.json",
        probe_artifact_manifest=PROBE_ARTIFACT_MANIFEST,
        release_root=root / "releases",
        report_root=root / "report",
        publish=True,
        created_at="2026-07-28T00:00:00+00:00",
    )


def test_phase4f_publishes_replayable_schema4_release(tmp_path):
    published = _build(tmp_path, "phase4f-test")
    release = PublishedReleaseRepository(
        release_root=tmp_path / "releases",
        catalog_path=tmp_path / "consumer-catalog-2.0.json",
        active_release_path=tmp_path / "releases" / "active.json",
    ).load_active()

    assert published == tmp_path / "releases" / "phase4f-test"
    assert release.manifest["schema_version"] == "konsider-release-4.0"
    assert release.manifest["previous_release_id"] == "2026-07-27.1"
    assert release.manifest["validation_summary"]["global_core_ready_count"] == 8
    coverage = release.manifest["criterion_coverage"]["overall_job_market_opportunity"]
    assert coverage["valid_country_count"] == 88
    assert coverage["outcome_counts"] == {
        "invalid": 0,
        "missing": 2,
        "rejected": 0,
        "stale": 1,
        "valid": 88,
    }
    non_valid = {
        item["country_code"]: (item["outcome"], item["reason_codes"])
        for item in release.outcomes
        if item["criterion_id"] == "overall_job_market_opportunity" and item["outcome"] != "valid"
    }
    assert non_valid == {
        "ATG": ("missing", ["COV_SOURCE_RECORD_MISSING"]),
        "GRD": ("missing", ["COV_SOURCE_RECORD_MISSING"]),
        "UKR": ("stale", ["FRS_STALE"]),
    }
    assert replay(published)


def test_phase4f_payload_checksums_are_deterministic(tmp_path):
    first = _build(tmp_path / "first", "phase4f-deterministic")
    second = _build(tmp_path / "second", "phase4f-deterministic")
    first_manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    second_manifest = json.loads((second / "manifest.json").read_text(encoding="utf-8"))

    assert first_manifest["file_checksums"] == second_manifest["file_checksums"]
    assert first_manifest["release_checksum"] == second_manifest["release_checksum"]
