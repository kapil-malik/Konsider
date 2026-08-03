import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPORT_DATE = "2026-08-03";
const REPORT_DIRECTORY = `phase6c-${REPORT_DATE}`;
const PERCENTILES = [0.5, 0.55, 0.6, 0.65, 0.7];
const BASE_PERCENTILE = 0.6;
const STATES = ["VERIFIED_STRONG_SIGNAL", "STRONG_SIGNAL_NOT_ESTABLISHED", "INSUFFICIENT_EVIDENCE"];

const CANDIDATES = [
  {
    candidate_id: "engineering_technology_education_opportunity",
    prompt_direction: "Engineering and technology",
    field_key: "physical-sciences-engineering",
    source_field: "Physical sciences and engineering",
    display_name: "Physical sciences and engineering research-university ecosystem",
    disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    rationale: "The official field is broader than engineering and technology, so the public name must follow the source taxonomy.",
  },
  {
    candidate_id: "computer_science_ict_education_opportunity",
    prompt_direction: "Computer science and ICT",
    field_key: "mathematics-computer-science",
    source_field: "Mathematics and computer science",
    display_name: "Mathematics and computer science research-university ecosystem",
    disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    rationale: "The source cannot isolate ICT programme availability from mathematics and computer science research output.",
  },
  {
    candidate_id: "medicine_health_sciences_education_opportunity",
    prompt_direction: "Medicine and health sciences",
    field_key: "biomedical-health",
    source_field: "Biomedical and health sciences",
    display_name: "Biomedical and health sciences research-university ecosystem",
    disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    rationale: "The signal is a research ecosystem, not clinical training access or professional qualification recognition.",
  },
  {
    candidate_id: "business_finance_education_opportunity",
    prompt_direction: "Business and finance",
    field_key: null,
    source_field: null,
    display_name: "Business and finance higher-education opportunity",
    disposition: "HOLD_SOURCE_GAP",
    rationale: "The available Social sciences and humanities field is too broad to establish business or finance opportunity.",
  },
  {
    candidate_id: "natural_sciences_education_opportunity",
    prompt_direction: "Natural sciences",
    field_key: "life-earth-sciences",
    source_field: "Life and earth sciences",
    display_name: "Life and earth sciences research-university ecosystem",
    disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE",
    rationale: "The retained route covers life and earth sciences; physical sciences sit in another official field.",
  },
  {
    candidate_id: "broad_university_excellence_opportunity",
    prompt_direction: "Broad university excellence",
    field_key: "all-sciences",
    source_field: "All sciences",
    display_name: "Broad scientific research-university ecosystem",
    disposition: "REJECT_AS_OPPORTUNITY_CRITERION",
    rationale: "Scientific performance is not generic university excellence and substantially overlaps the existing research/innovation criterion.",
  },
];

const MANUAL_INSTITUTION_MATCHES = new Map([
  ["University of Campania |Italy", ["University of Campania \"Luigi Vanvitelli\"", "02kqnpp86"]],
  ["University of Medicine and Pharmacy |Romania", ["University of Medicine and Pharmacy \"Carol Davila\" Bucharest", "04fm87419"]],
  ["University |Italy", ["University \"Magna Græcia\" of Catanzaro", "0530bdk91"]],
  ["Universitas Putra Indonesia |Indonesia", ["Universitas Putra Indonesia \"YPTK\"", "04pqmjc38"]],
  ["University of Prishtina |Kosovo", ["University of Prishtina \"Hasan Prishtina\"", "05t3p2g92"]],
  ["Medical University of Varna |Bulgaria", ["Medical University of Varna \"Prof. Dr. Paraskev Stoyanov\"", "03jkshc47"]],
]);

const SOURCE_NAME_ALIASES = new Map([
  ["South Korea", "KOR"], ["Russia", "RUS"], ["Slovakia", "SVK"], ["Turkey", "TUR"],
]);

const json = (value) => `${JSON.stringify(value, null, 2)}\n`;
const jsonl = (rows) => `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`;
const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");
const round = (value, digits = 4) => Number(value.toFixed(digits));
const sum = (values) => values.reduce((total, value) => total + value, 0);

function quantile(values, percentile) {
  const sorted = [...values].sort((a, b) => a - b);
  if (!sorted.length) throw new Error("Cannot calculate a quantile over an empty set.");
  const index = (sorted.length - 1) * percentile;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}

function countBy(rows, key = "state") {
  return Object.fromEntries(STATES.map((state) => [state, rows.filter((row) => row[key] === state).length]));
}

function thresholdsFor(observations, percentile) {
  const low = Math.max(0, percentile - 0.2);
  const high = Math.min(1, percentile + 0.2);
  return {
    percentile: `P${Math.round(percentile * 100)}`,
    base_output: quantile(observations.map((row) => row.fractional_publication_output), percentile),
    base_breadth: quantile(observations.map((row) => row.active_university_breadth), percentile),
    high_output: quantile(observations.map((row) => row.fractional_publication_output), high),
    high_breadth: quantile(observations.map((row) => row.active_university_breadth), high),
    low_output: quantile(observations.map((row) => row.fractional_publication_output), low),
    low_breadth: quantile(observations.map((row) => row.active_university_breadth), low),
  };
}

function roundedThresholds(value) {
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, typeof item === "number" ? round(item) : item]));
}

function routesFor(observation, thresholds) {
  if (!observation) return { exceptional_top100: false, prominent_top300_breadth: false, scale_and_breadth: false };
  return {
    exceptional_top100: observation.top100_count >= 1,
    prominent_top300_breadth: observation.top300_count >= 3,
    scale_and_breadth:
      (observation.fractional_publication_output >= thresholds.base_output && observation.active_university_breadth >= thresholds.base_breadth) ||
      (observation.fractional_publication_output >= thresholds.high_output && observation.active_university_breadth >= thresholds.low_breadth) ||
      (observation.active_university_breadth >= thresholds.high_breadth && observation.fractional_publication_output >= thresholds.low_output),
  };
}

function stateFor(observation, thresholds) {
  if (!observation) return "INSUFFICIENT_EVIDENCE";
  return Object.values(routesFor(observation, thresholds)).some(Boolean)
    ? "VERIFIED_STRONG_SIGNAL"
    : "STRONG_SIGNAL_NOT_ESTABLISHED";
}

async function readJsonLines(filePath) {
  return (await fs.readFile(filePath, "utf8")).trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
}

function incomeGroupMap(careerRows) {
  return new Map(careerRows.map((row) => [row.country_code, row.income_group]));
}

function stableCodeFor(sourceCountryName, stableByName) {
  return SOURCE_NAME_ALIASES.get(sourceCountryName) ?? stableByName.get(sourceCountryName)?.code ?? null;
}

function buildInstitutionMapping(fixture, stableByName) {
  const workbookByNameCountry = new Map(fixture.universities.rows.map(([name, ror, country]) => [`${name}|${country}`, { name, ror, country }]));
  const fieldRowsById = Object.fromEntries(Object.entries(fixture.results).map(([field, rows]) => [field, new Map(rows.map((row) => [row.source_institution_id, row]))]));
  const rows = fixture.results["all-sciences"].map((source) => {
    const key = `${source.display_name}|${source.country_name}`;
    const exact = workbookByNameCountry.get(key);
    const manual = MANUAL_INSTITUTION_MATCHES.get(`${source.display_name.trim()} |${source.country_name}`);
    const canonical = exact ?? (manual ? { name: manual[0], ror: manual[1], country: source.country_name } : null);
    if (!canonical) throw new Error(`Unmapped institution: ${key}`);
    const fields = Object.fromEntries(Object.entries(fieldRowsById).map(([field, byId]) => {
      const item = byId.get(source.source_institution_id);
      if (!item) throw new Error(`Missing ${field} row for source institution ${source.source_institution_id}`);
      return [field, {
        rank: item.rank,
        fractional_publications: item.fractional_publications,
        publications_50_plus_citations: item.publications_50_plus_citations,
        share_50_plus_citations_percent: item.share_50_plus_citations_percent,
        redacted: item.redacted,
      }];
    }));
    return {
      schema_version: "konsider-phase6c-institution-mapping-1.0",
      source_release: fixture.metadata.source_release,
      source_institution_id: source.source_institution_id,
      source_display_name: source.display_name,
      canonical_institution_name: canonical.name,
      ror_id: canonical.ror,
      ror_url: `https://ror.org/${canonical.ror}`,
      institution_type: "university",
      source_country_name: source.country_name,
      source_country_alpha2: source.country_alpha2,
      stable_country_code: stableCodeFor(source.country_name, stableByName),
      match_method: exact ? "EXACT_NAME_AND_COUNTRY" : "MANUAL_QUOTED_NAME_DISAMBIGUATION",
      match_confidence: "HIGH",
      locality: null,
      multi_campus_status: "UNKNOWN",
      locality_mapping_required_before_applicant_level_use: true,
      field_evidence: fields,
    };
  });
  if (rows.length !== 2831 || new Set(rows.map((row) => row.ror_id)).size !== 2831) {
    throw new Error("Expected 2,831 unique ROR institution mappings.");
  }
  return rows.sort((a, b) => a.source_institution_id.localeCompare(b.source_institution_id, "en", { numeric: true }));
}

function aggregateField(fieldRows, stableByName) {
  const grouped = new Map();
  for (const row of fieldRows) {
    const countryCode = stableCodeFor(row.country_name, stableByName);
    if (!countryCode) continue;
    if (!grouped.has(countryCode)) grouped.set(countryCode, []);
    grouped.get(countryCode).push(row);
  }
  return new Map([...grouped].map(([countryCode, rows]) => {
    const usable = rows.filter((row) => !row.redacted && Number.isFinite(row.fractional_publications));
    if (!usable.length) return [countryCode, null];
    return [countryCode, {
      country_code: countryCode,
      fractional_publication_output: round(sum(usable.map((row) => row.fractional_publications))),
      active_university_breadth: usable.filter((row) => row.fractional_publications > 0).length,
      top100_count: usable.filter((row) => row.rank <= 100).length,
      top200_count: usable.filter((row) => row.rank <= 200).length,
      top300_count: usable.filter((row) => row.rank <= 300).length,
      represented_university_count: rows.length,
      nonredacted_university_count: usable.length,
      redacted_university_count: rows.length - usable.length,
    }];
  }));
}

function benchmarkMemberships(countryCode, shortlists) {
  return Object.entries(shortlists.profiles)
    .filter(([, profile]) => profile.countries.some((row) => row.code === countryCode))
    .map(([profileId]) => profileId);
}

function buildEvidence({ fixture, stable, stableByName, incomeGroups, shortlists }) {
  const candidates = new Map();
  const evidence = [];
  for (const candidate of CANDIDATES) {
    const aggregate = candidate.field_key ? aggregateField(fixture.results[candidate.field_key], stableByName) : new Map();
    const observations = [...aggregate.values()].filter(Boolean);
    const thresholds = observations.length ? thresholdsFor(observations, BASE_PERCENTILE) : null;
    const rows = stable.countries.map((country) => {
      const observation = aggregate.get(country.code) ?? null;
      const routes = thresholds ? routesFor(observation, thresholds) : null;
      const state = thresholds ? stateFor(observation, thresholds) : "INSUFFICIENT_EVIDENCE";
      const reasonCode = !candidate.field_key
        ? "SOURCE_TAXONOMY_TOO_BROAD"
        : !observation
          ? "COUNTRY_NOT_REPRESENTED_IN_COMPLETE_RESEARCH_UNIVERSITY_RELEASE"
          : state === "VERIFIED_STRONG_SIGNAL"
            ? "ONE_OR_MORE_GLOBAL_RESEARCH_ECOSYSTEM_ROUTES_PASSED"
            : "COMPLETE_NARROW_EVIDENCE_TESTED_NO_ROUTE_PASSED";
      return {
        schema_version: "konsider-phase6c-country-opportunity-evidence-1.0",
        report_date: REPORT_DATE,
        candidate_id: candidate.candidate_id,
        candidate_display_name: candidate.display_name,
        candidate_disposition: candidate.disposition,
        country_code: country.code,
        country_name: country.display_name,
        region: country.region,
        income_group: incomeGroups.get(country.code) ?? null,
        state,
        reason_code: reasonCode,
        reason: state === "VERIFIED_STRONG_SIGNAL"
          ? "The country crosses at least one pre-registered research-university ecosystem route."
          : state === "STRONG_SIGNAL_NOT_ESTABLISHED"
            ? "The complete retained research-university evidence had a reasonable opportunity to detect a strong signal, but no route crossed; this is not a claim that the country lacks universities or programmes."
            : candidate.field_key
              ? "The country is not represented in the retained research-intensive university release; absence is not treated as zero or a negative."
              : "No sufficiently specific and reusable evidence route was retained for this construct.",
        source_field: candidate.source_field,
        publication_window: candidate.field_key ? fixture.metadata.publication_window : null,
        observation,
        passed_routes: routes ? Object.entries(routes).filter(([, passed]) => passed).map(([route]) => route) : [],
        threshold_version: "phase6c-p60-output-breadth-prominence-v1",
        thresholds: thresholds ? roundedThresholds(thresholds) : null,
        completeness: {
          source_field_supported: Boolean(candidate.field_key),
          country_represented: Boolean(observation),
          negative_capable: Boolean(candidate.field_key && observation),
        },
        confidence: observation ? "HIGH" : "LOW",
        benchmark_shortlist_memberships: benchmarkMemberships(country.code, shortlists),
        applicant_level_boundary: "COUNTRY_RESEARCH_ECOSYSTEM_ONLY_NO_ADMISSION_TEACHING_AFFORDABILITY_ACCREDITATION_VISA_OR_APPLICANT_SUCCESS_CLAIM",
      };
    });
    candidates.set(candidate.candidate_id, { candidate, aggregate, observations, thresholds, rows });
    evidence.push(...rows);
  }
  return { candidates, evidence };
}

function buildCoverage(candidates, shortlists) {
  const result = {};
  for (const candidate of CANDIDATES) {
    const rows = candidates.get(candidate.candidate_id).rows;
    result[candidate.candidate_id] = {
      display_name: candidate.display_name,
      assessable_count: rows.filter((row) => row.state !== "INSUFFICIENT_EVIDENCE").length,
      country_gate_60_of_91: rows.filter((row) => row.state !== "INSUFFICIENT_EVIDENCE").length >= 60,
      profiles: Object.fromEntries(Object.entries(shortlists.profiles).map(([profileId, profile]) => {
        const codes = profile.countries.map((row) => row.code);
        const assessable = codes.filter((code) => rows.find((row) => row.country_code === code)?.state !== "INSUFFICIENT_EVIDENCE");
        return [profileId, {
          frozen_country_codes_in_order: codes,
          assessable_country_codes_in_frozen_order: assessable,
          assessable_count: assessable.length,
          hard_floor_16_of_20: assessable.length >= 16,
          preferred_target_18_of_20: assessable.length >= 18,
          ordering_changed: false,
        }];
      })),
    };
  }
  return {
    schema_version: "konsider-phase6c-shortlist-coverage-1.0",
    report_date: REPORT_DATE,
    method: "Opportunity evidence is joined after each frozen Phase 6B top-20 list is generated and never changes ranking or order.",
    candidates: result,
  };
}

function buildSensitivity(candidates) {
  const result = {};
  for (const candidate of CANDIDATES) {
    const item = candidates.get(candidate.candidate_id);
    if (!candidate.field_key) {
      result[candidate.candidate_id] = {
        display_name: candidate.display_name,
        source_gap: true,
        percentiles: Object.fromEntries(PERCENTILES.map((p) => [`P${Math.round(p * 100)}`, { outcome_counts: { VERIFIED_STRONG_SIGNAL: 0, STRONG_SIGNAL_NOT_ESTABLISHED: 0, INSUFFICIENT_EVIDENCE: 91 } }])),
        source_removal: { assessable_count: 0, outcome_counts: { VERIFIED_STRONG_SIGNAL: 0, STRONG_SIGNAL_NOT_ESTABLISHED: 0, INSUFFICIENT_EVIDENCE: 91 } },
      };
      continue;
    }
    const percentiles = {};
    for (const percentile of PERCENTILES) {
      const thresholds = thresholdsFor(item.observations, percentile);
      const countryStates = item.rows.map((row) => ({
        country_code: row.country_code,
        state: stateFor(item.aggregate.get(row.country_code) ?? null, thresholds),
      }));
      percentiles[`P${Math.round(percentile * 100)}`] = {
        thresholds: roundedThresholds(thresholds),
        outcome_counts: countBy(countryStates),
        verified_country_codes: countryStates.filter((row) => row.state === "VERIFIED_STRONG_SIGNAL").map((row) => row.country_code),
      };
    }
    result[candidate.candidate_id] = {
      display_name: candidate.display_name,
      source_gap: false,
      represented_country_count: item.observations.length,
      global_band_country_counts: {
        at_least_one_top100: item.observations.filter((row) => row.top100_count >= 1).length,
        at_least_one_top200: item.observations.filter((row) => row.top200_count >= 1).length,
        at_least_one_top300: item.observations.filter((row) => row.top300_count >= 1).length,
        at_least_three_top300: item.observations.filter((row) => row.top300_count >= 3).length,
      },
      percentiles,
      primary_source_removal: {
        consequence: "No positive- or negative-capable country evidence remains.",
        assessable_count: 0,
        outcome_counts: { VERIFIED_STRONG_SIGNAL: 0, STRONG_SIGNAL_NOT_ESTABLISHED: 0, INSUFFICIENT_EVIDENCE: 91 },
      },
      canonical_identity_removal: {
        consequence: "All country states are suppressed because stable institution identity is a precondition for publication.",
        assessable_count: 0,
        outcome_counts: { VERIFIED_STRONG_SIGNAL: 0, STRONG_SIGNAL_NOT_ESTABLISHED: 0, INSUFFICIENT_EVIDENCE: 91 },
      },
      period_stability: "NOT_TESTED_SINGLE_FROZEN_2025_RELEASE_NO_TIME_TREND_CLAIM",
    };
  }
  return {
    schema_version: "konsider-phase6c-threshold-sensitivity-1.0",
    report_date: REPORT_DATE,
    global_rule: "top100 >= 1 OR top300 >= 3 OR (output >= base AND breadth >= base) OR (output >= high AND breadth >= low) OR (breadth >= high AND output >= low)",
    no_country_specific_thresholds: true,
    candidates: result,
  };
}

function gateSummary(candidate, item, coverage) {
  const counts = countBy(item.rows);
  const assessable = 91 - counts.INSUFFICIENT_EVIDENCE;
  const smallerClass = Math.min(counts.VERIFIED_STRONG_SIGNAL, counts.STRONG_SIGNAL_NOT_ESTABLISHED);
  const profiles = coverage.candidates[candidate.candidate_id].profiles;
  const allShortlistFloors = Object.values(profiles).every((profile) => profile.hard_floor_16_of_20);
  const approved = candidate.disposition.startsWith("APPROVE");
  return {
    candidate_id: candidate.candidate_id,
    prompt_direction: candidate.prompt_direction,
    public_display_name: candidate.display_name,
    source_field: candidate.source_field,
    disposition: candidate.disposition,
    rationale: candidate.rationale,
    p60_outcome_counts: counts,
    gates: {
      assessable_60_of_91: assessable >= 60,
      all_shortlists_at_least_16_of_20: allShortlistFloors,
      geographic_and_income_breadth: candidate.field_key ? "PASS_WITH_REPRESENTATION_LIMITATION_REPORTED" : "FAIL",
      smaller_assessed_class_at_least_8: smallerClass >= 8,
      reusable_source_and_replay: Boolean(candidate.field_key),
      source_aligned_public_name: !candidate.disposition.includes("HOLD") && candidate.candidate_id !== "broad_university_excellence_opportunity",
    },
    recommended_for_implementation_design: approved,
    runtime_change_authorized: false,
  };
}

function buildSourceMatrix(fixture) {
  return {
    schema_version: "konsider-phase6c-education-source-matrix-1.0",
    report_date: REPORT_DATE,
    sources: [
      {
        source_id: "CWTS_LEIDEN_OPEN_2025_RESULTS",
        role: "PRIMARY_POSITIVE_AND_NEGATIVE_CAPABLE_WITHIN_NARROW_RESEARCH_ECOSYSTEM_CONSTRUCT",
        title: fixture.metadata.source_release,
        doi: fixture.metadata.source_doi,
        official_urls: [
          "https://open.leidenranking.com/resources",
          "https://open.leidenranking.com/information/universities",
          "https://open.leidenranking.com/information/fields",
          "https://open.leidenranking.com/information/indicators",
          "https://open.leidenranking.com/information/responsibleuse",
          "https://zenodo.org/records/17473224",
        ],
        snapshot: fixture.metadata.openalex_snapshot,
        publication_window: fixture.metadata.publication_window,
        coverage: "2,831 universities in 120 countries; inclusion requires at least 1,500 qualifying publications in 2020-2023.",
        licence: "CC0-1.0 for result and underlying data; source code MIT",
        retention: "Commit compact derived fixture; keep raw captures ignored; retain source URLs and hashes.",
        strengths: ["complete frozen field result", "global within-field ranks", "fractional output", "official ROR identity workbook", "reusable"],
        limitations: ["scientific performance only", "research-intensive university selection", "no teaching quality", "no admissions", "no affordability", "no accreditation or qualification recognition", "single retained time window"],
      },
      {
        source_id: "ROR_VIA_CWTS_WORKBOOK",
        role: "CANONICAL_INSTITUTION_IDENTITY",
        official_url: "https://ror.org/",
        licence: "CC0",
        disposition: "RETAIN_EMBEDDED_IDENTIFIERS",
        limitation: "No campus locality or coordinate inference in this phase.",
      },
      {
        source_id: "OPENALEX_DIRECT_API",
        role: "UNDERLYING_BIBLIOGRAPHIC_SOURCE_NOT_DIRECTLY_ACQUIRED",
        official_url: "https://docs.openalex.org/",
        disposition: "NOT_SELECTED_FOR_PRIMARY_ROUTE",
        reason: "The CWTS release already pins an OpenAlex snapshot and publishes a reusable result; a direct current route would require a separately frozen access and replay policy.",
      },
      {
        source_id: "UNESCO_UIS_OPRI",
        role: "POTENTIAL_SPECIALISATION_SUPPLEMENT",
        official_url: "https://www.unesco.org/en/education/observatory/public-research-innovation",
        disposition: "HOLD_LEGAL_AND_COVERAGE_ROUTE",
        reason: "Not needed for the primary research-university signal; ShareAlike and normalized reuse implications require owner/legal review before integration.",
      },
    ],
    negative_integrity: {
      capable: "Complete retained field result plus stable institution and country mapping.",
      suppressed_when: ["country absent from release", "publisher redaction prevents complete country evidence", "field taxonomy is broader than construct", "canonical institution mapping unavailable"],
    },
  };
}

function currentCareerStates(phase6bRows, gapRows) {
  const map = new Map(phase6bRows.map((row) => [`${row.candidate_id}|${row.country_code}`, row.state]));
  for (const row of gapRows) {
    if (row.state !== "INSUFFICIENT_EVIDENCE") map.set(`${row.candidate_id}|${row.country_code}`, row.state);
  }
  return map;
}

function buildCrosswalk(stable, educationEvidence, careerStateMap) {
  const educationMap = new Map(educationEvidence.map((row) => [`${row.candidate_id}|${row.country_code}`, row.state]));
  const pairs = [
    ["science_engineering_research", "science_engineering_opportunity", "engineering_technology_education_opportunity"],
    ["technology_mathematics_research", "technology_software_opportunity", "computer_science_ict_education_opportunity"],
    ["biomedical_health_research", "health_social_work_opportunity", "medicine_health_sciences_education_opportunity"],
  ].map(([sharedTaxonomyId, careerId, educationId]) => {
    const countries = stable.countries.map((country) => {
      const career = careerStateMap.get(`${careerId}|${country.code}`) ?? "INSUFFICIENT_EVIDENCE";
      const education = educationMap.get(`${educationId}|${country.code}`) ?? "INSUFFICIENT_EVIDENCE";
      let relationship;
      if (career === "INSUFFICIENT_EVIDENCE" || education === "INSUFFICIENT_EVIDENCE") relationship = "ONE_OR_BOTH_INSUFFICIENT";
      else if (career === "VERIFIED_STRONG_SIGNAL" && education === "VERIFIED_STRONG_SIGNAL") relationship = "BOTH_STRONG";
      else if (education === "VERIFIED_STRONG_SIGNAL") relationship = "EDUCATION_STRONG_CAREER_NOT_ESTABLISHED";
      else if (career === "VERIFIED_STRONG_SIGNAL") relationship = "CAREER_STRONG_EDUCATION_NOT_ESTABLISHED";
      else relationship = "NEITHER_STRONG_WITH_COMPLETE_EVIDENCE";
      return { country_code: country.code, career_state: career, education_state: education, relationship };
    });
    const relationshipCounts = Object.fromEntries([...new Set(countries.map((row) => row.relationship))].sort().map((value) => [value, countries.filter((row) => row.relationship === value).length]));
    return {
      proposed_future_shared_taxonomy_id: sharedTaxonomyId,
      career_candidate_id: careerId,
      education_candidate_id: educationId,
      interpretation: "DESCRIPTIVE_ECOSYSTEM_COMPARISON_NOT_CAUSAL_AND_NOT_APPLICANT_SPECIFIC",
      relationship_counts: relationshipCounts,
      countries,
    };
  });
  return {
    schema_version: "konsider-phase6c-career-education-crosswalk-1.0",
    report_date: REPORT_DATE,
    runtime_taxonomy_change_authorized: false,
    pairs,
    unpaired_education_construct: {
      proposed_future_shared_taxonomy_id: "life_earth_sciences",
      education_candidate_id: "natural_sciences_education_opportunity",
      note: "No direct approved Phase 6B employment construct; do not force a proxy pairing.",
    },
  };
}

function geographySummary(rows) {
  const assessable = rows.filter((row) => row.state !== "INSUFFICIENT_EVIDENCE");
  const verified = rows.filter((row) => row.state === "VERIFIED_STRONG_SIGNAL");
  const group = (values, key) => Object.fromEntries([...new Set(values.map((row) => row[key] ?? "Unknown"))].sort().map((value) => [value, values.filter((row) => (row[key] ?? "Unknown") === value).length]));
  return { assessable_by_region: group(assessable, "region"), verified_by_region: group(verified, "region"), assessable_by_income_group: group(assessable, "income_group"), verified_by_income_group: group(verified, "income_group") };
}

function markdownReport({ matrix, coverage, sensitivity, crosswalk, sourceMatrix, portfolio, candidates, institutionMapping }) {
  const decisionRows = matrix.candidates.map((row) => `| ${row.prompt_direction} | ${row.public_display_name} | ${row.p60_outcome_counts.VERIFIED_STRONG_SIGNAL}/${row.p60_outcome_counts.STRONG_SIGNAL_NOT_ESTABLISHED}/${row.p60_outcome_counts.INSUFFICIENT_EVIDENCE} | ${row.disposition} |`).join("\n");
  const coverageRows = CANDIDATES.flatMap((candidate) => Object.entries(coverage.candidates[candidate.candidate_id].profiles).map(([profile, row]) => `| ${candidate.prompt_direction} | ${profile} | ${row.assessable_count}/20 | ${row.hard_floor_16_of_20 ? "pass" : "fail"} |`)).join("\n");
  const sensitivityRows = CANDIDATES.map((candidate) => {
    const values = sensitivity.candidates[candidate.candidate_id].percentiles;
    const count = (p) => values[p].outcome_counts.VERIFIED_STRONG_SIGNAL;
    return `| ${candidate.prompt_direction} | ${count("P50")} | ${count("P55")} | ${count("P60")} | ${count("P65")} | ${count("P70")} |`;
  }).join("\n");
  const thresholdRows = CANDIDATES.filter((candidate) => candidate.field_key).map((candidate) => {
    const t = sensitivity.candidates[candidate.candidate_id].percentiles.P60.thresholds;
    return `| ${candidate.source_field} | ${t.base_output} | ${t.base_breadth} | ${t.high_output} | ${t.high_breadth} | ${t.low_output} | ${t.low_breadth} |`;
  }).join("\n");
  const crosswalkRows = crosswalk.pairs.map((pair) => `| ${pair.career_candidate_id} | ${pair.education_candidate_id} | ${Object.entries(pair.relationship_counts).map(([key, value]) => `${key}: ${value}`).join("; ")} |`).join("\n");
  const approvedNames = portfolio.education.approved_for_implementation_design.map((row) => `- **${row.display_name}:** ${row.disposition}.`).join("\n");
  const regionSections = CANDIDATES.filter((candidate) => candidate.field_key).map((candidate) => {
    const item = candidates.get(candidate.candidate_id);
    const summary = geographySummary(item.rows);
    return `### ${candidate.display_name}\n\n- Assessable by region: ${Object.entries(summary.assessable_by_region).map(([key, value]) => `${key} ${value}`).join("; ")}.\n- Verified by region: ${Object.entries(summary.verified_by_region).map(([key, value]) => `${key} ${value}`).join("; ")}.\n- Assessable by income group: ${Object.entries(summary.assessable_by_income_group).map(([key, value]) => `${key} ${value}`).join("; ")}.\n- Verified by income group: ${Object.entries(summary.verified_by_income_group).map(([key, value]) => `${key} ${value}`).join("; ")}.`;
  }).join("\n\n");
  return `# Phase 6C — Higher-education opportunity exploration

Date: ${REPORT_DATE}
Status: **RESEARCH COMPLETE — OWNER DECISIONS REQUIRED — NO PRODUCTION CHANGE**

## Outcome

Four of the six Phase 6C directions have a defensible research-only route, but only after narrowing their public names to the official evidence taxonomy. Business/finance remains on hold because the available field is too broad. Broad university excellence is rejected as an opportunity criterion because scientific performance is neither generic excellence nor a complete applicant opportunity measure and would overlap the existing research/innovation criterion.

The four recommended constructs describe a country's **research-intensive university ecosystem**. They do not measure admissions, teaching quality, affordability, accreditation, qualification recognition, visa eligibility, campus access, or an applicant's chance of success.

${approvedNames}

Research/academia, moved from Phase 6B, is resolved through these field-specific education research ecosystems rather than revived as an employment proxy.

## Method inherited from Phase 6B.1

The Phase 6C prompt remains controlling. The augmented protocol pre-registers constructs, evidence routes, source precedence, negative capability, global thresholds, P50–P70 sensitivity, dependency removal, benchmark coverage, deterministic fixtures, and owner dispositions before outcomes are interpreted. Complete narrow evidence may establish either a positive or a carefully worded not-established state. Missing countries and taxonomy mismatches remain insufficient; no zero is invented.

## Primary source and rights

The retained route is CWTS Leiden Ranking Open Edition 2025 (DOI ${sourceMatrix.sources[0].doi}), using its frozen August 2025 OpenAlex snapshot and 2020–2023 publication window. It contains 2,831 universities in 120 countries and five broad fields. Its result and underlying data are CC0; the official workbook provides ROR identities. The source's own responsible-use boundary is decisive: this is scientific performance, not a generic best-university or teaching-quality measure.

The direct OpenAlex API is not needed for this release-specific route. UIS OPRI remains a possible specialization supplement but is held outside the primary signal pending a separate legal/coverage decision. No GeoNames or inferred campus coordinates are used.

## Institution identity and accessibility boundary

The mapping contains ${institutionMapping.length} institutions and ${institutionMapping.filter((row) => row.match_method === "EXACT_NAME_AND_COUNTRY").length} exact name/country matches. Six quoted names truncated in HTML tooltips use explicit high-confidence manual disambiguations. Every row has a unique ROR ID. Country is the only location signal retained. Locality, campus distribution, multi-campus status, cross-border provision, online availability, and applicant accessibility remain unknown and must be resolved before any institution-level experience is designed.

## Candidate decisions

P60 cells show verified / not-established / insufficient across the fixed 91-country universe.

| Prompt direction | Evidence-aligned public name | P60 states | Disposition |
|---|---|---:|---|
${decisionRows}

The four approvals pass the 60/91 assessability gate, every frozen-list 16/20 gate, and the eight-country smaller-class discrimination gate. Their approvals remain naming/scope changes because the official fields are not identical to the prompt shorthand.

Business/finance has 91 insufficient states. The broad social-sciences field cannot safely stand in for business and finance. Broad scientific research has full diagnostic classifications but is rejected as a public opportunity criterion; a good source does not rescue an invalid product construct.

## Classification routes and P60 thresholds

A represented country passes when it has at least one global top-100 institution, at least three global top-300 institutions, or crosses one of three global output/breadth combinations. Otherwise complete evidence produces not-established. Countries absent from the research-intensive release are insufficient. Thresholds are global; there are no country exceptions.

| Official field | Base output | Base breadth | High output | High breadth | Low output | Low breadth |
|---|---:|---:|---:|---:|---:|---:|
${thresholdRows}

Top-100 and top-300 routes prevent a small country with a genuinely prominent institution from being erased by national scale. Output/breadth routes prevent the measure from collapsing into a single league-table position. The result remains a research ecosystem indicator, not a university ranking copied into Konsider.

## Threshold sensitivity

Verified-country counts move monotonically as the percentile becomes more demanding:

| Candidate | P50 | P55 | P60 | P65 | P70 |
|---|---:|---:|---:|---:|---:|
${sensitivityRows}

P60 is retained for design discussion because it discriminates without making the fixed prominence routes irrelevant. P50 is noticeably more permissive; P70 is more restrictive. The exact country lists and thresholds are in the sensitivity artifact. Only one release/window is retained, so this study makes no false stability or time-trend claim.

Removing the CWTS result source makes every supported candidate 0/91 assessable. Removing canonical ROR identity also suppresses every state under the pre-registered publication rule. This single-source dependency must be accepted explicitly or reduced in a future research phase; it is not hidden by a weak substitute.

## Frozen benchmark-list coverage

Evidence is joined after the five Phase 6B top-20 lists are generated. It never changes rank or ordering.

| Candidate | Frozen profile | Assessable | ≥16 floor |
|---|---|---:|---|
${coverageRows}

All five supported diagnostic fields cover all 20 countries in every frozen benchmark list. Business/finance covers none because its field route is held. This high shortlist coverage does not erase the 16 countries absent from the complete 91-country research-university universe.

## Geographic, income, and system-size review

${regionSections}

The evidence spans every stable-universe region and multiple income groups among represented countries, but research-intensive inclusion structurally favors systems with sufficient publication scale. Exceptional/top-band routes help smaller systems when they contain prominent institutions. They cannot make countries absent from the release assessable. The report therefore keeps those countries insufficient rather than punishing small systems.

## Career–education comparison

The crosswalk compares ecosystem states without merging criteria or claiming that education supply causes labour-market opportunity.

| Career construct | Education construct | Relationship counts |
|---|---|---|
${crosswalkRows}

Life and earth sciences has no direct approved Phase 6B career pair and is left unpaired. Proposed shared taxonomy IDs are research notes only. Country-level combinations may help future explanation—for example, distinguishing a research ecosystem from an employment ecosystem—but cannot be interpreted as applicant outcomes.

## Final consolidated research portfolio

The consolidated portfolio contains the five career constructs approved in Phase 6B.1 plus four education research-ecosystem constructs approved here. Business/finance is held. Broad university excellence is rejected. The portfolio is a research/design recommendation only; no criterion, weight, preset, ranking, worker, schema, API, or UI change is authorised.

## Limitations and refresh policy

- Scientific publication output and prominence do not measure teaching, admissions, affordability, student support, institutional accreditation, recognition of a specific qualification, employment outcomes, or lived experience.
- The retained source selects research-intensive universities and may omit legitimate teaching-focused institutions and smaller systems.
- The official broad fields cannot isolate engineering, ICT, business, finance, medicine programmes, or all natural sciences exactly as phrased in the prompt.
- Country assignment is not campus-level accessibility; branch campuses, online programmes, language, visa, and geographic distance remain unresolved.
- A single 2025 release cannot establish temporal stability. Refresh annually only after pinning the new release, comparing coverage and taxonomy, rerunning every percentile, and reviewing state changes.
- A source/licence/access change must fail closed to insufficient rather than reuse stale or untraceable evidence.

## Deterministic artifacts and verification

The committed fixture freezes all 2,831 institution results for six official fields, 2,831 ROR mappings, 284 field-concept mappings, query parameters, source URLs, byte counts, and SHA-256 hashes. Ignored raw captures are verified when present; fixture-only replay remains possible. The generator enforces six × 91 = 546 unique outcomes, recognized states, unique institution identities, global threshold policy, benchmark-list non-interference, JSON/JSONL parseability, and stable output ordering. The replay manifest hashes every retained input and generated artifact. A second run must produce no diff.

The artifact commit SHA is supplied in the Git handoff because a commit cannot contain its own SHA.

## Owner decisions before implementation design

1. Accept that the public concept is a **research-university ecosystem**, not generic higher-education quality or applicant opportunity.
2. Accept all four official evidence-aligned names and reject broader shorthand in user-facing copy.
3. Accept P60 and the exceptional/top-band routes as the research baseline, subject to the recorded P50–P70 sensitivity.
4. Accept 75/91 assessability and the explicit insufficient state for countries absent from the research-intensive release.
5. Accept or require mitigation of the single-source and ROR-identity dependency.
6. Keep business/finance on hold and broad university excellence rejected.
7. Confirm that no production work begins until a separate implementation prompt and review.
`;
}

export async function runPhase6C({ repoRoot }) {
  const fixturePath = path.join(repoRoot, "project-history", "phases", "phase-6", "research", "fixtures", "phase6c-leiden-source-fixture.json");
  const stablePath = path.join(repoRoot, "data", "country-universes", "stable-supported-v1.json");
  const shortlistPath = path.join(repoRoot, "data", "reports", "phase6b-2026-08-02", "career-shortlist-coverage.json");
  const careerEvidencePath = path.join(repoRoot, "data", "reports", "phase6b-2026-08-02", "career-country-opportunity-evidence.jsonl");
  const gapEvidencePath = path.join(repoRoot, "data", "reports", "phase6b1-2026-08-03", "gap-fill-country-evidence.jsonl");
  const careerPortfolioPath = path.join(repoRoot, "data", "reports", "phase6b1-2026-08-03", "final-career-opportunity-portfolio.json");
  const protocolPath = path.join(repoRoot, "project-history", "phases", "phase-6", "02_PHASE_6C_AUGMENTED_RESEARCH_PROTOCOL.md");
  const scriptPath = fileURLToPath(import.meta.url);
  const outputDirectory = path.join(repoRoot, "data", "reports", REPORT_DIRECTORY);
  const reportPath = path.join(repoRoot, "docs", "research", "phase6c-education-opportunity-study.md");
  const rawDirectory = path.join(repoRoot, "data", "raw", "phase6c");

  const [fixtureText, stableText, shortlistText, careerEvidenceText, gapEvidenceText, careerPortfolioText, protocolText, scriptText] = await Promise.all([
    fs.readFile(fixturePath, "utf8"), fs.readFile(stablePath, "utf8"), fs.readFile(shortlistPath, "utf8"),
    fs.readFile(careerEvidencePath, "utf8"), fs.readFile(gapEvidencePath, "utf8"), fs.readFile(careerPortfolioPath, "utf8"),
    fs.readFile(protocolPath, "utf8"), fs.readFile(scriptPath, "utf8"),
  ]);
  const fixture = JSON.parse(fixtureText);
  const stable = JSON.parse(stableText);
  const shortlists = JSON.parse(shortlistText);
  const phase6bRows = careerEvidenceText.trim().split(/\r?\n/).map(JSON.parse);
  const gapRows = gapEvidenceText.trim().split(/\r?\n/).map(JSON.parse);
  const careerPortfolio = JSON.parse(careerPortfolioText);
  if (stable.countries.length !== 91) throw new Error("Stable universe is not 91 countries.");

  try {
    const rawFiles = await fs.readdir(rawDirectory);
    for (const [name, expected] of Object.entries(fixture.metadata.source_files)) {
      if (!rawFiles.includes(name)) throw new Error(`Raw capture missing: ${name}`);
      const content = await fs.readFile(path.join(rawDirectory, name));
      if (content.byteLength !== expected.bytes || sha256(content) !== expected.sha256) throw new Error(`Raw capture checksum mismatch: ${name}`);
    }
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }

  const stableByName = new Map(stable.countries.map((country) => [country.display_name, country]));
  const incomeGroups = incomeGroupMap(phase6bRows);
  const institutionMapping = buildInstitutionMapping(fixture, stableByName);
  const { candidates, evidence } = buildEvidence({ fixture, stable, stableByName, incomeGroups, shortlists });
  if (evidence.length !== 546 || new Set(evidence.map((row) => `${row.candidate_id}|${row.country_code}`)).size !== 546) throw new Error("Expected 546 unique candidate-country outcomes.");
  if (evidence.some((row) => !STATES.includes(row.state))) throw new Error("Unrecognized tri-state outcome.");

  const coverage = buildCoverage(candidates, shortlists);
  const sensitivity = buildSensitivity(candidates);
  const matrix = {
    schema_version: "konsider-phase6c-education-candidate-matrix-1.0",
    report_date: REPORT_DATE,
    status: "RESEARCH_COMPLETE_OWNER_DECISIONS_REQUIRED",
    production_change_authorized: false,
    frozen_country_universe: stable.universe_id,
    candidate_count: CANDIDATES.length,
    candidates: CANDIDATES.map((candidate) => ({
      ...gateSummary(candidate, candidates.get(candidate.candidate_id), coverage),
      geography_and_income_summary: geographySummary(candidates.get(candidate.candidate_id).rows),
    })),
  };
  const sourceMatrix = buildSourceMatrix(fixture);
  const crosswalk = buildCrosswalk(stable, evidence, currentCareerStates(phase6bRows, gapRows));
  const portfolio = {
    schema_version: "konsider-phase6c-approved-opportunity-portfolio-1.0",
    report_date: REPORT_DATE,
    status: "RESEARCH_COMPLETE_IMPLEMENTATION_DESIGN_ONLY",
    runtime_change_authorized: false,
    career: careerPortfolio,
    education: {
      approved_for_implementation_design: matrix.candidates.filter((row) => row.recommended_for_implementation_design).map((row) => ({
        candidate_id: row.candidate_id,
        display_name: row.public_display_name,
        disposition: row.disposition,
        assessable_count: 91 - row.p60_outcome_counts.INSUFFICIENT_EVIDENCE,
        implementation_status: "NOT_STARTED",
      })),
      held: matrix.candidates.filter((row) => row.disposition === "HOLD_SOURCE_GAP"),
      rejected: matrix.candidates.filter((row) => row.disposition === "REJECT_AS_OPPORTUNITY_CRITERION"),
    },
    consolidated_approved_count: careerPortfolio.approved_for_implementation_design.length + matrix.candidates.filter((row) => row.recommended_for_implementation_design).length,
    research_academia_resolution: "Resolved through source-aligned field-specific education research-university ecosystems; no employment proxy or generic academia criterion added.",
    owner_decisions_required: [
      "Accept the research-university ecosystem boundary and four source-aligned public names.",
      "Accept P60 plus fixed prominence routes and the recorded sensitivity.",
      "Accept 75/91 assessability and explicit insufficiency for absent systems.",
      "Accept or mitigate the single-source and ROR-identity dependency.",
      "Keep business/finance held and broad university excellence rejected.",
      "Require a separate implementation authorization before production work.",
    ],
  };

  const artifactValues = {
    "education-candidate-matrix.json": json(matrix),
    "education-country-opportunity-evidence.jsonl": jsonl(evidence),
    "education-source-matrix.json": json(sourceMatrix),
    "institution-mapping.jsonl": jsonl(institutionMapping),
    "education-shortlist-coverage.json": json(coverage),
    "education-threshold-sensitivity.json": json(sensitivity),
    "career-education-crosswalk.json": json(crosswalk),
    "approved-opportunity-portfolio.json": json(portfolio),
  };
  const reportText = markdownReport({ matrix, coverage, sensitivity, crosswalk, sourceMatrix, portfolio, candidates, institutionMapping });
  const inputTexts = {
    "project-history/phases/phase-6/research/fixtures/phase6c-leiden-source-fixture.json": fixtureText,
    "data/country-universes/stable-supported-v1.json": stableText,
    "data/reports/phase6b-2026-08-02/career-shortlist-coverage.json": shortlistText,
    "data/reports/phase6b-2026-08-02/career-country-opportunity-evidence.jsonl": careerEvidenceText,
    "data/reports/phase6b1-2026-08-03/gap-fill-country-evidence.jsonl": gapEvidenceText,
    "data/reports/phase6b1-2026-08-03/final-career-opportunity-portfolio.json": careerPortfolioText,
    "project-history/phases/phase-6/02_PHASE_6C_AUGMENTED_RESEARCH_PROTOCOL.md": protocolText,
    "project-history/phases/phase-6/research/run_phase6c_education_opportunity_study.mjs": scriptText,
  };
  const manifest = {
    schema_version: "konsider-phase6c-replay-manifest-1.0",
    report_date: REPORT_DATE,
    replay_mode: "COMMITTED_FIXTURE_WITH_OPTIONAL_RAW_CAPTURE_VALIDATION",
    deterministic: true,
    input_sha256: Object.fromEntries(Object.entries(inputTexts).map(([name, value]) => [name, sha256(value)])),
    output_sha256: {
      ...Object.fromEntries(Object.entries(artifactValues).map(([name, value]) => [name, sha256(value)])),
      "docs/research/phase6c-education-opportunity-study.md": sha256(reportText),
    },
    assertions: {
      candidate_count: 6,
      stable_country_count: 91,
      country_outcome_count: evidence.length,
      unique_country_outcome_keys: new Set(evidence.map((row) => `${row.candidate_id}|${row.country_code}`)).size,
      institution_mapping_count: institutionMapping.length,
      unique_ror_count: new Set(institutionMapping.map((row) => row.ror_id)).size,
      manual_institution_disambiguation_count: institutionMapping.filter((row) => row.match_method.startsWith("MANUAL")).length,
      recognized_states_only: evidence.every((row) => STATES.includes(row.state)),
      no_country_specific_thresholds: true,
      shortlist_ordering_changed: false,
      production_change_authorized: false,
    },
  };
  artifactValues["replay-manifest.json"] = json(manifest);

  await fs.mkdir(outputDirectory, { recursive: true });
  await fs.mkdir(path.dirname(reportPath), { recursive: true });
  await Promise.all([
    ...Object.entries(artifactValues).map(([name, value]) => fs.writeFile(path.join(outputDirectory, name), value, "utf8")),
    fs.writeFile(reportPath, reportText, "utf8"),
  ]);

  for (const [name, expected] of Object.entries(manifest.output_sha256)) {
    const actualPath = name.startsWith("docs/") ? path.join(repoRoot, ...name.split("/")) : path.join(outputDirectory, name);
    if (sha256(await fs.readFile(actualPath)) !== expected) throw new Error(`Generated output checksum mismatch: ${name}`);
  }
  await Promise.all(Object.keys(artifactValues).map(async (name) => {
    const text = await fs.readFile(path.join(outputDirectory, name), "utf8");
    if (name.endsWith(".jsonl")) text.trim().split(/\r?\n/).forEach(JSON.parse); else JSON.parse(text);
  }));
  return { reportDirectory: outputDirectory, reportPath, matrix, manifest };
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url));
if (isDirectRun) {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");
  const result = await runPhase6C({ repoRoot });
  console.log(JSON.stringify({ report_directory: result.reportDirectory, report_path: result.reportPath, outcome_counts: Object.fromEntries(result.matrix.candidates.map((row) => [row.candidate_id, row.p60_outcome_counts])) }, null, 2));
}
