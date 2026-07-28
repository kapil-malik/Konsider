import json
from pathlib import Path

import pytest

from konsider.application import RecommendationService
from konsider.domain.scoring import ScoringError
from konsider.domain.uncertainty_models import UncertaintyStatus
from konsider.repositories.published_release_repository import PublishedReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "phase4c"
FCC_ID = "fixture_global_core"
PCC_ID = "overall_job_market_opportunity_fixture"
GOLDEN = json.loads(
    (ROOT / "tests" / "fixtures" / "phase4d" / "golden-scenarios.json").read_text(encoding="utf-8")
)


@pytest.fixture(scope="module")
def phase4_service() -> RecommendationService:
    repository = PublishedReleaseRepository(
        FIXTURE / "releases",
        FIXTURE / "consumer-catalog-2.0.json",
    )
    return RecommendationService(repository)


@pytest.mark.parametrize(
    "scenario",
    GOLDEN["activation_weight_scenarios"],
    ids=lambda item: item["id"],
)
def test_pcc_activation_and_ignored_semantics(
    phase4_service,
    scenario,
) -> None:
    pcc_weight = scenario["weight"]
    weights = {FCC_ID: 1.0}
    if pcc_weight is not None:
        weights[PCC_ID] = pcc_weight

    result = phase4_service.rank_with_uncertainty(weights)

    assert len(result.ignored_pcc) == scenario["ignored_count"]
    assert len(result.active_pcc_ids) == scenario["active_count"]
    assert result.status == UncertaintyStatus(scenario["expected_status"])
    assert result.requested_top_k == 10
    if scenario["ignored_count"]:
        ignored = result.ignored_pcc[0]
        assert ignored.reason_code == "BELOW_PCC_ACTIVATION_THRESHOLD"
        assert ignored.activation_threshold == 0.6
        assert ignored.raw_weight == pcc_weight


def test_existing_schema3_fcc_scores_and_order_are_unchanged() -> None:
    service = RecommendationService()
    weights = {
        "ambient_pm25_population_weighted": 3,
        "intentional_homicide_rate": 2,
        "household_consumption_price_level_us_100": 1,
    }

    existing = service.rank(weights, top_k=91)
    phase4 = service.rank_with_uncertainty(weights, top_k=91)

    assert phase4.status == UncertaintyStatus.NO_PARTIAL_CRITERIA_ACTIVE
    assert [item.country_code for item in phase4.rankings] == [
        item["country_code"] for item in existing["rankings"]
    ]
    assert [item.total_score for item in phase4.rankings] == [
        item["total_score"] for item in existing["rankings"]
    ]


def test_server_owned_profile_uses_the_same_phase4_engine(phase4_service) -> None:
    result = phase4_service.rank_with_uncertainty(profile_id="phase4c_fixture")

    assert result.resolved_profile_id == "phase4c_fixture"
    assert result.active_pcc_ids == (PCC_ID,)
    assert result.status == UncertaintyStatus.ROBUST_TOP_K


@pytest.mark.parametrize(
    ("weights", "message"),
    [
        ({"crime_rate": 1}, "Unknown"),
        ({"uhc_service_coverage_index": 1}, "Non-ready"),
        ({"intentional_homicide_rate": -1}, "negative"),
        ({"intentional_homicide_rate": float("inf")}, "finite"),
    ],
)
def test_phase4_service_preserves_weight_validation(weights, message) -> None:
    service = RecommendationService()

    with pytest.raises(ScoringError, match=message):
        service.rank_with_uncertainty(weights)
