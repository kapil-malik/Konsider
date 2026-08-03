# Phase 6E career Opportunity Filter evidence onboarding

Status: complete; staged only

Completed: 2026-08-03

Implementation commit: pending final commit

## Outcome

Phase 6E productionizes the five approved career Opportunity Filters into a deterministic staged
release fragment. The bundle contains five inactive definitions and exactly 455 country-evidence
records across the stable 91-country universe. No release is activated, no ranking behavior changes,
and API v2 and UI remain unchanged.

Staged artifact ID: `phase6e-career-2026-08-03.1`

Build ID: `phase6e-career-promotion-1.0`

Source bundle: `career-opportunity-source-bundle-2026-08-03.1`

## Source routes

- ILOSTAT observed two-digit occupation `EMP_TEMP_SEX_OC2_NB_A` for technology/software and
  science/engineering.
- Statistics Canada `98-10-0594-01` with frozen NOC 2021 codes 2122, 2123 and 2222 for the Canada
  technology positive only.
- Eurostat `lfsa_egai2d` for Malta technology and science/engineering.
- ILO November 2025 modelled occupation `EMP_2EMP_SEX_OCU_NB_A` for skilled trades.
- ILO November 2025 modelled economic activity `EMP_2EMP_SEX_ECO_NB_A` for care, finance/insurance
  and construction.
- Japan e-Stat, KOSIS and Stats NZ limitations remain supplemental source-gap records only; no
  broad proxy is applied.

All locally retained raw captures passed recorded byte-count and SHA-256 verification. The build is
also reproducible from committed normalized inputs when ignored raw bytes are absent.

## Exact results

| Filter | Verified | Not established | Insufficient | Assessable |
|---|---:|---:|---:|---:|
| `technology_software_opportunity` | 20 | 43 | 28 | 63 |
| `science_engineering_opportunity` | 20 | 47 | 24 | 67 |
| `health_social_work_opportunity` | 27 | 61 | 3 | 88 |
| `finance_insurance_opportunity` | 22 | 66 | 3 | 88 |
| `skilled_trades_construction_opportunity` | 34 | 54 | 3 | 88 |

The skilled-trades/construction assessed split is exactly 15 skilled-only, 11 construction-only,
8 both and 54 neither, with 3 further countries insufficient. Both routes' scale, share, threshold
components and pass state are retained explicitly.

## Research reconciliation

Production states, state counts, metric components, threshold routes, confidence tiers, reference
periods, translated Phase 6D reason codes, source-family references and benchmark-shortlist coverage
match the approved Phase 6B/6B.1 artifacts. There are no documented discrepancies.

Canada technology is a medium-confidence positive under the approved NOC mapping. Canada science
retains its numeric supplemental evidence but remains insufficient because a complete official
crosswalk was not established. Malta remains not established for both constructs under the global
scale floor. Japan, South Korea and New Zealand remain insufficient.

## Deliverables

- production builder: `src/konsider/ingestion/phase6_career_opportunity.py`
- staged bundle: `data/reports/phase6e-2026-08-03/staged-release`
- build manifest: `data/reports/phase6e-2026-08-03/build-manifest.json`
- source/legal records: `data/reports/phase6e-2026-08-03/source-legal-records.json`
- production crosswalks: `data/reports/phase6e-2026-08-03/classification-crosswalks.json`
- reconciliation: `data/reports/phase6e-2026-08-03/research-production-reconciliation.json`
- evidence operations guide: `docs/data/career-opportunity-evidence.md`
- tests: `tests/unit/test_phase6e_career_opportunity.py`

The Phase 6D career metric contract is extended additively with explicit skilled-trades and
construction share fields; existing fixtures and consumers remain valid.

## Exact changed paths

Production contract and builder:

- `contracts/README.md`
- `contracts/schemas/v3/opportunity-filter-evidence.schema.json`
- `src/konsider/ingestion/phase6_career_opportunity.py`

Staged data and audit artifacts:

- `data/reports/phase6e-2026-08-03/build-manifest.json`
- `data/reports/phase6e-2026-08-03/classification-crosswalks.json`
- `data/reports/phase6e-2026-08-03/research-production-reconciliation.json`
- `data/reports/phase6e-2026-08-03/source-legal-records.json`
- `data/reports/phase6e-2026-08-03/staged-release/candidate-release-manifest.json`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-catalog.json`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-coverage-summary.json`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-evidence-policy.json`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-evidence.jsonl`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-source-manifest.json`
- `data/reports/phase6e-2026-08-03/staged-release/opportunity-filter-threshold-policies.json`

Tests and documentation:

- `tests/unit/test_phase6e_career_opportunity.py`
- `docs/README.md`
- `docs/architecture/opportunity-filter-contracts.md`
- `docs/data/career-opportunity-evidence.md`
- `docs/data/release-format.md`
- `docs/history/phase6e-career-opportunity-evidence.md`
- `docs/product/roadmap.md`
- `project-history/phases/phase-6/00_README.md`

## Verification

Local verification on 2026-08-03:

- retained Phase 6B/6B.1 research input checksums: passed;
- six locally retained raw source byte counts and SHA-256 checksums: passed;
- targeted Phase 6D/6E contracts and onboarding: `47 passed`;
- full backend regression: `327 passed` (one non-functional pytest cache warning caused by managed
  Windows directory permissions);
- Ruff: passed;
- Black: 107 files unchanged;
- Python compileall for `src` and `tests`: passed;
- active release `2026-07-29.2` retained-source replay: `replay=PASSED`;
- clean-checkout Phase 6E regeneration without raw bytes: byte-identical;
- regenerated OpenAPI JSON and TypeScript declarations: no Git diff;
- active release pointer/schema, ranking behavior and API v2 surface preservation: passed.

## Owner decisions before Phase 6F

Phase 6F should begin only after the owner accepts or revises:

1. the exact five staged state distributions and zero-discrepancy research promotion;
2. the continued ILO single-publisher dependency for the modelled routes;
3. Canada technology as medium-confidence official-source evidence under the frozen research
   crosswalk, with Canada science still insufficient;
4. the explicit route representation for skilled trades/construction and the additive metric-share
   contract fields;
5. retaining `phase6e-career-2026-08-03.1` as staged and inactive while Phase 6F adds four education
   filters to a later nine-filter candidate bundle.

No Phase 6F work has started.
