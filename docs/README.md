# Konsider documentation

This is the authoritative documentation index for the current repository. Code, tests, machine-
readable schemas, and published release manifests take precedence if prose ever disagrees.

## Start here

- [System architecture](architecture/system-architecture.md) - implemented boundaries, selected
  next steps, and deferred options.
- [Local setup](operations/local-setup.md) - install and verify a clean checkout.
- [CI preflight](operations/ci-preflight.md) - reproduce all Actions gates locally and install the
  clean-checkout pre-push hook.
- [Worker operations](operations/worker.md) - refresh, publish, replay, inspect, and roll back data.
- [Display-metadata-only releases](operations/display-metadata-release.md) - edit the centralized
  catalog and safely prepare, publish, activate, or roll back an offline display-only release pair.
- [API operations and reference](operations/api.md) - configure, start, and use the additive v2 API.
- [Product roadmap](product/roadmap.md) - current position and forward plan.
- [Phase 4A uncertainty-aware ranking policy](product/uncertainty-aware-ranking.md) - approved
  product and mathematical contract.
- [Phase 4B PCC selection](research/phase4b-pcc-selection.md) - approved initial, second-wave,
  reserve, and deferred dispositions with deterministic simulations.
- [Phase 4 Wave 2 PCC shortlist](research/phase4-wave2-pcc-candidates.md) - named strong
  conditional-coverage candidates, required gates, and explicit watchlist exclusions.
- [Phase 4 closure report](history/phase4-closure-report.md) - end-to-end scenarios, invariants,
  quality gates, remaining risks, and next phase.
- [Phase 5 closure report](history/phase5-closure-report.md) - final locality architecture,
  criterion dispositions, active inventory, verification, limitations, and next phase.
- [Phase 5I verification evidence](../data/reports/phase5i-2026-07-29/report.md) - working-tree and
  clean-checkout backend, frontend, browser, replay, and CI-status evidence.
- [Phase 4H verification evidence](../data/reports/phase4h-2026-07-28/report.md) - local gate
  results and clean-checkout CI status.
- [Phase 5A locality criteria discovery](research/phase5a-locality-criteria-discovery.md) - the
  45-criterion disposition, measured locality universe, source gates, and first-wave decision.
- [Phase 5B target architecture and contracts](architecture/phase5b-target-contracts.md) -
  orthogonal criterion metadata, canonical geography, derived lineage, structured assessments,
  target versions, fixtures, and migration plan.
- [Opportunity Filter contracts](architecture/opportunity-filter-contracts.md) - filter-only
  product role, tri-state evidence, release-5.1 binding, fixtures, validation and staged rollout.
- [Typed Feasibility Check contracts](architecture/tfc-contracts.md) - Phase 7 route-only product
  role, typed outcomes, assessment placement, release-6 target binding and compatibility boundary.
- [Applicant, household and scenario contracts](architecture/profile-scenario-contracts.md) -
  explicit profile layers, unknowns, provenance and immutable effective-context snapshots.
- [Profile privacy and retention](product/profile-privacy-retention.md) - guest-first stateless
  evaluation, browser consent, redaction, export and deletion policy.
- [Phase 7C implementation report](history/phase7c-tfc-profile-contracts.md) - chosen contracts,
  exact enums, fixtures, compatibility and owner gates before Phase 7D.
- [TFC release foundation](architecture/tfc-release-foundation.md) - typed destination rules,
  complete support matrices, deterministic release-6 candidates and semantic diffs.
- [TFC source and rule workflow](operations/tfc-source-workflow.md) - capture, normalization,
  legal review, effective dates, replay and research-to-production promotion.
- [Phase 7D implementation report](history/phase7d-tfc-release-foundation.md) - synthetic artifact
  inventory, compatibility, deterministic replay and Phase 7E boundary.
- [TFC assessment engine](product/tfc-assessment-engine.md) - normalization, sufficiency, typed
  route/metric evaluation, explicit filtering, invariants and scenario snapshots.
- [Phase 7E performance](product/tfc-assessment-performance.md) - reproducible 91-country,
  three-route-plus-metric benchmark.
- [Phase 7E implementation report](history/phase7e-tfc-assessment-engine.md) - evaluation order,
  golden scenarios, invariance, performance and Phase 7F boundary.
- [First-wave TFC evidence](product/tfc-first-wave-evidence.md) - exact three-check inventory,
  profile and destination boundaries, official source routes, policy, limitations and replay.
- [Phase 7F implementation report](history/phase7f-first-wave-onboarding.md) - staged artifacts,
  reconciliation, source decisions, verification and the Phase 7G gate.
- [Phase 7G implementation report](history/phase7g-stateless-tfc-api.md) - additive v2 request and
  response contracts, field registry, privacy controls, compatibility and the Phase 7H boundary.
- [Phase 7H UI guide](product/ui.md#phase-7h-guest-situation-and-feasibility-experience) - guided
  guest context, explicit TFC selection, result separation and browser state ownership.
- [Phase 7H UI test plan](product/phase7h-guest-profile-ui-test-plan.md) - interaction, privacy,
  responsive, accessibility and API-boundary verification.
- [Phase 7H implementation report](history/phase7h-guest-profile-ui.md) - delivered experience,
  retention behavior, safeguards and Phase 7I boundary.
- [TFC cross-feature behavior](product/tfc-cross-feature-behavior.md) - Phase 7I signal ordering,
  orthogonality, comparison behavior and live-versus-synthetic boundary.
- [Phase 7I scenario matrix](product/phase7i-scenario-matrix.md) - fictional profiles, combined
  feature cases and their machine-readable golden fixture.
- [Phase 7I UI test plan](product/phase7i-ui-test-plan.md) - combined desktop, mobile,
  accessibility and wording coverage.
- [Phase 7I verification report](history/phase7i-cross-feature-verification.md) - invariance,
  regression, replay, generated-contract and clean-checkout evidence.
- [Phase 6D Opportunity Filter contract report](history/phase6d-opportunity-filter-contracts.md) -
  architecture decision, exact enums, compatibility evidence, changed paths and owner gates.
- [Career Opportunity Filter evidence](data/career-opportunity-evidence.md) - Phase 6E constructs,
  source routes, frozen thresholds, missingness, refresh and deterministic replay.
- [Phase 6E implementation report](history/phase6e-career-opportunity-evidence.md) - staged artifact
  IDs, exact state counts, reconciliation, verification and Phase 6F owner gates.
- [Education Opportunity Filter evidence](data/education-opportunity-evidence.md) - Phase 6F exact
  CWTS fields, ROR identities, frozen routes, coverage, replay, refresh and limitations.
- [Phase 6F implementation report](history/phase6f-education-opportunity-evidence.md) - complete
  nine-filter candidate, education state counts, reconciliation, verification and Phase 6G gates.
- [Opportunity Filter engine](product/opportunity-filter-engine.md) - Phase 6G post-ranking strict
  AND evaluation, isolation guarantees, compatibility and API behavior.
- [Phase 6G implementation report](history/phase6g-opportunity-filter-api.md) - staged API candidate,
  exact runtime contract, verification and Phase 6H/6I gates.
- [Opportunity Filter UI guide](product/ui.md#phase-6h-opportunity-filter-experience) - Phase 6H
  controls, result/exclusion explanations, details, comparison and accessibility behavior.
- [Phase 6H UI test plan](product/phase6h-opportunity-filter-ui-test-plan.md) - interaction,
  contract, language, responsive and compatibility verification matrix.
- [Phase 6H implementation report](history/phase6h-opportunity-filter-ui.md) - delivered components,
  wording safeguards, staged verification and Phase 6I gates.
- [Phase 6 closure report](history/phase6-closure-report.md) - owner decisions, immutable release,
  activation, invariance, verification, risks and next-phase context.
- [Release 2026-08-04.1](history/releases/2026-08-04.1.md) - final release contents, checksums,
  compatibility and rollback boundary.
- [Terminology glossary](product/terminology-glossary.md) - authoritative meanings for ordering
  criteria, FCC/PCC/LSC, Opportunity Filters, states, confidence, base rank and filtered rank.
- [Phase 4C coverage contract](data/phase4c-coverage-contract.md) - schema-4 release, catalog,
  validation, fixture, and compatibility contract.
- [Phase 4D ranking engine](product/phase4d-ranking-engine.md) - typed complete-case ranking,
  tie-inclusive robustness analysis, statuses, and golden scenarios.
- [Phase 4E API contract](operations/phase4e-api-contract.md) - uncertainty-aware catalog,
  ranking, comparison matrix, OpenAPI, and compatibility behavior.
- [Phase 3D feasibility probes](research/phase3d-feasibility-probes.md) - deterministic,
  non-publishing source feasibility checks and offline replay.
- [Phase 3E deterministic probes](research/phase3e-deterministic-probes.md) - live measured
  results for seven approved candidates, aggregate recommendations, and replay evidence.
- [Phase 3F portfolio decision](research/konsider_phase3f_portfolio_decision.md) - approved
  portfolio, guardrails, fallback hierarchy, and Phase 3G implementation order.
- [Phase 3G-0 final probes](research/phase3g0-final-probes.md) - exact-source coverage,
  freshness, replay evidence, and final dispositions for four unresolved candidates.
- [Phase 3 closure report](research/phase3-closure-report.md) - the complete 84-item funnel,
  final dispositions, production outcome, guardrails, limitations, and refresh recommendations.
- [Phase 2C UI](product/ui.md) - implemented product behavior and technical boundaries.
- [Phase 2D country coverage audit](data/country-coverage-phase-2d.md) - reproducible universe,
  complete-case results, final 91-country universe, and closure decision.
- [Phase 2D.4 homicide source feasibility](data/homicide-source-feasibility-phase-2d4.md) -
  authoritative-source equivalence, coverage, licensing, and replay findings.

## Architecture decisions

- [ADR 001: Immutable release artifacts](architecture/decisions/001-immutable-release-artifacts.md)
- [ADR 002: Local files and S3](architecture/decisions/002-local-files-and-s3.md)
- [ADR 003: FastAPI API engine](architecture/decisions/003-fastapi-api-engine.md)
- [ADR 004: React and Vite UI](architecture/decisions/004-react-vite-ui.md)
- [ADR 005: Orthogonal criterion and geography](architecture/decisions/005-orthogonal-criterion-geography.md)
- [ADR 006: Canonical geography and derived lineage](architecture/decisions/006-canonical-geography-and-derived-lineage.md)
- [ADR 007: Structured assessments and preference presets](architecture/decisions/007-structured-assessments-and-preference-presets.md)
- [ADR 008: Schema-5 orchestration and country outcomes](architecture/decisions/008-schema5-orchestration-and-country-outcomes.md)
- [ADR 009: Deterministic locality aggregation and overlap](architecture/decisions/009-deterministic-locality-aggregation-and-overlap.md)
- [ADR 010: Opportunity Filters as filter-only contracts](architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md)
- [ADR 011: TFCs as a sibling product role](architecture/decisions/011-tfcs-as-sibling-product-role.md)
- [ADR 012: Applicant, household and scenario separation](architecture/decisions/012-applicant-household-and-scenario-separation.md)
- [ADR 013: Effective profile context snapshots](architecture/decisions/013-effective-profile-context-snapshots.md)
- [ADR 014: Guest-first stateless evaluation](architecture/decisions/014-guest-first-stateless-evaluation.md)
- [ADR 015: Explicit browser retention consent](architecture/decisions/015-explicit-browser-retention-consent.md)
- [ADR 016: Typed TFC outcomes](architecture/decisions/016-typed-tfc-outcomes.md)
- [ADR 017: TFC assessment independence](architecture/decisions/017-tfc-assessment-independence.md)
- [ADR 018: Persistence as an adapter](architecture/decisions/018-persistence-as-adapter.md)
- [ADR 019: Centralized display metadata and release versioning](architecture/decisions/019-centralized-display-metadata-and-release-versioning.md)

## Operations

- [Local setup](operations/local-setup.md)
- [CI preflight and pre-push protection](operations/ci-preflight.md)
- [Worker guide](operations/worker.md)
- [Display-metadata-only release workflow](operations/display-metadata-release.md)
- [API guide](operations/api.md)
- [Phase 4E API contract](operations/phase4e-api-contract.md)
- [Local deployment](operations/deployment-local.md)
- [AWS deployment design](operations/deployment-aws.md)

## Data and methods

- [Source and licence audit](data/source-audit.md)
- [Scoring methodology](data/scoring-methodology.md)
- [Release format](data/release-format.md)
- [Phase 5C generic release foundation](architecture/phase5c-generic-release-foundation.md)
- [Locality scoring policy](data/locality-scoring-policy.md)
- [Locality assessment policy](product/locality-assessment-policy.md)
- [Phase 5D verification](product/phase5d-verification.md)
- [Phase 4C coverage contract](data/phase4c-coverage-contract.md)
- [Phase 4D ranking engine](product/phase4d-ranking-engine.md)
- [Phase 2D country coverage audit](data/country-coverage-phase-2d.md)
- [Phase 2D.4 homicide source feasibility](data/homicide-source-feasibility-phase-2d4.md)
- [Phase 3D feasibility probes](research/phase3d-feasibility-probes.md)
- [Phase 3E deterministic probes](research/phase3e-deterministic-probes.md)
- [Phase 3F portfolio decision](research/konsider_phase3f_portfolio_decision.md)
- [Phase 3G-0 final probes](research/phase3g0-final-probes.md)
- [Phase 3 closure report](research/phase3-closure-report.md)
- [Phase 5A locality criteria discovery](research/phase5a-locality-criteria-discovery.md)
- [Phase 5B target architecture and contracts](architecture/phase5b-target-contracts.md)
- [Phase 5E verification report](product/phase5e-verification.md)
- [Phase 5H contract migration](product/phase5h-contract-migration.md)

## Historical records

- [Implementation history](history/implementation-history.md)
- [Release history](history/releases/README.md)
- [Phase 4 closure report](history/phase4-closure-report.md)
- [Phase 5 closure report](history/phase5-closure-report.md)
- [Phase 6D Opportunity Filter contract report](history/phase6d-opportunity-filter-contracts.md)
- [Phase 6E career Opportunity Filter report](history/phase6e-career-opportunity-evidence.md)
- [Phase 6F education Opportunity Filter report](history/phase6f-education-opportunity-evidence.md)
- [Phase 6G Opportunity Filter engine and API report](history/phase6g-opportunity-filter-api.md)
- [Phase 6H Opportunity Filter UI report](history/phase6h-opportunity-filter-ui.md)
- [Phase 7H guest profile UI report](history/phase7h-guest-profile-ui.md)
- [Phase 7I cross-feature verification](history/phase7i-cross-feature-verification.md)
- [Phase 7 closure report](history/phase7-closure-report.md)
- [Release 2026-08-05.1](history/releases/2026-08-05.1.md)
- [Release 2026-08-07.2](history/releases/2026-08-07.2.md)
- [Release 2026-08-07.4](history/releases/2026-08-07.4.md)
- [Phase 6 closure report](history/phase6-closure-report.md)
- [Archived phase workspaces](../project-history/README.md)

Historical files explain what was delivered at a point in time; they are not operational
instructions. The active runtime serves schema-6.1 overlay `2026-08-07.4`, resolving immutable
schema-5.2 ranking base `2026-08-07.3`; older releases require explicit historical loaders.
