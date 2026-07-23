# Phase 2D.4 homicide source feasibility

Status: discovery complete; no evaluated source path reaches 100 complete countries

Study date: 2026-07-23

The current criterion remains **Intentional homicide rate**, sourced in production from World Bank
WDI `VC.IHR.PSRC.P5` with UNODC lineage. The active release remains `2026-07-21.1` with 20
countries. This study did not change scoring, source precedence, the five-year freshness rule, or
any release.

## Starting point

The all-eligible Phase 2D audit found 91 complete countries and 30 otherwise-complete countries
excluded solely by homicide. At least nine fresh, equivalent observations were therefore required.

The 30 countries were Angola, Benin, Burkina Faso, Bangladesh, Belarus, Bhutan, Central African
Republic, China, Congo, Djibouti, Egypt, Gabon, Georgia, The Gambia, Guinea-Bissau, Iraq,
Kyrgyz Republic, Cambodia, Kuwait, Lao PDR, Libya, Madagascar, Mali, Papua New Guinea, Rwanda,
Saudi Arabia, Solomon Islands, Togo, Thailand, and Viet Nam.

Nine had no WDI homicide record: Congo, Djibouti, Gabon, The Gambia, Lao PDR, Libya, Madagascar,
Mali, and Togo. The other 21 had an observation older than the unchanged 2021 minimum reference
year for a 2026 audit.

## Official retrievals evaluated

| Candidate | Exact official interface | Authority and role |
| --- | --- | --- |
| Direct UNODC | `https://data.unodc.org/sites/dataportal.unodc.org/files/2026-07/data_cts_intentional_homicide.xlsx` and the sibling `metadata_intentional_homicide.pdf` | UNODC is the originating agency and SDG 16.1.1 custodian. |
| UNSD | `GET /SDGAPI/v1/sdg/Indicator/16.1.1/Series/List` and `GET /SDGAPI/v1/sdg/Series/Data` for `VC_IHR_PSRC`, years 2021-2026 | UNSD republishes data supplied under the global SDG process; UNODC remains custodian. |
| Eurostat | Statistics API dataset `crim_hom_soff`, filtered to `ICCS0101`, `PER_VICT`, sex `T`, unit `P_HTHAB`, 2021 onward | Eurostat is an official regional statistical authority using the joint Eurostat-UNODC collection. |
| OECD | SDMX dataflow `OECD.CFE.EDS,DSD_REG_SOC@DF_SAFETY,2.4` | OECD is official, but the identified dataflow is explicitly subnational and regional. |

UNODC exposes an official static workbook from its data-report page, so no rendered HTML was
scraped and no undocumented private endpoint was adopted. The workbook has a retrieval-stable URL
for the July 2026 publication, a file date, country ISO3 identifiers, reference years, dimensions,
unit, values, and source lineage. It has no release identifier beyond the dated file and no explicit
provisional/final flag.

The UNSD JSON interface is documented by its official Swagger schema. Its series catalogue reported
release `2026.Q2.G.01`, which was pinned in the observation request. One request returned all 10,291
series observations needed for historical reconciliation; the fresh-window records end in 2024,
with no 2025 or 2026 observation. Exact response bytes, HTTP metadata, URLs, and SHA-256 checksums
were retained.

## Record selection

Direct UNODC records had to match all of:

- indicator `Victims of intentional homicide`;
- dimension and category `Total`;
- sex and age `Total`;
- rate per 100,000 population;
- ISO3 in the homicide-only set; and
- finite, non-null value with an explicit observation year.

Conflicting duplicate country-year values are rejected rather than resolved using an invented source
priority. The workbook mixes criminal-justice, statistical-office, health, and other source lineages
across its history. That lineage is retained. The four fresh recoveries use police, national
statistical office, or UN crime-survey lineage; older target records include health-source lineage.

UNSD records had to match all of:

- indicator 16.1.1 series `VC_IHR_PSRC`, not the count series `VC_IHR_PSRCN`;
- country geography deterministically mapped from UN M49 to ISO3;
- unit `PER_100000_POP`;
- sex `BOTHSEX`;
- reporting type `G`, meaning the custodian's globally reported series; and
- nature `C` or `CA`.

Modelled and other non-country nature codes, aggregates, sex-specific records, wrong units, and
incompatible series are rejected. The response does not expose age for this sex-only series, nor a
distinct provisional/final or revised flag. Those metadata gaps are retained as limitations rather
than silently interpreted.

Freshness always uses the observation year. A revised old record remains old. No country-specific
exception was used.

## Coverage result

| Scenario | Additional fresh countries | Complete intersection | Reaches 100 |
| --- | ---: | ---: | --- |
| Current WDI baseline | 0 | 91 | No |
| Direct UNODC | 4 | 95 | No |
| UNSD SDG API | 4 | 95 | No |
| Eurostat after primary-source gate | 0 | 95 | No |
| OECD after primary-source gate | 0 | 95 | No |

Both primary channels recovered the same countries:

| Country | Current WDI | Direct UNODC | UNSD |
| --- | ---: | ---: | ---: |
| Bangladesh | 2.3422 (2018) | 1.7630 (2023) | 1.76 (2023) |
| Belarus | 2.3846 (2019) | 1.5348 (2024) | 1.53 (2024) |
| Kuwait | 0.2500 (2020) | 0.7844 (2022) | 0.78 (2022) |
| Saudi Arabia | 0.9353 (2019) | 0.8009 (2024) | 0.80 (2024) |

Direct UNODC and UNSD therefore each add four, not the required nine. Their union also contains only
those four countries.

Because both primary counts were below 100, fallback evaluation was correctly triggered for the
remaining 26 countries only. Eurostat's official ICCS 0101 victim-rate dataset is semantically
suitable, but none of those 26 countries is in its published geographic coverage. OECD's only
homicide-labelled dataflow is for subnational regions and is not a national-total ICCS 0101 series,
so it was rejected before any country value could be considered. No fallback value was used for a
country already recovered by a primary source or for a country failing another criterion.

## Equivalence and discrepancies

The Direct UNODC and UNSD constructs are intentional-homicide victims per 100,000 population and
align with ICCS 0101 / SDG 16.1.1. The metadata includes terrorist-offence deaths and serious assault
leading to death, while excluding attempts, non-intentional homicide, legal intervention,
self-defence, and armed conflict. National legal and recording differences remain a published
comparability caution.

For country-years overlapping current WDI, all 172 Direct UNODC comparisons were exact matches at
retained numeric precision. The 201 UNSD overlaps differed only by published rounding. No minor,
material, different-unit, or unexplained overlapping discrepancy was found. The four coverage gains
necessarily compare newer candidate years with older WDI years; they are classified as different
reference years, not revisions.

Direct UNODC values carry more decimal precision than UNSD display values for the fresh countries.
The values agree at UNSD's published precision. Availability and agreement do not resolve the
missing provisional/final fields or licence blocker.

## Licensing

The Direct UNODC portal and UNSD API link to the general United Nations website terms. Those terms
permit personal, non-commercial downloading and copying but, absent more specific permission,
prohibit redistribution and derivative compilations. No more permissive data-specific licence was
confirmed for the retained homicide payloads. Production redistribution compatibility is therefore
unresolved and would block adoption even if coverage were sufficient.

Eurostat permits commercial and non-commercial reuse of statistical data and metadata with
attribution, subject to identified third-party exceptions. OECD generally permits extraction,
adaptation, distribution, and commercial reuse of OECD-owned data with attribution, subject to
dataset-specific third-party rights. Neither fallback reached the value-selection stage for the
residual set.

The existing WDI representation remains explicitly CC BY 4.0 and was not replaced.

## Reproducibility

The finalized online output is:

`data/reports/homicide-source-feasibility/homicide-source-2026-07-23.4-online/`

The offline replay output is:

`data/reports/homicide-source-feasibility/homicide-source-2026-07-23.4-replay/`

The source comparison, country comparison, discrepancy report, and licensing report were
byte-identical between online processing and replay. Replay made no network calls. Exact third-party
bytes remain content-addressed under ignored `data/raw`; the committed artifact inventories retain
their checksums and retrieval metadata. The active pointer remained:

```json
{
  "release_id": "2026-07-21.1",
  "schema_version": "konsider-release-3.0"
}
```

## Recommendation and decision

This is **Outcome D**:

```text
The current five-year observed-data policy cannot support 100 complete countries using the
evaluated authoritative sources.
```

Do not migrate from WDI, create mixed-source precedence, publish a release, or weaken freshness.
No product decision can make the evaluated equivalent feeds reach 100 without changing policy or
criterion/source scope. If the product owner wants to continue, the next step is an explicit
definition decision about freshness or a materially different homicide construct; neither is
recommended or implemented by Phase 2D.4.

Known limitations are the UN redistribution ambiguity, absent provisional/final flags in both
primary disseminations, no explicit age dimension in the UNSD sex-only series, mutable upstream
revisions, and limited regional scope of the fallback sources.
