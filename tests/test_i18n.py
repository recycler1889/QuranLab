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


if __name__ == "__main__":
    unittest.main()