"""Favoris : versets mis de côté et conservés d'une session à l'autre.

Stockage volontairement simple (fichier JSON sous ``data/``), suffisant pour un
outil **local / personnel** : chaque déploiement garde ses propres favoris. Le
fichier est ignoré par git (``data/bookmarks.json``). Aucune donnée n'est
envoyée ailleurs ; aucune dépendance externe.

Format ::

    {
      "2:255": {"sura": 2, "aya": 255, "note": "", "added": "2026-01-01T12:00:00"},
      ...
    }
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from . import config

_BOOKMARKS_PATH = config.DATA_DIR / "bookmarks.json"
_LOCK = threading.Lock()

# Cache mémoire du fichier, invalidé si le fichier change sur le disque. Sans
# cela, ``contains`` relirait le JSON une fois **par verset** affiché.
_CACHE: dict | None = None
_CACHE_MTIME: int | None = None


def _path() -> Path:
    return _BOOKMARKS_PATH


def _key(sura: int, aya: int) -> str:
    return f"{int(sura)}:{int(aya)}"


def _load_cached() -> dict:
    """Version interne : renvoie le dict **caché** (ne pas muter)."""
    global _CACHE, _CACHE_MTIME
    path = _path()
    if not path.exists():
        _CACHE, _CACHE_MTIME = {}, None
        return _CACHE
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        return _CACHE or {}
    if _CACHE is None or _CACHE_MTIME != mtime:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return _CACHE or {}
        _CACHE = data if isinstance(data, dict) else {}
        _CACHE_MTIME = mtime
    return _CACHE


def load() -> dict:
    """Charge tous les favoris : {« sura:aya »: {sura, aya, note, added}}.

    Le fichier est mis en cache et l'invalidité suit son ``mtime`` : les
    lectures répétées (une par verset affiché) ne relisent pas le disque. Une
    copie est renvoyée pour que l'appelant ne mute pas l'état partagé.
    """
    return dict(_load_cached())


def _save(data: dict) -> None:
    global _CACHE, _CACHE_MTIME
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    tmp.replace(path)
    _CACHE, _CACHE_MTIME = None, None


def all_entries() -> list:
    """Tous les favoris, triés par référence (sourate puis verset)."""
    entries = list(_load_cached().values())
    entries.sort(key=lambda e: (int(e.get("sura", 0)), int(e.get("aya", 0))))
    return entries


def contains(sura: int, aya: int) -> bool:
    return _key(sura, aya) in _load_cached()


def add(sura: int, aya: int, note: str = "") -> None:
    """Ajoute (ou met à jour) un verset en favori."""
    with _LOCK:
        data = load()
        k = _key(sura, aya)
        existing = data.get(k, {})
        data[k] = {
            "sura": int(sura),
            "aya": int(aya),
            "note": note if note is not None else existing.get("note", ""),
            "added": existing.get("added")
            or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        _save(data)


def set_note(sura: int, aya: int, note: str) -> None:
    with _LOCK:
        data = load()
        k = _key(sura, aya)
        if k in data:
            data[k]["note"] = note or ""
            _save(data)


def remove(sura: int, aya: int) -> None:
    with _LOCK:
        data = load()
        if data.pop(_key(sura, aya), None) is not None:
            _save(data)


def toggle(sura: int, aya: int, note: str = "") -> bool:
    """Bascule un favori. Retourne True s'il est désormais enregistré."""
    if contains(sura, aya):
        remove(sura, aya)
        return False
    add(sura, aya, note)
    return True


def clear() -> None:
    with _LOCK:
        if _path().exists():
            _save({})


def count() -> int:
    return len(_load_cached())
