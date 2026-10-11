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
│  ├─ search.py               # moteur : texte, racines, versets, thèmes, référence
│  ├─ ui.py                   # vues partagées : versets, tableaux, recherche universelle
│  ├─ theme.py                # palettes Clair / Intermédiaire / Sombre
│  ├─ i18n.py                 # traductions FR/EN (parité des clés)
│  ├─ cache.py                # wrappers st.cache_data (racines, mots, sourates)
│  ├─ onboarding.py           # guide de démarrage (modale latérale)
│  ├─ bookmarks.py            # favoris (data/bookmarks.json)
│  ├─ learn_ui.py             # onglet « Apprendre » (tableau de bord SRS)
│  ├─ learning.py             # persistance des cartes et objectifs
│  ├─ srs.py                  # répétition espacée (SM-2 simplifié)
│  ├─ quiz.py                 # quiz de contexte / reconnaissance de racine
│  ├─ vocab.py                # fiche mot (forme, racine, glose, fréquence)
│  ├─ iqra.py                 # données du parcours de lecture (lettres, voyelles, signes, nombres)
│  ├─ iqra_ui.py              # onglet « Lire le Coran Iqra » (7 étapes)
│  ├─ asma.py                 # 99 Noms d'Allah (données étymologiques + filtre)
│  ├─ pwa.py                  # application installable (manifeste, icônes, métadonnées)
│  ├─ tts.py                  # synthèse vocale (Piper + repli navigateur)
│  ├─ themes.json             # cartographies thématiques (salât, wudû', ...)
│  ├─ lexicon_fr.json         # lexique FR → racines (passerelle, 86 entrées)
│  ├─ controversies.json      # idées reçues / controverses (12 sujets)
│  ├─ cli.py                  # interface ligne de commande
│  └─ __main__.py
├─ static/                    # ressources servies (manifeste PWA + icônes PNG)
│  ├─ manifest.webmanifest
│  └─ icons/                  # 192 / 512 / maskable / apple-touch-icon
└─ tests/                     # 18 fichiers unittest : buckwalter, search, i18n,
                              # thème, TTS, iqra, asma, onboarding, SRS, favoris, PWA…
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
> `language` (`fr` / `en`) pilote aussi la voix de la synthèse vocale (Piper :
> **6 voix françaises** et 4 anglaises au choix — hommes, femmes, neutres —
> plus la vitesse dans les paramètres TTS ; repli sur les voix du navigateur si
> Piper n'est pas installé).

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

La barre accepte aussi une **référence directe de verset** : `2:255`, `2.255`,
`2/255` ou `2 255` — les séparateurs **deux-points, point, barre oblique et
espace** sont équivalents — affichent immédiatement le verset correspondant
(texte arabe, translittération phonétique et traductions de la langue active)
sans passer par la recherche textuelle (`search.parse_ref()`, regex
`^\s*(\d{1,3})\s*[:./\s]\s*(\d{1,3})\s*$`). Une saisie qui n'est pas une
référence valide (hors bornes, verset inexistant… ou simple texte) retombe
automatiquement sur la recherche classique.

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

## 13. Apprentissage — répétition espacée (onglet *Apprendre*)

Mémorisation du **vocabulaire coranique** par répétition espacée (type Anki),
sans dépendance externe. La progression est stockée localement dans
`data/learning.json` (ignoré par git, comme les favoris).

- **Tableau de bord** : cartes à réviser, révisions et nouveautés du jour, série
  de jours, racines maîtrisées et **couverture du lexique fréquent** (part des
  `LEARN_TOP_ROOTS` racines les plus courantes déjà maîtrisées).
- **Révision espacée** (`quranlab/srs.py`) : algorithme SM-2 simplifié
  (`again` / `hard` / `good` / `easy`), états `new` → `learning` → `review`.
  `quranlab/learning.py` persiste les cartes, les objectifs et le journal.
- **Quiz de contexte** (`quranlab/quiz.py`) : le mot cible est surligné dans son
  verset ; il faut choisir la bonne glose parmi des leurres. Un second exercice
  fait **reconnaître la racine** d'une forme. Répondre met à jour le SRS.
- **Fiche mot / mots cliquables** : en activant *Mots cliquables* dans la barre
  latérale, chaque mot d'un verset devient cliquable ; la fiche affiche forme,
  racine, lemme, catégorie grammaticale, **fréquence** coranique et glose
  (`quranlab/vocab.py`).
- **Objectifs quotidiens paramétrables** (nouveaux mots, révisions) et rappels.

Désactivable via `config.LEARN_ENABLED = False`.

## 14. Favoris (onglet *Favoris*)

Tous les versets mis de côté sont **centralisés** dans l'onglet *Favoris*
(`quranlab/bookmarks.py`, stockage local `data/bookmarks.json`, ignoré par git) :

- **Ajout / retrait d'un clic** : sous chaque verset affiché, le bouton *favori*
  bascule l'appartenance à la liste (`bookmarks.toggle()`).
- **Ajout par référence** : saisie directe d'une référence — mêmes séparateurs
  tolérants que la recherche (`2:255`, `2.255`, `2/255`, `2 255`).
- **Annotations** : chaque favori peut recevoir une **note** personnelle.
- **Export** : la liste (références, texte uthmani et traductions de la langue
  active) se télécharge en un fichier texte ; bouton de **réinitialisation**.

Aucune donnée ne quitte la machine : chaque déploiement garde ses propres favoris.

## 15. Lire l'arabe — méthode Iqraʾ (onglet *Lire le Coran Iqra*)

Parcours guidé en **7 étapes** navigables (radio) pour apprendre à lire l'arabe du
Coran (`quranlab/iqra.py` pour les données, `quranlab/iqra_ui.py` pour la vue).
Chaque élément porte un bouton **Écouter** (synthèse vocale arabe `ar-SA` via
l'API du navigateur, `ui.tts_arabic`).

1. **Alphabet** — les 28 lettres, formes isolée / initiale / médiale / finale et
   règle des six lettres non connectantes ; un bouton bascule **Mélanger les
   lettres** réordonne les cartes aléatoirement (l'ordre est conservé dans
   l'état de session, donc stable pendant l'écoute TTS), avec retour à
   l'**ordre traditionnel** en un clic.
2. **Voyelles** — courtes (*ḥarakāt*) et longues (*moudoud*), avec un
   entraînement (choix de la transcription).
3. **Signes** — soukoun, chaddah, tanwīn, illustrés par des mots-exemples.
4. **Lecture** — mots, expressions consacrées puis courtes sourates, avec
   transcription phonétique et récitation audio.
5. **Vocabulaire essentiel** — les `config.IQRA_VOCAB_TOP` (500) racines les plus
   fréquentes, en cartes (mot représentatif, prononciation, sens, référence),
   filtre plein texte et limite d'affichage.
6. **Nombres** — de 1 à 1000 : chiffre arabo-indien, écriture en toutes lettres
   et prononciation (unités, dizaines, centaines).
7. **Les 99 Noms d'Allah** — voir ci-dessous.

### 15.1 Les 99 Noms d'Allah (`quranlab/asma.py`)

Les 99 Noms (*Asmāʾ Allāh al-Ḥusnā*) sont présentés en **cartes**, dans une
approche **strictement étymologique / lexicographique** (sans exégèse) :

- calligraphie arabe (RTL), **translittération** et **traduction directe** ;
- **racine** et **sens lexicographique** de cette racine ;
- repère graphique et teinte dérivés du rang ; **filtre** plein texte (arabe,
  translittération, français, anglais et racine — espaces internes des racines
  ignorés, ex. `رحم` retrouve `ر ح م`) ;
- bouton **Écouter** par Nom (prononciation arabe).

Données exposées par `asma.NAMES` et les helpers `asma.count()`,
`asma.translation()`, `asma.etymology()` et `asma.search()`.

## 16. Guide de démarrage (modale latérale)

`quranlab/onboarding.py` fournit un **guide de démarrage** bilingue, ouvert par un
**bouton de la barre latérale** — il ne s'ouvre **jamais automatiquement** (état
`ql_guide_open`, fermé par défaut sur une session neuve). Le guide décrit le rôle
de chaque onglet, la **recherche par référence** multi-séparateurs, les
**favoris**, le parcours **Iqra** (alphabet → 99 Noms) et les **99 Noms**, puis
propose des suggestions de parcours (`SUGGESTIONS`).

## 17. Application installable (PWA) et confort mobile

QuranLab est une **application web installable** : sur mobile ou bureau, le
navigateur propose « Installer » / « Ajouter à l'écran d'accueil » et l'app
s'ouvre alors **en plein écran**, sans barre d'adresse.

- `quranlab/pwa.py` génère, si absents, le **manifeste** et les **icônes PNG**
  (192, 512, variante *maskable* et `apple-touch-icon`), puis injecte dans
  l'en-tête du document le lien `<link rel="manifest">`, la couleur `theme-color`
  (assortie au thème courant) et les métadonnées `apple-mobile-web-app-*`.
- Les fichiers sont servis par Streamlit depuis le dossier `static/`, ce qui
  suppose `server.enableStaticServing = true` (déjà posé dans
  `.streamlit/config.toml`) ; ils sont exposés sous `/app/static/…`.
- Les icônes sont **versionnées** dans le dépôt ; Pillow n'est requis que pour
  les régénérer (`python -m quranlab.pwa`).

Le **design** a été homogénéisé : un gabarit CSS unique `.ql-card` (bordures
douces, ombre portée discrète, espacements généreux, hiérarchie typographique)
habille toutes les cartes pédagogiques du parcours Iqra, et des
*media queries* (`max-width: 780px` / `420px`) adaptent bandeau, cartes, onglets
et zones tactiles aux petits écrans.

