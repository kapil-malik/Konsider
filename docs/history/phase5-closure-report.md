# Phase 5 closure report

Status: complete locally; ready for remote CI confirmation

Date: 2026-07-29

Active release: `2026-07-29.2`

Release/catalog/API: `konsider-release-5.0` / `consumer-catalog-3.0` /
`konsider-api-2.0`

## Executive outcome

Phase 5 added locality evidence without turning Konsider into a city-ranking product or weakening
complete-case country ranking. Coverage, evidence scope, and applicant applicability are separate
dimensions. A criterion can therefore be national or locality-derived independently of being
global-core, conditional complete-case, or diagnostic.

Two experimental Locality-Specific Criteria are production-onboarded:

- C66 **Extreme heat exposure**; and
- C67 **Projected warm-day frequency (2030)**.

Both are locality-derived PCCs with valid results for 89/91 countries. Antigua and Barbuda and
Grenada have no qualifying locality and remain explicit missing outcomes. No city, country, or
criterion value is imputed.

The public runtime now has one clean path:

```text
active.json
    -> schema-5 CurrentReleaseRepository
    -> structured RecommendationService
    -> five /api/v2 routes
    -> generated TypeScript contract
    -> React UI
```

Historical schema-3/4 releases remain immutable and inspectable through an explicitly selected
internal historical loader. They are not an alternate active API.

## Architecture outcome

Phase 5 delivered:

- orthogonal criterion `coverage`, `scope`, and `applicability` metadata;
- canonical country and locality entities with source IDs and parentage;
- entity-neutral observations and scores;
- one explicit outcome per country and criterion;
- versioned locality universes, criterion policies, aggregation policies, and source lineages;
- deterministic locality-derived country evidence;
- independent country opportunity as the ranking interpretation;
- separate common-locality analysis that never changes the country aggregate by default;
- structured coverage, locality, and profile assessments;
- preference-preset terminology reserved from future applicant-profile terminology;
- a native schema-5 API/UI path with all temporary Phase 5 compatibility removed; and
- deterministic publication and replay through the generic release foundation.

ADRs 005-009 hold the binding architecture decisions. The
[Phase 5H migration report](../product/phase5h-contract-migration.md) records the final removed
surface.

## Reviewable delivery sequence

| Phase | Commit | Intent |
| --- | --- | --- |
| 5A | `8980add` | Complete locality-criterion discovery |
| 5B | `d2fdeba` | Define locality and structured-assessment contracts |
| 5C | `3325d98` | Generalize immutable releases and geography |
| 5D | `0cf1c41` | Add deterministic locality aggregation and assessment |
| 5E | `9102719` | Expose structured API v2 |
| 5F | `3e99b7d` | Render locality-aware rankings and evidence |
| 5G preparation | `dba0c70` | Record C66 onboarding blockers |
| 5G C66 | `aa1a072` | Onboard Extreme heat exposure |
| 5G C67 | `5efbe52` | Onboard Projected warm-day frequency (2030) |
| 5H | `c4870ef` | Finalize the structured public contract |
| 5I verification | `f4a01d7` | Verify the Phase 5 closure matrix |
| 5I closure | closure commit | Publish the authoritative closure and roadmap |

## Phase 5A disposition of all 45 criteria

The complete row-level matrix remains authoritative at
`data/reports/phase5a-2026-07-28/criterion-disposition-matrix.json`.

| Phase 5A disposition | Initial count | Final Phase 5 state |
| --- | ---: | --- |
| First wave | 1 | C66 onboarded experimentally |
| Second wave | 3 | C67 narrowed and onboarded; C05 and C68 held |
| Research only | 7 | All seven held |
| Future profile phase | 21 | All 21 held for typed applicant/household context |
| Reject locality proxy | 13 | Remain national or rejected as locality-derived proxies |
| **Total** | **45** | Every criterion has one documented disposition |

The seven research-only locality candidates are C11 Overall job-market opportunity, C16
Entrepreneurship and startup opportunity, C42 Social inclusion and acceptance of immigrants, C50
Healthcare system capacity and quality, C56 Electricity access and reliability, C57 Water-supply
reliability, and C58 Internet access, speed, and reliability.

The current strongest fast follow is C05 Research and innovation ecosystem, but it still needs a
pinned OpenAlex snapshot workflow, institution-to-locality identity mapping, field-normalized
bibliometrics, and a decision about coexistence with the current national WIPO criterion. C68
Natural-disaster risk remains weaker because the available occurrence data end in 2015 and do not
measure severity, vulnerability, or expected loss.

Occupation-specific jobs, institution/education questions, housing, earnings, visa access, and
professional licensing remain valuable product questions. They were held because answering them
honestly needs typed applicant, qualification, institution, household, or licensing context—not
because locality is unimportant.

## Active release inventory

Release `2026-07-29.2` is published, product-ready, and checksum-valid.

| Inventory | Count |
| --- | ---: |
| Stable countries | 91 |
| Selected urban centres | 388 across 89 countries |
| Canonical geographic entities | 479 |
| Catalog criteria | 14 |
| Ready/enabled criteria | 13 |
| Global-core criteria | 8 |
| Conditional complete-case criteria | 5 |
| Diagnostic-only criteria | 1 |
| Locality-derived criteria | 2 |
| Country/criterion outcomes | 1,274 |
| Observations | 2,034 |
| Scores | 2,034 |
| Derived country evidence rows | 178 |
| Source lineages | 15 |

The 13 enabled criteria are:

1. Extreme heat exposure;
2. Projected warm-day frequency (2030);
3. Population-weighted PM2.5 exposure;
4. Established immigrant presence;
5. Broad household-consumption relative cost;
6. Infrastructure readiness;
7. Intentional homicide rate;
8. Overall job-market opportunity;
9. Political stability;
10. Research and innovation ecosystem;
11. Rule of law;
12. School education quality; and
13. Women's legal and economic equality.

UHC service coverage remains diagnostic-only and cannot be weighted.

## Coverage and ranking

The eight global-core criteria have 91/91 valid country outcomes. Conditional coverage is:

| Criterion | Valid countries | Missing/stale |
| --- | ---: | --- |
| Overall job-market opportunity | 88/91 | 2 missing, 1 stale |
| School education quality | 88/91 | 3 unavailable |
| Research and innovation ecosystem | 85/91 | 6 unavailable |
| Extreme heat exposure | 89/91 | ATG and GRD: no qualifying locality |
| Projected warm-day frequency (2030) | 89/91 | ATG and GRD: no qualifying locality |

PCCs activate at raw weight `0.6`. The engine uses one normalized vector for every eligible
country, excludes any country missing an active criterion, and never emits a partial aggregate.
Coverage-limit fallback returns the FCC ranking when the conditional eligible universe is too
small. Excluded countries retain evidence but no final score.

## Locality universe and aggregation

Both onboarded LSCs use `ghsl-ucdb-top5-population-v1`:

- source: GHS-UCDB R2024A V1.2;
- qualifying urban-centre population: at least 50,000;
- selection: up to five centres per country;
- ordering: frozen 2025 population descending, then source entity ID;
- selection performed before criterion values are inspected;
- 388 centres selected across 89 countries; and
- no synthetic capital or fallback locality for ATG or GRD.

Each criterion uses a versioned top-two mean policy with minimum one qualifying locality. All valid
locality evidence remains stored and inspectable even though only the two strongest opportunity
scores contribute to the country result.

The product meaning is “this country contains strong major-locality options,” not national average
resident exposure. When several active LSCs favor different places, their independent country
scores remain unchanged. The API separately reports common locality, partial overlap, no overlap,
or insufficient evidence. Common-locality search uses every valid locality, including localities
outside displayed top-N contributors.

Raw weight `0.6` activates prominent locality-coherence analysis. Positive FCC locality weights
below that threshold still contribute and retain provenance. PCC activation remains a separate
coverage decision even where both thresholds currently equal `0.6`.

## Onboarded constructs and source gates

### C66 Extreme heat exposure

C66 is the annual mean number of days in 2011-2020 when daily maximum UTCI exceeded 32°C. The JRC
field is `CL_UTC_T32_2020`. Its exact JRC asset is CC BY 4.0. A visible disclaimer records that one
publisher methodology sentence says “pixels” even though the indicator name, unit, upstream
variable, and measured range support the approved day interpretation.

### C67 Projected warm-day frequency (2030)

C67 is the projected percentage of days in 2021-2030 when daily maximum temperature exceeds the
calendar-day 90th percentile relative to 1961-1990, using EC-Earth3 under SSP2-4.5. The field is
`CL_WDS_245_2030`. It is not total climate risk, observed future weather, an absolute heat
threshold, or a multi-model uncertainty estimate.

Both criteria passed separate construct, exact-asset, coverage, scoring, sensitivity, licensing,
lineage, product-value, validation, and replay gates. Exact raw bytes remain locally retained but
ignored by Git; the committed release retains checksums and complete source metadata.

## API contract

The public API exposes exactly:

- `GET /api/v2/health`;
- `GET /api/v2/catalog`;
- `POST /api/v2/rankings`;
- `POST /api/v2/comparisons`; and
- `POST /api/v2/countries/{country_code}/details`.

Ranking, comparison, and details responses keep `assessments.coverage`,
`assessments.locality`, and `assessments.profile` structurally separate. Country rows contain their
own locality and profile assessments without duplicating ranking-wide coverage state.

With no applicant input, profile assessment is always `NO_PROFILE_CONTEXT`, evaluates no
dimensions, and carries a `NOT_EVALUATED` reason. Preference presets are weight presets only and
use `preference_presets`, `preference_preset_id`, and `resolved_preference_preset_id`.

## Assessment statuses

Coverage statuses:

- `NO_PARTIAL_CRITERIA_ACTIVE`;
- `FULL_COVERAGE`;
- `PARTIAL_COMPLETE_CASE`; and
- `COVERAGE_LIMIT_FALLBACK`.

Locality statuses:

- `NO_ACTIVE_LOCALITY_CRITERIA`;
- `BELOW_ANALYSIS_THRESHOLD`;
- `ONE_ACTIVE_LOCALITY_CRITERION`;
- `COMMON_LOCALITY_AVAILABLE`;
- `PARTIAL_OVERLAP`;
- `NO_COMMON_LOCALITY`;
- `INSUFFICIENT_LOCALITY_EVIDENCE`; and
- `MIXED_COUNTRY_RESULTS`.

Profile status in Phase 5 is only `NO_PROFILE_CONTEXT`.

## UI outcome

The React UI consumes generated API-v2 types and does not calculate ranking, normalization,
coverage eligibility, locality aggregation, intersections, best-common locality, or assessment
statuses. It shows:

- coverage, scope, applicability, readiness, experimental state, and thresholds;
- ranked and excluded countries without fabricated aggregates;
- contributor localities, observations, periods, policies, lineages, sources, and caveats;
- separate coverage, locality, and profile explanations;
- comparisons with explicit unavailable cells;
- Data & Sources metadata;
- desktop tables and complete mobile cards; and
- controlled loading, empty, error, and unavailable-release states.

## Removed compatibility surface

Phase 5H removed:

- every public `/api/v1` route;
- the schema-4 active adapter and legacy mapper;
- `legacy-active.json`;
- the separate runtime catalog override;
- catalog `profiles`;
- request `profile_id`;
- response `resolved_profile_id`;
- root uncertainty/locality aliases and duplicate criterion lists;
- handwritten frontend legacy response aliases; and
- UI old-field fallbacks.

Historical names in source or criterion lineage remain evidence, not API compatibility aliases.

## Verification and CI

The authoritative verification record is
`data/reports/phase5i-2026-07-29/report.md`.

Final working-tree verification passed:

- 280 backend tests with no skips;
- Ruff, Black, and compileall;
- no-diff OpenAPI and generated TypeScript regeneration;
- TypeScript typecheck and ESLint;
- 15 frontend component tests;
- Vite production build;
- 8 Chromium desktop/mobile end-to-end scenarios; and
- retained-source replay of `2026-07-29.2`.

A Git-archive clean checkout on Windows passed 271 backend tests. Nine tests explicitly skipped
because licensed raw artifacts are intentionally absent from Git; committed release integrity,
active API loading, and schema/checksum validation still passed. The same clean checkout passed all
frontend gates and browser tests after an offline frozen-lockfile install.

The repository CI workflow targets Ubuntu and Windows for backend gates and Ubuntu for all
frontend/browser gates. The Phase 5 commits are local and have not been pushed, so no remote Linux
or Windows Actions run exists for the final local SHA. Remote matrix confirmation is therefore the
one operational follow-up after an authorized push; it is not represented as having run.

## Limitations and remaining risks

- C66 ends in 2020 and retains the disclosed publisher wording inconsistency.
- C67 uses one climate model, one scenario, and one horizon.
- Both LSCs describe selected major urban centres, not rural areas, neighbourhood variation,
  vulnerability, adaptation, or national population exposure.
- Top-two opportunity aggregation is a product choice and must not be described as a country
  average.
- ATG and GRD have no qualifying v1 locality.
- GHSL is release-based and has no product refresh SLA.
- No applicant, household, occupation, institution, visa, or professional-licensing facts are
  evaluated.
- C05 and C68 remain held behind their own independent production gates.
- Remote GitHub Actions confirmation awaits a push of the local Phase 5 commit series.

## Future extension points

The clean `applicability` metadata and explicitly unevaluated profile assessment are the extension
points for a later typed decision-context engine. That future work should model applicant,
occupation, qualification, licensing, institution, household, visa, and co-location requirements
explicitly. It must not reinterpret a preference preset as a person.

Conversational exploration belongs later still. Any chat or explanation layer must consume the
typed deterministic Phase 5 catalog, ranking, comparison, details, evidence, and assessment tools.
It must not invent scores, sources, locality intersections, profile assumptions, or eligibility.

## Recommended next phase

Proceed next with a **structured applicant and household context phase**, beginning with contract
and source discovery rather than immediate scoring. Prioritize the questions Phase 5 deliberately
held:

1. occupation families such as technology and healthcare;
2. qualification recognition and professional licensing;
3. institution/program-level higher education and international-student access;
4. household-aware housing and earnings; and
5. visa, residency, and family context.

C05 locality research can continue as an independent fast follow, but it must not block or inherit
approval from the profile work. Conversational exploration remains after these deterministic
boundaries are proven.
