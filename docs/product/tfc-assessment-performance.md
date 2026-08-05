# Phase 7E TFC assessment performance

Status: synthetic local measurement

Date: 2026-08-05

## Workload

The benchmark uses `stable_supported_v1` with all 91 countries, three synthetic route/rule checks,
one synthetic scenario metric, multiple routes in the supported destination, explicit unsupported
rows elsewhere, immutable source/policy artifacts, assessment assembly, schema validation and a
non-persisted scenario snapshot.

This intentionally exceeds the approved first-wave execution count by adding the synthetic metric
alongside three route checks. It does not measure API serialization, network calls or persistence;
none are part of Phase 7E.

## Result

Command:

```powershell
python scripts\benchmark_phase7e_tfc_engine.py --iterations 30
```

Measured on the local Windows development environment:

| Measure | Result |
|---|---:|
| Iterations | 30 |
| Countries | 91 |
| Route TFCs | 3 |
| Metric TFCs | 1 |
| Median | 179.867 ms |
| p95 | 291.118 ms |
| Maximum | 365.602 ms |

The focused test also requires the same 91-country/four-check workload to complete below a broad
2,000 ms safety ceiling, avoiding hardware-sensitive microbenchmark failures. Rule growth remains
bounded by explicit TFC-country support and referenced route IDs; the engine never scans a live
source or precomputes profile-country combinations.

Future optimization should be driven by Phase 7G request-level measurements. Candidate areas are
prevalidated immutable indexes and avoiding repeated response-schema validation, not weakening
effective-date, conflict, support-completeness or privacy checks.
