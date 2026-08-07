import type { components } from './schema'

export type ErrorEnvelope = components['schemas']['ErrorResponse']

export type CatalogV3 = components['schemas']['CatalogV3Response']
export type CatalogCriterionV3 = components['schemas']['CatalogCriterionV3Response']
export type CountryCoverageV2 = components['schemas']['CountryCoverageResponse']
export type PreferencePreset = components['schemas']['PreferencePresetResponse']
export type RankingRequestV3 = components['schemas']['V3RankingRequest']
export type WeightSelectionV3 = components['schemas']['V2WeightSelection']
export type RankingV3 = components['schemas']['RankingV3Response']
export type RankedCountryV3 = components['schemas']['RankedCountryV3Response']
export type ContributionV3 = components['schemas']['ContributionV3Response']
export type RankingContributionV3 = components['schemas']['CompactContributionV3Response']
export type ComparisonRequestV3 = components['schemas']['V2ComparisonRequest']
export type ComparisonV3 = components['schemas']['ComparisonV3Response']
export type CountryDetailsV3 = components['schemas']['CountryDetailsV3Response']
export type OpportunityFilterCatalogV3 =
  components['schemas']['OpportunityFilterCatalogV3Response']
export type OpportunityFilterDefinitionV3 =
  components['schemas']['OpportunityFilterDefinitionV3Response']
export type OpportunityFilterEvidenceV2 =
  components['schemas']['OpportunityFilterEvidenceSummaryResponse']
export type TfcCatalogV3 = components['schemas']['TfcCatalogV3Response']
export type TfcDefinitionV3 = components['schemas']['TfcDefinitionV3Response']
export type TfcFieldDefinitionV2 = components['schemas']['TfcFieldDefinitionV2Response']
export type TfcAssessmentSelectionV2 = components['schemas']['TfcAssessmentSelectionRequest']
export type TfcAssessmentV2 = components['schemas']['TfcAssessmentV2Response']
export type TfcCountryAssessmentV2 = components['schemas']['TfcCountryAssessmentV2Response']
export type TfcOutcomeV2 = components['schemas']['TfcOutcomeV2Response']

// Transitional source aliases while UI modules move to v3 names; all resolve to v3 responses.
export type CatalogV2 = CatalogV3
export type CatalogCriterionV2 = CatalogCriterionV3
export type RankingRequestV2 = RankingRequestV3
export type WeightSelectionV2 = WeightSelectionV3
export type RankingV2 = RankingV3
export type RankedCountryV2 = RankedCountryV3
export type ContributionV2 = ContributionV3
export type ComparisonRequestV2 = ComparisonRequestV3
export type ComparisonV2 = ComparisonV3
export type CountryDetailsV2 = CountryDetailsV3
export type OpportunityFilterCatalogV2 = OpportunityFilterCatalogV3
export type OpportunityFilterDefinitionV2 = OpportunityFilterDefinitionV3
export type TfcCatalogV2 = TfcCatalogV3
export type TfcDefinitionV2 = TfcDefinitionV3
