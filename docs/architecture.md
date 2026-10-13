# Architecture

## Data flow

| Step | What happens |
|---|---|
| Inbound | WhatsApp messages arrive through an official WhatsApp Business API provider at a webhook sidecar. Telegram messages arrive through a bot and a plugin bridge. |
| Single writer | The sidecar, the bridge, the owner dashboard and every agent send their writes to one writer service. Nothing else writes to the database. |
| Storage | The writer saves to SQLite in WAL mode, the source of truth. |
| Mirror | An outbox feeds a mirror that updates a Google Sheet for the owner. A sync job pulls owner edits back from the Sheet every 15 minutes. |
| Knowledge | A project history engine rebuilds a timeline, metrics and a knowledge graph on every commit, in plain code at 0 AI tokens. |

## The webhook sidecar

- **HMAC signature check that fails closed.** A request that cannot be verified is rejected, never guessed.
- **Type filter and de-duplication**, including messages split into several parts.
- **Guarded owner send**: outbound messages go through a guarded path.
- **Human takeover**: when staff reply from the business number, the provider's echo event is detected and agents step back for 24 hours.
- **History backfill**, so the record can be rebuilt from the provider's history.

## The single-writer spine

A spreadsheet is a view, not a database.

| Layer | Protection |
|---|---|
| 1 · Bounded lock | A writer that cannot get the lock in time does not block forever |
| 2 · Journal | Writes are journalled |
| 3 · Spool and replay | If the writer is unavailable, writes go to a spool that is replayed every minute |
| Snapshots | Hourly database snapshots |
| Formula-safe mirror | Values that a spreadsheet would treat as formulas are written safely, which fixed `#ERROR!` cells |

A **writer guardian** runs every 5 minutes: database integrity check (light, with a full check once a day), lead count, size, WAL size, lock holder and free disk.

The later phase that moved site visits, assignments and property interest onto the spine was checked independently: 5 of 5 checks passed.

## Resilience

- **Google Sheets access** uses a direct service account as primary with a second provider as fallback, a circuit breaker, failover, a serve-stale cache and a disk snapshot. Failover has been proven.
- **Outage recovery** re-reads WhatsApp history in both directions so messages missed during downtime are still captured. It runs in idle windows, at most 9 contacts a day, with one combined extraction per contact.
- **Idempotent importers** keyed by message id. A gap check found about 20 % of inbound messages missing at one point; a gap importer was built to close it.
- **Backups**: hourly snapshots, an AES-256 encrypted daily backup and a copy on client-owned cloud storage. A restore drill has passed.
- **Watchdog** every 5 minutes, with last-known-good fingerprints and automatic rollback for the sidecar.

## Where it runs

| Piece | Detail |
|---|---|
| Client node | One Apple-silicon laptop owned by the client runs the 15 agents, the gateway, the dashboard, the sidecar and the media vault as a 24/7 server, with 22 background services |
| Network | A private Tailscale network; only the webhook and a health endpoint are public |
| Trust | One-way: the architect's control plane can observe the client node, but the client node cannot reach upward |
| Data sovereignty | **No client data is pulled to the architect's machines.** Backups stay on client-owned storage |
| Access | Every dashboard route needs login (unauthenticated API calls get 401), with rate limits, an audit log and "log out everywhere" |
