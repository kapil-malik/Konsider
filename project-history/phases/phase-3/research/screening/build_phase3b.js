const fs = require("fs");
const path = require("path");

const researchRoot = path.resolve(__dirname, "..");
const masterPath = path.join(
  researchRoot,
  "framework",
  "phase3a_master_research_list.json",
);
const master = JSON.parse(fs.readFileSync(masterPath, "utf8"));
const byId = Object.fromEntries(master.criteria.map((item) => [item.criterion_id, item]));

const deepRanked = [
  "C11","C32","C33","C17","C21","C25","C50","C40","C01","C30","C12","C58","C56","C08","C66",
  "C38","C35","C36","C34","C05","C15","C13","C14","C16","C19","C22","C26","C29","C48","C49",
  "C53","C57","C62","C67","C68","C70","C71","C72","C06","C07","C42","C45"
];
const batch1 = deepRanked.slice(0, 15);
const batch2 = deepRanked.slice(15, 30);

const evidence = {
  E01: {
    claim: "UNESCO UIS describes itself as the official source of cross-nationally comparable education data; its browser offers APIs, bulk downloads, metadata, and a February 2026 release.",
    url: "https://databrowser.uis.unesco.org/resources",
    checked: "2026-07-24"
  },
  E02: {
    claim: "ILOSTAT provides bulk/API-style access to harmonised labour indicators, dictionaries, metadata, and modelled estimates.",
    url: "https://ilostat.ilo.org/data/bulk/",
    checked: "2026-07-24"
  },
  E03: {
    claim: "UN DESA International Migrant Stock 2024 covers 233 countries and areas for 1990–2024, but many 2024 values are extrapolations rather than full reassessments.",
    url: "https://www.un.org/development/desa/pd/content/international-migrant-stock",
    checked: "2026-07-24"
  },
  E04: {
    claim: "WHO Global Health Observatory exposes country and indicator data through an OData API.",
    url: "https://www.who.int/data/gho/info/gho-odata-api",
    checked: "2026-07-24"
  },
  E05: {
    claim: "ITU DataHub contains hundreds of ICT indicators and data for nearly 200 economies, including access, use, coverage, affordability, and quality-of-service indicators.",
    url: "https://datahub.itu.int/",
    checked: "2026-07-24"
  },
  E06: {
    claim: "WHO/UNICEF JMP's 2025 household WASH release reports estimates through 2024.",
    url: "https://washdata.org/reports/jmp-2025-wash-households",
    checked: "2026-07-24"
  },
  E07: {
    claim: "World Bank WGI 2025 reports six annual governance dimensions for more than 200 economies through 2024 and publishes uncertainty; it is a perception-based composite.",
    url: "https://www.worldbank.org/en/publication/worldwide-governance-indicators",
    checked: "2026-07-24"
  },
  E08: {
    claim: "World Bank WBL 2026 covers 190 economies, is current to 1 October 2025, and its catalog records CC BY 4.0.",
    url: "https://datacatalog.worldbank.org/search/dataset/0038489/women-business-and-the-law",
    checked: "2026-07-24"
  },
  E09: {
    claim: "World Bank ICP 2021 has observed results for 176 economies plus imputed results for 19; it provides PPPs and price-level indexes.",
    url: "https://www.worldbank.org/en/programs/icp/data",
    checked: "2026-07-24"
  },
  E10: {
    claim: "IMF WEO April 2026 includes inflation, unemployment, growth, fiscal and external indicators and is published twice yearly, with some country-series gaps.",
    url: "https://data.imf.org/Datasets/WEO",
    checked: "2026-07-24"
  },
  E11: {
    claim: "OECD Taxing Wages 2026 reports effective tax wedges for 38 member countries and selected household cases, well below the 91-country universe.",
    url: "https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/04/taxing-wages-2026_d1f39986/3a5169ef-en.pdf",
    checked: "2026-07-24"
  },
  E12: {
    claim: "World Bank CCKP offers country, subnational, watershed and gridded climate data, including API access and World Bank dataset terms.",
    url: "https://climateknowledgeportal.worldbank.org/download-data",
    checked: "2026-07-24"
  },
  E13: {
    claim: "Copernicus ERA5 is a globally complete, consistent reanalysis from 1940 onward with continuing updates.",
    url: "https://climate.copernicus.eu/climate-reanalysis",
    checked: "2026-07-24"
  },
  E14: {
    claim: "EU/JRC INFORM Risk 2026 is openly downloadable with source data and calculation steps for global country risk.",
    url: "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Results-and-data/moduleId/1782/id/453/controller/Admin/a",
    checked: "2026-07-24"
  },
  E15: {
    claim: "ILO NATLEX/NORMLEX provide large official corpora of national labour and social-security legislation, but not a ready-made relocation score.",
    url: "https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/home",
    checked: "2026-07-24"
  },
  E16: {
    claim: "ILGA World's 2024 Laws on Us covers 11 LGBTQ+ legal categories but is licensed CC BY-NC 4.0.",
    url: "https://ilga.org/laws-on-us-report/",
    checked: "2026-07-24"
  },
  E17: {
    claim: "World Happiness Report 2026 uses harmonised Gallup life-evaluation responses averaged over 2023–2025 and makes the published three-year averages downloadable.",
    url: "https://www.worldhappiness.report/data-sharing/",
    checked: "2026-07-24"
  },
  E18: {
    claim: "World Bank Logistics Performance Index 2023 is an official cross-country measure of trade-logistics speed and reliability.",
    url: "https://www.worldbank.org/en/news/press-release/2023/04/21/world-bank-releases-logistics-performance-index-2023",
    checked: "2026-07-24"
  }
};

// Tab-separated fields:
// id, measure, publishers, datasets, refs, comparability, coverage90, band,
// freshness, licence uncertainty, natural granularity, status, priority,
// downgrade rationale, reason codes.
const raw = `
C01	National breadth, participation, completion and credible quality signals in tertiary education.	UNESCO UIS; World Bank; national education ministries; OECD as a supplement	UIS tertiary enrolment/graduation/ISCED indicators; World Bank EdStats; OECD Education at a Glance	E01	C3	YES	HIGH	STANDARD_SOCIOECONOMIC: annual/0–3y likely	MEDIUM	national	SCREENED_PROMISING	HIGH	Quality is not captured by availability alone; rankings are commercially licensed and institution-weighted.	SEM_QUESTION_TOO_BROAD|LIC_AMBIGUOUS
C02	Strength and availability of tertiary programmes and graduates in engineering, ICT and related fields.	UNESCO UIS; national education/accreditation bodies; OECD; commercial ranking publishers	UIS graduates/enrolment by ISCED field; national programme registers; subject rankings for discovery	E01	C3	UNCERTAIN	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y likely	HIGH	city/regional	SCREENED_POSSIBLE	LOW	Global field-of-study counts are plausible, but comparable programme quality and institution location are not.	COV_BELOW_90_PERCENT|GRA_CITY_LEVEL_REQUIRED|LIC_AMBIGUOUS
C03	Availability and quality of medicine, dentistry, nursing, pharmacy and allied-health education.	UNESCO UIS; WHO; World Directory of Medical Schools; national accreditors	UIS health-field graduates; WDOMS; national accredited programme registers	E01|E04	C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: mixed 0–5y	HIGH	city/regional	SCREENED_LOW_FEASIBILITY	LOW	Programme quality, recognition and seat access vary by profession and institution; WDOMS is not a quality ranking.	COV_BELOW_90_PERCENT|CMP_DEFINITION_DIFFERS|GRA_PROFESSION_SPECIFIC
C04	Availability and quality of business, finance, economics, accounting and management education.	UNESCO UIS; national accreditors; OECD; commercial ranking/accreditation bodies	UIS business-field graduates; official programme registers; AACSB/EQUIS and subject rankings for discovery	E01	C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: mixed 0–5y	HIGH	city/regional	SCREENED_LOW_FEASIBILITY	LOW	Accreditation and rankings cover a selective institution set and carry licensing and selection bias.	COV_BELOW_90_PERCENT|LIC_AMBIGUOUS|GRA_CITY_LEVEL_REQUIRED
C05	National research intensity, outputs, patents, doctoral capacity and university–industry links.	UNESCO UIS; WIPO; World Bank; OECD	UIS R&D expenditure/researchers; WIPO IP Statistics; doctoral graduates; Global Innovation Index components	E01	C3	YES	HIGH	STANDARD_SOCIOECONOMIC: 0–3y with lag	MEDIUM	national	SCREENED_PROMISING	MEDIUM	A composite must avoid mixing inputs and outputs or importing opaque GII weights.	SCO_COMPOSITE_WEIGHTS_ARBITRARY|RED_SHARED_COMPONENTS
C06	Practical accessibility for international students: enrolment openness, English-taught options, visas and support.	UNESCO UIS; OECD; national immigration and education authorities	UIS inbound student mobility; OECD international students; official student-visa and post-study rules	E01	C2	NO	MEDIUM	CURRENT_POLICY plus annual mobility data	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Mobility stock is comparable; admissions, English-taught programmes and visa rules need manual current-policy coding.	COV_BELOW_90_PERCENT|CMP_DEFINITION_DIFFERS|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C07	Tuition cost faced by representative domestic/international students relative to income or PPP.	UNESCO UIS; OECD; national ministries and institution fee schedules	UIS education finance; OECD tertiary fees; official fee schedules; ICP PPP denominators	E01|E09	C2	NO	MEDIUM	FAST_MOVING: latest 0–2y	HIGH	city/regional	SCREENED_POSSIBLE	MEDIUM	Fees vary by institution, programme, residency and scholarship; global harmonised international-student prices are unlikely.	GRA_HOUSEHOLD_SCENARIO_REQUIRED|CMP_POPULATION_DIFFERS|COV_BELOW_90_PERCENT
C08	Primary/secondary learning outcomes, completion and system quality.	UNESCO UIS; World Bank; OECD; IEA	UIS SDG4 completion/proficiency; World Bank Learning Poverty/HCI; PISA; TIMSS/PIRLS	E01	C3	UNCERTAIN	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y, assessments periodic	MEDIUM	national	SCREENED_POSSIBLE	HIGH	Administrative completion is broad, but common learning assessments miss many stable-universe countries and cycles.	COV_BELOW_90_PERCENT|FRS_MIXED_REFERENCE_PERIODS
C09	Availability and affordability of recognised international schools in likely destinations.	IB; Cambridge International; national school registries; international-school directories	IB World Schools; Cambridge school finder; official school lists; fee schedules		C2	NO	LOW	FAST_MOVING: annual/current directories	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	A city-level institution inventory and commercial-directory licensing would be required.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C10	Ease of academic/professional recognition and portability of foreign qualifications.	UNESCO; ENIC-NARIC networks; national recognition and professional bodies	Global/Regional Recognition Conventions; WHED; ENIC-NARIC country procedures; regulated-profession rules		C2	NO	MEDIUM	STATIC_OR_LEGAL_ASOF: current	HIGH	profile-derived	SCREENED_LOW_FEASIBILITY	LOW	Outcome depends on origin, destination, qualification and profession; no single country score is defensible.	GRA_ORIGIN_SPECIFIC|GRA_PROFESSION_SPECIFIC|SCO_NO_CLEAR_DIRECTION
C11	National employment opportunity using employment, unemployment, participation and labour-underutilisation signals.	ILO; World Bank; national statistical offices	ILOSTAT modelled estimates and harmonised labour-force indicators; World Bank WDI representations	E02	C4	YES	HIGH	FAST_MOVING: annual/quarterly, latest 0–2y	MEDIUM	national	SCREENED_PROMISING	HIGH	Vacancies are not globally comparable, so the first version should stay with harmonised labour outcomes.	CMP_DEFINITION_DIFFERS
C12	Depth of software, ICT, data, AI and cybersecurity employment.	ILO; national statistical offices; official vacancy services; OECD	ILOSTAT employment by ISCO/industry; official vacancies; OECD ICT employment; online-job data for discovery	E02	C2	NO	MEDIUM	FAST_MOVING: latest 0–2y	HIGH	city/regional	SCREENED_POSSIBLE	HIGH	Global occupation aggregates are broad; granular tech vacancies are platform-dependent and concentrated in cities.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C13	Demand and employment opportunity for health professionals, separate from licensing access.	ILO; WHO; national health-workforce observatories	ILOSTAT occupation/industry employment; WHO health workforce density; official shortage lists	E02|E04	C3	UNCERTAIN	MEDIUM	FAST_MOVING/STANDARD: 0–3y	MEDIUM	city/regional	SCREENED_POSSIBLE	MEDIUM	Provider shortage is not equivalent to accessible jobs, and licensing must remain a separate gate.	GRA_PROFESSION_SPECIFIC|SEM_CAUSALITY_OVERCLAIM
C14	Demand for finance, consulting, accounting, marketing, operations, sales and management roles.	ILO; national statistical offices; official vacancy services	ILOSTAT ISCO/industry employment; labour force surveys; official vacancies	E02	C2	NO	MEDIUM	FAST_MOVING: latest 0–2y	HIGH	city/regional	SCREENED_POSSIBLE	MEDIUM	Occupational groupings are broad and vacancy data are uneven; major-city concentration is material.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT
C15	Demand for civil, mechanical, electrical, industrial, energy and skilled technical roles.	ILO; national statistical offices; official vacancy/shortage lists	ILOSTAT ISCO/industry employment; labour force surveys; official shortage occupation lists	E02	C3	UNCERTAIN	MEDIUM	FAST_MOVING: latest 0–2y	MEDIUM	city/regional	SCREENED_POSSIBLE	MEDIUM	Broad ISCO groups are comparable, but specialisms, licensing and regional projects are not.	GRA_PROFESSION_SPECIFIC|COV_BELOW_90_PERCENT
C16	Business formation, firm entry, startup activity, finance access and survival conditions.	World Bank; OECD; national business registries; Global Entrepreneurship Monitor	World Bank Entrepreneurship Database; Enterprise Surveys; GEM; venture databases for discovery		C2	UNCERTAIN	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Startup funding/activity sources often have selective coverage or commercial terms; formation counts are not survival quality.	COV_BELOW_90_PERCENT|LIC_AMBIGUOUS|SEM_QUESTION_TOO_BROAD
C17	Representative gross/net earnings, ideally occupation- and cost-adjusted.	ILO; World Bank; OECD; national statistical offices	ILOSTAT earnings; ILO modelled labour income; OECD average wages; ICP PPP conversion	E02|E09	C3	UNCERTAIN	MEDIUM	FAST_MOVING: latest 0–2y	MEDIUM	city/regional	SCREENED_POSSIBLE	HIGH	National averages mask occupation, tax and city-cost differences; net pay requires household scenarios.	GRA_HOUSEHOLD_SCENARIO_REQUIRED|CMP_GROSS_NET_MISMATCH|GRA_CITY_LEVEL_REQUIRED
C18	Wage growth, promotion prospects and occupational mobility over time.	ILO; OECD; national longitudinal and labour-force surveys	ILOSTAT wage growth; OECD earnings mobility; harmonised panel/microdata where available	E02	C2	NO	MEDIUM	FAST_MOVING: latest 0–3y	HIGH	city/regional	SCREENED_LOW_FEASIBILITY	LOW	Promotion and mobility require longitudinal microdata that are not globally harmonised or broadly reusable.	COV_BELOW_90_PERCENT|CMP_SURVEY_NOT_HARMONISED|LIC_AMBIGUOUS
C19	Formal and effective protection on hours, leave, dismissal, bargaining and core labour rights.	ILO; national labour ministries	ILO NATLEX/NORMLEX/EPLex; ILOSTAT working time; convention ratification; official statutes	E15|E02	C3	UNCERTAIN	MEDIUM	STATIC_OR_LEGAL_ASOF plus annual outcomes	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Law, ratification and enforcement are distinct; comparable coding requires current legal review.	CMP_LEGAL_NOT_LIVED_OUTCOME|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C20	Digital and legal practicality of remote work, including connectivity, visas, coworking and time-zone fit.	ITU; official immigration authorities; commercial coworking/latency providers	ITU connectivity; digital-nomad visa rules; coworking directories; time-zone calculation	E05	C2	NO	MEDIUM	CURRENT_POLICY/FAST_MOVING	HIGH	profile-derived	SCREENED_LOW_FEASIBILITY	LOW	It overlaps internet and visas, while time zone and legal fit depend on employer and user origin.	RED_SHARED_COMPONENTS|PRF_PROFILE_ONLY|LIC_AMBIGUOUS
C21	Effective personal income-tax burden for representative income and household cases.	National tax authorities; OECD; IMF/World Bank for denominators	Official tax schedules/calculators; OECD Taxing Wages; PwC/KPMG summaries for discovery	E11	C3	NO	MEDIUM	CURRENT_POLICY: current tax year	HIGH	national	SCREENED_POSSIBLE	HIGH	OECD's comparable effective-tax model covers only 38 countries; global extension requires maintained official-rule coding.	COV_BELOW_90_PERCENT|OPS_EXCESSIVE_MANUAL_MAINTENANCE|GRA_HOUSEHOLD_SCENARIO_REQUIRED
C22	Employee/employer payroll, pension and other compulsory contribution burden.	National social-security/tax authorities; OECD; ILO	Official contribution schedules; OECD Taxing Wages; ILO Social Security Inquiry	E11|E15	C3	NO	MEDIUM	CURRENT_POLICY: current contribution year	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Global comparability is constrained by ceilings, benefit entitlements and the same OECD coverage limit.	COV_BELOW_90_PERCENT|CMP_DEFINITION_DIFFERS|GRA_HOUSEHOLD_SCENARIO_REQUIRED
C23	VAT/GST/sales-tax rates and household exposure to indirect taxation.	National tax authorities; IMF; OECD; World Bank	Official VAT/GST schedules; IMF tax databases; OECD Consumption Tax Trends; household expenditure weights		C2	NO	MEDIUM	CURRENT_POLICY: current tax year	HIGH	national	SCREENED_LOW_FEASIBILITY	LOW	Headline rates are broad but effective burden needs country-specific exemptions and household consumption baskets.	GRA_HOUSEHOLD_SCENARIO_REQUIRED|COV_BELOW_90_PERCENT|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C24	Relative household-consumption price level against a common benchmark.	World Bank ICP	ICP household-consumption PPP and price-level indexes	E09	C4	YES	FULL	SLOW_STRUCTURAL/annual extrapolation	LOW	unsuitable independent	DEFERRED	NO FURTHER WORK	Already represented in Konsider; retain as an existing monitor, not a new Phase 3 research target.	RED_EXISTING_CRITERION
C25	Rent/home-price burden relative to income and availability in likely migrant destinations.	National statistical offices; OECD; Eurostat; central banks; city housing observatories	OECD affordable housing; official rent/price indexes; housing-cost-overburden; city rent datasets		C2	NO	MEDIUM	FAST_MOVING: latest 0–2y	HIGH	city/regional	DEFERRED_CITY_LAYER	HIGH	High decision value justifies strategic research, but a national average is misleading and global city rent data are often commercial.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C26	Out-of-pocket spending, insurance burden and financial-protection risk.	WHO; World Bank; national health accounts	WHO GHO out-of-pocket share; catastrophic health spending; UHC financial protection; national insurance rules	E04	C3	UNCERTAIN	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y	MEDIUM	national	SCREENED_POSSIBLE	MEDIUM	Aggregate out-of-pocket shares do not describe immigrant eligibility, premiums or point-of-care prices.	GRA_HOUSEHOLD_SCENARIO_REQUIRED|CMP_POPULATION_DIFFERS
C27	Childcare fees and other recurring family costs for representative households.	OECD; UNICEF; national ministries/statistical offices; city providers	OECD net childcare costs; UNICEF family policies; official childcare fee/coverage schedules		C2	NO	LOW	FAST_MOVING: latest 0–2y	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Fees depend on age, city, income, subsidies and immigration status; OECD-style comparisons do not approach global coverage.	GRA_CITY_LEVEL_REQUIRED|GRA_HOUSEHOLD_SCENARIO_REQUIRED|COV_BELOW_90_PERCENT
C28	Net income remaining after taxes and essential household costs.	Derived from approved earnings, tax, housing, health and childcare components	Profile calculator; no independent dataset		C1	N/A	N/A	Derived from component vintages	HIGH	profile-derived	DEFERRED_PROFILE_LAYER	LOW	This is a profile-derived composite with shared inputs and scenario weights, not an independent criterion.	PRF_PROFILE_ONLY|RED_SHARED_COMPONENTS|SCO_COMPOSITE_WEIGHTS_ARBITRARY
C29	Inflation, exchange-rate volatility and broad macro/sovereign stability.	IMF; World Bank; BIS; national central banks	IMF WEO/IFS; World Bank WDI inflation/exchange rates; sovereign risk only as supplement	E10	C4	YES	HIGH	FAST_MOVING: monthly/biannual, latest 0–1y	MEDIUM	national	SCREENED_PROMISING	MEDIUM	A transparent small indicator set is preferable to a proprietary sovereign-risk composite.	LIC_AMBIGUOUS|SCO_COMPOSITE_WEIGHTS_ARBITRARY
C30	International migrant or foreign-born stock as a share of resident population.	UN DESA Population Division; World Bank representation; national censuses	International Migrant Stock 2024 total destination and population denominator	E03	C3	YES	FULL	SLOW_STRUCTURAL: 2024 edition; census-driven updates	MEDIUM	national	SCREENED_PROMISING	HIGH	The source mixes country-of-birth and citizenship definitions and many 2024 values are extrapolated.	CMP_DEFINITION_DIFFERS|CMP_IMPUTED_VALUES_REQUIRED
C31	Size, origin diversity and local concentration of established migrant communities.	UN DESA; national censuses/statistical offices	UN migrant stock by origin/destination; census foreign-born by origin; city population tables	E03	C3	UNCERTAIN	MEDIUM	SLOW_STRUCTURAL: census/2024 stock	MEDIUM	city/regional	DEFERRED_CITY_LAYER	LOW	Origin-specific usefulness and city concentration make a single national diversity score weak.	GRA_ORIGIN_SPECIFIC|GRA_CITY_LEVEL_REQUIRED|SCO_NO_CLEAR_DIRECTION
C32	Accessibility of skilled-worker routes under a fixed worker profile and policy date.	National immigration authorities; EU Immigration Portal; OECD/ILO as cross-checks	Official visa statutes, occupation lists, salary thresholds, quotas, processing guidance		C2	NO	LOW	CURRENT_POLICY: current as-of snapshot	HIGH	profile-derived	SCREENED_POSSIBLE	HIGH	No global ready-made dataset; eligibility depends on occupation, salary, origin, sponsor and changing rules.	GRA_ORIGIN_SPECIFIC|GRA_PROFESSION_SPECIFIC|OPS_EXCESSIVE_MANUAL_MAINTENANCE|COV_BELOW_90_PERCENT
C33	Time, eligibility and predictability of permanent residence under defined scenarios.	National immigration authorities; EU Immigration Portal; OECD	Official residence statutes/guidance; long-term residence rules; policy coding		C2	NO	LOW	CURRENT_POLICY: current as-of snapshot	HIGH	profile-derived	SCREENED_POSSIBLE	HIGH	PR eligibility is route-, origin- and family-dependent and needs maintained legal coding.	GRA_ORIGIN_SPECIFIC|PRF_PROFILE_ONLY|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C34	Time and restrictions for naturalisation, including dual citizenship and tests.	National citizenship authorities; UNHCR/Global Citizenship Observatory; OECD	Official nationality laws; GLOBALCIT modes/law databases; dual-citizenship rules		C3	UNCERTAIN	MEDIUM	STATIC_OR_LEGAL_ASOF: current	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Formal law is codable, but discretion, residence counting and policy updates complicate a scalar score.	CMP_LEGAL_NOT_LIVED_OUTCOME|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C35	Ability of international graduates to stay, work and transition after study.	National immigration authorities; OECD; UNESCO/OECD student-mobility systems	Official post-study work rules; OECD retention indicators; student-to-work transition rules	E01	C2	NO	LOW	CURRENT_POLICY: current as-of snapshot	HIGH	profile-derived	SCREENED_POSSIBLE	MEDIUM	Pathways depend on credential level, institution, occupation and policy date.	GRA_PROFESSION_SPECIFIC|PRF_PROFILE_ONLY|COV_BELOW_90_PERCENT
C36	Ability to sponsor spouses, children, parents and other dependants.	National immigration authorities; EU Immigration Portal; OECD	Official family-reunification statutes, sponsor thresholds, waiting periods and dependant work rights		C2	NO	LOW	CURRENT_POLICY: current as-of snapshot	HIGH	profile-derived	SCREENED_POSSIBLE	MEDIUM	Family definitions, income thresholds and sponsor status differ materially; parent sponsorship is especially non-comparable.	GRA_HOUSEHOLD_SCENARIO_REQUIRED|GRA_ORIGIN_SPECIFIC|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C37	Formal immigration-policy direction, integration supports and stability of migrant access.	UN DESA; OECD; national governments; MIPEX research consortium	UN World Population Policies; OECD integration indicators; MIPEX; legal anti-discrimination components		C2	NO	MEDIUM	CURRENT_POLICY/SLOW_STRUCTURAL	HIGH	national	SCREENED_LOW_FEASIBILITY	LOW	It conflates policy intent, rights, implementation and attitudes; leading indexes have limited coverage or licensing uncertainty.	SEM_QUESTION_TOO_BROAD|COV_BELOW_90_PERCENT|CMP_LEGAL_NOT_LIVED_OUTCOME
C38	Ease of foreign-qualification recognition and entry to a specified regulated profession.	National professional regulators; WHO; UNESCO/ENIC-NARIC; OECD	Official licensing rules; WHO health-worker regulation; recognition databases; profession-specific pathways	E04	C2	NO	LOW	CURRENT_POLICY: current as-of snapshot	HIGH	profile-derived	SCREENED_POSSIBLE	MEDIUM	Origin, profession, credential and language dependence prevent a universal score; deep research should test scenario templates.	GRA_ORIGIN_SPECIFIC|GRA_PROFESSION_SPECIFIC|PRF_PROFILE_ONLY
C39	Transparency, speed and predictability of visa/immigration administration.	National immigration authorities; OECD; audit/ombudsman bodies	Official service standards and processing-time dashboards; refusal data; digitisation indicators		C2	NO	LOW	CURRENT_POLICY: current/quarterly	HIGH	national	SCREENED_LOW_FEASIBILITY	LOW	Published clocks use different case types and exclude paused/incomplete cases; rejection rates reflect applicant mix.	CMP_DEFINITION_DIFFERS|COV_BELOW_90_PERCENT|OPS_EXCESSIVE_MANUAL_MAINTENANCE
C40	Extent to which work, education, health, government and daily life can be navigated in English.	National census/statistical offices; UNESCO; EF for discovery	Census language ability/use; official-language law; education language; EF EPI only as discovery		C2	NO	MEDIUM	SLOW_STRUCTURAL: census plus current legal status	HIGH	city/regional	SCREENED_POSSIBLE	HIGH	Commercial proficiency rankings are not enough; usability varies strongly by city and domain.	GRA_CITY_LEVEL_REQUIRED|LIC_AMBIGUOUS|CMP_SURVEY_NOT_HARMONISED
C41	User-specific burden of learning and needing the local language.	Official language sources; linguistic research; FSI-style difficulty evidence	Official-language requirements; script/linguistic distance; training availability		C1	N/A	N/A	STATIC with policy updates	MEDIUM	preference-based	DEFERRED_PROFILE_LAYER	LOW	Difficulty depends on the user's known languages, profession and destination; no universal direction exists.	PRF_PREFERENCE_MATCH_REQUIRED|GRA_ORIGIN_SPECIFIC|SCO_NO_CLEAR_DIRECTION
C42	Surveyed acceptance of immigrants, discrimination experience and social trust.	Gallup; World Values Survey; regional barometers; OECD	World Poll migrant acceptance; WVS/EVS attitudes; OECD integration survey indicators; discrimination surveys		C2	NO	MEDIUM	SLOW_STRUCTURAL: survey waves 2–5y	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Global surveys differ in years and samples, and small states are often absent; lived experience varies locally.	CMP_SURVEY_NOT_HARMONISED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C43	Religious, ethnic, cultural and lifestyle diversity and practical openness.	UN agencies; WVS/regional surveys; national censuses; rights datasets	Census diversity; religious freedom; attitude surveys; migration diversity components		C1	NO	MEDIUM	SLOW_STRUCTURAL: mixed waves	HIGH	city/regional	SCREENED_LOW_FEASIBILITY	LOW	The construct mixes diversity, tolerance and freedom; direction and weights are contestable and city effects large.	SEM_QUESTION_TOO_BROAD|SCO_NO_CLEAR_DIRECTION|GRA_CITY_LEVEL_REQUIRED
C44	Legal and economic equality for women.	World Bank Women, Business and the Law	WBL 2026 legal, supportive-framework and enforcement-perception pillars	E08	C4	YES	FULL	STATIC_OR_LEGAL_ASOF: 2025-10-01	LOW	unsuitable independent	DEFERRED	NO FURTHER WORK	Already represented in Konsider; monitor the verified WBL source rather than duplicate research.	RED_EXISTING_CRITERION
C45	Legal protection, recognition and safety for LGBTQ+ people.	UN human-rights bodies; ILGA World; national legal authorities	ILGA Laws on Us/Database; UN legal findings; official statutes	E16	C3	YES	HIGH	STATIC_OR_LEGAL_ASOF: current legal snapshot	HIGH	national	SCREENED_POSSIBLE	MEDIUM	ILGA has strong scope but its 2024 report is CC BY-NC; social acceptance/safety needs separate survey evidence.	LIC_NONCOMMERCIAL_ONLY|CMP_LEGAL_NOT_LIVED_OUTCOME
C46	Intentional-homicide risk, with broader violence only where genuinely comparable.	World Bank WDI/UNODC; national justice systems	WDI intentional homicide series; UNODC homicide data		C4	YES	FULL	STANDARD_SOCIOECONOMIC: latest approved year	MEDIUM	unsuitable independent	DEFERRED	NO FURTHER WORK	Homicide is already represented; reported violent crime should not be appended without comparability evidence.	RED_EXISTING_CRITERION|CMP_REPORTING_CAPACITY_BIAS
C47	Day-to-day risk of theft, burglary, robbery, fraud and victimisation.	UNODC; national police; harmonised victimisation surveys; city safety surveys	UN-CTS recorded crime; victimisation surveys; police open data		C1	NO	LOW	FAST_MOVING: 0–2y desirable	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Recorded crime is dominated by reporting/legal differences; globally harmonised victim surveys and city coverage are sparse.	CMP_REPORTING_CAPACITY_BIAS|COV_BELOW_90_PERCENT|GRA_CITY_LEVEL_REQUIRED
C48	Conflict, political violence, unrest and continuity of normal civic life.	World Bank; UN; EU/JRC; UCDP/ACLED research sources	WGI Political Stability; INFORM human hazard; UCDP conflict data; official travel/security alerts	E07|E14	C3	YES	HIGH	SLOW_STRUCTURAL/EVENT_RISK_MODEL: annual/current edition	MEDIUM	national	SCREENED_PROMISING	MEDIUM	WGI is perception-based and conflict-event data may have licensing or reporting asymmetries.	CMP_MODEL_ASSUMPTIONS_OPAQUE|LIC_AMBIGUOUS
C49	Rule of law, corruption control, judicial confidence and institutional performance.	World Bank; UN; World Justice Project for discovery	WGI Rule of Law/Control of Corruption/Government Effectiveness; UN SDG16 indicators	E07	C3	YES	FULL	SLOW_STRUCTURAL: annual, through 2024	MEDIUM	national	SCREENED_PROMISING	MEDIUM	WGI is a composite of perceptions with margins of error; institutional trust is not identical to rule of law.	SEM_QUESTION_TOO_BROAD|SCO_UNCERTAINTY_TOO_HIGH
C50	Health-service capacity, coverage and quality using workforce, service and outcome indicators.	WHO; World Bank; IHME as research supplement	WHO GHO/UHC service coverage, workforce and beds; avoidable mortality; World Bank indicators	E04	C3	UNCERTAIN	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y	MEDIUM	national	SCREENED_POSSIBLE	HIGH	No single indicator captures access, quality and waiting time; mixed years and modelled values are likely.	SEM_QUESTION_TOO_BROAD|FRS_MIXED_REFERENCE_PERIODS|CMP_IMPUTED_VALUES_REQUIRED
C51	Ambulance access, trauma/emergency capacity and response readiness.	WHO; national emergency/health authorities; disaster agencies	WHO emergency-care system assessments; ambulance/trauma registries; Joint External Evaluation components	E04	C2	NO	LOW	STANDARD_SOCIOECONOMIC: irregular assessments	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Global emergency-care assessments are sparse and national averages cannot represent response time.	COV_BELOW_90_PERCENT|GRA_CITY_LEVEL_REQUIRED
C52	Population-weighted exposure to ambient PM2.5.	World Bank/WHO; satellite-model consortia	WDI PM2.5 mean annual exposure		C4	YES	FULL	STANDARD_SOCIOECONOMIC: latest approved model edition	LOW	unsuitable independent	DEFERRED	NO FURTHER WORK	Already represented in Konsider; city exposure may be a later layer but not a duplicate national criterion.	RED_EXISTING_CRITERION
C53	Safely managed drinking water/sanitation access and related service quality.	WHO/UNICEF JMP; World Bank; national utilities	JMP safely managed drinking water, sanitation and hygiene; wastewater indicators	E06	C4	YES	HIGH	STANDARD_SOCIOECONOMIC: estimates through 2024	MEDIUM	national	SCREENED_PROMISING	MEDIUM	JMP access is broad, but continuity, taste/contaminants and migrant-city reliability are separate constructs.	SEM_QUESTION_TOO_BROAD|GRA_CITY_LEVEL_REQUIRED
C54	Strength of food regulation, inspection and outbreak prevention/response.	WHO; FAO; national food-safety authorities	WHO IHR capacities; Codex participation; foodborne disease estimates; official inspection systems	E04	C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: irregular/annual mixed	HIGH	national	SCREENED_LOW_FEASIBILITY	LOW	Inputs and outbreak counts reflect surveillance capacity; comparable inspection-performance data are fragmented.	CMP_REPORTING_CAPACITY_BIAS|COV_BELOW_90_PERCENT
C55	Availability, affordability and acceptability of mental-health services.	WHO; national health systems; IHME	WHO Mental Health Atlas; provider density; service coverage; financial protection	E04	C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: periodic 2–5y	MEDIUM	city/regional	DEFERRED_CITY_LAYER	LOW	Provider counts do not measure affordability or stigma, and access is local with substantial missingness.	COV_BELOW_90_PERCENT|GRA_CITY_LEVEL_REQUIRED|SEM_QUESTION_TOO_BROAD
C56	Household electricity access plus outage frequency/duration and reliability.	World Bank; IEA; national regulators/utilities; Enterprise Surveys	WDI electricity access; Enterprise Surveys outages; SAIDI/SAIFI; RISE policy indicators		C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: 0–3y	MEDIUM	national	SCREENED_POSSIBLE	HIGH	Access is near-global, but outage metrics lack harmonised 90% coverage; current experimental composite overlaps access.	COV_BELOW_90_PERCENT|CMP_DEFINITION_DIFFERS|RED_EXISTING_CRITERION
C57	Continuity, shortage risk and resilience of household/urban water supply.	WHO/UNICEF JMP; national utilities; World Bank; WRI for stress	JMP availability-when-needed; utility continuity; water stress/drought indicators	E06	C2	NO	MEDIUM	STANDARD/EVENT_RISK: 0–3y	HIGH	city/regional	DEFERRED_CITY_LAYER	MEDIUM	JMP access does not ensure 24/7 supply; utility-level continuity is not globally standardised.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|CMP_DEFINITION_DIFFERS
C58	Internet adoption, mobile/fixed coverage, performance, affordability and reliability.	ITU; World Bank; national telecom regulators; measurement firms for speed	ITU DataHub/IDI components; WDI internet use; regulator QoS; Ookla/M-Lab for discovery	E05	C3	YES	HIGH	FAST_MOVING: annual/near-current	MEDIUM	national	SCREENED_PROMISING	HIGH	ITU access/coverage is broad, but speed/outage measures may be commercial or incomplete; avoid duplicating the existing composite.	LIC_AMBIGUOUS|RED_EXISTING_CRITERION
C59	Road, rail, port, airport and trade-logistics performance.	World Bank; UN transport agencies; national infrastructure ministries	Logistics Performance Index; WDI transport; UN road/rail/aviation/port indicators	E18	C3	NO	MEDIUM	SLOW_STRUCTURAL: LPI 2023/other annual	MEDIUM	national	SCREENED_LOW_FEASIBILITY	LOW	LPI has limited country coverage and is perception-based; a broad composite would overlap existing infrastructure readiness.	COV_BELOW_90_PERCENT|RED_EXISTING_CRITERION|SEM_QUESTION_TOO_BROAD
C60	Coverage, affordability, safety and reliability of public transport in destination cities.	UN-Habitat; city transit agencies; GTFS publishers; OECD/ITF	SDG 11.2.1; GTFS feeds; city route/stop/service data; fare schedules		C3	NO	LOW	FAST_MOVING: current feeds/annual	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Country scores are invalid; a fixed city universe and reusable feed policy are prerequisites.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C61	Direct-flight access, airport connectivity and travel time to relevant origins/centres.	ICAO; IATA/OAG for discovery; airport authorities; OpenFlights for discovery	ICAO air transport statistics; scheduled route data; airport connectivity indexes		C3	NO	MEDIUM	FAST_MOVING: seasonal/monthly	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Route schedules are city/airport and origin-specific; comprehensive timetable data are usually commercial.	GRA_CITY_LEVEL_REQUIRED|GRA_ORIGIN_SPECIFIC|LIC_REDISTRIBUTION_RESTRICTED
C62	Availability and maturity of online services, digital ID and digital public administration.	UN DESA; World Bank; ITU; OECD	UN E-Government Development Index/Online Service Index; World Bank GovTech Maturity Index; ID4D	E05	C3	YES	HIGH	SLOW_STRUCTURAL: biennial/current edition	MEDIUM	national	SCREENED_PROMISING	MEDIUM	Composite editions and weights require sensitivity review; user experience can diverge from formal availability.	SCO_COMPOSITE_WEIGHTS_ARBITRARY|CMP_LEGAL_NOT_LIVED_OUTCOME
C63	Combined digital and logistics readiness.	Existing Konsider inputs; World Bank/ITU	Existing experimental infrastructure readiness composite		C2	YES	FULL	Existing release cadence	LOW	unsuitable independent	DEFERRED	NO FURTHER WORK	Already available experimentally; Phase 3 should research its components rather than duplicate the composite.	RED_EXISTING_CRITERION|RED_SHARED_COMPONENTS
C64	Climatological heat, cold, humidity and seasonal exposure at likely destinations.	Copernicus/ECMWF; World Bank CCKP; national meteorological agencies	ERA5/ERA5-Land normals; CCKP ERA5/CRU aggregations; humidity/heat-index metrics	E12|E13	C4	YES	FULL	CLIMATE_NORMAL: fixed normal period/current dataset	LOW	city/regional	DEFERRED_CITY_LAYER	LOW	Global data are excellent, but national averages are misleading and comfort has no universal direction.	GRA_CITY_LEVEL_REQUIRED|PRF_PREFERENCE_MATCH_REQUIRED
C65	Match between a user's preferred warm/cold/dry/humid/four-season climate and destination conditions.	Copernicus/ECMWF; World Bank CCKP	Derived preference model over ERA5/CCKP temperature, precipitation and humidity	E12|E13	C4	YES	FULL	CLIMATE_NORMAL	LOW	preference-based	DEFERRED_PROFILE_LAYER	LOW	Data coverage is strong, but this belongs in a transparent preference model, not a higher-is-better criterion.	PRF_PREFERENCE_MATCH_REQUIRED|PRF_PROFILE_ONLY
C66	Exposure to heatwaves, floods, storms, wildfire, drought and severe cold.	EU/JRC INFORM; World Bank CCKP; WMO; UNDRR	INFORM hazard/exposure components; CCKP extreme indices; hazard-specific global datasets	E12|E14	C3	YES	HIGH	EVENT_RISK_MODEL: current 2026/model edition	MEDIUM	national	SCREENED_PROMISING	HIGH	Hazard components have different scales and city exposure; avoid double counting vulnerability/coping capacity.	SCO_COMPOSITE_WEIGHTS_ARBITRARY|GRA_CITY_LEVEL_REQUIRED
C67	Future physical exposure to sea-level rise, heat/water stress and ecosystem pressures.	World Bank CCKP; IPCC/WCRP CMIP; NASA/ESA; WRI as supplement	CCKP CMIP6 scenarios; sea-level projections; water-stress and heat-exposure datasets	E12	C3	YES	HIGH	EVENT_RISK_MODEL: current scenario/model edition	LOW	national	SCREENED_PROMISING	MEDIUM	Results depend on scenario, horizon, model ensemble and population exposure assumptions.	CMP_MODEL_ASSUMPTIONS_OPAQUE|SCO_NO_DEFENSIBLE_THRESHOLDS
C68	Expected loss/exposure from geophysical and weather-related natural hazards.	EU/JRC INFORM; UNDRR; World Bank; GEM/USGS	INFORM natural hazard/exposure; Global Assessment Report datasets; global earthquake/cyclone/flood layers	E14	C3	YES	HIGH	EVENT_RISK_MODEL: 2026/current edition	MEDIUM	national	SCREENED_PROMISING	MEDIUM	Overlaps extreme-weather risk; geophysical hazards should be separable and composite weights tested.	RED_CANDIDATE_OVERLAP|SCO_COMPOSITE_WEIGHTS_ARBITRARY
C69	Waste, water pollution, green space, noise, biodiversity and other environmental conditions.	UNEP; Yale/Columbia EPI consortium; WHO; city agencies	SDG environment indicators; EPI components; city green-space/noise/waste data		C2	NO	MEDIUM	STANDARD_SOCIOECONOMIC: mixed 0–5y	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	The construct is too broad, city-sensitive and dependent on composite weighting; EPI licensing must be checked.	SEM_QUESTION_TOO_BROAD|GRA_CITY_LEVEL_REQUIRED|LIC_AMBIGUOUS
C70	Institutional and infrastructure capacity to adapt to and recover from climate shocks.	EU/JRC INFORM; World Bank; UNDRR; ND-GAIN consortium	INFORM lack-of-coping-capacity; ND-GAIN readiness; adaptation policy indicators	E14	C3	YES	HIGH	EVENT_RISK_MODEL/SLOW_STRUCTURAL: annual edition	MEDIUM	national	SCREENED_PROMISING	MEDIUM	Readiness indexes are composite/modelled and overlap governance, infrastructure and disaster risk.	RED_SHARED_COMPONENTS|SCO_COMPOSITE_WEIGHTS_ARBITRARY
C71	Working hours, paid leave, parental leave and commute burden.	ILO; OECD; national labour authorities	ILOSTAT actual hours; ILO NATLEX leave law; OECD work-life indicators; commute surveys	E02|E15	C3	UNCERTAIN	MEDIUM	STANDARD/CURRENT_POLICY: 0–3y plus current law	HIGH	national	SCREENED_POSSIBLE	MEDIUM	Leave law is not take-up; commute is city-level and survey coverage is weak, so start with hours/leave components.	CMP_LEGAL_NOT_LIVED_OUTCOME|GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT
C72	Family-support environment spanning leave, childcare, schools, safety and recreation.	ILO; UNICEF; World Bank WBL; UNESCO; WHO	Parental-leave law; childcare support; school/health/safety component criteria	E08|E01	C2	N/A	N/A	Derived from component vintages	HIGH	profile-derived	SCREENED_POSSIBLE	MEDIUM	This is best as a transparent family profile assembled from approved components, not a new opaque dataset.	PRF_PROFILE_ONLY|RED_SHARED_COMPONENTS|SCO_COMPOSITE_WEIGHTS_ARBITRARY
C73	Urban public space, walkability, cleanliness, congestion, amenities and design.	UN-Habitat; city governments; satellite/open mapping providers	SDG 11 urban indicators; city prosperity; OpenStreetMap-derived amenities; congestion datasets		C2	NO	LOW	STANDARD/FAST_MOVING mixed	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Requires a city universe, geospatial methodology and multiple sources with uneven licensing.	GRA_CITY_LEVEL_REQUIRED|COV_BELOW_90_PERCENT|LIC_AMBIGUOUS
C74	Access to sports, arts, libraries, dining, nature and community activity.	UNESCO; city cultural agencies; open mapping; commercial POI providers	Cultural participation statistics; protected-area access; POI/amenity inventories		C1	NO	LOW	STANDARD/FAST_MOVING mixed	HIGH	city/regional	DEFERRED_CITY_LAYER	LOW	Amenity value is preference-based, highly local and usually reliant on commercial or volunteered POI data.	GRA_CITY_LEVEL_REQUIRED|PRF_PREFERENCE_MATCH_REQUIRED|LIC_AMBIGUOUS
C75	Formal and practical religious freedom, expression and civic participation.	UN human-rights mechanisms; OHCHR; national law; V-Dem/Freedom House for research	UN treaty/UPR evidence; official constitutional law; V-Dem freedom indicators; WGI Voice	E07	C3	YES	HIGH	STATIC_OR_LEGAL_ASOF/SLOW_STRUCTURAL	MEDIUM	national	SCREENED_POSSIBLE	LOW	Legal guarantees and lived freedom diverge; prominent indices mix expert judgments and may have reuse restrictions.	CMP_LEGAL_NOT_LIVED_OUTCOME|LIC_AMBIGUOUS
C76	Eligibility and adequacy of unemployment, pension, disability and family benefits.	ILO; World Bank; OECD; national social-security authorities	ILO World Social Protection Database; NATLEX; ASPIRE; OECD SOCX	E15	C3	UNCERTAIN	MEDIUM	STANDARD/CURRENT_POLICY mixed	HIGH	profile-derived	SCREENED_POSSIBLE	LOW	Benefit access and value depend on contributions, residence, immigration status and household scenario.	PRF_PROFILE_ONLY|GRA_HOUSEHOLD_SCENARIO_REQUIRED|COV_BELOW_90_PERCENT
C77	Combined suitability for older migrants: health, cost, pensions, residency, safety and lifestyle.	Derived from approved component criteria; national retirement visa authorities	Profile composite plus official retirement-residence rules		C1	N/A	N/A	Derived/current policy	HIGH	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Overlaps C84 and combines incompatible profile inputs; retain only one retirement profile after component approval.	PRF_PROFILE_ONLY|RED_CANDIDATE_OVERLAP|RED_SHARED_COMPONENTS
C78	Average self-reported life evaluation of residents.	Gallup; World Happiness Report; OECD as supplement	Gallup World Poll Cantril Ladder; WHR 2026 three-year averages	E17	C4	UNCERTAIN	MEDIUM	SLOW_STRUCTURAL: 2023–2025 average	HIGH	national	SCREENED_LOW_FEASIBILITY	LOW	The measure is comparable but misses some small states, is an outcome rather than an actionable lever, and Gallup reuse terms need audit.	COV_BELOW_90_PERCENT|LIC_AMBIGUOUS|SEM_NOT_ACTIONABLE
C79	Profile score for a software professional using jobs, pay, tax, English, visas and ecosystem.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit profile composite; no independent source search is warranted.	PRF_PROFILE_ONLY|RED_SHARED_COMPONENTS
C80	Profile score for a medical professional using demand, licensing, language, pay and visas.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit profession/profile composite; research its components instead.	PRF_PROFILE_ONLY|GRA_PROFESSION_SPECIFIC|RED_SHARED_COMPONENTS
C81	Student profile score using education, tuition, access, safety and post-study routes.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit profile composite; no independent criterion dataset exists.	PRF_PROFILE_ONLY|RED_SHARED_COMPONENTS
C82	Family-with-children profile score using schools, safety, health, housing and migration rules.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit household profile; component evidence and weights must remain visible.	PRF_PROFILE_ONLY|GRA_HOUSEHOLD_SCENARIO_REQUIRED|RED_SHARED_COMPONENTS
C83	Entrepreneur profile score using formation, finance, tax, immigration, markets and digital government.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit profile composite; research component criteria rather than seek a single index.	PRF_PROFILE_ONLY|RED_SHARED_COMPONENTS
C84	Retiree profile score using health, affordability, climate, residency, safety and life quality.	Derived from approved component criteria	Profile calculation only		C1	N/A	N/A	Derived from components	N/A	profile-derived	DEFERRED_PROFILE_LAYER	NO FURTHER WORK	Explicit preference/profile composite and duplicate of C77's intended decision.	PRF_PROFILE_ONLY|RED_CANDIDATE_OVERLAP|RED_SHARED_COMPONENTS
`.trim();

const rows = raw.split(/\r?\n/).map((line) => {
  const parts = line.split("\t");
  if (parts.length !== 15) {
    throw new Error(`Expected 15 fields, got ${parts.length}: ${line}`);
  }
  const [
    criterion_id, measures, publisher_families_preliminary, dataset_families_preliminary,
    refs, comparability_grade_estimate, coverage_90_plausibility_estimate,
    expected_coverage_band, freshness_estimate, licensing_uncertainty,
    natural_granularity, finding_status, deep_research_priority,
    downgrade_rationale, reasonCodes
  ] = parts;
  const source = byId[criterion_id];
  if (!source) throw new Error(`Unknown criterion ${criterion_id}`);
  const deepIndex = deepRanked.indexOf(criterion_id);
  return {
    criterion_id,
    source_item_number: source.source_item_number,
    name: source.name,
    category: source.category,
    measures,
    classification_tags: source.classification_tags,
    phase3a_granularity: source.natural_granularity,
    natural_granularity,
    likely_authoritative_publisher_families: publisher_families_preliminary.split("; "),
    likely_dataset_or_indicator_families: dataset_families_preliminary.split("; "),
    evidence_refs: refs ? refs.split("|") : [],
    fact_estimate_boundary: {
      measures: "VERIFIED_FROM_USER_SEARCH_SPACE",
      publisher_dataset_family_existence: refs ? "VERIFIED_WHERE_CITED; CANDIDATE_FIT_PRELIMINARY" : "PRELIMINARY_HYPOTHESIS",
      comparability_coverage_freshness_licensing: "PRELIMINARY_ESTIMATE_NOT_AUDITED"
    },
    cross_country_comparability_estimate: comparability_grade_estimate,
    coverage_90_percent_plausible_estimate: coverage_90_plausibility_estimate,
    expected_coverage_band_estimate: expected_coverage_band,
    likely_freshness: freshness_estimate,
    licensing_uncertainty,
    finding_status,
    deep_research_priority,
    deep_research_rank: deepIndex >= 0 ? deepIndex + 1 : null,
    recommended_batch: batch1.includes(criterion_id) ? "BATCH_1" : batch2.includes(criterion_id) ? "BATCH_2" : null,
    downgrade_rationale,
    reason_codes: reasonCodes.split("|")
  };
});

const ids = rows.map((r) => r.criterion_id);
if (rows.length !== 84 || new Set(ids).size !== 84) {
  throw new Error(`Expected 84 unique rows, got ${rows.length}/${new Set(ids).size}`);
}
for (let i = 1; i <= 84; i += 1) {
  const id = `C${String(i).padStart(2, "0")}`;
  if (!ids.includes(id)) throw new Error(`Missing ${id}`);
}
if (deepRanked.length < 35 || deepRanked.length > 45) throw new Error("Deep list size outside requested range");
if (batch1.length < 12 || batch1.length > 15 || batch2.length < 12 || batch2.length > 15) {
  throw new Error("Batch size outside requested range");
}

const output = {
  phase_id: "3B",
  version: "1.0-preliminary-screen",
  date: "2026-07-24",
  universe_id: master.universe_id,
  universe_size: master.universe_size,
  screening_threshold: master.screening_probe_threshold,
  scope_note: "Lightweight Gate A screening only. No exhaustive licensing audit, no measured 91-country coverage audit, and no production approval.",
  fact_estimate_legend: {
    VERIFIED_FROM_USER_SEARCH_SPACE: "Criterion construct is taken from the supplied 84-item search space.",
    VERIFIED_WHERE_CITED: "A cited official/primary page confirms that the publisher or dataset family exists and supports the stated scope/freshness fact.",
    PRELIMINARY_ESTIMATE: "Fit, comparability, stable-universe coverage, licensing fit, and priority remain hypotheses for Phase 3C unless explicitly stated otherwise."
  },
  deep_research_ranked_ids: deepRanked,
  recommended_batches: { first: batch1, second: batch2 },
  evidence_register: evidence,
  criteria: rows
};

fs.mkdirSync(__dirname, { recursive: true });
fs.writeFileSync(path.join(__dirname, "phase3b_screening.json"), `${JSON.stringify(output, null, 2)}\n`, "utf8");

const csvHeaders = [
  "criterion_id","source_item_number","name","category","measures","classification_tags",
  "phase3a_granularity","natural_granularity","likely_authoritative_publisher_families",
  "likely_dataset_or_indicator_families","evidence_refs","cross_country_comparability_estimate",
  "coverage_90_percent_plausible_estimate","expected_coverage_band_estimate","likely_freshness",
  "licensing_uncertainty","finding_status","deep_research_priority","deep_research_rank",
  "recommended_batch","downgrade_rationale","reason_codes","fact_estimate_boundary"
];
const csvEscape = (value) => {
  if (value === null || value === undefined) return "";
  const text = Array.isArray(value) ? value.join(" | ") : typeof value === "object" ? JSON.stringify(value) : String(value);
  return `"${text.replace(/"/g, '""')}"`;
};
const csv = [
  csvHeaders.map(csvEscape).join(","),
  ...rows.map((row) => csvHeaders.map((key) => csvEscape(row[key])).join(","))
].join("\r\n");
fs.writeFileSync(path.join(__dirname, "phase3b_screening.csv"), `${csv}\r\n`, "utf8");

const mdEscape = (value) => String(value).replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
const shortSource = (row) => `${row.likely_authoritative_publisher_families.join("; ")} — ${row.likely_dataset_or_indicator_families.join("; ")}`;
const comparison = (row) => `${row.cross_country_comparability_estimate}; 90% ${row.coverage_90_percent_plausible_estimate} (${row.expected_coverage_band_estimate})`;
const evidenceLinks = Object.entries(evidence)
  .map(([id, item]) => `- **${id}.** ${item.claim} [Primary source](${item.url}) (checked ${item.checked}).`)
  .join("\n");
const statusCounts = Object.fromEntries([...new Set(rows.map((r) => r.finding_status))].sort().map((s) => [s, rows.filter((r) => r.finding_status === s).length]));
const granularityCounts = Object.fromEntries([...new Set(rows.map((r) => r.natural_granularity))].sort().map((s) => [s, rows.filter((r) => r.natural_granularity === s).length]));
const priorityCounts = Object.fromEntries(["HIGH","MEDIUM","LOW","NO FURTHER WORK"].map((s) => [s, rows.filter((r) => r.deep_research_priority === s).length]));
const rankedLines = deepRanked.map((id, index) => {
  const row = rows.find((r) => r.criterion_id === id);
  return `${index + 1}. **${id} — ${row.name}** (${row.deep_research_priority}; ${row.finding_status}) — ${row.downgrade_rationale}`;
}).join("\n");
const batchLines = (idsForBatch) => idsForBatch.map((id, index) => {
  const row = rows.find((r) => r.criterion_id === id);
  return `${index + 1}. ${id} — ${row.name}`;
}).join("\n");
const cityRows = rows.filter((r) => r.natural_granularity === "city/regional");
const cityLines = cityRows.map((r) => `- **${r.criterion_id} — ${r.name}:** ${r.downgrade_rationale}`).join("\n");

const categoryOrder = [...new Set(rows.map((r) => r.category))];
const tables = categoryOrder.map((category) => {
  const categoryRows = rows.filter((r) => r.category === category);
  const body = categoryRows.map((row) =>
    `| ${row.criterion_id} | ${mdEscape(row.name)} | ${mdEscape(row.measures)} | ${mdEscape(shortSource(row))} | ${mdEscape(comparison(row))} | ${mdEscape(row.likely_freshness)}; licence ${row.licensing_uncertainty} | ${mdEscape(row.natural_granularity)} | ${row.finding_status} | ${row.deep_research_priority} | ${mdEscape(row.downgrade_rationale)} |`
  ).join("\n");
  return `### ${category}\n\n| ID | Criterion | What it measures | Likely publisher and dataset families (preliminary fit) | Comparability and 90% coverage estimate | Freshness; licence uncertainty | Natural granularity | Finding | Deep priority | Downgrade/caveat |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n${body}`;
}).join("\n\n");

const publisherSummary = `
| Recurring family | Best-fit criterion groups | Verified family fact | Main Phase 3C questions |
| --- | --- | --- | --- |
| UNESCO UIS / World Bank education | C01–C08 and R&D inputs | UIS exposes metadata, API/bulk data and a February 2026 release (E01). | Indicator-level 82/91 overlap, licence terms, mixed assessment years, and whether quality is overclaimed. |
| ILOSTAT / ILO legal systems | C11–C23, C71, C76 | ILOSTAT has reproducible bulk data; NATLEX/NORMLEX contain national legal materials (E02, E15). | Occupation detail, latest-year coverage, legal-versus-lived outcomes, and reuse terms. |
| World Bank / IMF economic families | C16–C29, C48–C50, C59, C62 | ICP, WGI, WBL and WEO are broad official families (E07–E10, E18). | Avoid composites hiding uncertainty; verify dataset-specific licences and stable-universe row coverage. |
| UN DESA migration | C30–C31 and context for C32–C39 | Migrant Stock 2024 covers 233 countries/areas (E03). | Definition mixing and extrapolation; it does not solve current legal-pathway coding. |
| WHO / WHO-UNICEF JMP | C13, C26, C50–C55, C57 | WHO GHO has a country/indicator API; JMP reports WASH estimates through 2024 (E04, E06). | Mixed reference years, modelled values, immigrant eligibility, and city service continuity. |
| ITU | C20, C58, C62 | DataHub covers nearly 200 economies and multiple connectivity dimensions (E05). | Licence clarity, exact 82/91 overlap, and whether speed/reliability require a second source. |
| World Bank CCKP / Copernicus ERA5 | C64–C70 | Global climate data and country/subnational access are available (E12, E13). | Aggregation geography, scenario/horizon choice, normal period, and preference scoring. |
| EU/JRC INFORM | C48, C66, C68, C70 | INFORM Risk 2026 is open with source data and calculation steps (E14). | Separate hazard, vulnerability and coping capacity; licensing/attribution and double counting. |
| Survey/rights consortia | C42–C45, C75, C78 | WBL is CC BY 4.0; ILGA's report is BY-NC; WHR publishes selected averages (E08, E16, E17). | Commercial microdata rights, missing small states, legal-versus-lived outcomes, and survey uncertainty. |
`;

const report = `# Konsider Phase 3B — Lightweight screening of 84 criteria

**Date:** 24 July 2026
**Universe:** \`${master.universe_id}\` (${master.universe_size} countries)
**Normal Phase 3 probe threshold:** ${master.screening_probe_threshold.minimum_validated}/${master.universe_size} (at least ${master.screening_probe_threshold.percentage}%)
**Scope:** Gate A screening only. This report does **not** approve sources, measure country coverage, or complete a licensing audit.

## Executive finding

The screen retains **${deepRanked.length} criteria** for deeper research. The first two batches contain **${batch1.length}** criteria each. High-value legal mobility, tax and housing criteria remain in the research list despite weak apparent coverage because Phase 3A explicitly permits strategic study of central relocation gates.

- Finding-status counts: ${Object.entries(statusCounts).map(([k,v]) => `${k} ${v}`).join("; ")}.
- Natural-granularity counts: ${Object.entries(granularityCounts).map(([k,v]) => `${k} ${v}`).join("; ")}.
- Priority counts: ${Object.entries(priorityCounts).map(([k,v]) => `${k} ${v}`).join("; ")}.
- The strongest apparent national-data candidates are C11, C29, C30, C48, C49, C53, C62, C66–C70 and selected education/health components.
- The clearest city-layer deferrals are housing, international schools, everyday crime, emergency care, water continuity, transit, flight connectivity, urban life, recreation and non-PM2.5 environmental quality.
- C79–C84 are profile calculations, not independent source searches. C24, C44, C46, C52 and C63 already overlap existing Konsider criteria.

## Fact versus estimate boundary

- **Verified facts:** criterion definitions come from the supplied search-space document; cited official/primary pages verify that named publisher/dataset families exist and support the specific scope, date or licensing fact stated in the evidence register.
- **Preliminary estimates:** every criterion-level fit judgment, C0–C4 comparability grade, 90%-coverage plausibility, coverage band, freshness expectation, licensing-uncertainty flag, granularity decision, status and priority.
- **Not performed:** row-by-row downloads, 91-country joins, current-policy legal coding, exact licence-chain review, commercial-use legal advice, or measured freshness validation.

## Ranked list for deeper research (${deepRanked.length})

${rankedLines}

## Recommended first batch (${batch1.length})

${batchLines(batch1)}

This batch balances immediately measurable national families with the most important strategic exceptions: jobs, pay, tax, housing, migration pathways, healthcare, English usability, digital/electric reliability, education and hazard risk.

## Recommended second batch (${batch2.length})

${batchLines(batch2)}

This batch tests profession and family migration rules, research/sector job signals, labour rights and contributions, healthcare affordability, macro stability and governance. It should be revised if Batch 1 reveals a reusable current-policy coding framework or an early hard licensing blocker.

## Recurring publisher and dataset families

${publisherSummary}

## Criteria likely to require city-level treatment

${cityLines}

## All 84 screening rows

Reading guide: publisher/dataset entries are **candidate families**, not approved sources. “90% YES” means plausibility only, not a measured 82/91 result.

${tables}

## Evidence register — verified family-level facts

${evidenceLinks}

## Handoff to Phase 3C

For each selected criterion, Phase 3C should replace family names with exact dataset/table/series candidates; capture dataset-specific terms; measure fresh/validated coverage against all 91 ISO codes; record missingness by region; and preserve legal, survey, model and city-layer limitations separately. No criterion in this report is production-approved.
`;
fs.writeFileSync(
  path.join(__dirname, "phase3b_screening.md"),
  `${report.trimEnd()}\n`,
  "utf8",
);

console.log(JSON.stringify({
  rows: rows.length,
  deep_research: deepRanked.length,
  batch1: batch1.length,
  batch2: batch2.length,
  statusCounts,
  granularityCounts,
  priorityCounts
}, null, 2));
