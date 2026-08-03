# ADR 010: Opportunity Filters as a separate filter-only product contract

Status: accepted

Date: 2026-08-03

## Context

Phase 6B.1 and Phase 6C approved five career and four education ecosystem signals for staged
implementation. They are not ordering criteria: selecting one is intended to restrict the ranked
country set, not add weight, change affinity, or reinterpret missing evidence. Treating OFC as a
peer of FCC, PCC or LSC would mix product role, evidence coverage and geographic scope in one
classification.

The public evidence is deliberately tri-state. A complete route that does not cross a strong
threshold supports a narrow “strong signal not established” conclusion. Missing, stale, partial,
incompatible, legally blocked or otherwise unsafe evidence supports no negative conclusion.

## Decision

The public product name is **Opportunity Filters**. `OFC` is internal shorthand only. The domain
concepts are `OpportunityFilterDefinition`, `OpportunityFilterEvidence`,
`OpportunityFilterState` and `OpportunityFilterAssessment`.

Opportunity Filters use a sibling catalog and evidence family. They do not enter the ordering
criterion catalog or carry weight, direction, normalization, score, PCC activation, imputation or
ranking coefficients. Product role, evidence coverage, geographic scope and applicability remain
orthogonal fields.

The public states are exactly:

- `VERIFIED_STRONG_SIGNAL`;
- `STRONG_SIGNAL_NOT_ESTABLISHED`; and
- `INSUFFICIENT_EVIDENCE`.

There is no negative-opportunity state. Missing data is not negative data. State and confidence are
separate: confidence describes the evidence route; state describes its result under a frozen
policy.

The initial filter behavior is strict. A country passes only on `VERIFIED_STRONG_SIGNAL`; all
selected filters are required. The two excluding states retain distinct reason codes and
explanations. An empty result is valid. No-filter requests preserve the canonical result exactly.

Filters are evaluated only after the canonical ranking and its complete-case evidence have been
computed. Filtering preserves affinity scores and relative survivor order. It does not join PCC
missing unions, trigger imputation, alter LSC aggregation or change coverage/locality/profile
assessments. A future sibling `assessments.opportunity` owns selected filters, state exclusions,
base rank and filtered rank.

Release 5.1 may optionally bind a checksummed Opportunity Filter catalog, country evidence, source
manifest, threshold policies, evidence policy and coverage summary. Release 5.0 remains valid
without these fields. A declared bundle must contain one explicit state for every filter-country
pair; runtime code never infers omitted rows as insufficient.

## Consequences

- Existing rankings, active release 5.0, API v2 and UI remain unchanged in Phase 6D.
- Career and education metric payloads can evolve behind separate typed versions without a false
  common numeric schema.
- Strict filtering can reduce the result to zero countries, which later API and UI phases must
  explain rather than undo.
- Evidence onboarding must preserve source identity, legal status, thresholds, confidence,
  route attribution, explicit missingness and deterministic release checksums.
- Adding a filter requires a new immutable release; research approval alone cannot activate one.

## Alternatives considered

Adding `OFC` to the FCC/PCC/LSC enum was rejected because those labels answer different questions.
Representing Opportunity Filters as zero-weight criteria was rejected because it would expose
ranking fields and invite scoring or PCC behavior. A binary state was rejected because it would
collapse complete below-threshold evidence and missing evidence. OR semantics and soft boosts were
rejected for the initial release because they make exclusion and ordering behavior less legible.

## Revisit when

The owner authorizes a different combination mode, applicant-context-dependent eligibility,
institution-level access, or a score-bearing opportunity concept. Each requires a new product and
contract decision; none may be inferred from the Phase 6 destination-side ecosystem signals.
