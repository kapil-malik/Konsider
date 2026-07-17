"""Audited source catalog for the first worker release."""

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.models import SourceRegistration

_WB_CODES = ";".join(COUNTRY_CODES)


def _gho_pages(indicator: str, pages: int) -> tuple[str, ...]:
    return tuple(
        f"https://ghoapi.azureedge.net/api/{indicator}?%24top=1000&%24skip={index * 1000}"
        for index in range(pages)
    )


SOURCES = {
    "who_air_quality": SourceRegistration(
        source_id="who_air_quality", publisher="World Health Organization", distributor=None,
        canonical_page_url="https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database",
        download_urls=_gho_pages("SDGPM25", 25),
        access_method="documented_gho_odata_api", dataset_version="GHO update 2026-05-08",
        reference_period="annual; latest available by country", update_frequency="irregular",
        methodology_url="https://www.who.int/data/gho/data/themes/air-pollution/who-modelled-estimates-of-air-pollution-from-particulate-matter",
        terms_url="https://www.who.int/about/policies/publishing/copyright",
        parser="who_air_quality", parser_version="who_air_quality_v1",
        official_or_independent="official",
        notes="Country-comparable modelled population exposure; ground-monitor V8 is not used for ranking.",
    ),
    "unodc_homicide": SourceRegistration(
        source_id="unodc_homicide", publisher="United Nations Office on Drugs and Crime",
        distributor="World Bank World Development Indicators",
        canonical_page_url="https://dataunodc.un.org/dp-intentional-homicide-victims",
        download_urls=(f"https://api.worldbank.org/v2/country/{_WB_CODES}/indicator/VC.IHR.PSRC.P5?format=json&date=2000:2026&per_page=20000",),
        access_method="documented_world_bank_api_secondary_distribution",
        dataset_version="UNODC metadata update 2025-05-15; WDI current retrieval",
        reference_period="annual; latest available by country", update_frequency="annual/irregular",
        methodology_url="https://data.unodc.org/sites/dataportal.unodc.org/files/2025-11/metadata_intentional_homicide.pdf",
        terms_url="https://www.un.org/en/about-us/terms-of-use",
        parser="world_bank_homicide", parser_version="world_bank_homicide_v1",
        official_or_independent="official_secondary_distribution",
        notes="Direct UNODC portal is client-dependent; lineage and distributor are both retained.",
    ),
    "who_uhc": SourceRegistration(
        source_id="who_uhc", publisher="World Health Organization", distributor=None,
        canonical_page_url="https://data.who.int/indicators/i/9A706FD",
        download_urls=_gho_pages("UHC_INDEX_REPORTED", 8),
        access_method="documented_gho_odata_api", dataset_version="GHO update 2025-12-05",
        reference_period="annual; latest available by country", update_frequency="irregular",
        methodology_url="https://www.who.int/data/gho/data/themes/topics/service-coverage",
        terms_url="https://www.who.int/about/policies/publishing/copyright",
        parser="who_uhc", parser_version="who_uhc_v1", official_or_independent="official",
        notes="Population-level essential-service coverage, not immigrant eligibility or care experience.",
    ),
    "world_bank_icp": SourceRegistration(
        source_id="world_bank_icp", publisher="World Bank International Comparison Program",
        distributor="World Development Indicators",
        canonical_page_url="https://www.worldbank.org/en/programs/icp/data",
        download_urls=(
            "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.PRVT.PP?format=json&date=2021&per_page=30000",
            "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF?format=json&date=2021&per_page=30000",
        ),
        access_method="documented_world_bank_api", dataset_version="ICP 2021 benchmark",
        reference_period="2021", update_frequency="benchmark cycle with annual extrapolations",
        methodology_url="https://www.worldbank.org/en/programs/icp/methodology",
        terms_url="https://www.worldbank.org/en/about/legal/terms-and-conditions",
        parser="world_bank_icp", parser_version="world_bank_icp_v1", official_or_independent="official",
        notes="Derives household price level as household PPP / official exchange rate * 100; US=100.",
    ),
    "wps_index": SourceRegistration(
        source_id="wps_index", publisher="Georgetown Institute for Women, Peace and Security and PRIO",
        distributor=None, canonical_page_url="https://giwps.georgetown.edu/the-index/",
        download_urls=("https://giwps.georgetown.edu/wp-content/uploads/2025/10/WPS-Index-2025-Data.xlsx",),
        access_method="xlsx_download", dataset_version="2025/26",
        reference_period="mixed underlying years, principally 2018-2025", update_frequency="biennial",
        methodology_url="https://giwps.georgetown.edu/wps-index-methodology/",
        terms_url="https://www.georgetown.edu/privacy-policy/",
        parser="wps_index", parser_version="wps_index_v1", official_or_independent="independent_academic",
        notes="Composite inclusion, justice, and security index; underlying years and imputations vary.",
    ),
}
