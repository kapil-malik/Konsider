# Phase 7G stateless TFC API

Status: complete; owner acceptance required before Phase 7H

Date: 2026-08-05

## Decision

API v2 evolves additively. A new major version is unnecessary because omitted or empty TFC
selection uses the existing service path and omits every new response field. There is no account
lookup, login, saved profile, query-string context or inferred TFC selection.

The active schema-5.1 release remains the only ranking and Opportunity Filter source. The Phase 7F
release-6 candidate is loaded separately, validated against the active release ID/checksum and
accepted only while draft, non-synthetic and activation-unauthorized. Candidate failure affects
`GET /api/v2/tfcs` and explicitly selected TFC requests; legacy ranking remains available.

## Public contract

- `GET /api/v2/tfcs` exposes exactly the three first-wave checks, field definitions,
  sensitivity/retention hints, input requirements, limitations, source summaries, effective dates
  and filter capability.
- Ranking, comparison and country-details POST requests accept an optional `feasibility` object
  containing explicit IDs, mode and separate applicant, household and scenario layers.
- Responses expose response-level and per-country typed outcomes, required inputs, routes,
  conditions, source/effective dates, base/filtered ranks and sanitized snapshot metadata.
- The metric result union remains generated and serialization-tested; no metric TFC is falsely
  advertised in the route-only first wave.
- `REQUIRE_SUPPORTED_MATCH` is explicit but rejected for all current `ASSESS_ONLY` policies.

Evaluation occurs after canonical ranking, coverage/locality handling and Opportunity Filters.
Scores, weights, contributions, affinity, base order, PCC, LSC and OFC results are unchanged.

## Privacy

Profile context exists only in the request and in-process evaluation. It is not stored, logged,
returned, placed in URLs, metrics or immutable release artifacts. Validation and domain errors are
redacted. Every API v2 POST response is private/no-store. Public snapshot output contains only an
opaque context hash, IDs, versions, date and base-ranking reference.

## Verification

The Phase 7G suite covers all three production route checks, no-context and missing-input states,
unknown versus explicit absence, unsupported destinations, source/route serialization, the metric
response union, typed selection/taxonomy errors, ranking invariance, OFC/PCC/LSC composition,
comparison/details consistency, cache headers, legacy compatibility and unavailable-candidate
fallback. OpenAPI and generated TypeScript are regenerated from FastAPI rather than duplicated.

## Boundary before Phase 7H

Phase 7G does not activate release 6 or add UI, authentication, server persistence, saved profiles
or chat. Phase 7H may consume the catalog to build progressive guest forms and explicit local-only
retention. It must preserve explicit TFC selection and the server-stateless boundary.
