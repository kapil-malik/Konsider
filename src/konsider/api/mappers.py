"""Pure mappings from Phase 2A service dictionaries to typed public responses."""

from __future__ import annotations

from typing import Any

from konsider.api.models.catalog import CatalogResponse
from konsider.api.models.common import ObservationResponse, SourceRecordResponse, SourceResponse
from konsider.api.models.countries import CountryMetricResponse
from konsider.api.models.rankings import ComparisonResponse, RankingResponse
from konsider.domain.uncertainty_models import (
    UncertaintyComparisonResult,
    UncertaintyRankingResult,
    UncertaintyStatus,
)


def _source(value: dict[str, Any]) -> SourceResponse:
    return SourceResponse(
        source_id=value["source_id"],
        publisher=value["publisher"],
        source_version=value["source_version"],
        dataset_version=value["dataset_version"],
        canonical_page_url=value["canonical_page_url"],
        attribution=value["attribution"],
    )


def _observation(value: dict[str, Any]) -> ObservationResponse:
    return ObservationResponse(
        observation_id=value["observation_id"],
        value=value["value"],
        unit=value["unit"],
        reference_start=value["reference_start"],
        reference_end=value["reference_end"],
        observation_method_version=value["method_version"],
        parser_version=value["parser_version"],
        quality_flags=value["quality_flags"],
        source_records=[
            SourceRecordResponse(locator=item["locator"], record_id=item["record_id"])
            for item in value["source_records"]
        ],
    )


def catalog_response(value: dict[str, Any]) -> CatalogResponse:
    return CatalogResponse.model_validate(value)


def _ranking_payload(value: dict[str, Any], collection_key: str) -> dict[str, Any]:
    payload = dict(value)
    countries = []
    for country in value[collection_key]:
        row = dict(country)
        row["contributions"] = [
            {
                "criterion_id": contribution["criterion_id"],
                "criterion_name": contribution["criterion_name"],
                "score": contribution["score"],
                "normalized_weight": contribution["normalized_weight"],
                "contribution": contribution["contribution"],
                "scoring_method_version": contribution["scoring_method_version"],
                "caveats": contribution["caveats"],
                "quality_limitations": contribution["quality_limitations"],
                "experimental": contribution["experimental"],
                "observations": [
                    _observation(item).model_dump(mode="json")
                    for item in contribution["input_observations"]
                ],
                "source": _source(contribution["source"]).model_dump(mode="json"),
            }
            for contribution in country["contributions"]
        ]
        countries.append(row)
    payload[collection_key] = countries
    return payload


def _excluded_payload(
    value: UncertaintyRankingResult,
    excluded_countries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_codes = {item.country_code for item in value.r0_top_k.rankings}
    return [
        {
            **item,
            "baseline_top_k_member": item["country_code"] in baseline_codes,
        }
        for item in excluded_countries
    ]


def _uncertainty_payload(
    value: UncertaintyRankingResult,
    *,
    returned_result_count: int,
) -> dict[str, Any]:
    serialized = value.to_dict()
    policy = serialized["policy"]
    if value.status == UncertaintyStatus.COVERAGE_LIMIT_EXCEEDED:
        kth_eligible_score = None
    elif value.r1_top_k is not None:
        kth_eligible_score = value.r1_top_k.kth_score
    else:
        kth_eligible_score = value.r0_top_k.kth_score
    return {
        "release_id": value.release_id,
        "release_schema_version": value.release_schema_version,
        "catalog_schema_version": value.catalog_schema_version,
        "scoring_method_versions": list(value.scoring_method_versions),
        "resolved_profile_id": value.resolved_profile_id,
        "normalized_weights": (
            value.final_normalized_weights
            if value.final_normalized_weights is not None
            else value.baseline_normalized_weights
        ),
        "all_zero_behavior": "equal_weights_across_all_enabled_fcc",
        "country_tie_breaker": value.policy.country_tie_breaker,
        "rounding_tolerance": value.policy.rounding_tolerance,
        "total_eligible_country_count": value.eligible_country_count,
        "returned_result_count": returned_result_count,
        "stable_universe_size": value.stable_country_count,
        "eligible_universe_size": value.eligible_country_count,
        "excluded_country_count": value.excluded_country_count,
        "ranking_coverage_mode": (
            "CONDITIONAL_COMPLETE_CASE" if value.r1_top_k is not None else "GLOBAL_CORE"
        ),
        "uncertainty_status": value.status.value,
        "coverage_band": value.coverage_band.value,
        "reason_codes": list(value.reason_codes),
        "message_code": value.status.value,
        "active_fcc_ids": list(value.active_fcc_ids),
        "active_pcc_ids": list(value.active_pcc_ids),
        "ignored_pcc": serialized["ignored_pcc"],
        "robustness_k": value.requested_top_k,
        "kth_eligible_score": kth_eligible_score,
        "potential_excluded_entrants": [
            item.country_code for item in value.excluded_countries if item.could_enter_top_k
        ],
        "baseline_top_k_country_codes": [item.country_code for item in value.r0_top_k.rankings],
        "baseline_kth_score": value.r0_top_k.kth_score,
        "baseline_boundary_tie_count": value.r0_top_k.boundary_tie_count,
        "baseline_returned_result_count": (value.r0_top_k.returned_result_count),
        "policy_version": value.policy.policy_version,
        "policy_thresholds": {
            key: policy[key]
            for key in (
                "stable_universe_id",
                "stable_country_count",
                "pcc_min_valid_country_count",
                "preferred_missing_union_max",
                "hard_missing_union_max",
                "min_eligible_country_count",
                "pcc_activation_raw_weight_min",
                "diagnostic_score_max",
                "rounding_tolerance",
            )
        },
        "excluded_countries": _excluded_payload(
            value,
            serialized["excluded_countries"],
        ),
    }


def ranking_response(value: UncertaintyRankingResult) -> RankingResponse:
    payload = _uncertainty_payload(
        value,
        returned_result_count=len(value.rankings),
    )
    payload["rankings"] = value.to_dict()["rankings"]
    return RankingResponse.model_validate(_ranking_payload(payload, "rankings"))


def comparison_response(
    value: UncertaintyComparisonResult,
) -> ComparisonResponse:
    ranking = value.ranking_result
    payload = _uncertainty_payload(
        ranking,
        returned_result_count=len(value.countries),
    )
    serialized = value.to_dict()
    payload.update(
        {
            "requested_country_codes": list(value.requested_country_codes),
            "comparison_country_count": len(value.requested_country_codes),
            "country_summaries": serialized["country_summaries"],
            "criterion_rows": serialized["criterion_rows"],
            "requested_excluded_countries": _excluded_payload(
                ranking,
                serialized["excluded_countries"],
            ),
            "countries": serialized["countries"],
        }
    )
    return ComparisonResponse.model_validate(_ranking_payload(payload, "countries"))


def country_metric_response(value: dict[str, Any]) -> CountryMetricResponse:
    return CountryMetricResponse.model_validate(
        {
            "release_id": value["release_id"],
            "release_schema_version": value["release_schema_version"],
            "catalog_schema_version": value["catalog_schema_version"],
            "scoring_method_versions": value["scoring_method_versions"],
            "country": value["country"],
            "criteria": [
                {
                    "criterion": {
                        key: field for key, field in item["criterion"].items() if key != "coverage"
                    },
                    "normalized_score": item["score"]["score"],
                    "scoring_method_version": item["score"]["method_version"],
                    "transform": item["score"]["transform"],
                    "direction": item["score"]["direction"],
                    "input_observation_ids": item["score"]["input_observation_ids"],
                    "observations": [
                        _observation(observation).model_dump(mode="json")
                        for observation in item["observations"]
                    ],
                    "source": _source(item["source"]).model_dump(mode="json"),
                }
                for item in value["criteria"]
            ],
        }
    )
