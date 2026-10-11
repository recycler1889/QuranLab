"""Application web installable (PWA) : icônes, manifeste et métadonnées.

L'application peut être installée sur mobile et bureau (« Ajouter à l'écran
d'accueil ») grâce à :

* un **manifeste** (``static/manifest.webmanifest``) décrivant nom, couleurs,
  icônes et mode d'affichage autonome ;
* des **icônes PNG** générées localement (aucune dépendance réseau) aux tailles
  requises (192 / 512 / 512 maskable / 180 Apple) ;
* des **métadonnées** (``theme-color``, ``apple-mobile-web-app-*``) et un lien
  ``<link rel="manifest">`` injectés dans l'en-tête du document.

Streamlit ne sert des fichiers locaux que si ``server.enableStaticServing`` est
activé : le dossier ``static`` de l'application est alors exposé sous
``/app/static/…`` (voir ``.streamlit/config.toml``).

La génération des icônes utilise Pillow si disponible ; elle est facultative
(les fichiers sont versionnés dans le dépôt) et ne doit jamais faire échouer
l'application en cas d'absence.
"""

import json
import math
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
ICONS_DIR = STATIC_DIR / "icons"

APP_NAME = "QuranLab"
APP_TITLE = "QuranLab — Étude du Coran"
APP_DESC = (
    "Étude du Coran : lecture, racines, concordance, parcours d'apprentissage "
    "de l'arabe (méthode Iqraʾ) et 99 Noms d'Allah."
)

BASE_ACCENT = "#0B6E4F"
BASE_BG = "#F7F5F0"

# Taille (px) — nom de fichier, motif, fond plein, transparence.
ICON_SPECS = (
    ("icon-192.png", 192, 0.30, True, True),
    ("icon-512.png", 512, 0.30, True, True),
    ("icon-maskable-512.png", 512, 0.26, False, False),
    ("apple-touch-icon.png", 180, 0.30, False, False),
)


def _shade(hex_color: str, factor: float) -> tuple:
    """Éclaircit (factor > 1) ou assombrit (factor < 1) une couleur hex."""
    h = hex_color.lstrip("#")
    return tuple(
        max(0, min(255, int(int(h[i:i + 2], 16) * factor)))
        for i in (0, 2, 4)
    )


def _star_points(cx: float, cy: float, outer: float,
                 inner: float) -> list:
    """Sommets d'une étoile à huit branches (motif géométrique islamique)."""
    pts = []
    for i in range(16):
        ang = -math.pi / 2 + i * (math.pi / 8)
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _render_icon(size: int, motif: float, rounded: bool,
                 transparent: bool) -> "object":
    """Rend une icône carrée (étoile à huit branches sur fond dégradé).

    Le rendu est effectué à 4× puis réduit (LANCZOS) pour un lissage soigné.
    """
    from PIL import Image, ImageDraw

    s = size * 4
    top = _shade(BASE_ACCENT, 1.12)
    bottom = _shade(BASE_ACCENT, 0.82)
    img = Image.new("RGBA", (s, s))
    px = img.load()
    for y in range(s):
        t = y / (s - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(s):
            px[x, y] = (r, g, b, 255)

    if rounded:
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=255
        )
        if transparent:
            img.putalpha(mask)

    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    outer = s * motif
    inner = outer * 0.42
    d.polygon(_star_points(cx, cy, outer, inner),
              fill=(255, 255, 255, 255))
    hole = outer * 0.40
    d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole],
              fill=top + (255,))
    dot = outer * 0.17
    d.ellipse([cx - dot, cy - dot, cx + dot, cy + dot],
              fill=(255, 255, 255, 255))

    return img.resize((size, size), Image.LANCZOS)


def _manifest() -> dict:
    """Contenu du manifeste PWA (chemins relatifs au manifeste)."""
    return {
        "name": APP_TITLE,
        "short_name": APP_NAME,
        "description": APP_DESC,
        "lang": "fr",
        "dir": "ltr",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": BASE_BG,
        "theme_color": BASE_ACCENT,
        "categories": ["education", "books", "reference"],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192",
             "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }


def ensure_assets(force: bool = False) -> None:
    """Crée le dossier ``static``, les icônes manquantes et le manifeste.

    Idempotent : ne régénère un fichier que s'il est absent (ou ``force``).
    Toute erreur est capturée — cet habillage ne doit jamais bloquer l'app.
    """
    try:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        manifest_path = STATIC_DIR / "manifest.webmanifest"
        if force or not manifest_path.exists():
            payload = json.dumps(_manifest(), ensure_ascii=False, indent=2)
            manifest_path.write_text(payload + "\n", encoding="utf-8")
        for name, size, motif, rounded, transparent in ICON_SPECS:
            target = ICONS_DIR / name
            if not force and target.exists():
                continue
            try:
                icon = _render_icon(size, motif, rounded, transparent)
                icon.save(target, "PNG")
            except Exception:
                pass
    except Exception:
        pass


def _head_script(theme_color: str) -> str:
    """Script d'injection des métadonnées et du manifeste dans l'en-tête."""
    return (
        "<script>(function(){try{"
        "var w=window.parent;var doc=w.document;"
        "var head=doc.head||doc.getElementsByTagName('head')[0];"
        "if(!head)return;var base=w.location.origin+'/app/static/';"
        "function meta(n,v){var el=head.querySelector('meta[name=\"'+n"
        "+'\"]');if(!el){el=doc.createElement('meta');el.setAttribute('name',n);"
        "head.appendChild(el);}el.setAttribute('content',v);}"
        "var l=head.querySelector('link[rel=\"manifest\"]');"
        "if(!l){l=doc.createElement('link');l.rel='manifest';head.appendChild(l);}"
        "l.href=base+'manifest.webmanifest';"
        "var a=head.querySelector('link[rel=\"apple-touch-icon\"]');"
        "if(!a){a=doc.createElement('link');a.rel='apple-touch-icon';"
        "head.appendChild(a);}a.href=base+'icons/apple-touch-icon.png';"
        f"meta('theme-color','{theme_color}');"
        "meta('apple-mobile-web-app-capable','yes');"
        "meta('mobile-web-app-capable','yes');"
        "meta('apple-mobile-web-app-status-bar-style','black-translucent');"
        "meta('apple-mobile-web-app-title','QuranLab');"
        "meta('application-name','QuranLab');"
        "var vp=head.querySelector('meta[name=\"viewport\"]');"
        "if(vp)vp.setAttribute('content','width=device-width, initial-scale=1, "
        "viewport-fit=cover');"
        "}catch(e){}})();</script>"
    )


def inject(theme_color: str = BASE_ACCENT) -> None:
    """Injecte manifeste et métadonnées PWA (appelé une fois par exécution)."""
    try:
        st.iframe(_head_script(theme_color), height=0, width=0)
    except Exception:
        pass


def page_icon_path() -> str:
    """Chemin relatif de l'icône de page (repli sur un émoji si absente)."""
    target = ICONS_DIR / "icon-192.png"
    return str(target.relative_to(ROOT)).replace("\\", "/") \
        if target.exists() else "📖"


if __name__ == "__main__":
    ensure_assets(force=True)
    print("PWA assets written to", STATIC_DIR)
