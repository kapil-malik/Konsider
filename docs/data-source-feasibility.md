# Data Source Feasibility

Status: first 20-country release published

Last updated: 2026-07-17

This file records the source decisions behind release `2026-07-17.1`. The experiment set is India,
Singapore, Canada, Australia, Germany, Netherlands, Switzerland, United States, United Kingdom,
United Arab Emirates, France, Sweden, Denmark, Norway, Ireland, New Zealand, Japan, South Korea,
Spain, and Portugal.

## Release Result

The first local release contains 100 observations and 100 scores: five criteria across all 20
countries. Validation passed with no issues, and replay reproduced the observations and scores from
the immutable raw artifacts.

| Criterion | Source | Release years | Coverage | Treatment |
| --- | --- | ---: | ---: | --- |
| `ambient_pm25_population_weighted` | WHO GHO `SDGPM25` | 2023 | 20/20 | Modelled national population exposure; lower is better. |
| `intentional_homicide_rate` | UNODC lineage via World Bank WDI `VC.IHR.PSRC.P5` | 2021-2023 | 20/20 | Latest available annual rate; lower is better. |
| `uhc_service_coverage_index` | WHO GHO `UHC_INDEX_REPORTED` | 2023 | 20/20 | Population-level service coverage; higher is better. |
| `household_consumption_price_level_us_100` | World Bank ICP/WDI `PA.NUS.PRVT.PP` and `PA.NUS.FCRF` | 2021 | 20/20 | Derived household price level, US=100; lower is better. |
| `women_peace_security_index` | GIWPS/PRIO WPS Index 2025 data workbook | 2025 | 20/20 | Independent composite index; higher is better. |

## Source Decisions

### WHO Air Quality

Use the WHO Global Health Observatory `SDGPM25` API for country-level modelled PM2.5 exposure. The
WHO ambient air quality ground-monitor database was verified as a current official source, but WHO's
own notes warn that monitor density and methods differ enough that direct country comparisons are not
appropriate. For ranking, the criterion is therefore narrowed to modelled national population exposure.

Official references: [WHO air quality database](https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database),
[WHO GHO OData API](https://www.who.int/data/gho/info/gho-odata-api).

### UNODC Crime

Use intentional homicide per 100,000 people. UNODC remains the source lineage and methodology
authority, while the worker currently downloads the WDI-distributed indicator because the official
UNODC data portal did not expose a stable unattended download during verification. The observation
flags retain `secondary_distribution`.

Official references: [UNODC intentional homicide metadata PDF](https://data.unodc.org/sites/dataportal.unodc.org/files/2025-11/metadata_intentional_homicide.pdf),
[World Bank WDI API](https://api.worldbank.org/v2/).

### WHO Healthcare

Use WHO's UHC Service Coverage Index. This is a defensible public-health access proxy, but it is not
an expatriate insurance, eligibility, waiting-time, or private-care quality metric. Those narrower
questions are deferred unless credible comparable sources are found.

Official references: [WHO service coverage topic](https://www.who.int/data/gho/data/themes/topics/service-coverage),
[WHO GHO OData API](https://www.who.int/data/gho/info/gho-odata-api).

### World Bank ICP Price Level

Use the 2021 ICP benchmark inputs distributed through WDI. The release derives household-consumption
price level as household/NPISH PPP divided by official exchange rate times 100, with the United States
anchored at 100. This is a national relative price level, not a city budget or household-specific cost
model.

Official references: [World Bank ICP data](https://www.worldbank.org/en/programs/icp/data),
[World Bank ICP methodology](https://www.worldbank.org/en/programs/icp/methodology),
[WDI April 2026 release note](https://datatopics.worldbank.org/world-development-indicators/release-note/apr-2026.html).

### WPS Index

Use the latest GIWPS/PRIO WPS Index data workbook for the overall 2025 score. It is an independent
academic composite with mixed underlying reference years and imputation caveats, so the release flags
it as `independent_composite`.

Official references: [WPS Index](https://giwps.georgetown.edu/the-index/),
[WPS methodology](https://giwps.georgetown.edu/wps-index-methodology/).

### Infrastructure

Infrastructure remains in feasibility status. A composite should not be published until component
coverage, units, correlation, weighting, and sensitivity tests are documented. Candidate components
include electricity access, internet use, water/sanitation, transport, and digital public-service
availability.

## Usage and Redistribution Notes

The release stores raw source bytes locally for audit and replay. Before packaging or redistributing
raw third-party files outside a local development environment, review each source's current terms:
WHO publishing/copyright, United Nations terms of use, World Bank legal terms, and Georgetown/GIWPS
site terms.
