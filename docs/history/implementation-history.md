# Implementation history

## Phase 5F: locality-aware UI and API-v2 client

- Goal: present structured coverage, locality, and profile assessments without reproducing server
  business logic in React.
- Delivered: an `/api/v2` generated-client migration; independent assessment summaries;
  locality-aware controls, rankings, country details, comparisons, and source metadata; desktop
  and mobile browser coverage; and compile-time rejection of legacy transport fields.
- Major decisions: locality advice never changes affinity or implies exclusion; coverage alone owns
  coverage-excluded wording; Low locality weights retain quiet provenance; historical C66 naming
  remains visible; production fixtures never fill the active release's locality-data gap.
- Completed: 2026-07-29 against active release `2026-07-28.2`.
- Remaining decisions: API retirement/version policy and production locality-criterion onboarding
  remain deferred to Phase 5G or later.

## Phase 4H: end-to-end verification and closure

- Goal: prove the uncertainty-aware ranking model end to end and close Phase 4.
- Delivered: active-release structural/runtime invariants, complete scenario coverage, release-
  scoped catalog snapshots, clean Windows/Linux backend CI, current architecture/API/UI/worker
  documentation, a closure report, and an indexed historical workspace.
- Major decisions: preserve the stable 91-country catalog separately from query eligibility; keep
  optimistic bounds diagnostic-only; archive prompts and research artifacts under
  `project-history` without moving operational or immutable release data.
- Completed: 2026-07-28 against active release `2026-07-28.2`.
- Remaining limitations: four Wave 2 candidates retain licensing/source/construct gates; city,
  occupation, household, and applicant-specific ranking are not implemented.

Historical records summarize completed milestones. Current behavior is documented in
[architecture](../architecture/system-architecture.md), [worker operations](../operations/worker.md),
and [API operations](../operations/api.md).

## Phase 4A-G: uncertainty-aware ranking, first partial criterion, and UI

- Goal: preserve the stable 91-country universe while allowing valuable criteria with bounded,
  explicit source gaps to participate without imputation or misleading partial scores.
- Delivered: the coverage policy, candidate simulations, schema-4 outcome matrix, conditional
  complete-case ranking engine, robustness statuses and optimistic bounds, comparison-cell
  availability, Phase 4E API contracts, and production onboarding of Overall job-market opportunity.
- UI result: coverage-aware priority controls, status-specific warnings, eligible/stable rank scope,
  expandable exclusion diagnostics, an API-fetched FCC baseline, unranked-country evidence, and
  comparison cells that preserve available data while marking unavailable cells.
- Production result: release `2026-07-28.1` publishes ten criteria and 910 explicit outcomes. The
  eight global-core criteria remain 91/91; job-market opportunity is valid for 88 countries and is
  active only at raw weight 0.6 or above.
- Major decisions: keep the 91-country identity stable; never impute; exclude a country from a
  conditional full score when any active partial criterion is non-ready; retain available
  criterion-by-country comparison cells; include Kth-score ties in robustness analysis; and publish
  schema changes only through a new immutable release.
- Completed through Phase 4G: 2026-07-28. A named Wave 2 shortlist and its evidence gates are retained in
  [Phase 4 Wave 2 candidates](../research/phase4-wave2-pcc-candidates.md).

## Phase 3: criteria expansion and source feasibility

- Goal: screen the full 84-item search space, deeply research the strongest or most strategically
  important candidates, measure exact source feasibility, select a guarded portfolio, and implement
  only production-ready additions.
- Delivered: 84 screening rows; three 15-criterion deep-research batches; a generic feasibility
  framework; ten exact live candidate probes; an approved portfolio decision; three new 91/91
  production criteria; active release `2026-07-27.1`; and a consolidated closure report.
- Major decisions: preserve the complete 91-country production universe; distinguish research
  thresholds from publication readiness; defer city, occupation, household, and legal-profile
  questions to their natural layers; retain uncertainty; prohibit imputation and partial-country
  scoring; and preserve rejected evidence.
- Completed: 2026-07-26. The portfolio has nine published criteria and eight enabled criteria.
- Next: Phase 4 deterministic, citation-ready evidence and explanations.

## Phase 3E deterministic measured probes

- Goal: measure the actual stable-91 suitability of the seven deterministic candidates approved
  after Phase 3C.
- Delivered: exact live captures, source and licence records, 91 explicit country outcomes per
  candidate, aggregate JSON/CSV/Markdown, country-status matrix, raw-artifact inventory, and
  content-addressed offline replay.
- Results: all seven passed the 82-country probe threshold. C30, C29, C48, and C49 reached 91/91;
  C11 reached 88/91; C08 reached 87/91 under its three-field rule; and C53 reached 86/91.
- Recommendations: production candidate for C11, C30, C48, and C49; experimental candidate for C08
  and C29; reserve candidate for C53; no rejection.
- Completed: 2026-07-26. All seven offline replays passed. No active release, production ingestion,
  scoring, API, or UI was modified.

## Phase 3D feasibility-probe framework

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

## Phase 3G-0 and 3G-1: portfolio expansion

- Goal: resolve the final conditional source questions and implement only approved, deterministic
  additions without weakening the stable 91-country contract.
- Delivered: exact-source online/offline probes for four candidates; production ingestion,
  provenance, uncertainty retention, versioned scoring, validation, sensitivity diagnostics, API
  catalog integration, immutable publication, and replay for three additions.
- Major decisions: health spending stays conditional at 90/91; disaster risk stays experimental;
  working hours fails current coverage; citizenship access awaits a stable archive. Political
  stability, rule of law, and established immigrant presence are ready at 91/91. Immigrant presence
  is preference-based, and WGI overlap is measured and disclosed.
- Completed: 2026-07-26 with active release `2026-07-27.1`.
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
