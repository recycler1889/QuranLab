"""Tests des aides de recherche sans dépendance à la base (purs)."""

import unittest

from quranlab import search


class TestThemeResolution(unittest.TestCase):
    def test_exact_key(self):
        self.assertEqual(search.resolve_theme_key("priere"), ("priere", []))

    def test_common_variant(self):
        # Le README et la CLI documentent `theme salat` : doit résoudre vers
        # la clé canonique « priere » (libellé « aṣ-ṣalāt »).
        self.assertEqual(search.resolve_theme_key("salat"), ("priere", []))

    def test_too_short_is_ignored(self):
        self.assertEqual(search.resolve_theme_key("or"), (None, []))

    def test_unknown_returns_no_suggestion(self):
        key, suggestions = search.resolve_theme_key("zzznope")
        self.assertIsNone(key)
        self.assertEqual(suggestions, [])


class TestFrenchHelpers(unittest.TestCase):
    def test_stem_plural(self):
        self.assertEqual(search._stem("prieres"), "priere")
        self.assertEqual(search._stem("or"), "or")

    def test_query_forms_tokens(self):
        forms = search._query_forms("la patience")
        self.assertIn("patience", forms)
        self.assertIn("la", forms)


if __name__ == "__main__":
    unittest.main()
