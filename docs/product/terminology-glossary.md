# Konsider terminology glossary

Status: authoritative product and contract terminology

## Ranking and evidence

**Affinity score** — The deterministic 0–10 score produced from selected ordering criteria. An
Opportunity Filter never changes it.

**Ordering criterion** — A weighted input that may contribute to affinity and country ordering.

**FCC (full-coverage criterion)** — An ordering-criterion coverage mode requiring valid evidence
for the full supported universe.

**PCC (partial-coverage criterion)** — An ordering-criterion coverage mode that enters
complete-case ranking at its activation threshold. It is not an Opportunity Filter.

**LSC (locality-specific criterion)** — A criterion whose country result is derived from locality
evidence. LSC describes scope, not coverage or product role.

**Opportunity Filter** — A filter-only destination-side ecosystem signal. Selecting one restricts
the already ranked country set and never contributes to score. `OFC` is internal shorthand.

**All selected required** (`ALL_REQUIRED`) — The only Opportunity Filter combination mode. A
country remains visible only when every selected filter is a verified strong signal. The UI never
auto-relaxes this selection.

**Opportunity-filter excluded** — A country that remains canonically rankable but fails at least
one selected Opportunity Filter. Its affinity score and base rank remain valid; it has no filtered
rank in that response.

**Research-university ecosystem** — The bounded education construct used by the four education
Opportunity Filters. It describes research-intensive university evidence, not teaching quality,
programme availability, admission access, affordability, accreditation or applicant eligibility.

## Opportunity Filter states

**Verified strong signal** (`VERIFIED_STRONG_SIGNAL`) — Complete approved evidence crosses a
frozen strong-ecosystem route. This is the only state that passes a strict Opportunity Filter.

**Strong signal not established** (`STRONG_SIGNAL_NOT_ESTABLISHED`) — Complete approved evidence
was assessed and no strong route passed. It does not mean no jobs, poor education, no universities
or no opportunity.

**Insufficient evidence** (`INSUFFICIENT_EVIDENCE`) — Missing, stale, incomplete, incompatible,
too broad, legally blocked or otherwise unsafe evidence supports neither conclusion. Missing data
is not negative data.

## Orthogonal dimensions

**Product role** — Whether a construct is score-bearing ordering evidence or filter-only
Opportunity evidence.

**Evidence coverage** — Whether the approved source route is complete, partial or unassessed for a
country.

**Geographic scope** — Whether evidence is country-direct, locality-derived or
institution-derived into a country result.

**Applicability** — Whether a result is destination-side, needs applicant context or is diagnostic
only.

**Confidence band** — Public `HIGH`, `MEDIUM` or `LOW` characterization of the evidence route. It
does not replace or determine the public state.

**Base rank** — Canonical rank before Opportunity Filters are applied.

**Filtered rank** — Display rank among countries that pass every selected Opportunity Filter. It
does not replace or mutate base rank.

**Preference preset** — A named set of ordering-criterion weights. It is not an applicant profile
and does not select Opportunity Filters.

## Profile context and feasibility

**Applicant profile** (`ApplicantProfile`) — Relatively stable, explicitly supplied applicant facts
such as citizenship, occupation, experience, qualifications and language evidence. It contains no
authentication fields and is not a preference preset.

**Household profile** (`HouseholdProfile`) — Anonymous partner and dependent composition relevant to
a declared relocation scenario. It contains roles and age bands, not names or document identifiers.

**Exploration scenario** (`ExplorationScenario`) — A specific purpose, destination, target date,
offer/study plan, relocation composition and selected TFC set. Changing a scenario does not mutate
the underlying applicant or household profile.

**Effective profile context** (`EffectiveProfileContext`) — An immutable request-scoped snapshot of
normalized applicant, household and scenario values, taxonomy versions and selected TFCs. Its hash
identifies evaluated facts; it does not require server persistence.

**Typed Feasibility Check** (`TFC`) — A sibling applicant-context assessment that checks an explicit
scenario against immutable destination rules. It is not an ordering criterion, PCC/LSC, Opportunity
Filter, affinity contribution or legal guarantee.

**TFC common status** — Execution state shared by TFCs: evaluated, input required, destination
evidence insufficient, unsupported, not applicable or technical evaluation error. It does not carry
the substantive route result.

**Supported route match** (`SUPPORTED_ROUTE_MATCH`) — A named route matches the supplied facts under
the frozen evidence, without predicting sponsorship, authorization or grant.

**Conditional route match** (`CONDITIONAL_ROUTE_MATCH`) — A named route appears relevant but at least
one route condition remains unknown or unmet.

**No supported route match** (`NO_SUPPORTED_ROUTE_MATCH`) — A guarded result allowed only when the
frozen supported inventory is explicitly complete. It never means permanent legal impossibility and
is not authorized by the current first-wave source policy.

**Destination support record** — The single explicit release record for one TFC-country pair. It
states supported, evidence insufficient, legally blocked, stale, not applicable nationally or
unsupported; absence is never interpreted as a state.

**TFC jurisdiction** — A typed country, region, city, institution or regulator/service-authority
identity used by destination rules. It is separate from route IDs and canonical country codes.

**TFC evaluation policy** — Immutable data controlling effective-date selection, jurisdiction
precedence, conflict and staleness handling, and whether negative route conclusions are permitted.
Substantive policy changes are reviewed as artifact diffs, not hidden parser changes.

**TFC semantic diff** — A review artifact that separately identifies source input, normalized
rule, effective date, evaluation policy and destination support-state changes between candidates.

**Synthetic TFC release candidate** — A draft-only release-6 overlay used to prove schemas,
validation and deterministic replay. It cannot be published or activated and conveys no real-world
destination conclusion.

**Assess only** (`ASSESS_ONLY`) — The default TFC mode. Feasibility outcomes are attached to the
copied ranking assessment without excluding countries or changing rank, score or contribution.

**Require supported match** (`REQUIRE_SUPPORTED_MATCH`) — An explicitly requested post-ranking
projection available only to authorized route/rule TFCs. Survivors retain base order and affinity;
metric thresholds cannot use this mode.

**Scenario result snapshot** — A request-scoped, non-persisted record of release, policy and source
versions, opaque effective-context hash, selected TFCs, evaluation date, base-order identity,
outcomes, assumptions and warnings. It does not contain profile objects or raw profile values.
