"""Gestionnaire de thèmes visuels (Clair / Intermédiaire / Sombre).

Identité visuelle **vert émeraude & or**, inspirée du patrimoine de l'art
islamique (géométrie sacrée, enluminures). Pour chaque palette, une feuille de
style est injectée via ``st.markdown(..., unsafe_allow_html=True)``. Les
couleurs sont exposées en variables CSS (``--ql-*``) afin d'habiller
uniformément les composants Streamlit et les blocs HTML internes (``table.ql``,
``.ql-card``, ``.ql-banner``).

Repères de conception :

* **Clair** : fond ivoire / « vert-de-gris » très clair (jamais blanc pur),
  chaleureux et reposant, cartes à bordures épurées relevées d'un filet doré ;
* **Intermédiaire** : vert sauge feutré sur fond sombre désaturé, pour les
  longues sessions (confort oculaire) ;
* **Sombre** : vert forêt profond, **mat et désaturé**, jamais éblouissant,
  avec un contraste franc sur le texte clair.

Des **motifs géométriques** subtils (étoile à huit branches / zellige) ornent
les bannières et cartes ; ils restent discrets (opacité très basse) pour
préserver la lisibilité et la rigueur de l'étude.
"""

from urllib.parse import quote

# Chaque palette définit un jeu cohérent de variables. Identité commune :
# vert émeraude (accent) + or/champagne (filets, ornements).
PALETTES = {
    "Clair": {
        "label": "Clair",
        "bg": "#F2F1E8",       # ivoire / vert-de-gris très clair (jamais blanc pur)
        "bg2": "#E7E8DB",      # surfaces secondaires (barre latérale, cartes)
        "field": "#FBFBF5",    # champs de saisie (ivoire clair)
        "fg": "#20302A",       # texte vert-anthracite profond
        "fg2": "#5C6B62",      # texte secondaire (sauge grisée)
        "border": "#DED9C4",   # bordure sable/champagne, épurée
        "accent": "#0C5C46",   # émeraude profond
        "gold": "#A98A45",     # or doux / champagne
        "pattern": "#A98A45",  # ornements dorés
        "pattern_opacity": "0.06",
    },
    "Intermediaire": {
        "label": "Intermédiaire (confort oculaire)",
        "bg": "#1C2622",       # vert-ardoise feutré
        "bg2": "#243029",
        "field": "#2A3630",
        "fg": "#EFEDE3",       # ivoire chaud
        "fg2": "#BFC6BA",      # sauge claire
        "border": "#39463F",
        "accent": "#6FA98C",   # émeraude sauge désaturé
        "gold": "#C2A567",     # champagne
        "pattern": "#C2A567",
        "pattern_opacity": "0.07",
    },
    "Sombre": {
        "label": "Sombre",
        "bg": "#101714",       # vert forêt très profond (pas de noir pur)
        "bg2": "#161F1A",
        "field": "#1B2620",
        "fg": "#EAEAE2",       # blanc doux
        "fg2": "#9DAA9F",
        "border": "#28362E",
        "accent": "#5E8F72",   # vert forêt mat, désaturé et feutré
        "gold": "#BFA268",     # or discret
        "pattern": "#BFA268",
        "pattern_opacity": "0.09",
    },
}

# Ordre d'affichage dans le sélecteur.
ORDER = ["Clair", "Intermediaire", "Sombre"]

DEFAULT = "Clair"

# Pile de polices latines du corps de texte (repli système, aucune dépendance).
FONT_STACK = (
    '"Inter", "Segoe UI", "Helvetica Neue", Arial, "Noto Sans", sans-serif'
)
# Pile de polices des titres : serif classique et élégant (repli système).
HEADING_STACK = (
    '"Cormorant Garamond", "Palatino Linotype", "Book Antiqua", Palatino, '
    'Georgia, "Iowan Old Style", "Times New Roman", serif'
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
    ornament = _ornament_svg(p["gold"])
    mosaic = _mosaic_svg(p["gold"], p["pattern_opacity"])
    zebra = _rgba(p["bg2"], 0.5)
    sel_bg = _rgba(p["accent"], 0.28)
    glow = _rgba(p["gold"], 0.10)
    gold_soft = _rgba(p["gold"], 0.16)
    accent_soft = _rgba(p["accent"], 0.12)
    return f"""
<style>
:root, html, body, .stApp,
[data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stSidebar"] {{
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
    --st-heading-font: {HEADING_STACK} !important;
}}

/* Typographie : corps sans-serif lisible ; titres en serif classique. On évite
   tout sélecteur « * » ou « span » global qui écraserait les fontes dédiées
   (code, icônes Material de Streamlit : chevrons, coches, ...). */
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

/* Confort de lecture « prestige » : colonne centrale aérée, jamais pleine
   largeur sur grand écran. */
[data-testid="stMainBlockContainer"], .block-container {{
    max-width: 1180px;
    margin-inline: auto;
    padding-top: 1.3rem;
    padding-bottom: 3rem;
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

/* Onglets : soulignement doré sur l'onglet actif */
.stTabs [data-baseweb="tab"] {{ color: var(--ql-fg2) !important; }}
.stTabs [aria-selected="true"] {{ color: var(--ql-gold) !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: var(--ql-gold) !important; }}
.stTabs [data-baseweb="tab-border"] {{
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    ) !important;
}}

/* Boutons : liseré doré discret, accent émeraude au survol */
.stButton > button {{
    border: 1px solid var(--ql-border) !important;
    border-radius: 12px !important;
    background-color: var(--ql-field) !important;
    color: var(--ql-fg) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, .04);
    transition: border-color .15s ease, color .15s ease, box-shadow .15s ease;
}}
.stButton > button:hover {{
    border-color: var(--ql-gold) !important;
    color: var(--ql-accent) !important;
}}
.stButton > button:focus:not(:active) {{
    border-color: var(--ql-gold) !important;
    box-shadow: 0 0 0 2px var(--ql-gold-soft) !important;
}}
.stButton > button[kind="primary"] {{
    background-color: var(--ql-accent) !important;
    border-color: var(--ql-accent) !important;
    color: {p['bg']} !important;
}}

/* Encadrés, expanders, alertes : bord gauche orné doré, aplats et contraste sûr */
[data-testid="stExpander"] {{
    background-color: var(--ql-bg2) !important;
    border: 1px solid var(--ql-border) !important;
    border-left: 3px solid var(--ql-gold) !important;
    border-radius: 12px;
    color: var(--ql-fg) !important;
}}
[data-testid="stExpander"] summary {{ color: var(--ql-fg) !important; }}
[data-testid="stAlert"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 12px;
}}
code, pre, .stCode, [data-testid="stCodeBlock"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}
hr {{ border-color: var(--ql-border) !important; }}
[data-testid="stSidebar"] hr {{
    height: 12px; border: none;
    background: var(--ql-ornament) center/120px 16px no-repeat;
    opacity: .8;
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
table.ql th {{
    background-color: var(--ql-bg2);
    border-bottom: 1px solid var(--ql-gold);
}}
table.ql tr:nth-child(even) td {{ background-color: {zebra}; }}

/* Tableaux de données natifs : rien à forcer, le texte suit --text-color. */

/* --- Bandeau d'en-tête (banner) : enluminure géométrique ----------------- */
.ql-banner {{
    position: relative;
    padding: 1.6rem 1.9rem 1.35rem 1.9rem;
    margin: 0 0 1.2rem 0;
    border: 1px solid var(--ql-border);
    border-radius: 18px;
    background:
        radial-gradient(120% 95% at 50% -25%, {glow}, transparent 62%),
        var(--ql-mosaic) center/232px 232px,
        var(--ql-bg2);
    box-shadow: 0 16px 40px -24px rgba(0, 0, 0, .5);
    overflow: hidden;
}}
.ql-banner::before {{
    /* liseré supérieur : or, façon encadrement d'enluminure */
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 3px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    opacity: .95;
}}
.ql-banner::after {{
    /* filet inférieur discret, en écho au liseré supérieur */
    content: "";
    position: absolute;
    left: 18%; right: 18%; bottom: 0;
    height: 1px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    opacity: .5;
}}
/* cadre intérieur délicat (respect du geste géométrique) */
.ql-inset {{
    position: absolute;
    inset: 8px;
    border: 1px solid var(--ql-border);
    border-radius: 13px;
    opacity: .6;
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
    background: var(--ql-gold);
    opacity: .8;
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
    font-size: 1.18rem;
    line-height: 1.3;
    letter-spacing: .01em;
    color: var(--ql-gold);
    opacity: .95;
}}
.ql-banner .ql-title {{
    margin: 0;
    text-align: center;
    font-family: var(--ql-heading);
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: .13em;
    color: var(--ql-fg);
    line-height: 1.15;
}}
.ql-banner .ql-rule {{
    width: 120px;
    height: 16px;
    margin: .6rem auto .05rem auto;
    background: var(--ql-ornament) center/120px 16px no-repeat;
    opacity: .85;
}}
.ql-banner .ql-subtitle {{
    margin: .4rem auto 0 auto;
    text-align: center;
    color: var(--ql-fg2);
    font-size: .96rem;
    max-width: 56rem;
}}

/* Petit habillage des titres Streamlit natifs (hors bandeau) : filet doré */
.stApp h2 {{
    border-bottom: 1px solid var(--ql-border);
    padding-bottom: .3rem;
    box-shadow: 0 6px 10px -12px var(--ql-gold);
}}

/* --- Cartes & conteneurs (.ql-card) : composition « prestige » -----------
   Un seul gabarit habille alphabet, voyelles, signes, mots, vocabulaire,
   nombres et 99 Noms : coins délicatement arrondis, bordure fine relevée d'un
   filet doré en tête, ombre douce pour un effet de profondeur feutré.
   Couleurs issues des variables --ql-*, donc contraste garanti. */
.ql-card {{
    position: relative;
    display: flex;
    flex-direction: column;
    gap: .32rem;
    height: 100%;
    padding: 1.05rem .9rem .9rem .9rem;
    border: 1px solid var(--ql-border);
    border-radius: 16px;
    background: var(--ql-bg2);
    color: var(--ql-fg);
    text-align: center;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0, 0, 0, .05),
                0 12px 28px -20px rgba(0, 0, 0, .5);
    transition: transform .16s ease, box-shadow .16s ease,
                border-color .16s ease;
}}
.ql-card::before {{
    /* filet doré en tête de carte, discret */
    content: "";
    position: absolute;
    top: 0; left: 12%; right: 12%;
    height: 2px;
    background: linear-gradient(
        90deg, transparent, var(--ql-gold), transparent
    );
    opacity: .55;
}}
.ql-card:hover {{
    transform: translateY(-2px);
    border-color: var(--ql-gold);
    box-shadow: 0 4px 12px rgba(0, 0, 0, .08),
                0 18px 36px -20px rgba(0, 0, 0, .55);
}}
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
/* En-tête de signe (soukoun / chaddah / tanwin) : carte alignée à gauche */
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

/* --- Versets (onglet « Lire ») : référence ornée, verset ciblé ----------- */
.ql-verse-anchor {{ display: block; height: 0; }}
.ql-verse-ref {{
    display: flex;
    align-items: center;
    gap: .55rem;
    margin: .15rem 0;
}}
.ql-verse-ref::before {{
    content: "";
    width: 1.7rem;
    height: 1px;
    background: var(--ql-gold);
    opacity: .85;
    flex: none;
}}
.ql-verse-ref .ql-ref-num {{
    font-family: var(--ql-heading);
    font-weight: 600;
    font-size: 1.02rem;
    color: var(--ql-accent);
    letter-spacing: .02em;
}}
.ql-verse-ar {{
    font-family: var(--ql-font-ar);
    line-height: 2.3;
    margin: .2rem 0 .5rem 0;
}}
.ql-target {{
    border-left: 3px solid var(--ql-gold);
    background: var(--ql-gold-soft);
    border-radius: 10px;
    padding: .35rem .75rem;
}}

/* --- Modale st.dialog ---
   Streamlit colore la fenêtre (panneau `[data-testid="stDialog"]`) avec le
   thème JS ; on remplace fond ET texte de la palette courante, appariés, pour
   un contraste garanti quel que soit le mode (Clair / Intermédiaire / Sombre). */
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

/* --- Confort mobile : l'app installée (PWA) reste lisible et tactile ---- */
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
    .stTabs [data-baseweb="tab"] {{
        padding-left: .5rem;
        padding-right: .5rem;
        font-size: .9rem;
    }}
    /* 16 px minimum : évite le zoom automatique des champs sur iOS */
    input, textarea, select {{ font-size: 16px !important; }}
}}
@media (max-width: 420px) {{
    .ql-card {{ padding: .7rem .45rem; gap: .22rem; }}
    .ql-card .ql-gloss {{ font-size: .82rem; }}
    .ql-card .ql-ar {{ font-size: 1.6rem; }}
}}
</style>
"""
