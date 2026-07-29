import type {
  ContributionV2,
  RankingV2,
  RankedCountryV2,
} from './api/types'

export const readableCode = (value: string) =>
  value
    .toLocaleLowerCase()
    .replaceAll(':', ' · ')
    .replaceAll('_', ' ')
    .replaceAll('.', ' ')
    .replace(/^\w/, (character) => character.toLocaleUpperCase())

export const countryCode = (entityId: string) => entityId.replace(/^country:/, '')

type Notice = {
  label: string
  message: string
  prominence: 'neutral' | 'mild' | 'caution' | 'strong'
  icon: string
}

export const COVERAGE_CONTENT: Record<
  RankingV2['assessments']['coverage']['status'],
  Notice
> = {
  NO_PARTIAL_CRITERIA_ACTIVE: {
    label: 'Full-coverage criteria only',
    message: 'No limited-coverage criterion is active for this ranking.',
    prominence: 'neutral',
    icon: 'i',
  },
  FULL_COVERAGE: {
    label: 'Full coverage',
    message: 'Every country has valid evidence for all active criteria.',
    prominence: 'neutral',
    icon: '✓',
  },
  PARTIAL_COMPLETE_CASE: {
    label: 'Limited-coverage ranking',
    message:
      'Countries without every active criterion are excluded; their available evidence remains inspectable.',
    prominence: 'caution',
    icon: '!',
  },
  COVERAGE_LIMIT_FALLBACK: {
    label: 'Coverage fallback applied',
    message:
      'The server removed limited-coverage criteria because too few complete country results remained.',
    prominence: 'strong',
    icon: '!',
  },
}

export const LOCALITY_CONTENT: Record<
  RankingV2['assessments']['locality']['status'],
  Notice
> = {
  NO_ACTIVE_LOCALITY_CRITERIA: {
    label: 'National evidence only',
    message: 'No locality-derived criterion contributes to this ranking.',
    prominence: 'neutral',
    icon: 'i',
  },
  BELOW_ANALYSIS_THRESHOLD: {
    label: 'Locality evidence retained',
    message:
      'A locality-derived criterion contributes below the analysis threshold. Detailed provenance remains available.',
    prominence: 'mild',
    icon: 'i',
  },
  ONE_ACTIVE_LOCALITY_CRITERION: {
    label: 'One locality criterion assessed',
    message:
      'Locality evidence is shown for the active criterion; cross-criterion compatibility is not applicable.',
    prominence: 'mild',
    icon: '⌖',
  },
  COMMON_LOCALITY_AVAILABLE: {
    label: 'Common locality available',
    message: 'The server found qualifying locality evidence shared across active locality criteria.',
    prominence: 'mild',
    icon: '✓',
  },
  PARTIAL_OVERLAP: {
    label: 'Partial locality overlap',
    message:
      'Some active locality criteria overlap, but no one locality satisfies every selected criterion.',
    prominence: 'caution',
    icon: '!',
  },
  NO_COMMON_LOCALITY: {
    label: 'Strong options are in different localities',
    message:
      'Strong options exist across the selected criteria, but the leading evidence comes from different metropolitan areas.',
    prominence: 'caution',
    icon: '!',
  },
  INSUFFICIENT_LOCALITY_EVIDENCE: {
    label: 'Locality compatibility is uncertain',
    message: 'The server found insufficient valid locality evidence for a compatibility assessment.',
    prominence: 'caution',
    icon: '!',
  },
  MIXED_COUNTRY_RESULTS: {
    label: 'Locality results vary by country',
    message:
      'Some countries have common locality evidence while others have partial, absent, or insufficient overlap.',
    prominence: 'caution',
    icon: '!',
  },
}

export const PROFILE_CONTENT: Record<
  RankingV2['assessments']['profile']['status'],
  Notice
> = {
  NO_PROFILE_CONTEXT: {
    label: 'No applicant profile assessed',
    message: 'Results use preference weights only; no personal or household suitability is inferred.',
    prominence: 'neutral',
    icon: 'i',
  },
  NOT_EVALUATED: {
    label: 'Profile suitability not evaluated',
    message: 'Applicant and household dimensions were not evaluated for this result.',
    prominence: 'mild',
    icon: 'i',
  },
  EVALUATED: {
    label: 'Profile context evaluated',
    message: 'The listed applicant or household dimensions were evaluated by the server.',
    prominence: 'mild',
    icon: '✓',
  },
}

export function localityContributions(country: RankedCountryV2): ContributionV2[] {
  return country.contributions.filter(
    (contribution) => contribution.derivation === 'AGGREGATED_FROM_LOCALITIES',
  )
}

export function contributingLocalityNames(country: RankedCountryV2): string[] {
  return [
    ...new Set(
      localityContributions(country).flatMap((contribution) =>
        contribution.contributing_localities.map(
          (locality) => locality.locality.display_name,
        ),
      ),
    ),
  ]
}

export function localityName(
  entityId: string | null,
  contributions: ContributionV2[],
): string | null {
  if (!entityId) return null
  return (
    contributions
      .flatMap((contribution) => contribution.contributing_localities)
      .find((item) => item.locality.entity_id === entityId)?.locality
      .display_name ?? readableCode(entityId)
  )
}
