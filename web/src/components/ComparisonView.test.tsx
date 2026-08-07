import { render, screen } from '@testing-library/react'

import { ComparisonView } from './ComparisonView'
import {
  comparisonWithOpportunityAndFeasibilityFixture,
  catalogFixture,
  opportunityCatalogFixture,
  tfcCatalogFixture,
} from '../test/fixtures'

test('comparison keeps OFC, feasibility, source dates, ranks, and criteria separate', () => {
  render(
    <ComparisonView
      comparison={comparisonWithOpportunityAndFeasibilityFixture}
      criteria={catalogFixture.criteria}
      opportunityCatalog={opportunityCatalogFixture}
      tfcCatalog={tfcCatalogFixture}
      onBack={() => undefined}
      onSelectCountry={() => undefined}
    />,
  )

  expect(screen.getAllByText('Opportunity filter')).not.toHaveLength(0)
  expect(screen.getAllByText('Feasibility check')).not.toHaveLength(0)
  expect(screen.queryByText('How the signals relate')).not.toBeInTheDocument()
  expect(screen.queryByText('Locality assessment')).not.toBeInTheDocument()
  expect(screen.queryByText('Locality-derived')).not.toBeInTheDocument()
  expect(screen.queryByText('Limited coverage')).not.toBeInTheDocument()
  expect(screen.getAllByText(/Fictional skilled work route · effective 2026-08-05/)).not.toHaveLength(0)
  expect(screen.getAllByText(/sources fictional-work-source/)).not.toHaveLength(0)
  expect(screen.getAllByText(/Check evidence effective 2026-08-05/)).not.toHaveLength(0)
  expect(screen.getAllByText(/Filtered rank/)).not.toHaveLength(0)
  expect(screen.getAllByText(/Base rank/)).not.toHaveLength(0)
  expect(screen.getByLabelText('Experimental criterion')).toHaveAttribute(
    'title',
    'Experimental criterion',
  )
})
