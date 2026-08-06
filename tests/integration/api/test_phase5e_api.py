import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from konsider.api.app import create_app
from konsider.api.models.v2 import (
    AssessmentsV2Response,
    ContributionV2Response,
    ProfileAssessmentResponse,
)
from konsider.api.v2_service import RecommendationService
from tests.unit.domain.test_phase5d_locality_engine import _load


@pytest.fixture
def current_client(tmp_path: Path):
    release = _load(
        tmp_path,
        [
            {
                "id": "N1",
                "scores": {"CAN": 5, "MEX": 6, "USA": 7},
            },
            {
                "id": "L1",
                "locality": True,
                "coverage": "CONDITIONAL_COMPLETE_CASE",
                "minimum_valid_country_count": 2,
                "scores": {
                    "CAN": {"a": 9, "b": 7},
                    "MEX": {"a": 8, "b": 6},
                },
            },
        ],
        countries=("CAN", "MEX", "USA"),
    )
    app = create_app(service=RecommendationService(release))
    with TestClient(app) as client:
        yield client


def test_v2_current_release_catalog_uses_clean_names_and_orthogonal_metadata(
    current_client: TestClient,
) -> None:
    response = current_client.get("/api/v2/catalog")
    assert response.status_code == 200
    body = response.json()
    assert body["api_contract_version"] == "konsider-api-2.0"
    assert "preference_presets" in body
    assert "profiles" not in body
    locality = next(item for item in body["criteria"] if item["id"] == "L1")
    assert locality["coverage"]["mode"] == "CONDITIONAL_COMPLETE_CASE"
    assert locality["scope"]["derivation"] == "AGGREGATED_FROM_LOCALITIES"
    assert locality["scope"]["locality_analysis_threshold"] == 0.6
    assert locality["scope"]["aggregation_policy_id"] == "aggregate:L1"
    assert locality["applicability"] == {"mode": "UNIVERSAL", "dimensions": []}
    assert {source["role"] for source in locality["sources"]} == {
        "PRIMARY_OBSERVATION",
        "ENTITY_UNIVERSE",
    }
    assert len(body["country_coverage"]) == 3
    usa = next(
        item for item in body["country_coverage"] if item["country"]["country_codes"] == ["USA"]
    )
    usa_locality = next(item for item in usa["criteria"] if item["criterion_id"] == "L1")
    assert usa_locality["outcome"] == "missing"
    assert usa_locality["reason_codes"]


def test_v2_ranking_exposes_locality_provenance_and_orthogonal_assessments(
    current_client: TestClient,
) -> None:
    response = current_client.post(
        "/api/v2/rankings",
        json={"weights": {"N1": 1, "L1": 0.6}, "top_k": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["resolved_preference_preset_id"] is None
    assert set(body["assessments"]) == {"coverage", "locality", "profile", "opportunity"}
    assert body["assessments"]["opportunity"]["status"] == "NO_FILTERS_ACTIVE"
    assert body["assessments"]["coverage"]["status"] == "PARTIAL_COMPLETE_CASE"
    assert body["assessments"]["locality"]["status"] == "ONE_ACTIVE_LOCALITY_CRITERION"
    profile = body["assessments"]["profile"]
    assert profile["status"] == "NO_PROFILE_CONTEXT"
    assert profile["evaluated_dimensions"] == []
    assert {reason["effect"] for reason in profile["reasons"]} == {"NOT_EVALUATED"}
    for country in body["rankings"]:
        country_profile = country["assessments"]["profile"]
        assert country_profile["status"] == "NO_PROFILE_CONTEXT"
        assert country_profile["evaluated_dimensions"] == []
        assert {reason["effect"] for reason in country_profile["reasons"]} == {"NOT_EVALUATED"}
    assert "uncertainty_status" not in body
    assert "locality_status" not in body

    locality = next(
        contribution
        for contribution in body["rankings"][0]["contributions"]
        if contribution["criterion_id"] == "L1"
    )
    assert locality["source_scope"] == "LOCALITY"
    assert locality["result_scope"] == "COUNTRY"
    assert locality["aggregation_policy"]["policy_id"] == "aggregate:L1"
    assert locality["locality_universe"]["locality_universe_id"] == "phase5d-cities-v1"
    assert len(locality["contributing_localities"]) == 2
    assert locality["observations"]
    assert locality["source_lineage_ids"] == ["lineage:L1", "lineage:universe"]

    excluded = body["assessments"]["coverage"]["excluded_countries"]
    assert [item["country"]["entity_id"] for item in excluded] == ["country:USA"]
    assert excluded[0]["final_aggregate"] is None
    unavailable = next(
        item for item in excluded[0]["criterion_evidence"] if item["criterion_id"] == "L1"
    )
    assert unavailable["outcome"] == "missing"
    assert unavailable["contribution"] is None


def test_v2_comparison_and_country_details_need_no_client_side_intersection(
    current_client: TestClient,
) -> None:
    payload = {"country_codes": ["CAN", "USA"], "weights": {"N1": 1, "L1": 0.6}}
    comparison = current_client.post("/api/v2/comparisons", json=payload)
    assert comparison.status_code == 200
    body = comparison.json()
    usa = next(row for row in body["countries"] if row["country"]["entity_id"] == "country:USA")
    assert usa["coverage_excluded"] is True
    assert usa["final_aggregate"] is None
    assert usa["rank"] is None
    l1 = next(row for row in body["criterion_rows"] if row["criterion_id"] == "L1")
    usa_cell = next(cell for cell in l1["cells"] if cell["country"]["entity_id"] == "country:USA")
    assert usa_cell["outcome"] == "missing"
    assert usa_cell["contribution"] is None

    details = current_client.post(
        "/api/v2/countries/USA/details",
        json={"weights": {"N1": 1, "L1": 0.6}},
    )
    assert details.status_code == 200
    detail = next(row for row in details.json()["criteria"] if row["criterion"]["id"] == "L1")
    assert detail["evidence"]["outcome"] == "missing"
    assert "reason_codes" in detail["evidence"]


def test_v2_rejects_legacy_aliases_and_undocumented_fields(current_client: TestClient) -> None:
    for payload in (
        {"profile_id": "equal", "top_k": 1},
        {"preference_preset_id": "equal", "profile_id": "equal", "top_k": 1},
        {"preference_preset_id": "equal", "unexpected": True, "top_k": 1},
    ):
        response = current_client.post("/api/v2/rankings", json=payload)
        assert response.status_code == 422


@pytest.mark.parametrize(
    "coverage_status",
    [
        "NO_PARTIAL_CRITERIA_ACTIVE",
        "FULL_COVERAGE",
        "PARTIAL_COMPLETE_CASE",
        "COVERAGE_LIMIT_FALLBACK",
    ],
)
@pytest.mark.parametrize(
    "locality_status",
    [
        "NO_ACTIVE_LOCALITY_CRITERIA",
        "BELOW_ANALYSIS_THRESHOLD",
        "ONE_ACTIVE_LOCALITY_CRITERION",
        "COMMON_LOCALITY_AVAILABLE",
        "PARTIAL_OVERLAP",
        "NO_COMMON_LOCALITY",
        "INSUFFICIENT_LOCALITY_EVIDENCE",
        "MIXED_COUNTRY_RESULTS",
    ],
)
def test_coverage_and_locality_statuses_are_transport_independent(
    coverage_status: str,
    locality_status: str,
) -> None:
    AssessmentsV2Response.model_validate(
        {
            "coverage": {
                "status": coverage_status,
                "policy_version": "coverage-1.0",
                "active_global_core_criterion_ids": ["N1"],
                "active_conditional_criterion_ids": [],
                "excluded_countries": [],
                "reasons": [],
            },
            "locality": {
                "status": locality_status,
                "policy_version": "locality-1.0",
                "contributing_criterion_ids": [],
                "analysis_triggered_criterion_ids": [],
                "below_threshold_criterion_ids": [],
                "analysis_thresholds": {},
                "aggregation_policy_ids": [],
                "reasons": [],
            },
            "profile": {
                "status": "NO_PROFILE_CONTEXT",
                "evaluated_dimensions": [],
                "reasons": [
                    {
                        "code": "PROFILE_CONTEXT_NOT_SUPPLIED",
                        "severity": "INFO",
                        "effect": "NOT_EVALUATED",
                    }
                ],
            },
            "opportunity": {
                "status": "NO_FILTERS_ACTIVE",
                "mode": "ALL_REQUIRED",
                "active_filter_ids": [],
                "input_ranked_country_count": 3,
                "passing_country_count": 3,
                "excluded_country_count": 0,
                "excluded_counts_by_state": {
                    "STRONG_SIGNAL_NOT_ESTABLISHED": 0,
                    "INSUFFICIENT_EVIDENCE": 0,
                },
                "per_filter": [],
                "excluded_countries": [],
                "opportunity_release_id": None,
                "evidence_policy_version": None,
                "source_bundle_version": None,
                "strict_filter_explanation": "Strict AND; no score impact.",
                "no_score_impact": True,
            },
        }
    )


def test_invalid_cross_domain_contribution_combinations_are_rejected(
    current_client: TestClient,
) -> None:
    body = current_client.post(
        "/api/v2/rankings",
        json={"weights": {"N1": 1, "L1": 0.6}, "top_k": 2},
    ).json()
    locality = next(
        contribution
        for contribution in body["rankings"][0]["contributions"]
        if contribution["criterion_id"] == "L1"
    )
    direct_with_locality = copy.deepcopy(locality)
    direct_with_locality["derivation"] = "DIRECT"
    direct_with_locality["source_scope"] = "COUNTRY"
    with pytest.raises(ValidationError):
        ContributionV2Response.model_validate(direct_with_locality)

    derived_without_policy = copy.deepcopy(locality)
    derived_without_policy["aggregation_policy"] = None
    with pytest.raises(ValidationError):
        ContributionV2Response.model_validate(derived_without_policy)


def test_profile_assessment_cannot_claim_evaluation_without_profile_input() -> None:
    with pytest.raises(ValidationError):
        ProfileAssessmentResponse.model_validate(
            {
                "status": "NO_PROFILE_CONTEXT",
                "evaluated_dimensions": ["occupation"],
                "reasons": [
                    {
                        "code": "PROFILE_CONTEXT_NOT_SUPPLIED",
                        "severity": "INFO",
                        "effect": "NOT_EVALUATED",
                    }
                ],
            }
        )

    with pytest.raises(ValidationError):
        ProfileAssessmentResponse.model_validate(
            {
                "status": "NO_PROFILE_CONTEXT",
                "evaluated_dimensions": [],
                "reasons": [
                    {
                        "code": "PROFILE_CONTEXT_NOT_SUPPLIED",
                        "severity": "INFO",
                        "effect": "ADVISORY",
                    }
                ],
            }
        )


def test_openapi_declares_only_the_final_public_routes_and_every_status() -> None:
    schema = create_app().openapi()
    assert set(schema["paths"]) == {
        "/api/v2/health",
        "/api/v2/catalog",
        "/api/v2/rankings",
        "/api/v2/comparisons",
        "/api/v2/countries/{country_code}/details",
        "/api/v2/opportunity-filters",
        "/api/v2/tfcs",
    }
    serialized = str(schema)
    for status in (
        "NO_PARTIAL_CRITERIA_ACTIVE",
        "COVERAGE_LIMIT_FALLBACK",
        "NO_ACTIVE_LOCALITY_CRITERIA",
        "COMMON_LOCALITY_AVAILABLE",
        "PARTIAL_OVERLAP",
        "NO_COMMON_LOCALITY",
        "INSUFFICIENT_LOCALITY_EVIDENCE",
        "MIXED_COUNTRY_RESULTS",
        "NO_FILTERS_ACTIVE",
        "FILTERS_APPLIED",
        "NO_COUNTRIES_MATCH",
    ):
        assert status in serialized


def test_exported_openapi_and_generated_types_match_application() -> None:
    root = Path(__file__).resolve().parents[3]
    expected = create_app().openapi()
    contract = json.loads(
        (root / "contracts" / "openapi" / "konsider-api-2.0.json").read_text(encoding="utf-8")
    )
    web_copy = json.loads(
        (root / "web" / "src" / "api" / "openapi.json").read_text(encoding="utf-8")
    )
    generated = (root / "web" / "src" / "api" / "schema.d.ts").read_text(encoding="utf-8")
    assert contract == web_copy == expected
    assert generated.startswith("// konsider-api-types-2.0\n")
    for component_name in expected["components"]["schemas"]:
        assert f'"{component_name}":' in generated
