"""Tests du module de synthèse convergente (analyse lexicale, sans base)."""

import unittest

from quranlab import config, synthesis


class TestReferenceKeys(unittest.TestCase):
    def test_french_reference_set_is_three(self):
        available = [("fr.hamidullah", "fr"), ("fr.rashidmaash", "fr"),
                     ("fr.montada", "fr"), ("en.sahih", "en"),
                     ("en.pickthall", "en")]
        keys = synthesis.reference_keys("fr", available)
        self.assertEqual(keys, ["fr.hamidullah", "fr.rashidmaash", "fr.montada"])
        self.assertEqual(len(keys), 3)

    def test_english_fallback_to_available(self):
        available = [("en.sahih", "en"), ("en.pickthall", "en")]
        keys = synthesis.reference_keys("en", available)
        self.assertEqual(keys, ["en.sahih", "en.pickthall"])

    def test_without_available_returns_catalog(self):
        self.assertEqual(
            synthesis.reference_keys("fr"),
            list(config.REFERENCE_TRANSLATIONS),
        )

    def test_at_most_three_when_no_reference_match(self):
        available = [("xx.a", "xx"), ("xx.b", "xx"), ("xx.c", "xx"), ("xx.d", "xx")]
        self.assertEqual(len(synthesis.reference_keys("xx", available)), 3)


class TestSplitTranslations(unittest.TestCase):
    def _trs(self):
        return [
            {"key": "fr.hamidullah", "language": "fr", "text": "A"},
            {"key": "fr.rashidmaash", "language": "fr", "text": "B"},
            {"key": "fr.montada", "language": "fr", "text": "C"},
            {"key": "en.sahih", "language": "en", "text": "D"},
        ]

    def test_default_shows_only_french_reference(self):
        shown, others = synthesis.split_translations(self._trs(), "fr", False)
        self.assertEqual([t["key"] for t in shown],
                         ["fr.hamidullah", "fr.rashidmaash", "fr.montada"])
        self.assertEqual([t["key"] for t in others], ["en.sahih"])

    def test_extended_adds_other_translations(self):
        shown, _ = synthesis.split_translations(self._trs(), "fr", True)
        self.assertEqual([t["key"] for t in shown],
                         ["fr.hamidullah", "fr.rashidmaash", "fr.montada",
                          "en.sahih"])

    def test_empty_input(self):
        shown, others = synthesis.split_translations([], "fr", False)
        self.assertEqual(shown, [])
        self.assertEqual(others, [])


class TestContentTerms(unittest.TestCase):
    def test_stopwords_removed(self):
        terms = synthesis.content_terms("les cieux et la terre", "fr")
        self.assertIn("cieux", terms)
        self.assertIn("terre", terms)
        self.assertNotIn("les", terms)
        self.assertNotIn("et", terms)

    def test_short_words_removed(self):
        self.assertNotIn("il", synthesis.content_terms("il est", "fr"))

    def test_bigrams_built(self):
        terms = synthesis.content_terms("notre seigneur", "fr")
        self.assertIn("seigneur", terms)
        self.assertIn("notre seigneur", terms)

    def test_accent_insensitive(self):
        self.assertIn("misericordieux", synthesis.content_terms("miséricordieux", "fr"))


class TestConvergentTerms(unittest.TestCase):
    def test_needs_majority(self):
        texts = ["le seigneur des mondes", "seigneur des mondes",
                 "au nom du seigneur"]
        terms = {d["term"]: d["docs"] for d in synthesis.convergent_terms(texts, "fr")}
        self.assertIn("seigneur", terms)
        self.assertEqual(terms["seigneur"], 3)

    def test_single_text_returns_empty(self):
        self.assertEqual(synthesis.convergent_terms(["un seul texte"], "fr"), [])

    def test_minority_is_excluded(self):
        texts = ["alpha beta", "gamma delta", "epsilon zeta"]
        self.assertEqual(synthesis.convergent_terms(texts, "fr"), [])

    def test_docs_never_exceed_total(self):
        texts = ["le livre", "le livre", "livre"]
        for d in synthesis.convergent_terms(texts, "fr"):
            self.assertLessEqual(d["docs"], 3)


class TestSynthesize(unittest.TestCase):
    def test_none_when_less_than_two(self):
        self.assertIsNone(synthesis.synthesize(
            [{"key": "fr.hamidullah", "language": "fr", "text": "seul"}], "fr"))

    def test_only_active_language_compared(self):
        trs = [
            {"key": "fr.hamidullah", "language": "fr", "text": "le seigneur"},
            {"key": "fr.rashidmaash", "language": "fr", "text": "le seigneur"},
            {"key": "en.sahih", "language": "en", "text": "totally different"},
        ]
        synth = synthesis.synthesize(trs, "fr")
        self.assertEqual(synth["n"], 2)
        self.assertIn("seigneur", [d["term"] for d in synth["terms"]])


if __name__ == "__main__":
    unittest.main()
