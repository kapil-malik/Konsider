# Konsider roadmap

Status: Phase 2A complete; Phase 2B minimal API is next

Last updated: 2026-07-20

This roadmap supersedes the earlier fixture-first sequence. The project now has a published real-data
release, but the legacy fixture repository and profiles are not product inputs and must never fill
gaps in a real release.

## Current position

Published release `2026-07-20.2` is structurally valid and contains six criteria for the fixed
20-country experiment set. Five criteria pass the configured criterion-level product-readiness
checks:

- population-weighted PM2.5 exposure;
- intentional homicide rate;
- broad household-consumption relative-cost bands;
- women's legal and economic equality; and
- an experimental infrastructure-readiness composite.

UHC service coverage has 20-country coverage but remains non-ready because its latest observation is
from 2021 and exceeds the three-year freshness threshold. Passing the aggregate five-of-six gate
does not make the UHC criterion ready and must not cause consumers to include it by default.

The existing framework-free ranking functions still consume the legacy ten-country fixture shape.
They do not yet consume release `2026-07-20.2`; the legacy profiles also reference criteria that are
absent from the published release. Phase 2A closes this integration gap before FastAPI or React work.

## Dataset readiness policy

A criterion is ready only when it has:

- audited usage and redistribution terms;
- complete expected attempts and 20-country coverage;
- acceptable freshness, type, unit and quality flags;
- exact record and component provenance;
- compatible versioned schemas;
- valid artifact, file and release checksums;
- versioned parsing and scoring methods; and
- reproducible replay from retained raw artifacts.

Consumers must read `criterion_readiness` from the published release and exclude non-ready criteria
by default. Structural validity, criterion readiness and aggregate release readiness are separate
decisions.

## Completed: worker-first data milestone

1. Audited the fixed 20-country source universe, licences, methodology, coverage and freshness.
2. Implemented immutable raw capture, source registrations, exact record provenance, normalized
   observations, attempts, validation, publication and replay.
3. Replaced direct WHO PM2.5 and UHC capture with World Bank-distributed CC BY 4.0 indicators.
4. Retained UNODC-lineage homicide through WDI and narrowed ICP output to broad relative-cost bands.
5. Replaced WPS with the WBL 2026 Legal Framework economy index and renamed the criterion.
6. Added an experimental equal-weight infrastructure composite covering digital access and
   trade/transport infrastructure quality.
7. Compared threshold, percentile and winsorized min-max scoring and selected fixed, versioned
   transformations.
8. Published immutable active release `2026-07-20.2` after five criteria passed.

## Completed: Phase 2A — Published-release consumer and deterministic engine foundation

Goal: load one active published release and deterministically rank the 20 countries using only its
ready criteria, without FastAPI, React, retrieval or LLM dependencies.

Implemented on 2026-07-20. The active release is schema-validated and checksum-verified, its
separate versioned consumer catalog exposes all six criteria, normal mode serves exactly the 100
ready score pairs, and framework-independent services provide deterministic catalog, ranking,
comparison, and country-breakdown results. UHC remains diagnostic/read-only and cannot be weighted.
See [phase-2a-implementation.md](phase-2a-implementation.md).

### 2A.1 Machine-readable release contracts

- Add JSON Schemas for the active pointer, manifest, validation report, source registration,
  observation, score and consumer catalog.
- Version every schema and reject incompatible major versions.
- Add positive and negative schema tests using release `2026-07-20.2` and deliberately malformed
  records.
- Reconcile documentation terminology with the actual release filenames, especially
  `scores.jsonl` versus older references to `metrics.jsonl`.

### 2A.2 Versioned consumer catalog

- Add a release-consumable catalog containing country ISO-3 code, display name and region.
- Add criterion metadata: ID, display name, description, direction, raw unit, caveats, readiness,
  experimental status, default inclusion and scoring-method version.
- Keep the catalog server-owned; future UI code must not embed business labels or readiness rules.
- Represent UHC in the catalog as available but disabled/non-ready.
- Label infrastructure as experimental and describe its limited digital plus trade/transport scope.

### 2A.3 Published release repository

- Implement a read-only repository that resolves `data/releases/active.json` and loads a compatible
  published release.
- Verify release status, schema version, declared counts and payload checksums before serving data.
- Load and join `scores.jsonl`, `observations.jsonl`, `sources.json` and `validation.json` through
  country, criterion and observation identifiers.
- Exclude criteria whose `criterion_readiness` is false unless an explicitly named diagnostic mode
  is used.
- Fail loudly on missing records, duplicate country/criterion pairs, broken observation lineage,
  unsupported schemas or checksum mismatches.
- Return dataset, source, parser, observation-method and scoring-method versions with consumer data.

### 2A.4 Domain-model and profile alignment

- Adapt or replace legacy fixture-oriented domain models so canonical ISO-3 country and criterion
  identifiers flow from the published release.
- Preserve the framework-free weight normalization, contribution calculation and deterministic
  ordering where their semantics remain valid.
- Replace the old ten-criterion default profiles with explicitly provisional profiles containing
  only the five ready criteria.
- Do not silently map `female_safety` to legal equality, `crime_rate` to homicide, or generic
  `cost_of_living` to the national price-level band; use the new precise criterion identities.
- Keep legacy fixtures available only for legacy tests, clearly separated from real-release tests.

### 2A.5 Ranking and comparison services

- Implement framework-free services for catalog retrieval, weighted ranking, country comparison and
  per-country breakdown.
- Normalize non-negative user weights and reject unknown or non-ready criterion IDs.
- Pin every calculation to one release ID and return normalized weights, totals, contributions,
  strengths, trade-offs, raw observations, reference years, sources and caveats.
- Treat equal relative-cost bands as genuine ties at the criterion level.
- Provide deterministic template explanations; do not add an LLM in this phase.

### 2A.6 Golden acceptance tests

- Assert that the active release loads 20 countries and six available criteria, with five enabled.
- Assert that UHC is excluded by default and cannot be weighted in normal product mode.
- Assert that every enabled score resolves to its observation and source provenance.
- Assert that repeated ranking requests are byte-for-byte deterministic for the same release and
  normalized weights.
- Assert that contributions sum to totals and rankings have deterministic tie-breaking.
- Assert that all responses expose release and scoring versions.
- Add regression fixtures for checksum failure, incompatible schema, missing lineage, duplicate
  score, non-ready criterion and unknown weight.

### 2A.7 Worker dependability fixes carried in parallel

- Derive freshness evaluation from the refresh timestamp instead of a hard-coded 2026 default,
  while retaining an injectable clock for tests.
- Prevent World Bank query date ranges from silently ending at 2026.
- Require an explicit source-registration/version update when upstream datasets or annual WBL
  workbook URLs change.
- Review and document acceptance of the ten material-change warnings in release `2026-07-20.2`
  before exposing historical trends.
- Document how retained raw artifacts will be made available to CI or private object storage for
  portable replay; this does not block read-only consumption of committed normalized releases.

### Phase 2A exit criteria

Phase 2A is complete only when one framework-free call can:

1. Resolve the active published release.
2. Verify its consumer contract.
3. Exclude UHC automatically.
4. Accept five criterion weights.
5. Return deterministic rankings for all 20 countries.
6. Return contribution, provenance, caveat and version details.
7. Pass the full unit, integration, schema and golden-release test suite.

## Phase 2B â€” Minimal versioned API

Goal: expose the proven Phase 2A services through a thin FastAPI transport layer.

- Add `GET /api/v1/catalog`.
- Add `POST /api/v1/rankings`.
- Add `GET /api/v1/countries/{country_code}/metrics`.
- Define separate Pydantic transport models without duplicating domain logic.
- Return release ID, scoring versions, normalized weights, caveats and provenance references.
- Add API contract tests for success, validation errors, unavailable criteria and incompatible
  releases.
- Load one immutable active release at startup or first request; never call external data sources
  during a user request.

Phase 2B excludes authentication, saved profiles, chat, agents, MCP and cloud deployment.

## Phase 2C â€” Comparison UI

Goal: provide a small React interface over the stable Phase 2B contracts.

- Build controls from `/api/v1/catalog`; do not hard-code countries, criteria or default profiles.
- Provide five criterion-weight controls and a ranked 20-country table.
- Show country breakdowns, raw values, reference years, source links and caveats.
- Mark infrastructure as experimental and do not expose UHC as an enabled weight.
- Keep user-edited weights in browser state initially.
- Add loading, empty, unavailable-release and API-error states.
- Add component and end-to-end tests for catalog-driven rendering and ranking updates.

## Phase 2D â€” Deterministic evidence and explanations

Goal: explain rankings without relying on generated prose or semantic retrieval.

- Add structured source and observation lookup.
- Generate deterministic strengths, trade-offs and comparison explanations from contributions.
- Expose citation-ready source metadata and provenance references.
- Add metadata and simple lexical lookup only if needed.
- Introduce an evidence artifact or index only after its consumer requirements are defined.
- Do not add a vector database unless measured evidence volume and search quality justify it.

## Phase 2E â€” Conversational layer

Goal: add LLM-assisted exploration only after deterministic ranking and explanations are proven.

- Define typed tools for profile inspection, weight proposals, ranking, comparison and evidence
  lookup.
- Require all numerical and factual claims to come from deterministic tool results.
- Use typed profile and ranking events; the UI must never parse state changes from prose.
- Provide a non-LLM template fallback.
- Add session, rate, token and tool-call limits before public access.
- Add agents, LangGraph or MCP only where a demonstrated workflow requires them.

## Deferred platform work

- AWS S3 adapters for releases and private raw artifacts.
- Scheduled worker execution and operational alerting.
- Authentication and durable profiles.
- Conversation persistence and usage accounting.
- Vector or relational stores.
- Multi-agent orchestration.

These remain deferred until the local Phase 2Aâ€“2C path is stable and measured requirements justify
the additional infrastructure.

## Delivery rules

- Published releases and raw artifacts are immutable; corrections create new release IDs.
- Missing, stale, incomparable and rejected data remains explicit; fixtures never fill real gaps.
- Non-ready criteria are excluded by default at the repository/service boundary, not merely hidden
  by the UI.
- The website never implements scoring or readiness rules.
- Every ranking identifies its dataset and scoring versions.
- The worker writes releases; the engine reads published releases; the website talks only to the API.
- No phase introduces retrieval, LLMs, cloud infrastructure or mutable databases before its stated
  dependency is proven.
