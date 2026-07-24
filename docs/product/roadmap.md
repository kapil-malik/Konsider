# Product roadmap

Status: Phase 2C and Phase 2D complete

Last updated: 2026-07-24

## Current position

The local worker, immutable real-data release pipeline, schema/checksum-validating release consumer,
deterministic recommendation service, five-route FastAPI v1 transport, and responsive React UI are
implemented. Active release `2026-07-24.1` exposes the stable 91-country universe and six available
criteria; five are enabled. UHC is non-ready because its latest observation is 2021. Infrastructure
is enabled but experimental. Phase 2D is closed: the universe is the audited complete-case
intersection under the approved WDI-only homicide source policy, and the UI supports search, region
filters, and the long list.

Completed Phase 2A and 2B details live in [implementation history](../history/implementation-history.md).
Historical releases live in [release history](../history/releases/README.md).

## Phase 2C: comparison UI — implemented

Dependency: stable `/api/v1` catalog, ranking, comparison, country-metric, and health contracts.

Deliver a small React/TypeScript/Vite interface that:

- derives controls, countries, criteria, profiles, labels, caveats, readiness, experimental flags,
  and source metadata from the API;
- provides five editable criterion weights and a ranked, searchable country table;
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

## Phase 2D: stable country coverage — complete

- Implemented official UN migrant-stock candidate ranking, UN M49/World Bank reconciliation,
  explicit entity exclusions, online capture, offline replay, and detailed complete-case reports.
- Retained all current release countries and proved candidate ordering/replay determinism.
- Replaced the arbitrary 100-country target with the supported-universe rule: Konsider supports the
  countries for which complete and sufficiently fresh data is available across every enabled
  ranking criterion under the approved source and licensing policy.
- Phase 2D.4 proved that Direct UNODC and UNSD could technically add Bangladesh, Belarus, Kuwait,
  and Saudi Arabia, but neither channel states sufficiently clear production reuse rights.
- Selected World Bank WDI as the only production homicide channel and published the 91-country
  complete-case intersection without weakening freshness, imputing values, or partially scoring.
- Removed the Direct UNODC, UNSD, Eurostat, and OECD runtime study paths while preserving their
  committed reports and rejection rationale.
- Published immutable release `2026-07-24.1`, retained the prior 20-country release, verified replay,
  and added country search, region filters, visible/total counts, and mobile long-list coverage.

See the [Phase 2D coverage report](../data/country-coverage-phase-2d.md) and
[Phase 2D.4 source study](../data/homicide-source-feasibility-phase-2d4.md).

## Phase 2E: deterministic evidence and explanations

- Prioritize additional criteria, fresher source editions, and stronger evidence quality while
  preserving complete-case publication.
- Add structured source/observation lookup and citation-ready provenance.
- Generate deterministic strengths, trade-offs, and comparison explanations from contributions.
- Add metadata and simple lexical lookup only if measured product needs require it.
- Do not introduce a vector database without evidence volume and retrieval-quality measurements.

## Phase 2F: conversational exploration

- Add AI explanations and chat only after deterministic ranking and explanations are proven.
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
