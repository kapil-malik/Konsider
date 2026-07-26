# Implementation history

Historical records summarize completed milestones. Current behavior is documented in
[architecture](../architecture/system-architecture.md), [worker operations](../operations/worker.md),
and [API operations](../operations/api.md).

## Phase 5E deterministic measured probes

- Goal: measure the actual stable-91 suitability of the seven deterministic candidates approved
  after Phase 5C.
- Delivered: exact live captures, source and licence records, 91 explicit country outcomes per
  candidate, aggregate JSON/CSV/Markdown, country-status matrix, raw-artifact inventory, and
  content-addressed offline replay.
- Results: all seven passed the 82-country probe threshold. C30, C29, C48, and C49 reached 91/91;
  C11 reached 88/91; C08 reached 87/91 under its three-field rule; and C53 reached 86/91.
- Recommendations: production candidate for C11, C30, C48, and C49; experimental candidate for C08
  and C29; reserve candidate for C53; no rejection.
- Completed: 2026-07-26. All seven offline replays passed. No active release, production ingestion,
  scoring, API, or UI was modified.

## Phase 5D feasibility-probe framework

- Goal: prove a minimal, generic, deterministic way to test candidate sources without entering
  production ingestion or publishing.
- Delivered: stable-91 country mapping, source-specific adapters, content-addressed raw capture,
  independent presence/freshness/parse/validation states, explicit reason codes, Markdown and
  machine-readable reports, and offline replay.
- Framework proofs: schema-faithful synthetic C30 World Bank JSON at 91/91, and C11 ILOSTAT CSV at
  88/91 with ATG, GRD, and UKR explicitly missing.
- Verification covers mapping, freshness, validation, count reconciliation, reason codes,
  deterministic output, offline replay, and active-release isolation.
- Completed: 2026-07-26. No active release, production ingestion, API, scoring, or UI was modified.
- Limitation: fixture outcomes prove framework behaviour only; they are not evidence of live source
  coverage or licensing suitability.

## Phase 5G-0 and 5G-1: portfolio expansion

- Goal: resolve the final conditional source questions and implement only approved, deterministic
  additions without weakening the stable 91-country contract.
- Delivered: exact-source online/offline probes for four candidates; production ingestion,
  provenance, uncertainty retention, versioned scoring, validation, sensitivity diagnostics, API
  catalog integration, immutable publication, and replay for three additions.
- Major decisions: health spending stays conditional at 90/91; disaster risk stays experimental;
  working hours fails current coverage; citizenship access awaits a stable archive. Political
  stability, rule of law, and established immigrant presence are ready at 91/91. Immigrant presence
  is preference-based, and WGI overlap is measured and disclosed.
- Completed: 2026-07-26 with active release `2026-07-26.3`.
- Remaining limitations: UHC remains stale; infrastructure remains experimental; refresh remains
  manual; raw third-party bytes remain local and ignored.

## Worker-first real-data milestone

- Goal: replace fixture-first product assumptions with audited, reproducible official data.
- Delivered: source registry, immutable raw capture, normalized observations, attempt records,
  provenance, versioned scoring, sensitivity diagnostics, structural/readiness validation,
  publication, and replay for 20 countries and six criteria.
- Major decisions: missing data stays explicit; five ready criteria are required; UHC remains
  non-ready; infrastructure remains experimental; fixtures are never product fallback data.
- Completed: 2026-07-20 with release `2026-07-20.2`.
- Remaining limitations: raw third-party bytes are local/ignored, refresh is manual, and AWS storage
  and scheduling are not implemented.

## Phase 2A: published-release consumer and deterministic engine

- Goal: load one active published release and deterministically rank 20 countries using only ready
  criteria, without FastAPI, React, retrieval, or LLM dependencies.
- Delivered: Draft 2020-12 consumer schemas, versioned catalog, read-only schema/checksum-validating
  repository, canonical country/criterion identifiers, provisional ready-only profile, ranking,
  comparison, country breakdown, deterministic explanations, and golden regression tests.
- Major decisions: the catalog must reconcile exactly with release readiness and scoring versions;
  UHC may be diagnostic but cannot be weighted; equal cost bands remain ties; output is pinned to a
  release and method versions.
- Completed: 2026-07-20, commit `8d0709c`, based on release `2026-07-20.2`.
- Remaining limitations: framework-independent calls only; no HTTP transport or UI.

## Phase 2B: minimal versioned API

- Goal: expose proven Phase 2A operations through a thin FastAPI transport.
- Delivered: typed health, catalog, rankings, country metrics, and comparisons routes under
  `/api/v1`; Pydantic request/response models; stable error envelopes; CORS settings; startup
  snapshot validation; path-independent defaults; OpenAPI and integration tests.
- Major decisions: routes contain no scoring/readiness/provenance rules; one immutable snapshot is
  reused per process; initialization failure produces controlled `503`; pointer changes need restart.
- Completed: 2026-07-21, commit `9ae342d`.
- Remaining limitations: no authentication, persistence, UI, chat, cloud adapters, or deployment.

## Phase 2C backend-readiness hardening

- Goal: make the Phase 2B baseline portable to Linux CI before UI work.
- Delivered: LF-enforced release artifacts, immutable packaging-corrected release `2026-07-21.1`,
  Ubuntu GitHub Actions gates, clean-checkout checksum/API verification, and regression tests proving
  semantic ranking equality with `2026-07-20.2`.
- Major decision: do not rewrite the CRLF-checksummed historical release; publish a new ID.
- Completed: 2026-07-21, commit `0350cdd`.
- Remaining limitations: full raw replay still requires intentionally uncommitted `data/raw` bytes.
