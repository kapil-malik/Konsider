from pathlib import Path

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]


def test_immutable_phase5g_release_contains_two_real_locality_criteria() -> None:
    release = CurrentReleaseRepository(ROOT / "data" / "releases").load(
        ROOT / "data" / "releases" / "2026-07-29.2"
    )
    assert release.validation["product_ready"] is True
    assert release.manifest["status"] == "published"
    assert release.manifest["artifact_counts"] == {
        "criterion_outcomes": 1274,
        "criterion_policies": 14,
        "derived_country_evidence": 178,
        "geographic_entities": 479,
        "observations": 2034,
        "scores": 2034,
        "source_lineages": 15,
    }

    criteria = {row["id"]: row for row in release.artifacts.consumer_catalog["criteria"]}
    assert criteria["C66"]["display_name"] == "Extreme heat exposure"
    assert criteria["C67"]["display_name"] == "Projected warm-day frequency (2030)"
    assert criteria["C67"]["historical_names"] == ["Long-term climate-change exposure"]
    assert criteria["C67"]["coverage"]["valid_country_count"] == 89
    assert criteria["C67"]["scope"]["derivation"] == "AGGREGATED_FROM_LOCALITIES"


def test_api_exposes_c67_construct_and_common_locality_evidence() -> None:
    with TestClient(create_app()) as client:
        catalog_response = client.get("/api/v2/catalog")
        ranking_response = client.post(
            "/api/v2/rankings",
            json={"weights": {"C66": 1, "C67": 1}},
        )
        details_response = client.post(
            "/api/v2/countries/CAN/details",
            json={"weights": {"C66": 1, "C67": 1}},
        )

    assert catalog_response.status_code == 200
    c67 = next(row for row in catalog_response.json()["criteria"] if row["id"] == "C67")
    assert c67["raw_unit"] == "percent_of_days"
    assert "SSP2-4.5" in c67["description"]
    assert "not an observed outcome" in c67["caveats"][0]
    assert c67["sources"][0]["asset_uri"].endswith("#CL_WDS_245_2030")

    assert ranking_response.status_code == 200
    ranking = ranking_response.json()
    assert ranking["assessments"]["coverage"]["status"] == "PARTIAL_COMPLETE_CASE"
    assert {
        row["country"]["country_codes"][0]
        for row in ranking["assessments"]["coverage"]["excluded_countries"]
    } == {"ATG", "GRD"}
    canada = next(row for row in ranking["rankings"] if row["country"]["country_codes"] == ["CAN"])
    assert canada["assessments"]["locality"]["status"] == "COMMON_LOCALITY_AVAILABLE"
    assert canada["assessments"]["locality"]["common_locality_entity_ids"]

    assert details_response.status_code == 200
    details = details_response.json()
    c67_evidence = next(row for row in details["criteria"] if row["criterion"]["id"] == "C67")[
        "evidence"
    ]
    contributors = c67_evidence["contribution"]["contributing_localities"]
    assert [row["locality"]["display_name"] for row in contributors] == [
        "Edmonton",
        "Montreal",
    ]
