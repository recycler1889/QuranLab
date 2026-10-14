"""Synthèse convergente lisible entre plusieurs traductions d'un même verset.

Ce module n'est **pas** un tafsir : il ne produit aucune interprétation
doctrinale. Il applique une simple **analyse lexicale distributionnelle** —
purement mécanique et vérifiable — sur les traductions *littérales* d'un verset :

  1. on isole le socle de traductions de référence (littérales, sans appareil
     d'exégèse) affiché par défaut ;
  2. on tokenise chaque traduction, on retire les mots-outils (stopwords) et on
     conserve les **unités lexicales de contenu** (mots pleins, et segments de
     deux mots adjacents) ;
  3. on retient les unités qui **convergent** : présentes dans la majorité des
     traductions comparées. Ce sont les éléments de sens les plus stables d'une
     traduction à l'autre.

Rien n'est déduit au-delà de ce que le texte dit : la convergence est un
indicateur de **fidélité lexicale**, laissé à l'appréciation du lecteur.
"""

from __future__ import annotations

import re

from .config import REFERENCE_TRANSLATIONS
from .buckwalter import normalize_latin

# Mots-outils (articles, pronoms, prépositions, auxiliaires…) : ils n'apportent
# pas de sens lexical et fausseraient la convergence.
_STOPWORDS = {
    "fr": {
        "le", "la", "les", "un", "une", "des", "du", "de", "d", "au", "aux",
        "et", "ou", "ni", "mais", "or", "car", "donc", "que", "qui", "quoi",
        "qu", "dont", "ou", "a", "en", "dans", "par", "pour", "sur", "sous",
        "avec", "sans", "vers", "chez", "entre", "est", "sont", "etait",
        "etaient", "etre", "ete", "il", "elle", "ils", "elles", "on", "nous",
        "vous", "je", "tu", "se", "sa", "son", "ses", "leur", "leurs", "ce",
        "cet", "cette", "ces", "cela", "ceci", "celui", "celle", "y", "ne",
        "pas", "plus", "moins", "tout", "toute", "tous", "toutes", "meme",
        "aussi", "comme", "si", "bien", "peut", "fait", "faire", "l", "s",
        "c", "j", "n", "m", "t", "quand", "alors", "puis", "afin", "voici",
        "voila", "oui", "non", "etait", "a", "the", "lui", "leur", "leurs",
        "tres", "aucun", "aucune", "celui", "celle", "ceux", "celles",
        "ainsi", "deja", "encore", "toujours", "jamais", "propre", "surtout",
    },
    "en": {
        "the", "a", "an", "and", "or", "nor", "but", "for", "yet", "so", "of",
        "to", "in", "on", "at", "by", "with", "from", "into", "onto", "over",
        "under", "is", "are", "was", "were", "be", "been", "being", "am",
        "he", "she", "it", "they", "we", "you", "i", "his", "her", "its",
        "their", "our", "your", "my", "this", "that", "these", "those",
        "not", "no", "yes", "as", "if", "then", "than", "there", "here",
        "who", "whom", "whose", "which", "what", "when", "where", "how",
        "all", "any", "each", "every", "some", "such", "do", "does", "did",
        "has", "have", "had", "will", "would", "shall", "should", "may",
        "might", "must", "can", "could", "unto", "upon", "lo",
    },
}

_WORD_RE = re.compile(r"[a-z]+")


def reference_keys(lang: str = "fr", available=None) -> list:
    """Clés du socle de traductions de référence pour la langue ``lang``.

    Priorité aux clés listées dans ``config.REFERENCE_TRANSLATIONS`` ; si la
    langue n'y figure pas (ex. anglais), on retombe sur les traductions
    disponibles de cette langue (au plus 3).
    """
    keys = [str(k) for k in (REFERENCE_TRANSLATIONS or [])]
    if available is None:
        return keys
    lang_keys = [
        str(k) for k, language in available if str(language).lower() == lang
    ]
    picked = [k for k in keys if k in lang_keys]
    if picked:
        return picked
    return lang_keys[:3]


def split_translations(translations, lang: str = "fr", extended: bool = False):
    """Répartit les traductions d'un verset entre socle et « autres ».

    Renvoie ``(affichées, autres)`` : par défaut, seules les traductions de
    référence de la langue active sont **affichées** ; ``extended=True`` (bouton
    « Afficher d'autres traductions ») ajoute les traductions restantes du
    catalogue. ``autres`` est la liste (toujours renvoyée) des traductions
    masquées, pour alimenter le compteur du bouton.
    """
    items = list(translations or [])
    available = [(tr.get("key"), tr.get("language")) for tr in items]
    refs = set(reference_keys(lang, available))
    active = [
        tr for tr in items if str(tr.get("language", "")).lower() == lang
    ]
    reference = [tr for tr in active if tr.get("key") in refs] or active[:3]
    rest = [tr for tr in items if tr not in reference]
    shown = (reference + rest) if extended else reference
    return shown, rest


def normalize_text(text: str) -> str:
    """Texte latin normalisé (minuscules, sans accents) et apostrophes éclatées."""
    return normalize_latin(text or "").replace("'", " ")


def content_terms(text: str, lang: str = "fr") -> list:
    """Unités lexicales de contenu : mots pleins + segments de deux mots.

    Les mots-outils sont écartés ; les locutions de deux mots adjacents (ex.
    « notre seigneur ») sont produites lorsque les deux termes sont significatifs.
    """
    stop = _STOPWORDS.get(lang, _STOPWORDS["fr"])
    words = [w for w in _WORD_RE.findall(normalize_text(text))]
    content = [w for w in words if len(w) >= 3 and w not in stop]
    terms = list(content)
    terms += [f"{a} {b}" for a, b in zip(content, content[1:])]
    return terms


def convergent_terms(texts, lang: str = "fr", min_share: float = 0.66,
                     top: int = 12) -> list:
    """Éléments lexicaux convergents entre plusieurs traductions.

    Une unité est retenue si elle apparaît dans **au moins** ``min_share`` des
    traductions comparées. Tri : fréquence documentaire décroissante, puis
    fréquence totale, puis ordre alphabétique.
    """
    texts = [t for t in (texts or []) if t and t.strip()]
    n = len(texts)
    if n < 2:
        return []
    need = max(2, int(n * min_share + 0.9999))
    doc_freq: dict = {}
    total_freq: dict = {}
    for text in texts:
        seen = set(content_terms(text, lang))
        for term in seen:
            doc_freq[term] = doc_freq.get(term, 0) + 1
        for term in content_terms(text, lang):
            total_freq[term] = total_freq.get(term, 0) + 1
    out = [
        {"term": term, "docs": df, "count": total_freq.get(term, df)}
        for term, df in doc_freq.items()
        if df >= need
    ]
    out.sort(key=lambda d: (-d["docs"], -d["count"], d["term"]))
    return out[:top]


def synthesize(translations, lang: str = "fr") -> dict | None:
    """Synthèse convergente des traductions (langue active, socle comparé).

    Ne considère que les traductions de la **langue active** (aucun mélange ;
    comparer des mots de langues différentes n'aurait pas de sens lexical).
    Renvoie ``None`` s'il y a moins de deux traductions à comparer.
    """
    active = [
        str(tr.get("text", ""))
        for tr in (translations or [])
        if str(tr.get("language", "")).lower() == lang and tr.get("text")
    ]
    if len(active) < 2:
        return None
    terms = convergent_terms(active, lang=lang)
    return {"n": len(active), "terms": terms}
