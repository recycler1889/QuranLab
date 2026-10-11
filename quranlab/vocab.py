"""Vocabulaire coranique : fréquence, glose de racine et fiche mot.

Alimente l'apprentissage (cartes par racine, quiz) et l'inspecteur de mot
(volet ouvert au clic sur un mot d'un verset). Toutes les données proviennent
du corpus déjà construit (tables ``words`` / ``verses``) et des lexiques
embarqués (``lexicon_fr.json``, ``themes.json`` / ``themes_en.json``).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import search
from .buckwalter import arabic_to_buckwalter, normalize_arabic

_DIR = Path(__file__).resolve().parent

# Caches mémoire (les lexiques ne changent pas pendant l'exécution).
_LEX_FR: dict | None = None      # {root_bw: gloss (fr)}
_THEME_FR: dict | None = None    # {root_bw: label (fr)}
_THEME_EN: dict | None = None    # {root_bw: label (en)}


def _load_json(name: str) -> dict:
    try:
        data = json.loads((_DIR / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _lex_fr() -> dict:
    """{racine Buckwalter: glose française} (index inverse de lexicon_fr)."""
    global _LEX_FR
    if _LEX_FR is None:
        out: dict = {}
        for key, spec in _load_json("lexicon_fr.json").items():
            if key.startswith("_") or not isinstance(spec, dict):
                continue
            gloss = spec.get("gloss") or spec.get("label") or ""
            for root in spec.get("roots", []) or []:
                out.setdefault(str(root), str(gloss))
        _LEX_FR = out
    return _LEX_FR


def _theme_index(name: str) -> dict:
    """{racine Buckwalter: libellé localisé} issu d'un fichier de thèmes."""
    out: dict = {}
    for key, spec in _load_json(name).items():
        if key.startswith("_") or not isinstance(spec, dict):
            continue
        label = spec.get("label") or ""
        for root_ar in spec.get("roots", []) or []:
            bw = arabic_to_buckwalter(normalize_arabic(str(root_ar)))
            if bw:
                out.setdefault(bw, str(label))
    return out


def _themes_fr() -> dict:
    global _THEME_FR
    if _THEME_FR is None:
        _THEME_FR = _theme_index("themes.json")
    return _THEME_FR


def _themes_en() -> dict:
    global _THEME_EN
    if _THEME_EN is None:
        _THEME_EN = _theme_index("themes_en.json")
    return _THEME_EN


def root_gloss(root_bw: str, lang: str = "fr") -> str:
    """Glose lisible d'une racine (français par défaut, anglais si dispo)."""
    if not root_bw:
        return ""
    if (lang or "fr").lower() == "en":
        return (_themes_en().get(root_bw)
                or _lex_fr().get(root_bw)
                or _themes_fr().get(root_bw)
                or "")
    return _lex_fr().get(root_bw) or _themes_fr().get(root_bw) or ""


# --- Fréquence ------------------------------------------------------------
def frequent_roots(con: sqlite3.Connection, top_n: int = 300,
                   lang: str = "fr") -> list:
    """Racines les plus fréquentes, avec occurrence, versets et glose."""
    rows = con.execute(
        """
        SELECT root_buckwalter AS bw, root_arabic AS ar,
               COUNT(*) AS occ,
               COUNT(DISTINCT sura || ':' || aya) AS verses
        FROM words
        WHERE root_buckwalter IS NOT NULL AND root_buckwalter <> ''
        GROUP BY root_buckwalter
        ORDER BY occ DESC, root_buckwalter ASC
        LIMIT ?
        """,
        (int(top_n),),
    ).fetchall()
    out = []
    for rank, r in enumerate(rows, start=1):
        out.append({
            "rank": rank,
            "root_bw": r["bw"],
            "root_ar": r["ar"],
            "occurrences": r["occ"],
            "verses": r["verses"],
            "gloss": root_gloss(r["bw"], lang),
        })
    return out


def frequent_lemmas(con: sqlite3.Connection, top_n: int = 300) -> list:
    """Lemmes les plus fréquents (pour cartes de type ``lemma``)."""
    rows = con.execute(
        """
        SELECT lemma_buckwalter AS bw, COUNT(*) AS occ,
               COUNT(DISTINCT sura || ':' || aya) AS verses,
               MAX(root_buckwalter) AS root_bw, MAX(root_arabic) AS root_ar
        FROM words
        WHERE lemma_buckwalter IS NOT NULL AND lemma_buckwalter <> ''
        GROUP BY lemma_buckwalter
        ORDER BY occ DESC, lemma_buckwalter ASC
        LIMIT ?
        """,
        (int(top_n),),
    ).fetchall()
    return [
        {
            "rank": i,
            "lemma_bw": r["bw"],
            "occurrences": r["occ"],
            "verses": r["verses"],
            "root_bw": r["root_bw"],
            "root_ar": r["root_ar"],
        }
        for i, r in enumerate(rows, start=1)
    ]


# --- Fiche mot (inspecteur) ----------------------------------------------
def word_info(con: sqlite3.Connection, sura: int, aya: int, word_index: int,
              lang: str = "fr") -> dict | None:
    """Fiche complète d'un mot : forme, racine, POS, fréquences, glose."""
    row = con.execute(
        """
        SELECT word_index, form_arabic, transliteration, root_arabic,
               root_buckwalter, lemma_buckwalter, pos
        FROM words WHERE sura = ? AND aya = ? AND word_index = ?
        """,
        (int(sura), int(aya), int(word_index)),
    ).fetchone()
    if row is None:
        return None
    info = dict(row)
    form = info.get("form_arabic") or ""
    root_bw = info.get("root_buckwalter")
    lemma_bw = info.get("lemma_buckwalter")

    info["form_count"] = con.execute(
        "SELECT COUNT(*) FROM words WHERE form_arabic = ?", (form,)
    ).fetchone()[0]
    info["lemma_count"] = (
        con.execute(
            "SELECT COUNT(*) FROM words WHERE lemma_buckwalter = ?", (lemma_bw,)
        ).fetchone()[0]
        if lemma_bw else 0
    )
    if root_bw:
        info["root_count"] = con.execute(
            "SELECT COUNT(*) FROM words WHERE root_buckwalter = ?", (root_bw,)
        ).fetchone()[0]
        info["root_verses"] = con.execute(
            "SELECT COUNT(DISTINCT sura || ':' || aya) FROM words "
            "WHERE root_buckwalter = ?", (root_bw,)
        ).fetchone()[0]
        info["root_forms"] = [
            {"form": r["form_arabic"], "count": r["n"]}
            for r in con.execute(
                """
                SELECT form_arabic, COUNT(*) AS n FROM words
                WHERE root_buckwalter = ?
                GROUP BY form_arabic ORDER BY n DESC, form_arabic ASC
                LIMIT 8
                """,
                (root_bw,),
            ).fetchall()
        ]
    else:
        info["root_count"] = 0
        info["root_verses"] = 0
        info["root_forms"] = []

    info["gloss"] = root_gloss(root_bw, lang) if root_bw else ""
    verse = search.get_verse(con, int(sura), int(aya))
    info["ref"] = f"{int(sura)}:{int(aya)}"
    info["verse_uthmani"] = (verse or {}).get("text_uthmani", "")
    info["translations"] = (verse or {}).get("translations", [])
    return info


def verse_tokens(con: sqlite3.Connection, sura: int, aya: int) -> list:
    """Mots d'un verset (table ``words``) — base du rendu cliquable."""
    rows = con.execute(
        """
        SELECT word_index, form_arabic, transliteration, root_arabic,
               root_buckwalter, lemma_buckwalter, pos
        FROM words WHERE sura = ? AND aya = ? ORDER BY word_index
        """,
        (int(sura), int(aya)),
    ).fetchall()
    return [dict(r) for r in rows]


def sample_verses(con: sqlite3.Connection, root_bw: str, limit: int = 1) -> list:
    """Quelques versets contenant une racine : [{sura, aya, word_index}]."""
    rows = con.execute(
        """
        SELECT DISTINCT sura, aya FROM words
        WHERE root_buckwalter = ?
        ORDER BY sura, aya LIMIT ?
        """,
        (root_bw, int(limit)),
    ).fetchall()
    return [{"sura": r["sura"], "aya": r["aya"]} for r in rows]


# --- Vocabulaire essentiel (parcours Iqra) --------------------------------
def corpus_token_count(con: sqlite3.Connection) -> int:
    """Nombre total de mots « racinisés » du corpus (= dénominateur de
    la couverture de fréquence)."""
    return con.execute(
        "SELECT COUNT(*) FROM words "
        "WHERE root_buckwalter IS NOT NULL AND root_buckwalter <> ''"
    ).fetchone()[0]


def frequent_words(con: sqlite3.Connection, top_n: int = 500,
                   lang: str = "fr") -> list:
    """Racines les plus fréquentes, avec leur mot le plus représentatif.

    Chaque entrée contient, outre le rang et la racine (arabe + Buckwalter) :

    - ``ar`` / ``tr`` : la **forme la plus fréquente** du corpus pour cette
      racine, avec sa translittération (colonne ``words.transliteration``) ;
    - ``occ`` / ``verses`` : occurrences totales et versets distincts ;
    - ``ref`` : première occurrence (``sura:aya``) du corpus ;
    - ``gloss`` : glose localisée (par ``lang``) ;
    - ``coverage_pct`` : part cumulée du texte couverte jusqu'à ce rang.

    Deux requêtes seulement (regroupement par racine puis par forme) :
    pas de sous-requête corrélée.
    """
    total = corpus_token_count(con)
    rows = con.execute(
        """
        SELECT root_buckwalter AS bw, root_arabic AS ar, COUNT(*) AS occ,
               COUNT(DISTINCT sura || ':' || aya) AS verses,
               MIN(sura * 1000 + aya) AS first_key
        FROM words
        WHERE root_buckwalter IS NOT NULL AND root_buckwalter <> ''
        GROUP BY root_buckwalter
        ORDER BY occ DESC, root_buckwalter ASC
        LIMIT ?
        """,
        (int(top_n),),
    ).fetchall()

    # Forme (arabe + translittération) la plus fréquente de chaque racine :
    # le tri par compte décroissant donne la première occurrence par racine.
    best: dict = {}
    for r in con.execute(
        """
        SELECT root_buckwalter AS bw, form_arabic AS form,
               MAX(transliteration) AS tr
        FROM words
        WHERE root_buckwalter IS NOT NULL AND root_buckwalter <> ''
          AND form_arabic <> '' AND transliteration <> ''
        GROUP BY root_buckwalter, form_arabic
        ORDER BY COUNT(*) DESC
        """
    ).fetchall():
        best.setdefault(r["bw"], (r["form"], r["tr"]))

    out = []
    cumulative = 0
    for rank, r in enumerate(rows, start=1):
        cumulative += r["occ"]
        form, tr = best.get(r["bw"], ("", ""))
        out.append({
            "rank": rank,
            "root_bw": r["bw"],
            "root_ar": r["ar"],
            "ar": form,
            "tr": tr,
            "occ": r["occ"],
            "verses": r["verses"],
            "ref": "%d:%d" % (r["first_key"] // 1000, r["first_key"] % 1000),
            "gloss": root_gloss(r["bw"], lang),
            "coverage_pct": round(cumulative / total * 100, 1) if total else 0.0,
        })
    return out
