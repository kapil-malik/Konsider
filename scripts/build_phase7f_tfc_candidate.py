"""Capture, build, and replay the staged Phase 7F first-wave TFC release."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from konsider.ingestion.tfc_first_wave import (
    build_first_wave_production_capture,
    capture_source_inventory,
    reconcile_phase7b,
    validate_source_capture,
)
from konsider.ingestion.tfc_release import (
    TfcCandidateReleaseRepository,
    build_tfc_release_artifacts,
)


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def _fetch(url: str) -> tuple[str, int, str, bytes]:
    marker = b"\nKONSIDER_CAPTURE_META\t"
    result = subprocess.run(
        [
            "curl.exe",
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--retry",
            "4",
            "--retry-all-errors",
            "--retry-delay",
            "2",
            "--connect-timeout",
            "30",
            "--max-time",
            "120",
            "--user-agent",
            "Mozilla/5.0 (compatible; Konsider evidence capture/1.0)",
            "--write-out",
            "\nKONSIDER_CAPTURE_META\\t%{url_effective}\\t%{http_code}\\t%{content_type}",
            url,
        ],
        check=False,
        capture_output=True,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"curl capture failed for {url}: {message}")
    try:
        content, metadata = result.stdout.rsplit(marker, 1)
        final_url, status, content_type = metadata.decode("utf-8").split("\t", 2)
    except ValueError as exc:
        raise RuntimeError(f"curl capture metadata was invalid for {url}.") from exc
    return final_url, int(status), content_type, content


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _capture(args: argparse.Namespace) -> int:
    capture = capture_source_inventory(_fetch, captured_at=args.captured_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_json_bytes(capture))
    print(
        json.dumps(
            {
                "asset_count": len(capture["assets"]),
                "output": str(args.output),
                "raw_retained": False,
                "status": "CAPTURED",
            },
            sort_keys=True,
        )
    )
    return 0


def _build(args: argparse.Namespace) -> int:
    source_capture = _read_json(args.source_capture)
    validate_source_capture(source_capture)
    production_capture = build_first_wave_production_capture(
        source_capture,
        release_id=args.release_id,
        validation_date=args.validation_date,
    )
    research_rows = _read_jsonl(args.research_support)
    reconciliation = reconcile_phase7b(production_capture, research_rows)
    if reconciliation["status"] != "PASSED":
        raise ValueError("Phase 7B reconciliation requires owner approval before staging.")
    artifacts = build_tfc_release_artifacts(production_capture)
    base_manifest = _read_json(args.base_release / "manifest.json")
    args.output.mkdir(parents=True, exist_ok=True)
    production_capture_path = args.output / "production-capture.json"
    reconciliation_path = args.output / "research-production-reconciliation.json"
    production_capture_path.write_bytes(_json_bytes(production_capture))
    reconciliation_path.write_bytes(_json_bytes(reconciliation))
    release_path = TfcCandidateReleaseRepository(args.output / "staged-release").write_draft(
        args.release_id,
        artifacts,
        base_manifest=base_manifest,
    )
    print(
        json.dumps(
            {
                "release_path": str(release_path),
                "route_rule_count": len(production_capture["rules"]),
                "source_asset_count": len(source_capture["assets"]),
                "status": "STAGED",
                "support_record_count": len(artifacts.catalog["definitions"]) * 91,
                "tfc_count": len(artifacts.catalog["definitions"]),
            },
            sort_keys=True,
        )
    )
    return 0


def _replay(args: argparse.Namespace) -> int:
    capture = _read_json(args.production_capture)
    repository = TfcCandidateReleaseRepository(args.release.parent)
    result = repository.replay(args.release, capture)
    print(
        json.dumps(
            {
                "compared_files": list(result.compared_files),
                "mismatched_files": list(result.mismatched_files),
                "status": result.status,
            },
            sort_keys=True,
        )
    )
    return 0 if result.passed else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture = subparsers.add_parser("capture")
    capture.add_argument("--captured-at", required=True)
    capture.add_argument("--output", type=Path, required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--source-capture", type=Path, required=True)
    build.add_argument("--research-support", type=Path, required=True)
    build.add_argument("--base-release", type=Path, required=True)
    build.add_argument("--release-id", required=True)
    build.add_argument("--validation-date", required=True)
    build.add_argument("--output", type=Path, required=True)
    replay = subparsers.add_parser("replay")
    replay.add_argument("--production-capture", type=Path, required=True)
    replay.add_argument("--release", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "capture":
        return _capture(args)
    if args.command == "build":
        return _build(args)
    return _replay(args)


if __name__ == "__main__":
    raise SystemExit(main())
