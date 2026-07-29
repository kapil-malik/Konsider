# Phase 5G — C66 Extreme heat exposure onboarding disposition

Date: 2026-07-29

Decision: **HELD — not production-onboarded**

Runtime, catalog, API, UI, and active release changed: **no**

The legal and exact-asset gates pass. The construct gate does not. The current
JRC v1.2 documentation gives `CL_UTC_T32_2020` a day-count label and unit, but
describes its urban-centre aggregation as a count of pixels exceeding the
threshold. Those descriptions are not interchangeable. The upstream
Copernicus variable is a count of days above a UTCI threshold, but that does not
authoritatively establish how JRC aggregated the upstream grid into the
published urban-centre field.

Phase 5G therefore stops before parser implementation, scoring, release
publication, or active-pointer mutation. Silently choosing either interpretation
would make the product label and score semantics unverifiable.

## Source and licence freeze

| Item | Frozen value |
| --- | --- |
| Publisher | European Commission, Joint Research Centre (JRC) |
| Distributor | JRC Data Catalogue and JRC open-data file service |
| Dataset | Global Human Settlement Layer Urban Centre Database, R2024A |
| Exact asset | `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip` |
| Exact field | `CL_UTC_T32_2020` |
| Asset URL | `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_UCDB_GLOBE_R2024A/GHS_UCDB_THEME_GLOBE_R2024A/GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A/V1-2/GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip` |
| Access method | Anonymous HTTPS download |
| Dataset/source version | GHS-UCDB R2024A, theme archive V1.2 |
| Archive update | Readme data update: 2026-05-15; server last-modified: 2026-05-19 |
| Reference period | Decade ending 2020 |
| Update frequency | Release-based; no production refresh SLA is frozen |
| Methodology | Upstream ERA5-HEAT/UTCI-derived threshold data, spatially summarized for GHSL urban centres; the exact summary semantics are unresolved |
| Licence | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Licence URL | `https://creativecommons.org/licenses/by/4.0/` |
| Commercial use | Permitted under CC BY 4.0 |
| Redistribution | Permitted under CC BY 4.0, subject to attribution and indication of changes |
| Attribution | Credit the European Commission/JRC GHSL product, cite the specific dataset and release, link the licence, and identify modifications; do not imply endorsement |
| Third-party boundary | The JRC asset uses Copernicus Climate Change Service/ERA5-HEAT inputs. Production would consume and redistribute only the JRC-published derived asset under its stated CC BY 4.0 terms. |
| Raw-byte retention | Downloaded source bytes retained locally under ignored `data/raw/phase5g/`; they are not committed or used by an active release |
| Parser version | Not assigned because the construct gate failed before implementation |

Authoritative references:

- JRC dataset record:
  `https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd`
- GHSL use and citation guidance:
  `https://human-settlement.emergency.copernicus.eu/GHSLhowToCite.php`
- GHS-UCDB R2024A manual:
  `https://human-settlement.emergency.copernicus.eu/documents/GHSL_UCDB_R2024.pdf`
- Copernicus UTCI historical-variable overview:
  `https://cds.climate.copernicus.eu/datasets/derived-utci-historical?tab=overview`

## Construct freeze

The intended product construct is **Extreme heat exposure**: lower-is-better
exposure to days on which the daily maximum Universal Thermal Climate Index
exceeds 32 °C in major urban destinations, using the decade ending 2020.

It is not:

- a broad extreme-weather or climate-risk score;
- a measure of mortality, health-system vulnerability, adaptive capacity, or
  neighbourhood-level heat inequality;
- a forward climate projection;
- a national land-area mean.

The intended locality type is a GHSL urban centre from
`ghsl_ucdb_top5_population_v1`. The previously proposed country aggregation is
the mean of the two lowest-exposure qualifying localities, with one locality
permitted where only one qualifies. Direction is lower-is-better. C66 remains
the runtime identity, with `Extreme-weather risk` retained only as historical
lineage.

This construct is **not frozen for production** because the raw unit and spatial
aggregation semantics remain contradictory in the publisher documentation.
Consequently freshness thresholds, valid/missing/stale/invalid rules, transform,
bands, experimental flag, and final aggregation cannot be frozen honestly yet.

## Coverage

The Phase 5A exploratory probe against the proposed locality universe measured:

| Measure | Result |
| --- | --- |
| Source records in the climate CSV | 11,422 |
| Localities selected by the proposed universe | 388 |
| Localities with a non-negative field value | 388/388 |
| Potential valid countries | 89/91 |
| Countries without a qualifying locality | Antigua and Barbuda (`ATG`), Grenada (`GRD`) |
| Anticipated coverage mode | PCC |

These are retained research measurements, not production outcomes. No
production parser or canonical mapping was run in Phase 5G, so mapped, valid,
stale, invalid, and rejected production counts are not claimed.

Coverage and locality scope remain independent: if eventually admitted, C66
would be both PCC and locality-derived. Its PCC status would arise only from
89/91 valid country results; its LSC status would arise from the urban-centre
evidence and aggregation method.

## Scoring, sensitivity, and product-value gates

Not run because the construct gate failed first:

- score distribution and discrimination;
- top-one/top-two/top-three/population-weighted sensitivity;
- locality-universe composition sensitivity;
- small-country and large-country effects;
- correlation and redundancy;
- contribution and rank movement;
- common-locality behaviour;
- locality-assessment API/UI examples.

These gates remain mandatory after the publisher semantics are resolved. The
earlier top-two proposal is not an approved scoring policy.

## Replay and checksums

No normalized release exists and no release replay was attempted.

Locally retained source checksums:

| File | SHA-256 |
| --- | --- |
| `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip` | `966b96ef701a8b0053467179a1231ddc24830ac2693add7d1388f281795c0bb` |
| `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A.csv` | `34c484b357bfdae6b6569d9e2235db4891b195d69db03eed2ce6e50547f42954` |
| `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A.pdf` | `7edda16eff38c50c0685313386730302b9f98d02a0a5c5bb2f7172e7e57b5883` |
| `GHSL_UCDB_R2024_V1_2.pdf` | `00dbf5ac9a44c59919106cbe01149aea2923e011e9bab0256fd1f9e818546260` |
| `readme_V1_2.txt` | `0ee8fb8e20da515f4b9fd41b28285ffeb596914c699bf7708e7e0a8a4a660a68` |

## Unblock condition

C66 may return to the Phase 5G production path only when an authoritative JRC
artifact or retained publisher clarification states the exact meaning and unit
of `CL_UTC_T32_2020`, including whether and how daily threshold counts are
spatially aggregated across pixels within an urban centre.

After that clarification, Phase 5G must still implement and pass the parser,
mapping, coverage, scoring, sensitivity, replay, API, and UI gates. The current
source and coverage work does not pre-approve activation.

## Limitations

- The decade ending 2020 is not current-weather evidence.
- Urban-centre geometry cannot represent neighbourhood heat variation.
- Antigua and Barbuda and Grenada currently lack qualifying localities.
- The proposed best-destination aggregation answers opportunity to choose a
  lower-exposure major destination, not average resident exposure.
- A resolved C66 would remain extreme-heat-only despite the historical
  `Extreme-weather risk` label.
