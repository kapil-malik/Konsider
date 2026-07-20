# Data-source feasibility and licence audit

Status: audited for candidate release `2026-07-20.2`; not legal advice

Last checked: 2026-07-20

A public endpoint is not a licence. This audit relies on dataset/indicator-specific metadata and the
[World Bank public licence terms](https://datacatalog.worldbank.org/public-licenses), not privacy
policies or generic website terms. All selected distributions state Creative Commons Attribution 4.0
International (CC BY 4.0), which permits copying, adaptation, and distribution for commercial and
non-commercial purposes with attribution and change indication, subject to the World Bank terms.
Konsider nevertheless keeps raw third-party bytes under ignored `data/raw/`; committed releases store
URLs, HTTP metadata, checksums, versions, attribution, and exact record references.

## Audited sources

| Criterion | Official access and methodology | Coverage and freshness observed 2026-07-20 | Licence and required use | Decision |
| --- | --- | --- | --- | --- |
| Population-weighted PM2.5 | WDI API `EN.ATM.PM25.MC.M3`; [indicator metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.ATM.PM25.MC.M3) | 20/20; latest 2023; WDI update shown as 2026-07-13 | Metadata says CC BY 4.0. Attribute World Bank WDI and GBD 2023/IHME, identify Konsider transformation. | Ready. Modelled national exposure for comparative health risk, not a monitoring-station or regulatory measure. |
| UHC service coverage | World Bank Indicators API, HNP source 16, `SH.UHC.SRVS.CV.XD`; [HNP metadata](https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SH.UHC.SRVS.CV.XD) | 20/20; latest 2021; HNP update shown as 2026-07-01. The current WDI source-2 endpoint returned no observations, so the registered official API source is HNP 16. | HNP metadata says CC BY 4.0. Attribute World Bank HNP and WHO GHO, identify transformation. | Not ready: complete but stale under the three-year rule. It measures population service coverage, not migrant eligibility, quality, or care experience. |
| Intentional homicide | WDI API `VC.IHR.PSRC.P5`; [indicator metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/VC.IHR.PSRC.P5) | 20/20; latest country values range 2021-2023; WDI update shown as 2026-07-13 | The WDI representation says CC BY 4.0. Attribute World Bank WDI and original source UNODC. Direct UNODC portal files are not ingested or redistributed. | Ready with legal-definition and reporting-capacity comparability cautions. |
| Household-consumption relative cost | WDI API `PA.NUS.PRVT.PP` and `PA.NUS.FCRF`; [PPP metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.PRVT.PP), [exchange-rate metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.FCRF) | 20/20 latest common year 2025; 2021 ICP benchmark with WDI extrapolations | Both inputs say CC BY 4.0. Attribute World Bank ICP/WDI and identify the derived price-level calculation and banding. | Ready only as broad relative-cost bands. ICP cautions against precise strict country ranking; the value is national, not a city or household budget. |
| Women’s legal and economic equality | Official [WBL 2026 download](https://wbl.worldbank.org/en/data/download-data), workbook `WBL26_FINAL_ALL.xlsx`; [methodology](https://wbl.worldbank.org/en/data/methodology), [catalog record](https://datacatalog.worldbank.org/search/dataset/0038489/women-business-and-the-law) | 20/20; report year 2026, law/data cutoff 2025-10-01; 190-economy dataset | The catalog and [reproducibility package](https://reproducibility.worldbank.org/catalog/459) say CC BY 4.0. Use the World Bank citation/DOI and identify transformations. | Ready. Uses the WBL Legal Framework economy index and therefore measures de jure law, not enforcement or lived outcomes. |
| Infrastructure readiness experiment | WDI APIs `IT.NET.USER.ZS`, `IT.NET.BBND.P2`, `LP.LPI.INFR.XQ`; metadata for [internet use](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IT.NET.USER.ZS), [fixed broadband](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IT.NET.BBND.P2), and [LPI infrastructure](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/LP.LPI.INFR.XQ) | 20/20 for every component; internet 2024-2025, broadband 2023-2024, LPI 2022 | Each WDI representation says CC BY 4.0. Attribute World Bank WDI and ITU for the digital indicators; identify the equal-weight derived composite. | Provisionally ready, still labelled experimental. It covers digital access and trade/transport logistics, not all infrastructure; component years differ and LPI is survey-based. |

## Observed API/download behavior

- WDI/HNP API requests use the fixed ISO-3 country set, an explicit date range, JSON, and a page size
  above the expected result count. The generic connector also follows documented next links or page
  metadata and terminates on an empty page without storing that terminal response.
- The WBL site requires normal browser request headers for its official workbook. The worker captures
  the final URL and HTTP response metadata and selects the latest report row per country rather than
  treating the workbook’s historical rows as duplicates.
- Source registrations freeze the URLs, dataset/source versions, parser versions, methodology links,
  licence evidence, redistribution decision, permitted usage, attribution, and limitations used by a
  release. Replay reads those embedded registrations rather than silently substituting the current
  registry.

## Product-readiness interpretation

Licence adequacy is necessary but not sufficient. Each criterion also has source-specific range,
unit, observation-type, quality-flag, coverage, freshness, attempt, provenance, schema, checksum, and
replay checks. Release `2026-07-20.2` passes five criteria. UHC remains visible with blockers rather
than being redefined, imputed, or replaced by a fixture score.
