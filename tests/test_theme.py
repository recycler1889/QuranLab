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

    def test_css_defines_shared_card_component(self):
        css = theme.css("Clair")
        self.assertIn(".ql-card", css)
        self.assertIn(".ql-card:hover", css)
        self.assertIn("box-shadow", css)
        for part in (".ql-ar", ".ql-name", ".ql-tr", ".ql-gloss", ".ql-meta",
                     ".ql-forms", ".ql-badge", ".ql-sep"):
            self.assertIn(part, css)

    def test_css_has_responsive_rules(self):
        css = theme.css("Sombre")
        self.assertIn("@media (max-width: 780px)", css)
        self.assertIn("@media (max-width: 420px)", css)
        self.assertIn("stMainBlockContainer", css)

    def test_css_exposes_gold_accent(self):
        for name in theme.ORDER:
            css = theme.css(name)
            self.assertIn("--ql-gold", css)
            self.assertIn(theme.PALETTES[name]["gold"], css)

    def test_css_defines_verse_anchors(self):
        css = theme.css("Clair")
        for part in (".ql-verse-anchor", ".ql-verse-ref", ".ql-ref-num",
                     ".ql-verse-ar", ".ql-target"):
            self.assertIn(part, css)

    def test_dark_accent_is_muted_forest_green(self):
        # Le vert du thème sombre doit rester mat/désaturé (pas de vert vif).
        accent = theme.PALETTES["Sombre"]["accent"].lstrip("#")
        r, g, b = (int(accent[i:i + 2], 16) for i in (0, 2, 4))
        self.assertGreater(g, r)          # dominante verte
        self.assertLess(g - b, 120)       # pas saturé à l'extrême
        self.assertLess(g, 170)           # sombre, non éblouissant

    def test_light_bg_is_not_pure_white(self):
        bg = theme.PALETTES["Clair"]["bg"].lstrip("#")
        self.assertNotEqual(bg.lower(), "ffffff")
        r, g, b = (int(bg[i:i + 2], 16) for i in (0, 2, 4))
        self.assertLess(max(r, g, b), 250)  # ivoire, jamais blanc pur

    def test_css_defines_thick_active_tab_indicator(self):
        # L'indicateur d'onglet actif doit être épais et contrasté.
        for name in theme.ORDER:
            css = theme.css(name)
            self.assertIn('[data-baseweb="tab-highlight"]', css)
            self.assertIn("height: 4px", css)
            self.assertIn("linear-gradient(", css)


if __name__ == "__main__":
    unittest.main()
