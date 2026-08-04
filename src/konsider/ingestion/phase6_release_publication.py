"""Build, publish, and atomically activate the final Phase 6 release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

from konsider.contracts import validate_contract
from konsider.domain.opportunity_filters import (
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_bundle,
)
from konsider.ingestion.current_release import (
    OPPORTUNITY_RELEASE_SCHEMA_VERSION,
    PAYLOAD_FILES,
    CurrentReleaseError,
    CurrentReleaseRepository,
)
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RELEASE_ROOT = ROOT / "data" / "releases"
DEFAULT_CATALOG_ROOT = ROOT / "data" / "catalogs" / "releases"
DEFAULT_STAGED_ROOT = ROOT / "data" / "reports" / "phase6g-2026-08-03" / "staged-release"
DEFAULT_REPORT_ROOT = ROOT / "data" / "reports" / "phase6i-2026-08-04"
BUILD_ID = "phase6i-release-publication-1.0"
GENERATED_AT = "2026-08-04T00:00:00+05:30"

OPPORTUNITY_ARTIFACTS = {
    "CATALOG": ("opportunity-filter-catalog.json", "opportunity-filter-catalog-1.0"),
    "COUNTRY_EVIDENCE": (
        "opportunity-filter-evidence.jsonl",
        "opportunity-filter-evidence-1.0",
    ),
    "SOURCE_MANIFEST": (
        "opportunity-filter-source-manifest.json",
        "opportunity-filter-source-manifest-1.0",
    ),
    "THRESHOLD_POLICIES": (
        "opportunity-filter-threshold-policies.json",
        "opportunity-filter-threshold-policies-1.0",
    ),
    "EVIDENCE_POLICY": (
        "opportunity-filter-evidence-policy.json",
        "opportunity-filter-evidence-policy-1.0",
    ),
    "COVERAGE_SUMMARY": (
        "opportunity-filter-coverage-summary.json",
        "opportunity-filter-coverage-summary-1.0",
    ),
}

EXPECTED_NAMES = {
    "technology_software_opportunity": "Technology and software employment ecosystem",
    "science_engineering_opportunity": "Science and engineering employment ecosystem",
    "health_social_work_opportunity": "Care-sector employment ecosystem",
    "finance_insurance_opportunity": "Finance and insurance employment ecosystem",
    "skilled_trades_construction_opportunity": (
        "Skilled-trades or construction employment ecosystem"
    ),
    "engineering_technology_education_opportunity": (
        "Physical sciences and engineering research-university ecosystem"
    ),
    "computer_science_ict_education_opportunity": (
        "Mathematics and computer science research-university ecosystem"
    ),
    "medicine_health_sciences_education_opportunity": (
        "Biomedical and health sciences research-university ecosystem"
    ),
    "natural_sciences_education_opportunity": (
        "Life and earth sciences research-university ecosystem"
    ),
}

EXPECTED_STATE_COUNTS = {
    "technology_software_opportunity": (20, 43, 28),
    "science_engineering_opportunity": (20, 47, 24),
    "health_social_work_opportunity": (27, 61, 3),
    "finance_insurance_opportunity": (22, 66, 3),
    "skilled_trades_construction_opportunity": (34, 54, 3),
    "engineering_technology_education_opportunity": (27, 48, 16),
    "computer_science_ict_education_opportunity": (30, 45, 16),
    "medicine_health_sciences_education_opportunity": (30, 45, 16),
    "natural_sciences_education_opportunity": (31, 44, 16),
}

STATE_ORDER = (
    "VERIFIED_STRONG_SIGNAL",
    "STRONG_SIGNAL_NOT_ESTABLISHED",
    "INSUFFICIENT_EVIDENCE",
)


class Phase6ReleaseError(ValueError):
    """Raised when Phase 6 publication cannot satisfy the accepted release gates."""


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_json(path: Path, payload: Any) -> None:
    write_text_lf(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    write_text_lf(
        path,
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
    )


def _checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _release_checksum(checksums: Mapping[str, str]) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            json.dumps(checksums, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )


def _portable_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def derive_next_release_id(release_root: Path, release_date: date | None = None) -> str:
    """Derive the next YYYY-MM-DD.N ID without reusing an immutable directory."""

    prefix = (release_date or date.today()).isoformat()
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)$")
    sequences = [
        int(match.group(1))
        for path in release_root.iterdir()
        if path.is_dir() and (match := pattern.fullmatch(path.name))
    ]
    return f"{prefix}.{max(sequences, default=0) + 1}"


def _verify_candidate_checksums(staged_root: Path) -> dict[str, str]:
    build_manifest = _json(staged_root.parent / "build-manifest.json")
    verified: dict[str, str] = {}
    for filename, expected in build_manifest["artifact_checksums"].items():
        path = staged_root / filename
        actual = _checksum(path)
        if actual != expected:
            raise Phase6ReleaseError(
                f"Staged Phase 6G checksum mismatch for {filename}: {actual} != {expected}."
            )
        verified[f"data/reports/phase6g-2026-08-03/staged-release/{filename}"] = actual
    return verified


def _verify_research_inputs(staged_root: Path) -> dict[str, str]:
    build_manifest = _json(staged_root.parent / "build-manifest.json")
    verified: dict[str, str] = {}
    for relative, expected in build_manifest["input_checksums"].items():
        path = ROOT / relative
        if not path.is_file():
            historical_staged_path = path.parent / "staged-release" / path.name
            if not historical_staged_path.is_file():
                raise Phase6ReleaseError(f"Accepted Phase 6 input is unavailable: {relative}.")
            path = historical_staged_path
        actual = _checksum(path)
        if actual != expected:
            raise Phase6ReleaseError(
                f"Accepted Phase 6 input checksum mismatch for {relative}: {actual} != {expected}."
            )
        verified[path.relative_to(ROOT).as_posix()] = actual
    return verified


def _validate_accepted_product(
    catalog: Mapping[str, Any],
    rows: list[dict[str, Any]],
    coverage: Mapping[str, Any],
) -> None:
    definitions = {row["id"]: row for row in catalog["definitions"]}
    if {item: definitions[item]["display_name"] for item in definitions} != EXPECTED_NAMES:
        raise Phase6ReleaseError("The final nine public Opportunity Filter names disagree.")
    if catalog["activation_status"] != "ACTIVE" or any(
        not row["active"] or row["availability"] != "AVAILABLE" for row in definitions.values()
    ):
        raise Phase6ReleaseError("Every final Opportunity Filter must be active and available.")
    if any(
        key in definition
        for definition in definitions.values()
        for key in ("weight", "score", "direction", "normalization", "coefficient")
    ):
        raise Phase6ReleaseError("Opportunity Filter definitions cannot contain ranking fields.")

    actual_counts: dict[str, tuple[int, int, int]] = {}
    for filter_id in EXPECTED_NAMES:
        counts = Counter(row["state"] for row in rows if row["filter_id"] == filter_id)
        actual_counts[filter_id] = tuple(counts[state] for state in STATE_ORDER)
    if actual_counts != EXPECTED_STATE_COUNTS:
        raise Phase6ReleaseError("Final Opportunity Filter state counts disagree with acceptance.")

    if any(
        coverage["filters"][filter_id]["assessable_count"] != 75
        for filter_id in EXPECTED_NAMES
        if definitions[filter_id]["category"] == "EDUCATION"
    ):
        raise Phase6ReleaseError(
            "Every education filter must remain assessable for 75/91 countries."
        )

    canada = next(
        row
        for row in rows
        if row["filter_id"] == "technology_software_opportunity" and row["country_code"] == "CAN"
    )
    if (
        canada["confidence_band"] != "MEDIUM"
        or canada["internal_confidence_tier"] != "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK"
    ):
        raise Phase6ReleaseError(
            "Canada technology must retain medium-confidence official mapping."
        )

    skilled_rows = [
        row
        for row in rows
        if row["filter_id"] == "skilled_trades_construction_opportunity"
        and row["state"] == "VERIFIED_STRONG_SIGNAL"
    ]
    route_sets = {frozenset(row["establishing_route_ids"]) for row in skilled_rows}
    required_routes = {
        frozenset({"skilled_trades"}),
        frozenset({"construction"}),
        frozenset({"skilled_trades", "construction"}),
    }
    if not required_routes.issubset(route_sets):
        raise Phase6ReleaseError(
            "Skilled, construction and both-route attribution must remain visible."
        )

    lowered_names = " ".join(EXPECTED_NAMES.values()).lower()
    if "business education" in lowered_names or "broad university excellence" in lowered_names:
        raise Phase6ReleaseError("Held education constructs cannot enter the final catalog.")


def build_release(
    *,
    release_root: Path = DEFAULT_RELEASE_ROOT,
    catalog_root: Path = DEFAULT_CATALOG_ROOT,
    active_pointer: Path | None = None,
    staged_root: Path = DEFAULT_STAGED_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
    release_id: str | None = None,
    verify_research_inputs: bool = True,
) -> tuple[str, Path]:
    """Create a validated draft release while leaving the active pointer unchanged."""

    repository = CurrentReleaseRepository(release_root, catalog_root)
    pointer = active_pointer or release_root / "active.json"
    base = repository.load_active(pointer)
    if base.manifest["status"] != "published" or not base.validation["product_ready"]:
        raise Phase6ReleaseError("The prior active release is not publishable input.")
    if "opportunity_filters" in base.manifest:
        raise Phase6ReleaseError("The active release already contains Opportunity Filters.")

    final_id = release_id or derive_next_release_id(release_root)
    draft = release_root / ".draft" / final_id
    published = release_root / final_id
    if draft.exists() or published.exists():
        raise FileExistsError(f"Release ID is already immutable or in use: {final_id}")

    candidate_checksums = _verify_candidate_checksums(staged_root)
    research_checksums = _verify_research_inputs(staged_root) if verify_research_inputs else {}
    catalog = _json(staged_root / "opportunity-filter-catalog.json")
    rows = [
        {**row, "release_id": final_id, "build_id": BUILD_ID, "generated_at": GENERATED_AT}
        for row in _jsonl(staged_root / "opportunity-filter-evidence.jsonl")
    ]
    coverage = {
        **_json(staged_root / "opportunity-filter-coverage-summary.json"),
        "release_id": final_id,
    }
    source_manifest = {
        **_json(staged_root / "opportunity-filter-source-manifest.json"),
        "build_id": BUILD_ID,
        "generated_at": GENERATED_AT,
    }
    threshold_policies = _json(staged_root / "opportunity-filter-threshold-policies.json")
    evidence_policy = _json(staged_root / "opportunity-filter-evidence-policy.json")
    countries = sorted(row.removeprefix("country:") for row in base.manifest["country_entity_ids"])

    validate_opportunity_filter_catalog(catalog)
    validate_opportunity_filter_evidence_matrix(catalog, rows, countries)
    validate_opportunity_filter_coverage_summary(coverage)
    validate_contract(
        source_manifest,
        "opportunity-filter-source-manifest",
        context="Phase 6I source manifest",
        schema_generation=3,
    )
    validate_contract(
        evidence_policy,
        "opportunity-filter-evidence-policy",
        context="Phase 6I evidence policy",
        schema_generation=3,
    )
    for policy in threshold_policies["policies"]:
        validate_contract(
            policy,
            "opportunity-filter-threshold-policy",
            context=policy["policy_version"],
            schema_generation=3,
        )
    _validate_accepted_product(catalog, rows, coverage)

    draft.mkdir(parents=True)
    for filename in PAYLOAD_FILES:
        shutil.copyfile(base.path / filename, draft / filename)
    _write_json(draft / "opportunity-filter-catalog.json", catalog)
    _write_jsonl(draft / "opportunity-filter-evidence.jsonl", rows)
    _write_json(draft / "opportunity-filter-source-manifest.json", source_manifest)
    _write_json(draft / "opportunity-filter-threshold-policies.json", threshold_policies)
    _write_json(draft / "opportunity-filter-evidence-policy.json", evidence_policy)
    _write_json(draft / "opportunity-filter-coverage-summary.json", coverage)

    filenames = [*PAYLOAD_FILES, *(value[0] for value in OPPORTUNITY_ARTIFACTS.values())]
    checksums = {filename: _checksum(draft / filename) for filename in filenames}
    manifest = {
        **base.manifest,
        "schema_version": OPPORTUNITY_RELEASE_SCHEMA_VERSION,
        "release_id": final_id,
        "status": "draft",
        "artifact_counts": {
            **base.manifest["artifact_counts"],
            "opportunity_filter_definitions": len(catalog["definitions"]),
            "opportunity_filter_evidence": len(rows),
        },
        "file_checksums": checksums,
        "release_checksum": _release_checksum(checksums),
        "opportunity_filters": {
            "binding_schema_version": "opportunity-filter-release-binding-1.0",
            "state_contract_version": "opportunity-filter-state-1.0",
            "artifacts": [
                {
                    "role": role,
                    "filename": filename,
                    "schema_version": schema_version,
                    "checksum": checksums[filename],
                }
                for role, (filename, schema_version) in OPPORTUNITY_ARTIFACTS.items()
            ],
        },
    }
    validate_contract(
        manifest,
        "release-manifest",
        context="Phase 6I release manifest",
        schema_generation=3,
    )
    validate_opportunity_filter_release_bundle(manifest, catalog, rows, countries)
    _write_json(draft / "manifest.json", manifest)
    repository.load(draft)

    report_root.mkdir(parents=True, exist_ok=True)
    _write_json(
        report_root / "build-manifest.json",
        {
            "schema_version": "phase6i-release-build-manifest-1.0",
            "build_id": BUILD_ID,
            "generated_at": GENERATED_AT,
            "release_id": final_id,
            "source_release_id": base.manifest["release_id"],
            "schema_release": OPPORTUNITY_RELEASE_SCHEMA_VERSION,
            "catalog_schema_version": base.manifest["catalog_schema_version"],
            "status": "draft",
            "active_pointer_changed": False,
            "candidate_input_checksums": candidate_checksums,
            "research_input_checksums": research_checksums,
            "release_file_checksums": {
                **checksums,
                "manifest.json": _checksum(draft / "manifest.json"),
            },
            "assertions": {
                "countries": len(countries),
                "ordering_criteria": len(base.manifest["criteria"]),
                "opportunity_filter_definitions": len(catalog["definitions"]),
                "opportunity_filter_evidence": len(rows),
                "base_payloads_byte_identical": all(
                    (base.path / filename).read_bytes() == (draft / filename).read_bytes()
                    for filename in PAYLOAD_FILES
                ),
                "expected_state_counts_match": True,
            },
        },
    )
    return final_id, draft


def publish_release(
    release_id: str,
    *,
    release_root: Path = DEFAULT_RELEASE_ROOT,
    catalog_root: Path = DEFAULT_CATALOG_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> Path:
    repository = CurrentReleaseRepository(release_root, catalog_root)
    draft = repository.load(release_root / ".draft" / release_id)
    if draft.manifest["status"] != "draft" or "opportunity_filters" not in draft.manifest:
        raise CurrentReleaseError("Only a validated Phase 6 draft can be published.")
    published = repository.publish(release_id)
    repository.load(published)
    report = _json(report_root / "build-manifest.json")
    report["release_file_checksums"]["manifest.json"] = _checksum(published / "manifest.json")
    report.update({"status": "published", "published_path": _portable_path(published)})
    _write_json(report_root / "build-manifest.json", report)
    return published


def activate_release(
    release_id: str,
    *,
    release_root: Path = DEFAULT_RELEASE_ROOT,
    catalog_root: Path = DEFAULT_CATALOG_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> Path:
    repository = CurrentReleaseRepository(release_root, catalog_root)
    published = repository.load(release_root / release_id)
    if "opportunity_filters" not in published.manifest:
        raise CurrentReleaseError("The target release has no Opportunity Filter binding.")
    pointer = repository.activate(release_id)
    active = repository.load_active(pointer)
    if active.manifest["release_id"] != release_id:
        raise CurrentReleaseError("Atomic activation did not select the requested release.")
    report = _json(report_root / "build-manifest.json")
    report.update({"status": "active", "active_pointer_changed": True})
    _write_json(report_root / "build-manifest.json", report)
    return pointer


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--release-id")
    publish = subparsers.add_parser("publish")
    publish.add_argument("release_id")
    activate = subparsers.add_parser("activate")
    activate.add_argument("release_id")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "build":
        release_id, path = build_release(release_id=args.release_id)
        print(f"release={release_id} status=draft path={path}")
    elif args.command == "publish":
        path = publish_release(args.release_id)
        print(f"release={args.release_id} status=published path={path}")
    else:
        path = activate_release(args.release_id)
        print(f"release={args.release_id} status=active pointer={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
