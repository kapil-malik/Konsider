# Konsider Contracts

This directory is reserved for machine-readable contracts shared between deployable applications.

When the live API is introduced, FastAPI-generated OpenAPI will be committed or generated in CI as
the canonical website contract. Event and dataset schemas may be added here once their producing
and consuming implementations exist. Hand-authored speculative schemas are intentionally avoided.

The first machine-readable contracts should cover:

- OpenAPI for `/api/v1` catalog, ranking, metrics, evidence, and chat endpoints.
- Release artifact schemas for catalog, metrics, observations, evidence, and manifests.
- SSE event schemas for chat and profile/ranking updates.

Current human-readable contracts are documented in:

- `docs/architecture.md`
- `docs/components/data-refresh-worker.md`
- `docs/components/live-engine.md`
- `docs/components/web-application.md`
- `docs/storage.md`
