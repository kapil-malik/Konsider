# TFC source and rule workflow

Status: Phase 7F first-wave official evidence captured and staged; no activation

## Add a source

1. Register a stable source ID and one bounded family: structured API, official table, official
   policy document, rule schedule, jurisdiction mapping or formula table.
2. Record publisher, responsible authority, exact asset or endpoint, extraction timestamp, source
   publication date, effective period, SHA-256 or lawful immutable identity, access and licence,
   attribution, refresh cadence, change detection, parser version and manual-review status.
3. Capture online only in the worker through an injected fetcher. Freeze exact URL, parser result,
   byte count and checksum. Retain raw source bodies only when approved; Phase 7F retains
   checksum-only normalized derivatives.
4. Promote the captured metadata and normalized conclusion into the source/legal manifest. A
   research script is never a runtime dependency.

Manual review remains `PENDING` when legal interpretation, extraction ambiguity or conflicting
authorities need a human decision. Such evidence cannot produce supported evaluation.

## Add a jurisdiction

Reuse `country:AAA` for canonical countries. Assign typed IDs such as `region:DE-BE`,
`city:example`, `institution:example` or `regulator:example` for narrower authorities and bind each
to its canonical country. A child must identify a known parent. Do not place route or regulator
identities in country-code fields.

## Add a route or rule

Create a versioned `ROUTE_RULE` with a stable route ID, typed jurisdiction, bounded conditions,
typed thresholds, source references and full effective-period metadata. A regional override names
the record it overrides. New versions must not overlap older versions for the same route and
jurisdiction.

Conditions remain inspectable data: presence, equality or typed threshold comparisons. Do not add
an arbitrary expression language or conceal substantive policy in parser code.

## Add a metric formula

Create a `METRIC_FORMULA` only after its result family and units are approved. Choose a versioned
formula type, output unit and named components with field IDs, coefficients and units. Currency,
period, ranges, assumptions and rounding belong in later type-specific contracts when required.
Never convert a metric into a 1-10 ordering score without a separate approved decision.

The Phase 7D housing formula is fictional and proves serialization only. It is not an approved TFC.

## Effective dates and review

For every mutable legal, policy or rate record, capture:

- effective-from and optional effective-to;
- source publication/update date;
- verification date and stale-after date;
- superseded record ID; and
- conflict status and resolution note.

At refresh, compare captured checksums first, rebuild normalized artifacts offline, generate a
semantic diff and review every source, rule, date, policy and support-state change. Future, expired,
stale and unresolved-conflict rules cannot back `SUPPORTED` rows.

## Build and replay

The checked-in input below is visibly fictional. Write candidates outside `data/releases`; Phase 7D
does not publish or activate them.

```powershell
python scripts\build_phase7d_tfc_foundation.py build `
  --capture tests\fixtures\phase7d\synthetic-capture.json `
  --base-release data\releases\2026-08-04.1 `
  --output .ci-tmp\phase7d-candidates

python scripts\build_phase7d_tfc_foundation.py replay `
  --capture tests\fixtures\phase7d\synthetic-capture.json `
  --release .ci-tmp\phase7d-candidates\synthetic-phase7d-6.0
```

Compare two validated candidates:

```powershell
python scripts\build_phase7d_tfc_foundation.py diff `
  --before <first-candidate> `
  --after <second-candidate>
```

Replay must report `PASSED` with no mismatched files. A checksum mismatch, incomplete support
matrix, broken jurisdiction, overlapping rule, unresolved selected conflict or forbidden profile,
ranking or Opportunity Filter field blocks the candidate.

The first-wave production candidate uses a separate capture/build/replay command:

```powershell
python scripts\build_phase7f_tfc_candidate.py capture `
  --captured-at 2026-08-05T12:00:00Z `
  --output data\reports\phase7f-2026-08-05\phase7f-source-capture.json

python scripts\build_phase7f_tfc_candidate.py build `
  --source-capture data\reports\phase7f-2026-08-05\phase7f-source-capture.json `
  --research-support data\reports\phase7b-2026-08-05\country-support-matrix.jsonl `
  --base-release data\releases\2026-08-04.1 `
  --release-id phase7f-first-wave-2026-08-05.6.0 `
  --validation-date 2026-08-05 `
  --output data\reports\phase7f-2026-08-05

python scripts\build_phase7f_tfc_candidate.py replay `
  --production-capture data\reports\phase7f-2026-08-05\production-capture.json `
  --release data\reports\phase7f-2026-08-05\staged-release\phase7f-first-wave-2026-08-05.6.0
```

The final production overlay can be replayed independently:

```powershell
python -m konsider.ingestion.phase7_release_publication replay --release-id 2026-08-05.1
```

## Research-to-production promotion

Research establishes source feasibility but cannot be copied directly into a release. Promotion
requires owner-approved TFC identity and result semantics, lawful captured bytes, production parser
and version, exact normalized records, explicit 91-country support, legal/manual review, complete
validation, deterministic replay, semantic-diff review and a new immutable release ID.

Phase 7F completed first-wave evidence onboarding. Phase 7J then revalidated the exact owner scope,
support matrix, source/legal manifest and replay before publishing immutable release
`2026-08-05.1`. Future corrections or source changes require a new release ID; never edit the
published directory. See the [first-wave evidence guide](../product/tfc-first-wave-evidence.md).
