# Phase 6 closure report

Status: complete and active

Date: 2026-08-04

Phase 6 is closed with immutable release `2026-08-04.1` selected by
`data/releases/active.json`. Release schema 5.1 binds nine filter-only Opportunity Filters and 819
explicit country states to the unchanged Phase 5 ranking payloads. The public term is
**Opportunity Filters**; they never contribute to affinity scores, weights, PCC calculations, or
canonical ordering.

## Recorded owner decisions

The owner accepted the sequential Phase 6D–6I execution by reviewing each phase and explicitly
instructing execution of the next prompt. The final implementation records all required decisions:

| Decision | Accepted disposition |
| --- | --- |
| Public term and shorthand | Opportunity Filters; internal OFC shorthand. |
| Combination | Strict `ALL_REQUIRED`/AND only. |
| Public states | Exactly verified strong signal, strong signal not established, insufficient evidence. |
| Science/engineering | Retained at the hard shortlist floor. |
| Canada technology | Medium-confidence official crosswalk retained. |
| Care name | Care-sector employment ecosystem. |
| Skilled/construction routes | Skilled trades, construction, or both remain visible. |
| Education boundary | Research-university ecosystem evidence only. |
| Education assessability | 75 of 91 countries for each education filter. |
| Career dependency | ILO single-publisher dependency accepted and disclosed. |
| Education dependency | CWTS/ROR single-route dependency accepted and disclosed. |
| Business/finance education | Held; no filter published. |
| Broad university excellence | Held; no generic filter published. |

## Final release

- release ID: `2026-08-04.1` (derived as the first repository release on 2026-08-04);
- prior active release: `2026-07-29.2`;
- release schema: `konsider-release-5.1`;
- catalog schema: `konsider-catalog-3.0`;
- stable countries: 91;
- ordering criteria: 14, unchanged; 13 enabled, unchanged;
- Opportunity Filters: 9;
- Opportunity Filter evidence rows: 819, one per filter-country pair;
- release checksum: `sha256:34854ec38a5fed7a7455b5a5a0a70dc03f10f88ceda9d19cc0742224b8155493`.

All eleven Phase 5 payload files are byte-identical to `2026-07-29.2`. The release adds six
checksummed OFC artifacts and validates their binding, schemas, identities, sources, legal records,
policies, reason codes, coverage, routes, and exact matrix before startup.

## Accepted state matrix

Counts are verified / not established / insufficient:

| Filter | Counts |
| --- | ---: |
| Technology/software | 20 / 43 / 28 |
| Science/engineering | 20 / 47 / 24 |
| Care sector | 27 / 61 / 3 |
| Finance/insurance | 22 / 66 / 3 |
| Skilled trades/construction | 34 / 54 / 3 |
| Physical sciences/engineering education | 27 / 48 / 16 |
| Mathematics/computer science education | 30 / 45 / 16 |
| Biomedical/health sciences education | 30 / 45 / 16 |
| Life/earth sciences education | 31 / 44 / 16 |

## Ranking and compatibility proof

Before activation, final and prior services were compared under default, single-criterion, and
weighted multi-criterion requests. After removing the intentionally changed release metadata and
new opportunity assessment, responses were identical: country eligibility, scores, normalized
weights, contributions, order, top-K behavior, PCC status, locality assessment, profile assessment,
and preset behavior did not change. Empty/omitted filter selections remain equivalent. Selected
filters operate only after canonical ranking and preserve survivor order and base rank.

Release-5.0 historical loaders remain supported and expose an empty Opportunity Filter service.
The temporary staged-bundle environment override was removed; the default application now loads
only the checksum-bound artifacts in the active release.

## Verification evidence

- pre-activation backend: 370 passed;
- independent prior-release invariance: 1 passed;
- final backend: 373 passed (243 unit and 130 integration);
- final active-release/API matrix: 25 passed;
- publication lifecycle and fail-closed checksum tests: 3 passed;
- byte-identical final release regeneration and active locality replay: passed;
- Ruff, Black, compile and schema validation: passed;
- OpenAPI and TypeScript regeneration: passed;
- frontend typecheck, ESLint and production build: passed;
- Vitest: 20 passed;
- Playwright Chromium: 10 passed, including desktop/mobile filters and no horizontal overflow;
- performance: passed; active load 2.180s, catalog p95 1.607ms, no-filter p95 904.812ms,
  one-filter p95 907.019ms, multi-filter p95 1348.975ms;
- no-filter median was 0.6625 times the measured prior-release baseline on the same Windows host.

Machine-readable publication and performance evidence is retained in
`data/reports/phase6i-2026-08-04`.

## Operations, rollback and retained risks

Activation was atomic and occurred only after the release was published and strictly reloaded.
Rollback means validating a compatible published release and atomically selecting its correct
schema in `active.json`; immutable release contents are never edited. Selecting `2026-07-29.2`
removes Opportunity Filters because release 5.0 has no binding.

Material retained limitations are product boundaries, not hidden fallbacks: career signals depend
on one ILO publisher route; education signals depend on CWTS plus ROR identities; education is
assessable for 75/91 countries; states describe destination ecosystems, not individual job,
licensing, visa, credential, programme, admission, affordability, or success outcomes. Missing or
incompatible evidence remains `INSUFFICIENT_EVIDENCE` and is never inferred as negative.

## Next-phase context

A future separately approved phase may consider source redundancy, refresh automation, additional
construct research, operational telemetry, or broader deployment validation. Phase 6 does not
authorize those changes and leaves the held business-education and generic university-excellence
ideas unpublished.
