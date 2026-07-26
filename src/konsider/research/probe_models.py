"""Contracts for deterministic, non-publishing feasibility probes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ComponentRule:
    component_id: str
    minimum: float | None = None
    maximum: float | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ComponentRule:
        return cls(
            component_id=str(value["component_id"]),
            minimum=float(value["minimum"]) if value.get("minimum") is not None else None,
            maximum=float(value["maximum"]) if value.get("maximum") is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProbeSource:
    source_candidate_id: str
    publisher: str
    dataset: str
    canonical_page_url: str
    access_urls: tuple[str, ...]
    methodology_url: str
    licence_name: str
    licence_url: str
    licence_evidence: str
    redistribution: str
    attribution: str
    dataset_version: str
    source_version: str
    update_frequency: str
    parser_version: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ProbeSource:
        return cls(
            source_candidate_id=str(value["source_candidate_id"]),
            publisher=str(value["publisher"]),
            dataset=str(value["dataset"]),
            canonical_page_url=str(value["canonical_page_url"]),
            access_urls=tuple(str(item) for item in value["access_urls"]),
            methodology_url=str(value["methodology_url"]),
            licence_name=str(value["licence_name"]),
            licence_url=str(value["licence_url"]),
            licence_evidence=str(value["licence_evidence"]),
            redistribution=str(value["redistribution"]),
            attribution=str(value["attribution"]),
            dataset_version=str(value["dataset_version"]),
            source_version=str(value["source_version"]),
            update_frequency=str(value["update_frequency"]),
            parser_version=str(value["parser_version"]),
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["access_urls"] = list(self.access_urls)
        return value


@dataclass(frozen=True)
class ProbeDefinition:
    schema_version: str
    criterion_id: str
    name: str
    adapter_id: str
    adapter_options: dict[str, Any]
    source: ProbeSource
    observation_type: str
    geographic_scope: str
    freshness_min_year: int
    minimum_coverage_count: int
    component_rules: tuple[ComponentRule, ...]
    blocker_codes: tuple[str, ...] = field(default_factory=tuple)
    rejection_reason_codes: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ProbeDefinition:
        if value.get("schema_version") != "feasibility-probe-definition-1.0":
            raise ValueError("Unsupported feasibility probe definition schema.")
        return cls(
            schema_version=str(value["schema_version"]),
            criterion_id=str(value["criterion_id"]),
            name=str(value["name"]),
            adapter_id=str(value["adapter_id"]),
            adapter_options=dict(value.get("adapter_options", {})),
            source=ProbeSource.from_dict(value["source"]),
            observation_type=str(value["observation_type"]),
            geographic_scope=str(value["geographic_scope"]),
            freshness_min_year=int(value["freshness_min_year"]),
            minimum_coverage_count=int(value.get("minimum_coverage_count", 82)),
            component_rules=tuple(
                ComponentRule.from_dict(item) for item in value["component_rules"]
            ),
            blocker_codes=tuple(str(item) for item in value.get("blocker_codes", [])),
            rejection_reason_codes=tuple(
                str(item) for item in value.get("rejection_reason_codes", [])
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "criterion_id": self.criterion_id,
            "name": self.name,
            "adapter_id": self.adapter_id,
            "adapter_options": self.adapter_options,
            "source": self.source.to_dict(),
            "observation_type": self.observation_type,
            "geographic_scope": self.geographic_scope,
            "freshness_min_year": self.freshness_min_year,
            "minimum_coverage_count": self.minimum_coverage_count,
            "component_rules": [item.to_dict() for item in self.component_rules],
            "blocker_codes": list(self.blocker_codes),
            "rejection_reason_codes": list(self.rejection_reason_codes),
        }


@dataclass(frozen=True)
class ArtifactInput:
    artifact_id: str
    requested_url: str
    body: bytes


@dataclass(frozen=True)
class ParsedProbeRecord:
    source_country_id: str | None
    source_country_name: str | None
    values: dict[str, float]
    reference_start: str | None
    reference_end: str | None
    artifact_ids: tuple[str, ...]
    record_locators: tuple[str, ...]
    parse_succeeded: bool = True
    parse_reason_codes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AdapterResult:
    records: tuple[ParsedProbeRecord, ...]


@dataclass(frozen=True)
class CountryProbeResult:
    criterion_id: str
    source_candidate_id: str
    country_code: str
    display_name: str
    source_country_id: str | None
    source_country_name: str | None
    mapped_by: str | None
    status: str
    presence_state: str
    freshness_state: str
    parse_state: str
    validation_state: str
    values: dict[str, float]
    reference_start: str | None
    reference_end: str | None
    artifact_ids: tuple[str, ...]
    record_locators: tuple[str, ...]
    blocker_codes: tuple[str, ...]
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("artifact_ids", "record_locators", "blocker_codes", "reason_codes"):
            value[key] = list(value[key])
        return value
