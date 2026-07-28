"""Uncertainty-aware complete-case ranking owned by the domain layer."""

from __future__ import annotations

from collections.abc import Mapping
from math import isclose
from typing import TYPE_CHECKING

from konsider.domain.scoring import ScoringError, normalize_weights
from konsider.domain.uncertainty_models import (
    POLICY,
    ContributionSource,
    CoverageBand,
    ExcludedCountryDiagnostic,
    IgnoredPartialCriterion,
    NonReadyCriterion,
    RankingContribution,
    TopKBoundary,
    UncertaintyPolicy,
    UncertaintyRankingResult,
    UncertaintyRankingRow,
    UncertaintyStatus,
)
from konsider.exceptions import (
    CriterionNotReadyError,
    InvalidTopKError,
    InvalidWeightError,
    RankingIntegrityError,
    UnknownCriterionError,
)

if TYPE_CHECKING:
    from konsider.repositories.published_release_repository import (
        PublishedMetricRecord,
        PublishedRelease,
    )


def rank_release_with_uncertainty(
    release: PublishedRelease,
    raw_weights: Mapping[str, float],
    *,
    resolved_profile_id: str | None = None,
    top_k: int | None = None,
    policy: UncertaintyPolicy = POLICY,
) -> UncertaintyRankingResult:
    """Apply the approved Phase 4A ranking and robustness contract."""

    countries = {item["code"]: item for item in release.catalog["countries"]}
    if len(countries) != policy.stable_country_count:
        raise RankingIntegrityError(
            f"Policy requires {policy.stable_country_count} stable countries."
        )
    criteria = {item["id"]: item for item in release.catalog["criteria"]}
    enabled = {key for key, item in criteria.items() if item["ready"]}
    supplied = set(raw_weights)
    non_ready = sorted(supplied & (set(criteria) - enabled))
    if non_ready:
        raise CriterionNotReadyError(non_ready)
    unknown = sorted(supplied - set(criteria))
    if unknown:
        raise UnknownCriterionError(unknown)
    try:
        # This call is intentionally validation-only. R0 and R1 have different active sets.
        normalize_weights(raw_weights, enabled)
    except (ScoringError, TypeError, ValueError) as exc:
        raise InvalidWeightError(str(exc)) from exc

    coverage_by_id = {
        criterion_id: _coverage_metadata(item)
        for criterion_id, item in criteria.items()
        if criterion_id in enabled
    }
    if any("coverage" in criteria[key] for key in enabled):
        if (
            release.catalog.get("coverage_policy_version") != policy.policy_version
            or release.catalog.get("stable_universe_id") != policy.stable_universe_id
        ):
            raise RankingIntegrityError(
                "Release coverage policy does not match the ranking policy."
            )
        for criterion_id, coverage in coverage_by_id.items():
            if (
                coverage["stable_universe_id"] != policy.stable_universe_id
                or coverage["stable_country_count"] != policy.stable_country_count
            ):
                raise RankingIntegrityError(
                    f"Stable coverage metadata disagrees for {criterion_id}."
                )
            if (
                coverage["mode"] == "CONDITIONAL_COMPLETE_CASE"
                and coverage["activation_threshold"] != policy.pcc_activation_raw_weight_min
            ):
                raise RankingIntegrityError(
                    f"PCC activation threshold disagrees for {criterion_id}."
                )
    fcc_ids = tuple(
        sorted(key for key, coverage in coverage_by_id.items() if coverage["mode"] == "GLOBAL_CORE")
    )
    pcc_ids = tuple(
        sorted(
            key
            for key, coverage in coverage_by_id.items()
            if coverage["mode"] == "CONDITIONAL_COMPLETE_CASE"
        )
    )
    if not fcc_ids:
        raise RankingIntegrityError("At least one GLOBAL_CORE criterion is required.")

    resolved_raw = {key: float(raw_weights.get(key, 0.0)) for key in enabled}
    active_fcc_ids = tuple(key for key in fcc_ids if resolved_raw[key] > 0)
    active_pcc_ids = tuple(
        key for key in pcc_ids if resolved_raw[key] >= policy.pcc_activation_raw_weight_min
    )
    ignored_pcc = tuple(
        IgnoredPartialCriterion(
            criterion_id=key,
            raw_weight=resolved_raw[key],
            reason_code="BELOW_PCC_ACTIVATION_THRESHOLD",
            activation_threshold=policy.pcc_activation_raw_weight_min,
        )
        for key in pcc_ids
        if 0 < resolved_raw[key] < policy.pcc_activation_raw_weight_min
    )

    fcc_raw = {key: resolved_raw[key] for key in fcc_ids}
    try:
        baseline_weights = normalize_weights(fcc_raw, fcc_ids)
    except ScoringError as exc:
        raise RankingIntegrityError(str(exc)) from exc
    baseline_weights = {key: baseline_weights.get(key, 0.0) for key in fcc_ids}

    records_by_pair = {
        (record.country["code"], record.criterion["id"]): record for record in release.records
    }
    if len(records_by_pair) != len(release.records):
        raise RankingIntegrityError("Published ranking records contain duplicate pairs.")
    r0 = _rank(
        countries,
        records_by_pair,
        fcc_ids,
        baseline_weights,
        set(countries),
        policy,
    )

    outcomes_by_pair = {
        (item["country_code"], item["criterion_id"]): item for item in release.outcomes
    }
    missing_by_country: dict[str, list[dict]] = {}
    for criterion_id in active_pcc_ids:
        for country_code in countries:
            outcome = outcomes_by_pair.get((country_code, criterion_id))
            if outcome is None:
                raise RankingIntegrityError(
                    f"Missing criterion outcome for {country_code}/{criterion_id}."
                )
            if outcome["outcome"] != "valid":
                missing_by_country.setdefault(country_code, []).append(outcome)

    excluded_codes = set(missing_by_country)
    eligible_codes = set(countries) - excluded_codes
    gate_exceeded = (
        len(excluded_codes) > policy.hard_missing_union_max
        or len(eligible_codes) < policy.min_eligible_country_count
    )
    ranking_universe_count = (
        len(countries) if not active_pcc_ids or gate_exceeded else len(eligible_codes)
    )
    resolved_top_k = policy.default_top_k if top_k is None else top_k
    if (
        isinstance(resolved_top_k, bool)
        or not isinstance(resolved_top_k, int)
        or not 1 <= resolved_top_k <= ranking_universe_count
    ):
        raise InvalidTopKError(resolved_top_k, ranking_universe_count)

    r0_boundary = _top_k(r0, resolved_top_k, policy)
    all_zero_fcc = not active_fcc_ids
    reason_codes: list[str] = []
    if ignored_pcc:
        reason_codes.append("PCC_BELOW_ACTIVATION_THRESHOLD")
    if all_zero_fcc:
        reason_codes.append("FCC_ALL_ZERO_EQUAL_WEIGHT_FALLBACK")

    final_weights: dict[str, float] | None = None
    r1: tuple[UncertaintyRankingRow, ...] | None = None
    r1_boundary: TopKBoundary | None = None
    excluded_diagnostics: tuple[ExcludedCountryDiagnostic, ...] = ()

    if not active_pcc_ids:
        status = UncertaintyStatus.NO_PARTIAL_CRITERIA_ACTIVE
        reason_codes.insert(0, "NO_PCC_AT_OR_ABOVE_ACTIVATION_THRESHOLD")
        coverage_band = CoverageBand.PREFERRED
        result_rows = r0_boundary.rankings
    elif gate_exceeded:
        status = UncertaintyStatus.COVERAGE_LIMIT_EXCEEDED
        coverage_band = CoverageBand.BLOCKED
        if len(excluded_codes) > policy.hard_missing_union_max:
            reason_codes.append("ACTIVE_MISSING_UNION_EXCEEDS_HARD_LIMIT")
        if len(eligible_codes) < policy.min_eligible_country_count:
            reason_codes.append("ELIGIBLE_UNIVERSE_BELOW_MINIMUM")
        excluded_diagnostics = _excluded_diagnostics(
            release,
            countries,
            missing_by_country,
            r0,
            records_by_pair,
            active_fcc_ids,
            active_pcc_ids,
            None,
            None,
            policy,
        )
        result_rows = r0_boundary.rankings
    else:
        active_ids = (*active_fcc_ids, *active_pcc_ids)
        final_weights = normalize_weights(
            {key: resolved_raw[key] for key in active_ids},
            active_ids,
        )
        r1 = _rank(
            countries,
            records_by_pair,
            active_ids,
            final_weights,
            eligible_codes,
            policy,
        )
        r1_boundary = _top_k(r1, resolved_top_k, policy)
        excluded_diagnostics = _excluded_diagnostics(
            release,
            countries,
            missing_by_country,
            r0,
            records_by_pair,
            active_fcc_ids,
            active_pcc_ids,
            final_weights,
            r1_boundary.kth_score,
            policy,
        )
        coverage_band = (
            CoverageBand.PREFERRED
            if len(excluded_codes) <= policy.preferred_missing_union_max
            else CoverageBand.ELEVATED
        )
        if not excluded_codes:
            status = UncertaintyStatus.FULL_COVERAGE
            reason_codes.append("ACTIVE_PCC_HAS_NO_NON_READY_COUNTRIES")
        else:
            reason_codes.append(
                "ACTIVE_MISSING_UNION_WITHIN_PREFERRED_LIMIT"
                if coverage_band == CoverageBand.PREFERRED
                else "ACTIVE_MISSING_UNION_ABOVE_PREFERRED_LIMIT"
            )
            r0_top_codes = {item.country_code for item in r0_boundary.rankings}
            if excluded_codes & r0_top_codes:
                status = UncertaintyStatus.BASELINE_TOP_K_EXCLUDED
                reason_codes.append("EXCLUDED_COUNTRY_IN_BASELINE_TOP_K")
            elif any(item.could_enter_top_k for item in excluded_diagnostics):
                status = UncertaintyStatus.POTENTIALLY_AFFECTED
                reason_codes.append("EXCLUDED_COUNTRY_CAN_REACH_TOP_K_BOUNDARY")
            else:
                status = UncertaintyStatus.ROBUST_TOP_K
                reason_codes.append("ALL_EXCLUDED_COUNTRIES_BELOW_TOP_K_BOUNDARY")
        result_rows = r1_boundary.rankings

    if (
        r0_boundary.returned_result_count > resolved_top_k
        or r1_boundary is not None
        and r1_boundary.returned_result_count > resolved_top_k
    ):
        reason_codes.append("TOP_K_BOUNDARY_INCLUDES_TIES")

    return UncertaintyRankingResult(
        release_id=release.release_id,
        release_schema_version=release.manifest["schema_version"],
        catalog_schema_version=release.catalog["schema_version"],
        scoring_method_versions=tuple(
            sorted(
                item["scoring_method_version"]
                for item in release.catalog["criteria"]
                if item["ready"]
            )
        ),
        resolved_profile_id=resolved_profile_id,
        policy=policy,
        status=status,
        reason_codes=tuple(dict.fromkeys(reason_codes)),
        coverage_band=coverage_band,
        requested_top_k=resolved_top_k,
        stable_country_count=len(countries),
        eligible_country_count=len(eligible_codes),
        excluded_country_count=len(excluded_codes),
        active_fcc_ids=active_fcc_ids,
        active_pcc_ids=active_pcc_ids,
        ignored_pcc=ignored_pcc,
        baseline_normalized_weights=baseline_weights,
        final_normalized_weights=final_weights,
        excluded_countries=excluded_diagnostics,
        r0_top_k=r0_boundary,
        r1_top_k=r1_boundary,
        r1_kth_score=r1_boundary.kth_score if r1_boundary else None,
        rankings=result_rows,
        _r0_rankings=r0,
        _r1_rankings=r1,
    )


def _coverage_metadata(criterion: dict) -> dict:
    coverage = criterion.get("coverage")
    if coverage is not None:
        return coverage
    # Schema-3 releases retain their original complete-matrix FCC interpretation.
    return {
        "mode": "GLOBAL_CORE",
        "source_versions": {},
        "scoring_method_version": criterion["scoring_method_version"],
    }


def _rank(
    countries: dict[str, dict],
    records_by_pair: dict[tuple[str, str], PublishedMetricRecord],
    criterion_ids: tuple[str, ...],
    normalized_weights: Mapping[str, float],
    eligible_codes: set[str],
    policy: UncertaintyPolicy,
) -> tuple[UncertaintyRankingRow, ...]:
    pending = []
    for country_code in sorted(eligible_codes):
        contributions = []
        for criterion_id in sorted(criterion_ids):
            record = records_by_pair.get((country_code, criterion_id))
            if record is None:
                raise RankingIntegrityError(
                    f"Eligible country lacks a score for {country_code}/{criterion_id}."
                )
            observation = record.observations[0]
            weight = normalized_weights.get(criterion_id, 0.0)
            contribution = round(record.score["score"] * weight, policy.score_precision)
            contributions.append(
                RankingContribution(
                    criterion_id=criterion_id,
                    criterion_name=record.criterion["display_name"],
                    score=record.score["score"],
                    normalized_weight=weight,
                    contribution=contribution,
                    raw_observation=observation["value"],
                    raw_unit=observation["unit"],
                    reference_start=observation["reference_start"],
                    reference_end=observation["reference_end"],
                    observation_id=observation["observation_id"],
                    observation_method_version=observation["method_version"],
                    parser_version=observation["parser_version"],
                    scoring_method_version=record.score["method_version"],
                    source=ContributionSource(
                        source_id=record.source["source_id"],
                        publisher=record.source["publisher"],
                        source_version=record.source["source_version"],
                        dataset_version=record.source["dataset_version"],
                        canonical_page_url=record.source["canonical_page_url"],
                        attribution=record.source["attribution"],
                    ),
                    caveats=tuple(record.criterion["caveats"]),
                    quality_limitations=tuple(record.criterion["quality_limitations"]),
                    experimental=record.criterion["experimental"],
                    input_observations=tuple(record.observations),
                )
            )
        total = round(sum(item.contribution for item in contributions), policy.score_precision)
        weighted = [item for item in contributions if item.normalized_weight > 0]
        strengths = tuple(
            item.criterion_id
            for item in sorted(
                weighted,
                key=lambda item: (-item.score, item.criterion_id),
            )[:3]
        )
        tradeoffs = tuple(
            item.criterion_id
            for item in sorted(
                weighted,
                key=lambda item: (item.score, item.criterion_id),
            )[:3]
        )
        country = countries[country_code]
        pending.append(
            (
                total,
                country_code,
                country,
                tuple(contributions),
                strengths,
                tradeoffs,
            )
        )
    pending.sort(key=lambda item: (-item[0], item[1]))
    return tuple(
        UncertaintyRankingRow(
            rank=rank,
            country_code=country_code,
            country_name=country["display_name"],
            region=country["region"],
            total_score=total,
            eligible_country_count=len(eligible_codes),
            contributions=contributions,
            strengths=strengths,
            tradeoffs=tradeoffs,
        )
        for rank, (total, country_code, country, contributions, strengths, tradeoffs) in enumerate(
            pending, 1
        )
    )


def _top_k(
    ranking: tuple[UncertaintyRankingRow, ...],
    requested_k: int,
    policy: UncertaintyPolicy,
) -> TopKBoundary:
    kth_score = ranking[requested_k - 1].total_score
    rows = tuple(
        item
        for item in ranking
        if item.total_score > kth_score
        or isclose(
            item.total_score,
            kth_score,
            rel_tol=0.0,
            abs_tol=policy.rounding_tolerance,
        )
    )
    boundary_tie_count = sum(
        isclose(
            item.total_score,
            kth_score,
            rel_tol=0.0,
            abs_tol=policy.rounding_tolerance,
        )
        for item in ranking
    )
    return TopKBoundary(
        requested_k=requested_k,
        kth_score=kth_score,
        boundary_tie_count=boundary_tie_count,
        returned_result_count=len(rows),
        rankings=rows,
    )


def _excluded_diagnostics(
    release: PublishedRelease,
    countries: dict[str, dict],
    missing_by_country: dict[str, list[dict]],
    r0: tuple[UncertaintyRankingRow, ...],
    records_by_pair: dict[tuple[str, str], PublishedMetricRecord],
    active_fcc_ids: tuple[str, ...],
    active_pcc_ids: tuple[str, ...],
    final_weights: Mapping[str, float] | None,
    r1_kth_score: float | None,
    policy: UncertaintyPolicy,
) -> tuple[ExcludedCountryDiagnostic, ...]:
    r0_by_country = {item.country_code: item for item in r0}
    criteria = {item["id"]: item for item in release.catalog["criteria"]}
    result = []
    for country_code, missing_outcomes in sorted(missing_by_country.items()):
        non_ready = tuple(
            NonReadyCriterion(
                criterion_id=outcome["criterion_id"],
                outcome=outcome["outcome"],
                reason_codes=tuple(outcome["reason_codes"]),
                source_id=outcome["source_id"],
                source_versions=dict(
                    criteria[outcome["criterion_id"]]["coverage"]["source_versions"]
                ),
                scoring_method_version=criteria[outcome["criterion_id"]]["scoring_method_version"],
                observation_id=outcome.get("observation_id"),
            )
            for outcome in sorted(missing_outcomes, key=lambda item: item["criterion_id"])
        )
        optimistic = None
        could_enter = None
        if final_weights is not None and r1_kth_score is not None:
            optimistic = 0.0
            non_ready_ids = {item["criterion_id"] for item in missing_outcomes}
            for criterion_id in (*active_fcc_ids, *active_pcc_ids):
                weight = final_weights[criterion_id]
                if criterion_id in non_ready_ids:
                    score = policy.diagnostic_score_max
                else:
                    record = records_by_pair.get((country_code, criterion_id))
                    if record is None:
                        raise RankingIntegrityError(
                            "Known active criterion lacks a score for "
                            f"{country_code}/{criterion_id}."
                        )
                    score = record.score["score"]
                optimistic += score * weight
            optimistic = round(optimistic, policy.score_precision)
            could_enter = optimistic > r1_kth_score or isclose(
                optimistic,
                r1_kth_score,
                rel_tol=0.0,
                abs_tol=policy.rounding_tolerance,
            )
        baseline = r0_by_country[country_code]
        result.append(
            ExcludedCountryDiagnostic(
                country_code=country_code,
                country_name=countries[country_code]["display_name"],
                r0_rank=baseline.rank,
                r0_score=baseline.total_score,
                non_ready_criteria=non_ready,
                optimistic_upper_bound=optimistic,
                could_enter_top_k=could_enter,
            )
        )
    return tuple(result)
