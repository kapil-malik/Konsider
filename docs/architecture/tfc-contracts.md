# Typed Feasibility Check contracts

Status: Phase 7C contracts accepted in code; runtime and evidence not implemented

## Boundary

Typed Feasibility Checks are applicant-context assessments and a sibling product role. They never
contribute to affinity, carry weights, enter complete-case ranking, aggregate locality evidence or
reuse Opportunity Filter states. The first-wave catalog contains exactly three inactive checks:

| ID | Public name | Criterion | Result family |
|---|---|---|---|
| `skilled_work_route_feasibility` | Highly qualified work route check | C32 | `RULE_ROUTE_MATCH` |
| `family_accompaniment_reunification` | Dependants on supported work and study routes | C36 | `RULE_ROUTE_MATCH` |
| `post_study_work_pathway` | Post-study stay and work route check | C35 | `RULE_ROUTE_MATCH` |

The definitions preserve the Phase 7B research boundary of 29 stable destinations. That is a
contract boundary, not onboarded production evidence. All definitions are `CONTRACT_ONLY`, inactive
and `ASSESSMENT_ONLY` in Phase 7C.

Binding decisions are recorded in [ADRs 011-018](decisions/011-tfcs-as-sibling-product-role.md).

## Schema generation

`contracts/schemas/v4` is the Phase 7 target-contract generation. It does not replace or weaken
schema generation 3. Active release `2026-08-04.1` remains release 5.1 and has no TFC binding.

Generation 4 defines:

- applicant, household, scenario and effective-context contracts;
- field privacy and requirement metadata;
- TFC definition and three-item catalog contracts;
- route/rule result and common outcome contracts;
- sibling profile/feasibility assessment placement;
- browser retention policy; and
- the standalone release-6 TFC binding.

It deliberately does not define a scenario-metric or advisory result. Adding either requires a new
owner-approved source gate and result schema.

## Common status

Every TFC outcome has exactly one execution status:

| Status | Meaning |
|---|---|
| `EVALUATED` | A typed route result was produced. |
| `INPUT_REQUIRED` | Required profile fields are missing; nothing was guessed. |
| `DESTINATION_EVIDENCE_INSUFFICIENT` | Source missingness, conflict or other evidence failure blocks a result. |
| `UNSUPPORTED` | The destination or declared profile is outside the frozen boundary. |
| `NOT_APPLICABLE` | The selected check does not apply to the declared scenario. |
| `EVALUATION_ERROR` | A technical failure occurred; never used for a policy or applicant result. |

The common status describes execution only. Substantive route meaning lives in
`tfc-route-result-1.0`.

## Route result

A route result identifies every supported route evaluated, matched route IDs, met, unmet, unknown
and blocking conditions, source assets, effective dates, checksums and caveats. Match classification
is one of:

- `SUPPORTED_ROUTE_MATCH`;
- `CONDITIONAL_ROUTE_MATCH`; or
- `NO_SUPPORTED_ROUTE_MATCH`.

Positive and conditional results require a matched evaluated-route identity. Conditional results
require at least one unmet or unknown condition. A no-match result requires an explicitly complete
frozen route inventory and the statement: “No supported-route match is not a permanent legal
impossibility.”

Phase 7B has not established complete inventories for the first wave. Their evaluation policy is
therefore positive/conditional only. The no-match fixture validates the guarded future contract
shape; it does not authorize that production outcome.

## Input requirements

Each definition declares every consumed field as:

- `ALWAYS_REQUIRED`;
- `CONDITIONALLY_REQUIRED`;
- `OPTIONAL_EXPLANATORY`; or
- `NOT_USED`.

Conditional inputs use a small inspectable vocabulary:

- destination rule requires field;
- another field equals a value;
- another field is present; or
- a household role is declared.

There is no general expression language. Missing required data produces `INPUT_REQUIRED` with exact
field IDs.

## Structured assessments

The future response placement is:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {},
    "opportunity": {},
    "feasibility": {}
  }
}
```

`assessments.profile` reports context presence, evaluated dimensions, snapshot hash and retention
state. `assessments.feasibility` reports selected TFCs, execution, required inputs, effective dates,
country outcomes and optional explicitly requested filtered position. Base rank stays unchanged.

The Phase 7C schema can represent `EXPLICIT_SUPPORTED_ROUTE_FILTER`, but approved definitions are
assessment-only. Enabling filtering requires an owner decision and later engine policy; it is not
implicit in route matching.

## Release extension

The draft `tfc-release-binding-1.0` targets a future additive/major `konsider-release-6.0` and binds
exactly six checksummed sibling artifacts:

1. TFC catalog;
2. destination route/rule evidence;
3. evaluation/effective-date policy bundles;
4. source and legal manifest;
5. coverage summary; and
6. validation report.

Release 6 must retain the full release-5.1 ranking and Opportunity Filter contract. Profile values
and outcomes are request-time data and are prohibited from immutable releases. Phase 7C defines
only the standalone binding; Phase 7D will implement a complete draft release-6 foundation. No
release is staged or activated here.

## Compatibility

Historical v1-v3 schemas are unchanged. Contract tests load the active release through the existing
repository, validate its generation-3 manifest and assert that the active OpenAPI document exposes
no TFC path or model. Current ranking, OFC, PCC, locality, API and UI behavior are unchanged.
