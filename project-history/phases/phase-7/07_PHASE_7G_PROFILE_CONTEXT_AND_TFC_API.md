# Konsider Phase 7G — Stateless Profile Context and TFC API

## Dependency

Proceed only after Phase 7F has a valid staged candidate containing at least three production TFCs.

## Role

Work as the lead API-domain integration, OpenAPI, privacy-safe transport and generated-client engineer for Konsider.

## Objective

Expose additive, typed API v2 support for:

- profile context;
- household context;
- exploration scenario;
- selected TFCs;
- input requirements;
- TFC catalog;
- per-country feasibility outcomes;
- optional explicit supported-match filtering;
- scenario snapshot metadata.

Do not activate the final release or add UI.

## Compatibility principle

Existing clients that send no profile/TFC fields must receive semantically identical ranking, OFC, coverage and locality behavior.

Prefer additive API v2 evolution if clean and compatible.

Introduce a new major API only if current contracts cannot represent the change without ambiguity.

Document the decision.

## Request contract

Support explicit request fields conceptually equivalent to:

```json
{
  "preference_preset_id": null,
  "weights": {},
  "opportunity_filter_ids": [],
  "profile_context": {},
  "household_context": {},
  "scenario_context": {},
  "tfc_ids": [],
  "feasibility_mode": "ASSESS_ONLY"
}
```

Exact nesting may differ.

Rules:

- no hidden account lookup;
- omitted profile means no profile context;
- unknown values remain unknown;
- selected TFCs are explicit;
- scenario purpose may drive recommended TFCs but must not silently activate them unless the contract clearly reports resolved selection;
- no profile values in query strings.

Prefer POST for profile-bearing assessments.

## Catalog and input requirements

Expose:

- available TFCs;
- check kinds;
- public descriptions;
- limitations;
- supported profile/destination boundaries;
- required and conditional inputs;
- field definitions;
- sensitivity/retention hints;
- source/effective-date summary;
- filter capability;
- sort/group order.

The UI must derive forms and labels from the API/catalog where practical.

Do not expose internal legal notes or sensitive operational data.

## Response contract

Return:

- existing ranking payload;
- profile-context summary;
- selected/resolved TFCs;
- response-level feasibility assessment;
- per-country TFC outcomes;
- input-required details;
- matched route summaries;
- scenario metric results;
- source/effective dates;
- warnings/limitations;
- base rank;
- optional filtered rank;
- snapshot/policy versions.

Do not change affinity scores.

## Endpoints

Evaluate the smallest clean surface, such as:

- catalog endpoint includes TFC definitions and field registry;
- ranking endpoint accepts profile/TFC context;
- country details include TFC evidence/result for the current request;
- comparison endpoint accepts the same context;
- optional validation/requirements endpoint only if it materially improves progressive forms.

Avoid duplicating evaluation rules across endpoints.

## Privacy and logging

Ensure:

- request bodies are not logged;
- validation errors do not echo sensitive values;
- profile context is not included in URLs;
- caches do not cross-contaminate profile-specific responses;
- response cache policy is private/no-store where required;
- traces contain IDs and timings, not raw profile values;
- server does not persist profile requests;
- health/metrics do not expose profile content.

Review framework defaults and reverse-proxy behavior.

## Errors

Add stable typed errors for:

- invalid profile field;
- unsupported taxonomy version;
- selected TFC unavailable;
- input missing;
- unsupported feasibility mode;
- stale/unavailable TFC bundle;
- candidate release unavailable.

Input missing for a TFC should normally be a successful assessment outcome, not an HTTP failure.

## OpenAPI and generated client

Regenerate:

- OpenAPI;
- TypeScript client/types;
- fixtures;
- contract snapshots.

Do not hand-write duplicate frontend types.

## Tests

Add tests for:

- no-profile backward compatibility;
- profile request validation;
- unknown versus false/none;
- required input responses;
- route result serialization;
- metric result serialization;
- unsupported destination;
- multiple TFC kinds;
- explicit filter mode;
- base-rank invariance;
- OFC + TFC;
- PCC + LSC + TFC;
- country details/comparison consistency;
- no profile data in logs;
- no-store/private caching;
- generated client parity;
- staged candidate unavailable.

## Documentation

Update:

- API guide;
- OpenAPI examples using fictional profiles;
- privacy behavior;
- field registry;
- feasibility modes;
- result interpretation;
- migration/compatibility;
- no-login/no-persistence boundary.

## Explicit non-goals

Do not:

- activate release;
- add UI;
- persist profile data;
- add login;
- add saved profiles;
- add chat;
- change base ranking;
- infer TFC selection invisibly.

## Commit

Use a focused commit such as:

`feat: expose stateless TFC assessment API`

## Stop condition

Stop when API, OpenAPI, generated client and compatibility tests pass against the staged candidate.

Report:

- endpoint/request/response decisions;
- privacy controls;
- compatibility;
- tests;
- generated artifacts;
- files changed;
- commit SHA;
- blockers before Phase 7H.
