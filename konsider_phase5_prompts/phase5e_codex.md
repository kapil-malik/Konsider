# Phase 5E — Candidate-Specific Measured Probes

## Intended for
Codex in the local Konsider repository.

## Inputs
- completed Phase 5D framework
- completed Phase 5C reports
- user-approved source candidates

## Prompt

Implement deterministic feasibility probes for the approved source candidates and measure their actual suitability for the stable 91-country universe.

For each candidate:

1. Use the exact approved dataset, series, table, API, or workbook.
2. Capture raw artifacts, versions, URLs, methodology, and licence evidence.
3. Map source identities to the canonical country registry.
4. Produce one expected result per country.
5. Record success, missing, stale, parse-failed, invalid, rejected, and unmapped outcomes explicitly.
6. Apply the proposed criterion-specific freshness rule without changing production policy.
7. Calculate found, fresh, parsed, validated, missing, stale, invalid, and unmapped counts.
8. Identify excluded and only-blocker countries where meaningful.
9. Support offline replay where possible.
10. Compare measured results with Phase 5C expectations.

These remain research probes. Do not publish a release, add production scoring, impute values, silently substitute indicators, or combine sources unless explicitly approved.

For each candidate produce machine-readable per-country results, raw-artifact inventory, Markdown summary, exact coverage statistics, licensing conclusion, and recommendation: production candidate, experimental candidate, reserve candidate, or reject.

Also produce an aggregate comparison report.
