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
