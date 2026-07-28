# ADR 005: Orthogonal criterion, coverage, scope, and applicability

Status: accepted for the Phase 5 target contract

## Context

Phase 4 classifies country-result coverage as global core, conditional complete case, or
diagnostic-only. Phase 5 adds evidence that may originate at a city, metro, region, or service
area. Future applicant and household context is a third concern.

Combining these concerns in one enum would create false restrictions. A locality-derived
criterion can have complete country coverage, and a national source can have incomplete coverage.
Likewise, locality relevance does not make a criterion universally applicable to every user.

Phase 5A retained research ID `C66` while narrowing its meaning from the historical
“Extreme-weather risk” label to the precise product construct “Extreme heat exposure.”

## Decision

A target criterion keeps core identity and interpretation fields at its root and owns three
separate objects:

- `coverage` answers whether Konsider can produce a valid country result;
- `scope` answers where the evidence came from and how it became a country result; and
- `applicability` answers whether the interpretation is universal, parameterized, or requires a
  future applicant/household profile.

Coverage and scope have no cross-axis enum. All semantically valid combinations are allowed,
including:

- global-core national-direct;
- conditional national-direct;
- global-core locality-derived; and
- conditional locality-derived.

The PCC activation threshold and locality-analysis threshold are distinct fields. They remain
distinct even when both initially equal raw weight `0.6`.

`C66` remains the criterion ID. Its canonical target name is `Extreme heat exposure`, and
`Extreme-weather risk` is retained in `historical_names`. Because C66 has never been published as
a runtime criterion, this is a pre-publication construct refinement rather than mutation of an
immutable public contract. Once C66 is published, its narrowed meaning is frozen.

## Consequences

- Coverage and locality behavior can evolve independently.
- A missing locality-derived country result uses normal coverage outcomes; locality status names
  do not encode FCC/PCC state.
- Profile-dependent criteria cannot masquerade as universal locality scores.
- Catalog consumers must read all three objects rather than infer scope or applicability from
  coverage.

## Alternatives considered

A single combined readiness/scope enum was rejected because it produces invalid coupling and an
unmanageable state space. Treating all locality-derived criteria as PCCs was rejected because
coverage is an observed property, not a geographic definition.

Assigning C66 a new runtime ID was rejected because no runtime/public C66 contract exists to
protect. The historical label remains explicit so the narrowing is auditable.

## Revisit when

A published criterion must change its core construct. That change requires a new criterion ID or
an explicit versioned semantic-migration policy; it must not be handled by silently changing the
name.
