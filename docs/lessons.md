# Engineering lessons

129 bugs were closed, each with a written root cause, fix and lesson. 75 lessons were recorded, and 61 were promoted into a reusable delivery playbook so the next client starts where this one ended. A selection:

## Integration and webhooks
- Webhooks are forward-only; history comes from exports.
- Capture the raw request body before parsing, or the HMAC check cannot work.
- Filter event types at the sidecar.
- List the provider's real webhook event types from live logs, not from the documentation. One unhandled type had silently dropped 997 echo events.
- Detect human takeover by exclusion, and fail open to "a human is handling this".
- **Signature checks must fail closed.**

## Go-live discipline
- "Activated" is not "working": gate go-live on one real round trip.
- Stub adapters pass every probe, so mark them and never deploy without a real message.
- A passing installer cannot prove the screen rendered; add a browser check.
- The dashboard and its runbook ship as one unit.

## Models and cost
- **Never route single-purpose model calls through a full agent.**
- **Deterministic checks first, a model only on change.**
- Free-tier models must never run security audits; one hallucinated a threat.
- Model names change; re-verify them.
- A dead fallback chain turns rate limits into outages, so probe every rung.
- **Privacy routing is a hard rule, not a price choice.**

## Data integrity
- A spreadsheet is a view, not a database: one writer, provenance and a change log.
- De-duplicate by phone number and append interactions.
- Silent saves lose data; confirm and offer undo.
- A single writer needs a bounded lock.
- Every fallback needs a non-lossy fallback (spool and replay).
- **Make importers idempotent by message id.**

## Security
- Never embed an owner token in a served page.
- Whitelist static files; never serve the project root.
- Private views are gated on the server, with non-enumerating responses and an access log.
- Drift tooling must redact before it saves anything.

## Process
- Grep the literal error before accepting a diagnosis.
- A dashboard that shows invented numbers is worse than one that says "not wired yet".
- After a blank-dashboard incident, an export guard now blocks any broken bundle before deploy.
