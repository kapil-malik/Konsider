const fs = require("fs");
const path = require("path");

const OUT = __dirname;
const CHECKED = "2026-07-26T00:00:00+05:30";
const UNIVERSE = "stable_supported_v1";
const url = (publisher, dataset, series, access, method, licence, version, grades) => ({
  publisher, dataset, series_or_table: series, access_url: access, methodology_url: method,
  licence_url: licence, version, authority_grade: grades[0], licence_grade: grades[1],
  comparability_grade: grades[2], mapping_grade: grades[3], evidence_level: "VERIFIED",
});
const estCoverage = (band, estimate, scope, rationale) => ({
  universe_id: UNIVERSE, denominator: 91, measured: false, expected_band: band,
  stable_91_estimate: estimate, source_scope: scope, rationale,
});
const ev = (claim, source, level = "VERIFIED") => ({
  claim, source, checked_at: CHECKED, evidence_level: level,
});

const specs = [
  {
    rank: 1, id: "C53", name: "Water quality and sanitation", category: "Environment and public services",
    question: "How widely can residents rely on at least basic drinking-water and sanitation services in the destination country?",
    definition: "Narrow to the lower of population shares using at least basic drinking-water and at least basic sanitation services. Do not label this tap-water safety or continuity.",
    granularity: "NATIONAL_WITH_LOCAL_CAVEAT", observation: "Modelled household-service estimates", freshness: "SLOW_STRUCTURAL",
    status: "PROBE_APPROVED", decision: "PROCEED_DETERMINISTIC_PROBE",
    coverage: { universe_id: UNIVERSE, denominator: 91, measured: true, expected_band: "HIGH", found: 86, fresh: 86, missing: 5, missing_codes: ["BHS", "BIH", "GRD", "HRV", "NIC"], stable_91_estimate: "86/91 measured (94.5%) for both basic components with a 2022-2024 observation", source_scope: "JMP 2025 reports basic drinking water for 217 countries/areas and basic sanitation for 210", rationale: "The exact WDI/JMP API intersection clears the 82-country threshold. Safely managed water plus sanitation reaches only 66/91." },
    sources: [
      url("WHO/UNICEF JMP via World Bank WDI", "World Development Indicators", "SH.H2O.BASW.ZS; SH.STA.BASS.ZS", "https://api.worldbank.org/v2/country/all/indicator/SH.H2O.BASW.ZS?format=json", "https://washdata.org/report/jmp-2025-wash-households", "https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets", "2025 JMP release; observations through 2024", ["A4","L4","C4","M4"]),
    ],
    methodology: ["JMP applies harmonised service ladders to household survey, census and administrative inputs.", "Basic service is not equivalent to contaminant-free, continuously available household tap water."],
    licensing: ["World Bank-distributed WDI data are CC BY 4.0; pin exact indicator metadata and attribution.", "WHO/UNICEF source attribution should be retained."],
    mapping: ["Five stable-universe countries lack one or both fresh basic-service components.", "National averages obscure city, neighbourhood and network differences."],
    scoring: { direction: "HIGHER_BETTER", grade: "S4", transformation: "Use min(basic water %, basic sanitation %), winsorised only if necessary; expose both components." },
    overlap: ["C57", "C69"], limitations: ["Weak proxy for water quality in high-income destinations.", "Country estimates may be modelled and lag local infrastructure changes."],
    blockers: ["CMP_BASIC_NOT_SAFELY_MANAGED", "GRA_LOCAL_VARIATION"], recommendation: "Proceed to Phase 3E with the narrow basic-service definition and explicit missing-country outcomes; keep safely managed services as optional metadata.",
    open: ["Is a high-coverage but low-discrimination basic-service score valuable enough for relocation ranking?"],
    evidence: [ev("Exact WDI API join returned 86/91 fresh intersections.", "konsider_phase3c_batch3/world_bank_coverage_measurements.json", "MEASURED"), ev("The safely managed pair returned 66/91.", "konsider_phase3c_batch3/world_bank_coverage_measurements.json", "MEASURED")],
  },
  {
    rank: 2, id: "C71", name: "Work-life balance", category: "Employment and quality of life",
    question: "How heavy is the average weekly working-time burden for employed people in the destination?",
    definition: "Narrow to mean weekly hours actually worked per employed person; it does not measure leave, schedule control, commute or subjective balance.",
    granularity: "NATIONAL", observation: "ILO-modelled labour estimate", freshness: "ANNUAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("HIGH", "At least 82/91 appears plausible; exact indicator download not joined", "ILOSTAT publishes global modelled estimates, November 2025 edition", "Modelled global scope is promising, but exact stable-91 recency and sex/age aggregates remain unmeasured."),
    sources: [url("International Labour Organization", "ILOSTAT working-time indicators", "Average weekly hours actually worked per employed person by sex — ILO modelled estimates, Nov. 2025", "https://ilostat.ilo.org/topics/working-time/", "https://ilostat.ilo.org/methods/concepts-and-definitions/ilo-modelled-estimates/", "https://www.ilo.org/rights-and-permissions", "November 2025 modelled estimates", ["A4","L4","C4","M3"])],
    methodology: ["Actual hours exclude annual leave, public holidays, sickness, parental leave and commuting.", "Modelled estimates improve coverage but depend on harmonisation and imputation."],
    licensing: ["ILO open data published after 3 May 2023 are generally CC BY 4.0; capture the exact bulk-file notice."],
    mapping: ["National ISO mapping should be tractable; aggregation and observation-status fields must be retained."],
    scoring: { direction: "LOWER_BETTER", grade: "S3", transformation: "Reverse robust percentile of mean weekly hours; label as working-time burden." },
    overlap: ["C78"], limitations: ["Cannot substantiate the broad work-life-balance label.", "Informal work and multiple jobs may be measured unevenly."],
    blockers: ["DEF_LABEL_TOO_BROAD", "COV_EXACT_JOIN_REQUIRED"], recommendation: "Run an experimental Phase 3E probe only after renaming to Working-time burden.",
    open: ["Should paid leave be a separate policy/profile feature rather than folded into this score?"],
    evidence: [ev("ILOSTAT lists a November 2025 modelled average-weekly-hours table.", "https://ilostat.ilo.org/topics/working-time/"), ev("Stable-91 coverage has not been measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 3, id: "C76", name: "Social protection and welfare support", category: "Public services and welfare",
    question: "What share of residents is effectively covered by at least one social-protection benefit?",
    definition: "Narrow to effective social-protection coverage; it does not establish a new immigrant's eligibility, adequacy or waiting period.",
    granularity: "NATIONAL_WITH_PROFILE_CAVEAT", observation: "Administrative reports plus ILO modelled estimates", freshness: "SLOW_STRUCTURAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "At least 90% appears highly plausible; exact stable-91 join not performed", "ILO model output supplies complete 2009-2023 series for 189 countries/territories", "Publisher scope clears the threshold, but reported versus imputed values must be distinguished."),
    sources: [url("International Labour Organization", "World Social Protection Database / WSPR 2024-26 annex", "SDG 1.3.1 effective coverage; modelled series 2009-2023", "https://webapps.ilo.org/static/english/reports/flagship/world_social_protection_report_2024-26/Annex.html", "https://www.ilo.org/resource/article/world-social-protection-report-2024-26-figures", "https://www.ilo.org/rights-and-permissions", "WSPR 2024-26; data through 2023", ["A4","L4","C3","M3"])],
    methodology: ["The complete series includes reported and imputed observations.", "Coverage says whether a benefit is received, not its value or migrant eligibility."],
    licensing: ["ILO terms are favourable, but the exact downloadable database asset and attribution must be pinned."],
    mapping: ["Country mapping should be broad; preserve imputation flags and benefit-population definitions."],
    scoring: { direction: "HIGHER_BETTER", grade: "S3", transformation: "Published effective-coverage percentage; report imputation and do not infer newcomer entitlement." },
    overlap: ["C72"], limitations: ["Legal residents, temporary migrants and citizens can face different entitlements.", "High coverage may coexist with low benefit adequacy."],
    blockers: ["PRF_ELIGIBILITY_NOT_MEASURED", "CMP_MODELLED_VALUES"], recommendation: "Run a conditional Phase 3E probe as a national welfare-system reach proxy.",
    open: ["Should imputed observations receive lower confidence or remain unscored?"],
    evidence: [ev("ILO states that model output provides complete 2009-2023 series for 189 countries and territories.", "https://webapps.ilo.org/static/english/reports/flagship/world_social_protection_report_2024-26/Annex.html"), ev("Stable-91 coverage is publisher-scope based, not measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 4, id: "C54", name: "Food safety and public-health protection", category: "Health and safety",
    question: "How strong is the country's self-reported capacity to prevent, detect and respond to food-safety and wider public-health threats?",
    definition: "Use WHO SPAR Food Safety capacity (C13) as a narrow system-capacity proxy, not observed foodborne-illness risk.",
    granularity: "NATIONAL", observation: "Annual government self-assessment", freshness: "ANNUAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "At least 82/91 appears highly plausible; exact 2025 download not joined", "WHO SPAR covers IHR States Parties using 35 indicators across 15 capacities", "Annual global reporting is broad, but non-response and self-assessment bias need measurement."),
    sources: [url("World Health Organization", "State Party Self-Assessment Annual Reporting Tool (SPAR)", "C13 Food Safety capacity; 2025 dashboard", "https://extranet.who.int/e-spar/Home/CapacityScoreDetails", "https://extranet.who.int/e-spar/", "https://data.who.int/about/data/terms-and-conditions", "2025 data; dashboard updated 15 May 2026", ["A4","L4","C3","M3"])],
    methodology: ["SPAR is a structured annual self-assessment against IHR capacities.", "It measures national capacity, not inspections, outbreak incidence or restaurant-level safety."],
    licensing: ["WHO data terms generally use CC BY 4.0 with dataset-specific notices; verify the dashboard export."],
    mapping: ["States Parties map nationally; preserve missing reports and score revisions."],
    scoring: { direction: "HIGHER_BETTER", grade: "S3", transformation: "Use published C13 capacity score only; avoid averaging all 15 IHR capacities." },
    overlap: ["Existing health-system criteria"], limitations: ["Self-reporting may inflate capacity.", "National capacity may not predict day-to-day food safety."],
    blockers: ["CMP_SELF_REPORTED", "DEF_CAPACITY_NOT_OUTCOME", "COV_EXACT_JOIN_REQUIRED"], recommendation: "Run an experimental Phase 3E probe; label it Food-safety system capacity.",
    open: ["Is a system-capacity measure sufficiently decision-useful without outcome data?"],
    evidence: [ev("WHO exposes a 2025 SPAR capacity dashboard including Food Safety.", "https://extranet.who.int/e-spar/Home/CapacityScoreDetails"), ev("Stable-91 coverage is not measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 5, id: "C67", name: "Long-term climate-change exposure", category: "Climate and environment",
    question: "How large are projected long-term heat and precipitation changes under a declared emissions scenario and horizon?",
    definition: "A scenario-specific national climate-hazard projection, not a single factual forecast or vulnerability score.",
    granularity: "NATIONAL_DERIVED_FROM_GRID", observation: "Downscaled multi-model climate projections", freshness: "PERIODIC_MODEL_RELEASE",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "91/91 spatial coverage appears plausible; country aggregation not measured", "World Bank CCKP CMIP6 is global at 0.25 degrees, 1950-2100", "Raster coverage is global, but a defensible national aggregation and coastal/territory mapping must be tested."),
    sources: [url("World Bank Climate Change Knowledge Portal", "Projected Climate Data CMIP6", "Temperature and precipitation projections by SSP/horizon", "https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree", "https://climateknowledgeportal.worldbank.org/download-data", "https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree", "CMIP6; 1950-2100", ["A4","L4","C3","M3"])],
    methodology: ["Results depend on scenario, reference period, horizon, ensemble statistic and variable.", "Country means can hide populated-coast and city exposure."],
    licensing: ["The World Bank catalogue marks the dataset CC BY 4.0."],
    mapping: ["Requires reproducible country geometry and land/population weighting.", "Small islands may need careful grid-cell treatment."],
    scoring: { direction: "CONTEXT_DEPENDENT", grade: "S2", transformation: "No single score until scenario, horizon, variables and weighting are user-approved." },
    overlap: ["C68", "C70"], limitations: ["Projection uncertainty is material.", "Hazard change is not adaptation capacity or realised loss."],
    blockers: ["SCO_SCENARIO_CHOICE_REQUIRED", "GRA_SPATIAL_AGGREGATION"], recommendation: "Run an experimental methodology probe, not a production score probe.",
    open: ["Which SSP, horizon and exposure variables answer the relocation question?"],
    evidence: [ev("CCKP provides global 0.25-degree CMIP6 data through 2100 under CC BY 4.0.", "https://datacatalog.worldbank.org/search/dataset/0042297/climate-change-knowledge-portal-projected-climate-data-cmip6-0-25-degree"), ev("Stable-91 country aggregation was not measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 6, id: "C62", name: "Digital-government readiness", category: "Governance and digital services",
    question: "How extensively has the government adopted common digital-government systems and practices?",
    definition: "Use GovTech practices/components diagnostically; do not represent GTMI as an official readiness ranking.",
    granularity: "NATIONAL", observation: "Government survey plus public-web verification", freshness: "TRIENNIAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "About 90/91 appears plausible; Nicaragua is the known publisher-scope exclusion", "2025 GovTech dataset covers 197 economies; 158 survey responses and 39 public-data assessments", "Publisher scope is nearly complete but the exact workbook was not joined."),
    sources: [url("World Bank", "GovTech Dataset / GTMI 2025", "48 indicators across four focus areas", "https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset", "https://www.worldbank.org/en/programs/govtech/gtmi", "https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset", "2025 update", ["A4","L4","C3","M4"])],
    methodology: ["The World Bank explicitly says GTMI is not intended to rank or assess readiness/performance.", "Mixed self-reported and public-web inputs can have different evidence quality."],
    licensing: ["The dataset catalogue specifies CC BY 4.0."],
    mapping: ["Economy-to-ISO mapping should be strong; Nicaragua requires explicit missing handling."],
    scoring: { direction: "NONE_WITHOUT_REDESIGN", grade: "S1", transformation: "Use component facts or an unscored diagnostic until a defensible relocation-oriented construct exists." },
    overlap: ["C05", "Governance criteria"], limitations: ["Practice adoption does not prove service usability for immigrants.", "Triennial updates are adequate only for structural change."],
    blockers: ["SCO_PUBLISHER_DISCLAIMS_RANKING", "COV_EXACT_JOIN_REQUIRED"], recommendation: "Experimental only; inspect components in Phase 3E and reject a direct GTMI rank.",
    open: ["Which GovTech components directly affect a newcomer rather than general public administration?"],
    evidence: [ev("The 2025 dataset covers 197 economies and is CC BY 4.0.", "https://datacatalog.worldbank.org/search/dataset/0037889/govtech-dataset"), ev("The publisher says GTMI is not a readiness/performance ranking.", "https://www.worldbank.org/en/programs/govtech/gtmi")],
  },
  {
    rank: 7, id: "C68", name: "Natural-disaster risk", category: "Climate and safety",
    question: "How exposed is the destination to natural hazards after accounting for vulnerability and coping capacity?",
    definition: "Use INFORM Risk or its natural-hazard components; separate hazard exposure from vulnerability/governance.",
    granularity: "NATIONAL", observation: "Composite of hazard, exposure, vulnerability and coping indicators", freshness: "ANNUAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "At least 90% appears plausible; exact release join not measured", "INFORM is a global open-source risk assessment", "Global scope appears sufficient but the exact downloadable release and stable join remain to be pinned."),
    sources: [url("European Commission JRC and INFORM partners", "INFORM Risk", "Natural hazard/exposure, vulnerability, lack of coping capacity", "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk", "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology", "https://commission.europa.eu/legal-notice_en", "Current annual INFORM Risk release", ["A4","L3","C3","M3"])],
    methodology: ["Composite structure is transparent, but broad vulnerability and coping inputs overlap governance and development criteria.", "The full risk score is not a pure natural-hazard exposure measure."],
    licensing: ["The project is open-source, but exact dataset-asset reuse terms require capture before redistribution."],
    mapping: ["Country scope is global; conflict/territory treatment and missing-component imputation require inspection."],
    scoring: { direction: "LOWER_BETTER", grade: "S2", transformation: "Prefer published natural-hazard/exposure dimension; test against full INFORM score." },
    overlap: ["C48", "C66", "C67", "C70"], limitations: ["National scores obscure local hazard zones.", "Shared governance inputs could double count."],
    blockers: ["LIC_EXACT_ASSET_UNCLEAR", "RED_SHARED_COMPONENTS", "GRA_LOCAL_VARIATION"], recommendation: "Conditional Phase 3E probe focused on natural-hazard exposure, subject to exact licence capture.",
    open: ["Use exposure-only or the full vulnerability-adjusted risk score?"],
    evidence: [ev("INFORM documents a global composite of hazards/exposure, vulnerability and lack of coping capacity.", "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology"), ev("Exact stable-91 coverage and asset licence were not measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 8, id: "C06", name: "International-student accessibility", category: "Education and migration",
    question: "How established is the destination as a host for internationally mobile tertiary students?",
    definition: "Narrow to inbound internationally mobile student stock/rate; it measures realised presence, not admission, visa, tuition or accessibility.",
    granularity: "NATIONAL_WITH_PROFILE_CAVEAT", observation: "Administrative education statistics", freshness: "ANNUAL_WITH_LAG",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("HIGH", "At least 82/91 appears plausible; exact series join not measured", "UNESCO UIS releases cover more than 200 countries and territories", "Publisher scope is broad, but inbound-mobility availability and recency vary."),
    sources: [url("UNESCO Institute for Statistics", "UIS global education database", "Inbound internationally mobile students; inbound mobility rate", "https://uis.unesco.org/en/news/uis-launches-september-2025-global-education-data-release-0", "https://uis.unesco.org/en/methodology/communication-et-information", "https://www.unesco.org/en/open-access/cc-sa", "September 2025 release; February 2026 background update", ["A4","L3","C3","M3"])],
    methodology: ["Internationally mobile students are identified by prior residence or education where available.", "Observed inbound stock reflects attractiveness and capacity as well as accessibility."],
    licensing: ["Exact UIS bulk-download licence and third-party restrictions need capture; do not infer from general UNESCO pages."],
    mapping: ["Country/economy and academic-year mapping need normalization.", "Very small destinations can have volatile rates."],
    scoring: { direction: "HIGHER_BETTER_WITH_CAVEAT", grade: "S2", transformation: "Prefer published inbound mobility rate; do not call it admissions accessibility." },
    overlap: ["C01", "C35"], limitations: ["Does not measure tuition, visas, language or selectivity.", "May reward destinations with capacity constraints and high fees."],
    blockers: ["DEF_OUTCOME_NOT_ACCESS", "LIC_EXACT_ASSET_UNCLEAR", "COV_EXACT_JOIN_REQUIRED"], recommendation: "Experimental only after renaming to International-student presence; otherwise defer.",
    open: ["Is realised student presence a useful independent criterion or only context for C01/C35?"],
    evidence: [ev("UIS states that its 2025 education release covers more than 200 countries and territories.", "https://uis.unesco.org/en/news/uis-launches-september-2025-global-education-data-release-0"), ev("Exact stable-91 coverage and licence were not measured.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 9, id: "C75", name: "Religious freedom and freedom of expression", category: "Rights and inclusion",
    question: "How strongly are freedom of expression and religious freedom protected in law and practice?",
    definition: "Use a small, predeclared V-Dem indicator/index subset with uncertainty; do not invent a broad civil-liberties composite.",
    granularity: "NATIONAL", observation: "Expert-coded annual estimates", freshness: "ANNUAL",
    status: "EXPERIMENTAL_CANDIDATE", decision: "EXPERIMENTAL_ONLY",
    coverage: estCoverage("FULL", "At least 90% appears plausible; exact variables not joined", "V-Dem v16 contains country-year data for 531 indicators and 251 indices", "Dataset scope is broad, but exact variables, rater counts and current values require a probe."),
    sources: [url("V-Dem Institute", "V-Dem Dataset v16", "Freedom of expression and religion-related indicators/indices", "https://www.v-dem.net/data/the-v-dem-dataset/", "https://www.v-dem.net/documents/55/codebook_v16.pdf", "https://www.v-dem.net/about/faq/", "Version 16, March 2026", ["A4","L2","C3","M3"])],
    methodology: ["Expert-coded estimates include uncertainty and variable rater counts.", "V-Dem recommends caution or filtering when an observation has three or fewer raters."],
    licensing: ["V-Dem says its data are open source and free to use, but an exact commercial redistribution licence was not verified for the v16 archive."],
    mapping: ["Historical country units and current states require a pinned country-year mapping.", "Retain uncertainty and rater-count variables."],
    scoring: { direction: "HIGHER_BETTER", grade: "S2", transformation: "Select published indices or variables; use latest multi-year median and expose uncertainty." },
    overlap: ["C42", "C45", "C48", "C49"], limitations: ["Expert perception may not represent minority-specific lived experience.", "Combining two freedoms introduces normative weighting."],
    blockers: ["LIC_COMMERCIAL_REUSE_UNCLEAR", "SCO_VARIABLE_SELECTION_REQUIRED", "CMP_EXPERT_CODED"], recommendation: "Conditional experimental probe only after exact licence and variable selection are resolved.",
    open: ["Separate expression and religion into preference-weighted dimensions?", "Which v16 variables have adequate rater counts?"],
    evidence: [ev("V-Dem v16 was released in March 2026 and provides 531 indicators and 251 indices.", "https://www.v-dem.net/data/the-v-dem-dataset/"), ev("Commercial redistribution terms for the exact v16 archive remain unverified.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 10, id: "C70", name: "Climate resilience and adaptation readiness", category: "Climate and governance",
    question: "How ready is a country to convert investment into climate adaptation while reducing vulnerability?",
    definition: "ND-GAIN readiness/vulnerability composite, with overlap explicitly audited.",
    granularity: "NATIONAL", observation: "Composite of 45 indicators", freshness: "ANNUAL_WITH_REVISIONS",
    status: "DEFERRED_REDUNDANT", decision: "DEFER",
    coverage: estCoverage("FULL", "At least 90% appears plausible", "ND-GAIN download page states 192 UN countries with data through 2024", "Coverage is strong, but the reason to defer is construct overlap rather than country availability."),
    sources: [url("Notre Dame Global Adaptation Initiative", "ND-GAIN Country Index", "Vulnerability (36 indicators) and readiness (9 indicators)", "https://gain-new.crc.nd.edu/about/download", "https://gain-new.crc.nd.edu/about/methodology", "https://gain-new.crc.nd.edu/about/download", "Site updated 26 June 2026; data through 2024", ["A4","L4","C3","M3"])],
    methodology: ["Readiness includes economic, governance and social inputs; vulnerability spans six sectors.", "Many inputs overlap governance, innovation, education, infrastructure and ICT criteria."],
    licensing: ["Download page specifies CC Attribution 3.0 Unported."],
    mapping: ["Broad UN-country coverage; exact current download should be joined if revived."],
    scoring: { direction: "HIGHER_BETTER", grade: "S3", transformation: "Published score only; no Konsider reweighting without overlap analysis." },
    overlap: ["C05", "C48", "C49", "C62", "C67", "C68"], limitations: ["Composite score obscures drivers.", "Current pages contain inconsistent historical-period wording."],
    blockers: ["RED_SHARED_COMPONENTS", "DEF_COMPOSITE_TOO_BROAD"], recommendation: "Defer until the active catalog is consolidated in Phase 3E; revive only if it replaces rather than duplicates multiple criteria.",
    open: ["Would ND-GAIN replace C67/C68 plus governance inputs, or is hazard-specific scoring preferable?"],
    evidence: [ev("ND-GAIN states coverage of 192 UN countries and CC BY 3.0 reuse.", "https://gain-new.crc.nd.edu/about/download"), ev("Overlap judgement is preliminary.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 11, id: "C78", name: "Overall life satisfaction", category: "Subjective wellbeing",
    question: "How do residents rate their lives overall in the destination?",
    definition: "Country-level Cantril Ladder life evaluation, typically reported as a three-year average.",
    granularity: "NATIONAL_SURVEY", observation: "Probability-sample survey", freshness: "ANNUAL_THREE_YEAR_AVERAGE",
    status: "DEFERRED_LICENCE", decision: "DEFER",
    coverage: estCoverage("HIGH", "Likely below full coverage and potentially near the threshold; not measured", "World Happiness Report 2026 publishes country three-year averages using Gallup World Poll", "Small states and irregular survey years may create gaps."),
    sources: [url("Wellbeing Research Centre / Gallup / UN SDSN", "World Happiness Report 2026 data", "Life evaluation three-year averages", "https://www.worldhappiness.report/data-sharing/", "https://www.worldhappiness.report/ed/2026/", "https://www.worldhappiness.report/data-sharing/", "2026 report", ["A4","L2","C4","M3"])],
    methodology: ["Life evaluation is a standard 0-10 Cantril Ladder measure.", "Three-year pooling improves precision but reduces freshness and can straddle shocks."],
    licensing: ["Underlying Gallup World Poll microdata and extended data require institutional access; exact commercial reuse of report tables is unresolved."],
    mapping: ["Some small countries lack recent observations; country labels require a join."],
    scoring: { direction: "HIGHER_BETTER", grade: "S3", transformation: "Published three-year average if licensed; retain confidence intervals." },
    overlap: ["C71", "Many outcome criteria"], limitations: ["Broad outcome can double-count all domain-specific criteria.", "Respondent adaptation and culture affect comparisons."],
    blockers: ["LIC_COMMERCIAL_REUSE_UNCLEAR", "RED_OUTCOME_UMBRELLA", "COV_EXACT_JOIN_REQUIRED"], recommendation: "Defer pending exact dataset licence and overlap policy.",
    open: ["Should subjective wellbeing be an independent outcome or a validation benchmark?"],
    evidence: [ev("WHR 2026 publishes three-year life-evaluation averages based on Gallup World Poll.", "https://www.worldhappiness.report/data-sharing/"), ev("Stable-91 coverage and production licence are unverified.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 12, id: "C42", name: "Social inclusion and acceptance of immigrants", category: "Inclusion",
    question: "How accepting are residents of immigrants as neighbours or members of society?",
    definition: "A repeated national-attitude measure; WVS is the best open research candidate but not a current global production panel.",
    granularity: "NATIONAL_SURVEY", observation: "National probability survey", freshness: "MULTIYEAR_WAVE",
    status: "DEFERRED_COVERAGE", decision: "DEFER",
    coverage: estCoverage("MEDIUM", "Below 82/91 is likely", "WVS Wave 7 covers 77 countries/societies, fielded 2017-2021", "Publisher scope alone is below the 90% threshold and observations are mixed-date."),
    sources: [url("World Values Survey Association", "World Values Survey Wave 7", "Immigrants/foreign workers as neighbours and related attitudes", "https://www.worldvaluessurvey.org/WVSEventsShow.jsp?ID=413", "https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp", "https://www.worldvaluessurvey.org/WVSContents.jsp", "Wave 7, 2017-2021", ["A4","L2","C3","M3"])],
    methodology: ["National probability samples are typically 1,000-3,200 respondents.", "Question wording and social desirability limit interpretation as lived immigrant experience."],
    licensing: ["Data are free for academic use; production/commercial redistribution terms require explicit permission."],
    mapping: ["Wave coverage and field years vary; societies and territories need normalization."],
    scoring: { direction: "HIGHER_BETTER", grade: "S2", transformation: "Possible percentage rejecting anti-immigrant response, but not production-ready." },
    overlap: ["C45", "C75"], limitations: ["Below threshold and stale for fast-moving sentiment.", "Attitudes do not measure discrimination outcomes."],
    blockers: ["COV_BELOW_90_PERCENT", "STA_MIXED_FIELD_YEARS", "LIC_COMMERCIAL_REUSE_UNCLEAR"], recommendation: "Defer; revisit only with a licensed recurring global attitude source.",
    open: ["Would a smaller-country experimental layer be useful despite missingness?"],
    evidence: [ev("WVS Wave 7 reports 77 participating countries/societies and 2017-2021 fieldwork.", "https://www.worldvaluessurvey.org/WVSEventsShow.jsp?ID=413"), ev("Stable-91 coverage is inferred from publisher scope, not joined.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 13, id: "C57", name: "Water-supply reliability", category: "Environment and infrastructure",
    question: "Can households in likely destination cities obtain safe piped water continuously when needed?",
    definition: "Utility/city continuity and service-interruption performance, not national basic-water access.",
    granularity: "CITY_OR_UTILITY", observation: "Household survey or utility administrative data", freshness: "ANNUAL_OR_IRREGULAR",
    status: "DEFERRED_CITY_LAYER", decision: "DEFER",
    coverage: estCoverage("MEDIUM", "Below 82/91 for the exact reliability construct is likely", "JMP 2025 reports 'available when needed' for 144 countries/areas globally", "Global publisher scope does not ensure stable-universe coverage, and high-income reporting is incomplete."),
    sources: [url("WHO/UNICEF JMP", "JMP household WASH estimates", "Drinking water available when needed", "https://washdata.org/report/jmp-2025-wash-households", "https://washdata.org/monitoring/drinking-water", "https://washdata.org/terms-use", "2025 report; 2024 estimates", ["A4","L3","C3","M3"])],
    methodology: ["Availability when needed is one safely managed service component.", "Household responses do not provide utility outage frequency or neighbourhood reliability."],
    licensing: ["JMP reuse terms and exact downloadable-file notices require capture."],
    mapping: ["Utility boundaries rarely align with national or city boundaries.", "National estimates can conceal rationing in particular cities."],
    scoring: { direction: "HIGHER_BETTER", grade: "S1", transformation: "No independent national score; future city layer could use hours/day and interruption frequency." },
    overlap: ["C53"], limitations: ["Coverage below threshold is likely.", "Exact relocation value is city and neighbourhood specific."],
    blockers: ["COV_BELOW_90_PERCENT", "GRA_CITY_UTILITY_REQUIRED"], recommendation: "Defer to a city/utility data programme and keep C53 as the national service proxy.",
    open: ["Which priority cities and utility metrics should define a later pilot?"],
    evidence: [ev("JMP 2025 reports availability-when-needed estimates for 144 countries/areas.", "https://washdata.org/report/jmp-2025-wash-households"), ev("Stable-91 coverage was not joined.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 14, id: "C45", name: "LGBTQ+ legal and social inclusion", category: "Rights and inclusion",
    question: "How inclusive is the destination's law for LGBTQ+ people?",
    definition: "ILGA World legal-category evidence; social inclusion would require a separate survey source.",
    granularity: "NATIONAL_LEGAL", observation: "Expert-coded law", freshness: "PERIODIC",
    status: "REJECTED_LICENCE", decision: "REJECT",
    coverage: estCoverage("FULL", "Global coverage appears plausible", "ILGA World Laws on Us tracks 11 legal categories globally", "Coverage is not the blocker; reuse terms are."),
    sources: [url("ILGA World", "Laws on Us", "11 legal categories", "https://ilga.org/laws-on-us-report/", "https://ilga.org/laws-on-us-report/", "https://ilga.org/laws-on-us-report/", "30 May 2024", ["A4","L1","C4","M3"])],
    methodology: ["Legal categories are comparable but do not capture social acceptance, enforcement or subnational variation."],
    licensing: ["The current report page states CC BY-NC 4.0, incompatible with an unrestricted commercial production dataset.", "A conflicting asset snippet makes conservative treatment necessary; obtain written permission before reconsideration."],
    mapping: ["National legal mapping is broad; federal/subnational exceptions may matter."],
    scoring: { direction: "HIGHER_BETTER", grade: "S2", transformation: "Technically possible but normatively weighted and presently licence-blocked." },
    overlap: ["C42", "C75"], limitations: ["Law is not lived inclusion.", "Combining 11 categories requires normative choices."],
    blockers: ["LIC_NONCOMMERCIAL", "SCO_NORMATIVE_WEIGHTS_REQUIRED"], recommendation: "Reject for Phase 3E production candidacy unless ILGA grants suitable reuse permission.",
    open: ["Would ILGA provide a commercial licence or written permission for derived country scores?"],
    evidence: [ev("The ILGA report page states CC BY-NC 4.0.", "https://ilga.org/laws-on-us-report/"), ev("Global coverage was not joined because licence is dispositive.", "Phase 3C Batch 3", "ESTIMATED")],
  },
  {
    rank: 15, id: "C69", name: "Environmental quality beyond PM2.5", category: "Environment",
    question: "How well does the country perform across environmental health and ecosystem vitality beyond air pollution?",
    definition: "Yale Environmental Performance Index composite.",
    granularity: "NATIONAL_COMPOSITE", observation: "Composite of modelled and reported indicators", freshness: "BIENNIAL",
    status: "REJECTED_LICENCE_REDUNDANCY", decision: "REJECT",
    coverage: estCoverage("FULL", "At least 90% appears plausible", "EPI provides broad country coverage", "Coverage is not the blocker."),
    sources: [url("Yale Center for Environmental Law & Policy", "Environmental Performance Index 2024", "Overall EPI and issue categories", "https://epi.yale.edu/about-epi", "https://epi.yale.edu/faq/2024-epi-faq", "https://epi.yale.edu/faq/2024-epi-faq", "2024 EPI", ["A4","L1","C2","M3"])],
    methodology: ["Methodology and indicators change between editions; Yale warns against comparing scores across editions.", "The composite overlaps air, climate, water, biodiversity and sanitation criteria."],
    licensing: ["EPI 2024 is CC BY-NC-SA 4.0 and prohibits commercial use."],
    mapping: ["National mapping is broad but does not solve city-level environmental variation."],
    scoring: { direction: "HIGHER_BETTER", grade: "S1", transformation: "Do not ingest or rescore under current licence." },
    overlap: ["C53", "C57", "C67", "Existing PM2.5 criterion"], limitations: ["Composite is broad and version-unstable.", "National score hides local exposures."],
    blockers: ["LIC_NONCOMMERCIAL", "RED_COMPOSITE_OVERLAP", "CMP_VERSION_BREAKS"], recommendation: "Reject as an independent production criterion; use open, specific indicators instead.",
    open: ["None unless commercial permission becomes available."],
    evidence: [ev("Yale states EPI 2024 is CC BY-NC-SA 4.0 and editions are not directly comparable.", "https://epi.yale.edu/faq/2024-epi-faq")],
  },
];

const shortlistIds = ["C53", "C71", "C76", "C54", "C67", "C62", "C68", "C06", "C75"];
const shortlist = shortlistIds.map((id, i) => {
  const x = specs.find((item) => item.id === id);
  return { rank: i + 1, criterion_id: id, name: x.name, track: x.decision === "PROCEED_DETERMINISTIC_PROBE" ? "DETERMINISTIC" : "CONDITIONAL_EXPERIMENTAL", rationale: x.recommendation };
});
const output = {
  phase_id: "3C", batch_id: "PHASE3C_BATCH3_2026-07-26", evidence_cutoff: "2026-07-26",
  universe_id: UNIVERSE, denominator: 91,
  evidence_labels: {
    VERIFIED: "Confirmed from an identified official/authoritative source or publisher documentation.",
    MEASURED: "Exact source data were queried/downloaded and joined to stable_supported_v1.",
    ESTIMATED: "Preliminary Phase 3C judgement; not an exhaustive coverage or licensing audit.",
  },
  measurement_note: "Only C53 coverage is measured. All other stable-91 statements are preliminary estimates based on publisher scope.",
  coverage_measurement_file: "konsider_phase3c_batch3/world_bank_coverage_measurements.json",
  decision_summary: {
    deterministic_probe: specs.filter((x) => x.decision === "PROCEED_DETERMINISTIC_PROBE").map((x) => x.id),
    conditional_experimental_probe: specs.filter((x) => x.decision === "EXPERIMENTAL_ONLY").map((x) => x.id),
    deferred: specs.filter((x) => x.decision === "DEFER").map((x) => x.id),
    rejected: specs.filter((x) => x.decision === "REJECT").map((x) => x.id),
  },
  phase3e_shortlist: shortlist,
  recurring_families: [
    { family: "World Bank open data", criteria: ["C53", "C62", "C67"], note: "CC BY 4.0 national/global datasets; only C53 has measured stable-91 coverage." },
    { family: "WHO/UNICEF monitoring", criteria: ["C53", "C54", "C57"], note: "Strong harmonised public-service definitions; quality, self-reporting and local granularity differ." },
    { family: "ILO modelled and administrative systems", criteria: ["C71", "C76"], note: "Broad scope and favourable reuse; exact current bulk files still need probes." },
    { family: "Expert-coded/composite indices", criteria: ["C68", "C70", "C75"], note: "Useful global scope but require overlap, uncertainty and component-selection controls." },
    { family: "Survey-based wellbeing and attitudes", criteria: ["C42", "C78"], note: "Conceptually relevant but constrained by coverage, mixed field years and/or reuse rights." },
    { family: "Non-commercial research products", criteria: ["C45", "C69"], note: "Authoritative but unsuitable for unrestricted production reuse under identified licences." },
  ],
  city_level_treatment: [
    { criterion_id: "C57", treatment: "REQUIRED", reason: "Reliability is utility/network and neighbourhood specific." },
    { criterion_id: "C53", treatment: "SUPPLEMENTAL", reason: "National basic-service access hides local quality and network gaps." },
    { criterion_id: "C67", treatment: "DESIRABLE", reason: "Gridded hazards should eventually be population/city weighted." },
    { criterion_id: "C68", treatment: "DESIRABLE", reason: "National hazard risk hides flood, wildfire, cyclone and seismic zones." },
    { criterion_id: "C69", treatment: "NATURAL_BUT_REJECTED", reason: "Environmental exposure is local, while the candidate is a licence-blocked national composite." },
  ],
  batch_conclusion: "Batch 3 adds one deterministic Phase 3E candidate (C53) and eight conditional experimental candidates. It does not justify a fourth broad Phase 3C batch; consolidate all batches in Phase 3E.",
  criteria: specs,
};

const esc = (v) => /[",\n]/.test(String(v ?? "")) ? `"${String(v ?? "").replaceAll('"', '""')}"` : String(v ?? "");
const md = ["# Konsider Phase 3C — Batch 3 source-feasibility research", "",
  `Evidence cutoff: **${output.evidence_cutoff}**`, `Universe: **${UNIVERSE} (91 countries)**`, "",
  "## Evidence boundary", "",
  "Only C53 coverage is **MEASURED** from captured World Bank API responses joined to the stable 91-country universe. Publisher scope, method and identified licence statements are **VERIFIED** where linked. Every other stable-91 conclusion is a preliminary **ESTIMATE**, not an exhaustive audit.", "",
  "## Executive conclusion", "",
  `Proceed to a deterministic Phase 3E probe for **${output.decision_summary.deterministic_probe.join(", ")}**. Treat **${output.decision_summary.conditional_experimental_probe.join(", ")}** as conditional experiments, not approved production criteria. Defer **${output.decision_summary.deferred.join(", ")}** and reject **${output.decision_summary.rejected.join(", ")}** under the identified sources. This is the final broad Phase 3C batch; next step is consolidated Phase 3E.`, "",
  "## Comparison table", "",
  "| Rank | ID | Criterion | Finding | Granularity | Stable-91 coverage | A/L/C/M | Phase 3E |",
  "| ---: | --- | --- | --- | --- | --- | --- | --- |",
];
for (const x of specs) {
  const s = x.sources[0];
  md.push(`| ${x.rank} | ${x.id} | ${x.name} | ${x.status} | ${x.granularity} | ${x.coverage.measured ? `${x.coverage.fresh}/91 measured` : `${x.coverage.expected_band} estimated`} | ${s.authority_grade}/${s.licence_grade}/${s.comparability_grade}/${s.mapping_grade} | ${x.decision} |`);
}
md.push("", "## Phase 3E shortlist", "");
shortlist.forEach((x) => md.push(`${x.rank}. **${x.criterion_id} — ${x.name}** (${x.track}): ${x.rationale}`));
md.push("", "## Recurring publisher and dataset families", "");
output.recurring_families.forEach((x) => md.push(`- **${x.family}** — ${x.criteria.join(", ")}. ${x.note}`));
md.push("", "## Criteria requiring city-level treatment", "");
output.city_level_treatment.forEach((x) => md.push(`- **${x.criterion_id} (${x.treatment})** — ${x.reason}`));
md.push("");
for (const x of specs) {
  md.push(`# ${x.id} — ${x.name}`, "", `**Relocation question.** ${x.question}`, "", `**Operational definition.** ${x.definition}`, "",
    `**Finding.** ${x.status}; **recommendation:** ${x.decision}.`, "",
    `**Natural granularity and observation.** ${x.granularity}; ${x.observation}. Freshness: ${x.freshness}.`, "",
    "## Source candidates", "");
  x.sources.forEach((s) => md.push(`- **${s.publisher} — ${s.dataset}.** ${s.series_or_table}. Version: ${s.version}. Grades: ${s.authority_grade}/${s.licence_grade}/${s.comparability_grade}/${s.mapping_grade}. [Access](${s.access_url}) · [Methodology](${s.methodology_url}) · [Licence](${s.licence_url})`));
  md.push("", "## Coverage and freshness", "", `- **${x.coverage.measured ? "MEASURED" : "ESTIMATED, not measured"}:** ${x.coverage.stable_91_estimate}.`, `- **VERIFIED publisher scope:** ${x.coverage.source_scope}.`, `- ${x.coverage.rationale}`);
  if (x.coverage.missing_codes) md.push(`- Missing/stale ISO3: ${x.coverage.missing_codes.join(", ")}.`);
  md.push("", "## Methodology and comparability", ""); x.methodology.forEach((v) => md.push(`- ${v}`));
  md.push("", "## Licensing and reuse", ""); x.licensing.forEach((v) => md.push(`- ${v}`));
  md.push("", "## Country and entity mapping", ""); x.mapping.forEach((v) => md.push(`- ${v}`));
  md.push("", "## Scoring feasibility", "", `- Direction: **${x.scoring.direction}**; grade: **${x.scoring.grade}**.`, `- ${x.scoring.transformation}`,
    "", "## Overlap, limitations, and blockers", "", `- Overlap: ${x.overlap.join(", ")}.`);
  x.limitations.forEach((v) => md.push(`- ${v}`));
  md.push(`- Reason codes: ${x.blockers.join("; ")}.`, "", "## Recommendation", "", x.recommendation, "", "## Evidence ledger", "");
  x.evidence.forEach((v) => md.push(`- **${v.evidence_level}:** ${v.claim} — ${v.source.startsWith("http") ? `[source](${v.source})` : v.source}`));
  md.push("", "## Open questions", ""); x.open.forEach((v) => md.push(`- ${v}`)); md.push("");
}

const csv = [["rank","criterion_id","name","status","decision","granularity","freshness","coverage_band","coverage_measured","found","fresh","missing","stable_91_estimate","primary_publisher","primary_dataset","version","authority_grade","licence_grade","comparability_grade","mapping_grade","scoring_direction","scoring_grade","blocker_codes","recommendation"],
  ...specs.map((x) => { const s = x.sources[0]; return [x.rank,x.id,x.name,x.status,x.decision,x.granularity,x.freshness,x.coverage.expected_band,x.coverage.measured,x.coverage.found,x.coverage.fresh,x.coverage.missing,x.coverage.stable_91_estimate,s.publisher,s.dataset,s.version,s.authority_grade,s.licence_grade,s.comparability_grade,s.mapping_grade,x.scoring.direction,x.scoring.grade,x.blockers.join(";"),x.recommendation]; })];

fs.writeFileSync(path.join(OUT, "phase3c_batch3.json"), `${JSON.stringify(output, null, 2)}\n`);
fs.writeFileSync(path.join(OUT, "phase3c_batch3.md"), `${md.join("\n").trimEnd()}\n`);
fs.writeFileSync(path.join(OUT, "phase3c_batch3.csv"), `${csv.map((r) => r.map(esc).join(",")).join("\n")}\n`);
console.log(`Wrote ${specs.length} criteria and ${shortlist.length} Phase 3E candidates.`);
