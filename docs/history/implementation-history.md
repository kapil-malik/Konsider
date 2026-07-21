# Implementation history

Historical records summarize completed milestones. Current behavior is documented in
[architecture](../architecture/system-architecture.md), [worker operations](../operations/worker.md),
and [API operations](../operations/api.md).

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
