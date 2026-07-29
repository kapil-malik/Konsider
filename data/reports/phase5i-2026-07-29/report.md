# Phase 5I end-to-end verification

Date: 2026-07-29

Decision: **local closure gates passed; remote matrix confirmation pending authorized push**

Verified commit before closure documentation: `f4a01d7`

Active release: `2026-07-29.2`

## Verification matrix

| Dimension | Cases | Evidence |
| --- | --- | --- |
| Coverage | FCC only; PCC below threshold; preferred/elevated exclusions; active PCC; fallback; diagnostic-only | `test_phase5d_locality_engine.py`, Phase 4 golden scenarios, `test_phase5i_closure.py` |
| Scope | national direct; one locality; top-N; insufficient evidence; one/multiple LSCs; common, partial, and no overlap | Phase 5D aggregation and ranking tests |
| Weights | 0, 0.2, 0.4, exactly 0.6, 0.8, 1.0; all-zero FCC fallback; mixed FCC/PCC/LSC | Phase 5D six-level test plus Phase 4 all-zero/golden tests |
| API | ranking, baseline semantics, exclusions, details, comparisons, unavailable release, generated contract | API integration tests and Phase 5I active-release test |
| UI | ranking, exclusions, details, comparisons, sources, mobile, accessibility semantics, unavailable release | 15 component tests and 8 Playwright scenarios |
| Profile boundary | no applicant input; explicit non-evaluation; preference preset not treated as applicant | API model, generated-contract, UI, and Phase 5I tests |

## Required invariants

| # | Invariant | Result |
| ---: | --- | --- |
| 1 | Coverage, locality, and profile are separate | Passed |
| 2 | Coverage and national/locality scope combine independently | Passed with schema fixtures and domain tests |
| 3 | Every ranked country has every active criterion | Passed |
| 4 | No locality overlap does not exclude or penalize | Passed |
| 5 | Below-Medium FCC locality evidence retains provenance | Passed at 0.2 and 0.4 |
| 6 | Medium activates locality analysis | Passed exactly at 0.6 |
| 7 | Common-locality search uses all valid evidence | Passed with common locality outside top-N contributors |
| 8 | Country aggregate and locality advisory are independent | Passed |
| 9 | No applicant/household assumption | Passed |
| 10 | No deprecated public response field | Passed recursively and in OpenAPI/TypeScript |
| 11 | Preference-preset terminology is clean | Passed |
| 12 | Release, validation, catalog, API, and UI agree | Passed |
| 13 | Replay is deterministic | Passed |
| 14 | Historical releases remain immutable and inspectable | Passed for schema-3/4 snapshots |
| 15 | Production source/licensing gates remain intact | Passed; every active lineage has licence, checksum, and asset identity |

## Working-tree commands and results

| Command | Result |
| --- | --- |
| `python -m pytest -q tests/unit` | 179 passed |
| `python -m pytest -q tests/integration/api tests/integration/repositories` | 65 passed |
| Root integration plus `tests/integration/worker` | 36 passed |
| **Backend total** | **280 passed, no skips** |
| `python -m black --check .` | 103 files unchanged |
| `python -m ruff check .` | Passed |
| `python -m compileall -q src tests` | Passed |
| `pnpm run generate:api` plus committed-artifact diff | Passed; no diff |
| `pnpm run typecheck` | Passed |
| `pnpm run lint` | Passed |
| `pnpm test --run` | 15 passed |
| `pnpm run build` | Passed |
| `pnpm run e2e` | 8 passed |
| `python -m konsider.ingestion.phase5_locality_onboarding --replay data\releases\2026-07-29.2` | `replay=PASSED` |

## Clean-checkout reproducibility

A source-only Git archive of `f4a01d7` was expanded to a new Windows temporary directory.

| Gate | Result |
| --- | --- |
| Backend unit | 179 passed |
| API/repository | 61 passed, 4 declared licensed-raw skips |
| Other integration/worker | 31 passed, 5 declared licensed-raw skips |
| Python static/format/compile | Passed |
| Offline `pnpm install --frozen-lockfile` | Passed; 271 packages reused, zero downloaded |
| OpenAPI generation and TypeScript | Passed; generated hashes matched committed artifacts |
| ESLint | Passed |
| Component tests | 15 passed |
| Production build | Passed |
| Playwright Chromium | 8 passed |

The nine clean-checkout skips are not concealed:

- four historical Phase 4 rebuild/replay tests require 15-17 licensed local raw files; and
- five raw replay tests require third-party bytes intentionally excluded from Git.

Committed release checksum/schema validation, active API loading, Phase 5I closure invariants, and
frontend/browser behavior still run without those bytes.

## CI status

`.github/workflows/ci.yml` defines:

- backend on `ubuntu-latest`;
- backend on `windows-latest`; and
- frontend generation, type, lint, components, build, Chromium install, and browser tests on
  `ubuntu-latest`.

The Phase 5 commits are eleven local commits ahead of `origin/main` at verification time. They were
not pushed as part of Phase 5I, so GitHub Actions has no run for `f4a01d7`. Current remote Ubuntu
and Windows confirmation must run after an authorized push. The local clean-checkout evidence above
is complete; this report does not claim the unrun remote matrix passed.

## Defects

No product or implementation defect was found. Phase 5I added focused verification for the six
weight levels and for whole-system active-release/disposition/licensing agreement in commit
`f4a01d7`.

