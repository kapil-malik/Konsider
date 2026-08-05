# Phase 7I cross-feature UI test plan

Status: implemented

Date: 2026-08-05

## Automated matrix

| Area | Assertion | Coverage |
| --- | --- | --- |
| Request composition | Applied weights/preset, strict OFC IDs and `ASSESS_ONLY` TFC selection are sent together. | Vitest + Playwright |
| Affinity | TFC presence does not change score, contribution, base rank or filtered rank. | Pytest + component |
| Coverage | PCC excluded set and unavailable aggregate cells remain unchanged. | Pytest + existing component |
| Locality | LSC aggregate/common-locality states remain API-owned and separate. | Pytest + Playwright |
| Opportunity | OFC pass/fail evidence and strict-AND exclusions survive TFC assessment unchanged. | Pytest + Playwright |
| Feasibility | Match, conditional, no-match, input-required, unsupported and insufficient states remain typed. | Pytest + Vitest |
| Explanation | Six approved cross-feature statements are deterministic and bounded. | Vitest |
| Details | Order is rank, coverage, locality, opportunity, feasibility, assumptions/sources. | Component + Playwright |
| Comparison | One snapshot; per-country TFC differences; route/metric dates and source IDs; no missing-as-zero. | Pytest + Vitest + Playwright |
| Scenarios | Shared applicant facts with distinct work/family/study scenario payloads. | Pytest + Vitest |
| Policy boundary | Live first wave rejects explicit feasibility filtering. | Pytest |
| Synthetic boundary | Licensing, selected-locality metric and explicit route filter remain fixture-only. | Pytest |
| Mobile | Combined evidence is complete at 390 x 844 without page overflow. | Playwright + manual browser QA |

## Accessibility checks

- Ranking rows remain keyboard-selectable and comparison controls retain accessible names.
- Details and comparison headings receive focus on entry; close/back returns to the invoking flow.
- Disclosures for route conditions, sources and limitations are keyboard-operable.
- Statuses use text and symbols in addition to color.
- Missing values have an accessible unavailable label rather than a numeric zero.
- Desktop table and mobile cards do not coexist as simultaneously visible duplicate content.

## Language review

Approved statements are listed under
[Cross-feature explanations](terminology-glossary.md#cross-feature-explanations). Prohibited claims
include immigration/admission guarantees, permanent impossibility, absence of jobs, and any claim
that an ecosystem signal establishes applicant access.

## Commands

Run the consolidated clean-revision preflight after committing:

```text
python scripts/verify_ci.py --clean-revision HEAD
```

Also replay the active release and staged TFC candidate, validate generation-4 schemas, regenerate
OpenAPI/TypeScript contracts without drift, and confirm `data/releases/active.json` is unchanged.
