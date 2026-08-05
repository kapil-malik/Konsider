# First-wave Typed Feasibility Check evidence

Status: Phase 7F candidate exposed through the Phase 7G stateless API; not active and no UI

## Frozen scope

Phase 7F productionizes exactly three route-only checks:

| TFC | Original criterion | Policy |
|---|---|---|
| `skilled_work_route_feasibility` | C32 | `skilled_work_route_feasibility.v1` |
| `family_accompaniment_reunification` | C36 | `family_accompaniment_reunification.v1` |
| `post_study_work_pathway` | C35 | `post_study_work_pathway.v1` |

Each policy is version `1.0`, `ASSESS_ONLY`, `NOT_FILTERABLE` and
`POSITIVE_CONDITIONAL_ONLY`. Every route requires external-authority confirmation, so a matching
first-wave route is conditional. The release does not authorize a negative route conclusion,
legal eligibility decision, ranking change or Opportunity Filter behavior.

The common supported boundary is 29 of the stable 91 destinations:

`AUS AUT BEL BGR CAN CYP CZE DEU ESP EST FIN FRA GBR GRC HRV HUN ITA LTU LUX LVA MLT NLD POL PRT ROU SVK SVN SWE USA`

The other 62 destinations have an explicit `UNSUPPORTED` record with reason
`DESTINATION_OUTSIDE_APPROVED_SOURCE_BOUNDARY`. Absence is never interpreted as unsupported.

## Highly qualified work route check

**User question:** Which supported highly qualified work route appears to match this declared
snapshot?

**Profile context:** declared occupation, qualifications, explicit job-offer state, destination
and target date. Citizenship is optional explanatory context. The check does not infer occupation
recognition, sponsorship, salary compliance, quotas or authority approval.

**Routes:**

- European Commission EU Immigration Portal: one country-specific EU Blue Card page and route ID
  for each of the 25 supported EU destinations.
- Australia: Skills in Demand visa, subclass 482.
- Canada: Express Entry skilled-worker programs.
- United Kingdom: Appendix Skilled Worker.
- United States: H-1B specialty occupations.

There are 29 route rules. A rule can return a conditional named-route result; it cannot establish
visa eligibility or grant likelihood.

## Dependants on supported work and study routes

**User question:** Do declared partner or dependent-child roles conditionally fit a supported
primary work or study route?

**Profile context:** partner relationship category, dependent-child presence, a declared primary
route from this frozen first-wave inventory, destination and target date. It does not evaluate
general family reunification, dependency evidence, custody, maintenance, accommodation or partner
work rights.

**Routes:**

- European Commission EU Immigration Portal: one country-specific family-member page for each of
  the 25 supported EU destinations.
- Australia: family unit attached to Skills in Demand subclass 482.
- Canada: open work permits for eligible family members of foreign workers.
- United Kingdom: Skilled Worker dependant partner or child.
- United States: H-4 dependant status.

Each destination has a partner rule and a dependent-child rule, for 58 rules in total. Both are
restricted to the same-country skilled-work or post-study primary route onboarded in this release.

## Post-study stay and work route check

**User question:** Does this declared study scenario conditionally fit a supported post-study stay
or work route?

**Profile context:** institution reference, qualification level, field, duration, study mode,
completion date/state, destination and target date. Citizenship is optional explanatory context.
Institution or program eligibility is never inferred.

**Routes:**

- European Commission EU Immigration Portal: one country-specific student page and frozen
  post-study or student-to-work route identity for each of the 25 supported EU destinations.
- Australia: Temporary Graduate visa, subclass 485.
- Canada: Post-Graduation Work Permit.
- United Kingdom: Appendix Graduate.
- United States: F-1 post-completion Optional Practical Training.

There are 29 rules. Two source-specific boundaries are explicit:

- Cyprus is limited to the official page's mobile-student master's/doctoral pathway.
- Sweden is the narrower in-country student-to-worker status-change route after the official
  study-progress floor and before the study permit expires. Those facts remain external authority
  checks because the Phase 7 profile contract does not collect ECTS totals or permit-validity
  attestations.

## Sources and legal handling

The frozen inventory contains 87 exact page bindings grouped into five approved source families:

| Source ID | Authority | Frozen pages |
|---|---|---:|
| `eu_immigration_portal` | European Commission and contributing national authorities | 75 |
| `au_home_affairs_routes` | Australian Department of Home Affairs | 3 |
| `ca_ircc_routes` | Immigration, Refugees and Citizenship Canada | 3 |
| `uk_home_office_routes` | UK Home Office | 3 |
| `us_uscis_routes` | U.S. Citizenship and Immigration Services | 3 |

Every page binding retains its URL, route identity, verification result, byte count and SHA-256.
Raw source bodies are not checked in. The legal manifest records licence/terms, attribution,
normalized-derivative conclusion, quarterly-or-release refresh, checksum change detection and
manual review. Three Canada pages use checksums of browser-rendered official DOM because direct
worker capture was not reliable; the other 84 use direct HTTP checksums.

## Effective and refresh policy

The candidate was verified on `2026-08-05`; its rules become stale after `2026-11-05`. Future,
expired, stale, conflicting or unavailable rules block evaluation. Refresh requires recapture,
checksum and semantic-diff review, research reconciliation, candidate rebuild and deterministic
replay. No runtime source calls occur.

## Synthetic examples

- A declared qualified-work scenario with occupation, qualifications and an offer in Germany can
  identify `EU.BLUE_CARD.DEU` as conditional, pending official confirmation.
- A spouse and dependent child attached to that declared primary route can identify the two German
  family-member checks as conditional.
- A completed study scenario in Canada can identify `CA.PGWP` as conditional; the result does not
  establish institution, program or application eligibility.
- Albania remains explicit as unsupported for all three checks in this source boundary. That says
  nothing about whether routes exist outside the frozen inventory.

## Replay

```powershell
python scripts\build_phase7f_tfc_candidate.py replay `
  --production-capture data\reports\phase7f-2026-08-05\production-capture.json `
  --release data\reports\phase7f-2026-08-05\staged-release\phase7f-first-wave-2026-08-05.6.0
```

Replay must report `PASSED` with no mismatched files. The candidate is a draft overlay on active
release `2026-08-04.1`; `activation_authorized` remains false.
