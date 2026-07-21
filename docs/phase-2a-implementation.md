# Phase 2A implementation and verification

Status: complete on 2026-07-20

Phase 2A adds a framework-independent consumer for active published real-data releases. The
consumer catalog is separately versioned so release `2026-07-20.2` and its checksum manifest remain
immutable. Catalog criteria and readiness must exactly match the active release before data is
served.

## Data boundaries

- `observations.jsonl` contains source-backed raw observations, units, periods, and record lineage.
- `scores.jsonl` contains versioned normalized 1-10 criterion scores linked to observation IDs.
- User-specific contributions are calculated at request time as score times normalized weight.
- Final country rankings sum those contributions and break equal totals by ascending ISO-3 code.

The normal repository view contains 20 countries times five ready criteria. UHC exists in the
catalog and diagnostic/read-only view but is excluded from normal records and rejected as a weight.
Infrastructure remains visibly experimental.

## Verification

The automated suite covers valid and malformed schemas, schema-major rejection, checksum tampering,
duplicate scores, missing observations, broken source lineage, readiness reconciliation, the full
100-pair enabled matrix, deterministic ranking, weight edge cases, cost-band ties, comparison and
breakdown services, future freshness, and World Bank query ranges. Published-release replay remains
separate because it requires ignored local raw artifacts.

Run:

```powershell
python -m pytest -q
python -m ruff check .
python -m black --check .
python -m compileall -q src tests
python -m konsider.ingestion.worker replay data\releases\2026-07-20.2
```
