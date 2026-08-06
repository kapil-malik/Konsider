# Konsider Phase 7H — Guest-First Profile and Feasibility UI

## Dependency

Proceed only after Phase 7G is accepted and generated client types are current.

## Role

Work as the lead product UX, React/TypeScript, accessibility and privacy-conscious browser-state engineer for Konsider.

## Objective

Add a guest-first “Your situation” experience that lets users:

- enter only relevant profile/scenario facts;
- select or confirm TFCs;
- see missing-input requests;
- view feasibility results separately from affinity and OFCs;
- retain context for the session;
- optionally remember it on the device;
- clear/export/import it;
- use Konsider without login.

Do not implement authentication or server persistence.

## Main-page information architecture

Keep the existing ranking usable without profile context.

Add compact summaries such as:

- **Priorities** — ordering weights;
- **Opportunity** — selected OFCs;
- **Your situation** — applicant/household/scenario summary;
- **Feasibility checks** — selected TFCs and status.

Do not display a permanent 20-field form beside ranking controls.

Use a guided drawer/modal/page flow.

## Progressive disclosure

The UI should:

1. ask the exploration purpose;
2. show relevant available TFCs;
3. ask only fields required by those TFCs;
4. distinguish required, optional and unknown;
5. show why a field is requested;
6. allow “I don’t know” where supported;
7. show an assumptions summary before or with results;
8. request additional data when a country/TFC needs it.

Do not infer omitted answers.

## Profile/scenario separation

Present stable facts separately from scenario assumptions.

Examples:

### Applicant

- citizenship;
- occupation;
- qualifications;
- experience;
- languages.

### Household

- accompanying partner;
- dependants;
- child ages where relevant.

### Scenario

- work/study/family purpose;
- job offer and salary;
- intended course;
- target year;
- cities;
- housing/budget assumptions.

Allow the same applicant profile to be reused with different local scenarios in browser state.

## TFC selection

Use API/catalog-driven labels and grouping.

The UI may recommend checks based on purpose, but must clearly show which checks will run.

Do not silently activate consequential checks.

Support:

- select/unselect;
- required-input indicator;
- source/effective-date indicator;
- assessment-only versus explicit filter capability.

## Results presentation

Keep separate visual concepts:

- affinity score and base rank;
- OFC evidence;
- TFC feasibility;
- locality compatibility.

Examples:

- “Strong technology ecosystem”
- “Supported skilled-work route match found”
- “More salary information required”
- “No supported route matched under the currently modelled routes”
- “Destination evidence unavailable”
- “Estimated employee tax and contribution range”

Never show:

- “You can immigrate”
- “Visa guaranteed”
- “You cannot move”
- “No jobs”
- “Admission likely”

## Country detail and comparison

Show:

- selected TFCs;
- match/condition details;
- missing inputs;
- assumptions;
- routes evaluated;
- source/effective date;
- limitations;
- metric components;
- base rank and optional filtered rank;
- relation to OFCs where useful.

Comparison must use one consistent effective profile/scenario snapshot.

## Explicit feasibility filtering

Default to assessment-only.

Where the API permits route-match filtering, provide an explicit control such as:

> Show only destinations with a supported route match

Explain:

- base affinity is unchanged;
- countries may be hidden due to the selected feasibility mode;
- input-required/unsupported handling;
- how to restore the base list.

Do not apply hidden filtering.

## Browser state and retention

### Default

- memory for current page/app session;
- session retention may be used where approved;
- no automatic persistent local storage.

### Remember on this device

Require explicit opt-in.

Show:

- what is stored;
- that it is stored on this device/browser;
- expiration/version behavior;
- clear action;
- shared-device caution.

Do not claim browser storage is equivalent to secure account storage.

### Clear/export/import

Provide:

- clear current situation;
- clear remembered data;
- export as versioned JSON;
- import with validation and preview.

Do not include assessment results in export unless explicitly designed.

Never include profile data in URLs.

## Multiple scenarios

Support a bounded local experience if practical:

- one active applicant/household context;
- a small number of named local scenarios;
- duplicate scenario;
- compare scenario summaries.

Do not build a full persistence platform.

## Accessibility

Ensure:

- keyboard flow;
- proper labels/descriptions;
- error association;
- screen-reader announcements;
- no color-only status;
- mobile responsiveness;
- focus management;
- accessible modal/drawer;
- understandable reason text.

## Analytics and privacy

Do not send raw field values to analytics.

If event analytics exist, allow only coarse events such as:

- profile flow opened;
- TFC selected;
- assessment requested;
- local retention enabled.

Review and document.

## UI tests

At minimum:

- ranking works without profile;
- open/cancel profile flow;
- progressive field requirements;
- unknown value behavior;
- selected TFC summary;
- input-required result;
- route result;
- metric result;
- OFC + TFC display;
- country detail;
- comparison;
- explicit filter/undo;
- session restoration;
- opt-in local retention;
- clear;
- export/import;
- schema-version mismatch;
- mobile;
- keyboard/screen reader semantics;
- API error;
- unavailable candidate/release.

No UI-side eligibility logic.

## Documentation

Update:

- UI guide;
- privacy/retention help;
- screenshots/test plan if repository convention supports them;
- user-facing limitations;
- developer state ownership.

## Explicit non-goals

Do not:

- add login;
- add account settings;
- add server persistence;
- add chat;
- add hidden profile inference;
- add UI-side TFC rules;
- change ranking.

## Commit

Use a focused commit such as:

`feat: add guest profile and TFC experience`

## Stop condition

Stop when the guest flow, local/session retention, details, comparison, accessibility and tests pass against the staged API.

Report:

- UX flow;
- retention behavior;
- privacy behavior;
- test results;
- screenshots/evidence where applicable;
- files changed;
- commit SHA;
- blockers before Phase 7I.
