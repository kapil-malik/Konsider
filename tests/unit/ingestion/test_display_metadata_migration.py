import json
import shutil
from pathlib import Path

from jsonschema import Draft202012Validator

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.tfc_service import TfcApiService
from konsider.api.v2_service import RecommendationService
from konsider.api.v3_service import RecommendationServiceV3
from konsider.ingestion.display_metadata_migration import (
    SOURCE_BASE_ID,
    SOURCE_OVERLAY_ID,
    activate_overlay,
    build_drafts,
    publish_pair,
)
from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.ingestion.phase7_release_publication import load_active_tfc_release
from konsider.ingestion.tfc_release import TfcCandidateReleaseRepository

ROOT = Path(__file__).resolve().parents[3]
UNCHANGED_BASE_FILES = {
    "aggregation-policies.json",
    "criterion-outcomes.jsonl",
    "criterion-policies.json",
    "derived-country-evidence.jsonl",
    "geographic-entities.jsonl",
    "locality-universes.json",
    "observations.jsonl",
    "opportunity-filter-coverage-summary.json",
    "opportunity-filter-evidence-policy.json",
    "opportunity-filter-evidence.jsonl",
    "opportunity-filter-source-manifest.json",
    "opportunity-filter-threshold-policies.json",
    "scores.jsonl",
    "source-lineages.json",
    "validation.json",
}


def _catalog():
    return load_product_display_catalog(
        ROOT / "data" / "catalogs" / "product-display-catalog.json",
        ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
    )


def _roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    releases = tmp_path / "releases"
    shutil.copytree(ROOT / "data" / "releases" / SOURCE_BASE_ID, releases / SOURCE_BASE_ID)
    shutil.copytree(ROOT / "data" / "releases" / SOURCE_OVERLAY_ID, releases / SOURCE_OVERLAY_ID)
    shutil.copyfile(ROOT / "data" / "releases" / "active.json", releases / "active.json")
    return releases, tmp_path / "reports", tmp_path / "catalogs"


def test_generation_five_schemas_are_valid() -> None:
    for path in (ROOT / "contracts" / "schemas" / "v5").glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_build_publish_and_activate_uniform_release_pair(tmp_path: Path) -> None:
    releases, reports, catalogs = _roots(tmp_path)
    base_draft, overlay_draft = build_drafts(
        release_root=releases,
        report_root=reports,
        display_catalog=_catalog(),
        base_release_id="new-base",
        overlay_release_id="new-overlay",
    )
    base_manifest = json.loads((base_draft / "manifest.json").read_text(encoding="utf-8"))
    overlay_manifest = json.loads((overlay_draft / "manifest.json").read_text(encoding="utf-8"))
    assert base_manifest["schema_version"] == "konsider-release-5.2"
    assert overlay_manifest["schema_version"] == "konsider-release-6.1"
    assert overlay_manifest["base_release"]["release_checksum"] == base_manifest["release_checksum"]
    assert base_manifest["display_metadata_equivalence"]["status"] == "PASSED"
    assert all(
        "display_name" not in item and "category" not in item
        for item in json.loads((base_draft / "consumer-catalog.json").read_text(encoding="utf-8"))[
            "criteria"
        ]
    )
    assert all(
        "name" not in item and "tfc_id" not in item
        for item in json.loads((overlay_draft / "tfc-catalog.json").read_text(encoding="utf-8"))[
            "definitions"
        ]
    )
    for filename in UNCHANGED_BASE_FILES:
        assert (base_draft / filename).read_bytes() == (
            releases / SOURCE_BASE_ID / filename
        ).read_bytes()

    base, overlay = publish_pair(
        release_root=releases,
        catalog_snapshot_root=catalogs,
        base_release_id="new-base",
        overlay_release_id="new-overlay",
    )
    assert base.is_dir() and overlay.is_dir()
    loaded_base = CurrentReleaseRepository(releases).load(base)
    loaded_overlay = TfcCandidateReleaseRepository(releases).load(overlay)
    assert loaded_base.manifest["release_id"] == "new-base"
    assert loaded_overlay.manifest["release_id"] == "new-overlay"
    legacy_service = RecommendationService(
        loaded_base,
        OpportunityFilterService.from_release(base, loaded_base.manifest),
        TfcApiService.from_published(loaded_overlay, loaded_base.manifest),
    )
    service = RecommendationServiceV3(legacy_service)
    catalog = service.catalog()
    filters = service.opportunity_filter_catalog()
    tfcs = service.tfc_catalog()
    assert catalog["api_contract_version"] == "konsider-api-3.0"
    assert all(
        {"id", "displayName", "compactName", "sectionId", "sectionName", "sortOrder"}
        <= definition.keys()
        for definition in catalog["criteria"] + filters["definitions"] + tfcs["definitions"]
    )
    assert [section["sectionName"] for section in filters["sections"]] == [
        "Career",
        "Education",
    ]
    assert "display_name" in legacy_service.catalog()["criteria"][0]
    ranking = service.rank(None, preference_preset_id=None, top_k=1)
    assert ranking["rankings"][0]["contributions"][0]["displayName"]
    assert "criterion_name" not in ranking["rankings"][0]["contributions"][0]
    pointer = activate_overlay(release_root=releases, overlay_release_id="new-overlay")
    assert json.loads(pointer.read_text(encoding="utf-8")) == {
        "release_id": "new-overlay",
        "schema_version": "konsider-release-6.1",
    }
    assert load_active_tfc_release(releases, pointer) is not None
    assert (
        CurrentReleaseRepository(releases).load_active(pointer).manifest["release_id"] == "new-base"
    )
