"""Weighted country scoring for Konsider Phase 1."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping

from konsider.domain.models import (
    Country,
    CountryMetric,
    CountryRanking,
    RankingRow,
    ScoreContribution,
)


class ScoringError(ValueError):
    """Raised when weights or metrics cannot produce a valid ranking."""


def normalize_weights(
    weights: Mapping[str, float],
    parameter_ids: Iterable[str] | None = None,
) -> dict[str, float]:
    """Normalize parameter weights so they sum to 1.0.

    If all supplied weights are zero and parameter_ids are provided, the function returns equal
    weights for those parameters. This keeps the future UI forgiving when sliders start at zero.
    """

    allowed_parameters = set(parameter_ids or weights.keys())
    unknown_parameters = set(weights) - allowed_parameters
    if unknown_parameters:
        raise ScoringError(f"Unknown weight parameter(s): {sorted(unknown_parameters)}")

    normalized_inputs = {
        parameter_id: float(weights.get(parameter_id, 0.0)) for parameter_id in allowed_parameters
    }
    negative_weights = [parameter_id for parameter_id, weight in normalized_inputs.items() if weight < 0]
    if negative_weights:
        raise ScoringError(f"Weights cannot be negative: {sorted(negative_weights)}")

    total = sum(normalized_inputs.values())
    if total == 0:
        if not normalized_inputs:
            raise ScoringError("At least one weight is required.")
        equal_weight = 1.0 / len(normalized_inputs)
        return {parameter_id: equal_weight for parameter_id in sorted(normalized_inputs)}

    return {
        parameter_id: weight / total
        for parameter_id, weight in sorted(normalized_inputs.items())
        if weight > 0
    }


def rank_countries(
    metrics: Iterable[CountryMetric],
    weights: Mapping[str, float],
) -> list[CountryRanking]:
    """Rank countries by weighted score using normalized parameter weights."""

    metric_rows = list(metrics)
    if not metric_rows:
        raise ScoringError("At least one metric is required.")

    parameter_ids = {metric.parameter_id for metric in metric_rows}
    normalized_weights = normalize_weights(weights, parameter_ids)

    metrics_by_country = group_metrics_by_country(metric_rows)

    rankings = []
    for country_id, country_metrics in metrics_by_country.items():
        rankings.append(score_country(country_id, country_metrics, normalized_weights))

    return sorted(rankings, key=lambda item: (-item.total_score, item.country_id))


def score_country(
    country_id: str,
    metrics: Iterable[CountryMetric],
    normalized_weights: Mapping[str, float],
) -> CountryRanking:
    """Score one country using already-normalized weights."""

    contributions = []
    for metric in sorted(metrics, key=lambda item: item.parameter_id):
        weight = normalized_weights.get(metric.parameter_id, 0.0)
        if weight == 0:
            continue
        contribution = metric.score * weight
        contributions.append(
            ScoreContribution(
                parameter_id=metric.parameter_id,
                raw_score=metric.score,
                weight=weight,
                contribution=round(contribution, 4),
            )
        )

    total_score = sum(item.contribution for item in contributions)
    return CountryRanking(
        country_id=country_id,
        total_score=round(total_score, 4),
        contributions=contributions,
    )


def group_metrics_by_country(metrics: Iterable[CountryMetric]) -> dict[str, list[CountryMetric]]:
    """Group metric rows by country id."""

    metrics_by_country: dict[str, list[CountryMetric]] = defaultdict(list)
    for metric in metrics:
        metrics_by_country[metric.country_id].append(metric)
    return dict(metrics_by_country)


def get_country_breakdown(ranking: CountryRanking) -> list[ScoreContribution]:
    """Return a country's score contributions from largest to smallest."""

    return sorted(ranking.contributions, key=lambda item: (-item.contribution, item.parameter_id))


def build_ranking_table(
    rankings: Iterable[CountryRanking],
    countries: Mapping[str, Country],
    *,
    signal_count: int = 3,
) -> list[RankingRow]:
    """Build display-ready ranking rows with strengths and tradeoffs."""

    rows = []
    for rank, ranking in enumerate(rankings, start=1):
        country = countries.get(ranking.country_id)
        country_name = country.name if country else ranking.country_id
        rows.append(
            RankingRow(
                rank=rank,
                country_id=ranking.country_id,
                country_name=country_name,
                total_score=ranking.total_score,
                top_strengths=_top_parameter_ids(ranking, signal_count, strongest=True),
                top_tradeoffs=_top_parameter_ids(ranking, signal_count, strongest=False),
            )
        )
    return rows


def _top_parameter_ids(
    ranking: CountryRanking,
    count: int,
    *,
    strongest: bool,
) -> list[str]:
    ordered = sorted(
        ranking.contributions,
        key=lambda item: (
            -item.raw_score if strongest else item.raw_score,
            -item.weight,
            item.parameter_id,
        ),
    )
    return [item.parameter_id for item in ordered[:count]]
