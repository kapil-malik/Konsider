# API operations and reference

The Phase 2B API is a JSON-only FastAPI transport over `RecommendationService`. It loads and
validates one active immutable release snapshot during application startup, reuses it for the
process lifetime, and never fetches external sources or recomputes canonical 1-10 scores. Changing
`active.json` requires a process restart. Every successful response identifies its release,
release schema, catalog schema, and relevant scoring methods.

OpenAPI at `/openapi.json` is authoritative for transport shapes. Swagger UI is available at
`/docs`. Frontend types must be generated from OpenAPI or runtime-validated against it; prose
examples here are tested but remain illustrative. The current API namespace is `/api/v1`.

## Install and start

Follow [local setup](local-setup.md), then start Uvicorn from the repository root.

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn konsider.api.app:app --reload
```

Bash:

```bash
source .venv/bin/activate
python -m uvicorn konsider.api.app:app --reload
```

Uvicorn defaults to `127.0.0.1:8000`.

- Health: <http://127.0.0.1:8000/api/v1/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>

## Configuration

All settings are optional.

| Variable | Purpose | Default | Example |
| --- | --- | --- | --- |
| `KONSIDER_RELEASE_ROOT` | Directory containing release folders. | Repository `data/releases` | `/srv/konsider/releases` |
| `KONSIDER_ACTIVE_RELEASE_PATH` | Active pointer JSON. | `RELEASE_ROOT/active.json` | `/srv/konsider/releases/active.json` |
| `KONSIDER_CATALOG_PATH` | Versioned consumer catalog. | Repository `data/catalogs/consumer-catalog-1.0.json` | `/srv/konsider/catalog.json` |
| `KONSIDER_ENVIRONMENT` | Environment label exposed to application settings. | `development` | `staging` |
| `KONSIDER_LOG_LEVEL` | `konsider.api` logger level; uppercased. | `INFO` | `DEBUG` |
| `KONSIDER_CORS_ORIGINS` | Comma-separated exact browser origins. Empty disables CORS middleware. | empty | `http://localhost:5173` |

Local Phase 2C CORS example:

```powershell
$env:KONSIDER_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
python -m uvicorn konsider.api.app:app --reload
```

```bash
KONSIDER_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173" \
  python -m uvicorn konsider.api.app:app --reload
```

Allowed CORS methods are `GET` and `POST`; allowed request headers are `Content-Type` and
`X-Request-ID`. Credentials are disabled.

## Startup validation and degraded mode

Startup resolves `active.json`, validates supported schema majors, validates the pointer, manifest,
validation report, catalog, sources, observations, and scores against JSON Schemas, verifies every
declared payload checksum and the aggregate checksum, reconciles counts/readiness/method versions,
and joins complete country/criterion provenance.

Missing files, checksum failures, incompatible contracts, incomplete matrices, or broken lineage do
not expose local paths to clients. The process starts in controlled degraded mode and all endpoints
that need the service return `503`. Detailed exceptions are logged server-side. Unexpected runtime
failures use a safe `500` envelope.

## Endpoint summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Report API and active-release readiness. |
| `GET` | `/api/v1/catalog` | Return countries, all criteria, readiness, caveats, and profiles. |
| `POST` | `/api/v1/rankings` | Rank eligible countries with a profile or explicit weights. |
| `GET` | `/api/v1/countries/{country_code}/metrics` | Return one country's enabled metric breakdown. |
| `POST` | `/api/v1/comparisons` | Compare 2-10 selected countries using ranking semantics. |

## Command examples

### curl

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/catalog
curl -X POST http://127.0.0.1:8000/api/v1/rankings \
  -H "Content-Type: application/json" \
  -d '{"weights":{"ambient_pm25_population_weighted":3,"intentional_homicide_rate":2},"top_k":3}'
curl http://127.0.0.1:8000/api/v1/countries/ind/metrics
curl -X POST http://127.0.0.1:8000/api/v1/comparisons \
  -H "Content-Type: application/json" \
  -d '{"country_codes":["IND","SGP","CAN"],"profile_id":"equal_weight_mvp"}'
```

### PowerShell

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/catalog

$ranking = @{
  weights = @{ ambient_pm25_population_weighted = 3; intentional_homicide_rate = 2 }
  top_k = 3
} | ConvertTo-Json
Invoke-RestMethod -Method Post -ContentType "application/json" -Body $ranking `
  http://127.0.0.1:8000/api/v1/rankings

Invoke-RestMethod http://127.0.0.1:8000/api/v1/countries/ind/metrics

$comparison = @{
  country_codes = @("IND", "SGP", "CAN")
  profile_id = "equal_weight_mvp"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -ContentType "application/json" -Body $comparison `
  http://127.0.0.1:8000/api/v1/comparisons
```

## `GET /api/v1/health`

Returns `200` after successful startup validation or `503` in degraded mode. It has no parameters.

Representative complete response:

```json
{
  "release_id": "2026-07-26.3",
  "release_schema_version": "konsider-release-3.0",
  "catalog_schema_version": "consumer-catalog-1.0",
  "scoring_method_versions": [
    "homicide_risk_bands_v1",
    "icp_relative_cost_bands_v2",
    "infrastructure_readiness_bands_v1",
    "pm25_health_bands_v1",
    "wbl_legal_equality_bands_v1"
  ],
  "status": "ok",
  "country_count": 91,
  "enabled_criterion_count": 5,
  "ready_for_rankings": true
}
```

Initialization failure example (`503`):

```json
{
  "error": {
    "code": "release_unavailable",
    "message": "A validated active release is unavailable.",
    "details": {},
    "request_id": null
  }
}
```

## `GET /api/v1/catalog`

Returns `200`, `500`, or `503`. The response contains:

- 20 ISO-3 countries with display names and regions;
- six criteria with descriptions, direction, raw units, interpretation, caveats, quality limits,
  readiness, default-enabled state, experimental status, and scoring method version; and
- four provisional, user-editable profiles, with `equal_weight_mvp` as the documented default; and
- a public source mapping and source reference period for every criterion.

UHC is returned with `ready: false` and `default_enabled: false`. Infrastructure is returned with
`experimental: true`. Catalog metadata is authoritative for the UI.

Carefully abbreviated response:

```text
{
  "release_id": "2026-07-26.3",
  "release_schema_version": "konsider-release-3.0",
  "catalog_schema_version": "consumer-catalog-1.0",
  "scoring_method_versions": [six available method versions],
  "countries": [20 CountryResponse objects],
  "criteria": [six CriterionResponse objects],
  "profiles": [four ProfileResponse objects]
}
```

The current profile IDs are `equal_weight_mvp`, `safety_and_stability`, `affordability_first`, and
`quality_of_life`. Profile labels and raw weights remain server-owned and must not be duplicated in
the browser.

The route declares `200`, `422`, `500`, and `503`; because it has no input, `422` is not expected in
a normal call. Startup/catalog validation failures use the shared `503` envelope shown above.

## `POST /api/v1/rankings`

Request fields:

| Field | Rules |
| --- | --- |
| `weights` | Optional object of criterion ID to JSON number. Values must be finite and non-negative. Unknown and non-ready criteria are rejected. |
| `profile_id` | Optional non-empty catalog profile ID. Cannot be supplied with `weights`. |
| `top_k` | Optional strict integer from 1 through the active eligible count (currently 91). Defaults to all eligible countries. |

If neither selector is supplied, `equal_weight_mvp` is used. With explicit weights, omitted enabled
criteria receive zero. If every explicit weight is zero (including an empty object), the service
uses equal weights across all five enabled criteria. Non-zero weights are normalized to sum to one.

Canonical scores come from the release. A contribution is the published score multiplied by its
normalized weight. Totals are sorted descending; ties use ascending ISO-3 country code. Strengths
and trade-offs deterministically list up to three positively weighted criterion IDs ordered by high
and low canonical score respectively. See [scoring methodology](../data/scoring-methodology.md).

Complete request:

```json
{
  "weights": {
    "ambient_pm25_population_weighted": 3,
    "intentional_homicide_rate": 2,
    "household_consumption_price_level_us_100": 1
  },
  "top_k": 3
}
```

Carefully abbreviated `200` response:

```text
{
  "release_id": "2026-07-26.3",
  "release_schema_version": "konsider-release-3.0",
  "catalog_schema_version": "consumer-catalog-1.0",
  "scoring_method_versions": [five enabled method versions],
  "resolved_profile_id": null,
  "normalized_weights": {five enabled criterion IDs},
  "all_zero_behavior": "equal_weights_across_all_enabled_criteria",
  "country_tie_breaker": "ascending_iso3_country_code",
  "rounding_tolerance": 1e-8,
  "total_eligible_country_count": 91,
  "returned_result_count": 3,
  "rankings": [{
    "rank": 1,
    "country_code": "...",
    "country_name": "...",
    "region": "...",
    "total_score": 0.0,
    "contributions": [ContributionResponse with observations and source],
    "strengths": [criterion IDs],
    "tradeoffs": [criterion IDs]
  }]
}
```

Returns `200`, request/domain `422`, `500`, or `503`.

Non-ready weight example (`422`):

```json
{
  "error": {
    "code": "criterion_not_ready",
    "message": "One or more criteria are not available for ranking.",
    "details": {"criterion_ids": ["uhc_service_coverage_index"]},
    "request_id": null
  }
}
```

## `GET /api/v1/countries/{country_code}/metrics`

`country_code` is case-insensitive ISO-3 input; output is canonical uppercase. A successful response
contains the country and its five enabled criterion records. Each record contains catalog metadata,
canonical normalized score, transform and direction, observation IDs, raw values and units,
reference periods, method/parser versions, quality flags, exact source-record locators, and public
source metadata. Caveats, quality limitations, and experimental status come from the criterion.

UHC is excluded from normal product metrics because it is non-ready. Infrastructure remains present
and experimental. The route declares `200`, unknown-country `404`, `422`, `500`, and `503`.

Carefully abbreviated response:

```text
{
  "release_id": "2026-07-26.3",
  "release_schema_version": "konsider-release-3.0",
  "catalog_schema_version": "consumer-catalog-1.0",
  "scoring_method_versions": [five enabled method versions],
  "country": {"code": "IND", "display_name": "India", "region": "South Asia"},
  "criteria": [five CountryCriterionMetricResponse objects]
}
```

Unknown country example (`404`):

```json
{
  "error": {
    "code": "country_not_found",
    "message": "One or more country codes are unknown.",
    "details": {"country_codes": ["ZZZ"]},
    "request_id": null
  }
}
```

## `POST /api/v1/comparisons`

The body requires `country_codes` plus the same mutually exclusive `weights`/`profile_id` selector
used by rankings. Supply 2-10 unique known ISO-3 codes. Input is normalized to uppercase. Returned
countries preserve request order, while each row's `rank` remains its rank among all 91 eligible
countries under the selected weights.

```json
{
  "country_codes": ["IND", "SGP", "CAN"],
  "profile_id": "equal_weight_mvp"
}
```

The response has the same version, normalized-weight, tie-breaker, tolerance, and ranked-country
shapes as rankings, with `countries` instead of `rankings`. Returns `200`, unknown-country `404`,
selection/domain `422`, `500`, or `503`.

Carefully abbreviated response:

```text
{
  "release_id": "2026-07-26.3",
  "resolved_profile_id": "equal_weight_mvp",
  "normalized_weights": {five enabled criterion IDs},
  "total_eligible_country_count": 91,
  "returned_result_count": 3,
  "countries": [three RankedCountryResponse objects in requested order]
}
```

Invalid selection example (`422`):

```json
{
  "error": {
    "code": "invalid_comparison",
    "message": "Comparisons require between 2 and 10 countries.",
    "details": {},
    "request_id": null
  }
}
```

## Errors

All errors share this envelope. `request_id` echoes `X-Request-ID` when provided.

```json
{
  "error": {
    "code": "criterion_not_ready",
    "message": "One or more criteria are not available for ranking.",
    "details": {"criterion_ids": ["uhc_service_coverage_index"]},
    "request_id": null
  }
}
```

| Code | HTTP | Meaning |
| --- | ---: | --- |
| `request_validation_failed` | 422 | JSON or Pydantic transport validation failed. |
| `unknown_criterion` | 422 | A weight key is not in the catalog. |
| `criterion_not_ready` | 422 | A known non-ready criterion, currently UHC, was weighted. |
| `invalid_weight` | 422 | A weight is negative, non-finite, invalid, or cannot normalize. |
| `invalid_top_k` | 422 | `top_k` is not an integer from 1 through the eligible count. |
| `invalid_profile_selection` | 422 | Both `weights` and `profile_id` were supplied. |
| `profile_not_found` | 422 | The selected profile ID does not exist. |
| `invalid_comparison` | 422 | Country count is outside 2-10 or codes are duplicated. |
| `country_not_found` | 404 | One or more ISO-3 country codes are unknown. |
| `unsupported_release_contract` | 503 | Active release uses an unsupported schema major. |
| `release_unavailable` | 503 | Active release is missing, corrupt, invalid, or failed startup validation. |
| `internal_error` | 500 | An unexpected failure occurred; private details remain server-side. |
