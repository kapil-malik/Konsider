"""Versioned scoring and sensitivity experiments over real observations."""

from __future__ import annotations

from collections import defaultdict
from statistics import pstdev

from konsider.ingestion.models import MetricObservation, MetricScore

NEGATIVE_METRICS = {
    "ambient_pm25_population_weighted", "intentional_homicide_rate",
    "household_consumption_price_level_us_100",
}

# Fixed, interpretable anchors avoid stretching a narrow country sample across the full 1-10 scale.
# Values between anchors are linearly interpolated and values outside are capped.
THRESHOLD_METHODS = {
    "ambient_pm25_population_weighted": ("pm25_health_bands_v1", ((5, 10), (15, 8), (25, 6), (35, 4), (50, 1))),
    "intentional_homicide_rate": ("homicide_risk_bands_v1", ((0, 10), (1, 9), (3, 7), (5, 5), (10, 1))),
    "uhc_service_coverage_index": ("uhc_coverage_bands_v1", ((50, 1), (60, 3), (70, 5), (80, 7.5), (90, 10))),
    "household_consumption_price_level_us_100": ("icp_price_level_bands_v1", ((50, 10), (75, 8), (100, 6), (125, 4), (150, 2), (175, 1))),
    "women_peace_security_index": ("wps_index_bands_v1", ((0.5, 1), (0.6, 3), (0.7, 5), (0.8, 7.5), (0.9, 10))),
}


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _threshold_score(value: float, anchors: tuple[tuple[float, float], ...]) -> float:
    if value <= anchors[0][0]:
        return anchors[0][1]
    if value >= anchors[-1][0]:
        return anchors[-1][1]
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:], strict=False):
        if x0 <= value <= x1:
            return y0 + (value - x0) / (x1 - x0) * (y1 - y0)
    raise AssertionError("threshold interpolation failed")


def _algorithm_scores(values: list[float], algorithm: str, direction: str, anchors=None) -> list[float]:
    if algorithm == "threshold":
        return [_threshold_score(value, anchors) for value in values]
    if algorithm == "winsorized_minmax":
        low, high = _percentile(values, 0.05), _percentile(values, 0.95)
        scaled = [0.5 if high == low else (min(max(v, low), high) - low) / (high - low) for v in values]
    elif algorithm == "percentile_rank":
        ordered = sorted(values)
        scaled = [0.5 if len(values) == 1 else sum(item < value for item in ordered) / (len(values) - 1) for value in values]
    else:
        raise ValueError(f"Unknown scoring algorithm: {algorithm}")
    if direction == "lower_is_better":
        scaled = [1 - value for value in scaled]
    return [1 + 9 * value for value in scaled]


def score_observations(observations: list[MetricObservation]) -> list[MetricScore]:
    grouped: dict[str, list[MetricObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.metric_id].append(observation)
    scores = []
    for metric_id, rows in sorted(grouped.items()):
        method_version, anchors = THRESHOLD_METHODS[metric_id]
        direction = "lower_is_better" if metric_id in NEGATIVE_METRICS else "higher_is_better"
        values = [row.value for row in rows]
        transformed = _algorithm_scores(values, "threshold", direction, anchors)
        for row, score in zip(rows, transformed, strict=True):
            scores.append(MetricScore(
                country_code=row.country_code, criterion_id=metric_id, score=round(score, 2),
                input_observation_ids=(row.observation_id,), method_version=method_version,
                transform="fixed_piecewise_linear_thresholds", direction=direction,
            ))
    return sorted(scores, key=lambda item: (item.criterion_id, item.country_code))


def sensitivity_experiments(observations: list[MetricObservation]) -> dict[str, object]:
    grouped: dict[str, list[MetricObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.metric_id].append(observation)
    results = {}
    for metric_id, rows in sorted(grouped.items()):
        values = [row.value for row in sorted(rows, key=lambda item: item.country_code)]
        direction = "lower_is_better" if metric_id in NEGATIVE_METRICS else "higher_is_better"
        method_version, anchors = THRESHOLD_METHODS[metric_id]
        algorithms = {
            name: _algorithm_scores(values, name, direction, anchors)
            for name in ("winsorized_minmax", "percentile_rank", "threshold")
        }
        ordered_values = sorted(values)
        trimmed = ordered_values[1:-1] if len(values) > 2 else ordered_values
        full_threshold = _algorithm_scores(values, "threshold", direction, anchors)
        trimmed_threshold = _algorithm_scores(trimmed, "threshold", direction, anchors)
        midpoint = sum(values) / len(values)
        width = max(max(values) - min(values), 1.0) * 0.01
        clustered = [midpoint - width / 2 + width * i / 19 for i in range(20)]
        cluster_spreads = {
            name: round(max(scores) - min(scores), 4)
            for name in ("winsorized_minmax", "percentile_rank", "threshold")
            for scores in [_algorithm_scores(clustered, name, direction, anchors)]
        }
        results[metric_id] = {
            "selected_method_version": method_version,
            "anchors": [list(item) for item in anchors],
            "observed_raw_range": [min(values), max(values)],
            "score_ranges": {name: [round(min(scores), 3), round(max(scores), 3)] for name, scores in algorithms.items()},
            "score_standard_deviation": {name: round(pstdev(scores), 4) for name, scores in algorithms.items()},
            "country_set_test": {
                "scenario": "remove one minimum and one maximum raw observation",
                "threshold_score_range_full": [round(min(full_threshold), 3), round(max(full_threshold), 3)],
                "threshold_score_range_trimmed": [round(min(trimmed_threshold), 3), round(max(trimmed_threshold), 3)],
            },
            "tight_cluster_test_score_spread": cluster_spreads,
            "selection_reason": "Fixed domain anchors are composition-stable and do not force small observed differences across the full score range.",
        }
    return {"schema_version": "scoring-sensitivity-1.0", "criteria": results}
