"""Prepare, publish, and activate display-metadata-only release pairs.

This workflow is deliberately offline. It reads the active immutable base/overlay pair,
regenerates only their display catalogs, and copies every evidence/rule/data artifact byte-for-byte.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from konsider.contracts import validate_contract
from konsider.domain.display_catalog import ProductDisplayCatalog, load_product_display_catalog
from konsider.ingestion.display_metadata_migration import (
    _checksum,
    _consumer_catalog,
    _display_binding,
    _opportunity_catalog,
    _overlay_release_checksum,
    _read_json,
    _release_checksum,
    _write_json,
    activate_overlay,
    publish_pair,
)

ROOT = Path(__file__).resolve().parents[3]
DISPLAY_CATALOG_PATH = ROOT / "data" / "catalogs" / "product-display-catalog.json"
DISPLAY_SCHEMA_PATH = (
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json"
)
DISPLAY_FIELDS = frozenset({"displayName", "compactName", "sectionId", "sectionName", "sortOrder"})


class DisplayMetadataReleaseError(ValueError):
    """Raised when a proposed release is not a display-only change."""


def _active_pair(release_root: Path) -> tuple[str, str]:
    pointer = _read_json(release_root / "active.json")
    overlay_id = pointer["release_id"]
    overlay_manifest = _read_json(release_root / overlay_id / "manifest.json")
    if overlay_manifest["schema_version"] != "konsider-release-6.1":
        raise DisplayMetadataReleaseError(
            "The active release must be a schema-6.1 overlay before a display-only release."
        )
    return overlay_manifest["base_release"]["release_id"], overlay_id


def derive_release_ids(release_root: Path, release_date: date | None = None) -> tuple[str, str]:
    """Return the next two unused YYYY-MM-DD.N IDs for the base and overlay."""

    prefix = (release_date or date.today()).isoformat()
    candidates = list(release_root.iterdir())
    draft_root = release_root / ".draft"
    if draft_root.is_dir():
        candidates.extend(draft_root.iterdir())
    used = {
        int(path.name.rsplit(".", 1)[1])
        for path in candidates
        if path.is_dir()
        and path.name.startswith(prefix + ".")
        and path.name.rsplit(".", 1)[1].isdigit()
    }
    sequence = max(used, default=0) + 1
    while sequence in used or sequence + 1 in used:
        sequence += 1
    return f"{prefix}.{sequence}", f"{prefix}.{sequence + 1}"


def _tfc_catalog(source: dict[str, Any], catalog: ProductDisplayCatalog) -> dict[str, Any]:
    result = {**source, "schema_version": "tfc-release-catalog-2.0"}
    definitions = []
    for old in source["definitions"]:
        definition_id = old.get("id", old.get("tfc_id"))
        if not definition_id:
            raise DisplayMetadataReleaseError("A TFC catalog definition has no stable ID.")
        display = catalog.definition("TYPED_FEASIBILITY_CHECK", definition_id)
        item = {
            key: value
            for key, value in old.items()
            if key not in {"tfc_id", "name", *DISPLAY_FIELDS}
        }
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


def _definition_rows(
    consumer: dict[str, Any], opportunity: dict[str, Any], tfc: dict[str, Any]
) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for role, definitions in (
        ("ORDERING_CRITERION", consumer["criteria"]),
        ("OPPORTUNITY_FILTER", opportunity["definitions"]),
        ("TYPED_FEASIBILITY_CHECK", tfc["definitions"]),
    ):
        for item in definitions:
            rows[(role, item["id"])] = {field: item.get(field) for field in DISPLAY_FIELDS}
    return rows


def _change_report(
    *,
    source_base_id: str,
    source_overlay_id: str,
    source_consumer: dict[str, Any],
    source_opportunity: dict[str, Any],
    source_tfc: dict[str, Any],
    consumer: dict[str, Any],
    opportunity: dict[str, Any],
    tfc: dict[str, Any],
) -> dict[str, Any]:
    before = _definition_rows(source_consumer, source_opportunity, source_tfc)
    after = _definition_rows(consumer, opportunity, tfc)
    if before.keys() != after.keys():
        raise DisplayMetadataReleaseError(
            "Display-only releases cannot add or remove technical IDs."
        )
    changes = []
    for role, definition_id in sorted(before):
        for field in sorted(DISPLAY_FIELDS):
            if before[(role, definition_id)][field] != after[(role, definition_id)][field]:
                changes.append(
                    {
                        "productRole": role,
                        "id": definition_id,
                        "field": field,
                        "before": before[(role, definition_id)][field],
                        "after": after[(role, definition_id)][field],
                    }
                )
    before_sections = {item["sectionId"]: item for item in source_opportunity.get("sections", [])}
    for item in opportunity.get("sections", []):
        previous = before_sections.get(item["sectionId"])
        if previous:
            for field in ("sectionName", "sortOrder"):
                if previous.get(field) != item.get(field):
                    changes.append(
                        {
                            "productRole": "OPPORTUNITY_FILTER",
                            "id": item["sectionId"],
                            "field": field,
                            "before": previous.get(field),
                            "after": item.get(field),
                        }
                    )
    if not changes:
        raise DisplayMetadataReleaseError(
            "The authoring catalog produces no display changes; refusing a no-op release."
        )
    return {
        "schemaVersion": "konsider-display-metadata-change-report-1.0",
        "status": "PASSED",
        "sourceBaseReleaseId": source_base_id,
        "sourceOverlayReleaseId": source_overlay_id,
        "definitionCount": len(after),
        "changeCount": len(changes),
        "changes": changes,
        "networkAccess": "NONE",
        "nonCatalogArtifacts": "COPIED_BYTE_FOR_BYTE",
    }


def _copy_unchanged(source: Path, target: Path, excluded: set[str]) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for path in source.iterdir():
        if path.name in excluded:
            continue
        destination = target / path.name
        shutil.copyfile(path, destination)
        if destination.read_bytes() != path.read_bytes():
            raise DisplayMetadataReleaseError(f"Copied artifact changed unexpectedly: {path.name}")
        checksums[path.name] = _checksum(destination)
    return checksums


def prepare_release_pair(
    *,
    release_root: Path,
    report_root: Path,
    display_catalog: ProductDisplayCatalog,
    source_base_id: str,
    source_overlay_id: str,
    base_release_id: str,
    overlay_release_id: str,
) -> tuple[Path, Path]:
    """Build and fully validate drafts without publishing or changing active.json."""

    source_base = release_root / source_base_id
    source_overlay = release_root / source_overlay_id
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

    source_base_manifest = _read_json(source_base / "manifest.json")
    source_overlay_manifest = _read_json(source_overlay / "manifest.json")
    if source_base_manifest["schema_version"] != "konsider-release-5.2":
        raise DisplayMetadataReleaseError("Source base must use konsider-release-5.2.")
    if source_overlay_manifest["schema_version"] != "konsider-release-6.1":
        raise DisplayMetadataReleaseError("Source overlay must use konsider-release-6.1.")
    if source_overlay_manifest["base_release"]["release_id"] != source_base_id:
        raise DisplayMetadataReleaseError(
            "The selected source overlay does not bind the selected source base."
        )
    if (
        display_catalog.catalog_version
        == source_base_manifest["display_catalog"]["catalog_version"]
    ):
        raise DisplayMetadataReleaseError(
            "Increment catalogVersion in product-display-catalog.json before preparing a release."
        )

    source_consumer = _read_json(source_base / "consumer-catalog.json")
    source_opportunity = _read_json(source_base / "opportunity-filter-catalog.json")
    source_tfc = _read_json(source_overlay / "tfc-catalog.json")
    expected_ids = {
        "ORDERING_CRITERION": {item["id"] for item in source_consumer["criteria"]},
        "OPPORTUNITY_FILTER": {item["id"] for item in source_opportunity["definitions"]},
        "TYPED_FEASIBILITY_CHECK": {item["id"] for item in source_tfc["definitions"]},
    }
    display_catalog.require_exact_ids(expected_ids)  # type: ignore[arg-type]

    consumer = _consumer_catalog(source_consumer, display_catalog)
    opportunity = _opportunity_catalog(source_opportunity, display_catalog)
    tfc = _tfc_catalog(source_tfc, display_catalog)
    consumer["criteria"].sort(key=lambda item: item["sortOrder"])
    opportunity["sections"].sort(key=lambda item: item["sortOrder"])
    opportunity["definitions"].sort(key=lambda item: item["sortOrder"])
    tfc["definitions"].sort(key=lambda item: item["sortOrder"])
    validate_contract(
        consumer, "consumer-catalog", context="display-only consumer catalog", schema_generation=5
    )
    validate_contract(
        opportunity,
        "opportunity-filter-catalog",
        context="display-only OFC catalog",
        schema_generation=5,
    )
    validate_contract(
        tfc, "tfc-release-catalog", context="display-only TFC catalog", schema_generation=5
    )

    report = _change_report(
        source_base_id=source_base_id,
        source_overlay_id=source_overlay_id,
        source_consumer=source_consumer,
        source_opportunity=source_opportunity,
        source_tfc=source_tfc,
        consumer=consumer,
        opportunity=opportunity,
        tfc=tfc,
    )
    report_path = report_root / "display-metadata-changes.json"
    _write_json(report_path, report)
    validation_binding = {
        "status": "PASSED",
        "definition_count": sum(len(ids) for ids in expected_ids.values()),
        "report_checksum": _checksum(report_path),
    }

    base_draft.mkdir(parents=True)
    unchanged_base = _copy_unchanged(
        source_base,
        base_draft,
        {"manifest.json", "consumer-catalog.json", "opportunity-filter-catalog.json"},
    )
    _write_json(base_draft / "consumer-catalog.json", consumer)
    _write_json(base_draft / "opportunity-filter-catalog.json", opportunity)
    base_checksums = {path.name: _checksum(path) for path in base_draft.iterdir()}
    base_manifest = {
        **source_base_manifest,
        "release_id": base_release_id,
        "status": "draft",
        "display_catalog": _display_binding(display_catalog),
        "display_metadata_equivalence": {
            **validation_binding,
            "source_release_id": source_base_manifest["display_metadata_equivalence"][
                "source_release_id"
            ],
        },
        "file_checksums": base_checksums,
        "release_checksum": _release_checksum(base_checksums),
    }
    base_manifest["opportunity_filters"] = {
        **base_manifest["opportunity_filters"],
        "artifacts": [
            {**item, "checksum": base_checksums[item["filename"]]}
            for item in base_manifest["opportunity_filters"]["artifacts"]
        ],
    }
    validate_contract(
        base_manifest, "release-manifest", context="display-only base manifest", schema_generation=5
    )
    _write_json(base_draft / "manifest.json", base_manifest)

    overlay_draft.mkdir(parents=True)
    unchanged_overlay = _copy_unchanged(
        source_overlay, overlay_draft, {"manifest.json", "tfc-catalog.json"}
    )
    _write_json(overlay_draft / "tfc-catalog.json", tfc)
    overlay_checksums = {path.name: _checksum(path) for path in overlay_draft.iterdir()}
    overlay_manifest = {
        **source_overlay_manifest,
        "release_id": overlay_release_id,
        "status": "draft",
        "activation_authorized": False,
        "base_release": {
            "release_id": base_release_id,
            "schema_version": "konsider-release-5.2",
            "release_checksum": base_manifest["release_checksum"],
        },
        "display_catalog": _display_binding(display_catalog),
        "display_metadata_equivalence": {
            **validation_binding,
            "source_release_id": source_overlay_manifest["display_metadata_equivalence"][
                "source_release_id"
            ],
        },
        "file_checksums": overlay_checksums,
    }
    overlay_manifest["tfc"] = {
        **overlay_manifest["tfc"],
        "artifacts": [
            {**item, "checksum": overlay_checksums[item["filename"]]}
            for item in overlay_manifest["tfc"]["artifacts"]
        ],
    }
    overlay_manifest["release_checksum"] = _overlay_release_checksum(overlay_manifest)
    validate_contract(
        overlay_manifest,
        "tfc-release-manifest",
        context="display-only overlay manifest",
        schema_generation=5,
    )
    _write_json(overlay_draft / "manifest.json", overlay_manifest)

    _write_json(
        report_root / "build-manifest.json",
        {
            "schemaVersion": "konsider-display-metadata-release-build-1.0",
            "status": "DRAFTS_BUILT",
            "sourceBaseReleaseId": source_base_id,
            "sourceOverlayReleaseId": source_overlay_id,
            "baseReleaseId": base_release_id,
            "baseReleaseChecksum": base_manifest["release_checksum"],
            "overlayReleaseId": overlay_release_id,
            "overlayReleaseChecksum": overlay_manifest["release_checksum"],
            "displayCatalog": _display_binding(display_catalog),
            "changeReportChecksum": validation_binding["report_checksum"],
            "unchangedBaseArtifacts": unchanged_base,
            "unchangedOverlayArtifacts": unchanged_overlay,
        },
    )
    return base_draft, overlay_draft


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "publish", "activate", "release"))
    parser.add_argument("--base-release-id")
    parser.add_argument("--overlay-release-id")
    parser.add_argument("--source-base-release-id")
    parser.add_argument("--source-overlay-release-id")
    parser.add_argument(
        "--confirm-activate",
        action="store_true",
        help="Required by 'release'; acknowledges publication and active-pointer replacement.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    release_root = ROOT / "data" / "releases"
    active_base, active_overlay = _active_pair(release_root)
    source_base = args.source_base_release_id or active_base
    source_overlay = args.source_overlay_release_id or active_overlay
    generated_base, generated_overlay = derive_release_ids(release_root)
    base_id = args.base_release_id or generated_base
    overlay_id = args.overlay_release_id or generated_overlay
    if args.command == "activate" and args.overlay_release_id:
        overlay_manifest = _read_json(release_root / overlay_id / "manifest.json")
        base_id = overlay_manifest["base_release"]["release_id"]
    report_root = ROOT / "data" / "reports" / f"display-metadata-{overlay_id}"

    if args.command in {"prepare", "release"}:
        if args.command == "release" and not args.confirm_activate:
            raise SystemExit("'release' requires --confirm-activate")
        catalog = load_product_display_catalog(DISPLAY_CATALOG_PATH, DISPLAY_SCHEMA_PATH)
        prepare_release_pair(
            release_root=release_root,
            report_root=report_root,
            display_catalog=catalog,
            source_base_id=source_base,
            source_overlay_id=source_overlay,
            base_release_id=base_id,
            overlay_release_id=overlay_id,
        )
    if args.command in {"publish", "release"}:
        if args.command == "publish" and (not args.base_release_id or not args.overlay_release_id):
            raise SystemExit("'publish' requires --base-release-id and --overlay-release-id")
        publish_pair(
            release_root=release_root,
            catalog_snapshot_root=ROOT / "data" / "catalogs" / "releases",
            base_release_id=base_id,
            overlay_release_id=overlay_id,
            report_root=report_root,
        )
    if args.command in {"activate", "release"}:
        if args.command == "activate" and not args.overlay_release_id:
            raise SystemExit("'activate' requires --overlay-release-id")
        activate_overlay(
            release_root=release_root, overlay_release_id=overlay_id, report_root=report_root
        )

    print(
        json.dumps(
            {
                "baseReleaseId": base_id,
                "overlayReleaseId": overlay_id,
                "reportRoot": str(report_root),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
