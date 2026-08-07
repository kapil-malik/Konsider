import type {
  OpportunityFilterDefinitionV2,
  OpportunityFilterEvidenceV2,
} from './api/types'
import { compactDisplayName } from './displayName'

export type OpportunityState = OpportunityFilterEvidenceV2['state']

export const EDUCATION_SHARED_LIMITATION =
  'This evidence describes research-intensive university ecosystems. It does not establish teaching quality, programme availability, admission access, affordability, accreditation or applicant eligibility.'

export const OPPORTUNITY_STATE_CONTENT: Record<
  OpportunityState,
  { label: string; icon: string; className: string; explanation: string }
> = {
  VERIFIED_STRONG_SIGNAL: {
    label: 'Verified strong signal',
    icon: '✓',
    className: 'verified',
    explanation: 'The approved comparable evidence crossed a frozen strong-ecosystem route.',
  },
  STRONG_SIGNAL_NOT_ESTABLISHED: {
    label: 'Strong signal not established',
    icon: '○',
    className: 'not-established',
    explanation:
      'Comparable evidence was available, but it did not cross Konsider’s strong-ecosystem threshold. This does not mean that no opportunity exists.',
  },
  INSUFFICIENT_EVIDENCE: {
    label: 'Insufficient evidence',
    icon: '?',
    className: 'insufficient',
    explanation:
      'Konsider does not currently have enough comparable evidence to assess this opportunity for the country.',
  },
}

const ROUTE_LABELS: Record<string, string> = {
  skilled_trades: 'Skilled trades',
  construction: 'Construction',
  health_social_work: 'Human health and social work',
  finance_insurance: 'Finance and insurance activity',
  top_100_institution: 'Top-100 institution',
  top_300_breadth: 'Top-300 breadth',
  base_output_and_breadth: 'Research output and breadth',
  high_output_minimum_breadth: 'High output with minimum breadth',
  high_breadth_minimum_output: 'High breadth with minimum output',
}

export function routeLabel(routeId: string): string {
  return (
    ROUTE_LABELS[routeId] ??
    routeId
      .split('_')
      .map((part) => `${part.charAt(0).toLocaleUpperCase()}${part.slice(1)}`)
      .join(' ')
  )
}

export function routeSummary(evidence: OpportunityFilterEvidenceV2): string {
  const routes = evidence.establishing_route_ids
  if (routes.includes('skilled_trades') && routes.includes('construction')) {
    return 'Both: skilled trades and construction'
  }
  return routes.map(routeLabel).join(', ')
}

export function opportunityExplanation(
  evidence: OpportunityFilterEvidenceV2,
  definition: OpportunityFilterDefinitionV2 | undefined,
): string {
  const stateExplanation =
    evidence.state === 'VERIFIED_STRONG_SIGNAL'
      ? definition?.meaning ?? OPPORTUNITY_STATE_CONTENT[evidence.state].explanation
      : OPPORTUNITY_STATE_CONTENT[evidence.state].explanation
  if (definition?.id === 'health_social_work_opportunity') {
    return `${stateExplanation} This filter covers human health and social work; it is not doctor-only evidence.`
  }
  if (definition?.id === 'finance_insurance_opportunity') {
    return `${stateExplanation} This filter covers finance and insurance activity, not all business or administration careers.`
  }
  return stateExplanation
}

export function filterName(
  definition: OpportunityFilterDefinitionV2 | undefined,
  filterId: string,
  compact = false,
): string {
  void compact
  if (!definition) return filterId
  return compactDisplayName(definition)
}
