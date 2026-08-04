# Release history

Release reports preserve the context, validation result, and known limitations of immutable
published artifacts. Manifests and payloads under `data/releases/` are authoritative if a report
ever disagrees.

| Release | Historical role | Report |
| --- | --- | --- |
| `2026-07-17.1` | Experimental first real-data baseline. | [Report](2026-07-17.1.md) |
| `2026-07-18.2` | Stabilized schema-v2 baseline; product gate blocked. | [Report](2026-07-18.2.md) |
| `2026-07-20.2` | Schema-v3 six-criterion publication; five criteria ready. | [Report](2026-07-20.2.md) |
| `2026-07-21.1` | LF packaging correction and prior 20-country release. | [Report](2026-07-21.1.md) |
| `2026-07-24.1` | Stable 91-country Phase 2D predecessor. | [Report](2026-07-24.1.md) |
| `2026-07-26.3` | Immutable Windows-packaging artifact; invalid after Git LF normalisation. | [Report](2026-07-26.3.md) |
| `2026-07-27.1` | LF-packaged schema-v3 Phase 3 baseline. | [Report](2026-07-27.1.md) |
| `2026-07-28.1` | Schema-v4 release; first conditional criterion. | [Report](2026-07-28.1.md) |
| `2026-07-28.2` | Schema-v4 Wave 2 release; three conditional criteria. | [Report](2026-07-28.2.md) |
| `2026-07-29.1` | First schema-v5 production locality criterion (C66). | [Report](2026-07-29.1.md) |
| `2026-07-29.2` | Prior schema-v5.0 release; second production locality criterion (C67). | [Report](2026-07-29.2.md) |
| `2026-08-04.1` | Active schema-v5.1 release; nine filter-only Opportunity Filters. | [Report](2026-08-04.1.md) |

`2026-07-21.1` exists separately because `2026-07-20.2` checksummed CRLF working-tree bytes while
Git stores LF blobs. The correction preserves parsed observations, scores, attempts, readiness,
scoring behavior, and API contracts but uses portable LF payload checksums. The old release remains
immutable and must not be silently rewritten.

`2026-07-27.1` applies the same packaging correction to `2026-07-26.3`. All seven payload checksums
in the old manifest describe pre-normalised Windows bytes rather than the committed LF blobs. The
successor was rebuilt from the retained raw artifacts and preserves observations, scores, attempts,
sources, sensitivity results, readiness, and API behavior.

`data/releases/active.json` currently selects `2026-08-04.1`. Historical releases are not current
operational references. See [release format](../../data/release-format.md) and the
[worker guide](../../operations/worker.md).
