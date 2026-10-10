"""Tests des aides pures de vocabulaire et de quiz (sans base de données)."""

import random
import unittest

from quranlab import quiz, srs, vocab


class TestRootGloss(unittest.TestCase):
    def test_gloss_from_lexicon(self):
        # lexicon_fr.json : « patience » -> racine Sbr.
        self.assertIn("sabr", vocab.root_gloss("Sbr", "fr"))

    def test_unknown_root_empty(self):
        self.assertEqual(vocab.root_gloss("zzzz", "fr"), "")

    def test_empty_input(self):
        self.assertEqual(vocab.root_gloss(""), "")


class TestBuildChoices(unittest.TestCase):
    def test_correct_included_once(self):
        opts = quiz.build_choices("bonne", ["a", "b", "c", "d"], n=4,
                                  rng=random.Random(1))
        texts = [o["text"] for o in opts]
        self.assertIn("bonne", texts)
        self.assertEqual(sum(1 for o in opts if o["correct"]), 1)
        self.assertEqual(len(opts), 4)

    def test_distinct_options(self):
        opts = quiz.build_choices("x", ["y", "y", "z"], n=4,
                                  rng=random.Random(2))
        texts = [o["text"] for o in opts]
        self.assertEqual(len(texts), len(set(texts)))

    def test_minimum_two_even_without_distractors(self):
        opts = quiz.build_choices("only", [], n=4, rng=random.Random(3))
        self.assertEqual(len(opts), 1)  # aucune alternative disponible
        self.assertTrue(opts[0]["correct"])


class TestGrade(unittest.TestCase):
    def test_grade_mapping(self):
        self.assertEqual(quiz.grade(True), srs.GRADE_GOOD)
        self.assertEqual(quiz.grade(False), srs.GRADE_AGAIN)


if __name__ == "__main__":
    unittest.main()
