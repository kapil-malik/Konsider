"""Typed Opportunity Filter contracts and cross-artifact validation.

Phase 6D defines these contracts without activating filters in the current release or API.
"""

from __future__ import annotations

from collections import Counter
from enum import StrEnum
from typing import Any, Iterable, Mapping

from konsider.contracts import ContractError, validate_contract


class OpportunityFilterContractError(ValueError):
    """Raised when individually valid OFC artifacts contradict one another."""


class OpportunityFilterState(StrEnum):
    VERIFIED_STRONG_SIGNAL = "VERIFIED_STRONG_SIGNAL"
    STRONG_SIGNAL_NOT_ESTABLISHED = "STRONG_SIGNAL_NOT_ESTABLISHED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class OpportunityFilterCategory(StrEnum):
    CAREER = "CAREER"
    EDUCATION = "EDUCATION"


class OpportunityFilterConfidenceBand(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OpportunityFilterConfidenceTier(StrEnum):
    HIGH_CONFIDENCE_OBSERVED_HARMONISED = "HIGH_CONFIDENCE_OBSERVED_HARMONISED"
    HIGH_CONFIDENCE_OBSERVED_NATIONAL = "HIGH_CONFIDENCE_OBSERVED_NATIONAL"
    HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET = "HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET"
    MEDIUM_CONFIDENCE_MODELLED_HARMONISED = "MEDIUM_CONFIDENCE_MODELLED_HARMONISED"
    MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK = "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK"
    LOW_CONFIDENCE_SUPPLEMENTAL = "LOW_CONFIDENCE_SUPPLEMENTAL"


class OpportunityFilterReasonCode(StrEnum):
    SCALE_AND_SHARE_ROUTE_PASSED = "SCALE_AND_SHARE_ROUTE_PASSED"
    EXCEPTIONAL_SCALE_ROUTE_PASSED = "EXCEPTIONAL_SCALE_ROUTE_PASSED"
    EXCEPTIONAL_SPECIALIZATION_ROUTE_PASSED = "EXCEPTIONAL_SPECIALIZATION_ROUTE_PASSED"
    SKILLED_TRADES_ROUTE_PASSED = "SKILLED_TRADES_ROUTE_PASSED"
    CONSTRUCTION_ROUTE_PASSED = "CONSTRUCTION_ROUTE_PASSED"
    SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED = "SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED"
    TOP_100_INSTITUTION_ROUTE_PASSED = "TOP_100_INSTITUTION_ROUTE_PASSED"
    TOP_300_BREADTH_ROUTE_PASSED = "TOP_300_BREADTH_ROUTE_PASSED"
    OUTPUT_AND_BREADTH_ROUTE_PASSED = "OUTPUT_AND_BREADTH_ROUTE_PASSED"
    COMPLETE_EVIDENCE_BELOW_STRONG_THRESHOLD = "COMPLETE_EVIDENCE_BELOW_STRONG_THRESHOLD"
    SCALE_FLOOR_NOT_MET = "SCALE_FLOOR_NOT_MET"
    BREADTH_THRESHOLD_NOT_MET = "BREADTH_THRESHOLD_NOT_MET"
    NO_APPROVED_STRONG_ROUTE_PASSED = "NO_APPROVED_STRONG_ROUTE_PASSED"
    SOURCE_MISSING = "SOURCE_MISSING"
    EVIDENCE_STALE = "EVIDENCE_STALE"
    UNSUPPORTED_TAXONOMY = "UNSUPPORTED_TAXONOMY"
    INSUFFICIENT_GRANULARITY = "INSUFFICIENT_GRANULARITY"
    CROSSWALK_INCOMPLETE = "CROSSWALK_INCOMPLETE"
    INCOMPATIBLE_NUMERATOR_DENOMINATOR = "INCOMPATIBLE_NUMERATOR_DENOMINATOR"
    SOURCE_LEGALLY_BLOCKED = "SOURCE_LEGALLY_BLOCKED"
    COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE = "COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE"
    INSTITUTION_IDENTITY_UNRESOLVED = "INSTITUTION_IDENTITY_UNRESOLVED"
    SOURCE_DEPENDENCY_UNAVAILABLE = "SOURCE_DEPENDENCY_UNAVAILABLE"
    CONFLICTING_EVIDENCE_UNRESOLVED = "CONFLICTING_EVIDENCE_UNRESOLVED"


POSITIVE_REASON_CODES = frozenset(
    {
        OpportunityFilterReasonCode.SCALE_AND_SHARE_ROUTE_PASSED,
        OpportunityFilterReasonCode.EXCEPTIONAL_SCALE_ROUTE_PASSED,
        OpportunityFilterReasonCode.EXCEPTIONAL_SPECIALIZATION_ROUTE_PASSED,
        OpportunityFilterReasonCode.SKILLED_TRADES_ROUTE_PASSED,
        OpportunityFilterReasonCode.CONSTRUCTION_ROUTE_PASSED,
        OpportunityFilterReasonCode.SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED,
        OpportunityFilterReasonCode.TOP_100_INSTITUTION_ROUTE_PASSED,
        OpportunityFilterReasonCode.TOP_300_BREADTH_ROUTE_PASSED,
        OpportunityFilterReasonCode.OUTPUT_AND_BREADTH_ROUTE_PASSED,
    }
)
NOT_ESTABLISHED_REASON_CODES = frozenset(
    {
        OpportunityFilterReasonCode.COMPLETE_EVIDENCE_BELOW_STRONG_THRESHOLD,
        OpportunityFilterReasonCode.SCALE_FLOOR_NOT_MET,
        OpportunityFilterReasonCode.BREADTH_THRESHOLD_NOT_MET,
        OpportunityFilterReasonCode.NO_APPROVED_STRONG_ROUTE_PASSED,
    }
)
INSUFFICIENT_REASON_CODES = frozenset(OpportunityFilterReasonCode) - (
    POSITIVE_REASON_CODES | NOT_ESTABLISHED_REASON_CODES
)

EXPECTED_RELEASE_ARTIFACTS = {
    "CATALOG": "opportunity-filter-catalog.json",
    "COUNTRY_EVIDENCE": "opportunity-filter-evidence.jsonl",
    "SOURCE_MANIFEST": "opportunity-filter-source-manifest.json",
    "THRESHOLD_POLICIES": "opportunity-filter-threshold-policies.json",
    "EVIDENCE_POLICY": "opportunity-filter-evidence-policy.json",
    "COVERAGE_SUMMARY": "opportunity-filter-coverage-summary.json",
}


def _contract(
    payload: Any, schema_name: str, context: str, *, generation: int | None = None
) -> None:
    selected_generation = generation or 3
    if isinstance(payload, Mapping) and payload.get("schema_version") in {
        "konsider-release-5.2",
        "opportunity-filter-catalog-2.0",
        "opportunity-filter-definition-2.0",
    }:
        selected_generation = 5
    try:
        validate_contract(
            payload, schema_name, context=context, schema_generation=selected_generation
        )
    except ContractError as exc:
        raise OpportunityFilterContractError(str(exc)) from exc


def validate_opportunity_filter_definition(definition: Mapping[str, Any]) -> None:
    """Validate one filter definition and its filter-only product role."""

    _contract(definition, "opportunity-filter-definition", "Opportunity Filter definition")


def validate_opportunity_filter_catalog(catalog: Mapping[str, Any]) -> None:
    """Validate the sibling OFC catalog and its cross-definition identities."""

    _contract(catalog, "opportunity-filter-catalog", "Opportunity Filter catalog")
    definitions = catalog["definitions"]
    ids = [row["id"] for row in definitions]
    order_key = (
        "sortOrder"
        if catalog["schema_version"] == "opportunity-filter-catalog-2.0"
        else "sort_order"
    )
    orders = [row[order_key] for row in definitions]
    if len(ids) != len(set(ids)):
        raise OpportunityFilterContractError("Opportunity Filter IDs must be unique.")
    if len(orders) != len(set(orders)):
        raise OpportunityFilterContractError("Opportunity Filter sort orders must be unique.")
    definition_generation = (
        5 if catalog["schema_version"] == "opportunity-filter-catalog-2.0" else 3
    )
    for definition in definitions:
        _contract(
            definition,
            "opportunity-filter-definition",
            "Opportunity Filter definition",
            generation=definition_generation,
        )
    if catalog["activation_status"] == "ACTIVE":
        if len(definitions) != 9 or not all(row["active"] for row in definitions):
            raise OpportunityFilterContractError(
                "An active Opportunity Filter catalog must contain exactly nine active definitions."
            )
    elif any(row["active"] for row in definitions):
        raise OpportunityFilterContractError(
            "A contracts-only catalog cannot activate Opportunity Filters."
        )


def validate_opportunity_filter_evidence(row: Mapping[str, Any]) -> None:
    """Validate one country result, including state/reason and route integrity."""

    _contract(row, "opportunity-filter-evidence", "Opportunity Filter evidence")
    state = OpportunityFilterState(row["state"])
    reasons = {OpportunityFilterReasonCode(code) for code in row["reason_codes"]}
    expected_reasons = {
        OpportunityFilterState.VERIFIED_STRONG_SIGNAL: POSITIVE_REASON_CODES,
        OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED: NOT_ESTABLISHED_REASON_CODES,
        OpportunityFilterState.INSUFFICIENT_EVIDENCE: INSUFFICIENT_REASON_CODES,
    }[state]
    if not reasons or not reasons.issubset(expected_reasons):
        raise OpportunityFilterContractError(
            f"Reason codes are inconsistent with public state {state}."
        )

    establishing = set(row["establishing_route_ids"])
    evaluated = set(row["evaluated_route_ids"])
    if not establishing.issubset(evaluated):
        raise OpportunityFilterContractError("Establishing routes must be evaluated routes.")
    passed_routes = {result["route_id"] for result in row["threshold_results"] if result["passed"]}
    if state == OpportunityFilterState.VERIFIED_STRONG_SIGNAL and not establishing.issubset(
        passed_routes
    ):
        raise OpportunityFilterContractError(
            "Every establishing route must have a passing threshold result."
        )
    if state != OpportunityFilterState.VERIFIED_STRONG_SIGNAL and establishing:
        raise OpportunityFilterContractError(
            "Only verified strong signals may carry establishing routes."
        )

    if OpportunityFilterReasonCode.SKILLED_TRADES_ROUTE_PASSED in reasons and establishing != {
        "skilled_trades"
    }:
        raise OpportunityFilterContractError(
            "The skilled-trades reason requires only the skilled_trades route."
        )
    if OpportunityFilterReasonCode.CONSTRUCTION_ROUTE_PASSED in reasons and establishing != {
        "construction"
    }:
        raise OpportunityFilterContractError(
            "The construction reason requires only the construction route."
        )
    if (
        OpportunityFilterReasonCode.SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED in reasons
        and establishing != {"skilled_trades", "construction"}
    ):
        raise OpportunityFilterContractError(
            "The combined route reason requires skilled_trades and construction."
        )


def validate_opportunity_filter_evidence_matrix(
    catalog: Mapping[str, Any],
    evidence_rows: Iterable[Mapping[str, Any]],
    country_codes: Iterable[str],
) -> None:
    """Require one explicit state for every declared filter-country pair."""

    validate_opportunity_filter_catalog(catalog)
    rows = list(evidence_rows)
    countries = tuple(country_codes)
    if len(countries) != len(set(countries)):
        raise OpportunityFilterContractError("Country codes must be unique.")
    definitions = {row["id"]: row for row in catalog["definitions"]}
    actual: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in rows:
        validate_opportunity_filter_evidence(row)
        pair = (row["filter_id"], row["country_code"])
        if pair in actual:
            raise OpportunityFilterContractError(
                f"Duplicate Opportunity Filter country state: {pair[0]}/{pair[1]}."
            )
        definition = definitions.get(row["filter_id"])
        if definition is None or row["country_code"] not in countries:
            raise OpportunityFilterContractError(
                f"Undeclared filter-country evidence pair: {pair[0]}/{pair[1]}."
            )
        for field in (
            "evidence_policy_version",
            "threshold_policy_version",
            "source_bundle_version",
        ):
            if row[field] != definition[field]:
                raise OpportunityFilterContractError(
                    f"Evidence {field} disagrees for {pair[0]}/{pair[1]}."
                )
        actual[pair] = row
    expected = {(filter_id, country) for filter_id in definitions for country in countries}
    if set(actual) != expected:
        missing = sorted(expected - set(actual))
        raise OpportunityFilterContractError(
            f"Opportunity Filter evidence matrix is incomplete; missing {missing[:3]}."
        )


def validate_opportunity_filter_assessment(assessment: Mapping[str, Any]) -> None:
    """Validate the future sibling assessment without exposing it through API v2."""

    _contract(assessment, "opportunity-filter-assessment", "Opportunity Filter assessment")
    selected = set(assessment["selected_filter_ids"])
    per_filter = {row["filter_id"]: row for row in assessment["per_filter"]}
    if len(per_filter) != len(assessment["per_filter"]) or set(per_filter) != selected:
        raise OpportunityFilterContractError(
            "Per-filter assessments must match selected filter IDs exactly."
        )
    if (
        assessment["passing_country_count"] + assessment["excluded_country_count"]
        != assessment["input_country_count"]
    ):
        raise OpportunityFilterContractError("Passing and excluded counts must reconcile.")
    if sum(assessment["excluded_counts_by_state"].values()) != assessment["excluded_country_count"]:
        raise OpportunityFilterContractError("Response exclusion-state counts must reconcile.")
    countries = assessment["countries"]
    if len(countries) != assessment["input_country_count"]:
        raise OpportunityFilterContractError("Country assessments must cover the input universe.")
    if len({row["country_code"] for row in countries}) != len(countries):
        raise OpportunityFilterContractError("Country assessments must be unique.")

    passing = 0
    for country in countries:
        states = {row["filter_id"]: row for row in country["filter_states"]}
        if len(states) != len(country["filter_states"]) or set(states) != selected:
            raise OpportunityFilterContractError(
                "Each country must carry exactly one state for every selected filter."
            )
        expected_pass = all(row["passes"] for row in states.values())
        if country["passes"] != expected_pass:
            raise OpportunityFilterContractError(
                "Country pass state violates strict AND semantics."
            )
        passing += int(country["passes"])
    if passing != assessment["passing_country_count"]:
        raise OpportunityFilterContractError("Country pass states do not reconcile with totals.")

    for filter_id, item in per_filter.items():
        states = [row["filter_states"] for row in countries]
        filter_states = [
            next(cell for cell in country_states if cell["filter_id"] == filter_id)
            for country_states in states
        ]
        counts = Counter(cell["state"] for cell in filter_states)
        if (
            item["input_country_count"] != len(countries)
            or item["passing_country_count"]
            != counts[OpportunityFilterState.VERIFIED_STRONG_SIGNAL]
        ):
            raise OpportunityFilterContractError(f"Per-filter counts disagree for {filter_id}.")
        if item["excluded_counts_by_state"] != {
            OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED: counts[
                OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED
            ],
            OpportunityFilterState.INSUFFICIENT_EVIDENCE: counts[
                OpportunityFilterState.INSUFFICIENT_EVIDENCE
            ],
        }:
            raise OpportunityFilterContractError(
                f"Per-filter state counts disagree for {filter_id}."
            )

    if not selected:
        if assessment["passing_country_count"] != assessment["input_country_count"]:
            raise OpportunityFilterContractError("No filters must preserve every input country.")
        if any(not row["passes"] or row["filtered_rank"] != row["base_rank"] for row in countries):
            raise OpportunityFilterContractError(
                "No-filter assessments must preserve pass state and rank exactly."
            )


def validate_opportunity_filter_coverage_summary(summary: Mapping[str, Any]) -> None:
    """Reconcile assessable and tri-state counts for each declared filter."""

    _contract(summary, "opportunity-filter-coverage-summary", "OFC coverage summary")
    country_count = summary["stable_country_count"]
    for filter_id, coverage in summary["filters"].items():
        counts = coverage["state_counts"]
        if sum(counts.values()) != country_count:
            raise OpportunityFilterContractError(
                f"Coverage state counts do not reconcile for {filter_id}."
            )
        if coverage["assessable_count"] != (
            counts[OpportunityFilterState.VERIFIED_STRONG_SIGNAL]
            + counts[OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED]
        ):
            raise OpportunityFilterContractError(
                f"Assessable count does not reconcile for {filter_id}."
            )


def validate_opportunity_filter_release_binding(manifest: Mapping[str, Any]) -> None:
    """Validate optional release-5.1 pointers while leaving release-5.0 valid."""

    _contract(manifest, "release-manifest", "release manifest")
    binding = manifest.get("opportunity_filters")
    if binding is None:
        return
    artifacts = {row["role"]: row for row in binding["artifacts"]}
    if len(artifacts) != len(binding["artifacts"]) or set(artifacts) != set(
        EXPECTED_RELEASE_ARTIFACTS
    ):
        raise OpportunityFilterContractError(
            "Opportunity Filter release binding must declare each artifact role exactly once."
        )
    checksums = manifest["file_checksums"]
    for role, filename in EXPECTED_RELEASE_ARTIFACTS.items():
        artifact = artifacts[role]
        if artifact["filename"] != filename or artifact["checksum"] != checksums[filename]:
            raise OpportunityFilterContractError(
                f"Opportunity Filter release artifact binding disagrees for {role}."
            )


def validate_opportunity_filter_release_bundle(
    manifest: Mapping[str, Any],
    catalog: Mapping[str, Any],
    evidence_rows: Iterable[Mapping[str, Any]],
    country_codes: Iterable[str],
) -> None:
    """Reconcile a future immutable OFC release bundle across contracts."""

    rows = list(evidence_rows)
    countries = tuple(country_codes)
    validate_opportunity_filter_release_binding(manifest)
    if "opportunity_filters" not in manifest:
        raise OpportunityFilterContractError("The release has no Opportunity Filter binding.")
    validate_opportunity_filter_evidence_matrix(catalog, rows, countries)
    if catalog["stable_universe_id"] != manifest["stable_universe_id"]:
        raise OpportunityFilterContractError("OFC catalog and release universe disagree.")
    counts = manifest["artifact_counts"]
    if counts["opportunity_filter_definitions"] != len(catalog["definitions"]) or counts[
        "opportunity_filter_evidence"
    ] != len(rows):
        raise OpportunityFilterContractError("OFC manifest artifact counts disagree.")


__all__ = [
    "OpportunityFilterCategory",
    "OpportunityFilterConfidenceBand",
    "OpportunityFilterConfidenceTier",
    "OpportunityFilterContractError",
    "OpportunityFilterReasonCode",
    "OpportunityFilterState",
    "validate_opportunity_filter_assessment",
    "validate_opportunity_filter_catalog",
    "validate_opportunity_filter_coverage_summary",
    "validate_opportunity_filter_definition",
    "validate_opportunity_filter_evidence",
    "validate_opportunity_filter_evidence_matrix",
    "validate_opportunity_filter_release_binding",
    "validate_opportunity_filter_release_bundle",
]
