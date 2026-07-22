"""Shared API transport contracts."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VersionedResponse(ApiModel):
    release_id: str
    release_schema_version: str
    catalog_schema_version: str
    scoring_method_versions: list[str]


class CountryResponse(ApiModel):
    code: str = Field(pattern=r"^[A-Z]{3}$")
    display_name: str
    region: str


class SourceResponse(ApiModel):
    source_id: str
    publisher: str
    source_version: str
    dataset_version: str
    canonical_page_url: HttpUrl
    attribution: str


class CriterionSourceResponse(SourceResponse):
    reference_period: str


class CriterionResponse(ApiModel):
    id: str
    display_name: str
    category: str
    description: str
    direction: str
    raw_unit: str
    interpretation: str
    caveats: list[str]
    quality_limitations: list[str]
    ready: bool
    default_enabled: bool
    experimental: bool
    scoring_method_version: str


class SourceRecordResponse(ApiModel):
    locator: str
    record_id: str


class ObservationResponse(ApiModel):
    observation_id: str
    value: float
    unit: str
    reference_start: date
    reference_end: date
    observation_method_version: str
    parser_version: str
    quality_flags: list[str]
    source_records: list[SourceRecordResponse]


class ErrorBody(ApiModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorResponse(ApiModel):
    error: ErrorBody
