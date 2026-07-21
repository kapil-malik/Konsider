# Storage Architecture

Status: worker stabilization storage decision record

Last updated: 2026-07-20

## Goals

Storage must make every recommendation reproducible, preserve original evidence, support atomic
dataset publication, and allow local file adapters to evolve into AWS-backed repositories. The
first production design should fit the expected scale: weekly refreshes, small catalog data,
fewer than 1,000 non-LLM API calls per day, and limited chat usage.

The guiding decision is: **use immutable release artifacts first; add databases only for mutable
state or proven query pressure.**

## Storage Classes

| Class | Examples | Mutability | Local store | Initial AWS store |
| --- | --- | --- | --- | --- |
| Raw source artifacts | API JSON, XLSX, headers, checksums | Immutable | Ignored files under `data/raw/` | Private S3 only after licence/security review |
| Extracted evidence | Clean snippets, document sections, source tags | Immutable by release | JSONL | S3 release artifact |
| Metric observations | Raw values, units, effective periods, source lineage | Immutable by release | JSONL | S3 release artifact |
| Metric scores | Normalized 1-10 values, confidence, method version | Immutable by release | JSONL | S3 release artifact |
| Catalog | Countries, criteria, profile templates, caveats | Separately versioned; checked against release | `data/catalogs/consumer-catalog-1.0.json` | S3 versioned artifact |
| Release manifests | Version, checksums, validation summary, active pointer | Immutable except pointer | JSON files | S3 objects |
| Refresh operations | Run status, counts, failures, manual trigger metadata | Append/update status | JSON logs first | DynamoDB later if needed |
| User profiles | Saved custom weights and revisions | Mutable with history | Deferred/local state | DynamoDB after accounts exist |
| Conversation state | Messages, tool events, citations, usage | Append-oriented | In memory or local dev file | DynamoDB after chat persistence exists |
| Retrieval index | Embeddings or lexical index | Rebuildable | None initially | Derived index later, not source of truth |

## Dataset Release Shape

A release is an immutable directory or S3 prefix. The active release is selected by a small pointer
file or object.

```text
releases/
  active.json
  2026-07-20.2/
    manifest.json
    observations.jsonl
    scores.jsonl
    attempts.jsonl
    raw-artifacts.json
    sources.json
    scoring-sensitivity.json
    validation.json
raw/
  source_id/
    sha256.bin
    sha256.json
catalogs/
  consumer-catalog-1.0.json
```

The catalog is deliberately separate from each release. This avoids modifying published release
`2026-07-20.2`; the consumer validates its schema major, exact criterion set, scoring versions, and
readiness against the active release before returning records.

Minimum release metadata:

```json
{
  "release_id": "2026-07-20.2",
  "schema_version": "konsider-release-3.0",
  "source_versions": {"world_bank_pm25": "EN.ATM.PM25.MC.M3@WDI-2026-07-13"},
  "scoring_method_versions": ["pm25_health_bands_v1"],
  "status": "published",
  "created_at": "2026-07-17T08:00:00Z",
  "published_at": "2026-07-17T10:00:00Z",
  "release_checksum": "sha256:...",
  "validation_summary": {
    "structural_passed": true,
    "product_ready": true,
    "ready_criterion_count": 5,
    "criterion_readiness": {"uhc_service_coverage_index": false}
  }
}
```

Published records are not edited. Corrections produce a new release. Rollback changes
`active.json` to an earlier compatible release and records who performed the operation and
why.

## Canonical Metric Records

The UI may present a matrix with countries as rows and criteria as columns, but storage should keep
metrics in long form.

```json
{
  "release_id": "rel_2026_07_17_01",
  "country_id": "canada",
  "criterion_id": "uhc_service_coverage_index",
  "raw_value": 78.4,
  "unit": "index",
  "normalized_score": 8.1,
  "confidence": 0.82,
  "methodology_version": "uhc_coverage_bands_v1",
  "observation_ids": ["obs_123"],
  "evidence_ids": ["ev_456"],
  "effective_date": "2026-01-01"
}
```

This shape allows more than one observation per criterion, preserves source lineage, and avoids
schema churn when criteria are added.

## Provenance Chain

Every `MetricScore` links to its `MetricObservation` inputs. Every observation and evidence item
links to a `RawArtifact` and `SourceRegistration`. Required provenance includes:

- Canonical source ID and public URL when redistribution permits it.
- Retrieval timestamp and source effective period.
- HTTP or file metadata and content checksum.
- Connector, parser, normalization, and scoring-method versions.
- Geographic scope, unit, and transformation notes.
- Confidence, quality flags, and human overrides with actor and reason.
- Attempt status for source/country/criterion coverage: `success`, `no_data`, `failed`, or
  `rejected`.
- For a derived observation, exact per-component value, unit, reference year, artifact, and source
  record; unrelated downloaded artifacts are never attached to the observation.

This chain allows the engine to answer "why does this score exist?" without relying on generated
text.

## Evidence and Retrieval

For Phase 1 and early production, metadata-filtered evidence lookup is enough:

```text
country_id + criterion_id + optional source/topic filters -> evidence items
```

A vector database is not required until the evidence corpus grows large enough that exact metadata
filtering and simple lexical search feel limiting. Embeddings should be treated as derived,
rebuildable data. The authoritative evidence remains `evidence.jsonl` and raw artifacts.

When a vector index is introduced, each vector record must include release ID, evidence ID,
country IDs, criterion IDs, source ID, and chunk checksum so the index can be rebuilt and audited.

## Profiles and Sessions

Profile persistence should be phased:

1. Template profiles live in the catalog and are served by the live engine.
2. User edits live in React state and can be sent to `POST /api/v1/rankings`.
3. Chat-modified profiles live in server session state for the duration of a conversation.
4. Saved custom profiles require user accounts and durable storage, likely DynamoDB first.

The UI should not hardcode template profiles except as fallback test fixtures. The API catalog is
the source of truth for profile labels, default weights, caveats, and version metadata.

## Logical Repository Interfaces

Python services depend on narrow interfaces rather than storage clients:

- `ReleaseRepository`: active release, release by version, publish/rollback operations.
- `CatalogRepository`: countries, criteria, and profile templates for a release.
- `MetricsRepository`: country/criterion scores and observation lineage.
- `EvidenceRepository`: filtered evidence lookup and later semantic search.
- `ProfileRepository`: revision-controlled user weights and templates.
- `ConversationRepository`: messages, typed events, tool calls, citations, and usage counters.

`PublishedReleaseRepository` is the product adapter for active releases. The
`FixtureProjectDataRepository` remains a clearly isolated legacy test adapter and is never a
fallback for catalog, metrics, observations, or evidence reads.

## Local and AWS Mapping

| Concern | Local Phase 1 | Initial AWS direction | Escalation path |
| --- | --- | --- | --- |
| Published release | Fixture files or generated local release directory | S3 prefix plus active pointer object | Database-backed manifest only if needed |
| Raw artifacts | Files under `raw/` | S3 with checksums and metadata | Lifecycle policies for large files |
| Metrics/catalog/evidence | JSON/JSONL/CSV fixtures | S3 release artifacts loaded into API memory | DynamoDB/SQL if query volume or data size demands it |
| Evidence retrieval | Metadata filter | Metadata filter over loaded release | Vector index when corpus justifies it |
| Profiles/conversations | React state or in-memory server state | DynamoDB after persistence is needed | SQL only if relational reporting becomes important |
| Refresh runs | Local run logs | CloudWatch logs plus optional DynamoDB item | Step Functions if orchestration state becomes complex |

## Security, Retention, and Recovery

- Encrypt S3 and databases at rest and require TLS in transit.
- Separate public-source data from user and conversation data with distinct access policies.
- Avoid collecting sensitive personal data until retention and deletion requirements are defined.
- Store credentials in Secrets Manager, not source registrations or application tables.
- Enable S3 versioning for production release buckets.
- Define lifecycle policies for large raw artifacts while retaining manifests, checksums, and
  required audit records.
- Backups are useful only when restore and active-release rollback procedures are tested.
