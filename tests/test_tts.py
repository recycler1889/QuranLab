"""Tests du moteur de synthèse vocale (choix de voix + fournisseur externe)."""

import unittest

from quranlab import config, i18n, tts, ui


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


class TestPiperVoices(unittest.TestCase):
    def test_four_or_more_french_voices(self):
        vs = config.piper_voices("fr")
        self.assertGreaterEqual(len(vs), 4, "au moins 4 voix françaises")
        for v in vs:
            self.assertTrue(v["voice"].startswith("fr_FR"))
            self.assertEqual(config.piper_voice_name(v["key"], "fr"), v["voice"])

    def test_default_and_fallback(self):
        first = config.piper_voices("fr")[0]["voice"]
        self.assertEqual(config.piper_voice_name("inexistant", "fr"), first)

    def test_en_voices_are_distinct_from_fr(self):
        en = config.piper_voices("en")
        self.assertGreaterEqual(len(en), 2)
        self.assertTrue(all(v["voice"].startswith("en_US") for v in en))
        self.assertNotEqual(en[0]["voice"], config.piper_voices("fr")[0]["voice"])


class TestEngineSelection(unittest.TestCase):
    def setUp(self):
        self._prov = config.TTS_PROVIDER
        self._avail = ui.tts_mod.available

    def tearDown(self):
        config.TTS_PROVIDER = self._prov
        ui.tts_mod.available = self._avail

    def test_forced_browser(self):
        config.TTS_PROVIDER = "browser"
        ui.tts_mod.available = lambda: True
        self.assertEqual(ui._tts_engine("fr"), "browser")

    def test_auto_prefers_piper(self):
        config.TTS_PROVIDER = "auto"
        ui.tts_mod.available = lambda: True
        self.assertEqual(ui._tts_engine("fr"), "piper")

    def test_auto_without_piper_falls_back(self):
        config.TTS_PROVIDER = "auto"
        ui.tts_mod.available = lambda: False
        self.assertEqual(ui._tts_engine("fr"), "browser")


class TestPiperModule(unittest.TestCase):
    def test_available_returns_bool(self):
        self.assertIsInstance(tts.available(), bool)

    def test_model_path_is_onnx(self):
        self.assertTrue(str(tts.model_path("fr_FR-siwis-medium")).endswith(".onnx"))

    def test_empty_text_is_empty_bytes(self):
        self.assertEqual(tts.synthesize_wav("", "fr_FR-siwis-medium"), b"")
        self.assertEqual(tts.synthesize_wav("   ", "fr_FR-siwis-medium"), b"")


class TestPiperI18n(unittest.TestCase):
    KEYS = (
        "ui.piper_engine",
        "ui.piper_voice",
        "ui.piper_voice_help",
        "ui.piper_first_use",
        "ui.piper_unavailable",
        "ui.tts_generating",
        "ui.tts_fail",
    )

    def test_keys_present_in_both_languages(self):
        fr = i18n.keys_fr()
        en = i18n.keys_en()
        for k in self.KEYS:
            self.assertIn(k, fr, f"{k} manquant en FR")
            self.assertIn(k, en, f"{k} manquant en EN")

    def test_fail_message_formats(self):
        self.assertIn("boom", i18n.t("ui.tts_fail", err="boom"))


if __name__ == "__main__":
    unittest.main()
