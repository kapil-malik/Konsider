# ADR 006: Canonical geographic subjects and replayable derived lineage

Status: accepted for the Phase 5 target contract

## Context

The current observation and score contracts identify a country with `country_code` and assume one
registered source per criterion. Locality-derived scoring needs canonical cities, metros, regions,
and service areas; multiple input sources; locality-level observations and scores; and replayable
country derivation.

Free-text locality labels are not stable identifiers. Overloading `country_code` with a locality ID
would make validation ambiguous. Collapsing several sources into one synthetic source string would
lose licensing, version, and transform lineage.

## Decision

Phase 5 generalizes observations and scores to an entity-neutral geographic subject:

```json
{
  "subject": {
    "entity_id": "ghsl-uc:10737",
    "entity_type": "CITY"
  }
}
```

Countries are canonical entities such as `country:CAN`; localities have their own namespaced IDs.
Every entity declares type, display name, country parentage, aliases, and exact source mappings.
References carry only canonical ID and type. Display names never function as joins.

A versioned locality universe freezes selection independently of criterion values. A separate
versioned aggregation policy identifies:

- source and result criteria;
- locality universe and type;
- aggregation method and `N`;
- minimum valid localities;
- score range;
- tie handling;
- one-locality behavior; and
- required source-lineage roles.

Derived country evidence records the exact policy version, input release, contributing locality
references, observation IDs, locality score IDs and values, result score, quality flags, and one
criterion source-lineage ID.

Source lineage is a first-class graph-like record. Each source input has an ID, role, version,
exact asset URI, checksum when redistributable, and licence ID. Ordered transform steps identify
their inputs, version, and output. No opaque composite source string is valid.

## Consequences

- Country and locality observations can use one generic ingestion and validation path.
- Existing `country_code` rows remain immutable historical artifacts and are adapted only when
  loaded internally.
- Cross-border entities can later declare multiple country parents without changing observation
  identity. Phase 5's v1 locality universe continues assigning each urban centre to its source
  parent country.
- Full locality evidence remains inspectable even when only top-N inputs contribute to the country
  result.
- Replay and licensing audits can follow every source and transform independently.

## Alternatives considered

Separate country and locality observation types were rejected because they would duplicate units,
periods, scoring, validation, and lineage logic. A union wrapper around legacy rows was rejected
as the final target because it would preserve two sources of truth.

Embedding aggregation rules directly in criterion-specific code was rejected. The engine will
execute versioned policies, including but not limited to top-two averages.

## Revisit when

Non-geographic subjects such as institutions become active product entities. They may extend the
canonical subject model, but must not weaken geographic type and parentage validation.
