# ADR 018: Future saved-profile persistence as an adapter

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

Future accounts may save multiple applicant profiles, households, scenarios and revisions. The
current domain must not depend on a database or ownership system that does not exist.

## Decision

Persistence remains outside the Phase 7 domain. A future adapter may implement ports for saved
profiles, households, scenarios, revisions, ownership, import/export and migration from guest
storage. It must resolve a saved revision into an explicit `EffectiveProfileContext` before
evaluation. No repository interface, CRUD service, database or authentication implementation is
added in Phase 7C because no runtime consumer exists yet.

## Consequences

Stateless evaluation remains testable and storage-independent. A later persistence phase can add
ports at the application boundary without changing TFC result semantics.

## Alternatives considered

Building speculative repositories now was rejected as unused architecture. Making evaluation query
an account store was rejected because it introduces hidden mutable context.
