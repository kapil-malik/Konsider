"""Core data models for Konsider Phase 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Country:
    id: str
    name: str
    region: str


@dataclass(frozen=True)
class ParameterDefinition:
    id: str
    name: str
    category: str
    description: str
    higher_is_better: bool


@dataclass(frozen=True)
class CountryMetric:
    country_id: str
    parameter_id: str
    score: float
    source: str
    last_updated: str
    notes: str


@dataclass(frozen=True)
class EvidenceDocument:
    country_id: str
    text: str
    source_path: str


@dataclass(frozen=True)
class ProjectData:
    countries: dict[str, Country]
    parameters: dict[str, ParameterDefinition]
    metrics: list[CountryMetric]
    evidence: dict[str, EvidenceDocument]


@dataclass(frozen=True)
class ScoreContribution:
    parameter_id: str
    raw_score: float
    weight: float
    contribution: float


@dataclass(frozen=True)
class CountryRanking:
    country_id: str
    total_score: float
    contributions: list[ScoreContribution]
