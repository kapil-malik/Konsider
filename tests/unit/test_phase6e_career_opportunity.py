import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from konsider.domain.opportunity_filters import (
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_bundle,
)
from konsider.ingestion import phase6_career_opportunity as phase6e
from konsider.ingestion.current_release import CurrentReleaseRepository

ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = ROOT / "data" / "reports" / "phase6e-2026-08-03"
STAGED_ROOT = REPORT_ROOT / "staged-release"
STATE_ORDER = (
    "VERIFIED_STRONG_SIGNAL",
    "STRONG_SIGNAL_NOT_ESTABLISHED",
    "INSUFFICIENT_EVIDENCE",
)
EXPECTED_COUNTS = {
    "technology_software_opportunity": (20, 43, 28),
    "science_engineering_opportunity": (20, 47, 24),
    "health_social_work_opportunity": (27, 61, 3),
    "finance_insurance_opportunity": (22, 66, 3),
    "skilled_trades_construction_opportunity": (34, 54, 3),
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _staged_rows() -> list[dict]:
    return _jsonl(STAGED_ROOT / "opportunity-filter-evidence.jsonl")


def _by_pair() -> dict[tuple[str, str], dict]:
    return {(row["filter_id"], row["country_code"]): row for row in _staged_rows()}


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


def test_research_inputs_and_optional_raw_checksum_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checksums = phase6e.verify_research_inputs()
    assert len(checksums) == 11
    assert all(value.startswith("sha256:") and len(value) == 71 for value in checksums.values())

    fixture = tmp_path / "source.bin"
    fixture.write_bytes(b"phase6e-checksum-fixture")
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    monkeypatch.setattr(
        phase6e,
        "RETAINED_RAW_SOURCES",
        {"synthetic": (fixture, digest, fixture.stat().st_size)},
    )
    assert phase6e.verify_retained_sources(require_all=True) == {"synthetic": "VERIFIED"}
    fixture.write_bytes(b"tampered")
    with pytest.raises(phase6e.CareerOpportunityBuildError, match="byte count mismatch"):
        phase6e.verify_retained_sources(require_all=True)


def test_parser_adapters_preserve_source_metrics_thresholds_and_lineage() -> None:
    base_rows = phase6e._read_jsonl(
        phase6e.PHASE6B_ROOT / "career-country-opportunity-evidence.jsonl"
    )
    base = next(
        row
        for row in base_rows
        if row["candidate_id"] == "technology_software_opportunity" and row["country_code"] == "ALB"
    )
    promoted = phase6e._base_evidence(base, phase6e.FILTER_BY_ID[base["candidate_id"]])
    source_path = base["evidence_paths"][0]
    assert promoted["metric_payload"]["scale_thousands"] == source_path["scale_thousands"]
    assert promoted["metric_payload"]["share_percent"] == source_path["share_percent"]
    assert promoted["reference_period"] == str(base["latest_period"])
    assert source_path["source_id"] in promoted["source_references"][0]["lineage_id"]
    components = promoted["threshold_results"][0]["components"]
    assert (
        components["base_scale_thousands"]
        == base["thresholds"]["frozen_values"]["base_scale_thousands"]
    )

    gap_rows = phase6e._read_jsonl(phase6e.PHASE6B1_ROOT / "gap-fill-country-evidence.jsonl")
    canada = next(
        row
        for row in gap_rows
        if row["candidate_id"] == "technology_software_opportunity" and row["country_code"] == "CAN"
    )
    canada_promoted = phase6e._gap_evidence(canada, phase6e.FILTER_BY_ID[canada["candidate_id"]])
    assert canada_promoted["metric_payload"]["scale_thousands"] == 613.685
    assert canada_promoted["threshold_results"][0]["passed"] is True
    assert canada_promoted["source_references"][0]["source_id"] == "statcan_2021_census_noc"


def test_staged_catalog_and_evidence_are_an_exact_five_by_91_matrix() -> None:
    catalog = _json(STAGED_ROOT / "opportunity-filter-catalog.json")
    rows = _staged_rows()
    universe = _json(ROOT / "data" / "country-universes" / "stable-supported-v1.json")
    country_codes = [row["code"] for row in universe["countries"]]

    assert len(catalog["definitions"]) == 5
    assert catalog["activation_status"] == "STAGED_CONTRACT_ONLY"
    assert all(
        item["availability"] == "STAGED" and not item["active"] for item in catalog["definitions"]
    )
    assert len(rows) == 455
    assert len({(row["filter_id"], row["country_code"]) for row in rows}) == 455
    validate_opportunity_filter_catalog(catalog)
    validate_opportunity_filter_evidence_matrix(catalog, rows, country_codes)


@pytest.mark.parametrize(("filter_id", "expected"), EXPECTED_COUNTS.items())
def test_state_counts_match_frozen_research(filter_id: str, expected: tuple[int, int, int]) -> None:
    counts = Counter(row["state"] for row in _staged_rows() if row["filter_id"] == filter_id)
    assert tuple(counts[state] for state in STATE_ORDER) == expected


def test_confidence_precedence_and_canada_positive_only_policy() -> None:
    policy = _json(STAGED_ROOT / "opportunity-filter-evidence-policy.json")
    assert policy["precedence"] == [
        "HIGH_CONFIDENCE_OBSERVED_HARMONISED",
        "HIGH_CONFIDENCE_OBSERVED_NATIONAL",
        "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK",
        "MEDIUM_CONFIDENCE_MODELLED_HARMONISED",
        "LOW_CONFIDENCE_SUPPLEMENTAL",
    ]
    pairs = _by_pair()
    technology = pairs[("technology_software_opportunity", "CAN")]
    science = pairs[("science_engineering_opportunity", "CAN")]
    assert technology["state"] == "VERIFIED_STRONG_SIGNAL"
    assert technology["internal_confidence_tier"] == "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK"
    assert technology["establishing_route_ids"] == ["canada_technology"]
    assert science["state"] == "INSUFFICIENT_EVIDENCE"
    assert science["reason_codes"] == ["CROSSWALK_INCOMPLETE"]
    assert science["metric_payload"] is not None
    assert science["establishing_route_ids"] == []
    assert all(not item["passed"] for item in science["threshold_results"])


def test_malta_and_targeted_granularity_gaps_remain_explicit() -> None:
    pairs = _by_pair()
    for filter_id in ("technology_software_opportunity", "science_engineering_opportunity"):
        malta = pairs[(filter_id, "MLT")]
        assert malta["state"] == "STRONG_SIGNAL_NOT_ESTABLISHED"
        assert malta["reason_codes"] == ["SCALE_FLOOR_NOT_MET"]
        assert malta["internal_confidence_tier"] == "HIGH_CONFIDENCE_OBSERVED_HARMONISED"
        for country_code in ("JPN", "KOR", "NZL"):
            row = pairs[(filter_id, country_code)]
            assert row["state"] == "INSUFFICIENT_EVIDENCE"
            assert row["reason_codes"] == ["INSUFFICIENT_GRANULARITY"]
            assert row["metric_payload"] is None


def test_skilled_trades_and_construction_routes_are_visible_and_reconcile() -> None:
    rows = [
        row
        for row in _staged_rows()
        if row["filter_id"] == "skilled_trades_construction_opportunity"
    ]
    counts = Counter()
    for row in rows:
        establishing = tuple(row["establishing_route_ids"])
        if establishing == ("skilled_trades",):
            counts["skilled_only"] += 1
        elif establishing == ("construction",):
            counts["construction_only"] += 1
        elif establishing == ("skilled_trades", "construction"):
            counts["both"] += 1
        elif row["state"] == "STRONG_SIGNAL_NOT_ESTABLISHED":
            counts["neither"] += 1
        else:
            counts["insufficient"] += 1
        if row["metric_payload"] is not None:
            assert row["metric_payload"]["skilled_trades_scale_thousands"] is not None
            assert row["metric_payload"]["skilled_trades_share_percent"] is not None
            assert row["metric_payload"]["construction_scale_thousands"] is not None
            assert row["metric_payload"]["construction_share_percent"] is not None
            assert {item["route_id"] for item in row["threshold_results"]} == {
                "skilled_trades",
                "construction",
            }
    assert counts == {
        "skilled_only": 15,
        "construction_only": 11,
        "both": 8,
        "neither": 54,
        "insufficient": 3,
    }


def test_no_opportunity_artifact_contains_score_or_weight_fields() -> None:
    payloads = [
        _json(STAGED_ROOT / "opportunity-filter-catalog.json"),
        *_staged_rows(),
    ]

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value)) if value else set()
        return set()

    all_keys = set().union(*(keys(payload) for payload in payloads))
    assert "score" not in all_keys
    assert "weight" not in all_keys
    assert "affinity_contribution" not in all_keys


def test_coverage_reconciliation_source_legal_records_and_shortlists_pass() -> None:
    summary = _json(STAGED_ROOT / "opportunity-filter-coverage-summary.json")
    reconciliation = _json(REPORT_ROOT / "research-production-reconciliation.json")
    legal = _json(REPORT_ROOT / "source-legal-records.json")
    crosswalks = _json(REPORT_ROOT / "classification-crosswalks.json")
    validate_opportunity_filter_coverage_summary(summary)
    assert reconciliation["row_count"] == 455
    assert reconciliation["unique_filter_country_count"] == 455
    assert reconciliation["state_count_mismatches"] == []
    assert reconciliation["shortlist_coverage"]["mismatches"] == []
    assert reconciliation["discrepancies"] == []
    assert len(legal["sources"]) == 8
    assert "sole evidence publisher" in legal["single_publisher_risk"]
    required = {
        "publisher",
        "api_query_or_asset",
        "table_or_indicator",
        "extraction_or_edition",
        "byte_count",
        "sha256",
        "licence_id",
        "attribution",
        "production_use_conclusion",
        "normalized_derivative_conclusion",
        "raw_retention",
        "refresh_cadence",
        "terms_snapshot",
    }
    assert all(required <= set(source) for source in legal["sources"])
    identity = {
        row["route_id"]: row["included_source_codes"]
        for row in crosswalks["harmonised_identity_mappings"]
    }
    assert identity["observed_technology"] == ["25", "35"]
    assert identity["observed_science_engineering"] == ["21", "31"]
    canada_technology = next(
        row
        for row in crosswalks["national_mappings"]
        if row["country_code"] == "CAN" and row["target_construct"] == "technology"
    )
    assert canada_technology["included_source_codes"] == ["2122", "2123", "2222"]
    assert canada_technology["excluded_adjacent_codes"] == ["2121", "2131"]


def test_phase6e_candidate_remains_draft_after_final_activation() -> None:
    manifest = _json(STAGED_ROOT / "candidate-release-manifest.json")
    catalog = _json(STAGED_ROOT / "opportunity-filter-catalog.json")
    rows = _staged_rows()
    countries = [
        item["code"]
        for item in _json(ROOT / "data" / "country-universes" / "stable-supported-v1.json")[
            "countries"
        ]
    ]
    assert manifest["schema_version"] == "konsider-release-5.1"
    assert manifest["status"] == "draft"
    validate_opportunity_filter_release_bundle(manifest, catalog, rows, countries)

    loaded = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    assert loaded.manifest["release_id"] == "2026-08-04.1"
    assert "opportunity_filters" in loaded.manifest
    assert loaded.manifest["schema_version"] == "konsider-release-5.1"
    active_pointer = _json(ROOT / "data" / "releases" / "active.json")
    assert active_pointer["release_id"] == "2026-08-04.1"


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


def test_regeneration_preserves_product_bytes_without_raw_source_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing_sources = {
        source_id: (tmp_path / f"missing-{source_id}", checksum, byte_count)
        for source_id, (_, checksum, byte_count) in phase6e.RETAINED_RAW_SOURCES.items()
    }
    monkeypatch.setattr(phase6e, "RETAINED_RAW_SOURCES", missing_sources)
    generated = tmp_path / "generated"
    phase6e.build_career_opportunity_bundle(generated)
    assert _semantic_tree(generated) == _semantic_tree(REPORT_ROOT)
