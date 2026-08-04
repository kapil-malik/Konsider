# Phase 7B TFC exact-source feasibility and owner gate

Status: research complete; owner approval required before Phase 7C  
Research cutoff: 2026-08-05  
Stable universe: `stable_supported_v1` (91 countries)  
Production-qualified count: 3  
Minimum-three gate: **PASS**

## Decision

Phase 7B qualifies exactly three first-wave Typed Feasibility Checks:

1. **Highly qualified work route check**
2. **Dependants on supported work and study routes**
3. **Post-study stay and work route check**

Each is a bounded `RULE_ROUTE_MATCH` check over the same 29-destination source boundary: the 25
countries covered by the EU Immigration Portal legal-migration directives, plus Australia, Canada,
the United Kingdom and the United States. This supports six of the eight frozen anchors and exceeds
each route candidate's predeclared stable-destination floor. The other 62 stable countries remain
visible as `DESTINATION_UNSUPPORTED`; that state is never an applicant-negative conclusion.

All three qualified checks use one result family. Phase 7C therefore must define a route/rule-match
contract only. It must not present itself as a generic multi-type TFC engine, and it must not add a
scenario-metric result family speculatively.

The initial route evidence is sufficient for positive and conditional supported-route matches. It
is not sufficient for a complete negative route conclusion. `NO_SUPPORTED_ROUTE_MATCHED` must not
be exposed until the completeness of a frozen route inventory is independently proven.

## Frozen product boundary

The first wave answers a narrow question: which named, supported route appears to match or
conditionally match the applicant's declared snapshot, and which required facts are missing?

It does not:

- predict invitations, sponsorship, admission, authorization, application approval or visa grant;
- claim that no route exists outside the supported inventory;
- infer missing occupation, qualification, salary, household or study facts;
- turn route results into country affinity or an opaque country score;
- browse sources at runtime;
- store real applicant data in research artifacts; or
- cover general family reunification, permanent residence, licensing or cost advice.

The family check is intentionally narrower than the Phase 7A working name. It covers partner and
dependent-child conditions attached to the frozen supported work and study routes. It is not a
general family-reunification checker.

## Qualification table

| TFC | Criterion | Kind | Support | Gate result | Disposition |
|---|---|---|---:|---|---|
| Highly qualified work route check | C32 | Rule/route | 29/91; 6/8 anchors | all nine gates pass | `PRODUCTION_QUALIFIED_FIRST_WAVE` |
| Dependants on supported work and study routes | C36 | Rule/route | 29/91; 6/8 anchors | all nine gates pass for the frozen primary-route family | `PRODUCTION_QUALIFIED_FIRST_WAVE` |
| Post-study stay and work route check | C35 | Rule/route | 29/91; 6/8 anchors | all nine gates pass | `PRODUCTION_QUALIFIED_FIRST_WAVE` |
| Permanent-residence pathway | C33 | Rule/route | 29/91 partial; 6/8 anchors | construct, source, coverage, replay and maintenance fail | `NEEDS_TARGETED_FOLLOW_UP` |
| Professional licensing requirements | C38 | Rule/route | 31/91 partial; 3/8 anchors | construct, source, coverage, replay and maintenance fail | `NEEDS_TARGETED_FOLLOW_UP` |
| Employment deductions estimate | C21+C22 | Scenario metric | 38/91 partial; 6/8 anchors | construct, source, coverage, replay and maintenance fail | `NEEDS_TARGETED_FOLLOW_UP` |
| Reference-city rent affordability scenario | C25 | Scenario metric | 37/91; 3/8 anchors | frozen coverage gate fails | `NEEDS_TARGETED_FOLLOW_UP` |
| Healthcare affordability scenario | C26 | Scenario metric | 30/91 partial; 2/8 anchors | construct, source, coverage, replay and maintenance fail | `NEEDS_TARGETED_FOLLOW_UP` |

No floor was lowered after measuring source coverage. In particular, the rent candidate has a good
official source and more than 12 stable destinations, but only three of eight anchors. The Phase 7A
floor required six anchors as well as 20 canonical cities across 12 destinations, so the candidate
does not qualify.

## First-wave sources

### European Union subset

The [EU Immigration Portal](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/eu-immigration-portal_en)
provides practical country/category information for stays longer than 90 days. The shared
legal-migration rules apply to 25 EU countries; Denmark and Ireland are outside this source bundle.
Country pages identify national competent authorities and national conditions. The exact Phase 7F
capture must preserve each country/category page, effective date, capture time and checksum.

The bundle is limited to:

`AUT BEL BGR HRV CYP CZE EST FIN FRA DEU GRC HUN ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE`

The Commission's [legal notice](https://commission.europa.eu/legal-notice_en) permits reuse of
Commission-owned content under CC BY 4.0 unless otherwise indicated. Production derivatives must
credit the European Union, link the licence, indicate changes and exclude third-party content and
official emblems. Portal guidance is not authentic legal text. National rules and authentic legal
acts outrank the practical summary when they conflict.

### Australia

The Department of Home Affairs publishes the
[Skills in Demand visa (subclass 482)](https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skills-in-demand-visa-subclass-482)
and [Temporary Graduate visa (subclass 485)](https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-graduate-485)
route pages. The 482 material covers sponsor, nominated-position and skill conditions and bounded
secondary-applicant roles. The 485 material covers post-study stay/work conditions.

The department's [copyright notice](https://www.homeaffairs.gov.au/access-and-accountability/using-our-website/copyright-and-disclaimer)
places department-produced website material under CC BY 3.0 Australia, excluding the coat of arms,
logo, specifically excluded and third-party material. Attribution must name the Australian
Government Department of Home Affairs. The site itself warns that it is a basic guide and that
legislation is authoritative.

### Canada

IRCC's [Express Entry](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html),
[study/work](https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work.html)
and [open work permit](https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada/open-work-permit.html)
pages provide the official route families for the bounded checks. Program match must remain
separate from profile acceptance, invitation, permit issuance and final decision.

The [Open Government Licence - Canada](https://open.canada.ca/en/open-government-licence-canada)
allows worldwide commercial and non-commercial reuse with prescribed attribution. Personal
information, official symbols, third-party rights and implied endorsement are excluded.

### United Kingdom

The Home Office publishes the current
[Skilled Worker rules](https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-skilled-worker),
[Graduate rules](https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-graduate)
and [Graduate dependant guidance](https://www.gov.uk/graduate-visa/your-partner-and-children).
The rule pages expose update history; the researched rules were updated on 2026-07-01. Every release
must pin the effective rule version rather than treat the current page as retroactive.

The [GOV.UK terms](https://www.gov.uk/help/terms-conditions) state that most Crown-copyright GOV.UK
content is published under the Open Government Licence. Production use must follow OGL attribution,
exclude credited third-party material and avoid implied official status.

### United States

USCIS publishes the H-1B specialty-occupation route and official guidance for H-4 dependants and
F-1 practical training. The normalized source bundle uses the H-1B route identity, the USCIS
[practical-training chapter](https://www.uscis.gov/node/92821) and the official H-dependant rule
material. OPT remains authorization-based; H-1B remains petition/cap-dependent; H-4 work rights are
not universal.

Under [17 USC 105](https://www.copyright.gov/title17/92chap1.html), works prepared by U.S. federal
employees as part of official duties are generally not protected by U.S. copyright. Exact page
provenance is still required, and transferred/third-party works, seals, logos and marks are
excluded.

## Follow-up source findings

### Permanent residence

The Commission's [long-term resident summary](https://home-affairs.ec.europa.eu/policies/migration-and-asylum/legal-migration-and-resettlement/long-term-residents_en)
supports a bounded EU concept, including a general five-year residence condition. It does not form
a complete national settlement-route inventory or normalize continuous/physical residence,
qualifying status, absence, discretion and transition rules. Comparable completeness is also not
yet captured for the four national route bundles.

### Professional licensing

The official [EU Regulated Professions Database](https://ec.europa.eu/growth/tools-databases/regprof/)
covers EU/EEA countries, Switzerland and the United Kingdom and identifies professions, contact
points and authorities. Each country is responsible for updates, and no stable versioned bulk
export was established. It does not by itself provide a replayable rule set for qualification
recognition, exams, supervised practice, language and regional regulator variation. A follow-up
must select precise profession families and regulators before measuring coverage.

### Employment deductions

[OECD Taxing Wages 2026](https://www.oecd.org/en/publications/2026/04/taxing-wages-2026_d1f39986/full-report/overview_d93131c3.html)
covers 38 stable OECD countries for tax year 2025, but its standardized household types and earnings
levels are benchmarks rather than arbitrary applicant tax calculations. The OECD TaxBEN calculator
models richer hypothetical families, but its underlying STATA command is application-controlled and
was not established as an openly replayable production dependency. A first version still needs
national tax and contribution parameters, subnational policy and a frozen household model.

### Housing

Eurostat dataset `prc_colc_rents` is the strongest metric candidate. The
[dissemination API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_colc_rents?lang=en&sinceTimePeriod=2024)
returned annual 2024-2025 values across five standardized dwelling types, two currencies and 44
reference-city geographies; 37 stable countries were represented. The metadata defines current
market rents in selected neighbourhoods collected for international-remuneration comparisons.
This is not a representative national rent series.

Eurostat permits reuse of statistical data and metadata under its
[copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice), subject to attribution,
change indication and third-party exceptions. Its dissemination API exposes the latest version and
updates twice daily rather than providing historical versioning. Production replay would therefore
require lawful raw-response capture and checksums for every evidence version.

### Healthcare

[MISSOC](https://employment-social-affairs.ec.europa.eu/policies-and-activities/moving-working-europe/eu-social-security-coordination/specialised-information/social-protection-systems-missoc_en)
provides ministry-contributed, twice-yearly comparative social-protection information across 30
stable EU/EEA/Swiss destinations. It can support system and eligibility research, but it does not
provide a comparable applicant-specific formula for mandatory premiums, salary-linked levies,
waiting periods and household bands. National sources remain necessary.

## Support matrix and explicit states

The deterministic matrix contains exactly 728 unique rows: eight candidates times all 91 stable
countries. The measured states are:

| Candidate | Assessable | Partially assessable | Unsupported |
|---|---:|---:|---:|
| Highly qualified work route | 29 | 0 | 62 |
| Dependants on supported routes | 29 | 0 | 62 |
| Post-study stay/work route | 29 | 0 | 62 |
| Permanent residence | 0 | 29 | 62 |
| Professional licensing | 0 | 31 | 60 |
| Employment deductions | 0 | 38 | 53 |
| Reference-city rent | 37 | 0 | 54 |
| Healthcare affordability | 0 | 30 | 61 |

No destination is silently omitted. No `DESTINATION_UNSUPPORTED`, source gap, stale value or
conflict is translated into applicant failure.

## Profile and result boundaries

The minimum fields remain route-specific. Common facts include citizenships, target destination,
snapshot date, occupation, qualification, job-offer state and route-dependent salary/language
facts. The dependant check additionally needs the declared primary route and bounded household
roles. The post-study check needs institution identity, qualification, study mode/duration and
completion state.

Missing fields produce `INPUT_REQUIRED`. Phase 7C should reuse facts across checks without building
a 91-country profile matrix. Sensitive household fields must be limited to those needed by a named
route; research and tests use synthetic profiles only.

The initial public states should be designed around:

- `INPUT_REQUIRED`;
- a positive supported-route match;
- a conditional supported-route match;
- destination unsupported;
- insufficient/conflicting evidence; and
- not applicable to the declared scenario.

Names and exact enums remain a Phase 7C contract decision. A complete negative no-match state is
outside the approved first-wave evidence boundary.

## Effective dates, conflicts and maintenance

Every future normalized rule must retain source identity, capture timestamp, checksum,
`effective_from` and `effective_to` where known. Evaluation must select the rule whose effective
interval contains the declared snapshot date. Current pages cannot be applied retroactively.

Authentic legislation or formally published immigration rules outrank practical guidance. National
rules outrank supranational summaries for national conditions. Unresolved evidence of equal rank
must return `CONFLICTING_UNRESOLVED`, block the conclusion and enter owner review.

The first wave is feasible only with release-based, offline evidence:

- capture source changes outside request time;
- diff normalized route facts and page identities;
- require policy/source review before activation;
- keep prior evidence versions immutable;
- expose the evidence effective date; and
- never make live browsing part of assessment.

The 29-destination boundary is a source-feasibility qualification, not completed production
onboarding. Phase 7F still has to build, review and verify every frozen route record before any
destination becomes publicly assessable.

## Deterministic replay

Run from the repository root:

```powershell
node project-history/phases/phase-7/research/run_phase7b_tfc_probe.mjs
```

The script uses only committed inputs: the stable country universe, Phase 7A deep-probe protocol and
the normalized lawful-source fixture. It performs no network access. It regenerates all 728 support
records, validates uniqueness and source references, verifies all nine gates for first-wave
candidates, asserts the minimum-three gate and writes SHA-256 identities to the replay manifest.

The machine-readable package is under `data/reports/phase7b-2026-08-05/`. It includes candidate,
source, legal, country-support, profile-field, route-rule, metric-formula, effective-date/conflict,
synthetic-scenario and owner-decision artifacts. It contains no real applicant data.

## Owner approval required

Phase 7B recommends that the owner approve:

1. the exact three-item first wave;
2. the three user-facing names shown in this report;
3. guest-entered route-specific profile boundaries and the 29-destination source boundary;
4. a route/rule-match-only Phase 7C contract;
5. positive/conditional results without a complete negative no-route result;
6. whether route matches may be used as an explicit post-ranking filter; and
7. browser-tab memory as the default, plus whether later opt-in same-device/session retention may be designed.

No production contracts, runtime worker, API field, UI or release activation is implemented in
Phase 7B. Stop here for owner approval; do not begin Phase 7C automatically.
