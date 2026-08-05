# Typed Feasibility Check assessment engine

Status: Phase 7E synthetic domain engine implemented; API, UI and production evidence deferred

## Domain boundary

`TfcAssessmentEngine` combines one request-scoped effective context with immutable TFC destination
artifacts. It accepts an already computed canonical ranking payload, deep-copies it and owns only
profile normalization, input sufficiency, TFC applicability, support resolution, rule evaluation,
metric calculation, feasibility projection and scenario snapshots.

It does not calculate ranking, weights, affinity, PCC complete-case unions, LSC aggregation or
Opportunity Filter states. FastAPI and React do not implement or expose these rules in Phase 7E.

## Evaluation order

The implemented deterministic order is:

1. validate filter mode and selected TFC identities;
2. deep-copy the canonical ranking payload;
3. normalize the applicant, household and scenario context and compute its opaque hash;
4. resolve TFC applicability for the declared scenario purpose and household composition;
5. read the explicit destination-support record for each TFC-country pair;
6. resolve jurisdiction precedence, regional overrides, effective dates, staleness and conflicts;
7. resolve blocking input requirements without inventing unknown values;
8. evaluate the bounded route/rule or metric policy;
9. aggregate per-route results into country/TFC outcomes and assessment summaries;
10. optionally create an explicitly requested supported-route projection while preserving base
    rank, survivor order, scores and all canonical assessments; and
11. build a non-persisted scenario snapshot with release, policy, source and context-hash identity.

Destination support precedes profile sufficiency: an unsupported destination remains unsupported
and does not solicit irrelevant profile fields.

## Normalization and input sufficiency

Country and currency codes are uppercased, user text is whitespace-normalized, arrays used as sets
are ordered, and client IDs/provenance are excluded from the snapshot hash. Missing values remain
missing. No default occupation, qualification, household member, locality, offer or scenario fact
is invented.

Input requirements are `ALWAYS_REQUIRED`, `CONDITIONALLY_REQUIRED` or
`OPTIONAL_EXPLANATORY`. A job offer is known absent only when the user supplies `state: ABSENT`.
An omitted, null or `UNKNOWN` offer produces `INPUT_REQUIRED` with `scenario.job_offer`.

Errors and diagnostics identify field IDs and record IDs; they never echo profile values. The
engine contains no request logging or persistence path.

## Route evaluation

The bounded condition vocabulary supports presence/absence, equality, set membership, numeric or
date ranges, thresholds, booleans, taxonomy membership, qualification level, jurisdiction,
conditional requirements and AND/OR groups. It is data-driven but not an arbitrary expression
language.

Each route preserves evaluated conditions as `MET`, `UNMET`, `UNKNOWN` or `NOT_APPLICABLE`, plus
jurisdiction, source IDs, effective period and evidence quality. Blocking unmet conditions produce
`NO_MATCH`; blocking unknown conditions produce `CONDITIONAL`; otherwise the route is `MATCH`.

Multiple routes aggregate deterministically:

- any clear route match: `SUPPORTED_ROUTE_MATCH`;
- otherwise any conditional route: `CONDITIONAL_ROUTE_MATCH`;
- otherwise guarded `NO_SUPPORTED_ROUTE_MATCH` only under a complete-inventory policy; or
- destination evidence insufficient when a negative conclusion is not authorized.

The no-match disclaimer is always: “No supported-route match is not a permanent legal
impossibility.”

## Scenario metrics

The synthetic metric evaluator supports versioned weighted-sum formulas, scalar or ranged
components, explicit units, currency, period, rounding, assumptions, optional/required locality,
missing components and exchange-rate policy. A currency conversion is rejected unless an approved
table policy exists. Phase 7E contains no such table and performs no conversion.

Metric output remains in its declared unit and is never converted to a 1-10 score. The metric
fixture is synthetic architecture proof, not an approved first-wave TFC.

## Filtering

Default mode is `ASSESS_ONLY`. `REQUIRE_SUPPORTED_MATCH` is allowed only when:

- the user explicitly requests it;
- at least one selected definition is route/rule and declares filtering capability;
- its immutable policy declares `EXCLUDE_WITH_REASON`; and
- each survivor has a clear supported route match for every filterable selected TFC.

Input-required, insufficient, unsupported, conditional and no-match outcomes remain visible in the
assessment even when excluded from the projection. Metric thresholds cannot filter. No-match
projections never relax or fall back when zero countries survive.

## Invariants and snapshots

With TFCs off, the canonical payload is returned unchanged. Assessment-only mode leaves ranking
rows unchanged and adds only `assessments.feasibility` to the copied top-level payload. Explicit
filtering renumbers display `rank` but preserves `base_rank`, `total_score`, contributions,
normalized weights and all pre-existing coverage, locality, profile and Opportunity assessments.

The scenario snapshot contains active and TFC release IDs, policy/source versions, effective
context hash, selected TFCs, evaluation date, base-order checksum, outcomes, assumptions and
warnings. It contains no profile objects or raw profile values and declares
`persisted_server_side: false`.

See the [performance report](tfc-assessment-performance.md) and
[Phase 7E implementation report](../history/phase7e-tfc-assessment-engine.md).
