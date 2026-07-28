"""Build the Phase 4F Overall job-market opportunity production release."""

from __future__ import annotations

import argparse
from pathlib import Path

from konsider.ingestion.phase4f import build_c11_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-id", default="2026-07-28.1")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--release-root", type=Path, default=Path("data/releases"))
    parser.add_argument(
        "--base-release",
        type=Path,
        default=Path("data/releases/2026-07-27.1"),
    )
    parser.add_argument(
        "--base-catalog",
        type=Path,
        default=Path("data/catalogs/consumer-catalog-1.0.json"),
    )
    parser.add_argument(
        "--catalog-v2",
        type=Path,
        default=Path("data/catalogs/consumer-catalog-2.0.json"),
    )
    parser.add_argument(
        "--probe-artifacts",
        type=Path,
        default=Path(
            "data/reports/feasibility-probes/" "phase3e-2026-07-26-c11-online/raw-artifacts.json"
        ),
    )
    parser.add_argument(
        "--report-root",
        type=Path,
        default=Path("data/reports/phase4f-2026-07-28"),
    )
    parser.add_argument("--created-at")
    args = parser.parse_args()
    path = build_c11_release(
        release_id=args.release_id,
        base_release_path=args.base_release,
        base_catalog_path=args.base_catalog,
        catalog_v2_path=args.catalog_v2,
        probe_artifact_manifest=args.probe_artifacts,
        release_root=args.release_root,
        report_root=args.report_root,
        publish=args.publish,
        created_at=args.created_at,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
