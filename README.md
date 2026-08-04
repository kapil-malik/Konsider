# Konsider

Konsider is an evidence-backed country-suitability project. It implements a local official-data
refresh worker, immutable versioned releases, a deterministic recommendation service, a typed
FastAPI v2 API, and a responsive catalog-driven React comparison UI.

Active release `2026-07-29.2` contains 91 countries, 388 selected urban centres, and fourteen
catalogued criteria. Eight global-core criteria cover all countries; Overall job-market
opportunity, School education quality, Research and innovation ecosystem, Extreme heat exposure,
and Projected warm-day frequency (2030) use conditional complete-case ranking. UHC is unavailable,
while infrastructure, the Phase 4 Wave 2 criteria, and both locality-derived climate criteria are
experimental. Legacy fixtures never fill product data. Rankings use complete cases across active
criteria, keep missing/stale outcomes explicit, and never impute or calculate partial country
scores.

```text
official sources -> worker -> immutable local releases -> RecommendationService -> FastAPI /api/v2
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

Health is available at <http://127.0.0.1:8000/api/v2/health> and interactive API documentation at
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
python -m konsider.ingestion.phase5_locality_onboarding --replay data\releases\2026-07-29.2
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

GitHub Actions runs the backend gates from clean Ubuntu and Windows checkouts.

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
- [Phase 3 closure report](docs/research/phase3-closure-report.md)
- [Roadmap](docs/product/roadmap.md)
- [Phase 4F onboarding report](data/reports/phase4f-2026-07-28/report.md)
- [Phase 4 Wave 2 onboarding report](data/reports/phase4-wave2-2026-07-28/report.md)
- [Phase 4 Wave 2 PCC candidates](docs/research/phase4-wave2-pcc-candidates.md)
- [Phase 4 closure report](docs/history/phase4-closure-report.md)
- [Phase 5 closure report](docs/history/phase5-closure-report.md)
- [Phase 5 verification report](data/reports/phase5i-2026-07-29/report.md)
- [Historical phase workspaces](project-history/README.md)
- [Phase 6 closure report](docs/history/phase6-closure-report.md)
- [Active release report](docs/history/releases/2026-08-04.1.md)
