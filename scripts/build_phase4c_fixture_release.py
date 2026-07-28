"""Build the deterministic schema-4 mixed-coverage contract fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from konsider.ingestion.countries import COUNTRY_RECORDS
from konsider.ingestion.coverage_validation import (
    COVERAGE_POLICY_VERSION,
    validate_coverage_release,
)
from konsider.ingestion.models import (
    CoverageMode,
    CriterionCoverage,
    CriterionOutcome,
    MetricObservation,
    MetricScore,
    SourceRecordReference,
)
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "phase4c"
RELEASE_ID = "phase4c-fixture-4.0"
UNIVERSE_ID = "stable_supported_v1"
GENERATED_AT = "2026-07-27T00:00:00+00:00"
FCC_ID = "fixture_global_core"
PCC_ID = "overall_job_market_opportunity_fixture"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _jsonl_bytes(values: list[dict[str, object]]) -> bytes:
    return (
        "\n".join(json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values)
        + "\n"
    ).encode()


def _write(path: Path, content: bytes) -> None:
    write_text_lf(path, content.decode())


def _source(source_id: str, criterion_id: str) -> dict[str, object]:
    return {
        "source_id": source_id,
        "criterion_id": criterion_id,
        "publisher": "Konsider Phase 4C deterministic fixture",
        "canonical_page_url": "https://example.invalid/konsider/phase4c-fixture",
        "download_urls": ["https://example.invalid/konsider/phase4c-fixture.json"],
        "dataset_version": "phase4c-fixture-v1",
        "source_version": f"{source_id}-v1",
        "reference_period": "fixture year 2025",
        "methodology_url": "https://example.invalid/konsider/phase4c-method",
        "license_name": "Fixture only; not production source data",
        "license_url": "https://example.invalid/konsider/phase4c-license",
        "attribution": "Synthetic fixture generated from country codes and ordinal positions.",
        "parser": "phase4c_fixture",
        "parser_version": "phase4c-fixture-parser-v1",
        "notes": "Contract-test fixture only. It is not candidate source onboarding.",
    }


def _coverage() -> list[CriterionCoverage]:
    return [
        CriterionCoverage(
            criterion_id=FCC_ID,
            mode=CoverageMode.GLOBAL_CORE,
            stable_universe_id=UNIVERSE_ID,
            stable_country_count=91,
            valid_country_count=91,
            minimum_valid_country_count=91,
            outcome_counts={
                "invalid": 0,
                "missing": 0,
                "rejected": 0,
                "stale": 0,
                "valid": 91,
            },
            activation_threshold=None,
            experimental=False,
            source_versions={"phase4c_fixture_fcc": "phase4c_fixture_fcc-v1"},
            scoring_method_version="phase4c-fixture-fcc-score-v1",
        ),
        CriterionCoverage(
            criterion_id=PCC_ID,
            mode=CoverageMode.CONDITIONAL_COMPLETE_CASE,
            stable_universe_id=UNIVERSE_ID,
            stable_country_count=91,
            valid_country_count=88,
            minimum_valid_country_count=82,
            outcome_counts={
                "invalid": 0,
                "missing": 2,
                "rejected": 0,
                "stale": 1,
                "valid": 88,
            },
            activation_threshold=0.6,
            experimental=True,
            source_versions={"phase4c_fixture_pcc": "phase4c_fixture_pcc-v1"},
            scoring_method_version="phase4c-fixture-pcc-score-v1",
        ),
    ]


def _payload_rows(coverage: list[CriterionCoverage]):
    observations: list[MetricObservation] = []
    scores: list[MetricScore] = []
    outcomes: list[CriterionOutcome] = []
    excluded = {
        "ATG": ("missing", ("COV_SOURCE_RECORD_MISSING",)),
        "GRD": ("missing", ("COV_SOURCE_RECORD_MISSING",)),
        "UKR": ("stale", ("FRS_STALE",)),
    }
    policy_by_id = {item.criterion_id: item for item in coverage}
    for criterion_id, source_id in (
        (FCC_ID, "phase4c_fixture_fcc"),
        (PCC_ID, "phase4c_fixture_pcc"),
    ):
        policy = policy_by_id[criterion_id]
        for index, country in enumerate(COUNTRY_RECORDS):
            country_code = country["code"]
            non_valid = excluded.get(country_code) if criterion_id == PCC_ID else None
            if non_valid:
                outcome, reason_codes = non_valid
                observation_id = None
            else:
                observation_id = f"{criterion_id}-{country_code}-fixture"
                value = float((index % 10) + 1)
                observations.append(
                    MetricObservation(
                        observation_id=observation_id,
                        country_code=country_code,
                        metric_id=criterion_id,
                        value=value,
                        unit="fixture_index_1_10",
                        reference_start="2025-01-01",
                        reference_end="2025-12-31",
                        source_id=source_id,
                        raw_artifact_ids=(f"sha256:{'a' if criterion_id == FCC_ID else 'b'}",),
                        source_records=(
                            SourceRecordReference(
                                f"sha256:{'a' if criterion_id == FCC_ID else 'b'}",
                                f"$[{index}]",
                                f"{criterion_id}|{country_code}",
                            ),
                        ),
                        observation_type="synthetic_fixture",
                        geographic_scope="national",
                        parser_version="phase4c-fixture-parser-v1",
                        method_version=policy.scoring_method_version,
                        quality_flags=("fixture_only",),
                    )
                )
                scores.append(
                    MetricScore(
                        country_code=country_code,
                        criterion_id=criterion_id,
                        score=value,
                        input_observation_ids=(observation_id,),
                        method_version=policy.scoring_method_version,
                        transform="identity_fixture_1_10",
                        direction="higher_is_better",
                    )
                )
                outcome, reason_codes = "valid", ()
            outcomes.append(
                CriterionOutcome(
                    criterion_id=criterion_id,
                    country_code=country_code,
                    outcome=outcome,
                    source_id=source_id,
                    attempted_at=GENERATED_AT,
                    observation_id=observation_id,
                    reason_codes=reason_codes,
                )
            )
    return observations, scores, outcomes


def _criterion_catalog(policy: CriterionCoverage) -> dict[str, object]:
    pcc = policy.mode == CoverageMode.CONDITIONAL_COMPLETE_CASE
    return {
        "id": policy.criterion_id,
        "display_name": (
            "Overall job-market opportunity (Phase 4C fixture)"
            if pcc
            else "Global core control (Phase 4C fixture)"
        ),
        "category": "Fixture",
        "description": (
            "Synthetic 88/91 PCC used only to verify complete-case release contracts."
            if pcc
            else "Synthetic 91/91 FCC used only to verify global-core release contracts."
        ),
        "direction": "higher_is_better",
        "raw_unit": "fixture_index_1_10",
        "interpretation": "Higher synthetic fixture values produce higher fixture scores.",
        "caveats": ["Not production data and not candidate source onboarding."],
        "quality_limitations": ["Ordinal synthetic values have no product meaning."],
        "ready": True,
        "default_enabled": True,
        "experimental": policy.experimental,
        "scoring_method_version": policy.scoring_method_version,
        "coverage": policy.to_dict(),
    }


def build(output_root: Path = FIXTURE_ROOT) -> None:
    release_path = output_root / "releases" / RELEASE_ID
    catalog_path = output_root / "consumer-catalog-2.0.json"
    coverage = _coverage()
    observations, scores, outcomes = _payload_rows(coverage)
    report = validate_coverage_release(
        stable_country_codes=[item["code"] for item in COUNTRY_RECORDS],
        stable_universe_id=UNIVERSE_ID,
        coverage=coverage,
        outcomes=outcomes,
        observations=observations,
        scores=scores,
        minimum_global_core_count=1,
    )
    if not report.structural_passed:
        raise ValueError("Phase 4C fixture failed its own coverage validation.")

    sources = [
        _source("phase4c_fixture_fcc", FCC_ID),
        _source("phase4c_fixture_pcc", PCC_ID),
    ]
    payloads = {
        "attempts.jsonl": _jsonl_bytes([item.to_dict() for item in outcomes]),
        "observations.jsonl": _jsonl_bytes([item.to_dict() for item in observations]),
        "scores.jsonl": _jsonl_bytes([item.to_dict() for item in scores]),
        "sources.json": _json_bytes(sources),
        "validation.json": _json_bytes(report.to_dict()),
    }
    release_path.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        _write(release_path / name, content)
    checksums = {
        name: "sha256:" + hashlib.sha256(content).hexdigest()
        for name, content in sorted(payloads.items())
    }
    coverage_by_id = {
        item.criterion_id: item.to_dict()
        for item in sorted(coverage, key=lambda item: item.criterion_id)
    }
    manifest = {
        "schema_version": "konsider-release-4.0",
        "release_id": RELEASE_ID,
        "status": "published",
        "created_at": GENERATED_AT,
        "published_at": GENERATED_AT,
        "previous_release_id": None,
        "observation_count": len(observations),
        "score_count": len(scores),
        "attempt_count": len(outcomes),
        "country_count": len(COUNTRY_RECORDS),
        "country_codes": sorted(item["code"] for item in COUNTRY_RECORDS),
        "criteria": sorted(coverage_by_id),
        "coverage_policy_version": COVERAGE_POLICY_VERSION,
        "criterion_coverage": coverage_by_id,
        "source_versions": {
            "phase4c_fixture_fcc": "phase4c_fixture_fcc-v1",
            "phase4c_fixture_pcc": "phase4c_fixture_pcc-v1",
        },
        "scoring_method_versions": sorted(item.scoring_method_version for item in coverage),
        "file_checksums": checksums,
        "release_checksum": "sha256:"
        + hashlib.sha256(
            json.dumps(checksums, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "validation_summary": {
            "structural_passed": True,
            "product_ready": True,
            "ready_criterion_count": 2,
            "criterion_readiness": {FCC_ID: True, PCC_ID: True},
            "global_core_ready_count": 1,
            "minimum_global_core_count": 1,
            "errors": 0,
            "blockers": 0,
            "warnings": 0,
        },
        "reproducibility": {
            "fixture_only": True,
            "line_endings": "LF",
            "generator": "scripts/build_phase4c_fixture_release.py",
            "replay_command": "python scripts/build_phase4c_fixture_release.py",
        },
    }
    _write(release_path / "manifest.json", _json_bytes(manifest))
    _write(
        output_root / "releases" / "active.json",
        _json_bytes(
            {
                "release_id": RELEASE_ID,
                "schema_version": "konsider-release-4.0",
            }
        ),
    )
    catalog = {
        "schema_version": "consumer-catalog-2.0",
        "compatible_release_schema_major": 4,
        "coverage_policy_version": COVERAGE_POLICY_VERSION,
        "stable_universe_id": UNIVERSE_ID,
        "countries": list(COUNTRY_RECORDS),
        "criteria": [_criterion_catalog(item) for item in coverage],
        "profiles": [
            {
                "id": "phase4c_fixture",
                "name": "Phase 4C fixture",
                "description": "Contract-only mixed-coverage fixture.",
                "weights": {FCC_ID: 1.0, PCC_ID: 0.6},
            }
        ],
    }
    _write(catalog_path, _json_bytes(catalog))


if __name__ == "__main__":
    build()
