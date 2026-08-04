"""Production onboarding for narrowly frozen Phase 5 GHSL locality criteria.

The builder migrates the immutable schema-4 normalized baseline through a generic
schema-5 processor and adds one or more independently configured GHSL criteria.
Each caller still publishes one additive immutable release at a time.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any

from konsider.domain.locality_aggregation import aggregate_locality_criterion
from konsider.ingestion.current_release import (
    CriterionBuildResult,
    CurrentReleaseError,
    CurrentReleaseRepository,
    GenericReleaseWorker,
    SourceBytesUnavailable,
)

BASE_RELEASE_ID = "2026-07-28.2"
GHSL_ARCHIVE_PATH = Path(
    "data/raw/phase5g/c66-ghs-ucdb-r2024a-v1-2/" "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip"
)
GHSL_ARCHIVE_SHA256 = "966b96ef701a8b0053467179a1231ddc24830ac2693aadd7d1388f281795c0bb"
GHSL_CSV_MEMBER = "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A.csv"
GHSL_SOURCE_VERSION = "GHS-UCDB-R2024A-V1.2"
GHSL_ASSET_URL = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/"
    "GHS_UCDB_GLOBE_R2024A/GHS_UCDB_THEME_GLOBE_R2024A/"
    "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A/V1-2/"
    "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip"
)
LOCALITY_UNIVERSE_ID = "ghsl-ucdb-top5-population-v1"
LOCALITY_UNIVERSE_VERSION = "1.0"
UNIVERSE_LINEAGE_ID = "lineage:ghsl-ucdb-r2024a-v1.2:locality-universe"
ATTEMPTED_AT = "2026-07-29T00:00:00+05:30"
MINIMUM_POPULATION = 50_000
MAXIMUM_LOCALITIES_PER_COUNTRY = 5


@dataclass(frozen=True)
class LocalityCriterionConfig:
    criterion_id: str
    display_name: str
    historical_names: tuple[str, ...]
    description: str
    field: str
    raw_unit: str
    reference_start: str
    reference_end: str
    maximum_raw_value: Decimal
    scoring_method_version: str
    aggregation_policy_id: str
    source_lineage_id: str
    interpretation: str
    caveats: tuple[str, ...]
    quality_limitations: tuple[str, ...]
    quality_flags: tuple[str, ...]


C66 = LocalityCriterionConfig(
    criterion_id="C66",
    display_name="Extreme heat exposure",
    historical_names=("Extreme-weather risk",),
    description=(
        "Locality-derived annual mean number of days when daily maximum Universal Thermal "
        "Climate Index exceeds 32 degrees Celsius, for the decade ending 2020."
    ),
    field="CL_UTC_T32_2020",
    raw_unit="annual_mean_days",
    reference_start="2011-01-01",
    reference_end="2020-12-31",
    maximum_raw_value=Decimal("365"),
    scoring_method_version="c66-extreme-heat-days-linear-v1",
    aggregation_policy_id="c66-extreme-heat-top2-v1",
    source_lineage_id="lineage:C66:ghsl-climate-r2024a-v1.2",
    interpretation=(
        "Fewer extreme-heat days receive a higher score. The country result averages the two "
        "best-scoring major urban centres, or uses one where only one qualifies."
    ),
    caveats=(
        "Konsider interprets CL_UTC_T32_2020 as annual mean extreme-heat days because the "
        "publisher's indicator name, unit, upstream variable, and observed 0-357 range support "
        "that reading. The JRC methodology sentence inconsistently refers to counting pixels.",
        "The underlying decadal reference ends in 2020.",
        "This is extreme heat exposure, not broad extreme-weather or climate risk.",
    ),
    quality_limitations=(
        "Urban-centre averages do not represent neighbourhood heat differences.",
        "The measure does not include adaptation, household cooling, health vulnerability, "
        "floods, storms, drought, or wildfire.",
    ),
    quality_flags=(
        "SOURCE_DOCUMENTATION_AGGREGATION_DISCLAIMER",
        "SOURCE_VALUE_INTERPRETED_AS_ANNUAL_MEAN_DAYS",
    ),
)

C67 = LocalityCriterionConfig(
    criterion_id="C67",
    display_name="Projected warm-day frequency (2030)",
    historical_names=("Long-term climate-change exposure",),
    description=(
        "Locality-derived projected percentage of days when daily maximum temperature exceeds "
        "the calendar-day 90th percentile, under SSP2-4.5 for the decade ending 2030."
    ),
    field="CL_WDS_245_2030",
    raw_unit="percent_of_days",
    reference_start="2021-01-01",
    reference_end="2030-12-31",
    maximum_raw_value=Decimal("100"),
    scoring_method_version="c67-projected-warm-days-ssp245-linear-v1",
    aggregation_policy_id="c67-projected-warm-days-top2-v1",
    source_lineage_id="lineage:C67:ghsl-climate-r2024a-v1.2",
    interpretation=(
        "A smaller projected share of unusually warm days receives a higher score. The country "
        "result averages the two best-scoring major urban centres, or uses one where only one "
        "qualifies."
    ),
    caveats=(
        "This is a scenario-based projection under SSP2-4.5, not an observed outcome or a "
        "forecast for a particular day.",
        "Warm days are defined relative to each calendar day's 1961-1990 local temperature "
        "baseline; the measure is not the number of days above a universal heat threshold.",
        "The source uses the EC-Earth3 climate model and reports a zonal average of source-pixel "
        "values for each urban centre.",
        "This deliberately replaces the broader historical label Long-term climate-change "
        "exposure; it does not measure total climate risk, adaptation, floods, drought, storms, "
        "wildfire, or sea-level rise.",
    ),
    quality_limitations=(
        "A single climate model and scenario do not express the full projection uncertainty.",
        "Urban-centre averages do not represent neighbourhood-level temperature differences.",
    ),
    quality_flags=(
        "PROJECTED_SSP2_4_5",
        "SINGLE_MODEL_EC_EARTH3",
        "RELATIVE_TO_1961_1990_CALENDAR_DAY_BASELINE",
    ),
)

CRITERIA = {config.criterion_id: config for config in (C66, C67)}

COUNTRY_NAME_ALIASES = {
    "bahamas": "BHS",
    "bolivia": "BOL",
    "moldova": "MDA",
    "russia": "RUS",
    "slovakia": "SVK",
    "south korea": "KOR",
    "turkey": "TUR",
    "turkiye": "TUR",
    "united states": "USA",
}

PRESET_WEIGHTS = {
    "equal_weight_mvp": {"C66": 1.0, "C67": 1.0},
    "safety_and_stability": {"C66": 0.6, "C67": 0.6},
    "affordability_first": {"C66": 0.4, "C67": 0.4},
    "quality_of_life": {"C66": 1.0, "C67": 1.0},
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _normalized_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value).casefold()
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_marks.replace(", the", "").replace("the ", "").split())


def _quality_flag(value: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")
    return normalized or "UNSPECIFIED_QUALITY_FLAG"


def _country_context(
    universe_path: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    universe = _read_json(universe_path)
    countries = {row["code"]: row for row in universe["countries"]}
    names = {_normalized_name(row["display_name"]): row["code"] for row in countries.values()}
    names.update({_normalized_name(name): code for name, code in COUNTRY_NAME_ALIASES.items()})
    return countries, names


def _load_ghsl_rows(archive_path: Path) -> list[dict[str, str]]:
    if not archive_path.exists():
        raise SourceBytesUnavailable(
            f"Retained GHSL source archive is unavailable: {archive_path.as_posix()}"
        )
    actual = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if actual != GHSL_ARCHIVE_SHA256:
        raise CurrentReleaseError(
            f"GHSL archive checksum mismatch: expected {GHSL_ARCHIVE_SHA256}, got {actual}."
        )
    with zipfile.ZipFile(archive_path) as archive:
        try:
            body = archive.read(GHSL_CSV_MEMBER)
        except KeyError as exc:
            raise CurrentReleaseError(f"GHSL archive lacks {GHSL_CSV_MEMBER}.") from exc
    return list(csv.DictReader(io.StringIO(body.decode("cp1252"))))


def _select_localities(
    rows: Iterable[dict[str, str]],
    *,
    stable_countries: dict[str, dict[str, Any]],
    country_names: dict[str, str],
) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_source_ids: set[str] = set()
    for row in rows:
        source_id = row["ID_UC_G0"].strip()
        if source_id in seen_source_ids:
            raise CurrentReleaseError(f"Duplicate GHSL urban-centre ID {source_id}.")
        seen_source_ids.add(source_id)
        country_code = country_names.get(_normalized_name(row["GC_CNT_GAD_2025"]))
        if country_code not in stable_countries:
            continue
        try:
            population = Decimal(row["GC_POP_TOT_2025"])
        except Exception as exc:
            raise CurrentReleaseError(
                f"Invalid GHSL population for urban centre {source_id}."
            ) from exc
        if population >= MINIMUM_POPULATION:
            grouped[country_code].append(row)
    selected: dict[str, list[dict[str, str]]] = {}
    for country_code in sorted(stable_countries):
        candidates = sorted(
            grouped.get(country_code, []),
            key=lambda row: (
                -Decimal(row["GC_POP_TOT_2025"]),
                int(row["ID_UC_G0"]),
            ),
        )
        selected[country_code] = candidates[:MAXIMUM_LOCALITIES_PER_COUNTRY]
    selected_count = sum(len(rows) for rows in selected.values())
    selected_countries = {code for code, country_rows in selected.items() if country_rows}
    if selected_count != 388 or selected_countries != set(stable_countries) - {"ATG", "GRD"}:
        raise CurrentReleaseError(
            "Frozen locality-universe selection no longer reconciles to 388 localities and "
            "89 countries with only ATG and GRD absent."
        )
    return selected


def _country_entities(countries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "entity_id": f"country:{code}",
            "entity_type": "COUNTRY",
            "display_name": row["display_name"],
            "country_codes": [code],
            "aliases": [],
            "source_mappings": [
                {
                    "source_id": "iso-3166",
                    "source_version": "stable_supported_v1",
                    "source_entity_id": code,
                }
            ],
        }
        for code, row in sorted(countries.items())
    ]


def _locality_entities(
    selected: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    entities = []
    for country_code, rows in sorted(selected.items()):
        for row in rows:
            source_id = row["ID_UC_G0"].strip()
            entities.append(
                {
                    "entity_id": f"ghsl-uc:{source_id}",
                    "entity_type": "CITY",
                    "display_name": row["GC_UCN_MAI_2025"].strip(),
                    "country_codes": [country_code],
                    "aliases": [],
                    "source_mappings": [
                        {
                            "source_id": "jrc-ghs-ucdb-climate",
                            "source_version": GHSL_SOURCE_VERSION,
                            "source_entity_id": source_id,
                        }
                    ],
                }
            )
    return entities


def _locality_universe(entities: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return {
        "locality_universe_id": LOCALITY_UNIVERSE_ID,
        "locality_universe_version": LOCALITY_UNIVERSE_VERSION,
        "locality_type": "CITY",
        "source_lineage_id": UNIVERSE_LINEAGE_ID,
        "selection": {
            "method": "BOUNDED_POPULATION",
            "minimum_population": MINIMUM_POPULATION,
            "maximum_per_country": MAXIMUM_LOCALITIES_PER_COUNTRY,
            "order_by": "GC_POP_TOT_2025",
            "order_direction": "DESC",
            "tie_breakers": ["ID_UC_G0_ASC"],
            "independent_of_criterion_values": True,
        },
        "country_treatment": {
            "no_qualifying_locality": "EXPLICIT_NO_LOCALITY_OUTCOME",
            "single_locality": "ALLOW_POLICY_TO_DECIDE",
            "cross_border": "SOURCE_PARENT_COUNTRY_V1",
        },
        "entity_ids": sorted(row["entity_id"] for row in entities if row["entity_type"] == "CITY"),
    }


def _universe_lineage() -> dict[str, Any]:
    return {
        "lineage_id": UNIVERSE_LINEAGE_ID,
        "lineage_version": "1.0",
        "sources": [
            {
                "source_id": "jrc-ghs-ucdb-climate",
                "role": "ENTITY_UNIVERSE",
                "source_version": GHSL_SOURCE_VERSION,
                "asset_uri": GHSL_ASSET_URL,
                "checksum": f"sha256:{GHSL_ARCHIVE_SHA256}",
                "licence_id": "CC-BY-4.0",
                "publisher": "European Commission, Joint Research Centre",
                "dataset_version": "GHS-UCDB R2024A V1.2",
                "canonical_page_url": (
                    "https://data.jrc.ec.europa.eu/dataset/" "1a338be6-7eaf-480c-9664-3a8ade88cbcd"
                ),
                "attribution": (
                    "European Commission, Joint Research Centre, GHS-UCDB R2024A V1.2, "
                    "licensed CC BY 4.0; transformed by Konsider."
                ),
                "reference_period": "2025 population and urban-centre identities",
            }
        ],
        "transforms": [
            {
                "step_id": "select-ghsl-top-five-population-localities",
                "transform_version": "ghsl-ucdb-top5-population-v1",
                "input_refs": ["jrc-ghs-ucdb-climate"],
                "output_ref": LOCALITY_UNIVERSE_ID,
            }
        ],
    }


def _criterion_lineage(config: LocalityCriterionConfig) -> dict[str, Any]:
    return {
        "lineage_id": config.source_lineage_id,
        "lineage_version": "1.0",
        "sources": [
            {
                "source_id": "jrc-ghs-ucdb-climate",
                "role": "PRIMARY_OBSERVATION",
                "source_version": GHSL_SOURCE_VERSION,
                "asset_uri": f"{GHSL_ASSET_URL}#{config.field}",
                "checksum": f"sha256:{GHSL_ARCHIVE_SHA256}",
                "licence_id": "CC-BY-4.0",
                "publisher": "European Commission, Joint Research Centre",
                "dataset_version": "GHS-UCDB R2024A V1.2",
                "canonical_page_url": (
                    "https://data.jrc.ec.europa.eu/dataset/" "1a338be6-7eaf-480c-9664-3a8ade88cbcd"
                ),
                "attribution": (
                    "European Commission, Joint Research Centre, GHS-UCDB R2024A V1.2, "
                    "licensed CC BY 4.0; transformed by Konsider."
                ),
                "reference_period": (f"{config.reference_start} through {config.reference_end}"),
            }
        ],
        "transforms": [
            {
                "step_id": f"parse-{config.field.lower()}",
                "transform_version": "jrc-ghsl-urban-climate-csv-v1",
                "input_refs": ["jrc-ghs-ucdb-climate"],
                "output_ref": f"{config.criterion_id}-locality-observations",
            },
            {
                "step_id": f"score-{config.criterion_id.lower()}",
                "transform_version": config.scoring_method_version,
                "input_refs": [f"{config.criterion_id}-locality-observations"],
                "output_ref": f"{config.criterion_id}-locality-scores",
            },
        ],
    }


def _direct_scope() -> dict[str, Any]:
    return {
        "evidence_level": "COUNTRY",
        "result_level": "COUNTRY",
        "locality_type": None,
        "derivation": "DIRECT",
        "locality_universe_id": None,
        "aggregation_policy_id": None,
        "locality_analysis_threshold": None,
    }


def _locality_scope(config: LocalityCriterionConfig) -> dict[str, Any]:
    return {
        "evidence_level": "LOCALITY",
        "result_level": "COUNTRY",
        "locality_type": "CITY",
        "derivation": "AGGREGATED_FROM_LOCALITIES",
        "locality_universe_id": LOCALITY_UNIVERSE_ID,
        "aggregation_policy_id": config.aggregation_policy_id,
        "locality_analysis_threshold": 0.6,
    }


def _aggregation_policy(config: LocalityCriterionConfig) -> dict[str, Any]:
    return {
        "policy_id": config.aggregation_policy_id,
        "policy_version": "1.0",
        "eligible_locality_universe": {
            "locality_universe_id": LOCALITY_UNIVERSE_ID,
            "locality_universe_version": LOCALITY_UNIVERSE_VERSION,
        },
        "source_criterion_id": config.criterion_id,
        "result_criterion_id": config.criterion_id,
        "locality_type": "CITY",
        "result_level": "COUNTRY",
        "selection": {"method": "TOP_N_MEAN", "n": 2},
        "minimum_valid_localities": 1,
        "score_range": {"minimum": 0, "maximum": 10},
        "score_precision": 8,
        "tie_handling": "STABLE_ENTITY_ID",
        "one_locality_treatment": "USE_AVAILABLE",
        "required_lineage_roles": ["PRIMARY_OBSERVATION", "ENTITY_UNIVERSE"],
    }


def _migrated_lineage(
    criterion_id: str,
    base_manifest: dict[str, Any],
    registrations: list[dict[str, Any]],
    raw_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    lineage_id = f"lineage:{criterion_id}:schema4-{base_manifest['release_id']}"
    matching_registrations = sorted(
        (row for row in registrations if row["criterion_id"] == criterion_id),
        key=lambda row: row["source_id"],
    )
    artifacts_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for artifact in raw_artifacts:
        artifacts_by_source[artifact["source_id"]].append(artifact)
    sources = []
    for index, registration in enumerate(matching_registrations):
        source_id = registration["source_id"]
        artifacts = sorted(
            artifacts_by_source.get(source_id, []),
            key=lambda row: row["artifact_id"],
        )
        checksum = artifacts[0]["artifact_id"] if artifacts else None
        asset_uri = (
            registration.get("download_urls", [None])[0]
            or registration.get("canonical_page_url")
            or f"konsider-source:{source_id}"
        )
        sources.append(
            {
                "source_id": source_id,
                "role": "PRIMARY_OBSERVATION" if index == 0 else "AUXILIARY",
                "source_version": registration["source_version"],
                "asset_uri": asset_uri,
                "checksum": checksum,
                "licence_id": registration["license_name"],
                "publisher": registration["publisher"],
                "dataset_version": registration["dataset_version"],
                "canonical_page_url": registration["canonical_page_url"],
                "attribution": registration["attribution"],
                "reference_period": registration["reference_period"],
            }
        )
    migration_source_id = f"konsider-schema4-{criterion_id}"
    sources.append(
        {
            "source_id": migration_source_id,
            "role": "SCORING_INPUT",
            "source_version": base_manifest["release_id"],
            "asset_uri": f"konsider-release:{base_manifest['release_id']}",
            "checksum": base_manifest["release_checksum"],
            "licence_id": "UPSTREAM-LICENCES-AS-RECORDED",
            "publisher": "Konsider",
            "dataset_version": base_manifest["release_id"],
            "canonical_page_url": None,
            "attribution": (
                "Normalized migration input; original publisher attribution is retained "
                "in the accompanying source-lineage inputs."
            ),
            "reference_period": None,
        }
    )
    return {
        "lineage_id": lineage_id,
        "lineage_version": "1.0",
        "sources": sources,
        "transforms": [
            {
                "step_id": "migrate-normalized-country-result",
                "transform_version": "schema4-to-schema5-normalized-v1",
                "input_refs": [row["source_id"] for row in sources],
                "output_ref": f"{criterion_id}-country-results",
            }
        ],
    }


def _coverage(
    *,
    mode: str,
    stable_count: int,
    counts: dict[str, int],
    minimum: int,
    threshold: float | None,
    lineage_ids: list[str],
    score_minimum: float,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "stable_universe_id": "stable_supported_v1",
        "stable_country_count": stable_count,
        "valid_country_count": counts["valid"],
        "minimum_valid_country_count": minimum,
        "outcome_counts": {
            status: counts[status]
            for status in ("valid", "missing", "stale", "invalid", "rejected")
        },
        "activation_threshold": threshold,
        "score_range": {"minimum": score_minimum, "maximum": 10},
        "source_lineage_ids": lineage_ids,
    }


def _build_inputs(
    *,
    base_release_path: Path,
    base_catalog_path: Path,
    universe_path: Path,
    archive_path: Path,
    locality_criterion_ids: tuple[str, ...],
) -> tuple[
    dict[str, Any],
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    dict[str, list[dict[str, str]]],
]:
    base_manifest = _read_json(base_release_path / "manifest.json")
    if base_manifest["schema_version"] != "konsider-release-4.0":
        raise CurrentReleaseError("The migration baseline must be a schema-4 release.")
    base_catalog = _read_json(base_catalog_path)
    base_registrations = _read_json(base_release_path / "sources.json")
    base_raw_artifacts = _read_json(base_release_path / "raw-artifacts.json")
    countries, country_names = _country_context(universe_path)
    ghsl_rows = _load_ghsl_rows(archive_path)
    selected = _select_localities(
        ghsl_rows,
        stable_countries=countries,
        country_names=country_names,
    )
    entities = _country_entities(countries) + _locality_entities(selected)
    locality_universe = _locality_universe(entities)
    base_attempts = _read_jsonl(base_release_path / "attempts.jsonl")
    base_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in base_attempts:
        base_counts[row["criterion_id"]][row["outcome"]] += 1

    criteria: list[dict[str, Any]] = []
    policies: list[dict[str, Any]] = []
    lineages: list[dict[str, Any]] = []
    for criterion in base_catalog["criteria"]:
        criterion_id = criterion["id"]
        lineage = _migrated_lineage(
            criterion_id,
            base_manifest,
            base_registrations,
            base_raw_artifacts,
        )
        lineage_ids = [lineage["lineage_id"]]
        old_coverage = criterion["coverage"]
        counts = {
            status: base_counts[criterion_id].get(status, 0)
            for status in ("valid", "missing", "stale", "invalid", "rejected")
        }
        coverage = _coverage(
            mode=old_coverage["mode"],
            stable_count=old_coverage["stable_country_count"],
            counts=counts,
            minimum=old_coverage["minimum_valid_country_count"],
            threshold=old_coverage["activation_threshold"],
            lineage_ids=lineage_ids,
            score_minimum=float(old_coverage["score_min"]),
        )
        criteria.append(
            {
                "id": criterion_id,
                "display_name": criterion["display_name"],
                "historical_names": [],
                "category": criterion["category"],
                "description": criterion["description"],
                "direction": criterion["direction"],
                "raw_unit": criterion["raw_unit"],
                "interpretation": criterion["interpretation"],
                "caveats": criterion["caveats"],
                "quality_limitations": criterion["quality_limitations"],
                "ready": criterion["ready"],
                "default_enabled": criterion["default_enabled"],
                "experimental": criterion["experimental"],
                "scoring_method_version": criterion["scoring_method_version"],
                "coverage": coverage,
                "scope": _direct_scope(),
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
            }
        )
        policies.append(
            {
                "criterion_id": criterion_id,
                "source_lineage_ids": lineage_ids,
                "parser": {"id": "schema4-normalized-release", "version": "1.0"},
                "scoring": {
                    "id": "schema4-canonical-score",
                    "version": criterion["scoring_method_version"],
                },
                "coverage_mode": coverage["mode"],
                "scope": _direct_scope(),
                "derivation": {"mode": "DIRECT", "processor": None},
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
                "ready": criterion["ready"],
                "experimental": criterion["experimental"],
            }
        )
        lineages.append(lineage)

    aggregation_policies = []
    for criterion_id in locality_criterion_ids:
        config = CRITERIA[criterion_id]
        lineage_ids = [config.source_lineage_id, UNIVERSE_LINEAGE_ID]
        counts = {"valid": 89, "missing": 2, "stale": 0, "invalid": 0, "rejected": 0}
        coverage = _coverage(
            mode="CONDITIONAL_COMPLETE_CASE",
            stable_count=len(countries),
            counts=counts,
            minimum=82,
            threshold=0.6,
            lineage_ids=lineage_ids,
            score_minimum=0,
        )
        scope = _locality_scope(config)
        criteria.append(
            {
                "id": config.criterion_id,
                "display_name": config.display_name,
                "historical_names": list(config.historical_names),
                "category": "Climate and environment",
                "description": config.description,
                "direction": "lower_is_better",
                "raw_unit": config.raw_unit,
                "interpretation": config.interpretation,
                "caveats": list(config.caveats),
                "quality_limitations": list(config.quality_limitations),
                "ready": True,
                "default_enabled": True,
                "experimental": True,
                "scoring_method_version": config.scoring_method_version,
                "coverage": coverage,
                "scope": scope,
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
            }
        )
        policies.append(
            {
                "criterion_id": config.criterion_id,
                "source_lineage_ids": lineage_ids,
                "parser": {"id": "jrc-ghsl-urban-climate-csv", "version": "1.0"},
                "scoring": {
                    "id": "lower-is-better-linear-domain",
                    "version": config.scoring_method_version,
                },
                "coverage_mode": "CONDITIONAL_COMPLETE_CASE",
                "scope": scope,
                "derivation": {
                    "mode": "AGGREGATED_FROM_LOCALITIES",
                    "processor": {"id": "top-n-mean", "version": "1.0"},
                },
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
                "ready": True,
                "experimental": True,
            }
        )
        lineages.append(_criterion_lineage(config))
        aggregation_policies.append(_aggregation_policy(config))
    lineages.append(_universe_lineage())

    presets = []
    for preset in base_catalog["profiles"]:
        weights = dict(preset["weights"])
        for criterion_id in locality_criterion_ids:
            weights[criterion_id] = PRESET_WEIGHTS[preset["id"]][criterion_id]
        presets.append({**preset, "weights": weights})
    catalog = {
        "schema_version": "consumer-catalog-3.0",
        "compatible_release_schema_major": 5,
        "target_api_contract_version": "konsider-api-2.0",
        "coverage_policy_version": base_catalog["coverage_policy_version"],
        "stable_universe_id": base_catalog["stable_universe_id"],
        "geographic_entities": entities,
        "criteria": criteria,
        "locality_universes": [locality_universe],
        "aggregation_policies": aggregation_policies,
        "preference_presets": presets,
    }
    return (
        catalog,
        tuple(entities),
        tuple(lineages),
        (locality_universe,),
        tuple(aggregation_policies),
        tuple(policies),
        selected,
    )


def _schema4_processor(
    base_release_path: Path,
    attempted_at: str,
):
    observations = {
        row["observation_id"]: row for row in _read_jsonl(base_release_path / "observations.jsonl")
    }
    scores = {
        (row["criterion_id"], row["country_code"]): row
        for row in _read_jsonl(base_release_path / "scores.jsonl")
    }
    attempts = {
        (row["criterion_id"], row["country_code"]): row
        for row in _read_jsonl(base_release_path / "attempts.jsonl")
    }

    def processor(policy, _criterion_lineages, _all_lineages):
        criterion_id = policy["criterion_id"]
        lineage_id = policy["source_lineage_ids"][0]
        result = CriterionBuildResult()
        relevant = sorted(
            (
                (country_code, attempt)
                for (candidate, country_code), attempt in attempts.items()
                if candidate == criterion_id
            ),
            key=lambda item: item[0],
        )
        for country_code, attempt in relevant:
            subject = {"entity_id": f"country:{country_code}", "entity_type": "COUNTRY"}
            flags = ["MIGRATED_FROM_SCHEMA4_NORMALIZED_RELEASE"]
            if attempt["outcome"] == "valid":
                old_score = scores[(criterion_id, country_code)]
                inputs = [observations[item] for item in old_score["input_observation_ids"]]
                flags.extend(
                    _quality_flag(flag)
                    for observation in inputs
                    for flag in observation.get("quality_flags", [])
                )
                flags = sorted(set(flags))
                observation_id = f"obs:migrated:{criterion_id}:country:{country_code}"
                score_id = f"score:migrated:{criterion_id}:country:{country_code}"
                observation = {
                    "observation_id": observation_id,
                    "criterion_id": criterion_id,
                    "subject": subject,
                    "value": old_score["score"],
                    "unit": "normalized_score_1_10",
                    "reference_period": {
                        "start": min(row["reference_start"] for row in inputs),
                        "end": max(row["reference_end"] for row in inputs),
                    },
                    "source_lineage_id": lineage_id,
                    "quality_flags": flags,
                }
                score = {
                    "score_id": score_id,
                    "criterion_id": criterion_id,
                    "subject": subject,
                    "score": old_score["score"],
                    "observation_ids": [observation_id],
                    "scoring_method_version": policy["scoring"]["version"],
                    "source_lineage_id": lineage_id,
                    "quality_flags": flags,
                }
                result.observations.append(observation)
                result.scores.append(score)
                evidence_kind = "DIRECT_OBSERVATION"
                reason_codes = []
            else:
                observation_id = score_id = None
                evidence_kind = "NONE"
                reason_codes = attempt["reason_codes"]
            result.criterion_outcomes.append(
                {
                    "criterion_id": criterion_id,
                    "subject": subject,
                    "outcome": attempt["outcome"],
                    "evidence_kind": evidence_kind,
                    "attempted_at": attempted_at,
                    "observation_id": observation_id,
                    "score_id": score_id,
                    "derived_evidence_id": None,
                    "source_lineage_ids": sorted(policy["source_lineage_ids"]),
                    "reason_codes": reason_codes,
                    "quality_flags": flags,
                }
            )
        return result

    return processor


def _score_lower_is_better(value: Decimal, maximum: Decimal) -> float:
    bounded = min(max(value, Decimal()), maximum)
    score = Decimal("10") - Decimal("9") * bounded / maximum
    return float(score.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN))


def _locality_processor(
    *,
    release_id: str,
    attempted_at: str,
    catalog: dict[str, Any],
    entities: tuple[dict[str, Any], ...],
    locality_universe: dict[str, Any],
    aggregation_policies: tuple[dict[str, Any], ...],
    selected: dict[str, list[dict[str, str]]],
):
    criteria = {row["id"]: row for row in catalog["criteria"]}
    policies = {row["policy_id"]: row for row in aggregation_policies}

    def processor(policy, _criterion_lineages, _all_lineages):
        config = CRITERIA[policy["criterion_id"]]
        lineage_id = config.source_lineage_id
        result = CriterionBuildResult()
        for country_code, rows in sorted(selected.items()):
            for row in rows:
                source_id = row["ID_UC_G0"].strip()
                value_text = row.get(config.field, "").strip()
                if not value_text:
                    continue
                try:
                    value = Decimal(value_text)
                except Exception as exc:
                    raise CurrentReleaseError(
                        f"Invalid {config.field} value for GHSL urban centre {source_id}."
                    ) from exc
                if value < 0 or value > config.maximum_raw_value:
                    raise CurrentReleaseError(
                        f"Out-of-range {config.field} value {value} for {source_id}."
                    )
                entity_id = f"ghsl-uc:{source_id}"
                subject = {"entity_id": entity_id, "entity_type": "CITY"}
                observation_id = f"obs:{config.criterion_id}:{entity_id}:{config.reference_end[:4]}"
                score_id = f"score:{config.criterion_id}:{entity_id}:{config.reference_end[:4]}"
                flags = sorted(config.quality_flags)
                result.observations.append(
                    {
                        "observation_id": observation_id,
                        "criterion_id": config.criterion_id,
                        "subject": subject,
                        "value": float(value),
                        "unit": config.raw_unit,
                        "reference_period": {
                            "start": config.reference_start,
                            "end": config.reference_end,
                        },
                        "source_lineage_id": lineage_id,
                        "quality_flags": flags,
                    }
                )
                result.scores.append(
                    {
                        "score_id": score_id,
                        "criterion_id": config.criterion_id,
                        "subject": subject,
                        "score": _score_lower_is_better(value, config.maximum_raw_value),
                        "observation_ids": [observation_id],
                        "scoring_method_version": config.scoring_method_version,
                        "source_lineage_id": lineage_id,
                        "quality_flags": flags,
                    }
                )
        aggregates = aggregate_locality_criterion(
            release_id=release_id,
            criterion=criteria[config.criterion_id],
            aggregation_policy=policies[config.aggregation_policy_id],
            locality_universe=locality_universe,
            geographic_entities=entities,
            observations=tuple(result.observations),
            scores=tuple(result.scores),
            source_lineage_ids=tuple(policy["source_lineage_ids"]),
            attempted_at=attempted_at,
        )
        for aggregate in aggregates:
            if aggregate.observation:
                result.observations.append(aggregate.observation)
            if aggregate.score:
                result.scores.append(aggregate.score)
            if aggregate.evidence:
                result.derived_country_evidence.append(aggregate.evidence)
            result.criterion_outcomes.append(aggregate.outcome)
        return result

    return processor


def build_locality_release(
    *,
    release_id: str,
    locality_criterion_ids: tuple[str, ...],
    base_release_path: Path = Path(f"data/releases/{BASE_RELEASE_ID}"),
    base_catalog_path: Path = Path(f"data/catalogs/releases/{BASE_RELEASE_ID}.json"),
    universe_path: Path = Path("data/country-universes/stable-supported-v1.json"),
    archive_path: Path = GHSL_ARCHIVE_PATH,
    release_root: Path = Path("data/releases"),
    catalog_snapshot_root: Path = Path("data/catalogs/releases"),
    activate: bool = False,
    attempted_at: str = ATTEMPTED_AT,
) -> tuple[Path, str]:
    """Build, publish, replay, and optionally activate one additive schema-5 release."""

    unknown = set(locality_criterion_ids) - set(CRITERIA)
    if unknown:
        raise CurrentReleaseError(f"Unknown locality criterion configurations: {sorted(unknown)}")
    inputs = _build_inputs(
        base_release_path=base_release_path,
        base_catalog_path=base_catalog_path,
        universe_path=universe_path,
        archive_path=archive_path,
        locality_criterion_ids=locality_criterion_ids,
    )
    (
        catalog,
        entities,
        lineages,
        locality_universes,
        aggregation_policies,
        criterion_policies,
        selected,
    ) = inputs
    processors = {
        ("schema4-normalized-release", "1.0"): _schema4_processor(base_release_path, attempted_at),
        ("jrc-ghsl-urban-climate-csv", "1.0"): _locality_processor(
            release_id=release_id,
            attempted_at=attempted_at,
            catalog=catalog,
            entities=entities,
            locality_universe=locality_universes[0],
            aggregation_policies=aggregation_policies,
            selected=selected,
        ),
    }
    worker = GenericReleaseWorker(processors)
    artifacts = worker.build(
        release_id=release_id,
        catalog=catalog,
        entities=entities,
        source_lineages=lineages,
        locality_universes=locality_universes,
        aggregation_policies=aggregation_policies,
        criterion_policies=criterion_policies,
        attempted_at=attempted_at,
    )
    repository = CurrentReleaseRepository(release_root, catalog_snapshot_root)
    repository.write_draft(release_id, artifacts)
    published = repository.publish(release_id, require_product_ready=True, activate=False)
    replay = repository.replay(published, processors=processors)
    if not replay.passed:
        raise CurrentReleaseError(
            f"Published release replay failed with {replay.status}: {replay.detail or ''}"
        )
    if activate:
        repository.activate(release_id)
    return published, replay.status


def replay_locality_release(
    release_path: Path,
    *,
    base_release_path: Path = Path(f"data/releases/{BASE_RELEASE_ID}"),
    base_catalog_path: Path = Path(f"data/catalogs/releases/{BASE_RELEASE_ID}.json"),
    universe_path: Path = Path("data/country-universes/stable-supported-v1.json"),
    archive_path: Path = GHSL_ARCHIVE_PATH,
    catalog_snapshot_root: Path = Path("data/catalogs/releases"),
) -> str:
    """Replay a published Phase 5 locality release from its frozen processors and inputs."""

    repository = CurrentReleaseRepository(release_path.parent, catalog_snapshot_root)
    loaded = repository.load(release_path)
    locality_criterion_ids = tuple(
        sorted(
            row["id"]
            for row in loaded.artifacts.consumer_catalog["criteria"]
            if row["scope"]["derivation"] == "AGGREGATED_FROM_LOCALITIES"
        )
    )
    _catalog, _entities, _lineages, _universes, _policies, _criterion_policies, selected = (
        _build_inputs(
            base_release_path=base_release_path,
            base_catalog_path=base_catalog_path,
            universe_path=universe_path,
            archive_path=archive_path,
            locality_criterion_ids=locality_criterion_ids,
        )
    )
    attempted_values = {row["attempted_at"] for row in loaded.artifacts.criterion_outcomes}
    if len(attempted_values) != 1:
        raise CurrentReleaseError("Replay requires one deterministic attempted_at value.")
    attempted_at = next(iter(attempted_values))
    input_release_ids = {
        row["input_release_id"] for row in loaded.artifacts.derived_country_evidence
    }
    if len(input_release_ids) != 1:
        raise CurrentReleaseError("Replay requires one frozen locality input release ID.")
    locality_input_release_id = next(iter(input_release_ids))
    processors = {
        ("schema4-normalized-release", "1.0"): _schema4_processor(base_release_path, attempted_at),
        ("jrc-ghsl-urban-climate-csv", "1.0"): _locality_processor(
            release_id=locality_input_release_id,
            attempted_at=attempted_at,
            catalog=loaded.artifacts.consumer_catalog,
            entities=loaded.artifacts.geographic_entities,
            locality_universe=loaded.artifacts.locality_universes[0],
            aggregation_policies=loaded.artifacts.aggregation_policies,
            selected=selected,
        ),
    }
    result = repository.replay(release_path, processors=processors)
    if not result.passed:
        print(
            "replay_detail="
            f"{result.detail or 'unspecified'};"
            f"mismatched_files={','.join(result.mismatched_files) or 'none'}"
        )
    return result.status


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--release-id")
    action.add_argument("--replay", type=Path)
    parser.add_argument(
        "--criterion",
        action="append",
        choices=sorted(CRITERIA),
        dest="criteria",
    )
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--archive", type=Path, default=GHSL_ARCHIVE_PATH)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.replay is not None:
        status = replay_locality_release(args.replay, archive_path=args.archive)
        print(f"replay={status}")
        return 0 if status == "PASSED" else 1
    if not args.criteria:
        raise SystemExit("--criterion is required when building a release")
    published, replay_status = build_locality_release(
        release_id=args.release_id,
        locality_criterion_ids=tuple(args.criteria),
        archive_path=args.archive,
        activate=args.activate,
    )
    print(f"published={published.as_posix()}")
    print(f"replay={replay_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
