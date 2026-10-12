"""Tests du « Vocabulaire essentiel » (vocab.frequent_words / corpus_token_count).

Base de test : une table ``words`` en mémoire (``sqlite3 :memory:``) calquée
sur le schéma du corpus — suffisante pour vérifier les agrégations, le choix
de la forme la plus fréquente, la première référence et la couverture cumulée.
"""

import sqlite3
import unittest

from quranlab import vocab


def _make_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE words (
            id INTEGER PRIMARY KEY, sura INTEGER, aya INTEGER, word_index INTEGER,
            form_buckwalter TEXT, form_arabic TEXT, transliteration TEXT,
            root_buckwalter TEXT, root_arabic TEXT, root_norm TEXT,
            lemma_buckwalter TEXT, pos TEXT)
        """
    )
    con.executemany(
        "INSERT INTO words (sura, aya, word_index, form_arabic,"
        " transliteration, root_buckwalter, root_arabic) VALUES (?,?,?,?,?,?,?)",
        [
            (1, 1, 1, "ٱللَّهِ", "allahi", "Alh", "الله"),
            (1, 1, 2, "ٱللَّهُ", "allahu", "Alh", "الله"),
            (2, 1, 1, "ٱللَّهِ", "allahi", "Alh", "الله"),
            (1, 1, 3, "كِتَابٌ", "kitabun", "KTB", "كتب"),
            (5, 5, 1, "", "", "Shm", "شمس"),
        ],
    )
    return con


class TestFrequentWords(unittest.TestCase):
    def setUp(self):
        self.con = _make_db()

    def tearDown(self):
        self.con.close()

    def test_corpus_token_count(self):
        self.assertEqual(vocab.corpus_token_count(self.con), 5)

    def test_racines_triees_par_occurrence(self):
        words = vocab.frequent_words(self.con, top_n=3, lang="fr")
        self.assertEqual(len(words), 3)
        self.assertEqual(words[0]["root_bw"], "Alh")
        self.assertEqual(words[0]["occ"], 3)
        occs = [w["occ"] for w in words]
        self.assertEqual(occs, sorted(occs, reverse=True))

    def test_forme_la_plus_frequente_et_reference(self):
        first = vocab.frequent_words(self.con, top_n=3)[0]
        self.assertEqual(first["ar"], "ٱللَّهِ")
        self.assertEqual(first["tr"], "allahi")
        self.assertEqual(first["verses"], 2)
        self.assertEqual(first["ref"], "1:1")
        self.assertEqual(first["rank"], 1)
        self.assertTrue(first["root_ar"])

    def test_couverture_cumulee(self):
        words = vocab.frequent_words(self.con, top_n=2)
        # (3 + 1) / 5 = 80 %.
        self.assertAlmostEqual(words[-1]["coverage_pct"], 80.0, places=1)

    def test_racine_sans_forme_voyellee_est_gardee(self):
        words = vocab.frequent_words(self.con, top_n=3)
        shm = [w for w in words if w["root_bw"] == "Shm"][0]
        self.assertEqual(shm["occ"], 1)
        self.assertEqual(shm["ref"], "5:5")


if __name__ == "__main__":
    unittest.main()