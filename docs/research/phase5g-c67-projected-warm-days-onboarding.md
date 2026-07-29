# Phase 5G: C67 projected warm-day frequency onboarding

Date: 2026-07-29

Decision: **experimentally onboarded**

Release: `2026-07-29.2`

## Product decision

C67 is no longer the vague **Long-term climate-change exposure** criterion. It is now
**Projected warm-day frequency (2030)**: the projected percentage of days in 2021-2030 when daily
maximum temperature exceeds the calendar-day 90th percentile, under SSP2-4.5.

The JRC fact sheet defines this field more cleanly than C66: its unit is percentage of days, its
spatial method is a zonal average of source-pixel values, and its scenario, horizon, baseline, and
model are explicit. Lower projected frequency scores better.

This is deliberately narrow. It is not a complete climate-risk score, an observed outcome, an
absolute heat threshold, or a multi-model uncertainty estimate. “Warm” is relative to each
calendar day's 1961-1990 local baseline. The projection uses EC-Earth3 and SSP2-4.5.

## Onboarding result

- Source field: `CL_WDS_245_2030` in GHS-UCDB R2024A V1.2.
- Frozen universe: 388 GHSL urban centres, at most five per supported country.
- Validity: 388/388 localities and 89/91 countries.
- Missing locality evidence: Antigua and Barbuda and Grenada.
- Coverage: conditional complete case.
- Scope: locality-derived country result.
- Country policy: mean of the two highest-scoring cities, minimum one.
- Status: ready, default-enabled, experimental.

The raw locality values range from 5.245% to 99.535%. The resulting country scores range from
1.21492 to 9.10702. Alternative top-one, top-three, all-five, population-weighted, and smaller
universe checks preserve rank correlation from 0.929469 to 0.988679. No existing non-locality
criterion has absolute Spearman correlation above 0.221166, and correlation with C66 is only
0.275754.

Adding C67 to the balanced preset keeps the same 83 eligible countries, changes 59 positions,
with mean movement 1.566 and maximum movement 7. This is meaningful but not dominating.

## Reproducibility

The worker uses the retained, ignored JRC archive with SHA-256
`966b96ef701a8b0053467179a1231ddc24830ac2693aadd7d1388f281795c0bb`.
Published release replay passed, with release checksum
`sha256:d68880bb8b366f74412df9894b4d38c89b4d9193a40134c87ab881cdca90426c`.

The machine-readable disposition is
`data/reports/phase5g-c67-2026-07-29/onboarding-disposition.json`.
