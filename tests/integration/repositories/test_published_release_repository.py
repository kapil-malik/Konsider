import hashlib
import json
import shutil
from pathlib import Path

import pytest

from konsider.repositories.published_release_repository import (
    PublishedReleaseError,
    PublishedReleaseRepository,
)

ROOT = Path(__file__).resolve().parents[3]
ACTIVE_RELEASE_ID = "2026-07-27.1"


def _repository(tmp_path: Path) -> tuple[PublishedReleaseRepository, Path]:
    release_root = tmp_path / "releases"
    shutil.copytree(
        ROOT / "data" / "releases" / ACTIVE_RELEASE_ID,
        release_root / ACTIVE_RELEASE_ID,
    )
    shutil.copy2(ROOT / "data" / "releases" / "active.json", release_root / "active.json")
    catalog = tmp_path / "consumer-catalog.json"
    shutil.copy2(ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json", catalog)
    return PublishedReleaseRepository(release_root, catalog), release_root / ACTIVE_RELEASE_ID


def _rewrite_manifest_checksum(release: Path, filename: str) -> None:
    manifest_path = release / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["file_checksums"][filename] = (
        "sha256:" + hashlib.sha256((release / filename).read_bytes()).hexdigest()
    )
    manifest["release_checksum"] = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest["file_checksums"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_active_release_loads_complete_ready_matrix() -> None:
    release = PublishedReleaseRepository().load_active()

    assert release.release_id == ACTIVE_RELEASE_ID
    assert len(release.catalog["countries"]) == 91
    assert len(release.available_criterion_ids) == 9
    assert len(release.enabled_criterion_ids) == 8
    assert "uhc_service_coverage_index" not in release.enabled_criterion_ids
    assert len(release.records) == 728
    assert len(release.sources) == 9
    assert all(record.observations and record.source for record in release.records)
    infrastructure = next(
        item
        for item in release.catalog["criteria"]
        if item["id"] == "infrastructure_readiness_composite"
    )
    assert infrastructure["experimental"] is True


def test_default_repository_paths_do_not_depend_on_working_directory(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    release = PublishedReleaseRepository().load_active()

    assert release.release_id == ACTIVE_RELEASE_ID


def test_active_release_loads_after_git_style_lf_normalization(tmp_path: Path) -> None:
    release_root = tmp_path / "releases"
    source = ROOT / "data" / "releases" / ACTIVE_RELEASE_ID
    target = release_root / ACTIVE_RELEASE_ID
    target.mkdir(parents=True)
    for source_path in source.iterdir():
        target_path = target / source_path.name
        target_path.write_bytes(source_path.read_bytes().replace(b"\r\n", b"\n"))
    pointer = ROOT / "data" / "releases" / "active.json"
    release_root.mkdir(parents=True, exist_ok=True)
    (release_root / "active.json").write_bytes(pointer.read_bytes().replace(b"\r\n", b"\n"))
    catalog = tmp_path / "consumer-catalog.json"
    shutil.copy2(ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json", catalog)

    release = PublishedReleaseRepository(release_root, catalog).load_active()

    assert release.release_id == ACTIVE_RELEASE_ID
    assert len(release.records) == 728


def test_diagnostic_mode_exposes_non_ready_records_without_enabling_them() -> None:
    release = PublishedReleaseRepository().load_active(diagnostic_read_only=True)

    assert len(release.records) == 819
    assert "uhc_service_coverage_index" not in release.enabled_criterion_ids


def test_checksum_tampering_fails(tmp_path: Path) -> None:
    repository, release = _repository(tmp_path)
    with (release / "scores.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("\n")

    with pytest.raises(PublishedReleaseError, match="Checksum mismatch"):
        repository.load_active()


def test_unsupported_schema_fails(tmp_path: Path) -> None:
    repository, _ = _repository(tmp_path)
    pointer_path = repository.release_root / "active.json"
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    pointer["schema_version"] = "konsider-release-4.0"
    pointer_path.write_text(json.dumps(pointer), encoding="utf-8")

    with pytest.raises(PublishedReleaseError, match="Unsupported"):
        repository.load_active()


def test_duplicate_score_pair_fails(tmp_path: Path) -> None:
    repository, release = _repository(tmp_path)
    path = release / "scores.jsonl"
    rows = path.read_text(encoding="utf-8").splitlines()
    rows[1] = rows[0]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    _rewrite_manifest_checksum(release, "scores.jsonl")

    with pytest.raises(PublishedReleaseError, match="Duplicate score pair"):
        repository.load_active()


def test_missing_observation_fails(tmp_path: Path) -> None:
    repository, release = _repository(tmp_path)
    path = release / "scores.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["input_observation_ids"] = ["missing-observation"]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    _rewrite_manifest_checksum(release, "scores.jsonl")

    with pytest.raises(PublishedReleaseError, match="Missing input observation"):
        repository.load_active()


def test_broken_source_lineage_fails(tmp_path: Path) -> None:
    repository, release = _repository(tmp_path)
    path = release / "observations.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["source_id"] = "unknown-source"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    _rewrite_manifest_checksum(release, "observations.jsonl")

    with pytest.raises(PublishedReleaseError, match="Broken source lineage"):
        repository.load_active()
