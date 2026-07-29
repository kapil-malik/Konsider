# Responsive locality-aware ranking and comparison UI

Status: Phase 5F implemented locally

The UI is a comparison and inspection surface over `/api/v2`, not a second recommendation engine.
It is implemented as one responsive React, TypeScript, and Vite application under `web/`.

## User experience

- A guest selects one of the server-owned preference presets or edits its enabled priorities
  with accessible six-state controls.
- Draft changes do not affect results until **Apply priorities**. **Undo changes** restores the last
  successfully applied profile or custom weights.
- The ranking shows every API result in a bounded sticky-header desktop table or full-page mobile
  cards. Detailed mode adds one API-driven score for each enabled criterion.
- Country-name/ISO search and an API-result-derived region filter keep all 91 countries accessible.
  The footer announces visible and total result counts, including explicit no-match states.
- Selecting a country loads its enabled metric observations, period, public source, caveat, quality
  limitation, and scoring context.
- The UI selects two to four countries for comparison. The API remains capable of two to ten, but
  four is the deliberate Phase 2C presentation limit.
- The Guest menu and release indicator open a focus-managed **Data & Sources** view covering every
  available criterion, including non-ready UHC and experimental infrastructure.

## Authority and state

- FastAPI remains authoritative for preference presets, readiness, normalization, canonical scores,
  contributions, ranking order, comparisons, structured coverage/locality/profile assessments,
  locality selection and overlap, and active release selection.
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
Apply/Undo requests, search, region filtering, result counts, dynamic ranking detail, country
evidence, comparison limits, guest help, empty results, and structured/network errors. Playwright
covers the main guest, update, filtering, detail, comparison, source-help, unavailable-release, and
91-country mobile long-list flows. Commands and local startup are documented in
[the web guide](../../web/README.md).

## Phase 2D scale status

Phase 2D is complete. The catalog-driven UI serves the active release with 91 countries,
bounded desktop scrolling, complete mobile cards, search, region filtering, visible/total counts,
details, comparisons, sources, and an always-visible release ID. No server pagination or
virtualization was needed for the measured response and rendering size.

## Phase 4G uncertainty-aware ranking

The UI renders the Phase 4E API's coverage and robustness decisions without calculating scores,
eligibility, missing-country unions, optimistic bounds, or statuses in the browser.

- Every priority shows its exact `valid/stable countries` coverage. Conditional criteria use a
  calm **Limited coverage** badge, state that Medium is the activation point, and visibly indicate
  whether the current draft setting is active.
- The result summary always shows ranked-of-stable countries, active limited-coverage criteria,
  excluded-country count, uncertainty state, and robustness K.
- `ROBUST_TOP_K` is informational, `POTENTIALLY_AFFECTED` is a prominent caution, and
  `BASELINE_TOP_K_EXCLUDED` and `COVERAGE_LIMIT_EXCEEDED` receive the strongest treatment. Icons and
  text accompany every colour treatment.
- Excluded countries remain outside the conditional ranking. A collapsible section shows their R0
  rank, baseline boundary membership, unavailable criteria and reason codes, optimistic upper
  bound, and potential-entry result.
- Opening an excluded country shows available national evidence and **Not ranked for this
  profile**. No affinity score is fabricated.
- When a partial-coverage criterion is active, **View full-coverage baseline** requests a second
  server ranking with conditional criteria disabled and `top_k` equal to the stable universe. The
  browser does not derive baseline scores or order. R1 remains the default view.
- Comparisons use the API's criterion matrix and country summaries. Missing, stale, invalid, and
  rejected cells show an em dash plus an accessible availability explanation. Available cells
  remain comparable, while an ineligible country column is labelled and has no aggregate score.

### Documented visual states

| API state | Visual treatment |
| --- | --- |
| `NO_PARTIAL_CRITERIA_ACTIVE` | Compact neutral full-coverage notice; no baseline control or exclusion list. |
| `FULL_COVERAGE` | Neutral confirmation; active PCC names remain visible. |
| `ROBUST_TOP_K` | Mild teal information panel and expandable excluded-country evidence. |
| `POTENTIALLY_AFFECTED` | Amber caution explaining that excluded countries could enter top K. |
| `BASELINE_TOP_K_EXCLUDED` | Strong outlined warning and baseline-boundary badge on affected countries. |
| `COVERAGE_LIMIT_EXCEEDED` | Strong warning; FCC-only table explicitly labelled as the baseline. |

Desktop uses the existing sticky ranking table and four-column summary. At 760px and below, the
summary becomes two columns, warnings and baseline controls stack, the table becomes full-featured
country cards, excluded diagnostics collapse to one column, and comparison evidence becomes
criterion cards. Browser QA covered the default desktop viewport and a 390-by-844 mobile viewport
with no horizontal document overflow.

Component fixtures cover all six statuses, zero/one/many excluded-country structures,
baseline-toggle/API behavior, PCC/experimental/unavailable badges, missing comparison cells,
unranked evidence access, and accessible status names.

Phase 4 closure confirms that the UI treats the stable catalog, eligible universe, R0, R1, and
robustness status as distinct API-owned concepts. It does not infer eligibility from blank cells or
calculate partial country totals. City, occupation, household, visa, licensing, and
applicant-specific suitability remain outside this interface.

## Phase 5F locality-aware presentation

The UI now consumes the structured Phase 5 API directly. Coverage, locality, and applicant-profile
assessments are rendered as separate domains so a locality advisory never implies that a country was
excluded. Country rows and cards show the server-supplied locality status, contributing locality
names, and best common locality when present. A no-common-locality advisory explicitly says the
country affinity score is unchanged.

Criterion controls show coverage, national or locality-derived scope, experimental state, and the
server-supplied locality-analysis threshold. Draft weights are compared only with that supplied
threshold to explain whether the next applied request will ask the server for compatibility
analysis. Low locality weights retain a quiet provenance marker without a prominent coherence
warning.

Expanded criterion evidence and country details distinguish direct national results,
locality-derived country results, and unavailable active criteria. Locality contributions include
the country score, contributor names and scores, aggregation policy, source lineage, reference
period, and caveats. Comparison cards and tables retain those distinctions and leave
coverage-excluded aggregates blank.

The browser does not select localities, compute intersections, derive a best common locality,
determine assessment statuses, alter affinity scores, or infer applicant constraints. Compile-time
contract checks reject legacy Phase 4 request and response fields, and Playwright verifies the
`/api/v2` request path on desktop and mobile.
