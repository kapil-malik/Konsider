# Phase 7J release verification

Status: PASSED

## Publication

```powershell
python -m konsider.ingestion.phase7_release_publication build
python -m konsider.ingestion.phase7_release_publication publish
python -m konsider.ingestion.phase7_release_publication replay
python -m konsider.ingestion.phase7_release_publication activate
```

Result: release `2026-08-05.1` is a published, non-synthetic, activation-authorized schema-6.0
overlay on immutable base `2026-08-04.1`. Draft and published replay reported `PASSED` with zero
mismatched files. The Phase 7F source capture also replayed with zero mismatches.

## Gates

- Three owner-approved TFC IDs and no others.
- Every policy is `ASSESS_ONLY` and `NOT_FILTERABLE`.
- 273 explicit support records: 29 `SUPPORTED` and 62 `UNSUPPORTED` per TFC.
- Phase 7B reconciliation: `PASSED`.
- Deferred licensing and metric candidates: absent.
- Ranking, PCC, locality and Opportunity Filter outputs: invariant under TFC assessment.
- Submitted profile values: absent from URLs, responses and captured logs.
- API POST cache policy: `private, no-store` with no-cache compatibility headers.

## Verification commands

```powershell
python -m pytest
python -m ruff check .
python -m black --check .
python -m compileall -q src tests scripts
python scripts/export_openapi.py --check
pnpm --dir web typecheck
pnpm --dir web lint
pnpm --dir web test -- --run
pnpm --dir web build
pnpm --dir web e2e
python scripts/verify_ci.py --clean-revision HEAD
```

Working-tree result: 473 backend tests, 37 frontend unit tests and 14 browser tests passed; all
static, contract-generation and build checks passed. The final clean-revision result is appended
after the release and documentation commits are created.

## Rollback drill

```powershell
python -m konsider.ingestion.phase7_release_publication rollback --release-id 2026-08-04.1
python -m konsider.ingestion.phase7_release_publication activate --release-id 2026-08-05.1
```

The automated integration test validates both pointer transitions and repository loading. The
production pointer was not left on the rollback target; it selects `2026-08-05.1`.
