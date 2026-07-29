# Konsider API operations and contract

Status: authoritative Phase 5H public contract

Contract version: `konsider-api-2.0`

Active release: `2026-07-29.2`

Konsider exposes one structured API over the schema-current immutable release selected by
`data/releases/active.json`. The generated
[`contracts/openapi/konsider-api-2.0.json`](../../contracts/openapi/konsider-api-2.0.json)
document is authoritative. Undocumented request fields are rejected.

## Start

From the repository root:

```text
python -m uvicorn konsider.api.app:app --reload
```

The default service is `http://127.0.0.1:8000`. Swagger UI is at `/docs` and OpenAPI is at
`/openapi.json`.

| Setting | Meaning | Default |
| --- | --- | --- |
| `KONSIDER_RELEASE_ROOT` | Immutable release directories. | `data/releases` |
| `KONSIDER_ACTIVE_RELEASE_PATH` | Schema-5 active pointer. | `data/releases/active.json` |
| `KONSIDER_ENVIRONMENT` | Deployment label. | `development` |
| `KONSIDER_LOG_LEVEL` | Python log level. | `INFO` |
| `KONSIDER_CORS_ORIGINS` | Comma-separated browser origins. | none |

The active runtime does not accept a separate catalog override. Catalog 3 is embedded in and
checksummed with each schema-5 release.

## Public routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/v2/health` | Report active-release readiness. |
| `GET` | `/api/v2/catalog` | Return criteria, canonical countries, and preference presets. |
| `POST` | `/api/v2/rankings` | Rank countries with structured assessments. |
| `POST` | `/api/v2/comparisons` | Compare two to ten countries. |
| `POST` | `/api/v2/countries/{country_code}/details` | Return contextual country evidence. |

There are no public v1 routes or aliases.

## Weight selection

Requests accept either `weights` or `preference_preset_id`, never both. If neither is supplied,
the server selects the default equal-weight preference preset.

```json
{
  "preference_preset_id": "equal_weight_mvp",
  "top_k": 10
}
```

`profile_id` is not a weight-preset alias. Profile terminology is reserved for future typed
applicant or household context.

## Authoritative response ownership

Ranking, comparison, and country-details responses contain:

- `assessments.coverage`: active global-core and conditional criteria, coverage fallback,
  excluded-country evidence, and structured coverage reasons;
- `assessments.locality`: contributing locality criteria, threshold-triggered analysis,
  aggregation policies, and response-wide locality status;
- `assessments.profile`: explicit `NO_PROFILE_CONTEXT`, no evaluated dimensions, and a
  `NOT_EVALUATED` reason.

Ranked and compared countries carry only their country-specific locality and profile assessments.
Coverage does not appear in locality statuses. A locality advisory never changes country
eligibility or the country aggregate.

Criterion catalog entries have root identity and interpretation fields plus exactly one
`coverage`, one `scope`, and one `applicability` object. Weight-only catalog entries are
`preference_presets`.

## Evidence and errors

National contributions carry direct country evidence. Locality-derived contributions additionally
carry the frozen locality universe, aggregation policy, contributor entities, observations,
scores, and source lineage. Unavailable criterion cells have an outcome and evidence reasons but
no contribution.

Errors use:

```json
{
  "error": {
    "code": "request_validation_failed",
    "message": "The request payload is invalid.",
    "details": {},
    "request_id": null
  }
}
```

Invalid input returns 422, unknown countries return 404, unavailable active releases return 503,
and unexpected failures return a redacted 500.

## Historical boundary

Schema-3/4 release and catalog readers remain internal for explicit audit and historical
regression. They are not consulted by the active application and do not expose HTTP routes.
