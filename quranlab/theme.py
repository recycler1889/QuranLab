"""Gestionnaire de thèmes visuels (Clair / Intermédiaire / Sombre).

Fournit, pour chaque palette, une feuille de style CSS injectée dynamiquement
dans Streamlit via ``st.markdown(..., unsafe_allow_html=True)``.  Les couleurs
sont exposées en variables CSS (``--ql-*``) afin d'habiller uniformément les
composants Streamlit et les tableaux HTML internes (``table.ql``).
"""

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
    },
}

# Ordre d'affichage dans le sélecteur.
ORDER = ["Clair", "Intermediaire", "Sombre"]

DEFAULT = "Clair"


def css(name: str) -> str:
    """Retourne la feuille de style pour la palette demandée."""
    p = PALETTES.get(name, PALETTES[DEFAULT])
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
}}

/* Fonds principaux */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background-color: var(--ql-bg) !important;
}}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
    background-color: var(--ql-bg2) !important;
}}

/* Texte */
.stApp, .stApp p, .stApp span, .stApp li, .stApp label, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp .stMarkdown, [data-testid="stSidebar"] * {{
    color: var(--ql-fg);
}}
.stApp h1, .stApp h2, .stApp h3 {{ color: var(--ql-fg) !important; }}
a, a:visited {{ color: var(--ql-accent) !important; }}

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

/* Encadrés, expanders, alertes */
[data-testid="stExpander"] {{
    background-color: var(--ql-bg2) !important;
    border: 1px solid var(--ql-border) !important;
    border-radius: 8px;
}}
[data-testid="stAlert"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
    border: 1px solid var(--ql-border) !important;
}}
code, pre, .stCode, [data-testid="stCodeBlock"] {{
    background-color: var(--ql-bg2) !important;
    color: var(--ql-fg) !important;
}}
hr {{ border-color: var(--ql-border) !important; }}

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
table.ql tr:nth-child(even) td {{ background-color: color-mix(in srgb, var(--ql-bg2) 45%, transparent); }}

/* Tableaux de données natifs (repli, la vue canvas reste limitée) */
[data-testid="stDataFrame"] {{ color: var(--ql-fg) !important; }}
</style>
"""
