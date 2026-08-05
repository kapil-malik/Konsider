# Phase 7F first-wave evidence onboarding

Status: complete on `2026-08-05`; owner-authorized source inventory staged, not activated

## Delivered

Phase 7F converted the three Phase 7B-approved checks into production-shaped immutable artifacts:

- 3 catalog definitions and policy bundles;
- 87 exact official page/route bindings across 29 destinations;
- 116 named route rules: 29 skilled-work, 58 family and 29 post-study;
- 273 explicit destination support records across all 91 stable countries;
- 5 source/legal registrations;
- a passed Phase 7B-to-production reconciliation;
- candidate `phase7f-first-wave-2026-08-05.6.0`; and
- deterministic build and replay tooling.

The candidate binds the existing active release `2026-08-04.1` by ID and checksum. It is
non-synthetic but remains `draft` with `activation_authorized: false`. No active release, API,
OpenAPI, UI, profile persistence, authentication, affinity, PCC, LSC or Opportunity Filter file
was changed.

## Owner-authorized reconciliation decision

Phase 7B retained source-family references rather than exact per-destination route identities. The
owner explicitly authorized Phase 7F to create and freeze the missing inventory within those
approved families under the discrepancy policy. Production support matches Phase 7B exactly at
29 destinations per TFC; all remaining countries stay unsupported. The reconciliation report has
no unresolved support discrepancies.

The source review preserved narrower page meanings rather than flattening them. Cyprus uses its
mobile master's/doctoral post-study boundary. Sweden uses the official in-country
student-to-worker status-change pathway. Canada official pages were captured through the rendered
browser DOM after direct worker requests proved unreliable; URL, byte count and checksum are
retained and raw DOM is not stored.

## Policy boundary

All three policy bundles are version `1.0`, route-only, assessment-only and
`POSITIVE_CONDITIONAL_ONLY`. Every production rule adds external-authority confirmation, so a
machine profile match remains conditional. A profile that does not satisfy the named rules cannot
produce an authorized negative route conclusion. Unsupported, stale, conflicting and missing
evidence remain explicit non-positive states.

## Verification

The Phase 7F suite covers inventory identity, source checksums, parser verification, 91-country
support completeness, route uniqueness, effective dates, input alignment, synthetic profile
evaluation, support-count reconciliation, absence of profile/ranking/OFC data, candidate
non-activation and deterministic regeneration/replay. The full repository suite is the final
regression gate recorded in the implementation closeout.

Machine-readable evidence lives in
`data/reports/phase7f-2026-08-05/`. Product interpretation and replay instructions live in the
[first-wave evidence guide](../product/tfc-first-wave-evidence.md).

## Phase 7G gate

Phase 7G may add profile-context and TFC API behavior only after owner acceptance of this staged
inventory and policy. It must load a deliberately selected release-6 candidate, preserve guest
privacy and retain the same no-ranking-change boundary. Phase 7F itself exposes nothing publicly.
