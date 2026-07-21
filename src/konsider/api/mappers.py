"""Pure mappings from Phase 2A service dictionaries to typed public responses."""

from __future__ import annotations

from typing import Any

from konsider.api.models.catalog import CatalogResponse
from konsider.api.models.common import ObservationResponse, SourceRecordResponse, SourceResponse
from konsider.api.models.countries import CountryMetricResponse
from konsider.api.models.rankings import ComparisonResponse, RankingResponse


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


def ranking_response(value: dict[str, Any]) -> RankingResponse:
    return RankingResponse.model_validate(_ranking_payload(value, "rankings"))


def comparison_response(value: dict[str, Any]) -> ComparisonResponse:
    return ComparisonResponse.model_validate(_ranking_payload(value, "countries"))


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
                    "criterion": item["criterion"],
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
