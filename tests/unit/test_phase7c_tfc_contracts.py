import copy
import json
from collections import Counter
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.contracts import ContractError, validate_contract
from konsider.domain.tfc_contracts import (
    APPROVED_FIRST_WAVE_IDS,
    RouteMatchClassification,
    TfcCommonStatus,
    TfcContractError,
    compute_profile_snapshot_hash,
    validate_applicant_profile,
    validate_effective_profile_context,
    validate_exploration_scenario,
    validate_household_profile,
    validate_privacy_retention_policy,
    validate_profile_export,
    validate_profile_field_registry,
    validate_route_result,
    validate_tfc_assessment,
    validate_tfc_catalog,
    validate_tfc_definition,
    validate_tfc_outcome,
    validate_tfc_release_binding,
)
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / "contracts" / "schemas" / "v4"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "phase7c"
VALID = FIXTURE_ROOT / "valid"


def _load(filename: str) -> dict:
    return json.loads((VALID / filename).read_text(encoding="utf-8"))


def _outcomes() -> dict[str, dict]:
    return _load("route-outcomes.json")["outcomes"]


def _build_assessment(scenario_name: str) -> dict:
    descriptor = _load("assessment-scenarios.json")["scenarios"][scenario_name]
    outcomes = []
    for name in descriptor["outcome_fixture_names"]:
        outcome = copy.deepcopy(_outcomes()[name])
        outcome["country_code"] = descriptor["country_code"]
        outcomes.append(outcome)
    counts = Counter(outcome["common_status"] for outcome in outcomes)
    return {
        "schema_version": "tfc-assessment-1.0",
        "profile": {
            "context_status": "COMPLETE_PROFILE_CONTEXT",
            "snapshot_hash": outcomes[0]["snapshot_hash"],
            "evaluated_dimensions": ["APPLICANT", "HOUSEHOLD", "SCENARIO"],
            "retention": {
                "mode": "TAB_MEMORY_ONLY",
                "consent": "NOT_REQUESTED",
                "policy_version": "profile-retention-policy-1.0",
                "consented_at": None,
                "expires_at": None,
            },
        },
        "feasibility": {
            "execution_status": "EXECUTED",
            "selected_tfc_ids": descriptor["selected_tfc_ids"],
            "filter_mode": descriptor["filter_mode"],
            "input_required_fields": [],
            "source_effective_dates": {"synthetic-bundle": "2026-01-01"},
            "status_counts": {status.value: counts[status.value] for status in TfcCommonStatus},
            "countries": [
                {
                    "country_code": descriptor["country_code"],
                    "base_rank": 1,
                    "feasibility_filtered_position": (
                        1
                        if descriptor["filter_mode"] == "EXPLICIT_SUPPORTED_ROUTE_FILTER"
                        else None
                    ),
                    "outcomes": outcomes,
                }
            ],
        },
    }


def test_all_generation_4_schemas_are_valid_draft_2020_12() -> None:
    schemas = sorted(SCHEMA_ROOT.glob("*.schema.json"))
    assert len(schemas) >= 15
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_profile_scenario_and_effective_snapshot_contracts() -> None:
    complete = _load("applicant-complete.json")
    partial = _load("applicant-partial.json")
    household = _load("household.json")
    scenario = _load("scenario-complete.json")
    context = _load("effective-profile-context.json")

    validate_applicant_profile(complete)
    validate_applicant_profile(partial)
    validate_household_profile(household)
    validate_exploration_scenario(scenario)
    validate_effective_profile_context(context)
    assert context["snapshot_hash"] == compute_profile_snapshot_hash(context)
    assert "account_id" not in context


def test_exact_birth_date_is_exception_only_and_never_device_retained() -> None:
    applicant = _load("applicant-complete.json")
    applicant["date_of_birth"] = "1995-01-01"
    with pytest.raises(TfcContractError, match="exception-only"):
        validate_applicant_profile(applicant)

    context = _load("effective-profile-context.json")
    context["applicant"]["age_years"] = None
    context["applicant"]["date_of_birth"] = "1995-01-01"
    context["retention"] = {
        "mode": "DEVICE_WITH_EXPLICIT_CONSENT",
        "consent": "GRANTED",
        "policy_version": "profile-retention-policy-1.0",
        "consented_at": "2026-08-05T10:00:00Z",
        "expires_at": "2026-09-04T10:00:00Z",
    }
    context["snapshot_hash"] = compute_profile_snapshot_hash(context)
    with pytest.raises(TfcContractError, match="date of birth"):
        validate_effective_profile_context(context)


def test_field_registry_covers_privacy_redaction_and_first_wave_only() -> None:
    registry = _load("profile-field-registry.json")
    validate_profile_field_registry(registry)
    assert len({field["field_id"] for field in registry["fields"]}) == len(registry["fields"])
    birth_date = next(
        field for field in registry["fields"] if field["field_id"] == "applicant.date_of_birth"
    )
    assert birth_date["default_retention"] == "NEVER_RETAIN_BY_DEFAULT"
    assert birth_date["redaction"] == "OMIT"
    assert birth_date["may_be_stored_locally"] is False


def test_catalog_contains_exactly_three_inactive_route_checks() -> None:
    catalog = _load("tfc-catalog.json")
    validate_tfc_catalog(catalog)
    definitions = catalog["definitions"]
    assert {definition["id"] for definition in definitions} == APPROVED_FIRST_WAVE_IDS
    assert all(definition["check_kind"] == "RULE_ROUTE_MATCH" for definition in definitions)
    assert all(definition["result_schema_id"] == "tfc-route-result-1.0" for definition in definitions)
    assert all(definition["filter_capability"] == "ASSESSMENT_ONLY" for definition in definitions)
    assert all(len(definition["supported_destination_codes"]) == 29 for definition in definitions)


@pytest.mark.parametrize(
    "forbidden",
    [
        "weight",
        "affinity_contribution",
        "normalization_direction",
        "pcc_activation_threshold",
        "ofc_state",
        "lsc_aggregation_policy",
        "account_lookup",
    ],
)
def test_tfc_definition_rejects_sibling_product_fields(forbidden: str) -> None:
    definition = copy.deepcopy(_load("tfc-catalog.json")["definitions"][0])
    definition[forbidden] = 1
    with pytest.raises(TfcContractError):
        validate_tfc_definition(definition)


def test_common_status_and_route_classification_enums_are_exact() -> None:
    assert [status.value for status in TfcCommonStatus] == [
        "EVALUATED",
        "INPUT_REQUIRED",
        "DESTINATION_EVIDENCE_INSUFFICIENT",
        "UNSUPPORTED",
        "NOT_APPLICABLE",
        "EVALUATION_ERROR",
    ]
    assert [classification.value for classification in RouteMatchClassification] == [
        "SUPPORTED_ROUTE_MATCH",
        "CONDITIONAL_ROUTE_MATCH",
        "NO_SUPPORTED_ROUTE_MATCH",
    ]


def test_all_synthetic_route_and_status_outcomes_validate() -> None:
    outcomes = _outcomes()
    assert {
        "route_match",
        "conditional_route_match",
        "no_supported_route_match",
        "input_required",
        "unsupported_destination",
        "insufficient_evidence",
        "household_not_relocating",
        "household_dependent_result",
        "region_dependent_result",
    } == set(outcomes)
    for outcome in outcomes.values():
        validate_tfc_outcome(outcome)


def test_no_route_match_requires_explicit_complete_inventory() -> None:
    result = copy.deepcopy(_outcomes()["no_supported_route_match"]["result"])
    result["route_inventory_complete"] = False
    with pytest.raises(TfcContractError, match="complete inventory"):
        validate_route_result(result)


def test_route_result_requires_evaluated_identity_and_source_effective_metadata() -> None:
    result = copy.deepcopy(_outcomes()["route_match"]["result"])
    result["supported_routes_evaluated"] = []
    with pytest.raises(TfcContractError):
        validate_route_result(result)

    missing_evidence = copy.deepcopy(_outcomes()["route_match"])
    missing_evidence["result"].pop("evidence")
    with pytest.raises(TfcContractError):
        validate_tfc_outcome(missing_evidence)


def test_no_context_no_tfc_and_multi_tfc_assessments_validate() -> None:
    validate_tfc_assessment(_load("assessment-no-context.json"))
    validate_tfc_assessment(_load("assessment-no-tfc.json"))
    multi = _build_assessment("multiple_tfc_types")
    validate_tfc_assessment(multi)
    assert len(multi["feasibility"]["countries"][0]["outcomes"]) == 3
    assert multi["profile"]["context_status"] == "COMPLETE_PROFILE_CONTEXT"


def test_explicit_filter_shape_is_contractible_but_not_enabled_for_first_wave() -> None:
    assessment = _build_assessment("optional_explicit_filtering_capability")
    validate_tfc_assessment(assessment)
    assert assessment["feasibility"]["filter_mode"] == "EXPLICIT_SUPPORTED_ROUTE_FILTER"
    assert all(
        definition["filter_capability"] == "ASSESSMENT_ONLY"
        for definition in _load("tfc-catalog.json")["definitions"]
    )


def test_scenario_metric_and_mixed_result_family_are_not_approved_contracts() -> None:
    invalid = json.loads(
        (FIXTURE_ROOT / "invalid" / "invalid-cases.json").read_text(encoding="utf-8")
    )
    payload = invalid["cases"]["numeric_result_without_units"]["payload"]
    with pytest.raises(TfcContractError):
        validate_tfc_outcome(payload)


def test_privacy_policy_and_release6_binding_contracts() -> None:
    validate_privacy_retention_policy(_load("privacy-retention-policy.json"))
    validate_profile_export(_load("profile-export-redacted.json"))
    validate_tfc_release_binding(_load("tfc-release-binding.json"))

    raw_profile_value = copy.deepcopy(_load("profile-export-redacted.json"))
    raw_profile_value["applicant"]["age_years"] = 31
    with pytest.raises(TfcContractError):
        validate_profile_export(raw_profile_value)

    profile_in_release = copy.deepcopy(_load("tfc-release-binding.json"))
    profile_in_release["profile_data"] = {"citizenships": ["IND"]}
    with pytest.raises(TfcContractError):
        validate_tfc_release_binding(profile_in_release)


def test_invalid_fixture_register_covers_every_required_rejection() -> None:
    cases = json.loads(
        (FIXTURE_ROOT / "invalid" / "invalid-cases.json").read_text(encoding="utf-8")
    )["cases"]
    assert set(cases) == {
        "tfc_weight_field",
        "ofc_state_in_tfc_payload",
        "profile_data_in_release_artifact",
        "hidden_account_identifier",
        "missing_source_effective_metadata",
        "route_without_evaluated_identity",
        "numeric_result_without_units",
        "sensitive_silent_persistence",
    }

    context = _load("effective-profile-context.json")
    context["account_id"] = "synthetic-account"
    with pytest.raises(TfcContractError):
        validate_effective_profile_context(context)

    registry = _load("profile-field-registry.json")
    registry["fields"][0]["default_retention"] = "DEVICE_WITHOUT_CONSENT"
    with pytest.raises(TfcContractError):
        validate_profile_field_registry(registry)


def test_active_release_and_api_remain_unchanged_and_tfc_free() -> None:
    active_release = ROOT / "data" / "releases" / "2026-08-04.1"
    manifest = json.loads((active_release / "manifest.json").read_text(encoding="utf-8"))
    validate_contract(manifest, "release-manifest", context="active manifest", schema_generation=3)
    loaded = CurrentReleaseRepository(ROOT / "data" / "releases").load(active_release)
    assert loaded.manifest["schema_version"] == "konsider-release-5.1"
    assert "tfcs" not in loaded.manifest

    openapi = json.loads(
        (ROOT / "contracts" / "openapi" / "konsider-api-2.0.json").read_text(encoding="utf-8")
    )
    assert "/api/v2/tfcs" not in openapi["paths"]
    assert "TypedFeasibilityCheck" not in json.dumps(openapi, sort_keys=True)


def test_schema_validator_rejects_direct_ofc_state_and_numeric_result() -> None:
    outcome = copy.deepcopy(_outcomes()["route_match"])
    outcome["state"] = "VERIFIED_STRONG_SIGNAL"
    with pytest.raises(TfcContractError):
        validate_tfc_outcome(outcome)

    with pytest.raises(ContractError):
        validate_contract(
            {"schema_version": "scenario-metric-result-1.0", "value": 42},
            "tfc-route-result",
            context="unapproved scenario metric",
            schema_generation=4,
        )
