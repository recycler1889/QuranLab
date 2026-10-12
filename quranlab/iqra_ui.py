"""Onglet « Apprendre » · parcours de lecture de l'arabe (méthode Iqraʾ).

Affiche le module pédagogique de ``iqra.py`` en sept étapes navigables
(Alphabet → Voyelles → Signes → Lecture → Vocabulaire → Nombres → 99 Noms) puis,
en toute fin de parcours de lecture, une passerelle vers le Coran : des sourates
courtes rendues en Uthmani avec récitation audio et transcription phonétique
via ``ui.render_verse``.

L'étape Alphabet propose un mode **mélangé** (bouton bascule) pour réviser les
lettres dans un ordre aléatoire — conservé dans l'état de session pour rester
stable entre les ré-exécutions — et un bouton de retour à l'ordre traditionnel.

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
def _delay(i: int) -> str:
    """Décalage d'animation (ms) pour une entrée en cascade, plafonné.

    Le plafond évite qu'une longue liste (99 Noms, 28 lettres) impose une
    attente perceptible en fin de grille.
    """
    return f" style='--ql-delay:{min(i, 11) * 28}ms'"


def _letter_card(letter: dict, c: dict, i: int = 0) -> str:
    """Carte d'une lettre : forme isolée, nom, transcription, quatre formes."""
    tiles = "".join(
        f"<span dir='rtl' lang='ar'>{form}</span>" for form in letter["forms"]
    )
    return (
        f"<div class='ql-card'{_delay(i)}>"
        "<span class='ql-orn'></span>"
        f"<div class='ql-ar' dir='rtl' lang='ar'>{html.escape(letter['ar'])}</div>"
        f"<div class='ql-name'>{html.escape(letter['name'])}</div>"
        f"<div class='ql-tr'>{html.escape(letter['tr'])}</div>"
        f"<div class='ql-forms'>{tiles}</div>"
        "</div>"
    )


def _reset_alpha_shuffle() -> None:
    """Revient à l'ordre traditionnel (callback : exécuté avant le rerun)."""
    st.session_state["iqra_alpha_shuffle"] = False
    st.session_state.pop("iqra_alpha_order", None)


def _alphabet_order(n: int) -> list:
    """Ordre d'affichage de l'alphabet : traditionnel ou mélangé (persistant).

    En mode mélangé, l'ordre tiré est **conservé dans l'état de session** afin
    de rester stable entre les ré-exécutions (écoute TTS, changement de forme) ;
    il n'est régénéré que s'il est absent ou invalide.
    """
    if not st.session_state.get("iqra_alpha_shuffle"):
        st.session_state.pop("iqra_alpha_order", None)
        return list(range(n))
    order = st.session_state.get("iqra_alpha_order")
    if not order or len(order) != n or sorted(order) != list(range(n)):
        order = iqra.shuffled_order(n)
        st.session_state["iqra_alpha_order"] = order
    return order


def _step_alphabet():
    st.subheader(t("iqra.s1_title"))
    st.caption(t("iqra.s1_desc"))
    st.caption(t("iqra.s1_legend"))

    n = len(iqra.ALPHABET)
    _c1, _c2 = st.columns([3, 1])
    with _c1:
        shuffled = st.toggle(t("iqra.s1_shuffle"), key="iqra_alpha_shuffle")
    with _c2:
        st.button(t("iqra.s1_reset"), key="iqra_alpha_reset",
                  on_click=_reset_alpha_shuffle, disabled=not shuffled)
    order = _alphabet_order(n)

    c = _css()
    for i, idx in enumerate(order):
        letter = iqra.ALPHABET[idx]
        if i % 4 == 0:
            cols = st.columns(4)
        with cols[i % 4]:
            st.markdown(_letter_card(letter, c, i), unsafe_allow_html=True)
            _listen(letter.get("ar_name") or letter["ar"])
    st.caption(t("iqra.s1_note_nonconnect"))
    st.markdown(_ar_div(" ".join(iqra.NON_CONNECTING), "2.1rem", c),
                unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Étape 2 — voyelles courtes et longues (+ exercice d'entraînement)
# --------------------------------------------------------------------------
def _vowel_card(v: dict, c: dict, i: int = 0) -> str:
    """Carte d'une voyelle : combinaison arabe, nom, construction, son."""
    combo = html.escape(v.get("combo", ""))
    combo_html = f"<div class='ql-tr'>{combo}</div>" if combo else ""
    return (
        f"<div class='ql-card'{_delay(i)}>"
        "<span class='ql-orn'></span>"
        f"<div class='ql-ar' dir='rtl' lang='ar'>{html.escape(v['ar'])}</div>"
        f"<div class='ql-name'>{html.escape(v['name'])}</div>"
        + combo_html
        + f"<div class='ql-gloss'>{html.escape(v['tr'])}</div>"
        + "</div>"
    )


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
    for i, (col, v) in enumerate(zip(cols, iqra.SHORT_VOWELS)):
        with col:
            st.markdown(_vowel_card(v, c, i), unsafe_allow_html=True)
            _listen(v["ar"])
    st.markdown(f"**{t('iqra.s2_table_long')}**")
    cols = st.columns(3)
    for i, (col, v) in enumerate(zip(cols, iqra.LONG_VOWELS)):
        with col:
            st.markdown(_vowel_card(v, c, i), unsafe_allow_html=True)
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
        "<div class='ql-card ql-mark'>"
        "<span class='ql-orn'></span>"
        "<div class='ql-head'>"
        f"<span><b class='ql-accent'>{html.escape(mark['name'])}</b> "
        f"<span dir='rtl' lang='ar' style='font-size:1.2rem'>"
        f"{html.escape(mark['sign'])}</span></span>"
        f"<span class='ql-tr'>{html.escape(t('iqra.s3_role'))} : "
        f"{html.escape(mark['tr'])}</span>"
        "</div></div>"
    )


def _word_card(w: dict, c: dict, i: int = 0) -> str:
    """Carte d'un mot d'exercice (arabe, transcription, sens, référence)."""
    ref_html = (
        f"<div class='ql-meta'>· {html.escape(w.get('ref', ''))}</div>"
        if w.get("ref")
        else ""
    )
    return (
        "".join([
            f"<div class='ql-card'{_delay(i)}>",
            "<span class='ql-orn'></span>",
            f"<div class='ql-ar' dir='rtl' lang='ar'>{html.escape(w['ar'])}</div>",
            f"<div class='ql-tr'>{html.escape(w['tr'])}</div>",
            f"<div class='ql-gloss'>{html.escape(_mean(w))}</div>",
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
        for i, (col, (ar, tr, fr, en)) in enumerate(zip(cols, mark["words"])):
            with col:
                st.markdown(
                    _word_card({"ar": ar, "tr": tr, "fr": fr, "en": en}, c, i),
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
            for i, (col, w) in enumerate(zip(cols, words[start:start + 3])):
                with col:
                    st.markdown(_word_card(w, c, i), unsafe_allow_html=True)
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
def _vocab_card(w: dict, c: dict, i: int = 0) -> str:
    """Carte d'un terme de vocabulaire : rang, racine, mot, translittération,
    sens localisé et trace dans le corpus (occurrences · versets · verset)."""
    root = html.escape(w.get("root_ar") or "")
    gloss = html.escape(w["gloss"] or "") or "—"
    meta = html.escape(t("iqra.vocab_meta", occ=w["occ"], verses=w["verses"],
                         ref=w.get("ref", "")))
    return (
        f"<div class='ql-card'{_delay(i)}>"
        "<span class='ql-orn'></span>"
        "<div class='ql-head'>"
        f"<span>{w['rank']} · {html.escape(t('iqra.vocab_root'))}</span>"
        f"<span class='ql-accent' dir='rtl' lang='ar' "
        f"style='font-size:.95rem'>{root}</span></div>"
        f"<div class='ql-ar' dir='rtl' lang='ar' style='font-size:1.5rem;"
        f"margin:.2rem 0'>{html.escape(w['ar'])}</div>"
        f"<div class='ql-tr'>{html.escape(w['tr'])}</div>"
        f"<div class='ql-gloss'>{gloss}</div>"
        f"<div class='ql-meta' style='margin-top:.15rem'>{meta}</div>"
        "</div>"
    )


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
        for j, (col, w) in enumerate(zip(cols, words[i:i + 3])):
            with col:
                st.markdown(_vocab_card(w, c, j), unsafe_allow_html=True)
                _listen(w["ar"] or w["root_ar"] or "")


# --------------------------------------------------------------------------
# Étape 6 — les nombres en arabe, de 1 à 1000 (+ écoute par nombre)
# --------------------------------------------------------------------------
def _num_card(item: dict, c: dict, i: int = 0) -> str:
    """Carte d'un nombre : chiffre arabo-indien, mot voyellé, transcription."""
    digit = iqra.arabic_digits(item["n"])
    return (
        f"<div class='ql-card'{_delay(i)}>"
        "<span class='ql-orn'></span>"
        f"<div class='ql-ar ql-ar-num' dir='rtl' lang='ar'>{digit}</div>"
        f"<div dir='rtl' lang='ar' style='font-size:1rem'>"
        f"{html.escape(item['ar'])}</div>"
        f"<div class='ql-tr'>{html.escape(item['tr'])}</div>"
        "</div>"
    )


def _num_grid(items: list, per_row: int, c: dict) -> None:
    """Grille de cartes-nombres, chacune avec son bouton « Écouter »."""
    for i in range(0, len(items), per_row):
        cols = st.columns(per_row)
        for j, (col, item) in enumerate(zip(cols, items[i:i + per_row])):
            with col:
                st.markdown(_num_card(item, c, j), unsafe_allow_html=True)
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
def _asma_card(name: dict, c: dict, i: int = 0) -> str:
    """Carte d'un Nom : calligraphie, translittération, traduction directe,
    racine et définition lexicographique ; repère graphique à teinte douce."""
    hue = name["hue"]
    badge_bg = f"hsla({hue},60%,50%,.16)"
    badge_br = f"hsla({hue},60%,45%,.55)"
    return (
        f"<div class='ql-card'{_delay(i)}>"
        "<span class='ql-orn'></span>"
        "<div class='ql-head'>"
        f"<span>{name['n']} / {asma.count()}</span>"
        "<span class='ql-badge' "
        f"style='background:{badge_bg};border:1px solid {badge_br}'>"
        f"{name['icon']}</span></div>"
        f"<div class='ql-ar ql-ar-xl' dir='rtl' lang='ar' "
        f"style='margin:.25rem 0 .1rem'>{html.escape(name['ar'])}</div>"
        f"<div class='ql-tr' style='font-size:.86rem'>"
        f"{html.escape(name['tr'])}</div>"
        f"<div class='ql-name' style='font-size:.92rem;margin:.15rem 0'>"
        f"{html.escape(asma.translation(name, _lang()))}</div>"
        f"<div class='ql-meta'>{html.escape(t('iqra.asma_root'))} : "
        f"<span dir='rtl' lang='ar'>{html.escape(name['root_ar'])}</span> · "
        f"{html.escape(name['root_tr'])}</div>"
        f"<div class='ql-sep'>{html.escape(asma.etymology(name, _lang()))}</div>"
        "</div>"
    )


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
        for j, (col, name) in enumerate(zip(cols, names[i:i + 3])):
            with col:
                st.markdown(_asma_card(name, c, j), unsafe_allow_html=True)
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