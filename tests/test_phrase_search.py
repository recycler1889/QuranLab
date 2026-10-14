"""Tests de la recherche d'expressions (multi-mots) et de la surbrillance.

- ``search.match_spans`` : positions de l'expression dans le texte d'origine,
  insensibles à la casse, aux accents et aux diacritiques (pur).
- ``ui.highlight_html`` : échappement HTML + balisage ``<mark class='ql-hit'>``.
- ``search.search_phrase`` : recherche multi-mots français et arabe (base
  en mémoire).
- ``search.surah_audio_stats`` : estimation de durée d'écoute par sourate.
"""

import sqlite3
import unittest

from quranlab import search, ui
from quranlab.buckwalter import normalize_arabic, normalize_latin


class TestMatchSpans(unittest.TestCase):
    def test_latin_accent_insensitive(self):
        spans = search.match_spans("ô notre Seigneur", "notre seigneur")
        self.assertEqual(spans, [(2, 16)])

    def test_multiple_occurrences(self):
        spans = search.match_spans("terre et terre", "terre")
        self.assertEqual(spans, [(0, 5), (9, 14)])

    def test_no_match(self):
        self.assertEqual(search.match_spans("les cieux", "terre"), [])

    def test_empty_query(self):
        self.assertEqual(search.match_spans("les cieux", ""), [])
        self.assertEqual(search.match_spans("", "terre"), [])
        self.assertEqual(search.match_spans("abc", None), [])

    def test_arabic_diacritics_ignored(self):
        text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ"
        spans = search.match_spans(text, "الرحمن", arabic=True)
        self.assertEqual(len(spans), 1)
        start, end = spans[0]
        self.assertEqual(normalize_arabic(text[start:end]), "الرحمن")


class TestHighlightHtml(unittest.TestCase):
    def test_marks_and_escapes(self):
        out = ui.highlight_html("terre <x>", "terre")
        self.assertIn("<mark class='ql-hit'>terre</mark>", out)
        self.assertIn("&lt;x&gt;", out)

    def test_no_query_escapes_only(self):
        self.assertEqual(ui.highlight_html("a & b", None), "a &amp; b")

    def test_no_match_is_plain(self):
        self.assertEqual(ui.highlight_html("ciel", "terre"), "ciel")


def _make_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE verses (
            sura INTEGER, aya INTEGER, text_uthmani TEXT,
            text_simple TEXT, text_simple_norm TEXT);
        CREATE TABLE translations (
            id INTEGER PRIMARY KEY, key TEXT, author TEXT, language TEXT);
        CREATE TABLE translation_verses (
            sura INTEGER, aya INTEGER, translation_id INTEGER,
            text TEXT, text_norm TEXT);
        """
    )
    verses = [
        (1, 1, "بسم الله الرحمن الرحيم", "بسم الله الرحمن الرحيم",
         normalize_arabic("بسم الله الرحمن الرحيم")),
        (2, 255, "الله لا اله الا هو", "الله لا اله الا هو",
         normalize_arabic("الله لا اله الا هو")),
    ]
    con.executemany("INSERT INTO verses VALUES (?,?,?,?,?)", verses)
    con.execute("INSERT INTO translations VALUES (1, 'fr.hamidullah', 'H', 'fr')")
    con.execute("INSERT INTO translations VALUES (2, 'en.sahih', 'S', 'en')")
    for sura, aya, tid, text in [
        (1, 1, 1, "Au nom d'Allah, le Tout Miséricordieux"),
        (2, 255, 1, "les cieux et la terre"),
        (2, 255, 2, "the heavens and the earth"),
    ]:
        con.execute(
            "INSERT INTO translation_verses VALUES (?,?,?,?,?)",
            (sura, aya, tid, text, normalize_latin(text)),
        )
    con.commit()
    return con


class TestSearchPhrase(unittest.TestCase):
    def setUp(self):
        self.con = _make_db()

    def tearDown(self):
        self.con.close()

    def test_french_multiword(self):
        res = search.search_phrase(self.con, "cieux et la terre")
        self.assertEqual(res["lang"], "fr")
        self.assertEqual(res["verses"], 1)
        self.assertEqual((res["rows"][0]["sura"], res["rows"][0]["aya"]), (2, 255))

    def test_french_accent_insensitive(self):
        res = search.search_phrase(self.con, "misericordieux")
        self.assertEqual(res["verses"], 1)
        self.assertEqual((res["rows"][0]["sura"], res["rows"][0]["aya"]), (1, 1))

    def test_arabic_phrase(self):
        res = search.search_phrase(self.con, "الرحمن")
        self.assertEqual(res["lang"], "ar")
        self.assertGreaterEqual(res["verses"], 1)
        self.assertEqual((res["rows"][0]["sura"], res["rows"][0]["aya"]), (1, 1))

    def test_empty_query(self):
        res = search.search_phrase(self.con, "   ")
        self.assertEqual(res["verses"], 0)
        self.assertEqual(res["rows"], [])

    def test_lang_key_absent_when_empty(self):
        res = search.search_phrase(self.con, "")
        self.assertNotIn("lang", res)


def _make_audio_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE surahs (
            number INTEGER PRIMARY KEY, name_translit TEXT, name_ar TEXT,
            name_en TEXT, revelation TEXT, verses_count INTEGER);
        CREATE TABLE verses (sura INTEGER, aya INTEGER, text_simple TEXT);
        CREATE TABLE translations (
            id INTEGER PRIMARY KEY, key TEXT, author TEXT, language TEXT);
        CREATE TABLE translation_verses (
            sura INTEGER, aya INTEGER, translation_id INTEGER, text TEXT);
        """
    )
    con.execute("INSERT INTO surahs VALUES (1,'Al-Faatiha','الفاتحة','The Opening','Meccan',2)")
    con.execute("INSERT INTO surahs VALUES (2,'Al-Baqara','البقرة','The Cow','Medinan',1)")
    for sura, aya, txt in [(1, 1, "بسم الله"), (1, 2, "الحمد لله"), (2, 1, "الم")]:
        con.execute("INSERT INTO verses VALUES (?,?,?)", (sura, aya, txt))
    # Insert French reference translations
    con.execute("INSERT INTO translations VALUES (1, 'fr.hamidullah', 'Hamidullah', 'fr')")
    con.execute("INSERT INTO translations VALUES (2, 'fr.rashidmaash', 'Maash', 'fr')")
    con.execute("INSERT INTO translations VALUES (3, 'fr.montada', 'Montada', 'fr')")
    con.execute("INSERT INTO translations VALUES (4, 'en.sahih', 'Sahih', 'en')")
    # Translation verses for surah 1
    con.execute("INSERT INTO translation_verses VALUES (1, 1, 1, 'Au nom d''Allah')")
    con.execute("INSERT INTO translation_verses VALUES (1, 2, 1, 'Louange à Allah')")
    con.execute("INSERT INTO translation_verses VALUES (1, 1, 2, 'Au nom de Dieu')")
    con.execute("INSERT INTO translation_verses VALUES (1, 2, 2, 'La louange est à Dieu')")
    # Translation verses for surah 2
    con.execute("INSERT INTO translation_verses VALUES (2, 1, 1, 'Alif Lam Mim')")
    con.execute("INSERT INTO translation_verses VALUES (2, 1, 2, 'A. L. M.')")
    con.commit()
    return con


class TestSurahAudioStats(unittest.TestCase):
    def setUp(self):
        self.con = _make_audio_db()

    def tearDown(self):
        self.con.close()

    def test_covers_all_surahs(self):
        stats = search.surah_audio_stats(self.con)
        self.assertEqual([s["number"] for s in stats], [1, 2])

    def test_duration_positive_and_monotonic(self):
        stats = {s["number"]: s for s in search.surah_audio_stats(self.con)}
        self.assertGreater(stats[1]["seconds"], 0)
        self.assertGreater(stats[1]["seconds"], stats[2]["seconds"])

    def test_verses_count_present(self):
        stats = {s["number"]: s for s in search.surah_audio_stats(self.con)}
        self.assertEqual(stats[1]["verses_count"], 2)


if __name__ == "__main__":
    unittest.main()
