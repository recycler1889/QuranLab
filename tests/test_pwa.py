"""Tests de l'habillage PWA (manifeste, icônes, injection d'en-tête)."""

import json
import unittest

from PIL import Image

from quranlab import pwa


class TestManifest(unittest.TestCase):
    def test_manifest_is_valid_json(self):
        path = pwa.STATIC_DIR / "manifest.webmanifest"
        self.assertTrue(path.exists(), "manifest.webmanifest absent")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

    def test_manifest_required_fields(self):
        data = json.loads(
            (pwa.STATIC_DIR / "manifest.webmanifest").read_text(encoding="utf-8")
        )
        for key in ("name", "short_name", "start_url", "display", "icons"):
            self.assertIn(key, data)
        self.assertEqual(data["display"], "standalone")
        self.assertTrue(data["start_url"].startswith("/"))

    def test_manifest_has_required_icon_sizes(self):
        data = json.loads(
            (pwa.STATIC_DIR / "manifest.webmanifest").read_text(encoding="utf-8")
        )
        sizes = {i["sizes"] for i in data["icons"]}
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)
        purposes = {i.get("purpose") for i in data["icons"]}
        self.assertIn("maskable", purposes)


class TestIcons(unittest.TestCase):
    def test_all_icons_exist_and_are_png(self):
        for name, size, _motif, _rounded, _transparent in pwa.ICON_SPECS:
            path = pwa.ICONS_DIR / name
            self.assertTrue(path.exists(), f"icône absente : {name}")
            with Image.open(path) as im:
                self.assertEqual(im.format, "PNG")
                self.assertEqual(im.size, (size, size))

    def test_ensure_assets_idempotent(self):
        pwa.ensure_assets()
        pwa.ensure_assets()
        self.assertTrue((pwa.STATIC_DIR / "manifest.webmanifest").exists())


class TestHeadScript(unittest.TestCase):
    def test_injection_points_to_manifest_and_icons(self):
        script = pwa._head_script("#123456")
        self.assertIn("manifest.webmanifest", script)
        self.assertIn("icons/apple-touch-icon.png", script)
        self.assertIn("#123456", script)
        self.assertIn("app/static/", script)

    def test_page_icon_path_resolves_to_existing_file(self):
        result = pwa.page_icon_path()
        if result != "📖":
            self.assertTrue((pwa.ROOT / result).exists())


if __name__ == "__main__":
    unittest.main()
