# Release format

Konsider publishes immutable directories under `data/releases/RELEASE_ID`. The only mutable
release file is the sibling `active.json` pointer. The public runtime accepts only release schema 5
with embedded consumer catalog schema 3. Historical schema-3/4 releases and their catalog snapshots
remain immutable; an explicitly configured internal historical loader can open them for audit.

Active release `2026-08-04.1` contains the complete Phase 5 ranking structure unchanged, plus the
release-5.1 Opportunity Filter binding: canonical geographic
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
    opportunity-filter-catalog.json
    opportunity-filter-evidence.jsonl
    opportunity-filter-source-manifest.json
    opportunity-filter-threshold-policies.json
    opportunity-filter-evidence-policy.json
    opportunity-filter-coverage-summary.json
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

## Active Opportunity Filter extension

Phase 6D defined the additive release-5.1 contract. Phase 6E staged five career filters, Phase 6F
completed the nine-filter evidence candidate, and Phase 6G produced the deterministic API
candidate. Phase 6I transformed its release identity, revalidated all retained input checksums, and
published the final 819-row binding as `2026-08-04.1`.

A 5.1 release binds six checksummed sibling files: Opportunity Filter catalog, country
evidence, source manifest, threshold policies, evidence policy and coverage summary. The OFC
catalog remains separate from `consumer-catalog.json`, which continues to own score-bearing
ordering criteria.

Release 5.0 manifests omit the binding and remain valid. A 5.1 bundle must store one explicit state
for every declared filter-country pair; no loader may infer an omitted row as insufficient. See
the [Opportunity Filter contracts](../architecture/opportunity-filter-contracts.md).

The evidence and replay inputs are documented in [Career Opportunity Filter evidence](career-opportunity-evidence.md)
and [Education Opportunity Filter evidence](education-opportunity-evidence.md). The Phase 6G
filter engine is documented in [Opportunity Filter engine](../product/opportunity-filter-engine.md).
The active release is `2026-08-04.1` on release schema 5.1.

The catalog is part of the immutable release and is covered by both its artifact binding and the
release file-checksum map. The runtime has no mutable Opportunity Filter catalog alias. Historical
release-scoped ordering catalogs under `data/catalogs/releases/` remain only for opening history.

## Draft Phase 7 TFC extension

Phase 7C defines `tfc-release-binding-1.0`; Phase 7D implements the draft-only
`konsider-release-6.0` manifest and candidate repository. A candidate binds the immutable checksum
of a release-5.1 base plus a TFC catalog, typed destination rule/evidence JSONL, policy bundles,
source/legal manifest, coverage summary and validation report.

The rule/evidence union contains explicit jurisdictions, one support row per staged TFC and stable
country, route rules and typed metric formulas. Missing support rows are invalid. Every mutable rule
has effective, verification, staleness, supersession and conflict metadata. The writer uses sorted
LF-stable serialization and SHA-256; replay compares all payloads and the manifest byte-for-byte.

The Phase 7D repository deliberately has no publication or activation method. Its committed input
is fictional, its catalog is `SYNTHETIC_ONLY`, and its scenario metric is an architecture fixture,
not an approved TFC. Profile inputs and computed outcomes remain request-time data and are
prohibited from immutable releases. Active release `2026-08-04.1` remains unchanged. See the
[TFC release foundation](../architecture/tfc-release-foundation.md).

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
