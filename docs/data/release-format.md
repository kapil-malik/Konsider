# Release format

Konsider publishes immutable directories under `data/releases/RELEASE_ID`. The only mutable
release file is the sibling `active.json` pointer. The public runtime accepts only release schema 5
with embedded consumer catalog schema 3. Historical schema-3/4 releases and their catalog snapshots
remain immutable; an explicitly configured internal historical loader can open them for audit.

Active release `2026-07-29.2` contains the complete Phase 5 structure: canonical geographic
entities, entity-neutral observations and scores, one explicit criterion outcome per country,
derived locality evidence, multiple-source lineages, locality universes, aggregation policies,
criterion ingestion policies, and `preference_presets`.

```text
data/releases/
  active.json
  RELEASE_ID/
    manifest.json
    consumer-catalog.json
    geographic-entities.jsonl
    observations.jsonl
    scores.jsonl
    criterion-outcomes.jsonl
    derived-country-evidence.jsonl
    source-lineages.json
    locality-universes.json
    aggregation-policies.json
    criterion-policies.json
    validation.json
```

Writers emit UTF-8 JSON and JSONL with explicit LF newlines on every operating system. Payload
checksums are calculated only after final bytes are closed. `.gitattributes` independently enforces
LF for committed release artifacts. Corrections always create a new release ID.

## Files and ownership

| File | Role |
| --- | --- |
| `active.json` | Mutable pointer selecting the one public schema-5 release. |
| `manifest.json` | Release/catalog versions, artifact counts, policy IDs, readiness, payload checksums, aggregate checksum, previous release, and replay metadata. |
| `consumer-catalog.json` | Countries, orthogonal criterion coverage/scope/applicability, display metadata, readiness, thresholds, sources, and preference presets. |
| `geographic-entities.jsonl` | Canonical country and locality identities plus containment relationships. |
| `observations.jsonl` | Source-backed values, units, periods, quality flags, exact provenance, and entity IDs. |
| `scores.jsonl` | Versioned canonical scores linked to input observations. |
| `criterion-outcomes.jsonl` | One explicit country/criterion availability outcome and normalized reason. |
| `derived-country-evidence.jsonl` | Country results derived from localities, including contributors and aggregation lineage. |
| `source-lineages.json` | Versioned one-or-more-source derivation graphs and attribution. |
| `locality-universes.json` | Frozen criterion-independent locality selection and membership. |
| `aggregation-policies.json` | Versioned selection and aggregation rules for locality-derived country results. |
| `criterion-policies.json` | Snapshotted criterion ingestion, coverage, scope, applicability, scoring, and assessment policy. |
| `validation.json` | Structural, coverage, readiness, policy, lineage, and product-gate results. |

## Staged Opportunity Filter extension

Phase 6D defines an additive release-5.1 contract. Phase 6E now exercises it with inactive draft
fragment `phase6e-career-2026-08-03.1`; it does not publish or activate that fragment. A future 5.1
release may bind six checksummed sibling files: Opportunity Filter catalog, country evidence,
source manifest, threshold policies, evidence policy and coverage summary. The OFC catalog remains
separate from `consumer-catalog.json`, which continues to own score-bearing ordering criteria.

Release 5.0 manifests omit the binding and remain valid. A 5.1 bundle must store one explicit state
for every declared filter-country pair; no loader may infer an omitted row as insufficient. See
the [Opportunity Filter contracts](../architecture/opportunity-filter-contracts.md).

The Phase 6E staged fragment and replay instructions are documented in
[Career Opportunity Filter evidence](career-opportunity-evidence.md). The active release remains
`2026-07-29.2` on release schema 5.0.

The catalog is part of the immutable release and is covered by its checksum. There is no active
catalog alias or runtime catalog override. Historical release-scoped catalogs under
`data/catalogs/releases/` remain only for opening schema-3/4 history.

## Checksums and replay

`manifest.file_checksums` maps every release payload to SHA-256 over exact committed bytes.
`manifest.release_checksum` is the SHA-256 over the canonical compact JSON serialization of that
sorted checksum map. The manifest itself is not included in its payload map.

The active consumer rejects a missing file, checksum mismatch, unsupported schema, inconsistent
entity/policy/criterion set, invalid outcome matrix, or non-product-ready release before serving
data. Full replay additionally reconstructs the normalized artifacts from retained inputs and
compares the result byte-for-byte.

```powershell
python -m konsider.ingestion.phase5_locality_onboarding `
  --replay data\releases\2026-07-29.2
```

## Provenance and derivation

```text
source artifact + source lineage
              |
              v
entity observation -> canonical score
              |
              +--> direct national country result
              |
              +--> locality contributors + aggregation policy
                                      |
                                      v
                         derived country evidence
                                      |
                                      v
                    country/criterion outcome
                                      |
                                      v
                    request-time contribution
```

Request-time contributions, normalized weights, ranks, coverage robustness, locality compatibility,
and profile applicability are not release artifacts. The recommendation service calculates them
from validated release facts and returns them as separate structured assessments.

## Compatibility boundary

Machine-readable Draft 2020-12 schemas live in `contracts/schemas/v1` for historical release
3/catalog 1, `contracts/schemas/v2` for historical release 4/catalog 2, and
`contracts/schemas/v3` for active release 5/catalog 3. Published historical contracts are never
weakened or rewritten. The public API does not translate them; audit code must explicitly name the
historical release it intends to load.

See the [Phase 5C foundation](../architecture/phase5c-generic-release-foundation.md),
[worker guide](../operations/worker.md), [contracts README](../../contracts/README.md), and
[release history](../history/releases/README.md).
