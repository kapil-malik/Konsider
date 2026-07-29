import copy
from collections import Counter
from pathlib import Path

import pytest

from konsider.contracts import ContractError, validate_contract
from konsider.domain.locality_aggregation import aggregate_locality_criterion
from konsider.domain.locality_models import (
    CoverageStatus,
    LocalityAggregationStatus,
    LocalityStatus,
)
from konsider.domain.phase5_ranking import rank_schema5_release
from konsider.ingestion.current_release import (
    CurrentReleaseArtifacts,
    CurrentReleaseRepository,
)

COUNTRY_NAMES = {"CAN": "Canada", "MEX": "Mexico", "USA": "United States"}
ATTEMPTED_AT = "2026-07-28T00:00:00Z"


def _lineage(lineage_id: str, role: str) -> dict:
    checksum_character = format((sum(map(ord, lineage_id)) % 15) + 1, "x")
    return {
        "lineage_id": lineage_id,
        "lineage_version": "1.0",
        "sources": [
            {
                "source_id": f"source:{lineage_id}",
                "role": role,
                "source_version": "2026",
                "asset_uri": f"local://phase5d/{lineage_id}.json",
                "checksum": f"sha256:{checksum_character * 64}",
                "licence_id": "SYNTHETIC-TEST-ONLY",
            }
        ],
        "transforms": [
            {
                "step_id": f"parse:{lineage_id}",
                "transform_version": "1.0",
                "input_refs": [f"source:{lineage_id}"],
                "output_ref": f"observations:{lineage_id}",
            }
        ],
    }


def _scope(criterion_id: str, locality: bool, threshold: float) -> dict:
    return {
        "evidence_level": "LOCALITY" if locality else "COUNTRY",
        "result_level": "COUNTRY",
        "locality_type": "CITY" if locality else None,
        "derivation": "AGGREGATED_FROM_LOCALITIES" if locality else "DIRECT",
        "locality_universe_id": "phase5d-cities-v1" if locality else None,
        "aggregation_policy_id": f"aggregate:{criterion_id}" if locality else None,
        "locality_analysis_threshold": threshold if locality else None,
    }


def _criterion(spec: dict, country_count: int) -> dict:
    mode = spec.get("coverage", "GLOBAL_CORE")
    activation = spec.get("activation", 0.6) if mode == "CONDITIONAL_COMPLETE_CASE" else None
    return {
        "id": spec["id"],
        "display_name": spec["id"],
        "historical_names": [],
        "category": "Synthetic",
        "description": "Synthetic Phase 5D criterion.",
        "direction": "higher_is_better",
        "raw_unit": "index",
        "interpretation": "Test-only deterministic opportunity score.",
        "caveats": ["Not product data."],
        "quality_limitations": [],
        "ready": spec.get("ready", True),
        "default_enabled": True,
        "experimental": spec.get("locality", False),
        "scoring_method_version": f"score:{spec['id']}:1.0",
        "coverage": {
            "mode": mode,
            "stable_universe_id": "phase5d-country-universe",
            "stable_country_count": country_count,
            "valid_country_count": 0,
            "minimum_valid_country_count": spec.get(
                "minimum_valid_country_count",
                country_count if mode == "GLOBAL_CORE" else max(1, country_count - 1),
            ),
            "outcome_counts": {
                "valid": 0,
                "missing": country_count,
                "stale": 0,
                "invalid": 0,
                "rejected": 0,
            },
            "activation_threshold": activation,
            "score_range": {"minimum": 0, "maximum": 10},
            "source_lineage_ids": [],
        },
        "scope": _scope(spec["id"], spec.get("locality", False), spec.get("threshold", 0.6)),
        "applicability": {"mode": "UNIVERSAL", "dimensions": []},
    }


def _entity_rows(countries: tuple[str, ...], locality_names: set[tuple[str, str]]) -> tuple:
    rows = [
        {
            "entity_id": f"country:{code}",
            "entity_type": "COUNTRY",
            "display_name": COUNTRY_NAMES[code],
            "country_codes": [code],
            "aliases": [],
            "source_mappings": [
                {
                    "source_id": "synthetic-countries",
                    "source_version": "2026",
                    "source_entity_id": code,
                }
            ],
        }
        for code in countries
    ]
    rows.extend(
        {
            "entity_id": f"city:{country}:{name}",
            "entity_type": "CITY",
            "display_name": f"{country} {name}",
            "country_codes": [country],
            "aliases": [],
            "source_mappings": [
                {
                    "source_id": "synthetic-cities",
                    "source_version": "2026",
                    "source_entity_id": f"{country}:{name}",
                }
            ],
        }
        for country, name in sorted(locality_names)
    )
    return tuple(rows)


def _raw_locality_rows(
    criterion_id: str,
    matrix: dict[str, dict[str, float | tuple[float, list[str]]]],
) -> tuple[list[dict], list[dict]]:
    observations, scores = [], []
    for country, values in sorted(matrix.items()):
        for locality_name, configured in sorted(values.items()):
            value, flags = configured if isinstance(configured, tuple) else (configured, [])
            entity_id = f"city:{country}:{locality_name}"
            observation_id = f"obs:raw:{criterion_id}:{entity_id}"
            observations.append(
                {
                    "observation_id": observation_id,
                    "criterion_id": criterion_id,
                    "subject": {"entity_id": entity_id, "entity_type": "CITY"},
                    "value": value,
                    "unit": "index",
                    "reference_period": {
                        "start": "2025-01-01",
                        "end": "2025-12-31",
                    },
                    "source_lineage_id": f"lineage:{criterion_id}",
                    "quality_flags": flags,
                }
            )
            scores.append(
                {
                    "score_id": f"score:raw:{criterion_id}:{entity_id}",
                    "criterion_id": criterion_id,
                    "subject": {"entity_id": entity_id, "entity_type": "CITY"},
                    "score": value,
                    "observation_ids": [observation_id],
                    "scoring_method_version": f"score:{criterion_id}:1.0",
                    "source_lineage_id": f"lineage:{criterion_id}",
                    "quality_flags": flags,
                }
            )
    return observations, scores


def _direct_country_rows(
    criterion_id: str,
    countries: tuple[str, ...],
    configured_scores: dict[str, float],
) -> tuple[list[dict], list[dict], list[dict]]:
    observations, scores, outcomes = [], [], []
    for country in countries:
        entity_id = f"country:{country}"
        value = configured_scores.get(country)
        observation = score = None
        if value is not None:
            observation = {
                "observation_id": f"obs:direct:{criterion_id}:{entity_id}",
                "criterion_id": criterion_id,
                "subject": {"entity_id": entity_id, "entity_type": "COUNTRY"},
                "value": value,
                "unit": "index",
                "reference_period": {
                    "start": "2025-01-01",
                    "end": "2025-12-31",
                },
                "source_lineage_id": f"lineage:{criterion_id}",
                "quality_flags": [],
            }
            score = {
                "score_id": f"score:direct:{criterion_id}:{entity_id}",
                "criterion_id": criterion_id,
                "subject": {"entity_id": entity_id, "entity_type": "COUNTRY"},
                "score": value,
                "observation_ids": [observation["observation_id"]],
                "scoring_method_version": f"score:{criterion_id}:1.0",
                "source_lineage_id": f"lineage:{criterion_id}",
                "quality_flags": [],
            }
            observations.append(observation)
            scores.append(score)
        outcomes.append(
            {
                "criterion_id": criterion_id,
                "subject": {"entity_id": entity_id, "entity_type": "COUNTRY"},
                "outcome": "valid" if value is not None else "missing",
                "evidence_kind": "DIRECT_OBSERVATION" if value is not None else "NONE",
                "attempted_at": ATTEMPTED_AT,
                "observation_id": observation["observation_id"] if observation else None,
                "score_id": score["score_id"] if score else None,
                "derived_evidence_id": None,
                "source_lineage_ids": [f"lineage:{criterion_id}"],
                "reason_codes": [] if value is not None else ["SOURCE_VALUE_MISSING"],
                "quality_flags": [],
            }
        )
    return observations, scores, outcomes


def _build_artifacts(
    specs: list[dict],
    *,
    countries: tuple[str, ...] = ("CAN", "MEX"),
) -> CurrentReleaseArtifacts:
    locality_names = {
        (country, locality_name)
        for spec in specs
        if spec.get("locality")
        for country, values in spec.get("scores", {}).items()
        for locality_name in values
    }
    if any(spec.get("locality") for spec in specs):
        locality_names.update((country, name) for country in countries for name in ("a", "b", "c"))
    entities = _entity_rows(countries, locality_names)
    universe_lineage = _lineage("lineage:universe", "ENTITY_UNIVERSE")
    source_lineages = [universe_lineage]
    locality_universe = {
        "locality_universe_id": "phase5d-cities-v1",
        "locality_universe_version": "1.0",
        "locality_type": "CITY",
        "source_lineage_id": "lineage:universe",
        "selection": {
            "method": "BOUNDED_POPULATION",
            "minimum_population": 50000,
            "maximum_per_country": 5,
            "order_by": "synthetic_population",
            "order_direction": "DESC",
            "tie_breakers": ["entity_id"],
            "independent_of_criterion_values": True,
        },
        "country_treatment": {
            "no_qualifying_locality": "EXPLICIT_NO_LOCALITY_OUTCOME",
            "single_locality": "ALLOW_POLICY_TO_DECIDE",
            "cross_border": "SOURCE_PARENT_COUNTRY_V1",
        },
        "entity_ids": sorted(row["entity_id"] for row in entities if row["entity_type"] == "CITY"),
    }
    criteria = [_criterion(spec, len(countries)) for spec in specs]
    criteria_by_id = {row["id"]: row for row in criteria}
    aggregation_policies, criterion_policies = [], []
    observations: list[dict] = []
    scores: list[dict] = []
    outcomes: list[dict] = []
    evidence: list[dict] = []

    for spec in specs:
        criterion_id = spec["id"]
        source_lineages.append(_lineage(f"lineage:{criterion_id}", "PRIMARY_OBSERVATION"))
        lineage_ids = [f"lineage:{criterion_id}"]
        if spec.get("locality"):
            lineage_ids.append("lineage:universe")
        criteria_by_id[criterion_id]["coverage"]["source_lineage_ids"] = lineage_ids
        criterion_policies.append(
            {
                "criterion_id": criterion_id,
                "source_lineage_ids": lineage_ids,
                "parser": {
                    "id": "synthetic-locality" if spec.get("locality") else "synthetic-national",
                    "version": "1.0",
                },
                "scoring": {
                    "id": "synthetic-score",
                    "version": f"score:{criterion_id}:1.0",
                },
                "coverage_mode": criteria_by_id[criterion_id]["coverage"]["mode"],
                "scope": criteria_by_id[criterion_id]["scope"],
                "derivation": {
                    "mode": criteria_by_id[criterion_id]["scope"]["derivation"],
                    "processor": (
                        {"id": "locality-aggregation", "version": "1.0"}
                        if spec.get("locality")
                        else None
                    ),
                },
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
                "ready": spec.get("ready", True),
                "experimental": spec.get("locality", False),
            }
        )
        if not spec.get("locality"):
            new_observations, new_scores, new_outcomes = _direct_country_rows(
                criterion_id,
                countries,
                spec.get("scores", {country: 5.0 for country in countries}),
            )
            observations.extend(new_observations)
            scores.extend(new_scores)
            outcomes.extend(new_outcomes)
            continue
        new_observations, new_scores = _raw_locality_rows(criterion_id, spec.get("scores", {}))
        observations.extend(new_observations)
        scores.extend(new_scores)
        policy = {
            "policy_id": f"aggregate:{criterion_id}",
            "policy_version": "1.0",
            "eligible_locality_universe": {
                "locality_universe_id": "phase5d-cities-v1",
                "locality_universe_version": "1.0",
            },
            "source_criterion_id": criterion_id,
            "result_criterion_id": criterion_id,
            "locality_type": "CITY",
            "result_level": "COUNTRY",
            "selection": {
                "method": spec.get("method", "TOP_N_MEAN"),
                "n": (None if spec.get("method") == "ALL_VALID_MEAN" else spec.get("n", 2)),
            },
            "minimum_valid_localities": spec.get("minimum", 1),
            "score_range": {"minimum": 0, "maximum": 10},
            "score_precision": spec.get("precision", 8),
            "tie_handling": spec.get("tie", "STABLE_ENTITY_ID"),
            "one_locality_treatment": spec.get("one", "USE_AVAILABLE"),
            "required_lineage_roles": ["PRIMARY_OBSERVATION", "ENTITY_UNIVERSE"],
        }
        aggregation_policies.append(policy)
        results = aggregate_locality_criterion(
            release_id="phase5d-synthetic-5.0",
            criterion=criteria_by_id[criterion_id],
            aggregation_policy=policy,
            locality_universe=locality_universe,
            geographic_entities=entities,
            observations=tuple(observations),
            scores=tuple(scores),
            source_lineage_ids=tuple(lineage_ids),
            attempted_at=ATTEMPTED_AT,
        )
        for result in results:
            outcomes.append(result.outcome)
            if result.observation:
                observations.append(result.observation)
                scores.append(result.score)
                evidence.append(result.evidence)

    for criterion in criteria:
        counts = Counter(
            row["outcome"] for row in outcomes if row["criterion_id"] == criterion["id"]
        )
        criterion["coverage"]["outcome_counts"] = {
            status: counts.get(status, 0)
            for status in ("valid", "missing", "stale", "invalid", "rejected")
        }
        criterion["coverage"]["valid_country_count"] = counts.get("valid", 0)
    catalog = {
        "schema_version": "consumer-catalog-3.0",
        "compatible_release_schema_major": 5,
        "target_api_contract_version": "konsider-api-2.0",
        "coverage_policy_version": "phase5d-coverage-policy-1.0",
        "stable_universe_id": "phase5d-country-universe",
        "geographic_entities": list(entities),
        "criteria": criteria,
        "locality_universes": ([locality_universe] if aggregation_policies else []),
        "aggregation_policies": aggregation_policies,
        "preference_presets": [
            {
                "id": "equal",
                "name": "Equal",
                "description": "Synthetic equal weights.",
                "weights": {spec["id"]: 1 for spec in specs},
            }
        ],
    }
    return CurrentReleaseArtifacts(
        geographic_entities=entities,
        observations=tuple(observations),
        scores=tuple(scores),
        criterion_outcomes=tuple(outcomes),
        derived_country_evidence=tuple(evidence),
        source_lineages=tuple(source_lineages),
        locality_universes=(locality_universe,) if aggregation_policies else (),
        aggregation_policies=tuple(aggregation_policies),
        criterion_policies=tuple(criterion_policies),
        consumer_catalog=catalog,
    )


def _load(tmp_path: Path, specs: list[dict], *, countries=("CAN", "MEX")):
    repository = CurrentReleaseRepository(tmp_path / "releases", tmp_path / "catalogs")
    draft = repository.write_draft(
        "phase5d-synthetic-5.0", _build_artifacts(specs, countries=countries)
    )
    return repository.load(draft)


def test_top_n_aggregation_handles_fewer_than_n_one_locality_and_precision() -> None:
    artifacts = _build_artifacts(
        [
            {
                "id": "L1",
                "locality": True,
                "n": 3,
                "precision": 2,
                "scores": {
                    "CAN": {"a": 8.005, "b": 7.004},
                    "MEX": {"a": 6.666},
                },
            }
        ]
    )
    evidence = {row["country"]["entity_id"]: row for row in artifacts.derived_country_evidence}
    assert evidence["country:CAN"]["result_score"] == 7.5
    assert "FEWER_THAN_N_AVAILABLE" in evidence["country:CAN"]["quality_flags"]
    assert evidence["country:MEX"]["result_score"] == 6.67
    assert "SINGLE_LOCALITY_RESULT" in evidence["country:MEX"]["quality_flags"]


@pytest.mark.parametrize(
    ("tie_handling", "expected_status", "expected_contributors"),
    [
        ("STABLE_ENTITY_ID", "valid", ("city:CAN:a", "city:CAN:b")),
        (
            "INCLUDE_ALL_AT_BOUNDARY",
            "valid",
            ("city:CAN:a", "city:CAN:b", "city:CAN:c"),
        ),
        ("FAIL_AMBIGUOUS", "rejected", ()),
    ],
)
def test_top_n_boundary_ties_are_policy_driven(
    tie_handling, expected_status, expected_contributors
) -> None:
    artifacts = _build_artifacts(
        [
            {
                "id": "L1",
                "locality": True,
                "n": 2,
                "tie": tie_handling,
                "scores": {
                    "CAN": {"a": 9, "b": 8, "c": 8},
                    "MEX": {"a": 7},
                },
            }
        ]
    )
    outcome = next(
        row for row in artifacts.criterion_outcomes if row["subject"]["entity_id"] == "country:CAN"
    )
    assert outcome["outcome"] == expected_status
    evidence = next(
        (
            row
            for row in artifacts.derived_country_evidence
            if row["country"]["entity_id"] == "country:CAN"
        ),
        None,
    )
    actual = (
        tuple(row["locality"]["entity_id"] for row in evidence["contributing_localities"])
        if evidence
        else ()
    )
    assert actual == expected_contributors


def test_stale_invalid_and_insufficient_inputs_emit_normalized_outcomes() -> None:
    artifacts = _build_artifacts(
        [
            {
                "id": "L1",
                "locality": True,
                "minimum": 2,
                "scores": {
                    "CAN": {"a": (8, ["STALE"]), "b": (7, ["STALE"])},
                    "MEX": {"a": (6, ["INVALID"]), "b": 5},
                },
            }
        ]
    )
    outcomes = {row["subject"]["entity_id"]: row for row in artifacts.criterion_outcomes}
    assert outcomes["country:CAN"]["outcome"] == "stale"
    assert outcomes["country:CAN"]["reason_codes"] == ["LOCALITY_INPUT_STALE"]
    assert outcomes["country:MEX"]["outcome"] == "missing"
    assert outcomes["country:MEX"]["reason_codes"] == ["INSUFFICIENT_VALID_LOCALITIES"]
    assert not any(
        row["subject"]["entity_id"] == "country:MEX"
        for row in artifacts.scores
        if row["subject"]["entity_type"] == "COUNTRY"
    )


def test_outside_universe_is_ignored_and_no_qualifying_locality_is_explicit() -> None:
    artifacts = _build_artifacts(
        [
            {
                "id": "L1",
                "locality": True,
                "scores": {
                    "CAN": {"a": 8, "outside": 10},
                    "MEX": {"a": 7},
                },
            }
        ]
    )
    universe = copy.deepcopy(artifacts.locality_universes[0])
    universe["entity_ids"] = [
        entity_id
        for entity_id in universe["entity_ids"]
        if entity_id != "city:CAN:outside" and not entity_id.startswith("city:MEX:")
    ]
    criterion = artifacts.consumer_catalog["criteria"][0]
    results = aggregate_locality_criterion(
        release_id="outside-universe",
        criterion=criterion,
        aggregation_policy=artifacts.aggregation_policies[0],
        locality_universe=universe,
        geographic_entities=artifacts.geographic_entities,
        observations=tuple(
            row for row in artifacts.observations if row["subject"]["entity_type"] == "CITY"
        ),
        scores=tuple(row for row in artifacts.scores if row["subject"]["entity_type"] == "CITY"),
        source_lineage_ids=("lineage:L1", "lineage:universe"),
        attempted_at=ATTEMPTED_AT,
    )
    by_country = {row.country_entity_id: row for row in results}

    assert by_country["country:CAN"].status == LocalityAggregationStatus.VALID
    assert "city:CAN:outside" in by_country["country:CAN"].ignored_locality_entity_ids
    assert "OUTSIDE_UNIVERSE_INPUT_IGNORED" in by_country["country:CAN"].quality_flags
    assert by_country["country:MEX"].status == LocalityAggregationStatus.MISSING
    assert by_country["country:MEX"].reason_codes == ("NO_QUALIFYING_LOCALITY",)


def test_one_locality_can_be_rejected_by_policy() -> None:
    artifacts = _build_artifacts(
        [
            {
                "id": "L1",
                "locality": True,
                "one": "INSUFFICIENT_EVIDENCE",
                "scores": {"CAN": {"a": 8}, "MEX": {"a": 7}},
            }
        ]
    )
    assert {
        (row["outcome"], tuple(row["reason_codes"])) for row in artifacts.criterion_outcomes
    } == {("missing", ("SINGLE_LOCALITY_INSUFFICIENT",))}


def test_national_only_and_locality_activation_thresholds(tmp_path: Path) -> None:
    national = _load(
        tmp_path / "national",
        [{"id": "N1", "scores": {"CAN": 8, "MEX": 7}}],
    )
    result = rank_schema5_release(national, {"N1": 1})
    assert result.locality_assessment.status == LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA

    locality = _load(
        tmp_path / "locality",
        [
            {"id": "N1", "scores": {"CAN": 8, "MEX": 7}},
            {
                "id": "L1",
                "locality": True,
                "scores": {"CAN": {"a": 9}, "MEX": {"a": 6}},
            },
        ],
    )
    low = rank_schema5_release(locality, {"N1": 1, "L1": 0.5})
    medium = rank_schema5_release(locality, {"N1": 1, "L1": 0.6})
    assert low.locality_assessment.status == LocalityStatus.BELOW_ANALYSIS_THRESHOLD
    assert low.locality_assessment.below_threshold_criterion_ids == ("L1",)
    assert all(any(item.criterion_id == "L1" for item in row.contributions) for row in low.rankings)
    assert medium.locality_assessment.status == LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION


@pytest.mark.parametrize(
    ("weight", "expected_status", "contributes"),
    [
        (0.0, LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA, False),
        (0.2, LocalityStatus.BELOW_ANALYSIS_THRESHOLD, True),
        (0.4, LocalityStatus.BELOW_ANALYSIS_THRESHOLD, True),
        (0.6, LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION, True),
        (0.8, LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION, True),
        (1.0, LocalityStatus.ONE_ACTIVE_LOCALITY_CRITERION, True),
    ],
)
def test_all_six_weight_levels_preserve_provenance_and_medium_boundary(
    tmp_path: Path,
    weight: float,
    expected_status: LocalityStatus,
    contributes: bool,
) -> None:
    release = _load(
        tmp_path,
        [
            {"id": "N1", "scores": {"CAN": 8, "MEX": 7}},
            {
                "id": "L1",
                "locality": True,
                "scores": {"CAN": {"a": 9}, "MEX": {"a": 6}},
            },
        ],
    )

    result = rank_schema5_release(release, {"N1": 1, "L1": weight})

    assert result.locality_assessment.status == expected_status
    assert all(
        any(item.criterion_id == "L1" for item in row.contributions) is contributes
        for row in result.rankings
    )
    if weight in {0.2, 0.4}:
        assert result.locality_assessment.below_threshold_criterion_ids == ("L1",)
        assert all(
            next(
                item for item in row.contributions if item.criterion_id == "L1"
            ).derived_evidence_id
            is not None
            for row in result.rankings
        )


def test_pcc_coverage_activation_is_independent_of_locality_threshold(tmp_path: Path) -> None:
    release = _load(
        tmp_path,
        [
            {"id": "N1", "scores": {"CAN": 8, "MEX": 7}},
            {
                "id": "LP",
                "locality": True,
                "coverage": "CONDITIONAL_COMPLETE_CASE",
                "activation": 0.6,
                "threshold": 0.4,
                "scores": {"CAN": {"a": 9}},
            },
        ],
    )
    below_coverage = rank_schema5_release(release, {"N1": 1, "LP": 0.5})
    active = rank_schema5_release(release, {"N1": 1, "LP": 0.6})

    assert below_coverage.coverage_assessment.status == CoverageStatus.NO_PARTIAL_CRITERIA_ACTIVE
    assert below_coverage.locality_assessment.status == LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA
    assert active.coverage_assessment.status == CoverageStatus.PARTIAL_COMPLETE_CASE
    assert active.coverage_assessment.excluded_country_entity_ids == ("country:MEX",)
    assert active.locality_assessment.analysis_triggered_criterion_ids == ("LP",)
    assert {row.country["entity_id"] for row in active.rankings} == {"country:CAN"}


def test_common_locality_uses_full_valid_sets_not_top_n(tmp_path: Path) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "L1",
                "locality": True,
                "n": 1,
                "scores": {
                    "CAN": {"a": 10, "c": 7},
                    "MEX": {"a": 8, "c": 6},
                },
            },
            {
                "id": "L2",
                "locality": True,
                "n": 1,
                "scores": {
                    "CAN": {"b": 9, "c": 8},
                    "MEX": {"b": 7, "c": 5},
                },
            },
        ],
    )
    result = rank_schema5_release(release, {"L1": 1, "L2": 1})
    canada = result.country_locality_assessments["country:CAN"]

    assert canada.status == LocalityStatus.COMMON_LOCALITY_AVAILABLE
    assert canada.common_locality_entity_ids == ("city:CAN:c",)
    assert canada.best_common_locality_entity_id == "city:CAN:c"
    assert "city:CAN:c" not in canada.contributing_locality_entity_ids


def test_two_active_criteria_with_same_leading_locality(tmp_path: Path) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "L1",
                "locality": True,
                "n": 1,
                "scores": {"CAN": {"a": 9, "b": 7}, "MEX": {"a": 8}},
            },
            {
                "id": "L2",
                "locality": True,
                "n": 1,
                "scores": {"CAN": {"a": 8, "c": 7}, "MEX": {"a": 7}},
            },
        ],
    )
    result = rank_schema5_release(release, {"L1": 1, "L2": 1})
    canada = result.country_locality_assessments["country:CAN"]

    assert canada.status == LocalityStatus.COMMON_LOCALITY_AVAILABLE
    assert canada.best_common_locality_entity_id == "city:CAN:a"
    assert canada.contributing_locality_entity_ids == ("city:CAN:a",)


def test_no_overlap_is_advisory_and_does_not_change_country_total(tmp_path: Path) -> None:
    common_specs = [
        {
            "id": "L1",
            "locality": True,
            "n": 1,
            "scores": {"CAN": {"a": 9, "c": 7}, "MEX": {"a": 7, "c": 5}},
        },
        {
            "id": "L2",
            "locality": True,
            "n": 1,
            "scores": {"CAN": {"b": 8, "c": 6}, "MEX": {"b": 6, "c": 4}},
        },
    ]
    no_overlap_specs = copy.deepcopy(common_specs)
    no_overlap_specs[0]["scores"]["CAN"].pop("c")
    no_overlap_specs[1]["scores"]["CAN"].pop("c")
    common = rank_schema5_release(_load(tmp_path / "common", common_specs), {"L1": 1, "L2": 1})
    separate = rank_schema5_release(
        _load(tmp_path / "separate", no_overlap_specs), {"L1": 1, "L2": 1}
    )
    common_canada = next(
        row for row in common.rankings if row.country["entity_id"] == "country:CAN"
    )
    separate_canada = next(
        row for row in separate.rankings if row.country["entity_id"] == "country:CAN"
    )

    assert common_canada.locality_assessment.status == LocalityStatus.COMMON_LOCALITY_AVAILABLE
    assert separate_canada.locality_assessment.status == LocalityStatus.NO_COMMON_LOCALITY
    assert common_canada.total_score == separate_canada.total_score == 8.5


def test_two_active_criteria_can_produce_mixed_country_overlap_results(
    tmp_path: Path,
) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "L1",
                "locality": True,
                "scores": {
                    "CAN": {"a": 9, "c": 7},
                    "MEX": {"a": 8},
                },
            },
            {
                "id": "L2",
                "locality": True,
                "scores": {
                    "CAN": {"b": 8, "c": 6},
                    "MEX": {"b": 7},
                },
            },
        ],
    )
    result = rank_schema5_release(release, {"L1": 1, "L2": 1})

    assert (
        result.country_locality_assessments["country:CAN"].status
        == LocalityStatus.COMMON_LOCALITY_AVAILABLE
    )
    assert (
        result.country_locality_assessments["country:MEX"].status
        == LocalityStatus.NO_COMMON_LOCALITY
    )
    assert result.locality_assessment.status == LocalityStatus.MIXED_COUNTRY_RESULTS


def test_three_criteria_common_and_pairwise_only_overlap(tmp_path: Path) -> None:
    common_release = _load(
        tmp_path / "common",
        [
            {
                "id": criterion_id,
                "locality": True,
                "scores": {
                    "CAN": {leading: 9, "c": common_score},
                    "MEX": {"a": 6},
                },
            }
            for criterion_id, leading, common_score in (
                ("L1", "a", 6),
                ("L2", "b", 7),
                ("L3", "d", 8),
            )
        ],
    )
    common = rank_schema5_release(common_release, {"L1": 1, "L2": 2, "L3": 3})
    assert (
        common.country_locality_assessments["country:CAN"].best_common_locality_entity_id
        == "city:CAN:c"
    )

    pairwise_release = _load(
        tmp_path / "pairwise",
        [
            {
                "id": "L1",
                "locality": True,
                "scores": {"CAN": {"a": 9, "b": 8}, "MEX": {"a": 6}},
            },
            {
                "id": "L2",
                "locality": True,
                "scores": {"CAN": {"b": 9, "c": 8}, "MEX": {"b": 6}},
            },
            {
                "id": "L3",
                "locality": True,
                "scores": {"CAN": {"c": 9, "a": 8}, "MEX": {"c": 6}},
            },
        ],
    )
    pairwise = rank_schema5_release(pairwise_release, {"L1": 1, "L2": 1, "L3": 1})
    assert (
        pairwise.country_locality_assessments["country:CAN"].status
        == LocalityStatus.PARTIAL_OVERLAP
    )
    assert pairwise.country_locality_assessments["country:CAN"].common_locality_entity_ids == ()


def test_best_common_locality_uses_relevant_weights_and_stable_ties(
    tmp_path: Path,
) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "L1",
                "locality": True,
                "method": "ALL_VALID_MEAN",
                "scores": {
                    "CAN": {"a": 10, "b": 6},
                    "MEX": {"a": 7, "b": 7},
                },
            },
            {
                "id": "L2",
                "locality": True,
                "method": "ALL_VALID_MEAN",
                "scores": {
                    "CAN": {"a": 4, "b": 9},
                    "MEX": {"a": 7, "b": 7},
                },
            },
        ],
    )
    l1_heavy = rank_schema5_release(release, {"L1": 3, "L2": 1})
    l2_heavy = rank_schema5_release(release, {"L1": 1, "L2": 3})

    assert (
        l1_heavy.country_locality_assessments["country:CAN"].best_common_locality_entity_id
        == "city:CAN:a"
    )
    assert (
        l2_heavy.country_locality_assessments["country:CAN"].best_common_locality_entity_id
        == "city:CAN:b"
    )
    assert (
        l1_heavy.country_locality_assessments["country:MEX"].best_common_locality_entity_id
        == "city:MEX:a"
    )
    assert all(
        {item.criterion_id: item.normalized_weight for item in row.contributions}
        == l1_heavy.normalized_weights
        for row in l1_heavy.rankings
    )
    top_one = rank_schema5_release(release, {"L1": 3, "L2": 1}, top_k=1)
    assert top_one.to_dict()["assessments"]["locality"]["excluded_country_assessments"] == []


def test_coverage_exclusion_retains_independent_locality_warning(tmp_path: Path) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "L1",
                "locality": True,
                "coverage": "CONDITIONAL_COMPLETE_CASE",
                "minimum_valid_country_count": 1,
                "scores": {"CAN": {"a": 8}, "MEX": {"a": 7}},
            },
            {
                "id": "L2",
                "locality": True,
                "scores": {"CAN": {"b": 9}},
            },
        ],
    )
    result = rank_schema5_release(release, {"L1": 1, "L2": 1})

    assert result.coverage_assessment.excluded_country_entity_ids == ("country:MEX",)
    assert (
        result.country_locality_assessments["country:CAN"].status
        == LocalityStatus.NO_COMMON_LOCALITY
    )
    assert (
        result.country_locality_assessments["country:MEX"].status
        == LocalityStatus.INSUFFICIENT_LOCALITY_EVIDENCE
    )
    assert "country:MEX" not in {row.country["entity_id"] for row in result.rankings}


def test_coverage_limit_fallback_deactivates_pcc_locality_analysis(tmp_path: Path) -> None:
    release = _load(
        tmp_path,
        [
            {
                "id": "N1",
                "scores": {"CAN": 8, "MEX": 7, "USA": 6},
            },
            {
                "id": "LP",
                "locality": True,
                "coverage": "CONDITIONAL_COMPLETE_CASE",
                "minimum_valid_country_count": 2,
                "scores": {"CAN": {"a": 9}},
            },
        ],
        countries=("CAN", "MEX", "USA"),
    )
    result = rank_schema5_release(release, {"N1": 1, "LP": 1})

    assert result.coverage_assessment.status == CoverageStatus.COVERAGE_LIMIT_FALLBACK
    assert result.coverage_assessment.active_conditional_criterion_ids == ()
    assert result.locality_assessment.status == LocalityStatus.NO_ACTIVE_LOCALITY_CRITERIA
    assert len(result.rankings) == 3
    assert all(
        [item.criterion_id for item in row.contributions] == ["N1"] for row in result.rankings
    )


def test_one_normalized_vector_no_partial_aggregate_and_deterministic_contract(
    tmp_path: Path,
) -> None:
    release = _load(
        tmp_path,
        [
            {"id": "N1", "scores": {"CAN": 8, "MEX": 7}},
            {
                "id": "LP",
                "locality": True,
                "coverage": "CONDITIONAL_COMPLETE_CASE",
                "minimum_valid_country_count": 1,
                "scores": {"CAN": {"a": 9}},
            },
        ],
    )
    first = rank_schema5_release(release, {"N1": 2, "LP": 1})
    second = rank_schema5_release(release, {"N1": 2, "LP": 1})

    assert first.to_dict() == second.to_dict()
    assert first.normalized_weights == {"LP": pytest.approx(1 / 3), "N1": pytest.approx(2 / 3)}
    assert {row.country["entity_id"] for row in first.rankings} == {"country:CAN"}
    for row in first.rankings:
        assert sorted(item.normalized_weight for item in row.contributions) == pytest.approx(
            [1 / 3, 2 / 3]
        )
        assert row.profile_assessment.status.value == "NO_PROFILE_CONTEXT"
        for contribution in row.contributions:
            outcome = next(
                item
                for item in release.artifacts.criterion_outcomes
                if item["criterion_id"] == contribution.criterion_id
                and item["subject"] == row.country
            )
            assert contribution.observation_id == outcome["observation_id"]
            assert contribution.score_id == outcome["score_id"]
            if contribution.evidence_kind == "DERIVED_LOCALITIES":
                assert contribution.derived_evidence_id in {
                    item["evidence_id"] for item in release.artifacts.derived_country_evidence
                }
    validate_contract(
        first.to_dict(),
        "ranking-response",
        context="Phase 5D ranking result",
        schema_generation=3,
    )


@pytest.mark.parametrize(
    "profile_field",
    (
        "occupation",
        "spouse",
        "visa",
        "age",
        "citizenship",
        "licensing",
        "co_location_requirement",
    ),
)
def test_phase5d_request_rejects_future_profile_fields(profile_field: str) -> None:
    request = {
        "api_contract_version": "konsider-api-2.0",
        "weights": {"L1": 1},
        profile_field: "not-supported-in-phase5d",
    }
    with pytest.raises(ContractError):
        validate_contract(
            request,
            "ranking-request",
            context=f"Phase 5D {profile_field}",
            schema_generation=3,
        )
