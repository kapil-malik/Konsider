# React Web Application

## Responsibility

The website provides the complete user experience for selecting or describing a profile, editing
weights, inspecting rankings, reviewing evidence, and conversing with Konsider. It is a client of
the live engine and has no direct access to storage, public data sources, or LLM providers.

## Product Surfaces

- Profile template selection and editable weight controls.
- Normalized-weight summary and reset/undo behavior.
- Ranked country table and top recommendations.
- Per-country score contribution and tradeoff breakdown.
- Evidence drawer or detail view with source, date, confidence, and caveats.
- Chat panel that can explain rankings, retrieve evidence, and propose or apply profile changes.
- Visible dataset freshness and approximation warnings.
- Loading, empty, partial-data, disconnected, and recoverable error states.

## API Access

The web application calls only the live engine:

| UI need | API interaction |
| --- | --- |
| Build controls | `GET /api/v1/catalog` |
| Calculate or refresh ranking | `POST /api/v1/rankings` |
| Inspect supporting information | `GET /api/v1/countries/{id}/evidence` |
| Start chat | `POST /api/v1/chat/sessions` |
| Send message and receive updates | SSE response from the session message endpoint |

The API base URL is supplied through Vite environment configuration. Only variables intended for
the browser use the `VITE_` prefix; secrets must never be placed there.

## State Ownership

- The API catalog is authoritative for countries, metrics, labels, and profile templates.
- The server is authoritative for persisted profile and conversation revisions.
- The browser owns temporary form edits until ranking or profile update submission.
- Ranking responses replace client calculations; the website does not normalize or score locally.
- Chat text and typed events are stored separately. Typed events update profile and ranking state.
- URLs may identify selected countries or views, but must not expose private conversation content.

## Technology

- React with Vite and TypeScript.
- A small API client generated or typed from FastAPI OpenAPI.
- Native fetch or a focused query library for request caching and cancellation.
- An SSE-capable client for streamed chat.
- Component and accessibility tests plus end-to-end coverage for the principal ranking flow.
- AWS Amplify Hosting with Git-based builds and SPA route fallback.

The first UI should remain an operational decision tool: compact, responsive, accessible, and
optimized for comparison. It does not need server-side rendering because ranking and chat content
are personalized application data rather than search-indexed marketing pages.

## Amplify Build Contract

The deployable application lives in `web` and builds to `web/dist`. A typical monorepo Amplify
configuration uses `web` as the application root, installs from the committed lockfile, runs tests
and `npm run build`, and publishes `dist`.

Runtime configuration includes:

```text
VITE_API_BASE_URL=https://api.example.com
```

Authentication configuration may be added when Cognito is introduced. The browser receives public
client configuration only, never source-system or LLM credentials.

## Chat Interaction Contract

The client renders `message.delta` events as assistant text and handles state events independently:

- `profile.proposed` displays the intended changes and confirmation controls.
- `profile.updated` replaces sliders using the returned profile revision and enables undo.
- `ranking.updated` replaces the result set and displays its dataset/scoring versions.
- `citation` links rendered claims to evidence detail.
- `error` preserves recoverable input and offers retry when appropriate.

This prevents conversational wording from becoming an application protocol.

## Testing Expectations

- Unit tests for formatting and state reducers.
- Component tests for sliders, ranking table, evidence details, and typed chat events.
- Contract tests using API fixtures generated from OpenAPI examples.
- End-to-end tests for profile selection, weight editing, ranking, evidence inspection, and one chat
  weight-change flow.
- Responsive and accessibility checks at supported desktop and mobile sizes.
