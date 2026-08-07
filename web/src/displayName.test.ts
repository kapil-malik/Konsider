import { describe, expect, test } from 'vitest'

import {
  boundedCompactDisplayName,
  byDisplayOrder,
  compactDisplayName,
  distinctDisplayName,
} from './displayName'

describe('display metadata names', () => {
  test('prefers compactName and exposes a distinct formal name', () => {
    const definition = { compactName: 'Work VISA', displayName: 'Highly qualified work route check' }

    expect(compactDisplayName(definition)).toBe('Work VISA')
    expect(distinctDisplayName(definition)).toBe('Highly qualified work route check')
  })

  test('falls back to displayName only when compactName is unavailable', () => {
    const definition = { compactName: null, displayName: 'Political stability' }

    expect(compactDisplayName(definition)).toBe('Political stability')
    expect(distinctDisplayName(definition)).toBeNull()
  })

  test('orders definitions by product display order rather than id', () => {
    const definitions = [
      { id: 'C01', sortOrder: 20 },
      { id: 'z_named_criterion', sortOrder: 10 },
    ]

    expect([...definitions].sort(byDisplayOrder).map((item) => item.id)).toEqual([
      'z_named_criterion',
      'C01',
    ])
  })

  test('bounds compact criterion names to 22 characters', () => {
    expect(
      boundedCompactDisplayName({ compactName: '1234567890123456789012', displayName: 'Formal' }),
    ).toBe('1234567890123456789012')
    expect(
      boundedCompactDisplayName({ compactName: '12345678901234567890123', displayName: 'Formal' }),
    ).toBe('1234567890123456789...')
  })
})
