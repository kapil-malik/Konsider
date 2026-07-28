# Scoring methodology and sensitivity

Status: versioned transformations for active release `2026-07-28.2`

Last updated: 2026-07-28

For each criterion the worker compares 5th/95th winsorized min-max, sample percentile rank, and a
fixed domain transformation. Percentile and winsorized min-max can span the entire 1-10 range even
when a synthetic 20-country sample is tightly clustered. Fixed transformations produced 0-0.104
score spread in those tests, so they do not magnify tiny raw differences merely because of
the selected country set.

| Criterion | Selected method | Interpretation |
| --- | --- | --- |
| Population-weighted PM2.5, lower better | `pm25_health_bands_v1`: piecewise 5→10, 15→8, 25→6, 35→4, 50→1 µg/m³ | Fixed exposure/health-risk bands; modelled national comparison only. |
| Intentional homicide, lower better | `homicide_risk_bands_v1`: 0→10, 1→9, 3→7, 5→5, 10→1 per 100,000 | Fixed risk bands; no claim that reporting systems are identical. |
| UHC coverage, higher better | `uhc_coverage_bands_v1`: 50→1, 60→3, 70→5, 80→7.5, 90→10 | Retained for experiment/replay, but criterion is not product-ready because 2021 data is stale. |
| Household price level, lower cost better | `icp_relative_cost_bands_v2`: ≤60→9, ≤80→8, ≤100→6, ≤125→4, ≤150→2, >150→1 | Deliberately discrete broad bands. Equal scores are expected; do not use the underlying index or band score for precise country ordering. |
| Women’s legal and economic equality, higher better | `wbl_legal_equality_bands_v1`: 40→1, 55→3, 70→5.5, 85→8, 100→10 | WBL legal-framework index only; not a score of lived equality or enforcement. |
| Infrastructure readiness, higher better | `infrastructure_readiness_bands_v1`: composite 30→1, 45→3, 60→5.5, 75→8, 90→10 | Experimental equal-weight composite after fixed transforms of internet use, fixed broadband, and LPI infrastructure quality. |

Overall job-market opportunity uses `job_market_equal_component_percentiles_v1`. The pinned 2025
ILOSTAT modelled estimates for total population age 15+ are transformed as follows:

1. employment-to-population and labour-force participation become higher-is-better average-rank
   percentile scores from 1 to 10;
2. unemployment becomes a lower-is-better average-rank percentile score;
3. the three component scores receive equal one-third weights; and
4. the published composite is rounded to two decimal places.

The source edition's 2026–2027 projections are excluded. The score is distribution-relative across
the 88 valid supported countries. Employment-heavy, unemployment-heavy, and all three
leave-one-component-out variants are diagnostics only. No missing value is imputed and no
country-specific weight renormalisation occurs.

School education quality uses `learning_adjusted_schooling_bands_v1` with fixed LAYS anchors:
4→1, 6→3, 8→5.5, 10→8, and 12→10. The raw construct is learning-adjusted years of schooling, not a
percentage and not a rating of an individual school.

Research and innovation ecosystem uses `wipo_innovation_outputs_bands_v1` with fixed WIPO output
anchors: 10→1, 20→3, 30→5.5, 45→8, and 60→10. Only the published Innovation outputs sub-index is
used; the overall GII and input pillars are excluded.

The three Phase 3G-1 additions use fixed, versioned broad-band transformations:

- `wgi_political_stability_bands_v1` and `wgi_rule_of_law_bands_v1` map the WGI estimate range to
  broad 1-10 bands. Published uncertainty is retained; fine-grained rank claims are inappropriate.
- `migrant_presence_bands_v1` maps migrant stock as a percentage of population to broad bands.
  Higher means more of a user-selected preference property, not greater universal country quality.

The committed `scoring-sensitivity.json` records observed ranges, method score ranges and standard
deviations, removal of the raw minimum/maximum, and the tightly clustered sample for all six
criteria. Infrastructure additionally records component years and pairwise component correlations.
Those diagnostics must be reviewed on every refresh; high redundancy, missing components, stale LPI,
or material distribution changes can make the experimental composite non-ready.

The active release also records average-rank Spearman correlation between political stability and
rule of law. The measured value is 0.7295, below the pre-set 0.90 review threshold; both criteria
remain separately visible with the overlap disclosed.

The selected methods are provisional policy choices, not source facts. Scores retain observation
IDs, direction, transform parameters, and method versions. No scoring method can cure stale,
incomparable, missing, or inadequately licensed observations; validation handles those separately.

For a conditional ranking, canonical scores are never transformed again at request time. The
engine excludes any country lacking a valid outcome for an active PCC and normalizes one weight
vector over the same active criterion set for every remaining country. Score 10 substitution is
used only for the named optimistic excluded-country diagnostic; it is never persisted as an
observation, canonical score, total, or rank.
