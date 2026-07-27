# Konsider Phase 3C — Batch 1 source-feasibility research

Evidence cutoff: **24 July 2026**
Universe: **stable_supported_v1 (91 countries)**
Scope: the first 15-criterion batch recommended by Phase 3B. This is source feasibility research, not production ingestion or a complete legal audit.

## How to read evidence

- **VERIFIED** means confirmed from an identified official/authoritative page, metadata record or exact dataset documentation.
- **MEASURED** means the exact source was downloaded or queried and joined to the stable 91-country ISO3 list.
- **ESTIMATED** is a preliminary Phase 3C judgement.
- **HYPOTHESIS** is an unverified discovery lead.

## Outcome

Three criteria should proceed to deterministic Phase 3E probes: **C30 Existing immigrant share**, **C11 Overall job-market opportunity**, and **C08 School education quality**. Three more justify conditional experimental or recovery probes: **C66 Extreme-weather risk**, **C01 Overall higher-education opportunity**, and **C58 Internet access, speed, and reliability** (only under a narrowed access/penetration definition). Nine should not consume a national Phase 3E probe yet.

## Comparison table

| Rank | ID | Phase 3A status | Natural granularity | Coverage | A/L/C/S | Phase 3E track |
|---:|---|---|---|---|---|---|
| 1 | C11 | PROBE_APPROVED | NATIONAL | 88/91 measured; 88 fresh | A4/L4/C4/S3 | DETERMINISTIC |
| 2 | C32 | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated | A4/L3/C3/S1 | No further 3E work |
| 3 | C33 | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated | A4/L1/C2/S1 | No further 3E work |
| 4 | C17 | DEFERRED | NATIONAL_WITH_CITY_CAVEAT | 76/91 measured; 60 fresh | A4/L4/C3/S3 | No further 3E work |
| 5 | C21 | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated | A4/L4/C4/S2 | No further 3E work |
| 6 | C25 | DEFERRED_CITY_LAYER | CITY_OR_REGIONAL | LOW estimated | A4/L4/C3/S3 | No further 3E work |
| 7 | C50 | DEFERRED | NATIONAL | 91/91 measured; 0 fresh | A4/L4/C4/S4 | No further 3E work |
| 8 | C40 | DEFERRED_CITY_LAYER | CITY_OR_REGIONAL | MEDIUM estimated | A2/L1/C2/S2 | No further 3E work |
| 9 | C01 | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_CITY_CAVEAT | 88/91 measured; 77 fresh | A4/L4/C4/S2 | CONDITIONAL |
| 10 | C30 | PROBE_APPROVED | NATIONAL | 91/91 measured; 91 fresh | A4/L4/C4/S3 | DETERMINISTIC |
| 11 | C12 | DEFERRED_CITY_LAYER | CITY_OR_REGIONAL | 66/91 measured; 66 fresh | A4/L4/C3/S2 | No further 3E work |
| 12 | C58 | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_CITY_CAVEAT | 91/91 measured; 91 fresh | A4/L4/C4/S3 | CONDITIONAL |
| 13 | C56 | DEFERRED | NATIONAL_WITH_CITY_CAVEAT | 0/91 measured; 0 fresh | A4/L4/C4/S2 | No further 3E work |
| 14 | C08 | PROBE_APPROVED | NATIONAL_WITH_CITY_CAVEAT | 89/91 measured; 88 fresh | A4/L4/C4/S4 | DETERMINISTIC |
| 15 | C66 | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_CITY_CAVEAT | 91/91 measured; 91 fresh | A4/L3/C4/S2 | CONDITIONAL |

## Phase 3E shortlist

1. **C30 — Existing immigrant share** (deterministic): Proceed to deterministic Phase 3E probe; measured current coverage is 91/91.
2. **C11 — Overall job-market opportunity** (deterministic): Proceed to a deterministic Phase 3E probe. The measured 88/91 intersection clears the 82-country threshold but requires an explicit missing-country policy.
3. **C08 — School education quality** (deterministic): Proceed to deterministic Phase 3E probe; measured field coverage is 89/91 and the source is current, official and reusable.
4. **C66 — Extreme-weather risk** (conditional): Experimental Phase 3E probe only. Coverage is complete, but a Konsider-specific weather subset and weighting need defensibility testing.
5. **C01 — Overall higher-education opportunity** (conditional): Experimental/recovery probe only. Overall coverage is 88/91, but only 77/91 have 2023+ data and 81/91 have 2021+ data.
6. **C58 — Internet access, speed, and reliability** (conditional): Experimental/redundancy probe only for a narrowed access-and-penetration criterion. Do not claim speed or reliability.

## Open decisions across the batch

1. Whether 82/91 remains the probe threshold while production continues to require 91/91 complete cases.
2. Whether modelled current-year ILO observations are acceptable for C11.
3. Whether C30 is higher-better, informational, or preference-based.
4. Which HCI+ education field should represent C08 and how to resolve its catalogue/file year-label discrepancy.
5. Whether the INFORM weather subset may omit heatwaves and wildfire, and how it should be aggregated.
6. Whether C58 adds value beyond the existing infrastructure experiment.
7. Which city and user-profile universes Phase 3 should support before resuming C17, C21, C25, C32, C33 and C40.

## Recurring publisher and dataset families

- **World Bank WDI/HNP distributions:** strongest reusable bridge for UN/WHO/ITU indicators where the exact representation is CC BY 4.0.
- **ILOSTAT bulk/API:** strongest labour family; excellent licence and harmonisation, but earnings and occupational tables miss the 90% threshold.
- **UNESCO UIS via WDI and direct Data Browser:** strong education family; direct UIS is CC BY-SA 4.0 while WDI representations are CC BY 4.0.
- **OECD comparative systems:** high methodological quality but structurally inadequate for a 91-country global universe.
- **WHO/ITU direct systems:** authoritative and broad, but direct commercial reuse is constrained or unclear; prefer a clearly licensed World Bank representation.
- **EC JRC / INFORM:** globally complete and transparent risk workbooks; exact derivative-field and upstream-rights handling still needs confirmation.
- **National immigration/tax/housing authorities:** indispensable for profile/city layers, but high-maintenance and not a harmonised global feed.

## Criteria requiring city or profile treatment

- City/regional: **C25, C40, C12**; **C17** also needs a city/occupation adjustment.
- Profile/legal/household: **C32, C33, C21**.
- National-with-local caveat: **C01, C08, C50, C56, C58, C66**.

---

# C11 — Overall job-market opportunity

## Decision summary

- Status: `PROBE_APPROVED`
- Recommendation: Proceed to a deterministic Phase 3E probe. The measured 88/91 intersection clears the 82-country threshold but requires an explicit missing-country policy.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_NOT_FULL_91`
- Caveat codes: `RED_SHARED_COMPONENTS`, `CMP_MODEL_ASSUMPTIONS_OPAQUE`

## 1. Relocation question

How strong is the destination's national labour market for a working-age newcomer, before occupation-specific matching?

## 2. Precise definition

A narrow national composite of modelled unemployment, employment-to-population ratio and labour-force participation for total population age 15+.

## 3. Classification and granularity

Tags: IC. Natural granularity: **NATIONAL**. Observation type: National, modelled annual estimates.

## 4. User profiles and decision value

Profiles: working-age movers, job seekers. Decision value: 5/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. International Labour Organization (ILOSTAT) — ILOSTAT bulk download

- Exact series/table: UNE_2EAP_SEX_AGE_RT_A; EMP_2WAP_SEX_AGE_RT_A; EAP_2WAP_SEX_AGE_RT_A
- Version: ILO modelled estimates, Nov. 2025
- Access: [source](https://rplumber.ilo.org/data/indicator/)
- Methodology: [methodology](https://ilostat.ilo.org/data/bulk/)
- Licence evidence: [reuse terms](https://www.ilo.org/rights-and-permissions)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- [VERIFIED] ILO modelled estimates use a common statistical system and identical age/sex dimensions.
- [ESTIMATED] The three components partly duplicate one latent labour-utilisation factor.

## 7. Expected or measured 91-country coverage

**MEASURED:** 88/91 found; 88/91 fresh under the stated criterion rule; 3 missing.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. Annual edition pinning is required; projections beyond the edition's current year must not be mixed with observed/modelled current-year values.

## 9. Country mapping and territory policy

- [MEASURED] ISO3 joined deterministically; ATG, GRD and UKR were absent from all three 2025 slices.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S3`
- Proposed method: Reverse unemployment; robust-percentile each component; average only after correlation and weight sensitivity checks.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C12, C17. RED_SHARED_COMPONENTS

## 12. Retrieval, replay and maintenance

- Annual edition pinning is required; projections beyond the edition's current year must not be mixed with observed/modelled current-year values.

## 13. Blockers, caveats and reason codes

- Blockers: COV_NOT_FULL_91
- Caveats: RED_SHARED_COMPONENTS, CMP_MODEL_ASSUMPTIONS_OPAQUE

## 14. Recommendation

Proceed to a deterministic Phase 3E probe. The measured 88/91 intersection clears the 82-country threshold but requires an explicit missing-country policy.

## 15. Open questions

- Should C11 remain a composite or expose unemployment and employment separately?
- Is 2025 accepted as a modelled current-year value?

## Evidence register

- **MEASURED:** The three exact ILOSTAT 2025 total/15+ series each returned 88 stable countries; common missing ISO3 codes were ATG, GRD and UKR. [Evidence](https://rplumber.ilo.org/data/indicator/)
- **VERIFIED:** The ILOSTAT catalogue labels the series as Nov. 2025 modelled estimates and exposes reproducible bulk CSV downloads. [Evidence](https://ilostat.ilo.org/data/bulk/)
- **VERIFIED:** ILOSTAT data licence is CC BY 4.0 for datasets published from 3 May 2023. [Evidence](https://www.ilo.org/rights-and-permissions)

---

# C32 — Skilled-work visa accessibility

## Decision summary

- Status: `DEFERRED_PROFILE_LAYER`
- Recommendation: Defer to a future profile/legal-mobility layer. Reject it as an independent destination criterion.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `GRA_ORIGIN_SPECIFIC`, `GRA_PROFESSION_SPECIFIC`, `PRF_PROFILE_ONLY`, `OPS_EXCESSIVE_MANUAL_MAINTENANCE`
- Caveat codes: `CMP_LEGAL_NOT_LIVED_OUTCOME`, `FRS_UPDATE_CADENCE_UNKNOWN`

## 1. Relocation question

Given a person's nationality, occupation, qualifications, salary and employer situation, how feasible is a lawful skilled-work route?

## 2. Precise definition

A profile-derived eligibility and friction assessment, not a destination-only national score.

## 3. Classification and granularity

Tags: IC, SC, LF. Natural granularity: **PROFILE_ONLY**. Observation type: Administrative/legal policy; profile- and origin-dependent.

## 4. User profiles and decision value

Profiles: skilled workers, regulated professionals, employer-sponsored applicants. Decision value: 5/5. Profile dependence: PROFILE_ONLY.

## 5. Source candidates

### 1. OECD — Indicators of Talent Attractiveness 2023

- Exact series/table: Highly educated workers; migration-policy dimension
- Version: 2023
- Access: [source](https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html)
- Methodology: [methodology](https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html)
- Licence evidence: [reuse terms](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)
- Grades: authority A4; licence L3; comparability C3; mapping M3
- Evidence level: **VERIFIED**

### 2. European Commission — EU Immigration Portal

- Exact series/table: Highly-qualified worker country pages
- Version: accessed 2026-07-24
- Access: [source](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en)
- Methodology: Not independently located
- Licence evidence: [reuse terms](https://commission.europa.eu/legal-notice_en)
- Grades: authority A4; licence L4; comparability C2; mapping M3
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- [VERIFIED] EU rules depend on job offer, salary threshold, qualifications and member-state implementation.
- [ESTIMATED] OECD ITA is useful discovery evidence but OECD-only and broader than visa accessibility.

## 7. Expected or measured 91-country coverage

**ESTIMATED:** LOW; no source query/download was used to count stable countries.

## 8. Freshness assessment

Class: `CURRENT_POLICY`. Legal rules and thresholds require frequent country-by-country change detection and dated snapshots.

## 9. Country mapping and territory policy

- Country is insufficient: origin, profession, employer, salary and family status alter eligibility.

## 10. Scoring options and sensitivity risks

- Mode/grade: `PROFILE_DERIVED` / `S1`
- Proposed method: Rule-engine eligibility plus route-specific friction; no standalone country percentile.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C11, C12, C33. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Legal rules and thresholds require frequent country-by-country change detection and dated snapshots.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, GRA_ORIGIN_SPECIFIC, GRA_PROFESSION_SPECIFIC, PRF_PROFILE_ONLY, OPS_EXCESSIVE_MANUAL_MAINTENANCE
- Caveats: CMP_LEGAL_NOT_LIVED_OUTCOME, FRS_UPDATE_CADENCE_UNKNOWN

## 14. Recommendation

Defer to a future profile/legal-mobility layer. Reject it as an independent destination criterion.

## 15. Open questions

- Which origin passports and occupations define the first supported profiles?

## Evidence register

- **VERIFIED:** The EU portal applies to 25 EU countries and describes job-offer, qualification and salary conditions. [Evidence](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en)
- **VERIFIED:** OECD ITA 2023 compares talent attractiveness for highly educated workers but is limited to OECD countries. [Evidence](https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html)
- **ESTIMATED:** No current official global dataset was verified that converts individual skilled-work eligibility into comparable destination scores. [Evidence](Phase 3C source search)

---

# C33 — Permanent-residency accessibility

## Decision summary

- Status: `DEFERRED_PROFILE_LAYER`
- Recommendation: Defer to a route-aware profile layer; reject a single national accessibility score.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `SRC_NO_AUTHORITATIVE_SOURCE`, `LIC_REDISTRIBUTION_RESTRICTED`, `GRA_ORIGIN_SPECIFIC`, `PRF_PROFILE_ONLY`, `OPS_EXCESSIVE_MANUAL_MAINTENANCE`
- Caveat codes: `CMP_LEGAL_NOT_LIVED_OUTCOME`, `FRS_POLICY_SNAPSHOT_OUTDATED`

## 1. Relocation question

For a specific migrant route and personal history, what lawful path exists to permanent residence and on what conditions?

## 2. Precise definition

A route-specific legal pathway assessment covering qualifying residence, permit continuity, income/language conditions and exclusions.

## 3. Classification and granularity

Tags: IC, SC, LF. Natural granularity: **PROFILE_ONLY**. Observation type: Administrative/legal policy; route- and profile-dependent.

## 4. User profiles and decision value

Profiles: temporary skilled workers, students transitioning to work, family migrants. Decision value: 5/5. Profile dependence: PROFILE_ONLY.

## 5. Source candidates

### 1. UN DESA / IOM — SDG indicator 10.7.2

- Exact series/table: Country migration-policy data, 2021 update
- Version: 2021
- Access: [source](https://www.un.org/development/desa/pd/data/sdg-indicator-1072)
- Methodology: [methodology](https://www.un.org/development/desa/pd/data/sdg-indicator-1072)
- Licence evidence: [reuse terms](https://www.un.org/en/about-us/terms-of-use)
- Grades: authority A4; licence L1; comparability C2; mapping M3
- Evidence level: **VERIFIED**

### 2. National immigration authorities — Residence and settlement rules

- Exact series/table: Not yet identified
- Version: Not pinned
- Access: No single global endpoint
- Methodology: Not independently located
- Licence evidence: No dataset-specific evidence verified
- Grades: authority A4; licence L2; comparability C1; mapping M2
- Evidence level: **HYPOTHESIS**

## 6. Comparability assessment

- SDG 10.7.2 measures broad well-managed migration policy, not personal permanent-residence eligibility.
- National terminology and qualifying residence rules are not harmonised.

## 7. Expected or measured 91-country coverage

**ESTIMATED:** LOW; no source query/download was used to count stable countries.

## 8. Freshness assessment

Class: `CURRENT_POLICY`. Requires dated legal rules, legal-review governance and frequent change detection.

## 9. Country mapping and territory policy

- Route and legal-history mapping dominate ISO country mapping.

## 10. Scoring options and sensitivity risks

- Mode/grade: `PROFILE_DERIVED` / `S1`
- Proposed method: Eligibility timeline and conditions by route; informational result rather than a destination-only score.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C32. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Requires dated legal rules, legal-review governance and frequent change detection.

## 13. Blockers, caveats and reason codes

- Blockers: SRC_NO_AUTHORITATIVE_SOURCE, LIC_REDISTRIBUTION_RESTRICTED, GRA_ORIGIN_SPECIFIC, PRF_PROFILE_ONLY, OPS_EXCESSIVE_MANUAL_MAINTENANCE
- Caveats: CMP_LEGAL_NOT_LIVED_OUTCOME, FRS_POLICY_SNAPSHOT_OUTDATED

## 14. Recommendation

Defer to a route-aware profile layer; reject a single national accessibility score.

## 15. Open questions

- Whether permanent residence and citizenship pathways should be separate product modules.

## Evidence register

- **VERIFIED:** The current official SDG 10.7.2 update is based on 2018–2021 government inquiries and measures broad migration-policy domains. [Evidence](https://www.un.org/development/desa/pd/data/sdg-indicator-1072)
- **VERIFIED:** Generic UN website terms do not provide production-compatible reuse for a derived commercial dataset. [Evidence](https://www.un.org/en/about-us/terms-of-use)
- **ESTIMATED:** No authoritative, current, global route-level permanent-residence dataset was verified. [Evidence](Phase 3C source search)

---

# C17 — Average earning potential

## Decision summary

- Status: `DEFERRED`
- Recommendation: Defer. Measured recent PPP earnings coverage is 60/91 for 2023+ and 76/91 for 2021+, below the Phase 3A threshold.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `GRA_CITY_LEVEL_REQUIRED`, `GRA_PROFESSION_SPECIFIC`
- Caveat codes: `CMP_POPULATION_DIFFERS`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

What gross earning level could a typical employee plausibly attain, before occupation and city adjustments?

## 2. Precise definition

Average monthly employee earnings converted to PPP, with explicit limits as a national proxy for personal earning potential.

## 3. Classification and granularity

Tags: IC, DO, CR. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National survey/administrative estimates, harmonised by ILOSTAT.

## 4. User profiles and decision value

Profiles: employees, skilled workers. Decision value: 5/5. Profile dependence: HIGH.

## 5. Source candidates

### 1. International Labour Organization (ILOSTAT) — ILOSTAT bulk download

- Exact series/table: EAR_EMTA_SEX_CUR_NB_A; CUR_TYPE_PPP; SEX_T
- Version: updated 2026-07-19
- Access: [source](https://rplumber.ilo.org/data/indicator/)
- Methodology: [methodology](https://ilostat.ilo.org/data/bulk/)
- Licence evidence: [reuse terms](https://www.ilo.org/rights-and-permissions)
- Grades: authority A4; licence L4; comparability C3; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Employee coverage, informal work, hours and source instruments vary.
- PPP improves price comparability but does not remove occupation or city composition effects.

## 7. Expected or measured 91-country coverage

**MEASURED:** 76/91 found; 60/91 fresh under the stated criterion rule; 15 missing.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. Currency and PPP classifications must be pinned; source breaks and multiple national observations need deterministic precedence.

## 9. Country mapping and territory policy

- ISO3 is stable; the substantive blocker is observation availability.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S3`
- Proposed method: Log PPP earnings, winsorise tails, then robust percentile; do not treat as expected salary for a user.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C11, C25. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Currency and PPP classifications must be pinned; source breaks and multiple national observations need deterministic precedence.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, GRA_CITY_LEVEL_REQUIRED, GRA_PROFESSION_SPECIFIC
- Caveats: CMP_POPULATION_DIFFERS, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Defer. Measured recent PPP earnings coverage is 60/91 for 2023+ and 76/91 for 2021+, below the Phase 3A threshold.

## 15. Open questions

- Whether a different official income concept can recover 82+ countries without changing the question.

## Evidence register

- **MEASURED:** EAR_EMTA_SEX_CUR_NB_A PPP observations covered 76 stable countries from 2021 onward and 60 from 2023 onward. [Evidence](https://rplumber.ilo.org/data/indicator/)
- **VERIFIED:** The exact ILOSTAT table was updated 19 July 2026 and spans through 2026. [Evidence](https://rplumber.ilo.org/metadata/toc/indicator/)

---

# C21 — Personal income-tax burden

## Decision summary

- Status: `DEFERRED_PROFILE_LAYER`
- Recommendation: Defer to a profile-based affordability calculator; do not use the OECD-only series as a 91-country ranking criterion.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `GRA_HOUSEHOLD_SCENARIO_REQUIRED`, `PRF_PROFILE_ONLY`
- Caveat codes: `CMP_DEFINITION_DIFFERS`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

For a given salary, household and employment arrangement, what share of labour cost or gross earnings is taken by income tax and mandatory contributions?

## 2. Precise definition

A household-scenario tax wedge or net personal average tax rate, not a universal national rate.

## 3. Classification and granularity

Tags: IC. Natural granularity: **PROFILE_ONLY**. Observation type: Administrative tax model; household-scenario dependent.

## 4. User profiles and decision value

Profiles: employees, families, self-employed workers. Decision value: 5/5. Profile dependence: PROFILE_ONLY.

## 5. Source candidates

### 1. OECD — Taxing Wages 2026 / OECD Data Explorer

- Exact series/table: OECD.CTP.TPS,DSD_TAX_WAGES_COMP@DF_TW_COMP
- Version: 2025 tax year
- Access: [source](https://data-explorer.oecd.org/)
- Methodology: [methodology](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html)
- Licence evidence: [reuse terms](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- OECD methodology is highly comparable inside 38 OECD members but not globally representative.
- Results change by earnings level, household type and social-contribution treatment.

## 7. Expected or measured 91-country coverage

**ESTIMATED:** LOW; no source query/download was used to count stable countries.

## 8. Freshness assessment

Class: `FAST_MOVING`. Annual tax-law parameter updates and scenario versioning are required.

## 9. Country mapping and territory policy

- Country mapping is straightforward; tax-unit and household mapping are not.

## 10. Scoring options and sensitivity risks

- Mode/grade: `PROFILE_DERIVED` / `S2`
- Proposed method: Compute net burden for explicit salary and household scenarios; lower is not automatically better without service-benefit context.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C25. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Annual tax-law parameter updates and scenario versioning are required.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, GRA_HOUSEHOLD_SCENARIO_REQUIRED, PRF_PROFILE_ONLY
- Caveats: CMP_DEFINITION_DIFFERS, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Defer to a profile-based affordability calculator; do not use the OECD-only series as a 91-country ranking criterion.

## 15. Open questions

- Which standard household and salary scenarios would be product-supported?

## Evidence register

- **VERIFIED:** Taxing Wages 2026 covers the 38 OECD countries and reports 2025 tax wedges/net personal average rates by household type. [Evidence](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html)
- **VERIFIED:** The exact comparative Data Explorer family is DSD_TAX_WAGES_COMP@DF_TW_COMP. [Evidence](https://data-explorer.oecd.org/)

---

# C25 — Housing affordability

## Decision summary

- Status: `DEFERRED_CITY_LAYER`
- Recommendation: Defer to the city and profile layers. National OECD ratios are useful validation data, not the independent criterion.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `COV_REGIONALLY_BIASED`, `GRA_CITY_LEVEL_REQUIRED`, `GRA_HOUSEHOLD_SCENARIO_REQUIRED`
- Caveat codes: `CMP_DEFINITION_DIFFERS`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

Can the user's household afford suitable housing in the destination city on its expected disposable income?

## 2. Precise definition

City-level rent or ownership cost divided by profile-specific disposable income, with tenure and household size explicit.

## 3. Classification and granularity

Tags: IC, SC, CR, LF. Natural granularity: **CITY_OR_REGIONAL**. Observation type: City/regional market data plus household income scenario.

## 4. User profiles and decision value

Profiles: renters, buyers, families. Decision value: 5/5. Profile dependence: HIGH.

## 5. Source candidates

### 1. OECD — Affordable Housing Database

- Exact series/table: HC1.2 Housing costs over income
- Version: files current 2025-10
- Access: [source](https://www.oecd.org/en/data/datasets/oecd-affordable-housing-database.html)
- Methodology: [methodology](https://webfs.oecd.org/Els-com/Affordable_Housing_Database/HC1-2-Housing-costs-over-income.pdf)
- Licence evidence: [reuse terms](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)
- Grades: authority A4; licence L4; comparability C3; mapping M3
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- HC1.2 total housing costs are available mainly for European countries plus New Zealand and definitions differ.
- National ratios conceal metropolitan rent dispersion.

## 7. Expected or measured 91-country coverage

**ESTIMATED:** LOW; no source query/download was used to count stable countries.

## 8. Freshness assessment

Class: `FAST_MOVING`. Fast-moving city rents and disposable incomes require more frequent updates than annual national statistics.

## 9. Country mapping and territory policy

- Requires city/metro identifiers, tenure, bedrooms and household composition.

## 10. Scoring options and sensitivity risks

- Mode/grade: `LOWER_BETTER` / `S3`
- Proposed method: Profile-specific housing-cost share; national price-to-income only as context.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C17, C21. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Fast-moving city rents and disposable incomes require more frequent updates than annual national statistics.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, COV_REGIONALLY_BIASED, GRA_CITY_LEVEL_REQUIRED, GRA_HOUSEHOLD_SCENARIO_REQUIRED
- Caveats: CMP_DEFINITION_DIFFERS, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Defer to the city and profile layers. National OECD ratios are useful validation data, not the independent criterion.

## 15. Open questions

- City universe, rental unit specification and household scenarios.

## Evidence register

- **VERIFIED:** OECD HC1.2 is an exact housing-cost-over-income table, but its documentation says total housing costs are available only for European countries and New Zealand. [Evidence](https://webfs.oecd.org/Els-com/Affordable_Housing_Database/HC1-2-Housing-costs-over-income.pdf)
- **VERIFIED:** The Affordable Housing Database is explicitly OECD/EU/key-partner focused. [Evidence](https://www.oecd.org/en/data/datasets/oecd-affordable-housing-database.html)

---

# C50 — Healthcare system capacity and quality

## Decision summary

- Status: `DEFERRED`
- Recommendation: Defer now. The reusable World Bank representation is complete but remains at 2021; the fresh 2023 WHO release has unresolved commercial reuse for direct ingestion.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `FRS_STALE`
- Caveat codes: `SEM_QUESTION_TOO_BROAD`, `CMP_IMPUTED_VALUES_REQUIRED`, `LIC_NONCOMMERCIAL_ONLY`

## 1. Relocation question

How capable is the national health system of delivering broad essential care, acknowledging that migrant eligibility may differ?

## 2. Precise definition

UHC service coverage index as a national capacity/access proxy; it does not directly measure migrant entitlement, waiting times or care experience.

## 3. Classification and granularity

Tags: IC, DO. Natural granularity: **NATIONAL**. Observation type: National composite using reported and modelled tracer indicators.

## 4. User profiles and decision value

Profiles: all movers, families, people with chronic conditions. Decision value: 5/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. World Bank (distribution) / WHO (upstream) — Health Nutrition and Population Statistics

- Exact series/table: SH.UHC.SRVS.CV.XD
- Version: World Bank source 16; latest 2021
- Access: [source](https://api.worldbank.org/v2/country/all/indicator/SH.UHC.SRVS.CV.XD?source=16&format=json)
- Methodology: [methodology](https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SH.UHC.SRVS.CV.XD)
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

### 2. World Health Organization / World Bank — Tracking UHC 2025 full dataset

- Exact series/table: UHC service coverage index, 2023
- Version: 2025 release; 2023 reference
- Access: [source](https://www.who.int/data/uhc-2025-technical-appendices-and-regional-data-tables)
- Methodology: [methodology](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/uhc-index-of-service-coverage)
- Licence evidence: [reuse terms](https://www.who.int/about/policies/publishing/copyright)
- Grades: authority A4; licence L1; comparability C4; mapping M3
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- The index is a geometric mean of 14 tracers; not every tracer directly measures service coverage.
- National population coverage does not establish migrant entitlement or local access.

## 7. Expected or measured 91-country coverage

**MEASURED:** 91/91 found; 0/91 fresh under the stated criterion rule; 0 missing.

## 8. Freshness assessment

Class: `SLOW_STRUCTURAL`. Monitor for the 2023 WHO revision to enter a production-compatible World Bank distribution and for methodology breaks.

## 9. Country mapping and territory policy

- World Bank representation maps cleanly to ISO3.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S4`
- Proposed method: Use the published 0–100 index directly after freshness and licence gates.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C56. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Monitor for the 2023 WHO revision to enter a production-compatible World Bank distribution and for methodology breaks.

## 13. Blockers, caveats and reason codes

- Blockers: FRS_STALE
- Caveats: SEM_QUESTION_TOO_BROAD, CMP_IMPUTED_VALUES_REQUIRED, LIC_NONCOMMERCIAL_ONLY

## 14. Recommendation

Defer now. The reusable World Bank representation is complete but remains at 2021; the fresh 2023 WHO release has unresolved commercial reuse for direct ingestion.

## 15. Open questions

- When will the World Bank CC BY representation refresh to the revised 2023 series?

## Evidence register

- **MEASURED:** The current World Bank HNP API returned 91/91 stable countries, all with latest year 2021. [Evidence](https://api.worldbank.org/v2/country/all/indicator/SH.UHC.SRVS.CV.XD?source=16&format=json)
- **VERIFIED:** The 2025 global monitoring release reports the UHC service coverage index through 2023. [Evidence](https://www.worldbank.org/en/topic/universalhealthcoverage/publication/2025-global-monitoring-report-gmr)
- **VERIFIED:** WHO requires permission for commercial use of WHO materials absent a more specific licence. [Evidence](https://www.who.int/about/policies/publishing/copyright)

---

# C40 — English usability

## Decision summary

- Status: `DEFERRED_CITY_LAYER`
- Recommendation: Defer to a city/preference layer. Do not use EF EPI as a production country criterion.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `LIC_NO_EVIDENCE`, `CMP_SURVEY_NOT_HARMONISED`, `GRA_CITY_LEVEL_REQUIRED`, `SCO_SAMPLE_RELATIVE_DISTORTION`
- Caveat codes: `COV_MISSING_KEY_DESTINATIONS`, `SEM_QUESTION_TOO_BROAD`

## 1. Relocation question

How easily can an English-speaking newcomer handle work, services and daily life in the specific destination?

## 2. Precise definition

A local usability concept combining institutional language availability and population proficiency; national adult test scores are only a weak proxy.

## 3. Classification and granularity

Tags: IC, CR. Natural granularity: **CITY_OR_REGIONAL**. Observation type: Self-selected online assessment; city/regional cuts.

## 4. User profiles and decision value

Profiles: English-speaking movers. Decision value: 4/5. Profile dependence: HIGH.

## 5. Source candidates

### 1. EF Education First — EF English Proficiency Index 2025

- Exact series/table: Country, region and city scores
- Version: 2025
- Access: [source](https://www.ef.com/wwen/epi/)
- Methodology: [methodology](https://www.ef.com/wwen/epi/about-epi/)
- Licence evidence: No dataset-specific evidence verified
- Grades: authority A2; licence L1; comparability C2; mapping M2
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- EF test takers are self-selected, young-skewed and internet-only.
- Adult proficiency is not the same as service or workplace usability; native-English destinations are not symmetrically observed.

## 7. Expected or measured 91-country coverage

**ESTIMATED:** MEDIUM; no source query/download was used to count stable countries.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. Annual edition changes and city sample thresholds create unstable coverage.

## 9. Country mapping and territory policy

- EF includes countries/regions and thresholded cities; stable-country and native-language exceptions require policy.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S2`
- Proposed method: No independent score until native-English destinations and institutional usability have equivalent measures.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C32. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Annual edition changes and city sample thresholds create unstable coverage.

## 13. Blockers, caveats and reason codes

- Blockers: LIC_NO_EVIDENCE, CMP_SURVEY_NOT_HARMONISED, GRA_CITY_LEVEL_REQUIRED, SCO_SAMPLE_RELATIVE_DISTORTION
- Caveats: COV_MISSING_KEY_DESTINATIONS, SEM_QUESTION_TOO_BROAD

## 14. Recommendation

Defer to a city/preference layer. Do not use EF EPI as a production country criterion.

## 15. Open questions

- Whether English usability should be a user preference/filter rather than a ranked criterion.

## Evidence register

- **VERIFIED:** EF EPI 2025 uses more than 2.2 million 2024 test takers, but the sample is self-selected and not guaranteed representative. [Evidence](https://www.ef.com/wwen/epi/about-epi/)
- **VERIFIED:** EF states that its raw source data are not prepared for sharing outside the organisation. [Evidence](https://www.ef.com/wwen/epi/about-epi/)

---

# C01 — Overall higher-education opportunity

## Decision summary

- Status: `EXPERIMENTAL_CANDIDATE`
- Recommendation: Experimental/recovery probe only. Overall coverage is 88/91, but only 77/91 have 2023+ data and 81/91 have 2021+ data.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`
- Caveat codes: `SEM_QUESTION_TOO_BROAD`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

How broad is access to tertiary education in the destination, before institution, field, tuition and international-student constraints?

## 2. Precise definition

Gross tertiary enrolment ratio as a national participation proxy; it is not a university-quality or migrant-access measure.

## 3. Classification and granularity

Tags: IC. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National administrative education statistics.

## 4. User profiles and decision value

Profiles: students, families with older children. Decision value: 4/5. Profile dependence: HIGH.

## 5. Source candidates

### 1. World Bank (distribution) / UNESCO UIS (upstream) — World Development Indicators

- Exact series/table: SE.TER.ENRR
- Version: UIS Feb. 2026 release
- Access: [source](https://api.worldbank.org/v2/country/all/indicator/SE.TER.ENRR?format=json)
- Methodology: [methodology](https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SE.TER.ENRR)
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Gross enrolment can exceed 100 and reflects system participation, not teaching quality, places for foreigners, tuition or field availability.

## 7. Expected or measured 91-country coverage

**MEASURED:** 88/91 found; 77/91 fresh under the stated criterion rule; 3 missing.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. Annual UIS/WDI release; pin extraction date and latest-observation rule.

## 9. Country mapping and territory policy

- ISO3 mapping is clean; small states have sparse updates.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S2`
- Proposed method: Robust percentile only as tertiary participation; do not label it quality or international-student opportunity.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C08. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Annual UIS/WDI release; pin extraction date and latest-observation rule.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT
- Caveats: SEM_QUESTION_TOO_BROAD, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Experimental/recovery probe only. Overall coverage is 88/91, but only 77/91 have 2023+ data and 81/91 have 2021+ data.

## 15. Open questions

- Can a second UIS participation/completion series recover at least 82 fresh countries without changing semantics?

## Evidence register

- **MEASURED:** The WDI API returned 88/91 with any 2010–2025 value, 81/91 at 2021+, and 77/91 at 2023+. [Evidence](https://api.worldbank.org/v2/country/all/indicator/SE.TER.ENRR?format=json)
- **VERIFIED:** WDI metadata identifies UIS as upstream, annual periodicity and CC BY 4.0. [Evidence](https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SE.TER.ENRR)

---

# C30 — Existing immigrant share

## Decision summary

- Status: `PROBE_APPROVED`
- Recommendation: Proceed to deterministic Phase 3E probe; measured current coverage is 91/91.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: none
- Caveat codes: `CMP_IMPUTED_VALUES_REQUIRED`, `CMP_DEFINITION_DIFFERS`, `SEM_CAUSALITY_OVERCLAIM`

## 1. Relocation question

How established is international migration in the destination, as indicated by the foreign-born share of residents?

## 2. Precise definition

International migrant stock as a percentage of total population, using UN Population Division estimates distributed by WDI.

## 3. Classification and granularity

Tags: IC. Natural granularity: **NATIONAL**. Observation type: National stock estimate from censuses, registers, surveys and imputation.

## 4. User profiles and decision value

Profiles: all international movers. Decision value: 4/5. Profile dependence: NONE.

## 5. Source candidates

### 1. World Bank (distribution) / UN Population Division (upstream) — World Development Indicators

- Exact series/table: SM.POP.TOTL.ZS
- Version: 2024
- Access: [source](https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL.ZS?format=json)
- Methodology: [methodology](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SM.POP.TOTL)
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Foreign-born is used where possible; citizenship is substituted in some countries and missing countries are imputed.
- Stock reflects history and geography, not current visa openness or lived inclusion.

## 7. Expected or measured 91-country coverage

**MEASURED:** 91/91 found; 91/91 fresh under the stated criterion rule; 0 missing.

## 8. Freshness assessment

Class: `SLOW_STRUCTURAL`. Slow-moving; pin UN revision and WDI release.

## 9. Country mapping and territory policy

- WDI ISO3 mapping is deterministic; country breakups create historical discontinuities.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S3`
- Proposed method: Logit-transform percentage, winsorise, then robust percentile; keep interpretation as established migrant presence, not friendliness.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C32, C33. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Slow-moving; pin UN revision and WDI release.

## 13. Blockers, caveats and reason codes

- Blockers: none
- Caveats: CMP_IMPUTED_VALUES_REQUIRED, CMP_DEFINITION_DIFFERS, SEM_CAUSALITY_OVERCLAIM

## 14. Recommendation

Proceed to deterministic Phase 3E probe; measured current coverage is 91/91.

## 15. Open questions

- Whether scoring should be higher-better or informational/preference based.

## Evidence register

- **MEASURED:** The WDI API returned 2024 observations for all 91 stable countries. [Evidence](https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL.ZS?format=json)
- **VERIFIED:** WDI metadata identifies UN Population Division as publisher, describes census/register/survey inputs and imputation, and assigns CC BY 4.0. [Evidence](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SM.POP.TOTL)

---

# C12 — Software and technology jobs

## Decision summary

- Status: `DEFERRED_CITY_LAYER`
- Recommendation: Defer to a city/occupation layer. Recent two-digit occupation data cover only 66/91 and remain semantically too broad.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `GRA_CITY_LEVEL_REQUIRED`, `GRA_PROFESSION_SPECIFIC`
- Caveat codes: `CMP_DEFINITION_DIFFERS`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

How large and accessible is the software/technology employment market in the relevant city for the user's occupation?

## 2. Precise definition

Employment in selected ISCO-08 two-digit ICT-related occupations as a national proxy; vacancies and city concentration remain unmeasured.

## 3. Classification and granularity

Tags: IC, SC, CR. Natural granularity: **CITY_OR_REGIONAL**. Observation type: National labour-force survey occupation counts.

## 4. User profiles and decision value

Profiles: software professionals, ICT technicians. Decision value: 5/5. Profile dependence: HIGH.

## 5. Source candidates

### 1. International Labour Organization (ILOSTAT) — ILOSTAT bulk download

- Exact series/table: EMP_TEMP_SEX_OC2_NB_A; ISCO-08 level 2
- Version: accessed 2026-07-24
- Access: [source](https://rplumber.ilo.org/data/indicator/)
- Methodology: [methodology](https://ilostat.ilo.org/about/get-started/)
- Licence evidence: [reuse terms](https://www.ilo.org/rights-and-permissions)
- Grades: authority A4; licence L4; comparability C3; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Two-digit occupation groups are broader than software jobs and miss tech-industry roles outside selected occupations.
- National employment stocks do not measure vacancies, hiring friction or city clusters.

## 7. Expected or measured 91-country coverage

**MEASURED:** 66/91 found; 66/91 fresh under the stated criterion rule; 25 missing.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. ISCO revisions, survey breaks and city labour-market sourcing would be substantial.

## 9. Country mapping and territory policy

- ISO3 is deterministic; ISCO version and occupation-code mapping require version controls.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S2`
- Proposed method: Selected ICT occupation employment divided by total employment; experimental only after occupation-code review.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C11, C17. No additional coded risk.

## 12. Retrieval, replay and maintenance

- ISCO revisions, survey breaks and city labour-market sourcing would be substantial.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, GRA_CITY_LEVEL_REQUIRED, GRA_PROFESSION_SPECIFIC
- Caveats: CMP_DEFINITION_DIFFERS, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Defer to a city/occupation layer. Recent two-digit occupation data cover only 66/91 and remain semantically too broad.

## 15. Open questions

- Whether to define tech by occupation, industry, vacancies, or a hybrid.

## Evidence register

- **MEASURED:** EMP_TEMP_SEX_OC2_NB_A had 2023+ observations for 66/91 stable countries. [Evidence](https://rplumber.ilo.org/data/indicator/)
- **VERIFIED:** ILOSTAT exposes occupation data only up to ISCO two-digit level in the relevant public table family. [Evidence](https://ilostat.ilo.org/about/get-started/)

---

# C58 — Internet access, speed, and reliability

## Decision summary

- Status: `EXPERIMENTAL_CANDIDATE`
- Recommendation: Experimental/redundancy probe only for a narrowed access-and-penetration criterion. Do not claim speed or reliability.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: none
- Caveat codes: `SEM_QUESTION_TOO_BROAD`, `RED_EXISTING_CRITERION`, `RED_SHARED_COMPONENTS`, `LIC_NONCOMMERCIAL_ONLY`

## 1. Relocation question

Can a newcomer expect affordable, fast and dependable connectivity where they live and work?

## 2. Precise definition

Current reusable sources support national internet use and fixed-broadband penetration, not a complete speed/reliability measure.

## 3. Classification and granularity

Tags: IC, SC, DO. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National household/administrative indicators; composite proxy.

## 4. User profiles and decision value

Profiles: remote workers, students, all households. Decision value: 5/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. World Bank (distribution) / ITU (upstream) — World Development Indicators

- Exact series/table: IT.NET.USER.ZS; IT.NET.BBND.P2
- Version: WDI 2026-07-13 snapshot
- Access: [source](https://api.worldbank.org/v2/country/all/indicator/IT.NET.USER.ZS?format=json)
- Methodology: [methodology](https://beta.datahub.itu.int/about/)
- Licence evidence: [reuse terms](https://data.worldbank.org/summary-terms-of-use)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

### 2. International Telecommunication Union — ITU DataHub

- Exact series/table: Internet, broadband and quality-of-service indicators
- Version: regular updates
- Access: [source](https://datahub.itu.int/)
- Methodology: [methodology](https://beta.datahub.itu.int/about/)
- Licence evidence: [reuse terms](https://beta.datahub.itu.int/about/)
- Grades: authority A4; licence L1; comparability C4; mapping M3
- Evidence level: **VERIFIED**

## 6. Comparability assessment

- Internet use and fixed-broadband subscriptions are comparable but are not throughput, latency, outages or affordability.

## 7. Expected or measured 91-country coverage

**MEASURED:** 91/91 found; 91/91 fresh under the stated criterion rule; 0 missing.

## 8. Freshness assessment

Class: `FAST_MOVING`. Annual WDI refresh is manageable; a true speed/reliability source would require faster updates and city/geospatial policy.

## 9. Country mapping and territory policy

- WDI ISO3 mapping is already validated in the repository.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S3`
- Proposed method: Experimental access/penetration composite only; do not label it speed and reliability.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C56. RED_EXISTING_CRITERION; RED_SHARED_COMPONENTS

## 12. Retrieval, replay and maintenance

- Annual WDI refresh is manageable; a true speed/reliability source would require faster updates and city/geospatial policy.

## 13. Blockers, caveats and reason codes

- Blockers: none
- Caveats: SEM_QUESTION_TOO_BROAD, RED_EXISTING_CRITERION, RED_SHARED_COMPONENTS, LIC_NONCOMMERCIAL_ONLY

## 14. Recommendation

Experimental/redundancy probe only for a narrowed access-and-penetration criterion. Do not claim speed or reliability.

## 15. Open questions

- Whether this adds value beyond the existing infrastructure experiment and whether speed should be city-level.

## Evidence register

- **MEASURED:** The repository's existing source audit measured both WDI components at 91/91; latest internet-use observations were 2024–25 and fixed broadband 2023–24. [Evidence](../docs/data/source-audit.md)
- **VERIFIED:** ITU DataHub describes about 200 economies and direct data under CC BY-NC-SA 3.0 IGO. [Evidence](https://beta.datahub.itu.int/about/)

---

# C56 — Electricity access and reliability

## Decision summary

- Status: `DEFERRED`
- Recommendation: Defer. Access measured 91/91 for 2024, but the WDI API returned no observations for IC.ELC.OUTG; access alone does not answer reliability.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_BELOW_90_PERCENT`, `SEM_QUESTION_TOO_BROAD`
- Caveat codes: `CMP_SURVEY_NOT_HARMONISED`, `FRS_MIXED_REFERENCE_PERIODS`, `RED_SHARED_COMPONENTS`

## 1. Relocation question

Can a household and workplace expect continuous electricity service, not merely a grid connection?

## 2. Precise definition

Electricity-access percentage plus an outage/reliability outcome; only access currently meets global coverage.

## 3. Classification and granularity

Tags: IC, SC, DO. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National access estimate plus firm-survey outage data.

## 4. User profiles and decision value

Profiles: remote workers, business owners, all households. Decision value: 5/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. World Bank / WHO-UNICEF tracking partners — World Development Indicators

- Exact series/table: EG.ELC.ACCS.ZS
- Version: 2024
- Access: [source](https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json)
- Methodology: [methodology](https://databank.worldbank.org/metadataglossary/jobs/series/EG.ELC.ACCS.ZS)
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

### 2. World Bank Enterprise Surveys — Enterprise Surveys / WDI metadata

- Exact series/table: IC.ELC.OUTG
- Version: Not pinned
- Access: [source](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IC.ELC.OUTG)
- Methodology: Not independently located
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C2; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Access is near-ceiling in much of the stable universe and is not reliability.
- Enterprise Survey outages reflect sampled firms, subnational survey locations and heterogeneous survey years.

## 7. Expected or measured 91-country coverage

**MEASURED:** 0/91 found; 0/91 fresh under the stated criterion rule; 91 missing.

## 8. Freshness assessment

Class: `STANDARD_SOCIOECONOMIC`. Reliability requires survey-year and coverage controls; access alone adds little differentiation.

## 9. Country mapping and territory policy

- ISO3 is straightforward; subnational survey strata do not map to a national lived-experience claim.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S2`
- Proposed method: Access higher-better and outages lower-better; no combined score until reliability clears coverage.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C58. RED_SHARED_COMPONENTS

## 12. Retrieval, replay and maintenance

- Reliability requires survey-year and coverage controls; access alone adds little differentiation.

## 13. Blockers, caveats and reason codes

- Blockers: COV_BELOW_90_PERCENT, SEM_QUESTION_TOO_BROAD
- Caveats: CMP_SURVEY_NOT_HARMONISED, FRS_MIXED_REFERENCE_PERIODS, RED_SHARED_COMPONENTS

## 14. Recommendation

Defer. Access measured 91/91 for 2024, but the WDI API returned no observations for IC.ELC.OUTG; access alone does not answer reliability.

## 15. Open questions

- A global reusable SAIDI/SAIFI or household-outage source with 82+ stable-country coverage.

## Evidence register

- **MEASURED:** EG.ELC.ACCS.ZS returned 2024 observations for all 91 stable countries. [Evidence](https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json)
- **MEASURED:** The current WDI API query for IC.ELC.OUTG returned zero stable-country observations. [Evidence](https://api.worldbank.org/v2/country/all/indicator/IC.ELC.OUTG?format=json)

---

# C08 — School education quality

## Decision summary

- Status: `PROBE_APPROVED`
- Recommendation: Proceed to deterministic Phase 3E probe; measured field coverage is 89/91 and the source is current, official and reusable.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: `COV_NOT_FULL_91`
- Caveat codes: `CMP_MODEL_ASSUMPTIONS_OPAQUE`, `FRS_MIXED_REFERENCE_PERIODS`

## 1. Relocation question

How much effective learning does the national school system produce for a child, before local school choice?

## 2. Precise definition

HCI+ harmonized learning outcomes and learning-adjusted years of schooling, used as national outcome measures.

## 3. Classification and granularity

Tags: IC. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National composite/modelled harmonisation of assessments and schooling.

## 4. User profiles and decision value

Profiles: families with children. Decision value: 5/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. World Bank — Human Capital Index Plus

- Exact series/table: hlo_mf; lays_mf; hcip_schooling_component_mf in hci_plus_index_panel.dta
- Version: version 3; file updated 2026-02-11
- Access: [source](https://datacatalog.worldbank.org/search/dataset/0067030/human-capital-index-plus)
- Methodology: [methodology](https://humancapital.worldbank.org/hciplus/methodology/)
- Licence evidence: [reuse terms](https://datacatalog.worldbank.org/int/public-licenses#cc-by)
- Grades: authority A4; licence L4; comparability C4; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- Harmonized learning outcomes bridge different assessments through a common scale and modelling.
- National averages mask region, school sector, language and migrant-child access.

## 7. Expected or measured 91-country coverage

**MEASURED:** 89/91 found; 88/91 fresh under the stated criterion rule; 2 missing.

## 8. Freshness assessment

Class: `SLOW_STRUCTURAL`. Pin HCI+ version and clarify whether file year 2025 is an estimate; catalogue temporal metadata says 2009–2024 while the file contains 2025 labels.

## 9. Country mapping and territory policy

- ISO3 mapping was deterministic; BHS and BOL lacked the tested schooling/learning fields.

## 10. Scoring options and sensitivity risks

- Mode/grade: `HIGHER_BETTER` / `S4`
- Proposed method: Prefer the published schooling component or learning-adjusted years; test sensitivity against HLO alone.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: C01. No additional coded risk.

## 12. Retrieval, replay and maintenance

- Pin HCI+ version and clarify whether file year 2025 is an estimate; catalogue temporal metadata says 2009–2024 while the file contains 2025 labels.

## 13. Blockers, caveats and reason codes

- Blockers: COV_NOT_FULL_91
- Caveats: CMP_MODEL_ASSUMPTIONS_OPAQUE, FRS_MIXED_REFERENCE_PERIODS

## 14. Recommendation

Proceed to deterministic Phase 3E probe; measured field coverage is 89/91 and the source is current, official and reusable.

## 15. Open questions

- Use the schooling component, LAYS, or HLO as the primary score?
- Resolve the catalogue/file year-label discrepancy.

## Evidence register

- **MEASURED:** The downloaded HCI+ panel contained 89/91 stable countries for HLO/LAYS; BHS and BOL were missing. Eighty-eight had latest labels at 2024+ for HLO/LAYS. [Evidence](https://datacatalogfiles.worldbank.org/ddh-published/0067030/DR0095876/hci_plus_index_panel.dta)
- **VERIFIED:** The catalogue states 166-country coverage, national granularity, file update 11 February 2026 and CC BY 4.0. [Evidence](https://datacatalog.worldbank.org/search/dataset/0067030/human-capital-index-plus)

---

# C66 — Extreme-weather risk

## Decision summary

- Status: `EXPERIMENTAL_CANDIDATE`
- Recommendation: Experimental Phase 3E probe only. Coverage is complete, but a Konsider-specific weather subset and weighting need defensibility testing.
- Evidence cutoff: 2026-07-24
- Primary blocker codes: none
- Caveat codes: `SCO_COMPOSITE_WEIGHTS_ARBITRARY`, `LIC_SOURCE_CHAIN_UNCLEAR`, `SEM_QUESTION_TOO_BROAD`

## 1. Relocation question

How exposed is the destination to severe weather-related hazards that could disrupt life, property and services?

## 2. Precise definition

A transparent subset of INFORM 2026 hazard scores: river flood, tropical cyclone, coastal flood and drought; earthquakes, tsunamis, epidemics and conflict are excluded.

## 3. Classification and granularity

Tags: IC, SC, DO. Natural granularity: **NATIONAL_WITH_CITY_CAVEAT**. Observation type: National multi-source hazard/exposure composite.

## 4. User profiles and decision value

Profiles: all movers, home buyers, climate-sensitive households. Decision value: 4/5. Profile dependence: MODERATE.

## 5. Source candidates

### 1. European Commission JRC / INFORM partners — INFORM Risk Index 2026

- Exact series/table: INFORM_Risk_2026_v072.xlsx: River Flood, Tropical Cyclone, Coastal flood, Drought
- Version: INFORM Risk 2026 v072
- Access: [source](https://drmkc.jrc.ec.europa.eu/inform-index/Portals/0/InfoRM/2026/INFORM_Risk_2026_v072.xlsx)
- Methodology: [methodology](https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology)
- Licence evidence: [reuse terms](https://commission.europa.eu/legal-notice_en)
- Grades: authority A4; licence L3; comparability C4; mapping M3
- Evidence level: **MEASURED**

## 6. Comparability assessment

- The official Natural score also includes geophysical and epidemic hazards, so it is semantically too broad.
- The selected subset omits heatwaves, wildfire, severe convective storms and local adaptation.

## 7. Expected or measured 91-country coverage

**MEASURED:** 91/91 found; 91/91 fresh under the stated criterion rule; 0 missing.

## 8. Freshness assessment

Class: `EVENT_RISK_MODEL`. Pin workbook version and component names; monitor annual methodology changes.

## 9. Country mapping and territory policy

- All 91 stable ISO3 codes mapped and had values in each selected field.

## 10. Scoring options and sensitivity risks

- Mode/grade: `LOWER_BETTER` / `S2`
- Proposed method: Experimental maximum or weighted mean of the four published 0–10 hazards; publish sensitivity and avoid calling it the official INFORM Natural score.
- Sensitivity required: yes

## 11. Redundancy and composite risks

Links: none identified. SCO_COMPOSITE_WEIGHTS_ARBITRARY

## 12. Retrieval, replay and maintenance

- Pin workbook version and component names; monitor annual methodology changes.

## 13. Blockers, caveats and reason codes

- Blockers: none
- Caveats: SCO_COMPOSITE_WEIGHTS_ARBITRARY, LIC_SOURCE_CHAIN_UNCLEAR, SEM_QUESTION_TOO_BROAD

## 14. Recommendation

Experimental Phase 3E probe only. Coverage is complete, but a Konsider-specific weather subset and weighting need defensibility testing.

## 15. Open questions

- Maximum versus mean aggregation
- Whether heatwave and wildfire omissions are acceptable
- Confirm workbook-level reuse and upstream source chain.

## Evidence register

- **MEASURED:** The downloaded INFORM Risk 2026 v072 workbook mapped all 91 stable ISO3 codes and had non-null River Flood, Tropical Cyclone, Coastal flood and Drought scores for every country. [Evidence](https://drmkc.jrc.ec.europa.eu/inform-index/Portals/0/InfoRM/2026/INFORM_Risk_2026_v072.xlsx)
- **VERIFIED:** INFORM describes the index as global and open and publishes the workbook with source data and calculation steps. [Evidence](https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Results-and-data/moduleId/1782/id/453/controller/Admin/a)
- **VERIFIED:** EC-owned website content is CC BY 4.0 unless otherwise indicated, with third-party-rights caveats. [Evidence](https://commission.europa.eu/legal-notice_en)
