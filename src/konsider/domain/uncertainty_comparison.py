"""Evidence-matrix comparison built on one Phase 4D ranking computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from konsider.domain.uncertainty_models import (
    ComparisonAggregateKind,
    ComparisonAvailability,
    ComparisonCell,
    ComparisonCountrySummary,
    ComparisonCriterionRow,
    ComparisonRankingStatus,
    ContributionSource,
    UncertaintyComparisonResult,
    UncertaintyRankingResult,
    UncertaintyStatus,
)
from konsider.exceptions import RankingIntegrityError

if TYPE_CHECKING:
    from konsider.repositories.published_release_repository import PublishedRelease


def compare_release_with_uncertainty(
    release: PublishedRelease,
    ranking: UncertaintyRankingResult,
    country_codes: tuple[str, ...],
) -> UncertaintyComparisonResult:
    """Build cell-level availability without ever calculating a partial total."""

    countries = {item["code"]: item for item in release.catalog["countries"]}
    criteria = {item["id"]: item for item in release.catalog["criteria"] if item["ready"]}
    records = {(item.country["code"], item.criterion["id"]): item for item in release.records}
    outcomes = {(item["country_code"], item["criterion_id"]): item for item in release.outcomes}
    sources = {item["source_id"]: item for item in release.sources}
    active_ids = _active_criterion_ids(ranking)

    criterion_rows = []
    unavailable_by_country: dict[str, int] = dict.fromkeys(country_codes, 0)
    unavailable_active_by_country: dict[str, int] = dict.fromkeys(country_codes, 0)
    for criterion_id, criterion in sorted(criteria.items()):
        cells = []
        for country_code in country_codes:
            outcome = outcomes.get((country_code, criterion_id))
            record = records.get((country_code, criterion_id))
            active = criterion_id in active_ids
            if outcome is not None and outcome["outcome"] != "valid":
                availability = ComparisonAvailability(outcome["outcome"].upper())
                source = _source(sources[outcome["source_id"]])
                reason_codes = tuple(outcome["reason_codes"])
                cell = ComparisonCell(
                    country_code=country_code,
                    availability=availability,
                    message_code=f"DATA_{availability.value}",
                    active_for_ranking=active,
                    normalized_score=None,
                    raw_observation=None,
                    raw_unit=None,
                    reference_start=None,
                    reference_end=None,
                    source=source,
                    reason_codes=reason_codes,
                )
                unavailable_by_country[country_code] += 1
                if active:
                    unavailable_active_by_country[country_code] += 1
            elif record is not None:
                observation = record.observations[0]
                cell = ComparisonCell(
                    country_code=country_code,
                    availability=ComparisonAvailability.AVAILABLE,
                    message_code="DATA_AVAILABLE",
                    active_for_ranking=active,
                    normalized_score=record.score["score"],
                    raw_observation=observation["value"],
                    raw_unit=observation["unit"],
                    reference_start=observation["reference_start"],
                    reference_end=observation["reference_end"],
                    source=_source(record.source),
                    reason_codes=(),
                )
            else:
                raise RankingIntegrityError(
                    f"Comparison criterion lacks an outcome for " f"{country_code}/{criterion_id}."
                )
            cells.append(cell)
        coverage = criterion.get("coverage")
        coverage_mode = coverage["mode"] if coverage is not None else "GLOBAL_CORE"
        criterion_rows.append(
            ComparisonCriterionRow(
                criterion_id=criterion_id,
                criterion_name=criterion["display_name"],
                coverage_mode=coverage_mode,
                experimental=criterion["experimental"],
                cells=tuple(cells),
            )
        )

    r0_by_country = ranking.r0_rankings_by_country
    r1_by_country = ranking.r1_rankings_by_country
    summaries = []
    aggregate_rows = []
    for country_code in country_codes:
        unavailable = unavailable_by_country[country_code]
        unavailable_active = unavailable_active_by_country[country_code]
        if ranking.status == UncertaintyStatus.COVERAGE_LIMIT_EXCEEDED:
            row = r0_by_country[country_code]
            eligible = False
            aggregate_kind = ComparisonAggregateKind.FCC_BASELINE
            ranking_status = ComparisonRankingStatus.FCC_BASELINE_ONLY
            message_code = "FCC_BASELINE_COVERAGE_LIMIT"
        elif ranking.active_pcc_ids:
            row = r1_by_country.get(country_code)
            if row is None:
                eligible = False
                aggregate_kind = ComparisonAggregateKind.NONE
                ranking_status = ComparisonRankingStatus.NOT_RANKED_ACTIVE_DATA_GAP
                message_code = "NOT_RANKED_ACTIVE_DATA_GAP"
            else:
                eligible = True
                aggregate_kind = ComparisonAggregateKind.FINAL
                ranking_status = ComparisonRankingStatus.RANKED
                message_code = "FINAL_COMPLETE_CASE_RANK"
        else:
            row = r0_by_country[country_code]
            eligible = True
            aggregate_kind = ComparisonAggregateKind.FINAL
            ranking_status = ComparisonRankingStatus.RANKED
            message_code = "FINAL_GLOBAL_CORE_RANK"
        if row is not None:
            aggregate_rows.append(row)
        summaries.append(
            ComparisonCountrySummary(
                country_code=country_code,
                country_name=countries[country_code]["display_name"],
                comparison_data_complete=unavailable == 0,
                ranking_eligible=eligible,
                unavailable_displayed_criterion_count=unavailable,
                unavailable_active_criterion_count=unavailable_active,
                aggregate_kind=aggregate_kind,
                ranking_status=ranking_status,
                message_code=message_code,
                total_score=row.total_score if row is not None else None,
                rank=row.rank if row is not None else None,
            )
        )

    excluded = {item.country_code: item for item in ranking.excluded_countries}
    return UncertaintyComparisonResult(
        ranking_result=ranking,
        requested_country_codes=country_codes,
        country_summaries=tuple(summaries),
        criterion_rows=tuple(criterion_rows),
        countries=tuple(aggregate_rows),
        excluded_countries=tuple(excluded[code] for code in country_codes if code in excluded),
    )


def _active_criterion_ids(
    ranking: UncertaintyRankingResult,
) -> frozenset[str]:
    if ranking.final_normalized_weights is not None:
        return frozenset(ranking.final_normalized_weights)
    if ranking.active_pcc_ids:
        return frozenset((*ranking.active_fcc_ids, *ranking.active_pcc_ids))
    return frozenset(key for key, value in ranking.baseline_normalized_weights.items() if value > 0)


def _source(value: dict) -> ContributionSource:
    return ContributionSource(
        source_id=value["source_id"],
        publisher=value["publisher"],
        source_version=value["source_version"],
        dataset_version=value["dataset_version"],
        canonical_page_url=value["canonical_page_url"],
        attribution=value["attribution"],
    )
