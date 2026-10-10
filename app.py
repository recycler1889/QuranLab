"""Interface Streamlit locale pour quranlab.

Lancement :
    streamlit run app.py
"""

import sqlite3

import streamlit as st

from quranlab import bookmarks, config, db, i18n, onboarding, search, ui
from quranlab import theme as theme_mod
from quranlab.buckwalter import buckwalter_to_arabic

# Rendu partagé (versets, tableaux, recherche universelle) : voir quranlab/ui.py.
html_table = ui.html_table
render_verse = ui.render_verse
render_root_results = ui.render_root_results
t = i18n.t
lang = i18n.lang

st.set_page_config(page_title=t("app.title"), layout="wide")

# Réinitialise les compteurs d'occurrence des clés de widgets (unicité par run).
ui.begin_run()

# --- Langue d'interface (FR ou EN — jamais de mélange) ----------------------
with st.sidebar:
    i18n.sidebar_language_selector()

    st.header(t("app.prefs"))
    theme_name = st.radio(
        t("app.theme"),
        theme_mod.ORDER,
        index=theme_mod.ORDER.index(theme_mod.DEFAULT),
        format_func=lambda k: theme_mod.PALETTES[k]["label"],
        key="theme_choice",
    )

    st.subheader(t("app.audio"))
    _reciters = list(getattr(config, "RECITERS", []) or [])
    _reciter_keys = [r.get("key") for r in _reciters if r.get("key")]
    st.selectbox(
        t("app.reciter"),
        _reciter_keys,
        format_func=lambda k: next(
            (r.get("label", k) for r in _reciters if r.get("key") == k), k
        ),
        key="reciter",
        help=t("app.reciter_help"),
    )
    st.checkbox(t("app.show_audio"), value=True, key="show_quran_audio")
    st.checkbox(
        t("app.show_tts"), value=True, key="show_tts",
        help=t("app.tts_help"),
    )
    if st.session_state.get("show_tts", True):
        ui.tts_settings()

    st.divider()
    st.caption(t("app.caption_scope"))
    st.divider()
    onboarding.sidebar_guide_button()

    with st.expander(t("app.suggest_title")):
        st.markdown(t("app.suggest_body"))
        if config.SUGGESTIONS_URL:
            st.markdown(
                f"[{t('app.write_us', email=config.SUGGESTIONS_EMAIL)}]"
                f"({config.SUGGESTIONS_URL})"
            )
        else:
            st.caption(t("app.suggest_see_guide"))

    # Section de don : préparée mais masquée tant que DONATIONS_ENABLED est False.
    ui.donation_section()

st.markdown(theme_mod.css(theme_name), unsafe_allow_html=True)

ui.page_header("quranlab", t("app.subtitle"))

# Tutoriel de première visite (modale) + rappel accessible en permanence.
onboarding.init()
onboarding.render()
onboarding.inline_guide()


@st.cache_resource(show_spinner=False)
def get_con():
    # Construit la base au premier lancement si elle est absente (déploiement
    # cloud où data/ n'est pas versionné), puis renvoie une connexion unique.
    # db.connect() utilise check_same_thread=False : Streamlit crée ce cache
    # dans un thread et le réutilise dans d'autres threads.
    from quranlab.build import ensure_db

    with st.spinner(t("ui.spinner")):
        ensure_db(verbose=False)
    return db.connect()


try:
    con = get_con()
except Exception as exc:  # noqa: BLE001
    st.error(f"{t('app.con')}: {exc}")
    st.stop()


# --------------------------------------------------------------------------
# Compteurs mis en cache (sidebar + onglets)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def corpus_stats() -> dict:
    """Chiffres du corpus : sourates, versets, mots, racines, traductions."""
    c = get_con()
    row = c.execute(
        "SELECT (SELECT COUNT(*) FROM surahs) AS surahs,"
        "       (SELECT COUNT(*) FROM verses) AS verses,"
        "       (SELECT COUNT(*) FROM words) AS words,"
        "       (SELECT COUNT(DISTINCT root_norm) FROM words"
        "         WHERE root_norm IS NOT NULL) AS roots,"
        "       (SELECT COUNT(*) FROM translations) AS translations"
    ).fetchone()
    return dict(row)


@st.cache_data(show_spinner="Comptage des occurrences des 164 thèmes…")
def theme_counts_cached(fingerprint: int) -> dict:
    """{clé de thème: nb de versets} — recalculé seulement si themes.json change."""
    return search.theme_counts(db.connect())


@st.cache_data(show_spinner=False, hash_funcs={sqlite3.Connection: lambda c: id(c)})
def read_verses_cached(con, sura: int, lo: int, hi: int) -> list:
    """Versets du lecteur (onglet « Lire ») — mis en cache entre les rendus.

    Bouger le curseur de plage provoque un nouveau rendu du script sans que la
    requête SQL ne soit rejouée pour une plage déjà affichée. La connexion
    unique (``get_con``, ``check_same_thread=False``) est hachée par son identité.
    """
    return search.surah_verses(con, sura, lo, hi)


with st.sidebar:
    st.header(t("app.corpus"))
    stats = corpus_stats()
    n_themes = sum(len(v) for v in search.themes_by_category().values())
    n_topics = len(search.controversy_topics())

    def _fmt(n: int) -> str:
        return f"{n:,}".replace(",", " ")

    st.markdown(
        f"- **{_fmt(stats['surahs'])}** {t('app.word_surahs')} · "
        f"**{_fmt(stats['verses'])}** {t('app.word_verses')}\n"
        f"- **{_fmt(stats['words'])}** {t('app.word_words')} · "
        f"**{_fmt(stats['roots'])}** {t('app.word_roots')}\n"
        f"- **{stats['translations']}** {t('app.word_translations')}\n"
        f"- **{n_themes}** {t('app.word_themes')} · "
        f"**{n_topics}** {t('app.word_topics')}"
    )


tab_read, tab_root, tab_search, tab_verse, tab_theme, tab_controv, tab_concord, tab_cross, tab_bm = st.tabs(
    [
        t("app.tab.read"),
        t("app.tab.root"),
        t("app.tab.search"),
        t("app.tab.verse"),
        t("app.tab.theme"),
        t("app.tab.controv"),
        t("app.tab.concord"),
        t("app.tab.cross"),
        t("app.tab.bookmarks"),
    ]
)


def _lang_label(code: str) -> str:
    return t("ui.lang.fr") if code == "fr" else t("ui.lang.ar")


# ---------------------------------------------------------------- Lire le Coran
with tab_read:
    st.subheader(t("app.read_title"))
    st.caption(t("app.read_caption"))

    _surahs = search.surah_list(con)
    _by_num = {s["number"]: s for s in _surahs}
    _labels = {
        s["number"]: t(
            "app.read_surah_fmt",
            n=s["number"],
            name=s["name_translit"],
            count=s["verses_count"],
        )
        for s in _surahs
    }
    _sura = st.selectbox(
        t("app.read_surah"),
        [s["number"] for s in _surahs],
        format_func=lambda n: _labels[n],
        key="read_sura",
    )
    _last = _by_num[_sura]["verses_count"]
    _lo, _hi = st.slider(
        t("app.read_range"),
        1,
        _last,
        (1, min(_last, 20)),
        key=f"read_range_{_sura}",
    )
    st.caption(t("app.read_showing", a=_lo, b=_hi, n=_last))

    _verses = read_verses_cached(con, _sura, _lo, _hi)

    _force_media = st.checkbox(
        t("app.read_media"),
        value=False,
        key="read_media",
        help=t("app.read_media_help"),
    )

    st.markdown(f"**{t('app.read_continuous')}**")
    st.caption(t("app.read_continuous_help"))
    ui.continuous_player(_verses)

    _per_media = (_hi - _lo + 1) <= 50 or _force_media
    for _v in _verses:
        render_verse(
            _v["sura"], _v["aya"], _v["text_uthmani"], _v["translations"],
            bookmark=True, media=_per_media,
        )


# --------------------------------------------------- Rendu partagé : racine
with tab_root:
    st.subheader(t("app.root_title"))
    ui.universal_search(
        con, "root",
        placeholder=t("app.root_placeholder"),
    )
    st.caption(t("app.root_caption"))
    col1, col2 = st.columns([3, 1])
    root_in = col1.text_input(t("app.root_label"), key="root_in")
    ctx = col2.number_input(t("app.root_ctx"), 0, 10, 1)
    if root_in:
        res = search.search_root(con, root_in, with_context=int(ctx))
        render_root_results(con, res)

# ---------------------------------------------------------------- Recherche
with tab_search:
    st.subheader(t("app.search_title"))
    ui.universal_search(
        con, "search",
        placeholder=t("app.search_placeholder"),
    )
    lang_choice = st.radio(
        t("app.input_lang"),
        ["fr", "ar"],
        horizontal=True,
        key="search_lang",
        format_func=_lang_label,
    )
    q = st.text_input(t("app.search_term"), key="q")

    if q and lang_choice == "fr":
        # --- 1. Passerelle linguistique français -> arabe -----------------
        st.markdown(f"#### {t('app.bridge_heading')}")
        props = search.french_bridge(con, q)["proposals"]
        if not props:
            st.info(t("app.bridge_none"))
        else:
            html_table(
                [
                    {
                        t("ui.table_fr"): p["fr"],
                        t("ui.table_root"): p["root_ar"],
                        t("ui.table_bw"): p["root_bw"],
                        t("ui.table_verses"): p["verses"],
                        t("ui.table_occ"): p["occurrences"],
                        t("ui.table_source"): p["source"],
                    }
                    for p in props
                ]
            )
            pick = st.selectbox(
                t("app.bridge_query_root"),
                list(range(len(props))),
                format_func=lambda i: (
                    f"{props[i]['root_ar']} [{props[i]['root_bw']}] — "
                    f"{props[i]['fr']} · {props[i]['verses']} versets"
                ),
                key="bridge_pick",
            )
            limit_root = st.slider(
                t("app.bridge_limit"),
                10, 500, 50, key="bridge_limit",
            )
            res_root = search.search_root(
                con, props[pick]["root_bw"], limit=limit_root
            )
            note = None
            if res_root.get("found") and res_root["count"] >= limit_root:
                note = t("app.bridge_note", n=res_root["count"], limit=limit_root)
            st.markdown(f"##### {t('app.original_heading')}")
            render_root_results(con, res_root, limit_note=note)

        # --- 2. Occurrences dans les traductions françaises ---------------
        st.markdown(f"#### {t('app.fr_occurrences')}")
        rows = search.search_french(con, q)
        st.write(t("app.rows_verses", n=len(rows)))
        if len(rows) >= 100:
            st.caption(t("app.limit_100"))
        bundle = search.verses_bundle(
            con, [(r["sura"], r["aya"]) for r in rows]
        )
        for r in rows:
            data = bundle.get((r["sura"], r["aya"]), {})
            render_verse(
                r["sura"], r["aya"],
                data.get("text_uthmani", r.get("text_uthmani", "")),
                data.get("translations", []),
                caption=t(
                    "app.hits_trans",
                    n=r["hits"],
                    keys=r["translation_keys"],
                ),
            )

    elif q:
        # --- Recherche arabe (texte original) -----------------------------
        rows = search.search_arabic(con, q)
        st.write(t("app.rows_verses", n=len(rows)))
        if len(rows) >= 100:
            st.caption(t("app.limit_100"))

        bundle = search.verses_bundle(
            con, [(r["sura"], r["aya"]) for r in rows]
        )
        for r in rows:
            data = bundle.get((r["sura"], r["aya"]), {})
            render_verse(
                r["sura"], r["aya"],
                data.get("text_uthmani", r.get("text_uthmani", "")),
                data.get("translations", []),
            )

# ------------------------------------------------------------------- Verset
with tab_verse:
    st.subheader(t("app.verse_title"))
    ui.universal_search(
        con, "verse",
        placeholder=t("app.verse_placeholder"),
    )

    mode = st.radio(
        t("app.mode"),
        ["compare", "similar"],
        horizontal=True,
        key="verse_mode",
        format_func=lambda m: (
            t("app.mode_compare") if m == "compare" else t("app.mode_similar")
        ),
    )

    # --- Mode 1 : comparaison manuelle de deux versets ---------------------
    if mode == "compare":
        st.caption(t("app.compare_caption"))
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**{t('app.verse_a')}**")
            sa, aa = ui.verse_picker(con, "a", default_sura=2, default_aya=255)
            va = search.get_verse(con, sa, aa)
        with colB:
            st.markdown(f"**{t('app.verse_b')}**")
            sb, ab = ui.verse_picker(con, "b", default_sura=4, default_aya=34)
            vb = search.get_verse(con, sb, ab)

        colA2, colB2 = st.columns(2)
        with colA2:
            if va:
                st.markdown(f"#### {db.surah_name(con, sa)} — {aa}")
                ui.render_verse(
                    sa, aa, va["text_uthmani"], va["translations"],
                    label=f"{sa}:{aa}", font_size="1.5rem",
                )
            else:
                st.warning(t("app.verse_missing", ref=t("app.verse_a")))
        with colB2:
            if vb:
                st.markdown(f"#### {db.surah_name(con, sb)} — {ab}")
                ui.render_verse(
                    sb, ab, vb["text_uthmani"], vb["translations"],
                    label=f"{sb}:{ab}", font_size="1.5rem",
                )
            else:
                st.warning(t("app.verse_missing", ref=t("app.verse_b")))

        if va and vb:
            ra = search.verse_root_set(con, sa, aa)
            rb = search.verse_root_set(con, sb, ab)
            common = ra & rb
            st.markdown(f"### {t('app.struct_title')}")
            st.markdown(
                t(
                    "app.common_roots",
                    n=len(common),
                    roots=(
                        " · ".join(sorted(buckwalter_to_arabic(r) for r in common))
                        or t("app.none")
                    ),
                )
            )
            cc1, cc2 = st.columns(2)
            cc1.markdown(
                t(
                    "app.roots_of",
                    ref=f"{sa}:{aa}",
                    n=len(ra),
                    roots=" · ".join(
                        sorted(buckwalter_to_arabic(r) for r in ra)
                    ),
                )
            )
            cc2.markdown(
                t(
                    "app.roots_of",
                    ref=f"{sb}:{ab}",
                    n=len(rb),
                    roots=" · ".join(
                        sorted(buckwalter_to_arabic(r) for r in rb)
                    ),
                )
            )

    # --- Mode 2 : suggestion automatique de versets similaires -------------
    else:
        st.caption(t("app.similar_caption"))
        qv = st.text_input(
            t("app.ref_input"),
            key="similar_q",
        )
        s1, s2 = st.columns(2)
        min_shared = s1.slider(
            t("app.min_shared"), 1, 6, 2, key="similar_min"
        )
        limit = s2.slider(
            t("app.nb_suggestions"), 5, 40, 12, key="similar_limit"
        )

        if qv and ":" in qv:
            msura = maya = None
            try:
                msura, maya = (int(x) for x in qv.split(":"))
            except ValueError:
                # Avertir sans interrompre le script : st.stop() couperait aussi
                # le rendu des onglets suivants (Thèmes, Idées reçues, …).
                st.warning(t("app.ref_format"))
            if msura is not None:
                base = search.get_verse(con, msura, maya)
                if base is None:
                    st.warning(t("app.ref_format", ref=f"{msura}:{maya}"))
                else:
                    st.markdown(f"**{t('app.ref_verse')}**")
                    ui.render_verse(
                        msura, maya, base["text_uthmani"], base["translations"],
                        label=f"{msura}:{maya}",
                    )
                    mir = search.mirror_verses(
                        con, msura, maya, limit=limit, min_shared=min_shared
                    )
                    st.markdown(
                        t(
                            "app.mirror_roots",
                            n=len(mir["roots_arabic"]),
                            roots=" · ".join(mir["roots_arabic"]),
                        )
                    )
                    st.markdown(
                        t("app.mirror_matches", n=len(mir["matches"]))
                    )
                    if not mir["matches"]:
                        st.info(t("app.mirror_empty"))
                    for m in mir["matches"]:
                        ui.render_verse(
                            m["sura"], m["aya"], m["text_uthmani"],
                            m["translations"],
                            label=t(
                                "app.mirror_label",
                                ref=f"{m['sura']}:{m['aya']}",
                                n=m["shared"],
                                pct=f"{m['ratio'] * 100:.0f}",
                            ),
                            caption=t(
                                "app.shared_roots_caption",
                                roots=" · ".join(m["roots_arabic"]),
                            ),
                        )
        elif qv:
            summary = ui.occurrence_summary(con, qv)
            roots = [p["root_bw"] for p in summary["props"]] if summary else []
            if not roots and summary and summary["ar_rows"]:
                roots = [
                    r["root_buckwalter"]
                    for r in search.top_roots_in_verses(
                        con,
                        [(r["sura"], r["aya"]) for r in summary["ar_rows"]],
                        top=8,
                    )
                ]
            if not roots:
                st.warning(t("app.no_roots_keyword", q=qv))
            else:
                sim = search.similar_verses_by_roots(
                    con, roots, limit=limit, min_shared=min_shared
                )
                st.markdown(
                    t(
                        "app.keyword_roots",
                        q=qv,
                        n=len(sim["roots_arabic"]),
                        roots=" · ".join(sim["roots_arabic"]),
                    )
                )
                st.markdown(
                    t("app.suggested_matches", n=len(sim["matches"]))
                )
                if not sim["matches"]:
                    st.info(t("app.mirror_empty"))
                for m in sim["matches"]:
                    ui.render_verse(
                        m["sura"], m["aya"], m["text_uthmani"], m["translations"],
                        label=t(
                            "app.mirror_label",
                            ref=f"{m['sura']}:{m['aya']}",
                            n=m["shared"],
                            pct=f"{m['ratio'] * 100:.0f}",
                        ),
                        caption=t(
                            "app.shared_roots_caption",
                            roots=" · ".join(m["roots_arabic"]),
                        ),
                    )

# ------------------------------------------------------------------- Thèmes
with tab_theme:
    st.subheader(t("app.theme_title"))
    ui.universal_search(
        con, "theme",
        placeholder=t("app.theme_placeholder"),
    )
    note = search.themes_meta(lang()).get("note", "")
    if note:
        st.caption(note)

    grouped = search.themes_by_category(lang())
    total = sum(len(v) for v in grouped.values())
    counts = theme_counts_cached(search.themes_fingerprint())

    col_q, col_cat = st.columns([3, 2])
    query = col_q.text_input(
        t("app.theme_query"),
        key="theme_query",
        placeholder=t("app.theme_query_ph"),
    )
    category = col_cat.selectbox(
        t("app.category"),
        ["all"] + list(grouped),
        key="theme_category",
        format_func=lambda c: (
            t("app.category_all") if c == "all" else c
        ),
    )

    filtered = search.filter_themes(
        query, None if category == "all" else category, lang()
    )
    shown = sum(counts.get(k, 0) for _, k, _ in filtered)
    st.caption(
        t(
            "app.theme_count",
            shown=len(filtered),
            total=total,
            cats=len(grouped),
            links=shown,
        )
    )

    if not filtered:
        st.info(t("app.theme_none"))
    else:
        labels = {
            k: f"{spec['label']}  ·  {cat}  —  {counts.get(k, 0)}"
            f" {t('app.tab.verse')}"
            for cat, k, spec in filtered
        }
        key = st.selectbox(
            t("app.theme_pick"),
            [k for _, k, _ in filtered],
            format_func=lambda k: labels[k],
            key="theme_pick",
            index=None,
            placeholder=t("app.theme_pick_ph"),
        )

        if key is None:
            st.info(t("app.theme_pick_wait"))
        else:
            res = search.theme(con, key, lang=lang())
            st.markdown(f"### {res['label']}")
            st.markdown(res["description"])
            extra = ""
            if res.get("terms_ar"):
                extra += t(
                    "app.theme_extra_ar",
                    terms=", ".join(res["terms_ar"]),
                )
            if res.get("terms_fr"):
                extra += t(
                    "app.theme_extra_fr",
                    terms=", ".join(res["terms_fr"]),
                )
            st.caption(
                t(
                    "app.theme_catline",
                    cat=res["category"],
                    roots=", ".join(res["roots"]),
                    n=res["verses_count"],
                    extra=extra,
                )
            )

            bundle = search.verses_bundle(
                con, [(v["sura"], v["aya"]) for v in res["verses"]]
            )
            for v in res["verses"]:
                data = bundle.get((v["sura"], v["aya"]), {})
                render_verse(
                    v["sura"], v["aya"],
                    data.get("text_uthmani", ""),
                    data.get("translations", []),
                    caption=t("app.theme_sources", src=", ".join(v["sources"])),
                )

        with st.expander(
            t("app.theme_overview", n=len(filtered))
        ):
            html_table(
                [
                    {
                        t("app.overview_cat"): c,
                        t("app.overview_theme"): s["label"],
                        t("app.overview_key"): k,
                        t("app.overview_roots"): " ".join(s.get("roots", [])),
                        t("app.overview_verses"): counts.get(k, 0),
                    }
                    for c, k, s in filtered
                ]
            )

# ------------------------------------------- Idées reçues et controverses
with tab_controv:
    st.subheader(t("app.controv_title"))
    ui.universal_search(
        con, "controv",
        placeholder=t("app.controv_placeholder"),
    )
    meta = search.controversy_meta(lang())
    st.info(meta.get("disclaimer", ""))
    st.caption(t("app.controv_method", m=meta.get("method", "")))

    topics = search.controversy_topics(lang())
    st.caption(t("app.controv_count", n=len(topics)))
    key = st.selectbox(
        t("app.controv_pick"), sorted(topics),
        format_func=lambda k: topics[k]["label"],
        index=None,
        placeholder=t("app.controv_pick_ph"),
        key="controv_pick",
    )
    if key is None:
        st.info(t("app.controv_wait"))
    elif key:
        res = search.controversy(con, key, lang=lang())
        st.markdown(f"### {res['label']}")
        st.markdown(t("app.controv_question", q=res["question"]))
        st.markdown(t("app.controv_framing", f=res["framing"]))
        if res["context_hint"]:
            st.caption(t("app.controv_read", tt=res["context_hint"]))

        st.markdown(f"**{t('app.recurrence_title')}**")
        html_table(
            [
                {
                    t("app.rec_type"): r["kind"],
                    t("app.rec_item"): r["label"],
                    t("app.rec_detail"): r["detail"],
                    t("app.rec_occ"): r["occurrences"],
                    t("app.rec_verses"): r["verses"],
                }
                for r in res["recurrence"]
            ]
        )

        if res.get("polysemy"):
            st.markdown(f"**{t('app.polysemy_title')}**")
            for poly in res["polysemy"]:
                with st.expander(
                    t(
                        "app.polysemy_form",
                        root=poly["root"],
                        bw=poly["buckwalter"],
                        n=poly["total"],
                        v=poly["verses"],
                    )
                ):
                    st.markdown(
                        t(
                            "app.polysemy_forms",
                            forms=" · ".join(
                                f"{f} ({n})" for f, n in poly["forms"]
                            ),
                        )
                    )
                    html_table(
                        [
                            {
                                t("app.poly_verse"): f"{o['sura']}:{o['aya']}",
                                t("app.poly_form"): o["form"],
                                "POS": o["pos"],
                                t("app.poly_context"): o["text_uthmani"],
                            }
                            for o in poly["occurrences"]
                        ]
                    )

        st.markdown(f"**{t('app.key_verses')}**")
        for v in res["verses"]:
            if v["missing"]:
                st.warning(
                    t("app.verse_missing_key", ref=f"{v['sura']}:{v['aya']}")
                )
                continue
            render_verse(v["sura"], v["aya"], v["text_uthmani"], v["translations"])

# ------------------------------- Concordance interne / versets en miroir
with tab_concord:
    st.subheader(t("app.concord_title"))
    ui.universal_search(
        con, "concord",
        placeholder=t("app.concord_placeholder"),
    )
    st.caption(t("app.concord_caption"))

    mode = st.radio(
        t("app.mode"),
        ["mirror", "notion"],
        horizontal=True,
        key="concord_mode",
        format_func=lambda m: (
            t("app.mode_mirror") if m == "mirror" else t("app.mode_notion")
        ),
    )

    if mode == "mirror":
        col_ref, col_opts = st.columns([2, 3])
        ref = col_ref.text_input(t("app.mirror_ref"), key="mirror_ref")
        min_shared = col_opts.slider(
            t("app.min_shared_mirror"), 1, 6, 2
        )
        limit = col_opts.slider(t("app.nb_mirror"), 5, 40, 12)
        if ref and ":" in ref:
            msura = maya = None
            try:
                msura, maya = (int(x) for x in ref.split(":"))
            except ValueError:
                # Avertir sans interrompre le script : st.stop() couperait aussi
                # le rendu des onglets suivants (Thèmes, Idées reçues, …).
                st.warning(t("app.ref_format"))
            if msura is not None:
                base = search.get_verse(con, msura, maya)
                if base is None:
                    st.warning(t("app.ref_format", ref=f"{msura}:{maya}"))
                else:
                    st.markdown(f"**{t('app.ref_verse')}**")
                    render_verse(
                        msura, maya, base["text_uthmani"], base["translations"],
                        label=f"{msura}:{maya}",
                    )
                    mir = search.mirror_verses(
                        con, msura, maya, limit=limit, min_shared=min_shared
                    )
                    st.markdown(
                        t(
                            "app.mirror_roots",
                            n=len(mir["roots_arabic"]),
                            roots=" · ".join(mir["roots_arabic"]),
                        )
                    )
                    st.markdown(
                        t("app.mirror_matches_n", n=len(mir["matches"]))
                    )
                    for m in mir["matches"]:
                        render_verse(
                            m["sura"], m["aya"], m["text_uthmani"],
                            m["translations"],
                            label=t(
                                "app.mirror_label",
                                ref=f"{m['sura']}:{m['aya']}",
                                n=m["shared"],
                                pct=f"{m['ratio']*100:.0f}",
                            ),
                            caption=t(
                                "app.shared_roots_caption",
                                roots=" · ".join(m["roots_arabic"]),
                            ),
                        )
    else:
        kind = st.radio(
            t("app.criterion"),
            ["root", "term"],
            horizontal=True,
            format_func=lambda k: (
                t("app.crit_root") if k == "root" else t("app.crit_term")
            ),
        )
        if kind == "root":
            value = st.text_input(
                t("app.root_input"), value="صبر",
                key="conc_root",
            )
            res = search.concordance(con, root=value) if value else {"found": False}
        else:
            value = st.text_input(
                t("app.arabic_term"), value="الصبر",
                key="conc_term",
            )
            res = search.concordance(con, term=value) if value else {"found": False}

        if res.get("found"):
            st.markdown(
                t(
                    "app.concord_line",
                    kind=t("ui.type.root") if kind == "root" else t("ui.type.term"),
                    label=res["label"],
                    detail=res["detail"],
                    n=res["occurrences"],
                    v=res["verses_count"],
                )
            )
            for v in res["verses"]:
                render_verse(v["sura"], v["aya"], v["text_uthmani"], v["translations"])
        elif value:
            st.warning(t("app.no_result"))

# ------------------------------------------------------------- Croisement
with tab_cross:
    st.subheader(t("app.cross_title"))
    st.caption(t("app.cross_caption"))

    _cmode = st.radio(
        t("app.mode"),
        ["pair", "co"],
        horizontal=True,
        key="cross_mode",
        format_func=lambda m: (
            t("app.cross_mode_pair") if m == "pair" else t("app.cross_mode_co")
        ),
    )

    if _cmode == "pair":
        _c1, _c2, _c3 = st.columns(3)
        _a = _c1.text_input(
            t("app.cross_root_a"), key="cross_a", placeholder=t("app.cross_ph")
        )
        _b = _c2.text_input(
            t("app.cross_root_b"), key="cross_b", placeholder=t("app.cross_ph")
        )
        _c = _c3.text_input(
            t("app.cross_root_c"), key="cross_c", placeholder=t("app.cross_ph")
        )
        _roots = [r for r in (_a, _b, _c) if r and r.strip()]
        if not _roots:
            st.caption(t("app.cross_need_root"))
        else:
            _res = search.verses_with_all_roots(con, _roots)
            if not _res.get("found"):
                st.warning(t("app.cross_notfound", r=_res.get("input", "")))
            else:
                st.markdown(
                    t(
                        "app.cross_result",
                        roots=" · ".join(_res["roots_arabic"]),
                        n=_res["verses_count"],
                    )
                )
                if not _res["verses"]:
                    st.info(t("app.cross_none"))
                for _v in _res["verses"]:
                    render_verse(
                        _v["sura"], _v["aya"], _v["text_uthmani"],
                        _v["translations"], bookmark=True,
                    )
    else:
        _r = st.text_input(
            t("app.cross_co_root"), key="cross_co", placeholder=t("app.cross_ph")
        )
        if _r:
            _res = search.co_roots(con, _r, top=25)
            if not _res.get("found"):
                st.warning(t("app.cross_notfound", r=_r))
            else:
                st.markdown(
                    t("app.cross_co_result", root=_res["root_arabic"])
                )
                if not _res["co_roots"]:
                    st.info(t("app.cross_co_none"))
                else:
                    html_table(
                        [
                            {
                                t("ui.table_root"): row["root_arabic"],
                                t("ui.table_bw"): row["root_buckwalter"],
                                t("ui.table_verses"): row["n"],
                            }
                            for row in _res["co_roots"]
                        ]
                    )

# ---------------------------------------------------------------- Favoris
with tab_bm:
    st.subheader(t("app.bm_title"))
    st.caption(t("app.bm_caption"))

    _entries = bookmarks.all_entries()
    st.markdown(t("app.bm_count", n=len(_entries)))

    _c1, _c2 = st.columns([3, 1])
    _ref = _c1.text_input(
        t("app.bm_add_ref"), key="bm_ref", placeholder=t("app.bm_ref_ph")
    )
    if _c2.button(t("app.bm_add_btn")):
        _parsed = ui.parse_ref(_ref)
        if _parsed is None:
            st.warning(t("app.bm_bad_ref"))
        elif search.get_verse(con, _parsed[0], _parsed[1]) is None:
            st.warning(t("app.bm_missing", ref=_ref))
        else:
            bookmarks.add(_parsed[0], _parsed[1])
            st.success(t("app.bm_added", ref=f"{_parsed[0]}:{_parsed[1]}"))
            st.rerun()

    if not _entries:
        st.info(t("app.bm_empty"))
    else:
        for _e in _entries:
            _sura, _aya = _e["sura"], _e["aya"]
            _verse = search.get_verse(con, _sura, _aya)
            if _verse is None:
                continue
            render_verse(
                _sura, _aya, _verse["text_uthmani"], _verse["translations"],
                bookmark=True,
            )
            with st.expander(t("app.bm_note") + f" — {_sura}:{_aya}"):
                _note = st.text_area(
                    t("app.bm_note"),
                    value=_e.get("note", ""),
                    key=f"bmnote_{_sura}_{_aya}",
                    placeholder=t("app.bm_note_ph"),
                )
                if st.button(
                    t("app.bm_save_note"), key=f"bmsave_{_sura}_{_aya}"
                ):
                    bookmarks.set_note(_sura, _aya, _note)
                    st.success(t("app.bm_save_note"))

        _lines = []
        for _e in _entries:
            _verse = search.get_verse(con, _e["sura"], _e["aya"])
            _frag = f"## {_e['sura']}:{_e['aya']}"
            if _e.get("note"):
                _frag += f" — {_e['note']}"
            _lines.append(_frag)
            if _verse:
                _lines.append(_verse["text_uthmani"])
                for _tr in ui.translations_for_lang(_verse["translations"]):
                    _lines.append(f"[{_tr['author']}] {_tr['text']}")
            _lines.append("")
        _payload = "\n".join(_lines)

        _b1, _b2 = st.columns(2)
        _b1.download_button(
            t("app.bm_export"),
            _payload,
            file_name="favoris.txt",
            key="bm_download",
        )
        if _b2.button(t("app.bm_clear")):
            bookmarks.clear()
            st.success(t("app.bm_cleared"))
            st.rerun()