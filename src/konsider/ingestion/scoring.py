"""Versioned criterion scoring and sensitivity experiments."""

from __future__ import annotations

from collections import defaultdict
from statistics import correlation, pstdev

from konsider.ingestion.models import MetricObservation, MetricScore

NEGATIVE_METRICS = {
    "ambient_pm25_population_weighted",
    "intentional_homicide_rate",
    "household_consumption_price_level_us_100",
}

LEGACY_THRESHOLD_METHODS = {
    "ambient_pm25_population_weighted": (
        "pm25_health_bands_v1",
        ((5, 10), (15, 8), (25, 6), (35, 4), (50, 1)),
    ),
    "intentional_homicide_rate": (
        "homicide_risk_bands_v1",
        ((0, 10), (1, 9), (3, 7), (5, 5), (10, 1)),
    ),
    "uhc_service_coverage_index": (
        "uhc_coverage_bands_v1",
        ((50, 1), (60, 3), (70, 5), (80, 7.5), (90, 10)),
    ),
    "household_consumption_price_level_us_100": (
        "icp_price_level_bands_v1",
        ((50, 10), (75, 8), (100, 6), (125, 4), (150, 2), (175, 1)),
    ),
    "women_peace_security_index": (
        "wps_index_bands_v1",
        ((0.5, 1), (0.6, 3), (0.7, 5), (0.8, 7.5), (0.9, 10)),
    ),
}

CURRENT_THRESHOLD_METHODS = {
    **LEGACY_THRESHOLD_METHODS,
    "household_consumption_price_level_us_100": (
        "icp_relative_cost_bands_v2",
        ((50, 9), (75, 8), (100, 6), (125, 4), (150, 2), (175, 1)),
    ),
    "women_legal_economic_equality": (
        "wbl_legal_equality_bands_v1",
        ((40, 1), (55, 3), (70, 5.5), (85, 8), (100, 10)),
    ),
    "infrastructure_readiness_composite": (
        "infrastructure_readiness_bands_v1",
        ((30, 1), (45, 3), (60, 5.5), (75, 8), (90, 10)),
    ),
    "political_stability": (
        "wgi_political_stability_bands_v1",
        ((-2, 1), (-1, 3), (0, 5.5), (1, 8), (2, 10)),
    ),
    "rule_of_law": (
        "wgi_rule_of_law_bands_v1",
        ((-2, 1), (-1, 3), (0, 5.5), (1, 8), (2, 10)),
    ),
    "established_immigrant_presence": (
        "migrant_presence_bands_v1",
        ((0, 1), (5, 3), (15, 5.5), (30, 8), (50, 10)),
    ),
}


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _average_ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        rank = (start + end - 1) / 2 + 1
        for original_index, _ in ordered[start:end]:
            ranks[original_index] = rank
        start = end
    return ranks


def _threshold_score(value: float, anchors: tuple[tuple[float, float], ...]) -> float:
    if value <= anchors[0][0]:
        return anchors[0][1]
    if value >= anchors[-1][0]:
        return anchors[-1][1]
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:], strict=False):
        if x0 <= value <= x1:
            return y0 + (value - x0) / (x1 - x0) * (y1 - y0)
    raise AssertionError("threshold interpolation failed")


def _icp_broad_band(value: float) -> float:
    for upper, score in ((60, 9), (80, 8), (100, 6), (125, 4), (150, 2)):
        if value <= upper:
            return score
    return 1


def _algorithm_scores(
    values: list[float],
    algorithm: str,
    direction: str,
    anchors=None,
    *,
    metric_id: str | None = None,
    broad_icp: bool = False,
) -> list[float]:
    if algorithm == "threshold":
        if broad_icp and metric_id == "household_consumption_price_level_us_100":
            return [_icp_broad_band(value) for value in values]
        return [_threshold_score(value, anchors) for value in values]
    if algorithm == "winsorized_minmax":
        low, high = _percentile(values, 0.05), _percentile(values, 0.95)
        scaled = [
            0.5 if high == low else (min(max(v, low), high) - low) / (high - low) for v in values
        ]
    elif algorithm == "percentile_rank":
        ordered = sorted(values)
        scaled = [
            0.5 if len(values) == 1 else sum(item < value for item in ordered) / (len(values) - 1)
            for value in values
        ]
    else:
        raise ValueError(f"Unknown scoring algorithm: {algorithm}")
    if direction == "lower_is_better":
        scaled = [1 - value for value in scaled]
    return [1 + 9 * value for value in scaled]


def score_observations(
    observations: list[MetricObservation],
    *,
    profile: str = "current",
) -> list[MetricScore]:
    methods = LEGACY_THRESHOLD_METHODS if profile == "legacy" else CURRENT_THRESHOLD_METHODS
    grouped: dict[str, list[MetricObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.metric_id].append(observation)
    scores = []
    for metric_id, rows in sorted(grouped.items()):
        method_version, anchors = methods[metric_id]
        direction = "lower_is_better" if metric_id in NEGATIVE_METRICS else "higher_is_better"
        broad_icp = profile != "legacy"
        transformed = _algorithm_scores(
            [row.value for row in rows],
            "threshold",
            direction,
            anchors,
            metric_id=metric_id,
            broad_icp=broad_icp,
        )
        transform = (
            "fixed_broad_relative_cost_bands"
            if broad_icp and metric_id == "household_consumption_price_level_us_100"
            else "fixed_piecewise_linear_thresholds"
        )
        for row, score in zip(rows, transformed, strict=True):
            scores.append(
                MetricScore(
                    country_code=row.country_code,
                    criterion_id=metric_id,
                    score=round(score, 2),
                    input_observation_ids=(row.observation_id,),
                    method_version=method_version,
                    transform=transform,
                    direction=direction,
                )
            )
    return sorted(scores, key=lambda item: (item.criterion_id, item.country_code))


def _infrastructure_experiment(rows: list[MetricObservation]) -> dict[str, object]:
    component_ids = [component.component_id for component in rows[0].components]
    series = {
        component_id: [
            next(c.value for c in row.components if c.component_id == component_id) for row in rows
        ]
        for component_id in component_ids
    }
    correlations = {}
    for index, left in enumerate(component_ids):
        for right in component_ids[index + 1 :]:
            correlations[f"{left}__{right}"] = round(correlation(series[left], series[right]), 4)
    component_years = {
        component_id: sorted(
            {
                next(c.reference_year for c in row.components if c.component_id == component_id)
                for row in rows
            }
        )
        for component_id in component_ids
    }
    return {
        "components": component_ids,
        "component_reference_years": component_years,
        "pairwise_pearson_correlations": correlations,
        "weighting": "equal one-third weights after fixed component transformations",
        "interpretation": "Digital access and trade/transport readiness only; excludes utilities, housing, and local service quality.",
    }


def sensitivity_experiments(observations: list[MetricObservation]) -> dict[str, object]:
    grouped: dict[str, list[MetricObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.metric_id].append(observation)
    results = {}
    for metric_id, unsorted_rows in sorted(grouped.items()):
        rows = sorted(unsorted_rows, key=lambda item: item.country_code)
        values = [row.value for row in rows]
        direction = "lower_is_better" if metric_id in NEGATIVE_METRICS else "higher_is_better"
        method_version, anchors = CURRENT_THRESHOLD_METHODS[metric_id]
        broad_icp = metric_id == "household_consumption_price_level_us_100"
        algorithms = {
            name: _algorithm_scores(
                values, name, direction, anchors, metric_id=metric_id, broad_icp=broad_icp
            )
            for name in ("winsorized_minmax", "percentile_rank", "threshold")
        }
        ordered_values = sorted(values)
        trimmed = ordered_values[1:-1] if len(values) > 2 else ordered_values
        full_threshold = algorithms["threshold"]
        trimmed_threshold = _algorithm_scores(
            trimmed, "threshold", direction, anchors, metric_id=metric_id, broad_icp=broad_icp
        )
        midpoint = sum(values) / len(values)
        width = max(max(values) - min(values), 1.0) * 0.01
        clustered = [midpoint - width / 2 + width * i / 19 for i in range(20)]
        cluster_spreads = {
            name: round(max(scores) - min(scores), 4)
            for name in ("winsorized_minmax", "percentile_rank", "threshold")
            for scores in [
                _algorithm_scores(
                    clustered, name, direction, anchors, metric_id=metric_id, broad_icp=broad_icp
                )
            ]
        }
        result = {
            "selected_method_version": method_version,
            "anchors": [list(item) for item in anchors],
            "observed_raw_range": [min(values), max(values)],
            "score_ranges": {
                name: [round(min(scores), 3), round(max(scores), 3)]
                for name, scores in algorithms.items()
            },
            "score_standard_deviation": {
                name: round(pstdev(scores), 4) for name, scores in algorithms.items()
            },
            "country_set_test": {
                "scenario": "remove one minimum and one maximum raw observation",
                "threshold_score_range_full": [
                    round(min(full_threshold), 3),
                    round(max(full_threshold), 3),
                ],
                "threshold_score_range_trimmed": [
                    round(min(trimmed_threshold), 3),
                    round(max(trimmed_threshold), 3),
                ],
            },
            "tight_cluster_test_score_spread": cluster_spreads,
            "selection_reason": "Fixed domain anchors are composition-stable and do not force small observed differences across the full score range.",
        }
        if broad_icp:
            result["selection_reason"] = (
                "Discrete broad bands prevent ICP extrapolations from implying a precise country ranking."
            )
        if metric_id == "infrastructure_readiness_composite":
            result["component_experiment"] = _infrastructure_experiment(rows)
        results[metric_id] = result
    redundancy = {}
    governance_ids = ("political_stability", "rule_of_law")
    if all(metric in grouped for metric in governance_ids):
        aligned = {
            metric: {row.country_code: row.value for row in grouped[metric]}
            for metric in governance_ids
        }
        countries = sorted(set(aligned[governance_ids[0]]) & set(aligned[governance_ids[1]]))
        left = [aligned[governance_ids[0]][country] for country in countries]
        right = [aligned[governance_ids[1]][country] for country in countries]
        spearman = correlation(_average_ranks(left), _average_ranks(right))
        redundancy["political_stability__rule_of_law"] = {
            "country_count": len(countries),
            "spearman_correlation": round(spearman, 4),
            "review_threshold": 0.9,
            "review_required": abs(spearman) > 0.9,
            "decision": (
                "Retain both with distinct labels and inspect ranking contribution; "
                "high correlation alone is not an automatic rejection."
            ),
        }
    return {
        "schema_version": "scoring-sensitivity-2.0",
        "criteria": results,
        "redundancy": redundancy,
    }
