"""Small source-specific parsers used by Phase 5 feasibility probes."""

from __future__ import annotations

import csv
import io
import json
import math
from collections import defaultdict
from collections.abc import Iterable
from typing import Protocol

from konsider.research.probe_models import (
    AdapterResult,
    ArtifactInput,
    ParsedProbeRecord,
)


class ProbeAdapter(Protocol):
    def parse(
        self, artifacts: tuple[ArtifactInput, ...], options: dict[str, object]
    ) -> AdapterResult: ...


def _finite_float(value: object) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Value is not finite.")
    return number


class WorldBankIndicatorJsonAdapter:
    """Parse the World Bank API's [metadata, observations] JSON response."""

    def parse(
        self, artifacts: tuple[ArtifactInput, ...], options: dict[str, object]
    ) -> AdapterResult:
        if len(artifacts) != 1:
            raise ValueError("World Bank JSON adapter requires exactly one artifact.")
        component_id = str(options["component_id"])
        payload = json.loads(artifacts[0].body.decode("utf-8-sig"))
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            raise ValueError("Unexpected World Bank indicator response.")
        latest: dict[str, tuple[int, ParsedProbeRecord]] = {}
        for index, row in enumerate(payload[1]):
            if not isinstance(row, dict) or row.get("value") is None:
                continue
            source_code = str(row.get("countryiso3code") or "").strip()
            source_name = (
                str(row.get("country", {}).get("value"))
                if isinstance(row.get("country"), dict)
                else None
            )
            try:
                year = int(row["date"])
                number = _finite_float(row["value"])
                record = ParsedProbeRecord(
                    source_country_id=source_code or None,
                    source_country_name=source_name,
                    values={component_id: number},
                    reference_start=str(year),
                    reference_end=str(year),
                    artifact_ids=(artifacts[0].artifact_id,),
                    record_locators=(f"response[1][{index}]",),
                )
            except (KeyError, TypeError, ValueError):
                year = int(row.get("date") or 0)
                record = ParsedProbeRecord(
                    source_country_id=source_code or None,
                    source_country_name=source_name,
                    values={},
                    reference_start=str(year) if year else None,
                    reference_end=str(year) if year else None,
                    artifact_ids=(artifacts[0].artifact_id,),
                    record_locators=(f"response[1][{index}]",),
                    parse_succeeded=False,
                    parse_reason_codes=("PRS_VALUE_INVALID",),
                )
            if source_code and (source_code not in latest or year > latest[source_code][0]):
                latest[source_code] = (year, record)
        return AdapterResult(
            tuple(
                item[1]
                for item in sorted(latest.values(), key=lambda x: x[1].source_country_id or "")
            )
        )


def _world_bank_rows(
    artifact: ArtifactInput,
) -> Iterable[tuple[int, dict[str, object]]]:
    payload = json.loads(artifact.body.decode("utf-8-sig"))
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("Unexpected World Bank indicator response.")
    for index, row in enumerate(payload[1]):
        if isinstance(row, dict):
            yield index, row


class WorldBankMultiIndicatorJsonAdapter:
    """Combine several WDI time-series responses into one country record."""

    def parse(
        self, artifacts: tuple[ArtifactInput, ...], options: dict[str, object]
    ) -> AdapterResult:
        indicator_components = {
            str(key): str(value)
            for key, value in dict(options["indicator_components"]).items()
        }
        minimum_observations = {
            str(key): int(value)
            for key, value in dict(options.get("minimum_observations", {})).items()
        }
        observations: dict[
            str, dict[str, list[tuple[int, float, str, str]]]
        ] = defaultdict(lambda: defaultdict(list))
        names: dict[str, str] = {}
        parse_failures: dict[str, tuple[str, str, int, str]] = {}
        for artifact in artifacts:
            for index, row in _world_bank_rows(artifact):
                indicator = row.get("indicator")
                indicator_id = (
                    str(indicator.get("id") or "") if isinstance(indicator, dict) else ""
                )
                component = indicator_components.get(indicator_id)
                if component is None:
                    continue
                code = str(row.get("countryiso3code") or "").strip()
                if not code or row.get("value") is None:
                    continue
                country = row.get("country")
                if isinstance(country, dict) and country.get("value"):
                    names[code] = str(country["value"])
                locator = f"{artifact.requested_url}#response[1][{index}]"
                try:
                    year = int(row["date"])
                    number = _finite_float(row["value"])
                except (KeyError, TypeError, ValueError):
                    parse_failures[code] = (
                        artifact.artifact_id,
                        locator,
                        int(row.get("date") or 0),
                        component,
                    )
                    continue
                observations[code][component].append(
                    (year, number, artifact.artifact_id, locator)
                )

        records = []
        for code in sorted(set(observations) | set(parse_failures)):
            components = observations.get(code, {})
            values: dict[str, float] = {}
            selected: list[tuple[int, float, str, str]] = []
            component_latest_years: list[int] = []
            for component in sorted(set(indicator_components.values())):
                rows = sorted(components.get(component, ()), reverse=True)
                required = minimum_observations.get(component, 1)
                if len(rows) < required:
                    continue
                latest = rows[0]
                values[component] = latest[1]
                values[f"{component}_observation_count"] = float(len(rows))
                component_latest_years.append(latest[0])
                selected.extend(rows)
            if not selected and code in parse_failures:
                artifact_id, locator, year, _ = parse_failures[code]
                records.append(
                    ParsedProbeRecord(
                        source_country_id=code,
                        source_country_name=names.get(code),
                        values={},
                        reference_start=str(year) if year else None,
                        reference_end=str(year) if year else None,
                        artifact_ids=(artifact_id,),
                        record_locators=(locator,),
                        parse_succeeded=False,
                        parse_reason_codes=("PRS_VALUE_INVALID",),
                    )
                )
                continue
            all_years = [item[0] for item in selected]
            records.append(
                ParsedProbeRecord(
                    source_country_id=code,
                    source_country_name=names.get(code),
                    values=values,
                    reference_start=str(min(all_years)) if all_years else None,
                    # A composite is only as fresh as its oldest latest component.
                    reference_end=(
                        str(min(component_latest_years)) if component_latest_years else None
                    ),
                    artifact_ids=tuple(dict.fromkeys(item[2] for item in selected)),
                    record_locators=tuple(item[3] for item in selected),
                )
            )
        return AdapterResult(tuple(records))


class IlostatLabourCompositeCsvAdapter:
    """Combine exact ILOSTAT annual modelled labour-market CSV tables."""

    def parse(
        self, artifacts: tuple[ArtifactInput, ...], options: dict[str, object]
    ) -> AdapterResult:
        indicator_components = {
            str(key): str(value) for key, value in dict(options["indicator_components"]).items()
        }
        sex_code = str(options.get("sex_code", "SEX_T"))
        age_code = str(options.get("age_code", "AGE_YTHADULT_YGE15"))
        by_country: dict[str, dict[str, tuple[int, float, str, str]]] = defaultdict(dict)
        names: dict[str, str] = {}
        parse_failures: dict[str, tuple[str, str, int]] = {}
        for artifact in artifacts:
            rows = csv.DictReader(io.StringIO(artifact.body.decode("utf-8-sig")))
            for line_number, row in enumerate(rows, start=2):
                if row.get("sex") != sex_code or row.get("classif1") != age_code:
                    continue
                indicator = str(row.get("indicator") or "")
                component = indicator_components.get(indicator)
                if component is None:
                    continue
                code = str(row.get("ref_area") or "").strip()
                if not code:
                    continue
                names[code] = str(row.get("ref_area.label") or code)
                locator = f"{artifact.requested_url}#row={line_number}"
                try:
                    year = int(row["time"])
                    number = _finite_float(row["obs_value"])
                except (KeyError, TypeError, ValueError):
                    parse_failures[code] = (
                        artifact.artifact_id,
                        locator,
                        int(row.get("time") or 0),
                    )
                    continue
                previous = by_country[code].get(component)
                if previous is None or year > previous[0]:
                    by_country[code][component] = (
                        year,
                        number,
                        artifact.artifact_id,
                        locator,
                    )
        records = []
        for code in sorted(set(by_country) | set(parse_failures)):
            components = by_country.get(code, {})
            if not components and code in parse_failures:
                artifact_id, locator, year = parse_failures[code]
                records.append(
                    ParsedProbeRecord(
                        source_country_id=code,
                        source_country_name=names.get(code),
                        values={},
                        reference_start=str(year) if year else None,
                        reference_end=str(year) if year else None,
                        artifact_ids=(artifact_id,),
                        record_locators=(locator,),
                        parse_succeeded=False,
                        parse_reason_codes=("PRS_VALUE_INVALID",),
                    )
                )
                continue
            years = [item[0] for item in components.values()]
            records.append(
                ParsedProbeRecord(
                    source_country_id=code,
                    source_country_name=names.get(code),
                    values={component: item[1] for component, item in sorted(components.items())},
                    reference_start=str(min(years)),
                    reference_end=str(max(years)),
                    artifact_ids=tuple(
                        dict.fromkeys(item[2] for _, item in sorted(components.items()))
                    ),
                    record_locators=tuple(item[3] for _, item in sorted(components.items())),
                )
            )
        return AdapterResult(tuple(records))


class HciPlusStataAdapter:
    """Read the exact HCI+ panel fields used by the C08 research probe."""

    def parse(
        self, artifacts: tuple[ArtifactInput, ...], options: dict[str, object]
    ) -> AdapterResult:
        if len(artifacts) != 1:
            raise ValueError("HCI+ Stata adapter requires exactly one artifact.")
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - depends on research runtime
            raise RuntimeError(
                "The HCI+ research adapter requires pandas with Stata support."
            ) from exc
        country_code_field = str(options.get("country_code_field", "iso3c"))
        country_name_field = str(options.get("country_name_field", "wbcountryname"))
        year_field = str(options.get("year_field", "year"))
        field_components = {
            str(key): str(value)
            for key, value in dict(options["field_components"]).items()
        }
        frame = pd.read_stata(io.BytesIO(artifacts[0].body))
        required_fields = {
            country_code_field,
            country_name_field,
            year_field,
            *field_components,
        }
        missing_fields = required_fields - set(frame.columns)
        if missing_fields:
            raise ValueError(
                f"HCI+ Stata file is missing fields: {', '.join(sorted(missing_fields))}"
            )
        latest: dict[str, tuple[int, ParsedProbeRecord]] = {}
        for index, row in frame.iterrows():
            code = str(row[country_code_field]).strip()
            if not code or code.lower() == "nan":
                continue
            try:
                year = int(row[year_field])
            except (TypeError, ValueError):
                continue
            values = {}
            for field, component in field_components.items():
                value = row[field]
                if pd.isna(value):
                    continue
                try:
                    values[component] = _finite_float(value)
                except (TypeError, ValueError):
                    continue
            if not values:
                continue
            record = ParsedProbeRecord(
                source_country_id=code,
                source_country_name=str(row[country_name_field]),
                values=values,
                reference_start=str(year),
                reference_end=str(year),
                artifact_ids=(artifacts[0].artifact_id,),
                record_locators=(f"row={int(index) + 2}",),
            )
            if code not in latest or year > latest[code][0]:
                latest[code] = (year, record)
        return AdapterResult(
            tuple(latest[code][1] for code in sorted(latest))
        )


ADAPTERS: dict[str, ProbeAdapter] = {
    "world_bank_indicator_json_v1": WorldBankIndicatorJsonAdapter(),
    "world_bank_multi_indicator_json_v1": WorldBankMultiIndicatorJsonAdapter(),
    "ilostat_labour_composite_csv_v1": IlostatLabourCompositeCsvAdapter(),
    "hci_plus_stata_v1": HciPlusStataAdapter(),
}
