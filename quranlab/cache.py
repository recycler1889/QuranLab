"""Couche de mise en cache Streamlit pour les requêtes partagées.

Les modules purs (``search``, ``vocab``) restent testables sans Streamlit ;
les wrappers ``st.cache_data`` vivent ici pour ne pas rejouer les mêmes
requêtes SQL à chaque rendu (onglets Lire / Apprendre / Quiz). Les imports
sont locaux (même motif que ``learning.py``) pour éviter tout cycle d'imports.
"""

from __future__ import annotations

import sqlite3

import streamlit as st


def _connection_hash(con: sqlite3.Connection) -> int:
    """Hachage de la connexion unique par identité (check_same_thread=False)."""
    return id(con)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def frequent_roots_cached(con: sqlite3.Connection, top_n: int,
                          lang: str = "fr") -> list:
    from . import vocab
    return vocab.frequent_roots(con, top_n, lang)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def frequent_lemmas_cached(con: sqlite3.Connection, top_n: int) -> list:
    from . import vocab
    return vocab.frequent_lemmas(con, top_n)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def frequent_words_cached(con: sqlite3.Connection, top_n: int,
                          lang: str = "fr") -> list:
    from . import vocab
    return vocab.frequent_words(con, top_n, lang)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def surah_list_cached(con: sqlite3.Connection) -> list:
    from . import search
    return search.surah_list(con)


# --- Recherches (rejouées à chaque rendu Streamlit sans cache) -------------
@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def search_arabic_cached(con: sqlite3.Connection, query: str,
                         limit: int = 100) -> list:
    from . import search
    return search.search_arabic(con, query, limit=limit)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def search_french_cached(con: sqlite3.Connection, query: str, limit: int = 100,
                         translation_key: str | None = None) -> list:
    from . import search
    return search.search_french(con, query, limit=limit,
                                translation_key=translation_key)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def search_root_cached(con: sqlite3.Connection, root_input: str,
                       limit: int = 1000, with_context: int = 0) -> dict:
    from . import search
    return search.search_root(con, root_input, limit=limit,
                              with_context=with_context)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def verses_bundle_cached(con: sqlite3.Connection, refs: tuple) -> dict:
    from . import search
    refs = tuple(tuple(r) for r in refs)
    return search.verses_bundle(con, refs)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def french_bridge_cached(con: sqlite3.Connection, query: str) -> dict:
    from . import search
    return search.french_bridge(con, query)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def theme_cached(con: sqlite3.Connection, name: str, limit: int = 500,
                 lang: str = "fr") -> dict:
    from . import search
    return search.theme(con, name, limit=limit, lang=lang)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def controversy_cached(con: sqlite3.Connection, name: str, limit: int = 500,
                       lang: str = "fr") -> dict:
    from . import search
    return search.controversy(con, name, limit=limit, lang=lang)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def concordance_cached(con: sqlite3.Connection, root: str | None = None,
                       term: str | None = None, limit: int = 300) -> dict:
    from . import search
    return search.concordance(con, root=root, term=term, limit=limit)


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: _connection_hash})
def occurrence_summary_cached(con: sqlite3.Connection, query: str) -> dict | None:
    """Bilan bilingue d'une requête (mot/racine FR ou AR) — onglets recherche."""
    from . import ui
    return ui.occurrence_summary(con, query)