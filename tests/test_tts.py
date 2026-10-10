"""Tests du moteur de synthèse vocale (choix de voix + fournisseur externe)."""

import unittest

from quranlab import config, ui


class TestVoiceJs(unittest.TestCase):
    def test_lang_tag_is_quoted(self):
        """__LG__ doit produire un littéral JS, pas un identifiant (sinon ReferenceError)."""
        for lg in ("fr", "en"):
            js = ui._tts_voice_js(lg)
            self.assertIn(f'indexOf("{lg}")', js, f"lang non quotée pour {lg}")

    def test_ls_key_is_quoted(self):
        """La clé localStorage doit être une chaîne littérale dans getItem()."""
        for lg in ("fr", "en"):
            js = ui._tts_voice_js(lg)
            self.assertIn(f'getItem("ql_tts_voice_{lg}")', js)

    def test_template_placeholders_resolved(self):
        for lg in ("fr", "en"):
            self.assertNotIn("__LG__", ui._tts_voice_js(lg))
            self.assertNotIn("__SUBS__", ui._tts_voice_js(lg))
            self.assertNotIn("__PREFS__", ui._tts_voice_js(lg))
            self.assertNotIn("__LS_KEY__", ui._tts_voice_js(lg))

    def test_prefers_natural_and_online_voices(self):
        fr = ui._LG_PREFS["fr"]
        self.assertIn("natural", fr[:3])
        self.assertIn("neural", fr[:3])


class TestExternalProvider(unittest.TestCase):
    def setUp(self):
        self._orig = config.TTS_HTTP_URL

    def tearDown(self):
        config.TTS_HTTP_URL = self._orig

    def test_disabled_by_default(self):
        self.assertEqual(config.TTS_HTTP_URL, "")
        self.assertEqual(ui._tts_external_url("Bonjour", "fr-FR"), "")

    def test_substitutes_and_encodes(self):
        config.TTS_HTTP_URL = "http://x/api?lang={lang}&text={text}"
        out = ui._tts_external_url("le texte & le reste", "fr-FR")
        self.assertEqual(out, "http://x/api?lang=fr-FR&text=le%20texte%20%26%20le%20reste")

    def test_lang_encoded(self):
        config.TTS_HTTP_URL = "{lang}/{text}"
        out = ui._tts_external_url("mot", "fr-FR")
        self.assertEqual(out, "fr-FR/mot")


if __name__ == "__main__":
    unittest.main()
