# Phase 6E Prompt — Portfolio Integration and Product Validation

## Dependency

Proceed only after the career and education releases are published locally and replay successfully.

## Objective

Validate the new criteria as a coherent product portfolio, not merely as individually valid datasets.

Do not add unrelated new source families in this phase.

## Criterion inventory

Produce a definitive inventory of:

- all previously enabled criteria;
- all Phase 6 criteria;
- diagnostic-only criteria;
- held Phase 6 candidates;
- Phase 3 lineage;
- coverage mode;
- scope;
- experimental status;
- default-enabled status;
- preset membership.

Confirm that at least four new criteria are public unless a critical blocker is documented.

## Semantic separation

Validate and document these distinctions:

### Overall job market versus occupation market

- Overall job-market opportunity measures broad labour-market conditions.
- Technology/engineering/healthcare/business criteria measure occupation-family market depth.
- Neither measures applicant accessibility.

### Education capacity versus academic ecosystem

- Higher-education capacity measures education production/participation.
- Academic ecosystem measures institution/research strength and concentration.
- Neither measures admission probability or tuition affordability.

### Education versus employment

- Engineering education capacity and engineering employment depth are related but independent.
- Avoid combining them into one hidden composite.
- Allow users and presets to weight them separately.

## Redundancy and correlation analysis

For every new criterion compute:

- correlation with relevant existing criteria;
- correlation among Phase 6 criteria;
- rank contribution;
- countries most affected;
- sensitivity to weight 0.2, 0.4, 0.6, 0.8, and 1.0;
- score distribution;
- outliers.

Investigate at least:

- Technology employment versus Overall job market.
- Engineering employment versus Overall job market.
- Technology versus Engineering employment.
- Engineering education capacity versus School education quality.
- Engineering academic ecosystem versus Research and innovation ecosystem.
- Engineering education capacity versus academic ecosystem.
- ICT education versus Technology employment, if present.

High correlation is not automatic rejection, but the report must explain distinct decision value.

## Coverage-union analysis

This is a hard gate.

Adding many PCCs can make a request exceed the Phase 4/5 missing-union limit.

Test:

- each new criterion alone;
- career criteria together;
- education criteria together;
- all Phase 6 criteria together;
- all existing PCCs plus all Phase 6 PCCs;
- every public preference preset;
- representative custom weight combinations.

For each report:

- active PCCs;
- excluded-country union;
- eligible count;
- coverage status;
- fallback behavior;
- top-K robustness.

Do not modify the hard coverage limit merely because the portfolio grew.

## Preference-preset strategy

Create a small, useful preset portfolio.

Consider:

- General balanced;
- Technology career;
- Engineering career;
- Engineering education;
- Career and education.

Rules:

- do not create many near-duplicate presets;
- no preset may hide that it is specialized;
- validate every preset's PCC union;
- specialized criteria may default to zero outside relevant presets;
- preserve user ability to configure all criteria manually;
- do not call presets applicant profiles.

If a desired preset would trigger coverage-limit fallback, redesign its weights or clearly decide not to publish it.

## Product copy

Ensure criterion descriptions say exactly what is measured.

Required phrases or equivalent ideas:

- “employment-market depth, not live vacancies or personal hiring probability”;
- “education capacity, not admission likelihood or teaching quality”;
- “academic and research ecosystem, not programme accreditation or student fit”;
- “profile assessment remains unevaluated because no applicant context is supplied.”

Avoid overly defensive text in the main UI. Keep concise wording in controls and fuller caveats in details/Data & Sources.

## API/UI integration check

Do not redesign the API or UI unless evidence requires it.

Verify:

- catalog-driven rendering;
- structured coverage/locality/profile assessments;
- national and locality-derived contributions;
- institution/locality evidence;
- unavailable outcomes;
- comparisons;
- country details;
- mobile behavior;
- accessibility;
- source and methodology pages;
- preset behavior.

The browser must not calculate taxonomy membership, scores, coverage unions, or locality aggregation.

## Ranking scenarios

Create golden scenarios for:

1. Technology career only.
2. Engineering career only.
3. Engineering education only.
4. Combined engineering employment and education.
5. Strong education but weak employment country.
6. Strong employment but weak education country.
7. Common and non-common locality behavior where academic ecosystem is active with other LSCs.
8. Multiple active PCCs within limit.
9. Multiple active PCCs exceeding limit.
10. Excluded country retaining available evidence.
11. All specialized weights zero.
12. General preset.

Use both synthetic invariants and active-release evidence.

## Required corrections

Fix:

- misleading names;
- caveats;
- preset weights;
- duplicated criterion family metadata;
- catalog readiness;
- API/UI evidence omissions;
- test gaps;
- documentation inconsistencies.

Do not change source values or score methods merely to make rankings look intuitive. Any scoring correction requires evidence and a new immutable release.

## Required outputs

Create:

- `docs/product/phase6e-career-education-portfolio.md`
- a machine-readable correlation/sensitivity report;
- a PCC union/preset report;
- active release examples;
- final preset definitions;
- product wording and limitations.

## Commit

Suggested commit:

`feat: integrate Phase 6 career and education portfolio`

Stop and report:

- total enabled criteria;
- Phase 6 criteria;
- default and specialized presets;
- coverage-union findings;
- remaining product risks.
