# Phase 6F Prompt — Next-Criterion Unlock Map and Applicant-Context Boundary

## Dependency

Proceed only after Phase 6E confirms the Phase 6 portfolio is coherent.

## Objective

Use actual Phase 6 evidence to state clearly what should be built next to unlock more Phase 3 criteria.

Do not implement a full applicant/profile scoring engine in this phase.

Do not avoid recommending applicant/context work merely because it is larger than another data-only criterion.

## Required analysis

Revisit all remaining unpublished Phase 3 criteria, especially:

- C01 Overall higher-education opportunity;
- C06 International-student accessibility;
- C12-C15 occupation-specific jobs;
- C17 Average earning potential;
- C21-C22 tax/contribution burden;
- C25 Housing affordability;
- C26 Healthcare affordability;
- C32-C36 migration pathways;
- C38 Professional licensing;
- C40 English usability;
- C50 Healthcare capacity;
- C76 Social protection.

Account for the narrowed Phase 6 criteria. Do not claim full C01/C12/C15 completion if Phase 6 only implemented one destination-level component.

## Unlock categories

Classify each remaining criterion into one of these groups:

### A. Immediate reuse

Can be added mostly through existing Phase 6 sources/taxonomies.

Examples may include:

- healthcare employment-market depth;
- business and finance employment-market depth;
- ICT education capacity;
- medical/health education capacity.

These should be recommended as fast follows only if they were not already onboarded.

### B. One additional evidence layer

Requires one substantial new source family but not a full profile engine.

Examples:

- occupation-specific earnings;
- university programme/accreditation inventory;
- tuition and scholarship evidence;
- live or recent vacancy evidence;
- programme teaching language.

For each, identify the exact missing evidence layer and source candidates.

### C. Typed applicant/context engine

Cannot be answered honestly without user-specific inputs.

Examples:

- personal job accessibility;
- professional licensing accessibility;
- university admission fit;
- housing affordability for a household;
- personal tax burden;
- visa and migration pathways;
- co-location of household careers.

For each, identify the minimum context fields.

### D. Still blocked by source/licensing/construct

Not ready even with profile context.

State precise blockers.

## Minimal future context vocabulary

Design a simple next-phase context model using Phase 6 taxonomy IDs.

The design should be minimal and practical.

At minimum consider:

### Applicant

- age band where legally/materially relevant;
- citizenship/current residence;
- occupation family;
- years/seniority;
- qualification field;
- qualification level;
- qualification country;
- languages;
- regulated-profession status.

### Student

- education field;
- intended degree level;
- current curriculum/qualification;
- academic result range;
- budget range;
- teaching language;
- international-student status.

### Household

- members;
- which career/education need belongs to which member;
- co-location preferred or required;
- household income/budget;
- dependants.

Do not turn this into an exhaustive immigration form.

## Separate ecosystem from accessibility

Propose a future scoring pattern:

```text
destination ecosystem score
+ applicant accessibility assessment
+ household/co-location assessment
```

The existing Phase 6 opportunity criteria should remain valid evidence and should not be replaced by opaque personalized scores.

A future applicant result may qualify or constrain the interpretation.

## Decide the next best phase honestly

Choose one of:

1. **Structured applicant and household context**
2. **Additional career/education data wave**
3. **Another source-limited criterion family**

Use evidence from Phase 6.

Decision guidance:

- If the shared source backbone has obvious high-value approved criteria not yet onboarded, a short data fast-follow may be justified.
- If further meaningful criteria require admissions, licensing, earnings, visa, tax, household, or qualification context, recommend the applicant/context phase directly.
- Do not keep adding broad proxies merely to avoid profile work.

## Next-phase candidate plan

Provide:

- recommended next phase title;
- top 5 criteria it could unlock;
- required context fields;
- required source layers;
- architecture changes;
- estimated sequencing;
- criteria that should remain deferred;
- what Phase 6 infrastructure will be reused.

## Required outputs

Create:

- `docs/product/phase6f-next-criterion-unlock-map.md`
- machine-readable remaining-criteria matrix;
- a concise ADR/design note for future context references;
- roadmap update with the honest next phase.

No active runtime change is required unless small metadata corrections are necessary.

## Commit

Suggested commit:

`docs: define post-Phase 6 criterion unlock path`

Stop and present the recommendation plainly.
