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
