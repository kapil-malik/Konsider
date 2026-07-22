"""Catalog and health transport contracts."""

from __future__ import annotations

from konsider.api.models.common import (
    ApiModel,
    CountryResponse,
    CriterionResponse,
    CriterionSourceResponse,
    VersionedResponse,
)


class ProfileResponse(ApiModel):
    id: str
    name: str
    description: str
    weights: dict[str, float]


class CatalogCriterionResponse(CriterionResponse):
    sources: list[CriterionSourceResponse]


class HealthResponse(VersionedResponse):
    status: str
    country_count: int
    enabled_criterion_count: int
    ready_for_rankings: bool


class CatalogResponse(VersionedResponse):
    countries: list[CountryResponse]
    criteria: list[CatalogCriterionResponse]
    profiles: list[ProfileResponse]
