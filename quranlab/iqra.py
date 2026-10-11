"""Parcours de lecture de l'arabe (méthode Iqraʾ).

Données pédagogiques statiques, volontairement indépendantes de Streamlit
(pour être testables à l'unité) :

- ``ALPHABET`` : les 28 lettres, avec leur nom, leur nom arabe (pour la
  synthèse vocale), leur transcription et leurs quatre formes
  positionnelles (isolée, initiale, médiale, finale) ;
- ``SHORT_VOWELS`` / ``LONG_VOWELS`` : voyelles courtes (harakāt) et longues
  (moudoud), présentées sur la consonne ``ب`` ;
- ``MARKS`` : soukoun, chaddah, tanwin, avec des mots-exemples voyellés ;
- ``NUM_UNITS`` / ``NUM_TENS`` / ``NUM_HUNDREDS`` : les nombres arabes de 1 à
  1000 (chiffre arabo-indien, mot voyellé, transcription) ;
- ``syllable_items()`` / ``syllables_grid()`` : grilles consonne × voyelle ;
- ``READING_TIERS`` : des listes de mots progressifs (du mot simple aux
  expressions consacrées), chacune accompagnée de sa transcription et de sa
  signification en français et en anglais ;
- ``PRACTICE_SURAHS`` : de courtes sourates à lire en toute fin de parcours
  (la transcription phonétique par verset sert de filet de lecture).

Le sens des mots de lecture est fourni dans les deux langues de l'interface
(champ ``fr`` / ``en``) : il s'agit de données pédagogiques, non de textes
d'interface.
"""

# ---------------------------------------------------------------- Alphabet -
# (lettre, nom, nom arabe, transcription, quatre formes). Deux conventions :
#   - le ``name`` latin est identique en français et en anglais ; ``ar_name``
#     est le nom de la lettre en écriture arabe (lu par la synthèse vocale) ;
#   - les lettres « non connectives » (ا د ذ ر ز و) ne joignent jamais la
#     lettre suivante : leur forme initiale égale leur forme isolée.
ALPHABET = [
    {"ar": "ا", "name": "alif",    "ar_name": "أَلِف",   "tr": "ā / ʾ",    "forms": ("ا", "ا", "ـا", "ـا")},
    {"ar": "ب", "name": "bāʾ",     "ar_name": "بَاء",    "tr": "b",        "forms": ("ب", "بـ", "ـبـ", "ـب")},
    {"ar": "ت", "name": "tāʾ",     "ar_name": "تَاء",    "tr": "t",        "forms": ("ت", "تـ", "ـتـ", "ـت")},
    {"ar": "ث", "name": "thāʾ",    "ar_name": "ثَاء",    "tr": "th",       "forms": ("ث", "ثـ", "ـثـ", "ـث")},
    {"ar": "ج", "name": "jīm",     "ar_name": "جِيم",    "tr": "j",        "forms": ("ج", "جـ", "ـجـ", "ـج")},
    {"ar": "ح", "name": "ḥāʾ",     "ar_name": "حَاء",    "tr": "ḥ",        "forms": ("ح", "حـ", "ـحـ", "ـح")},
    {"ar": "خ", "name": "khāʾ",    "ar_name": "خَاء",    "tr": "kh",       "forms": ("خ", "خـ", "ـخـ", "ـخ")},
    {"ar": "د", "name": "dāl",     "ar_name": "دَال",    "tr": "d",        "forms": ("د", "د", "ـد", "ـد")},
    {"ar": "ذ", "name": "dhāl",    "ar_name": "ذَال",    "tr": "dh",       "forms": ("ذ", "ذ", "ـذ", "ـذ")},
    {"ar": "ر", "name": "rāʾ",     "ar_name": "رَاء",    "tr": "r",        "forms": ("ر", "ر", "ـر", "ـر")},
    {"ar": "ز", "name": "zay",     "ar_name": "زَاي",    "tr": "z",        "forms": ("ز", "ز", "ـز", "ـز")},
    {"ar": "س", "name": "sīn",     "ar_name": "سِين",    "tr": "s",        "forms": ("س", "سـ", "ـسـ", "ـس")},
    {"ar": "ش", "name": "shīn",    "ar_name": "شِين",    "tr": "sh",       "forms": ("ش", "شـ", "ـشـ", "ـش")},
    {"ar": "ص", "name": "ṣād",     "ar_name": "صَاد",    "tr": "ṣ",        "forms": ("ص", "صـ", "ـصـ", "ـص")},
    {"ar": "ض", "name": "ḍād",     "ar_name": "ضَاد",    "tr": "ḍ",        "forms": ("ض", "ضـ", "ـضـ", "ـض")},
    {"ar": "ط", "name": "ṭāʾ",     "ar_name": "طَاء",    "tr": "ṭ",        "forms": ("ط", "طـ", "ـطـ", "ـط")},
    {"ar": "ظ", "name": "ẓāʾ",     "ar_name": "ظَاء",    "tr": "ẓ",        "forms": ("ظ", "ظـ", "ـظـ", "ـظ")},
    {"ar": "ع", "name": "ʿayn",    "ar_name": "عَيْن",   "tr": "ʿ",        "forms": ("ع", "عـ", "ـعـ", "ـع")},
    {"ar": "غ", "name": "ghayn",   "ar_name": "غَيْن",   "tr": "gh",       "forms": ("غ", "غـ", "ـغـ", "ـغ")},
    {"ar": "ف", "name": "fāʾ",     "ar_name": "فَاء",    "tr": "f",        "forms": ("ف", "فـ", "ـفـ", "ـف")},
    {"ar": "ق", "name": "qāf",     "ar_name": "قَاف",    "tr": "q",        "forms": ("ق", "قـ", "ـقـ", "ـق")},
    {"ar": "ك", "name": "kāf",     "ar_name": "كَاف",    "tr": "k",        "forms": ("ك", "كـ", "ـكـ", "ـك")},
    {"ar": "ل", "name": "lām",     "ar_name": "لَام",    "tr": "l",        "forms": ("ل", "لـ", "ـلـ", "ـل")},
    {"ar": "م", "name": "mīm",     "ar_name": "مِيم",    "tr": "m",        "forms": ("م", "مـ", "ـمـ", "ـم")},
    {"ar": "ن", "name": "nūn",     "ar_name": "نُون",    "tr": "n",        "forms": ("ن", "نـ", "ـنـ", "ـن")},
    {"ar": "ه", "name": "hāʾ",     "ar_name": "هَاء",    "tr": "h",        "forms": ("ه", "هـ", "ـهـ", "ـه")},
    {"ar": "و", "name": "wāw",     "ar_name": "وَاو",    "tr": "w",        "forms": ("و", "و", "ـو", "ـو")},
    {"ar": "ي", "name": "yāʾ",     "ar_name": "يَاء",    "tr": "y",        "forms": ("ي", "يـ", "ـيـ", "ـي")},
]

# Lettres qui ne s'attachent jamais à la suivante (forme initiale == isolée).
NON_CONNECTING = ("ا", "د", "ذ", "ر", "ز", "و")

# Diacritiques combinables (Unicode) : voyelles courtes et signes.
FATHA = "\u064E"
DAMMA = "\u064F"
KASRA = "\u0650"
SHADDA = "\u0651"
SUKUN = "\u0652"
FATHATAN = "\u064B"
DAMMATAN = "\u064C"
KASRATAN = "\u064D"

VOWEL_SIGNS = {"fatha": FATHA, "kasra": KASRA, "dhamma": DAMMA}

# --------------------------------------------------------------- Voyelles ----
# Voyelles courtes présentées sur la consonne de référence ``ب``.
SHORT_VOWELS = [
    {"key": "fatha", "name": "Fatha",  "tr": "a", "ar": "ب\u064E"},
    {"key": "kasra", "name": "Kasra",  "tr": "i", "ar": "ب\u0650"},
    {"key": "dhamma", "name": "Dhamma", "tr": "u", "ar": "ب\u064F"},
]

# Voyelles longues : consonne + voyelle courte + lettre de prolongation.
LONG_VOWELS = [
    {"key": "madda_alif", "name": "Alif", "tr": "ā", "combo": "Fatha + Alif", "ar": "ب\u064Eا"},
    {"key": "madda_waw",  "name": "Wāw",  "tr": "ū", "combo": "Dhamma + Wāw", "ar": "ب\u064Fو"},
    {"key": "madda_ya",   "name": "Yāʾ",  "tr": "ī", "combo": "Kasra + Yāʾ",  "ar": "ب\u0650ي"},
]

# ------------------------------------------------------------------ Signes --
# soukoun (pas de voyelle), chaddah (consonne doublée), tanwin (n final).
# `words` : tuples (mot voyellé, transcription, sens FR, sens EN).
MARKS = [
    {
        "key": "sukun",
        "name": "Soukoun",
        "ar": "ب" + SUKUN,
        "sign": SUKUN,
        "tr": "consonne sans voyelle",
        "words": [
            ("قَلْب", "qalb", "cœur", "heart"),
            ("نَفْس", "nafs", "âme / être", "soul / self"),
            ("صَبْر", "ṣabr", "patience", "patience"),
        ],
    },
    {
        "key": "shadda",
        "name": "Chaddah",
        "ar": "ب" + SHADDA,
        "sign": SHADDA,
        "tr": "consonne doublée",
        "words": [
            ("جَنَّة", "janna", "jardin / paradis", "garden / paradise"),
            ("حَقّ", "ḥaqq", "vérité", "truth"),
            ("رَبِّ", "rabbi", "mon Seigneur", "my Lord"),
        ],
    },
    {
        "key": "tanwin",
        "name": "Tanwin",
        "ar": "ب" + FATHATAN,
        "sign": FATHATAN + " " + KASRATAN + " " + DAMMATAN,
        "tr": "n final (an · in · un)",
        "words": [
            ("كِتَابٌ", "kitābun", "un livre", "a book"),
            ("كِتَابًا", "kitāban", "un livre (acc.)", "a book (acc.)"),
            ("كِتَابٍ", "kitābin", "d'un livre", "of a book"),
        ],
    },
]

# ----------------------------------------------------------------- Syllabes --
def consonants(exclude_alif: bool = True) -> list:
    """Les lettres consonnes (par défaut sans alif, qui joue rôle de voyelle)."""
    letters = list(ALPHABET)
    if exclude_alif:
        letters = [l for l in letters if l["ar"] != "ا"]
    return letters


def syllable_pairs() -> list:
    """Toutes les syllabes consonne × voyelle courte (arabe + transcription).

    Exemple : ``{"ar": "بَ", "tr": "ba"}``. L'alif est exclu : porteur de
    voyelle longue, il s'étudie avec les moudoud.
    """
    pairs = []
    for letter in consonants(exclude_alif=True):
        for vowel in SHORT_VOWELS:
            pairs.append({
                "ar": letter["ar"] + VOWEL_SIGNS[vowel["key"]],
                "tr": letter["tr"] + vowel["tr"],
                "key": letter["ar"] + "-" + vowel["key"],
            })
    return pairs


def syllables_grid() -> list:
    """Grille consonne × voyelles courtes pour affichage tableau.

    Une ligne par consonne ; les colonnes (déquié par clé de voyelle)
    contiennent la syllabe arabe et sa transcription.
    """
    rows = []
    for letter in consonants(exclude_alif=True):
        row = {"ar": letter["ar"], "tr": letter["tr"]}
        for vowel in SHORT_VOWELS:
            v = vowel["key"]
            row[v] = letter["ar"] + VOWEL_SIGNS[v]
            row[v + "_tr"] = letter["tr"] + vowel["tr"]
        rows.append(row)
    return rows


# -------------------------------------------------- Mots progressifs (lecture)
# `ref` : référence coranique facultative. Le sens est fourni en FR et en EN.
READING_TIERS = [
    {
        "key": 1,
        "title_fr": "Palier 1 — consonne + voyelle",
        "title_en": "Step 1 — consonant + vowel",
        "hint_fr": "Lisez à voix haute : anā, huwa, hiya…",
        "hint_en": "Read aloud: anā, huwa, hiya…",
        "words": [
            {"ar": "أَنَا", "tr": "anā",  "fr": "je / moi",  "en": "I / me"},
            {"ar": "هُوَ",  "tr": "huwa",  "fr": "il",       "en": "he"},
            {"ar": "هِيَ",  "tr": "hiya",  "fr": "elle",     "en": "she"},
            {"ar": "مَا",   "tr": "mā",    "fr": "quoi / que", "en": "what / that"},
            {"ar": "مَن",   "tr": "man",   "fr": "qui",      "en": "who"},
            {"ar": "فِي",   "tr": "fī",    "fr": "dans",     "en": "in"},
        ],
    },
    {
        "key": 2,
        "title_fr": "Palier 2 — le soukoun coupe la syllabe",
        "title_en": "Step 2 — the sukun snaps the syllable",
        "hint_fr": "La consonne marquée se prononce sèche : qalb, nafs, ṣabr.",
        "hint_en": "A marked consonant is snapped short: qalb, nafs, ṣabr.",
        "words": [
            {"ar": "قَلْب", "tr": "qalb",  "fr": "cœur",       "en": "heart", "ref": "2:7"},
            {"ar": "نَفْس", "tr": "nafs",  "fr": "âme / être", "en": "soul / self"},
            {"ar": "صَبْر", "tr": "ṣabr",  "fr": "patience",   "en": "patience", "ref": "2:45"},
            {"ar": "عِلْم", "tr": "ʿilm",  "fr": "savoir",     "en": "knowledge"},
            {"ar": "ظُلْم", "tr": "ẓulm",  "fr": "injustice",  "en": "injustice"},
            {"ar": "شَمْس", "tr": "shams", "fr": "soleil",     "en": "sun"},
        ],
    },
    {
        "key": 3,
        "title_fr": "Palier 3 — la chaddah double la consonne",
        "title_en": "Step 3 — the shadda doubles the consonant",
        "hint_fr": "Prononcez la consonne deux fois : ḥaqq, janna, rabbī.",
        "hint_en": "Say the consonant twice: ḥaqq, janna, rabbī.",
        "words": [
            {"ar": "حَقّ",     "tr": "ḥaqq",      "fr": "vérité",           "en": "truth", "ref": "2:42"},
            {"ar": "جَنَّة",   "tr": "janna",     "fr": "jardin / paradis", "en": "garden / paradise", "ref": "2:35"},
            {"ar": "رَبِّي",   "tr": "rabbī",     "fr": "mon Seigneur",     "en": "my Lord", "ref": "2:129"},
            {"ar": "أُمَّة",   "tr": "umma",      "fr": "communauté",       "en": "community", "ref": "2:128"},
            {"ar": "مُحَمَّد", "tr": "Muḥammad",  "fr": "Mohammad (loué)",  "en": "Muhammad (praised)"},
        ],
    },
    {
        "key": 4,
        "title_fr": "Palier 4 — moudoud et mots longs",
        "title_en": "Step 4 — long vowels (moudoud) and longer words",
        "hint_fr": "Les voyelles longues allongent la syllabe : kitāb, nūr, Qurʾān.",
        "hint_en": "Long vowels stretch the syllable: kitāb, nūr, Qurʾān.",
        "words": [
            {"ar": "كِتَاب",  "tr": "kitāb",   "fr": "livre / Écriture", "en": "book / Scripture", "ref": "2:2"},
            {"ar": "سَمَاء",  "tr": "samāʾ",   "fr": "ciel",             "en": "sky", "ref": "2:19"},
            {"ar": "نُور",    "tr": "nūr",     "fr": "lumière",          "en": "light", "ref": "24:35"},
            {"ar": "قُرْآن",  "tr": "Qurʾān",  "fr": "Coran (récitation)", "en": "Qur'an (recitation)", "ref": "2:185"},
            {"ar": "سَلَام",  "tr": "salām",   "fr": "paix",             "en": "peace", "ref": "2:208"},
            {"ar": "إِيمَان", "tr": "īmān",    "fr": "foi",              "en": "faith", "ref": "2:143"},
            {"ar": "رَحْمَة", "tr": "raḥma",   "fr": "miséricorde",      "en": "mercy", "ref": "2:64"},
        ],
    },
    {
        "key": 5,
        "title_fr": "Expressions consacrées",
        "title_en": "Set phrases",
        "hint_fr": "Vous lisez déjà certaines expressions du Coran !",
        "hint_en": "You are already reading expressions of the Qur'an!",
        "words": [
            {"ar": "بِسْمِ اللَّهِ",           "tr": "bismi llāh",        "fr": "au nom de Dieu",           "en": "in the name of God", "ref": "1:1"},
            {"ar": "الْحَمْدُ لِلَّهِ",         "tr": "al-ḥamdu lillāh",   "fr": "louange à Dieu",           "en": "praise be to God", "ref": "1:2"},
            {"ar": "سُبْحَانَ اللَّهِ",        "tr": "subḥāna llāh",      "fr": "gloire à Dieu",            "en": "glory be to God"},
            {"ar": "لَا إِلَٰهَ إِلَّا اللَّهُ", "tr": "lā ilāha illā llāh", "fr": "nulle divinité sinon Dieu", "en": "no god but God"},
        ],
    },
]

# --------------------------------------------------------------- Nombres ----
# Chiffres arabo-indiens (levantins) pour convertir l'écriture d'un nombre.
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def arabic_digits(n: int) -> str:
    """Convertit un entier en chiffres arabo-indiens (``21`` -> ``٢١``)."""
    return "".join(ARABIC_DIGITS[int(ch)] for ch in str(int(n)))


# De 1 à 10 : chiffre, mot voyellé (forme de comptage) et transcription.
NUM_UNITS = [
    {"n": 1,  "ar": "وَاحِد",    "tr": "wāḥid"},
    {"n": 2,  "ar": "اِثْنَانِ", "tr": "ithnāni"},
    {"n": 3,  "ar": "ثَلَاثَة",  "tr": "thalātha"},
    {"n": 4,  "ar": "أَرْبَعَة", "tr": "arbaʿa"},
    {"n": 5,  "ar": "خَمْسَة",   "tr": "khamsa"},
    {"n": 6,  "ar": "سِتَّة",    "tr": "sitta"},
    {"n": 7,  "ar": "سَبْعَة",   "tr": "sabʿa"},
    {"n": 8,  "ar": "ثَمَانِيَة", "tr": "thamāniya"},
    {"n": 9,  "ar": "تِسْعَة",   "tr": "tisʿa"},
    {"n": 10, "ar": "عَشَرَة",   "tr": "ʿashara"},
]

# Les dizaines : 20, 30, …, 90 (le 10 est déjà compté dans NUM_UNITS).
NUM_TENS = [
    {"n": 20, "ar": "عِشْرُون",   "tr": "ʿishrūn"},
    {"n": 30, "ar": "ثَلَاثُون",  "tr": "thalāthūn"},
    {"n": 40, "ar": "أَرْبَعُون", "tr": "arbaʿūn"},
    {"n": 50, "ar": "خَمْسُون",   "tr": "khamsūn"},
    {"n": 60, "ar": "سِتُّون",    "tr": "sittūn"},
    {"n": 70, "ar": "سَبْعُون",   "tr": "sabʿūn"},
    {"n": 80, "ar": "ثَمَانُون",  "tr": "thamānūn"},
    {"n": 90, "ar": "تِسْعُون",   "tr": "tisʿūn"},
]

# Les centaines : 100, 200, …, 1000 (200 est la forme duelle de مائة).
NUM_HUNDREDS = [
    {"n": 100,  "ar": "مِائَة",       "tr": "miʾa"},
    {"n": 200,  "ar": "مِائَتَان",    "tr": "miʾatān"},
    {"n": 300,  "ar": "ثَلَاثُمِائَة", "tr": "thalāthu miʾa"},
    {"n": 400,  "ar": "أَرْبَعُمِائَة", "tr": "arbaʿu miʾa"},
    {"n": 500,  "ar": "خَمْسُمِائَة", "tr": "khamsu miʾa"},
    {"n": 600,  "ar": "سِتُّمِائَة",  "tr": "sittu miʾa"},
    {"n": 700,  "ar": "سَبْعُمِائَة", "tr": "sabʿu miʾa"},
    {"n": 800,  "ar": "ثَمَانِي مِائَة", "tr": "thamāni miʾa"},
    {"n": 900,  "ar": "تِسْعُمِائَة", "tr": "tisʿu miʾa"},
    {"n": 1000, "ar": "أَلْف",        "tr": "alf"},
]

# Sourates courtes à lire en fin de parcours : verset -> transcription.
PRACTICE_SURAHS = [
    (112, {
        1: "qul huwa llāhu aḥad",
        2: "allāhu ṣ-ṣamad",
        3: "lam yalid wa-lam yūlad",
        4: "wa-lam yakun lahu kufuwan aḥad",
    }),
    (113, {
        1: "qul aʿūdhu bi-rabbi l-falaq",
        2: "min sharri mā khalaq",
        3: "wa-min sharri ghāsiqin idhā waqab",
        4: "wa-min sharri n-naffāthāti fī l-ʿuqad",
        5: "wa-min sharri ḥāsidin idhā ḥasad",
    }),
    (114, {
        1: "qul aʿūdhu bi-rabbi n-nās",
        2: "maliki n-nās",
        3: "ilāhi n-nās",
        4: "min sharri l-waswāsi l-khannās",
        5: "alladhī yuwaswisu fī ṣudūri n-nās",
        6: "mina l-jinnati wa-n-nās",
    }),
    (1, {
        1: "bismi llāhi r-raḥmāni r-raḥīm",
        2: "al-ḥamdu lillāhi rabbi l-ʿālamīn",
        3: "ar-raḥmāni r-raḥīm",
        4: "māliki yawmi d-dīn",
        5: "iyyāka naʿbudu wa-iyyāka nastaʿīn",
        6: "ihdinā ṣ-ṣirāṭa l-mustaqīm",
        7: "ṣirāṭa lladhīna anʿamta ʿalayhim ghayri l-maghḍūbi "
           "ʿalayhim wa-lā ḍ-ḍāllīn",
    }),
]