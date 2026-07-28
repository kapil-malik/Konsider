import { expect, test, type Page, type Route } from '@playwright/test'

import {
  catalogFixture,
  comparisonFixture,
  countryMetricFixture,
  rankingFixture,
} from '../src/test/fixtures'

async function json(route: Route, body: unknown, status = 200) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

async function mockApi(
  page: Page,
  requests: Array<{ path: string; body?: unknown }> = [],
  ranking = rankingFixture,
) {
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push({ path: url.pathname, body: request.postDataJSON() })
    if (url.pathname.endsWith('/catalog')) return json(route, catalogFixture)
    if (url.pathname.endsWith('/rankings')) return json(route, ranking)
    if (url.pathname.includes('/countries/')) return json(route, countryMetricFixture)
    if (url.pathname.endsWith('/comparisons')) return json(route, comparisonFixture)
    return json(route, { error: { code: 'not_found', message: 'Not found' } }, 404)
  })
}

test('initial guest ranking and explicit priority update', async ({ page }) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests)
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Country ranking' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Guest/ })).toBeVisible()
  const rankingCallsBeforeApply = requests.filter((item) => item.path.endsWith('/rankings')).length
  await page.getByLabel('Preference profile').selectOption('safety_profile')
  await page.getByRole('slider', { name: 'Air quality' }).press('ArrowRight')
  await expect(page.getByLabel('Preference profile')).toHaveValue('__custom')
  await page.getByRole('button', { name: 'Apply priorities' }).click()

  await expect
    .poll(() => requests.filter((item) => item.path.endsWith('/rankings')).length)
    .toBe(rankingCallsBeforeApply + 1)
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    weights: { air: 0.6, infrastructure: 0.8, jobs: 0.4 },
  })
})

test('country detail exposes a public source link', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')
  await page.locator('.ranking-table tbody tr[data-country-code="C00"]').click()

  await expect(page.getByRole('heading', { name: 'Country 1', level: 2 })).toBeVisible()
  const source = page.getByRole('link', { name: /View Public Data Publisher source/ }).first()
  await expect(source).toHaveAttribute('href', 'https://example.com/public-data')
  await expect(source).toHaveAttribute('target', '_blank')
})

test('selects countries, compares, and returns without refetching ranking', async ({ page }) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests)
  await page.goto('/')
  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await boxes.nth(2).check()
  await page.getByRole('button', { name: 'Compare selected (3)' }).click()

  await expect(page.getByRole('heading', { name: 'Compare countries' })).toBeVisible()
  const rankingCallsBeforeBack = requests.filter((item) => item.path.endsWith('/rankings')).length
  await page.getByRole('button', { name: '← Back to rankings' }).click()
  await expect(page.getByRole('heading', { name: 'Country ranking' })).toBeVisible()
  expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(
    rankingCallsBeforeBack,
  )
})

test('opens and closes Data & Sources from the Guest menu', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')
  await page.getByRole('button', { name: /Guest/ }).click()
  await page.getByRole('menuitem', { name: 'Data & Sources' }).click()
  const dialog = page.getByRole('dialog', { name: 'Data & Sources' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'UHC service coverage' })).toBeVisible()
  await dialog.getByRole('button', { name: 'Close Data and Sources' }).click()
  await expect(dialog).toBeHidden()
})

test('search and region filters update visible and total result counts', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')

  await page.getByRole('searchbox', { name: 'Search countries' }).fill('C03')
  await expect(page.getByText(/Showing 1 of 5 returned countries/)).toBeVisible()
  await expect(page.locator('.ranking-table tbody tr[data-country-code="C03"]')).toBeVisible()

  await page.getByRole('combobox', { name: 'Region' }).selectOption('Region 2')
  await expect(page.getByRole('heading', { name: 'No countries match these filters' })).toBeVisible()
  await expect(page.getByText(/Showing 0 of 5 returned countries/)).toBeVisible()
})

test('shows a controlled unavailable-release state', async ({ page }) => {
  await page.route('**/api/v1/catalog', (route) =>
    json(
      route,
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
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Country data is temporarily unavailable' }),
  ).toBeVisible()
})

test('mobile keeps detailed scores, details, and comparison complete', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(page)
  await page.goto('/')
  await page.getByLabel('Show detailed scores').check()
  await expect(
    page.locator('.ranking-card[data-country-code="C00"] .mobile-score-list dt').filter({
      hasText: 'Air quality',
    }),
  ).toBeVisible()
  await page.locator('.ranking-card[data-country-code="C00"] .text-button').click()
  await expect(page.getByRole('heading', { name: 'Country 1', level: 2 })).toBeVisible()
  await page.getByRole('button', { name: 'Close country details' }).click()

  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  await expect(page.getByRole('heading', { name: 'Overall affinity' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Air quality' })).toBeVisible()
})

test('mobile long list keeps the final country accessible through search', async ({ page }) => {
  const longRanking = {
    ...rankingFixture,
    total_eligible_country_count: 91,
    returned_result_count: 91,
    rankings: Array.from({ length: 91 }, (_, index) => ({
      ...rankingFixture.rankings[0],
      rank: index + 1,
      country_code: `X${String(index).padStart(2, '0')}`,
      country_name: `Long list country ${index + 1}`,
      region: index % 2 ? 'Region A' : 'Region B',
    })),
  }
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(page, [], longRanking)
  await page.goto('/')

  await page.getByRole('searchbox', { name: 'Search countries' }).fill('Long list country 91')
  await expect(page.locator('.ranking-card[data-country-code="X90"]')).toBeVisible()
  await expect(page.getByText(/Showing 1 of 91 returned countries/)).toBeVisible()
})
