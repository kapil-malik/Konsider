# Konsider Phase 3C — Batch 2 source-feasibility research

Evidence cutoff: **2026-07-26**
Universe: **stable_supported_v1 (91 countries)**

## Evidence boundary

Publisher scope, methodology, version, and licensing statements labelled VERIFIED were checked against the linked source pages. Exact World Bank API responses were captured and joined for C16, C29, C48 and C49; those results are labelled MEASURED. All other stable-91 coverage statements are ESTIMATES.

## Executive conclusion

Proceed to deterministic Phase 3E probes for **C29, C48, C49**. Run conditional experimental probes for **C34, C05, C16, C26**. Defer **C38, C35, C36, C15, C13, C14, C22** to profile, occupation, city, or legal modules. Reject **C19** as a scored criterion under the identified source methodology.

## Comparison table

| Rank | ID | Criterion | Finding | Granularity | Stable-91 coverage | A/L/C/M | Phase 3E |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | C38 | Professional-licensing accessibility for immigrants | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated; not measured | A4/L4/C2/M2 | DEFER |
| 2 | C35 | Post-study migration pathway | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated; not measured | A4/L4/C3/M3 | DEFER |
| 3 | C36 | Family reunification support | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated; not measured | A4/L4/C3/M3 | DEFER |
| 4 | C34 | Citizenship accessibility | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_PROFILE_CAVEAT | FULL estimated; not measured | A4/L4/C4/M4 | EXPERIMENTAL_ONLY |
| 5 | C05 | Research and innovation ecosystem | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_CITY_CAVEAT | HIGH estimated; not measured | A4/L4/C3/M3 | EXPERIMENTAL_ONLY |
| 6 | C15 | Engineering and skilled technical jobs | DEFERRED_CITY_LAYER | CITY_OR_REGIONAL_PROFILE | MEDIUM estimated; not measured | A4/L4/C3/M3 | DEFER |
| 7 | C13 | Medical and healthcare jobs | DEFERRED_PROFILE_LAYER | CITY_OR_REGIONAL_PROFILE | MEDIUM estimated; not measured | A4/L4/C3/M3 | DEFER |
| 8 | C14 | Business, finance, and professional-services jobs | DEFERRED_CITY_LAYER | CITY_OR_REGIONAL_PROFILE | MEDIUM estimated; not measured | A4/L4/C3/M3 | DEFER |
| 9 | C16 | Entrepreneurship and startup opportunity | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_CITY_CAVEAT | 79/91 measured | A4/L4/C4/M3 | EXPERIMENTAL_ONLY |
| 10 | C19 | Employment protection and worker rights | REJECTED | NATIONAL | HIGH estimated; not measured | A4/L4/C1/M3 | REJECT |
| 11 | C22 | Social-security and mandatory contribution burden | DEFERRED_PROFILE_LAYER | PROFILE_ONLY | LOW estimated; not measured | A4/L4/C4/M3 | DEFER |
| 12 | C26 | Healthcare affordability | EXPERIMENTAL_CANDIDATE | NATIONAL_WITH_PROFILE_CAVEAT | FULL estimated; not measured | A4/L4/C4/M3 | EXPERIMENTAL_ONLY |
| 13 | C29 | Currency and macroeconomic stability | PROBE_APPROVED | NATIONAL | 91/91 measured | A4/L4/C4/M4 | PROCEED_DETERMINISTIC_PROBE |
| 14 | C48 | Political stability and civil peace | PROBE_APPROVED | NATIONAL | 91/91 measured | A4/L4/C4/M4 | PROCEED_DETERMINISTIC_PROBE |
| 15 | C49 | Rule of law and institutional trust | PROBE_APPROVED | NATIONAL | 91/91 measured | A4/L4/C4/M4 | PROCEED_DETERMINISTIC_PROBE |

## Phase 3E shortlist

1. **C29 — Currency and macroeconomic stability** (DETERMINISTIC): Proceed to a deterministic Phase 3E probe using pinned 2020-2024 observations and explicit currency-break handling.
2. **C48 — Political stability and civil peace** (DETERMINISTIC): Proceed to a deterministic Phase 3E probe on the 2025-revision aggregate and its uncertainty fields.
3. **C49 — Rule of law and institutional trust** (DETERMINISTIC): Proceed to a deterministic Phase 3E probe after narrowing the label to Rule of Law and checking overlap with the active catalog.
4. **C34 — Citizenship accessibility** (CONDITIONAL): Run an experimental Phase 3E probe on the exact v3 archive, stable-91 mapping and a deliberately narrow naturalisation-rule subset.
5. **C05 — Research and innovation ecosystem** (CONDITIONAL): Run a conditional Phase 3E probe to measure stable-91 coverage, capture the exact data licence and compare overall/output-only variants.
6. **C26 — Healthcare affordability** (CONDITIONAL): Run a conditional Phase 3E probe for stable-91 recency and licensing capture; keep the criterion explicitly labelled financial-protection proxy.
7. **C16 — Entrepreneurship and startup opportunity** (CONDITIONAL): Run only a conditional Phase 3E recovery probe. The measured 79/91 result misses the 82-country threshold before partial-geography exclusions.

## Recurring publisher and dataset families

- **World Bank WDI/API** — C05, C16, C29, C49. Reusable JSON API, WDI metadata, and CC BY 4.0 indicator pages.
- **World Bank Worldwide Governance Indicators** — C48, C49. One 2025-revision dataset; share one adapter and uncertainty treatment.
- **ILOSTAT occupation and rights systems** — C15, C13, C14, C19. Strong classifications, but sector opportunity coverage/granularity and explicit 8.8.2 usage limits constrain scoring.
- **OECD migration and tax-benefit publications** — C35, C36, C22. High-quality comparative evidence but regionally limited and often scenario-specific.
- **WHO health workforce and expenditure** — C38, C13, C26. Useful official context; only GHED currently looks suitable for a national proxy probe.
- **EC and national legal portals** — C38, C35, C36. Current-policy discovery, not a global harmonised dataset.

## Open decisions

- Whether C34 may use a narrow legal inclusiveness score or should remain informational.
- Whether C05 should use overall GII, Innovation Output, or a research-only subset.
- Whether C16 should exclude or flag partial-geography and offshore registration observations.
- Whether C26 is acceptable when explicitly labelled as a financial-protection proxy rather than migrant healthcare cost.
- How C29 should treat currency unions, fixed pegs, redenominations and user income currency.
- Whether C49 should be renamed Rule of law and how it overlaps the current active catalog.
- Which professions, cities, origins and households define future profile-layer pilots for C38, C35, C36, C15, C13, C14 and C22.

# C38 — Professional-licensing accessibility for immigrants

**Relocation question.** For a named regulated profession and a person's origin qualification, how difficult is recognition and licensing in the destination?

**Operational definition.** A profile-derived recognition pathway covering regulator, qualification equivalence, exams, language, supervised practice, cost and expected time.

**Finding.** DEFERRED_PROFILE_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** PROFILE_ONLY; Profession- and origin-specific administrative/legal rules. Freshness class: CURRENT_POLICY.

## Source candidates

- **C38-WHO-NRI — World Health Organization, National Reporting Instrument reports database.** WHO Global Code health-personnel migration reporting. Version: Reports and consolidated evidence current through the latest NRI cycle. Grades: A4/L4/C2/M2. [Access](https://www.who.int/teams/health-workforce/migration/practice/reports-database) · [Methodology](https://www.who.int/publications/i/item/9789240066649) · [Licence](https://data.who.int/about/data/terms-and-conditions)
- **C38-ENIC-NARIC — European Commission / Council of Europe / UNESCO, ENIC-NARIC networks.** Country recognition authorities and regulated-profession guidance. Version: Current country pages. Grades: A4/L3/C2/M2. [Access](https://www.enic-naric.net/) · [Methodology](https://www.enic-naric.net/page-about-ENIC-NARIC-Networks) · [Licence](https://commission.europa.eu/legal-notice_en)

## Coverage and freshness

- **ESTIMATED, not measured:** LOW. Below 82 for the exact construct.
- **VERIFIED publisher scope:** WHO reporting covers 134 countries, but not a comparable licensing score.
- No global dataset codes current recognition requirements across professions and qualification origins.

## Methodology and comparability

- WHO NRI provides a common reporting framework for health-worker mobility, not applicant-level licensing outcomes.
- Recognition depends on profession, regulator, qualification country, curriculum, language and supervised-practice requirements.

## Licensing and reuse

- WHO dataset terms are generally CC BY 4.0 with additional terms; linked national regulator material needs page-specific review.
- ENIC-NARIC is a discovery network, not one reusable harmonised dataset.

## Country and entity mapping

- Country ISO mapping is secondary to profession, regulator and qualification-origin mapping.
- Federal and devolved systems may have multiple competent authorities.

## Scoring feasibility

- Direction: **PROFILE_DERIVED**; grade: **S1**.
- Return pathway steps and eligibility flags; do not calculate a destination-only score.

## Overlap, limitations, and blockers

- Overlap: C13, C15, C32.
- No global comparable processing-time, exam, fee or success-rate series.
- Health-profession evidence cannot be generalized to engineering, law, teaching or trades.
- Reason codes: GRA_PROFESSION_SPECIFIC; GRA_ORIGIN_SPECIFIC; PRF_PROFILE_ONLY; SRC_NO_AUTHORITATIVE_GLOBAL_SCORE; OPS_EXCESSIVE_MANUAL_MAINTENANCE.

## Recommendation

Defer to a later profile/legal pathway module. A Phase 3E national criterion probe would test the wrong unit of analysis.

## Evidence ledger

- **VERIFIED:** WHO describes its NRI as a common platform for comparable reporting on implementation of the Global Code. — [source](https://www.who.int/teams/health-workforce/migration/practice/reports-database)
- **VERIFIED:** WHO's consolidated health-worker mobility report combines mechanisms and covers 134 countries. — [source](https://www.who.int/publications/i/item/9789240066649)
- **ESTIMATED:** No current authoritative global profession-by-origin licensing dataset was verified. — Phase 3C Batch 2 source search

## Open questions

- Which two or three regulated professions and origin qualifications should define a future pilot?

# C35 — Post-study migration pathway

**Relocation question.** Given nationality, credential, institution and graduation date, can an international graduate remain, work and transition to longer-term status?

**Operational definition.** A dated, profile-specific rule assessment for post-study work permission, duration, employer conditions and transition routes.

**Finding.** DEFERRED_PROFILE_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** PROFILE_ONLY; Administrative/legal policy. Freshness class: CURRENT_POLICY.

## Source candidates

- **C35-OECD-IMO-2025 — OECD, International Migration Outlook 2025.** Recent post-study and migration-policy changes. Version: 2025. Grades: A4/L4/C3/M3. [Access](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en.html) · [Methodology](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html) · [Licence](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)
- **C35-EU-PORTAL — European Commission, EU Immigration Portal.** Student and highly-qualified worker country pages. Version: Pages current in 2025; 25 EU countries. Grades: A4/L4/C2/M3. [Access](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en) · [Methodology](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en) · [Licence](https://commission.europa.eu/legal-notice_en)

## Coverage and freshness

- **ESTIMATED, not measured:** LOW. Well below 82 for a maintained exact ruleset.
- **VERIFIED publisher scope:** OECD members and 25 EU countries have structured comparative discovery material.
- Outside OECD/EU, national immigration portals must be coded individually.

## Methodology and comparability

- OECD provides current comparative policy narrative but not a global applicant-level eligibility table.
- Rules vary by qualification level, course length, institution recognition, nationality and later job conditions.

## Licensing and reuse

- OECD post-July-2024 content is generally CC BY 4.0 subject to page exceptions.
- Commission-owned portal content is generally CC BY 4.0 under the EC legal notice.

## Country and entity mapping

- Requires credential level, institution status, completion date and nationality in addition to destination.
- Policy-effective dates and transition provisions must be preserved.

## Scoring feasibility

- Direction: **PROFILE_DERIVED**; grade: **S1**.
- Eligibility and route timeline, not a universal higher-better national percentile.

## Overlap, limitations, and blockers

- Overlap: C01, C06, C32, C33.
- Published policy changes can precede implementation guidance.
- A long nominal permit may still impose job, salary or sponsorship constraints.
- Reason codes: COV_BELOW_90_PERCENT; GRA_ORIGIN_SPECIFIC; PRF_PROFILE_ONLY; OPS_EXCESSIVE_MANUAL_MAINTENANCE.

## Recommendation

Defer to the legal/profile layer; retain OECD and the EU portal as discovery and cross-check sources.

## Evidence ledger

- **VERIFIED:** OECD 2024/2025 migration outlooks describe frequent changes to post-study work and transition policies. — [source](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html)
- **VERIFIED:** The EU Immigration Portal's structured category information applies to 25 EU countries. — [source](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en)

## Open questions

- Which student nationalities, credential levels and graduation scenarios should a future module support?

# C36 — Family reunification support

**Relocation question.** For a sponsor's status and a named family relationship, can the family member join, work and remain in the destination?

**Operational definition.** A route-specific legal assessment of eligible relatives, sponsor residence and income conditions, waiting periods, fees and dependant work rights.

**Finding.** DEFERRED_PROFILE_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** PROFILE_ONLY; Administrative/legal policy. Freshness class: CURRENT_POLICY.

## Source candidates

- **C36-EU-PORTAL — European Commission, EU Immigration Portal.** Family-member country pages. Version: Country pages dated 2025; 25 EU countries. Grades: A4/L4/C3/M3. [Access](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/already-eu_en) · [Methodology](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/legal-migration-and-resettlement/family-reunification-non-eu-nationals_en) · [Licence](https://commission.europa.eu/legal-notice_en)
- **C36-OECD-IMO-2025 — OECD, International Migration Outlook 2025.** Recent family-reunification policy changes. Version: 2025. Grades: A4/L4/C3/M3. [Access](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en.html) · [Methodology](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html) · [Licence](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)

## Coverage and freshness

- **ESTIMATED, not measured:** LOW. Below 82 for exact current rules.
- **VERIFIED publisher scope:** Structured EC coverage for 25 EU countries; OECD comparative narrative for 38 members.
- Global extension requires maintained national-law coding.

## Methodology and comparability

- EC pages distinguish sponsor status, family relationship and member-state implementation.
- OECD documents changing requirements, demonstrating that a static scalar quickly becomes stale.

## Licensing and reuse

- EC-owned portal content and OECD-owned content have favourable reuse terms, but neither is a global structured rules dataset.

## Country and entity mapping

- Sponsor permit, sponsor nationality, family relationship, dependency, age and applicant nationality change the result.

## Scoring feasibility

- Direction: **PROFILE_DERIVED**; grade: **S1**.
- Return eligibility, conditions and dated route facts; avoid ranking family definitions.

## Overlap, limitations, and blockers

- Overlap: C32, C33, C72.
- Legal entitlement differs from processing time and practical approval.
- Humanitarian, EU-citizen and third-country sponsor regimes are materially different.
- Reason codes: COV_BELOW_90_PERCENT; GRA_HOUSEHOLD_SCENARIO_REQUIRED; GRA_ORIGIN_SPECIFIC; PRF_PROFILE_ONLY; OPS_EXCESSIVE_MANUAL_MAINTENANCE.

## Recommendation

Defer to a family/profile legal module. Do not create an independent national score.

## Evidence ledger

- **VERIFIED:** The Commission states that its family-reunification portal applies to 25 EU countries and national rules may be more favourable. — [source](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/already-eu_en)
- **VERIFIED:** OECD reports multiple family-reunification rule changes in 2024-2025. — [source](https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html)

## Open questions

- Should spouse/partner, minor children and dependent parents be separate product questions?

# C34 — Citizenship accessibility

**Relocation question.** How inclusive is the destination's ordinary residence-based naturalisation law for a settled adult migrant?

**Operational definition.** A narrow legal-policy construct based on residence naturalisation modes and dual-citizenship restrictions; it excludes administrative discretion and applicant-specific eligibility.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_PROFILE_CAVEAT; Expert-coded law in force. Freshness class: STATIC_OR_LEGAL_ASOF.

## Source candidates

- **C34-GLOBALCIT-V3 — European University Institute / GLOBALCIT, GLOBALCIT Citizenship Law Dataset.** v3.0 country-year-mode acquisition/loss; A06 residence naturalisation and dual-citizenship modes. Version: v3.0; laws in force 2020-2024; 191 states. Grades: A4/L4/C4/M4. [Access](https://globalcit.eu/databases/globalcit-citizenship-law-dataset/) · [Methodology](https://cadmus.eui.eu/handle/1814/73190) · [Licence](https://cadmus.eui.eu/handle/1814/73190)

## Coverage and freshness

- **ESTIMATED, not measured:** FULL. At least 90% appears highly plausible.
- **VERIFIED publisher scope:** GLOBALCIT v3 covers laws in force in 191 states.
- All stable-universe states are expected to map, but this was not downloaded and joined in Batch 2.

## Methodology and comparability

- The dataset uses a comprehensive typology: 28 acquisition and 15 loss modes with qualitative descriptions and quantitative categories.
- Formal law does not capture discretion, backlogs, residence interruptions, language-test difficulty or approval probability.

## Licensing and reuse

- The EUI repository identifies CC BY 4.0 for the dataset.
- Exact v3 archive and codebook should be captured together in a probe.

## Country and entity mapping

- ISO3 is supplied; historical/predecessor states and non-state economies require exclusion rules.
- Use law-in-force year, not repository publication year.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S2**.
- Test a transparent small rule set for residence naturalisation and dual citizenship; do not sum all 43 modes.

## Overlap, limitations, and blockers

- Overlap: C33.
- A legal inclusiveness score needs normative weights.
- Ordinary residence naturalisation is only one citizenship route.
- Reason codes: CMP_LEGAL_NOT_LIVED_OUTCOME; SCO_NORMATIVE_WEIGHTS_REQUIRED.

## Recommendation

Run an experimental Phase 3E probe on the exact v3 archive, stable-91 mapping and a deliberately narrow naturalisation-rule subset.

## Evidence ledger

- **VERIFIED:** GLOBALCIT v3 covers laws in force in 191 states on 1 January 2024 and provides downloadable files. — [source](https://globalcit.eu/databases/globalcit-citizenship-law-dataset/)
- **VERIFIED:** The EUI repository specifies Creative Commons Attribution 4.0. — [source](https://cadmus.eui.eu/handle/1814/73190)

## Open questions

- Which A06 conditions are defensibly ordinal, and should dual citizenship be a separate preference flag?

# C05 — Research and innovation ecosystem

**Relocation question.** How strong is the destination's national ecosystem for creating, funding and translating research and innovation?

**Operational definition.** A transparent national innovation measure, preferably using WIPO GII outputs or a small approved subset rather than an opaque Konsider composite.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_CITY_CAVEAT; Annual composite of hard, composite and survey indicators. Freshness class: SLOW_STRUCTURAL.

## Source candidates

- **C05-WIPO-GII-2025 — World Intellectual Property Organization, Global Innovation Index 2025 database.** Overall score; Innovation Input and Output sub-indices; 78 indicators. Version: 2025; 139 economies. Grades: A4/L4/C3/M3. [Access](https://www.wipo.int/en/web/global-innovation-index/2025/index) · [Methodology](https://www.wipo.int/web-publications/global-innovation-index-2025/en/appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html) · [Licence](https://www.wipo.int/web-publications/global-innovation-index-2025/en/copyright.html)
- **C05-WDI-RD — World Bank / UNESCO UIS, World Development Indicators.** SP.POP.SCIE.RD.P6 researchers in R&D per million. Version: 1996-2024; source published 2025-02. Grades: A4/L4/C3/M3. [Access](https://data.worldbank.org/indicator/SP.POP.SCIE.RD.P6) · [Methodology](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SP.POP.SCIE.RD.P6) · [Licence](https://data.worldbank.org/indicator/SP.POP.SCIE.RD.P6)

## Coverage and freshness

- **ESTIMATED, not measured:** HIGH. Approximately 82-88 of 91 appears plausible.
- **VERIFIED publisher scope:** GII 2025 ranks 139 economies.
- Several stable-universe microstates may be outside GII; an exact join is required.

## Methodology and comparability

- GII 2025 uses 78 indicators: 63 hard, 10 composite and five survey measures.
- The index applies minimum data-coverage rules, uses the most recent value from a multi-year window and changes some indicators between editions.

## Licensing and reuse

- WIPO states the 2025 work is CC BY 4.0, including commercial adaptation with attribution; third-party-attributed content remains excluded.
- The exact downloadable data workbook should be checked for third-party columns before redistribution.

## Country and entity mapping

- GII uses economies, including some non-sovereign territories; stable-country ISO mapping needs an explicit inclusion policy.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S2**.
- Prefer a published GII score or published sub-index; test sensitivity and avoid reweighting dozens of inputs.

## Overlap, limitations, and blockers

- Overlap: C01, C16, C62.
- National GII obscures research-city clusters.
- Composite inputs overlap governance, education, infrastructure and entrepreneurship criteria.
- Reason codes: COV_EXACT_JOIN_REQUIRED; RED_SHARED_COMPONENTS; SCO_COMPOSITE_SENSITIVITY_REQUIRED.

## Recommendation

Run a conditional Phase 3E probe to measure stable-91 coverage, capture the exact data licence and compare overall/output-only variants.

## Evidence ledger

- **VERIFIED:** GII 2025 ranks 139 economies and the downloadable model contains 78 indicators. — [source](https://www.wipo.int/web-publications/global-innovation-index-2025/en/appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html)
- **VERIFIED:** WIPO licenses the 2025 publication under CC BY 4.0, subject to third-party content. — [source](https://www.wipo.int/web-publications/global-innovation-index-2025/en/copyright.html)
- **ESTIMATED:** The exact stable-91 intersection was not measured in Batch 2. — Phase 3C Batch 2

## Open questions

- Use overall GII, Innovation Output, or a small research-only subset?
- How much overlap with C16 and governance criteria is acceptable?

# C15 — Engineering and skilled technical jobs

**Relocation question.** How large and accessible is the labour market for a person's engineering or technical specialty in likely destination regions?

**Operational definition.** Occupation- and region-specific demand, not the national stock of all professionals and technicians.

**Finding.** DEFERRED_CITY_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** CITY_OR_REGIONAL_PROFILE; Labour-force survey occupation stocks; vacancies would be platform/administrative. Freshness class: FAST_MOVING.

## Source candidates

- **C15-ILOSTAT-ISCO — International Labour Organization, ILOSTAT employment by occupation.** Employment by sex and occupation, ISCO level 2, annual. Version: Latest country survey observations; annual. Grades: A4/L4/C3/M3. [Access](https://ilostat.ilo.org/topics/employment/) · [Methodology](https://ilostat.ilo.org/methods/concepts-and-definitions/description-labour-force-statistics/) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** MEDIUM. Below 82 for recent specialty-level data.
- **VERIFIED publisher scope:** ILOSTAT has global broad occupation tables; detailed ISCO-08 level 2 coverage is materially smaller.
- Modelled major groups are broad; detailed engineering groups rely on national surveys.

## Methodology and comparability

- ISCO-08 creates an internationally comparable occupational framework.
- Occupation stock is not vacancies, wage opportunity, shortage, migrant access or engineering-specialty demand.

## Licensing and reuse

- ILOSTAT datasets published since 3 May 2023 are generally CC BY 4.0; source microdata are not redistributed.

## Country and entity mapping

- Requires ISCO-08 groups, specialty mapping, region and profession licensing.
- Countries may report different ISCO versions or broad groups.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S1**.
- No national scoring until a profession and regional demand measure exists.

## Overlap, limitations, and blockers

- Overlap: C11, C12, C17, C38.
- National employment shares can reward mature sectors without indicating openings.
- Engineering projects and jobs are geographically concentrated.
- Reason codes: COV_BELOW_90_PERCENT; GRA_CITY_LEVEL_REQUIRED; GRA_PROFESSION_SPECIFIC; CMP_STOCK_NOT_OPPORTUNITY.

## Recommendation

Defer. Use ILOSTAT only as contextual sector size in a later occupation/city module.

## Evidence ledger

- **VERIFIED:** ILOSTAT offers annual ISCO level-2 employment tables and documents ISCO comparability. — [source](https://ilostat.ilo.org/topics/employment/)
- **ESTIMATED:** No globally comparable vacancy series at engineering-specialty and city level was verified. — Phase 3C Batch 2 source search

## Open questions

- Which engineering specialties and metros define the first occupational profile?

# C13 — Medical and healthcare jobs

**Relocation question.** For a named health profession and recognised qualification, where are accessible jobs available in the destination?

**Operational definition.** A profession-specific opportunity measure combining demand, vacancies and licensing eligibility; provider shortages alone are insufficient.

**Finding.** DEFERRED_PROFILE_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** CITY_OR_REGIONAL_PROFILE; Health-workforce administrative data and labour surveys. Freshness class: STANDARD_SOCIOECONOMIC.

## Source candidates

- **C13-WHO-NHWA — World Health Organization, National Health Workforce Accounts / Global Health Workforce statistics.** Health-worker density and distribution; foreign-trained/foreign-born indicators. Version: Current WHO workforce releases. Grades: A4/L4/C3/M3. [Access](https://www.who.int/data/gho/data/themes/topics/health-workforce) · [Methodology](https://www.who.int/publications/i/item/9789240066649) · [Licence](https://data.who.int/about/data/terms-and-conditions)
- **C13-ILO-CARE — International Labour Organization, ILOSTAT worker and sector profiles.** Care employment by occupation, including ISCO level 2. Version: Latest harmonised microdata observations. Grades: A4/L4/C3/M3. [Access](https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/) · [Methodology](https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** MEDIUM. Below 82 for accessible jobs.
- **VERIFIED publisher scope:** WHO mobility evidence covers 134 countries; detailed occupational employment is sparser.
- Health worker density is broad but does not encode licensing or vacancies.

## Methodology and comparability

- WHO/NHWA measures workforce supply and migration, not vacancies accessible to a foreign-qualified applicant.
- ILOSTAT care profiles may estimate missing 4-digit detail using income-group shares, which weakens specialty interpretation.

## Licensing and reuse

- WHO datasets are generally CC BY 4.0 with additional terms; ILOSTAT data are generally CC BY 4.0.
- Licensing is not the principal blocker.

## Country and entity mapping

- Profession, qualification origin, regulator, language, region and public/private employer matter.

## Scoring feasibility

- Direction: **PROFILE_DERIVED**; grade: **S1**.
- Do not invert provider density or shortage into job accessibility.

## Overlap, limitations, and blockers

- Overlap: C11, C38, C50.
- Shortage may coexist with hiring freezes or licensing barriers.
- Country aggregates obscure rural/urban maldistribution.
- Reason codes: GRA_PROFESSION_SPECIFIC; GRA_CITY_LEVEL_REQUIRED; PRF_PROFILE_ONLY; CMP_SHORTAGE_NOT_JOB_ACCESS.

## Recommendation

Defer to a regulated-profession profile module; retain WHO and ILOSTAT as contextual evidence.

## Evidence ledger

- **VERIFIED:** WHO's mobility report covers 134 countries through multiple reporting mechanisms. — [source](https://www.who.int/publications/i/item/9789240066649)
- **VERIFIED:** ILOSTAT care profiles are derived from harmonised microdata and may estimate detailed categories. — [source](https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/)

## Open questions

- Should medicine, nursing and allied health be completely separate profiles?

# C14 — Business, finance, and professional-services jobs

**Relocation question.** How strong is demand for the user's business, finance or professional-services occupation in likely destination cities?

**Operational definition.** Occupation- and city-specific opportunity; national professional employment stock is only background context.

**Finding.** DEFERRED_CITY_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** CITY_OR_REGIONAL_PROFILE; Labour-force survey occupation/industry stocks. Freshness class: FAST_MOVING.

## Source candidates

- **C14-ILOSTAT-ISCO-ISIC — International Labour Organization, ILOSTAT employment tables.** Employment by occupation and economic activity, annual. Version: Latest annual national observations. Grades: A4/L4/C3/M3. [Access](https://ilostat.ilo.org/topics/employment/) · [Methodology](https://ilostat.ilo.org/methods/concepts-and-definitions/description-labour-force-statistics/) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** MEDIUM. Below 82 for recent exact construct.
- **VERIFIED publisher scope:** ILOSTAT broad occupation and industry data are global, detailed intersections are sparse.
- Business/finance is not one ISCO major group and city demand is unavailable globally.

## Methodology and comparability

- ISCO and ISIC support harmonised broad classifications.
- Crossing occupation and industry substantially reduces coverage and still measures incumbents, not openings.

## Licensing and reuse

- ILOSTAT reuse terms are favourable; no global official vacancy dataset was identified.

## Country and entity mapping

- Requires occupation, industry and metropolitan-area mappings.
- Professional licensing applies to some finance, accounting and legal roles.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S1**.
- No independent national score; later use vacancy rates or occupation-adjusted demand.

## Overlap, limitations, and blockers

- Overlap: C11, C12, C17.
- Jobs cluster in financial and corporate centres.
- A large sector can have weak current hiring.
- Reason codes: COV_BELOW_90_PERCENT; GRA_CITY_LEVEL_REQUIRED; GRA_PROFESSION_SPECIFIC; CMP_STOCK_NOT_OPPORTUNITY.

## Recommendation

Defer to the occupation/city layer.

## Evidence ledger

- **VERIFIED:** ILOSTAT exposes occupation, economic-activity and combined employment tables. — [source](https://ilostat.ilo.org/topics/employment/)
- **ESTIMATED:** No authoritative global city vacancy source with production-compatible reuse was verified. — Phase 3C Batch 2 source search

## Open questions

- Which ISCO occupations and business centres should define an eventual pilot?

# C16 — Entrepreneurship and startup opportunity

**Relocation question.** How active is formal new-firm creation in the destination, as a narrow signal of entrepreneurial opportunity?

**Operational definition.** New limited-liability business registrations per 1,000 working-age people; it does not claim startup survival, funding or immigrant eligibility.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_CITY_CAVEAT; Administrative business-registry data. Freshness class: STANDARD_SOCIOECONOMIC.

## Source candidates

- **C16-WB-ENTREPRENEURSHIP — World Bank, Entrepreneurship Database / World Development Indicators.** IC.BUS.NDNS.ZS new business density. Version: 8th edition; annual 2006-2024. Grades: A4/L4/C4/M3. [Access](https://api.worldbank.org/v2/country/all/indicator/IC.BUS.NDNS.ZS?format=json&per_page=20000) · [Methodology](https://www.worldbank.org/en/programs/entrepreneurship/methodology) · [Licence](https://databank.worldbank.org/metadataglossary/sustainable-development-goals-%28sdgs%29/series/IC.BUS.NDNS.ZS)

## Coverage and freshness

- **MEASURED:** MEDIUM. 79/91 measured for at least one non-null 2022-2024 observation.
- **MEASURED missing/insufficient ISO3:** ARE, BHS, CMR, DOM, GRD, HTI, NIC, OMN, QAT, TTO, UKR, USA.
- **VERIFIED publisher scope:** World Bank collects from registries in 170 economies; 2006-2024.
- Measured current coverage is below the Phase 3A minimum of 82; some available country values also cover partial geography.

## Methodology and comparability

- A consistent concept—new limited-liability registrations per 1,000 people ages 15-64—is collected mainly from national registries.
- The measure excludes informal firms and does not capture formation quality, survival or venture funding.

## Licensing and reuse

- World Bank metadata marks the exact series CC BY 4.0.

## Country and entity mapping

- China covers Shanghai and Canada covers selected registries; these geographic exceptions must be explicit.
- Offshore financial centres may have registrations disconnected from resident opportunity.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S3**.
- Log1p, winsorise extreme offshore values, robust percentile; require recency and geography flags.

## Overlap, limitations, and blockers

- Overlap: C05, C29.
- Formal registration can reflect regulatory or tax structures.
- New-firm density is not startup employment or success.
- Reason codes: COV_BELOW_90_PERCENT; CMP_PARTIAL_GEOGRAPHY; SCO_OUTLIER_POLICY_REQUIRED.

## Recommendation

Run only a conditional Phase 3E recovery probe. The measured 79/91 result misses the 82-country threshold before partial-geography exclusions.

## Evidence ledger

- **VERIFIED:** The 8th Entrepreneurship Database edition contains annual company data through 2024 and uses a common limited-liability definition. — [source](https://www.worldbank.org/en/programs/entrepreneurship/methodology)
- **VERIFIED:** World Bank metadata identifies IC.BUS.NDNS.ZS as annual and CC BY 4.0. — [source](https://databank.worldbank.org/metadataglossary/sustainable-development-goals-%28sdgs%29/series/IC.BUS.NDNS.ZS)
- **MEASURED:** The exact 2022-2024 WDI query returned current observations for 79/91 stable countries; 12 were missing. — konsider_phase3c_batch2/world_bank_coverage_measurements.json

## Open questions

- Exclude or flag partial-geography and offshore observations?
- Require 2023+ or allow 2022?

# C19 — Employment protection and worker rights

**Relocation question.** How well are workers' fundamental organizing and collective-bargaining rights protected in law and practice?

**Operational definition.** The exact ILO SDG 8.8.2 construct, evaluated for suitability; broader dismissal protection and enforcement are not silently added.

**Finding.** REJECTED; **recommendation:** REJECT.

**Natural granularity and observation.** NATIONAL; ILO coding of supervisory texts and national legislation. Freshness class: SLOW_STRUCTURAL.

## Source candidates

- **C19-ILO-SDG-882 — International Labour Organization, ILOSTAT SDG indicator 8.8.2.** National compliance with labour rights: freedom of association and collective bargaining. Version: Methodology amended 2022; current ILO textual sources. Grades: A4/L4/C1/M3. [Access](https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/) · [Methodology](https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/) · [Licence](https://www.ilo.org/rights-and-permissions)

## Coverage and freshness

- **ESTIMATED, not measured:** HIGH. Broad nominal coverage is plausible.
- **VERIFIED publisher scope:** Method applies to ILO member states.
- Coverage cannot cure the source's explicit prohibition on cross-country comparison.

## Methodology and comparability

- The ILO states that SDG 8.8.2 measures freedom of association and collective bargaining using six supervisory textual sources and national law.
- The ILO explicitly says the indicator is not intended to compare compliance among member states because reporting obligations differ.

## Licensing and reuse

- ILOSTAT reuse is generally CC BY 4.0; methodological unsuitability, not licence, is decisive.

## Country and entity mapping

- Country mapping is straightforward; ratification and reporting-regime differences are substantive.

## Scoring feasibility

- Direction: **LOWER_BETTER**; grade: **S0**.
- None. Do not rank countries against the custodian agency's usage warning.

## Overlap, limitations, and blockers

- Overlap: C11, C71.
- Covers only two fundamental labour-right domains.
- Textual-source intensity and reporting obligations differ across states.
- Reason codes: CMP_SOURCE_PROHIBITS_COUNTRY_COMPARISON; CMP_DEFINITION_TOO_NARROW; SCO_INDEFENSIBLE.

## Recommendation

Reject as an independent scored criterion. Retain only as descriptive research evidence if the product later adds unranked labour-rights profiles.

## Evidence ledger

- **VERIFIED:** ILO states SDG 8.8.2 is not intended as a tool to compare compliance among member states. — [source](https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/)
- **VERIFIED:** The indicator is limited to freedom of association and effective recognition of collective bargaining. — [source](https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/)

## Open questions

- Whether an unscored worker-rights information panel is valuable.

# C22 — Social-security and mandatory contribution burden

**Relocation question.** For a given salary, household and employment arrangement, what mandatory employee and employer social contributions apply and what benefits do they confer?

**Operational definition.** A salary- and household-specific contribution calculation, not an aggregate national revenue ratio.

**Finding.** DEFERRED_PROFILE_LAYER; **recommendation:** DEFER.

**Natural granularity and observation.** PROFILE_ONLY; Administrative tax-benefit model. Freshness class: FAST_MOVING.

## Source candidates

- **C22-OECD-TW-2026 — OECD, Taxing Wages 2026.** Employee/employer social-security contributions by eight household types. Version: 2025 tax year; 38 countries. Grades: A4/L4/C4/M3. [Access](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en.html) · [Methodology](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html) · [Licence](https://www.oecd.org/en/about/oecd-open-by-default-policy.html)

## Coverage and freshness

- **ESTIMATED, not measured:** LOW. Far below 82.
- **VERIFIED publisher scope:** OECD Taxing Wages covers 38 members.
- No equally comparable global household-level contribution model was verified.

## Methodology and comparability

- OECD calculates comparable effective burdens for specified earnings and household types.
- Contributions have ceilings, benefit entitlements and employee/employer incidence that make a headline statutory rate misleading.

## Licensing and reuse

- OECD-owned post-July-2024 content is generally CC BY 4.0, subject to exceptions.

## Country and entity mapping

- Requires salary, household, age, employment status and sometimes region.
- Tax years can differ from calendar years.

## Scoring feasibility

- Direction: **PROFILE_DERIVED**; grade: **S2**.
- Calculate scenario-specific net burden; do not assume lower contributions are always better.

## Overlap, limitations, and blockers

- Overlap: C21, C26, C72.
- OECD-only coverage.
- Burden without benefit entitlement is incomplete for relocation decisions.
- Reason codes: COV_BELOW_90_PERCENT; GRA_HOUSEHOLD_SCENARIO_REQUIRED; PRF_PROFILE_ONLY; SCO_DIRECTION_AMBIGUOUS.

## Recommendation

Defer to a future tax-benefit calculator; reject as a universal national criterion.

## Evidence ledger

- **VERIFIED:** Taxing Wages 2026 covers all 38 OECD members and eight household types using 2025 rules. — [source](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report.html)
- **VERIFIED:** The model separates employee and employer social contributions, income tax and cash benefits. — [source](https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html)

## Open questions

- Should contributions be displayed with expected health, pension and unemployment entitlements?

# C26 — Healthcare affordability

**Relocation question.** How exposed are households to paying for healthcare directly rather than through pooled financing?

**Operational definition.** Household out-of-pocket health spending as a share of current health expenditure, used only as a national financial-protection proxy.

**Finding.** EXPERIMENTAL_CANDIDATE; **recommendation:** EXPERIMENTAL_ONLY.

**Natural granularity and observation.** NATIONAL_WITH_PROFILE_CAVEAT; National health accounts, reported and estimated. Freshness class: STANDARD_SOCIOECONOMIC.

## Source candidates

- **C26-WHO-GHED-OOP — World Health Organization, Global Health Expenditure Database.** OOP%CHE; household out-of-pocket payment / current health expenditure. Version: GHED all data March 2026; series commonly through 2023/2024. Grades: A4/L4/C4/M3. [Access](https://apps.who.int/nha/database/DocumentationCentre/Index/en) · [Methodology](https://www.who.int/publications/b/80101) · [Licence](https://data.who.int/about/data/terms-and-conditions)

## Coverage and freshness

- **ESTIMATED, not measured:** FULL. 91/91 appears plausible.
- **VERIFIED publisher scope:** WHO GHED provides comparable data for more than 190 members since 2000.
- Exact latest-year stable-91 coverage must be queried; GHED includes reported and estimated values.

## Methodology and comparability

- GHED uses the SHA 2011 framework and defines OOP%CHE consistently.
- The ratio measures financing structure, not immigrant eligibility, insurance premiums, prices, unmet need or catastrophic-spending incidence.

## Licensing and reuse

- WHO dataset terms generally provide CC BY 4.0 with additional terms.
- The 2025 methodology publication itself is CC BY-NC-SA 3.0 IGO; publication and dataset licences must not be conflated.

## Country and entity mapping

- WHO country codes require stable ISO mapping; territories and historical names need explicit rules.

## Scoring feasibility

- Direction: **LOWER_BETTER**; grade: **S3**.
- Reverse robust percentile; test against catastrophic-spending measures and do not label it personal cost.

## Overlap, limitations, and blockers

- Overlap: C22, C50.
- A low share may reflect high total pooled spending or suppressed access.
- Migrant coverage rules can differ from citizen coverage.
- Reason codes: COV_EXACT_JOIN_REQUIRED; CMP_PROXY_ONLY; GRA_MIGRANT_ELIGIBILITY_MISSING.

## Recommendation

Run a conditional Phase 3E probe for stable-91 recency and licensing capture; keep the criterion explicitly labelled financial-protection proxy.

## Evidence ledger

- **VERIFIED:** WHO defines OOP%CHE as household out-of-pocket payment divided by current health expenditure. — [source](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/out-of-pocket-expenditure-as-percentage-of-current-health-expenditure-%28che%29-%28-%29)
- **VERIFIED:** GHED provides comparable data for more than 190 WHO member states since 2000. — [source](https://www.who.int/teams/health-financing-and-economics/health-financing/expenditure-tracking/data-and-analytics)
- **VERIFIED:** WHO dataset terms are generally CC BY 4.0 unless specifically indicated otherwise. — [source](https://data.who.int/about/data/terms-and-conditions)

## Open questions

- Prefer OOP%CHE or catastrophic health spending where available?
- How should migrant eligibility be surfaced separately?

# C29 — Currency and macroeconomic stability

**Relocation question.** How stable are household purchasing power and the destination's price/currency environment over a recent multi-year period?

**Operational definition.** A transparent small composite of consumer-price inflation level/volatility and official-exchange-rate volatility, with currency-union and peg caveats.

**Finding.** PROBE_APPROVED; **recommendation:** PROCEED_DETERMINISTIC_PROBE.

**Natural granularity and observation.** NATIONAL; Official macroeconomic annual series. Freshness class: FAST_MOVING.

## Source candidates

- **C29-WDI-INFLATION — World Bank distribution / IMF IFS upstream, World Development Indicators.** FP.CPI.TOTL.ZG consumer-price inflation. Version: Annual through 2024. Grades: A4/L4/C4/M4. [Access](https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json&per_page=20000) · [Methodology](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG) · [Licence](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG)
- **C29-WDI-FXRATE — World Bank distribution / IMF IFS upstream, World Development Indicators.** PA.NUS.FCRF official exchange rate, LCU per USD. Version: Annual through 2024. Grades: A4/L4/C3/M4. [Access](https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF?format=json&per_page=20000) · [Methodology](https://data.worldbank.org/indicator/PA.NUS.FCRF) · [Licence](https://data.worldbank.org/indicator/PA.NUS.FCRF)

## Coverage and freshness

- **MEASURED:** FULL. 91/91 measured component intersection.
- **VERIFIED publisher scope:** WDI/IMF annual inflation and official-exchange-rate series through 2024.
- All 91 countries had at least three non-null 2020-2024 observations in both components and a latest observation in 2023 or 2024.

## Methodology and comparability

- Inflation is comparable as annual CPI change; exchange-rate volatility requires log returns over several years.
- Official exchange rates can diverge from market rates, and a fixed peg can show low volatility despite reserve or convertibility risk.

## Licensing and reuse

- The exact WDI indicator pages mark the distributed data CC BY 4.0.

## Country and entity mapping

- Countries sharing EUR, XCD or USD need currency-union awareness.
- Redenominations and currency breaks must not be interpreted as volatility.

## Scoring feasibility

- Direction: **LOWER_BETTER**; grade: **S3**.
- Robust percentile of five-year median absolute inflation plus exchange-rate log-return volatility; publish component sensitivity.

## Overlap, limitations, and blockers

- Overlap: C16, Existing economic indicators.
- Macroeconomic stability is broader than inflation and FX.
- Using USD as the sole reference may not match the user's income currency.
- Reason codes: CMP_CURRENCY_REGIME; SCO_COMPOSITE_SENSITIVITY_REQUIRED.

## Recommendation

Proceed to a deterministic Phase 3E probe using pinned 2020-2024 observations and explicit currency-break handling.

## Evidence ledger

- **VERIFIED:** WDI distributes annual CPI inflation through 2024 under CC BY 4.0. — [source](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG)
- **VERIFIED:** WDI provides official exchange-rate observations for most stable-universe countries through 2024. — [source](https://data.worldbank.org/indicator/PA.NUS.FCRF)
- **MEASURED:** The stated two-component recency rule produced a measured 91/91 stable-country intersection. — konsider_phase3c_batch2/world_bank_coverage_measurements.json

## Open questions

- Should FX volatility be user-income-currency specific?
- Should fixed/union currencies receive a separate regime flag?

# C48 — Political stability and civil peace

**Relocation question.** How low is the perceived likelihood of political instability, politically motivated violence or terrorism disrupting normal life?

**Operational definition.** World Bank WGI Political Stability and Absence of Violence/Terrorism, using the 2025 revision's absolute score and uncertainty interval.

**Finding.** PROBE_APPROVED; **recommendation:** PROCEED_DETERMINISTIC_PROBE.

**Natural granularity and observation.** NATIONAL; Annual perception-based composite. Freshness class: SLOW_STRUCTURAL.

## Source candidates

- **C48-WGI-PV-2025 — World Bank, Worldwide Governance Indicators 2025 revision.** Political Stability and Absence of Violence/Terrorism; estimate and absolute 0-100 score. Version: 2025 revision; 1996-2024 recalculated. Grades: A4/L4/C4/M4. [Access](https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators) · [Methodology](https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation) · [Licence](https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators)

## Coverage and freshness

- **MEASURED:** FULL. 91/91 measured for 2024.
- **VERIFIED publisher scope:** WGI covers more than 200 economies through 2024.
- The exact GOV_WGI_PV_EST 2024 API query mapped to all 91 stable countries.

## Methodology and comparability

- WGI aggregates perception data from 35 cross-country sources using an unobserved-components model.
- The 2025 revision recalculates history, adds an anchored 0-100 scale and supplies uncertainty intervals.

## Licensing and reuse

- The World Bank catalogue marks WGI CC BY 4.0.
- Underlying commercial source data have separate constraints, but published aggregate estimates are the candidate input.

## Country and entity mapping

- More than 200 economies allow stable-91 ISO mapping; territory treatment must follow the universe registry.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S4**.
- Use published absolute score; retain confidence interval and test rank ties/uncertainty.

## Overlap, limitations, and blockers

- Overlap: C66, C68, C49.
- Perception composite is not an event forecast.
- Margins of error make small rank differences non-substantive.
- Reason codes: CMP_PERCEPTION_BASED; SCO_UNCERTAINTY_REQUIRED.

## Recommendation

Proceed to a deterministic Phase 3E probe on the 2025-revision aggregate and its uncertainty fields.

## Evidence ledger

- **VERIFIED:** WGI 2025 covers more than 200 economies from 1996-2024 and is CC BY 4.0. — [source](https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators)
- **VERIFIED:** The 2025 methodology uses 35 perception sources and publishes absolute 0-100 scores plus uncertainty. — [source](https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation)
- **MEASURED:** The exact 2024 GOV_WGI_PV_EST API query returned 91/91 stable countries. — konsider_phase3c_batch2/world_bank_coverage_measurements.json

## Open questions

- Use only PV or add conflict-event data later as an unscored alert layer?

# C49 — Rule of law and institutional trust

**Relocation question.** How strongly do people and experts perceive that contracts, property rights, police, courts and rules are respected?

**Operational definition.** Narrow to WGI Rule of Law; do not claim it directly measures interpersonal or political trust.

**Finding.** PROBE_APPROVED; **recommendation:** PROCEED_DETERMINISTIC_PROBE.

**Natural granularity and observation.** NATIONAL; Annual perception-based composite. Freshness class: SLOW_STRUCTURAL.

## Source candidates

- **C49-WGI-RL-2025 — World Bank, Worldwide Governance Indicators 2025 revision.** Rule of Law estimate and absolute 0-100 score; GOV_WGI_RL_EST. Version: 2025 revision; 2024 observations. Grades: A4/L4/C4/M4. [Access](https://data.worldbank.org/indicator/GOV_WGI_RL_EST) · [Methodology](https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation) · [Licence](https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators)

## Coverage and freshness

- **MEASURED:** FULL. 91/91 measured for 2024.
- **VERIFIED publisher scope:** WGI covers more than 200 economies through 2024.
- The exact GOV_WGI_RL_EST 2024 API query mapped to all 91 stable countries.

## Methodology and comparability

- WGI Rule of Law captures perceptions of confidence in and adherence to societal rules, including contracts, property rights, police, courts, crime and violence.
- Institutional trust is related but not identical; the criterion name should be narrowed in production.

## Licensing and reuse

- The exact WGI dataset is CC BY 4.0.

## Country and entity mapping

- Stable-91 ISO mapping should be straightforward; use the current WGI revision consistently across all years.

## Scoring feasibility

- Direction: **HIGHER_BETTER**; grade: **S4**.
- Use published absolute score and uncertainty; do not average Rule of Law, corruption and effectiveness without a separate rationale.

## Overlap, limitations, and blockers

- Overlap: C48, Existing governance-related criteria.
- Perception sources and source availability vary by economy.
- Small differences are often within confidence intervals.
- Reason codes: CMP_PERCEPTION_BASED; SCO_UNCERTAINTY_REQUIRED; RED_POTENTIAL_GOVERNANCE_OVERLAP.

## Recommendation

Proceed to a deterministic Phase 3E probe after narrowing the label to Rule of Law and checking overlap with the active catalog.

## Evidence ledger

- **VERIFIED:** The exact WGI Rule of Law indicator is distributed under CC BY 4.0 with 2024 data. — [source](https://data.worldbank.org/indicator/GOV_WGI_RL_EST)
- **VERIFIED:** WGI documentation advises using uncertainty and treating the composites as broad cross-country lenses. — [source](https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation)
- **MEASURED:** The exact 2024 GOV_WGI_RL_EST API query returned 91/91 stable countries. — konsider_phase3c_batch2/world_bank_coverage_measurements.json

## Open questions

- Rename to Rule of law?
- Would Control of Corruption or Government Effectiveness add distinct relocation value?
