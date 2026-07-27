# Konsider Phase 3C — Batch 3 source-feasibility research

Evidence cutoff: **2026-07-26**
Universe: **stable_supported_v1 (91 countries)**

## Evidence boundary

Only C53 coverage is **MEASURED** from captured World Bank API responses joined to the stable 91-country universe. Publisher scope, method and identified licence statements are **VERIFIED** where linked. Every other stable-91 conclusion is a preliminary **ESTIMATE**, not an exhaustive audit.

## Executive conclusion

Proceed to a deterministic Phase 3E probe for **C53**. Treat **C71, C76, C54, C67, C62, C68, C06, C75** as conditional experiments, not approved production criteria. Defer **C70, C78, C42, C57** and reject **C45, C69** under the identified sources. This is the final broad Phase 3C batch; next step is consolidated Phase 3E.

## Comparison table

| Rank | ID | Criterion | Finding | Granularity | Stable-91 coverage | A/L/C/M | Phase 3E |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | C53 | Water quality and sanitation | PROBE_APPROVED | NATIONAL_WITH_LOCAL_CAVEAT | 86/91 measured | A4/L4/C4/M4 | PROCEED_DETERMINISTIC_PROBE |
| 2 | C71 | Work-life balance | EXPERIMENTAL_CANDIDATE | NATIONAL | HIGH estimated | A4/L4/C4/M3 | EXPERIMENTAL_ONLY |
| 3 | C76 | Social protection and welfare support | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_PROFILE_CAVEAT | FULL estimated | A4/L4/C3/M3 | EXPERIMENTAL_ONLY |
| 4 | C54 | Food safety and public-health protection | EXPERIMENTAL_CANDIDATE | NATIONAL | FULL estimated | A4/L4/C3/M3 | EXPERIMENTAL_ONLY |
| 5 | C67 | Long-term climate-change exposure | EXPERIMENTAL_CANDIDATE | NATIONAL_DERIVED_FROM_GRID | FULL estimated | A4/L4/C3/M3 | EXPERIMENTAL_ONLY |
| 6 | C62 | Digital-government readiness | EXPERIMENTAL_CANDIDATE | NATIONAL | FULL estimated | A4/L4/C3/M4 | EXPERIMENTAL_ONLY |
| 7 | C68 | Natural-disaster risk | EXPERIMENTAL_CANDIDATE | NATIONAL | FULL estimated | A4/L3/C3/M3 | EXPERIMENTAL_ONLY |
| 8 | C06 | International-student accessibility | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_PROFILE_CAVEAT | HIGH estimated | A4/L3/C3/M3 | EXPERIMENTAL_ONLY |
| 9 | C75 | Religious freedom and freedom of expression | EXPERIMENTAL_CANDIDATE | NATIONAL | FULL estimated | A4/L2/C3/M3 | EXPERIMENTAL_ONLY |
| 10 | C70 | Climate resilience and adaptation readiness | DEFERRED_REDUNDANT | NATIONAL | FULL estimated | A4/L4/C3/M3 | DEFER |
| 11 | C78 | Overall life satisfaction | DEFERRED_LICENCE | NATIONAL_SURVEY | HIGH estimated | A4/L2/C4/M3 | DEFER |
| 12 | C42 | Social inclusion and acceptance of immigrants | DEFERRED_COVERAGE | NATIONAL_SURVEY | MEDIUM estimated | A4/L2/C3/M3 | DEFER |
| 13 | C57 | Water-supply reliability | DEFERRED_CITY_LAYER | CITY_OR_UTILITY | MEDIUM estimated | A4/L3/C3/M3 | DEFER |
| 14 | C45 | LGBTQ+ legal and social inclusion | REJECTED_LICENCE | NATIONAL_LEGAL | FULL estimated | A4/L1/C4/M3 | REJECT |
| 15 | C69 | Environmental quality beyond PM2.5 | REJECTED_LICENCE_REDUNDANCY | NATIONAL_COMPOSITE | FULL estimated | A4/L1/C2/M3 | REJECT |

## Phase 3E shortlist

1. **C53 — Water quality and sanitation** (DETERMINISTIC): Proceed to Phase 3E with the narrow basic-service definition and explicit missing-country outcomes; keep safely managed services as optional metadata.
2. **C71 — Work-life balance** (CONDITIONAL_EXPERIMENTAL): Run an experimental Phase 3E probe only after renaming to Working-time burden.
3. **C76 — Social protection and welfare support** (CONDITIONAL_EXPERIMENTAL): Run a conditional Phase 3E probe as a national welfare-system reach proxy.
4. **C54 — Food safety and public-health protection** (CONDITIONAL_EXPERIMENTAL): Run an experimental Phase 3E probe; label it Food-safety system capacity.
5. **C67 — Long-term climate-change exposure** (CONDITIONAL_EXPERIMENTAL): Run an experimental methodology probe, not a production score probe.
6. **C62 — Digital-government readiness** (CONDITIONAL_EXPERIMENTAL): Experimental only; inspect components in Phase 3E and reject a direct GTMI rank.
7. **C68 — Natural-disaster risk** (CONDITIONAL_EXPERIMENTAL): Conditional Phase 3E probe focused on natural-hazard exposure, subject to exact licence capture.
8. **C06 — International-student accessibility** (CONDITIONAL_EXPERIMENTAL): Experimental only after renaming to International-student presence; otherwise defer.
9. **C75 — Religious freedom and freedom of expression** (CONDITIONAL_EXPERIMENTAL): Conditional experimental probe only after exact licence and variable selection are resolved.

## Recurring publisher and dataset families

- **World Bank open data** — C53, C62, C67. CC BY 4.0 national/global datasets; only C53 has measured stable-91 coverage.
- **WHO/UNICEF monitoring** — C53, C54, C57. Strong harmonised public-service definitions; quality, self-reporting and local granularity differ.
- **ILO modelled and administrative systems** — C71, C76. Broad scope and favourable reuse; exact current bulk files still need probes.
- **Expert-coded/composite indices** — C68, C70, C75. Useful global scope but require overlap, uncertainty and component-selection controls.
- **Survey-based wellbeing and attitudes** — C42, C78. Conceptually relevant but constrained by coverage, mixed field years and/or reuse rights.
- **Non-commercial research products** — C45, C69. Authoritative but unsuitable for unrestricted production reuse under identified licences.

## Criteria requiring city-level treatment

- **C57 (REQUIRED)** — Reliability is utility/network and neighbourhood specific.
- **C53 (SUPPLEMENTAL)** — National basic-service access hides local quality and network gaps.
- **C67 (DESIRABLE)** — Gridded hazards should eventually be population/city weighted.
- **C68 (DESIRABLE)** — National hazard risk hides flood, wildfire, cyclone and seismic zones.
- **C69 (NATURAL_BUT_REJECTED)** — Environmental exposure is local, while the candidate is a licence-blocked national composite.

# C53 — Water quality and sanitation

**Relocation question.** How widely can residents rely on at least basic drinking-water and sanitation services in the destination country?

**Operational definition.** Narrow to the lower of population shares using at least basic drinking-water and at least basic sanitation services. Do not label this tap-water safety or continuity.

**Finding.** PROBE_APPROVED; **recommendation:** PROCEED_DETERMINISTIC_PROBE.

**Natural granularity and observation.** NATIONAL_WITH_LOCAL_CAVEAT; Modelled household-service estimates. Freshness: SLOW_STRUCTURAL.

## Source candidates

- **WHO/UNICEF JMP via World Bank WDI — World Development Indicators.** SH.H2O.BASW.ZS; SH.STA.BASS.ZS. Version: 2025 JMP release; observations through 2024. Grades: A4/L4/C4/M4. [Access](https://api.worldbank.org/v2/country/all/indicator/SH.H2O.BASW.ZS?format=json) · [Methodology](https://washdata.org/report/jmp-2025-wash-households) · [Licence](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets)

## Coverage and freshness

- **MEASURED:** 86/91 measured (94.5%) for both basic components with a 2022-2024 observation.
- **VERIFIED publisher scope:** JMP 2025 reports basic drinking water for 217 countries/areas and basic sanitation for 210.
- The exact WDI/JMP API intersection clears the 82-country threshold. Safely managed water plus sanitation reaches only 66/91.
- Missing/stale ISO3: BHS, BIH, GRD, HRV, NIC.

## Methodology and comparability

- JMP applies harmonised service ladders to household survey, census and administrative inputs.
- Basic service is not equivalent to contaminant-free, continuously available household tap water.

## Licensing and reuse

- World Bank-distributed WDI data are CC BY 4.0; pin exact indicator metadata and attribution.
- WHO/UNICEF source attribution should be retained.

## Country and entity mapping

- Five stable-universe countries lack one or both fresh basic-service components.
- National averages obscure city, neighbourhood and network differences.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S4**.
- Use min(basic water %, basic sanitation %), winsorised only if necessary; expose both components.

## Overlap, limitations, and blockers

- Overlap: C57, C69.
- Weak proxy for water quality in high-income destinations.
- Country estimates may be modelled and lag local infrastructure changes.
- Reason codes: CMP_BASIC_NOT_SAFELY_MANAGED; GRA_LOCAL_VARIATION.

## Recommendation

Proceed to Phase 3E with the narrow basic-service definition and explicit missing-country outcomes; keep safely managed services as optional metadata.

## Evidence ledger

- **MEASURED:** Exact WDI API join returned 86/91 fresh intersections. — konsider_phase3c_batch3/world_bank_coverage_measurements.json
- **MEASURED:** The safely managed pair returned 66/91. — konsider_phase3c_batch3/world_bank_coverage_measurements.json

## Open questions

- Is a high-coverage but low-discrimination basic-service score valuable enough for relocation ranking?

# C71 — Work-life balance

**Relocation question.** How heavy is the average weekly working-time burden for employed people in the destination?

**Operational definition.** Narrow to mean weekly hours actually worked per employed person; it does not measure leave, schedule control, commute or subjective balance.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL; ILO-modelled labour estimate. Freshness: ANNUAL.

## Source candidates

- **International Labour Organization — ILOSTAT working-time indicators.** Average weekly hours actually worked per employed person by sex — ILO modelled estimates, Nov. 2025. Version: November 2025 modelled estimates. Grades: A4/L4/C4/M3. [Access](https://ilostat.ilo.org/topics/working-time/) · [Methodology](https://ilostat.ilo.org/methods/concepts-and-definitions/ilo-modelled-estimates/) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 82/91 appears plausible; exact indicator download not joined.
- **VERIFIED publisher scope:** ILOSTAT publishes global modelled estimates, November 2025 edition.
- Modelled global scope is promising, but exact stable-91 recency and sex/age aggregates remain unmeasured.

## Methodology and comparability

- Actual hours exclude annual leave, public holidays, sickness, parental leave and commuting.
- Modelled estimates improve coverage but depend on harmonisation and imputation.

## Licensing and reuse

- ILO open data published after 3 May 2023 are generally CC BY 4.0; capture the exact bulk-file notice.

## Country and entity mapping

- National ISO mapping should be tractable; aggregation and observation-status fields must be retained.

## Scoring feasibility

- Direction: **LOWER_BETTER**; grade: **S3**.
- Reverse robust percentile of mean weekly hours; label as working-time burden.

## Overlap, limitations, and blockers

- Overlap: C78.
- Cannot substantiate the broad work-life-balance label.
- Informal work and multiple jobs may be measured unevenly.
- Reason codes: DEF_LABEL_TOO_BROAD; COV_EXACT_JOIN_REQUIRED.

## Recommendation

Run an experimental Phase 3E probe only after renaming to Working-time burden.

## Evidence ledger

- **VERIFIED:** ILOSTAT lists a November 2025 modelled average-weekly-hours table. — [source](https://ilostat.ilo.org/topics/working-time/)
- **ESTIMATED:** Stable-91 coverage has not been measured. — Phase 3C Batch 3

## Open questions

- Should paid leave be a separate policy/profile feature rather than folded into this score?

# C76 — Social protection and welfare support

**Relocation question.** What share of residents is effectively covered by at least one social-protection benefit?

**Operational definition.** Narrow to effective social-protection coverage; it does not establish a new immigrant's eligibility, adequacy or waiting period.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_PROFILE_CAVEAT; Administrative reports plus ILO modelled estimates. Freshness: SLOW_STRUCTURAL.

## Source candidates

- **International Labour Organization — World Social Protection Database / WSPR 2024-26 annex.** SDG 1.3.1 effective coverage; modelled series 2009-2023. Version: WSPR 2024-26; data through 2023. Grades: A4/L4/C3/M3. [Access](https://webapps.ilo.org/static/english/reports/flagship/world_social_protection_report_2024-26/Annex.html) · [Methodology](https://www.ilo.org/resource/article/world-social-protection-report-2024-26-figures) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 90% appears highly plausible; exact stable-91 join not performed.
- **VERIFIED publisher scope:** ILO model output supplies complete 2009-2023 series for 189 countries/territories.
- Publisher scope clears the threshold, but reported versus imputed values must be distinguished.

## Methodology and comparability

- The complete series includes reported and imputed observations.
- Coverage says whether a benefit is received, not its value or migrant eligibility.

## Licensing and reuse

- ILO terms are favourable, but the exact downloadable database asset and attribution must be pinned.

## Country and entity mapping

- Country mapping should be broad; preserve imputation flags and benefit-population definitions.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S3**.
- Published effective-coverage percentage; report imputation and do not infer newcomer entitlement.

## Overlap, limitations, and blockers

- Overlap: C72.
- Legal residents, temporary migrants and citizens can face different entitlements.
- High coverage may coexist with low benefit adequacy.
- Reason codes: PRF_ELIGIBILITY_NOT_MEASURED; CMP_MODELLED_VALUES.

## Recommendation

Run a conditional Phase 3E probe as a national welfare-system reach proxy.

## Evidence ledger

- **VERIFIED:** ILO states that model output provides complete 2009-2023 series for 189 countries and territories. — [source](https://webapps.ilo.org/static/english/reports/flagship/world_social_protection_report_2024-26/Annex.html)
- **ESTIMATED:** Stable-91 coverage is publisher-scope based, not measured. — Phase 3C Batch 3

## Open questions

- Should imputed observations receive lower confidence or remain unscored?

# C54 — Food safety and public-health protection

**Relocation question.** How strong is the country's self-reported capacity to prevent, detect and respond to food-safety and wider public-health threats?

**Operational definition.** Use WHO SPAR Food Safety capacity (C13) as a narrow system-capacity proxy, not observed foodborne-illness risk.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL; Annual government self-assessment. Freshness: ANNUAL.

## Source candidates

- **World Health Organization — State Party Self-Assessment Annual Reporting Tool (SPAR).** C13 Food Safety capacity; 2025 dashboard. Version: 2025 data; dashboard updated 15 May 2026. Grades: A4/L4/C3/M3. [Access](https://extranet.who.int/e-spar/Home/CapacityScoreDetails) · [Methodology](https://extranet.who.int/e-spar/) · [Licence](https://data.who.int/about/data/terms-and-conditions)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 82/91 appears highly plausible; exact 2025 download not joined.
- **VERIFIED publisher scope:** WHO SPAR covers IHR States Parties using 35 indicators across 15 capacities.
- Annual global reporting is broad, but non-response and self-assessment bias need measurement.

## Methodology and comparability

- SPAR is a structured annual self-assessment against IHR capacities.
- It measures national capacity, not inspections, outbreak incidence or restaurant-level safety.

## Licensing and reuse

- WHO data terms generally use CC BY 4.0 with dataset-specific notices; verify the dashboard export.

## Country and entity mapping

- States Parties map nationally; preserve missing reports and score revisions.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S3**.
- Use published C13 capacity score only; avoid averaging all 15 IHR capacities.

## Overlap, limitations, and blockers

- Overlap: Existing health-system criteria.
- Self-reporting may inflate capacity.
- National capacity may not predict day-to-day food safety.
- Reason codes: CMP_SELF_REPORTED; DEF_CAPACITY_NOT_OUTCOME; COV_EXACT_JOIN_REQUIRED.

## Recommendation

Run an experimental Phase 3E probe; label it Food-safety system capacity.

## Evidence ledger

- **VERIFIED:** WHO exposes a 2025 SPAR capacity dashboard including Food Safety. — [source](https://extranet.who.int/e-spar/Home/CapacityScoreDetails)
- **ESTIMATED:** Stable-91 coverage is not measured. — Phase 3C Batch 3

## Open questions

- Is a system-capacity measure sufficiently decision-useful without outcome data?

# C67 — Long-term climate-change exposure

**Relocation question.** How large are projected long-term heat and precipitation changes under a declared emissions scenario and horizon?

**Operational definition.** A scenario-specific national climate-hazard projection, not a single factual forecast or vulnerability score.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_DERIVED_FROM_GRID; Downscaled multi-model climate projections. Freshness: PERIODIC_MODEL_RELEASE.

## Source candidates

- **World Bank Climate Change Knowledge Portal — Projected Climate Data CMIP6.** Temperature and precipitation projections by SSP/horizon. Version: CMIP6; 1950-2100. Grades: A4/L4/C3/M3. [Access](https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree) · [Methodology](https://climateknowledgeportal.worldbank.org/download-data) · [Licence](https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree)

## Coverage and freshness

- **ESTIMATED, not measured:** 91/91 spatial coverage appears plausible; country aggregation not measured.
- **VERIFIED publisher scope:** World Bank CCKP CMIP6 is global at 0.25 degrees, 1950-2100.
- Raster coverage is global, but a defensible national aggregation and coastal/territory mapping must be tested.

## Methodology and comparability

- Results depend on scenario, reference period, horizon, ensemble statistic and variable.
- Country means can hide populated-coast and city exposure.

## Licensing and reuse

- The World Bank catalogue marks the dataset CC BY 4.0.

## Country and entity mapping

- Requires reproducible country geometry and land/population weighting.
- Small islands may need careful grid-cell treatment.

## Scoring feasibility

- Direction: **CONTEXT_DEPENDENT**; grade: **S2**.
- No single score until scenario, horizon, variables and weighting are user-approved.

## Overlap, limitations, and blockers

- Overlap: C68, C70.
- Projection uncertainty is material.
- Hazard change is not adaptation capacity or realised loss.
- Reason codes: SCO_SCENARIO_CHOICE_REQUIRED; GRA_SPATIAL_AGGREGATION.

## Recommendation

Run an experimental methodology probe, not a production score probe.

## Evidence ledger

- **VERIFIED:** CCKP provides global 0.25-degree CMIP6 data through 2100 under CC BY 4.0. — [source](https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree)
- **ESTIMATED:** Stable-91 country aggregation was not measured. — Phase 3C Batch 3

## Open questions

- Which SSP, horizon and exposure variables answer the relocation question?

# C62 — Digital-government readiness

**Relocation question.** How extensively has the government adopted common digital-government systems and practices?

**Operational definition.** Use GovTech practices/components diagnostically; do not represent GTMI as an official readiness ranking.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL; Government survey plus public-web verification. Freshness: TRIENNIAL.

## Source candidates

- **World Bank — GovTech Dataset / GTMI 2025.** 48 indicators across four focus areas. Version: 2025 update. Grades: A4/L4/C3/M4. [Access](https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset) · [Methodology](https://www.worldbank.org/en/programs/govtech/gtmi) · [Licence](https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset)

## Coverage and freshness

- **ESTIMATED, not measured:** About 90/91 appears plausible; Nicaragua is the known publisher-scope exclusion.
- **VERIFIED publisher scope:** 2025 GovTech dataset covers 197 economies; 158 survey responses and 39 public-data assessments.
- Publisher scope is nearly complete but the exact workbook was not joined.

## Methodology and comparability

- The World Bank explicitly says GTMI is not intended to rank or assess readiness/performance.
- Mixed self-reported and public-web inputs can have different evidence quality.

## Licensing and reuse

- The dataset catalogue specifies CC BY 4.0.

## Country and entity mapping

- Economy-to-ISO mapping should be strong; Nicaragua requires explicit missing handling.

## Scoring feasibility

- Direction: **NONE_WITHOUT_REDESIGN**; grade: **S1**.
- Use component facts or an unscored diagnostic until a defensible relocation-oriented construct exists.

## Overlap, limitations, and blockers

- Overlap: C05, Governance criteria.
- Practice adoption does not prove service usability for immigrants.
- Triennial updates are adequate only for structural change.
- Reason codes: SCO_PUBLISHER_DISCLAIMS_RANKING; COV_EXACT_JOIN_REQUIRED.

## Recommendation

Experimental only; inspect components in Phase 3E and reject a direct GTMI rank.

## Evidence ledger

- **VERIFIED:** The 2025 dataset covers 197 economies and is CC BY 4.0. — [source](https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset)
- **VERIFIED:** The publisher says GTMI is not a readiness/performance ranking. — [source](https://www.worldbank.org/en/programs/govtech/gtmi)

## Open questions

- Which GovTech components directly affect a newcomer rather than general public administration?

# C68 — Natural-disaster risk

**Relocation question.** How exposed is the destination to natural hazards after accounting for vulnerability and coping capacity?

**Operational definition.** Use INFORM Risk or its natural-hazard components; separate hazard exposure from vulnerability/governance.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL; Composite of hazard, exposure, vulnerability and coping indicators. Freshness: ANNUAL.

## Source candidates

- **European Commission JRC and INFORM partners — INFORM Risk.** Natural hazard/exposure, vulnerability, lack of coping capacity. Version: Current annual INFORM Risk release. Grades: A4/L3/C3/M3. [Access](https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk) · [Methodology](https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology) · [Licence](https://commission.europa.eu/legal-notice_en)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 90% appears plausible; exact release join not measured.
- **VERIFIED publisher scope:** INFORM is a global open-source risk assessment.
- Global scope appears sufficient but the exact downloadable release and stable join remain to be pinned.

## Methodology and comparability

- Composite structure is transparent, but broad vulnerability and coping inputs overlap governance and development criteria.
- The full risk score is not a pure natural-hazard exposure measure.

## Licensing and reuse

- The project is open-source, but exact dataset-asset reuse terms require capture before redistribution.

## Country and entity mapping

- Country scope is global; conflict/territory treatment and missing-component imputation require inspection.

## Scoring feasibility

- Direction: **LOWER_BETTER**; grade: **S2**.
- Prefer published natural-hazard/exposure dimension; test against full INFORM score.

## Overlap, limitations, and blockers

- Overlap: C48, C66, C67, C70.
- National scores obscure local hazard zones.
- Shared governance inputs could double count.
- Reason codes: LIC_EXACT_ASSET_UNCLEAR; RED_SHARED_COMPONENTS; GRA_LOCAL_VARIATION.

## Recommendation

Conditional Phase 3E probe focused on natural-hazard exposure, subject to exact licence capture.

## Evidence ledger

- **VERIFIED:** INFORM documents a global composite of hazards/exposure, vulnerability and lack of coping capacity. — [source](https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology)
- **ESTIMATED:** Exact stable-91 coverage and asset licence were not measured. — Phase 3C Batch 3

## Open questions

- Use exposure-only or the full vulnerability-adjusted risk score?

# C06 — International-student accessibility

**Relocation question.** How established is the destination as a host for internationally mobile tertiary students?

**Operational definition.** Narrow to inbound internationally mobile student stock/rate; it measures realised presence, not admission, visa, tuition or accessibility.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_PROFILE_CAVEAT; Administrative education statistics. Freshness: ANNUAL_WITH_LAG.

## Source candidates

- **UNESCO Institute for Statistics — UIS global education database.** Inbound internationally mobile students; inbound mobility rate. Version: September 2025 release; February 2026 background update. Grades: A4/L3/C3/M3. [Access](https://uis.unesco.org/en/news/uis-launches-september-2025-global-education-data-release-0) · [Methodology](https://uis.unesco.org/en/methodology/communication-et-information) · [Licence](https://www.unesco.org/en/open-access/cc-sa)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 82/91 appears plausible; exact series join not measured.
- **VERIFIED publisher scope:** UNESCO UIS releases cover more than 200 countries and territories.
- Publisher scope is broad, but inbound-mobility availability and recency vary.

## Methodology and comparability

- Internationally mobile students are identified by prior residence or education where available.
- Observed inbound stock reflects attractiveness and capacity as well as accessibility.

## Licensing and reuse

- Exact UIS bulk-download licence and third-party restrictions need capture; do not infer from general UNESCO pages.

## Country and entity mapping

- Country/economy and academic-year mapping need normalization.
- Very small destinations can have volatile rates.

## Scoring feasibility

- Direction: **HIGHER_BETTER_WITH_CAVEAT**; grade: **S2**.
- Prefer published inbound mobility rate; do not call it admissions accessibility.

## Overlap, limitations, and blockers

- Overlap: C01, C35.
- Does not measure tuition, visas, language or selectivity.
- May reward destinations with capacity constraints and high fees.
- Reason codes: DEF_OUTCOME_NOT_ACCESS; LIC_EXACT_ASSET_UNCLEAR; COV_EXACT_JOIN_REQUIRED.

## Recommendation

Experimental only after renaming to International-student presence; otherwise defer.

## Evidence ledger

- **VERIFIED:** UIS states that its 2025 education release covers more than 200 countries and territories. — [source](https://uis.unesco.org/en/news/uis-launches-september-2025-global-education-data-release-0)
- **ESTIMATED:** Exact stable-91 coverage and licence were not measured. — Phase 3C Batch 3

## Open questions

- Is realised student presence a useful independent criterion or only context for C01/C35?

# C75 — Religious freedom and freedom of expression

**Relocation question.** How strongly are freedom of expression and religious freedom protected in law and practice?

**Operational definition.** Use a small, predeclared V-Dem indicator/index subset with uncertainty; do not invent a broad civil-liberties composite.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL; Expert-coded annual estimates. Freshness: ANNUAL.

## Source candidates

- **V-Dem Institute — V-Dem Dataset v16.** Freedom of expression and religion-related indicators/indices. Version: Version 16, March 2026. Grades: A4/L2/C3/M3. [Access](https://www.v-dem.net/data/the-v-dem-dataset/) · [Methodology](https://www.v-dem.net/documents/55/codebook_v16.pdf) · [Licence](https://www.v-dem.net/about/faq/)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 90% appears plausible; exact variables not joined.
- **VERIFIED publisher scope:** V-Dem v16 contains country-year data for 531 indicators and 251 indices.
- Dataset scope is broad, but exact variables, rater counts and current values require a probe.

## Methodology and comparability

- Expert-coded estimates include uncertainty and variable rater counts.
- V-Dem recommends caution or filtering when an observation has three or fewer raters.

## Licensing and reuse

- V-Dem says its data are open source and free to use, but an exact commercial redistribution licence was not verified for the v16 archive.

## Country and entity mapping

- Historical country units and current states require a pinned country-year mapping.
- Retain uncertainty and rater-count variables.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S2**.
- Select published indices or variables; use latest multi-year median and expose uncertainty.

## Overlap, limitations, and blockers

- Overlap: C42, C45, C48, C49.
- Expert perception may not represent minority-specific lived experience.
- Combining two freedoms introduces normative weighting.
- Reason codes: LIC_COMMERCIAL_REUSE_UNCLEAR; SCO_VARIABLE_SELECTION_REQUIRED; CMP_EXPERT_CODED.

## Recommendation

Conditional experimental probe only after exact licence and variable selection are resolved.

## Evidence ledger

- **VERIFIED:** V-Dem v16 was released in March 2026 and provides 531 indicators and 251 indices. — [source](https://www.v-dem.net/data/the-v-dem-dataset/)
- **ESTIMATED:** Commercial redistribution terms for the exact v16 archive remain unverified. — Phase 3C Batch 3

## Open questions

- Separate expression and religion into preference-weighted dimensions?
- Which v16 variables have adequate rater counts?

# C70 — Climate resilience and adaptation readiness

**Relocation question.** How ready is a country to convert investment into climate adaptation while reducing vulnerability?

**Operational definition.** ND-GAIN readiness/vulnerability composite, with overlap explicitly audited.

**Finding.** DEFERRED_REDUNDANT; **recommendation:** DEFER.

**Natural granularity and observation.** NATIONAL; Composite of 45 indicators. Freshness: ANNUAL_WITH_REVISIONS.

## Source candidates

- **Notre Dame Global Adaptation Initiative — ND-GAIN Country Index.** Vulnerability (36 indicators) and readiness (9 indicators). Version: Site updated 26 June 2026; data through 2024. Grades: A4/L4/C3/M3. [Access](https://gain-new.crc.nd.edu/about/download) · [Methodology](https://gain-new.crc.nd.edu/about/methodology) · [Licence](https://gain-new.crc.nd.edu/about/download)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 90% appears plausible.
- **VERIFIED publisher scope:** ND-GAIN download page states 192 UN countries with data through 2024.
- Coverage is strong, but the reason to defer is construct overlap rather than country availability.

## Methodology and comparability

- Readiness includes economic, governance and social inputs; vulnerability spans six sectors.
- Many inputs overlap governance, innovation, education, infrastructure and ICT criteria.

## Licensing and reuse

- Download page specifies CC Attribution 3.0 Unported.

## Country and entity mapping

- Broad UN-country coverage; exact current download should be joined if revived.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S3**.
- Published score only; no Konsider reweighting without overlap analysis.

## Overlap, limitations, and blockers

- Overlap: C05, C48, C49, C62, C67, C68.
- Composite score obscures drivers.
- Current pages contain inconsistent historical-period wording.
- Reason codes: RED_SHARED_COMPONENTS; DEF_COMPOSITE_TOO_BROAD.

## Recommendation

Defer until the active catalog is consolidated in Phase 3E; revive only if it replaces rather than duplicates multiple criteria.

## Evidence ledger

- **VERIFIED:** ND-GAIN states coverage of 192 UN countries and CC BY 3.0 reuse. — [source](https://gain-new.crc.nd.edu/about/download)
- **ESTIMATED:** Overlap judgement is preliminary. — Phase 3C Batch 3

## Open questions

- Would ND-GAIN replace C67/C68 plus governance inputs, or is hazard-specific scoring preferable?

# C78 — Overall life satisfaction

**Relocation question.** How do residents rate their lives overall in the destination?

**Operational definition.** Country-level Cantril Ladder life evaluation, typically reported as a three-year average.

**Finding.** DEFERRED_LICENCE; **recommendation:** DEFER.

**Natural granularity and observation.** NATIONAL_SURVEY; Probability-sample survey. Freshness: ANNUAL_THREE_YEAR_AVERAGE.

## Source candidates

- **Wellbeing Research Centre / Gallup / UN SDSN — World Happiness Report 2026 data.** Life evaluation three-year averages. Version: 2026 report. Grades: A4/L2/C4/M3. [Access](https://www.worldhappiness.report/data-sharing/) · [Methodology](https://www.worldhappiness.report/ed/2026/) · [Licence](https://www.worldhappiness.report/data-sharing/)

## Coverage and freshness

- **ESTIMATED, not measured:** Likely below full coverage and potentially near the threshold; not measured.
- **VERIFIED publisher scope:** World Happiness Report 2026 publishes country three-year averages using Gallup World Poll.
- Small states and irregular survey years may create gaps.

## Methodology and comparability

- Life evaluation is a standard 0-10 Cantril Ladder measure.
- Three-year pooling improves precision but reduces freshness and can straddle shocks.

## Licensing and reuse

- Underlying Gallup World Poll microdata and extended data require institutional access; exact commercial reuse of report tables is unresolved.

## Country and entity mapping

- Some small countries lack recent observations; country labels require a join.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S3**.
- Published three-year average if licensed; retain confidence intervals.

## Overlap, limitations, and blockers

- Overlap: C71, Many outcome criteria.
- Broad outcome can double-count all domain-specific criteria.
- Respondent adaptation and culture affect comparisons.
- Reason codes: LIC_COMMERCIAL_REUSE_UNCLEAR; RED_OUTCOME_UMBRELLA; COV_EXACT_JOIN_REQUIRED.

## Recommendation

Defer pending exact dataset licence and overlap policy.

## Evidence ledger

- **VERIFIED:** WHR 2026 publishes three-year life-evaluation averages based on Gallup World Poll. — [source](https://www.worldhappiness.report/data-sharing/)
- **ESTIMATED:** Stable-91 coverage and production licence are unverified. — Phase 3C Batch 3

## Open questions

- Should subjective wellbeing be an independent outcome or a validation benchmark?

# C42 — Social inclusion and acceptance of immigrants

**Relocation question.** How accepting are residents of immigrants as neighbours or members of society?

**Operational definition.** A repeated national-attitude measure; WVS is the best open research candidate but not a current global production panel.

**Finding.** DEFERRED_COVERAGE; **recommendation:** DEFER.

**Natural granularity and observation.** NATIONAL_SURVEY; National probability survey. Freshness: MULTIYEAR_WAVE.

## Source candidates

- **World Values Survey Association — World Values Survey Wave 7.** Immigrants/foreign workers as neighbours and related attitudes. Version: Wave 7, 2017-2021. Grades: A4/L2/C3/M3. [Access](https://www.worldvaluessurvey.org/WVSEventsShow.jsp?ID=413) · [Methodology](https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp) · [Licence](https://www.worldvaluessurvey.org/WVSContents.jsp)

## Coverage and freshness

- **ESTIMATED, not measured:** Below 82/91 is likely.
- **VERIFIED publisher scope:** WVS Wave 7 covers 77 countries/societies, fielded 2017-2021.
- Publisher scope alone is below the 90% threshold and observations are mixed-date.

## Methodology and comparability

- National probability samples are typically 1,000-3,200 respondents.
- Question wording and social desirability limit interpretation as lived immigrant experience.

## Licensing and reuse

- Data are free for academic use; production/commercial redistribution terms require explicit permission.

## Country and entity mapping

- Wave coverage and field years vary; societies and territories need normalization.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S2**.
- Possible percentage rejecting anti-immigrant response, but not production-ready.

## Overlap, limitations, and blockers

- Overlap: C45, C75.
- Below threshold and stale for fast-moving sentiment.
- Attitudes do not measure discrimination outcomes.
- Reason codes: COV_BELOW_90_PERCENT; STA_MIXED_FIELD_YEARS; LIC_COMMERCIAL_REUSE_UNCLEAR.

## Recommendation

Defer; revisit only with a licensed recurring global attitude source.

## Evidence ledger

- **VERIFIED:** WVS Wave 7 reports 77 participating countries/societies and 2017-2021 fieldwork. — [source](https://www.worldvaluessurvey.org/WVSEventsShow.jsp?ID=413)
- **ESTIMATED:** Stable-91 coverage is inferred from publisher scope, not joined. — Phase 3C Batch 3

## Open questions

- Would a smaller-country experimental layer be useful despite missingness?

# C57 — Water-supply reliability

**Relocation question.** Can households in likely destination cities obtain safe piped water continuously when needed?

**Operational definition.** Utility/city continuity and service-interruption performance, not national basic-water access.

**Finding.** DEFERRED_CITY_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** CITY_OR_UTILITY; Household survey or utility administrative data. Freshness: ANNUAL_OR_IRREGULAR.

## Source candidates

- **WHO/UNICEF JMP — JMP household WASH estimates.** Drinking water available when needed. Version: 2025 report; 2024 estimates. Grades: A4/L3/C3/M3. [Access](https://washdata.org/report/jmp-2025-wash-households) · [Methodology](https://washdata.org/monitoring/drinking-water) · [Licence](https://washdata.org/terms-use)

## Coverage and freshness

- **ESTIMATED, not measured:** Below 82/91 for the exact reliability construct is likely.
- **VERIFIED publisher scope:** JMP 2025 reports 'available when needed' for 144 countries/areas globally.
- Global publisher scope does not ensure stable-universe coverage, and high-income reporting is incomplete.

## Methodology and comparability

- Availability when needed is one safely managed service component.
- Household responses do not provide utility outage frequency or neighbourhood reliability.

## Licensing and reuse

- JMP reuse terms and exact downloadable-file notices require capture.

## Country and entity mapping

- Utility boundaries rarely align with national or city boundaries.
- National estimates can conceal rationing in particular cities.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S1**.
- No independent national score; future city layer could use hours/day and interruption frequency.

## Overlap, limitations, and blockers

- Overlap: C53.
- Coverage below threshold is likely.
- Exact relocation value is city and neighbourhood specific.
- Reason codes: COV_BELOW_90_PERCENT; GRA_CITY_UTILITY_REQUIRED.

## Recommendation

Defer to a city/utility data programme and keep C53 as the national service proxy.

## Evidence ledger

- **VERIFIED:** JMP 2025 reports availability-when-needed estimates for 144 countries/areas. — [source](https://washdata.org/report/jmp-2025-wash-households)
- **ESTIMATED:** Stable-91 coverage was not joined. — Phase 3C Batch 3

## Open questions

- Which priority cities and utility metrics should define a later pilot?

# C45 — LGBTQ+ legal and social inclusion

**Relocation question.** How inclusive is the destination's law for LGBTQ+ people?

**Operational definition.** ILGA World legal-category evidence; social inclusion would require a separate survey source.

**Finding.** REJECTED_LICENCE; **recommendation:** REJECT.

**Natural granularity and observation.** NATIONAL_LEGAL; Expert-coded law. Freshness: PERIODIC.

## Source candidates

- **ILGA World — Laws on Us.** 11 legal categories. Version: 30 May 2024. Grades: A4/L1/C4/M3. [Access](https://ilga.org/laws-on-us-report/) · [Methodology](https://ilga.org/laws-on-us-report/) · [Licence](https://ilga.org/laws-on-us-report/)

## Coverage and freshness

- **ESTIMATED, not measured:** Global coverage appears plausible.
- **VERIFIED publisher scope:** ILGA World Laws on Us tracks 11 legal categories globally.
- Coverage is not the blocker; reuse terms are.

## Methodology and comparability

- Legal categories are comparable but do not capture social acceptance, enforcement or subnational variation.

## Licensing and reuse

- The current report page states CC BY-NC 4.0, incompatible with an unrestricted commercial production dataset.
- A conflicting asset snippet makes conservative treatment necessary; obtain written permission before reconsideration.

## Country and entity mapping

- National legal mapping is broad; federal/subnational exceptions may matter.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S2**.
- Technically possible but normatively weighted and presently licence-blocked.

## Overlap, limitations, and blockers

- Overlap: C42, C75.
- Law is not lived inclusion.
- Combining 11 categories requires normative choices.
- Reason codes: LIC_NONCOMMERCIAL; SCO_NORMATIVE_WEIGHTS_REQUIRED.

## Recommendation

Reject for Phase 3E production candidacy unless ILGA grants suitable reuse permission.

## Evidence ledger

- **VERIFIED:** The ILGA report page states CC BY-NC 4.0. — [source](https://ilga.org/laws-on-us-report/)
- **ESTIMATED:** Global coverage was not joined because licence is dispositive. — Phase 3C Batch 3

## Open questions

- Would ILGA provide a commercial licence or written permission for derived country scores?

# C69 — Environmental quality beyond PM2.5

**Relocation question.** How well does the country perform across environmental health and ecosystem vitality beyond air pollution?

**Operational definition.** Yale Environmental Performance Index composite.

**Finding.** REJECTED_LICENCE_REDUNDANCY; **recommendation:** REJECT.

**Natural granularity and observation.** NATIONAL_COMPOSITE; Composite of modelled and reported indicators. Freshness: BIENNIAL.

## Source candidates

- **Yale Center for Environmental Law & Policy — Environmental Performance Index 2024.** Overall EPI and issue categories. Version: 2024 EPI. Grades: A4/L1/C2/M3. [Access](https://epi.yale.edu/about-epi) · [Methodology](https://epi.yale.edu/faq/2024-epi-faq) · [Licence](https://epi.yale.edu/faq/2024-epi-faq)

## Coverage and freshness

- **ESTIMATED, not measured:** At least 90% appears plausible.
- **VERIFIED publisher scope:** EPI provides broad country coverage.
- Coverage is not the blocker.

## Methodology and comparability

- Methodology and indicators change between editions; Yale warns against comparing scores across editions.
- The composite overlaps air, climate, water, biodiversity and sanitation criteria.

## Licensing and reuse

- EPI 2024 is CC BY-NC-SA 4.0 and prohibits commercial use.

## Country and entity mapping

- National mapping is broad but does not solve city-level environmental variation.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S1**.
- Do not ingest or rescore under current licence.

## Overlap, limitations, and blockers

- Overlap: C53, C57, C67, Existing PM2.5 criterion.
- Composite is broad and version-unstable.
- National score hides local exposures.
- Reason codes: LIC_NONCOMMERCIAL; RED_COMPOSITE_OVERLAP; CMP_VERSION_BREAKS.

## Recommendation

Reject as an independent production criterion; use open, specific indicators instead.

## Evidence ledger

- **VERIFIED:** Yale states EPI 2024 is CC BY-NC-SA 4.0 and editions are not directly comparable. — [source](https://epi.yale.edu/faq/2024-epi-faq)

## Open questions

- None unless commercial permission becomes available.
