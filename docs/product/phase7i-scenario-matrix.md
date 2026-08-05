# Phase 7I end-to-end scenario matrix

Status: implemented with fictional profiles

Date: 2026-08-05

`LIVE` means the staged three-check API candidate is exercised. `SYNTHETIC` means the generic
engine is exercised without adding a public TFC. The machine-readable inventory is
`tests/fixtures/phase7i/golden-scenarios.json`.

| Scenario family | Cases | Surface | Required result |
| --- | --- | --- | --- |
| Career + work route | supported, conditional, no match, input required | Live | OFC and route state remain separate; score/order unchanged. |
| Career mismatch | skilled-trades ecosystem not established while a work route matches | Live | Country may be OFC-excluded while route evidence and base rank remain inspectable. |
| Care + licensing | supported, conditional, unsupported, regional regulator, language/qualification missing | Synthetic | Generic route engine returns typed results; no licensing TFC enters the live catalog. |
| Education + post-study | route result, intended degree missing, source/effective-date warning | Live | Admission is not evaluated; missing study facts request input. |
| Locality + household | common locality, no common locality, selected-city metric, unsupported city | Live ranking plus synthetic metric | Country result is preserved while locality advice or metric support differs. |
| PCC + TFC | active PCC, three excluded countries, supported survivor | Live | No partial aggregate; excluded countries are not revived; survivor TFC remains inspectable. |
| Strict OFC AND | career filters combined with TFC | Live | OFC evidence and exclusion reasons are unchanged by TFC evaluation. |
| Explicit feasibility filter | tied supported/non-supported routes | Synthetic | Explicit policy-gated filtering preserves base values, ties and survivor order. |
| Multiple scenarios | same applicant with solo work, family and study scenarios | Live API and browser state | Applicant facts remain shared; each scenario creates a distinct snapshot and TFC selection. |
| Mobile UI | OFC + locality + TFC ranking/details/comparison | Browser | Complete visible evidence, keyboard operation and no horizontal overflow at 390 x 844. |

## Fictional profiles

- **Work applicant:** fictional systems analyst/civil engineer with declared qualification and
  explicit offer state.
- **Regulated professional:** fictional nurse with declared qualification and language evidence;
  synthetic only.
- **International student:** fictional planned master's study; admission likelihood is never
  assessed.
- **Family relocation:** fictional spouse and dependent child attached to a named supported route.

## Expected independent combinations

| Opportunity signal | Personal feasibility | Interpretation |
| --- | --- | --- |
| Verified strong signal | Supported or conditional route | Both destination ecosystem and current route evidence are positive, within their separate bounds. |
| Verified strong signal | No supported route match | Broad ecosystem evidence does not establish access for this scenario. |
| Not established/insufficient | Supported route | A named route can exist without the selected broad ecosystem signal. |
| Any OFC state | Input required | Destination evidence remains valid; more scenario facts are needed for feasibility. |
| Any OFC state | Unsupported/evidence unavailable | No negative applicant conclusion is inferred. |

The matrix does not activate release 6, change the first-wave policy or authorize feasibility
filtering in the UI.
