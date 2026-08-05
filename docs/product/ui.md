# Responsive ranking, Opportunity Filter, and comparison UI

Status: Phase 7H guest-first situation and feasibility UI implemented

The UI is a comparison and inspection surface over `/api/v2`, not a second recommendation engine.
It is implemented as one responsive React, TypeScript, and Vite application under `web/`.

## User experience

- A guest selects one of the server-owned preference presets or edits its enabled priorities
  with accessible six-state controls.
- A separate **Opportunity filters** section groups five career and four education/research-
  university signals. Checkbox selection is strict: every selected filter is required.
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
  Opportunity Filter definitions/states/evaluation, locality selection and overlap, and active
  release selection.
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
91-country mobile long-list flows, plus Opportunity Filter selection, exclusions, evidence,
comparison and mobile behavior. Commands and local startup are documented in
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

## Phase 5H contract finalization

The UI has one transport contract: generated `/api/v2` component types. Handwritten aliases for
the retired Phase 3/4 payloads and runtime fallbacks for old field names have been removed.
`preference_presets` is the only catalog preset collection, and requests use
`preference_preset_id`. Coverage, locality, and profile applicability render only from their
separate structured assessments. With no applicant profile input, every profile assessment is
explicitly `NO_PROFILE_CONTEXT`, has no evaluated dimensions, and carries a `NOT_EVALUATED`
reason. The compile-time negative checks are retained as tests, not production compatibility code.

## Phase 6H Opportunity Filter experience

Opportunity Filters are presented as optional destination evidence, visibly separate from weighted
ordering priorities. The UI renders the nine available definitions from
`GET /api/v2/opportunity-filters`; it does not hard-code availability or derive filter states. Five
career filters and four education/research-university filters appear in independently collapsible
groups. They use checkboxes only—there are no Opportunity Filter weights, sliders, score controls,
or alternate combination modes.

Draft filter changes share the existing **Apply priorities** and **Undo changes** transaction with
preference changes. Applied requests send sorted IDs under `opportunity_filters` with
`mode: ALL_REQUIRED`. Active chips remove one filter or all filters while preserving the applied
preference preset or weights. Removing a filter never silently changes a weight, and the service
never auto-relaxes a zero-match selection.

The result summary distinguishes:

- **Verified strong signal**: the filter passes;
- **Strong signal not established**: comparable evidence was assessed but did not cross the frozen
  strong-ecosystem threshold; and
- **Insufficient evidence**: comparable evidence is not adequate to reach either conclusion and is
  not negative evidence.

Filtered rows preserve the API affinity score and show filtered rank, base rank, and one compact
selected-filter summary rather than adding nine table columns. A collapsible exclusion inspector
shows every excluded country, its base rank, each failing filter and its exact public state. A
zero-match result is a valid non-error state with current counts and explicit remove-filter actions;
the unfiltered ranking is never substituted automatically.

Country details show selected-filter state, confidence, reference period, establishing route,
sources/version/attribution, limitations, and methodology reference. Skilled-trades/construction
evidence identifies skilled trades, construction, or both. Care-sector wording is limited to human
health and social work; finance wording is limited to finance and insurance. Education evidence is
labelled as a research-university ecosystem and repeats the shared limitation that it does not
establish teaching quality, programme availability, admission access, affordability, accreditation,
or applicant eligibility. Comparison views retain these filters as a separate evidence domain and
preserve an opportunity-excluded country's canonical score and base rank.

Desktop retains the compact sticky ranking table. At 760px and below the filter groups, result
counts, evidence cards, and comparison content stack into full-width cards; the nine-filter grid is
never presented as a mobile table. Controls meet the existing large-target convention, native
checkbox and disclosure semantics remain keyboard-operable, every color state also has text and an
icon, and focus/status behavior uses the existing accessible patterns. No one-off analytics hook was
added because this codebase has no established product-analytics convention.

See the [Phase 6H test plan](phase6h-opportunity-filter-ui-test-plan.md) and
[implementation report](../history/phase6h-opportunity-filter-ui.md). The UI is verified against
the staged nine-filter API candidate; it does not activate that candidate or change
`data/releases/active.json`.

## Phase 7H guest situation and feasibility experience

The ranking remains the first screen and works without profile context. A compact applied-context
strip keeps four concepts separate: ordering priorities, Opportunity Filters, the active local
scenario and explicitly selected feasibility checks. **Add your situation** opens a guided modal;
no permanent profile form competes with ranking controls.

The flow asks purpose first, then shows API-catalogued checks relevant to that purpose without
selecting any automatically. After the guest selects checks, the details step renders only their
declared input requirements and field-registry help/sensitivity labels. Applicant and household
facts are shared across up to three named browser-local scenarios; purpose, destinations, date,
offer, route and study assumptions stay scenario-specific. Scenarios can be added, duplicated,
removed and switched. Unknown values remain explicit and may produce `INPUT_REQUIRED`.

**Save and assess** is the only action that submits the draft. Requests use generated API v2 types,
sorted TFC IDs and `ASSESS_ONLY`; the first-wave policies do not expose a feasibility filter. The
browser does not implement route, eligibility, support or metric rules. Catalog failure disables
only the situation flow, leaving legacy ranking available.

Feasibility is a sibling presentation to affinity, coverage, locality, profile and Opportunity
evidence. Ranking summaries show selected checks, evaluation/input-required counts, unchanged-
affinity wording and scenario snapshot metadata. Country details show route conditions, sources,
effective dates, limitations and metric assumptions/ranges. Comparison sends the same explicit
selection and keeps one feasibility row/card per check alongside, rather than inside, ordering or
Opportunity evidence.

Tab-scoped session storage is the default. Device storage is an explicit unchecked opt-in with a
30-day expiry, version invalidation, shared-device caution and independent clear control. Clear
current is confirmed separately. Export produces versioned JSON without assessment results,
citizenship or household details; import validates and previews before use. Profile values never
enter URLs, analytics or server persistence.

The modal traps focus, closes on Escape, restores the invoking control, uses native labelled
controls and text-plus-icon status, and becomes a full-screen surface at 760px and below. See the
[Phase 7H test plan](phase7h-guest-profile-ui-test-plan.md) and
[implementation report](../history/phase7h-guest-profile-ui.md).

## Phase 7I cross-feature experience

Combined views keep their evidence domains in a stable reading order: affinity and base rank,
coverage, locality, Opportunity evidence, feasibility, then assumptions or missing information.
Six bounded templates explain useful disagreements, such as a strong ecosystem with unresolved
personal access or a route match with a locality trade-off. They never synthesize a new status or
alter any underlying result.

Country details place the combined explanation between Opportunity and feasibility evidence.
Comparison preserves one scenario snapshot and keeps Opportunity evidence and each selected TFC in
separate rows or mobile sections. Expanded TFC evidence includes route or metric effective dates,
source IDs and catalog review dates; an unavailable metric remains unavailable and is never shown
as zero. Base and filtered ranks remain distinct.

Desktop and mobile use the same data and explanation order. At the mobile breakpoint the visible
comparison cards, disclosures and evidence metadata fit without horizontal overflow; the hidden
desktop table is not treated as the accessible representation. See the
[cross-feature behavior guide](tfc-cross-feature-behavior.md),
[scenario matrix](phase7i-scenario-matrix.md) and [Phase 7I UI test plan](phase7i-ui-test-plan.md).
