"""Conversion Buckwalter <-> arabe et translittération latine.

Le Quranic Arabic Corpus encode les formes et les racines en translittération
de Buckwalter (ASCII).  Ce module permet de :
  * convertir une chaîne Buckwalter en écriture arabe (affichage / recherche) ;
  * reconvertir de l'arabe vers Buckwalter (clé de recherche) ;
  * produire une translittération latine approximative (optionnelle) ;
  * normaliser l'arabe (retrait des diacritiques, unification des alif).
"""

import unicodedata

# Buckwalter -> caractère arabe (table standard du corpus).
_BW_TO_AR = {
    "'": "\u0621",  # ء
    "|": "\u0622",  # آ
    ">": "\u0623",  # أ
    "&": "\u0624",  # ؤ
    "<": "\u0625",  # إ
    "}": "\u0626",  # ئ
    "A": "\u0627",  # ا
    "b": "\u0628",
    "p": "\u0629",  # ة
    "t": "\u062A",
    "v": "\u062B",
    "j": "\u062C",
    "H": "\u062D",
    "x": "\u062E",
    "d": "\u062F",
    "*": "\u0630",
    "r": "\u0631",
    "z": "\u0632",
    "s": "\u0633",
    "$": "\u0634",
    "S": "\u0635",
    "D": "\u0636",
    "T": "\u0637",
    "Z": "\u0638",
    "E": "\u0639",
    "g": "\u063A",
    "f": "\u0641",
    "q": "\u0642",
    "k": "\u0643",
    "l": "\u0644",
    "m": "\u0645",
    "n": "\u0646",
    "h": "\u0647",
    "w": "\u0648",
    "Y": "\u0649",  # ى
    "y": "\u064A",
    "F": "\u064B",
    "N": "\u064C",
    "K": "\u064D",
    "a": "\u064E",
    "u": "\u064F",
    "i": "\u0650",
    "~": "\u0651",
    "o": "\u0652",
    "`": "\u0670",  # alef suscrit (dagger alef)
    "{": "\u0671",  # alef wasla
    "_": "\u0640",  # tatweel
}

_AR_TO_BW = {v: k for k, v in _BW_TO_AR.items()}
_BW_CHARS = set(_BW_TO_AR)


def strip_buckwalter_noise(text: str) -> str:
    """Retire du Buckwalter les marques non phonétiques du corpus
    (signes de waqf `,` `.`, marqueurs `^` `#` ...) et le tatweel."""
    return "".join(ch for ch in text if ch in _BW_CHARS and ch != "_")


def clean_arabic(text: str) -> str:
    """Ne conserve que les caractères du bloc arabe (retire ponctuation ASCII
    et tatweel) pour l'affichage des formes."""
    return "".join(
        ch for ch in text if "\u0600" <= ch <= "\u06FF" and ch != "\u0640"
    )

# Buckwalter -> translittération latine (approximative, lisible).
_BW_TO_LATIN = {
    "'": "ʾ",
    "|": "ʾā",
    ">": "aʾ",
    "&": "uʾ",
    "<": "iʾ",
    "}": "iʾ",
    "A": "ā",
    "b": "b",
    "p": "a",
    "t": "t",
    "v": "th",
    "j": "j",
    "H": "ḥ",
    "x": "kh",
    "d": "d",
    "*": "dh",
    "r": "r",
    "z": "z",
    "s": "s",
    "$": "sh",
    "S": "ṣ",
    "D": "ḍ",
    "T": "ṭ",
    "Z": "ẓ",
    "E": "ʿ",
    "g": "gh",
    "f": "f",
    "q": "q",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "h": "h",
    "w": "w",
    "Y": "ā",
    "y": "y",
    "F": "an",
    "N": "un",
    "K": "in",
    "a": "a",
    "u": "u",
    "i": "i",
    "~": "",
    "o": "",
    "`": "ā",
    "{": "a",
    "_": "",
}


def buckwalter_to_arabic(text: str) -> str:
    """Translitère du Buckwalter vers l'écriture arabe."""
    return "".join(_BW_TO_AR.get(ch, ch) for ch in text)


def arabic_to_buckwalter(text: str) -> str:
    """Translitère de l'arabe vers le Buckwalter (clé de recherche)."""
    return "".join(_AR_TO_BW.get(ch, ch) for ch in text)


def buckwalter_to_latin(text: str) -> str:
    """Translitère du Buckwalter vers une translittération latine lisible."""
    return "".join(_BW_TO_LATIN.get(ch, ch) for ch in text)


def strip_diacritics(text: str) -> str:
    """Retire les marques combinantes (harakât, shadda...) et le tatweel."""
    return "".join(
        ch for ch in text if unicodedata.category(ch) != "Mn" and ch != "\u0640"
    )


def normalize_arabic(text: str) -> str:
    """Normalise l'arabe pour la comparaison : sans diacritiques,
    alif unifiés (آ أ إ ٱ -> ا), alif maqsûra -> yâ (ى -> ي)."""
    text = strip_diacritics(text)
    for src, dst in (
        ("\u0622", "\u0627"),
        ("\u0623", "\u0627"),
        ("\u0625", "\u0627"),
        ("\u0671", "\u0627"),
        ("\u0649", "\u064A"),
    ):
        text = text.replace(src, dst)
    return text


def normalize_latin(text: str) -> str:
    """Normalise une chaîne latine (français) : minuscules, sans accents."""
    text = text.lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def is_arabic(text: str) -> bool:
    """Vrai si la chaîne contient au moins un caractère du bloc arabe."""
    return any("\u0600" <= ch <= "\u06FF" for ch in text)
