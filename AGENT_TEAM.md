# Begborim AI: Astra specialist team

This change adds 100 distinct specialist instruction profiles to the existing Python studio. All specialist and synthesis calls explicitly request `gpt-6-astra`. These are text/code planning agents; no browsing, shell execution, account actions or media generation tools are attached. They are not copies of ChatGPT Work or separate subscriptions.

## Behavior

The owner connects with the existing bearer token, searches/selects 1–100 specialists, enters a task and confirms the paid request. Specialists run sequentially; for multiple specialists, an additional lead call combines bounded excerpts of their results. Each result and reported token usage is saved in SQLite. Partial results remain visible. Cancellation stops subsequent calls; a call already in flight may still be charged.

Job IDs are idempotent. Same-ID different-payload submissions return 409. Only one agent run is active at a time. Startup marks interrupted runs UNKNOWN without retrying. HTTP errors, uncertain responses and timeouts are never retried automatically. This is deliberately not a crash-resuming job queue; use one server process/replica with durable SQLite storage.

## Server controls

- Existing `OPENAI_API_KEY` must have access and funded API usage. Never place it in browser code or Git.
- `BEGBORIM_AGENTS_ENABLED` defaults off. `1` allows paid submissions.
- `AGENT_DAILY_CALL_LIMIT` defaults to 20 reserved calls per UTC day (maximum 1000). A 100-specialist job requires 101 calls including synthesis, so the default cap rejects it.
- `AGENT_MAX_OUTPUT_TOKENS` defaults to 2048 and includes model reasoning tokens; some answers may be incomplete. Supported range 256–8192.
- Entire call count is reserved atomically before starting. Reservations are conservatively retained after failures/cancellation. This is a request limit, **not a dollar spending cap**. Input token sizes and rates also affect cost.
- Agent records and budgets use the existing `BEGBORIM_DB`. The deployment must mount persistent storage there.

## Deployment review — not deployed

The live `begborim-server` Railway service, inspected October 7, 2026, has a custom start command that executes code from `BEGBORIM_BOOT_080_Z` and also patches UI files. It does not simply launch this repository's `server.py`. The existing production service has an OPENAI_API_KEY variable, but its value, validity, balance and Astra access were not verified. It currently has no persistent volume mounted.

Do not replace the custom command with `python server.py` as a shortcut: that would discard production-specific media behavior. Before enabling in production, reconcile the effective running source and frontend with these routes and hooks, preserve existing media adapters, and establish durable SQLite storage. Verify authenticated agent routes and existing media flows in a preview deployment first. No production config, paid request, deployment, APK or main-branch change is included in this draft.

## Verification

`python -m unittest test_agents.AgentTest test_agents.AgentHTTPTest -q`

21 tests cover all 100 profiles, authentication, new HTTP routes, real HTTP lifecycle with a mocked provider, exact Astra request payload, sequential synthesis, idempotency, conflicting IDs, atomic budget reservation, cancellation, restart handling, no automatic timeout retries and the existing media gateway regressions. Provider responses are mocked: these tests do not prove live Astra access.

API references consulted:
- https://developers.openai.com/api/docs/models/gpt-6-astra
- https://developers.openai.com/api/reference/python/resources/responses/methods/create

JavaScript syntax checks passed for both scripts. Mobile browser verification was attempted but could not run: no Chromium binary was installed and the browser download failed. Visual layout and interactive browser behavior still need preview verification.
