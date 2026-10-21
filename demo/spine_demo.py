#!/usr/bin/env python3
"""spine_demo: a small, runnable model of the case study's design ideas, on invented leads.

    python3 demo/spine_demo.py            # run the scripted day and print the event log
    python3 demo/spine_demo.py --db x.db  # keep the SQLite file to inspect it

It shows, in about 250 lines of standard-library Python:
  * one writer: every producer (webhook, agents, owner dashboard) sends writes to a single writer;
  * idempotent inbound messages keyed by message id (a duplicate webhook delivery is ignored);
  * a spool: when the writer cannot get the lock in time, writes are spooled and replayed;
  * owner approval: agent follow-ups wait in a queue until the owner approves or rejects them;
  * quiet hours 21:00-09:00: approved messages are held until morning;
  * human takeover: when staff reply, agents step back for 24 hours;
  * owner notes with an undo handle.

This is a teaching model written for this repository. It is not the production code, it sends
nothing, and every lead, message and time is synthetic.
"""
from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta

QUIET_START, QUIET_END = 21, 9
TAKEOVER = timedelta(hours=24)

SCHEMA = """
CREATE TABLE leads(id TEXT PRIMARY KEY, name TEXT, stage TEXT, takeover_until TEXT);
CREATE TABLE messages(msg_id TEXT PRIMARY KEY, lead_id TEXT, direction TEXT, body TEXT, ts TEXT);
CREATE TABLE outbox(id INTEGER PRIMARY KEY, lead_id TEXT, template TEXT, status TEXT, proposed_by TEXT, ts TEXT);
CREATE TABLE journal(seq INTEGER PRIMARY KEY, ts TEXT, source TEXT, op TEXT, detail TEXT);
CREATE TABLE undo(handle TEXT PRIMARY KEY, lead_id TEXT, field TEXT, old TEXT);
"""


def in_quiet_hours(t: datetime) -> bool:
    return t.hour >= QUIET_START or t.hour < QUIET_END


def next_morning(t: datetime) -> datetime:
    day = t if t.hour < QUIET_END else t + timedelta(days=1)
    return day.replace(hour=QUIET_END, minute=0, second=0, microsecond=0)


@dataclass
class Write:
    source: str
    op: str
    args: dict


@dataclass
class Writer:
    """The only component that writes to the database."""

    db: sqlite3.Connection
    lock_available: bool = True
    spool: list[Write] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    now: datetime = datetime(2026, 1, 5, 10, 0)
    undo_seq: int = 0

    def say(self, line: str) -> None:
        self.log.append(f"{self.now:%a %H:%M}  {line}")

    def submit(self, w: Write) -> None:
        if not self.lock_available:  # bounded lock: give up quickly, never block forever
            self.spool.append(w)
            self.say(f"SPOOL   writer busy, {w.source} {w.op} spooled ({len(self.spool)} waiting)")
            return
        self._apply(w)

    def replay(self) -> None:
        waiting, self.spool = self.spool, []
        for w in waiting:
            self._apply(w)
        if waiting:
            self.say(f"replay  {len(waiting)} spooled write(s) applied")

    def _journal(self, w: Write, detail: str) -> None:
        self.db.execute("INSERT INTO journal(ts, source, op, detail) VALUES (?,?,?,?)", (self.now.isoformat(), w.source, w.op, detail))

    def _apply(self, w: Write) -> None:
        a, ts = w.args, self.now.isoformat()
        with self.db:
            if w.op == "new_lead":
                self.db.execute("INSERT INTO leads VALUES (?,?,?,NULL)", (a["lead"], a["name"], "new"))
                self.say(f"OK      new lead {a['lead']} ({a['name']}) from {w.source}")
            elif w.op == "inbound":
                cur = self.db.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?,?)", (a["msg_id"], a["lead"], "in", a["body"], ts))
                if cur.rowcount == 0:
                    self.say(f"OK      duplicate delivery of {a['msg_id']} ignored (idempotent by message id)")
                    return
                self.say(f"OK      inbound {a['msg_id']} from {a['lead']}: \"{a['body']}\"")
            elif w.op == "staff_reply":
                until = (self.now + TAKEOVER).isoformat()
                self.db.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?,?)", (a["msg_id"], a["lead"], "out-staff", a["body"], ts))
                self.db.execute("UPDATE leads SET takeover_until=? WHERE id=?", (until, a["lead"]))
                self.say(f"HOLD    staff replied to {a['lead']}: agents step back until {self.now + TAKEOVER:%a %H:%M}")
            elif w.op == "propose_followup":
                row = self.db.execute("SELECT takeover_until FROM leads WHERE id=?", (a["lead"],)).fetchone()
                if row and row[0] and row[0] > ts:
                    self.say(f"HOLD    {w.source} follow-up for {a['lead']} dropped: human takeover active")
                    return
                self.db.execute("INSERT INTO outbox(lead_id, template, status, proposed_by, ts) VALUES (?,?,?,?,?)",
                                (a["lead"], a["template"], "pending_approval", w.source, ts))
                self.say(f"WAIT    {w.source} proposed template '{a['template']}' for {a['lead']}: waiting for owner approval")
            elif w.op == "owner_decides":
                oid = self.db.execute("SELECT id FROM outbox WHERE lead_id=? AND status='pending_approval' ORDER BY id LIMIT 1", (a["lead"],)).fetchone()
                if not oid:
                    return
                if a["decision"] == "reject":
                    self.db.execute("UPDATE outbox SET status='rejected' WHERE id=?", oid)
                    self.say(f"REJECTED owner rejected the follow-up for {a['lead']}")
                elif in_quiet_hours(self.now):
                    self.db.execute("UPDATE outbox SET status='held_quiet_hours' WHERE id=?", oid)
                    self.say(f"HOLD    owner approved {a['lead']}, but it is quiet hours: held until {next_morning(self.now):%a %H:%M}")
                else:
                    self.db.execute("UPDATE outbox SET status='sent' WHERE id=?", oid)
                    self.say(f"SENT    owner approved; follow-up to {a['lead']} sent (simulated)")
            elif w.op == "release_held":
                n = self.db.execute("UPDATE outbox SET status='sent' WHERE status='held_quiet_hours'").rowcount
                self.say(f"SENT    quiet hours over: {n} held message(s) sent (simulated)")
            elif w.op == "owner_note":
                select, update = FIELD_SQL[a["field"]]
                old = self.db.execute(select, (a["lead"],)).fetchone()[0]
                self.undo_seq += 1
                handle = f"U{self.undo_seq:03d}"
                self.db.execute(update, (a["value"], a["lead"]))
                self.db.execute("INSERT INTO undo VALUES (?,?,?,?)", (handle, a["lead"], a["field"], old))
                self.say(f"OK      owner note: {a['lead']} {a['field']} {old} -> {a['value']} (undo handle {handle})")
            elif w.op == "undo":
                lead, fld, old = self.db.execute("SELECT lead_id, field, old FROM undo WHERE handle=?", (a["handle"],)).fetchone()
                self.db.execute(FIELD_SQL[fld][1], (old, lead))
                self.db.execute("DELETE FROM undo WHERE handle=?", (a["handle"],))
                self.say(f"OK      undo {a['handle']}: {lead} {fld} back to {old}")
            self._journal(w, str(a))


# Owner notes may change only these fields; each has fixed SQL (no string-built queries).
FIELD_SQL = {"stage": ("SELECT stage FROM leads WHERE id=?", "UPDATE leads SET stage=? WHERE id=?")}
ALLOWED_FIELDS = set(FIELD_SQL)


def owner_note(text: str) -> Write | None:
    """Apply a note only when it is unambiguous: one lead id plus one known field. Anything else asks first."""
    parts = text.split()
    if len(parts) == 3 and parts[0].startswith("lead-") and parts[1] in ALLOWED_FIELDS and parts[2] not in ("lost", "do-not-contact"):
        return Write("owner-telegram", "owner_note", {"lead": parts[0], "field": parts[1], "value": parts[2]})
    return None


def scripted_day(db_path: str | None = None) -> Writer:
    db = sqlite3.connect(db_path or ":memory:")
    if db_path:
        db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    w = Writer(db)

    def at(h: int, m: int = 0, day: int = 0) -> None:
        w.now = datetime(2026, 1, 5 + day, h, m)

    at(10, 0)
    w.submit(Write("webhook", "new_lead", {"lead": "lead-001", "name": "Synthetic lead A"}))
    w.submit(Write("webhook", "inbound", {"lead": "lead-001", "msg_id": "m-1", "body": "Is the 2BHK still available?"}))
    w.submit(Write("webhook", "inbound", {"lead": "lead-001", "msg_id": "m-1", "body": "Is the 2BHK still available?"}))
    at(10, 5)
    w.submit(Write("webhook", "new_lead", {"lead": "lead-002", "name": "Synthetic lead B"}))
    w.submit(Write("follow-up-agent", "propose_followup", {"lead": "lead-001", "template": "warm_follow_up"}))
    at(10, 20)
    w.submit(Write("owner-dashboard", "owner_decides", {"lead": "lead-001", "decision": "approve"}))
    at(11, 0)
    w.submit(Write("staff-phone", "staff_reply", {"lead": "lead-002", "msg_id": "m-2", "body": "Calling you now"}))
    w.submit(Write("follow-up-agent", "propose_followup", {"lead": "lead-002", "template": "warm_follow_up"}))
    at(14, 0)
    w.lock_available = False
    w.submit(Write("webhook", "inbound", {"lead": "lead-001", "msg_id": "m-3", "body": "Can I visit on Saturday?"}))
    w.submit(Write("scheduler-agent", "propose_followup", {"lead": "lead-001", "template": "site_visit_reminder"}))
    at(14, 1)
    w.lock_available = True
    w.replay()
    note = owner_note("lead-001 stage site-visit")
    if note:
        w.submit(note)
    if owner_note("mark lead-002 lost") is None:
        w.say("WAIT    owner note 'mark lead-002 lost' is sensitive or ambiguous: asked the owner to confirm")
    at(22, 30)
    w.submit(Write("owner-dashboard", "owner_decides", {"lead": "lead-001", "decision": "approve"}))
    at(9, 0, day=1)
    w.submit(Write("scheduler", "release_held", {}))
    w.submit(Write("owner-telegram", "undo", {"handle": "U001"}))
    return w


def main(argv: list[str]) -> int:
    path = argv[argv.index("--db") + 1] if "--db" in argv else None
    w = scripted_day(path)
    print("WhatsApp agent case study: teaching model on invented leads (synthetic, not real)")
    print("-" * 92)
    for line in w.log:
        print(line)
    print("-" * 92)
    q = w.db.execute("SELECT status, COUNT(*) FROM outbox GROUP BY status ORDER BY status").fetchall()
    n_in = w.db.execute("SELECT COUNT(*) FROM messages WHERE direction='in'").fetchone()[0]
    n_j = w.db.execute("SELECT COUNT(*) FROM journal").fetchone()[0]
    print(f"outbox: {', '.join(f'{s}={n}' for s, n in q)} · inbound stored: {n_in} · journal entries: {n_j} · spool: {len(w.spool)}")
    print("every write went through one writer; nothing was sent to anyone")
    if path:
        print(f"database kept at {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
