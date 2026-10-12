"""Tests de recherche adossés à une base en mémoire.

Couvre l'échappement des métacaractères ``LIKE`` (une saisie littérale ne doit
jamais se comporter comme un joker) et la tolérance des entrées vides/``None``.
"""

import sqlite3
import unittest

from quranlab import search
from quranlab.buckwalter import normalize_arabic, normalize_latin


def _make_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE verses (
            sura INTEGER, aya INTEGER, text_uthmani TEXT,
            text_simple TEXT, text_simple_norm TEXT);
        CREATE TABLE translations (
            id INTEGER PRIMARY KEY, key TEXT, author TEXT);
        CREATE TABLE translation_verses (
            sura INTEGER, aya INTEGER, translation_id INTEGER,
            text TEXT, text_norm TEXT);
        """
    )
    verses = [
        (1, 1, "بسم الله", "بسم الله", normalize_arabic("بسم الله")),
        (1, 2, "الرحمن", "الرحمن", normalize_arabic("الرحمن")),
        (1, 3, "نسبة 100% ماء_", "نسبة 100% ماء_", normalize_arabic("نسبة 100% ماء_")),
    ]
    con.executemany("INSERT INTO verses VALUES (?,?,?,?,?)", verses)
    con.execute("INSERT INTO translations VALUES (1, 'k1', 'Auteur')")
    for sura, aya, text in [
        (1, 1, "Au nom de Dieu"),
        (1, 2, "l\u2019homme est faible"),
        (1, 3, "cent pour cent 100% et a_b"),
    ]:
        con.execute(
            "INSERT INTO translation_verses VALUES (?,?,?,?,?)",
            (sura, aya, 1, text, normalize_latin(text)),
        )
    con.commit()
    return con


class TestArabicSearchEscaping(unittest.TestCase):
    def setUp(self):
        self.con = _make_db()

    def tearDown(self):
        self.con.close()

    def test_joker_pourcent_litteral(self):
        # « % » ne doit PAS renvoyer tout le corpus : seul le verset en
        # contenant un littéralement est retourné.
        rows = search.search_arabic(self.con, "%", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in rows], [(1, 3)])

    def test_joker_souligne_litteral(self):
        rows = search.search_arabic(self.con, "_", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in rows], [(1, 3)])

    def test_recherche_arabe_normale(self):
        rows = search.search_arabic(self.con, "الرحمن", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in rows], [(1, 2)])

    def test_entree_vide_toleree(self):
        self.assertEqual(search.search_arabic(self.con, None), [])
        self.assertEqual(search.search_arabic(self.con, "   "), [])


class TestFrenchSearchEscaping(unittest.TestCase):
    def setUp(self):
        self.con = _make_db()

    def tearDown(self):
        self.con.close()

    def test_apostrophe_courbe_et_droite_equivalentes(self):
        droite = search.search_french(self.con, "l'homme", limit=999)
        courbe = search.search_french(self.con, "l\u2019homme", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in droite], [(1, 2)])
        self.assertEqual(
            [(r["sura"], r["aya"]) for r in droite],
            [(r["sura"], r["aya"]) for r in courbe],
        )

    def test_joker_pourcent_litteral(self):
        rows = search.search_french(self.con, "100%", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in rows], [(1, 3)])

    def test_joker_souligne_litteral(self):
        rows = search.search_french(self.con, "a_b", limit=999)
        self.assertEqual([(r["sura"], r["aya"]) for r in rows], [(1, 3)])

    def test_entree_vide_toleree(self):
        self.assertEqual(search.search_french(self.con, None), [])
        self.assertEqual(search.search_french(self.con, ""), [])


if __name__ == "__main__":
    unittest.main()
