# quranlab

**Local** tool for research and analysis that is **strictly intra-Quranic**.
The starting point is always the **Arabic text** (root, morphology), with a
comparative display of translations (French and English).

[**Français**](README.md) · English

No tafsir, no hadith, no post-Quranic traditional interpretation: the Quran is
illuminated by the Quran.

---

## 1. Project structure

```
quran-lab/
├─ app.py                     # Local web interface (Streamlit)
├─ requirements.txt           # Streamlit (the rest = standard library)
├─ README.md                  # Documentation (Français)
├─ README.en.md               # Documentation (English)
├─ data/                      # created by `init`
│  ├─ raw/                    # raw downloaded sources (JSON + morphology)
│  └─ quran.db                # generated SQLite database
├─ quranlab/                  # the core (no external dependency)
│  ├─ config.py               # paths + data sources
│  ├─ buckwalter.py           # Buckwalter <-> Arabic, transliteration, normalization
│  ├─ download.py             # source download
│  ├─ build.py                # schema + SQLite build
│  ├─ db.py                   # SQLite connection
│  ├─ search.py               # engine: text, roots, verses, themes, reference
│  ├─ ui.py                   # shared views: verses, tables, universal search
│  ├─ theme.py                # Light / Medium / Dark palettes
│  ├─ i18n.py                 # FR/EN translations (key parity)
│  ├─ cache.py                # st.cache_data wrappers (roots, words, surahs)
│  ├─ onboarding.py           # getting-started guide (sidebar modal)
│  ├─ bookmarks.py            # bookmarks (data/bookmarks.json)
│  ├─ learn_ui.py             # "Learn" tab (SRS dashboard)
│  ├─ learning.py             # card & goal persistence
│  ├─ srs.py                  # spaced repetition (simplified SM-2)
│  ├─ quiz.py                 # context / root-recognition quiz
│  ├─ vocab.py                # word card (form, root, gloss, frequency)
│  ├─ iqra.py                 # reading-course data (letters, vowels, signs, numbers)
│  ├─ iqra_ui.py              # "Read the Quran Iqra" tab (7 steps)
│  ├─ asma.py                 # 99 Names of Allah (etymological data + filter)
│  ├─ pwa.py                  # installable app (manifest, icons, metadata)
│  ├─ tts.py                  # text-to-speech (Piper + browser fallback)
│  ├─ themes.json             # thematic maps (salat, wudu', ...)
│  ├─ lexicon_fr.json         # FR lexicon → roots (bridge, 86 entries)
│  ├─ controversies.json      # misconceptions / controversies (12 topics)
│  ├─ cli.py                  # command-line interface
│  └─ __main__.py
├─ static/                    # served assets (PWA manifest + PNG icons)
│  ├─ manifest.webmanifest
│  └─ icons/                  # 192 / 512 / maskable / apple-touch-icon
└─ tests/                     # 18 unittest files: buckwalter, search, i18n,
                              # theme, TTS, iqra, asma, onboarding, SRS, bookmarks, PWA…
```

## 2. Getting started

```powershell
# 1. (optional) virtual environment
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 2. web interface dependency (the core has none)
pip install -r requirements.txt

# 3. download sources + build the SQLite database
python -m quranlab init

# 4. local web interface
streamlit run app.py
```

## 3. Command line

```powershell
python -m quranlab root رحم              # occurrences of a root (Arabic)
python -m quranlab root rHm --context 1  # same in Buckwalter, with context
python -m quranlab search "الرحمن" --lang ar
python -m quranlab search "mercy" --lang en --translation en.sahih
python -m quranlab bridge "patience"       # French → Arabic root
python -m quranlab verse 5:6             # verse + translations + word-by-word
python -m quranlab theme salat           # thematic map
python -m quranlab themes                # list of predefined themes
```

## 4. SQLite database schema

| Table | Role |
|---|---|
| `surahs` | 114 surahs: transliterated, Arabic, English name, revelation, verse count |
| `verses` | **uthmani** text, simple text and normalized text (without diacritics) |
| `translations` | translation catalog (key, author, language) |
| `translation_verses` | verse-by-verse translation + normalized version |
| `words` | **one row per word**: Arabic form, transliteration, **root**, lemma, POS |
| `segments` | fine morphological split (prefix / root / suffix) |

`words.root_buckwalter` / `root_arabic` / `root_norm` carry the root-based
indexing; `segments.features` preserves the full corpus annotation.

## 5. Data sources (public, verifiable)

- **Uthmani Arabic text**: `ara-quranuthmanihaf` (King Fahd Complex),
  via the *Quran API* (jsDelivr mirror) — see `config.py`.
- **Simple (imla'i) text**: `ara-quransimple`, the word alignment base.
- **French translations**: Muhammad Hamidullah, Rashid Maash,
  Islamic Foundation (Montada).
- **English translations**: Saheeh International (Umm Muhammad),
  Marmaduke Pickthall.
- **Morphology & roots**: *Quranic Arabic Corpus* v0.4 (Kais Dukes, GPL),
  annotated on the verified Tanzil text.

> Note: Blachère and Masson are under copyright and cannot be freely
> distributed. The selected translations are literal and without a doctrinal
> apparatus. A local translation (file `{chapter, verse, text}`) can be added by
> registering it in `config.TRANSLATIONS`; its `language` (`fr` / `en`) also
> drives the text-to-speech voice (Piper: **6 French** and 4 English voices to
> choose from — male, female, neutral — plus speed in the TTS settings; falls
> back to the browser voices if Piper is not installed).

## 6. Thematic mapping (`quranlab/themes.json`)

The file contains **164 themes** spread over **10 categories**, each anchored on
one or more **Arabic roots**. The `_meta` key lists the category order.

```json
"misericorde": {
  "category": "Ethics and Behaviour",
  "label": "Mercy (ar-raḥma)",
  "description": "Root r-ḥ-m: compassion, clemency.",
  "roots": ["رحم"],
  "terms_ar": ["الرحمن", "الرحيم"],
  "terms_fr": ["misericorde"]
}
```

- `roots`: **primary reference** — roots written in Arabic (or Buckwalter),
  automatically resolved against the database (`words.root_norm`).
- `terms_ar` / `terms_fr`: non-root forms or translations (optional).
- `category`: one of the axes listed in `_meta.categories`.

**Adding a theme**: copy a block, change the key and the roots. It appears
automatically in the CLI (`python -m quranlab themes`) and in the Streamlit
dropdown (the *Themes* tab), grouped by category. To verify that a root exists,
the command `python -m quranlab root <root>` or the *Root* tab serves as a check.

**Tolerant name resolution**: the CLI (`theme <name>`) accepts the exact key
(`priere`) **or** a common variant. The input is searched (beyond 4 characters)
in the key, the label and the fr/ar terms, and is retained only if it designates
a single theme. Thus `python -m quranlab theme salat` finds `priere` (label
"aṣ-ṣalāt"), `zakat` finds `aumone`, `hajj` finds `pelerinage`. In case of
ambiguity or absence, the list of available themes is shown
(`search.resolve_theme_key()`).

**Themes tab (app)**: all 164 themes are accessible — full-text search (label,
description, key, Arabic root **or** Buckwalter, fr/ar terms), category filter
("All" by default), **per-theme verse counter** (computed once then cached,
invalidated if `themes.json` changes) and an overview table of all filtered
themes. The sidebar shows corpus figures (surahs, verses, words, roots, themes,
topics).

## 7. Multilingual search and the French → Arabic bridge (the *Search* tab)

The *Search* tab offers two modes (radio **French** by default):

- **French**: a **linguistic bridge** (`search.french_bridge()`) merges three
  sources of matches, deduplicated by root:
  1. **lexicon** — `quranlab/lexicon_fr.json` (86 common entries: FR word →
     triliteral roots verified in the database);
  2. **themes** — FR terms of the 164 themes (`terms_fr`);
  3. **corpus** — distributionally inferred roots (lift: frequent in the French
     verses touched, rare elsewhere).

  A table shows the proposals (Arabic root, Buckwalter, verse count,
  occurrences, source); a dropdown then queries the **original text** by chosen
  root (display limit slider). Direct entry of a root (Arabic or Buckwalter,
  e.g. `rHm`) is resolved immediately. French results are **deduplicated: one
  display per verse**, with the list of translations containing the term.
- **Arabic**: direct search in the original text.

`search.search_french()` groups by verse (`GROUP BY sura, aya`); the per-translation
detail remains available via `search.french_matches_rows()` (used by the CLI).
The root rendering is shared between the *Root* tab and the bridge
(`render_root_results`): **one expander per verse**, all forms of the root are
listed there.

### 7.1 Bilingual universal search bar (in every tab)

Every tab (*Root*, *Search*, *Compared verse*, *Themes*, *Misconceptions*,
*Concordance*) opens on a **universal search bar**
(`quranlab/ui.py`, `ui.universal_search()`) which accepts **either French or
Arabic**. The language is detected automatically
(`ui.occurrence_summary()`, via `buckwalter.is_arabic`):

- **French input** (any word) → **bridge** to the roots
  `search.french_bridge()` (lexicon → themes → corpus inference);
- **Arabic input** → if the word is a **root** (`صبر`, `رحم`), a root search;
  otherwise **textual search** (`search.arabic_occurrence_summary()`) with exact
  occurrence counting in `verses.text_simple_norm`.

In all cases the interface **systematically displays the total number of
occurrences**: **"N occurrence(s) found in Y verse(s)"**
(`ui.counter_label()`). For French queries the count is computed as a
**union** of roots (`search.roots_union_stats()`): a verse containing several
target roots is counted only once. The verses are then displayed with context
(root selector + display limit, or a textual list for Arabic), with a collapsible
fallback listing the French occurrences in the translations.

The bar also accepts a **direct verse reference**: `2:255`, `2.255`, `2/255`
or `2 255` — the separators **colon, dot, slash and space** are equivalent —
immediately display the matching verse (Arabic text, phonetic transliteration
and the translations of the active language) without going through the textual
search (`search.parse_ref()`, regex `^\s*(\d{1,3})\s*[:./\s]\s*(\d{1,3})\s*$`).
Any input that is not a valid reference (out of bounds, missing verse… or plain
text) falls back to the classic search.

The view components (`html_table`, `render_verse`, `render_verses`,
`render_root_results`, `universal_search`, `verse_picker`) are **shared in
`quranlab/ui.py`**; `app.py` only orchestrates the tabs. No extra visual theme
is required: the results inherit the current charter (Light / Medium blue-grey /
Dark).

### 7.2 The *Compared verse* tab — two modes

Re-architected (`app.py`, the *Compared verse* tab) around a reusable
`ui.verse_picker()` selector (list of surahs + verse number):

- **Mode "Compare two verses"**: two **independent** A and B selectors, shown
  **side by side** (uthmani Arabic text + multiple translations). A synthesis
  compares their **thematic structure**: roots of each verse, **common** roots
  and their count (`search.verse_root_set()`).
- **Mode "Suggest similar verses"**: from a **reference** `sura:aya` → verses in
  **mirror** by shared roots (`search.mirror_verses()`); from a **keyword**
  (French or Arabic) → bridge to the roots then lexical proximity
  (`search.similar_verses_by_roots()`, roots derived by
  `search.top_roots_in_verses()` for an Arabic word). Adjustable thresholds
  (minimum common roots, number of suggestions).

## 8. Misconceptions, controversies and practices (`quranlab/controversies.json`)

A **strictly descriptive and intra-Quranic** section (the *Misconceptions* tab).
Each topic contains: `question`, `framing` (methodological note, without
doctrinal conclusion), `roots`, `terms_ar`, `key_verses`, `context_hint`, and
optionally `root_polysemy` (roots for which **all forms** are shown).

The app computes: **lexical recurrence**, **polysemy** (all forms of a root and
their contexts), then shows the key verses in Arabic with all translations. No
tafsir, hadith or traditional opinion.

12 topics: status of women/gender, marital correction (root ḍ-r-b), constraint
and freedom, servitude and emancipation (*fakk raqaba*), marriage and maturity
(*rushd*), modalities of prayer (postures + recitation), war and peace,
punishments, clothing and modesty (*khumur* / *jalābīb*), freedom of belief,
People of the Book, alcohol and gambling.

## 9. Internal concordance / mirror verses (the *Concordance* tab)

Purely lexical crossing of verses — "the Quran explains the Quran":

- **Mirror verse**: from a verse (`sura:aya`), `search.mirror_verses()`
  computes the set of its roots, then ranks the other verses by number of
  **common roots** (and overlap ratio). Each mirror is shown with its text and
  translations.
- **Concordance by concept**: `search.concordance()` groups all occurrences of a
  **root** or a **term** with multiple translations.

Functions: `search.verse_root_set()`, `search.mirror_verses()`,
`search.concordance()`, `search.root_polysemy()`.

## 10. Methodological principles

- Search by **root** (triliteral/quadriliteral) as the primary axis.
- Arabic normalization (diacritics, alif, alif maqsura) for robust searches
  without losing the original form on display.
- Systematic display of **context** (verses before/after) to let the text
  comment itself.
- **Thematic** aggregation by crossing roots and terms.

## 11. Deployment (Streamlit Community Cloud)

1. Push the project to a **public** GitHub repository.
2. On https://share.streamlit.io → *New app* → choose the repo, branch `main`,
   and **Main file path = `app.py`**.
3. Deploy. No secret is required.

**Database online**: `data/quran.db` is ignored by git. On first launch,
`app.py` calls `build.ensure_db()` which **downloads the sources and builds the
database automatically** (≈30 s, once per container, cached by
`@st.cache_resource`). Paths are strictly relative (`config.py` is based on
`__file__`), so nothing is Windows-specific.

> For an instant start, the database can be versioned: comment out the
> `data/quran.db` line in `.gitignore`, then commit `data/quran.db` (~29 MB).

Useful deployment files: `requirements.txt` (streamlit + pandas),
`.streamlit/config.toml` (theme), `.gitignore`.

> **Deliberately lightweight dependencies.** `piper-tts` (offline neural voices)
> is **not** in `requirements.txt`: it is distributed as source only and needs a
> C++ build (CMake + `espeak-ng`) that **makes installation fail** on Streamlit
> Community Cloud (the app would stay stuck on *"Your app is in the oven"*). The
> app automatically falls back to the browser voices (Web Speech API). For Piper
> voices **locally**: `pip install piper-tts`.

## 12. Visual theme (Light / Medium / Dark)

A selector is present in the **sidebar** (`quranlab/theme.py`).
Three **Islamic-inspired** palettes (identity: **emerald green & gold**),
applied dynamically by CSS injection (variables `--ql-*`):

| Mode | Background | Accent | Usage |
|---|---|---|---|
| **Light** | `#F2F1E8` (ivory / grey-green) | `#0C5C46` (emerald) | daytime, warm |
| **Medium** | `#1C2622` (muted green-slate) | `#6FA98C` (sage) | eye comfort |
| **Dark** | `#101714` (deep forest green) | `#5E8F72` (matte forest) | low brightness |

Rules and ornaments use **gold/champagne** (`--ql-gold`): geometric motifs
(zellige mosaic) on banners, `.ql-card` cards with rounded corners and soft
shadows, serif headings. In **Dark**, the green is deliberately **matte and
desaturated** (never glaring); in **Light**, the background is never pure white.

The CSS styles backgrounds, text, sidebar, tabs, fields, expanders and internal
HTML tables (`table.ql`). Tables are generated in HTML (`html_table()`) rather
than with `st.dataframe`, whose *canvas* view does not follow the themes.

## 13. Learning — spaced repetition (*Learn* tab)

Memorise **Qur'anic vocabulary** through spaced repetition (Anki-style), with no
external dependency. Progress is stored locally in `data/learning.json` (git
ignored, like bookmarks).

- **Dashboard**: cards due, reviews and new cards today, day streak, mastered
  roots and **frequent-lexicon coverage** (share of the `LEARN_TOP_ROOTS` most
  common roots already mastered).
- **Spaced repetition** (`quranlab/srs.py`): simplified SM-2
  (`again` / `hard` / `good` / `easy`), states `new` → `learning` → `review`.
  `quranlab/learning.py` persists cards, goals and the daily log.
- **Context quiz** (`quranlab/quiz.py`): the target word is highlighted in its
  verse; pick the right gloss among distractors. A second exercise asks to
  **recognise the root** of a form. Answering updates the SRS.
- **Word card / clickable words**: enabling *Clickable words* in the sidebar
  makes every word in a verse clickable; the card shows form, root, lemma, part
  of speech, Qur'anic **frequency** and gloss (`quranlab/vocab.py`).
- **Configurable daily goals** (new words, reviews) and reminders.

Can be disabled via `config.LEARN_ENABLED = False`.

## 14. Bookmarks (the *Bookmarks* tab)

Every saved verse is **centralised** in the *Bookmarks* tab
(`quranlab/bookmarks.py`, local storage `data/bookmarks.json`, git ignored):

- **Add / remove in one click**: under each displayed verse, the *bookmark*
  button toggles membership (`bookmarks.toggle()`).
- **Add by reference**: type a reference directly — same tolerant separators as
  the search (`2:255`, `2.255`, `2/255`, `2 255`).
- **Annotations**: each bookmark can carry a personal **note**.
- **Export**: the list (references, uthmani text and translations of the active
  language) downloads as a text file; a **reset** button clears everything.

No data leaves the machine: each deployment keeps its own bookmarks.

## 15. Reading Arabic — the Iqraʾ method (the *Read the Quran Iqra* tab)

A guided course in **7 navigable steps** (radio) to learn to read Qur'anic Arabic
(`quranlab/iqra.py` for the data, `quranlab/iqra_ui.py` for the view). Every item
has a **Listen** button (Arabic speech synthesis `ar-SA` via the browser API,
`ui.tts_arabic`).

1. **Alphabet** — the 28 letters, isolated / initial / medial / final forms and
   the rule of the six non-connecting letters; a **Shuffle the letters** toggle
   reorders the cards randomly (the order is kept in the session state, so it
   is stable while listening to the TTS), with a one-click return to the
   **traditional order**.
2. **Vowels** — short (*ḥarakāt*) and long (*moudoud*), with a drill (pick the
   transcription).
3. **Signs** — soukoun, chaddah, tanwīn, illustrated by example words.
4. **Reading** — words, set expressions then short surahs, with phonetic
   transcription and audio recitation.
5. **Essential vocabulary** — the `config.IQRA_VOCAB_TOP` (500) most frequent
   roots, as cards (representative word, pronunciation, meaning, reference),
   with a full-text filter and a display limit.
6. **Numbers** — from 1 to 1000: Arabic-Indic digit, spelling in words and
   pronunciation (units, tens, hundreds).
7. **The 99 Names of Allah** — see below.

### 15.1 The 99 Names of Allah (`quranlab/asma.py`)

The 99 Names (*Asmāʾ Allāh al-Ḥusnā*) are presented as **cards**, in a
**strictly etymological / lexicographic** approach (no exegesis):

- Arabic calligraphy (RTL), **transliteration** and **direct translation**;
- **root** and the **lexicographic meaning** of that root;
- a graphic marker and a tint derived from the rank; a full-text **filter**
  (Arabic, transliteration, French, English and root — internal spaces of roots
  ignored, e.g. `رحم` finds `ر ح م`);
- a **Listen** button per Name (Arabic pronunciation).

Data exposed through `asma.NAMES` and the helpers `asma.count()`,
`asma.translation()`, `asma.etymology()` and `asma.search()`.

## 16. Getting-started guide (sidebar modal)

`quranlab/onboarding.py` provides a bilingual **getting-started guide**, opened by
a **sidebar button** — it **never opens automatically** (state `ql_guide_open`,
closed by default on a fresh session). The guide describes the role of each tab,
the multi-separator **reference search**, **bookmarks**, the **Iqra** course
(alphabet → 99 Names) and the **99 Names**, then offers course suggestions
(`SUGGESTIONS`).

## 17. Installable app (PWA) and mobile comfort

QuranLab is an **installable web app**: on mobile or desktop the browser offers
"Install" / "Add to Home screen", and the app then opens **full screen**, with
no address bar.

- `quranlab/pwa.py` generates, if missing, the **manifest** and the **PNG icons**
  (192, 512, a *maskable* variant and `apple-touch-icon`), then injects into the
  document head the `<link rel="manifest">`, the `theme-color` (matching the
  current theme) and the `apple-mobile-web-app-*` metadata.
- The files are served by Streamlit from the `static/` folder, which requires
  `server.enableStaticServing = true` (already set in `.streamlit/config.toml`);
  they are exposed under `/app/static/…`.
- The icons are **committed** to the repo; Pillow is only needed to regenerate
  them (`python -m quranlab.pwa`).

The **design** has been unified: a single `.ql-card` CSS template (soft borders,
subtle drop shadow, generous spacing, clear typographic hierarchy) dresses every
pedagogical card of the Iqra course, and *media queries*
(`max-width: 780px` / `420px`) adapt the banner, cards, tabs and touch targets to
small screens.

