# System architecture

Status: authoritative architecture as of 2026-07-28

Konsider separates data acquisition, immutable publication, deterministic recommendation logic,
HTTP transport, and the browser UI. Scoring and readiness rules have one server-side owner.

## Implemented now

```text
Registered official sources
        |
        v
Local Python worker ---> data/raw/ (ignored, content-addressed bytes)
        |                  |
        |                  +--> non-publishing country-universe/coverage audit
        |
        v
data/releases/{release_id}/ + data/releases/active.json
        |
        v
PublishedReleaseRepository ---> RecommendationService ---> FastAPI /api/v1 ---> React/Vite UI
                                       ^                         |
                                       |                         v
                          consumer catalog             OpenAPI + JSON responses
```

- The worker downloads ten registered official-source distributions, captures exact raw bytes,
  parses observations, computes versioned canonical scores, validates readiness, and publishes an
  immutable release only when the gate passes.
- `PublishedReleaseRepository` validates the active pointer, schema majors, payload checksums,
  counts, readiness, scoring versions, and provenance before joining records.
- `RecommendationService` owns weight selection, normalization, contribution calculations,
  deterministic ranking, comparison, and country breakdowns.
- FastAPI and Pydantic provide a thin versioned transport. One validated release snapshot is loaded
  during process startup and reused. Requests never fetch sources or recompute canonical scores.
- Local files are the only implemented storage adapter. Legacy fixtures remain isolated tests and
  never fill product-release gaps.
- The responsive React UI derives profiles, priority controls, ranking columns, sources, flags, and
  release labels from `/api/v1`. TanStack Query owns API work; local state owns guest edits.

The active release is `2026-07-28.2`: 91 countries, twelve available criteria, eleven ready criteria,
and eight 91/91 global-core criteria. Overall job-market opportunity is conditionally scored for
its 88 valid countries when its raw weight reaches 0.6. UHC is diagnostic-only and cannot be
weighted. Infrastructure remains experimental.
Country-universe discovery and complete-case auditing are implemented as a separate safe worker
flow. They use UN migrant-stock/M49 inputs plus the registered criterion sources, write diagnostic
reports, and assert that `active.json` is unchanged. They do not share publication authority.

## Browser architecture

The Phase 2C React, TypeScript, and Vite browser application calls only `/api/v1`, derives countries,
criteria, profiles, labels, readiness, experimental flags, caveats, and sources from the catalog,
and keeps editable weights in browser state. The UI contains no scoring or readiness logic.

Local development will run Vite and Uvicorn as separate processes. The selected initial AWS design
uses S3 and CloudFront for static UI assets, API Gateway plus Lambda for FastAPI, S3 for raw and
release artifacts, and EventBridge Scheduler plus Lambda for refreshes. This is a design, not an
implemented deployment.

## Deferred options

Authentication, saved profiles, persistent sessions, chat, LLMs, retrieval, agents, MCP, mutable
databases, vector storage, and AWS infrastructure are not implemented. DynamoDB is reserved for
future mutable state. Containers or databases are introduced only when measured runtime, size,
query, persistence, or retrieval requirements justify them.

## Runtime ownership

| Concern | Authority | Must not own it |
| --- | --- | --- |
| Source registration and parsing | Worker registry and parsers | API and UI |
| Canonical observations and 1-10 scores | Immutable release | API request handlers and UI |
| Readiness and publication | Worker validation | UI visibility logic |
| Ranking semantics | `RecommendationService` | FastAPI routes and UI |
| HTTP shapes and errors | FastAPI OpenAPI/Pydantic models | Hand-written frontend guesses |
| Active dataset selection | `data/releases/active.json` | Per-request client input |

## Primary flows

### Refresh and publication

The worker captures source registrations and raw artifacts, creates observations and scores, writes
attempt and diagnostic records, validates the candidate, writes a draft, atomically promotes a new
release directory, and then replaces only `active.json`. A failed run cannot mutate a published
release or the active pointer.

### Country-universe and coverage audit

The worker builds a canonical ISO3 registry from official UN M49 and World Bank metadata, ranks
eligible destinations using official UN migrant stock, evaluates every catalog-enabled criterion,
and writes candidate, coverage, exclusion, source, and checksum reports. Online mode captures bytes;
offline mode deterministically replays them. The final stable universe is the 91-country
complete-case intersection under the approved WDI-only homicide licensing policy. Future country
count changes require a deliberate source and data review.

### API startup and request

At startup the API resolves and validates the active snapshot. Healthy requests reuse that in-memory
snapshot. Initialization failures leave the process running in controlled degraded mode; health and
product endpoints return safe `503` envelopes. Changing the pointer requires a restart.

### Ranking

The stable catalog remains 91 countries. The catalog or explicit request selects raw weights, and
the domain service classifies ready criteria as full-coverage or conditional. It always creates
the 91-country FCC baseline R0. When a conditional criterion reaches raw weight 0.6, the service
builds the missing-country union, complete-case eligible universe, and R1 using one normalized
vector for every eligible country. Excluded countries receive diagnostics but no R1 score or
rank. Score-boundary top K includes every Kth-score tie.

The repository owns canonical outcomes and scores, the domain owns activation, complete-case
selection, weights, ranks, bounds, and status, the API maps typed results, and the UI renders them.
Responses retain release, method, observation, source, caveat, and experimental metadata.

## Decision records

The binding decisions are recorded in [architecture/decisions](decisions/001-immutable-release-artifacts.md).
Operational details belong in the [worker](../operations/worker.md),
[API](../operations/api.md), and deployment guides rather than here.
