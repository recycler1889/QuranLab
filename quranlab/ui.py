"""Composants d'interface partagés par tous les onglets de QuranLab.

Regroupe le rendu de versets (arabe RTL + traductions), les tableaux HTML
thémés, et surtout la **passerelle de recherche français → arabe universelle**
avec son **compteur d'occurrences** commun. `app.py` ne fait plus qu'orchestrer
les onglets et appelle ces briques.

Aucune logique de base ici : tout passe par `search` / `db`. Ce module ne
dépend que de Streamlit pour l'affichage.
"""

from __future__ import annotations

import html
import json

import streamlit as st

from . import config, db, search
from . import theme as theme_mod
from .buckwalter import is_arabic

# --------------------------------------------------------------------------
# Noms de sourates (cache paresseux — évite de dépendre d'app.py)
# --------------------------------------------------------------------------
_NAMES: dict | None = None


def surah_names() -> dict:
    """{numéro: nom translittéré} — chargé une fois par processus."""
    global _NAMES
    if _NAMES is None:
        _NAMES = db.surah_names(db.connect())
    return _NAMES


# --------------------------------------------------------------------------
# Rendu de base
# --------------------------------------------------------------------------
def page_header(title: str, subtitle: str) -> None:
    """Bandeau de titre orné (motif de mosaïque + fleuron calligraphique).

    Habille l'en-tête sans recourir à st.title/st.caption, afin de bénéficier
    de la charte décorative (variables CSS --ql-*, classes .ql-banner).
    """
    st.markdown(
        "<div class='ql-banner'>"
        f"<h1 class='ql-title'>{html.escape(title)}</h1>"
        "<div class='ql-rule'></div>"
        f"<p class='ql-subtitle'>{html.escape(subtitle)}</p>"
        "</div>",
        unsafe_allow_html=True,
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


# --------------------------------------------------------------------------
# Lecteurs audio : récitation coranique (verset) et TTS (traduction FR/EN)
# --------------------------------------------------------------------------
def _palette() -> dict:
    """Palette visuelle courante (suit le sélecteur de thème de la sidebar)."""
    name = st.session_state.get("theme_choice", theme_mod.DEFAULT)
    return theme_mod.PALETTES.get(name, theme_mod.PALETTES[theme_mod.DEFAULT])


def active_reciter() -> dict:
    """Récitateur sélectionné (repli sur le premier de config.RECITERS)."""
    key = st.session_state.get("reciter")
    for r in config.RECITERS:
        if r["key"] == key:
            return r
    return config.RECITERS[0]


def quran_audio(sura: int, aya: int, reciter: dict | None = None) -> None:
    """Lecteur audio compact et **indépendant** pour un verset donné.

    Chaque appel produit un composant autonome (bouton Lecture/Pause + Arrêt)
    branché sur l'URL du récitateur choisi ; les lecteurs de deux versets ne se
    perturbent donc pas mutuellement.
    """
    pal = _palette()
    reciter = reciter or active_reciter()
    url = config.audio_url(reciter["edition"], sura, aya)
    title = html.escape(f"{reciter['label']} · {sura}:{aya}")
    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;}}
      .bar{{display:flex;align-items:center;gap:6px;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      button{{cursor:pointer;border:1px solid {pal['border']};
        background:{pal['field']};color:{pal['fg']};border-radius:999px;
        height:28px;padding:0 10px;font-size:12.5px;display:inline-flex;
        align-items:center;gap:5px;transition:.15s;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
      .meta{{font-size:11px;color:{pal['fg2']};white-space:nowrap;
        overflow:hidden;text-overflow:ellipsis;max-width:170px;}}
    </style></head><body>
      <div class="bar">
        <button id="pp" title="Lecture / Pause">&#9654; Écouter</button>
        <button id="st" title="Arrêter">&#9632;</button>
        <span class="meta">{title}</span>
        <audio id="au" preload="none" src="{url}"></audio>
      </div>
      <script>
        var au=document.getElementById('au'),pp=document.getElementById('pp');
        pp.addEventListener('click',function(){{
          if(au.paused){{au.play();pp.textContent='\u275A\u275A Pause';}}
          else{{au.pause();pp.textContent='\u25B6 Écouter';}}
        }});
        document.getElementById('st').addEventListener('click',function(){{
          au.pause();au.currentTime=0;pp.textContent='\u25B6 Écouter';
        }});
        au.addEventListener('ended',function(){{
          pp.textContent='\u25B6 Écouter';}});
      </script>
    </body></html>"""
    st.iframe(comp, height=36)


def tts(text: str, language: str = "fr") -> None:
    """Bouton de synthèse vocale (Web Speech API du navigateur) d'un texte.

    La voix suit la langue de la traduction (``fr`` → fr-FR, ``en`` → en-US).
    Composant autonome : chaque traduction dispose de son propre lecteur, qui
    bascule entre « Lire » et « Stop ». Aucune clé/API externe n'est requise ;
    le moteur TTS est celui du navigateur.
    """
    pal = _palette()
    locale = config.tts_locale(language)
    # json.dumps → littéral JS sûr ; « < » échappé pour ne pas clore </script>.
    payload = json.dumps(text or "", ensure_ascii=False).replace("<", "\\u003c")
    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;}}
      button{{cursor:pointer;border:1px solid {pal['border']};
        background:{pal['field']};color:{pal['fg2']};border-radius:999px;
        height:26px;padding:0 10px;font-size:12px;display:inline-flex;
        align-items:center;gap:5px;transition:.15s;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
    </style></head><body>
      <button id="b" title="Lire à voix haute ({locale})">
        &#9654; Lire</button>
      <script>
        var b=document.getElementById('b'),t={payload};
        b.addEventListener('click',function(){{
          if(!('speechSynthesis' in window)){{
            b.textContent='TTS indisponible';return;}}
          if(b.dataset.on==='1'){{
            speechSynthesis.cancel();
            b.dataset.on='0';b.textContent='\u25B6 Lire';return;}}
          var u=new SpeechSynthesisUtterance(t);
          u.lang='{locale}';u.rate=0.98;
          u.onend=function(){{
            b.dataset.on='0';b.textContent='\u25B6 Lire';}};
          speechSynthesis.cancel();speechSynthesis.speak(u);
          b.dataset.on='1';b.textContent='\u25A0 Stop';
        }});
      </script>
    </body></html>"""
    st.iframe(comp, height=30)


def verse_media(
    sura: int,
    aya: int,
    translations: list,
    reciter: dict | None = None,
) -> None:
    """Lecteur unique par verset : **un seul iframe** au lieu d'un par lecteur.

    Regroupe le lecteur de récitation (verset) et un bouton **Lire** par
    traduction (voix selon la langue de la traduction). Quand de nombreux
    versets sont affichés, divise par ~6 le nombre de composants embarqués.
    """
    show_audio = st.session_state.get("show_quran_audio", True)
    show_tts = st.session_state.get("show_tts", True)
    tts_items = [t for t in translations if show_tts and t.get("text")]
    if not show_audio and not tts_items:
        return

    pal = _palette()
    reciter = reciter or active_reciter()
    items = [
        {
            "i": i,
            "lang": config.tts_locale(t.get("language", "fr")),
            "author": html.escape(t.get("author", "")),
            "text": t["text"],
        }
        for i, t in enumerate(tts_items)
    ]
    payload = json.dumps(
        [{"t": it["text"], "lang": it["lang"]} for it in items],
        ensure_ascii=False,
    ).replace("<", "\\u003c")

    audio_row = ""
    audio_js = ""
    if show_audio:
        url = config.audio_url(reciter["edition"], sura, aya)
        title = html.escape(f"{reciter['label']} · {sura}:{aya}")
        audio_row = f"""
        <div class="row">
          <button id="pp" title="Lecture / Pause">&#9654; Écouter</button>
          <button id="st" title="Arrêter">&#9632;</button>
          <span class="meta">{title}</span>
          <audio id="au" preload="none" src="{url}"></audio>
        </div>"""
        audio_js = """
        var au=document.getElementById('au');
        document.getElementById('pp').addEventListener('click',function(){
          if(au.paused){au.play();this.textContent='\u275A\u275A Pause';}
          else{au.pause();this.textContent='\u25B6 Écouter';}
        });
        document.getElementById('st').addEventListener('click',function(){
          au.pause();au.currentTime=0;
          document.getElementById('pp').textContent='\u25B6 Écouter';});
        au.addEventListener('ended',function(){
          document.getElementById('pp').textContent='\u25B6 Écouter';});"""

    buttons = "".join(
        '<div class="row tts">'
        f'<button id="l{it["i"]}" title="{it["author"]}">'
        "&#9654; Lire&nbsp;·&nbsp;"
        f'{it["lang"].split("-")[0]}</button></div>'
        for it in items
    )

    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;}}
      .row{{display:flex;align-items:center;gap:6px;margin:1px 0;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      button{{cursor:pointer;border:1px solid {pal['border']};
        background:{pal['field']};color:{pal['fg']};border-radius:999px;
        height:26px;padding:0 10px;font-size:12px;display:inline-flex;
        align-items:center;gap:5px;transition:.15s;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
      .row.tts button{{color:{pal['fg2']};height:23px;font-size:11.5px;}}
      .meta{{font-size:11px;color:{pal['fg2']};white-space:nowrap;
        overflow:hidden;text-overflow:ellipsis;max-width:170px;}}
    </style></head><body>
      {audio_row}
      {buttons}
      <script>
        var synth=window.speechSynthesis,voices=[];
        function norm(s){{return (s||'').split('_').join('-').toLowerCase();}}
        function load(){{voices=synth.getVoices()||[];}}
        load();if(synth.onvoiceschanged!==undefined){{synth.onvoiceschanged=load;}}
        function pickVoice(lang,base){{
          if(!voices.length){{load();}}
          var pool=voices.filter(function(v){{
            return norm(v.lang)===lang.toLowerCase();}});
          if(!pool.length){{pool=voices.filter(function(v){{
            return norm(v.lang).indexOf(base)===0;}});}}
          if(!pool.length){{return null;}}
          var PREF=['google '+base,'microsoft paulina','microsoft hortense',
            'microsoft julie','microsoft denise','hortense','am\u00e9lie',
            'amelie','audrey','virginie','google'];
          for(var j=0;j<PREF.length;j++){{
            var h=pool.filter(function(v){{
              return norm(v.name).indexOf(PREF[j])>=0;}});
            if(h.length){{return h[0];}}
          }}
          return pool[0];
        }}
        var ITEMS={payload};
        function speak(i){{
          var b=document.getElementById('l'+i);
          if(!('speechSynthesis' in window)){{
            b.textContent='TTS indisponible';return;}}
          if(b&&b.dataset.on==='1'){{
            synth.cancel();b.dataset.on='0';
            b.textContent='\u25B6 Lire';return;}}
          var base=ITEMS[i].lang.split('-')[0];
          var u=new SpeechSynthesisUtterance(ITEMS[i].t);
          u.lang=ITEMS[i].lang;u.rate=0.95;
          var v=pickVoice(ITEMS[i].lang,base);
          if(v){{u.voice=v;}}
          var done=function(){{
            if(b){{b.dataset.on='0';b.textContent='\u25B6 Lire';}}}};
          u.onend=done;u.onerror=done;
          synth.cancel();
          setTimeout(function(){{synth.speak(u);}},80);
          if(b){{b.dataset.on='1';b.textContent='\u25A0 Stop';}}
        }}
        {audio_js}
        for(var k=0;k<ITEMS.length;k++){{
          (function(i){{
            document.getElementById('l'+i).addEventListener(
              'click',function(){{speak(i);}});
          }})(ITEMS[k].i);
        }}
      </script>
    </body></html>"""
    st.iframe(comp, height=34 + len(items) * 26)


def render_verse(
    sura: int,
    aya: int,
    text_uthmani: str,
    translations: list,
    label: str | None = None,
    caption: str | None = None,
    font_size: str = "1.45rem",
    audio: bool = True,
) -> None:
    """Affiche un verset : référence (avec nom de sourate), texte arabe uthmani
    puis, systématiquement, les traductions empilées.

    Si les préférences l'autorisent, un **lecteur de récitation** (verset) et un
    bouton **de synthèse vocale** (voix suivant la langue de la traduction) par
    traduction sont ajoutés. ``audio=False`` permet de désactiver la récitation
    (ex. versets de contexte).
    """
    names = surah_names()
    ref = f"{sura}:{aya}"
    name = names.get(sura, "")
    show_audio = bool(audio) and st.session_state.get("show_quran_audio", True)
    show_tts = st.session_state.get("show_tts", True)
    st.markdown(f"**{label or (f'{ref} — {name}' if name else ref)}**")
    st.markdown(
        f"<div dir='rtl' lang='ar' style='font-size:{font_size};"
        f"line-height:2.2;margin:.2rem 0 .5rem 0'>{text_uthmani}</div>",
        unsafe_allow_html=True,
    )
    if show_audio or (show_tts and translations):
        verse_media(sura, aya, translations)
    if not translations:
        st.caption("Aucune traduction disponible.")
    for t in translations:
        st.markdown(f"**{t['author']}** — {t['text']}")
    if caption:
        st.caption(caption)
    st.divider()


def render_verses(con, refs) -> None:
    """Affiche une liste de versets (sura, aya) avec leurs traductions."""
    refs = list(dict.fromkeys(tuple(r) for r in refs))
    bundle = search.verses_bundle(con, refs)
    for sura, aya in refs:
        data = bundle.get((sura, aya), {})
        render_verse(sura, aya, data.get("text_uthmani", ""), data.get("translations", []))


def render_root_results(con, res, limit_note: str | None = None) -> None:
    """Résumé + occurrences d'une racine (un expander par verset, formes listées)."""
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

    refs = [(o["sura"], o["aya"]) for o in res["occurrences"]]
    for o in res["occurrences"]:
        if "context" in o:
            refs += [(c["sura"], c["aya"])
                     for c in o["context"]["before"] + o["context"]["after"]]
    bundle = search.verses_bundle(con, refs)

    by_verse: dict = {}
    for o in res["occurrences"]:
        by_verse.setdefault((o["sura"], o["aya"]), []).append(o)

    names = surah_names()
    for (sura, aya), occs in by_verse.items():
        nom = names.get(sura, "")
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
                    audio=False,
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
                    audio=False,
                )


# --------------------------------------------------------------------------
# Compteur d'occurrences partagé (bilingue : français ↔ arabe)
# --------------------------------------------------------------------------
def _summary_french(con, q: str) -> dict:
    """Mot français : passerelle vers racines + occurrences dans les traductions."""
    props = search.french_bridge(con, q)["proposals"]
    stats = search.roots_union_stats(con, [p["root_bw"] for p in props])
    fr_rows = search.search_french(con, q)
    return {
        "kind": "bridge",
        "props": props,
        "ar_rows": [],
        "fr_rows": fr_rows,
        "occurrences": stats["occurrences"],
        "verses": stats["verses"],
    }


def _summary_arabic(con, q: str) -> dict:
    """Mot arabe : racine exacte si possible, sinon occurrences textuelles."""
    resolved = search.resolve_root(con, q)
    if resolved is not None:
        st = search.root_stats(con, resolved["root_buckwalter"])
        if st:
            return {
                "kind": "root",
                "props": [
                    {
                        "fr": q,
                        "root_bw": st["root_bw"],
                        "root_ar": st["root_ar"],
                        "occurrences": st["occurrences"],
                        "verses": st["verses"],
                        "source": "racine (saisie directe)",
                    }
                ],
                "ar_rows": [],
                "fr_rows": [],
                "occurrences": st["occurrences"],
                "verses": st["verses"],
            }
    ar = search.arabic_occurrence_summary(con, q)
    return {
        "kind": "text",
        "props": [],
        "ar_rows": ar["rows"],
        "fr_rows": [],
        "occurrences": ar["occurrences"],
        "verses": ar["verses"],
    }


def occurrence_summary(con, query: str) -> dict | None:
    """Bilan d'une requête **bilingue** (mot français ou mot/racine arabe).

    Détecte la langue de la saisie puis renvoie un dict unifié contenant le
    nombre **total** d'occurrences et de versets (union des racines, sans double
    comptage), les propositions de la passerelle et les versets à afficher.
    """
    q = (query or "").strip()
    if not q:
        return None
    arabic = is_arabic(q)
    core = _summary_arabic(con, q) if arabic else _summary_french(con, q)
    core.update(
        {
            "query": q,
            "lang": "ar" if arabic else "fr",
            "roots": len(core["props"]),
            "fr_verses": len(core["fr_rows"]),
        }
    )
    return core


def counter_label(summary: dict) -> str:
    """Phrase du compteur : « N occurrence(s) trouvée(s) dans Y verset(s) »."""
    return (
        f"{summary['occurrences']} occurrence(s) trouvée(s) "
        f"dans {summary['verses']} verset(s)"
    )


def _render_rows(con, rows) -> None:
    """Affiche des versets (lignes brutes) avec leurs traductions."""
    if not rows:
        return
    refs = [(r["sura"], r["aya"]) for r in rows]
    bundle = search.verses_bundle(con, refs)
    for r in rows:
        data = bundle.get((r["sura"], r["aya"]), {})
        render_verse(
            r["sura"], r["aya"],
            data.get("text_uthmani", r.get("text_uthmani", "")),
            data.get("translations", []),
        )


# --------------------------------------------------------------------------
# Barre de recherche universelle (français **ou** arabe) — chaque onglet
# --------------------------------------------------------------------------
def universal_search(
    con,
    section_key: str,
    placeholder: str = "Rechercher en français ou en arabe (ex. miséricorde / رحمة)…",
    default_limit: int = 50,
) -> None:
    """Champ de recherche universel réutilisé par tous les modules.

    Accepte indifféremment un **mot français** (passerelle automatique vers les
    racines) ou un **mot / racine arabe** (recherche dans le texte). Affiche
    **systématiquement le nombre total d'occurrences**, puis les versets
    contextualisés dans la charte visuelle courante.
    """
    q = st.text_input(
        "Recherche universelle (français ou arabe)",
        key=f"uni_{section_key}",
        placeholder=placeholder,
        label_visibility="collapsed",
    )
    if not q:
        return

    with st.spinner("Recherche dans tout le Coran…"):
        summary = occurrence_summary(con, q)

    has_hits = summary and (
        summary["props"] or summary["ar_rows"] or summary["fr_rows"]
    )
    if not has_hits:
        st.warning(
            f"Aucune correspondance trouvée pour « {q} ». Essayez un autre mot "
            "(français ou arabe) ou une racine (ex. رحم ou rHm)."
        )
        return

    # --- Compteur d'occurrences : toujours affiché ------------------------
    if summary["kind"] == "text":
        st.success(
            f"**{counter_label(summary)}** pour « {summary['query']} » "
            f"(recherche textuelle arabe)."
        )
    elif summary["occurrences"]:
        st.success(
            f"**{counter_label(summary)}** — à partir de "
            f"{summary['roots']} racine(s) associée(s) à « {summary['query']} »."
        )
    else:
        st.info(
            f"Aucune racine associée automatiquement, mais « {summary['query']} » "
            f"apparaît dans {summary['fr_verses']} verset(s) (traductions)."
        )
    if summary["fr_verses"]:
        st.caption(
            f"« {summary['query']} » figure aussi dans les traductions de "
            f"{summary['fr_verses']} verset(s)."
        )

    # --- Correspondances (français → racines) -----------------------------
    if summary["props"]:
        with st.expander(
            f"Correspondances français → arabe ({len(summary['props'])})",
            expanded=(summary["kind"] == "bridge"),
        ):
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
                    for p in summary["props"]
                ]
            )

    # --- Versets contextualisés -------------------------------------------
    if summary["kind"] == "text":
        # Mot arabe : occurrences textuelles directes.
        _render_rows(con, summary["ar_rows"])
        if summary["verses"] > len(summary["ar_rows"]):
            st.caption(
                f"Limite atteinte : {len(summary['ar_rows'])} versets affichés "
                f"sur {summary['verses']}."
            )
    elif summary["props"]:
        # Racine (arabe directe) ou passerelle française : explorer une racine.
        pick = st.selectbox(
            "Racine à explorer",
            list(range(len(summary["props"]))),
            format_func=lambda i: (
                f"{summary['props'][i]['root_ar']} "
                f"[{summary['props'][i]['root_bw']}] — "
                f"{summary['props'][i]['verses']} versets"
            ),
            key=f"uni_pick_{section_key}",
        )
        limit = st.slider(
            "Occurrences à afficher",
            10, 500, default_limit,
            key=f"uni_limit_{section_key}",
        )
        res = search.search_root(con, summary["props"][pick]["root_bw"], limit=limit)
        note = None
        if res.get("found") and res["count"] >= limit:
            note = (
                f"Premières {res['count']} occurrences "
                f"(limite réglée à {limit})."
            )
        render_root_results(con, res, limit_note=note)

    # --- Occurrences dans les traductions françaises -----------------------
    if summary["fr_rows"]:
        with st.expander(
            f"Versets où « {summary['query']} » figure dans les traductions "
            f"({summary['fr_verses']})"
        ):
            _render_rows(con, summary["fr_rows"])

    st.divider()


# --------------------------------------------------------------------------
# Sélecteur de verset (sourate + verset) — réutilisé par « Verset comparé »
# --------------------------------------------------------------------------
def verse_picker(
    con,
    key: str,
    default_sura: int = 2,
    default_aya: int = 255,
) -> tuple[int, int]:
    """Sélecteur indépendant (sourate + numéro de verset) → (sura, aya)."""
    names = surah_names()
    surahs = sorted(names) or list(range(1, 115))
    col_s, col_a = st.columns([3, 2])
    sura = col_s.selectbox(
        "Sourate",
        surahs,
        index=surahs.index(default_sura) if default_sura in surahs else 0,
        format_func=lambda n: f"{n}. {names.get(n, '')}",
        key=f"vp_sura_{key}",
    )
    max_aya = con.execute(
        "SELECT MAX(aya) FROM verses WHERE sura = ?", (sura,)
    ).fetchone()[0] or 1
    default = default_aya if sura == default_sura else 1
    default = min(int(default), int(max_aya))
    aya = col_a.number_input(
        "Verset",
        1,
        int(max_aya),
        default,
        key=f"vp_aya_{key}",
    )
    return int(sura), int(aya)

