"""Catalog and health transport contracts."""

from __future__ import annotations

from typing import Literal

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
    enabled: bool
    coverage_mode: Literal[
        "GLOBAL_CORE",
        "CONDITIONAL_COMPLETE_CASE",
        "DIAGNOSTIC_ONLY",
    ]
    valid_country_count: int
    stable_country_count: int
    coverage_percentage: float
    pcc_activation_threshold: float | None
    missing_country_count: int
    concise_caveat: str | None
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
