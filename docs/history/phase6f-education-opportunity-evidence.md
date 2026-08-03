# Phase 6F education Opportunity Filter evidence onboarding

Status: complete; staged only

Completed: 2026-08-03

Implementation commit: `<implementation-commit>`

## Outcome

Phase 6F productionizes the four approved education/research-university Opportunity Filters and
combines them with Phase 6E into a deterministic complete nine-filter candidate. The four
education filters contain exactly 364 country rows; the candidate contains exactly 819. All nine
definitions are inactive. Release activation, filtering engine, API, UI, and ranking behavior are
unchanged.

Candidate ID: `phase6f-complete-2026-08-03.1`

Build ID: `phase6f-education-promotion-1.0`

Source bundle: `complete-opportunity-source-bundle-2026-08-03.1`

## Institution and source result

The build checksum-verifies the complete committed Phase 6C replay chain and Phase 6E staged
outputs. All 13 locally retained CWTS captures match their recorded byte counts and SHA-256 hashes.
The frozen source remains CWTS Leiden Ranking Open Edition 2025, DOI
`10.5281/zenodo.17473224`, August 2025 OpenAlex snapshot, 2020–2023 window, and CC0 result/data.
No live OpenAlex or locality/campus inference is used.

Institution validation passes with 2,831 source institutions, 2,831 unique ROR identities, 2,825
exact name/country matches, and six explicit high-confidence manual disambiguations. There are no
many-to-one ROR merges. The promoted normalization retains exact field output and rank-band
components for all four filters.

## Exact education results

| Filter | Verified | Not established | Insufficient | Assessable |
|---|---:|---:|---:|---:|
| `engineering_technology_education_opportunity` | 27 | 48 | 16 | 75 |
| `computer_science_ict_education_opportunity` | 30 | 45 | 16 | 75 |
| `medicine_health_sciences_education_opportunity` | 30 | 45 | 16 | 75 |
| `natural_sciences_education_opportunity` | 31 | 44 | 16 | 75 |

All passing top-100, top-300 breadth, base output/breadth, high-output/minimum-breadth, and
high-breadth/minimum-output routes are retained separately. Represented non-passing countries are
not established; the 16 countries absent from the frozen research-intensive universe are
insufficient. Every supported-field benchmark shortlist remains 20/20 assessable.

## Research reconciliation and exclusions

The production matrix matches Phase 6C state, output, breadth, prominence counts, field, period,
country mapping, and the equivalent research route families with no discrepancies. Institution
aggregation reproduces every represented country metric. Frozen P60 thresholds are immutable and
global, with no country exceptions.

Business/finance remains held for a taxonomy/source gap. Broad university excellence remains
rejected as a product construct. Generic research/academia employment is not onboarded. The
career–education crosswalk is retained as explanatory, non-causal metadata with no runtime effect.

## Deliverables

- production builder: `src/konsider/ingestion/phase6_education_opportunity.py`
- complete staged bundle: `data/reports/phase6f-2026-08-03/staged-release`
- education-only catalog and 364-row evidence matrix: `data/reports/phase6f-2026-08-03`
- 2,831-row institution normalization and identity summary: `data/reports/phase6f-2026-08-03`
- source/legal record and research reconciliation: `data/reports/phase6f-2026-08-03`
- explanatory career–education crosswalk: `data/reports/phase6f-2026-08-03/career-education-crosswalk.json`
- operations/data guide: `docs/data/education-opportunity-evidence.md`
- tests: `tests/unit/test_phase6f_education_opportunity.py`

## Verification

Local verification on 2026-08-03:

- Phase 6C and Phase 6E committed input hashes: passed;
- 13 retained CWTS source byte counts and SHA-256 hashes: passed;
- institution/ROR/manual-disambiguation validation: passed;
- focused Phase 6F tests: `17 passed`;
- full backend regression: `344 passed`;
- repository-wide Ruff, Black check (100 files unchanged), and Python compileall: passed;
- active release `2026-07-29.2` replay: `replay=PASSED`;
- regenerated OpenAPI JSON and TypeScript declarations: no Git diff;
- clean-checkout regeneration without raw sources: byte-identical.

## Owner decisions before Phase 6G

Phase 6G should begin only after the owner accepts or revises:

1. the exact four education state distributions and zero-discrepancy Phase 6C promotion;
2. the narrow research-intensive university boundary and exact four CWTS fields;
3. CWTS as the material result dependency and verified ROR identity as a publication gate;
4. frozen global P60 routes with no country exceptions and all passing routes visible;
5. continued exclusion of business/finance, broad university excellence, and generic academia
   employment;
6. the combined `phase6f-complete-2026-08-03.1` bundle remaining draft and inactive while Phase 6G
   adds only the filter engine and API behavior under its separate prompt.

No Phase 6G work has started.
