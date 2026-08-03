# Education Opportunity Filter evidence

Status: Phase 6F staged evidence complete; not active and not exposed through API or UI

Build: `phase6f-education-promotion-1.0`

Complete staged release fragment: `phase6f-complete-2026-08-03.1`

## Product boundary

The four education Opportunity Filters describe the country-level strength of a research-intensive
university ecosystem in one exact official CWTS field. They do not establish teaching or programme
quality, programme availability, admissions or international-student access, tuition,
scholarships, accreditation, qualification recognition, visa eligibility, campus accessibility,
language fit, employment outcomes, or applicant success.

`STRONG_SIGNAL_NOT_ESTABLISHED` means a represented country had complete evidence but passed no
approved strong route. It does not mean that the country has no universities or programmes.
`INSUFFICIENT_EVIDENCE` is never a negative conclusion.

The complete nine-filter candidate is under
`data/reports/phase6f-2026-08-03/staged-release`. It contains the five Phase 6E career definitions
and these four education definitions, all inactive. Active release `2026-07-29.2`, ranking, API v2,
and UI are unchanged.

## Official source and institution identity

The production route is exactly the Phase 6C frozen source:

- CWTS Leiden Ranking Open Edition 2025, DOI `10.5281/zenodo.17473224`;
- frozen August 2025 OpenAlex snapshot and 2020–2023 publication window;
- 2,831 research-intensive universities across 120 countries;
- CC0 result/data and official ROR identifiers from the CWTS universities workbook;
- committed normalized fixture plus exact raw source/workbook byte counts and SHA-256 hashes;
- no live OpenAlex API, inferred coordinates, GeoNames, locality, or campus mapping.

The normalized institution artifact retains source ID and display name, canonical name, ROR ID,
country, mapping method and confidence, and per-field output, rank, citation, redaction, and
top-100/200/300 band components. Validation proves 2,831 unique source IDs, 2,831 unique ROR IDs,
2,825 exact name/country matches, six high-confidence manual quoted-name disambiguations, and no
many-to-one ROR merges. Country is the finest geographic assignment.

Both source families are material dependencies. Without the CWTS results, every supported field is
unassessable. Without verified ROR identity, publication fails closed. The API runtime never
acquires source data.

## Frozen portfolio and coverage

| Filter | Official field | Verified | Not established | Insufficient | Assessable |
|---|---|---:|---:|---:|---:|
| Engineering and technology | Physical sciences and engineering | 27 | 48 | 16 | 75 |
| Computer science and ICT | Mathematics and computer science | 30 | 45 | 16 | 75 |
| Medicine and health sciences | Biomedical and health sciences | 30 | 45 | 16 | 75 |
| Natural sciences | Life and earth sciences | 31 | 44 | 16 | 75 |

The education-only matrix contains exactly 4 × 91 = 364 rows. The combined staged matrix contains
exactly 9 × 91 = 819 rows. Every frozen Phase 6C benchmark top-20 list remains 20/20 assessable and
its order is unchanged.

The same 16 stable countries are absent from the retained research-intensive source universe for
all four fields: ALB, ATG, BHS, DOM, FJI, GTM, GUY, HND, HTI, MDA, MNG, MUS, NIC, PAN, SLV, and
TTO. Their state is `INSUFFICIENT_EVIDENCE`; absence is not treated as zero.

Business and finance higher-education opportunity is not onboarded because the official source
taxonomy cannot isolate it. Broad university excellence is not onboarded because it was rejected
as a product construct. Generic research or academia employment is also outside this phase.

## Frozen P60 routes

A represented country is `VERIFIED_STRONG_SIGNAL` when at least one route passes:

1. `top_100_institution`: at least one institution in the global field top 100;
2. `top_300_breadth`: at least three institutions in the global field top 300;
3. `base_output_and_breadth`: output ≥ base output and breadth ≥ base breadth;
4. `high_output_minimum_breadth`: output ≥ high output and breadth ≥ minimum breadth;
5. `high_breadth_minimum_output`: breadth ≥ high breadth and output ≥ minimum output.

All passing route IDs remain visible. Percentiles are never recomputed and there are no country
exceptions.

| Official field | Base output | Base breadth | High output | Min breadth | High breadth | Min output |
|---|---:|---:|---:|---:|---:|---:|
| Physical sciences and engineering | 7,834.8 | 12.8 | 30,774.2 | 6 | 39.2 | 2,623.2 |
| Mathematics and computer science | 6,337.0 | 12.8 | 17,870.8 | 6 | 39.2 | 2,215.6 |
| Biomedical and health sciences | 12,502.8 | 12.8 | 39,464.8 | 6 | 39.2 | 2,761.6 |
| Life and earth sciences | 4,560.2 | 12.8 | 13,754.6 | 6 | 39.2 | 1,397.8 |

The evidence payload retains fractional publication output, active institution breadth, and
top-100, top-200, and top-300 counts. The committed institution normalization retains the
underlying institution ranks and components; normal ranking responses do not expose a full
institution list.

## Replay and refresh

Rebuild from committed, checksum-bound Phase 6C and Phase 6E inputs:

```powershell
python -m konsider.ingestion.phase6_education_opportunity `
  --output data/reports/phase6f-2026-08-03
```

Add `--verify-retained-sources` when the ignored CWTS captures are present to require all 13 exact
byte counts and hashes. The generated derivative is byte-identical without raw source files.

For a future source release:

1. capture source bytes outside API runtime and record version, DOI, snapshot, window, licence,
   byte count, and SHA-256;
2. verify official ROR identities, review every non-exact mapping, and prohibit many-to-one merges;
3. retain the four exact official fields and country-only geography;
4. keep the frozen release policy unless a separately approved recalibration changes its version;
5. regenerate to a new immutable draft ID and compare all states, routes, metrics, source fields,
   periods, identities, and country assignments;
6. run retained-source replay, deterministic regeneration, full regression, and owner review before
   publication.

## Reconciliation and metadata

[`research-production-reconciliation.json`](../../data/reports/phase6f-2026-08-03/research-production-reconciliation.json)
records zero state, metric, route, institution-identity, shortlist, source-field, period, or country
mapping discrepancies. The production builder recomputes all five exact subroutes and reconciles
them to the three Phase 6C research route families.

[`career-education-crosswalk.json`](../../data/reports/phase6f-2026-08-03/career-education-crosswalk.json)
is explanatory metadata only. It does not merge states, infer causality or applicant opportunity,
or create runtime profile taxonomy.

Source/legal details are in
[`source-legal-records.json`](../../data/reports/phase6f-2026-08-03/source-legal-records.json), and
the identity audit is in
[`institution-identity-summary.json`](../../data/reports/phase6f-2026-08-03/institution-identity-summary.json).

