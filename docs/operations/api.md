# Konsider API operations and contract

Status: authoritative active Phase 6 public contract

Contract version: `konsider-api-2.0`

Active release: `2026-08-04.1`

Konsider exposes one structured API over the schema-current immutable ranking release selected by
`data/releases/active.json`. Release `2026-08-04.1` binds the active Opportunity Filter catalog and
evidence in the same checksummed publication envelope. The generated
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

Neither catalog accepts a runtime override. Catalog 3 and the sibling Opportunity Filter catalog
are bound to and checksummed by the selected immutable release.

## Public routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/v2/health` | Report active-release readiness. |
| `GET` | `/api/v2/catalog` | Return criteria, canonical countries, and preference presets. |
| `GET` | `/api/v2/opportunity-filters` | Return the loaded filter-only catalog and coverage summary. |
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

## Opportunity Filter selection

Ranking, comparison, and country-details requests accept this additive sibling of the weight
selection:

```json
{
  "preference_preset_id": "equal_weight_mvp",
  "opportunity_filters": {
    "mode": "ALL_REQUIRED",
    "required_filter_ids": [
      "technology_software_opportunity",
      "computer_science_ict_education_opportunity"
    ]
  },
  "top_k": 10
}
```

Omitting `opportunity_filters`, or providing an empty `required_filter_ids`, preserves the exact
unfiltered response. Selected IDs must be unique, known, and active in the configured bundle.
Only `ALL_REQUIRED` is supported: every selected state must be `VERIFIED_STRONG_SIGNAL` for the
country to survive. Unknown, inactive, duplicate, weighted, or OR-style selections fail with 422.

The service always computes the canonical ranking first. Filtering then preserves every survivor's
score, normalized weights, contribution values, canonical `base_rank`, and relative order; only
`filtered_rank` is recomputed. `top_k` is applied after filtering. Selected-filter results include
all countries tied at the score boundary. The no-filter path retains the established exact `top_k`
slice for byte-compatible behavior. A valid filter result may contain zero countries and reports
`NO_COUNTRIES_MATCH`; it never falls back to an unfiltered list.

## Authoritative response ownership

Ranking, comparison, and country-details responses contain:

- `assessments.coverage`: active global-core and conditional criteria, coverage fallback,
  excluded-country evidence, and structured coverage reasons;
- `assessments.locality`: contributing locality criteria, threshold-triggered analysis,
  aggregation policies, and response-wide locality status;
- `assessments.profile`: explicit `NO_PROFILE_CONTEXT`, no evaluated dimensions, and a
  `NOT_EVALUATED` reason; and
- `assessments.opportunity`: selected filters, strict-AND counts, per-filter state counts,
  exclusions, and the independent Opportunity Filter release identity.

Ranked and compared countries carry only their country-specific locality and profile assessments.
Coverage does not appear in locality statuses. A locality advisory never changes country
eligibility or the country aggregate.

Ranked countries also carry `base_rank`, `filtered_rank`, and their selected-filter evidence.
Comparisons preserve canonical score and base rank for a requested country excluded only by an
Opportunity Filter and mark it `opportunity_excluded`. Country details expose bounded evidence for
the selected filters. Responses do not expose raw metric payloads; the catalog and summaries carry
construct, limitations, state, route, period, source, confidence, and reason information needed to
explain the decision.

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

Opportunity Filter selection errors use stable 422 codes:

- `unknown_opportunity_filter`;
- `opportunity_filter_not_active`; and
- `invalid_opportunity_filter_selection`.

The bundle is parsed and cross-validated once at application startup. Request-time assessment uses
indexed definitions and country evidence only; it performs no source I/O. Opportunity Filters do
not alter FCC/PCC activation, LSC aggregation, coverage fallback, imputation, profile assessment,
normalization, weights, affinity scores, or the canonical ranking engine.

## Historical boundary

Schema-3/4 release and catalog readers remain internal for explicit audit and historical
regression. They are not consulted by the active application and do not expose HTTP routes.
