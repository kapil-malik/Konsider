"""Publication-gate validation for observations, scores, and provenance."""

from __future__ import annotations

from collections import Counter, defaultdict

from konsider.ingestion.countries import COUNTRIES
from konsider.ingestion.models import MetricObservation, MetricScore, RawArtifact, ValidationIssue, ValidationReport

RANGES = {
    "ambient_pm25_population_weighted": (0, 500),
    "intentional_homicide_rate": (0, 200),
    "uhc_service_coverage_index": (0, 100),
    "household_consumption_price_level_us_100": (1, 500),
    "women_peace_security_index": (0, 1),
}
REQUIRED_UNITS = {
    "ambient_pm25_population_weighted": "micrograms_per_cubic_metre",
    "intentional_homicide_rate": "per_100000_people",
    "uhc_service_coverage_index": "index_0_100",
    "household_consumption_price_level_us_100": "index_us_100",
    "women_peace_security_index": "index_0_1",
}


def validate_release(
    observations: list[MetricObservation], scores: list[MetricScore], artifacts: list[RawArtifact],
    *, min_criteria: int = 5, min_country_coverage: int = 18,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    artifact_ids = {artifact.artifact_id for artifact in artifacts}
    keys = Counter((item.country_code, item.metric_id, item.reference_end) for item in observations)
    coverage: dict[str, set[str]] = defaultdict(set)
    observation_ids = {item.observation_id for item in observations}
    for observation in observations:
        coverage[observation.metric_id].add(observation.country_code)
        if observation.country_code not in COUNTRIES:
            issues.append(ValidationIssue("unknown_country", "error", "Country is outside the experiment set.", observation.country_code, observation.metric_id))
        if keys[(observation.country_code, observation.metric_id, observation.reference_end)] > 1:
            issues.append(ValidationIssue("duplicate_observation", "error", "Duplicate country/metric/period.", observation.country_code, observation.metric_id))
        expected_unit = REQUIRED_UNITS.get(observation.metric_id)
        if expected_unit != observation.unit:
            issues.append(ValidationIssue("invalid_unit", "error", f"Expected {expected_unit}, got {observation.unit}.", observation.country_code, observation.metric_id))
        low, high = RANGES.get(observation.metric_id, (-float("inf"), float("inf")))
        if not low <= observation.value <= high:
            issues.append(ValidationIssue("implausible_value", "error", f"Value {observation.value} outside [{low}, {high}].", observation.country_code, observation.metric_id))
        if not observation.raw_artifact_ids or not set(observation.raw_artifact_ids) <= artifact_ids:
            issues.append(ValidationIssue("incomplete_provenance", "error", "Raw artifact lineage is missing.", observation.country_code, observation.metric_id))
        year = int(observation.reference_end[:4])
        if observation.metric_id != "household_consumption_price_level_us_100" and year < 2021:
            issues.append(ValidationIssue("stale_observation", "warning", f"Latest available observation is from {year}.", observation.country_code, observation.metric_id))
    if len(coverage) < min_criteria:
        issues.append(ValidationIssue("insufficient_criteria", "error", f"Only {len(coverage)} criteria; need {min_criteria}."))
    for metric_id, countries in sorted(coverage.items()):
        if len(countries) < min_country_coverage:
            missing = sorted(set(COUNTRIES) - countries)
            issues.append(ValidationIssue("insufficient_coverage", "error", f"Coverage {len(countries)}/20; missing {missing}.", metric_id=metric_id))
        elif len(countries) < len(COUNTRIES):
            missing = sorted(set(COUNTRIES) - countries)
            issues.append(ValidationIssue("partial_coverage", "warning", f"Coverage {len(countries)}/20; missing {missing}.", metric_id=metric_id))
    for score in scores:
        if not 1 <= score.score <= 10:
            issues.append(ValidationIssue("invalid_score", "error", f"Score {score.score} outside [1, 10].", score.country_code, score.criterion_id))
        if not set(score.input_observation_ids) <= observation_ids:
            issues.append(ValidationIssue("score_lineage_missing", "error", "Score input observation is missing.", score.country_code, score.criterion_id))
    return ValidationReport(
        passed=not any(issue.severity == "error" for issue in issues),
        observation_count=len(observations), score_count=len(scores),
        criterion_coverage={metric: len(countries) for metric, countries in coverage.items()},
        issues=tuple(issues),
    )
