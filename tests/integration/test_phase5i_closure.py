import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
RELEASE_ID = "2026-08-07.1"
DEPRECATED_PUBLIC_FIELDS = {
    "profiles",
    "profile_id",
    "resolved_profile_id",
    "uncertainty_status",
    "locality_status",
}


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for item in value.values() for key in _all_keys(item)}
    if isinstance(value, list):
        return {key for item in value for key in _all_keys(item)}
    return set()


def test_phase5_dispositions_and_fast_follow_register_cover_all_45_criteria() -> None:
    matrix = json.loads(
        (
            ROOT / "data" / "reports" / "phase5a-2026-07-28" / "criterion-disposition-matrix.json"
        ).read_text(encoding="utf-8")
    )
    rows = matrix["matrix"]

    assert len(rows) == len({row["criterion_id"] for row in rows}) == 45
    assert {row["recommendation"] for row in rows} == {
        "FIRST_WAVE",
        "SECOND_WAVE",
        "RESEARCH_ONLY",
        "PROFILE_PHASE",
        "REJECT_LOCALITY_PROXY",
    }

    onboarded = {
        json.loads(path.read_text(encoding="utf-8"))["criterion_id"]
        for path in (
            ROOT / "data" / "reports" / "phase5g-c66-2026-07-29" / "onboarding-disposition.json",
            ROOT / "data" / "reports" / "phase5g-c67-2026-07-29" / "onboarding-disposition.json",
        )
    }
    assert onboarded == {"C66", "C67"}
    assert {row["criterion_id"] for row in rows} - onboarded == {
        "C01",
        "C05",
        "C06",
        "C08",
        "C11",
        "C12",
        "C13",
        "C14",
        "C15",
        "C16",
        "C17",
        "C19",
        "C21",
        "C22",
        "C25",
        "C26",
        "C29",
        "C30",
        "C32",
        "C33",
        "C34",
        "C35",
        "C36",
        "C38",
        "C40",
        "C42",
        "C45",
        "C48",
        "C49",
        "C50",
        "C53",
        "C54",
        "C56",
        "C57",
        "C58",
        "C62",
        "C68",
        "C69",
        "C70",
        "C71",
        "C75",
        "C76",
        "C78",
    }


def test_active_release_catalog_validation_api_and_licences_agree() -> None:
    release = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    manifest = release.manifest
    artifacts = release.artifacts
    catalog = artifacts.consumer_catalog

    assert manifest["release_id"] == RELEASE_ID
    assert manifest["schema_version"] == "konsider-release-5.2"
    assert manifest["catalog_schema_version"] == "consumer-catalog-4.0"
    assert manifest["status"] == "published"
    assert release.validation["structural_passed"] is True
    assert release.validation["lineage_passed"] is True
    assert release.validation["locality_policy_passed"] is True
    assert release.validation["product_ready"] is True
    assert {row["id"] for row in catalog["criteria"]} == set(manifest["criteria"])
    assert {row["id"] for row in catalog["criteria"] if row["ready"]} == {
        criterion_id
        for criterion_id, coverage in release.validation["criterion_coverage"].items()
        if coverage["mode"] != "DIAGNOSTIC_ONLY"
    }

    for lineage in artifacts.source_lineages:
        for source in lineage["sources"]:
            assert source["licence_id"]
            assert source["checksum"]
            assert source["asset_uri"]
    locality_sources = {
        source["source_id"]: source
        for lineage in artifacts.source_lineages
        for source in lineage["sources"]
        if source["source_id"] == "jrc-ghs-ucdb-climate"
    }
    assert locality_sources["jrc-ghs-ucdb-climate"]["licence_id"] == "CC-BY-4.0"

    with TestClient(create_app()) as client:
        catalog_response = client.get("/api/v2/catalog")
        ranking_response = client.post(
            "/api/v2/rankings",
            json={"weights": {"C66": 0.6, "C67": 0.6}},
        )
        diagnostic_response = client.post(
            "/api/v2/rankings",
            json={"weights": {"uhc_service_coverage_index": 1}},
        )

    assert catalog_response.status_code == ranking_response.status_code == 200
    assert diagnostic_response.status_code == 422
    public_catalog = catalog_response.json()
    ranking = ranking_response.json()
    assert public_catalog["release_id"] == manifest["release_id"]
    assert public_catalog["release_schema_version"] == manifest["schema_version"]
    assert public_catalog["catalog_schema_version"] == catalog["schema_version"]
    assert {row["id"] for row in public_catalog["criteria"]} == set(manifest["criteria"])
    assert set(ranking["assessments"]) == {
        "coverage",
        "locality",
        "profile",
        "opportunity",
    }
    assert ranking["assessments"]["coverage"]["status"] == "PARTIAL_COMPLETE_CASE"
    assert ranking["assessments"]["locality"]["status"] in {
        "COMMON_LOCALITY_AVAILABLE",
        "MIXED_COUNTRY_RESULTS",
    }
    assert ranking["assessments"]["profile"]["status"] == "NO_PROFILE_CONTEXT"
    assert ranking["assessments"]["profile"]["evaluated_dimensions"] == []
    assert {reason["effect"] for reason in ranking["assessments"]["profile"]["reasons"]} == {
        "NOT_EVALUATED"
    }
    assert ranking["assessments"]["opportunity"]["status"] == "NO_FILTERS_ACTIVE"
    assert ranking["assessments"]["opportunity"]["active_filter_ids"] == []
    assert DEPRECATED_PUBLIC_FIELDS.isdisjoint(_all_keys(public_catalog))
    assert DEPRECATED_PUBLIC_FIELDS.isdisjoint(_all_keys(ranking))

    active_criteria = set(
        ranking["assessments"]["coverage"]["active_global_core_criterion_ids"]
    ) | set(ranking["assessments"]["coverage"]["active_conditional_criterion_ids"])
    excluded_codes = {
        row["country"]["country_codes"][0]
        for row in ranking["assessments"]["coverage"]["excluded_countries"]
    }
    assert excluded_codes == {"ATG", "GRD"}
    for country in ranking["rankings"]:
        assert {row["criterion_id"] for row in country["contributions"]} == active_criteria
        assert country["assessments"]["profile"]["status"] == "NO_PROFILE_CONTEXT"
