import { expect, test, type Page, type Route } from '@playwright/test'

import {
  catalogFixture,
  comparisonFixture,
  comparisonWithFeasibilityFixture,
  comparisonWithOpportunityAndFeasibilityFixture,
  comparisonWithOpportunityFixture,
  countryDetailsFixture,
  countryDetailsWithFeasibilityFixture,
  countryDetailsWithOpportunityAndFeasibilityFixture,
  countryDetailsWithOpportunityFixture,
  coverageWarningRanking,
  opportunityCatalogFixture,
  rankingFixture,
  rankingWithFeasibility,
  rankingWithOpportunityAndFeasibility,
  rankingWithOpportunityFilters,
  tfcCatalogFixture,
} from '../src/test/fixtures'

async function json(route: Route, body: unknown, status = 200) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

async function mockApi(
  page: Page,
  requests: Array<{ path: string; body?: unknown }> = [],
  ranking = rankingFixture,
  filteredRanking = ranking,
) {
  await page.route('http://127.0.0.1:8000/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push({ path: url.pathname, body: request.postDataJSON() })
    if (url.pathname.endsWith('/catalog')) return json(route, catalogFixture)
    if (url.pathname.endsWith('/opportunity-filters')) {
      return json(route, opportunityCatalogFixture)
    }
    if (url.pathname.endsWith('/tfcs')) return json(route, tfcCatalogFixture)
    if (url.pathname.endsWith('/rankings')) {
      const body = request.postDataJSON() as {
        opportunity_filters?: unknown
        feasibility?: unknown
      } | null
      if (body?.feasibility && body?.opportunity_filters) {
        return json(route, rankingWithOpportunityAndFeasibility)
      }
      if (body?.feasibility) return json(route, rankingWithFeasibility)
      return json(route, body?.opportunity_filters ? filteredRanking : ranking)
    }
    if (url.pathname.includes('/countries/')) {
      const code = url.pathname.split('/countries/')[1]?.split('/')[0] ?? 'C00'
      const index = Number(code.slice(-1))
      const body = request.postDataJSON() as {
        opportunity_filters?: unknown
        feasibility?: unknown
      } | null
      if (body?.feasibility && body?.opportunity_filters) {
        return json(
          route,
          countryDetailsWithOpportunityAndFeasibilityFixture(
            Number.isFinite(index) ? index : 0,
          ),
        )
      }
      if (body?.feasibility) {
        return json(route, countryDetailsWithFeasibilityFixture(Number.isFinite(index) ? index : 0))
      }
      if (body?.opportunity_filters) {
        return json(route, countryDetailsWithOpportunityFixture(Number.isFinite(index) ? index : 0))
      }
      const excluded = ranking.assessments.coverage.excluded_countries.some(
        (item) => item.country.country_codes.includes(code),
      )
      return json(route, countryDetailsFixture(Number.isFinite(index) ? index : 0, excluded))
    }
    if (url.pathname.endsWith('/comparisons')) {
      const body = request.postDataJSON() as {
        opportunity_filters?: unknown
        feasibility?: unknown
      } | null
      if (body?.feasibility && body?.opportunity_filters) {
        return json(route, comparisonWithOpportunityAndFeasibilityFixture)
      }
      if (body?.feasibility) return json(route, comparisonWithFeasibilityFixture)
      return json(route, body?.opportunity_filters ? comparisonWithOpportunityFixture : comparisonFixture)
    }
    return json(route, { error: { code: 'not_found', message: 'Not found' } }, 404)
  })
}

async function applyWorkSituation(page: Page) {
  await page.getByRole('button', { name: 'Add your situation' }).click()
  const dialog = page.getByRole('dialog', { name: 'Your situation' })
  await dialog.getByRole('radio', { name: 'Work' }).check()
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('checkbox', { name: /Highly qualified work route check/ }).check()
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('combobox', { name: /Target destinations/ }).fill('DEU')
  await dialog.getByLabel(/Target date/).fill('2026-08-05')
  await dialog.getByRole('textbox', { name: /Current occupation/ }).fill('Civil engineer')
  await dialog.getByRole('combobox', { name: /Qualifications/ }).selectOption('MASTERS')
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('button', { name: 'Save and assess' }).click()
}

async function expandOpportunityGroups(page: Page) {
  const panel = page.locator('section[aria-labelledby="opportunity-filters-heading"]')
  await expect(panel).toBeVisible()
  const groups = panel.locator('.opportunity-group')
  await expect(groups).toHaveCount(2)
  for (let index = 0; index < await groups.count(); index += 1) {
    const group = groups.nth(index)
    if (!(await group.evaluate((element) => element.hasAttribute('open')))) {
      await group.locator('summary').click()
    }
  }
  return panel
}

test('initial guest ranking and explicit priority update use the v3 contract', async ({ page }) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests)
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Country ranking' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Guest/ })).toBeVisible()
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
  await expect(page.getByLabel('Locality-derived criterion').first()).toBeVisible()
  await expect(page.getByText(/Harbor City/).first()).toBeVisible()
  const rankingCallsBeforeBack = requests.filter((item) => item.path.endsWith('/rankings')).length
  await page.getByRole('button', { name: '← Back to rankings' }).click()
  await expect(page.getByRole('heading', { name: 'Country ranking' })).toBeVisible()
  expect(requests.filter((item) => item.path.endsWith('/rankings'))).toHaveLength(
    rankingCallsBeforeBack,
  )
})

test('opens and closes Criteria and sources from the Guest menu', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')
  await page.getByRole('button', { name: /Guest/ }).click()
  await page.getByRole('menuitem', { name: 'Criteria and sources' }).click()
  const dialog = page.getByRole('dialog', { name: 'Criteria and sources' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Extreme heat exposure' })).toBeVisible()
  await expect(dialog.getByText('top-two:heat')).toBeVisible()
  await dialog.getByRole('button', { name: 'Close Criteria and sources' }).click()
  await expect(dialog).toBeHidden()
})

test('search and region filters update visible and total result counts', async ({ page }) => {
  await mockApi(page)
  await page.goto('/')

  await page.getByRole('combobox', { name: 'Search countries' }).fill('C03')
  await expect(page.getByText(/Showing 1 of 5 returned countries/)).toBeVisible()
  await expect(page.locator('.ranking-table tbody tr[data-country-code="C03"]')).toBeVisible()

  await page.locator('.ranking-filters select').selectOption('Region 2')
  await expect(page.getByRole('heading', { name: 'No countries match these filters' })).toBeVisible()
  await expect(page.getByText(/Showing 0 of 5 returned countries/)).toBeVisible()
})

test('shows a controlled unavailable-release state', async ({ page }) => {
  await page.route('**/api/v3/catalog', (route) =>
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

test('applies strict Opportunity Filters and exposes removable evidence and exclusions', async ({
  page,
}) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests, rankingFixture, rankingWithOpportunityFilters())
  await page.goto('/')

  const opportunityPanel = await expandOpportunityGroups(page)
  await expect(opportunityPanel.getByRole('checkbox')).toHaveCount(9)
  await expect(opportunityPanel.getByRole('slider')).toHaveCount(0)
  await opportunityPanel.getByRole('checkbox', { name: /Technology and software/ }).check()
  await opportunityPanel.getByRole('checkbox', { name: /Skilled-trades or construction/ }).check()
  await page.getByRole('button', { name: 'Apply priorities' }).click()

  await expect(
    page.getByRole('heading', { name: '2 countries match all selected opportunity filters' }),
  ).toBeVisible()
  const opportunitySummary = page.getByRole('region', {
    name: '2 countries match all selected opportunity filters',
  })
  await expect(
    opportunitySummary.getByText('Strong signal not established', { exact: true }),
  ).toBeVisible()
  await expect(
    opportunitySummary.getByText('Insufficient evidence', { exact: true }),
  ).toBeVisible()
  await expect(page.getByText('8.5 / 10').first()).toBeVisible()
  expect(requests.filter((item) => item.path.endsWith('/rankings')).at(-1)?.body).toEqual({
    preference_preset_id: 'balanced',
    opportunity_filters: {
      mode: 'ALL_REQUIRED',
      required_filter_ids: [
        'skilled_trades_construction_opportunity',
        'technology_software_opportunity',
      ],
    },
  })

  await page.getByText(/Review 3 opportunity-filter excluded countries/).click()
  await page.getByRole('button', { name: 'Country 3' }).click()
  await expect(page.getByText('Both: skilled trades and construction')).toBeVisible()
  const details = page.getByRole('region', { name: 'Country 3' })
  const careEvidence = details
    .locator('.opportunity-evidence-card')
    .filter({ hasText: 'Care-sector employment ecosystem' })
  await expect(
    careEvidence.locator('p').filter({ hasText: 'This filter covers human health and social work' }),
  ).toBeVisible()
})

test('mobile Opportunity Filters remain collapsible, complete, and free of horizontal overflow', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(
    page,
    [],
    rankingFixture,
    rankingWithOpportunityFilters(['skilled_trades_construction_opportunity']),
  )
  await page.goto('/')

  const opportunityPanel = page.locator(
    'section[aria-labelledby="opportunity-filters-heading"]',
  )
  await expect(opportunityPanel.locator('.opportunity-group summary').first()).toContainText(
    'Career',
  )
  await expect(opportunityPanel.locator('.opportunity-group summary').nth(1)).toContainText(
    'Education',
  )
  await expect(opportunityPanel.getByRole('checkbox')).toHaveCount(0)
  await expandOpportunityGroups(page)
  await expect(opportunityPanel.getByRole('checkbox')).toHaveCount(9)
  await opportunityPanel
    .getByRole('checkbox', { name: /Skilled-trades or construction/ })
    .check()
  await page.getByRole('button', { name: 'Apply priorities' }).click()
  await expect(page.locator('.ranking-card').first().getByText(/Matches 1 filter/)).toBeVisible()

  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  await expect(page.getByText('Opportunity filter').first()).toBeVisible()
  await expect(
    page.locator('.comparison-cards').getByText(/Both: skilled trades and construction/).first(),
  ).toBeVisible()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
})

test('guest situation explicitly assesses one TFC and reuses the snapshot in details and comparison', async ({
  page,
}) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(page, requests)
  await page.goto('/')

  const opener = page.getByRole('button', { name: 'Add your situation' })
  await opener.click()
  const dialog = page.getByRole('dialog', { name: 'Your situation' })
  await dialog.getByRole('radio', { name: 'Work' }).check()
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('checkbox', { name: /Highly qualified work route check/ }).check()
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('combobox', { name: /Target destinations/ }).fill('DEU')
  await dialog.getByLabel(/Target date/).fill('2026-08-05')
  await dialog.getByRole('textbox', { name: /Current occupation/ }).fill('Civil engineer')
  await dialog.getByRole('combobox', { name: /Qualifications/ }).selectOption('MASTERS')
  await dialog.getByRole('button', { name: 'Continue' }).click()
  await dialog.getByRole('button', { name: 'Save and assess' }).click()

  await expect(page.getByRole('button', { name: 'Edit situation' }).first()).toBeFocused()
  await expect(page.getByText('Additional inputs requested')).toBeVisible()
  const rankingRequest = requests.filter((item) => item.path.endsWith('/rankings')).at(-1)
  expect(rankingRequest?.body).toMatchObject({
    preference_preset_id: 'balanced',
    feasibility: {
      tfc_ids: ['skilled_work_route_feasibility'],
      mode: 'ASSESS_ONLY',
      scenario_context: {
        purpose: 'WORK',
        target_country_codes: ['DEU'],
        job_offer: { state: 'UNKNOWN' },
      },
    },
  })
  expect(await page.evaluate(() => localStorage.getItem('konsider:situation:remembered'))).toBeNull()

  await page.locator('.ranking-table tbody tr').first().click()
  await expect(page.getByText('Fictional skilled work route')).toBeVisible()
  await page.getByRole('button', { name: 'Close country details' }).click()
  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  await expect(page.getByText('Feasibility check').first()).toBeVisible()
  expect(requests.find((item) => item.path.endsWith('/comparisons'))?.body).toMatchObject({
    feasibility: { tfc_ids: ['skilled_work_route_feasibility'] },
  })
})

test('strict OFC, locality, and TFC evidence remain separate across details and comparison', async ({
  page,
}) => {
  const requests: Array<{ path: string; body?: unknown }> = []
  await mockApi(
    page,
    requests,
    rankingFixture,
    rankingWithOpportunityFilters(['skilled_trades_construction_opportunity']),
  )
  await page.goto('/')

  await expandOpportunityGroups(page)

  await page
    .getByRole('checkbox', { name: /Skilled-trades or construction/ })
    .check()
  await page.getByRole('button', { name: 'Apply priorities' }).click()
  await applyWorkSituation(page)

  const rankingRequest = requests.filter((item) => item.path.endsWith('/rankings')).at(-1)
  expect(rankingRequest?.body).toMatchObject({
    opportunity_filters: {
      mode: 'ALL_REQUIRED',
      required_filter_ids: ['skilled_trades_construction_opportunity'],
    },
    feasibility: {
      mode: 'ASSESS_ONLY',
      tfc_ids: ['skilled_work_route_feasibility'],
    },
  })
  await expect(page.getByRole('columnheader', { name: 'Opportunity filters' })).toBeVisible()
  await expect(page.getByRole('columnheader', { name: 'Feasibility checks' })).toBeVisible()
  await expect(page.getByText('Common locality available').first()).toBeVisible()

  await page.locator('.ranking-table tbody tr').first().click()
  await expect(page.getByText('Routes evaluated')).toBeVisible()
  await page.getByText('Conditions and sources').click()
  await expect(page.getByText(/Sources: fictional-work-source/)).toBeVisible()
  await page.getByText('Sources and limitations').click()
  await expect(page.getByText(/Evidence effective 2026-08-05/)).toBeVisible()
  await page.getByRole('button', { name: 'Close country details' }).click()

  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  await expect(page.getByText('How the signals relate')).toHaveCount(0)
  await expect(page.getByText(/sources fictional-work-source/).first()).toBeVisible()
  await expect(page.getByText(/Check evidence effective 2026-08-05/).first()).toBeVisible()
  await expect(page.getByText(/Filtered rank/).first()).toBeVisible()
})

test('mobile combined evidence remains complete and free of horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(
    page,
    [],
    rankingFixture,
    rankingWithOpportunityFilters(['skilled_trades_construction_opportunity']),
  )
  await page.goto('/')
  await expandOpportunityGroups(page)
  await page
    .getByRole('checkbox', { name: /Skilled-trades or construction/ })
    .check()
  await page.getByRole('button', { name: 'Apply priorities' }).click()
  await applyWorkSituation(page)

  await expect(
    page.locator('.ranking-card').first().getByText('Conditional route match found'),
  ).toBeVisible()
  await expect(page.locator('.ranking-card').first().getByText(/Matches 1 filter/)).toBeVisible()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)

  const boxes = page.getByRole('checkbox', { name: /Select Country/ })
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await page.getByRole('button', { name: 'Compare selected (2)' }).click()
  const comparisonCards = page.locator('.comparison-cards')
  await expect(comparisonCards.getByText(/sources fictional-work-source/).first()).toBeVisible()
  await expect(
    comparisonCards.getByText(/Check evidence effective 2026-08-05/).first(),
  ).toBeVisible()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
})

test('mobile situation flow is full-screen, keyboard closable, and has no horizontal overflow', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockApi(page)
  await page.goto('/')
  const opener = page.getByRole('button', { name: 'Add your situation' })
  await opener.click()
  const dialog = page.getByRole('dialog', { name: 'Your situation' })
  await expect(dialog).toBeVisible()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(opener).toBeFocused()
})
