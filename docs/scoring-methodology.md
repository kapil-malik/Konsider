# Scoring Methodology

Status: first real-data experiment

Last updated: 2026-07-17

Release `2026-07-17.1` uses version `winsorized_minmax_v1`. Scores are exploratory and are retained
beside raw observations; they are not replacements for the source values.

For each metric, the worker:

1. keeps only source-backed observations;
2. sorts the observed values for that metric;
3. uses the 5th and 95th percentile positions as clipping bounds;
4. maps the clipped value to a 1-10 score;
5. reverses the direction for lower-is-better metrics; and
6. records the input observation ID, method version, direction, bounds, and quality flags.

The current lower-is-better metrics are PM2.5 exposure, intentional homicide rate, and household
price level. UHC service coverage and WPS score are higher-is-better.

This method is intentionally modest. It is good enough to compare whether the worker can preserve
provenance and produce deterministic scores from real data. It is not yet a final policy model. The
next scoring work should compare threshold bands, percentile ranks, and sensitivity to country-set
composition before any live product consumes the scores.
