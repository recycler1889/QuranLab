"""Tests du parcours de lecture de l'arabe (module iqra, pur)."""

import unittest

from quranlab import iqra


class TestAlphabet(unittest.TestCase):
    def test_28_lettres_completes(self):
        self.assertEqual(len(iqra.ALPHABET), 28)
        for letter in iqra.ALPHABET:
            self.assertTrue(letter["ar"])
            self.assertTrue(letter["name"])
            self.assertTrue(letter["tr"])
            self.assertEqual(len(letter["forms"]), 4)
            self.assertTrue(letter["ar_name"])
            self.assertTrue(
                any("\u0620" <= ch <= "\u064a" for ch in letter["ar_name"]),
                f"{letter['ar']}: ar_name non arabe",
            )

    def test_lettres_connectives_ont_4_formes_distinctes(self):
        for letter in iqra.ALPHABET:
            if letter["ar"] in iqra.NON_CONNECTING:
                continue
            self.assertNotEqual(letter["forms"][0], letter["forms"][1],
                                f"{letter['ar']}: initiale == isolée")
            self.assertNotEqual(letter["forms"][1], letter["forms"][2],
                                f"{letter['ar']}: médiale == initiale")
            self.assertNotEqual(letter["forms"][2], letter["forms"][3],
                                f"{letter['ar']}: finale == médiale")

    def test_lettres_non_connectives(self):
        for ar in iqra.NON_CONNECTING:
            letter = next(l for l in iqra.ALPHABET if l["ar"] == ar)
            self.assertEqual(letter["forms"][0], letter["forms"][1])
            self.assertEqual(letter["forms"][2], letter["forms"][3])

    def test_consonants_sans_alif(self):
        self.assertEqual(len(iqra.consonants()), 27)
        self.assertTrue(all(l["ar"] != "ا" for l in iqra.consonants()))
        self.assertEqual(len(iqra.consonants(exclude_alif=False)), 28)


class TestVowels(unittest.TestCase):
    def test_trois_voyelles_courtes(self):
        self.assertEqual(len(iqra.SHORT_VOWELS), 3)
        self.assertEqual(len({v["key"] for v in iqra.SHORT_VOWELS}), 3)
        for v in iqra.SHORT_VOWELS:
            self.assertTrue(v["ar"].startswith("ب"))
            self.assertTrue(v["tr"])

    def test_trois_voyelles_longues(self):
        self.assertEqual(len(iqra.LONG_VOWELS), 3)
        keys = {v["key"] for v in iqra.LONG_VOWELS}
        self.assertEqual(len(keys), 3)
        for v in iqra.LONG_VOWELS:
            self.assertTrue(v["ar"].startswith("ب"))
            self.assertTrue(len(v["ar"]) >= 2)
            self.assertTrue(v["combo"])


class TestSyllables(unittest.TestCase):
    def test_syllable_pairs_coherence(self):
        pairs = iqra.syllable_pairs()
        self.assertEqual(len(pairs), 27 * 3)
        pairs_ar = [p["ar"] for p in pairs]
        self.assertEqual(len(set(pairs_ar)), len(pairs_ar))
        for p in pairs:
            self.assertTrue(p["tr"])
            self.assertTrue(p["ar"])

    def test_syllables_grid_equals_pairs(self):
        grid = iqra.syllables_grid()
        self.assertEqual(len(grid), 27)
        for row in grid:
            for key in iqra.SHORT_VOWELS:
                v = key["key"]
                self.assertIn(v, row)
                expected = next(
                    p for p in iqra.syllable_pairs()
                    if p["key"] == f"{row['ar']}-{v}"
                )
                self.assertEqual(row[v], expected["ar"])
                self.assertEqual(row[v + "_tr"], expected["tr"])


class TestMarks(unittest.TestCase):
    def test_trois_signes(self):
        self.assertEqual([m["key"] for m in iqra.MARKS],
                         ["sukun", "shadda", "tanwin"])
        for m in iqra.MARKS:
            self.assertTrue(m["name"])
            self.assertTrue(m["sign"])
            self.assertTrue(m["tr"])
            self.assertTrue(m["ar"])
            self.assertTrue(m["words"])
            for (ar, tr, fr, en) in m["words"]:
                self.assertTrue(ar)
                self.assertTrue(tr)
                self.assertTrue(fr)
                self.assertTrue(en)


class TestReadingTiers(unittest.TestCase):
    def test_tiers_ordonnes_et_complets(self):
        keys = [t["key"] for t in iqra.READING_TIERS]
        self.assertEqual(keys, [1, 2, 3, 4, 5])
        for tier in iqra.READING_TIERS:
            self.assertTrue(tier["title_fr"])
            self.assertTrue(tier["title_en"])
            self.assertTrue(tier["hint_fr"])
            self.assertTrue(tier["hint_en"])
            self.assertTrue(tier["words"])
            for w in tier["words"]:
                self.assertTrue(w["ar"])
                self.assertTrue(w["tr"])
                self.assertTrue(w["fr"])
                self.assertTrue(w["en"])
                if w.get("ref"):
                    sura, aya = w["ref"].split(":")
                    self.assertTrue(sura.isdigit())
                    self.assertTrue(aya.isdigit())

    def test_premier_tier_mots_simples(self):
        self.assertEqual(iqra.READING_TIERS[0]["key"], 1)
        self.assertTrue(len(iqra.READING_TIERS[0]["words"]) >= 4)


class TestPracticeSurahs(unittest.TestCase):
    def test_sourates_courtes_contigues(self):
        for sura, translit in iqra.PRACTICE_SURAHS:
            self.assertIn(sura, (1, 112, 113, 114))
            keys = sorted(translit)
            self.assertEqual(keys, list(range(1, len(keys) + 1)),
                             f"sourate {sura}: versets non contigus")
            for v in translit.values():
                self.assertTrue(v.strip())

    def test_transcriptions_presentes(self):
        total = sum(len(translit) for _, translit in iqra.PRACTICE_SURAHS)
        # 4 + 5 + 6 + 7 = 22 versets transcrits.
        self.assertEqual(total, 22)


class TestNumbers(unittest.TestCase):
    def _has_arabic(self, s: str) -> bool:
        return any(
            "\u0620" <= ch <= "\u064a"
            or ch in "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652"
            for ch in s
        )

    def test_unites_1_a_10(self):
        self.assertEqual([u["n"] for u in iqra.NUM_UNITS],
                         list(range(1, 11)))
        for u in iqra.NUM_UNITS:
            self.assertTrue(u["ar"])
            self.assertTrue(u["tr"])
            self.assertTrue(self._has_arabic(u["ar"]))

    def test_dizaines_et_centaines(self):
        self.assertEqual([t["n"] for t in iqra.NUM_TENS],
                         list(range(20, 100, 10)))
        self.assertEqual([h["n"] for h in iqra.NUM_HUNDREDS],
                         [*range(100, 1000, 100), 1000])
        for item in iqra.NUM_TENS + iqra.NUM_HUNDREDS:
            self.assertTrue(self._has_arabic(item["ar"]))
            self.assertTrue(item["tr"])

    def test_arabic_digits_conversion(self):
        self.assertEqual(iqra.arabic_digits(0), "٠")
        self.assertEqual(iqra.arabic_digits(1), "١")
        self.assertEqual(iqra.arabic_digits(21), "٢١")
        self.assertEqual(iqra.arabic_digits(1000), "١٠٠٠")
        self.assertEqual(len(iqra.arabic_digits(999)), 3)

    def test_valeurs_uniques(self):
        seen = [x["n"] for x in iqra.NUM_UNITS + iqra.NUM_TENS
                + iqra.NUM_HUNDREDS]
        self.assertEqual(len(seen), len(set(seen)))


if __name__ == "__main__":
    unittest.main()