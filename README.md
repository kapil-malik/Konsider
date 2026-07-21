# Konsider

Konsider is an evidence-backed country-suitability project. It currently implements a local official-
data refresh worker, immutable versioned releases, a deterministic recommendation service, and a
typed FastAPI v1 API.

Active release `2026-07-21.1` contains 20 countries and six available criteria. Five are enabled for
ranking. UHC is unavailable because its latest official observation is stale; infrastructure is
enabled but explicitly experimental. Legacy fixtures are tests only and never fill product data.

```text
official sources -> worker -> immutable local releases -> RecommendationService -> FastAPI /api/v1
                                      ^
                                      |
                               active.json pointer
```

React UI, AWS deployment, scheduled refresh, authentication, saved profiles, persistent sessions,
retrieval, chat, LLMs, agents, and MCP are not implemented. Phase 2C adds the catalog-driven UI next.

## Quick start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
python -m uvicorn konsider.api.app:app --reload
```

Health is available at <http://127.0.0.1:8000/api/v1/health> and interactive API documentation at
<http://127.0.0.1:8000/docs>.

Worker commands run from the repository root. A refresh downloads live official data and requires a
new release ID plus every printed source-version acknowledgement:

```powershell
python -m konsider.ingestion.worker list-sources
python -m konsider.ingestion.worker replay data\releases\2026-07-21.1
```

See the [worker guide](docs/operations/worker.md) for the complete refresh command and publication
rules. Full replay requires ignored raw bytes retained under `data/raw`.

## Quality gates

```bash
pytest
ruff check .
black --check .
python -m compileall -q src tests
```

GitHub Actions runs the same gates on Ubuntu.

## Documentation

Start at the [documentation index](docs/README.md).

- [System architecture](docs/architecture/system-architecture.md)
- [Local setup](docs/operations/local-setup.md)
- [Worker operations](docs/operations/worker.md)
- [API operations and reference](docs/operations/api.md)
- [Release format](docs/data/release-format.md)
- [Roadmap](docs/product/roadmap.md)
- [Active release report](docs/history/releases/2026-07-21.1.md)
