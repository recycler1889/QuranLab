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
    reciters = [r for r in (getattr(config, "RECITERS", None) or [])
                if isinstance(r, dict) and r.get("key")]
    if not reciters:
        reciters = [{"key": "alafasy", "label": "Mishary Rachid Alafasy",
                     "edition": "Alafasy_128kbps"}]
    key = st.session_state.get("reciter")
    for r in reciters:
        if r.get("key") == key:
            return r
    return reciters[0]


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


_TTS_VOICE_JS = r"""
var VOICES = window.speechSynthesis ? (window.speechSynthesis.getVoices() || []) : [];
if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = function() {
    VOICES = window.speechSynthesis.getVoices() || VOICES;
  };
}
function qlFr(v) {
  if (!v) { return false; }
  var l = (v.lang || '').replace(/_/g, '-').toLowerCase();
  return l.indexOf('fr') === 0 ||
    (v.name || '').toLowerCase().indexOf('fran') >= 0 ||
    (v.name || '').toLowerCase().indexOf('french') >= 0;
}
function qlPick() {
  var chosen = null;
  try { chosen = window.localStorage.getItem('ql_tts_voice') || null; }
  catch (e) { chosen = null; }
  if (chosen) {
    var m = VOICES.filter(function(v) { return v.name === chosen; });
    if (m.length) { return m[0]; }
  }
  var fr = VOICES.filter(qlFr);
  if (!fr.length) { return null; }
  var PREF = ['google franc', 'microso', 'hortense', 'julie', 'denise',
    'aurore', 'pauline', 'amelie', 'am', 'virginie', 'audrey', 'samantha'];
  for (var j = 0; j < PREF.length; j++) {
    var h = fr.filter(function(v) {
      return (v.name || '').toLowerCase().indexOf(PREF[j]) >= 0;
    });
    if (h.length) { return h[0]; }
  }
  var exact = fr.filter(function(v) {
    return (v.lang || '').replace(/_/g, '-').toLowerCase() === 'fr-fr';
  });
  if (exact.length) { return exact[0]; }
  return fr[0];
}
"""


def tts(text: str, language: str = "fr") -> None:
    """Bouton de synthèse vocale (Web Speech API du navigateur) d'un texte.

    La voix suit la langue de la traduction (``fr`` → fr-FR, ``en`` → en-US).
    Composant autonome : chaque traduction dispose de son propre lecteur, qui
    bascule entre « Lire » et « Stop ». Aucune clé/API externe n'est requise ;
    le moteur TTS est celui du navigateur.
    """
    pal = _palette()
    locale = config.tts_locale(language)
    rate = float(st.session_state.get("tts_rate", 1.0))
    pitch = float(st.session_state.get("tts_pitch", 1.0))
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
        var RATE={rate!r};var PITCH={pitch!r};
        {_TTS_VOICE_JS}
        var b=document.getElementById('b'),t={payload};
        var IDLE='\u25B6 Lire';
        b.addEventListener('click',function(){{
          if(!('speechSynthesis' in window)){{
            b.textContent='TTS indisponible';return;}}
          if(b.dataset.on==='1'){{
            speechSynthesis.cancel();b.dataset.on='0';b.textContent=IDLE;return;}}
          var u=new SpeechSynthesisUtterance(t);
          var v=null;try{{v=qlPick();}}catch(e){{}}
          if(v){{u.voice=v;u.lang=v.lang||{locale!r};}}else{{u.lang={locale!r};}}
          u.rate=RATE;u.pitch=PITCH;u.volume=1;
          var done=function(){{b.dataset.on='0';b.textContent=IDLE;}};
          u.onend=done;u.onerror=done;
          speechSynthesis.cancel();
          try{{speechSynthesis.resume();}}catch(e){{}}
          speechSynthesis.speak(u);
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
    """Lecteur unique par verset : **deux actions, jamais de doublon**.

    - une **récitation** du verset par le récitateur choisi ;
    - un **unique** bouton de synthèse vocale **en français** (voix ``fr-FR``
      du navigateur), qui lit la première traduction française disponible.

    Tout est regroupé dans un seul iframe ``st.iframe`` (non sandboxé : la Web
    Speech API s'y active normalement).
    """
    show_audio = st.session_state.get("show_quran_audio", True)
    show_tts = st.session_state.get("show_tts", True)

    fr_text = ""
    if show_tts:
        fr_text = (
            next(
                (t["text"] for t in translations
                 if t.get("language") == "fr" and t.get("text")),
                None,
            )
            or next(
                (t["text"] for t in translations if t.get("text")),
                None,
            )
            or ""
        )

    if not show_audio and not fr_text:
        return

    pal = _palette()
    reciter = reciter or active_reciter()
    rate = float(st.session_state.get("tts_rate", 1.0))
    pitch = float(st.session_state.get("tts_pitch", 1.0))

    rows = []
    listeners = ""

    if show_audio:
        url = config.audio_url(reciter["edition"], sura, aya)
        title = html.escape(f"{reciter['label']} · {sura}:{aya}")
        rows.append(
            '<div class="row">'
            '<button id="pp" title="Lecture / Pause">▶ Écouter</button>'
            '<button id="st" title="Arrêter">■</button>'
            f'<span class="meta">{title}</span>'
            f'<audio id="au" preload="none" src="{url}"></audio>'
            "</div>"
        )
        listeners += """
        var au=document.getElementById('au');
        document.getElementById('pp').addEventListener('click',function(){
          if(au.paused){au.play();this.textContent='\u275A\u275A Pause';}
          else{au.pause();this.textContent='\u25B6 \u00C9couter';}
        });
        document.getElementById('st').addEventListener('click',function(){
          au.pause();au.currentTime=0;
          document.getElementById('pp').textContent='\u25B6 \u00C9couter';});
        au.addEventListener('ended',function(){
          document.getElementById('pp').textContent='\u25B6 \u00C9couter';});
        """

    if fr_text:
        payload = json.dumps(fr_text, ensure_ascii=False).replace("<", "\\u003c")
        rows.append(
            '<div class="row">'
            '<button id="speak" title="Synthèse vocale française (fr-FR)">'
            "▶ Écouter en français</button></div>"
        )
        listeners += f"""
        var RATE={rate!r};var PITCH={pitch!r};
        {_TTS_VOICE_JS}
        var b=document.getElementById('speak');
        var IDLE='\u25B6 \u00C9couter en fran\u00E7ais';
        b.addEventListener('click',function(){{
          if(!('speechSynthesis' in window)){{
            b.textContent='TTS indisponible';return;}}
          if(b.dataset.on==='1'){{
            speechSynthesis.cancel();b.dataset.on='0';b.textContent=IDLE;return;}}
          var u=new SpeechSynthesisUtterance({payload});
          var v=null;try{{v=qlPick();}}catch(e){{}}
          if(v){{u.voice=v;u.lang=v.lang||'fr-FR';}}else{{u.lang='fr-FR';}}
          u.rate=RATE;u.pitch=PITCH;u.volume=1;
          var done=function(){{
            b.dataset.on='0';b.textContent=IDLE;}};
          u.onend=done;u.onerror=done;
          speechSynthesis.cancel();
          try{{speechSynthesis.resume();}}catch(e){{}}
          speechSynthesis.speak(u);
          b.dataset.on='1';b.textContent='\u25A0 Arr\u00EAter';
        }});
        """

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
      .meta{{font-size:11px;color:{pal['fg2']};white-space:nowrap;
        overflow:hidden;text-overflow:ellipsis;max-width:180px;}}
    </style></head><body>
      {''.join(rows)}
      <script>
        {listeners}
      </script>
    </body></html>"""
    st.iframe(comp, height=34 + len(rows) * 27)


def tts_settings() -> None:
    """Réglages accessibles de la synthèse vocale (sidebar).

    - **Débit / hauteur** : injectés dans chaque lecteur des versets ;
    - **choix de la voix** : le sélecteur est rempli par le navigateur
      lui-même (fini la « voix anglophone » qui épeille les lettres) ; le
      choix est mémorisé dans ``localStorage``, partagé par les iframes
      ``srcdoc`` non sandboxés du même onglet.
    """
    with st.expander("Paramètres de la synthèse vocale"):
        st.slider(
            "Débit", 0.5, 1.5, 1.0, 0.05, key="tts_rate",
            help="Vitesse de lecture : 1.0 = normale.",
        )
        st.slider(
            "Hauteur (ton)", 0.5, 2.0, 1.0, 0.05, key="tts_pitch",
            help="Gravité de la voix : 1.0 = normale.",
        )
        st.caption(
            "Si la lecture épeille les lettres, sélectionnez une voix "
            "francophone ci-dessous puis cliquez *Appliquer*."
        )
        _voice_picker()


def _voice_picker() -> None:
    """Sélecteur de voix rempli par le navigateur, persistant par localStorage."""
    pal = _palette()
    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      label{{display:block;font-size:11px;color:{pal['fg2']};margin:2px 0;}}
      select{{width:100%;height:26px;font-size:12px;color:{pal['fg']};
        background:{pal['field']};border:1px solid {pal['border']};
        border-radius:6px;padding:0 4px;margin-bottom:4px;}}
      button{{cursor:pointer;height:24px;padding:0 9px;font-size:11.5px;
        border:1px solid {pal['border']};border-radius:999px;
        background:{pal['field']};color:{pal['fg']};margin:1px 2px 1px 0;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
      #info{{font-size:11px;color:{pal['fg2']};margin-top:3px;line-height:1.35;}}
    </style></head><body>
      <label for="vl">Voix de synthèse (francophone de préférence)</label>
      <select id="vl"></select>
      <div>
        <button id="ap">Appliquer</button>
        <button id="au">Auto</button>
      </div>
      <div id="info">Chargement des voix…</div>
      <script>
        var sel=document.getElementById('vl'),info=document.getElementById('info');
        var ALL=[];
        function read(){{try{{return window.localStorage.getItem('ql_tts_voice')||'';}}
          catch(e){{return '';}}}}
        function write(n){{try{{window.localStorage.setItem('ql_tts_voice',n);}}
          catch(e){{}}}}
        function fr(v){{var l=(v.lang||'').replace(/_/g,'-').toLowerCase();
          return l.indexOf('fr')===0||
            (v.name||'').toLowerCase().indexOf('fran')>=0||
            (v.name||'').toLowerCase().indexOf('french')>=0;}}
        function render(){{
          var curv=read();
          sel.innerHTML='';
          var auto=document.createElement('option');
          auto.value='';auto.textContent='Auto (meilleure voix française)';
          sel.appendChild(auto);
          var frs=ALL.filter(fr).sort(function(a,b){{return (a.name||'')<(b.name||'')?-1:1;}});
          var rest=ALL.filter(function(v){{return !fr(v);}})
            .sort(function(a,b){{return (a.name||'')<(b.name||'')?-1:1;}});
          frs.forEach(function(v){{var o=document.createElement('option');
            o.value=v.name;o.textContent=v.name+' \u2014 '+(v.lang||'');sel.appendChild(o);}});
          if(rest.length){{var g=document.createElement('optgroup');
            g.label='Autres voix';rest.forEach(function(v){{
              var o=document.createElement('option');
              o.value=v.name;o.textContent=v.name+' \u2014 '+(v.lang||'');g.appendChild(o);}});
            sel.appendChild(g);}}
          if(curv){{try{{sel.value=curv;}}catch(e){{}}}}
          var selName=curv&&frs.some(function(v){{return v.name===curv;}})
            ?curv:(curv?'(introuvable)':'Auto');
          info.textContent=frs.length+' voix francophone(s) d\u00E9tect\u00E9e(s)'
            +(curv?' \u2014 s\u00E9lectionn\u00E9e : '+selName:'')
            +'. Puis \u00AB \u00C9couter en fran\u00E7ais \u00BB dans un verset.';
        }}
        function load(){{
          if(!('speechSynthesis' in window)){{
            info.textContent='Synth\u00E8se vocale indisponible dans ce navigateur.';return;}}
          ALL=window.speechSynthesis.getVoices()||[];
          if(!ALL.length){{setTimeout(load,250);return;}}
          render();
        }}
        if(window.speechSynthesis&&window.speechSynthesis.onvoiceschanged!==undefined){{
          window.speechSynthesis.onvoiceschanged=load;}}
        load();
        document.getElementById('ap').addEventListener('click',function(){{
          write(sel.value);render();}});
        document.getElementById('au').addEventListener('click',function(){{
          write('');render();}});
      </script>
    </body></html>"""
    st.iframe(comp, height=172)


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
    **unique** bouton **de synthèse vocale en français** (voix ``fr-FR``)
    sont ajoutés, regroupés en un seul composant. ``audio=False`` permet de
    désactiver la récitation (ex. versets de contexte).
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

