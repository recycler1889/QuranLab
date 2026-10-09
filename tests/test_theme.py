"""Tests des générateurs SVG et de la feuille de style des thèmes visuels."""

import unittest

from quranlab import theme


class TestThemeSvg(unittest.TestCase):
    def test_ornament_has_no_literal_placeholder(self):
        # Régression : la ligne <circle> doit interpoller {color}, pas l'afficher.
        svg = theme._ornament_svg("#0B6E4F")
        self.assertNotIn("{color}", svg)
        self.assertNotIn("%7Bcolor%7D", svg)

    def test_mosaic_has_no_literal_placeholder(self):
        svg = theme._mosaic_svg("#0B6E4F", "0.06")
        for placeholder in ("{color}", "%7Bcolor%7D", "{opacity}", "%7Bopacity%7D"):
            self.assertNotIn(placeholder, svg)

    def test_css_exposes_palette_variables(self):
        css = theme.css("Clair")
        self.assertIn("--ql-bg", css)
        self.assertIn("--ql-accent", css)
        self.assertIn(theme.PALETTES["Clair"]["accent"], css)
        self.assertNotIn("{color}", css)

    def test_css_falls_back_to_default(self):
        self.assertEqual(theme.css("Inconnu"), theme.css(theme.DEFAULT))


if __name__ == "__main__":
    unittest.main()
