# Opportunity Filter engine

Status: Phase 6G complete against staged API candidate

Date: 2026-08-04

Opportunity Filters are a post-ranking restriction over destination-side evidence. They answer
whether a country has a verified strong signal for every selected construct. They do not estimate
an individual's job, licensing, visa, admission, or credential outcome and do not contribute to
country affinity.

## Evaluation pipeline

For each ranking, comparison, or detail request, the service:

1. runs the unchanged schema-5 ranking engine over the canonical release;
2. joins each canonically eligible country to the selected Opportunity Filter states;
3. retains a country only when every selected state is `VERIFIED_STRONG_SIGNAL`;
4. preserves canonical score, normalized weights, contributions, `base_rank`, and survivor order;
5. assigns contiguous `filtered_rank` values; and
6. applies `top_k` to the filtered list, including every score tie at the selected-filter boundary.

The no-filter path is an explicit compatibility path: it retains the established exact `top_k`
slice and returns `NO_FILTERS_ACTIVE`. An empty filtered result is valid and returns
`NO_COUNTRIES_MATCH`; the service never substitutes an unfiltered fallback.

Only `ALL_REQUIRED` is supported. Selected filter IDs are canonicalized into deterministic order.
Duplicates, unknown IDs, inactive IDs, and unsupported combination modes are rejected rather than
silently weakened. `STRONG_SIGNAL_NOT_ESTABLISHED` and `INSUFFICIENT_EVIDENCE` both exclude a
country, but remain distinct public explanations. Where multiple selected filters fail, all
filter-level evidence is retained. The response-wide exclusion category uses insufficient-evidence
precedence so the mutually exclusive aggregate counts reconcile to the excluded-country count.

## Isolation guarantees

The engine is a separate `OpportunityFilterService`, not a branch in the affinity calculator. It
never changes:

- FCC/PCC activation or conditional-coverage fallback;
- LSC aggregation, locality contributors, or locality assessment;
- profile applicability or `NO_PROFILE_CONTEXT` behavior;
- imputation, scoring direction, normalization, or weights;
- country eligibility in the canonical ranking; or
- affinity scores, criterion contributions, canonical ranks, or relative survivor order.

Comparisons retain the canonical score and base rank for a requested country excluded solely by an
Opportunity Filter and label it `opportunity_excluded`. Countries excluded by canonical coverage
remain canonically unavailable. Details and comparisons expose bounded evidence for selected
filters only; raw employment and publication metric payloads stay in the immutable evidence bundle.

## Loading and compatibility

The bundle loader validates checksums, schemas, definition identities, policy references, source
references, coverage summaries, and the exact definition-by-country matrix once at startup. It
then indexes definitions and evidence by ID. Request-time evaluation performs no file or source
I/O.

`KONSIDER_OPPORTUNITY_RELEASE_PATH` selects an immutable bundle directory independently of the
schema-5 ranking release. With no configured bundle, old release-5.0 deployments expose an empty
filter catalog and all existing no-filter requests continue to work. The Phase 6G integration
candidate is `data/reports/phase6g-2026-08-03/staged-release`, release
`phase6g-api-2026-08-03.1`, containing nine active definitions and 819 explicit evidence rows.
`data/releases/active.json` remains `2026-07-29.2`; publication is reserved for Phase 6I.

## API surfaces

- `GET /api/v2/opportunity-filters` returns definitions, coverage, source vintage, availability,
  activation, and explicit no-score-impact semantics.
- `POST /api/v2/rankings` returns response-wide and per-country Opportunity Filter assessments,
  canonical `base_rank`, and display `filtered_rank`.
- `POST /api/v2/comparisons` preserves requested-country context when a filter excludes it.
- `POST /api/v2/countries/{country_code}/details` returns selected-filter evidence summaries.

The OpenAPI contract remains versioned as `konsider-api-2.0`; Phase 6G fields and the catalog route
are additive. UI controls and presentation are Phase 6H work.

## Verification contract

Tests cover omitted/empty compatibility, all nine real definitions, strict AND behavior, every
public failure state, zero-match validity, deterministic ID ordering, top-k ties, PCC/LSC and
profile isolation, comparison/detail evidence, old-release behavior, inactive selections,
candidate replay, checksum validation, and indexed-request performance. The implementation report
records the exact gate results and measured timing.
