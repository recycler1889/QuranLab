"""Moteur de recherche intra-coranique.

Trois axes, strictement textuels :
  1. recherche textuelle arabe (normalisée, sans diacritiques) ;
  2. recherche textuelle française (insensible aux accents/casse) ;
  3. recherche par racine (trilitère / quadrilitère), en arabe ou Buckwalter.
Plus une agrégation thématique (racines + termes) définie dans themes.json.
"""

import json
import sqlite3
from pathlib import Path

from .buckwalter import (
    arabic_to_buckwalter,
    buckwalter_to_arabic,
    is_arabic,
    normalize_arabic,
    normalize_latin,
)

_THEMES_PATH = Path(__file__).resolve().parent / "themes.json"
_THEMES_EN_PATH = Path(__file__).resolve().parent / "themes_en.json"
_CONTROVERSIES_PATH = Path(__file__).resolve().parent / "controversies.json"
_CONTROVERSIES_EN_PATH = Path(__file__).resolve().parent / "controversies_en.json"

# Cache en mémoire du fichier de thèmes (invalidé si le fichier change).
_THEMES_CACHE: dict | None = None
_THEMES_MTIME: int | None = None
_THEMES_EN_CACHE: dict | None = None
_THEMES_EN_MTIME: int | None = None


def _load_json_cached(path: Path, cache_name: str, mtime_name: str) -> dict:
    """Charge un JSON en le mettant en cache, invalidé si le fichier change."""
    if not path.exists():
        return {}
    mtime = path.stat().st_mtime_ns
    cached = globals().get(cache_name)
    if cached is None or globals().get(mtime_name) != mtime:
        cached = json.loads(path.read_text(encoding="utf-8"))
        globals()[cache_name] = cached
        globals()[mtime_name] = mtime
    return cached


def load_themes_en() -> dict:
    """Superposition anglaise de themes.json (libellés, descriptions, catégories)."""
    return _load_json_cached(
        _THEMES_EN_PATH, "_THEMES_EN_CACHE", "_THEMES_EN_MTIME"
    )


def load_controversies_en() -> dict:
    """Superposition anglaise de controversies.json (libellés, notes)."""
    return _load_json_cached(_CONTROVERSIES_EN_PATH, "_CONTROV_EN_CACHE", "_CONTROV_EN_MTIME")


# --------------------------------------------------------------------------
# Recherche textuelle
# --------------------------------------------------------------------------
def search_arabic(con: sqlite3.Connection, query: str, limit: int = 100) -> list:
    """Recherche une chaîne arabe (diacritiques ignorés) dans le texte simple."""
    q = normalize_arabic(query).strip()
    if not q:
        return []
    rows = con.execute(
        """
        SELECT sura, aya, text_uthmani, text_simple
        FROM verses
        WHERE text_simple_norm LIKE ?
        ORDER BY sura, aya
        LIMIT ?
        """,
        (f"%{q}%", limit),
    ).fetchall()
    return [dict(r) for r in rows]


def arabic_occurrence_summary(
    con: sqlite3.Connection, query: str, limit: int = 100
) -> dict:
    """Compte les occurrences d'une chaîne arabe dans tout le texte du Coran.

    `occurrences` = nombre de fois où le terme (diacritiques ignorés) apparaît ;
    `verses` = nombre de versets distincts qui le contiennent. Les versets
    (jusqu'à `limit`) sont renvoyés pour l'affichage contextualisé.
    """
    q = normalize_arabic(query).strip()
    if not q:
        return {"occurrences": 0, "verses": 0, "rows": []}
    row = con.execute(
        "SELECT COUNT(*) AS verses, "
        "COALESCE(SUM((LENGTH(text_simple_norm) "
        "  - LENGTH(REPLACE(text_simple_norm, ?, ''))) / LENGTH(?)), 0) "
        "  AS occurrences "
        "FROM verses WHERE text_simple_norm LIKE ?",
        (q, q, f"%{q}%"),
    ).fetchone()
    return {
        "occurrences": int(row["occurrences"] or 0),
        "verses": row["verses"] or 0,
        "rows": search_arabic(con, q, limit=limit),
    }


def search_french(
    con: sqlite3.Connection,
    query: str,
    limit: int = 100,
    translation_key: str | None = None,
) -> list:
    """Recherche une chaîne française dans les traductions.

    **Un seul enregistrement par verset** (`GROUP BY sura, aya`) : un verset
    dont le terme apparaît dans plusieurs traductions n'est retourné qu'une
    fois. `hits` compte le nombre de traductions touchées, `translation_keys`
    les clés correspondantes, `translation`/`author` un extrait représentatif
    (détail complet via `french_matches_rows`).
    """
    q = normalize_latin(query).strip()
    if not q:
        return []
    sql = """
        SELECT tv.sura, tv.aya, v.text_uthmani,
               COUNT(DISTINCT tv.translation_id) AS hits,
               GROUP_CONCAT(DISTINCT t.key) AS translation_keys,
               MIN(tv.text) AS translation,
               MIN(t.author) AS author
        FROM translation_verses tv
        JOIN translations t ON t.id = tv.translation_id
        JOIN verses v ON v.sura = tv.sura AND v.aya = tv.aya
        WHERE tv.text_norm LIKE ?
    """
    params: list = [f"%{q}%"]
    if translation_key:
        sql += " AND t.key = ?"
        params.append(translation_key)
    sql += " GROUP BY tv.sura, tv.aya ORDER BY tv.sura, tv.aya LIMIT ?"
    params.append(limit)
    return [dict(r) for r in con.execute(sql, params).fetchall()]


def french_matches_rows(
    con: sqlite3.Connection,
    query: str,
    refs,
    translation_key: str | None = None,
) -> list:
    """Lignes détaillées (une par traduction touchée) pour des versets donnés.

    Sert d'appoint à `search_french` (dédupliqué) quand on veut afficher
    chaque traduction contenant réellement le terme.
    """
    q = normalize_latin(query).strip()
    refs = list(dict.fromkeys(tuple(r) for r in refs))
    if not q or not refs:
        return []
    where = " OR ".join("(tv.sura = ? AND tv.aya = ?)" for _ in refs)
    sql = f"""
        SELECT tv.sura, tv.aya, tv.text AS translation, t.key AS translation_key,
               t.author, v.text_uthmani
        FROM translation_verses tv
        JOIN translations t ON t.id = tv.translation_id
        JOIN verses v ON v.sura = tv.sura AND v.aya = tv.aya
        WHERE tv.text_norm LIKE ? AND ({where})
    """
    params: list = [f"%{q}%"] + [x for ref in refs for x in ref]
    if translation_key:
        sql += " AND t.key = ?"
        params.append(translation_key)
    sql += " ORDER BY tv.sura, tv.aya, t.id"
    return [dict(r) for r in con.execute(sql, params).fetchall()]


# --------------------------------------------------------------------------
# Recherche par racine
# --------------------------------------------------------------------------
def resolve_root(con: sqlite3.Connection, root_input: str):
    """Résout une racine saisie (arabe ou Buckwalter) vers sa forme canonique."""
    root_input = root_input.strip()
    row = None
    if is_arabic(root_input):
        row = con.execute(
            "SELECT root_buckwalter, root_arabic FROM words "
            "WHERE root_norm = ? LIMIT 1",
            (normalize_arabic(root_input),),
        ).fetchone()
        if row is None:
            bw = arabic_to_buckwalter(root_input)
            row = con.execute(
                "SELECT root_buckwalter, root_arabic FROM words "
                "WHERE root_buckwalter = ? LIMIT 1",
                (bw,),
            ).fetchone()
    else:
        row = con.execute(
            "SELECT root_buckwalter, root_arabic FROM words "
            "WHERE root_buckwalter = ? LIMIT 1",
            (root_input,),
        ).fetchone()
    return row


def search_root(
    con: sqlite3.Connection,
    root_input: str,
    limit: int = 1000,
    with_context: int = 0,
) -> dict:
    """Liste toutes les occurrences d'une racine.

    with_context : nombre de versets de contexte avant/après (0 = aucun).
    """
    resolved = resolve_root(con, root_input)
    if resolved is None:
        return {"found": False, "input": root_input, "occurrences": []}

    root_bw = resolved["root_buckwalter"]
    root_ar = resolved["root_arabic"]
    rows = con.execute(
        """
        SELECT w.sura, w.aya, w.word_index, w.form_arabic, w.transliteration,
               w.lemma_buckwalter, w.pos, v.text_uthmani, v.text_simple
        FROM words w
        JOIN verses v ON v.sura = w.sura AND v.aya = w.aya
        WHERE w.root_buckwalter = ?
        ORDER BY w.sura, w.aya, w.word_index
        LIMIT ?
        """,
        (root_bw, limit),
    ).fetchall()

    occurrences = []
    seen_verses = set()
    for r in rows:
        occ = dict(r)
        if with_context and (r["sura"], r["aya"]) not in seen_verses:
            seen_verses.add((r["sura"], r["aya"]))
            occ["context"] = get_context(
                con, r["sura"], r["aya"], before=with_context, after=with_context
            )
        occurrences.append(occ)

    return {
        "found": True,
        "input": root_input,
        "root_buckwalter": root_bw,
        "root_arabic": root_ar,
        "count": len(occurrences),
        "verses_count": len({(o["sura"], o["aya"]) for o in occurrences}),
        "occurrences": occurrences,
    }


# --------------------------------------------------------------------------
# Lecture de versets / contexte
# --------------------------------------------------------------------------
def get_verse(con: sqlite3.Connection, sura: int, aya: int) -> dict | None:
    v = con.execute(
        "SELECT sura, aya, text_uthmani, text_simple FROM verses "
        "WHERE sura = ? AND aya = ?",
        (sura, aya),
    ).fetchone()
    if v is None:
        return None
    verse = dict(v)
    verse["translations"] = [
        dict(r)
        for r in con.execute(
            """
            SELECT t.key, t.author, t.language, tv.text
            FROM translation_verses tv
            JOIN translations t ON t.id = tv.translation_id
            WHERE tv.sura = ? AND tv.aya = ?
            ORDER BY t.id
            """,
            (sura, aya),
        ).fetchall()
    ]
    verse["words"] = [
        dict(r)
        for r in con.execute(
            """
            SELECT word_index, form_arabic, transliteration, root_arabic,
                   lemma_buckwalter, pos
            FROM words WHERE sura = ? AND aya = ? ORDER BY word_index
            """,
            (sura, aya),
        ).fetchall()
    ]
    return verse


def get_context(
    con: sqlite3.Connection, sura: int, aya: int, before: int = 1, after: int = 1
) -> dict:
    rows = con.execute(
        """
        SELECT sura, aya, text_uthmani FROM verses
        WHERE sura = ? AND aya BETWEEN ? AND ?
        ORDER BY aya
        """,
        (sura, max(1, aya - before), aya + after),
    ).fetchall()
    return {"before": [dict(r) for r in rows if r["aya"] < aya],
            "verse": next((dict(r) for r in rows if r["aya"] == aya), None),
            "after": [dict(r) for r in rows if r["aya"] > aya]}


def verses_bundle(con: sqlite3.Connection, refs) -> dict:
    """Récupère en une passe, pour une liste de références (sura, aya), le texte
    uthmani et toutes les traductions disponibles.

    Retourne {(sura, aya): {"text_uthmani": str, "translations": [ {author, key, text} ]}}.
    """
    refs = list(dict.fromkeys(tuple(r) for r in refs))
    if not refs:
        return {}
    where = " OR ".join("(v.sura = ? AND v.aya = ?)" for _ in refs)
    params = [x for ref in refs for x in ref]

    bundle: dict = {}
    for row in con.execute(
        f"SELECT v.sura, v.aya, v.text_uthmani FROM verses v WHERE {where}", params
    ):
        bundle[(row["sura"], row["aya"])] = {
            "text_uthmani": row["text_uthmani"],
            "translations": [],
        }

    where_tv = " OR ".join("(tv.sura = ? AND tv.aya = ?)" for _ in refs)
    for row in con.execute(
        f"""
        SELECT tv.sura, tv.aya, t.key, t.author, t.language, tv.text
        FROM translation_verses tv
        JOIN translations t ON t.id = tv.translation_id
        WHERE {where_tv}
        ORDER BY tv.sura, tv.aya, t.id
        """,
        params,
    ):
        key = (row["sura"], row["aya"])
        if key in bundle:
            bundle[key]["translations"].append(
                {
                    "key": row["key"],
                    "author": row["author"],
                    "language": row["language"],
                    "text": row["text"],
                }
            )
    return bundle


# --------------------------------------------------------------------------
# Thèmes (agrégation racines + termes)
# --------------------------------------------------------------------------
def themes_fingerprint() -> int:
    """Empreinte (mtime) du fichier de thèmes — sert de clé de cache."""
    return _THEMES_PATH.stat().st_mtime_ns


def load_themes() -> dict:
    """Charge le fichier themes.json brut (clé `_meta` incluse).

    Résultat mis en mémoire : invalidé automatiquement si le fichier change
    (édition de themes.json pendant que l'app tourne).
    """
    global _THEMES_CACHE, _THEMES_MTIME
    mtime = _THEMES_PATH.stat().st_mtime_ns
    if _THEMES_CACHE is None or mtime != _THEMES_MTIME:
        _THEMES_CACHE = json.loads(_THEMES_PATH.read_text(encoding="utf-8"))
        _THEMES_MTIME = mtime
    return _THEMES_CACHE


def _themes_only() -> dict:
    """Ne retourne que les thèmes (sans la clé de métadonnées `_meta`)."""
    return {k: v for k, v in load_themes().items() if not k.startswith("_")}


def themes_meta(lang: str = "fr") -> dict:
    """Métadonnées des thèmes (note, catégories) dans la langue ``lang``."""
    if lang == "en":
        meta = load_themes_en().get("_meta")
        if meta:
            return meta
    return load_themes().get("_meta", {})


def _category_map() -> dict:
    """{catégorie FR: catégorie EN} par alignement des listes de `_meta`."""
    fr = load_themes().get("_meta", {}).get("categories", [])
    en = load_themes_en().get("_meta", {}).get("categories", [])
    return {f: en[i] for i, f in enumerate(fr) if i < len(en)}


def localize_theme(key: str, spec: dict, lang: str = "fr") -> dict:
    """Copie du thème avec libellé/description/catégorie dans la langue ``lang``."""
    if lang != "en":
        return spec
    over = load_themes_en().get(key)
    if not isinstance(over, dict):
        return spec
    out = dict(spec)
    if over.get("label"):
        out["label"] = over["label"]
    if over.get("description"):
        out["description"] = over["description"]
    cat = spec.get("category")
    if cat in _category_map():
        out["category"] = _category_map()[cat]
    return out


def themes_categories(lang: str = "fr") -> list:
    """Liste ordonnée des catégories thématiques (depuis `_meta`), localisée."""
    if lang == "en":
        cats = list(themes_meta("en").get("categories", []))
        if cats:
            cmap = _category_map()
            for spec in _themes_only().values():
                cat = cmap.get(spec.get("category", "Sans catégorie"))
                if cat and cat not in cats:
                    cats.append(cat)
            return cats
    data = load_themes()
    cats = list(data.get("_meta", {}).get("categories", []))
    for spec in _themes_only().values():
        cat = spec.get("category", "Sans catégorie")
        if cat not in cats:
            cats.append(cat)
    return cats


def themes_by_category(lang: str = "fr") -> dict:
    """Regroupe les thèmes par catégorie : {catégorie: [(clé, spec), ...]}."""
    themes = _themes_only()
    grouped = {cat: [] for cat in themes_categories(lang)}
    for key, spec in themes.items():
        loc = localize_theme(key, spec, lang)
        grouped.setdefault(loc.get("category", "Sans catégorie"), []).append(
            (key, loc)
        )
    for items in grouped.values():
        items.sort(key=lambda kv: kv[1].get("label", kv[0]))
    return grouped


def _theme_haystacks(key: str, spec: dict) -> tuple[str, str]:
    """Texte d'index d'un thème : (pôle latin, pôle arabe) normalisés."""
    roots = spec.get("roots", [])
    roots_lat = " ".join(
        arabic_to_buckwalter(r) if is_arabic(r) else r for r in roots
    )
    hay_lat = normalize_latin(
        " ".join(
            [
                key,
                spec.get("label", ""),
                spec.get("description", ""),
                spec.get("category", ""),
                roots_lat,
                " ".join(spec.get("terms_fr", [])),
            ]
        )
    )
    hay_ar = normalize_arabic(
        " ".join(
            [
                key,
                spec.get("label", ""),
                spec.get("description", ""),
                " ".join(roots),
                " ".join(spec.get("terms_ar", [])),
            ]
        )
    )
    return hay_lat, hay_ar


def theme_matches(key: str, spec: dict, query: str) -> bool:
    """Vrai si `query` (français, arabe ou Buckwalter) apparaît dans le thème."""
    q = (query or "").strip()
    if not q:
        return True
    hay_lat, hay_ar = _theme_haystacks(key, spec)
    if is_arabic(q):
        return normalize_arabic(q) in hay_ar
    return normalize_latin(q) in hay_lat


def filter_themes(query: str = "", category: str | None = None,
                  lang: str = "fr") -> list:
    """Filtre les thèmes par catégorie et/ou terme libre.

    Retourne une liste ordonnée de `(catégorie, clé, spec)` ; la recherche
    porte sur le libellé, la description, la clé, les racines (arabe ou
    Buckwalter) et les termes arabe/français. La langue ``lang`` localise les
    libellés/descriptions/catégories affichés.
    """
    grouped = themes_by_category(lang)
    q = (query or "").strip()
    out: list = []
    for cat, items in grouped.items():
        if category and cat != category:
            continue
        for key, spec in items:
            if q and not theme_matches(key, spec, q):
                continue
            out.append((cat, key, spec))
    return out


def theme_counts(con: sqlite3.Connection, limit: int = 500) -> dict:
    """{clé de thème: nombre de versets rattachés} pour tous les thèmes."""
    return {k: theme(con, k, limit=limit)["verses_count"] for k in _themes_only()}


def resolve_theme_key(name: str) -> tuple[str | None, list[str]]:
    """Résout un nom de thème tolérant : clé exacte, sinon correspondance unique.

    Au-delà de la clé exacte (``priere``), on accepte une variante usuelle en
    recherchant la saisie dans la clé, le libellé et les termes fr/ar des thèmes
    (ex. ``salat`` retrouve le thème ``priere`` dont le libellé contient
    « aṣ-ṣalāt »). La correspondance par sous-chaîne n'est tentée qu'au-delà de
    4 caractères et n'aboutit que si elle désigne **un seul** thème.

    Retourne ``(clé, [])`` si résolu, sinon ``(None, suggestions)``.
    """
    themes = _themes_only()
    key = name.strip().lower()
    if key in themes:
        return key, []
    q_lat = normalize_latin(key)
    q_ar = normalize_arabic(key)
    if len(q_lat) < 4 and len(q_ar) < 4:
        return None, []
    matches: list[str] = []
    for k, spec in themes.items():
        hay_lat = normalize_latin(
            " ".join(
                [k, spec.get("label", ""), " ".join(spec.get("terms_fr", []))]
            )
        )
        hay_ar = normalize_arabic(
            " ".join(
                [spec.get("label", ""), " ".join(spec.get("terms_ar", []))]
            )
        )
        if (q_lat and len(q_lat) >= 4 and q_lat in hay_lat) or (
            q_ar and len(q_ar) >= 4 and q_ar in hay_ar
        ):
            matches.append(k)
    if len(matches) == 1:
        return matches[0], []
    return None, sorted(matches)


def theme(con: sqlite3.Connection, name: str, limit: int = 500,
          lang: str = "fr") -> dict:
    """Regroupe toutes les occurrences textuelles d'un thème intra-coranique."""
    themes = _themes_only()
    key = name.strip().lower()
    if key not in themes:
        key, suggestions = resolve_theme_key(name)
        if key is None:
            return {
                "found": False,
                "name": name,
                "available": sorted(themes),
                "suggestions": suggestions,
            }

    spec = localize_theme(key, themes[key], lang)
    src_root = "root {r}" if lang == "en" else "racine {r}"
    src_term = "term {t}" if lang == "en" else "terme {t}"
    src_fr = "fr \u00ab {t} \u00bb" if lang != "en" else "fr \u201c{t}\u201d"
    verses: dict = {}

    def _add(sura, aya, source, detail=None):
        entry = verses.setdefault(
            (sura, aya), {"sura": sura, "aya": aya, "sources": [], "matches": []}
        )
        if source not in entry["sources"]:
            entry["sources"].append(source)
        if detail and detail not in entry["matches"]:
            entry["matches"].append(detail)

    for root in spec.get("roots", []):
        res = search_root(con, root, limit=limit)
        if res.get("found"):
            for o in res["occurrences"]:
                _add(o["sura"], o["aya"],
                     src_root.format(r=res["root_arabic"]), o["form_arabic"])

    for term in spec.get("terms_ar", []):
        for row in search_arabic(con, term, limit=limit):
            _add(row["sura"], row["aya"], src_term.format(t=term))

    for term in spec.get("terms_fr", []):
        for row in search_french(con, term, limit=limit):
            _add(row["sura"], row["aya"], src_fr.format(t=term))

    ordered = [verses[k] for k in sorted(verses)]
    return {
        "found": True,
        "name": key,
        "category": spec.get("category", "Sans catégorie"),
        "label": spec.get("label", key),
        "description": spec.get("description", ""),
        "roots": spec.get("roots", []),
        "terms_ar": spec.get("terms_ar", []),
        "terms_fr": spec.get("terms_fr", []),
        "verses_count": len(ordered),
        "verses": ordered,
    }


# --------------------------------------------------------------------------
# Idées reçues et controverses (analyse strictement textuelle)
# --------------------------------------------------------------------------
def load_controversies() -> dict:
    """Charge controversies.json (clé `_meta` incluse)."""
    path = Path(__file__).resolve().parent / "controversies.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _controversies_only() -> dict:
    return {k: v for k, v in load_controversies().items() if not k.startswith("_")}


def controversy_meta(lang: str = "fr") -> dict:
    """Métadonnées (titre, avertissement, méthode) dans la langue ``lang``."""
    if lang == "en":
        meta = load_controversies_en().get("_meta")
        if meta:
            return meta
    return load_controversies().get("_meta", {})


def localize_controversy(key: str, spec: dict, lang: str = "fr") -> dict:
    """Copie du sujet avec libellé/question/cadrage dans la langue ``lang``."""
    if lang != "en":
        return spec
    over = load_controversies_en().get(key)
    if not isinstance(over, dict):
        return spec
    out = dict(spec)
    for field in ("label", "question", "framing", "context_hint"):
        if over.get(field):
            out[field] = over[field]
    return out


def controversy_topics(lang: str = "fr") -> dict:
    """Retourne les sujets de controverse {clé: spec} (sans `_meta`), localisés."""
    base = _controversies_only()
    if lang == "en":
        return {k: localize_controversy(k, v, lang) for k, v in base.items()}
    return base


def _term_stem(term: str) -> str:
    """Retire l'article défini pour compter les occurrences d'un terme."""
    return term[2:] if term.startswith("ال") and len(term) > 3 else term


def controversy(con: sqlite3.Connection, name: str, limit: int = 500,
                lang: str = "fr") -> dict:
    """Analyse textuelle d'un sujet : récurrence lexicale + versets clés.

    Ne produit aucune conclusion : compte les occurrences (racines et termes),
    et retourne les versets clés avec leur texte et toutes leurs traductions.
    """
    items = _controversies_only()
    key = name.strip().lower()
    if key not in items:
        return {"found": False, "name": name, "available": sorted(items)}

    spec = localize_controversy(key, items[key], lang)
    kind_root = "root" if lang == "en" else "racine"
    kind_term = "term" if lang == "en" else "terme"
    notfound = "not found" if lang == "en" else "introuvable"

    recurrence = []
    for root in spec.get("roots", []):
        res = search_root(con, root, limit=limit)
        if res.get("found"):
            recurrence.append(
                {
                    "kind": kind_root,
                    "label": res["root_arabic"],
                    "detail": res["root_buckwalter"],
                    "occurrences": res["count"],
                    "verses": res["verses_count"],
                }
            )
        else:
            recurrence.append(
                {
                    "kind": kind_root,
                    "label": root,
                    "detail": notfound,
                    "occurrences": 0,
                    "verses": 0,
                }
            )
    for term in spec.get("terms_ar", []):
        rows = search_arabic(con, _term_stem(term), limit=limit)
        recurrence.append(
            {
                "kind": kind_term,
                "label": term,
                "detail": _term_stem(term),
                "occurrences": len(rows),
                "verses": len(rows),
            }
        )

    polysemy = []
    for root in spec.get("root_polysemy", []):
        p = root_polysemy(con, root, limit=limit)
        if p:
            polysemy.append(p)

    refs = []
    for ref in spec.get("key_verses", []):
        sura, aya = (int(x) for x in ref.split(":"))
        refs.append((sura, aya))
    bundle = verses_bundle(con, refs)

    verses = []
    for sura, aya in refs:
        data = bundle.get((sura, aya), {})
        verses.append(
            {
                "sura": sura,
                "aya": aya,
                "text_uthmani": data.get("text_uthmani", ""),
                "translations": data.get("translations", []),
                "missing": (sura, aya) not in bundle,
            }
        )

    return {
        "found": True,
        "name": key,
        "label": spec.get("label", key),
        "question": spec.get("question", ""),
        "framing": spec.get("framing", ""),
        "context_hint": spec.get("context_hint", ""),
        "recurrence": recurrence,
        "polysemy": polysemy,
        "verses": verses,
    }


def root_polysemy(con: sqlite3.Connection, root_input: str, limit: int = 1000) -> dict | None:
    """Analyse la polysémie d'une racine : toutes ses formes et occurrences.

    Retourne les formes distinctes (avec comptage) et la liste des occurrences
    (verset, forme, POS) pour observer la variété des emplois dans le corpus.
    """
    res = search_root(con, root_input, limit=limit)
    if not res.get("found"):
        return None
    forms: dict = {}
    occurrences = []
    for o in res["occurrences"]:
        form = o["form_arabic"]
        forms[form] = forms.get(form, 0) + 1
        occurrences.append(
            {
                "sura": o["sura"],
                "aya": o["aya"],
                "form": form,
                "pos": o["pos"],
                "text_uthmani": o["text_uthmani"],
            }
        )
    return {
        "root": res["root_arabic"],
        "buckwalter": res["root_buckwalter"],
        "total": res["count"],
        "verses": res["verses_count"],
        "forms": sorted(forms.items(), key=lambda kv: (-kv[1], kv[0])),
        "occurrences": occurrences,
    }


# --------------------------------------------------------------------------
# Concordance interne / versets en miroir (le Coran s'explique par le Coran)
# --------------------------------------------------------------------------
def verse_root_set(con: sqlite3.Connection, sura: int, aya: int) -> set:
    """Ensemble des racines (Buckwalter) présentes dans un verset."""
    rows = con.execute(
        "SELECT DISTINCT root_buckwalter FROM words "
        "WHERE sura = ? AND aya = ? AND root_buckwalter IS NOT NULL",
        (sura, aya),
    ).fetchall()
    return {r["root_buckwalter"] for r in rows}


def _verses_sharing_roots(
    con: sqlite3.Connection,
    target: set,
    exclude: tuple | None = None,
    limit: int = 12,
    min_shared: int = 2,
) -> list:
    """Versets partageant le plus de racines avec un ensemble cible (Buckwalter).

    Cœur commun de `mirror_verses` (cible = racines d'un verset) et de
    `similar_verses_by_roots` (cible = racines issues d'un mot-clé). Chaque
    résultat porte son nombre de racines communes, le ratio de recouvrement,
    le texte uthmani et les traductions.
    """
    if not target:
        return []

    qmarks = ",".join("?" * len(target))
    sql = (
        "SELECT DISTINCT w.sura, w.aya, w.root_buckwalter "
        "FROM words w "
        f"WHERE w.root_buckwalter IN ({qmarks})"
    )
    extra: list = [*sorted(target)]
    if exclude is not None:
        sql += " AND NOT (w.sura = ? AND w.aya = ?)"
        extra += [exclude[0], exclude[1]]
    rows = con.execute(sql, extra).fetchall()

    shared: dict = {}
    for r in rows:
        shared.setdefault((r["sura"], r["aya"]), set()).add(r["root_buckwalter"])

    matches = []
    for (s, a), roots in shared.items():
        if len(roots) >= min_shared:
            matches.append(
                {
                    "sura": s,
                    "aya": a,
                    "shared": len(roots),
                    "ratio": round(len(roots) / len(target), 2),
                    "roots_arabic": sorted(buckwalter_to_arabic(r) for r in roots),
                }
            )
    matches.sort(key=lambda m: (-m["shared"], m["sura"], m["aya"]))
    matches = matches[:limit]

    bundle = verses_bundle(con, [(m["sura"], m["aya"]) for m in matches])
    for m in matches:
        data = bundle.get((m["sura"], m["aya"]), {})
        m["text_uthmani"] = data.get("text_uthmani", "")
        m["translations"] = data.get("translations", [])
    return matches


def top_roots_in_verses(con: sqlite3.Connection, refs, top: int = 8) -> list:
    """Racines les plus fréquentes dans un ensemble de versets.

    Sert à dériver des racines « représentatives » d'un mot-clé arabe (dont le
    texte apparaît dans plusieurs versets) pour en suggérer des similaires.
    """
    refs = list(dict.fromkeys(tuple(r) for r in refs))
    if not refs:
        return []
    where = " OR ".join("(sura = ? AND aya = ?)" for _ in refs)
    params = [x for ref in refs for x in ref]
    rows = con.execute(
        f"SELECT root_buckwalter, root_arabic, COUNT(*) AS n "
        f"FROM words WHERE root_buckwalter IS NOT NULL AND ({where}) "
        f"GROUP BY root_buckwalter ORDER BY n DESC LIMIT ?",
        params + [top],
    ).fetchall()
    return [dict(r) for r in rows]


def mirror_verses(
    con: sqlite3.Connection, sura: int, aya: int, limit: int = 12, min_shared: int = 2
) -> dict:
    """Trouve les « versets en miroir » : autres versets partageant le plus de
    racines avec le verset de référence (correspondance lexicale intra-coranique)."""
    target = verse_root_set(con, sura, aya)
    matches = _verses_sharing_roots(
        con, target, exclude=(sura, aya), limit=limit, min_shared=min_shared
    )
    return {
        "sura": sura,
        "aya": aya,
        "roots_arabic": sorted(buckwalter_to_arabic(r) for r in target),
        "matches": matches,
    }


def similar_verses_by_roots(
    con: sqlite3.Connection,
    roots,
    limit: int = 12,
    min_shared: int = 2,
) -> dict:
    """Versets similaires suggérés à partir d'un mot-clé / d'une liste de racines.

    Les racines (arabe ou Buckwalter) sont résolues contre la base ; les versets
    sont classés par nombre de racines communes puis par ratio de recouvrement.
    """
    target_bw = {
        (arabic_to_buckwalter(r) if is_arabic(r) else r)
        for r in roots
    }
    target_bw = {r for r in target_bw if root_stats(con, r)}
    matches = _verses_sharing_roots(
        con, target_bw, exclude=None, limit=limit, min_shared=min_shared
    )
    return {
        "roots_arabic": sorted(buckwalter_to_arabic(r) for r in target_bw),
        "matches": matches,
    }


def concordance(
    con: sqlite3.Connection,
    root: str | None = None,
    term: str | None = None,
    limit: int = 300,
) -> dict:
    """Grille de concordance pour une notion : toutes les occurrences d'une
    racine ou d'un terme, avec texte arabe et traductions."""
    if root:
        res = search_root(con, root, limit=limit)
        if not res.get("found"):
            return {"found": False, "kind": "racine", "input": root}
        refs = list(dict.fromkeys((o["sura"], o["aya"]) for o in res["occurrences"]))
        bundle = verses_bundle(con, refs)
        verses = [
            {
                "sura": s,
                "aya": a,
                "text_uthmani": bundle.get((s, a), {}).get("text_uthmani", ""),
                "translations": bundle.get((s, a), {}).get("translations", []),
            }
            for (s, a) in refs
        ]
        return {
            "found": True,
            "kind": "racine",
            "label": res["root_arabic"],
            "detail": res["root_buckwalter"],
            "occurrences": res["count"],
            "verses_count": len(refs),
            "verses": verses,
        }
    if term:
        rows = search_arabic(con, term, limit=limit)
        refs = list(dict.fromkeys((r["sura"], r["aya"]) for r in rows))
        bundle = verses_bundle(con, refs)
        verses = [
            {
                "sura": s,
                "aya": a,
                "text_uthmani": bundle.get((s, a), {}).get("text_uthmani", ""),
                "translations": bundle.get((s, a), {}).get("translations", []),
            }
            for (s, a) in refs
        ]
        return {
            "found": True,
            "kind": "terme",
            "label": term,
            "detail": "",
            "occurrences": len(refs),
            "verses_count": len(refs),
            "verses": verses,
        }
    return {"found": False}


# --------------------------------------------------------------------------
# Lecture continue (sourates / versets) — onglet « Lire »
# --------------------------------------------------------------------------
def surah_list(con: sqlite3.Connection) -> list:
    """Liste ordonnée des 114 sourates (n°, noms, révélation, nb de versets)."""
    rows = con.execute(
        "SELECT number, name_translit, name_ar, name_en, revelation, verses_count "
        "FROM surahs ORDER BY number"
    ).fetchall()
    return [dict(r) for r in rows]


def surah_verses(
    con: sqlite3.Connection, sura: int, start: int = 1, end: int | None = None
) -> list:
    """Versets d'une sourate dans l'ordre, avec texte uthmani et traductions.

    ``start``/``end`` délimitent la plage (bornes incluses) pour un affichage
    paginé ; ``end`` par défaut va jusqu'au dernier verset de la sourate.
    """
    row = con.execute(
        "SELECT verses_count FROM surahs WHERE number = ?", (sura,)
    ).fetchone()
    if row is None:
        return []
    last = int(row["verses_count"])
    start = max(1, int(start))
    end = last if end is None else min(last, int(end))
    if end < start:
        return []
    refs = [(sura, a) for a in range(start, end + 1)]
    bundle = verses_bundle(con, refs)
    out = []
    for (s, a) in refs:
        data = bundle.get((s, a), {})
        out.append(
            {
                "sura": s,
                "aya": a,
                "text_uthmani": data.get("text_uthmani", ""),
                "translations": data.get("translations", []),
            }
        )
    return out


# --------------------------------------------------------------------------
# Croisement de racines (co-occurrence) — onglet « Croisement »
# --------------------------------------------------------------------------
def verses_with_all_roots(
    con: sqlite3.Connection, roots, limit: int = 200
) -> dict:
    """Versets contenant **toutes** les racines demandées (intersection).

    Chaque entrée ``roots`` peut être de l'arabe ou du Buckwalter. Sert au
    croisement de deux (ou plusieurs) notions : « où le texte les réunit-il ? ».
    """
    resolved: list = []
    for r in roots:
        row = resolve_root(con, r)
        if row is None:
            return {"found": False, "input": r}
        if row["root_buckwalter"] not in resolved:
            resolved.append(row["root_buckwalter"])
    if not resolved:
        return {"found": False, "input": ""}

    qmarks = ",".join("?" * len(resolved))
    rows = con.execute(
        f"SELECT sura, aya, COUNT(DISTINCT root_buckwalter) AS n "
        f"FROM words WHERE root_buckwalter IN ({qmarks}) "
        f"GROUP BY sura, aya HAVING n = ? ORDER BY sura, aya LIMIT ?",
        [*resolved, len(resolved), limit],
    ).fetchall()
    refs = [(r["sura"], r["aya"]) for r in rows]
    bundle = verses_bundle(con, refs)
    verses = [
        {
            "sura": s,
            "aya": a,
            "text_uthmani": bundle.get((s, a), {}).get("text_uthmani", ""),
            "translations": bundle.get((s, a), {}).get("translations", []),
        }
        for (s, a) in refs
    ]
    return {
        "found": True,
        "roots_arabic": sorted(buckwalter_to_arabic(r) for r in resolved),
        "verses_count": len(refs),
        "verses": verses,
    }


def co_roots(
    con: sqlite3.Connection, root_input: str, top: int = 15
) -> dict:
    """Racines les plus souvent **co-occurrentes** avec une racine donnée.

    Pour toutes les occurrences de la racine, on compte les autres racines
    présentes dans les mêmes versets. Révèle le champ lexical qui entoure une
    notion (« avec quoi le texte l'associe-t-il ? »).
    """
    row = resolve_root(con, root_input)
    if row is None:
        return {"found": False, "input": root_input}
    bw = row["root_buckwalter"]
    rows = con.execute(
        "SELECT w2.root_buckwalter AS root_buckwalter, w2.root_arabic AS root_arabic, "
        "       COUNT(DISTINCT w2.sura || ':' || w2.aya) AS n "
        "FROM words w1 JOIN words w2 "
        "  ON w1.sura = w2.sura AND w1.aya = w2.aya "
        "WHERE w1.root_buckwalter = ? AND w2.root_buckwalter IS NOT NULL "
        "  AND w2.root_buckwalter <> ? "
        "GROUP BY w2.root_buckwalter ORDER BY n DESC LIMIT ?",
        (bw, bw, top),
    ).fetchall()
    return {
        "found": True,
        "root_arabic": row["root_arabic"],
        "root_buckwalter": bw,
        "co_roots": [dict(r) for r in rows],
    }


# --------------------------------------------------------------------------
# Passerelle français -> arabe (lexique + thèmes + déduction par le corpus)
# --------------------------------------------------------------------------
_LEXICON_PATH = Path(__file__).resolve().parent / "lexicon_fr.json"
_LEXICON_CACHE: dict | None = None
_LEXICON_MTIME: int | None = None


def load_lexicon() -> dict:
    """Charge lexicon_fr.json (FR -> racines), mis en cache comme themes.json."""
    global _LEXICON_CACHE, _LEXICON_MTIME
    if not _LEXICON_PATH.exists():
        return {}
    mtime = _LEXICON_PATH.stat().st_mtime_ns
    if _LEXICON_CACHE is None or mtime != _LEXICON_MTIME:
        _LEXICON_CACHE = json.loads(_LEXICON_PATH.read_text(encoding="utf-8"))
        _LEXICON_MTIME = mtime
    return _LEXICON_CACHE


def _stem(word: str) -> str:
    """Ébauche de pluriel français : « prieres » -> «priere» (si > 4 lettres)."""
    word = normalize_latin(word)
    if len(word) > 4 and word.endswith(("s", "x")):
        return word[:-1]
    return word


def _query_forms(query: str) -> set:
    """Formes normalisées d'une requête : chaîne entière + tokens (singulier)."""
    q = normalize_latin(query).strip()
    if not q:
        return set()
    forms = {q}
    for w in q.replace("-", " ").replace("'", " ").split():
        forms.add(w)
        forms.add(_stem(w))
    return forms


def _entry_matches(key: str, forms: set, query: str) -> bool:
    """Vrai si l'entrée (clé FR) correspond à la requête."""
    key_n = normalize_latin(key)
    if {key_n, _stem(key_n)} & forms:
        return True
    qn = normalize_latin(query).strip()
    # sous-chaîne pour les libellés multi-mots : « liberte de croyance »
    return len(key_n) > 4 and (key_n in qn or qn in key_n)


def lexicon_candidates(query: str) -> list:
    """Entrées du lexique FR correspondant : [{fr, roots, gloss, source}]."""
    forms = _query_forms(query)
    if not forms:
        return []
    out = []
    for key, spec in load_lexicon().items():
        if key.startswith("_"):
            continue
        if _entry_matches(key, forms, query):
            out.append(
                {
                    "fr": spec.get("label", key),
                    "key": key,
                    "roots": list(spec.get("roots", [])),
                    "gloss": spec.get("gloss", ""),
                    "source": "lexique",
                }
            )
    return out


def themes_fr_candidates(query: str) -> list:
    """Thèmes (themes.json) dont un terme FR correspond à la requête."""
    forms = _query_forms(query)
    if not forms:
        return []
    out = []
    for key, spec in _themes_only().items():
        terms_ok = any(
            {normalize_latin(t), _stem(t)} & forms
            for t in spec.get("terms_fr", [])
        )
        if not terms_ok and not _entry_matches(key, forms, query):
            continue
        roots = list(spec.get("roots", []))
        if not roots:
            continue
        label = spec.get("label", key)
        out.append(
            {
                "fr": label,
                "key": key,
                "roots": roots,
                "gloss": spec.get("description", ""),
                "source": f"thème « {label} »",
            }
        )
    return out


def root_stats(con: sqlite3.Connection, root_bw: str) -> dict | None:
    """Statistiques légères d'une racine (sans charger les occurrences)."""
    row = con.execute(
        "SELECT root_arabic, COUNT(*) AS occurrences, "
        "COUNT(DISTINCT sura || ':' || aya) AS verses "
        "FROM words WHERE root_buckwalter = ? "
        "GROUP BY root_buckwalter",
        (root_bw,),
    ).fetchone()
    if row is None:
        return None
    return {
        "root_bw": root_bw,
        "root_ar": row["root_arabic"],
        "occurrences": row["occurrences"],
        "verses": row["verses"],
    }


def roots_union_stats(con: sqlite3.Connection, root_bws) -> dict:
    """Occurrences et versets distincts pour un ensemble de racines (union).

    Sert de compteur partagé à la passerelle français→arabe : additionner les
    compteurs par racine surestimerait les versets ; ici un verset contenant
    plusieurs racines ciblées n'est compté qu'une fois.
    """
    root_bws = list(dict.fromkeys(r for r in root_bws if r))
    if not root_bws:
        return {"occurrences": 0, "verses": 0}
    qmarks = ",".join("?" * len(root_bws))
    row = con.execute(
        f"SELECT COUNT(*) AS occurrences, "
        f"COUNT(DISTINCT sura || ':' || aya) AS verses "
        f"FROM words WHERE root_buckwalter IN ({qmarks})",
        root_bws,
    ).fetchone()
    return {"occurrences": row["occurrences"] or 0, "verses": row["verses"] or 0}


def resolve_roots(con: sqlite3.Connection, roots) -> list:
    """Ne garde que les racines réellement présentes dans le corpus."""
    out, seen = [], set()
    for r in roots:
        bw = arabic_to_buckwalter(r) if is_arabic(r) else r
        if bw in seen:
            continue
        st = root_stats(con, bw)
        if st:
            seen.add(bw)
            out.append(st)
    return out


def corpus_root_bridge(
    con: sqlite3.Connection,
    query: str,
    limit: int = 100,
    top: int = 6,
    min_hit_ratio: float = 0.3,
    max_corpus_ratio: float = 0.1,
) -> list:
    """Racines déduites du corpus (approche distributionnelle).

    Cherche d'abord les versets dont les traductions contiennent le terme FR,
    puis les racines présentes dans ces versets — en retenant celles qui y sont
    fréquentes (`hit_ratio`) mais rares dans le corpus entier (`lift`).
    """
    rows = search_french(con, query, limit=limit)
    if len(rows) < 2:
        return []
    refs = [(r["sura"], r["aya"]) for r in rows]
    n = len(refs)
    where = " OR ".join("(sura = ? AND aya = ?)" for _ in refs)
    params = [x for ref in refs for x in ref]
    hits = {
        r["root_buckwalter"]: r["nv"]
        for r in con.execute(
            f"SELECT root_buckwalter, "
            f"COUNT(DISTINCT sura || ':' || aya) AS nv "
            f"FROM words WHERE root_buckwalter IS NOT NULL AND ({where}) "
            f"GROUP BY root_buckwalter",
            params,
        )
    }
    if not hits:
        return []
    total = con.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    qmarks = ",".join("?" * len(hits))
    corp = con.execute(
        f"SELECT root_buckwalter, COUNT(DISTINCT sura || ':' || aya) AS nv "
        f"FROM words WHERE root_buckwalter IN ({qmarks}) "
        f"GROUP BY root_buckwalter",
        list(hits),
    ).fetchall()
    out = []
    for r in corp:
        p_hit = hits[r["root_buckwalter"]] / n
        p_all = r["nv"] / total
        if p_all <= 0 or p_hit < min_hit_ratio or p_all > max_corpus_ratio:
            continue
        out.append(
            {
                "root_bw": r["root_buckwalter"],
                "hit_ratio": p_hit,
                "lift": p_hit / p_all,
                "verses": r["nv"],
            }
        )
    out.sort(key=lambda d: (-d["lift"], -d["hit_ratio"]))
    return out[:top]


def french_bridge(
    con: sqlite3.Connection, query: str, limit: int = 100, top_corpus: int = 6
) -> dict:
    """Passerelle FR -> AR : correspondances proposées pour une requête française.

    Trois sources fusionnées et dédupliquées par racine (priorité d'insertion :
    lexique > thème > corpus déduit). Seules les racines présentes dans la
    base sont retournées.
    """
    q = (query or "").strip()
    proposals: dict = {}

    def _add(p: dict) -> None:
        bw = p["root_bw"]
        if bw in proposals:
            for src in p["sources"]:
                if src not in proposals[bw]["sources"]:
                    proposals[bw]["sources"].append(src)
        else:
            proposals[bw] = p

    # Saisie directe d'une racine (arabe ou Buckwalter) : résolution immédiate.
    # Inoffensif pour les mots français (root_stats ne matche pas) — un seul
    # SELECT indexé de plus.
    for st in resolve_roots(con, [q]):
        _add(
            {
                "fr": q,
                "root_bw": st["root_bw"],
                "root_ar": st["root_ar"],
                "occurrences": st["occurrences"],
                "verses": st["verses"],
                "sources": ["racine"],
                "detail": "saisie directe de racine",
            }
        )

    for entry in lexicon_candidates(q):
        for st in resolve_roots(con, entry["roots"]):
            _add(
                {
                    "fr": entry["fr"],
                    "root_bw": st["root_bw"],
                    "root_ar": st["root_ar"],
                    "occurrences": st["occurrences"],
                    "verses": st["verses"],
                    "sources": [entry["source"]],
                    "detail": entry.get("gloss", ""),
                }
            )
    for entry in themes_fr_candidates(q):
        for st in resolve_roots(con, entry["roots"]):
            _add(
                {
                    "fr": entry["fr"],
                    "root_bw": st["root_bw"],
                    "root_ar": st["root_ar"],
                    "occurrences": st["occurrences"],
                    "verses": st["verses"],
                    "sources": [entry["source"]],
                    "detail": entry.get("gloss", ""),
                }
            )

    added_by_corpus = 0
    for c in corpus_root_bridge(con, q, limit=limit, top=top_corpus):
        st = root_stats(con, c["root_bw"])
        if not st:
            continue
        src = f"corpus (lift ×{c['lift']:.0f})"
        if c["root_bw"] in proposals:
            _add({"root_bw": c["root_bw"], "sources": [src]})
            continue
        if added_by_corpus >= top_corpus:
            continue
        added_by_corpus += 1
        _add(
            {
                "fr": q,
                "root_bw": st["root_bw"],
                "root_ar": st["root_ar"],
                "occurrences": st["occurrences"],
                "verses": st["verses"],
                "sources": [src],
                "detail": (
                    f"present dans {c['hit_ratio'] * 100:.0f}% des versets FR "
                    f"touche(s), rare ailleurs"
                ),
            }
        )

    out = []
    for p in proposals.values():
        p["source"] = " · ".join(p.get("sources", []))
        out.append(p)
    return {"query": q, "proposals": out}
