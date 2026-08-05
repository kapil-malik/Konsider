from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.v2_service import RecommendationService
from konsider.ingestion import phase6_opportunity_api_candidate as phase6g
from konsider.ingestion.current_release import CurrentReleaseRepository
from tests.unit.domain.test_phase5d_locality_engine import _load

ROOT = Path(__file__).resolve().parents[3]
STAGED = ROOT / "data" / "reports" / "phase6g-2026-08-03" / "staged-release"
GLOBAL_WEIGHTS = {"political_stability": 1}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.fixture(scope="module")
def opportunity_service() -> OpportunityFilterService:
    return OpportunityFilterService.from_directory(STAGED)


@pytest.fixture(scope="module")
def service(opportunity_service: OpportunityFilterService) -> RecommendationService:
    release = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    return RecommendationService(release, opportunity_service)


@pytest.fixture(scope="module")
def client(service: RecommendationService):
    with TestClient(create_app(service=service)) as current:
        yield current


def _selection(*filter_ids: str) -> dict:
    return {
        "mode": "ALL_REQUIRED",
        "required_filter_ids": list(filter_ids),
    }


def test_phase6g_candidate_is_draft_complete_and_does_not_change_active_pointer() -> None:
    manifest = _json(STAGED / "candidate-release-manifest.json")
    catalog = _json(STAGED / "opportunity-filter-catalog.json")
    evidence = _jsonl(STAGED / "opportunity-filter-evidence.jsonl")
    assert phase6g.verify_phase6f_inputs()
    assert manifest["status"] == "draft"
    assert manifest["release_id"] == "phase6g-api-2026-08-03.1"
    assert catalog["activation_status"] == "ACTIVE"
    assert len(catalog["definitions"]) == 9
    assert all(
        row["active"] and row["availability"] == "AVAILABLE" for row in catalog["definitions"]
    )
    assert (
        len(evidence) == len({(row["filter_id"], row["country_code"]) for row in evidence}) == 819
    )
    active = _json(ROOT / "data" / "releases" / "active.json")
    assert active == {
        "release_id": "2026-08-05.1",
        "schema_version": "konsider-release-6.0",
    }


def test_phase6g_candidate_regeneration_is_byte_identical() -> None:
    report = STAGED.parent
    with tempfile.TemporaryDirectory(dir=ROOT / "data" / "reports") as temporary:
        generated = Path(temporary) / "phase6g"
        phase6g.build_opportunity_api_candidate(generated)
        assert _tree_bytes(generated) == _tree_bytes(report)


def test_no_field_and_empty_filter_list_are_exactly_equivalent(client: TestClient) -> None:
    omitted = client.post("/api/v2/rankings", json={"top_k": 10})
    empty = client.post(
        "/api/v2/rankings",
        json={"top_k": 10, "opportunity_filters": _selection()},
    )
    assert omitted.status_code == empty.status_code == 200
    assert omitted.json() == empty.json()
    body = omitted.json()
    assert body["assessments"]["opportunity"]["status"] == "NO_FILTERS_ACTIVE"
    assert all(row["rank"] == row["base_rank"] for row in body["rankings"])


@pytest.mark.parametrize(
    ("filter_ids", "passing_count", "top_codes"),
    [
        (
            ("technology_software_opportunity",),
            20,
            ["AUS", "SWE", "CHE", "NLD", "SGP", "CAN", "DEU", "DNK", "IRL", "GBR"],
        ),
        (
            ("science_engineering_opportunity",),
            20,
            ["SWE", "CHE", "NOR", "NLD", "SGP", "DEU", "DNK", "GBR", "FIN", "AUT"],
        ),
        (
            (
                "health_social_work_opportunity",
                "medicine_health_sciences_education_opportunity",
            ),
            22,
            ["AUS", "SWE", "CHE", "NLD", "JPN", "CAN", "DEU", "DNK", "GBR", "KOR"],
        ),
        (
            (
                "technology_software_opportunity",
                "computer_science_ict_education_opportunity",
            ),
            17,
            ["AUS", "SWE", "CHE", "NLD", "SGP", "CAN", "DEU", "DNK", "GBR", "BEL"],
        ),
        (
            ("skilled_trades_construction_opportunity",),
            33,
            ["AUS", "NZL", "JPN", "KOR", "CZE", "ESP", "USA", "ITA", "POL", "SVK"],
        ),
    ],
)
def test_real_data_golden_filtered_rankings(
    client: TestClient,
    filter_ids: tuple[str, ...],
    passing_count: int,
    top_codes: list[str],
) -> None:
    response = client.post(
        "/api/v2/rankings",
        json={"top_k": 10, "opportunity_filters": _selection(*filter_ids)},
    )
    assert response.status_code == 200
    body = response.json()
    opportunity = body["assessments"]["opportunity"]
    assert opportunity["status"] == "FILTERS_APPLIED"
    assert opportunity["active_filter_ids"] == sorted(filter_ids)
    assert opportunity["passing_country_count"] == passing_count
    assert opportunity["no_score_impact"] is True
    assert [row["country"]["country_codes"][0] for row in body["rankings"]] == top_codes


def test_strict_and_states_and_multiple_failure_reasons_are_visible(client: TestClient) -> None:
    payload = {
        "country_codes": ["AUS", "ARE", "ALB", "ARM"],
        "weights": GLOBAL_WEIGHTS,
        "opportunity_filters": _selection(
            "technology_software_opportunity",
            "engineering_technology_education_opportunity",
        ),
    }
    response = client.post("/api/v2/comparisons", json=payload)
    assert response.status_code == 200
    countries = {row["country"]["country_codes"][0]: row for row in response.json()["countries"]}
    assert countries["AUS"]["assessments"]["opportunity"]["passes"] is True
    assert countries["ARE"]["opportunity_excluded"] is True
    assert countries["ARM"]["opportunity_excluded"] is True
    alb = countries["ALB"]["assessments"]["opportunity"]
    assert alb["passes"] is False
    states = {row["filter_id"]: row["state"] for row in alb["filter_evidence"]}
    assert states == {
        "engineering_technology_education_opportunity": "INSUFFICIENT_EVIDENCE",
        "technology_software_opportunity": "STRONG_SIGNAL_NOT_ESTABLISHED",
    }


def test_invalid_duplicate_and_unsupported_filter_requests_are_rejected(
    client: TestClient,
) -> None:
    unknown = client.post(
        "/api/v2/rankings",
        json={"opportunity_filters": _selection("unknown_opportunity")},
    )
    duplicate = client.post(
        "/api/v2/rankings",
        json={
            "opportunity_filters": _selection(
                "technology_software_opportunity", "technology_software_opportunity"
            )
        },
    )
    unsupported = client.post(
        "/api/v2/rankings",
        json={
            "opportunity_filters": {
                "mode": "ANY_REQUIRED",
                "required_filter_ids": ["technology_software_opportunity"],
            }
        },
    )
    assert unknown.status_code == duplicate.status_code == unsupported.status_code == 422
    assert unknown.json()["error"]["code"] == "unknown_opportunity_filter"
    assert duplicate.json()["error"]["code"] == "request_validation_failed"
    assert unsupported.json()["error"]["code"] == "request_validation_failed"


def test_filtered_scores_order_base_rank_and_top_k_are_post_ranking_only(
    service: RecommendationService,
) -> None:
    canonical = service.rank(None, preference_preset_id=None, top_k=None, opportunity_filter_ids=())
    filtered = service.rank(
        None,
        preference_preset_id=None,
        top_k=10,
        opportunity_filter_ids=("technology_software_opportunity",),
    )
    canonical_by_code = {row["country"]["country_codes"][0]: row for row in canonical["rankings"]}
    survivor_base_ranks = []
    for row in filtered["rankings"]:
        code = row["country"]["country_codes"][0]
        source = canonical_by_code[code]
        assert row["base_rank"] == source["rank"]
        assert row["total_score"] == source["total_score"]
        assert row["contributions"] == source["contributions"]
        survivor_base_ranks.append(row["base_rank"])
    assert survivor_base_ranks == sorted(survivor_base_ranks)
    assert [row["rank"] for row in filtered["rankings"]] == list(
        range(1, len(filtered["rankings"]) + 1)
    )


def test_filtered_top_k_is_tie_inclusive_without_breaking_survivor_order(
    tmp_path: Path, opportunity_service: OpportunityFilterService
) -> None:
    release = _load(
        tmp_path,
        [{"id": "N1", "scores": {"CAN": 7, "MEX": 7, "USA": 7}}],
        countries=("CAN", "MEX", "USA"),
    )
    synthetic = RecommendationService(release, opportunity_service)
    result = synthetic.rank(
        {"N1": 1},
        preference_preset_id=None,
        top_k=2,
        opportunity_filter_ids=("engineering_technology_education_opportunity",),
    )
    assert len(result["rankings"]) == 3
    assert {row["total_score"] for row in result["rankings"]} == {7.0}
    assert [row["base_rank"] for row in result["rankings"]] == [1, 2, 3]


def test_no_countries_match_is_valid_and_never_falls_back() -> None:
    catalog = _json(STAGED / "opportunity-filter-catalog.json")
    rows = _jsonl(STAGED / "opportunity-filter-evidence.jsonl")
    coverage = _json(STAGED / "opportunity-filter-coverage-summary.json")
    target = "technology_software_opportunity"
    for row in rows:
        if row["filter_id"] != target:
            continue
        row.update(
            {
                "state": "INSUFFICIENT_EVIDENCE",
                "confidence_band": "LOW",
                "internal_confidence_tier": None,
                "coverage_completeness": "UNASSESSED",
                "evaluated_route_ids": [],
                "establishing_route_ids": [],
                "reason_codes": ["SOURCE_MISSING"],
                "metric_payload": None,
                "threshold_results": [],
                "source_observation_status": "MISSING",
            }
        )
    coverage["filters"][target] = {
        "assessable_count": 0,
        "state_counts": {
            "VERIFIED_STRONG_SIGNAL": 0,
            "STRONG_SIGNAL_NOT_ESTABLISHED": 0,
            "INSUFFICIENT_EVIDENCE": 91,
        },
        "source_dependency_status": "UNAVAILABLE",
    }
    opportunity = OpportunityFilterService(
        release_id="synthetic-empty",
        catalog=catalog,
        evidence_rows=rows,
        source_manifest=_json(STAGED / "opportunity-filter-source-manifest.json"),
        coverage_summary=coverage,
        evidence_policy=_json(STAGED / "opportunity-filter-evidence-policy.json"),
    )
    service = RecommendationService(
        CurrentReleaseRepository(ROOT / "data" / "releases").load_active(), opportunity
    )
    result = service.rank(
        GLOBAL_WEIGHTS,
        preference_preset_id=None,
        top_k=10,
        opportunity_filter_ids=(target,),
    )
    assert result["rankings"] == []
    assessment = result["assessments"]["opportunity"]
    assert assessment["status"] == "NO_COUNTRIES_MATCH"
    assert assessment["passing_country_count"] == 0
    assert assessment["excluded_country_count"] == 91
    assert result["normalized_weights"] == GLOBAL_WEIGHTS


@pytest.mark.parametrize(
    ("criteria", "weights", "expected_status"),
    [
        (
            [{"id": "N1", "scores": {"CAN": 5, "MEX": 6, "USA": 7}}],
            {"N1": 1},
            "NO_PARTIAL_CRITERIA_ACTIVE",
        ),
        (
            [
                {
                    "id": "P1",
                    "coverage": "CONDITIONAL_COMPLETE_CASE",
                    "minimum_valid_country_count": 2,
                    "scores": {"CAN": 5, "MEX": 6, "USA": 7},
                }
            ],
            {"P1": 1},
            "FULL_COVERAGE",
        ),
        (
            [
                {
                    "id": "P1",
                    "coverage": "CONDITIONAL_COMPLETE_CASE",
                    "minimum_valid_country_count": 2,
                    "scores": {"CAN": 5, "MEX": 6},
                }
            ],
            {"P1": 1},
            "PARTIAL_COMPLETE_CASE",
        ),
        (
            [
                {"id": "N1", "scores": {"CAN": 5, "MEX": 6, "USA": 7}},
                {
                    "id": "P1",
                    "coverage": "CONDITIONAL_COMPLETE_CASE",
                    "minimum_valid_country_count": 2,
                    "scores": {"CAN": 5},
                },
            ],
            {"N1": 1, "P1": 1},
            "COVERAGE_LIMIT_FALLBACK",
        ),
        (
            [
                {"id": "N1", "scores": {"CAN": 5, "MEX": 6, "USA": 7}},
                {
                    "id": "L1",
                    "locality": True,
                    "scores": {
                        "CAN": {"a": 9, "b": 7},
                        "MEX": {"a": 8, "b": 6},
                        "USA": {"a": 7, "b": 5},
                    },
                },
            ],
            {"N1": 1, "L1": 0.6},
            "NO_PARTIAL_CRITERIA_ACTIVE",
        ),
    ],
)
def test_pcc_lsc_and_profile_assessments_are_unchanged_by_filtering(
    tmp_path: Path,
    opportunity_service: OpportunityFilterService,
    criteria: list[dict],
    weights: dict[str, float],
    expected_status: str,
) -> None:
    release = _load(tmp_path, criteria, countries=("CAN", "MEX", "USA"))
    service = RecommendationService(release, opportunity_service)
    canonical = service.rank(
        weights, preference_preset_id=None, top_k=None, opportunity_filter_ids=()
    )
    filtered = service.rank(
        weights,
        preference_preset_id=None,
        top_k=None,
        opportunity_filter_ids=("technology_software_opportunity",),
    )
    assert canonical["assessments"]["coverage"]["status"] == expected_status
    assert filtered["assessments"]["coverage"] == canonical["assessments"]["coverage"]
    assert filtered["assessments"]["locality"] == canonical["assessments"]["locality"]
    assert filtered["assessments"]["profile"] == canonical["assessments"]["profile"]
    assert filtered["normalized_weights"] == canonical["normalized_weights"]


def test_catalog_comparison_and_detail_expose_bounded_evidence(client: TestClient) -> None:
    catalog = client.get("/api/v2/opportunity-filters")
    assert catalog.status_code == 200
    body = catalog.json()
    assert body["opportunity_release_id"] == "phase6g-api-2026-08-03.1"
    assert len(body["definitions"]) == 9
    assert all(item["no_score_impact"] for item in body["definitions"])
    assert not ({item["id"] for item in body["definitions"]} & {"criteria", "weights"})
    education = next(
        item
        for item in body["definitions"]
        if item["id"] == "engineering_technology_education_opportunity"
    )
    limitations = " ".join(education["limitations"]).lower()
    assert "teaching" in limitations and "admissions" in limitations and "visa" in limitations

    comparison = client.post(
        "/api/v2/comparisons",
        json={
            "country_codes": ["ARE", "CAN"],
            "weights": GLOBAL_WEIGHTS,
            "opportunity_filters": _selection(
                "skilled_trades_construction_opportunity",
                "technology_software_opportunity",
            ),
        },
    )
    assert comparison.status_code == 200
    countries = {row["country"]["country_codes"][0]: row for row in comparison.json()["countries"]}
    are_evidence = countries["ARE"]["assessments"]["opportunity"]["filter_evidence"]
    skilled = next(
        row for row in are_evidence if row["filter_id"] == "skilled_trades_construction_opportunity"
    )
    assert set(skilled["establishing_route_ids"]) == {"skilled_trades", "construction"}
    can_evidence = countries["CAN"]["assessments"]["opportunity"]["filter_evidence"]
    technology = next(
        row for row in can_evidence if row["filter_id"] == "technology_software_opportunity"
    )
    assert technology["confidence_band"] == "MEDIUM"
    assert technology["establishing_route_ids"] == ["canada_technology"]

    details = client.post(
        "/api/v2/countries/CAN/details",
        json={
            "weights": GLOBAL_WEIGHTS,
            "opportunity_filters": _selection("technology_software_opportunity"),
        },
    )
    assert details.status_code == 200
    assert details.json()["opportunity_filters"] == [technology]
    assert "metric_payload" not in json.dumps(comparison.json())


def test_old_release_without_opportunity_bundle_is_additive_and_rejects_selection() -> None:
    service = RecommendationService(
        CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    )
    with TestClient(create_app(service=service)) as client:
        catalog = client.get("/api/v2/opportunity-filters")
        no_filter = client.post("/api/v2/rankings", json={"top_k": 3})
        selected = client.post(
            "/api/v2/rankings",
            json={"opportunity_filters": _selection("technology_software_opportunity")},
        )
    assert catalog.status_code == no_filter.status_code == 200
    assert catalog.json()["definitions"] == []
    assert catalog.json()["opportunity_release_id"] is None
    assert no_filter.json()["assessments"]["opportunity"]["status"] == "NO_FILTERS_ACTIVE"
    assert selected.status_code == 422
    assert selected.json()["error"]["code"] == "unknown_opportunity_filter"


def test_phase6f_staged_definition_cannot_be_selected_before_api_candidate_promotion() -> None:
    phase6f_staged = ROOT / "data" / "reports" / "phase6f-2026-08-03" / "staged-release"
    service = RecommendationService(
        CurrentReleaseRepository(ROOT / "data" / "releases").load_active(),
        OpportunityFilterService.from_directory(phase6f_staged),
    )
    with TestClient(create_app(service=service)) as client:
        response = client.post(
            "/api/v2/rankings",
            json={"opportunity_filters": _selection("technology_software_opportunity")},
        )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "opportunity_filter_not_active"


def test_indexed_filter_evaluation_performance(
    service: RecommendationService, opportunity_service: OpportunityFilterService
) -> None:
    assert opportunity_service.filter_count == 9
    assert opportunity_service.evidence_count == 819
    canonical = service.rank(
        None, preference_preset_id=None, top_k=None, opportunity_filter_ids=()
    )["rankings"]
    filter_ids = tuple(item["id"] for item in service.opportunity_filter_catalog()["definitions"])
    started = time.perf_counter()
    for _ in range(100):
        opportunity_service.assess_ranked_countries(canonical, filter_ids)
    elapsed = time.perf_counter() - started
    assert elapsed < 2.0


def test_filter_id_order_is_result_invariant(service: RecommendationService) -> None:
    first = service.rank(
        None,
        preference_preset_id=None,
        top_k=10,
        opportunity_filter_ids=(
            "technology_software_opportunity",
            "computer_science_ict_education_opportunity",
        ),
    )
    second = service.rank(
        None,
        preference_preset_id=None,
        top_k=10,
        opportunity_filter_ids=(
            "computer_science_ict_education_opportunity",
            "technology_software_opportunity",
        ),
    )
    assert first == second
