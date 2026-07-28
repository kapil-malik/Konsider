# Prompt — Phase 4G: UI and UX for Uncertainty-Aware Ranking

## Intended for
Codex in the local Konsider repository.

## Inputs
- Phase 4E API contract and generated types.
- Phase 4F active release/catalog.
- Existing responsive React UI and `docs/product/ui.md`.

## Objective

Add clear uncertainty-aware ranking UX without reproducing ranking logic in the browser.

## Criteria controls

For every criterion show its status clearly:

- full coverage: `91/91 countries`;
- partial coverage: for example `88/91 countries`;
- experimental where applicable;
- unavailable/non-ready where applicable.

For PCC:

- show a concise indicator such as `Limited coverage`;
- show the activation rule: it affects ranking only at Medium or above;
- when set to No, Very Low, or Low, indicate that it is not active in the ranking;
- provide an accessible details view listing missing-country count and criterion caveat.

Do not use alarming red styling merely because a criterion is PCC.

## Pre-apply coverage preview

When weights change, the UI may use catalog metadata to preview:

- active PCC count;
- potential missing-country union count where the API provides a preview endpoint or deterministic metadata;
- whether the preferred five-country band is exceeded.

Do not reimplement the final ranking or robustness calculation client-side. If no preview API exists, show the definitive result only after Apply.

## Results summary

Always show:

- `X of 91 countries ranked`;
- active PCC names;
- excluded-country count;
- uncertainty status;
- robustness K.

### Mild state — ROBUST_TOP_K

Example meaning:

> Some countries were excluded because of missing data. Even with the best possible missing scores, none could enter your top 10.

### Prominent caution — POTENTIALLY_AFFECTED

Example meaning:

> One or more excluded countries could potentially enter your top 10. Treat the recommendations as incomplete.

### Strongest warning — BASELINE_TOP_K_EXCLUDED

Example meaning:

> A country that appeared in the full-coverage top 10 is excluded because an important selected criterion lacks data.

### Coverage limit

Show the FCC-only baseline and explain that the PCC-inclusive result was not generated because too many countries would be excluded.

## Excluded-country details

Provide an expandable section with:

- country;
- baseline R0 rank;
- missing/stale criteria;
- reason;
- optimistic upper bound;
- whether it could enter top K.

Never display excluded countries at the bottom of the ranked table.

## Ranking table

- Label the rank scope, e.g. `Rank among 88 eligible countries`.
- Keep the existing basic/detailed table behavior.
- Preserve country comparison selection for ranked countries.
- An excluded country may still be opened for available FCC evidence, but it must be labelled `Not ranked for this profile`.
- Do not fabricate an affinity score for excluded countries.

## Baseline view

Add a secondary `View full-coverage baseline` control when PCC is active.

- `R1` remains the primary result.
- The baseline is explanatory, not a competing default.
- Clearly distinguish its criteria and 91-country universe.

## Accessibility and responsiveness

- Use icons plus text, not colour alone.
- Ensure warnings are screen-reader accessible.
- Preserve full mobile functionality.
- Keep long excluded-country lists collapsible.
- Do not reserve excessive vertical space when no PCC is active.

## Testing

Add:

- component tests for every uncertainty status;
- mobile and desktop layout tests;
- API-driven tests proving no client-side ranking;
- empty/one/many excluded-country cases;
- baseline-toggle behavior;
- experimental/unavailable/PCC badges;
- accessible warning semantics.

## Deliverables

- React implementation;
- updated types and API client;
- tests;
- screenshots or documented visual states;
- updated UI documentation.
