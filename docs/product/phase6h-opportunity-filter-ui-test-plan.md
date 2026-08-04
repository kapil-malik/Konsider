# Phase 6H Opportunity Filter UI test plan

Status: implemented against the staged nine-filter API candidate

Date: 2026-08-04

This plan verifies that the browser consumes the Phase 6G contract without recreating filtering,
evidence interpretation, or affinity logic. Product-data component tests use typed deterministic
fixtures. Playwright supplies the same contract through a mocked HTTP boundary. Backend integration
tests bind the real staged bundle at
`data/reports/phase6g-2026-08-03/staged-release`.

## Interaction and contract matrix

| Area | Required assertion | Automated coverage |
| --- | --- | --- |
| Catalog | Render exactly five Career and four Education/research-university available filters from the API. | Vitest + Playwright |
| Controls | Native checkbox interaction; no Opportunity Filter sliders, weights, toggles, or alternate combination mode. | Vitest + Playwright |
| Draft state | Changes wait for Apply; Undo restores the last applied priorities and filters. | Vitest regression suite |
| Request | Send sorted IDs as `ALL_REQUIRED`; omit the object when the selection is empty. | Vitest + Playwright |
| Score isolation | Applied and removed filters preserve preset/custom weights, affinity scores, contributions, base rank, and survivor order. | Backend integration + Vitest + Playwright |
| Active filters | Show compact removable chips and clear-all without adding nine result columns. | Vitest + Playwright |
| Result summary | Show passing/excluded counts plus distinct verified, not-established, and insufficient states. | Vitest + Playwright |
| Exclusions | Inspect every excluded country, base rank, failing filter, public state, and non-negative explanation. | Vitest + Playwright |
| Empty result | Treat zero matches as a valid response; show counts and remove-filter actions; never auto-relax or show an unfiltered fallback. | Vitest |
| Country details | Show state, confidence, period, establishing route, sources/version/attribution, limitations, and methodology reference. | Vitest + Playwright |
| Domain wording | Disclose skilled-trades/construction route; scope care to human health/social work and finance to finance/insurance; repeat the education limitation. | Vitest + Playwright |
| Comparison | Render selected filters separately on desktop/mobile and preserve canonical context for opportunity-excluded countries. | Vitest + Playwright |
| Responsive | Keep controls collapsible and full width, use cards rather than a nine-column grid, and avoid horizontal document overflow at 390 × 844. | Playwright |
| Accessibility | Keyboard-operable checkboxes/disclosures, visible focus, 44px-or-larger targets, semantic headings/status, text and icons in addition to color. | Vitest + Playwright + CSS review |
| Compatibility | No-filter Phase 5 behavior, coverage/locality/profile assessments, errors, details, comparison, search, and mobile long-list flows remain intact. | Full Vitest + Playwright + backend suites |

## Golden scenarios

1. Apply technology/software and skilled-trades/construction together. Confirm strict AND request
   serialization, two deterministic survivors, unchanged scores/base ranks, and three exclusions
   split between not-established and insufficient evidence.
2. Inspect an excluded country. Confirm all failing filter states remain distinct and the detail
   surface identifies **Both: skilled trades and construction** where both routes establish a
   different selected result.
3. Apply a selection that returns `NO_COUNTRIES_MATCH`. Confirm it is not an error, no fallback
   countries appear, and removing one filter issues a new request with identical preferences.
4. Compare two countries under a selected filter. Confirm filter evidence is separate from ordering
   criteria and an opportunity-excluded country retains its affinity score and base rank.
5. Repeat the selected-filter and comparison flow at 390 × 844. Confirm all nine controls remain
   reachable and the page has no horizontal overflow.

## Manual language and visual review

- No UI label says that a country has no opportunity, is weak, or is bad.
- `INSUFFICIENT_EVIDENCE` states that missing/incompatible evidence is not negative evidence.
- `STRONG_SIGNAL_NOT_ESTABLISHED` states that comparable evidence did not cross the frozen
  threshold; it does not claim absence.
- Education is consistently qualified as research-university ecosystem evidence.
- Verified, not-established, and insufficient treatments have different text, icons, borders and
  tone; meaning never depends on red/green color alone.
- The help disclosure explains strict selection, score independence, evidence freshness, and links
  to the methodology.

## Execution commands

From `web/`:

```text
pnpm run generate:api
pnpm run typecheck
pnpm run lint
pnpm run test -- --run
pnpm run build
pnpm run e2e
```

From the repository root, also run the focused Phase 6G staged-API suite, the full backend suite,
Black/Ruff/compile checks, active-release replay, and `git diff --check`. Phase 6I remains
responsible for clean-checkout publication verification and activation approval.
