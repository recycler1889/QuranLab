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
from urllib.parse import quote

import streamlit as st

from . import bookmarks, config, db, i18n, search
from . import theme as theme_mod
from .buckwalter import is_arabic

t = i18n.t

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


def _lang_name(code: str | None = None) -> str:
    """Nom localisé de la langue d'interface (ou ``code`` si fourni)."""
    return t("ui.lang." + (code or i18n.lang()))


def translations_for_lang(translations: list) -> list:
    """Traductions de la langue d'interface active (repli : toutes).

    Garantit qu'un verset affiché ne mélange **jamais** les langues : seul le
    jeu de traductions de la langue choisie est retenu. Si aucune ne correspond
    (données incomplètes), on renvoie la liste complète pour ne rien perdre.
    """
    lg = i18n.lang()
    picked = [
        tr for tr in (translations or [])
        if str(tr.get("language", "")).lower() == lg
    ]
    return picked or list(translations or [])


# --------------------------------------------------------------------------
# Rendu de base
# --------------------------------------------------------------------------
def page_header(title: str, subtitle: str) -> None:
    """Bandeau de titre orné (cadre géométrique + nappe calligraphique arabe).

    Habille l'en-tête sans recourir à st.title/st.caption, afin de bénéficier
    de la charte décorative (variables CSS --ql-*, classes .ql-banner). Le
    décor est purement SVG/CSS embarqué (data-URI) — aucun fichier réseau,
    aucun surcoût de performance.
    """
    st.markdown(
        "<div class='ql-banner'>"
        "<span class='ql-corner ql-c-tl'></span>"
        "<span class='ql-corner ql-c-tr'></span>"
        "<span class='ql-corner ql-c-br'></span>"
        "<span class='ql-corner ql-c-bl'></span>"
        "<div class='ql-inset'></div>"
        "<p class='ql-ar' lang='ar' dir='rtl'>القرآن الكريم</p>"
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
    play = json.dumps(t("ui.listen"), ensure_ascii=False)
    pause = json.dumps(t("ui.pause"), ensure_ascii=False)
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
        <button id="pp" title="{html.escape(t('ui.listen_title'))}">&#9654; {t("ui.listen")}</button>
        <button id="st" title="{html.escape(t('ui.stop_title'))}">&#9632;</button>
        <span class="meta">{title}</span>
        <audio id="au" preload="none" src="{url}"></audio>
      </div>
      <script>
        var au=document.getElementById('au'),pp=document.getElementById('pp');
        var PLAY='\u25B6 ' + {play}, PAUSE='\u275A\u275A ' + {pause};
        pp.addEventListener('click',function(){{
          if(au.paused){{au.play();pp.textContent=PAUSE;}}
          else{{au.pause();pp.textContent=PLAY;}}
        }});
        document.getElementById('st').addEventListener('click',function(){{
          au.pause();au.currentTime=0;pp.textContent=PLAY;
        }});
        au.addEventListener('ended',function(){{
          pp.textContent=PLAY;}});
      </script>
    </body></html>"""
    st.iframe(comp, height=36)


# Gabarit du sélecteur de voix : les marqueurs __*__ sont remplacés par
# ``_tts_voice_js`` selon la langue (fr-FR / en-US), la liste des préférences de
# voix et la clé localStorage propre à la langue.
#
# Deux listes distinctes :
#   * SUBS : marqueurs d'APPARTENANCE à la langue (pour filtrer les voix du
#     navigateur). On n'y met QUE des indices linguistiques — jamais un nom de
#     marque (« google », « microsoft »), sinon les voix anglaises seraient
#     considérées comme françaises.
#   * PREFS : indices de QUALITÉ/préférence (classement des voix déjà filtrées).
#     Les voix « Natural / Neural / Online » (Microsoft Edge, gratuites et très
#     naturelles) sont classées en tête, puis Google (Chrome), puis les voix
#     locales du système.
_LG_MATCH = {"fr": "fr", "en": "en"}
_LG_SUBS = {
    "fr": ("fran", "french", "français", "francais"),
    "en": ("english", "eng"),
}
_LG_PREFS = {
    "fr": [
        "natural", "neural", "online", "google franc", "google français",
        "microsoft denise", "microsoft henri", "microsoft vivienne",
        "microsoft hortense", "microsoft julie", "microsoft pauline",
        "hortense", "julie", "pauline", "denise", "vivienne",
        "amelie", "amélie", "thomas", "google", "microsoft",
    ],
    "en": [
        "natural", "neural", "online", "google us", "google uk",
        "microsoft aria", "microsoft jenny", "microsoft guy",
        "samantha", "zira", "david", "mark", "google", "microsoft",
    ],
}

_TTS_VOICE_JS = r"""
var VOICES = window.speechSynthesis ? (window.speechSynthesis.getVoices() || []) : [];
if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = function() {
    VOICES = window.speechSynthesis.getVoices() || VOICES;
  };
}
/* Appartenance à la langue : par la locale (fr-FR, fr-CA, fr-BE, fr-CH…) ou par
   un indice linguistique du nom (French, français…). */
function qlMatch(v) {
  if (!v) { return false; }
  var l = (v.lang || '').replace(/_/g, '-').toLowerCase();
  if (l.indexOf(__LG__) === 0) { return true; }
  var n = (v.name || '').toLowerCase(), SUB = __SUBS__;
  for (var i = 0; i < SUB.length; i++) {
    if (n.indexOf(SUB[i]) >= 0) { return true; }
  }
  return false;
}
/* Score de QUALITÉ : favorise les voix neuronales/en ligne (naturelles) et
   pénalise les anciennes voix « Desktop/Compact » du système (souvent
   saccadées). */
function qlQuality(v) {
  var n = (v.name || '').toLowerCase(), q = 0;
  if (v.localService === false) { q += 35; }
  if (n.indexOf('natural') >= 0) { q += 60; }
  if (n.indexOf('neural') >= 0) { q += 55; }
  if (n.indexOf('online') >= 0) { q += 30; }
  if (n.indexOf('premium') >= 0) { q += 25; }
  if (n.indexOf('enhanced') >= 0) { q += 25; }
  if (n.indexOf('google') >= 0) { q += 30; }
  if (n.indexOf('desktop') >= 0) { q -= 20; }
  if (n.indexOf('compact') >= 0) { q -= 20; }
  return q;
}
/* Rang de préférence : plus petit = préféré (index dans la liste PREFS). */
function qlPrefRank(v) {
  var n = (v.name || '').toLowerCase(), PREF = __PREFS__;
  for (var i = 0; i < PREF.length; i++) {
    if (n.indexOf(PREF[i]) >= 0) { return i; }
  }
  return PREF.length;
}
/* Choix automatique : 1) voix mémorisée, 2) meilleur couple
   (préférence, qualité) parmi les voix de la bonne langue. */
function qlPick() {
  var chosen = null;
  try { chosen = window.localStorage.getItem(__LS_KEY__) || null; }
  catch (e) { chosen = null; }
  if (chosen) {
    var m = VOICES.filter(function(v) { return v.name === chosen; });
    if (m.length) { return m[0]; }
  }
  var match = VOICES.filter(qlMatch);
  if (!match.length) { return null; }
  var best = null, bestRank = 1e9, bestQ = -1e9;
  for (var i = 0; i < match.length; i++) {
    var r = qlPrefRank(match[i]), q = qlQuality(match[i]);
    if (r < bestRank || (r === bestRank && q > bestQ)) {
      best = match[i]; bestRank = r; bestQ = q;
    }
  }
  return best;
}
function qlNorm(s) { return (s || '').replace(/_/g, '-'); }
function qlSpeak(text, voiceName, langTag, rate, pitch) {
  if (window.speechSynthesis && (!VOICES || !VOICES.length)) {
    try { VOICES = window.speechSynthesis.getVoices() || VOICES; } catch (e) {}
  }
  var u = new SpeechSynthesisUtterance(text);
  var v = null;
  if (voiceName) {
    v = VOICES.filter(function(x) { return x.name === voiceName; })[0] || null;
  }
  if (!v) { v = qlPick(); }
  if (v) { u.voice = v; u.lang = qlNorm(v.lang) || qlNorm(langTag); }
  else { u.lang = qlNorm(langTag); }
  u.rate = rate || 1; u.pitch = pitch || 1; u.volume = 1;
  try { speechSynthesis.cancel(); } catch (e) {}
  setTimeout(function() {
    try { speechSynthesis.resume(); } catch (e) {}
    try { speechSynthesis.speak(u); } catch (e) {}
  }, 80);
  return u;
}
"""



def _tts_voice_js(lg: str) -> str:
    """Gabarit JS de choix de voix paramétré pour la langue ``lg``."""
    tag = _LG_MATCH.get(lg, _LG_MATCH["fr"])
    subs = json.dumps(list(_LG_SUBS.get(lg, _LG_SUBS["fr"])), ensure_ascii=False)
    prefs = json.dumps(list(_LG_PREFS.get(lg, _LG_PREFS["fr"])), ensure_ascii=False)
    return (
        _TTS_VOICE_JS
        .replace("__LG__", json.dumps(tag))
        .replace("__SUBS__", subs)
        .replace("__PREFS__", prefs)
        .replace("__LS_KEY__", json.dumps(f"ql_tts_voice_{tag}"))
    )


def _tts_external_url(text: str, locale: str) -> str:
    """URL audio d'un fournisseur TTS externe (vide si non configuré).

    Le gabarit ``config.TTS_HTTP_URL`` contient ``{text}`` et ``{lang}``,
    remplacés par le texte et la locale encodés. Renvoie "" si aucun
    fournisseur n'est configuré (repli : Web Speech API du navigateur).
    """
    tpl = (getattr(config, "TTS_HTTP_URL", "") or "").strip()
    if not tpl:
        return ""
    return tpl.replace("{text}", quote(text or "", safe="")).replace(
        "{lang}", quote(locale or "", safe="")
    )


def tts(text: str, language: str = "fr") -> None:
    """Bouton de synthèse vocale d'un texte.

    Deux fonctionnements, selon la configuration :

    * **Voix du navigateur** (défaut) : Web Speech API — voix « Natural » de
      Microsoft Edge, voix Google de Chrome ou voix système. Un moteur de choix
      privilégie les voix françaises neuronales/en ligne et évite l'épellation
      lettre à lettre.
    * **Fournisseur externe** (si ``config.TTS_HTTP_URL`` est renseigné) : le
      texte est lu depuis le flux audio du service configuré (aucune voix
      locale requise).

    Les libellés suivent la langue d'**interface** active ; la langue lue suit
    ``language``. Composant autonome (bascule lire/arrêter).
    """
    pal = _palette()
    locale = config.tts_locale(language)
    rate = float(st.session_state.get("tts_rate", 1.0))
    pitch = float(st.session_state.get("tts_pitch", 1.0))
    # json.dumps → littéral JS sûr ; « < » échappé pour ne pas clore </script>.
    payload = json.dumps(text or "", ensure_ascii=False).replace("<", "\\u003c")
    play = json.dumps(t("ui.play"), ensure_ascii=False)
    stop = json.dumps(t("ui.stop"), ensure_ascii=False)
    unavail = json.dumps(t("ui.tts_unavail"), ensure_ascii=False)
    title = html.escape(t("ui.tts_title", locale=locale))

    external = _tts_external_url(text or "", locale)
    if external:
        button_js = f"""
        var au=document.getElementById('ext');var PLAY='\\u25B6 ' + {play};
        var STOP='\\u25A0 ' + {stop};
        if(au){{
          if(b.dataset.on==='1'){{au.pause();au.currentTime=0;
            b.dataset.on='0';b.textContent=PLAY;return;}}
          au.play();b.dataset.on='1';b.textContent=STOP;
          au.onended=function(){{b.dataset.on='0';b.textContent=PLAY;}};
        }} else {{ b.textContent={unavail}; }}
        """
        audio_tag = f'<audio id="ext" preload="none" src="{html.escape(external)}"></audio>'
    else:
        button_js = f"""
        if(!('speechSynthesis' in window)){{ b.textContent={unavail};return; }}
        if(b.dataset.on==='1'){{
          speechSynthesis.cancel();b.dataset.on='0';b.textContent=IDLE;return;}}
        var u=qlSpeak({payload},'',{locale!r},RATE,PITCH);
        var done=function(){{b.dataset.on='0';b.textContent=IDLE;}};
        u.onend=done;u.onerror=done;
        b.dataset.on='1';b.textContent='\\u25A0 ' + {stop};
        """
        audio_tag = ""
    voice_js = "" if external else _tts_voice_js(language)
    idle_js = "" if external else f"var IDLE='\\u25B6 ' + {play};"

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
      <button id="b" title="{title}">
        &#9654; {t("ui.play")}</button>
      {audio_tag}
      <script>
        var RATE={rate!r};var PITCH={pitch!r};
        {voice_js}
        var b=document.getElementById('b'),t={payload};
        {idle_js}
        b.addEventListener('click',function(){{
          {button_js}
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
    - un **unique** bouton de synthèse vocale dans la langue d'interface active
      (voix ``fr-FR`` ou ``en-US`` du navigateur), qui lit la première
      traduction disponible dans cette langue.

    Tout est regroupé dans un seul iframe ``st.iframe`` (non sandboxé : la Web
    Speech API s'y active normalement). Aucun mélange de langues : les
    traductions lues suivent la langue choisie.
    """
    show_audio = st.session_state.get("show_quran_audio", True)
    show_tts = st.session_state.get("show_tts", True)

    lg = i18n.lang()
    locale = i18n.ui_locale()
    active_trans = translations_for_lang(translations)

    tts_text = ""
    if show_tts:
        tts_text = next(
            (tr["text"] for tr in active_trans if tr.get("text")), ""
        )

    if not show_audio and not tts_text:
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
            f'<button id="pp" title="{html.escape(t("ui.listen_title"))}">'
            f'\u25B6 {t("ui.listen")}</button>'
            f'<button id="st" title="{html.escape(t("ui.stop_title"))}">\u25A0</button>'
            f'<span class="meta">{title}</span>'
            f'<audio id="au" preload="none" src="{url}"></audio>'
            "</div>"
        )
        listeners += """
        var au=document.getElementById('au');
        var PLAY='\u25B6 ' + %s, PAUSE='\u275A\u275A ' + %s;
        document.getElementById('pp').addEventListener('click',function(){
          if(au.paused){au.play();this.textContent=PAUSE;}
          else{au.pause();this.textContent=PLAY;}
        });
        document.getElementById('st').addEventListener('click',function(){
          au.pause();au.currentTime=0;
          document.getElementById('pp').textContent=PLAY;});
        au.addEventListener('ended',function(){
          document.getElementById('pp').textContent=PLAY;});
        """ % (
            json.dumps(t("ui.listen"), ensure_ascii=False),
            json.dumps(t("ui.pause"), ensure_ascii=False),
        )

    if tts_text:
        tts_button = t("ui.tts_button")
        external = _tts_external_url(tts_text, locale)
        if external:
            rows.append(
                '<div class="row">'
                f'<button id="speak" title="{html.escape(t("ui.speak_tooltip", locale=locale))}">'
                f'\u25B6 {tts_button}</button>'
                f'<audio id="exttts" preload="none" src="{html.escape(external)}"></audio>'
                "</div>"
            )
            listeners += f"""
            var ext=document.getElementById('exttts');
            var b=document.getElementById('speak');
            var TIDLE='\u25B6 ' + {json.dumps(tts_button, ensure_ascii=False)};
            var TSTOP='\u25A0 ' + {json.dumps(t("ui.stop"), ensure_ascii=False)};
            b.addEventListener('click',function(){{
              if(b.dataset.on==='1'){{
                ext.pause();ext.currentTime=0;b.dataset.on='0';
                b.textContent=TIDLE;return;}}
              ext.play();b.dataset.on='1';b.textContent=TSTOP;
              ext.onended=function(){{b.dataset.on='0';b.textContent=TIDLE;}};
            }});
            """
        else:
            payload = json.dumps(tts_text, ensure_ascii=False).replace("<", "\\u003c")
            rows.append(
                '<div class="row">'
                f'<button id="speak" title="{html.escape(t("ui.speak_tooltip", locale=locale))}">'
                f'\u25B6 {tts_button}</button></div>'
            )
            listeners += f"""
            var RATE={rate!r};var PITCH={pitch!r};
            {_tts_voice_js(lg)}
            var b=document.getElementById('speak');
            var IDLE='\u25B6 ' + {json.dumps(tts_button, ensure_ascii=False)};
            b.addEventListener('click',function(){{
              if(!('speechSynthesis' in window)){{
                b.textContent={json.dumps(t("ui.tts_unavail"), ensure_ascii=False)};return;}}
              if(b.dataset.on==='1'){{
                speechSynthesis.cancel();b.dataset.on='0';b.textContent=IDLE;return;}}
              var u=qlSpeak({payload},'',{locale!r},RATE,PITCH);
              var done=function(){{
                b.dataset.on='0';b.textContent=IDLE;}};
              u.onend=done;u.onerror=done;
              b.dataset.on='1';b.textContent='\u25A0 ' + {json.dumps(t("ui.stop"), ensure_ascii=False)};
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
      choix est mémorisé dans ``localStorage`` (une clé par langue), partagé
      par les iframes ``srcdoc`` non sandboxés du même onglet.
    """
    with st.expander(t("ui.tts_settings")):
        st.slider(
            t("ui.rate"), 0.5, 1.5, 1.0, 0.05, key="tts_rate",
            help=t("ui.rate_help"),
        )
        st.slider(
            t("ui.pitch"), 0.5, 2.0, 1.0, 0.05, key="tts_pitch",
            help=t("ui.pitch_help"),
        )
        if _tts_external_url("test", i18n.ui_locale()):
            st.caption(t("ui.tts_external_on"))
        else:
            st.caption(t("ui.voice_hint", lang=_lang_name()))
            _voice_picker()
            st.caption(t("ui.voice_tip"))


def _voice_picker() -> None:
    """Sélecteur de voix rempli par le navigateur, persistant par localStorage.

    Liste **plusieurs voix** de la langue active (les candidates en premier,
    les autres à part) et propose un bouton **Tester** pour écouter chaque voix
    sur un court échantillon avant de la retenir — utile quand une voix lit
    lettre à lettre. La clé de stockage et les voix préférées suivent la langue
    d'interface (``ql_tts_voice_fr`` / ``ql_tts_voice_en``) : aucun mélange.
    """
    pal = _palette()
    lg = i18n.lang()
    lname = _lang_name(lg)
    ls_key = f"ql_tts_voice_{lg}"
    locale = i18n.ui_locale()
    sample = t("ui.sample_fr") if lg == "fr" else t("ui.sample_en")
    rate = float(st.session_state.get("tts_rate", 1.0))
    pitch = float(st.session_state.get("tts_pitch", 1.0))
    label = t("ui.vl_label", lang=lname)
    auto_opt = json.dumps(t("ui.auto_opt", lang=lname), ensure_ascii=False)
    other = json.dumps(t("ui.other_voices"), ensure_ascii=False)
    loading = json.dumps(t("ui.loading_voices"), ensure_ascii=False)
    no_tts = json.dumps(t("ui.no_tts"), ensure_ascii=False)
    found_tpl = json.dumps(t("ui.voices_found", n="{n}", lang=lname), ensure_ascii=False)
    selected = json.dumps(t("ui.voice_selected", name="{name}"), ensure_ascii=False)
    unavailable = json.dumps(t("ui.unavailable"), ensure_ascii=False)
    then = json.dumps(
        t("ui.then_listen", label=t("ui.tts_button")), ensure_ascii=False
    )
    voice_none = json.dumps(t("ui.voice_none", lang=lname), ensure_ascii=False)
    voice_few = json.dumps(t("ui.voice_few", lang=lname), ensure_ascii=False)
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
      #test{{border-style:dashed;}}
      #info{{font-size:11px;color:{pal['fg2']};margin-top:3px;line-height:1.35;
        white-space:pre-line;}}
    </style></head><body>
      <label for="vl">{html.escape(label)}</label>
      <select id="vl"></select>
      <div>
        <button id="ap">{t("ui.apply")}</button>
        <button id="au">{t("ui.auto")}</button>
        <button id="test">&#9654; {t("ui.test_voice")}</button>
      </div>
      <div id="info">{t("ui.loading_voices")}</div>
      <script>
        var RATE={rate!r},PITCH={pitch!r};
        {_tts_voice_js(lg)}
        var sel=document.getElementById('vl'),info=document.getElementById('info');
        var LS_KEY={json.dumps(ls_key)};
        var SAMPLE={json.dumps(sample, ensure_ascii=False)};
        var LOCALE={locale!r};
        var ALL=[];
        function read(){{try{{return window.localStorage.getItem(LS_KEY)||'';}}
          catch(e){{return '';}}}}
        function write(n){{try{{window.localStorage.setItem(LS_KEY,n);}}
          catch(e){{}}}}
        function matchLang(v){{var l=(v.lang||'').replace(/_/g,'-').toLowerCase();
          return l.indexOf({json.dumps(_LG_MATCH.get(lg, 'fr'))})===0||
            ({json.dumps(list(_LG_SUBS.get(lg, _LG_SUBS['fr'])))}).some(function(s){{
              return (v.name||'').toLowerCase().indexOf(s)>=0;}});}}
        var FOUND={found_tpl}, SEL={selected}, UNAV={unavailable},
          THEN={then}, NO_TTS={no_tts}, AUTO={auto_opt},
          OTHERS={other}, VNONE={voice_none}, VFEW={voice_few};
        function setInfo(n,selName){{
          if(n===0){{info.textContent=VNONE;return;}}
          var s=FOUND.replace('{{n}}',String(n))+(selName?
            SEL.replace('{{name}}',selName):'')+THEN;
          if(n<=1){{s=s+'\\n'+VFEW;}}
          info.textContent=s;}}
        function render(){{
          var curv=read();
          sel.innerHTML='';
          var auto=document.createElement('option');
          auto.value='';auto.textContent=AUTO;
          sel.appendChild(auto);
          var ls=ALL.filter(matchLang)
            .sort(function(a,b){{return (a.name||'')<(b.name||'')?-1:1;}});
          var rest=ALL.filter(function(v){{return !matchLang(v);}})
            .sort(function(a,b){{return (a.name||'')<(b.name||'')?-1:1;}});
          ls.forEach(function(v){{var o=document.createElement('option');
            o.value=v.name;o.textContent=v.name+' \u2014 '+(v.lang||'');sel.appendChild(o);}});
          if(rest.length){{var g=document.createElement('optgroup');
            g.label=OTHERS;rest.forEach(function(v){{
              var o=document.createElement('option');
              o.value=v.name;o.textContent=v.name+' \u2014 '+(v.lang||'');g.appendChild(o);}});
            sel.appendChild(g);}}
          if(curv){{try{{sel.value=curv;}}catch(e){{}}}}
          var selName=(curv&&ls.some(function(v){{return v.name===curv;}}))
            ?curv:(curv?UNAV:'');
          setInfo(ls.length,selName);
        }}
        function load(){{
          if(!('speechSynthesis' in window)){{
            info.textContent=NO_TTS;return;}}
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
        document.getElementById('test').addEventListener('click',function(){{
          try{{ qlSpeak(SAMPLE,sel.value,LOCALE,RATE,PITCH); }}catch(e){{}}}});
      </script>
    </body></html>"""
    st.iframe(comp, height=196)


def continuous_player(verses: list, reciter: dict | None = None) -> None:
    """Lecteur de **récitation en continu** : enchaîne les versets fournis.

    ``verses`` : liste de dicts ``{"sura": int, "aya": int}`` dans l'ordre de
    lecture. Un seul élément audio enchaîne les fichiers MP3 du récitateur
    choisi (everyayah) ; un bandeau indique le verset en cours. Les boutons
    Lecture / Arrêt sont traduits selon la langue active.
    """
    if not verses:
        return
    reciter = reciter or active_reciter()
    pal = _palette()
    items = [
        {
            "sura": int(v["sura"]),
            "aya": int(v["aya"]),
            "url": config.audio_url(reciter["edition"], v["sura"], v["aya"]),
        }
        for v in verses
    ]
    payload = json.dumps(items, ensure_ascii=False)
    play = json.dumps(t("ui.listen"), ensure_ascii=False)
    stop = json.dumps(t("ui.stop"), ensure_ascii=False)
    playing = json.dumps(t("app.read_playing"), ensure_ascii=False)
    meta = html.escape(f"{reciter['label']} · {len(items)} {t('ui.verse')}")
    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;}}
      .wrap{{display:flex;align-items:center;gap:8px;
        font-family:system-ui,"Segoe UI",sans-serif;flex-wrap:wrap;}}
      button{{cursor:pointer;border:1px solid {pal['border']};
        background:{pal['field']};color:{pal['fg']};border-radius:999px;
        height:30px;padding:0 12px;font-size:13px;display:inline-flex;
        align-items:center;gap:6px;transition:.15s;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
      .pos{{font-size:12.5px;color:{pal['fg2']};min-width:150px;}}
      .meta{{font-size:11px;color:{pal['fg2']};}}
    </style></head><body>
      <div class="wrap">
        <button id="pp">&#9654; {t("ui.listen")}</button>
        <button id="st">&#9632; {t("ui.stop")}</button>
        <span class="pos" id="pos">{meta}</span>
        <audio id="au" preload="none"></audio>
      </div>
      <script>
        const ITEMS = {payload};
        const au = document.getElementById('au');
        const pos = document.getElementById('pos');
        const pp = document.getElementById('pp');
        const PLAY = {play}, STOP = {stop}, tmpl = {playing};
        let idx = 0, playing = false;
        function show(i){{pos.textContent = tmpl.replace('{{a}}', ITEMS[i].sura + ':' + ITEMS[i].aya);}}
        function load(i){{au.src = ITEMS[i].url; show(i);}}
        function next(){{ idx++; if(idx >= ITEMS.length){{ stop(); return; }} load(idx); au.play(); }}
        function start(){{ playing = true; pp.textContent = STOP; if(!au.src) load(0); au.play(); }}
        function stop(){{ playing = false; pp.textContent = PLAY; au.pause(); idx = 0; au.removeAttribute('src'); pos.textContent = {json.dumps(meta)}; }}
        pp.addEventListener('click', function(){{ if(playing) stop(); else start(); }});
        document.getElementById('st').addEventListener('click', stop);
        au.addEventListener('ended', function(){{ if(playing) next(); }});
      </script>
    </body></html>"""
    st.iframe(comp, height=64)


def parse_ref(text: str) -> tuple[int, int] | None:
    """Analyse une référence « sourate:verset » → (sura, aya) ou None."""
    if not text or ":" not in text:
        return None
    left, _, right = text.strip().partition(":")
    try:
        sura, aya = int(left), int(right)
    except ValueError:
        return None
    if 1 <= sura <= 114 and aya >= 1:
        return sura, aya
    return None


def bookmark_button(sura: int, aya: int, key_prefix: str = "bmv") -> None:
    """Petit bouton d'ajout / retrait d'un verset aux favoris."""
    saved = bookmarks.contains(sura, aya)
    label = t("ui.bookmark_remove") if saved else t("ui.bookmark_add")
    if st.button(label, key=f"{key_prefix}_{sura}_{aya}"):
        bookmarks.toggle(sura, aya)
        st.rerun()


def render_verse(
    sura: int,
    aya: int,
    text_uthmani: str,
    translations: list,
    label: str | None = None,
    caption: str | None = None,
    font_size: str = "1.45rem",
    audio: bool = True,
    bookmark: bool = False,
    media: bool = True,
) -> None:
    """Affiche un verset : référence (avec nom de sourate), texte arabe uthmani
    puis, systématiquement, les traductions empilées.

    Si les préférences l'autorisent, un **lecteur de récitation** (verset) et un
    **unique** bouton **de synthèse vocale dans la langue active** (voix
    ``fr-FR`` ou ``en-US``) sont ajoutés, regroupés en un seul composant.
    ``audio=False`` permet de désactiver la récitation (ex. versets de contexte).
    ``bookmark=True`` ajoute un bouton d'ajout / retrait des favoris.
    """
    names = surah_names()
    ref = f"{sura}:{aya}"
    name = names.get(sura, "")
    show_audio = bool(audio) and st.session_state.get("show_quran_audio", True)
    show_tts = st.session_state.get("show_tts", True)
    trans = translations_for_lang(translations)
    st.markdown(f"**{label or (f'{ref} — {name}' if name else ref)}**")
    st.markdown(
        f"<div dir='rtl' lang='ar' style='font-size:{font_size};"
        f"line-height:2.2;margin:.2rem 0 .5rem 0'>{text_uthmani}</div>",
        unsafe_allow_html=True,
    )
    if media and (show_audio or (show_tts and trans)):
        verse_media(sura, aya, trans)
    if not trans:
        st.caption(t("ui.no_translation"))
    for tr in trans:
        st.markdown(f"**{tr['author']}** — {tr['text']}")
    if caption:
        st.caption(caption)
    if bookmark:
        bookmark_button(sura, aya)
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
        st.warning(t("ui.root_notfound", q=res.get("input", "")))
        return
    st.markdown(
        t(
            "ui.root_header",
            ar=res["root_arabic"],
            bw=res["root_buckwalter"],
            n=res["count"],
            v=res["verses_count"],
        )
    )
    if limit_note:
        st.caption(limit_note)
    elif res["count"] >= 1000:
        st.caption(t("ui.limit_1000"))

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
                    t(
                        "ui.lemma_fmt",
                        form=o["form_arabic"],
                        trans=o["transliteration"],
                        pos=o["pos"],
                        lemma=o["lemma_buckwalter"],
                    )
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
    return t(
        "ui.counter",
        n=summary["occurrences"],
        v=summary["verses"],
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
    placeholder: str | None = None,
    default_limit: int = 50,
) -> None:
    """Champ de recherche universel réutilisé par tous les modules.

    Accepte indifféremment un **mot français** (passerelle automatique vers les
    racines) ou un **mot / racine arabe** (recherche dans le texte). Affiche
    **systématiquement le nombre total d'occurrences**, puis les versets
    contextualisés dans la charte visuelle courante.
    """
    q = st.text_input(
        t("ui.uni_label"),
        key=f"uni_{section_key}",
        placeholder=placeholder or t("ui.uni_placeholder"),
        label_visibility="collapsed",
    )
    if not q:
        return

    with st.spinner(t("ui.spinner")):
        summary = occurrence_summary(con, q)

    has_hits = summary and (
        summary["props"] or summary["ar_rows"] or summary["fr_rows"]
    )
    if not has_hits:
        st.warning(t("ui.no_match", q=q))
        return

    # --- Compteur d'occurrences : toujours affiché ------------------------
    if summary["kind"] == "text":
        st.success(t("ui.success_text", count=counter_label(summary), q=summary["query"]))
    elif summary["occurrences"]:
        st.success(
            t(
                "ui.success_bridge",
                count=counter_label(summary),
                roots=summary["roots"],
                q=summary["query"],
            )
        )
    else:
        st.info(
            t(
                "ui.success_no_root",
                q=summary["query"],
                n=summary["fr_verses"],
            )
        )
    if summary["fr_verses"]:
        st.caption(t("ui.also_trans", q=summary["query"], n=summary["fr_verses"]))

    # --- Correspondances (français → racines) -----------------------------
    if summary["props"]:
        with st.expander(
            t("ui.bridge_expander", n=len(summary["props"])),
            expanded=(summary["kind"] == "bridge"),
        ):
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
                    for p in summary["props"]
                ]
            )

    # --- Versets contextualisés -------------------------------------------
    if summary["kind"] == "text":
        # Mot arabe : occurrences textuelles directes.
        _render_rows(con, summary["ar_rows"])
        if summary["verses"] > len(summary["ar_rows"]):
            st.caption(
                t(
                    "ui.limit_rows",
                    shown=len(summary["ar_rows"]),
                    total=summary["verses"],
                )
            )
    elif summary["props"]:
        # Racine (arabe directe) ou passerelle française : explorer une racine.
        pick = st.selectbox(
            t("ui.pick_root"),
            list(range(len(summary["props"]))),
            format_func=lambda i: (
                f"{summary['props'][i]['root_ar']} "
                f"[{summary['props'][i]['root_bw']}] — "
                f"{summary['props'][i]['verses']} {t('app.word_verses')}"
            ),
            key=f"uni_pick_{section_key}",
        )
        limit = st.slider(
            t("ui.occ_limit"),
            10, 500, default_limit,
            key=f"uni_limit_{section_key}",
        )
        res = search.search_root(con, summary["props"][pick]["root_bw"], limit=limit)
        note = None
        if res.get("found") and res["count"] >= limit:
            note = t("ui.limit_props", n=res["count"], limit=limit)
        render_root_results(con, res, limit_note=note)

    # --- Occurrences dans les traductions de la langue active --------------
    if summary["fr_rows"]:
        with st.expander(
            t(
                "ui.verses_where",
                q=summary["query"],
                n=summary["fr_verses"],
            )
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
        t("ui.surah"),
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
        t("ui.verse"),
        1,
        int(max_aya),
        default,
        key=f"vp_aya_{key}",
    )
    return int(sura), int(aya)


# --------------------------------------------------------------------------
# Dons / soutien (PRÉPARÉ, désactivé par défaut — voir config.DONATIONS_ENABLED)
# --------------------------------------------------------------------------
def donation_section() -> None:
    """Section « Soutenir le projet » (PayPal, carte, Bitcoin).

    N'est rendue que si ``config.DONATIONS_ENABLED`` est vrai et qu'au moins un
    moyen de paiement est renseigné. Le module est prêt mais **inactif** tant
    que le drapeau reste à False : aucune donnée ni lien n'est exposé.
    """
    if not getattr(config, "DONATIONS_ENABLED", False):
        return
    links = getattr(config, "DONATIONS", {}) or {}
    if not any((links.get("paypal"), links.get("card"), links.get("bitcoin"))):
        return

    with st.expander(t("app.donate_title")):
        st.markdown(t("app.donate_intro"))
        if links.get("paypal"):
            st.link_button(t("app.donate_paypal"), links["paypal"])
        if links.get("card"):
            st.link_button(t("app.donate_card"), links["card"])
        if links.get("bitcoin"):
            st.markdown(f"**{t('app.donate_bitcoin')}**")
            st.code(links["bitcoin"])
        st.caption(t("app.donate_note"))

