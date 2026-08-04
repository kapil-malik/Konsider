# Career Opportunity Filter evidence

Status: promoted into active release `2026-08-04.1`

Build: `phase6e-career-promotion-1.0`

Staged release fragment: `phase6e-career-2026-08-03.1`

## Product boundary

These five Opportunity Filters describe destination-side employment ecosystems. They do not alter
affinity scores or country order and do not estimate vacancies, hiring probability, salary, job
quality, licensing, qualification recognition, visa access or applicant success. A
`STRONG_SIGNAL_NOT_ESTABLISHED` state does not mean that no employment exists, and
`INSUFFICIENT_EVIDENCE` is never a negative conclusion.

The retained Phase 6E source artifacts are under `data/reports/phase6e-2026-08-03/staged-release`.
Their accepted evidence was combined, identity-rebound, checksummed, and published in active
release `2026-08-04.1`.

## Frozen portfolio and coverage

| Filter | Exact construct | Verified | Not established | Insufficient | Assessable |
|---|---|---:|---:|---:|---:|
| Technology and software | ISCO-08 groups 25 and 35 employment | 20 | 43 | 28 | 63 |
| Science and engineering | ISCO-08 groups 21 and 31 employment | 20 | 47 | 24 | 67 |
| Care sector | ISIC Rev.4 section Q human health and social work employment | 27 | 61 | 3 | 88 |
| Finance and insurance | ISIC Rev.4 section K employment | 22 | 66 | 3 | 88 |
| Skilled trades or construction | ISCO-08 major group 7 OR ISIC Rev.4 section F employment | 34 | 54 | 3 | 88 |

Every filter has exactly one state for every country in `stable_supported_v1`: 5 filters × 91
countries = 455 records. Only `VERIFIED_STRONG_SIGNAL` will pass a future strict filter.

## Source routes and confidence

### Technology and science/engineering

The primary route is the retained ILOSTAT observed two-digit occupation indicator
`EMP_TEMP_SEX_OC2_NB_A`. It selects the latest acceptable 2021-or-later both-sex observation and
uses numerator and denominator from the same country, source, year and population. ILO break status
`B` is retained as a caveat. These complete rows use
`HIGH_CONFIDENCE_OBSERVED_HARMONISED`.

Phase 6B.1 adds two narrowly frozen routes:

- Canada technology uses Statistics Canada table `98-10-0594-01`, NOC 2021 v1.0 codes 2122,
  2123 and 2222, and `MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK`. Adjacent codes 2121 and 2131 remain
  excluded. The mapping may establish a positive but is not treated as a complete negative route.
- Canada science retains its conservative research mapping and numeric result only as
  `LOW_CONFIDENCE_SUPPLEMENTAL`. With no official NOC 2021–ISCO-08 concordance, its public state is
  `INSUFFICIENT_EVIDENCE` with `CROSSWALK_INCOMPLETE`.
- Malta uses Eurostat `lfsa_egai2d`, 2025, both sexes, age 15–74, thousand persons, at exact ISCO-08
  two-digit granularity. Both technology and science are complete harmonised observations but stay
  below the global scale floor, so both are `STRONG_SIGNAL_NOT_ESTABLISHED`.
- Japan, South Korea and New Zealand remain `INSUFFICIENT_EVIDENCE`; the retained public sources do
  not expose the detailed employment stock required by the frozen constructs. Major-group proxies
  are not used.

### Care, finance, skilled trades and construction

The broad routes use the November 2025 ILO modelled-estimate editions:

- `EMP_2EMP_SEX_ECO_NB_A` for ISIC Q, K and F;
- `EMP_2EMP_SEX_OCU_NB_A` for ISCO major group 7.

They use `MEDIUM_CONFIDENCE_MODELLED_HARMONISED`, disclose modelled status, and cover 88 of the 91
stable countries. Antigua and Barbuda, Grenada and Ukraine are absent from the retained source
universe and remain insufficient. An observed result would take precedence over a modelled result;
the builder never overwrites stronger evidence.

ILO is a material single-publisher dependency. Removing its modelled families makes the three broad
filters unassessable. This risk is explicit in the source/legal record.

## Frozen P60 thresholds

Every route uses:

`(scale >= P60 AND share >= P60) OR (scale >= P80 AND share >= P40) OR (share >= P80 AND scale >= P40)`

The raw values remain frozen to the approved pre-gap-fill reference distributions. They are never
recomputed from whichever countries happen to be present during a refresh.

| Route family | P60 scale (000s) | P60 share % | P80 scale (000s) | P40 share % | P80 share % | P40 scale (000s) |
|---|---:|---:|---:|---:|---:|---:|
| Technology | 183.694 | 3.404585 | 492.363 | 2.323686 | 4.058963 | 88.868 |
| Science/engineering | 364.893 | 6.083528 | 814.458 | 4.901980 | 7.526469 | 126.713 |
| Care sector | 453.0574 | 7.484637 | 1469.0624 | 4.722972 | 11.691941 | 147.652 |
| Finance/insurance | 119.7200 | 2.381522 | 470.9548 | 1.821987 | 2.950836 | 50.7606 |
| Skilled trades | 787.6608 | 11.966052 | 2209.4046 | 10.530950 | 13.856934 | 319.8666 |
| Construction | 471.3942 | 7.773501 | 1583.1238 | 6.879055 | 8.886313 | 217.8856 |

P50/P55/P60/P65/P70 sensitivity remains in the Phase 6B.1 calibration artifact. Only P60 is the
production policy; there are no country-specific exceptions.

## Skilled-trades/construction visibility

The two routes are never collapsed into an opaque score. Every assessed record retains both routes'
scale, share, threshold components and pass result. Verified records expose their establishing
route:

- 15 skilled-trades only;
- 11 construction only;
- 8 both;
- 54 neither among complete assessed outcomes;
- 3 insufficient.

The generic schema-1.0 scale/share pair mirrors the skilled-trades route for this construct; the
four explicit skilled/construction metric fields and both threshold-result objects are authoritative
for route inspection.

## Insufficient-evidence countries

- Technology/software (28): ARM, ATG, BHR, BHS, BWA, CMR, DZA, FJI, GHA, GRD, HND, HTI, JAM,
  JPN, KAZ, KOR, MDA, MYS, NAM, NIC, NZL, OMN, PRY, QAT, TTO, UKR, UZB, ZAF.
- Science/engineering (24): ARM, ATG, BHR, CAN, CMR, DZA, GHA, HTI, JAM, JPN, KAZ, KOR, MDA,
  MYS, NAM, NIC, NZL, OMN, PRY, QAT, TTO, UKR, UZB, ZAF.
- Care, finance/insurance and skilled-trades/construction (3 each): ATG, GRD, UKR.

Missingness never becomes zero and never supports a negative state.

## Artifacts and replay

The staged fragment contains the catalog, 455-row evidence matrix, source manifest, five threshold
policies, evidence policy, coverage summary and a draft `konsider-release-5.1` manifest. The draft
manifest checksum-binds the six Opportunity Filter siblings and the unchanged active-release base
artifacts. It is not a published release and is not referenced by `data/releases/active.json`.

Rebuild from committed normalized research inputs:

```powershell
python -m konsider.ingestion.phase6_career_opportunity `
  --output data/reports/phase6e-2026-08-03
```

When the ignored source bytes are locally retained, add `--verify-retained-sources` to require all
recorded byte counts and SHA-256 values to match before generation. The generated derivative is
byte-identical with or without local raw bytes.

The builder verifies Phase 6B/6B.1 input hashes, constructs the explicit 5 × 91 matrix, validates
every Phase 6D schema and cross-artifact rule, reconciles state and shortlist counts, checks the
15/11/8/54 route split, and writes deterministic JSON/JSONL.

## Refresh procedure

1. Fetch source bytes outside API runtime into the ignored `data/raw` source path.
2. Record publisher version, extraction identity, byte count, SHA-256, licence and attribution.
3. Apply the existing exact classification and same-source numerator/denominator rules.
4. Preserve the frozen raw thresholds; do not recalculate percentiles.
5. Apply confidence precedence and negative-integrity rules.
6. Regenerate into a new immutable staged release ID and compare all states, metrics, routes,
   confidence, periods, reasons and sources to the preceding evidence.
7. Run the full regression and retained-source replay before any later publication decision.

The API never fetches ILO, Eurostat or national sources live.

## Research reconciliation

[`research-production-reconciliation.json`](../../data/reports/phase6e-2026-08-03/research-production-reconciliation.json)
records zero state-count, shortlist, route, metric, threshold, confidence, period, reason or source
discrepancies after the approved Phase 6D vocabulary/family normalization. The Phase 6B and 6B.1
public states and metric components are unchanged. Source identities that were row-specific in the
research output are retained in lineage IDs while production source references use stable family
IDs.

Source and legal details are in
[`source-legal-records.json`](../../data/reports/phase6e-2026-08-03/source-legal-records.json).
The promoted ISCO/ISIC identity mappings and national crosswalk decisions are in
[`classification-crosswalks.json`](../../data/reports/phase6e-2026-08-03/classification-crosswalks.json).
