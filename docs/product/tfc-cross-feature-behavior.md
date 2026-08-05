# TFC cross-feature behavior

Status: Phase 7I verified behavior over the staged first-wave TFC candidate

Date: 2026-08-05

## Product ordering

Konsider explains a destination in this order:

1. affinity score and canonical base rank from ordering criteria;
2. FCC/PCC coverage and whether a complete-case aggregate exists;
3. locality-derived evidence and locality compatibility;
4. selected Opportunity Filter ecosystem signals;
5. personal feasibility under the explicitly selected TFCs; and
6. assumptions, missing inputs, source dates and limitations.

The sequence is explanatory, not a formula. Later dimensions do not rewrite earlier dimensions.
A strong ecosystem can coexist with no supported route match. A supported route can coexist with
an OFC state that does not establish a broad ecosystem. Locality advice can differ while the
country affinity result remains unchanged.

## Orthogonality contract

| Dimension | TFC behavior |
| --- | --- |
| Affinity | Never changes weights, contributions, scores or canonical ordering. |
| Coverage | Never changes FCC/PCC activation, missing unions, exclusions or robustness. |
| Locality | Never changes LSC aggregation, common-locality sets or advisory status. |
| Opportunity | Never changes OFC evidence, strict-AND pass states or filtered ranks. |
| Profile | Supplying context does not select or execute an unselected TFC. |
| Feasibility | Adds typed outcomes; filtering is allowed only for a policy-authorized route TFC and an explicit request. |

The production first-wave catalog authorizes only `ASSESS_ONLY`. `REQUIRE_SUPPORTED_MATCH` remains
covered by synthetic engine fixtures and is rejected by the live API for all three first-wave
checks.

## PCC and ranking views

When a PCC is active, R1 remains the complete-case ranking. A coverage-excluded country receives
no R1 aggregate, base rank or filtered rank and cannot be revived by OFC or TFC processing. Its
available criterion/locality evidence may still be inspected. TFC outcomes are attached to R1
countries for which the staged destination support matrix can be evaluated.

The active Overall job-market opportunity case excludes ATG, GRD and UKR. Phase 7I verifies that
this exact set and every R1 score/contribution remain unchanged when a work-route TFC is assessed.
The current staged TFC source boundary has no positive route evidence for those three excluded
destinations, so no missing feasibility result is disguised as a negative route result.

## Comparison

Comparison uses one request-scoped effective-context snapshot and keeps these rows separate:

- overall affinity with base rank and optional OFC-filtered rank;
- locality assessment;
- one row per selected Opportunity Filter;
- one row per selected TFC; and
- one row per ordering criterion.

Route and metric cells expose effective dates and source IDs. Missing criterion or metric evidence
uses an unavailable marker and is never rendered as zero. Coverage-excluded countries have no
aggregate. Opportunity-excluded countries retain their affinity and base rank but have no filtered
rank. TFC results never substitute for either state.

## Live and synthetic boundaries

Live end-to-end cases use highly qualified work routes, family accompaniment and post-study routes.
Professional licensing and locality-specific housing metrics did not pass the Phase 7B production
gate. Their Phase 7I cases use fictional engine-only fixtures to verify conditional rules,
regional jurisdiction precedence, input sufficiency, selected-locality metrics and explicit
feasibility filtering without adding them to the public catalog.

See the [scenario matrix](phase7i-scenario-matrix.md),
[explanation glossary](terminology-glossary.md#cross-feature-explanations), and
[Phase 7I UI test plan](phase7i-ui-test-plan.md).
