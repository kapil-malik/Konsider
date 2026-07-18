"""Audited source catalog for the five-criterion stabilization release."""

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.models import SourceRegistration

_WB_CODES = ";".join(COUNTRY_CODES)


def _gho_first_page(indicator: str) -> tuple[str, ...]:
    # The worker increments $skip and terminates at the first empty `value` page.
    return (f"https://ghoapi.azureedge.net/api/{indicator}?%24top=1000&%24skip=0",)


SOURCES = {
    "who_air_quality": SourceRegistration(
        source_id="who_air_quality", criterion_id="ambient_pm25_population_weighted",
        publisher="World Health Organization", distributor=None,
        canonical_page_url="https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database",
        download_urls=_gho_first_page("SDGPM25"), access_method="GHO OData API",
        pagination="odata_skip_until_empty", dataset_version="GHO update 2026-05-08",
        source_version="SDGPM25@2026-05-08", reference_period="annual; latest available by country",
        update_frequency="irregular",
        methodology_url="https://www.who.int/data/gho/data/themes/air-pollution/who-modelled-estimates-of-air-pollution-from-particulate-matter",
        license_name="WHO material; dataset-specific licence not displayed by GHO API",
        license_url="https://www.who.int/about/policies/publishing/copyright",
        redistribution="raw API responses kept local; redistribution not treated as permitted",
        permitted_usage="WHO states CC BY-NC-SA 3.0 IGO applies only where a work is issued under it; commercial use or database-product licensing otherwise requires permission.",
        attribution="World Health Organization, Global Health Observatory, indicator SDGPM25; include retrieval date and adaptation disclaimer.",
        license_evidence="WHO copyright page, checked 2026-07-18; the indicator response contains no dataset-specific licence notice.",
        parser="who_air_quality", parser_version="who_air_quality_v2",
        official_or_independent="official",
        notes="Country-comparable modelled population exposure; ground-monitor V8 is not used for ranking.",
    ),
    "unodc_homicide": SourceRegistration(
        source_id="unodc_homicide", criterion_id="intentional_homicide_rate",
        publisher="United Nations Office on Drugs and Crime",
        distributor="World Bank World Development Indicators",
        canonical_page_url="https://dataunodc.un.org/dp-intentional-homicide-victims",
        download_urls=(f"https://api.worldbank.org/v2/country/{_WB_CODES}/indicator/VC.IHR.PSRC.P5?format=json&date=2000:2026&per_page=20000",),
        access_method="World Bank Indicators API secondary distribution", pagination="none",
        dataset_version="WDI current retrieval; UNODC lineage", source_version="VC.IHR.PSRC.P5@WDI",
        reference_period="annual; latest available by country", update_frequency="annual/irregular",
        methodology_url="https://data.unodc.org/sites/dataportal.unodc.org/files/2025-11/metadata_intentional_homicide.pdf",
        license_name="Creative Commons Attribution 4.0 International (WDI distribution)",
        license_url="https://datacatalog.worldbank.org/public-licenses#cc-by",
        redistribution="World Bank WDI API representation may be copied, modified, and distributed with attribution; direct UNODC portal files are not redistributed.",
        permitted_usage="CC BY 4.0 permits commercial and non-commercial copying, adaptation, and distribution with attribution and change indication, subject to World Bank additional terms.",
        attribution="World Bank, World Development Indicators, indicator VC.IHR.PSRC.P5; original source UNODC Research Data Portal; licence CC BY 4.0.",
        license_evidence="WDI indicator metadata explicitly labels VC.IHR.PSRC.P5 CC BY-4.0; checked 2026-07-18.",
        parser="world_bank_homicide", parser_version="world_bank_homicide_v2",
        official_or_independent="official_secondary_distribution",
        notes="The generic UN website terms do not grant redistribution; the release relies on the explicit WDI indicator licence.",
    ),
    "who_uhc": SourceRegistration(
        source_id="who_uhc", criterion_id="uhc_service_coverage_index",
        publisher="World Health Organization", distributor=None,
        canonical_page_url="https://data.who.int/indicators/i/9A706FD",
        download_urls=_gho_first_page("UHC_INDEX_REPORTED"), access_method="GHO OData API",
        pagination="odata_skip_until_empty", dataset_version="GHO update 2025-12-05",
        source_version="UHC_INDEX_REPORTED@2025-12-05",
        reference_period="annual; latest available by country", update_frequency="irregular",
        methodology_url="https://www.who.int/data/gho/data/themes/topics/service-coverage",
        license_name="WHO material; dataset-specific licence not displayed by GHO API",
        license_url="https://www.who.int/about/policies/publishing/copyright",
        redistribution="raw API responses kept local; redistribution not treated as permitted",
        permitted_usage="WHO states CC BY-NC-SA 3.0 IGO applies only where a work is issued under it; commercial use or database-product licensing otherwise requires permission.",
        attribution="World Health Organization, Global Health Observatory, UHC_INDEX_REPORTED; include retrieval date and adaptation disclaimer.",
        license_evidence="WHO copyright page, checked 2026-07-18; the indicator response contains no dataset-specific licence notice.",
        parser="who_uhc", parser_version="who_uhc_v2", official_or_independent="official",
        notes="Population-level essential-service coverage, not immigrant eligibility or care experience.",
    ),
    "world_bank_icp": SourceRegistration(
        source_id="world_bank_icp", criterion_id="household_consumption_price_level_us_100",
        publisher="World Bank International Comparison Program", distributor="World Development Indicators",
        canonical_page_url="https://www.worldbank.org/en/programs/icp/data",
        download_urls=(
            "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.PRVT.PP?format=json&date=2021&per_page=30000",
            "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF?format=json&date=2021&per_page=30000",
        ), access_method="World Bank Indicators API", pagination="none",
        dataset_version="ICP 2021 benchmark", source_version="PA.NUS.PRVT.PP+PA.NUS.FCRF@2021",
        reference_period="2021", update_frequency="benchmark cycle with annual extrapolations",
        methodology_url="https://www.worldbank.org/en/programs/icp/methodology",
        license_name="Creative Commons Attribution 4.0 International",
        license_url="https://datacatalog.worldbank.org/public-licenses#cc-by",
        redistribution="API inputs and derived observations may be redistributed with attribution and change indication.",
        permitted_usage="CC BY 4.0 permits commercial and non-commercial copying, adaptation, and distribution with attribution, subject to World Bank additional terms.",
        attribution="World Bank, International Comparison Program / World Development Indicators, PA.NUS.PRVT.PP and PA.NUS.FCRF; licence CC BY 4.0; PLI derived by Konsider.",
        license_evidence="WDI metadata for both indicators explicitly labels CC BY-4.0; checked 2026-07-18.",
        parser="world_bank_icp", parser_version="world_bank_icp_v2", official_or_independent="official",
        notes="PLI = household PPP / official exchange rate * 100. ICP cautions against precise strict rankings.",
    ),
    "wps_index": SourceRegistration(
        source_id="wps_index", criterion_id="women_peace_security_index",
        publisher="Georgetown Institute for Women, Peace and Security and PRIO", distributor=None,
        canonical_page_url="https://giwps.georgetown.edu/the-index/",
        download_urls=("https://giwps.georgetown.edu/wp-content/uploads/2025/10/WPS-Index-2025-Data.xlsx",),
        access_method="XLSX download", pagination="none", dataset_version="2025/26",
        source_version="WPS-Index-2025-Data", reference_period="mixed underlying years, principally 2018-2025",
        update_frequency="biennial", methodology_url="https://giwps.georgetown.edu/wps-index-methodology/",
        license_name="CC BY-NC 4.0 stated in 2025/26 report; workbook scope not explicit",
        license_url="https://giwps.georgetown.edu/wp-content/uploads/2025/10/WPS-Index-2025-Report.pdf",
        redistribution="raw workbook kept local; normalized values treated as non-commercial research output pending written confirmation that the report licence covers the workbook.",
        permitted_usage="The report's CC BY-NC 4.0 notice permits sharing and adaptation for non-commercial purposes with attribution; it does not establish commercial rights.",
        attribution="Georgetown Institute for Women, Peace and Security and Peace Research Institute Oslo. Women, Peace and Security Index 2025/26. CC BY-NC 4.0.",
        license_evidence="Copyright page of official 2025/26 report; workbook carries no separate machine-readable or visible licence notice found; checked 2026-07-18.",
        parser="wps_index", parser_version="wps_index_v2", official_or_independent="independent_academic",
        notes="Composite with mixed underlying years and imputations; commercial product readiness is blocked pending clarification.",
    ),
}
