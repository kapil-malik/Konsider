# Data Refresh Worker

Status: first local vertical slice implemented

Last updated: 2026-07-18

## Responsibility

The data refresh worker converts approved public information into a validated, publishable
Konsider dataset release. It may run on a weekly schedule or from an authorized manual trigger.
It does not serve user requests and does not mutate an active release in place.

The worker is an ordinary Python executable first:

```powershell
$env:PYTHONPATH = "src"
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N
python -m konsider.ingestion.worker replay data\releases\2026-07-18.2
```

AWS Lambda or ECS adapters should be thin wrappers around the same command/service code.

## Processing Stages

1. Resolve requested source registrations, countries, criteria, and refresh window.
2. Create a refresh-run record and a draft dataset release.
3. For each registered source, determine the source-specific country/criterion coverage.
4. Fetch each source with bounded retries, timeouts, rate limits, and source-specific credentials.
5. Store the original payload or document with content type, retrieval metadata, and checksum.
6. Extract source-backed text evidence and raw metric observations.
7. Record coverage status by source/country/criterion: `success`, `no_data`, `failed`, or
   `rejected`.
8. Normalize units, geography, date ranges, and metric direction.
9. Derive 1-10 scores using a versioned methodology; retain the input observations.
10. Validate completeness, ranges, freshness, duplicates, provenance, and material score changes.
11. Publish atomically when the release passes, or retain it as failed/draft for diagnosis.

## Inputs

The worker consumes a source registry rather than arbitrary URLs supplied at runtime.

```json
{
  "source_id": "example-public-api",
  "kind": "api",
  "base_url": "https://example.org/api",
  "coverage": {
    "country_ids": ["canada", "germany"],
    "criterion_ids": ["uhc_service_coverage_index"]
  },
  "schedule": "rate(7 days)",
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
  "criterion_ids": ["uhc_service_coverage_index"],
  "publish_if_valid": true
}
```

## Outputs and Handshake

The worker communicates with the live engine through published storage contracts, not direct
process calls. Its principal outputs are:

- `RefreshRun`: status, scope, attempts, counts, timings, and errors.
- `RawArtifact`: immutable source body or file, request metadata, content hash, and retrieval time.
- `EvidenceItem`: source-backed excerpt or document with country/criterion tags.
- `MetricObservation`: raw value, unit, effective period, geography, source, and parser version.
- `MetricScore`: normalized score, derivation inputs, method version, and confidence.
- `DatasetRelease`: immutable manifest, catalog, metrics, evidence, and validation summary.

Publication must update the active-release pointer atomically. A release manifest includes a schema
version and checksums so consumers can detect incompatible or incomplete data.

## Idempotency and Failure Handling

- A run has an idempotency key derived from source, scope, and effective refresh window.
- Raw artifacts are content-addressed; repeated downloads do not create conflicting facts.
- Connector retries are bounded and jittered. Permanent source failures do not erase the previous
  published release.
- Sources are allowed to cover subsets. Missing data is explicit and evaluated against required
  coverage rules.
- One failed optional source may produce warnings; a missing required metric blocks publication.
- Material score movement beyond configured thresholds requires review or an explicit override.
- Failed and superseded releases remain auditable and are never selected for live requests.

## Technology

- Python 3.11 or newer.
- HTTP clients and source-specific SDKs behind connector interfaces.
- Structured parsing and validation with typed models.
- Local filesystem release writer for development.
- S3 release writer for production raw artifacts and published releases.
- EventBridge Scheduler for recurring triggers and an authenticated administrative trigger for
  manual runs.
- Lambda for weekly refresh jobs while execution is reliably under the Lambda timeout limit.
- Scheduled ECS Fargate task only for browser automation, large documents, or long-running jobs.
- Step Functions only after simple scheduler-driven execution becomes too limited.

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
