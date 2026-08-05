import { afterEach, describe, expect, test, vi } from 'vitest'

import {
  LOCAL_STORAGE_KEY,
  MAX_SCENARIOS,
  SESSION_STORAGE_KEY,
  activeScenario,
  createEmptySituation,
  exportSituation,
  feasibilityFor,
  loadSituation,
  parseSituation,
  persistSituation,
} from './situation'

afterEach(() => {
  vi.useRealTimers()
  sessionStorage.clear()
  localStorage.clear()
})

describe('guest situation storage', () => {
  test('keeps a tab copy by default and only writes device storage after opt-in', () => {
    const situation = createEmptySituation()
    activeScenario(situation).selectedTfcIds = ['skilled_work_route_feasibility']

    persistSituation(situation, false)
    expect(sessionStorage.getItem(SESSION_STORAGE_KEY)).toContain('skilled_work_route_feasibility')
    expect(localStorage.getItem(LOCAL_STORAGE_KEY)).toBeNull()

    persistSituation(situation, true)
    expect(localStorage.getItem(LOCAL_STORAGE_KEY)).toContain('konsider-situation-storage-1.0')
    expect(loadSituation()).toMatchObject({ remembered: true, warning: null })
  })

  test('clears an expired remembered copy without discarding a valid tab copy', () => {
    const now = new Date('2026-08-05T00:00:00.000Z')
    vi.useFakeTimers()
    vi.setSystemTime(now)
    const situation = createEmptySituation()
    persistSituation(situation, true)
    const envelope = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY)!)
    envelope.expires_at = '2026-08-04T23:59:59.000Z'
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(envelope))

    const loaded = loadSituation()

    expect(loaded.situation.active_scenario_id).toBe(situation.active_scenario_id)
    expect(loaded.remembered).toBe(false)
    expect(loaded.warning).toMatch(/expired or used an unsupported version/)
    expect(localStorage.getItem(LOCAL_STORAGE_KEY)).toBeNull()
  })
})

describe('guest situation portability', () => {
  test('exports declared context without assessment results or URLs', () => {
    const situation = createEmptySituation()
    situation.applicant.occupation = 'Civil engineer'
    const exported = exportSituation(situation)

    const imported = parseSituation(JSON.parse(exported))
    expect(imported.applicant.occupation).toBe('Civil engineer')
    expect(imported.applicant.citizenships).toBe('')
    expect(imported.household.partnerStatus).toBe('UNKNOWN')
    expect(exported).not.toMatch(/assessment|result|https?:\/\//i)
  })

  test('rejects incomplete and over-limit imported documents', () => {
    const situation = createEmptySituation()
    expect(() => parseSituation({ ...situation, applicant: {} })).toThrow(
      'Applicant or household data is missing.',
    )
    expect(() =>
      parseSituation({
        ...situation,
        scenarios: Array.from({ length: MAX_SCENARIOS + 1 }, () => situation.scenarios[0]),
      }),
    ).toThrow(`A maximum of ${MAX_SCENARIOS} scenarios can be imported.`)
  })
})

test('serializes explicit unknowns and keeps feasibility assessment-only', () => {
  const situation = createEmptySituation()
  situation.applicant.occupationUnknown = true
  const scenario = activeScenario(situation)
  scenario.purpose = 'WORK'
  scenario.selectedTfcIds = ['skilled_work_route_feasibility']
  scenario.targetCountries = 'deu, can'

  expect(feasibilityFor(situation)).toMatchObject({
    tfc_ids: ['skilled_work_route_feasibility'],
    mode: 'ASSESS_ONLY',
    profile_context: {
      unknown_fields: ['applicant.occupation', 'applicant.qualifications'],
    },
    scenario_context: {
      purpose: 'WORK',
      target_country_codes: ['DEU', 'CAN'],
      job_offer: { state: 'UNKNOWN' },
    },
  })
})
