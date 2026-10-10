"""Onglet « Apprendre » · parcours de lecture de l'arabe (méthode Iqraʾ).

Affiche « proprement » le module pédagogique de ``iqra.py`` en quatre
étapes navigables (Alphabet → Voyelles → Signes → Lecture) puis, en toute
fin de parcours, une passerelle vers la lecture du Coran : des sourates
courtes rendues en Uthmani avec récitation audio et transcription
phonétique, via ``ui.render_verse``.

Charte graphique : cartes HTML thémées à partir de la palette courante
(``ui._palette``) — lisibles en Clair, Intermédiaire et Sombre en suivant
automatiquement le sélecteur de thème de la barre latérale.

Conventions du projet : tous les widgets interactifs portent une ``key=``
explicite (stable, une seule occurrence par run) ; tous les textes
d'interface passent par ``i18n.t`` (parité FR/EN).
"""

import html

import streamlit as st

from . import config, i18n, iqra, search, ui

t = i18n.t

STEP_LABELS = ("iqra.step1", "iqra.step2", "iqra.step3", "iqra.step4")


def _css() -> dict:
    """Couleurs de la palette courante (Clair / Intermédiaire / Sombre)."""
    p = ui._palette()
    return {"accent": p["accent"], "fg": p["fg"], "fg2": p["fg2"],
            "bg2": p["bg2"], "border": p["border"]}


def _ar_div(text: str, size: str, c: dict, margin: str = ".2rem 0") -> str:
    """Div arabe RTL (lettres, syllabes, mots) sur la couleur d'accent."""
    return (
        f"<div dir='rtl' lang='ar' style='text-align:center;font-size:{size};"
        f"color:{c['accent']};margin:{margin}'>{text}</div>"
    )


def _lang() -> str:
    """Langue d'interface active ('fr' / 'en')."""
    return i18n.lang()


def _mean(word: dict) -> str:
    """Signification d'un mot de lecture dans la langue d'interface."""
    return word.get(_lang()) or word.get("fr") or word.get("en", "")


# --------------------------------------------------------------------------
# Étape 1 — alphabet et formes positionnelles
# --------------------------------------------------------------------------
def _step_alphabet():
    st.caption(t("iqra.s1_intro"))
    c = _css()
    headers = ("iqra.s1_col_letter", "iqra.s1_col_name", "iqra.s1_col_iso",
               "iqra.s1_col_init", "iqra.s1_col_medi", "iqra.s1_col_fin",
               "iqra.s1_col_tr")
    head = "".join(f"<th>{html.escape(t(h))}</th>" for h in headers)
    rows = []
    for letter in iqra.ALPHABET:
        forms = "".join(
            f"<td lang='ar' dir='rtl' style='text-align:center;"
            f"font-size:1.35rem'>{form}</td>"
            for form in letter["forms"]
        )
        rows.append(
            f"<tr><td lang='ar' dir='rtl' style='text-align:center;"
            f"font-size:1.35rem'>{letter['ar']}</td>"
            f"<td>{html.escape(letter['name'])}</td>{forms}"
            f"<td>{html.escape(letter['tr'])}</td></tr>"
        )
    st.markdown(
        f"<table class='ql'><thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.caption(t("iqra.s1_note_connect"))
    st.caption(t("iqra.s1_note_nonconnect"))
    st.markdown(_ar_div(" ".join(iqra.NON_CONNECTING), "2.1rem", c),
                unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Étape 2 — voyelles courtes et longues (+ exercice d'entraînement)
# --------------------------------------------------------------------------
def _vowel_table(rows: list, columns: list) -> None:
    """Tableau voyelles. ``columns`` = [(champ des données, clé i18n), ...]."""
    head = "".join(f"<th>{html.escape(t(label))}</th>" for _, label in columns)
    body = []
    for row in rows:
        cells = []
        for key, _label in columns:
            val = row.get(key, "")
            attr = (
                "lang='ar' dir='rtl' style='text-align:center;font-size:1.3rem'"
                if key == "ar"
                else ""
            )
            cells.append(f"<td {attr}>{val}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    st.markdown(
        f"<table class='ql'><thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>",
        unsafe_allow_html=True,
    )


def _drill():
    """Mini-exercice : lire une syllabe arabe et choisir sa transcription."""
    pool = iqra.syllable_pairs()
    idx = st.session_state.get("iqra_drill_i", 0) % len(pool)
    item = pool[idx]
    good = item["tr"]
    st.markdown(_ar_div(item["ar"], "3.2rem", _css()), unsafe_allow_html=True)
    wrongs = [p["tr"] for p in pool
              if p["key"].startswith(item["ar"][0] + "-") and p["tr"] != good]
    options = [good] + wrongs[:2]
    rotate = idx % len(options)
    ordered = options[rotate:] + options[:rotate]
    st.radio(
        t("iqra.s2_drill_hint"),
        ordered,
        horizontal=True,
        key="iqra_drill_choice",
    )
    if st.button(t("iqra.s2_check"), key="iqra_drill_check"):
        st.session_state["iqra_drill_fb"] = (
            st.session_state["iqra_drill_choice"] == good
        )
    fb = st.session_state.get("iqra_drill_fb")
    if fb is True:
        st.success(t("iqra.s2_correct"))
    elif fb is False:
        st.error(t("iqra.s2_wrong", tr=good))
    if st.button(t("iqra.s2_next"), key="iqra_drill_next"):
        st.session_state["iqra_drill_i"] = (idx + 1) % len(pool)
        st.session_state.pop("iqra_drill_fb", None)


def _step_vowels():
    st.caption(t("iqra.s2_intro"))
    st.markdown(f"**{t('iqra.s2_table_short')}**")
    _vowel_table(
        [{"ar": v["ar"], "name": v["name"], "tr": v["tr"]}
         for v in iqra.SHORT_VOWELS],
        [("ar", "iqra.s2_col_form"), ("name", "iqra.s2_col_name"),
         ("tr", "iqra.s2_col_sound")],
    )
    st.markdown(f"**{t('iqra.s2_table_long')}**")
    _vowel_table(
        [{"ar": v["ar"], "combo": v["combo"], "tr": v["tr"]}
         for v in iqra.LONG_VOWELS],
        [("ar", "iqra.s2_col_form"), ("combo", "iqra.s2_col_combo"),
         ("tr", "iqra.s2_col_sound")],
    )
    st.divider()
    st.markdown(f"**{t('iqra.s2_exercise')}**")
    _drill()


# --------------------------------------------------------------------------
# Étape 3 — soukoun, chaddah, tanwin
# --------------------------------------------------------------------------
def _mark_card(mark: dict, c: dict) -> str:
    c_start = (
        "<div style='border:1px solid {border};border-left:3px solid {accent};"
        "border-radius:12px;background:{bg2};padding:.6rem 1rem;margin:.4rem 0;"
        "color:{fg}'>"
    ).format(**{k: c[k] for k in ("border", "accent", "bg2", "fg")})
    rows = "".join(
        "<tr>"
        f"<td lang='ar' dir='rtl' style='text-align:center;font-size:1.3rem'>{ar}</td>"
        f"<td>{html.escape(tr)}</td>"
        f"<td>{html.escape(fr)}</td>"
        "</tr>"
        for (ar, tr, fr, _en) in mark["words"]
    )
    return (
        c_start
        + f"<b style='color:{c['accent']}'>{html.escape(mark['name'])}</b>"
        + f" {_ar_div(mark['ar'], '1.9rem', c, margin='.15rem 0')}"
        + f"<span style='color:{c['fg2']}'>{html.escape(t('iqra.s3_role'))} : "
        + f"{html.escape(mark['tr'])}</span>"
        + "<table class='ql' style='margin-top:.5rem'>"
        + f"<thead><tr><th>{html.escape(t('iqra.s3_mot'))}</th>"
        + f"<th>{html.escape(t('iqra.s3_tr'))}</th>"
        + f"<th>{html.escape(t('iqra.s3_mean'))}</th></tr></thead>"
        + f"<tbody>{rows}</tbody></table>"
        + "</div>"
    )


def _step_marks():
    st.caption(t("iqra.s3_intro"))
    c = _css()
    for mark in iqra.MARKS:
        st.markdown(_mark_card(mark, c), unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Étape 4 — lecture progressive puis passerelle vers le Coran
# --------------------------------------------------------------------------
def _word_card(w: dict, c: dict) -> str:
    ref = w.get("ref", "")
    ref_html = (
        f"<div style='text-align:center;color:{c['fg2']};font-size:.8rem'>"
        f"· {html.escape(ref)}</div>"
        if ref
        else ""
    )
    return (
        "".join([
            f"<div style='border:1px solid {c['border']};border-radius:12px;"
            f"padding:.6rem;background:{c['bg2']};color:{c['fg']}'>",
            _ar_div(w["ar"], "1.9rem", c, margin=".1rem 0"),
            f"<div style='text-align:center'>{html.escape(w['tr'])}</div>",
            f"<div style='text-align:center;color:{c['fg2']};font-size:.86rem'>"
            f"{html.escape(_mean(w))}</div>",
            ref_html,
            "</div>",
        ])
    )


def _step_reading(con):
    st.caption(t("iqra.s4_intro"))
    c = _css()
    for tier in iqra.READING_TIERS:
        title = tier.get("title_" + _lang()) or tier.get("title_fr")
        hint = tier.get("hint_" + _lang()) or tier.get("hint_fr")
        st.markdown(f"**{html.escape(title)}**")
        st.caption(html.escape(hint))
        words = tier["words"]
        for start in range(0, len(words), 3):
            cols = st.columns(3)
            for col, w in zip(cols, words[start:start + 3]):
                with col:
                    st.markdown(_word_card(w, c), unsafe_allow_html=True)
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

    # Passerelle vers la lecture du Coran (sourates courtes, Uthmani + audio).
    st.markdown(f"**{t('iqra.s4_practice')}**")
    st.caption(t("iqra.s4_practice_hint"))
    if con is None:
        st.caption(t("iqra.s4_no_con"))
        return
    names = ui.surah_names()
    for sura, translit in iqra.PRACTICE_SURAHS:
        label = t("iqra.s4_surah_fmt", n=sura, name=names.get(sura, ""))
        with st.expander(html.escape(label)):
            bundle = search.verses_bundle(con, [(sura, a) for a in translit])
            for aya in sorted(translit):
                data = bundle.get((sura, aya), {})
                ui.render_verse(
                    sura,
                    aya,
                    data.get("text_uthmani", ""),
                    data.get("translations", []),
                    caption=translit[aya],
                    audio=True,
                    bookmark=True,
                    media=True,
                    con=con,
                )


# --------------------------------------------------------------------------
# Rendu complet
# --------------------------------------------------------------------------
def render_tab(con) -> None:
    """Contenu de la section « Lire l'arabe » de l'onglet Apprendre."""
    if not getattr(config, "LEARN_ENABLED", False):
        return
    st.subheader(t("iqra.title"))
    st.caption(t("iqra.caption"))
    step = st.radio(
        t("iqra.choose_step"),
        list(range(len(STEP_LABELS))),
        format_func=lambda i: t(STEP_LABELS[i]),
        horizontal=True,
        key="iqra_step",
    )
    st.divider()
    if step == 0:
        _step_alphabet()
    elif step == 1:
        _step_vowels()
    elif step == 2:
        _step_marks()
    else:
        _step_reading(con=con)