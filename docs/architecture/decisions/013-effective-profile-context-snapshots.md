# ADR 013: Explicit effective profile context snapshots

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

Route results must be reproducible against the facts, taxonomy versions and effective rules used at
evaluation time. Mutable profiles cannot provide that identity.

## Decision

Every evaluation consumes an immutable request-scoped `EffectiveProfileContext` containing
normalized applicant, household and scenario values, selected TFCs, taxonomy versions, an evaluation
timestamp and a canonical SHA-256 snapshot hash. Mutable client IDs and evaluation time are excluded
from the hash; normalized values and versions are included.

## Consequences

Results can cite one context identity without storing the context server-side. Editing any evaluated
value creates a new snapshot. A mutable saved profile is never itself the evaluation object.

## Alternatives considered

Hashing an account or profile ID was rejected because it does not identify values. Hashing timestamps
was rejected because identical inputs would lose deterministic identity.
