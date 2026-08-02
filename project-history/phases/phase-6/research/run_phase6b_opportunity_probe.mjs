import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

const REPORT_DATE = "2026-08-02";
const RELEASE_ID = "2026-07-29.2";
const FRESHNESS_MIN_YEAR = 2021;
const BASE_PERCENTILE = 0.6;
const SENSITIVITY_PERCENTILES = [0.5, 0.6, 0.7];

const EXPECTED_RAW_HASHES = {
  ilo_observed_occupation: "aaadd9ad52c88af5b00edce9c78821481d352251fe1ee944bb9bff299bdd04d4",
  ilo_modelled_occupation: "00c76b161f5308f6655bac28ac3b6edeca25f4d262fc694e1aec5c310ef89986",
  ilo_modelled_economy: "ab1baf83fb7f3cd3646df98b129571c21651e65fe49237efc873bff7e832efef",
  ilo_observed_economy: "f66ac2ba0364f70a2ed1709d99d7e2c5786819fae703247f8cb3642e7895aa96",
  world_bank_metadata: "d29d57f8adf954c5e2a1520a02fb2c7b45575d8db3bd327a9dff47d66914231c",
};

const EXPECTED_BENCHMARK_TOP20 = {
  general_balanced: ["AUS", "NZL", "SWE", "CHE", "NOR", "NLD", "LUX", "JPN", "SGP", "CAN", "EST", "DEU", "MLT", "DNK", "IRL", "GBR", "KOR", "FIN", "ISL", "AUT"],
  affordability_sensitive: ["SGP", "MLT", "AUS", "NZL", "JPN", "NOR", "NLD", "LUX", "EST", "CZE", "KOR", "SVN", "CYP", "SWE", "PRT", "CAN", "DEU", "HUN", "ARE", "AUT"],
  safety_governance_oriented: ["NZL", "AUS", "NOR", "LUX", "CHE", "ISL", "NLD", "JPN", "DNK", "SWE", "IRL", "CAN", "FIN", "CZE", "EST", "MLT", "DEU", "AUT", "SVN", "KOR"],
  career_prioritised: ["SGP", "CHE", "NLD", "MLT", "AUS", "NZL", "ISL", "NOR", "SWE", "KOR", "JPN", "DNK", "LUX", "DEU", "ARE", "IRL", "GBR", "CAN", "CYP", "EST"],
  family_education_oriented: ["AUS", "NZL", "LUX", "NOR", "SWE", "FIN", "CAN", "EST", "JPN", "CHE", "NLD", "AUT", "IRL", "DNK", "SVN", "DEU", "CZE", "ESP", "PRT", "BEL"],
};

const CANDIDATES = {
  technology_software_opportunity: {
    display_name: "Technology and software employment ecosystem",
    original_scope: "Technology/software",
    construct: "Employment in ISCO-08 groups 25 and 35, measured as both national employment scale and employment share.",
    primary_route: "observed_technology_occupation",
    decision: "HOLD_SOURCE_GAP",
    decision_reason: "The exact observed route is assessable for 61 countries, but only 15 of 20 countries are assessable in four career-relevant benchmark shortlists; Canada, Japan, Korea, Malta and New Zealand are material gaps.",
  },
  science_engineering_opportunity: {
    display_name: "Science and engineering employment ecosystem",
    original_scope: "Science/engineering",
    construct: "Employment in ISCO-08 groups 21 and 31, measured as both national employment scale and employment share.",
    primary_route: "observed_science_engineering_occupation",
    decision: "HOLD_SOURCE_GAP",
    decision_reason: "The exact observed route is assessable for 66 countries, but four benchmark shortlists reach only 15 of 20; the modelled professional/technician aggregate is too broad to repair the construct.",
  },
  health_social_work_opportunity: {
    display_name: "Health and social-work employment ecosystem",
    original_scope: "Healthcare",
    construct: "Employment in ISIC Rev.4 section Q (human health and social work), measured as both national employment scale and employment share.",
    primary_route: "modelled_health_social_work_sector",
    decision: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    decision_reason: "The modelled section-Q route is assessable for 88 countries and all five benchmark top-20 lists, but it cannot be presented as healthcare alone because it includes social work.",
  },
  finance_insurance_opportunity: {
    display_name: "Finance and insurance employment ecosystem",
    original_scope: "Business/finance/administration",
    construct: "Employment in ISIC Rev.4 section K (financial and insurance activities), measured as both national employment scale and employment share.",
    primary_route: "modelled_finance_insurance_sector",
    decision: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    decision_reason: "The modelled section-K route is assessable for 88 countries and all benchmark lists; it supports finance and insurance, not the broader business/administration label.",
  },
  research_academia_opportunity: {
    display_name: "Research and academia opportunity",
    original_scope: "Research/academia",
    construct: "Field-relevant research employment or active hiring, with research output and institutions only as supporting evidence.",
    primary_route: "observed_research_development_sector",
    decision: "HOLD_SOURCE_GAP",
    decision_reason: "Fresh ISIC M72 employment is assessable for only 54 countries and measures research-and-development activity rather than academia; innovation-output evidence cannot safely produce a negative opportunity state.",
  },
  skilled_trades_construction_opportunity: {
    display_name: "Skilled-trades or construction employment ecosystem",
    original_scope: "Skilled trades/construction",
    construct: "A strong signal may be established by either ISCO-08 major group 7 employment or ISIC Rev.4 section F construction employment, each tested on national scale and share.",
    primary_route: "modelled_skilled_trades_or_construction",
    decision: "APPROVE_FOR_IMPLEMENTATION_DESIGN",
    decision_reason: "Both transparent modelled routes are available for the same 88 countries, cover every benchmark top-20 list, and retain an explicit OR rule without a composite score.",
  },
};

const PROFILE_WEIGHTS = {
  career_prioritised: {
    C66: 0.2, C67: 0.2, ambient_pm25_population_weighted: 0.2,
    established_immigrant_presence: 0.5, household_consumption_price_level_us_100: 0.3,
    infrastructure_readiness_composite: 0.6, intentional_homicide_rate: 0.3,
    overall_job_market_opportunity: 1, political_stability: 0.4,
    research_innovation_ecosystem: 0.8, rule_of_law: 0.4,
    school_education_quality: 0.2, women_legal_economic_equality: 0.3,
  },
  family_education_oriented: {
    C66: 0.6, C67: 0.6, ambient_pm25_population_weighted: 0.7,
    established_immigrant_presence: 0.6, household_consumption_price_level_us_100: 0.6,
    infrastructure_readiness_composite: 0.7, intentional_homicide_rate: 1,
    overall_job_market_opportunity: 0.4, political_stability: 0.8,
    research_innovation_ecosystem: 0.4, rule_of_law: 0.8,
    school_education_quality: 1, women_legal_economic_equality: 0.8,
  },
};

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (quoted && character === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += character;
    }
  }
  values.push(current);
  return values;
}

function quantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

function round(value, digits = 8) {
  return Number(value.toFixed(digits));
}

function json(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function countBy(rows, key) {
  return Object.fromEntries(
    [...new Set(rows.map((row) => row[key]))].sort().map((value) => [
      value,
      rows.filter((row) => row[key] === value).length,
    ]),
  );
}

function thresholdsFor(observations, percentile) {
  const low = Math.max(0, percentile - 0.2);
  const high = Math.min(1, percentile + 0.2);
  const scales = observations.map((row) => row.scale_thousands);
  const shares = observations.map((row) => row.share_percent);
  return {
    base_scale_thousands: quantile(scales, percentile),
    base_share_percent: quantile(shares, percentile),
    high_scale_thousands: quantile(scales, high),
    high_share_percent: quantile(shares, high),
    low_scale_thousands: quantile(scales, low),
    low_share_percent: quantile(shares, low),
  };
}

function routePasses(observation, thresholds) {
  if (!observation) return false;
  return (
    (observation.scale_thousands >= thresholds.base_scale_thousands &&
      observation.share_percent >= thresholds.base_share_percent) ||
    (observation.scale_thousands >= thresholds.high_scale_thousands &&
      observation.share_percent >= thresholds.low_share_percent) ||
    (observation.share_percent >= thresholds.high_share_percent &&
      observation.scale_thousands >= thresholds.low_scale_thousands)
  );
}

function thresholdDescription(thresholds) {
  return {
    rule: "(scale >= P60 and share >= P60) OR (scale >= P80 and share >= P40) OR (share >= P80 and scale >= P40)",
    frozen_values: Object.fromEntries(
      Object.entries(thresholds).map(([key, value]) => [key, round(value, 6)]),
    ),
  };
}

async function readJsonLines(filePath) {
  return (await fs.readFile(filePath, "utf8"))
    .trim()
    .split(/\r?\n/)
    .filter(Boolean)
    .map(JSON.parse);
}

async function loadModelled(filePath, prefix, wantedCodes, countrySet) {
  const lines = (await fs.readFile(filePath, "utf8")).trim().split(/\r?\n/);
  const headers = parseCsvLine(lines[0].replace(/^\uFEFF/, ""));
  const at = Object.fromEntries(headers.map((name, index) => [name, index]));
  const selected = new Map();
  for (const line of lines.slice(1)) {
    const row = parseCsvLine(line);
    const countryCode = row[at.ref_area];
    if (
      !countrySet.has(countryCode) ||
      row[at.sex] !== "SEX_T" ||
      row[at.time] !== "2025"
    ) continue;
    const classCode = row[at.classif1].replace(prefix, "");
    if (!wantedCodes.has(classCode)) continue;
    if (!row[at.obs_value]?.trim()) continue;
    const value = Number(row[at.obs_value]);
    if (!Number.isFinite(value)) continue;
    const current = selected.get(countryCode) ?? {};
    if (current._source_id && current._source_id !== row[at.source]) {
      throw new Error(`Multiple modelled source identifiers for ${countryCode}/2025.`);
    }
    current._source_id = row[at.source];
    current[classCode] = value;
    selected.set(countryCode, current);
  }
  return selected;
}

function modelledObservations(selected, numeratorCodes) {
  const result = new Map();
  for (const [countryCode, row] of selected.entries()) {
    if (
      !Number.isFinite(row.TOTAL) ||
      row.TOTAL <= 0 ||
      !numeratorCodes.every((code) => Number.isFinite(row[code]))
    ) continue;
    const scale = numeratorCodes.reduce((sum, code) => sum + row[code], 0);
    result.set(countryCode, {
      country_code: countryCode,
      scale_thousands: scale,
      share_percent: (100 * scale) / row.TOTAL,
      latest_period: 2025,
      source_id: row._source_id,
      observation_statuses: [],
    });
  }
  return result;
}

async function loadObservedResearchDevelopment(filePath, countrySet) {
  const lines = (await fs.readFile(filePath, "utf8")).trim().split(/\r?\n/);
  const headers = parseCsvLine(lines[0].replace(/^\uFEFF/, ""));
  const at = Object.fromEntries(headers.map((name, index) => [name, index]));
  const combinations = new Map();
  for (const line of lines.slice(1)) {
    const row = parseCsvLine(line);
    const countryCode = row[at.ref_area];
    if (!countrySet.has(countryCode) || row[at.sex] !== "SEX_T") continue;
    const classCode = row[at.classif1];
    if (!new Set(["EC2_ISIC4_TOTAL", "EC2_ISIC4_M72"]).has(classCode)) continue;
    const key = `${countryCode}|${row[at.source]}|${row[at.time]}`;
    const current = combinations.get(key) ?? {
      country_code: countryCode,
      source_id: row[at.source],
      year: Number(row[at.time]),
      values: {},
      statuses: {},
    };
    if (row[at.obs_value]?.trim()) current.values[classCode] = Number(row[at.obs_value]);
    current.statuses[classCode] = row[at.obs_status] || "";
    combinations.set(key, current);
  }
  const selected = new Map();
  for (const row of combinations.values()) {
    const total = row.values.EC2_ISIC4_TOTAL;
    const value = row.values.EC2_ISIC4_M72;
    const statuses = [row.statuses.EC2_ISIC4_TOTAL, row.statuses.EC2_ISIC4_M72].filter(Boolean);
    if (!Number.isFinite(total) || total <= 0 || !Number.isFinite(value) || statuses.includes("U")) continue;
    const previous = selected.get(row.country_code);
    if (
      !previous || row.year > previous.latest_period ||
      (row.year === previous.latest_period && row.source_id < previous.source_id)
    ) {
      selected.set(row.country_code, {
        country_code: row.country_code,
        scale_thousands: value,
        share_percent: (100 * value) / total,
        latest_period: row.year,
        source_id: row.source_id,
        observation_statuses: statuses,
      });
    }
  }
  return new Map([...selected].filter(([, row]) => row.latest_period >= FRESHNESS_MIN_YEAR));
}

function observedOccupationMap(phase6aRows, candidateId) {
  return new Map(
    phase6aRows
      .filter((row) => row.candidate_id === candidateId && row.outcome === "valid")
      .map((row) => [row.country_code, {
        country_code: row.country_code,
        scale_thousands: row.family_employment_thousands,
        share_percent: row.family_share_percent,
        latest_period: row.latest_year,
        source_id: row.source_id,
        observation_statuses: row.observation_statuses,
      }]),
  );
}

function benchmarkProfiles(catalog) {
  const presets = Object.fromEntries(catalog.preference_presets.map((row) => [row.id, row.weights]));
  return {
    general_balanced: presets.equal_weight_mvp,
    affordability_sensitive: presets.affordability_first,
    safety_governance_oriented: presets.safety_and_stability,
    ...PROFILE_WEIGHTS,
  };
}

function rankBenchmarks({ catalog, entities, outcomes, scores }) {
  const criteria = Object.fromEntries(catalog.criteria.map((row) => [row.id, row]));
  const countries = entities.filter((row) => row.entity_type === "COUNTRY")
    .sort((left, right) => left.entity_id.localeCompare(right.entity_id));
  const outcomeMap = new Map(outcomes.map((row) => [`${row.criterion_id}|${row.subject.entity_id}`, row]));
  const scoreMap = new Map(scores.filter((row) => row.subject.entity_type === "COUNTRY")
    .map((row) => [`${row.criterion_id}|${row.subject.entity_id}`, row]));
  const result = {};
  for (const [profileId, weights] of Object.entries(benchmarkProfiles(catalog))) {
    const fcc = Object.values(criteria).filter((criterion) =>
      criterion.ready && (weights[criterion.id] ?? 0) > 0 && criterion.coverage.mode === "GLOBAL_CORE")
      .map((criterion) => criterion.id).sort();
    let pcc = Object.values(criteria).filter((criterion) =>
      criterion.ready && criterion.coverage.mode === "CONDITIONAL_COMPLETE_CASE" &&
      (weights[criterion.id] ?? 0) >= criterion.coverage.activation_threshold)
      .map((criterion) => criterion.id).sort();
    let active = [...fcc, ...pcc];
    let eligible = countries.filter((country) => active.every((criterionId) =>
      outcomeMap.get(`${criterionId}|${country.entity_id}`)?.outcome === "valid"));
    if (pcc.length) {
      const minimum = Math.max(...pcc.map((id) => criteria[id].coverage.minimum_valid_country_count));
      if (eligible.length < minimum) {
        pcc = [];
        active = [...fcc];
        eligible = countries.filter((country) => active.every((criterionId) =>
          outcomeMap.get(`${criterionId}|${country.entity_id}`)?.outcome === "valid"));
      }
    }
    const totalWeight = active.reduce((sum, criterionId) => sum + weights[criterionId], 0);
    const ranked = eligible.map((country) => {
      const contributions = active.map((criterionId) =>
        round(scoreMap.get(`${criterionId}|${country.entity_id}`).score * weights[criterionId] / totalWeight));
      return { country, score: round(contributions.reduce((sum, value) => sum + value, 0)) };
    }).sort((left, right) => right.score - left.score || left.country.entity_id.localeCompare(right.country.entity_id));
    result[profileId] = {
      weights,
      active_fcc: fcc,
      active_pcc: pcc,
      eligible_count: eligible.length,
      countries: ranked.slice(0, 20).map((row, index) => ({
        code: row.country.country_codes[0],
        name: row.country.display_name,
        score: row.score,
        rank: index + 1,
      })),
    };
  }
  return result;
}

function classifyCandidate({ candidateId, country, routeMaps, thresholds, profiles, percentile = BASE_PERCENTILE }) {
  const definition = CANDIDATES[candidateId];
  const memberships = Object.entries(profiles)
    .filter(([, profile]) => profile.countries.some((row) => row.code === country.code))
    .map(([profileId]) => profileId);
  let observations = [];
  let assessable = false;
  let strong = false;
  let reasonCode;

  if (candidateId === "skilled_trades_construction_opportunity") {
    const trade = routeMaps.modelled_skilled_trades.get(country.code);
    const construction = routeMaps.modelled_construction_sector.get(country.code);
    observations = [
      trade && { route_id: "modelled_skilled_trades", ...trade },
      construction && { route_id: "modelled_construction_sector", ...construction },
    ].filter(Boolean);
    assessable = Boolean(trade && construction);
    if (assessable) {
      strong = routePasses(trade, thresholds.modelled_skilled_trades[percentile]) ||
        routePasses(construction, thresholds.modelled_construction_sector[percentile]);
      reasonCode = strong ? "AT_LEAST_ONE_TRANSPARENT_ROUTE_CROSSES_THRESHOLD" : "BOTH_TRANSPARENT_ROUTES_TESTED_NONE_CROSSES_THRESHOLD";
    } else {
      reasonCode = "MODELLED_OCCUPATION_OR_SECTOR_ROW_MISSING";
    }
  } else {
    const observation = routeMaps[definition.primary_route].get(country.code);
    if (observation) observations = [{ route_id: definition.primary_route, ...observation }];
    assessable = Boolean(observation);
    if (assessable) {
      strong = routePasses(observation, thresholds[definition.primary_route][percentile]);
      reasonCode = strong ? "TRANSPARENT_SCALE_SHARE_ROUTE_CROSSES_THRESHOLD" : "COMPARABLE_ROUTE_TESTED_DOES_NOT_CROSS_THRESHOLD";
    } else {
      reasonCode = candidateId === "research_academia_opportunity"
        ? "NO_FRESH_COMPARABLE_FIELD_RELEVANT_EMPLOYMENT_ROUTE"
        : "NO_FRESH_COMPARABLE_PRIMARY_ROUTE";
    }
  }

  const state = !assessable ? "INSUFFICIENT_EVIDENCE"
    : strong ? "VERIFIED_STRONG_SIGNAL"
      : "STRONG_SIGNAL_NOT_ESTABLISHED";
  const confidence = !assessable ? "LOW"
    : definition.primary_route.startsWith("modelled_") || candidateId === "skilled_trades_construction_opportunity"
      ? "MEDIUM" : "HIGH";
  return {
    schema_version: "konsider-career-country-opportunity-evidence-1.0",
    report_date: REPORT_DATE,
    candidate_id: candidateId,
    candidate_display_name: definition.display_name,
    country_code: country.code,
    country_name: country.display_name,
    region: country.region,
    income_group: country.income_group,
    state,
    reason_code: reasonCode,
    reason: state === "VERIFIED_STRONG_SIGNAL"
      ? "At least one frozen, reproducible route crosses the strong ecosystem threshold."
      : state === "STRONG_SIGNAL_NOT_ESTABLISHED"
        ? "Comparable evidence had a reasonable opportunity to detect a strong signal, but no route crossed the threshold; this does not mean there are no jobs."
        : "The evidence is missing, stale, incomplete, incomparable, or too weak for either a positive or negative conclusion.",
    latest_period: observations.length ? Math.max(...observations.map((row) => row.latest_period)) : null,
    evidence_paths: observations.map((row) => ({
      route_id: row.route_id,
      source_id: row.source_id,
      scale_thousands: round(row.scale_thousands, 6),
      share_percent: round(row.share_percent, 6),
      observation_statuses: row.observation_statuses,
    })),
    threshold_version: `phase6b-p${Math.round(percentile * 100)}-scale-share-routes-v1`,
    thresholds: candidateId === "skilled_trades_construction_opportunity"
      ? {
        modelled_skilled_trades: thresholdDescription(thresholds.modelled_skilled_trades[percentile]),
        modelled_construction_sector: thresholdDescription(thresholds.modelled_construction_sector[percentile]),
      }
      : thresholdDescription(thresholds[definition.primary_route][percentile]),
    completeness: {
      primary_route_assessable: assessable,
      route_count_present: observations.length,
      required_route_policy: candidateId === "skilled_trades_construction_opportunity" ? "BOTH_PRESENT_FOR_NEGATIVE; EITHER_MAY_ESTABLISH_POSITIVE" : "PRIMARY_ROUTE_PRESENT",
    },
    confidence,
    benchmark_shortlist_memberships: memberships,
  };
}

function buildSourceMatrix(rawHashes) {
  return {
    schema_version: "konsider-career-source-matrix-1.0",
    report_date: REPORT_DATE,
    sources: [
      {
        source_id: "ilo_observed_occupation_oc2",
        publisher: "International Labour Organization",
        table: "EMP_TEMP_SEX_OC2_NB_A",
        construct_role: "Exact two-digit occupation employment for technology/software and science/engineering.",
        coverage_result: "61 fresh technology rows; 66 fresh science/engineering rows in the 91-country universe.",
        comparability: "ISCO-08 two-digit, total sex, latest acceptable 2021+ national observation.",
        licence: "ILO content is available under CC BY 4.0 unless otherwise indicated.",
        exact_url: "https://rplumber.ilo.org/data/indicator/?id=EMP_TEMP_SEX_OC2_NB_A&format=csv",
        replay: { status: "PASS", sha256: rawHashes.ilo_observed_occupation },
        decision: "USABLE_EXACT_ROUTE_WITH_COVERAGE_GAP",
      },
      {
        source_id: "ilo_modelled_occupation_2025",
        publisher: "International Labour Organization",
        table: "EMP_2EMP_SEX_OCU_NB_A; Nov. 2025 edition",
        construct_role: "ISCO-08 major-group employment; exact for skilled trades group 7 and supporting-only for broad professionals/technicians.",
        coverage_result: "88 of 91 stable countries; Antigua and Barbuda, Grenada and Ukraine absent.",
        comparability: "Balanced internationally comparable panel combining reported and imputed country estimates; country estimates with limited information carry higher uncertainty.",
        licence: "ILO content is available under CC BY 4.0 unless otherwise indicated.",
        exact_url: "https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_OCU_NB_A&format=csv",
        methodology_url: "https://ilostat.ilo.org/methods/concepts-and-definitions/ilo-modelled-estimates/",
        replay: { status: "PASS", sha256: rawHashes.ilo_modelled_occupation },
        decision: "USABLE_WITH_MODELLED_CONFIDENCE_CAVEAT",
      },
      {
        source_id: "ilo_modelled_economic_activity_2025",
        publisher: "International Labour Organization",
        table: "EMP_2EMP_SEX_ECO_NB_A; Nov. 2025 edition",
        construct_role: "ISIC Rev.4 section F construction, K finance/insurance and Q health/social-work employment.",
        coverage_result: "88 of 91 stable countries; the same three absences as the occupation model.",
        comparability: "Balanced internationally comparable panel; sections are broad and must be named exactly.",
        licence: "ILO content is available under CC BY 4.0 unless otherwise indicated.",
        exact_url: "https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_ECO_NB_A&format=csv",
        methodology_url: "https://ilostat.ilo.org/methods/concepts-and-definitions/ilo-modelled-estimates/",
        replay: { status: "PASS", sha256: rawHashes.ilo_modelled_economy },
        decision: "USABLE_WITH_SCOPE_AND_MODELLED_CONFIDENCE_CAVEATS",
      },
      {
        source_id: "ilo_observed_economic_activity_isic2",
        publisher: "International Labour Organization",
        table: "EMP_TEMP_SEX_EC2_NB_A",
        construct_role: "Detailed supporting route for J62/J63, M71/M72, Q86, K/M/N families and construction divisions.",
        coverage_result: "No tested detailed family reaches the 60-country hard floor; fresh M72 research employment reaches 54.",
        comparability: "Observed ISIC Rev.4 two-digit rows, but source/year/status gaps are material.",
        licence: "ILO content is available under CC BY 4.0 unless otherwise indicated.",
        exact_url: "https://rplumber.ilo.org/data/indicator/?id=EMP_TEMP_SEX_EC2_NB_A&format=csv",
        replay: { status: "PASS", sha256: rawHashes.ilo_observed_economy },
        decision: "SUPPORTING_ONLY_SOURCE_GAP",
      },
      {
        source_id: "eurostat_job_vacancy_statistics",
        publisher: "Eurostat",
        construct_role: "Current unmet labour demand by economic activity; occupation breakdown is voluntary and experimental.",
        coverage_result: "European regional scope; cannot satisfy geographic breadth for the 91-country universe.",
        comparability: "Generally comparable but country coverage and establishment scope differ.",
        exact_url: "https://ec.europa.eu/eurostat/web/labour-market/information-data/job-vacancies",
        decision: "SUPPLEMENTAL_ONLY_GEOGRAPHIC_GAP",
      },
      {
        source_id: "cedefop_skills_ovate",
        publisher: "Cedefop and Eurostat Web Intelligence Hub",
        construct_role: "Near-real-time online job-advertisement demand by occupation and skills.",
        coverage_result: "EU, EFTA and United Kingdom only.",
        comparability: "Online advertisements are mined and classified; platform representation differs by country.",
        exact_url: "https://www.cedefop.europa.eu/en/projects/skills-online-job-advertisements",
        decision: "SUPPLEMENTAL_ONLY_GEOGRAPHIC_AND_REPRESENTATION_GAP",
      },
      {
        source_id: "national_labour_force_and_shortage_sources",
        publisher: "National statistical and immigration authorities",
        construct_role: "Potential gap-filling observations for Canada, Japan, Korea and New Zealand.",
        coverage_result: "Prominent-country positives may be recoverable, but taxonomies, reference periods and machine interfaces are not yet normalized.",
        comparability: "NOC, Japan Standard Occupational Classification, KSCO and ANZSCO do not form an automatic ISCO-08 two-digit join.",
        decision: "NOT_USED_UNTIL_CROSSWALKS_AND_REPLAY_ARE_FROZEN",
      },
      {
        source_id: "major_employer_ecosystem_route",
        publisher: "No qualifying cross-country source identified",
        construct_role: "Large relevant employers with material in-country employment.",
        coverage_result: "No authoritative, harmonized, reproducible 91-country source with employment counts and acceptable reuse was found.",
        comparability: "Office presence, search result counts and crowdsourced employer lists do not establish material employment.",
        decision: "REJECTED_FOR_CURRENT_STUDY",
      },
      {
        source_id: "world_bank_country_metadata",
        publisher: "World Bank",
        construct_role: "Income-group breadth diagnostic only; never used to classify opportunity.",
        exact_url: "https://api.worldbank.org/v2/country?format=json&per_page=400",
        replay: { status: "PASS", sha256: rawHashes.world_bank_metadata },
        decision: "ANALYSIS_ONLY",
      },
    ],
  };
}

function markdownReport({ candidateMatrix, shortlistCoverage, sourceMatrix, approvedPortfolio, rawHashes }) {
  const candidateRows = candidateMatrix.candidates.map((row) =>
    `| ${row.display_name} | ${row.outcome_counts.VERIFIED_STRONG_SIGNAL} | ${row.outcome_counts.STRONG_SIGNAL_NOT_ESTABLISHED} | ${row.outcome_counts.INSUFFICIENT_EVIDENCE} | ${row.decision} |`).join("\n");
  const shortlistRows = Object.values(shortlistCoverage.candidates).flatMap((candidate) =>
    Object.entries(candidate.profiles).map(([profileId, row]) =>
      `| ${candidate.display_name} | ${profileId} | ${row.assessable_count}/20 | ${row.verified_strong_signal_count} | ${row.preferred_target_passes ? "pass" : "fail"} |`),
  ).join("\n");
  return `# Phase 6B career-opportunity source study

Date: ${REPORT_DATE}

Status: research complete; implementation deliberately not started

Authoritative prompt: \`project-history/phases/phase-6/Konsider Phase 6B Career Opportunity Criteria.pdf\`

## Executive decision

The study approves three transparent, non-ranking employment-ecosystem criteria for implementation design, holds three candidates on source coverage, and approves no runtime change. “Approved” here means the construct, evidence route, tri-state semantics and frozen study threshold are sufficiently defined for a later owner decision; it does not authorize schema, worker, ranking, API, release, preset or UI work.

Approved portfolio:

- **Health and social-work employment ecosystem** — \`APPROVE_WITH_NAMING_OR_SCOPE_CHANGE\`; ISIC Rev.4 section Q cannot be labelled healthcare alone.
- **Finance and insurance employment ecosystem** — \`APPROVE_WITH_NAMING_OR_SCOPE_CHANGE\`; ISIC section K cannot represent all business and administration careers.
- **Skilled-trades or construction employment ecosystem** — \`APPROVE_FOR_IMPLEMENTATION_DESIGN\`; either the major-group-7 occupation route or section-F construction route may establish a positive signal.

Held:

- Technology/software and science/engineering have exact observed occupation constructs and clear the 60-country hard floor, but only 15/20 countries are assessable in four benchmark lists. Canada, Japan, Korea, Malta and New Zealand are material gaps.
- Research/academia has only 54 fresh, field-relevant M72 employment rows and the measure is business R&D rather than academia. Research output or institution counts may support a positive case but cannot safely establish a negative opportunity state.

## Semantics and frozen decision rule

This phase defines a filter, never a ranking input:

- \`VERIFIED_STRONG_SIGNAL\`: at least one reproducible route crosses a frozen strong-ecosystem threshold.
- \`STRONG_SIGNAL_NOT_ESTABLISHED\`: comparable evidence had a reasonable opportunity to detect the signal, but no route crosses it. This does **not** mean there are no jobs.
- \`INSUFFICIENT_EVIDENCE\`: missing, stale, incomplete, incomparable or construct-mismatched evidence. It is never a negative conclusion.

For each single employment route the base rule is: (scale ≥ P60 and share ≥ P60), or (scale ≥ P80 and share ≥ P40), or (share ≥ P80 and scale ≥ P40). Percentiles are converted to frozen raw thresholds in the artifacts. This avoids an opaque score, admits either exceptional scale or specialization only with a minimum on the other dimension, and keeps the positive/negative evidence asymmetry explicit. P50 and P70 variants are sensitivity tests, not alternative policy defaults.

Modelled ILO estimates are treated as medium-confidence comparable evidence. ILO describes the series as a balanced internationally comparable panel combining nationally reported and imputed observations and cautions that estimates for countries with limited information have higher uncertainty. Antigua and Barbuda, Grenada and Ukraine are absent from the November 2025 modelled captures and therefore remain \`INSUFFICIENT_EVIDENCE\`.

## Candidate results

| Candidate | Strong | Not established | Insufficient | Decision |
|---|---:|---:|---:|---|
${candidateRows}

The smaller assessed state class is at least eight for every approved candidate at the base threshold. No approved candidate is a near-universal toggle.

## Benchmark shortlist coverage

The five lists are regenerated solely from current release ${RELEASE_ID} criteria and the existing complete-case ranking rules. Opportunity evidence is not used to create or reorder a list.

| Candidate | Profile | Assessable | Strong | Preferred ≥16/20 |
|---|---|---:|---:|---|
${shortlistRows}

All three approved candidates are assessable for 20/20 countries in every benchmark list. The exact technology and science/engineering routes reach 17/20 only for the family/education list and 15/20 for each other list.

## Geographic, economic and source-dependency findings

The 88-country modelled routes span every stable-universe region and every World Bank income group represented in the universe. The three absent countries are distributed across Latin America/Caribbean and Europe/Central Asia, so they are explicit evidence gaps rather than inferred negatives. Detailed region and income-state counts are retained in \`career-candidate-matrix.json\`.

The approved portfolio has a material single-publisher dependency: removing the ILO modelled-estimate family turns every approved assessment into insufficient evidence. That is acceptable for this implementation-design approval only because the source is authoritative, exact captures and hashes are frozen, reuse is compatible, and the state is non-ranking. An implementation owner should decide whether medium-confidence modelled country estimates are acceptable before any product work.

## Source findings

${sourceMatrix.sources.map((source) => `- **${source.source_id}** — ${source.decision}. ${source.coverage_result ?? source.construct_role}`).join("\n")}

Current-demand evidence remains supplemental. Eurostat job-vacancy statistics are authoritative but geographically regional and occupational breakdown is voluntary/experimental. Cedefop Skills OVATE is valuable near-real-time European evidence but online-ad representation and geographic scope prevent a 91-country negative state. No qualifying harmonized major-employer dataset was found; office locations, search counts and crowdsourced lists are excluded.

## Legal, replay and quality gates

- ILO source use: pass under the publisher's CC BY 4.0 default, with attribution and source-specific notices retained.
- Exact captures: pass; SHA-256 checks are frozen in \`replay-manifest.json\` and rechecked by the replay script.
- World Bank metadata: analysis-only income grouping; it never changes a country state.
- Construct validity: pass only for the final names shown above. Broader labels are not approved.
- Shortlist gate: pass for the three approved candidates; material failure for technology/software and science/engineering.
- Discrimination: pass at P60; see P50/P70 state flips in \`career-threshold-sensitivity.json\`.
- Runtime boundary: pass; no production catalog, schema, worker, ranking, API, release, preset or UI artifact changed.

Raw capture checksums used in this run:

${Object.entries(rawHashes).map(([id, hash]) => `- \`${id}\`: \`${hash}\``).join("\n")}

## Files and verification

- \`data/reports/phase6b-${REPORT_DATE}/career-candidate-matrix.json\`
- \`data/reports/phase6b-${REPORT_DATE}/career-country-opportunity-evidence.jsonl\`
- \`data/reports/phase6b-${REPORT_DATE}/career-source-matrix.json\`
- \`data/reports/phase6b-${REPORT_DATE}/career-shortlist-coverage.json\`
- \`data/reports/phase6b-${REPORT_DATE}/career-threshold-sensitivity.json\`
- \`data/reports/phase6b-${REPORT_DATE}/approved-career-opportunity-portfolio.json\`
- \`data/reports/phase6b-${REPORT_DATE}/replay-manifest.json\`
- \`project-history/phases/phase-6/research/run_phase6b_opportunity_probe.mjs\`

The replay verifies input hashes, reconstructs 546 country-candidate rows (91 × 6), requires exactly one state per row, checks the hard coverage and shortlist counts, and writes deterministic artifacts. The introducing Git commit is intentionally reported in the task handoff rather than embedded here because a commit cannot contain its own final hash.

## Owner decisions required before implementation

1. Accept or reject medium-confidence ILO modelled country estimates for a non-ranking filter.
2. Accept the exact public names and the OR semantics for skilled trades/construction.
3. Choose whether held technology/science criteria should wait for frozen national crosswalks or proceed later with the documented prominent-country gaps.
4. Decide whether an independent second-source requirement is mandatory despite the current single-publisher dependency.

Phase 6B stops here. No implementation phase is started.
`;
}

export async function runPhase6B({ repoRoot }) {
  const rawDirectory = path.join(repoRoot, "data", "raw", "phase6b");
  const outputDirectory = path.join(repoRoot, "data", "reports", `phase6b-${REPORT_DATE}`);
  const reportPath = path.join(repoRoot, "docs", "research", "phase6b-career-opportunity-study.md");
  const stableUniverse = JSON.parse(await fs.readFile(path.join(repoRoot, "data", "country-universes", "stable-supported-v1.json"), "utf8"));
  const countrySet = new Set(stableUniverse.countries.map((country) => country.code));
  const releaseDirectory = path.join(repoRoot, "data", "releases", RELEASE_ID);
  const catalog = JSON.parse(await fs.readFile(path.join(releaseDirectory, "consumer-catalog.json"), "utf8"));
  const entities = await readJsonLines(path.join(releaseDirectory, "geographic-entities.jsonl"));
  const outcomes = await readJsonLines(path.join(releaseDirectory, "criterion-outcomes.jsonl"));
  const scores = await readJsonLines(path.join(releaseDirectory, "scores.jsonl"));
  const phase6aRows = await readJsonLines(path.join(repoRoot, "data", "reports", "phase6a-2026-07-30", "country-coverage.jsonl"));

  const rawPaths = {
    ilo_observed_occupation: path.join(repoRoot, "data", "raw", "phase6a", "ilostat-emp-oc2.csv"),
    ilo_modelled_occupation: path.join(rawDirectory, "ilo-modelled-employment-occupation-2025.csv"),
    ilo_modelled_economy: path.join(rawDirectory, "ilo-modelled-employment-economic-activity-2025.csv"),
    ilo_observed_economy: path.join(rawDirectory, "ilo-employment-economic-activity-isic2.csv"),
    world_bank_metadata: path.join(rawDirectory, "world-bank-country-metadata.json"),
  };
  const rawBuffers = Object.fromEntries(await Promise.all(Object.entries(rawPaths).map(async ([id, filePath]) => [id, await fs.readFile(filePath)])));
  const rawHashes = Object.fromEntries(Object.entries(rawBuffers).map(([id, buffer]) => [id, sha256(buffer)]));
  for (const [sourceId, expectedHash] of Object.entries(EXPECTED_RAW_HASHES)) {
    if (rawHashes[sourceId] !== expectedHash) {
      throw new Error(`Raw source hash mismatch for ${sourceId}: expected ${expectedHash}, got ${rawHashes[sourceId]}.`);
    }
  }

  const modelledOccupation = await loadModelled(rawPaths.ilo_modelled_occupation, "OCU_ISCO08_", new Set(["TOTAL", "7"]), countrySet);
  const modelledEconomy = await loadModelled(rawPaths.ilo_modelled_economy, "ECO_ISIC4_", new Set(["TOTAL", "F", "K", "Q"]), countrySet);
  const routeMaps = {
    observed_technology_occupation: observedOccupationMap(phase6aRows, "technology_employment_market_depth"),
    observed_science_engineering_occupation: observedOccupationMap(phase6aRows, "science_engineering_employment_market_depth"),
    modelled_health_social_work_sector: modelledObservations(modelledEconomy, ["Q"]),
    modelled_finance_insurance_sector: modelledObservations(modelledEconomy, ["K"]),
    observed_research_development_sector: await loadObservedResearchDevelopment(rawPaths.ilo_observed_economy, countrySet),
    modelled_skilled_trades: modelledObservations(modelledOccupation, ["7"]),
    modelled_construction_sector: modelledObservations(modelledEconomy, ["F"]),
  };
  const thresholds = Object.fromEntries(Object.entries(routeMaps).map(([routeId, routeMap]) => {
    const observations = [...routeMap.values()];
    return [routeId, Object.fromEntries(SENSITIVITY_PERCENTILES.map((percentile) => [percentile, thresholdsFor(observations, percentile)]))];
  }));

  const worldBank = JSON.parse(rawBuffers.world_bank_metadata.toString("utf8"));
  const incomeByCode = new Map(worldBank[1].map((row) => [row.id, row.incomeLevel?.value ?? "Unknown"]));
  const countries = stableUniverse.countries.map((country) => ({ ...country, income_group: incomeByCode.get(country.code) ?? "Unknown" }));
  const profiles = rankBenchmarks({ catalog, entities, outcomes, scores });
  for (const [profileId, expectedCodes] of Object.entries(EXPECTED_BENCHMARK_TOP20)) {
    const actualCodes = profiles[profileId].countries.map((row) => row.code);
    if (JSON.stringify(actualCodes) !== JSON.stringify(expectedCodes)) {
      throw new Error(`Benchmark top-20 mismatch for ${profileId}.`);
    }
  }
  const evidenceRows = Object.keys(CANDIDATES).flatMap((candidateId) => countries.map((country) =>
    classifyCandidate({ candidateId, country, routeMaps, thresholds, profiles })));
  if (evidenceRows.length !== 546) throw new Error(`Expected 546 evidence rows, got ${evidenceRows.length}.`);
  if (new Set(evidenceRows.map((row) => `${row.candidate_id}|${row.country_code}`)).size !== 546) throw new Error("Duplicate country-candidate evidence row.");

  const candidateMatrix = {
    schema_version: "konsider-career-candidate-matrix-1.0",
    report_date: REPORT_DATE,
    stable_universe_id: stableUniverse.universe_id,
    stable_country_count: countries.length,
    hard_minimum_assessable: 60,
    preferred_shortlist_assessable: 16,
    candidates: Object.entries(CANDIDATES).map(([candidateId, definition]) => {
      const rows = evidenceRows.filter((row) => row.candidate_id === candidateId);
      const outcomeCounts = countBy(rows, "state");
      const byRegion = Object.fromEntries([...new Set(rows.map((row) => row.region))].sort().map((region) => {
        const group = rows.filter((row) => row.region === region);
        return [region, countBy(group, "state")];
      }));
      const byIncome = Object.fromEntries([...new Set(rows.map((row) => row.income_group))].sort().map((incomeGroup) => {
        const group = rows.filter((row) => row.income_group === incomeGroup);
        return [incomeGroup, countBy(group, "state")];
      }));
      return {
        candidate_id: candidateId,
        display_name: definition.display_name,
        original_scope: definition.original_scope,
        exact_construct: definition.construct,
        does_not_mean: "Live vacancies, job quality, licensing or credential recognition, immigration eligibility, applicant success probability, or absence of jobs.",
        primary_route: definition.primary_route,
        outcome_counts: {
          VERIFIED_STRONG_SIGNAL: outcomeCounts.VERIFIED_STRONG_SIGNAL ?? 0,
          STRONG_SIGNAL_NOT_ESTABLISHED: outcomeCounts.STRONG_SIGNAL_NOT_ESTABLISHED ?? 0,
          INSUFFICIENT_EVIDENCE: outcomeCounts.INSUFFICIENT_EVIDENCE ?? 0,
        },
        assessable_count: rows.filter((row) => row.state !== "INSUFFICIENT_EVIDENCE").length,
        hard_minimum_passes: rows.filter((row) => row.state !== "INSUFFICIENT_EVIDENCE").length >= 60,
        state_counts_by_region: byRegion,
        state_counts_by_income_group: byIncome,
        decision: definition.decision,
        decision_reason: definition.decision_reason,
        source_dependency: "ILO_SINGLE_PUBLISHER_MATERIAL_DEPENDENCY",
        implementation_status: "NOT_STARTED",
      };
    }),
  };

  const shortlistCoverage = {
    schema_version: "konsider-career-shortlist-coverage-1.0",
    report_date: REPORT_DATE,
    release_id: RELEASE_ID,
    generation_note: "Lists use only current production criteria and current complete-case ranking semantics; Phase 6B opportunity evidence is joined afterward and never affects rank or ordering.",
    profiles,
    candidates: Object.fromEntries(Object.entries(CANDIDATES).map(([candidateId, definition]) => [candidateId, {
      display_name: definition.display_name,
      profiles: Object.fromEntries(Object.entries(profiles).map(([profileId, profile]) => {
        const codes = profile.countries.map((row) => row.code);
        const rows = evidenceRows.filter((row) => row.candidate_id === candidateId && codes.includes(row.country_code));
        const missing = rows.filter((row) => row.state === "INSUFFICIENT_EVIDENCE").map((row) => row.country_code).sort();
        const assessable = 20 - missing.length;
        return [profileId, {
          assessable_count: assessable,
          verified_strong_signal_count: rows.filter((row) => row.state === "VERIFIED_STRONG_SIGNAL").length,
          strong_signal_not_established_count: rows.filter((row) => row.state === "STRONG_SIGNAL_NOT_ESTABLISHED").length,
          insufficient_evidence_count: missing.length,
          insufficient_evidence_countries: missing,
          preferred_target_passes: assessable >= 16,
        }];
      })),
    }])),
  };

  const thresholdSensitivity = {
    schema_version: "konsider-career-threshold-sensitivity-1.0",
    report_date: REPORT_DATE,
    base_percentile: BASE_PERCENTILE,
    scenarios: Object.fromEntries(Object.keys(CANDIDATES).map((candidateId) => {
      const baseStates = new Map(evidenceRows.filter((row) => row.candidate_id === candidateId).map((row) => [row.country_code, row.state]));
      return [candidateId, Object.fromEntries(SENSITIVITY_PERCENTILES.map((percentile) => {
        const rows = countries.map((country) => classifyCandidate({ candidateId, country, routeMaps, thresholds, profiles, percentile }));
        const counts = countBy(rows, "state");
        return [`p${Math.round(percentile * 100)}`, {
          percentile,
          outcome_counts: {
            VERIFIED_STRONG_SIGNAL: counts.VERIFIED_STRONG_SIGNAL ?? 0,
            STRONG_SIGNAL_NOT_ESTABLISHED: counts.STRONG_SIGNAL_NOT_ESTABLISHED ?? 0,
            INSUFFICIENT_EVIDENCE: counts.INSUFFICIENT_EVIDENCE ?? 0,
          },
          state_changes_from_p60: rows.filter((row) => row.state !== baseStates.get(row.country_code)).map((row) => ({
            country_code: row.country_code,
            from: baseStates.get(row.country_code),
            to: row.state,
          })),
        }];
      }))];
    })),
    route_thresholds: Object.fromEntries(
      Object.entries(thresholds).map(([routeId, scenarios]) => [
        routeId,
        Object.fromEntries(
          Object.entries(scenarios).map(([percentile, values]) => [
            `p${Math.round(Number(percentile) * 100)}`,
            thresholdDescription(values),
          ]),
        ),
      ]),
    ),
  };

  const approvedPortfolio = {
    schema_version: "konsider-approved-career-opportunity-portfolio-1.0",
    report_date: REPORT_DATE,
    status: "APPROVED_FOR_IMPLEMENTATION_DESIGN_ONLY",
    approved_count: 3,
    held_count: 3,
    runtime_change_authorized: false,
    approved: candidateMatrix.candidates.filter((row) => row.decision.startsWith("APPROVE")),
    held: candidateMatrix.candidates.filter((row) => row.decision.startsWith("HOLD")),
    rejected: [],
    common_semantics: {
      ranking_effect: "NONE",
      ordering_effect: "NONE",
      states: ["VERIFIED_STRONG_SIGNAL", "STRONG_SIGNAL_NOT_ESTABLISHED", "INSUFFICIENT_EVIDENCE"],
      insufficient_evidence_policy: "NEVER_NEGATIVE",
    },
    owner_decisions_required: [
      "Accept medium-confidence ILO modelled country estimates for a non-ranking filter.",
      "Accept exact scope names and the skilled-trades/construction OR route.",
      "Choose a source-gap strategy for technology/software, science/engineering and research/academia.",
      "Decide whether a second independent publisher is mandatory before implementation.",
    ],
  };

  const sourceMatrix = buildSourceMatrix(rawHashes);
  await fs.mkdir(outputDirectory, { recursive: true });
  const outputFiles = {
    "career-candidate-matrix.json": json(candidateMatrix),
    "career-country-opportunity-evidence.jsonl": `${evidenceRows.map((row) => JSON.stringify(row)).join("\n")}\n`,
    "career-source-matrix.json": json(sourceMatrix),
    "career-shortlist-coverage.json": json(shortlistCoverage),
    "career-threshold-sensitivity.json": json(thresholdSensitivity),
    "approved-career-opportunity-portfolio.json": json(approvedPortfolio),
  };
  for (const [fileName, content] of Object.entries(outputFiles)) await fs.writeFile(path.join(outputDirectory, fileName), content, "utf8");
  const manifest = {
    schema_version: "konsider-phase6b-replay-manifest-1.0",
    report_date: REPORT_DATE,
    command: "node project-history/phases/phase-6/research/run_phase6b_opportunity_probe.mjs",
    input_sha256: {
      ...rawHashes,
      stable_universe: sha256(await fs.readFile(path.join(repoRoot, "data", "country-universes", "stable-supported-v1.json"))),
      phase6a_country_coverage: sha256(await fs.readFile(path.join(repoRoot, "data", "reports", "phase6a-2026-07-30", "country-coverage.jsonl"))),
      release_catalog: sha256(await fs.readFile(path.join(releaseDirectory, "consumer-catalog.json"))),
      release_entities: sha256(await fs.readFile(path.join(releaseDirectory, "geographic-entities.jsonl"))),
      release_outcomes: sha256(await fs.readFile(path.join(releaseDirectory, "criterion-outcomes.jsonl"))),
      release_scores: sha256(await fs.readFile(path.join(releaseDirectory, "scores.jsonl"))),
    },
    output_sha256: Object.fromEntries(Object.entries(outputFiles).map(([fileName, content]) => [fileName, sha256(Buffer.from(content))])),
    assertions: {
      candidate_count: Object.keys(CANDIDATES).length,
      country_count: countries.length,
      evidence_row_count: evidenceRows.length,
      unique_country_candidate_count: new Set(evidenceRows.map((row) => `${row.candidate_id}|${row.country_code}`)).size,
      approved_count: approvedPortfolio.approved_count,
      all_approved_meet_hard_minimum: approvedPortfolio.approved.every((row) => row.hard_minimum_passes),
      all_approved_shortlists_meet_preferred_target: approvedPortfolio.approved.every((row) =>
        Object.values(shortlistCoverage.candidates[row.candidate_id].profiles).every((profile) => profile.preferred_target_passes)),
      all_approved_have_at_least_eight_in_smaller_assessed_state: approvedPortfolio.approved.every((row) =>
        Math.min(row.outcome_counts.VERIFIED_STRONG_SIGNAL, row.outcome_counts.STRONG_SIGNAL_NOT_ESTABLISHED) >= 8),
      modelled_routes_assessable_count: routeMaps.modelled_health_social_work_sector.size,
      modelled_routes_expected_88: [
        routeMaps.modelled_health_social_work_sector,
        routeMaps.modelled_finance_insurance_sector,
        routeMaps.modelled_skilled_trades,
        routeMaps.modelled_construction_sector,
      ].every((routeMap) => routeMap.size === 88),
      runtime_change_authorized: false,
    },
  };
  const requiredTrueAssertions = [
    manifest.assertions.evidence_row_count === 546,
    manifest.assertions.unique_country_candidate_count === 546,
    manifest.assertions.approved_count === 3,
    manifest.assertions.all_approved_meet_hard_minimum,
    manifest.assertions.all_approved_shortlists_meet_preferred_target,
    manifest.assertions.all_approved_have_at_least_eight_in_smaller_assessed_state,
    manifest.assertions.modelled_routes_expected_88,
    manifest.assertions.runtime_change_authorized === false,
  ];
  if (!requiredTrueAssertions.every(Boolean)) throw new Error("One or more Phase 6B replay assertions failed.");
  await fs.writeFile(path.join(outputDirectory, "replay-manifest.json"), json(manifest), "utf8");
  await fs.writeFile(reportPath, markdownReport({ candidateMatrix, shortlistCoverage, sourceMatrix, approvedPortfolio, rawHashes }), "utf8");
  return { outputDirectory, reportPath, manifest, candidateMatrix, shortlistCoverage };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/(.:)/, "$1"))) {
  const result = await runPhase6B({ repoRoot: process.cwd() });
  console.log(JSON.stringify({
    output_directory: path.relative(process.cwd(), result.outputDirectory).replaceAll("\\", "/"),
    report: path.relative(process.cwd(), result.reportPath).replaceAll("\\", "/"),
    assertions: result.manifest.assertions,
  }, null, 2));
}
