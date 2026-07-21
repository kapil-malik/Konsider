# Product roadmap

Status: Phase 2B complete and backend hardened; Phase 2C comparison UI is next

Last updated: 2026-07-21

## Current position

The local worker, immutable real-data release pipeline, schema/checksum-validating release consumer,
deterministic recommendation service, and five-route FastAPI v1 transport are implemented. Active
release `2026-07-21.1` exposes 20 countries and six available criteria; five are enabled. UHC is
non-ready because its latest observation is 2021. Infrastructure is enabled but experimental.

Completed Phase 2A and 2B details live in [implementation history](../history/implementation-history.md).
Historical releases live in [release history](../history/releases/README.md).

## Phase 2C: comparison UI

Dependency: stable `/api/v1` catalog, ranking, comparison, country-metric, and health contracts.

Deliver a small React/TypeScript/Vite interface that:

- derives controls, countries, criteria, profiles, labels, caveats, readiness, experimental flags,
  and source metadata from the API;
- provides five editable criterion weights and a ranked 20-country table;
- shows country metric details, observations, reference periods, source links, and caveats;
- supports 2-10 country comparisons;
- marks infrastructure experimental and never enables UHC as a weight;
- keeps weights in browser state;
- handles loading, empty, API-error, and unavailable-release states; and
- has component and limited end-to-end coverage, accessible controls, and responsive layouts.

Exit criteria:

1. UI contains no scoring or readiness business rules.
2. Catalog changes drive rendering without hard-coded business labels.
3. Ranking updates reconcile with API results and preserve provenance.
4. UHC and infrastructure states are represented accurately.
5. Tests cover initial catalog load, weight edits, ranking refresh, details, comparisons, and errors.

See the [UI plan](ui.md) and [React/Vite decision](../architecture/decisions/004-react-vite-ui.md).

## Phase 2D: deterministic evidence and explanations

- Add structured source/observation lookup and citation-ready provenance.
- Generate deterministic strengths, trade-offs, and comparison explanations from contributions.
- Add metadata and simple lexical lookup only if measured product needs require it.
- Do not introduce a vector database without evidence volume and retrieval-quality measurements.

## Phase 2E: conversational exploration

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
