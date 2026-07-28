# Release format

Konsider publishes immutable directories under `data/releases/RELEASE_ID`. The only mutable release
file is the sibling `active.json` pointer. Production currently uses release schema 4 and consumer
catalog schema 2 for explicit mixed-coverage outcomes. Historical schema-3 releases remain
immutable and loadable with their matching schema-1 catalogs.

Schema 5/catalog 3 are implemented as the inactive Phase 5 target. They use canonical geographic
entities, entity-neutral observations/scores, a country-result outcome matrix, explicit derived
evidence, multiple-source lineage, locality universes, aggregation policies, and snapshotted
criterion ingestion policies. See the
[Phase 5C foundation](../architecture/phase5c-generic-release-foundation.md). The active schema-4
bytes and pointer are unchanged.

```text
data/
  catalogs/
    consumer-catalog-1.0.json
    consumer-catalog-2.0.json
  raw/
    SOURCE_ID/              # ignored third-party bytes and capture metadata
  releases/
    active.json
    RELEASE_ID/
      manifest.json
      observations.jsonl
      scores.jsonl
      attempts.jsonl
      raw-artifacts.json
      sources.json
      scoring-sensitivity.json
      validation.json
```

Release and report writers emit UTF-8 JSON, JSONL, and Markdown with explicit LF newlines on every
operating system. Payload checksums are calculated only after those final bytes are closed on disk;
`.gitattributes` independently enforces LF for committed release JSON and JSONL. Corrections create
a new release ID and never rewrite a historical directory.

Country-universe and coverage-audit outputs live under `data/reports/country-coverage/AUDIT_ID`.
They are diagnostic artifacts, not releases, are never selected by `active.json`, and do not relax
the publication contract. The authoritative stable list and its audit/licensing decision live in
`data/country-universes/stable-supported-v1.json`; release manifests embed the universe ID, policy
version, source audit ID, country count/codes, and licensing decision.

## Files

| File | Role | Classification |
| --- | --- | --- |
| `active.json` | Selects release ID and compatible release schema. | Mutable activation pointer. |
| `manifest.json` | Publication status, country count/codes and universe metadata, observation/score/attempt counts, criteria, timestamps, previous ID, source/parser/observation/scoring versions, payload and aggregate checksums, validation summary, replay metadata. | Authoritative release envelope. |
| `observations.jsonl` | Source-backed values, units, periods, scope, flags, exact artifact/record provenance, and component lineage. | Authoritative normalized observations. |
| `scores.jsonl` | Canonical versioned 1-10 score, direction, transform, and input observation IDs. Schema 3 requires every pair; schema 4 permits rows only for explicit valid outcomes. | Authoritative derived scores. |
| `attempts.jsonl` | Schema 3 acquisition attempts or schema 4's exact criterion/country outcome matrix with normalized reasons. | Authoritative completeness record. |
| `raw-artifacts.json` | Capture URLs, response metadata, local raw path, source version, byte size, and SHA-256. | Authoritative raw inventory; bytes remain ignored. |
| `sources.json` | Frozen publisher, methodology, licence, attribution, URL, parser, criterion, and source version. | Authoritative release source contract. |
| `validation.json` | Structural issues, coverage, criterion readiness, blockers, warnings, and product gate. | Authoritative readiness decision. |
| `scoring-sensitivity.json` | Alternative methods, distributions, component years/correlations, and perturbation results. | Diagnostic review artifact. |
| consumer catalog | Countries, criterion labels/meaning/caveats/readiness, coverage policy, experimental flags, and provisional profiles. | Separately versioned consumer contract with a release-scoped snapshot. |

The catalog remains outside immutable release directories. The current aliases are
`consumer-catalog-1.0.json` and `consumer-catalog-2.0.json`; immutable release-scoped snapshots live
under `data/catalogs/releases/{release_id}.json`. The repository prefers the matching snapshot and
validates its compatible schema major, exact country/criterion set, readiness, coverage metadata,
and scoring methods against the selected release. This allows historical releases to remain
loadable after a later catalog adds criteria.

## Checksums

`manifest.file_checksums` maps each of the seven payload files to SHA-256 over exact committed bytes.
`manifest.release_checksum` is SHA-256 over the canonical compact JSON serialization of that sorted
checksum map. Raw artifact IDs and metadata separately identify the original ignored bytes by
SHA-256. The manifest itself is not included in its payload checksum map.

The active consumer rejects missing or mismatched files before serving product data. Full replay
also reloads raw bytes, verifies their hashes, reparses them using embedded registrations, and
compares regenerated observations, attempts, and scores.

## Provenance and derivation

```text
SourceRegistration
  -> RawArtifact (exact bytes and HTTP metadata)
  -> MetricObservation (artifact + record/cell locator)
  -> MetricScore (input observation IDs + method version)
  -> request-time contribution (score x normalized user weight)
  -> deterministic total and rank
```

Request-time contributions and totals are not published release files. They are calculated by the
recommendation service from canonical scores and user weights.

## Readiness layers

- Structural validation checks contracts, counts, checksums, registrations, provenance, attempts,
  types, units, ranges, and score lineage.
- Criterion readiness additionally requires acceptable licence, coverage, freshness, and quality.
- Aggregate product readiness currently requires at least five ready criteria.

An aggregate pass does not make every criterion ready. Active UHC remains non-ready and is excluded
at the repository/service boundary. Fixtures never fill release gaps.

Machine-readable Draft 2020-12 schemas live in `contracts/schemas/v1` for release 3/catalog 1 and
`contracts/schemas/v2` for release 4/catalog 2. The inactive schema-5/catalog-3 contracts live in
`contracts/schemas/v3`. See the
[worker guide](../operations/worker.md), [contracts README](../../contracts/README.md), and
[release history](../history/releases/README.md). The schema-4 invariants and fixture boundary are
documented in the [Phase 4C coverage contract](phase4c-coverage-contract.md).
