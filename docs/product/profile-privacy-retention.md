# Profile privacy and retention

Status: Phase 7J release privacy verification passed

## Defaults

Phase 7 is guest-first. Profile values exist in tab-scoped `sessionStorage` and in the stateless
evaluation request only. The server does not persist them. Closing the tab clears the default
context. The ranking remains usable without any profile or TFC selection.

Profile values are prohibited in:

- URLs and query strings;
- application or access logs;
- analytics events and session-replay tools; and
- immutable public release artifacts.

Operational telemetry may record schema versions, selected TFC IDs and aggregate outcome statuses,
but not field values, unknown-field lists or snapshot contents.

Phase 7G accepts profile-bearing data only in POST bodies. API request bodies are not logged, error
payloads omit submitted values, and all API v2 POST responses carry `Cache-Control: private,
no-store`, `Pragma: no-cache` and `Expires: 0`. Runtime assessment performs no profile writes. The
returned snapshot is metadata only: it contains IDs, policy/source versions, an opaque context
hash, evaluation date and base-ranking reference. It does not contain the effective context or
country-outcome copy held by the domain snapshot during the request.

## Sensitivity and minimization

Fields are classified `LOW`, `MODERATE_PERSONAL`, `MODERATE_CONSEQUENTIAL`, `HIGH_PERSONAL`,
`HIGH_FINANCIAL` or `HIGH_CONSEQUENTIAL`. TFC definitions request a field only when it is always
required or an inspectable route condition makes it required.

Citizenship, household composition, qualifications, offers and salary are consequential. Exact
birth date is exception-only. Names, passport numbers, employer identity, account IDs and uploaded
documents are not part of Phase 7 profile contracts.

## Same-device retention

Persistent browser storage is off by default. The **Remember my situation on this device** control
is explicit and unchecked initially. When selected, the versioned applicant, household and bounded
scenario document is copied to `localStorage` with a 30-day expiry. Invalid, expired or incompatible
documents are deleted on load and the guest is notified. Turning retention off on a later save or
using **Clear remembered data** removes the durable copy; the current tab copy remains until it is
separately cleared.

Exact birth date may never enter same-device retention. A user can clear all local profile and
scenario data without an account.

## Export and redaction

Export is user-initiated and uses `konsider-situation-1.0`. The default export contains no
assessment results, source URLs or snapshot hash. It omits citizenship and resets household/age
details to explicit unknown values. Exact birth date is not collected. A future full-fidelity
export would require a separate explicit action and warning. Imports validate the schema, bounded
scenario count, required structure, enum values and active-scenario identity, then show a preview
before replacing the draft. Imports never imply verification.

No profile values are placed in URLs or analytics. The browser sends them only in explicit API v2
POST bodies after **Save and assess**. Opening, cancelling or editing the flow does not request an
assessment.

## Server and future accounts

Phase 7 server persistence is fixed to `NONE`. A future saved-profile phase requires separate
privacy, security, ownership, revision, deletion and migration decisions. Even then, evaluation
must consume an explicit immutable context snapshot, not silently read a mutable account record.

Phase 7J re-verified that representative submitted values do not appear in response bodies, URLs
or captured application logs, that profile-bearing POST responses retain private/no-store headers,
and that immutable release artifacts contain no profile fields or values. Release activation did
not add authentication, server persistence or analytics.
