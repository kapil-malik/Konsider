# ADR 007: Structured assessments and preference-preset terminology

Status: accepted for the Phase 5 target contract

## Context

Phase 4 ranking responses expose coverage and uncertainty fields at the response root. Phase 5
adds request-wide and country-specific locality analysis while reserving profile assessment for
future applicant or household context. Adding more top-level status fields would create duplicate
and contradictory sources of truth.

The current catalog's “profiles” contain only weight presets. Calling them profiles conflicts with
the future meaning of applicant and household profiles.

## Decision

The clean API v2 target has one response-level `assessments` envelope:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {}
  }
}
```

Each ranked country has `assessments.locality` and `assessments.profile`. Country rows do not
repeat response-level coverage state.

Field ownership is:

- response coverage: active FCC/PCC sets, excluded country entities, coverage policy, and fallback;
- response locality: active LSCs, criteria crossing the raw-weight `0.6` analysis threshold,
  aggregation policies, and an overall summary;
- response profile: whether profile context existed and which dimensions were evaluated;
- country locality: eligible, valid, contributing, and common localities plus overlap/evidence
  status; and
- country profile: future country suitability for supplied profile dimensions.

Structured reasons contain `code`, `severity`, and `effect`. Locality statuses are:

- `NO_ACTIVE_LOCALITY_CRITERIA`;
- `BELOW_ANALYSIS_THRESHOLD`;
- `ONE_ACTIVE_LOCALITY_CRITERION`;
- `COMMON_LOCALITY_AVAILABLE`;
- `PARTIAL_OVERLAP`;
- `NO_COMMON_LOCALITY`;
- `INSUFFICIENT_LOCALITY_EVIDENCE`; and
- `MIXED_COUNTRY_RESULTS` for a response containing different country-level results.

Locality status names never encode FCC, PCC, missing-union, or other coverage state.

Phase 5 without applicant context uses `NO_PROFILE_CONTEXT` or `NOT_EVALUATED`; it does not invent
profile defaults.

Weight-only catalog entries become `preference_presets`. API v2 uses
`preference_preset_id` and `resolved_preference_preset_id`. The word `profile` is reserved for
actual applicant/household assessment.

## Consequences

- Coverage, locality, and profile messages cannot overwrite one another.
- The UI can render typed reasons without reproducing domain decisions.
- A country can retain an independently derived score while separately warning that its best
  localities do not overlap across active LSCs.
- Generated TypeScript types derive from the API v2 OpenAPI document and use the same clean names.

## Alternatives considered

Adding `locality_status` and `profile_status` beside Phase 4 top-level fields was rejected because
it duplicates the assessment envelope. Encoding coverage in locality status names was rejected
because the axes are orthogonal.

Keeping `profile_id` as a permanent alias was rejected. Compatibility aliases may exist only on
the legacy API during migration and are removed from the active public surface in Phase 5H.

## Revisit when

The product accepts typed applicant or household context. The existing profile assessment object
can then move from explicit non-evaluation to evaluated dimensions without changing preference
preset semantics.
