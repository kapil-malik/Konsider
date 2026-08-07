# Pending Release Snapshot and API Change Buffer

This document parks backend and release-generation changes that should be implemented and published together. The purpose is to avoid producing multiple intermediate release snapshots while related issues are still being collected.

## Working rules

- Add newly discovered release or API changes to this document before implementation.
- Keep each item marked as `Pending`, `In progress`, `Verified`, or `Deferred`.
- Do not publish a new snapshot until all items selected for the batch are implemented and verified together.
- UI-only changes do not belong here unless they depend on a new backend contract or snapshot field.
- Before publishing, confirm that every API v3 operation uses the same release ID.

## 1. Restore country regions in API v3 responses

**Status:** Verified
**Affected feature:** Home screen country-ranking Region dropdown
**Observed against:** API contract `konsider-api-3.0`, release `2026-08-07.3`

### User-visible symptom

The Region dropdown contains only `All regions`. No actual region options are available. Country rows also fall back to displaying their country code where the UI expects a region.

The web layer is functioning as designed. It builds the dropdown from the distinct, non-empty values in:

```text
ranking.rankings[*].country.region
```

The running API currently returns `region: null` for every country, leaving the UI with no values from which to construct the options.

### Source data already available

The stable country universe contains the required region metadata for the supported countries:

```text
data/country-universes/stable-supported-v1.json
```

Examples include `Europe & Central Asia`, `East Asia & Pacific`, `South Asia`, and `North America`. This is therefore not a research or source-acquisition gap; the metadata is being dropped during release construction and API response assembly.

### Root causes

#### A. Release snapshot generation omits the region

`_country_entities()` in:

```text
src/konsider/ingestion/phase5_locality_onboarding.py
```

constructs country geographic entities from the stable-universe rows but does not copy `row["region"]`. Consequently, the published artifact:

```text
data/releases/2026-08-07.3/geographic-entities.jsonl
```

contains country IDs, display names, codes, aliases, and source mappings, but no region field.

The active consumer catalog snapshot for `2026-08-07.3` also contains no usable country-region metadata.

#### B. The release-backed API service hard-codes a null region

`RecommendationService` in:

```text
src/konsider/api/v2_service.py
```

currently emits:

```python
"region": None
```

when assembling geographic entities for the catalog and ranking-related responses. API v3 routes use `RecommendationServiceV3`, but that class is an adapter over this release-backed service. Therefore, the hard-coded null propagates through `/api/v3/*` responses as well.

### Required backend changes

1. Update country geographic-entity generation to preserve the stable-universe region:

   ```python
   "region": row["region"]
   ```

2. Review the geographic-entity artifact schema and validation rules. Add or permit `region` as appropriate, with the intended rule for entity types:

   - Country entities should carry a non-empty region.
   - Locality entities may inherit the parent country's region if useful across API responses, or remain nullable if the contract intentionally limits regions to countries.
   - Validation should fail publication if a supported country lacks a region.

3. Replace hard-coded `"region": None` values in the release-backed API response assembly with the value from the geographic entity, for example:

   ```python
   "region": entity.get("region")
   ```

4. Audit every place that emits `GeographicEntityResponse`, particularly:

   - `GET /api/v3/catalog`
   - `POST /api/v3/rankings`
   - `POST /api/v3/comparisons`
   - `POST /api/v3/countries/{country_code}/details`
   - coverage-excluded country records
   - locality evidence records, if locality regions are included by policy

5. Add regression coverage at both levels:

   - Release validation: every supported country has the expected non-empty region.
   - API contract tests: catalog, ranking, comparison, and country-detail country objects preserve the same region.

### Snapshot publication work

When this item is included in the eventual release batch:

1. Regenerate the release artifacts rather than manually editing JSON/JSONL files.
2. Confirm `geographic-entities.jsonl` includes region metadata for all supported country entities.
3. Run the complete release validation suite, including manifest/checksum generation.
4. Publish one new release ID containing this fix and the other items accumulated in this buffer.
5. Point the active-release mechanism at the new release and restart the API.
6. Do not mutate or republish `2026-08-07.3` in place.

### Verification checklist

- [x] All supported countries in the generated geographic-entity artifact have a non-empty region.
- [x] `/api/v3/catalog` returns populated `countries[*].region` values.
- [x] `/api/v3/rankings` returns populated `rankings[*].country.region` values.
- [x] Comparison and country-detail responses return the same region for the same country.
- [x] Catalog, opportunity-filter catalog, TFC catalog, ranking, comparison, and country-detail responses report the same new release ID.
- [x] The Region dropdown contains all distinct regions represented in the current ranked result.
- [x] Selecting a region filters the visible rankings correctly.
- [x] `All regions` restores the unfiltered ranked result.
- [x] Country rows/cards display the region rather than falling back to the country code.
- [x] Existing ranking order and affinity scores are unchanged by adding region metadata.

### Acceptance criteria

The item is complete when a newly published release preserves region metadata end-to-end and every API v3 country representation exposes it consistently. The UI must then populate the Region dropdown without any additional mapping or hard-coded region list.

## 2. Return the complete eligible ranking through a compact API v3 response

**Status:** Verified
**Affected feature:** Home screen country-ranking table, search, Region filtering, and comparison selection
**Observed against:** API contract `konsider-api-3.0`, release `2026-08-07.3`

### Desired behavior

The ranking view should receive every country that has a valid final aggregate, rather than only the first ten. The UI should provide the browsing experience through its existing search and Region controls plus a bounded, scrollable desktop table.

The implementation release contains 91 supported countries, of which 83 are presently ranking-eligible and eight are coverage-excluded. “Return all ranked countries” therefore means returning all 83 eligible countries. Coverage-excluded countries remain in the separate exclusions section unless a later product decision explicitly changes the semantics of the ranking table.

Server-side pagination is not required for a result set of this size. Client-side search, Region filtering, selection, and comparison are preferable because they remain immediate and operate across the complete result set.

### Current behavior and constraints

The v3 ranking route currently accepts the request model named `V2RankingRequest`. Its `top_k` field defaults to 10 in:

```text
src/konsider/api/models/v2.py
```

The UI omits `top_k`, so the API default limits every ranking response to ten countries.

The existing API can return all 88 eligible countries when explicitly given `top_k: 88`, but hard-coding either 88 or 91 in the UI would be brittle:

- The eligible-country count can change between releases or with coverage policy.
- A request for `top_k: 91` currently fails because only 88 countries are eligible.
- Opportunity filters may reduce the surviving result set further.

The existing rich response is also too heavy to use indiscriminately as an all-country response. Measurements against the current local v3 API were:

| Requested result | Returned countries | Uncompressed response size |
| --- | ---: | ---: |
| `top_k: 10` | 10 | approximately 0.34 MB |
| `top_k: 88` | 88 | approximately 2.35 MB |

The size is driven by repeated contribution evidence, observations, sources, lineage metadata, locality evidence, and assessments—not by the number of table rows alone. Ranking requests are repeated when priorities, opportunity filters, or declared-scenario inputs change, so the full rich response would create unnecessary transfer and parsing cost.

### API v3 contract changes

1. Introduce a v3-specific ranking request model rather than continuing to expose the older-named request model as the public v3 contract.

2. Give the v3 request an explicit all-results representation. Recommended semantics:

   ```python
   top_k: int | None = None
   ```

   - Omitted or `null`: return all ranking-eligible countries.
   - Positive integer: return the requested top subset using the existing ranking and tie policy.
   - The UI must not need to know the release's eligible-country count in advance.

3. Preserve the existing meaning of exclusions:

   - Coverage-excluded countries are not inserted into the ranked sequence because they lack a final aggregate.
   - Opportunity-filter-excluded countries remain outside the filtered ranked sequence.
   - Both sets remain available through the existing assessment/exclusion structures.

4. Review `top_k` validation and tie-inclusive truncation in the release-backed ranking service so that:

   - `None` reliably means no truncation.
   - Explicit positive limits continue to work.
   - Limits are validated against the appropriate canonical eligible universe.
   - Opportunity filtering does not incorrectly reject a valid limit merely because fewer countries survive the filters.

5. Regenerate the API v3 OpenAPI contract and frontend generated types after introducing the v3 request and compact response models.

### Compact ranking response

Do not return the current full evidence graph for all countries in the main ranking request. Define a compact v3 ranking-row representation containing only what the ranking workspace needs:

- `rank` and `base_rank`
- Country entity ID, country code, display name, and region
- Final affinity score
- Compact locality assessment/status
- Compact opportunity-filter match summary
- Compact feasibility-check summary
- Lightweight per-criterion score/contribution values required by the optional detailed-evidence table columns

Avoid repeating the following in every ranking row unless a demonstrated UI requirement remains:

- Full observations
- Source metadata and source lineages
- Long limitations and caveats
- Complete locality evidence records
- Full feasibility route or metric evidence

Detailed evidence should continue to come from the country-details endpoint when a user opens a country. Comparison-specific evidence should continue to come from the comparison endpoint.

If introducing a separate compact response type is impractical, an explicit response projection such as `include_evidence: false` may be considered, but the preferred design is a stable compact ranking contract with clear responsibilities.

### UI changes

1. Request the complete eligible ranking using the new v3 all-results semantics. Do not hard-code the current eligible count.

2. Continue using client-side filtering for:

   - Country name or code search
   - Region selection
   - Comparison selection state

3. Restore a bounded scroll experience for the desktop table:

   - Use a maximum height based on the viewport, approximately `60–70vh` with a sensible pixel cap.
   - Apply vertical overflow to the table container.
   - Retain the sticky table header.
   - Keep search, Region, evidence, and comparison controls outside the scrolling container.

4. Retain normal page scrolling for the mobile card presentation unless mobile testing demonstrates that a nested card scroller is materially better.

5. Update result-count messaging to distinguish the complete ranked set from the currently visible client-side subset, for example:

   ```text
   Showing 12 of 88 ranked countries
   ```

6. Ensure selection and comparison actions remain usable while scrolling. Consider a sticky selection action only if testing shows that the toolbar becomes difficult to reach after selecting countries farther down the list.

### Regression and performance coverage

- [x] Omitted or `null` `top_k` returns all eligible countries through API v3.
- [x] Explicit positive `top_k` values continue to return the intended subset.
- [x] Coverage-excluded countries remain outside the ranked list and in coverage diagnostics.
- [x] Opportunity filters return every surviving eligible country when no explicit limit is supplied.
- [x] Ranking order, base ranks, final scores, and tie behavior are unchanged.
- [x] The compact ranking response contains every field required by the desktop table and mobile cards.
- [x] Full evidence remains available from country details and comparisons.
- [x] The all-country response is 766,532 bytes, substantially below the prior approximately 2.35 MB rich response.
- [x] Search and Region filtering operate across the complete returned ranking.
- [x] The desktop table scrolls within its bounded container and retains a sticky header.
- [x] Keyboard navigation, row selection, clear selection, and comparison work for countries beyond the first ten.
- [x] Mobile continues to use accessible country cards without an awkward nested scroll region.

### Release and deployment coordination

This item is primarily API-engine, API-contract, and UI work; it does not independently require a new data snapshot. However, it should be deployed in the same coordinated batch as Item 1 because Region filtering across the full ranking depends on populated region metadata.

Recommended sequence for the combined batch:

1. Implement and test the compact all-results v3 contract.
2. Implement and test region preservation in release generation and API responses.
3. Generate one new release snapshot containing the region metadata fix and any other accumulated snapshot changes.
4. Regenerate API and frontend contracts.
5. Deploy the API and UI together against the new release.
6. Verify that all v3 endpoints report the same new release ID before making the deployment active.

### Acceptance criteria

The item is complete when the ranking workspace receives every currently eligible country without pagination, the API response stays within the agreed performance budget, and the desktop table provides smooth client-side search, Region filtering, selection, and scrolling. No UI code should contain a hard-coded country-count limit.

## 3. Present the Balanced preset as Medium while preserving equal weighting

**Status:** Verified
**Affected feature:** Balanced preference preset and the importance controls on the home screen
**Observed against:** API contract `konsider-api-3.0`, release `2026-08-07.3`

### Desired behavior

When the user selects the `Balanced` preset, every enabled criterion should display `Medium` rather than `Very High`. The preset must remain genuinely balanced: every enabled criterion must have the same relative influence on the affinity score.

This is intended as a correction to the user-facing importance scale, not a change to ranking policy. Country scores, ranking order, active criteria, locality-analysis behavior, opportunity filtering, and feasibility behavior should remain unchanged.

### Why the UI currently shows Very High

The active release defines the `equal_weight_mvp` preset, displayed as `Balanced`, with a raw weight of `1.0` for all 13 enabled criteria:

```text
data/releases/2026-08-07.3/consumer-catalog.json
```

The API exposes those release-owned preset values without changing their display scale. The UI maps raw importance values as follows in:

```text
web/src/preferences.ts
```

| Raw value | UI label |
| ---: | --- |
| `0.0` | No |
| `0.2` | Very Low |
| `0.4` | Low |
| `0.6` | Medium |
| `0.8` | High |
| `1.0` | Very High |

Therefore, the UI correctly renders the release value `1.0` as `Very High`. Hard-coding a special UI interpretation for Balanced would make the displayed values disagree with the API and with custom-edit behavior, so this must be corrected in the release-owned preset definition.

### Why changing every value to 0.6 preserves the ranking

The ranking engine normalizes active raw weights so that they sum to one. With 13 equally weighted criteria:

```text
Current:  1.0 / (13 × 1.0) = 1/13
Proposed: 0.6 / (13 × 0.6) = 1/13
```

Measured against the active preset, both forms normalize each criterion to approximately `0.0769230769`. Uniformly scaling every Balanced weight from `1.0` to `0.6` should therefore leave affinity scores, contributions, and ranking order unchanged.

This invariance only holds if every enabled Balanced criterion is changed together. A partial migration—for example, changing the older national criteria but leaving subsequently onboarded criteria at `1.0`—would no longer be balanced and would change results.

### Locality-analysis threshold constraint

Raw importance values have one additional use before normalization. Locality-derived criteria contribute to locality analysis when their raw weight meets the criterion's `locality_analysis_threshold`.

The active locality-derived criteria are:

| Criterion | Threshold | Current Balanced | Proposed Balanced |
| --- | ---: | ---: | ---: |
| `C66` — Extreme heat exposure | `0.6` | `1.0` | `0.6` |
| `C67` — Projected warm-day frequency (2030) | `0.6` | `1.0` | `0.6` |

The engine uses `raw_weight >= locality_analysis_threshold`, so a proposed value of exactly `0.6` keeps both criteria triggered. Regression tests must lock this behavior down. Choosing a value below `0.6` would preserve equal normalized affinity weights but would change locality-analysis status, so it would not satisfy this item's acceptance criteria.

### Authoritative release-generation changes

The Balanced values are embedded in release/catalog generation rather than maintained by the UI. Historical construction currently draws from several layers:

- The base catalog profile `equal_weight_mvp` stores its original criteria at `1.0`.
- `src/konsider/ingestion/phase4f.py` adds the job-market criterion to the equal-weight preset at `1.0`.
- `src/konsider/ingestion/phase4_wave2.py` adds education and research criteria at `1.0`.
- `PRESET_WEIGHTS` in `src/konsider/ingestion/phase5_locality_onboarding.py` adds `C66` and `C67` at `1.0`.
- Later releases carry the resulting preset forward in `consumer-catalog.json`.

For the combined release batch:

1. Establish or update the authoritative preset-generation source so `equal_weight_mvp` assigns `0.6` to every enabled criterion.

2. Apply the change as a deterministic release migration over the complete current preset, not as manual edits to generated JSON files. A safe migration should:

   - Locate `preference_presets[id == "equal_weight_mvp"]`.
   - Verify its criterion keys exactly match the intended enabled Balanced criterion set.
   - Replace every value with `0.6` in a stable, sorted representation.
   - Fail if criteria are unexpectedly missing or newly added without an explicit preset decision.

3. Update older generator constants that could otherwise reintroduce `1.0` when releases are rebuilt or replayed. In particular, review the Phase 4 and Phase 5 preset-extension constants listed above.

4. Keep the preset ID unless a separate migration requires renaming it. `equal_weight_mvp` is an internal identifier used as the default fallback by the release-backed recommendation service; changing it would create unnecessary compatibility work.

5. The existing description—“all enabled criteria contribute equally”—remains accurate. It may be refined only if product copy needs to explain that `Medium` represents neutral equal importance.

### API behavior

No ranking-algorithm change should be necessary. API v3 should expose the updated release-owned preset through `GET /api/v3/catalog`, and ranking, comparison, and country-detail operations should continue resolving `preference_preset_id: "equal_weight_mvp"` through the same release catalog.

The API must not rescale the catalog values back to `1.0` for display. It should:

- Return raw preset weights of `0.6` in the catalog.
- Normalize them internally for scoring as it already does.
- Return normalized ranking weights of approximately `1/13` for the 13-criterion active release.
- Continue reporting `resolved_preference_preset_id: "equal_weight_mvp"`.

### UI and fixture updates

No production UI mapping change is required. Once the new catalog is active, the existing importance mapping will display each `0.6` value as `Medium`.

Frontend fixtures and assertions that model the Balanced catalog must be updated to use `0.6` for every enabled criterion. Add an explicit UI regression test confirming that selecting Balanced renders every enabled importance control as `Medium`, without converting the selection to `Custom`.

### Snapshot and publication work

This item requires a new release snapshot because preference presets are part of the immutable release consumer catalog. Do not modify `2026-08-07.3` or its catalog snapshot in place.

Include the Balanced migration in the same new snapshot as the Region metadata fix and any further accumulated release changes. During publication:

1. Generate the new `consumer-catalog.json` through the release pipeline.
2. Confirm every `equal_weight_mvp.weights` value is exactly `0.6` and that its key set matches all enabled criteria.
3. Rebuild manifests/checksums and complete release replay and product-readiness validation.
4. Activate the new release only after API v3 and UI regression verification succeeds.

### Verification checklist

- [x] The generated Balanced preset contains every enabled criterion exactly once.
- [x] Every Balanced raw importance is exactly `0.6`.
- [x] `/api/v3/catalog` returns `0.6` for every Balanced criterion.
- [x] The UI displays `Medium` for every Balanced importance control.
- [x] The preset remains selected as Balanced until the user edits a value.
- [x] Normalized weights remain equal across all active criteria.
- [x] Normalized weights match the prior Balanced release within the agreed numeric tolerance.
- [x] Affinity scores and ranking order match the prior Balanced release.
- [x] Criterion contribution values match the prior Balanced release within numeric tolerance.
- [x] `C66` and `C67` continue to contribute and trigger locality analysis at the `0.6` threshold.
- [x] Coverage exclusions and locality assessments are unchanged.
- [x] Ranking, comparison, and country-detail operations resolve the same Balanced preset and normalized weights.
- [x] Release replay, schema validation, manifest validation, API tests, and frontend tests pass.

### Acceptance criteria

The item is complete when a newly published release causes every Balanced priority to display as `Medium`, while automated comparison with the prior release proves that equal normalized weighting, affinity scores, ranking order, criterion contributions, coverage behavior, and locality-analysis activation remain unchanged.

## Additional changes to batch

Add subsequent release-snapshot or API-engine findings below this heading before beginning the combined implementation and publication pass.

## Completed batch result

The architecture-first batch was published and activated on 2026-08-08 as coordinated immutable
release pair `2026-08-08.1` (schema 5.2 ranking base) and `2026-08-08.2` (schema 6.1 overlay).
The public API remains `konsider-api-3.0`; no new API version was required. All six v3 surfaces
resolve base release ID `2026-08-08.1`, and `data/releases/active.json` selects overlay
`2026-08-08.2`. The generated release report is under
`data/reports/snapshot-release-2026-08-08.2/`.
