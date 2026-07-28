# Konsider Phase 4 — Uncertainty-Aware Ranking Model

## Why this is a separate phase

Phase 3 is closed. It researched 84 criteria, deeply reviewed 45, measured selected sources, and added three globally complete criteria. Phase 4 changes a different architectural assumption: ranking no longer has to reject every otherwise-valid criterion merely because a small number of stable countries lack fresh data.

Phase 4 must preserve the stable 91-country catalog and must not use imputation or country-specific weight renormalisation. It introduces query-specific complete-case ranking, explicit excluded-country reporting, and a mathematical top-K robustness analysis.

## Baseline

- Stable catalog: 91 countries.
- Current enabled full-coverage criteria: 8.
- Full-coverage criterion (FCC): valid and ranking-ready for all 91 countries.
- Partial-coverage criterion (PCC): otherwise production-suitable, but valid for at least 82 of 91 countries.
- Default score range: 1–10.
- Existing user priority scale:
  - No = 0.0
  - Very Low = 0.2
  - Low = 0.4
  - Medium = 0.6
  - High = 0.8
  - Very High = 1.0

## Approved policy defaults to encode and test

- PCC activation threshold: Medium or above, raw weight >= 0.6.
- Preferred active missing-country union: 5 or fewer.
- Hard active missing-country union: 9 or fewer.
- Equivalent minimum eligible-country universe: 82.
- Default top K: 10.
- Actual robustness K: the request's `top_k`, defaulting to 10.
- Missing values are never imputed.
- Countries are never scored with different active criterion sets.
- A PCC below the activation threshold is excluded from ranking entirely, not merely ignored during missing-data analysis.
- The stable catalog remains 91 even when a query ranks fewer countries.

## Core algorithm

Given user weights:

1. Classify enabled criteria as FCC or PCC.
2. Compute baseline `R0` over all 91 countries using the user's FCC weights.
3. Activate only PCC whose raw user weight is >= 0.6. Call these `PCC-u`.
4. Let `Mu` be the union of countries missing or stale for any criterion in `PCC-u`.
5. Let `Eu = stable_91 - Mu`.
6. If `|Mu| > 9` or `|Eu| < 82`, do not produce a PCC-inclusive ranking. Return the FCC-only baseline with a structured coverage-limit explanation.
7. Otherwise compute `R1` over `Eu` using the same active criterion set and the same normalised weights for every ranked country.
8. For each excluded country, calculate an optimistic upper bound:
   - use its real scores for known active criteria;
   - use score 10 only for each missing active PCC;
   - this is diagnostic only and is never published as the country's score.
9. Compare each optimistic bound with the actual Kth score in `R1`.
10. Classify uncertainty:
    - `FULL_COVERAGE`: no active PCC country exclusions.
    - `ROBUST_TOP_K`: exclusions exist, but no excluded country could enter top K even with perfect missing scores.
    - `POTENTIALLY_AFFECTED`: at least one excluded country's optimistic bound reaches or exceeds the Kth score.
    - `BASELINE_TOP_K_EXCLUDED`: at least one excluded country was already in the FCC-only `R0` top K.
    - `COVERAGE_LIMIT_EXCEEDED`: more than 9 countries would be excluded or fewer than 82 would remain.
11. Always report excluded countries, missing criteria, baseline ranks, optimistic bounds, and exact ranking-universe size.

`BASELINE_TOP_K_EXCLUDED` is the strongest warning. `POTENTIALLY_AFFECTED` is also a prominent caution. `ROBUST_TOP_K` supports a mild warning.

## Initial Phase 3 candidates to evaluate

These are candidates for Phase 4 review, not automatic approvals:

- C11 Overall job-market opportunity: 88/91.
- C26 Financial protection from health costs: 90/91.
- C08 School education quality: 87/91; experimental construct decision remains.
- C53 Basic water and sanitation access: 86/91; reserve because discrimination and semantic value are weak.

Suggested initial onboarding sequence:

1. C11 + C26
2. C08 after its scoring construct is frozen
3. Keep C53 as reserve unless it adds clear decision value

Known active missing-union examples from Phase 3 evidence:

- C11 + C26: 3 unique missing/stale countries.
- C08 + C26: 5.
- C11 + C08 + C26: 6.
- C11 + C08 + C26 + C53: 9.

Full-coverage candidates such as macroeconomic stability or extreme-weather risk are not PCC problems. They may be added later after their separate methodology blockers are resolved.

## Phase structure

- Phase 4A — Product policy and mathematical contract
  Intended for: Desktop ChatGPT Work

- Phase 4B — Candidate selection and coverage simulations
  Intended for: Desktop ChatGPT Work

- Phase 4C — Release, catalog, and validation contracts
  Intended for: Codex

- Phase 4D — Ranking engine and robustness analysis
  Intended for: Codex

- Phase 4E — API contract and integration
  Intended for: Codex

- Phase 4F — Candidate source onboarding and immutable release
  Intended for: Codex

- Phase 4G — UI and UX implementation
  Intended for: Codex

- Phase 4H — End-to-end verification, closure, and roadmap update
  Intended for: Codex, followed by ChatGPT review

## Recommended execution order

Run 4A and 4B before writing production code. Revise later prompts with the approved 4A policy and 4B candidate list. Phases 4C–4E can use fixture-backed PCC data. Phase 4F introduces exact sources and a new immutable release. Phase 4G renders API metadata without duplicating ranking logic. Phase 4H closes the phase.


---

# Prompt — Phase 4A: Product Policy and Mathematical Contract

## Intended for
ChatGPT Desktop Work on the Windows laptop.

## Inputs
- Current Konsider repository.
- Phase 3 closure report.
- Phase 3F portfolio decision.
- Phase 3 measured probe reports and country-status matrices.
- Current recommendation engine, API contract, UI documentation, and active release.

## Objective

Create the authoritative product and mathematical specification for **Phase 4 — Uncertainty-Aware Ranking Model**. Do not implement code.

## Required decisions

### 1. Terminology

Define:

- stable country catalog;
- full-coverage criterion (`FCC`);
- partial-coverage criterion (`PCC`);
- user-active PCC (`PCC-u`);
- baseline ranking (`R0`);
- eligible ranking universe (`Eu`);
- user-specific missing-country union (`Mu`);
- final complete-case ranking (`R1`);
- optimistic excluded-country upper bound;
- top-K robustness status.

Do not call missing countries low-ranked countries. They are excluded or unranked.

### 2. Policy defaults

Use these defaults unless repository evidence proves they conflict with an existing contract:

- stable catalog size: 91;
- PCC minimum criterion coverage: 82/91;
- preferred query-specific missing union: `Mu <= 5`;
- hard maximum missing union: `Mu <= 9`;
- minimum eligible query universe: 82;
- PCC activation threshold: raw user weight >= 0.6, corresponding to Medium;
- default top K: 10;
- actual robustness K: requested `top_k`;
- score maximum used for diagnostic upper bounds: 10.

Make every value versioned/configurable in policy rather than scattered magic constants.

### 3. Ranking algorithm

Specify precisely:

1. Use the user's FCC weights to calculate `R0` across all 91 countries.
2. An FCC with zero weight does not contribute. Preserve the existing all-zero fallback semantics.
3. A PCC contributes only when its raw weight is at least 0.6.
4. A PCC below 0.6 is fully ignored for `R1`, weight normalisation, missing-country analysis, and robustness analysis.
5. Build `Mu` from missing, stale, invalid, rejected, or otherwise non-ready observations for every criterion in `PCC-u`.
6. Rank only `Eu = stable_91 - Mu`.
7. Every country in `R1` must have every active criterion.
8. Normalise weights once over the active criteria and apply the same weights to all countries in `R1`.
9. Never impute values or renormalise weights per country.
10. If more than nine countries are excluded, return `R0` plus a structured coverage-limit result instead of `R1`.

### 4. Top-K robustness analysis

For each excluded country `x`, define:

`upper_bound(x) = sum(known active criterion contributions) + sum(normalised weight of each missing active PCC * 10)`

This is a diagnostic bound only.

Compare the upper bound with the actual Kth score in `R1`, respecting ties.

Define these statuses:

- `NO_PARTIAL_CRITERIA_ACTIVE`
- `FULL_COVERAGE`
- `ROBUST_TOP_K`
- `POTENTIALLY_AFFECTED`
- `BASELINE_TOP_K_EXCLUDED`
- `COVERAGE_LIMIT_EXCEEDED`

Specify deterministic precedence when more than one condition applies. Recommended precedence:

1. `COVERAGE_LIMIT_EXCEEDED`
2. `BASELINE_TOP_K_EXCLUDED`
3. `POTENTIALLY_AFFECTED`
4. `ROBUST_TOP_K`
5. `FULL_COVERAGE`
6. `NO_PARTIAL_CRITERIA_ACTIVE`

### 5. Warning semantics

Define user-facing meaning, not final UI copy:

- mild disclosure for `ROBUST_TOP_K`;
- prominent caution for `POTENTIALLY_AFFECTED`;
- strongest warning for `BASELINE_TOP_K_EXCLUDED`;
- no PCC-inclusive results for `COVERAGE_LIMIT_EXCEEDED`.

### 6. Non-goals

Keep outside Phase 4:

- imputation;
- probabilistic prediction of missing criterion values;
- LLM-generated scores;
- city-level rankings;
- applicant-specific visa/legal eligibility;
- profile-derived tax or housing calculations;
- silent source fallback;
- country-specific criterion sets;
- changing the stable catalog from 91.

## Deliverables

Produce:

1. `docs/product/uncertainty-aware-ranking.md`
2. A policy table with every default and rationale.
3. Mathematical examples using:
   - no active PCC;
   - one PCC with three missing countries;
   - several PCC with five, six, and nine unique missing countries;
   - a coverage-limit case;
   - robust and potentially affected top-10 examples.
4. Stable status and reason-code definitions.
5. Acceptance criteria for Phases 4C–4H.
6. A concise list of open decisions that truly require user approval.

Do not change repository code or production data.


---

# Prompt — Phase 4B: Candidate Selection and Coverage Simulations

## Intended for
ChatGPT Desktop Work on the Windows laptop.

## Inputs
- Approved Phase 4A policy.
- Phase 3A–3H research and closure evidence.
- Phase 3 country-status matrices and exact probe outputs.
- Current active catalog and release.

## Objective

Select the first partial-coverage criteria for Phase 4 and quantify their effect on the 91-country catalog before implementation. Do not write production code.

## Candidate eligibility gates

A PCC candidate must:

1. Have an exact authoritative source and production-compatible licence.
2. Have deterministic parsing, mapping, provenance, and replay evidence, or a clear bounded path to obtain them.
3. Have at least 82/91 valid countries under its approved freshness rule.
4. Be a meaningful national criterion, not a city, profession, household, origin, or applicant-specific question.
5. Have a frozen or explicitly experimental scoring construct.
6. Preserve every missing/stale/invalid country outcome explicitly.
7. Add material decision value without unacceptable redundancy.
8. Have manageable refresh and maintenance cost.

Coverage alone must not promote a criterion whose construct or scoring remains indefensible.

## Initial candidates to assess

Assess at minimum:

- C11 Overall job-market opportunity — measured 88/91.
- C26 Financial protection from health costs — measured 90/91.
- C08 School education quality — measured 87/91 and experimental.
- C53 Basic water and sanitation access — measured 86/91 and reserve.

Also list full-coverage future candidates such as C29 macroeconomic stability and C66 extreme-weather risk separately. They are not PCC candidates and must not be mixed into the missing-data policy decision.

## Required analysis

### 1. Exact missing matrix

For every candidate, record:

- valid count;
- missing countries;
- stale countries;
- invalid countries;
- missing reason by country;
- source version;
- freshness rule;
- scoring/readiness blockers unrelated to coverage.

### 2. Combination simulations

Calculate the union of non-valid countries for:

- every single candidate;
- every pair;
- every triple;
- the full candidate set.

Classify each combination:

- preferred: 0–5 missing;
- elevated: 6–9 missing;
- blocked: more than 9 missing.

Verify the known Phase 3 examples rather than assuming them:

- C11 + C26 expected union: 3;
- C08 + C26 expected union: 5;
- C11 + C08 + C26 expected union: 6;
- C11 + C08 + C26 + C53 expected union: 9.

### 3. Historical ranking simulations

Using the current eight FCC and representative profiles/weights:

- compute `R0`;
- simulate each candidate combination;
- calculate excluded-country baseline ranks;
- calculate optimistic upper bounds;
- classify top-5, top-10, and top-20 robustness;
- identify cases where a missing country was in the baseline top K;
- identify country or regional bias in exclusions.

Use deterministic scripts or repository data, not prose estimates.

### 4. Candidate decision

Recommend:

- initial production PCC set;
- second-wave experimental PCC set;
- reserve;
- reject/defer.

The starting hypothesis is:

1. C11 + C26 first;
2. C08 after its scoring construct is frozen;
3. C53 remains reserve unless simulation shows clear marginal value.

This is a hypothesis to verify, not a required conclusion.

## Deliverables

Produce:

- `docs/research/phase4b-pcc-selection.md`;
- machine-readable candidate matrix;
- combination-union matrix;
- robustness simulation report;
- approved initial PCC IDs;
- exact reasons for every candidate not selected;
- inputs required by Phase 4F.

Do not add sources to production or publish a release.


---

# Prompt — Phase 4C: Release, Catalog, and Validation Contracts

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4A policy.
- Approved Phase 4B candidate selection.
- Current release `2026-07-27.1`.
- Existing release repository, validation, consumer catalog, and immutable-release rules.

## Objective

Extend Konsider's release and catalog contracts so a release can contain both globally complete ranking criteria and approved partial-coverage criteria without weakening structural validation.

Use fixture-backed PCC data in this phase. Do not ingest live candidate sources yet.

## Required contract model

Add a versioned criterion coverage mode, for example:

- `GLOBAL_CORE`
- `CONDITIONAL_COMPLETE_CASE`
- `DIAGNOSTIC_ONLY`

For each enabled criterion store or derive:

- coverage mode;
- stable universe ID and denominator;
- valid country count;
- minimum valid count;
- missing/stale/invalid country outcomes;
- PCC activation threshold;
- experimental status;
- source/scoring versions;
- allowed score range.

## Release behavior

1. `GLOBAL_CORE` criteria require 91/91 valid scores.
2. `CONDITIONAL_COMPLETE_CASE` criteria require at least 82/91 valid scores.
3. All 91 attempt outcomes must still be present for every published criterion.
4. Scores exist only for valid observations.
5. Missing, stale, invalid, and rejected observations remain explicit.
6. No validation path may treat absent score rows as valid without consulting the attempt/outcome record.
7. Product readiness requires the configured minimum number of global core criteria.
8. Historical releases and schemas remain immutable and loadable.
9. Publish a new schema version rather than rewriting release schema 3.0 in place.
10. Catalog and release validation must reconcile exactly.

## Validation requirements

Add checks for:

- criterion coverage mode;
- conditional minimum coverage;
- exact attempt completeness for all 91 countries;
- valid-score count reconciliation;
- country outcome reason codes;
- no score for non-valid observations;
- no missing attempt;
- activation threshold range;
- stable policy version;
- no PCC enabled when its valid count is below 82;
- global core remains 91/91;
- deterministic checksums and LF-normalised artifacts.

## Compatibility

- Preserve loading of the active schema-3 release.
- Add explicit schema negotiation or migration logic for the new release schema.
- Do not silently reinterpret an old criterion as PCC.
- Keep the API and engine behavior unchanged until later sub-phases use the new metadata.

## Tests

Add unit and integration tests for:

- one 91/91 FCC;
- one 88/91 PCC;
- mixed outcomes;
- insufficient 81/91 PCC;
- score/attempt mismatch;
- stale versus missing reason preservation;
- old release compatibility;
- new release checksum/replay;
- Windows/Linux byte stability.

## Deliverables

- schema and model changes;
- fixture release using the new contract;
- validation and repository support;
- tests;
- documentation;
- no active release pointer change.


---

# Prompt — Phase 4D: Ranking Engine and Robustness Analysis

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4A mathematical contract.
- Phase 4C release/catalog support.
- Phase 4B candidate missing-country matrices.
- Existing deterministic recommendation service.

## Objective

Implement uncertainty-aware complete-case ranking in the domain/service layer. Do not put ranking rules in API routes or UI code.

## Algorithm requirements

### Criterion activation

- FCC uses the existing user-weight semantics.
- PCC is active only when raw weight >= 0.6.
- PCC with raw weight below 0.6 is removed before weight normalisation and missing-union analysis.
- Preserve existing behavior for unknown criteria, disabled criteria, negative/non-finite weights, omitted weights, and all-zero weights.

### Baseline R0

- Calculate `R0` over all 91 stable countries using the user's active FCC weights.
- Use existing deterministic tie-breaking.
- Preserve contributions and explanation semantics.

### Final R1

- Build `Mu` from every non-valid country outcome across active PCC.
- Build `Eu = stable_91 - Mu`.
- If `|Mu| > 9` or `|Eu| < 82`, do not calculate a PCC-inclusive result. Return the FCC baseline plus `COVERAGE_LIMIT_EXCEEDED`.
- Otherwise normalise weights once across active FCC and PCC.
- Rank only `Eu`.
- Every ranked country must have every active criterion.
- Never impute and never renormalise by country.

### Robustness

For each excluded country:

- retain its `R0` rank and FCC score;
- use real known scores for active criteria;
- substitute score 10 only inside an optimistic diagnostic calculation for missing active PCC;
- compute the optimistic total using the same normalised weights as `R1`;
- compare against the Kth `R1` score;
- treat equality as potentially able to enter because of ties.

Status precedence:

1. `COVERAGE_LIMIT_EXCEEDED`
2. `BASELINE_TOP_K_EXCLUDED`
3. `POTENTIALLY_AFFECTED`
4. `ROBUST_TOP_K`
5. `FULL_COVERAGE`
6. `NO_PARTIAL_CRITERIA_ACTIVE`

`K` equals requested `top_k`, default 10.

## Domain output

Return structured data including:

- stable country count;
- eligible country count;
- excluded country count;
- active FCC IDs;
- active PCC IDs;
- ignored PCC IDs and their raw weights;
- excluded countries and exact missing criteria/reasons;
- R0 top K;
- R1 top K;
- Kth score;
- excluded-country R0 ranks;
- optimistic upper-bound scores;
- could-enter-top-K flags;
- uncertainty status and reason codes;
- policy version and thresholds.

Do not rely only on prewritten warning strings.

## Tests

Cover:

- no PCC active;
- PCC below 0.6;
- one active PCC;
- multiple active PCC;
- unions of 5, 6, 9, and 10;
- baseline-top-K exclusion;
- optimistic bound below, equal to, and above Kth score;
- ties;
- top_k 5, 10, and 20;
- all-zero weights;
- deterministic ordering;
- no partial scoring;
- contribution reconciliation;
- old FCC-only behavior unchanged.

## Deliverables

- domain/service implementation;
- typed result models;
- tests and golden scenarios;
- algorithm documentation;
- no API/UI implementation in this sub-phase.


---

# Prompt — Phase 4E: API Contract and Integration

## Intended for
Codex in the local Konsider repository.

## Inputs
- Phase 4C contract support.
- Phase 4D domain/service implementation.
- Existing FastAPI v1 routes and typed error envelope.

## Objective

Expose uncertainty-aware ranking through the thin typed API without duplicating ranking, coverage, readiness, or robustness logic.

## Catalog changes

For each criterion expose:

- criterion ID and label;
- enabled/readiness status;
- coverage mode;
- valid-country count and stable denominator;
- coverage percentage;
- PCC activation threshold;
- experimental flag;
- concise caveat;
- optionally missing-country count, with full details available in ranking output.

## Ranking request

Keep the existing weight request semantics where possible.

- `top_k` defaults to 10.
- User weights continue to use the existing raw scale.
- Do not require the client to identify FCC/PCC.
- Do not let the client choose excluded countries.
- Consider an optional `include_baseline` flag only if the domain result is otherwise too large; default behavior must still provide enough metadata to explain uncertainty.

## Ranking response

Add typed fields for:

- stable universe size;
- eligible universe size;
- ranking coverage mode;
- active/ignored PCC;
- excluded countries;
- missing criteria and reason codes;
- uncertainty status;
- robustness K;
- Kth eligible score;
- potential excluded entrants;
- baseline top-K membership;
- policy version;
- warning/message code.

Keep ranked countries separate from excluded/unranked countries.

## Error behavior

Use stable structured codes, including:

- `coverage_limit_exceeded` only when the API contract chooses to represent the fallback as an error;
- preferably return a successful FCC baseline with structured coverage status rather than a transport error;
- preserve existing 422, 404, 503, and 500 behavior for unrelated failures.

## Compatibility

- Update API models and OpenAPI.
- Keep routes thin.
- Update generated or checked-in frontend types.
- Add integration and contract tests.
- Ensure old FCC-only requests produce semantically identical rankings plus additive uncertainty metadata.

## Deliverables

- API models/routes integration;
- OpenAPI update;
- contract tests;
- documentation examples for all uncertainty states;
- no source ingestion or UI implementation.


---

# Prompt — Phase 4F: Candidate Source Onboarding and Immutable Release

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4B PCC list.
- Phase 4C–4E implementation.
- Exact Phase 3 probe artifacts, source records, licensing conclusions, and missing-country outcomes.
- Current active release and retained local raw artifacts.

## Objective

Implement only the user-approved initial PCC candidates as production or explicitly experimental criteria under the new Phase 4 contract, then publish a new immutable release if every gate passes.

## Candidate order

Use the Phase 4B decision. The working hypothesis is:

1. C11 Overall job-market opportunity
2. C26 Financial protection from health costs
3. C08 School education quality as a second-wave experimental candidate
4. C53 remains reserve unless explicitly approved

Do not automatically implement all four.

## For each approved criterion

1. Freeze the exact source, edition, series/components, methodology, licence, attribution, parser version, freshness rule, and scoring method.
2. Preserve 91 explicit attempt outcomes.
3. Produce observations and scores only for valid countries.
4. Preserve missing/stale/invalid reasons.
5. Set coverage mode to `CONDITIONAL_COMPLETE_CASE`.
6. Require at least 82 valid countries.
7. Add component and sensitivity diagnostics.
8. Avoid broad labels that overclaim the source.
9. Add online and offline replay.
10. Add parser, scoring, validation, release, repository, engine, and API tests.

## Candidate-specific cautions

### C11

- Measures harmonised national labour-market outcomes, not vacancies or occupation-specific opportunity.
- Freeze the unemployment, employment-to-population, and labour-force-participation construction.
- Test component redundancy and weights.
- Preserve known non-valid countries.

### C26

- Label as financial protection from health costs, not total healthcare affordability.
- Do not imply migrant eligibility, premiums, quality, or waiting times.
- Preserve Ukraine's stale outcome unless a newer approved source resolves it.

### C08

- Freeze the exact schooling/learning construct before implementation.
- Do not treat the published schooling component as a percentage.
- Keep experimental status and model/mixed-year caveats.
- Preserve known non-valid countries.

### C53

- Do not enable merely because it fits the coverage model.
- It measures basic access, not safety, taste, continuity, or utility reliability.
- Require explicit user approval and discrimination evidence.

## Publication

- Publish only with a new release ID and new schema version.
- Do not modify historical releases.
- Keep global core criteria at 91/91.
- Validate the query-specific missing unions for the approved PCC set.
- Verify cross-platform checksums from a clean Git checkout/worktree.
- Move `active.json` only after all tests, replay, and catalog reconciliation pass.

## Deliverables

- source registrations and ingestion;
- new immutable release if valid;
- updated catalog;
- exact coverage report;
- replay and checksums;
- documentation and release history;
- no UI implementation.


---

# Prompt — Phase 4G: UI and UX for Uncertainty-Aware Ranking

## Intended for
Codex in the local Konsider repository.

## Inputs
- Phase 4E API contract and generated types.
- Phase 4F active release/catalog.
- Existing responsive React UI and `docs/product/ui.md`.

## Objective

Add clear uncertainty-aware ranking UX without reproducing ranking logic in the browser.

## Criteria controls

For every criterion show its status clearly:

- full coverage: `91/91 countries`;
- partial coverage: for example `88/91 countries`;
- experimental where applicable;
- unavailable/non-ready where applicable.

For PCC:

- show a concise indicator such as `Limited coverage`;
- show the activation rule: it affects ranking only at Medium or above;
- when set to No, Very Low, or Low, indicate that it is not active in the ranking;
- provide an accessible details view listing missing-country count and criterion caveat.

Do not use alarming red styling merely because a criterion is PCC.

## Pre-apply coverage preview

When weights change, the UI may use catalog metadata to preview:

- active PCC count;
- potential missing-country union count where the API provides a preview endpoint or deterministic metadata;
- whether the preferred five-country band is exceeded.

Do not reimplement the final ranking or robustness calculation client-side. If no preview API exists, show the definitive result only after Apply.

## Results summary

Always show:

- `X of 91 countries ranked`;
- active PCC names;
- excluded-country count;
- uncertainty status;
- robustness K.

### Mild state — ROBUST_TOP_K

Example meaning:

> Some countries were excluded because of missing data. Even with the best possible missing scores, none could enter your top 10.

### Prominent caution — POTENTIALLY_AFFECTED

Example meaning:

> One or more excluded countries could potentially enter your top 10. Treat the recommendations as incomplete.

### Strongest warning — BASELINE_TOP_K_EXCLUDED

Example meaning:

> A country that appeared in the full-coverage top 10 is excluded because an important selected criterion lacks data.

### Coverage limit

Show the FCC-only baseline and explain that the PCC-inclusive result was not generated because too many countries would be excluded.

## Excluded-country details

Provide an expandable section with:

- country;
- baseline R0 rank;
- missing/stale criteria;
- reason;
- optimistic upper bound;
- whether it could enter top K.

Never display excluded countries at the bottom of the ranked table.

## Ranking table

- Label the rank scope, e.g. `Rank among 88 eligible countries`.
- Keep the existing basic/detailed table behavior.
- Preserve country comparison selection for ranked countries.
- An excluded country may still be opened for available FCC evidence, but it must be labelled `Not ranked for this profile`.
- Do not fabricate an affinity score for excluded countries.

## Baseline view

Add a secondary `View full-coverage baseline` control when PCC is active.

- `R1` remains the primary result.
- The baseline is explanatory, not a competing default.
- Clearly distinguish its criteria and 91-country universe.

## Accessibility and responsiveness

- Use icons plus text, not colour alone.
- Ensure warnings are screen-reader accessible.
- Preserve full mobile functionality.
- Keep long excluded-country lists collapsible.
- Do not reserve excessive vertical space when no PCC is active.

## Testing

Add:

- component tests for every uncertainty status;
- mobile and desktop layout tests;
- API-driven tests proving no client-side ranking;
- empty/one/many excluded-country cases;
- baseline-toggle behavior;
- experimental/unavailable/PCC badges;
- accessible warning semantics.

## Deliverables

- React implementation;
- updated types and API client;
- tests;
- screenshots or documented visual states;
- updated UI documentation.


---

# Prompt — Phase 4H: End-to-End Verification and Closure

## Intended for
Codex in the local Konsider repository, followed by review in ChatGPT Desktop Work or Web ChatGPT.

## Inputs
- Completed Phase 4A–4G outputs.
- New active release, if Phase 4F published one.
- Current backend, API, UI, CI, roadmap, and documentation.

## Objective

Verify and close **Phase 4 — Uncertainty-Aware Ranking Model** without weakening the evidence-first guarantees established in Phases 1–3.

## End-to-end scenarios

Test at minimum:

1. FCC-only profile: 91 countries, unchanged ranking semantics.
2. PCC present but below Medium: ignored completely.
3. One active PCC with three excluded countries.
4. Active PCC combination with five excluded countries.
5. Combination with six excluded countries and heightened disclosure.
6. Combination with nine excluded countries.
7. Ten excluded countries: PCC-inclusive ranking blocked and R0 returned.
8. `ROBUST_TOP_K`.
9. `POTENTIALLY_AFFECTED`.
10. `BASELINE_TOP_K_EXCLUDED`.
11. top_k 5, 10, and 20.
12. ties at the Kth score.
13. excluded country detail and FCC evidence access.
14. deterministic repeat requests.
15. clean Windows and Linux checkouts.

## Invariants

Prove:

- stable catalog remains 91;
- global core criteria remain 91/91;
- PCC has at least 82 valid countries;
- all 91 attempts exist for every criterion;
- no score exists for a non-valid PCC observation;
- every R1 country has every active criterion;
- one normalised weight vector is used for all R1 countries;
- no imputation;
- no per-country weight renormalisation;
- excluded countries are never assigned final ranks;
- optimistic bounds are diagnostic only;
- API and UI do not duplicate engine logic;
- historical releases remain immutable and loadable;
- offline replay and checksums pass.

## Documentation

Create/update:

- Phase 4 closure report;
- architecture;
- release schema and catalog docs;
- scoring methodology;
- API docs;
- UI docs;
- worker operations;
- implementation history;
- release report;
- roadmap;
- documentation index.

Document the distinction between:

- stable 91-country catalog;
- query-specific eligible ranking universe;
- full-coverage baseline R0;
- final complete-case R1;
- robustness status.

## Quality gates

Run:

- complete pytest suite;
- Ruff;
- Black formatting check;
- Python compileall;
- frontend typecheck;
- frontend unit/component tests;
- production frontend build;
- OpenAPI/documentation contract checks;
- clean-checkout release validation;
- offline replay.

## Closure report

Record:

- approved policy values;
- enabled FCC and PCC;
- actual missing-country unions;
- robustness test results;
- source and scoring limitations;
- final enabled criterion count;
- UI states;
- known gaps;
- future criteria that remain blocked for city/profile/legal/methodology reasons.

Do not claim that Phase 4 solves city-level, occupation-level, household, or applicant-specific ranking.

## Deliverables

- passing end-to-end system;
- Phase 4 closure report;
- roadmap update;
- quality-gate evidence;
- concise list of remaining risks and next phase.
