import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import App from './App'
import type { CatalogV2, ComparisonV2, RankingV2 } from './api/types'
import {
  catalogFixture,
  comparisonFixture,
  comparisonWithUnavailableFixture,
  countryDetailsFixture,
  coverageWarningRanking,
  rankingFixture,
  rankingForLocalityStatus,
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
  subsequentRanking = ranking,
}: {
  ranking?: RankingV2
  comparison?: ComparisonV2
  catalog?: CatalogV2
  subsequentRanking?: RankingV2
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
      if (url.pathname.endsWith('/rankings')) {
        rankingCalls += 1
        return jsonResponse(rankingCalls === 1 ? ranking : subsequentRanking)
      }
      if (url.pathname.includes('/countries/')) {
        const excluded = url.pathname.includes('/C04/')
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

test('renders API-owned coverage, scope, experimental, and locality threshold indicators', async () => {
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
  expect(screen.getAllByText('⌖ Locality-derived').length).toBeGreaterThan(0)
  expect(screen.getByText('◇ Experimental')).toBeInTheDocument()
  expect(screen.getByText('! Limited coverage')).toBeInTheDocument()
  expect(screen.getByText('4/5 countries')).toBeInTheDocument()
  expect(
    screen.getByText('Locality compatibility will be assessed when applied.'),
  ).toBeInTheDocument()

  const heat = screen.getByRole('slider', { name: 'Extreme heat exposure' })
  heat.focus()
  fireEvent.keyDown(heat, { key: 'ArrowLeft' })
  expect(heat).toHaveValue('0.4')
  expect(
    screen.getByText(/Locality provenance remains available; prominent analysis begins at Medium/),
  ).toBeInTheDocument()
  expect(
    screen.queryByText('Locality compatibility will be assessed when applied.'),
  ).not.toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: /Guest/ }))
  await user.click(screen.getByRole('menuitem', { name: 'Data & Sources' }))
  const dialog = screen.getByRole('dialog', { name: 'Data & Sources' })
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
  renderApp()
  expect(
    await screen.findByRole('status', { name: `Locality status: ${label}` }),
  ).toBeInTheDocument()
})

test('keeps coverage, locality, and profile summaries separate', async () => {
  installApi({ ranking: coverageWarningRanking })
  renderApp()
  expect(
    await screen.findByRole('status', {
      name: 'Coverage status: Limited-coverage ranking',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('status', {
      name: 'Locality status: Strong options are in different localities',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('status', {
      name: 'Profile status: No applicant profile assessed',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getAllByText(/affinity score is unchanged/i).length,
  ).toBeGreaterThan(0)
})

test('shows locality names, detailed derivation, policy, source, period, and caveat', async () => {
  installApi()
  const user = userEvent.setup()
  renderApp()
  await screen.findByRole('heading', { name: 'Country ranking' })

  expect(screen.getAllByText('Best common: Harbor City 1').length).toBeGreaterThan(0)
  await user.click(screen.getByLabelText('Show detailed evidence'))
  const heatDetails = screen.getAllByText(/Locality-derived/, { selector: 'summary' })[0]
  await user.click(heatDetails)
  expect(screen.getAllByText(/Harbor City 1 \(8.8\)/).length).toBeGreaterThan(0)
  expect(screen.getAllByText('top-two:heat').length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Public Data Publisher · 2025-01-01 to 2025-12-31/).length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Extreme heat exposure caveat/).length).toBeGreaterThan(0)
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
  expect(screen.getAllByText('⌖ Locality-derived').length).toBeGreaterThan(0)
  expect(screen.getAllByText(/Harbor City/).length).toBeGreaterThan(0)
  expect(screen.getAllByLabelText(/Data not available: Source value missing/).length).toBeGreaterThan(0)
  expect(screen.getByText(/No partial aggregate is fabricated/)).toBeInTheDocument()
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
