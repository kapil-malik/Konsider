"""Versioned, source-neutral ingestion and release contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRegistration:
    source_id: str
    criterion_id: str
    publisher: str
    distributor: str | None
    canonical_page_url: str
    download_urls: tuple[str, ...]
    access_method: str
    pagination: str
    dataset_version: str
    source_version: str
    reference_period: str
    update_frequency: str
    methodology_url: str
    license_name: str
    license_url: str
    redistribution: str
    permitted_usage: str
    attribution: str
    license_evidence: str
    parser: str
    parser_version: str
    official_or_independent: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["download_urls"] = list(self.download_urls)
        return value


@dataclass(frozen=True)
class RawArtifact:
    artifact_id: str
    source_id: str
    requested_url: str
    final_url: str
    retrieved_at: str
    media_type: str
    byte_length: int
    sha256: str
    dataset_version: str
    parser_version: str
    path: str
    http_status: int = 200
    etag: str | None = None
    last_modified: str | None = None
    content_length_header: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceRecordReference:
    artifact_id: str
    locator: str
    record_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MetricObservation:
    observation_id: str
    country_code: str
    metric_id: str
    value: float
    unit: str
    reference_start: str
    reference_end: str
    source_id: str
    raw_artifact_ids: tuple[str, ...]
    source_records: tuple[SourceRecordReference, ...]
    observation_type: str
    geographic_scope: str
    parser_version: str
    method_version: str
    quality_flags: tuple[str, ...] = field(default_factory=tuple)
    lower_bound: float | None = None
    upper_bound: float | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["raw_artifact_ids"] = list(dict.fromkeys(self.raw_artifact_ids))
        value["source_records"] = [item.to_dict() for item in self.source_records]
        value["quality_flags"] = list(self.quality_flags)
        return value


@dataclass(frozen=True)
class SourceAttempt:
    source_id: str
    criterion_id: str
    country_code: str
    status: str
    attempted_at: str
    parser_version: str
    artifact_ids: tuple[str, ...] = field(default_factory=tuple)
    observation_id: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["artifact_ids"] = list(dict.fromkeys(self.artifact_ids))
        return value


@dataclass(frozen=True)
class MetricScore:
    country_code: str
    criterion_id: str
    score: float
    input_observation_ids: tuple[str, ...]
    method_version: str
    transform: str
    direction: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["input_observation_ids"] = list(self.input_observation_ids)
        return value


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str
    scope: str = "structural"
    country_code: str | None = None
    metric_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    structural_passed: bool
    product_ready: bool
    observation_count: int
    score_count: int
    attempt_count: int
    criterion_coverage: dict[str, int]
    status_counts: dict[str, int]
    issues: tuple[ValidationIssue, ...]

    @property
    def passed(self) -> bool:
        """Backward-compatible publication meaning: structural validity only."""
        return self.structural_passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "validation-2.0",
            "structural_passed": self.structural_passed,
            "product_ready": self.product_ready,
            "passed": self.structural_passed,
            "observation_count": self.observation_count,
            "score_count": self.score_count,
            "attempt_count": self.attempt_count,
            "criterion_coverage": dict(sorted(self.criterion_coverage.items())),
            "status_counts": dict(sorted(self.status_counts.items())),
            "issues": [issue.to_dict() for issue in self.issues],
        }
