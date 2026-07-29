import type { PreferencePreset } from './api/types'

export const IMPORTANCE_STATES = [
  { label: 'No', shortLabel: 'No', value: 0 },
  { label: 'Very Low', shortLabel: 'V. Low', value: 0.2 },
  { label: 'Low', shortLabel: 'Low', value: 0.4 },
  { label: 'Medium', shortLabel: 'Med', value: 0.6 },
  { label: 'High', shortLabel: 'High', value: 0.8 },
  { label: 'Very High', shortLabel: 'V. High', value: 1 },
] as const

export type PreferenceDraft = {
  preferencePresetId: string | null
  weights: Record<string, number>
}

export function preferenceFromPreset(preset: PreferencePreset): PreferenceDraft {
  return { preferencePresetId: preset.id, weights: { ...preset.weights } }
}

export function importanceState(value: number) {
  const index = Math.max(0, Math.min(5, Math.round(value * 5)))
  return IMPORTANCE_STATES[index]
}

export function preferencesEqual(
  first: PreferenceDraft | null,
  second: PreferenceDraft | null,
): boolean {
  if (
    !first ||
    !second ||
    first.preferencePresetId !== second.preferencePresetId
  )
    return false
  const keys = new Set([...Object.keys(first.weights), ...Object.keys(second.weights)])
  return [...keys].every((key) => first.weights[key] === second.weights[key])
}

export function clonePreference(preference: PreferenceDraft): PreferenceDraft {
  return {
    preferencePresetId: preference.preferencePresetId,
    weights: { ...preference.weights },
  }
}

export function formatScore(value: number): string {
  return `${value.toFixed(1)} / 10`
}

export function humanizeUnit(value: string): string {
  return value.replaceAll('_', ' ')
}

export function formatObservation(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}
