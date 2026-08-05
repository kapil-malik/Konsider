# Phase 7D generic TFC release foundation report

Status: complete; acceptance required before Phase 7E

Date: 2026-08-05

## Outcome

Phase 7D implements a generic, draft-only production path for destination-side TFC sources, rules,
policies and immutable release artifacts. No approved first-wave source data was onboarded. The
only capture is visibly fictional and expands deterministically to an explicit synthetic
two-TFC-by-91-country support matrix.

## Schema and release changes

Generation 4 now includes bounded release catalog, source/legal manifest, rule/evidence union,
policy bundle, coverage, validation, semantic diff and release-6 candidate manifest schemas.
`konsider-release-6.0` binds the unchanged `2026-08-04.1` release-5.1 checksum plus the six TFC
artifacts. The repository exposes write, load and replay only; it cannot publish or activate.

The active pointer, current loader, OpenAPI, ranking, PCC/LSC, locality and Opportunity Filter
artifacts are unchanged. Historical releases remain inspectable through their existing loaders.

## Synthetic artifact inventory

- two synthetic catalog definitions: one route/rule and one scenario metric;
- 91 canonical country jurisdictions plus one fictional regional jurisdiction;
- 182 explicit support records, exactly one per TFC-country pair;
- two national routes, one regional override, one unresolved-conflict route and one stale route;
- one typed metric formula with two unit-bearing components;
- three fictional source/legal registrations;
- two evaluation policies, coverage summary and reproducible validation report; and
- one release-6 manifest with six artifact checksums and an immutable base-release checksum.

The scenario metric proves only the generic artifact family required by Phase 7D. The approved
first wave remains the three route/rule TFCs from Phase 7C.

## Validation and review

Validation covers source manifests, typed records, unique identities, non-overlapping effective
periods, jurisdiction parentage, exact country support, selected-rule dates, staleness, conflict
blocking, source and policy bindings, coverage reconciliation, prohibited profile/ranking/OFC
fields and legacy release compatibility.

Semantic diff emits five explicit categories: source input, normalized rule, effective date,
evaluation policy and support state. Stable JSON/JSONL serialization uses sorted identities and LF
line endings. Offline replay compares all six artifacts and the manifest byte-for-byte.

## Commands

Build, replay and diff use `scripts/build_phase7d_tfc_foundation.py`; the production implementation
lives in `konsider.ingestion.tfc_release` and `konsider.ingestion.tfc_sources`. Online acquisition is
worker-only through an injected fetcher. API runtime has no live network path.

## Verification

- focused Phase 7D suite: 17 passed;
- complete backend unit suite: 285 passed;
- Ruff: passed;
- documented synthetic CLI build: passed; and
- offline replay: `PASSED`, zero mismatched files across six artifacts plus the manifest.

Changed paths are limited to generation-4 schemas, the TFC ingestion modules and command wrapper,
fictional Phase 7D fixtures/tests, and TFC architecture, operations, release, glossary, roadmap and
history documentation. No active release, OpenAPI, API, frontend or ranking-domain file changed.

## Boundary before Phase 7E

There is no technical blocker after owner acceptance of Phase 7D. Phase 7E must:

- use synthetic or staged test data only;
- keep the three approved first-wave definitions route-only and assessment-only by default;
- evaluate effective profile snapshots at request time rather than storing outcomes;
- preserve ranking, locality, PCC/LSC and Opportunity Filter behavior; and
- leave production evidence onboarding to Phase 7F.
