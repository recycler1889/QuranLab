"""Onglet « Écoute du Coran » — lecteur sticky compact ultra-complet (natif, sans TTS).

Fonctionnalités :
- Table des sourates : clic → lecteur sticky compact (2-3 lignes)
- Métadonnées sourate : n°, nom AR/FR, nb versets, time-lapse dynamique
- Contrôles : Play/Pause, << >> (sourate préc/suiv), -10s/+10s, seek bar cliquable
- Modes : Arabe seul / Arabe + Français (fichiers natifs uniquement)
- Enchaînement auto sourate suivante, sticky au scroll, zero TTS
"""

from __future__ import annotations

import html
import json

import streamlit as st

from . import cache, config, i18n, search, ui

t = i18n.t


def _fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds or 0))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_duration_pair(ar_sec: float, bi_sec: float) -> str:
    """Format 'AR / BI' pour la colonne durée du tableau."""
    return f"{_fmt_duration(ar_sec)} / {_fmt_duration(bi_sec)}"


def _fmt_time_short(seconds: float) -> str:
    """Format court mm:ss pour l'affichage courant."""
    seconds = max(0, int(round(seconds or 0)))
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


def _has_french_audio() -> bool:
    return bool(config.FRENCH_AUDIO_BASE and config.FRENCH_AUDIO_EDITION)


def _build_surah_items(con, sura: int, reciter: dict, mode: str) -> list:
    verses = search.surah_verses(con, sura, 1, None)
    items = []
    for v in verses:
        ar_url = config.audio_url(reciter["edition"], v["sura"], v["aya"])
        fr_url = config.french_audio_url(v["sura"], v["aya"]) if mode == "bilingual" else ""
        items.append({
            "sura": v["sura"],
            "aya": v["aya"],
            "ar_url": ar_url,
            "fr_url": fr_url,
        })
    return items


def _player_html(
    items: list,
    mode: str,
    sura: int,
    sura_name: str,
    sura_name_ar: str,
    verses_count: int,
    total_est_seconds: float,
    auto_chain: bool,
    next_sura: int | None,
    next_sura_name: str | None,
    prev_sura: int | None,
    prev_sura_name: str | None,
    reciters: list | None = None,
    current_reciter_key: str | None = None,
    autoplay_requested: bool = False,
) -> str:
    pal = ui._palette()
    payload = json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")
    play = json.dumps(t("ui.listen"), ensure_ascii=False)
    pause = json.dumps(t("ui.pause"), ensure_ascii=False)
    stop = json.dumps(t("ui.stop"), ensure_ascii=False)
    tmpl = json.dumps(t("app.read_playing"), ensure_ascii=False)
    now_playing = html.escape(t("audio.now_playing", sura=sura, name=sura_name))
    legend = html.escape(t("audio.bilingual_legend" if mode == "bilingual" else "audio.arabic_help"))
    chain_js = "true" if auto_chain else "false"
    next_sura_js = str(next_sura) if next_sura else "null"
    next_sura_name_js = json.dumps(next_sura_name) if next_sura_name else "null"
    prev_sura_js = str(prev_sura) if prev_sura else "null"
    prev_sura_name_js = json.dumps(prev_sura_name) if prev_sura_name else "null"
    total_dur_fmt = html.escape(_fmt_duration(total_est_seconds))
    surah_meta = html.escape(t("audio.surah_meta", num=sura, name=sura_name, name_ar=sura_name_ar, verses=verses_count))

    glass_bg = "linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)"
    glass_border = pal['border']
    accent = pal['accent']
    gold = pal['gold']
    fg = pal['fg']
    fg2 = pal['fg2']
    fg3 = pal['fg']  # Use darker fg for better contrast in light theme

    comp = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  html,body{{margin:0;padding:0;background:transparent;
    font-family:system-ui,"Segoe UI",sans-serif;}}
  .player-wrap {{
    position: sticky; top: .75rem; z-index: 1000;
    background: {glass_bg};
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    border: 1px solid {glass_border};
    border-radius: 16px;
    padding: .7rem .9rem;
    box-shadow: 
      0 1px 0 rgba(255,255,255,0.05) inset,
      0 12px 32px -12px rgba(0,0,0,0.5);
    animation: ql-rise .35s cubic-bezier(.2,.7,.3,1) both;
  }}
  @keyframes ql-rise {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to   {{ opacity: 1; transform: none; }}
  }}
  .meta-row {{ display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; margin-bottom:.5rem; }}
  .surah-badge {{
    display:inline-flex; align-items:center; gap:.4rem;
    padding:.25rem .6rem;
    background: linear-gradient(135deg, {accent} 0%, #1a6b4a 100%);
    border-radius: 999px; font-weight:600; font-size:.72rem;
    color: #FDF6E3; box-shadow: 0 2px 8px -2px {accent};
    white-space: nowrap;
  }}
  .surah-meta {{ font-size:.7rem; color:{fg}; line-height:1.3; flex:1; min-width:180px; }}
  .time-lapse {{ font-family:ui-monospace,monospace; font-size:.75rem; font-variant-numeric:tabular-nums; color:{fg}; background:rgba(12,92,70,0.18); padding:.15rem .5rem; border-radius:999px; border:1px solid rgba(12,92,70,0.35); }}
  .mode-pills {{ display:flex; gap:.35rem; }}
  .mode-pill {{
    padding:.2rem .55rem;
    border: 1px solid {glass_border};
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    color: {fg2}; font-size:.65rem; font-weight:500; cursor:pointer;
    transition: all .12s ease;
  }}
  .mode-pill.active {{
    border-color: {gold};
    background: linear-gradient(135deg, rgba(169,138,69,0.18) 0%, rgba(12,92,70,0.12) 100%);
    color: {fg};
    box-shadow: 0 0 0 1px rgba(169,138,69,0.2);
  }}
  .controls {{ display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; }}
  .btn {{
    display:inline-flex; align-items:center; justify-content:center;
    width:32px; height:32px;
    border: 1px solid {glass_border};
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    color: {fg}; font-size:.7rem; font-weight:600; cursor:pointer;
    transition: all .1s cubic-bezier(.2,.7,.3,1);
    line-height:1;
  }}
  .btn:hover {{ border-color: {gold}; color: {accent}; transform:translateY(-1px);
    box-shadow: 0 3px 10px -3px rgba(0,0,0,0.2); }}
  .btn:active {{ transform:translateY(0) scale(.97); }}
  .btn.primary {{
    width:40px; background: linear-gradient(135deg, {accent} 0%, #0a4d3a 100%);
    border-color: {accent}; color: {pal['bg']};
  }}
  .btn.primary:hover {{ box-shadow: 0 4px 14px -4px {accent}; }}
  .time {{ font-family:ui-monospace,monospace; font-size:.7rem; font-variant-numeric:tabular-nums; color:{fg}; min-width:42px; text-align:center; }}
  .progress-wrap {{ flex:1; min-width:140px; height:5px; cursor:pointer;
    background: rgba(169,138,69,0.15); border-radius: 999px; overflow:hidden; margin:0 .4rem; position:relative; }}
  .progress-bar {{
    height:100%; background: linear-gradient(90deg, {accent} 0%, {gold} 100%);
    border-radius: 999px; transition: width .03s linear;
    box-shadow: 0 0 5px rgba(169,138,69,0.35);
  }}
  .progress-wrap:hover .progress-bar {{ box-shadow: 0 0 8px rgba(169,138,69,0.5); }}
  .legend {{ font-size:8px; color:{fg2}; margin-top:3px; opacity:.8; }}
  .nav-surah {{ display:flex; gap:.35rem; }}
  .nav-btn {{ padding:.15rem .45rem; font-size:.62rem; font-weight:600; }}
</style></head><body>
  <div class="player-wrap">
    <!-- Ligne 1 : Métadonnées + mode -->
    <div class="meta-row">
      <span class="surah-badge">{surah_meta}</span>
      <span class="time-lapse" id="tl">00:00 / {total_dur_fmt}</span>
      <div class="mode-pills">
        <span class="mode-pill {'active' if mode=='arabic_only' else ''}" data-mode="arabic_only">{t("audio.mode_arabic_only")}</span>
        <span class="mode-pill {'active' if mode=='bilingual' else ''}" data-mode="bilingual">{t("audio.mode_bilingual")}</span>
      </div>
    </div>
    <!-- Ligne 2 : Contrôles complets (disposition symétrique Windows Media Player) -->
    <div class="controls">
      <button class="btn" id="rew10" title="{t('audio.rewind_10')}">-10s</button>
      <button class="btn nav-btn" id="prev_sura" title="{t('audio.prev_surah')}">&#171;</button>
      <button class="btn primary" id="pp">&#9654;</button>
      <button class="btn nav-btn" id="next_sura" title="{t('audio.next_surah')}">&#187;</button>
      <button class="btn" id="fwd10" title="{t('audio.forward_10')}">+10s</button>
      <span class="time" id="cur">00:00</span>
      <div class="progress-wrap" id="prog"><div class="progress-bar" id="pbar" style="width:0%"></div></div>
      <span class="time" id="dur">{total_dur_fmt}</span>
      <button class="btn" id="st" title="{t('ui.stop')}">&#9632;</button>
      <span class="reciter-select" id="reciterDisplay">{t("audio.reciter")}</span>
    </div>
    <div class="legend">{legend}</div>
    <audio id="au" preload="metadata" crossorigin="anonymous"></audio>
  </div>
  <script>
    var ITEMS = {payload};
    var au = document.getElementById('au');
    var pp = document.getElementById('pp');
    var pbar = document.getElementById('pbar');
    var prog = document.getElementById('prog');
    var cur = document.getElementById('cur');
    var dur = document.getElementById('dur');
    var tl = document.getElementById('tl');
    var PLAY = {play}, PAUSE = {pause}, STOP = {stop}, tmpl = {tmpl};
    var idx = 0, phase = 'ar', playing = false;
    var AUTO_CHAIN = {chain_js};
    var NEXT_SURA = {next_sura_js};
    var NEXT_SURA_NAME = {next_sura_name_js};
    var PREV_SURA = {prev_sura_js};
    var PREV_SURA_NAME = {prev_sura_name_js};
    var MODE = "{mode}";
    var AUTOPLAY_REQUESTED = {str(autoplay_requested).lower()};
    var TOTAL_EST = {float(total_est_seconds)};
    function fmt(t){{ if(!isFinite(t)) return "00:00"; var m=Math.floor(t/60), s=Math.floor(t%60); return (m<10?"0":"")+m+":"+(s<10?"0":"")+s; }}
    function show(i, fr){{
      var tag = ITEMS[i].sura + ':' + ITEMS[i].aya + (fr ? ' · FR' : '');
      cur.textContent = tmpl.replace('{{a}}', tag);
    }}
    function loadSurah(suraNum, suraName){{
if (window.parent && window.postMessage) {{
        window.postMessage({{type: 'ql_load_surah', sura: suraNum}}, '*');
      }}
    }}
    function playAr(){{ phase = 'ar'; au.src = ITEMS[idx].ar_url; show(idx, false); au.play(); }}
    function playFr(){{
      var url = ITEMS[idx].fr_url;
      if(!url){{ next(); return; }}
      phase = 'fr'; show(idx, true);
      au.src = url; au.play();
    }}
    function nextVerse(){{
      idx++;
      if(idx >= ITEMS.length){{
        if (AUTO_CHAIN && NEXT_SURA) {{ loadSurah(NEXT_SURA, NEXT_SURA_NAME); }} else {{ stop(); }}
        return;
      }}
      if (MODE === "bilingual") {{ playFr(); }} else {{ playAr(); }}
    }}
    function prevSurah(){{
      if (PREV_SURA) {{ loadSurah(PREV_SURA, PREV_SURA_NAME); }}
    }}
    function nextSurah(){{
      if (NEXT_SURA) {{ loadSurah(NEXT_SURA, NEXT_SURA_NAME); }}
    }}
    function rewind10(){{ au.currentTime = Math.max(0, au.currentTime - 10); }}
    function forward10(){{ if(au.duration) au.currentTime = Math.min(au.duration, au.currentTime + 10); }}
    function start(){{
      playing = true; pp.textContent = PAUSE; pp.innerHTML = '&#10074;&#10074;';
      if(!au.src) {{ if (MODE === "bilingual") {{ playFr(); }} else {{ playAr(); }} }} else {{ au.play(); }}
    }}
    function stop(){{
      playing = false; pp.textContent = PLAY; pp.innerHTML = '&#9654;'; au.pause();
      idx = 0; phase = 'ar'; au.removeAttribute('src');
      cur.textContent = "00:00"; dur.textContent = fmt(TOTAL_EST);
      pbar.style.width = "0%";
      tl.textContent = "00:00 / " + fmt(TOTAL_EST);
    }}
    au.addEventListener('loadedmetadata', function(){{
      var d = isFinite(au.duration) ? au.duration : TOTAL_EST;
      dur.textContent = fmt(d);
      tl.textContent = "00:00 / " + fmt(d);
    }});
    au.addEventListener('timeupdate', function(){{
      if(au.duration){{
        cur.textContent = fmt(au.currentTime);
        var d = isFinite(au.duration) ? au.duration : TOTAL_EST;
        tl.textContent = fmt(au.currentTime) + " / " + fmt(d);
        pbar.style.width = (au.currentTime/au.duration*100) + "%";
      }}
    }});
    prog.addEventListener('click', function(e){{
      if(!au.duration) return;
      var rect = prog.getBoundingClientRect();
      var pct = (e.clientX - rect.left) / rect.width;
      au.currentTime = pct * au.duration;
    }});
    au.addEventListener('ended', function(){{
      if(!playing) return;
      if(phase === 'ar'){{
        if (MODE === "bilingual") {{ playFr(); }} else {{ nextVerse(); }}
      }} else {{
        nextVerse();
      }}
    }});
    pp.addEventListener('click', function(){{ if(playing) stop(); else start(); }});
    document.getElementById('st').addEventListener('click', stop);
    document.getElementById('rew10').addEventListener('click', rewind10);
    document.getElementById('fwd10').addEventListener('click', forward10);
    document.getElementById('prev_sura').addEventListener('click', prevSurah);
    document.getElementById('next_sura').addEventListener('click', nextSurah);
    // Auto-play on load if requested
    if (AUTOPLAY_REQUESTED) {{
      setTimeout(function() {{ start(); }}, 100);
    }}
    // Reciter display click → cycle to next reciter
    var reciterDisplay = document.getElementById('reciterDisplay');
    reciterDisplay.addEventListener('click', function() {{
      // Cycle through available reciters
      var current = reciterOptions[currentReciterIdx];
      var nextIdx = (currentReciterIdx + 1) % reciterOptions.length;
      var nextReciter = reciterOptions[nextIdx];
      // Post message to parent Streamlit app
      if (window.parent) {{
        window.parent.postMessage({{type: 'ql_change_reciter', key: nextReciter.key}}, '*');
      }}
      currentReciterIdx = nextIdx;
      // Update display text
      reciterDisplay.textContent = nextReciter.label;
    }}
  </script>
</body></html>"""
    return comp


def render_tab(con) -> None:
    st.subheader(t("audio.title"))
    st.caption(t("audio.caption"))

    stats = cache.surah_audio_stats_cached(con)

    # Filtre
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

    # État session
    if "audio_current_sura" not in st.session_state:
        st.session_state.audio_current_sura = filtered[0]["number"]
    if "audio_mode" not in st.session_state:
        st.session_state.audio_mode = "arabic_only"
    if "audio_auto_chain" not in st.session_state:
        st.session_state.audio_auto_chain = True
    if "audio_reciter_key" not in st.session_state:
        st.session_state.audio_reciter_key = ui.active_reciter()["key"]

    # Gestion clic tableau via postMessage (iframe -> parent)
    msg_js = """
    <script>
    (function(){
      if (window._qlMsgHandler) return;
      window._qlMsgHandler = true;
      window.addEventListener('message', function(e) {
        if (!e.data || e.data.type !== 'ql_load_surah') return;
        var sura = e.data.sura;
        var autoplay = e.data.autoplay;
        var url = new URL(window.location.href);
        url.searchParams.set('audio_sura', sura);
        if (autoplay) url.searchParams.set('audio_autoplay', '1');
        window.history.replaceState({}, '', url);
        window.location.reload();
      });
      // Gestion changement de récitateur
      if (e.data && e.data.type === 'ql_change_reciter') {{
        st.session_state.audio_reciter_key = e.data.key;
        window.location.reload();
      }}
    })();
    </script>
    """
    st.components.v1.html(msg_js, height=0)

    # Gestion clic tableau via query_params (fallback / reload)
    qp = st.query_params
    if "audio_sura" in qp:
        try:
            clicked = int(qp["audio_sura"])
            if any(s["number"] == clicked for s in filtered):
                st.session_state.audio_current_sura = clicked
                if qp.get("audio_autoplay") == "1":
                    st.session_state.audio_autoplay_requested = True
                st.query_params.clear()
        except (ValueError, TypeError):
            pass

    sura = st.session_state.audio_current_sura
    mode = st.session_state.audio_mode
    auto_chain = st.session_state.audio_auto_chain

    if not any(s["number"] == sura for s in filtered):
        sura = filtered[0]["number"]
        st.session_state.audio_current_sura = sura

    if mode == "bilingual" and not _has_french_audio():
        mode = "arabic_only"
        st.session_state.audio_mode = "arabic_only"

    info = next(s for s in stats if s["number"] == sura)

    # Tableau sourates cliquable (durées AR / BI séparées)
    table_rows = []
    for s in filtered:
        table_rows.append({
            t("audio.col_num"): s["number"],
            t("audio.col_name_ar"): s["name_ar"],
            t("audio.col_name_lat"): s["name_translit"],
            t("audio.col_verses"): s["verses_count"],
            t("audio.col_duration_ar"): _fmt_duration(s.get("seconds_ar", 0)),
            t("audio.col_duration_bi"): _fmt_duration(s.get("seconds_bi", 0)),
        })

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
                // Send message to parent Streamlit app
                window.postMessage({type: 'ql_load_surah', sura: parseInt(sura, 10), autoplay: true}, '*');
              }
            });
          }
        });
      }
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attach);
      } else { attach(); }
      var mo = new MutationObserver(attach);
      mo.observe(document.body, {childList: true, subtree: true});
    })();
    </script>
    """
    st.components.v1.html(click_js, height=0)

    if table_rows:
        headers = list(table_rows[0].keys())
        table_html = "<table class='ql ql-clickable'><thead><tr>"
        for h in headers:
            table_html += f"<th>{h}</th>"
        table_html += "</tr></thead><tbody>"
        for row in table_rows:
            table_html += "<tr>"
            for v in row.values():
                table_html += f"<td>{v}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info(t("audio.none"))
        return

    # Contrôles compacts
    _reciters = [r for r in (getattr(config, "RECITERS", []) or []) if r.get("key")]
    reciter_keys = [r["key"] for r in _reciters]
    reciter_labels = {r["key"]: r["label"] for r in _reciters}
    # Vérifier que le réciteur courant existe toujours
    if st.session_state.audio_reciter_key not in reciter_keys:
        st.session_state.audio_reciter_key = reciter_keys[0] if reciter_keys else ""

    col_mode, col_chain, col_rec = st.columns([2, 1, 2])
    with col_mode:
        mode = st.radio(
            t("audio.mode_label"),
            options=["arabic_only", "bilingual"],
            format_func=lambda m: t("audio.mode_arabic_only") if m == "arabic_only" else t("audio.mode_bilingual"),
            horizontal=True,
            key="audio_mode_radio",
            disabled=not _has_french_audio(),
        )
        st.session_state.audio_mode = mode
        if not _has_french_audio():
            st.caption(t("audio.french_help"))
    with col_chain:
        auto_chain = st.checkbox(
            t("audio.auto_chain"),
            value=auto_chain,
            help=t("audio.auto_chain_help"),
            key="audio_auto_chain_cb",
        )
        st.session_state.audio_auto_chain = auto_chain
    with col_rec:
        st.selectbox(
            t("audio.reciter_label"),
            options=reciter_keys,
            format_func=lambda k: reciter_labels.get(k, k),
            key="audio_reciter_select",
            on_change=lambda: setattr(st.session_state, "audio_reciter_key", st.session_state.audio_reciter_select),
            disabled=not reciter_keys,
        )

    # Métriques
    col_a, col_b = st.columns(2)
    col_a.metric(t("audio.col_verses"), info["verses_count"])
    col_b.metric(t("audio.col_duration"), _fmt_duration_pair(info.get("seconds_ar", 0), info.get("seconds_bi", 0)))

    # Sourates adjacentes
    all_suras = [s["number"] for s in stats]
    idx = all_suras.index(sura)
    prev_sura = all_suras[idx - 1] if idx > 0 else None
    prev_sura_name = None
    if prev_sura:
        prev_info = next(s for s in stats if s["number"] == prev_sura)
        prev_sura_name = prev_info["name_translit"]
    next_sura = all_suras[idx + 1] if idx + 1 < len(all_suras) else None
    next_sura_name = None
    if next_sura:
        next_info = next(s for s in stats if s["number"] == next_sura)
        next_sura_name = next_info["name_translit"]

    # Réciteur actuel (depuis session_state)
    reciter_key = st.session_state.audio_reciter_key
    reciter = next((r for r in _reciters if r["key"] == reciter_key), _reciters[0] if _reciters else ui.active_reciter())

    # Préparer la liste des récitateurs pour le player
    reciters_for_player = [{"key": r["key"], "label": r["label"], "edition": r["edition"]} for r in _reciters]

    # Lecteur STICKY ultra-compact
    autoplay_requested = st.session_state.pop("audio_autoplay_requested", False)
    items = _build_surah_items(con, sura, reciter, mode)
    player_html = _player_html(
        items=items,
        mode=mode,
        sura=sura,
        sura_name=info["name_translit"],
        sura_name_ar=info["name_ar"],
        verses_count=info["verses_count"],
        total_est_seconds=info.get("seconds_bi" if mode == "bilingual" else "seconds_ar", 0),
        auto_chain=auto_chain,
        next_sura=next_sura,
        next_sura_name=next_sura_name,
        prev_sura=prev_sura,
        prev_sura_name=prev_sura_name,
        reciters=reciters_for_player,
        current_reciter_key=reciter_key,
        autoplay_requested=autoplay_requested,
    )
    st.components.v1.html(player_html, height=140)