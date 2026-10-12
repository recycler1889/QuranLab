"""Tests des favoris (persistance JSON), sans toucher au fichier réel."""

import tempfile
import unittest
from pathlib import Path

from quranlab import bookmarks


class TestBookmarks(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = bookmarks._BOOKMARKS_PATH
        bookmarks._BOOKMARKS_PATH = Path(self._tmp.name) / "bookmarks.json"

    def tearDown(self):
        bookmarks._BOOKMARKS_PATH = self._orig
        self._tmp.cleanup()

    def test_empty_initially(self):
        self.assertEqual(bookmarks.count(), 0)
        self.assertEqual(bookmarks.all_entries(), [])

    def test_add_contains_remove(self):
        bookmarks.add(2, 255, "verset du Trône")
        self.assertTrue(bookmarks.contains(2, 255))
        self.assertEqual(bookmarks.count(), 1)
        entry = bookmarks.all_entries()[0]
        self.assertEqual((entry["sura"], entry["aya"]), (2, 255))
        self.assertEqual(entry["note"], "verset du Trône")
        bookmarks.remove(2, 255)
        self.assertFalse(bookmarks.contains(2, 255))

    def test_toggle(self):
        self.assertTrue(bookmarks.toggle(1, 1))   # ajouté
        self.assertTrue(bookmarks.contains(1, 1))
        self.assertFalse(bookmarks.toggle(1, 1))  # retiré
        self.assertFalse(bookmarks.contains(1, 1))

    def test_set_note(self):
        bookmarks.add(4, 34)
        bookmarks.set_note(4, 34, "patience")
        self.assertEqual(bookmarks.all_entries()[0]["note"], "patience")

    def test_sorted_by_reference(self):
        bookmarks.add(3, 5)
        bookmarks.add(1, 1)
        bookmarks.add(2, 255)
        refs = [(e["sura"], e["aya"]) for e in bookmarks.all_entries()]
        self.assertEqual(refs, [(1, 1), (2, 255), (3, 5)])

    def test_clear(self):
        bookmarks.add(1, 1)
        bookmarks.clear()
        self.assertEqual(bookmarks.count(), 0)

    def test_load_renvoie_une_copie(self):
        bookmarks.add(1, 1)
        data = bookmarks.load()
        data["9:9"] = {"sura": 9, "aya": 9, "note": "", "added": ""}
        self.assertFalse(bookmarks.contains(9, 9))

    def test_cache_invalide_sur_modification_externe(self):
        import json
        bookmarks.add(1, 1)
        self.assertTrue(bookmarks.contains(1, 1))
        path = bookmarks._path()
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["2:2"] = {"sura": 2, "aya": 2, "note": "", "added": ""}
        path.write_text(json.dumps(raw), encoding="utf-8")
        self.assertTrue(bookmarks.contains(2, 2))


if __name__ == "__main__":
    unittest.main()
