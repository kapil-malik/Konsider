# Phase 6I release verification evidence

Release `2026-08-04.1` is published, strictly validated, and selected by the atomic active pointer.
The build manifest in this directory records accepted upstream checksums, final payload checksums,
base-payload identity, and activation state. `performance.json` records the measured environment,
samples, thresholds, prior-release baseline, and passing result.

## Final local gates

| Gate | Result |
| --- | --- |
| Release schema/binding/checksums/matrix | passed |
| Final release byte regeneration | passed |
| Active locality replay | `replay=PASSED` |
| Prior-release ranking invariance | passed |
| Backend | 373 passed (243 unit, 130 integration) |
| Ruff / Black / compile | passed |
| OpenAPI / TypeScript regeneration | passed |
| TypeScript / ESLint / production build | passed |
| Vitest | 20 passed |
| Playwright Chromium | 10 passed |
| Performance and prior baseline | passed |

The [Phase 6 closure report](../../../docs/history/phase6-closure-report.md) records owner
decisions, exact state counts, compatibility, retained risks, rollback, and next-phase context.
