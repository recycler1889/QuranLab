"""Tests de l'état du guide de démarrage (modale fermée par défaut).

Régression : le tutoriel ne doit **plus** s'ouvrir automatiquement à la
première visite (ancien comportement ``ql_guide_open = True`` dans ``init``).
Il ne s'affiche que par le clic sur le bouton de la barre latérale.
"""

import unittest

from quranlab import onboarding


class _StubSt:
    """Faux module streamlit : état et bouton du guide uniquement."""

    def __init__(self):
        self.session_state = {}
        self._button_result = False
        self.rerun_called = False

    def button(self, *args, **kwargs):
        return self._button_result

    def rerun(self):
        self.rerun_called = True


class TestGuideClosedByDefault(unittest.TestCase):
    def setUp(self):
        self._orig_st = onboarding.st
        onboarding.st = _StubSt()
        self.stub = onboarding.st

    def tearDown(self):
        onboarding.st = self._orig_st

    def test_init_leaves_guide_closed_on_fresh_session(self):
        """Une session neuve (aucune clé) arrive **masquée** : ql_guide_open=False."""
        onboarding.init()
        self.assertFalse(onboarding.st.session_state.get("ql_guide_open"))

    def test_init_preserves_an_explicit_open(self):
        """Si le guide a déjà été demandé (clic), init ne le referme pas."""
        onboarding.st.session_state["ql_guide_open"] = True
        onboarding.init()
        self.assertTrue(onboarding.st.session_state["ql_guide_open"])

    def test_init_no_longer_sets_guide_seen_flag(self):
        """L'ancien drapeau « première visite » a disparu de l'état."""
        onboarding.init()
        self.assertNotIn("ql_guide_seen", onboarding.st.session_state)

    def test_sidebar_button_opens_the_guide(self):
        """Le clic sur le bouton latéral doit être la seule porte d'ouverture."""
        self.stub._button_result = True
        onboarding.sidebar_guide_button()
        self.assertTrue(onboarding.st.session_state["ql_guide_open"])
        self.assertTrue(self.stub.rerun_called)

    def test_sidebar_button_without_click_keeps_it_closed(self):
        """Sans clic, le guide reste fermé après le passage du bouton."""
        onboarding.init()
        self.stub._button_result = False
        onboarding.sidebar_guide_button()
        self.assertFalse(onboarding.st.session_state.get("ql_guide_open"))
        self.assertFalse(self.stub.rerun_called)

    def test_render_skips_dialog_when_closed(self):
        """render() ne déclenche aucun rendu quand la modale est fermée."""
        onboarding.init()
        try:
            onboarding.render()
        except Exception as exc:  # noqa: BLE001
            self.fail(
                f"render() a levé une exception alors que la modale devrait être masquée : {exc}"
            )


if __name__ == "__main__":
    unittest.main()