# Phase 2C responsive comparison UI

Status: implemented locally

The UI is a comparison and inspection surface over `/api/v1`, not a second recommendation engine.
It is implemented as one responsive React, TypeScript, and Vite application under `web/`.

## User experience

- A guest selects one of the server-owned provisional profiles or edits its five enabled priorities
  with accessible six-state controls.
- Draft changes do not affect results until **Apply priorities**. **Undo changes** restores the last
  successfully applied profile or custom weights.
- The ranking shows every API result in a bounded sticky-header desktop table or full-page mobile
  cards. Detailed mode adds one API-driven score for each enabled criterion.
- Selecting a country loads its enabled metric observations, period, public source, caveat, quality
  limitation, and scoring context.
- The UI selects two to four countries for comparison. The API remains capable of two to ten, but
  four is the deliberate Phase 2C presentation limit.
- The Guest menu and release indicator open a focus-managed **Data & Sources** view covering every
  available criterion, including non-ready UHC and experimental infrastructure.

## Authority and state

- FastAPI remains authoritative for profiles, readiness, normalization, canonical scores,
  contributions, ranking order, comparisons, and active release selection.
- Catalog source metadata is assembled from the validated active release source registry. Published
  release files are not modified.
- OpenAPI is exported and converted to generated TypeScript component types by
  `web/scripts/export_openapi.py`.
- TanStack Query owns API requests and caching. Local React state owns the current draft, last
  applied guest preference, view toggles, selections, and modal/menu state.
- The UI does not persist preferences, encode them in URLs, or provide product-data fixtures as a
  runtime fallback.

## Responsive and accessibility behavior

The same component hierarchy adapts from a two-column workspace on wide screens to stacked
priority controls, ranking cards, comparison sections, and full-width detail cards on mobile.
Semantic tables remain on desktop. Controls have visible keyboard focus and accessible labels;
sliders expose numeric and human values; dialogs trap and restore focus; status and errors are
announced; reduced-motion preferences are respected; zoom is not disabled.

## Verification

Component tests cover catalog rendering, readiness and experimental states, slider/profile behavior,
Apply/Undo requests, dynamic ranking detail, country evidence, comparison limits, guest help, empty
results, and structured/network errors. Playwright covers the main guest, update, detail, comparison,
source-help, unavailable-release, and mobile flows. Commands and local startup are documented in
[the web guide](../../web/README.md).

## Phase 2D scale status

Country search, API-derived region filters, filtered result counts, selected-country trays, and
100-country mobile verification are intentionally not implemented yet. The Phase 2D discovery gate
found only 91 complete countries across the full eligible universe, so there is no valid expanded
release to drive or verify those changes. The existing UI remains catalog-driven and continues to
serve the unchanged 20-country active release.
