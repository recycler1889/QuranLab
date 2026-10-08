"""Téléchargement des sources textuelles dans data/raw/."""

import json
import urllib.request
from pathlib import Path

from . import config

_UA = "quranlab/0.1 (outil local de recherche intra-coranique)"


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def _fetch_json(url: str) -> dict:
    return json.loads(_fetch(url).decode("utf-8"))


def download_texts(force: bool = False) -> dict:
    """Télécharge le texte arabe, les métadonnées et les traductions.

    Retourne un dictionnaire des fichiers écrits.
    """
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    written = {}

    # Texte arabe (uthmani + simple)
    for label, edition in config.ARABIC_EDITIONS.items():
        dest = config.RAW_DIR / f"ara-{label}.json"
        if force or not dest.exists():
            data = _fetch_json(f"{config.QURAN_API}/{edition}.json")
            dest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        written[f"ara-{label}"] = dest
        print(f"  [texte]     {dest.name}")

    # Métadonnées des sourates
    info_dest = config.RAW_DIR / "info.json"
    if force or not info_dest.exists():
        info_dest.write_text(
            json.dumps(_fetch_json(config.INFO_URL), ensure_ascii=False),
            encoding="utf-8",
        )
    written["info"] = info_dest
    print(f"  [métadonnées] {info_dest.name}")

    # Traductions françaises
    for tr in config.TRANSLATIONS:
        dest = config.RAW_DIR / f"{tr['edition']}.json"
        if force or not dest.exists():
            data = _fetch_json(f"{config.QURAN_API}/{tr['edition']}.json")
            dest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        written[tr["key"]] = dest
        print(f"  [traduction] {tr['author']:32s} -> {dest.name}")

    # Morphologie / racines
    morph_dest = config.RAW_DIR / "morphology.txt"
    if force or not morph_dest.exists():
        morph_dest.write_bytes(_fetch(config.MORPHOLOGY_URL))
    written["morphology"] = morph_dest
    print(f"  [morphologie] {morph_dest.name}")

    return written


def download_all(force: bool = False) -> dict:
    print("Téléchargement des sources textuelles...")
    return download_texts(force=force)
