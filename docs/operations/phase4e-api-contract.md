# Phase 4E: uncertainty-aware API contract

Status: implemented on existing API v1 paths

Policy: `uncertainty-aware-ranking-policy-1.0`

Phase 4E upgrades `POST /api/v1/rankings`, `POST /api/v1/comparisons`, and
`GET /api/v1/catalog`. It does not add a second ranking endpoint. FastAPI routes only select the
service method and map typed domain results; ranking and completeness decisions remain in the
Phase 4D domain layer.

## Catalog additions

Every catalog criterion now includes:

- `enabled`, `ready`, and `default_enabled`;
- `coverage_mode`;
- `valid_country_count`, `stable_country_count`, `coverage_percentage`, and
  `missing_country_count`;
- `pcc_activation_threshold`;
- `experimental`; and
- `concise_caveat`.

Schema-3 ready criteria retain their historical `GLOBAL_CORE` meaning. A schema-3 non-ready
criterion is exposed as `DIAGNOSTIC_ONLY`; it is never inferred to be a PCC.

## Ranking request and response

`top_k` is a strict positive integer and now defaults to 10. Tie-inclusive score-boundary
membership means the response can contain more than K ranked countries. The existing `weights`
and `profile_id` selection rules are unchanged.

The response preserves the existing ranking rows and contribution evidence while adding:

- stable, eligible, and excluded universe sizes;
- `ranking_coverage_mode`;
- active FCC/PCC and threshold-ignored PCCs;
- excluded countries with non-ready criteria and source reason codes;
- uncertainty status, coverage band, reason codes, and message code;
- robustness K and Kth eligible score;
- potential excluded entrants;
- compact baseline boundary membership; and
- policy version and thresholds.

Ranked countries and excluded countries are separate collections. A coverage-limit result is HTTP
200 with the FCC baseline, `ranking_coverage_mode: "GLOBAL_CORE"`, and
`kth_eligible_score: null`. It is not a transport error.

## Examples for every uncertainty status

The following are deliberately abbreviated. The complete OpenAPI schema is authoritative.

```json
{"uncertainty_status":"NO_PARTIAL_CRITERIA_ACTIVE","ranking_coverage_mode":"GLOBAL_CORE","active_pcc_ids":[]}
```

```json
{"uncertainty_status":"FULL_COVERAGE","ranking_coverage_mode":"CONDITIONAL_COMPLETE_CASE","excluded_country_count":0}
```

```json
{"uncertainty_status":"ROBUST_TOP_K","excluded_country_count":3,"potential_excluded_entrants":[]}
```

```json
{"uncertainty_status":"POTENTIALLY_AFFECTED","potential_excluded_entrants":["AAA"],"kth_eligible_score":7.25}
```

```json
{"uncertainty_status":"BASELINE_TOP_K_EXCLUDED","excluded_countries":[{"country_code":"AAA","baseline_top_k_member":true}]}
```

```json
{"uncertainty_status":"COVERAGE_LIMIT_EXCEEDED","ranking_coverage_mode":"GLOBAL_CORE","kth_eligible_score":null}
```

## Comparison evidence matrix

Comparisons retain the existing country order and ranked-country collection, and add
`country_summaries`, `criterion_rows`, and `requested_excluded_countries`.

Each country/criterion cell has one availability state:

- `AVAILABLE`;
- `MISSING`;
- `STALE`;
- `INVALID`; or
- `REJECTED`.

An unavailable cell has null values plus exact reason codes and source identity. It may be
displayed even when its PCC is inactive. Country summaries therefore distinguish:

- `comparison_data_complete`: all displayed criterion cells are available; and
- `ranking_eligible`: every active ranking criterion is available and a final ranking exists.

Example:

```json
{
  "country_summaries": [
    {
      "country_code": "ATG",
      "comparison_data_complete": false,
      "ranking_eligible": false,
      "aggregate_kind": "NONE",
      "ranking_status": "NOT_RANKED_ACTIVE_DATA_GAP",
      "total_score": null,
      "rank": null
    }
  ],
  "criterion_rows": [
    {
      "criterion_id": "overall_job_market_opportunity_fixture",
      "cells": [
        {
          "country_code": "ATG",
          "availability": "MISSING",
          "normalized_score": null,
          "reason_codes": ["COV_SOURCE_RECORD_MISSING"]
        }
      ]
    }
  ]
}
```

No country-specific weight renormalization or partial aggregate score is produced. When the global
coverage gate blocks R1, a comparison may include the complete FCC aggregate with
`aggregate_kind: "FCC_BASELINE"` and `ranking_status: "FCC_BASELINE_ONLY"`.

Phase 4G owns visual table layout, em dashes, badges, highlighting, tooltips, and disclaimer text.
