"""Phase 4F production onboarding for Overall job-market opportunity."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from konsider.domain.display_catalog import ProductDisplayCatalog
from konsider.ingestion.countries import COUNTRY_CODES, COUNTRY_UNIVERSE
from konsider.ingestion.coverage_validation import (
    COVERAGE_POLICY_VERSION,
    validate_coverage_release,
)
from konsider.ingestion.models import (
    CoverageMode,
    CriterionCoverage,
    RawArtifact,
    SourceRegistration,
)
from konsider.ingestion.outcomes import build_criterion_outcomes
from konsider.ingestion.registry import SOURCES
from konsider.ingestion.scoring import score_observations, sensitivity_experiments
from konsider.ingestion.worker import _parse_artifacts
from konsider.repositories.raw_artifact_repository import RawArtifactRepository
from konsider.repositories.release_repository import ReleaseRepository
from konsider.text_io import write_text_lf

C11_CRITERION_ID = "overall_job_market_opportunity"
C11_SOURCE_ID = "ilostat_job_market_opportunity"
C11_SCORING_METHOD = "job_market_equal_component_percentiles_v1"
MINIMUM_GLOBAL_CORE_COUNT = 8
PROFILE_WEIGHTS = {
    "equal_weight_mvp": 1.0,
    "safety_and_stability": 0.6,
    "affordability_first": 0.6,
    "quality_of_life": 0.8,
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _write_json(path: Path, value: object) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _registrations(path: Path) -> list[SourceRegistration]:
    return [SourceRegistration(**item) for item in _read_json(path)]


def _base_artifacts(path: Path) -> list[RawArtifact]:
    return [RawArtifact(**item) for item in _read_json(path)]


def _c11_artifacts(probe_artifact_manifest: Path) -> list[RawArtifact]:
    registration = SOURCES[C11_SOURCE_ID]
    artifacts = []
    for item in _read_json(probe_artifact_manifest):
        source = RawArtifact(**item)
        artifacts.append(
            replace(
                source,
                source_id=registration.source_id,
                dataset_version=registration.dataset_version,
                parser_version=registration.parser_version,
            )
        )
    expected_urls = set(registration.download_urls)
    actual_urls = {item.requested_url for item in artifacts}
    if actual_urls != expected_urls:
        raise ValueError("Retained C11 artifacts do not match the frozen production URLs.")
    return artifacts


def _coverage_policies(
    *,
    base_catalog: dict[str, object],
    registrations: list[SourceRegistration],
    outcomes,
    scores,
) -> list[CriterionCoverage]:
    catalog_by_id = {item["id"]: item for item in base_catalog["criteria"]}
    registrations_by_criterion = {
        registration.criterion_id: registration for registration in registrations
    }
    method_by_criterion = {score.criterion_id: score.method_version for score in scores}
    counts_by_criterion = {}
    for criterion_id in (*catalog_by_id, C11_CRITERION_ID):
        counts = Counter(item.outcome for item in outcomes if item.criterion_id == criterion_id)
        counts_by_criterion[criterion_id] = {
            key: counts.get(key, 0) for key in ("invalid", "missing", "rejected", "stale", "valid")
        }

    policies = []
    for criterion_id, criterion in catalog_by_id.items():
        registration = registrations_by_criterion[criterion_id]
        ready = bool(criterion["ready"])
        policies.append(
            CriterionCoverage(
                criterion_id=criterion_id,
                mode=CoverageMode.GLOBAL_CORE if ready else CoverageMode.DIAGNOSTIC_ONLY,
                stable_universe_id=COUNTRY_UNIVERSE["universe_id"],
                stable_country_count=len(COUNTRY_CODES),
                valid_country_count=counts_by_criterion[criterion_id]["valid"],
                minimum_valid_country_count=len(COUNTRY_CODES) if ready else 0,
                outcome_counts=counts_by_criterion[criterion_id],
                activation_threshold=None,
                experimental=bool(criterion["experimental"]),
                source_versions={registration.source_id: registration.source_version},
                scoring_method_version=method_by_criterion[criterion_id],
            )
        )
    registration = registrations_by_criterion[C11_CRITERION_ID]
    policies.append(
        CriterionCoverage(
            criterion_id=C11_CRITERION_ID,
            mode=CoverageMode.CONDITIONAL_COMPLETE_CASE,
            stable_universe_id=COUNTRY_UNIVERSE["universe_id"],
            stable_country_count=len(COUNTRY_CODES),
            valid_country_count=counts_by_criterion[C11_CRITERION_ID]["valid"],
            minimum_valid_country_count=82,
            outcome_counts=counts_by_criterion[C11_CRITERION_ID],
            activation_threshold=0.6,
            experimental=False,
            source_versions={registration.source_id: registration.source_version},
            scoring_method_version=C11_SCORING_METHOD,
        )
    )
    return sorted(policies, key=lambda item: item.criterion_id)


def build_consumer_catalog_v2(
    *,
    base_catalog: dict[str, object],
    coverage: list[CriterionCoverage],
    display_catalog: ProductDisplayCatalog,
) -> dict[str, object]:
    """Migrate the production catalog to schema 2 and add the approved PCC."""

    coverage_by_id = {item.criterion_id: item.to_dict() for item in coverage}
    criteria = []
    for item in base_catalog["criteria"]:
        criterion = dict(item)
        display = display_catalog.definition("ORDERING_CRITERION", criterion["id"])
        if display.section_name is None:
            raise ValueError(f"Ordering criterion {criterion['id']} has no display section.")
        criterion["display_name"] = display.display_name
        criterion["category"] = display.section_name
        criterion["coverage"] = coverage_by_id[criterion["id"]]
        criteria.append(criterion)
    display = display_catalog.definition("ORDERING_CRITERION", C11_CRITERION_ID)
    if display.section_name is None:
        raise ValueError(f"Ordering criterion {C11_CRITERION_ID} has no display section.")
    criteria.append(
        {
            "id": C11_CRITERION_ID,
            "display_name": display.display_name,
            "category": display.section_name,
            "description": (
                "Harmonised national labour-market conditions derived from employment, labour-"
                "force participation and unemployment modelled estimates."
            ),
            "direction": "higher_is_better",
            "raw_unit": "equal_component_percentile_index_1_10",
            "interpretation": (
                "Higher values indicate stronger broad national labour utilisation in the pinned "
                "2025 ILOSTAT modelled estimates. This is occupation-neutral and is not a vacancy, "
                "wage, visa-access or city-level jobs measure."
            ),
            "caveats": [
                "National modelled estimates may differ from local or occupation-specific conditions.",
                "The score is distribution-relative within the 88 valid supported countries.",
                "Antigua and Barbuda and Grenada have no eligible source record; Ukraine is stale.",
            ],
            "quality_limitations": [
                "Employment and participation are related measures, so component redundancy is monitored.",
                "Equal component weights are a transparent product choice, not a publisher weighting.",
                "Future projections included in the source edition are excluded; only the 2025 cross-section is used.",
            ],
            "ready": True,
            "default_enabled": True,
            "experimental": False,
            "scoring_method_version": C11_SCORING_METHOD,
            "coverage": coverage_by_id[C11_CRITERION_ID],
        }
    )
    profiles = []
    for item in base_catalog["profiles"]:
        profile = {**item, "weights": dict(item["weights"])}
        profile["weights"][C11_CRITERION_ID] = PROFILE_WEIGHTS[profile["id"]]
        profiles.append(profile)
    return {
        "schema_version": "consumer-catalog-2.0",
        "compatible_release_schema_major": 4,
        "coverage_policy_version": COVERAGE_POLICY_VERSION,
        "stable_universe_id": COUNTRY_UNIVERSE["universe_id"],
        "countries": base_catalog["countries"],
        "criteria": criteria,
        "profiles": profiles,
    }


def _assert_base_preserved(base_release_path: Path, observations, scores) -> None:
    expected_observations = _read_jsonl(base_release_path / "observations.jsonl")
    actual_observations = [
        item.to_dict() for item in observations if item.metric_id != C11_CRITERION_ID
    ]
    if actual_observations != expected_observations:
        raise ValueError("Phase 4F would change historical base observations.")
    expected_scores = _read_jsonl(base_release_path / "scores.jsonl")
    actual_scores = [item.to_dict() for item in scores if item.criterion_id != C11_CRITERION_ID]
    if actual_scores != expected_scores:
        raise ValueError("Phase 4F would change historical base scores.")


def _write_report(
    *,
    report_root: Path,
    release_id: str,
    criterion_name: str,
    coverage: list[CriterionCoverage],
    outcomes,
    sensitivity: dict[str, object],
    c11_artifacts: list[RawArtifact],
) -> None:
    report_root.mkdir(parents=True, exist_ok=True)
    c11_coverage = next(item for item in coverage if item.criterion_id == C11_CRITERION_ID)
    non_valid = [
        item.to_dict()
        for item in outcomes
        if item.criterion_id == C11_CRITERION_ID and item.outcome != "valid"
    ]
    payload = {
        "schema_version": "phase4f-onboarding-report-1.0",
        "release_id": release_id,
        "criterion_id": C11_CRITERION_ID,
        "criterion_name": criterion_name,
        "decision": "PRODUCTION_ONBOARDED",
        "source_id": C11_SOURCE_ID,
        "source_version": SOURCES[C11_SOURCE_ID].source_version,
        "reference_year": 2025,
        "coverage": c11_coverage.to_dict(),
        "non_valid_outcomes": non_valid,
        "raw_artifacts": [
            {
                "artifact_id": item.artifact_id,
                "sha256": item.sha256,
                "byte_length": item.byte_length,
                "requested_url": item.requested_url,
            }
            for item in c11_artifacts
        ],
        "scoring": sensitivity["criteria"][C11_CRITERION_ID],
        "replay_evidence": {
            "phase3_online_run": "phase3e-2026-07-26-c11-online",
            "phase3_offline_replay": "exact country-result agreement",
            "phase4f_offline_replay_command": (
                f"python -m konsider.ingestion.worker replay data/releases/{release_id}"
            ),
        },
    }
    report_json = report_root / "report.json"
    _write_json(report_json, payload)
    markdown = f"""# Phase 4F: Overall job-market opportunity onboarding

Status: production-onboarded in immutable release `{release_id}`

## Frozen construct

- Source: International Labour Organization, ILOSTAT modelled estimates, November 2025 edition.
- Reference period: the 2025 cross-section only; 2026-2027 projections are excluded.
- Components: employment-to-population ratio, labour-force participation, and unemployment for
  total population age 15+.
- Transform: average-rank percentile per component, unemployment direction reversed, followed by
  an equal one-third mean.
- Scoring method: `{C11_SCORING_METHOD}`.

## Exact coverage

- Valid: 88/91.
- Missing: Antigua and Barbuda; Grenada.
- Stale: Ukraine (latest complete source year 2021).
- Coverage mode: `CONDITIONAL_COMPLETE_CASE`.
- Activation threshold: 0.6.

No observation or score is produced for a non-valid country. No imputation or country-specific
weight renormalisation is used.

## Interpretation boundary

The criterion measures broad, harmonised national labour-market utilisation. It does not measure
vacancies, wages, occupation-specific demand, credential recognition, work-visa access, or
city-level opportunity.

## Replay

The production parser uses the three retained, content-addressed raw artifacts listed in
`report.json`. The earlier online probe and exact offline replay are retained, and the published
release is replayed with the production parser and scoring implementation.
"""
    report_md = report_root / "report.md"
    write_text_lf(report_md, markdown)
    files = {
        path.name: "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (report_json, report_md)
    }
    _write_json(
        report_root / "manifest.json",
        {
            "schema_version": "phase4f-report-manifest-1.0",
            "release_id": release_id,
            "files": files,
        },
    )


def build_c11_release(
    *,
    release_id: str,
    base_release_path: Path,
    base_catalog_path: Path,
    catalog_v2_path: Path,
    probe_artifact_manifest: Path,
    release_root: Path,
    report_root: Path,
    display_catalog: ProductDisplayCatalog,
    publish: bool,
    created_at: str | None = None,
) -> Path:
    """Build and optionally publish the immutable schema-4 C11 release."""

    base_manifest = _read_json(base_release_path / "manifest.json")
    if base_manifest["schema_version"] != "konsider-release-3.0":
        raise ValueError("Phase 4F expects the approved schema-3 production baseline.")
    registrations = _registrations(base_release_path / "sources.json")
    registrations.append(SOURCES[C11_SOURCE_ID])
    artifacts = _base_artifacts(base_release_path / "raw-artifacts.json")
    c11_artifacts = _c11_artifacts(probe_artifact_manifest)
    artifacts.extend(c11_artifacts)
    artifacts.sort(key=lambda item: (item.source_id, item.requested_url))
    raw_repository = RawArtifactRepository()
    for artifact in artifacts:
        raw_repository.load(artifact)

    observations, _ = _parse_artifacts(
        artifacts,
        raw_repository,
        registrations,
        country_codes=COUNTRY_CODES,
    )
    scores = score_observations(observations, profile="current")
    _assert_base_preserved(base_release_path, observations, scores)
    criterion_ids = [registration.criterion_id for registration in registrations]
    outcomes = build_criterion_outcomes(
        registrations=registrations,
        artifacts=artifacts,
        observations=observations,
        raw_repository=raw_repository,
        criterion_ids=criterion_ids,
    )
    base_catalog = _read_json(base_catalog_path)
    coverage = _coverage_policies(
        base_catalog=base_catalog,
        registrations=registrations,
        outcomes=outcomes,
        scores=scores,
    )
    validation = validate_coverage_release(
        stable_country_codes=COUNTRY_CODES,
        stable_universe_id=COUNTRY_UNIVERSE["universe_id"],
        coverage=coverage,
        outcomes=outcomes,
        observations=observations,
        scores=scores,
        minimum_global_core_count=MINIMUM_GLOBAL_CORE_COUNT,
    )
    if not validation.structural_passed or not validation.product_ready:
        raise ValueError("Phase 4F schema-4 validation did not pass.")
    catalog = build_consumer_catalog_v2(
        base_catalog=base_catalog,
        coverage=coverage,
        display_catalog=display_catalog,
    )
    catalog_v2_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(catalog_v2_path, catalog)
    sensitivity = sensitivity_experiments(observations)
    _write_report(
        report_root=report_root,
        release_id=release_id,
        criterion_name=display_catalog.definition(
            "ORDERING_CRITERION", C11_CRITERION_ID
        ).display_name,
        coverage=coverage,
        outcomes=outcomes,
        sensitivity=sensitivity,
        c11_artifacts=c11_artifacts,
    )
    repository = ReleaseRepository(release_root, catalog_v2_path)
    draft = repository.write_draft(
        release_id,
        observations,
        scores,
        artifacts,
        [item.to_dict() for item in registrations],
        validation,
        outcomes,
        sensitivity,
        coverage=coverage,
        previous_release_id=base_manifest["release_id"],
        created_at=created_at,
    )
    return repository.publish(release_id, require_product_ready=True) if publish else draft
