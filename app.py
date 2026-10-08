"""Interface Streamlit locale pour quranlab.

Lancement :
    streamlit run app.py
"""

import html

import streamlit as st

from quranlab import db, search
from quranlab import theme as theme_mod

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
    st.caption(
        "Lecture strictement intra-coranique — sans tafsir, hadith ni "
        "interprétation post-coranique."
    )

st.markdown(theme_mod.css(theme_name), unsafe_allow_html=True)

st.title("quranlab")
st.caption(
    "Recherche et analyse strictement intra-coraniques — texte, structure, "
    "linguistique et racines. Sans tafsir, hadith ni interprétation post-coranique."
)


def html_table(rows: list, columns: list | None = None) -> None:
    """Tableau HTML thémé (respecte les variables CSS --ql-*)."""
    if not rows:
        return
    columns = columns or list(rows[0].keys())
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in columns
        ) + "</tr>"
        for r in rows
    )
    st.markdown(
        f"<table class='ql'><thead><tr>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table>",
        unsafe_allow_html=True,
    )


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

SURAH_NAMES = db.surah_names(con)


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
        f"- **{stats['translations']}** traductions françaises\n"
        f"- **{n_themes}** thèmes · **{n_topics}** sujets d'analyse"
    )


# --------------------------------------------------------------------------
# Rendu unifié d'un verset : texte arabe (RTL) + traductions françaises
# --------------------------------------------------------------------------
def render_verse(
    sura: int,
    aya: int,
    text_uthmani: str,
    translations: list,
    label: str | None = None,
    caption: str | None = None,
    font_size: str = "1.45rem",
) -> None:
    """Affiche un verset : référence (avec nom de sourate), texte arabe uthmani
    puis, systématiquement, les traductions françaises empilées."""
    ref = f"{sura}:{aya}"
    name = SURAH_NAMES.get(sura, "")
    st.markdown(f"**{label or (f'{ref} — {name}' if name else ref)}**")
    st.markdown(
        f"<div dir='rtl' lang='ar' style='font-size:{font_size};"
        f"line-height:2.2;margin:.2rem 0 .5rem 0'>{text_uthmani}</div>",
        unsafe_allow_html=True,
    )
    if not translations:
        st.caption("Aucune traduction disponible.")
    for t in translations:
        st.markdown(f"**{t['author']}** — {t['text']}")
    if caption:
        st.caption(caption)
    st.divider()


tab_root, tab_search, tab_verse, tab_theme, tab_controv, tab_concord = st.tabs(
    ["Racine", "Recherche", "Verset comparé", "Thèmes", "Idées reçues", "Concordance"]
)

# --------------------------------------------------- Rendu partagé : racine
def render_root_results(con, res, limit_note: str | None = None) -> None:
    """Résumé + occurrences d'une racine (expanders : verset complet)."""
    if not res.get("found"):
        st.warning(f"Racine introuvable : {res.get('input', '')}")
        return
    st.markdown(
        f"**Racine {res['root_arabic']}** `[{res['root_buckwalter']}]` — "
        f"{res['count']} occurrence(s) dans {res['verses_count']} verset(s)"
    )
    if limit_note:
        st.caption(limit_note)
    elif res["count"] >= 1000:
        st.caption("Limite atteinte : 1000 premières occurrences affichées.")

    # Traductions de tous les versets concernés (+ contexte) en une passe.
    refs = [(o["sura"], o["aya"]) for o in res["occurrences"]]
    for o in res["occurrences"]:
        if "context" in o:
            refs += [(c["sura"], c["aya"])
                     for c in o["context"]["before"] + o["context"]["after"]]
    bundle = search.verses_bundle(con, refs)

    # Un seul expander par verset, même si le racine y apparaît en plusieurs
    # formes (ex. « فَاصْبِرْ » + « صَبْرٌ » dans le même verset).
    by_verse: dict = {}
    for o in res["occurrences"]:
        by_verse.setdefault((o["sura"], o["aya"]), []).append(o)

    for (sura, aya), occs in by_verse.items():
        nom = SURAH_NAMES.get(sura, "")
        forms = " · ".join(dict.fromkeys(o["form_arabic"] for o in occs))
        with st.expander(f"{sura}:{aya} — {nom} · {forms}"):
            data = bundle.get((sura, aya), {})
            ctx = occs[0].get("context", {})
            for c in ctx.get("before", []):
                cd = bundle.get((c["sura"], c["aya"]), {})
                render_verse(
                    c["sura"], c["aya"],
                    cd.get("text_uthmani", c["text_uthmani"]),
                    cd.get("translations", []),
                    font_size="1.1rem",
                )
            render_verse(
                sura, aya,
                data.get("text_uthmani", occs[0]["text_uthmani"]),
                data.get("translations", []),
                caption=" · ".join(
                    f"{o['form_arabic']} ({o['transliteration']}, {o['pos']}, "
                    f"lemme {o['lemma_buckwalter']})"
                    for o in occs
                ),
            )
            for c in ctx.get("after", []):
                cd = bundle.get((c["sura"], c["aya"]), {})
                render_verse(
                    c["sura"], c["aya"],
                    cd.get("text_uthmani", c["text_uthmani"]),
                    cd.get("translations", []),
                    font_size="1.1rem",
                )


# ------------------------------------------------------------------ Racine
with tab_root:
    st.subheader("Indexation par racine")
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
    st.subheader("Affichage comparatif multi-sources")
    ref = st.text_input("Référence (sura:aya)", value="2:255", key="ref")
    if ref and ":" in ref:
        try:
            sura, aya = (int(x) for x in ref.split(":"))
        except ValueError:
            st.warning("Format attendu : sura:aya (ex. 2:255)")
            st.stop()
        v = search.get_verse(con, sura, aya)
        if v is None:
            st.warning("Verset introuvable.")
        else:
            st.markdown(f"### {db.surah_name(con, sura)} — {aya}")
            render_verse(
                sura, aya, v["text_uthmani"], v["translations"],
                label="Texte et traductions", font_size="1.8rem",
            )
            st.markdown("**Analyse mot-à-mot**")
            html_table(
                [
                    {
                        "n": w["word_index"],
                        "forme": w["form_arabic"],
                        "translittération": w["transliteration"],
                        "racine": w["root_arabic"],
                        "POS": w["pos"],
                    }
                    for w in v["words"]
                ]
            )

# ------------------------------------------------------------------- Thèmes
with tab_theme:
    st.subheader("Cartographie thématique intra-coranique")
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
        )

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
    meta = search.load_controversies().get("_meta", {})
    st.info(meta.get("disclaimer", ""))
    st.caption("Méthode : " + meta.get("method", ""))

    topics = search.controversy_topics()
    st.caption(
        f"{len(topics)} sujets — analyse textuelle descriptive, sans conclusion doctrinale."
    )
    key = st.selectbox(
        "Sujet", sorted(topics), format_func=lambda k: topics[k]["label"]
    )
    if key:
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
    st.caption(
        "Croisement de versets par racines partagées : concordance par notion, "
        "et versets en miroir d'un verset de référence."
    )

    mode = st.radio(
        "Mode", ["Verset en miroir", "Concordance par notion"], horizontal=True
    )

    if mode == "Verset en miroir":
        col_ref, col_opts = st.columns([2, 3])
        ref = col_ref.text_input("Verset de référence (sura:aya)", value="4:34", key="mirror_ref")
        min_shared = col_opts.slider("Racines communes minimales", 1, 6, 2)
        limit = col_opts.slider("Nombre de versets en miroir", 5, 40, 12)
        if ref and ":" in ref:
            try:
                msura, maya = (int(x) for x in ref.split(":"))
            except ValueError:
                st.warning("Format attendu : sura:aya (ex. 4:34)")
                st.stop()
            base = search.get_verse(con, msura, maya)
            if base is None:
                st.warning("Verset introuvable.")
            else:
                st.markdown("**Verset de référence**")
                render_verse(
                    msura, maya, base["text_uthmani"], base["translations"],
                    label=f"{msura}:{maya}",
                )
                mir = search.mirror_verses(con, msura, maya, limit=limit, min_shared=min_shared)
                st.markdown(
                    f"**Racines du verset ({len(mir['roots_arabic'])}) :** "
                    + " · ".join(mir["roots_arabic"])
                )
                st.markdown(f"**{len(mir['matches'])} verset(s) en miroir**")
                for m in mir["matches"]:
                    render_verse(
                        m["sura"], m["aya"], m["text_uthmani"], m["translations"],
                        label=(
                            f"{m['sura']}:{m['aya']}  ·  {m['shared']} racines "
                            f"communes ({m['ratio']*100:.0f}%)"
                        ),
                        caption="racines partagées : " + " · ".join(m["roots_arabic"]),
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
