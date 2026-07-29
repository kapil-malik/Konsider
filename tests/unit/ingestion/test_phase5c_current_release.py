import copy
from dataclasses import replace
from pathlib import Path

import pytest

from konsider.ingestion.current_release import (
    CriterionBuildResult,
    CurrentReleaseArtifacts,
    CurrentReleaseError,
    CurrentReleaseRepository,
    GenericReleaseWorker,
    SourceBytesUnavailable,
    validate_current_artifacts,
)

RELEASE_ID = "phase5c-synthetic-5.0"
ATTEMPTED_AT = "2026-07-28T00:00:00Z"
COUNTRIES = (("CAN", "Canada"), ("MEX", "Mexico"))
LOCALITIES = (
    ("city:toronto", "Toronto", "CAN"),
    ("city:mexico-city", "Mexico City", "MEX"),
)


def _mapping(source_id: str, source_entity_id: str) -> dict:
    return {
        "source_id": source_id,
        "source_version": "2026",
        "source_entity_id": source_entity_id,
    }


def _entities() -> tuple[dict, ...]:
    return tuple(
        {
            "entity_id": f"country:{code}",
            "entity_type": "COUNTRY",
            "display_name": name,
            "country_codes": [code],
            "aliases": [],
            "source_mappings": [_mapping("synthetic-countries", code)],
        }
        for code, name in COUNTRIES
    ) + tuple(
        {
            "entity_id": entity_id,
            "entity_type": "CITY",
            "display_name": name,
            "country_codes": [country],
            "aliases": [],
            "source_mappings": [_mapping("synthetic-cities", entity_id)],
        }
        for entity_id, name, country in LOCALITIES
    )


def _lineage(lineage_id: str, roles: tuple[str, ...]) -> dict:
    return {
        "lineage_id": lineage_id,
        "lineage_version": "1.0",
        "sources": [
            {
                "source_id": f"{lineage_id}:{index}",
                "role": role,
                "source_version": "2026",
                "asset_uri": f"local://phase5c/{lineage_id}/{index}.json",
                "checksum": f"sha256:{str(index + 1) * 64}",
                "licence_id": "SYNTHETIC-TEST-ONLY",
            }
            for index, role in enumerate(roles)
        ],
        "transforms": [
            {
                "step_id": f"{lineage_id}:parse",
                "transform_version": "1.0",
                "input_refs": [f"{lineage_id}:0"],
                "output_ref": f"{lineage_id}:observations",
            }
        ],
    }


def _scope(locality: bool, policy_id: str | None = None) -> dict:
    return {
        "evidence_level": "LOCALITY" if locality else "COUNTRY",
        "result_level": "COUNTRY",
        "locality_type": "CITY" if locality else None,
        "derivation": "AGGREGATED_FROM_LOCALITIES" if locality else "DIRECT",
        "locality_universe_id": "phase5c-cities-v1" if locality else None,
        "aggregation_policy_id": policy_id if locality else None,
        "locality_analysis_threshold": 0.6 if locality else None,
    }


def _coverage(mode: str, lineage_ids: list[str]) -> dict:
    return {
        "mode": mode,
        "stable_universe_id": "phase5c-country-universe",
        "stable_country_count": 2,
        "valid_country_count": 2,
        "minimum_valid_country_count": 2 if mode == "GLOBAL_CORE" else 1,
        "outcome_counts": {
            "valid": 2,
            "missing": 0,
            "stale": 0,
            "invalid": 0,
            "rejected": 0,
        },
        "activation_threshold": 0.5 if mode == "CONDITIONAL_COMPLETE_CASE" else None,
        "score_range": {"minimum": 0, "maximum": 10},
        "source_lineage_ids": lineage_ids,
    }


def _fixture_inputs():
    specs = (
        ("C-N-FCC", "GLOBAL_CORE", False),
        ("C-N-PCC", "CONDITIONAL_COMPLETE_CASE", False),
        ("C-L-FCC", "GLOBAL_CORE", True),
        ("C-L-PCC", "CONDITIONAL_COMPLETE_CASE", True),
    )
    source_lineages = [
        _lineage("lineage:universe", ("ENTITY_UNIVERSE",)),
        _lineage("lineage:C-N-FCC", ("PRIMARY_OBSERVATION", "AUXILIARY")),
        _lineage("lineage:C-N-PCC", ("PRIMARY_OBSERVATION",)),
        _lineage("lineage:C-L-FCC", ("PRIMARY_OBSERVATION",)),
        _lineage("lineage:C-L-PCC", ("PRIMARY_OBSERVATION",)),
    ]
    criteria, criterion_policies, aggregation_policies = [], [], []
    for criterion_id, mode, locality in specs:
        primary_lineage = f"lineage:{criterion_id}"
        lineage_ids = [primary_lineage, "lineage:universe"] if locality else [primary_lineage]
        aggregation_id = f"aggregate:{criterion_id}" if locality else None
        scope = _scope(locality, aggregation_id)
        criteria.append(
            {
                "id": criterion_id,
                "display_name": criterion_id,
                "historical_names": [],
                "category": "Synthetic",
                "description": "Synthetic Phase 5C release-path criterion.",
                "direction": "higher_is_better",
                "raw_unit": "index",
                "interpretation": "Test-only deterministic index.",
                "caveats": ["Not product data."],
                "quality_limitations": [],
                "ready": True,
                "default_enabled": True,
                "experimental": locality,
                "scoring_method_version": f"score:{criterion_id}:1.0",
                "coverage": _coverage(mode, lineage_ids),
                "scope": scope,
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
            }
        )
        criterion_policies.append(
            {
                "criterion_id": criterion_id,
                "source_lineage_ids": lineage_ids,
                "parser": {
                    "id": "synthetic-locality" if locality else "synthetic-national",
                    "version": "1.0",
                },
                "scoring": {"id": "linear-test-score", "version": f"score:{criterion_id}:1.0"},
                "coverage_mode": mode,
                "scope": scope,
                "derivation": {
                    "mode": scope["derivation"],
                    "processor": ({"id": "synthetic-mean", "version": "1.0"} if locality else None),
                },
                "applicability": {"mode": "UNIVERSAL", "dimensions": []},
                "ready": True,
                "experimental": locality,
            }
        )
        if locality:
            aggregation_policies.append(
                {
                    "policy_id": aggregation_id,
                    "policy_version": "1.0",
                    "eligible_locality_universe": {
                        "locality_universe_id": "phase5c-cities-v1",
                        "locality_universe_version": "1.0",
                    },
                    "source_criterion_id": criterion_id,
                    "result_criterion_id": criterion_id,
                    "locality_type": "CITY",
                    "result_level": "COUNTRY",
                    "selection": {"method": "ALL_VALID_MEAN", "n": None},
                    "minimum_valid_localities": 1,
                    "score_range": {"minimum": 0, "maximum": 10},
                    "score_precision": 8,
                    "tie_handling": "STABLE_ENTITY_ID",
                    "one_locality_treatment": "USE_AVAILABLE",
                    "required_lineage_roles": ["PRIMARY_OBSERVATION", "ENTITY_UNIVERSE"],
                }
            )
    entities = _entities()
    locality_universe = {
        "locality_universe_id": "phase5c-cities-v1",
        "locality_universe_version": "1.0",
        "locality_type": "CITY",
        "source_lineage_id": "lineage:universe",
        "selection": {
            "method": "BOUNDED_POPULATION",
            "minimum_population": 50000,
            "maximum_per_country": 1,
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
        "entity_ids": [row[0] for row in LOCALITIES],
    }
    catalog = {
        "schema_version": "consumer-catalog-3.0",
        "compatible_release_schema_major": 5,
        "target_api_contract_version": "konsider-api-2.0",
        "coverage_policy_version": "phase5c-test-1.0",
        "stable_universe_id": "phase5c-country-universe",
        "geographic_entities": list(entities),
        "criteria": criteria,
        "locality_universes": [locality_universe],
        "aggregation_policies": aggregation_policies,
        "preference_presets": [
            {
                "id": "balanced",
                "name": "Balanced",
                "description": "Synthetic equal weights.",
                "weights": {criterion["id"]: 1 for criterion in criteria},
            }
        ],
    }
    return {
        "catalog": catalog,
        "entities": entities,
        "source_lineages": tuple(source_lineages),
        "locality_universes": (locality_universe,),
        "aggregation_policies": tuple(aggregation_policies),
        "criterion_policies": tuple(criterion_policies),
    }


def _observation(criterion_id: str, entity_id: str, entity_type: str, value: float) -> dict:
    return {
        "observation_id": f"obs:{criterion_id}:{entity_id}",
        "criterion_id": criterion_id,
        "subject": {"entity_id": entity_id, "entity_type": entity_type},
        "value": value,
        "unit": "index",
        "reference_period": {"start": "2025-01-01", "end": "2025-12-31"},
        "source_lineage_id": f"lineage:{criterion_id}",
        "quality_flags": [],
    }


def _score(criterion_id: str, entity_id: str, entity_type: str, value: float) -> dict:
    return {
        "score_id": f"score:{criterion_id}:{entity_id}",
        "criterion_id": criterion_id,
        "subject": {"entity_id": entity_id, "entity_type": entity_type},
        "score": value,
        "observation_ids": [f"obs:{criterion_id}:{entity_id}"],
        "scoring_method_version": f"score:{criterion_id}:1.0",
        "source_lineage_id": f"lineage:{criterion_id}",
        "quality_flags": [],
    }


def _national_processor(policy, _criterion_lineages, _all_lineages):
    criterion_id = policy["criterion_id"]
    result = CriterionBuildResult()
    for index, (code, _) in enumerate(COUNTRIES):
        entity_id = f"country:{code}"
        value = 6.0 + index
        result.observations.append(_observation(criterion_id, entity_id, "COUNTRY", value))
        result.scores.append(_score(criterion_id, entity_id, "COUNTRY", value))
    return result


def _locality_processor(policy, _criterion_lineages, _all_lineages):
    criterion_id = policy["criterion_id"]
    result = CriterionBuildResult()
    for index, (locality_id, _, country) in enumerate(LOCALITIES):
        value = 7.0 + index
        locality_observation = _observation(criterion_id, locality_id, "CITY", value)
        locality_score = _score(criterion_id, locality_id, "CITY", value)
        country_id = f"country:{country}"
        country_observation = _observation(criterion_id, country_id, "COUNTRY", value)
        country_score = _score(criterion_id, country_id, "COUNTRY", value)
        result.observations.extend((locality_observation, country_observation))
        result.scores.extend((locality_score, country_score))
        result.derived_country_evidence.append(
            {
                "evidence_id": f"derived:{criterion_id}:{country_id}",
                "result_criterion_id": criterion_id,
                "country": {"entity_id": country_id, "entity_type": "COUNTRY"},
                "derivation_method": "AGGREGATED_FROM_LOCALITIES",
                "aggregation_policy": {
                    "policy_id": f"aggregate:{criterion_id}",
                    "policy_version": "1.0",
                },
                "input_release_id": RELEASE_ID,
                "result_observation_id": country_observation["observation_id"],
                "result_score_id": country_score["score_id"],
                "contributing_localities": [
                    {
                        "locality": {"entity_id": locality_id, "entity_type": "CITY"},
                        "observation_ids": [locality_observation["observation_id"]],
                        "score_id": locality_score["score_id"],
                        "score": value,
                    }
                ],
                "eligible_locality_count": 1,
                "valid_locality_count": 1,
                "result_score": value,
                "criterion_source_lineage_id": f"lineage:{criterion_id}",
                "quality_flags": ["SINGLE_LOCALITY_RESULT"],
            }
        )
    return result


PROCESSORS = {
    ("synthetic-national", "1.0"): _national_processor,
    ("synthetic-locality", "1.0"): _locality_processor,
}


def _artifacts() -> CurrentReleaseArtifacts:
    return GenericReleaseWorker(PROCESSORS).build(
        release_id=RELEASE_ID,
        attempted_at=ATTEMPTED_AT,
        **_fixture_inputs(),
    )


def _mutate(artifacts: CurrentReleaseArtifacts, field: str, mutator) -> CurrentReleaseArtifacts:
    rows = list(copy.deepcopy(getattr(artifacts, field)))
    mutator(rows)
    return replace(artifacts, **{field: tuple(rows)})


def _issue_codes(artifacts: CurrentReleaseArtifacts) -> set[str]:
    return {issue["code"] for issue in validate_current_artifacts(artifacts)["issues"]}


def test_schema5_generic_worker_covers_national_and_locality_fcc_and_pcc() -> None:
    artifacts = _artifacts()
    report = validate_current_artifacts(artifacts)

    assert report["structural_passed"] is True
    assert len(artifacts.criterion_outcomes) == 8
    assert {row["subject"]["entity_type"] for row in artifacts.criterion_outcomes} == {"COUNTRY"}
    combinations = {
        (row["coverage_mode"], row["scope"]["evidence_level"])
        for row in artifacts.criterion_policies
    }
    assert combinations == {
        ("GLOBAL_CORE", "COUNTRY"),
        ("CONDITIONAL_COMPLETE_CASE", "COUNTRY"),
        ("GLOBAL_CORE", "LOCALITY"),
        ("CONDITIONAL_COMPLETE_CASE", "LOCALITY"),
    }


def test_generic_worker_preserves_processor_owned_non_valid_outcomes() -> None:
    inputs = _fixture_inputs()
    original = PROCESSORS[("synthetic-national", "1.0")]

    def processor_with_stale_country(policy, criterion_lineages, all_lineages):
        result = original(policy, criterion_lineages, all_lineages)
        country_id = "country:MEX"
        result.observations = [
            row for row in result.observations if row["subject"]["entity_id"] != country_id
        ]
        result.scores = [row for row in result.scores if row["subject"]["entity_id"] != country_id]
        result.criterion_outcomes.append(
            {
                "criterion_id": policy["criterion_id"],
                "subject": {"entity_id": country_id, "entity_type": "COUNTRY"},
                "outcome": "stale",
                "evidence_kind": "NONE",
                "attempted_at": ATTEMPTED_AT,
                "observation_id": None,
                "score_id": None,
                "derived_evidence_id": None,
                "source_lineage_ids": sorted(policy["source_lineage_ids"]),
                "reason_codes": ["SOURCE_STALE"],
                "quality_flags": ["SOURCE_STALE"],
            }
        )
        return result

    processors = {**PROCESSORS, ("synthetic-national", "1.0"): processor_with_stale_country}
    artifacts = GenericReleaseWorker(processors).build(
        release_id=RELEASE_ID,
        attempted_at=ATTEMPTED_AT,
        **inputs,
    )
    stale = [
        row
        for row in artifacts.criterion_outcomes
        if row["criterion_id"] in {"C-N-FCC", "C-N-PCC"}
        and row["subject"]["entity_id"] == "country:MEX"
    ]
    assert len(stale) == 2
    assert {row["outcome"] for row in stale} == {"stale"}
    multi = next(row for row in artifacts.source_lineages if row["lineage_id"] == "lineage:C-N-FCC")
    assert len(multi["sources"]) == 2


def test_schema5_release_is_deterministic_loadable_and_replayable(tmp_path: Path) -> None:
    repository = CurrentReleaseRepository(tmp_path / "releases", tmp_path / "catalog-snapshots")
    draft = repository.write_draft(RELEASE_ID, _artifacts())
    first_bytes = {path.name: path.read_bytes() for path in draft.iterdir() if path.is_file()}
    assert sum(len(value) for value in first_bytes.values()) < 256 * 1024

    replay = repository.replay(draft, processors=PROCESSORS)
    assert replay.passed
    assert replay.mismatched_files == ()

    published = repository.publish(RELEASE_ID, require_product_ready=True, activate=False)
    loaded = repository.load(published)
    assert loaded.validation["structural_passed"] is True
    assert (tmp_path / "catalog-snapshots" / f"{RELEASE_ID}.json").exists()
    assert not (tmp_path / "releases" / "active.json").exists()
    assert first_bytes["observations.jsonl"] == (published / "observations.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        repository.write_draft(RELEASE_ID, _artifacts())


def test_schema5_serialization_is_independent_of_registry_row_order(tmp_path: Path) -> None:
    original = _artifacts()
    catalog = copy.deepcopy(original.consumer_catalog)
    for field in (
        "geographic_entities",
        "criteria",
        "locality_universes",
        "aggregation_policies",
        "preference_presets",
    ):
        catalog[field].reverse()
    reversed_artifacts = replace(
        original,
        geographic_entities=tuple(reversed(original.geographic_entities)),
        observations=tuple(reversed(original.observations)),
        scores=tuple(reversed(original.scores)),
        criterion_outcomes=tuple(reversed(original.criterion_outcomes)),
        derived_country_evidence=tuple(reversed(original.derived_country_evidence)),
        source_lineages=tuple(reversed(original.source_lineages)),
        locality_universes=tuple(reversed(original.locality_universes)),
        aggregation_policies=tuple(reversed(original.aggregation_policies)),
        criterion_policies=tuple(reversed(original.criterion_policies)),
        consumer_catalog=catalog,
    )
    first = CurrentReleaseRepository(tmp_path / "first", tmp_path / "catalog-a").write_draft(
        RELEASE_ID, original
    )
    second = CurrentReleaseRepository(tmp_path / "second", tmp_path / "catalog-b").write_draft(
        RELEASE_ID, reversed_artifacts
    )

    assert {path.name: path.read_bytes() for path in first.iterdir() if path.is_file()} == {
        path.name: path.read_bytes() for path in second.iterdir() if path.is_file()
    }


def test_invalid_parentage_is_rejected() -> None:
    invalid = _mutate(
        _artifacts(),
        "geographic_entities",
        lambda rows: rows[-1].update(country_codes=["ZZZ"]),
    )
    assert "BROKEN_LOCALITY_PARENTAGE" in _issue_codes(invalid)


def test_undeclared_locality_is_rejected() -> None:
    invalid = _mutate(
        _artifacts(),
        "locality_universes",
        lambda rows: rows[0]["entity_ids"].append("city:not-declared"),
    )
    assert "UNDECLARED_LOCALITY" in _issue_codes(invalid)


def test_broken_aggregation_lineage_is_rejected() -> None:
    invalid = _mutate(
        _artifacts(),
        "derived_country_evidence",
        lambda rows: rows[0]["aggregation_policy"].update(policy_version="9.9"),
    )
    assert "BROKEN_AGGREGATION_LINEAGE" in _issue_codes(invalid)


def test_contradictory_scope_and_coverage_policy_is_rejected() -> None:
    invalid = _mutate(
        _artifacts(),
        "criterion_policies",
        lambda rows: rows[0].update(coverage_mode="DIAGNOSTIC_ONLY"),
    )
    assert "CONTRADICTORY_CRITERION_POLICY" in _issue_codes(invalid)


def test_multiple_source_lineage_mismatch_is_rejected() -> None:
    invalid = _mutate(
        _artifacts(),
        "criterion_outcomes",
        lambda rows: rows[4].update(source_lineage_ids=["lineage:C-L-FCC"]),
    )
    assert "MULTIPLE_SOURCE_LINEAGE_MISMATCH" in _issue_codes(invalid)


def test_clean_checkout_reports_intentionally_local_source_bytes(tmp_path: Path) -> None:
    repository = CurrentReleaseRepository(tmp_path / "releases", tmp_path / "catalogs")
    draft = repository.write_draft(RELEASE_ID, _artifacts())

    def unavailable(*_args):
        raise SourceBytesUnavailable("Licensed fixture bytes are intentionally excluded from git.")

    processors = dict(PROCESSORS)
    processors[("synthetic-national", "1.0")] = unavailable
    result = repository.replay(draft, processors=processors)

    assert result.status == "SOURCE_BYTES_UNAVAILABLE"
    assert "excluded from git" in result.detail


def test_structurally_invalid_release_cannot_publish(tmp_path: Path) -> None:
    invalid = _mutate(
        _artifacts(),
        "criterion_outcomes",
        lambda rows: rows.pop(),
    )
    repository = CurrentReleaseRepository(tmp_path / "releases", tmp_path / "catalogs")
    repository.write_draft("invalid", invalid)
    with pytest.raises(CurrentReleaseError):
        repository.publish("invalid", require_product_ready=False)
