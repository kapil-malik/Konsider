import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.contracts import ContractError, validate_contract

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / "contracts" / "schemas" / "v3"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "phase5b"


VALID_FIXTURES = {
    "criterion-fcc-lsc.json": "criterion-definition",
    "criterion-pcc-lsc-c66.json": "criterion-definition",
    "criterion-policy-c66.json": "criterion-policy",
    "geographic-entity-country.json": "geographic-entity",
    "geographic-entity-city.json": "geographic-entity",
    "source-lineage-multiple.json": "source-lineage",
    "source-lineage-universe.json": "source-lineage",
    "locality-universe.json": "locality-universe",
    "locality-aggregation-policy-c66.json": "locality-aggregation-policy",
    "geographic-observation-c66.json": "geographic-observation",
    "geographic-score-c66.json": "geographic-score",
    "derived-country-evidence-c66.json": "derived-country-evidence",
    "criterion-outcome-direct.json": "criterion-outcome",
    "criterion-outcome-derived.json": "criterion-outcome",
    "ranking-request.json": "ranking-request",
    "ranking-response.json": "ranking-response",
    "release-manifest.json": "release-manifest",
    "validation-report.json": "validation-report",
    "consumer-catalog.json": "consumer-catalog",
}

INVALID_FIXTURES = {
    "criterion-direct-with-locality.json": "criterion-definition",
    "geographic-observation-free-text-subject.json": "geographic-observation",
    "geographic-observation-mismatched-subject.json": "geographic-observation",
    "source-lineage-opaque-string.json": "source-lineage",
    "derived-country-evidence-opaque-source.json": "derived-country-evidence",
    "criterion-outcome-derived-without-evidence.json": "criterion-outcome",
    "ranking-request-legacy-profile.json": "ranking-request",
    "ranking-response-duplicate-locality-status.json": "ranking-response",
    "ranking-response-coverage-in-locality-status.json": "ranking-response",
}


def _load(kind: str, filename: str) -> dict:
    return json.loads((FIXTURE_ROOT / kind / filename).read_text(encoding="utf-8"))


def _validate(payload: dict, schema_name: str, context: str) -> None:
    validate_contract(
        payload,
        schema_name,
        context=context,
        schema_generation=3,
    )


def test_phase5b_schemas_are_valid_draft_2020_12() -> None:
    schemas = sorted(SCHEMA_ROOT.glob("*.schema.json"))
    assert len(schemas) == 23
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(("filename", "schema_name"), VALID_FIXTURES.items())
def test_valid_phase5b_contract_fixtures(filename: str, schema_name: str) -> None:
    _validate(_load("valid", filename), schema_name, filename)


@pytest.mark.parametrize(("filename", "schema_name"), INVALID_FIXTURES.items())
def test_invalid_phase5b_contract_fixtures(filename: str, schema_name: str) -> None:
    with pytest.raises(ContractError):
        _validate(_load("invalid", filename), schema_name, filename)


def test_coverage_and_locality_scope_are_orthogonal() -> None:
    fcc_lsc = _load("valid", "criterion-fcc-lsc.json")
    pcc_lsc = _load("valid", "criterion-pcc-lsc-c66.json")

    assert fcc_lsc["coverage"]["mode"] == "GLOBAL_CORE"
    assert pcc_lsc["coverage"]["mode"] == "CONDITIONAL_COMPLETE_CASE"
    for criterion in (fcc_lsc, pcc_lsc):
        assert criterion["scope"]["derivation"] == "AGGREGATED_FROM_LOCALITIES"
        assert criterion["scope"]["evidence_level"] == "LOCALITY"
        _validate(criterion, "criterion-definition", criterion["id"])

    assert fcc_lsc["coverage"]["activation_threshold"] is None
    assert fcc_lsc["scope"]["locality_analysis_threshold"] == 0.6
    assert pcc_lsc["coverage"]["activation_threshold"] == 0.6
    assert pcc_lsc["scope"]["locality_analysis_threshold"] == 0.6
    for criterion in (fcc_lsc, pcc_lsc):
        coverage = criterion["coverage"]
        assert sum(coverage["outcome_counts"].values()) == coverage["stable_country_count"]
        assert coverage["outcome_counts"]["valid"] == coverage["valid_country_count"]

        national_direct = copy.deepcopy(criterion)
        national_direct["scope"] = {
            "evidence_level": "COUNTRY",
            "result_level": "COUNTRY",
            "locality_type": None,
            "derivation": "DIRECT",
            "locality_universe_id": None,
            "aggregation_policy_id": None,
            "locality_analysis_threshold": None,
        }
        _validate(
            national_direct,
            "criterion-definition",
            f"{criterion['coverage']['mode']} national direct",
        )


def test_c66_keeps_identity_and_records_narrowed_construct() -> None:
    criterion = _load("valid", "criterion-pcc-lsc-c66.json")
    assert criterion["id"] == "C66"
    assert criterion["display_name"] == "Extreme heat exposure"
    assert criterion["historical_names"] == ["Extreme-weather risk"]
    assert "broad extreme-weather risk" in criterion["interpretation"]


def test_geographic_records_use_canonical_entity_references() -> None:
    observation = _load("valid", "geographic-observation-c66.json")
    score = _load("valid", "geographic-score-c66.json")
    evidence = _load("valid", "derived-country-evidence-c66.json")

    assert observation["subject"] == {
        "entity_id": "ghsl-uc:10737",
        "entity_type": "CITY",
    }
    assert score["subject"] == observation["subject"]
    assert evidence["country"]["entity_type"] == "COUNTRY"
    assert all(
        item["locality"]["entity_type"] != "COUNTRY" for item in evidence["contributing_localities"]
    )
    assert "country_code" not in observation
    assert "country_code" not in score


def test_derived_evidence_retains_multiple_source_lineage() -> None:
    lineage = _load("valid", "source-lineage-multiple.json")
    evidence = _load("valid", "derived-country-evidence-c66.json")

    assert len(lineage["sources"]) == 2
    assert {source["role"] for source in lineage["sources"]} == {
        "PRIMARY_OBSERVATION",
        "ENTITY_UNIVERSE",
    }
    assert evidence["criterion_source_lineage_id"] == lineage["lineage_id"]
    assert len(evidence["contributing_localities"]) == 2
    assert all(
        item["observation_ids"] and item["score_id"] for item in evidence["contributing_localities"]
    )


def test_locality_universe_has_criterion_independent_lineage() -> None:
    universe = _load("valid", "locality-universe.json")
    universe_lineage = _load("valid", "source-lineage-universe.json")

    assert universe["source_lineage_id"] == universe_lineage["lineage_id"]
    assert universe["selection"]["independent_of_criterion_values"] is True
    assert "C66" not in universe["source_lineage_id"]
    assert {source["role"] for source in universe_lineage["sources"]} == {"ENTITY_UNIVERSE"}


def test_release_catalog_and_validation_reconcile_coverage_metadata() -> None:
    catalog = _load("valid", "consumer-catalog.json")
    manifest = _load("valid", "release-manifest.json")
    validation = _load("valid", "validation-report.json")
    c66_catalog = next(item for item in catalog["criteria"] if item["id"] == "C66")

    assert c66_catalog["coverage"] == manifest["criterion_coverage"]["C66"]
    assert validation["criterion_coverage"] == manifest["criterion_coverage"]
    assert manifest["catalog_schema_version"] == catalog["schema_version"]
    assert manifest["validation_schema_version"] == validation["schema_version"]


def test_preference_preset_naming_rejects_legacy_profile_fields() -> None:
    catalog = _load("valid", "consumer-catalog.json")
    request = _load("valid", "ranking-request.json")

    assert "preference_presets" in catalog
    assert "profiles" not in catalog
    assert "preference_preset_id" in request
    assert "profile_id" not in request

    invalid_catalog = copy.deepcopy(catalog)
    invalid_catalog["profiles"] = invalid_catalog.pop("preference_presets")
    with pytest.raises(ContractError):
        _validate(invalid_catalog, "consumer-catalog", "legacy catalog profile field")


def test_structured_assessments_have_one_source_of_truth() -> None:
    response = _load("valid", "ranking-response.json")
    assert set(response["assessments"]) == {"coverage", "locality", "profile"}
    assert set(response["rankings"][0]["assessments"]) == {"locality", "profile"}
    assert response["assessments"]["profile"]["status"] == "NO_PROFILE_CONTEXT"

    for duplicate in ("coverage_status", "locality_status", "profile_status"):
        invalid = copy.deepcopy(response)
        invalid[duplicate] = "DUPLICATE"
        with pytest.raises(ContractError):
            _validate(invalid, "ranking-response", duplicate)


def test_locality_statuses_do_not_encode_coverage() -> None:
    schema = json.loads((SCHEMA_ROOT / "ranking-response.schema.json").read_text(encoding="utf-8"))
    statuses = schema["$defs"]["localityStatus"]["enum"]
    assert {
        "NO_ACTIVE_LOCALITY_CRITERIA",
        "BELOW_ANALYSIS_THRESHOLD",
        "ONE_ACTIVE_LOCALITY_CRITERION",
        "COMMON_LOCALITY_AVAILABLE",
        "PARTIAL_OVERLAP",
        "NO_COMMON_LOCALITY",
        "INSUFFICIENT_LOCALITY_EVIDENCE",
    }.issubset(statuses)
    assert all(
        token not in status
        for status in statuses
        for token in ("GLOBAL_CORE", "CONDITIONAL", "PCC", "FCC", "COVERAGE")
    )
