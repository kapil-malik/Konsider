# Phase 5D verification report

Status: implementation complete

Date: 2026-07-28

Scope: synthetic locality aggregation, country ranking, and structured coverage/locality/profile
assessments

Production sources, active release, API, UI, and production C66 scoring changed: no

## Delivered

Phase 5D adds three domain components:

- `locality_aggregation.py`: criterion-neutral execution of versioned locality aggregation
  policies;
- `locality_models.py`: typed aggregation, coverage, locality, profile, contribution, ranking, and
  reason outputs; and
- `phase5_ranking.py`: schema-5 complete-case ranking with orthogonal assessments.

The implementation consumes the immutable schema-5 release foundation from Phase 5C. It does not
add a production source, activate a release, alter `/api/v1`, or expose API v2; transport remains
Phase 5E.

## Contract refinements

Implementation added the previously implicit aggregation `score_precision` field. Derived evidence
quality flags now cover fewer-than-N, included ties, outside-universe inputs, and stale/invalid
inputs. The target ranking response now carries:

- contributing, triggered, and below-threshold locality criterion IDs;
- a per-criterion threshold map;
- contribution provenance;
- per-criterion locality inventories;
- deterministic best-common locality; and
- excluded-country locality assessments.

These are clean schema-5/API-v2 target changes. No active contract changed.

## Golden scenarios

Synthetic tests cover:

1. national FCC only;
2. one FCC LSC below the locality threshold;
3. one FCC LSC at the threshold;
4. a PCC LSC below coverage activation;
5. an active PCC LSC with a missing country;
6. two LSCs with the same leading locality;
7. a common locality outside both displayed top-N selections;
8. two LSCs producing mixed common/no-common results across countries;
9. two LSCs with no overlap;
10. three LSCs with one complete common locality;
11. three LSCs with pairwise but no three-way overlap;
12. one qualifying locality under both allow and reject policies;
13. insufficient, stale, and invalid locality evidence;
14. coverage exclusion with an independent locality warning; and
15. boundary ties, weighted best-common ties, and score precision.

Under the strict set definition in ADR 009, country-level partial overlap cannot exist for exactly
two criteria: their intersection is either common to both or empty. The two-criterion mixed
scenario is represented by response status `MIXED_COUNTRY_RESULTS`; country-level
`PARTIAL_OVERLAP` is verified with three pairwise-overlapping criteria.

## Invariants proved

- Changing common-locality status without changing selected country inputs leaves the country total
  unchanged.
- Every country contribution uses the same normalized vector.
- A country missing any active result is excluded; no partial total is emitted.
- PCC and locality thresholds are evaluated independently.
- Coverage fallback deactivates the PCC without creating locality advice from an inactive
  criterion.
- Full valid locality sets, not top-N contributors, drive common-locality analysis.
- Best-common selection uses relevant weights and stable entity-ID ties.
- Contribution observation, score, and derived-evidence IDs reconcile with the loaded release.
- Repeated ranking produces byte-equivalent dictionaries and stable order.
- Profile fields remain contract-invalid and profile assessment is explicitly unevaluated.

## Remaining gates

Phase 5G still owns C66 source semantics, its production score transform, sensitivity analysis,
licensing, and onboarding. Phase 5E owns transport and generated API types. Phase 5D makes no claim
that the synthetic aggregation policy is approved for C66 production.

## Final verification

| Command | Result |
| --- | --- |
| `python -m pytest tests/unit/domain/test_phase5d_locality_engine.py tests/unit/test_phase5b_contracts.py tests/unit/ingestion/test_phase5c_current_release.py -q` | 73 passed |
| `python -m pytest -q` | 262 passed |
| `python -m ruff check .` | All checks passed |
| `python -m black --check .` | 101 files unchanged |
