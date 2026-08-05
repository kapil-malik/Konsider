# Phase 7H guest situation and feasibility UI test plan

Status: implemented against the staged three-check API candidate

Date: 2026-08-05

This plan verifies that the browser gathers explicit guest context and presents API-owned TFC
outcomes without recreating eligibility, destination support, ranking or filtering logic.

## Interaction and contract matrix

| Area | Required assertion | Automated coverage |
| --- | --- | --- |
| Guest baseline | Ranking works when no situation or TFC is selected. | Existing Vitest + Playwright |
| Guided flow | Open/cancel does not submit; purpose precedes checks and details. | Vitest + Playwright |
| Selection | Relevant checks are catalog-driven and never selected silently. | Vitest + Playwright |
| Inputs | Only selected-check inputs appear; unknown is preserved as unknown. | Vitest + Playwright |
| Request | Send sorted explicit IDs, separate context layers and `ASSESS_ONLY`. | Vitest + Playwright |
| Result isolation | Feasibility is separate from affinity, OFC and locality; affinity is unchanged. | Vitest + Playwright |
| Outcomes | Render input-required, route, unsupported/insufficient and generic metric results. | Vitest component tests |
| Details | Show routes, conditions, source IDs, effective dates, disclaimers and limitations. | Vitest + Playwright |
| Comparison | Reuse the same feasibility selection and present checks separately. | Vitest + Playwright |
| Scenarios | Bound state to three named scenarios with duplicate/remove/switch controls. | Component/state tests |
| Tab state | Save to session storage after successful assessment and restore on reload. | Vitest |
| Device state | Write local storage only after opt-in; expire/version-clear within 30 days. | Vitest state tests |
| Portability | Export no results/URLs/citizenship/household; validate and preview imports. | Vitest |
| Failure | TFC catalog failure is non-blocking; incompatible imports are rejected. | Vitest |
| Accessibility | Labelled native controls, modal semantics, focus trap/return and Escape close. | Vitest + Playwright |
| Responsive | Full-screen mobile flow and no horizontal overflow at 390 x 844. | Playwright |

The current three first-wave policies are all `ASSESS_ONLY`; the explicit-filter/undo case is not
rendered because the API catalog authorizes no filter-capable check. Phase 7I must add that scenario
only if an accepted catalog policy exposes `REQUIRE_SUPPORTED_MATCH_ALLOWED`.

## Manual language and privacy review

- No copy guarantees immigration, a visa, employment or admission.
- No omitted fact is inferred and no browser rule determines eligibility.
- Route no-match wording is bounded to modelled routes and includes the legal disclaimer.
- Source/effective-date and limitations remain inspectable.
- Device retention is off by default and carries a shared-device warning.
- No profile value appears in a URL, analytics hook, returned snapshot or exported result.

## Execution

From `web/`:

```text
pnpm run typecheck
pnpm run lint
pnpm run test -- --run
pnpm run build
pnpm run e2e
```

Also run backend regression tests and `git diff --check`. Phase 7I owns combined integration
verification beyond the staged Phase 7H UI boundary.
