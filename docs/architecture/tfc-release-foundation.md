# TFC rule and immutable release foundation

Status: Phase 7F production evidence staged on the Phase 7D foundation; no activation

## Release boundary

A release-6 TFC candidate is a draft-only immutable overlay on an identified release-5.1 base. The
base checksum preserves the complete ranking, locality and Opportunity Filter release without
copying or mutating it. The candidate binds exactly six checksummed artifacts:

| Artifact | Ownership |
|---|---|
| `tfc-catalog.json` | Staged TFC identities, result families and evaluation-policy IDs. |
| `tfc-destination-rule-evidence.jsonl` | Typed jurisdiction, support, route-rule and metric-formula records. |
| `tfc-policy-bundles.json` | Effective selection, conflict, staleness and negative-result policy. |
| `tfc-source-legal-manifest.json` | Exact source, asset, legal, lineage, parser and refresh metadata. |
| `tfc-coverage-summary.json` | Reconciled explicit TFC-country support counts. |
| `tfc-validation.json` | Reproducible structural and semantic validation result. |

The repository has no publish or activate method. `activation_authorized` and
`promotion_eligible` are always false. Phase 7D's fixture remains visibly `SYNTHETIC_ONLY`;
Phase 7F adds a non-synthetic `RELEASE_CANDIDATE` containing only the three owner-approved checks.

## Typed records

The evidence file is JSON Lines with a bounded `record_type` union. It is not an open payload bag.

- `JURISDICTION` maps country, region, city, institution or regulator identities without
  overloading country codes.
- `DESTINATION_SUPPORT` stores exactly one explicit state for every staged TFC-country pair.
- `ROUTE_RULE` stores named routes, bounded conditions, thresholds, jurisdiction, source
  references and effective periods.
- `METRIC_FORMULA` stores a versioned formula type, units and typed components. Phase 7D uses this
  only to prove the generic synthetic foundation; no metric TFC is product-approved.

Support states are `SUPPORTED`, `EVIDENCE_INSUFFICIENT`, `LEGALLY_BLOCKED`, `STALE`,
`NOT_APPLICABLE_NATIONAL` and `UNSUPPORTED`. Missing rows are invalid and are never interpreted as
unsupported.

## Geography and overrides

Canonical `stable_supported_v1` country identities are reused. More specific jurisdictions carry
their own IDs and canonical country parent. A regional route can identify the national record it
overrides. Runtime evaluation must apply the policy bundle's explicit jurisdiction precedence;
country codes never stand in for route, institution, regulator or service-authority IDs.

## Effective selection

Every route or formula carries effective-from, optional effective-to, source publication date,
verification date, stale-after date, supersession identity and conflict status. The foundation
rejects a `SUPPORTED` row when a selected rule is future, expired, stale or in unresolved conflict.
Historical and blocked records may remain inspectable when the support state says why evaluation
is unavailable.

Rule versions sharing TFC, type, route/metric identity and jurisdiction cannot overlap. A policy
change is a data change in `tfc-policy-bundles.json`, not a hidden parser branch.

## Deterministic assembly

`build_tfc_release_artifacts` normalizes a frozen capture, expands the complete 91-country support
matrix, sorts records by type and identity, generates coverage and validation, and rejects an
invalid candidate. `TfcCandidateReleaseRepository` writes LF-stable JSON/JSONL, binds SHA-256
checksums, validates the release-6 manifest and can replay from the same frozen input.

Replay rebuilds into a temporary directory and compares all six payloads plus `manifest.json`
byte-for-byte. A semantic diff separately reports source input, normalized rule, effective date,
evaluation policy and support-state changes.

## Request-time outcomes

Releases store destination facts and evaluation policies, never applicant-country outcomes.
Applicant, household and scenario facts vary by request, can be incomplete, and have stronger
privacy requirements than immutable public evidence. The Phase 7E engine combines an effective
profile snapshot with a loaded rule bundle at request time. Precomputing the Cartesian product
would be stale, privacy-hostile and impossible to audit against the user's exact snapshot.

The release contracts structurally exclude profile, session, account, rank, affinity, PCC, LSC and
Opportunity Filter state fields. API runtime performs no live source calls.

See the [first-wave evidence](../product/tfc-first-wave-evidence.md),
[source workflow](../operations/tfc-source-workflow.md), [release format](../data/release-format.md)
and [Phase 7F report](../history/phase7f-first-wave-onboarding.md).
