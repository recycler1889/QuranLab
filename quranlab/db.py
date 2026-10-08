"""Accès à la base SQLite."""

import sqlite3
from pathlib import Path

from . import config


def connect(
    db_path: Path = config.DB_PATH, check_same_thread: bool = False
) -> sqlite3.Connection:
    """Ouvre une connexion SQLite.

    ``check_same_thread=False`` est nécessaire pour Streamlit : la connexion
    mise en cache (``@st.cache_resource``) est créée dans un thread et réutilisée
    dans d'autres threads (un par session / rerun). SQLite est ici compilé en
    mode sérialisé (``sqlite3.threadsafety == 3``), donc le partage est sûr.
    La base est utilisée en lecture seule par l'application.
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"Base introuvable : {db_path}\n"
            "Lancez d'abord :  python -m quranlab init"
        )
    con = sqlite3.connect(db_path, check_same_thread=check_same_thread)
    con.row_factory = sqlite3.Row
    ensure_indexes(con, db_path)
    return con


_INDEXED: set = set()

# Index secondaires : accélèrent la recherche par racine (les bases existantes
# construites avant leur ajout ne les ont pas — migration légère, une seule fois).
_EXTRA_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_words_root_bw ON words (root_buckwalter)",
)


def ensure_indexes(con: sqlite3.Connection, db_path: Path = config.DB_PATH) -> None:
    """Crée, une seule fois par base, les index absents des vieux schémas."""
    key = str(Path(db_path).resolve())
    if key in _INDEXED:
        return
    for stmt in _EXTRA_INDEXES:
        con.execute(stmt)
    con.commit()
    _INDEXED.add(key)


def is_built(db_path: Path = config.DB_PATH) -> bool:
    return Path(db_path).exists()


def surah_name(con: sqlite3.Connection, number: int) -> str:
    row = con.execute(
        "SELECT name_translit, name_ar FROM surahs WHERE number = ?", (number,)
    ).fetchone()
    if not row:
        return str(number)
    return f"{number}. {row['name_translit']} ({row['name_ar']})"


def surah_names(con: sqlite3.Connection) -> dict:
    """{numéro: nom translittéré} pour les 114 sourates (labels d'affichage)."""
    return {
        row["number"]: row["name_translit"] or ""
        for row in con.execute("SELECT number, name_translit FROM surahs")
    }
