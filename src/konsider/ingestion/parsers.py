"""Isolated parsers with record-level provenance for the five source families."""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Iterable

from openpyxl import load_workbook

from konsider.ingestion.countries import COUNTRIES, COUNTRY_ALIASES
from konsider.ingestion.models import MetricObservation, RawArtifact, SourceRecordReference


def _observation_id(source: str, country: str, metric: str, year: int) -> str:
    return "obs_" + hashlib.sha256(f"{source}|{country}|{metric}|{year}".encode()).hexdigest()[:20]


def _annual_observation(
    *, records: tuple[SourceRecordReference, ...], source_id: str, country: str, metric: str,
    value: float, unit: str, year: int, observation_type: str, parser_version: str,
    method: str, flags: tuple[str, ...] = (), lower: float | None = None,
    upper: float | None = None,
) -> MetricObservation:
    artifact_ids = tuple(dict.fromkeys(record.artifact_id for record in records))
    return MetricObservation(
        observation_id=_observation_id(source_id, country, metric, year), country_code=country,
        metric_id=metric, value=float(value), unit=unit,
        reference_start=f"{year}-01-01", reference_end=f"{year}-12-31", source_id=source_id,
        raw_artifact_ids=artifact_ids, source_records=records, observation_type=observation_type,
        geographic_scope="national", parser_version=parser_version, method_version=method,
        quality_flags=flags, lower_bound=lower, upper_bound=upper,
    )


def _json(body: bytes) -> object:
    return json.loads(body.decode("utf-8-sig"))


def _latest_by_country(
    rows: Iterable[tuple[dict[str, object], SourceRecordReference]], code_key: str, year_key: str,
) -> dict[str, tuple[dict[str, object], SourceRecordReference]]:
    latest: dict[str, tuple[dict[str, object], SourceRecordReference]] = {}
    for row, reference in rows:
        code = str(row.get(code_key, ""))
        if code not in COUNTRIES or row.get(year_key) is None:
            continue
        if code not in latest or int(row[year_key]) > int(latest[code][0][year_key]):
            latest[code] = (row, reference)
    return latest


def _who_rows(artifacts: list[RawArtifact], bodies: list[bytes]):
    for artifact, body in zip(artifacts, bodies, strict=True):
        payload = _json(body)
        for index, row in enumerate(payload["value"]):  # type: ignore[index]
            record_id = "|".join(str(row.get(key, "")) for key in ("SpatialDim", "TimeDim", "Dim1"))
            yield row, SourceRecordReference(artifact.artifact_id, f"$.value[{index}]", record_id)


def parse_who_air_quality(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    all_area_codes = {"RESIDENCEAREATYPE_ALL", "RESIDENCEAREATYPE_TOTL", "RESIDENCEAREATYPE_BTSX"}
    eligible = [(row, ref) for row, ref in _who_rows(artifacts, bodies)
                if row.get("SpatialDimType") == "COUNTRY" and str(row.get("Dim1", "")).upper() in all_area_codes]
    latest = _latest_by_country(eligible, "SpatialDim", "TimeDim")
    return [_annual_observation(
        records=(ref,), source_id="who_air_quality", country=code,
        metric="ambient_pm25_population_weighted", value=row["NumericValue"],
        unit="micrograms_per_cubic_metre", year=int(row["TimeDim"]), observation_type="modelled",
        parser_version="who_air_quality_v2", method="who_air_quality_observation_v2",
        flags=("modelled_estimate", "uncertainty_interval_required"), lower=row.get("Low"), upper=row.get("High"),
    ) for code, (row, ref) in sorted(latest.items()) if row.get("NumericValue") is not None]


def parse_who_uhc(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    latest = _latest_by_country(_who_rows(artifacts, bodies), "SpatialDim", "TimeDim")
    return [_annual_observation(
        records=(ref,), source_id="who_uhc", country=code, metric="uhc_service_coverage_index",
        value=row["NumericValue"], unit="index_0_100", year=int(row["TimeDim"]),
        observation_type="estimated", parser_version="who_uhc_v2", method="who_uhc_observation_v2",
        flags=("population_level_not_expat_access",),
    ) for code, (row, ref) in sorted(latest.items()) if row.get("NumericValue") is not None]


def _world_bank_rows(artifact: RawArtifact, body: bytes):
    payload = _json(body)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("Unexpected World Bank API response")
    for index, row in enumerate(payload[1]):
        record_id = f"{row.get('countryiso3code')}|{row.get('indicator', {}).get('id')}|{row.get('date')}"
        yield row, SourceRecordReference(artifact.artifact_id, f"$[1][{index}]", record_id)


def parse_world_bank_homicide(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    rows = []
    for row, ref in _world_bank_rows(artifacts[0], bodies[0]):
        if row.get("value") is not None:
            rows.append(({**row, "iso3": row.get("countryiso3code"), "year": int(str(row["date"]))}, ref))
    latest = _latest_by_country(rows, "iso3", "year")
    return [_annual_observation(
        records=(ref,), source_id="unodc_homicide", country=code,
        metric="intentional_homicide_rate", value=row["value"], unit="per_100000_people",
        year=int(row["year"]), observation_type="reported_or_estimated",
        parser_version="world_bank_homicide_v2", method="world_bank_homicide_observation_v2",
        flags=("secondary_distribution", "cross_country_comparability_caution"),
    ) for code, (row, ref) in sorted(latest.items())]


def parse_world_bank_icp(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    ppp = {row["countryiso3code"]: (row, ref) for row, ref in _world_bank_rows(artifacts[0], bodies[0]) if row.get("value") is not None}
    exchange = {row["countryiso3code"]: (row, ref) for row, ref in _world_bank_rows(artifacts[1], bodies[1]) if row.get("value") is not None}
    output = []
    for code in sorted(set(ppp) & set(exchange) & set(COUNTRIES)):
        ppp_row, ppp_ref = ppp[code]
        exchange_row, exchange_ref = exchange[code]
        value = float(ppp_row["value"]) / float(exchange_row["value"]) * 100
        output.append(_annual_observation(
            records=(ppp_ref, exchange_ref), source_id="world_bank_icp", country=code,
            metric="household_consumption_price_level_us_100", value=value, unit="index_us_100",
            year=2021, observation_type="derived", parser_version="world_bank_icp_v2",
            method="world_bank_icp_pli_v2",
            flags=("derived_from_official_ppp_and_exchange_rate", "national_not_city_level", "not_for_precise_strict_ranking"),
        ))
    return output


def parse_wps_index(artifacts: list[RawArtifact], bodies: list[bytes]) -> list[MetricObservation]:
    workbook = load_workbook(io.BytesIO(bodies[0]), read_only=True, data_only=True)
    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        for header_index, row in enumerate(rows[:30]):
            labels = [str(value).strip().lower() if value is not None else "" for value in row]
            previous = [str(value).strip().lower() if value is not None else "" for value in rows[header_index - 1]] if header_index else []
            country_columns = [i for i, label in enumerate(labels) if label in {"country", "economy", "country name", "code"}]
            score_columns = [i for i, label in enumerate(labels) if "index score" in label or label in {"wps index", "score"}]
            score_columns.extend(i for i, label in enumerate(previous) if "women, peace, and security index" in label and str(row[i]).strip() == "2025")
            if not country_columns or not score_columns:
                continue
            result = []
            for row_index, values in enumerate(rows[header_index + 1:], start=header_index + 2):
                country_value = str(values[country_columns[0]]).strip() if values[country_columns[0]] is not None else ""
                code = country_value if country_value in COUNTRIES else COUNTRY_ALIASES.get(country_value)
                score = values[score_columns[0]]
                if code and isinstance(score, (int, float)):
                    reference = SourceRecordReference(artifacts[0].artifact_id, f"{sheet.title}!R{row_index}C{score_columns[0] + 1}", code)
                    result.append(_annual_observation(
                        records=(reference,), source_id="wps_index", country=code,
                        metric="women_peace_security_index", value=float(score), unit="index_0_1", year=2025,
                        observation_type="composite", parser_version="wps_index_v2", method="wps_index_observation_v2",
                        flags=("mixed_reference_years", "independent_composite", "possible_underlying_imputation"),
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
