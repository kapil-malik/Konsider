# ADR 016: Typed TFC outcomes instead of a universal score or state

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

A route match, a future cost range and an advisory checklist have different semantics. A universal
favorable/unfavorable state would erase conditions and encourage false comparisons.

## Decision

Every outcome has a small common execution status and a separately typed result. Phase 7C implements
only `tfc-route-result-1.0`, because all three approved checks are route/rule matches. Common statuses
are `EVALUATED`, `INPUT_REQUIRED`, `DESTINATION_EVIDENCE_INSUFFICIENT`, `UNSUPPORTED`,
`NOT_APPLICABLE` and technical-only `EVALUATION_ERROR`.

Route classifications are `SUPPORTED_ROUTE_MATCH`, `CONDITIONAL_ROUTE_MATCH` and a guarded
`NO_SUPPORTED_ROUTE_MATCH`. The last requires an explicitly complete frozen inventory and always
carries wording that it is not permanent legal impossibility. The Phase 7B first-wave policy permits
positive and conditional conclusions only until completeness is independently proven.

## Consequences

Scenario metrics are not smuggled into the first contract. A future result family requires a new
schema and owner-approved source gate.

## Alternatives considered

A 0-10 feasibility score and favorable/unfavorable enum were rejected as opaque and legally unsafe.
