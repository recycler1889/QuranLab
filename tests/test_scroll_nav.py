"""Tests du widget flottant de navigation rapide (remonter / descendre).

Le composant ``ui.scroll_nav`` s'exécute dans une iframe de composant (même
origine) et injecte le widget dans le document parent Streamlit. On teste ici le
gabarit HTML/JS produit (``ui._scroll_nav_html``) : présence du conteneur, des
deux boutons, du défilement fluide et des cibles robustes.
"""

import unittest

from quranlab import ui


class TestScrollNavHtml(unittest.TestCase):
    def test_contains_widget_container_and_both_buttons(self):
        html = ui._scroll_nav_html()
        self.assertIn("ql-scroll-nav", html)
        self.assertIn("ql-scroll-up", html)
        self.assertIn("ql-scroll-down", html)
        # glyphes flèche haut / bas
        self.assertIn("\\u2191", html)
        self.assertIn("\\u2193", html)

    def test_scrolls_smoothly_to_top_and_bottom(self):
        html = ui._scroll_nav_html()
        self.assertIn("scrollTo", html)
        self.assertIn("behavior:'smooth'", html)
        self.assertIn("scrollHeight", html)

    def test_targets_streamlit_scroll_container(self):
        html = ui._scroll_nav_html()
        self.assertIn("stAppViewContainer", html)
        self.assertIn("scrollingElement", html)

    def test_operates_on_parent_document(self):
        html = ui._scroll_nav_html()
        self.assertIn("window.parent", html)

    def test_is_idempotent_on_rerun(self):
        html = ui._scroll_nav_html()
        # l'ancien widget est retiré avant recréation
        self.assertIn("getElementById('ql-scroll-nav')", html)
        self.assertIn("removeChild", html)

    def test_visibility_toggle_exists(self):
        html = ui._scroll_nav_html()
        self.assertIn("ql-visible", html)

    def test_labels_follow_interface_language(self):
        from quranlab import i18n

        i18n.set_lang("fr")
        fr = ui._scroll_nav_html()
        self.assertIn(ui.t("ui.scroll_top"), fr)
        i18n.set_lang("en")
        en = ui._scroll_nav_html()
        self.assertIn(ui.t("ui.scroll_top"), en)
        self.assertNotEqual(fr, en)


if __name__ == "__main__":
    unittest.main()
