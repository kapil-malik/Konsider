"""Source-neutral ingestion contracts derived from real source experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRegistration:
    source_id: str
    publisher: str
    distributor: str | None
    canonical_page_url: str
    download_urls: tuple[str, ...]
    access_method: str
    dataset_version: str
    reference_period: str
    update_frequency: str
    methodology_url: str
    terms_url: str
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
    observation_type: str
    geographic_scope: str
    method_version: str
    quality_flags: tuple[str, ...] = field(default_factory=tuple)
    lower_bound: float | None = None
    upper_bound: float | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["raw_artifact_ids"] = list(self.raw_artifact_ids)
        value["quality_flags"] = list(self.quality_flags)
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
    country_code: str | None = None
    metric_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    observation_count: int
    score_count: int
    criterion_coverage: dict[str, int]
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "observation_count": self.observation_count,
            "score_count": self.score_count,
            "criterion_coverage": dict(sorted(self.criterion_coverage.items())),
            "issues": [issue.to_dict() for issue in self.issues],
        }
