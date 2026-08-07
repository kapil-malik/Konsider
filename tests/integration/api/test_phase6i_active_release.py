from __future__ import annotations

import copy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[3]
RELEASES = ROOT / "data" / "releases"
FINAL_RELEASE_ID = "2026-08-04.1"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _final_service() -> RecommendationService:
    repository = CurrentReleaseRepository(RELEASES)
    draft = RELEASES / ".draft" / FINAL_RELEASE_ID
    release = repository.load(draft if draft.exists() else RELEASES / FINAL_RELEASE_ID)
    opportunity = OpportunityFilterService(
        release_id=FINAL_RELEASE_ID,
        catalog=_json(release.path / "opportunity-filter-catalog.json"),
        evidence_rows=_jsonl(release.path / "opportunity-filter-evidence.jsonl"),
        source_manifest=_json(release.path / "opportunity-filter-source-manifest.json"),
        coverage_summary=_json(release.path / "opportunity-filter-coverage-summary.json"),
        evidence_policy=_json(release.path / "opportunity-filter-evidence-policy.json"),
    )
    return RecommendationService(release, opportunity)


def _without_release_or_opportunity(payload: dict) -> dict:
    comparable = copy.deepcopy(payload)
    comparable.pop("release_id", None)
    comparable.pop("release_schema_version", None)
    comparable.get("assessments", {}).pop("opportunity", None)
    return comparable


def test_final_payload_preserves_prior_ranking_exactly() -> None:
    repository = CurrentReleaseRepository(RELEASES)
    prior = RecommendationService(repository.load(RELEASES / "2026-07-29.2"))
    final = _final_service()
    scenarios = (
        (None, None),
        ({"political_stability": 1}, None),
        ({"political_stability": 1, "rule_of_law": 2}, 10),
    )
    for weights, top_k in scenarios:
        old = prior.rank(
            weights,
            preference_preset_id=None,
            top_k=top_k,
            opportunity_filter_ids=(),
        )
        new = final.rank(
            weights,
            preference_preset_id=None,
            top_k=top_k,
            opportunity_filter_ids=(),
        )
        assert _without_release_or_opportunity(new) == _without_release_or_opportunity(old)


def test_default_application_loads_final_active_release_without_override() -> None:
    active = CurrentReleaseRepository(RELEASES).load_active()
    assert active.manifest["release_id"] == "2026-08-07.3"
    assert active.manifest["schema_version"] == "konsider-release-5.2"
    assert active.manifest["artifact_counts"]["opportunity_filter_definitions"] == 9
    assert active.manifest["artifact_counts"]["opportunity_filter_evidence"] == 819

    with TestClient(create_app()) as client:
        health = client.get("/api/v2/health")
        catalog = client.get("/api/v2/opportunity-filters")
        ranking = client.post(
            "/api/v2/rankings",
            json={
                "top_k": 5,
                "opportunity_filters": {
                    "mode": "ALL_REQUIRED",
                    "required_filter_ids": ["technology_software_opportunity"],
                },
            },
        )
    assert health.status_code == catalog.status_code == ranking.status_code == 200
    assert health.json()["release_id"] == "2026-08-07.3"
    assert catalog.json()["opportunity_release_id"] == "2026-08-07.3"
    assert len(catalog.json()["definitions"]) == 9
    assert ranking.json()["assessments"]["opportunity"]["passing_country_count"] == 20
