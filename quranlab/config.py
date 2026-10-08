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

# Traductions françaises : littérales / lexicales, sans appareil dogmatique.
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
]

# --- Morphologie / racines (Quranic Arabic Corpus, Kais Dukes) -----------
# Annotation mot-à-mot et segment-à-segment ; fournit ROOT (racine),
# LEM (lemme) et POS (catégorie grammaticale).
MORPHOLOGY_URL = (
    "https://raw.githubusercontent.com/cltk/arabic_morphology_quranic-corpus"
    "/master/quranic-corpus-morphology-0.4.txt"
)
