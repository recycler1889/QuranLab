"""Tests du store de progression (persistance JSON), sans toucher au fichier réel."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from quranlab import learning, srs


class TestLearningStore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = learning._LEARNING_PATH
        learning._LEARNING_PATH = Path(self._tmp.name) / "learning.json"
        self.now = datetime(2026, 1, 1, 12, 0, 0)

    def tearDown(self):
        learning._LEARNING_PATH = self._orig
        self._tmp.cleanup()

    def test_empty_initially(self):
        self.assertEqual(learning.all_cards(), [])
        self.assertEqual(learning.stats()["total_cards"], 0)

    def test_ensure_card_idempotent(self):
        c1 = learning.ensure_card("root", "ktb", ar="كتب", label="écrire")
        c2 = learning.ensure_card("root", "ktb", ar="كتب", label="écrire")
        self.assertEqual(c1["id"], "ktb")
        self.assertEqual(learning.stats()["total_cards"], 1)
        self.assertEqual(c2["state"], "new")

    def test_record_review_updates_daily(self):
        learning.record_review("root", "ktb", srs.GRADE_GOOD, now=self.now)
        learning.record_review("root", "ktb", srs.GRADE_GOOD, now=self.now)
        stats_day = learning.stats(now=self.now)
        self.assertEqual(stats_day["reviews_today"], 2)
        self.assertEqual(stats_day["new_today"], 1)
        self.assertEqual(stats_day["correct_today"], 2)
        self.assertEqual(stats_day["total_cards"], 1)

    def test_due_cards(self):
        learning.record_review("root", "ktb", srs.GRADE_EASY, now=self.now)
        # « facile » place la carte dans 4 jours : plus due le même jour.
        self.assertEqual(len(learning.due_cards(now=self.now)), 0)

    def test_settings_roundtrip(self):
        learning.set_settings(daily_new=15, daily_review=50, reminders=True)
        s = learning.get_settings()
        self.assertEqual(s["daily_new"], 15)
        self.assertEqual(s["daily_review"], 50)
        self.assertTrue(s["reminders"])

    def test_streak_counts_today(self):
        learning.record_review("root", "ktb", srs.GRADE_GOOD, now=self.now)
        self.assertEqual(learning.stats(now=self.now)["streak"], 1)


if __name__ == "__main__":
    unittest.main()
