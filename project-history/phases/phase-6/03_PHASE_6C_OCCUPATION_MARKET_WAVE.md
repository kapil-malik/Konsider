# Phase 6C Prompt — Occupation-Market Criterion Wave

## Dependency

Proceed only after Phase 6B is complete and the Phase 6A occupation constructs remain approved.

## Objective

Implement and publish all approved occupation-market criteria as one coherent career wave.

The minimum intended set is:

1. Technology employment-market depth.
2. Engineering employment-market depth, or the approved truthful renamed form.

Also include, in the same wave, if approved:

3. Healthcare employment-market depth.
4. Business and finance employment-market depth.

Do not artificially defer approved stretch criteria that use the same source, parser, taxonomy, and scoring framework.

## Product meaning

Every criterion must answer:

> How deep and established is this occupation-family employment market in the country?

It must not answer or imply:

- current vacancy count;
- personal hiring probability;
- salary;
- visa availability;
- language fit;
- recognition of qualifications;
- licensing eligibility;
- seniority fit;
- locality-specific demand unless locality evidence exists.

Use visible caveats in catalog, API evidence, UI details, and documentation.

## Scope decision

Use national direct scope unless Phase 6A found a globally reproducible locality source that clears the same gates.

Do not manufacture an LSC by assigning national occupation data to cities.

A national PCC is acceptable and expected.

## Input selection

For each country and occupation family:

- choose observations using an explicit freshness and source-priority policy;
- require compatible classification;
- prefer both-sex totals;
- avoid summing incompatible national estimates;
- preserve observation method flags;
- reject duplicate/conflicting records deterministically;
- classify missing/stale/invalid/rejected outcomes explicitly.

## Metric and scoring

Implement the approved simple metric.

If Phase 6A approved a blend of scale and specialization, define each component and weight explicitly.

Requirements:

- score range remains consistent with Konsider;
- transform is monotonic;
- reference population/denominator is compatible;
- no large-country domination;
- no tiny-market inflation;
- outlier handling is explicit;
- scoring version is frozen;
- sensitivity analysis supports the selected transform.

Do not use different score formulas for different countries.

## Naming gate

Before publication verify:

- technology codes genuinely represent ICT work;
- engineering name matches the actual code granularity;
- healthcare name does not imply foreign licensing access;
- business/finance name matches included codes.

If the data only supports broader groups, rename truthfully before publication.

## Coverage and portfolio analysis

For each new criterion report:

- valid countries;
- missing countries;
- stale countries;
- invalid/rejected countries;
- selected coverage mode;
- activation threshold;
- eligible-country count when active alone;
- missing-country union with each existing PCC;
- missing-country union with the other career criteria;
- missing-country union under proposed presets.

Do not alter the global coverage policy.

If an approved criterion falls below the existing PCC publication minimum during implementation, hold it with evidence or use an already approved replacement. Do not invent values.

## Interaction with existing Overall job-market opportunity

Quantify:

- Pearson/Spearman correlation;
- rank changes;
- countries with strong overall market but weak occupation-family depth;
- countries with weak overall market but strong occupation-family specialization;
- conceptual overlap.

The new criteria must remain independently useful.

Do not remove Overall job-market opportunity merely because occupation criteria exist.

## Readiness and experimental state

New criteria should normally begin as experimental unless all construct, coverage, and interpretation risks are unusually mature.

Experimental criteria may still be ready and weightable if the current product contract permits it.

## Preference presets

Do not simply add every new PCC at Medium to every existing preset.

Create or update presets deliberately, for example:

- Technology career;
- Engineering career;
- Career opportunity.

A preset must be validated against the PCC missing-union hard limit.

The equal/general preset should remain broadly useful and should not silently trigger coverage fallback because several specialized criteria were added.

Keep weights transparent.

## Release

Publish all approved occupation criteria in one additive immutable release.

Required:

- source registrations and lineages;
- taxonomy snapshots;
- criterion policies;
- scoring methods;
- exact outcomes for all 91 countries;
- observations and scores;
- catalog snapshot;
- checksums;
- replay;
- active pointer update only after all gates pass.

Do not mutate the Phase 5 release.

## API and UI

The current catalog-driven API/UI should render new criteria automatically.

Make only minimal changes required for:

- career domain labels;
- taxonomy/evidence details;
- caveats;
- new presets;
- unavailable outcomes;
- mobile display.

Do not introduce applicant controls in this phase.

## Tests

Cover:

- each occupation family;
- multiple families derived from one source capture;
- missing/stale data;
- classification mismatch;
- scoring boundaries;
- combined PCC activation;
- default and specialized presets;
- comparison and country details;
- active release load;
- offline replay;
- generated API types;
- UI rendering.

## Required report

Create a Phase 6C report including:

- exact public criteria;
- code mappings;
- source/version/licence;
- coverage;
- scoring;
- sensitivity;
- correlations;
- ranking movement;
- default-preset behavior;
- limitations;
- release ID and checksums.

## Commits

Prefer two reviewable commits:

1. implementation and tests:
   - `feat: add occupation-market criteria`
2. immutable release and product integration:
   - `data: publish Phase 6 career criteria release`

If repository conventions strongly favor one commit per additive release, keep the wave coherent but do not mix unrelated education work.

Stop after the career release and report whether the minimum Phase 6 four-criterion target remains achievable.
