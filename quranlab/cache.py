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