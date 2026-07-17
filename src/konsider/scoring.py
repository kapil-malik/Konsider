"""Weighted country scoring for Konsider Phase 1."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping

from konsider.models import CountryMetric, CountryRanking, ScoreContribution


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

    normalized_inputs = {parameter_id: float(weights.get(parameter_id, 0.0)) for parameter_id in allowed_parameters}
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

    metrics_by_country: dict[str, list[CountryMetric]] = defaultdict(list)
    for metric in metric_rows:
        metrics_by_country[metric.country_id].append(metric)

    rankings = []
    for country_id, country_metrics in metrics_by_country.items():
        contributions = []
        for metric in sorted(country_metrics, key=lambda item: item.parameter_id):
            weight = normalized_weights.get(metric.parameter_id, 0.0)
            if weight == 0:
                continue
            contribution = metric.score * weight
            contributions.append(
                ScoreContribution(
                    parameter_id=metric.parameter_id,
                    raw_score=metric.score,
                    weight=weight,
                    contribution=contribution,
                )
            )

        total_score = sum(item.contribution for item in contributions)
        rankings.append(
            CountryRanking(
                country_id=country_id,
                total_score=round(total_score, 4),
                contributions=contributions,
            )
        )

    return sorted(rankings, key=lambda item: (-item.total_score, item.country_id))
