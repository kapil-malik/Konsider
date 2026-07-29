"""Policy-driven deterministic locality-to-country aggregation."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN
from itertools import chain
from typing import Any

from konsider.domain.locality_models import (
    LocalityAggregationResult,
    LocalityAggregationStatus,
)

DISQUALIFYING_STALE_FLAGS = frozenset({"STALE", "SOURCE_STALE"})
DISQUALIFYING_INVALID_FLAGS = frozenset(
    {"INVALID", "REJECTED", "SOURCE_INVALID", "SOURCE_REJECTED"}
)


class LocalityAggregationError(ValueError):
    """Raised when release inputs cannot safely execute an aggregation policy."""


def _reference(entity_id: str, entity_type: str) -> dict[str, str]:
    return {"entity_id": entity_id, "entity_type": entity_type}


def _round_score(value: Decimal, precision: int) -> float:
    quantum = Decimal(1).scaleb(-precision)
    return float(value.quantize(quantum, rounding=ROUND_HALF_EVEN))


def _classify_quality(flags: set[str]) -> str:
    if flags & DISQUALIFYING_INVALID_FLAGS:
        return "invalid"
    if flags & DISQUALIFYING_STALE_FLAGS:
        return "stale"
    return "valid"


def _select_scores(
    rows: list[dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[list[dict[str, Any]], tuple[str, ...], str | None]:
    selection = policy["selection"]
    method = selection["method"]
    if method == "ALL_VALID_MEAN":
        return sorted(rows, key=lambda row: row["subject"]["entity_id"]), (), None

    reverse = method == "TOP_N_MEAN"
    ordered = sorted(
        rows,
        key=lambda row: (
            -Decimal(str(row["score"])) if reverse else Decimal(str(row["score"])),
            row["subject"]["entity_id"],
        ),
    )
    n = selection["n"]
    if len(ordered) <= n:
        flags = ("FEWER_THAN_N_AVAILABLE",) if len(ordered) < n else ()
        return ordered, flags, None
    boundary = Decimal(str(ordered[n - 1]["score"]))
    tied_after_boundary = [row for row in ordered[n:] if Decimal(str(row["score"])) == boundary]
    if not tied_after_boundary:
        return ordered[:n], (), None
    tie_handling = policy["tie_handling"]
    if tie_handling == "STABLE_ENTITY_ID":
        return ordered[:n], (), None
    if tie_handling == "FAIL_AMBIGUOUS":
        return [], (), "AMBIGUOUS_BOUNDARY_TIE"
    selected = [
        row
        for row in ordered
        if (
            Decimal(str(row["score"])) >= boundary
            if reverse
            else Decimal(str(row["score"])) <= boundary
        )
    ]
    return selected, ("BOUNDARY_TIES_INCLUDED",), None


def aggregate_locality_criterion(
    *,
    release_id: str,
    criterion: dict[str, Any],
    aggregation_policy: dict[str, Any],
    locality_universe: dict[str, Any],
    geographic_entities: tuple[dict[str, Any], ...],
    observations: tuple[dict[str, Any], ...],
    scores: tuple[dict[str, Any], ...],
    source_lineage_ids: tuple[str, ...],
    attempted_at: str,
) -> tuple[LocalityAggregationResult, ...]:
    """Aggregate every country for one locality-derived criterion.

    Input locality scores are canonical 0-10 opportunity scores. Therefore TOP_N
    always means the highest normalized opportunity scores, regardless of the raw
    criterion direction.
    """

    scope = criterion["scope"]
    if (
        scope["derivation"] != "AGGREGATED_FROM_LOCALITIES"
        or scope["locality_universe_id"] != locality_universe["locality_universe_id"]
        or scope["aggregation_policy_id"] != aggregation_policy["policy_id"]
    ):
        raise LocalityAggregationError(
            "Criterion scope, locality universe, and aggregation policy disagree."
        )
    if (
        aggregation_policy["eligible_locality_universe"]["locality_universe_version"]
        != locality_universe["locality_universe_version"]
        or aggregation_policy["result_criterion_id"] != criterion["id"]
    ):
        raise LocalityAggregationError("Aggregation policy version or result criterion mismatch.")
    if not source_lineage_ids:
        raise LocalityAggregationError("Aggregation requires at least one source lineage.")

    entities = {row["entity_id"]: row for row in geographic_entities}
    countries = sorted(
        (row for row in geographic_entities if row["entity_type"] == "COUNTRY"),
        key=lambda row: row["entity_id"],
    )
    universe_ids = set(locality_universe["entity_ids"])
    for entity_id in universe_ids:
        entity = entities.get(entity_id)
        if entity is None or entity["entity_type"] != locality_universe["locality_type"]:
            raise LocalityAggregationError(
                f"Locality universe contains absent or mismatched entity {entity_id}."
            )

    observations_by_id = {row["observation_id"]: row for row in observations}
    relevant_scores = [
        row
        for row in scores
        if row["criterion_id"] == aggregation_policy["source_criterion_id"]
        and row["subject"]["entity_type"] != "COUNTRY"
    ]
    seen_score_subjects: set[str] = set()
    for row in relevant_scores:
        entity_id = row["subject"]["entity_id"]
        entity = entities.get(entity_id)
        if entity is None or entity["entity_type"] != row["subject"]["entity_type"]:
            raise LocalityAggregationError(
                f"Score subject is absent or mismatched for {entity_id}."
            )
        if entity_id in seen_score_subjects:
            raise LocalityAggregationError(
                f"Criterion has more than one locality score for {entity_id}."
            )
        seen_score_subjects.add(entity_id)
        for observation_id in row["observation_ids"]:
            observation = observations_by_id.get(observation_id)
            if (
                observation is None
                or observation["criterion_id"] != row["criterion_id"]
                or observation["subject"] != row["subject"]
            ):
                raise LocalityAggregationError(
                    f"Score {row['score_id']} has broken observation lineage."
                )
    outside_ids = sorted(
        {
            row["subject"]["entity_id"]
            for row in relevant_scores
            if row["subject"]["entity_id"] not in universe_ids
        }
    )
    eligible_scores = [
        row for row in relevant_scores if row["subject"]["entity_id"] in universe_ids
    ]

    results: list[LocalityAggregationResult] = []
    for country in countries:
        country_id = country["entity_id"]
        country_code = country_id.removeprefix("country:")
        eligible_ids = sorted(
            entity_id
            for entity_id in universe_ids
            if country_code in entities[entity_id]["country_codes"]
        )
        country_scores = [
            row for row in eligible_scores if row["subject"]["entity_id"] in eligible_ids
        ]
        valid_rows: list[dict[str, Any]] = []
        quality_counts: Counter[str] = Counter()
        for row in country_scores:
            flags = set(row.get("quality_flags", []))
            flags.update(
                chain.from_iterable(
                    observations_by_id[observation_id].get("quality_flags", [])
                    for observation_id in row["observation_ids"]
                )
            )
            classification = _classify_quality(flags)
            quality_counts[classification] += 1
            if classification == "valid":
                valid_rows.append(row)

        status = LocalityAggregationStatus.MISSING
        reasons: tuple[str, ...] = ()
        selected: list[dict[str, Any]] = []
        selection_flags: tuple[str, ...] = ()
        if not eligible_ids:
            reasons = ("NO_QUALIFYING_LOCALITY",)
        elif not valid_rows:
            if quality_counts["stale"] and not quality_counts["invalid"]:
                status, reasons = LocalityAggregationStatus.STALE, ("LOCALITY_INPUT_STALE",)
            elif quality_counts["invalid"]:
                status, reasons = LocalityAggregationStatus.INVALID, ("LOCALITY_INPUT_INVALID",)
            else:
                reasons = ("NO_VALID_LOCALITY_SCORE",)
        elif (
            len(valid_rows) == 1
            and aggregation_policy["one_locality_treatment"] == "INSUFFICIENT_EVIDENCE"
        ):
            reasons = ("SINGLE_LOCALITY_INSUFFICIENT",)
        elif len(valid_rows) < aggregation_policy["minimum_valid_localities"]:
            reasons = ("INSUFFICIENT_VALID_LOCALITIES",)
        else:
            selected, selection_flags, selection_error = _select_scores(
                valid_rows, aggregation_policy
            )
            if selection_error:
                status = LocalityAggregationStatus.REJECTED
                reasons = (selection_error,)
            else:
                status = LocalityAggregationStatus.VALID

        valid_ids = tuple(sorted(row["subject"]["entity_id"] for row in valid_rows))
        country_outside_ids = {
            entity_id
            for entity_id in outside_ids
            if country_code in entities[entity_id]["country_codes"]
        }
        ignored_ids = tuple(
            sorted(
                country_outside_ids
                | {row["subject"]["entity_id"] for row in country_scores if row not in valid_rows}
            )
        )
        quality_flags = set(selection_flags)
        if country_outside_ids:
            quality_flags.add("OUTSIDE_UNIVERSE_INPUT_IGNORED")
        if quality_counts["stale"]:
            quality_flags.add("STALE_LOCALITY_INPUT_IGNORED")
        if quality_counts["invalid"]:
            quality_flags.add("INVALID_LOCALITY_INPUT_IGNORED")

        observation = score = evidence = None
        if status == LocalityAggregationStatus.VALID:
            if len(valid_rows) == len(eligible_ids):
                quality_flags.add("COMPLETE_LOCALITY_INPUTS")
            else:
                quality_flags.add("PARTIAL_LOCALITY_INPUTS")
            if len(selected) == 1:
                quality_flags.add("SINGLE_LOCALITY_RESULT")
            score_value = _round_score(
                sum((Decimal(str(row["score"])) for row in selected), Decimal())
                / Decimal(len(selected)),
                aggregation_policy["score_precision"],
            )
            result_criterion_id = aggregation_policy["result_criterion_id"]
            suffix = (
                f"{result_criterion_id}:{country_id}:{aggregation_policy['policy_id']}:"
                f"{aggregation_policy['policy_version']}"
            )
            observation_id = f"obs:derived:{suffix}"
            score_id = f"score:derived:{suffix}"
            evidence_id = f"derived:{suffix}"
            selected_observations = [
                observations_by_id[observation_id]
                for row in selected
                for observation_id in row["observation_ids"]
            ]
            reference_period = {
                "start": min(row["reference_period"]["start"] for row in selected_observations),
                "end": max(row["reference_period"]["end"] for row in selected_observations),
            }
            subject = _reference(country_id, "COUNTRY")
            observation = {
                "observation_id": observation_id,
                "criterion_id": result_criterion_id,
                "subject": subject,
                "value": score_value,
                "unit": "normalized_score_0_10",
                "reference_period": reference_period,
                "source_lineage_id": source_lineage_ids[0],
                "quality_flags": sorted(quality_flags),
            }
            score = {
                "score_id": score_id,
                "criterion_id": result_criterion_id,
                "subject": subject,
                "score": score_value,
                "observation_ids": [observation_id],
                "scoring_method_version": criterion["scoring_method_version"],
                "source_lineage_id": source_lineage_ids[0],
                "quality_flags": sorted(quality_flags),
            }
            evidence = {
                "evidence_id": evidence_id,
                "result_criterion_id": result_criterion_id,
                "country": subject,
                "derivation_method": "AGGREGATED_FROM_LOCALITIES",
                "aggregation_policy": {
                    "policy_id": aggregation_policy["policy_id"],
                    "policy_version": aggregation_policy["policy_version"],
                },
                "input_release_id": release_id,
                "result_observation_id": observation_id,
                "result_score_id": score_id,
                "contributing_localities": [
                    {
                        "locality": dict(row["subject"]),
                        "observation_ids": list(row["observation_ids"]),
                        "score_id": row["score_id"],
                        "score": row["score"],
                    }
                    for row in selected
                ],
                "eligible_locality_count": len(eligible_ids),
                "valid_locality_count": len(valid_rows),
                "result_score": score_value,
                "criterion_source_lineage_id": source_lineage_ids[0],
                "quality_flags": sorted(quality_flags),
            }

        outcome = {
            "criterion_id": criterion["id"],
            "subject": _reference(country_id, "COUNTRY"),
            "outcome": status.value,
            "evidence_kind": (
                "DERIVED_LOCALITIES" if status == LocalityAggregationStatus.VALID else "NONE"
            ),
            "attempted_at": attempted_at,
            "observation_id": observation["observation_id"] if observation else None,
            "score_id": score["score_id"] if score else None,
            "derived_evidence_id": evidence["evidence_id"] if evidence else None,
            "source_lineage_ids": sorted(source_lineage_ids),
            "reason_codes": list(reasons),
            "quality_flags": sorted(quality_flags),
        }
        results.append(
            LocalityAggregationResult(
                criterion_id=criterion["id"],
                country_entity_id=country_id,
                status=status,
                reason_codes=reasons,
                quality_flags=tuple(sorted(quality_flags)),
                eligible_locality_entity_ids=tuple(eligible_ids),
                valid_locality_entity_ids=valid_ids,
                ignored_locality_entity_ids=ignored_ids,
                observation=observation,
                score=score,
                evidence=evidence,
                outcome=outcome,
            )
        )
    return tuple(results)
