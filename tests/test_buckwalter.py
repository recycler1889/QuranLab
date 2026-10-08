"""Tests rapides de la conversion Buckwalter et de la normalisation."""

import unittest

from quranlab.buckwalter import (
    arabic_to_buckwalter,
    buckwalter_to_arabic,
    buckwalter_to_latin,
    is_arabic,
    normalize_arabic,
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


if __name__ == "__main__":
    unittest.main()
