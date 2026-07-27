# Konsider Phase 3 — Criteria Expansion and Source Feasibility

## Purpose

Phase 3 expands Konsider from the current five enabled ranking criteria toward a balanced portfolio of approximately 10–15 production-ready criteria.

It preserves the current evidence-first principles: authoritative sources, explicit production reuse rights, adequate coverage of the stable 91-country universe, acceptable freshness, comparable definitions, deterministic processing, replayability, and explicit rejection evidence.

## Sub-phases

- **3A — Research framework and prioritisation**
  Owner: Web ChatGPT

- **3B — Lightweight screening of all 84 criteria**
  Owner: Desktop ChatGPT Work, or Web ChatGPT

- **3C — Deep source-feasibility research**
  Owner: Desktop ChatGPT Work, in batches of 12–15

- **3D — Generic deterministic feasibility-probe framework**
  Owner: Codex

- **3E — Candidate-specific measured probes**
  Owner: Codex

- **3F — Portfolio selection and guardrail review**
  Owner: Web ChatGPT

- **3G — Production implementation of approved criteria**
  Owner: Codex

- **3H — Closure report and roadmap renumbering**
  Owner: Codex, reviewed by Web ChatGPT

## Recommended order

Run 3A, then 3B. Review both before finalising the first 3C batch. Start 3D only after 3C reveals recurring source and reporting patterns. Run 3E only for approved promising candidates. Complete 3F before any production implementation.

## Roadmap numbering

- New Phase 3: Criteria expansion and source feasibility
- Former deterministic evidence and explanations phase: Phase 4
- Former conversational exploration phase: Phase 5
- Shift later forward-looking phases accordingly

Do not renumber historical completed phases or release records.


---

# Phase 3A — Research Framework and Prioritisation

## Intended for
Web ChatGPT in the existing Konsider project conversation.

## Prompt

Review the current Konsider repository and documentation, especially the source audit, scoring methodology, stable 91-country coverage report, worker publication rules, and the 84-item criteria search-space document.

Focus only on criteria expansion, source feasibility, publishing benchmarks, and research methodology. Park API and UI details.

Create a Phase 3A framework that:

1. Defines a standard evaluation rubric covering:
   - relocation decision value;
   - precise definition;
   - national versus city/regional suitability;
   - authoritative publisher;
   - candidate dataset or indicator;
   - comparability;
   - expected 91-country coverage;
   - freshness and update cadence;
   - licensing clarity;
   - country mapping;
   - scoring feasibility;
   - redundancy;
   - profile dependence;
   - likely readiness;
   - research priority.

2. Classifies all 84 items as one or more of:
   - independent criterion;
   - sub-criterion;
   - profile composite;
   - duplicate or overlapping;
   - city/regional criterion;
   - preference-fit criterion;
   - low-feasibility criterion.

3. Produces an ordered master research list.

4. Selects a balanced first batch of 12–15 criteria.

5. Defines common outcome statuses and rejection reason codes.

6. Recommends standard Markdown and machine-readable report schemas.

7. Produces a complete document that can serve as authoritative input to Desktop ChatGPT Work and Codex.

Do not perform a full source audit for all 84 criteria in this phase.


---

# Phase 3B — Lightweight Screening of All 84 Criteria

## Intended for
ChatGPT Desktop Work.

## Inputs
- Konsider repository
- 84-item criteria search space
- completed Phase 3A framework

## Prompt

Perform a lightweight screening of all 84 criteria using the Phase 3A rubric.

For every criterion:

1. Confirm what it measures.
2. Identify likely authoritative publisher families.
3. Identify likely datasets or indicator families.
4. Estimate cross-country comparability.
5. Estimate whether at least 90% coverage of the stable 91-country universe appears plausible.
6. Estimate likely freshness.
7. Flag licensing uncertainty.
8. Mark its natural granularity: national, city/regional, preference-based, profile-derived, or unsuitable as an independent criterion.
9. Assign a Phase 3A finding status.
10. Assign deep-research priority: high, medium, low, or no further work.

Produce:

- one structured row per criterion;
- concise rationales for non-obvious downgrades;
- a ranked list of approximately 35–45 criteria for deeper research;
- recommended first and second 12–15 criterion batches;
- recurring publisher and dataset families;
- criteria likely to require city-level treatment;
- Markdown plus JSON or CSV output.

Clearly distinguish verified facts from preliminary estimates. Do not write production code or perform exhaustive licensing and coverage audits.


---

# Phase 3C — Deep Source-Feasibility Research

## Intended for
ChatGPT Desktop Work.

## Inputs
- Phase 3A framework
- Phase 3B screening report
- user-approved batch of 12–15 criteria
- current Konsider repository documentation

## Prompt

Conduct a deep source-feasibility investigation for the approved batch.

For each criterion:

1. Define the precise relocation question it answers.
2. Identify the strongest official or authoritative source candidates.
3. Record exact datasets, series, tables, APIs, workbooks, or downloads.
4. Review methodology and comparability.
5. Review exact dataset-specific licensing or reuse evidence.
6. Determine update cadence and latest observation period.
7. Estimate or measure geographic coverage where practical.
8. Evaluate expected coverage of the stable 91-country universe.
9. Identify country and territory mapping complications.
10. Record whether the source is national, city-level, survey-based, modelled, administrative, or composite.
11. Evaluate scoring direction and transformation feasibility.
12. Identify overlap with other criteria.
13. Record material limitations.
14. Recommend:
    - proceed to deterministic probe;
    - experimental only;
    - defer;
    - reject.

Assign explicit rejection reason codes such as no authoritative source, unclear licence, insufficient coverage, stale data, poor comparability, unsuitable granularity, excessive maintenance, redundancy, or indefensible scoring.

Do not implement production ingestion. Do not describe coverage as measured unless the source was actually downloaded or queried.

Produce detailed criterion sections, a comparison table, a Phase 3E shortlist, open decisions, and Markdown plus machine-readable output.


---

# Phase 3D — Generic Deterministic Feasibility-Probe Framework

## Intended for
Codex in the local Konsider repository.

## Inputs
- current repository
- Phase 3A and 3B reports
- at least one completed Phase 3C batch

## Objective

Add a small reusable research framework for measuring candidate-source feasibility. It must not modify active releases, production scoring, the API, or the UI.

## Requirements

1. Reuse current audit, raw-artifact, country-registry, and report conventions where practical.
2. Model:
   - criterion and source candidate IDs;
   - publisher and dataset;
   - access and methodology references;
   - licence evidence;
   - source version and retrieval time;
   - raw artifact checksum;
   - country mapping;
   - observation period;
   - presence, freshness, parse, and validation states;
   - blocker and rejection reason codes.
3. Default to the stable 91-country universe.
4. Generate per-country results and summary counts for found, fresh, parsed, valid, missing, stale, invalid, and unmapped observations.
5. Produce Markdown and machine-readable reports.
6. Keep retrieval and parsing source-specific through small plug-ins or adapters.
7. Do not build an AI-agent or web-search orchestration system.
8. Preserve raw artifacts content-addressed and ignored where appropriate.
9. Support offline replay where practical.
10. Test mapping, freshness, counts, reason codes, deterministic output, and non-modification of active release state.
11. Document how to add and run a probe, and the difference between a probe and production ingestion.

Keep the design minimal and prove it with only one or two fixture-backed examples.


---

# Phase 3E — Candidate-Specific Measured Probes

## Intended for
Codex in the local Konsider repository.

## Inputs
- completed Phase 3D framework
- completed Phase 3C reports
- user-approved source candidates

## Prompt

Implement deterministic feasibility probes for the approved source candidates and measure their actual suitability for the stable 91-country universe.

For each candidate:

1. Use the exact approved dataset, series, table, API, or workbook.
2. Capture raw artifacts, versions, URLs, methodology, and licence evidence.
3. Map source identities to the canonical country registry.
4. Produce one expected result per country.
5. Record success, missing, stale, parse-failed, invalid, rejected, and unmapped outcomes explicitly.
6. Apply the proposed criterion-specific freshness rule without changing production policy.
7. Calculate found, fresh, parsed, validated, missing, stale, invalid, and unmapped counts.
8. Identify excluded and only-blocker countries where meaningful.
9. Support offline replay where possible.
10. Compare measured results with Phase 3C expectations.

These remain research probes. Do not publish a release, add production scoring, impute values, silently substitute indicators, or combine sources unless explicitly approved.

For each candidate produce machine-readable per-country results, raw-artifact inventory, Markdown summary, exact coverage statistics, licensing conclusion, and recommendation: production candidate, experimental candidate, reserve candidate, or reject.

Also produce an aggregate comparison report.


---

# Phase 3F — Portfolio Selection and Guardrail Review

## Intended for
Web ChatGPT in the existing Konsider conversation.

## Inputs
- Phase 3A and 3B reports
- all Phase 3C research reports
- Phase 3E measured reports
- current source, coverage, scoring, and publication documentation

## Prompt

Review all Phase 3 evidence and recommend the strongest balanced portfolio of additional criteria.

Target approximately 10–15 total enabled criteria, including the current five, plus a small reserve set.

1. Compare candidates on decision value, measured coverage, freshness, licensing, comparability, scoring defensibility, redundancy, category balance, and maintenance cost.
2. Recommend production additions, experimental additions, reserve candidates, deferred candidates, and rejections.
3. Ensure the portfolio answers:
   - can I legally move and remain;
   - can I find work or education;
   - can I afford life there;
   - will my family be safe and healthy;
   - can we function and integrate;
   - is infrastructure dependable;
   - does the environment fit our preferences.
4. Review existing guardrails:
   - freshness;
   - complete-country coverage;
   - minimum ready criteria;
   - source authority;
   - licensing;
   - imputation;
   - partial-country scoring;
   - national versus city granularity;
   - composites;
   - survey indicators.
5. For every proposed relaxation, state the current rule, proposed rule, quantified benefit, quality cost, visible caveats or fallback, and recommendation.
6. Prefer criterion-specific exceptions over broad weakening.
7. Recommend the Phase 3G implementation order.

Produce a repository-ready decision document. Do not implement code.


---

# Phase 3G — Production Implementation of Approved Criteria

## Intended for
Codex in the local Konsider repository.

## Inputs
- user-approved Phase 3F decision
- exact approved sources, definitions, guardrails, and scoring rules

## Prompt

Implement only the approved Phase 3 criteria as production-grade Konsider criteria.

For each criterion:

1. Add an audited source registration with exact version, methodology, licence evidence, redistribution decision, attribution, limitations, and parser version.
2. Implement deterministic retrieval and parsing.
3. Produce source-neutral observations with exact provenance.
4. Implement the approved versioned scoring transformation.
5. Add criterion-specific readiness validation for coverage, freshness, units, types, flags, provenance, attempts, checksums, schemas, and versions.
6. Preserve missing, stale, rejected, and incomparable results explicitly.
7. Add sensitivity and redundancy diagnostics where required.
8. Add parser, mapping, scoring, readiness, failure, replay, publication, and catalog tests.
9. Publish a new immutable release only if all approved requirements pass.
10. Update source audit, scoring methodology, coverage report, release report, worker documentation, roadmap, and implementation history as needed.

Do not use fixture fallback, unapproved imputation, source substitution, silent partial scoring, duplicated API/UI business rules, or modification of historical releases.

Experimental criteria must remain visibly experimental, and non-ready criteria must remain excluded from ranking.


---

# Phase 3H — Closure Report and Roadmap Renumbering

## Intended for
Codex in the local Konsider repository, followed by Web ChatGPT review.

## Prompt

Close Phase 3 and update forward-looking documentation without rewriting history.

1. Create a closure report covering:
   - the 84-item search space;
   - screening methodology;
   - criteria deeply researched;
   - sources probed;
   - production additions;
   - experimental, reserve, deferred, and rejected criteria;
   - rejection reasons;
   - final country coverage;
   - final enabled criterion count;
   - guardrail decisions;
   - limitations;
   - refresh recommendations.
2. Preserve rejected research evidence.
3. Update the roadmap:
   - Phase 3: criteria expansion;
   - former deterministic evidence and explanations: Phase 4;
   - former conversational exploration: Phase 5;
   - shift later future phases accordingly.
4. Do not renumber historical completed phases or historical release records.
5. Update documentation links and indexes.
6. Add a concise Phase 4 recommendation.
7. Run documentation checks and normal repository quality gates.

Deliver the closure report, updated roadmap and index, implementation-history entry where appropriate, quality-gate results, and a concise outcome summary.
