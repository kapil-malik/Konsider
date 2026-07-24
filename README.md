# Konsider

Konsider is an evidence-backed country-suitability project. It implements a local official-data
refresh worker, immutable versioned releases, a deterministic recommendation service, a typed
FastAPI v1 API, and a responsive catalog-driven React comparison UI.

Active release `2026-07-24.1` contains 91 countries and six available criteria. Five are enabled for
ranking. UHC is unavailable because its latest official observation is stale; infrastructure is
enabled but explicitly experimental. Legacy fixtures are tests only and never fill product data.
Phase 2D is complete. Konsider supports the countries for which complete and sufficiently fresh data
is available across every enabled ranking criterion under the approved source and licensing policy.
The stable universe is generated from the audited complete-case intersection; no imputation or
partial-country scoring is used.

```text
official sources -> worker -> immutable local releases -> RecommendationService -> FastAPI /api/v1
                                      ^
                                      |
                               active.json pointer
```

AWS deployment, scheduled refresh, authentication, saved profiles, persistent sessions, retrieval,
chat, LLMs, agents, and MCP are not implemented. Guest preferences remain in browser memory only.

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

Start the responsive UI in a second terminal after following the API CORS instructions in the
[web application guide](web/README.md):

```powershell
Set-Location web
pnpm install
pnpm run generate:api
pnpm run dev
```

On Windows, after the Python and frontend dependencies are installed, the repository-root helper
commands manage both services in the background:

```powershell
.\start-local.cmd
.\restart-local.cmd
.\stop-local.cmd
```

The start command waits for both health checks and prints the UI and API documentation URLs. Runtime
PID state and logs are written to the ignored `.konsider-run` directory. See the
[local deployment guide](docs/operations/deployment-local.md) for prerequisites, overrides, and
troubleshooting.

Worker commands run from the repository root. A refresh downloads live official data and requires a
new release ID plus every printed source-version acknowledgement:

```powershell
python -m konsider.ingestion.worker list-sources
python -m konsider.ingestion.worker replay data\releases\2026-07-24.1
python -m konsider.ingestion.worker audit-coverage --universe data\country-universes\popular-relocation-v1.json --audit-id AUDIT_ID --mode offline --artifacts data\reports\country-coverage\coverage-2026-07-23.6\raw-artifacts.json
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

Frontend gates are documented in [web/README.md](web/README.md).

## Documentation

Start at the [documentation index](docs/README.md).

- [System architecture](docs/architecture/system-architecture.md)
- [Local setup](docs/operations/local-setup.md)
- [Worker operations](docs/operations/worker.md)
- [API operations and reference](docs/operations/api.md)
- [Release format](docs/data/release-format.md)
- [Phase 2D country coverage audit](docs/data/country-coverage-phase-2d.md)
- [Phase 2D.4 homicide source feasibility](docs/data/homicide-source-feasibility-phase-2d4.md)
- [Roadmap](docs/product/roadmap.md)
- [Active release report](docs/history/releases/2026-07-24.1.md)
