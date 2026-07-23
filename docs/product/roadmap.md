# Product roadmap

Status: Phase 2C implemented; Phase 2D discovery implemented and publication blocked

Last updated: 2026-07-23

## Current position

The local worker, immutable real-data release pipeline, schema/checksum-validating release consumer,
deterministic recommendation service, five-route FastAPI v1 transport, and responsive React UI are
implemented. Active release `2026-07-21.1` exposes 20 countries and six available criteria; five
are enabled. UHC is non-ready because its latest observation is 2021. Infrastructure is enabled but
experimental.
Phase 2D now has a reproducible country universe and online/offline coverage audit. The initial 150
candidates yield 79 complete countries; all 195 eligible countries yield 91. The required 100-country
release, API/UI scale work, and activation are blocked pending a valid same-construct homicide data
path or an explicitly approved product-definition decision.

Completed Phase 2A and 2B details live in [implementation history](../history/implementation-history.md).
Historical releases live in [release history](../history/releases/README.md).

## Phase 2C: comparison UI — implemented

Dependency: stable `/api/v1` catalog, ranking, comparison, country-metric, and health contracts.

Deliver a small React/TypeScript/Vite interface that:

- derives controls, countries, criteria, profiles, labels, caveats, readiness, experimental flags,
  and source metadata from the API;
- provides five editable criterion weights and a ranked 20-country table;
- shows country metric details, observations, reference periods, source links, and caveats;
- supports 2-4 country comparisons in the UI while retaining the API's 2-10 contract;
- marks infrastructure experimental and never enables UHC as a weight;
- keeps weights in browser state;
- handles loading, empty, API-error, and unavailable-release states; and
- has component and limited end-to-end coverage, accessible controls, and responsive layouts.

Delivered exit criteria:

1. UI contains no scoring or readiness business rules.
2. Catalog changes drive rendering without hard-coded business labels.
3. Ranking updates reconcile with API results and preserve provenance.
4. UHC and infrastructure states are represented accurately.
5. Tests cover initial catalog load, weight edits, ranking refresh, details, comparisons, and errors.

See the [implemented UI guide](ui.md) and [React/Vite decision](../architecture/decisions/004-react-vite-ui.md).

## Phase 2D: country coverage expansion — discovery implemented, publication blocked

- Implemented official UN migrant-stock candidate ranking, UN M49/World Bank reconciliation,
  explicit entity exclusions, online capture, offline replay, and detailed complete-case reports.
- Retained all current release countries and proved candidate ordering/replay determinism.
- Did not publish because the complete intersection is 79/150 and 91/195, below 100.
- Phase 2D.4 evaluated Direct UNODC, UNSD, Eurostat, and OECD. The primary channels each raise the
  complete intersection only to 95; fallbacks add none, and UN redistribution terms remain unclear.
- Next decision: do not weaken freshness, change the homicide construct, or redefine infrastructure
  without explicit product approval.

See the [Phase 2D coverage report](../data/country-coverage-phase-2d.md) and
[Phase 2D.4 source study](../data/homicide-source-feasibility-phase-2d4.md).

## Phase 2E: deterministic evidence and explanations

- Add structured source/observation lookup and citation-ready provenance.
- Generate deterministic strengths, trade-offs, and comparison explanations from contributions.
- Add metadata and simple lexical lookup only if measured product needs require it.
- Do not introduce a vector database without evidence volume and retrieval-quality measurements.

## Phase 2F: conversational exploration

- Add LLM assistance only after deterministic ranking and explanations are proven.
- Require numerical and factual claims to come from typed deterministic tools.
- Provide non-LLM fallbacks and explicit rate, token, session, and tool limits.
- Add agents, LangGraph, or MCP only for demonstrated workflows.

## Deliberately deferred platform work

AWS infrastructure, scheduled refreshes, S3 adapters, authentication, saved profiles, persistent
sessions, chat, LLMs, retrieval, vector/relational stores, and multi-agent orchestration remain
unimplemented. The [AWS document](../operations/deployment-aws.md) is a design only.

## Delivery rules

- Published releases and raw artifacts are immutable; corrections use new IDs.
- Missing, stale, incomparable, and rejected data stays explicit; fixtures never fill product gaps.
- Non-ready criteria are excluded at the repository/service boundary, not merely hidden in the UI.
- The website talks only to the API and never implements scoring or readiness.
- Every ranking identifies its release and scoring versions.
