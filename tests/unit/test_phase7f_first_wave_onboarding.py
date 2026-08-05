import copy
import json
import re
from pathlib import Path

from konsider.domain.tfc_assessment import TfcAssessmentEngine
from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.tfc_first_wave import (
    FIRST_WAVE_TFC_IDS,
    SUPPORTED_COUNTRIES,
    build_first_wave_production_capture,
    reconcile_phase7b,
    source_asset_specs,
    validate_source_capture,
)
from konsider.ingestion.tfc_release import (
    PAYLOAD_FILES,
    TfcCandidateReleaseRepository,
    build_tfc_release_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "data" / "reports" / "phase7f-2026-08-05"
SOURCE_CAPTURE_PATH = REPORT / "phase7f-source-capture.json"
PRODUCTION_CAPTURE_PATH = REPORT / "production-capture.json"
RECONCILIATION_PATH = REPORT / "research-production-reconciliation.json"
RESEARCH_SUPPORT_PATH = (
    ROOT / "data" / "reports" / "phase7b-2026-08-05" / "country-support-matrix.jsonl"
)
CANDIDATE = REPORT / "staged-release" / "phase7f-first-wave-2026-08-05.6.0"
ACTIVE_RELEASE = ROOT / "data" / "releases" / "2026-08-04.1"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _all_keys(value) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _all_keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()


def _ranking(rank: int, code: str) -> dict:
    return {
        "rank": rank,
        "base_rank": rank,
        "country": {
            "entity_id": f"country:{code}",
            "entity_type": "COUNTRY",
            "display_name": code,
            "country_codes": [code],
            "region": None,
        },
        "total_score": 9.0 - rank,
        "contributions": [
            {
                "criterion_id": "existing_affinity",
                "normalized_weight": 1.0,
                "contribution": 9.0 - rank,
            }
        ],
        "assessments": {
            "coverage": {"status": "PCC_PRESERVED"},
            "locality": {"status": "LSC_PRESERVED"},
            "opportunity": {"status": "OFC_PRESERVED"},
        },
    }


def _payload() -> dict:
    return {
        "release_id": "2026-08-04.1",
        "normalized_weights": {"existing_affinity": 1.0},
        "rankings": [_ranking(1, "DEU"), _ranking(2, "ALB")],
        "assessments": {
            "coverage": {"status": "PCC_PRESERVED"},
            "locality": {"status": "LSC_PRESERVED"},
            "profile": {"status": "PROFILE_ASSESSMENT_PRESERVED"},
            "opportunity": {"status": "OFC_PRESERVED"},
        },
    }


def _context() -> dict:
    taxonomy = {
        "user_text": "Synthetic reference",
        "taxonomy_id": "synthetic",
        "taxonomy_version": "1",
        "code": "SYN-1",
        "mapping_state": "MAPPED",
    }
    return {
        "applicant": {
            "citizenships": ["IND"],
            "age_years": 31,
            "occupation": copy.deepcopy(taxonomy),
            "qualifications": [{"level": "MASTERS"}],
            "unknown_fields": [],
        },
        "household": {
            "partner_status": "SPOUSE",
            "partner_accompanying": True,
            "dependants": [{"role": "DEPENDENT_CHILD", "relocating": True, "age_band": "UNDER_18"}],
            "unknown_fields": [],
        },
        "scenario": {
            "purpose": "EXPLORATION",
            "target_date": "2026-08-05",
            "target_country_codes": ["DEU", "ALB"],
            "target_region_ids": [],
            "target_locality_ids": [],
            "job_offer": {
                "state": "PRESENT",
                "role": "Synthetic role",
                "salary": {"amount": 80000, "currency": "EUR", "period": "ANNUAL"},
            },
            "intended_study": {
                "institution": copy.deepcopy(taxonomy),
                "qualification_level": "MASTERS",
                "field": copy.deepcopy(taxonomy),
                "duration_months": 24,
                "mode": "IN_PERSON",
                "completion_date": "2026-07-01",
                "completion_state": "COMPLETED",
            },
            "primary_route_id": "EU.BLUE_CARD.DEU",
            "relocation_composition": "WITH_PARTNER_AND_DEPENDANTS",
            "unknown_fields": [],
        },
    }


def test_exact_first_wave_inventory_is_frozen_at_three_by_29() -> None:
    specs = source_asset_specs()
    assert len(FIRST_WAVE_TFC_IDS) == 3
    assert len(SUPPORTED_COUNTRIES) == 29
    assert len(specs) == 87
    assert len({row.asset_id for row in specs}) == 87
    assert len({(row.tfc_id, row.country_code) for row in specs}) == 87
    assert {row.tfc_id for row in specs} == set(FIRST_WAVE_TFC_IDS)
    assert {row.country_code for row in specs} == set(SUPPORTED_COUNTRIES)
    sweden = next(
        row
        for row in specs
        if row.tfc_id == "post_study_work_pathway" and row.country_code == "SWE"
    )
    assert sweden.route_id == "EU.STUDENT.TO_WORK.SWE"
    assert "status change" in sweden.route_name


def test_frozen_source_capture_has_verified_identity_without_raw_bodies() -> None:
    capture = _json(SOURCE_CAPTURE_PATH)
    validate_source_capture(capture)
    assert capture["raw_retention_policy"] == "CHECKSUM_ONLY_NORMALIZED_DERIVATIVE"
    assert len(capture["assets"]) == 87
    assert sum(row["capture_method"] == "DIRECT_HTTP_CHECKSUM" for row in capture["assets"]) == 84
    assert (
        sum(row["capture_method"] == "BROWSER_RENDERED_DOM_CHECKSUM" for row in capture["assets"])
        == 3
    )
    for row in capture["assets"]:
        assert row["http_status"] == 200
        assert row["byte_count"] > 0
        assert re.fullmatch(r"sha256:[a-f0-9]{64}", row["content_checksum"])
        assert "content" not in row and "raw_body" not in row


def test_production_artifacts_have_complete_support_and_conditional_rules() -> None:
    capture = _json(PRODUCTION_CAPTURE_PATH)
    artifacts = build_tfc_release_artifacts(capture)
    definitions = artifacts.catalog["definitions"]
    rules = [row for row in artifacts.rule_evidence if row["record_type"] == "ROUTE_RULE"]
    supports = [
        row for row in artifacts.rule_evidence if row["record_type"] == "DESTINATION_SUPPORT"
    ]

    assert artifacts.catalog["synthetic"] is False
    assert artifacts.catalog["activation_status"] == "RELEASE_CANDIDATE"
    assert len(definitions) == 3
    assert {row["tfc_id"] for row in definitions} == set(FIRST_WAVE_TFC_IDS)
    assert all(row["filter_capability"] == "ASSESS_ONLY" for row in definitions)
    assert all(len(row["supported_destination_codes"]) == 29 for row in definitions)
    assert len(supports) == 273 == 3 * len(COUNTRY_CODES)
    assert len({(row["tfc_id"], row["country_code"]) for row in supports}) == 273
    assert sum(row["support_status"] == "SUPPORTED" for row in supports) == 87
    assert sum(row["support_status"] == "UNSUPPORTED" for row in supports) == 186
    assert {row["reason_code"] for row in supports if row["support_status"] == "UNSUPPORTED"} == {
        "DESTINATION_OUTSIDE_APPROVED_SOURCE_BOUNDARY"
    }
    assert len(rules) == 116
    assert len({row["route_id"] for row in rules}) == 116
    assert {
        row["tfc_id"]: sum(rule["tfc_id"] == row["tfc_id"] for rule in rules) for row in definitions
    } == {
        "skilled_work_route_feasibility": 29,
        "family_accompaniment_reunification": 58,
        "post_study_work_pathway": 29,
    }
    assert all(
        row["evaluation_boundary"] == "CONDITIONAL_EXTERNAL_CONFIRMATION_REQUIRED" for row in rules
    )
    assert all(row["effective_period"]["effective_from"] == "2026-08-05" for row in rules)
    assert all(row["effective_period"]["stale_after"] == "2026-11-05" for row in rules)
    assert artifacts.validation["structural_passed"] is True


def test_source_legal_manifest_and_research_reconciliation_are_release_ready() -> None:
    capture = _json(PRODUCTION_CAPTURE_PATH)
    sources = capture["source_legal_manifest"]["sources"]
    reconciliation = _json(RECONCILIATION_PATH)

    assert len(sources) == 5
    assert capture["source_legal_manifest"]["synthetic"] is False
    assert all(row["production_use_decision"] == "APPROVED_STAGED" for row in sources)
    assert all(row["manual_review_status"] == "APPROVED" for row in sources)
    assert all(
        row["raw_retention_policy"] == "CHECKSUM_ONLY_NORMALIZED_DERIVATIVE" for row in sources
    )
    assert all(row["access_and_licence"] and row["attribution"] for row in sources)
    assert reconciliation["status"] == "PASSED"
    assert reconciliation["discrepancies"] == []
    assert set(reconciliation["actual_supported_count_per_tfc"].values()) == {29}
    assert reconciliation["route_rule_count_per_tfc"] == {
        "family_accompaniment_reunification": 58,
        "post_study_work_pathway": 29,
        "skilled_work_route_feasibility": 29,
    }


def test_reconciliation_requires_owner_review_for_any_support_mismatch() -> None:
    capture = _json(PRODUCTION_CAPTURE_PATH)
    research = _jsonl(RESEARCH_SUPPORT_PATH)
    changed = copy.deepcopy(research)
    row = next(
        item
        for item in changed
        if item["tfc_id"] == "post_study_work_pathway" and item["country_code"] == "SWE"
    )
    row["research_support_state"] = "SOURCE_NOT_ASSESSABLE"
    result = reconcile_phase7b(capture, changed)
    assert result["status"] == "OWNER_APPROVAL_REQUIRED"
    assert result["discrepancies"] == [
        {
            "tfc_id": "post_study_work_pathway",
            "country_code": "SWE",
            "research_state": "SOURCE_NOT_ASSESSABLE",
            "production_state": "SUPPORTED",
            "approval_required": True,
        }
    ]


def test_three_checks_assess_conditionally_without_changing_ranking_or_ofc() -> None:
    capture = _json(PRODUCTION_CAPTURE_PATH)
    engine = TfcAssessmentEngine(
        build_tfc_release_artifacts(capture),
        active_release_id="2026-08-04.1",
        tfc_release_id="phase7f-first-wave-2026-08-05.6.0",
    )
    payload = _payload()
    original = copy.deepcopy(payload)
    run = engine.assess_ranking_payload(
        payload,
        context=_context(),
        selected_tfc_ids=list(FIRST_WAVE_TFC_IDS),
        evaluation_date="2026-08-05",
    )
    deu = next(row for row in run.assessment["countries"] if row["country_code"] == "DEU")
    alb = next(row for row in run.assessment["countries"] if row["country_code"] == "ALB")

    assert run.payload["rankings"] == original["rankings"]
    for key in ("coverage", "locality", "profile", "opportunity"):
        assert run.payload["assessments"][key] == original["assessments"][key]
    assert all(outcome["common_status"] == "EVALUATED" for outcome in deu["outcomes"])
    assert all(
        outcome["result"]["match_classification"] == "CONDITIONAL_ROUTE_MATCH"
        for outcome in deu["outcomes"]
    )
    assert all(
        route["classification"] == "CONDITIONAL"
        for outcome in deu["outcomes"]
        for route in outcome["result"]["routes"]
    )
    assert all(outcome["common_status"] == "UNSUPPORTED" for outcome in alb["outcomes"])
    assert all(
        outcome["reason_codes"] == ["DESTINATION_NOT_SUPPORTED"] for outcome in alb["outcomes"]
    )
    assert run.assessment["no_change_affinity"] is True


def test_artifacts_contain_no_profile_values_ranking_or_opportunity_fields() -> None:
    capture = _json(PRODUCTION_CAPTURE_PATH)
    keys = _all_keys(capture)
    assert not {"profile_id", "rank", "base_rank", "total_score", "contributions"} & keys
    assert not {"opportunity", "ofc", "pcc", "lsc"} & {key.casefold() for key in keys}
    rendered = json.dumps(capture, sort_keys=True)
    assert "Synthetic reference" not in rendered
    assert "SYN-1" not in rendered


def test_staged_candidate_is_non_active_and_replays_without_diff() -> None:
    manifest = _json(CANDIDATE / "manifest.json")
    active_manifest = _json(ACTIVE_RELEASE / "manifest.json")
    replay = TfcCandidateReleaseRepository(CANDIDATE.parent).replay(
        CANDIDATE, _json(PRODUCTION_CAPTURE_PATH)
    )

    assert manifest["schema_version"] == "konsider-release-6.0"
    assert manifest["status"] == "draft"
    assert manifest["synthetic"] is False
    assert manifest["activation_authorized"] is False
    assert manifest["base_release"]["release_id"] == active_manifest["release_id"]
    assert manifest["base_release"]["release_checksum"] == active_manifest["release_checksum"]
    assert replay.passed
    assert replay.mismatched_files == ()
    assert replay.compared_files == (*PAYLOAD_FILES, "manifest.json")


def test_generated_production_capture_is_deterministic_from_frozen_source_capture() -> None:
    rebuilt = build_first_wave_production_capture(
        _json(SOURCE_CAPTURE_PATH),
        release_id="phase7f-first-wave-2026-08-05.6.0",
        validation_date="2026-08-05",
    )
    assert rebuilt == _json(PRODUCTION_CAPTURE_PATH)
