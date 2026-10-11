"""Internationalisation légère de QuranLab (français / anglais).

Le site est **entièrement** dans une langue : soit le français (défaut), soit
l'anglais — jamais un mélange. Le sélecteur de langue vit dans la barre
latérale ; le choix est persisté dans ``st.session_state``.

Le français est la langue de référence : si une clé manque dans l'anglais, la
traduction française est renvoyée en repli (aucun plantage). Les **données
d'étude** rédigées en français (catalogue des 164 thèmes, analyses des
controverses) restent telles quelles ; seul l'habillage autour d'elle est
traduit.
"""

from __future__ import annotations

import streamlit as st

LANG_KEY = "app_lang"
DEFAULT = "fr"

# --------------------------------------------------------------------------
# Catalogue FR (référence). Les valeurs anglaises reprennent les mêmes clés.
# --------------------------------------------------------------------------
_FR = {
    # --- Application / sidebar --------------------------------------------
    "app.title": "quranlab — analyse intra-coranique",
    "app.subtitle": (
        "Recherche et analyse strictement intra-coraniques — texte, structure, "
        "linguistique et racines. Sans tafsir, hadith ni interprétation "
        "post-coranique."
    ),
    "app.choose_lang": "Langue d'affichage",
    "app.prefs": "Préférences",
    "app.theme": "Thème visuel",
    "app.audio": "Audio",
    "app.reciter": "Récitateur",
    "app.reciter_help": "Récitation verset par verset (EveryAyah).",
    "app.show_audio": "Lecteur coranique par verset",
    "app.show_tts": "Synthèse vocale (TTS)",
    "app.tts_help": (
        "Lit chaque traduction à voix haute via le moteur du navigateur "
        "(voix sélectionnable et réglages dans les paramètres TTS)."
    ),
    "app.caption_scope": (
        "Lecture strictement intra-coranique — sans tafsir, hadith ni "
        "interprétation post-coranique."
    ),
    "app.suggest_title": "Suggestions d'amélioration",
    "app.suggest_body": (
        "QuranLab évolue au fil des usages. Idées, incohérences, sources à "
        "ajouter, nouveaux récitateurs ou langues, améliorations d'ergonomie : "
        "**faites-nous en part**."
    ),
    "app.write_us": "Écrivez-nous : {email}",
    "app.suggest_see_guide": (
        "Voir la section du même nom dans le guide de démarrage."
    ),
    "app.con": "Connexion à la base impossible",
    "app.none": "aucune",
    "app.word_surahs": "sourates",
    "app.word_verses": "versets",
    "app.word_words": "mots annotés",
    "app.word_roots": "racines",
    "app.word_translations": "traductions",
    "app.word_themes": "thèmes",
    "app.word_topics": "sujets d'analyse",
    "app.corpus": "Corpus",
    "app.stat_surahs": "{s} sourates · {v} versets",
    "app.stat_words": "{m} mots annotés · {r} racines distinctes",
    "app.stat_translations": "{n} traductions",
    "app.stat_themes": "{n} thèmes · {t} sujets d'analyse",
    # --- Onglets ------------------------------------------------------------
    "app.tab.root": "Racine",
    "app.tab.search": "Recherche",
    "app.tab.verse": "Verset comparé",
    "app.tab.theme": "Thèmes",
    "app.tab.controv": "Idées reçues",
    "app.tab.concord": "Concordance",
    # --- Onglet Racine ------------------------------------------------------
    "app.root_title": "Indexation par racine",
    "app.root_placeholder": (
        "Rechercher en français ou en arabe (ex. miséricorde / رحمة)…"
    ),
    "app.root_caption": (
        "Saisir une racine en arabe (رحم) ou en Buckwalter (rHm)."
    ),
    "app.root_label": "Racine",
    "app.root_ctx": "Contexte (± versets)",
    # --- Onglet Recherche ---------------------------------------------------
    "app.search_title": "Recherche textuelle et multilingue",
    "app.search_placeholder": "Rechercher un mot en français ou en arabe…",
    "app.input_lang": "Langue",
    "app.search_term": "Terme",
    "app.bridge_heading": "Passerelle français → arabe",
    "app.bridge_none": (
        "Aucune correspondance automatique trouvée pour ce terme (lexique, "
        "thèmes, corpus) — voir les résultats textuels français ci-dessous."
    ),
    "app.bridge_query_root": "Interroger le texte original par racine",
    "app.bridge_limit": "Occurrences de la racine à afficher",
    "app.bridge_note": (
        "Premières {n} occurrences (limite réglée à {limit})."
    ),
    "app.original_heading": "Texte original (racine sélectionnée)",
    "app.fr_occurrences": "Occurrences françaises (traductions)",
    "app.rows_verses": "{n} verset(s) — un seul affichage par verset.",
    "app.limit_100": "Limite atteinte : 100 premiers versets affichés.",
    "app.hits_trans": "terme présent dans {n} traduction(s) : {keys}",
    # --- Onglet Verset comparé ----------------------------------------------
    "app.verse_title": "Affichage comparatif et versets similaires",
    "app.verse_placeholder": "Rechercher en français ou en arabe (ex. lumière / نور)…",
    "app.mode": "Mode",
    "app.mode_compare": "Comparer deux versets",
    "app.mode_similar": "Suggérer des versets similaires",
    "app.compare_caption": (
        "Sélectionnez deux versets indépendamment : ils sont affichés côte à "
        "côte avec leur texte arabe, leurs traductions et leurs racines."
    ),
    "app.verse_a": "Verset A",
    "app.verse_b": "Verset B",
    "app.verse_missing": "Verset {ref} introuvable.",
    "app.struct_title": "Comparaison de structure thématique (racines)",
    "app.common_roots": "{n} racine(s) commune(s) : {roots}",
    "app.roots_of": "Racines de {ref} ({n}) — {roots}",
    "app.similar_caption": (
        "Saisissez une référence (sura:aya) pour trouver ses versets en miroir, "
        "ou un mot-clé (français ou arabe) pour une suggestion par proximité de "
        "racines."
    ),
    "app.ref_input": "Verset de référence (sura:aya) ou mot-clé",
    "app.min_shared": "Racines communes minimales",
    "app.nb_suggestions": "Nombre de suggestions",
    "app.ref_verse": "Verset de référence",
    "app.ref_format": "Format attendu : sura:aya (ex. 4:34)",
    "app.mirror_roots": "Racines du verset ({n}) : {roots}",
    "app.mirror_matches": "{n} verset(s) similaire(s)",
    "app.mirror_empty": (
        "Aucun verset ne partage assez de racines — baissez le seuil de racines "
        "communes minimales."
    ),
    "app.mirror_label": "{ref}  ·  {n} racines communes ({pct}%)",
    "app.shared_roots_caption": "racines partagées : {roots}",
    "app.no_roots_keyword": (
        "Aucune racine exploitable pour « {q} » — essayez un autre mot-clé ou "
        "une référence sura:aya."
    ),
    "app.keyword_roots": "Racines du mot-clé « {q} » ({n}) : {roots}",
    "app.suggested_matches": "{n} verset(s) similaire(s) suggéré(s)",
    # --- Onglet Thèmes ------------------------------------------------------
    "app.theme_title": "Cartographie thématique intra-coranique",
    "app.theme_placeholder": (
        "Rechercher en français ou en arabe (lancera aussi la passerelle)…"
    ),
    "app.theme_query": "Rechercher un thème (libellé, description, racine, terme…)",
    "app.theme_query_ph": "ex. salât, رحم, miséricorde, or, orphelins…",
    "app.category": "Catégorie",
    "app.category_all": "Toutes",
    "app.theme_count": (
        "{shown} thème(s) affiché(s) sur {total} · {cats} catégories · "
        "{links} rattachement(s) thème↔verset."
    ),
    "app.theme_none": (
        "Aucun thème ne correspond — modifiez le mot-clé ou repassez la "
        "catégorie sur « Toutes »."
    ),
    "app.theme_pick": "Thème",
    "app.theme_pick_ph": "— Choisissez un thème pour voir ses versets —",
    "app.theme_pick_wait": (
        "Sélectionnez un thème ci-dessus : les versets rattachés et leur "
        "récitation s'afficheront ici (rien n'est chargé tant que rien n'est "
        "choisi — l'interface reste légère)."
    ),
    "app.theme_catline": (
        "Catégorie : {cat} · Racines : {roots} · {n} verset(s){extra}"
    ),
    "app.theme_extra_ar": " · termes arabe : {terms}",
    "app.theme_extra_fr": " · termes fr : {terms}",
    "app.theme_sources": "sources : {src}",
    "app.theme_overview": "Vue d'ensemble des {n} thème(s) affiché(s)",
    "app.overview_cat": "catégorie",
    "app.overview_theme": "thème",
    "app.overview_key": "clé",
    "app.overview_roots": "racines",
    "app.overview_verses": "versets",
    "app.data_en_note": (
        "Contenu du catalogue (thèmes / controverses) rédigé en français — "
        "source d'étude conservée telle quelle."
    ),
    # --- Onglet Idées reçues ------------------------------------------------
    "app.controv_title": "Analyse textuelle des idées reçues et controverses",
    "app.controv_placeholder": (
        "Rechercher en français ou en arabe (ex. femme / نساء)…"
    ),
    "app.controv_method": "Méthode : {m}",
    "app.controv_count": "{n} sujets — analyse textuelle descriptive, sans conclusion doctrinale.",
    "app.controv_pick": "Sujet",
    "app.controv_pick_ph": "— Choisissez un sujet pour voir son analyse —",
    "app.controv_wait": (
        "Choisissez un sujet dans la liste : récurrence lexicale, polysémie et "
        "versets clés s'afficheront ici."
    ),
    "app.controv_question": "Question posée : {q}",
    "app.controv_framing": "Note intra-coranique : {f}",
    "app.controv_read": "Lecture conseillée : {t}",
    "app.recurrence_title": "Récurrence lexicale dans tout le corpus",
    "app.rec_type": "type",
    "app.rec_item": "élément",
    "app.rec_detail": "clé",
    "app.rec_occ": "occurrences",
    "app.rec_verses": "versets",
    "app.polysemy_title": "Polysémie — toutes les formes d'une même racine",
    "app.polysemy_form": "Racine {root} [{bw}] — {n} occurrences / {v} versets",
    "app.polysemy_forms": "Formes rencontrées : {forms}",
    "app.poly_verse": "verset",
    "app.poly_form": "forme",
    "app.poly_context": "contexte",
    "app.key_verses": "Versets clés — texte arabe et traductions plurielles",
    "app.verse_missing_key": "Verset introuvable : {ref}",
    # --- Onglet Concordance -------------------------------------------------
    "app.concord_title": "Concordance interne — « le Coran s'explique par le Coran »",
    "app.concord_placeholder": (
        "Rechercher en français ou en arabe pour bâtir une concordance…"
    ),
    "app.concord_caption": (
        "Croisement de versets par racines partagées : concordance par notion, "
        "et versets en miroir d'un verset de référence."
    ),
    "app.mode_mirror": "Verset en miroir",
    "app.mode_notion": "Concordance par notion",
    "app.mirror_ref": "Verset de référence (sura:aya)",
    "app.min_shared_mirror": "Racines communes minimales",
    "app.nb_mirror": "Nombre de versets en miroir",
    "app.mirror_matches_n": "{n} verset(s) en miroir",
    "app.criterion": "Critère",
    "app.crit_root": "Racine",
    "app.crit_term": "Terme arabe",
    "app.root_input": "Racine (arabe ou Buckwalter)",
    "app.arabic_term": "Terme arabe",
    "app.concord_line": (
        "Concordance {kind} : {label} `[{detail}]` — {n} occurrence(s) dans "
        "{v} verset(s)"
    ),
    "app.no_result": "Aucun résultat.",
    # --- Thèmes des libellés de type (polysémie) ----------------------------
    "ui.type.root": "racine",
    "ui.type.term": "terme",
    "ui.lang.fr": "Français",
    "ui.lang.ar": "Arabe",
    "ui.lang.en": "Anglais",
    # --- TTS (lecteurs audio / synthèse vocale) -----------------------------
    "ui.listen": "Écouter",
    "ui.pause": "Pause",
    "ui.stop": "Arrêter",
    "ui.tts_unavail": "TTS indisponible",
    "ui.play": "Lire",
    "ui.listen_title": "Lecture / Pause",
    "ui.stop_title": "Arrêter",
    "ui.tts_title": "Lire à voix haute ({locale})",
    "ui.tts_button": "Écouter en français",
    "ui.speak_tooltip": "Synthèse vocale ({locale})",
    "ui.tts_settings": "Paramètres de la synthèse vocale",
    "ui.rate": "Débit",
    "ui.rate_help": "Vitesse de lecture : 1.0 = normale.",
    "ui.pitch": "Hauteur (ton)",
    "ui.pitch_help": "Gravité de la voix : 1.0 = normale.",
    "ui.voice_hint": (
        "Si la lecture épeille les lettres, sélectionnez une voix {lang} "
        "ci-dessous puis cliquez *Appliquer*."
    ),
    "ui.vl_label": "Voix de synthèse (francophone de préférence)",
    "ui.apply": "Appliquer",
    "ui.test_voice": "Tester",
    "ui.voice_none": (
        "Aucune voix « {lang} » détectée dans ce navigateur : le texte risque "
        "d'être mal prononcé ou épelé lettre à lettre."
    ),
    "ui.voice_few": (
        "Une seule voix « {lang} » détectée. Pour un rendu plus naturel, ouvrez "
        "le site dans Microsoft Edge (voix « Natural » en ligne, gratuites) ou "
        "installez d'autres voix dans Windows : Paramètres → Heure et langue → "
        "Parole."
    ),
    "ui.voice_tip": (
        "Astuce : Microsoft Edge propose des voix « Natural » françaises très "
        "fluides, sans rien installer."
    ),
    "ui.tts_external_on": (
        "Synthèse vocale fournie par un service externe configuré (voix "
        "hors navigateur)."
    ),
    "ui.piper_engine": (
        "Moteur : Piper — voix neuronales hors-ligne, plusieurs voix au choix."
    ),
    "ui.piper_voice": "Voix",
    "ui.piper_voice_help": (
        "Choisissez parmi plusieurs voix françaises, puis cliquez *Tester*."
    ),
    "ui.piper_first_use": (
        "La première utilisation télécharge le modèle (quelques Mo)."
    ),
    "ui.piper_unavailable": (
        "Piper n'est pas installé : lecture via les voix du navigateur."
    ),
    "ui.tts_generating": "Génération de la voix…",
    "ui.tts_fail": "Échec de la synthèse : {err}",
    "ui.sample_fr": (
        "Bonjour. Ceci est un test de lecture en français : le Coran "
        "s'explique par le Coran."
    ),
    "ui.sample_en": (
        "Hello. This is an English reading test: the Qur'an explains itself "
        "by the Qur'an."
    ),
    "ui.auto": "Auto",
    "ui.auto_opt": "Auto (meilleure voix {lang})",
    "ui.other_voices": "Autres voix",
    "ui.loading_voices": "Chargement des voix…",
    "ui.no_tts": "Synthèse vocale indisponible dans ce navigateur.",
    "ui.voices_found": "{n} voix francophone(s) détectée(s)",
    "ui.voice_selected": " — sélectionnée : {name}",
    "ui.unavailable": "(introuvable)",
    "ui.then_listen": ". Puis « {label} » dans un verset.",
    "ui.no_translation": "Aucune traduction disponible.",
    "ui.root_notfound": "Racine introuvable : {q}",
    "ui.root_header": "**Racine {ar}** `[{bw}]` — {n} occurrence(s) dans {v} verset(s)",
    "ui.limit_1000": "Limite atteinte : 1000 premières occurrences affichées.",
    "ui.lemma_fmt": "{form} ({trans}, {pos}, lemme {lemma})",
    "ui.counter": "{n} occurrence(s) trouvée(s) dans {v} verset(s)",
    "ui.uni_label": "Recherche universelle (français ou arabe)",
    "ui.uni_placeholder": "Rechercher en français ou en arabe (ex. miséricorde / رحمة)…",
    "ui.spinner": "Recherche dans tout le Coran…",
    "ui.ref_detected": "Référence directe reconnue — affichage du verset {ref}.",
    "ui.ref_label": "Verset {ref} (référence directe)",
    "ui.ref_missing": "Verset {ref} introuvable dans le corpus.",
    "ui.no_match": (
        "Aucune correspondance trouvée pour « {q} ». Essayez un autre mot "
        "(français ou arabe) ou une racine (ex. رحم ou rHm)."
    ),
    "ui.success_text": "**{count}** pour « {q} » (recherche textuelle arabe).",
    "ui.success_bridge": (
        "**{count}** — à partir de {roots} racine(s) associée(s) à « {q} »."
    ),
    "ui.success_no_root": (
        "Aucune racine associée automatiquement, mais « {q} » apparaît dans "
        "{n} verset(s) (traductions)."
    ),
    "ui.also_trans": "« {q} » figure aussi dans les traductions de {n} verset(s).",
    "ui.bridge_expander": "Correspondances français → arabe ({n})",
    "ui.table_fr": "français",
    "ui.table_root": "racine",
    "ui.table_bw": "buckwalter",
    "ui.table_verses": "versets",
    "ui.table_occ": "occurrences",
    "ui.table_source": "source",
    "ui.limit_rows": "Limite atteinte : {shown} versets affichés sur {total}.",
    "ui.limit_props": "Premières {n} occurrences (limite réglée à {limit}).",
    "ui.verses_where": "Versets où « {q} » figure dans les traductions ({n})",
    "ui.pick_root": "Racine à explorer",
    "ui.pick_root_fmt": "{ar} [{bw}] — {v} versets",
    "ui.occ_limit": "Occurrences à afficher",
    "ui.surah": "Sourate",
    "ui.verse": "Verset",
    "ui.bookmark_add": "☆ Ajouter aux favoris",
    "ui.bookmark_remove": "★ En favori",
    "app.tab.read": "Lire le Coran Iqra",
    "app.read_title": "Lire le Coran Iqra",
    "app.read_caption": (
        "Sourate par sourate, verset par verset — texte arabe, traductions et "
        "récitation."
    ),
    "app.read_surah": "Sourate",
    "app.read_surah_fmt": "{n}. {name} — {count} versets",
    "app.read_from": "Du verset",
    "app.read_to": "au verset",
    "app.read_range": "Plage de versets à afficher",
    "app.read_prev": "Précédents",
    "app.read_next": "Suivants",
    "app.read_all": "Toute la sourate",
    "app.read_showing": "Versets {a} à {b} sur {n}.",
    "app.read_jump": "Aller à une sourate ou un verset",
    "app.read_jump_ph": "ex. 2:255 · 2.255 · 2/255 · 2 255 (ou n° : 2)",
    "app.read_jump_bad": (
        "Entrée incomprise : utilisez « sourate:verset » (ex. 2:255) ou un "
        "numéro de sourate (ex. 2) dans la limite du corpus."
    ),
    "app.read_jump_verse": "Verset {ref} affiché (sourate {n}).",
    "app.read_jump_sura": "Sourate {n} — affichage des versets {a} à {b}.",
    "app.read_continuous": "Lecture continue de la sourate",
    "app.read_continuous_help": "Enchaîne la récitation verset par verset.",
    "app.read_media": "Lecteurs audio par verset",
    "app.read_media_help": (
        "Force l'affichage des lecteurs audio par verset, même pour les grandes "
        "plages (l'interface les masque au-delà de 50 versets pour rester réactive)."
    ),
    "app.read_playing": "Verset {a} en cours…",
    "app.read_stop": "Arrêter",
    "app.tab.bookmarks": "Favoris",
    "app.bm_title": "Versets mis de côté",
    "app.bm_caption": "Favoris conservés sur cet appareil (data/bookmarks.json).",
    "app.bm_count": "{n} verset(s) en favori.",
    "app.bm_empty": (
        "Aucun favori pour l'instant. Ajoutez-en avec le bouton sous un verset "
        "ou via une référence."
    ),
    "app.bm_add_ref": "Ajouter une référence",
    "app.bm_ref_ph": "ex. 2:255",
    "app.bm_add_btn": "Ajouter",
    "app.bm_added": "{ref} ajouté aux favoris.",
    "app.bm_bad_ref": "Référence invalide (format sourate:verset).",
    "app.bm_missing": "{ref} introuvable dans la base.",
    "app.bm_note": "Note",
    "app.bm_note_ph": "note personnelle (optionnel)",
    "app.bm_save_note": "Enregistrer la note",
    "app.bm_remove": "Retirer",
    "app.bm_removed": "{ref} retiré des favoris.",
    "app.bm_clear": "Vider les favoris",
    "app.bm_cleared": "Favoris vidés.",
    "app.bm_export": "Exporter en texte",
    "app.tab.cross": "Croisement",
    "app.cross_title": "Croisement de racines",
    "app.cross_caption": "Deux notions : où le texte les réunit-il ?",
    "app.cross_root_a": "Première racine",
    "app.cross_root_b": "Seconde racine",
    "app.cross_root_c": "Troisième racine (optionnel)",
    "app.cross_ph": "arabe ou Buckwalter",
    "app.cross_run": "Croiser",
    "app.cross_mode_pair": "Croiser deux racines",
    "app.cross_mode_co": "Racines co-occurrentes",
    "app.cross_result": "Versets réunissant les racines {roots} : {n}",
    "app.cross_none": "Aucun verset ne réunit ces racines.",
    "app.cross_notfound": "Racine introuvable : {r}",
    "app.cross_co_title": "Racines co-occurrentes",
    "app.cross_co_caption": "Avec quoi une racine apparaît-elle le plus souvent ?",
    "app.cross_co_root": "Racine",
    "app.cross_co_result": "Racines les plus souvent associées à {root}",
    "app.cross_co_none": "Aucune co-occurrence.",
    "app.cross_need_root": "Indiquez au moins une racine.",
    "app.donate_title": "Soutenir le projet",
    "app.donate_intro": (
        "Ce service est libre, sans publicité ni traçage. Un don, entièrement "
        "facultatif, aide à couvrir l'hébergement et le développement."
    ),
    "app.donate_paypal": "Faire un don via PayPal",
    "app.donate_card": "Don par carte bancaire",
    "app.donate_bitcoin": "Don en Bitcoin (BTC)",
    "app.donate_note": (
        "Le soutien est facultatif et n'ouvre accès à aucun contenu "
        "supplémentaire."
    ),
    "app.tab.learn": "Apprendre",
    "learn.title": "Apprendre le vocabulaire du Coran",
    "learn.caption": (
        "Répétition espacée : mémorisez les racines les plus fréquentes et "
        "révisez-les au bon moment."
    ),
    "learn.disabled": "Le module d'apprentissage est désactivé.",
    "learn.dashboard": "Tableau de bord",
    "learn.m_due": "À réviser",
    "learn.m_reviews_today": "Révisions aujourd'hui",
    "learn.m_new_today": "Nouveaux aujourd'hui",
    "learn.m_streak": "Jours d'affilée",
    "learn.m_mastered": "Racines maîtrisées",
    "learn.m_coverage": "Couverture du lexique fréquent",
    "learn.coverage_fmt": "{n} / {total} racines fréquentes maîtrisées",
    "learn.coverage_na": "Couverture non disponible.",
    "learn.goals_header": "Objectifs quotidiens",
    "learn.goal_new": "Nouveaux mots par jour",
    "learn.goal_review": "Révisions par jour",
    "learn.reminders": "Activer les rappels",
    "learn.reminders_help": "Affiche un rappel quand des cartes sont à réviser.",
    "learn.settings_saved": "Objectifs enregistrés.",
    "learn.start": "Commencer la révision",
    "learn.reviewing": "Révision en cours",
    "learn.progress": "Carte {i} / {n}",
    "learn.show_answer": "Voir la réponse",
    "learn.answer": "Réponse",
    "learn.again": "À revoir",
    "learn.hard": "Difficile",
    "learn.good": "Bien",
    "learn.easy": "Facile",
    "learn.no_due": (
        "Aucune carte à réviser pour l'instant. Revenez plus tard ou lancez "
        "un quiz."
    ),
    "learn.next_due": "Prochaine échéance : {when}",
    "learn.queue_empty": (
        "Aucune carte disponible. Ajoutez des mots depuis la lecture."
    ),
    "learn.finished": "Session terminée. Bravo !",
    "learn.quiz_title": "Quiz de contexte",
    "learn.quiz_intro": (
        "Choisissez le sens de la racine surlignée dans ce verset."
    ),
    "learn.quiz_root_title": "Reconnaissance de racine",
    "learn.quiz_root_intro": "À quelle racine appartient cette forme ?",
    "learn.quiz_root_prompt": "Racine de la forme {form} ({tr}) ?",
    "learn.quiz_context_prompt": "Sens de la racine {root} surlignée ?",
    "learn.quiz_submit": "Valider",
    "learn.quiz_correct": "Correct !",
    "learn.quiz_wrong": "Incorrect. Réponse : {ans}",
    "learn.quiz_another": "Autre question",
    "learn.quiz_none": "Pas assez de données pour générer un quiz.",
    "learn.add_card": "Ajouter à la révision",
    "learn.added": "Ajouté à la révision.",
    "learn.inspect_title": "Mot sélectionné",
    "learn.inspect_form": "Forme",
    "learn.inspect_root": "Racine",
    "learn.inspect_lemma": "Lemme",
    "learn.inspect_pos": "Catégorie grammaticale",
    "learn.inspect_gloss": "Glose",
    "learn.inspect_freq_form": "Cette forme : {n} fois",
    "learn.inspect_freq_lemma": "Ce lemme : {n} fois",
    "learn.inspect_freq_root": "Racine : {n} occurrences dans {v} versets",
    "learn.inspect_root_forms": "Autres formes de la racine",
    "learn.close": "Fermer",
    "learn.click_hint": (
        "Astuce : cliquez un mot d'un verset pour voir sa racine et sa "
        "fréquence."
    ),
    "learn.sort_verses": "Versets",
    "learn.words_clickable": "Mots cliquables",
    "learn.words_clickable_help": (
        "Rendre chaque mot des versets cliquable (ouvre la fiche du mot)."
    ),
    "learn.no_vocab": "Lexique indisponible.",
    "iqra.title": "Lire l'arabe — méthode Iqraʾ",
    "iqra.caption": (
        "Un parcours guidé : alphabet, voyelles, signes, lecture progressive, "
        "vocabulaire essentiel du Coran et nombres arabes."
    ),
    "iqra.choose_step": "Étape du parcours",
    "iqra.step1": "1 · Alphabet",
    "iqra.step2": "2 · Voyelles",
    "iqra.step3": "3 · Signes",
    "iqra.step4": "4 · Lecture",
    "iqra.step5": "5 · Vocabulaire",
    "iqra.step6": "6 · Nombres",
    "iqra.s1_title": "Alphabet arabe — les 28 lettres",
    "iqra.s1_desc": (
        "Chaque lettre a une forme isolée (seule) et des formes liées qui "
        "dépendent de sa place dans le mot. Le bouton « Écouter » lit son nom."
    ),
    "iqra.s1_legend": "Formes dans un mot : isolée · initiale · médiale · finale",
    "iqra.s1_note_nonconnect": (
        "Ces six lettres ne se rattachent jamais à la suivante : leur forme "
        "initiale égale leur forme isolée."
    ),
    "iqra.s2_title": "Voyelles — courtes (harakāt) et longues (moudoud)",
    "iqra.s2_desc": (
        "Une voyelle courte sonorise la consonne qui la porte ; une voyelle "
        "longue allonge la syllabe. Écoutez chaque combinaison, puis "
        "entraînez-vous."
    ),
    "iqra.s2_table_short": "Voyelles courtes — harakāt",
    "iqra.s2_table_long": "Voyelles longues — moudoud",
    "iqra.s2_exercise": "Entraînement : lisez la syllabe, puis vérifiez.",
    "iqra.s2_drill_hint": "Quelle transcription pour cette syllabe ?",
    "iqra.s2_check": "Vérifier",
    "iqra.s2_correct": "Correct !",
    "iqra.s2_wrong": "Non — c'était « {tr} ».",
    "iqra.s2_next": "Syllabe suivante",
    "iqra.s3_title": "Signes de lecture — soukoun, chaddah, tanwin",
    "iqra.s3_desc": (
        "Ces signes affinent la prononciation : aucune voyelle, consonne "
        "doublée, n final. Écoutez chaque mot-exemple, puis lisez à voix haute."
    ),
    "iqra.s3_role": "Rôle",
    "iqra.s4_title": "Lecture progressive — mots puis sourates",
    "iqra.s4_desc": (
        "Assemblez ce que vous savez : mots simples, expressions consacrées, "
        "puis de courtes sourates avec transcription phonétique et récitation."
    ),
    "iqra.s4_practice": "Passerelle vers le Coran — lisez ces sourates courtes",
    "iqra.s4_practice_hint": (
        "Chaque verset s'affiche en Uthmani avec sa récitation audio (bouton "
        "du lecteur) et sa transcription phonétique juste au-dessous : lisez "
        "lentement, puis écoutez."
    ),
    "iqra.s4_surah_fmt": "Sourate {n} — {name}",
    "iqra.s4_no_con": "Connexion aux données indisponible : passerelle Coran masquée.",
    "iqra.vocab_title": "Vocabulaire essentiel du Coran",
    "iqra.vocab_desc": (
        "Les racines les plus fréquentes du texte coranique : chaque carte "
        "montre le mot le plus représentatif, sa prononciation, son sens et "
        "une référence. « Écouter » lit le mot."
    ),
    "iqra.vocab_cov": (
        "Les {n} racines les plus fréquentes couvrent {pct} % des {total} "
        "mots racinisés du Coran."
    ),
    "iqra.vocab_search": "Filtrer les mots (arabe, prononciation, sens…)",
    "iqra.vocab_limit": "Nombre de cartes affichées",
    "iqra.vocab_root": "racine",
    "iqra.vocab_meta": "{occ} fois · {verses} versets · {ref}",
    "iqra.vocab_none": "Aucun mot ne correspond au filtre.",
    "iqra.vocab_no_con": "Connexion aux données indisponible : vocabulaire masqué.",
    "iqra.num_title": "Les nombres en arabe — de 1 à 1000",
    "iqra.num_desc": (
        "Chaque nombre associe son chiffre arabo-indien (٠١٢٣٤٥٦٧٨٩), son "
        "écriture en toutes lettres et sa prononciation : écoutez-la d'un "
        "clic sur « Écouter »."
    ),
    "iqra.num_units_title": "De 1 à 10",
    "iqra.num_tens_title": "Les dizaines — de 20 à 90",
    "iqra.num_tens_hint": (
        "Pour composer un nombre, unité puis dizaine reliées par « و » : "
        "« 21 » se dit « واحد وعشرون » (un et vingt)."
    ),
    "iqra.num_hundreds_title": "Les centaines — jusqu'à 1000",
    "iqra.num_hundreds_hint": (
        "La centaine se construit sur مِائَة ; 200 fait exception avec la "
        "forme duelle مِائَتَان. « 1000 » se dit أَلْف."
    ),
    "iqra.listen": "Écouter",
    "iqra.listen_ar": "Écouter la prononciation arabe",
}

_EN = {
    "app.title": "quranlab — intra-Qur'anic analysis",
    "app.subtitle": (
        "Strictly intra-Qur'anic search and analysis — text, structure, "
        "linguistics and roots. Without tafsir, hadith or post-Qur'anic "
        "interpretation."
    ),
    "app.choose_lang": "Display language",
    "app.prefs": "Preferences",
    "app.theme": "Visual theme",
    "app.audio": "Audio",
    "app.reciter": "Reciter",
    "app.reciter_help": "Verse-by-verse recitation (EveryAyah).",
    "app.show_audio": "Verse Qur'anic player",
    "app.show_tts": "Speech synthesis (TTS)",
    "app.tts_help": (
        "Reads each translation aloud via the browser engine (selectable voice "
        "and settings in the TTS parameters)."
    ),
    "app.caption_scope": (
        "Strictly intra-Qur'anic reading — without tafsir, hadith or "
        "post-Qur'anic interpretation."
    ),
    "app.suggest_title": "Suggestions",
    "app.suggest_body": (
        "QuranLab evolves with use. Ideas, inconsistencies, sources to add, new "
        "reciters or languages, UX improvements: **share them with us**."
    ),
    "app.write_us": "Write to us: {email}",
    "app.suggest_see_guide": "See the section of the same name in the getting-started guide.",
    "app.con": "Database connection failed",
    "app.none": "none",
    "app.word_surahs": "surahs",
    "app.word_verses": "verses",
    "app.word_words": "annotated words",
    "app.word_roots": "roots",
    "app.word_translations": "translations",
    "app.word_themes": "themes",
    "app.word_topics": "analysis topics",
    "app.corpus": "Corpus",
    "app.stat_surahs": "{s} surahs · {v} verses",
    "app.stat_words": "{m} annotated words · {r} distinct roots",
    "app.stat_translations": "{n} translations",
    "app.stat_themes": "{n} themes · {t} analysis topics",
    "app.tab.root": "Root",
    "app.tab.search": "Search",
    "app.tab.verse": "Compared verse",
    "app.tab.theme": "Themes",
    "app.tab.controv": "Misconceptions",
    "app.tab.concord": "Concordance",
    "app.root_title": "Root indexing",
    "app.root_placeholder": "Search in French or Arabic (e.g. mercy / رحمة)…",
    "app.root_caption": "Enter a root in Arabic (رحم) or in Buckwalter (rHm).",
    "app.root_label": "Root",
    "app.root_ctx": "Context (± verses)",
    "app.search_title": "Textual and multilingual search",
    "app.search_placeholder": "Search for a word in French or Arabic…",
    "app.input_lang": "Language",
    "app.search_term": "Term",
    "app.bridge_heading": "French → Arabic bridge",
    "app.bridge_none": (
        "No automatic match found for this term (lexicon, themes, corpus) — "
        "see the French textual results below."
    ),
    "app.bridge_query_root": "Query the original text by root",
    "app.bridge_limit": "Root occurrences to display",
    "app.bridge_note": "First {n} occurrences (limit set to {limit}).",
    "app.original_heading": "Original text (selected root)",
    "app.fr_occurrences": "French occurrences (translations)",
    "app.rows_verses": "{n} verse(s) — one display per verse.",
    "app.limit_100": "Limit reached: first 100 verses shown.",
    "app.hits_trans": "term present in {n} translation(s): {keys}",
    "app.verse_title": "Comparative display and similar verses",
    "app.verse_placeholder": "Search in French or Arabic (e.g. light / نور)…",
    "app.mode": "Mode",
    "app.mode_compare": "Compare two verses",
    "app.mode_similar": "Suggest similar verses",
    "app.compare_caption": (
        "Select two verses independently: they are shown side by side with "
        "their Arabic text, translations and roots."
    ),
    "app.verse_a": "Verse A",
    "app.verse_b": "Verse B",
    "app.verse_missing": "Verse {ref} not found.",
    "app.struct_title": "Thematic structure comparison (roots)",
    "app.common_roots": "{n} shared root(s): {roots}",
    "app.roots_of": "Roots of {ref} ({n}) — {roots}",
    "app.similar_caption": (
        "Enter a reference (sura:aya) to find its mirror verses, or a keyword "
        "(French or Arabic) for a root-proximity suggestion."
    ),
    "app.ref_input": "Reference verse (sura:aya) or keyword",
    "app.min_shared": "Minimum shared roots",
    "app.nb_suggestions": "Number of suggestions",
    "app.ref_verse": "Reference verse",
    "app.ref_format": "Expected format: sura:aya (e.g. 4:34)",
    "app.mirror_roots": "Roots of the verse ({n}): {roots}",
    "app.mirror_matches": "{n} similar verse(s)",
    "app.mirror_empty": (
        "No verse shares enough roots — lower the minimum shared-roots "
        "threshold."
    ),
    "app.mirror_label": "{ref}  ·  {n} shared roots ({pct}%)",
    "app.shared_roots_caption": "shared roots: {roots}",
    "app.no_roots_keyword": (
        "No usable root for “{q}” — try another keyword or a sura:aya reference."
    ),
    "app.keyword_roots": "Roots of keyword “{q}” ({n}): {roots}",
    "app.suggested_matches": "{n} suggested similar verse(s)",
    "app.theme_title": "Intra-Qur'anic thematic mapping",
    "app.theme_placeholder": "Search in French or Arabic (will also trigger the bridge)…",
    "app.theme_query": "Search a theme (label, description, root, term…)",
    "app.theme_query_ph": "e.g. salat, رحم, mercy, gold, orphans…",
    "app.category": "Category",
    "app.category_all": "All",
    "app.theme_count": (
        "{shown} theme(s) shown out of {total} · {cats} categories · "
        "{links} theme↔verse links."
    ),
    "app.theme_none": (
        "No theme matches — change the keyword or set the category back to “All”."
    ),
    "app.theme_pick": "Theme",
    "app.theme_pick_ph": "— Choose a theme to see its verses —",
    "app.theme_pick_wait": (
        "Select a theme above: the linked verses and their recitation will be "
        "shown here (nothing loads until a choice is made — the interface stays "
        "light)."
    ),
    "app.theme_catline": "Category: {cat} · Roots: {roots} · {n} verse(s){extra}",
    "app.theme_extra_ar": " · Arabic terms: {terms}",
    "app.theme_extra_fr": " · French terms: {terms}",
    "app.theme_sources": "sources: {src}",
    "app.theme_overview": "Overview of the {n} theme(s) shown",
    "app.overview_cat": "category",
    "app.overview_theme": "theme",
    "app.overview_key": "key",
    "app.overview_roots": "roots",
    "app.overview_verses": "verses",
    "app.data_en_note": (
        "Catalogue content (themes / misconceptions) is authored in French — "
        "the study source is kept as-is."
    ),
    "app.controv_title": "Textual analysis of misconceptions and controversies",
    "app.controv_placeholder": "Search in French or Arabic (e.g. woman / نساء)…",
    "app.controv_method": "Method: {m}",
    "app.controv_count": "{n} topics — descriptive textual analysis, no doctrinal conclusion.",
    "app.controv_pick": "Topic",
    "app.controv_pick_ph": "— Choose a topic to see its analysis —",
    "app.controv_wait": (
        "Choose a topic from the list: lexical recurrence, polysemy and key "
        "verses will be shown here."
    ),
    "app.controv_question": "Question asked: {q}",
    "app.controv_framing": "Intra-Qur'anic note: {f}",
    "app.controv_read": "Suggested reading: {t}",
    "app.recurrence_title": "Lexical recurrence across the whole corpus",
    "app.rec_type": "type",
    "app.rec_item": "item",
    "app.rec_detail": "key",
    "app.rec_occ": "occurrences",
    "app.rec_verses": "verses",
    "app.polysemy_title": "Polysemy — every form of a single root",
    "app.polysemy_form": "Root {root} [{bw}] — {n} occurrences / {v} verses",
    "app.polysemy_forms": "Forms encountered: {forms}",
    "app.poly_verse": "verse",
    "app.poly_form": "form",
    "app.poly_context": "context",
    "app.key_verses": "Key verses — Arabic text and plural translations",
    "app.verse_missing_key": "Verse not found: {ref}",
    "app.concord_title": "Internal concordance — “the Qur'an explains itself by the Qur'an”",
    "app.concord_placeholder": "Search in French or Arabic to build a concordance…",
    "app.concord_caption": (
        "Cross-referencing verses by shared roots: concordance by notion, and "
        "mirror verses of a reference verse."
    ),
    "app.mode_mirror": "Mirror verse",
    "app.mode_notion": "Concordance by notion",
    "app.mirror_ref": "Reference verse (sura:aya)",
    "app.min_shared_mirror": "Minimum shared roots",
    "app.nb_mirror": "Number of mirror verses",
    "app.mirror_matches_n": "{n} mirror verse(s)",
    "app.criterion": "Criterion",
    "app.crit_root": "Root",
    "app.crit_term": "Arabic term",
    "app.root_input": "Root (Arabic or Buckwalter)",
    "app.arabic_term": "Arabic term",
    "app.concord_line": (
        "Concordance {kind}: {label} `[{detail}]` — {n} occurrence(s) in "
        "{v} verse(s)"
    ),
    "app.no_result": "No result.",
    "ui.type.root": "root",
    "ui.type.term": "term",
    "ui.lang.fr": "French",
    "ui.lang.ar": "Arabic",
    "ui.lang.en": "English",
    "ui.listen": "Listen",
    "ui.pause": "Pause",
    "ui.stop": "Stop",
    "ui.tts_unavail": "TTS unavailable",
    "ui.play": "Read",
    "ui.listen_title": "Play / Pause",
    "ui.stop_title": "Stop",
    "ui.tts_title": "Read aloud ({locale})",
    "ui.tts_button": "Listen in English",
    "ui.speak_tooltip": "Speech synthesis ({locale})",
    "ui.tts_settings": "Speech synthesis settings",
    "ui.rate": "Rate",
    "ui.rate_help": "Reading speed: 1.0 = normal.",
    "ui.pitch": "Pitch (tone)",
    "ui.pitch_help": "Voice depth: 1.0 = normal.",
    "ui.voice_hint": "If reading spells out letters, pick a {lang} voice below then click *Apply*.",
    "ui.vl_label": "Speech voice (prefer {lang} voices)",
    "ui.apply": "Apply",
    "ui.test_voice": "Test",
    "ui.voice_none": (
        'No "{lang}" voice found in this browser: the text may be '
        "mispronounced or spelled out letter by letter."
    ),
    "ui.voice_few": (
        'Only one "{lang}" voice detected. For a more natural result, open the '
        "site in Microsoft Edge (free online “Natural” voices) or install more "
        "voices in Windows: Settings → Time & language → Speech."
    ),
    "ui.voice_tip": (
        "Tip: Microsoft Edge provides very smooth French “Natural” voices, with "
        "no installation."
    ),
    "ui.tts_external_on": (
        "Speech synthesis provided by a configured external service (voice "
        "outside the browser)."
    ),
    "ui.piper_engine": (
        "Engine: Piper — offline neural voices, several to choose from."
    ),
    "ui.piper_voice": "Voice",
    "ui.piper_voice_help": (
        "Pick one of several voices, then click *Test*."
    ),
    "ui.piper_first_use": (
        "First use downloads the model (a few MB)."
    ),
    "ui.piper_unavailable": (
        "Piper is not installed: reading through the browser voices."
    ),
    "ui.tts_generating": "Generating voice…",
    "ui.tts_fail": "Synthesis failed: {err}",
    "ui.sample_fr": (
        "Bonjour. Ceci est un test de lecture en français : le Coran "
        "s'explique par le Coran."
    ),
    "ui.sample_en": (
        "Hello. This is an English reading test: the Qur'an explains itself "
        "by the Qur'an."
    ),
    "ui.auto": "Auto",
    "ui.auto_opt": "Auto (best {lang} voice)",
    "ui.other_voices": "Other voices",
    "ui.loading_voices": "Loading voices…",
    "ui.no_tts": "Speech synthesis unavailable in this browser.",
    "ui.voices_found": "{n} {lang} voice(s) detected",
    "ui.voice_selected": " — selected: {name}",
    "ui.unavailable": "(not found)",
    "ui.then_listen": ". Then hit “{label}” in a verse.",
    "ui.no_translation": "No translation available.",
    "ui.root_notfound": "Root not found: {q}",
    "ui.root_header": "**Root {ar}** `[{bw}]` — {n} occurrence(s) in {v} verse(s)",
    "ui.limit_1000": "Limit reached: first 1000 occurrences shown.",
    "ui.lemma_fmt": "{form} ({trans}, {pos}, lemma {lemma})",
    "ui.counter": "{n} occurrence(s) found in {v} verse(s)",
    "ui.uni_label": "Universal search (French or Arabic)",
    "ui.uni_placeholder": "Search in French or Arabic (e.g. mercy / رحمة)…",
    "ui.spinner": "Searching the whole Qur'an…",
    "ui.ref_detected": "Direct reference recognized — displaying verse {ref}.",
    "ui.ref_label": "Verse {ref} (direct reference)",
    "ui.ref_missing": "Verse {ref} not found in the corpus.",
    "ui.no_match": (
        "No match found for “{q}”. Try another word (French or Arabic) or a "
        "root (e.g. رحم or rHm)."
    ),
    "ui.success_text": "**{count}** for “{q}” (Arabic textual search).",
    "ui.success_bridge": "**{count}** — from {roots} root(s) linked to “{q}”.",
    "ui.success_no_root": (
        "No root linked automatically, but “{q}” appears in {n} verse(s) "
        "(translations)."
    ),
    "ui.also_trans": "“{q}” also appears in the translations of {n} verse(s).",
    "ui.bridge_expander": "French → Arabic matches ({n})",
    "ui.table_fr": "French",
    "ui.table_root": "root",
    "ui.table_bw": "buckwalter",
    "ui.table_verses": "verses",
    "ui.table_occ": "occurrences",
    "ui.table_source": "source",
    "ui.limit_rows": "Limit reached: {shown} verses shown out of {total}.",
    "ui.limit_props": "First {n} occurrences (set limit: {limit}).",
    "ui.verses_where": "Verses where “{q}” appears in translations ({n})",
    "ui.pick_root": "Root to explore",
    "ui.pick_root_fmt": "{ar} [{bw}] — {v} verses",
    "ui.occ_limit": "Occurrences to show",
    "ui.surah": "Surah",
    "ui.verse": "Verse",
    "ui.bookmark_add": "☆ Add to bookmarks",
    "ui.bookmark_remove": "★ Bookmarked",
    "app.tab.read": "Read the Quran Iqra",
    "app.read_title": "Read the Quran Iqra",
    "app.read_caption": (
        "Surah by surah, verse by verse — Arabic text, translations and "
        "recitation."
    ),
    "app.read_surah": "Surah",
    "app.read_surah_fmt": "{n}. {name} — {count} verses",
    "app.read_from": "From verse",
    "app.read_to": "to verse",
    "app.read_range": "Verse range to display",
    "app.read_prev": "Previous",
    "app.read_next": "Next",
    "app.read_all": "Whole surah",
    "app.read_showing": "Verses {a} to {b} of {n}.",
    "app.read_jump": "Jump to a surah or verse",
    "app.read_jump_ph": "e.g. 2:255 · 2.255 · 2/255 · 2 255 (or #: 2)",
    "app.read_jump_bad": (
        "Unrecognized input: use “surah:verse” (e.g. 2:255) or a surah number "
        "(e.g. 2) within the corpus bounds."
    ),
    "app.read_jump_verse": "Verse {ref} displayed (surah {n}).",
    "app.read_jump_sura": "Surah {n} — showing verses {a} to {b}.",
    "app.read_continuous": "Continuous recitation of the surah",
    "app.read_continuous_help": "Plays the recitation verse by verse.",
    "app.read_media": "Per-verse audio players",
    "app.read_media_help": (
        "Force the per-verse audio players to show even on large ranges (the UI "
        "hides them beyond 50 verses to stay responsive)."
    ),
    "app.read_playing": "Verse {a} playing…",
    "app.read_stop": "Stop",
    "app.tab.bookmarks": "Bookmarks",
    "app.bm_title": "Verses set aside",
    "app.bm_caption": "Bookmarks kept on this device (data/bookmarks.json).",
    "app.bm_count": "{n} bookmarked verse(s).",
    "app.bm_empty": (
        "No bookmark yet. Add one with the button under a verse or with a "
        "reference."
    ),
    "app.bm_add_ref": "Add a reference",
    "app.bm_ref_ph": "e.g. 2:255",
    "app.bm_add_btn": "Add",
    "app.bm_added": "{ref} added to bookmarks.",
    "app.bm_bad_ref": "Invalid reference (format sura:verse).",
    "app.bm_missing": "{ref} not found in the database.",
    "app.bm_note": "Note",
    "app.bm_note_ph": "personal note (optional)",
    "app.bm_save_note": "Save the note",
    "app.bm_remove": "Remove",
    "app.bm_removed": "{ref} removed from bookmarks.",
    "app.bm_clear": "Clear bookmarks",
    "app.bm_cleared": "Bookmarks cleared.",
    "app.bm_export": "Export as text",
    "app.tab.cross": "Crossing",
    "app.cross_title": "Root crossing",
    "app.cross_caption": "Two notions: where does the text bring them together?",
    "app.cross_root_a": "First root",
    "app.cross_root_b": "Second root",
    "app.cross_root_c": "Third root (optional)",
    "app.cross_ph": "Arabic or Buckwalter",
    "app.cross_run": "Cross",
    "app.cross_mode_pair": "Cross two roots",
    "app.cross_mode_co": "Co-occurring roots",
    "app.cross_result": "Verses bringing together the roots {roots}: {n}",
    "app.cross_none": "No verse brings these roots together.",
    "app.cross_notfound": "Root not found: {r}",
    "app.cross_co_title": "Co-occurring roots",
    "app.cross_co_caption": "What does a root most often appear with?",
    "app.cross_co_root": "Root",
    "app.cross_co_result": "Roots most often associated with {root}",
    "app.cross_co_none": "No co-occurrence.",
    "app.cross_need_root": "Provide at least one root.",
    "app.donate_title": "Support the project",
    "app.donate_intro": (
        "This service is free, with no advertising and no tracking. A donation, "
        "entirely optional, helps cover hosting and development."
    ),
    "app.donate_paypal": "Donate via PayPal",
    "app.donate_card": "Donate by card",
    "app.donate_bitcoin": "Donate in Bitcoin (BTC)",
    "app.donate_note": (
        "Support is optional and grants access to no additional content."
    ),
    "app.tab.learn": "Learn",
    "learn.title": "Learn Qur'anic vocabulary",
    "learn.caption": (
        "Spaced repetition: memorise the most frequent roots and review them "
        "at the right time."
    ),
    "learn.disabled": "The learning module is disabled.",
    "learn.dashboard": "Dashboard",
    "learn.m_due": "Due",
    "learn.m_reviews_today": "Reviews today",
    "learn.m_new_today": "New today",
    "learn.m_streak": "Day streak",
    "learn.m_mastered": "Mastered roots",
    "learn.m_coverage": "Frequent-lexicon coverage",
    "learn.coverage_fmt": "{n} / {total} frequent roots mastered",
    "learn.coverage_na": "Coverage unavailable.",
    "learn.goals_header": "Daily goals",
    "learn.goal_new": "New words per day",
    "learn.goal_review": "Reviews per day",
    "learn.reminders": "Enable reminders",
    "learn.reminders_help": "Show a reminder when cards are due.",
    "learn.settings_saved": "Goals saved.",
    "learn.start": "Start review",
    "learn.reviewing": "Review in progress",
    "learn.progress": "Card {i} / {n}",
    "learn.show_answer": "Show answer",
    "learn.answer": "Answer",
    "learn.again": "Again",
    "learn.hard": "Hard",
    "learn.good": "Good",
    "learn.easy": "Easy",
    "learn.no_due": (
        "No cards due right now. Come back later or take a quiz."
    ),
    "learn.next_due": "Next due: {when}",
    "learn.queue_empty": (
        "No card available. Add words from reading."
    ),
    "learn.finished": "Session complete. Well done!",
    "learn.quiz_title": "Context quiz",
    "learn.quiz_intro": (
        "Choose the meaning of the highlighted root in this verse."
    ),
    "learn.quiz_root_title": "Root recognition",
    "learn.quiz_root_intro": "Which root does this form belong to?",
    "learn.quiz_root_prompt": "Root of the form {form} ({tr})?",
    "learn.quiz_context_prompt": "Meaning of the highlighted root {root}?",
    "learn.quiz_submit": "Submit",
    "learn.quiz_correct": "Correct!",
    "learn.quiz_wrong": "Wrong. Answer: {ans}",
    "learn.quiz_another": "Another question",
    "learn.quiz_none": "Not enough data to build a quiz.",
    "learn.add_card": "Add to review",
    "learn.added": "Added to review.",
    "learn.inspect_title": "Selected word",
    "learn.inspect_form": "Form",
    "learn.inspect_root": "Root",
    "learn.inspect_lemma": "Lemma",
    "learn.inspect_pos": "Part of speech",
    "learn.inspect_gloss": "Gloss",
    "learn.inspect_freq_form": "This form: {n} times",
    "learn.inspect_freq_lemma": "This lemma: {n} times",
    "learn.inspect_freq_root": "Root: {n} occurrences in {v} verses",
    "learn.inspect_root_forms": "Other forms of the root",
    "learn.close": "Close",
    "learn.click_hint": (
        "Tip: click a word in a verse to see its root and frequency."
    ),
    "learn.sort_verses": "Verses",
    "learn.words_clickable": "Clickable words",
    "learn.words_clickable_help": (
        "Make every word in verses clickable (opens the word card)."
    ),
    "learn.no_vocab": "Lexicon unavailable.",
    "iqra.title": "Read Arabic — Iqraʾ method",
    "iqra.caption": (
        "A guided path: alphabet, vowels, signs, progressive reading, "
        "essential Qur'an vocabulary and Arabic numbers."
    ),
    "iqra.choose_step": "Course step",
    "iqra.step1": "1 · Alphabet",
    "iqra.step2": "2 · Vowels",
    "iqra.step3": "3 · Signs",
    "iqra.step4": "4 · Reading",
    "iqra.step5": "5 · Vocabulary",
    "iqra.step6": "6 · Numbers",
    "iqra.s1_title": "Arabic alphabet — the 28 letters",
    "iqra.s1_desc": (
        "Each letter has an isolated form (alone) and linked forms that "
        "depend on its position in the word. The 'Listen' button reads its "
        "name."
    ),
    "iqra.s1_legend": "Forms in a word: isolated · initial · medial · final",
    "iqra.s1_note_nonconnect": (
        "These six letters never bind to the next one: their initial form "
        "equals their isolated form."
    ),
    "iqra.s2_title": "Vowels — short (harakāt) and long (moudoud)",
    "iqra.s2_desc": (
        "A short vowel voices the consonant that carries it; a long vowel "
        "stretches the syllable. Listen to each combination, then practice."
    ),
    "iqra.s2_table_short": "Short vowels — harakāt",
    "iqra.s2_table_long": "Long vowels — moudoud",
    "iqra.s2_exercise": "Practice: read the syllable, then check.",
    "iqra.s2_drill_hint": "Which transliteration for this syllable?",
    "iqra.s2_check": "Check",
    "iqra.s2_correct": "Correct!",
    "iqra.s2_wrong": "No — it was “{tr}”.",
    "iqra.s2_next": "Next syllable",
    "iqra.s3_title": "Reading signs — sukun, shadda, tanwin",
    "iqra.s3_desc": (
        "These signs refine your pronunciation: no vowel, doubled consonant, "
        "final n. Listen to each example word, then read aloud."
    ),
    "iqra.s3_role": "Role",
    "iqra.s4_title": "Progressive reading — words then surahs",
    "iqra.s4_desc": (
        "Assemble what you know: simple words, set phrases, then short surahs "
        "with phonetic transliteration and recitation."
    ),
    "iqra.s4_practice": "Bridge to the Qur'an — read these short surahs",
    "iqra.s4_practice_hint": (
        "Each verse shows in Uthmani with its audio recitation (player "
        "button) and its phonetic transliteration right below: read slowly, "
        "then listen."
    ),
    "iqra.s4_surah_fmt": "Surah {n} — {name}",
    "iqra.s4_no_con": "Data connection unavailable: Qur'an bridge hidden.",
    "iqra.vocab_title": "Essential Qur'an vocabulary",
    "iqra.vocab_desc": (
        "The most frequent roots of the Qur'anic text: each card shows the "
        "most representative word, its pronunciation, its meaning and a "
        "reference. 'Listen' reads the word."
    ),
    "iqra.vocab_cov": (
        "The {n} most frequent roots cover {pct} % of the {total} rooted "
        "words of the Qur'an."
    ),
    "iqra.vocab_search": "Filter words (Arabic, pronunciation, meaning…)",
    "iqra.vocab_limit": "Number of cards shown",
    "iqra.vocab_root": "root",
    "iqra.vocab_meta": "{occ} times · {verses} verses · {ref}",
    "iqra.vocab_none": "No word matches the filter.",
    "iqra.vocab_no_con": "Data connection unavailable: vocabulary hidden.",
    "iqra.num_title": "Arabic numbers — from 1 to 1000",
    "iqra.num_desc": (
        "Each number pairs its Arabic-Indic digit (٠١٢٣٤٥٦٧٨٩), its spelling "
        "in full letters and its pronunciation: listen with a click on "
        "'Listen'."
    ),
    "iqra.num_units_title": "From 1 to 10",
    "iqra.num_tens_title": "The tens — from 20 to 90",
    "iqra.num_tens_hint": (
        "To compose a number, unit then ten joined by 'و': '21' is said "
        "'واحد وعشرون' (one and twenty)."
    ),
    "iqra.num_hundreds_title": "The hundreds — up to 1000",
    "iqra.num_hundreds_hint": (
        "The hundred is built on مِائَة; 200 is the exception with the dual "
        "form مِائَتَان. '1000' is أَلْف."
    ),
    "iqra.listen": "Listen",
    "iqra.listen_ar": "Listen to Arabic pronunciation",
}

# --- API ------------------------------------------------------------------
_CATALOG = {"fr": _FR, "en": _EN}


def lang() -> str:
    """Langue active ('fr' ou 'en')."""
    value = st.session_state.get(LANG_KEY, DEFAULT) or DEFAULT
    return value if value in ("fr", "en") else DEFAULT


def set_lang(value: str) -> None:
    st.session_state[LANG_KEY] = value if value in ("fr", "en") else DEFAULT


def t(key: str, **fmt) -> str:
    """Traduit une clé dans la langue active (repli : français)."""
    text = _CATALOG[lang()].get(key) or _FR.get(key) or key
    if fmt:
        try:
            return text.format(**fmt)
        except (KeyError, IndexError):
            return text
    return text


def ui_locale() -> str:
    """Locale de la langue d'interface pour la synthèse vocale."""
    return "fr-FR" if lang() == "fr" else "en-US"


def ui_lang_prefix() -> str:
    return lang()


def keys_fr() -> set:
    return set(_FR)


def keys_en() -> set:
    return set(_EN)


def sidebar_language_selector() -> None:
    """Sélecteur de langue d'interface (barre latérale)."""
    st.radio(
        "Langue d'affichage" if lang() == "fr" else "Display language",
        ["fr", "en"],
        index=0 if lang() == "fr" else 1,
        format_func=lambda code: "Français" if code == "fr" else "English",
        key=LANG_KEY,
        help=(
            "Le site entier bascule dans une seule langue (interface + "
            "traductions de versets) — pas de mélange."
            if lang() == "fr" else
            "The whole site switches to a single language (interface + verse "
            "translations) — no mixing."
        ),
    )