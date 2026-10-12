"""Génération de questions d'apprentissage (contexte + reconnaissance de racine).

Deux types d'exercices, tous deux **ancrés sur le texte** :

* **Quiz de contexte** : un verset contenant la racine cible est affiché (mot
  cible surligné) ; il faut choisir la bonne glose parmi des leurres.
* **Reconnaissance de racine** : une forme du corpus est montrée ; il faut
  identifier sa racine parmi d'autres racines réelles.

Les fonctions ``build_choices`` et ``grade`` sont pures et testables sans base.
"""

from __future__ import annotations

import random
import sqlite3

from . import cache, config, srs, vocab


def build_choices(correct: str, distractors, n: int = 4,
                  rng: random.Random | None = None) -> list:
    """Assemble ``n`` propositions (bonne réponse + leurres distincts).

    Renvoie une liste de ``{"text": str, "correct": bool}`` mélangée. Le
    nombre réel de propositions peut être inférieur à ``n`` si les leurres
    disponibles sont insuffisants (jamais en dessous de 2).
    """
    rng = rng or random
    correct = (correct or "").strip()
    pool = []
    seen = {correct}
    for d in distractors or []:
        d = (d or "").strip()
        if d and d not in seen:
            seen.add(d)
            pool.append(d)
    rng.shuffle(pool)
    picked = pool[:max(1, int(n) - 1)]
    options = [{"text": correct, "correct": True}]
    options += [{"text": d, "correct": False} for d in picked]
    rng.shuffle(options)
    return options


def grade(correct: bool) -> str:
    """Note SRS correspondant à une réponse de quiz."""
    return srs.GRADE_GOOD if correct else srs.GRADE_AGAIN


def context_question(con: sqlite3.Connection, card: dict, lang: str = "fr",
                     rng: random.Random | None = None) -> dict | None:
    """Question de contexte pour une carte-racine (voir module docstring)."""
    rng = rng or random
    root_bw = (card or {}).get("id")
    if not root_bw:
        return None
    verses = vocab.sample_verses(con, root_bw, limit=50)
    if not verses:
        return None
    ref = rng.choice(verses)
    tokens = vocab.verse_tokens(con, ref["sura"], ref["aya"])
    target = next(
        (i for i, t in enumerate(tokens)
         if t.get("root_buckwalter") == root_bw), None
    )
    if target is None:
        return None

    answer = card.get("label") or vocab.root_gloss(root_bw, lang)
    if not answer:
        return None
    distractors = [
        r["gloss"] for r in cache.frequent_roots_cached(
            con, config.LEARN_TOP_ROOTS, lang=lang)
        if r["root_bw"] != root_bw and r.get("gloss")
    ]
    options = build_choices(answer, distractors, config.LEARN_QUIZ_CHOICES, rng)
    return {
        "kind": "context",
        "sura": ref["sura"],
        "aya": ref["aya"],
        "ref": f"{ref['sura']}:{ref['aya']}",
        "tokens": tokens,
        "target_index": target,
        "root_bw": root_bw,
        "root_ar": card.get("ar") or "",
        "options": options,
        "answer": answer,
    }


def root_question(con: sqlite3.Connection, lang: str = "fr",
                  rng: random.Random | None = None) -> dict | None:
    """Question de reconnaissance de racine à partir d'une forme du corpus."""
    rng = rng or random
    lemmas = [
        lemma for lemma in cache.frequent_lemmas_cached(
            con, config.LEARN_TOP_ROOTS)
        if lemma.get("root_bw") and lemma.get("root_ar")
    ]
    if not lemmas:
        return None
    lemma = rng.choice(lemmas)
    row = con.execute(
        "SELECT form_arabic, transliteration FROM words "
        "WHERE lemma_buckwalter = ? LIMIT 1",
        (lemma["lemma_bw"],),
    ).fetchone()
    if row is None:
        return None
    answer = lemma["root_ar"]
    distractors = [
        r["root_ar"] for r in cache.frequent_roots_cached(
            con, config.LEARN_TOP_ROOTS)
        if r["root_bw"] != lemma["root_bw"] and r.get("root_ar")
    ]
    options = build_choices(answer, distractors, config.LEARN_QUIZ_CHOICES, rng)
    return {
        "kind": "root",
        "form": row["form_arabic"],
        "transliteration": row["transliteration"],
        "lemma_bw": lemma["lemma_bw"],
        "root_bw": lemma["root_bw"],
        "root_ar": lemma["root_ar"],
        "options": options,
        "answer": answer,
    }
