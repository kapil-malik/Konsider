from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.ingestion.current_release import (
    PAYLOAD_FILES,
    CurrentReleaseError,
    CurrentReleaseRepository,
)
from konsider.ingestion.phase6_release_publication import (
    activate_release,
    build_release,
    derive_next_release_id,
    publish_release,
)

ROOT = Path(__file__).resolve().parents[3]
SOURCE_RELEASES = ROOT / "data" / "releases"
STAGED = ROOT / "data" / "reports" / "phase6g-2026-08-03" / "staged-release"
BASE_RELEASE_ID = "2026-07-29.2"
FINAL_RELEASE_ID = "2026-08-04.1"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_release_roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    releases = tmp_path / "releases"
    catalogs = tmp_path / "catalogs"
    reports = tmp_path / "reports"
    releases.mkdir()
    shutil.copytree(SOURCE_RELEASES / BASE_RELEASE_ID, releases / BASE_RELEASE_ID)
    (releases / "active.json").write_text(
        json.dumps(
            {
                "release_id": BASE_RELEASE_ID,
                "schema_version": "konsider-release-5.0",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return releases, catalogs, reports


def _historical_display_catalog(tmp_path: Path):
    payload = _json(ROOT / "data" / "catalogs" / "product-display-catalog.json")
    staged = _json(STAGED / "opportunity-filter-catalog.json")
    authoring = {
        item["id"]: item
        for item in payload["definitions"]
        if item["productRole"] == "OPPORTUNITY_FILTER"
    }
    for definition in staged["definitions"]:
        item = authoring[definition["id"]]
        item["displayName"] = definition["display_name"]
        item["compactName"] = definition["compact_label"]
        item["sectionId"] = definition["category"].lower()
    path = tmp_path / "historical-product-display-catalog.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return load_product_display_catalog(
        path,
        ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
    )


def test_release_id_sequence_is_monotonic(tmp_path: Path) -> None:
    (tmp_path / "2026-08-04.1").mkdir()
    (tmp_path / "2026-08-04.3").mkdir()
    (tmp_path / "unrelated").mkdir()
    assert derive_next_release_id(tmp_path, date(2026, 8, 4)) == "2026-08-04.4"


def test_build_publish_activate_lifecycle_is_immutable_and_atomic(tmp_path: Path) -> None:
    releases, catalogs, reports = _prepare_release_roots(tmp_path)
    before_pointer = (releases / "active.json").read_bytes()
    before_payloads = {
        filename: (releases / BASE_RELEASE_ID / filename).read_bytes() for filename in PAYLOAD_FILES
    }

    release_id, draft = build_release(
        display_catalog=_historical_display_catalog(tmp_path),
        release_root=releases,
        catalog_root=catalogs,
        staged_root=STAGED,
        report_root=reports,
        release_id=FINAL_RELEASE_ID,
        verify_research_inputs=False,
    )

    assert release_id == FINAL_RELEASE_ID
    assert (releases / "active.json").read_bytes() == before_pointer
    assert all((draft / name).read_bytes() == payload for name, payload in before_payloads.items())
    draft_manifest = _json(draft / "manifest.json")
    assert draft_manifest["schema_version"] == "konsider-release-5.1"
    assert draft_manifest["artifact_counts"]["opportunity_filter_definitions"] == 9
    assert draft_manifest["artifact_counts"]["opportunity_filter_evidence"] == 819
    CurrentReleaseRepository(releases, catalogs).load(draft)

    published = publish_release(
        release_id,
        release_root=releases,
        catalog_root=catalogs,
        report_root=reports,
    )
    assert published == releases / FINAL_RELEASE_ID
    assert not draft.exists()
    assert (releases / "active.json").read_bytes() == before_pointer
    assert (catalogs / f"{FINAL_RELEASE_ID}.json").is_file()

    pointer = activate_release(
        release_id,
        release_root=releases,
        catalog_root=catalogs,
        report_root=reports,
    )
    active = CurrentReleaseRepository(releases, catalogs).load_active(pointer)
    service = OpportunityFilterService.from_release(active.path, active.manifest)
    assert active.manifest["release_id"] == FINAL_RELEASE_ID
    assert active.manifest["schema_version"] == "konsider-release-5.1"
    assert service.filter_count == 9
    assert service.evidence_count == 819
    assert _json(reports / "build-manifest.json")["status"] == "active"


def test_bound_opportunity_payload_corruption_fails_closed(tmp_path: Path) -> None:
    releases, catalogs, reports = _prepare_release_roots(tmp_path)
    build_release(
        display_catalog=_historical_display_catalog(tmp_path),
        release_root=releases,
        catalog_root=catalogs,
        staged_root=STAGED,
        report_root=reports,
        release_id=FINAL_RELEASE_ID,
        verify_research_inputs=False,
    )
    published = publish_release(
        FINAL_RELEASE_ID,
        release_root=releases,
        catalog_root=catalogs,
        report_root=reports,
    )
    evidence = published / "opportunity-filter-evidence.jsonl"
    evidence.write_bytes(evidence.read_bytes() + b"\n")

    with pytest.raises(CurrentReleaseError, match="Checksum mismatch"):
        CurrentReleaseRepository(releases, catalogs).load(published)
    with pytest.raises(ValueError, match="checksum"):
        OpportunityFilterService.from_release(published, _json(published / "manifest.json"))


def test_final_release_rebuild_is_byte_identical(tmp_path: Path) -> None:
    releases, catalogs, reports = _prepare_release_roots(tmp_path)
    _, draft = build_release(
        display_catalog=_historical_display_catalog(tmp_path),
        release_root=releases,
        catalog_root=catalogs,
        staged_root=STAGED,
        report_root=reports,
        release_id=FINAL_RELEASE_ID,
        verify_research_inputs=True,
    )
    final = SOURCE_RELEASES / FINAL_RELEASE_ID
    for path in final.iterdir():
        if path.name == "manifest.json":
            rebuilt_manifest = _json(draft / path.name)
            rebuilt_manifest["status"] = "published"
            assert rebuilt_manifest == _json(path)
        else:
            assert (draft / path.name).read_bytes() == path.read_bytes(), path.name
