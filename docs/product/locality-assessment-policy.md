# Locality assessment policy

Status: implemented with synthetic schema-5 fixtures

Policy version: `locality-assessment-policy-1.0`

## Independent activation axes

A locality-derived criterion contributes to country affinity when it is ready, has positive raw
weight, and is active under its independent coverage policy.

It participates in prominent locality analysis only when its raw weight also meets its own
`locality_analysis_threshold`.

Consequently:

- an FCC LSC below the locality threshold still contributes to country affinity;
- a PCC LSC must first activate under coverage;
- meeting the locality threshold cannot activate an otherwise inactive PCC; and
- coverage fallback removes a PCC from both final country contribution and locality analysis.

The response reports contributing criteria, analysis-triggered criteria, below-threshold criteria,
per-criterion thresholds, aggregation-policy IDs, and stable reasons.

## Country affinity

Each active criterion uses its independently produced country score. Every eligible country uses
one normalized criterion-weight vector. A country is ranked only when every active criterion has a
valid country result; the engine never renormalizes around a country's missing criterion and never
creates a partial aggregate.

Different contributing localities across criteria do not penalize the country. Locality coherence
is a separate advisory assessment.

## Common locality assessment

For every country, analysis loads all valid locality scores from each active criterion's frozen
universe. It does not use only displayed or top-N contributing rows.

Status semantics are fixed by
[ADR 009](../architecture/decisions/009-deterministic-locality-aggregation-and-overlap.md):

- no contributing locality criteria;
- contributing criteria below analysis threshold;
- one active locality criterion;
- a valid locality common to every active criterion;
- pairwise but not all-criterion overlap;
- no pairwise common locality;
- insufficient valid locality evidence; or
- mixed country-level results across the response.

The best common locality maximizes the weighted mean of relevant canonical locality scores. The
same ranking weights are used, normalized within the comparison only; stable entity ID breaks a
tie. This selection never changes the country aggregate.

## Assessment ownership

Coverage owns PCC activation, complete-case eligibility, country exclusion, and fallback.
Locality owns evidence inventories, contributing locality provenance, overlap, best-common
selection, and advisory reasons. Profile assessment explicitly returns `NO_PROFILE_CONTEXT`.

An excluded country still receives an internal locality assessment, so an evidence warning is not
lost or misclassified as coverage. The schema-5 domain result exposes excluded-country locality
assessments separately from ranked rows.

Reason severity (`INFO`, `WARNING`, `BLOCKER`) and effect (`NONE`, `ADVISORY`,
`COUNTRY_EXCLUDED`, `RANKING_FALLBACK`, `NOT_EVALUATED`) remain separate. No locality reason uses a
coverage exclusion effect.

## Future profile constraints

Phase 5D accepts no occupation, spouse, visa, age, citizenship, licensing, or co-location fields.
A future profile engine can add an explicitly typed co-location constraint:

- `PREFERRED`: retain independent country scoring and strengthen advisory ordering among common
  localities; or
- `REQUIRED`: apply a profile-owned eligibility rule after locality evidence exists.

That future rule must reference the same locality evidence and must not rewrite aggregation,
coverage, or source lineage.
