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
## Phase 2A JSON Schemas

Versioned Draft 2020-12 consumer schemas live in `contracts/schemas/v1`. They cover the active
pointer, manifest, validation report, source registration, observation (including derived
components), score, and consumer catalog. Payload schemas remain versioned independently while the
consumer rejects incompatible release, validation, and catalog major versions before joining data.
