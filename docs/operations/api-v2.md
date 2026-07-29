# Konsider API v2

Status: primary Phase 5 contract; API v1 remains temporarily available until Phase 5H.

Contract version: `konsider-api-2.0`

The generated OpenAPI document is authoritative. Every request and response model forbids
undocumented fields. Coverage, locality, and future applicant/household profile state have
separate owners under `assessments`.

## Routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/v2/health` | Report API and active-release readiness. |
| `GET` | `/api/v2/catalog` | Return criteria with orthogonal coverage, scope, applicability, source, readiness, and experimental metadata. |
| `POST` | `/api/v2/rankings` | Rank with structured coverage, locality, and profile assessments. |
| `POST` | `/api/v2/comparisons` | Compare available and unavailable evidence without client-side intersection logic. |
| `POST` | `/api/v2/countries/{country_code}/details` | Return country evidence and locality advice in one supplied weight context. |

Country details use `POST` because locality compatibility and active-criterion availability depend
on the same weight or preference-preset selection as a ranking. This avoids a hidden default
context and leaves room for later profile-aware inputs without adding query-string aliases.

## Weight selection

Ranking requests accept either `weights` or `preference_preset_id`, never both. If neither is
provided, the release's default equal-weight preset is selected. API v2 never accepts `profile_id`.

```json
{
  "preference_preset_id": "equal_weight_mvp",
  "top_k": 10
}
```

Comparison requests add two to ten unique country codes:

```json
{
  "country_codes": ["IND", "CAN"],
  "weights": {
    "intentional_homicide_rate": 1,
    "political_stability": 0.8
  }
}
```

## Authoritative assessment ownership

- `assessments.coverage` owns ranking-universe coverage state, active FCC/PCC sets, coverage
  fallback, and excluded-country evidence.
- `assessments.locality` owns request-wide locality policy, thresholds, and overlap summary.
- `assessments.profile` states whether actual applicant or household context was evaluated.
- Each ranked or compared country owns its country-specific locality and profile assessment.
- Coverage-excluded countries expose exact criterion outcomes and evidence but no final aggregate.

A lack of common locality is advisory and never makes an otherwise complete country result
coverage-excluded.

## Contribution provenance

Every contribution uses one general shape. National-direct contributions set locality policy
references to null and locality arrays to empty. Locality-derived contributions include:

- source and result scope;
- derivation type;
- aggregation policy and locality-universe versions;
- contributing locality entities and input scores;
- referenced observations and scores;
- typed source lineage;
- scoring and observation versions; and
- quality flags.

The API rejects a national contribution carrying locality-only fields and rejects incomplete
locality-derived provenance.

## Active schema-4 migration

The production release remains `2026-07-28.2` (`konsider-release-4.0`). Until a validated
schema-5 release is activated, API v2 uses a backend-only migration adapter:

- historical country evidence is represented as national-direct scope;
- existing source registrations become typed primary-observation lineage;
- coverage fields are moved into `assessments.coverage`;
- no locality evidence is invented; and
- preference preset names are translated without exposing legacy aliases in v2.

This adapter is temporary and scheduled for removal in Phase 5H. Historical release loaders remain
for audit and replay.
