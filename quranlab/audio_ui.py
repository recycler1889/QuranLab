"""Onglet « Écouter le Coran » — écoute audio sourate par sourate.

Complète l'onglet *Lire* par une vue **audio** : liste complète des sourates
(numéro, nom arabe et nom latin, nombre de versets, durée approximative) et
lecture de la récitation — arabe seul, ou **récitation arabe suivie de la
traduction française** de chaque verset (compréhension et contemplation).

Aucune donnée locale : la récitation provient d'EveryAyah (MP3 verset par
verset) ; la traduction française est lue par la synthèse vocale du navigateur
(Web Speech API).
"""

from __future__ import annotations

import html
import json

import streamlit as st

from . import cache, config, i18n, search, ui

t = i18n.t


def _fmt_duration(seconds: float) -> str:
    """Formatte une durée approximative (h min / min s / s)."""
    seconds = int(round(seconds or 0))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h} h {m:02d} min"
    if m:
        return f"{m} min {s:02d} s"
    return f"{s} s"


def _bilingual_player(items: list) -> None:
    """Lecteur bilingue : récitation arabe puis traduction française, enchaînées.

    ``items`` : ``[{"sura","aya","url","fr"}]`` — ``fr`` est la traduction
    française du verset (chaîne vide si indisponible). Un enchaînement par
    verset : MP3 du récitateur → synthèse vocale ``fr-FR`` → verset suivant.
    """
    if not items:
        return
    pal = ui._palette()
    payload = json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")
    play = json.dumps(t("ui.listen"), ensure_ascii=False)
    stop = json.dumps(t("ui.stop"), ensure_ascii=False)
    tmpl = json.dumps(t("app.read_playing"), ensure_ascii=False)
    legend = html.escape(t("audio.bilingual_legend"))
    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      .wrap{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
      button{{cursor:pointer;border:1px solid {pal['border']};
        background:{pal['field']};color:{pal['fg']};border-radius:999px;
        height:32px;padding:0 14px;font-size:13px;display:inline-flex;
        align-items:center;gap:6px;transition:.15s;}}
      button:hover{{border-color:{pal['accent']};color:{pal['accent']};}}
      .pos{{font-size:12.5px;color:{pal['fg2']};min-width:170px;}}
      .legend{{font-size:11px;color:{pal['fg2']};margin-top:4px;}}
    </style></head><body>
      <div class="wrap">
        <button id="pp">&#9654; {t("ui.listen")}</button>
        <button id="st">&#9632; {t("ui.stop")}</button>
        <span class="pos" id="pos">{legend}</span>
        <audio id="au" preload="none"></audio>
      </div>
      <div class="legend">{legend}</div>
      <script>
        var ITEMS = {payload};
        var au = document.getElementById('au');
        var pos = document.getElementById('pos');
        var pp = document.getElementById('pp');
        var PLAY = {play}, STOP = {stop}, tmpl = {tmpl};
        var idx = 0, phase = 'ar', playing = false;
        function show(i, fr){{
          var tag = ITEMS[i].sura + ':' + ITEMS[i].aya + (fr ? ' \\u00B7 FR' : '');
          pos.textContent = tmpl.replace('{{a}}', tag);
        }}
        function playAr(){{ phase = 'ar'; au.src = ITEMS[idx].url; show(idx, false); au.play(); }}
        function speakFr(){{
          var txt = ITEMS[idx].fr;
          if(!txt || !('speechSynthesis' in window)){{ next(); return; }}
          phase = 'fr'; show(idx, true);
          var u = qlSpeak(txt, '', 'fr-FR', RATE, PITCH);
          u.onend = function(){{ next(); }};
          u.onerror = function(){{ next(); }};
        }}
        function next(){{ idx++; if(idx >= ITEMS.length){{ stop(); return; }} playAr(); }}
        function start(){{
          playing = true; pp.textContent = STOP;
          if(!au.src) {{ playAr(); }} else {{ au.play(); }}
        }}
        function stop(){{
          playing = false; pp.textContent = PLAY; au.pause();
          try{{ speechSynthesis.cancel(); }}catch(e){{}}
          idx = 0; au.removeAttribute('src'); pos.textContent = {json.dumps(legend)};
        }}
        au.addEventListener('ended', function(){{
          if(!playing){{ return; }}
          if(phase === 'ar'){{ speakFr(); }}
        }});
        pp.addEventListener('click', function(){{ if(playing) stop(); else start(); }});
        document.getElementById('st').addEventListener('click', stop);
        var RATE={float(st.session_state.get('tts_rate', 1.0))!r};
        var PITCH={float(st.session_state.get('tts_pitch', 1.0))!r};
        {ui._tts_voice_js('fr')}
      </script>
    </body></html>"""
    st.iframe(comp, height=82)


def render_tab(con) -> None:
    """Vue « Écouter le Coran » : liste des sourates + lecteurs audio."""
    st.subheader(t("audio.title"))
    st.caption(t("audio.caption"))

    stats = cache.surah_audio_stats_cached(con)

    query = st.text_input(
        t("audio.filter"),
        key="audio_filter",
        placeholder=t("audio.filter_ph"),
        label_visibility="collapsed",
    )
    q = search.normalize_latin(query or "")
    filtered = [
        s for s in stats
        if not q
        or q in search.normalize_latin(s["name_translit"] or "")
        or q in search.normalize_arabic(s["name_ar"] or "")
        or (q.isdigit() and q == str(s["number"]))
    ]

    st.caption(t("audio.count", shown=len(filtered), total=len(stats)))

    ui.html_table([
        {
            t("audio.col_num"): s["number"],
            t("audio.col_name_ar"): s["name_ar"],
            t("audio.col_name_lat"): s["name_translit"],
            t("audio.col_verses"): s["verses_count"],
            t("audio.col_duration"): _fmt_duration(s["seconds"]),
        }
        for s in filtered
    ])

    if not filtered:
        st.info(t("audio.none"))
        return

    numbers = [s["number"] for s in filtered]
    labels = {
        s["number"]: t(
            "audio.surah_fmt",
            n=s["number"],
            ar=s["name_ar"],
            name=s["name_translit"],
            count=s["verses_count"],
        )
        for s in filtered
    }
    sura = st.selectbox(
        t("audio.choose_surah"),
        numbers,
        format_func=lambda n: labels[n],
        key="audio_sura",
    )
    info = next(s for s in stats if s["number"] == sura)

    col_a, col_b = st.columns(2)
    col_a.metric(t("audio.col_verses"), info["verses_count"])
    col_b.metric(t("audio.col_duration"), _fmt_duration(info["seconds"]))

    verses = search.surah_verses(con, sura, 1, None)

    st.markdown(f"**{t('audio.arabic_heading')}**")
    st.caption(t("audio.arabic_help"))
    ui.continuous_player(verses)

    st.markdown(f"**{t('audio.bilingual_heading')}**")
    st.caption(t("audio.bilingual_help"))
    with_fr = st.checkbox(t("audio.bilingual_toggle"), value=True, key="audio_fr")

    items = []
    reciter = ui.active_reciter()
    for v in verses:
        fr = ""
        if with_fr:
            fr = next(
                (
                    tr["text"] for tr in v.get("translations", [])
                    if str(tr.get("language", "")).lower() == "fr" and tr.get("text")
                ),
                "",
            )
        items.append(
            {
                "sura": v["sura"],
                "aya": v["aya"],
                "url": config.audio_url(reciter["edition"], v["sura"], v["aya"]),
                "fr": fr,
            }
        )
    _bilingual_player(items)
