# Phase 7I cross-feature verification

Status: implementation and working-tree verification complete

Date: 2026-08-05

## Outcome

Phase 7I composes ordering, PCC, two active locality-derived criteria, strict Opportunity Filters,
the staged first-wave TFC candidate, comparison and browser scenarios without changing the base
ranking. It adds no TFC, policy, release activation, account, server persistence or chat behavior.

## Invariance result

A real request combines Political stability, active PCC Overall job-market opportunity, active LSCs
C66/C67, Technology/software OFC and the skilled-work TFC. The assessed response preserves the
baseline normalized weights, rank/base-rank/score/contribution tuples, PCC exclusion set, locality
assessment, OFC assessment and reserved profile assessment exactly. Every TFC country row reports
unchanged affinity.

The active PCC case continues to exclude ATG, GRD and UKR. They receive no partial aggregate or R1
rank and are not revived by TFC processing. DEU and other supported R1 destinations retain
inspectable route results.

## Product explanation decisions

- Evidence is ordered affinity, coverage, locality, opportunity, feasibility, then assumptions.
- Ecosystem and personal-access statements may disagree because they answer different questions.
- Comparison exposes route/metric effective dates and source IDs in both desktop and mobile forms.
- Missing metrics remain unavailable, never zero.
- Licensing, locality-cost metric and explicit-filter cases are synthetic-only because they are not
  approved first-wave production checks.

## Failures and fixes

- An admission-out-of-scope disclaimer correctly contained the word “admission”; the test was
  narrowed to prove no admission field or route condition is evaluated while retaining the warning.
- A fictional regional licensing rule initially changed the route ID of its national override;
  artifact validation rejected it. The fixture now preserves route identity and asserts regional
  jurisdiction precedence.
- Browser assertions initially targeted collapsed source disclosures and hidden desktop content on
  mobile. The journeys now operate the disclosures and scope assertions to the visible responsive
  representation.
- The situation dialog restored focus on a scheduled animation frame, which raced the full Vitest
  assertion. Restoration now runs on the committed open-to-closed layout transition for Cancel,
  Escape and successful assessment.
- The first backend regression used an inaccessible global Windows pytest temp directory. It had
  403 passing tests and 64 setup errors with no failed assertions; the repository-local CI temp
  rerun passed all 467 tests.
- The legacy generic worker cannot replay schema-5.1 because the active release intentionally has
  no `raw-artifacts.json`. The release-specific locality replay and Phase 6I byte-regeneration test
  are the applicable active-release gates; both pass.

## Verification

Completed working-tree checks:

- full backend: 467 passed, including 10 Phase 7I integration/golden tests;
- frontend ESLint, TypeScript and production build: passed;
- Vitest: 37 passed;
- Playwright Chromium: 14 passed, including two combined desktop/mobile Phase 7I journeys;
- Ruff, Black and Python compilation: passed;
- active locality replay: `replay=PASSED`;
- staged first-wave replay: seven files compared, no mismatches;
- OpenAPI and generated TypeScript regeneration: no drift; and
- manual browser QA: desktop and 390 x 844 mobile passed with no horizontal overflow or console
  warnings/errors. Evidence order, bounded explanations, responsive comparison cards, dates and
  keyboard focus were inspected.

The clean-checkout verifier is run against the Phase 7I commit and recorded in the final execution
summary because it requires the committed revision. Repository CI defines Ubuntu and Windows
backend jobs plus an Ubuntu frontend job; the local unpushed revision has no remote CI run.

## Phase 7J boundary

Phase 7J owns release-6 publication/activation and final closure. Before activation, the owner must
confirm that all three first-wave TFCs remain assessment-only, accept the 29/91 source boundary and
unsupported-destination wording, and confirm that deferred licensing/metric candidates remain out
of the release.
