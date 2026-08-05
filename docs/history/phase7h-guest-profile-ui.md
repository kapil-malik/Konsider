# Phase 7H guest situation and feasibility UI

Status: complete against staged first-wave TFC candidate; Phase 7I pending

Completion date: 2026-08-05

## Outcome

Phase 7H adds a guest-first **Your situation** experience to the existing responsive ranking. It
consumes the Phase 7G generated catalog and request/response types, keeps TFC choice explicit and
renders feasibility as a sibling assessment. It does not activate release 6, add authentication,
persist server-side, implement chat, change ranking or reproduce TFC rules in React.

## Delivered experience

- Compact summaries distinguish priorities, Opportunity Filters, active scenario and TFC choice.
- A four-step accessible modal covers purpose, checks, relevant details and review.
- One applicant/household context supports up to three named local scenarios with duplicate,
  remove and switch operations.
- Every check is explicitly selected from API labels; unknown facts remain unknown.
- Ranking, country details and comparison submit one typed selection and show input-required,
  route and metric presentations independently of affinity and Opportunity evidence.
- Candidate/catalog failure is non-blocking for ordinary ranking.

## State and privacy

Successful assessments save the situation to tab-scoped session storage. Versioned device storage
is opt-in, expires after 30 days and is cleared when expired, incompatible or explicitly disabled.
Current and remembered state have separate clear actions. Imports are validated and previewed.
Default exports omit citizenship, household details, assessment results and URLs.

No profile data is inferred, placed in URLs, sent to analytics or persisted by the API. The staged
snapshot remains sanitized metadata only.

## Accessibility and responsive behavior

The modal has labelled semantics, heading focus, Tab containment, Escape close and trigger focus
return. Status meaning uses text and symbols in addition to color. At 760px and below the flow is
full-screen and details/comparison remain stacked without horizontal page overflow.

## Verification boundary

Vitest covers baseline compatibility, progressive fields, explicit unknowns, TFC serialization,
input-required/route/metric rendering, details/comparison consistency, retention, expiry,
redacted export, validated import and unavailable-catalog behavior. Playwright covers the complete
desktop guest flow and the mobile modal/overflow/focus behavior.

Completed verification:

- frontend typecheck and ESLint: passed;
- frontend production build: passed;
- Vitest: 31 passed;
- Playwright Chromium: 12 passed;
- Ruff: passed;
- Black: 130 files unchanged;
- Pytest: 457 passed; and
- manual in-app browser QA: desktop and 390 x 844 mobile layouts passed with no page-level
  horizontal overflow and correct Escape focus restoration.

## Main implementation paths

- `web/src/situation.ts`
- `web/src/components/SituationDialog.tsx`
- `web/src/components/FeasibilitySummary.tsx`
- `web/src/tfcPresentation.ts`
- `web/src/App.tsx`
- `web/src/components/RankingView.tsx`
- `web/src/components/CountryDetails.tsx`
- `web/src/components/ComparisonView.tsx`
- `web/src/App.test.tsx`
- `web/e2e/konsider.spec.ts`

## Phase 7I boundary

Phase 7I must verify combined OFC, locality and TFC behavior and any future explicitly authorized
feasibility filtering. The current three first-wave policies remain assessment-only. Phase 7H does
not authorize release publication or activation.
