# ADR 012: Separate applicant, household and exploration scenario

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

Citizenship and qualifications are relatively stable; household composition changes independently;
job offers, study plans, destination and target date belong to an exploration scenario.

## Decision

Use three versioned contracts: `ApplicantProfile`, `HouseholdProfile` and `ExplorationScenario`.
Preference presets remain weight-only. Applicant profiles contain no authentication fields, and a
scenario explicitly selects TFC IDs and destinations. Age in years is normal; exact date of birth is
exception-only when a dated legal boundary cannot be evaluated otherwise.

## Consequences

The same applicant facts can be reused across scenarios without mutating them. Unknown values stay
explicit, and the product can request only fields consumed by the selected checks.

## Alternatives considered

One large profile object was rejected because it conflates stable identity, household and intent.
Using an account record was rejected because it creates hidden context and persistence coupling.
