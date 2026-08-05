from __future__ import annotations

import copy
import json

import pytest
from fastapi.testclient import TestClient

from konsider.api.app import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(create_app()) as current:
        yield current


def _work_selection(*, offer_state: str = "PRESENT") -> dict:
    return {
        "tfc_ids": ["skilled_work_route_feasibility"],
        "mode": "ASSESS_ONLY",
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
        "scenario_context": {
            "purpose": "WORK",
            "target_country_codes": ["DEU"],
            "target_date": "2026-08-05",
            "job_offer": {"state": offer_state},
            "relocation_composition": "APPLICANT_ONLY",
        },
    }


def _family_selection() -> dict:
    return {
        "tfc_ids": ["family_accompaniment_reunification"],
        "mode": "ASSESS_ONLY",
        "profile_context": copy.deepcopy(_work_selection()["profile_context"]),
        "household_context": {
            "partner_status": "SPOUSE",
            "partner_accompanying": True,
            "dependants": [{"role": "DEPENDENT_CHILD", "relocating": True, "age_band": "UNDER_18"}],
        },
        "scenario_context": {
            "purpose": "FAMILY",
            "target_country_codes": ["AUS"],
            "target_date": "2026-08-05",
            "primary_route_id": "AU.SID.482",
            "relocation_composition": "WITH_PARTNER_AND_DEPENDANTS",
        },
    }


def _study_selection(*, include_study: bool = True) -> dict:
    scenario = {
        "purpose": "STUDY",
        "target_country_codes": ["AUS"],
        "target_date": "2026-08-05",
        "relocation_composition": "APPLICANT_ONLY",
    }
    if include_study:
        scenario["intended_study"] = {
            "institution": {
                "user_text": "Fictional University",
                "mapping_state": "UNRESOLVED",
            },
            "qualification_level": "MASTERS",
            "field": {
                "user_text": "Fictional Computing",
                "mapping_state": "UNRESOLVED",
            },
            "duration_months": 24,
            "mode": "IN_PERSON",
            "completion_date": "2027-06-30",
            "completion_state": "PLANNED",
        }
    return {
        "tfc_ids": ["post_study_work_pathway"],
        "mode": "ASSESS_ONLY",
        "profile_context": copy.deepcopy(_work_selection()["profile_context"]),
        "scenario_context": scenario,
    }


def _country(payload: dict, code: str) -> dict:
    return next(row for row in payload["countries"] if row["country"]["country_codes"] == [code])


def _tfc_country(payload: dict, code: str) -> dict:
    return next(row for row in payload["countries"] if row["country_code"] == code)


def _ranking_signature(payload: dict) -> list[tuple]:
    return [
        (
            row["country"]["entity_id"],
            row["rank"],
            row["base_rank"],
            row["total_score"],
            row["contributions"],
        )
        for row in payload["rankings"]
    ]


def test_real_pcc_two_lsc_ofc_and_tfc_request_is_strictly_orthogonal(
    client: TestClient,
) -> None:
    request = {
        "weights": {
            "political_stability": 0.4,
            "overall_job_market_opportunity": 0.8,
            "C66": 1,
            "C67": 1,
        },
        "top_k": 20,
        "opportunity_filters": {
            "mode": "ALL_REQUIRED",
            "required_filter_ids": ["technology_software_opportunity"],
        },
    }
    baseline_response = client.post("/api/v2/rankings", json=request)
    assessed_response = client.post(
        "/api/v2/rankings",
        json={**request, "feasibility": _work_selection()},
    )
    assert baseline_response.status_code == assessed_response.status_code == 200
    baseline = baseline_response.json()
    assessed = assessed_response.json()

    assert baseline["assessments"]["coverage"]["status"] == "PARTIAL_COMPLETE_CASE"
    assert baseline["assessments"]["locality"]["status"] == "MIXED_COUNTRY_RESULTS"
    assert baseline["assessments"]["opportunity"]["status"] == "FILTERS_APPLIED"
    assert assessed["normalized_weights"] == baseline["normalized_weights"]
    assert _ranking_signature(assessed) == _ranking_signature(baseline)
    for dimension in ("coverage", "locality", "opportunity", "profile"):
        assert assessed["assessments"][dimension] == baseline["assessments"][dimension]
    for assessed_row, baseline_row in zip(assessed["rankings"], baseline["rankings"], strict=True):
        for dimension in ("locality", "opportunity", "profile"):
            assert assessed_row["assessments"][dimension] == baseline_row["assessments"][dimension]
        assert assessed_row["assessments"]["feasibility"]["no_change_affinity"] is True

    feasibility = assessed["assessments"]["feasibility"]
    assert feasibility["filter_mode"] == "ASSESS_ONLY"
    assert feasibility["no_change_affinity"] is True
    assert {row["country_code"] for row in feasibility["countries"]} == {
        row["country"]["country_codes"][0] for row in assessed["rankings"]
    }


def test_pcc_exclusions_are_not_revived_or_given_partial_aggregates(
    client: TestClient,
) -> None:
    request = {
        "weights": {"overall_job_market_opportunity": 1},
        "top_k": 88,
    }
    baseline = client.post("/api/v2/rankings", json=request).json()
    assessed = client.post(
        "/api/v2/rankings",
        json={**request, "feasibility": _work_selection()},
    ).json()
    excluded_codes = {
        row["country"]["country_codes"][0]
        for row in baseline["assessments"]["coverage"]["excluded_countries"]
    }
    assert excluded_codes == {"ATG", "GRD", "UKR"}
    assert assessed["assessments"]["coverage"] == baseline["assessments"]["coverage"]
    assert _ranking_signature(assessed) == _ranking_signature(baseline)
    assert excluded_codes.isdisjoint(
        row["country_code"] for row in assessed["assessments"]["feasibility"]["countries"]
    )

    comparison = client.post(
        "/api/v2/comparisons",
        json={
            "country_codes": ["ATG", "DEU"],
            "weights": request["weights"],
            "feasibility": _work_selection(),
        },
    )
    assert comparison.status_code == 200
    compared = comparison.json()
    excluded = _country(compared, "ATG")
    supported = _country(compared, "DEU")
    assert excluded["coverage_excluded"] is True
    assert excluded["rank"] is excluded["base_rank"] is excluded["final_aggregate"] is None
    assert "feasibility" not in excluded["assessments"]
    assert supported["coverage_excluded"] is False
    assert supported["assessments"]["feasibility"]["outcomes"]


def test_ecosystem_and_route_evidence_can_disagree_without_contradiction(
    client: TestClient,
) -> None:
    route_without_ecosystem = client.post(
        "/api/v2/comparisons",
        json={
            "country_codes": ["DEU", "AUS"],
            "opportunity_filters": {
                "mode": "ALL_REQUIRED",
                "required_filter_ids": ["skilled_trades_construction_opportunity"],
            },
            "feasibility": _work_selection(),
        },
    )
    assert route_without_ecosystem.status_code == 200
    deu = _country(route_without_ecosystem.json(), "DEU")
    assert deu["opportunity_excluded"] is True
    assert deu["rank"] is None
    assert deu["base_rank"] is not None
    assert deu["final_aggregate"] is not None
    assert deu["assessments"]["opportunity"]["passes"] is False
    route = deu["assessments"]["feasibility"]["outcomes"][0]["result"]
    assert route["match_classification"] in {
        "SUPPORTED_ROUTE_MATCH",
        "CONDITIONAL_ROUTE_MATCH",
    }
    assert all(item["source_ids"] and item["effective_from"] for item in route["routes"])

    ecosystem_without_route = client.post(
        "/api/v2/comparisons",
        json={
            "country_codes": ["DEU", "AUS"],
            "opportunity_filters": {
                "mode": "ALL_REQUIRED",
                "required_filter_ids": ["technology_software_opportunity"],
            },
            "feasibility": _work_selection(offer_state="ABSENT"),
        },
    )
    assert ecosystem_without_route.status_code == 200
    deu = _country(ecosystem_without_route.json(), "DEU")
    assert deu["assessments"]["opportunity"]["passes"] is True
    outcome = deu["assessments"]["feasibility"]["outcomes"][0]
    assert outcome["common_status"] in {"EVALUATED", "DESTINATION_EVIDENCE_INSUFFICIENT"}
    if outcome["common_status"] == "EVALUATED":
        assert outcome["result"]["match_classification"] != "SUPPORTED_ROUTE_MATCH"


def test_education_ecosystem_and_post_study_route_keep_admission_out_of_scope(
    client: TestClient,
) -> None:
    complete = client.post(
        "/api/v2/comparisons",
        json={
            "country_codes": ["AUS", "DEU"],
            "opportunity_filters": {
                "mode": "ALL_REQUIRED",
                "required_filter_ids": ["computer_science_ict_education_opportunity"],
            },
            "feasibility": _study_selection(),
        },
    )
    assert complete.status_code == 200
    body = complete.json()
    aus = _country(body, "AUS")
    assert aus["assessments"]["opportunity"]["passes"] is True
    outcome = aus["assessments"]["feasibility"]["outcomes"][0]
    assert outcome["common_status"] == "EVALUATED"
    assert outcome["result"]["routes"]
    assert all("admission" not in field.lower() for field in outcome["input_required_fields"])
    assert all(
        "admission" not in condition["condition_id"].lower()
        for route in outcome["result"]["routes"]
        for condition in route["conditions"]
    )
    assert any(
        "admission" in limitation.lower()
        for evidence in aus["assessments"]["opportunity"]["filter_evidence"]
        for limitation in evidence["limitations"]
    )

    missing = client.post(
        "/api/v2/rankings",
        json={"top_k": 10, "feasibility": _study_selection(include_study=False)},
    )
    assert missing.status_code == 200
    assessment = missing.json()["assessments"]["feasibility"]
    assert "scenario.intended_study" in assessment["input_required_fields"]
    assert _tfc_country(assessment, "AUS")["outcomes"][0]["common_status"] == "INPUT_REQUIRED"


def test_same_applicant_uses_distinct_work_family_and_study_snapshots(
    client: TestClient,
) -> None:
    selections = (_work_selection(), _family_selection(), _study_selection())
    applicant = selections[0]["profile_context"]
    assert all(selection["profile_context"] == applicant for selection in selections)

    assessments = []
    for selection in selections:
        response = client.post(
            "/api/v2/rankings",
            json={"top_k": 20, "feasibility": selection},
        )
        assert response.status_code == 200
        assessments.append(response.json()["assessments"]["feasibility"])

    hashes = {
        assessment["snapshot"]["effective_profile_context_hash"] for assessment in assessments
    }
    assert len(hashes) == 3
    assert [assessment["selected_tfc_ids"] for assessment in assessments] == [
        ["skilled_work_route_feasibility"],
        ["family_accompaniment_reunification"],
        ["post_study_work_pathway"],
    ]
    rendered = json.dumps(assessments)
    assert "Fictional systems analyst" not in rendered
    assert all(
        assessment["snapshot"]["persisted_server_side"] is False for assessment in assessments
    )


def test_live_first_wave_rejects_explicit_feasibility_filtering(
    client: TestClient,
) -> None:
    selection = _work_selection()
    selection["mode"] = "REQUIRE_SUPPORTED_MATCH"
    response = client.post(
        "/api/v2/rankings",
        json={"top_k": 10, "feasibility": selection},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "feasibility_filter_not_allowed"
