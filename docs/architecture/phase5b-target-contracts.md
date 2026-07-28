# Phase 5B target architecture and contracts

Status: complete

Date: 2026-07-28

Scope: ADRs, target schemas, synthetic contract fixtures, and migration design only

Runtime, API behavior, UI behavior, contracts in active use, and active release changed: no

## Outcome

Phase 5B defines a clean major-version target for locality-aware criteria without weakening Phase
4 coverage guarantees.

The design proves the central independence rule:

- an FCC can be locality-derived;
- a PCC can be locality-derived;
- an FCC can be national-direct; and
- a PCC can be national-direct.

Coverage answers whether a valid country result exists. Scope answers where that result came from.
Applicability answers whether the result is meaningful without future applicant or household
context. None is inferred from another.

The first-wave criterion keeps ID `C66`. Its canonical target name is **Extreme heat exposure**,
and `Extreme-weather risk` is retained as its historical research name. The new construct is
explicitly narrower: it does not claim to measure broad weather or disaster risk.

## Accepted decisions

Three ADRs own the Phase 5B decisions:

- [ADR 005](decisions/005-orthogonal-criterion-geography.md) separates criterion core, coverage,
  scope, and applicability and records the C66 identity decision.
- [ADR 006](decisions/006-canonical-geography-and-derived-lineage.md) selects entity-neutral
  observations/scores, canonical geographic entities, versioned locality policies, and explicit
  multiple-source lineage.
- [ADR 007](decisions/007-structured-assessments-and-preference-presets.md) defines structured
  response assessments and reserves profile terminology for real applicant/household context.

## Target versions

| Surface | Current active | Phase 5 target | Reason for major |
| --- | --- | --- | --- |
| Immutable release | `konsider-release-4.0` | `konsider-release-5.0` | Adds canonical entities, entity-neutral observations/scores, locality policy artifacts, multiple-source lineage, and derived evidence. |
| Consumer catalog | `consumer-catalog-2.0` | `consumer-catalog-3.0` | Adds orthogonal scope/applicability, geographic entities, locality policies, and renames weight profiles. |
| HTTP API | `/api/v1`, current OpenAPI | `/api/v2`, `konsider-api-2.0` | Restructures assessments and renames request/response fields without duplicate aliases. |
| Generated TypeScript | current OpenAPI-generated surface | `konsider-api-types-2.0` generated from API v2 | The frontend must consume the same major response shape; handwritten compatibility types are not allowed. |

The `contracts/schemas/v3` directory is schema-generation 3. It contains release major 5 and
catalog major 3; the directory number is not the release major.

## Criterion representation

Core identity, interpretation, scoring, caveat, readiness, and experimental fields remain at the
criterion root. Three objects are orthogonal:

```json
{
  "coverage": {
    "mode": "CONDITIONAL_COMPLETE_CASE",
    "activation_threshold": 0.6
  },
  "scope": {
    "evidence_level": "LOCALITY",
    "result_level": "COUNTRY",
    "locality_type": "CITY",
    "derivation": "AGGREGATED_FROM_LOCALITIES",
    "locality_universe_id": "major-urban-opportunity-v1",
    "aggregation_policy_id": "c66-extreme-heat-top2",
    "locality_analysis_threshold": 0.6
  },
  "applicability": {
    "mode": "UNIVERSAL",
    "dimensions": []
  }
}
```

The two `0.6` values have different owners:

- `coverage.activation_threshold` decides whether a PCC enters complete-case ranking; and
- `scope.locality_analysis_threshold` decides whether an LSC enters prominent locality-coherence
  analysis.

An FCC LSC has a null coverage activation threshold but may still have locality threshold `0.6`.
An active PCC LSC must independently satisfy both rules.

The fixtures include one synthetic `GLOBAL_CORE` locality-derived criterion and C66 as a
`CONDITIONAL_COMPLETE_CASE` locality-derived criterion.

## C66 target definition

| Field | Phase 5B target |
| --- | --- |
| ID | `C66` |
| Canonical name | Extreme heat exposure |
| Historical name | Extreme-weather risk |
| Evidence level | locality |
| Locality type | city / GHSL urban centre |
| Country result | aggregated from localities |
| Expected coverage | PCC, currently measured at 89/91 |
| Applicability | universal |
| Locality-analysis threshold | raw weight `0.6` |
| Production status | not ready; no source data onboarded |

The schema and fixture preserve the JRC day-count/pixel-count clarification as a production
onboarding caveat. Phase 5B does not resolve the source semantics, freeze the score transform, or
approve the illustrative top-two policy for production.

## Canonical geography

A geographic entity has:

- a stable namespaced `entity_id`;
- `COUNTRY`, `CITY`, `METRO`, `REGION`, or `SERVICE_AREA` type;
- display name;
- one or more country-parent codes;
- aliases; and
- exact source mappings with source version and source entity ID.

Observations and scores carry:

```json
{
  "subject": {
    "entity_id": "ghsl-uc:10737",
    "entity_type": "CITY"
  }
}
```

They do not put locality IDs into `country_code`. Country observations use a country entity
reference, so Phase 5C can build one generic path. Historical release-3/4 rows retain their
original `country_code` bytes and are adapted only inside historical loaders.

## Locality universe and aggregation

`locality-universe.schema.json` freezes:

- source lineage and version;
- locality type;
- population eligibility;
- per-country cap;
- ordering and tie-breakers;
- independence from criterion values;
- small/no-locality behavior;
- cross-border treatment; and
- exact entity inventory.

The target Phase 5A direction is `major-urban-opportunity-v1`: quality-controlled GHSL urban
centres, minimum population 50,000, at most five per country, ordered by frozen 2025 population and
stable source ID before criterion values are observed.

`locality-aggregation-policy.schema.json` owns top-N or all-valid behavior. It carries policy and
universe versions, source/result criteria, `N`, minimum valid localities, score range, tie handling,
one-locality handling, and required lineage roles. Domain logic must not hard-code a universal
top-two average.

The C66 fixture illustrates `TOP_N_MEAN` over the two highest normalized locality scores. It is a
contract example, not the Phase 5G sensitivity decision.

## Derived evidence and multiple-source lineage

A derived country evidence row exposes:

- result criterion and canonical country;
- `AGGREGATED_FROM_LOCALITIES`;
- exact aggregation policy ID/version;
- input release;
- every contributing locality;
- locality observation and score IDs plus input score;
- eligible and valid locality counts;
- derived result score;
- quality flags; and
- criterion source-lineage ID.

`source-lineage.schema.json` replaces the one-source assumption with a list of typed source inputs
and ordered transforms. Source roles distinguish primary observation, entity universe, boundary,
auxiliary, and scoring inputs. Each input retains exact version, asset URI, checksum when
available, and licence ID. A composite free-text source is invalid.

## Structured assessments

The API v2 target has one response-level source of truth:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {}
  },
  "rankings": [
    {
      "assessments": {
        "locality": {},
        "profile": {}
      }
    }
  ]
}
```

### Field ownership

| Location | Owns |
| --- | --- |
| Response coverage | Active FCC/PCC sets, coverage policy, excluded countries, complete-case/fallback status, coverage reasons. |
| Response locality | Active LSCs, LSCs crossing Medium, analysis threshold, policy IDs, request-wide summary. |
| Response profile | Whether applicant/household context existed and dimensions evaluated. |
| Country locality | Eligible, valid, contributing, and common locality IDs; overlap/evidence status and reasons. |
| Country profile | Future evaluated suitability; explicitly unevaluated in Phase 5. |

Country rows do not repeat ranking-universe coverage status. Coverage state never appears in a
locality status name.

Structured reasons contain:

- stable code;
- `INFO`, `WARNING`, or `BLOCKER` severity; and
- `NONE`, `ADVISORY`, `COUNTRY_EXCLUDED`, `RANKING_FALLBACK`, or `NOT_EVALUATED` effect.

Phase 5 emits `NO_PROFILE_CONTEXT` or `NOT_EVALUATED`. It does not manufacture a profile.

## Preference presets

Catalog weight presets become `preference_presets`. API v2 accepts
`preference_preset_id` and returns `resolved_preference_preset_id`. The clean schemas reject
`profiles`, `profile_id`, and duplicate profile aliases.

This is terminology migration only. It does not introduce applicant, occupation, household, visa,
or licensing inputs.

## Contract inventory

The target schemas are under [`contracts/schemas/v3`](../../contracts/schemas/v3/README.md):

| Schema | Responsibility |
| --- | --- |
| `criterion-definition` | Root/core fields plus orthogonal coverage, scope, and applicability. |
| `geographic-entity` | Canonical country/locality IDs, type, parentage, aliases, and mappings. |
| `geographic-observation` | Entity-neutral raw observation. |
| `geographic-score` | Entity-neutral normalized score. |
| `criterion-outcome` | Explicit valid/missing/stale/invalid/rejected country outcome with direct or derived evidence kind. |
| `source-lineage` | Multiple exact source inputs and replayable transforms. |
| `locality-universe` | Frozen independent locality inventory and selection. |
| `locality-aggregation-policy` | Versioned locality-to-country scoring policy. |
| `derived-country-evidence` | Contributing locality inputs and replay lineage. |
| `consumer-catalog` | Catalog 3 criteria, entities, policies, and preference presets. |
| `release-manifest` | Release 5 artifact inventory and checksums. |
| `validation-report` | Coverage, lineage, policy, and artifact-count validation results. |
| `ranking-request` | API v2 weights or preference-preset selection. |
| `ranking-response` | Final structured assessment envelope. |

## Migration plan

| Phase | Migration action | Temporary compatibility |
| --- | --- | --- |
| 5B | Publish target schemas, ADRs, and synthetic fixtures only. | None in active runtime. |
| 5C | Add release-5 writer/loader and entity-neutral internal records. Keep release-3/4 loaders for audit and replay. | Internal adapters may translate historical country rows to entity references; historical bytes never change. |
| 5D | Add policy-driven locality aggregation and structured domain assessments. | Current API continues using Phase 4 service behavior. |
| 5E | Introduce `/api/v2` with only clean fields and generate API v2 OpenAPI/types. Keep `/api/v1` temporarily unchanged. | `/api/v1` retains `profiles`, `profile_id`, `resolved_profile_id`, and Phase 4 top-level coverage fields. API v2 never exposes aliases. |
| 5F | Move the UI to `/api/v2` and generated API v2 TypeScript types. | No UI-side scoring or assessment translation. |
| 5G | If C66 clears every gate, publish one immutable release-5/catalog-3 additive release. | Active release remains schema 4 until a validated schema-5 release exists. |
| 5H | Remove legacy public aliases/routes and all internal active-path translation. | Historical release-3/4/catalog-1/2 loaders remain for inspection and replay only. |

If C66 is held in Phase 5G, Phase 5H must still migrate the active dataset through a replayed,
packaging-only release-5/catalog-3 release before retiring the legacy public surface. Synthetic
fixtures can never activate that migration.

The active release `2026-07-28.2` remains unchanged in Phase 5B.

## Synthetic verification

Valid fixtures cover:

- FCC + locality-derived scope;
- PCC + locality-derived scope;
- C66 identity and historical name;
- canonical country and city entities;
- entity-neutral observations and scores;
- frozen locality universe and aggregation policy;
- multiple source inputs;
- replayable derived country evidence;
- preference-preset request/catalog naming;
- release-5 manifest; and
- response/country assessment envelopes.

Invalid fixtures reject:

- direct derivation carrying locality-only policy fields;
- free-text observation subjects;
- opaque source-lineage strings;
- derived evidence without typed lineage;
- legacy `profile_id`;
- duplicate top-level locality status; and
- locality status names contaminated with coverage state.

## Validation results

Run from the repository root on 2026-07-28:

| Command | Result |
| --- | --- |
| `python -m pytest tests/unit/test_phase5b_contracts.py -q` | 37 passed |
| `python -m pytest -q` | 226 passed |
| `python -m ruff check .` | All checks passed |
| `python -m black --check .` | 95 files unchanged |

The contract tests validate all Draft 2020-12 schemas, accept every valid fixture, reject every
invalid fixture, exercise all four coverage/scope combinations, reconcile coverage metadata, and
verify C66 identity, canonical references, independent universe lineage, derived evidence,
multiple-source lineage, preference naming, and assessment ownership.

## Open decisions and blockers

No product clarification or technical blocker prevents Phase 5B closure.

Later gates remain intentionally unresolved:

- Phase 5C must choose physical artifact partitioning and validate release-size/replay behavior.
- Phase 5D must freeze locality overlap algorithms and tie behavior in executable domain policy.
- Phase 5G must resolve C66 source semantics, score transform, and top-N sensitivity before
  production onboarding.

These are owned by their later phases and do not weaken the Phase 5B target contract.
