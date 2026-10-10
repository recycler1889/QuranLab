"""Tutoriel de première visite et guide de démarrage (bilingue FR/EN).

Fournit le contenu pédagogique de QuranLab (rôle de chaque onglet) sous trois
formes complémentaires, partageant le même jeu de données : une **modale** de
bienvenue ouverte à la première visite, un **bouton** réutilisable dans la barre
latérale, et un **accordéon** discret sous l'en-tête pour un rappel permanent.

Le contenu suit la langue d'interface active (``i18n.lang()``) : tout est en
français **ou** en anglais, jamais un mélange.
"""

from __future__ import annotations

import streamlit as st

from . import i18n

# --- Contenu (français = référence ; anglais = traduction) ------------------
_CONTENT = {
    "fr": {
        "INTRO": (
            "Outil **local** d'étude strictement intra-coranique. Toute "
            "recherche part du **texte arabe** (racine, morphologie) et "
            "s'éclaire par le Coran lui-même — sans tafsir, hadith ni "
            "interprétation post-coranique."
        ),
        "OUTRO": (
            "**Astuce** : chaque onglet ouvre sur une barre de recherche "
            "universelle qui accepte indifféremment le français **ou** l'arabe."
        ),
        "AUDIO": {
            "label": "Audio et lecture",
            "desc": (
                "Sous chaque verset, un **lecteur de récitation** permet "
                "d'écouter la lecture (Lecture/Pause, Arrêt) par le "
                "**récitateur** choisi dans la barre latérale. À côté de chaque "
                "**traduction** (française ou anglaise), un bouton **Lire** "
                "déclenche une **synthèse vocale** (moteur du navigateur) dans "
                "la langue de la traduction. Chaque verset et chaque traduction "
                "disposent de leur propre lecteur, totalement indépendant."
            ),
            "tips": [
                "Récitateur et lecteurs se règlent dans « Préférences › Audio ».",
                "La synthèse vocale suit la voix du système (fr-FR ou en-US), "
                "sans clé externe.",
            ],
        },
        "SUGGESTIONS": (
            "**Suggestions d'amélioration** — QuranLab évolue au fil des "
            "usages. Idées, incohérences, sources à ajouter, nouveaux "
            "récitateurs ou langues, améliorations d'ergonomie : **faites-nous "
            "en part** par **kylemarks5522@gmail.com**."
        ),
        "SECTIONS": [
            {
                "key": "Racine",
                "label": "Racine",
                "desc": (
                    "Indexation du corpus par **racine arabe** (trilitère ou "
                    "quadrilitère) ou par **saisie bilingue** : un mot français "
                    "est converti en racines candidates. Chaque résultat "
                    "présente les versets, les formes rencontrées et un contexte "
                    "réglable."
                ),
                "tips": [
                    "Saisissez une racine en arabe (رحم) ou en Buckwalter (rHm).",
                    "Réglez le contexte (± versets) pour lire les versets voisins.",
                ],
            },
            {
                "key": "Recherche",
                "label": "Recherche",
                "desc": (
                    "Recherche globale bilingue dans tout le texte. Le "
                    "**compteur d'occurrences** s'affiche toujours en tête : "
                    "nombre total d'occurrences et de versets, en union des "
                    "racines (sans double comptage). Deux modes : **Français** "
                    "(passerelle vers les racines) et **Arabe** (texte original)."
                ),
                "tips": [
                    "Le compteur « N occurrence(s) dans Y verset(s) » est "
                    "systématique.",
                    "Le repli « occurrences dans les traductions » regroupe les "
                    "traductions contenant le terme.",
                ],
            },
            {
                "key": "Verset comparé",
                "label": "Verset comparé",
                "desc": (
                    "**Comparez deux versets** côte à côte (texte uthmani + "
                    "traductions plurielles) et faites ressortir leurs **racines "
                    "communes**. Le mode « Suggérer » retrouve, à partir d'une "
                    "référence `sura:aya` ou d'un mot-clé, les versets **en "
                    "miroir** par proximité de racines."
                ),
                "tips": [
                    "Deux sélecteurs indépendants A et B pour la comparaison "
                    "manuelle.",
                    "Ajustez le seuil de racines communes pour resserrer ou "
                    "élargir.",
                ],
            },
            {
                "key": "Thèmes",
                "label": "Thèmes",
                "desc": (
                    "Explorez une **cartographie thématique** : chaque thème est "
                    "ancré sur une ou plusieurs racines arabes, regroupé par "
                    "catégorie. Filtrez par thème ou par catégorie et affichez "
                    "le nombre de versets rattachés."
                ),
                "tips": [
                    "La recherche plein texte couvre le libellé, la description, "
                    "la racine et les termes associés.",
                    "La vue d'ensemble liste tous les thèmes filtrés dans un "
                    "tableau.",
                ],
            },
            {
                "key": "Idées reçues",
                "label": "Idées reçues",
                "desc": (
                    "Analyse textuelle **descriptive** de controverses et "
                    "d'idées reçues : récurrence lexicale, **polysémie** d'une "
                    "racine (toutes ses formes et leurs contextes) et versets "
                    "clés en arabe avec toutes les traductions. Aucun tafsir, "
                    "aucune conclusion doctrinale."
                ),
                "tips": [
                    "Chaque sujet expose sa question, sa note méthodologique et "
                    "sa lecture conseillée.",
                    "La polysémie déploie toutes les occurrences d'une racine.",
                ],
            },
            {
                "key": "Concordance",
                "label": "Concordance",
                "desc": (
                    "Mettez les versets en relation par leurs **racines "
                    "partagées** : « verset en miroir » d'une référence, ou "
                    "concordance complète par racine ou terme arabe. « Le Coran "
                    "s'explique par le Coran »."
                ),
                "tips": [
                    "Le classement se fait par nombre de racines communes et "
                    "taux de recouvrement.",
                    "Choisissez le critère « Racine » ou « Terme arabe ».",
                ],
            },
        ],
        "GUIDE_TITLE": "Guide de démarrage — rôle de chaque onglet",
        "WELCOME_TITLE": "Bienvenue dans QuranLab",
        "WELCOME_CAPTION": (
            "Un rapide tour d'horizon avant de commencer. Réouvrable à tout "
            "moment depuis la barre latérale."
        ),
        "BTN_START": "Commencer l'exploration",
        "BTN_LATER": "Plus tard",
        "BTN_OPEN": "Ouvrir le guide de démarrage",
    },
    "en": {
        "INTRO": (
            "A **local** tool for strictly intra-Qur'anic study. Every search "
            "starts from the **Arabic text** (root, morphology) and is "
            "illuminated by the Qur'an itself — without tafsir, hadith or "
            "post-Qur'anic interpretation."
        ),
        "OUTRO": (
            "**Tip**: every tab opens with a universal search bar that accepts "
            "French **or** Arabic alike."
        ),
        "AUDIO": {
            "label": "Audio and recitation",
            "desc": (
                "Under each verse, a **recitation player** lets you listen "
                "(Play/Pause, Stop) by the **reciter** chosen in the sidebar. "
                "Next to each **translation** (French or English), a **Read** "
                "button triggers **speech synthesis** (browser engine) in the "
                "language of the translation. Each verse and each translation "
                "has its own fully independent player."
            ),
            "tips": [
                "Reciter and players are configured in “Preferences › Audio”.",
                "Speech synthesis follows the system voice (fr-FR or en-US), "
                "with no external key.",
            ],
        },
        "SUGGESTIONS": (
            "**Improvement suggestions** — QuranLab evolves with use. Ideas, "
            "inconsistencies, sources to add, new reciters or languages, UX "
            "improvements: **share them with us** at "
            "**kylemarks5522@gmail.com**."
        ),
        "SECTIONS": [
            {
                "key": "Root",
                "label": "Root",
                "desc": (
                    "Indexing of the corpus by **Arabic root** (triliteral or "
                    "quadriliteral) or by **bilingual input**: a French word is "
                    "converted into candidate roots. Each result shows the "
                    "verses, the forms encountered and an adjustable context."
                ),
                "tips": [
                    "Enter a root in Arabic (رحم) or in Buckwalter (rHm).",
                    "Adjust the context (± verses) to read the neighbouring "
                    "verses.",
                ],
            },
            {
                "key": "Search",
                "label": "Search",
                "desc": (
                    "Bilingual global search across the whole text. The "
                    "**occurrence counter** is always shown at the top: total "
                    "number of occurrences and verses, as a union of roots (no "
                    "double counting). Two modes: **French** (bridge to roots) "
                    "and **Arabic** (original text)."
                ),
                "tips": [
                    "The counter “N occurrence(s) in Y verse(s)” is systematic.",
                    "The “occurrences in translations” accordion groups the "
                    "translations containing the term.",
                ],
            },
            {
                "key": "Compared verse",
                "label": "Compared verse",
                "desc": (
                    "**Compare two verses** side by side (Uthmani text + "
                    "multiple translations) and highlight their **shared "
                    "roots**. The “Suggest” mode finds, from a `sura:aya` "
                    "reference or a keyword, the **mirror** verses by root "
                    "proximity."
                ),
                "tips": [
                    "Two independent selectors A and B for the manual "
                    "comparison.",
                    "Adjust the shared-roots threshold to tighten or widen.",
                ],
            },
            {
                "key": "Themes",
                "label": "Themes",
                "desc": (
                    "Explore a **thematic mapping**: each theme is anchored on "
                    "one or more Arabic roots, grouped by category. Filter by "
                    "theme or by category and display the number of linked "
                    "verses."
                ),
                "tips": [
                    "The full-text search covers the label, description, root "
                    "and associated terms.",
                    "The overview lists all filtered themes in a table.",
                ],
            },
            {
                "key": "Misconceptions",
                "label": "Misconceptions",
                "desc": (
                    "**Descriptive** textual analysis of controversies and "
                    "misconceptions: lexical recurrence, **polysemy** of a root "
                    "(all its forms and their contexts) and key verses in Arabic "
                    "with all translations. No tafsir, no doctrinal conclusion."
                ),
                "tips": [
                    "Each topic exposes its question, its methodological note "
                    "and its suggested reading.",
                    "Polysemy unfolds every occurrence of a root.",
                ],
            },
            {
                "key": "Concordance",
                "label": "Concordance",
                "desc": (
                    "Relate verses by their **shared roots**: “mirror verse” of "
                    "a reference, or full concordance by Arabic root or term. "
                    "“The Qur'an explains itself by the Qur'an”."
                ),
                "tips": [
                    "Ranking is by number of shared roots and overlap ratio.",
                    "Choose the criterion “Root” or “Arabic term”.",
                ],
            },
        ],
        "GUIDE_TITLE": "Getting-started guide — role of each tab",
        "WELCOME_TITLE": "Welcome to QuranLab",
        "WELCOME_CAPTION": (
            "A quick overview before you start. Reopen it anytime from the "
            "sidebar."
        ),
        "BTN_START": "Start exploring",
        "BTN_LATER": "Later",
        "BTN_OPEN": "Open the getting-started guide",
    },
}

# Raccourci de compatibilité (contenu français de référence).
SECTIONS = _CONTENT["fr"]["SECTIONS"]


def _c() -> dict:
    """Contenu dans la langue d'interface active."""
    return _CONTENT.get(i18n.lang(), _CONTENT["fr"])


# --- Rendu ----------------------------------------------------------------
def _section_block(sec: dict) -> None:
    st.markdown(f"**{sec['label']}** — {sec['desc']}")
    if sec.get("tips"):
        st.markdown(
            "".join(f"- {t}\n" for t in sec["tips"])
        )


def guide_body() -> None:
    """Contenu complet du guide (utilisé par la modale et l'accordéon)."""
    c = _c()
    st.markdown(c["INTRO"])
    for sec in c["SECTIONS"]:
        with st.expander(sec["label"], expanded=False):
            _section_block(sec)
    with st.expander(c["AUDIO"]["label"], expanded=False):
        _section_block(c["AUDIO"])
    st.markdown(c["OUTRO"])
    st.info(c["SUGGESTIONS"])


def inline_guide() -> None:
    """Accordéon discret sous l'en-tête : guide accessible en permanence."""
    with st.expander(_c()["GUIDE_TITLE"], expanded=False):
        guide_body()


# --- Modale de bienvenue ---------------------------------------------------
def _close_dialog() -> None:
    st.session_state["ql_guide_open"] = False


def _dialog_body() -> None:
    c = _c()
    st.caption(c["WELCOME_CAPTION"])
    guide_body()
    col_go, col_later = st.columns([1, 1])
    if col_go.button(
        c["BTN_START"], type="primary", use_container_width=True
    ):
        st.session_state["ql_guide_open"] = False
        st.rerun()
    if col_later.button(c["BTN_LATER"], use_container_width=True):
        st.session_state["ql_guide_open"] = False
        st.rerun()


def sidebar_guide_button() -> None:
    """Bouton de réouverture du guide (à placer dans la barre latérale)."""
    if st.button(_c()["BTN_OPEN"], use_container_width=True):
        st.session_state["ql_guide_open"] = True
        st.rerun()


def init() -> None:
    """Initialise l'état et ouvre la modale à la **première** visite."""
    st.session_state.setdefault("ql_guide_seen", False)
    st.session_state.setdefault("ql_guide_open", False)
    if not st.session_state["ql_guide_seen"]:
        st.session_state["ql_guide_seen"] = True
        st.session_state["ql_guide_open"] = True


def render() -> None:
    """Affiche la modale si elle est demandée (première visite ou bouton).

    Le titre du dialogue est évalué **à l'exécution** (et non à l'import) afin
    de suivre la langue d'interface active, qui peut changer entre deux reruns.
    """
    if st.session_state.get("ql_guide_open"):
        st.dialog(
            _c()["WELCOME_TITLE"], width="large", on_dismiss=_close_dialog
        )(_dialog_body)()
