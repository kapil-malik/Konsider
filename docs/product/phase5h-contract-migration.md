# Phase 5H final contract migration

Status: complete on 2026-07-29

Phase 5H makes the structured Phase 5 model the only active product contract. The active pointer
already selected replayed schema-5 release `2026-07-29.2`, so no release contents were mutated and
no semantically identical replacement release was published. Historical schema-3/4 releases remain
immutable and are available only to an explicitly configured internal audit loader.

## Final runtime

```text
data/releases/active.json
          |
          v
CurrentReleaseRepository (schema 5/catalog 3)
          |
          v
RecommendationService (structured domain)
          |
          v
five /api/v2 routes -> generated TypeScript types -> React UI
```

There is one startup release snapshot, one service, one public route family, and one generated
frontend contract. Coverage eligibility, locality compatibility, and applicant-profile
applicability are independent assessments. A locality advisory never changes country ranking
eligibility. Because the API accepts no applicant profile facts, profile assessment is always
explicitly `NO_PROFILE_CONTEXT`, evaluates no dimensions, and supplies a `NOT_EVALUATED` reason.

## Removed compatibility surface

| Removed item | Final owner or replacement |
| --- | --- |
| Five public `/api/v1` routes | The five `/api/v2` routes only |
| Dual legacy/current services at application startup | One schema-5 `RecommendationService` |
| Implicit `legacy-active.json` runtime pointer | `active.json` only; explicit release ID for historical audit |
| Schema-4-to-v2 mapper/adapter shims | Native structured schema-5 domain results |
| Standalone runtime catalog path and `KONSIDER_CATALOG_PATH` | Checksummed `consumer-catalog.json` inside the active release |
| Catalog `profiles` | `preference_presets` |
| Request `profile_id` | `preference_preset_id` |
| Response `resolved_profile_id` | `resolved_preference_preset_id` |
| Root-level coverage/uncertainty aliases and duplicate active-criterion lists | `assessments.coverage` |
| Root-level locality aliases | `assessments.locality` |
| Ambiguous profile status or evaluated placeholder dimensions | `assessments.profile` with explicit no-context semantics |
| Handwritten frontend legacy response aliases | OpenAPI-generated `/api/v2` component types |
| UI old-field fallbacks | Direct structured assessment rendering |
| Separate transitional API-v2 operations document | One authoritative API guide |

Outcome reason codes remain distinct from assessment explanations: an outcome explains why a
country/criterion value is unavailable, while an assessment reason explains the effect of that
fact on the current request. This is intentional domain separation, not a duplicate alias.

## Compatibility policy

- Published release directories and release-scoped historical catalogs were not edited.
- The internal historical loader requires a caller-supplied release ID and cannot select the active
  runtime implicitly.
- The public API rejects a schema-3/4 `active.json` pointer with a safe unavailable response.
- The exported OpenAPI document is authoritative; frontend types are regenerated from it.
- Compile-time negative checks intentionally mention retired fields to prove that they no longer
  exist. They are tests, not runtime fallbacks.

## Verification

Phase 5H gates cover:

- exactly five public `/api/v2` paths and no v1 or profile-management route;
- absence of removed aliases from OpenAPI and generated TypeScript;
- schema-5 active loading and safe schema-4 pointer rejection;
- coexistence of full/partial coverage with national/locality-derived scope;
- independent coverage and locality decisions;
- explicit unevaluated profile assessment without applicant input;
- no deprecated UI property access;
- deterministic replay of `2026-07-29.2`; and
- backend and frontend lint, formatting, type, component, build, and end-to-end suites.

Local verification completed on 2026-07-29:

| Gate | Result |
| --- | --- |
| Backend unit and integration coverage | 272 tests passed across the final grouped run; affected historical-loader tests were rerun after the last boundary tightening |
| Active release replay | `replay=PASSED` for `2026-07-29.2` |
| Python quality | Ruff, Black check, and compileall passed |
| Frontend static/build | TypeScript, ESLint, and Vite production build passed |
| Frontend component tests | 15 passed |
| Chromium end-to-end tests | 8 passed |

The operational contracts are the [API guide](../operations/api.md),
[worker guide](../operations/worker.md), [release format](../data/release-format.md), and
[UI guide](ui.md).
