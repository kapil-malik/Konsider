import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import App from './App'
import type {
  CatalogV2,
  ComparisonV2,
  CountryDetailsV2,
  OpportunityFilterCatalogV2,
  RankingV2,
  TfcCatalogV2,
} from './api/types'
import {
  catalogFixture,
  comparisonFixture,
  comparisonWithOpportunityFixture,
  comparisonWithUnavailableFixture,
  countryDetailsFixture,
  countryDetailsWithOpportunityFixture,
  coverageWarningRanking,
  opportunityCatalogFixture,
  rankingFixture,
  rankingForLocalityStatus,
  rankingWithOpportunityFilters,
  rankingWithFeasibility,
  tfcCatalogFixture,
  comparisonWithFeasibilityFixture,
  countryDetailsWithFeasibilityFixture,
} from './test/fixtures'

type RecordedRequest = { path: string; method: string; body?: unknown }

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function installApi({
  ranking = rankingFixture,
  comparison = comparisonFixture,
  catalog = catalogFixture,
  opportunityCatalog = opportunityCatalogFixture,
  tfcCatalog = tfcCatalogFixture,
  subsequentRanking = ranking,
  detailsForCode,
}: {
  ranking?: RankingV2
  comparison?: ComparisonV2
  catalog?: CatalogV2
  opportunityCatalog?: OpportunityFilterCatalogV2
  tfcCatalog?: TfcCatalogV2 | null
  subsequentRanking?: RankingV2
  detailsForCode?: (code: string) => CountryDetailsV2
} = {}) {
  const requests: RecordedRequest[] = []
  let rankingCalls = 0
  const fetchMock = vi.fn(
    async (input: string | URL | Request, init?: RequestInit) => {
      const url = new URL(
        typeof input === 'string'
          ? input
          : input instanceof URL
            ? input
            : input.url,
      )
      const body = init?.body ? JSON.parse(String(init.body)) : undefined
      requests.push({ path: url.pathname, method: init?.method ?? 'GET', body })
      if (url.pathname.endsWith('/catalog')) return jsonResponse(catalog)
      if (url.pathname.endsWith('/opportunity-filters')) {
        return jsonResponse(opportunityCatalog)
      }
      if (url.pathname.endsWith('/tfcs')) {
        return tfcCatalog
          ? jsonResponse(tfcCatalog)
          : jsonResponse(
              {
                error: {
                  code: 'tfc_release_unavailable',
                  message: 'The active feasibility evidence is unavailable.',
                  details: {},
                  request_id: null,
                },
              },
              503,
            )
      }
      if (url.pathname.endsWith('/rankings')) {
        rankingCalls += 1
        return jsonResponse(rankingCalls === 1 ? ranking : subsequentRanking)
      }
      if (url.pathname.includes('/countries/')) {
        const code = url.pathname.split('/countries/')[1]?.split('/')[0] ?? 'C00'
        if (detailsForCode) return jsonResponse(detailsForCode(code))
        const excluded = code === 'C04'
        return jsonResponse(countryDetailsFixture(excluded ? 4 : 0, excluded))
      }
      if (url.pathname.endsWith('/comparisons')) return jsonResponse(comparison)
      return jsonResponse(
        { error: { code: 'not_found', message: 'Not found' } },
        404,
      )
    },
  )
  vi.stubGlobal('fetch', fetchMock)
  return requests
}

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
      mutations: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  )
}

async function configureWorkSituation(
  user: ReturnType<typeof userEvent.setup>,
  { remember = false, includeOffer = false } = {},
) {
  await user.click(screen.getByRole('button', { name: 'Add your situation' }))
  const dialog = screen.getByRole('dialog', { name: 'Your situation' })
  await user.click(within(dialog).getByRole('radio', { name: 'Work' }))
  await user.click(within(dialog).getByRole('button', { name: 'Continue' }))
  await user.click(
    within(dialog).getByRole('checkbox', {
      name: /Highly qualified work route check/,
    }),
  )
  await user.click(within(dialog).getByRole('button', { name: 'Continue' }))
  await user.type(within(dialog).getByRole('combobox', { name: /Target destinations/ }), 'DEU')
  fireEvent.change(within(dialog).getByLabelText(/Target date/), {
    target: { value: '2026-08-05' },
  })
  await user.type(within(dialog).getByRole('textbox', { name: /Current occupation/ }), 'Fictional analyst')
  await user.selectOptions(
    within(dialog).getByRole('combobox', { name: /Qualifications/ }),
    'MASTERS',
  )
  if (includeOffer) {
    await user.selectOptions(
      within(dialog).getByRole('combobox', { name: /Job offer/ }),
      'PRESENT',
    )
  }
  await user.click(within(dialog).getByRole('button', { name: 'Continue' }))
  if (remember) {
    await user.click(
      within(dialog).getByRole('checkbox', {
        name: 'Remember my situation on this device',
      }),
    )
  }
  await user.click(within(dialog).getByRole('button', { name: 'Save and assess' }))
}

test('renders compact accessible criterion symbols and source links', async () => {
  installApi()
  const user = userEvent.setup()
  renderApp()

  expect(
    await screen.findByRole('heading', { name: 'What matters most?' }),
  ).toBeInTheDocument()
  expect(screen.getAllByRole('slider')).toHaveLength(3)
  expect(
    screen.getByRole('slider', { name: 'Extreme heat exposure' }),
  ).toHaveValue('0.6')
  expect(screen.getAllByLabelText('Locality-derived criterion').length).toBeGreaterThan(0)
  expect(screen.getByLabelText('Experimental criterion')).toBeInTheDocument()
  expect(screen.getAllByLabelText('Partial-coverage criterion').length).toBeGreaterThan(0)
  expect(screen.getByLabelText('4 of 5 countries covered')).toHaveTextContent('4/5')
  expect(screen.queryByText('! Limited coverage')).not.toBeInTheDocument()
  expect(screen.queryByText('Coverage and scope details')).not.toBeInTheDocument()

  const heat = screen.getByRole('slider', { name: 'Extreme heat exposure' })
  heat.focus()
  fireEvent.keyDown(heat, { key: 'ArrowLeft' })
  expect(heat).toHaveValue('0.4')
  expect(screen.queryByText(/Locality provenance remains available/)).not.toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Open criteria and sources for Extreme heat exposure' }))
  const directDialog = screen.getByRole('dialog', { name: 'Criteria and sources' })
  expect(within(directDialog).getByText('Extreme heat exposure')).toBeInTheDocument()
  await user.click(within(directDialog).getByRole('button', { name: 'Close Criteria and sources' }))

  await user.click(screen.getByRole('button', { name: /Guest/ }))
  await user.click(screen.getByRole('menuitem', { name: 'Criteria and sources' }))
  const dialog = screen.getByRole('dialog', { name: 'Criteria and sources' })
  expect(within(dialog).getByText('Extreme heat exposure')).toBeInTheDocument()
  expect(within(dialog).getByText('major-cities-v1')).toBeInTheDocument()
  expect(within(dialog).getByText('Top n mean ·')).toBeInTheDocument()
  expect(within(dialog).getAllByText('Universal').length).toBeGreaterThan(0)
  expect(within(dialog).getAllByText(/Primary observation/).length).toBeGreaterThan(0)
})

test('uses preference_preset_id until an edit creates custom weights', async () => {
  const requests = installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(requests.find((item) => item.path.endsWith('/rankings'))?.body).toEqual({
    preference_preset_id: 'balanced',
  })
  const preset = screen.getByLabelText('Preference preset')
  await user.selectOptions(preset, 'climate')
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  await waitFor(() =>
    expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(2),
  )
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    preference_preset_id: 'climate',
  })

  const air = screen.getByRole('slider', { name: 'Air quality' })
  air.focus()
  fireEvent.keyDown(air, { key: 'ArrowRight' })
  expect(preset).toHaveValue('__custom')
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  await waitFor(() =>
    expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(3),
  )
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    weights: { air: 0.6, heat: 0.8, jobs: 0.4 },
  })
})

test('opens all three helper pages and filters the country coverage table', async () => {
  installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  await user.click(screen.getByRole('button', { name: /Guest/ }))
  expect(screen.getByRole('menuitem', { name: 'How Konsider works' })).toBeInTheDocument()
  expect(screen.getByRole('menuitem', { name: 'Criteria and sources' })).toBeInTheDocument()
  await user.click(screen.getByRole('menuitem', { name: 'Countries and coverage' }))

  const dialog = screen.getByRole('dialog', { name: 'Countries and coverage' })
  expect(within(dialog).getByRole('row', { name: /C04 Country 5 2\/4 available/ })).toBeInTheDocument()
  expect(within(dialog).getByText('Extreme heat exposure')).toBeInTheDocument()
  await user.type(within(dialog).getByRole('searchbox', { name: 'Search countries' }), 'c03')
  expect(within(dialog).getByRole('row', { name: /C03 Country 4/ })).toBeInTheDocument()
  expect(within(dialog).queryByRole('row', { name: /C00 Country 1/ })).not.toBeInTheDocument()
})

test.each([
  ['NO_ACTIVE_LOCALITY_CRITERIA', 'National evidence only'],
  ['BELOW_ANALYSIS_THRESHOLD', 'Locality evidence retained'],
  ['ONE_ACTIVE_LOCALITY_CRITERION', 'One locality criterion assessed'],
  ['COMMON_LOCALITY_AVAILABLE', 'Common locality available'],
  ['PARTIAL_OVERLAP', 'Partial locality overlap'],
  ['NO_COMMON_LOCALITY', 'Strong options are in different localities'],
  ['INSUFFICIENT_LOCALITY_EVIDENCE', 'Locality compatibility is uncertain'],
  ['MIXED_COUNTRY_RESULTS', 'Locality results vary by country'],
] as const)('renders the %s locality status supplied by the API', async (status, label) => {
  installApi({ ranking: rankingForLocalityStatus(status) })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await user.click(screen.getByRole('button', { name: /Guest/ }))
  await user.click(screen.getByRole('menuitem', { name: 'How Konsider works' }))
  expect(
    await screen.findByRole('status', { name: `Locality status: ${label}` }),
  ).toBeInTheDocument()
})

test('keeps coverage, locality, and profile explanations together in How Konsider works', async () => {
  installApi({ ranking: coverageWarningRanking })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  expect(screen.queryByRole('status', { name: /Coverage status/ })).not.toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: /Guest/ }))
  await user.click(screen.getByRole('menuitem', { name: 'How Konsider works' }))
  const dialog = screen.getByRole('dialog', { name: 'How Konsider works' })
  expect(
    within(dialog).getByRole('status', {
      name: 'Coverage status: Limited-coverage ranking',
    }),
  ).toBeInTheDocument()
  expect(
    within(dialog).getByRole('status', {
      name: 'Locality status: Strong options are in different localities',
    }),
  ).toBeInTheDocument()
  expect(
    within(dialog).getByRole('status', {
      name: 'Profile status: No applicant profile assessed',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getAllByText(/affinity score is unchanged/i).length,
  ).toBeGreaterThan(0)
})

test('shows criterion names, symbols, and score-only detailed ranking cells', async () => {
  installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(screen.getAllByText('Best common: Harbor City 1').length).toBeGreaterThan(0)
  await user.click(screen.getByLabelText('Show detailed evidence'))
  const heatHeader = screen.getByRole('columnheader', { name: /Extreme heat exposure/ })
  expect(within(heatHeader).getByLabelText('Full-coverage criterion')).toBeInTheDocument()
  expect(within(heatHeader).getByLabelText('Locality-derived criterion')).toBeInTheDocument()
  expect(within(heatHeader).getByLabelText('Experimental criterion')).toBeInTheDocument()
  expect(screen.queryByRole('columnheader', { name: /Climate and environment/ })).not.toBeInTheDocument()
  expect(screen.queryByText('top-two:heat')).not.toBeInTheDocument()
  expect(screen.queryByText(/Extreme heat exposure caveat/)).not.toBeInTheDocument()
  expect(document.querySelector('.criterion-score-cell details')).not.toBeInTheDocument()
})

test('country details distinguish locality advice from coverage exclusion', async () => {
  installApi({ ranking: coverageWarningRanking })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  await user.click(screen.getByRole('button', { name: 'Country 5' }))
  expect(
    await screen.findByRole('heading', { name: 'Country 5', level: 2 }),
  ).toBeInTheDocument()
  expect(screen.getByText('Coverage excluded · not ranked')).toBeInTheDocument()
  expect(screen.getByText('Unavailable active criterion')).toBeInTheDocument()
  expect(screen.getByText('Source value missing')).toBeInTheDocument()
  expect(screen.getAllByText(/Strong options are in different localities/).length).toBeGreaterThan(0)

  await user.click(screen.getByRole('button', { name: 'Close country details' }))
  await user.click(screen.getAllByRole('button', { name: 'View country details' })[0])
  expect(
    await screen.findByRole('heading', { name: 'Country 1', level: 2 }),
  ).toBeInTheDocument()
  expect(
    screen.queryByText('Coverage excluded · not ranked'),
  ).not.toBeInTheDocument()
  expect(screen.getByText('Contributing localities')).toBeInTheDocument()
  expect(
    screen.getAllByRole('link', {
      name: /View Public Data Publisher source/,
    })[0],
  ).toHaveAttribute('href', 'https://example.com/public-data')
})

test('comparison shows aggregates, locality provenance, status, and unavailable cells', async () => {
  installApi({
    ranking: coverageWarningRanking,
    comparison: comparisonWithUnavailableFixture,
  })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  const boxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  for (const checkbox of boxes.slice(0, 4)) await user.click(checkbox)
  await user.click(screen.getByRole('button', { name: 'Compare selected (4)' }))
  expect(
    await screen.findByRole('heading', { name: 'Compare countries' }),
  ).toBeInTheDocument()
  expect(screen.getAllByText('Coverage excluded').length).toBeGreaterThan(0)
  expect(screen.getAllByLabelText('Locality-derived criterion').length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Harbor City/).length).toBeGreaterThan(0)
  expect(screen.getAllByLabelText(/Data not available: Source value missing/).length).toBeGreaterThan(0)
  expect(screen.queryByText(/come directly from the API/)).not.toBeInTheDocument()
})

test('renders empty rankings and structured API failures without fallback data', async () => {
  installApi({ ranking: { ...rankingFixture, rankings: [] } })
  const first = renderApp()
  expect(
    await screen.findByRole('heading', { name: 'No ranking results' }),
  ).toBeInTheDocument()
  first.unmount()

  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      jsonResponse(
        {
          error: {
            code: 'release_unavailable',
            message: 'A validated active release is unavailable.',
            details: {},
            request_id: null,
          },
        },
        503,
      ),
    ),
  )
  renderApp()
  expect(
    await screen.findByRole('heading', {
      name: 'Country data is temporarily unavailable',
    }),
  ).toBeInTheDocument()
})

test('renders and keyboard-operates nine grouped Opportunity Filters without weights', async () => {
  installApi()
  const user = userEvent.setup()
  renderApp()

  const heading = await screen.findByRole('heading', { name: 'Opportunity filters' })
  const panel = heading.closest('section')!
  const careerGroup = within(panel).getByText('Career')
  const educationGroup = within(panel).getByText('Education')
  expect(careerGroup.closest('details')).not.toHaveAttribute('open')
  expect(educationGroup.closest('details')).not.toHaveAttribute('open')
  expect(within(panel).getByLabelText('0 of 5 filters selected')).toHaveTextContent(
    '0/5 selected',
  )
  expect(within(panel).getByLabelText('0 of 4 filters selected')).toHaveTextContent(
    '0/4 selected',
  )
  expect(within(panel).queryByText('Education and research universities')).not.toBeInTheDocument()
  await user.click(careerGroup)
  await user.click(educationGroup)
  expect(within(panel).getAllByRole('checkbox')).toHaveLength(9)
  expect(within(panel).queryByRole('slider')).not.toBeInTheDocument()
  expect(
    within(panel).getByText(
      'All selected opportunity filters must have a verified strong signal.',
    ),
  ).toBeInTheDocument()

  const technology = within(panel).getByRole('checkbox', {
    name: /Technology and software/,
  })
  technology.focus()
  await user.keyboard(' ')
  expect(technology).toBeChecked()
  expect(within(panel).getByText('1 selected')).toBeInTheDocument()
  expect(within(panel).getByLabelText('1 of 5 filters selected')).toHaveTextContent(
    '1/5 selected',
  )
  expect(within(panel).getByLabelText('0 of 4 filters selected')).toHaveTextContent(
    '0/4 selected',
  )
  await user.click(
    within(panel).getByRole('button', { name: 'Clear all opportunity filters' }),
  )
  expect(technology).not.toBeChecked()

  expect(within(panel).queryByText('How opportunity filters work')).not.toBeInTheDocument()
  await user.click(
    within(panel).getByRole('button', {
      name: 'Open criteria and sources for opportunity filters',
    }),
  )
  const dialog = screen.getByRole('dialog', { name: 'Criteria and sources' })
  expect(
    within(dialog).getByText(/Insufficient evidence is not negative/),
  ).toBeInTheDocument()
  expect(
    within(dialog).getByText(/does not establish teaching quality, programme availability/),
  ).toBeInTheDocument()
})

test('serializes one and multiple required filters, preserves scores, and exposes removable active chips', async () => {
  const filtered = rankingWithOpportunityFilters()
  const requests = installApi({ subsequentRanking: filtered })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(requests.find((request) => request.path.endsWith('/rankings'))?.body).toEqual({
    preference_preset_id: 'balanced',
  })
  await user.click(
    screen.getByRole('checkbox', { name: /Technology and software/ }),
  )
  await user.click(
    screen.getByRole('checkbox', { name: /Skilled-trades or construction/ }),
  )
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))

  await screen.findByRole('heading', {
    name: '2 countries match all selected opportunity filters',
  })
  expect(requests.filter((request) => request.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    preference_preset_id: 'balanced',
    opportunity_filters: {
      mode: 'ALL_REQUIRED',
      required_filter_ids: [
        'skilled_trades_construction_opportunity',
        'technology_software_opportunity',
      ],
    },
  })
  expect(screen.getAllByText('8.5 / 10').length).toBeGreaterThan(0)
  expect(
    screen.getByRole('button', {
      name: 'Remove Technology and software employment ecosystem opportunity filter',
    }),
  ).toBeInTheDocument()
  expect(screen.getAllByText(/Matches 2 filters/).length).toBeGreaterThan(0)
  expect(screen.getAllByText('Strong signal not established').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Insufficient evidence').length).toBeGreaterThan(0)

  expect({
    heading: screen.getByRole('heading', {
      level: 3,
      name: '2 countries match all selected opportunity filters',
    }).textContent,
    returned: filtered.rankings.map((country) => ({
      rank: country.rank,
      baseRank: country.base_rank,
      score: country.total_score,
    })),
    exclusions: filtered.assessments.opportunity.excluded_counts_by_state,
  }).toMatchInlineSnapshot(`
    {
      "exclusions": {
        "INSUFFICIENT_EVIDENCE": 1,
        "STRONG_SIGNAL_NOT_ESTABLISHED": 2,
      },
      "heading": "2 countries match all selected opportunity filters",
      "returned": [
        {
          "baseRank": 1,
          "rank": 1,
          "score": 8.5,
        },
        {
          "baseRank": 2,
          "rank": 2,
          "score": 8.1,
        },
      ],
    }
  `)
})

test('explains excluded states and country evidence without negative or applicant-success claims', async () => {
  const filtered = rankingWithOpportunityFilters()
  const requests = installApi({
    subsequentRanking: filtered,
    detailsForCode: (code) =>
      countryDetailsWithOpportunityFixture(Number(code.slice(-1))),
  })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await user.click(
    screen.getByRole('checkbox', { name: /Technology and software/ }),
  )
  await user.click(
    screen.getByRole('checkbox', { name: /Skilled-trades or construction/ }),
  )
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  await user.click(await screen.findByText(/Review 3 opportunity-filter excluded countries/))
  await user.click(screen.getByRole('button', { name: 'Country 3' }))

  expect(
    await screen.findByRole('heading', { name: 'Opportunity filters', level: 3 }),
  ).toBeInTheDocument()
  expect(screen.getByText('Both: skilled trades and construction')).toBeInTheDocument()
  expect(
    screen.getAllByText(
      /Comparable evidence was available, but it did not cross Konsider’s strong-ecosystem threshold/,
    ).length,
  ).toBeGreaterThan(0)
  expect(
    screen.getAllByText(/does not currently have enough comparable evidence to assess/).length,
  ).toBeGreaterThan(0)
  expect(screen.getAllByText(/covers human health and social work/i).length).toBeGreaterThan(0)
  expect(
    screen.getAllByText(/does not establish teaching quality, programme availability/).length,
  ).toBeGreaterThan(0)
  expect(screen.queryByText(/^no opportunity$/i)).not.toBeInTheDocument()
  expect(screen.queryByText(/^(weak|bad) country$/i)).not.toBeInTheDocument()

  const detailsRequest = requests.find((request) => request.path.includes('/countries/C02/'))
  expect(detailsRequest?.body).toMatchObject({
    opportunity_filters: {
      mode: 'ALL_REQUIRED',
      required_filter_ids: [
        'skilled_trades_construction_opportunity',
        'technology_software_opportunity',
      ],
    },
  })
})

test('renders a non-error zero-match state and removes one filter without changing applied weights', async () => {
  const empty = rankingWithOpportunityFilters(['technology_software_opportunity'], true)
  const requests = installApi({ subsequentRanking: empty })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await user.click(
    screen.getByRole('checkbox', { name: /Technology and software/ }),
  )
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))

  expect(
    (
      await screen.findAllByRole('heading', {
        name: 'No country matches every selected opportunity filter',
      })
    ).length,
  ).toBeGreaterThan(0)
  expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  expect(
    screen.getAllByText(/some countries may have insufficient comparable evidence/).length,
  ).toBeGreaterThan(0)
  await user.click(
    screen.getByRole('button', { name: 'Remove Technology and software' }),
  )
  await waitFor(() =>
    expect(requests.filter((request) => request.path.endsWith('/rankings'))).toHaveLength(3),
  )
  expect(requests.filter((request) => request.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    preference_preset_id: 'balanced',
  })
})

test('keeps Opportunity Filter evidence separate in desktop and mobile comparison presentations', async () => {
  const filtered = rankingWithOpportunityFilters([
    'skilled_trades_construction_opportunity',
  ])
  const requests = installApi({
    subsequentRanking: filtered,
    comparison: comparisonWithOpportunityFixture,
  })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await user.click(
    screen.getByRole('checkbox', { name: /Skilled-trades or construction/ }),
  )
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  const comparisonBoxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  await user.click(comparisonBoxes[0])
  await user.click(comparisonBoxes[1])
  await user.click(screen.getByRole('button', { name: 'Compare selected (2)' }))

  expect(await screen.findByRole('heading', { name: 'Compare countries' })).toBeInTheDocument()
  expect(screen.getAllByText('Opportunity filter').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Verified strong signal').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Strong signal not established').length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Both: skilled trades and construction/).length).toBeGreaterThan(0)
  expect(screen.getByText(/Opportunity-filter excluded countries retain/)).toBeInTheDocument()
  expect(requests.find((request) => request.path.endsWith('/comparisons'))?.body).toMatchObject({
    opportunity_filters: {
      mode: 'ALL_REQUIRED',
      required_filter_ids: ['skilled_trades_construction_opportunity'],
    },
  })
})

test('clears selected comparison countries and shows no locality context as a hyphen', async () => {
  installApi({ ranking: rankingForLocalityStatus('NO_ACTIVE_LOCALITY_CRITERIA') })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(screen.getAllByText('-').length).toBeGreaterThan(0)
  const comparisonBoxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  await user.click(comparisonBoxes[0])
  await user.click(comparisonBoxes[1])
  expect(screen.getByRole('button', { name: 'Compare selected (2)' })).toBeEnabled()

  await user.click(screen.getByRole('button', { name: 'Clear selection' }))

  expect(comparisonBoxes[0]).not.toBeChecked()
  expect(comparisonBoxes[1]).not.toBeChecked()
  expect(screen.getByRole('button', { name: 'Compare selected (0)' })).toBeDisabled()
  expect(screen.queryByRole('button', { name: 'Clear selection' })).not.toBeInTheDocument()
})

test('opens and cancels the guided situation flow without changing the ranking request', async () => {
  const requests = installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  const opener = screen.getByRole('button', { name: 'Add your situation' })
  await user.click(opener)
  const dialog = screen.getByRole('dialog', { name: 'Your situation' })
  expect(within(dialog).getByText(/Nothing is selected automatically/)).toBeInTheDocument()
  await user.click(within(dialog).getByRole('button', { name: 'Cancel' }))
  expect(screen.queryByRole('dialog', { name: 'Your situation' })).not.toBeInTheDocument()
  expect(opener).toHaveFocus()
  expect(requests.filter((request) => request.path.endsWith('/rankings'))).toHaveLength(1)
})

test('progressively selects a TFC, preserves unknown offer state, and renders input requests', async () => {
  const requests = installApi({ subsequentRanking: rankingWithFeasibility })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await configureWorkSituation(user)

  await screen.findByRole('heading', { name: 'Feasibility checks', level: 3 })
  expect(screen.getByText('Additional inputs requested')).toBeInTheDocument()
  expect(screen.getAllByText('More information required').length).toBeGreaterThan(0)
  const request = requests.filter((item) => item.path.endsWith('/rankings')).at(-1)
  expect(request?.body).toMatchObject({
    preference_preset_id: 'balanced',
    feasibility: {
      tfc_ids: ['skilled_work_route_feasibility'],
      mode: 'ASSESS_ONLY',
      profile_context: {
        occupation: {
          user_text: 'Fictional analyst',
          mapping_state: 'UNRESOLVED',
        },
        qualifications: [{ level: 'MASTERS' }],
      },
      scenario_context: {
        purpose: 'WORK',
        target_country_codes: ['DEU'],
        target_date: '2026-08-05',
        job_offer: { state: 'UNKNOWN' },
      },
    },
  })
  expect(sessionStorage.getItem('konsider:situation:session')).toContain(
    'skilled_work_route_feasibility',
  )
  expect(localStorage.getItem('konsider:situation:remembered')).toBeNull()
})

test('uses one situation snapshot for route details and country comparison', async () => {
  const requests = installApi({
    subsequentRanking: rankingWithFeasibility,
    comparison: comparisonWithFeasibilityFixture,
    detailsForCode: (code) => countryDetailsWithFeasibilityFixture(Number(code.slice(-1))),
  })
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await configureWorkSituation(user, { includeOffer: true })
  expect((await screen.findAllByText('Conditional route match found')).length).toBeGreaterThan(0)

  await user.click(screen.getAllByRole('button', { name: 'View country details' })[0])
  expect(
    (await screen.findAllByRole('heading', { name: 'Feasibility checks', level: 3 })).length,
  ).toBeGreaterThan(1)
  expect(screen.getByText('Fictional skilled work route')).toBeInTheDocument()
  expect(screen.getByText(/external authority confirmation/i)).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Close country details' }))

  const boxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  await user.click(boxes[0])
  await user.click(boxes[1])
  await user.click(screen.getByRole('button', { name: 'Compare selected (2)' }))
  expect(await screen.findByRole('heading', { name: 'Compare countries' })).toBeInTheDocument()
  expect(screen.getAllByText('Feasibility check').length).toBeGreaterThan(0)
  const comparisonRequest = requests.find((item) => item.path.endsWith('/comparisons'))
  expect(comparisonRequest?.body).toMatchObject({
    feasibility: {
      tfc_ids: ['skilled_work_route_feasibility'],
      scenario_context: { target_date: '2026-08-05' },
    },
  })
})

test('restores session context and stores it locally only after explicit opt-in', async () => {
  const firstRequests = installApi({ subsequentRanking: rankingWithFeasibility })
  const user = userEvent.setup()
  const first = renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await configureWorkSituation(user, { remember: true, includeOffer: true })
  expect((await screen.findAllByText('Conditional route match found')).length).toBeGreaterThan(0)
  expect(localStorage.getItem('konsider:situation:remembered')).toContain(
    'konsider-situation-storage-1.0',
  )
  expect(firstRequests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(2)

  first.unmount()
  const restoredRequests = installApi({ ranking: rankingWithFeasibility })
  renderApp()
  expect(await screen.findByRole('button', { name: 'Edit situation' })).toBeInTheDocument()
  await waitFor(() =>
    expect(restoredRequests.find((item) => item.path.endsWith('/rankings'))?.body).toHaveProperty(
      'feasibility',
    ),
  )
})

test('validates imported versions and keeps TFC catalog failure non-blocking', async () => {
  installApi({ tfcCatalog: null })
  const unavailableApp = renderApp()
  expect(await screen.findByRole('heading', { name: 'Country ranking' })).toBeInTheDocument()
  expect(
    screen.getByText('Feasibility checks are temporarily unavailable. Country ranking still works.'),
  ).toBeInTheDocument()

  unavailableApp.unmount()
  sessionStorage.clear()
  localStorage.clear()
  installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findAllByRole('heading', { name: 'Country ranking' })
  const addButtons = screen.getAllByRole('button', { name: 'Add your situation' })
  await user.click(addButtons.at(-1)!)
  const dialog = screen.getByRole('dialog', { name: 'Your situation' })
  await user.click(within(dialog).getByRole('button', { name: /Review/ }))
  const file = new File(
    [JSON.stringify({ schema_version: 'konsider-situation-9.0' })],
    'old-situation.json',
    { type: 'application/json' },
  )
  Object.defineProperty(file, 'text', {
    value: async () => JSON.stringify({ schema_version: 'konsider-situation-9.0' }),
  })
  const importInput = dialog.querySelector<HTMLInputElement>('input[type="file"]')
  expect(importInput).not.toBeNull()
  await user.upload(importInput!, file)
  expect(await within(dialog).findByRole('alert')).toHaveTextContent(
    'This file is not konsider-situation-1.0.',
  )
})
