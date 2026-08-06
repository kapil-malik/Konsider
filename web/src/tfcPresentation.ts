import type { TfcDefinitionV2, TfcOutcomeV2 } from './api/types'

export const readableTfcCode = (value: string) =>
  value
    .toLocaleLowerCase()
    .replaceAll('_', ' ')
    .replace(/^./, (letter) => letter.toLocaleUpperCase())

export function tfcOutcomeContent(outcome: TfcOutcomeV2) {
  if (outcome.common_status === 'INPUT_REQUIRED') {
    return { label: 'More information required', tone: 'input', icon: '?' }
  }
  if (outcome.common_status === 'UNSUPPORTED') {
    return { label: 'Destination not covered', tone: 'unsupported', icon: '○' }
  }
  if (outcome.common_status === 'DESTINATION_EVIDENCE_INSUFFICIENT') {
    return { label: 'Destination evidence unavailable', tone: 'insufficient', icon: '!' }
  }
  if (outcome.common_status === 'NOT_APPLICABLE') {
    return { label: 'Not applicable to this scenario', tone: 'neutral', icon: '–' }
  }
  if (outcome.common_status === 'EVALUATION_ERROR') {
    return { label: 'Assessment unavailable', tone: 'insufficient', icon: '!' }
  }
  const result = outcome.result
  if (result && 'routes' in result) {
    if (result.match_classification === 'SUPPORTED_ROUTE_MATCH') {
      return { label: 'Supported route match found', tone: 'match', icon: '✓' }
    }
    if (result.match_classification === 'CONDITIONAL_ROUTE_MATCH') {
      return { label: 'Conditional route match found', tone: 'conditional', icon: '◇' }
    }
    return { label: 'No supported route matched', tone: 'neutral', icon: '–' }
  }
  if (result && 'metric_id' in result) {
    return { label: 'Scenario estimate available', tone: 'match', icon: '✓' }
  }
  return { label: 'Assessment completed', tone: 'match', icon: '✓' }
}

export const tfcName = (
  definition: TfcDefinitionV2 | undefined,
  fallback: string,
) => definition?.displayName ?? readableTfcCode(fallback)
