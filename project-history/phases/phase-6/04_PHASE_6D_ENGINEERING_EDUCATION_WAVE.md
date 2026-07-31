# Phase 6D Prompt — Engineering-Education Criterion Wave

## Dependency

Proceed only after:

- Phase 6B shared foundation is complete;
- Phase 6A approved the education constructs;
- Phase 6C career wave is stable.

## Objective

Implement and publish the approved education criteria as one coherent wave.

The intended minimum set is:

1. Engineering higher-education capacity.
2. Engineering academic and research ecosystem.

Also include ICT higher-education capacity if approved and supported by the same UIS evidence.

Do not implement applicant admission probability, tuition affordability, accreditation accessibility, or post-study migration in Phase 6.

## Criterion 1 — Engineering higher-education capacity

### Meaning

Answer:

> How substantial and specialized is tertiary engineering education in this country?

Do not imply:

- that programmes are high quality;
- that programmes are accredited;
- that an international student can enter them;
- that tuition is affordable;
- that teaching is in English;
- that graduates obtain jobs.

### Evidence

Use the exact approved UIS indicators and dimensions.

Retain:

- field code;
- level;
- sex dimension;
- measure;
- unit;
- reference year;
- status/quality flags;
- country mapping;
- source metadata.

### Metric

Implement the Phase 6A-approved simple metric.

If capacity and specialization are blended:

- show both components;
- freeze their weights;
- test sensitivity;
- ensure a high field share with tiny absolute scale does not dominate;
- ensure very large countries do not dominate solely due to population.

If only one component has adequate coverage, use a truthful narrower construct rather than a fragile composite.

### Coverage

Classify all 91 countries explicitly.

Do not fill missing annual values from unrelated sources.

Use a clear freshness policy suitable for education statistics, which may update more slowly than labour statistics.

## Criterion 2 — Engineering academic and research ecosystem

### Meaning

Answer:

> How strong and geographically concentrated is this country's recent engineering academic and research ecosystem?

Do not imply:

- undergraduate teaching quality;
- admissions;
- programme accreditation;
- research employment access;
- innovation commercialization;
- personal university fit.

### Evidence acquisition

Use the approved pinned OpenAlex capture and ROR release.

The production release must not depend on live API calls.

Freeze:

- snapshot/capture date;
- queries or filters;
- data version;
- checksums;
- selected time window;
- field taxonomy mapping;
- institution identity mapping;
- source licence.

### Institution and locality mapping

Map institution evidence to canonical Konsider geographic entities.

Requirements:

- exact institution IDs;
- exact country;
- deterministic locality mapping;
- explicit multi-campus policy;
- explicit treatment of institutions outside the selected locality universe;
- rejected/unmapped records retained in reports;
- no silent nearest-city guess beyond an approved distance/boundary rule.

If institution is valid nationally but cannot be mapped to a selected locality, decide whether it contributes to a national-only component or is excluded. The decision must be consistent and documented.

### Locality aggregation

Use the Phase 5 policy-driven LSC foundation.

Do not automatically reuse the climate locality universe/policy without testing suitability.

Evaluate whether the existing major urban-centre universe is acceptable for academic institutions. If a new institution-oriented locality universe is required, version it and justify it.

The country result should expose:

- contributing institutions;
- contributing localities;
- locality scores;
- aggregation policy;
- full valid locality evidence;
- source lineage.

### Metric

Use a recent multi-year window.

Prefer a transparent combination of:

- engineering research scale;
- breadth/number of active institutions;
- field-normalized impact if robust.

Avoid raw citation totals alone.

Use fractional institutional attribution where needed to prevent multi-institution works from being counted fully multiple times.

### Overlap with existing C05

The new criterion must earn its place.

Report:

- correlation with existing Research and innovation ecosystem;
- correlation with country size;
- examples where field-specific/locality evidence changes interpretation;
- whether the new criterion should coexist, replace a component, or remain experimental.

Do not remove the broad criterion without a separate approved product decision.

## ICT higher-education capacity stretch

If approved, derive it from the same UIS capture and education-field taxonomy.

Apply the same construct discipline.

Do not conflate ICT education capacity with technology labour-market depth. They should be independently weightable and may diverge.

## Portfolio coverage

For every education criterion report:

- valid/missing/stale/invalid/rejected countries;
- coverage mode;
- individual activation effect;
- missing-country union with all existing PCCs and career-wave PCCs;
- behavior under general, technology, engineering-career, and engineering-education presets.

Do not weaken the coverage policy.

## Release strategy

Publish the approved education criteria in one additive immutable release after the career release.

Include:

- source captures and checksums;
- taxonomy snapshots;
- institution mappings;
- locality universe/policies where applicable;
- criterion policies;
- outcomes;
- observations;
- scores;
- derived country evidence;
- catalog snapshot;
- replay verification.

Do not activate the release until both national and locality-derived evidence pass validation.

## API and UI

Use current generic structures.

Make only minimal additions required for:

- education/career domain organization;
- institution evidence;
- contributor localities;
- source and time-window explanation;
- new engineering-education preset;
- experimental labels and caveats.

Do not add applicant admission fields.

## Tests

Cover:

- UIS field parsing;
- count/share consistency;
- stale/missing education data;
- OpenAlex capture replay;
- ROR identity;
- institution/locality mapping;
- fractional attribution;
- field mapping;
- locality aggregation;
- one-locality and multiple-locality countries;
- unmapped institutions;
- overlap/correlation report generation;
- combined PCC coverage;
- API comparison/details;
- UI evidence display;
- full release replay.

## Critical-blocker and replacement rule

If Engineering academic and research ecosystem fails a genuine critical gate:

1. do not publish a weak proxy;
2. record the exact blocker;
3. publish ICT higher-education capacity or another Phase 6A-approved stretch criterion if it clears all gates;
4. keep Engineering academic ecosystem as a named held criterion with a concrete reopening condition.

The phase-level goal remains at least four new criteria, but not by lowering standards.

## Required report

Create a Phase 6D report including:

- final public names;
- Phase 3 lineage;
- exact assets;
- licensing;
- taxonomy;
- coverage;
- scoring;
- institution/locality mapping;
- overlap with C05;
- release inventory;
- limitations;
- held/replacement decisions.

## Commits

Prefer:

1. `feat: add engineering education criteria`
2. `data: publish Phase 6 education criteria release`

Stop after the education release.
