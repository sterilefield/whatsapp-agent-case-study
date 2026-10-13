# 15 agents on three model tiers

Expensive models only where judgement is needed. Lighter, cheaper models everywhere else, and local embeddings for property matching.

| Role | Tier | Heartbeat |
|---|---|---|
| Lead intake, de-duplication and owner alerts on WhatsApp and Telegram | Top | Every 2 h |
| Lead routing and assignment | Mid | Every 4 h |
| Semantic property matching (local embeddings) | Mid | Every 6 h |
| Risk scans: forgotten lead, hot lead with no response, visit no-show risk, inactive executive, stuck in stage, negative trend | Mid | Every 24 h |
| Multilingual help and a deterministic daily digest for the owner | Mid | Scheduled only |
| Builder-inventory extraction and follow-up scan | Mid | Scheduled only |
| Listing copy | Mid | Scheduled only |
| Content guidance | Mid | Scheduled only |
| Knowledge-base curator (at most every 6 h) | Mid | Scheduled only |
| Orchestrator and housekeeping | Mid | Off |
| Structured extraction (no tools, no memory) | Light | Off |
| Read-only dashboard analyst (capped at 20 answers a day) | Light | Off |
| Market watch | Light | Off |
| Channel scout | Light | Off |
| Cold-lead reactivation (built, deliberately held off) | Light | Off |

## How the cost came down

| Change | Effect |
|---|---|
| Heartbeat intervals set per agent; 11 agents moved to scheduled runs only; a 0-token check wakes a model only when something changed | Heartbeat tokens **12.0 M → 1.0 M a day (−91 %)** |
| Extraction moved out of the full intake agent into a tool-less, memory-less extractor, with rule-based parsing first | **~38 k → ~4 k tokens per message** (1,177 turns, 0 errors) |
| Privacy-aware fallback routing | Customer-data agents never fall back to providers that may train on prompts |
| Cache-friendly prompts | **76–79 %** of tokens served from cache |
| Monitoring, digests and project history built as plain code | 0 AI tokens for monitoring |

Result: **₹0 marginal API cost per lead** (≈ ₹13 at list price).

The full playbook, with all 18 methods, is in [llm-token-economics](https://github.com/sterilefield/llm-token-economics).
