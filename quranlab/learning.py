"""Progression d'apprentissage : store JSON local + files d'attente SRS.

Pendant du module ``bookmarks`` : la progression (cartes de répétition espacée,
objectifs quotidiens, journal) est conservée dans ``data/learning.json`` —
propre à chaque déploiement, aucune donnée envoyée ailleurs. La logique
d'ordonnancement vit dans ``srs.py`` ; ici on persiste et on agrège.

Format ::

    {
      "version": 1,
      "cards": {"root:rHm": {...carte srs...}},
      "settings": {"daily_new": 5, "daily_review": 20, "reminders": false},
      "daily": {"2026-10-10": {"reviews": 12, "new": 5, "correct": 9}}
    }
"""

from __future__ import annotations

import json
import threading
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config, srs

_LEARNING_PATH = getattr(config, "LEARNING_PATH", config.DATA_DIR / "learning.json")
_LOCK = threading.Lock()
_VERSION = 1


def _path() -> Path:
    return Path(_LEARNING_PATH)


def _ckey(kind: str, ident: str) -> str:
    return f"{kind}:{ident}"


def _default_settings() -> dict:
    return {
        "daily_new": int(getattr(config, "LEARN_DEFAULT_DAILY_NEW", 5)),
        "daily_review": int(getattr(config, "LEARN_DEFAULT_DAILY_REVIEW", 20)),
        "reminders": False,
    }


def _empty() -> dict:
    return {"version": _VERSION, "cards": {}, "settings": _default_settings(),
            "daily": {}}


def load() -> dict:
    """Charge le store (structure normalisée, jamais None)."""
    path = _path()
    if not path.exists():
        return _empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _empty()
    if not isinstance(data, dict):
        return _empty()
    data.setdefault("version", _VERSION)
    data.setdefault("cards", {})
    data.setdefault("daily", {})
    settings = _default_settings()
    settings.update(data.get("settings") or {})
    data["settings"] = settings
    return data


def _save(data: dict) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    tmp.replace(path)


# --- Objectifs ------------------------------------------------------------
def get_settings() -> dict:
    return dict(load()["settings"])


def set_settings(**kw) -> dict:
    """Met à jour les objectifs (daily_new, daily_review, reminders)."""
    with _LOCK:
        data = load()
        settings = data["settings"]
        for key in ("daily_new", "daily_review"):
            if key in kw and kw[key] is not None:
                try:
                    settings[key] = max(0, int(kw[key]))
                except (TypeError, ValueError):
                    pass
        if "reminders" in kw and kw["reminders"] is not None:
            settings["reminders"] = bool(kw["reminders"])
        _save(data)
    return dict(settings)


# --- Cartes ---------------------------------------------------------------
def get_card(kind: str, ident: str) -> dict | None:
    return load()["cards"].get(_ckey(kind, ident))


def ensure_card(kind: str, ident: str, ar: str = "",
                label: str = "") -> dict:
    """Récupère la carte, ou la crée si absente (sans écraser l'existante)."""
    key = _ckey(kind, ident)
    with _LOCK:
        data = load()
        card = data["cards"].get(key)
        if card is None:
            card = srs.new_card(kind, ident, ar=ar, label=label)
            data["cards"][key] = card
            _save(data)
        return card


def has_card(kind: str, ident: str) -> bool:
    return _ckey(kind, ident) in load()["cards"]


def _today(now=None) -> str:
    return (now or datetime.now()).date().isoformat()


def record_review(kind: str, ident: str, grade, now=None,
                  ar: str = "", label: str = "") -> dict:
    """Applique une révision SRS et met à jour le journal du jour."""
    steps = getattr(config, "LEARN_STEPS", srs._DEFAULT_STEPS)
    key = _ckey(kind, ident)
    with _LOCK:
        data = load()
        card = data["cards"].get(key)
        is_new = card is None or card.get("state") == "new"
        if card is None:
            card = srs.new_card(kind, ident, ar=ar, label=label)
        card = srs.review(card, grade, steps=steps, now=now)
        data["cards"][key] = card
        day = _today(now)
        entry = data["daily"].setdefault(day, {"reviews": 0, "new": 0,
                                               "correct": 0})
        entry["reviews"] = int(entry.get("reviews", 0)) + 1
        if is_new:
            entry["new"] = int(entry.get("new", 0)) + 1
        if srs._grade_name(grade) in (srs.GRADE_GOOD, srs.GRADE_EASY):
            entry["correct"] = int(entry.get("correct", 0)) + 1
        _save(data)
    return card


def all_cards() -> list:
    cards = list(load()["cards"].values())
    cards.sort(key=lambda c: (c.get("kind", ""), c.get("id", "")))
    return cards


def due_cards(limit: int | None = None, now=None) -> list:
    """Cartes à réviser maintenant, triées par échéance."""
    cards = [c for c in load()["cards"].values() if srs.is_due(c, now)]
    cards.sort(key=lambda c: (str(c.get("due") or ""), c.get("id", "")))
    return cards[:limit] if limit else cards


def new_queue(con, count: int | None = None, lang: str | None = None) -> list:
    """Cartes neuves à introduire (racines fréquentes pas encore vues).

    ``con`` : connexion SQLite (pour le classement par fréquence). ``lang``
    localise la glose persistée comme libellé de carte (par défaut, la langue
    d'interface active) — sans quoi les cartes seraient toujours en français.
    Import paresseux de ``cache`` pour éviter toute dépendance circulaire.
    """
    from . import cache, i18n  # import local : évite un cycle d'imports

    lg = lang or i18n.lang()
    settings = get_settings()
    n = settings["daily_new"] if count is None else count
    if n <= 0:
        return []
    cards = load()["cards"]
    out = []
    for root in cache.frequent_roots_cached(con, config.LEARN_TOP_ROOTS, lang=lg):
        if _ckey("root", root["root_bw"]) in cards:
            continue
        out.append({
            "kind": "root",
            "id": root["root_bw"],
            "ar": root["root_ar"],
            "label": root.get("gloss", ""),
        })
        if len(out) >= n:
            break
    return out


# --- Statistiques ---------------------------------------------------------
def _streak(daily: dict, today: date | None = None) -> int:
    today = today or date.today()
    streak = 0
    cursor = today
    while True:
        key = cursor.isoformat()
        entry = daily.get(key)
        if entry and int(entry.get("reviews", 0)) > 0:
            streak += 1
            cursor = cursor - timedelta(days=1)
        else:
            break
    return streak


def stats(con=None, now=None) -> dict:
    """Indicateurs du tableau de bord.

    ``mastered_roots`` / ``coverage_pct`` ne sont calculés que si ``con`` est
    fourni (classement des racines fréquentes).
    """
    now_dt = now or datetime.now()
    data = load()
    cards = data["cards"]
    day = data["daily"].get(_today(now_dt), {})
    root_cards = [c for c in cards.values() if c.get("kind") == "root"]
    mastered = [c for c in root_cards
                if srs.mastery(c, getattr(config, "LEARN_MASTERY_REPS", 2))]

    result = {
        "total_cards": len(cards),
        "due": len(due_cards(now=now_dt)),
        "reviews_today": int(day.get("reviews", 0)),
        "new_today": int(day.get("new", 0)),
        "correct_today": int(day.get("correct", 0)),
        "streak": _streak(data["daily"], now_dt.date()),
        "mastered_roots": len(mastered),
        "coverage_pct": None,
        "vocab_total": None,
    }

    if con is not None:
        from . import cache  # import local

        top = cache.frequent_roots_cached(con, config.LEARN_TOP_ROOTS)
        total = len(top)
        ids = {r["root_bw"] for r in top}
        m = sum(1 for c in mastered if c.get("id") in ids)
        result["vocab_total"] = total
        result["coverage_pct"] = (m / total * 100.0) if total else 0.0
    return result
