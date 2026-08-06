"""Build the release-5.2/base and release-6.1/TFC display-metadata migration pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from konsider.contracts import validate_contract
from konsider.domain.display_catalog import ProductDisplayCatalog, load_product_display_catalog
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[3]
SOURCE_BASE_ID = "2026-08-04.1"
SOURCE_OVERLAY_ID = "2026-08-05.1"
DEFAULT_BASE_ID = "2026-08-07.1"
DEFAULT_OVERLAY_ID = "2026-08-07.2"
DISPLAY_CATALOG_PATH = ROOT / "data" / "catalogs" / "product-display-catalog.json"
DISPLAY_SCHEMA_PATH = (
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json"
)


class DisplayMetadataMigrationError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _release_checksum(checksums: dict[str, str]) -> str:
    body = json.dumps(checksums, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _overlay_release_checksum(manifest: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in manifest.items() if key != "release_checksum"}
    body = json.dumps(unsigned, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _display_binding(catalog: ProductDisplayCatalog) -> dict[str, str]:
    return {
        "schema_version": catalog.schema_version,
        "catalog_version": catalog.catalog_version,
        "checksum": catalog.checksum,
    }


def _consumer_catalog(source: dict[str, Any], catalog: ProductDisplayCatalog) -> dict[str, Any]:
    result = {
        **source,
        "schema_version": "consumer-catalog-4.0",
        "target_api_contract_version": "konsider-api-3.0",
    }
    criteria = []
    for old in source["criteria"]:
        display = catalog.definition("ORDERING_CRITERION", old["id"])
        item = {key: value for key, value in old.items() if key not in {"display_name", "category"}}
        item.update(
            {
                "displayName": display.display_name,
                "compactName": display.compact_name,
                "sectionId": display.section_id,
                "sectionName": display.section_name,
                "sortOrder": display.sort_order,
            }
        )
        criteria.append(item)
    result["criteria"] = criteria
    return result


def _opportunity_catalog(source: dict[str, Any], catalog: ProductDisplayCatalog) -> dict[str, Any]:
    result = {**source, "schema_version": "opportunity-filter-catalog-2.0"}
    result["sections"] = [
        {
            "sectionId": item.section_id,
            "sectionName": item.section_name,
            "sortOrder": item.sort_order,
        }
        for item in catalog.sections("OPPORTUNITY_FILTER")
    ]
    definitions = []
    for old in source["definitions"]:
        display = catalog.definition("OPPORTUNITY_FILTER", old["id"])
        item = {
            key: value
            for key, value in old.items()
            if key not in {"display_name", "compact_label", "category", "sort_order"}
        }
        item.update(
            {
                "displayName": display.display_name,
                "compactName": display.compact_name,
                "sectionId": display.section_id,
                "sectionName": display.section_name,
                "sortOrder": display.sort_order,
            }
        )
        definitions.append(item)
    result["definitions"] = definitions
    return result


def _tfc_catalog(source: dict[str, Any], catalog: ProductDisplayCatalog) -> dict[str, Any]:
    result = {**source, "schema_version": "tfc-release-catalog-2.0"}
    definitions = []
    for old in source["definitions"]:
        definition_id = old["tfc_id"]
        display = catalog.definition("TYPED_FEASIBILITY_CHECK", definition_id)
        item = {key: value for key, value in old.items() if key not in {"tfc_id", "name"}}
        item.update(
            {
                "id": definition_id,
                "displayName": display.display_name,
                "compactName": display.compact_name,
                "sectionId": display.section_id,
                "sectionName": display.section_name,
                "sortOrder": display.sort_order,
            }
        )
        definitions.append(item)
    result["definitions"] = definitions
    return result


def _equivalence_report(
    consumer: dict[str, Any], opportunity: dict[str, Any], tfc: dict[str, Any]
) -> dict[str, Any]:
    resolved = []
    for role, definitions in (
        ("ORDERING_CRITERION", consumer["criteria"]),
        ("OPPORTUNITY_FILTER", opportunity["definitions"]),
        ("TYPED_FEASIBILITY_CHECK", tfc["definitions"]),
    ):
        resolved.extend(
            {
                "productRole": role,
                "id": item["id"],
                "displayName": item["displayName"],
                "compactName": item["compactName"],
                "sectionName": item["sectionName"],
            }
            for item in definitions
        )
    golden = _read_json(ROOT / "tests" / "fixtures" / "catalog-display-metadata-golden.json")
    if resolved != golden["definitions"]:
        raise DisplayMetadataMigrationError(
            "New catalogs differ from the golden display inventory."
        )
    return {
        "schemaVersion": "konsider-display-metadata-equivalence-1.0",
        "status": "PASSED",
        "sourceBaseReleaseId": SOURCE_BASE_ID,
        "sourceOverlayReleaseId": SOURCE_OVERLAY_ID,
        "definitionCount": len(resolved),
        "definitions": resolved,
    }


def build_drafts(
    *,
    release_root: Path,
    report_root: Path,
    display_catalog: ProductDisplayCatalog,
    base_release_id: str,
    overlay_release_id: str,
) -> tuple[Path, Path]:
    source_base = release_root / SOURCE_BASE_ID
    source_overlay = release_root / SOURCE_OVERLAY_ID
    base_draft = release_root / ".draft" / base_release_id
    overlay_draft = release_root / ".draft" / overlay_release_id
    for path in (
        base_draft,
        overlay_draft,
        release_root / base_release_id,
        release_root / overlay_release_id,
    ):
        if path.exists():
            raise FileExistsError(f"Immutable release ID is already in use: {path}")

    consumer = _consumer_catalog(_read_json(source_base / "consumer-catalog.json"), display_catalog)
    opportunity = _opportunity_catalog(
        _read_json(source_base / "opportunity-filter-catalog.json"), display_catalog
    )
    tfc = _tfc_catalog(_read_json(source_overlay / "tfc-catalog.json"), display_catalog)
    validate_contract(
        consumer, "consumer-catalog", context="consumer catalog 4.0", schema_generation=5
    )
    validate_contract(
        opportunity, "opportunity-filter-catalog", context="OFC catalog 2.0", schema_generation=5
    )
    validate_contract(tfc, "tfc-release-catalog", context="TFC catalog 2.0", schema_generation=5)

    report = _equivalence_report(consumer, opportunity, tfc)
    equivalence_path = report_root / "display-metadata-equivalence.json"
    _write_json(equivalence_path, report)
    equivalence_checksum = _checksum(equivalence_path)
    equivalence_binding = {
        "status": "PASSED",
        "definition_count": report["definitionCount"],
        "report_checksum": equivalence_checksum,
    }
    base_equivalence_binding = {
        **equivalence_binding,
        "source_release_id": SOURCE_BASE_ID,
    }
    overlay_equivalence_binding = {
        **equivalence_binding,
        "source_release_id": SOURCE_OVERLAY_ID,
    }

    base_draft.mkdir(parents=True)
    for source in source_base.iterdir():
        if source.name not in {
            "manifest.json",
            "consumer-catalog.json",
            "opportunity-filter-catalog.json",
        }:
            shutil.copyfile(source, base_draft / source.name)
    _write_json(base_draft / "consumer-catalog.json", consumer)
    _write_json(base_draft / "opportunity-filter-catalog.json", opportunity)
    source_base_manifest = _read_json(source_base / "manifest.json")
    base_checksums = {path.name: _checksum(path) for path in base_draft.iterdir()}
    ofc_artifacts = []
    for artifact in source_base_manifest["opportunity_filters"]["artifacts"]:
        updated = {**artifact, "checksum": base_checksums[artifact["filename"]]}
        if artifact["role"] == "CATALOG":
            updated["schema_version"] = "opportunity-filter-catalog-2.0"
        ofc_artifacts.append(updated)
    base_manifest = {
        **source_base_manifest,
        "schema_version": "konsider-release-5.2",
        "release_id": base_release_id,
        "status": "draft",
        "catalog_schema_version": "consumer-catalog-4.0",
        "display_catalog": _display_binding(display_catalog),
        "display_metadata_equivalence": base_equivalence_binding,
        "opportunity_filters": {
            **source_base_manifest["opportunity_filters"],
            "binding_schema_version": "opportunity-filter-release-binding-2.0",
            "artifacts": ofc_artifacts,
        },
        "file_checksums": base_checksums,
        "release_checksum": _release_checksum(base_checksums),
    }
    validate_contract(
        base_manifest, "release-manifest", context="release 5.2 manifest", schema_generation=5
    )
    _write_json(base_draft / "manifest.json", base_manifest)

    overlay_draft.mkdir(parents=True)
    for source in source_overlay.iterdir():
        if source.name not in {"manifest.json", "tfc-catalog.json"}:
            shutil.copyfile(source, overlay_draft / source.name)
    _write_json(overlay_draft / "tfc-catalog.json", tfc)
    source_overlay_manifest = _read_json(source_overlay / "manifest.json")
    overlay_checksums = {path.name: _checksum(path) for path in overlay_draft.iterdir()}
    tfc_artifacts = []
    for artifact in source_overlay_manifest["tfc"]["artifacts"]:
        updated = {**artifact, "checksum": overlay_checksums[artifact["filename"]]}
        if artifact["role"] == "TFC_CATALOG":
            updated["schema_version"] = "tfc-release-catalog-2.0"
        tfc_artifacts.append(updated)
    overlay_manifest = {
        **source_overlay_manifest,
        "schema_version": "konsider-release-6.1",
        "release_id": overlay_release_id,
        "status": "draft",
        "activation_authorized": False,
        "base_release": {
            "release_id": base_release_id,
            "schema_version": "konsider-release-5.2",
            "release_checksum": base_manifest["release_checksum"],
        },
        "display_catalog": _display_binding(display_catalog),
        "display_metadata_equivalence": overlay_equivalence_binding,
        "tfc": {
            **source_overlay_manifest["tfc"],
            "binding_schema_version": "tfc-release-binding-2.0",
            "target_release_schema_version": "konsider-release-6.1",
            "artifacts": tfc_artifacts,
        },
        "file_checksums": overlay_checksums,
        "release_checksum": "sha256:" + "0" * 64,
    }
    overlay_manifest["release_checksum"] = _overlay_release_checksum(overlay_manifest)
    validate_contract(
        overlay_manifest,
        "tfc-release-manifest",
        context="release 6.1 manifest",
        schema_generation=5,
    )
    _write_json(overlay_draft / "manifest.json", overlay_manifest)
    _write_json(
        report_root / "build-manifest.json",
        {
            "schemaVersion": "catalog-display-metadata-migration-build-1.0",
            "status": "DRAFTS_BUILT",
            "baseReleaseId": base_release_id,
            "baseReleaseChecksum": base_manifest["release_checksum"],
            "overlayReleaseId": overlay_release_id,
            "overlayReleaseChecksum": overlay_manifest["release_checksum"],
            "displayCatalog": _display_binding(display_catalog),
            "displayMetadataEquivalence": {
                **equivalence_binding,
                "sourceBaseReleaseId": SOURCE_BASE_ID,
                "sourceOverlayReleaseId": SOURCE_OVERLAY_ID,
            },
        },
    )
    return base_draft, overlay_draft


def publish_pair(
    *,
    release_root: Path,
    catalog_snapshot_root: Path,
    base_release_id: str,
    overlay_release_id: str,
    report_root: Path | None = None,
) -> tuple[Path, Path]:
    published = []
    for release_id, schema_name in (
        (base_release_id, "release-manifest"),
        (overlay_release_id, "tfc-release-manifest"),
    ):
        draft = release_root / ".draft" / release_id
        target = release_root / release_id
        if target.exists():
            raise FileExistsError(f"Published release is immutable: {target}")
        manifest = _read_json(draft / "manifest.json")
        manifest["status"] = "published"
        if schema_name == "tfc-release-manifest":
            manifest["activation_authorized"] = True
            manifest["release_checksum"] = _overlay_release_checksum(manifest)
        validate_contract(
            manifest, schema_name, context=f"published {release_id}", schema_generation=5
        )
        _write_json(draft / "manifest.json", manifest)
        draft.replace(target)
        published.append(target)
    snapshot = catalog_snapshot_root / f"{base_release_id}.json"
    if snapshot.exists():
        raise FileExistsError(f"Published catalog snapshot is immutable: {snapshot}")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(published[0] / "consumer-catalog.json", snapshot)
    if report_root is not None:
        report = _read_json(report_root / "build-manifest.json")
        report.update(
            {
                "status": "PUBLISHED",
                "baseReleaseChecksum": _read_json(published[0] / "manifest.json")[
                    "release_checksum"
                ],
                "overlayReleaseChecksum": _read_json(published[1] / "manifest.json")[
                    "release_checksum"
                ],
            }
        )
        _write_json(report_root / "build-manifest.json", report)
    return published[0], published[1]


def activate_overlay(
    *, release_root: Path, overlay_release_id: str, report_root: Path | None = None
) -> Path:
    from konsider.ingestion.current_release import CurrentReleaseRepository
    from konsider.ingestion.phase7_release_publication import load_active_tfc_release
    from konsider.ingestion.tfc_release import TfcCandidateReleaseRepository

    overlay = TfcCandidateReleaseRepository(release_root).load(release_root / overlay_release_id)
    manifest = overlay.manifest
    if manifest["status"] != "published" or not manifest["activation_authorized"]:
        raise DisplayMetadataMigrationError(
            "Only a published, authorized display-metadata overlay can be activated."
        )
    base = CurrentReleaseRepository(release_root).load(
        release_root / manifest["base_release"]["release_id"]
    )
    expected_base = {
        "release_id": base.manifest["release_id"],
        "schema_version": base.manifest["schema_version"],
        "release_checksum": base.manifest["release_checksum"],
    }
    if manifest["base_release"] != expected_base:
        raise DisplayMetadataMigrationError(
            "The activation target does not bind the loaded immutable base release."
        )
    pointer = release_root / "active.json"
    previous = _read_json(pointer)
    temporary = pointer.with_suffix(".json.tmp")
    target = {
        "release_id": overlay_release_id,
        "schema_version": "konsider-release-6.1",
    }
    _write_json(temporary, target)
    load_active_tfc_release(release_root, temporary)
    os.replace(temporary, pointer)
    load_active_tfc_release(release_root, pointer)
    CurrentReleaseRepository(release_root).load_active(pointer)
    if report_root is not None:
        _write_json(
            report_root / "activation.json",
            {
                "schemaVersion": "catalog-display-metadata-activation-1.0",
                "status": "ACTIVE",
                "active": target,
                "rollback": previous,
                "baseRelease": expected_base,
                "overlayReleaseChecksum": manifest["release_checksum"],
            },
        )
        build_report = _read_json(report_root / "build-manifest.json")
        build_report["status"] = "ACTIVE"
        build_report["rollbackReleaseId"] = previous["release_id"]
        _write_json(report_root / "build-manifest.json", build_report)
    return pointer


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "publish", "activate"))
    parser.add_argument("--base-release-id", default=DEFAULT_BASE_ID)
    parser.add_argument("--overlay-release-id", default=DEFAULT_OVERLAY_ID)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    releases = ROOT / "data" / "releases"
    reports = ROOT / "data" / "reports" / "catalog-display-metadata-2026-08-07"
    if args.command == "build":
        catalog = load_product_display_catalog(DISPLAY_CATALOG_PATH, DISPLAY_SCHEMA_PATH)
        paths = build_drafts(
            release_root=releases,
            report_root=reports,
            display_catalog=catalog,
            base_release_id=args.base_release_id,
            overlay_release_id=args.overlay_release_id,
        )
    elif args.command == "publish":
        paths = publish_pair(
            release_root=releases,
            catalog_snapshot_root=ROOT / "data" / "catalogs" / "releases",
            base_release_id=args.base_release_id,
            overlay_release_id=args.overlay_release_id,
            report_root=reports,
        )
    else:
        paths = (
            activate_overlay(
                release_root=releases,
                overlay_release_id=args.overlay_release_id,
                report_root=reports,
            ),
        )
    print("\n".join(str(path) for path in paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
