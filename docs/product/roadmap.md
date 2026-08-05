# Product roadmap

Status: Phase 7I cross-feature integration complete; Phase 7J release gate next

Last updated: 2026-08-05

## Current position

The local worker, immutable real-data release pipeline, schema/checksum-validating release consumer,
deterministic recommendation service, five-route FastAPI v2 transport, and responsive React UI are
implemented. Active release `2026-08-04.1` exposes the stable 91-country universe, 388 frozen
urban centres, and fourteen available criteria. Eight are 91/91 global-core criteria; Overall job-market opportunity, School
education quality, and Research and innovation ecosystem are conditional criteria, and UHC remains
diagnostic-only. Infrastructure and the two Wave 2 additions are experimental. Phase 4's ranking
and API contracts preserve missing/stale outcomes without
imputation and provide complete-case robustness diagnostics.

Phase 5A classified all 45 deeply researched locality-related criteria and measured a stable
urban-centre universe. Phase 5G has now onboarded Extreme heat exposure and the narrowed
Projected warm-day frequency (2030) as experimental locality-derived criteria, each with 89/91
country coverage.

Phase 5B defined the clean target for orthogonal coverage, locality scope, applicability, canonical
geography, policy-driven locality aggregation, multiple-source lineage, structured assessments,
and preference presets. Phase 5H finalized that contract as the sole public runtime.

Phase 5C implemented the schema-5 generic worker, canonical geographic validation,
policy and lineage snapshots, immutable release/catalog writer and loader, and deterministic replay.
The same path accepts national/locality and FCC/PCC combinations. Explicit outcomes remain at the
country result level; locality observations and scores are linked evidence. Phase 5G then published
the first production locality criteria through this path.

Phase 5D has implemented policy-driven locality aggregation, independent country affinity,
full-universe common-locality analysis, weighted best-common selection, and typed
coverage/locality/profile assessments against synthetic schema-5 releases. Coverage and locality
advice are invariantly separate. Phase 5E/F exposed these concepts through the typed API and UI,
and Phase 5H removed the temporary dual-contract runtime.

Phase 5I closed the phase with 280 passing backend tests, deterministic active-release replay,
clean OpenAPI/TypeScript regeneration, frontend and browser gates, and a source-only Windows
clean-checkout verification. The final architecture, 45-criterion disposition, active inventory,
limitations, and remote-CI status are in the
[Phase 5 closure report](../history/phase5-closure-report.md).

Phase 6A exposed source and construct blockers. The Phase 6B/6B.1 pivot subsequently approved five
career ecosystem signals as filter-only product concepts, and Phase 6C approved four
source-aligned research-university ecosystem signals. These nine signals are Opportunity Filters,
not weighted criteria or PCCs.

Phase 6D defined the sibling catalog, tri-state evidence, confidence, reason, policy, source,
coverage, assessment and optional release-5.1 contracts. Phase 6E stages five career filters and
455 explicit country states. Phase 6F adds four education filters, 364 education rows, and a
complete 819-row draft candidate. Phase 6G implements the isolated post-ranking strict-AND engine
and additive typed API against `phase6g-api-2026-08-03.1`. Phase 6H implemented the separate
checkbox controls, result/exclusion explanations, details and comparison presentation. Phase 6I
published and atomically activated release `2026-08-04.1`, preserving every prior ordering payload
while binding nine filters and 819 states under release schema 5.1. See the
[Opportunity Filter architecture](../architecture/opportunity-filter-contracts.md) and
[Opportunity Filter engine](opportunity-filter-engine.md), [UI guide](ui.md),
[career evidence guide](../data/career-opportunity-evidence.md) and
[education evidence guide](../data/education-opportunity-evidence.md).

Completed Phase 2A and 2B details live in [implementation history](../history/implementation-history.md).
Historical releases live in [release history](../history/releases/README.md).

## Phase 2C: comparison UI — implemented

Historical dependency: the original five-route API contract, now superseded by `/api/v2`.

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

## Phase 5: locality-aware criteria and structured assessments — complete

Phase 5 added carefully bounded locality evidence without converting Konsider into a city-ranking
product or weakening its country-level comparison contract.

- Classified all 45 researched criteria by locality and profile suitability.
- Froze a reproducible GHSL urban-centre universe independently of criterion values.
- Separated coverage, scope, and applicability in schema 5/catalog 3.
- Added deterministic locality aggregation, common-locality advice, lineage, and replay.
- Onboarded experimental C66 Extreme heat exposure and C67 Projected warm-day frequency (2030).
- Exposed separate coverage, locality, and unevaluated-profile assessments through API v2 and UI.
- Renamed weight profiles to preference presets and removed every transitional public field.
- Preserved historical releases and all Phase 4 complete-case guarantees.

Phase 5A is documented in the
[locality criteria discovery report](../research/phase5a-locality-criteria-discovery.md).
Phase 5B is documented in the
[target architecture and contracts report](../architecture/phase5b-target-contracts.md).
The final public-contract cleanup is documented in the
[Phase 5H migration report](phase5h-contract-migration.md).
The complete outcome is documented in the
[Phase 5 closure report](../history/phase5-closure-report.md).

## Phase 6: career and engineering-education opportunity — complete

Phase 6 tests narrower, profile-neutral destination constructs without estimating an applicant's
job, licensing, visa, or admission probability.

- Phase 6A completed the initial source-gate study. Phase 6B/6B.1 then froze five career constructs,
  exact source routes, confidence/negative-integrity policy, P60 thresholds and gap-fill decisions.
- Phase 6C froze four field-specific research-university ecosystem filters using the source-aligned
  education methodology.
- Phase 6D completed the separate filter-only contracts and optional release-5.1 binding without
  changing ranking, API or UI behavior.
- Phase 6E stages the five career filters with exactly 455 explicit country records and complete
  research reconciliation.
- Phase 6F stages the four education filters with exactly 364 records and validates the complete
  nine-filter, 819-record candidate without changing the active release.
- Phase 6G implements indexed strict-AND evaluation after canonical ranking, additive API v2
  selection/catalog/assessment fields, and deterministic compatibility and golden tests. It does
  not activate the staged candidate.
- Phase 6H implements grouped checkbox controls, Apply/Undo and removable-filter interactions,
  result/exclusion explanations, evidence details, comparison, responsive behavior and
  accessibility over the staged API without activating it.
- Phase 6I published and activated `2026-08-04.1`, verified compatibility, and closed Phase 6.

## Phase 7: Typed Feasibility Checks - complete

Phase 7A defines Typed Feasibility Checks as optional, guest-first assessments of an explicit
applicant, household and exploration-scenario snapshot. TFCs are sibling assessments, not ordering
criteria, PCC/LSC behavior, Opportunity Filters, preference presets or account settings. They never
change affinity. The discovery revisits all 21 Phase 5 `PROFILE_PHASE` candidates and recommends
eight exact-source probes spanning route/rule matches and scenario metrics. See the
[Phase 7A discovery report](../research/phase7a-tfc-discovery.md).

Phase 7B completed the exact-source gate and qualified exactly three first-wave checks without
lowering the Phase 7A floors: highly qualified work routes, dependants attached to supported work
and study routes, and post-study stay/work routes. Each has an explicit 29/91 source boundary (EU
Immigration Portal 25 plus Australia, Canada, the United Kingdom and the United States), with all
other stable destinations explicit as unsupported. See the
[Phase 7B source-feasibility report](../research/phase7b-tfc-source-feasibility.md).

The owner approved those three checks for Phase 7C. Phase 7C now defines separate applicant,
household and scenario contracts, immutable effective-context snapshots, guest-first retention,
typed route outcomes, sibling feasibility assessments and a standalone future release-6 binding.
See the [TFC contracts](../architecture/tfc-contracts.md) and
[Phase 7C report](../history/phase7c-tfc-profile-contracts.md). The active release, API, UI,
ranking, locality and Opportunity Filter behavior remain unchanged.

All three checks use `RULE_ROUTE_MATCH`, so the contract is route-only rather than a speculative
generic multi-result engine. Permanent residence, professional licensing, employment deductions,
reference-city rent and healthcare affordability remain targeted follow-up research.

Until the Phase 7D owner gate and later Phase 7 gates pass:

- keep applicant, household and scenario facts separate from preference presets and immutable
  destination evidence;
- use synthetic profiles only for research;
- retain guest use and browser-tab memory as the default;
- do not add authentication, server-side saved profiles, sync, chat or conversational memory; and
- keep C05 locality research as an independent fast follow with its own source and identity gates.

Phase 7D now implements typed destination support, jurisdiction, route/rule and synthetic metric
formula artifacts; audited source/legal registrations; effective-date and conflict validation;
an explicit support row for every staged TFC-country pair; deterministic release-6 candidate
assembly and replay; and five-category semantic diffs. Its only input is visibly fictional, and the
draft repository cannot publish or activate. See the
[Phase 7D report](../history/phase7d-tfc-release-foundation.md).

Phase 7E now implements request-time context normalization and hashing, input sufficiency,
applicability, effective jurisdiction/rule selection, multiple-route aggregation, synthetic metric
ranges, explicit policy-gated filtering, feasibility summaries and non-persisted scenario
snapshots. Golden tests preserve ranking, PCC/LSC, locality and Opportunity Filter invariants. See
the [Phase 7E report](../history/phase7e-tfc-assessment-engine.md).

Phase 7F now stages the approved three route-only checks with 87 exact official page bindings,
116 named route rules, 273 explicit destination support records, five approved source/legal
registrations and a passed Phase 7B reconciliation. All policies remain assessment-only and
positive/conditional; the draft cannot activate. See the
[first-wave evidence guide](tfc-first-wave-evidence.md) and
[Phase 7F report](../history/phase7f-first-wave-onboarding.md).

Phase 7G now exposes that deliberately selected candidate through additive API v2 contracts. It
adds the TFC catalog/field registry and explicit stateless context on ranking, comparison and
details; returns typed outcomes and sanitized snapshot metadata; and enforces private/no-store
transport. Empty selection remains exactly legacy-compatible. The release-6 candidate remains
draft and non-active, and all three checks reject filtering because their policies are
assessment-only. See the [Phase 7G report](../history/phase7g-stateless-tfc-api.md).

Phase 7H now adds a guided **Your situation** flow over the catalog-driven API. Guests explicitly
choose checks, provide only relevant applicant/household/scenario facts, preserve unknowns, review
assumptions and see route or metric outcomes separately from affinity, locality and Opportunity
evidence. Ranking, details and comparison reuse one effective scenario selection. Tab retention is
the default; versioned 30-day device storage is opt-in, with clear and privacy-reduced
export/validated-import controls. No account, server persistence, analytics, profile URL or UI-side
eligibility rule was added.

Phase 7I now verifies the combined affinity, PCC, locality, Opportunity Filter and TFC experience
end to end. It preserves canonical rank and every pre-TFC assessment, adds bounded explanations for
independent signals, exposes TFC source/effective-date evidence in comparison, and covers desktop
and mobile journeys. The live matrix uses only the staged three-check assessment-only candidate;
licensing, locality-cost and explicit-filter cases remain synthetic engine tests. See the
[cross-feature behavior guide](tfc-cross-feature-behavior.md),
[scenario matrix](phase7i-scenario-matrix.md), [UI test plan](phase7i-ui-test-plan.md) and
[verification report](../history/phase7i-cross-feature-verification.md).

Phase 7J published and activated immutable schema-6.0 overlay `2026-08-05.1`. The production API
now loads the three approved assessment-only checks only through the active pointer, while the
ranking and Opportunity Filter data continue to resolve from checksum-bound base `2026-08-04.1`.
Final replay, compatibility, privacy, browser and rollback verification passed. See the
[Phase 7 closure report](../history/phase7-closure-report.md).

## Recommended Phase 8: TFC maintenance and measured expansion

- Re-verify official route sources on their declared cadence and review semantic changes before
  publishing successor overlays.
- Measure whether users understand conditional results and the 29/91 source boundary without
  collecting raw profile values.
- Gate a second route-check wave, locality depth or occupation mapping on source quality and
  demonstrated user need.
- Keep authentication and server-saved profiles deferred until evidence shows that cross-device
  continuity or data loss is a material problem.

## Future phase: conversational exploration

- Add AI explanations and chat only after deterministic ranking and structured profile tools are
  proven.
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
