"""Audited source catalog for the six-criterion World Bank candidate release."""

from datetime import UTC, datetime

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.models import SourceRegistration

_WB_CODES = ";".join(COUNTRY_CODES)
_WB_API = "https://api.worldbank.org/v2"
_WB_LICENSE = "https://datacatalog.worldbank.org/public-licenses#cc-by"
_WB_USAGE = (
    "CC BY 4.0 permits commercial and non-commercial copying, adaptation, and distribution with "
    "attribution and change indication, subject to the World Bank dataset terms."
)


def world_bank_query_range(start_year: int, as_of_year: int | None = None) -> str:
    """Return a discovery range that advances with the refresh year."""

    end_year = as_of_year if as_of_year is not None else datetime.now(UTC).year
    if end_year < start_year:
        raise ValueError("World Bank query end year cannot precede its start year.")
    return f"{start_year}:{end_year}"


def _wdi(indicator: str, dates: str | None = None, source: int | None = None) -> str:
    dates = dates or world_bank_query_range(2000)
    suffix = f"&source={source}" if source is not None else ""
    return (
        f"{_WB_API}/country/{_WB_CODES}/indicator/{indicator}"
        f"?format=json&date={dates}&per_page=5000{suffix}"
    )


SOURCES = {
    "world_bank_pm25": SourceRegistration(
        source_id="world_bank_pm25",
        criterion_id="ambient_pm25_population_weighted",
        publisher="World Bank World Development Indicators",
        distributor="World Bank Indicators API",
        canonical_page_url="https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3",
        download_urls=(_wdi("EN.ATM.PM25.MC.M3", world_bank_query_range(2018)),),
        access_method="World Bank Indicators API v2, WDI source 2",
        pagination="none",
        dataset_version="WDI update 2026-07-13",
        source_version="EN.ATM.PM25.MC.M3@WDI-2026-07-13",
        reference_period="annual, 1990-2023; latest 2023",
        update_frequency="annual/irregular",
        methodology_url="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.ATM.PM25.MC.M3",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="WDI API representation and normalized observations may be redistributed with attribution and change indication.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank, World Development Indicators, EN.ATM.PM25.MC.M3; source GBD 2023/IHME; licence CC BY 4.0; transformed by Konsider.",
        license_evidence="WDI indicator metadata explicitly labels CC BY-4.0; checked 2026-07-20.",
        parser="world_bank_pm25",
        parser_version="world_bank_pm25_v1",
        official_or_independent="official_secondary_distribution",
        notes="Population-weighted modelled exposure for comparative health risk, not local monitoring or regulatory compliance.",
    ),
    "world_bank_uhc": SourceRegistration(
        source_id="world_bank_uhc",
        criterion_id="uhc_service_coverage_index",
        publisher="World Bank Health Nutrition and Population Statistics",
        distributor="World Bank Indicators API",
        canonical_page_url="https://data.worldbank.org/indicator/SH.UHC.SRVS.CV.XD",
        download_urls=(_wdi("SH.UHC.SRVS.CV.XD", world_bank_query_range(2018), source=16),),
        access_method="World Bank Indicators API v2, HNP source 16",
        pagination="none",
        dataset_version="HNP update 2026-07-01",
        source_version="SH.UHC.SRVS.CV.XD@HNP-2026-07-01",
        reference_period="annual, latest API value 2021",
        update_frequency="irregular",
        methodology_url="https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SH.UHC.SRVS.CV.XD",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="World Bank API representation and normalized observations may be redistributed with attribution and change indication.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank HNP, SH.UHC.SRVS.CV.XD; source WHO Global Health Observatory; licence CC BY 4.0; transformed by Konsider.",
        license_evidence="World Bank HNP metadata explicitly labels CC BY-4.0; checked 2026-07-20.",
        parser="world_bank_uhc",
        parser_version="world_bank_uhc_v1",
        official_or_independent="official_secondary_distribution",
        notes="Complete supported-universe coverage, but 2021 is beyond the freshness threshold and remains non-ready unless refreshed upstream.",
    ),
    "unodc_homicide": SourceRegistration(
        source_id="unodc_homicide",
        criterion_id="intentional_homicide_rate",
        publisher="United Nations Office on Drugs and Crime",
        distributor="World Bank World Development Indicators",
        canonical_page_url="https://data.worldbank.org/indicator/VC.IHR.PSRC.P5",
        download_urls=(_wdi("VC.IHR.PSRC.P5", world_bank_query_range(2000)),),
        access_method="World Bank Indicators API v2, WDI source 2",
        pagination="none",
        dataset_version="WDI update 2026-07-13",
        source_version="VC.IHR.PSRC.P5@WDI-2026-07-13",
        reference_period="annual; latest country values 2021-2023",
        update_frequency="annual/irregular",
        methodology_url="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/VC.IHR.PSRC.P5",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="The explicitly licensed WDI representation may be redistributed; direct UNODC portal files are not used.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank WDI, VC.IHR.PSRC.P5; original source UNODC Research Data Portal; licence CC BY 4.0; transformed by Konsider.",
        license_evidence="WDI indicator metadata explicitly labels CC BY-4.0; checked 2026-07-20.",
        parser="world_bank_homicide_current",
        parser_version="world_bank_homicide_v3",
        official_or_independent="official_secondary_distribution",
        notes="Country comparison requires caution because legal classification and reporting capacity vary.",
    ),
    "world_bank_icp": SourceRegistration(
        source_id="world_bank_icp",
        criterion_id="household_consumption_price_level_us_100",
        publisher="World Bank International Comparison Program",
        distributor="World Development Indicators",
        canonical_page_url="https://www.worldbank.org/en/programs/icp/data",
        download_urls=(
            _wdi("PA.NUS.PRVT.PP", world_bank_query_range(2021)),
            _wdi("PA.NUS.FCRF", world_bank_query_range(2021)),
        ),
        access_method="World Bank Indicators API v2, WDI source 2",
        pagination="none",
        dataset_version="2021 ICP benchmark with WDI extrapolations through 2025",
        source_version="PA.NUS.PRVT.PP+PA.NUS.FCRF@WDI-2026-07-13",
        reference_period="latest common country year, currently 2025",
        update_frequency="annual extrapolation; periodic benchmark",
        methodology_url="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.PRVT.PP",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="API inputs and derived broad price-level bands may be redistributed with attribution and change indication.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank ICP/WDI, PA.NUS.PRVT.PP and PA.NUS.FCRF; licence CC BY 4.0; PLI and broad bands derived by Konsider.",
        license_evidence="WDI metadata for both inputs explicitly labels CC BY-4.0; checked 2026-07-20.",
        parser="world_bank_icp_current",
        parser_version="world_bank_icp_v3",
        official_or_independent="official",
        notes="PLI is household PPP / official exchange rate * 100. Publish only broad relative-cost bands, never a precise ordinal cost ranking.",
    ),
    "world_bank_wbl": SourceRegistration(
        source_id="world_bank_wbl",
        criterion_id="women_legal_economic_equality",
        publisher="World Bank Women, Business and the Law",
        distributor=None,
        canonical_page_url="https://wbl.worldbank.org/en/data/download-data",
        download_urls=(
            "https://wbl.worldbank.org/content/dam/sites/wbl/documents/2026/WBL26_FINAL_ALL.xlsx",
        ),
        access_method="official WBL 2026 XLSX download",
        pagination="none",
        dataset_version="Women, Business and the Law 2026",
        source_version="WBL26_FINAL_ALL@2026-02-23",
        reference_period="current as of 2025-10-01; report year 2026",
        update_frequency="annual",
        methodology_url="https://wbl.worldbank.org/en/data/methodology",
        license_name="Creative Commons Attribution 4.0 International",
        license_url="https://datacatalog.worldbank.org/search/dataset/0038489/women-business-and-the-law",
        redistribution="Official WBL 2026 dataset is public and explicitly licensed CC BY 4.0.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank. 2026. Women, Business and the Law [dataset]. DOI 10.57966/gtdw-yp27; licence CC BY 4.0; transformed by Konsider.",
        license_evidence="World Bank Data Catalog and WBL reproducibility package explicitly label WBL 2026 CC BY 4.0; checked 2026-07-20.",
        parser="world_bank_wbl",
        parser_version="world_bank_wbl_v1",
        official_or_independent="official",
        notes="Uses the WBL 2026 Legal Framework economy index. It measures de jure legal equality, not lived outcomes or enforcement.",
    ),
    "world_bank_infrastructure": SourceRegistration(
        source_id="world_bank_infrastructure",
        criterion_id="infrastructure_readiness_composite",
        publisher="World Bank World Development Indicators",
        distributor="World Bank Indicators API; ITU-origin digital components",
        canonical_page_url="https://data.worldbank.org/",
        download_urls=(
            _wdi("IT.NET.USER.ZS", world_bank_query_range(2018)),
            _wdi("IT.NET.BBND.P2", world_bank_query_range(2018)),
            _wdi("LP.LPI.INFR.XQ", world_bank_query_range(2018)),
        ),
        access_method="World Bank Indicators API v2, WDI source 2",
        pagination="none",
        dataset_version="WDI update 2026-07-13",
        source_version="INFRA-3@WDI-2026-07-13",
        reference_period="latest components: Internet 2024-2025, broadband 2023-2024, LPI infrastructure 2022",
        update_frequency="mixed annual and periodic survey",
        methodology_url="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/LP.LPI.INFR.XQ",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="All three WDI representations and the derived composite may be redistributed with attribution and change indication.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank WDI indicators IT.NET.USER.ZS, IT.NET.BBND.P2, LP.LPI.INFR.XQ; cite ITU for digital components; licence CC BY 4.0; composite derived by Konsider.",
        license_evidence="WDI metadata for all three components explicitly labels CC BY-4.0; checked 2026-07-20.",
        parser="world_bank_infrastructure",
        parser_version="world_bank_infrastructure_v1",
        official_or_independent="official_composite_of_official_distributions",
        notes="Equal-weight experiment covering internet use, fixed broadband penetration, and trade/transport infrastructure quality; not a complete infrastructure measure.",
    ),
}
