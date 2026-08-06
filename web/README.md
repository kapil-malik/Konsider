# Konsider web application

The Phase 6H UI is a responsive React, TypeScript, and Vite application over the local FastAPI
`/api/v3` contract. It uses TanStack Query for API state, local React state for unapplied guest
preferences, generated TypeScript types from FastAPI OpenAPI, Vitest and React Testing Library for
component coverage, and Playwright for focused browser flows.

The browser never scores, normalizes, sorts, selects localities, calculates locality intersections,
chooses a best common locality, determines assessment statuses, or supplies fallback product data.
Countries, criteria, preference presets, Opportunity Filter definitions/evidence, sources,
contributions, structured assessments, flags, and release IDs come from the API. Opportunity
Filters are checkbox-only strict restrictions; they never become score weights in the browser.
The current 91-country release is shown in a bounded desktop table and complete mobile cards.
Country-name/ISO search and API-derived region filtering are client-side because the bounded global
response remains small enough that server pagination is not justified.

## Requirements

- Node.js 22 or newer
- pnpm 11 (the exact package manager is recorded in `package.json`)
- the repository Python environment from [local setup](../docs/operations/local-setup.md)

## Configure

Copy `.env.example` to `.env.local` only when the API is not available at the default URL:

```text
VITE_KONSIDER_API_BASE_URL=http://127.0.0.1:8000/api/v3
```

Only browser-safe `VITE_` variables belong here. Do not add secrets.

## Start locally

Start the API first from the repository root.

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:KONSIDER_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
python -m uvicorn konsider.api.app:app --reload
```

Bash:

```bash
source .venv/bin/activate
KONSIDER_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173" \
  python -m uvicorn konsider.api.app:app --reload
```

In a second terminal:

```bash
cd web
pnpm install
pnpm run generate:api
pnpm run dev
```

Open <http://127.0.0.1:5173>. If you use `http://localhost:5173`, ensure that exact origin is in
`KONSIDER_CORS_ORIGINS`.

## Contract generation and quality gates

`pnpm run generate:api` exports OpenAPI directly from the local FastAPI application and regenerates
`src/api/openapi.json` plus `src/api/schema.d.ts`. Run it after any Pydantic transport change and
commit both generated files.

```bash
pnpm run generate:api
pnpm run typecheck
pnpm run lint
pnpm run test --run
pnpm run build
pnpm run e2e
```

Use `pnpm run test:watch` while developing. Playwright uses deterministic mocked API responses and
starts Vite on port 4173. The normal development UI uses port 5173; FastAPI uses port 8000.
Before any push, run `python scripts/verify_ci.py --clean-revision HEAD` from the repository root;
it includes all commands above and detects generated-contract drift.
The browser loads Opportunity Filter definitions from `GET /api/v3/opportunity-filters` and sends
selected IDs with ranking, comparison, and country-detail requests; the API remains authoritative
for strict-AND evaluation and evidence explanations.

## Troubleshooting

- **The UI says it cannot reach the API:** start Uvicorn and confirm
  <http://127.0.0.1:8000/api/v3/health> returns `200`.
- **The browser reports a CORS failure:** add the exact Vite origin to
  `KONSIDER_CORS_ORIGINS`, then restart Uvicorn.
- **Generated types changed unexpectedly:** confirm the intended Python environment and active
  checkout, rerun `pnpm run generate:api`, and inspect both generated files.
- **Playwright has no browser:** run `pnpm exec playwright install chromium` once, then rerun
  `pnpm run e2e`.
