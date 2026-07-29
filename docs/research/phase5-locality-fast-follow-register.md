# Phase 5 locality onboarding fast-follow register

Date: 2026-07-29

This register overlays production-onboarding state on the complete 45-criterion
Phase 5A disposition matrix. The immutable detailed source for every criterion
remains
`data/reports/phase5a-2026-07-28/criterion-disposition-matrix.json`.

Two locality-scoped criteria are now experimentally production-onboarded:
C66 Extreme heat exposure and C67 Projected warm-day frequency (2030), most recently in release
`2026-07-29.2`. The other 43 criteria
retain their Phase 5A dispositions until their own onboarding decisions.

## Complete not-onboarded inventory

| Current queue | Count | Criterion IDs | Next action |
| --- | ---: | --- | --- |
| Second wave | 2 | C05, C68 | Resolve each criterion's listed construct, source, coverage, and scoring blockers before any onboarding approval |
| Research only | 7 | C11, C16, C42, C50, C56, C57, C58 | Retain as research; do not promote without materially new evidence |
| Profile phase | 21 | C01, C06, C08, C12, C13, C14, C15, C17, C21, C22, C25, C26, C32, C33, C34, C35, C36, C38, C40, C45, C76 | Revisit only with explicit applicant or household context |
| Reject locality proxy | 13 | C19, C29, C30, C48, C49, C53, C54, C62, C69, C70, C71, C75, C78 | Keep national; do not create locality-derived country proxies |
| **Total not onboarded** | **43** | **All except C66 and C67** | Track through Phase 5 closure and later roadmap work |

The categories are not coverage modes. FCC/PCC is a country-result coverage
classification; national/locality-derived is a scope classification. A future
criterion can therefore be FCC + LSC or PCC + LSC independently.

## Next fast-follow recommendation

**Primary candidate: C05 Research and innovation ecosystem, but only after its larger source and
identity blockers are resolved.**

Why C67 left the queue:

- it was narrowed to one explicit, documented field: `CL_WDS_245_2030`;
- the source unambiguously defines percentage-of-days and zonal-average semantics;
- all 388 selected urban centres contain valid values, producing 89/91 PCC coverage;
- release `2026-07-29.2` passed replay and product-readiness gates.

### Alternatives

| Candidate | Position | Reason |
| --- | --- | --- |
| C05 Research and innovation ecosystem | Primary remaining candidate | The exact OpenAlex quarterly manifest and 330 GB snapshot workflow are not frozen; institution-to-locality mapping and field normalization are substantial. The active release already contains a national C05 criterion sourced from WIPO, so locality onboarding also requires an explicit identity/migration decision. |
| C68 Natural-disaster risk | Defer | The available occurrence fields end in 2015 and do not measure severity, vulnerability, or expected loss. That makes current relocation guidance materially weaker even if mapping is easy. |

## Promotion rules

A queued criterion advances only through its own Phase 5G run. Shared
infrastructure may reduce implementation work, but it does not inherit another
criterion's source, construct, coverage, freshness, scoring, replay, or product
value approval. One criterion and one immutable release per successful
onboarding remain the default.
