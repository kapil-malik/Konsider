const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../../..");

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, relativePath), "utf8"));
}

const batch1 = readJson(
  "project-history/phases/phase-3/research/candidate-batch-1/phase3c_batch1.json",
).records;
const batch2 = readJson(
  "project-history/phases/phase-3/research/candidate-batch-2/phase3c_batch2.json",
).criteria;
const batch3 = readJson(
  "project-history/phases/phase-3/research/candidate-batch-3/phase3c_batch3.json",
).criteria;

const phase3Rows = [
  ...batch1.map((row) => ({
    id: row.criterion_id,
    name: row.name,
    status: row.status,
    decision: null,
    recommendation: row.recommendation,
    granularity: row.natural_granularity,
    freshness: row.freshness_class,
    coverage: row.coverage,
    sources: row.source_candidates || [],
    comparability: row.comparability_notes || [],
    licensing: row.licensing_notes || [],
    blockers: row.blocker_codes || [],
    limitations: row.caveat_codes || [],
  })),
  ...[...batch2, ...batch3].map((row) => ({
    id: row.id,
    name: row.name,
    status: row.status,
    decision: row.decision,
    recommendation: row.recommendation,
    granularity: row.granularity,
    freshness: row.freshness,
    coverage: row.coverage,
    sources: row.sources || [],
    comparability: row.methodology || [],
    licensing: row.licensing || [],
    blockers: row.blockers || [],
    limitations: row.limitations || [],
  })),
];

const expectedIds = [
  "C01",
  "C05",
  "C06",
  "C08",
  "C11",
  "C12",
  "C13",
  "C14",
  "C15",
  "C16",
  "C17",
  "C19",
  "C21",
  "C22",
  "C25",
  "C26",
  "C29",
  "C30",
  "C32",
  "C33",
  "C34",
  "C35",
  "C36",
  "C38",
  "C40",
  "C42",
  "C45",
  "C48",
  "C49",
  "C50",
  "C53",
  "C54",
  "C56",
  "C57",
  "C58",
  "C62",
  "C66",
  "C67",
  "C68",
  "C69",
  "C70",
  "C71",
  "C75",
  "C76",
  "C78",
];

const recommendationById = {};
function recommend(ids, value) {
  for (const id of ids) recommendationById[id] = value;
}

recommend(["C66"], "FIRST_WAVE");
recommend(["C05", "C67", "C68"], "SECOND_WAVE");
recommend(
  ["C11", "C16", "C42", "C50", "C56", "C57", "C58"],
  "RESEARCH_ONLY",
);
recommend(
  [
    "C01",
    "C06",
    "C08",
    "C12",
    "C13",
    "C14",
    "C15",
    "C17",
    "C21",
    "C22",
    "C25",
    "C26",
    "C32",
    "C33",
    "C34",
    "C35",
    "C36",
    "C38",
    "C40",
    "C45",
    "C76",
  ],
  "PROFILE_PHASE",
);
recommend(
  [
    "C19",
    "C29",
    "C30",
    "C48",
    "C49",
    "C53",
    "C54",
    "C62",
    "C69",
    "C70",
    "C71",
    "C75",
    "C78",
  ],
  "REJECT_LOCALITY_PROXY",
);

const localityMaterialIds = new Set([
  "C01",
  "C05",
  "C06",
  "C08",
  "C11",
  "C12",
  "C13",
  "C14",
  "C15",
  "C16",
  "C17",
  "C25",
  "C26",
  "C38",
  "C40",
  "C42",
  "C45",
  "C50",
  "C53",
  "C56",
  "C57",
  "C58",
  "C66",
  "C67",
  "C68",
  "C69",
  "C76",
]);

const defensibleIndependentProxyIds = new Set([
  "C05",
  "C11",
  "C16",
  "C56",
  "C57",
  "C58",
  "C66",
  "C67",
  "C68",
]);

const occupationSpecificIds = new Set(["C12", "C13", "C14", "C15", "C38"]);
const profileRequiredIds = new Set(
  Object.keys(recommendationById).filter(
    (id) => recommendationById[id] === "PROFILE_PHASE",
  ),
);

const evidenceOverrides = {
  C01: ["INSTITUTION", "APPLICANT_PROFILE"],
  C05: ["METRO", "INSTITUTION"],
  C06: ["INSTITUTION", "APPLICANT_PROFILE"],
  C08: ["REGION_STATE", "CITY", "APPLICANT_PROFILE"],
  C11: ["METRO"],
  C12: ["METRO", "APPLICANT_PROFILE"],
  C13: ["METRO", "REGION_STATE", "APPLICANT_PROFILE"],
  C14: ["METRO", "APPLICANT_PROFILE"],
  C15: ["METRO", "REGION_STATE", "APPLICANT_PROFILE"],
  C16: ["METRO"],
  C17: ["METRO", "APPLICANT_PROFILE"],
  C21: ["COUNTRY", "APPLICANT_PROFILE"],
  C22: ["COUNTRY", "APPLICANT_PROFILE"],
  C25: ["METRO", "APPLICANT_PROFILE"],
  C26: ["COUNTRY", "APPLICANT_PROFILE"],
  C32: ["COUNTRY", "APPLICANT_PROFILE"],
  C33: ["COUNTRY", "APPLICANT_PROFILE"],
  C34: ["COUNTRY", "APPLICANT_PROFILE"],
  C35: ["COUNTRY", "INSTITUTION", "APPLICANT_PROFILE"],
  C36: ["COUNTRY", "APPLICANT_PROFILE"],
  C38: ["REGION_STATE", "INSTITUTION", "APPLICANT_PROFILE"],
  C40: ["CITY", "APPLICANT_PROFILE"],
  C42: ["CITY", "REGION_STATE"],
  C45: ["COUNTRY", "CITY", "APPLICANT_PROFILE"],
  C50: ["REGION_STATE", "METRO"],
  C53: ["COUNTRY"],
  C56: ["UTILITY_SERVICE_AREA"],
  C57: ["UTILITY_SERVICE_AREA"],
  C58: ["METRO", "CITY"],
  C66: ["CITY"],
  C67: ["CITY"],
  C68: ["CITY", "REGION_STATE"],
  C69: ["CITY", "REGION_STATE"],
  C76: ["COUNTRY", "APPLICANT_PROFILE"],
};

const localityUnitOverrides = {
  C01: "INSTITUTION",
  C05: "METRO",
  C06: "INSTITUTION",
  C08: "REGION_STATE",
  C11: "METRO",
  C12: "METRO",
  C13: "METRO",
  C14: "METRO",
  C15: "METRO",
  C16: "METRO",
  C17: "METRO",
  C25: "METRO",
  C38: "REGION_STATE",
  C40: "CITY",
  C42: "CITY",
  C45: "CITY",
  C50: "METRO",
  C56: "UTILITY_SERVICE_AREA",
  C57: "UTILITY_SERVICE_AREA",
  C58: "METRO",
  C66: "CITY",
  C67: "CITY",
  C68: "CITY",
  C69: "CITY",
};

const seriousCandidateSources = {
  C05: [
    {
      source_candidate_id: "C05-OPENALEX-SNAPSHOT",
      publisher: "OurResearch",
      distributor: "OpenAlex public S3 snapshot",
      dataset: "OpenAlex data snapshot",
      exact_asset_or_api:
        "s3://openalex/data/institutions and s3://openalex/data/works; exact quarterly manifest not yet frozen",
      access_method: "Anonymous S3 snapshot; gzip-compressed JSON Lines",
      licence: "CC0",
      licence_url: "https://help.openalex.org/hc/en-us/articles/24397762024087-Pricing",
      commercial_use: "permitted",
      redistribution: "permitted",
      freshness: "Quarterly public snapshot; API updates more frequently",
      evidence_level: "EXACT_FAMILY_NOT_PINNED_ASSET",
    },
  ],
  C11: [
    {
      source_candidate_id: "C11-OECD-FUA-LABOUR",
      publisher: "OECD",
      distributor: "OECD Data Explorer",
      dataset: "Labour market - functional urban areas",
      exact_asset_or_api:
        "OECD.CFE.EDS,DSD_FUA_LAB@DF_LABOUR via OECD SDMX API",
      access_method: "Public SDMX REST API",
      licence: "OECD open-access policy; exact dataflow notice must be frozen",
      licence_url: "https://www.oecd.org/en/about/oecd-open-by-default-policy.html",
      commercial_use: "expected permitted; exact dataflow verification required",
      redistribution: "expected permitted; exact dataflow verification required",
      freshness: "Dataflow updated 2026-01-27",
      evidence_level: "EXACT_API_FAMILY",
    },
  ],
  C25: [
    {
      source_candidate_id: "C25-OECD-REGIONAL-HOUSING",
      publisher: "OECD and national statistical agencies",
      distributor: "OECD Data Explorer",
      dataset: "National and regional house price indices",
      exact_asset_or_api:
        "OECD.SDD.TPS,DSD_RHPI@DF_RHPI_ALL via OECD SDMX API",
      access_method: "Public SDMX REST API",
      licence: "OECD open-access policy; third-party component boundary remains",
      licence_url: "https://www.oecd.org/en/about/oecd-open-by-default-policy.html",
      commercial_use: "not established for every upstream series",
      redistribution: "not established for every upstream series",
      freshness: "Dataflow updated 2026-07-23",
      evidence_level: "EXACT_API_BUT_INSUFFICIENT_CONSTRUCT",
    },
  ],
  C40: [
    {
      source_candidate_id: "C40-EF-EPI-2025",
      publisher: "EF Education First",
      distributor: "EF",
      dataset: "EF English Proficiency Index 2025",
      exact_asset_or_api: "Published country, region, and city reports; no reusable raw dataset",
      access_method: "Website/report",
      licence: "No dataset-specific production licence verified",
      licence_url: "https://www.ef.com/wwen/epi/about-epi/",
      commercial_use: "not established",
      redistribution: "not established; raw data are not shared",
      freshness: "2025 edition using 2024 tests",
      evidence_level: "CONCEPTUAL_NOT_REPRODUCIBLE",
    },
  ],
  C57: [
    {
      source_candidate_id: "C57-WB-IBNET-UTILITY",
      publisher: "World Bank / participating utilities",
      distributor: "IBNET and World Bank reproducibility catalog",
      dataset: "IBNET utility performance data",
      exact_asset_or_api:
        "IBNET_2023.xlsx and New_IBNET_2024.xlsx referenced by World Bank reproducibility catalog entry 484",
      access_method: "Catalog/workbook; parts are limited-access",
      licence: "No complete production redistribution conclusion for utility submissions",
      licence_url: "https://reproducibility.worldbank.org/catalog/484",
      commercial_use: "not established for all records",
      redistribution: "some data explicitly omitted as limited-access",
      freshness: "Historical through 2022; pilot/revised records through 2024",
      evidence_level: "EXACT_ASSETS_PARTLY_LIMITED",
    },
  ],
  C58: [
    {
      source_candidate_id: "C58-GHS-UCDB-OOKLA",
      publisher: "European Commission JRC; upstream Speedtest by Ookla",
      distributor: "JRC Open Data Portal",
      dataset: "GHS-UCDB R2024A v1.2 socioeconomic theme",
      exact_asset_or_api:
        "GHS_UCDB_THEME_SOCIOECONOMIC_GLOBE_R2024A_V1_2.zip; SC_CON_DSF_2023 and SC_CON_DSM_2023",
      access_method: "Anonymous HTTPS ZIP containing CSV/XLSX/GPKG",
      licence:
        "JRC catalog marks the asset CC BY 4.0, but the documented upstream Ookla map tiles are CC BY-NC-SA 4.0",
      licence_url:
        "https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd",
      commercial_use: "ambiguous because of the upstream non-commercial term",
      redistribution: "ambiguous component boundary; production gate fails pending clarification",
      freshness: "JRC asset updated 2026-05-15; metric reference year 2023",
      evidence_level: "EXACT_ASSET_LICENCE_CONFLICT",
    },
  ],
  C66: [
    {
      source_candidate_id: "C66-GHS-UCDB-UTCI",
      publisher: "European Commission JRC / Copernicus Climate Change Service",
      distributor: "JRC Open Data Portal",
      dataset: "GHS-UCDB R2024A v1.2 climate theme",
      exact_asset_or_api:
        "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip; CL_UTC_T32_2020",
      access_method: "Anonymous HTTPS ZIP containing CSV/XLSX/GPKG",
      licence: "CC BY 4.0 on the exact JRC downloadable asset",
      licence_url:
        "https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd",
      commercial_use: "permitted with attribution",
      redistribution: "permitted with attribution",
      freshness:
        "JRC asset updated 2026-05-15; underlying decadal climate reference ends in 2020",
      evidence_level: "EXACT_ASSET_VERIFIED",
    },
  ],
  C67: [
    {
      source_candidate_id: "C67-GHS-UCDB-CLIMATE-PROJECTIONS",
      publisher: "European Commission JRC / Copernicus Climate Change Service",
      distributor: "JRC Open Data Portal",
      dataset: "GHS-UCDB R2024A v1.2 climate theme",
      exact_asset_or_api:
        "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip; scenario-specific CL_* projection fields",
      access_method: "Anonymous HTTPS ZIP containing CSV/XLSX/GPKG",
      licence: "CC BY 4.0 on the exact JRC downloadable asset",
      licence_url:
        "https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd",
      commercial_use: "permitted with attribution",
      redistribution: "permitted with attribution",
      freshness: "Current asset; scenario horizons include 2030-2070",
      evidence_level: "EXACT_ASSET_CONSTRUCT_NOT_FROZEN",
    },
  ],
  C68: [
    {
      source_candidate_id: "C68-GHS-UCDB-MULTIHAZARD",
      publisher: "European Commission JRC; upstream MYRIAD-HESA research",
      distributor: "JRC Open Data Portal",
      dataset: "GHS-UCDB R2024A v1.2 hazard/risk theme",
      exact_asset_or_api:
        "GHS_UCDB_THEME_HAZARD_RISK_GLOBE_R2024A_V1_2.zip; HZ_CEV_*_2015",
      access_method: "Anonymous HTTPS ZIP containing CSV/XLSX/GPKG",
      licence: "CC BY 4.0 on the exact JRC downloadable asset",
      licence_url:
        "https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd",
      commercial_use: "permitted with attribution",
      redistribution: "permitted with attribution",
      freshness: "Current asset, but event-set reference years stop at 2015",
      evidence_level: "EXACT_ASSET_STALE_FOR_RANKING",
    },
  ],
};

const customCoverage = {
  C05: {
    country: "Expected broad coverage; not measured against stable_supported_v1",
    locality:
      "Unknown until a pinned snapshot is spatially mapped from institution coordinates to the frozen locality universe",
  },
  C11: {
    country:
      "OECD FUA data cover OECD members and selected accessions, not the 91-country universe",
    locality:
      "1,285 FUAs are described for OECD members except Costa Rica plus three accession countries; exact stable-universe intersection not measured",
  },
  C25: {
    country:
      "Mainly OECD and selected non-OECD economies; insufficient for stable_supported_v1",
    locality:
      "Regional observations are uneven and are not a comparable rent-to-household-income measure",
  },
  C40: {
    country: "116 countries/regions in EF EPI 2025; stable-universe intersection not measured",
    locality:
      "Thresholded, self-selected city samples; native-English destinations are not symmetrically observed",
  },
  C57: {
    country:
      "Historical IBNET described more than 150 countries, but current reproducible/open records are not complete",
    locality:
      "Utility submissions are voluntary, temporally uneven, and partly limited-access",
  },
  C58: {
    country:
      "Measured 89/91 countries under the proposed top-five GHSL universe; ATG and GRD have no qualifying GHSL urban centre",
    locality:
      "Measured 388/388 selected urban centres with non-negative fixed and mobile 2023 values",
  },
  C66: {
    country:
      "Measured 89/91 countries under the proposed top-five GHSL universe; ATG and GRD have no qualifying GHSL urban centre",
    locality:
      "Measured 388/388 selected urban centres with a non-negative CL_UTC_T32_2020 value",
  },
  C67: {
    country:
      "Potentially 89/91 under the proposed GHSL universe; scenario-field validity not fully measured",
    locality:
      "Potentially 388 selected urban centres; exact construct/scenario intersection not measured",
  },
  C68: {
    country:
      "Potentially 89/91 under the proposed GHSL universe; exact chosen hazard intersection not measured",
    locality:
      "Potentially 388 selected urban centres; historical event fields require construct and zero/missing validation",
  },
};

const customRisks = {
  C05: [
    "Bibliometric output is not the whole innovation ecosystem.",
    "Institution disambiguation, multi-campus lineage, field mix, and citation-age bias require controls.",
    "The public snapshot is roughly 330 GB compressed, creating high replay and refresh cost.",
  ],
  C11: [
    "Published FUA values may be modelled from regional values using population shares.",
    "A broad metro labour market remains occupation-neutral.",
    "Coverage is concentrated in OECD economies.",
  ],
  C25: [
    "Affordability requires rent or purchase specification, dwelling size, tenure, household income, and tax context.",
    "Regional house-price indices measure change, not a comparable price-to-income level.",
  ],
  C40: [
    "Self-selected online test takers are not representative.",
    "Proficiency is not institutional or daily-life usability.",
    "Native-English destinations and cities are not symmetrically measured.",
  ],
  C57: [
    "Utility territories do not align cleanly with cities or metros.",
    "Voluntary reporting creates selection, age, and survivorship bias.",
    "Continuity hours do not establish potability, pressure, or household access.",
  ],
  C58: [
    "Speedtest users are self-selected and missingness depends on test activity.",
    "The JRC/upstream licence boundary is contradictory for commercial use.",
    "2023 values are already fast-moving for a connectivity criterion.",
  ],
  C66: [
    "This is extreme heat exposure, not broad extreme-weather risk.",
    "The fact sheet description says days above the UTCI threshold while its methodology wording says pixel count; exact semantics require confirmation.",
    "The latest decadal reference ends in 2020 and does not capture neighbourhood-scale heat.",
  ],
  C67: [
    "Scenario choice, horizon, baseline, hazard weighting, and user climate preferences are normative.",
    "A broad climate-exposure composite would obscure distinct hazards.",
  ],
  C68: [
    "Occurrence is not expected loss, severity, vulnerability, or current risk.",
    "The event-set reference stops at 2015.",
    "Rare-event counts are unstable and sensitive to reporting and boundary choices.",
  ],
};

const customAggregation = {
  C05:
    "Top-two mean of a field-normalised, size-aware metro research-output score; minimum one valid metro; expose institution and work lineage.",
  C11:
    "Top-two mean of metro employment/participation/unemployment composite after an exact FUA coverage probe; minimum one valid metro.",
  C16:
    "Top-two mean of comparable metro new-firm density only if a reproducible registration denominator exists.",
  C56:
    "No aggregation until measured outage/reliability observations can be attached to validated utility service areas.",
  C57:
    "Top-two mean of utility continuity scores only after service territories are mapped to eligible localities and record selection is frozen.",
  C58:
    "Top-two mean of fixed-network performance among eligible metros, minimum one valid locality; do not combine fixed and mobile without sensitivity analysis.",
  C66:
    "Lower-is-better mean of the two lowest-exposure eligible urban-centre scores, or the single score where only one qualifies; retain all locality evidence.",
  C67:
    "No composite until one scenario, horizon, hazard, and direction are frozen; then apply a policy-driven top-N opportunity aggregation.",
  C68:
    "Top-two mean of the lowest comparable locality hazard scores only after severity, exposure, period, and zero/missing semantics are frozen.",
};

function inferEvidence(row) {
  if (evidenceOverrides[row.id]) return evidenceOverrides[row.id];
  if (row.granularity && row.granularity.includes("PROFILE")) {
    return ["COUNTRY", "APPLICANT_PROFILE"];
  }
  if (row.granularity && row.granularity.includes("GRID")) {
    return ["COUNTRY", "REGION_STATE"];
  }
  return ["COUNTRY"];
}

function summarizePhase3Coverage(coverage) {
  if (!coverage) return "Not recorded";
  if (coverage.measured) {
    const fresh = coverage.fresh ?? coverage.valid ?? coverage.found;
    return `${fresh}/${coverage.denominator || 91} measured fresh/valid at Phase 3 cutoff`;
  }
  return coverage.stable_91_estimate || coverage.expected_band || "Not measured";
}

function normalizeSource(source) {
  return {
    source_candidate_id: source.source_candidate_id || null,
    publisher: source.publisher || null,
    distributor: source.distributor || source.publisher || null,
    dataset: source.dataset || null,
    exact_asset_or_api: source.exact_asset_or_api || source.series_or_table || null,
    access_method: source.access_method || source.access_url || null,
    licence: source.licence || null,
    licence_url: source.licence_url || null,
    commercial_use: source.commercial_use || "Not separately established in this row",
    redistribution: source.redistribution || "See retained Phase 3 licensing evidence",
    freshness: source.freshness || source.version || null,
    evidence_level: source.evidence_level || null,
  };
}

function defaultAggregation(row, recommendation) {
  if (customAggregation[row.id]) return customAggregation[row.id];
  if (recommendation === "PROFILE_PHASE") {
    return "None in Phase 5; evaluate only after applicant/household parameters and any required co-location rule exist.";
  }
  if (recommendation === "REJECT_LOCALITY_PROXY") {
    return "DIRECT_COUNTRY_ONLY; locality aggregation would change or misstate the construct.";
  }
  return "No production aggregation until an exact comparable locality source clears feasibility, coverage, freshness, and licensing gates.";
}

function defaultBlockers(row, recommendation) {
  const blockers = [...row.blockers];
  if (recommendation === "PROFILE_PHASE") {
    blockers.push("FUTURE_PROFILE_CONTEXT_REQUIRED");
  }
  if (recommendation === "REJECT_LOCALITY_PROXY") {
    blockers.push("LOCALITY_PROXY_CHANGES_CONSTRUCT");
  }
  if (recommendation === "RESEARCH_ONLY") {
    blockers.push("NO_PRODUCTION_READY_LOCALITY_SOURCE");
  }
  return [...new Set(blockers)];
}

const matrix = phase3Rows
  .map((row) => {
    const recommendation = recommendationById[row.id];
    const phase5Sources = seriousCandidateSources[row.id] || [];
    const sources = [...phase5Sources, ...row.sources].map(normalizeSource);
    const coverage = customCoverage[row.id] || {
      country: summarizePhase3Coverage(row.coverage),
      locality: "Not measured; no exact production locality asset was promoted in Phase 3",
    };
    return {
      criterion_id: row.id,
      exact_name: row.name,
      original_phase3_disposition: {
        status: row.status,
        decision: row.decision,
        recommendation: row.recommendation,
        natural_granularity: row.granularity,
      },
      natural_evidence_level: inferEvidence(row),
      locality_materially_changes_relocation_usefulness:
        localityMaterialIds.has(row.id),
      locality_derived_country_proxy_semantically_defensible:
        defensibleIndependentProxyIds.has(row.id),
      occupation_specific: occupationSpecificIds.has(row.id),
      requires_applicant_or_household_data: profileRequiredIds.has(row.id),
      applicability_dimensions: profileRequiredIds.has(row.id)
        ? ["APPLICANT_OR_HOUSEHOLD_CONTEXT"]
        : [],
      recommended_locality_unit: localityUnitOverrides[row.id] || null,
      candidate_sources: sources,
      exact_source_asset_or_api:
        sources[0]?.exact_asset_or_api || "No exact source asset retained",
      source_publisher: sources[0]?.publisher || "No source retained",
      source_distributor: sources[0]?.distributor || "No distributor retained",
      access_method: sources[0]?.access_method || "Not established",
      licensing_and_redistribution_evidence:
        sources[0]?.licence ||
        row.licensing.join(" ") ||
        "Not established for locality production",
      freshness: sources[0]?.freshness || row.freshness,
      estimated_country_coverage: coverage.country,
      estimated_locality_coverage_within_covered_countries: coverage.locality,
      cross_country_comparability: [
        ...row.comparability,
        ...(recommendation === "PROFILE_PHASE"
          ? ["Cannot be compared honestly without explicit profile parameters."]
          : []),
      ],
      major_construct_risks: customRisks[row.id] || row.limitations,
      possible_aggregation_method: defaultAggregation(row, recommendation),
      recommendation,
      precise_blockers: defaultBlockers(row, recommendation),
    };
  })
  .sort((a, b) => a.criterion_id.localeCompare(b.criterion_id));

const actualIds = matrix.map((row) => row.criterion_id);
if (matrix.length !== 45 || new Set(actualIds).size !== 45) {
  throw new Error(`Expected 45 unique criteria, got ${matrix.length}/${new Set(actualIds).size}`);
}
if (JSON.stringify(actualIds) !== JSON.stringify(expectedIds)) {
  throw new Error(`Criterion ID mismatch:\n${actualIds.join(",")}`);
}
if (Object.keys(recommendationById).length !== 45) {
  throw new Error("Every criterion must have one Phase 5A recommendation");
}
const allowedRecommendations = new Set([
  "FIRST_WAVE",
  "SECOND_WAVE",
  "RESEARCH_ONLY",
  "PROFILE_PHASE",
  "REJECT_LOCALITY_PROXY",
]);
for (const row of matrix) {
  if (!allowedRecommendations.has(row.recommendation)) {
    throw new Error(`Invalid recommendation for ${row.criterion_id}`);
  }
}
const firstWave = matrix.filter((row) => row.recommendation === "FIRST_WAVE");
if (firstWave.length > 3) throw new Error("First wave exceeds three criteria");

const report = {
  schema_version: "konsider-phase5a-locality-disposition-matrix-1.0",
  generated_at: "2026-07-28T00:00:00+05:30",
  evidence_cutoff: "2026-07-28",
  stable_universe_id: "stable_supported_v1",
  criterion_count: matrix.length,
  recommendation_counts: Object.fromEntries(
    [...allowedRecommendations].map((name) => [
      name,
      matrix.filter((row) => row.recommendation === name).length,
    ]),
  ),
  first_wave_ids: firstWave.map((row) => row.criterion_id),
  matrix,
};

const decisionSummary = {
  schema_version: "konsider-phase5a-decision-summary-1.0",
  date: "2026-07-28",
  decision: "APPROVE_ONE_CRITERION_FIRST_WAVE",
  first_wave: [
    {
      research_id: "C66",
      target_product_name: "Extreme heat exposure",
      source_asset:
        "GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip#CL_UTC_T32_2020",
      locality_unit: "GHSL urban centre",
      proposed_aggregation: "LOWEST_EXPOSURE_TOP_2_MEAN_MIN_1",
      measured_coverage: {
        countries: 89,
        stable_countries: 91,
        localities: 388,
        missing_countries: ["ATG", "GRD"],
      },
      licence_conclusion: "PASS_FOR_EXACT_JRC_ASSET_WITH_ATTRIBUTION",
      pre_onboarding_blockers: [
        "Confirm the fact sheet's day-count versus pixel-count methodology wording.",
        "Freeze the final score transform and sensitivity analysis.",
        "Decide in Phase 5B whether C66 remains research lineage only and the narrowed product construct receives a new runtime criterion ID.",
      ],
    },
  ],
  locality_universe_direction: {
    policy_id: "major-urban-opportunity-v1-draft",
    source: "GHS-UCDB R2024A v1.2",
    selection:
      "Up to five most-populous qualifying urban centres per country using frozen 2025 source population, selected before criterion values are observed.",
    measured_inventory: {
      countries_with_localities: 89,
      selected_localities: 388,
      countries_without_qualifying_locality: ["ATG", "GRD"],
    },
  },
  deferred_boundaries: {
    applicant_profile_engine: "OUT_OF_SCOPE",
    household_affordability_engine: "OUT_OF_SCOPE",
    visa_and_licensing_engine: "OUT_OF_SCOPE",
    conversational_exploration: "FUTURE_PHASE",
  },
};

fs.writeFileSync(
  path.join(__dirname, "criterion-disposition-matrix.json"),
  `${JSON.stringify(report, null, 2)}\n`,
  "utf8",
);
fs.writeFileSync(
  path.join(__dirname, "decision-summary.json"),
  `${JSON.stringify(decisionSummary, null, 2)}\n`,
  "utf8",
);

console.log(
  `Wrote ${matrix.length} criteria; first wave: ${firstWave
    .map((row) => row.criterion_id)
    .join(", ")}`,
);
