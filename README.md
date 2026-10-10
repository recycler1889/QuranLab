# quranlab

Outil **local** de recherche et d'analyse **strictement intra-coranique**.
Le point de départ est toujours le **texte arabe** (racine, morphologie),
avec un affichage comparatif de traductions (françaises et anglaises).

Aucun tafsir, aucun hadith, aucune interprétation traditionnelle
post-coranique : le Coran est éclairé par le Coran.

Français · [**English**](README.en.md)

---

## 1. Structure du projet

```
quran-lab/
├─ app.py                     # Interface web locale (Streamlit)
├─ requirements.txt           # Streamlit (le reste = bibliothèque standard)
├─ README.md
├─ README.en.md               # documentation en anglais
├─ data/                      # créé par `init`
│  ├─ raw/                    # sources brutes téléchargées (JSON + morphologie)
│  └─ quran.db                # base SQLite générée
├─ quranlab/                  # le cœur (sans dépendance externe)
│  ├─ config.py               # chemins + sources de données
│  ├─ buckwalter.py           # Buckwalter <-> arabe, translittération, normalisation
│  ├─ download.py             # téléchargement des sources
│  ├─ build.py                # schéma + construction de la base SQLite
│  ├─ db.py                   # connexion SQLite
│  ├─ search.py               # moteur : texte, racines, versets, thèmes
│  ├─ ui.py                   # vues partagées : versets, tableaux, recherche universelle
│  ├─ themes.json             # cartographies thématiques (salât, wudû', ...)
│  ├─ lexicon_fr.json         # lexique FR → racines (passerelle, 86 entrées)
│  ├─ cli.py                  # interface ligne de commande
│  └─ __main__.py
└─ tests/
   ├─ test_buckwalter.py       # conversions Buckwalter ↔ arabe, normalisation
   ├─ test_theme.py            # générateurs SVG / feuille de style
   └─ test_search_helpers.py   # aides de recherche pures (sans base)
```

## 2. Démarrage

```powershell
# 1. (optionnel) environnement virtuel
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 2. dépendance de l'interface web (le cœur n'en a aucune)
pip install -r requirements.txt

# 3. téléchargement des sources + construction de la base SQLite
python -m quranlab init

# 4. interface web locale
streamlit run app.py
```

## 3. Ligne de commande

```powershell
python -m quranlab root رحم              # occurrences d'une racine (arabe)
python -m quranlab root rHm --context 1  # idem en Buckwalter, avec contexte
python -m quranlab search "الرحمن" --lang ar
python -m quranlab search "miséricorde" --lang fr --translation fr.hamidullah
python -m quranlab bridge "patience"       # français → racine arabe
python -m quranlab verse 5:6             # verset + traductions + mot-à-mot
python -m quranlab theme salat           # cartographie thématique
python -m quranlab themes                # liste des thèmes prédéfinis
```

## 4. Schéma de la base SQLite

| Table | Rôle |
|---|---|
| `surahs` | 114 sourates : nom translittéré, arabe, anglais, révélation, nb de versets |
| `verses` | texte **uthmani**, texte simple et texte normalisé (sans diacritiques) |
| `translations` | catalogue des traductions (clé, auteur, langue) |
| `translation_verses` | traduction verset par verset + version normalisée |
| `words` | **un mot par ligne** : forme arabe, translittération, **racine**, lemme, POS |
| `segments` | découpage morphologique fin (préfixe / radical / suffixe) |

`words.root_buckwalter` / `root_arabic` / `root_norm` portent l'indexation par
racine ; `segments.features` conserve l'annotation complète du corpus.

## 5. Sources de données (publiques, vérifiables)

- **Texte arabe uthmani** : `ara-quranuthmanihaf` (Complexe du Roi Fahd),
  via la *Quran API* (miroir jsDelivr) — cf. `config.py`.
- **Texte simple (imla'i)** : `ara-quransimple`, base d'alignement des mots.
- **Traductions françaises** : Muhammad Hamidullah, Rashid Maash,
  Islamic Foundation (Montada).
- **Traductions anglaises** : Saheeh International (Umm Muhammad),
  Marmaduke Pickthall.
- **Morphologie & racines** : *Quranic Arabic Corpus* v0.4 (Kais Dukes, GPL),
  annoté sur le texte vérifié de Tanzil.

> Remarque : Blachère et Masson sont sous droits d'auteur et ne sont pas
> distribuables librement. Les traductions retenues sont littérales et sans
> appareil dogmatique. On peut ajouter une traduction locale (fichier
> `{chapter, verse, text}`) en l'enregistrant dans `config.TRANSLATIONS` ; sa
> `language` (`fr` / `en`) pilote aussi la voix de la synthèse vocale.

## 6. Cartographie thématique (`quranlab/themes.json`)

Le fichier contient **164 thèmes** répartis en **10 catégories**, chacun ancré sur
une ou plusieurs **racines arabes**. La clé `_meta` liste l'ordre des catégories.

```json
"misericorde": {
  "category": "Éthique et Comportement",
  "label": "La miséricorde (ar-raḥma)",
  "description": "Racine ر-ح-م : compassion, clémence.",
  "roots": ["رحم"],
  "terms_ar": ["الرحمن", "الرحيم"],
  "terms_fr": ["misericorde"]
}
```

- `roots` : **référence principale** — racines écrites en arabe (ou Buckwalter),
  résolues automatiquement contre la base (`words.root_norm`).
- `terms_ar` / `terms_fr` : formes ou traductions hors racine (facultatif).
- `category` : un des axes listés dans `_meta.categories`.

**Ajouter un thème** : copier un bloc, changer la clé et les racines. Il apparaît
automatiquement dans la CLI (`python -m quranlab themes`) et dans le menu
déroulant Streamlit (onglet *Thèmes*), regroupé par catégorie. Pour vérifier
qu'une racine existe, la commande `python -m quranlab root <racine>` ou
l'onglet *Racine* sert de contrôle.

**Résolution tolérante du nom** : la CLI (`theme <nom>`) accepte la clé exacte
(`priere`) **ou** une variante usuelle. La saisie est recherchée (au-delà de
4 caractères) dans la clé, le libellé et les termes fr/ar, et n'est retenue que
si elle désigne un seul thème. Ainsi `python -m quranlab theme salat` retrouve
`priere` (libellé « aṣ-ṣalāt »), `zakat` retrouve `aumone`, `hajj` retrouve
`pelerinage`. En cas d'ambiguïté ou d'absence, la liste des thèmes disponibles
est affichée (`search.resolve_theme_key()`).

**Onglet *Thèmes* (app)** : les 164 thèmes sont tous accessibles — recherche
plein texte (libellé, description, clé, racine arabe **ou** Buckwalter, termes
ar/fr), filtre par catégorie (« Toutes » par défaut), **compteur de versets par
thème** (calculé une seule fois puis mis en cache, invalidé si `themes.json`
change) et tableau de vue d'ensemble de tous les thèmes filtrés. La sidebar
affiche les chiffres du corpus (sourates, versets, mots, racines, thèmes,
sujets).

## 7. Recherche multilingue et passerelle français → arabe (onglet *Recherche*)

L'onglet *Recherche* propose deux modes (radio **Français** par défaut) :

- **Français** : une **passerelle linguistique** (`search.french_bridge()`)
  fusionne trois sources de correspondances, dédupliquées par racine :
  1. **lexique** — `quranlab/lexicon_fr.json` (86 entrées courantes : mot FR →
     racines trilitères vérifiées dans la base) ;
  2. **thèmes** — termes FR des 164 thèmes (`terms_fr`) ;
  3. **corpus** — racines déduites distributionnellement (lift : fréquentes dans
     les versets français touchés, rares ailleurs).

  Un tableau affiche les propositions (racine arabe, Buckwalter, nb de versets,
  occurrences, source) ; une liste déroulante interroge ensuite le **texte
  original** par racine choisie (slider de limite d'affichage). La saisie
  directe d'une racine (arabe ou Buckwalter, ex. `rHm`) est résolue
  immédiatement. Les résultats français sont **dédupliqués : un seul affichage
  par verset**, avec la liste des traductions contenant le terme.
- **Arabe** : recherche directe dans le texte original.

`search.search_french()` groupe par verset (`GROUP BY sura, aya`) ; le détail
par traduction reste disponible via `search.french_matches_rows()` (utilisé par
la CLI). Le rendu des racines est partagé entre l'onglet *Racine* et la
passerelle (`render_root_results`) : **un seul expander par verset**, toutes
les formes de la racine y sont listées.

### 7.1 Barre de recherche universelle bilingue (dans chaque onglet)

Chaque onglet (*Racine*, *Recherche*, *Verset comparé*, *Thèmes*, *Idées reçues*,
*Concordance*) ouvre sur une **barre de recherche universelle**
(`quranlab/ui.py`, `ui.universal_search()`) qui accepte **indifféremment le
français ou l'arabe**. La langue est détectée automatiquement
(`ui.occurrence_summary()`, via `buckwalter.is_arabic`) :

- **Saisie française** (n'importe quel mot) → **passerelle** vers les racines
  `search.french_bridge()` (lexique → thèmes → déduction par le corpus) ;
- **Saisie arabe** → si le mot est une **racine** (`صبر`, `رحم`), recherche par
  racine ; sinon **recherche textuelle** (`search.arabic_occurrence_summary()`)
  avec comptage exact des occurrences dans `verses.text_simple_norm`.

Dans tous les cas, l'interface affiche **systématiquement le nombre total
d'occurrences** : **« N occurrence(s) trouvée(s) dans Y verset(s) »**
(`ui.counter_label()`). Pour les requêtes françaises, le compteur est calculé en
**union** des racines (`search.roots_union_stats()`) : un verset contenant
plusieurs racines ciblées n'est compté qu'une fois. Les versets sont ensuite
affichés contextualisés (sélecteur de racine + limite d'affichage, ou liste
textuelle pour l'arabe), avec un repli dépliable reprenant les occurrences
françaises dans les traductions.

Les composants de vue (`html_table`, `render_verse`, `render_verses`,
`render_root_results`, `universal_search`, `verse_picker`) sont **mutualisés dans
`quranlab/ui.py`** ; `app.py` ne fait plus qu'orchestrer les onglets. Aucun
thème visuel supplémentaire n'est requis : les résultats héritent de la charte
courante (Clair / Intermédiaire bleu-gris / Sombre).

### 7.2 Onglet « Verset comparé » — deux modes

Réarchitecturé (`app.py`, onglet *Verset comparé*) autour d'un sélecteur
réutilisable `ui.verse_picker()` (liste des sourates + numéro de verset) :

- **Mode « Comparer deux versets »** : deux sélecteurs **indépendants** A et B,
  affichés **côte à côte** (texte arabe uthmani + traductions plurielles). Une
  synthèse compare leur **structure thématique** : racines de chaque verset,
  racines **communes** et leur nombre (`search.verse_root_set()`).
- **Mode « Suggérer des versets similaires »** : à partir d'une **référence**
  `sura:aya` → versets en **miroir** par racines partagées
  (`search.mirror_verses()`) ; à partir d'un **mot-clé** (français ou arabe) →
  passerelle vers les racines puis proximité lexicale
  (`search.similar_verses_by_roots()`, racines dérivées par
  `search.top_roots_in_verses()` pour un mot arabe). Seuils réglables (racines
  communes minimales, nombre de suggestions).

## 8. Idées reçues, controverses et pratiques (`quranlab/controversies.json`)

Section **strictement descriptive et intra-coranique** (onglet *Idées reçues*).
Chaque sujet contient : `question`, `framing` (note méthodologique, sans
conclusion doctrinale), `roots`, `terms_ar`, `key_verses`, `context_hint`, et
optionnellement `root_polysemy` (racines dont on affiche **toutes les formes**).

L'app calcule : la **récurrence lexicale**, la **polysémie** (toutes les formes
d'une racine et leurs contextes), puis affiche les versets clés en arabe avec
toutes les traductions. Aucun tafsir, hadith ou avis traditionnel.

12 sujets : statut de la femme/genre, correction conjugale (racine ḍ-r-b),
contrainte et liberté, servitude et affranchissement (*fakk raqaba*), mariage et
maturité (*rushd*), modalités de la prière (postures + récitation), guerre et
paix, peines, vêtement et pudeur (*khumur* / *jalābīb*), liberté de croyance,
gens du Livre, alcool et jeu.

## 9. Concordance interne / versets en miroir (onglet *Concordance*)

Croisement purement lexical de versets — « le Coran s'explique par le Coran » :

- **Verset en miroir** : à partir d'un verset (`sura:aya`), `search.mirror_verses()`
  calcule l'ensemble de ses racines, puis classe les autres versets par nombre de
  **racines communes** (et ratio de recouvrement). Chaque miroir est affiché avec
  son texte et ses traductions.
- **Concordance par notion** : `search.concordance()` regroupe toutes les
  occurrences d'une **racine** ou d'un **terme** avec traductions plurielles.

Fonctions : `search.verse_root_set()`, `search.mirror_verses()`,
`search.concordance()`, `search.root_polysemy()`.

## 10. Principes méthodologiques

- Recherche par **racine** (trilitère/quadrilitère) comme axe primaire.
- Normalisation arabe (diacritiques, alif, alif maqsûra) pour des recherches
  robustes sans perdre la forme d'origine à l'affichage.
- Affichage systématique du **contexte** (versets avant/après) pour laisser
  le texte se commenter lui-même.
- Agrégation **thématique** par croisement de racines et de termes.

## 11. Déploiement (Streamlit Community Cloud)

1. Pousser le projet sur un dépôt GitHub **public**.
2. Sur https://share.streamlit.io → *New app* → choisir le dépôt, branche `main`,
   et **Main file path = `app.py`**.
3. Déployer. Aucun secret n'est nécessaire.

**Base de données en ligne** : `data/quran.db` est ignoré par git. Au premier
lancement, `app.py` appelle `build.ensure_db()` qui **télécharge les sources et
construit la base automatiquement** (≈30 s, une seule fois par conteneur, mis en
cache par `@st.cache_resource`). Les chemins sont strictement relatifs
(`config.py` se base sur `__file__`), donc rien de spécifique à Windows.

> Pour un démarrage instantané, on peut versionner la base : commenter la ligne
> `data/quran.db` dans `.gitignore`, puis committer `data/quran.db` (~29 Mo).

Fichiers utiles au déploiement : `requirements.txt` (streamlit + pandas),
`.streamlit/config.toml` (thème), `.gitignore`.

## 12. Thème visuel (Clair / Intermédiaire / Sombre)

Un sélecteur est présent dans la **barre latérale** (`quranlab/theme.py`).
Trois palettes, appliquées dynamiquement par injection CSS (variables `--ql-*`) :

| Mode | Fond | Texte | Usage |
|---|---|---|---|
| **Clair** | `#F7F5F0` (blanc cassé) | `#23272B` | lecture de jour |
| **Intermédiaire** | `#1E293B` (ardoise) | `#F1F5F9` | confort oculaire |
| **Sombre** | `#16181D` (gris-noir) | `#E6E8EB` | faible luminosité |

La CSS habille les fonds, le texte, la sidebar, les onglets, les champs, les
expanders et les tableaux HTML internes (`table.ql`). Les tableaux sont générés
en HTML (`html_table()`) plutôt qu'avec `st.dataframe`, dont la vue *canvas* ne
suit pas les thèmes.
