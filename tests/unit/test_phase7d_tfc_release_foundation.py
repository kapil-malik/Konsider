import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.tfc_release import (
    PAYLOAD_FILES,
    TfcCandidateReleaseRepository,
    TfcReleaseError,
    build_tfc_release_artifacts,
    semantic_diff,
    validate_tfc_release_artifacts,
)
from konsider.ingestion.tfc_sources import TfcSourceError, TfcSourceRegistry

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_PATH = ROOT / "tests" / "fixtures" / "phase7d" / "synthetic-capture.json"
ACTIVE_RELEASE = ROOT / "data" / "releases" / "2026-08-04.1"


def _capture() -> dict:
    return json.loads(CAPTURE_PATH.read_text(encoding="utf-8"))


def _base_manifest() -> dict:
    return json.loads((ACTIVE_RELEASE / "manifest.json").read_text(encoding="utf-8"))


def _issue_codes(artifacts) -> set[str]:
    report = validate_tfc_release_artifacts(
        replace(artifacts, validation={}), validated_as_of="2026-08-05"
    )
    return {issue["code"] for issue in report["issues"]}


def test_all_generation_4_schemas_remain_valid_after_release_extension() -> None:
    schemas = sorted((ROOT / "contracts" / "schemas" / "v4").glob("*.schema.json"))
    assert len(schemas) >= 23
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_synthetic_capture_builds_all_typed_families_and_explicit_support() -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    records = artifacts.rule_evidence
    supports = [row for row in records if row["record_type"] == "DESTINATION_SUPPORT"]
    route_rules = [row for row in records if row["record_type"] == "ROUTE_RULE"]
    formulas = [row for row in records if row["record_type"] == "METRIC_FORMULA"]

    assert artifacts.validation["structural_passed"] is True
    assert len(supports) == 2 * len(COUNTRY_CODES) == 182
    assert len({(row["tfc_id"], row["country_code"]) for row in supports}) == 182
    assert {row["record_type"] for row in records} == {
        "JURISDICTION",
        "DESTINATION_SUPPORT",
        "ROUTE_RULE",
        "METRIC_FORMULA",
    }
    national_deu_routes = {
        row["route_id"] for row in route_rules if row["jurisdiction_id"] == "country:DEU"
    }
    assert national_deu_routes == {"FX.HIGH_SKILL_A", "FX.HIGH_SKILL_B"}
    assert len(formulas) == 1
    assert sum(component["coefficient"] for component in formulas[0]["components"]) == 1.0
    assert artifacts.coverage_summary["actual_support_records"] == 182
    assert artifacts.catalog["activation_status"] == "SYNTHETIC_ONLY"


def test_source_registry_supports_family_neutral_checksum_verified_capture() -> None:
    manifest = copy.deepcopy(_capture()["source_legal_manifest"])
    content = b"fictional captured policy bytes\n"
    source = manifest["sources"][0]
    source["checksum"] = f"sha256:{hashlib.sha256(content).hexdigest()}"
    registry = TfcSourceRegistry(manifest)

    captured = registry.capture_online(source["source_id"], lambda asset: content)
    assert captured.asset == source["asset"]
    assert captured.content == content
    with pytest.raises(TfcSourceError, match="Checksum mismatch"):
        registry.capture_online(source["source_id"], lambda asset: b"changed")

    manifest["sources"].append(copy.deepcopy(source))
    with pytest.raises(TfcSourceError, match="unique"):
        TfcSourceRegistry(manifest)

    manifest = copy.deepcopy(_capture()["source_legal_manifest"])
    manifest["sources"][0].pop("access_and_licence")
    with pytest.raises(TfcSourceError):
        TfcSourceRegistry(manifest)


def test_candidate_write_load_replay_and_serialization_are_deterministic(tmp_path: Path) -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    first = TfcCandidateReleaseRepository(tmp_path / "first").write_draft(
        "synthetic-phase7d-6.0", artifacts, base_manifest=_base_manifest()
    )
    second = TfcCandidateReleaseRepository(tmp_path / "second").write_draft(
        "synthetic-phase7d-6.0", artifacts, base_manifest=_base_manifest()
    )
    first_bytes = {path.name: path.read_bytes() for path in first.iterdir() if path.is_file()}
    second_bytes = {path.name: path.read_bytes() for path in second.iterdir() if path.is_file()}

    assert first_bytes == second_bytes
    assert all(b"\r\n" not in content for content in first_bytes.values())
    repository = TfcCandidateReleaseRepository(tmp_path / "first")
    loaded = repository.load(first)
    replay = repository.replay(first, _capture())
    assert loaded.manifest["schema_version"] == "konsider-release-6.0"
    assert loaded.manifest["base_release"]["release_id"] == "2026-08-04.1"
    assert replay.passed
    assert replay.mismatched_files == ()
    assert replay.compared_files == (*PAYLOAD_FILES, "manifest.json")


def test_loader_rejects_checksum_tampering(tmp_path: Path) -> None:
    repository = TfcCandidateReleaseRepository(tmp_path)
    path = repository.write_draft(
        "synthetic-phase7d-6.0",
        build_tfc_release_artifacts(_capture()),
        base_manifest=_base_manifest(),
    )
    target = path / "tfc-policy-bundles.json"
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(TfcReleaseError, match="checksum mismatch"):
        repository.load(path)


def test_country_support_requires_exactly_one_record_per_tfc_country() -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    rows = list(copy.deepcopy(artifacts.rule_evidence))
    supports = [
        index for index, row in enumerate(rows) if row["record_type"] == "DESTINATION_SUPPORT"
    ]
    rows.pop(supports[0])
    missing = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert {"INCOMPLETE_COUNTRY_SUPPORT", "COVERAGE_SUMMARY_MISMATCH"} <= _issue_codes(missing)

    rows = list(copy.deepcopy(artifacts.rule_evidence))
    duplicate = copy.deepcopy(rows[supports[0]])
    duplicate["record_id"] += ":duplicate"
    rows.append(duplicate)
    repeated = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "DUPLICATE_TFC_COUNTRY_SUPPORT" in _issue_codes(repeated)


def test_overlapping_route_versions_and_broken_jurisdiction_are_rejected() -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    rows = list(copy.deepcopy(artifacts.rule_evidence))
    route = next(row for row in rows if row["record_id"] == "rule:synthetic_skilled_route:deu:a:v1")
    duplicate = copy.deepcopy(route)
    duplicate["record_id"] = "rule:synthetic_skilled_route:deu:a:v2"
    duplicate["effective_period"]["supersedes_record_id"] = route["record_id"]
    rows.append(duplicate)
    invalid = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "OVERLAPPING_EFFECTIVE_PERIOD" in _issue_codes(invalid)

    rows = list(copy.deepcopy(artifacts.rule_evidence))
    region = next(row for row in rows if row["record_id"] == "jurisdiction:region:DE-FX")
    region["parent_jurisdiction_id"] = "country:ZZZ"
    invalid = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "BROKEN_JURISDICTION_PARENT" in _issue_codes(invalid)

    rows = list(copy.deepcopy(artifacts.rule_evidence))
    region = next(row for row in rows if row["record_id"] == "jurisdiction:region:DE-FX")
    region["country_code"] = "CAN"
    invalid = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "JURISDICTION_COUNTRY_MISMATCH" in _issue_codes(invalid)


def test_regional_override_must_identify_the_same_tfc_and_route() -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    rows = list(copy.deepcopy(artifacts.rule_evidence))
    override = next(
        row for row in rows if row["record_id"] == "rule:synthetic_skilled_route:deu:north:v1"
    )
    override["overrides_record_id"] = "rule:synthetic_skilled_route:deu:b:v1"
    invalid = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "INVALID_RULE_OVERRIDE" in _issue_codes(invalid)


@pytest.mark.parametrize("field", ["profile_data", "ranking_weight", "ofc_state"])
def test_release_contracts_reject_profile_ranking_and_ofc_fields(field: str) -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    catalog = copy.deepcopy(artifacts.catalog)
    catalog[field] = {"synthetic": True}
    with pytest.raises(TfcReleaseError):
        validate_tfc_release_artifacts(
            replace(artifacts, catalog=catalog, validation={}), validated_as_of="2026-08-05"
        )


@pytest.mark.parametrize(
    ("effective_from", "effective_to", "stale_after"),
    [
        ("2027-01-01", None, "2028-01-01"),
        ("2025-01-01", "2026-07-31", "2027-01-01"),
        ("2025-01-01", None, "2026-08-04"),
    ],
)
def test_supported_records_reject_future_expired_and_stale_rules(
    effective_from: str, effective_to: str | None, stale_after: str
) -> None:
    capture = _capture()
    route = next(
        row
        for row in capture["rules"]
        if row["record_id"] == "rule:synthetic_skilled_route:deu:a:v1"
    )
    route["effective_period"].update(
        effective_from=effective_from, effective_to=effective_to, stale_after=stale_after
    )
    with pytest.raises(TfcReleaseError, match="INACTIVE_RULE_SELECTED"):
        build_tfc_release_artifacts(capture)


def test_unresolved_conflict_blocks_supported_state_but_is_preserved_as_insufficient() -> None:
    artifacts = build_tfc_release_artifacts(_capture())
    conflict = next(
        row
        for row in artifacts.rule_evidence
        if row["record_id"] == "rule:synthetic_skilled_route:can:conflict:v1"
    )
    support = next(
        row
        for row in artifacts.rule_evidence
        if row["record_id"] == "support:synthetic_skilled_route:CAN"
    )
    assert conflict["effective_period"]["conflict_status"] == "UNRESOLVED"
    assert support["support_status"] == "EVIDENCE_INSUFFICIENT"

    rows = list(copy.deepcopy(artifacts.rule_evidence))
    support = next(row for row in rows if row["record_id"] == "support:synthetic_skilled_route:CAN")
    support["support_status"] = "SUPPORTED"
    support["reason_code"] = None
    invalid = replace(artifacts, rule_evidence=tuple(rows), validation={})
    assert "UNRESOLVED_CONFLICT_SELECTED" in _issue_codes(invalid)


def test_semantic_diff_exposes_all_reviewable_policy_change_categories(tmp_path: Path) -> None:
    before_capture = _capture()
    after_capture = _capture()
    after_capture["release_id"] = "synthetic-phase7d-change-6.0"
    source = after_capture["source_legal_manifest"]["sources"][0]
    source["checksum"] = "sha256:" + "9" * 64
    route = next(
        row
        for row in after_capture["rules"]
        if row["record_id"] == "rule:synthetic_skilled_route:deu:a:v1"
    )
    route["route_name"] = "Fictional amended national specialist route"
    route["effective_period"]["effective_from"] = "2026-02-01"
    after_capture["policy_bundles"]["policies"][0]["policy_version"] = "1.1"
    can = next(
        row
        for row in after_capture["support_overrides"]
        if row["tfc_id"] == "synthetic_skilled_route" and row["country_code"] == "CAN"
    )
    can["support_status"] = "UNSUPPORTED"
    can["reason_code"] = "SYNTHETIC_UNSUPPORTED"

    before_path = TfcCandidateReleaseRepository(tmp_path / "before").write_draft(
        before_capture["release_id"],
        build_tfc_release_artifacts(before_capture),
        base_manifest=_base_manifest(),
    )
    after_path = TfcCandidateReleaseRepository(tmp_path / "after").write_draft(
        after_capture["release_id"],
        build_tfc_release_artifacts(after_capture),
        base_manifest=_base_manifest(),
    )
    before = TfcCandidateReleaseRepository(tmp_path / "before").load(before_path)
    after = TfcCandidateReleaseRepository(tmp_path / "after").load(after_path)
    diff = semantic_diff(before, after)

    assert all(diff["change_counts"][change_type] >= 1 for change_type in diff["change_counts"])
    assert {change["change_type"] for change in diff["changes"]} == set(diff["change_counts"])


def test_active_legacy_release_remains_loadable_and_unchanged() -> None:
    before = (ROOT / "data" / "releases" / "active.json").read_bytes()
    loaded = CurrentReleaseRepository(ROOT / "data" / "releases").load_active()
    after = (ROOT / "data" / "releases" / "active.json").read_bytes()
    assert loaded.manifest["schema_version"] == "konsider-release-5.1"
    assert loaded.manifest["release_id"] == "2026-08-04.1"
    assert before == after
