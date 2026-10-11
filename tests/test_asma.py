"""Tests des 99 Noms d'Allah (approche étymologique).

Vérifie l'intégrité des données (99 entrées complètes, rangs et
translittérations uniques, script arabe, teintes valides) et le filtre.
"""

import re
import unittest

from quranlab import asma

_ARABIC = re.compile(r"[\u0600-\u06FF]")
_FIELDS = ("ar", "tr", "root_ar", "root_tr", "fr", "en",
           "etym_fr", "etym_en", "icon")


class TestAsmaData(unittest.TestCase):
    def test_count_is_99(self):
        self.assertEqual(asma.count(), 99)
        self.assertEqual(len(asma.NAMES), 99)

    def test_ranks_are_one_to_99(self):
        self.assertEqual(sorted(n["n"] for n in asma.NAMES), list(range(1, 100)))

    def test_fields_are_all_non_empty(self):
        for name in asma.NAMES:
            for field in _FIELDS:
                self.assertTrue(name.get(field), f"champ vide {field} (#{name['n']})")

    def test_arabic_fields_use_arabic_script(self):
        for name in asma.NAMES:
            self.assertRegex(name["ar"], _ARABIC, f"ar non arabe #{name['n']}")
            self.assertRegex(name["root_ar"], _ARABIC, f"racine non arabe #{name['n']}")

    def test_transliterations_unique(self):
        trs = [n["tr"] for n in asma.NAMES]
        self.assertEqual(len(trs), len(set(trs)))

    def test_arabic_names_unique(self):
        ars = [n["ar"] for n in asma.NAMES]
        self.assertEqual(len(ars), len(set(ars)))

    def test_traditional_first_and_last(self):
        self.assertEqual(asma.NAMES[0]["tr"], "Ar-Raḥmān")
        self.assertEqual(asma.NAMES[98]["tr"], "As-Sabūr")

    def test_hues_in_range(self):
        for name in asma.NAMES:
            self.assertTrue(0 <= name["hue"] < 360, f"teinte hors plage #{name['n']}")


class TestAsmaHelpers(unittest.TestCase):
    def test_translation_follows_language(self):
        first = asma.NAMES[0]
        self.assertEqual(asma.translation(first, "fr"), first["fr"])
        self.assertEqual(asma.translation(first, "en"), first["en"])

    def test_translation_falls_back_to_french(self):
        fake = {"n": 1, "fr": "Le Tout-Miséricordieux"}
        self.assertEqual(asma.translation(fake, "xx"), "Le Tout-Miséricordieux")

    def test_etymology_follows_language(self):
        first = asma.NAMES[0]
        self.assertEqual(asma.etymology(first, "fr"), first["etym_fr"])
        self.assertEqual(asma.etymology(first, "en"), first["etym_en"])

    def test_fold_strips_accents_and_case(self):
        self.assertEqual(asma._fold("Créateur"), "createur")


class TestAsmaSearch(unittest.TestCase):
    def test_empty_query_returns_all(self):
        self.assertEqual(len(asma.search("", "fr")), 99)

    def test_find_by_transliteration(self):
        self.assertIn(1, [n["n"] for n in asma.search("Rahman", "fr")])

    def test_find_by_arabic_name(self):
        self.assertIn(1, [n["n"] for n in asma.search("الرحمن", "fr")])

    def test_find_by_french_meaning(self):
        self.assertIn(11, [n["n"] for n in asma.search("créateur", "fr")])

    def test_find_root_ignoring_spaces(self):
        matches = [n["n"] for n in asma.search("رحم", "fr")]
        self.assertIn(1, matches)

    def test_no_match_returns_empty(self):
        self.assertEqual(asma.search("zzzzz", "fr"), [])


if __name__ == "__main__":
    unittest.main()
