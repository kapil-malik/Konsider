"""Structural publication validation separated from product-readiness review."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from konsider.ingestion.countries import COUNTRIES
from konsider.ingestion.models import (
    MetricObservation, MetricScore, RawArtifact, SourceAttempt, SourceRegistration,
    ValidationIssue, ValidationReport,
)

RELEASE_SCHEMA_VERSION = "konsider-release-2.0"
RANGES = {
    "ambient_pm25_population_weighted": (0, 500), "intentional_homicide_rate": (0, 200),
    "uhc_service_coverage_index": (0, 100), "household_consumption_price_level_us_100": (1, 500),
    "women_peace_security_index": (0, 1),
}
REQUIRED_UNITS = {
    "ambient_pm25_population_weighted": "micrograms_per_cubic_metre",
    "intentional_homicide_rate": "per_100000_people", "uhc_service_coverage_index": "index_0_100",
    "household_consumption_price_level_us_100": "index_us_100", "women_peace_security_index": "index_0_1",
}
SOURCE_RULES = {
    "ambient_pm25_population_weighted": (2023, {"modelled"}, {"modelled_estimate", "uncertainty_interval_required"}),
    "intentional_homicide_rate": (2021, {"reported_or_estimated"}, {"secondary_distribution", "cross_country_comparability_caution"}),
    "uhc_service_coverage_index": (2023, {"estimated"}, {"population_level_not_expat_access"}),
    "household_consumption_price_level_us_100": (2021, {"derived"}, {"derived_from_official_ppp_and_exchange_rate", "not_for_precise_strict_ranking"}),
    "women_peace_security_index": (2025, {"composite"}, {"mixed_reference_years", "possible_underlying_imputation"}),
}


def validate_release(
    observations: list[MetricObservation], scores: list[MetricScore], artifacts: list[RawArtifact],
    attempts: list[SourceAttempt] | None = None, sources: list[SourceRegistration] | None = None,
    *, min_criteria: int = 5, min_country_coverage: int = 18,
    schema_version: str = RELEASE_SCHEMA_VERSION,
    previous_observations: list[MetricObservation] | None = None,
) -> ValidationReport:
    attempts = attempts or []
    sources = sources or []
    issues: list[ValidationIssue] = []
    artifact_by_id = {artifact.artifact_id: artifact for artifact in artifacts}
    keys = Counter((item.country_code, item.metric_id, item.reference_end) for item in observations)
    coverage: dict[str, set[str]] = defaultdict(set)
    observation_ids = {item.observation_id for item in observations}
    if schema_version != RELEASE_SCHEMA_VERSION:
        issues.append(ValidationIssue("incompatible_schema", "error", f"Expected {RELEASE_SCHEMA_VERSION}, got {schema_version}."))

    for artifact in artifacts:
        if artifact.artifact_id != f"sha256:{artifact.sha256}":
            issues.append(ValidationIssue("artifact_id_checksum_mismatch", "error", artifact.artifact_id))
        if artifact.http_status < 200 or artifact.http_status >= 300 or not artifact.final_url:
            issues.append(ValidationIssue("invalid_http_metadata", "error", f"HTTP retrieval metadata invalid for {artifact.artifact_id}."))
        try:
            datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
        except ValueError:
            issues.append(ValidationIssue("invalid_retrieval_timestamp", "error", artifact.artifact_id))
        path = Path(artifact.path)
        if path.exists():
            body = path.read_bytes()
            if len(body) != artifact.byte_length or hashlib.sha256(body).hexdigest() != artifact.sha256:
                issues.append(ValidationIssue("artifact_checksum_failed", "error", artifact.artifact_id))

    for observation in observations:
        coverage[observation.metric_id].add(observation.country_code)
        if observation.country_code not in COUNTRIES:
            issues.append(ValidationIssue("unknown_country", "error", "Country outside experiment set.", country_code=observation.country_code, metric_id=observation.metric_id))
        if keys[(observation.country_code, observation.metric_id, observation.reference_end)] > 1:
            issues.append(ValidationIssue("duplicate_observation", "error", "Duplicate country/metric/period.", country_code=observation.country_code, metric_id=observation.metric_id))
        if len(observation.raw_artifact_ids) != len(set(observation.raw_artifact_ids)):
            issues.append(ValidationIssue("duplicate_artifact_reference", "error", "Duplicate raw artifact reference.", country_code=observation.country_code, metric_id=observation.metric_id))
        record_artifacts = {record.artifact_id for record in observation.source_records}
        if not observation.source_records or set(observation.raw_artifact_ids) != record_artifacts or not record_artifacts <= artifact_by_id.keys():
            issues.append(ValidationIssue("incomplete_record_provenance", "error", "Exact artifact and source record lineage is required.", country_code=observation.country_code, metric_id=observation.metric_id))
        if any(not record.locator for record in observation.source_records) or not observation.parser_version or not observation.method_version:
            issues.append(ValidationIssue("incomplete_method_provenance", "error", "Record locator, parser, and method versions are required.", country_code=observation.country_code, metric_id=observation.metric_id))
        expected_unit = REQUIRED_UNITS.get(observation.metric_id)
        if expected_unit != observation.unit:
            issues.append(ValidationIssue("invalid_unit", "error", f"Expected {expected_unit}, got {observation.unit}.", country_code=observation.country_code, metric_id=observation.metric_id))
        low, high = RANGES.get(observation.metric_id, (-float("inf"), float("inf")))
        if not low <= observation.value <= high:
            issues.append(ValidationIssue("implausible_value", "error", f"Value {observation.value} outside [{low}, {high}].", country_code=observation.country_code, metric_id=observation.metric_id))
        min_year, types, flags = SOURCE_RULES[observation.metric_id]
        year = int(observation.reference_end[:4])
        if year < min_year:
            issues.append(ValidationIssue("source_stale", "error", f"{year} is older than source rule {min_year}.", country_code=observation.country_code, metric_id=observation.metric_id))
        if observation.observation_type not in types:
            issues.append(ValidationIssue("invalid_observation_type", "error", f"Unexpected type {observation.observation_type}.", country_code=observation.country_code, metric_id=observation.metric_id))
        missing_flags = flags - set(observation.quality_flags)
        if missing_flags:
            issues.append(ValidationIssue("missing_quality_flags", "error", f"Missing flags {sorted(missing_flags)}.", country_code=observation.country_code, metric_id=observation.metric_id))
        if observation.metric_id == "ambient_pm25_population_weighted" and (observation.lower_bound is None or observation.upper_bound is None):
            issues.append(ValidationIssue("missing_uncertainty_interval", "error", "WHO PM2.5 interval required.", country_code=observation.country_code, metric_id=observation.metric_id))

    expected_attempts = {(source.source_id, source.criterion_id, code) for source in sources for code in COUNTRIES}
    actual_attempts = {(item.source_id, item.criterion_id, item.country_code) for item in attempts}
    if sources and expected_attempts != actual_attempts:
        missing = len(expected_attempts - actual_attempts)
        extra = len(actual_attempts - expected_attempts)
        issues.append(ValidationIssue("attempt_matrix_incomplete", "error", f"Attempt matrix missing {missing}, extra {extra}."))
    if len(actual_attempts) != len(attempts):
        issues.append(ValidationIssue("duplicate_attempt", "error", "Duplicate source/country/criterion attempt."))
    valid_statuses = {"success", "no_data", "failed", "rejected"}
    for attempt in attempts:
        if attempt.status not in valid_statuses:
            issues.append(ValidationIssue("invalid_attempt_status", "error", attempt.status, country_code=attempt.country_code, metric_id=attempt.criterion_id))
        if attempt.status == "success" and (not attempt.observation_id or attempt.observation_id not in observation_ids):
            issues.append(ValidationIssue("attempt_observation_missing", "error", "Successful attempt must reference an observation.", country_code=attempt.country_code, metric_id=attempt.criterion_id))
        if attempt.status != "success" and not attempt.reason:
            issues.append(ValidationIssue("attempt_reason_missing", "error", "Non-success attempt needs a reason.", country_code=attempt.country_code, metric_id=attempt.criterion_id))

    if len(coverage) < min_criteria:
        issues.append(ValidationIssue("insufficient_criteria", "error", f"Only {len(coverage)} criteria; need {min_criteria}."))
    for metric_id, countries in sorted(coverage.items()):
        if len(countries) < min_country_coverage:
            issues.append(ValidationIssue("insufficient_coverage", "error", f"Coverage {len(countries)}/20.", metric_id=metric_id))
        elif len(countries) < len(COUNTRIES):
            issues.append(ValidationIssue("partial_coverage", "warning", f"Coverage {len(countries)}/20.", metric_id=metric_id))
    for score in scores:
        if not 1 <= score.score <= 10 or not set(score.input_observation_ids) <= observation_ids:
            issues.append(ValidationIssue("invalid_score_lineage", "error", "Score range or lineage invalid.", country_code=score.country_code, metric_id=score.criterion_id))

    if previous_observations:
        previous = {(item.country_code, item.metric_id): item for item in previous_observations}
        for observation in observations:
            old = previous.get((observation.country_code, observation.metric_id))
            if old and old.value != 0:
                change = abs(observation.value - old.value) / abs(old.value)
                if change > 0.25:
                    issues.append(ValidationIssue("material_change_review", "warning", f"Value changed {change:.1%} from previous release.", scope="product_readiness", country_code=observation.country_code, metric_id=observation.metric_id))

    for source in sources:
        if "not treated as permitted" in source.redistribution or "pending" in source.redistribution:
            issues.append(ValidationIssue("licence_clearance_pending", "blocker", f"{source.source_id}: {source.redistribution}", scope="product_readiness", metric_id=source.criterion_id))
        if source.criterion_id == "household_consumption_price_level_us_100":
            issues.append(ValidationIssue("strict_ranking_not_recommended", "blocker", "ICP advises PPPs are not a precise measure for strict country rankings.", scope="product_readiness", metric_id=source.criterion_id))

    structural_passed = not any(issue.severity == "error" and issue.scope == "structural" for issue in issues)
    product_ready = structural_passed and not any(issue.severity in {"error", "blocker"} for issue in issues)
    return ValidationReport(
        structural_passed=structural_passed, product_ready=product_ready,
        observation_count=len(observations), score_count=len(scores), attempt_count=len(attempts),
        criterion_coverage={metric: len(countries) for metric, countries in coverage.items()},
        status_counts=dict(Counter(item.status for item in attempts)), issues=tuple(issues),
    )
