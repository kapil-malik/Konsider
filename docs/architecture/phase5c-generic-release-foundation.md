# Phase 5C: generic locality-aware release foundation

Status: complete

Date: 2026-07-28

Scope: schema-5 ingestion orchestration, validation, immutable release/catalog storage, loading,
and replay

Active release, API, UI, ranking engine, locality-coherence logic, and production C66 data changed:
no

## Outcome

Phase 5C replaces the future release path's country-only and one-source assumptions with one
policy-driven schema-5 foundation. The implementation supports:

- global-core, conditional-complete-case, and diagnostic coverage modes;
- national-direct and locality-derived evidence independently of coverage;
- country, city, metro, region, and service-area subjects;
- multiple source inputs and multiple declared lineage records per criterion;
- an explicit country outcome matrix;
- versioned locality universes and aggregation policies;
- replayable derived country observations, scores, and contributor evidence; and
- immutable release and catalog snapshots with deterministic LF serialization and checksums.

The implementation is in
`src/konsider/ingestion/current_release.py`. Historical schema-3/4 worker, repository, and active
API consumer paths remain unchanged and retain their existing tests. Schema 5 intentionally uses a
separate repository until the API-v2 migration, preventing a schema-current release from falling
through the old complete-country-matrix loader.

## Orchestration boundary

`GenericReleaseWorker` reads declarative criterion policies and dispatches versioned processors.
The release snapshots those policies in `criterion-policies.json`. Parsers and scoring transforms
remain code, but replay fails if the exact declared processor ID/version is not registered.

Each processor returns entity-neutral observations and scores, optional derived evidence, and
normalized country rejection reasons. Shared orchestration builds the country outcome matrix.
There is no criterion-specific or Phase-specific release writer.

Phase 5C does not decide or implement production aggregation. The synthetic locality processor used
by tests is deterministic fixture code only. Phase 5D remains responsible for executable
aggregation and locality-coherence policy.

## Entity and outcome model

Countries use IDs such as `country:CAN`; localities use source-stable namespaced IDs. Validation
checks type, parent-country existence, source mappings, locality-universe membership, and subject
references. A locality can never masquerade as a country.

Per [ADR 008](decisions/008-schema5-orchestration-and-country-outcomes.md), explicit outcomes exist
only for country results. Every criterion/country pair has exactly one outcome. Locality
observations and scores remain inspectable evidence and are linked into derived country evidence;
they do not create a second sparse outcome matrix.

The Phase 5B derived-evidence contract was tightened during implementation. It now requires
`result_observation_id` and `result_score_id`, and a valid derived outcome references both the
generated country observation and its evidence row. This is necessary to replay derived country
observations, not only their scores.

## Release partition

Large row sets are JSONL:

- `geographic-entities.jsonl`
- `observations.jsonl`
- `scores.jsonl`
- `criterion-outcomes.jsonl`
- `derived-country-evidence.jsonl`

Small snapshots are sorted JSON:

- `source-lineages.json`
- `locality-universes.json`
- `aggregation-policies.json`
- `criterion-policies.json`
- `consumer-catalog.json`
- `validation.json`

`manifest.json` reconciles every payload checksum, aggregate release checksum, criterion coverage,
entity and artifact counts, lineage/universe/policy IDs, and scoring versions. Publishing also
writes an immutable catalog snapshot. Activation is separate and defaults off in Phase 5C.

## Validation

The schema-current validator rejects:

- duplicate or broken entity identity and locality parentage;
- undeclared locality observations or locality-universe members;
- policy/catalog contradictions across coverage, scope, applicability, readiness, and scoring;
- unknown or mismatched source lineages, including incomplete multiple-source outcome lineage;
- score/observation subject or criterion mismatches;
- unknown aggregation policies or policy-version mismatches;
- missing contributor observation/score lineage;
- derived result observation/score/evidence disagreement;
- missing or duplicate country outcomes;
- invalid score range through the schema contract; and
- catalog coverage counts that do not reconcile with the explicit outcome matrix.

This proves coverage and locality scope are independent: tests exercise national FCC, national PCC,
locality-derived FCC, and locality-derived PCC in one release.

## Replay and clean checkouts

Replay loads and revalidates the immutable release, invokes the exact snapshotted processor
versions, writes a temporary release, and compares every payload file byte-for-byte. Results are:

- `PASSED` for deterministic equality;
- `FAILED` for checksum, validation, or byte mismatch; and
- `SOURCE_BYTES_UNAVAILABLE` when licensed/local source bytes are intentionally absent.

The last state is not reported as corrupted committed data. It preserves the existing clean-checkout
boundary: normalized committed releases remain loadable while full source replay requires retained
local bytes.

## Migration and compatibility

The reusable outcome construction, validation, deterministic serialization, checksum, catalog
snapshot, and replay responsibilities that had accumulated in Phase 4F and Phase 4 Wave 2 now have
one schema-current home. Those historical scripts are retained for byte-exact audit and replay;
the new path does not call them.

The `/api/v1` published-release repository stays restricted to release 3/4 and catalog 1/2 until
Phase 5E. Schema-5 loading is available through `CurrentReleaseRepository`, so Phase 5 work does
not silently fall back to old complete-matrix semantics.

## Verification

The Phase 5C test suite covers the four coverage/scope combinations, multiple-source lineage,
deterministic draft/write/load/publish/replay, immutable IDs, catalog snapshot isolation, and
invalid parentage, undeclared locality, broken aggregation lineage, contradictory policy metadata,
multiple-source mismatch, missing country outcomes, and unavailable ignored bytes.

Final repository-root gates:

| Command | Result |
| --- | --- |
| `python -m pytest tests/unit/ingestion/test_phase5c_current_release.py tests/unit/test_phase5b_contracts.py -q` | 48 passed |
| `python -m pytest -q` | 237 passed |
| `python -m ruff check .` | All checks passed |
| `python -m black --check .` | 97 files unchanged |

The four-criterion synthetic release (two countries, two localities, direct and derived evidence)
is asserted below 256 KiB. This is a regression envelope, not a production capacity claim; the
JSONL partition is the scaling boundary for later measured C66 data.

No production locality source was onboarded. C66 remains **Extreme heat exposure**, retains
**Extreme-weather risk** as its historical name, and remains gated on source semantics and scoring
decisions owned by later phases.
