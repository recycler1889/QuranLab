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


class TestParseRef(unittest.TestCase):
    def test_colon(self):
        self.assertEqual(search.parse_ref("2:255"), (2, 255))

    def test_space_separator(self):
        self.assertEqual(search.parse_ref("2 255"), (2, 255))

    def test_whitespace_around(self):
        self.assertEqual(search.parse_ref("  2 : 255  "), (2, 255))

    def test_last_sura(self):
        self.assertEqual(search.parse_ref("114:6"), (114, 6))

    def test_not_a_ref(self):
        for bad in ("", "2", "2:255:1", "abc", "2:35x", "2255", "2,255"):
            self.assertIsNone(search.parse_ref(bad), bad)

    def test_out_of_bounds(self):
        self.assertIsNone(search.parse_ref("0:5"))
        self.assertIsNone(search.parse_ref("115:1"))
        self.assertIsNone(search.parse_ref("2:0"))


if __name__ == "__main__":
    unittest.main()
