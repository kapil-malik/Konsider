import type {
  CatalogV2,
  ContributionV2,
  RankingContributionV3,
  RankingRequestV2,
  RankingV2,
} from './types'

// Compile-time assertions against generated konsider-api-types-3.0.
const validRequest: RankingRequestV2 = { preference_preset_id: 'balanced' }
void validRequest

// @ts-expect-error API v2 rejects the legacy Phase 4 request alias.
const legacyRequest: RankingRequestV2 = { profile_id: 'balanced' }
void legacyRequest

declare const ranking: RankingV2
void ranking.assessments.coverage.status
void ranking.assessments.locality.status
void ranking.assessments.profile.status
void ranking.assessments.opportunity.status
void ranking.rankings[0]?.base_rank

// @ts-expect-error API v2 has no duplicate root locality status.
void ranking.locality_status

declare const catalog: CatalogV2
void catalog.preference_presets

// @ts-expect-error API v2 reserves profile terminology for applicant context.
void catalog.profiles

declare const contribution: ContributionV2
void contribution.contributing_localities
void contribution.aggregation_policy
void contribution.displayName

declare const rankingContribution: RankingContributionV3
void rankingContribution.contributing_localities
// @ts-expect-error Compact ranking contributions omit the full evidence graph.
void rankingContribution.observations

// @ts-expect-error Locality provenance is structured, not a free-text city field.
void contribution.city
