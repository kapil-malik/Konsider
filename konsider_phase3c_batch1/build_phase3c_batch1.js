const fs = require("fs");
const path = require("path");

const OUT = __dirname;
const CHECKED = "2026-07-24T00:00:00+05:30";
const U = "stable_supported_v1";

const src = (id, publisher, dataset, series, access, method, licence, grades, level = "VERIFIED", version = null) => ({
  source_candidate_id: id, publisher, dataset, series_or_table: series, access_url: access,
  methodology_url: method, licence_url: licence, version,
  authority_grade: grades[0], licence_grade: grades[1], comparability_grade: grades[2],
  mapping_grade: grades[3], evidence_level: level
});

const ev = (claim, source, level = "VERIFIED", notes = null) => ({
  claim, source, locator: source, checked_at: CHECKED, evidence_level: level, notes
});

const cov = (band, measured, found = null, fresh = null, missing = null, parsed = null) => ({
  universe_id: U, denominator: 91, expected_band: band, measured, found, fresh,
  parsed, validated: null, missing, stale: null, invalid: null, rejected: null,
  unmapped: null, only_blocker: null
});

const score = (mode, grade, method, sensitivity = true) => ({
  mode, grade, proposed_method: method, sensitivity_required: sensitivity
});

const common = {
  phase_id: "3C",
  research_wave: "BATCH_1"
};

const specs = [
  {
    rank: 1, id: "C11", name: "Overall job-market opportunity",
    category: "Employment, income and economic opportunity", tags: ["IC"],
    granularity: "NATIONAL", pillars: ["WORK_AND_STUDY"],
    question: "How strong is the destination's national labour market for a working-age newcomer, before occupation-specific matching?",
    definition: "A narrow national composite of modelled unemployment, employment-to-population ratio and labour-force participation for total population age 15+.",
    profiles: ["working-age movers", "job seekers"], value: 5, dependence: "MODERATE",
    status: "PROBE_APPROVED", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("HIGH", true, 88, 88, 3, 88),
    observation: "National, modelled annual estimates",
    sources: [
      src("C11-ILO-MODEL-2025", "International Labour Organization (ILOSTAT)", "ILOSTAT bulk download", "UNE_2EAP_SEX_AGE_RT_A; EMP_2WAP_SEX_AGE_RT_A; EAP_2WAP_SEX_AGE_RT_A", "https://rplumber.ilo.org/data/indicator/", "https://ilostat.ilo.org/data/bulk/", "https://www.ilo.org/rights-and-permissions", ["A4","L4","C4","M3"], "MEASURED", "ILO modelled estimates, Nov. 2025")
    ],
    scoring: score("HIGHER_BETTER", "S3", "Reverse unemployment; robust-percentile each component; average only after correlation and weight sensitivity checks."),
    comp: ["[VERIFIED] ILO modelled estimates use a common statistical system and identical age/sex dimensions.", "[ESTIMATED] The three components partly duplicate one latent labour-utilisation factor."],
    mapping: ["[MEASURED] ISO3 joined deterministically; ATG, GRD and UKR were absent from all three 2025 slices."],
    licensing: ["[VERIFIED] ILO datasets and referential metadata published from 3 May 2023 are CC BY 4.0; restricted partner microdata are excluded."],
    redundancy: ["C12", "C17"],
    maintenance: ["Annual edition pinning is required; projections beyond the edition's current year must not be mixed with observed/modelled current-year values."],
    blockers: ["COV_NOT_FULL_91"],
    caveats: ["RED_SHARED_COMPONENTS", "CMP_MODEL_ASSUMPTIONS_OPAQUE"],
    recommendation: "Proceed to a deterministic Phase 3E probe. The measured 88/91 intersection clears the 82-country threshold but requires an explicit missing-country policy.",
    open: ["Should C11 remain a composite or expose unemployment and employment separately?", "Is 2025 accepted as a modelled current-year value?"],
    evidence: [
      ev("The three exact ILOSTAT 2025 total/15+ series each returned 88 stable countries; common missing ISO3 codes were ATG, GRD and UKR.", "https://rplumber.ilo.org/data/indicator/", "MEASURED"),
      ev("The ILOSTAT catalogue labels the series as Nov. 2025 modelled estimates and exposes reproducible bulk CSV downloads.", "https://ilostat.ilo.org/data/bulk/"),
      ev("ILOSTAT data licence is CC BY 4.0 for datasets published from 3 May 2023.", "https://www.ilo.org/rights-and-permissions")
    ],
    shortlist: "DETERMINISTIC", shortlistRank: 2
  },
  {
    rank: 2, id: "C32", name: "Skilled-work visa accessibility",
    category: "Migration, visa and settlement", tags: ["IC","SC","LF"],
    granularity: "PROFILE_ONLY", pillars: ["LEGAL_MOBILITY"],
    question: "Given a person's nationality, occupation, qualifications, salary and employer situation, how feasible is a lawful skilled-work route?",
    definition: "A profile-derived eligibility and friction assessment, not a destination-only national score.",
    profiles: ["skilled workers", "regulated professionals", "employer-sponsored applicants"], value: 5, dependence: "PROFILE_ONLY",
    status: "DEFERRED_PROFILE_LAYER", freshness: "CURRENT_POLICY",
    coverage: cov("LOW", false),
    observation: "Administrative/legal policy; profile- and origin-dependent",
    sources: [
      src("C32-OECD-ITA-2023", "OECD", "Indicators of Talent Attractiveness 2023", "Highly educated workers; migration-policy dimension", "https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html", "https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", ["A4","L3","C3","M3"], "VERIFIED", "2023"),
      src("C32-EU-PORTAL", "European Commission", "EU Immigration Portal", "Highly-qualified worker country pages", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en", null, "https://commission.europa.eu/legal-notice_en", ["A4","L4","C2","M3"], "VERIFIED", "accessed 2026-07-24")
    ],
    scoring: score("PROFILE_DERIVED", "S1", "Rule-engine eligibility plus route-specific friction; no standalone country percentile."),
    comp: ["[VERIFIED] EU rules depend on job offer, salary threshold, qualifications and member-state implementation.", "[ESTIMATED] OECD ITA is useful discovery evidence but OECD-only and broader than visa accessibility."],
    mapping: ["Country is insufficient: origin, profession, employer, salary and family status alter eligibility."],
    licensing: ["OECD default open-access policy is not a substitute for checking the exact 2023 tool export; EC-owned portal content is CC BY 4.0 unless otherwise indicated."],
    redundancy: ["C11", "C12", "C33"],
    maintenance: ["Legal rules and thresholds require frequent country-by-country change detection and dated snapshots."],
    blockers: ["COV_BELOW_90_PERCENT","GRA_ORIGIN_SPECIFIC","GRA_PROFESSION_SPECIFIC","PRF_PROFILE_ONLY","OPS_EXCESSIVE_MANUAL_MAINTENANCE"],
    caveats: ["CMP_LEGAL_NOT_LIVED_OUTCOME","FRS_UPDATE_CADENCE_UNKNOWN"],
    recommendation: "Defer to a future profile/legal-mobility layer. Reject it as an independent destination criterion.",
    open: ["Which origin passports and occupations define the first supported profiles?"],
    evidence: [
      ev("The EU portal applies to 25 EU countries and describes job-offer, qualification and salary conditions.", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en"),
      ev("OECD ITA 2023 compares talent attractiveness for highly educated workers but is limited to OECD countries.", "https://www.oecd.org/en/data/tools/talent-attractiveness-2023.html"),
      ev("No current official global dataset was verified that converts individual skilled-work eligibility into comparable destination scores.", "Phase 3C source search", "ESTIMATED")
    ]
  },
  {
    rank: 3, id: "C33", name: "Permanent-residency accessibility",
    category: "Migration, visa and settlement", tags: ["IC","SC","LF"],
    granularity: "PROFILE_ONLY", pillars: ["LEGAL_MOBILITY"],
    question: "For a specific migrant route and personal history, what lawful path exists to permanent residence and on what conditions?",
    definition: "A route-specific legal pathway assessment covering qualifying residence, permit continuity, income/language conditions and exclusions.",
    profiles: ["temporary skilled workers", "students transitioning to work", "family migrants"], value: 5, dependence: "PROFILE_ONLY",
    status: "DEFERRED_PROFILE_LAYER", freshness: "CURRENT_POLICY",
    coverage: cov("LOW", false),
    observation: "Administrative/legal policy; route- and profile-dependent",
    sources: [
      src("C33-UNDESA-1072", "UN DESA / IOM", "SDG indicator 10.7.2", "Country migration-policy data, 2021 update", "https://www.un.org/development/desa/pd/data/sdg-indicator-1072", "https://www.un.org/development/desa/pd/data/sdg-indicator-1072", "https://www.un.org/en/about-us/terms-of-use", ["A4","L1","C2","M3"], "VERIFIED", "2021"),
      src("C33-NATIONAL-PORTALS", "National immigration authorities", "Residence and settlement rules", null, null, null, null, ["A4","L2","C1","M2"], "HYPOTHESIS")
    ],
    scoring: score("PROFILE_DERIVED", "S1", "Eligibility timeline and conditions by route; informational result rather than a destination-only score."),
    comp: ["SDG 10.7.2 measures broad well-managed migration policy, not personal permanent-residence eligibility.", "National terminology and qualifying residence rules are not harmonised."],
    mapping: ["Route and legal-history mapping dominate ISO country mapping."],
    licensing: ["UN website terms permit personal non-commercial use and prohibit redistribution/derivatives absent a specific licence."],
    redundancy: ["C32"],
    maintenance: ["Requires dated legal rules, legal-review governance and frequent change detection."],
    blockers: ["SRC_NO_AUTHORITATIVE_SOURCE","LIC_REDISTRIBUTION_RESTRICTED","GRA_ORIGIN_SPECIFIC","PRF_PROFILE_ONLY","OPS_EXCESSIVE_MANUAL_MAINTENANCE"],
    caveats: ["CMP_LEGAL_NOT_LIVED_OUTCOME","FRS_POLICY_SNAPSHOT_OUTDATED"],
    recommendation: "Defer to a route-aware profile layer; reject a single national accessibility score.",
    open: ["Whether permanent residence and citizenship pathways should be separate product modules."],
    evidence: [
      ev("The current official SDG 10.7.2 update is based on 2018–2021 government inquiries and measures broad migration-policy domains.", "https://www.un.org/development/desa/pd/data/sdg-indicator-1072"),
      ev("Generic UN website terms do not provide production-compatible reuse for a derived commercial dataset.", "https://www.un.org/en/about-us/terms-of-use"),
      ev("No authoritative, current, global route-level permanent-residence dataset was verified.", "Phase 3C source search", "ESTIMATED")
    ]
  },
  {
    rank: 4, id: "C17", name: "Average earning potential",
    category: "Employment, income and economic opportunity", tags: ["IC","DO","CR"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["WORK_AND_STUDY","FINANCIAL_VIABILITY"],
    question: "What gross earning level could a typical employee plausibly attain, before occupation and city adjustments?",
    definition: "Average monthly employee earnings converted to PPP, with explicit limits as a national proxy for personal earning potential.",
    profiles: ["employees", "skilled workers"], value: 5, dependence: "HIGH",
    status: "DEFERRED", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("MEDIUM", true, 76, 60, 15, 76),
    observation: "National survey/administrative estimates, harmonised by ILOSTAT",
    sources: [
      src("C17-ILO-EARN", "International Labour Organization (ILOSTAT)", "ILOSTAT bulk download", "EAR_EMTA_SEX_CUR_NB_A; CUR_TYPE_PPP; SEX_T", "https://rplumber.ilo.org/data/indicator/", "https://ilostat.ilo.org/data/bulk/", "https://www.ilo.org/rights-and-permissions", ["A4","L4","C3","M3"], "MEASURED", "updated 2026-07-19")
    ],
    scoring: score("HIGHER_BETTER", "S3", "Log PPP earnings, winsorise tails, then robust percentile; do not treat as expected salary for a user."),
    comp: ["Employee coverage, informal work, hours and source instruments vary.", "PPP improves price comparability but does not remove occupation or city composition effects."],
    mapping: ["ISO3 is stable; the substantive blocker is observation availability."],
    licensing: ["ILOSTAT dataset and metadata are CC BY 4.0."],
    redundancy: ["C11","C25"],
    maintenance: ["Currency and PPP classifications must be pinned; source breaks and multiple national observations need deterministic precedence."],
    blockers: ["COV_BELOW_90_PERCENT","GRA_CITY_LEVEL_REQUIRED","GRA_PROFESSION_SPECIFIC"],
    caveats: ["CMP_POPULATION_DIFFERS","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Defer. Measured recent PPP earnings coverage is 60/91 for 2023+ and 76/91 for 2021+, below the Phase 3A threshold.",
    open: ["Whether a different official income concept can recover 82+ countries without changing the question."],
    evidence: [
      ev("EAR_EMTA_SEX_CUR_NB_A PPP observations covered 76 stable countries from 2021 onward and 60 from 2023 onward.", "https://rplumber.ilo.org/data/indicator/", "MEASURED"),
      ev("The exact ILOSTAT table was updated 19 July 2026 and spans through 2026.", "https://rplumber.ilo.org/metadata/toc/indicator/", "VERIFIED")
    ]
  },
  {
    rank: 5, id: "C21", name: "Personal income-tax burden",
    category: "Tax, cost and financial conditions", tags: ["IC"],
    granularity: "PROFILE_ONLY", pillars: ["FINANCIAL_VIABILITY"],
    question: "For a given salary, household and employment arrangement, what share of labour cost or gross earnings is taken by income tax and mandatory contributions?",
    definition: "A household-scenario tax wedge or net personal average tax rate, not a universal national rate.",
    profiles: ["employees", "families", "self-employed workers"], value: 5, dependence: "PROFILE_ONLY",
    status: "DEFERRED_PROFILE_LAYER", freshness: "FAST_MOVING",
    coverage: cov("LOW", false),
    observation: "Administrative tax model; household-scenario dependent",
    sources: [
      src("C21-OECD-TW-2026", "OECD", "Taxing Wages 2026 / OECD Data Explorer", "OECD.CTP.TPS,DSD_TAX_WAGES_COMP@DF_TW_COMP", "https://data-explorer.oecd.org/", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", ["A4","L4","C4","M3"], "VERIFIED", "2025 tax year")
    ],
    scoring: score("PROFILE_DERIVED", "S2", "Compute net burden for explicit salary and household scenarios; lower is not automatically better without service-benefit context."),
    comp: ["OECD methodology is highly comparable inside 38 OECD members but not globally representative.", "Results change by earnings level, household type and social-contribution treatment."],
    mapping: ["Country mapping is straightforward; tax-unit and household mapping are not."],
    licensing: ["OECD content from July 2024 is generally CC BY 4.0, subject to exact-page exceptions and third-party material."],
    redundancy: ["C25"],
    maintenance: ["Annual tax-law parameter updates and scenario versioning are required."],
    blockers: ["COV_BELOW_90_PERCENT","GRA_HOUSEHOLD_SCENARIO_REQUIRED","PRF_PROFILE_ONLY"],
    caveats: ["CMP_DEFINITION_DIFFERS","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Defer to a profile-based affordability calculator; do not use the OECD-only series as a 91-country ranking criterion.",
    open: ["Which standard household and salary scenarios would be product-supported?"],
    evidence: [
      ev("Taxing Wages 2026 covers the 38 OECD countries and reports 2025 tax wedges/net personal average rates by household type.", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html"),
      ev("The exact comparative Data Explorer family is DSD_TAX_WAGES_COMP@DF_TW_COMP.", "https://data-explorer.oecd.org/")
    ]
  },
  {
    rank: 6, id: "C25", name: "Housing affordability",
    category: "Tax, cost and financial conditions", tags: ["IC","SC","CR","LF"],
    granularity: "CITY_OR_REGIONAL", pillars: ["FINANCIAL_VIABILITY"],
    question: "Can the user's household afford suitable housing in the destination city on its expected disposable income?",
    definition: "City-level rent or ownership cost divided by profile-specific disposable income, with tenure and household size explicit.",
    profiles: ["renters", "buyers", "families"], value: 5, dependence: "HIGH",
    status: "DEFERRED_CITY_LAYER", freshness: "FAST_MOVING",
    coverage: cov("LOW", false),
    observation: "City/regional market data plus household income scenario",
    sources: [
      src("C25-OECD-AHD", "OECD", "Affordable Housing Database", "HC1.2 Housing costs over income", "https://www.oecd.org/en/data/datasets/oecd-affordable-housing-database.html", "https://webfs.oecd.org/Els-com/Affordable_Housing_Database/HC1-2-Housing-costs-over-income.pdf", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", ["A4","L4","C3","M3"], "VERIFIED", "files current 2025-10")
    ],
    scoring: score("LOWER_BETTER", "S3", "Profile-specific housing-cost share; national price-to-income only as context."),
    comp: ["HC1.2 total housing costs are available mainly for European countries plus New Zealand and definitions differ.", "National ratios conceal metropolitan rent dispersion."],
    mapping: ["Requires city/metro identifiers, tenure, bedrooms and household composition."],
    licensing: ["OECD open-access policy is favourable; exact workbook/front-page licence still needs capture in implementation."],
    redundancy: ["C17","C21"],
    maintenance: ["Fast-moving city rents and disposable incomes require more frequent updates than annual national statistics."],
    blockers: ["COV_BELOW_90_PERCENT","COV_REGIONALLY_BIASED","GRA_CITY_LEVEL_REQUIRED","GRA_HOUSEHOLD_SCENARIO_REQUIRED"],
    caveats: ["CMP_DEFINITION_DIFFERS","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Defer to the city and profile layers. National OECD ratios are useful validation data, not the independent criterion.",
    open: ["City universe, rental unit specification and household scenarios."],
    evidence: [
      ev("OECD HC1.2 is an exact housing-cost-over-income table, but its documentation says total housing costs are available only for European countries and New Zealand.", "https://webfs.oecd.org/Els-com/Affordable_Housing_Database/HC1-2-Housing-costs-over-income.pdf"),
      ev("The Affordable Housing Database is explicitly OECD/EU/key-partner focused.", "https://www.oecd.org/en/data/datasets/oecd-affordable-housing-database.html")
    ]
  },
  {
    rank: 7, id: "C50", name: "Healthcare system capacity and quality",
    category: "Safety, health and public services", tags: ["IC","DO"],
    granularity: "NATIONAL", pillars: ["SAFETY_AND_HEALTH"],
    question: "How capable is the national health system of delivering broad essential care, acknowledging that migrant eligibility may differ?",
    definition: "UHC service coverage index as a national capacity/access proxy; it does not directly measure migrant entitlement, waiting times or care experience.",
    profiles: ["all movers", "families", "people with chronic conditions"], value: 5, dependence: "MODERATE",
    status: "DEFERRED", freshness: "SLOW_STRUCTURAL",
    coverage: cov("FULL", true, 91, 0, 0, 91),
    observation: "National composite using reported and modelled tracer indicators",
    sources: [
      src("C50-WB-HNP-UHC", "World Bank (distribution) / WHO (upstream)", "Health Nutrition and Population Statistics", "SH.UHC.SRVS.CV.XD", "https://api.worldbank.org/v2/country/all/indicator/SH.UHC.SRVS.CV.XD?source=16&format=json", "https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SH.UHC.SRVS.CV.XD", "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C4","M3"], "MEASURED", "World Bank source 16; latest 2021"),
      src("C50-WHO-UHC-2025", "World Health Organization / World Bank", "Tracking UHC 2025 full dataset", "UHC service coverage index, 2023", "https://www.who.int/data/uhc-2025-technical-appendices-and-regional-data-tables", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/uhc-index-of-service-coverage", "https://www.who.int/about/policies/publishing/copyright", ["A4","L1","C4","M3"], "VERIFIED", "2025 release; 2023 reference")
    ],
    scoring: score("HIGHER_BETTER", "S4", "Use the published 0–100 index directly after freshness and licence gates."),
    comp: ["The index is a geometric mean of 14 tracers; not every tracer directly measures service coverage.", "National population coverage does not establish migrant entitlement or local access."],
    mapping: ["World Bank representation maps cleanly to ISO3."],
    licensing: ["World Bank representation is CC BY 4.0; direct WHO commercial reuse requires permission or a dataset-specific compatible licence."],
    redundancy: ["C56"],
    maintenance: ["Monitor for the 2023 WHO revision to enter a production-compatible World Bank distribution and for methodology breaks."],
    blockers: ["FRS_STALE"],
    caveats: ["SEM_QUESTION_TOO_BROAD","CMP_IMPUTED_VALUES_REQUIRED","LIC_NONCOMMERCIAL_ONLY"],
    recommendation: "Defer now. The reusable World Bank representation is complete but remains at 2021; the fresh 2023 WHO release has unresolved commercial reuse for direct ingestion.",
    open: ["When will the World Bank CC BY representation refresh to the revised 2023 series?"],
    evidence: [
      ev("The current World Bank HNP API returned 91/91 stable countries, all with latest year 2021.", "https://api.worldbank.org/v2/country/all/indicator/SH.UHC.SRVS.CV.XD?source=16&format=json", "MEASURED"),
      ev("The 2025 global monitoring release reports the UHC service coverage index through 2023.", "https://www.worldbank.org/en/topic/universalhealthcoverage/publication/2025-global-monitoring-report-gmr"),
      ev("WHO requires permission for commercial use of WHO materials absent a more specific licence.", "https://www.who.int/about/policies/publishing/copyright")
    ]
  },
  {
    rank: 8, id: "C40", name: "English usability",
    category: "Language, culture and integration", tags: ["IC","CR"],
    granularity: "CITY_OR_REGIONAL", pillars: ["INTEGRATION"],
    question: "How easily can an English-speaking newcomer handle work, services and daily life in the specific destination?",
    definition: "A local usability concept combining institutional language availability and population proficiency; national adult test scores are only a weak proxy.",
    profiles: ["English-speaking movers"], value: 4, dependence: "HIGH",
    status: "DEFERRED_CITY_LAYER", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("MEDIUM", false),
    observation: "Self-selected online assessment; city/regional cuts",
    sources: [
      src("C40-EF-EPI-2025", "EF Education First", "EF English Proficiency Index 2025", "Country, region and city scores", "https://www.ef.com/wwen/epi/", "https://www.ef.com/wwen/epi/about-epi/", null, ["A2","L1","C2","M2"], "VERIFIED", "2025")
    ],
    scoring: score("HIGHER_BETTER", "S2", "No independent score until native-English destinations and institutional usability have equivalent measures."),
    comp: ["EF test takers are self-selected, young-skewed and internet-only.", "Adult proficiency is not the same as service or workplace usability; native-English destinations are not symmetrically observed."],
    mapping: ["EF includes countries/regions and thresholded cities; stable-country and native-language exceptions require policy."],
    licensing: ["Raw data are not prepared for external sharing; no dataset-specific production licence was verified."],
    redundancy: ["C32"],
    maintenance: ["Annual edition changes and city sample thresholds create unstable coverage."],
    blockers: ["LIC_NO_EVIDENCE","CMP_SURVEY_NOT_HARMONISED","GRA_CITY_LEVEL_REQUIRED","SCO_SAMPLE_RELATIVE_DISTORTION"],
    caveats: ["COV_MISSING_KEY_DESTINATIONS","SEM_QUESTION_TOO_BROAD"],
    recommendation: "Defer to a city/preference layer. Do not use EF EPI as a production country criterion.",
    open: ["Whether English usability should be a user preference/filter rather than a ranked criterion."],
    evidence: [
      ev("EF EPI 2025 uses more than 2.2 million 2024 test takers, but the sample is self-selected and not guaranteed representative.", "https://www.ef.com/wwen/epi/about-epi/"),
      ev("EF states that its raw source data are not prepared for sharing outside the organisation.", "https://www.ef.com/wwen/epi/about-epi/")
    ]
  },
  {
    rank: 9, id: "C01", name: "Overall higher-education opportunity",
    category: "Education and human capital", tags: ["IC"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["WORK_AND_STUDY"],
    question: "How broad is access to tertiary education in the destination, before institution, field, tuition and international-student constraints?",
    definition: "Gross tertiary enrolment ratio as a national participation proxy; it is not a university-quality or migrant-access measure.",
    profiles: ["students", "families with older children"], value: 4, dependence: "HIGH",
    status: "EXPERIMENTAL_CANDIDATE", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("HIGH", true, 88, 77, 3, 88),
    observation: "National administrative education statistics",
    sources: [
      src("C01-WDI-TER", "World Bank (distribution) / UNESCO UIS (upstream)", "World Development Indicators", "SE.TER.ENRR", "https://api.worldbank.org/v2/country/all/indicator/SE.TER.ENRR?format=json", "https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SE.TER.ENRR", "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C4","M3"], "MEASURED", "UIS Feb. 2026 release")
    ],
    scoring: score("HIGHER_BETTER", "S2", "Robust percentile only as tertiary participation; do not label it quality or international-student opportunity."),
    comp: ["Gross enrolment can exceed 100 and reflects system participation, not teaching quality, places for foreigners, tuition or field availability."],
    mapping: ["ISO3 mapping is clean; small states have sparse updates."],
    licensing: ["World Bank representation is CC BY 4.0; direct UIS browser data are CC BY-SA 4.0."],
    redundancy: ["C08"],
    maintenance: ["Annual UIS/WDI release; pin extraction date and latest-observation rule."],
    blockers: ["COV_BELOW_90_PERCENT"],
    caveats: ["SEM_QUESTION_TOO_BROAD","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Experimental/recovery probe only. Overall coverage is 88/91, but only 77/91 have 2023+ data and 81/91 have 2021+ data.",
    open: ["Can a second UIS participation/completion series recover at least 82 fresh countries without changing semantics?"],
    evidence: [
      ev("The WDI API returned 88/91 with any 2010–2025 value, 81/91 at 2021+, and 77/91 at 2023+.", "https://api.worldbank.org/v2/country/all/indicator/SE.TER.ENRR?format=json", "MEASURED"),
      ev("WDI metadata identifies UIS as upstream, annual periodicity and CC BY 4.0.", "https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SE.TER.ENRR")
    ],
    shortlist: "CONDITIONAL", shortlistRank: 5
  },
  {
    rank: 10, id: "C30", name: "Existing immigrant share",
    category: "Migration, visa and settlement", tags: ["IC"],
    granularity: "NATIONAL", pillars: ["INTEGRATION"],
    question: "How established is international migration in the destination, as indicated by the foreign-born share of residents?",
    definition: "International migrant stock as a percentage of total population, using UN Population Division estimates distributed by WDI.",
    profiles: ["all international movers"], value: 4, dependence: "NONE",
    status: "PROBE_APPROVED", freshness: "SLOW_STRUCTURAL",
    coverage: cov("FULL", true, 91, 91, 0, 91),
    observation: "National stock estimate from censuses, registers, surveys and imputation",
    sources: [
      src("C30-WDI-MIGRANT", "World Bank (distribution) / UN Population Division (upstream)", "World Development Indicators", "SM.POP.TOTL.ZS", "https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL.ZS?format=json", "https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SM.POP.TOTL", "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C4","M3"], "MEASURED", "2024")
    ],
    scoring: score("HIGHER_BETTER", "S3", "Logit-transform percentage, winsorise, then robust percentile; keep interpretation as established migrant presence, not friendliness."),
    comp: ["Foreign-born is used where possible; citizenship is substituted in some countries and missing countries are imputed.", "Stock reflects history and geography, not current visa openness or lived inclusion."],
    mapping: ["WDI ISO3 mapping is deterministic; country breakups create historical discontinuities."],
    licensing: ["The exact WDI representation is CC BY 4.0, avoiding restrictive generic UN website terms."],
    redundancy: ["C32","C33"],
    maintenance: ["Slow-moving; pin UN revision and WDI release."],
    blockers: [],
    caveats: ["CMP_IMPUTED_VALUES_REQUIRED","CMP_DEFINITION_DIFFERS","SEM_CAUSALITY_OVERCLAIM"],
    recommendation: "Proceed to deterministic Phase 3E probe; measured current coverage is 91/91.",
    open: ["Whether scoring should be higher-better or informational/preference based."],
    evidence: [
      ev("The WDI API returned 2024 observations for all 91 stable countries.", "https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL.ZS?format=json", "MEASURED"),
      ev("WDI metadata identifies UN Population Division as publisher, describes census/register/survey inputs and imputation, and assigns CC BY 4.0.", "https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SM.POP.TOTL")
    ],
    shortlist: "DETERMINISTIC", shortlistRank: 1
  },
  {
    rank: 11, id: "C12", name: "Software and technology jobs",
    category: "Employment, income and economic opportunity", tags: ["IC","SC","CR"],
    granularity: "CITY_OR_REGIONAL", pillars: ["WORK_AND_STUDY"],
    question: "How large and accessible is the software/technology employment market in the relevant city for the user's occupation?",
    definition: "Employment in selected ISCO-08 two-digit ICT-related occupations as a national proxy; vacancies and city concentration remain unmeasured.",
    profiles: ["software professionals", "ICT technicians"], value: 5, dependence: "HIGH",
    status: "DEFERRED_CITY_LAYER", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("MEDIUM", true, 66, 66, 25, 66),
    observation: "National labour-force survey occupation counts",
    sources: [
      src("C12-ILO-ISCO2", "International Labour Organization (ILOSTAT)", "ILOSTAT bulk download", "EMP_TEMP_SEX_OC2_NB_A; ISCO-08 level 2", "https://rplumber.ilo.org/data/indicator/", "https://ilostat.ilo.org/about/get-started/", "https://www.ilo.org/rights-and-permissions", ["A4","L4","C3","M3"], "MEASURED", "accessed 2026-07-24")
    ],
    scoring: score("HIGHER_BETTER", "S2", "Selected ICT occupation employment divided by total employment; experimental only after occupation-code review."),
    comp: ["Two-digit occupation groups are broader than software jobs and miss tech-industry roles outside selected occupations.", "National employment stocks do not measure vacancies, hiring friction or city clusters."],
    mapping: ["ISO3 is deterministic; ISCO version and occupation-code mapping require version controls."],
    licensing: ["ILOSTAT data are CC BY 4.0."],
    redundancy: ["C11","C17"],
    maintenance: ["ISCO revisions, survey breaks and city labour-market sourcing would be substantial."],
    blockers: ["COV_BELOW_90_PERCENT","GRA_CITY_LEVEL_REQUIRED","GRA_PROFESSION_SPECIFIC"],
    caveats: ["CMP_DEFINITION_DIFFERS","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Defer to a city/occupation layer. Recent two-digit occupation data cover only 66/91 and remain semantically too broad.",
    open: ["Whether to define tech by occupation, industry, vacancies, or a hybrid."],
    evidence: [
      ev("EMP_TEMP_SEX_OC2_NB_A had 2023+ observations for 66/91 stable countries.", "https://rplumber.ilo.org/data/indicator/", "MEASURED"),
      ev("ILOSTAT exposes occupation data only up to ISCO two-digit level in the relevant public table family.", "https://ilostat.ilo.org/about/get-started/")
    ]
  },
  {
    rank: 12, id: "C58", name: "Internet access, speed, and reliability",
    category: "Infrastructure and daily-life reliability", tags: ["IC","SC","DO"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["DAILY_RELIABILITY"],
    question: "Can a newcomer expect affordable, fast and dependable connectivity where they live and work?",
    definition: "Current reusable sources support national internet use and fixed-broadband penetration, not a complete speed/reliability measure.",
    profiles: ["remote workers", "students", "all households"], value: 5, dependence: "MODERATE",
    status: "EXPERIMENTAL_CANDIDATE", freshness: "FAST_MOVING",
    coverage: cov("FULL", true, 91, 91, 0, 91),
    observation: "National household/administrative indicators; composite proxy",
    sources: [
      src("C58-WDI-ICT", "World Bank (distribution) / ITU (upstream)", "World Development Indicators", "IT.NET.USER.ZS; IT.NET.BBND.P2", "https://api.worldbank.org/v2/country/all/indicator/IT.NET.USER.ZS?format=json", "https://beta.datahub.itu.int/about/", "https://data.worldbank.org/summary-terms-of-use", ["A4","L4","C4","M3"], "MEASURED", "WDI 2026-07-13 snapshot"),
      src("C58-ITU-DIRECT", "International Telecommunication Union", "ITU DataHub", "Internet, broadband and quality-of-service indicators", "https://datahub.itu.int/", "https://beta.datahub.itu.int/about/", "https://beta.datahub.itu.int/about/", ["A4","L1","C4","M3"], "VERIFIED", "regular updates")
    ],
    scoring: score("HIGHER_BETTER", "S3", "Experimental access/penetration composite only; do not label it speed and reliability."),
    comp: ["Internet use and fixed-broadband subscriptions are comparable but are not throughput, latency, outages or affordability."],
    mapping: ["WDI ISO3 mapping is already validated in the repository."],
    licensing: ["WDI representations are CC BY 4.0; direct ITU DataHub is CC BY-NC-SA 3.0 IGO and unsuitable for commercial production."],
    redundancy: ["C56"],
    maintenance: ["Annual WDI refresh is manageable; a true speed/reliability source would require faster updates and city/geospatial policy."],
    blockers: [],
    caveats: ["SEM_QUESTION_TOO_BROAD","RED_EXISTING_CRITERION","RED_SHARED_COMPONENTS","LIC_NONCOMMERCIAL_ONLY"],
    recommendation: "Experimental/redundancy probe only for a narrowed access-and-penetration criterion. Do not claim speed or reliability.",
    open: ["Whether this adds value beyond the existing infrastructure experiment and whether speed should be city-level."],
    evidence: [
      ev("The repository's existing source audit measured both WDI components at 91/91; latest internet-use observations were 2024–25 and fixed broadband 2023–24.", "../docs/data/source-audit.md", "MEASURED"),
      ev("ITU DataHub describes about 200 economies and direct data under CC BY-NC-SA 3.0 IGO.", "https://beta.datahub.itu.int/about/")
    ],
    shortlist: "CONDITIONAL", shortlistRank: 6
  },
  {
    rank: 13, id: "C56", name: "Electricity access and reliability",
    category: "Infrastructure and daily-life reliability", tags: ["IC","SC","DO"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["DAILY_RELIABILITY"],
    question: "Can a household and workplace expect continuous electricity service, not merely a grid connection?",
    definition: "Electricity-access percentage plus an outage/reliability outcome; only access currently meets global coverage.",
    profiles: ["remote workers", "business owners", "all households"], value: 5, dependence: "MODERATE",
    status: "DEFERRED", freshness: "STANDARD_SOCIOECONOMIC",
    coverage: cov("UNKNOWN", true, 0, 0, 91, 0),
    observation: "National access estimate plus firm-survey outage data",
    sources: [
      src("C56-WDI-ACCESS", "World Bank / WHO-UNICEF tracking partners", "World Development Indicators", "EG.ELC.ACCS.ZS", "https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json", "https://databank.worldbank.org/metadataglossary/jobs/series/EG.ELC.ACCS.ZS", "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C4","M3"], "MEASURED", "2024"),
      src("C56-WB-OUTAGES", "World Bank Enterprise Surveys", "Enterprise Surveys / WDI metadata", "IC.ELC.OUTG", "https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IC.ELC.OUTG", null, "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C2","M3"], "MEASURED")
    ],
    scoring: score("HIGHER_BETTER", "S2", "Access higher-better and outages lower-better; no combined score until reliability clears coverage."),
    comp: ["Access is near-ceiling in much of the stable universe and is not reliability.", "Enterprise Survey outages reflect sampled firms, subnational survey locations and heterogeneous survey years."],
    mapping: ["ISO3 is straightforward; subnational survey strata do not map to a national lived-experience claim."],
    licensing: ["World Bank series are CC BY 4.0."],
    redundancy: ["C58"],
    maintenance: ["Reliability requires survey-year and coverage controls; access alone adds little differentiation."],
    blockers: ["COV_BELOW_90_PERCENT","SEM_QUESTION_TOO_BROAD"],
    caveats: ["CMP_SURVEY_NOT_HARMONISED","FRS_MIXED_REFERENCE_PERIODS","RED_SHARED_COMPONENTS"],
    recommendation: "Defer. Access measured 91/91 for 2024, but the WDI API returned no observations for IC.ELC.OUTG; access alone does not answer reliability.",
    open: ["A global reusable SAIDI/SAIFI or household-outage source with 82+ stable-country coverage."],
    evidence: [
      ev("EG.ELC.ACCS.ZS returned 2024 observations for all 91 stable countries.", "https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json", "MEASURED"),
      ev("The current WDI API query for IC.ELC.OUTG returned zero stable-country observations.", "https://api.worldbank.org/v2/country/all/indicator/IC.ELC.OUTG?format=json", "MEASURED")
    ]
  },
  {
    rank: 14, id: "C08", name: "School education quality",
    category: "Education and human capital", tags: ["IC"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["WORK_AND_STUDY"],
    question: "How much effective learning does the national school system produce for a child, before local school choice?",
    definition: "HCI+ harmonized learning outcomes and learning-adjusted years of schooling, used as national outcome measures.",
    profiles: ["families with children"], value: 5, dependence: "MODERATE",
    status: "PROBE_APPROVED", freshness: "SLOW_STRUCTURAL",
    coverage: cov("HIGH", true, 89, 88, 2, 89),
    observation: "National composite/modelled harmonisation of assessments and schooling",
    sources: [
      src("C08-HCIPLUS", "World Bank", "Human Capital Index Plus", "hlo_mf; lays_mf; hcip_schooling_component_mf in hci_plus_index_panel.dta", "https://datacatalog.worldbank.org/search/dataset/0067030/human-capital-index-plus", "https://humancapital.worldbank.org/hciplus/methodology/", "https://datacatalog.worldbank.org/int/public-licenses#cc-by", ["A4","L4","C4","M3"], "MEASURED", "version 3; file updated 2026-02-11")
    ],
    scoring: score("HIGHER_BETTER", "S4", "Prefer the published schooling component or learning-adjusted years; test sensitivity against HLO alone."),
    comp: ["Harmonized learning outcomes bridge different assessments through a common scale and modelling.", "National averages mask region, school sector, language and migrant-child access."],
    mapping: ["ISO3 mapping was deterministic; BHS and BOL lacked the tested schooling/learning fields."],
    licensing: ["Dataset catalogue assigns CC BY 4.0."],
    redundancy: ["C01"],
    maintenance: ["Pin HCI+ version and clarify whether file year 2025 is an estimate; catalogue temporal metadata says 2009–2024 while the file contains 2025 labels."],
    blockers: ["COV_NOT_FULL_91"],
    caveats: ["CMP_MODEL_ASSUMPTIONS_OPAQUE","FRS_MIXED_REFERENCE_PERIODS"],
    recommendation: "Proceed to deterministic Phase 3E probe; measured field coverage is 89/91 and the source is current, official and reusable.",
    open: ["Use the schooling component, LAYS, or HLO as the primary score?", "Resolve the catalogue/file year-label discrepancy."],
    evidence: [
      ev("The downloaded HCI+ panel contained 89/91 stable countries for HLO/LAYS; BHS and BOL were missing. Eighty-eight had latest labels at 2024+ for HLO/LAYS.", "https://datacatalogfiles.worldbank.org/ddh-published/0067030/DR0095876/hci_plus_index_panel.dta", "MEASURED"),
      ev("The catalogue states 166-country coverage, national granularity, file update 11 February 2026 and CC BY 4.0.", "https://datacatalog.worldbank.org/search/dataset/0067030/human-capital-index-plus")
    ],
    shortlist: "DETERMINISTIC", shortlistRank: 3
  },
  {
    rank: 15, id: "C66", name: "Extreme-weather risk",
    category: "Climate, environment and location", tags: ["IC","SC","DO"],
    granularity: "NATIONAL_WITH_CITY_CAVEAT", pillars: ["ENVIRONMENT_AND_LIFESTYLE","SAFETY_AND_HEALTH"],
    question: "How exposed is the destination to severe weather-related hazards that could disrupt life, property and services?",
    definition: "A transparent subset of INFORM 2026 hazard scores: river flood, tropical cyclone, coastal flood and drought; earthquakes, tsunamis, epidemics and conflict are excluded.",
    profiles: ["all movers", "home buyers", "climate-sensitive households"], value: 4, dependence: "MODERATE",
    status: "EXPERIMENTAL_CANDIDATE", freshness: "EVENT_RISK_MODEL",
    coverage: cov("FULL", true, 91, 91, 0, 91),
    observation: "National multi-source hazard/exposure composite",
    sources: [
      src("C66-INFORM-2026", "European Commission JRC / INFORM partners", "INFORM Risk Index 2026", "INFORM_Risk_2026_v072.xlsx: River Flood, Tropical Cyclone, Coastal flood, Drought", "https://drmkc.jrc.ec.europa.eu/inform-index/Portals/0/InfoRM/2026/INFORM_Risk_2026_v072.xlsx", "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology", "https://commission.europa.eu/legal-notice_en", ["A4","L3","C4","M3"], "MEASURED", "INFORM Risk 2026 v072")
    ],
    scoring: score("LOWER_BETTER", "S2", "Experimental maximum or weighted mean of the four published 0–10 hazards; publish sensitivity and avoid calling it the official INFORM Natural score."),
    comp: ["The official Natural score also includes geophysical and epidemic hazards, so it is semantically too broad.", "The selected subset omits heatwaves, wildfire, severe convective storms and local adaptation."],
    mapping: ["All 91 stable ISO3 codes mapped and had values in each selected field."],
    licensing: ["INFORM calls results open; EC-owned site content defaults to CC BY 4.0, but workbook source-data chains require a dataset-specific third-party-rights check before production."],
    redundancy: [],
    maintenance: ["Pin workbook version and component names; monitor annual methodology changes."],
    blockers: [],
    caveats: ["SCO_COMPOSITE_WEIGHTS_ARBITRARY","LIC_SOURCE_CHAIN_UNCLEAR","SEM_QUESTION_TOO_BROAD"],
    recommendation: "Experimental Phase 3E probe only. Coverage is complete, but a Konsider-specific weather subset and weighting need defensibility testing.",
    open: ["Maximum versus mean aggregation", "Whether heatwave and wildfire omissions are acceptable", "Confirm workbook-level reuse and upstream source chain."],
    evidence: [
      ev("The downloaded INFORM Risk 2026 v072 workbook mapped all 91 stable ISO3 codes and had non-null River Flood, Tropical Cyclone, Coastal flood and Drought scores for every country.", "https://drmkc.jrc.ec.europa.eu/inform-index/Portals/0/InfoRM/2026/INFORM_Risk_2026_v072.xlsx", "MEASURED"),
      ev("INFORM describes the index as global and open and publishes the workbook with source data and calculation steps.", "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Results-and-data/moduleId/1782/id/453/controller/Admin/a"),
      ev("EC-owned website content is CC BY 4.0 unless otherwise indicated, with third-party-rights caveats.", "https://commission.europa.eu/legal-notice_en")
    ],
    shortlist: "CONDITIONAL", shortlistRank: 4
  }
];

function record(s) {
  return {
    ...common,
    criterion_id: s.id, name: s.name, category: s.category,
    description: s.definition, classification_tags: s.tags,
    natural_granularity: s.granularity, decision_pillars: s.pillars,
    relocation_question: s.question, definition: s.definition,
    target_profiles: s.profiles, decision_value: s.value,
    profile_dependence: s.dependence, research_rank: s.rank,
    research_priority_score: null, status: s.status,
    freshness_class: s.freshness, coverage: s.coverage,
    source_candidates: s.sources, scoring: s.scoring,
    comparability_notes: s.comp, country_mapping_notes: s.mapping,
    licensing_notes: s.licensing, redundancy_links: s.redundancy,
    maintenance_notes: s.maintenance, blocker_codes: s.blockers,
    caveat_codes: s.caveats, recommendation: s.recommendation,
    open_questions: s.open, evidence: s.evidence
  };
}

const records = specs.map(record);
const shortlist = specs.filter(x => x.shortlist).sort((a,b) => a.shortlistRank-b.shortlistRank).map(x => ({
  rank: x.shortlistRank, criterion_id: x.id, name: x.name, track: x.shortlist,
  status: x.status, rationale: x.recommendation
}));

const output = {
  phase_id: "3C",
  batch_id: "PHASE3C_BATCH1_2026-07-24",
  evidence_cutoff: "2026-07-24",
  universe_id: U,
  denominator: 91,
  evidence_labels: {
    VERIFIED: "Confirmed from an identified source page, metadata record or exact dataset documentation.",
    MEASURED: "The exact source was downloaded or queried and joined to the stable 91-country universe.",
    ESTIMATED: "Phase 3C analyst judgement; not a completed coverage or licensing audit.",
    HYPOTHESIS: "Candidate requiring discovery or confirmation."
  },
  decision_summary: {
    deterministic_probe: ["C30","C11","C08"],
    conditional_experimental_or_recovery_probe: ["C66","C01","C58"],
    deferred_or_special_layer: ["C32","C33","C17","C21","C25","C50","C40","C12","C56"]
  },
  phase3e_shortlist: shortlist,
  records
};

const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
const csvHeaders = ["rank","criterion_id","name","status","recommendation_track","natural_granularity","observation_type","coverage_measured","found","fresh","coverage_summary","primary_source","series_or_table","authority","licence","comparability","mapping","scoring","blocker_codes","caveat_codes","recommendation"];
const csvRows = specs.map(s => {
  const p = s.sources[0];
  const track = s.shortlist || "NO_FURTHER_PHASE3E_WORK";
  return [s.rank,s.id,s.name,s.status,track,s.granularity,s.observation,s.coverage.measured,s.coverage.found,s.coverage.fresh,
    s.coverage.measured ? `${s.coverage.found ?? 0}/91 measured; ${s.coverage.fresh ?? "n/a"} fresh` : `${s.coverage.expected_band} estimated`,
    `${p.publisher} — ${p.dataset}`,p.series_or_table,p.authority_grade,p.licence_grade,p.comparability_grade,p.mapping_grade,
    `${s.scoring.mode}/${s.scoring.grade}`,s.blockers.join(";"),s.caveats.join(";"),s.recommendation].map(esc).join(",");
});

function bullets(a) {
  return a.length ? a.map(x => `- ${x}`).join("\n") : "- None.";
}

function coverageText(s) {
  if (!s.coverage.measured) return `**ESTIMATED:** ${s.coverage.expected_band}; no source query/download was used to count stable countries.`;
  return `**MEASURED:** ${s.coverage.found}/91 found; ${s.coverage.fresh ?? "not separately assessed"}/91 fresh under the stated criterion rule; ${s.coverage.missing ?? "unknown"} missing.`;
}

function criterionMd(s) {
  return `# ${s.id} — ${s.name}

## Decision summary

- Status: \`${s.status}\`
- Recommendation: ${s.recommendation}
- Evidence cutoff: 2026-07-24
- Primary blocker codes: ${s.blockers.length ? s.blockers.map(x=>`\`${x}\``).join(", ") : "none"}
- Caveat codes: ${s.caveats.length ? s.caveats.map(x=>`\`${x}\``).join(", ") : "none"}

## 1. Relocation question

${s.question}

## 2. Precise definition

${s.definition}

## 3. Classification and granularity

Tags: ${s.tags.join(", ")}. Natural granularity: **${s.granularity}**. Observation type: ${s.observation}.

## 4. User profiles and decision value

Profiles: ${s.profiles.join(", ")}. Decision value: ${s.value}/5. Profile dependence: ${s.dependence}.

## 5. Source candidates

${s.sources.map((x,i)=>`### ${i+1}. ${x.publisher} — ${x.dataset}

- Exact series/table: ${x.series_or_table || "Not yet identified"}
- Version: ${x.version || "Not pinned"}
- Access: ${x.access_url ? `[source](${x.access_url})` : "No single global endpoint"}
- Methodology: ${x.methodology_url ? `[methodology](${x.methodology_url})` : "Not independently located"}
- Licence evidence: ${x.licence_url ? `[reuse terms](${x.licence_url})` : "No dataset-specific evidence verified"}
- Grades: authority ${x.authority_grade}; licence ${x.licence_grade}; comparability ${x.comparability_grade}; mapping ${x.mapping_grade}
- Evidence level: **${x.evidence_level}**`).join("\n\n")}

## 6. Comparability assessment

${bullets(s.comp)}

## 7. Expected or measured 91-country coverage

${coverageText(s)}

## 8. Freshness assessment

Class: \`${s.freshness}\`. ${s.maintenance[0]}

## 9. Country mapping and territory policy

${bullets(s.mapping)}

## 10. Scoring options and sensitivity risks

- Mode/grade: \`${s.scoring.mode}\` / \`${s.scoring.grade}\`
- Proposed method: ${s.scoring.proposed_method}
- Sensitivity required: ${s.scoring.sensitivity_required ? "yes" : "no"}

## 11. Redundancy and composite risks

Links: ${s.redundancy.length ? s.redundancy.join(", ") : "none identified"}. ${s.caveats.filter(x=>x.startsWith("RED_")||x.startsWith("SCO_")).join("; ") || "No additional coded risk."}

## 12. Retrieval, replay and maintenance

${bullets(s.maintenance)}

## 13. Blockers, caveats and reason codes

- Blockers: ${s.blockers.length ? s.blockers.join(", ") : "none"}
- Caveats: ${s.caveats.length ? s.caveats.join(", ") : "none"}

## 14. Recommendation

${s.recommendation}

## 15. Open questions

${bullets(s.open)}

## Evidence register

${s.evidence.map(e=>`- **${e.evidence_level}:** ${e.claim} [Evidence](${e.source})${e.notes ? ` — ${e.notes}` : ""}`).join("\n")}
`;
}

const table = specs.map(s => {
  const c = s.coverage.measured ? `${s.coverage.found}/91 measured; ${s.coverage.fresh ?? "n/a"} fresh` : `${s.coverage.expected_band} estimated`;
  return `| ${s.rank} | ${s.id} | ${s.status} | ${s.granularity} | ${c} | ${s.sources[0].authority_grade}/${s.sources[0].licence_grade}/${s.sources[0].comparability_grade}/${s.scoring.grade} | ${s.shortlist || "No further 3E work"} |`;
}).join("\n");

const md = `# Konsider Phase 3C — Batch 1 source-feasibility research

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
${table}

## Phase 3E shortlist

${shortlist.map(x=>`${x.rank}. **${x.criterion_id} — ${x.name}** (${x.track.toLowerCase()}): ${x.rationale}`).join("\n")}

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

${specs.map(criterionMd).join("\n---\n\n")}
`;

fs.writeFileSync(path.join(OUT, "phase3c_batch1.json"), JSON.stringify(output, null, 2) + "\n");
fs.writeFileSync(path.join(OUT, "phase3c_batch1.csv"), csvHeaders.map(esc).join(",") + "\n" + csvRows.join("\n") + "\n");
fs.writeFileSync(path.join(OUT, "phase3c_batch1.md"), `${md.trimEnd()}\n`);

// Lightweight local validation against the Phase 3A record schema. This is report QA,
// not production ingestion code.
const schema = JSON.parse(fs.readFileSync(path.join(OUT, "..", "konsider_phase3a", "phase3a_research_record.schema.json"), "utf8"));
function validate(v, s, p = "$") {
  const errors = [];
  const types = Array.isArray(s.type) ? s.type : s.type ? [s.type] : [];
  const actual = v === null ? "null" : Array.isArray(v) ? "array" : Number.isInteger(v) ? "integer" : typeof v === "number" ? "number" : typeof v;
  if (types.length && !types.includes(actual) && !(actual === "integer" && types.includes("number"))) errors.push(`${p}: expected ${types}, got ${actual}`);
  if (s.enum && !s.enum.includes(v)) errors.push(`${p}: invalid enum ${v}`);
  if (typeof v === "string" && s.pattern && !(new RegExp(s.pattern).test(v))) errors.push(`${p}: pattern mismatch`);
  if (typeof v === "string" && s.minLength && v.length < s.minLength) errors.push(`${p}: too short`);
  if (typeof v === "number" && s.minimum != null && v < s.minimum) errors.push(`${p}: below minimum`);
  if (typeof v === "number" && s.maximum != null && v > s.maximum) errors.push(`${p}: above maximum`);
  if (Array.isArray(v)) {
    if (s.uniqueItems && new Set(v.map(JSON.stringify)).size !== v.length) errors.push(`${p}: duplicate array values`);
    if (s.items) v.forEach((x, i) => errors.push(...validate(x, s.items, `${p}[${i}]`)));
  }
  if (v && actual === "object") {
    (s.required || []).forEach(k => { if (!(k in v)) errors.push(`${p}: missing ${k}`); });
    if (s.additionalProperties === false) Object.keys(v).forEach(k => { if (!s.properties[k]) errors.push(`${p}: unexpected ${k}`); });
    Object.entries(s.properties || {}).forEach(([k, child]) => { if (k in v) errors.push(...validate(v[k], child, `${p}.${k}`)); });
  }
  return errors;
}
const validationErrors = records.flatMap((r, i) => validate(r, schema, `records[${i}]`));
if (validationErrors.length) {
  console.error(validationErrors.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`Wrote and schema-validated ${records.length} records; ${shortlist.length} Phase 3E shortlist entries.`);
}
