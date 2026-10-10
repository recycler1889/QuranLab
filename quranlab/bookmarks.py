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


def _path() -> Path:
    return _BOOKMARKS_PATH


def _key(sura: int, aya: int) -> str:
    return f"{int(sura)}:{int(aya)}"


def load() -> dict:
    """Charge tous les favoris : {« sura:aya »: {sura, aya, note, added}}."""
    path = _path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    tmp.replace(path)


def all_entries() -> list:
    """Tous les favoris, triés par référence (sourate puis verset)."""
    data = load()
    entries = list(data.values())
    entries.sort(key=lambda e: (int(e.get("sura", 0)), int(e.get("aya", 0))))
    return entries


def contains(sura: int, aya: int) -> bool:
    return _key(sura, aya) in load()


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
    return len(load())
