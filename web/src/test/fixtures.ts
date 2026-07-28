import type {
  Catalog,
  CatalogCriterion,
  Comparison,
  Contribution,
  CountryMetric,
  RankedCountry,
  Ranking,
} from '../api/types'

const source = {
  source_id: 'public-source',
  publisher: 'Public Data Publisher',
  source_version: 'source-v1',
  dataset_version: 'dataset-v1',
  canonical_page_url: 'https://example.com/public-data',
  attribution: 'Public Data Publisher; transformed by Konsider.',
}

const criterion = (
  id: string,
  displayName: string,
  category: string,
  ready = true,
  experimental = false,
): CatalogCriterion => ({
  id,
  display_name: displayName,
  category,
  description: `${displayName} description`,
  direction: 'higher_is_better',
  raw_unit: 'index_0_100',
  interpretation: 'Higher observations receive higher comparative scores.',
  caveats: [`${displayName} caveat.`],
  quality_limitations: [`${displayName} limitation.`],
  ready,
  enabled: ready,
  default_enabled: ready,
  experimental,
  scoring_method_version: `${id}_v1`,
  coverage_mode: ready ? 'GLOBAL_CORE' : 'DIAGNOSTIC_ONLY',
  valid_country_count: ready ? 5 : 0,
  stable_country_count: 5,
  coverage_percentage: ready ? 100 : 0,
  pcc_activation_threshold: null,
  missing_country_count: ready ? 0 : 5,
  concise_caveat: `${displayName} caveat.`,
  sources: [
    {
      ...source,
      reference_period: ready ? 'latest 2025' : 'latest 2021',
    },
  ],
})

export const airCriterion = criterion('air', 'Air quality', 'Environment')
export const infrastructureCriterion = criterion(
  'infrastructure',
  'Infrastructure readiness',
  'Infrastructure',
  true,
  true,
)
export const unavailableCriterion = criterion('health', 'UHC service coverage', 'Healthcare', false)
export const jobCriterion: CatalogCriterion = {
  ...criterion('jobs', 'Overall job-market opportunity', 'Work'),
  coverage_mode: 'CONDITIONAL_COMPLETE_CASE',
  valid_country_count: 4,
  stable_country_count: 5,
  coverage_percentage: 80,
  pcc_activation_threshold: 0.6,
  missing_country_count: 1,
  concise_caveat: 'National labour-market conditions do not guarantee an individual job.',
}

export const catalogFixture: Catalog = {
  release_id: 'test-release',
  release_schema_version: 'test-release-schema',
  catalog_schema_version: 'test-catalog-schema',
  scoring_method_versions: ['air_v1', 'infrastructure_v1', 'jobs_v1', 'health_v1'],
  countries: Array.from({ length: 5 }, (_, index) => ({
    code: `C0${index}`,
    display_name: `Country ${index + 1}`,
    region: `Region ${index + 1}`,
  })),
  criteria: [airCriterion, infrastructureCriterion, jobCriterion, unavailableCriterion],
  profiles: [
    {
      id: 'equal_weight_mvp',
      name: 'Balanced',
      description: 'Equal test weights.',
      weights: { air: 1, infrastructure: 1, jobs: 0.4 },
    },
    {
      id: 'safety_profile',
      name: 'Safety profile',
      description: 'A different server profile.',
      weights: { air: 0.4, infrastructure: 0.8, jobs: 0.4 },
    },
  ],
}

const observation = {
  observation_id: 'observation',
  value: 72.4,
  unit: 'index_0_100',
  reference_start: '2025-01-01',
  reference_end: '2025-12-31',
  observation_method_version: 'observation-v1',
  parser_version: 'parser-v1',
  quality_flags: [],
  source_records: [{ locator: 'row 1', record_id: 'record-1' }],
}

const contribution = (
  criterionValue: CatalogCriterion,
  score: number,
): Contribution => ({
  criterion_id: criterionValue.id,
  criterion_name: criterionValue.display_name,
  score,
  normalized_weight: 0.5,
  contribution: score * 0.5,
  scoring_method_version: criterionValue.scoring_method_version,
  caveats: criterionValue.caveats,
  quality_limitations: criterionValue.quality_limitations,
  experimental: criterionValue.experimental,
  observations: [observation],
  source,
})

const country = (index: number): RankedCountry => ({
  rank: index + 1,
  country_code: `C0${index}`,
  country_name: `Country ${index + 1}`,
  region: `Region ${index + 1}`,
  total_score: 8.5 - index * 0.5,
  eligible_country_count: 5,
  contributions: [
    contribution(airCriterion, 9 - index * 0.5),
    contribution(infrastructureCriterion, 8 - index * 0.5),
  ],
  strengths: ['air'],
  tradeoffs: ['infrastructure'],
})

export const rankedCountries = Array.from({ length: 5 }, (_, index) => country(index))

const uncertaintyMetadata = {
  release_id: 'test-release',
  release_schema_version: 'test-release-schema',
  catalog_schema_version: 'test-catalog-schema',
  scoring_method_versions: ['air_v1', 'infrastructure_v1'],
  resolved_profile_id: 'equal_weight_mvp',
  normalized_weights: { air: 0.5, infrastructure: 0.5, jobs: 0 },
  all_zero_behavior: 'equal_weights_across_all_enabled_criteria',
  country_tie_breaker: 'ascending_iso3_country_code',
  rounding_tolerance: 0.00000001,
  total_eligible_country_count: 5,
  returned_result_count: 5,
  stable_universe_size: 5,
  eligible_universe_size: 5,
  excluded_country_count: 0,
  ranking_coverage_mode: 'GLOBAL_CORE' as const,
  uncertainty_status: 'NO_PARTIAL_CRITERIA_ACTIVE' as const,
  coverage_band: 'PREFERRED' as const,
  reason_codes: ['NO_PCC_AT_OR_ABOVE_ACTIVATION_THRESHOLD'],
  message_code: 'NO_PARTIAL_CRITERIA_ACTIVE',
  active_fcc_ids: ['air', 'infrastructure'],
  active_pcc_ids: [],
  ignored_pcc: [
    {
      criterion_id: 'jobs',
      raw_weight: 0.4,
      reason_code: 'BELOW_PCC_ACTIVATION_THRESHOLD',
      activation_threshold: 0.6,
    },
  ],
  robustness_k: 5,
  kth_eligible_score: 6.5,
  potential_excluded_entrants: [],
  baseline_top_k_country_codes: ['C00', 'C01', 'C02', 'C03', 'C04'],
  baseline_kth_score: 6.5,
  baseline_boundary_tie_count: 1,
  baseline_returned_result_count: 5,
  policy_version: 'uncertainty-aware-ranking-policy-1.0',
  policy_thresholds: {
    stable_universe_id: 'test-universe',
    stable_country_count: 5,
    pcc_min_valid_country_count: 4,
    preferred_missing_union_max: 1,
    hard_missing_union_max: 1,
    min_eligible_country_count: 4,
    pcc_activation_raw_weight_min: 0.6,
    diagnostic_score_max: 10,
    rounding_tolerance: 0.00000001,
  },
  excluded_countries: [],
}

export const rankingFixture: Ranking = {
  ...uncertaintyMetadata,
  rankings: rankedCountries,
}

const excludedCountry = {
  country_code: 'C04',
  country_name: 'Country 5',
  r0_rank: 2,
  r0_score: 8,
  baseline_top_k_member: false,
  non_ready_criteria: [
    {
      criterion_id: 'jobs',
      outcome: 'missing' as const,
      reason_codes: ['COV_SOURCE_RECORD_MISSING'],
      source_id: 'public-source',
      source_versions: { 'public-source': 'source-v1' },
      scoring_method_version: 'jobs_v1',
      observation_id: null,
    },
  ],
  optimistic_upper_bound: 7.2,
  could_enter_top_k: false,
}

export function rankingForStatus(status: Ranking['uncertainty_status']): Ranking {
  if (status === 'NO_PARTIAL_CRITERIA_ACTIVE') return rankingFixture
  if (status === 'FULL_COVERAGE') {
    return {
      ...rankingFixture,
      uncertainty_status: status,
      reason_codes: ['ALL_ACTIVE_PCC_HAVE_FULL_COVERAGE'],
      ranking_coverage_mode: 'CONDITIONAL_COMPLETE_CASE',
      active_pcc_ids: ['jobs'],
      ignored_pcc: [],
    }
  }

  const isCoverageLimit = status === 'COVERAGE_LIMIT_EXCEEDED'
  const couldEnter = status === 'POTENTIALLY_AFFECTED'
  const baselineMember = status === 'BASELINE_TOP_K_EXCLUDED'
  return {
    ...rankingFixture,
    uncertainty_status: status,
    coverage_band: isCoverageLimit ? 'BLOCKED' : 'PREFERRED',
    reason_codes: [status],
    ranking_coverage_mode: isCoverageLimit ? 'GLOBAL_CORE' : 'CONDITIONAL_COMPLETE_CASE',
    eligible_universe_size: 4,
    total_eligible_country_count: 4,
    excluded_country_count: 1,
    active_pcc_ids: ['jobs'],
    ignored_pcc: [],
    kth_eligible_score: isCoverageLimit ? null : 6.8,
    potential_excluded_entrants: couldEnter ? ['C04'] : [],
    excluded_countries: [
      {
        ...excludedCountry,
        baseline_top_k_member: baselineMember,
        optimistic_upper_bound: isCoverageLimit ? null : excludedCountry.optimistic_upper_bound,
        could_enter_top_k: isCoverageLimit ? null : couldEnter,
      },
    ],
    rankings: isCoverageLimit ? rankedCountries : rankedCountries.slice(0, 4),
    returned_result_count: isCoverageLimit ? 5 : 4,
  }
}

const comparisonCodes = ['C00', 'C01', 'C02', 'C03']

export const comparisonFixture: Comparison = {
  ...uncertaintyMetadata,
  requested_country_codes: comparisonCodes,
  comparison_country_count: 4,
  country_summaries: comparisonCodes.map((countryCode, index) => ({
    country_code: countryCode,
    country_name: `Country ${index + 1}`,
    comparison_data_complete: true,
    ranking_eligible: true,
    unavailable_displayed_criterion_count: 0,
    unavailable_active_criterion_count: 0,
    aggregate_kind: 'FINAL',
    ranking_status: 'RANKED',
    message_code: 'FINAL_GLOBAL_CORE_RANK',
    total_score: rankedCountries[index].total_score,
    rank: rankedCountries[index].rank,
  })),
  criterion_rows: [airCriterion, infrastructureCriterion].map((item, criterionIndex) => ({
    criterion_id: item.id,
    criterion_name: item.display_name,
    coverage_mode: 'GLOBAL_CORE',
    experimental: item.experimental,
    cells: comparisonCodes.map((countryCode, countryIndex) => ({
      country_code: countryCode,
      availability: 'AVAILABLE',
      message_code: 'DATA_AVAILABLE',
      active_for_ranking: true,
      normalized_score: 9 - countryIndex * 0.5 - criterionIndex,
      raw_observation: 72.4,
      raw_unit: 'index_0_100',
      reference_start: '2025-01-01',
      reference_end: '2025-12-31',
      source,
      reason_codes: [],
    })),
  })),
  requested_excluded_countries: [],
  countries: rankedCountries.slice(0, 4),
  returned_result_count: 4,
}

export const comparisonWithUnavailableFixture: Comparison = {
  ...comparisonFixture,
  uncertainty_status: 'POTENTIALLY_AFFECTED',
  ranking_coverage_mode: 'CONDITIONAL_COMPLETE_CASE',
  eligible_universe_size: 4,
  total_eligible_country_count: 4,
  excluded_country_count: 1,
  active_pcc_ids: ['jobs'],
  ignored_pcc: [],
  potential_excluded_entrants: ['C03'],
  country_summaries: comparisonFixture.country_summaries.map((summary) =>
    summary.country_code === 'C03'
      ? {
          ...summary,
          comparison_data_complete: false,
          ranking_eligible: false,
          unavailable_displayed_criterion_count: 1,
          unavailable_active_criterion_count: 1,
          aggregate_kind: 'NONE',
          ranking_status: 'NOT_RANKED_ACTIVE_DATA_GAP',
          message_code: 'NOT_RANKED_ACTIVE_DATA_GAP',
          total_score: null,
          rank: null,
        }
      : summary,
  ),
  criterion_rows: [
    ...comparisonFixture.criterion_rows,
    {
      criterion_id: jobCriterion.id,
      criterion_name: jobCriterion.display_name,
      coverage_mode: 'CONDITIONAL_COMPLETE_CASE',
      experimental: false,
      cells: comparisonCodes.map((countryCode) =>
        countryCode === 'C03'
          ? {
              country_code: countryCode,
              availability: 'MISSING',
              message_code: 'DATA_NOT_AVAILABLE',
              active_for_ranking: true,
              normalized_score: null,
              raw_observation: null,
              raw_unit: null,
              reference_start: null,
              reference_end: null,
              source,
              reason_codes: ['COV_SOURCE_RECORD_MISSING'],
            }
          : {
              country_code: countryCode,
              availability: 'AVAILABLE',
              message_code: 'DATA_AVAILABLE',
              active_for_ranking: true,
              normalized_score: 7.5,
              raw_observation: 66,
              raw_unit: 'composite_percentile',
              reference_start: '2025',
              reference_end: '2025',
              source,
              reason_codes: [],
            },
      ),
    },
  ],
  requested_excluded_countries: [
    {
      ...excludedCountry,
      country_code: 'C03',
      country_name: 'Country 4',
      could_enter_top_k: true,
    },
  ],
  countries: rankedCountries.slice(0, 3),
  returned_result_count: 3,
}

export const countryMetricFixture: CountryMetric = {
  release_id: 'test-release',
  release_schema_version: 'test-release-schema',
  catalog_schema_version: 'test-catalog-schema',
  scoring_method_versions: ['air_v1', 'infrastructure_v1'],
  country: catalogFixture.countries[0],
  criteria: [airCriterion, infrastructureCriterion].map((item, index) => ({
    criterion: {
      id: item.id,
      display_name: item.display_name,
      category: item.category,
      description: item.description,
      direction: item.direction,
      raw_unit: item.raw_unit,
      interpretation: item.interpretation,
      caveats: item.caveats,
      quality_limitations: item.quality_limitations,
      ready: item.ready,
      default_enabled: item.default_enabled,
      experimental: item.experimental,
      scoring_method_version: item.scoring_method_version,
    },
    normalized_score: 9 - index,
    scoring_method_version: item.scoring_method_version,
    transform: 'test transform',
    direction: item.direction,
    input_observation_ids: [observation.observation_id],
    observations: [observation],
    source,
  })),
}
