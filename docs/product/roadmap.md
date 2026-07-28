# Product roadmap

Status: Phase 5B contract design complete

Last updated: 2026-07-28

## Current position

The local worker, immutable real-data release pipeline, schema/checksum-validating release consumer,
deterministic recommendation service, five-route FastAPI v1 transport, and responsive React UI are
implemented. Active release `2026-07-28.2` exposes the stable 91-country universe and twelve
available criteria. Eight are 91/91 global-core criteria; Overall job-market opportunity, School
education quality, and Research and innovation ecosystem are conditional criteria, and UHC remains
diagnostic-only. Infrastructure and the two Wave 2 additions are experimental. Phase 4's ranking
and API contracts preserve missing/stale outcomes without
imputation and provide complete-case robustness diagnostics.

Phase 5A has classified all 45 deeply researched locality-related criteria, measured a stable
urban-centre universe, and approved one deliberately narrow first-wave candidate: Extreme heat
exposure. No Phase 5 runtime, API, UI, release, catalog, or scoring changes have been made.

Phase 5B has defined the clean major-version target for orthogonal coverage, locality scope,
applicability, canonical geography, policy-driven locality aggregation, multiple-source lineage,
structured assessments, and preference presets. These schemas and fixtures remain inactive design
contracts; the active release and API are unchanged.

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

## Phase 3: criteria expansion and source feasibility — complete

- Completed exact-source, non-publishing probes for health spending, disaster-risk resilience,
  working hours, and citizenship access.
- Added political stability, rule of law, and established immigrant presence with 91/91 coverage,
  versioned scoring, provenance, validation, diagnostics, and replay.
- Published immutable release `2026-07-27.1`; eight criteria are now enabled.
- Retained WGI uncertainty, disclosed governance overlap, and kept immigrant presence
  preference-based rather than treating it as universal quality.
- Closed the 84-item research funnel with all screening and rejection evidence preserved.

See the [Phase 3 closure report](../research/phase3-closure-report.md),
[Phase 3G-0 probe report](../research/phase3g0-final-probes.md), and
[active release report](../history/releases/2026-07-27.1.md).

## Phase 4: uncertainty-aware partial coverage — complete

- Added release/catalog schema 4/2 with one explicit outcome per country and criterion.
- Added complete-case conditional ranking, tie-inclusive robustness analysis, optimistic upper
  bounds, and comparison cells that retain available data while marking unavailable data.
- Onboarded Overall job-market opportunity from ILOSTAT at 88/91 without imputation.
- Published immutable release `2026-07-28.1` after validation and offline replay.
- Onboarded experimental School education quality at 88/91 using HCI+ learning-adjusted years and
  Research and innovation ecosystem at 85/91 using WIPO's Innovation outputs sub-index.
- Published immutable additive release `2026-07-28.2` after deterministic replay and coverage
  validation.
- Added coverage-aware controls, status-specific warnings, exclusion diagnostics, an API-fetched
  full-coverage baseline, and comparison cells that retain available evidence without partial
  aggregate scores.
- Reassessed the Wave 2 shortlist and retained explicit source, licence, and construct gates for
  Financial protection from health costs, Social-protection system reach, Food-safety system
  capacity, and Freedom of expression and religion.

- Closed Phase 4H with end-to-end scenario/invariant tests, release-scoped catalog snapshots,
  Windows/Linux clean-checkout CI, offline replay, documentation, and the
  [closure report](../history/phase4-closure-report.md).

Held Wave 2 criteria remain future onboarding candidates, not unfinished Phase 4 behavior. They
must clear commercial reuse, construct, coverage, scoring, and replay requirements independently.

## Phase 5: locality-aware criteria and structured assessments

Phase 5 will add carefully bounded locality evidence without converting Konsider into a city-ranking
product or weakening its country-level comparison contract.

- Keep criterion definitions separate from source implementations and locality aggregation policy.
- Use a frozen, reproducible GHSL urban-centre universe selected independently of criterion values.
- Start with at most three criteria; Phase 5A currently approves only Extreme heat exposure.
- Keep sparse applicant/household-specific questions in a later structured-profile phase.
- Require every candidate to clear construct, licensing, coverage, aggregation, validation, and
  replay gates before production onboarding.
- Preserve missingness and uncertainty; never fill locality gaps with fixtures or silent proxies.

Phase 5A is documented in the
[locality criteria discovery report](../research/phase5a-locality-criteria-discovery.md).
Phase 5B is documented in the
[target architecture and contracts report](../architecture/phase5b-target-contracts.md).

## Future phase: conversational exploration

- Add AI explanations and chat only after deterministic ranking and explanations are proven.
- Require numerical and factual claims to come from typed deterministic tools.
- Provide non-LLM fallbacks and explicit rate, token, session, and tool limits.
- Add agents, LangGraph, or MCP only for demonstrated workflows.

## Deliberately deferred platform work

AWS infrastructure, scheduled refreshes, S3 adapters, authentication, saved applicant/household
profiles, persistent sessions, chat, LLMs, retrieval, vector/relational stores, and multi-agent
orchestration remain unimplemented. The [AWS document](../operations/deployment-aws.md) is a design
only.

## Delivery rules

- Published releases and raw artifacts are immutable; corrections use new IDs.
- Missing, stale, incomparable, and rejected data stays explicit; fixtures never fill product gaps.
- Non-ready criteria are excluded at the repository/service boundary, not merely hidden in the UI.
- The website talks only to the API and never implements scoring or readiness.
- Every ranking identifies its release and scoring versions.
