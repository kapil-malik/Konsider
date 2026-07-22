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
  default_enabled: ready,
  experimental,
  scoring_method_version: `${id}_v1`,
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

export const catalogFixture: Catalog = {
  release_id: 'test-release',
  release_schema_version: 'test-release-schema',
  catalog_schema_version: 'test-catalog-schema',
  scoring_method_versions: ['air_v1', 'infrastructure_v1', 'health_v1'],
  countries: Array.from({ length: 5 }, (_, index) => ({
    code: `C0${index}`,
    display_name: `Country ${index + 1}`,
    region: `Region ${index + 1}`,
  })),
  criteria: [airCriterion, infrastructureCriterion, unavailableCriterion],
  profiles: [
    {
      id: 'equal_weight_mvp',
      name: 'Balanced',
      description: 'Equal test weights.',
      weights: { air: 1, infrastructure: 1 },
    },
    {
      id: 'safety_profile',
      name: 'Safety profile',
      description: 'A different server profile.',
      weights: { air: 0.4, infrastructure: 0.8 },
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
  contributions: [
    contribution(airCriterion, 9 - index * 0.5),
    contribution(infrastructureCriterion, 8 - index * 0.5),
  ],
  strengths: ['air'],
  tradeoffs: ['infrastructure'],
})

export const rankedCountries = Array.from({ length: 5 }, (_, index) => country(index))

export const rankingFixture: Ranking = {
  release_id: 'test-release',
  release_schema_version: 'test-release-schema',
  catalog_schema_version: 'test-catalog-schema',
  scoring_method_versions: ['air_v1', 'infrastructure_v1'],
  resolved_profile_id: 'equal_weight_mvp',
  normalized_weights: { air: 0.5, infrastructure: 0.5 },
  all_zero_behavior: 'equal_weights_across_all_enabled_criteria',
  country_tie_breaker: 'ascending_iso3_country_code',
  rounding_tolerance: 0.00000001,
  total_eligible_country_count: 5,
  returned_result_count: 5,
  rankings: rankedCountries,
}

export const comparisonFixture: Comparison = {
  ...rankingFixture,
  countries: rankedCountries.slice(0, 4),
  returned_result_count: 4,
}
delete (comparisonFixture as Partial<Ranking>).rankings

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
