# ADR 011: Typed Feasibility Checks as a sibling product role

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

The approved checks answer applicant-specific route questions. Ordering criteria calculate affinity,
while Opportunity Filters describe destination-side ecosystems. Neither contract can safely own a
legal-route assessment.

## Decision

`TFC` is a separate product role with its own catalog, evidence, policy and outcome contracts. A TFC
has no weight, score direction, normalization, affinity contribution, PCC threshold, LSC aggregation
or Opportunity Filter state. Phase 7C defines three inactive route checks only.

## Consequences

TFCs can evolve without changing ranking semantics. Adding one requires source qualification,
immutable evidence onboarding and release activation rather than a catalog-only edit.

## Alternatives considered

Score-bearing criteria and zero-weight criteria were rejected because both invite ranking behavior.
Opportunity Filter reuse was rejected because route outcomes depend on explicit applicant context.
