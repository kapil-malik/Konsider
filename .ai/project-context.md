# Konsider coding-assistant context

Code, tests, machine-readable contracts, current documentation, and release manifests are
authoritative. Do not revive older fixture-first plans from Git history or historical release notes.

## Orientation

- [Documentation index](../docs/README.md)
- [System architecture](../docs/architecture/system-architecture.md)
- [Worker operations](../docs/operations/worker.md)
- [API operations](../docs/operations/api.md)
- [Product roadmap](../docs/product/roadmap.md)
- [Active release report](../docs/history/releases/2026-07-21.1.md)

## Current state

The repository implements a local data worker, immutable release artifacts, a framework-independent
recommendation service, a typed FastAPI v1 API, and the Phase 2C responsive React UI. Active release
`2026-07-21.1` contains 20 countries and six criteria; five are enabled. UHC is non-ready.
Infrastructure is experimental. The browser remains catalog-driven and guest state is not saved.

## Non-negotiable boundaries

- Published releases are immutable; corrections use new IDs and change only the active pointer.
- Fixtures never fill product-release gaps.
- Missing, stale, rejected, or incomparable data remains explicit.
- The worker owns acquisition, canonical observations/scores, validation, and publication.
- `RecommendationService` owns ranking semantics. FastAPI is transport only. The UI must not score
  or decide readiness.
- Requests never fetch upstream data, recompute canonical scores, or switch releases.
- UHC cannot be weighted while non-ready; infrastructure must remain labelled experimental.
- Do not claim React, AWS, authentication, persistence, retrieval, chat, LLMs, agents, or MCP are
  implemented until code and tests establish that fact.

Run `pytest`, `ruff check .`, `black --check .`, and `python -m compileall -q src tests` after changes.
