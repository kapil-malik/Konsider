from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.models.catalog import CatalogResponse
from konsider.api.models.rankings import ComparisonResponse, RankingResponse
from konsider.application import RecommendationService
from konsider.repositories.published_release_repository import (
    PublishedReleaseRepository,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests" / "fixtures" / "phase4c"
FCC_ID = "fixture_global_core"
PCC_ID = "overall_job_market_opportunity_fixture"


class _StaticRepository:
    def __init__(self, release):
        self.release = release

    def load_active(self):
        return self.release


def _fixture_service() -> RecommendationService:
    repository = PublishedReleaseRepository(
        FIXTURE / "releases",
        FIXTURE / "consumer-catalog-2.0.json",
    )
    return RecommendationService(repository)


def _coverage_limit_service() -> RecommendationService:
    release = _fixture_service().release
    current_missing = {
        item["country_code"]
        for item in release.outcomes
        if item["criterion_id"] == PCC_ID and item["outcome"] != "valid"
    }
    country_codes = [item["code"] for item in release.catalog["countries"]]
    missing = set(current_missing)
    missing.update(code for code in country_codes if code not in missing and len(missing) < 10)
    outcomes = []
    for item in release.outcomes:
        if item["criterion_id"] == PCC_ID and item["country_code"] in missing:
            item = {
                **item,
                "outcome": "missing",
                "observation_id": None,
                "reason_codes": ["COV_SOURCE_RECORD_MISSING"],
            }
        outcomes.append(item)
    records = tuple(
        item
        for item in release.records
        if not (item.criterion["id"] == PCC_ID and item.country["code"] in missing)
    )
    modified = replace(
        release,
        outcomes=tuple(outcomes),
        records=records,
    )
    return RecommendationService(_StaticRepository(modified))


@pytest.fixture(scope="module")
def phase4_client():
    with TestClient(create_app(service=_fixture_service())) as client:
        yield client


def test_catalog_exposes_typed_fcc_and_pcc_coverage(phase4_client) -> None:
    response = phase4_client.get("/api/v1/catalog")
    body = CatalogResponse.model_validate(response.json())
    criteria = {item.id: item for item in body.criteria}

    assert response.status_code == 200
    assert criteria[FCC_ID].coverage_mode == "GLOBAL_CORE"
    assert criteria[FCC_ID].valid_country_count == 91
    assert criteria[FCC_ID].coverage_percentage == 100
    assert criteria[PCC_ID].coverage_mode == "CONDITIONAL_COMPLETE_CASE"
    assert criteria[PCC_ID].valid_country_count == 88
    assert criteria[PCC_ID].stable_country_count == 91
    assert criteria[PCC_ID].coverage_percentage == 96.7
    assert criteria[PCC_ID].pcc_activation_threshold == 0.6
    assert criteria[PCC_ID].missing_country_count == 3


def test_ranking_endpoint_returns_additive_uncertainty_contract(
    phase4_client,
) -> None:
    response = phase4_client.post(
        "/api/v1/rankings",
        json={"weights": {FCC_ID: 1, PCC_ID: 0.6}},
    )
    body = RankingResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.uncertainty_status == "ROBUST_TOP_K"
    assert body.ranking_coverage_mode == "CONDITIONAL_COMPLETE_CASE"
    assert body.robustness_k == 10
    assert body.stable_universe_size == 91
    assert body.eligible_universe_size == 88
    assert body.excluded_country_count == 3
    assert body.active_pcc_ids == [PCC_ID]
    assert body.kth_eligible_score is not None
    assert len(body.excluded_countries) == 3
    assert all(
        item.optimistic_upper_bound is not None and item.could_enter_top_k is False
        for item in body.excluded_countries
    )
    assert all(
        item.country_code not in {excluded.country_code for excluded in body.excluded_countries}
        for item in body.rankings
    )


def test_comparison_separates_unavailable_cell_from_partial_score(
    phase4_client,
) -> None:
    response = phase4_client.post(
        "/api/v1/comparisons",
        json={
            "country_codes": ["ALB", "ATG"],
            "weights": {FCC_ID: 1, PCC_ID: 0.6},
        },
    )
    body = ComparisonResponse.model_validate(response.json())
    summaries = {item.country_code: item for item in body.country_summaries}
    pcc_row = next(item for item in body.criterion_rows if item.criterion_id == PCC_ID)
    pcc_cells = {item.country_code: item for item in pcc_row.cells}

    assert response.status_code == 200
    assert summaries["ALB"].ranking_eligible is True
    assert summaries["ALB"].comparison_data_complete is True
    assert summaries["ATG"].ranking_eligible is False
    assert summaries["ATG"].ranking_status == "NOT_RANKED_ACTIVE_DATA_GAP"
    assert summaries["ATG"].aggregate_kind == "NONE"
    assert summaries["ATG"].total_score is None
    assert summaries["ATG"].rank is None
    assert summaries["ATG"].unavailable_active_criterion_count == 1
    assert pcc_cells["ATG"].availability == "MISSING"
    assert pcc_cells["ATG"].normalized_score is None
    assert pcc_cells["ATG"].reason_codes == ["COV_SOURCE_RECORD_MISSING"]
    assert [item.country_code for item in body.countries] == ["ALB"]
    assert [item.country_code for item in body.requested_excluded_countries] == ["ATG"]


def test_inactive_pcc_gap_does_not_remove_comparison_rank(
    phase4_client,
) -> None:
    response = phase4_client.post(
        "/api/v1/comparisons",
        json={
            "country_codes": ["ALB", "ATG"],
            "weights": {FCC_ID: 1, PCC_ID: 0.4},
        },
    )
    body = ComparisonResponse.model_validate(response.json())
    summaries = {item.country_code: item for item in body.country_summaries}
    pcc_row = next(item for item in body.criterion_rows if item.criterion_id == PCC_ID)
    atg_cell = next(item for item in pcc_row.cells if item.country_code == "ATG")

    assert body.uncertainty_status == "NO_PARTIAL_CRITERIA_ACTIVE"
    assert len(body.ignored_pcc) == 1
    assert summaries["ATG"].comparison_data_complete is False
    assert summaries["ATG"].ranking_eligible is True
    assert summaries["ATG"].aggregate_kind == "FINAL"
    assert summaries["ATG"].total_score is not None
    assert summaries["ATG"].unavailable_active_criterion_count == 0
    assert atg_cell.availability == "MISSING"
    assert atg_cell.active_for_ranking is False


def test_coverage_limit_is_successful_and_has_no_r1_conclusion() -> None:
    service = _coverage_limit_service()
    with TestClient(create_app(service=service)) as client:
        response = client.post(
            "/api/v1/rankings",
            json={"weights": {FCC_ID: 1, PCC_ID: 0.6}},
        )
        body = RankingResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.uncertainty_status == "COVERAGE_LIMIT_EXCEEDED"
    assert body.ranking_coverage_mode == "GLOBAL_CORE"
    assert body.eligible_universe_size == 81
    assert body.excluded_country_count == 10
    assert body.kth_eligible_score is None
    assert body.potential_excluded_entrants == []
    assert all(item.could_enter_top_k is None for item in body.excluded_countries)
    assert all(item.optimistic_upper_bound is None for item in body.excluded_countries)


def test_coverage_limit_comparison_labels_fcc_baseline() -> None:
    service = _coverage_limit_service()
    missing = {
        item["country_code"]
        for item in service.release.outcomes
        if item["criterion_id"] == PCC_ID and item["outcome"] != "valid"
    }
    available = [
        item["code"] for item in service.release.catalog["countries"] if item["code"] not in missing
    ][:2]
    with TestClient(create_app(service=service)) as client:
        response = client.post(
            "/api/v1/comparisons",
            json={
                "country_codes": available,
                "weights": {FCC_ID: 1, PCC_ID: 0.6},
            },
        )
        body = ComparisonResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.uncertainty_status == "COVERAGE_LIMIT_EXCEEDED"
    assert all(item.ranking_eligible is False for item in body.country_summaries)
    assert all(
        item.aggregate_kind == "FCC_BASELINE"
        and item.ranking_status == "FCC_BASELINE_ONLY"
        and item.total_score is not None
        for item in body.country_summaries
    )


def test_openapi_lists_every_uncertainty_status() -> None:
    schema = create_app(service=_fixture_service()).openapi()
    status_schema = schema["components"]["schemas"]["RankingResponse"]["properties"][
        "uncertainty_status"
    ]

    assert set(status_schema["enum"]) == {
        "NO_PARTIAL_CRITERIA_ACTIVE",
        "COVERAGE_LIMIT_EXCEEDED",
        "FULL_COVERAGE",
        "BASELINE_TOP_K_EXCLUDED",
        "POTENTIALLY_AFFECTED",
        "ROBUST_TOP_K",
    }
