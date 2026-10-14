# WhatsApp agent case study

**A 15-agent WhatsApp and Telegram operations platform for a Hyderabad real-estate brokerage: how it was built to recover missed enquiries, keep a human in charge, and run AI at almost no marginal cost.**

Live since June 2026. Designed, built and operated by one architect directing AI coding agents. The client is anonymised; no customer data, code, prompts or configuration are published here. Figures are shared with the client's permission.

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/sterilefield/whatsapp-agent-case-study/badge)](https://scorecard.dev/viewer/?uri=github.com/sterilefield/whatsapp-agent-case-study)

## Results

| Measure | Value |
|---|---|
| Leads handled | 460+ |
| Customer interactions logged | 8,688 |
| WhatsApp template follow-ups | 284 in 4 weeks, **each approved by the owner** in the dashboard |
| Owner time saved | 7+ hours a week (client-confirmed) |
| Heartbeat tokens | 12.0 M → 1.0 M a day (−91 %) |
| Extraction cost per WhatsApp message | ~38 k → ~4 k tokens (1,177 turns, 0 errors) |
| Marginal API cost per lead | ₹0 (≈ ₹13 at list price) |
| Tokens served from cache | 76–79 % |
| Bugs closed | 129, each with root cause, fix and lesson |

The platform is presented as **delivered and operating**. It is not claimed to have driven sales.

## The design in one picture

```mermaid
flowchart LR
    WA["WhatsApp<br/>Business API"] --> SC["Webhook sidecar<br/>HMAC check · de-dup"]
    TG["Telegram bot"] --> PB["Plugin bridge"]
    SC --> W["Single writer"]
    PB --> W
    DB2["Owner dashboard"] --> W
    AG["15 agents"] --> W
    W --> DB[("SQLite (WAL)<br/>source of truth")]
    DB --> M["Outbox → mirror"] --> GS["Google Sheet<br/>owner's view"]
    W -. "lock timeout" .-> SP["Spool<br/>replayed every minute"]
    SP --> W
```

Three ideas carry the system:

1. **One writer, one source of truth.** Every write from every channel, agent and screen goes through a single writer into SQLite. The spreadsheet the owner likes is a mirror, never the database. See [docs/architecture.md](docs/architecture.md).
2. **A human stays in charge.** Behaviour lives in a policy file, not in code: reply rules, follow-up cadence, quiet hours and which messages may go out without a person. Template follow-ups go out only after the owner approves them. See [docs/human-in-charge.md](docs/human-in-charge.md).
3. **AI only where it earns its cost.** Rules first, a small single-purpose model for extraction, a top-tier model only for live intake, and plain code for monitoring. See [docs/agents-and-cost.md](docs/agents-and-cost.md).

## Read more

| Document | What it covers |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Data flow, single-writer spine, safety net, recovery, client-node trust |
| [docs/human-in-charge.md](docs/human-in-charge.md) | Engagement policy, approvals, takeover, undo |
| [docs/agents-and-cost.md](docs/agents-and-cost.md) | 15 agents on 3 model tiers, and how token spend was cut |
| [docs/lessons.md](docs/lessons.md) | Engineering lessons from 129 bugs, grouped |
| [docs/timeline.md](docs/timeline.md) | From first commit to a live 15-agent platform |

## Related

- [llm-token-economics](https://github.com/sterilefield/llm-token-economics): the 18 cost methods behind the −91 %.
- [agent-governance-kit](https://github.com/sterilefield/agent-governance-kit): autonomy levels, risk classes and approval tiers.
- [empire-os-reference-architecture](https://github.com/sterilefield/empire-os-reference-architecture): the platform these agents run on.

## Author

**Dr. Ravi Teja Thiriveedhi**: clinician turned AI systems architect, with 20 years of clinical practice and hospital operations. [GitHub](https://github.com/Raviteja2k2k) · [LinkedIn](https://www.linkedin.com/in/dr-ravi-teja-thiriveedhi/)

## Licence

Documentation in this repository is licensed under [CC BY-NC-ND 4.0](LICENSE). Share it with credit; no commercial use and no derivatives.
