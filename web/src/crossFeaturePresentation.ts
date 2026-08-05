import type {
  OpportunityFilterEvidenceV2,
  TfcCountryAssessmentV2,
} from './api/types'

type LocalityStatus =
  | 'NO_ACTIVE_LOCALITY_CRITERIA'
  | 'BELOW_ANALYSIS_THRESHOLD'
  | 'ONE_ACTIVE_LOCALITY_CRITERION'
  | 'COMMON_LOCALITY_AVAILABLE'
  | 'PARTIAL_OVERLAP'
  | 'NO_COMMON_LOCALITY'
  | 'INSUFFICIENT_LOCALITY_EVIDENCE'
  | 'MIXED_COUNTRY_RESULTS'

export const CROSS_FEATURE_TEMPLATES = {
  ecosystemWithoutAccess:
    'The selected opportunity ecosystem has a verified strong signal, but no supported route matched the current scenario.',
  accessWithoutEcosystem:
    'A supported route matched the current scenario, but the selected opportunity ecosystem signal was not established.',
  attractiveWithoutAccess:
    'This destination remains attractive under your priorities, but no supported route matched the current scenario.',
  accessWithLocalityTradeoff:
    'A supported route matched, while locality compatibility or housing trade-offs remain separate.',
  evidenceUnavailable:
    'Personal feasibility evidence is unavailable for this destination. Its country evidence and rank remain unchanged.',
  inputRequired:
    'More information is needed before personal feasibility can be assessed. The country evidence above remains unchanged.',
} as const

const routeClassifications = (assessment: TfcCountryAssessmentV2) =>
  assessment.outcomes.flatMap((outcome) => {
    const result = outcome.result
    return result && 'routes' in result ? [result.match_classification] : []
  })

const isLocalityTradeoff = (status: LocalityStatus) =>
  [
    'PARTIAL_OVERLAP',
    'NO_COMMON_LOCALITY',
    'INSUFFICIENT_LOCALITY_EVIDENCE',
    'MIXED_COUNTRY_RESULTS',
  ].includes(status)

export function crossFeatureExplanations({
  assessment,
  opportunityEvidence,
  localityStatus,
  finalAggregate,
}: {
  assessment: TfcCountryAssessmentV2
  opportunityEvidence: OpportunityFilterEvidenceV2[]
  localityStatus: LocalityStatus
  finalAggregate: number | null
}) {
  const classifications = routeClassifications(assessment)
  const hasMatch = classifications.some((value) =>
    ['SUPPORTED_ROUTE_MATCH', 'CONDITIONAL_ROUTE_MATCH'].includes(value),
  )
  const hasNoMatch = classifications.includes('NO_SUPPORTED_ROUTE_MATCH')
  const opportunityEvaluated = opportunityEvidence.length > 0
  const opportunityPasses =
    opportunityEvaluated &&
    opportunityEvidence.every((evidence) => evidence.state === 'VERIFIED_STRONG_SIGNAL')
  const explanations: string[] = []

  if (opportunityPasses && hasNoMatch) {
    explanations.push(CROSS_FEATURE_TEMPLATES.ecosystemWithoutAccess)
  } else if (opportunityEvaluated && !opportunityPasses && hasMatch) {
    explanations.push(CROSS_FEATURE_TEMPLATES.accessWithoutEcosystem)
  } else if (!opportunityEvaluated && finalAggregate !== null && hasNoMatch) {
    explanations.push(CROSS_FEATURE_TEMPLATES.attractiveWithoutAccess)
  }
  if (hasMatch && isLocalityTradeoff(localityStatus)) {
    explanations.push(CROSS_FEATURE_TEMPLATES.accessWithLocalityTradeoff)
  }
  if (
    assessment.outcomes.some((outcome) =>
      ['UNSUPPORTED', 'DESTINATION_EVIDENCE_INSUFFICIENT', 'EVALUATION_ERROR'].includes(
        outcome.common_status,
      ),
    )
  ) {
    explanations.push(CROSS_FEATURE_TEMPLATES.evidenceUnavailable)
  }
  if (assessment.outcomes.some((outcome) => outcome.common_status === 'INPUT_REQUIRED')) {
    explanations.push(CROSS_FEATURE_TEMPLATES.inputRequired)
  }
  return explanations
}
