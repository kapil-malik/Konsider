# Konsider Phase 7I — OFC, Locality and TFC Integration with End-to-End Scenarios

## Dependency

Proceed only after Phase 7H is accepted.

## Role

Work as the lead cross-feature domain verifier, product-explanation engineer and end-to-end test owner for Konsider.

## Objective

Prove that profile/TFC behavior composes correctly with:

- ordering criteria;
- PCC uncertainty;
- locality-derived criteria and locality compatibility;
- Opportunity Filters;
- country comparison;
- browser scenario state.

Do not activate the final release yet.

## Orthogonality matrix

Create and test a matrix covering:

| Dimension | Must remain independent |
|---|---|
| Affinity | TFCs do not change weights, contributions or scores |
| Coverage | TFCs do not change FCC/PCC missing unions |
| Locality | TFCs do not change locality aggregation |
| Opportunity | TFCs do not change OFC states |
| Profile | Context presence does not imply every TFC is evaluated |
| Feasibility | TFC results may explain or explicitly filter only under approved mode |

## Required combined scenarios

At minimum:

### Career ecosystem + work route

- technology OFC verified;
- work-route TFC matched;
- work-route TFC conditional;
- no supported route matched;
- input required;
- OFC insufficient but TFC route matches.

### Care ecosystem + licensing

- care-sector OFC verified;
- licensing TFC matched/conditional;
- licensing evidence unsupported;
- regional regulator;
- language/qualification input required.

### Education ecosystem + student/post-study route

- education OFC verified;
- student/post-study route match;
- admission inputs intentionally not evaluated;
- intended degree missing;
- source/effective-date warning.

### Locality + household

- active LSCs with common locality;
- no common locality;
- target city supplied;
- housing or cost metric uses the selected locality;
- target city unsupported;
- country result preserved while locality advice differs.

### PCC + TFC

- active PCC excludes countries from R1;
- TFC outcomes remain inspectable where evidence exists;
- no fabricated aggregate score;
- feasibility filtering does not revive countries excluded from complete-case ranking unless product policy explicitly defines a separate view;
- base R0/R1 semantics remain clear.

### Multiple scenarios

- same applicant, solo move;
- same applicant, family move;
- same applicant, study scenario;
- results use different scenario snapshots without mutating the applicant facts.

## Explanation policy

Create consistent explanation ordering:

1. country attractiveness/base rank;
2. coverage uncertainty;
3. locality compatibility;
4. opportunity ecosystem;
5. personal feasibility;
6. assumptions and missing inputs.

Avoid contradictory-looking statements.

Provide approved templates for:

- strong ecosystem but access conditions unmet;
- no broad ecosystem signal but a supported route exists;
- destination attractive but current supported route not matched;
- route matched but locality/housing trade-offs remain;
- evidence unavailable;
- more input required.

## Comparison semantics

Ensure country comparison:

- uses one effective context snapshot;
- exposes per-country TFC differences;
- shows source/effective dates;
- shows base rank;
- shows optional filtered rank;
- does not compare missing metrics as zero;
- preserves OFC and criterion evidence separately.

## Golden end-to-end fixtures

Use fictional profiles.

Cover at least:

- work applicant;
- regulated professional;
- international student;
- family relocation;
- missing input;
- unsupported destination;
- two TFC kinds;
- OFC strict AND;
- PCC active;
- two LSCs;
- explicit feasibility filter;
- mobile UI.

## Regression verification

Run:

- backend unit/integration;
- schema validation;
- release replay;
- OpenAPI generation;
- frontend unit/component;
- browser E2E;
- accessibility;
- clean-checkout;
- Windows/Linux CI where available.

Confirm no change to canonical ranking payloads for requests without profile/TFC context.

## Documentation

Create/update:

- cross-feature behavior guide;
- explanation glossary;
- end-to-end scenario matrix;
- UI test plan;
- Phase 7I verification report.

## Explicit non-goals

Do not:

- activate final release;
- add new TFCs;
- change first-wave policy;
- implement login/persistence/chat;
- change base ranking.

## Commit

Use a focused commit such as:

`test: verify TFC cross-feature integration`

## Stop condition

Stop when all combined scenarios and regression suites pass.

Report:

- invariance results;
- scenario matrix;
- explanation decisions;
- failures and fixes;
- tests/CI;
- files changed;
- commit SHA;
- owner decisions before Phase 7J.
