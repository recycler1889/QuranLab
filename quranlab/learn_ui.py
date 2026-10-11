"""Onglet « Apprendre » : tableau de bord, révision espacée, quiz, inspecteur.

Regroupe l'IHM de l'apprentissage. La logique vit dans ``srs``,
``learning``, ``vocab`` et ``quiz`` ; ce module ne fait que l'orchestrer et
l'afficher (comme ``ui`` pour le reste de l'application).
"""

from __future__ import annotations

import random

import streamlit as st

from . import cache, config, i18n, learning, quiz, search, srs, ui, vocab

t = i18n.t

# Clés de session (état de la session de révision et des quiz).
# NB : ces clés de *session* ne doivent jamais coïncider avec une clé de
# *widget* (sinon Streamlit interdit l'écriture via st.session_state).
_Q = "learn_queue_state"
_POS = "learn_pos_state"
_REVEAL = "learn_reveal_state"
_QC = "learn_quiz_context"
_QR = "learn_quiz_root"
_TOASTED = "learn_toasted"


# --------------------------------------------------------------------------
# Inspecteur de mot (volet ouvert au clic sur un mot — paramètre `appw`)
# --------------------------------------------------------------------------
def _parse_appw(value) -> tuple[int, int, int] | None:
    if not value:
        return None
    parts = str(value).split(":")
    if len(parts) != 3:
        return None
    try:
        sura, aya, wi = (int(p) for p in parts)
    except ValueError:
        return None
    if sura < 1 or aya < 1 or wi < 1:
        return None
    return sura, aya, wi


def word_inspector(con) -> None:
    """Affiche la fiche du mot sélectionné (clic sur un mot cliquable).

    Sans sélection, affiche une brève astuce d'usage.
    """
    value = None
    try:
        value = st.query_params.get("appw")
    except Exception:  # noqa: BLE001 — hors contexte Streamlit
        value = None
    parsed = _parse_appw(value)
    if not parsed:
        if st.session_state.get("learn_clickable"):
            st.caption(t("learn.click_hint"))
        return

    sura, aya, wi = parsed
    info = vocab.word_info(con, sura, aya, wi, i18n.lang())
    with st.container(border=True):
        if info is None:
            st.warning(t("learn.no_vocab"))
            return
        head = f"**{info.get('form_arabic', '')}**"
        if info.get("transliteration"):
            head += f"  ·  *{info['transliteration']}*"
        st.markdown(f"{t('learn.inspect_title')} — {info['ref']}")
        st.markdown(
            f"<div dir='rtl' lang='ar' style='font-size:1.8rem;"
            f"line-height:2'>{info.get('form_arabic', '')}</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        cols[0].markdown(f"**{t('learn.inspect_root')}** : "
                         f"{info.get('root_arabic') or '—'} "
                         f"[{info.get('root_buckwalter') or '—'}]")
        cols[0].markdown(f"**{t('learn.inspect_lemma')}** : "
                         f"{info.get('lemma_buckwalter') or '—'}")
        cols[1].markdown(f"**{t('learn.inspect_pos')}** : "
                         f"{info.get('pos') or '—'}")
        if info.get("gloss"):
            cols[1].markdown(f"**{t('learn.inspect_gloss')}** : "
                             f"{info['gloss']}")

        st.caption(
            t("learn.inspect_freq_form", n=info["form_count"]) + " · "
            + t("learn.inspect_lemma", n=info["lemma_count"]) + " · "
            + t("learn.inspect_freq_root", n=info["root_count"],
                v=info["root_verses"])
        )

        if info.get("root_forms"):
            forms = " · ".join(
                f"{f['form']} ({f['count']})" for f in info["root_forms"]
            )
            st.caption(f"{t('learn.inspect_root_forms')} : {forms}")

        for tr in ui.translations_for_lang(info.get("translations", [])):
            st.markdown(f"**{tr['author']}** — {tr['text']}")

        actions = st.columns([1, 1, 1])
        if info.get("gloss") and st.session_state.get("show_tts", True):
            if actions[0].button(t("ui.listen"), key=ui.unique_key("wi_tts")):
                ui.tts(info["gloss"], i18n.lang())
        if info.get("root_buckwalter"):
            if actions[1].button(t("learn.add_card"),
                                 key=ui.unique_key("wi_add")):
                learning.ensure_card(
                    "root", info["root_buckwalter"],
                    ar=info.get("root_arabic", ""), label=info.get("gloss", ""),
                )
                st.success(t("learn.added"))
        if actions[2].button(t("learn.close"), key=ui.unique_key("wi_close")):
            try:
                del st.query_params["appw"]
            except Exception:  # noqa: BLE001
                pass
            st.rerun()


# --------------------------------------------------------------------------
# Réglages (barre latérale)
# --------------------------------------------------------------------------
def learning_settings() -> None:
    """Objectifs quotidiens et rappels (barre latérale)."""
    settings = learning.get_settings()
    with st.expander(t("learn.goals_header")):
        new_goal = st.number_input(
            t("learn.goal_new"), min_value=0, max_value=100,
            value=int(settings.get("daily_new", 5)), step=1,
            key="learn_goal_new",
        )
        review_goal = st.number_input(
            t("learn.goal_review"), min_value=0, max_value=500,
            value=int(settings.get("daily_review", 20)), step=5,
            key="learn_goal_review",
        )
        reminders = st.checkbox(
            t("learn.reminders"), value=bool(settings.get("reminders")),
            help=t("learn.reminders_help"), key="learn_reminders",
        )
        if st.button(t("learn.settings_saved"), key=ui.unique_key("learn_save")):
            learning.set_settings(
                daily_new=int(new_goal), daily_review=int(review_goal),
                reminders=bool(reminders),
            )
            st.success(t("learn.settings_saved"))


# --------------------------------------------------------------------------
# Aides
# --------------------------------------------------------------------------
def _pick_card(con) -> dict | None:
    """Une carte à réviser : priorité aux cartes dues, sinon racine fréquente."""
    due = learning.due_cards(limit=1)
    if due:
        return due[0]
    roots = cache.frequent_roots_cached(con, config.LEARN_TOP_ROOTS,
                                        lang=i18n.lang())
    if not roots:
        return None
    r = random.choice(roots)
    return {"kind": "root", "id": r["root_bw"], "ar": r["root_ar"],
            "label": r.get("gloss", "")}


def _dashboard(con) -> None:
    stats = learning.stats(con)
    cols = st.columns(5)
    cols[0].metric(t("learn.m_due"), stats["due"])
    cols[1].metric(t("learn.m_reviews_today"), stats["reviews_today"])
    cols[2].metric(t("learn.m_new_today"), stats["new_today"])
    cols[3].metric(t("learn.m_streak"), stats["streak"])
    cols[4].metric(t("learn.m_mastered"), stats["mastered_roots"])
    if stats.get("coverage_pct") is not None:
        st.progress(min(1.0, stats["coverage_pct"] / 100.0))
        st.caption(t("learn.coverage_fmt",
                     n=stats["mastered_roots"], total=stats["vocab_total"]))
    else:
        st.caption(t("learn.coverage_na"))
    if stats["due"] and learning.get_settings().get("reminders") \
            and not st.session_state.get(_TOASTED):
        st.toast(f"{t('learn.m_due')} : {stats['due']}")
        st.session_state[_TOASTED] = True


# --------------------------------------------------------------------------
# Session de révision espacée
# --------------------------------------------------------------------------
def _review_session(con) -> None:
    st.subheader(t("learn.reviewing"))
    if st.session_state.get(_Q) is None:
        if st.button(t("learn.start"), key=ui.unique_key("learn_start")):
            settings = learning.get_settings()
            queue = learning.due_cards(limit=int(settings["daily_review"]))
            queue += learning.new_queue(con, int(settings["daily_new"]))
            st.session_state[_Q] = queue
            st.session_state[_POS] = 0
            st.session_state[_REVEAL] = False
            st.rerun()
        return

    queue = st.session_state.get(_Q) or []
    pos = int(st.session_state.get(_POS, 0))
    if pos >= len(queue):
        st.success(t("learn.finished"))
        if st.button(t("learn.start"), key=ui.unique_key("learn_restart")):
            st.session_state[_Q] = None
            st.rerun()
        return

    card = queue[pos]
    st.caption(t("learn.progress", i=pos + 1, n=len(queue)))
    st.markdown(
        f"<div dir='rtl' lang='ar' style='font-size:2.6rem;line-height:1.6'>"
        f"{card.get('ar', '')}</div>",
        unsafe_allow_html=True,
    )
    if not st.session_state.get(_REVEAL):
        if st.button(t("learn.show_answer"), key=ui.unique_key("learn_reveal")):
            st.session_state[_REVEAL] = True
            st.rerun()
        return

    st.markdown(f"**{t('learn.answer')}** : {card.get('label') or '—'}")
    sample = vocab.sample_verses(con, card["id"], limit=1)
    if sample:
        verse = search.get_verse(con, sample[0]["sura"], sample[0]["aya"])
        if verse:
            ui.render_verse(sample[0]["sura"], sample[0]["aya"],
                            verse["text_uthmani"], verse["translations"],
                            interactive=True, con=con)

    grades = (
        (t("learn.again"), srs.GRADE_AGAIN),
        (t("learn.hard"), srs.GRADE_HARD),
        (t("learn.good"), srs.GRADE_GOOD),
        (t("learn.easy"), srs.GRADE_EASY),
    )
    cols = st.columns(4)
    for col, (label, value) in zip(cols, grades):
        if col.button(label, key=ui.unique_key(f"learn_g_{value}"),
                      use_container_width=True):
            learning.record_review(card["kind"], card["id"], value,
                                   ar=card.get("ar", ""),
                                   label=card.get("label", ""))
            st.session_state[_POS] = pos + 1
            st.session_state[_REVEAL] = False
            st.rerun()


# --------------------------------------------------------------------------
# Quiz
# --------------------------------------------------------------------------
def _quiz_block(con) -> None:
    st.subheader(t("learn.quiz_title"))
    st.caption(t("learn.quiz_intro"))
    q = st.session_state.get(_QC)
    if q is None:
        if st.button(t("learn.quiz_another"), key=ui.unique_key("quiz_c_new")):
            card = _pick_card(con)
            st.session_state[_QC] = (
                quiz.context_question(con, card, i18n.lang()) if card else None
            )
            st.rerun()
        else:
            return
    elif q is None:
        st.info(t("learn.quiz_none"))
        return

    if q:
        st.markdown(t("learn.quiz_context_prompt",
                      root=q.get("root_ar") or ""))
        tokens = q["tokens"]
        ti = q["target_index"]
        rendered = []
        for i, tok in enumerate(tokens):
            form = tok["form_arabic"]
            if i == ti:
                rendered.append(
                    f"<mark style='background:#ffe08a;padding:0 .1em'>"
                    f"{form}</mark>"
                )
            else:
                rendered.append(form)
        st.markdown(
            f"<div dir='rtl' lang='ar' style='font-size:1.5rem;line-height:2.2'>"
            f"{' '.join(rendered)}</div> "
            f"<span style='opacity:.7'>({q['ref']})</span>",
            unsafe_allow_html=True,
        )
        _ask(con, q, _QC)


def _quiz_root_block(con) -> None:
    st.subheader(t("learn.quiz_root_title"))
    st.caption(t("learn.quiz_root_intro"))
    q = st.session_state.get(_QR)
    if q is None:
        if st.button(t("learn.quiz_another"), key=ui.unique_key("quiz_r_new")):
            st.session_state[_QR] = quiz.root_question(con, i18n.lang())
            st.rerun()
        else:
            return
    elif q is None:
        st.info(t("learn.quiz_none"))
        return

    if q:
        st.markdown(
            t("learn.quiz_root_prompt", form=q["form"],
              tr=q.get("transliteration") or "")
        )
        st.markdown(
            f"<div dir='rtl' lang='ar' style='font-size:2rem'>{q['form']}</div>",
            unsafe_allow_html=True,
        )
        _ask(con, q, _QR)


def _ask(con, q: dict, state_key: str) -> None:
    """Affiche les propositions d'un quiz, corrige et alimente le SRS."""
    labels = [opt["text"] for opt in q["options"]]
    choice = st.radio(t("learn.quiz_submit"), list(range(len(labels))),
                      format_func=lambda i: labels[i],
                      key=ui.unique_key(f"quiz_choice_{state_key}"))
    if st.button(t("learn.quiz_submit"), key=ui.unique_key(f"quiz_submit_{state_key}")):
        correct = bool(q["options"][choice]["correct"])
        if correct:
            st.success(t("learn.quiz_correct"))
        else:
            st.error(t("learn.quiz_wrong", ans=q["answer"]))
        if q.get("kind") == "context" and q.get("root_ar"):
            card = {"kind": "root", "id": "", "ar": q["root_ar"],
                    "label": q["answer"]}
            # On retrouve la racine Buckwalter via la glose (best effort).
            for r in cache.frequent_roots_cached(
                    con, config.LEARN_TOP_ROOTS, lang=i18n.lang()):
                if r.get("gloss") == q["answer"]:
                    card["id"] = r["root_bw"]
                    break
            if card["id"]:
                learning.record_review("root", card["id"],
                                       quiz.grade(correct),
                                       ar=card["ar"], label=card["label"])
        st.session_state[state_key] = None


# --------------------------------------------------------------------------
# Onglet complet
# --------------------------------------------------------------------------
def render_tab(con) -> None:
    """Contenu de l'onglet « Apprendre »."""
    if not getattr(config, "LEARN_ENABLED", False):
        st.info(t("learn.disabled"))
        return
    st.subheader(t("learn.title"))
    st.caption(t("learn.caption"))
    st.markdown(f"**{t('learn.dashboard')}**")
    _dashboard(con)
    st.divider()
    _review_session(con)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        _quiz_block(con)
    with col2:
        _quiz_root_block(con)
