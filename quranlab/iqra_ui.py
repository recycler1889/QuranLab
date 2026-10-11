"""Onglet « Apprendre » · parcours de lecture de l'arabe (méthode Iqraʾ).

Affiche le module pédagogique de ``iqra.py`` en six étapes navigables
(Alphabet → Voyelles → Signes → Lecture → Vocabulaire → Nombres) puis, en
toute fin de parcours de lecture, une passerelle vers le Coran : des sourates
courtes rendues en Uthmani avec récitation audio et transcription phonétique
via ``ui.render_verse``.

Synthèse vocale : un bouton « Écouter » (``ui.tts_arabic``) accompagne chaque
lettre, voyelle, signe, mot-exemple, terme de vocabulaire et nombre — la
prononciation arabe est lue par la Web Speech API du navigateur.

Charte graphique : cartes HTML thémées à partir de la palette courante
(``ui._palette``) — lisibles en Clair, Intermédiaire et Sombre en suivant
automatiquement le sélecteur de thème de la barre latérale.

Conventions du projet : tous les widgets interactifs portent une ``key=``
explicite (stable, une seule occurrence par run) ; tous les textes
d'interface passent par ``i18n.t`` (parité FR/EN).
"""

import html

import streamlit as st

from . import asma, cache, config, i18n, iqra, search, ui, vocab

t = i18n.t

STEP_LABELS = ("iqra.step1", "iqra.step2", "iqra.step3", "iqra.step4",
               "iqra.step5", "iqra.step6", "iqra.step7")


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


def _listen(text: str) -> None:
    """Bouton « Écouter » : prononciation arabe du texte (Web Speech API)."""
    if (text or "").strip():
        ui.tts_arabic(text)


# --------------------------------------------------------------------------
# Étape 1 — alphabet et formes positionnelles (cartes + écoute par lettre)
# --------------------------------------------------------------------------
def _letter_card(letter: dict, c: dict) -> str:
    """Carte d'une lettre : forme isolée, nom, transcription, quatre formes."""
    tiles = "".join(
        f"<span dir='rtl' lang='ar' style='flex:1;padding:.12rem 0;"
        f"font-size:1.05rem;border-radius:6px;background:{c['bg2']};"
        f"color:{c['fg']}'>{form}</span>"
        for form in letter["forms"]
    )
    return (
        "<div style='border:1px solid {border};border-radius:12px;"
        "padding:.5rem .4rem;background:{bg2};color:{fg};text-align:center'>"
        f"<div dir='rtl' lang='ar' style='font-size:2rem;"
        f"color:{c['accent']}'>{letter['ar']}</div>"
        f"<div style='font-weight:600;font-size:.9rem'>{html.escape(letter['name'])}</div>"
        f"<div style='color:{c['fg2']};font-size:.78rem'>{html.escape(letter['tr'])}</div>"
        "<div style='display:flex;gap:3px;margin-top:.35rem'>" + tiles + "</div>"
        "</div>"
    ).format(**{k: c[k] for k in ("border", "bg2", "fg")})


def _step_alphabet():
    st.subheader(t("iqra.s1_title"))
    st.caption(t("iqra.s1_desc"))
    st.caption(t("iqra.s1_legend"))
    c = _css()
    for i, letter in enumerate(iqra.ALPHABET):
        if i % 4 == 0:
            cols = st.columns(4)
        with cols[i % 4]:
            st.markdown(_letter_card(letter, c), unsafe_allow_html=True)
            _listen(letter.get("ar_name") or letter["ar"])
    st.caption(t("iqra.s1_note_nonconnect"))
    st.markdown(_ar_div(" ".join(iqra.NON_CONNECTING), "2.1rem", c),
                unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Étape 2 — voyelles courtes et longues (+ exercice d'entraînement)
# --------------------------------------------------------------------------
def _vowel_card(v: dict, c: dict) -> str:
    """Carte d'une voyelle : combinaison arabe, nom, construction, son."""
    combo = html.escape(v.get("combo", ""))
    combo_html = (
        f"<div style='color:{c['fg2']};font-size:.78rem'>{combo}</div>"
        if combo else ""
    )
    return (
        "<div style='border:1px solid {border};border-radius:12px;"
        "padding:.55rem .3rem;background:{bg2};color:{fg};text-align:center'>"
        f"<div dir='rtl' lang='ar' style='font-size:2rem;"
        f"color:{c['accent']}'>{html.escape(v['ar'])}</div>"
        f"<div style='font-weight:600;font-size:.95rem'>{html.escape(v['name'])}</div>"
        + combo_html
        + f"<div style='color:{c['fg']};font-size:.85rem'>{html.escape(v['tr'])}</div>"
        + "</div>"
    ).format(**{k: c[k] for k in ("border", "bg2", "fg")})


def _drill():
    """Mini-exercice : lire une syllabe arabe et choisir sa transcription."""
    pool = iqra.syllable_pairs()
    idx = st.session_state.get("iqra_drill_i", 0) % len(pool)
    item = pool[idx]
    good = item["tr"]
    _listen(item["ar"])
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
    st.subheader(t("iqra.s2_title"))
    st.caption(t("iqra.s2_desc"))
    c = _css()
    st.markdown(f"**{t('iqra.s2_table_short')}**")
    cols = st.columns(3)
    for col, v in zip(cols, iqra.SHORT_VOWELS):
        with col:
            st.markdown(_vowel_card(v, c), unsafe_allow_html=True)
            _listen(v["ar"])
    st.markdown(f"**{t('iqra.s2_table_long')}**")
    cols = st.columns(3)
    for col, v in zip(cols, iqra.LONG_VOWELS):
        with col:
            st.markdown(_vowel_card(v, c), unsafe_allow_html=True)
            _listen(v["ar"])
    st.divider()
    st.markdown(f"**{t('iqra.s2_exercise')}**")
    _drill()


# --------------------------------------------------------------------------
# Étape 3 — soukoun, chaddah, tanwin (+ écoute des mots-exemples)
# --------------------------------------------------------------------------
def _mark_header(mark: dict, c: dict) -> str:
    """En-tête d'un signe : nom, glyphe du signe et rôle."""
    return (
        "<div style='border:1px solid {border};border-left:3px solid {accent};"
        "border-radius:12px;background:{bg2};padding:.6rem 1rem;margin:.4rem 0;"
        "color:{fg}'>"
        f"<b style='color:{c['accent']}'>{html.escape(mark['name'])}</b>"
        f" <span dir='rtl' lang='ar' style='font-size:1.2rem'>"
        f"{html.escape(mark['sign'])}</span>"
        f"<span style='color:{c['fg2']}'>{html.escape(t('iqra.s3_role'))} : "
        f"{html.escape(mark['tr'])}</span>"
        "</div>"
    ).format(**{k: c[k] for k in ("border", "accent", "bg2", "fg")})


def _word_card(w: dict, c: dict) -> str:
    """Carte d'un mot d'exercice (arabe, transcription, sens, référence)."""
    ref_html = (
        f"<div style='text-align:center;color:{c['fg2']};font-size:.8rem'>"
        f"· {html.escape(w.get('ref', ''))}</div>"
        if w.get("ref")
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


def _step_marks():
    st.subheader(t("iqra.s3_title"))
    st.caption(t("iqra.s3_desc"))
    c = _css()
    for mark in iqra.MARKS:
        st.markdown(_mark_header(mark, c), unsafe_allow_html=True)
        cols = st.columns(len(mark["words"]))
        for col, (ar, tr, fr, en) in zip(cols, mark["words"]):
            with col:
                st.markdown(
                    _word_card({"ar": ar, "tr": tr, "fr": fr, "en": en}, c),
                    unsafe_allow_html=True,
                )
                _listen(ar)


# --------------------------------------------------------------------------
# Étape 4 — lecture progressive puis passerelle vers le Coran (+ écoute)
# --------------------------------------------------------------------------
def _step_reading(con):
    st.subheader(t("iqra.s4_title"))
    st.caption(t("iqra.s4_desc"))
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
                    _listen(w["ar"])
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
# Étape 5 — vocabulaire essentiel du Coran (cartes + écoute + filtre)
# --------------------------------------------------------------------------
def _vocab_card(w: dict, c: dict) -> str:
    """Carte d'un terme de vocabulaire : rang, racine, mot, translittération,
    sens localisé et trace dans le corpus (occurrences · versets · verset)."""
    root = html.escape(w.get("root_ar") or "")
    gloss = html.escape(w["gloss"] or "") or "—"
    meta = html.escape(t("iqra.vocab_meta", occ=w["occ"], verses=w["verses"],
                         ref=w.get("ref", "")))
    return (
        "<div style='border:1px solid {border};border-radius:12px;"
        "padding:.55rem .4rem;background:{bg2};color:{fg}'>"
        f"<div style='display:flex;justify-content:space-between;"
        f"align-items:center'>"
        f"<span style='color:{c['fg2']};font-size:.72rem'>{w['rank']} · "
        f"{html.escape(t('iqra.vocab_root'))}</span>"
        f"<span dir='rtl' lang='ar' style='color:{c['accent']};font-size:.95rem'>{root}</span></div>"
        f"<div dir='rtl' lang='ar' style='text-align:center;font-size:1.5rem;"
        f"color:{c['accent']};margin:.2rem 0'>{html.escape(w['ar'])}</div>"
        f"<div style='text-align:center;font-size:.82rem'>{html.escape(w['tr'])}</div>"
        f"<div style='text-align:center;color:{c['fg']};font-size:.85rem;"
        f"min-height:1.1rem'>{gloss}</div>"
        f"<div style='text-align:center;color:{c['fg2']};font-size:.72rem;"
        f"margin-top:.15rem'>{meta}</div>"
        "</div>"
    ).format(**{k: c[k] for k in ("border", "bg2", "fg")})


def _step_vocab(con):
    st.subheader(t("iqra.vocab_title"))
    st.caption(t("iqra.vocab_desc"))
    if con is None:
        st.caption(t("iqra.vocab_no_con"))
        return
    words = cache.frequent_words_cached(con, config.IQRA_VOCAB_TOP,
                                        lang=_lang())
    if words:
        st.caption(t("iqra.vocab_cov", n=len(words),
                     pct=words[-1]["coverage_pct"],
                     total=vocab.corpus_token_count(con)))
    q = st.text_input(t("iqra.vocab_search"), key="iqra_vocab_q")
    shown = st.slider(t("iqra.vocab_limit"), 5, 50, 24, 1, key="iqra_vocab_n")
    ql = (q or "").strip().lower()
    if ql:
        words = [w for w in words
                 if ql in (w["ar"] or "").lower()
                 or ql in (w["root_ar"] or "").lower()
                 or ql in (w["tr"] or "").lower()
                 or ql in (w["gloss"] or "").lower()]
    if not words:
        st.caption(t("iqra.vocab_none"))
        return
    c = _css()
    for i in range(0, min(len(words), shown), 3):
        cols = st.columns(3)
        for col, w in zip(cols, words[i:i + 3]):
            with col:
                st.markdown(_vocab_card(w, c), unsafe_allow_html=True)
                _listen(w["ar"] or w["root_ar"] or "")


# --------------------------------------------------------------------------
# Étape 6 — les nombres en arabe, de 1 à 1000 (+ écoute par nombre)
# --------------------------------------------------------------------------
def _num_card(item: dict, c: dict) -> str:
    """Carte d'un nombre : chiffre arabo-indien, mot voyellé, transcription."""
    digit = iqra.arabic_digits(item["n"])
    return (
        "<div style='border:1px solid {border};border-radius:12px;"
        "padding:.5rem .3rem;background:{bg2};color:{fg};text-align:center'>"
        f"<div dir='rtl' lang='ar' style='font-size:1.75rem;"
        f"color:{c['accent']}'>{digit}</div>"
        f"<div dir='rtl' lang='ar' style='font-size:1rem;"
        f"color:{c['fg']}'>{html.escape(item['ar'])}</div>"
        f"<div style='color:{c['fg2']};font-size:.78rem'>"
        f"{html.escape(item['tr'])}</div>"
        "</div>"
    ).format(**{k: c[k] for k in ("border", "bg2", "fg")})


def _num_grid(items: list, per_row: int, c: dict) -> None:
    """Grille de cartes-nombres, chacune avec son bouton « Écouter »."""
    for i in range(0, len(items), per_row):
        cols = st.columns(per_row)
        for col, item in zip(cols, items[i:i + per_row]):
            with col:
                st.markdown(_num_card(item, c), unsafe_allow_html=True)
                _listen(item["ar"])


def _step_numbers():
    st.subheader(t("iqra.num_title"))
    st.caption(t("iqra.num_desc"))
    c = _css()
    st.markdown(f"**{t('iqra.num_units_title')}**")
    _num_grid(iqra.NUM_UNITS, 5, c)
    st.markdown(f"**{t('iqra.num_tens_title')}**")
    st.caption(t("iqra.num_tens_hint"))
    _num_grid(iqra.NUM_TENS, 4, c)
    st.markdown(f"**{t('iqra.num_hundreds_title')}**")
    st.caption(t("iqra.num_hundreds_hint"))
    _num_grid(iqra.NUM_HUNDREDS, 5, c)


# --------------------------------------------------------------------------
# Étape 7 — les 99 Noms d'Allah (cartes étymologiques + écoute par Nom)
# --------------------------------------------------------------------------
def _asma_card(name: dict, c: dict) -> str:
    """Carte d'un Nom : calligraphie, translittération, traduction directe,
    racine et définition lexicographique ; repère graphique à teinte douce."""
    hue = name["hue"]
    badge_bg = f"hsla({hue},60%,50%,.16)"
    badge_br = f"hsla({hue},60%,45%,.55)"
    return (
        "<div style='border:1px solid {border};border-radius:14px;"
        "padding:.6rem .55rem;background:{bg2};color:{fg};height:100%'>"
        "<div style='display:flex;align-items:center;"
        "justify-content:space-between'>"
        f"<span style='font-size:.72rem;color:{c['fg2']}'>{name['n']} / "
        f"{asma.count()}</span>"
        "<span style='display:inline-flex;align-items:center;"
        "justify-content:center;width:1.9rem;height:1.9rem;"
        f"border-radius:50%;background:{badge_bg};border:1px solid {badge_br};"
        f"font-size:1rem'>{name['icon']}</span></div>"
        f"<div dir='rtl' lang='ar' style='text-align:center;font-size:1.7rem;"
        f"color:{c['accent']};margin:.25rem 0 .1rem'>"
        f"{html.escape(name['ar'])}</div>"
        f"<div style='text-align:center;font-size:.86rem'>"
        f"{html.escape(name['tr'])}</div>"
        f"<div style='text-align:center;font-weight:600;font-size:.92rem;"
        f"margin:.15rem 0'>{html.escape(asma.translation(name, _lang()))}</div>"
        f"<div style='text-align:center;font-size:.74rem;color:{c['fg2']}'>"
        f"{html.escape(t('iqra.asma_root'))} : "
        f"<span dir='rtl' lang='ar'>{html.escape(name['root_ar'])}</span> · "
        f"{html.escape(name['root_tr'])}</div>"
        f"<div style='font-size:.78rem;color:{c['fg']};margin-top:.35rem;"
        f"border-top:1px solid {c['border']};padding-top:.35rem'>"
        f"{html.escape(asma.etymology(name, _lang()))}</div>"
        "</div>"
    ).format(**{k: c[k] for k in ("border", "bg2", "fg")})


def _step_asma():
    st.subheader(t("iqra.asma_title"))
    st.caption(t("iqra.asma_desc"))
    st.caption(t("iqra.asma_legend"))
    q = st.text_input(t("iqra.asma_search"), key="iqra_asma_q")
    names = asma.search(q or "", _lang())
    if not names:
        st.caption(t("iqra.asma_none"))
        return
    c = _css()
    for i in range(0, len(names), 3):
        cols = st.columns(3)
        for col, name in zip(cols, names[i:i + 3]):
            with col:
                st.markdown(_asma_card(name, c), unsafe_allow_html=True)
                _listen(name["ar"])


# --------------------------------------------------------------------------
# Rendu complet
# --------------------------------------------------------------------------
def render_tab(con) -> None:
    """Contenu de la section « Apprendre l'arabe » de l'onglet Apprendre."""
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
    elif step == 3:
        _step_reading(con=con)
    elif step == 4:
        _step_vocab(con)
    elif step == 5:
        _step_numbers()
    else:
        _step_asma()