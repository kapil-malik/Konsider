"""Deterministic request-time Typed Feasibility Check assessment engine."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping, Sequence

from konsider.contracts import ContractError, validate_contract
from konsider.ingestion.tfc_release import TfcReleaseArtifacts

NO_MATCH_DISCLAIMER = "No supported-route match is not a permanent legal impossibility."
COMMON_STATUSES = (
    "EVALUATED",
    "INPUT_REQUIRED",
    "DESTINATION_EVIDENCE_INSUFFICIENT",
    "UNSUPPORTED",
    "NOT_APPLICABLE",
    "EVALUATION_ERROR",
)


class TfcAssessmentError(ValueError):
    """Raised for invalid assessment configuration without echoing profile values."""


@dataclass(frozen=True)
class ResolvedField:
    known: bool
    present: bool
    value: Any = None


@dataclass(frozen=True)
class TfcAssessmentRun:
    payload: dict[str, Any]
    assessment: dict[str, Any]
    snapshot: dict[str, Any] | None
    effective_context: dict[str, Any] | None


def _contract(payload: Any, schema: str, context: str) -> None:
    try:
        validate_contract(payload, schema, context=context, schema_generation=4)
    except ContractError as exc:
        raise TfcAssessmentError(str(exc)) from exc


def _canonical_hash(payload: Any) -> str:
    value = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _normalized_string(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_tree(value: Any, key: str | None = None) -> Any:
    if isinstance(value, Mapping):
        return {str(name): _normalize_tree(child, str(name)) for name, child in value.items()}
    if isinstance(value, list):
        return [_normalize_tree(child, key) for child in value]
    if isinstance(value, tuple):
        return [_normalize_tree(child, key) for child in value]
    if isinstance(value, str):
        normalized = _normalized_string(value)
        if key in {
            "country_code",
            "country_of_residence",
            "awarding_country",
            "currency",
        }:
            return normalized.upper()
        return normalized
    return value


def normalize_effective_context(
    context: Mapping[str, Any],
    *,
    selected_tfc_ids: Sequence[str],
    evaluation_date: str,
) -> dict[str, Any]:
    """Normalize known profile layers without inventing absent or unknown values."""

    normalized = {
        "schema_version": "tfc-engine-context-1.0",
        "applicant": _normalize_tree(copy.deepcopy(context.get("applicant", {}))),
        "household": _normalize_tree(copy.deepcopy(context.get("household", {}))),
        "scenario": _normalize_tree(copy.deepcopy(context.get("scenario", {}))),
        "selected_tfc_ids": list(selected_tfc_ids),
        "evaluation_date": evaluation_date,
    }
    applicant = normalized["applicant"]
    if "citizenships" in applicant:
        applicant["citizenships"] = sorted(
            {str(country).strip().upper() for country in applicant["citizenships"]}
        )
    scenario = normalized["scenario"]
    if "target_country_codes" in scenario:
        scenario["target_country_codes"] = sorted(
            {str(country).strip().upper() for country in scenario["target_country_codes"]}
        )
    for layer in (applicant, normalized["household"], scenario):
        layer.pop("profile_id", None)
        layer.pop("household_id", None)
        layer.pop("scenario_id", None)
        layer.pop("field_provenance", None)
    hash_value = {key: value for key, value in normalized.items() if key != "evaluation_date"}
    normalized["snapshot_hash"] = _canonical_hash(hash_value)
    return normalized


def _unknown_field_ids(context: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for namespace in ("applicant", "household", "scenario"):
        layer = context.get(namespace, {})
        if isinstance(layer, Mapping):
            result.update(str(value) for value in layer.get("unknown_fields", []))
    return result


def _resolve_field(context: Mapping[str, Any], field_id: str) -> ResolvedField:
    path = field_id.split(".")
    unknown_fields = _unknown_field_ids(context)
    if any(".".join(path[:index]) in unknown_fields for index in range(2, len(path) + 1)):
        return ResolvedField(False, False)
    value: Any = context
    for segment in path:
        if not isinstance(value, Mapping) or segment not in value:
            return ResolvedField(False, False)
        value = value[segment]
    if value is None or value == "UNKNOWN":
        return ResolvedField(False, False)
    if isinstance(value, Mapping):
        if value.get("state") == "UNKNOWN" or value.get("mapping_state") == "UNKNOWN":
            return ResolvedField(False, False)
        if value.get("state") == "ABSENT":
            return ResolvedField(True, False, value)
    if isinstance(value, (list, tuple, set, dict)) and not value:
        return ResolvedField(True, False, value)
    return ResolvedField(True, True, value)


def _condition_field_ids(condition: Mapping[str, Any]) -> list[str]:
    values = []
    if condition.get("field_id"):
        values.append(condition["field_id"])
    when = condition.get("when")
    if isinstance(when, Mapping):
        values.append(when["field_id"])
    return sorted(set(values))


def _compare(value: Any, operator: str, expected: Any) -> bool:
    if operator == "EQ":
        return value == expected
    if operator == "IN":
        return value in expected
    if operator == "GTE":
        return value >= expected
    if operator == "GT":
        return value > expected
    if operator == "LTE":
        return value <= expected
    if operator == "LT":
        return value < expected
    if operator == "BETWEEN":
        return expected[0] <= value <= expected[1]
    raise TfcAssessmentError("Unsupported condition operator for the declared field ID.")


def _taxonomy_code(value: Any) -> Any:
    return value.get("code") if isinstance(value, Mapping) else value


def _evaluate_atomic_condition(
    condition: Mapping[str, Any],
    context: Mapping[str, Any],
    thresholds: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    field_ids = _condition_field_ids(condition)
    blocking = bool(condition.get("blocking", True))
    condition_type = condition["condition_type"]
    when = condition.get("when")
    if isinstance(when, Mapping):
        resolved_when = _resolve_field(context, when["field_id"])
        if not resolved_when.known:
            status = "UNKNOWN"
        elif when["operator"] == "PRESENT":
            status = "MET" if resolved_when.present else "NOT_APPLICABLE"
        else:
            status = (
                "MET"
                if resolved_when.present
                and _compare(resolved_when.value, "EQ", when["expected_value"])
                else "NOT_APPLICABLE"
            )
        if status != "MET":
            return {
                "condition_id": condition["condition_id"],
                "field_ids": field_ids,
                "status": status,
                "blocking": blocking,
            }

    field_id = condition.get("field_id")
    resolved = _resolve_field(context, field_id) if field_id else ResolvedField(False, False)
    if condition_type == "FIELD_PRESENT":
        status = "UNKNOWN" if not resolved.known else ("MET" if resolved.present else "UNMET")
    elif condition_type == "FIELD_ABSENT":
        status = "UNKNOWN" if not resolved.known else ("MET" if not resolved.present else "UNMET")
    elif not resolved.known:
        status = "UNKNOWN"
    elif condition_type == "FIELD_EQUALS":
        status = "MET" if _compare(resolved.value, "EQ", condition["expected_value"]) else "UNMET"
    elif condition_type == "FIELD_IN_SET":
        status = "MET" if _compare(resolved.value, "IN", condition["expected_value"]) else "UNMET"
    elif condition_type == "THRESHOLD":
        threshold = thresholds.get(condition["threshold_id"])
        if threshold is None:
            raise TfcAssessmentError(f"Unknown threshold for field ID {field_id}.")
        status = (
            "MET"
            if _compare(resolved.value, condition["operator"], threshold["value"])
            else "UNMET"
        )
    elif condition_type == "RANGE":
        status = (
            "MET" if _compare(resolved.value, "BETWEEN", condition["expected_value"]) else "UNMET"
        )
    elif condition_type == "TAXONOMY_MEMBERSHIP":
        code = _taxonomy_code(resolved.value)
        status = (
            "UNKNOWN"
            if code is None
            else ("MET" if _compare(code, "IN", condition["expected_value"]) else "UNMET")
        )
    elif condition_type == "QUALIFICATION_LEVEL":
        qualifications = resolved.value if isinstance(resolved.value, list) else []
        levels = {item.get("level") for item in qualifications if isinstance(item, Mapping)}
        status = "MET" if levels & set(condition["expected_value"]) else "UNMET"
    elif condition_type == "JURISDICTION":
        values = resolved.value if isinstance(resolved.value, list) else [resolved.value]
        status = "MET" if set(values) & set(condition["expected_value"]) else "UNMET"
    elif condition_type == "CONDITIONAL_REQUIREMENT":
        status = "MET" if resolved.present else "UNMET"
    else:
        raise TfcAssessmentError(f"Unsupported condition type for field IDs {','.join(field_ids)}.")
    return {
        "condition_id": condition["condition_id"],
        "field_ids": field_ids,
        "status": status,
        "blocking": blocking,
    }


def evaluate_route_conditions(
    rule: Mapping[str, Any], context: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Evaluate a bounded rule vocabulary; no arbitrary expression execution is possible."""

    thresholds = {item["threshold_id"]: item for item in rule["thresholds"]}
    evaluations: dict[str, dict[str, Any]] = {}
    groups = []
    for condition in rule["conditions"]:
        if condition["condition_type"] == "GROUP":
            groups.append(condition)
            continue
        result = _evaluate_atomic_condition(condition, context, thresholds)
        evaluations[result["condition_id"]] = result
    for condition in groups:
        children = [evaluations.get(item) for item in condition.get("child_condition_ids", [])]
        if not children or any(child is None for child in children):
            raise TfcAssessmentError("Condition group references an unknown condition ID.")
        statuses = {child["status"] for child in children if child is not None}
        if condition.get("group_operator") == "OR":
            status = "MET" if "MET" in statuses else "UNKNOWN" if "UNKNOWN" in statuses else "UNMET"
        else:
            status = (
                "UNMET" if "UNMET" in statuses else "UNKNOWN" if "UNKNOWN" in statuses else "MET"
            )
        evaluations[condition["condition_id"]] = {
            "condition_id": condition["condition_id"],
            "field_ids": sorted(
                {
                    field_id
                    for child in children
                    if child is not None
                    for field_id in child["field_ids"]
                }
            ),
            "status": status,
            "blocking": bool(condition.get("blocking", True)),
        }
    ordered = [evaluations[condition["condition_id"]] for condition in rule["conditions"]]
    if rule.get("evaluation_boundary") == "CONDITIONAL_EXTERNAL_CONFIRMATION_REQUIRED":
        ordered.append(
            {
                "condition_id": "external_authority_confirmation",
                "field_ids": [],
                "status": "UNKNOWN",
                "blocking": True,
            }
        )
    return ordered


def _route_classification(conditions: Sequence[Mapping[str, Any]]) -> str:
    blocking = [row for row in conditions if row["blocking"]]
    if any(row["status"] == "UNMET" for row in blocking):
        return "NO_MATCH"
    if any(row["status"] == "UNKNOWN" for row in blocking):
        return "CONDITIONAL"
    return "MATCH"


def _is_effective(rule: Mapping[str, Any], evaluation_date: date) -> bool:
    period = rule["effective_period"]
    effective_to = period["effective_to"]
    return (
        date.fromisoformat(period["effective_from"]) <= evaluation_date
        and (effective_to is None or evaluation_date <= date.fromisoformat(effective_to))
        and evaluation_date <= date.fromisoformat(period["stale_after"])
    )


def _country_code(ranking: Mapping[str, Any]) -> str:
    if "country_code" in ranking:
        return str(ranking["country_code"])
    country = ranking.get("country")
    if isinstance(country, Mapping) and country.get("country_codes"):
        return str(country["country_codes"][0])
    raise TfcAssessmentError("A ranking row is missing its country identity.")


def _base_rank(ranking: Mapping[str, Any]) -> int:
    return int(ranking.get("base_rank", ranking.get("rank")))


def _affinity_score(ranking: Mapping[str, Any]) -> float:
    if "affinity_score" in ranking:
        return float(ranking["affinity_score"])
    return float(ranking.get("total_score", 0.0))


def _warning(
    code: str,
    *,
    tfc_id: str | None,
    country_code: str | None,
    record_ids: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "code": code,
        "tfc_id": tfc_id,
        "country_code": country_code,
        "record_ids": sorted(set(record_ids)),
    }


class TfcAssessmentEngine:
    """Evaluate immutable destination rules against one normalized request-scoped context."""

    def __init__(
        self,
        artifacts: TfcReleaseArtifacts,
        *,
        active_release_id: str,
        tfc_release_id: str,
    ) -> None:
        self.artifacts = artifacts
        self.active_release_id = active_release_id
        self.tfc_release_id = tfc_release_id
        self.definitions = {
            str(row.get("id", row.get("tfc_id"))): row for row in artifacts.catalog["definitions"]
        }
        self.policies = {row["tfc_id"]: row for row in artifacts.policy_bundles["policies"]}
        self.records = {row["record_id"]: row for row in artifacts.rule_evidence}
        self.support = {
            (row["tfc_id"], row["country_code"]): row
            for row in artifacts.rule_evidence
            if row["record_type"] == "DESTINATION_SUPPORT"
        }
        self.jurisdictions = {
            row["jurisdiction_id"]: row
            for row in artifacts.rule_evidence
            if row["record_type"] == "JURISDICTION"
        }
        self.sources = {row["source_id"]: row for row in artifacts.source_legal_manifest["sources"]}

    def _selected(self, selected_tfc_ids: Sequence[str]) -> tuple[str, ...]:
        if len(selected_tfc_ids) != len(set(selected_tfc_ids)):
            raise TfcAssessmentError("Selected TFC IDs must be unique.")
        unknown = sorted(set(selected_tfc_ids) - set(self.definitions))
        if unknown:
            raise TfcAssessmentError(f"Unknown TFC IDs: {','.join(unknown)}.")
        return tuple(
            str(definition.get("id", definition.get("tfc_id")))
            for definition in self.artifacts.catalog["definitions"]
            if str(definition.get("id", definition.get("tfc_id"))) in selected_tfc_ids
        )

    def _applicable(self, definition: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
        scenario = context["scenario"]
        if scenario.get("purpose") not in definition["applicable_purposes"]:
            return False
        if definition["requires_household_relocation"] and scenario.get(
            "relocation_composition"
        ) in {None, "APPLICANT_ONLY", "UNKNOWN"}:
            return False
        return True

    def _missing_required_fields(
        self, definition: Mapping[str, Any], context: Mapping[str, Any]
    ) -> list[str]:
        missing = []
        for requirement in definition["input_requirements"]:
            required = requirement["requirement"] == "ALWAYS_REQUIRED"
            if requirement["requirement"] == "CONDITIONALLY_REQUIRED":
                when_id = requirement.get("when_field_id")
                when = _resolve_field(context, when_id) if when_id else ResolvedField(False, False)
                required = when.known and when.value == requirement.get("when_equals")
            if required and not _resolve_field(context, requirement["field_id"]).known:
                missing.append(requirement["field_id"])
        return sorted(set(missing))

    def _current_rules(
        self,
        support: Mapping[str, Any],
        context: Mapping[str, Any],
        evaluation_date: date,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        warnings = []
        candidates = [self.records[record_id] for record_id in support["rule_record_ids"]]
        current = [row for row in candidates if _is_effective(row, evaluation_date)]
        if len(current) != len(candidates):
            warnings.append(
                _warning(
                    "RULE_FUTURE_EXPIRED_OR_STALE",
                    tfc_id=support["tfc_id"],
                    country_code=support["country_code"],
                    record_ids=[row["record_id"] for row in candidates if row not in current],
                )
            )
        if any(row["effective_period"]["conflict_status"] == "UNRESOLVED" for row in current):
            warnings.append(
                _warning(
                    "UNRESOLVED_AUTHORITY_CONFLICT",
                    tfc_id=support["tfc_id"],
                    country_code=support["country_code"],
                    record_ids=[
                        row["record_id"]
                        for row in current
                        if row["effective_period"]["conflict_status"] == "UNRESOLVED"
                    ],
                )
            )
            return [], warnings
        target_regions = set(context["scenario"].get("target_region_ids", []))
        scoped = []
        for row in current:
            jurisdiction = self.jurisdictions[row["jurisdiction_id"]]
            if jurisdiction["level"] == "COUNTRY" or row["jurisdiction_id"] in target_regions:
                scoped.append(row)
        overridden = {
            row["overrides_record_id"]
            for row in scoped
            if row.get("overrides_record_id") is not None
        }
        return [row for row in scoped if row["record_id"] not in overridden], warnings

    def _route_result(
        self,
        tfc_id: str,
        support: Mapping[str, Any],
        context: Mapping[str, Any],
        evaluation_date: date,
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
        rules, warnings = self._current_rules(support, context, evaluation_date)
        if not rules:
            return None, warnings, "NO_CURRENT_CONFLICT_FREE_RULE"
        routes = []
        for rule in sorted(rules, key=lambda row: (row["route_id"], row["record_id"])):
            conditions = evaluate_route_conditions(rule, context)
            routes.append(
                {
                    "route_id": rule["route_id"],
                    "route_name": rule["route_name"],
                    "jurisdiction_id": rule["jurisdiction_id"],
                    "classification": _route_classification(conditions),
                    "conditions": conditions,
                    "source_ids": sorted(
                        {reference["source_id"] for reference in rule["source_references"]}
                    ),
                    "effective_from": rule["effective_period"]["effective_from"],
                    "effective_to": rule["effective_period"]["effective_to"],
                    "evidence_quality": rule["evidence_quality"],
                }
            )
        clear = [row["route_id"] for row in routes if row["classification"] == "MATCH"]
        conditional = [row["route_id"] for row in routes if row["classification"] == "CONDITIONAL"]
        policy = self.policies[tfc_id]
        if clear:
            classification = "SUPPORTED_ROUTE_MATCH"
            matched = clear
            complete = False
        elif conditional:
            classification = "CONDITIONAL_ROUTE_MATCH"
            matched = conditional
            complete = False
        elif policy["negative_result_policy"] == "COMPLETE_INVENTORY_REQUIRED":
            classification = "NO_SUPPORTED_ROUTE_MATCH"
            matched = []
            complete = True
        else:
            return None, warnings, "NEGATIVE_RESULT_NOT_AUTHORIZED"
        return (
            {
                "result_type": "ROUTE_RULE",
                "match_classification": classification,
                "routes": routes,
                "matched_route_ids": sorted(set(matched)),
                "route_inventory_complete": complete,
                "legal_impossibility_disclaimer": NO_MATCH_DISCLAIMER,
            },
            warnings,
            None,
        )

    def _metric_value(
        self,
        field_id: str,
        expected_unit: str,
        expected_currency: str | None,
        expected_period: str,
        exchange_rate_policy: str,
        context: Mapping[str, Any],
    ) -> tuple[float, float, str] | None:
        resolved = _resolve_field(context, field_id)
        if not resolved.known:
            return None
        value = resolved.value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value), float(value), expected_unit
        if not isinstance(value, Mapping):
            raise TfcAssessmentError(
                f"Metric input requires a numeric range for field ID {field_id}."
            )
        unit = str(value.get("unit", expected_unit))
        if unit != expected_unit:
            raise TfcAssessmentError(
                f"Metric input has an incompatible unit for field ID {field_id}."
            )
        currency = value.get("currency", expected_currency)
        if currency != expected_currency:
            if exchange_rate_policy == "NONE":
                raise TfcAssessmentError(
                    f"Metric input requires an approved currency policy for field ID {field_id}."
                )
            raise TfcAssessmentError(
                f"Metric input requires an unavailable approved exchange table for field ID {field_id}."
            )
        period = value.get("period", expected_period)
        if period != expected_period:
            raise TfcAssessmentError(
                f"Metric input has an incompatible period for field ID {field_id}."
            )
        if "value" in value:
            minimum = maximum = float(value["value"])
        else:
            minimum = float(value["minimum"])
            maximum = float(value["maximum"])
        if not math.isfinite(minimum) or not math.isfinite(maximum) or minimum > maximum:
            raise TfcAssessmentError(f"Metric input range is invalid for field ID {field_id}.")
        return minimum, maximum, unit

    def _round(self, value: float, rounding: Mapping[str, Any]) -> float:
        if rounding["mode"] == "NONE":
            return value
        quantum = Decimal(1).scaleb(-int(rounding["decimal_places"]))
        return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))

    def _metric_result(
        self,
        support: Mapping[str, Any],
        context: Mapping[str, Any],
        evaluation_date: date,
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
        rules, warnings = self._current_rules(support, context, evaluation_date)
        formulas = [row for row in rules if row["record_type"] == "METRIC_FORMULA"]
        if not formulas:
            return None, warnings, "NO_CURRENT_CONFLICT_FREE_RULE"
        formula = sorted(formulas, key=lambda row: row["record_id"])[-1]
        locality_ids = context["scenario"].get("target_locality_ids", [])
        if formula["locality_requirement"] == "REQUIRED_TARGET_LOCALITY" and not locality_ids:
            return None, warnings, "TARGET_LOCALITY_REQUIRED"
        components = []
        minimum = 0.0
        maximum = 0.0
        for component in formula["components"]:
            resolved = self._metric_value(
                component["field_id"],
                component["unit"],
                formula["output_currency"],
                formula["output_period"],
                formula["exchange_rate_policy"],
                context,
            )
            if resolved is None:
                return None, warnings, "METRIC_COMPONENT_MISSING"
            component_minimum, component_maximum, unit = resolved
            contribution_minimum = component_minimum * component["coefficient"]
            contribution_maximum = component_maximum * component["coefficient"]
            minimum += contribution_minimum
            maximum += contribution_maximum
            components.append(
                {
                    "component_id": component["component_id"],
                    "field_id": component["field_id"],
                    "status": "EVALUATED",
                    "contribution_minimum": self._round(contribution_minimum, formula["rounding"]),
                    "contribution_maximum": self._round(contribution_maximum, formula["rounding"]),
                    "unit": unit,
                }
            )
        minimum = self._round(minimum, formula["rounding"])
        maximum = self._round(maximum, formula["rounding"])
        return (
            {
                "result_type": "SCENARIO_METRIC",
                "metric_id": formula["metric_id"],
                "formula_type": formula["formula_type"],
                "value": minimum if minimum == maximum else None,
                "minimum": minimum,
                "maximum": maximum,
                "unit": formula["output_unit"],
                "currency": formula["output_currency"],
                "period": formula["output_period"],
                "components": components,
                "assumptions": sorted(
                    set(formula["assumptions"])
                    | set(context["scenario"].get("metric_assumptions", []))
                ),
                "rounding": formula["rounding"],
                "locality_id": locality_ids[0] if locality_ids else None,
                "source_ids": sorted(
                    {reference["source_id"] for reference in formula["source_references"]}
                ),
                "effective_from": formula["effective_period"]["effective_from"],
                "effective_to": formula["effective_period"]["effective_to"],
                "evidence_quality": formula["evidence_quality"],
            },
            warnings,
            None,
        )

    def _support_outcome(
        self,
        tfc_id: str,
        country_code: str,
        context: Mapping[str, Any],
        evaluation_date: date,
    ) -> dict[str, Any]:
        definition = self.definitions[tfc_id]
        if not self._applicable(definition, context):
            return self._outcome(
                tfc_id, country_code, "NOT_APPLICABLE", ["SCENARIO_NOT_APPLICABLE"]
            )
        support = self.support[(tfc_id, country_code)]
        support_status = support["support_status"]
        if support_status == "UNSUPPORTED":
            return self._outcome(tfc_id, country_code, "UNSUPPORTED", ["DESTINATION_NOT_SUPPORTED"])
        if support_status == "NOT_APPLICABLE_NATIONAL":
            return self._outcome(
                tfc_id,
                country_code,
                "NOT_APPLICABLE",
                ["DESTINATION_NOT_APPLICABLE_NATIONAL"],
            )
        if support_status in {"EVIDENCE_INSUFFICIENT", "LEGALLY_BLOCKED", "STALE"}:
            reason = {
                "EVIDENCE_INSUFFICIENT": "DESTINATION_EVIDENCE_CONFLICT",
                "LEGALLY_BLOCKED": "DESTINATION_SOURCE_LEGALLY_BLOCKED",
                "STALE": "DESTINATION_RULE_STALE",
            }[support_status]
            warning = _warning(
                reason,
                tfc_id=tfc_id,
                country_code=country_code,
                record_ids=support["rule_record_ids"],
            )
            return self._outcome(
                tfc_id,
                country_code,
                "DESTINATION_EVIDENCE_INSUFFICIENT",
                [reason],
                warnings=[warning],
            )
        missing = self._missing_required_fields(definition, context)
        if missing:
            return self._outcome(
                tfc_id,
                country_code,
                "INPUT_REQUIRED",
                ["PROFILE_FIELDS_MISSING"],
                input_required_fields=missing,
            )
        if definition["result_family"] == "RULE_ROUTE_MATCH":
            result, warnings, failure = self._route_result(
                tfc_id, support, context, evaluation_date
            )
        else:
            result, warnings, failure = self._metric_result(support, context, evaluation_date)
        if result is None:
            if failure in {"METRIC_COMPONENT_MISSING", "TARGET_LOCALITY_REQUIRED"}:
                missing = self._missing_required_fields(definition, context)
                if failure == "TARGET_LOCALITY_REQUIRED":
                    missing = sorted(set((*missing, "scenario.target_locality_ids")))
                return self._outcome(
                    tfc_id,
                    country_code,
                    "INPUT_REQUIRED",
                    [failure],
                    input_required_fields=missing or definition["input_field_ids"],
                    warnings=warnings,
                )
            return self._outcome(
                tfc_id,
                country_code,
                "DESTINATION_EVIDENCE_INSUFFICIENT",
                [failure or "DESTINATION_RULE_UNAVAILABLE"],
                warnings=warnings,
            )
        reason = (
            {
                "SUPPORTED_ROUTE_MATCH": "ROUTE_MATCHED",
                "CONDITIONAL_ROUTE_MATCH": "ROUTE_CONDITIONALLY_MATCHED",
                "NO_SUPPORTED_ROUTE_MATCH": "NO_SUPPORTED_ROUTE_MATCH",
            }[result["match_classification"]]
            if result["result_type"] == "ROUTE_RULE"
            else "SCENARIO_METRIC_CALCULATED"
        )
        return self._outcome(
            tfc_id,
            country_code,
            "EVALUATED",
            [reason],
            result=result,
            warnings=warnings,
        )

    def _outcome(
        self,
        tfc_id: str,
        country_code: str,
        common_status: str,
        reason_codes: Sequence[str],
        *,
        input_required_fields: Sequence[str] = (),
        result: Mapping[str, Any] | None = None,
        warnings: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        return {
            "tfc_id": tfc_id,
            "country_code": country_code,
            "common_status": common_status,
            "reason_codes": sorted(set(reason_codes)),
            "input_required_fields": sorted(set(input_required_fields)),
            "result": copy.deepcopy(result),
            "warnings": [copy.deepcopy(row) for row in warnings],
        }

    def _no_context_assessment(self, selected: Sequence[str], filter_mode: str) -> dict[str, Any]:
        return {
            "schema_version": "tfc-engine-assessment-1.0",
            "profile_context_status": "NO_PROFILE_CONTEXT",
            "execution_status": "NOT_EXECUTED_NO_CONTEXT",
            "filter_mode": filter_mode,
            "selected_tfc_ids": list(selected),
            "input_required_fields": sorted(
                {
                    requirement["field_id"]
                    for tfc_id in selected
                    for requirement in self.definitions[tfc_id]["input_requirements"]
                    if requirement["requirement"] == "ALWAYS_REQUIRED"
                }
            ),
            "status_counts": {status: 0 for status in COMMON_STATUSES},
            "matched_route_count": 0,
            "metric_result_count": 0,
            "no_change_affinity": True,
            "warnings": [
                _warning(
                    "PROFILE_CONTEXT_ABSENT",
                    tfc_id=None,
                    country_code=None,
                )
            ],
            "countries": [],
        }

    def _snapshot(
        self,
        context: Mapping[str, Any],
        selected: Sequence[str],
        evaluation_date: str,
        rankings: Sequence[Mapping[str, Any]],
        assessment: Mapping[str, Any],
    ) -> dict[str, Any]:
        ordering = [
            {
                "country_code": _country_code(row),
                "base_rank": _base_rank(row),
                "affinity_score": _affinity_score(row),
            }
            for row in rankings
        ]
        source_ids = {
            source_id
            for country in assessment["countries"]
            for outcome in country["outcomes"]
            if outcome["result"] is not None
            for source_id in (
                outcome["result"].get("source_ids", [])
                if outcome["result"]["result_type"] == "SCENARIO_METRIC"
                else {
                    source_id
                    for route in outcome["result"]["routes"]
                    for source_id in route["source_ids"]
                }
            )
        }
        assumptions = sorted(
            {
                assumption
                for country in assessment["countries"]
                for outcome in country["outcomes"]
                if outcome["result"] is not None
                and outcome["result"]["result_type"] == "SCENARIO_METRIC"
                for assumption in outcome["result"]["assumptions"]
            }
        )
        snapshot_hash = context["snapshot_hash"]
        snapshot = {
            "schema_version": "tfc-scenario-snapshot-1.0",
            "snapshot_id": f"snapshot:{snapshot_hash.removeprefix('sha256:')[:16]}:{evaluation_date}",
            "active_release_id": self.active_release_id,
            "tfc_release_id": self.tfc_release_id,
            "policy_versions": {
                tfc_id: self.policies[tfc_id]["policy_version"] for tfc_id in selected
            },
            "source_versions": {
                source_id: self.sources[source_id]["checksum"] for source_id in sorted(source_ids)
            },
            "effective_profile_context_hash": snapshot_hash,
            "selected_tfc_ids": list(selected),
            "evaluation_date": evaluation_date,
            "base_ranking_reference": {
                "release_id": self.active_release_id,
                "country_count": len(rankings),
                "ordering_checksum": _canonical_hash(ordering),
            },
            "country_outcomes": copy.deepcopy(assessment["countries"]),
            "assumptions": assumptions,
            "warnings": copy.deepcopy(assessment["warnings"]),
            "persisted_server_side": False,
        }
        _contract(snapshot, "tfc-scenario-snapshot", "TFC scenario snapshot")
        return snapshot

    def assess_ranking_payload(
        self,
        canonical_payload: Mapping[str, Any],
        *,
        context: Mapping[str, Any] | None,
        selected_tfc_ids: Sequence[str],
        evaluation_date: str,
        filter_mode: str = "ASSESS_ONLY",
    ) -> TfcAssessmentRun:
        """Assess a deep copy of canonical ranking output; the input is never mutated."""

        if filter_mode not in {"ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH"}:
            raise TfcAssessmentError("Unsupported feasibility filter mode.")
        selected = self._selected(selected_tfc_ids)
        canonical_copy = copy.deepcopy(canonical_payload)
        rankings = canonical_copy.get("rankings")
        if not isinstance(rankings, list):
            raise TfcAssessmentError("Canonical payload is missing rankings.")
        if not selected:
            assessment = {
                "schema_version": "tfc-engine-assessment-1.0",
                "profile_context_status": (
                    "NO_PROFILE_CONTEXT" if context is None else "COMPLETE_PROFILE_CONTEXT"
                ),
                "execution_status": "NO_TFC_SELECTED",
                "filter_mode": "ASSESS_ONLY",
                "selected_tfc_ids": [],
                "input_required_fields": [],
                "status_counts": {status: 0 for status in COMMON_STATUSES},
                "matched_route_count": 0,
                "metric_result_count": 0,
                "no_change_affinity": True,
                "warnings": [],
                "countries": [],
            }
            _contract(assessment, "tfc-engine-assessment", "no-TFC assessment")
            return TfcAssessmentRun(canonical_copy, assessment, None, None)
        if filter_mode == "REQUIRE_SUPPORTED_MATCH":
            filterable = [
                tfc_id
                for tfc_id in selected
                if self.definitions[tfc_id]["filter_capability"]
                == "REQUIRE_SUPPORTED_MATCH_ALLOWED"
            ]
            if not filterable:
                raise TfcAssessmentError("Selected TFC IDs do not permit route filtering.")
            if any(
                self.policies[tfc_id]["filter_non_match_behavior"] != "EXCLUDE_WITH_REASON"
                for tfc_id in filterable
            ):
                raise TfcAssessmentError(
                    "Selected TFC IDs do not define non-match filtering behavior."
                )
        if context is None:
            assessment = self._no_context_assessment(selected, filter_mode)
            _contract(assessment, "tfc-engine-assessment", "no-context TFC assessment")
            return TfcAssessmentRun(canonical_copy, assessment, None, None)
        normalized = normalize_effective_context(
            context,
            selected_tfc_ids=selected,
            evaluation_date=evaluation_date,
        )
        day = date.fromisoformat(evaluation_date)
        countries = []
        all_outcomes = []
        required_fields: set[str] = set()
        warnings = []
        for ranking in rankings:
            country_code = _country_code(ranking)
            outcomes = [
                self._support_outcome(tfc_id, country_code, normalized, day) for tfc_id in selected
            ]
            for outcome in outcomes:
                required_fields.update(outcome["input_required_fields"])
                warnings.extend(outcome["warnings"])
            all_outcomes.extend(outcomes)
            score = _affinity_score(ranking)
            countries.append(
                {
                    "country_code": country_code,
                    "base_rank": _base_rank(ranking),
                    "filtered_rank": None,
                    "affinity_score_before": score,
                    "affinity_score_after": score,
                    "no_change_affinity": True,
                    "outcomes": outcomes,
                }
            )
        status_counts = Counter(outcome["common_status"] for outcome in all_outcomes)
        matched_route_count = sum(
            len(outcome["result"]["matched_route_ids"])
            for outcome in all_outcomes
            if outcome["result"] is not None
            and outcome["result"]["result_type"] == "ROUTE_RULE"
            and outcome["result"]["match_classification"] == "SUPPORTED_ROUTE_MATCH"
        )
        metric_result_count = sum(
            outcome["result"] is not None and outcome["result"]["result_type"] == "SCENARIO_METRIC"
            for outcome in all_outcomes
        )
        profile_status = (
            "PARTIAL_PROFILE_CONTEXT" if required_fields else "COMPLETE_PROFILE_CONTEXT"
        )
        assessment = {
            "schema_version": "tfc-engine-assessment-1.0",
            "profile_context_status": profile_status,
            "execution_status": "EXECUTED",
            "filter_mode": filter_mode,
            "selected_tfc_ids": list(selected),
            "input_required_fields": sorted(required_fields),
            "status_counts": {status: status_counts[status] for status in COMMON_STATUSES},
            "matched_route_count": matched_route_count,
            "metric_result_count": metric_result_count,
            "no_change_affinity": True,
            "warnings": sorted(
                {json.dumps(row, sort_keys=True): row for row in warnings}.values(),
                key=lambda row: (
                    row["code"],
                    row["tfc_id"] or "",
                    row["country_code"] or "",
                ),
            ),
            "countries": countries,
        }
        if filter_mode == "REQUIRE_SUPPORTED_MATCH":
            filterable = {
                tfc_id
                for tfc_id in selected
                if self.definitions[tfc_id]["filter_capability"]
                == "REQUIRE_SUPPORTED_MATCH_ALLOWED"
            }
            survivors = []
            surviving_codes = []
            for ranking, country in zip(rankings, countries, strict=True):
                passes = all(
                    outcome["common_status"] == "EVALUATED"
                    and outcome["result"] is not None
                    and outcome["result"]["result_type"] == "ROUTE_RULE"
                    and outcome["result"]["match_classification"] == "SUPPORTED_ROUTE_MATCH"
                    for outcome in country["outcomes"]
                    if outcome["tfc_id"] in filterable
                )
                if passes:
                    row = copy.deepcopy(ranking)
                    row["rank"] = len(survivors) + 1
                    row["base_rank"] = _base_rank(ranking)
                    survivors.append(row)
                    surviving_codes.append(country["country_code"])
            canonical_copy["rankings"] = survivors
            filtered_positions = {code: index + 1 for index, code in enumerate(surviving_codes)}
            for country in countries:
                country["filtered_rank"] = filtered_positions.get(country["country_code"])
        assessments = canonical_copy.setdefault("assessments", {})
        assessments["feasibility"] = copy.deepcopy(assessment)
        snapshot = self._snapshot(normalized, selected, evaluation_date, rankings, assessment)
        _contract(assessment, "tfc-engine-assessment", "TFC domain assessment")
        return TfcAssessmentRun(canonical_copy, assessment, snapshot, normalized)


def benchmark_tfc_assessment(
    engine: TfcAssessmentEngine,
    canonical_payload: Mapping[str, Any],
    context: Mapping[str, Any],
    selected_tfc_ids: Sequence[str],
    *,
    iterations: int = 20,
) -> dict[str, Any]:
    """Measure deterministic in-process assessment without logging request/profile data."""

    durations = []
    for _ in range(iterations):
        started = time.perf_counter()
        engine.assess_ranking_payload(
            canonical_payload,
            context=context,
            selected_tfc_ids=selected_tfc_ids,
            evaluation_date="2026-08-05",
        )
        durations.append((time.perf_counter() - started) * 1000)
    ordered = sorted(durations)
    p95_index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
    return {
        "iterations": iterations,
        "country_count": len(canonical_payload["rankings"]),
        "tfc_count": len(selected_tfc_ids),
        "median_ms": round(statistics.median(durations), 3),
        "p95_ms": round(ordered[p95_index], 3),
        "maximum_ms": round(max(durations), 3),
    }


__all__ = [
    "NO_MATCH_DISCLAIMER",
    "TfcAssessmentEngine",
    "TfcAssessmentError",
    "TfcAssessmentRun",
    "benchmark_tfc_assessment",
    "evaluate_route_conditions",
    "normalize_effective_context",
]
