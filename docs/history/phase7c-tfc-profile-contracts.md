# Phase 7C TFC and profile contract report

Status: complete; owner decisions required before Phase 7D

Date: 2026-08-05

## Outcome

Phase 7C defines contracts, ADRs, schemas and visibly fictional synthetic fixtures for the three
owner-approved first-wave checks. It does not onboard evidence, stage or activate a release, expose
API fields, add UI, persist profiles or change ranking.

Chosen terminology is `ApplicantProfile`, `HouseholdProfile`, `ExplorationScenario`,
`EffectiveProfileContext`, `TypedFeasibilityCheck`, `TFCOutcome`, `TfcCommonStatus` and
`RouteRuleResult`. TFCs are sibling assessments, not criteria or Opportunity Filters.

## Approved first wave

- Highly qualified work route check (`skilled_work_route_feasibility`, C32)
- Dependants on supported work and study routes (`family_accompaniment_reunification`, C36)
- Post-study stay and work route check (`post_study_work_pathway`, C35)

All use `RULE_ROUTE_MATCH`, retain the Phase 7B 29-destination research boundary and remain inactive
`CONTRACT_ONLY` definitions.

## Version decisions

- Contract schema generation: `contracts/schemas/v4`
- Applicant profile: `applicant-profile-1.0`
- Household profile: `household-profile-1.0`
- Exploration scenario: `exploration-scenario-1.0`
- Effective context: `effective-profile-context-1.0`
- TFC catalog/definition/outcome: version 1.0
- Typed result: `tfc-route-result-1.0` only
- Retention policy: `profile-retention-policy-1.0`
- Redacted profile export: `profile-export-1.0`
- Draft release binding: `tfc-release-binding-1.0`, targeting future release 6.0

Generation 3 and active release 5.1 remain unchanged. Phase 7D must design the complete release-6
foundation around the standalone binding; Phase 7C does not alter the production loader.

## Exact statuses and result types

Common statuses are `EVALUATED`, `INPUT_REQUIRED`, `DESTINATION_EVIDENCE_INSUFFICIENT`,
`UNSUPPORTED`, `NOT_APPLICABLE` and technical-only `EVALUATION_ERROR`.

Route classifications are `SUPPORTED_ROUTE_MATCH`, `CONDITIONAL_ROUTE_MATCH` and guarded
`NO_SUPPORTED_ROUTE_MATCH`. The final state validates only with a complete frozen inventory and a
permanent-impossibility disclaimer. First-wave policy remains positive/conditional only.

No scenario metric or advisory result schema exists. The required scenario-metric synthetic case
is represented as an intentional invalid fixture, proving that mixed result families cannot enter
the route-only contract accidentally.

## Privacy decisions

- age in years by default; exact birth date exception-only;
- explicit unknowns and field-level provenance;
- no names, passport numbers, employer identity or account lookup;
- server persistence `NONE`;
- tab memory by default;
- same-device storage only after explicit consent, maximum 30 days;
- exact birth date never device-retained;
- profile values prohibited in URL, logs, analytics and releases; and
- user-initiated, redacted-by-default export plus clear/delete without an account.

## Assessment and filtering

`assessments.profile` owns context and retention summaries. `assessments.feasibility` owns TFC
execution and country outcomes. Ranking, coverage, locality and Opportunity Filter assessments stay
independent.

The schema can represent explicit feasibility filtering for a later approved policy, and a
synthetic fixture validates the shape. All approved definitions are `ASSESSMENT_ONLY`; no filtering
behavior is enabled in Phase 7C.

## Compatibility

Contract tests validate every generation-4 schema, valid and invalid fixtures, exact enum sets,
snapshot hashing, no-match completeness, source/effective metadata, privacy retention, release
binding and multi-TFC assessment reconciliation. They also load active release `2026-08-04.1`
through the existing repository, validate its generation-3 manifest and confirm that current
OpenAPI exposes no TFC path or model.

## Owner decisions before Phase 7D

1. Confirm the three definitions remain assessment-only, or explicitly authorize supported-route
   post-ranking filtering for one or more checks.
2. Confirm the 30-day maximum for optional consented same-device retention.
3. Accept release 6.0 as the future additive/major TFC binding target.
4. Confirm positive/conditional-only first-wave policy until route inventory completeness is proven.

Do not begin production evidence onboarding. Phase 7F remains the first-wave evidence phase.
