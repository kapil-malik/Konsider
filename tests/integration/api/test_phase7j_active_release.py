from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.settings import ApiSettings
from konsider.ingestion.phase7_release_publication import (
    BASE_RELEASE_ID,
    FINAL_RELEASE_ID,
    activate_release,
    build_release,
    publish_release,
)

ROOT = Path(__file__).resolve().parents[3]
PRODUCTION_CAPTURE = ROOT / "data" / "reports" / "phase7f-2026-08-05" / "production-capture.json"


def _settings(tmp_path: Path) -> ApiSettings:
    releases = tmp_path / "releases"
    reports = tmp_path / "reports"
    releases.mkdir()
    shutil.copytree(ROOT / "data" / "releases" / BASE_RELEASE_ID, releases / BASE_RELEASE_ID)
    (releases / "active.json").write_text(
        json.dumps(
            {"release_id": BASE_RELEASE_ID, "schema_version": "konsider-release-5.1"},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    build_release(
        release_root=releases,
        production_capture=PRODUCTION_CAPTURE,
        report_root=reports,
    )
    publish_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    activate_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    return ApiSettings(release_root=releases, active_release_path=releases / "active.json")


def test_default_factory_resolves_active_overlay_and_serves_three_assessment_only_tfcs(
    tmp_path: Path,
) -> None:
    with TestClient(create_app(settings=_settings(tmp_path))) as client:
        health = client.get("/api/v2/health")
        catalog = client.get("/api/v2/tfcs")
        legacy = client.post("/api/v2/rankings", json={"top_k": 3})
        assessed = client.post(
            "/api/v2/rankings",
            json={
                "top_k": 3,
                "feasibility": {
                    "tfc_ids": ["skilled_work_route_feasibility"],
                    "mode": "ASSESS_ONLY",
                },
            },
        )
    assert (
        health.status_code
        == catalog.status_code
        == legacy.status_code
        == assessed.status_code
        == 200
    )
    assert health.json()["release_id"] == BASE_RELEASE_ID
    assert catalog.json()["tfc_release_id"] == FINAL_RELEASE_ID
    assert catalog.json()["release_status"] == "published"
    assert catalog.json()["activation_authorized"] is True
    assert len(catalog.json()["definitions"]) == 3
    assert {row["filter_capability"] for row in catalog.json()["definitions"]} == {"ASSESS_ONLY"}
    assert "feasibility" not in legacy.json()["assessments"]
    assert assessed.json()["assessments"]["feasibility"]["execution_status"] == (
        "NOT_EXECUTED_NO_CONTEXT"
    )
    assert assessed.headers["cache-control"] == "private, no-store"


def test_profile_values_are_not_logged_returned_or_placed_in_urls(tmp_path: Path, caplog) -> None:
    secret = "private-phase7j-profile-value"
    with TestClient(create_app(settings=_settings(tmp_path))) as client:
        response = client.post(
            "/api/v2/rankings",
            json={
                "top_k": 2,
                "feasibility": {
                    "tfc_ids": ["skilled_work_route_feasibility"],
                    "mode": "ASSESS_ONLY",
                    "profile_context": {
                        "occupation": {
                            "user_text": secret,
                            "mapping_state": "UNRESOLVED",
                        }
                    },
                },
            },
        )
    assert response.status_code == 200
    assert secret not in response.text
    assert secret not in caplog.text
    assert secret not in str(response.request.url)
