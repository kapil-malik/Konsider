"""Isolated parsers for the five initial source families."""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Iterable

from openpyxl import load_workbook

from konsider.ingestion.countries import COUNTRIES, COUNTRY_ALIASES
from konsider.ingestion.models import MetricObservation, RawArtifact


def _observation_id(source: str, country: str, metric: str, year: int) -> str:
    raw = f"{source}|{country}|{metric}|{year}".encode()
    return "obs_" + hashlib.sha256(raw).hexdigest()[:20]


def _annual_observation(
    *, artifact_ids: tuple[str, ...], source_id: str, country: str, metric: str,
    value: float, unit: str, year: int, observation_type: str, method: str,
    flags: tuple[str, ...] = (), lower: float | None = None, upper: float | None = None,
) -> MetricObservation:
    return MetricObservation(
        observation_id=_observation_id(source_id, country, metric, year), country_code=country,
        metric_id=metric, value=float(value), unit=unit,
        reference_start=f"{year}-01-01", reference_end=f"{year}-12-31",
        source_id=source_id, raw_artifact_ids=artifact_ids,
        observation_type=observation_type, geographic_scope="national",
        method_version=method, quality_flags=flags, lower_bound=lower, upper_bound=upper,
    )


def _json(body: bytes) -> object:
    return json.loads(body.decode("utf-8-sig"))


def _latest_by_country(rows: Iterable[dict[str, object]], code_key: str, year_key: str) -> dict[str, dict[str, object]]:
    latest: dict[str, dict[str, object]] = {}
    for row in rows:
        code = str(row.get(code_key, ""))
        if code not in COUNTRIES or row.get(year_key) is None:
            continue
        if code not in latest or int(row[year_key]) > int(latest[code][year_key]):
            latest[code] = row
    return latest


def parse_who_air_quality(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    rows = [row for body in bodies for row in _json(body)["value"]]  # type: ignore[index]
    all_area_codes = {"RESIDENCEAREATYPE_ALL", "RESIDENCEAREATYPE_TOTL", "RESIDENCEAREATYPE_BTSX"}
    eligible = [
        row for row in rows
        if row.get("SpatialDimType") == "COUNTRY" and str(row.get("Dim1", "")).upper() in all_area_codes
    ]
    latest = _latest_by_country(eligible, "SpatialDim", "TimeDim")
    artifact_ids = tuple(item.artifact_id for item in artifacts)
    return [_annual_observation(
        artifact_ids=artifact_ids, source_id="who_air_quality", country=code,
        metric="ambient_pm25_population_weighted", value=row["NumericValue"],
        unit="micrograms_per_cubic_metre", year=int(row["TimeDim"]),
        observation_type="modelled", method="who_air_quality_v1",
        flags=("modelled_estimate",), lower=row.get("Low"), upper=row.get("High"),
    ) for code, row in sorted(latest.items()) if row.get("NumericValue") is not None]


def parse_who_uhc(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    rows = [row for body in bodies for row in _json(body)["value"]]  # type: ignore[index]
    latest = _latest_by_country(rows, "SpatialDim", "TimeDim")
    artifact_ids = tuple(item.artifact_id for item in artifacts)
    return [_annual_observation(
        artifact_ids=artifact_ids, source_id="who_uhc", country=code,
        metric="uhc_service_coverage_index", value=row["NumericValue"], unit="index_0_100",
        year=int(row["TimeDim"]), observation_type="estimated", method="who_uhc_v1",
        flags=("population_level_not_expat_access",),
    ) for code, row in sorted(latest.items()) if row.get("NumericValue") is not None]


def _world_bank_rows(body: bytes) -> list[dict[str, object]]:
    payload = _json(body)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("Unexpected World Bank API response")
    return payload[1]


def parse_world_bank_homicide(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    rows = [row for row in _world_bank_rows(bodies[0]) if row.get("value") is not None]
    normalized = [{**row, "iso3": row.get("countryiso3code"), "year": int(str(row["date"]))} for row in rows]
    latest = _latest_by_country(normalized, "iso3", "year")
    artifact_ids = tuple(item.artifact_id for item in artifacts)
    return [_annual_observation(
        artifact_ids=artifact_ids, source_id="unodc_homicide", country=code,
        metric="intentional_homicide_rate", value=row["value"], unit="per_100000_people",
        year=int(row["year"]), observation_type="reported_or_estimated",
        method="world_bank_homicide_v1", flags=("secondary_distribution",),
    ) for code, row in sorted(latest.items())]


def parse_world_bank_icp(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    ppp = {row["countryiso3code"]: row for row in _world_bank_rows(bodies[0]) if row.get("value") is not None}
    exchange = {row["countryiso3code"]: row for row in _world_bank_rows(bodies[1]) if row.get("value") is not None}
    artifact_ids = tuple(item.artifact_id for item in artifacts)
    output = []
    for code in sorted(set(ppp) & set(exchange) & set(COUNTRIES)):
        value = float(ppp[code]["value"]) / float(exchange[code]["value"]) * 100
        output.append(_annual_observation(
            artifact_ids=artifact_ids, source_id="world_bank_icp", country=code,
            metric="household_consumption_price_level_us_100", value=value,
            unit="index_us_100", year=2021, observation_type="derived",
            method="world_bank_icp_v1", flags=("derived_from_official_ppp_and_exchange_rate", "national_not_city_level"),
        ))
    return output


def parse_wps_index(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    workbook = load_workbook(io.BytesIO(bodies[0]), read_only=True, data_only=True)
    artifact_ids = tuple(item.artifact_id for item in artifacts)
    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        for header_index, row in enumerate(rows[:30]):
            labels = [str(value).strip().lower() if value is not None else "" for value in row]
            previous_labels = [
                str(value).strip().lower() if value is not None else ""
                for value in rows[header_index - 1]
            ] if header_index else []
            country_columns = [i for i, label in enumerate(labels) if label in {"country", "economy", "country name", "code"}]
            score_columns = [i for i, label in enumerate(labels) if "index score" in label or label in {"wps index", "score"}]
            score_columns.extend(
                i for i, label in enumerate(previous_labels)
                if "women, peace, and security index" in label and str(row[i]).strip() == "2025"
            )
            if not country_columns or not score_columns:
                continue
            result = []
            for values in rows[header_index + 1:]:
                country_value = str(values[country_columns[0]]).strip() if values[country_columns[0]] is not None else ""
                code = country_value if country_value in COUNTRIES else COUNTRY_ALIASES.get(country_value)
                score = values[score_columns[0]]
                if code and isinstance(score, (int, float)):
                    result.append(_annual_observation(
                        artifact_ids=artifact_ids, source_id="wps_index", country=code,
                        metric="women_peace_security_index", value=float(score), unit="index_0_1",
                        year=2025, observation_type="composite", method="wps_index_v1",
                        flags=("mixed_reference_years", "independent_composite"),
                    ))
            if result:
                return sorted(result, key=lambda item: item.country_code)
    raise ValueError("Could not locate country and WPS index score columns")


PARSERS = {
    "who_air_quality": parse_who_air_quality,
    "who_uhc": parse_who_uhc,
    "world_bank_homicide": parse_world_bank_homicide,
    "world_bank_icp": parse_world_bank_icp,
    "wps_index": parse_wps_index,
}
