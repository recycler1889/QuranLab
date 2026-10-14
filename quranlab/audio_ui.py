"""Onglet « Écoute du Coran » — lecture audio immersive avec enchaînement automatique.

Fonctionnalités :
- Table des sourates interactive (clic sur une ligne → lecture immédiate)
- Deux modes : **Arabe seul** (récitation MP3 EveryAyah) / **Arabe + Traduction FR** (MP3 + TTS)
- Enchaînement automatique : à la fin d'une sourate, la suivante démarre
- Interface glassmorphism, animations fluides, état persistant
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


def _build_surah_items(con, sura: int, reciter: dict, mode: str) -> list:
    """Construit la liste des items audio pour une sourate.

    Chaque item : {"sura", "aya", "url", "fr" (optionnel)}
    """
    verses = search.surah_verses(con, sura, 1, None)
    items = []
    for v in verses:
        item = {
            "sura": v["sura"],
            "aya": v["aya"],
            "url": config.audio_url(reciter["edition"], v["sura"], v["aya"]),
        }
        if mode == "bilingual":
            fr = next(
                (
                    tr["text"] for tr in v.get("translations", [])
                    if str(tr.get("language", "")).lower() == "fr" and tr.get("text")
                ),
                "",
            )
            item["fr"] = fr
        items.append(item)
    return items


def _player_html(
    items: list,
    mode: str,
    sura: int,
    sura_name: str,
    auto_chain: bool,
    next_sura: int | None,
    next_sura_name: str | None,
) -> str:
    """Génère le HTML/JS du lecteur audio unifié (glassmorphism)."""
    pal = ui._palette()
    payload = json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")
    play = json.dumps(t("ui.listen"), ensure_ascii=False)
    stop = json.dumps(t("ui.stop"), ensure_ascii=False)
    tmpl = json.dumps(t("app.read_playing"), ensure_ascii=False)
    now_playing = html.escape(t("audio.now_playing", sura=sura, name=sura_name))
    next_surah_str = ""
    if next_sura and next_sura_name:
        next_surah_str = html.escape(t("audio.next_surah", sura=next_sura, name=next_sura_name))
    legend = html.escape(t("audio.bilingual_legend" if mode == "bilingual" else "audio.arabic_help"))
    chain_js = "true" if auto_chain else "false"
    next_sura_js = str(next_sura) if next_sura else "null"
    next_sura_name_js = json.dumps(next_sura_name) if next_sura_name else "null"
    click_hint = html.escape(t("audio.click_to_play"))

    # Styles inline pour le player (glassmorphism)
    glass_bg = f"linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%)"
    glass_border = pal['border']
    accent = pal['accent']
    gold = pal['gold']
    fg = pal['fg']
    fg2 = pal['fg2']

    comp = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;padding:0;background:transparent;
        font-family:system-ui,"Segoe UI",sans-serif;}}
      .player-wrap {{
        background: {glass_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {glass_border};
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 8px 32px -8px rgba(0,0,0,0.25);
        animation: ql-rise .4s cubic-bezier(.2,.7,.3,1) both;
      }}
      @keyframes ql-rise {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: none; }}
      }}
      .head {{ display:flex; align-items:center; gap:1rem; margin-bottom:1rem; flex-wrap:wrap; }}
      .surah-badge {{
        display:inline-flex; align-items:center; gap:.5rem;
        padding:.4rem .8rem;
        background: linear-gradient(135deg, {accent} 0%, #0a4d3a 100%);
        border-radius: 999px; font-weight:600; font-size:.85rem;
        color: {pal['bg']}; box-shadow: 0 2px 10px -2px {accent};
      }}
      .mode-pills {{ display:flex; gap:.5rem; flex-wrap:wrap; }}
      .mode-pill {{
        padding:.35rem .85rem;
        border: 1px solid {glass_border};
        border-radius: 999px;
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        color: {fg2}; font-size:.78rem; font-weight:500; cursor:pointer;
        transition: all .2s ease;
      }}
      .mode-pill.active, .mode-pill:hover {{
        border-color: {gold};
        background: linear-gradient(135deg, rgba(169,138,69,0.18) 0%, rgba(12,92,70,0.12) 100%);
        color: {fg};
      }}
      .mode-pill.active {{ box-shadow: 0 0 0 1px rgba(169,138,69,0.2); }}
      .controls {{ display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; margin-top:1rem; }}
      .btn {{
        display:inline-flex; align-items:center; gap:.4rem;
        padding:.55rem 1.1rem;
        border: 1px solid {glass_border};
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        color: {fg}; font-size:.85rem; font-weight:600; cursor:pointer;
        transition: all .18s cubic-bezier(.2,.7,.3,1);
      }}
      .btn:hover {{ border-color: {gold}; color: {accent}; transform:translateY(-1px);
        box-shadow: 0 4px 14px -4px rgba(0,0,0,0.2); }}
      .btn.primary {{
        background: linear-gradient(135deg, {accent} 0%, #0a4d3a 100%);
        border-color: {accent}; color: {pal['bg']};
      }}
      .btn.primary:hover {{ box-shadow: 0 6px 20px -6px {accent}; }}
      .time {{
        font-family:system-ui,"Segoe UI",sans-serif; font-size:.95rem;
        font-variant-numeric: tabular-nums; color: {fg2};
        min-width:90px; text-align:center;
      }}
      .progress {{ flex:1; min-width:120px; height:4px;
        background: rgba(169,138,69,0.15); border-radius: 999px; overflow:hidden; margin:0 .5rem; }}
      .progress-bar {{
        height:100%; background: linear-gradient(90deg, {accent} 0%, {gold} 100%);
        border-radius: 999px; transition: width .15s linear;
        box-shadow: 0 0 8px rgba(169,138,69,0.3);
      }}
      .legend {{ font-size:11px; color:{fg2}; margin-top:8px; }}
      .hint {{ font-size:10px; color:{fg2}; margin-top:4px; opacity:.7; }}
      .next-surah {{
        display:inline-flex; align-items:center; gap:.4rem;
        padding:.4rem .8rem;
        background: linear-gradient(135deg, rgba(169,138,69,0.12) 0%, transparent 100%);
        border: 1px solid {gold}; border-radius: 999px;
        color: {gold}; font-size:.78rem; font-weight:500;
        transition: all .2s ease;
      }}
      .next-surah:hover {{ background: linear-gradient(135deg, rgba(169,138,69,0.22) 0%, rgba(169,138,69,0.1) 100%);
        transform: translateX(3px); }}
    </style></head><body>
      <div class="player-wrap">
        <div class="head">
          <span class="surah-badge">{now_playing}</span>
          <div class="mode-pills">
            <span class="mode-pill {'active' if mode=='arabic_only' else ''}" data-mode="arabic_only">{t("audio.mode_arabic_only")}</span>
            <span class="mode-pill {'active' if mode=='bilingual' else ''}" data-mode="bilingual">{t("audio.mode_bilingual")}</span>
          </div>
        </div>
        <div class="controls">
          <button class="btn primary" id="pp">&#9654; {t("ui.listen")}</button>
          <button class="btn" id="st">&#9632; {t("ui.stop")}</button>
          <span class="time" id="cur">0:00</span>
          <div class="progress"><div class="progress-bar" id="pbar" style="width:0%"></div></div>
          <span class="time" id="dur">0:00</span>
        </div>
        <div class="legend">{legend}</div>
        <div class="hint">{click_hint}</div>
        <audio id="au" preload="metadata"></audio>
      </div>
      <script>
        var ITEMS = {payload};
        var au = document.getElementById('au');
        var pp = document.getElementById('pp');
        var pbar = document.getElementById('pbar');
        var cur = document.getElementById('cur');
        var dur = document.getElementById('dur');
        var PLAY = {play}, STOP = {stop}, tmpl = {tmpl};
        var idx = 0, phase = 'ar', playing = false;
        var AUTO_CHAIN = {chain_js};
        var NEXT_SURA = {next_sura_js};
        var NEXT_SURA_NAME = {next_sura_name_js};
        var MODE = "{mode}";
        function fmt(t){{ if(!isFinite(t)) return "0:00"; var m=Math.floor(t/60), s=Math.floor(t%60); return m+":"+(s<10?"0":"")+s; }}
        function show(i, fr){{
          var tag = ITEMS[i].sura + ':' + ITEMS[i].aya + (fr ? ' · FR' : '');
          cur.textContent = tmpl.replace('{{a}}', tag);
        }}
        function loadNextSurah(){{
          if (window.parent && window.parent.postMessage) {{
            window.parent.postMessage({{type: 'ql_load_surah', sura: NEXT_SURA}}, '*');
          }}
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
        function next(){{
          idx++;
          if(idx >= ITEMS.length){{
            if (AUTO_CHAIN && NEXT_SURA) {{
              loadNextSurah();
            }} else {{
              stop();
            }}
            return;
          }}
          playAr();
        }}
        function start(){{
          playing = true; pp.textContent = STOP;
          if(!au.src) {{ playAr(); }} else {{ au.play(); }}
        }}
        function stop(){{
          playing = false; pp.textContent = PLAY; au.pause();
          try{{ speechSynthesis.cancel(); }}catch(e){{}}
          idx = 0; au.removeAttribute('src');
          cur.textContent = "0:00"; dur.textContent = "0:00";
          pbar.style.width = "0%";
        }}
        au.addEventListener('loadedmetadata', function(){{
          dur.textContent = fmt(au.duration);
        }});
        au.addEventListener('timeupdate', function(){{
          if(au.duration){{
            cur.textContent = fmt(au.currentTime);
            pbar.style.width = (au.currentTime/au.duration*100) + "%";
          }}
        }});
        au.addEventListener('ended', function(){{
          if(!playing) return;
          if(phase === 'ar'){{
            if (MODE === "bilingual") {{ speakFr(); }} else {{ next(); }}
          }}
        }});
        pp.addEventListener('click', function(){{ if(playing) stop(); else start(); }});
        document.getElementById('st').addEventListener('click', stop);
        var RATE={float(st.session_state.get('tts_rate', 1.0))!r};
        var PITCH={float(st.session_state.get('tts_pitch', 1.0))!r};
        {ui._tts_voice_js('fr')}
      </script>
    </body></html>"""
    return comp


def render_tab(con) -> None:
    """Vue « Écoute du Coran » : table interactive + lecteur glassmorphism."""
    st.subheader(t("audio.title"))
    st.caption(t("audio.caption"))

    stats = cache.surah_audio_stats_cached(con)

    # --- Filtre ---
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

    # --- Tableau interactif (cliquable) ---
    table_rows = []
    for s in filtered:
        table_rows.append({
            t("audio.col_num"): s["number"],
            t("audio.col_name_ar"): s["name_ar"],
            t("audio.col_name_lat"): s["name_translit"],
            t("audio.col_verses"): s["verses_count"],
            t("audio.col_duration"): _fmt_duration(s["seconds"]),
        })

    # Injection CSS pour classe ql-clickable + script de clic
    click_js = """
    <script>
    (function(){
      function attach(){
        var tables = window.parent.document.querySelectorAll('table.ql');
        tables.forEach(function(table){
          if (table.dataset.qlAttached) return;
          table.dataset.qlAttached = '1';
          if (table.classList.contains('ql-clickable')){
            table.addEventListener('click', function(e){
              var row = e.target.closest('tr');
              if (!row || row.rowIndex === 0) return;
              var cells = row.cells;
              if (cells.length === 0) return;
              var sura = cells[0].textContent.trim();
              if (/^\\d+$/.test(sura)) {
                var url = new URL(window.location.href);
                url.searchParams.set('audio_sura', sura);
                window.history.replaceState({}, '', url);
                window.location.reload();
              }
            });
          }
        });
      }
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attach);
      } else { attach(); }
      // Re-attacher après reruns Streamlit
      var obs = new MutationObserver(attach);
      obs.observe(document.body, {childList: true, subtree: true});
    })();
    </script>
    """
    st.components.v1.html(click_js, height=0)

    # Appliquer la classe cliquable via HTML table (on ne peut pas modifier les classes facilement)
    # Solution: on génère le HTML nous-mêmes avec la classe
    table_html = "<table class='ql ql-clickable'><thead><tr>"
    for h in table_rows[0].keys() if table_rows else []:
        table_html += f"<th>{h}</th>"
    table_html += "</tr></thead><tbody>"
    for row in table_rows:
        table_html += "<tr>"
        for v in row.values():
            table_html += f"<td>{v}</td>"
        table_html += "</tr>"
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    if not filtered:
        st.info(t("audio.none"))
        return

    # --- État de session ---
    if "audio_current_sura" not in st.session_state:
        st.session_state.audio_current_sura = filtered[0]["number"]
    if "audio_mode" not in st.session_state:
        st.session_state.audio_mode = "arabic_only"
    if "audio_auto_chain" not in st.session_state:
        st.session_state.audio_auto_chain = True

    # Gérer clic sur tableau via query_params
    qp = st.query_params
    if "audio_sura" in qp:
        try:
            clicked = int(qp["audio_sura"])
            if any(s["number"] == clicked for s in filtered):
                st.session_state.audio_current_sura = clicked
                st.query_params.clear()
        except (ValueError, TypeError):
            pass

    sura = st.session_state.audio_current_sura
    mode = st.session_state.audio_mode
    auto_chain = st.session_state.audio_auto_chain

    # S'assurer que la sourate est dans la liste filtrée
    if not any(s["number"] == sura for s in filtered):
        sura = filtered[0]["number"]
        st.session_state.audio_current_sura = sura

    info = next(s for s in stats if s["number"] == sura)

    # --- Contrôles : mode + auto-chaining ---
    col_mode, col_chain = st.columns([2, 1])
    with col_mode:
        mode = st.radio(
            t("audio.mode_label"),
            options=["arabic_only", "bilingual"],
            format_func=lambda m: t("audio.mode_arabic_only") if m == "arabic_only" else t("audio.mode_bilingual"),
            horizontal=True,
            key="audio_mode_radio",
        )
        st.session_state.audio_mode = mode
    with col_chain:
        auto_chain = st.checkbox(
            t("audio.auto_chain"),
            value=auto_chain,
            help=t("audio.auto_chain_help"),
            key="audio_auto_chain_cb",
        )
        st.session_state.audio_auto_chain = auto_chain

    # Métriques
    col_a, col_b = st.columns(2)
    col_a.metric(t("audio.col_verses"), info["verses_count"])
    col_b.metric(t("audio.col_duration"), _fmt_duration(info["seconds"]))

    # Sourate suivante pour l'enchaînement
    all_suras = [s["number"] for s in stats]
    idx = all_suras.index(sura)
    next_sura = all_suras[idx + 1] if idx + 1 < len(all_suras) else None
    next_sura_name = None
    if next_sura:
        next_info = next(s for s in stats if s["number"] == next_sura)
        next_sura_name = next_info["name_translit"]

    # --- Lecteur unifié ---
    reciter = ui.active_reciter()
    items = _build_surah_items(con, sura, reciter, mode)
    player_html = _player_html(
        items=items,
        mode=mode,
        sura=sura,
        sura_name=info["name_translit"],
        auto_chain=auto_chain,
        next_sura=next_sura,
        next_sura_name=next_sura_name,
    )
    st.components.v1.html(player_html, height=140)

    # Bouton "Suivante" si auto_chain désactivé
    if not auto_chain and next_sura:
        if st.button(t("audio.next_surah", sura=next_sura, name=next_sura_name), key="audio_next_btn"):
            st.session_state.audio_current_sura = next_sura
            st.rerun()