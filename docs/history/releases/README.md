# Release history

Release reports preserve the context, validation result, and known limitations of immutable
published artifacts. Manifests and payloads under `data/releases/` are authoritative if a report
ever disagrees.

| Release | Historical role | Report |
| --- | --- | --- |
| `2026-07-17.1` | Experimental first real-data baseline. | [Report](2026-07-17.1.md) |
| `2026-07-18.2` | Stabilized schema-v2 baseline; product gate blocked. | [Report](2026-07-18.2.md) |
| `2026-07-20.2` | Schema-v3 six-criterion publication; five criteria ready. | [Report](2026-07-20.2.md) |
| `2026-07-21.1` | Active LF packaging correction. | [Report](2026-07-21.1.md) |

`2026-07-21.1` exists separately because `2026-07-20.2` checksummed CRLF working-tree bytes while
Git stores LF blobs. The correction preserves parsed observations, scores, attempts, readiness,
scoring behavior, and API contracts but uses portable LF payload checksums. The old release remains
immutable and must not be silently rewritten.

`data/releases/active.json` currently selects `2026-07-21.1`. Historical releases are not current
operational references. See [release format](../../data/release-format.md) and the
[worker guide](../../operations/worker.md).
