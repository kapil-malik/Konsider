"""Generic schema-5 ingestion, validation, immutable release, and replay support.

Historical schema-3/4 code deliberately remains in ``worker.py`` and
``release_repository.py``.  This module is the schema-current path and operates
on entity-neutral dictionaries validated by contracts/schemas/v3.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from konsider.contracts import ContractError, validate_contract
from konsider.text_io import write_text_lf

RELEASE_SCHEMA_VERSION = "konsider-release-5.0"
VALIDATION_SCHEMA_VERSION = "validation-5.0"
PAYLOAD_FILES = (
    "geographic-entities.jsonl",
    "observations.jsonl",
    "scores.jsonl",
    "criterion-outcomes.jsonl",
    "derived-country-evidence.jsonl",
    "source-lineages.json",
    "locality-universes.json",
    "aggregation-policies.json",
    "criterion-policies.json",
    "consumer-catalog.json",
    "validation.json",
)


class CurrentReleaseError(ValueError):
    """Raised when a schema-current release cannot be built or consumed."""


class SourceBytesUnavailable(CurrentReleaseError):
    """Raised when replay needs intentionally local source bytes that are absent."""


@dataclass(frozen=True)
class CurrentReleaseArtifacts:
    geographic_entities: tuple[dict[str, Any], ...]
    observations: tuple[dict[str, Any], ...]
    scores: tuple[dict[str, Any], ...]
    criterion_outcomes: tuple[dict[str, Any], ...]
    derived_country_evidence: tuple[dict[str, Any], ...]
    source_lineages: tuple[dict[str, Any], ...]
    locality_universes: tuple[dict[str, Any], ...]
    aggregation_policies: tuple[dict[str, Any], ...]
    criterion_policies: tuple[dict[str, Any], ...]
    consumer_catalog: dict[str, Any]


@dataclass
class CriterionBuildResult:
    observations: list[dict[str, Any]] = field(default_factory=list)
    scores: list[dict[str, Any]] = field(default_factory=list)
    derived_country_evidence: list[dict[str, Any]] = field(default_factory=list)
    criterion_outcomes: list[dict[str, Any]] = field(default_factory=list)
    rejected_countries: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadedCurrentRelease:
    path: Path
    manifest: dict[str, Any]
    validation: dict[str, Any]
    artifacts: CurrentReleaseArtifacts


@dataclass(frozen=True)
class ReplayResult:
    status: str
    compared_files: tuple[str, ...] = ()
    mismatched_files: tuple[str, ...] = ()
    detail: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == "PASSED"


CriterionProcessor = Callable[
    [dict[str, Any], tuple[dict[str, Any], ...], Mapping[str, dict[str, Any]]],
    CriterionBuildResult,
]


def _issue(
    code: str,
    message: str,
    scope: str,
    *,
    criterion_id: str | None = None,
    entity_id: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "scope": scope,
        "criterion_id": criterion_id,
        "entity_id": entity_id,
    }


def _duplicates(values: Iterable[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def _validate_rows(
    rows: Iterable[dict[str, Any]],
    schema_name: str,
    issues: list[dict[str, Any]],
) -> None:
    for index, row in enumerate(rows):
        try:
            validate_contract(
                row,
                schema_name,
                context=f"{schema_name} row {index}",
                schema_generation=3,
            )
        except ContractError as exc:
            issues.append(_issue("CONTRACT_INVALID", str(exc), schema_name))


def validate_current_artifacts(artifacts: CurrentReleaseArtifacts) -> dict[str, Any]:
    """Validate schema-5 artifacts and their cross-file invariants."""

    issues: list[dict[str, Any]] = []
    row_sets = (
        (artifacts.geographic_entities, "geographic-entity"),
        (artifacts.observations, "geographic-observation"),
        (artifacts.scores, "geographic-score"),
        (artifacts.criterion_outcomes, "criterion-outcome"),
        (artifacts.derived_country_evidence, "derived-country-evidence"),
        (artifacts.source_lineages, "source-lineage"),
        (artifacts.locality_universes, "locality-universe"),
        (artifacts.aggregation_policies, "locality-aggregation-policy"),
        (artifacts.criterion_policies, "criterion-policy"),
    )
    for rows, schema_name in row_sets:
        _validate_rows(rows, schema_name, issues)
    try:
        validate_contract(
            artifacts.consumer_catalog,
            "consumer-catalog",
            context="consumer catalog",
            schema_generation=3,
        )
    except ContractError as exc:
        issues.append(_issue("CONTRACT_INVALID", str(exc), "consumer-catalog"))

    entities = {row.get("entity_id"): row for row in artifacts.geographic_entities}
    observations = {row.get("observation_id"): row for row in artifacts.observations}
    scores = {row.get("score_id"): row for row in artifacts.scores}
    evidences = {row.get("evidence_id"): row for row in artifacts.derived_country_evidence}
    lineages = {row.get("lineage_id"): row for row in artifacts.source_lineages}
    universes = {row.get("locality_universe_id"): row for row in artifacts.locality_universes}
    aggregation_policies = {row.get("policy_id"): row for row in artifacts.aggregation_policies}
    criterion_policies = {row.get("criterion_id"): row for row in artifacts.criterion_policies}
    catalog_criteria = {
        row.get("id"): row for row in artifacts.consumer_catalog.get("criteria", [])
    }
    countries = {
        entity_id: entity
        for entity_id, entity in entities.items()
        if entity.get("entity_type") == "COUNTRY"
    }
    catalog_entities = {
        row.get("entity_id"): row
        for row in artifacts.consumer_catalog.get("geographic_entities", [])
    }
    catalog_universes = {
        row.get("locality_universe_id"): row
        for row in artifacts.consumer_catalog.get("locality_universes", [])
    }
    catalog_aggregation_policies = {
        row.get("policy_id"): row
        for row in artifacts.consumer_catalog.get("aggregation_policies", [])
    }
    for code, actual, expected in (
        ("CATALOG_ENTITY_MISMATCH", catalog_entities, entities),
        ("CATALOG_UNIVERSE_MISMATCH", catalog_universes, universes),
        (
            "CATALOG_AGGREGATION_POLICY_MISMATCH",
            catalog_aggregation_policies,
            aggregation_policies,
        ),
    ):
        if actual != expected:
            issues.append(
                _issue(
                    code,
                    "Consumer catalog and release artifact snapshot disagree.",
                    "consumer-catalog",
                )
            )

    id_sets = (
        ("DUPLICATE_ENTITY_ID", [row.get("entity_id") for row in artifacts.geographic_entities]),
        (
            "DUPLICATE_OBSERVATION_ID",
            [row.get("observation_id") for row in artifacts.observations],
        ),
        ("DUPLICATE_SCORE_ID", [row.get("score_id") for row in artifacts.scores]),
        (
            "DUPLICATE_EVIDENCE_ID",
            [row.get("evidence_id") for row in artifacts.derived_country_evidence],
        ),
        ("DUPLICATE_LINEAGE_ID", [row.get("lineage_id") for row in artifacts.source_lineages]),
        (
            "DUPLICATE_CRITERION_POLICY",
            [row.get("criterion_id") for row in artifacts.criterion_policies],
        ),
    )
    for code, values in id_sets:
        for duplicate in sorted(_duplicates(str(value) for value in values)):
            issues.append(_issue(code, f"Duplicate identifier {duplicate}.", "identity"))

    for entity_id, entity in entities.items():
        if entity.get("entity_type") == "COUNTRY":
            expected_code = str(entity_id).removeprefix("country:")
            if entity.get("country_codes") != [expected_code]:
                issues.append(
                    _issue(
                        "BROKEN_COUNTRY_IDENTITY",
                        "Country ID and country_codes disagree.",
                        "geographic-entity",
                        entity_id=entity_id,
                    )
                )
        else:
            for code in entity.get("country_codes", []):
                if f"country:{code}" not in countries:
                    issues.append(
                        _issue(
                            "BROKEN_LOCALITY_PARENTAGE",
                            f"Parent country {code} is not a declared country entity.",
                            "geographic-entity",
                            entity_id=entity_id,
                        )
                    )

    for universe_id, universe in universes.items():
        if universe.get("source_lineage_id") not in lineages:
            issues.append(
                _issue(
                    "UNKNOWN_UNIVERSE_LINEAGE",
                    "Locality universe references an unknown lineage.",
                    "locality-universe",
                )
            )
        for entity_id in universe.get("entity_ids", []):
            entity = entities.get(entity_id)
            if entity is None or entity.get("entity_type") != universe.get("locality_type"):
                issues.append(
                    _issue(
                        "UNDECLARED_LOCALITY",
                        f"{entity_id} is absent or has the wrong locality type.",
                        "locality-universe",
                        entity_id=entity_id,
                    )
                )

    for aggregation_id, aggregate in aggregation_policies.items():
        criterion_id = aggregate.get("result_criterion_id")
        policy = criterion_policies.get(criterion_id, {})
        scope = policy.get("scope", {})
        universe_ref = aggregate.get("eligible_locality_universe", {})
        universe = universes.get(universe_ref.get("locality_universe_id"))
        if (
            scope.get("aggregation_policy_id") != aggregation_id
            or aggregate.get("source_criterion_id") != criterion_id
            or universe is None
            or universe.get("locality_universe_version")
            != universe_ref.get("locality_universe_version")
            or universe.get("locality_type") != aggregate.get("locality_type")
            or scope.get("locality_type") != aggregate.get("locality_type")
        ):
            issues.append(
                _issue(
                    "CONTRADICTORY_AGGREGATION_POLICY",
                    "Aggregation policy, criterion scope, and locality universe disagree.",
                    "locality-aggregation-policy",
                    criterion_id=criterion_id,
                )
            )
        declared_roles = {
            source["role"]
            for lineage_id in policy.get("source_lineage_ids", [])
            for source in lineages.get(lineage_id, {}).get("sources", [])
        }
        if not set(aggregate.get("required_lineage_roles", [])).issubset(declared_roles):
            issues.append(
                _issue(
                    "MISSING_REQUIRED_LINEAGE_ROLE",
                    "Criterion lineages do not provide every aggregation-required source role.",
                    "locality-aggregation-policy",
                    criterion_id=criterion_id,
                )
            )

    for criterion_id, policy in criterion_policies.items():
        criterion = catalog_criteria.get(criterion_id)
        if criterion is None:
            issues.append(
                _issue(
                    "UNKNOWN_CRITERION",
                    "Criterion policy is absent from the catalog.",
                    "criterion-policy",
                    criterion_id=criterion_id,
                )
            )
            continue
        comparisons = (
            ("coverage_mode", policy.get("coverage_mode"), criterion["coverage"]["mode"]),
            ("scope", policy.get("scope"), criterion["scope"]),
            ("applicability", policy.get("applicability"), criterion["applicability"]),
            ("ready", policy.get("ready"), criterion["ready"]),
            ("experimental", policy.get("experimental"), criterion["experimental"]),
            (
                "derivation",
                policy.get("derivation", {}).get("mode"),
                criterion["scope"]["derivation"],
            ),
            (
                "scoring version",
                policy.get("scoring", {}).get("version"),
                criterion["scoring_method_version"],
            ),
            (
                "source lineages",
                set(policy.get("source_lineage_ids", [])),
                set(criterion["coverage"]["source_lineage_ids"]),
            ),
        )
        for field_name, actual, expected in comparisons:
            if actual != expected:
                issues.append(
                    _issue(
                        "CONTRADICTORY_CRITERION_POLICY",
                        f"Policy {field_name} does not match the catalog.",
                        "criterion-policy",
                        criterion_id=criterion_id,
                    )
                )
        for lineage_id in policy.get("source_lineage_ids", []):
            if lineage_id not in lineages:
                issues.append(
                    _issue(
                        "UNKNOWN_SOURCE_LINEAGE",
                        f"Policy references unknown lineage {lineage_id}.",
                        "criterion-policy",
                        criterion_id=criterion_id,
                    )
                )

    for criterion_id in sorted(set(catalog_criteria) - set(criterion_policies)):
        issues.append(
            _issue(
                "MISSING_CRITERION_POLICY",
                "Catalog criterion has no replayable ingestion policy.",
                "criterion-policy",
                criterion_id=criterion_id,
            )
        )

    for observation in artifacts.observations:
        subject = observation.get("subject", {})
        entity = entities.get(subject.get("entity_id"))
        criterion_id = observation.get("criterion_id")
        policy = criterion_policies.get(criterion_id, {})
        if entity is None or entity.get("entity_type") != subject.get("entity_type"):
            issues.append(
                _issue(
                    "UNKNOWN_OBSERVATION_ENTITY",
                    "Observation subject is absent or has a mismatched type.",
                    "observation",
                    criterion_id=criterion_id,
                    entity_id=subject.get("entity_id"),
                )
            )
        if observation.get("source_lineage_id") not in policy.get("source_lineage_ids", []):
            issues.append(
                _issue(
                    "SOURCE_LINEAGE_MISMATCH",
                    "Observation lineage is not declared by its criterion policy.",
                    "observation",
                    criterion_id=criterion_id,
                    entity_id=subject.get("entity_id"),
                )
            )
        scope = policy.get("scope", {})
        if subject.get("entity_type") == "COUNTRY" and scope.get("derivation") == "DIRECT":
            continue
        if subject.get("entity_type") == "COUNTRY" and scope.get("derivation") != "DIRECT":
            continue
        universe = universes.get(scope.get("locality_universe_id"), {})
        if scope.get("evidence_level") != "LOCALITY" or subject.get(
            "entity_id"
        ) not in universe.get("entity_ids", []):
            issues.append(
                _issue(
                    "UNDECLARED_LOCALITY_OBSERVATION",
                    "Locality observation is outside the criterion's declared universe.",
                    "observation",
                    criterion_id=criterion_id,
                    entity_id=subject.get("entity_id"),
                )
            )

    for score in artifacts.scores:
        subject = score.get("subject", {})
        criterion_id = score.get("criterion_id")
        policy = criterion_policies.get(criterion_id, {})
        if subject.get("entity_id") not in entities:
            issues.append(
                _issue(
                    "UNKNOWN_SCORE_ENTITY",
                    "Score subject is not a declared entity.",
                    "score",
                    criterion_id=criterion_id,
                    entity_id=subject.get("entity_id"),
                )
            )
        if score.get("source_lineage_id") not in policy.get("source_lineage_ids", []):
            issues.append(
                _issue(
                    "SOURCE_LINEAGE_MISMATCH",
                    "Score lineage is not declared by its criterion policy.",
                    "score",
                    criterion_id=criterion_id,
                    entity_id=subject.get("entity_id"),
                )
            )
        if score.get("scoring_method_version") != policy.get("scoring", {}).get("version"):
            issues.append(
                _issue(
                    "SCORING_METHOD_MISMATCH",
                    "Score method version does not match its criterion policy.",
                    "score",
                    criterion_id=criterion_id,
                )
            )
        score_range = (
            catalog_criteria.get(criterion_id, {}).get("coverage", {}).get("score_range", {})
        )
        if not (
            score_range.get("minimum", 0)
            <= score.get("score", -1)
            <= score_range.get("maximum", 10)
        ):
            issues.append(
                _issue(
                    "SCORE_RANGE_MISMATCH",
                    "Score is outside its criterion's declared score range.",
                    "score",
                    criterion_id=criterion_id,
                )
            )
        for observation_id in score.get("observation_ids", []):
            observation = observations.get(observation_id)
            if (
                observation is None
                or observation.get("criterion_id") != criterion_id
                or observation.get("subject") != subject
            ):
                issues.append(
                    _issue(
                        "BROKEN_SCORE_LINEAGE",
                        f"Score references incompatible observation {observation_id}.",
                        "score",
                        criterion_id=criterion_id,
                    )
                )

    for evidence in artifacts.derived_country_evidence:
        criterion_id = evidence.get("result_criterion_id")
        policy = criterion_policies.get(criterion_id, {})
        aggregate = aggregation_policies.get(
            evidence.get("aggregation_policy", {}).get("policy_id")
        )
        result_observation = observations.get(evidence.get("result_observation_id"))
        result_score = scores.get(evidence.get("result_score_id"))
        if (
            aggregate is None
            or aggregate.get("policy_version")
            != evidence.get("aggregation_policy", {}).get("policy_version")
            or policy.get("scope", {}).get("aggregation_policy_id")
            != evidence.get("aggregation_policy", {}).get("policy_id")
        ):
            issues.append(
                _issue(
                    "BROKEN_AGGREGATION_LINEAGE",
                    "Derived evidence does not resolve to its declared aggregation policy/version.",
                    "derived-country-evidence",
                    criterion_id=criterion_id,
                )
            )
        if (
            result_observation is None
            or result_score is None
            or result_observation.get("subject") != evidence.get("country")
            or result_score.get("subject") != evidence.get("country")
            or result_score.get("score") != evidence.get("result_score")
        ):
            issues.append(
                _issue(
                    "BROKEN_DERIVED_RESULT",
                    "Derived country observation/score does not reconcile with evidence.",
                    "derived-country-evidence",
                    criterion_id=criterion_id,
                )
            )
        for contributor in evidence.get("contributing_localities", []):
            contributor_score = scores.get(contributor.get("score_id"))
            if (
                contributor_score is None
                or contributor_score.get("subject") != contributor.get("locality")
                or contributor_score.get("score") != contributor.get("score")
            ):
                issues.append(
                    _issue(
                        "BROKEN_AGGREGATION_LINEAGE",
                        "Contributing locality score is missing or inconsistent.",
                        "derived-country-evidence",
                        criterion_id=criterion_id,
                    )
                )
            for observation_id in contributor.get("observation_ids", []):
                if observation_id not in observations:
                    issues.append(
                        _issue(
                            "BROKEN_AGGREGATION_LINEAGE",
                            f"Contributing observation {observation_id} is missing.",
                            "derived-country-evidence",
                            criterion_id=criterion_id,
                        )
                    )

    outcomes_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for outcome in artifacts.criterion_outcomes:
        criterion_id = outcome.get("criterion_id")
        entity_id = outcome.get("subject", {}).get("entity_id")
        key = (str(criterion_id), str(entity_id))
        if key in outcomes_by_key:
            issues.append(
                _issue(
                    "DUPLICATE_COUNTRY_OUTCOME",
                    "Criterion/country has more than one outcome.",
                    "criterion-outcome",
                    criterion_id=criterion_id,
                    entity_id=entity_id,
                )
            )
        outcomes_by_key[key] = outcome
        policy = criterion_policies.get(criterion_id, {})
        if set(outcome.get("source_lineage_ids", [])) != set(policy.get("source_lineage_ids", [])):
            issues.append(
                _issue(
                    "MULTIPLE_SOURCE_LINEAGE_MISMATCH",
                    "Outcome lineage set does not exactly match its criterion policy.",
                    "criterion-outcome",
                    criterion_id=criterion_id,
                    entity_id=entity_id,
                )
            )
        if outcome.get("outcome") == "valid":
            score = scores.get(outcome.get("score_id"))
            observation = observations.get(outcome.get("observation_id"))
            if (
                score is None
                or observation is None
                or score.get("subject") != outcome.get("subject")
                or observation.get("subject") != outcome.get("subject")
            ):
                issues.append(
                    _issue(
                        "BROKEN_OUTCOME_RESULT",
                        "Valid outcome does not resolve to a country observation and score.",
                        "criterion-outcome",
                        criterion_id=criterion_id,
                        entity_id=entity_id,
                    )
                )
            if outcome.get("evidence_kind") == "DERIVED_LOCALITIES":
                evidence = evidences.get(outcome.get("derived_evidence_id"))
                if (
                    evidence is None
                    or evidence.get("result_observation_id") != outcome.get("observation_id")
                    or evidence.get("result_score_id") != outcome.get("score_id")
                ):
                    issues.append(
                        _issue(
                            "BROKEN_AGGREGATION_LINEAGE",
                            "Derived outcome does not reconcile with derived evidence.",
                            "criterion-outcome",
                            criterion_id=criterion_id,
                            entity_id=entity_id,
                        )
                    )

    expected_keys = {
        (criterion_id, country_id) for criterion_id in catalog_criteria for country_id in countries
    }
    for criterion_id, entity_id in sorted(expected_keys - set(outcomes_by_key)):
        issues.append(
            _issue(
                "MISSING_COUNTRY_OUTCOME",
                "Every criterion/country result must have an explicit outcome.",
                "criterion-outcome",
                criterion_id=criterion_id,
                entity_id=entity_id,
            )
        )

    outcome_counts: dict[str, dict[str, int]] = {}
    for criterion_id, criterion in catalog_criteria.items():
        counts = Counter(
            outcome.get("outcome")
            for (candidate, _), outcome in outcomes_by_key.items()
            if candidate == criterion_id
        )
        normalized = {
            status: counts.get(status, 0)
            for status in ("valid", "missing", "stale", "invalid", "rejected")
        }
        outcome_counts[criterion_id] = normalized
        coverage = criterion.get("coverage", {})
        if (
            normalized != coverage.get("outcome_counts")
            or normalized["valid"] != coverage.get("valid_country_count")
            or sum(normalized.values()) != coverage.get("stable_country_count")
            or coverage.get("stable_country_count") != len(countries)
        ):
            issues.append(
                _issue(
                    "COVERAGE_RECONCILIATION_FAILED",
                    "Catalog coverage does not reconcile with explicit country outcomes.",
                    "coverage",
                    criterion_id=criterion_id,
                )
            )

    structural_passed = not any(issue["severity"] in {"error", "blocker"} for issue in issues)
    product_ready = structural_passed and all(
        not criterion.get("ready")
        or criterion["coverage"]["valid_country_count"]
        >= criterion["coverage"]["minimum_valid_country_count"]
        for criterion in catalog_criteria.values()
    )
    report = {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "structural_passed": structural_passed,
        "product_ready": product_ready,
        "passed": structural_passed,
        "stable_universe_id": artifacts.consumer_catalog.get("stable_universe_id", "unknown"),
        "country_count": len(countries),
        "geographic_entity_count": len(artifacts.geographic_entities),
        "observation_count": len(artifacts.observations),
        "score_count": len(artifacts.scores),
        "criterion_outcome_count": len(artifacts.criterion_outcomes),
        "derived_country_evidence_count": len(artifacts.derived_country_evidence),
        "source_lineage_count": len(artifacts.source_lineages),
        "criterion_coverage": {
            criterion_id: criterion["coverage"]
            for criterion_id, criterion in sorted(catalog_criteria.items())
        },
        "lineage_passed": not any("LINEAGE" in issue["code"] for issue in issues),
        "locality_policy_passed": not any(
            issue["code"]
            in {
                "BROKEN_LOCALITY_PARENTAGE",
                "UNDECLARED_LOCALITY",
                "UNDECLARED_LOCALITY_OBSERVATION",
                "BROKEN_AGGREGATION_LINEAGE",
            }
            for issue in issues
        ),
        "issues": issues,
    }
    try:
        validate_contract(
            report,
            "validation-report",
            context="generated validation report",
            schema_generation=3,
        )
    except ContractError as exc:
        raise CurrentReleaseError(str(exc)) from exc
    return report


def build_country_outcomes(
    *,
    policies: Iterable[dict[str, Any]],
    entities: Iterable[dict[str, Any]],
    observations: Iterable[dict[str, Any]],
    scores: Iterable[dict[str, Any]],
    evidence: Iterable[dict[str, Any]],
    attempted_at: str,
    rejected_countries: Mapping[str, Mapping[str, str]] | None = None,
    explicit_outcomes: Iterable[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Build the explicit country-result matrix; locality outcomes are intentionally absent."""

    observations_by_key = {
        (row["criterion_id"], row["subject"]["entity_id"]): row
        for row in observations
        if row["subject"]["entity_type"] == "COUNTRY"
    }
    scores_by_key = {
        (row["criterion_id"], row["subject"]["entity_id"]): row
        for row in scores
        if row["subject"]["entity_type"] == "COUNTRY"
    }
    evidence_by_key = {
        (row["result_criterion_id"], row["country"]["entity_id"]): row for row in evidence
    }
    explicit_rows = tuple(explicit_outcomes)
    explicit_by_key = {
        (row["criterion_id"], row["subject"]["entity_id"]): row for row in explicit_rows
    }
    if len(explicit_by_key) != len(explicit_rows):
        raise CurrentReleaseError(
            "Explicit country outcomes contain duplicate criterion/country rows."
        )
    countries = sorted(
        (row for row in entities if row["entity_type"] == "COUNTRY"),
        key=lambda row: row["entity_id"],
    )
    rows: list[dict[str, Any]] = []
    for policy in sorted(policies, key=lambda row: row["criterion_id"]):
        criterion_id = policy["criterion_id"]
        for country in countries:
            entity_id = country["entity_id"]
            explicit = explicit_by_key.get((criterion_id, entity_id))
            if explicit is not None:
                rows.append(explicit)
                continue
            subject = {"entity_id": entity_id, "entity_type": "COUNTRY"}
            observation = observations_by_key.get((criterion_id, entity_id))
            score = scores_by_key.get((criterion_id, entity_id))
            derived = evidence_by_key.get((criterion_id, entity_id))
            rejected_reason = (rejected_countries or {}).get(criterion_id, {}).get(entity_id)
            if rejected_reason:
                outcome, reason_codes = "rejected", [rejected_reason]
            elif observation is not None and score is not None:
                outcome, reason_codes = "valid", []
            else:
                outcome, reason_codes = "missing", ["SOURCE_VALUE_MISSING"]
            evidence_kind = (
                "DERIVED_LOCALITIES"
                if outcome == "valid" and policy["derivation"]["mode"] != "DIRECT"
                else ("DIRECT_OBSERVATION" if outcome == "valid" else "NONE")
            )
            rows.append(
                {
                    "criterion_id": criterion_id,
                    "subject": subject,
                    "outcome": outcome,
                    "evidence_kind": evidence_kind,
                    "attempted_at": attempted_at,
                    "observation_id": observation["observation_id"] if outcome == "valid" else None,
                    "score_id": score["score_id"] if outcome == "valid" else None,
                    "derived_evidence_id": (
                        derived["evidence_id"]
                        if outcome == "valid" and evidence_kind == "DERIVED_LOCALITIES"
                        else None
                    ),
                    "source_lineage_ids": sorted(policy["source_lineage_ids"]),
                    "reason_codes": reason_codes,
                    "quality_flags": sorted(
                        set(observation.get("quality_flags", []) if observation else [])
                        | set(score.get("quality_flags", []) if score else [])
                    ),
                }
            )
    return rows


class GenericReleaseWorker:
    """Policy-driven schema-5 orchestrator with injectable versioned processors."""

    def __init__(self, processors: Mapping[tuple[str, str], CriterionProcessor]) -> None:
        self.processors = processors

    def build(
        self,
        *,
        release_id: str,
        catalog: dict[str, Any],
        entities: Iterable[dict[str, Any]],
        source_lineages: Iterable[dict[str, Any]],
        locality_universes: Iterable[dict[str, Any]],
        aggregation_policies: Iterable[dict[str, Any]],
        criterion_policies: Iterable[dict[str, Any]],
        attempted_at: str,
    ) -> CurrentReleaseArtifacts:
        entity_rows = tuple(entities)
        lineage_rows = tuple(source_lineages)
        policy_rows = tuple(criterion_policies)
        lineages_by_id = {row["lineage_id"]: row for row in lineage_rows}
        observations: list[dict[str, Any]] = []
        scores: list[dict[str, Any]] = []
        derived: list[dict[str, Any]] = []
        explicit_outcomes: list[dict[str, Any]] = []
        rejected: dict[str, dict[str, str]] = {}
        for policy in sorted(policy_rows, key=lambda row: row["criterion_id"]):
            parser = policy["parser"]
            key = (parser["id"], parser["version"])
            try:
                processor = self.processors[key]
            except KeyError as exc:
                raise CurrentReleaseError(
                    f"No registered processor for {parser['id']}@{parser['version']}."
                ) from exc
            criterion_lineages = tuple(
                lineages_by_id[lineage_id] for lineage_id in policy["source_lineage_ids"]
            )
            result = processor(policy, criterion_lineages, lineages_by_id)
            observations.extend(result.observations)
            scores.extend(result.scores)
            derived.extend(result.derived_country_evidence)
            explicit_outcomes.extend(result.criterion_outcomes)
            rejected[policy["criterion_id"]] = result.rejected_countries
        outcomes = build_country_outcomes(
            policies=policy_rows,
            entities=entity_rows,
            observations=observations,
            scores=scores,
            evidence=derived,
            attempted_at=attempted_at,
            rejected_countries=rejected,
            explicit_outcomes=explicit_outcomes,
        )
        return CurrentReleaseArtifacts(
            geographic_entities=tuple(entity_rows),
            observations=tuple(observations),
            scores=tuple(scores),
            criterion_outcomes=tuple(outcomes),
            derived_country_evidence=tuple(derived),
            source_lineages=lineage_rows,
            locality_universes=tuple(locality_universes),
            aggregation_policies=tuple(aggregation_policies),
            criterion_policies=policy_rows,
            consumer_catalog=catalog,
        )


def _write_json(path: Path, value: object) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    rows = [json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values]
    write_text_lf(path, "\n".join(rows) + ("\n" if rows else ""))


def _checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _canonicalize(artifacts: CurrentReleaseArtifacts) -> CurrentReleaseArtifacts:
    catalog = deepcopy(artifacts.consumer_catalog)
    for field_name, id_field in (
        ("geographic_entities", "entity_id"),
        ("criteria", "id"),
        ("locality_universes", "locality_universe_id"),
        ("aggregation_policies", "policy_id"),
        ("preference_presets", "id"),
    ):
        catalog[field_name] = sorted(catalog[field_name], key=lambda row: row[id_field])
    return CurrentReleaseArtifacts(
        geographic_entities=tuple(
            sorted(artifacts.geographic_entities, key=lambda row: row["entity_id"])
        ),
        observations=tuple(sorted(artifacts.observations, key=lambda row: row["observation_id"])),
        scores=tuple(sorted(artifacts.scores, key=lambda row: row["score_id"])),
        criterion_outcomes=tuple(
            sorted(
                artifacts.criterion_outcomes,
                key=lambda row: (row["criterion_id"], row["subject"]["entity_id"]),
            )
        ),
        derived_country_evidence=tuple(
            sorted(
                artifacts.derived_country_evidence,
                key=lambda row: row["evidence_id"],
            )
        ),
        source_lineages=tuple(sorted(artifacts.source_lineages, key=lambda row: row["lineage_id"])),
        locality_universes=tuple(
            sorted(
                artifacts.locality_universes,
                key=lambda row: row["locality_universe_id"],
            )
        ),
        aggregation_policies=tuple(
            sorted(artifacts.aggregation_policies, key=lambda row: row["policy_id"])
        ),
        criterion_policies=tuple(
            sorted(artifacts.criterion_policies, key=lambda row: row["criterion_id"])
        ),
        consumer_catalog=catalog,
    )


class CurrentReleaseRepository:
    """Immutable writer/loader for release-5 and catalog-3 snapshots."""

    def __init__(
        self,
        root: Path | str = "data/releases",
        catalog_snapshot_root: Path | str = "data/catalogs/releases",
    ) -> None:
        self.root = Path(root)
        self.catalog_snapshot_root = Path(catalog_snapshot_root)

    def write_draft(self, release_id: str, artifacts: CurrentReleaseArtifacts) -> Path:
        draft = self.root / ".draft" / release_id
        published = self.root / release_id
        if draft.exists() or published.exists():
            raise FileExistsError(f"Release ID is already immutable or in use: {release_id}")
        artifacts = _canonicalize(artifacts)
        report = validate_current_artifacts(artifacts)
        draft.mkdir(parents=True)
        jsonl = {
            "geographic-entities.jsonl": artifacts.geographic_entities,
            "observations.jsonl": artifacts.observations,
            "scores.jsonl": artifacts.scores,
            "criterion-outcomes.jsonl": artifacts.criterion_outcomes,
            "derived-country-evidence.jsonl": artifacts.derived_country_evidence,
        }
        for filename, rows in jsonl.items():
            _write_jsonl(draft / filename, rows)
        json_files = {
            "source-lineages.json": artifacts.source_lineages,
            "locality-universes.json": artifacts.locality_universes,
            "aggregation-policies.json": artifacts.aggregation_policies,
            "criterion-policies.json": artifacts.criterion_policies,
            "consumer-catalog.json": artifacts.consumer_catalog,
            "validation.json": report,
        }
        for filename, value in json_files.items():
            _write_json(draft / filename, value)
        file_checksums = {filename: _checksum(draft / filename) for filename in PAYLOAD_FILES}
        release_checksum = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(file_checksums, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        criteria = sorted(row["id"] for row in artifacts.consumer_catalog["criteria"])
        manifest = {
            "schema_version": RELEASE_SCHEMA_VERSION,
            "release_id": release_id,
            "status": "draft",
            "catalog_schema_version": artifacts.consumer_catalog["schema_version"],
            "validation_schema_version": report["schema_version"],
            "stable_universe_id": artifacts.consumer_catalog["stable_universe_id"],
            "country_entity_ids": sorted(
                row["entity_id"]
                for row in artifacts.geographic_entities
                if row["entity_type"] == "COUNTRY"
            ),
            "criteria": criteria,
            "criterion_coverage": report["criterion_coverage"],
            "artifact_counts": {
                "geographic_entities": len(artifacts.geographic_entities),
                "observations": len(artifacts.observations),
                "scores": len(artifacts.scores),
                "criterion_outcomes": len(artifacts.criterion_outcomes),
                "derived_country_evidence": len(artifacts.derived_country_evidence),
                "source_lineages": len(artifacts.source_lineages),
                "criterion_policies": len(artifacts.criterion_policies),
            },
            "source_lineage_ids": sorted(row["lineage_id"] for row in artifacts.source_lineages),
            "locality_universe_ids": sorted(
                row["locality_universe_id"] for row in artifacts.locality_universes
            ),
            "aggregation_policy_ids": sorted(
                row["policy_id"] for row in artifacts.aggregation_policies
            ),
            "scoring_method_versions": sorted(
                {row["scoring_method_version"] for row in artifacts.scores}
                or {row["scoring"]["version"] for row in artifacts.criterion_policies}
            ),
            "file_checksums": file_checksums,
            "release_checksum": release_checksum,
        }
        validate_contract(
            manifest,
            "release-manifest",
            context="generated release manifest",
            schema_generation=3,
        )
        _write_json(draft / "manifest.json", manifest)
        return draft

    def publish(
        self,
        release_id: str,
        *,
        require_product_ready: bool = True,
        activate: bool = False,
    ) -> Path:
        draft = self.root / ".draft" / release_id
        validation = json.loads((draft / "validation.json").read_text(encoding="utf-8"))
        if not validation["structural_passed"]:
            raise CurrentReleaseError("A structurally invalid release cannot be published.")
        if require_product_ready and not validation["product_ready"]:
            raise CurrentReleaseError("A non-product-ready release cannot be published.")
        published = self.root / release_id
        snapshot = self.catalog_snapshot_root / f"{release_id}.json"
        if published.exists() or snapshot.exists():
            raise FileExistsError(f"Published release/catalog is immutable: {release_id}")
        manifest_path = draft / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "published"
        _write_json(manifest_path, manifest)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot_tmp = snapshot.with_suffix(".json.tmp")
        _write_json(
            snapshot_tmp,
            json.loads((draft / "consumer-catalog.json").read_text(encoding="utf-8")),
        )
        published.parent.mkdir(parents=True, exist_ok=True)
        draft.replace(published)
        os.replace(snapshot_tmp, snapshot)
        if activate:
            self.activate(release_id)
        return published

    def activate(self, release_id: str) -> Path:
        """Atomically activate an already-published, validated schema-5 release."""

        published = self.root / release_id
        loaded = self.load(published)
        if loaded.manifest["status"] != "published":
            raise CurrentReleaseError("Only a published release can be activated.")
        if not loaded.validation["product_ready"]:
            raise CurrentReleaseError("A non-product-ready release cannot be activated.")
        pointer_tmp = self.root / "active.json.tmp"
        _write_json(
            pointer_tmp,
            {"release_id": release_id, "schema_version": RELEASE_SCHEMA_VERSION},
        )
        os.replace(pointer_tmp, self.root / "active.json")
        return self.root / "active.json"

    def load_active(self, pointer_path: Path | str | None = None) -> LoadedCurrentRelease:
        """Load the schema-current release selected by the active pointer."""

        path = Path(pointer_path) if pointer_path is not None else self.root / "active.json"
        try:
            pointer = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise CurrentReleaseError(
                "The active release pointer is unavailable or invalid."
            ) from exc
        if pointer.get("schema_version") != RELEASE_SCHEMA_VERSION:
            raise CurrentReleaseError(
                "The active release pointer does not select the schema-current contract."
            )
        release_id = pointer.get("release_id")
        if not isinstance(release_id, str) or not release_id:
            raise CurrentReleaseError("The active release pointer has no valid release ID.")
        loaded = self.load(self.root / release_id)
        if loaded.manifest["release_id"] != release_id:
            raise CurrentReleaseError("The active pointer and release manifest IDs disagree.")
        return loaded

    def load(self, path: Path | str) -> LoadedCurrentRelease:
        release_path = Path(path)
        manifest = json.loads((release_path / "manifest.json").read_text(encoding="utf-8"))
        validate_contract(
            manifest,
            "release-manifest",
            context="release manifest",
            schema_generation=3,
        )
        for filename, expected in manifest["file_checksums"].items():
            actual = _checksum(release_path / filename)
            if actual != expected:
                raise CurrentReleaseError(
                    f"Checksum mismatch for {filename}: expected {expected}, got {actual}."
                )
        actual_release_checksum = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(
                    manifest["file_checksums"], sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest()
        )
        if actual_release_checksum != manifest["release_checksum"]:
            raise CurrentReleaseError("Release checksum does not reconcile with payload files.")

        def read_jsonl(filename: str) -> tuple[dict[str, Any], ...]:
            return tuple(
                json.loads(line)
                for line in (release_path / filename).read_text(encoding="utf-8").splitlines()
            )

        def read_json(filename: str) -> Any:
            return json.loads((release_path / filename).read_text(encoding="utf-8"))

        artifacts = CurrentReleaseArtifacts(
            geographic_entities=read_jsonl("geographic-entities.jsonl"),
            observations=read_jsonl("observations.jsonl"),
            scores=read_jsonl("scores.jsonl"),
            criterion_outcomes=read_jsonl("criterion-outcomes.jsonl"),
            derived_country_evidence=read_jsonl("derived-country-evidence.jsonl"),
            source_lineages=tuple(read_json("source-lineages.json")),
            locality_universes=tuple(read_json("locality-universes.json")),
            aggregation_policies=tuple(read_json("aggregation-policies.json")),
            criterion_policies=tuple(read_json("criterion-policies.json")),
            consumer_catalog=read_json("consumer-catalog.json"),
        )
        report = read_json("validation.json")
        regenerated = validate_current_artifacts(artifacts)
        if regenerated != report:
            raise CurrentReleaseError("Stored validation report is not reproducible.")
        if (
            manifest["catalog_schema_version"] != artifacts.consumer_catalog["schema_version"]
            or manifest["validation_schema_version"] != report["schema_version"]
            or manifest["stable_universe_id"] != artifacts.consumer_catalog["stable_universe_id"]
        ):
            raise CurrentReleaseError(
                "Manifest, catalog, and validation schema/universe metadata disagree."
            )
        if manifest["artifact_counts"] != {
            "geographic_entities": len(artifacts.geographic_entities),
            "observations": len(artifacts.observations),
            "scores": len(artifacts.scores),
            "criterion_outcomes": len(artifacts.criterion_outcomes),
            "derived_country_evidence": len(artifacts.derived_country_evidence),
            "source_lineages": len(artifacts.source_lineages),
            "criterion_policies": len(artifacts.criterion_policies),
        }:
            raise CurrentReleaseError("Manifest artifact counts do not match payload files.")
        if manifest["criterion_coverage"] != report["criterion_coverage"]:
            raise CurrentReleaseError("Manifest and validation coverage metadata disagree.")
        expected_inventory = {
            "country_entity_ids": sorted(
                row["entity_id"]
                for row in artifacts.geographic_entities
                if row["entity_type"] == "COUNTRY"
            ),
            "criteria": sorted(row["id"] for row in artifacts.consumer_catalog["criteria"]),
            "source_lineage_ids": sorted(row["lineage_id"] for row in artifacts.source_lineages),
            "locality_universe_ids": sorted(
                row["locality_universe_id"] for row in artifacts.locality_universes
            ),
            "aggregation_policy_ids": sorted(
                row["policy_id"] for row in artifacts.aggregation_policies
            ),
            "scoring_method_versions": sorted(
                {row["scoring_method_version"] for row in artifacts.scores}
                or {row["scoring"]["version"] for row in artifacts.criterion_policies}
            ),
        }
        for field_name, expected in expected_inventory.items():
            if manifest[field_name] != expected:
                raise CurrentReleaseError(
                    f"Manifest {field_name} does not match release artifacts."
                )
        return LoadedCurrentRelease(release_path, manifest, report, artifacts)

    def replay(
        self,
        path: Path | str,
        *,
        processors: Mapping[tuple[str, str], CriterionProcessor],
    ) -> ReplayResult:
        loaded = self.load(path)
        attempted_values = {row["attempted_at"] for row in loaded.artifacts.criterion_outcomes}
        if len(attempted_values) != 1:
            return ReplayResult(
                "FAILED", detail="Replay requires one deterministic attempted_at value."
            )
        try:
            rebuilt = GenericReleaseWorker(processors).build(
                release_id=loaded.manifest["release_id"],
                catalog=loaded.artifacts.consumer_catalog,
                entities=loaded.artifacts.geographic_entities,
                source_lineages=loaded.artifacts.source_lineages,
                locality_universes=loaded.artifacts.locality_universes,
                aggregation_policies=loaded.artifacts.aggregation_policies,
                criterion_policies=loaded.artifacts.criterion_policies,
                attempted_at=next(iter(attempted_values)),
            )
        except SourceBytesUnavailable as exc:
            return ReplayResult("SOURCE_BYTES_UNAVAILABLE", detail=str(exc))
        with tempfile.TemporaryDirectory(prefix="konsider-release5-replay-") as temporary:
            replay_repository = CurrentReleaseRepository(
                Path(temporary) / "releases", Path(temporary) / "catalogs"
            )
            rebuilt_path = replay_repository.write_draft(loaded.manifest["release_id"], rebuilt)
            compared = tuple(PAYLOAD_FILES)
            mismatched = list(
                filename
                for filename in compared
                if (loaded.path / filename).read_bytes() != (rebuilt_path / filename).read_bytes()
            )
            rebuilt_manifest = json.loads(
                (rebuilt_path / "manifest.json").read_text(encoding="utf-8")
            )
            rebuilt_manifest["status"] = loaded.manifest["status"]
            if rebuilt_manifest != loaded.manifest:
                mismatched.append("manifest.json")
        return ReplayResult(
            "PASSED" if not mismatched else "FAILED",
            compared_files=(*compared, "manifest.json"),
            mismatched_files=tuple(mismatched),
            detail=None if not mismatched else "Rebuilt payload bytes differ.",
        )
