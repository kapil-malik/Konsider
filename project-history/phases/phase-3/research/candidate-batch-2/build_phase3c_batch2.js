const fs = require("fs");
const path = require("path");

const OUT = __dirname;
const CHECKED = "2026-07-26T00:00:00+05:30";
const UNIVERSE = "stable_supported_v1";

const source = (id, publisher, dataset, series, access, method, licence, version, grades) => ({
  source_candidate_id: id,
  publisher,
  dataset,
  series_or_table: series,
  access_url: access,
  methodology_url: method,
  licence_url: licence,
  version,
  authority_grade: grades[0],
  licence_grade: grades[1],
  comparability_grade: grades[2],
  mapping_grade: grades[3],
  evidence_level: "VERIFIED",
});

const evidence = (claim, url, level = "VERIFIED") => ({
  claim,
  source: url,
  locator: url,
  checked_at: CHECKED,
  evidence_level: level,
});

const coverage = (band, sourceScope, estimate, rationale) => ({
  universe_id: UNIVERSE,
  denominator: 91,
  expected_band: band,
  measured: false,
  found: null,
  fresh: null,
  stable_91_estimate: estimate,
  source_scope: sourceScope,
  rationale,
});

const specs = [
  {
    rank: 1,
    id: "C38",
    name: "Professional-licensing accessibility for immigrants",
    category: "Migration, visa and settlement",
    question: "For a named regulated profession and a person's origin qualification, how difficult is recognition and licensing in the destination?",
    definition: "A profile-derived recognition pathway covering regulator, qualification equivalence, exams, language, supervised practice, cost and expected time.",
    granularity: "PROFILE_ONLY",
    observation: "Profession- and origin-specific administrative/legal rules",
    freshness: "CURRENT_POLICY",
    status: "DEFERRED_PROFILE_LAYER",
    decision: "DEFER",
    coverage: coverage("LOW", "WHO reporting covers 134 countries, but not a comparable licensing score", "Below 82 for the exact construct", "No global dataset codes current recognition requirements across professions and qualification origins."),
    sources: [
      source("C38-WHO-NRI", "World Health Organization", "National Reporting Instrument reports database", "WHO Global Code health-personnel migration reporting", "https://www.who.int/teams/health-workforce/migration/practice/reports-database", "https://www.who.int/publications/i/item/9789240066649", "https://data.who.int/about/data/terms-and-conditions", "Reports and consolidated evidence current through the latest NRI cycle", ["A4", "L4", "C2", "M2"]),
      source("C38-ENIC-NARIC", "European Commission / Council of Europe / UNESCO", "ENIC-NARIC networks", "Country recognition authorities and regulated-profession guidance", "https://www.enic-naric.net/", "https://www.enic-naric.net/page-about-ENIC-NARIC-Networks", "https://commission.europa.eu/legal-notice_en", "Current country pages", ["A4", "L3", "C2", "M2"]),
    ],
    methodology: ["WHO NRI provides a common reporting framework for health-worker mobility, not applicant-level licensing outcomes.", "Recognition depends on profession, regulator, qualification country, curriculum, language and supervised-practice requirements."],
    licensing: ["WHO dataset terms are generally CC BY 4.0 with additional terms; linked national regulator material needs page-specific review.", "ENIC-NARIC is a discovery network, not one reusable harmonised dataset."],
    mapping: ["Country ISO mapping is secondary to profession, regulator and qualification-origin mapping.", "Federal and devolved systems may have multiple competent authorities."],
    scoring: { direction: "PROFILE_DERIVED", grade: "S1", transformation: "Return pathway steps and eligibility flags; do not calculate a destination-only score." },
    overlap: ["C13", "C15", "C32"],
    limitations: ["No global comparable processing-time, exam, fee or success-rate series.", "Health-profession evidence cannot be generalized to engineering, law, teaching or trades."],
    blockers: ["GRA_PROFESSION_SPECIFIC", "GRA_ORIGIN_SPECIFIC", "PRF_PROFILE_ONLY", "SRC_NO_AUTHORITATIVE_GLOBAL_SCORE", "OPS_EXCESSIVE_MANUAL_MAINTENANCE"],
    recommendation: "Defer to a later profile/legal pathway module. A Phase 3E national criterion probe would test the wrong unit of analysis.",
    open: ["Which two or three regulated professions and origin qualifications should define a future pilot?"],
    evidence: [
      evidence("WHO describes its NRI as a common platform for comparable reporting on implementation of the Global Code.", "https://www.who.int/teams/health-workforce/migration/practice/reports-database"),
      evidence("WHO's consolidated health-worker mobility report combines mechanisms and covers 134 countries.", "https://www.who.int/publications/i/item/9789240066649"),
      evidence("No current authoritative global profession-by-origin licensing dataset was verified.", "Phase 3C Batch 2 source search", "ESTIMATED"),
    ],
  },
  {
    rank: 2,
    id: "C35",
    name: "Post-study migration pathway",
    category: "Migration, visa and settlement",
    question: "Given nationality, credential, institution and graduation date, can an international graduate remain, work and transition to longer-term status?",
    definition: "A dated, profile-specific rule assessment for post-study work permission, duration, employer conditions and transition routes.",
    granularity: "PROFILE_ONLY",
    observation: "Administrative/legal policy",
    freshness: "CURRENT_POLICY",
    status: "DEFERRED_PROFILE_LAYER",
    decision: "DEFER",
    coverage: coverage("LOW", "OECD members and 25 EU countries have structured comparative discovery material", "Well below 82 for a maintained exact ruleset", "Outside OECD/EU, national immigration portals must be coded individually."),
    sources: [
      source("C35-OECD-IMO-2025", "OECD", "International Migration Outlook 2025", "Recent post-study and migration-policy changes", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en.html", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", "2025", ["A4", "L4", "C3", "M3"]),
      source("C35-EU-PORTAL", "European Commission", "EU Immigration Portal", "Student and highly-qualified worker country pages", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en", "https://commission.europa.eu/legal-notice_en", "Pages current in 2025; 25 EU countries", ["A4", "L4", "C2", "M3"]),
    ],
    methodology: ["OECD provides current comparative policy narrative but not a global applicant-level eligibility table.", "Rules vary by qualification level, course length, institution recognition, nationality and later job conditions."],
    licensing: ["OECD post-July-2024 content is generally CC BY 4.0 subject to page exceptions.", "Commission-owned portal content is generally CC BY 4.0 under the EC legal notice."],
    mapping: ["Requires credential level, institution status, completion date and nationality in addition to destination.", "Policy-effective dates and transition provisions must be preserved."],
    scoring: { direction: "PROFILE_DERIVED", grade: "S1", transformation: "Eligibility and route timeline, not a universal higher-better national percentile." },
    overlap: ["C01", "C06", "C32", "C33"],
    limitations: ["Published policy changes can precede implementation guidance.", "A long nominal permit may still impose job, salary or sponsorship constraints."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_ORIGIN_SPECIFIC", "PRF_PROFILE_ONLY", "OPS_EXCESSIVE_MANUAL_MAINTENANCE"],
    recommendation: "Defer to the legal/profile layer; retain OECD and the EU portal as discovery and cross-check sources.",
    open: ["Which student nationalities, credential levels and graduation scenarios should a future module support?"],
    evidence: [
      evidence("OECD 2024/2025 migration outlooks describe frequent changes to post-study work and transition policies.", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html"),
      evidence("The EU Immigration Portal's structured category information applies to 25 EU countries.", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/what-category-do-i-fit_en"),
    ],
  },
  {
    rank: 3,
    id: "C36",
    name: "Family reunification support",
    category: "Migration, visa and settlement",
    question: "For a sponsor's status and a named family relationship, can the family member join, work and remain in the destination?",
    definition: "A route-specific legal assessment of eligible relatives, sponsor residence and income conditions, waiting periods, fees and dependant work rights.",
    granularity: "PROFILE_ONLY",
    observation: "Administrative/legal policy",
    freshness: "CURRENT_POLICY",
    status: "DEFERRED_PROFILE_LAYER",
    decision: "DEFER",
    coverage: coverage("LOW", "Structured EC coverage for 25 EU countries; OECD comparative narrative for 38 members", "Below 82 for exact current rules", "Global extension requires maintained national-law coding."),
    sources: [
      source("C36-EU-PORTAL", "European Commission", "EU Immigration Portal", "Family-member country pages", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/already-eu_en", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/legal-migration-and-resettlement/family-reunification-non-eu-nationals_en", "https://commission.europa.eu/legal-notice_en", "Country pages dated 2025; 25 EU countries", ["A4", "L4", "C3", "M3"]),
      source("C36-OECD-IMO-2025", "OECD", "International Migration Outlook 2025", "Recent family-reunification policy changes", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en.html", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", "2025", ["A4", "L4", "C3", "M3"]),
    ],
    methodology: ["EC pages distinguish sponsor status, family relationship and member-state implementation.", "OECD documents changing requirements, demonstrating that a static scalar quickly becomes stale."],
    licensing: ["EC-owned portal content and OECD-owned content have favourable reuse terms, but neither is a global structured rules dataset."],
    mapping: ["Sponsor permit, sponsor nationality, family relationship, dependency, age and applicant nationality change the result."],
    scoring: { direction: "PROFILE_DERIVED", grade: "S1", transformation: "Return eligibility, conditions and dated route facts; avoid ranking family definitions." },
    overlap: ["C32", "C33", "C72"],
    limitations: ["Legal entitlement differs from processing time and practical approval.", "Humanitarian, EU-citizen and third-country sponsor regimes are materially different."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_HOUSEHOLD_SCENARIO_REQUIRED", "GRA_ORIGIN_SPECIFIC", "PRF_PROFILE_ONLY", "OPS_EXCESSIVE_MANUAL_MAINTENANCE"],
    recommendation: "Defer to a family/profile legal module. Do not create an independent national score.",
    open: ["Should spouse/partner, minor children and dependent parents be separate product questions?"],
    evidence: [
      evidence("The Commission states that its family-reunification portal applies to 25 EU countries and national rules may be more favourable.", "https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal/already-eu_en"),
      evidence("OECD reports multiple family-reunification rule changes in 2024-2025.", "https://www.oecd.org/en/publications/international-migration-outlook-2025_ae26c893-en/full-report/recent-developments-in-migration-policy_e3826f20.html"),
    ],
  },
  {
    rank: 4,
    id: "C34",
    name: "Citizenship accessibility",
    category: "Migration, visa and settlement",
    question: "How inclusive is the destination's ordinary residence-based naturalisation law for a settled adult migrant?",
    definition: "A narrow legal-policy construct based on residence naturalisation modes and dual-citizenship restrictions; it excludes administrative discretion and applicant-specific eligibility.",
    granularity: "NATIONAL_WITH_PROFILE_CAVEAT",
    observation: "Expert-coded law in force",
    freshness: "STATIC_OR_LEGAL_ASOF",
    status: "EXPERIMENTAL_CANDIDATE",
    decision: "EXPERIMENTAL_ONLY",
    coverage: coverage("FULL", "GLOBALCIT v3 covers laws in force in 191 states", "At least 90% appears highly plausible", "All stable-universe states are expected to map, but this was not downloaded and joined in Batch 2."),
    sources: [
      source("C34-GLOBALCIT-V3", "European University Institute / GLOBALCIT", "GLOBALCIT Citizenship Law Dataset", "v3.0 country-year-mode acquisition/loss; A06 residence naturalisation and dual-citizenship modes", "https://globalcit.eu/databases/globalcit-citizenship-law-dataset/", "https://cadmus.eui.eu/handle/1814/73190", "https://cadmus.eui.eu/handle/1814/73190", "v3.0; laws in force 2020-2024; 191 states", ["A4", "L4", "C4", "M4"]),
    ],
    methodology: ["The dataset uses a comprehensive typology: 28 acquisition and 15 loss modes with qualitative descriptions and quantitative categories.", "Formal law does not capture discretion, backlogs, residence interruptions, language-test difficulty or approval probability."],
    licensing: ["The EUI repository identifies CC BY 4.0 for the dataset.", "Exact v3 archive and codebook should be captured together in a probe."],
    mapping: ["ISO3 is supplied; historical/predecessor states and non-state economies require exclusion rules.", "Use law-in-force year, not repository publication year."],
    scoring: { direction: "HIGHER_BETTER", grade: "S2", transformation: "Test a transparent small rule set for residence naturalisation and dual citizenship; do not sum all 43 modes." },
    overlap: ["C33"],
    limitations: ["A legal inclusiveness score needs normative weights.", "Ordinary residence naturalisation is only one citizenship route."],
    blockers: ["CMP_LEGAL_NOT_LIVED_OUTCOME", "SCO_NORMATIVE_WEIGHTS_REQUIRED"],
    recommendation: "Run an experimental Phase 3E probe on the exact v3 archive, stable-91 mapping and a deliberately narrow naturalisation-rule subset.",
    open: ["Which A06 conditions are defensibly ordinal, and should dual citizenship be a separate preference flag?"],
    evidence: [
      evidence("GLOBALCIT v3 covers laws in force in 191 states on 1 January 2024 and provides downloadable files.", "https://globalcit.eu/databases/globalcit-citizenship-law-dataset/"),
      evidence("The EUI repository specifies Creative Commons Attribution 4.0.", "https://cadmus.eui.eu/handle/1814/73190"),
    ],
  },
  {
    rank: 5,
    id: "C05",
    name: "Research and innovation ecosystem",
    category: "Education, research and innovation",
    question: "How strong is the destination's national ecosystem for creating, funding and translating research and innovation?",
    definition: "A transparent national innovation measure, preferably using WIPO GII outputs or a small approved subset rather than an opaque Konsider composite.",
    granularity: "NATIONAL_WITH_CITY_CAVEAT",
    observation: "Annual composite of hard, composite and survey indicators",
    freshness: "SLOW_STRUCTURAL",
    status: "EXPERIMENTAL_CANDIDATE",
    decision: "EXPERIMENTAL_ONLY",
    coverage: coverage("HIGH", "GII 2025 ranks 139 economies", "Approximately 82-88 of 91 appears plausible", "Several stable-universe microstates may be outside GII; an exact join is required."),
    sources: [
      source("C05-WIPO-GII-2025", "World Intellectual Property Organization", "Global Innovation Index 2025 database", "Overall score; Innovation Input and Output sub-indices; 78 indicators", "https://www.wipo.int/en/web/global-innovation-index/2025/index", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/copyright.html", "2025; 139 economies", ["A4", "L4", "C3", "M3"]),
      source("C05-WDI-RD", "World Bank / UNESCO UIS", "World Development Indicators", "SP.POP.SCIE.RD.P6 researchers in R&D per million", "https://data.worldbank.org/indicator/SP.POP.SCIE.RD.P6", "https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SP.POP.SCIE.RD.P6", "https://data.worldbank.org/indicator/SP.POP.SCIE.RD.P6", "1996-2024; source published 2025-02", ["A4", "L4", "C3", "M3"]),
    ],
    methodology: ["GII 2025 uses 78 indicators: 63 hard, 10 composite and five survey measures.", "The index applies minimum data-coverage rules, uses the most recent value from a multi-year window and changes some indicators between editions."],
    licensing: ["WIPO states the 2025 work is CC BY 4.0, including commercial adaptation with attribution; third-party-attributed content remains excluded.", "The exact downloadable data workbook should be checked for third-party columns before redistribution."],
    mapping: ["GII uses economies, including some non-sovereign territories; stable-country ISO mapping needs an explicit inclusion policy."],
    scoring: { direction: "HIGHER_BETTER", grade: "S2", transformation: "Prefer a published GII score or published sub-index; test sensitivity and avoid reweighting dozens of inputs." },
    overlap: ["C01", "C16", "C62"],
    limitations: ["National GII obscures research-city clusters.", "Composite inputs overlap governance, education, infrastructure and entrepreneurship criteria."],
    blockers: ["COV_EXACT_JOIN_REQUIRED", "RED_SHARED_COMPONENTS", "SCO_COMPOSITE_SENSITIVITY_REQUIRED"],
    recommendation: "Run a conditional Phase 3E probe to measure stable-91 coverage, capture the exact data licence and compare overall/output-only variants.",
    open: ["Use overall GII, Innovation Output, or a small research-only subset?", "How much overlap with C16 and governance criteria is acceptable?"],
    evidence: [
      evidence("GII 2025 ranks 139 economies and the downloadable model contains 78 indicators.", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/appendix-i-conceptual-and-measurement-framework-of-the-global-innovation-index.html"),
      evidence("WIPO licenses the 2025 publication under CC BY 4.0, subject to third-party content.", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/copyright.html"),
      evidence("The exact stable-91 intersection was not measured in Batch 2.", "Phase 3C Batch 2", "ESTIMATED"),
    ],
  },
  {
    rank: 6,
    id: "C15",
    name: "Engineering and skilled technical jobs",
    category: "Employment, income and economic opportunity",
    question: "How large and accessible is the labour market for a person's engineering or technical specialty in likely destination regions?",
    definition: "Occupation- and region-specific demand, not the national stock of all professionals and technicians.",
    granularity: "CITY_OR_REGIONAL_PROFILE",
    observation: "Labour-force survey occupation stocks; vacancies would be platform/administrative",
    freshness: "FAST_MOVING",
    status: "DEFERRED_CITY_LAYER",
    decision: "DEFER",
    coverage: coverage("MEDIUM", "ILOSTAT has global broad occupation tables; detailed ISCO-08 level 2 coverage is materially smaller", "Below 82 for recent specialty-level data", "Modelled major groups are broad; detailed engineering groups rely on national surveys."),
    sources: [
      source("C15-ILOSTAT-ISCO", "International Labour Organization", "ILOSTAT employment by occupation", "Employment by sex and occupation, ISCO level 2, annual", "https://ilostat.ilo.org/topics/employment/", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-labour-force-statistics/", "https://www.ilo.org/rights-and-permissions", "Latest country survey observations; annual", ["A4", "L4", "C3", "M3"]),
    ],
    methodology: ["ISCO-08 creates an internationally comparable occupational framework.", "Occupation stock is not vacancies, wage opportunity, shortage, migrant access or engineering-specialty demand."],
    licensing: ["ILOSTAT datasets published since 3 May 2023 are generally CC BY 4.0; source microdata are not redistributed."],
    mapping: ["Requires ISCO-08 groups, specialty mapping, region and profession licensing.", "Countries may report different ISCO versions or broad groups."],
    scoring: { direction: "HIGHER_BETTER", grade: "S1", transformation: "No national scoring until a profession and regional demand measure exists." },
    overlap: ["C11", "C12", "C17", "C38"],
    limitations: ["National employment shares can reward mature sectors without indicating openings.", "Engineering projects and jobs are geographically concentrated."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_CITY_LEVEL_REQUIRED", "GRA_PROFESSION_SPECIFIC", "CMP_STOCK_NOT_OPPORTUNITY"],
    recommendation: "Defer. Use ILOSTAT only as contextual sector size in a later occupation/city module.",
    open: ["Which engineering specialties and metros define the first occupational profile?"],
    evidence: [
      evidence("ILOSTAT offers annual ISCO level-2 employment tables and documents ISCO comparability.", "https://ilostat.ilo.org/topics/employment/"),
      evidence("No globally comparable vacancy series at engineering-specialty and city level was verified.", "Phase 3C Batch 2 source search", "ESTIMATED"),
    ],
  },
  {
    rank: 7,
    id: "C13",
    name: "Medical and healthcare jobs",
    category: "Employment, income and economic opportunity",
    question: "For a named health profession and recognised qualification, where are accessible jobs available in the destination?",
    definition: "A profession-specific opportunity measure combining demand, vacancies and licensing eligibility; provider shortages alone are insufficient.",
    granularity: "CITY_OR_REGIONAL_PROFILE",
    observation: "Health-workforce administrative data and labour surveys",
    freshness: "STANDARD_SOCIOECONOMIC",
    status: "DEFERRED_PROFILE_LAYER",
    decision: "DEFER",
    coverage: coverage("MEDIUM", "WHO mobility evidence covers 134 countries; detailed occupational employment is sparser", "Below 82 for accessible jobs", "Health worker density is broad but does not encode licensing or vacancies."),
    sources: [
      source("C13-WHO-NHWA", "World Health Organization", "National Health Workforce Accounts / Global Health Workforce statistics", "Health-worker density and distribution; foreign-trained/foreign-born indicators", "https://www.who.int/data/gho/data/themes/topics/health-workforce", "https://www.who.int/publications/i/item/9789240066649", "https://data.who.int/about/data/terms-and-conditions", "Current WHO workforce releases", ["A4", "L4", "C3", "M3"]),
      source("C13-ILO-CARE", "International Labour Organization", "ILOSTAT worker and sector profiles", "Care employment by occupation, including ISCO level 2", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/", "https://www.ilo.org/rights-and-permissions", "Latest harmonised microdata observations", ["A4", "L4", "C3", "M3"]),
    ],
    methodology: ["WHO/NHWA measures workforce supply and migration, not vacancies accessible to a foreign-qualified applicant.", "ILOSTAT care profiles may estimate missing 4-digit detail using income-group shares, which weakens specialty interpretation."],
    licensing: ["WHO datasets are generally CC BY 4.0 with additional terms; ILOSTAT data are generally CC BY 4.0.", "Licensing is not the principal blocker."],
    mapping: ["Profession, qualification origin, regulator, language, region and public/private employer matter."],
    scoring: { direction: "PROFILE_DERIVED", grade: "S1", transformation: "Do not invert provider density or shortage into job accessibility." },
    overlap: ["C11", "C38", "C50"],
    limitations: ["Shortage may coexist with hiring freezes or licensing barriers.", "Country aggregates obscure rural/urban maldistribution."],
    blockers: ["GRA_PROFESSION_SPECIFIC", "GRA_CITY_LEVEL_REQUIRED", "PRF_PROFILE_ONLY", "CMP_SHORTAGE_NOT_JOB_ACCESS"],
    recommendation: "Defer to a regulated-profession profile module; retain WHO and ILOSTAT as contextual evidence.",
    open: ["Should medicine, nursing and allied health be completely separate profiles?"],
    evidence: [
      evidence("WHO's mobility report covers 134 countries through multiple reporting mechanisms.", "https://www.who.int/publications/i/item/9789240066649"),
      evidence("ILOSTAT care profiles are derived from harmonised microdata and may estimate detailed categories.", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-worker-and-sector-profiles/"),
    ],
  },
  {
    rank: 8,
    id: "C14",
    name: "Business, finance, and professional-services jobs",
    category: "Employment, income and economic opportunity",
    question: "How strong is demand for the user's business, finance or professional-services occupation in likely destination cities?",
    definition: "Occupation- and city-specific opportunity; national professional employment stock is only background context.",
    granularity: "CITY_OR_REGIONAL_PROFILE",
    observation: "Labour-force survey occupation/industry stocks",
    freshness: "FAST_MOVING",
    status: "DEFERRED_CITY_LAYER",
    decision: "DEFER",
    coverage: coverage("MEDIUM", "ILOSTAT broad occupation and industry data are global, detailed intersections are sparse", "Below 82 for recent exact construct", "Business/finance is not one ISCO major group and city demand is unavailable globally."),
    sources: [
      source("C14-ILOSTAT-ISCO-ISIC", "International Labour Organization", "ILOSTAT employment tables", "Employment by occupation and economic activity, annual", "https://ilostat.ilo.org/topics/employment/", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-labour-force-statistics/", "https://www.ilo.org/rights-and-permissions", "Latest annual national observations", ["A4", "L4", "C3", "M3"]),
    ],
    methodology: ["ISCO and ISIC support harmonised broad classifications.", "Crossing occupation and industry substantially reduces coverage and still measures incumbents, not openings."],
    licensing: ["ILOSTAT reuse terms are favourable; no global official vacancy dataset was identified."],
    mapping: ["Requires occupation, industry and metropolitan-area mappings.", "Professional licensing applies to some finance, accounting and legal roles."],
    scoring: { direction: "HIGHER_BETTER", grade: "S1", transformation: "No independent national score; later use vacancy rates or occupation-adjusted demand." },
    overlap: ["C11", "C12", "C17"],
    limitations: ["Jobs cluster in financial and corporate centres.", "A large sector can have weak current hiring."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_CITY_LEVEL_REQUIRED", "GRA_PROFESSION_SPECIFIC", "CMP_STOCK_NOT_OPPORTUNITY"],
    recommendation: "Defer to the occupation/city layer.",
    open: ["Which ISCO occupations and business centres should define an eventual pilot?"],
    evidence: [
      evidence("ILOSTAT exposes occupation, economic-activity and combined employment tables.", "https://ilostat.ilo.org/topics/employment/"),
      evidence("No authoritative global city vacancy source with production-compatible reuse was verified.", "Phase 3C Batch 2 source search", "ESTIMATED"),
    ],
  },
  {
    rank: 9,
    id: "C16",
    name: "Entrepreneurship and startup opportunity",
    category: "Employment, income and economic opportunity",
    question: "How active is formal new-firm creation in the destination, as a narrow signal of entrepreneurial opportunity?",
    definition: "New limited-liability business registrations per 1,000 working-age people; it does not claim startup survival, funding or immigrant eligibility.",
    granularity: "NATIONAL_WITH_CITY_CAVEAT",
    observation: "Administrative business-registry data",
    freshness: "STANDARD_SOCIOECONOMIC",
    status: "EXPERIMENTAL_CANDIDATE",
    decision: "EXPERIMENTAL_ONLY",
    coverage: {
      universe_id: UNIVERSE, denominator: 91, expected_band: "MEDIUM", measured: true,
      found: 79, fresh: 79, missing: 12,
      missing_codes: ["ARE", "BHS", "CMR", "DOM", "GRD", "HTI", "NIC", "OMN", "QAT", "TTO", "UKR", "USA"],
      stable_91_estimate: "79/91 measured for at least one non-null 2022-2024 observation",
      source_scope: "World Bank collects from registries in 170 economies; 2006-2024",
      rationale: "Measured current coverage is below the Phase 3A minimum of 82; some available country values also cover partial geography.",
    },
    sources: [
      source("C16-WB-ENTREPRENEURSHIP", "World Bank", "Entrepreneurship Database / World Development Indicators", "IC.BUS.NDNS.ZS new business density", "https://api.worldbank.org/v2/country/all/indicator/IC.BUS.NDNS.ZS?format=json&per_page=20000", "https://www.worldbank.org/en/programs/entrepreneurship/methodology", "https://databank.worldbank.org/metadataglossary/sustainable-development-goals-%28sdgs%29/series/IC.BUS.NDNS.ZS", "8th edition; annual 2006-2024", ["A4", "L4", "C4", "M3"]),
    ],
    methodology: ["A consistent concept—new limited-liability registrations per 1,000 people ages 15-64—is collected mainly from national registries.", "The measure excludes informal firms and does not capture formation quality, survival or venture funding."],
    licensing: ["World Bank metadata marks the exact series CC BY 4.0."],
    mapping: ["China covers Shanghai and Canada covers selected registries; these geographic exceptions must be explicit.", "Offshore financial centres may have registrations disconnected from resident opportunity."],
    scoring: { direction: "HIGHER_BETTER", grade: "S3", transformation: "Log1p, winsorise extreme offshore values, robust percentile; require recency and geography flags." },
    overlap: ["C05", "C29"],
    limitations: ["Formal registration can reflect regulatory or tax structures.", "New-firm density is not startup employment or success."],
    blockers: ["COV_BELOW_90_PERCENT", "CMP_PARTIAL_GEOGRAPHY", "SCO_OUTLIER_POLICY_REQUIRED"],
    recommendation: "Run only a conditional Phase 3E recovery probe. The measured 79/91 result misses the 82-country threshold before partial-geography exclusions.",
    open: ["Exclude or flag partial-geography and offshore observations?", "Require 2023+ or allow 2022?"],
    evidence: [
      evidence("The 8th Entrepreneurship Database edition contains annual company data through 2024 and uses a common limited-liability definition.", "https://www.worldbank.org/en/programs/entrepreneurship/methodology"),
      evidence("World Bank metadata identifies IC.BUS.NDNS.ZS as annual and CC BY 4.0.", "https://databank.worldbank.org/metadataglossary/sustainable-development-goals-%28sdgs%29/series/IC.BUS.NDNS.ZS"),
      evidence("The exact 2022-2024 WDI query returned current observations for 79/91 stable countries; 12 were missing.", "project-history/phases/phase-3/research/candidate-batch-2/world_bank_coverage_measurements.json", "MEASURED"),
    ],
  },
  {
    rank: 10,
    id: "C19",
    name: "Employment protection and worker rights",
    category: "Employment, income and economic opportunity",
    question: "How well are workers' fundamental organizing and collective-bargaining rights protected in law and practice?",
    definition: "The exact ILO SDG 8.8.2 construct, evaluated for suitability; broader dismissal protection and enforcement are not silently added.",
    granularity: "NATIONAL",
    observation: "ILO coding of supervisory texts and national legislation",
    freshness: "SLOW_STRUCTURAL",
    status: "REJECTED",
    decision: "REJECT",
    coverage: coverage("HIGH", "Method applies to ILO member states", "Broad nominal coverage is plausible", "Coverage cannot cure the source's explicit prohibition on cross-country comparison."),
    sources: [
      source("C19-ILO-SDG-882", "International Labour Organization", "ILOSTAT SDG indicator 8.8.2", "National compliance with labour rights: freedom of association and collective bargaining", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/", "https://www.ilo.org/rights-and-permissions", "Methodology amended 2022; current ILO textual sources", ["A4", "L4", "C1", "M3"]),
    ],
    methodology: ["The ILO states that SDG 8.8.2 measures freedom of association and collective bargaining using six supervisory textual sources and national law.", "The ILO explicitly says the indicator is not intended to compare compliance among member states because reporting obligations differ."],
    licensing: ["ILOSTAT reuse is generally CC BY 4.0; methodological unsuitability, not licence, is decisive."],
    mapping: ["Country mapping is straightforward; ratification and reporting-regime differences are substantive."],
    scoring: { direction: "LOWER_BETTER", grade: "S0", transformation: "None. Do not rank countries against the custodian agency's usage warning." },
    overlap: ["C11", "C71"],
    limitations: ["Covers only two fundamental labour-right domains.", "Textual-source intensity and reporting obligations differ across states."],
    blockers: ["CMP_SOURCE_PROHIBITS_COUNTRY_COMPARISON", "CMP_DEFINITION_TOO_NARROW", "SCO_INDEFENSIBLE"],
    recommendation: "Reject as an independent scored criterion. Retain only as descriptive research evidence if the product later adds unranked labour-rights profiles.",
    open: ["Whether an unscored worker-rights information panel is valuable."],
    evidence: [
      evidence("ILO states SDG 8.8.2 is not intended as a tool to compare compliance among member states.", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/"),
      evidence("The indicator is limited to freedom of association and effective recognition of collective bargaining.", "https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/about-sdg-indicator-8-8-2/"),
    ],
  },
  {
    rank: 11,
    id: "C22",
    name: "Social-security and mandatory contribution burden",
    category: "Tax, cost and financial conditions",
    question: "For a given salary, household and employment arrangement, what mandatory employee and employer social contributions apply and what benefits do they confer?",
    definition: "A salary- and household-specific contribution calculation, not an aggregate national revenue ratio.",
    granularity: "PROFILE_ONLY",
    observation: "Administrative tax-benefit model",
    freshness: "FAST_MOVING",
    status: "DEFERRED_PROFILE_LAYER",
    decision: "DEFER",
    coverage: coverage("LOW", "OECD Taxing Wages covers 38 members", "Far below 82", "No equally comparable global household-level contribution model was verified."),
    sources: [
      source("C22-OECD-TW-2026", "OECD", "Taxing Wages 2026", "Employee/employer social-security contributions by eight household types", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en.html", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html", "https://www.oecd.org/en/about/oecd-open-by-default-policy.html", "2025 tax year; 38 countries", ["A4", "L4", "C4", "M3"]),
    ],
    methodology: ["OECD calculates comparable effective burdens for specified earnings and household types.", "Contributions have ceilings, benefit entitlements and employee/employer incidence that make a headline statutory rate misleading."],
    licensing: ["OECD-owned post-July-2024 content is generally CC BY 4.0, subject to exceptions."],
    mapping: ["Requires salary, household, age, employment status and sometimes region.", "Tax years can differ from calendar years."],
    scoring: { direction: "PROFILE_DERIVED", grade: "S2", transformation: "Calculate scenario-specific net burden; do not assume lower contributions are always better." },
    overlap: ["C21", "C26", "C72"],
    limitations: ["OECD-only coverage.", "Burden without benefit entitlement is incomplete for relocation decisions."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_HOUSEHOLD_SCENARIO_REQUIRED", "PRF_PROFILE_ONLY", "SCO_DIRECTION_AMBIGUOUS"],
    recommendation: "Defer to a future tax-benefit calculator; reject as a universal national criterion.",
    open: ["Should contributions be displayed with expected health, pension and unemployment entitlements?"],
    evidence: [
      evidence("Taxing Wages 2026 covers all 38 OECD members and eight household types using 2025 rules.", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report.html"),
      evidence("The model separates employee and employer social contributions, income tax and cash benefits.", "https://www.oecd.org/en/publications/taxing-wages-2026_3a5169ef-en/full-report/overview_d93131c3.html"),
    ],
  },
  {
    rank: 12,
    id: "C26",
    name: "Healthcare affordability",
    category: "Safety, health and public services",
    question: "How exposed are households to paying for healthcare directly rather than through pooled financing?",
    definition: "Household out-of-pocket health spending as a share of current health expenditure, used only as a national financial-protection proxy.",
    granularity: "NATIONAL_WITH_PROFILE_CAVEAT",
    observation: "National health accounts, reported and estimated",
    freshness: "STANDARD_SOCIOECONOMIC",
    status: "EXPERIMENTAL_CANDIDATE",
    decision: "EXPERIMENTAL_ONLY",
    coverage: coverage("FULL", "WHO GHED provides comparable data for more than 190 members since 2000", "91/91 appears plausible", "Exact latest-year stable-91 coverage must be queried; GHED includes reported and estimated values."),
    sources: [
      source("C26-WHO-GHED-OOP", "World Health Organization", "Global Health Expenditure Database", "OOP%CHE; household out-of-pocket payment / current health expenditure", "https://apps.who.int/nha/database/DocumentationCentre/Index/en", "https://www.who.int/publications/b/80101", "https://data.who.int/about/data/terms-and-conditions", "GHED all data March 2026; series commonly through 2023/2024", ["A4", "L4", "C4", "M3"]),
    ],
    methodology: ["GHED uses the SHA 2011 framework and defines OOP%CHE consistently.", "The ratio measures financing structure, not immigrant eligibility, insurance premiums, prices, unmet need or catastrophic-spending incidence."],
    licensing: ["WHO dataset terms generally provide CC BY 4.0 with additional terms.", "The 2025 methodology publication itself is CC BY-NC-SA 3.0 IGO; publication and dataset licences must not be conflated."],
    mapping: ["WHO country codes require stable ISO mapping; territories and historical names need explicit rules."],
    scoring: { direction: "LOWER_BETTER", grade: "S3", transformation: "Reverse robust percentile; test against catastrophic-spending measures and do not label it personal cost." },
    overlap: ["C22", "C50"],
    limitations: ["A low share may reflect high total pooled spending or suppressed access.", "Migrant coverage rules can differ from citizen coverage."],
    blockers: ["COV_EXACT_JOIN_REQUIRED", "CMP_PROXY_ONLY", "GRA_MIGRANT_ELIGIBILITY_MISSING"],
    recommendation: "Run a conditional Phase 3E probe for stable-91 recency and licensing capture; keep the criterion explicitly labelled financial-protection proxy.",
    open: ["Prefer OOP%CHE or catastrophic health spending where available?", "How should migrant eligibility be surfaced separately?"],
    evidence: [
      evidence("WHO defines OOP%CHE as household out-of-pocket payment divided by current health expenditure.", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/out-of-pocket-expenditure-as-percentage-of-current-health-expenditure-%28che%29-%28-%29"),
      evidence("GHED provides comparable data for more than 190 WHO member states since 2000.", "https://www.who.int/teams/health-financing-and-economics/health-financing/expenditure-tracking/data-and-analytics"),
      evidence("WHO dataset terms are generally CC BY 4.0 unless specifically indicated otherwise.", "https://data.who.int/about/data/terms-and-conditions"),
    ],
  },
  {
    rank: 13,
    id: "C29",
    name: "Currency and macroeconomic stability",
    category: "Tax, cost and financial conditions",
    question: "How stable are household purchasing power and the destination's price/currency environment over a recent multi-year period?",
    definition: "A transparent small composite of consumer-price inflation level/volatility and official-exchange-rate volatility, with currency-union and peg caveats.",
    granularity: "NATIONAL",
    observation: "Official macroeconomic annual series",
    freshness: "FAST_MOVING",
    status: "PROBE_APPROVED",
    decision: "PROCEED_DETERMINISTIC_PROBE",
    coverage: {
      universe_id: UNIVERSE, denominator: 91, expected_band: "FULL", measured: true,
      found: 91, fresh: 91, missing: 0, missing_codes: [],
      stable_91_estimate: "91/91 measured component intersection",
      source_scope: "WDI/IMF annual inflation and official-exchange-rate series through 2024",
      rationale: "All 91 countries had at least three non-null 2020-2024 observations in both components and a latest observation in 2023 or 2024.",
    },
    sources: [
      source("C29-WDI-INFLATION", "World Bank distribution / IMF IFS upstream", "World Development Indicators", "FP.CPI.TOTL.ZG consumer-price inflation", "https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json&per_page=20000", "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG", "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG", "Annual through 2024", ["A4", "L4", "C4", "M4"]),
      source("C29-WDI-FXRATE", "World Bank distribution / IMF IFS upstream", "World Development Indicators", "PA.NUS.FCRF official exchange rate, LCU per USD", "https://api.worldbank.org/v2/country/all/indicator/PA.NUS.FCRF?format=json&per_page=20000", "https://data.worldbank.org/indicator/PA.NUS.FCRF", "https://data.worldbank.org/indicator/PA.NUS.FCRF", "Annual through 2024", ["A4", "L4", "C3", "M4"]),
    ],
    methodology: ["Inflation is comparable as annual CPI change; exchange-rate volatility requires log returns over several years.", "Official exchange rates can diverge from market rates, and a fixed peg can show low volatility despite reserve or convertibility risk."],
    licensing: ["The exact WDI indicator pages mark the distributed data CC BY 4.0."],
    mapping: ["Countries sharing EUR, XCD or USD need currency-union awareness.", "Redenominations and currency breaks must not be interpreted as volatility."],
    scoring: { direction: "LOWER_BETTER", grade: "S3", transformation: "Robust percentile of five-year median absolute inflation plus exchange-rate log-return volatility; publish component sensitivity." },
    overlap: ["C16", "Existing economic indicators"],
    limitations: ["Macroeconomic stability is broader than inflation and FX.", "Using USD as the sole reference may not match the user's income currency."],
    blockers: ["CMP_CURRENCY_REGIME", "SCO_COMPOSITE_SENSITIVITY_REQUIRED"],
    recommendation: "Proceed to a deterministic Phase 3E probe using pinned 2020-2024 observations and explicit currency-break handling.",
    open: ["Should FX volatility be user-income-currency specific?", "Should fixed/union currencies receive a separate regime flag?"],
    evidence: [
      evidence("WDI distributes annual CPI inflation through 2024 under CC BY 4.0.", "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG"),
      evidence("WDI provides official exchange-rate observations for most stable-universe countries through 2024.", "https://data.worldbank.org/indicator/PA.NUS.FCRF"),
      evidence("The stated two-component recency rule produced a measured 91/91 stable-country intersection.", "project-history/phases/phase-3/research/candidate-batch-2/world_bank_coverage_measurements.json", "MEASURED"),
    ],
  },
  {
    rank: 14,
    id: "C48",
    name: "Political stability and civil peace",
    category: "Safety, governance and rights",
    question: "How low is the perceived likelihood of political instability, politically motivated violence or terrorism disrupting normal life?",
    definition: "World Bank WGI Political Stability and Absence of Violence/Terrorism, using the 2025 revision's absolute score and uncertainty interval.",
    granularity: "NATIONAL",
    observation: "Annual perception-based composite",
    freshness: "SLOW_STRUCTURAL",
    status: "PROBE_APPROVED",
    decision: "PROCEED_DETERMINISTIC_PROBE",
    coverage: {
      universe_id: UNIVERSE, denominator: 91, expected_band: "FULL", measured: true,
      found: 91, fresh: 91, missing: 0, missing_codes: [],
      stable_91_estimate: "91/91 measured for 2024",
      source_scope: "WGI covers more than 200 economies through 2024",
      rationale: "The exact GOV_WGI_PV_EST 2024 API query mapped to all 91 stable countries.",
    },
    sources: [
      source("C48-WGI-PV-2025", "World Bank", "Worldwide Governance Indicators 2025 revision", "Political Stability and Absence of Violence/Terrorism; estimate and absolute 0-100 score", "https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators", "https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation", "https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators", "2025 revision; 1996-2024 recalculated", ["A4", "L4", "C4", "M4"]),
    ],
    methodology: ["WGI aggregates perception data from 35 cross-country sources using an unobserved-components model.", "The 2025 revision recalculates history, adds an anchored 0-100 scale and supplies uncertainty intervals."],
    licensing: ["The World Bank catalogue marks WGI CC BY 4.0.", "Underlying commercial source data have separate constraints, but published aggregate estimates are the candidate input."],
    mapping: ["More than 200 economies allow stable-91 ISO mapping; territory treatment must follow the universe registry."],
    scoring: { direction: "HIGHER_BETTER", grade: "S4", transformation: "Use published absolute score; retain confidence interval and test rank ties/uncertainty." },
    overlap: ["C66", "C68", "C49"],
    limitations: ["Perception composite is not an event forecast.", "Margins of error make small rank differences non-substantive."],
    blockers: ["CMP_PERCEPTION_BASED", "SCO_UNCERTAINTY_REQUIRED"],
    recommendation: "Proceed to a deterministic Phase 3E probe on the 2025-revision aggregate and its uncertainty fields.",
    open: ["Use only PV or add conflict-event data later as an unscored alert layer?"],
    evidence: [
      evidence("WGI 2025 covers more than 200 economies from 1996-2024 and is CC BY 4.0.", "https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators"),
      evidence("The 2025 methodology uses 35 perception sources and publishes absolute 0-100 scores plus uncertainty.", "https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation"),
      evidence("The exact 2024 GOV_WGI_PV_EST API query returned 91/91 stable countries.", "project-history/phases/phase-3/research/candidate-batch-2/world_bank_coverage_measurements.json", "MEASURED"),
    ],
  },
  {
    rank: 15,
    id: "C49",
    name: "Rule of law and institutional trust",
    category: "Safety, governance and rights",
    question: "How strongly do people and experts perceive that contracts, property rights, police, courts and rules are respected?",
    definition: "Narrow to WGI Rule of Law; do not claim it directly measures interpersonal or political trust.",
    granularity: "NATIONAL",
    observation: "Annual perception-based composite",
    freshness: "SLOW_STRUCTURAL",
    status: "PROBE_APPROVED",
    decision: "PROCEED_DETERMINISTIC_PROBE",
    coverage: {
      universe_id: UNIVERSE, denominator: 91, expected_band: "FULL", measured: true,
      found: 91, fresh: 91, missing: 0, missing_codes: [],
      stable_91_estimate: "91/91 measured for 2024",
      source_scope: "WGI covers more than 200 economies through 2024",
      rationale: "The exact GOV_WGI_RL_EST 2024 API query mapped to all 91 stable countries.",
    },
    sources: [
      source("C49-WGI-RL-2025", "World Bank", "Worldwide Governance Indicators 2025 revision", "Rule of Law estimate and absolute 0-100 score; GOV_WGI_RL_EST", "https://data.worldbank.org/indicator/GOV_WGI_RL_EST", "https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation", "https://datacatalog.worldbank.org/search/dataset/0038026/worldwide-governance-indicators", "2025 revision; 2024 observations", ["A4", "L4", "C4", "M4"]),
    ],
    methodology: ["WGI Rule of Law captures perceptions of confidence in and adherence to societal rules, including contracts, property rights, police, courts, crime and violence.", "Institutional trust is related but not identical; the criterion name should be narrowed in production."],
    licensing: ["The exact WGI dataset is CC BY 4.0."],
    mapping: ["Stable-91 ISO mapping should be straightforward; use the current WGI revision consistently across all years."],
    scoring: { direction: "HIGHER_BETTER", grade: "S4", transformation: "Use published absolute score and uncertainty; do not average Rule of Law, corruption and effectiveness without a separate rationale." },
    overlap: ["C48", "Existing governance-related criteria"],
    limitations: ["Perception sources and source availability vary by economy.", "Small differences are often within confidence intervals."],
    blockers: ["CMP_PERCEPTION_BASED", "SCO_UNCERTAINTY_REQUIRED", "RED_POTENTIAL_GOVERNANCE_OVERLAP"],
    recommendation: "Proceed to a deterministic Phase 3E probe after narrowing the label to Rule of Law and checking overlap with the active catalog.",
    open: ["Rename to Rule of law?", "Would Control of Corruption or Government Effectiveness add distinct relocation value?"],
    evidence: [
      evidence("The exact WGI Rule of Law indicator is distributed under CC BY 4.0 with 2024 data.", "https://data.worldbank.org/indicator/GOV_WGI_RL_EST"),
      evidence("WGI documentation advises using uncertainty and treating the composites as broad cross-country lenses.", "https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation"),
      evidence("The exact 2024 GOV_WGI_RL_EST API query returned 91/91 stable countries.", "project-history/phases/phase-3/research/candidate-batch-2/world_bank_coverage_measurements.json", "MEASURED"),
    ],
  },
];

const shortlistOrder = ["C29", "C48", "C49", "C34", "C05", "C26", "C16"];
const shortlist = specs
  .filter((item) => ["PROCEED_DETERMINISTIC_PROBE", "EXPERIMENTAL_ONLY"].includes(item.decision))
  .sort((a, b) => shortlistOrder.indexOf(a.id) - shortlistOrder.indexOf(b.id))
  .map((item, index) => ({
    rank: index + 1,
    criterion_id: item.id,
    name: item.name,
    track: item.decision === "PROCEED_DETERMINISTIC_PROBE" ? "DETERMINISTIC" : "CONDITIONAL",
    status: item.status,
    rationale: item.recommendation,
  }));

const output = {
  phase_id: "3C",
  batch_id: "PHASE3C_BATCH2_2026-07-26",
  evidence_cutoff: "2026-07-26",
  universe_id: UNIVERSE,
  denominator: 91,
  evidence_labels: {
    VERIFIED: "Confirmed from an identified source page, metadata record, exact dataset documentation, or publisher statement.",
    MEASURED: "The exact source was downloaded or queried and joined to the stable 91-country universe.",
    ESTIMATED: "Phase 3C analyst judgement; not a completed coverage or licensing audit.",
    HYPOTHESIS: "Candidate requiring discovery or confirmation.",
  },
  measurement_note: "Exact World Bank API responses were downloaded and joined for C16, both C29 components, C48 and C49. Their coverage is MEASURED. All other stable-91 coverage statements remain ESTIMATED.",
  coverage_measurement_file: "project-history/phases/phase-3/research/candidate-batch-2/world_bank_coverage_measurements.json",
  decision_summary: {
    deterministic_probe: specs.filter((x) => x.decision === "PROCEED_DETERMINISTIC_PROBE").map((x) => x.id),
    conditional_experimental_probe: specs.filter((x) => x.decision === "EXPERIMENTAL_ONLY").map((x) => x.id),
    deferred: specs.filter((x) => x.decision === "DEFER").map((x) => x.id),
    rejected: specs.filter((x) => x.decision === "REJECT").map((x) => x.id),
  },
  phase3e_shortlist: shortlist,
  recurring_families: [
    { family: "World Bank WDI/API", criteria: ["C05", "C16", "C29", "C49"], note: "Reusable JSON API, WDI metadata, and CC BY 4.0 indicator pages." },
    { family: "World Bank Worldwide Governance Indicators", criteria: ["C48", "C49"], note: "One 2025-revision dataset; share one adapter and uncertainty treatment." },
    { family: "ILOSTAT occupation and rights systems", criteria: ["C15", "C13", "C14", "C19"], note: "Strong classifications, but sector opportunity coverage/granularity and explicit 8.8.2 usage limits constrain scoring." },
    { family: "OECD migration and tax-benefit publications", criteria: ["C35", "C36", "C22"], note: "High-quality comparative evidence but regionally limited and often scenario-specific." },
    { family: "WHO health workforce and expenditure", criteria: ["C38", "C13", "C26"], note: "Useful official context; only GHED currently looks suitable for a national proxy probe." },
    { family: "EC and national legal portals", criteria: ["C38", "C35", "C36"], note: "Current-policy discovery, not a global harmonised dataset." },
  ],
  open_decisions: [
    "Whether C34 may use a narrow legal inclusiveness score or should remain informational.",
    "Whether C05 should use overall GII, Innovation Output, or a research-only subset.",
    "Whether C16 should exclude or flag partial-geography and offshore registration observations.",
    "Whether C26 is acceptable when explicitly labelled as a financial-protection proxy rather than migrant healthcare cost.",
    "How C29 should treat currency unions, fixed pegs, redenominations and user income currency.",
    "Whether C49 should be renamed Rule of law and how it overlaps the current active catalog.",
    "Which professions, cities, origins and households define future profile-layer pilots for C38, C35, C36, C15, C13, C14 and C22.",
  ],
  criteria: specs,
};

const esc = (value) => {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
};

const md = [];
md.push("# Konsider Phase 3C — Batch 2 source-feasibility research", "");
md.push(`Evidence cutoff: **${output.evidence_cutoff}**`);
md.push(`Universe: **${UNIVERSE} (91 countries)**`, "");
md.push("## Evidence boundary", "");
md.push("Publisher scope, methodology, version, and licensing statements labelled VERIFIED were checked against the linked source pages. Exact World Bank API responses were captured and joined for C16, C29, C48 and C49; those results are labelled MEASURED. All other stable-91 coverage statements are ESTIMATES.", "");
md.push("## Executive conclusion", "");
md.push(`Proceed to deterministic Phase 3E probes for **${output.decision_summary.deterministic_probe.join(", ")}**. Run conditional experimental probes for **${output.decision_summary.conditional_experimental_probe.join(", ")}**. Defer **${output.decision_summary.deferred.join(", ")}** to profile, occupation, city, or legal modules. Reject **${output.decision_summary.rejected.join(", ")}** as a scored criterion under the identified source methodology.`, "");
md.push("## Comparison table", "");
md.push("| Rank | ID | Criterion | Finding | Granularity | Stable-91 coverage | A/L/C/M | Phase 3E |");
md.push("| ---: | --- | --- | --- | --- | --- | --- | --- |");
for (const item of specs) {
  const g = item.sources[0];
  const coverageText = item.coverage.measured
    ? `${item.coverage.fresh}/${item.coverage.denominator} measured`
    : `${item.coverage.expected_band} estimated; not measured`;
  md.push(`| ${item.rank} | ${item.id} | ${item.name} | ${item.status} | ${item.granularity} | ${coverageText} | ${g.authority_grade}/${g.licence_grade}/${g.comparability_grade}/${g.mapping_grade} | ${item.decision} |`);
}
md.push("", "## Phase 3E shortlist", "");
for (const item of shortlist) md.push(`${item.rank}. **${item.criterion_id} — ${item.name}** (${item.track}): ${item.rationale}`);
md.push("", "## Recurring publisher and dataset families", "");
for (const item of output.recurring_families) md.push(`- **${item.family}** — ${item.criteria.join(", ")}. ${item.note}`);
md.push("", "## Open decisions", "");
for (const item of output.open_decisions) md.push(`- ${item}`);
md.push("");

for (const item of specs) {
  md.push(`# ${item.id} — ${item.name}`, "");
  md.push(`**Relocation question.** ${item.question}`, "");
  md.push(`**Operational definition.** ${item.definition}`, "");
  md.push(`**Finding.** ${item.status}; **recommendation:** ${item.decision}.`, "");
  md.push(`**Natural granularity and observation.** ${item.granularity}; ${item.observation}. Freshness class: ${item.freshness}.`, "");
  md.push("## Source candidates", "");
  for (const s of item.sources) {
    md.push(`- **${s.source_candidate_id} — ${s.publisher}, ${s.dataset}.** ${s.series_or_table || "No single series"}. Version: ${s.version}. Grades: ${s.authority_grade}/${s.licence_grade}/${s.comparability_grade}/${s.mapping_grade}. [Access](${s.access_url}) · [Methodology](${s.methodology_url}) · [Licence](${s.licence_url})`);
  }
  md.push("", "## Coverage and freshness", "");
  md.push(`- **${item.coverage.measured ? "MEASURED" : "ESTIMATED, not measured"}:** ${item.coverage.expected_band}. ${item.coverage.stable_91_estimate}.`);
  if (item.coverage.measured && item.coverage.missing_codes?.length) {
    md.push(`- **MEASURED missing/insufficient ISO3:** ${item.coverage.missing_codes.join(", ")}.`);
  }
  md.push(`- **VERIFIED publisher scope:** ${item.coverage.source_scope}.`);
  md.push(`- ${item.coverage.rationale}`);
  md.push("", "## Methodology and comparability", "");
  item.methodology.forEach((x) => md.push(`- ${x}`));
  md.push("", "## Licensing and reuse", "");
  item.licensing.forEach((x) => md.push(`- ${x}`));
  md.push("", "## Country and entity mapping", "");
  item.mapping.forEach((x) => md.push(`- ${x}`));
  md.push("", "## Scoring feasibility", "");
  md.push(`- Direction: **${item.scoring.direction}**; grade: **${item.scoring.grade}**.`);
  md.push(`- ${item.scoring.transformation}`);
  md.push("", "## Overlap, limitations, and blockers", "");
  md.push(`- Overlap: ${item.overlap.join(", ")}.`);
  item.limitations.forEach((x) => md.push(`- ${x}`));
  md.push(`- Reason codes: ${item.blockers.join("; ")}.`);
  md.push("", "## Recommendation", "");
  md.push(item.recommendation, "");
  md.push("## Evidence ledger", "");
  item.evidence.forEach((x) => md.push(`- **${x.evidence_level}:** ${x.claim} — ${x.source.startsWith("http") ? `[source](${x.source})` : x.source}`));
  md.push("", "## Open questions", "");
  item.open.forEach((x) => md.push(`- ${x}`));
  md.push("");
}

const csvRows = [
  ["rank", "criterion_id", "name", "status", "decision", "granularity", "coverage_band", "coverage_measured", "found", "fresh", "missing", "stable_91_estimate", "primary_publisher", "primary_dataset", "source_version", "authority_grade", "licence_grade", "comparability_grade", "mapping_grade", "scoring_direction", "scoring_grade", "blocker_codes", "recommendation"],
  ...specs.map((x) => {
    const s = x.sources[0];
    return [x.rank, x.id, x.name, x.status, x.decision, x.granularity, x.coverage.expected_band, x.coverage.measured, x.coverage.found, x.coverage.fresh, x.coverage.missing, x.coverage.stable_91_estimate, s.publisher, s.dataset, s.version, s.authority_grade, s.licence_grade, s.comparability_grade, s.mapping_grade, x.scoring.direction, x.scoring.grade, x.blockers.join(";"), x.recommendation];
  }),
];

fs.writeFileSync(path.join(OUT, "phase3c_batch2.json"), `${JSON.stringify(output, null, 2)}\n`);
fs.writeFileSync(path.join(OUT, "phase3c_batch2.md"), `${md.join("\n").trimEnd()}\n`);
fs.writeFileSync(path.join(OUT, "phase3c_batch2.csv"), `${csvRows.map((row) => row.map(esc).join(",")).join("\n")}\n`);
console.log(`Wrote ${specs.length} criteria, ${shortlist.length} Phase 3E candidates.`);
