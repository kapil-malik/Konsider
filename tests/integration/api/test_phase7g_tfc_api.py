from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.models.v2 import TfcMetricResultV2Response
from konsider.api.tfc_service import TfcApiService
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = (
    ROOT
    / "data"
    / "reports"
    / "phase7f-2026-08-05"
    / "staged-release"
    / "phase7f-first-wave-2026-08-05.6.0"
)
TFC_IDS = {
    "skilled_work_route_feasibility",
    "family_accompaniment_reunification",
    "post_study_work_pathway",
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    release = CurrentReleaseRepository(ROOT / "data" / "releases").load(
        ROOT / "data" / "releases" / "2026-08-04.1"
    )
    opportunity = OpportunityFilterService.from_release(release.path, release.manifest)
    tfc = TfcApiService.from_candidate(CANDIDATE, release.manifest)
    service = RecommendationService(release, opportunity, tfc)
    with TestClient(create_app(service=service)) as current:
        yield current


def _work_selection(*, include_offer: bool = True, mode: str = "ASSESS_ONLY") -> dict:
    scenario = {
        "purpose": "WORK",
        "target_country_codes": ["DEU"],
        "target_date": "2026-08-05",
        "relocation_composition": "APPLICANT_ONLY",
    }
    if include_offer:
        scenario["job_offer"] = {"state": "PRESENT"}
    return {
        "tfc_ids": ["skilled_work_route_feasibility"],
        "mode": mode,
        "profile_context": {
            "citizenships": ["IND"],
            "occupation": {
                "user_text": "Fictional systems analyst",
                "taxonomy_id": "isco08",
                "taxonomy_version": "2008",
                "code": "2511",
                "mapping_state": "MAPPED",
            },
            "qualifications": [{"level": "MASTERS"}],
        },
        "scenario_context": scenario,
    }


def _country(assessment: dict, code: str) -> dict:
    return next(row for row in assessment["countries"] if row["country_code"] == code)


def test_catalog_exposes_only_the_frozen_first_wave_and_privacy_contract(
    client: TestClient,
) -> None:
    response = client.get("/api/v2/tfcs")
    assert response.status_code == 200
    body = response.json()
    assert body["release_status"] == "draft"
    assert body["activation_authorized"] is False
    assert body["selection_is_explicit"] is True
    assert body["persisted_server_side"] is False
    assert body["no_score_impact"] is True
    assert {row["id"] for row in body["definitions"]} == TFC_IDS
    assert {row["check_kind"] for row in body["definitions"]} == {"RULE_ROUTE_MATCH"}
    assert all(row["source_summary"] for row in body["definitions"])
    fields = {row["field_id"]: row for row in body["field_registry"]}
    assert fields["applicant.citizenships"]["sensitivity"] == "HIGH_PERSONAL"
    assert all(row["default_retention"] == "NEVER_RETAIN_BY_DEFAULT" for row in fields.values())


def test_candidate_is_still_non_active_and_bound_to_the_active_release_base() -> None:
    manifest = json.loads((CANDIDATE / "manifest.json").read_text(encoding="utf-8"))
    active = json.loads((ROOT / "data" / "releases" / "active.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "draft"
    assert manifest["activation_authorized"] is False
    assert active["release_id"] == "2026-08-05.1"
    published = json.loads(
        (ROOT / "data" / "releases" / active["release_id"] / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["base_release"] == published["base_release"]


def test_omitted_and_empty_tfc_selection_are_exactly_legacy_compatible(
    client: TestClient,
) -> None:
    omitted = client.post("/api/v2/rankings", json={"top_k": 5})
    empty = client.post(
        "/api/v2/rankings",
        json={"top_k": 5, "feasibility": {"tfc_ids": []}},
    )
    assert omitted.status_code == empty.status_code == 200
    assert omitted.json() == empty.json()
    assert "feasibility" not in omitted.json()["assessments"]
    assert all("feasibility" not in row["assessments"] for row in omitted.json()["rankings"])


def test_selected_tfc_without_context_is_explicitly_not_executed(client: TestClient) -> None:
    response = client.post(
        "/api/v2/rankings",
        json={
            "top_k": 3,
            "feasibility": {"tfc_ids": ["skilled_work_route_feasibility"]},
        },
    )
    assert response.status_code == 200
    feasibility = response.json()["assessments"]["feasibility"]
    assert feasibility["profile_context_status"] == "NO_PROFILE_CONTEXT"
    assert feasibility["execution_status"] == "NOT_EXECUTED_NO_CONTEXT"
    assert feasibility["countries"] == []
    assert feasibility["snapshot"] is None


def test_complete_profile_returns_route_evidence_without_changing_affinity_or_rank(
    client: TestClient,
) -> None:
    baseline = client.post("/api/v2/rankings", json={"top_k": 83}).json()
    response = client.post(
        "/api/v2/rankings",
        json={"top_k": 83, "feasibility": _work_selection()},
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    body = response.json()
    assessment = body["assessments"]["feasibility"]
    aus = _country(assessment, "AUS")
    outcome = aus["outcomes"][0]
    assert assessment["execution_status"] == "EXECUTED"
    assert outcome["common_status"] == "EVALUATED"
    assert outcome["result"]["result_type"] == "ROUTE_RULE"
    assert outcome["result"]["routes"]
    assert aus["affinity_score_before"] == aus["affinity_score_after"]
    assert assessment["no_change_affinity"] is True
    assert [(row["rank"], row["total_score"]) for row in body["rankings"]] == [
        (row["rank"], row["total_score"]) for row in baseline["rankings"]
    ]
    rendered = json.dumps(body)
    assert "Fictional systems analyst" not in rendered
    assert assessment["snapshot"]["persisted_server_side"] is False
    assert assessment["profile_context_summary"]["returned_profile_values"] is False


def test_unknown_field_and_explicit_absence_remain_distinct(client: TestClient) -> None:
    partial = client.post(
        "/api/v2/rankings",
        json={"top_k": 83, "feasibility": _work_selection(include_offer=False)},
    ).json()["assessments"]["feasibility"]
    absent_selection = _work_selection(include_offer=True)
    absent_selection["scenario_context"]["job_offer"] = {"state": "ABSENT"}
    explicit = client.post(
        "/api/v2/rankings",
        json={"top_k": 83, "feasibility": absent_selection},
    ).json()["assessments"]["feasibility"]
    assert _country(partial, "AUS")["outcomes"][0]["common_status"] == "INPUT_REQUIRED"
    assert (
        _country(explicit, "AUS")["outcomes"][0]["common_status"]
        == "DESTINATION_EVIDENCE_INSUFFICIENT"
    )


def test_unsupported_destination_and_missing_target_date_are_typed_outcomes(
    client: TestClient,
) -> None:
    unsupported = client.post(
        "/api/v2/rankings",
        json={"top_k": 83, "feasibility": _work_selection()},
    ).json()["assessments"]["feasibility"]
    assert _country(unsupported, "ALB")["outcomes"][0]["common_status"] == "UNSUPPORTED"
    selection = _work_selection()
    selection["scenario_context"].pop("target_date")
    partial = client.post("/api/v2/rankings", json={"top_k": 83, "feasibility": selection})
    assert partial.status_code == 200
    outcome = _country(partial.json()["assessments"]["feasibility"], "DEU")["outcomes"][0]
    assert outcome["common_status"] == "INPUT_REQUIRED"
    assert "scenario.target_date" in outcome["input_required_fields"]


def test_opportunity_filters_and_tfc_assessment_compose_without_score_changes(
    client: TestClient,
) -> None:
    request = {
        "top_k": 10,
        "opportunity_filters": {"required_filter_ids": ["technology_software_opportunity"]},
    }
    baseline = client.post("/api/v2/rankings", json=request).json()
    assessed = client.post(
        "/api/v2/rankings", json={**request, "feasibility": _work_selection()}
    ).json()
    assessed_order = [
        (row["country"]["entity_id"], row["rank"], row["total_score"])
        for row in assessed["rankings"]
    ]
    assert assessed_order == [
        (row["country"]["entity_id"], row["rank"], row["total_score"])
        for row in baseline["rankings"]
    ]
    assert assessed["assessments"]["opportunity"] == baseline["assessments"]["opportunity"]
    for name in ("coverage", "locality", "profile"):
        assert assessed["assessments"][name] == baseline["assessments"][name]


def test_family_and_post_study_checks_serialize_route_results(client: TestClient) -> None:
    family = {
        "tfc_ids": ["family_accompaniment_reunification"],
        "household_context": {
            "partner_status": "SPOUSE",
            "partner_accompanying": True,
            "dependants": [{"role": "DEPENDENT_CHILD", "relocating": True, "age_band": "UNDER_18"}],
        },
        "scenario_context": {
            "purpose": "FAMILY",
            "target_date": "2026-08-05",
            "target_country_codes": ["AUS"],
            "primary_route_id": "AU.SID.482",
            "relocation_composition": "WITH_PARTNER_AND_DEPENDANTS",
        },
    }
    study = {
        "tfc_ids": ["post_study_work_pathway"],
        "profile_context": {"citizenships": ["IND"]},
        "scenario_context": {
            "purpose": "STUDY",
            "target_date": "2026-08-05",
            "target_country_codes": ["AUS"],
            "intended_study": {
                "institution": {"user_text": "Fictional University", "mapping_state": "UNRESOLVED"},
                "qualification_level": "MASTERS",
                "field": {"user_text": "Fictional Computing", "mapping_state": "UNRESOLVED"},
                "duration_months": 24,
                "mode": "IN_PERSON",
                "completion_date": "2027-06-30",
                "completion_state": "PLANNED",
            },
        },
    }
    for selection in (family, study):
        response = client.post("/api/v2/rankings", json={"top_k": 83, "feasibility": selection})
        assert response.status_code == 200
        outcome = _country(response.json()["assessments"]["feasibility"], "AUS")["outcomes"][0]
        assert outcome["common_status"] == "EVALUATED"
        assert outcome["result"]["result_type"] == "ROUTE_RULE"


def test_metric_result_union_serializes_without_a_live_metric_candidate() -> None:
    result = TfcMetricResultV2Response.model_validate(
        {
            "result_type": "SCENARIO_METRIC",
            "metric_id": "fictional-monthly-budget",
            "formula_type": "ADDITIVE",
            "value": 2500,
            "minimum": 2500,
            "maximum": 2500,
            "unit": "currency",
            "currency": "EUR",
            "period": "MONTHLY",
            "components": [],
            "assumptions": ["Fictional contract fixture only"],
            "rounding": {"mode": "HALF_UP", "decimal_places": 0},
            "locality_id": None,
            "source_ids": ["fictional-source"],
            "effective_from": "2026-08-05",
            "effective_to": None,
            "evidence_quality": "HIGH",
        }
    )
    assert result.model_dump(mode="json")["result_type"] == "SCENARIO_METRIC"


def test_comparison_and_details_return_the_same_country_assessment(client: TestClient) -> None:
    selection = _work_selection()
    comparison = client.post(
        "/api/v2/comparisons",
        json={"country_codes": ["DEU", "CAN"], "feasibility": selection},
    )
    details = client.post(
        "/api/v2/countries/DEU/details",
        json={"feasibility": selection},
    )
    assert comparison.status_code == details.status_code == 200
    compared = next(
        row for row in comparison.json()["countries"] if row["country"]["country_codes"] == ["DEU"]
    )
    assert compared["assessments"]["feasibility"] == details.json()["feasibility"]


@pytest.mark.parametrize(
    ("feasibility", "code"),
    [
        ({"tfc_ids": ["not_a_tfc"]}, "selected_tfc_unavailable"),
        (
            {
                **_work_selection(mode="REQUIRE_SUPPORTED_MATCH"),
            },
            "feasibility_filter_not_allowed",
        ),
    ],
)
def test_stable_selection_errors(client: TestClient, feasibility: dict, code: str) -> None:
    response = client.post("/api/v2/rankings", json={"top_k": 3, "feasibility": feasibility})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == code


def test_unsupported_taxonomy_and_extra_profile_fields_are_rejected_without_values(
    client: TestClient,
) -> None:
    taxonomy = _work_selection()
    taxonomy["profile_context"]["occupation"]["taxonomy_version"] = "fictional-secret-v9"
    response = client.post("/api/v2/rankings", json={"top_k": 3, "feasibility": taxonomy})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_taxonomy_version"
    assert "fictional-secret-v9" not in response.text

    extra = _work_selection()
    extra["profile_context"]["private_note"] = "do-not-echo-this"
    response = client.post("/api/v2/rankings", json={"top_k": 3, "feasibility": extra})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_profile_field"
    assert "do-not-echo-this" not in response.text


def test_unsupported_mode_and_logs_do_not_echo_profile_values(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    response = client.post(
        "/api/v2/rankings",
        json={
            "top_k": 3,
            "feasibility": {
                **_work_selection(),
                "mode": "Fictional secret mode",
            },
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_feasibility_mode"
    assert "Fictional secret mode" not in response.text
    assert "Fictional systems analyst" not in caplog.text
    assert "Fictional secret mode" not in caplog.text
    assert response.headers["cache-control"] == "private, no-store"


def test_unavailable_candidate_does_not_break_legacy_rankings() -> None:
    release = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    opportunity = OpportunityFilterService.from_release(release.path, release.manifest)
    service = RecommendationService(release, opportunity, TfcApiService.unavailable())
    with TestClient(create_app(service=service)) as current:
        assert current.post("/api/v2/rankings", json={"top_k": 3}).status_code == 200
        assert current.get("/api/v2/tfcs").status_code == 503
        selected = current.post(
            "/api/v2/rankings",
            json={"top_k": 3, "feasibility": {"tfc_ids": ["skilled_work_route_feasibility"]}},
        )
        assert selected.status_code == 503
        assert selected.json()["error"]["code"] == "tfc_release_unavailable"
