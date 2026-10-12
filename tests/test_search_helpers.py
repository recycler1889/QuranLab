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

    def test_none_is_ignored(self):
        self.assertEqual(search.resolve_theme_key(None), (None, []))


class TestLikeEscaping(unittest.TestCase):
    def test_jokers_echappes(self):
        self.assertEqual(search._like_pattern("100%"), "%100\\%%")
        self.assertEqual(search._like_pattern("a_b"), "%a\\_b%")
        self.assertEqual(search._like_pattern("a\\b"), "%a\\\\b%")

    def test_terme_simple_inchange(self):
        self.assertEqual(search._like_pattern("miséricorde"), "%miséricorde%")


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

    def test_dot(self):
        self.assertEqual(search.parse_ref("22.78"), (22, 78))

    def test_dot_whitespace_around(self):
        self.assertEqual(search.parse_ref("  22 . 78  "), (22, 78))

    def test_slash(self):
        self.assertEqual(search.parse_ref("22/78"), (22, 78))

    def test_slash_whitespace_around(self):
        self.assertEqual(search.parse_ref(" 22 / 78 "), (22, 78))

    def test_space_separator(self):
        self.assertEqual(search.parse_ref("2 255"), (2, 255))

    def test_multiple_spaces(self):
        self.assertEqual(search.parse_ref("22    78"), (22, 78))

    def test_whitespace_around(self):
        self.assertEqual(search.parse_ref("  2 : 255  "), (2, 255))

    def test_last_sura(self):
        self.assertEqual(search.parse_ref("114:6"), (114, 6))

    def test_all_separators(self):
        for sep in (":", ".", "/", " "):
            self.assertEqual(search.parse_ref(f"22{sep}78"), (22, 78), repr(sep))

    def test_not_a_ref(self):
        for bad in ("", "2", "2:255:1", "abc", "2:35x", "2255", "2,255",
                    "22-78", "22..78", "22//78", "22.35x"):
            self.assertIsNone(search.parse_ref(bad), bad)

    def test_out_of_bounds(self):
        self.assertIsNone(search.parse_ref("0:5"))
        self.assertIsNone(search.parse_ref("115:1"))
        self.assertIsNone(search.parse_ref("2:0"))


_BY_NUM = {n: {"verses_count": 286 if n == 2 else 7 if n == 1 else 6}
           for n in (1, 2, 114)}


class TestJumpTarget(unittest.TestCase):
    def test_verse_ref_colon(self):
        self.assertEqual(search.jump_target("2:255", _BY_NUM), ("verse", 2, 255))

    def test_verse_ref_space(self):
        self.assertEqual(search.jump_target("2 255", _BY_NUM), ("verse", 2, 255))

    def test_verse_ref_dot(self):
        self.assertEqual(search.jump_target("2.255", _BY_NUM), ("verse", 2, 255))

    def test_verse_ref_slash(self):
        self.assertEqual(search.jump_target("2/255", _BY_NUM), ("verse", 2, 255))

    def test_surah_number(self):
        self.assertEqual(search.jump_target("2", _BY_NUM), ("sura", 2))

    def test_whitespace_tolerated(self):
        self.assertEqual(search.jump_target("  2 : 255  ", _BY_NUM), ("verse", 2, 255))

    def test_unknown_input(self):
        for bad in ("", "abc", "2:35x", "0:5", "2:999", "115", "999", "2-255"):
            self.assertIsNone(search.jump_target(bad, _BY_NUM), bad)


if __name__ == "__main__":
    unittest.main()
