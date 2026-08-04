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
