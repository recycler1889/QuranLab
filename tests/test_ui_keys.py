"""Tests des clés de widgets (unicité par occurrence, stabilité entre reruns).

Régression : le même verset rendu dans plusieurs onglets (Lire + Favoris) au
même rerun produisait des clés identiques et faisait planter Streamlit
(``StreamlitDuplicateElementKey``). ``unique_key`` ajoute un indice d'occurrence
par run, remis à zéro par ``begin_run()``.
"""

import unittest

from quranlab import ui


class _StubSt:
    """Faux ``streamlit`` minimal : juste un ``session_state`` de type dict."""

    def __init__(self) -> None:
        self.session_state: dict = {}


class TestUniqueKey(unittest.TestCase):
    def setUp(self):
        self._orig = ui.st
        ui.st = _StubSt()

    def tearDown(self):
        ui.st = self._orig

    def test_first_occurrence_is_bare_seed(self):
        ui.begin_run()
        self.assertEqual(ui.unique_key("verse_1_1"), "verse_1_1")

    def test_duplicates_get_distinct_keys(self):
        ui.begin_run()
        k1 = ui.unique_key("verse_1_1")
        k2 = ui.unique_key("verse_1_1")
        self.assertNotEqual(k1, k2)
        self.assertEqual((k1, k2), ("verse_1_1", "verse_1_1#1"))

    def test_keys_are_stable_across_runs(self):
        """Mêmes appels dans un nouveau run -> mêmes clés (matching du clic)."""
        ui.begin_run()
        run1 = (ui.unique_key("verse_2_255"), ui.unique_key("verse_2_255"))
        ui.begin_run()
        run2 = (ui.unique_key("verse_2_255"), ui.unique_key("verse_2_255"))
        self.assertEqual(run1, run2)

    def test_distinct_seeds_do_not_interfere(self):
        ui.begin_run()
        self.assertEqual(ui.unique_key("a"), "a")
        self.assertEqual(ui.unique_key("b"), "b")
        self.assertEqual(ui.unique_key("a"), "a#1")


if __name__ == "__main__":
    unittest.main()
