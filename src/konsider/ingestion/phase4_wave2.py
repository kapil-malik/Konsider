"""Onboard the approved Phase 4 Wave 2 partial-coverage criteria."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from konsider.domain.display_catalog import ProductDisplayCatalog
from konsider.ingestion.countries import COUNTRY_CODES, COUNTRY_UNIVERSE
from konsider.ingestion.coverage_validation import validate_coverage_release
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

SCHOOL_ID = "school_education_quality"
SCHOOL_SOURCE_ID = "world_bank_hci_plus_schooling"
SCHOOL_METHOD = "learning_adjusted_schooling_bands_v1"
INNOVATION_ID = "research_innovation_ecosystem"
INNOVATION_SOURCE_ID = "wipo_innovation_outputs"
INNOVATION_METHOD = "wipo_innovation_outputs_bands_v1"
WIPO_DOWNLOAD_URL = "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-2000-2025-tech1.xlsx"
NEW_CRITERIA = (SCHOOL_ID, INNOVATION_ID)
MINIMUM_GLOBAL_CORE_COUNT = 8
PROFILE_WEIGHTS = {
    "equal_weight_mvp": {SCHOOL_ID: 0.6, INNOVATION_ID: 0.6},
    "safety_and_stability": {SCHOOL_ID: 0.4, INNOVATION_ID: 0.4},
    "affordability_first": {SCHOOL_ID: 0.4, INNOVATION_ID: 0.4},
    "quality_of_life": {SCHOOL_ID: 1.0, INNOVATION_ID: 0.8},
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _write_json(path: Path, value: object) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _probe_artifact(path: Path, source_id: str) -> RawArtifact:
    registration = SOURCES[source_id]
    items = _read_json(path)
    if len(items) != 1:
        raise ValueError(f"{source_id} requires exactly one retained probe artifact.")
    artifact = RawArtifact(**items[0])
    result = replace(
        artifact,
        source_id=source_id,
        dataset_version=registration.dataset_version,
        parser_version=registration.parser_version,
    )
    if result.requested_url != registration.download_urls[0]:
        raise ValueError(f"Retained {source_id} artifact does not match the frozen URL.")
    return result


def _local_wipo_artifact(path: Path, retrieved_at: str) -> RawArtifact:
    body = path.read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    registration = SOURCES[INNOVATION_SOURCE_ID]
    return RawArtifact(
        artifact_id=f"sha256:{digest}",
        source_id=INNOVATION_SOURCE_ID,
        requested_url=WIPO_DOWNLOAD_URL,
        final_url=WIPO_DOWNLOAD_URL,
        retrieved_at=retrieved_at,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        byte_length=len(body),
        sha256=digest,
        dataset_version=registration.dataset_version,
        parser_version=registration.parser_version,
        path=path.as_posix(),
        http_status=200,
        content_length_header=str(len(body)),
    )


def _coverage_from_catalog(item: dict[str, object]) -> CriterionCoverage:
    value = dict(item["coverage"])
    value["mode"] = CoverageMode(value["mode"])
    return CriterionCoverage(**value)


def _coverage_policies(
    *,
    base_catalog: dict[str, object],
    outcomes,
) -> list[CriterionCoverage]:
    policies = [_coverage_from_catalog(item) for item in base_catalog["criteria"]]
    counts = {}
    for criterion_id in NEW_CRITERIA:
        counter = Counter(item.outcome for item in outcomes if item.criterion_id == criterion_id)
        counts[criterion_id] = {
            key: counter.get(key, 0) for key in ("invalid", "missing", "rejected", "stale", "valid")
        }
    for criterion_id, source_id, method in (
        (SCHOOL_ID, SCHOOL_SOURCE_ID, SCHOOL_METHOD),
        (INNOVATION_ID, INNOVATION_SOURCE_ID, INNOVATION_METHOD),
    ):
        policies.append(
            CriterionCoverage(
                criterion_id=criterion_id,
                mode=CoverageMode.CONDITIONAL_COMPLETE_CASE,
                stable_universe_id=COUNTRY_UNIVERSE["universe_id"],
                stable_country_count=len(COUNTRY_CODES),
                valid_country_count=counts[criterion_id]["valid"],
                minimum_valid_country_count=82,
                outcome_counts=counts[criterion_id],
                activation_threshold=0.6,
                experimental=True,
                source_versions={source_id: SOURCES[source_id].source_version},
                scoring_method_version=method,
            )
        )
    return sorted(policies, key=lambda item: item.criterion_id)


def build_wave2_catalog(
    *,
    base_catalog: dict[str, object],
    coverage: list[CriterionCoverage],
    display_catalog: ProductDisplayCatalog,
) -> dict[str, object]:
    coverage_by_id = {item.criterion_id: item.to_dict() for item in coverage}
    criteria = []
    for item in base_catalog["criteria"]:
        display = display_catalog.definition("ORDERING_CRITERION", item["id"])
        if display.section_name is None:
            raise ValueError(f"Ordering criterion {item['id']} has no display section.")
        criteria.append(
            {
                **item,
                "display_name": display.display_name,
                "category": display.section_name,
                "coverage": coverage_by_id[item["id"]],
            }
        )
    school_display = display_catalog.definition("ORDERING_CRITERION", SCHOOL_ID)
    innovation_display = display_catalog.definition("ORDERING_CRITERION", INNOVATION_ID)
    if school_display.section_name is None or innovation_display.section_name is None:
        raise ValueError("Wave 2 ordering criteria require display sections.")
    criteria.extend(
        [
            {
                "id": SCHOOL_ID,
                "display_name": school_display.display_name,
                "category": school_display.section_name,
                "description": (
                    "National learning-adjusted years of schooling, combining expected schooling "
                    "quantity with harmonized learning outcomes."
                ),
                "direction": "higher_is_better",
                "raw_unit": "learning_adjusted_years",
                "interpretation": (
                    "Higher values indicate more effective national school-system learning under "
                    "the World Bank HCI+ model. They do not rate an individual school or city."
                ),
                "caveats": [
                    "National modelled learning conditions can differ by city, school type, language, and household.",
                    "Underlying assessments and reference periods are harmonized rather than identical.",
                    "The file contains 2025 labels while the catalogue temporal metadata ends in 2024.",
                ],
                "quality_limitations": [
                    "Learning-adjusted years are a modelled construct, not a direct percentage.",
                    "Bahamas and Bolivia have no usable record; Guyana's latest usable record is stale.",
                ],
                "ready": True,
                "default_enabled": True,
                "experimental": True,
                "scoring_method_version": SCHOOL_METHOD,
                "coverage": coverage_by_id[SCHOOL_ID],
            },
            {
                "id": INNOVATION_ID,
                "display_name": innovation_display.display_name,
                "category": innovation_display.section_name,
                "description": (
                    "WIPO's published Innovation outputs sub-index, covering national knowledge, "
                    "technology, and creative outputs."
                ),
                "direction": "higher_is_better",
                "raw_unit": "wipo_innovation_outputs_score_0_100",
                "interpretation": (
                    "Higher values indicate stronger measured national innovation outputs in the "
                    "2025 GII edition; this is not a city-cluster or personal research-opportunity score."
                ),
                "caveats": [
                    "The source combines indicators with mixed reference years.",
                    "National results can obscure research and innovation clusters concentrated in a few cities.",
                    "Only WIPO's output sub-index is used; Konsider does not republish third-party input columns.",
                ],
                "quality_limitations": [
                    "The output sub-index is a WIPO composite and remains experimental in Konsider.",
                    "Six supported countries are outside the 2025 GII economy set.",
                ],
                "ready": True,
                "default_enabled": True,
                "experimental": True,
                "scoring_method_version": INNOVATION_METHOD,
                "coverage": coverage_by_id[INNOVATION_ID],
            },
        ]
    )
    profiles = []
    for item in base_catalog["profiles"]:
        profile = {**item, "weights": dict(item["weights"])}
        profile["weights"].update(PROFILE_WEIGHTS[profile["id"]])
        profiles.append(profile)
    return {**base_catalog, "criteria": criteria, "profiles": profiles}


def _without_wave2_catalog_entries(catalog: dict[str, object]) -> dict[str, object]:
    """Make rebuilding safe when the operational catalog already points at Wave 2."""

    criteria = [item for item in catalog["criteria"] if item["id"] not in NEW_CRITERIA]
    profiles = []
    for item in catalog["profiles"]:
        profile = {**item, "weights": dict(item["weights"])}
        for criterion_id in NEW_CRITERIA:
            profile["weights"].pop(criterion_id, None)
        profiles.append(profile)
    return {**catalog, "criteria": criteria, "profiles": profiles}


def _assert_base_preserved(base_release_path: Path, observations, scores) -> None:
    expected_observations = _read_jsonl(base_release_path / "observations.jsonl")
    actual_observations = [
        item.to_dict() for item in observations if item.metric_id not in NEW_CRITERIA
    ]
    if actual_observations != expected_observations:
        raise ValueError("Wave 2 would change historical base observations.")
    expected_scores = _read_jsonl(base_release_path / "scores.jsonl")
    actual_scores = [item.to_dict() for item in scores if item.criterion_id not in NEW_CRITERIA]
    if actual_scores != expected_scores:
        raise ValueError("Wave 2 would change historical base scores.")


def _write_report(
    *,
    report_root: Path,
    release_id: str,
    coverage: list[CriterionCoverage],
    outcomes,
    artifacts: list[RawArtifact],
    sensitivity: dict[str, object],
) -> None:
    report_root.mkdir(parents=True, exist_ok=True)
    coverage_by_id = {item.criterion_id: item.to_dict() for item in coverage}
    non_valid = {
        criterion_id: [
            item.to_dict()
            for item in outcomes
            if item.criterion_id == criterion_id and item.outcome != "valid"
        ]
        for criterion_id in NEW_CRITERIA
    }
    payload = {
        "schema_version": "phase4-wave2-onboarding-report-1.0",
        "release_id": release_id,
        "decisions": {
            SCHOOL_ID: "EXPERIMENTAL_ONBOARDED",
            INNOVATION_ID: "EXPERIMENTAL_ONBOARDED",
            "financial_protection_from_health_costs": "HELD_LICENSING",
            "social_protection_system_reach": "HELD_EXACT_SOURCE_AND_MODEL_POLICY",
            "food_safety_system_capacity": "HELD_EXACT_EXPORT_AND_CONSTRUCT_VALUE",
            "freedom_expression_religion": "HELD_LICENSE_AND_VARIABLE_SELECTION",
        },
        "coverage": {criterion_id: coverage_by_id[criterion_id] for criterion_id in NEW_CRITERIA},
        "non_valid_outcomes": non_valid,
        "raw_artifacts": [
            {
                "source_id": item.source_id,
                "artifact_id": item.artifact_id,
                "sha256": item.sha256,
                "byte_length": item.byte_length,
                "requested_url": item.requested_url,
            }
            for item in artifacts
        ],
        "scoring": {
            criterion_id: sensitivity["criteria"][criterion_id] for criterion_id in NEW_CRITERIA
        },
    }
    _write_json(report_root / "report.json", payload)
    write_text_lf(
        report_root / "report.md",
        f"""# Phase 4 Wave 2 candidate onboarding

Status: two experimental criteria onboarded in immutable release `{release_id}`.

## Onboarded

- **School education quality** — frozen to learning-adjusted years of schooling (LAYS), scored
  with fixed domain bands. Production coverage is 88/91: Bahamas and Bolivia are missing, and
  Guyana is stale. This differs from the earlier 87/91 multi-field probe because the frozen LAYS
  construct does not reject Antigua and Barbuda for a missing, unrelated HCI+ schooling component.
- **Research and innovation ecosystem** — frozen to WIPO's published Innovation outputs sub-index,
  not the overall GII. Coverage is 85/91; Antigua and Barbuda, Bahamas, Fiji, Grenada, Guyana, and
  Haiti are missing. The criterion remains experimental.

Both use `CONDITIONAL_COMPLETE_CASE`, activate at raw weight 0.6 or above, preserve explicit
outcomes for all 91 countries, and produce no score for non-valid outcomes.

## Held

- **Financial protection from health costs** — the exact GHED asset remains commercially
  ambiguous; WHO material cites the database as CC BY-NC-SA 3.0 IGO.
- **Social-protection system reach** — the ILO construct is useful and licensing is favourable,
  but the exact country export, reported-versus-imputed policy, and replay artifact are not frozen.
- **Food-safety system capacity** — exact SPAR export coverage and licensing are not captured, and
  the self-reported capacity proxy still needs discrimination evidence.
- **Freedom of expression and religion** — V-Dem says the data are free to use, but an explicit
  production redistribution licence and a non-arbitrary expression/religion variable policy are
  not frozen.
""",
    )
    files = {
        path.name: "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (report_root / "report.json", report_root / "report.md")
    }
    _write_json(
        report_root / "manifest.json",
        {
            "schema_version": "phase4-wave2-report-manifest-1.0",
            "release_id": release_id,
            "files": files,
        },
    )


def build_wave2_release(
    *,
    release_id: str,
    base_release_path: Path,
    base_catalog_path: Path,
    catalog_output_path: Path,
    school_probe_artifact_manifest: Path,
    wipo_raw_path: Path,
    release_root: Path,
    report_root: Path,
    display_catalog: ProductDisplayCatalog,
    publish: bool,
    created_at: str | None = None,
    wipo_retrieved_at: str = "2026-07-28T07:05:47+00:00",
) -> Path:
    """Build and optionally publish the additive Wave 2 schema-4 release."""

    base_manifest = _read_json(base_release_path / "manifest.json")
    if base_manifest["schema_version"] != "konsider-release-4.0":
        raise ValueError("Wave 2 expects the approved schema-4 production baseline.")
    registrations = [
        SourceRegistration(**item) for item in _read_json(base_release_path / "sources.json")
    ]
    registrations.extend([SOURCES[SCHOOL_SOURCE_ID], SOURCES[INNOVATION_SOURCE_ID]])
    artifacts = [
        RawArtifact(**item) for item in _read_json(base_release_path / "raw-artifacts.json")
    ]
    new_artifacts = [
        _probe_artifact(school_probe_artifact_manifest, SCHOOL_SOURCE_ID),
        _local_wipo_artifact(wipo_raw_path, wipo_retrieved_at),
    ]
    artifacts.extend(new_artifacts)
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
    base_catalog = _without_wave2_catalog_entries(_read_json(base_catalog_path))
    coverage = _coverage_policies(base_catalog=base_catalog, outcomes=outcomes)
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
        issues = "; ".join(item.message for item in validation.issues)
        raise ValueError(f"Wave 2 schema-4 validation did not pass: {issues}")
    catalog = build_wave2_catalog(
        base_catalog=base_catalog,
        coverage=coverage,
        display_catalog=display_catalog,
    )
    catalog_output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(catalog_output_path, catalog)
    sensitivity = sensitivity_experiments(observations)
    _write_report(
        report_root=report_root,
        release_id=release_id,
        coverage=coverage,
        outcomes=outcomes,
        artifacts=new_artifacts,
        sensitivity=sensitivity,
    )
    repository = ReleaseRepository(release_root, catalog_output_path)
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
