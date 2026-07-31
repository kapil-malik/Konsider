# Phase 6G Prompt — Final Verification and Closure

## Dependency

Proceed only after Phase 6A-F are complete and all intended releases are built locally.

## Objective

Verify Phase 6 end to end, fix defects in focused commits, and close the phase with an authoritative criterion-focused report.

## Required exit outcome

Phase 6 should close with at least four new public, ready, weightable criteria unless the closure report demonstrates a critical blocker.

The intended four are:

1. Technology employment-market depth.
2. Engineering employment-market depth or truthful renamed form.
3. Engineering higher-education capacity.
4. Engineering academic and research ecosystem.

If one is blocked, document:

- the exact blocker;
- why it is critical;
- why a weaker proxy was rejected;
- whether an approved stretch criterion replaced it;
- the reopening condition.

Do not describe the phase as fully successful if fewer than four criteria are public without clearly calling out the shortfall.

## Criterion verification

For every Phase 6 criterion verify:

- public ID and name;
- Phase 3 lineage;
- exact construct;
- non-claims;
- category/domain/family;
- coverage;
- scope;
- applicability;
- source/version/licence;
- taxonomy version;
- scoring version;
- readiness;
- experimental state;
- default/preset weights;
- country outcomes;
- source lineage;
- replay.

## Data invariants

Prove:

- all 91 countries have explicit outcomes;
- score exists exactly for valid country result;
- no imputation;
- no country-specific renormalization;
- source codes resolve to frozen taxonomy mappings;
- reference years obey policy;
- classification versions match;
- derived institution/locality evidence is valid;
- release/catalog/manifest/checksums reconcile;
- historical releases are unchanged.

## Ranking and portfolio invariants

Prove:

- each new PCC activates under existing policy;
- combined missing-country unions are correct;
- coverage-limit fallback remains correct;
- no default preset unexpectedly falls back;
- specialized presets are reproducible;
- contributions reconcile to totals;
- new criteria do not change eligibility through profile status;
- `NO_PROFILE_CONTEXT` remains truthful;
- LSC academic evidence does not change country aggregate through common-locality advice.

## Semantic tests

Ensure the public product never claims:

- live vacancies from employment stock;
- personal job probability;
- engineering specificity when data are broader;
- admission probability from education capacity;
- programme quality from graduate counts;
- accreditation from research output;
- applicant fit without context.

## Full test matrix

Run and record:

### Backend

- unit tests;
- integration tests;
- release validation;
- source capture replay;
- active release replay;
- format/lint/static checks;
- compile checks.

### API

- health;
- catalog;
- ranking;
- comparison;
- country details;
- OpenAPI regeneration;
- strict schema tests;
- generated TypeScript no-diff check.

### Frontend

- typecheck;
- lint;
- component tests;
- production build;
- desktop and mobile browser tests;
- accessibility checks.

### Clean checkout

- Windows;
- Linux;
- committed release integrity without licensed raw bytes;
- documented skips only where exact retained raw artifacts are intentionally absent.

### Portfolio

- correlation report;
- score sensitivity;
- PCC union matrix;
- all preference presets;
- ranking scenarios from Phase 6E.

## Defect handling

When a defect is found:

- fix it in a focused commit;
- rerun affected tests;
- rerun full closure gates;
- do not weaken assertions or source standards to pass.

Do not bundle unrelated defects into the closure documentation commit.

## Closure report

Create:

- `docs/history/phase6-closure-report.md`
- `data/reports/phase6g-<date>/report.md`
- updated roadmap;
- updated README/current-position text;
- updated release history;
- updated documentation index.

The closure report must focus on criteria and include:

1. Starting public criterion inventory.
2. Phase 6 target portfolio.
3. Final new criteria.
4. Exact source families.
5. Taxonomies.
6. Coverage and missing countries.
7. Scoring and limitations.
8. National versus locality-derived scope.
9. Relationship to original C01, C05, C12-C15.
10. Which original criteria remain only partially addressed.
11. Stretch criteria added or held.
12. Combined PCC behavior.
13. Preference presets.
14. Test and CI results.
15. Remaining source risks.
16. The next-unlock recommendation.
17. Whether structured applicant/context work is now the best next phase.

Be direct. If the next meaningful criteria require applicant context, say so plainly.

## Final criterion accounting

Provide a table covering all 45 Phase 3 criteria with:

- public;
- partially represented by narrowed criterion;
- immediate fast follow;
- needs one additional evidence layer;
- needs profile/context;
- source/construct blocked;
- rejected.

Do not count a narrowed component as the full original criterion.

## Commit history

List every Phase 6 commit in order.

A reasonable closure commit is:

`docs: close Phase 6 career and engineering education`

## Final report to owner

State:

- active release ID;
- total public criteria;
- new Phase 6 criteria;
- blocked/replaced criteria;
- coverage modes;
- replay/CI status;
- next recommended phase;
- the first five criteria that next phase can unlock.

Stop after closure.
