# Opportunity Filter contracts and staged architecture

Status: Phase 6G engine/API and Phase 6H UI complete against a staged candidate; publication pending

Date: 2026-08-03

Binding decision: [ADR 010](decisions/010-opportunity-filters-as-filter-only-contracts.md)

## Product boundary

Opportunity Filters restrict a previously computed ranked country list. They are not weighted
criteria and never contribute to affinity. `OFC` is internal shorthand, not user-facing copy.

Four dimensions remain independent:

| Dimension | Values owned here |
| --- | --- |
| Product role | `OPPORTUNITY_FILTER` rather than ordering criterion |
| Evidence coverage | complete, partial or unassessed on each country result |
| Geographic scope | country-direct, locality-derived or institution-derived country result |
| Applicability | destination-side, applicant-context-dependent or diagnostic-only |

FCC/PCC remain ordering-criterion coverage modes. LSC remains locality-derived scope. Neither is a
peer of OFC, and no combined enum is introduced.

## Contract versions

| Surface | Phase 6D contract | Active production |
| --- | --- | --- |
| Immutable release | optional `konsider-release-5.1` OFC binding | unchanged `konsider-release-5.0` |
| Ordering catalog | unchanged `consumer-catalog-3.0` | unchanged `consumer-catalog-3.0` |
| OFC catalog | `opportunity-filter-catalog-1.0` | optional Phase 6G staged bundle |
| OFC state | `opportunity-filter-state-1.0` | optional Phase 6G staged bundle |
| OFC evidence | `opportunity-filter-evidence-1.0` | optional Phase 6G staged bundle |
| OFC assessment | `opportunity-filter-assessment-1.0` | exposed when API bundle is configured |
| HTTP API | additive Opportunity Filter fields | `konsider-api-2.0` |

Schema generation remains `contracts/schemas/v3`. The directory number is not a release or catalog
major. Release 5.1 is additive and optional; it does not authorize the active pointer to select a
5.1 release.

## Definition contract

`OpportunityFilterDefinition` owns stable identity, public name, category, exact construct,
meaning, explicit limitations, filter-only role, strict behavior, policy/source versions, scope,
applicability, refresh, source dependency, availability, activation, sort order and documentation.

The schema prohibits undeclared fields, which excludes weight, score direction, normalization,
affinity contribution, PCC activation, imputation and ranking coefficients. The contracts-only
catalog may be empty. A catalog marked active must contain exactly nine active definitions.

## Public states and reasons

The public states are closed and versioned:

| State | Contract meaning | Strict-filter behavior |
| --- | --- | --- |
| `VERIFIED_STRONG_SIGNAL` | Complete approved evidence crosses at least one frozen strong route. | Pass |
| `STRONG_SIGNAL_NOT_ESTABLISHED` | Complete approved evidence was tested and no strong route passed. | Exclude with a non-negative explanation |
| `INSUFFICIENT_EVIDENCE` | Neither conclusion is defensible. | Exclude with a missing/incompatible-evidence explanation |

Stable reason codes are data. Presentation text is not. Positive reasons cover scale/share,
exceptional scale/specialization, skilled trades, construction, both routes, top-100 institution,
top-300 breadth and output/breadth. Complete below-threshold reasons cover scale, breadth and no
approved route. Insufficient reasons cover missing/stale sources, taxonomy/granularity/crosswalk
gaps, incompatible measures, legal blocks, source-universe absence, unresolved institution
identity, unavailable dependencies and unresolved conflicts.

A verified row must carry at least one evaluated, passing, establishing route. Not-established
requires complete evidence and no establishing route. Insufficient needs no numeric metrics and
cannot carry an establishing route. Skilled-trades/construction results retain exactly which route
or routes established the result.

## Confidence contract

Public confidence is `HIGH`, `MEDIUM` or `LOW`. The exact internal tier is retained separately:

- high: observed harmonised, observed national, or frozen research dataset;
- medium: modelled harmonised or official crosswalk; and
- low: supplemental.

The education tier `HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET` is the one source-aligned addition
required by the Phase 6C evidence. No finer education confidence taxonomy is invented.

## Typed evidence payloads

Every country row retains release/filter/country identity, state, confidence, completeness,
evaluated and establishing routes, reason codes, period, source references, observation status,
caveats, policy/source versions and deterministic build identity.

Metric payloads are versioned variants:

- `career-employment-metrics-1.0` owns employment scale/share and optional skilled-trades or
  construction components;
- `education-research-ecosystem-metrics-1.0` owns fractional publication output, institution
  breadth and top-100/200/300 counts; and
- `null` is valid for insufficient evidence.

These variants prevent unlike employment and institution metrics from being flattened into one
misleading numeric model.

## Runtime assessment

`OpportunityFilterAssessment` remains independent of coverage, locality, and profile assessments.
Phase 6G implements its typed Pydantic and OpenAPI transport without changing the ranking engine.

It owns:

- no filters, filters applied and no-match states;
- selected filter IDs and `ALL_SELECTED_REQUIRED` semantics;
- input, passing and excluded counts;
- response and per-filter exclusion counts by public state;
- one state per selected filter and country; and
- separate canonical `base_rank` and display `filtered_rank`.

With no filters, every country passes and filtered rank equals base rank. With filters, only rows
whose every selected state is verified pass. A zero-row result is valid. The service computes the
canonical full ranking before the indexed filter pass, preserves survivor score and order, then
applies selected-filter `top_k` with score-boundary ties. The legacy no-filter path keeps its exact
top-k slice for compatibility.

## Release 5.1 binding

A future release may declare six checksummed siblings:

1. `opportunity-filter-catalog.json`;
2. `opportunity-filter-evidence.jsonl`;
3. `opportunity-filter-source-manifest.json`;
4. `opportunity-filter-threshold-policies.json`;
5. `opportunity-filter-evidence-policy.json`; and
6. `opportunity-filter-coverage-summary.json`.

The manifest binds role, filename, schema version and checksum, and records definition/evidence
counts. The same files appear in `file_checksums`. Cross-artifact validation rejects duplicate
identities, policy/version mismatches, incomplete filter-country matrices, undeclared pairs,
binding/checksum disagreement and active catalogs with anything other than nine definitions.

Old release 5.0 manifests omit the OFC block and remain valid. No loader infers missing evidence
rows. A future active release must explicitly store all 819 states (nine filters × 91 countries),
including `INSUFFICIENT_EVIDENCE`.

## Adding an Opportunity Filter

Research approval is necessary but not sufficient. A production addition must:

1. freeze a source-aligned construct and public limitations;
2. add one catalog definition with no ranking fields;
3. register source/version, legal terms, attribution, retention and checksums;
4. freeze global evidence and threshold policies plus named routes;
5. generate exactly one explicit evidence row for every stable country;
6. validate state/reason/confidence/route consistency and source dependencies;
7. update coverage summaries and all six release artifact checksums;
8. build a new immutable release and verify deterministic replay;
9. test that canonical scores and survivor order are unchanged; and
10. obtain separate authorization before activation, API or UI exposure.

Research-history scripts may inform a production adapter but cannot be imported by the runtime.
Reusable logic must move into a tested production module with a versioned policy owner.

## Phase boundaries

- Phase 6D: contracts, synthetic fixtures, validators, ADR and documentation only.
- Phase 6E: five career evidence filters are onboarded in staged immutable fragment
  `phase6e-career-2026-08-03.1`; they remain inactive.
- Phase 6F: onboard four education filters and complete the nine-filter staged bundle.
- Phase 6G: strict AND evaluation and additive API transport complete against
  `phase6g-api-2026-08-03.1`; active ranking pointer unchanged.
- Phase 6H: UI controls and explanations complete against the staged nine-filter API candidate.
- Phase 6I: publish, activate, verify and close.

Phase 6G changes the API contract additively, but the default runtime has an empty Opportunity
Filter catalog unless a bundle is explicitly configured. Phase 6H does not change that default or
the active release pointer; publication remains gated by Phase 6I.
