"""Versioned transparent scoring experiments over real observations."""

from __future__ import annotations

from collections import defaultdict

from konsider.ingestion.models import MetricObservation, MetricScore

METHOD_VERSION = "winsorized_minmax_v1"
NEGATIVE_METRICS = {"ambient_pm25_population_weighted", "intentional_homicide_rate", "household_consumption_price_level_us_100"}


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def score_observations(observations: list[MetricObservation]) -> list[MetricScore]:
    grouped: dict[str, list[MetricObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.metric_id].append(observation)
    scores = []
    for metric_id, rows in sorted(grouped.items()):
        values = [row.value for row in rows]
        low, high = _percentile(values, 0.05), _percentile(values, 0.95)
        for row in rows:
            clipped = min(max(row.value, low), high)
            scaled = 0.5 if high == low else (clipped - low) / (high - low)
            direction = "lower_is_better" if metric_id in NEGATIVE_METRICS else "higher_is_better"
            if direction == "lower_is_better":
                scaled = 1 - scaled
            scores.append(MetricScore(
                country_code=row.country_code, criterion_id=metric_id,
                score=round(1 + 9 * scaled, 2), input_observation_ids=(row.observation_id,),
                method_version=METHOD_VERSION, transform="winsorized_minmax_5_95",
                direction=direction,
            ))
    return sorted(scores, key=lambda item: (item.criterion_id, item.country_code))
