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


# --- Fournisseur de synthèse vocale EXTERNE (optionnel, désactivé) --------
# Par défaut, la synthèse vocale utilise la Web Speech API du navigateur (voix
# « Natural » de Microsoft Edge, voix Google de Chrome, ou voix installées dans
# le système) : aucune clé, aucun coût.
#
# Pour garantir une voix française naturelle même quand le navigateur n'expose
# aucune voix de qualité, on peut brancher un service HTTP renvoyant un flux
# audio pour un texte donné (ex. serveur Piper local, gateway TTS, Azure/Google
# TTS auto-hébergé…). Renseigner une URL MODÈLE, par exemple :
#   TTS_HTTP_URL = "http://localhost:5000/api/tts?lang={lang}&text={text}"
# « {text} » et « {lang} » sont remplacés (valeur encodée pour l'URL). Laisser
# vide pour n'utiliser que les voix du navigateur (aucun appel réseau).
TTS_HTTP_URL = ""


# --- Moteur de synthèse vocale : Piper (neuronale, hors-ligne) ------------
# Piper fournit des voix neuronales naturelles, sans clé ni compte, exécutées
# en local (onnxruntime). C'est le moteur privilégié : il propose PLUSIEURS voix
# françaises au choix, ne dépend pas des voix installées dans le système et ne
# risque jamais d'épeler lettre à lettre. Repli automatique sur la Web Speech
# API du navigateur si Piper n'est pas installé.
#
#   "auto"    : Piper si disponible, sinon navigateur (défaut) ;
#   "piper"   : force Piper (télécharge le modèle au premier usage) ;
#   "browser" : force la synthèse du navigateur.
TTS_PROVIDER = "auto"

# Modèles (~20-60 Mo) téléchargés une seule fois dans données `data/piper/`.
PIPER_DIR = DATA_DIR / "piper"
PIPER_VOICES = [
    {"key": "siwis",  "voice": "fr_FR-siwis-medium", "label": "Siwis — femme (recommandée)", "gender": "F"},
    {"key": "tom",    "voice": "fr_FR-tom-medium",   "label": "Tom — homme",                 "gender": "M"},
    {"key": "upmc",   "voice": "fr_FR-upmc-medium",  "label": "UPMC — voix neutre",          "gender": "N"},
    {"key": "mls",    "voice": "fr_FR-mls-medium",   "label": "MLS — femme (claire)",        "gender": "F"},
    {"key": "gilles", "voice": "fr_FR-gilles-low",   "label": "Gilles — homme (léger)",      "gender": "M"},
    {"key": "siwis_l", "voice": "fr_FR-siwis-low",   "label": "Siwis léger — femme",         "gender": "F"},
]
PIPER_VOICES_EN = [
    {"key": "lessac", "voice": "en_US-lessac-medium", "label": "Lessac — female", "gender": "F"},
    {"key": "ryan",   "voice": "en_US-ryan-medium",   "label": "Ryan — male",     "gender": "M"},
    {"key": "amy",    "voice": "en_US-amy-medium",    "label": "Amy — female",    "gender": "F"},
    {"key": "joe",    "voice": "en_US-joe-medium",    "label": "Joe — male",      "gender": "M"},
]


def piper_voices(language: str) -> list:
    """Voix Piper proposées pour une langue (français par défaut)."""
    return PIPER_VOICES_EN if (language or "").lower() == "en" else PIPER_VOICES


def piper_voice_name(key: str, language: str = "fr") -> str | None:
    """Nom de modèle Piper pour une clé courte (repli : première voix)."""
    vs = piper_voices(language)
    for v in vs:
        if v["key"] == key:
            return v["voice"]
    return vs[0]["voice"] if vs else None



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
    {"key": "shatri",   "label": "Abu Bakr Al-Shatri",
     "edition": "Abu_Bakr_Ash-Shaatree_128kbps"},
    {"key": "hudhaify", "label": "Ali Al-Hudhaify",
     "edition": "Hudhaify_128kbps"},
    {"key": "qatami",   "label": "Nasser Al-Qatami",
     "edition": "Nasser_Alqatami_128kbps"},
    {"key": "dussary",  "label": "Yasser Al-Dossari",
     "edition": "Yasser_Ad-Dussary_128kbps"},
    {"key": "budair",   "label": "Salah Al-Budair",
     "edition": "Salah_Al_Budair_128kbps"},
    {"key": "bukhatir", "label": "Salaah Bukhatir",
     "edition": "Salaah_AbdulRahman_Bukhatir_128kbps"},
    {"key": "husary_m", "label": "Al-Husary (mujawwad)",
     "edition": "Husary_Mujawwad_64kbps"},
    {"key": "basit_m",  "label": "Abdul Basit (mujawwad)",
     "edition": "Abdul_Basit_Mujawwad_128kbps"},
    {"key": "minshawy_t", "label": "Al-Minshawi (enseignement)",
     "edition": "Minshawy_Teacher_128kbps"},
]

# URL audio d'un verset pour une édition (dossier) de récitateur donné.
def audio_url(edition: str, sura: int, aya: int) -> str:
    return f"{AUDIO_BASE}/{edition}/{int(sura):03d}{int(aya):03d}.mp3"


def reciter_edition(key: str | None) -> str:
    """Édition audio (dossier everyayah) d'un récitateur, par sa clé.

    Repli sur le premier récitateur de la liste si la clé est inconnue.
    """
    items = RECITERS or [{"key": None, "edition": "Alafasy_128kbps"}]
    for r in items:
        if r.get("key") == key:
            return r["edition"]
    return items[0]["edition"]


# --- Suggestions d'amélioration ------------------------------------------
# Adresse e-mail de contact pour recueillir les propositions d'amélioration.
SUGGESTIONS_EMAIL = "kylemarks5522@gmail.com"
# Lien d'action affiché : mailto pré-rempli. Une URL de dépôt ou de formulaire
# peut aussi être utilisée ici.
SUGGESTIONS_URL = (
    f"mailto:{SUGGESTIONS_EMAIL}"
    "?subject=Suggestion%20d%27am%C3%A9lioration%20pour%20QuranLab"
)


# --- Dons / soutien financier --------------------------------------------
# Fonctionnalité PRÉPARÉE mais DÉSACTIVÉE : passer DONATIONS_ENABLED à True
# (et renseigner les liens ci-dessous) pour l'activer. Tant que le drapeau
# vaut False, aucune section de don n'apparaît dans l'interface.
DONATIONS_ENABLED = False

# Renseigner les liens une fois les comptes créés. Laisser une valeur vide
# pour masquer le bouton correspondant.
#
#   paypal     : lien « Donate » ou « PayPal.Me » (ex.
#                "https://www.paypal.com/donate/?hosted_button_id=XXXXXXXX")
#   card       : lien de paiement carte bancaire (Stripe Payment Link,
#                SumUp, Mollie, ou le bouton carte de PayPal, ex.
#                "https://buy.stripe.com/XXXXXXXX")
#   bitcoin    : adresse BTC ou lien de paiement (ex. "bc1q...")
DONATIONS = {
    "paypal": "",
    "card": "",
    "bitcoin": "",
}



# --- Morphologie / racines (Quranic Arabic Corpus, Kais Dukes) -----------
# Annotation mot-à-mot et segment-à-segment ; fournit ROOT (racine),
# LEM (lemme) et POS (catégorie grammaticale).
MORPHOLOGY_URL = (
    "https://raw.githubusercontent.com/cltk/arabic_morphology_quranic-corpus"
    "/master/quranic-corpus-morphology-0.4.txt"
)
