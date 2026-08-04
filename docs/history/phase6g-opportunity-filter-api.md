# Phase 6G Opportunity Filter engine and API report

Status: complete against staged candidate; Phase 6H UI and Phase 6I publication pending

Completion date: 2026-08-04

Implementation commit: `96c5fa1`

## Outcome

Phase 6G implements the filter-only runtime and additive API transport defined by the Phase 6D
contracts over the complete Phase 6F evidence matrix. It does not change the canonical ranking
algorithm or activate a release.

The deterministic API candidate is:

- build: `phase6g-api-integration-1.0`;
- Opportunity Filter release: `phase6g-api-2026-08-03.1`;
- definitions: 9 active and available;
- evidence rows: 819 (9 filters x 91 countries); and
- location: `data/reports/phase6g-2026-08-03/staged-release`.

`data/releases/active.json` remains `2026-07-29.2`.

## Delivered contract

The API adds `GET /api/v2/opportunity-filters` plus the optional request object
`opportunity_filters: {mode: "ALL_REQUIRED", required_filter_ids: [...]}` to rankings,
comparisons, and country details. Omitted and empty selections preserve the established unfiltered
behavior. Selected IDs must be unique, known, and active.

Evaluation is deliberately downstream of the full canonical ranking. A country survives only when
all selected evidence states are `VERIFIED_STRONG_SIGNAL`. Survivor scores, contributions,
normalized weights, base ranks, and relative order remain canonical. Filtered ranks are separate,
and selected-filter `top_k` includes boundary ties. A zero-row result is valid and never falls back
to unfiltered results.

Responses add a sibling Opportunity Filter assessment with selected definitions, state counts,
exclusions, evidence routes and reasons. Comparisons keep canonical context for countries excluded
only by the selected filters. Details expose bounded selected-filter evidence without returning the
raw metric payload.

## Compatibility proof

- The schema-5 `rank_schema5_release` engine is unchanged.
- No-filter omitted and empty requests are equal.
- FCC/PCC activation, fallback, coverage, LSC aggregation, locality, and profile assessments are
  invariant under filter selection.
- Scores, weights, contributions, base ranks, and survivor order are invariant.
- Release-5.0 deployments load an empty filter catalog unless an explicit immutable bundle path is
  configured.
- The active release pointer and public UI are unchanged.

## Evidence and performance

The bundle is checksum-validated, cross-artifact validated, and indexed once at startup. The
measured Phase 6G candidate load was 656.437 ms. Two hundred assessments using all nine filters
over 83 canonically eligible countries averaged 2.436 ms; measured p95 was 2.424 ms. Request-time
assessment reads no source files or external services.

The golden scenarios cover technology, science/engineering, care/biomedical, combined technology
and mathematics/computer-science, and skilled-trades/construction filters. Additional scenarios
cover mixed failure states, all-nine-filter conjunctions, empty results, tie inclusion,
inactive/unknown/duplicate selections, old-release compatibility, and source/evidence explanation
boundaries.

## Verification

- Phase 6G focused API and settings suite: 70 passed.
- Full backend suite: 367 passed.
- Formatting and lint: Black check passed for 103 files; Ruff passed; compileall passed.
- Active release deterministic replay: passed for `data/releases/2026-07-29.2`.
- Generated OpenAPI and TypeScript contract drift: regenerated and matched the application;
  backend contract tests passed.
- Frontend contract/build gates: ESLint passed, TypeScript typecheck passed, 15 Vitest tests
  passed, and the Vite production build passed.

## Main implementation paths

- `src/konsider/api/opportunity_filter_service.py`
- `src/konsider/api/v2_service.py`
- `src/konsider/api/models/v2.py`
- `src/konsider/api/app.py`
- `src/konsider/ingestion/phase6_opportunity_api_candidate.py`
- `tests/integration/api/test_phase6g_opportunity_api.py`
- `contracts/openapi/konsider-api-2.0.json`
- `web/src/api/schema.d.ts`

## Gates before Phase 6H and 6I

Phase 6H may consume only the typed API contract. The UI must not recreate filtering, evidence
interpretation, or ranking logic and must explain non-established and insufficient evidence
without presenting either as proof of absence.

Phase 6I remains responsible for owner approval, immutable publication, active binding,
clean-checkout verification, rollback evidence, UI/API end-to-end verification, and final closure.
No Phase 6G artifact authorizes production activation by itself.
