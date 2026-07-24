"""Stable supported country universe generated from the final Phase 2D audit."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
COUNTRY_UNIVERSE_PATH = PROJECT_ROOT / "data" / "country-universes" / "stable-supported-v1.json"
COUNTRY_UNIVERSE = json.loads(COUNTRY_UNIVERSE_PATH.read_text(encoding="utf-8"))
COUNTRY_RECORDS = tuple(COUNTRY_UNIVERSE["countries"])
COUNTRIES = {item["code"]: item["display_name"] for item in COUNTRY_RECORDS}
COUNTRY_REGIONS = {item["code"]: item["region"] for item in COUNTRY_RECORDS}

COUNTRY_ALIASES = {
    "Bahamas": "BHS",
    "Czech Republic": "CZE",
    "Korea, Rep.": "KOR",
    "South Korea": "KOR",
    "Republic of Korea": "KOR",
    "Russia": "RUS",
    "Russian Federation": "RUS",
    "Slovak Republic": "SVK",
    "Türkiye": "TUR",
    "Turkiye": "TUR",
    "United States of America": "USA",
    "United Kingdom": "GBR",
    "United Arab Emirates": "ARE",
    "Netherlands": "NLD",
}
COUNTRY_ALIASES.update({name: code for code, name in COUNTRIES.items()})

COUNTRY_CODES = tuple(COUNTRIES)
