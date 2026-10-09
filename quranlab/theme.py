"""Gestionnaire de thèmes visuels (Clair / Intermédiaire / Sombre).

Fournit, pour chaque palette, une feuille de style CSS injectée dynamiquement
dans Streamlit via ``st.markdown(..., unsafe_allow_html=True)``.  Les couleurs
sont exposées en variables CSS (``--ql-*``) afin d'habiller uniformément les
composants Streamlit et les tableaux HTML internes (``table.ql``).

La charte intègre de **subtiles touches d'art géométrique islamique** : un
motif de mosaïque (étoile à huit branches / zéllij) répété en filigrane en
arrière-plan, des bordures ornées de cartes et un bandeau d'en-tête à
l'inspiration calligraphique.  Les motifs restent volontairement discrets
(opacité très basse) pour préserver la lisibilité et la rigueur de l'étude.
"""

from urllib.parse import quote

# Chaque palette définit un jeu cohérent de variables.
PALETTES = {
    "Clair": {
        "label": "Clair (blanc cassé)",
        "bg": "#F7F5F0",       # fond blanc cassé
        "bg2": "#ECE7DD",      # barre latérale / surfaces secondaires
        "field": "#FFFFFF",    # champs de saisie
        "fg": "#23272B",       # texte gris très foncé
        "fg2": "#555B61",      # texte secondaire
        "border": "#D8D2C6",
        "accent": "#0B6E4F",
        "pattern": "#0B6E4F",  # couleur du motif de mosaïque
        "pattern_opacity": "0.06",
    },
    "Intermediaire": {
        "label": "Intermédiaire (bleu-gris / confort oculaire)",
        "bg": "#1E293B",       # ardoise feutrée
        "bg2": "#273449",
        "field": "#243146",
        "fg": "#F1F5F9",       # texte doux et lisible
        "fg2": "#CBD5E1",
        "border": "#3B4A61",
        "accent": "#7DD3FC",
        "pattern": "#7DD3FC",
        "pattern_opacity": "0.07",
    },
    "Sombre": {
        "label": "Sombre (gris-noir profond)",
        "bg": "#16181D",       # pas de noir pur
        "bg2": "#1F232B",
        "field": "#22262E",
        "fg": "#E6E8EB",
        "fg2": "#A3A9B3",
        "border": "#333A44",
        "accent": "#4FB286",
        "pattern": "#8FB8A6",
        "pattern_opacity": "0.10",
    },
}

# Ordre d'affichage dans le sélecteur.
ORDER = ["Clair", "Intermediaire", "Sombre"]

DEFAULT = "Clair"

# Pile de polices latines (repli système, aucune dépendance externe).
FONT_STACK = (
    '"Inter", "Segoe UI", "Helvetica Neue", Arial, "Noto Sans", sans-serif'
)
# Pile de polices arabes (si installées localement, sinon repli système).
ARABIC_STACK = (
    '"Amiri", "Scheherazade New", "Traditional Arabic", "Noto Naskh Arabic", '
    '"Times New Roman", serif'
)


def _mosaic_svg(color: str, opacity: str) -> str:
    """Motif de mosaïque (étoile à huit branches + quartiers) en data-URI SVG.

    L'étoile est obtenue par deux carrés superposés dont l'un pivoté de 45° ;
    un quadrillage fin et des demi-étoiles de coin assurent la continuité du
    pavage. Le SVG est encodé en data-URI pour être posé en ``background-image``.
    """
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='128' height='128' "
        "viewBox='0 0 128 128'>"
        f"<g fill='none' stroke='{color}' stroke-width='0.9' "
        f"opacity='{opacity}'>"
        # étoile à huit branches centrée sur la tuile
        "<rect x='32' y='32' width='64' height='64'/>"
        "<rect x='32' y='32' width='64' height='64' "
        "transform='rotate(45 64 64)'/>"
        "<circle cx='64' cy='64' r='12'/>"
        "<circle cx='64' cy='64' r='4.5'/>"
        # demi-étoiles aux coins : continuité du pavage
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
    """Petit fleuron calligraphique (losange + étoile) pour les titres."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='16' "
        "viewBox='0 0 120 16'>"
        f"<g fill='none' stroke='{color}' stroke-width='1' opacity='0.75'>"
        "<path d='M0 8 H44 M76 8 H120'/>"
        "<rect x='52' y='1' width='14' height='14' transform='rotate(45 59 8)'/>"
        f"<circle cx='59' cy='8' r='2.4' fill='{color}'/>"
        "</g></svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


def _rgba(hex_color: str, alpha: float) -> str:
    """Convertit une couleur hexadécimale en rgba(…) pour les calques doux."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def css(name: str) -> str:
    """Retourne la feuille de style pour la palette demandée."""
    p = PALETTES.get(name, PALETTES[DEFAULT])
    ornament = _ornament_svg(p["pattern"])
    zebra = _rgba(p["bg2"], 0.5)
    sel_bg = _rgba(p["accent"], 0.28)
    return f"""
<style>
:root {{
    --ql-bg: {p['bg']};
    --ql-bg2: {p['bg2']};
    --ql-field: {p['field']};
    --ql-fg: {p['fg']};
    --ql-fg2: {p['fg2']};
    --ql-border: {p['border']};
    --ql-accent: {p['accent']};
    --ql-ornament: url("{ornament}");
    --ql-font: {FONT_STACK};
    --ql-font-ar: {ARABIC_STACK};
}}

/* Typographie : la police est posée sur le conteneur puis héritée. On évite
   tout sélecteur « * » ou « span » global qui écraserait les fontes dédiées
   (code, icônes Material de Streamlit : chevrons, coches, ...). */
.stApp, [data-testid="stSidebar"] {{
    font-family: var(--ql-font);
}}
.stApp input, .stApp textarea,
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {{
    font-family: var(--ql-font);
}}
.stApp [dir="rtl"], .stApp [lang="ar"] {{ font-family: var(--ql-font-ar); }}

/* Icônes Material de Streamlit (chevron _arrow_right_, coches, flèches de
   sélecteurs) : maintenir LA police d'icônes, jamais celle du texte courant.
   Sinon l'identifiant s'affiche en clair (ex. « arrow_right ») et déborde sur
   le libellé voisin. */
[class*="material"], [class*="Material"], [class*="sticon"],
[data-testid*="icon"] {{
    font-family: "Material Symbols Rounded", "Material Symbols Outlined",
        "Material Icons Rounded", "Material Icons", "Material Icons Outlined";
    font-variant-ligatures: normal;
    letter-spacing: normal;
}}

/* Fonds principaux : aplats solides (aucun filigrane répété ni fond fixé :
   beaucoup plus léger pour le rendu et le défilement) */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
    background-color: var(--ql-bg2) !important;
}}

/* Texte */
.stApp, .stApp p, .stApp li, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp .stMarkdown, [data-testid="stSidebar"] {{
    color: var(--ql-fg);
}}
.stApp h1, .stApp h2, .stApp h3 {{ color: var(--ql-fg) !important; }}
a, a:visited {{ color: var(--ql-accent) !important; }}
::selection {{ background: {sel_bg}; }}

/* Champs de saisie et sélecteurs */
input, textarea,
[data-baseweb="input"], [data-baseweb="input"] input,
[data-baseweb="select"] > div, [data-baseweb="textarea"] {{
    background-color: var(--ql-field) !important;
    color: var(--ql-fg) !important;
    border-color: var(--ql-border) !important;
}}
[data-baseweb="select"] * {{ color: var(--ql-fg) !important; }}
[data-baseweb="popover"], [role="listbox"], [role="option"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}

/* Onglets */
.stTabs [data-baseweb="tab"] {{ color: var(--ql-fg2) !important; }}
.stTabs [aria-selected="true"] {{ color: var(--ql-accent) !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: var(--ql-accent) !important; }}
.stTabs [data-baseweb="tab-border"] {{
    background: linear-gradient(
        90deg, transparent, var(--ql-accent), transparent
    ) !important;
}}

/* Boutons */
.stButton > button {{
    border: 1px solid var(--ql-border) !important;
    border-radius: 10px !important;
    background-color: var(--ql-field) !important;
    color: var(--ql-fg) !important;
}}
.stButton > button:hover {{
    border-color: var(--ql-accent) !important;
    color: var(--ql-accent) !important;
}}
.stButton > button[kind="primary"] {{
    background-color: var(--ql-accent) !important;
    border-color: var(--ql-accent) !important;
    color: {p['bg']} !important;
}}

/* Encadrés, expanders, alertes : bord gauche orné, aplats et contraste sûr */
[data-testid="stExpander"] {{
    background-color: var(--ql-bg2) !important;
    border: 1px solid var(--ql-border) !important;
    border-left: 3px solid var(--ql-accent) !important;
    border-radius: 10px;
    color: var(--ql-fg) !important;
}}
[data-testid="stExpander"] summary {{ color: var(--ql-fg) !important; }}
[data-testid="stAlert"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 10px;
}}
code, pre, .stCode, [data-testid="stCodeBlock"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}
hr {{ border-color: var(--ql-border) !important; }}
[data-testid="stSidebar"] hr {{
    height: 12px; border: none;
    background: var(--ql-ornament) center/120px 16px no-repeat;
    opacity: .7;
}}

/* Tableaux HTML internes (table.ql) */
table.ql {{
    border-collapse: collapse;
    width: 100%;
    margin: 0.4rem 0 0.8rem 0;
    font-size: 0.92rem;
}}
table.ql th, table.ql td {{
    border: 1px solid var(--ql-border);
    padding: 5px 9px;
    text-align: left;
    color: var(--ql-fg);
    vertical-align: top;
}}
table.ql th {{ background-color: var(--ql-bg2); }}
table.ql tr:nth-child(even) td {{ background-color: {zebra}; }}

/* Tableaux de données natifs (repli, la vue canvas reste limitée) */
[data-testid="stDataFrame"] {{ color: var(--ql-fg) !important; }}

/* --- Bandeau d'en-tête (banner) à l'esprit calligraphique ---------------- */
.ql-banner {{
    position: relative;
    padding: 1.35rem 1.6rem 1.15rem 1.6rem;
    margin: 0 0 1.1rem 0;
    border: 1px solid var(--ql-border);
    border-radius: 16px;
    background-color: var(--ql-bg2);
    overflow: hidden;
}}
.ql-banner::before {{
    /* filet doré supérieur et inférieur, façon encadrement de mosaïque */
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 4px;
    background: linear-gradient(
        90deg, transparent, var(--ql-accent), transparent
    );
    opacity: .8;
}}
.ql-banner .ql-title {{
    margin: 0;
    font-size: 2.15rem;
    font-weight: 700;
    letter-spacing: .04em;
    color: var(--ql-fg);
}}
.ql-banner .ql-subtitle {{
    margin: .35rem 0 0 0;
    color: var(--ql-fg2);
    font-size: .96rem;
    max-width: 62rem;
}}
.ql-banner .ql-rule {{
    height: 16px;
    margin: .7rem 0 .1rem 0;
    background: var(--ql-ornament) left center/120px 16px no-repeat;
    opacity: .65;
}}

/* Petit habillage des titres Streamlit natifs (hors bandeau) */
.stApp h2 {{
    border-bottom: 1px solid var(--ql-border);
    padding-bottom: .25rem;
}}

/* --- Modale st.dialog : couleurs du thème courant (jamais texte sombre sur
   fond sombre ou clair sur clair, quel que soit le mode) ----------------- */
[data-testid*="Dialog"], [class*="stDialog"] {{
    color: var(--ql-fg) !important;
    background-color: var(--ql-bg) !important;
}}
[data-testid*="Dialog"] p, [data-testid*="Dialog"] li, [data-testid*="Dialog"] label,
[data-testid*="Dialog"] span, [data-testid*="Dialog"] h1, [data-testid*="Dialog"] h2,
[data-testid*="Dialog"] h3, [data-testid*="Dialog"] h4, [data-testid*="Dialog"] .stMarkdown,
[data-testid*="Dialog"] code, [data-testid*="Dialog"] caption {{
    color: var(--ql-fg) !important;
}}
[data-testid*="Dialog"] [data-testid="stExpander"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}
[data-testid*="Dialog"] input, [data-testid*="Dialog"] textarea {{
    color: var(--ql-fg) !important;
    background-color: var(--ql-field) !important;
}}
[data-testid*="Dialog"] hr {{ border-color: var(--ql-border) !important; }}
</style>
"""
