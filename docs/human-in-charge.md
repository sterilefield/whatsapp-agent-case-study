# A human stays in charge

## Engagement policy as a file

One versioned policy file decides how the agents engage. The plugin reads it at runtime, so **behaviour changes by editing the policy and its changelog, not the code.**

| Area | Rule |
|---|---|
| Objective and privacy | Stated objective; data minimisation in line with India's DPDP Act |
| Replies | Answer first; ask at most one or two questions; mirror the customer's Telugu written in English letters; **never state prices, legal status or RERA claims** |
| Follow-up cadence | Hot leads: day 0, 1, 3 and 7, then weekly (at most twice a week). Warm leads: day 0, 3 and 10, then every two weeks. Cool automatically after 4 ignored messages. Cold leads: monthly, value-only content |
| Quiet hours | 21:00–09:00 |
| Festival calendar | A verified local festival calendar with cited sources |
| Human-in-the-loop tiers | Which messages may be sent automatically and which are draft-only for a person |
| Targets | Reply rate ≥ 40 %, opt-out < 2 %, qualified ≥ 85 %, hot lead to a human in < 24 h |

## Approvals

- **Template follow-ups**: 284 WhatsApp template follow-ups went out in 4 weeks, **each approved by the owner** in the dashboard.
- **9 Meta-approved templates**, each mapped to one job: welcoming a new lead, following up a warm lead, recommending a property, site-visit reminders for the customer and the executive, assignment notices, a daily health report, returning customers and case follow-ups.
- **A cold-lead reactivation agent was built and deliberately kept off.**

## Takeover and acknowledgement

- **Human takeover**: when staff reply, the agents step back for 24 hours.
- **Pending-acknowledgement loop**: a new lead alerts the owner. If nobody acknowledges it, the customer confirmation goes out at 30 minutes. Reminders back off at 30 minutes, 1 hour, 2 hours, then 4 hours.

## Owner notes with undo

The owner can create or update leads with a quick note on Telegram.

- A note is applied only when it is unambiguous: one phone number plus a field.
- Ambiguous notes, and sensitive changes such as marking a lead lost, do-not-contact, opted out or deleted, ask for confirmation first.
- **Every write returns an undo handle.**

## Change discipline

Every change to the platform follows the same order: backup → rollback script → change → live check → log → commit.

## Ownership

An IP and data-ownership framework was drafted for the pilot: the architect owns the code, architecture, agents, prompts and configuration; the client owns its raw business data and approves outbound messages to its own customers.
