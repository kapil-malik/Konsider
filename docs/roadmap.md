# Konsider Roadmap

Status: worker-first roadmap

Last updated: 2026-07-18

Supersedes the fixture-first product sequence in `konsider_context.md`. The fixture repository remains
test-only; fixture scores are not evidence and cannot enter a real dataset release.

## Completion Gate

Current state: **blocked / not green**. Release `2026-07-18.2` passes structural validation, but
product readiness remains false until WHO GHO and WPS workbook reuse rights are cleared and the ICP
criterion is narrowed or presented without a precise strict-rank interpretation.

The live engine, FastAPI surface, React UI, retrieval, explanations, LLM chat, agents, SSE, MCP, and
cloud deployment are blocked until a local release demonstrates all of the following:

- at least five defensible criteria backed by reproducible official or clearly identified independent
  sources across the 20-country experiment set;
- immutable raw bytes plus URL, retrieval time, HTTP metadata, checksum, source version, and parser
  version;
- normalized observations that retain year, unit, geographic scope, and reported/modelled/imputed or
  derived status;
- explicit missing, stale, incomparable, and rejected records without substituted estimates;
- versioned, transparent scoring experiments and sensitivity results;
- a validation report that passes schema, range, coverage, freshness, duplication, and provenance
  checks;
- immutable draft-to-published promotion and replay tests that reproduce observations and scores.

A criterion that fails the gate is narrowed, redefined, or deferred. Missing data is never filled with
fixture-era scores.

## Stage 1: 20-Country Feasibility Spike

Evaluate India, Singapore, Canada, Australia, Germany, Netherlands, Switzerland, United States,
United Kingdom, United Arab Emirates, France, Sweden, Denmark, Norway, Ireland, New Zealand, Japan,
South Korea, Spain, and Portugal using stable ISO alpha-3 codes.

For every proposed source, verify the current official download or documented API, methodology,
coverage, reference period, update cadence, usage/attribution terms, and redistribution constraints.
Record the result in the source catalog even when the source is rejected.

Initial decisions:

1. Air pollution exposure: WHO population-weighted modelled PM2.5. The unevenly monitored WHO
   ground-measurement database is retained as reconnaissance evidence but is not used to rank countries.
2. Serious violent-crime risk: intentional homicide per 100,000, with UNODC lineage and source type.
3. Healthcare service access: WHO UHC Service Coverage Index (SDG 3.8.1), not expat healthcare quality.
4. Relative national price level: World Bank ICP household-consumption PPP relative to market exchange,
   anchored to the 2021 benchmark; it is not a city budget.
5. Women's inclusion, justice, and security: latest downloadable GIWPS/PRIO WPS Index data, preserving
   composite and imputation caveats.
6. Infrastructure: component feasibility only until coverage, correlation, weighting, and sensitivity
   tests justify a composite.

## Stage 2: Observation, Provenance, and Release Contracts

Implement source registrations, immutable content-addressed raw artifacts, source-neutral observations,
quality flags, validation reports, draft releases, atomic publication, active-release pointers, and replay.
Contracts are finalized from the real source schemas rather than from fixture tables.

## Stage 3: WHO Air-Quality Vertical Slice

Deliver source registration -> HTTP capture -> immutable artifact -> parser -> normalized modelled PM2.5
observations -> validation -> draft release -> publication -> replay. Publication must fail on missing
provenance, duplicates, invalid units/ranges, or insufficient country coverage.

## Stage 4: Worker Expansion

Add one source family at a time, rerunning the full release gate after each:

1. UNODC intentional homicide and WHO UHC.
2. World Bank ICP household price-level inputs and derivation.
3. WPS Index overall and dimension data where terms permit redistribution.
4. Infrastructure components from World Bank, UN DESA, and ITU; do not publish a composite until the
   sensitivity study passes.

## Stage 5: Scoring Experiments

Explore policy-threshold bands and winsorized min-max/percentile transformations using real
distributions. Every score retains input observation IDs, direction, transform parameters, method
version, and sensitivity results. Scores use modest precision and never imply source certainty that is
not present.

## Stage 6: First Published Local Dataset

Publish an immutable release only after at least five criteria pass. Keep fixtures isolated for unit tests.
Document what every observation and score means, does not mean, and how stale/modelled/imputed data is
shown. This stage is the prerequisite for all live-product work.

## Deferred Product Sequence

After the completion gate, and only then:

1. Build the framework-free live ranking service and FastAPI endpoints against one published release.
2. Build the React comparison UI.
3. Add structured evidence lookup and deterministic explanations.
4. Add retrieval only when metadata/lexical lookup is insufficient.
5. Add LLM chat, typed events/SSE, agents, and MCP after deterministic behavior is proven.
6. Add AWS storage and scheduling adapters after local worker operations are reliable.

## Delivery Rules

- Each meaningful source or infrastructure increment ends with tests and updated source/methodology docs.
- Published releases and local raw artifacts are immutable; corrections produce new IDs. Raw
  third-party bytes are ignored by Git unless an audited source licence explicitly permits
  redistribution.
- The worker never manufactures observations or scores for missing source data.
- Source-specific parsing stays isolated; scoring logic is not duplicated in worker, API, or UI.
- Live requests never depend on external source availability.
- Product-stack work remains out of scope until the release gate is demonstrably green.
