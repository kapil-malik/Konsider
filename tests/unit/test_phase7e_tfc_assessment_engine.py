import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.domain.tfc_assessment import (
    NO_MATCH_DISCLAIMER,
    TfcAssessmentEngine,
    TfcAssessmentError,
    benchmark_tfc_assessment,
    evaluate_route_conditions,
    normalize_effective_context,
)
from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.tfc_release import build_tfc_release_artifacts

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_PATH = ROOT / "tests" / "fixtures" / "phase7d" / "synthetic-capture.json"
CONTEXT_PATH = ROOT / "tests" / "fixtures" / "phase7e" / "golden-contexts.json"
ROUTE_TFC = "synthetic_skilled_route"
METRIC_TFC = "synthetic_housing_metric"


def _capture() -> dict:
    return json.loads(CAPTURE_PATH.read_text(encoding="utf-8"))


def _contexts() -> dict[str, dict]:
    return json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))


def _engine(capture: dict | None = None) -> TfcAssessmentEngine:
    return TfcAssessmentEngine(
        build_tfc_release_artifacts(capture or _capture()),
        active_release_id="2026-08-04.1",
        tfc_release_id="synthetic-phase7e-6.0",
    )


def _ranking_row(rank: int, code: str, score: float = 7.0) -> dict:
    return {
        "rank": rank,
        "base_rank": rank,
        "country": {
            "entity_id": f"country:{code}",
            "entity_type": "COUNTRY",
            "display_name": f"Synthetic {code}",
            "country_codes": [code],
            "region": None,
        },
        "total_score": score,
        "contributions": [
            {
                "criterion_id": "synthetic_pcc_lsc",
                "normalized_weight": 1.0,
                "contribution": score,
            }
        ],
        "assessments": {
            "locality": {"status": "SYNTHETIC_LSC_PRESERVED"},
            "profile": {"status": "EXISTING_PROFILE_ASSESSMENT"},
            "opportunity": {
                "evaluated": True,
                "passes": code != "ALB",
                "filter_evidence": [{"filter_id": "synthetic_ofc", "state": "PRESERVED"}],
            },
        },
    }


def _payload(codes: tuple[str, ...] = ("DEU", "AUS", "USA", "ALB")) -> dict:
    return {
        "release_id": "2026-08-04.1",
        "normalized_weights": {"synthetic_pcc_lsc": 1.0},
        "rankings": [
            _ranking_row(index, code, 9.0 - index * 0.25)
            for index, code in enumerate(codes, start=1)
        ],
        "assessments": {
            "coverage": {"status": "SYNTHETIC_PCC_PRESERVED"},
            "locality": {"status": "SYNTHETIC_LSC_PRESERVED"},
            "profile": {"status": "EXISTING_PROFILE_ASSESSMENT"},
            "opportunity": {"status": "SYNTHETIC_OFC_PRESERVED"},
        },
    }


def _country(run, code: str) -> dict:
    return next(row for row in run.assessment["countries"] if row["country_code"] == code)


def _outcome(run, code: str, tfc_id: str = ROUTE_TFC) -> dict:
    return next(row for row in _country(run, code)["outcomes"] if row["tfc_id"] == tfc_id)


def _run(context_name: str, selected: tuple[str, ...] = (ROUTE_TFC,)):
    return _engine().assess_ranking_payload(
        _payload(),
        context=_contexts()[context_name],
        selected_tfc_ids=selected,
        evaluation_date="2026-08-05",
    )


def _capture_with_second_supported_route() -> dict:
    capture = _capture()
    source_rule = next(
        row
        for row in capture["rules"]
        if row["record_id"] == "rule:synthetic_skilled_route:deu:a:v1"
    )
    rule = copy.deepcopy(source_rule)
    rule.update(
        record_id="rule:synthetic_skilled_route:gbr:a:v1",
        route_id="FX.GBR_HIGH_SKILL_A",
        route_name="Fictional second-country specialist route",
        jurisdiction_id="country:GBR",
    )
    capture["rules"].append(rule)
    capture["support_overrides"].append(
        {
            "tfc_id": ROUTE_TFC,
            "country_code": "GBR",
            "support_status": "SUPPORTED",
            "jurisdiction_ids": ["country:GBR"],
            "rule_record_ids": [rule["record_id"]],
            "reason_code": None,
        }
    )
    return capture


def _capture_for_three_route_checks_and_metric() -> dict:
    capture = _capture()
    route_definition = copy.deepcopy(capture["catalog"]["definitions"][0])
    route_policy = copy.deepcopy(capture["policy_bundles"]["policies"][0])
    source_rules = [
        row
        for row in capture["rules"]
        if row["tfc_id"] == ROUTE_TFC and row["jurisdiction_id"] == "country:DEU"
    ]
    for suffix in ("family", "study"):
        tfc_id = f"synthetic_{suffix}_route"
        definition = copy.deepcopy(route_definition)
        definition.update(
            tfc_id=tfc_id,
            name=f"Fictional {suffix} route performance check",
            policy_id=f"{tfc_id}.v1",
            applicable_purposes=["EXPLORATION"],
        )
        capture["catalog"]["definitions"].append(definition)
        policy = copy.deepcopy(route_policy)
        policy.update(tfc_id=tfc_id, policy_id=f"{tfc_id}.v1")
        capture["policy_bundles"]["policies"].append(policy)
        ids = []
        for index, source in enumerate(source_rules, start=1):
            rule = copy.deepcopy(source)
            rule.update(
                record_id=f"rule:{tfc_id}:deu:{index}:v1",
                tfc_id=tfc_id,
                route_id=f"FX.{suffix.upper()}_{index}",
                overrides_record_id=None,
            )
            capture["rules"].append(rule)
            ids.append(rule["record_id"])
        capture["support_overrides"].append(
            {
                "tfc_id": tfc_id,
                "country_code": "DEU",
                "support_status": "SUPPORTED",
                "jurisdiction_ids": ["country:DEU"],
                "rule_record_ids": ids,
                "reason_code": None,
            }
        )
    return capture


def test_generation_4_engine_and_snapshot_schemas_are_valid() -> None:
    schemas = sorted((ROOT / "contracts" / "schemas" / "v4").glob("*.schema.json"))
    assert len(schemas) >= 25
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_context_normalization_is_deterministic_and_hashes_without_client_ids() -> None:
    context = _contexts()["complete_work"]
    context["applicant"]["profile_id"] = "client-only-profile"
    context["applicant"]["field_provenance"] = {"applicant.age_years": {"raw": "omit"}}
    first = normalize_effective_context(
        context, selected_tfc_ids=[ROUTE_TFC], evaluation_date="2026-08-05"
    )
    second = normalize_effective_context(
        context, selected_tfc_ids=[ROUTE_TFC], evaluation_date="2026-08-06"
    )
    changed = copy.deepcopy(context)
    changed["applicant"]["age_years"] = 32
    third = normalize_effective_context(
        changed, selected_tfc_ids=[ROUTE_TFC], evaluation_date="2026-08-05"
    )

    assert first["applicant"]["citizenships"] == ["IND"]
    assert first["scenario"]["target_country_codes"] == ["DEU"]
    assert first["scenario"]["job_offer"]["salary"]["currency"] == "EUR"
    assert first["applicant"]["occupation"]["user_text"] == "Software engineer"
    assert "profile_id" not in first["applicant"]
    assert "field_provenance" not in first["applicant"]
    assert first["snapshot_hash"] == second["snapshot_hash"]
    assert first["snapshot_hash"] != third["snapshot_hash"]


def test_no_tfc_returns_canonical_payload_and_no_context_does_not_filter() -> None:
    engine = _engine()
    canonical = _payload()
    no_tfc = engine.assess_ranking_payload(
        canonical,
        context=_contexts()["complete_work"],
        selected_tfc_ids=[],
        evaluation_date="2026-08-05",
    )
    no_context = engine.assess_ranking_payload(
        canonical,
        context=None,
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
        filter_mode="REQUIRE_SUPPORTED_MATCH",
    )

    assert no_tfc.payload == canonical
    assert no_tfc.snapshot is None
    assert no_tfc.assessment["execution_status"] == "NO_TFC_SELECTED"
    assert no_context.payload == canonical
    assert no_context.snapshot is None
    assert no_context.assessment["profile_context_status"] == "NO_PROFILE_CONTEXT"
    assert no_context.assessment["input_required_fields"] == ["scenario.job_offer"]


def test_complete_work_matches_multiple_routes_with_bounded_detail() -> None:
    run = _run("complete_work")
    outcome = _outcome(run, "DEU")
    result = outcome["result"]

    assert outcome["common_status"] == "EVALUATED"
    assert result["match_classification"] == "SUPPORTED_ROUTE_MATCH"
    assert result["matched_route_ids"] == ["FX.HIGH_SKILL_A", "FX.HIGH_SKILL_B"]
    assert {route["classification"] for route in result["routes"]} == {"MATCH"}
    assert all(route["source_ids"] == ["fictional_route_schedule"] for route in result["routes"])
    rendered = json.dumps(run.assessment, sort_keys=True)
    assert "Software engineer" not in rendered
    assert "72000" not in rendered


def test_conditional_and_guarded_no_match_aggregation() -> None:
    conditional = _outcome(_run("conditional_work"), "DEU")["result"]
    no_match = _outcome(_run("no_match_work"), "DEU")["result"]

    assert conditional["match_classification"] == "CONDITIONAL_ROUTE_MATCH"
    assert {route["classification"] for route in conditional["routes"]} == {"CONDITIONAL"}
    assert no_match["match_classification"] == "NO_SUPPORTED_ROUTE_MATCH"
    assert no_match["route_inventory_complete"] is True
    assert no_match["legal_impossibility_disclaimer"] == NO_MATCH_DISCLAIMER
    assert no_match["matched_route_ids"] == []


def test_missing_job_offer_is_unknown_but_explicit_absence_is_evaluated() -> None:
    partial = _outcome(_run("partial_work"), "DEU")
    explicit_absence = _outcome(_run("no_match_work"), "DEU")

    assert partial["common_status"] == "INPUT_REQUIRED"
    assert partial["input_required_fields"] == ["scenario.job_offer"]
    assert explicit_absence["common_status"] == "EVALUATED"
    assert explicit_absence["result"]["match_classification"] == "NO_SUPPORTED_ROUTE_MATCH"


def test_unsupported_stale_regional_study_and_family_scenarios() -> None:
    work = _run("complete_work")
    regional = _outcome(_run("regional_work"), "DEU")["result"]
    study = _run("study")
    family = _run("family")

    assert _outcome(work, "ALB")["common_status"] == "UNSUPPORTED"
    assert _outcome(work, "USA")["common_status"] == "DESTINATION_EVIDENCE_INSUFFICIENT"
    assert _outcome(work, "USA")["reason_codes"] == ["DESTINATION_RULE_STALE"]
    assert "FX.HIGH_SKILL_A" in regional["matched_route_ids"]
    regional_route = next(
        route for route in regional["routes"] if route["route_id"] == "FX.HIGH_SKILL_A"
    )
    assert regional_route["jurisdiction_id"] == "region:DE-FX"
    assert all(
        outcome["common_status"] == "NOT_APPLICABLE"
        for country in study.assessment["countries"]
        for outcome in country["outcomes"]
    )
    assert all(
        outcome["common_status"] == "NOT_APPLICABLE"
        for country in family.assessment["countries"]
        for outcome in country["outcomes"]
    )


def test_metric_range_units_currency_period_locality_and_rounding() -> None:
    run = _run("metric_range", (METRIC_TFC,))
    outcome = _outcome(run, "AUS", METRIC_TFC)
    result = outcome["result"]

    assert outcome["common_status"] == "EVALUATED"
    assert result["result_type"] == "SCENARIO_METRIC"
    assert result["value"] is None
    assert (result["minimum"], result["maximum"]) == (1840.0, 2280.0)
    assert result["unit"] == "AUD_per_month"
    assert result["currency"] == "AUD"
    assert result["period"] == "MONTHLY"
    assert result["locality_id"] == "city:synthetic-sydney"
    assert result["rounding"] == {"mode": "HALF_UP", "decimal_places": 2}
    assert "score" not in json.dumps(result, sort_keys=True).lower()


@pytest.mark.parametrize(("field", "value"), [("currency", "USD"), ("period", "ANNUAL")])
def test_metric_mismatch_errors_name_field_ids_without_echoing_values(
    field: str, value: str
) -> None:
    context = _contexts()["metric_range"]
    context["scenario"]["housing_cost"][field] = value
    with pytest.raises(TfcAssessmentError) as captured:
        _engine().assess_ranking_payload(
            _payload(),
            context=context,
            selected_tfc_ids=[METRIC_TFC],
            evaluation_date="2026-08-05",
        )
    assert "scenario.housing_cost" in str(captured.value)
    assert value not in str(captured.value)


def test_two_tfc_kinds_are_assessed_without_cross_family_coercion() -> None:
    run = _run("metric_range", (ROUTE_TFC, METRIC_TFC))
    deu = _country(run, "DEU")["outcomes"]
    aus = _country(run, "AUS")["outcomes"]

    assert (
        next(row for row in deu if row["tfc_id"] == ROUTE_TFC)["result"]["result_type"]
        == "ROUTE_RULE"
    )
    assert (
        next(row for row in aus if row["tfc_id"] == METRIC_TFC)["result"]["result_type"]
        == "SCENARIO_METRIC"
    )
    assert run.assessment["matched_route_count"] == 2
    assert run.assessment["metric_result_count"] == 1


def test_bounded_condition_vocabulary_including_groups_and_conditional_requirement() -> None:
    context = normalize_effective_context(
        {
            "applicant": {
                "age_years": 31,
                "occupation": {"code": "2512", "mapping_state": "MAPPED"},
                "qualifications": [{"level": "MASTERS"}],
                "unknown_fields": [],
            },
            "household": {
                "partner_accompanying": True,
                "dependants": [{"role": "DEPENDENT_CHILD"}],
                "unknown_fields": [],
            },
            "scenario": {
                "target_date": "2026-10-01",
                "target_region_ids": ["region:DE-FX"],
                "job_offer": {"state": "ABSENT"},
                "unknown_fields": [],
            },
        },
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
    )
    rule = {
        "thresholds": [{"threshold_id": "age_min", "value": 25, "unit": "years"}],
        "conditions": [
            {
                "condition_id": "present",
                "condition_type": "FIELD_ABSENT",
                "field_id": "scenario.job_offer",
                "operator": "ABSENT",
                "expected_value": None,
                "threshold_id": None,
            },
            {
                "condition_id": "boolean",
                "condition_type": "FIELD_EQUALS",
                "field_id": "household.partner_accompanying",
                "operator": "EQ",
                "expected_value": True,
                "threshold_id": None,
            },
            {
                "condition_id": "threshold",
                "condition_type": "THRESHOLD",
                "field_id": "applicant.age_years",
                "operator": "GTE",
                "expected_value": None,
                "threshold_id": "age_min",
            },
            {
                "condition_id": "set_membership",
                "condition_type": "FIELD_IN_SET",
                "field_id": "applicant.age_years",
                "operator": "IN",
                "expected_value": [30, 31],
                "threshold_id": None,
            },
            {
                "condition_id": "range",
                "condition_type": "RANGE",
                "field_id": "scenario.target_date",
                "operator": "BETWEEN",
                "expected_value": ["2026-01-01", "2026-12-31"],
                "threshold_id": None,
            },
            {
                "condition_id": "taxonomy",
                "condition_type": "TAXONOMY_MEMBERSHIP",
                "field_id": "applicant.occupation",
                "operator": "IN",
                "expected_value": ["2512"],
                "threshold_id": None,
            },
            {
                "condition_id": "qualification",
                "condition_type": "QUALIFICATION_LEVEL",
                "field_id": "applicant.qualifications",
                "operator": "ANY_OF",
                "expected_value": ["MASTERS", "DOCTORATE"],
                "threshold_id": None,
            },
            {
                "condition_id": "jurisdiction",
                "condition_type": "JURISDICTION",
                "field_id": "scenario.target_region_ids",
                "operator": "ANY_OF",
                "expected_value": ["region:DE-FX"],
                "threshold_id": None,
            },
            {
                "condition_id": "conditional",
                "condition_type": "CONDITIONAL_REQUIREMENT",
                "field_id": "household.dependants",
                "operator": "PRESENT",
                "expected_value": None,
                "threshold_id": None,
                "when": {
                    "field_id": "household.partner_accompanying",
                    "operator": "EQ",
                    "expected_value": True,
                },
            },
            {
                "condition_id": "group",
                "condition_type": "GROUP",
                "field_id": None,
                "operator": "ALL_OF",
                "expected_value": None,
                "threshold_id": None,
                "group_operator": "AND",
                "child_condition_ids": ["boolean", "qualification", "jurisdiction"],
            },
            {
                "condition_id": "or_group",
                "condition_type": "GROUP",
                "field_id": None,
                "operator": "ANY_OF",
                "expected_value": None,
                "threshold_id": None,
                "group_operator": "OR",
                "child_condition_ids": ["set_membership", "range"],
            },
        ],
    }
    results = evaluate_route_conditions(rule, context)
    assert {row["status"] for row in results} == {"MET"}


def test_assessment_only_preserves_all_ranking_ofc_pcc_lsc_fields() -> None:
    engine = _engine()
    canonical = _payload()
    original = copy.deepcopy(canonical)
    run = engine.assess_ranking_payload(
        canonical,
        context=_contexts()["complete_work"],
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
    )

    assert canonical == original
    assert run.payload["rankings"] == original["rankings"]
    assert run.payload["normalized_weights"] == original["normalized_weights"]
    for key in ("coverage", "locality", "profile", "opportunity"):
        assert run.payload["assessments"][key] == original["assessments"][key]
    assert run.payload["assessments"]["feasibility"] == run.assessment
    assert all(country["no_change_affinity"] for country in run.assessment["countries"])


def test_explicit_route_filter_preserves_ties_survivor_order_and_base_values() -> None:
    engine = _engine(_capture_with_second_supported_route())
    canonical = _payload(("GBR", "CAN", "DEU", "ALB"))
    for row in canonical["rankings"]:
        row["total_score"] = 8.0
    original = copy.deepcopy(canonical)
    run = engine.assess_ranking_payload(
        canonical,
        context=_contexts()["complete_work"],
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
        filter_mode="REQUIRE_SUPPORTED_MATCH",
    )

    assert [row["country"]["country_codes"][0] for row in run.payload["rankings"]] == [
        "GBR",
        "DEU",
    ]
    assert [row["rank"] for row in run.payload["rankings"]] == [1, 2]
    assert [row["base_rank"] for row in run.payload["rankings"]] == [1, 3]
    assert [row["total_score"] for row in run.payload["rankings"]] == [8.0, 8.0]
    assert [row["contributions"] for row in run.payload["rankings"]] == [
        original["rankings"][0]["contributions"],
        original["rankings"][2]["contributions"],
    ]
    assert canonical == original


def test_no_matches_never_falls_back_and_metric_threshold_filtering_is_forbidden() -> None:
    no_matches = _engine().assess_ranking_payload(
        _payload(("DEU", "AUS", "ALB")),
        context=_contexts()["no_match_work"],
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
        filter_mode="REQUIRE_SUPPORTED_MATCH",
    )
    assert no_matches.payload["rankings"] == []
    with pytest.raises(TfcAssessmentError, match="do not permit route filtering"):
        _engine().assess_ranking_payload(
            _payload(),
            context=_contexts()["metric_range"],
            selected_tfc_ids=[METRIC_TFC],
            evaluation_date="2026-08-05",
            filter_mode="REQUIRE_SUPPORTED_MATCH",
        )


def test_snapshot_is_request_scoped_versioned_and_contains_no_raw_profile_values() -> None:
    run = _run("metric_range", (ROUTE_TFC, METRIC_TFC))
    snapshot = run.snapshot
    assert snapshot is not None
    assert snapshot["active_release_id"] == "2026-08-04.1"
    assert snapshot["tfc_release_id"] == "synthetic-phase7e-6.0"
    assert snapshot["effective_profile_context_hash"] == run.effective_context["snapshot_hash"]
    assert snapshot["persisted_server_side"] is False
    assert snapshot["policy_versions"] == {
        ROUTE_TFC: "1.0",
        METRIC_TFC: "1.0",
    }
    assert set(snapshot["source_versions"]) == {
        "fictional_formula_table",
        "fictional_route_schedule",
    }
    rendered = json.dumps(snapshot, sort_keys=True)
    assert "Software engineer" not in rendered
    assert "1400" not in rendered
    assert "3000" not in rendered
    assert not hasattr(_engine(), "snapshots")


def test_91_country_three_route_plus_metric_assessment_stays_bounded() -> None:
    capture = _capture_for_three_route_checks_and_metric()
    engine = _engine(capture)
    selected = [
        ROUTE_TFC,
        "synthetic_family_route",
        "synthetic_study_route",
        METRIC_TFC,
    ]
    payload = _payload(tuple(COUNTRY_CODES))
    result = benchmark_tfc_assessment(
        engine,
        payload,
        _contexts()["metric_range"],
        selected,
        iterations=5,
    )
    assert result["country_count"] == 91
    assert result["tfc_count"] == 4
    assert result["maximum_ms"] < 2000
