# ADR 019: Centralized display metadata and release versioning

Status: accepted

## Context

Ordering criteria, Opportunity Filters, and Typed Feasibility Checks historically stored public
titles in separate production builders and exposed different field names in their immutable
catalogs. The display-metadata migration changes those catalog shapes while preserving every
visible string and every technical outcome.

Historical release schemas and published releases are immutable. Konsider also distinguishes a
catalog contract major from the release manifest version that binds the catalog: release 5.1, for
example, additively introduced an Opportunity Filter artifact family while retaining release-5
orchestration.

## Decision

The authoritative authoring source is
`data/catalogs/product-display-catalog.json`, validated as
`konsider-product-display-catalog-1.0`. Technical builders join it by stable product role and ID;
evidence, scoring, policies, and rules do not receive display metadata.

New immutable snapshots use breaking catalog majors:

- `consumer-catalog-4.0`;
- `opportunity-filter-catalog-2.0`; and
- `tfc-release-catalog-2.0`.

The new ranking/OFC base uses `konsider-release-5.2`. The new TFC overlay uses
`konsider-release-6.1` and checksum-binds that exact 5.2 base. These are minor release-manifest
increments because base and overlay orchestration remain unchanged and each manifest explicitly
binds the new catalog major. The breaking compatibility boundary is the catalog schema version,
not an implicit mutation of a release-5.1 or release-6.0 artifact.

API transport is independently versioned as `konsider-api-3.0` under `/api/v3` because its field
renames are breaking for clients.

Release manifests and build reports record the authoring schema version, authoring catalog
version, authoring checksum, emitted catalog checksums, and the no-copy-change equivalence result.

## Consequences

- Existing 5.1/6.0 schemas and releases remain byte-immutable and readable by historical loaders.
- Current public names have one authoring authority and remain pinned inside each published
  release snapshot.
- Consumers must select the catalog major declared by the release instead of assuming that every
  release-5 or release-6 catalog has the same fields.
- The base and overlay must be published and activated as one checksum-bound pair; a 6.1 overlay
  cannot bind a 5.1 base.
- Rollback continues to select an older immutable pointer rather than dual-writing aliases into
  new snapshots.
