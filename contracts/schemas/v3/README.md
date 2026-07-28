# Phase 5 target contract schemas

Status: design contracts; not active production contracts

Schema generation `v3` defines the clean Phase 5 target:

- release schema `konsider-release-5.x`;
- consumer catalog `consumer-catalog-3.x`;
- API contract marker `konsider-api-2.0`; and
- generated TypeScript surface `konsider-api-types-2.x`.

The schema-directory generation is not the release-schema major. Existing `v1` and `v2` schemas
remain immutable and supported for historical inspection.

Contracts:

- `criterion-definition` separates core fields, coverage, scope, and applicability;
- `criterion-policy` snapshots parser, scoring, source, derivation, and readiness orchestration;
- `geographic-entity` defines canonical country and locality identity;
- `geographic-observation` and `geographic-score` use entity-neutral subjects;
- `criterion-outcome` keeps every country result or non-result explicit without overloading
  `country_code`;
- `source-lineage` represents every source input and transform independently;
- `locality-universe` freezes independent locality selection;
- `locality-aggregation-policy` versions locality-to-country derivation;
- `derived-country-evidence` preserves contributing locality and replay lineage;
- `consumer-catalog` uses `preference_presets`;
- `release-manifest` declares the target immutable artifact set;
- `validation-report` reconciles coverage, lineage, policies, and artifact counts; and
- `ranking-request` and `ranking-response` define the clean API v2 assessment shape.

The synthetic valid and invalid examples are under `tests/fixtures/phase5b`. They are contract
evidence only and must never be published as product data.
