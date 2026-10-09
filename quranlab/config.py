"""Configuration centrale : chemins locaux et sources de données.

Toutes les sources sont publiques, vérifiables et de nature textuelle
(texte arabe + traductions + annotation morphologique par racines).
Aucun tafsir, aucun hadith.
"""

from pathlib import Path

# --- Arborescence locale -------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGE_DIR.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "quran.db"

# --- Source des textes (Quran API, miroir jsDelivr) ----------------------
QURAN_API = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions"
INFO_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/info.json"

# Texte arabe : Uthmani (King Fahd Complex) pour l'affichage,
# et "simple" (imla'i) qui sert de base à l'annotation du corpus.
ARABIC_EDITIONS = {
    "uthmani": "ara-quranuthmanihaf",
    "simple": "ara-quransimple",
}

# Traductions (français et anglais) : littérales / lexicales, sans appareil
# dogmatique. La langue pilote la voix de synthèse vocale (voir TTS_LOCALES).
TRANSLATIONS = [
    {
        "key": "fr.hamidullah",
        "edition": "fra-muhammadhamidul",
        "author": "Muhammad Hamidullah",
        "language": "fr",
    },
    {
        "key": "fr.rashidmaash",
        "edition": "fra-rashidmaash",
        "author": "Rashid Maash",
        "language": "fr",
    },
    {
        "key": "fr.montada",
        "edition": "fra-islamicfoundati",
        "author": "Islamic Foundation (Montada)",
        "language": "fr",
    },
    {
        "key": "en.sahih",
        "edition": "eng-ummmuhammad",
        "author": "Saheeh International (Umm Muhammad)",
        "language": "en",
    },
    {
        "key": "en.pickthall",
        "edition": "eng-mohammedmarmadu",
        "author": "Marmaduke Pickthall",
        "language": "en",
    },
]

# Locale BCP-47 par langue, utilisée par la synthèse vocale du navigateur.
TTS_LOCALES = {"fr": "fr-FR", "en": "en-US"}


def tts_locale(language: str) -> str:
    """Locale de lecture pour une langue de traduction (repli : français)."""
    return TTS_LOCALES.get((language or "").lower(), "fr-FR")

# --- Récitateurs audio (récitation verset par verset) --------------------
# Audio public hébergé par EveryAyah (fichiers « SSSAAA.mp3 », S=sourate,
# A=verset, zéro-padded). Indépendant du reste : aucune donnée locale.
AUDIO_BASE = "https://everyayah.com/data"

RECITERS = [
    {"key": "alafasy",  "label": "Mishary Rachid Alafasy",
     "edition": "Alafasy_128kbps"},
    {"key": "sudais",   "label": "Abdul Rahman Al-Sudais",
     "edition": "Abdurrahmaan_As-Sudais_192kbps"},
    {"key": "shuraym",  "label": "Saud Al-Shuraim",
     "edition": "Saood_ash-Shuraym_128kbps"},
    {"key": "ghamdi",   "label": "Saad Al-Ghamdi",
     "edition": "Ghamadi_40kbps"},
    {"key": "muaiqly",  "label": "Maher Al-Muaiqly",
     "edition": "MaherAlMuaiqly128kbps"},
    {"key": "basit",    "label": "Abdul Basit (murattal)",
     "edition": "Abdul_Basit_Murattal_192kbps"},
    {"key": "husary",   "label": "Mahmoud Khalil Al-Husary",
     "edition": "Husary_128kbps"},
    {"key": "minshawy", "label": "Mohamed Al-Minshawi",
     "edition": "Minshawy_Murattal_128kbps"},
]

# URL audio d'un verset pour une édition (dossier) de récitateur donné.
def audio_url(edition: str, sura: int, aya: int) -> str:
    return f"{AUDIO_BASE}/{edition}/{int(sura):03d}{int(aya):03d}.mp3"


# --- Suggestions d'amélioration ------------------------------------------
# Laisser vide pour n'afficher qu'un texte d'invitation ; y placer l'URL du
# dépôt (ou d'un formulaire) pour proposer un lien cliquable.
SUGGESTIONS_URL = ""


# --- Morphologie / racines (Quranic Arabic Corpus, Kais Dukes) -----------
# Annotation mot-à-mot et segment-à-segment ; fournit ROOT (racine),
# LEM (lemme) et POS (catégorie grammaticale).
MORPHOLOGY_URL = (
    "https://raw.githubusercontent.com/cltk/arabic_morphology_quranic-corpus"
    "/master/quranic-corpus-morphology-0.4.txt"
)
