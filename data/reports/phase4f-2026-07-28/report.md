# Phase 4F: Overall job-market opportunity onboarding

Status: production-onboarded in immutable release `2026-07-28.1`

## Frozen construct

- Source: International Labour Organization, ILOSTAT modelled estimates, November 2025 edition.
- Reference period: the 2025 cross-section only; 2026-2027 projections are excluded.
- Components: employment-to-population ratio, labour-force participation, and unemployment for
  total population age 15+.
- Transform: average-rank percentile per component, unemployment direction reversed, followed by
  an equal one-third mean.
- Scoring method: `job_market_equal_component_percentiles_v1`.

## Exact coverage

- Valid: 88/91.
- Missing: Antigua and Barbuda; Grenada.
- Stale: Ukraine (latest complete source year 2021).
- Coverage mode: `CONDITIONAL_COMPLETE_CASE`.
- Activation threshold: 0.6.

No observation or score is produced for a non-valid country. No imputation or country-specific
weight renormalisation is used.

## Interpretation boundary

The criterion measures broad, harmonised national labour-market utilisation. It does not measure
vacancies, wages, occupation-specific demand, credential recognition, work-visa access, or
city-level opportunity.

## Replay

The production parser uses the three retained, content-addressed raw artifacts listed in
`report.json`. The earlier online probe and exact offline replay are retained, and the published
release is replayed with the production parser and scoring implementation.
