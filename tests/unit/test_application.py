import json

import pytest

from konsider.application import RecommendationService
from konsider.domain.scoring import ScoringError


@pytest.fixture(scope="module")
def service() -> RecommendationService:
    return RecommendationService()


def test_catalog_has_eleven_enabled_criteria(service) -> None:
    catalog = service.get_catalog()
    assert len(catalog["countries"]) == 91
    assert len(catalog["criteria"]) == 12
    assert sum(item["default_enabled"] for item in catalog["criteria"]) == 11


def test_ranking_is_deterministic_and_contributions_sum(service) -> None:
    weights = {
        "ambient_pm25_population_weighted": 3,
        "intentional_homicide_rate": 2,
        "household_consumption_price_level_us_100": 1,
    }
    first = service.rank(weights)
    second = service.rank(weights)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert len(first["rankings"]) == 91
    for row in first["rankings"]:
        assert (
            abs(sum(item["contribution"] for item in row["contributions"]) - row["total_score"])
            <= first["rounding_tolerance"]
        )


def test_omitted_weights_are_zero_and_all_zero_is_equal(service) -> None:
    one = service.rank({"intentional_homicide_rate": 2})
    assert one["normalized_weights"]["intentional_homicide_rate"] == 1
    assert sum(value == 0 for value in one["normalized_weights"].values()) == 10

    zero = service.rank({})
    assert set(zero["normalized_weights"].values()) == {1 / 11}
    assert zero["total_eligible_country_count"] == 91


@pytest.mark.parametrize(
    ("weights", "message"),
    [
        ({"intentional_homicide_rate": -1}, "negative"),
        ({"intentional_homicide_rate": float("nan")}, "finite"),
        ({"crime_rate": 1}, "Unknown"),
        ({"uhc_service_coverage_index": 1}, "Non-ready"),
    ],
)
def test_invalid_weights_fail(service, weights, message) -> None:
    with pytest.raises(ScoringError, match=message):
        service.rank(weights)


def test_equal_cost_bands_remain_equal(service) -> None:
    result = service.rank({"household_consumption_price_level_us_100": 1})
    by_score = {}
    for country in result["rankings"]:
        cost = next(
            item
            for item in country["contributions"]
            if item["criterion_id"] == "household_consumption_price_level_us_100"
        )
        by_score.setdefault(cost["score"], []).append(cost["contribution"])
    tied = [values for values in by_score.values() if len(values) > 1]
    assert tied
    assert all(len(set(values)) == 1 for values in tied)


def test_compare_and_breakdown_are_release_pinned(service) -> None:
    comparison = service.compare(["IND", "SGP"], {})
    breakdown = service.country_breakdown("IND")

    assert comparison["release_id"] == breakdown["release_id"] == "2026-07-28.2"
    assert [item["country_code"] for item in comparison["countries"]] == ["IND", "SGP"]
    assert len(breakdown["criteria"]) == 11
