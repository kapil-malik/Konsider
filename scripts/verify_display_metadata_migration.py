"""Verify that the published display-metadata migration preserves product semantics."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.tfc_service import TfcApiService
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.ingestion.tfc_release import TfcCandidateReleaseRepository
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / "data" / "releases"
REPORT = (
    ROOT
    / "data"
    / "reports"
    / "catalog-display-metadata-2026-08-07"
    / "cross-feature-verification.json"
)
SOURCE_BASE_ID = "2026-08-04.1"
SOURCE_OVERLAY_ID = "2026-08-05.1"
TARGET_BASE_ID = "2026-08-07.1"
TARGET_OVERLAY_ID = "2026-08-07.2"
IDENTITY_KEYS = {
    "api_contract_version",
    "release_id",
    "release_schema_version",
    "catalog_schema_version",
    "opportunity_release_id",
    "tfc_release_id",
    "tfc_release_schema_version",
    "snapshot_id",
}


def _checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _semantic(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _semantic(child)
            for key, child in sorted(value.items())
            if key not in IDENTITY_KEYS
        }
    if isinstance(value, list):
        return [_semantic(child) for child in value]
    return value


def _service(base_id: str, overlay_id: str) -> RecommendationService:
    base = CurrentReleaseRepository(RELEASES).load(RELEASES / base_id)
    overlay = TfcCandidateReleaseRepository(RELEASES).load(RELEASES / overlay_id)
    return RecommendationService(
        base,
        OpportunityFilterService.from_release(base.path, base.manifest),
        TfcApiService.from_published(overlay, base.manifest),
    )


def main() -> int:
    unchanged_files: list[dict[str, str]] = []
    for source_id, target_id, changed in (
        (
            SOURCE_BASE_ID,
            TARGET_BASE_ID,
            {"manifest.json", "consumer-catalog.json", "opportunity-filter-catalog.json"},
        ),
        (SOURCE_OVERLAY_ID, TARGET_OVERLAY_ID, {"manifest.json", "tfc-catalog.json"}),
    ):
        for source in sorted((RELEASES / source_id).iterdir()):
            if source.name in changed:
                continue
            target = RELEASES / target_id / source.name
            if source.read_bytes() != target.read_bytes():
                raise AssertionError(f"Unchanged artifact differs: {source_id}/{source.name}")
            unchanged_files.append(
                {
                    "filename": source.name,
                    "sourceReleaseId": source_id,
                    "targetReleaseId": target_id,
                    "checksum": _checksum(source),
                }
            )

    before = _service(SOURCE_BASE_ID, SOURCE_OVERLAY_ID)
    after = _service(TARGET_BASE_ID, TARGET_OVERLAY_ID)
    cases: dict[str, Callable[[RecommendationService], Any]] = {
        "catalog": lambda service: service.catalog(),
        "opportunity_filter_catalog": lambda service: service.opportunity_filter_catalog(),
        "tfc_catalog": lambda service: service.tfc_catalog(),
        "ranking": lambda service: service.rank(None, preference_preset_id=None, top_k=10),
        "ranking_with_ofc": lambda service: service.rank(
            None,
            preference_preset_id=None,
            top_k=10,
            opportunity_filter_ids=["technology_software_opportunity"],
        ),
        "ranking_with_tfc": lambda service: service.rank(
            None,
            preference_preset_id=None,
            top_k=10,
            feasibility={
                "tfc_ids": ["skilled_work_route_feasibility"],
                "mode": "ASSESS_ONLY",
                "context": None,
            },
        ),
        "comparison": lambda service: service.compare(
            ["ALB", "ARE"], None, preference_preset_id=None
        ),
        "country_details": lambda service: service.country_details(
            "ALB", None, preference_preset_id=None
        ),
    }
    verified_cases = []
    for name, run in cases.items():
        before_value = _semantic(run(before))
        after_value = _semantic(run(after))
        if before_value != after_value:
            raise AssertionError(f"Cross-feature semantics changed for {name}.")
        body = json.dumps(after_value, sort_keys=True, separators=(",", ":")).encode()
        verified_cases.append(
            {
                "name": name,
                "status": "PASSED",
                "semanticChecksum": "sha256:" + hashlib.sha256(body).hexdigest(),
            }
        )

    report = {
        "schemaVersion": "catalog-display-metadata-cross-feature-verification-1.0",
        "status": "PASSED",
        "sourceBaseReleaseId": SOURCE_BASE_ID,
        "sourceOverlayReleaseId": SOURCE_OVERLAY_ID,
        "targetBaseReleaseId": TARGET_BASE_ID,
        "targetOverlayReleaseId": TARGET_OVERLAY_ID,
        "unchangedArtifactCount": len(unchanged_files),
        "unchangedArtifacts": unchanged_files,
        "cases": verified_cases,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(REPORT, json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
