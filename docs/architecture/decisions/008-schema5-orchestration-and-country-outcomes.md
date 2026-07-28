# ADR 008: Schema-5 orchestration and country-result outcomes

Status: accepted

Date: 2026-07-28

## Context

Phase 4 ingestion is country-specific and its outcome builder assumes one source registration per
criterion. Phase 5 needs one path for national and locality evidence, more than one source input,
replayable derived country results, and immutable release/catalog snapshots. It must preserve every
schema-3/4 byte and must not implement the Phase 5D ranking or locality-coherence algorithms.

The target contracts also left one question open: whether every locality needs its own explicit
outcome row.

## Decision

Schema-current ingestion uses a declarative criterion-policy snapshot. Each policy names its
criterion, source lineages, parser, scoring method, coverage mode, geographic scope, derivation,
applicability, readiness, and experimental state. Versioned processors remain code, but a release
records exactly which processor IDs and versions produced it. A policy may reference multiple
lineages, and each lineage may contain multiple typed source inputs.

Release 5 uses row-oriented JSONL for entities, observations, scores, country outcomes, and derived
evidence. Smaller registries and policies use sorted JSON. This keeps large locality payloads
streamable while making configuration snapshots easy to inspect. The release includes
`criterion-policies.json`; catalog 3 is embedded and also copied to an immutable release-scoped
snapshot on publication.

Explicit outcomes are required at the country result level only:

- every criterion/country pair has exactly one valid, missing, stale, invalid, or rejected outcome;
- locality observations and scores are evidence inventory, not a second outcome matrix;
- a locality missing from an expected universe contributes to the country outcome and evidence
  quality, rather than creating an N-by-criterion locality outcome table; and
- no locality entity can appear as a country outcome subject.

A valid locality-derived outcome references a generated country observation, generated country
score, and derived-evidence record. The evidence record identifies both generated result IDs and
all contributing locality observation/score IDs. This closes the replay chain in both directions.

Schema-3/4 repositories remain the only consumers for the current `/api/v1` active release.
Schema-5 has a separate writer/loader, so enabling its contract support cannot accidentally make
the old API interpret a locality release through country-only joins. Activation is an explicit
option; schema-5 publication does not move `active.json` by default during Phase 5C.

## Consequences

- Coverage, scope, and applicability remain independent and are checked against the catalog rather
  than inferred from each other.
- The generic worker accepts national FCC, national PCC, locality-derived FCC, locality-derived
  PCC, and diagnostic policies without a phase-specific release builder.
- Replay rebuilds every schema-5 payload file and compares exact bytes. Missing intentionally
  uncommitted source bytes produce `SOURCE_BYTES_UNAVAILABLE`, distinct from a deterministic
  mismatch.
- Release validation reconciles entity parentage, locality-universe membership, policy versions,
  multiple-source lineage, observations, scores, outcomes, derived evidence, catalog coverage,
  validation counts, manifest counts, and checksums.
- Phase 5D owns aggregation algorithms and locality-coherence ranking behavior. Phase 5C only
  executes injected, versioned processors and validates their outputs.

## Alternatives considered

An explicit outcome per locality was rejected because the selected locality universe already owns
eligibility and because sparse locality evidence would create a large duplicate status matrix.
Locality evidence remains fully explicit through observations, scores, universes, quality flags,
and derived evidence.

One JSON file for the entire release was rejected because locality payloads need streamable,
diffable records. Criterion-specific release builders were rejected because they recreate the
Phase 4F/Wave 2 migration problem and obscure shared validation.

## Revisit when

Phase 5E activates the API-v2 consumer. At that point the active-release dispatcher can add
schema-5/catalog-3 loading without weakening the historical schema-3/4 adapter.
