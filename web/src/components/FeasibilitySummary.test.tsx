import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'

import type { TfcCountryAssessmentV2 } from '../api/types'
import { tfcCatalogFixture } from '../test/fixtures'
import { FeasibilityEvidence } from './FeasibilitySummary'

test('renders scenario metric estimates, assumptions, units, and effective date', () => {
  const assessment: TfcCountryAssessmentV2 = {
    country_code: 'DEU',
    base_rank: 2,
    filtered_rank: 2,
    affinity_score_before: 7.8,
    affinity_score_after: 7.8,
    no_change_affinity: true,
    outcomes: [
      {
        tfc_id: 'illustrative_scenario_cost',
        country_code: 'DEU',
        common_status: 'EVALUATED',
        reason_codes: ['METRIC_CALCULATED'],
        input_required_fields: [],
        result: {
          result_type: 'SCENARIO_METRIC',
          metric_id: 'illustrative_cost',
          formula_type: 'BOUNDED_SUM',
          value: null,
          minimum: 1200,
          maximum: 1600,
          unit: 'EUR',
          currency: 'EUR',
          period: 'MONTHLY',
          components: [],
          assumptions: ['One applicant', 'National estimate'],
          rounding: {},
          locality_id: null,
          source_ids: ['illustrative-source'],
          effective_from: '2026-07-01',
          effective_to: null,
          evidence_quality: 'MEDIUM',
        },
        warnings: [],
      },
    ],
  }

  render(<FeasibilityEvidence assessment={assessment} catalog={tfcCatalogFixture} />)

  expect(screen.getByText('Scenario estimate available')).toBeInTheDocument()
  expect(screen.getByText(/1200.*1600 EUR.*monthly/i)).toBeInTheDocument()
  expect(screen.getByText('2026-07-01')).toBeInTheDocument()
  expect(screen.getByText('One applicant, National estimate')).toBeInTheDocument()
})
