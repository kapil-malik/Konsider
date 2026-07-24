# Release format

Konsider publishes immutable directories under `data/releases/RELEASE_ID`. The only mutable release
file is the sibling `active.json` pointer. The current consumer schema major is 3.

```text
data/
  catalogs/
    consumer-catalog-1.0.json
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

Published files are LF-normalized by `.gitattributes`. Corrections create a new release ID; they do
not rewrite a historical directory.

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
| `scores.jsonl` | Canonical versioned 1-10 score, direction, transform, and input observation IDs for every country/criterion pair. | Authoritative derived scores. |
| `attempts.jsonl` | Expected acquisition result per source/country/criterion. | Authoritative completeness record. |
| `raw-artifacts.json` | Capture URLs, response metadata, local raw path, source version, byte size, and SHA-256. | Authoritative raw inventory; bytes remain ignored. |
| `sources.json` | Frozen publisher, methodology, licence, attribution, URL, parser, criterion, and source version. | Authoritative release source contract. |
| `validation.json` | Structural issues, coverage, criterion readiness, blockers, warnings, and product gate. | Authoritative readiness decision. |
| `scoring-sensitivity.json` | Alternative methods, distributions, component years/correlations, and perturbation results. | Diagnostic review artifact. |
| consumer catalog | Countries, criterion labels/meaning/caveats/readiness, experimental flags, and provisional profiles. | Separately versioned consumer contract. |

The catalog remains outside immutable release directories. The repository validates its compatible
schema major, exact country/criterion set, readiness, and scoring methods against the active release.

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

Machine-readable Draft 2020-12 schemas live in `contracts/schemas/v1`. See the
[worker guide](../operations/worker.md), [contracts README](../../contracts/README.md), and
[release history](../history/releases/README.md).
