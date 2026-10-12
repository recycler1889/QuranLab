"""Tests rapides de la conversion Buckwalter et de la normalisation."""

import unittest

from quranlab.buckwalter import (
    arabic_to_buckwalter,
    buckwalter_to_arabic,
    buckwalter_to_latin,
    is_arabic,
    normalize_arabic,
    normalize_latin,
)


class TestBuckwalter(unittest.TestCase):
    def test_root_smw(self):
        self.assertEqual(buckwalter_to_arabic("smw"), "سمو")

    def test_root_rHm(self):
        self.assertEqual(buckwalter_to_arabic("rHm"), "رحم")

    def test_roundtrip(self):
        for bw in ("smw", "rHm", "Alh", "wDw"):
            self.assertEqual(arabic_to_buckwalter(buckwalter_to_arabic(bw)), bw)

    def test_latin(self):
        self.assertEqual(buckwalter_to_latin("rHm"), "rḥm")

    def test_is_arabic(self):
        self.assertTrue(is_arabic("رحم"))
        self.assertFalse(is_arabic("rHm"))

    def test_normalize_arabic(self):
        self.assertEqual(normalize_arabic("الرَّحْمَٰنِ"), "الرحمن")
        self.assertEqual(normalize_arabic("إِسْمَاعِيل"), "اسماعيل")


class TestNormalizeLatin(unittest.TestCase):
    def test_apostrophe_typographique_repliee(self):
        # « l’homme » (apostrophe courbe) doit se normaliser comme « l'homme ».
        self.assertEqual(normalize_latin("l\u2019homme"), normalize_latin("l'homme"))

    def test_fonte_apostrophe_courbe(self):
        self.assertIn("'", normalize_latin("l\u2019homme"))

    def test_ligatures_repliees(self):
        self.assertEqual(normalize_latin("cœur"), normalize_latin("coeur"))
        self.assertEqual(normalize_latin("æon"), normalize_latin("aeon"))

    def test_accents_retires(self):
        self.assertEqual(normalize_latin("Patience Élève"), "patience eleve")


class TestNoneGuards(unittest.TestCase):
    def test_normalisations_tolerant_none(self):
        self.assertEqual(normalize_arabic(None), "")
        self.assertEqual(normalize_latin(None), "")
        self.assertFalse(is_arabic(None))
        self.assertFalse(is_arabic(""))

    def test_is_arabic_ignore_chiffres_et_ponctuation(self):
        # Chiffres arabo-indiens et ponctuation : pas des lettres arabes.
        self.assertFalse(is_arabic("\u0661\u0662"))
        self.assertFalse(is_arabic("\u060c"))
        self.assertTrue(is_arabic("\u0661رحم"))


if __name__ == "__main__":
    unittest.main()
