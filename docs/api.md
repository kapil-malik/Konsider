# Konsider API v1

Status: Phase 2B implemented

The API is a JSON-only FastAPI adapter over one immutable `RecommendationService` snapshot. It reads
published release files, never calls official sources, and never recalculates canonical 1-10 scores.
OpenAPI is generated at `/openapi.json`; interactive documentation is available at `/docs` locally.

## Start and configure

```powershell
python -m pip install -e .[dev]
python -m uvicorn konsider.api.app:app --reload
```

Optional environment variables are `KONSIDER_RELEASE_ROOT`, `KONSIDER_ACTIVE_RELEASE_PATH`,
`KONSIDER_CATALOG_PATH`, `KONSIDER_ENVIRONMENT`, `KONSIDER_LOG_LEVEL`, and a comma-separated
`KONSIDER_CORS_ORIGINS`. CORS is disabled unless explicit origins are supplied. Defaults target the
local source checkout and do not depend on the launch directory. Restart the process after changing
the active pointer; automatic snapshot polling is deferred.

## Endpoints

```text
GET  /api/v1/health
GET  /api/v1/catalog
POST /api/v1/rankings
GET  /api/v1/countries/{country_code}/metrics
POST /api/v1/comparisons
```

Health:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Catalog, including all six criteria and the non-ready UHC entry:

```bash
curl http://127.0.0.1:8000/api/v1/catalog
```

Ranking with explicit weights and a top-three response:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/rankings \
  -H "Content-Type: application/json" \
  -d '{"weights":{"intentional_homicide_rate":5,"ambient_pm25_population_weighted":4},"top_k":3}'
```

Omitting both `weights` and `profile_id` selects `equal_weight_mvp`. A request may instead provide
`profile_id`, or provide explicit `weights`, but not both. Omitted enabled weights are zero. Explicit
all-zero weights retain Phase 2A's equal-weight behavior. `top_k` defaults to all 20 and must be 1-20.

Country metrics accept case-insensitive ISO-3 input and return canonical uppercase codes:

```bash
curl http://127.0.0.1:8000/api/v1/countries/ind/metrics
```

Comparison requires 2-10 unique countries and uses the same profile/weight semantics:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/comparisons \
  -H "Content-Type: application/json" \
  -d '{"country_codes":["IND","SGP","CAN"],"profile_id":"equal_weight_mvp"}'
```

Successful responses identify the release, release schema, catalog schema, and relevant scoring
methods. Rankings and comparisons include normalized weights, totals, contributions, observations,
public source metadata, caveats, and experimental flags. UHC cannot be weighted and is absent from
normal metric breakdowns; infrastructure is marked experimental.

## Errors

Errors share one envelope:

```json
{"error":{"code":"criterion_not_ready","message":"One or more criteria are not available for ranking.","details":{"criterion_ids":["uhc_service_coverage_index"]},"request_id":null}}
```

Stable codes include `request_validation_failed`, `unknown_criterion`, `criterion_not_ready`,
`invalid_weight`, `invalid_top_k`, `country_not_found`, `invalid_comparison`,
`release_unavailable`, `unsupported_release_contract`, and `internal_error`. Server-side diagnostics
retain failure context while public `500` and `503` responses omit stack traces and filesystem paths.

S3 storage, Lambda/API Gateway adapters, authentication, rate limiting, UI code, chat, and generated
explanations are deliberately deferred.

## Continuous integration

`.github/workflows/ci.yml` checks the backend on Ubuntu for pushes and pull requests. Run its gates
locally from the repository root before opening or merging a change:

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
black --check .
python -m compileall -q src tests
```

CI deliberately uses the committed active release. Its checkout therefore also exercises LF
normalization and release checksum validation on Linux.
