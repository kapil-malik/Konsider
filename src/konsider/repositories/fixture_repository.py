"""Load and validate the local Phase 1 fixture release."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from konsider.domain.models import (
    Country,
    CountryMetric,
    EvidenceDocument,
    ParameterDefinition,
    ProjectData,
)

DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"


class DataValidationError(ValueError):
    """Raised when the local MVP data files are incomplete or inconsistent."""


class FixtureProjectDataRepository:
    """Read one complete local fixture release from disk."""

    def __init__(self, data_dir: Path | str = DEFAULT_FIXTURE_DIR) -> None:
        self.data_dir = Path(data_dir)

    def load(self) -> ProjectData:
        """Load and validate the complete fixture release."""

        return load_project_data(self.data_dir)


def load_project_data(data_dir: Path | str = DEFAULT_FIXTURE_DIR) -> ProjectData:
    """Load all structured and qualitative data from a fixture release."""

    data_path = Path(data_dir)
    countries = load_countries(data_path / "countries.yml")
    parameters = load_parameter_definitions(data_path / "parameter_definitions.yml")
    metrics = load_country_metrics(data_path / "country_metrics.csv", countries, parameters)
    evidence = load_evidence_documents(data_path / "evidence", countries)

    return ProjectData(
        countries=countries,
        parameters=parameters,
        metrics=metrics,
        evidence=evidence,
    )


def load_countries(path: Path | str) -> dict[str, Country]:
    rows = _load_json_compatible_yaml(Path(path))
    if not isinstance(rows, list):
        raise DataValidationError("countries.yml must contain a list of countries.")

    countries: dict[str, Country] = {}
    for row in rows:
        _require_keys(row, {"id", "name", "region"}, "country")
        country = Country(id=row["id"], name=row["name"], region=row["region"])
        if country.id in countries:
            raise DataValidationError(f"Duplicate country id: {country.id}")
        countries[country.id] = country
    return countries


def load_parameter_definitions(path: Path | str) -> dict[str, ParameterDefinition]:
    rows = _load_json_compatible_yaml(Path(path))
    if not isinstance(rows, list):
        raise DataValidationError("parameter_definitions.yml must contain a list of parameters.")

    parameters: dict[str, ParameterDefinition] = {}
    for row in rows:
        _require_keys(
            row,
            {"id", "name", "category", "description", "higher_is_better"},
            "parameter definition",
        )
        parameter = ParameterDefinition(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            description=row["description"],
            higher_is_better=bool(row["higher_is_better"]),
        )
        if parameter.id in parameters:
            raise DataValidationError(f"Duplicate parameter id: {parameter.id}")
        parameters[parameter.id] = parameter
    return parameters


def load_country_metrics(
    path: Path | str,
    countries: dict[str, Country],
    parameters: dict[str, ParameterDefinition],
) -> list[CountryMetric]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {"country_id", "parameter_id", "score", "source", "last_updated", "notes"}
        if set(reader.fieldnames or []) != expected_fields:
            raise DataValidationError(
                f"country_metrics.csv must have columns: {sorted(expected_fields)}"
            )

        metrics = []
        seen_pairs: set[tuple[str, str]] = set()
        for row in reader:
            country_id = row["country_id"]
            parameter_id = row["parameter_id"]
            if country_id not in countries:
                raise DataValidationError(f"Metric references unknown country: {country_id}")
            if parameter_id not in parameters:
                raise DataValidationError(f"Metric references unknown parameter: {parameter_id}")

            pair = (country_id, parameter_id)
            if pair in seen_pairs:
                raise DataValidationError(
                    f"Duplicate metric for country/parameter pair: {country_id}/{parameter_id}"
                )
            seen_pairs.add(pair)

            try:
                score = float(row["score"])
            except ValueError as exc:
                raise DataValidationError(
                    f"Metric score must be numeric for {country_id}/{parameter_id}."
                ) from exc
            if not 1 <= score <= 10:
                raise DataValidationError(
                    f"Metric score must be between 1 and 10 for {country_id}/{parameter_id}."
                )

            metrics.append(
                CountryMetric(
                    country_id=country_id,
                    parameter_id=parameter_id,
                    score=score,
                    source=row["source"],
                    last_updated=row["last_updated"],
                    notes=row["notes"],
                )
            )

    expected_pairs = {
        (country_id, parameter_id) for country_id in countries for parameter_id in parameters
    }
    missing_pairs = expected_pairs - seen_pairs
    if missing_pairs:
        formatted = ", ".join(
            f"{country}/{parameter}" for country, parameter in sorted(missing_pairs)
        )
        raise DataValidationError(f"Missing metrics for: {formatted}")

    return metrics


def load_evidence_documents(
    evidence_dir: Path | str,
    countries: dict[str, Country],
) -> dict[str, EvidenceDocument]:
    directory = Path(evidence_dir)
    evidence: dict[str, EvidenceDocument] = {}

    for country_id in countries:
        path = directory / f"{country_id}.md"
        if not path.exists():
            raise DataValidationError(f"Missing evidence document for country: {country_id}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise DataValidationError(f"Evidence document is empty: {path}")
        evidence[country_id] = EvidenceDocument(
            country_id=country_id,
            text=text,
            source_path=str(path),
        )

    return evidence


def _load_json_compatible_yaml(path: Path) -> Any:
    """Load .yml files that are intentionally kept JSON-compatible for Sprint 1."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataValidationError(
            f"{path.name} must be valid JSON-compatible YAML in Sprint 1."
        ) from exc


def _require_keys(row: object, keys: set[str], label: str) -> None:
    if not isinstance(row, dict):
        raise DataValidationError(f"Each {label} entry must be an object.")
    missing = keys - set(row)
    if missing:
        raise DataValidationError(f"{label.title()} entry missing keys: {sorted(missing)}")
