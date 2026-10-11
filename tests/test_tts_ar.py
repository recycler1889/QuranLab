"""Tests de la synthèse vocale arabe (locale, gabarit JS, clés i18n).

La fonction ``ui.tts_arabic`` s'appuie sur la Web Speech API du navigateur :
on vérifie ici sa configuration (locale ``ar-SA``), le gabarit JS de choix de
voix pour l'arabe et la présence des clés d'interface correspondantes.
"""

import unittest

from quranlab import config, i18n, ui


class TestTtsArabe(unittest.TestCase):
    def test_locale_arabe(self):
        self.assertEqual(config.tts_locale("ar"), "ar-SA")
        self.assertEqual(config.tts_locale("fr"), "fr-FR")
        self.assertEqual(config.tts_locale("en"), "en-US")

    def test_gabarit_voix_arabe(self):
        js = ui._tts_voice_js("ar")
        self.assertNotIn("__LG__", js)
        self.assertIn("ql_tts_voice_ar", js)
        self.assertIn('"ar"', js)

    def test_maps_voix_arabe(self):
        self.assertEqual(ui._LG_MATCH["ar"], "ar")
        self.assertTrue(ui._LG_SUBS["ar"])
        self.assertTrue(ui._LG_PREFS["ar"])

    def test_cles_i18n_ecouter(self):
        for key in ("iqra.listen", "iqra.listen_ar", "iqra.step6",
                    "iqra.num_title"):
            self.assertIn(key, i18n.keys_fr())
            self.assertIn(key, i18n.keys_en())


if __name__ == "__main__":
    unittest.main()