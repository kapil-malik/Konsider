"""Country metric-breakdown transport contracts."""

from __future__ import annotations

from konsider.api.models.common import (
    ApiModel,
    CountryResponse,
    CriterionResponse,
    ObservationResponse,
    SourceResponse,
    VersionedResponse,
)


class CountryCriterionMetricResponse(ApiModel):
    criterion: CriterionResponse
    normalized_score: float
    scoring_method_version: str
    transform: str
    direction: str
    input_observation_ids: list[str]
    observations: list[ObservationResponse]
    source: SourceResponse


class CountryMetricResponse(VersionedResponse):
    country: CountryResponse
    criteria: list[CountryCriterionMetricResponse]
