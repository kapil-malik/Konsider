# Phase 4B: partial-coverage candidate selection and simulations

Status: complete; dispositions approved by the user on 2026-07-27

Decision status: `USER_APPROVED`

Evidence and simulation date: 2026-07-27

Policy: [`uncertainty-aware-ranking-policy-1.0`](../product/uncertainty-aware-ranking.md)

Active baseline release: `2026-07-27.1`

## 1. Decision summary

Phase 4B evaluated C08, C11, C26, and C53 against the approved Phase 4A policy. All four pass the
82/91 coverage threshold. None of their 15 possible non-empty combinations exceeds the hard
nine-country missing-union limit, although nine combinations are in the elevated six-to-nine
country band.

The recommendation is:

```text
recommended_initial_pcc_ids = [C11]
recommended_second_wave_pcc_ids = [C08]
recommended_reserve_pcc_ids = [C53]
recommended_deferred_pcc_ids = [C26]
decision_status = USER_APPROVED
```

- **C11** is the recommended initial PCC because it has high relocation decision value, 88/91
  coverage, deterministic evidence and replay, and clear CC BY 4.0 evidence. Its singleton
  simulations were robust across every tested transform, profile, weight, and K. Phase 4F must
  still freeze the composite and component weights.
- **C08** is recommended for a second experimental wave. Its singleton and all tested combinations
  that exclude C53 were robust across variants, but its HLO/LAYS/published-schooling-component
  construct is not frozen and all four exclusions are in Latin America and the Caribbean.
- **C53** remains reserve. Its measured construct is narrow and saturated: 64 of 86 valid countries
  have at least 90% on both basic-service components, 51 have at least 95%, and the median lower
  component is 97.37%. It also drives every persistent affected case involving Croatia in these
  simulations.
- **C26** is deferred despite excellent 90/91 coverage. The exact probe still carries
  `LIC_REDISTRIBUTION_REVIEW`; Phase 4B cannot convert open public access into a production reuse
  approval. If that gate is resolved, C26 should be reconsidered for the initial set alongside
  C11.

C29 macroeconomic stability and C66 extreme-weather risk remain separate full-coverage future
candidates. They are not PCCs and were not mixed into the missing-data decision.

## 2. Evidence boundary

This phase used only:

- the stable 91-country catalog and four current server-owned profiles;
- the eight enabled FCC scores in immutable release `2026-07-27.1`;
- committed Phase 3 candidate definitions and exact country-result matrices;
- committed online/offline replay conclusions; and
- deterministic, research-only transforms defined below.

No live source was fetched. No source was registered for production. No catalog, immutable release,
production score, or active pointer was changed.

Coverage findings are source facts under the pinned editions. Ranking and robustness findings are
conditional on provisional transforms and must not be treated as production-method approval.

## 3. Candidate eligibility matrix

| Candidate | Valid | Exact non-valid outcomes | Source and freshness | Non-coverage gates | Phase 4B disposition |
| --- | ---: | --- | --- | --- | --- |
| C08 School education quality | 87/91 | ATG invalid; BHS missing; BOL missing; GUY stale | World Bank HCI+ v3; freshness floor 2024 | CC BY 4.0 and replay pass; experimental construct and local-school/year-label caveats remain | Second wave, experimental |
| C11 Overall job-market opportunity | 88/91 | ATG missing; GRD missing; UKR stale | ILOSTAT Nov. 2025 modelled estimates; freshness floor 2025 | CC BY 4.0 and replay pass; composite weighting, shared-component and modelled-estimate review remain | Initial, conditional on method freeze |
| C26 Financial protection from health costs | 90/91 | UKR stale | WHO GHED March 2026; freshness floor 2023 | Replay passes; proxy semantics and estimated values remain; `LIC_REDISTRIBUTION_REVIEW` is unresolved | Deferred pending licence resolution |
| C53 Basic water and sanitation service access | 86/91 | BHS missing; BIH invalid; GRD invalid; HRV invalid; NIC missing | JMP 2025 via WDI; freshness floor 2022 | CC BY 4.0 and replay pass; weak discrimination, local variation, and basic-not-safely-managed caveats remain | Reserve |

The exact normalized and source reason codes are in the
[candidate matrix](../../data/reports/phase4b-2026-07-27/candidate-matrix.json). In particular:

- C08 ATG fails `VAL_COMPONENT_MISSING:hci_plus_schooling_component`; BHS and BOL have
  `COV_SOURCE_RECORD_MISSING`; GUY has `FRS_STALE`.
- C11 ATG and GRD have `COV_SOURCE_RECORD_MISSING`; UKR has `FRS_STALE`.
- C26 UKR has `FRS_STALE`.
- C53 BHS and NIC have `COV_SOURCE_RECORD_MISSING`; BIH and HRV lack basic sanitation; GRD lacks
  basic drinking water.

All four candidate matrices contain one explicit outcome for every stable country. Provisional
scores exist only for outcomes marked valid.

## 4. Combination coverage

The exact union calculation produces:

| Active PCC combination | Excluded | Eligible | Band |
| --- | ---: | ---: | --- |
| C08 | 4 | 87 | Preferred |
| C11 | 3 | 88 | Preferred |
| C26 | 1 | 90 | Preferred |
| C53 | 5 | 86 | Preferred |
| C08 + C11 | 6 | 85 | Elevated |
| C08 + C26 | 5 | 86 | Preferred |
| C08 + C53 | 8 | 83 | Elevated |
| C11 + C26 | 3 | 88 | Preferred |
| C11 + C53 | 7 | 84 | Elevated |
| C26 + C53 | 6 | 85 | Elevated |
| C08 + C11 + C26 | 6 | 85 | Elevated |
| C08 + C11 + C53 | 9 | 82 | Elevated |
| C08 + C26 + C53 | 9 | 82 | Elevated |
| C11 + C26 + C53 | 7 | 84 | Elevated |
| C08 + C11 + C26 + C53 | 9 | 82 | Elevated |

Results:

- Six combinations are preferred.
- Nine are elevated.
- None is blocked.
- C11 + C26 excludes ATG, GRD, and UKR: three, as expected.
- C08 + C26 excludes ATG, BHS, BOL, GUY, and UKR: five.
- C08 + C11 + C26 excludes ATG, BHS, BOL, GRD, GUY, and UKR: six.
- The four-candidate union adds BIH, HRV, and NIC for a total of nine.

The exact every-singleton/pair/triple/full-set matrix is available as
[JSON](../../data/reports/phase4b-2026-07-27/combination-unions.json) and
[CSV](../../data/reports/phase4b-2026-07-27/combination-unions.csv).

## 5. Regional concentration

The stable catalog contains 42 Europe and Central Asia countries, 22 Latin America and Caribbean
countries, 10 East Asia and Pacific countries, seven Middle East/North Africa/Afghanistan/Pakistan
countries, seven Sub-Saharan Africa countries, two North America countries, and one South Asia
country.

| Candidate | Regional result | Descriptive flag |
| --- | --- | --- |
| C08 | All four exclusions are in Latin America and the Caribbean: 100% of exclusions versus 24.2% of the catalog; ratio 4.14 | `STRONG_REGIONAL_CONCENTRATION` |
| C11 | Two of three exclusions are in Latin America and the Caribbean: 66.7% versus 24.2%; ratio 2.76 | `STRONG_REGIONAL_CONCENTRATION` |
| C26 | The sole exclusion is in Europe and Central Asia: 100% versus 46.2%; ratio 2.17; the sample is one country | `SOME_REGIONAL_CONCENTRATION` |
| C53 | Three of five exclusions are in Latin America and the Caribbean: 60% versus 24.2%; ratio 2.48 | `STRONG_REGIONAL_CONCENTRATION` |

Every combination containing C08 has substantial Latin America and Caribbean concentration. That
does not trigger a coverage block, but it makes C08's four-country exclusion qualitatively more
important than the count alone suggests. C11 has the same directional concern at smaller scale.

For repeatable descriptive labeling, Phase 4B used:

- `STRONG_REGIONAL_CONCENTRATION` when at least three countries are excluded and one region
  contains at least 60% of exclusions at an overrepresentation ratio of at least 2;
- `SOME_REGIONAL_CONCENTRATION` when a region's ratio is at least 1.5 but the strong condition is
  not met; and
- `NO_VISIBLE_CONCENTRATION` otherwise.

These are research descriptions, not product-policy thresholds. The full counts, within-region
rates, catalog shares, exclusion shares, ratios, and evidence strings are in the
[regional-bias artifact](../../data/reports/phase4b-2026-07-27/regional-bias.json).

## 6. Provisional transforms

Every transform is deterministic, versioned, monotonic, uses only Phase 3 values, and is marked
`PROVISIONAL_RESEARCH_ONLY`.

### C08

- Base: `C08_LAYS_PERCENTILE_PROVISIONAL_V1` — average-rank percentile of learning-adjusted years
  of schooling.
- Sensitivity: `C08_HLO_PERCENTILE_PROVISIONAL_V1` — average-rank percentile of harmonized
  learning outcome.
- Sensitivity: `C08_SCHOOLING_COMPONENT_PERCENTILE_PROVISIONAL_V1` — average-rank percentile of
  the published schooling component, without treating it as a percentage.

### C11

- Base: `C11_EQUAL_COMPONENT_PERCENTILES_PROVISIONAL_V1` — equal mean of employment,
  participation, and reverse-unemployment percentiles.
- Sensitivity: `C11_EMPLOYMENT_HEAVY_PROVISIONAL_V1` — weights 0.50, 0.25, and 0.25.
- Sensitivity: `C11_UNEMPLOYMENT_HEAVY_PROVISIONAL_V1` — weights 0.25, 0.15, and 0.60.

### C26

- Base: `C26_OOP_BROAD_BANDS_PROVISIONAL_V1` — fixed broad piecewise mapping of lower
  out-of-pocket share to a higher score.
- Sensitivity: `C26_OOP_REVERSE_PERCENTILE_PROVISIONAL_V1`.
- Sensitivity: `C26_OOP_LINEAR_0_70_PROVISIONAL_V1` — fixed linear 0%=10 to 70%=1, clamped.

### C53

- Base: `C53_MINIMUM_BASIC_SERVICE_BANDS_PROVISIONAL_V1` — fixed bands applied to the lower of
  basic drinking-water and basic sanitation access.

Variants preserve identical candidate coverage. The optimistic bound always substitutes score 10
for every non-ready active PCC outcome; that is the Phase 4A diagnostic rule, not provisional
imputation.

Exact definitions, score ranges, and all provisional country scores are in
[provisional-transforms.json](../../data/reports/phase4b-2026-07-27/provisional-transforms.json).

## 7. Simulation design and count

Each of the four existing catalog profiles retained its current eight FCC raw weights. For every
profile the generator evaluated:

- all 15 non-empty candidate combinations;
- uniform PCC weights 0.6, 0.8, and 1.0;
- for every multi-PCC combination, each one-dominant case with one PCC at 1.0 and all others at
  0.6;
- top K values 5, 10, and 20;
- one FCC-only control; and
- four singleton Low=0.4 controls proving that below-threshold PCC is ignored.

Per profile this is:

- 73 active weight cases;
- five controls;
- 78 total weight cases; and
- 234 profile/weight/K groups.

Across four profiles:

- 936 grouped cases were evaluated;
- 876 had active PCC;
- 60 were FCC-only/below-threshold controls; and
- expanding the applicable transform cross-products produced 8,736 deterministic runs.

The singleton 0.6/0.8/1.0 requirements are included in the 73 active cases and were not duplicated.

The generator is
[`scripts/phase4b_candidate_simulation.py`](../../scripts/phase4b_candidate_simulation.py).
Its input/output hashes are recorded in the
[manifest](../../data/reports/phase4b-2026-07-27/manifest.json).

## 8. Robustness findings

### 8.1 Overall

Among the 876 active grouped cases:

| Variant classification | Groups | Share |
| --- | ---: | ---: |
| `ROBUST_ACROSS_VARIANTS` | 786 | 89.7% |
| `POTENTIALLY_AFFECTED_ACROSS_VARIANTS` | 52 | 5.9% |
| `TRANSFORM_SENSITIVE` | 38 | 4.3% |

The 8,736 transform-expanded runs contain 8,186 `ROBUST_TOP_K`, 91
`POTENTIALLY_AFFECTED`, 399 `BASELINE_TOP_K_EXCLUDED`, and 60 no-active-PCC controls.

All 60 controls reproduced FCC-only behavior. Each Low=0.4 PCC was ignored before normalization,
coverage, and robustness.

### 8.2 By K

| K | Robust across variants | Affected across variants | Transform-sensitive |
| ---: | ---: | ---: | ---: |
| 5 | 286 | 1 | 5 |
| 10 | 272 | 7 | 13 |
| 20 | 228 | 44 | 20 |

Uncertainty naturally rises at top 20 because the boundary extends farther down the ranked set.

### 8.3 By profile

| Profile | Robust across variants | Affected across variants | Transform-sensitive |
| --- | ---: | ---: | ---: |
| Balanced | 215 | 0 | 4 |
| Safety & Stability | 207 | 0 | 12 |
| Affordability First | 146 | 52 | 21 |
| Quality of Life | 218 | 0 | 1 |

Every affected-across-variants group occurs under Affordability First. That profile assigns lower
FCC weights to several non-cost criteria, so a high optimistic substitution for a selected PCC has
more leverage at the boundary. This is a scenario finding, not evidence that the profile or
candidate score is wrong.

### 8.4 Singleton findings

| Candidate | Grouped cases | Result |
| --- | ---: | --- |
| C08 | 36 | All `ROBUST_ACROSS_VARIANTS` |
| C11 | 36 | All `ROBUST_ACROSS_VARIANTS` |
| C26 | 36 | All `ROBUST_ACROSS_VARIANTS` |
| C53 | 36 | 31 robust; five affected across variants |

C53's five affected singleton cases are all Affordability First:

- weight 0.6 at top 20: HRV was already on the score-bounded FCC top-20 boundary;
- weights 0.8 and 1.0 at top 10: HRV's optimistic bound could reach the boundary; and
- weights 0.8 and 1.0 at top 20: HRV was already on the FCC top-20 boundary.

### 8.5 Combination findings

| Combination | Grouped variant result |
| --- | --- |
| C08 + C11 | 60/60 robust |
| C08 + C26 | 60/60 robust |
| C08 + C11 + C26 | 72/72 robust |
| C11 + C26 | 56 robust; three transform-sensitive; one affected across variants |
| C08 + C53 | 55 robust; five affected across variants |
| C11 + C53 | 54 robust; one sensitive; five affected |
| C26 + C53 | 37 robust; 12 sensitive; 11 affected |
| C08 + C11 + C53 | 66 robust; six affected |
| C08 + C26 + C53 | 58 robust; eight sensitive; six affected |
| C11 + C26 + C53 | 58 robust; eight sensitive; six affected |
| All four | 71 robust; six sensitive; seven affected |

For C11 + C26, all four non-robust groups are Affordability First at top 20:

- uniform 1.0 is affected across all variants because UKR can reach the boundary;
- uniform 0.8 is transform-sensitive; and
- the C11-dominant and C26-dominant stress cases are transform-sensitive.

Every persistent affected case in combinations containing C53 is driven by HRV. In some top-20
cases HRV was already on the FCC baseline boundary, which correctly triggers the strongest
`BASELINE_TOP_K_EXCLUDED` status regardless of provisional transform.

The full grouped report is
[robustness-summary.json](../../data/reports/phase4b-2026-07-27/robustness-summary.json).
The compressed, machine-readable transform-expanded runs—including exact baseline ranks,
score-boundary membership, optimistic bounds, and potential-entry flags—are in
[robustness-simulations.jsonl.gz](../../data/reports/phase4b-2026-07-27/robustness-simulations.jsonl.gz).

## 9. Candidate decisions

### C11 — approved for the initial wave

C11 best satisfies the Phase 4 exception rationale: it addresses a central relocation question,
excludes only three countries, has reproducible source and replay evidence, and is robust across all
36 singleton grouped cases. Its regional concentration is material and must be disclosed.

Phase 4F inputs still required:

- freeze whether the three-component composite remains the product construct;
- freeze component transforms and weights;
- record component correlations and removal/weight sensitivity;
- keep the national/modelled/occupation-neutral label and caveats; and
- preserve ATG and GRD missing plus UKR stale.

### C08 — recommend experimental second wave

C08's robustness results are encouraging, but they do not decide between LAYS, HLO, and the
published schooling component. Its 100% Latin America and Caribbean exclusion concentration and
local-school interpretation are material. It should follow C11 only after a user-approved
experimental scoring construct is frozen.

Phase 4F inputs still required:

- select and version the primary construct;
- explain why that construct answers the relocation question;
- retain model, mixed-year, and local-school caveats;
- keep experimental status; and
- preserve ATG invalid, BHS/BOL missing, and GUY stale.

### C53 — retain as reserve

C53 fits the coverage mechanics but does not gain enough product value merely by becoming
technically rankable. Its construct is saturated among many destinations, its label must remain
limited to basic service access, its exclusions are regionally concentrated, and it causes the
clearest affected/baseline-warning scenarios in this study. Promotion requires separate user
approval plus evidence of marginal decision value beyond existing environmental/infrastructure
context.

### C26 — defer until licensing is resolved

C26 has the best coverage and its singleton simulations are robust. It would be a strong candidate
after a production-compatible reuse conclusion is documented. Phase 4B does not reject the
construct; it rejects silently treating an unresolved licence blocker as passed.

If licensing is resolved:

- reconsider C26 for the initial set with C11;
- freeze the OOP-share scoring method;
- retain the financial-protection-proxy label and estimated-value caveat;
- do not imply migrant eligibility, premiums, quality, waiting time, or personal affordability;
- preserve UKR stale; and
- explicitly test the four Affordability First/top-20 C11+C26 caution cases.

## 10. Inputs for Phase 4F

Phase 4F must receive:

1. User-approved dispositions: C11 initial, C08 second wave, C53 reserve, and C26 deferred.
2. The exact candidate source definition and Phase 3 country-result file recorded in the manifest.
3. A resolved production licence conclusion for every selected candidate.
4. A frozen, versioned production transform and sensitivity rationale; no provisional Phase 4B
   transform may be copied into production by default.
5. Exact 91-country attempt outcomes and normalized/source reason codes from the candidate matrix.
6. The combination-union and regional-bias artifacts for the approved set.
7. Candidate-specific label, granularity, model/estimate, local-variation, and proxy caveats.
8. Online/offline replay evidence and retained raw artifact hashes.
9. For C11, component redundancy and weight sensitivity.
10. For C08, the selected schooling construct and experimental decision.
11. For C26, resolved `LIC_REDISTRIBUTION_REVIEW`.
12. For C53, separate discrimination evidence and explicit user approval if it leaves reserve.

## 11. Limitations

- Provisional rank-percentile variants are distribution-dependent and deliberately unsuitable for
  automatic production adoption.
- Optimistic score 10 is a policy diagnostic; it is intentionally extreme and not a prediction.
- Historical simulation uses the current eight FCC scores and four current profiles only.
- Robustness does not establish construct validity, source licensing, maintenance feasibility, or
  user value.
- Regional labels are descriptive and do not constitute a blocking policy.
- National measures do not solve city, school, occupation, household, migrant-eligibility, or
  local-service questions.
- The analysis did not modify or publish production data.

## 12. Reproduction and artifacts

From the repository root:

```powershell
python scripts\phase4b_candidate_simulation.py
```

The output directory is
[`data/reports/phase4b-2026-07-27`](../../data/reports/phase4b-2026-07-27/summary.json).
Its summary records:

- four candidates;
- 15 combinations;
- six preferred, nine elevated, and zero blocked combinations;
- 936 grouped simulations;
- 8,736 transform-expanded simulations; and
- the four approved disposition arrays with `USER_APPROVED`.

Re-running the generator must reproduce every output hash in the manifest. Production activation
is outside Phase 4B.
