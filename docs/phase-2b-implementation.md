# Phase 2B implementation and verification

Status: complete on 2026-07-21

Phase 2B exposes the Phase 2A recommendation service through five typed `/api/v1` FastAPI endpoints.
Routes contain no scoring, readiness, checksum, or provenance business rules. Pydantic contracts and
pure mapping functions protect the public response shape, while typed application/repository errors
produce stable HTTP envelopes.

One complete active release is loaded during application lifespan startup and reused for all
requests. Explicit settings remove launch-directory dependence. A restart is required to adopt a
new active pointer. Missing, corrupt, and unsupported releases place the API in a controlled `503`
state without exposing local paths.

Verification covers successful models, error envelopes, all five OpenAPI paths, catalog readiness,
ranking determinism and reconciliation, weight/profile/top-k semantics, case-insensitive country
lookups, comparison bounds, single construction, path injection, working-directory independence,
safe `500`/`503` responses, and regression of the complete Phase 2A suite.

Final local verification:

- `python -m pytest -q`: 92 passed, 0 failed, 0 skipped.
- `python -m ruff check .`: passed.
- `python -m black --check .`: passed across 57 files.
- `python -m compileall -q src tests`: passed.
- `python -m konsider.ingestion.worker replay data/releases/2026-07-20.2`: passed.
- Uvicorn was started from outside the repository root and returned a healthy 20-country,
  five-enabled-criterion snapshot.
