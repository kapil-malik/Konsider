# ADR 015: Explicit consent for browser retention

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

Tab memory supports guest use without durable storage. Same-device convenience can be useful, but
silently persisting profile facts would surprise users and expand exposure.

## Decision

Default retention is `TAB_MEMORY_ONLY`. Same-device retention requires an explicit `GRANTED` consent
marker, records policy version and consent time, and expires within 30 days. Exact date of birth is
never device-retained. Incompatible profile or policy versions invalidate stored data. Clear/delete
is available without an account.

## Consequences

Closing the tab clears default context. A later UI must explain and request durable storage rather
than preselecting it. Export is user-initiated and redacted by default.

## Alternatives considered

Silent local storage and indefinite retention were rejected. Server persistence was rejected by ADR
014. Session cookies carrying profile values were rejected because they still transmit sensitive data.
