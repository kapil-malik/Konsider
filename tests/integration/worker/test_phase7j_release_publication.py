from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.tfc_service import TfcApiService
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.ingestion.phase7_release_publication import (
    BASE_RELEASE_ID,
    FINAL_RELEASE_ID,
    activate_release,
    build_release,
    load_active_tfc_release,
    publish_release,
    replay_release,
    rollback_to_base,
)
from konsider.ingestion.tfc_release import TfcCandidateReleaseRepository, TfcReleaseError

ROOT = Path(__file__).resolve().parents[3]
SOURCE_RELEASES = ROOT / "data" / "releases"
PRODUCTION_CAPTURE = ROOT / "data" / "reports" / "phase7f-2026-08-05" / "production-capture.json"
DISPLAY_CATALOG = load_product_display_catalog(
    ROOT / "data" / "catalogs" / "product-display-catalog.json",
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare(tmp_path: Path) -> tuple[Path, Path]:
    releases = tmp_path / "releases"
    reports = tmp_path / "reports"
    releases.mkdir()
    shutil.copytree(SOURCE_RELEASES / BASE_RELEASE_ID, releases / BASE_RELEASE_ID)
    (releases / "active.json").write_text(
        json.dumps(
            {
                "release_id": BASE_RELEASE_ID,
                "schema_version": "konsider-release-5.1",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return releases, reports


def _publish(tmp_path: Path) -> tuple[Path, Path, Path]:
    releases, reports = _prepare(tmp_path)
    build_release(
        display_catalog=DISPLAY_CATALOG,
        release_root=releases,
        production_capture=PRODUCTION_CAPTURE,
        report_root=reports,
    )
    published = publish_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    return releases, reports, published


def _service(releases: Path, *, with_tfc: bool) -> RecommendationService:
    base = CurrentReleaseRepository(releases).load(releases / BASE_RELEASE_ID)
    opportunity = OpportunityFilterService.from_release(base.path, base.manifest)
    tfc = (
        TfcApiService.from_published(load_active_tfc_release(releases), base.manifest)
        if with_tfc
        else TfcApiService.unavailable()
    )
    return RecommendationService(base, opportunity, tfc)


def _without_feasibility(payload: dict) -> dict:
    result = copy.deepcopy(payload)
    result.get("assessments", {}).pop("feasibility", None)
    for country in result.get("rankings", []):
        country.pop("feasibility", None)
    return result


def test_build_publish_activate_and_rollback_are_strict_and_atomic(tmp_path: Path) -> None:
    releases, reports = _prepare(tmp_path)
    before = (releases / "active.json").read_bytes()
    draft = build_release(
        display_catalog=DISPLAY_CATALOG,
        release_root=releases,
        production_capture=PRODUCTION_CAPTURE,
        report_root=reports,
    )
    assert (releases / "active.json").read_bytes() == before
    loaded_draft = TfcCandidateReleaseRepository(draft.parent).load(draft)
    assert loaded_draft.manifest["status"] == "draft"
    assert not loaded_draft.manifest["activation_authorized"]
    assert loaded_draft.artifacts.catalog["activation_status"] == "ACTIVE"
    assert loaded_draft.artifacts.validation["promotion_eligible"]
    assert (
        replay_release(
            draft,
            display_catalog=DISPLAY_CATALOG,
            production_capture=PRODUCTION_CAPTURE,
        )
        == ()
    )

    published = publish_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    assert (releases / "active.json").read_bytes() == before
    assert not draft.exists()
    assert published == releases / FINAL_RELEASE_ID
    with pytest.raises(FileExistsError):
        publish_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)

    pointer = activate_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    assert _json(pointer) == {
        "release_id": FINAL_RELEASE_ID,
        "schema_version": "konsider-release-6.0",
    }
    overlay = load_active_tfc_release(releases)
    assert overlay is not None
    assert overlay.manifest["status"] == "published"
    assert overlay.manifest["activation_authorized"]
    assert (
        CurrentReleaseRepository(releases).load_active().manifest["release_id"] == BASE_RELEASE_ID
    )
    assert _json(reports / "build-manifest.json")["status"] == "active"

    rollback_to_base(release_root=releases)
    assert _json(pointer) == {
        "release_id": BASE_RELEASE_ID,
        "schema_version": "konsider-release-5.1",
    }
    assert load_active_tfc_release(releases) is None
    assert published.is_dir()


def test_final_release_replays_and_corruption_fails_closed(tmp_path: Path) -> None:
    releases, reports, published = _publish(tmp_path)
    assert (
        replay_release(
            published,
            display_catalog=DISPLAY_CATALOG,
            production_capture=PRODUCTION_CAPTURE,
        )
        == ()
    )
    activate_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    catalog = published / "tfc-catalog.json"
    catalog.write_bytes(catalog.read_bytes() + b"\n")
    with pytest.raises(TfcReleaseError, match="checksum"):
        load_active_tfc_release(releases)


def test_activation_preserves_ranking_and_opportunity_semantics(tmp_path: Path) -> None:
    releases, reports, _ = _publish(tmp_path)
    before = _service(releases, with_tfc=False)
    activate_release(FINAL_RELEASE_ID, release_root=releases, report_root=reports)
    after = _service(releases, with_tfc=True)
    scenarios = (
        ({"political_stability": 1}, ()),
        (
            {"political_stability": 1, "overall_job_market_opportunity": 1},
            ("technology_software_opportunity",),
        ),
    )
    for weights, filters in scenarios:
        baseline = before.rank(
            weights,
            preference_preset_id=None,
            top_k=10,
            opportunity_filter_ids=filters,
        )
        active = after.rank(
            weights,
            preference_preset_id=None,
            top_k=10,
            opportunity_filter_ids=filters,
        )
        assert _without_feasibility(active) == _without_feasibility(baseline)


def test_release_artifacts_exclude_profile_and_deferred_tfc_data(tmp_path: Path) -> None:
    _, _, published = _publish(tmp_path)
    forbidden = {
        "applicant_profile",
        "household_profile",
        "profile_data",
        "session_id",
        "account_id",
        "precomputed_outcome",
    }
    combined = "\n".join(path.read_text(encoding="utf-8") for path in published.iterdir())
    assert forbidden.isdisjoint(
        set().union(
            *(
                set(json.loads(line))
                for line in (published / "tfc-destination-rule-evidence.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
        )
    )
    assert "professional_licensing" not in combined
    assert "locality_cost" not in combined
    assert "SCENARIO_METRIC" not in combined
