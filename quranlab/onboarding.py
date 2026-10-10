"""Tutoriel de première visite et guide de démarrage.

Fournit le contenu pédagogique de QuranLab (rôle de chaque onglet) sous trois
formes complémentaires, partageant le même jeu de données : une **modale** de
bienvenue ouverte à la première visite, un **bouton** réutilisable dans la barre
latérale, et un **accordéon** discret sous l'en-tête pour un rappel permanent.

Ce module ne contient que de la présentation : la clé de contenu ``SECTIONS``
suffit à tout régénérer.
"""

from __future__ import annotations

import streamlit as st

# --- Données du guide : un bloc par onglet ---------------------------------
SECTIONS = [
    {
        "key": "Racine",
        "label": "Racine",
        "desc": (
            "Indexation du corpus par **racine arabe** (trilitère ou "
            "quadrilitère) ou par **saisie bilingue** : un mot français est "
            "converti en racines candidates. Chaque résultat présente les "
            "versets, les formes rencontrées et un contexte réglable."
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
            "Recherche globale bilingue dans tout le texte. Le **compteur "
            "d'occurrences** s'affiche toujours en tête : nombre total "
            "d'occurrences et de versets, en union des racines (sans double "
            "comptage). Deux modes : **Français** (passerelle vers les "
            "racines) et **Arabe** (texte original)."
        ),
        "tips": [
            "Le compteur « N occurrence(s) dans Y verset(s) » est systématique.",
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
            "référence `sura:aya` ou d'un mot-clé, les versets **en miroir** "
            "par proximité de racines."
        ),
        "tips": [
            "Deux sélecteurs indépendants A et B pour la comparaison manuelle.",
            "Ajustez le seuil de racines communes pour resserrer ou élargir.",
        ],
    },
    {
        "key": "Thèmes",
        "label": "Thèmes",
        "desc": (
            "Explorez une **cartographie thématique** : chaque thème est ancré "
            "sur une ou plusieurs racines arabes, regroupé par catégorie. "
            "Filtrez par thème ou par catégorie et affichez le nombre de "
            "versets rattachés."
        ),
        "tips": [
            "La recherche plein texte couvre le libellé, la description, la "
            "racine et les termes associés.",
            "La vue d'ensemble liste tous les thèmes filtrés dans un tableau.",
        ],
    },
    {
        "key": "Idées reçues",
        "label": "Idées reçues",
        "desc": (
            "Analyse textuelle **descriptive** de controverses et d'idées "
            "reçues : récurrence lexicale, **polysémie** d'une racine (toutes "
            "ses formes et leurs contextes) et versets clés en arabe avec "
            "toutes les traductions. Aucun tafsir, aucune conclusion "
            "doctrinale."
        ),
        "tips": [
            "Chaque sujet expose sa question, sa note méthodologique et sa "
            "lecture conseillée.",
            "La polysémie déploie toutes les occurrences d'une racine.",
        ],
    },
    {
        "key": "Concordance",
        "label": "Concordance",
        "desc": (
            "Mettez les versets en relation par leurs **racines partagées** : "
            "« verset en miroir » d'une référence, ou concordance complète par "
            "racine ou terme arabe. « Le Coran s'explique par le Coran »."
        ),
        "tips": [
            "Le classement se fait par nombre de racines communes et taux de "
            "recouvrement.",
            "Choisissez le critère « Racine » ou « Terme arabe ».",
        ],
    },
]

INTRO = (
    "Outil **local** d'étude strictement intra-coranique. Toute recherche part "
    "du **texte arabe** (racine, morphologie) et s'éclaire par le Coran "
    "lui-même — sans tafsir, hadith ni interprétation post-coranique."
)

OUTRO = (
    "**Astuce** : chaque onglet ouvre sur une barre de recherche universelle "
    "qui accepte indifféremment le français **ou** l'arabe."
)

AUDIO = {
    "label": "Audio et lecture",
    "desc": (
        "Sous chaque verset, un **lecteur de récitation** permet d'écouter la "
        "lecture (Lecture/Pause, Arrêt) par le **récitateur** choisi dans la "
        "barre latérale. À côté de chaque **traduction** (française ou "
        "anglaise), un bouton **Lire** déclenche une **synthèse vocale** "
        "(moteur du navigateur) dans la langue de la traduction. Chaque verset "
        "et chaque traduction disposent de leur propre lecteur, totalement "
        "indépendant."
    ),
    "tips": [
        "Récitateur et lecteurs se règlent dans « Préférences › Audio ».",
        "La synthèse vocale suit la voix du système (fr-FR ou en-US), sans clé "
        "externe.",
    ],
}

SUGGESTIONS = (
    "**Suggestions d'amélioration** — QuranLab évolue au fil des usages. "
    "Idées, incohérences, sources à ajouter, nouveaux récitateurs ou langues, "
    "améliorations d'ergonomie : **faites-nous en part** par "
    "**kylemarks5522@gmail.com**."
)


# --- Rendu ----------------------------------------------------------------
def _section_block(sec: dict) -> None:
    st.markdown(f"**{sec['label']}** — {sec['desc']}")
    if sec.get("tips"):
        st.markdown(
            "".join(f"- {t}\n" for t in sec["tips"])
        )


def guide_body() -> None:
    """Contenu complet du guide (utilisé par la modale et l'accordéon)."""
    st.markdown(INTRO)
    for sec in SECTIONS:
        with st.expander(sec["label"], expanded=False):
            _section_block(sec)
    with st.expander(AUDIO["label"], expanded=False):
        _section_block(AUDIO)
    st.markdown(OUTRO)
    st.info(SUGGESTIONS)


def inline_guide() -> None:
    """Accordéon discret sous l'en-tête : guide accessible en permanence."""
    with st.expander("Guide de démarrage — rôle de chaque onglet", expanded=False):
        guide_body()


# --- Modale de bienvenue ---------------------------------------------------
def _close_dialog() -> None:
    st.session_state["ql_guide_open"] = False


@st.dialog(
    "Bienvenue dans QuranLab",
    width="large",
    on_dismiss=_close_dialog,
)
def _guide_dialog() -> None:
    st.caption(
        "Un rapide tour d'horizon avant de commencer. Réouvrable à tout moment "
        "depuis la barre latérale."
    )
    guide_body()
    col_go, col_later = st.columns([1, 1])
    if col_go.button(
        "Commencer l'exploration", type="primary", use_container_width=True
    ):
        st.session_state["ql_guide_open"] = False
        st.rerun()
    if col_later.button("Plus tard", use_container_width=True):
        st.session_state["ql_guide_open"] = False
        st.rerun()


def sidebar_guide_button() -> None:
    """Bouton de réouverture du guide (à placer dans la barre latérale)."""
    if st.button("Ouvrir le guide de démarrage", use_container_width=True):
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
    """Affiche la modale si elle est demandée (première visite ou bouton)."""
    if st.session_state.get("ql_guide_open"):
        _guide_dialog()
