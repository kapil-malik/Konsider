# Phase 6H Opportunity Filter UI and explanations report

Status: complete against staged candidate; Phase 6I publication pending

Completion date: 2026-08-04

Implementation commit: `ba113ab`

## Outcome

Phase 6H adds the browser controls, result explanations, exclusion inspection, country evidence and
comparison presentation for all nine Opportunity Filters exposed by the Phase 6G API. It consumes
only the typed `/api/v2` contract. It does not reproduce threshold logic, evaluate evidence, change
affinity, alter ranking weights, publish a release, or modify the active release pointer.

The verified candidate remains:

- Opportunity Filter release `phase6g-api-2026-08-03.1`;
- 9 active definitions: 5 career and 4 education/research-university filters;
- 819 explicit evidence rows over 91 countries; and
- `data/reports/phase6g-2026-08-03/staged-release`.

`data/releases/active.json` remains `2026-07-29.2`.

## Delivered experience

- A distinct **Opportunity filters** section groups Career and Education/research-university
  definitions and uses native checkboxes only.
- Every selected filter is required. Draft filters share Apply/Undo with preference changes, while
  removable active chips and clear-all preserve the applied preset or custom weights.
- Ranking responses show filter/base ranks, unchanged affinity, compact match summaries, state
  counts, and a separate inspection panel for excluded countries and every failing filter.
- Zero matches is a deliberate non-error state with counts and explicit broadening controls. The
  interface does not auto-relax filters or substitute the unfiltered ranking.
- Country details show exact state explanations, confidence, period, establishing routes, sources,
  versions, attribution, limitations, and methodology reference for selected filters only.
- Comparison surfaces keep Opportunity Filter evidence separate from ordering criteria and retain
  canonical score/base-rank context for filter-only exclusions.

## Language safeguards

**Verified strong signal**, **Strong signal not established**, and **Insufficient evidence** receive
distinct text, icon, border and background treatments. Not-established wording says comparable
evidence did not cross the frozen strong-ecosystem threshold. Insufficient wording says comparable
evidence is inadequate to reach either conclusion and is not negative evidence.

Skilled-trades/construction results identify skilled trades, construction, or both routes. Care is
described as human health and social work, not doctor-only evidence. Finance is limited to finance
and insurance, not all business or administration careers. Education is consistently qualified as
research-university ecosystem evidence and repeats this limitation:

> This evidence describes research-intensive university ecosystems. It does not establish teaching
> quality, programme availability, admission access, affordability, accreditation or applicant
> eligibility.

## Component descriptions

- **OpportunityFiltersPanel**: grouped collapsible catalog controls, selection count, strict-AND
  explanation, help disclosure and clear-all action.
- **AssessmentSummary**: applied chips, pass/exclusion counts, per-filter state counts and excluded-
  country inspection.
- **RankingView**: preserved affinity/rank presentation, one compact Opportunity Filter column,
  mobile badges and a controlled zero-match state.
- **CountryDetails**: selected-filter evidence cards with route, confidence, period, source and
  limitation context.
- **ComparisonView**: separate selected-filter rows/cards and filter-exclusion context.

At 760px and below, controls and evidence stack into cards and the desktop result/comparison tables
yield to mobile presentations. Large targets, native keyboard semantics, visible focus, status
announcements and text-plus-icon state indicators follow the established accessibility patterns.
No analytics event was added because the repository has no established product-analytics
convention.

## Verification

- Staged Phase 6G API integration suite: 23 passed.
- Full backend suite: 367 passed.
- Backend quality: Black check passed for 103 files; Ruff and compileall passed.
- Active release deterministic replay: `replay=PASSED` for `2026-07-29.2`.
- OpenAPI/TypeScript regeneration: passed with no generated contract drift.
- Frontend quality: TypeScript, ESLint and production build passed; 20 Vitest component tests
  passed.
- Browser verification: 10 Playwright scenarios passed, including strict-filter desktop evidence,
  390 × 844 mobile controls/comparison, legacy no-filter flows and no horizontal overflow.
- Manual language/contract review: no filter weights or alternate modes; distinct non-negative
  state explanations; required career/education scope limitations; no activation or active-pointer
  change.

The detailed scenario matrix is in the
[Phase 6H test plan](../product/phase6h-opportunity-filter-ui-test-plan.md).

## Main implementation paths

- `web/src/components/OpportunityFiltersPanel.tsx`
- `web/src/components/AssessmentSummary.tsx`
- `web/src/components/RankingView.tsx`
- `web/src/components/CountryDetails.tsx`
- `web/src/components/ComparisonView.tsx`
- `web/src/opportunityPresentation.ts`
- `web/src/App.tsx`
- `web/src/App.test.tsx`
- `web/e2e/konsider.spec.ts`

## Phase 6I gates

Phase 6I remains responsible for owner approval, immutable publication and activation, end-to-end
verification against the published active binding, clean-checkout/CI evidence, rollback proof and
Phase 6 closure. Phase 6H does not authorize activation by itself.
