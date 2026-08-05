from __future__ import annotations

import copy
import json
from pathlib import Path

from tests.unit.test_phase7e_tfc_assessment_engine import (
    METRIC_TFC,
    ROUTE_TFC,
    _capture,
    _capture_with_second_supported_route,
    _contexts,
    _engine,
    _outcome,
    _payload,
)

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "tests" / "fixtures" / "phase7i" / "golden-scenarios.json"
LICENSING_TFC = "synthetic_professional_licensing"


def _matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def _licensing_capture() -> dict:
    capture = _capture()
    source_definition = copy.deepcopy(capture["catalog"]["definitions"][0])
    source_policy = copy.deepcopy(capture["policy_bundles"]["policies"][0])
    source_rule = next(
        row
        for row in capture["rules"]
        if row["record_id"] == "rule:synthetic_skilled_route:deu:a:v1"
    )
    definition = copy.deepcopy(source_definition)
    definition.update(
        tfc_id=LICENSING_TFC,
        name="Fictional regulated-profession licensing check",
        original_criterion_ids=["C38"],
        user_question="Does this fictional professional context fit a modelled regulator route?",
        policy_id=f"{LICENSING_TFC}.v1",
        input_field_ids=["applicant.qualifications", "applicant.languages"],
        input_requirements=[
            {
                "field_id": "applicant.qualifications",
                "requirement": "ALWAYS_REQUIRED",
                "when_field_id": None,
                "when_equals": None,
            },
            {
                "field_id": "applicant.languages",
                "requirement": "ALWAYS_REQUIRED",
                "when_field_id": None,
                "when_equals": None,
            },
        ],
        filter_capability="ASSESS_ONLY",
        supported_profile_boundary="Synthetic qualifications and language evidence only.",
        supported_destination_codes=["DEU"],
        public_limitations=["Synthetic engine coverage; not a production licensing TFC."],
    )
    capture["catalog"]["definitions"].append(definition)
    policy = copy.deepcopy(source_policy)
    policy.update(policy_id=f"{LICENSING_TFC}.v1", tfc_id=LICENSING_TFC)
    capture["policy_bundles"]["policies"].append(policy)

    period = copy.deepcopy(source_rule["effective_period"])
    references = copy.deepcopy(source_rule["source_references"])
    common_conditions = [
        {
            "condition_id": "qualification_declared",
            "condition_type": "FIELD_PRESENT",
            "field_id": "applicant.qualifications",
            "operator": "PRESENT",
            "expected_value": None,
            "threshold_id": None,
        },
        {
            "condition_id": "language_evidence_declared",
            "condition_type": "FIELD_PRESENT",
            "field_id": "applicant.languages",
            "operator": "PRESENT",
            "expected_value": None,
            "threshold_id": None,
        },
    ]
    clear = {
        **copy.deepcopy(source_rule),
        "record_id": "rule:synthetic_professional_licensing:deu:clear:v1",
        "tfc_id": LICENSING_TFC,
        "route_id": "FX.LICENSE.CLEAR",
        "route_name": "Fictional national direct-recognition route",
        "conditions": [
            *copy.deepcopy(common_conditions),
            {
                "condition_id": "direct_recognition_age_band",
                "condition_type": "THRESHOLD",
                "field_id": "applicant.age_years",
                "operator": "LTE",
                "expected_value": None,
                "threshold_id": "direct_maximum_age",
            },
        ],
        "thresholds": [{"threshold_id": "direct_maximum_age", "value": 30, "unit": "years"}],
        "effective_period": period,
        "source_references": references,
    }
    conditional = {
        **copy.deepcopy(source_rule),
        "record_id": "rule:synthetic_professional_licensing:deu:conditional:v1",
        "tfc_id": LICENSING_TFC,
        "route_id": "FX.LICENSE.CONDITIONAL",
        "route_name": "Fictional regulator-confirmation route",
        "evaluation_boundary": "CONDITIONAL_EXTERNAL_CONFIRMATION_REQUIRED",
        "conditions": [
            *copy.deepcopy(common_conditions),
            {
                "condition_id": "conditional_age_band",
                "condition_type": "THRESHOLD",
                "field_id": "applicant.age_years",
                "operator": "LTE",
                "expected_value": None,
                "threshold_id": "conditional_maximum_age",
            },
        ],
        "thresholds": [{"threshold_id": "conditional_maximum_age", "value": 55, "unit": "years"}],
        "effective_period": copy.deepcopy(period),
        "source_references": copy.deepcopy(references),
    }
    regional = {
        **copy.deepcopy(conditional),
        "record_id": "rule:synthetic_professional_licensing:deu:region:v1",
        "route_name": "Fictional regional regulator route",
        "jurisdiction_id": "region:DE-FX",
        "overrides_record_id": conditional["record_id"],
        "evaluation_boundary": "FULLY_MACHINE_EVALUABLE",
        "conditions": copy.deepcopy(common_conditions),
        "thresholds": [],
    }
    capture["rules"].extend([clear, conditional, regional])
    capture["support_overrides"].append(
        {
            "tfc_id": LICENSING_TFC,
            "country_code": "DEU",
            "support_status": "SUPPORTED",
            "jurisdiction_ids": ["country:DEU", "region:DE-FX"],
            "rule_record_ids": [
                clear["record_id"],
                conditional["record_id"],
                regional["record_id"],
            ],
            "reason_code": None,
        }
    )
    return capture


def _licensing_context(*, age: int = 28, regional: bool = False, language: bool = True) -> dict:
    applicant = {
        "age_years": age,
        "occupation": {
            "user_text": "Fictional registered nurse",
            "code": "2221",
            "mapping_state": "MAPPED",
        },
        "qualifications": [{"level": "BACHELORS", "recognition_state": "NOT_ASSESSED"}],
        "unknown_fields": [],
    }
    if language:
        applicant["languages"] = [
            {"language": "English", "evidence_type": "NAMED_TEST", "level_or_score": "C1"}
        ]
    return {
        "applicant": applicant,
        "household": {"partner_status": "NONE", "dependants": [], "unknown_fields": []},
        "scenario": {
            "purpose": "WORK",
            "target_country_codes": ["DEU"],
            "target_region_ids": ["region:DE-FX"] if regional else [],
            "target_locality_ids": [],
            "relocation_composition": "APPLICANT_ONLY",
            "unknown_fields": [],
        },
    }


def test_golden_matrix_covers_every_required_phase7i_dimension() -> None:
    matrix = _matrix()
    scenarios = {row["id"]: row for row in matrix["scenarios"]}
    tags = {tag for row in scenarios.values() for tag in row["tags"]}
    assert set(matrix["fictional_profiles"]) == {
        "work_applicant",
        "regulated_professional",
        "international_student",
        "family_relocation",
    }
    assert {
        "CAREER_OFC",
        "CARE_OFC",
        "EDUCATION_OFC",
        "MISSING_INPUT",
        "LICENSING_UNSUPPORTED",
        "OFC_STRICT_AND",
        "PCC_ACTIVE",
        "TWO_LSCS",
        "EXPLICIT_FILTER",
        "MOBILE_UI",
        "TWO_TFC_KINDS",
    } <= tags
    assert all(
        row["surface"] == "SYNTHETIC_ENGINE_ONLY"
        for row in scenarios.values()
        if row["id"].startswith("licensing_")
    )


def test_synthetic_licensing_matrix_covers_match_conditional_regional_and_missing_input() -> None:
    engine = _engine(_licensing_capture())

    def run(context: dict):
        return engine.assess_ranking_payload(
            _payload(("DEU", "ALB")),
            context=context,
            selected_tfc_ids=[LICENSING_TFC],
            evaluation_date="2026-08-05",
        )

    matched = _outcome(run(_licensing_context()), "DEU", LICENSING_TFC)
    conditional = _outcome(run(_licensing_context(age=40)), "DEU", LICENSING_TFC)
    no_match = _outcome(run(_licensing_context(age=60)), "DEU", LICENSING_TFC)
    regional = _outcome(run(_licensing_context(age=60, regional=True)), "DEU", LICENSING_TFC)
    missing = _outcome(run(_licensing_context(language=False)), "DEU", LICENSING_TFC)
    unsupported = _outcome(run(_licensing_context()), "ALB", LICENSING_TFC)

    assert matched["result"]["match_classification"] == "SUPPORTED_ROUTE_MATCH"
    assert conditional["result"]["match_classification"] == "CONDITIONAL_ROUTE_MATCH"
    assert no_match["result"]["match_classification"] == "NO_SUPPORTED_ROUTE_MATCH"
    assert regional["result"]["matched_route_ids"] == ["FX.LICENSE.CONDITIONAL"]
    regional_route = next(
        route
        for route in regional["result"]["routes"]
        if route["route_id"] == "FX.LICENSE.CONDITIONAL"
    )
    assert regional_route["jurisdiction_id"] == "region:DE-FX"
    assert missing["common_status"] == "INPUT_REQUIRED"
    assert missing["input_required_fields"] == ["applicant.languages"]
    assert unsupported["common_status"] == "UNSUPPORTED"


def test_synthetic_locality_metric_and_explicit_filter_preserve_country_ranking() -> None:
    canonical = _payload(("GBR", "CAN", "DEU", "ALB"))
    for row in canonical["rankings"]:
        row["total_score"] = 8.0
    filtered = _engine(_capture_with_second_supported_route()).assess_ranking_payload(
        canonical,
        context=_contexts()["complete_work"],
        selected_tfc_ids=[ROUTE_TFC],
        evaluation_date="2026-08-05",
        filter_mode="REQUIRE_SUPPORTED_MATCH",
    )
    assert [row["country"]["country_codes"][0] for row in filtered.payload["rankings"]] == [
        "GBR",
        "DEU",
    ]
    assert [row["base_rank"] for row in filtered.payload["rankings"]] == [1, 3]
    assert [row["total_score"] for row in filtered.payload["rankings"]] == [8.0, 8.0]
    assert canonical["rankings"][1]["country"]["country_codes"] == ["CAN"]

    metric_canonical = _payload()
    metric = _engine().assess_ranking_payload(
        metric_canonical,
        context=_contexts()["metric_range"],
        selected_tfc_ids=[METRIC_TFC],
        evaluation_date="2026-08-05",
    )
    outcome = _outcome(metric, "AUS", METRIC_TFC)
    assert outcome["result"]["locality_id"] == "city:synthetic-sydney"
    assert (outcome["result"]["minimum"], outcome["result"]["maximum"]) == (1840.0, 2280.0)
    assert metric.payload["rankings"] == metric_canonical["rankings"]


def test_same_applicant_synthetic_scenarios_create_distinct_snapshots() -> None:
    base = _contexts()["complete_work"]
    scenarios = []
    for purpose in ("WORK", "FAMILY", "STUDY"):
        context = copy.deepcopy(base)
        context["scenario"]["purpose"] = purpose
        scenarios.append(context)
    assert all(context["applicant"] == base["applicant"] for context in scenarios)

    runs = [
        _engine().assess_ranking_payload(
            _payload(),
            context=context,
            selected_tfc_ids=[ROUTE_TFC],
            evaluation_date="2026-08-05",
        )
        for context in scenarios
    ]
    assert len({run.snapshot["effective_profile_context_hash"] for run in runs}) == 3
    assert all(run.snapshot["persisted_server_side"] is False for run in runs)
