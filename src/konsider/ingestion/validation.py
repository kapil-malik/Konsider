"""Structural and criterion-level product-readiness validation."""

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

RELEASE_SCHEMA_VERSION = "konsider-release-3.0"
RANGES = {
    "ambient_pm25_population_weighted": (0, 500), "intentional_homicide_rate": (0, 200),
    "uhc_service_coverage_index": (0, 100), "household_consumption_price_level_us_100": (1, 500),
    "women_peace_security_index": (0, 1), "women_legal_economic_equality": (0, 100),
    "infrastructure_readiness_composite": (0, 100),
}
REQUIRED_UNITS = {
    "ambient_pm25_population_weighted": "micrograms_per_cubic_metre",
    "intentional_homicide_rate": "per_100000_people", "uhc_service_coverage_index": "index_0_100",
    "household_consumption_price_level_us_100": "index_us_100",
    "women_peace_security_index": "index_0_1", "women_legal_economic_equality": "index_0_100",
    "infrastructure_readiness_composite": "index_0_100",
}
SOURCE_RULES = {
    "ambient_pm25_population_weighted": ({"modelled"}, {"wdi_distribution", "modelled_estimate", "cross_country_comparison_only"}),
    "intentional_homicide_rate": ({"reported_or_estimated"}, {"wdi_distribution", "secondary_distribution", "cross_country_comparability_caution"}),
    "uhc_service_coverage_index": ({"estimated"}, {"wdi_distribution", "population_level_not_expat_access"}),
    "household_consumption_price_level_us_100": ({"derived"}, {"wdi_distribution", "derived_from_official_ppp_and_exchange_rate", "broad_band_only", "not_for_precise_strict_ranking"}),
    "women_legal_economic_equality": ({"composite"}, {"world_bank_primary_dataset", "de_jure_legal_framework", "not_de_facto_outcomes"}),
    "infrastructure_readiness_composite": ({"derived_composite"}, {"wdi_distribution", "equal_weight_three_components", "mixed_reference_years"}),
    "women_peace_security_index": ({"composite"}, {"mixed_reference_years", "possible_underlying_imputation"}),
}
FRESHNESS_MAX_AGE = {
    "ambient_pm25_population_weighted": 3, "intentional_homicide_rate": 5,
    "uhc_service_coverage_index": 3, "household_consumption_price_level_us_100": 2,
    "women_legal_economic_equality": 2, "infrastructure_readiness_composite": 4,
}
EXPECTED_SCORING_METHODS = {
    "ambient_pm25_population_weighted": "pm25_health_bands_v1",
    "intentional_homicide_rate": "homicide_risk_bands_v1",
    "uhc_service_coverage_index": "uhc_coverage_bands_v1",
    "household_consumption_price_level_us_100": "icp_relative_cost_bands_v2",
    "women_legal_economic_equality": "wbl_legal_equality_bands_v1",
    "infrastructure_readiness_composite": "infrastructure_readiness_bands_v1",
}


def validate_release(
    observations: list[MetricObservation], scores: list[MetricScore], artifacts: list[RawArtifact],
    attempts: list[SourceAttempt] | None = None, sources: list[SourceRegistration] | None = None,
    *, min_criteria: int = 5, min_country_coverage: int = 18, product_country_coverage: int = 20,
    product_min_ready: int = 5, schema_version: str = RELEASE_SCHEMA_VERSION,
    previous_observations: list[MetricObservation] | None = None, as_of_year: int = 2026,
) -> ValidationReport:
    attempts, sources = attempts or [], sources or []
    issues: list[ValidationIssue] = []
    artifact_by_id = {artifact.artifact_id: artifact for artifact in artifacts}
    source_by_id = {source.source_id: source for source in sources}
    source_by_metric = {source.criterion_id: source for source in sources}
    keys = Counter((item.country_code, item.metric_id, item.reference_end) for item in observations)
    coverage: dict[str, set[str]] = defaultdict(set)
    observation_ids = {item.observation_id for item in observations}

    def issue(code, severity, message, *, scope="structural", country=None, metric=None):
        issues.append(ValidationIssue(code, severity, message, scope, country, metric))

    if schema_version != RELEASE_SCHEMA_VERSION:
        issue("incompatible_schema", "error", f"Expected {RELEASE_SCHEMA_VERSION}, got {schema_version}.")

    for source in sources:
        if source.license_name != "Creative Commons Attribution 4.0 International":
            issue("licence_not_product_ready", "blocker", f"{source.source_id} lacks audited CC BY 4.0.", scope="product_readiness", metric=source.criterion_id)
        if "may be redistributed" not in source.redistribution and "explicitly licensed" not in source.redistribution:
            issue("redistribution_not_verified", "blocker", source.redistribution, scope="product_readiness", metric=source.criterion_id)
        if not source.license_url or not source.license_evidence or not source.attribution:
            issue("licence_contract_incomplete", "error", f"Licence evidence incomplete for {source.source_id}.", metric=source.criterion_id)

    for artifact in artifacts:
        source = source_by_id.get(artifact.source_id)
        if artifact.artifact_id != f"sha256:{artifact.sha256}":
            issue("artifact_id_checksum_mismatch", "error", artifact.artifact_id)
        if artifact.http_status < 200 or artifact.http_status >= 300 or not artifact.final_url:
            issue("invalid_http_metadata", "error", f"HTTP retrieval metadata invalid for {artifact.artifact_id}.")
        try:
            datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
        except ValueError:
            issue("invalid_retrieval_timestamp", "error", artifact.artifact_id)
        if source and artifact.parser_version != source.parser_version:
            issue("artifact_parser_version_mismatch", "error", artifact.artifact_id, metric=source.criterion_id)
        if source and artifact.requested_url not in source.download_urls:
            issue("unregistered_download_url", "error", artifact.requested_url, metric=source.criterion_id)
        path = Path(artifact.path)
        if sources and not path.exists():
            issue("local_raw_artifact_missing", "error", artifact.artifact_id)
        elif path.exists():
            body = path.read_bytes()
            if len(body) != artifact.byte_length or hashlib.sha256(body).hexdigest() != artifact.sha256:
                issue("artifact_checksum_failed", "error", artifact.artifact_id)

    for observation in observations:
        metric, country = observation.metric_id, observation.country_code
        coverage[metric].add(country)
        source = source_by_id.get(observation.source_id)
        if country not in COUNTRIES:
            issue("unknown_country", "error", "Country outside experiment set.", country=country, metric=metric)
        if keys[(country, metric, observation.reference_end)] > 1:
            issue("duplicate_observation", "error", "Duplicate country/metric/period.", country=country, metric=metric)
        if sources and (not source or source.criterion_id != metric):
            issue("source_contract_mismatch", "error", "Observation source is not registered for criterion.", country=country, metric=metric)
        elif source and observation.parser_version != source.parser_version:
            issue("observation_parser_version_mismatch", "error", observation.parser_version, country=country, metric=metric)
        if len(observation.raw_artifact_ids) != len(set(observation.raw_artifact_ids)):
            issue("duplicate_artifact_reference", "error", "Duplicate raw artifact reference.", country=country, metric=metric)
        record_artifacts = {record.artifact_id for record in observation.source_records}
        if not observation.source_records or set(observation.raw_artifact_ids) != record_artifacts or not record_artifacts <= artifact_by_id.keys():
            issue("incomplete_record_provenance", "error", "Exact artifact and source record lineage is required.", country=country, metric=metric)
        if any(not record.locator or not record.record_id for record in observation.source_records) or not observation.method_version:
            issue("incomplete_method_provenance", "error", "Record ID/locator and method versions are required.", country=country, metric=metric)
        if REQUIRED_UNITS.get(metric) != observation.unit:
            issue("invalid_unit", "error", f"Expected {REQUIRED_UNITS.get(metric)}, got {observation.unit}.", country=country, metric=metric)
        low, high = RANGES.get(metric, (-float("inf"), float("inf")))
        if not low <= observation.value <= high:
            issue("implausible_value", "error", f"Value {observation.value} outside [{low}, {high}].", country=country, metric=metric)
        allowed_types, flags = SOURCE_RULES[metric]
        if observation.observation_type not in allowed_types:
            issue("invalid_observation_type", "error", observation.observation_type, country=country, metric=metric)
        missing_flags = flags - set(observation.quality_flags)
        if missing_flags:
            issue("missing_quality_flags", "error", f"Missing flags {sorted(missing_flags)}.", country=country, metric=metric)
        if observation.components:
            component_artifacts = {component.source_record.artifact_id for component in observation.components}
            if not component_artifacts <= record_artifacts or any(component.reference_year <= 0 for component in observation.components):
                issue("component_provenance_invalid", "error", "Derived components must reference exact source records and years.", country=country, metric=metric)
        if metric == "household_consumption_price_level_us_100" and len(observation.components) != 2:
            issue("icp_component_contract", "error", "ICP PLI requires PPP and exchange-rate components.", country=country, metric=metric)
        if metric == "infrastructure_readiness_composite":
            component_ids = {component.component_id for component in observation.components}
            expected = {"internet_users_percent", "fixed_broadband_per_100", "lpi_infrastructure_quality"}
            if component_ids != expected:
                issue("infrastructure_component_contract", "error", f"Expected {sorted(expected)}.", country=country, metric=metric)

    expected_attempts = {(source.source_id, source.criterion_id, code) for source in sources for code in COUNTRIES}
    actual_attempts = {(item.source_id, item.criterion_id, item.country_code) for item in attempts}
    if sources and expected_attempts != actual_attempts:
        issue("attempt_matrix_incomplete", "error", f"Attempt matrix missing {len(expected_attempts - actual_attempts)}, extra {len(actual_attempts - expected_attempts)}.")
    if len(actual_attempts) != len(attempts):
        issue("duplicate_attempt", "error", "Duplicate source/country/criterion attempt.")
    for attempt in attempts:
        if attempt.status not in {"success", "no_data", "failed", "rejected"}:
            issue("invalid_attempt_status", "error", attempt.status, country=attempt.country_code, metric=attempt.criterion_id)
        if attempt.status == "success" and (not attempt.observation_id or attempt.observation_id not in observation_ids):
            issue("attempt_observation_missing", "error", "Successful attempt must reference an observation.", country=attempt.country_code, metric=attempt.criterion_id)
        if attempt.status != "success" and not attempt.reason:
            issue("attempt_reason_missing", "error", "Non-success attempt needs a reason.", country=attempt.country_code, metric=attempt.criterion_id)

    if len(coverage) < min_criteria:
        issue("insufficient_criteria", "error", f"Only {len(coverage)} criteria; need {min_criteria}.")
    for metric, countries in sorted(coverage.items()):
        if len(countries) < min_country_coverage:
            issue("insufficient_coverage", "error", f"Coverage {len(countries)}/20.", metric=metric)
        elif len(countries) < product_country_coverage:
            issue("partial_product_coverage", "blocker", f"Product coverage {len(countries)}/20.", scope="product_readiness", metric=metric)

    score_keys = Counter((score.country_code, score.criterion_id) for score in scores)
    for score in scores:
        if not 1 <= score.score <= 10 or not set(score.input_observation_ids) <= observation_ids:
            issue("invalid_score_lineage", "error", "Score range or lineage invalid.", country=score.country_code, metric=score.criterion_id)
        if score_keys[(score.country_code, score.criterion_id)] > 1:
            issue("duplicate_score", "error", "Duplicate country/criterion score.", country=score.country_code, metric=score.criterion_id)
        expected_method = EXPECTED_SCORING_METHODS.get(score.criterion_id)
        if expected_method and score.method_version != expected_method:
            issue("scoring_method_not_product_ready", "blocker", f"Expected {expected_method}, got {score.method_version}.", scope="product_readiness", country=score.country_code, metric=score.criterion_id)

    if sources:
        for metric, source in source_by_metric.items():
            rows = [row for row in observations if row.metric_id == metric]
            max_age = FRESHNESS_MAX_AGE.get(metric)
            if max_age is not None:
                for row in rows:
                    years = [component.reference_year for component in row.components] or [int(row.reference_end[:4])]
                    if max(as_of_year - year for year in years) > max_age:
                        issue("source_stale", "blocker", f"Source year(s) {sorted(years)} exceed {max_age}-year freshness limit.", scope="product_readiness", country=row.country_code, metric=metric)

    if previous_observations:
        previous = {(item.country_code, item.metric_id): item for item in previous_observations}
        for observation in observations:
            old = previous.get((observation.country_code, observation.metric_id))
            if old and old.value != 0:
                change = abs(observation.value - old.value) / abs(old.value)
                if change > 0.25:
                    issue("material_change_review", "warning", f"Value changed {change:.1%} from previous release.", scope="product_readiness", country=observation.country_code, metric=observation.metric_id)

    structural_passed = not any(item.severity == "error" and item.scope == "structural" for item in issues)
    criterion_readiness = {}
    for metric in sorted(source_by_metric):
        success_count = sum(item.criterion_id == metric and item.status == "success" for item in attempts)
        blockers = [item for item in issues if item.metric_id == metric and item.severity in {"error", "blocker"}]
        criterion_readiness[metric] = (
            structural_passed and len(coverage.get(metric, set())) >= product_country_coverage
            and success_count >= product_country_coverage and not blockers
        )
    ready_count = sum(criterion_readiness.values())
    product_ready = structural_passed and ready_count >= product_min_ready
    if sources and ready_count < product_min_ready:
        issue("insufficient_product_ready_criteria", "blocker", f"Only {ready_count} criteria ready; need {product_min_ready}.", scope="product_readiness")
    return ValidationReport(
        structural_passed=structural_passed, product_ready=product_ready,
        observation_count=len(observations), score_count=len(scores), attempt_count=len(attempts),
        criterion_coverage={metric: len(countries) for metric, countries in coverage.items()},
        criterion_readiness=criterion_readiness, ready_criterion_count=ready_count,
        status_counts=dict(Counter(item.status for item in attempts)), issues=tuple(issues),
    )
