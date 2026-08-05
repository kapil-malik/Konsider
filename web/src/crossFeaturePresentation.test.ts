import { describe, expect, test } from 'vitest'

import type { TfcCountryAssessmentV2 } from './api/types'
import {
  CROSS_FEATURE_TEMPLATES,
  crossFeatureExplanations,
} from './crossFeaturePresentation'
import { comparisonWithOpportunityAndFeasibilityFixture } from './test/fixtures'

const compared = comparisonWithOpportunityAndFeasibilityFixture.countries
const matchedAssessment = compared[2].assessments.feasibility!
const verifiedEvidence = compared[0].assessments.opportunity.filter_evidence
const insufficientEvidence = compared[2].assessments.opportunity.filter_evidence

const explain = (
  assessment: TfcCountryAssessmentV2,
  opportunityEvidence = insufficientEvidence,
  localityStatus:
    | 'COMMON_LOCALITY_AVAILABLE'
    | 'NO_COMMON_LOCALITY' = 'COMMON_LOCALITY_AVAILABLE',
  finalAggregate: number | null = 7.7,
) =>
  crossFeatureExplanations({
    assessment,
    opportunityEvidence,
    localityStatus,
    finalAggregate,
  })

describe('cross-feature explanation policy', () => {
  test('explains a supported route without a broad ecosystem signal', () => {
    expect(explain(matchedAssessment)).toContain(
      CROSS_FEATURE_TEMPLATES.accessWithoutEcosystem,
    )
  })

  test('explains strong ecosystem evidence without a supported route', () => {
    const assessment = structuredClone(matchedAssessment)
    const result = assessment.outcomes[0].result
    if (!result || !('routes' in result)) throw new Error('Expected a route result fixture.')
    result.match_classification = 'NO_SUPPORTED_ROUTE_MATCH'
    result.matched_route_ids = []
    result.routes = []
    expect(explain(assessment, verifiedEvidence)).toContain(
      CROSS_FEATURE_TEMPLATES.ecosystemWithoutAccess,
    )
    expect(explain(assessment, [], 'COMMON_LOCALITY_AVAILABLE')).toContain(
      CROSS_FEATURE_TEMPLATES.attractiveWithoutAccess,
    )
  })

  test('keeps locality trade-offs separate from a route match', () => {
    expect(explain(matchedAssessment, verifiedEvidence, 'NO_COMMON_LOCALITY')).toContain(
      CROSS_FEATURE_TEMPLATES.accessWithLocalityTradeoff,
    )
  })

  test('distinguishes unavailable evidence from missing inputs', () => {
    const unavailable = structuredClone(matchedAssessment)
    unavailable.outcomes[0].common_status = 'DESTINATION_EVIDENCE_INSUFFICIENT'
    unavailable.outcomes[0].result = null
    const inputRequired = structuredClone(matchedAssessment)
    inputRequired.outcomes[0].common_status = 'INPUT_REQUIRED'
    inputRequired.outcomes[0].result = null
    inputRequired.outcomes[0].input_required_fields = ['scenario.job_offer']
    expect(explain(unavailable, [])).toContain(
      CROSS_FEATURE_TEMPLATES.evidenceUnavailable,
    )
    expect(explain(inputRequired, [])).toContain(
      CROSS_FEATURE_TEMPLATES.inputRequired,
    )
  })
})
