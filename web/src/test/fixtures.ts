import type {
  CatalogCriterionV2,
  CatalogV2,
  ComparisonV2,
  ContributionV2,
  CountryDetailsV2,
  RankedCountryV2,
  RankingV2,
} from '../api/types'

const versionFields = {
  api_contract_version: 'konsider-api-2.0' as const,
  release_id: 'test-release',
  release_schema_version: 'konsider-release-5.0',
  catalog_schema_version: 'consumer-catalog-3.0',
  scoring_method_versions: ['air-v1', 'heat-v1', 'jobs-v1'],
}

export const countries = Array.from({ length: 5 }, (_, index) => ({
  entity_id: `country:C0${index}`,
  entity_type: 'COUNTRY' as const,
  display_name: `Country ${index + 1}`,
  country_codes: [`C0${index}`],
  region: `Region ${index + 1}`,
}))

const source = {
  source_id: 'public-source',
  role: 'PRIMARY_OBSERVATION' as const,
  publisher: 'Public Data Publisher',
  source_version: 'source-v1',
  dataset_version: 'dataset-v1',
  asset_uri: 'https://example.com/data.csv',
  checksum: null,
  licence_id: 'CC-BY-4.0',
  canonical_page_url: 'https://example.com/public-data',
  attribution: 'Public Data Publisher; transformed by Konsider.',
  reference_period: 'latest 2025',
}

const coverage = (
  mode: 'GLOBAL_CORE' | 'CONDITIONAL_COMPLETE_CASE' | 'DIAGNOSTIC_ONLY',
  valid = 5,
) => ({
  mode,
  stable_universe_id: 'test-country-universe',
  stable_country_count: 5,
  valid_country_count: valid,
  minimum_valid_country_count: mode === 'CONDITIONAL_COMPLETE_CASE' ? 4 : 5,
  outcome_counts: {
    valid,
    missing: 5 - valid,
    stale: 0,
    invalid: 0,
    rejected: 0,
  },
  activation_threshold: mode === 'CONDITIONAL_COMPLETE_CASE' ? 0.6 : null,
  score_range: { minimum: 0, maximum: 10 },
  source_lineage_ids: ['lineage:public'],
})

const directScope = {
  evidence_level: 'COUNTRY' as const,
  result_level: 'COUNTRY' as const,
  locality_type: null,
  derivation: 'DIRECT' as const,
  locality_universe_id: null,
  aggregation_policy_id: null,
  locality_analysis_threshold: null,
}

const localityScope = (criterionId: string) => ({
  evidence_level: 'LOCALITY' as const,
  result_level: 'COUNTRY' as const,
  locality_type: 'CITY' as const,
  derivation: 'AGGREGATED_FROM_LOCALITIES' as const,
  locality_universe_id: 'major-cities-v1',
  aggregation_policy_id: `top-two:${criterionId}`,
  locality_analysis_threshold: 0.6,
})

const criterion = (
  id: string,
  displayName: string,
  category: string,
  options: {
    ready?: boolean
    experimental?: boolean
    locality?: boolean
    coverageMode?:
      | 'GLOBAL_CORE'
      | 'CONDITIONAL_COMPLETE_CASE'
      | 'DIAGNOSTIC_ONLY'
    valid?: number
  } = {},
): CatalogCriterionV2 => ({
  id,
  display_name: displayName,
  historical_names: id === 'heat' ? ['Extreme-weather risk'] : [],
  category,
  description: `${displayName} description.`,
  direction: 'higher_is_better',
  raw_unit: 'index',
  interpretation: 'Higher scores indicate stronger comparative results.',
  caveats: [`${displayName} caveat.`],
  quality_limitations: [`${displayName} limitation.`],
  ready: options.ready ?? true,
  default_enabled: options.ready ?? true,
  experimental: options.experimental ?? false,
  scoring_method_version: `${id}-v1`,
  coverage: coverage(
    options.coverageMode ?? 'GLOBAL_CORE',
    options.valid ?? (options.ready === false ? 0 : 5),
  ),
  scope: options.locality ? localityScope(id) : directScope,
  applicability: { mode: 'UNIVERSAL', dimensions: [] },
  sources: [source],
})

export const airCriterion = criterion('air', 'Air quality', 'Environment')
export const heatCriterion = criterion('heat', 'Extreme heat exposure', 'Climate', {
  locality: true,
  experimental: true,
})
export const jobsCriterion = criterion(
  'jobs',
  'Overall job-market opportunity',
  'Work',
  { coverageMode: 'CONDITIONAL_COMPLETE_CASE', valid: 4 },
)
export const unavailableCriterion = criterion(
  'health',
  'UHC service coverage',
  'Healthcare',
  { ready: false, coverageMode: 'DIAGNOSTIC_ONLY' },
)

export const catalogFixture: CatalogV2 = {
  ...versionFields,
  coverage_policy_version: 'coverage-policy-v1',
  stable_universe_id: 'test-country-universe',
  countries,
  criteria: [airCriterion, heatCriterion, jobsCriterion, unavailableCriterion],
  preference_presets: [
    {
      id: 'balanced',
      name: 'Balanced',
      description: 'Balanced national and locality priorities.',
      weights: { air: 1, heat: 0.6, jobs: 0.4 },
    },
    {
      id: 'climate',
      name: 'Climate focused',
      description: 'Places more weight on extreme heat exposure.',
      weights: { air: 0.4, heat: 0.8, jobs: 0.4 },
    },
  ],
}

const profileAssessment = {
  status: 'NO_PROFILE_CONTEXT' as const,
  evaluated_dimensions: [],
  reasons: [
    {
      code: 'PROFILE_CONTEXT_NOT_SUPPLIED',
      severity: 'INFO' as const,
      effect: 'NOT_EVALUATED' as const,
    },
  ],
}

const observation = (criterionId: string, entityId: string, value: number) => ({
  observation_id: `obs:${criterionId}:${entityId}`,
  subject: {
    entity_id: entityId,
    entity_type: entityId.startsWith('country:')
      ? ('COUNTRY' as const)
      : ('CITY' as const),
  },
  value,
  unit: 'index',
  reference_start: '2025-01-01',
  reference_end: '2025-12-31',
  source_lineage_id: 'lineage:public',
  observation_method_version: 'observation-v1',
  parser_version: 'parser-v1',
  quality_flags: [],
})

const city = (countryIndex: number, suffix: string) => ({
  entity_id: `city:C0${countryIndex}:${suffix}`,
  entity_type: 'CITY' as const,
  display_name: `${suffix === 'a' ? 'Harbor' : suffix === 'b' ? 'Garden' : 'Summit'} City ${
    countryIndex + 1
  }`,
  country_codes: [`C0${countryIndex}`],
  region: null,
})

const directContribution = (
  criterionValue: CatalogCriterionV2,
  countryIndex: number,
  score: number,
): ContributionV2 => ({
  criterion_id: criterionValue.id,
  criterion_name: criterionValue.display_name,
  source_scope: 'COUNTRY',
  result_scope: 'COUNTRY',
  derivation: 'DIRECT',
  score,
  normalized_weight: 0.625,
  contribution: score * 0.625,
  score_id: `score:${criterionValue.id}:country:C0${countryIndex}`,
  derived_evidence_id: null,
  aggregation_policy: null,
  locality_universe: null,
  contributing_localities: [],
  observations: [
    observation(criterionValue.id, `country:C0${countryIndex}`, 72.4 - countryIndex),
  ],
  source_lineage_ids: ['lineage:public'],
  sources: [source],
  scoring_method_version: criterionValue.scoring_method_version,
  observation_method_versions: ['observation-v1'],
  quality_flags: [],
})

const localityContribution = (
  countryIndex: number,
  criterionValue = heatCriterion,
  suffixes = ['a', 'b'],
): ContributionV2 => {
  const inputs = suffixes.map((suffix, inputIndex) => {
    const entity = city(countryIndex, suffix)
    return {
      locality: entity,
      input_score: 8.8 - countryIndex * 0.3 - inputIndex * 0.5,
      observation_id: `obs:${criterionValue.id}:${entity.entity_id}`,
      score_id: `score:${criterionValue.id}:${entity.entity_id}`,
    }
  })
  return {
    criterion_id: criterionValue.id,
    criterion_name: criterionValue.display_name,
    source_scope: 'LOCALITY',
    result_scope: 'COUNTRY',
    derivation: 'AGGREGATED_FROM_LOCALITIES',
    score:
      inputs.reduce((total, item) => total + item.input_score, 0) / inputs.length,
    normalized_weight: 0.375,
    contribution: 3.1,
    score_id: `score:${criterionValue.id}:country:C0${countryIndex}`,
    derived_evidence_id: `derived:${criterionValue.id}:country:C0${countryIndex}`,
    aggregation_policy: {
      policy_id: `top-two:${criterionValue.id}`,
      policy_version: '1.0',
      method: 'TOP_N_MEAN',
      n: 2,
    },
    locality_universe: {
      locality_universe_id: 'major-cities-v1',
      locality_universe_version: '1.0',
    },
    contributing_localities: inputs,
    observations: inputs.map((item) =>
      observation(criterionValue.id, item.locality.entity_id, item.input_score),
    ),
    source_lineage_ids: ['lineage:public', 'lineage:cities'],
    sources: [
      source,
      {
        ...source,
        source_id: 'city-universe',
        role: 'ENTITY_UNIVERSE',
        publisher: 'Independent City Registry',
      },
    ],
    scoring_method_version: criterionValue.scoring_method_version,
    observation_method_versions: ['observation-v1'],
    quality_flags: [],
  }
}

type LocalityStatus = RankedCountryV2['assessments']['locality']['status']

const countryOpportunityAssessment: RankedCountryV2['assessments']['opportunity'] = {
  evaluated: false,
  passes: null,
  filter_evidence: [],
}

const opportunityAssessment: RankingV2['assessments']['opportunity'] = {
  status: 'NO_FILTERS_ACTIVE',
  mode: 'ALL_REQUIRED',
  active_filter_ids: [],
  input_ranked_country_count: 5,
  passing_country_count: 5,
  excluded_country_count: 0,
  excluded_counts_by_state: {
    STRONG_SIGNAL_NOT_ESTABLISHED: 0,
    INSUFFICIENT_EVIDENCE: 0,
  },
  per_filter: [],
  excluded_countries: [],
  opportunity_release_id: null,
  evidence_policy_version: null,
  source_bundle_version: null,
  strict_filter_explanation:
    'No Opportunity Filters were selected; canonical ranking is unchanged.',
  no_score_impact: true,
}

const countryLocalityAssessment = (
  countryIndex: number,
  status: LocalityStatus,
) => {
  const localityIds = [
    `city:C0${countryIndex}:a`,
    `city:C0${countryIndex}:b`,
  ]
  return {
    status,
    eligible_locality_entity_ids: localityIds,
    valid_locality_entity_ids: localityIds,
    contributing_locality_entity_ids: localityIds,
    common_locality_entity_ids:
      status === 'COMMON_LOCALITY_AVAILABLE' ? [localityIds[0]] : [],
    best_common_locality_entity_id:
      status === 'COMMON_LOCALITY_AVAILABLE' ? localityIds[0] : null,
    criterion_evidence: [
      {
        criterion_id: 'heat',
        eligible_locality_entity_ids: localityIds,
        valid_locality_entity_ids: localityIds,
        contributing_locality_entity_ids: localityIds,
      },
    ],
    reasons: [
      {
        code:
          status === 'NO_COMMON_LOCALITY'
            ? 'NO_COMMON_VALID_LOCALITY'
            : status,
        severity:
          status === 'NO_COMMON_LOCALITY' ? ('WARNING' as const) : ('INFO' as const),
        effect:
          status === 'NO_COMMON_LOCALITY' ? ('ADVISORY' as const) : ('NONE' as const),
      },
    ],
  }
}

const rankedCountry = (
  index: number,
  localityStatus: LocalityStatus = 'COMMON_LOCALITY_AVAILABLE',
): RankedCountryV2 => ({
  rank: index + 1,
  base_rank: index + 1,
  country: countries[index],
  total_score: 8.5 - index * 0.4,
  contributions: [
    directContribution(airCriterion, index, 8.7 - index * 0.4),
    localityContribution(index),
  ],
  assessments: {
    locality: countryLocalityAssessment(index, localityStatus),
    profile: profileAssessment,
    opportunity: countryOpportunityAssessment,
  },
})

export const rankedCountries = Array.from({ length: 5 }, (_, index) =>
  rankedCountry(index),
)

const responseLocalityAssessment = (
  status: LocalityStatus,
): RankingV2['assessments']['locality'] => ({
  status,
  policy_version: 'locality-policy-v1',
  contributing_criterion_ids:
    status === 'NO_ACTIVE_LOCALITY_CRITERIA' ? [] : ['heat'],
  analysis_triggered_criterion_ids:
    status === 'NO_ACTIVE_LOCALITY_CRITERIA' ||
    status === 'BELOW_ANALYSIS_THRESHOLD'
      ? []
      : ['heat'],
  below_threshold_criterion_ids:
    status === 'BELOW_ANALYSIS_THRESHOLD' ? ['heat'] : [],
  analysis_thresholds:
    status === 'NO_ACTIVE_LOCALITY_CRITERIA' ? {} : { heat: 0.6 },
  aggregation_policy_ids:
    status === 'NO_ACTIVE_LOCALITY_CRITERIA' ? [] : ['top-two:heat'],
  reasons: [
    {
      code: status,
      severity:
        status === 'NO_COMMON_LOCALITY' ||
        status === 'PARTIAL_OVERLAP' ||
        status === 'INSUFFICIENT_LOCALITY_EVIDENCE' ||
        status === 'MIXED_COUNTRY_RESULTS'
          ? ('WARNING' as const)
          : ('INFO' as const),
      effect:
        status === 'NO_ACTIVE_LOCALITY_CRITERIA'
          ? ('NONE' as const)
          : ('ADVISORY' as const),
    },
  ],
})

const coverageAssessment = {
  status: 'FULL_COVERAGE' as const,
  policy_version: 'coverage-policy-v1',
  active_global_core_criterion_ids: ['air', 'heat'],
  active_conditional_criterion_ids: [],
  excluded_countries: [],
  reasons: [
    {
      code: 'FULL_COVERAGE',
      severity: 'INFO' as const,
      effect: 'NONE' as const,
    },
  ],
}

export const rankingFixture: RankingV2 = {
  ...versionFields,
  resolved_preference_preset_id: 'balanced',
  normalized_weights: { air: 0.625, heat: 0.375 },
  assessments: {
    coverage: coverageAssessment,
    locality: responseLocalityAssessment('COMMON_LOCALITY_AVAILABLE'),
    profile: profileAssessment,
    opportunity: opportunityAssessment,
  },
  rankings: rankedCountries,
}

export function rankingForLocalityStatus(status: LocalityStatus): RankingV2 {
  const countryStatus =
    status === 'MIXED_COUNTRY_RESULTS' ? 'NO_COMMON_LOCALITY' : status
  return {
    ...rankingFixture,
    assessments: {
      ...rankingFixture.assessments,
      locality: responseLocalityAssessment(status),
    },
    rankings: rankedCountries.map((country, index) => ({
      ...country,
      contributions:
        status === 'NO_ACTIVE_LOCALITY_CRITERIA'
          ? [country.contributions[0]]
          : country.contributions,
      assessments: {
        ...country.assessments,
        locality:
          status === 'NO_ACTIVE_LOCALITY_CRITERIA'
            ? {
                ...countryLocalityAssessment(
                  index,
                  'NO_ACTIVE_LOCALITY_CRITERIA',
                ),
                eligible_locality_entity_ids: [],
                valid_locality_entity_ids: [],
                contributing_locality_entity_ids: [],
                criterion_evidence: [],
              }
            : countryLocalityAssessment(index, countryStatus),
      },
    })),
  }
}

const unavailableEvidence = {
  criterion_id: 'jobs',
  outcome: 'missing' as const,
  active_for_ranking: true,
  reason_codes: ['SOURCE_VALUE_MISSING'],
  source_lineage_ids: ['lineage:public'],
  observation_id: null,
  score_id: null,
  contribution: null,
}

export const coverageWarningRanking: RankingV2 = {
  ...rankingForLocalityStatus('NO_COMMON_LOCALITY'),
  normalized_weights: { air: 0.4, heat: 0.3, jobs: 0.3 },
  assessments: {
    ...rankingFixture.assessments,
    coverage: {
      status: 'PARTIAL_COMPLETE_CASE',
      policy_version: 'coverage-policy-v1',
      active_global_core_criterion_ids: ['air', 'heat'],
      active_conditional_criterion_ids: ['jobs'],
      excluded_countries: [
        {
          country: countries[4],
          final_aggregate: null,
          criterion_evidence: [
            {
              criterion_id: 'air',
              outcome: 'valid',
              active_for_ranking: true,
              reason_codes: [],
              source_lineage_ids: ['lineage:public'],
              observation_id: 'obs:air:country:C04',
              score_id: 'score:air:country:C04',
              contribution: directContribution(airCriterion, 4, 6.9),
            },
            unavailableEvidence,
          ],
          locality_assessment: countryLocalityAssessment(
            4,
            'NO_COMMON_LOCALITY',
          ),
          reasons: [
            {
              code: 'COUNTRY_EXCLUDED:C04',
              severity: 'WARNING',
              effect: 'COUNTRY_EXCLUDED',
            },
          ],
        },
      ],
      reasons: [
        {
          code: 'COUNTRY_EXCLUDED:C04',
          severity: 'WARNING',
          effect: 'COUNTRY_EXCLUDED',
        },
      ],
    },
    locality: responseLocalityAssessment('NO_COMMON_LOCALITY'),
    profile: profileAssessment,
  },
  rankings: rankedCountries.slice(0, 4).map((country, index) => ({
    ...country,
    assessments: {
      ...country.assessments,
      locality: countryLocalityAssessment(index, 'NO_COMMON_LOCALITY'),
    },
  })),
}

export const comparisonFixture: ComparisonV2 = {
  ...versionFields,
  resolved_preference_preset_id: 'balanced',
  normalized_weights: { air: 0.625, heat: 0.375 },
  assessments: rankingFixture.assessments,
  requested_country_entity_ids: countries
    .slice(0, 4)
    .map((country) => country.entity_id),
  countries: rankedCountries.slice(0, 4).map((country) => ({
    country: country.country,
    rank: country.rank,
    base_rank: country.base_rank,
    final_aggregate: country.total_score,
    coverage_excluded: false,
    opportunity_excluded: false,
    assessments: country.assessments,
  })),
  criterion_rows: [airCriterion, heatCriterion].map((criterionValue) => ({
    criterion_id: criterionValue.id,
    criterion_name: criterionValue.display_name,
    coverage: criterionValue.coverage,
    scope: criterionValue.scope,
    cells: rankedCountries.slice(0, 4).map((country) => {
      const contribution = country.contributions.find(
        (item) => item.criterion_id === criterionValue.id,
      )!
      return {
        criterion_id: criterionValue.id,
        outcome: 'valid' as const,
        active_for_ranking: true,
        reason_codes: [],
        source_lineage_ids: contribution.source_lineage_ids,
        observation_id: contribution.observations[0].observation_id,
        score_id: contribution.score_id,
        contribution,
        country: country.country,
      }
    }),
  })),
}

export const comparisonWithUnavailableFixture: ComparisonV2 = {
  ...comparisonFixture,
  assessments: coverageWarningRanking.assessments,
  countries: [
    ...comparisonFixture.countries.slice(0, 3),
    {
      country: countries[4],
      rank: null,
      base_rank: null,
      final_aggregate: null,
      coverage_excluded: true,
      opportunity_excluded: false,
      assessments: {
        locality: countryLocalityAssessment(4, 'NO_COMMON_LOCALITY'),
        profile: profileAssessment,
        opportunity: countryOpportunityAssessment,
      },
    },
  ],
  requested_country_entity_ids: [
    ...countries.slice(0, 3).map((country) => country.entity_id),
    countries[4].entity_id,
  ],
  criterion_rows: [
    ...comparisonFixture.criterion_rows,
    {
      criterion_id: jobsCriterion.id,
      criterion_name: jobsCriterion.display_name,
      coverage: jobsCriterion.coverage,
      scope: jobsCriterion.scope,
      cells: [
        ...rankedCountries.slice(0, 3).map((country, index) => {
          const contribution = directContribution(
            jobsCriterion,
            index,
            7.5 - index * 0.2,
          )
          return {
            criterion_id: jobsCriterion.id,
            outcome: 'valid' as const,
            active_for_ranking: true,
            reason_codes: [],
            source_lineage_ids: contribution.source_lineage_ids,
            observation_id: contribution.observations[0].observation_id,
            score_id: contribution.score_id,
            contribution,
            country: country.country,
          }
        }),
        { ...unavailableEvidence, country: countries[4] },
      ],
    },
  ],
}

export function countryDetailsFixture(
  countryIndex = 0,
  excluded = false,
): CountryDetailsV2 {
  const ranking = excluded ? coverageWarningRanking : rankingFixture
  const country = countries[countryIndex]
  const ranked = rankedCountries[countryIndex]
  const contributions = new Map(
    ranked.contributions.map((item) => [item.criterion_id, item]),
  )
  const criteria: CountryDetailsV2['criteria'] = [
    airCriterion,
    heatCriterion,
  ].map((criterionValue) => {
    const contribution = contributions.get(criterionValue.id)!
    return {
      criterion: criterionValue,
      evidence: {
        criterion_id: criterionValue.id,
        outcome: 'valid' as const,
        active_for_ranking: true,
        reason_codes: [],
        source_lineage_ids: contribution.source_lineage_ids,
        observation_id: contribution.observations[0].observation_id,
        score_id: contribution.score_id,
        contribution,
      },
    }
  })
  if (excluded) {
    criteria.push({
      criterion: jobsCriterion,
      evidence: unavailableEvidence,
    })
  }
  return {
    ...versionFields,
    resolved_preference_preset_id: 'balanced',
    normalized_weights: ranking.normalized_weights,
    assessments: ranking.assessments,
    country,
    criteria,
    opportunity_filters: [],
  }
}
