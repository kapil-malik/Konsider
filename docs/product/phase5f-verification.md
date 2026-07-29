# Phase 5F verification report

Status: implementation complete

Date: 2026-07-29

Scope: React migration to API v2, locality-aware presentation, structured assessment rendering,
responsive comparison, generated-contract checks, and browser verification

Production sources, active release, ranking rules, API version policy, and production C66 scoring
changed: no

## Delivered

The React client now uses `/api/v2` for catalog, ranking, comparison, and weight-contextual country
details. Requests use `preference_preset_id` or explicit `weights`; legacy Phase 4 profile aliases
are neither sent nor accepted by the generated TypeScript contract checks.

The UI renders coverage, locality, and applicant-profile assessments as three separate domains.
Coverage exclusions retain prominent eligibility wording and null aggregates. Locality assessments
remain advisory and explicitly state that they do not change the country affinity score.

Criterion controls show API-owned coverage counts, complete or limited coverage, national or
locality-derived scope, experimental state, and locality-analysis thresholds. A draft weight is
compared with the supplied threshold only to describe whether compatibility analysis will be
requested when applied; the browser does not determine the resulting status.

Country rows, mobile cards, details, and comparisons present server-supplied locality statuses,
contributor names and scores, best-common-locality identifiers resolved against supplied
contributions, aggregation policy, source lineage, periods, caveats, and unavailable reason codes.
The Data & Sources view includes scope, locality universe, aggregation, coverage, applicability,
experimental state, and historical criterion names. C66 is displayed as **Extreme heat exposure**
with **Extreme-weather risk** retained as its historical name when that catalog metadata is present.

## Browser authority boundary

The browser does not select top localities, calculate intersections, calculate a best common
locality, determine coverage/locality/profile statuses, adjust affinity scores, or infer applicant
constraints. `web/src/localityPresentation.ts` maps exact API statuses to copy and icons; it does
not derive those statuses.

Country-name/code search and region filtering remain presentation-only operations over the bounded
set of results already returned by the API.

## Test evidence

Component fixtures cover:

- no active locality criterion;
- one below-threshold locality criterion;
- one active locality criterion;
- common locality, partial overlap, no common locality, insufficient evidence, and mixed results;
- simultaneous coverage exclusion and locality advice;
- ranked and excluded country details;
- detailed national and locality-derived contributions;
- comparison aggregates, unavailable cells, locality evidence, and coverage exclusion; and
- structured API failures without runtime fixture fallback.

`web/src/api/generatedContractChecks.ts` proves at compile time that legacy `profile_id`,
`profiles`, duplicate root locality status, and flat city fields are rejected.

Playwright uses deterministic API-v2 mocks for eight desktop/mobile flows. It verifies that no v1
request is emitted, exercises locality evidence and coverage/locality separation, and checks a
390-by-844 comparison layout for document-width overflow.

## Visual evidence

The screenshots use the real active release `2026-07-28.2`. That release has no production locality
criterion yet, so the expected live locality state is **National evidence only**. Locality-active
states are verified with contract-faithful synthetic API-v2 responses and are not presented as
production data.

- [Desktop assessment domains](screenshots/phase5f-desktop.png)
- [Mobile country cards](screenshots/phase5f-mobile.png)

Visual inspection confirmed text-and-icon status cues, separate assessment cards, responsive
country cards, and no browser console warnings or errors.

## Final verification

| Command | Result |
| --- | --- |
| `pnpm run test --run --reporter=dot` | 15 passed |
| `pnpm run lint` | Passed |
| `pnpm run build` | Passed; TypeScript and Vite production build |
| `pnpm run e2e` | 8 passed |
| `python -m pytest tests/unit/test_documentation.py -q` | 5 passed |
| In-app browser, active release, desktop | Passed; no console warnings/errors |
| In-app browser, active release, 390-by-844 | Passed; responsive cards verified |

## Unresolved decisions and blockers

There is no active technical blocker for Phase 5F.

The choice to retire API v1, evolve API v2, or introduce a later contract version remains deferred
as requested. The UI intentionally uses the existing Phase 5E `/api/v2` contract.

Production C66 onboarding remains a Phase 5G decision and still requires the documented JRC
day-count versus pixel-count semantic clarification plus the other production data gates. The
active schema-4 release therefore continues to show the explicit no-active-locality-criterion
state; no fixture fills that production gap.
