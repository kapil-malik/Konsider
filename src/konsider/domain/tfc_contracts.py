"""Phase 7C Typed Feasibility Check contracts and semantic validation.

These contracts are intentionally disconnected from runtime ranking, API models, and release
activation. Phase 7D and later phases may consume them only after owner approval.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from enum import StrEnum
from typing import Any, Mapping

from konsider.contracts import ContractError, validate_contract


class TfcContractError(ValueError):
    """Raised when a Phase 7 contract is structurally or semantically invalid."""


class TfcCommonStatus(StrEnum):
    EVALUATED = "EVALUATED"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    DESTINATION_EVIDENCE_INSUFFICIENT = "DESTINATION_EVIDENCE_INSUFFICIENT"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    EVALUATION_ERROR = "EVALUATION_ERROR"


class RouteMatchClassification(StrEnum):
    SUPPORTED_ROUTE_MATCH = "SUPPORTED_ROUTE_MATCH"
    CONDITIONAL_ROUTE_MATCH = "CONDITIONAL_ROUTE_MATCH"
    NO_SUPPORTED_ROUTE_MATCH = "NO_SUPPORTED_ROUTE_MATCH"


APPROVED_FIRST_WAVE_IDS = frozenset(
    {
        "skilled_work_route_feasibility",
        "family_accompaniment_reunification",
        "post_study_work_pathway",
    }
)

EXPECTED_TFC_RELEASE_ARTIFACTS = {
    "TFC_CATALOG": "tfc-catalog.json",
    "DESTINATION_RULE_EVIDENCE": "tfc-destination-rule-evidence.jsonl",
    "TFC_POLICY_BUNDLES": "tfc-policy-bundles.json",
    "TFC_SOURCE_LEGAL_MANIFEST": "tfc-source-legal-manifest.json",
    "TFC_COVERAGE_SUMMARY": "tfc-coverage-summary.json",
    "TFC_VALIDATION": "tfc-validation.json",
}


def _contract(payload: Any, schema_name: str, context: str) -> None:
    try:
        validate_contract(payload, schema_name, context=context, schema_generation=4)
    except ContractError as exc:
        raise TfcContractError(str(exc)) from exc


def _canonical_snapshot_value(context: Mapping[str, Any]) -> dict[str, Any]:
    value = {
        "schema_version": context["schema_version"],
        "applicant": copy.deepcopy(context["applicant"]),
        "household": copy.deepcopy(context["household"]),
        "scenario": copy.deepcopy(context["scenario"]),
        "selected_tfc_ids": context["selected_tfc_ids"],
        "resolved_taxonomy_versions": context["resolved_taxonomy_versions"],
    }
    value["applicant"].pop("profile_id", None)
    value["household"].pop("household_id", None)
    value["scenario"].pop("scenario_id", None)
    return value


def compute_profile_snapshot_hash(context: Mapping[str, Any]) -> str:
    """Hash normalized values without mutable client IDs or evaluation time."""

    serialized = json.dumps(
        _canonical_snapshot_value(context),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def validate_applicant_profile(profile: Mapping[str, Any]) -> None:
    _contract(profile, "applicant-profile", "ApplicantProfile")
    unknown = set(profile["unknown_fields"])
    if any(not field.startswith("applicant.") for field in unknown):
        raise TfcContractError("Applicant unknown fields must use the applicant namespace.")
    if profile.get("date_of_birth") is not None and profile.get("age_years") is not None:
        raise TfcContractError("Use age_years normally; date_of_birth is exception-only, not additive.")


def validate_household_profile(profile: Mapping[str, Any]) -> None:
    _contract(profile, "household-profile", "HouseholdProfile")
    unknown = set(profile["unknown_fields"])
    if any(not field.startswith("household.") for field in unknown):
        raise TfcContractError("Household unknown fields must use the household namespace.")
    declared_size = 1 + int(profile["partner_status"] not in {"NONE", "UNKNOWN"}) + len(
        profile["dependants"]
    )
    if declared_size > 20:
        raise TfcContractError("Declared household composition exceeds the supported boundary.")


def validate_exploration_scenario(scenario: Mapping[str, Any]) -> None:
    _contract(scenario, "exploration-scenario", "ExplorationScenario")
    if set(scenario["selected_tfc_ids"]) - APPROVED_FIRST_WAVE_IDS:
        raise TfcContractError("Scenario selects a TFC outside the approved first wave.")
    if scenario["purpose"] == "STUDY" and scenario.get("intended_study") is None:
        raise TfcContractError("A study-purpose scenario requires intended_study facts.")


def validate_effective_profile_context(context: Mapping[str, Any]) -> None:
    _contract(context, "effective-profile-context", "EffectiveProfileContext")
    validate_applicant_profile(context["applicant"])
    validate_household_profile(context["household"])
    validate_exploration_scenario(context["scenario"])
    if context["selected_tfc_ids"] != context["scenario"]["selected_tfc_ids"]:
        raise TfcContractError("Effective and scenario selected TFC IDs must match in order.")
    if context["snapshot_hash"] != compute_profile_snapshot_hash(context):
        raise TfcContractError("Effective profile snapshot hash does not match normalized values.")
    if (
        context["retention"]["mode"] == "DEVICE_WITH_EXPLICIT_CONSENT"
        and context["applicant"].get("date_of_birth") is not None
    ):
        raise TfcContractError("Exact date of birth may never enter same-device retention.")


def validate_profile_field_registry(registry: Mapping[str, Any]) -> None:
    _contract(registry, "profile-field-registry", "profile field registry")
    fields = registry["fields"]
    ids = [field["field_id"] for field in fields]
    if len(ids) != len(set(ids)):
        raise TfcContractError("Profile field IDs must be unique.")
    for field in fields:
        if set(field["consumer_tfc_ids"]) - APPROVED_FIRST_WAVE_IDS:
            raise TfcContractError("Field registry contains a non-first-wave consumer.")
        if field["sensitivity"].startswith("HIGH_") and field["may_be_stored_locally"]:
            if field["default_retention"] != "TAB_MEMORY_ONLY":
                raise TfcContractError("High-sensitivity fields cannot be silently persisted.")


def validate_tfc_definition(definition: Mapping[str, Any]) -> None:
    _contract(definition, "tfc-definition", "TFC definition")
    if definition["id"] not in APPROVED_FIRST_WAVE_IDS:
        raise TfcContractError("Definition is outside the owner-approved first wave.")
    input_ids = [requirement["field_id"] for requirement in definition["input_requirements"]]
    if len(input_ids) != len(set(input_ids)):
        raise TfcContractError("A TFC definition must declare each input field once.")
    if definition["active"] or definition["availability"] != "CONTRACT_ONLY":
        raise TfcContractError("Phase 7C definitions must remain inactive and contracts-only.")


def validate_tfc_catalog(catalog: Mapping[str, Any]) -> None:
    _contract(catalog, "tfc-catalog", "TFC catalog")
    definitions = catalog["definitions"]
    ids = [definition["id"] for definition in definitions]
    orders = [definition["sort_order"] for definition in definitions]
    if set(ids) != APPROVED_FIRST_WAVE_IDS or len(ids) != len(set(ids)):
        raise TfcContractError("Catalog must contain each approved first-wave TFC exactly once.")
    if len(orders) != len(set(orders)):
        raise TfcContractError("TFC sort orders must be unique.")
    for definition in definitions:
        validate_tfc_definition(definition)
    if catalog["activation_status"] != "CONTRACTS_ONLY":
        raise TfcContractError("Phase 7C cannot stage or activate a TFC catalog.")


def validate_route_result(result: Mapping[str, Any]) -> None:
    _contract(result, "tfc-route-result", "TFC route result")
    classification = RouteMatchClassification(result["match_classification"])
    evaluated = [route["route_id"] for route in result["supported_routes_evaluated"]]
    matched = result["matched_route_ids"]
    if len(evaluated) != len(set(evaluated)):
        raise TfcContractError("Evaluated route identities must be unique.")
    if not set(matched).issubset(evaluated):
        raise TfcContractError("Matched routes must be identified in supported_routes_evaluated.")
    if classification in {
        RouteMatchClassification.SUPPORTED_ROUTE_MATCH,
        RouteMatchClassification.CONDITIONAL_ROUTE_MATCH,
    } and not matched:
        raise TfcContractError("Positive and conditional classifications require a matched route.")
    if classification == RouteMatchClassification.CONDITIONAL_ROUTE_MATCH and not (
        result["unknown_conditions"] or result["unmet_conditions"]
    ):
        raise TfcContractError("A conditional route match requires an unknown or unmet condition.")
    if classification == RouteMatchClassification.NO_SUPPORTED_ROUTE_MATCH:
        if matched or not result["route_inventory_complete"]:
            raise TfcContractError(
                "No supported-route match requires an empty match set and complete inventory."
            )


def validate_tfc_outcome(outcome: Mapping[str, Any]) -> None:
    _contract(outcome, "tfc-outcome", "TFC outcome")
    status = TfcCommonStatus(outcome["common_status"])
    reasons = set(outcome["reason_codes"])
    expected = {
        TfcCommonStatus.EVALUATED: {
            "ROUTE_MATCHED",
            "ROUTE_CONDITIONALLY_MATCHED",
            "NO_SUPPORTED_ROUTE_MATCH",
        },
        TfcCommonStatus.INPUT_REQUIRED: {"PROFILE_FIELDS_MISSING"},
        TfcCommonStatus.DESTINATION_EVIDENCE_INSUFFICIENT: {
            "DESTINATION_SOURCE_MISSING",
            "DESTINATION_EVIDENCE_CONFLICT",
        },
        TfcCommonStatus.UNSUPPORTED: {
            "DESTINATION_NOT_SUPPORTED",
            "PROFILE_BOUNDARY_UNSUPPORTED",
        },
        TfcCommonStatus.NOT_APPLICABLE: {"HOUSEHOLD_NOT_RELOCATING", "NO_TFC_SELECTED"},
        TfcCommonStatus.EVALUATION_ERROR: {"TECHNICAL_FAILURE"},
    }[status]
    if not reasons.issubset(expected):
        raise TfcContractError(f"Reason codes do not match common status {status}.")
    if status == TfcCommonStatus.EVALUATED:
        validate_route_result(outcome["result"])


def validate_tfc_assessment(assessment: Mapping[str, Any]) -> None:
    _contract(assessment, "tfc-assessment", "TFC assessment")
    feasibility = assessment["feasibility"]
    selected = set(feasibility["selected_tfc_ids"])
    if selected - APPROVED_FIRST_WAVE_IDS:
        raise TfcContractError("Assessment selects a TFC outside the approved first wave.")
    outcomes = []
    countries = feasibility["countries"]
    if len({country["country_code"] for country in countries}) != len(countries):
        raise TfcContractError("Country feasibility assessments must be unique.")
    for country in countries:
        ids = [outcome["tfc_id"] for outcome in country["outcomes"]]
        if set(ids) != selected or len(ids) != len(set(ids)):
            raise TfcContractError("Each country must carry one outcome per selected TFC.")
        for outcome in country["outcomes"]:
            validate_tfc_outcome(outcome)
            if outcome["country_code"] != country["country_code"]:
                raise TfcContractError("Country and outcome country codes must agree.")
        outcomes.extend(country["outcomes"])
    counts = Counter(outcome["common_status"] for outcome in outcomes)
    if feasibility["status_counts"] != {
        status.value: counts[status.value] for status in TfcCommonStatus
    }:
        raise TfcContractError("TFC outcome status counts do not reconcile.")
    if feasibility["execution_status"] == "NO_TFC_SELECTED" and (
        selected or countries or any(feasibility["status_counts"].values())
    ):
        raise TfcContractError("No-TFC assessment must contain no execution outcomes.")


def validate_privacy_retention_policy(policy: Mapping[str, Any]) -> None:
    _contract(policy, "privacy-retention-policy", "privacy retention policy")


def validate_profile_export(export: Mapping[str, Any]) -> None:
    _contract(export, "profile-export", "redacted profile export")


def validate_tfc_release_binding(binding: Mapping[str, Any]) -> None:
    _contract(binding, "tfc-release-binding", "draft TFC release binding")
    artifacts = {artifact["role"]: artifact for artifact in binding["artifacts"]}
    if len(artifacts) != len(binding["artifacts"]) or set(artifacts) != set(
        EXPECTED_TFC_RELEASE_ARTIFACTS
    ):
        raise TfcContractError("TFC release binding must declare every artifact role once.")
    for role, filename in EXPECTED_TFC_RELEASE_ARTIFACTS.items():
        if artifacts[role]["filename"] != filename:
            raise TfcContractError(f"TFC release filename disagrees for {role}.")


__all__ = [
    "APPROVED_FIRST_WAVE_IDS",
    "RouteMatchClassification",
    "TfcCommonStatus",
    "TfcContractError",
    "compute_profile_snapshot_hash",
    "validate_applicant_profile",
    "validate_effective_profile_context",
    "validate_exploration_scenario",
    "validate_household_profile",
    "validate_privacy_retention_policy",
    "validate_profile_export",
    "validate_profile_field_registry",
    "validate_route_result",
    "validate_tfc_assessment",
    "validate_tfc_catalog",
    "validate_tfc_definition",
    "validate_tfc_outcome",
    "validate_tfc_release_binding",
]
