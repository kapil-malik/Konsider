# Phase 5E verification report

Status: implementation complete

Date: 2026-07-29

Scope: structured API v2, schema-4 transport migration, native schema-5 locality transport,
authoritative OpenAPI, and generated TypeScript contracts

Production sources, active release, ranking rules, UI, and production C66 scoring changed: no

## Delivered

Phase 5E introduces `konsider-api-2.0` under `/api/v2` while retaining `/api/v1` as the explicitly
temporary Phase 5 migration surface.

The v2 routes cover health, catalog, rankings, comparisons, and weight-contextual country details.
All use strict Pydantic models, and FastAPI routes only select dependencies and validate transport.
The application-facing v2 service owns release adaptation and response assembly.

API v2 uses only:

- `preference_presets`;
- `preference_preset_id`; and
- `resolved_preference_preset_id`.

No legacy profile alias is accepted or emitted.

## Structured assessments

Ranking, comparison, and country-details responses have one response-level `assessments` object:

- `coverage` owns ranking-universe state and complete excluded-country evidence;
- `locality` owns request-wide locality thresholds, policies, and overlap summary; and
- `profile` explicitly reports `NO_PROFILE_CONTEXT` in Phase 5.

Country rows contain only country-specific locality and profile assessments. They do not repeat
coverage status. A locality warning has advisory effect and cannot become a coverage exclusion.

Excluded countries expose exact active-criterion outcomes, reason codes, source lineage, available
criterion contributions, and country-locality evidence. Their final aggregate is always null.

## Contribution contract

The general contribution contract covers direct and locality-derived results. It exposes scope,
derivation, score and weight, policy/universe identity, locality inputs, observations, source
lineage, scoring versions, observation versions, and quality flags.

Strict cross-domain validation rejects:

- direct contributions with locality policy or locality arrays;
- locality-derived contributions without full policy, universe, evidence, and contributors;
- unavailable cells carrying contributions; and
- coverage-excluded comparison rows carrying ranks or final aggregates.

## Temporary migration boundary

The active release is still `2026-07-28.2`, so v2 includes a backend-only adapter for the active
schema-4/catalog-2 snapshot. It translates existing national evidence into the clean contract and
does not infer locality data. Native schema-5 releases bypass that adapter and expose the Phase 5D
locality engine output directly.

| Temporary field/route | Replacement | Removal phase |
| --- | --- | --- |
| `/api/v1/health` | `/api/v2/health` | 5H |
| `/api/v1/catalog` | `/api/v2/catalog` | 5H |
| `/api/v1/rankings` | `/api/v2/rankings` | 5H |
| `/api/v1/comparisons` | `/api/v2/comparisons` | 5H |
| `/api/v1/countries/{country_code}/metrics` | `/api/v2/countries/{country_code}/details` | 5H |
| v1 `profiles` | v2 `preference_presets` | 5H |
| v1 `profile_id` | v2 `preference_preset_id` | 5H |
| v1 `resolved_profile_id` | v2 `resolved_preference_preset_id` | 5H |
| v1 top-level coverage/uncertainty fields | v2 `assessments.coverage` | 5H |
| internal schema-4-to-v2 active-path adapter | native schema-5 v2 service path | 5H |

No temporary alias exists inside `/api/v2`.

## Contract verification

Transport tests exercise:

- native schema-5 locality provenance in rankings;
- coverage-excluded countries in rankings, comparisons, and details;
- schema-4 compatibility without changing v1;
- all 32 orthogonal coverage/locality status pairs;
- invalid cross-domain contribution combinations;
- rejection of legacy and undocumented request fields; and
- all v2 routes and status enums in OpenAPI.

The authoritative OpenAPI is exported to
`contracts/openapi/konsider-api-2.0.json` and mirrored for the web build. TypeScript component types
are generated from that document; handwritten compatibility response types are not used.

## Final verification

| Command | Result |
| --- | --- |
| `python -m pytest tests/integration/api tests/unit/test_documentation.py tests/unit/test_phase5b_contracts.py -q` | 124 passed |
| `python -m pytest -q` | 302 passed |
| `python -m ruff check .` | All checks passed |
| `python -m black --check .` | 104 files unchanged |
| `pnpm run typecheck` | Passed |
| `pnpm run lint` | Passed |

## Unresolved decisions and blockers

There is no active technical blocker for Phase 5E.

The production-onboarding gates for C66 remain owned by Phase 5G, including JRC day-count versus
pixel-count semantics, scoring transform, policy sensitivity, licensing, and release activation.
No Phase 5E API behavior depends on resolving those source questions.
