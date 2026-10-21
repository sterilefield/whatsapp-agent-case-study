# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ravi Teja Thiriveedhi
"""Tests for demo/spine_demo.py (standard library unittest)."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "demo"))
import spine_demo as sd  # noqa: E402


class Spine(unittest.TestCase):
    def setUp(self):
        self.w = sd.scripted_day()
        self.q = lambda sql: self.w.db.execute(sql).fetchall()

    def test_duplicate_inbound_is_stored_once(self):
        self.assertEqual(self.q("SELECT COUNT(*) FROM messages WHERE msg_id='m-1'")[0][0], 1)

    def test_spool_is_empty_after_replay(self):
        self.assertEqual(self.w.spool, [])
        self.assertEqual(self.q("SELECT COUNT(*) FROM messages WHERE msg_id='m-3'")[0][0], 1)

    def test_nothing_sent_without_owner_approval(self):
        statuses = {s for (s,) in self.q("SELECT status FROM outbox")}
        self.assertLessEqual(statuses, {"sent", "rejected", "withdrawn"})
        self.assertNotIn("pending_approval", statuses)
        self.assertEqual(self.q("SELECT COUNT(*) FROM outbox WHERE status='sent'")[0][0], 2)

    def test_takeover_blocks_agent_followups(self):
        self.assertEqual(self.q("SELECT COUNT(*) FROM outbox WHERE lead_id='lead-002'")[0][0], 0)

    def test_takeover_withdraws_queued_followups(self):
        w = sd.Writer(sd.sqlite3.connect(":memory:"))
        w.db.executescript(sd.SCHEMA)
        w.submit(sd.Write("webhook", "new_lead", {"lead": "lead-009", "name": "Synthetic lead"}))
        w.submit(sd.Write("agent", "propose_followup", {"lead": "lead-009", "template": "demo_template_1"}))
        w.submit(sd.Write("staff", "staff_reply", {"lead": "lead-009", "msg_id": "m-9", "body": "hi"}))
        self.assertEqual(w.db.execute("SELECT status FROM outbox").fetchone()[0], "withdrawn")

    def test_quiet_hours(self):
        self.assertTrue(sd.in_quiet_hours(datetime(2026, 1, 5, 22, 0)))
        self.assertTrue(sd.in_quiet_hours(datetime(2026, 1, 5, 8, 59)))
        self.assertFalse(sd.in_quiet_hours(datetime(2026, 1, 5, 9, 0)))
        self.assertEqual(sd.next_morning(datetime(2026, 1, 5, 22, 0)), datetime(2026, 1, 6, 9, 0))

    def test_undo_restores_value(self):
        self.assertEqual(self.q("SELECT stage FROM leads WHERE id='lead-001'")[0][0], "new")

    def test_sensitive_or_ambiguous_notes_are_not_applied(self):
        self.assertIsNone(sd.owner_note("mark lead-002 lost"))
        self.assertIsNone(sd.owner_note("lead-002 stage lost"))
        self.assertIsNone(sd.owner_note("lead-002 stage opted-out"))
        self.assertIsNone(sd.owner_note("lead-002 stage deleted"))
        self.assertIsNone(sd.owner_note("lead-002 phone 123"))
        self.assertIsNotNone(sd.owner_note("lead-002 stage warm"))


if __name__ == "__main__":
    unittest.main()
