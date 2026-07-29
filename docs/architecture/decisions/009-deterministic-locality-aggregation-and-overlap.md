# ADR 009: Deterministic locality aggregation and overlap semantics

Status: accepted

Date: 2026-07-28

## Context

Phase 5C can package locality observations, locality scores, derived country results, and their
policies. Phase 5D must execute those policies and assess whether active locality criteria can be
satisfied in a common place without allowing that advice to alter country coverage or affinity.

The target status list includes both common locality and partial overlap. Those terms need precise,
criterion-count-independent definitions.

## Decision

Country derivation executes the versioned aggregation policy rather than criterion-specific code.
The first executor supports `TOP_N_MEAN`, `BOTTOM_N_MEAN`, and `ALL_VALID_MEAN`. Canonical locality
scores are already oriented so higher is better; therefore top-N operates on normalized opportunity
scores, not raw-source direction.

Selection order is score followed by stable entity ID. A policy chooses one of three boundary-tie
behaviors: stable entity ID, include every boundary tie, or reject the ambiguous result. Means use
decimal arithmetic and half-even rounding at the policy's declared precision. One-locality and
minimum-valid-locality behavior remain policy fields.

Locality analysis uses all valid locality scores in the frozen universe, never only the top-N rows
that produced country scores.

For one country and two or more active locality criteria:

- `COMMON_LOCALITY_AVAILABLE` means the intersection of every active criterion's valid locality set
  is non-empty;
- `PARTIAL_OVERLAP` means the all-criterion intersection is empty but at least one criterion pair
  has a non-empty intersection;
- `NO_COMMON_LOCALITY` means every pairwise intersection is empty; and
- `INSUFFICIENT_LOCALITY_EVIDENCE` means at least one active criterion has no valid locality set.

This strict definition means country-level `PARTIAL_OVERLAP` is distinct only with three or more
active criteria. With exactly two criteria, a shared valid locality is necessarily common to all,
otherwise there is no common locality. For two criteria with different results across countries,
the response-level status is `MIXED_COUNTRY_RESULTS`; the engine does not manufacture a third
set-theoretic state.

The best common locality maximizes the weighted mean of its canonical locality scores across the
active locality criteria. It uses the same criterion weights as country ranking, renormalized only
within the locality comparison. Stable entity ID breaks equal-score ties. This advisory comparison
does not replace any independently derived country score.

## Consequences

- Software and medical opportunity can contribute independently to one country's score even when
  they derive from different cities.
- A common locality outside a criterion's displayed top-N contributors is still discovered.
- Partial or absent overlap never excludes a country, changes coverage activation, renormalizes the
  country vector, or changes a country total.
- Future spatial containment or travel-time overlap would require an explicit versioned relation
  model. It must not silently redefine entity-ID intersection.

## Alternatives considered

Comparing only top-N contributors was rejected because it hides valid common localities. Treating
non-identical two-criterion sets as partial was rejected because they may still contain a locality
valid for both criteria. Penalizing the country score for no overlap was rejected because Phase 5
defines independent country opportunity and advisory locality coherence.

## Revisit when

A future profile engine introduces `PREFERRED` or `REQUIRED` co-location constraints, or a
versioned geographic-relation model supports containment and travel-time equivalence between
different locality entity types.
