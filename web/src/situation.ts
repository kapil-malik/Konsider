import type { TfcAssessmentSelectionV2, TfcCatalogV2 } from './api/types'

export const SITUATION_SCHEMA_VERSION = 'konsider-situation-1.0' as const
export const SESSION_STORAGE_KEY = 'konsider:situation:session'
export const LOCAL_STORAGE_KEY = 'konsider:situation:remembered'
export const MAX_SCENARIOS = 3

type Purpose = 'WORK' | 'STUDY' | 'FAMILY' | 'EXPLORATION'
type QualificationLevel =
  | 'SECONDARY'
  | 'VOCATIONAL'
  | 'BACHELORS'
  | 'MASTERS'
  | 'DOCTORATE'
  | 'OTHER'
  | 'UNKNOWN'
type PartnerStatus =
  | 'NONE'
  | 'SPOUSE'
  | 'CIVIL_PARTNER'
  | 'UNMARRIED_PARTNER'
  | 'UNKNOWN'
type JobOfferState = 'PRESENT' | 'ABSENT' | 'UNKNOWN'

export type SituationApplicant = {
  citizenships: string
  occupation: string
  occupationUnknown: boolean
  qualificationLevel: QualificationLevel
}

export type SituationHousehold = {
  partnerStatus: PartnerStatus
  partnerAccompanying: boolean | null
  dependantsKnown: boolean
  dependantCount: number
  dependantAgeBand:
    | 'UNDER_18'
    | 'AGE_18_TO_20'
    | 'AGE_21_TO_22'
    | 'AGE_23_TO_25'
    | 'OVER_25'
    | 'UNKNOWN'
}

export type SituationScenario = {
  id: string
  name: string
  purpose: Purpose
  selectedTfcIds: string[]
  targetDate: string
  targetCountries: string
  jobOfferState: JobOfferState
  primaryRouteId: string
  relocationComposition:
    | 'APPLICANT_ONLY'
    | 'WITH_PARTNER'
    | 'WITH_DEPENDANTS'
    | 'WITH_PARTNER_AND_DEPENDANTS'
    | 'UNKNOWN'
  studyInstitution: string
  studyField: string
  studyQualificationLevel:
    | 'VOCATIONAL'
    | 'BACHELORS'
    | 'MASTERS'
    | 'DOCTORATE'
    | 'OTHER'
    | 'UNKNOWN'
  studyDurationMonths: number
  studyMode: 'IN_PERSON' | 'HYBRID' | 'ONLINE' | 'UNKNOWN'
  studyCompletionDate: string
  studyCompletionState: 'COMPLETED' | 'CURRENT' | 'PLANNED'
}

export type SituationDocument = {
  schema_version: typeof SITUATION_SCHEMA_VERSION
  applicant: SituationApplicant
  household: SituationHousehold
  scenarios: SituationScenario[]
  active_scenario_id: string
}

type RememberedEnvelope = {
  schema_version: 'konsider-situation-storage-1.0'
  expires_at: string
  situation: SituationDocument
}

export type SituationLoadResult = {
  situation: SituationDocument
  remembered: boolean
  warning: string | null
}

const scenarioId = () =>
  typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `scenario-${Date.now()}-${Math.random().toString(16).slice(2)}`

export const createScenario = (
  name = 'My scenario',
  purpose: Purpose = 'EXPLORATION',
): SituationScenario => ({
  id: scenarioId(),
  name,
  purpose,
  selectedTfcIds: [],
  targetDate: '',
  targetCountries: '',
  jobOfferState: 'UNKNOWN',
  primaryRouteId: '',
  relocationComposition: 'UNKNOWN',
  studyInstitution: '',
  studyField: '',
  studyQualificationLevel: 'UNKNOWN',
  studyDurationMonths: 24,
  studyMode: 'UNKNOWN',
  studyCompletionDate: '',
  studyCompletionState: 'PLANNED',
})

export const createEmptySituation = (): SituationDocument => {
  const scenario = createScenario()
  return {
    schema_version: SITUATION_SCHEMA_VERSION,
    applicant: {
      citizenships: '',
      occupation: '',
      occupationUnknown: false,
      qualificationLevel: 'UNKNOWN',
    },
    household: {
      partnerStatus: 'UNKNOWN',
      partnerAccompanying: null,
      dependantsKnown: false,
      dependantCount: 0,
      dependantAgeBand: 'UNKNOWN',
    },
    scenarios: [scenario],
    active_scenario_id: scenario.id,
  }
}

export const cloneSituation = (value: SituationDocument): SituationDocument =>
  structuredClone(value)

export const activeScenario = (value: SituationDocument): SituationScenario =>
  value.scenarios.find((scenario) => scenario.id === value.active_scenario_id) ??
  value.scenarios[0]

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === 'string')

const hasAllowedValue = <T extends string>(value: unknown, allowed: readonly T[]): value is T =>
  typeof value === 'string' && allowed.includes(value as T)

function isApplicant(value: Record<string, unknown>): value is SituationApplicant {
  return (
    typeof value.citizenships === 'string' &&
    typeof value.occupation === 'string' &&
    typeof value.occupationUnknown === 'boolean' &&
    hasAllowedValue(value.qualificationLevel, [
      'SECONDARY',
      'VOCATIONAL',
      'BACHELORS',
      'MASTERS',
      'DOCTORATE',
      'OTHER',
      'UNKNOWN',
    ] as const)
  )
}

function isHousehold(value: Record<string, unknown>): value is SituationHousehold {
  return (
    hasAllowedValue(value.partnerStatus, [
      'NONE',
      'SPOUSE',
      'CIVIL_PARTNER',
      'UNMARRIED_PARTNER',
      'UNKNOWN',
    ] as const) &&
    (typeof value.partnerAccompanying === 'boolean' || value.partnerAccompanying === null) &&
    typeof value.dependantsKnown === 'boolean' &&
    typeof value.dependantCount === 'number' &&
    Number.isInteger(value.dependantCount) &&
    value.dependantCount >= 0 &&
    value.dependantCount <= 19 &&
    hasAllowedValue(value.dependantAgeBand, [
      'UNDER_18',
      'AGE_18_TO_20',
      'AGE_21_TO_22',
      'AGE_23_TO_25',
      'OVER_25',
      'UNKNOWN',
    ] as const)
  )
}

function isScenario(value: Record<string, unknown>): value is SituationScenario {
  return (
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    hasAllowedValue(value.purpose, ['WORK', 'STUDY', 'FAMILY', 'EXPLORATION'] as const) &&
    isStringArray(value.selectedTfcIds) &&
    typeof value.targetDate === 'string' &&
    typeof value.targetCountries === 'string' &&
    hasAllowedValue(value.jobOfferState, ['PRESENT', 'ABSENT', 'UNKNOWN'] as const) &&
    typeof value.primaryRouteId === 'string' &&
    hasAllowedValue(value.relocationComposition, [
      'APPLICANT_ONLY',
      'WITH_PARTNER',
      'WITH_DEPENDANTS',
      'WITH_PARTNER_AND_DEPENDANTS',
      'UNKNOWN',
    ] as const) &&
    typeof value.studyInstitution === 'string' &&
    typeof value.studyField === 'string' &&
    hasAllowedValue(value.studyQualificationLevel, [
      'VOCATIONAL',
      'BACHELORS',
      'MASTERS',
      'DOCTORATE',
      'OTHER',
      'UNKNOWN',
    ] as const) &&
    typeof value.studyDurationMonths === 'number' &&
    Number.isInteger(value.studyDurationMonths) &&
    value.studyDurationMonths >= 1 &&
    value.studyDurationMonths <= 120 &&
    hasAllowedValue(value.studyMode, ['IN_PERSON', 'HYBRID', 'ONLINE', 'UNKNOWN'] as const) &&
    typeof value.studyCompletionDate === 'string' &&
    hasAllowedValue(value.studyCompletionState, ['COMPLETED', 'CURRENT', 'PLANNED'] as const)
  )
}

export function parseSituation(value: unknown): SituationDocument {
  if (!isRecord(value) || value.schema_version !== SITUATION_SCHEMA_VERSION) {
    throw new Error(`This file is not ${SITUATION_SCHEMA_VERSION}.`)
  }
  if (
    !isRecord(value.applicant) ||
    !isApplicant(value.applicant) ||
    !isRecord(value.household) ||
    !isHousehold(value.household)
  ) {
    throw new Error('Applicant or household data is missing.')
  }
  if (!Array.isArray(value.scenarios) || value.scenarios.length < 1) {
    throw new Error('At least one scenario is required.')
  }
  if (value.scenarios.length > MAX_SCENARIOS) {
    throw new Error(`A maximum of ${MAX_SCENARIOS} scenarios can be imported.`)
  }
  const scenarios = value.scenarios.map((scenario, index) => {
    if (!isRecord(scenario) || !isScenario(scenario)) {
      throw new Error(`Scenario ${index + 1} is invalid.`)
    }
    return scenario as SituationScenario
  })
  if (typeof value.active_scenario_id !== 'string') {
    throw new Error('The active scenario is invalid.')
  }
  const parsed = value as SituationDocument
  if (!scenarios.some((scenario) => scenario.id === parsed.active_scenario_id)) {
    throw new Error('The active scenario does not exist in the imported file.')
  }
  return cloneSituation(parsed)
}

export function loadSituation(): SituationLoadResult {
  const fallback = createEmptySituation()
  try {
    const session = sessionStorage.getItem(SESSION_STORAGE_KEY)
    if (session) {
      const situation = parseSituation(JSON.parse(session))
      const remembered = localStorage.getItem(LOCAL_STORAGE_KEY)
      if (!remembered) return { situation, remembered: false, warning: null }
      try {
        const envelope = JSON.parse(remembered) as RememberedEnvelope
        if (
          envelope.schema_version !== 'konsider-situation-storage-1.0' ||
          new Date(envelope.expires_at).getTime() <= Date.now()
        ) {
          localStorage.removeItem(LOCAL_STORAGE_KEY)
          return {
            situation,
            remembered: false,
            warning: 'Remembered situation data expired or used an unsupported version and was cleared.',
          }
        }
        parseSituation(envelope.situation)
        return { situation, remembered: true, warning: null }
      } catch {
        localStorage.removeItem(LOCAL_STORAGE_KEY)
        return {
          situation,
          remembered: false,
          warning: 'Remembered situation data could not be read and was cleared.',
        }
      }
    }
  } catch {
    sessionStorage.removeItem(SESSION_STORAGE_KEY)
  }
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY)
    if (!raw) return { situation: fallback, remembered: false, warning: null }
    const envelope = JSON.parse(raw) as RememberedEnvelope
    if (
      envelope.schema_version !== 'konsider-situation-storage-1.0' ||
      new Date(envelope.expires_at).getTime() <= Date.now()
    ) {
      localStorage.removeItem(LOCAL_STORAGE_KEY)
      return {
        situation: fallback,
        remembered: false,
        warning: 'Remembered situation data expired or used an unsupported version and was cleared.',
      }
    }
    const situation = parseSituation(envelope.situation)
    sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(situation))
    return { situation, remembered: true, warning: null }
  } catch {
    localStorage.removeItem(LOCAL_STORAGE_KEY)
    return {
      situation: fallback,
      remembered: false,
      warning: 'Remembered situation data could not be read and was cleared.',
    }
  }
}

export function persistSituation(value: SituationDocument, remember: boolean): void {
  sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(value))
  if (!remember) {
    localStorage.removeItem(LOCAL_STORAGE_KEY)
    return
  }
  const expires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
  const envelope: RememberedEnvelope = {
    schema_version: 'konsider-situation-storage-1.0',
    expires_at: expires.toISOString(),
    situation: value,
  }
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(envelope))
}

export function clearSituationStorage(): void {
  sessionStorage.removeItem(SESSION_STORAGE_KEY)
  localStorage.removeItem(LOCAL_STORAGE_KEY)
}

export function clearRememberedSituation(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEY)
}

const countryCodes = (value: string): string[] =>
  value
    .split(',')
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean)

export function validateSituation(value: SituationDocument): string[] {
  const errors: string[] = []
  const scenario = activeScenario(value)
  for (const [label, raw] of [
    ['Citizenship', value.applicant.citizenships],
    ['Target destination', scenario.targetCountries],
  ]) {
    const invalid = countryCodes(raw).filter((code) => !/^[A-Z]{3}$/.test(code))
    if (invalid.length) errors.push(`${label} codes must contain three letters.`)
  }
  if (!scenario.name.trim()) errors.push('Scenario name is required.')
  if (value.scenarios.some((item) => !item.name.trim())) {
    errors.push('Every scenario needs a name.')
  }
  return [...new Set(errors)]
}

export function feasibilityFor(value: SituationDocument): TfcAssessmentSelectionV2 | undefined {
  const scenario = activeScenario(value)
  if (!scenario.selectedTfcIds.length) return undefined
  const applicantUnknown: string[] = []
  if (value.applicant.occupationUnknown) applicantUnknown.push('applicant.occupation')
  if (value.applicant.qualificationLevel === 'UNKNOWN') {
    applicantUnknown.push('applicant.qualifications')
  }
  const citizenships = countryCodes(value.applicant.citizenships)
  const applicant = {
    ...(citizenships.length ? { citizenships } : {}),
    ...(value.applicant.occupation.trim() && !value.applicant.occupationUnknown
      ? {
          occupation: {
            user_text: value.applicant.occupation.trim(),
            mapping_state: 'UNRESOLVED' as const,
          },
        }
      : {}),
    ...(value.applicant.qualificationLevel !== 'UNKNOWN'
      ? { qualifications: [{ level: value.applicant.qualificationLevel }] }
      : {}),
    ...(applicantUnknown.length ? { unknown_fields: applicantUnknown } : {}),
  }
  const householdUnknown = value.household.dependantsKnown
    ? []
    : ['household.dependants']
  const household = {
    partner_status: value.household.partnerStatus,
    partner_accompanying: value.household.partnerAccompanying,
    ...(value.household.dependantsKnown
      ? {
          dependants: Array.from({ length: value.household.dependantCount }, () => ({
            role: 'DEPENDENT_CHILD' as const,
            relocating: true,
            age_band: value.household.dependantAgeBand,
          })),
        }
      : {}),
    ...(householdUnknown.length ? { unknown_fields: householdUnknown } : {}),
  }
  const targets = countryCodes(scenario.targetCountries)
  const studyComplete =
    scenario.studyInstitution.trim() &&
    scenario.studyField.trim() &&
    scenario.studyCompletionDate
  const scenarioContext = {
    purpose: scenario.purpose,
    ...(scenario.targetDate ? { target_date: scenario.targetDate } : {}),
    ...(targets.length ? { target_country_codes: targets } : {}),
    ...(scenario.purpose === 'WORK' || scenario.jobOfferState !== 'UNKNOWN'
      ? { job_offer: { state: scenario.jobOfferState } }
      : {}),
    ...(scenario.primaryRouteId.trim()
      ? { primary_route_id: scenario.primaryRouteId.trim() }
      : {}),
    relocation_composition: scenario.relocationComposition,
    ...(studyComplete
      ? {
          intended_study: {
            institution: {
              user_text: scenario.studyInstitution.trim(),
              mapping_state: 'UNRESOLVED' as const,
            },
            qualification_level: scenario.studyQualificationLevel,
            field: {
              user_text: scenario.studyField.trim(),
              mapping_state: 'UNRESOLVED' as const,
            },
            duration_months: scenario.studyDurationMonths,
            mode: scenario.studyMode,
            completion_date: scenario.studyCompletionDate,
            completion_state: scenario.studyCompletionState,
          },
        }
      : {}),
  }
  return {
    tfc_ids: [...scenario.selectedTfcIds].sort(),
    mode: 'ASSESS_ONLY',
    profile_context: applicant,
    household_context: household,
    scenario_context: scenarioContext,
  }
}

export const recommendedTfcs = (catalog: TfcCatalogV2, purpose: Purpose) =>
  catalog.definitions.filter((definition) =>
    definition.applicable_purposes.includes(purpose),
  )

export const situationSummary = (value: SituationDocument): string => {
  const scenario = activeScenario(value)
  const parts = [scenario.name, scenario.purpose.toLocaleLowerCase()]
  const countries = countryCodes(scenario.targetCountries)
  if (countries.length) parts.push(countries.join(', '))
  return parts.join(' · ')
}

export const exportSituation = (value: SituationDocument): string => {
  const exported = cloneSituation(value)
  exported.applicant.citizenships = ''
  exported.household = createEmptySituation().household
  return `${JSON.stringify(exported, null, 2)}\n`
}
