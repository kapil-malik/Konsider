import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.models.catalog import CatalogResponse, HealthResponse
from konsider.api.models.countries import CountryMetricResponse
from konsider.api.models.rankings import ComparisonResponse, RankingResponse
from konsider.api.settings import ApiSettings
from konsider.application import RecommendationService
from konsider.repositories.published_release_repository import PublishedReleaseRepository

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def client(tmp_path):
    active = tmp_path / "schema4-active.json"
    active.write_text(
        json.dumps(
            {
                "release_id": "2026-07-28.2",
                "schema_version": "konsider-release-4.0",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    settings = ApiSettings(
        release_root=ROOT / "data" / "releases",
        active_release_path=active,
        catalog_path=ROOT / "data" / "catalogs" / "releases" / "2026-07-28.2.json",
    )
    with TestClient(create_app(settings=settings)) as value:
        yield value


def test_health_reports_validated_snapshot(client) -> None:
    response = client.get("/api/v1/health")
    body = HealthResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.status == "ok"
    assert body.release_id == "2026-07-28.2"
    assert body.country_count == 91
    assert body.enabled_criterion_count == 11
    assert body.ready_for_rankings is True
    assert len(body.scoring_method_versions) == 11


def test_catalog_has_available_and_enabled_contracts(client) -> None:
    response = client.get("/api/v1/catalog")
    body = CatalogResponse.model_validate(response.json())

    assert response.status_code == 200
    assert len(body.countries) == 91
    assert len(body.criteria) == 12
    assert sum(item.default_enabled for item in body.criteria) == 11
    uhc = next(item for item in body.criteria if item.id == "uhc_service_coverage_index")
    infrastructure = next(
        item for item in body.criteria if item.id == "infrastructure_readiness_composite"
    )
    assert uhc.ready is False and uhc.default_enabled is False
    assert infrastructure.ready is True and infrastructure.experimental is True
    job_market = next(item for item in body.criteria if item.id == "overall_job_market_opportunity")
    assert job_market.coverage_mode == "CONDITIONAL_COMPLETE_CASE"
    assert job_market.valid_country_count == 88
    assert job_market.pcc_activation_threshold == 0.6
    assert [item.id for item in body.profiles] == [
        "equal_weight_mvp",
        "safety_and_stability",
        "affordability_first",
        "quality_of_life",
    ]
    assert all(item.sources for item in body.criteria)
    assert uhc.sources[0].reference_period == "annual, latest API value 2021"
    serialized = response.text
    assert "raw_observation" not in serialized
    assert "contribution" not in serialized


def test_catalog_profiles_are_exact_enabled_raw_weights(client) -> None:
    body = CatalogResponse.model_validate(client.get("/api/v1/catalog").json())
    enabled = {item.id for item in body.criteria if item.ready and item.default_enabled}
    expected = {
        "equal_weight_mvp": {
            "ambient_pm25_population_weighted": 1.0,
            "established_immigrant_presence": 1.0,
            "household_consumption_price_level_us_100": 1.0,
            "infrastructure_readiness_composite": 1.0,
            "intentional_homicide_rate": 1.0,
            "overall_job_market_opportunity": 1.0,
            "political_stability": 1.0,
            "research_innovation_ecosystem": 1.0,
            "rule_of_law": 1.0,
            "school_education_quality": 1.0,
            "women_legal_economic_equality": 1.0,
        },
        "safety_and_stability": {
            "ambient_pm25_population_weighted": 0.6,
            "established_immigrant_presence": 0.3,
            "household_consumption_price_level_us_100": 0.4,
            "infrastructure_readiness_composite": 0.6,
            "intentional_homicide_rate": 1.0,
            "overall_job_market_opportunity": 0.6,
            "political_stability": 1.0,
            "research_innovation_ecosystem": 0.4,
            "rule_of_law": 0.8,
            "school_education_quality": 0.4,
            "women_legal_economic_equality": 0.6,
        },
        "affordability_first": {
            "ambient_pm25_population_weighted": 0.4,
            "established_immigrant_presence": 0.3,
            "household_consumption_price_level_us_100": 1.0,
            "infrastructure_readiness_composite": 0.4,
            "intentional_homicide_rate": 0.6,
            "overall_job_market_opportunity": 0.6,
            "political_stability": 0.5,
            "research_innovation_ecosystem": 0.4,
            "rule_of_law": 0.5,
            "school_education_quality": 0.4,
            "women_legal_economic_equality": 0.4,
        },
        "quality_of_life": {
            "ambient_pm25_population_weighted": 1.0,
            "established_immigrant_presence": 0.5,
            "household_consumption_price_level_us_100": 0.4,
            "infrastructure_readiness_composite": 0.8,
            "intentional_homicide_rate": 0.8,
            "overall_job_market_opportunity": 0.8,
            "political_stability": 0.8,
            "research_innovation_ecosystem": 0.8,
            "rule_of_law": 0.8,
            "school_education_quality": 1.0,
            "women_legal_economic_equality": 0.8,
        },
    }

    assert {item.id: item.weights for item in body.profiles} == expected
    assert all(set(item.weights) == enabled for item in body.profiles)


def test_added_profiles_use_existing_ranking_semantics(client) -> None:
    response = client.post("/api/v1/rankings", json={"profile_id": "safety_and_stability"})
    body = RankingResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.resolved_profile_id == "safety_and_stability"
    assert sum(body.normalized_weights.values()) == pytest.approx(1)
    assert body.normalized_weights["intentional_homicide_rate"] == pytest.approx(1 / 5.9)


def test_rankings_default_profile_and_top_k(client) -> None:
    response = client.post("/api/v1/rankings", json={"top_k": 3})
    body = RankingResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.resolved_profile_id == "equal_weight_mvp"
    assert body.total_eligible_country_count == 83
    assert body.returned_result_count == 3
    assert len(body.rankings) == 3
    assert set(body.normalized_weights.values()) == {1 / 11}
    assert all(len(item.contributions) == 11 for item in body.rankings)


def test_explicit_ranking_is_deterministic_and_reconciles(client) -> None:
    payload = {
        "weights": {
            "ambient_pm25_population_weighted": 3,
            "intentional_homicide_rate": 2,
            "household_consumption_price_level_us_100": 1,
        }
    }
    first = client.post("/api/v1/rankings", json=payload)
    second = client.post("/api/v1/rankings", json=payload)
    body = RankingResponse.model_validate(first.json())

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert body.resolved_profile_id is None
    assert body.normalized_weights["ambient_pm25_population_weighted"] == 0.5
    assert body.normalized_weights["intentional_homicide_rate"] == pytest.approx(1 / 3)
    assert body.normalized_weights["household_consumption_price_level_us_100"] == pytest.approx(
        1 / 6
    )
    ordering = [(item.total_score, item.country_code) for item in body.rankings]
    assert ordering == sorted(ordering, key=lambda item: (-item[0], item[1]))
    for country in body.rankings:
        total = sum(item.contribution for item in country.contributions)
        assert abs(total - country.total_score) <= body.rounding_tolerance
        assert all(item.observations and item.source.source_id for item in country.contributions)


def test_omitted_and_all_zero_weights_keep_service_semantics(client) -> None:
    omitted = RankingResponse.model_validate(
        client.post("/api/v1/rankings", json={"weights": {"intentional_homicide_rate": 2}}).json()
    )
    zero = RankingResponse.model_validate(
        client.post(
            "/api/v1/rankings",
            json={"weights": {"intentional_homicide_rate": 0}},
        ).json()
    )

    assert omitted.normalized_weights["intentional_homicide_rate"] == 1
    assert sum(value == 0 for value in omitted.normalized_weights.values()) == 7
    assert set(zero.normalized_weights.values()) == {0.125}


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ({"weights": {"crime_rate": 1}}, "unknown_criterion"),
        ({"weights": {"uhc_service_coverage_index": 1}}, "criterion_not_ready"),
        ({"weights": {"intentional_homicide_rate": -1}}, "invalid_weight"),
        ({"weights": {"intentional_homicide_rate": float("nan")}}, "invalid_weight"),
        ({"weights": {"intentional_homicide_rate": float("inf")}}, "invalid_weight"),
        ({"weights": {"intentional_homicide_rate": float("-inf")}}, "invalid_weight"),
        (
            {
                "weights": {
                    "intentional_homicide_rate": 1e308,
                    "ambient_pm25_population_weighted": 1e308,
                }
            },
            "invalid_weight",
        ),
        ({"top_k": 0}, "invalid_top_k"),
        ({"top_k": 92}, "invalid_top_k"),
    ],
)
def test_structured_ranking_failures(client, payload, code) -> None:
    contains_non_finite = any(
        isinstance(value, float) and (value != value or abs(value) == float("inf"))
        for value in payload.get("weights", {}).values()
    )
    if contains_non_finite:
        response = client.post(
            "/api/v1/rankings",
            content=json.dumps(payload),
            headers={"content-type": "application/json"},
        )
    else:
        response = client.post("/api/v1/rankings", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == code


def test_transport_validation_is_structured(client) -> None:
    invalid_string = client.post(
        "/api/v1/rankings", json={"weights": {"intentional_homicide_rate": "5"}}
    )
    malformed = client.post(
        "/api/v1/rankings", content="{", headers={"content-type": "application/json"}
    )

    assert invalid_string.status_code == malformed.status_code == 422
    assert invalid_string.json()["error"]["code"] == "request_validation_failed"
    assert malformed.json()["error"]["code"] == "request_validation_failed"


def test_profile_and_weights_are_mutually_exclusive(client) -> None:
    response = client.post(
        "/api/v1/rankings",
        json={"profile_id": "equal_weight_mvp", "weights": {}},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_profile_selection"


def test_unknown_profile_is_structured(client) -> None:
    response = client.post("/api/v1/rankings", json={"profile_id": "missing"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "profile_not_found"


def test_country_metrics_are_enabled_public_records(client) -> None:
    response = client.get("/api/v1/countries/ind/metrics")
    body = CountryMetricResponse.model_validate(response.json())

    assert response.status_code == 200
    assert body.country.code == "IND"
    assert len(body.criteria) == 11
    assert all(item.criterion.ready for item in body.criteria)
    assert all(item.observations and item.source.canonical_page_url for item in body.criteria)
    assert "uhc_service_coverage_index" not in {item.criterion.id for item in body.criteria}


def test_unknown_country_is_structured_404(client) -> None:
    response = client.get("/api/v1/countries/zzz/metrics")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "country_not_found"
    assert response.json()["error"]["details"]["country_codes"] == ["ZZZ"]


def test_comparison_uses_ranking_semantics(client) -> None:
    response = client.post(
        "/api/v1/comparisons",
        json={
            "country_codes": ["ind", "sgp", "can"],
            "weights": {"intentional_homicide_rate": 2},
        },
    )
    body = ComparisonResponse.model_validate(response.json())

    assert response.status_code == 200
    assert [item.country_code for item in body.countries] == ["IND", "SGP", "CAN"]
    assert body.returned_result_count == 3
    assert body.normalized_weights["intentional_homicide_rate"] == 1
    assert all(len(item.contributions) == 8 for item in body.countries)


@pytest.mark.parametrize(
    "country_codes",
    [
        ["IND"],
        ["IND", "IND"],
        ["IND", "SGP", "CAN", "AUS", "DEU", "NLD", "CHE", "USA", "GBR", "ARE", "FRA"],
    ],
)
def test_invalid_comparison_selection(client, country_codes) -> None:
    response = client.post("/api/v1/comparisons", json={"country_codes": country_codes})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_comparison"


def test_unknown_comparison_country_is_404(client) -> None:
    response = client.post("/api/v1/comparisons", json={"country_codes": ["IND", "ZZZ"]})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "country_not_found"


def test_default_paths_do_not_depend_on_current_working_directory(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    with TestClient(create_app()) as other_client:
        response = other_client.get("/api/v2/health")

    assert response.status_code == 200
    assert response.json()["release_id"] == "2026-07-29.1"


def test_service_is_constructed_once_per_app_lifecycle(tmp_path) -> None:
    calls = []
    active = tmp_path / "schema4-active.json"
    active.write_text(
        json.dumps(
            {
                "release_id": "2026-07-28.2",
                "schema_version": "konsider-release-4.0",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    settings = ApiSettings(
        release_root=ROOT / "data" / "releases",
        active_release_path=active,
        catalog_path=ROOT / "data" / "catalogs" / "releases" / "2026-07-28.2.json",
    )

    def factory(factory_settings):
        calls.append(factory_settings)
        return RecommendationService(
            PublishedReleaseRepository(
                factory_settings.release_root,
                factory_settings.catalog_path,
                active_release_path=factory_settings.active_release_path,
            )
        )

    with TestClient(create_app(settings=settings, service_factory=factory)) as other_client:
        assert other_client.get("/api/v1/health").status_code == 200
        assert other_client.get("/api/v1/catalog").status_code == 200
        assert other_client.post("/api/v1/rankings", json={}).status_code == 200

    assert len(calls) == 1


def test_missing_release_returns_safe_503(tmp_path) -> None:
    missing = tmp_path / "private" / "releases"
    settings = ApiSettings(
        release_root=missing,
        active_release_path=missing / "active.json",
        catalog_path=ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json",
    )
    with TestClient(create_app(settings=settings)) as other_client:
        health = other_client.get("/api/v1/health")
        catalog = other_client.get("/api/v1/catalog")

    assert health.status_code == catalog.status_code == 503
    assert health.json()["error"]["code"] == "release_unavailable"
    assert str(tmp_path) not in health.text
    assert str(tmp_path) not in catalog.text


def test_unsupported_release_contract_returns_safe_503(tmp_path) -> None:
    release_root = tmp_path / "releases"
    release_root.mkdir()
    (release_root / "active.json").write_text(
        json.dumps({"release_id": "future", "schema_version": "konsider-release-5.0"}),
        encoding="utf-8",
    )
    settings = ApiSettings(
        release_root=release_root,
        active_release_path=release_root / "active.json",
        catalog_path=ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json",
    )
    with TestClient(create_app(settings=settings)) as other_client:
        response = other_client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "unsupported_release_contract"
    assert "4.0" not in response.text


def test_temporary_release_and_catalog_paths_are_injectable(tmp_path) -> None:
    release_root = tmp_path / "releases"
    shutil.copytree(ROOT / "data" / "releases", release_root)
    (release_root / "active.json").write_text(
        json.dumps(
            {
                "release_id": "2026-07-28.2",
                "schema_version": "konsider-release-4.0",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    catalog = tmp_path / "catalog.json"
    shutil.copy2(ROOT / "data" / "catalogs" / "consumer-catalog-2.0.json", catalog)
    settings = ApiSettings(
        release_root=release_root,
        active_release_path=release_root / "active.json",
        catalog_path=catalog,
    )
    with TestClient(create_app(settings=settings)) as other_client:
        response = other_client.get("/api/v1/catalog")

    assert response.status_code == 200
    assert response.json()["release_id"] == "2026-07-28.2"


def test_unexpected_failure_returns_safe_500() -> None:
    service = RecommendationService()

    def fail():
        raise RuntimeError("private C:\\secret\\release path")

    service.get_catalog = fail
    with TestClient(create_app(service=service), raise_server_exceptions=False) as other_client:
        response = other_client.get("/api/v1/catalog")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "secret" not in response.text
    assert "RuntimeError" not in response.text


def test_openapi_retains_the_five_v1_routes_during_the_v2_migration() -> None:
    schema = create_app(service=RecommendationService()).openapi()
    expected = {
        "/api/v1/health",
        "/api/v1/catalog",
        "/api/v1/rankings",
        "/api/v1/countries/{country_code}/metrics",
        "/api/v1/comparisons",
    }

    assert {path for path in schema["paths"] if path.startswith("/api/v1/")} == expected
    assert schema["info"]["version"] == "2.0.0"
    assert "RankingRequest" in schema["components"]["schemas"]
    assert "RankingResponse" in schema["components"]["schemas"]
    assert "ErrorResponse" in schema["components"]["schemas"]


def test_success_responses_do_not_leak_local_paths_or_raw_bytes(client) -> None:
    responses = [
        client.get("/api/v1/catalog"),
        client.post("/api/v1/rankings", json={"top_k": 1}),
        client.get("/api/v1/countries/IND/metrics"),
        client.post("/api/v1/comparisons", json={"country_codes": ["IND", "SGP"]}),
    ]

    for response in responses:
        assert response.status_code == 200
        assert "C:\\" not in response.text
        assert "data/raw" not in response.text
        assert "raw_artifact_ids" not in response.text
