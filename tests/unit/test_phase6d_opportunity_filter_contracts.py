import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.api.models.v2 import AssessmentsV2Response
from konsider.contracts import validate_contract
from konsider.domain.opportunity_filters import (
    OpportunityFilterConfidenceBand,
    OpportunityFilterConfidenceTier,
    OpportunityFilterContractError,
    OpportunityFilterReasonCode,
    OpportunityFilterState,
    validate_opportunity_filter_assessment,
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_definition,
    validate_opportunity_filter_evidence,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_binding,
    validate_opportunity_filter_release_bundle,
)
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / "contracts" / "schemas" / "v3"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "phase6d" / "valid"


def _load(filename: str) -> dict:
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def test_all_schema_generation_3_contracts_are_valid_draft_2020_12() -> None:
    schemas = sorted(SCHEMA_ROOT.glob("*.schema.json"))
    assert len(schemas) == 23
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    ("filename", "schema_name"),
    [
        ("definition-career.json", "opportunity-filter-definition"),
        ("definition-education.json", "opportunity-filter-definition"),
        ("catalog-empty.json", "opportunity-filter-catalog"),
        ("evidence-verified-career.json", "opportunity-filter-evidence"),
        ("evidence-not-established-education.json", "opportunity-filter-evidence"),
        ("evidence-insufficient.json", "opportunity-filter-evidence"),
        ("assessment-no-filters.json", "opportunity-filter-assessment"),
        ("assessment-filtered.json", "opportunity-filter-assessment"),
        ("source-manifest.json", "opportunity-filter-source-manifest"),
        ("evidence-policy.json", "opportunity-filter-evidence-policy"),
        ("threshold-policy.json", "opportunity-filter-threshold-policy"),
        ("coverage-summary.json", "opportunity-filter-coverage-summary"),
        ("release-manifest-5.1.json", "release-manifest"),
    ],
)
def test_valid_phase6d_schema_fixtures(filename: str, schema_name: str) -> None:
    validate_contract(_load(filename), schema_name, context=filename, schema_generation=3)


def test_public_state_confidence_and_reason_enums_are_exact() -> None:
    assert [state.value for state in OpportunityFilterState] == [
        "VERIFIED_STRONG_SIGNAL",
        "STRONG_SIGNAL_NOT_ESTABLISHED",
        "INSUFFICIENT_EVIDENCE",
    ]
    assert {band.value for band in OpportunityFilterConfidenceBand} == {"HIGH", "MEDIUM", "LOW"}
    assert {tier.value for tier in OpportunityFilterConfidenceTier} == {
        "HIGH_CONFIDENCE_OBSERVED_HARMONISED",
        "HIGH_CONFIDENCE_OBSERVED_NATIONAL",
        "HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET",
        "MEDIUM_CONFIDENCE_MODELLED_HARMONISED",
        "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK",
        "LOW_CONFIDENCE_SUPPLEMENTAL",
    }
    assert len(OpportunityFilterReasonCode) == 24


@pytest.mark.parametrize(
    "forbidden",
    [
        "weight",
        "score_direction",
        "normalization",
        "affinity_contribution",
        "pcc_activation_threshold",
        "imputation",
        "ranking_coefficient",
    ],
)
def test_opportunity_filter_definitions_reject_ranking_fields(forbidden: str) -> None:
    definition = _load("definition-career.json")
    definition[forbidden] = 1
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_definition(definition)


def test_catalog_requires_unique_ids_and_sort_order_without_activation() -> None:
    career = _load("definition-career.json")
    education = _load("definition-education.json")
    catalog = _load("catalog-empty.json")
    catalog["definitions"] = [career, education]
    validate_opportunity_filter_catalog(catalog)

    duplicate_id = copy.deepcopy(catalog)
    duplicate_id["definitions"][1]["id"] = career["id"]
    with pytest.raises(OpportunityFilterContractError, match="IDs must be unique"):
        validate_opportunity_filter_catalog(duplicate_id)

    duplicate_order = copy.deepcopy(catalog)
    duplicate_order["definitions"][1]["sort_order"] = career["sort_order"]
    with pytest.raises(OpportunityFilterContractError, match="sort orders must be unique"):
        validate_opportunity_filter_catalog(duplicate_order)

    active_in_staged = copy.deepcopy(catalog)
    active_in_staged["definitions"][0]["active"] = True
    active_in_staged["definitions"][0]["availability"] = "AVAILABLE"
    with pytest.raises(OpportunityFilterContractError, match="cannot activate"):
        validate_opportunity_filter_catalog(active_in_staged)


def test_state_reason_and_evidence_completeness_are_consistent() -> None:
    verified = _load("evidence-verified-career.json")
    not_established = _load("evidence-not-established-education.json")
    insufficient = _load("evidence-insufficient.json")
    for row in (verified, not_established, insufficient):
        validate_opportunity_filter_evidence(row)

    wrong_reason = copy.deepcopy(verified)
    wrong_reason["reason_codes"] = ["NO_APPROVED_STRONG_ROUTE_PASSED"]
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_evidence(wrong_reason)

    incomplete_negative = copy.deepcopy(not_established)
    incomplete_negative["coverage_completeness"] = "PARTIAL"
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_evidence(incomplete_negative)

    no_route = copy.deepcopy(verified)
    no_route["establishing_route_ids"] = []
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_evidence(no_route)

    assert insufficient["metric_payload"] is None
    assert insufficient["source_references"] == []


@pytest.mark.parametrize(
    ("reason", "establishing"),
    [
        ("SKILLED_TRADES_ROUTE_PASSED", ["skilled_trades"]),
        ("CONSTRUCTION_ROUTE_PASSED", ["construction"]),
        (
            "SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED",
            ["skilled_trades", "construction"],
        ),
    ],
)
def test_skilled_trades_and_construction_route_attribution(
    reason: str, establishing: list[str]
) -> None:
    row = _load("evidence-verified-career.json")
    row["filter_id"] = "synthetic_trades_opportunity"
    row["reason_codes"] = [reason]
    row["evaluated_route_ids"] = ["skilled_trades", "construction"]
    row["establishing_route_ids"] = establishing
    row["threshold_results"] = [
        {
            "route_id": route,
            "passed": route in establishing,
            "policy_version": row["threshold_policy_version"],
            "components": {},
        }
        for route in row["evaluated_route_ids"]
    ]
    validate_opportunity_filter_evidence(row)

    wrong = copy.deepcopy(row)
    wrong["establishing_route_ids"] = (
        ["skilled_trades"] if establishing == ["construction"] else ["construction"]
    )
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_evidence(wrong)


def test_evidence_matrix_requires_one_explicit_state_per_pair() -> None:
    catalog = _load("catalog-empty.json")
    catalog["definitions"] = [_load("definition-career.json")]
    row = _load("evidence-verified-career.json")
    validate_opportunity_filter_evidence_matrix(catalog, [row], ["CAN"])

    with pytest.raises(OpportunityFilterContractError, match="incomplete"):
        validate_opportunity_filter_evidence_matrix(catalog, [], ["CAN"])
    with pytest.raises(OpportunityFilterContractError, match="Duplicate"):
        validate_opportunity_filter_evidence_matrix(catalog, [row, row], ["CAN"])


def test_assessment_contract_preserves_no_filter_behavior_and_strict_filtering() -> None:
    no_filters = _load("assessment-no-filters.json")
    filtered = _load("assessment-filtered.json")
    validate_opportunity_filter_assessment(no_filters)
    validate_opportunity_filter_assessment(filtered)
    assert [row["base_rank"] for row in no_filters["countries"]] == [
        row["filtered_rank"] for row in no_filters["countries"]
    ]

    inconsistent = copy.deepcopy(filtered)
    inconsistent["countries"][1]["passes"] = True
    inconsistent["countries"][1]["filtered_rank"] = 2
    with pytest.raises(OpportunityFilterContractError):
        validate_opportunity_filter_assessment(inconsistent)

    empty = copy.deepcopy(filtered)
    empty["status"] = "NO_COUNTRIES_MATCH"
    empty["passing_country_count"] = 0
    empty["excluded_country_count"] = 2
    empty["excluded_counts_by_state"] = {
        "STRONG_SIGNAL_NOT_ESTABLISHED": 2,
        "INSUFFICIENT_EVIDENCE": 0,
    }
    empty["per_filter"][0]["passing_country_count"] = 0
    empty["per_filter"][0]["excluded_counts_by_state"] = {
        "STRONG_SIGNAL_NOT_ESTABLISHED": 2,
        "INSUFFICIENT_EVIDENCE": 0,
    }
    empty["countries"][0]["passes"] = False
    empty["countries"][0]["filtered_rank"] = None
    empty["countries"][0]["filter_states"][0] = {
        "filter_id": "synthetic_career_opportunity",
        "state": "STRONG_SIGNAL_NOT_ESTABLISHED",
        "passes": False,
    }
    validate_opportunity_filter_assessment(empty)


def test_coverage_summary_reconciles_all_91_explicit_states() -> None:
    summary = _load("coverage-summary.json")
    validate_opportunity_filter_coverage_summary(summary)

    broken = copy.deepcopy(summary)
    broken["filters"]["synthetic_career_opportunity"]["assessable_count"] = 62
    with pytest.raises(OpportunityFilterContractError, match="Assessable count"):
        validate_opportunity_filter_coverage_summary(broken)


def test_release_5_0_remains_valid_and_release_5_1_binding_is_consistent() -> None:
    active_manifest = json.loads(
        (ROOT / "data" / "releases" / "2026-07-29.2" / "manifest.json").read_text(encoding="utf-8")
    )
    validate_opportunity_filter_release_binding(active_manifest)
    assert "opportunity_filters" not in active_manifest

    staged = _load("release-manifest-5.1.json")
    validate_opportunity_filter_release_binding(staged)
    validate_opportunity_filter_release_bundle(staged, _load("catalog-empty.json"), [], ["CAN"])
    broken = copy.deepcopy(staged)
    broken["opportunity_filters"]["artifacts"][0]["checksum"] = "sha256:" + "f" * 64
    with pytest.raises(OpportunityFilterContractError, match="disagrees"):
        validate_opportunity_filter_release_binding(broken)


def test_release5_0_compatibility_and_phase6g_api_surface_is_additive() -> None:
    loaded = CurrentReleaseRepository(ROOT / "data" / "releases").load(
        ROOT / "data" / "releases" / "2026-07-29.2"
    )
    assert loaded.manifest["schema_version"] == "konsider-release-5.0"
    assert loaded.artifacts.consumer_catalog["schema_version"] == "consumer-catalog-3.0"
    assert "opportunity_filters" not in loaded.manifest
    assert set(AssessmentsV2Response.model_fields) == {
        "coverage",
        "locality",
        "profile",
        "opportunity",
    }

    openapi = json.loads(
        (ROOT / "contracts" / "openapi" / "konsider-api-2.0.json").read_text(encoding="utf-8")
    )
    serialized = json.dumps(openapi, sort_keys=True)
    assert "/api/v2/opportunity-filters" in openapi["paths"]
    assert "OpportunityAssessmentV2Response" in serialized
    assert "OpportunityFilterSelection" in serialized
