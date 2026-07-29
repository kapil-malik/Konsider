# Locality-to-country scoring policy

Status: implemented with synthetic schema-5 fixtures

Production locality source onboarded: no

## Inputs

`aggregate_locality_criterion` consumes:

- one criterion with locality-derived scope;
- its exact aggregation policy and version;
- its exact locality universe and version;
- the canonical geographic entity registry;
- entity-neutral locality observations and scores;
- every declared source-lineage ID; and
- a deterministic release ID and attempt timestamp.

Only locality scores whose canonical entity is in the frozen universe are eligible. Entity type,
parent country, criterion, observation lineage, score range, and policy references must already
reconcile with the schema-5 release contracts.

## Supported selection methods

| Method | Deterministic behavior |
| --- | --- |
| `TOP_N_MEAN` | Select the highest canonical opportunity scores, ordered by descending score and stable entity ID. |
| `BOTTOM_N_MEAN` | Select the lowest canonical opportunity scores, ordered by ascending score and stable entity ID. |
| `ALL_VALID_MEAN` | Use every valid eligible locality, ordered by stable entity ID. |

Canonical scores are always higher-is-better even when the raw construct is lower-is-better. For
C66, lower heat exposure becomes a higher canonical opportunity score before top-N selection.

## Evidence rules

The executor groups universe members by canonical parent country and classifies locality inputs:

- stale flags (`STALE`, `SOURCE_STALE`) are excluded;
- invalid/rejected flags are excluded;
- scores outside the frozen universe are ignored and flagged;
- broken observation lineage or entity types are integrity errors, not missing values.

A country result is emitted only when the policy's evidence gate passes. Normalized non-result
reasons include:

- `NO_QUALIFYING_LOCALITY`;
- `NO_VALID_LOCALITY_SCORE`;
- `LOCALITY_INPUT_STALE`;
- `LOCALITY_INPUT_INVALID`;
- `SINGLE_LOCALITY_INSUFFICIENT`;
- `INSUFFICIENT_VALID_LOCALITIES`; and
- `AMBIGUOUS_BOUNDARY_TIE`.

No country score is fabricated for these outcomes.

## Small sets and ties

When valid locality count is below `N` but at least the declared minimum, the executor uses every
valid row and adds `FEWER_THAN_N_AVAILABLE`. A single row is allowed only under
`USE_AVAILABLE`; otherwise the country receives `SINGLE_LOCALITY_INSUFFICIENT`.

At an N-boundary tie:

- `STABLE_ENTITY_ID` selects deterministically by ID;
- `INCLUDE_ALL_AT_BOUNDARY` includes all equal boundary scores; and
- `FAIL_AMBIGUOUS` emits a rejected country outcome.

## Precision and lineage

Means use `Decimal` values constructed from serialized scores and `ROUND_HALF_EVEN` at
`score_precision` (0–8). The result observation, result score, and derived evidence use
deterministic IDs containing criterion, country, policy ID, and policy version.

Derived evidence retains:

- every selected locality;
- its observation IDs, score ID, and score;
- eligible and valid counts;
- result observation and score IDs;
- aggregation policy ID/version;
- input release;
- criterion lineage; and
- quality flags for incomplete, single, tied, ignored, stale, or invalid inputs.

All valid locality evidence remains in the release for later analysis, including rows outside the
country aggregation's selected top-N.
