"""Tutoriel de démarrage et guide (bilingue FR/EN).

Fournit le contenu pédagogique de QuranLab (rôle de chaque onglet) sous trois
formes complémentaires, partageant le même jeu de données : une **modale**
ouverte **uniquement** par le bouton de la barre latérale (jamais
automatiquement à l'arrivée), ce même **bouton** réutilisable dans la barre
latérale, et un **accordéon** discret sous l'en-tête pour un rappel permanent.

Le contenu suit la langue d'interface active (``i18n.lang()``) : tout est en
français **ou** en anglais, jamais un mélange.
"""

from __future__ import annotations

import streamlit as st

from . import config, i18n

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
            f"en part** par **{config.SUGGESTIONS_EMAIL}**."
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
            {
                "key": "Référence",
                "label": "Recherche par référence",
                "desc": (
                    "Dans la barre de recherche universelle, saisissez "
                    "directement une **référence de verset** : `2:255`, "
                    "`2.255`, `2/255` ou `2 255` ouvrent le verset (sourate 2, "
                    "verset 255). Les séparateurs `:`, `.`, `/` et l'espace "
                    "sont équivalents."
                ),
                "tips": [
                    "Formats acceptés : `36:1`, `36.1`, `36/1`, `36 1`.",
                    "La référence ouvre le verset dans l'onglet Lire, au bon "
                    "endroit.",
                ],
            },
            {
                "key": "Favoris",
                "label": "Favoris",
                "desc": (
                    "L'onglet **Favoris** rassemble tous les versets mis de "
                    "côté : gestion **centralisée** (consultation, "
                    "suppression, export) et bouton de favori sous chaque "
                    "verset pour ajouter ou retirer d'un clic."
                ),
                "tips": [
                    "Le bouton sous un verset l'ajoute aux favoris.",
                    "Les favoris restent locaux à votre installation.",
                ],
            },
            {
                "key": "Apprendre l'arabe",
                "label": "Apprendre l'arabe (Iqra)",
                "desc": (
                    "Parcours progressif de l'onglet **Apprendre** : "
                    "**alphabet** (28 lettres et formes), **voyelles** et "
                    "**signes**, **lecture**, **vocabulaire essentiel** (les "
                    "500 mots les plus fréquents du Coran), **nombres** (de 1 "
                    "à 1000) et les **99 Noms d'Allah**. Chaque élément porte "
                    "un bouton **Écouter** (synthèse vocale arabe)."
                ),
                "tips": [
                    "Sept étapes navigables dans le parcours Iqra.",
                    "La synthèse vocale arabe suit la voix du navigateur.",
                    "À l'étape alphabet, un mode **mélangé** réaffiche les "
                    "lettres dans un ordre aléatoire (révision) ; un bouton "
                    "revient à l'ordre traditionnel.",
                ],
            },
            {
                "key": "99 Noms",
                "label": "Les 99 Noms d'Allah",
                "desc": (
                    "Dernière étape du parcours Iqra : les **99 Noms** (Asmāʾ "
                    "Allāh al-Ḥusnā) en cartes — calligraphie arabe, "
                    "translittération, traduction directe, **racine** et "
                    "**sens lexicographique** de cette racine (étymologie, "
                    "sans exégèse), avec écoute de la prononciation et filtre."
                ),
                "tips": [
                    "Filtrez par arabe, translittération, sens ou racine.",
                    "Un clic sur « Écouter » donne la prononciation arabe du "
                    "Nom.",
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
            f"**{config.SUGGESTIONS_EMAIL}**."
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
            {
                "key": "Reference",
                "label": "Reference search",
                "desc": (
                    "In the universal search bar, type a **verse reference** "
                    "directly: `2:255`, `2.255`, `2/255` or `2 255` open the "
                    "verse (surah 2, verse 255). The separators `:`, `.`, `/` "
                    "and space are equivalent."
                ),
                "tips": [
                    "Accepted formats: `36:1`, `36.1`, `36/1`, `36 1`.",
                    "The reference opens the verse in the Read tab, at the "
                    "right place.",
                ],
            },
            {
                "key": "Bookmarks",
                "label": "Bookmarks",
                "desc": (
                    "The **Bookmarks** tab gathers every saved verse: "
                    "**centralised** management (browse, remove, export) plus "
                    "a bookmark button under each verse to add or remove in "
                    "one click."
                ),
                "tips": [
                    "The button under a verse adds it to bookmarks.",
                    "Bookmarks stay local to your installation.",
                ],
            },
            {
                "key": "Learn Arabic",
                "label": "Learn Arabic (Iqra)",
                "desc": (
                    "A progressive course in the **Learn** tab: **alphabet** "
                    "(28 letters and forms), **vowels** and **signs**, "
                    "**reading**, **essential vocabulary** (the 500 most "
                    "frequent words of the Qur'an), **numbers** (1 to 1000) "
                    "and the **99 Names of Allah**. Every item has a "
                    "**Listen** button (Arabic speech synthesis)."
                ),
                "tips": [
                    "Seven navigable steps in the Iqra course.",
                    "Arabic speech synthesis follows the browser voice.",
                    "In the alphabet step, a **shuffled** mode redisplays the "
                    "letters in random order (revision); a button restores the "
                    "traditional order.",
                ],
            },
            {
                "key": "99 Names",
                "label": "The 99 Names of Allah",
                "desc": (
                    "Final step of the Iqra course: the **99 Names** (Asmāʾ "
                    "Allāh al-Ḥusnā) as cards — Arabic calligraphy, "
                    "transliteration, direct translation, **root** and the "
                    "**lexicographic meaning** of that root (etymology, no "
                    "exegesis), with pronunciation playback and a filter."
                ),
                "tips": [
                    "Filter by Arabic, transliteration, meaning or root.",
                    "One click on “Listen” gives the Arabic pronunciation of "
                    "the Name.",
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
        c["BTN_START"], type="primary", use_container_width=True,
        key="ql_guide_start_btn",
    ):
        st.session_state["ql_guide_open"] = False
        st.rerun()
    if col_later.button(
        c["BTN_LATER"], use_container_width=True, key="ql_guide_later_btn"
    ):
        st.session_state["ql_guide_open"] = False
        st.rerun()


def sidebar_guide_button() -> None:
    """Bouton de réouverture du guide (à placer dans la barre latérale)."""
    if st.button(
        _c()["BTN_OPEN"], use_container_width=True, key="ql_guide_reopen_btn"
    ):
        st.session_state["ql_guide_open"] = True
        st.rerun()


def init() -> None:
    """Initialise l'état du guide : **masqué par défaut**.

    Contrairement à l'ancien comportement, la modale ne **s'ouvre plus
    automatiquement** à la première visite. Elle ne s'affiche que lorsque
    l'utilisateur clique explicitement sur le bouton de la barre latérale
    (``sidebar_guide_button``), ce qui positionne ``ql_guide_open`` à True.
    """
    st.session_state.setdefault("ql_guide_open", False)


def render() -> None:
    """Affiche la modale si elle est demandée (clic sur le bouton latéral).

    Le titre du dialogue est évalué **à l'exécution** (et non à l'import) afin
    de suivre la langue d'interface active, qui peut changer entre deux reruns.
    """
    if st.session_state.get("ql_guide_open"):
        st.dialog(
            _c()["WELCOME_TITLE"], width="large", on_dismiss=_close_dialog
        )(_dialog_body)()
