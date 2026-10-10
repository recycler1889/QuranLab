"""Tests de l'ordonnancement SRS (algorithme pur, sans base ni Streamlit)."""

import unittest
from datetime import datetime, timedelta

from quranlab import srs


class TestNewCard(unittest.TestCase):
    def test_new_card_is_due(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        card = srs.new_card("root", "ktb", ar="كتب", label="écrire", now=now)
        self.assertEqual(card["state"], "new")
        self.assertEqual(card["reps"], 0)
        self.assertTrue(srs.is_due(card, now))

    def test_future_due_not_due(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        card = srs.new_card("root", "ktb", now=now)
        card["state"] = "review"
        card["due"] = (now + timedelta(days=3)).isoformat(timespec="seconds")
        self.assertFalse(srs.is_due(card, now))


class TestLearningPhase(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 1, 12, 0, 0)
        self.card = srs.new_card("root", "ktb", now=self.now)

    def test_good_advances_step(self):
        card = srs.review(self.card, srs.GRADE_GOOD, steps=(1, 10),
                          now=self.now)
        self.assertEqual(card["state"], "learning")
        self.assertEqual(card["step"], 1)

    def test_again_resets_and_counts_lapse(self):
        card = srs.review(self.card, srs.GRADE_AGAIN, steps=(1, 10),
                          now=self.now)
        self.assertEqual(card["state"], "learning")
        self.assertEqual(card["step"], 0)
        self.assertEqual(card["lapses"], 1)

    def test_easy_graduates_to_review(self):
        card = srs.review(self.card, srs.GRADE_EASY, steps=(1, 10),
                          now=self.now)
        self.assertEqual(card["state"], "review")
        self.assertGreaterEqual(card["interval"], 4)

    def test_two_good_graduate(self):
        card = srs.review(self.card, srs.GRADE_GOOD, steps=(1, 10),
                          now=self.now)
        card = srs.review(card, srs.GRADE_GOOD, steps=(1, 10), now=self.now)
        self.assertEqual(card["state"], "review")
        self.assertEqual(card["reps"], 1)


class TestReviewPhase(unittest.TestCase):
    def _due(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        card = srs.new_card("root", "ktb", now=now)
        card.update({"state": "review", "interval": 10.0, "reps": 2,
                     "ease": 2.5,
                     "due": now.isoformat(timespec="seconds")})
        return card, now

    def test_good_multiplies_interval(self):
        card, now = self._due()
        out = srs.review(card, srs.GRADE_GOOD, now=now)
        self.assertEqual(out["state"], "review")
        self.assertGreater(out["interval"], 10)
        self.assertEqual(out["reps"], 3)

    def test_again_returns_to_learning(self):
        card, now = self._due()
        out = srs.review(card, srs.GRADE_AGAIN, now=now)
        self.assertEqual(out["state"], "learning")
        self.assertEqual(out["lapses"], 1)

    def test_ease_bounds(self):
        card, now = self._due()
        for _ in range(20):
            card = srs.review(card, srs.GRADE_EASY, now=now)
        self.assertLessEqual(card["ease"], 3.0)
        for _ in range(40):
            card = srs.review(card, srs.GRADE_HARD, now=now)
        self.assertGreaterEqual(card["ease"], 1.3)


class TestMastery(unittest.TestCase):
    def test_mastery_requires_review_and_reps(self):
        now = datetime(2026, 1, 1)
        card = srs.new_card("root", "ktb", now=now)
        self.assertFalse(srs.mastery(card))
        card.update({"state": "review", "reps": 2})
        self.assertTrue(srs.mastery(card, reps=2))


class TestGradeNames(unittest.TestCase):
    def test_int_and_str(self):
        self.assertEqual(srs._grade_name(0), srs.GRADE_AGAIN)
        self.assertEqual(srs._grade_name(3), srs.GRADE_EASY)
        self.assertEqual(srs._grade_name("good"), srs.GRADE_GOOD)
        self.assertEqual(srs._grade_name("unknown"), srs.GRADE_GOOD)


if __name__ == "__main__":
    unittest.main()
