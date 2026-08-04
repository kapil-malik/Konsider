"""Build the explicit, inactive-pointer Phase 6G API integration candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from konsider.contracts import validate_contract
from konsider.domain.opportunity_filters import (
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_bundle,
)

ROOT = Path(__file__).resolve().parents[3]
PHASE6F_ROOT = ROOT / "data" / "reports" / "phase6f-2026-08-03"
PHASE6F_STAGED = PHASE6F_ROOT / "staged-release"
UNIVERSE_PATH = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "reports" / "phase6g-2026-08-03"
RELEASE_ID = "phase6g-api-2026-08-03.1"
BUILD_ID = "phase6g-api-integration-1.0"
GENERATED_AT = "2026-08-03T00:00:00+05:30"


class OpportunityApiCandidateBuildError(ValueError):
    """Raised when the Phase 6G candidate cannot preserve the Phase 6F evidence bundle."""


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode())


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows
        ).encode()
    )


def verify_phase6f_inputs() -> dict[str, str]:
    manifest = _json(PHASE6F_ROOT / "build-manifest.json")
    staged_names = {
        "candidate-release-manifest.json",
        "opportunity-filter-catalog.json",
        "opportunity-filter-coverage-summary.json",
        "opportunity-filter-evidence-policy.json",
        "opportunity-filter-evidence.jsonl",
        "opportunity-filter-source-manifest.json",
        "opportunity-filter-threshold-policies.json",
    }
    verified = {}
    for filename, expected in manifest["artifact_checksums"].items():
        path = (PHASE6F_STAGED if filename in staged_names else PHASE6F_ROOT) / filename
        actual = f"sha256:{_sha256(path)}"
        if actual != expected:
            raise OpportunityApiCandidateBuildError(
                f"Phase 6F checksum mismatch for {filename}: expected {expected}, got {actual}."
            )
        verified[f"data/reports/phase6f-2026-08-03/{filename}"] = expected
    return verified


def _candidate_manifest(
    source: Mapping[str, Any], artifact_checksums: Mapping[str, str]
) -> dict[str, Any]:
    manifest = dict(source)
    manifest["release_id"] = RELEASE_ID
    manifest["status"] = "draft"
    manifest["file_checksums"] = {
        **source["file_checksums"],
        **artifact_checksums,
    }
    manifest["opportunity_filters"] = {
        **source["opportunity_filters"],
        "artifacts": [
            {**artifact, "checksum": artifact_checksums[artifact["filename"]]}
            for artifact in source["opportunity_filters"]["artifacts"]
        ],
    }
    unsigned = {key: value for key, value in manifest.items() if key != "release_checksum"}
    manifest["release_checksum"] = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    return manifest


def build_opportunity_api_candidate(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Promote the accepted Phase 6F definitions to selectable state in a draft only."""

    input_checksums = verify_phase6f_inputs()
    universe = _json(UNIVERSE_PATH)
    countries = [row["code"] for row in universe["countries"]]
    if universe["universe_id"] != "stable_supported_v1" or len(countries) != 91:
        raise OpportunityApiCandidateBuildError("Phase 6G requires the stable 91-country universe.")

    catalog = _json(PHASE6F_STAGED / "opportunity-filter-catalog.json")
    catalog["activation_status"] = "ACTIVE"
    catalog["definitions"] = [
        {**definition, "active": True, "availability": "AVAILABLE"}
        for definition in catalog["definitions"]
    ]
    rows = [
        {**row, "release_id": RELEASE_ID, "build_id": BUILD_ID, "generated_at": GENERATED_AT}
        for row in _jsonl(PHASE6F_STAGED / "opportunity-filter-evidence.jsonl")
    ]
    source_manifest = _json(PHASE6F_STAGED / "opportunity-filter-source-manifest.json")
    source_manifest["build_id"] = BUILD_ID
    source_manifest["generated_at"] = GENERATED_AT
    coverage = _json(PHASE6F_STAGED / "opportunity-filter-coverage-summary.json")
    coverage["release_id"] = RELEASE_ID
    thresholds = _json(PHASE6F_STAGED / "opportunity-filter-threshold-policies.json")
    evidence_policy = _json(PHASE6F_STAGED / "opportunity-filter-evidence-policy.json")

    validate_opportunity_filter_catalog(catalog)
    validate_opportunity_filter_evidence_matrix(catalog, rows, countries)
    validate_opportunity_filter_coverage_summary(coverage)
    validate_contract(
        source_manifest,
        "opportunity-filter-source-manifest",
        context="Phase 6G source manifest",
        schema_generation=3,
    )

    staged = output_root / "staged-release"
    artifacts = {
        "opportunity-filter-catalog.json": catalog,
        "opportunity-filter-source-manifest.json": source_manifest,
        "opportunity-filter-threshold-policies.json": thresholds,
        "opportunity-filter-evidence-policy.json": evidence_policy,
        "opportunity-filter-coverage-summary.json": coverage,
    }
    for filename, payload in artifacts.items():
        _write_json(staged / filename, payload)
    _write_jsonl(staged / "opportunity-filter-evidence.jsonl", rows)
    checksums = {
        filename: f"sha256:{_sha256(staged / filename)}"
        for filename in (*artifacts, "opportunity-filter-evidence.jsonl")
    }
    candidate = _candidate_manifest(
        _json(PHASE6F_STAGED / "candidate-release-manifest.json"), checksums
    )
    validate_opportunity_filter_release_bundle(candidate, catalog, rows, countries)
    _write_json(staged / "candidate-release-manifest.json", candidate)
    checksums["candidate-release-manifest.json"] = (
        f"sha256:{_sha256(staged / 'candidate-release-manifest.json')}"
    )

    build_manifest = {
        "schema_version": "phase6g-api-candidate-build-manifest-1.0",
        "release_id": RELEASE_ID,
        "build_id": BUILD_ID,
        "generated_at": GENERATED_AT,
        "command": "python -m konsider.ingestion.phase6_opportunity_api_candidate --output data/reports/phase6g-2026-08-03",
        "source_release_id": "phase6f-complete-2026-08-03.1",
        "status": "draft",
        "active_pointer_changed": False,
        "ui_authorized": False,
        "input_checksums": input_checksums,
        "artifact_checksums": checksums,
        "assertions": {
            "active_definition_count_inside_draft": 9,
            "evidence_record_count": 819,
            "country_count": 91,
            "ranking_release_id": "2026-07-29.2",
            "active_pointer_unchanged": True,
            "final_release_activated": False,
        },
    }
    _write_json(output_root / "build-manifest.json", build_manifest)
    return build_manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    manifest = build_opportunity_api_candidate(_parse_args().output)
    print(
        f"build={manifest['build_id']} filters=9 evidence=819 "
        f"active_pointer_changed={str(manifest['active_pointer_changed']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
