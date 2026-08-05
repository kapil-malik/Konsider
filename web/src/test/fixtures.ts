import type {
  CatalogCriterionV2,
  CatalogV2,
  ComparisonV2,
  ContributionV2,
  CountryDetailsV2,
  OpportunityFilterCatalogV2,
  OpportunityFilterEvidenceV2,
  RankedCountryV2,
  RankingV2,
  TfcAssessmentV2,
  TfcCatalogV2,
  TfcCountryAssessmentV2,
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

const opportunityDefinition = (
  id: string,
  displayName: string,
  compactLabel: string,
  category: 'CAREER' | 'EDUCATION',
  meaning: string,
  limitations: string[] = [],
): OpportunityFilterCatalogV2['definitions'][number] => ({
  id,
  display_name: displayName,
  compact_label: compactLabel,
  category,
  meaning,
  limitations,
  documentation_ref:
    category === 'CAREER'
      ? 'docs/data/career-opportunity-evidence.md'
      : 'docs/data/education-opportunity-evidence.md',
  coverage: {
    assessable_count: 4,
    state_counts: {
      VERIFIED_STRONG_SIGNAL: 2,
      STRONG_SIGNAL_NOT_ESTABLISHED: 2,
      INSUFFICIENT_EVIDENCE: 1,
    },
    source_dependency_status: 'AVAILABLE',
  },
  source_vintage: [
    {
      source_id: category === 'CAREER' ? 'ilo-source' : 'cwts-source',
      source_version: '2025-v1',
      publisher: category === 'CAREER' ? 'International Labour Organization' : 'CWTS Leiden Ranking',
      attribution: 'Source data transformed by Konsider.',
    },
  ],
  active: true,
  availability: 'AVAILABLE',
  mode: 'ALL_SELECTED_REQUIRED',
  eligibility_state: 'VERIFIED_STRONG_SIGNAL',
  no_score_impact: true,
})

export const opportunityCatalogFixture: OpportunityFilterCatalogV2 = {
  ...versionFields,
  opportunity_release_id: 'phase6g-api-test.1',
  state_contract_version: 'opportunity-filter-state-1.0',
  evidence_policy_version: 'opportunity-filter-evidence-policy-1.1',
  source_bundle_version: 'opportunity-source-test.1',
  mode: 'ALL_REQUIRED',
  no_score_impact: true,
  definitions: [
    opportunityDefinition(
      'technology_software_opportunity',
      'Technology and software employment ecosystem',
      'Technology and software',
      'CAREER',
      'A substantial and established technology/software employment ecosystem.',
    ),
    opportunityDefinition(
      'science_engineering_opportunity',
      'Science and engineering employment ecosystem',
      'Science and engineering',
      'CAREER',
      'A substantial science and engineering employment ecosystem.',
    ),
    opportunityDefinition(
      'health_social_work_opportunity',
      'Care-sector employment ecosystem',
      'Care sector',
      'CAREER',
      'A substantial human health and social-work employment ecosystem.',
      ['Covers human health and social work; it is not doctor-only evidence.'],
    ),
    opportunityDefinition(
      'finance_insurance_opportunity',
      'Finance and insurance employment ecosystem',
      'Finance and insurance',
      'CAREER',
      'A substantial finance and insurance activity employment ecosystem.',
      ['Does not describe all business or administration careers.'],
    ),
    opportunityDefinition(
      'skilled_trades_construction_opportunity',
      'Skilled-trades or construction employment ecosystem',
      'Skilled trades or construction',
      'CAREER',
      'A strong skilled-trades route, construction route, or both.',
    ),
    opportunityDefinition(
      'engineering_technology_education_opportunity',
      'Physical sciences and engineering research-university ecosystem',
      'Physical sciences and engineering',
      'EDUCATION',
      'A research-intensive university ecosystem in physical sciences and engineering.',
    ),
    opportunityDefinition(
      'computer_science_ict_education_opportunity',
      'Mathematics and computer science research-university ecosystem',
      'Mathematics and computer science',
      'EDUCATION',
      'A research-intensive university ecosystem in mathematics and computer science.',
    ),
    opportunityDefinition(
      'medicine_health_sciences_education_opportunity',
      'Biomedical and health sciences research-university ecosystem',
      'Biomedical and health sciences',
      'EDUCATION',
      'A research-intensive university ecosystem in biomedical and health sciences.',
    ),
    opportunityDefinition(
      'natural_sciences_education_opportunity',
      'Life and earth sciences research-university ecosystem',
      'Life and earth sciences',
      'EDUCATION',
      'A research-intensive university ecosystem in life and earth sciences.',
    ),
  ],
}

export const opportunityEvidence = (
  filterId: string,
  state: OpportunityFilterEvidenceV2['state'] = 'VERIFIED_STRONG_SIGNAL',
  routes: string[] = ['observed_technology'],
): OpportunityFilterEvidenceV2 => ({
  filter_id: filterId,
  state,
  passes: state === 'VERIFIED_STRONG_SIGNAL',
  confidence_band: state === 'INSUFFICIENT_EVIDENCE' ? 'LOW' : 'HIGH',
  establishing_route_ids: state === 'VERIFIED_STRONG_SIGNAL' ? routes : [],
  reason_codes:
    state === 'VERIFIED_STRONG_SIGNAL'
      ? ['APPROVED_STRONG_ROUTE_PASSED']
      : state === 'STRONG_SIGNAL_NOT_ESTABLISHED'
        ? ['NO_APPROVED_STRONG_ROUTE_PASSED']
        : ['COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE'],
  reference_period: state === 'INSUFFICIENT_EVIDENCE' ? null : '2025',
  source_ids: state === 'INSUFFICIENT_EVIDENCE' ? [] : ['ilo-source'],
  limitations: ['Destination-side ecosystem evidence only.'],
  documentation_ref: 'docs/data/career-opportunity-evidence.md',
})

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

export function rankingWithOpportunityFilters(
  filterIds = [
    'technology_software_opportunity',
    'skilled_trades_construction_opportunity',
  ],
  empty = false,
): RankingV2 {
  const evidenceFor = (filterId: string) =>
    opportunityEvidence(
      filterId,
      'VERIFIED_STRONG_SIGNAL',
      filterId === 'skilled_trades_construction_opportunity'
        ? ['skilled_trades', 'construction']
        : ['observed_technology'],
    )
  const passingCountries = empty
    ? []
    : rankedCountries.slice(0, 2).map((country, index) => ({
        ...country,
        rank: index + 1,
        assessments: {
          ...country.assessments,
          opportunity: {
            evaluated: true,
            passes: true,
            filter_evidence: filterIds.map(evidenceFor),
          },
        },
      }))
  const excluded = [
    {
      country_code: 'C02',
      base_rank: 3,
      exclusion_category: 'STRONG_SIGNAL_NOT_ESTABLISHED' as const,
      failing_filter_evidence: [
        opportunityEvidence(filterIds[0], 'STRONG_SIGNAL_NOT_ESTABLISHED'),
      ],
    },
    {
      country_code: 'C03',
      base_rank: 4,
      exclusion_category: 'INSUFFICIENT_EVIDENCE' as const,
      failing_filter_evidence: [
        opportunityEvidence(filterIds.at(-1)!, 'INSUFFICIENT_EVIDENCE'),
      ],
    },
    {
      country_code: 'C04',
      base_rank: 5,
      exclusion_category: 'STRONG_SIGNAL_NOT_ESTABLISHED' as const,
      failing_filter_evidence: [
        opportunityEvidence(filterIds[0], 'STRONG_SIGNAL_NOT_ESTABLISHED'),
      ],
    },
  ]
  if (empty) {
    excluded.unshift(
      {
        country_code: 'C00',
        base_rank: 1,
        exclusion_category: 'STRONG_SIGNAL_NOT_ESTABLISHED' as const,
        failing_filter_evidence: [
          opportunityEvidence(filterIds[0], 'STRONG_SIGNAL_NOT_ESTABLISHED'),
        ],
      },
      {
        country_code: 'C01',
        base_rank: 2,
        exclusion_category: 'INSUFFICIENT_EVIDENCE' as const,
        failing_filter_evidence: [
          opportunityEvidence(filterIds.at(-1)!, 'INSUFFICIENT_EVIDENCE'),
        ],
      },
    )
  }
  return {
    ...rankingFixture,
    assessments: {
      ...rankingFixture.assessments,
      opportunity: {
        status: empty ? 'NO_COUNTRIES_MATCH' : 'FILTERS_APPLIED',
        mode: 'ALL_REQUIRED',
        active_filter_ids: [...filterIds].sort(),
        input_ranked_country_count: 5,
        passing_country_count: passingCountries.length,
        excluded_country_count: excluded.length,
        excluded_counts_by_state: {
          STRONG_SIGNAL_NOT_ESTABLISHED: empty ? 3 : 2,
          INSUFFICIENT_EVIDENCE: empty ? 2 : 1,
        },
        per_filter: filterIds.map((filterId) => ({
          filter_id: filterId,
          input_country_count: 5,
          passing_country_count: empty ? 0 : 2,
          state_counts: {
            VERIFIED_STRONG_SIGNAL: empty ? 0 : 2,
            STRONG_SIGNAL_NOT_ESTABLISHED: empty ? 3 : 2,
            INSUFFICIENT_EVIDENCE: empty ? 2 : 1,
          },
        })),
        excluded_countries: excluded,
        opportunity_release_id: 'phase6g-api-test.1',
        evidence_policy_version: 'opportunity-filter-evidence-policy-1.1',
        source_bundle_version: 'opportunity-source-test.1',
        strict_filter_explanation:
          'Every selected opportunity filter requires a verified strong signal.',
        no_score_impact: true,
      },
    },
    rankings: passingCountries,
  }
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

export const comparisonWithOpportunityFixture: ComparisonV2 = (() => {
  const ranking = rankingWithOpportunityFilters([
    'skilled_trades_construction_opportunity',
  ])
  const verified = opportunityEvidence(
    'skilled_trades_construction_opportunity',
    'VERIFIED_STRONG_SIGNAL',
    ['skilled_trades', 'construction'],
  )
  const notEstablished = opportunityEvidence(
    'skilled_trades_construction_opportunity',
    'STRONG_SIGNAL_NOT_ESTABLISHED',
  )
  return {
    ...comparisonFixture,
    assessments: ranking.assessments,
    countries: comparisonFixture.countries.slice(0, 3).map((country, index) => ({
      ...country,
      rank: index === 2 ? null : country.rank,
      opportunity_excluded: index === 2,
      assessments: {
        ...country.assessments,
        opportunity: {
          evaluated: true,
          passes: index !== 2,
          filter_evidence: [index === 2 ? notEstablished : verified],
        },
      },
    })),
    requested_country_entity_ids: comparisonFixture.requested_country_entity_ids.slice(0, 3),
    criterion_rows: comparisonFixture.criterion_rows.map((row) => ({
      ...row,
      cells: row.cells.slice(0, 3),
    })),
  }
})()

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

const firstWaveDefinitions: TfcCatalogV2['definitions'] = [
  {
    id: 'skilled_work_route_feasibility',
    display_name: 'Highly qualified work route check',
    original_criterion_ids: ['C32'],
    user_question: 'Which supported highly qualified work route appears to match this snapshot?',
    check_kind: 'RULE_ROUTE_MATCH',
    supported_profile_boundary: 'Declared occupation, qualification, offer, destination and date.',
    supported_destination_codes: ['C00', 'C01'],
    input_requirements: [
      ['applicant.occupation', 'ALWAYS_REQUIRED'],
      ['applicant.qualifications', 'ALWAYS_REQUIRED'],
      ['scenario.job_offer', 'ALWAYS_REQUIRED'],
      ['scenario.target_country_codes', 'ALWAYS_REQUIRED'],
      ['scenario.target_date', 'ALWAYS_REQUIRED'],
    ].map(([field_id, requirement]) => ({
      field_id,
      requirement: requirement as 'ALWAYS_REQUIRED',
      when_field_id: null,
      when_equals: null,
    })),
    limitations: ['A route match is a bounded source-based screening result, not legal advice.'],
    filter_capability: 'ASSESS_ONLY',
    applicable_purposes: ['WORK', 'EXPLORATION'],
    refresh_cadence: 'Quarterly',
    policy_id: 'work.v1',
    policy_version: '1.0',
    source_summary: [
      {
        source_id: 'fictional-work-source',
        publisher: 'Fictional Immigration Authority',
        verified_at: '2026-08-05',
        effective_from: '2026-08-05',
        effective_to: null,
        attribution: 'Fictional test source.',
      },
    ],
    effective_from: '2026-08-05',
    stale_after: '2026-11-05',
    sort_order: 10,
    no_score_impact: true,
  },
  {
    id: 'family_accompaniment_reunification',
    display_name: 'Dependants on supported work and study routes',
    original_criterion_ids: ['C36'],
    user_question: 'Do declared family roles fit a supported primary route?',
    check_kind: 'RULE_ROUTE_MATCH',
    supported_profile_boundary: 'Declared household attached to a supported primary route.',
    supported_destination_codes: ['C00', 'C01'],
    input_requirements: [
      'household.dependants',
      'household.partner_status',
      'scenario.primary_route_id',
      'scenario.target_country_codes',
      'scenario.target_date',
    ].map((field_id) => ({
      field_id,
      requirement: 'ALWAYS_REQUIRED' as const,
      when_field_id: null,
      when_equals: null,
    })),
    limitations: ['This is not a general family-reunification check.'],
    filter_capability: 'ASSESS_ONLY',
    applicable_purposes: ['WORK', 'STUDY', 'FAMILY', 'EXPLORATION'],
    refresh_cadence: 'Quarterly',
    policy_id: 'family.v1',
    policy_version: '1.0',
    source_summary: [],
    effective_from: '2026-08-05',
    stale_after: '2026-11-05',
    sort_order: 20,
    no_score_impact: true,
  },
  {
    id: 'post_study_work_pathway',
    display_name: 'Post-study stay and work route check',
    original_criterion_ids: ['C35'],
    user_question: 'Does this study scenario fit a supported post-study route?',
    check_kind: 'RULE_ROUTE_MATCH',
    supported_profile_boundary: 'Declared institution, study and completion scenario.',
    supported_destination_codes: ['C00', 'C01'],
    input_requirements: [
      'scenario.intended_study',
      'scenario.target_country_codes',
      'scenario.target_date',
    ].map((field_id) => ({
      field_id,
      requirement: 'ALWAYS_REQUIRED' as const,
      when_field_id: null,
      when_equals: null,
    })),
    limitations: ['Planned completion remains provisional.'],
    filter_capability: 'ASSESS_ONLY',
    applicable_purposes: ['STUDY', 'EXPLORATION'],
    refresh_cadence: 'Quarterly',
    policy_id: 'study.v1',
    policy_version: '1.0',
    source_summary: [],
    effective_from: '2026-08-05',
    stale_after: '2026-11-05',
    sort_order: 30,
    no_score_impact: true,
  },
]

const registryField = (
  field_id: string,
  prompt: string,
  sensitivity: TfcCatalogV2['field_registry'][number]['sensitivity'] = 'MODERATE_CONSEQUENTIAL',
) => ({
  field_id,
  data_type: 'string',
  validation: 'Fictional test validation.',
  sensitivity,
  default_retention: 'NEVER_RETAIN_BY_DEFAULT' as const,
  consumer_tfc_ids: firstWaveDefinitions
    .filter((definition) =>
      definition.input_requirements.some((item) => item.field_id === field_id),
    )
    .map((definition) => definition.id),
  prompt,
  help_text: `Why we ask for ${prompt.toLocaleLowerCase()}.`,
  may_be_omitted: true,
  may_be_stored_locally: true,
})

export const tfcCatalogFixture: TfcCatalogV2 = {
  ...versionFields,
  tfc_release_id: 'phase7f-test.1',
  tfc_release_schema_version: 'konsider-release-6.0',
  candidate_status: 'draft',
  activation_authorized: false,
  available_modes: ['ASSESS_ONLY', 'REQUIRE_SUPPORTED_MATCH'],
  default_mode: 'ASSESS_ONLY',
  selection_is_explicit: true,
  persisted_server_side: false,
  no_score_impact: true,
  definitions: firstWaveDefinitions,
  field_registry: [
    registryField('applicant.citizenships', 'Citizenship(s)', 'HIGH_PERSONAL'),
    registryField('applicant.occupation', 'Current occupation'),
    registryField('applicant.qualifications', 'Qualifications', 'HIGH_CONSEQUENTIAL'),
    registryField('household.dependants', 'Dependants', 'HIGH_PERSONAL'),
    registryField('household.partner_status', 'Partner status', 'HIGH_PERSONAL'),
    registryField('scenario.job_offer', 'Job offer', 'HIGH_CONSEQUENTIAL'),
    registryField('scenario.intended_study', 'Intended study', 'HIGH_CONSEQUENTIAL'),
    registryField('scenario.primary_route_id', 'Primary route'),
    registryField('scenario.target_country_codes', 'Target destinations', 'LOW'),
    registryField('scenario.target_date', 'Target date', 'LOW'),
  ],
}

const tfcCountryAssessment = (
  index: number,
  status: 'EVALUATED' | 'INPUT_REQUIRED' | 'UNSUPPORTED' =
    index === 0 ? 'EVALUATED' : index === 1 ? 'INPUT_REQUIRED' : 'UNSUPPORTED',
): TfcCountryAssessmentV2 => ({
  country_code: `C0${index}`,
  base_rank: index + 1,
  filtered_rank: null,
  affinity_score_before: 8.5 - index * 0.4,
  affinity_score_after: 8.5 - index * 0.4,
  no_change_affinity: true,
  outcomes: [
    {
      tfc_id: 'skilled_work_route_feasibility',
      country_code: `C0${index}`,
      common_status: status,
      reason_codes:
        status === 'EVALUATED'
          ? ['ROUTE_CONDITIONALLY_MATCHED']
          : status === 'INPUT_REQUIRED'
            ? ['PROFILE_FIELDS_MISSING']
            : ['DESTINATION_NOT_SUPPORTED'],
      input_required_fields: status === 'INPUT_REQUIRED' ? ['scenario.job_offer'] : [],
      result:
        status === 'EVALUATED'
          ? {
              result_type: 'ROUTE_RULE',
              match_classification: 'CONDITIONAL_ROUTE_MATCH',
              routes: [
                {
                  route_id: 'FX.WORK.1',
                  route_name: 'Fictional skilled work route',
                  jurisdiction_id: `country:C0${index}`,
                  classification: 'CONDITIONAL',
                  conditions: [
                    {
                      condition_id: 'external_authority_confirmation',
                      field_ids: [],
                      status: 'UNKNOWN',
                      blocking: true,
                    },
                  ],
                  source_ids: ['fictional-work-source'],
                  effective_from: '2026-08-05',
                  effective_to: null,
                  evidence_quality: 'MEDIUM',
                },
              ],
              matched_route_ids: ['FX.WORK.1'],
              route_inventory_complete: false,
              legal_impossibility_disclaimer:
                'No supported-route match is not a permanent legal impossibility.',
            }
          : null,
      warnings: [],
    },
  ],
})

const tfcAssessment: TfcAssessmentV2 = {
  schema_version: 'tfc-engine-assessment-1.0',
  profile_context_status: 'PARTIAL_PROFILE_CONTEXT',
  execution_status: 'EXECUTED',
  filter_mode: 'ASSESS_ONLY',
  selected_tfc_ids: ['skilled_work_route_feasibility'],
  input_required_fields: ['scenario.job_offer'],
  status_counts: {
    EVALUATED: 1,
    INPUT_REQUIRED: 1,
    DESTINATION_EVIDENCE_INSUFFICIENT: 0,
    UNSUPPORTED: 3,
    NOT_APPLICABLE: 0,
    EVALUATION_ERROR: 0,
  },
  matched_route_count: 0,
  metric_result_count: 0,
  no_change_affinity: true,
  warnings: [],
  countries: Array.from({ length: 5 }, (_, index) => tfcCountryAssessment(index)),
  profile_context_summary: {
    provided_layers: ['applicant', 'household', 'scenario'],
    unknown_field_ids: ['scenario.job_offer'],
    returned_profile_values: false,
    persisted_server_side: false,
  },
  snapshot: {
    snapshot_id: 'snapshot:fictional:2026-08-05',
    tfc_release_id: 'phase7f-test.1',
    policy_versions: { skilled_work_route_feasibility: '1.0' },
    source_versions: { 'fictional-work-source': 'sha256:fictional' },
    effective_profile_context_hash: 'sha256:fictional-context',
    evaluation_date: '2026-08-05',
    base_ranking_reference: {
      release_id: 'test-release',
      country_count: 5,
      ordering_checksum: 'sha256:fictional-order',
    },
    persisted_server_side: false,
  },
}

export const rankingWithFeasibility: RankingV2 = {
  ...rankingFixture,
  assessments: { ...rankingFixture.assessments, feasibility: tfcAssessment },
  rankings: rankedCountries.map((country, index) => ({
    ...country,
    assessments: {
      ...country.assessments,
      feasibility: tfcCountryAssessment(index),
    },
  })),
}

export const comparisonWithFeasibilityFixture: ComparisonV2 = {
  ...comparisonFixture,
  assessments: { ...comparisonFixture.assessments, feasibility: tfcAssessment },
  countries: comparisonFixture.countries.map((country, index) => ({
    ...country,
    assessments: {
      ...country.assessments,
      feasibility: tfcCountryAssessment(index),
    },
  })),
}

export const rankingWithOpportunityAndFeasibility: RankingV2 = (() => {
  const opportunity = rankingWithOpportunityFilters([
    'skilled_trades_construction_opportunity',
  ])
  return {
    ...opportunity,
    assessments: { ...opportunity.assessments, feasibility: tfcAssessment },
    rankings: opportunity.rankings.map((country) => {
      const index = Number(country.country.country_codes[0]?.slice(-1))
      return {
        ...country,
        assessments: {
          ...country.assessments,
          feasibility: tfcCountryAssessment(index),
        },
      }
    }),
  }
})()

export const comparisonWithOpportunityAndFeasibilityFixture: ComparisonV2 = (() => {
  const opportunity = comparisonWithOpportunityFixture
  return {
    ...opportunity,
    assessments: { ...opportunity.assessments, feasibility: tfcAssessment },
    countries: opportunity.countries.map((country, index) => ({
      ...country,
      assessments: {
        ...country.assessments,
        feasibility:
          index === 2
            ? tfcCountryAssessment(index, 'EVALUATED')
            : tfcCountryAssessment(index),
      },
    })),
  }
})()

export function countryDetailsWithFeasibilityFixture(index = 0): CountryDetailsV2 {
  return {
    ...countryDetailsFixture(index),
    assessments: {
      ...countryDetailsFixture(index).assessments,
      feasibility: tfcAssessment,
    },
    feasibility: tfcCountryAssessment(index),
  }
}

export function countryDetailsWithOpportunityAndFeasibilityFixture(
  index = 0,
): CountryDetailsV2 {
  const evidence = [
    opportunityEvidence(
      'skilled_trades_construction_opportunity',
      index === 2 ? 'STRONG_SIGNAL_NOT_ESTABLISHED' : 'VERIFIED_STRONG_SIGNAL',
      index === 2 ? [] : ['skilled_trades', 'construction'],
    ),
  ]
  const base = countryDetailsWithOpportunityFixture(index, evidence)
  const feasibility =
    index === 2 ? tfcCountryAssessment(index, 'EVALUATED') : tfcCountryAssessment(index)
  return {
    ...base,
    assessments: { ...base.assessments, feasibility: tfcAssessment },
    feasibility,
  }
}

export function countryDetailsWithOpportunityFixture(
  countryIndex = 0,
  evidence: OpportunityFilterEvidenceV2[] = [
    opportunityEvidence(
      'skilled_trades_construction_opportunity',
      'VERIFIED_STRONG_SIGNAL',
      ['skilled_trades', 'construction'],
    ),
    {
      ...opportunityEvidence(
        'medicine_health_sciences_education_opportunity',
        'INSUFFICIENT_EVIDENCE',
      ),
      documentation_ref: 'docs/data/education-opportunity-evidence.md',
    },
    opportunityEvidence(
      'health_social_work_opportunity',
      'STRONG_SIGNAL_NOT_ESTABLISHED',
    ),
  ],
): CountryDetailsV2 {
  const base = countryDetailsFixture(countryIndex)
  const activeFilterIds = evidence.map((item) => item.filter_id).sort()
  return {
    ...base,
    assessments: {
      ...base.assessments,
      opportunity: {
        ...rankingWithOpportunityFilters(activeFilterIds).assessments.opportunity,
        passing_country_count: 0,
        excluded_country_count: 1,
      },
    },
    opportunity_filters: evidence,
  }
}
