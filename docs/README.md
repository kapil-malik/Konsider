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
- [Phase 2C UI](product/ui.md) - implemented product behavior and technical boundaries.

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

## Historical records

- [Implementation history](history/implementation-history.md)
- [Release history](history/releases/README.md)

Historical files explain what was delivered at a point in time; they are not operational
instructions. The active release is `2026-07-21.1`.
