# Phase 7E typed assessment engine report

Status: complete; acceptance required before Phase 7F

Date: 2026-08-05

## Outcome

Phase 7E implements a deterministic domain service that evaluates an explicit normalized profile
context against immutable synthetic TFC destination artifacts. It adds typed route and metric
results, country feasibility summaries, optional explicit route filtering and request-scoped
scenario snapshots. No production source data, release activation, API, UI, login or persistence
was added.

## Result types and order

Route evaluation preserves every route and condition, then aggregates to supported,
conditional or guarded no-supported-route match. Scenario metrics preserve formula, component
ranges, units, currency, period, rounding, assumptions, locality, source and effective dates.
Common execution statuses remain evaluated, input required, destination evidence insufficient,
unsupported, not applicable and technical evaluation error.

The implemented order is selection validation, context normalization/hash, applicability,
destination support, jurisdiction/effective rule selection, input sufficiency, typed evaluation,
route aggregation, country/response assessment, optional post-ranking projection and snapshot.

## Filtering

`ASSESS_ONLY` is the default. `REQUIRE_SUPPORTED_MATCH` requires an explicit user request, an
authorized route definition and `EXCLUDE_WITH_REASON` policy. It preserves base rank and survivor
order and never changes affinity. Metric thresholds cannot filter. Zero survivors is a valid empty
projection with no fallback.

## Golden and invariance coverage

Synthetic tests cover no context, no selected TFC, partial profile, complete work, study, family,
clear match, conditional match, guarded no-match, input required, unsupported destination, stale
rule, regional override, metric range, two TFC kinds, explicit filtering, no matches and
tie-preserving survivor order.

They also prove that weights, contributions, affinity, PCC coverage, LSC/locality and Opportunity
Filter assessments remain unchanged, and that disabling TFCs returns the canonical ranking payload.
Snapshots contain no raw profile values and are not stored by the engine.

## Performance

The reproducible 91-country benchmark with three synthetic route checks and one synthetic metric
completed 30 iterations at 179.867 ms median, 291.118 ms p95 and 365.602 ms maximum. See the
[performance report](../product/tfc-assessment-performance.md).

## Verification

- Phase 7E focused suite: 17 passed.
- Complete backend unit suite: 302 passed.
- Ruff checks: passed.
- Black formatting check: passed.
- Diff whitespace check: passed.
- Synthetic 91-country benchmark: 30 iterations, four TFCs, 179.867 ms median.

## Changed paths

Changes are limited to generation-4 engine/snapshot contracts, additive synthetic release-policy
metadata, the domain engine and benchmark command, fictional golden fixtures/tests, and Phase 7
product/history documentation. The active release, API/OpenAPI, frontend, production evidence,
ranking engine, locality engine and Opportunity Filter engine are unchanged.

## Boundary before Phase 7F

There is no engine blocker after owner acceptance of Phase 7E. Phase 7F must replace fictional
route data only through the Phase 7D source/legal and immutable-release workflow, preserve the
first-wave positive/conditional evidence policy until complete inventories are proven, and keep
production activation, API and UI deferred to their later gates.
