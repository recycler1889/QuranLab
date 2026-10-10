"""Ordonnancement de répétition espacée (SRS) — algorithme pur, sans IHM.

Réimplémentation simplifiée de l'algorithme SM-2 (inspiré d'Anki) : chaque
« carte » (une racine ou un lemme du lexique coranique) porte un facteur de
facilité, un intervalle, un nombre de répétitions et une échéance. Réviser une
carte avec une note la replanifie.

Module volontairement **sans dépendance** (à Streamlit, à la base ou à la
config) pour rester testable de façon isolée. ``learning.py`` y ajoute la
persistance et l'orchestration.

États d'une carte :
  * ``new``      : jamais révisée ;
  * ``learning`` : en cours d'acquisition (intervalles en minutes) ;
  * ``review``   : en révision espacée (intervalles en jours).
"""

from __future__ import annotations

from datetime import datetime, timedelta

# Notes possibles (de l'échec à la réussite facile), façon Anki.
GRADE_AGAIN = "again"
GRADE_HARD = "hard"
GRADE_GOOD = "good"
GRADE_EASY = "easy"
GRADES = (GRADE_AGAIN, GRADE_HARD, GRADE_GOOD, GRADE_EASY)

# Notes numériques (rétrocompatibilité : 0..3).
_NUM_TO_GRADE = {0: GRADE_AGAIN, 1: GRADE_HARD, 2: GRADE_GOOD, 3: GRADE_EASY}

_DEFAULT_STEPS = (1, 10)  # minutes
_EASY_INTERVAL = 4        # jours, à la première réussite « facile »
_MAX_INTERVAL = 36500     # plafond (~100 ans) : évite tout débordement de date


def _grade_name(grade) -> str:
    """Normalise une note (chaîne ou entier 0..3) en nom canonique."""
    if isinstance(grade, int):
        return _NUM_TO_GRADE.get(grade, GRADE_GOOD)
    g = str(grade).strip().lower()
    return g if g in GRADES else GRADE_GOOD


def _now(now=None) -> datetime:
    """Horodatage courant (naïf) ou conversion d'une valeur fournie."""
    if now is None:
        return datetime.now()
    if isinstance(now, datetime):
        return now
    return datetime.fromisoformat(str(now))


def _steps(steps) -> tuple:
    steps = tuple(int(s) for s in (steps or _DEFAULT_STEPS))
    return steps or _DEFAULT_STEPS


def new_card(kind: str, ident: str, ar: str | None = None,
             label: str = "", now=None) -> dict:
    """Crée une carte neuve (état ``new``), due immédiatement."""
    stamp = _now(now).isoformat(timespec="seconds")
    return {
        "kind": kind,
        "id": ident,
        "ar": ar or "",
        "label": label or "",
        "state": "new",
        "ease": 2.5,
        "interval": 0.0,
        "reps": 0,
        "lapses": 0,
        "step": 0,
        "due": stamp,
        "last": None,
    }


def is_due(card: dict, now=None) -> bool:
    """Vrai si la carte est à réviser (échéance atteinte ou dépassée)."""
    if not card:
        return False
    if card.get("state") == "new":
        return True
    due = card.get("due")
    if not due:
        return True
    try:
        return _now(now) >= datetime.fromisoformat(str(due))
    except (TypeError, ValueError):
        return True


def mastery(card: dict, reps: int = 2) -> bool:
    """Vrai si la carte est maîtrisée (révisée assez de fois en ``review``)."""
    if not card:
        return False
    return card.get("state") == "review" and int(card.get("reps", 0)) >= int(reps)


def review(card: dict, grade, steps=_DEFAULT_STEPS, now=None) -> dict:
    """Replanifie une carte après révision. Renvoie une **copie** modifiée.

    ``grade`` : ``again`` / ``hard`` / ``good`` / ``easy`` (ou entier 0..3).
    """
    g = _grade_name(grade)
    s = _steps(steps)
    now_dt = _now(now)
    c = dict(card or new_card("root", ""))
    c.setdefault("ease", 2.5)
    c.setdefault("interval", 0.0)
    c.setdefault("reps", 0)
    c.setdefault("lapses", 0)
    c.setdefault("step", 0)
    c["last"] = now_dt.isoformat(timespec="seconds")

    state = c.get("state", "new")

    if state in ("new", "learning"):
        if g == GRADE_AGAIN:
            c["step"] = 0
            c["lapses"] = int(c.get("lapses", 0)) + 1
            c["state"] = "learning"
            c["due"] = (now_dt + timedelta(minutes=s[0])).isoformat(
                timespec="seconds")
        elif g == GRADE_HARD:
            c["state"] = "learning"
            c["due"] = (now_dt + timedelta(minutes=s[0])).isoformat(
                timespec="seconds")
        elif g == GRADE_EASY:
            c["state"] = "review"
            c["interval"] = float(_EASY_INTERVAL)
            c["reps"] = int(c.get("reps", 0)) + 1
            c["due"] = (now_dt + timedelta(days=_EASY_INTERVAL)).isoformat(
                timespec="seconds")
        else:  # good
            step = int(c.get("step", 0)) + 1
            if step >= len(s):
                c["state"] = "review"
                c["interval"] = 1.0
                c["step"] = 0
                c["reps"] = int(c.get("reps", 0)) + 1
                c["due"] = (now_dt + timedelta(days=1)).isoformat(
                    timespec="seconds")
            else:
                c["state"] = "learning"
                c["step"] = step
                c["due"] = (now_dt + timedelta(minutes=s[step])).isoformat(
                    timespec="seconds")
        return c

    # --- État « review » : progression espacée ---------------------------
    ease = float(c.get("ease", 2.5))
    interval = float(c.get("interval", 1.0))
    if g == GRADE_AGAIN:
        ease = max(1.3, ease - 0.2)
        c["lapses"] = int(c.get("lapses", 0)) + 1
        c["state"] = "learning"
        c["step"] = 0
        c["due"] = (now_dt + timedelta(minutes=s[0])).isoformat(
            timespec="seconds")
        c["ease"] = round(ease, 3)
        return c
    if g == GRADE_HARD:
        ease = max(1.3, ease - 0.15)
        interval = max(1.0, interval * 1.2)
    elif g == GRADE_EASY:
        ease = min(3.0, ease + 0.15)
        interval = interval * ease * 1.3
    else:  # good
        interval = interval * ease

    interval = min(float(_MAX_INTERVAL), max(1.0, round(interval)))
    c["ease"] = round(ease, 3)
    c["interval"] = interval
    c["reps"] = int(c.get("reps", 0)) + 1
    c["state"] = "review"
    c["due"] = (now_dt + timedelta(days=interval)).isoformat(
        timespec="seconds")
    return c
