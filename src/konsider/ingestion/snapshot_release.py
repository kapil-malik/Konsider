"""Build the coordinated region and Balanced-preset release snapshot pair."""

from __future__ import annotations

import argparse
import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any

from konsider.contracts import validate_contract
from konsider.ingestion.current_release import (
    CurrentReleaseArtifacts,
    CurrentReleaseRepository,
    validate_current_artifacts,
)
from konsider.ingestion.display_metadata_migration import (
    _checksum,
    _overlay_release_checksum,
    _read_json,
    _release_checksum,
    _write_json,
    activate_overlay,
    publish_pair,
)
from konsider.ingestion.display_metadata_release import _active_pair, derive_release_ids
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[3]
STABLE_UNIVERSE = ROOT / "data" / "country-universes" / "stable-supported-v1.json"


class SnapshotReleaseError(ValueError):
    """Raised when the release batch cannot preserve its declared invariants."""


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    write_text_lf(
        path,
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
    )


def _copy_except(source: Path, target: Path, excluded: set[str]) -> dict[str, str]:
    copied = {}
    for path in source.iterdir():
        if path.name in excluded:
            continue
        destination = target / path.name
        shutil.copyfile(path, destination)
        if destination.read_bytes() != path.read_bytes():
            raise SnapshotReleaseError(f"Copied artifact changed unexpectedly: {path.name}")
        copied[path.name] = _checksum(destination)
    return copied


def _migrate_base(source_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    source = CurrentReleaseRepository(source_path.parent).load(source_path)
    entities = [deepcopy(row) for row in source.artifacts.geographic_entities]
    catalog = deepcopy(source.artifacts.consumer_catalog)
    universe = _read_json(STABLE_UNIVERSE)
    regions = {row["code"]: row["region"] for row in universe["countries"]}
    country_ids = {row["entity_id"] for row in entities if row["entity_type"] == "COUNTRY"}
    expected_ids = {f"country:{code}" for code in regions}
    if country_ids != expected_ids:
        raise SnapshotReleaseError("Stable-universe and release country inventories disagree.")
    for row in entities:
        if row["entity_type"] == "COUNTRY":
            row["region"] = regions[row["country_codes"][0]]
    catalog["geographic_entities"] = deepcopy(entities)

    presets = {row["id"]: row for row in catalog["preference_presets"]}
    balanced = presets.get("equal_weight_mvp")
    enabled = {row["id"] for row in catalog["criteria"] if row["default_enabled"]}
    if balanced is None or set(balanced["weights"]) != enabled:
        raise SnapshotReleaseError("Balanced weights must exactly match enabled criteria.")
    balanced["weights"] = {criterion_id: 0.6 for criterion_id in sorted(enabled)}

    artifacts = CurrentReleaseArtifacts(
        geographic_entities=tuple(entities),
        observations=source.artifacts.observations,
        scores=source.artifacts.scores,
        criterion_outcomes=source.artifacts.criterion_outcomes,
        derived_country_evidence=source.artifacts.derived_country_evidence,
        source_lineages=source.artifacts.source_lineages,
        locality_universes=source.artifacts.locality_universes,
        aggregation_policies=source.artifacts.aggregation_policies,
        criterion_policies=source.artifacts.criterion_policies,
        consumer_catalog=catalog,
    )
    validation = validate_current_artifacts(artifacts)
    if not validation["structural_passed"] or not validation["product_ready"]:
        raise SnapshotReleaseError("Migrated release failed product-readiness validation.")
    return entities, catalog, validation


def prepare_release_pair(
    *,
    release_root: Path,
    report_root: Path,
    source_base_id: str,
    source_overlay_id: str,
    base_release_id: str,
    overlay_release_id: str,
) -> tuple[Path, Path]:
    """Prepare one validated base/overlay snapshot batch without activating it."""

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

    base_source_manifest = _read_json(source_base / "manifest.json")
    overlay_source_manifest = _read_json(source_overlay / "manifest.json")
    if base_source_manifest["schema_version"] != "konsider-release-5.2":
        raise SnapshotReleaseError("Source base must use konsider-release-5.2.")
    if overlay_source_manifest["base_release"]["release_id"] != source_base_id:
        raise SnapshotReleaseError("Source overlay does not bind the selected source base.")

    entities, catalog, validation = _migrate_base(source_base)
    base_draft.mkdir(parents=True)
    unchanged_base = _copy_except(
        source_base,
        base_draft,
        {"manifest.json", "geographic-entities.jsonl", "consumer-catalog.json", "validation.json"},
    )
    _write_jsonl(base_draft / "geographic-entities.jsonl", entities)
    _write_json(base_draft / "consumer-catalog.json", catalog)
    _write_json(base_draft / "validation.json", validation)
    base_checksums = {path.name: _checksum(path) for path in base_draft.iterdir()}
    base_manifest = {
        **base_source_manifest,
        "release_id": base_release_id,
        "status": "draft",
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
        base_manifest, "release-manifest", context="snapshot base", schema_generation=5
    )
    _write_json(base_draft / "manifest.json", base_manifest)
    CurrentReleaseRepository(release_root).load(base_draft)

    overlay_draft.mkdir(parents=True)
    unchanged_overlay = _copy_except(source_overlay, overlay_draft, {"manifest.json"})
    overlay_manifest = {
        **overlay_source_manifest,
        "release_id": overlay_release_id,
        "status": "draft",
        "activation_authorized": False,
        "base_release": {
            "release_id": base_release_id,
            "schema_version": base_manifest["schema_version"],
            "release_checksum": base_manifest["release_checksum"],
        },
    }
    overlay_manifest["release_checksum"] = _overlay_release_checksum(overlay_manifest)
    validate_contract(
        overlay_manifest, "tfc-release-manifest", context="snapshot overlay", schema_generation=5
    )
    _write_json(overlay_draft / "manifest.json", overlay_manifest)

    report_root.mkdir(parents=True, exist_ok=True)
    _write_json(
        report_root / "build-manifest.json",
        {
            "schemaVersion": "konsider-snapshot-release-build-1.0",
            "status": "DRAFTS_BUILT",
            "sourceBaseReleaseId": source_base_id,
            "sourceOverlayReleaseId": source_overlay_id,
            "baseReleaseId": base_release_id,
            "baseReleaseChecksum": base_manifest["release_checksum"],
            "overlayReleaseId": overlay_release_id,
            "overlayReleaseChecksum": overlay_manifest["release_checksum"],
            "countryRegionCount": sum(
                1 for row in entities if row["entity_type"] == "COUNTRY" and row.get("region")
            ),
            "balancedCriterionCount": len(
                next(
                    row for row in catalog["preference_presets"] if row["id"] == "equal_weight_mvp"
                )["weights"]
            ),
            "unchangedBaseArtifacts": unchanged_base,
            "unchangedOverlayArtifacts": unchanged_overlay,
        },
    )
    return base_draft, overlay_draft


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "publish", "activate", "release"))
    parser.add_argument("--base-release-id")
    parser.add_argument("--overlay-release-id")
    parser.add_argument("--confirm-activate", action="store_true")
    args = parser.parse_args()
    release_root = ROOT / "data" / "releases"
    source_base, source_overlay = _active_pair(release_root)
    generated_base, generated_overlay = derive_release_ids(release_root)
    base_id = args.base_release_id or generated_base
    overlay_id = args.overlay_release_id or generated_overlay
    if args.command == "activate":
        if not args.overlay_release_id:
            raise SystemExit("'activate' requires --overlay-release-id")
        base_id = _read_json(release_root / overlay_id / "manifest.json")["base_release"][
            "release_id"
        ]
    report_root = ROOT / "data" / "reports" / f"snapshot-release-{overlay_id}"
    if args.command in {"prepare", "release"}:
        if args.command == "release" and not args.confirm_activate:
            raise SystemExit("'release' requires --confirm-activate")
        prepare_release_pair(
            release_root=release_root,
            report_root=report_root,
            source_base_id=source_base,
            source_overlay_id=source_overlay,
            base_release_id=base_id,
            overlay_release_id=overlay_id,
        )
    if args.command in {"publish", "release"}:
        if args.command == "publish" and (not args.base_release_id or not args.overlay_release_id):
            raise SystemExit("'publish' requires both release IDs")
        publish_pair(
            release_root=release_root,
            catalog_snapshot_root=ROOT / "data" / "catalogs" / "releases",
            base_release_id=base_id,
            overlay_release_id=overlay_id,
            report_root=report_root,
        )
    if args.command in {"activate", "release"}:
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
