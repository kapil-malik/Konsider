# Konsider Phase 7E — Typed Assessment Engine and Scenario Snapshots

## Dependency

Proceed only after Phase 7D is accepted.

## Role

Work as the lead domain-engine, policy-evaluation, deterministic-assessment and scenario-snapshot engineer for Konsider.

Use synthetic or staged test data only.

Do not activate production TFC data, expose final API behavior or add UI.

## Objective

Implement the generic TFC assessment engine that evaluates an explicit effective profile context against immutable destination rules/evidence.

Preserve canonical country ranking and all existing assessments.

## Domain ownership

The domain service owns:

- profile/scenario normalization;
- input sufficiency;
- TFC applicability;
- destination support;
- effective-date selection;
- route/rule evaluation;
- scenario metric calculation;
- reason codes;
- optional explicit feasibility filtering;
- assessment summaries.

FastAPI routes and React components must not own these rules.

## Effective context normalization

Normalize:

- country/citizenship codes;
- occupation taxonomy/version;
- qualifications;
- currencies;
- dates/years;
- household composition;
- scenario intent;
- target locality;
- selected TFCs.

Do not invent missing values.

Produce an immutable effective-context snapshot and hash.

The hash must avoid exposing raw personal values in logs.

## Input sufficiency

For each selected TFC:

1. resolve input requirements;
2. determine which are satisfied;
3. return structured missing-input requirements;
4. do not evaluate substantive outcome when blocking inputs are absent;
5. allow partial explanatory evaluation only when policy explicitly permits it.

A missing job offer must be represented as “no job offer” only if the user explicitly provided that value. Otherwise it is unknown.

## Evaluation order

A suggested deterministic order:

1. validate request and context;
2. resolve selected/applicable TFCs;
3. resolve destination support;
4. resolve jurisdiction and effective date;
5. evaluate input sufficiency;
6. evaluate type-specific policy;
7. assemble per-TFC outcome;
8. assemble country feasibility assessment;
9. optionally apply explicit permitted feasibility filtering;
10. preserve base ranking and survivor order.

Document and test the final order.

## Route/rule engine

Implement only the condition vocabulary required by approved first-wave TFCs.

Support deterministic conditions such as:

- equality/set membership;
- numeric minimum/maximum/range;
- boolean requirement;
- presence/absence;
- date/age range;
- occupation/taxonomy membership;
- qualification level;
- jurisdiction;
- AND/OR groups where required;
- conditional requirement.

Avoid a Turing-complete or arbitrary expression engine.

For each route return:

- evaluated conditions;
- met;
- unmet;
- unknown;
- blocking;
- route match classification;
- source/effective date.

## Multiple routes

A TFC may evaluate multiple routes.

Define deterministic aggregation:

- at least one clear match;
- one or more conditional matches;
- no supported route matched;
- input required;
- insufficient destination evidence;
- unsupported.

Do not discard route-level detail.

Do not describe “no supported route matched” as impossible immigration or permanent ineligibility.

## Scenario metric engine

For approved metric TFCs support:

- versioned formula;
- components;
- units;
- currency;
- period;
- ranges;
- rounding;
- missing components;
- assumptions;
- exchange-rate policy only if approved;
- locality selection;
- confidence/quality.

Do not convert a metric to a 1–10 score unless Phase 7B and owner approval explicitly froze the transform.

## Country and response assessments

Produce:

- profile context present/absent summary;
- selected TFCs;
- evaluated/input-required/unsupported counts;
- per-country TFC outcomes;
- matched-route counts;
- scenario metric summaries;
- source/effective-date warnings;
- base rank;
- optional filtered rank;
- explicit no-change affinity score.

## Optional feasibility filtering

Default behavior is assessment-only.

Permit post-ranking filtering only when:

- a TFC definition explicitly allows it;
- the user explicitly requests it;
- the TFC is a route/rule type with approved match semantics;
- survivor order is stable from base ranking;
- affinity scores and base ranks remain unchanged;
- input-required/insufficient/unsupported handling is visible and policy-defined.

Prefer modes such as:

- `ASSESS_ONLY`;
- `REQUIRE_SUPPORTED_MATCH`.

Do not allow metric thresholds as filters in Phase 7 unless explicitly approved.

## Interaction invariants

Test that:

- TFC evaluation does not change weights;
- TFC evaluation does not change contributions;
- TFC evaluation does not change affinity;
- TFC evaluation does not change PCC unions;
- TFC evaluation does not change LSC aggregation;
- TFC evaluation does not change OFC states;
- explicit feasibility filtering preserves survivor order;
- turning TFCs off returns canonical existing ranking payloads.

## Scenario snapshots

Define a result snapshot containing:

- active release ID;
- TFC policy/source versions;
- effective profile context hash;
- selected TFCs;
- evaluation date;
- base ranking reference;
- TFC outcomes;
- assumptions;
- warnings.

Snapshots are returned to the client but not persisted server-side.

Do not put raw profile fields into diagnostic IDs.

## Synthetic golden scenarios

Create golden tests for:

- no profile context;
- partial profile;
- complete work scenario;
- study scenario;
- family scenario;
- matched route;
- conditional route;
- no supported route;
- input required;
- unsupported country;
- stale rule;
- regional rule;
- metric range;
- two TFC kinds active;
- explicit feasibility filter;
- no matches;
- OFC selected alongside TFC;
- PCC and LSC active alongside TFC;
- tie-preserving filtered order.

## Performance and safety

Measure assessment cost across:

- 91 countries;
- approved first-wave TFC count;
- multiple routes;
- scenario metrics.

Avoid uncontrolled rule explosion.

No request body or profile field may be logged.

Error messages must identify field IDs, not echo sensitive values.

## Required outputs

- TFC assessment domain service;
- context normalization;
- input-sufficiency evaluator;
- approved typed evaluators;
- scenario snapshot;
- optional filtering engine;
- golden tests;
- invariance tests;
- performance report;
- product/domain documentation;
- Phase 7E implementation report.

## Explicit non-goals

Do not:

- onboard production source data;
- activate release;
- expose final API/UI;
- persist profiles;
- implement login;
- use LLM reasoning;
- introduce arbitrary rules DSL;
- change base ranking.

## Commit

Use a focused commit such as:

`feat: implement typed feasibility assessment engine`

## Stop condition

Stop when synthetic/staged golden scenarios pass and all ranking/OFC/locality invariants hold.

Report:

- evaluation order;
- result types;
- filtering behavior;
- performance;
- invariance results;
- files changed;
- tests run;
- commit SHA;
- blockers before Phase 7F.
