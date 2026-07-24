import json
from pathlib import Path

from konsider.ingestion.countries import (
    COUNTRIES,
    COUNTRY_CODES,
    COUNTRY_UNIVERSE,
    COUNTRY_UNIVERSE_PATH,
)
from konsider.ingestion.registry import SOURCES

ROOT = Path(__file__).resolve().parents[3]
EXISTING_COUNTRIES = {
    "ARE",
    "AUS",
    "CAN",
    "CHE",
    "DEU",
    "DNK",
    "ESP",
    "FRA",
    "GBR",
    "IND",
    "IRL",
    "JPN",
    "KOR",
    "NLD",
    "NOR",
    "NZL",
    "PRT",
    "SGP",
    "SWE",
    "USA",
}


def test_final_universe_is_the_validated_91_country_intersection() -> None:
    assert COUNTRY_UNIVERSE_PATH.name == "stable-supported-v1.json"
    assert COUNTRY_UNIVERSE["universe_id"] == "stable_supported_v1"
    assert COUNTRY_UNIVERSE["country_count"] == len(COUNTRIES) == len(COUNTRY_CODES) == 91
    assert len(set(COUNTRY_CODES)) == 91
    assert EXISTING_COUNTRIES <= set(COUNTRY_CODES)
    assert not {"BGD", "BLR", "KWT", "SAU"} & set(COUNTRY_CODES)


def test_consumer_catalog_uses_the_authoritative_country_universe() -> None:
    catalog = json.loads(
        (ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json").read_text(encoding="utf-8")
    )
    assert catalog["countries"] == COUNTRY_UNIVERSE["countries"]


def test_wdi_is_the_only_production_homicide_channel() -> None:
    homicide_sources = [
        source for source in SOURCES.values() if source.criterion_id == "intentional_homicide_rate"
    ]
    assert len(homicide_sources) == 1
    assert homicide_sources[0].source_id == "unodc_homicide"
    assert homicide_sources[0].distributor == "World Bank World Development Indicators"
    assert all(
        url.startswith("https://api.worldbank.org/") for url in homicide_sources[0].download_urls
    )
    assert all(rejected not in SOURCES for rejected in ("direct_unodc", "unsd", "eurostat", "oecd"))
