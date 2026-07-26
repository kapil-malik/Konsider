"""Build small schema-faithful Phase 5D fixtures and nothing else."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
OUTPUT = ROOT / "tests" / "fixtures" / "phase5d"
MISSING_C11 = {"ATG", "GRD", "UKR"}


def world_bank_fixture(countries: list[dict[str, str]]) -> bytes:
    rows = []
    for index, country in enumerate(countries):
        rows.append(
            {
                "indicator": {
                    "id": "SM.POP.TOTL.ZS",
                    "value": "International migrant stock (% of population)",
                },
                "country": {"id": country["code"], "value": country["display_name"]},
                "countryiso3code": country["code"],
                "date": "2024",
                "value": round(1.5 + (index % 35) * 0.7, 3),
                "unit": "",
                "obs_status": "",
                "decimal": 1,
            }
        )
    payload = [
        {
            "page": 1,
            "pages": 1,
            "per_page": 20000,
            "total": len(rows),
            "sourceid": "2",
            "lastupdated": "2026-07-13",
        },
        rows,
    ]
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def ilostat_fixture(
    countries: list[dict[str, str]], indicator: str, component_offset: float
) -> bytes:
    stream = io.StringIO(newline="")
    fields = [
        "ref_area",
        "ref_area.label",
        "source",
        "indicator",
        "sex",
        "classif1",
        "time",
        "obs_value",
        "obs_status",
    ]
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for index, country in enumerate(countries):
        if country["code"] in MISSING_C11:
            continue
        value = round(component_offset + (index % 20) * 0.45, 3)
        writer.writerow(
            {
                "ref_area": country["code"],
                "ref_area.label": country["display_name"],
                "source": "XA:PHASE5D_FIXTURE",
                "indicator": indicator,
                "sex": "SEX_T",
                "classif1": "AGE_YTHADULT_YGE15",
                "time": "2025",
                "obs_value": value,
                "obs_status": "",
            }
        )
    return stream.getvalue().encode()


def main() -> None:
    universe = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    countries = universe["countries"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "c30-world-bank.json").write_bytes(world_bank_fixture(countries))
    components = (
        ("c11-unemployment.csv", "UNE_2EAP_SEX_AGE_RT", 3.0),
        ("c11-employment.csv", "EMP_2WAP_SEX_AGE_RT", 48.0),
        ("c11-participation.csv", "EAP_2WAP_SEX_AGE_RT", 55.0),
    )
    for filename, indicator, offset in components:
        (OUTPUT / filename).write_bytes(ilostat_fixture(countries, indicator, offset))
    print(f"Wrote Phase 5D fixtures to {OUTPUT}")


if __name__ == "__main__":
    main()
