# Phase 7 Owner Decision Checklist

Use this after Phase 7B and before Phase 7C.

## Terminology

- [ ] Approve **Typed Feasibility Check (TFC)**
- [ ] Approve user-facing language: Feasibility checks / Your situation / Your feasibility

## Minimum gate

- [ ] At least three TFCs are production-qualified
- [ ] No gate was weakened to reach three
- [ ] First wave contains no more than five unless explicitly justified

## First-wave scope

For each approved TFC:

- [ ] Stable ID
- [ ] Public name
- [ ] Original criterion mapping
- [ ] Exact user question
- [ ] Check kind
- [ ] Required profile inputs
- [ ] Scenario inputs
- [ ] Supported destination boundary
- [ ] Supported applicant boundary
- [ ] Source route
- [ ] Legal/reuse conclusion
- [ ] Effective-date/refresh policy
- [ ] Public limitation
- [ ] Assessment-only or explicit filtering capability

## Product behavior

- [ ] Guest use remains fully supported
- [ ] Profile context is optional
- [ ] No login in Phase 7
- [ ] No server-side profile persistence
- [ ] Browser memory/session is default
- [ ] Remember-on-device requires explicit consent
- [ ] TFCs do not change affinity
- [ ] TFCs do not change OFCs
- [ ] TFCs do not change PCC/LSC behavior
- [ ] Explicit feasibility filtering, if allowed, preserves base rank and score

## Privacy

- [ ] Only purpose-bound fields are requested
- [ ] Sensitive fields are optional
- [ ] Unknown values are not inferred
- [ ] No profile data in URLs
- [ ] No request-body logging
- [ ] No raw profile analytics
- [ ] Clear/export/import behavior approved
- [ ] Synthetic fixtures only

## Architecture

- [ ] Applicant profile, household and scenario are separate
- [ ] Evaluation uses an explicit immutable snapshot
- [ ] Destination rules/evidence are stored, not profile × country outcomes
- [ ] Future account persistence is an adapter, not a Phase 7 dependency
- [ ] Old releases remain immutable and inspectable

## Stop decision

- [ ] Proceed to Phase 7C
- [ ] Stop as research-only because fewer than three TFCs qualified
- [ ] Request targeted Phase 7B follow-up before deciding
