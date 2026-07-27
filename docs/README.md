# Konsider documentation

This is the authoritative documentation index for the current repository. Code, tests, machine-
readable schemas, and published release manifests take precedence if prose ever disagrees.

## Start here

- [System architecture](architecture/system-architecture.md) - implemented boundaries, selected
  next steps, and deferred options.
- [Local setup](operations/local-setup.md) - install and verify a clean checkout.
- [Worker operations](operations/worker.md) - refresh, publish, replay, inspect, and roll back data.
- [API operations and reference](operations/api.md) - configure, start, and use all five routes.
- [Product roadmap](product/roadmap.md) - current position and forward plan.
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

## Operations

- [Local setup](operations/local-setup.md)
- [Worker guide](operations/worker.md)
- [API guide](operations/api.md)
- [Local deployment](operations/deployment-local.md)
- [AWS deployment design](operations/deployment-aws.md)

## Data and methods

- [Source and licence audit](data/source-audit.md)
- [Scoring methodology](data/scoring-methodology.md)
- [Release format](data/release-format.md)
- [Phase 2D country coverage audit](data/country-coverage-phase-2d.md)
- [Phase 2D.4 homicide source feasibility](data/homicide-source-feasibility-phase-2d4.md)
- [Phase 3D feasibility probes](research/phase3d-feasibility-probes.md)
- [Phase 3E deterministic probes](research/phase3e-deterministic-probes.md)
- [Phase 3F portfolio decision](research/konsider_phase3f_portfolio_decision.md)
- [Phase 3G-0 final probes](research/phase3g0-final-probes.md)
- [Phase 3 closure report](research/phase3-closure-report.md)

## Historical records

- [Implementation history](history/implementation-history.md)
- [Release history](history/releases/README.md)

Historical files explain what was delivered at a point in time; they are not operational
instructions. The active release is `2026-07-27.1`.
