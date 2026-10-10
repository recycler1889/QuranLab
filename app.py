"""Interface Streamlit locale pour quranlab.

Lancement :
    streamlit run app.py
"""

import streamlit as st

from quranlab import config, db, onboarding, search, ui
from quranlab import theme as theme_mod
from quranlab.buckwalter import buckwalter_to_arabic

# Rendu partagé (versets, tableaux, recherche universelle) : voir quranlab/ui.py.
html_table = ui.html_table
render_verse = ui.render_verse
render_root_results = ui.render_root_results

st.set_page_config(page_title="quranlab — analyse intra-coranique", layout="wide")

# --- Gestionnaire de thème visuel (Clair / Intermédiaire / Sombre) ---------
with st.sidebar:
    st.header("Préférences")
    theme_name = st.radio(
        "Thème visuel",
        theme_mod.ORDER,
        index=theme_mod.ORDER.index(theme_mod.DEFAULT),
        format_func=lambda k: theme_mod.PALETTES[k]["label"],
        key="theme_choice",
    )

    st.subheader("Audio")
    _reciters = list(getattr(config, "RECITERS", []) or [])
    _reciter_keys = [r.get("key") for r in _reciters if r.get("key")]
    st.selectbox(
        "Récitateur",
        _reciter_keys,
        format_func=lambda k: next(
            (r.get("label", k) for r in _reciters if r.get("key") == k), k
        ),
        key="reciter",
        help="Récitation verset par verset (EveryAyah).",
    )
    st.checkbox(
        "Lecteur coranique par verset", value=True, key="show_quran_audio"
    )
    st.checkbox(
        "Synthèse vocale (TTS)", value=True, key="show_tts",
        help="Lit chaque traduction à voix haute via le moteur du navigateur "
        "(voix française ou anglaise selon la traduction).",
    )

    st.divider()
    st.caption(
        "Lecture strictement intra-coranique — sans tafsir, hadith ni "
        "interprétation post-coranique."
    )
    st.divider()
    onboarding.sidebar_guide_button()

    with st.expander("Suggestions d'amélioration"):
        st.markdown(
            "QuranLab évolue au fil des usages. Idées, incohérences, sources à "
            "ajouter, nouveaux récitateurs ou langues, améliorations "
            "d'ergonomie : **faites-nous en part**."
        )
        if config.SUGGESTIONS_URL:
            st.markdown(f"[Proposer une amélioration]({config.SUGGESTIONS_URL})")
        else:
            st.caption(
                "Voir la section du même nom dans le guide de démarrage."
            )

st.markdown(theme_mod.css(theme_name), unsafe_allow_html=True)

ui.page_header(
    "quranlab",
    "Recherche et analyse strictement intra-coraniques — texte, structure, "
    "linguistique et racines. Sans tafsir, hadith ni interprétation "
    "post-coranique.",
)

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

    with st.spinner("Préparation de la base coranique (premier lancement)..."):
        ensure_db(verbose=False)
    return db.connect()


try:
    con = get_con()
except Exception as exc:  # noqa: BLE001
    st.error(f"Impossible de préparer la base : {exc}")
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


with st.sidebar:
    st.header("Corpus")
    stats = corpus_stats()
    n_themes = sum(len(v) for v in search.themes_by_category().values())
    n_topics = len(search.controversy_topics())

    def _fmt(n: int) -> str:
        return f"{n:,}".replace(",", " ")

    st.markdown(
        f"- **{_fmt(stats['surahs'])}** sourates · **{_fmt(stats['verses'])}** versets\n"
        f"- **{_fmt(stats['words'])}** mots annotés · **{_fmt(stats['roots'])}** racines distinctes\n"
        f"- **{stats['translations']}** traductions (FR/EN)\n"
        f"- **{n_themes}** thèmes · **{n_topics}** sujets d'analyse"
    )


tab_root, tab_search, tab_verse, tab_theme, tab_controv, tab_concord = st.tabs(
    ["Racine", "Recherche", "Verset comparé", "Thèmes", "Idées reçues", "Concordance"]
)

# --------------------------------------------------- Rendu partagé : racine
# ------------------------------------------------------------------ Racine
with tab_root:
    st.subheader("Indexation par racine")
    ui.universal_search(
        con, "root",
        placeholder="Rechercher en français ou en arabe (ex. miséricorde / رحمة)…",
    )
    st.caption("Saisir une racine en arabe (رحم) ou en Buckwalter (rHm).")
    col1, col2 = st.columns([3, 1])
    root_in = col1.text_input("Racine", key="root_in")
    ctx = col2.number_input("Contexte (± versets)", 0, 10, 1)
    if root_in:
        res = search.search_root(con, root_in, with_context=int(ctx))
        render_root_results(con, res)

# ---------------------------------------------------------------- Recherche
with tab_search:
    st.subheader("Recherche textuelle et multilingue")
    ui.universal_search(
        con, "search",
        placeholder="Rechercher un mot en français ou en arabe…",
    )
    lang = st.radio(
        "Langue", ["Français", "Arabe"], horizontal=True, key="search_lang"
    )
    q = st.text_input("Terme", key="q")

    if q and lang == "Français":
        # --- 1. Passerelle linguistique français -> arabe -----------------
        st.markdown("#### Passerelle français → arabe")
        props = search.french_bridge(con, q)["proposals"]
        if not props:
            st.info(
                "Aucune correspondance automatique trouvée pour ce terme "
                "(lexique, thèmes, corpus) — voir les résultats textuels "
                "français ci-dessous."
            )
        else:
            html_table(
                [
                    {
                        "français": p["fr"],
                        "racine": p["root_ar"],
                        "buckwalter": p["root_bw"],
                        "versets": p["verses"],
                        "occurrences": p["occurrences"],
                        "source": p["source"],
                    }
                    for p in props
                ]
            )
            pick = st.selectbox(
                "Interroger le texte original par racine",
                list(range(len(props))),
                format_func=lambda i: (
                    f"{props[i]['root_ar']} [{props[i]['root_bw']}] — "
                    f"{props[i]['fr']} · {props[i]['verses']} versets"
                ),
                key="bridge_pick",
            )
            limit_root = st.slider(
                "Occurrences de la racine à afficher",
                10, 500, 50, key="bridge_limit",
            )
            res_root = search.search_root(
                con, props[pick]["root_bw"], limit=limit_root
            )
            note = None
            if res_root.get("found") and res_root["count"] >= limit_root:
                note = (
                    f"Premières {res_root['count']} occurrences "
                    f"(limite réglée à {limit_root})."
                )
            st.markdown("##### Texte original (racine sélectionnée)")
            render_root_results(con, res_root, limit_note=note)

        # --- 2. Occurrences dans les traductions françaises ---------------
        st.markdown("#### Occurrences françaises (traductions)")
        rows = search.search_french(con, q)
        st.write(f"{len(rows)} verset(s) — un seul affichage par verset.")
        if len(rows) >= 100:
            st.caption("Limite atteinte : 100 premiers versets affichés.")
        bundle = search.verses_bundle(
            con, [(r["sura"], r["aya"]) for r in rows]
        )
        for r in rows:
            data = bundle.get((r["sura"], r["aya"]), {})
            render_verse(
                r["sura"], r["aya"],
                data.get("text_uthmani", r.get("text_uthmani", "")),
                data.get("translations", []),
                caption=(
                    f"terme présent dans {r['hits']} traduction(s) : "
                    f"{r['translation_keys']}"
                ),
            )

    elif q:
        # --- Recherche arabe (texte original) -----------------------------
        rows = search.search_arabic(con, q)
        st.write(f"{len(rows)} verset(s)")
        if len(rows) >= 100:
            st.caption("Limite atteinte : 100 premiers versets affichés.")

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
    st.subheader("Affichage comparatif et versets similaires")
    ui.universal_search(
        con, "verse",
        placeholder="Rechercher en français ou en arabe (ex. lumière / نور)…",
    )

    mode = st.radio(
        "Mode",
        ["Comparer deux versets", "Suggérer des versets similaires"],
        horizontal=True,
        key="verse_mode",
    )

    # --- Mode 1 : comparaison manuelle de deux versets ---------------------
    if mode == "Comparer deux versets":
        st.caption(
            "Sélectionnez deux versets indépendamment : ils sont affichés côte "
            "à côte avec leur texte arabe, leurs traductions et leurs racines."
        )
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Verset A**")
            sa, aa = ui.verse_picker(con, "a", default_sura=2, default_aya=255)
            va = search.get_verse(con, sa, aa)
        with colB:
            st.markdown("**Verset B**")
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
                st.warning("Verset A introuvable.")
        with colB2:
            if vb:
                st.markdown(f"#### {db.surah_name(con, sb)} — {ab}")
                ui.render_verse(
                    sb, ab, vb["text_uthmani"], vb["translations"],
                    label=f"{sb}:{ab}", font_size="1.5rem",
                )
            else:
                st.warning("Verset B introuvable.")

        if va and vb:
            ra = search.verse_root_set(con, sa, aa)
            rb = search.verse_root_set(con, sb, ab)
            common = ra & rb
            st.markdown("### Comparaison de structure thématique (racines)")
            st.markdown(
                f"**{len(common)} racine(s) commune(s)** : "
                + (" · ".join(sorted(buckwalter_to_arabic(r) for r in common))
                   or "aucune")
            )
            cc1, cc2 = st.columns(2)
            cc1.markdown(
                f"**Racines de {sa}:{aa} ({len(ra)})** — "
                + " · ".join(sorted(buckwalter_to_arabic(r) for r in ra))
            )
            cc2.markdown(
                f"**Racines de {sb}:{ab} ({len(rb)})** — "
                + " · ".join(sorted(buckwalter_to_arabic(r) for r in rb))
            )

    # --- Mode 2 : suggestion automatique de versets similaires -------------
    else:
        st.caption(
            "Saisissez une référence (sura:aya) pour trouver ses versets en "
            "miroir, ou un mot-clé (français ou arabe) pour une suggestion par "
            "proximité de racines."
        )
        qv = st.text_input(
            "Verset de référence (sura:aya) ou mot-clé",
            key="similar_q",
        )
        s1, s2 = st.columns(2)
        min_shared = s1.slider(
            "Racines communes minimales", 1, 6, 2, key="similar_min"
        )
        limit = s2.slider(
            "Nombre de suggestions", 5, 40, 12, key="similar_limit"
        )

        if qv and ":" in qv:
            msura = maya = None
            try:
                msura, maya = (int(x) for x in qv.split(":"))
            except ValueError:
                # Avertir sans interrompre le script : st.stop() couperait aussi
                # le rendu des onglets suivants (Thèmes, Idées reçues, …).
                st.warning("Format attendu : sura:aya (ex. 4:34)")
            if msura is not None:
                base = search.get_verse(con, msura, maya)
                if base is None:
                    st.warning("Verset introuvable.")
                else:
                    st.markdown("**Verset de référence**")
                    ui.render_verse(
                        msura, maya, base["text_uthmani"], base["translations"],
                        label=f"{msura}:{maya}",
                    )
                    mir = search.mirror_verses(
                        con, msura, maya, limit=limit, min_shared=min_shared
                    )
                    st.markdown(
                        f"**Racines du verset ({len(mir['roots_arabic'])}) :** "
                        + " · ".join(mir["roots_arabic"])
                    )
                    st.markdown(
                        f"**{len(mir['matches'])} verset(s) similaire(s)**"
                    )
                    if not mir["matches"]:
                        st.info(
                            "Aucun verset ne partage assez de racines — baissez "
                            "le seuil de racines communes minimales."
                        )
                    for m in mir["matches"]:
                        ui.render_verse(
                            m["sura"], m["aya"], m["text_uthmani"],
                            m["translations"],
                            label=(
                                f"{m['sura']}:{m['aya']}  ·  {m['shared']} "
                                f"racines communes ({m['ratio'] * 100:.0f}%)"
                            ),
                            caption=(
                                "racines partagées : "
                                + " · ".join(m["roots_arabic"])
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
                st.warning(
                    f"Aucune racine exploitable pour « {qv} » — essayez un autre "
                    "mot-clé ou une référence sura:aya."
                )
            else:
                sim = search.similar_verses_by_roots(
                    con, roots, limit=limit, min_shared=min_shared
                )
                st.markdown(
                    f"**Racines du mot-clé « {qv} » ({len(sim['roots_arabic'])}) :** "
                    + " · ".join(sim["roots_arabic"])
                )
                st.markdown(
                    f"**{len(sim['matches'])} verset(s) similaire(s) suggéré(s)**"
                )
                if not sim["matches"]:
                    st.info(
                        "Aucun verset ne partage assez de racines — baissez le "
                        "seuil de racines communes minimales."
                    )
                for m in sim["matches"]:
                    ui.render_verse(
                        m["sura"], m["aya"], m["text_uthmani"], m["translations"],
                        label=(
                            f"{m['sura']}:{m['aya']}  ·  {m['shared']} racines "
                            f"communes ({m['ratio'] * 100:.0f}%)"
                        ),
                        caption="racines partagées : " + " · ".join(m["roots_arabic"]),
                    )

# ------------------------------------------------------------------- Thèmes
with tab_theme:
    st.subheader("Cartographie thématique intra-coranique")
    ui.universal_search(
        con, "theme",
        placeholder="Rechercher en français ou en arabe (lancera aussi la passerelle)…",
    )
    note = search.load_themes().get("_meta", {}).get("note", "")
    if note:
        st.caption(note)

    grouped = search.themes_by_category()
    total = sum(len(v) for v in grouped.values())
    counts = theme_counts_cached(search.themes_fingerprint())

    col_q, col_cat = st.columns([3, 2])
    query = col_q.text_input(
        "Rechercher un thème (libellé, description, racine, terme…)",
        key="theme_query",
        placeholder="ex. salât, رحم, miséricorde, or, orphelins…",
    )
    category = col_cat.selectbox(
        "Catégorie", ["Toutes"] + list(grouped), key="theme_category"
    )

    filtered = search.filter_themes(
        query, None if category == "Toutes" else category
    )
    shown = sum(counts.get(k, 0) for _, k, _ in filtered)
    st.caption(
        f"{len(filtered)} thème(s) affiché(s) sur {total} · "
        f"{len(grouped)} catégories · {shown} rattachement(s) thème↔verset."
    )

    if not filtered:
        st.info(
            "Aucun thème ne correspond — modifiez le mot-clé ou repassez la "
            "catégorie sur « Toutes »."
        )
    else:
        labels = {
            k: f"{spec['label']}  ·  {cat}  —  {counts.get(k, 0)} verset(s)"
            for cat, k, spec in filtered
        }
        key = st.selectbox(
            "Thème",
            [k for _, k, _ in filtered],
            format_func=lambda k: labels[k],
            key="theme_pick",
            index=None,
            placeholder="— Choisissez un thème pour voir ses versets —",
        )

        if key is None:
            st.info(
                "Sélectionnez un thème ci-dessus : les versets rattachés et leur "
                "récitation s'afficheront ici (rien n'est chargé tant que rien "
                "n'est choisi — l'interface reste légère)."
            )
        else:
            res = search.theme(con, key)
            st.markdown(f"### {res['label']}")
            st.markdown(res["description"])
            extra = ""
            if res.get("terms_ar"):
                extra += f" · termes arabe : {', '.join(res['terms_ar'])}"
            if res.get("terms_fr"):
                extra += f" · termes fr : {', '.join(res['terms_fr'])}"
            st.caption(
                f"Catégorie : {res['category']} · Racines : {', '.join(res['roots'])} · "
                f"{res['verses_count']} verset(s){extra}"
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
                    caption="sources : " + ", ".join(v["sources"]),
                )

        with st.expander(f"Vue d'ensemble des {len(filtered)} thème(s) affiché(s)"):
            html_table(
                [
                    {
                        "catégorie": c,
                        "thème": s["label"],
                        "clé": k,
                        "racines": " ".join(s.get("roots", [])),
                        "versets": counts.get(k, 0),
                    }
                    for c, k, s in filtered
                ]
            )

# ------------------------------------------- Idées reçues et controverses
with tab_controv:
    st.subheader("Analyse textuelle des idées reçues et controverses")
    ui.universal_search(
        con, "controv",
        placeholder="Rechercher en français ou en arabe (ex. femme / نساء)…",
    )
    meta = search.load_controversies().get("_meta", {})
    st.info(meta.get("disclaimer", ""))
    st.caption("Méthode : " + meta.get("method", ""))

    topics = search.controversy_topics()
    st.caption(
        f"{len(topics)} sujets — analyse textuelle descriptive, sans conclusion doctrinale."
    )
    key = st.selectbox(
        "Sujet", sorted(topics), format_func=lambda k: topics[k]["label"],
        index=None,
        placeholder="— Choisissez un sujet pour voir son analyse —",
    )
    if key is None:
        st.info(
            "Choisissez un sujet dans la liste : récurrence lexicale, polysémie "
            "et versets clés s'afficheront ici."
        )
    elif key:
        res = search.controversy(con, key)
        st.markdown(f"### {res['label']}")
        st.markdown(f"**Question posée :** {res['question']}")
        st.markdown(f"**Note intra-coranique :** {res['framing']}")
        if res["context_hint"]:
            st.caption("Lecture conseillée : " + res["context_hint"])

        st.markdown("**Récurrence lexicale dans tout le corpus**")
        html_table(
            [
                {
                    "type": r["kind"],
                    "élément": r["label"],
                    "clé": r["detail"],
                    "occurrences": r["occurrences"],
                    "versets": r["verses"],
                }
                for r in res["recurrence"]
            ]
        )

        if res.get("polysemy"):
            st.markdown("**Polysémie — toutes les formes d'une même racine**")
            for poly in res["polysemy"]:
                with st.expander(
                    f"Racine {poly['root']} [{poly['buckwalter']}] — "
                    f"{poly['total']} occurrences / {poly['verses']} versets"
                ):
                    st.markdown(
                        "Formes rencontrées : "
                        + " · ".join(f"{f} ({n})" for f, n in poly["forms"])
                    )
                    html_table(
                        [
                            {
                                "verset": f"{o['sura']}:{o['aya']}",
                                "forme": o["form"],
                                "POS": o["pos"],
                                "contexte": o["text_uthmani"],
                            }
                            for o in poly["occurrences"]
                        ]
                    )

        st.markdown("**Versets clés — texte arabe et traductions plurielles**")
        for v in res["verses"]:
            if v["missing"]:
                st.warning(f"Verset introuvable : {v['sura']}:{v['aya']}")
                continue
            render_verse(v["sura"], v["aya"], v["text_uthmani"], v["translations"])

# ------------------------------- Concordance interne / versets en miroir
with tab_concord:
    st.subheader("Concordance interne — « le Coran s'explique par le Coran »")
    ui.universal_search(
        con, "concord",
        placeholder="Rechercher en français ou en arabe pour bâtir une concordance…",
    )
    st.caption(
        "Croisement de versets par racines partagées : concordance par notion, "
        "et versets en miroir d'un verset de référence."
    )

    mode = st.radio(
        "Mode", ["Verset en miroir", "Concordance par notion"], horizontal=True
    )

    if mode == "Verset en miroir":
        col_ref, col_opts = st.columns([2, 3])
        ref = col_ref.text_input("Verset de référence (sura:aya)", key="mirror_ref")
        min_shared = col_opts.slider("Racines communes minimales", 1, 6, 2)
        limit = col_opts.slider("Nombre de versets en miroir", 5, 40, 12)
        if ref and ":" in ref:
            msura = maya = None
            try:
                msura, maya = (int(x) for x in ref.split(":"))
            except ValueError:
                # Avertir sans interrompre le script : st.stop() couperait aussi
                # le rendu des onglets suivants (Thèmes, Idées reçues, …).
                st.warning("Format attendu : sura:aya (ex. 4:34)")
            if msura is not None:
                base = search.get_verse(con, msura, maya)
                if base is None:
                    st.warning("Verset introuvable.")
                else:
                    st.markdown("**Verset de référence**")
                    render_verse(
                        msura, maya, base["text_uthmani"], base["translations"],
                        label=f"{msura}:{maya}",
                    )
                    mir = search.mirror_verses(
                        con, msura, maya, limit=limit, min_shared=min_shared
                    )
                    st.markdown(
                        f"**Racines du verset ({len(mir['roots_arabic'])}) :** "
                        + " · ".join(mir["roots_arabic"])
                    )
                    st.markdown(f"**{len(mir['matches'])} verset(s) en miroir**")
                    for m in mir["matches"]:
                        render_verse(
                            m["sura"], m["aya"], m["text_uthmani"],
                            m["translations"],
                            label=(
                                f"{m['sura']}:{m['aya']}  ·  {m['shared']} "
                                f"racines communes ({m['ratio']*100:.0f}%)"
                            ),
                            caption=(
                                "racines partagées : "
                                + " · ".join(m["roots_arabic"])
                            ),
                        )
    else:
        kind = st.radio("Critère", ["Racine", "Terme arabe"], horizontal=True)
        if kind == "Racine":
            value = st.text_input("Racine (arabe ou Buckwalter)", value="صبر", key="conc_root")
            res = search.concordance(con, root=value) if value else {"found": False}
        else:
            value = st.text_input("Terme arabe", value="الصبر", key="conc_term")
            res = search.concordance(con, term=value) if value else {"found": False}

        if res.get("found"):
            st.markdown(
                f"**Concordance {res['kind']} : {res['label']}** "
                f"`[{res['detail']}]` — {res['occurrences']} occurrence(s) "
                f"dans {res['verses_count']} verset(s)"
            )
            for v in res["verses"]:
                render_verse(v["sura"], v["aya"], v["text_uthmani"], v["translations"])
        elif value:
            st.warning("Aucun résultat.")
