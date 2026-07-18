# Scoring methodology and sensitivity

Status: provisional research methods; not product-ready rankings

Last updated: 2026-07-18

Release `2026-07-18.2` compares three transformations for every criterion: 5th/95th winsorized
min-max, sample percentile rank, and fixed piecewise-linear domain thresholds. Min-max and percentile
always span roughly 1-10 even when observations are nearly identical and change when countries enter
or leave the sample. That behaviour exaggerates small differences, so neither is selected.

The provisional methods use fixed anchors and cap outside values:

| Criterion | Method version | Raw value -> score anchors |
| --- | --- | --- |
| Modelled PM2.5, lower better | `pm25_health_bands_v1` | 5->10, 15->8, 25->6, 35->4, 50->1 µg/m³ |
| Intentional homicide, lower better | `homicide_risk_bands_v1` | 0->10, 1->9, 3->7, 5->5, 10->1 per 100k |
| WHO UHC, higher better | `uhc_coverage_bands_v1` | 50->1, 60->3, 70->5, 80->7.5, 90->10 |
| ICP household price level, lower better | `icp_price_level_bands_v1` | 50->10, 75->8, 100->6, 125->4, 150->2, 175->1; US=100 |
| WPS Index, higher better | `wps_index_bands_v1` | 0.5->1, 0.6->3, 0.7->5, 0.8->7.5, 0.9->10 |

The release's `scoring-sensitivity.json` records observed ranges, score ranges and standard
deviations for all methods, removal of the raw minimum and maximum, and a synthetic tightly clustered
20-country sample. In the tight-cluster test, percentile and winsorized min-max each still span 9
score points. Fixed thresholds span only about 0.06 PM2.5, 0.06 homicide, 0.06 UHC, 0.09 ICP, and
0.25 WPS points for the tested clusters.

These anchors are provisional, not normative truth. Before product readiness they need domain review,
uncertainty propagation, missing-data policy review, and user testing. In particular, the ICP score
must not be presented as a precise strict country ranking, and WPS/WHO licensing must be cleared.
