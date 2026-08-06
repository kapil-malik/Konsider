# Catalog display metadata centralization and uniform naming plan

Status: proposed implementation plan only  
Scope: ordering criteria, Opportunity Filters (OFCs), and Typed Feasibility Checks (TFCs)  
Constraint: preserve every current user-facing name exactly during the migration

## 1. Decision summary

Konsider should have one authoritative, versioned authoring catalog for criterion display metadata.
Evidence collection, scoring, threshold policies, route rules, and other domain processing should
refer to a criterion only by its stable ID. Release builders should join those ID-keyed technical
artifacts to the authoritative display catalog and publish immutable, checksum-bound catalog
snapshots.

The common display vocabulary for all three product roles will be:

- `displayName`: required formal user-facing name;
- `compactName`: optional shorter user-facing name; and
- `sectionName`: optional user-facing section name.

Section identity must not depend on editable copy, so the model also needs a stable `sectionId`.
The authoring catalog will define a section name once, and definitions will refer to it by
`sectionId`. A release builder may denormalize the resolved `sectionName` into its immutable
snapshots for simple API consumption.

This proposal deliberately does not centralize unrelated prose such as `meaning`, `description`,
`interpretation`, limitations, caveats, TFC questions, profile prompts, status messages, or field
help. Those can be considered separately. It does remove any build-time generation of those fields
from `displayName`, because that would make a name change alter semantic prose accidentally.

## 2. Desired end state

```text
authoritative product display catalog
                 +
evidence, scoring, policies and rules keyed only by stable ID
                 |
                 v
          release builders
                 |
                 v
three immutable release catalog snapshots
  - consumer-catalog.json
  - opportunity-filter-catalog.json
  - tfc-catalog.json
                 |
                 v
         API contract and UI
```

The authoritative authoring file should be:

```text
data/catalogs/product-display-catalog.json
```

This is one logical source of truth for all three product roles. The three files under
`data/releases/<release-id>/` remain immutable runtime snapshots, not independently edited sources.

The source catalog itself should be versioned and checksum-addressable. Each release build report
should record its catalog version and checksum. Published historical releases continue to carry
their own snapshots, so changing the authoring catalog later cannot change historical results.

## 3. Authoritative source contract

Add an authoring-time JSON Schema for a new catalog family such as
`konsider-product-display-catalog-1.0`. This is an input contract, not a published evidence-release
contract.

A recommended shape is:

```json
{
  "schemaVersion": "konsider-product-display-catalog-1.0",
  "catalogVersion": "2026-08-06.1",
  "sections": [
    {
      "productRole": "OPPORTUNITY_FILTER",
      "sectionId": "career",
      "sectionName": "Career",
      "sortOrder": 10
    },
    {
      "productRole": "OPPORTUNITY_FILTER",
      "sectionId": "education",
      "sectionName": "Education",
      "sortOrder": 20
    }
  ],
  "definitions": [
    {
      "productRole": "OPPORTUNITY_FILTER",
      "id": "technology_software_opportunity",
      "displayName": "Technology and software employment ecosystem",
      "compactName": "Technology and software",
      "sectionId": "career"
    }
  ]
}
```

Required invariants:

1. `(productRole, id)` is unique.
2. `(productRole, sectionId)` is unique.
3. Every non-null `sectionId` resolves within the same `productRole`.
4. `displayName` is non-empty.
5. `compactName` is either non-empty or null.
6. A definition without a current compact name stores `compactName: null`; it does not invent copy.
7. A definition without a current section stores `sectionId: null`; its resolved `sectionName` is
   null.
8. Section order is explicit and unique within a product role.
9. Definition order remains explicit in the product-specific technical catalog or is added as a
   separate stable `sortOrder`; array position must not be the only ordering contract.
10. The catalog contains no evidence, scores, thresholds, coverage counts, policy versions, source
    versions, or destination support.

Use these product-role identifiers:

- `ORDERING_CRITERION`
- `OPPORTUNITY_FILTER`
- `TYPED_FEASIBILITY_CHECK`

## 4. Exact preservation rules

The initial authoritative catalog must be seeded from the active immutable releases, not typed
again from Python constants or documentation.

### Ordering criteria

- `displayName` is copied byte-for-byte from the current `display_name`.
- `compactName` is null because ordering criteria currently have no distinct compact label.
- `sectionName` is copied byte-for-byte from the current `category`.
- Each distinct current category receives a stable, non-display `sectionId`.

Current section text that must remain unchanged includes:

- Affordability
- Climate and environment
- Education and human capital
- Education, research and innovation
- Environment
- Equality
- Healthcare
- Infrastructure
- Institutions
- Integration context
- Jobs and economic opportunity
- Safety

FCC/PCC coverage mode and LSC locality derivation remain technical fields and must not be represented
as display sections.

### Opportunity Filters

- `displayName` is copied byte-for-byte from the current `display_name`.
- `compactName` is copied byte-for-byte from the current `compact_label`.
- `sectionName` is `Career` or `Education`, preserving the UI's present casing.
- The current machine categories `CAREER` and `EDUCATION` become stable section IDs, preferably
  normalized to `career` and `education` in the authoring contract and mapped once during migration.

### Typed Feasibility Checks

- `displayName` is copied byte-for-byte from the current TFC `name`.
- `compactName` is null because the active TFC release has no distinct compact name.
- `sectionName` is null because TFCs are not currently grouped into named sections.
- `applicable_purposes` and `result_family` remain technical classification fields; neither is
  silently converted into a display section.

No wording change is allowed in this migration. A generated migration report should compare the
old and new resolved values for every ID and fail if any non-null current value changes.

## 5. Shared loader and join boundary

Add one small domain-neutral loader responsible for:

- reading and validating the authoring catalog;
- indexing definitions by `(productRole, id)`;
- indexing sections by `(productRole, sectionId)`;
- resolving `sectionName`;
- rejecting duplicate, missing, orphaned, or unexpected IDs; and
- returning immutable display metadata records.

The loader should expose a narrow interface conceptually equivalent to:

```python
display_catalog.definition("ORDERING_CRITERION", criterion_id)
display_catalog.definition("OPPORTUNITY_FILTER", filter_id)
display_catalog.definition("TYPED_FEASIBILITY_CHECK", tfc_id)
```

Release builders must receive the catalog or loader explicitly. Avoid module-level reads hidden in
processors, so tests and offline replay can inject a pinned catalog.

The join belongs at catalog/release assembly time. Parsers, evidence collectors, scoring functions,
threshold engines, and TFC evaluators must not receive names.

## 6. Ordering-criterion ingestion changes

The generic schema-5 worker is already close to the desired boundary: it receives a completed
catalog and technical policies separately. Preserve that design.

Refactor production onboarding code as follows:

1. Remove `display_name` from locality criterion configuration in
   `src/konsider/ingestion/phase5_locality_onboarding.py`.
2. Resolve the display metadata for C66 and C67 from the authoritative catalog during consumer
   catalog assembly.
3. Replace copied legacy `category`/`display_name` access with a single display-catalog join for all
   active ordering criteria.
4. Remove active production name literals from:
   - `src/konsider/ingestion/phase4f.py`;
   - `src/konsider/ingestion/phase4_wave2.py`; and
   - `src/konsider/ingestion/phase5_locality_onboarding.py`.
5. Historical fixtures may retain synthetic names local to the fixture. They are not production
   authorities.
6. Keep criterion policies, outcomes, observations, scores, source lineages, and locality evidence
   keyed by criterion ID exactly as today.

The new ordering release snapshot definition should contain:

```json
{
  "id": "C66",
  "displayName": "Extreme heat exposure",
  "compactName": null,
  "sectionId": "climate_environment",
  "sectionName": "Climate and environment"
}
```

All existing technical and explanatory fields continue alongside these fields.

## 7. Opportunity Filter ingestion changes

Refactor the Phase 6 pipeline so public names are absent from evidence configuration:

1. Remove `display_name`, `compact_label`, and `meaning` values derived from either name from
   `CareerFilterConfig` and `EducationFilterConfig`.
2. Keep only technical inputs there: filter ID, route IDs, source IDs, source dependency mode,
   thresholds, expected evidence counts, and similar evidence-building data.
3. Make `_definition` and `_education_definition` join display metadata by filter ID.
4. Replace the `EXPECTED_NAMES` publication guard in
   `src/konsider/ingestion/phase6_release_publication.py` with an `EXPECTED_FILTER_IDS` gate.
5. Validate exact ID-set equality among:
   - authoritative OFC display definitions;
   - technical filter configurations;
   - threshold policies;
   - evidence rows;
   - coverage summaries; and
   - the release snapshot.
6. Replace prose generation that interpolates `config.display_name`. Existing `meaning`, construct,
   and description text must be preserved explicitly rather than regenerated from the new name.
7. Remove the UI's hard-coded OFC `groups` label array once the new API supplies `sectionId`,
   `sectionName`, and section ordering.

The new OFC snapshot definition should contain:

```json
{
  "id": "technology_software_opportunity",
  "displayName": "Technology and software employment ecosystem",
  "compactName": "Technology and software",
  "sectionId": "career",
  "sectionName": "Career"
}
```

The current `category` field is replaced by stable `sectionId` plus display `sectionName`.

## 8. TFC ingestion changes

Refactor the first-wave TFC path as follows:

1. Remove `name` literals from `_catalog()` in
   `src/konsider/ingestion/tfc_first_wave.py`.
2. Prefer moving the entire display-neutral TFC definition assembly out of the source-capture module;
   source capture should not manufacture public catalog copy.
3. Resolve `displayName`, `compactName`, `sectionId`, and `sectionName` from the authoritative catalog
   by `tfc_id` when the TFC release catalog is assembled.
4. Preserve `user_question`, input requirements, supported-profile boundary, public limitations,
   purposes, policy ID, result family, refresh cadence, and support boundaries exactly as today.
5. Keep route/rule evidence, source/legal records, policy bundles, coverage, and outcomes keyed only
   by `tfc_id`.
6. Add an explicit `sortOrder` to the TFC release catalog instead of deriving it from array position
   in the API service.

The new TFC snapshot definition should contain:

```json
{
  "id": "skilled_work_route_feasibility",
  "displayName": "Highly qualified work route check",
  "compactName": null,
  "sectionId": null,
  "sectionName": null,
  "sortOrder": 10
}
```

This also removes the current `tfc_id` versus `id` and `name` versus `display_name` translation at
the API boundary.

## 9. Release-contract changes

Do not mutate historical schemas or published releases. Introduce new catalog contract majors:

- `consumer-catalog-4.0`
- `opportunity-filter-catalog-2.0`
- `tfc-release-catalog-2.0`

For the three display concepts, the published schemas use only:

- `displayName`
- `compactName`
- `sectionName`

They may additionally use `sectionId` and `sortOrder`, because those are identities/order rather
than alternative names.

Remove these old fields from the new schemas:

- ordering `display_name` and `category`;
- OFC `display_name`, `compact_label`, and `category`; and
- TFC `name`.

Do not add aliases containing the same text to the new immutable snapshots. Compatibility belongs
at a versioned boundary, not as permanent duplicate fields.

Because the active TFC overlay checksum-binds its base release, the migration requires:

1. a new base release containing the new consumer and OFC catalog snapshots; and
2. a new TFC overlay containing the new TFC catalog snapshot and binding the new base checksum.

Use new release contract versions rather than weakening the existing 5.1/6.0 contracts. A practical
minimal versioning choice is a new base contract such as `konsider-release-5.2` and overlay contract
such as `konsider-release-6.1`, provided the new schemas explicitly bind the new catalog majors.
If project policy treats a catalog field rename as requiring a release major, use the next release
major instead. The implementation must decide this once and record it in an ADR; it must not edit
the 5.1 or 6.0 schemas in place.

The new manifests and build reports should record:

- authoritative catalog schema version;
- authoritative catalog version;
- authoritative catalog checksum;
- each emitted catalog snapshot checksum; and
- a display-metadata equivalence report for this no-copy-change migration.

Evidence, outcome, score, source, policy, and coverage artifacts should remain byte-identical where
their schemas are unchanged.

## 10. API-contract changes

This is a breaking transport change even though the visible strings do not change. Publish
`konsider-api-3.0` and expose it under `/api/v3` rather than silently changing API v2.

Limit camel-case migration to the agreed display vocabulary; do not rename every unrelated API
field in this work.

For criterion/filter/TFC definitions, API v3 exposes:

```text
id
displayName
compactName
sectionId
sectionName
sortOrder
```

Rules:

- `displayName` is required.
- `compactName`, `sectionId`, and `sectionName` are nullable.
- `compactName ?? displayName` is the only compact-title fallback.
- A non-null `sectionId` requires a non-null `sectionName`.
- The API must not map TFC `name` to `displayName`; the release snapshot already uses
  `displayName`.
- The API must not invent OFC section labels from enum values.

Remove duplicate response-specific naming such as `criterion_name`. Ranking contributions and
comparison rows should carry `displayName`, or preferably carry only `criterion_id` when the parent
response already includes an authoritative definition map. The least disruptive v3 choice is to
replace `criterion_name` with `displayName` while leaving IDs and response structure unchanged.

Keep API v2 available only for an explicitly bounded compatibility window if it is still useful for
tests or local rollback. Since there are no external consumers, it can be removed after the UI and
end-to-end tests use v3. Avoid a permanent dual-write model.

Regenerate from FastAPI's authoritative OpenAPI output:

- `contracts/openapi/konsider-api-3.0.json`;
- `web/src/api/openapi.json`; and
- `web/src/api/schema.d.ts`.

## 11. UI changes

UI behavior and visible wording remain unchanged, but property access becomes uniform:

- `criterion.display_name` becomes `criterion.displayName`;
- `definition.compact_label` becomes `definition.compactName`;
- TFC `definition.display_name` becomes `definition.displayName`;
- comparison/contribution `criterion_name` becomes `displayName`; and
- ordering `category`/OFC `category` presentation becomes `sectionName`.

Update the following consumers at minimum:

- `web/src/components/ImportanceControl.tsx`
- `web/src/components/OpportunityFiltersPanel.tsx`
- `web/src/components/AssessmentSummary.tsx`
- `web/src/components/RankingView.tsx`
- `web/src/components/ComparisonView.tsx`
- `web/src/components/CountryDetails.tsx`
- `web/src/components/SituationDialog.tsx`
- `web/src/components/SourcesDialog.tsx`
- `web/src/tfcPresentation.ts`
- frontend fixtures, unit tests, and end-to-end tests

Replace the OFC hard-coded section array with grouping by `sectionId`, ordered by source-catalog
section order and labelled by `sectionName`. Ordering criteria and TFCs should not be newly grouped
as part of this migration; their fields are present for consistency and future use.

Do not change profile-field prompts, help text, select options, status labels, or other general UI
copy in this work.

## 12. Validation and failure behavior

All joins must fail closed. A release must not be buildable when:

- a technical ID lacks display metadata;
- display metadata contains an unused production ID;
- an ID appears under the wrong product role;
- a section reference is missing or cross-role;
- duplicate definitions or sections exist;
- `displayName` is blank;
- `compactName` is blank rather than null;
- section order or definition order is ambiguous;
- a builder supplies a public name independently of the catalog; or
- the generated snapshot differs from the authoritative values.

Add a static or structural regression test that production ingestion configuration contains no
fields named `display_name`, `displayName`, `compact_label`, `compactName`, `name` when used as a
criterion title, `category` when used as a display section, or literal accepted-name dictionaries.
The test should target production builder modules, not synthetic fixtures.

## 13. Test plan

### Authoring catalog

- JSON Schema validation.
- Unique IDs and section IDs.
- Complete exact ID inventory for all active ordering criteria, nine OFCs, and three TFCs.
- Section resolution and null behavior.
- Stable ordering.

### Builder tests

- Every builder joins by ID.
- Missing/extra metadata fails before writing a draft.
- Evidence processors receive no display metadata.
- `EXPECTED_NAMES` no longer exists.
- OFC generated prose does not change when only display metadata changes.
- TFC source capture contains no title literals.

### Release tests

- Old published releases still validate with old schemas.
- New base and overlay validate with new schemas.
- Catalog and release checksums reconcile.
- Replaying a published release uses its snapshot and is independent of the current authoring file.
- Evidence, scores, outcomes, coverage, ranking order, OFC states, and TFC outcomes are unchanged.
- An automated old-to-new report proves exact preservation of every current display, compact, and
  section string.

### API tests

- API v3 emits the uniform fields for all three product roles.
- No old title keys appear in v3.
- Ranking and comparison response names agree with catalog `displayName`.
- Nullable compact and section fields serialize consistently.
- OpenAPI and generated TypeScript types agree.

### UI tests

- Every visible criterion/OFC/TFC name is unchanged.
- OFCs remain grouped as Career then Education.
- OFC compact-name fallback remains correct.
- Ordering criteria remain ungrouped.
- TFC relevance sorting remains based on `applicable_purposes`, not `sectionName`.
- Accessibility labels and tooltips use the same resolved names as visible content.

## 14. Recommended implementation sequence

Implement in separable checkpoints:

1. **Golden inventory:** generate a checked test fixture from the active releases containing all
   current names, compact names, and section names.
2. **Authoring contract:** add the authoritative source JSON, its schema, loader, indexes, and
   validation tests.
3. **Builder centralization without wire changes:** make ordering, OFC, and TFC builders source names
   only from that catalog while temporarily emitting the existing release shapes. Prove generated
   text and technical artifacts are unchanged.
4. **New release contracts:** add the uniform camel-case snapshot schemas and update loaders/writers
   without modifying historical schemas.
5. **API v3:** add uniform transport models and serialization, export OpenAPI, and generate frontend
   types.
6. **UI cutover:** update property access and make OFC section presentation catalog-driven.
7. **Publish base release:** build, validate, publish, but do not activate until the overlay exists.
8. **Publish TFC overlay:** bind it to the exact new base checksum.
9. **Cross-feature verification:** compare rankings, comparisons, country details, OFCs, locality
   assessments, profile behavior, and TFC outcomes against the current active release.
10. **Activate atomically:** select the new overlay only after all gates pass.
11. **Remove transitional paths:** once rollback confidence is adequate, remove temporary v2/UI
    compatibility code while retaining historical release readers.

Checkpoint 3 is intentionally separate from the field rename. It proves centralization first, then
allows schema/API/UI migration failures to be diagnosed independently.

## 15. Non-goals

This change must not:

- rename any criterion, OFC, TFC, or section;
- change any stable criterion/filter/TFC ID;
- change coverage mode, locality scope, weights, scores, thresholds, or ranking behavior;
- change OFC evidence states or survivor ordering;
- change TFC rules, support boundaries, policies, questions, or outcomes;
- centralize country or locality names;
- centralize profile-field prompts/help or general UI copy;
- infer TFC sections from purposes;
- group ordering criteria or TFCs in the UI merely because section fields now exist; or
- mutate an existing published release or historical schema.

## 16. Completion criteria

The migration is complete when:

1. One authoritative authoring JSON contains all criterion display, compact, and section names.
2. No production ingestion, source, evidence, policy, or release-publication module owns an exact
   criterion title.
3. Every technical artifact relates to criteria by stable ID.
4. All three immutable release catalogs expose the uniform display fields.
5. API v3 and the UI consume those fields without product-specific name translation.
6. OFC section labels and ordering come from the catalog rather than a UI constant.
7. Existing published releases remain readable and immutable.
8. A new base release and TFC overlay are published and checksum-bound.
9. Automated equivalence proves that no current user-facing name changed.
10. Ranking, filtering, locality, profile, and feasibility outputs remain semantically identical.

## 17. Architectural conclusion

The stable ID is the cross-layer identity. The authoritative authoring catalog is the only place a
current public name is edited. A release snapshots that catalog immutably. The API serves the
snapshot, and the UI renders the API without maintaining a second title dictionary.

This preserves historical reproducibility while making future copy maintenance a deliberate,
single-touch catalog change followed by a normal release.
