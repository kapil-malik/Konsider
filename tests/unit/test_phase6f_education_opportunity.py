from __future__ import annotations

import json
import hashlib
import tempfile
from collections import Counter
from pathlib import Path

import pytest

from konsider.domain.display_catalog import load_product_display_catalog
from konsider.domain.opportunity_filters import validate_opportunity_filter_release_bundle
from konsider.ingestion import phase6_education_opportunity as phase6f
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = ROOT / "data" / "reports" / "phase6f-2026-08-03"
STAGED_ROOT = REPORT_ROOT / "staged-release"
DISPLAY_CATALOG = load_product_display_catalog(
    ROOT / "data" / "catalogs" / "product-display-catalog.json",
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json",
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _rows() -> list[dict]:
    return _jsonl(STAGED_ROOT / "opportunity-filter-evidence.jsonl")


def _education_rows() -> list[dict]:
    return _jsonl(REPORT_ROOT / "education-opportunity-filter-evidence.jsonl")


def _without_checksum_fields(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: _without_checksum_fields(child)
            for key, child in value.items()
            if "checksum" not in key
        }
    if isinstance(value, list):
        return [_without_checksum_fields(child) for child in value]
    return value


def _semantic_tree(root: Path) -> dict[str, object]:
    tree: dict[str, object] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix == ".jsonl":
            payload: object = [
                json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line
            ]
        elif path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = path.read_bytes()
        tree[relative] = _without_checksum_fields(payload)
    return tree


def test_research_phase6e_and_optional_raw_checksum_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    research = phase6f.verify_research_inputs()
    phase6e = phase6f.verify_phase6e_inputs()
    raw = phase6f.verify_retained_sources(require_all=False)
    assert len(research) >= 17
    assert len(phase6e) >= 10
    assert len(raw) == 13
    assert set(raw.values()) <= {"VERIFIED", "NOT_PRESENT"}
    monkeypatch.setattr(phase6f, "ROOT", tmp_path)
    with pytest.raises(phase6f.EducationOpportunityBuildError, match="unavailable"):
        phase6f.verify_retained_sources(require_all=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "data" / "reports") as temporary:
        checkout_text = Path(temporary) / "checkout.txt"
        checkout_text.write_bytes(b"one\ntwo\n")
        crlf_digest = hashlib.sha256(b"one\r\ntwo\r\n").hexdigest()
        phase6f._verify_checksum(checkout_text, crlf_digest, "Git EOL normalization fixture")


def test_institution_identity_and_promoted_normalization_are_one_to_one() -> None:
    summary = _json(REPORT_ROOT / "institution-identity-summary.json")
    rows = _jsonl(REPORT_ROOT / "institution-normalization.jsonl")
    assert summary["institution_count"] == 2831
    assert summary["unique_ror_count"] == 2831
    assert summary["exact_name_country_count"] == 2825
    assert summary["manual_disambiguation_count"] == 6
    assert summary["many_to_one_ror_count"] == 0
    assert summary["locality_inference_performed"] is False
    assert len(rows) == len({row["source_institution_id"] for row in rows}) == 2831
    assert len({row["ror_id"] for row in rows}) == 2831
    assert all(row["locality"] is None for row in rows)
    assert all(len(row["field_evidence"]) == 4 for row in rows)


def test_identity_validation_fails_closed_when_ror_is_not_one_to_one() -> None:
    rows = _jsonl(phase6f.PHASE6C_ROOT / "institution-mapping.jsonl")
    rows[1] = {**rows[1], "ror_id": rows[0]["ror_id"]}
    with pytest.raises(phase6f.EducationOpportunityBuildError, match="ROR identities"):
        phase6f._validate_institution_mapping(rows)


def test_staged_catalog_and_evidence_are_exact_four_and_nine_filter_matrices() -> None:
    catalog = _json(STAGED_ROOT / "opportunity-filter-catalog.json")
    education_catalog = _json(REPORT_ROOT / "education-opportunity-filter-catalog.json")
    rows = _rows()
    education_rows = _education_rows()
    assert len(catalog["definitions"]) == 9
    assert len(education_catalog["definitions"]) == 4
    assert len(rows) == len({(row["filter_id"], row["country_code"]) for row in rows}) == 819
    assert len(education_rows) == 364
    assert all(
        not item["active"] and item["availability"] == "STAGED" for item in catalog["definitions"]
    )
    assert catalog["activation_status"] == "STAGED_CONTRACT_ONLY"


@pytest.mark.parametrize(
    ("filter_id", "expected"),
    [
        ("engineering_technology_education_opportunity", (27, 48, 16)),
        ("computer_science_ict_education_opportunity", (30, 45, 16)),
        ("medicine_health_sciences_education_opportunity", (30, 45, 16)),
        ("natural_sciences_education_opportunity", (31, 44, 16)),
    ],
)
def test_education_state_counts_match_frozen_phase6c(
    filter_id: str, expected: tuple[int, int, int]
) -> None:
    counts = Counter(row["state"] for row in _education_rows() if row["filter_id"] == filter_id)
    assert tuple(counts[state] for state in phase6f.STATE_ORDER) == expected


def test_country_absence_is_insufficient_and_complete_nonpass_is_not_established() -> None:
    by_pair = {(row["filter_id"], row["country_code"]): row for row in _education_rows()}
    for config in phase6f.FILTERS:
        absent = by_pair[(config.filter_id, "ALB")]
        assert absent["state"] == "INSUFFICIENT_EVIDENCE"
        assert absent["reason_codes"] == ["COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE"]
        assert absent["metric_payload"] is None
        assert absent["coverage_completeness"] == "UNASSESSED"

        represented_nonpass = next(
            row
            for row in _education_rows()
            if row["filter_id"] == config.filter_id
            and row["state"] == "STRONG_SIGNAL_NOT_ESTABLISHED"
        )
        assert represented_nonpass["coverage_completeness"] == "COMPLETE"
        assert represented_nonpass["reason_codes"] == ["NO_APPROVED_STRONG_ROUTE_PASSED"]
        assert represented_nonpass["metric_payload"] is not None


def test_all_five_routes_are_retained_with_exact_components_and_reconcile() -> None:
    rows = [row for row in _education_rows() if row["state"] != "INSUFFICIENT_EVIDENCE"]
    assert all(row["evaluated_route_ids"] == list(phase6f.ROUTE_IDS) for row in rows)
    observed_routes = {route for row in rows for route in row["establishing_route_ids"]}
    assert observed_routes == set(phase6f.ROUTE_IDS)
    for row in rows:
        results = {result["route_id"]: result for result in row["threshold_results"]}
        assert set(results) == set(phase6f.ROUTE_IDS)
        assert row["establishing_route_ids"] == [
            route_id for route_id in phase6f.ROUTE_IDS if results[route_id]["passed"]
        ]
        metrics = row["metric_payload"]
        assert results["top_100_institution"]["passed"] == (metrics["top_100_count"] >= 1)
        assert results["top_300_breadth"]["passed"] == (metrics["top_300_count"] >= 3)


def test_thresholds_are_frozen_global_p60_with_no_country_exceptions() -> None:
    policies = _json(STAGED_ROOT / "opportunity-filter-threshold-policies.json")["policies"]
    by_id = {row["filter_id"]: row for row in policies}
    for config in phase6f.FILTERS:
        policy = by_id[config.filter_id]
        assert policy["global_only"] is True
        assert [route["route_id"] for route in policy["routes"]] == list(phase6f.ROUTE_IDS)
        assert all(route["parameters"]["frozen_percentile"] == "P60" for route in policy["routes"])
        assert all(route["parameters"]["country_exceptions"] is False for route in policy["routes"])
        assert policy["policy_version"] == config.threshold_policy_version


def test_institution_aggregation_reproduces_country_metrics() -> None:
    institutions = _jsonl(REPORT_ROOT / "institution-normalization.jsonl")
    evidence = {
        (row["filter_id"], row["country_code"]): row
        for row in _education_rows()
        if row["metric_payload"] is not None
    }
    for config in phase6f.FILTERS:
        for country_code in {
            country for filter_id, country in evidence if filter_id == config.filter_id
        }:
            field_rows = [
                row["field_evidence"][config.filter_id]
                for row in institutions
                if row["stable_country_code"] == country_code
                and not row["field_evidence"][config.filter_id]["redacted"]
            ]
            metrics = evidence[(config.filter_id, country_code)]["metric_payload"]
            assert metrics["fractional_publication_output"] == sum(
                row["fractional_publications"] for row in field_rows
            )
            assert metrics["active_university_breadth"] == len(field_rows)
            assert metrics["top_100_count"] == sum(row["top_100"] for row in field_rows)
            assert metrics["top_200_count"] == sum(row["top_200"] for row in field_rows)
            assert metrics["top_300_count"] == sum(row["top_300"] for row in field_rows)


def test_source_dependency_boundary_and_crosswalk_are_noncausal_metadata_only() -> None:
    catalog = _json(STAGED_ROOT / "opportunity-filter-catalog.json")
    education = [row for row in catalog["definitions"] if row["category"] == "EDUCATION"]
    assert all(
        row["source_dependency"]
        == {
            "mode": "MULTI_SOURCE",
            "required_source_ids": [phase6f.CWTS_SOURCE_ID, phase6f.ROR_SOURCE_ID],
            "failure_state": "INSUFFICIENT_EVIDENCE",
        }
        for row in education
    )
    boundary_text = " ".join(text for row in education for text in row["does_not_mean"]).lower()
    for prohibited in (
        "teaching",
        "admissions",
        "tuition",
        "accreditation",
        "visa",
        "campus",
        "language",
        "employment outcomes",
        "applicant success",
    ):
        assert prohibited in boundary_text
    crosswalk = _json(REPORT_ROOT / "career-education-crosswalk.json")
    assert crosswalk["runtime_taxonomy_change_authorized"] is False
    assert (
        crosswalk["phase6f_usage"]
        == "EXPLANATORY_METADATA_ONLY_NO_STATE_MERGING_CAUSALITY_OR_RUNTIME_TAXONOMY"
    )


def test_excluded_constructs_are_not_onboarded_and_shortlist_coverage_is_20_of_20() -> None:
    catalog_ids = {
        row["id"] for row in _json(STAGED_ROOT / "opportunity-filter-catalog.json")["definitions"]
    }
    assert "business_finance_education_opportunity" not in catalog_ids
    assert "broad_university_excellence_opportunity" not in catalog_ids
    reconciliation = _json(REPORT_ROOT / "research-production-reconciliation.json")
    assert reconciliation["shortlist_coverage"]["mismatches"] == []
    for profiles in reconciliation["shortlist_coverage"]["filters"].values():
        for result in profiles.values():
            assert result["actual"]["assessable_count"] == 20
            assert result["actual"]["ordering_changed"] is False


def test_phase6f_candidate_remains_draft_after_final_activation() -> None:
    manifest = _json(STAGED_ROOT / "candidate-release-manifest.json")
    catalog = _json(STAGED_ROOT / "opportunity-filter-catalog.json")
    countries = [
        row["code"]
        for row in _json(ROOT / "data" / "country-universes" / "stable-supported-v1.json")[
            "countries"
        ]
    ]
    assert manifest["schema_version"] == "konsider-release-5.1"
    assert manifest["status"] == "draft"
    validate_opportunity_filter_release_bundle(manifest, catalog, _rows(), countries)
    loaded = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    assert loaded.manifest["release_id"] == "2026-08-07.1"
    assert "opportunity_filters" in loaded.manifest
    assert loaded.manifest["schema_version"] == "konsider-release-5.2"
    assert _json(ROOT / "data" / "releases" / "active.json") == {
        "release_id": "2026-08-07.2",
        "schema_version": "konsider-release-6.1",
    }


def test_no_opportunity_artifact_contains_score_or_weight_fields() -> None:
    prohibited = {"score", "scores", "weight", "weights", "affinity_score", "ranking_score"}

    def walk(value: object) -> None:
        if isinstance(value, dict):
            assert not (set(value) & prohibited)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(_json(STAGED_ROOT / "opportunity-filter-catalog.json"))
    for row in _rows():
        walk(row)


def test_regeneration_is_semantically_identical_without_raw_source_dependency() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT / "data" / "reports") as temporary:
        generated = Path(temporary) / "generated"
        phase6f.build_education_opportunity_bundle(generated, display_catalog=DISPLAY_CATALOG)
        assert _semantic_tree(generated) == _semantic_tree(REPORT_ROOT)
