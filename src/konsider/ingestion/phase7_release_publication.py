"""Build, publish, activate, replay, and roll back the Phase 7 TFC overlay."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.ingestion.tfc_first_wave import FIRST_WAVE_TFC_IDS
from konsider.ingestion.tfc_release import (
    PAYLOAD_FILES,
    LoadedTfcRelease,
    TfcCandidateReleaseRepository,
    TfcReleaseError,
    _json_bytes,
    _release_checksum,
    build_tfc_release_artifacts,
)

FINAL_RELEASE_ID = "2026-08-05.1"
BASE_RELEASE_ID = "2026-08-04.1"
RELEASE_SCHEMA_VERSION = "konsider-release-6.0"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_json_bytes(payload))
    os.replace(temporary, path)


def _owner_gate(loaded: LoadedTfcRelease) -> None:
    artifacts = loaded.artifacts
    definition_ids = tuple(row["tfc_id"] for row in artifacts.catalog["definitions"])
    if set(definition_ids) != set(FIRST_WAVE_TFC_IDS) or len(definition_ids) < 3:
        raise TfcReleaseError("The release does not satisfy the owner-approved minimum-three gate.")
    if any(row["filter_capability"] != "ASSESS_ONLY" for row in artifacts.catalog["definitions"]):
        raise TfcReleaseError("Every first-wave TFC must remain assessment-only.")
    coverage = artifacts.coverage_summary
    if coverage["actual_support_records"] != 273 or any(
        row["support_state_counts"]["SUPPORTED"] != 29 for row in coverage["by_tfc"]
    ):
        raise TfcReleaseError("The release does not preserve the approved 29/91 support boundary.")
    if artifacts.catalog["activation_status"] != "ACTIVE":
        raise TfcReleaseError("The final TFC catalog is not marked active.")
    if (
        not artifacts.validation["structural_passed"]
        or not artifacts.validation["promotion_eligible"]
    ):
        raise TfcReleaseError("The final TFC validation report is not promotion-eligible.")


def build_release(
    *,
    release_root: Path,
    production_capture: Path,
    report_root: Path,
    release_id: str = FINAL_RELEASE_ID,
    base_release_id: str = BASE_RELEASE_ID,
) -> Path:
    """Build a final, owner-approved draft without changing the active pointer."""

    pointer_path = release_root / "active.json"
    pointer_before = pointer_path.read_bytes()
    base = CurrentReleaseRepository(release_root).load(release_root / base_release_id)
    capture = copy.deepcopy(_read_json(production_capture))
    capture["catalog"]["activation_status"] = "ACTIVE"
    artifacts = build_tfc_release_artifacts(capture)
    draft = TfcCandidateReleaseRepository(release_root / ".draft").write_draft(
        release_id,
        artifacts,
        base_manifest=base.manifest,
    )
    loaded = TfcCandidateReleaseRepository(draft.parent).load(draft)
    _owner_gate(loaded)
    if pointer_path.read_bytes() != pointer_before:
        raise TfcReleaseError("Candidate verification changed the active pointer.")
    _write_json(
        report_root / "build-manifest.json",
        {
            "schema_version": "phase7-release-build-report-1.0",
            "release_id": release_id,
            "base_release": loaded.manifest["base_release"],
            "status": "draft",
            "owner_approved_tfc_ids": sorted(FIRST_WAVE_TFC_IDS),
            "file_checksums": loaded.manifest["file_checksums"],
            "release_checksum": loaded.manifest["release_checksum"],
            "support_records": artifacts.coverage_summary["actual_support_records"],
            "supported_destinations_per_tfc": 29,
        },
    )
    return draft


def publish_release(
    release_id: str,
    *,
    release_root: Path,
    report_root: Path,
) -> Path:
    """Move a strictly validated draft into the immutable release namespace."""

    draft = release_root / ".draft" / release_id
    published = release_root / release_id
    if published.exists():
        raise FileExistsError(f"Published TFC release is immutable: {release_id}")
    repository = TfcCandidateReleaseRepository(draft.parent)
    loaded = repository.load(draft)
    _owner_gate(loaded)
    if loaded.manifest["status"] != "draft" or loaded.manifest["activation_authorized"]:
        raise TfcReleaseError("Only an unauthorized draft can enter publication.")
    manifest = copy.deepcopy(loaded.manifest)
    manifest["status"] = "published"
    manifest["activation_authorized"] = True
    manifest["release_checksum"] = _release_checksum(manifest)
    (draft / "manifest.json").write_bytes(_json_bytes(manifest))
    repository.load(draft)
    draft.replace(published)
    report = _read_json(report_root / "build-manifest.json")
    report.update(
        {
            "status": "published",
            "release_checksum": manifest["release_checksum"],
        }
    )
    _write_json(report_root / "build-manifest.json", report)
    return published


def load_active_tfc_release(
    release_root: Path,
    pointer_path: Path | None = None,
) -> LoadedTfcRelease | None:
    """Load the active release-6 overlay, or return none for a schema-5 pointer."""

    pointer = _read_json(pointer_path or release_root / "active.json")
    if pointer.get("schema_version") != RELEASE_SCHEMA_VERSION:
        return None
    release_id = pointer.get("release_id")
    if not isinstance(release_id, str) or not release_id:
        raise TfcReleaseError("The active release-6 pointer has no valid release ID.")
    release = TfcCandidateReleaseRepository(release_root).load(release_root / release_id)
    if release.manifest["release_id"] != release_id:
        raise TfcReleaseError("The active pointer and TFC release ID disagree.")
    if release.manifest["status"] != "published" or not release.manifest["activation_authorized"]:
        raise TfcReleaseError("The active TFC overlay is not published and authorized.")
    _owner_gate(release)
    base_path = release_root / release.manifest["base_release"]["release_id"]
    base = CurrentReleaseRepository(release_root).load(base_path)
    expected_base = {
        "release_id": base.manifest["release_id"],
        "schema_version": base.manifest["schema_version"],
        "release_checksum": base.manifest["release_checksum"],
    }
    if release.manifest["base_release"] != expected_base:
        raise TfcReleaseError("The active TFC overlay does not match its immutable base release.")
    return release


def activate_release(
    release_id: str,
    *,
    release_root: Path,
    report_root: Path,
) -> Path:
    """Atomically select an already-published release-6 overlay."""

    release = TfcCandidateReleaseRepository(release_root).load(release_root / release_id)
    _owner_gate(release)
    if release.manifest["status"] != "published" or not release.manifest["activation_authorized"]:
        raise TfcReleaseError("Only a published, authorized TFC overlay can be activated.")
    pointer = release_root / "active.json"
    _write_json(
        pointer,
        {"release_id": release_id, "schema_version": RELEASE_SCHEMA_VERSION},
    )
    load_active_tfc_release(release_root, pointer)
    report = _read_json(report_root / "build-manifest.json")
    report["status"] = "active"
    report["rollback_release_id"] = release.manifest["base_release"]["release_id"]
    _write_json(report_root / "build-manifest.json", report)
    return pointer


def rollback_to_base(*, release_root: Path, release_id: str = BASE_RELEASE_ID) -> Path:
    """Atomically restore a validated schema-5 base pointer without mutating releases."""

    base = CurrentReleaseRepository(release_root).load(release_root / release_id)
    pointer = release_root / "active.json"
    _write_json(
        pointer,
        {"release_id": release_id, "schema_version": base.manifest["schema_version"]},
    )
    CurrentReleaseRepository(release_root).load_active(pointer)
    return pointer


def replay_release(
    release_path: Path,
    *,
    production_capture: Path,
) -> tuple[str, ...]:
    """Rebuild a published overlay offline and return mismatched filenames."""

    source = TfcCandidateReleaseRepository(release_path.parent).load(release_path)
    with tempfile.TemporaryDirectory(prefix="konsider-phase7-replay-") as temporary:
        root = Path(temporary) / "releases"
        reports = Path(temporary) / "reports"
        root.mkdir(parents=True)
        source_root = (
            release_path.parent.parent
            if release_path.parent.name == ".draft"
            else release_path.parent
        )
        base_source = source_root / source.manifest["base_release"]["release_id"]
        base_target = root / source.manifest["base_release"]["release_id"]
        import shutil

        shutil.copytree(base_source, base_target)
        _write_json(
            root / "active.json",
            {
                "release_id": source.manifest["base_release"]["release_id"],
                "schema_version": source.manifest["base_release"]["schema_version"],
            },
        )
        build_release(
            release_root=root,
            production_capture=production_capture,
            report_root=reports,
            release_id=source.manifest["release_id"],
            base_release_id=source.manifest["base_release"]["release_id"],
        )
        rebuilt = root / ".draft" / source.manifest["release_id"]
        if source.manifest["status"] == "published":
            rebuilt = publish_release(
                source.manifest["release_id"], release_root=root, report_root=reports
            )
        compared = (*PAYLOAD_FILES, "manifest.json")
        return tuple(
            filename
            for filename in compared
            if (release_path / filename).read_bytes() != (rebuilt / filename).read_bytes()
        )


__all__ = [
    "BASE_RELEASE_ID",
    "FINAL_RELEASE_ID",
    "activate_release",
    "build_release",
    "load_active_tfc_release",
    "publish_release",
    "replay_release",
    "rollback_to_base",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-root", type=Path, default=PROJECT_ROOT / "data" / "releases")
    parser.add_argument(
        "--report-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports" / "phase7j-2026-08-05",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument(
        "--production-capture",
        type=Path,
        default=(
            PROJECT_ROOT / "data" / "reports" / "phase7f-2026-08-05" / "production-capture.json"
        ),
    )
    build.add_argument("--release-id", default=FINAL_RELEASE_ID)
    build.add_argument("--base-release-id", default=BASE_RELEASE_ID)
    publish = subparsers.add_parser("publish")
    publish.add_argument("--release-id", default=FINAL_RELEASE_ID)
    activate = subparsers.add_parser("activate")
    activate.add_argument("--release-id", default=FINAL_RELEASE_ID)
    replay = subparsers.add_parser("replay")
    replay.add_argument("--release-id", default=FINAL_RELEASE_ID)
    replay.add_argument(
        "--production-capture",
        type=Path,
        default=(
            PROJECT_ROOT / "data" / "reports" / "phase7f-2026-08-05" / "production-capture.json"
        ),
    )
    rollback = subparsers.add_parser("rollback")
    rollback.add_argument("--release-id", default=BASE_RELEASE_ID)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "build":
        path = build_release(
            release_root=args.release_root,
            production_capture=args.production_capture,
            report_root=args.report_root,
            release_id=args.release_id,
            base_release_id=args.base_release_id,
        )
        result: Any = {"status": "BUILT", "path": str(path)}
    elif args.command == "publish":
        path = publish_release(
            args.release_id,
            release_root=args.release_root,
            report_root=args.report_root,
        )
        result = {"status": "PUBLISHED", "path": str(path)}
    elif args.command == "activate":
        path = activate_release(
            args.release_id,
            release_root=args.release_root,
            report_root=args.report_root,
        )
        result = {"status": "ACTIVE", "pointer": str(path)}
    elif args.command == "replay":
        mismatches = replay_release(
            args.release_root / args.release_id,
            production_capture=args.production_capture,
        )
        result = {
            "status": "PASSED" if not mismatches else "FAILED",
            "mismatched_files": list(mismatches),
        }
    else:
        path = rollback_to_base(release_root=args.release_root, release_id=args.release_id)
        result = {"status": "ROLLED_BACK", "pointer": str(path)}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] != "FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
