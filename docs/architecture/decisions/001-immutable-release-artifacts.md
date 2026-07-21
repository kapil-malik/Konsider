# ADR 001: Immutable release artifacts

Status: accepted

## Context

Recommendations must be reproducible and source corrections must remain auditable.

## Decision

Data is published as immutable versioned releases. Published directories are never edited;
corrections receive a new release ID. `active.json` selects the current release. The worker writes
releases, the recommendation service reads them, and the API never refreshes data during a request.
Fixtures never fill gaps in product releases.

## Consequences

Rollback changes only the pointer and requires an API restart. Storage retains historical releases,
and release IDs must always be new. Packaging corrections such as `2026-07-21.1` remain separate
from the original release.

## Alternatives considered

Mutable tables and in-place file correction were rejected because they weaken replay and auditability.

## Revisit when

Measured release size or query patterns require another physical representation without weakening
versioning, checksum validation, lineage, or atomic activation.
