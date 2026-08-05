# ADR 017: TFC assessment independence from ranking and sibling assessments

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

Konsider already separates coverage, locality, profile and Opportunity Filter assessments. TFC
execution must not make the presence of a profile equivalent to a feasibility result.

## Decision

`assessments.profile` summarizes context presence, evaluated dimensions and retention. The sibling
`assessments.feasibility` owns selected TFCs, execution status, country outcomes, required inputs,
source effective dates and any explicitly requested filtered position. Base rank remains canonical.

TFC evaluation never changes affinity, PCC complete-case rules, locality aggregation or Opportunity
Filter evidence. The approved definitions are assessment-only in Phase 7C; explicit route filtering
remains an owner decision before runtime implementation.

## Consequences

Country recommendation and applicant feasibility can disagree without overwriting one another. The
UI can explain the axes independently in later phases.

## Alternatives considered

Placing TFC results inside `assessments.profile` and attaching outcomes to criterion contributions
were rejected because both collapse independent concepts.
