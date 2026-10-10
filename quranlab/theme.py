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
        "label": "Clair",
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
        "label": "Intermédiaire (confort oculaire)",
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
        "label": "Sombre",
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
    """Fleuron géométrique (étoile à huit branches, façon zellige) pour titres."""
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
    glow = _rgba(p["accent"], 0.10)
    return f"""
<style>
:root, html, body, .stApp,
[data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stSidebar"] {{
    /* Palette QuranLab : composants internes (bandeau, tableaux, ornements) */
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

    /* Remappage des variables NATIVES de Streamlit (préfixe `--st-`, cf.
       Streamlit 1.58). Tout composant natif — fenêtres modales (st.dialog),
       menus, expanders, alertes, saisies, titres — tire désormais fond ET
       texte de la MÊME palette : contraste garanti sur les trois modes. C'est
       le mécanisme officiel de personnalisation du thème. */
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
    --st-heading-font: {FONT_STACK} !important;
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
   beaucoup plus léger pour le rendu et le défilement).
   Le fond de la PAGE vient d'un thème JS (pas d'une variable CSS) : on force
   donc explicitement l'aplat de la palette, SINON le fond reste clair alors
   que le texte forcé est clair → illisible en Sombre/Intermédiaire. */
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

/* Accents uniquement, complétés par un recolorage du TEXTE du contenu : la
   coloration du texte Streamlit vient d'un thème JS (pas de variables CSS),
   on force donc explicitement la couleur du contenu, TOUJOURS en cohérence
   avec le fond forcé (clair/sombre), pour un contraste garanti. */
a, a:visited {{ color: var(--ql-accent) !important; }}
::selection {{ background: {sel_bg}; }}

/* Texte du contenu principal (hors dialogues) */
.stApp p, .stApp li, .stApp label, .stApp caption,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp .stMarkdown, .stApp [data-testid="stMarkdownContainer"] {{
    color: var(--ql-fg);
}}

/* Champs de saisie et sélecteurs */
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

/* Tableaux de données natifs : rien à forcer, le texte suit --text-color. */

/* --- Bandeau d'en-tête (banner) à l'esprit calligraphique ---------------- */
.ql-banner {{
    position: relative;
    padding: 1.5rem 1.8rem 1.25rem 1.8rem;
    margin: 0 0 1.1rem 0;
    border: 1px solid var(--ql-border);
    border-radius: 16px;
    background:
        radial-gradient(120% 95% at 50% -25%, {glow}, transparent 62%),
        var(--ql-bg2);
    box-shadow: 0 12px 30px -18px rgba(0,0,0,.35);
    overflow: hidden;
}}
.ql-banner::before {{
    /* double filet supérieur : liseré fin + liseré accent, façon encadrement */
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 3px;
    background: linear-gradient(
        90deg, transparent, var(--ql-accent), transparent
    );
    opacity: .85;
}}
.ql-banner::after {{
    /* filet inférieur discret, en écho au liseré supérieur */
    content: "";
    position: absolute;
    left: 18%; right: 18%; bottom: 0;
    height: 1px;
    background: linear-gradient(
        90deg, transparent, var(--ql-accent), transparent
    );
    opacity: .4;
}}
/* cadre intérieur délicat (respect du geste géométrique) */
.ql-inset {{
    position: absolute;
    inset: 8px;
    border: 1px solid var(--ql-border);
    border-radius: 12px;
    opacity: .55;
    pointer-events: none;
}}
/* fleurons d'angle (équerres fines, façon feuille d'arabesque) */
.ql-corner {{
    position: absolute;
    width: 15px; height: 15px;
    pointer-events: none;
}}
.ql-corner::before, .ql-corner::after {{
    content: "";
    position: absolute;
    background: var(--ql-accent);
    opacity: .7;
}}
.ql-corner::before {{ width: 1.5px; height: 100%; }}
.ql-corner::after  {{ width: 100%; height: 1.5px; }}
.ql-c-tl {{ top: 5px; left: 5px; }}
.ql-c-tr {{ top: 5px; right: 5px; transform: rotate(90deg); }}
.ql-c-br {{ bottom: 5px; right: 5px; transform: rotate(180deg); }}
.ql-c-bl {{ bottom: 5px; left: 5px; transform: rotate(-90deg); }}
/* nappe calligraphique arabe au-dessus du titre */
.ql-banner .ql-ar {{
    margin: 0 0 .12rem 0;
    text-align: center;
    font-family: var(--ql-font-ar);
    font-size: 1.12rem;
    line-height: 1.3;
    letter-spacing: .01em;
    color: var(--ql-accent);
    opacity: .92;
}}
.ql-banner .ql-title {{
    margin: 0;
    text-align: center;
    font-size: 2.05rem;
    font-weight: 700;
    letter-spacing: .14em;
    color: var(--ql-fg);
    line-height: 1.15;
}}
.ql-banner .ql-rule {{
    width: 120px;
    height: 16px;
    margin: .6rem auto .05rem auto;
    background: var(--ql-ornament) center/120px 16px no-repeat;
    opacity: .75;
}}
.ql-banner .ql-subtitle {{
    margin: .4rem auto 0 auto;
    text-align: center;
    color: var(--ql-fg2);
    font-size: .96rem;
    max-width: 54rem;
}}

/* Petit habillage des titres Streamlit natifs (hors bandeau) */
.stApp h2 {{
    border-bottom: 1px solid var(--ql-border);
    padding-bottom: .25rem;
}}

/* --- Modale st.dialog ---
   Streamlit colore la fenêtre (panneau `[data-testid="stDialog"]`) avec le
   thème JS ; on remplace fond ET texte de la palette courante, appariés, pour
   un contraste garanti quel que soit le mode (Clair / Intermédiaire / Sombre).
   `background` (raccourci) l'emporte sur le fond natif du panneau. */
[data-testid="stDialog"] {{
    background: var(--ql-bg) !important;
    color: var(--ql-fg) !important;
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
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}
[data-testid="stDialog"] hr {{ border-color: var(--ql-border) !important; }}
</style>
"""
