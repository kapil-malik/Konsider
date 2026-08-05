"""Deterministic, draft-only release foundation for destination-side TFC artifacts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from konsider.contracts import ContractError, validate_contract
from konsider.ingestion.countries import COUNTRIES, COUNTRY_CODES
from konsider.ingestion.tfc_sources import TfcSourceError, TfcSourceRegistry

ARTIFACT_SPECS = (
    ("TFC_CATALOG", "tfc-catalog.json", "tfc-release-catalog-1.0"),
    (
        "DESTINATION_RULE_EVIDENCE",
        "tfc-destination-rule-evidence.jsonl",
        "tfc-rule-evidence-record-1.0",
    ),
    ("TFC_POLICY_BUNDLES", "tfc-policy-bundles.json", "tfc-policy-bundles-1.0"),
    (
        "TFC_SOURCE_LEGAL_MANIFEST",
        "tfc-source-legal-manifest.json",
        "tfc-source-legal-manifest-1.0",
    ),
    ("TFC_COVERAGE_SUMMARY", "tfc-coverage-summary.json", "tfc-coverage-summary-1.0"),
    ("TFC_VALIDATION", "tfc-validation.json", "tfc-validation-report-1.0"),
)
PAYLOAD_FILES = tuple(spec[1] for spec in ARTIFACT_SPECS)
SUPPORT_STATES = (
    "SUPPORTED",
    "EVIDENCE_INSUFFICIENT",
    "LEGALLY_BLOCKED",
    "STALE",
    "NOT_APPLICABLE_NATIONAL",
    "UNSUPPORTED",
)
DIFF_TYPES = (
    "SOURCE_INPUT_CHANGED",
    "NORMALIZED_RULE_CHANGED",
    "EFFECTIVE_DATE_CHANGED",
    "EVALUATION_POLICY_CHANGED",
    "SUPPORT_STATE_CHANGED",
)
FORBIDDEN_RELEASE_KEYS = {
    "account_id",
    "affinity_contribution",
    "applicant_profile",
    "household_profile",
    "lsc_aggregation_policy",
    "ofc_state",
    "pcc_activation_threshold",
    "precomputed_outcome",
    "profile_data",
    "rank",
    "ranking_weight",
    "session_id",
}


class TfcReleaseError(ValueError):
    """Raised when a TFC candidate cannot be built, loaded, or replayed."""


@dataclass(frozen=True)
class TfcReleaseArtifacts:
    catalog: dict[str, Any]
    rule_evidence: tuple[dict[str, Any], ...]
    policy_bundles: dict[str, Any]
    source_legal_manifest: dict[str, Any]
    coverage_summary: dict[str, Any]
    validation: dict[str, Any]


@dataclass(frozen=True)
class LoadedTfcRelease:
    path: Path
    manifest: dict[str, Any]
    artifacts: TfcReleaseArtifacts


@dataclass(frozen=True)
class TfcReplayResult:
    status: str
    compared_files: tuple[str, ...]
    mismatched_files: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.status == "PASSED"


def _contract(payload: Any, schema: str, context: str) -> None:
    try:
        validate_contract(payload, schema, context=context, schema_generation=4)
    except ContractError as exc:
        raise TfcReleaseError(str(exc)) from exc


def _json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        for row in rows
    )


def _checksum(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def _release_checksum(manifest: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in manifest.items() if key != "release_checksum"}
    canonical = json.dumps(unsigned, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return _checksum(canonical.encode("utf-8"))


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            yield from _walk_keys(child)


def _period(record: Mapping[str, Any]) -> Mapping[str, Any]:
    return record["effective_period"]


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _is_current(record: Mapping[str, Any], as_of: date) -> bool:
    period = _period(record)
    effective_to = period["effective_to"]
    return (
        _date(period["effective_from"]) <= as_of
        and (effective_to is None or as_of <= _date(effective_to))
        and as_of <= _date(period["stale_after"])
    )


def _issue(code: str, message: str, *record_ids: str) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "ERROR",
        "message": message,
        "record_ids": sorted(set(record_ids)),
    }


def _validate_schema_contracts(artifacts: TfcReleaseArtifacts) -> None:
    _contract(artifacts.catalog, "tfc-release-catalog", "TFC release catalog")
    _contract(artifacts.policy_bundles, "tfc-policy-bundles", "TFC policy bundles")
    _contract(
        artifacts.source_legal_manifest,
        "tfc-source-legal-manifest",
        "TFC source/legal manifest",
    )
    _contract(artifacts.coverage_summary, "tfc-coverage-summary", "TFC coverage summary")
    for row in artifacts.rule_evidence:
        _contract(row, "tfc-rule-evidence-record", f"TFC record {row.get('record_id')}")


def validate_tfc_release_artifacts(
    artifacts: TfcReleaseArtifacts, *, validated_as_of: str
) -> dict[str, Any]:
    """Validate structure, identity, effective dates, support completeness, and boundaries."""

    _validate_schema_contracts(artifacts)
    as_of = _date(validated_as_of)
    issues: list[dict[str, Any]] = []
    keys = set(_walk_keys(replace(artifacts, validation={}).__dict__))
    forbidden = sorted(keys & FORBIDDEN_RELEASE_KEYS)
    if forbidden:
        issues.append(
            _issue(
                "FORBIDDEN_RELEASE_FIELD",
                f"Release artifacts contain forbidden profile/ranking fields: {forbidden}.",
            )
        )

    definitions = artifacts.catalog["definitions"]
    tfc_ids = [row["tfc_id"] for row in definitions]
    policy_ids = [row["policy_id"] for row in artifacts.policy_bundles["policies"]]
    if len(tfc_ids) != len(set(tfc_ids)):
        issues.append(_issue("DUPLICATE_TFC_ID", "Release catalog TFC IDs must be unique."))
    if len(policy_ids) != len(set(policy_ids)):
        issues.append(_issue("DUPLICATE_POLICY_ID", "Evaluation policy IDs must be unique."))
    policy_by_id = {row["policy_id"]: row for row in artifacts.policy_bundles["policies"]}
    for definition in definitions:
        policy = policy_by_id.get(definition["policy_id"])
        if policy is None or policy["tfc_id"] != definition["tfc_id"]:
            issues.append(
                _issue(
                    "BROKEN_POLICY_BINDING",
                    f"TFC {definition['tfc_id']} does not bind its own evaluation policy.",
                )
            )
        elif policy["result_family"] != definition["result_family"]:
            issues.append(
                _issue(
                    "RESULT_FAMILY_MISMATCH",
                    f"TFC {definition['tfc_id']} and its policy disagree on result family.",
                )
            )

    try:
        source_registry = TfcSourceRegistry(artifacts.source_legal_manifest)
    except TfcSourceError as exc:
        raise TfcReleaseError(str(exc)) from exc
    source_ids = set(source_registry.source_ids)
    for source_id in source_registry.source_ids:
        source = source_registry.get(source_id)
        effective_to = source["effective_to"]
        if effective_to is not None and _date(str(effective_to)) < _date(
            str(source["effective_from"])
        ):
            issues.append(
                _issue(
                    "INVALID_SOURCE_EFFECTIVE_PERIOD",
                    f"Source {source_id} ends before it begins.",
                    source_id,
                )
            )
    records = artifacts.rule_evidence
    record_ids = [row["record_id"] for row in records]
    if len(record_ids) != len(set(record_ids)):
        issues.append(_issue("DUPLICATE_RECORD_ID", "Rule/evidence record IDs must be unique."))
    by_record_id = {row["record_id"]: row for row in records}
    jurisdictions = [row for row in records if row["record_type"] == "JURISDICTION"]
    jurisdiction_by_id = {row["jurisdiction_id"]: row for row in jurisdictions}
    if len(jurisdiction_by_id) != len(jurisdictions):
        issues.append(_issue("DUPLICATE_JURISDICTION_ID", "Jurisdiction IDs must be unique."))
    prefix_by_level = {
        "COUNTRY": "country:",
        "REGION": "region:",
        "CITY": "city:",
        "INSTITUTION": "institution:",
        "REGULATOR": "regulator:",
    }
    for row in jurisdictions:
        if not row["jurisdiction_id"].startswith(prefix_by_level[row["level"]]):
            issues.append(
                _issue(
                    "JURISDICTION_LEVEL_MISMATCH",
                    f"Jurisdiction {row['jurisdiction_id']} has the wrong identity prefix.",
                    row["record_id"],
                )
            )
        parent_id = row["parent_jurisdiction_id"]
        if parent_id is not None and parent_id not in jurisdiction_by_id:
            issues.append(
                _issue(
                    "BROKEN_JURISDICTION_PARENT",
                    f"Jurisdiction {row['jurisdiction_id']} has an unknown parent.",
                    row["record_id"],
                )
            )
        elif (
            parent_id is not None
            and jurisdiction_by_id[parent_id]["country_code"] != row["country_code"]
        ):
            issues.append(
                _issue(
                    "JURISDICTION_COUNTRY_MISMATCH",
                    f"Jurisdiction {row['jurisdiction_id']} and its parent disagree on country.",
                    row["record_id"],
                )
            )
        if row["country_code"] not in COUNTRY_CODES:
            issues.append(
                _issue(
                    "UNKNOWN_JURISDICTION_COUNTRY",
                    f"Jurisdiction {row['jurisdiction_id']} is outside the stable universe.",
                    row["record_id"],
                )
            )

    rules = [row for row in records if row["record_type"] in {"ROUTE_RULE", "METRIC_FORMULA"}]
    rules_by_identity: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    catalog_families = {row["tfc_id"]: row["result_family"] for row in definitions}
    for row in rules:
        record_id = row["record_id"]
        expected_family = (
            "RULE_ROUTE_MATCH" if row["record_type"] == "ROUTE_RULE" else "SCENARIO_METRIC"
        )
        if catalog_families.get(row["tfc_id"]) != expected_family:
            issues.append(
                _issue(
                    "RULE_FAMILY_NOT_CATALOGED",
                    f"{record_id} is not bound to a matching catalog result family.",
                    record_id,
                )
            )
        if row["jurisdiction_id"] not in jurisdiction_by_id:
            issues.append(
                _issue(
                    "UNKNOWN_RULE_JURISDICTION",
                    f"{record_id} references an unknown jurisdiction.",
                    record_id,
                )
            )
        missing_sources = sorted(
            {reference["source_id"] for reference in row["source_references"]} - source_ids
        )
        if missing_sources:
            issues.append(
                _issue(
                    "UNKNOWN_RULE_SOURCE",
                    f"{record_id} references unknown sources {missing_sources}.",
                    record_id,
                )
            )
        period = _period(row)
        if period["effective_to"] is not None and _date(period["effective_to"]) < _date(
            period["effective_from"]
        ):
            issues.append(
                _issue("INVALID_EFFECTIVE_PERIOD", f"{record_id} ends before it begins.", record_id)
            )
        if row["record_type"] == "ROUTE_RULE":
            override_id = row["overrides_record_id"]
            if override_id is not None:
                overridden = by_record_id.get(override_id)
                if (
                    overridden is None
                    or overridden["record_type"] != "ROUTE_RULE"
                    or overridden["tfc_id"] != row["tfc_id"]
                    or overridden["route_id"] != row["route_id"]
                ):
                    issues.append(
                        _issue(
                            "INVALID_RULE_OVERRIDE",
                            f"{record_id} does not identify a matching route rule to override.",
                            record_id,
                        )
                    )
            threshold_ids = [item["threshold_id"] for item in row["thresholds"]]
            if len(threshold_ids) != len(set(threshold_ids)):
                issues.append(
                    _issue(
                        "DUPLICATE_THRESHOLD_ID",
                        f"{record_id} repeats a threshold ID.",
                        record_id,
                    )
                )
            missing_thresholds = {
                condition["threshold_id"]
                for condition in row["conditions"]
                if condition["condition_type"] == "THRESHOLD"
                and condition["threshold_id"] not in threshold_ids
            }
            if missing_thresholds:
                issues.append(
                    _issue(
                        "UNKNOWN_THRESHOLD",
                        f"{record_id} references unknown thresholds {sorted(missing_thresholds)}.",
                        record_id,
                    )
                )
            identity = (row["tfc_id"], "ROUTE_RULE", row["route_id"], row["jurisdiction_id"])
        else:
            if sum(component["coefficient"] for component in row["components"]) <= 0:
                issues.append(
                    _issue(
                        "INVALID_FORMULA_COMPONENTS",
                        f"{record_id} formula coefficients must have a positive sum.",
                        record_id,
                    )
                )
            identity = (row["tfc_id"], "METRIC_FORMULA", row["metric_id"], row["jurisdiction_id"])
        rules_by_identity.setdefault(identity, []).append(row)

    for versions in rules_by_identity.values():
        versions.sort(key=lambda row: _period(row)["effective_from"])
        for previous, current in zip(versions, versions[1:], strict=False):
            previous_to = _period(previous)["effective_to"]
            if previous_to is None or _date(_period(current)["effective_from"]) <= _date(
                previous_to
            ):
                issues.append(
                    _issue(
                        "OVERLAPPING_EFFECTIVE_PERIOD",
                        "Rule versions with the same identity must not overlap.",
                        previous["record_id"],
                        current["record_id"],
                    )
                )

    supports = [row for row in records if row["record_type"] == "DESTINATION_SUPPORT"]
    support_pairs = [(row["tfc_id"], row["country_code"]) for row in supports]
    expected_pairs = {(tfc_id, country) for tfc_id in tfc_ids for country in COUNTRY_CODES}
    actual_pairs = set(support_pairs)
    if len(support_pairs) != len(actual_pairs):
        issues.append(
            _issue(
                "DUPLICATE_TFC_COUNTRY_SUPPORT",
                "Each TFC-country pair must have exactly one support record.",
            )
        )
    if actual_pairs != expected_pairs:
        missing = len(expected_pairs - actual_pairs)
        extra = len(actual_pairs - expected_pairs)
        issues.append(
            _issue(
                "INCOMPLETE_COUNTRY_SUPPORT",
                f"Explicit support matrix differs from the stable universe: {missing} missing, {extra} extra.",
            )
        )
    for support in supports:
        support_id = support["record_id"]
        if support["evaluated_as_of"] != validated_as_of:
            issues.append(
                _issue(
                    "SUPPORT_DATE_MISMATCH",
                    f"{support_id} was not resolved at the candidate validation date.",
                    support_id,
                )
            )
        unknown_jurisdictions = set(support["jurisdiction_ids"]) - set(jurisdiction_by_id)
        unknown_rules = set(support["rule_record_ids"]) - set(by_record_id)
        if unknown_jurisdictions:
            issues.append(
                _issue(
                    "UNKNOWN_SUPPORT_JURISDICTION",
                    f"{support_id} references unknown jurisdictions.",
                    support_id,
                )
            )
        if unknown_rules:
            issues.append(
                _issue(
                    "UNKNOWN_SUPPORT_RULE",
                    f"{support_id} references unknown rules.",
                    support_id,
                )
            )
            continue
        for jurisdiction_id in support["jurisdiction_ids"]:
            jurisdiction = jurisdiction_by_id.get(jurisdiction_id)
            if jurisdiction is not None and jurisdiction["country_code"] != support["country_code"]:
                issues.append(
                    _issue(
                        "SUPPORT_JURISDICTION_COUNTRY_MISMATCH",
                        f"{support_id} references a jurisdiction in another country.",
                        support_id,
                    )
                )
        selected_rules = [by_record_id[record_id] for record_id in support["rule_record_ids"]]
        for rule in selected_rules:
            jurisdiction = jurisdiction_by_id.get(rule["jurisdiction_id"])
            if jurisdiction is not None and jurisdiction["country_code"] != support["country_code"]:
                issues.append(
                    _issue(
                        "SUPPORT_RULE_COUNTRY_MISMATCH",
                        f"{support_id} references a rule in another country.",
                        support_id,
                        rule["record_id"],
                    )
                )
        if support["support_status"] == "SUPPORTED":
            if not selected_rules:
                issues.append(
                    _issue(
                        "SUPPORTED_WITHOUT_RULE",
                        f"{support_id} is supported without an explicit rule.",
                        support_id,
                    )
                )
            for rule in selected_rules:
                if rule["tfc_id"] != support["tfc_id"]:
                    issues.append(
                        _issue(
                            "CROSS_TFC_RULE_REFERENCE",
                            f"{support_id} references a rule from another TFC.",
                            support_id,
                            rule["record_id"],
                        )
                    )
                if not _is_current(rule, as_of):
                    issues.append(
                        _issue(
                            "INACTIVE_RULE_SELECTED",
                            f"{support_id} selects a future, expired, or stale rule.",
                            support_id,
                            rule["record_id"],
                        )
                    )
                if _period(rule)["conflict_status"] == "UNRESOLVED":
                    issues.append(
                        _issue(
                            "UNRESOLVED_CONFLICT_SELECTED",
                            f"{support_id} selects a rule with unresolved authority conflict.",
                            support_id,
                            rule["record_id"],
                        )
                    )

    expected_coverage = make_coverage_summary(tfc_ids, supports)
    if artifacts.coverage_summary != expected_coverage:
        issues.append(_issue("COVERAGE_SUMMARY_MISMATCH", "Coverage summary does not reconcile."))

    checks = {
        "catalog_policy_binding": not any(
            issue["code"] in {"BROKEN_POLICY_BINDING", "RESULT_FAMILY_MISMATCH"} for issue in issues
        ),
        "country_support_complete": not any(
            issue["code"] in {"DUPLICATE_TFC_COUNTRY_SUPPORT", "INCOMPLETE_COUNTRY_SUPPORT"}
            for issue in issues
        ),
        "effective_periods_valid": not any(
            issue["code"] in {"INVALID_EFFECTIVE_PERIOD", "OVERLAPPING_EFFECTIVE_PERIOD"}
            for issue in issues
        ),
        "jurisdictions_valid": not any("JURISDICTION" in issue["code"] for issue in issues),
        "profile_ranking_fields_absent": not any(
            issue["code"] == "FORBIDDEN_RELEASE_FIELD" for issue in issues
        ),
        "rule_sources_resolved": not any(
            issue["code"] in {"UNKNOWN_RULE_SOURCE", "UNKNOWN_SUPPORT_RULE"} for issue in issues
        ),
    }
    report = {
        "schema_version": "tfc-validation-report-1.0",
        "validated_as_of": validated_as_of,
        "structural_passed": not issues,
        "promotion_eligible": False,
        "checks": checks,
        "issues": sorted(issues, key=lambda issue: (issue["code"], issue["record_ids"])),
    }
    _contract(report, "tfc-validation-report", "TFC validation report")
    return report


def make_coverage_summary(
    tfc_ids: Sequence[str], supports: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    by_tfc = []
    for tfc_id in sorted(tfc_ids):
        states = Counter(row["support_status"] for row in supports if row["tfc_id"] == tfc_id)
        by_tfc.append(
            {
                "tfc_id": tfc_id,
                "record_count": sum(states.values()),
                "support_state_counts": {state: states[state] for state in SUPPORT_STATES},
            }
        )
    return {
        "schema_version": "tfc-coverage-summary-1.0",
        "stable_universe_id": "stable_supported_v1",
        "stable_country_count": len(COUNTRY_CODES),
        "tfc_count": len(tfc_ids),
        "expected_support_records": len(tfc_ids) * len(COUNTRY_CODES),
        "actual_support_records": len(supports),
        "by_tfc": by_tfc,
    }


def build_tfc_release_artifacts(capture: Mapping[str, Any]) -> TfcReleaseArtifacts:
    """Normalize a frozen capture bundle into deterministic immutable release artifacts."""

    if capture.get("schema_version") != "tfc-synthetic-capture-1.0":
        raise TfcReleaseError("Unsupported or missing TFC capture schema version.")
    catalog = copy.deepcopy(capture["catalog"])
    policies = copy.deepcopy(capture["policy_bundles"])
    sources = copy.deepcopy(capture["source_legal_manifest"])
    tfc_ids = [row["tfc_id"] for row in catalog["definitions"]]
    jurisdictions = [
        {
            "schema_version": "tfc-rule-evidence-record-1.0",
            "record_id": f"jurisdiction:country:{code}",
            "record_type": "JURISDICTION",
            "jurisdiction_id": f"country:{code}",
            "level": "COUNTRY",
            "country_code": code,
            "parent_jurisdiction_id": None,
            "name": COUNTRIES[code],
            "mapping_status": "ACTIVE",
        }
        for code in COUNTRY_CODES
    ]
    jurisdictions.extend(copy.deepcopy(capture.get("additional_jurisdictions", [])))
    rules = copy.deepcopy(capture["rules"])
    overrides = {(row["tfc_id"], row["country_code"]): row for row in capture["support_overrides"]}
    if len(overrides) != len(capture["support_overrides"]):
        raise TfcReleaseError("Synthetic capture repeats a TFC-country support override.")
    unknown_overrides = set(overrides) - {
        (tfc_id, country) for tfc_id in tfc_ids for country in COUNTRY_CODES
    }
    if unknown_overrides:
        raise TfcReleaseError(
            f"Synthetic capture has unknown support overrides: {unknown_overrides}."
        )
    supports = []
    for tfc_id in sorted(tfc_ids):
        for country in COUNTRY_CODES:
            override = overrides.get((tfc_id, country), {})
            status = override.get("support_status", "UNSUPPORTED")
            supports.append(
                {
                    "schema_version": "tfc-rule-evidence-record-1.0",
                    "record_id": f"support:{tfc_id}:{country}",
                    "record_type": "DESTINATION_SUPPORT",
                    "tfc_id": tfc_id,
                    "country_code": country,
                    "support_status": status,
                    "jurisdiction_ids": override.get("jurisdiction_ids", [f"country:{country}"]),
                    "rule_record_ids": override.get("rule_record_ids", []),
                    "reason_code": override.get(
                        "reason_code", None if status == "SUPPORTED" else "SYNTHETIC_UNSUPPORTED"
                    ),
                    "evaluated_as_of": capture["validated_as_of"],
                }
            )
    records = tuple(
        sorted(
            (*jurisdictions, *rules, *supports),
            key=lambda row: (row["record_type"], row["record_id"]),
        )
    )
    coverage = make_coverage_summary(tfc_ids, supports)
    artifacts = TfcReleaseArtifacts(catalog, records, policies, sources, coverage, {})
    report = validate_tfc_release_artifacts(artifacts, validated_as_of=capture["validated_as_of"])
    if not report["structural_passed"]:
        codes = sorted({issue["code"] for issue in report["issues"]})
        raise TfcReleaseError(f"TFC capture failed semantic validation: {codes}.")
    return replace(artifacts, validation=report)


def _artifact_bytes(artifacts: TfcReleaseArtifacts) -> dict[str, bytes]:
    return {
        "tfc-catalog.json": _json_bytes(artifacts.catalog),
        "tfc-destination-rule-evidence.jsonl": _jsonl_bytes(artifacts.rule_evidence),
        "tfc-policy-bundles.json": _json_bytes(artifacts.policy_bundles),
        "tfc-source-legal-manifest.json": _json_bytes(artifacts.source_legal_manifest),
        "tfc-coverage-summary.json": _json_bytes(artifacts.coverage_summary),
        "tfc-validation.json": _json_bytes(artifacts.validation),
    }


class TfcCandidateReleaseRepository:
    """Writes and loads release-6 drafts; publication and activation are intentionally absent."""

    def __init__(self, release_root: Path | str) -> None:
        self.release_root = Path(release_root)

    def write_draft(
        self,
        release_id: str,
        artifacts: TfcReleaseArtifacts,
        *,
        base_manifest: Mapping[str, Any],
    ) -> Path:
        if base_manifest.get("schema_version") != "konsider-release-5.1":
            raise TfcReleaseError("Release 6 candidates must bind an immutable release-5.1 base.")
        if not artifacts.validation.get("structural_passed"):
            raise TfcReleaseError("A structurally invalid TFC candidate cannot be written.")
        regenerated = validate_tfc_release_artifacts(
            replace(artifacts, validation={}),
            validated_as_of=artifacts.validation["validated_as_of"],
        )
        if regenerated != artifacts.validation:
            raise TfcReleaseError("Stored TFC validation report is not reproducible.")
        release_path = self.release_root / release_id
        if release_path.exists():
            raise FileExistsError(f"TFC candidate {release_id} already exists.")
        release_path.mkdir(parents=True)
        payloads = _artifact_bytes(artifacts)
        for filename, content in payloads.items():
            (release_path / filename).write_bytes(content)
        checksums = {filename: _checksum(content) for filename, content in payloads.items()}
        binding = {
            "binding_schema_version": "tfc-release-binding-1.0",
            "target_release_schema_version": "konsider-release-6.0",
            "artifacts": [
                {
                    "role": role,
                    "filename": filename,
                    "schema_version": schema_version,
                    "checksum": checksums[filename],
                }
                for role, filename, schema_version in ARTIFACT_SPECS
            ],
        }
        _contract(binding, "tfc-release-binding", "release-6 TFC binding")
        manifest = {
            "schema_version": "konsider-release-6.0",
            "release_id": release_id,
            "status": "draft",
            "synthetic": artifacts.catalog["synthetic"],
            "base_release": {
                "release_id": base_manifest["release_id"],
                "schema_version": base_manifest["schema_version"],
                "release_checksum": base_manifest["release_checksum"],
            },
            "tfc": binding,
            "file_checksums": checksums,
            "release_checksum": "sha256:" + "0" * 64,
            "activation_authorized": False,
        }
        manifest["release_checksum"] = _release_checksum(manifest)
        _contract(manifest, "tfc-release-manifest", "release-6 TFC candidate manifest")
        (release_path / "manifest.json").write_bytes(_json_bytes(manifest))
        return release_path

    def load(self, path: Path | str) -> LoadedTfcRelease:
        release_path = Path(path)
        manifest = json.loads((release_path / "manifest.json").read_text(encoding="utf-8"))
        _contract(manifest, "tfc-release-manifest", "stored release-6 TFC manifest")
        if manifest["release_checksum"] != _release_checksum(manifest):
            raise TfcReleaseError("TFC release checksum does not reconcile.")
        payloads = {filename: (release_path / filename).read_bytes() for filename in PAYLOAD_FILES}
        checksums = {filename: _checksum(content) for filename, content in payloads.items()}
        if checksums != manifest["file_checksums"]:
            raise TfcReleaseError("TFC artifact checksum mismatch.")
        binding_checksums = {
            row["filename"]: row["checksum"] for row in manifest["tfc"]["artifacts"]
        }
        if binding_checksums != checksums:
            raise TfcReleaseError("TFC binding and file checksums disagree.")
        records = tuple(
            json.loads(line)
            for line in payloads["tfc-destination-rule-evidence.jsonl"].decode("utf-8").splitlines()
            if line
        )
        artifacts = TfcReleaseArtifacts(
            catalog=json.loads(payloads["tfc-catalog.json"]),
            rule_evidence=records,
            policy_bundles=json.loads(payloads["tfc-policy-bundles.json"]),
            source_legal_manifest=json.loads(payloads["tfc-source-legal-manifest.json"]),
            coverage_summary=json.loads(payloads["tfc-coverage-summary.json"]),
            validation=json.loads(payloads["tfc-validation.json"]),
        )
        regenerated = validate_tfc_release_artifacts(
            replace(artifacts, validation={}),
            validated_as_of=artifacts.validation["validated_as_of"],
        )
        if regenerated != artifacts.validation:
            raise TfcReleaseError("Stored TFC validation report is not reproducible.")
        return LoadedTfcRelease(release_path, manifest, artifacts)

    def replay(
        self,
        path: Path | str,
        capture: Mapping[str, Any],
    ) -> TfcReplayResult:
        loaded = self.load(path)
        rebuilt = build_tfc_release_artifacts(capture)
        with tempfile.TemporaryDirectory(prefix="konsider-tfc-replay-") as temporary:
            repository = TfcCandidateReleaseRepository(Path(temporary))
            replay_path = repository.write_draft(
                loaded.manifest["release_id"],
                rebuilt,
                base_manifest=loaded.manifest["base_release"],
            )
            compared = (*PAYLOAD_FILES, "manifest.json")
            mismatched = tuple(
                filename
                for filename in compared
                if (loaded.path / filename).read_bytes() != (replay_path / filename).read_bytes()
            )
        return TfcReplayResult(
            "PASSED" if not mismatched else "FAILED", tuple(compared), mismatched
        )


def semantic_diff(before: LoadedTfcRelease, after: LoadedTfcRelease) -> dict[str, Any]:
    """Expose source, normalized rule, date, policy, and support changes as reviewable data."""

    changes: list[dict[str, Any]] = []

    def add(change_type: str, identity: str, old: Any, new: Any) -> None:
        changes.append(
            {"change_type": change_type, "identity": identity, "before": old, "after": new}
        )

    before_sources = {
        row["source_id"]: row for row in before.artifacts.source_legal_manifest["sources"]
    }
    after_sources = {
        row["source_id"]: row for row in after.artifacts.source_legal_manifest["sources"]
    }
    for identity in sorted(set(before_sources) | set(after_sources)):
        if before_sources.get(identity) != after_sources.get(identity):
            add(
                "SOURCE_INPUT_CHANGED",
                identity,
                before_sources.get(identity),
                after_sources.get(identity),
            )

    def records(loaded: LoadedTfcRelease, record_type: str) -> dict[str, dict[str, Any]]:
        return {
            row["record_id"]: row
            for row in loaded.artifacts.rule_evidence
            if row["record_type"] == record_type
        }

    before_rules = {
        **records(before, "ROUTE_RULE"),
        **records(before, "METRIC_FORMULA"),
    }
    after_rules = {**records(after, "ROUTE_RULE"), **records(after, "METRIC_FORMULA")}
    for identity in sorted(set(before_rules) | set(after_rules)):
        old = before_rules.get(identity)
        new = after_rules.get(identity)
        if old == new:
            continue
        old_period = None if old is None else old.get("effective_period")
        new_period = None if new is None else new.get("effective_period")
        if old_period != new_period:
            add("EFFECTIVE_DATE_CHANGED", identity, old_period, new_period)
        old_normalized = (
            None if old is None else {k: v for k, v in old.items() if k != "effective_period"}
        )
        new_normalized = (
            None if new is None else {k: v for k, v in new.items() if k != "effective_period"}
        )
        if old_normalized != new_normalized:
            add("NORMALIZED_RULE_CHANGED", identity, old_normalized, new_normalized)

    before_policies = {row["policy_id"]: row for row in before.artifacts.policy_bundles["policies"]}
    after_policies = {row["policy_id"]: row for row in after.artifacts.policy_bundles["policies"]}
    for identity in sorted(set(before_policies) | set(after_policies)):
        if before_policies.get(identity) != after_policies.get(identity):
            add(
                "EVALUATION_POLICY_CHANGED",
                identity,
                before_policies.get(identity),
                after_policies.get(identity),
            )

    before_support = records(before, "DESTINATION_SUPPORT")
    after_support = records(after, "DESTINATION_SUPPORT")
    for identity in sorted(set(before_support) | set(after_support)):
        old = before_support.get(identity)
        new = after_support.get(identity)
        old_state = None if old is None else old["support_status"]
        new_state = None if new is None else new["support_status"]
        if old_state != new_state:
            add("SUPPORT_STATE_CHANGED", identity, old_state, new_state)

    counts = Counter(change["change_type"] for change in changes)
    result = {
        "schema_version": "tfc-semantic-diff-1.0",
        "from_release_id": before.manifest["release_id"],
        "to_release_id": after.manifest["release_id"],
        "change_counts": {change_type: counts[change_type] for change_type in DIFF_TYPES},
        "changes": sorted(changes, key=lambda row: (row["change_type"], row["identity"])),
    }
    _contract(result, "tfc-semantic-diff", "TFC semantic diff")
    return result


def build_candidate_from_capture(
    capture_path: Path,
    output_root: Path,
    base_release_path: Path,
) -> Path:
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    base_manifest = json.loads((base_release_path / "manifest.json").read_text(encoding="utf-8"))
    artifacts = build_tfc_release_artifacts(capture)
    return TfcCandidateReleaseRepository(output_root).write_draft(
        capture["release_id"], artifacts, base_manifest=base_manifest
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--capture", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--base-release", type=Path, required=True)
    replay = subparsers.add_parser("replay")
    replay.add_argument("--capture", type=Path, required=True)
    replay.add_argument("--release", type=Path, required=True)
    diff = subparsers.add_parser("diff")
    diff.add_argument("--before", type=Path, required=True)
    diff.add_argument("--after", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "build":
        path = build_candidate_from_capture(args.capture, args.output, args.base_release)
        print(path)
        return 0
    if args.command == "replay":
        capture = json.loads(args.capture.read_text(encoding="utf-8"))
        result = TfcCandidateReleaseRepository(args.release.parent).replay(args.release, capture)
        print(json.dumps({"status": result.status, "mismatched_files": result.mismatched_files}))
        return 0 if result.passed else 1
    repository = TfcCandidateReleaseRepository(args.before.parent)
    result = semantic_diff(repository.load(args.before), repository.load(args.after))
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ARTIFACT_SPECS",
    "LoadedTfcRelease",
    "TfcCandidateReleaseRepository",
    "TfcReleaseArtifacts",
    "TfcReleaseError",
    "TfcReplayResult",
    "build_candidate_from_capture",
    "build_tfc_release_artifacts",
    "make_coverage_summary",
    "semantic_diff",
    "validate_tfc_release_artifacts",
]
