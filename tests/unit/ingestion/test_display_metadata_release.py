import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.ingestion.display_metadata_migration import activate_overlay, publish_pair
from konsider.ingestion.display_metadata_release import (
    DisplayMetadataReleaseError,
    derive_release_ids,
    prepare_release_pair,
)

ROOT = Path(__file__).resolve().parents[3]
SOURCE_BASE = "2026-08-07.1"
SOURCE_OVERLAY = "2026-08-07.2"


def _workspace(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    releases = tmp_path / "releases"
    shutil.copytree(ROOT / "data" / "releases" / SOURCE_BASE, releases / SOURCE_BASE)
    shutil.copytree(ROOT / "data" / "releases" / SOURCE_OVERLAY, releases / SOURCE_OVERLAY)
    shutil.copyfile(ROOT / "data" / "releases" / "active.json", releases / "active.json")

    catalog_path = tmp_path / "product-display-catalog.json"
    payload = json.loads(
        (ROOT / "data" / "catalogs" / "product-display-catalog.json").read_text(encoding="utf-8")
    )
    payload["catalogVersion"] = "test-display-copy-1"
    definition = next(
        item
        for item in payload["definitions"]
        if item["productRole"] == "ORDERING_CRITERION" and item["id"] == "C66"
    )
    definition["displayName"] = "Extreme heat exposure test label"
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    return releases, tmp_path / "reports", tmp_path / "catalog-snapshots", catalog_path


def _catalog(path: Path):
    return load_product_display_catalog(
        path,
        ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
    )


def test_prepare_builds_display_only_drafts_without_activation(tmp_path: Path) -> None:
    releases, reports, _, catalog_path = _workspace(tmp_path)
    pointer_before = (releases / "active.json").read_bytes()

    base, overlay = prepare_release_pair(
        release_root=releases,
        report_root=reports,
        display_catalog=_catalog(catalog_path),
        source_base_id=SOURCE_BASE,
        source_overlay_id=SOURCE_OVERLAY,
        base_release_id="new-base",
        overlay_release_id="new-overlay",
    )

    assert base == releases / ".draft" / "new-base"
    assert overlay == releases / ".draft" / "new-overlay"
    assert not (releases / "new-base").exists()
    assert not (releases / "new-overlay").exists()
    assert (releases / "active.json").read_bytes() == pointer_before
    consumer = json.loads((base / "consumer-catalog.json").read_text(encoding="utf-8"))
    c66 = next(item for item in consumer["criteria"] if item["id"] == "C66")
    assert c66["displayName"] == "Extreme heat exposure test label"
    assert [item["sortOrder"] for item in consumer["criteria"]] == sorted(
        item["sortOrder"] for item in consumer["criteria"]
    )
    report = json.loads((reports / "display-metadata-changes.json").read_text(encoding="utf-8"))
    assert report["networkAccess"] == "NONE"
    assert report["nonCatalogArtifacts"] == "COPIED_BYTE_FOR_BYTE"
    assert {
        "productRole": "ORDERING_CRITERION",
        "id": "C66",
        "field": "displayName",
        "before": "Extreme heat exposure",
        "after": "Extreme heat exposure test label",
    } in report["changes"]
    assert (base / "scores.jsonl").read_bytes() == (
        releases / SOURCE_BASE / "scores.jsonl"
    ).read_bytes()
    assert (overlay / "tfc-destination-rule-evidence.jsonl").read_bytes() == (
        releases / SOURCE_OVERLAY / "tfc-destination-rule-evidence.jsonl"
    ).read_bytes()


def test_prepared_pair_can_be_published_and_activated(tmp_path: Path) -> None:
    releases, reports, snapshots, catalog_path = _workspace(tmp_path)
    prepare_release_pair(
        release_root=releases,
        report_root=reports,
        display_catalog=_catalog(catalog_path),
        source_base_id=SOURCE_BASE,
        source_overlay_id=SOURCE_OVERLAY,
        base_release_id="new-base",
        overlay_release_id="new-overlay",
    )
    publish_pair(
        release_root=releases,
        catalog_snapshot_root=snapshots,
        base_release_id="new-base",
        overlay_release_id="new-overlay",
        report_root=reports,
    )
    activate_overlay(
        release_root=releases,
        overlay_release_id="new-overlay",
        report_root=reports,
    )
    assert json.loads((releases / "active.json").read_text(encoding="utf-8")) == {
        "release_id": "new-overlay",
        "schema_version": "konsider-release-6.1",
    }


def test_prepare_rejects_unchanged_catalog_version(tmp_path: Path) -> None:
    releases, reports, _, catalog_path = _workspace(tmp_path)
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["catalogVersion"] = "2026-08-06.1"
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    catalog = load_product_display_catalog(
        catalog_path,
        ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
    )
    with pytest.raises(DisplayMetadataReleaseError, match="Increment catalogVersion"):
        prepare_release_pair(
            release_root=releases,
            report_root=reports,
            display_catalog=catalog,
            source_base_id=SOURCE_BASE,
            source_overlay_id=SOURCE_OVERLAY,
            base_release_id="new-base",
            overlay_release_id="new-overlay",
        )


def test_release_id_derivation_reserves_consecutive_pair(tmp_path: Path) -> None:
    (tmp_path / "2026-08-07.1").mkdir()
    (tmp_path / "2026-08-07.2").mkdir()
    assert derive_release_ids(tmp_path, date(2026, 8, 7)) == (
        "2026-08-07.3",
        "2026-08-07.4",
    )
