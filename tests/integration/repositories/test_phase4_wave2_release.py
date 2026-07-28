import json
from pathlib import Path

from konsider.ingestion.phase4_wave2 import build_wave2_release
from konsider.ingestion.worker import replay
from konsider.repositories.published_release_repository import PublishedReleaseRepository

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _build(root: Path, release_id: str):
    return build_wave2_release(
        release_id=release_id,
        base_release_path=PROJECT_ROOT / "data" / "releases" / "2026-07-28.1",
        base_catalog_path=PROJECT_ROOT / "data" / "catalogs" / "consumer-catalog-2.0.json",
        catalog_output_path=root / "consumer-catalog-2.0.json",
        school_probe_artifact_manifest=(
            PROJECT_ROOT
            / "data"
            / "reports"
            / "feasibility-probes"
            / "phase3e-2026-07-26-c08-online-v2"
            / "raw-artifacts.json"
        ),
        wipo_raw_path=PROJECT_ROOT / "data" / "raw" / "wave2-probes" / "wipo-gii-2025.xlsx",
        release_root=root / "releases",
        report_root=root / "report",
        publish=True,
        created_at="2026-07-28T08:00:00+00:00",
    )


def test_wave2_release_has_exact_partial_coverage_and_replays(tmp_path):
    published = _build(tmp_path, "wave2-test")
    release = PublishedReleaseRepository(
        release_root=tmp_path / "releases",
        catalog_path=tmp_path / "consumer-catalog-2.0.json",
    ).load_active()

    assert published == tmp_path / "releases" / "wave2-test"
    assert (tmp_path / "releases" / "wave2-test.json").exists()
    assert release.manifest["previous_release_id"] == "2026-07-28.1"
    assert release.manifest["schema_version"] == "konsider-release-4.0"
    assert release.manifest["validation_summary"]["ready_criterion_count"] == 11
    school = release.manifest["criterion_coverage"]["school_education_quality"]
    innovation = release.manifest["criterion_coverage"]["research_innovation_ecosystem"]
    assert school["outcome_counts"] == {
        "invalid": 0,
        "missing": 2,
        "rejected": 0,
        "stale": 1,
        "valid": 88,
    }
    assert innovation["outcome_counts"] == {
        "invalid": 0,
        "missing": 6,
        "rejected": 0,
        "stale": 0,
        "valid": 85,
    }
    assert replay(published)


def test_wave2_release_checksums_are_deterministic(tmp_path):
    first = _build(tmp_path / "first", "wave2-deterministic")
    second = _build(tmp_path / "second", "wave2-deterministic")
    first_manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    second_manifest = json.loads((second / "manifest.json").read_text(encoding="utf-8"))

    assert first_manifest["file_checksums"] == second_manifest["file_checksums"]
    assert first_manifest["release_checksum"] == second_manifest["release_checksum"]
