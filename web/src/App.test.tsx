import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import App from './App'
import {
  catalogFixture,
  comparisonFixture,
  comparisonWithUnavailableFixture,
  countryMetricFixture,
  rankingForStatus,
  rankingFixture,
} from './test/fixtures'

type RecordedRequest = { path: string; method: string; body?: unknown }

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function installHappyApi(
  ranking = rankingFixture,
  comparison = comparisonFixture,
  subsequentRanking = ranking,
) {
  const requests: RecordedRequest[] = []
  let rankingCalls = 0
  const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = new URL(typeof input === 'string' ? input : input instanceof URL ? input : input.url)
    const body = init?.body ? JSON.parse(String(init.body)) : undefined
    requests.push({ path: url.pathname, method: init?.method ?? 'GET', body })
    if (url.pathname.endsWith('/catalog')) return jsonResponse(catalogFixture)
    if (url.pathname.endsWith('/rankings')) {
      rankingCalls += 1
      return jsonResponse(rankingCalls === 1 ? ranking : subsequentRanking)
    }
    if (url.pathname.includes('/countries/')) return jsonResponse(countryMetricFixture)
    if (url.pathname.endsWith('/comparisons')) return jsonResponse(comparison)
    return jsonResponse({ error: { code: 'not_found', message: 'Not found' } }, 404)
  })
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

test('renders catalog-owned controls, profile options, flags, guest help, and all source metadata', async () => {
  installHappyApi()
  const user = userEvent.setup()
  renderApp()

  expect(await screen.findByRole('heading', { name: 'What matters most?' })).toBeInTheDocument()
  expect(screen.getAllByRole('slider')).toHaveLength(3)
  expect(screen.getByRole('slider', { name: 'Air quality' })).toHaveValue('1')
  expect(screen.getByRole('slider', { name: 'Overall job-market opportunity' })).toHaveValue('0.4')
  expect(screen.queryByRole('slider', { name: 'UHC service coverage' })).not.toBeInTheDocument()
  expect(screen.getByRole('option', { name: 'Safety profile' })).toBeInTheDocument()
  expect(screen.getByText('Experimental')).toBeInTheDocument()
  expect(screen.getByText('Limited coverage')).toBeInTheDocument()
  expect(screen.getByText('4/5 countries')).toBeInTheDocument()
  expect(screen.getByText('Not active in the ranking at this setting.')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: /Guest/ }))
  expect(screen.getByText('Your priorities and selections are not saved.')).toBeInTheDocument()
  await user.click(screen.getByRole('menuitem', { name: 'Data & Sources' }))
  const dialog = screen.getByRole('dialog', { name: 'Data & Sources' })
  expect(within(dialog).getByText('UHC service coverage')).toBeInTheDocument()
  expect(within(dialog).getByText('Unavailable')).toBeInTheDocument()
  expect(within(dialog).getAllByText('Public Data Publisher')).toHaveLength(4)
  expect(within(dialog).getByText(/latest 2021/)).toBeInTheDocument()
  await user.click(within(dialog).getByRole('button', { name: 'Close Data and Sources' }))
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
})

test('uses profile IDs until a keyboard edit creates Custom, waits for Apply, and supports Undo', async () => {
  const requests = installHappyApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  const profile = screen.getByLabelText('Preference profile')
  await user.selectOptions(profile, 'safety_profile')
  expect(screen.getByRole('slider', { name: 'Air quality' })).toHaveValue('0.4')
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  await waitFor(() => expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(2))
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    profile_id: 'safety_profile',
  })

  let airSlider = screen.getByRole('slider', { name: 'Air quality' })
  airSlider.focus()
  fireEvent.keyDown(airSlider, { key: 'ArrowRight' })
  expect(profile).toHaveValue('__custom')
  expect(airSlider).toHaveAttribute('aria-valuetext', 'Medium, 0.6')
  expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(2)

  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  await waitFor(() => expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(3))
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    weights: { air: 0.6, infrastructure: 0.8, jobs: 0.4 },
  })

  airSlider = screen.getByRole('slider', { name: 'Air quality' })
  airSlider.focus()
  fireEvent.keyDown(airSlider, { key: 'ArrowLeft' })
  expect(airSlider).toHaveValue('0.4')
  await user.click(screen.getByRole('button', { name: 'Undo changes' }))
  expect(airSlider).toHaveValue('0.6')
})

test('shows dynamic details, loads country evidence, caps comparison at four, and restores ranking mode', async () => {
  installHappyApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(screen.getAllByText('8.5 / 10').length).toBeGreaterThan(0)
  expect(screen.queryByText('85%')).not.toBeInTheDocument()
  await user.click(screen.getByLabelText('Show detailed scores'))
  expect(screen.getByRole('columnheader', { name: 'Environment' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: /Infrastructure/ })).toBeInTheDocument()

  await user.click(screen.getAllByRole('button', { name: 'View country details' })[0])
  expect(await screen.findByRole('heading', { name: 'Country 1', level: 2 })).toBeInTheDocument()
  expect(screen.getAllByText(/72.4 index 0 100/).length).toBeGreaterThan(0)
  expect(screen.getAllByRole('link', { name: /View Public Data Publisher source/ }).length).toBeGreaterThan(0)

  const comparisonBoxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  for (const checkbox of comparisonBoxes.slice(0, 4)) await user.click(checkbox)
  await user.click(comparisonBoxes[4])
  expect(screen.getByText(/compare up to four countries/i)).toBeInTheDocument()
  expect(comparisonBoxes[4]).not.toBeChecked()

  await user.click(screen.getByRole('button', { name: 'Compare selected (4)' }))
  expect(await screen.findByRole('heading', { name: 'Compare countries' })).toBeInTheDocument()
  expect(screen.queryByRole('heading', { name: 'Country ranking' })).not.toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: '← Back to rankings' }))
  expect(screen.getByRole('heading', { name: 'Country ranking' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Country 1', level: 2 })).toBeInTheDocument()
})

test('renders an empty ranking response without inventing countries', async () => {
  installHappyApi({ ...rankingFixture, rankings: [], returned_result_count: 0 })
  renderApp()
  expect(await screen.findByRole('heading', { name: 'No ranking results' })).toBeInTheDocument()
  expect(screen.queryByText('Country 1')).not.toBeInTheDocument()
})

test('filters the catalog-driven ranking by country name, code, and region with visible counts', async () => {
  installHappyApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  const search = screen.getByRole('searchbox', { name: 'Search countries' })
  const region = screen.getByRole('combobox', { name: 'Region' })
  expect(screen.getByText(/Showing 5 of 5 returned countries · 5 of 5 ranked/)).toBeInTheDocument()

  await user.type(search, 'C03')
  expect(screen.getAllByText('Country 4').length).toBeGreaterThan(0)
  expect(screen.queryByText('Country 1')).not.toBeInTheDocument()
  expect(screen.getByText(/Showing 1 of 5 returned countries · 5 of 5 ranked/)).toBeInTheDocument()

  await user.selectOptions(region, 'Region 2')
  expect(screen.getByRole('heading', { name: 'No countries match these filters' })).toBeInTheDocument()
  expect(screen.getByText(/Showing 0 of 5 returned countries · 5 of 5 ranked/)).toBeInTheDocument()

  await user.clear(search)
  expect(screen.getAllByText('Country 2').length).toBeGreaterThan(0)
  expect(screen.queryByText('Country 4')).not.toBeInTheDocument()
  expect(screen.getByText(/Showing 1 of 5 returned countries · 5 of 5 ranked/)).toBeInTheDocument()
})

test.each([
  ['NO_PARTIAL_CRITERIA_ACTIVE', 'Full-coverage ranking'],
  ['FULL_COVERAGE', 'Full coverage'],
  ['ROBUST_TOP_K', 'Robust top results'],
  ['POTENTIALLY_AFFECTED', 'Recommendations may be affected'],
  ['BASELINE_TOP_K_EXCLUDED', 'A baseline top country is excluded'],
  ['COVERAGE_LIMIT_EXCEEDED', 'Coverage limit reached'],
] as const)('renders the %s uncertainty state from the API', async (status, label) => {
  installHappyApi(rankingForStatus(status))
  renderApp()

  expect(
    await screen.findByRole('status', { name: `Ranking coverage status: ${label}` }),
  ).toBeInTheDocument()
  expect(screen.getByText(label)).toBeInTheDocument()
})

test('shows excluded-country diagnostics and available evidence without inventing a score', async () => {
  installHappyApi(rankingForStatus('ROBUST_TOP_K'))
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(screen.queryByText('Country 5', { selector: '.ranking-table strong' })).not.toBeInTheDocument()
  await user.click(screen.getByText('Review 1 excluded country'))
  expect(screen.getByText('Rank 2, score 8.00')).toBeInTheDocument()
  expect(screen.getByText(/Overall job-market opportunity: Missing/)).toBeInTheDocument()
  expect(screen.getByText('No', { selector: '.excluded-country-card dd' })).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Country 5' }))
  expect(await screen.findByRole('heading', { name: 'Country 5', level: 2 })).toBeInTheDocument()
  expect(screen.getByText('Not ranked for this profile', { selector: '.unranked-country-notice strong' })).toBeInTheDocument()
  expect(screen.queryByText(/Rank .*Country 5/)).not.toBeInTheDocument()
})

test('keeps multiple excluded countries collapsed and labels baseline-boundary membership', async () => {
  const oneExcluded = rankingForStatus('BASELINE_TOP_K_EXCLUDED')
  const template = oneExcluded.excluded_countries[0]
  const manyExcluded = {
    ...oneExcluded,
    eligible_universe_size: 2,
    total_eligible_country_count: 2,
    excluded_country_count: 3,
    rankings: oneExcluded.rankings.slice(0, 2),
    returned_result_count: 2,
    excluded_countries: ['C02', 'C03', 'C04'].map((countryCode, index) => ({
      ...template,
      country_code: countryCode,
      country_name: `Country ${index + 3}`,
      r0_rank: index + 2,
      baseline_top_k_member: index === 0,
    })),
  }
  installHappyApi(manyExcluded)
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  const details = screen.getByText('Review 3 excluded countries').closest('details')
  expect(details).not.toHaveAttribute('open')
  await user.click(screen.getByText('Review 3 excluded countries'))
  expect(screen.getByText('Baseline top 5')).toBeInTheDocument()
  expect(within(details as HTMLElement).getAllByText('Not ranked for this profile')).toHaveLength(3)
})

test('loads the 91-country-style baseline from the API without calculating it in the browser', async () => {
  const requests = installHappyApi(
    rankingForStatus('ROBUST_TOP_K'),
    comparisonFixture,
    rankingFixture,
  )
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  await user.click(screen.getByRole('button', { name: 'View full-coverage baseline' }))
  expect(await screen.findByText(/Full-coverage baseline · Rank among 5 countries/)).toBeInTheDocument()
  await waitFor(() => expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(2))
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    weights: { air: 1, infrastructure: 1, jobs: 0 },
    top_k: 5,
  })
  expect(screen.getByText(/Showing 5 of 5 returned countries · 5 of 5 ranked/)).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Return to conditional ranking' }))
  expect(screen.getByText(/Rank among 4 eligible countries/)).toBeInTheDocument()
})

test('comparison keeps available cells and marks missing data and aggregate scores', async () => {
  installHappyApi(rankingFixture, comparisonWithUnavailableFixture)
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  const comparisonBoxes = screen.getAllByRole('checkbox', { name: /Select Country/ })
  for (const checkbox of comparisonBoxes.slice(0, 4)) await user.click(checkbox)
  await user.click(screen.getByRole('button', { name: 'Compare selected (4)' }))

  expect(await screen.findByRole('heading', { name: 'Compare countries' })).toBeInTheDocument()
  expect(screen.getAllByText('Not ranked for this profile').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Data not available').length).toBeGreaterThan(0)
  expect(screen.getAllByLabelText(/Data not available: Cov source record missing/).length).toBeGreaterThan(0)
  expect(screen.getByText(/no partial affinity score is fabricated/i)).toBeInTheDocument()
})

test('uses structured 503 and network-safe catalog errors', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(
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
    )
  vi.stubGlobal('fetch', fetchMock)
  const first = renderApp()
  expect(await screen.findByRole('heading', { name: 'Country data is temporarily unavailable' })).toBeInTheDocument()
  first.unmount()

  fetchMock.mockReset()
  fetchMock.mockRejectedValue(new TypeError('offline'))
  renderApp()
  expect(await screen.findByRole('heading', { name: 'Konsider cannot reach the API' })).toBeInTheDocument()
})

test('keeps a successful ranking visible when a structured 422 apply fails', async () => {
  let rankingCalls = 0
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string | URL | Request) => {
      const url = new URL(typeof input === 'string' ? input : input instanceof URL ? input : input.url)
      if (url.pathname.endsWith('/catalog')) return jsonResponse(catalogFixture)
      if (url.pathname.endsWith('/rankings')) {
        rankingCalls += 1
        if (rankingCalls === 1) return jsonResponse(rankingFixture)
        return jsonResponse(
          {
            error: {
              code: 'invalid_weight',
              message: 'The submitted weights are invalid.',
              details: {},
              request_id: null,
            },
          },
          422,
        )
      }
      return jsonResponse({})
    }),
  )
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })
  await user.selectOptions(screen.getByLabelText('Preference profile'), 'safety_profile')
  await user.click(screen.getByRole('button', { name: 'Apply priorities' }))
  expect(await screen.findByRole('heading', { name: 'Those priorities could not be applied' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Country ranking' })).toBeInTheDocument()
  expect(screen.getAllByText('8.5 / 10').length).toBeGreaterThan(0)
})
