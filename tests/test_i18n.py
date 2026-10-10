"""Tests du support i18n FR/EN (parité des catalogues + filtrage des versets)."""

import unittest

from quranlab import i18n, ui


class TestCatalogs(unittest.TestCase):
    def test_parity_fr_en(self):
        """Toute clé anglaisée doit exister en français et vice-versa (aucun plantage en EN)."""
        fr, en = i18n.keys_fr(), i18n.keys_en()
        self.assertEqual(fr, en, "les catalogues FR et EN doivent être identiques")

    def test_translation_has_placeholders_preserved(self):
        """La traduction formate correctement les paramètres nommés."""
        self.assertEqual(i18n.t("ui.counter", n=3, v=2), "3 occurrence(s) trouvée(s) dans 2 verset(s)")

    def test_format_missing_arg_returns_text(self):
        """Un paramètre manquant ne fait pas planter t()."""
        out = i18n.t("ui.counter")
        self.assertIn("occurrence", out)


class TestTranslationFiltering(unittest.TestCase):
    def _set(self, lg):
        i18n.set_lang(lg)

    def test_filters_to_french_by_default(self):
        i18n.set_lang("fr")
        out = ui.translations_for_lang(
            [{"language": "fr", "text": "a"}, {"language": "en", "text": "b"}]
        )
        self.assertEqual([x["text"] for x in out], ["a"])

    def test_filters_to_english_when_en(self):
        i18n.set_lang("en")
        out = ui.translations_for_lang(
            [{"language": "fr", "text": "a"}, {"language": "en", "text": "b"}]
        )
        self.assertEqual([x["text"] for x in out], ["b"])

    def test_fallback_to_all_when_lang_missing(self):
        i18n.set_lang("en")
        out = ui.translations_for_lang([{"language": "ar", "text": "a"}])
        self.assertEqual([x["text"] for x in out], ["a"])


class TestLanguageName(unittest.TestCase):
    def test_lang_name_is_never_a_raw_key(self):
        """ui.lang.<code> doit être traduit dans les deux sens (rétroaction)."""
        for lg in ("fr", "en"):
            i18n.set_lang(lg)
            name = ui._lang_name(lg)
            self.assertNotIn(
                "ui.lang", name, f"_lang_name('{lg}') a renvoyé une clé brute"
            )
            self.assertTrue(name.strip(), f"_lang_name('{lg}') vide")

    def test_lang_name_default_follows_selector(self):
        i18n.set_lang("fr")
        self.assertEqual(ui._lang_name(), ui._lang_name("fr"))


if __name__ == "__main__":
    unittest.main()