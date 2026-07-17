# Data Refresh Worker

## Responsibility

The data refresh worker converts approved public information into a validated, publishable
Konsider dataset release. It may run on a schedule or from an authorized manual trigger. It does
not serve user requests and does not mutate an active release in place.

## Processing Stages

1. Resolve the requested source registrations, countries, metrics, and refresh window.
2. Create a refresh-run record and a draft dataset release.
3. Fetch each source with bounded retries, timeouts, rate limits, and source-specific credentials.
4. Store the original payload or document with content type, retrieval metadata, and checksum.
5. Parse source records into raw metric observations and qualitative evidence items.
6. Normalize units, geography, date ranges, and metric direction.
7. Derive 1-10 scores using a versioned methodology; retain the input observations.
8. Validate completeness, ranges, freshness, duplicates, provenance, and material score changes.
9. Publish atomically when the release passes, or retain it as failed/draft for diagnosis.

## Inputs

The worker consumes a source registry rather than arbitrary URLs supplied at runtime.

```json
{
  "source_id": "example-public-api",
  "kind": "api",
  "base_url": "https://example.org/api",
  "countries": ["canada", "germany"],
  "metrics": ["healthcare"],
  "schedule": "rate(30 days)",
  "connector": "example_api_v1",
  "license_notes": "Review before production use",
  "enabled": true
}
```

Manual triggers may narrow scope but may not bypass source registration or publication checks:

```json
{
  "requested_by": "admin-user-id",
  "source_ids": ["example-public-api"],
  "country_ids": ["canada"],
  "publish_if_valid": true
}
```

## Outputs and Handshake

The worker communicates with the live engine through published storage contracts, not direct
process calls. Its principal outputs are:

- `RefreshRun`: status, scope, attempts, counts, timings, and errors.
- `RawArtifact`: immutable source body or file, request metadata, content hash, and retrieval time.
- `MetricObservation`: raw value, unit, effective period, geography, source, and parser version.
- `EvidenceItem`: source-backed excerpt or document with country/metric tags.
- `MetricScore`: normalized score, derivation inputs, method version, and confidence.
- `DatasetRelease`: immutable manifest and validation summary.

Publication must update the active-release pointer transactionally. A release manifest includes a
schema version and checksums so consumers can detect incompatible or incomplete data.

## Idempotency and Failure Handling

- A run has an idempotency key derived from source, scope, and effective refresh window.
- Raw artifacts are content-addressed; repeated downloads do not create conflicting facts.
- Connector retries are bounded and jittered. Permanent source failures do not erase the previous
  published release.
- One failed optional source may produce warnings; a missing required metric blocks publication.
- Material score movement beyond configured thresholds requires review or an explicit override.
- Failed and superseded releases remain auditable and are never selected for live requests.

## Technology

- Python 3.11 or newer.
- HTTP clients and source-specific SDKs behind connector interfaces.
- Structured parsing and validation with typed models.
- EventBridge Scheduler for recurring triggers and an authenticated administrative trigger for
  manual runs.
- Step Functions when orchestration, fan-out, review, or retries need durable workflow state.
- Lambda for short bounded connectors; ECS Fargate tasks for browser automation, large documents,
  or long-running jobs.
- S3 for raw artifacts and PostgreSQL/Aurora for release metadata and structured records.

## Repository Placement

The deployable entrypoint belongs in `apps/worker`. Reusable connectors and pipeline behavior live
under `src/konsider/ingestion`; storage implementations live under
`src/konsider/repositories`. Phase 1 fixture files represent a pre-published local dataset and are
kept under `data/fixtures`.

## Testing Expectations

- Unit tests for each parser, normalizer, and score derivation.
- Contract fixtures captured from sources with sensitive data removed.
- Integration tests for draft creation, validation, and atomic publication.
- Replay tests proving the same raw artifacts and method version produce the same scores.
- Failure tests for timeouts, malformed content, schema drift, duplicates, and partial coverage.
