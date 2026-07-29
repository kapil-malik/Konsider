import { expect, test, type Page, type Route } from '@playwright/test'

import {
  catalogFixture,
  comparisonFixture,
  countryDetailsFixture,
  coverageWarningRanking,
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
  await page.route('http://127.0.0.1:8000/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push({ path: url.pathname, body: request.postDataJSON() })
    if (url.pathname.endsWith('/catalog')) return json(route, catalogFixture)
    if (url.pathname.endsWith('/rankings')) return json(route, ranking)
    if (url.pathname.includes('/countries/')) {
      const code = url.pathname.split('/countries/')[1]?.split('/')[0] ?? 'C00'
      const index = Number(code.slice(-1))
      const excluded = ranking.assessments.coverage.excluded_countries.some(
        (item) => item.country.country_codes.includes(code),
      )
      return json(route, countryDetailsFixture(Number.isFinite(index) ? index : 0, excluded))
    }
    if (url.pathname.endsWith('/comparisons')) return json(route, comparisonFixture)
    return json(route, { error: { code: 'not_found', message: 'Not found' } }, 404)
  })
}

test('initial guest ranking and explicit priority update use the v2 contract', async ({ page }) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests)
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Country ranking' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Guest/ })).toBeVisible()
  await expect(
    page.getByRole('status', { name: 'Coverage status: Full coverage' }),
  ).toBeVisible()
  await expect(
    page.getByRole('status', { name: 'Locality status: Common locality available' }),
  ).toBeVisible()

  const rankingCallsBeforeApply = requests.filter((item) => item.path.endsWith('/rankings')).length
  await page.getByLabel('Preference preset').selectOption('climate')
  await page.getByRole('slider', { name: 'Air quality' }).press('ArrowRight')
  await expect(page.getByLabel('Preference preset')).toHaveValue('__custom')
  await page.getByRole('button', { name: 'Apply priorities' }).click()

  await expect
    .poll(() => requests.filter((item) => item.path.endsWith('/rankings')).length)
    .toBe(rankingCallsBeforeApply + 1)
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    weights: { air: 0.6, heat: 0.8, jobs: 0.4 },
  })
  expect(requests.some((item) => item.path.startsWith('/api/v1'))).toBe(false)
})

test('country details expose locality derivation and public source evidence', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')
  await page.locator('.ranking-table tbody tr[data-country-code="C00"]').click()

  await expect(page.getByRole('heading', { name: 'Country 1', level: 2 })).toBeVisible()
  await expect(page.getByText('Country score aggregated from locality evidence')).toBeVisible()
  await expect(page.getByText('Contributing localities')).toBeVisible()
  await expect(page.getByText('Aggregation policy')).toBeVisible()
  const source = page.getByRole('link', { name: /View Public Data Publisher source/ }).first()
  await expect(source).toHaveAttribute('href', 'https://example.com/public-data')
  await expect(source).toHaveAttribute('target', '_blank')
})

test('coverage exclusion and locality advice remain distinct', async ({ page }) => {
  await mockApi(page, [], coverageWarningRanking)
  await page.goto('/')

  await expect(
    page.getByRole('status', { name: 'Coverage status: Limited-coverage ranking' }),
  ).toBeVisible()
  await expect(
    page.getByRole('status', {
      name: 'Locality status: Strong options are in different localities',
    }),
  ).toBeVisible()
  await expect(page.getByText(/affinity score is unchanged/i).first()).toBeVisible()
  await page.getByText(/Review 1 coverage-excluded country/).click()
  await page.getByRole('button', { name: 'Country 5' }).click()
  await expect(page.getByText('Coverage excluded · not ranked')).toBeVisible()
  await expect(page.getByText('Unavailable active criterion')).toBeVisible()
  await expect(page.getByText('Strong options are in different localities').first()).toBeVisible()
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
  await expect(page.getByText('Locality-derived').first()).toBeVisible()
  await expect(page.getByText(/Best common: Harbor City/).first()).toBeVisible()
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
  await expect(dialog.getByRole('heading', { name: 'Extreme heat exposure' })).toBeVisible()
  await expect(dialog.getByText(/Previously called: Extreme-weather risk/)).toBeVisible()
  await expect(dialog.getByText(/Locality evidence · Aggregated from localities/)).toBeVisible()
  await expect(dialog.getByText('top-two:heat')).toBeVisible()
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
  await page.route('**/api/v2/catalog', (route) =>
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

test('mobile keeps locality evidence, details, and comparison complete without overflow', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(page)
  await page.goto('/')
  await page.getByLabel('Show detailed evidence').check()
  await expect(
    page
      .locator('.ranking-card[data-country-code="C00"]')
      .getByText('Extreme heat exposure', { exact: true }),
  ).toBeVisible()
  await expect(
    page.locator('.ranking-card[data-country-code="C00"]').getByText('Locality-derived'),
  ).toBeVisible()
  await page.locator('.ranking-card[data-country-code="C00"] .text-button').click()
  await expect(page.getByRole('heading', { name: 'Country 1', level: 2 })).toBeVisible()
  await page.getByRole('button', { name: 'Close country details' }).click()

  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  await expect(page.getByRole('heading', { name: 'Compare countries' })).toBeVisible()
  await expect(page.locator('.comparison-card').first()).toContainText('8.5 / 10 · Rank 1')
  await expect(
    page.locator('.comparison-card').first().getByText('Extreme heat exposure', { exact: true }),
  ).toBeVisible()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
})
