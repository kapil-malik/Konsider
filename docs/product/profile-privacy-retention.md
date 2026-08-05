# Profile privacy and retention

Status: Phase 7C policy contract

## Defaults

Phase 7 is guest-first. Profile values exist in browser tab memory and in the stateless evaluation
request only. The server does not persist them. Closing the tab clears the default context.

Profile values are prohibited in:

- URLs and query strings;
- application or access logs;
- analytics events and session-replay tools; and
- immutable public release artifacts.

Operational telemetry may record schema versions, selected TFC IDs and aggregate outcome statuses,
but not field values, unknown-field lists or snapshot contents.

## Sensitivity and minimization

Fields are classified `LOW`, `MODERATE_PERSONAL`, `MODERATE_CONSEQUENTIAL`, `HIGH_PERSONAL`,
`HIGH_FINANCIAL` or `HIGH_CONSEQUENTIAL`. TFC definitions request a field only when it is always
required or an inspectable route condition makes it required.

Citizenship, household composition, qualifications, offers and salary are consequential. Exact
birth date is exception-only. Names, passport numbers, employer identity, account IDs and uploaded
documents are not part of Phase 7 profile contracts.

## Same-device retention

Persistent browser storage is off by default. A later UI may offer it only when the user explicitly
chooses it. The consent marker records the policy version and consent time; stored data expires
within 30 days and is cleared when profile or policy versions become incompatible.

Exact birth date may never enter same-device retention. A user can clear all local profile and
scenario data without an account.

## Export and redaction

Export is user-initiated. The default export omits exact birth date and generalizes sensitive age,
household and citizenship details according to the field registry. A future full-fidelity export
would require a separate explicit action and warning. Imports preserve provenance and never imply
verification.

## Server and future accounts

Phase 7 server persistence is fixed to `NONE`. A future saved-profile phase requires separate
privacy, security, ownership, revision, deletion and migration decisions. Even then, evaluation
must consume an explicit immutable context snapshot, not silently read a mutable account record.
