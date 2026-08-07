# System architecture

Status: authoritative architecture as of 2026-08-05

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
CurrentReleaseRepository ----> RecommendationService --> FastAPI /api/v2 ---> React/Vite UI
                                       ^                         |
                                       |                         v
                         release catalog              OpenAPI + JSON responses
```

The active pointer selects schema-6.1 overlay `2026-08-08.2`. The repository validates its six TFC
payloads and checksum-bound schema-5.2 base `2026-08-08.1`, then exposes one joined in-memory
snapshot. Historical schema-3/4 releases remain immutable and require an explicit internal loader.

- The worker downloads ten registered official-source distributions, captures exact raw bytes,
  parses observations, computes versioned canonical scores, validates readiness, and publishes an
  immutable release only when the gate passes.
- `CurrentReleaseRepository` resolves either a schema-5 base or the base referenced by a validated
  active schema-6 TFC overlay. It validates checksums, catalogs, geography, policies, outcomes,
  readiness, scoring versions, provenance and OFC binding before joining data.
- `RecommendationService` owns weight selection, normalization, contribution calculations,
  deterministic ranking, comparison, and country breakdowns.
- FastAPI and Pydantic provide a thin versioned transport. One validated release snapshot is loaded
  during process startup and reused. Requests never fetch sources or recompute canonical scores.
- Local files are the only implemented storage adapter. Legacy fixtures remain isolated tests and
  never fill product-release gaps.
- The responsive React UI derives preference presets, priority controls, ranking columns, sources,
  flags, assessments, and release labels from `/api/v2`. TanStack Query owns API work; local state
  owns guest edits.

The active overlay is `2026-08-08.2`; its base contains 91 countries, 388 frozen urban centres and
fourteen catalogued criteria. Extreme heat exposure and Projected warm-day frequency (2030) are experimental
locality-derived criteria with 89/91 country coverage. Coverage, locality compatibility, and
applicant-profile applicability, and filter-only opportunity remain independent structured
assessments.
Country-universe discovery and complete-case auditing are implemented as a separate safe worker
flow. They use UN migrant-stock/M49 inputs plus the registered criterion sources, write diagnostic
reports, and assert that `active.json` is unchanged. They do not share publication authority.

## Opportunity Filter architecture

The sibling filter-only contract family is bound by the active release-5.1 manifest. Opportunity
Filter definitions contain no ranking fields; country evidence uses a separate tri-state and
`assessments.opportunity` shape. `OpportunityFilterService` validates and indexes the binding at
startup, then applies strict AND filtering after canonical ranking. The API and UI expose the
separate assessment without changing scoring, PCC, locality, or profile behavior.

See [Opportunity Filter contracts](opportunity-filter-contracts.md) and [ADR 010](decisions/010-opportunity-filters-as-filter-only-contracts.md).

## Browser architecture

The React, TypeScript, and Vite browser application calls only `/api/v2`, derives countries,
criteria, preference presets, labels, readiness, experimental flags, caveats, sources, and
structured assessments from the catalog and ranking responses, and keeps editable weights in
browser state. The UI contains no scoring, readiness, locality-selection, or eligibility logic.

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
| TFC support, rules and policy | Active schema-6 overlay | Profile context, API and UI |

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

At startup the API resolves and validates the active pointer. For schema 6 it loads the immutable
TFC overlay and checksum-bound ranking base as one snapshot. Healthy requests reuse it in memory;
there is no candidate-path override. Initialization failures leave the process in controlled
degraded mode and product endpoints return safe `503` envelopes. Changing the pointer requires a
restart.

### Ranking

The stable catalog remains 91 countries. A preference preset or explicit request selects raw weights, and
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
