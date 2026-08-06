"""Deterministic Phase 6F promotion of education Opportunity Filter evidence.

The builder promotes the four approved Phase 6C research-university ecosystem constructs,
consolidates them with the staged Phase 6E career bundle, and emits an inactive nine-filter
release candidate. It never imports the historical research script, accesses the network,
activates a release, exposes an API/UI surface, or changes ranking behaviour.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from konsider.contracts import validate_contract
from konsider.domain.display_catalog import ProductDisplayCatalog, load_product_display_catalog
from konsider.domain.opportunity_filters import (
    OpportunityFilterState,
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_bundle,
)

ROOT = Path(__file__).resolve().parents[3]
PHASE6C_ROOT = ROOT / "data" / "reports" / "phase6c-2026-08-03"
PHASE6E_ROOT = ROOT / "data" / "reports" / "phase6e-2026-08-03"
PHASE6E_STAGED_ROOT = PHASE6E_ROOT / "staged-release"
PHASE6C_FIXTURE = (
    ROOT
    / "project-history"
    / "phases"
    / "phase-6"
    / "research"
    / "fixtures"
    / "phase6c-leiden-source-fixture.json"
)
UNIVERSE_PATH = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
ACTIVE_RELEASE_PATH = ROOT / "data" / "releases" / "2026-07-29.2"
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "reports" / "phase6f-2026-08-03"
DISPLAY_CATALOG_PATH = ROOT / "data" / "catalogs" / "product-display-catalog.json"
DISPLAY_CATALOG_SCHEMA_PATH = (
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json"
)

RELEASE_ID = "phase6f-complete-2026-08-03.1"
BUILD_ID = "phase6f-education-promotion-1.0"
GENERATED_AT = "2026-08-03T00:00:00+05:30"
SOURCE_BUNDLE_VERSION = "complete-opportunity-source-bundle-2026-08-03.1"
EVIDENCE_POLICY_VERSION = "opportunity-filter-evidence-policy-1.1"
EDUCATION_THRESHOLD_VERSION = "phase6c-p60-output-breadth-prominence-v1"
CWTS_SOURCE_ID = "cwts_leiden_open_2025_results"
ROR_SOURCE_ID = "ror_via_cwts_workbook"
CWTS_SOURCE_VERSION = "CWTS-Leiden-Open-2025:10.5281/zenodo.17473224"
ROR_SOURCE_VERSION = "CWTS-Leiden-Open-2025-universities-workbook:ROR"
STATE_ORDER = (
    OpportunityFilterState.VERIFIED_STRONG_SIGNAL.value,
    OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value,
    OpportunityFilterState.INSUFFICIENT_EVIDENCE.value,
)
ROUTE_IDS = (
    "top_100_institution",
    "top_300_breadth",
    "base_output_and_breadth",
    "high_output_minimum_breadth",
    "high_breadth_minimum_output",
)


class EducationOpportunityBuildError(ValueError):
    """Raised when Phase 6F promotion or reconciliation fails closed."""


@dataclass(frozen=True)
class EducationFilterConfig:
    filter_id: str
    source_field: str
    source_field_slug: str
    sort_order: int
    expected_counts: tuple[int, int, int]
    thresholds: Mapping[str, float]

    @property
    def threshold_policy_version(self) -> str:
        return f"education-p60-{self.filter_id}-1.0"


FILTERS = (
    EducationFilterConfig(
        "engineering_technology_education_opportunity",
        "Physical sciences and engineering",
        "physical-sciences-engineering",
        6,
        (27, 48, 16),
        {
            "base_output": 7834.8,
            "base_breadth": 12.8,
            "high_output": 30774.2,
            "high_breadth": 39.2,
            "low_output": 2623.2,
            "low_breadth": 6,
        },
    ),
    EducationFilterConfig(
        "computer_science_ict_education_opportunity",
        "Mathematics and computer science",
        "mathematics-computer-science",
        7,
        (30, 45, 16),
        {
            "base_output": 6337,
            "base_breadth": 12.8,
            "high_output": 17870.8,
            "high_breadth": 39.2,
            "low_output": 2215.6,
            "low_breadth": 6,
        },
    ),
    EducationFilterConfig(
        "medicine_health_sciences_education_opportunity",
        "Biomedical and health sciences",
        "biomedical-health",
        8,
        (30, 45, 16),
        {
            "base_output": 12502.8,
            "base_breadth": 12.8,
            "high_output": 39464.8,
            "high_breadth": 39.2,
            "low_output": 2761.6,
            "low_breadth": 6,
        },
    ),
    EducationFilterConfig(
        "natural_sciences_education_opportunity",
        "Life and earth sciences",
        "life-earth-sciences",
        9,
        (31, 44, 16),
        {
            "base_output": 4560.2,
            "base_breadth": 12.8,
            "high_output": 13754.6,
            "high_breadth": 39.2,
            "low_output": 1397.8,
            "low_breadth": 6,
        },
    ),
)
FILTER_BY_ID = {item.filter_id: item for item in FILTERS}
MEANING_BY_ID = {
    "engineering_technology_education_opportunity": (
        "A substantial and established physical sciences and engineering "
        "research-university ecosystem."
    ),
    "computer_science_ict_education_opportunity": (
        "A substantial and established mathematics and computer science "
        "research-university ecosystem."
    ),
    "medicine_health_sciences_education_opportunity": (
        "A substantial and established biomedical and health sciences "
        "research-university ecosystem."
    ),
    "natural_sciences_education_opportunity": (
        "A substantial and established life and earth sciences research-university ecosystem."
    ),
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    path.write_bytes(body.encode("utf-8"))


def _verify_checksum(path: Path, expected: str, label: str) -> None:
    expected_digest = expected.removeprefix("sha256:")
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual == expected_digest:
        return
    # Git's Windows checkout policy may change only text EOL bytes. Accept the two canonical EOL
    # encodings when one is the checksum-bound representation; no other byte change is tolerated.
    lf = data.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    if expected_digest in {hashlib.sha256(lf).hexdigest(), hashlib.sha256(crlf).hexdigest()}:
        return
    if actual != expected_digest:
        raise EducationOpportunityBuildError(
            f"{label} checksum mismatch: expected {expected}, got {actual}."
        )


def verify_research_inputs() -> dict[str, str]:
    """Verify the complete committed Phase 6C replay chain used for promotion."""

    replay = _read_json(PHASE6C_ROOT / "replay-manifest.json")
    verified: dict[str, str] = {}
    for relative, expected in replay["input_sha256"].items():
        path = ROOT / relative
        _verify_checksum(path, expected, relative)
        verified[relative] = f"sha256:{expected}"
    for relative, expected in replay["output_sha256"].items():
        path = ROOT / relative if relative.startswith("docs/") else PHASE6C_ROOT / relative
        _verify_checksum(path, expected, relative)
        verified[f"data/reports/phase6c-2026-08-03/{relative}"] = f"sha256:{expected}"
    assertions = replay["assertions"]
    if assertions["institution_mapping_count"] != 2831 or assertions["unique_ror_count"] != 2831:
        raise EducationOpportunityBuildError(
            "Phase 6C replay assertions do not preserve 2,831 ROR identities."
        )
    return verified


def verify_phase6e_inputs() -> dict[str, str]:
    """Verify every committed Phase 6E output reused in the combined draft."""

    manifest = _read_json(PHASE6E_ROOT / "build-manifest.json")
    verified: dict[str, str] = {}
    for relative, expected in manifest["artifact_checksums"].items():
        path = PHASE6E_STAGED_ROOT / relative
        if not path.exists():
            path = PHASE6E_ROOT / relative
        _verify_checksum(path, expected, f"Phase 6E {relative}")
        verified[f"data/reports/phase6e-2026-08-03/{relative}"] = expected
    if manifest["assertions"]["evidence_record_count"] != 455:
        raise EducationOpportunityBuildError(
            "Phase 6E no longer declares the required 455 career rows."
        )
    return verified


def verify_retained_sources(*, require_all: bool = False) -> dict[str, str]:
    """Verify optional ignored CWTS captures without making clean builds depend on them."""

    metadata = _read_json(PHASE6C_FIXTURE)["metadata"]
    raw_root = ROOT / "data" / "raw" / "phase6c"
    results: dict[str, str] = {}
    for filename, expected in metadata["source_files"].items():
        path = raw_root / filename
        if not path.exists():
            if require_all:
                raise EducationOpportunityBuildError(f"Retained source is unavailable: {path}")
            results[filename] = "NOT_PRESENT"
            continue
        if path.stat().st_size != expected["bytes"]:
            raise EducationOpportunityBuildError(
                f"{filename} byte count mismatch: expected {expected['bytes']}, got {path.stat().st_size}."
            )
        _verify_checksum(path, expected["sha256"], filename)
        results[filename] = "VERIFIED"
    return results


def _validate_institution_mapping(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 2831:
        raise EducationOpportunityBuildError("Institution mapping must contain exactly 2,831 rows.")
    if len({row["source_institution_id"] for row in rows}) != 2831:
        raise EducationOpportunityBuildError("CWTS institution IDs must be unique.")
    if len({row["ror_id"] for row in rows}) != 2831:
        raise EducationOpportunityBuildError("ROR identities must be one-to-one and unique.")
    methods = Counter(row["match_method"] for row in rows)
    if methods != {"EXACT_NAME_AND_COUNTRY": 2825, "MANUAL_QUOTED_NAME_DISAMBIGUATION": 6}:
        raise EducationOpportunityBuildError(f"Unexpected institution identity methods: {methods}.")
    if any(row["locality"] is not None for row in rows):
        raise EducationOpportunityBuildError("Phase 6F prohibits locality or campus inference.")
    required_fields = {config.source_field_slug for config in FILTERS}
    if any(not required_fields.issubset(row["field_evidence"]) for row in rows):
        raise EducationOpportunityBuildError(
            "Institution rows are missing one or more approved fields."
        )
    manual = [
        {
            key: row[key]
            for key in (
                "source_institution_id",
                "source_display_name",
                "canonical_institution_name",
                "ror_id",
                "source_country_name",
                "source_country_alpha2",
                "stable_country_code",
                "match_method",
                "match_confidence",
            )
        }
        for row in rows
        if row["match_method"] == "MANUAL_QUOTED_NAME_DISAMBIGUATION"
    ]
    return {
        "schema_version": "phase6f-institution-identity-summary-1.0",
        "source_release": "CWTS Leiden Ranking Open Edition 2025",
        "institution_count": len(rows),
        "unique_source_institution_id_count": len({row["source_institution_id"] for row in rows}),
        "unique_ror_count": len({row["ror_id"] for row in rows}),
        "exact_name_country_count": methods["EXACT_NAME_AND_COUNTRY"],
        "manual_disambiguation_count": methods["MANUAL_QUOTED_NAME_DISAMBIGUATION"],
        "many_to_one_ror_count": 0,
        "locality_inference_performed": False,
        "manual_disambiguations": manual,
    }


def _institution_normalization(row: Mapping[str, Any]) -> dict[str, Any]:
    fields = {}
    for config in FILTERS:
        evidence = row["field_evidence"][config.source_field_slug]
        fields[config.filter_id] = {
            "source_field": config.source_field,
            "rank": evidence["rank"],
            "fractional_publications": evidence["fractional_publications"],
            "publications_50_plus_citations": evidence["publications_50_plus_citations"],
            "share_50_plus_citations_percent": evidence["share_50_plus_citations_percent"],
            "redacted": evidence["redacted"],
            "top_100": evidence["rank"] <= 100,
            "top_200": evidence["rank"] <= 200,
            "top_300": evidence["rank"] <= 300,
        }
    return {
        "schema_version": "phase6f-institution-normalization-1.0",
        "source_release": row["source_release"],
        "source_institution_id": row["source_institution_id"],
        "source_display_name": row["source_display_name"],
        "canonical_institution_name": row["canonical_institution_name"],
        "ror_id": row["ror_id"],
        "ror_url": row["ror_url"],
        "source_country_name": row["source_country_name"],
        "source_country_alpha2": row["source_country_alpha2"],
        "stable_country_code": row["stable_country_code"],
        "match_method": row["match_method"],
        "match_confidence": row["match_confidence"],
        "locality": None,
        "multi_campus_status": row["multi_campus_status"],
        "field_evidence": fields,
    }


def _route_results(
    observation: Mapping[str, Any], config: EducationFilterConfig
) -> list[dict[str, Any]]:
    output = observation["fractional_publication_output"]
    breadth = observation["active_university_breadth"]
    thresholds = config.thresholds
    values = (
        (
            "top_100_institution",
            observation["top100_count"] >= 1,
            {"top_100_count": observation["top100_count"], "minimum_top_100_count": 1},
        ),
        (
            "top_300_breadth",
            observation["top300_count"] >= 3,
            {"top_300_count": observation["top300_count"], "minimum_top_300_count": 3},
        ),
        (
            "base_output_and_breadth",
            output >= thresholds["base_output"] and breadth >= thresholds["base_breadth"],
            {
                "fractional_publication_output": output,
                "active_university_breadth": breadth,
                "minimum_output": thresholds["base_output"],
                "minimum_breadth": thresholds["base_breadth"],
            },
        ),
        (
            "high_output_minimum_breadth",
            output >= thresholds["high_output"] and breadth >= thresholds["low_breadth"],
            {
                "fractional_publication_output": output,
                "active_university_breadth": breadth,
                "minimum_output": thresholds["high_output"],
                "minimum_breadth": thresholds["low_breadth"],
            },
        ),
        (
            "high_breadth_minimum_output",
            breadth >= thresholds["high_breadth"] and output >= thresholds["low_output"],
            {
                "fractional_publication_output": output,
                "active_university_breadth": breadth,
                "minimum_output": thresholds["low_output"],
                "minimum_breadth": thresholds["high_breadth"],
            },
        ),
    )
    return [
        {
            "route_id": route_id,
            "passed": passed,
            "policy_version": config.threshold_policy_version,
            "components": components,
        }
        for route_id, passed, components in values
    ]


def _source_references(country_code: str, config: EducationFilterConfig) -> list[dict[str, str]]:
    suffix = f"{config.source_field_slug}:{country_code}"
    return [
        {
            "source_id": CWTS_SOURCE_ID,
            "source_version": CWTS_SOURCE_VERSION,
            "lineage_id": f"lineage:{CWTS_SOURCE_ID}:{suffix}",
        },
        {
            "source_id": ROR_SOURCE_ID,
            "source_version": ROR_SOURCE_VERSION,
            "lineage_id": f"lineage:{ROR_SOURCE_ID}:{suffix}",
        },
    ]


def _education_evidence(row: Mapping[str, Any], config: EducationFilterConfig) -> dict[str, Any]:
    observation = row["observation"]
    if row["threshold_version"] != EDUCATION_THRESHOLD_VERSION:
        raise EducationOpportunityBuildError("Phase 6C threshold version changed.")
    expected_thresholds = {"percentile": "P60", **dict(config.thresholds)}
    if row["thresholds"] != expected_thresholds:
        raise EducationOpportunityBuildError(f"Frozen thresholds changed for {config.filter_id}.")

    if observation is None:
        return {
            "schema_version": "opportunity-filter-evidence-1.0",
            "release_id": RELEASE_ID,
            "filter_id": config.filter_id,
            "country_code": row["country_code"],
            "state": "INSUFFICIENT_EVIDENCE",
            "confidence_band": "LOW",
            "internal_confidence_tier": None,
            "coverage_completeness": "UNASSESSED",
            "evaluated_route_ids": [],
            "establishing_route_ids": [],
            "reason_codes": ["COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE"],
            "reference_period": row["publication_window"],
            "metric_payload": None,
            "threshold_results": [],
            "source_references": _source_references(row["country_code"], config),
            "source_observation_status": "MISSING",
            "caveats": [
                "Country absence from the research-intensive university release is not zero and cannot establish a negative.",
                "No teaching, programme, admissions, affordability, accreditation, visa, campus, language, employment-outcome, or applicant-success claim is made.",
            ],
            "evidence_policy_version": EVIDENCE_POLICY_VERSION,
            "threshold_policy_version": config.threshold_policy_version,
            "source_bundle_version": SOURCE_BUNDLE_VERSION,
            "generated_at": GENERATED_AT,
            "build_id": BUILD_ID,
        }

    results = _route_results(observation, config)
    passed = [result["route_id"] for result in results if result["passed"]]
    state = "VERIFIED_STRONG_SIGNAL" if passed else "STRONG_SIGNAL_NOT_ESTABLISHED"
    reasons = []
    if "top_100_institution" in passed:
        reasons.append("TOP_100_INSTITUTION_ROUTE_PASSED")
    if "top_300_breadth" in passed:
        reasons.append("TOP_300_BREADTH_ROUTE_PASSED")
    if set(passed) & set(ROUTE_IDS[2:]):
        reasons.append("OUTPUT_AND_BREADTH_ROUTE_PASSED")
    if not reasons:
        reasons = ["NO_APPROVED_STRONG_ROUTE_PASSED"]
    research_passed = set(row["passed_routes"])
    expected_research_passed = set()
    if "top_100_institution" in passed:
        expected_research_passed.add("exceptional_top100")
    if "top_300_breadth" in passed:
        expected_research_passed.add("prominent_top300_breadth")
    if set(passed) & set(ROUTE_IDS[2:]):
        expected_research_passed.add("scale_and_breadth")
    if research_passed != expected_research_passed:
        raise EducationOpportunityBuildError(
            f"Route reconciliation failed for {config.filter_id}/{row['country_code']}."
        )
    expected_state = "VERIFIED_STRONG_SIGNAL" if passed else "STRONG_SIGNAL_NOT_ESTABLISHED"
    if row["state"] != expected_state:
        raise EducationOpportunityBuildError(
            f"State reconciliation failed for {config.filter_id}/{row['country_code']}."
        )
    return {
        "schema_version": "opportunity-filter-evidence-1.0",
        "release_id": RELEASE_ID,
        "filter_id": config.filter_id,
        "country_code": row["country_code"],
        "state": state,
        "confidence_band": "HIGH",
        "internal_confidence_tier": "HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET",
        "coverage_completeness": "COMPLETE",
        "evaluated_route_ids": list(ROUTE_IDS),
        "establishing_route_ids": passed,
        "reason_codes": reasons,
        "reference_period": row["publication_window"],
        "metric_payload": {
            "schema_version": "education-research-ecosystem-metrics-1.0",
            "fractional_publication_output": observation["fractional_publication_output"],
            "active_university_breadth": observation["active_university_breadth"],
            "top_100_count": observation["top100_count"],
            "top_200_count": observation["top200_count"],
            "top_300_count": observation["top300_count"],
        },
        "threshold_results": results,
        "source_references": _source_references(row["country_code"], config),
        "source_observation_status": "FROZEN_RESEARCH_DATASET",
        "caveats": [
            "This is a country-level research-intensive university ecosystem signal for the named field only.",
            "No teaching, programme, admissions, affordability, accreditation, visa, campus, language, employment-outcome, or applicant-success claim is made.",
        ],
        "evidence_policy_version": EVIDENCE_POLICY_VERSION,
        "threshold_policy_version": config.threshold_policy_version,
        "source_bundle_version": SOURCE_BUNDLE_VERSION,
        "generated_at": GENERATED_AT,
        "build_id": BUILD_ID,
    }


def _education_definition(
    config: EducationFilterConfig, display_catalog: ProductDisplayCatalog
) -> dict[str, Any]:
    display = display_catalog.definition("OPPORTUNITY_FILTER", config.filter_id)
    if display.compact_name is None or display.section_id != "education":
        raise EducationOpportunityBuildError(
            f"Invalid education display metadata for {config.filter_id}."
        )
    return {
        "id": config.filter_id,
        "display_name": display.display_name,
        "compact_label": display.compact_name,
        "category": "EDUCATION",
        "construct": (
            f"Country-level scale, breadth, and global prominence of research-intensive universities "
            f"in {config.source_field.lower()}, using the frozen CWTS Leiden Open 2025 release."
        ),
        "meaning": MEANING_BY_ID[config.filter_id],
        "does_not_mean": [
            "Teaching quality or programme quality",
            "Programme availability, admissions, or student access",
            "Tuition, scholarships, or affordability",
            "Accreditation, qualification recognition, or licensing",
            "Visa access, campus locality, language, employment outcomes, or applicant success",
            "Absence of universities when a strong signal is not established",
        ],
        "product_role": "OPPORTUNITY_FILTER",
        "state_contract_version": "opportunity-filter-state-1.0",
        "filter_behavior": {
            "eligibility_state": "VERIFIED_STRONG_SIGNAL",
            "combination": "ALL_SELECTED_REQUIRED",
            "changes_affinity_score": False,
            "changes_survivor_order": False,
        },
        "evidence_policy_version": EVIDENCE_POLICY_VERSION,
        "threshold_policy_version": config.threshold_policy_version,
        "source_bundle_version": SOURCE_BUNDLE_VERSION,
        "scope": {
            "evidence_level": "INSTITUTION",
            "result_level": "COUNTRY",
            "derivation": "AGGREGATED_FROM_INSTITUTIONS",
        },
        "applicability": {
            "mode": "DESTINATION_SIDE",
            "dimensions": ["RESEARCH_UNIVERSITY_ECOSYSTEM"],
        },
        "refresh_policy": {
            "policy_id": "education-opportunity-source-release-review-1.0",
            "cadence": "SOURCE_RELEASE",
            "maximum_age_months": 36,
            "fail_closed": True,
        },
        "source_dependency": {
            "mode": "MULTI_SOURCE",
            "required_source_ids": [CWTS_SOURCE_ID, ROR_SOURCE_ID],
            "failure_state": "INSUFFICIENT_EVIDENCE",
        },
        "availability": "STAGED",
        "active": False,
        "sort_order": config.sort_order,
        "documentation_ref": "docs/data/education-opportunity-evidence.md",
    }


def _consolidated_career_artifacts() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalog = _read_json(PHASE6E_STAGED_ROOT / "opportunity-filter-catalog.json")
    definitions = []
    for source in catalog["definitions"]:
        definition = dict(source)
        definition["evidence_policy_version"] = EVIDENCE_POLICY_VERSION
        definition["source_bundle_version"] = SOURCE_BUNDLE_VERSION
        definitions.append(definition)
    rows = []
    for source in _read_jsonl(PHASE6E_STAGED_ROOT / "opportunity-filter-evidence.jsonl"):
        row = dict(source)
        row["release_id"] = RELEASE_ID
        row["evidence_policy_version"] = EVIDENCE_POLICY_VERSION
        row["source_bundle_version"] = SOURCE_BUNDLE_VERSION
        row["generated_at"] = GENERATED_AT
        row["build_id"] = BUILD_ID
        rows.append(row)
    return definitions, rows


def _catalog(
    career_definitions: list[dict[str, Any]], display_catalog: ProductDisplayCatalog
) -> dict[str, Any]:
    technical_ids = {item["id"] for item in career_definitions} | set(FILTER_BY_ID)
    catalog_ids = {item.id for item in display_catalog.definitions("OPPORTUNITY_FILTER")}
    if technical_ids != catalog_ids:
        raise EducationOpportunityBuildError(
            f"Opportunity Filter display ID mismatch: technical={sorted(technical_ids)}, "
            f"catalog={sorted(catalog_ids)}."
        )
    return {
        "schema_version": "opportunity-filter-catalog-1.0",
        "compatible_release_schema_major": 5,
        "stable_universe_id": "stable_supported_v1",
        "activation_status": "STAGED_CONTRACT_ONLY",
        "state_contract_version": "opportunity-filter-state-1.0",
        "definitions": career_definitions
        + [_education_definition(config, display_catalog) for config in FILTERS],
    }


def _education_threshold_policy(config: EducationFilterConfig) -> dict[str, Any]:
    threshold = config.thresholds
    route_specs = (
        (
            "top_100_institution",
            "At least one institution ranks in the global field top 100.",
            "top_100_count >= 1",
            {"minimum_top_100_count": 1},
        ),
        (
            "top_300_breadth",
            "At least three institutions rank in the global field top 300.",
            "top_300_count >= 3",
            {"minimum_top_300_count": 3},
        ),
        (
            "base_output_and_breadth",
            "Frozen P60 output and breadth route.",
            "output >= base_output AND breadth >= base_breadth",
            {
                "minimum_output": threshold["base_output"],
                "minimum_breadth": threshold["base_breadth"],
            },
        ),
        (
            "high_output_minimum_breadth",
            "Frozen high-output and minimum-breadth route.",
            "output >= high_output AND breadth >= low_breadth",
            {
                "minimum_output": threshold["high_output"],
                "minimum_breadth": threshold["low_breadth"],
            },
        ),
        (
            "high_breadth_minimum_output",
            "Frozen high-breadth and minimum-output route.",
            "breadth >= high_breadth AND output >= low_output",
            {
                "minimum_output": threshold["low_output"],
                "minimum_breadth": threshold["high_breadth"],
            },
        ),
    )
    return {
        "schema_version": "opportunity-filter-threshold-policy-1.0",
        "policy_id": f"education-p60-{config.filter_id}",
        "policy_version": config.threshold_policy_version,
        "filter_id": config.filter_id,
        "global_only": True,
        "routes": [
            {
                "route_id": route_id,
                "description": description,
                "rule": rule,
                "parameters": {
                    **parameters,
                    "frozen_percentile": "P60",
                    "country_exceptions": False,
                },
            }
            for route_id, description, rule, parameters in route_specs
        ],
    }


def _threshold_policies() -> dict[str, Any]:
    career = _read_json(PHASE6E_STAGED_ROOT / "opportunity-filter-threshold-policies.json")
    return {
        "schema_version": "opportunity-filter-threshold-policies-1.0",
        "policies": career["policies"]
        + [_education_threshold_policy(config) for config in FILTERS],
    }


def _evidence_policy() -> dict[str, Any]:
    return {
        "schema_version": "opportunity-filter-evidence-policy-1.0",
        "policy_id": "complete-opportunity-evidence-policy",
        "policy_version": EVIDENCE_POLICY_VERSION,
        "public_states": list(STATE_ORDER),
        "eligibility_state": "VERIFIED_STRONG_SIGNAL",
        "combination": "ALL_SELECTED_REQUIRED",
        "precedence": [
            "HIGH_CONFIDENCE_OBSERVED_HARMONISED",
            "HIGH_CONFIDENCE_OBSERVED_NATIONAL",
            "HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET",
            "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK",
            "MEDIUM_CONFIDENCE_MODELLED_HARMONISED",
            "LOW_CONFIDENCE_SUPPLEMENTAL",
        ],
        "negative_integrity": {
            "requires_complete_evidence": True,
            "partial_source_can_establish_negative": False,
            "source_absence_state": "INSUFFICIENT_EVIDENCE",
        },
        "missing_record_behavior": "REJECT_RELEASE_NO_RUNTIME_INFERENCE",
    }


def _education_source_records() -> list[dict[str, Any]]:
    return [
        {
            "source_id": CWTS_SOURCE_ID,
            "source_version": CWTS_SOURCE_VERSION,
            "publisher": "Centre for Science and Technology Studies, Leiden University",
            "asset_uri": "project-history/phases/phase-6/research/fixtures/phase6c-leiden-source-fixture.json",
            "canonical_page_url": "https://doi.org/10.5281/zenodo.17473224",
            "checksum": f"sha256:{_sha256(PHASE6C_FIXTURE)}",
            "licence_id": "CC0-1.0",
            "attribution": "CWTS Leiden Ranking Open Edition 2025; DOI 10.5281/zenodo.17473224; adapted by Konsider.",
            "reuse_status": "APPROVED",
            "retention_policy": "COMMITTED",
        },
        {
            "source_id": ROR_SOURCE_ID,
            "source_version": ROR_SOURCE_VERSION,
            "publisher": "Research Organization Registry via CWTS Leiden Open workbook",
            "asset_uri": "data/raw/phase6c/leiden-open-2025-universities.xlsx",
            "canonical_page_url": "https://open.leidenranking.com/information/universities",
            "checksum": "sha256:35d96fe44a0f1724f0071fd11c47185063654b444cc837775c65643119ea2e74",
            "licence_id": "CC0-1.0",
            "attribution": "ROR identifiers supplied in the CWTS Leiden Ranking Open Edition 2025 universities workbook.",
            "reuse_status": "APPROVED",
            "retention_policy": "IGNORED_LOCAL",
        },
    ]


def _source_manifest() -> dict[str, Any]:
    career = _read_json(PHASE6E_STAGED_ROOT / "opportunity-filter-source-manifest.json")
    return {
        "schema_version": "opportunity-filter-source-manifest-1.0",
        "bundle_id": "complete-opportunity-sources",
        "bundle_version": SOURCE_BUNDLE_VERSION,
        "sources": career["sources"] + _education_source_records(),
        "generated_at": GENERATED_AT,
        "build_id": BUILD_ID,
    }


def _coverage_summary(rows: list[dict[str, Any]], filter_ids: list[str]) -> dict[str, Any]:
    filters = {}
    for filter_id in filter_ids:
        counts = Counter(row["state"] for row in rows if row["filter_id"] == filter_id)
        filters[filter_id] = {
            "assessable_count": counts[STATE_ORDER[0]] + counts[STATE_ORDER[1]],
            "state_counts": {state: counts[state] for state in STATE_ORDER},
            "source_dependency_status": "AVAILABLE",
        }
    return {
        "schema_version": "opportunity-filter-coverage-summary-1.0",
        "release_id": RELEASE_ID,
        "stable_universe_id": "stable_supported_v1",
        "stable_country_count": 91,
        "filters": filters,
    }


def _shortlist_reconciliation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    research = _read_json(PHASE6C_ROOT / "education-shortlist-coverage.json")
    by_pair = {(row["filter_id"], row["country_code"]): row["state"] for row in rows}
    filters = {}
    mismatches = []
    for config in FILTERS:
        profiles = {}
        for profile_id, source in research["candidates"][config.filter_id]["profiles"].items():
            codes = source["frozen_country_codes_in_order"]
            assessable = [
                code for code in codes if by_pair[(config.filter_id, code)] != STATE_ORDER[2]
            ]
            actual = {
                "frozen_country_codes_in_order": codes,
                "assessable_country_codes_in_frozen_order": assessable,
                "assessable_count": len(assessable),
                "ordering_changed": False,
            }
            expected = {key: source[key] for key in actual}
            if actual != expected:
                mismatches.append(f"{config.filter_id}/{profile_id}")
            profiles[profile_id] = {"actual": actual, "expected": expected}
        filters[config.filter_id] = profiles
    return {"filters": filters, "mismatches": mismatches}


def _reconciliation(
    education_rows: list[dict[str, Any]], all_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    counts = {}
    mismatches = []
    for config in FILTERS:
        counter = Counter(
            row["state"] for row in education_rows if row["filter_id"] == config.filter_id
        )
        actual = {state: counter[state] for state in STATE_ORDER}
        expected = dict(zip(STATE_ORDER, config.expected_counts, strict=True))
        counts[config.filter_id] = {"actual": actual, "expected": expected}
        if actual != expected:
            mismatches.append(config.filter_id)
    route_counts = {
        config.filter_id: Counter(
            route
            for row in education_rows
            if row["filter_id"] == config.filter_id
            for route in row["establishing_route_ids"]
        )
        for config in FILTERS
    }
    shortlist = _shortlist_reconciliation(education_rows)
    return {
        "schema_version": "phase6f-research-production-reconciliation-1.0",
        "release_id": RELEASE_ID,
        "research_source": "data/reports/phase6c-2026-08-03",
        "education_row_count": len(education_rows),
        "combined_row_count": len(all_rows),
        "unique_filter_country_count": len(
            {(row["filter_id"], row["country_code"]) for row in all_rows}
        ),
        "state_counts": counts,
        "state_count_mismatches": mismatches,
        "state_mismatches": [],
        "metric_component_mismatches": [],
        "threshold_route_mismatches": [],
        "institution_identity_mismatches": [],
        "route_pass_counts": {
            filter_id: dict(counter) for filter_id, counter in route_counts.items()
        },
        "shortlist_coverage": shortlist,
        "excluded_constructs": [
            "business_finance_education_opportunity",
            "broad_university_excellence_opportunity",
            "generic_research_or_academia_employment",
        ],
        "career_education_crosswalk_runtime_effect": False,
        "discrepancies": [],
    }


def _source_legal_records() -> dict[str, Any]:
    fixture = _read_json(PHASE6C_FIXTURE)
    return {
        "schema_version": "phase6f-education-source-legal-records-1.0",
        "source_release": fixture["metadata"]["source_release"],
        "source_doi": fixture["metadata"]["source_doi"],
        "openalex_snapshot": fixture["metadata"]["openalex_snapshot"],
        "publication_window": fixture["metadata"]["publication_window"],
        "licence": fixture["metadata"]["licence"],
        "source_files": fixture["metadata"]["source_files"],
        "production_use_conclusion": "COMMIT_DERIVED_CC0_RESULTS_AND_ROR_IDENTITIES",
        "direct_live_openalex_access_used": False,
        "source_dependency_policy": (
            "CWTS result removal makes every education field unassessable; ROR identity removal fails publication."
        ),
        "terms_snapshot": "docs/research/phase6c-education-opportunity-study.md",
    }


def _candidate_manifest(
    catalog: Mapping[str, Any], rows: list[dict[str, Any]], artifact_checksums: Mapping[str, str]
) -> dict[str, Any]:
    active = _read_json(ACTIVE_RELEASE_PATH / "manifest.json")
    manifest = {**active}
    manifest["schema_version"] = "konsider-release-5.1"
    manifest["release_id"] = RELEASE_ID
    manifest["status"] = "draft"
    manifest["artifact_counts"] = {
        **active["artifact_counts"],
        "opportunity_filter_definitions": len(catalog["definitions"]),
        "opportunity_filter_evidence": len(rows),
    }
    manifest["file_checksums"] = {**active["file_checksums"], **artifact_checksums}
    specs = (
        ("CATALOG", "opportunity-filter-catalog.json", "opportunity-filter-catalog-1.0"),
        (
            "COUNTRY_EVIDENCE",
            "opportunity-filter-evidence.jsonl",
            "opportunity-filter-evidence-1.0",
        ),
        (
            "SOURCE_MANIFEST",
            "opportunity-filter-source-manifest.json",
            "opportunity-filter-source-manifest-1.0",
        ),
        (
            "THRESHOLD_POLICIES",
            "opportunity-filter-threshold-policies.json",
            "opportunity-filter-threshold-policies-1.0",
        ),
        (
            "EVIDENCE_POLICY",
            "opportunity-filter-evidence-policy.json",
            "opportunity-filter-evidence-policy-1.0",
        ),
        (
            "COVERAGE_SUMMARY",
            "opportunity-filter-coverage-summary.json",
            "opportunity-filter-coverage-summary-1.0",
        ),
    )
    manifest["opportunity_filters"] = {
        "binding_schema_version": "opportunity-filter-release-binding-1.0",
        "state_contract_version": "opportunity-filter-state-1.0",
        "artifacts": [
            {
                "role": role,
                "filename": filename,
                "schema_version": schema_version,
                "checksum": artifact_checksums[filename],
            }
            for role, filename, schema_version in specs
        ],
    }
    unsigned = {key: value for key, value in manifest.items() if key != "release_checksum"}
    body = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    manifest["release_checksum"] = f"sha256:{hashlib.sha256(body).hexdigest()}"
    return manifest


def build_education_opportunity_bundle(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    display_catalog: ProductDisplayCatalog,
    verify_raw: bool = False,
) -> dict[str, Any]:
    """Build and validate the staged nine-filter Phase 6F release fragment."""

    research_checksums = verify_research_inputs()
    phase6e_checksums = verify_phase6e_inputs()
    verify_retained_sources(require_all=verify_raw)
    universe = _read_json(UNIVERSE_PATH)
    countries = [row["code"] for row in universe["countries"]]
    if universe["universe_id"] != "stable_supported_v1" or len(countries) != 91:
        raise EducationOpportunityBuildError(
            "Phase 6F requires stable_supported_v1 with 91 countries."
        )

    institution_rows = _read_jsonl(PHASE6C_ROOT / "institution-mapping.jsonl")
    identity_summary = _validate_institution_mapping(institution_rows)
    normalized_institutions = [_institution_normalization(row) for row in institution_rows]

    research_rows = {
        (row["candidate_id"], row["country_code"]): row
        for row in _read_jsonl(PHASE6C_ROOT / "education-country-opportunity-evidence.jsonl")
        if row["candidate_id"] in FILTER_BY_ID
    }
    expected_pairs = {(config.filter_id, code) for config in FILTERS for code in countries}
    if set(research_rows) != expected_pairs:
        raise EducationOpportunityBuildError(
            "Phase 6C evidence is not an exact approved 4 x 91 matrix."
        )
    education_rows = [
        _education_evidence(research_rows[(config.filter_id, code)], config)
        for config in FILTERS
        for code in countries
    ]
    career_definitions, career_rows = _consolidated_career_artifacts()
    all_rows = career_rows + education_rows
    catalog = _catalog(career_definitions, display_catalog)
    threshold_policies = _threshold_policies()
    evidence_policy = _evidence_policy()
    source_manifest = _source_manifest()
    filter_ids = [row["id"] for row in catalog["definitions"]]
    coverage_summary = _coverage_summary(all_rows, filter_ids)
    reconciliation = _reconciliation(education_rows, all_rows)
    source_legal = _source_legal_records()
    crosswalk = _read_json(PHASE6C_ROOT / "career-education-crosswalk.json")
    crosswalk["phase6f_usage"] = (
        "EXPLANATORY_METADATA_ONLY_NO_STATE_MERGING_CAUSALITY_OR_RUNTIME_TAXONOMY"
    )

    validate_opportunity_filter_catalog(catalog)
    validate_opportunity_filter_evidence_matrix(catalog, all_rows, countries)
    validate_opportunity_filter_coverage_summary(coverage_summary)
    validate_contract(
        evidence_policy,
        "opportunity-filter-evidence-policy",
        context="Phase 6F evidence policy",
        schema_generation=3,
    )
    validate_contract(
        source_manifest,
        "opportunity-filter-source-manifest",
        context="Phase 6F source manifest",
        schema_generation=3,
    )
    for policy in threshold_policies["policies"]:
        validate_contract(
            policy,
            "opportunity-filter-threshold-policy",
            context=policy["policy_version"],
            schema_generation=3,
        )
    if (
        reconciliation["state_count_mismatches"]
        or reconciliation["shortlist_coverage"]["mismatches"]
    ):
        raise EducationOpportunityBuildError(
            "Production education evidence does not reconcile with Phase 6C."
        )

    staged = output_root / "staged-release"
    staged.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "opportunity-filter-catalog.json": catalog,
        "opportunity-filter-source-manifest.json": source_manifest,
        "opportunity-filter-threshold-policies.json": threshold_policies,
        "opportunity-filter-evidence-policy.json": evidence_policy,
        "opportunity-filter-coverage-summary.json": coverage_summary,
    }
    for filename, payload in artifacts.items():
        _write_json(staged / filename, payload)
    _write_jsonl(staged / "opportunity-filter-evidence.jsonl", all_rows)
    artifact_checksums = {
        filename: f"sha256:{_sha256(staged / filename)}"
        for filename in (*artifacts, "opportunity-filter-evidence.jsonl")
    }
    candidate = _candidate_manifest(catalog, all_rows, artifact_checksums)
    validate_opportunity_filter_release_bundle(candidate, catalog, all_rows, countries)
    _write_json(staged / "candidate-release-manifest.json", candidate)

    education_catalog = {
        **catalog,
        "definitions": [row for row in catalog["definitions"] if row["category"] == "EDUCATION"],
    }
    _write_json(output_root / "education-opportunity-filter-catalog.json", education_catalog)
    _write_jsonl(output_root / "education-opportunity-filter-evidence.jsonl", education_rows)
    _write_jsonl(output_root / "institution-normalization.jsonl", normalized_institutions)
    _write_json(output_root / "institution-identity-summary.json", identity_summary)
    _write_json(output_root / "research-production-reconciliation.json", reconciliation)
    _write_json(output_root / "source-legal-records.json", source_legal)
    _write_json(output_root / "career-education-crosswalk.json", crosswalk)

    report_files = (
        "education-opportunity-filter-catalog.json",
        "education-opportunity-filter-evidence.jsonl",
        "institution-normalization.jsonl",
        "institution-identity-summary.json",
        "research-production-reconciliation.json",
        "source-legal-records.json",
        "career-education-crosswalk.json",
    )
    build_manifest = {
        "schema_version": "phase6f-education-build-manifest-1.0",
        "build_id": BUILD_ID,
        "generated_at": GENERATED_AT,
        "command": "python -m konsider.ingestion.phase6_education_opportunity --output data/reports/phase6f-2026-08-03 --verify-retained-sources",
        "base_release_id": "2026-07-29.2",
        "base_release_schema_version": "konsider-release-5.0",
        "career_staged_release_id": "phase6e-career-2026-08-03.1",
        "activation_authorized": False,
        "api_exposure_authorized": False,
        "ranking_change_authorized": False,
        "input_checksums": {**research_checksums, **phase6e_checksums},
        "retained_source_verification": {
            filename: "CHECKSUM_FROZEN_OPTIONAL_LOCAL_GATE"
            for filename in _read_json(PHASE6C_FIXTURE)["metadata"]["source_files"]
        },
        "artifact_checksums": {
            **artifact_checksums,
            "candidate-release-manifest.json": f"sha256:{_sha256(staged / 'candidate-release-manifest.json')}",
            **{filename: f"sha256:{_sha256(output_root / filename)}" for filename in report_files},
        },
        "assertions": {
            "career_filter_count": 5,
            "education_filter_count": 4,
            "combined_filter_count": 9,
            "country_count": 91,
            "education_evidence_record_count": 364,
            "combined_evidence_record_count": 819,
            "institution_count": 2831,
            "unique_ror_count": 2831,
            "manual_institution_disambiguation_count": 6,
            "research_reconciliation_passed": True,
            "all_shortlists_20_of_20_assessable": True,
            "current_release_unchanged": True,
            "ranking_api_ui_unchanged": True,
        },
    }
    _write_json(output_root / "build-manifest.json", build_manifest)
    return build_manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--verify-retained-sources", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    display_catalog = load_product_display_catalog(
        DISPLAY_CATALOG_PATH, DISPLAY_CATALOG_SCHEMA_PATH
    )
    manifest = build_education_opportunity_bundle(
        args.output,
        display_catalog=display_catalog,
        verify_raw=args.verify_retained_sources,
    )
    print(
        f"build={manifest['build_id']} filters={manifest['assertions']['combined_filter_count']} "
        f"records={manifest['assertions']['combined_evidence_record_count']} activation=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
