# -*- coding: utf-8 -*-
"""Gestionnaire de themes visuels (Clair / Intermediaire / Sombre).

Identite visuelle **vert emeraude & or**, inspiree du patrimoine de l'art
islamique (geometrie sacree, enluminures). Pour chaque palette, une feuille de
style est injectee via ``st.markdown(..., unsafe_allow_html=True)``. Les
couleurs sont exposees en variables CSS (``--ql-*``) afin d'habiller
uniformement les composants Streamlit et les blocs HTML internes (``table.ql``,
``.ql-card``, ``.ql-banner``).

Reperes de conception :

* **Clair** : fond ivoire / << vert-de-gris >> tres clair (jamais blanc pur),
  chaleureux et reposant, cartes a bordures epurees relevees d'un filet dore ;
* **Intermediaire** : vert sauge feutre sur fond sombre desature, pour les
  longues sessions (confort oculaire) ;
* **Sombre** : vert foret profond, **mat et desature**, jamais eblouissant,
  avec un contraste franc sur le texte clair.

Des **motifs geometriques** subtils (etoile a huit branches / zellige) ornent
les bannieres et cartes ; ils restent discrets (opacite tres basse) pour
preserver la lisibilite et la rigueur de l'etude.
"""

from urllib.parse import quote

# Chaque palette definit un jeu coherent de variables. Identite commune :
# vert emeraude (accent) + or/champagne (filets, ornements).
PALETTES = {
    "Clair": {
        "label": "Clair",
        "bg": "#F2F1E8",       # ivoire / vert-de-gris tres clair (jamais blanc pur)
        "bg2": "#E7E8DB",      # surfaces secondaires (barre laterale, cartes)
        "field": "#FBFBF5",    # champs de saisie (ivoire clair)
        "fg": "#20302A",       # texte vert-anthracite profond
        "fg2": "#5C6B62",      # texte secondaire (sauge grisee)
        "border": "#DED9C4",   # bordure sable/champagne, epuree
        "accent": "#0C5C46",   # emeraude profond
        "gold": "#A98A45",     # or doux / champagne
        "pattern": "#A98A45",  # ornements dores
        "pattern_opacity": "0.06",
    },
    "Intermediaire": {
        "label": "Intermediaire (confort oculaire)",
        "bg": "#1C2622",       # vert-ardoise feutre
        "bg2": "#243029",
        "field": "#2A3630",
        "fg": "#EFEDE3",       # ivoire chaud
        "fg2": "#BFC6BA",      # sauge claire
        "border": "#39463F",
        "accent": "#6FA98C",   # emeraude sauge desature
        "gold": "#C2A567",     # champagne
        "pattern": "#C2A567",
        "pattern_opacity": "0.07",
    },
    "Sombre": {
        "label": "Sombre",
        "bg": "#101714",       # vert foret tres profond (pas de noir pur)
        "bg2": "#161F1A",
        "field": "#1B2620",
        "fg": "#EAEAE2",       # blanc doux
        "fg2": "#9DAA9F",
        "border": "#28362E",
        "accent": "#5E8F72",   # vert foret mat, desature et feutre
        "gold": "#BFA268",     # or discret
        "pattern": "#BFA268",
        "pattern_opacity": "0.09",
    },
}

# Ordre d'affichage dans le selecteur.
ORDER = ["Clair", "Intermediaire", "Sombre"]

DEFAULT = "Clair"

# Pile de polices latines du corps de texte (repli systeme, aucune dependance).
FONT_STACK = (
    '"Inter", "Segoe UI", "Helvetica Neue", Arial, "Noto Sans", sans-serif'
)
# Pile de polices des titres : serif classique et elegant (repli systeme).
HEADING_STACK = (
    '"Cormorant Garamond", "Palatino Linotype", "Book Antiqua", Palatino, '
    'Georgia, "Iowan Old Style", "Times New Roman", serif'
)
# Pile de polices arabes (si installees localement, sinon repli systeme).
ARABIC_STACK = (
    '"Amiri", "Scheherazade New", "Traditional Arabic", "Noto Naskh Arabic", '
    '"Times New Roman", serif'
)


def _mosaic_svg(color: str, opacity: str) -> str:
    """Motif de mosaique (etoile a huit branches + quartiers) en data-URI SVG.

    L'etoile est obtenue par deux carres superposes dont l'un pivote de 45deg ;
    un quadrillage fin et des demi-etoiles de coin assurent la continuite du
    pavage. Le SVG est encode en data-URI pour etre pose en ``background-image``.
    """
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='128' height='128' "
        "viewBox='0 0 128 128'>"
        f"<g fill='none' stroke='{color}' stroke-width='0.9' "
        f"opacity='{opacity}'>"
        # etoile a huit branches centree sur la tuile
        "<rect x='32' y='32' width='64' height='64'/>"
        "<rect x='32' y='32' width='64' height='64' "
        "transform='rotate(45 64 64)'/>"
        "<circle cx='64' cy='64' r='12'/>"
        "<circle cx='64' cy='64' r='4.5'/>"
        # demi-etoiles aux coins : continuite du pavage
        "<rect x='-32' y='-32' width='64' height='64'/>"
        "<rect x='-32' y='-32' width='64' height='64' "
        "transform='rotate(45 0 0)'/>"
        "<rect x='96' y='-32' width='64' height='64'/>"
        "<rect x='96' y='-32' width='64' height='64' "
        "transform='rotate(45 128 0)'/>"
        "<rect x='-32' y='96' width='64' height='64'/>"
        "<rect x='-32' y='96' width='64' height='64' "
        "transform='rotate(45 0 128)'/>"
        "<rect x='96' y='96' width='64' height='64'/>"
        "<rect x='96' y='96' width='64' height='64' "
        "transform='rotate(45 128 128)'/>"
        "</g></svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


def _ornament_svg(color: str) -> str:
    """Fleuron geometrique (etoile a huit branches, facon zellige) pour titres."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='16' "
        "viewBox='0 0 120 16'>"
        f"<g fill='none' stroke='{color}' stroke-width='1' opacity='0.8'>"
        "<path d='M0 8 H36 M84 8 H120'/>"
        "<rect x='52' y='2' width='16' height='16' "
        "transform='rotate(45 60 8)'/>"
        "<rect x='52' y='2' width='16' height='16'/>"
        f"<circle cx='60' cy='8' r='2.2' fill='{color}'/>"
        "</g></svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


def _rgba(hex_color: str, alpha: float) -> str:
    """Convertit une couleur hexadecimale en rgba(...) pour les calques doux."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def _illuminated_css() -> str:
    """Styles pour le design << manuscrit enlumine >> des cartes des 99 Noms.

    Cette fonction retourne une chaine CSS statique (sans interpolation f-string)
    pour eviter les problemes d'echappement des accolades CSS dans les f-strings.
    """
    return """
/* ============================================================================
   ILLUMINATED MANUSCRIPT STYLE -- Cartes des 99 Noms (Asmāʾ al-Ḥusnā)
   Inspiration : enluminures traditionnelles (rabats de manuscrits, tapis de priere)
   Palette : bleu lapis profond, or chaud, rouge cinabre, vert emeraude, ivoire
   ============================================================================ */

/* Motif de bordure ornementale (data-URI SVG) -- reutilise pour border-image */
:root {{
    --ql-illum-border-svg: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 200 200'%3E%3Cdefs%3E%3Cpattern id='illumPattern' width='40' height='40' patternUnits='userSpaceOnUse'%3E%3Cpath d='M20 0 Q40 0 40 20 Q40 40 20 40 Q0 40 0 20 Q0 0 20 0 Z' fill='none' stroke='%23A98A45' stroke-width='1.2' opacity='0.8'/%3E%3Ccircle cx='20' cy='20' r='8' fill='none' stroke='%231B4F72' stroke-width='1' opacity='0.6'/%3E%3Ccircle cx='20' cy='20' r='4' fill='%23C0392B' opacity='0.7'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='200' height='200' fill='url(%23illumPattern)'/%3E%3C/svg%3E");
    --ql-illum-border-width: 24px;
}}

/* Carte style manuscrit enlumine */
.ql-illum-card {{
    position: relative;
    background:
        linear-gradient(135deg, 
            #FDF6E3 0%, 
            #F5ECD5 40%, 
            #E8DCC8 100%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 24px,
            rgba(139, 115, 85, 0.03) 24px,
            rgba(139, 115, 85, 0.03) 25px
        );
    background-blend-mode: multiply, normal;
    border: var(--ql-illum-border-width) solid transparent;
    border-image: var(--ql-illum-border-svg) var(--ql-illum-border-width) round;
    border-radius: 4px;
    padding: calc(var(--ql-illum-border-width) + 1rem) 1.5rem 1.5rem 1.5rem;
    margin: 0.5rem;
    min-height: 420px;
    box-shadow: 
        0 4px 20px -4px rgba(0, 0, 0, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.6),
        inset 0 -1px 0 rgba(139, 115, 85, 0.1);
    transition: transform 0.25s cubic-bezier(.2,.7,.3,1), box-shadow 0.25s ease;
    animation: ql-rise 0.4s cubic-bezier(.2,.7,.3,1) both;
    animation-delay: var(--ql-delay, 0ms);
    will-change: transform;
    overflow: hidden;
}}
.ql-illum-card::before {{
    content: "";
    position: absolute;
    top: 2px;
    left: 2px;
    right: 2px;
    height: calc(var(--ql-illum-border-width) - 2px);
    background: var(--ql-illum-border-svg);
    opacity: 0.9;
    pointer-events: none;
}}
.ql-illum-card::after {{
    content: attr(data-page);
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 0.65rem;
    font-style: italic;
    color: rgba(139, 115, 85, 0.6);
    background: rgba(255, 255, 255, 0.8);
    padding: 2px 10px;
    border-radius: 999px;
    border: 1px solid rgba(169, 138, 69, 0.3);
    pointer-events: none;
}}
.ql-illum-card:hover {{
    transform: translateY(-6px) scale(1.015);
    box-shadow: 
        0 16px 40px -8px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.6),
        inset 0 -1px 0 rgba(139, 115, 85, 0.1);
    z-index: 10;
}}
.ql-illum-card:hover::before {{
    opacity: 1;
}}

/* Contenu interne de la carte enluminee */
.ql-illum-inner {{
    padding-top: 1.5rem;
    text-align: center;
}}

/* Nom arabe -- calligraphie Naskh elegante */
.ql-illum-arabic {{
    font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', 'Noto Naskh Arabic', 'Arabic Typesetting', serif;
    font-size: 2.5rem;
    line-height: 1.4;
    color: #1B4F72;
    margin: 0.5rem 0 0.75rem 0;
    text-shadow: 0 1px 2px rgba(27, 79, 114, 0.2);
    direction: rtl;
    text-align: center;
    font-weight: 400;
    letter-spacing: 0.02em;
}}

/* Translitteration */
.ql-illum-translit {{
    font-family: 'Cormorant Garamond', 'Palatino Linotype', 'Book Antiqua', Palatino, Georgia, serif;
    font-size: 1.1rem;
    color: #1B4F72;
    margin: 0.25rem 0 0.5rem 0;
    font-style: italic;
    letter-spacing: 0.03em;
}}

/* Traduction francaise -- rouge cinabre pour l'accent */
.ql-illum-french {{
    font-family: 'Cormorant Garamond', 'Palatino Linotype', 'Book Antiqua', Palatino, Georgia, serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #C0392B;
    margin: 0.5rem 0 1rem 0;
    letter-spacing: 0.01em;
}}

/* Rang / numero */
.ql-illum-rank {{
    font-family: 'Georgia', serif;
    font-size: 0.75rem;
    font-style: italic;
    color: rgba(139, 115, 85, 0.5);
    margin-bottom: 0.75rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    background: rgba(169, 138, 69, 0.1);
    border: 1px solid rgba(169, 138, 69, 0.2);
    border-radius: 999px;
}}
.ql-illum-rank-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
    background: linear-gradient(135deg, hsl(var(--hue, 0), 50%, 45%), hsl(var(--hue, 0), 50%, 35%));
    color: white;
    font-size: 0.7rem;
    box-shadow: 0 2px 6px -2px rgba(0, 0, 0, 0.2);
}}

/* Racine */
.ql-illum-root {{
    margin: 1rem 0;
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, rgba(169, 138, 69, 0.08), rgba(139, 115, 85, 0.05));
    border: 1px solid rgba(169, 138, 69, 0.15);
    border-radius: 8px;
    font-size: 0.85rem;
    color: #5C6B62;
}}
.ql-illum-root-label {{
    font-weight: 600;
    color: #1B4F72;
    margin-right: 0.5rem;
}}
.ql-illum-root-arabic {{
    font-family: 'Amiri', serif;
    color: #1B4F72;
    margin: 0 0.5rem;
    direction: rtl;
}}
.ql-illum-root-tr {{
    font-family: 'Georgia', serif;
    font-style: italic;
    color: #5C6B62;
}}

/* Etymologie / definition */
.ql-illum-etymology {{
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(253,246,227,0.8));
    border: 1px solid rgba(139, 115, 85, 0.12);
    border-radius: 8px;
    font-size: 0.82rem;
    line-height: 1.6;
    color: #2C3E2E;
    text-align: justify;
    font-family: 'Georgia', 'Times New Roman', serif;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
}}

/* Bouton Ecouter integre au style manuscrit */
.ql-illum-listen-btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 0.5rem 1.25rem;
    background: linear-gradient(135deg, #A98A45 0%, #8B7333 100%);
    border: 1px solid #8B7333;
    border-radius: 999px;
    color: #1B2A1A;
    font-family: 'Georgia', serif;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px -2px rgba(169, 138, 69, 0.4);
}}
.ql-illum-listen-btn:hover {{
    background: linear-gradient(135deg, #BFA268 0%, #A98A45 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px -4px rgba(169, 138, 69, 0.5);
}}
.ql-illum-listen-btn:active {{
    transform: translateY(0) scale(0.98);
}}
.ql-illum-listen-btn .ear-icon {{
    font-size: 1rem;
    opacity: 0.9;
}}

/* Tiroir / Modal pour les versets d'un Nom Divin */
.ql-illum-drawer {{
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    width: 100%;
    max-width: 600px;
    background: linear-gradient(180deg, #FDF6E3 0%, #F5ECD5 100%);
    z-index: 10000;
    box-shadow: -8px 0 32px -4px rgba(0, 0, 0, 0.2);
    transform: translateX(100%);
    transition: transform 0.35s cubic-bezier(.2,.7,.3,1);
    overflow-y: auto;
    border-left: 3px solid #A98A45;
}}
.ql-illum-drawer.open {{
    transform: translateX(0);
}}
.ql-illum-drawer-overlay {{
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 9999;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}}
.ql-illum-drawer-overlay.visible {{
    opacity: 1;
    visibility: visible;
}}

/* En-tete du tiroir */
.ql-illum-drawer-header {{
    position: sticky;
    top: 0;
    background: linear-gradient(135deg, #1B4F72 0%, #0D3A5C 100%);
    color: #FDF6E3;
    padding: 1.5rem 1.25rem 1rem 1.25rem;
    border-bottom: 2px solid #A98A45;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}}
.ql-illum-drawer-close {{
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #FDF6E3;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}}
.ql-illum-drawer-close:hover {{
    background: rgba(192, 57, 43, 0.3);
    border-color: #C0392B;
}}

/* Liste des versets dans le tiroir */
.ql-illum-verse-list {{
    padding: 1rem 1.25rem;
}}
.ql-illum-verse-item {{
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(139, 115, 85, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}}
.ql-illum-verse-item:hover {{
    border-color: rgba(169, 138, 69, 0.4);
    box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.1);
    transform: translateX(-4px);
}}
.ql-illum-verse-ref {{
    font-family: 'Georgia', serif;
    font-size: 0.8rem;
    font-weight: 600;
    color: #A98A45;
    margin-bottom: 0.5rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.2rem 0.6rem;
    background: linear-gradient(135deg, rgba(169, 138, 69, 0.15), rgba(27, 79, 114, 0.1));
    border-radius: 999px;
    border: 1px solid rgba(169, 138, 69, 0.2);
}}
.ql-illum-verse-arabic {{
    font-family: 'Amiri', serif;
    font-size: 1.3rem;
    line-height: 2;
    color: #1B4F72;
    direction: rtl;
    text-align: right;
    margin: 0.5rem 0;
}}
.ql-illum-verse-translation {{
    font-family: 'Georgia', serif;
    font-size: 0.9rem;
    line-height: 1.6;
    color: #2C3E2E;
    font-style: italic;
    border-top: 1px dashed rgba(139, 115, 85, 0.2);
    padding-top: 0.75rem;
    margin-top: 0.5rem;
}}

/* Responsive */
@media (max-width: 780px) {{
    .ql-illum-card {{
        min-height: auto;
        padding: calc(var(--ql-illum-border-width) + 1rem) 1rem 1rem 1rem;
        margin: 0.25rem;
    }}
    .ql-illum-arabic {{
        font-size: 2rem;
    }}
    .ql-illum-drawer {{
        max-width: 100%;
    }}
}}
"""


def css(name: str) -> str:
    p = PALETTES.get(name, PALETTES[DEFAULT])
    ornament = _ornament_svg(p["gold"])
    mosaic = _mosaic_svg(p["gold"], p["pattern_opacity"])
    zebra = _rgba(p["bg2"], 0.04)
    sel_bg = _rgba(p["accent"], 0.28)
    glow = _rgba(p["gold"], 0.10)
    gold_soft = _rgba(p["gold"], 0.16)
    accent_soft = _rgba(p["accent"], 0.12)
    sheen = _rgba(p["gold"], 0.20)
    card_edge = _rgba(p["fg"], 0.06)
    gold_glow = _rgba(p["gold"], 0.28)
    css_content = f"""
    /* Palette QuranLab : composants internes (bandeau, cartes, tableaux) */
    --ql-bg: {p['bg']};
    --ql-bg2: {p['bg2']};
    --ql-field: {p['field']};
    --ql-fg: {p['fg']};
    --ql-fg2: {p['fg2']};
    --ql-border: {p['border']};
    --ql-accent: {p['accent']};
    --ql-gold: {p['gold']};
    --ql-gold-soft: {gold_soft};
    --ql-accent-soft: {accent_soft};
    --ql-ornament: url("{ornament}");
    --ql-mosaic: url("{mosaic}");
    --ql-font: {FONT_STACK};
    --ql-heading: {HEADING_STACK};
    --ql-font-ar: {ARABIC_STACK};

    /* Remappage des variables NATIVES de Streamlit (prefixe `--st-`, cf.
       Streamlit 1.58). Tout composant natif -- fenetres modales (st.dialog),
       menus, expanders, alertes, saisies, titres -- tire desormais fond ET
       texte de la MEME palette : contraste garanti sur les trois modes. Cest
       le mecanisme officiel de personnalisation du theme. */
    --st-background-color: {p['bg']} !important;
    --st-secondary-background-color: {p['bg2']} !important;
    --st-text-color: {p['fg']} !important;
    --st-heading-color: {p['fg']} !important;
    --st-primary-color: {p['accent']} !important;
    --st-link-color: {p['accent']} !important;
    --st-border-color: {p['border']} !important;
    --st-code-background-color: {p['bg2']} !important;
    --st-code-text-color: {p['fg']} !important;
    --st-font: {FONT_STACK} !important;
    --st-heading-font: {HEADING_STACK} !important;
}}

/* Typographie : corps sans-serif lisible ; titres en serif classique. On evite
   tout selecteur << * >> ou << span >> global qui ecraserait les fontes dediees
   (code, icones Material de Streamlit : chevrons, coches, ...). */
.stApp, [data-testid="stSidebar"] {{
    font-family: var(--ql-font);
}}
.stApp input, .stApp textarea,
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {{
    font-family: var(--ql-font);
}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
    font-family: var(--ql-heading);
    letter-spacing: .01em;
}}
.stApp [dir="rtl"], .stApp [lang="ar"] {{ font-family: var(--ql-font-ar); }}

/* Icones Material de Streamlit (chevron _arrow_right_, coches, fleches de
   selecteurs) : maintenir LA police d'icones, jamais celle du texte courant.
   Sinon l'identifiant s'affiche en clair (ex. << arrow_right >>) et deborde sur
   le libelle voisin. */
[class*="material"], [class*="Material"], [class*="sticon"],
[data-testid*="icon"] {{
    font-family: "Material Symbols Rounded", "Material Symbols Outlined",
        "Material Icons Rounded", "Material Icons", "Material Icons Outlined";
    font-variant-ligatures: normal;
    letter-spacing: normal;
}}

/* Confort de lecture << prestige >> : colonne centrale aeree, jamais pleine
   largeur sur grand ecran. */
[data-testid="stMainBlockContainer"], .block-container {{
    max-width: 1180px;
    margin-inline: auto;
    padding-top: 1.3rem;
    padding-bottom: 3rem;
}}

/* Fonds principaux : aplats solides (aucun filigrane repete ni fond fixe :
   beaucoup plus leger pour le rendu et le defilement).
   Le fond de la PAGE vient d'un theme JS (pas d'une variable CSS) : on force
   donc explicitement l'aplat de la palette, SINON le fond reste clair alors
   que le texte force est clair -> illisible en Sombre/Intermediaire. */
html, body,
[data-testid="stApp"], .stApp,
[data-testid="stAppViewContainer"] {{
    background: var(--ql-bg) !important;
    color: var(--ql-fg) !important;
}}
[data-testid="stHeader"] {{ background: var(--ql-bg) !important; }}
[data-testid="stToolbar"] {{ background: transparent !important; }}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}

/* Accents uniquement, completes par un recolorage du TEXTE du contenu : la
   coloration du texte Streamlit vient d'un theme JS (pas de variables CSS),
   on force donc explicitement la couleur du contenu, TOUJOURS en coherence
   avec le fond force (clair/sombre), pour un contraste garanti. */
a, a:visited {{ color: var(--ql-accent) !important; }}
::selection {{ background: {sel_bg}; }}

/* Texte du contenu principal (hors dialogues) */
.stApp p, .stApp li, .stApp label, .stApp caption,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp .stMarkdown, .stApp [data-testid="stMarkdownContainer"] {{
    color: var(--ql-fg);
}}

/* Champs de saisie et selecteurs */
input, textarea,
[data-baseweb="input"], [data-baseweb="input"] input,
[data-baseweb="select"] > div, [data-baseweb="textarea"] {{
    background-color: var(--ql-field) !important;
    color: var(--ql-fg) !important;
    border-color: var(--ql-border) !important;
}}
[data-baseweb="popover"], [role="listbox"], [role="option"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}

/* Onglets : indicateur de l'onglet actif, epais et immediatement lisible -----
   La barre de fond (tab-border) reste fine et neutre ; l'onglet actif recoit
   un filet epais (4 px) en degrade emeraude -> or, rehausse d'un leger halo.
   Les couleurs sont puisees dans la palette (--ql-*), donc l'indicateur se
   detache nettement dans les trois themes (Clair, Intermediaire, Sombre). */
.stTabs [data-baseweb="tab"] {{
    color: var(--ql-fg2) !important;
    font-weight: 600;
    padding-bottom: .7rem;
}}
.stTabs [aria-selected="true"] {{
    color: var(--ql-gold) !important;
    font-weight: 700 !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    height: 4px !important;
    border-radius: 4px 4px 0 0 !important;
    background: linear-gradient(
        90deg, var(--ql-accent), var(--ql-gold)
    ) !important;
    box-shadow: 0 0 8px var(--ql-gold-soft), 0 0 2px var(--ql-gold) !important;
}}
.stTabs [data-baseweb="tab-border"] {{
    height: 1px !important;
    background: var(--ql-border) !important;
}}

/* Boutons : glassmorphism, lisere dore, accent emeraude au survol */
.stButton > button {{
    border: 1px solid var(--ql-border) !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.05) 0%, 
        rgba(255,255,255,0.02) 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: var(--ql-fg) !important;
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 2px 8px -2px rgba(0, 0, 0, .15);
    transition: all .18s cubic-bezier(.2,.7,.3,1);
    position: relative;
    overflow: hidden;
}}
.stButton > button::after {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, 
        rgba(169,138,69,0) 0%, 
        rgba(169,138,69,0.12) 50%, 
        rgba(169,138,69,0) 100%);
    transform: translateX(-120%) skewX(-12deg);
    opacity: 0;
    transition: opacity .2s ease, transform .5s ease;
    pointer-events: none;
}}
.stButton > button:hover {{
    border-color: var(--ql-gold) !important;
    color: var(--ql-accent) !important;
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.08) inset,
        0 4px 16px -4px rgba(0, 0, 0, .2),
        0 0 0 1px var(--ql-gold-soft);
    transform: translateY(-1px);
}}
.stButton > button:hover::after {{
    opacity: 1;
    transform: translateX(120%) skewX(-12deg);
    animation: ql-sheen .6s ease;
}}
.stButton > button:active {{
    transform: translateY(0) scale(.99);
    transition-duration: .05s;
}}
.stButton > button:focus:not(:active) {{
    border-color: var(--ql-gold) !important;
    box-shadow: 0 0 0 3px var(--ql-gold-soft) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, var(--ql-accent) 0%, #0a4d3a 100%) !important;
    border-color: var(--ql-accent) !important;
    color: var(--ql-bg) !important;
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.1) inset,
        0 4px 16px -4px var(--ql-accent);
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.15) inset,
        0 6px 24px -6px var(--ql-accent),
        0 0 0 1px var(--ql-gold);
    transform: translateY(-1px);
}}

/* Encadres, expanders, alertes : glassmorphism + bord gauche orne */
[data-testid="stExpander"] {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.04) 0%, 
        rgba(255,255,255,0.01) 100%) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid var(--ql-border) !important;
    border-left: 4px solid var(--ql-gold) !important;
    border-radius: 14px;
    color: var(--ql-fg) !important;
    box-shadow: 0 4px 16px -4px rgba(0,0,0,0.15);
    transition: border-color .2s ease, box-shadow .2s ease;
}}
[data-testid="stExpander"]:hover {{
    border-left-color: var(--ql-accent) !important;
    box-shadow: 0 6px 20px -6px rgba(0,0,0,0.2);
}}
[data-testid="stExpander"] summary {{ 
    color: var(--ql-fg) !important; 
    font-weight: 600;
    letter-spacing: .01em;
}}
[data-testid="stAlert"] {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.05) 0%, 
        rgba(255,255,255,0.01) 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: var(--ql-fg) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 14px;
    box-shadow: 0 4px 16px -4px rgba(0,0,0,0.15);
}}
code, pre, .stCode, [data-testid="stCodeBlock"] {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.03) 0%, 
        rgba(255,255,255,0.01) 100%) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    color: var(--ql-fg) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 12px;
}}
hr {{ border-color: var(--ql-border) !important; }}
[data-testid="stSidebar"] hr {{
    height: 14px; border: none;
    background: var(--ql-ornament) center/130px 18px no-repeat;
    opacity: .85;
}}

/* Tableaux HTML internes (table.ql) - glassmorphism */
table.ql {{
    border-collapse: collapse;
    width: 100%;
    margin: 0.4rem 0 0.8rem 0;
    font-size: 0.92rem;
    border-radius: 14px;
    overflow: hidden;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.03) 0%, 
        rgba(255,255,255,0.01) 100%),
        var(--ql-bg2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px -4px rgba(0,0,0,0.2);
    animation: ql-rise .3s cubic-bezier(.2,.7,.3,1) both;
}}
table.ql th, table.ql td {{
    border: 1px solid var(--ql-border);
    padding: 8px 12px;
    text-align: left;
    color: var(--ql-fg);
    vertical-align: top;
    transition: background .2s ease;
}}
table.ql th {{
    background: linear-gradient(180deg, 
        rgba(169,138,69,0.12) 0%, 
        rgba(169,138,69,0.04) 100%);
    border-bottom: 2px solid var(--ql-gold);
    font-weight: 600;
    letter-spacing: .02em;
    text-transform: uppercase;
    font-size: .78rem;
}}
table.ql tr:nth-child(even) td {{ background-color: {zebra}; }}
table.ql tr:hover td {{
    background: linear-gradient(90deg, 
        rgba(169,138,69,0.06) 0%, 
        transparent 100%) !important;
}}

/* Surcharge pour rendre les lignes cliquables (onglet Ecouter) */
table.ql.ql-clickable tbody tr {{
    cursor: pointer;
    transition: background .18s ease, transform .18s ease;
}}
table.ql.ql-clickable tbody tr:hover {{
    background: rgba(169,138,69,0.12) !important;
    transform: translateX(3px);
}}
table.ql.ql-clickable tbody tr:active {{
    transform: translateX(1px) scale(.998);
}}

/* Tableaux de donnees natifs : rien a forcer, le texte suit --text-color. */

/* --- Bandeau d'en-tete (banner) : enluminure geometrique + glassmorphism -- */
.ql-banner {{
    position: relative;
    padding: 2rem 2.2rem 1.6rem 2.2rem;
    margin: 0 0 1.5rem 0;
    border: 1px solid var(--ql-border);
    border-radius: 22px;
    background:
        radial-gradient(ellipse 140% 100% at 50% -20%, {glow}, transparent 65%),
        linear-gradient(135deg, 
            rgba(255,255,255,0.04) 0%, 
            rgba(255,255,255,0.01) 50%, 
            rgba(255,255,255,0.02) 100%),
        var(--ql-mosaic) center/260px 260px,
        var(--ql-bg2);
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    box-shadow: 
        0 20px 50px -28px rgba(0, 0, 0, .55),
        0 0 0 1px rgba(169,138,69,0.08) inset;
    overflow: hidden;
    animation: ql-rise .5s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-banner::before {{
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 3px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    background-size: 35% 100%;
    background-repeat: no-repeat;
    opacity: .95;
    animation: ql-sheen-line 8s ease-in-out infinite;
}}
.ql-banner::after {{
    content: "";
    position: absolute;
    left: 20%; right: 20%; bottom: 0;
    height: 1px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    opacity: .45;
}}
/* cadre interieur delicat */
.ql-inset {{
    position: absolute;
    inset: 10px;
    border: 1px solid var(--ql-border);
    border-radius: 16px;
    opacity: .5;
    pointer-events: none;
}}
/* fleurons d'angle (equerres fines, facon feuille d'arabesque) */
.ql-corner {{
    position: absolute;
    width: 18px; height: 18px;
    pointer-events: none;
    transition: transform .3s ease;
}}
.ql-banner:hover .ql-corner {{ transform: scale(1.15); }}
.ql-corner::before, .ql-corner::after {{
    content: "";
    position: absolute;
    background: var(--ql-gold);
    opacity: .85;
}}
.ql-corner::before {{ width: 1.5px; height: 100%; }}
.ql-corner::after  {{ width: 100%; height: 1.5px; }}
.ql-c-tl {{ top: 6px; left: 6px; }}
.ql-c-tr {{ top: 6px; right: 6px; transform: rotate(90deg); }}
.ql-c-br {{ bottom: 6px; right: 6px; transform: rotate(180deg); }}
.ql-c-bl {{ bottom: 6px; left: 6px; transform: rotate(-90deg); }}
/* nappe calligraphique arabe au-dessus du titre */
.ql-banner .ql-ar {{
    margin: 0 0 .15rem 0;
    text-align: center;
    font-family: var(--ql-font-ar);
    font-size: 1.3rem;
    line-height: 1.35;
    letter-spacing: .015em;
    color: var(--ql-gold);
    opacity: .95;
    transition: transform .3s ease, text-shadow .3s ease;
}}
.ql-banner:hover .ql-ar {{
    transform: scale(1.05);
    text-shadow: 0 2px 16px var(--ql-gold-soft);
}}
.ql-banner .ql-title {{
    margin: 0;
    text-align: center;
    font-family: var(--ql-heading);
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: .14em;
    color: var(--ql-fg);
    line-height: 1.2;
    background: linear-gradient(135deg, var(--ql-fg) 0%, var(--ql-gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.ql-banner .ql-rule {{
    width: 140px;
    height: 18px;
    margin: .7rem auto .1rem auto;
    background: var(--ql-ornament) center/140px 18px no-repeat;
    opacity: .9;
}}
.ql-banner .ql-subtitle {{
    margin: .5rem auto 0 auto;
    text-align: center;
    color: var(--ql-fg2);
    font-size: 1rem;
    max-width: 56rem;
    line-height: 1.5;
}}

/* Petit habillage des titres Streamlit natifs (hors bandeau) : filet dore */
.stApp h2 {{
    border-bottom: 1px solid var(--ql-border);
    padding-bottom: .3rem;
    box-shadow: 0 6px 10px -12px var(--ql-gold);
}}

/* --- Cartes & conteneurs (.ql-card) : composition << prestige >> -----------
   Glassmorphism moderne : fond semi-transparent, blur, bordure lumineuse.
   Animations au scroll + micro-interactions au survol. */
.ql-card {{
    position: relative;
    display: flex;
    flex-direction: column;
    gap: .32rem;
    height: 100%;
    padding: 1.05rem .9rem .9rem .9rem;
    border: 1px solid var(--ql-border);
    border-radius: 18px;
    background:
        linear-gradient(135deg, 
            rgba(255,255,255,0.06) 0%, 
            rgba(255,255,255,0.02) 50%, 
            rgba(255,255,255,0.03) 100%),
        var(--ql-bg2);
    backdrop-filter: blur(16px) saturate(140%);
    -webkit-backdrop-filter: blur(16px) saturate(140%);
    color: var(--ql-fg);
    text-align: center;
    overflow: hidden;
    isolation: isolate;
    -webkit-tap-highlight-color: transparent;
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.04) inset,
        0 4px 20px -6px rgba(0, 0, 0, .25),
        0 20px 40px -24px rgba(0, 0, 0, .4);
    transition: transform .28s cubic-bezier(.2, .7, .3, 1),
                box-shadow .28s ease, border-color .28s ease;
    animation: ql-rise .4s cubic-bezier(.2, .7, .3, 1) both;
    animation-delay: var(--ql-delay, 0ms);
    will-change: transform, box-shadow;
}}
.ql-card::before {{
    /* filet dore en tete de carte, discret */
    content: "";
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1.5px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    opacity: .5;
    transition: opacity .28s ease, width .28s ease;
}}
.ql-card::after {{
    /* eclat lumineux qui balaie la carte au survol */
    content: "";
    position: absolute;
    top: 0; bottom: 0; left: 0;
    width: 60%;
    background: linear-gradient(
        100deg, transparent, rgba(169,138,69,0.18), transparent
    );
    transform: translateX(-180%) skewX(-18deg);
    opacity: 0;
    pointer-events: none;
    z-index: 1;
}}
.ql-card:hover {{
    transform: translateY(-6px) scale(1.018);
    border-color: var(--ql-gold);
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.06) inset,
        0 12px 32px -8px rgba(0, 0, 0, .3),
        0 28px 50px -24px rgba(0, 0, 0, .45),
        0 0 0 1px var(--ql-gold-soft);
}}
.ql-card:hover::before {{ opacity: 1; width: 80%; left: 10%; }}
.ql-card:hover::after {{ opacity: 1; animation: ql-sheen .9s ease; }}
.ql-card:active {{
    transform: translateY(-2px) scale(.995);
    transition-duration: .08s;
}}
/* halo dore sur le glyphe arabe au survol : la carte << repond >> au doigt */
.ql-card:hover .ql-ar {{
    transform: scale(1.08);
    text-shadow: 0 4px 20px {gold_glow};
}}
.ql-card .ql-ar {{
    transition: transform .28s cubic-bezier(.2, .7, .3, 1),
                text-shadow .28s ease;
}}
/* petit fleuron d'angle (rosette geometrique, 100 % CSS) */
.ql-card .ql-orn {{
    position: absolute;
    top: 10px; right: 10px;
    width: 14px; height: 14px;
    opacity: .3;
    transition: opacity .28s ease, transform .45s cubic-bezier(.2,.7,.3,1);
    pointer-events: none;
    z-index: 2;
}}
.ql-card .ql-orn::before, .ql-card .ql-orn::after {{
    content: "";
    position: absolute;
    inset: 0;
    border: 1px solid var(--ql-gold);
    border-radius: 3px;
}}
.ql-card .ql-orn::after {{ transform: rotate(45deg); }}
.ql-card:hover .ql-orn {{ opacity: .95; transform: rotate(45deg) scale(1.1); }}
.ql-card .ql-ar,
.ql-ar {{ font-family: var(--ql-font-ar); color: var(--ql-accent); }}
.ql-card .ql-ar {{
    font-size: 1.9rem;
    line-height: 1.5;
    text-align: center;
}}
.ql-ar-num {{ font-size: 1.75rem; }}
.ql-ar-xl {{ font-size: 2.1rem; }}
.ql-card .ql-name {{
    font-weight: 600;
    font-size: .95rem;
    letter-spacing: .01em;
}}
.ql-card .ql-tr {{ color: var(--ql-fg2); font-size: .8rem; }}
.ql-card .ql-gloss {{
    color: var(--ql-fg);
    font-size: .86rem;
    min-height: 1.1rem;
}}
.ql-card .ql-meta {{ color: var(--ql-fg2); font-size: .72rem; }}
.ql-card .ql-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .4rem;
    font-size: .72rem;
    color: var(--ql-fg2);
}}
.ql-card .ql-sep {{
    margin-top: auto;
    padding-top: .4rem;
    border-top: 1px solid var(--ql-border);
    font-size: .78rem;
    color: var(--ql-fg);
    text-align: left;
}}
.ql-card .ql-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.9rem;
    height: 1.9rem;
    border-radius: 50%;
    font-size: 1rem;
    flex: none;
}}
.ql-accent {{ color: var(--ql-accent) !important; }}
/* En-tete de signe (soukoun / chaddah / tanwin) : carte alignee a gauche */
.ql-card.ql-mark {{ text-align: left; gap: .2rem; }}
.ql-card.ql-mark .ql-head {{ font-size: .82rem; }}
.ql-forms {{ display: flex; gap: 3px; margin-top: .4rem; }}
.ql-forms span {{
    flex: 1;
    padding: .14rem 0;
    border-radius: 7px;
    background: var(--ql-bg);
    color: var(--ql-fg);
    font-size: 1.05rem;
}}

/* --- Versets (onglet << Lire >>) : reference ornee, verset cible ----------- */
.ql-verse-anchor {{ display: block; height: 0; }}
.ql-verse-ref {{
    display: flex;
    align-items: center;
    gap: .6rem;
    margin: .2rem 0;
    padding-left: .4rem;
    border-left: 2px solid var(--ql-gold);
    opacity: .9;
    transition: opacity .2s ease, border-color .2s ease;
}}
.ql-verse-ref:hover {{
    opacity: 1;
    border-left-color: var(--ql-accent);
}}
.ql-verse-ref .ql-ref-num {{
    font-family: var(--ql-heading);
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--ql-accent);
    letter-spacing: .02em;
    background: linear-gradient(135deg, var(--ql-accent) 0%, var(--ql-gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.ql-verse-ar {{
    font-family: var(--ql-font-ar);
    line-height: 2.5;
    margin: .25rem 0 .6rem 0;
    font-size: 1.2rem;
    color: var(--ql-fg);
    transition: transform .2s ease;
}}
.ql-verse-ar:hover {{
    transform: translateX(2px);
}}
.ql-target {{
    border-left: 3px solid var(--ql-gold);
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.18) 0%, 
        rgba(12,92,70,0.12) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: .4rem .85rem;
    border: 1px solid rgba(169,138,69,0.2);
    animation: ql-slide-in-right .3s cubic-bezier(.2,.7,.3,1) both;
}}

/* --- Surbrillance de recherche (onglet Recherche) ------------------------
   Glassmorphism, fond emeraude dore, lisible dans les trois palettes. */
mark.ql-hit {{
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.35) 0%, 
        rgba(12,92,70,0.25) 100%);
    color: inherit;
    padding: .04em .14em;
    border-radius: 5px;
    box-shadow: 
        inset 0 -2px 0 var(--ql-gold),
        0 1px 3px -1px rgba(0,0,0,0.2);
    font-weight: 600;
    border: 1px solid rgba(169,138,69,0.3);
    animation: ql-fade-in .2s ease-out;
}}

/* --- Synthese convergente (encadre sous les traductions) -----------------
   Glassmorphism, lisere dore, fond degrade emeraude, en-tete petites capitales. */
.ql-synth {{
    margin: .6rem 0 .3rem 0;
    padding: 1rem 1.1rem .85rem 1.1rem;
    border: 1px solid var(--ql-gold);
    border-left: 4px solid var(--ql-accent);
    border-radius: 16px;
    background: linear-gradient(135deg, 
        rgba(12,92,70,0.12) 0%, 
        rgba(12,92,70,0.04) 50%, 
        transparent 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 
        0 1px 0 rgba(169,138,69,0.1) inset,
        0 4px 16px -4px rgba(0,0,0,0.12);
    animation: ql-rise .35s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-synth-head {{
    font-family: var(--ql-font);
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
    color: var(--ql-accent);
    margin-bottom: .15rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}}
.ql-synth-head::before {{
    content: "";
    width: 24px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--ql-gold), transparent);
}}
.ql-synth-note {{
    font-size: .74rem;
    color: var(--ql-fg2);
    margin-bottom: .5rem;
    line-height: 1.5;
}}
.ql-synth-terms {{
    display: flex;
    flex-wrap: wrap;
    gap: .3rem;
}}
.ql-synth-term {{
    display: inline-flex;
    align-items: center;
    gap: .28rem;
    padding: .16rem .5rem .16rem .55rem;
    border: 1px solid var(--ql-gold);
    border-radius: 999px;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.04) 0%, 
        rgba(255,255,255,0.01) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--ql-fg);
    font-size: .8rem;
    line-height: 1.4;
    transition: all .2s ease;
    animation: ql-slide-in-right .35s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-synth-term:hover {{
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.18) 0%, 
        rgba(169,138,69,0.08) 100%);
    border-color: var(--ql-accent);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px -2px var(--ql-gold-soft);
}}
.ql-synth-n {{
    font-size: .64rem;
    font-weight: 700;
    color: var(--ql-bg);
    background: linear-gradient(135deg, var(--ql-accent) 0%, #0a4d3a 100%);
    border-radius: 999px;
    padding: .02rem .3rem;
    box-shadow: 0 1px 3px -1px rgba(0,0,0,0.3);
}}
.ql-synth-foot {{
    margin-top: .55rem;
    font-size: .68rem;
    color: var(--ql-fg2);
    border-top: 1px solid var(--ql-border);
    padding-top: .35rem;
    line-height: 1.5;
}}

/* --- Navigation rapide flottante (haut / bas de page) --------------------
   Widget discret ancre a droite a ~30% du haut : deux boutons empiles --
   remonter (^) et descendre (v) -- en emeraude rehausse d'un filet dore.
   Glassmorphism. */
.ql-scroll-nav {{
    position: fixed;
    right: 18px;
    top: 30vh;
    z-index: 999990;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid var(--ql-gold);
    border-radius: 18px;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.06) 0%, 
        rgba(255,255,255,0.02) 100%) !important;
    backdrop-filter: blur(20px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
    box-shadow: 
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 12px 36px -16px rgba(0, 0, 0, .6);
    opacity: 0;
    visibility: hidden;
    transform: translateY(12px) scale(0.95);
    transition: opacity .3s ease, transform .3s cubic-bezier(.2,.7,.3,1), visibility .3s ease;
    pointer-events: none;
}}
.ql-scroll-nav.ql-visible {{
    opacity: 1;
    visibility: visible;
    transform: none;
    pointer-events: auto;
}}
.ql-scroll-nav button {{
    width: 48px;
    height: 48px;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: 0;
    background: linear-gradient(135deg, var(--ql-accent) 0%, #0a4d3a 100%);
    color: var(--ql-bg);
    font-family: var(--ql-font);
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1;
    -webkit-tap-highlight-color: transparent;
    transition: all .15s ease;
    position: relative;
    overflow: hidden;
}}
.ql-scroll-nav button::after {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0) 0%, 
        rgba(255,255,255,0.18) 50%, 
        rgba(255,255,255,0) 100%);
    transform: translateX(-120%) skewX(-12deg);
    opacity: 0;
    transition: opacity .2s ease, transform .5s ease;
    pointer-events: none;
}}
.ql-scroll-nav button + button {{
    border-top: 1px solid var(--ql-gold);
}}
.ql-scroll-nav button:hover {{
    box-shadow: inset 0 0 0 2px var(--ql-gold), 0 0 16px var(--ql-gold-soft);
    filter: brightness(1.1);
}}
.ql-scroll-nav button:hover::after {{
    opacity: 1;
    transform: translateX(120%) skewX(-12deg);
    animation: ql-sheen .5s ease;
}}
.ql-scroll-nav button:active {{
    filter: brightness(.95);
    transform: scale(.97);
}}
.ql-scroll-nav button:focus-visible {{
    outline: 2px solid var(--ql-gold);
    outline-offset: -3px;
}}

/* --- Modale st.dialog : glassmorphism */
[data-testid="stDialog"] {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.04) 0%, 
        rgba(255,255,255,0.01) 100%) !important;
    backdrop-filter: blur(24px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 22px !important;
    color: var(--ql-fg) !important;
    box-shadow: 
        0 24px 60px -20px rgba(0, 0, 0, .7),
        0 0 0 1px rgba(169,138,69,0.1) inset !important;
}}
[data-testid="stDialog"] > div:first-child {{
    border-radius: 22px !important;
}}
[data-testid="stDialog"] p, [data-testid="stDialog"] li,
[data-testid="stDialog"] label, [data-testid="stDialog"] caption,
[data-testid="stDialog"] h1, [data-testid="stDialog"] h2,
[data-testid="stDialog"] h3, [data-testid="stDialog"] h4,
[data-testid="stDialog"] h5, [data-testid="stDialog"] h6,
[data-testid="stDialog"] .stMarkdown,
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] {{
    color: var(--ql-fg) !important;
}}
[data-testid="stDialog"] [data-testid="stExpander"] {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.04) 0%, 
        rgba(255,255,255,0.01) 100%) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    color: var(--ql-fg) !important;
}}
[data-testid="stDialog"] hr {{ border-color: var(--ql-border) !important; }}
[data-testid="stDialog"] .stButton > button {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.08) 0%, 
        rgba(255,255,255,0.03) 100%) !important;
}}

/* --- Confort mobile : l'app installee (PWA) reste lisible et tactile ---- */
@media (max-width: 780px) {{
    [data-testid="stMainBlockContainer"], .block-container {{
        padding-left: .9rem !important;
        padding-right: .9rem !important;
    }}
    .ql-banner {{ padding: 1.2rem 1rem 1.05rem 1rem; border-radius: 15px; }}
    .ql-banner .ql-title {{ font-size: 1.6rem; letter-spacing: .08em; }}
    .ql-banner .ql-ar {{ font-size: 1.02rem; }}
    .ql-card {{ padding: .85rem .6rem; border-radius: 14px; gap: .26rem; }}
    .ql-card .ql-ar {{ font-size: 1.75rem; }}
    .ql-card .ql-ar.ql-ar-xl {{ font-size: 1.85rem; }}
    .ql-card .ql-ar.ql-ar-num {{ font-size: 1.6rem; }}
    .stApp h2 {{ font-size: 1.35rem; }}
    .stButton > button {{ min-height: 2.75rem; }}
    .ql-scroll-nav {{
        right: 12px;
        bottom: calc(16px + env(safe-area-inset-bottom, 0px));
        border-radius: 13px;
    }}
    .ql-scroll-nav button {{ width: 42px; height: 42px; font-size: 1.15rem; }}
    .stTabs [data-baseweb="tab"] {{
        padding-left: .5rem;
        padding-right: .5rem;
        font-size: .9rem;
    }}
    /* 16 px minimum : evite le zoom automatique des champs sur iOS */
    input, textarea, select {{ font-size: 16px !important; }}
}}
@media (max-width: 420px) {{
    .ql-card {{ padding: .7rem .45rem; gap: .22rem; }}
    .ql-card .ql-gloss {{ font-size: .82rem; }}
    .ql-card .ql-ar {{ font-size: 1.6rem; }}
}}

/* --- Glassmorphism utilities ------------------------------------------------ */
.ql-glass {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.08) 0%, 
        rgba(255,255,255,0.02) 50%, 
        rgba(255,255,255,0.04) 100%) !important;
    backdrop-filter: blur(18px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 
        0 8px 32px -8px rgba(0,0,0,0.3),
        inset 0 1px 0 rgba(255,255,255,0.1) !important;
}}
.ql-glass-light {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.25) 0%, 
        rgba(255,255,255,0.1) 50%, 
        rgba(255,255,255,0.15) 100%) !important;
    backdrop-filter: blur(20px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
    border: 1px solid rgba(169,138,69,0.2) !important;
    box-shadow: 
        0 4px 24px -4px rgba(0,0,0,0.15),
        inset 0 1px 0 rgba(255,255,255,0.3) !important;
}}

/* --- Scroll Reveal (entree progressive au scroll) ---------------------------
   Utilisation : ajouter la classe .ql-reveal aux elements a animer.
   Le script d'observation (dans app.py) pose .ql-visible quand l'element
   entre dans le viewport. Les delais sont geres via --ql-delay (ms). */
.ql-reveal {{
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s cubic-bezier(.2,.7,.3,1),
                transform 0.6s cubic-bezier(.2,.7,.3,1);
    transition-delay: var(--ql-delay, 0ms);
    will-change: opacity, transform;
}}
.ql-reveal.ql-visible {{
    opacity: 1;
    transform: none;
}}
/* Variantes de direction */
.ql-reveal-left {{
    transform: translateX(-32px);
}}
.ql-reveal-left.ql-visible {{
    transform: none;
}}
.ql-reveal-right {{
    transform: translateX(32px);
}}
.ql-reveal-right.ql-visible {{
    transform: none;
}}
.ql-reveal-scale {{
    transform: scale(0.92);
}}
.ql-reveal-scale.ql-visible {{
    transform: none;
}}

/* Stagger delays automatiques pour les grilles (premier = 0ms, +60ms/item) */
.ql-stagger > *:nth-child(1)  {{ --ql-delay: 0ms;   }}
.ql-stagger > *:nth-child(2)  {{ --ql-delay: 60ms;  }}
.ql-stagger > *:nth-child(3)  {{ --ql-delay: 120ms; }}
.ql-stagger > *:nth-child(4)  {{ --ql-delay: 180ms; }}
.ql-stagger > *:nth-child(5)  {{ --ql-delay: 240ms; }}
.ql-stagger > *:nth-child(6)  {{ --ql-delay: 300ms; }}
.ql-stagger > *:nth-child(7)  {{ --ql-delay: 360ms; }}
.ql-stagger > *:nth-child(8)  {{ --ql-delay: 420ms; }}
.ql-stagger > *:nth-child(9)  {{ --ql-delay: 480ms; }}
.ql-stagger > *:nth-child(10) {{ --ql-delay: 540ms; }}
.ql-stagger > *:nth-child(11) {{ --ql-delay: 600ms; }}
.ql-stagger > *:nth-child(12) {{ --ql-delay: 660ms; }}

/* --- Animations : entree en cascade, eclats -- transform/opacity seuls,
   acceleres par le GPU, donc fluides meme sur mobile/PWA ------------------- */
@keyframes ql-rise {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: none; }}
}}
@keyframes ql-sheen {{
    from {{ transform: translateX(-160%) skewX(-16deg); }}
    to   {{ transform: translateX(260%) skewX(-16deg); }}
}}
@keyframes ql-sheen-line {{
    0%   {{ background-position: -60% 0; }}
    55%  {{ background-position: 160% 0; }}
    100% {{ background-position: 160% 0; }}
}}
@keyframes ql-pulse {{
    0%   {{ box-shadow: 0 0 0 0 {gold_glow}; }}
    70%  {{ box-shadow: 0 0 0 8px transparent; }}
    100% {{ box-shadow: 0 0 0 0 transparent; }}
}}
@keyframes ql-float {{
    0%, 100% {{ transform: translateY(0); }}
    50%      {{ transform: translateY(-4px); }}
}}
@keyframes ql-glow-pulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 var(--ql-gold-soft); }}
    50%      {{ box-shadow: 0 0 0 6px var(--ql-gold-soft); }}
}}
@keyframes ql-slide-in-right {{
    from {{ opacity: 0; transform: translateX(20px); }}
    to   {{ opacity: 1; transform: none; }}
}}
@keyframes ql-fade-in {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}

/* Classes utilitaires d'animation */
.ql-float {{
    animation: ql-float 3.5s ease-in-out infinite;
}}
.ql-glow-pulse {{
    animation: ql-glow-pulse 2.5s ease-in-out infinite;
}}
.ql-slide-in {{
    animation: ql-slide-in-right 0.5s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-fade-in {{
    animation: ql-fade-in 0.4s ease-out both;
}}

/* Tactile : pas de survol persistant ; l'appui direct donne le retour visuel */
@media (hover: none) {{
    .ql-card:hover {{
        transform: none;
        border-color: var(--ql-border);
        box-shadow: 0 1px 0 {card_edge} inset,
                    0 2px 4px -1px rgba(0, 0, 0, .06),
                    0 14px 30px -22px rgba(0, 0, 0, .55);
    }}
    .ql-card:hover .ql-orn {{ opacity: .35; transform: none; }}
    .ql-card:active {{
        transform: scale(.985);
        border-color: var(--ql-gold);
        box-shadow: 0 0 0 1px {gold_soft};
    }}
}}

/* --- Audio Player (onglet Ecoute) ------------------------------------------ */
.ql-audio-player {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.04) 0%, 
        rgba(255,255,255,0.01) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--ql-border);
    border-radius: 18px;
    padding: 1.2rem;
    box-shadow: 0 8px 32px -8px rgba(0,0,0,0.25);
    animation: ql-rise .4s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-audio-player .ql-player-head {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}}
.ql-audio-player .ql-surah-badge {{
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    padding: .4rem .8rem;
    background: linear-gradient(135deg, var(--ql-accent) 0%, #0a4d3a 100%);
    border-radius: 999px;
    font-weight: 600;
    font-size: .85rem;
    color: #FDF6E3;
    box-shadow: 0 2px 10px -2px var(--ql-accent);
}}
.ql-audio-player .ql-mode-pills {{
    display: flex;
    gap: .5rem;
    flex-wrap: wrap;
}}
.ql-audio-player .ql-mode-pill {{
    padding: .35rem .85rem;
    border: 1px solid var(--ql-border);
    border-radius: 999px;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.03) 0%, 
        rgba(255,255,255,0.01) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--ql-fg2);
    font-size: .78rem;
    font-weight: 500;
    cursor: pointer;
    transition: all .2s ease;
}}
.ql-audio-player .ql-mode-pill.active,
.ql-audio-player .ql-mode-pill:hover {{
    border-color: var(--ql-gold);
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.18) 0%, 
        rgba(12,92,70,0.12) 100%);
    color: var(--ql-fg);
}}
.ql-audio-player .ql-mode-pill.active {{
    box-shadow: 0 0 0 1px var(--ql-gold-soft);
}}
.ql-audio-player .ql-controls {{
    display: flex;
    align-items: center;
    gap: .75rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}}
.ql-audio-player .ql-btn {{
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .55rem 1.1rem;
    border: 1px solid var(--ql-border);
    border-radius: 12px;
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.05) 0%, 
        rgba(255,255,255,0.02) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: var(--ql-fg);
    font-size: .85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .18s cubic-bezier(.2,.7,.3,1);
}}
.ql-audio-player .ql-btn:hover {{
    border-color: var(--ql-gold);
    color: var(--ql-accent);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px -4px rgba(0,0,0,0.2);
}}
.ql-audio-player .ql-btn.primary {{
    background: linear-gradient(135deg, var(--ql-accent) 0%, #0a4d3a 100%);
    border-color: var(--ql-accent);
    color: var(--ql-bg);
}}
.ql-audio-player .ql-btn.primary:hover {{
    box-shadow: 0 6px 20px -6px var(--ql-accent);
}}
.ql-audio-player .ql-time {{
    font-family: var(--ql-font);
    font-size: .95rem;
    font-variant-numeric: tabular-nums;
    color: var(--ql-fg2);
    min-width: 90px;
    text-align: center;
}}
.ql-audio-player .ql-progress {{
    flex: 1;
    min-width: 120px;
    height: 4px;
    background: rgba(169,138,69,0.15);
    border-radius: 999px;
    overflow: hidden;
    margin: 0 .5rem;
}}
.ql-audio-player .ql-progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, var(--ql-accent) 0%, var(--ql-gold) 100%);
    border-radius: 999px;
    transition: width .15s linear;
    box-shadow: 0 0 8px var(--ql-gold-soft);
}}
.ql-audio-player .ql-next-surah {{
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .4rem .8rem;
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.12) 0%, 
        transparent 100%);
    border: 1px solid var(--ql-gold);
    border-radius: 999px;
    color: var(--ql-gold);
    font-size: .78rem;
    font-weight: 500;
    transition: all .2s ease;
}}
.ql-audio-player .ql-next-surah:hover {{
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.22) 0%, 
        rgba(169,138,69,0.1) 100%);
    transform: translateX(3px);
}}

/* --- Multi-Traductions (affichage verset) ---------------------------------- */
.ql-translations {{
    margin: .5rem 0;
}}
.ql-translation {{
    background: linear-gradient(135deg, 
        rgba(255,255,255,0.02) 0%, 
        rgba(255,255,255,0.005) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid var(--ql-border);
    border-left: 3px solid var(--ql-gold);
    border-radius: 12px;
    padding: .7rem .9rem;
    margin-bottom: .5rem;
    animation: ql-rise .3s cubic-bezier(.2,.7,.3,1) both;
}}
.ql-translation:hover {{
    border-left-color: var(--ql-accent);
    box-shadow: 0 2px 10px -2px rgba(0,0,0,0.1);
}}
.ql-translation-header {{
    display: flex;
    align-items: baseline;
    gap: .6rem;
    margin-bottom: .35rem;
    flex-wrap: wrap;
}}
.ql-translation-author {{
    font-family: var(--ql-heading);
    font-weight: 600;
    font-size: .88rem;
    color: var(--ql-accent);
}}
.ql-translation-lang {{
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .05em;
    text-transform: uppercase;
    color: var(--ql-fg2);
    background: rgba(169,138,69,0.15);
    padding: .08rem .45rem;
    border-radius: 999px;
}}
.ql-translation-text {{
    line-height: 1.7;
    color: var(--ql-fg);
    font-size: .95rem;
}}
.ql-translations-toggle {{
    margin: .5rem 0 1rem 0;
    padding: .6rem 1.2rem;
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.08) 0%, 
        transparent 100%);
    border: 1px solid var(--ql-gold);
    border-radius: 10px;
    color: var(--ql-gold);
    font-weight: 600;
    font-size: .85rem;
    cursor: pointer;
    transition: all .2s ease;
}}
.ql-translations-toggle:hover {{
    background: linear-gradient(135deg, 
        rgba(169,138,69,0.18) 0%, 
        rgba(169,138,69,0.08) 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px -4px var(--ql-gold-soft);
}}
{_illuminated_css()}
</style>
"""
    return f"<style>{css_content}</style>"
