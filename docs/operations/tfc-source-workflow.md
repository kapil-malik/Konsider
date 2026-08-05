# TFC source and rule workflow

Status: Phase 7D production-shaped workflow proven with fictional inputs only

## Add a source

1. Register a stable source ID and one bounded family: structured API, official table, official
   policy document, rule schedule, jurisdiction mapping or formula table.
2. Record publisher, responsible authority, exact asset or endpoint, extraction timestamp, source
   publication date, effective period, SHA-256 or lawful immutable identity, access and licence,
   attribution, refresh cadence, change detection, parser version and manual-review status.
3. Capture online only in the worker through an injected fetcher. Verify bytes against the frozen
   checksum and retain them outside the API runtime.
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

## Research-to-production promotion

Research establishes source feasibility but cannot be copied directly into a release. Promotion
requires owner-approved TFC identity and result semantics, lawful captured bytes, production parser
and version, exact normalized records, explicit 91-country support, legal/manual review, complete
validation, deterministic replay, semantic-diff review and a new immutable release ID.

Phase 7F is the earliest first-wave evidence-onboarding phase. Phase 7D contains no production
route evidence and provides no publication command.
