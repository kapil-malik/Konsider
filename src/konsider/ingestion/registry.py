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
_ILO_USAGE = (
    "CC BY 4.0 permits commercial and non-commercial copying, adaptation, and distribution with "
    "attribution and change indication; restricted partner microdata are not used."
)
_WIPO_USAGE = (
    "CC BY 4.0 permits commercial and non-commercial copying, adaptation, and distribution with "
    "attribution and change indication. Konsider uses only WIPO's published sub-index score, not "
    "third-party indicator content."
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
    "world_bank_wgi_political_stability": SourceRegistration(
        source_id="world_bank_wgi_political_stability",
        criterion_id="political_stability",
        publisher="World Bank Worldwide Governance Indicators",
        distributor="World Bank Indicators API",
        canonical_page_url="https://data.worldbank.org/indicator/GOV_WGI_PV_EST",
        download_urls=(
            "https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset_with_sourcedata-2025.xlsx",
        ),
        access_method="Official WGI 2025 all-dimensions XLSX",
        pagination="none",
        dataset_version="Worldwide Governance Indicators 2025 revision",
        source_version="wgidataset_with_sourcedata-2025.xlsx#pv@2024",
        reference_period="2024 estimate with published standard error",
        update_frequency="annual",
        methodology_url="https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation",
        license_name="Creative Commons Attribution 4.0 International",
        license_url="https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators",
        redistribution="Published WGI aggregate estimates may be redistributed with attribution.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank, Worldwide Governance Indicators, 2025 revision; transformed into broad Konsider bands.",
        license_evidence="The WGI catalogue record identifies CC BY 4.0 for published aggregate data; checked 2026-07-26.",
        parser="world_bank_wgi_political_stability",
        parser_version="world_bank_wgi_xlsx_v1",
        official_or_independent="official",
        notes="Perception-based aggregate; uncertainty is retained and precise country ranks are not claimed.",
    ),
    "world_bank_wgi_rule_of_law": SourceRegistration(
        source_id="world_bank_wgi_rule_of_law",
        criterion_id="rule_of_law",
        publisher="World Bank Worldwide Governance Indicators",
        distributor="World Bank Indicators API",
        canonical_page_url="https://data.worldbank.org/indicator/GOV_WGI_RL_EST",
        download_urls=(
            "https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset_with_sourcedata-2025.xlsx",
        ),
        access_method="Official WGI 2025 all-dimensions XLSX",
        pagination="none",
        dataset_version="Worldwide Governance Indicators 2025 revision",
        source_version="wgidataset_with_sourcedata-2025.xlsx#rl@2024",
        reference_period="2024 estimate with published standard error",
        update_frequency="annual",
        methodology_url="https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation",
        license_name="Creative Commons Attribution 4.0 International",
        license_url="https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators",
        redistribution="Published WGI aggregate estimates may be redistributed with attribution.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank, Worldwide Governance Indicators, 2025 revision; transformed into broad Konsider bands.",
        license_evidence="The WGI catalogue record identifies CC BY 4.0 for published aggregate data; checked 2026-07-26.",
        parser="world_bank_wgi_rule_of_law",
        parser_version="world_bank_wgi_xlsx_v1",
        official_or_independent="official",
        notes="Perception-based aggregate; uncertainty is retained and redundancy is reviewed against political stability.",
    ),
    "world_bank_migrant_stock": SourceRegistration(
        source_id="world_bank_migrant_stock",
        criterion_id="established_immigrant_presence",
        publisher="World Bank World Development Indicators",
        distributor="United Nations Population Division upstream",
        canonical_page_url="https://data.worldbank.org/indicator/SM.POP.TOTL.ZS",
        download_urls=(_wdi("SM.POP.TOTL.ZS", "2024:2024"),),
        access_method="World Bank Indicators API v2",
        pagination="none",
        dataset_version="World Development Indicators, July 2026",
        source_version="SM.POP.TOTL.ZS@WDI-2026-07",
        reference_period="2024",
        update_frequency="annual",
        methodology_url="https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SM.POP.TOTL",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=_WB_LICENSE,
        redistribution="WDI API representation and normalized observations may be redistributed with attribution and change indication.",
        permitted_usage=_WB_USAGE,
        attribution="World Bank WDI; International Migrant Stock, United Nations Population Division; transformed by Konsider.",
        license_evidence="WDI metadata identifies CC BY 4.0; checked 2026-07-26.",
        parser="world_bank_migrant_stock",
        parser_version="world_bank_migrant_stock_v1",
        official_or_independent="official_secondary_distribution",
        notes="Measures established immigrant presence only; not acceptance, integration quality, or visa accessibility.",
    ),
    "ilostat_job_market_opportunity": SourceRegistration(
        source_id="ilostat_job_market_opportunity",
        criterion_id="overall_job_market_opportunity",
        publisher="International Labour Organization (ILOSTAT)",
        distributor="ILOSTAT bulk download service",
        canonical_page_url="https://ilostat.ilo.org/data/bulk/",
        download_urls=(
            "https://rplumber.ilo.org/data/indicator/?id=UNE_2EAP_SEX_AGE_RT_A&format=csv",
            "https://rplumber.ilo.org/data/indicator/?id=EMP_2WAP_SEX_AGE_RT_A&format=csv",
            "https://rplumber.ilo.org/data/indicator/?id=EAP_2WAP_SEX_AGE_RT_A&format=csv",
        ),
        access_method="ILOSTAT official annual-indicator CSV bulk downloads",
        pagination="none",
        dataset_version="ILO modelled estimates, November 2025 edition",
        source_version="UNE+EMP+EAP@ILOSTAT-MODEL-2025-11",
        reference_period=(
            "2025 modelled national estimates for total population age 15+; "
            "future projections in the edition are not used"
        ),
        update_frequency="annual model edition",
        methodology_url=(
            "https://ilostat.ilo.org/methods/concepts-and-definitions/" "ilo-modelled-estimates/"
        ),
        license_name="Creative Commons Attribution 4.0 International",
        license_url="https://www.ilo.org/rights-and-permissions",
        redistribution=(
            "Derived observations and scores may be redistributed with attribution; retained "
            "raw bulk files remain local and are not committed."
        ),
        permitted_usage=_ILO_USAGE,
        attribution=(
            "International Labour Organization, ILOSTAT, ILO modelled estimates, November 2025 "
            "edition; 2025 UNE, EMP and EAP total-population age-15+ series; transformed by "
            "Konsider."
        ),
        license_evidence=(
            "ILOSTAT datasets and referential metadata published from 3 May 2023 are CC BY 4.0; "
            "checked and recorded during Phase 3 on 2026-07-26."
        ),
        parser="ilostat_job_market_opportunity",
        parser_version="ilostat_job_market_opportunity_v1",
        official_or_independent="official_modelled_estimates",
        notes=(
            "National, occupation-neutral labour-market conditions. Equal-weight composite of "
            "employment-to-population, labour-force participation and reverse unemployment "
            "average-rank percentiles. Does not measure vacancies, wages, occupation fit, visa "
            "access, or city-level opportunity."
        ),
    ),
    "world_bank_hci_plus_schooling": SourceRegistration(
        source_id="world_bank_hci_plus_schooling",
        criterion_id="school_education_quality",
        publisher="World Bank",
        distributor="World Bank Data Catalog",
        canonical_page_url=(
            "https://datacatalog.worldbank.org/search/dataset/0067030/" "human-capital-index-plus"
        ),
        download_urls=(
            "https://datacatalogfiles.worldbank.org/ddh-published/0067030/DR0095876/"
            "hci_plus_index_panel.dta",
        ),
        access_method="Official HCI+ version 3 Stata panel",
        pagination="none",
        dataset_version="Human Capital Index Plus version 3",
        source_version="HCI+V3-LAYS@2026-02-11",
        reference_period="latest labelled country estimate; production freshness requires 2024+",
        update_frequency="periodic",
        methodology_url="https://humancapital.worldbank.org/hciplus/methodology/",
        license_name="Creative Commons Attribution 4.0 International",
        license_url=(
            "https://datacatalog.worldbank.org/search/dataset/0067030/" "human-capital-index-plus"
        ),
        redistribution=(
            "The official HCI+ dataset and derived observations may be redistributed with "
            "attribution and change indication."
        ),
        permitted_usage=_WB_USAGE,
        attribution=(
            "World Bank, Human Capital Index Plus version 3, learning-adjusted years of "
            "schooling; licence CC BY 4.0; transformed into fixed Konsider bands."
        ),
        license_evidence=(
            "The World Bank Data Catalog explicitly identifies HCI+ as CC BY 4.0; "
            "rechecked 2026-07-28."
        ),
        parser="world_bank_hci_plus_schooling",
        parser_version="world_bank_hci_plus_schooling_v1",
        official_or_independent="official_modelled_and_harmonized",
        notes=(
            "Learning-adjusted years of schooling combines expected schooling quantity with "
            "harmonized learning outcomes. It is a national modelled condition, not a school, "
            "city, curriculum, language-support, or migrant-access assessment."
        ),
    ),
    "wipo_innovation_outputs": SourceRegistration(
        source_id="wipo_innovation_outputs",
        criterion_id="research_innovation_ecosystem",
        publisher="World Intellectual Property Organization",
        distributor=None,
        canonical_page_url="https://www.wipo.int/en/web/global-innovation-index/2025/index",
        download_urls=("https://www.wipo.int/edocs/pubdocs/en/wipo-pub-2000-2025-tech1.xlsx",),
        access_method="Official Global Innovation Index 2025 data workbook",
        pagination="none",
        dataset_version="Global Innovation Index 2025",
        source_version="GII2025-INNOVATION-OUTPUTS",
        reference_period="GII 2025 edition using latest available inputs in its multi-year window",
        update_frequency="annual",
        methodology_url=(
            "https://www.wipo.int/web-publications/global-innovation-index-2025/en/"
            "appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html"
        ),
        license_name="Creative Commons Attribution 4.0 International",
        license_url=(
            "https://www.wipo.int/web-publications/global-innovation-index-2025/en/"
            "copyright.html"
        ),
        redistribution=(
            "Konsider redistributes WIPO's published Innovation outputs sub-index score only, "
            "with attribution and change indication; third-party input columns are not published."
        ),
        permitted_usage=_WIPO_USAGE,
        attribution=(
            "World Intellectual Property Organization, Global Innovation Index 2025, "
            "Innovation outputs sub-index; licence CC BY 4.0; transformed into fixed Konsider "
            "bands."
        ),
        license_evidence=(
            "WIPO licenses the GII 2025 publication for commercial reproduction and adaptation "
            "under CC BY 4.0; exact workbook and third-party boundary rechecked 2026-07-28."
        ),
        parser="wipo_innovation_outputs",
        parser_version="wipo_innovation_outputs_v1",
        official_or_independent="official_composite",
        notes=(
            "Uses only WIPO's published Innovation outputs sub-index, not the overall GII or its "
            "governance, infrastructure, education, and market input pillars. National results "
            "can obscure city-level research clusters."
        ),
    ),
}
