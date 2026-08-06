"""Build the approved Phase 4 Wave 2 experimental PCC release."""

from __future__ import annotations

import argparse
from pathlib import Path

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.ingestion.phase4_wave2 import build_wave2_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-id", default="2026-07-28.2")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--release-root", type=Path, default=Path("data/releases"))
    parser.add_argument(
        "--base-release",
        type=Path,
        default=Path("data/releases/2026-07-28.1"),
    )
    parser.add_argument(
        "--base-catalog",
        type=Path,
        default=Path("data/catalogs/consumer-catalog-2.0.json"),
    )
    parser.add_argument(
        "--catalog-output",
        type=Path,
        default=Path("data/catalogs/consumer-catalog-2.0.json"),
    )
    parser.add_argument(
        "--school-probe-artifacts",
        type=Path,
        default=Path(
            "data/reports/feasibility-probes/" "phase3e-2026-07-26-c08-online-v2/raw-artifacts.json"
        ),
    )
    parser.add_argument(
        "--wipo-raw",
        type=Path,
        default=Path("data/raw/wave2-probes/wipo-gii-2025.xlsx"),
    )
    parser.add_argument(
        "--report-root",
        type=Path,
        default=Path("data/reports/phase4-wave2-2026-07-28"),
    )
    parser.add_argument("--created-at")
    args = parser.parse_args()
    display_catalog = load_product_display_catalog(
        Path("data/catalogs/product-display-catalog.json"),
        Path("contracts/schemas/authoring/product-display-catalog.schema.json"),
    )
    path = build_wave2_release(
        release_id=args.release_id,
        base_release_path=args.base_release,
        base_catalog_path=args.base_catalog,
        catalog_output_path=args.catalog_output,
        school_probe_artifact_manifest=args.school_probe_artifacts,
        wipo_raw_path=args.wipo_raw,
        release_root=args.release_root,
        report_root=args.report_root,
        display_catalog=display_catalog,
        publish=args.publish,
        created_at=args.created_at,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
