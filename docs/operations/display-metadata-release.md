# Display-metadata-only release workflow

Use this workflow after changing the public name, compact name, section, or display order of an
ordering criterion, Opportunity Filter (OFC), or Typed Feasibility Check (TFC). It creates a new
immutable ranking/OFC base and a checksum-bound TFC overlay without refreshing evidence or
recomputing product outcomes.

## What to edit

Edit only the authoritative authoring file:

`data/catalogs/product-display-catalog.json`

- Change `displayName` for a public title.
- Change `compactName` for compact UI copy.
- Change a definition's `sectionId` to move it to an existing section.
- Change a section's `sectionName` once to rename that section everywhere.
- Change a definition's `sortOrder` to change criterion/filter/check order. Change an OFC section's
  `sortOrder` to change OFC group order. Values must remain unique within a product role. Ordering
  and TFC sections are not currently rendered as groups, so their section order has no UI effect.
- Increment `catalogVersion` for every release-worthy edit. Use a unique, monotonically advancing
  value such as `YYYY-MM-DD.N`.

Do not change a criterion `id`, `productRole`, or `sectionId` merely to revise copy. Those values
are stable technical identities. Adding/removing a criterion, changing evidence, or changing a
rule is not a display-only release and must use the corresponding normal ingestion workflow.

## Recommended review-first workflow

From the repository root, prepare the pair:

```powershell
python -m konsider.ingestion.display_metadata_release prepare
```

The command automatically:

1. Reads `data/releases/active.json` and resolves its schema-6.1 overlay and schema-5.2 base.
2. Validates the authoring catalog and exact stable-ID inventory.
3. Requires a new `catalogVersion` and at least one real display-field change.
4. Selects the next two unused `YYYY-MM-DD.N` release IDs.
5. Regenerates only `consumer-catalog.json`, `opportunity-filter-catalog.json`, and
   `tfc-catalog.json`.
6. Copies all evidence, policies, rules, observations, scores, and validation artifacts
   byte-for-byte from the active pair and verifies each copied byte sequence.
7. Recomputes catalog, manifest, base, and overlay checksums and validates all release contracts.
8. Writes draft releases under `data/releases/.draft/<release-id>/` and an audit report under
   `data/reports/display-metadata-<overlay-release-id>/`.

`prepare` does not publish a release and does not modify `active.json`. Its final JSON output gives
the generated base ID, overlay ID, and report directory.

Review `display-metadata-changes.json` in that report directory. It lists every allowed field's
before/after values and states that network access was absent and non-catalog artifacts were
copied byte-for-byte. Also review `build-manifest.json`, which records the source pair, new pair,
authoring-catalog checksum, release checksums, and checksums for every unchanged artifact.

After review, publish the exact IDs printed by `prepare`:

```powershell
python -m konsider.ingestion.display_metadata_release publish `
  --base-release-id <base-release-id> `
  --overlay-release-id <overlay-release-id>
```

Publishing moves the validated drafts into the immutable release namespace and creates the
release-scoped consumer-catalog snapshot. It does not change the active pointer.

Activate the published overlay:

```powershell
python -m konsider.ingestion.display_metadata_release activate `
  --overlay-release-id <overlay-release-id>
```

Activation revalidates the overlay, its exact checksum-bound base, and the complete active release
before atomically replacing `data/releases/active.json`. The activation report records the prior
pointer as the rollback target.

Restart or redeploy the API after activation. The API intentionally loads one validated immutable
release at process startup.

## Single-command workflow

When the authoring edit has already been reviewed and immediate activation is intentional, the
entire prepare, validate, publish, and activate sequence is:

```powershell
python -m konsider.ingestion.display_metadata_release release --confirm-activate
```

The confirmation flag is mandatory because this command publishes immutable directories and
changes the active pointer. It uses the same gates and reports as the review-first workflow.

If preparation fails, nothing is published or activated. If publication succeeds but a later
activation gate fails, the new immutable pair remains published but inactive; the old pointer
remains active. Fix the cause and run `activate` for the already-published overlay—do not edit or
reuse its release directories.

## Offline and safety guarantees

This command performs filesystem-only release assembly. It contains no HTTP client, browser,
source connector, worker refresh, or subprocess call. It never fetches external websites and does
not rerun evidence ingestion. The active release's non-catalog artifacts are copied and compared
byte-for-byte.

The command refuses to proceed when:

- the active pair is not schema 5.2/6.1;
- the authoring `catalogVersion` was not incremented;
- there is no actual display change;
- technical ID inventories differ;
- a catalog or manifest violates its schema;
- either new immutable ID already exists; or
- the overlay does not bind the exact newly generated base checksum.

Run the normal repository test and pre-push gates before committing the authoring edit and newly
generated release artifacts.

## Rollback

The activation report contains the exact previous pointer. Rollback means atomically selecting
that previously published overlay again and restarting/redeploying the API. Never mutate the new
or old published release directories.
