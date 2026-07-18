# Data-source feasibility and licence audit

Status: stabilization audit; not legal advice

Last checked: 2026-07-18

This audit covers the five 20-country experimental criteria. A public download is not itself a
licence. Privacy policies and generic site terms are not recorded as dataset licences. Raw source
bytes live under ignored `data/raw/`; release manifests retain URLs, retrieval metadata, and SHA-256
checksums. The earlier committed raw files are removed from the current Git index without rewriting
history.

| Criterion / source | Exact licence evidence | Permitted use and required attribution | Konsider decision |
| --- | --- | --- | --- |
| WHO modelled PM2.5 (`SDGPM25`) | [WHO Copyright, Licensing and Permissions](https://www.who.int/about/policies/publishing/copyright) says CC BY-NC-SA 3.0 IGO applies to materials *issued under that licence*. It permits non-commercial copying, distribution, translation, and adaptation with WHO attribution and share-alike; commercial use and licensing technical information in database products require permission. The GHO API response and indicator page do not display a dataset-specific licence. | Do not use the WHO logo or imply endorsement. Cite WHO/GHO, the indicator, retrieval date, and identify adaptations. Commercial/database-product use is not cleared from the evidence found. | Raw responses remain local. Experimental normalized observations may be used only in a non-commercial research context pending written confirmation. Product readiness is blocked. |
| WHO UHC Service Coverage (`UHC_INDEX_REPORTED`) | Same WHO copyright page and same absence of a licence notice in the GHO response. | Same conditional CC BY-NC-SA terms and attribution requirements as above. | Raw responses remain local. Commercial/database-product use is not cleared. Product readiness is blocked. |
| UNODC homicide via World Bank WDI (`VC.IHR.PSRC.P5`) | [WDI indicator metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/VC.IHR.PSRC.P5) explicitly labels the distributed indicator `CC BY-4.0`. [World Bank Data Access and Licensing](https://datacatalog.worldbank.org/public-licenses) says CC BY 4.0 permits copying, modification, and distribution for any purpose with attribution and change indication, subject to its additional terms. Generic UN terms allow only personal non-commercial copying and prohibit redistribution/derivative compilations, so Konsider does not rely on those terms or redistribute direct UNODC downloads. | Attribute World Bank WDI indicator `VC.IHR.PSRC.P5`, identify UNODC as original source, link the licence, and state Konsider transformations. | Use only the explicitly CC BY-4.0 WDI representation. Raw WDI API bytes are still kept local under the repository-wide conservative raw-artifact policy. |
| World Bank ICP / WDI (`PA.NUS.PRVT.PP`, `PA.NUS.FCRF`) | WDI metadata for [private-consumption PPP](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.PRVT.PP) and [official exchange rate](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/PA.NUS.FCRF) explicitly labels both `CC BY-4.0`. | Commercial and non-commercial copy, adaptation, and redistribution are allowed with attribution and change indication, subject to World Bank additional terms. Attribute ICP/WDI and label the Konsider PLI calculation. | Licence is adequate for redistribution. Methodology remains a blocker for strict rankings: ICP metadata says PPPs are not recommended as a precise measure for establishing strict country rankings. |
| GIWPS/PRIO WPS Index 2025/26 | The copyright page of the [official 2025/26 report](https://giwps.georgetown.edu/wp-content/uploads/2025/10/WPS-Index-2025-Report.pdf) states `Creative Commons Attribution Non-Commercial 4.0`. The downloadable workbook contains no separate licence notice found in this audit. A Georgetown privacy policy is not a data licence. | The report licence permits sharing and adaptation only for non-commercial purposes with attribution and change indication. It does not grant commercial rights. It is unclear whether the workbook is within the licensed work. | Keep the workbook local. Treat normalized values as non-commercial research output only; obtain written confirmation of workbook scope and commercial plans before product use. Product readiness is blocked. |

Source quality remains separate from licence status. WHO PM2.5 is a modelled population-weighted
national estimate with uncertainty bounds. WHO UHC measures population service coverage, not migrant
eligibility or care experience. UNODC/WDI homicide has legal-system and reporting comparability
limits. ICP is a national price-level comparison, not a household budget or city cost index. WPS is
an independent composite using mixed reference years and possible imputation.

The worker source registry stores the licence name, URL, evidence statement, redistribution decision,
permitted use, and attribution text. Any change in those fields requires a new source version and a
fresh audit date.
