"""Construction de la base SQLite à partir des sources brutes.

Schéma :
  surahs            métadonnées des 114 sourates
  verses            texte arabe (uthmani + simple) et texte normalisé
  translations      catalogue des traductions
  translation_verses traduction verset par verset
  words             un enregistrement par mot : forme, racine, lemme, POS
  segments          découpage morphologique fin (préfixe/radical/suffixe)
"""

import json
import re
import sqlite3
from pathlib import Path

from . import config
from .buckwalter import (
    buckwalter_to_arabic,
    buckwalter_to_latin,
    clean_arabic,
    normalize_arabic,
    normalize_latin,
    strip_buckwalter_noise,
)

_LOC = re.compile(r"^\((\d+):(\d+):(\d+):(\d+)\)$")

SCHEMA = """
DROP TABLE IF EXISTS segments;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS translation_verses;
DROP TABLE IF EXISTS translations;
DROP TABLE IF EXISTS verses;
DROP TABLE IF EXISTS surahs;

CREATE TABLE surahs (
    number        INTEGER PRIMARY KEY,
    name_translit TEXT,
    name_ar       TEXT,
    name_en       TEXT,
    revelation    TEXT,
    verses_count  INTEGER
);

CREATE TABLE verses (
    sura             INTEGER NOT NULL,
    aya              INTEGER NOT NULL,
    text_uthmani     TEXT NOT NULL,
    text_simple      TEXT NOT NULL,
    text_simple_norm TEXT NOT NULL,
    PRIMARY KEY (sura, aya)
);

CREATE TABLE translations (
    id       INTEGER PRIMARY KEY,
    key      TEXT UNIQUE NOT NULL,
    author   TEXT NOT NULL,
    language TEXT NOT NULL
);

CREATE TABLE translation_verses (
    translation_id INTEGER NOT NULL,
    sura           INTEGER NOT NULL,
    aya            INTEGER NOT NULL,
    text           TEXT NOT NULL,
    text_norm      TEXT NOT NULL,
    PRIMARY KEY (translation_id, sura, aya)
);

CREATE TABLE words (
    id              INTEGER PRIMARY KEY,
    sura            INTEGER NOT NULL,
    aya             INTEGER NOT NULL,
    word_index      INTEGER NOT NULL,
    form_buckwalter TEXT,
    form_arabic     TEXT,
    transliteration TEXT,
    root_buckwalter TEXT,
    root_arabic     TEXT,
    root_norm       TEXT,
    lemma_buckwalter TEXT,
    pos             TEXT,
    UNIQUE (sura, aya, word_index)
);

CREATE TABLE segments (
    id              INTEGER PRIMARY KEY,
    sura            INTEGER NOT NULL,
    aya             INTEGER NOT NULL,
    word_index      INTEGER NOT NULL,
    segment_index   INTEGER NOT NULL,
    form_buckwalter TEXT,
    tag             TEXT,
    features        TEXT,
    UNIQUE (sura, aya, word_index, segment_index)
);

CREATE INDEX idx_words_root ON words (root_norm);
CREATE INDEX idx_words_root_bw ON words (root_buckwalter);
CREATE INDEX idx_words_verse ON words (sura, aya);
CREATE INDEX idx_segments_verse ON segments (sura, aya, word_index);
CREATE INDEX idx_tv_sura ON translation_verses (sura, aya);
"""


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edition_to_dict(path: Path) -> dict:
    """Transforme une édition {quran:[{chapter,verse,text}]} en dict (sura,aya)->text."""
    data = _load_json(path)
    return {(v["chapter"], v["verse"]): v["text"] for v in data["quran"]}


def parse_morphology(path: Path):
    """Retourne (words, segments).

    words    : (sura, aya, word) -> {forms, root, lemma, pos}
    segments : liste de tuples (sura, aya, word, seg, form, tag, features)
    """
    words: dict = {}
    segments: list = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("("):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            m = _LOC.match(parts[0])
            if not m:
                continue
            sura, aya, word, seg = (int(x) for x in m.groups())
            form, tag = parts[1], parts[2]
            features = parts[3] if len(parts) > 3 else ""
            segments.append((sura, aya, word, seg, form, tag, features))
            entry = words.setdefault(
                (sura, aya, word),
                {"forms": [], "root": None, "lemma": None, "pos": None},
            )
            entry["forms"].append((seg, form))
            for token in features.split("|"):
                if token.startswith("ROOT:") and entry["root"] is None:
                    entry["root"] = token[5:]
                elif token.startswith("LEM:") and entry["lemma"] is None:
                    entry["lemma"] = token[4:]
                elif token.startswith("POS:") and entry["pos"] is None:
                    entry["pos"] = token[4:]
    return words, segments


def build(db_path: Path = config.DB_PATH, verbose: bool = True) -> Path:
    raw = config.RAW_DIR
    uthmani = _edition_to_dict(raw / "ara-uthmani.json")
    simple = _edition_to_dict(raw / "ara-simple.json")
    info = _load_json(raw / "info.json")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript(SCHEMA)

        # --- Sourates ---------------------------------------------------
        chapters = {c["chapter"]: c for c in info["chapters"]}
        counts: dict = {}
        for (sura, _aya) in uthmani:
            counts[sura] = counts.get(sura, 0) + 1
        for number in range(1, 115):
            c = chapters.get(number, {})
            con.execute(
                "INSERT INTO surahs VALUES (?,?,?,?,?,?)",
                (
                    number,
                    c.get("name", ""),
                    c.get("arabicname", ""),
                    c.get("englishname", ""),
                    c.get("revelation", ""),
                    counts.get(number, 0),
                ),
            )

        # --- Versets ----------------------------------------------------
        verse_rows = []
        for (sura, aya), text in uthmani.items():
            simple_text = simple.get((sura, aya), text)
            verse_rows.append(
                (
                    sura,
                    aya,
                    text,
                    simple_text,
                    normalize_arabic(simple_text),
                )
            )
        con.executemany("INSERT INTO verses VALUES (?,?,?,?,?)", verse_rows)

        # --- Traductions ------------------------------------------------
        for tr in config.TRANSLATIONS:
            cur = con.execute(
                "INSERT INTO translations (key, author, language) VALUES (?,?,?)",
                (tr["key"], tr["author"], tr["language"]),
            )
            tid = cur.lastrowid
            trans = _edition_to_dict(raw / f"{tr['edition']}.json")
            rows = [
                (tid, sura, aya, text, normalize_latin(text))
                for (sura, aya), text in trans.items()
            ]
            con.executemany(
                "INSERT INTO translation_verses VALUES (?,?,?,?,?)", rows
            )

        # --- Morphologie : mots et segments -----------------------------
        words, segments = parse_morphology(raw / "morphology.txt")
        word_rows = []
        for (sura, aya, word_index), entry in words.items():
            forms = strip_buckwalter_noise(
                "".join(f for _seg, f in sorted(entry["forms"]))
            )
            root_bw = entry["root"]
            root_ar = buckwalter_to_arabic(root_bw) if root_bw else None
            word_rows.append(
                (
                    sura,
                    aya,
                    word_index,
                    forms,
                    clean_arabic(buckwalter_to_arabic(forms)),
                    buckwalter_to_latin(forms),
                    root_bw,
                    root_ar,
                    normalize_arabic(root_ar) if root_ar else None,
                    entry["lemma"],
                    entry["pos"],
                )
            )
        con.executemany(
            "INSERT INTO words VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)", word_rows
        )
        con.executemany(
            "INSERT INTO segments VALUES (NULL,?,?,?,?,?,?,?)", segments
        )

        con.commit()

        if verbose:
            stats = {
                "sourates": con.execute("SELECT COUNT(*) FROM surahs").fetchone()[0],
                "versets": con.execute("SELECT COUNT(*) FROM verses").fetchone()[0],
                "mots": con.execute("SELECT COUNT(*) FROM words").fetchone()[0],
                "segments": con.execute("SELECT COUNT(*) FROM segments").fetchone()[0],
                "traductions": con.execute(
                    "SELECT COUNT(*) FROM translations"
                ).fetchone()[0],
                "racines uniques": con.execute(
                    "SELECT COUNT(DISTINCT root_norm) FROM words "
                    "WHERE root_norm IS NOT NULL"
                ).fetchone()[0],
            }
            print("Base construite :", db_path)
            for k, v in stats.items():
                print(f"  {k:20s}: {v}")
    finally:
        con.close()
    return db_path


def ensure_db(db_path: Path = config.DB_PATH, verbose: bool = True) -> Path:
    """Garantit la présence de la base.

    Si la base n'existe pas (cas d'un déploiement cloud où data/ est ignoré par
    git), elle est téléchargée et construite automatiquement. Sinon, la base
    existante est réutilisée telle quelle.
    """
    if Path(db_path).exists():
        return db_path
    from . import download

    download.download_all()
    return build(db_path, verbose=verbose)


if __name__ == "__main__":
    build()
