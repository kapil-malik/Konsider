# Phase 2C UI plan

Status: constraints selected; implementation not started

The UI is a comparison and inspection surface over the existing API, not a second recommendation
engine. Final visual design remains open.

## Product scope

- Load `/api/v1/catalog` and build all country, criterion, profile, label, caveat, readiness,
  experimental, and source presentation from server data.
- Show five enabled weight controls and a ranked table of all 20 eligible countries.
- Keep UHC visible only where an unavailable/non-ready catalog explanation is useful; never offer it
  as an enabled ranking weight.
- Label infrastructure as experimental wherever it influences or appears in results.
- Show country detail with canonical score, raw observation, unit, reference period, source link,
  attribution, caveats, quality limitations, and method versions.
- Support comparison of 2-10 unique countries while preserving requested order.
- Keep edited weights in browser memory during Phase 2C. No account or durable profile exists.

## Technical constraints

- React + TypeScript + Vite.
- TanStack Query for API/server state; local React state for editable weights.
- Generate TypeScript types from `/openapi.json` or validate runtime payloads against equivalent
  generated schemas. Do not maintain hand-written business-shape guesses.
- Use only `/api/v1`; configure the base URL through a browser-safe Vite environment variable.
- Never calculate canonical scores, readiness, profiles, strengths, trade-offs, or ranking order in
  the frontend. Submit weights and render API results.
- Preserve release ID while results are visible so catalog and ranking snapshots cannot be confused.

## Required states

- Initial catalog and ranking loading.
- Empty or temporarily absent results.
- Controlled `503` unavailable-release screen with retry.
- Structured validation and API errors without leaking internals.
- Network failure and stale-request cancellation when weights change rapidly.
- No enabled criteria guard, even though the current catalog has five.

## Accessibility and responsive behavior

- Every weight input needs a visible label, numeric value, keyboard operation, and programmatic name.
- Readiness and experimental status cannot rely on color alone.
- Tables need semantic headers; narrow screens may use an accessible card/list alternative without
  hiding provenance or ranking meaning.
- Focus must move predictably for dialogs/details and error summaries. Respect reduced motion.
- Source links must identify destination and open behavior.

## Testing

- Vitest and React Testing Library: catalog-driven rendering, five enabled controls, UHC state,
  experimental labels, weight edits, loading/empty/error states, and accessible interactions.
- Contract fixtures generated from or validated against OpenAPI.
- Playwright: one initial ranking flow, one weight update, one country detail, one comparison, and one
  unavailable-release path.
- Tests must fail if the frontend hard-codes the active release ID, country list, criterion list, or
  ranking output.

See [API reference](../operations/api.md), [local deployment](../operations/deployment-local.md), and
[ADR 004](../architecture/decisions/004-react-vite-ui.md).
