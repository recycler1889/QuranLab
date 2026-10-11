"""Les 99 Noms d'Allah (Asmāʾ Allāh al-Ḥusnā) — approche linguistique.

Pour chaque Nom, on ne retient que la **donnée lexicale** : le Nom en écriture
arabe, sa translittération, sa traduction directe, la **racine** dont il dérive
et le **sens étymologique de cette racine** (esprit des dictionnaires de la
langue arabe : *Lisān al-ʿArab*, *Maqāyīs al-Lugha*). Aucune théologie, aucune
exégèse post-coranique : c'est un matériel lexicographique, cohérent avec la
ligne « strictement intra-coranique » de QuranLab.

Chaque entrée expose : ``n`` (rang), ``ar``, ``tr`` (translittération),
``fr``/``en`` (traduction directe), ``root_ar``/``root_tr`` (racine),
``etym_fr``/``etym_en`` (définition de la racine), ``icon`` (repère graphique
doux) et ``hue`` (teinte de code couleur, dérivée du rang).
"""

from __future__ import annotations

import unicodedata

# (ar, tr, root_ar, root_tr, fr, en, etym_fr, etym_en, icon)
_RAW = [
    ("الرَّحْمَٰن", "Ar-Raḥmān", "ر ح م", "r-ḥ-m", "Le Tout-Miséricordieux",
     "The Most Merciful",
     "De رَحِمَ, « avoir la tendresse, être pris de compassion » ; la même "
     "racine donne رَحِم (la matrice) et رَحْمَة (la miséricorde). Le schéma "
     "فَعْلَان marque la plénitude de l'attribut : celui dont la miséricorde "
     "embrasse tout.",
     "From رَحِمَ, 'to feel tenderness, to be moved to compassion'; the same "
     "root yields رَحِم (the womb) and رَحْمَة (mercy). The pattern فَعْلَان "
     "marks fullness of the attribute: the one whose mercy embraces all.",
     "💗"),
    ("الرَّحِيم", "Ar-Raḥīm", "ر ح م", "r-ḥ-m", "Le Très-Miséricordieux",
     "The Most Compassionate",
     "Même racine ر ح م que الرَّحْمَٰن ; le schéma فَعِيل exprime l'attribut "
     "durable et répété : la miséricorde qui se renouvelle sans cesse.",
     "Same root ر ح م as الرَّحْمَٰن; the pattern فَعِيل expresses a lasting, "
     "recurring attribute: mercy forever renewed.",
     "🤲"),
    ("الْمَلِك", "Al-Malik", "م ل ك", "m-l-k", "Le Roi", "The King",
     "De مَلَكَ, « posséder, disposer souverainement » ; مِلْك et مُلْك "
     "désignent la possession et la royauté. Sens lexical : celui qui détient "
     "l'autorité et la propriété de toute chose.",
     "From مَلَكَ, 'to possess, to have sovereign disposal of'; مِلْك and "
     "مُلْك denote ownership and dominion. Lexical sense: the holder of "
     "authority and ownership over all things.",
     "👑"),
    ("الْقُدُّوس", "Al-Quddūs", "ق د س", "q-d-s", "Le Très-Saint",
     "The Most Holy",
     "De قَدُسَ/قَدَّسَ, « être pur, purifier, sanctifier » ; قُدْس désigne la "
     "pureté et la sainteté. Le schéma فَعُّول intensif : la pureté portée à "
     "son comble, l'absolue exemption de tout défaut.",
     "From قَدُسَ/قَدَّسَ, 'to be pure, to purify, to hallow'; قُدْس means "
     "purity and holiness. The intensive pattern فَعُّول: purity at its "
     "fullest, absolute freedom from any flaw.",
     "✨"),
    ("السَّلَام", "As-Salām", "س ل م", "s-l-m", "La Paix",
     "The Source of Peace",
     "De سَلِمَ, « être sain, indemne, à l'abri » ; سَلَام désigne la santé, "
     "l'intégrité et la paix, أَسْلَمَ le fait de s'en remettre. Sens "
     "lexical : celui dont émane l'absence de tout dommage.",
     "From سَلِمَ, 'to be sound, unharmed, safe'; سَلَام means soundness, "
     "integrity and peace, أَسْلَمَ to surrender safely. Lexical sense: the "
     "one from whom freedom from all harm proceeds.",
     "🕊️"),
    ("الْمُؤْمِن", "Al-Mu'min", "أ م ن", "ʾ-m-n", "Le Garant de la sécurité",
     "The Guarantor of Faith",
     "De أَمِنَ/آمَنَ, « être en sécurité, se fier, croire » ; أَمْن et "
     "أَمَان sont la sécurité et la sauvegarde. Le schéma مُفْعِل (causatif) : "
     "celui qui procure la sécurité et la confiance.",
     "From أَمِنَ/آمَنَ, 'to be safe, to trust, to believe'; أَمْن and أَمَان "
     "are security and safeguard. The causative pattern مُفْعِل: the one who "
     "grants safety and trust.",
     "🛡️"),
    ("الْمُهَيْمِن", "Al-Muhaymin", "ه م ن", "h-m-n", "Le Surveillant",
     "The Guardian",
     "De هَيْمَنَ, « veiller sur, surveiller, contrôler » — verbe d'origine "
     "étrangère intégré à l'arabe. Sens lexical : celui qui observe et "
     "protège toute chose.",
     "From هَيْمَنَ, 'to watch over, to supervise, to control' — a verb of "
     "foreign origin naturalised into Arabic. Lexical sense: the one who "
     "observes and protects all things.",
     "👁️"),
    ("الْعَزِيز", "Al-'Azīz", "ع ز ز", "ʿ-z-z", "Le Tout-Puissant",
     "The Almighty",
     "De عَزَّ, « être fort, puissant, rare » ; عِزّ est la puissance et "
     "l'honneur, عَزِيز ce qui est à la fois puissant et précieux car "
     "difficile d'accès. Sens lexical : force invincible.",
     "From عَزَّ, 'to be strong, mighty, rare'; عِزّ is might and honour, "
     "عَزِيز both mighty and precious for being hard to reach. Lexical sense: "
     "invincible strength.",
     "💪"),
    ("الْجَبَّار", "Al-Jabbār", "ج ب ر", "j-b-r", "Le Contraignant",
     "The Compeller",
     "De جَبَرَ, « remettre droit, réparer (un os brisé), contraindre » ; "
     "جَبْر est la réparation et la contrainte. Le schéma فَعَّال : celui qui "
     "redresse ce qui est brisé et soumet par sa volonté.",
     "From جَبَرَ, 'to set right, to mend (a broken bone), to compel'; جَبْر "
     "is mending and coercion. The pattern فَعَّال: the one who restores what "
     "is broken and subdues by His will.",
     "⚡"),
    ("الْمُتَكَبِّر", "Al-Mutakabbir", "ك ب ر", "k-b-r", "Le Suprême",
     "The Supreme",
     "De كَبُرَ, « être grand, avoir de la grandeur » ; كِبْر est la grandeur "
     "et la majesté. Le schéma مُتَفَعِّل : celui qui détient en propre la "
     "grandeur, sans rien emprunter à personne.",
     "From كَبُرَ, 'to be great, to have greatness'; كِبْر is greatness and "
     "majesty. The pattern مُتَفَعِّل: the one who inherently owns greatness, "
     "borrowing it from no one.",
     "⛰️"),
    ("الْخَالِق", "Al-Khāliq", "خ ل ق", "kh-l-q", "Le Créateur", "The Creator",
     "De خَلَقَ, « créer, façonner, mesurer, proportionner » ; خَلْق désigne "
     "à la fois la création et la conformation native. Sens lexical : celui "
     "qui mesure et fait être à partir de rien.",
     "From خَلَقَ, 'to create, to shape, to measure out, to proportion'; "
     "خَلْق denotes both creation and innate conformation. Lexical sense: the "
     "one who measures and brings into being from nothing.",
     "🌍"),
    ("الْبَارِئ", "Al-Bāri'", "ب ر أ", "b-r-ʾ", "L'Inventeur", "The Originator",
     "De بَرَأَ, « faire surgir, produire sans modèle » ; بَرِيء (libre, "
     "dégagé) montre l'idée de donner l'être en se dégageant de tout modèle. "
     "Sens lexical : celui qui fait émerger les êtres.",
     "From بَرَأَ, 'to bring forth, to produce without a model'; بَرِيء "
     "(free, disengaged) shows the idea of giving being without any "
     "template. Lexical sense: the one who brings beings forth.",
     "🧱"),
    ("الْمُصَوِّر", "Al-Musawwir", "ص و ر", "ṣ-w-r", "Le Modeleur",
     "The Fashioner",
     "De صَوَّرَ, « former, façonner, donner une figure » ; صُورَة est la "
     "forme et l'image. Le schéma مُفَعِّل : celui qui donne à chaque être sa "
     "configuration propre.",
     "From صَوَّرَ, 'to form, to fashion, to give a figure'; صُورَة is the "
     "form and image. The pattern مُفَعِّل: the one who gives each being its "
     "own configuration.",
     "🖌️"),
    ("الْغَفَّار", "Al-Ghaffār", "غ ف ر", "gh-f-r", "Le Très-Pardonnant",
     "The All-Forgiving",
     "De غَفَرَ, « couvrir, voiler » — d'où la protection (غِفَارَة, le "
     "voile) puis le pardon, car pardonner c'est couvrir la faute. Le schéma "
     "فَعَّال : celui qui couvre sans cesse.",
     "From غَفَرَ, 'to cover, to veil' — hence protection (غِفَارَة, a "
     "covering) and then forgiveness, for to forgive is to cover the fault. "
     "The pattern فَعَّال: the one who covers unceasingly.",
     "💧"),
    ("الْقَهَّار", "Al-Qahhār", "ق ه ر", "q-h-r", "Le Dominateur",
     "The Subduer",
     "De قَهَرَ, « vaincre, dominer, assujettir » ; قَهْر est la domination. "
     "Le schéma فَعَّال : celui qui maîtrise irrésistiblement toute chose.",
     "From قَهَرَ, 'to overcome, to dominate, to subjugate'; قَهْر is "
     "domination. The pattern فَعَّال: the one who irresistibly masters all "
     "things.",
     "🌩️"),
    ("الْوَهَّاب", "Al-Wahhāb", "و ه ب", "w-h-b", "Le Donateur",
     "The Bestower",
     "De وَهَبَ, « donner gratuitement, offrir sans retour » ; هِبَة est le "
     "don désintéressé. Le schéma فَعَّال : celui qui ne cesse de donner sans "
     "attendre de contrepartie.",
     "From وَهَبَ, 'to give freely, to bestow with no return'; هِبَة is a "
     "gratuitous gift. The pattern فَعَّال: the one who gives endlessly with "
     "no counterpart.",
     "🎁"),
    ("الرَّزَّاق", "Ar-Razzāq", "ر ز ق", "r-z-q", "Le Pourvoyeur",
     "The Provider",
     "De رَزَقَ, « attribuer la subsistance, pourvoir » ; رِزْق est la "
     "nourriture et la part allouée. Le schéma فَعَّال : celui qui assure à "
     "chaque vivant de quoi vivre.",
     "From رَزَقَ, 'to allot sustenance, to provide'; رِزْق is provision and "
     "the allotted share. The pattern فَعَّال: the one who secures for every "
     "living being its means of living.",
     "🌾"),
    ("الْفَتَّاح", "Al-Fattāh", "ف ت ح", "f-t-ḥ", "L'Ouvreur", "The Opener",
     "De فَتَحَ, « ouvrir, dévoiler, trancher (juger) » ; فَتْح est "
     "l'ouverture, la victoire et la clé de ce qui est fermé. Le schéma "
     "فَعَّال : celui qui ouvre et décide.",
     "From فَتَحَ, 'to open, to disclose, to decide (judge)'; فَتْح is "
     "opening, victory, and the key to what is closed. The pattern فَعَّال: "
     "the one who opens and decides.",
     "🔑"),
    ("الْعَلِيم", "Al-'Alīm", "ع ل م", "ʿ-l-m", "L'Omniscient",
     "The All-Knowing",
     "De عَلِمَ, « savoir, connaître » ; عِلْم est le savoir et عَلَامَة le "
     "signe qui le rend lisible ; عَالَم (le monde) est le champ des signes. "
     "Schéma فَعِيل : savoir permanent et universel.",
     "From عَلِمَ, 'to know'; عِلْم is knowledge and عَلَامَة the sign that "
     "renders it legible; عَالَم (the world) is the field of signs. Pattern "
     "فَعِيل: knowledge both permanent and universal.",
     "📖"),
    ("الْقَابِض", "Al-Qābid", "ق ب ض", "q-b-ḍ", "Le Resserreur",
     "The Withholder",
     "De قَبَضَ, « saisir, serrer, retenir » ; قَبْض est la saisie et la "
     "rétention. Participe فَاعِل : celui qui contracte et retient selon sa "
     "mesure.",
     "From قَبَضَ, 'to grasp, to contract, to withhold'; قَبْض is grasping "
     "and holding back. Participle فَاعِل: the one who contracts and "
     "withholds by His measure.",
     "✊"),
    ("الْبَاسِط", "Al-Bāsit", "ب س ط", "b-s-ṭ", "Le Dilatateur",
     "The Extender",
     "De بَسَطَ, « étendre, déployer, élargir » ; بَسْط est l'extension. "
     "Participe فَاعِل, antonyme de القَابِض : celui qui déploie et répand.",
     "From بَسَطَ, 'to spread, to unfold, to widen'; بَسْط is extension. "
     "Participle فَاعِل, opposite of القَابِض: the one who spreads and "
     "pours forth.",
     "🫱"),
    ("الْخَافِض", "Al-Khāfid", "خ ف ض", "kh-f-ḍ", "L'Abaisseur",
     "The Abaser",
     "De خَفَضَ, « baisser, abaisser, réduire » ; خَفْض est l'abaissement. "
     "Participe فَاعِل : celui qui rabaisse.",
     "From خَفَضَ, 'to lower, to abase, to reduce'; خَفْض is lowering. "
     "Participle فَاعِل: the one who brings low.",
     "⬇️"),
    ("الرَّافِع", "Ar-Rāfi'", "ر ف ع", "r-f-ʿ", "L'Éleveur", "The Exalter",
     "De رَفَعَ, « lever, élever, hausser » ; رَفْع est l'élévation. "
     "Participe فَاعِل : celui qui élève en degrés.",
     "From رَفَعَ, 'to raise, to lift, to elevate'; رَفْع is elevation. "
     "Participle فَاعِل: the one who raises in ranks.",
     "⬆️"),
    ("الْمُعِزّ", "Al-Mu'izz", "ع ز ز", "ʿ-z-z", "Le Glorificateur",
     "The Honourer",
     "De la racine ع ز ز (force, honneur). Le schéma مُفْعِل (causatif) : "
     "celui qui confère la puissance et la considération.",
     "From root ع ز ز (strength, honour). The causative pattern مُفْعِل: the "
     "one who confers might and esteem.",
     "🏅"),
    ("الْمُذِلّ", "Al-Mudhill", "ذ ل ل", "dh-l-l", "L'Avilisseur",
     "The Dishonourer",
     "De ذَلَّ, « être bas, s'humilier » ; ذُلّ est l'abaissement. Le schéma "
     "مُفْعِل (causatif) : celui qui abaisse.",
     "From ذَلَّ, 'to be low, to humble oneself'; ذُلّ is abasement. The "
     "causative pattern مُفْعِل: the one who lowers.",
     "🧎"),
    ("السَّمِيع", "As-Samī'", "س م ع", "s-m-ʿ", "L'Audient", "The All-Hearing",
     "De سَمِعَ, « entendre, écouter » ; سَمْع est l'ouïe. Le schéma فَعِيل : "
     "celui qui entend tout, jusqu'au murmure le plus ténu.",
     "From سَمِعَ, 'to hear, to listen'; سَمْع is hearing. The pattern "
     "فَعِيل: the one who hears all, down to the faintest whisper.",
     "👂"),
    ("الْبَصِير", "Al-Basīr", "ب ص ر", "b-ṣ-r", "Le Clairvoyant",
     "The All-Seeing",
     "De بَصُرَ/أَبْصَرَ, « voir, percevoir » ; بَصَر est la vue. Le schéma "
     "فَعِيل : celui dont la vision embrasse tout.",
     "From بَصُرَ/أَبْصَرَ, 'to see, to perceive'; بَصَر is sight. The "
     "pattern فَعِيل: the one whose vision encompasses all.",
     "👁️"),
    ("الْحَكَم", "Al-Hakam", "ح ك م", "ḥ-k-m", "Le Juge", "The Judge",
     "De حَكَمَ, « juger, trancher, retenir » ; حُكْم est le jugement et "
     "حِكْمَة la sagesse qui le fonde. Schéma فَعَل : celui qui tranche avec "
     "vérité.",
     "From حَكَمَ, 'to judge, to decide, to restrain'; حُكْم is judgment and "
     "حِكْمَة the wisdom grounding it. Pattern فَعَل: the one who decides "
     "with truth.",
     "⚖️"),
    ("الْعَدْل", "Al-'Adl", "ع د ل", "ʿ-d-l", "L'Équitable", "The Just",
     "De عَدَلَ, « être droit, égal, équilibrer » ; عَدْل est la justice et "
     "l'équité. Sens lexical : celui qui tient toute chose en juste balance.",
     "From عَدَلَ, 'to be straight, equal, to balance'; عَدْل is justice and "
     "equity. Lexical sense: the one who holds all things in fair balance.",
     "🟰"),
    ("اللَّطِيف", "Al-Latīf", "ل ط ف", "l-ṭ-f", "Le Subtil", "The Subtle",
     "De لَطُفَ, « être ténu, fin, doux, délicat » ; لُطْف est la douceur et "
     "la finesse. Schéma فَعِيل : celui dont la science et la bienveillance "
     "pénètrent les choses les plus fines.",
     "From لَطُفَ, 'to be subtle, fine, gentle, delicate'; لُطْف is "
     "gentleness and subtlety. Pattern فَعِيل: the one whose knowledge and "
     "kindness penetrate the finest things.",
     "🍃"),
    ("الْخَبِير", "Al-Khabīr", "خ ب ر", "kh-b-r", "L'Informé", "The All-Aware",
     "De خَبَرَ, « sonder, éprouver, connaître par expérience » ; خَبَر est "
     "la nouvelle et خِبْر l'expérience. Schéma فَعِيل : celui qui connaît "
     "l'intérieur des choses.",
     "From خَبَرَ, 'to probe, to test, to know by experience'; خَبَر is "
     "news and خِبْر experience. Pattern فَعِيل: the one who knows the inner "
     "reality of things.",
     "🔍"),
    ("الْحَلِيم", "Al-Halīm", "ح ل م", "ḥ-l-m", "L'Indulgent",
     "The Forbearing",
     "De حَلَمَ, « être patient, indulgent, maître de soi » ; حِلْم est la "
     "longanimité et la raison. Schéma فَعِيل : celui qui ne se hâte pas de "
     "châtier.",
     "From حَلَمَ, 'to be patient, forbearing, self-restrained'; حِلْم is "
     "forbearance and reason. Pattern فَعِيل: the one who does not hasten to "
     "punish.",
     "🕰️"),
    ("الْعَظِيم", "Al-'Azīm", "ع ظ م", "ʿ-ẓ-m", "L'Immense",
     "The Magnificent",
     "De عَظُمَ, « être grand, imposant » ; عَظَمَة est la grandeur et عَظْم "
     "l'os, la trame solide du corps. Schéma فَعِيل : grandeur sans limite.",
     "From عَظُمَ, 'to be great, imposing'; عَظَمَة is greatness and عَظْم "
     "the bone, the body's solid frame. Pattern فَعِيل: grandeur without "
     "limit.",
     "🏔️"),
    ("الْغَفُور", "Al-Ghafūr", "غ ف ر", "gh-f-r", "Le Très-Pardonnant",
     "The All-Forgiving",
     "Même racine غ ف ر que الغَفَّار (couvrir, voiler, pardonner). Le schéma "
     "فَعُول intensif : celui dont le pardon est inépuisable.",
     "Same root غ ف ر as الغَفَّار (to cover, veil, forgive). The intensive "
     "pattern فَعُول: the one whose forgiveness is inexhaustible.",
     "🫧"),
    ("الشَّكُور", "Ash-Shakūr", "ش ك ر", "sh-k-r", "Le Reconnaissant",
     "The Most Appreciative",
     "De شَكَرَ, « remercier, reconnaître le bienfait, apprécier » ; شُكْر "
     "est la gratitude. Schéma فَعُول : celui qui reconnaît et récompense "
     "largement le moindre bien.",
     "From شَكَرَ, 'to thank, to acknowledge a favour, to appreciate'; شُكْر "
     "is gratitude. Pattern فَعُول: the one who acknowledges and generously "
     "rewards the least good.",
     "🙏"),
    ("الْعَلِيّ", "Al-'Alī", "ع ل و", "ʿ-l-w", "Le Très-Haut", "The Most High",
     "De عَلَا, « s'élever, être haut » ; عُلُوّ est la hauteur et l'élévation "
     "digne. Schéma فَعِيل : celui qui est élevé au-dessus de toute chose.",
     "From عَلَا, 'to rise, to be high'; عُلُوّ is height and lofty "
     "elevation. Pattern فَعِيل: the one raised above all things.",
     "🌌"),
    ("الْكَبِير", "Al-Kabīr", "ك ب ر", "k-b-r", "Le Grand", "The Most Great",
     "Même racine ك ب ر que الْمُتَكَبِّر (grandeur). Schéma فَعِيل : celui "
     "dont la grandeur dépasse toute mesure.",
     "Same root ك ب ر as الْمُتَكَبِّر (greatness). Pattern فَعِيل: the one "
     "whose greatness exceeds all measure.",
     "🗻"),
    ("الْحَفِيظ", "Al-Hafīz", "ح ف ظ", "ḥ-f-ẓ", "Le Gardien", "The Preserver",
     "De حَفِظَ, « garder, préserver, mémoriser » ; حِفْظ est la conservation. "
     "Schéma فَعِيل : celui qui maintient toute chose dans l'être.",
     "From حَفِظَ, 'to keep, to preserve, to memorize'; حِفْظ is "
     "preservation. Pattern فَعِيل: the one who maintains all things in "
     "being.",
     "🛡️"),
    ("الْمُقِيت", "Al-Muqīt", "ق و ت", "q-w-t", "Le Nourricier",
     "The Sustainer",
     "De قَاتَ, « nourrir, sustenter » ; قُوت est la nourriture et la ration. "
     "Schéma مُفْعِل : celui qui crée la nourriture et la fait parvenir.",
     "From قَاتَ, 'to feed, to sustain'; قُوت is food and the ration. "
     "Pattern مُفْعِل: the one who creates nourishment and delivers it.",
     "🍲"),
    ("الْحَسِيب", "Al-Hasīb", "ح س ب", "ḥ-s-b", "Le Comptable",
     "The Reckoner",
     "De حَسَبَ, « compter, calculer, tenir compte » ; حِسَاب est le compte "
     "et حَسْب la suffisance. Schéma فَعِيل : celui qui tient le compte de "
     "tout et suffit à Ses serviteurs.",
     "From حَسَبَ, 'to count, to reckon, to take account'; حِسَاب is the "
     "reckoning and حَسْب sufficiency. Pattern فَعِيل: the one who keeps "
     "account of all and suffices for His servants.",
     "🧮"),
    ("الْجَلِيل", "Al-Jalīl", "ج ل ل", "j-l-l", "Le Majestueux",
     "The Majestic",
     "De جَلَّ, « être grand, haut, surpasser » ; جَلَال est la majesté. "
     "Schéma فَعِيل : celui dont la majesté et la dignité sont absolues.",
     "From جَلَّ, 'to be great, lofty, to surpass'; جَلَال is majesty. "
     "Pattern فَعِيل: the one whose majesty and dignity are absolute.",
     "🎖️"),
    ("الْكَرِيم", "Al-Karīm", "ك ر م", "k-r-m", "Le Généreux", "The Generous",
     "De كَرُمَ, « être généreux, noble, précieux » ; كَرَم est la générosité "
     "et la noblesse. Schéma فَعِيل : celui qui donne sans être sollicité.",
     "From كَرُمَ, 'to be generous, noble, precious'; كَرَم is generosity "
     "and nobility. Pattern فَعِيل: the one who gives even unasked.",
     "💎"),
    ("الرَّقِيب", "Ar-Raqīb", "ر ق ب", "r-q-b", "L'Observateur",
     "The Watchful",
     "De رَقَبَ, « observer, surveiller, guetter » ; رَقَبَة est la nuque que "
     "l'on surveille. Schéma فَعِيل : celui qui observe attentivement.",
     "From رَقَبَ, 'to watch, to observe, to keep guard'; رَقَبَة is the "
     "nape one keeps an eye on. Pattern فَعِيل: the one who watches "
     "attentively.",
     "🔭"),
    ("الْمُجِيب", "Al-Mujīb", "ج و ب", "j-w-b", "Le Répondant",
     "The Responsive",
     "De أَجَابَ, « répondre, exaucer » ; جَوَاب est la réponse et جَابَ "
     "l'action de fendre/traverser. Schéma مُفْعِل : celui qui répond à "
     "l'appel.",
     "From أَجَابَ, 'to answer, to grant'; جَوَاب is the answer and جَابَ to "
     "cut through. Pattern مُفْعِل: the one who answers the call.",
     "📣"),
    ("الْوَاسِع", "Al-Wāsi'", "و س ع", "w-s-ʿ", "L'Immense", "The Vast",
     "De وَسِعَ, « contenir, embrasser, être large » ; سَعَة est l'amplitude "
     "et وُسْع la capacité. Participe فَاعِل : celui dont la science et la "
     "grâce embrassent tout.",
     "From وَسِعَ, 'to contain, to embrace, to be wide'; سَعَة is amplitude "
     "and وُسْع capacity. Participle فَاعِل: the one whose knowledge and "
     "grace embrace all.",
     "🌐"),
    ("الْحَكِيم", "Al-Hakīm", "ح ك م", "ḥ-k-m", "Le Sage", "The Wise",
     "Même racine ح ك م que الْحَكَم (juger, retenir). Schéma فَعِيل : celui "
     "dont l'agir et la création sont parfaitement réglés par la sagesse.",
     "Same root ح ك م as الْحَكَم (to judge, restrain). Pattern فَعِيل: the "
     "one whose acts and creation are perfectly ordered by wisdom.",
     "🦉"),
    ("الْوَدُود", "Al-Wadūd", "و د د", "w-d-d", "L'Aimant", "The Loving",
     "De وَدَّ, « aimer, chérir, souhaiter » ; وُدّ et مَوَدَّة sont l'amour "
     "et l'affection. Schéma فَعُول : celui qui aime et qui est aimé.",
     "From وَدَّ, 'to love, to cherish, to wish'; وُدّ and مَوَدَّة are love "
     "and affection. Pattern فَعُول: the one who loves and is loved.",
     "❤️"),
    ("الْمَجِيد", "Al-Majīd", "م ج د", "m-j-d", "Le Glorieux", "The Glorious",
     "De مَجَدَ, « être glorieux, noble » ; مَجْد est la gloire et l'honneur. "
     "Schéma فَعِيل : celui dont la gloire est parfaite.",
     "From مَجَدَ, 'to be glorious, noble'; مَجْد is glory and honour. "
     "Pattern فَعِيل: the one whose glory is perfect.",
     "🌟"),
    ("الْبَاعِث", "Al-Bā'ith", "ب ع ث", "b-ʿ-th", "Le Ressusciteur",
     "The Resurrector",
     "De بَعَثَ, « envoyer, éveiller, ressusciter » ; بَعْث est l'envoi et la "
     "résurrection. Participe فَاعِل : celui qui envoie, suscite et ranime.",
     "From بَعَثَ, 'to send, to rouse, to resurrect'; بَعْث is sending and "
     "resurrection. Participle فَاعِل: the one who sends, rouses and revives.",
     "🌅"),
    ("الشَّهِيد", "Ash-Shahīd", "ش ه د", "sh-h-d", "Le Témoin", "The Witness",
     "De شَهِدَ, « être présent, témoigner » ; شَهَادَة est le témoignage et "
     "شَاهِد le témoin. Schéma فَعِيل : celui qui est présent à toute chose et "
     "en témoigne.",
     "From شَهِدَ, 'to be present, to bear witness'; شَهَادَة is testimony "
     "and شَاهِد the witness. Pattern فَعِيل: the one present to all things "
     "and witnessing them.",
     "📜"),
    ("الْحَقّ", "Al-Haqq", "ح ق ق", "ḥ-q-q", "La Vérité", "The Truth",
     "De حَقَّ, « être vrai, établi, nécessaire » ; حَقّ est le vrai, le réel, "
     "ce qui est dû. Sens lexical : la réalité ferme et incontestable.",
     "From حَقَّ, 'to be true, established, necessary'; حَقّ is the true, "
     "the real, what is due. Lexical sense: firm and incontestable reality.",
     "✅"),
    ("الْوَكِيل", "Al-Wakīl", "و ك ل", "w-k-l", "Le Garant", "The Trustee",
     "De وَكَلَ, « confier, s'en remettre à » ; وَكِيل est le mandataire en "
     "qui l'on a confiance. Schéma فَعِيل : celui à qui toute affaire est "
     "confiée et qui suffit.",
     "From وَكَلَ, 'to entrust, to rely upon'; وَكِيل is the trusted "
     "deputy. Pattern فَعِيل: the one to whom every affair is entrusted and "
     "who suffices.",
     "🤝"),
    ("الْقَوِيّ", "Al-Qawī", "ق و ي", "q-w-y", "Le Fort", "The Strong",
     "De قَوِيَ, « être fort, vigoureux » ; قُوَّة est la force. Schéma "
     "فَعِيل : celui dont la force ne connaît aucune faiblesse.",
     "From قَوِيَ, 'to be strong, vigorous'; قُوَّة is strength. Pattern "
     "فَعِيل: the one whose strength knows no weakness.",
     "🏋️"),
    ("الْمَتِين", "Al-Matīn", "م ت ن", "m-t-n", "Le Solide", "The Firm",
     "De مَتَّنَ, « rendre ferme, consolider » ; مَتَانَة est la fermeté et "
     "مَتْن le dos, la partie solide. Schéma فَعِيل : solidité inébranlable.",
     "From مَتَّنَ, 'to make firm, to consolidate'; مَتَانَة is firmness and "
     "مَتْن the solid back. Pattern فَعِيل: unshakable solidity.",
     "🏛️"),
    ("الْوَلِيّ", "Al-Walī", "و ل ي", "w-l-y", "L'Allié",
     "The Protecting Friend",
     "De وَلِيَ, « être proche, protéger, gouverner » ; وِلَايَة est la "
     "proximité tutélaire. Schéma فَعِيل : le proche qui prend en charge et "
     "protège.",
     "From وَلِيَ, 'to be near, to protect, to govern'; وِلَايَة is "
     "protective nearness. Pattern فَعِيل: the near one who supports and "
     "protects.",
     "🫂"),
    ("الْحَمِيد", "Al-Hamīd", "ح م د", "ḥ-m-d", "Le Digne de louange",
     "The Praiseworthy",
     "De حَمِدَ, « louer, approuver » ; حَمْد est la louange. Schéma فَعِيل : "
     "celui qui est digne de louange en tout temps.",
     "From حَمِدَ, 'to praise, to approve'; حَمْد is praise. Pattern "
     "فَعِيل: the one worthy of praise at all times.",
     "🙌"),
    ("الْمُحْصِي", "Al-Muhsī", "ح ص ي", "ḥ-ṣ-y", "L'Énumérateur",
     "The Accounter",
     "De أَحْصَى, « dénombrer, compter exactement » ; إِحْصَاء est le "
     "dénombrement (d'où حَصَاة, le caillou servant à compter). Schéma "
     "مُفْعِل : celui qui dénombre toute chose avec exactitude.",
     "From أَحْصَى, 'to enumerate, to count exactly'; إِحْصَاء is "
     "enumeration (hence حَصَاة, a counting pebble). Pattern مُفْعِل: the one "
     "who counts all things exactly.",
     "🔢"),
    ("الْمُبْدِئ", "Al-Mubdi'", "ب د أ", "b-d-ʾ", "Le Commenceur",
     "The Initiator",
     "De بَدَأَ, « commencer, initier » ; مَبْدَأ est le principe et le début. "
     "Schéma مُفْعِل : celui qui commence la création sans modèle.",
     "From بَدَأَ, 'to begin, to initiate'; مَبْدَأ is the principle and "
     "beginning. Pattern مُفْعِل: the one who begins creation without a "
     "model.",
     "🌱"),
    ("الْمُعِيد", "Al-Mu'īd", "ع و د", "ʿ-w-d", "Le Rénovateur",
     "The Restorer",
     "De عَادَ, « revenir » ; أَعَادَ est « faire revenir, rétablir ». Schéma "
     "مُفْعِل : celui qui ramène la création à son état initial.",
     "From عَادَ, 'to return'; أَعَادَ is 'to bring back, to restore'. "
     "Pattern مُفْعِل: the one who returns creation to its initial state.",
     "🔄"),
    ("الْمُحْيِي", "Al-Muhyī", "ح ي ي", "ḥ-y-y", "Le Vivificateur",
     "The Giver of Life",
     "De حَيَّ, « vivre » ; حَيَاة est la vie, أَحْيَا « donner vie, "
     "revivifier ». Schéma مُفْعِل : celui qui donne la vie.",
     "From حَيَّ, 'to live'; حَيَاة is life, أَحْيَا 'to give life, to "
     "revive'. Pattern مُفْعِل: the one who gives life.",
     "💚"),
    ("الْمُمِيت", "Al-Mumīt", "م و ت", "m-w-t", "Le Mortificateur",
     "The Bringer of Death",
     "De مَاتَ, « mourir » ; مَوْت est la mort, أَمَاتَ « faire mourir ». "
     "Schéma مُفْعِل : celui qui décrète la mort.",
     "From مَاتَ, 'to die'; مَوْت is death, أَمَاتَ 'to cause to die'. "
     "Pattern مُفْعِل: the one who decrees death.",
     "🥀"),
    ("الْحَيّ", "Al-Hayy", "ح ي ي", "ḥ-y-y", "Le Vivant", "The Ever-Living",
     "Même racine ح ي ي que الْمُحْيِي (vie). Schéma فَعْل : celui dont la vie "
     "est permanente, sans début ni fin.",
     "Same root ح ي ي as الْمُحْيِي (life). Pattern فَعْل: the one whose life "
     "is permanent, without beginning or end.",
     "💫"),
    ("الْقَيُّوم", "Al-Qayyūm", "ق و م", "q-w-m", "Le Subsistant",
     "The Self-Subsisting",
     "De قَامَ, « se tenir debout, se maintenir » ; قِيَام est la station "
     "droite et le soutien. Schéma فَيْعُول : celui qui se tient par "
     "lui-même et fait subsister toute chose.",
     "From قَامَ, 'to stand, to uphold'; قِيَام is upright standing and "
     "sustaining. Pattern فَيْعُول: the one who stands by Himself and upholds "
     "all things.",
     "🧭"),
    ("الْوَاجِد", "Al-Wājid", "و ج د", "w-j-d", "Le Trouveur", "The Finder",
     "De وَجَدَ, « trouver, exister, éprouver » ; وُجُود est l'existence et "
     "وُجْد la capacité. Participe فَاعِل : celui qui ne manque de rien.",
     "From وَجَدَ, 'to find, to exist, to perceive'; وُجُود is existence and "
     "وُجْد capacity. Participle فَاعِل: the one who lacks nothing.",
     "🔎"),
    ("الْمَاجِد", "Al-Mājid", "م ج د", "m-j-d", "Le Noble", "The Noble",
     "Même racine م ج د que الْمَجِيد (gloire). Schéma فَاعِل : celui dont la "
     "noblesse et la bienfaisance sont débordantes.",
     "Same root م ج د as الْمَجِيد (glory). Pattern فَاعِل: the one whose "
     "nobility and beneficence overflow.",
     "🏵️"),
    ("الْوَاحِد", "Al-Wāhid", "و ح د", "w-ḥ-d", "L'Unique", "The One",
     "De وَحَدَ, « être un, seul » ; وَحْدَة est l'unité. Participe فَاعِل : "
     "celui qui est un dans son essence, sans associé.",
     "From وَحَدَ, 'to be one, alone'; وَحْدَة is unity. Participle فَاعِل: "
     "the one who is one in essence, without any partner.",
     "1️⃣"),
    ("الْأَحَد", "Al-Ahad", "أ ح د", "ʾ-ḥ-d", "L'Un", "The Unique",
     "Racine de l'unicité (و ح د / أ ح د) ; أَحَد désigne l'un absolu, "
     "indivisible. Sens lexical : l'un sans pluralité ni division possible.",
     "From the root of oneness (و ح د / أ ح د); أَحَد denotes the absolute, "
     "indivisible one. Lexical sense: the one admitting no plurality or "
     "division.",
     "☝️"),
    ("الصَّمَد", "As-Samad", "ص م د", "ṣ-m-d", "L'Éternel", "The Eternal",
     "De صَمَدَ, « se tourner vers, être solide, sans creux » ; الصَّمَد est "
     "celui vers qui l'on va et qui ne dépend de rien. Sens lexical : le "
     "solide, sans besoin ni vide.",
     "From صَمَدَ, 'to turn to, to be solid, without hollow'; الصَّمَد is the "
     "one all turn to, depending on nothing. Lexical sense: the solid, "
     "needing nothing and void of any lack.",
     "🗿"),
    ("الْقَادِر", "Al-Qādir", "ق د ر", "q-d-r", "Le Capable", "The Able",
     "De قَدَرَ, « pouvoir, mesurer, décréter » ; قُدْرَة est la capacité et "
     "قَدَر le décret-mesure. Participe فَاعِل : celui qui est capable de "
     "toute chose.",
     "From قَدَرَ, 'to be able, to measure, to decree'; قُدْرَة is power and "
     "قَدَر the measuring decree. Participle فَاعِل: the one able to do all "
     "things.",
     "⭐"),
    ("الْمُقْتَدِر", "Al-Muqtadir", "ق د ر", "q-d-r", "Le Puissant",
     "The Powerful",
     "Racine ق د ر (pouvoir) au schéma مُفْتَعِل de اِقْتَدَرَ, « exercer "
     "pleinement sa puissance » : la capacité portée à sa plénitude.",
     "Root ق د ر (power) in the pattern مُفْتَعِل from اِقْتَدَرَ, 'to "
     "exercise full power': ability raised to its fullness.",
     "🧨"),
    ("الْمُقَدِّم", "Al-Muqaddim", "ق د م", "q-d-m", "Le Précurseur",
     "The Expediter",
     "De قَدَّمَ, « avancer, mettre en avant, faire précéder » ; قَدَم est le "
     "pas et l'antériorité. Schéma مُفَعِّل : celui qui avance ce qu'il veut.",
     "From قَدَّمَ, 'to put forward, to advance, to cause to precede'; قَدَم "
     "is the step and precedence. Pattern مُفَعِّل: the one who advances what "
     "He wills.",
     "⏩"),
    ("الْمُؤَخِّر", "Al-Mu'akhkhir", "أ خ ر", "ʾ-kh-r", "Le Retardateur",
     "The Delayer",
     "De أَخَّرَ, « retarder, mettre en arrière » ; آخِر est le dernier. "
     "Schéma مُفَعِّل : celui qui retarde selon sa sagesse.",
     "From أَخَّرَ, 'to delay, to put back'; آخِر is the last. Pattern "
     "مُفَعِّل: the one who delays according to His wisdom.",
     "⏳"),
    ("الْأَوَّل", "Al-Awwal", "أ و ل", "ʾ-w-l", "Le Premier", "The First",
     "De آلَ, « revenir à l'origine » ; أَوَّل est le premier et أَوَّلَ "
     "« interpréter, ramener au sens premier ». Sens lexical : celui avant "
     "qui rien n'était.",
     "From آلَ, 'to return to the origin'; أَوَّل is the first, أَوَّلَ 'to "
     "interpret, to trace back'. Lexical sense: the one before whom nothing "
     "was.",
     "🥇"),
    ("الْآخِر", "Al-Ākhir", "أ خ ر", "ʾ-kh-r", "Le Dernier", "The Last",
     "Racine أ خ ر (être après, retarder) ; آخِر est le dernier. Sens "
     "lexical : celui après qui rien ne subsiste.",
     "Root أ خ ر (to be after, to delay); آخِر is the last. Lexical sense: "
     "the one after whom nothing remains.",
     "🏁"),
    ("الظَّاهِر", "Az-Zāhir", "ظ ه ر", "ẓ-h-r", "L'Apparent", "The Manifest",
     "De ظَهَرَ, « paraître, être visible, l'emporter » ; ظُهُور est "
     "l'apparition et ظَهْر le support visible. Participe فَاعِل : celui qui "
     "est manifeste par Ses signes.",
     "From ظَهَرَ, 'to appear, to be visible, to prevail'; ظُهُور is "
     "appearance and ظَهْر the visible support. Participle فَاعِل: the one "
     "manifest through His signs.",
     "☀️"),
    ("الْبَاطِن", "Al-Bātin", "ب ط ن", "b-ṭ-n", "Le Caché", "The Hidden",
     "De بَطَنَ, « être caché, être intérieur » ; بَاطِن est l'intérieur et "
     "بَطْن le ventre, la profondeur. Participe فَاعِل : celui qui est caché "
     "à la vue.",
     "From بَطَنَ, 'to be hidden, to be inner'; بَاطِن is the inner and "
     "بَطْن the belly, the depth. Participle فَاعِل: the one hidden from "
     "sight.",
     "🌑"),
    ("الْوَالِي", "Al-Wālī", "و ل ي", "w-l-y", "Le Gouverneur", "The Governor",
     "Racine و ل ي (être proche, protéger, gouverner) ; وَالِي est celui qui "
     "administre et gère. Participe فَاعِل : celui qui conduit toute affaire.",
     "Root و ل ي (to be near, to protect, to govern); وَالِي is the one who "
     "administers and manages. Participle فَاعِل: the one who conducts every "
     "affair.",
     "🗺️"),
    ("الْمُتَعَالِي", "Al-Muta'ālī", "ع ل و", "ʿ-l-w", "Le Très-Élevé",
     "The Most Exalted",
     "Racine ع ل و (hauteur) au schéma مُتَفَاعِل de تَعَالَى, « s'élever "
     "haut » : celui qui s'élève au-dessus de toute conception.",
     "Root ع ل و (height) in the pattern مُتَفَاعِل from تَعَالَى, 'to rise "
     "high': the one exalted beyond all conception.",
     "🏔️"),
    ("الْبَرّ", "Al-Barr", "ب ر ر", "b-r-r", "Le Bienfaisant",
     "The Source of Goodness",
     "De بَرَّ, « être bon, pieux, véridique » ; بِرّ est la bonté et la "
     "droiture, بَرّ la terre ferme. Sens lexical : celui dont la bonté est "
     "vaste et constante.",
     "From بَرَّ, 'to be good, dutiful, truthful'; بِرّ is goodness and "
     "rectitude, بَرّ the dry land. Lexical sense: the one whose goodness is "
     "vast and constant.",
     "🌳"),
    ("التَّوَّاب", "At-Tawwāb", "ت و ب", "t-w-b", "L'Accueillant au repentir",
     "The Acceptor of Repentance",
     "De تَابَ, « revenir, se repentir » ; تَوْبَة est le retour et le "
     "repentir. Schéma فَعَّال : celui qui accueille sans cesse le retour de "
     "Ses serviteurs.",
     "From تَابَ, 'to turn back, to repent'; تَوْبَة is the return and "
     "repentance. Pattern فَعَّال: the one who endlessly welcomes His "
     "servants' return.",
     "↩️"),
    ("الْمُنْتَقِم", "Al-Muntaqim", "ن ق م", "n-q-m", "Le Vengeur",
     "The Avenger",
     "De اِنْتَقَمَ, « châtier, tirer vengeance » ; نِقْمَة est la "
     "rétribution. Schéma مُفْتَعِل : celui qui fait justice en châtiant le "
     "méfait.",
     "From اِنْتَقَمَ, 'to punish, to take retribution'; نِقْمَة is "
     "retribution. Pattern مُفْتَعِل: the one who does justice by punishing "
     "wrongdoing.",
     "⚔️"),
    ("الْعَفُوّ", "Al-'Afuww", "ع ف و", "ʿ-f-w", "Le Pardonneur",
     "The Pardoner",
     "De عَفَا, « effacer, pardonner, surabonder » ; عَفْو est l'effacement "
     "de la faute et le surplus. Schéma فَعُول : celui qui efface les fautes.",
     "From عَفَا, 'to efface, to pardon, to abound'; عَفْو is the effacing "
     "of a fault and what abounds. Pattern فَعُول: the one who effaces "
     "faults.",
     "🧽"),
    ("الرَّؤُوف", "Ar-Ra'ūf", "ر أ ف", "r-ʾ-f", "Le Compatissant",
     "The Compassionate",
     "De رَأَفَ, « être saisi de compassion » ; رَأْفَة est la compassion "
     "vive. Schéma فَعُول : celui dont la tendresse est intense.",
     "From رَأَفَ, 'to be moved to compassion'; رَأْفَة is keen compassion. "
     "Pattern فَعُول: the one whose tenderness is intense.",
     "🫶"),
    ("مَالِكُ الْمُلْك", "Mālik al-Mulk", "م ل ك", "m-l-k", "Maître de la Royauté",
     "Master of the Kingdom",
     "De la racine م ل ك (posséder, régner) : مَالِك (détenteur) et مُلْك "
     "(royaume, souveraineté). Sens lexical : celui qui possède et régit tout "
     "le royaume.",
     "From root م ل ك (to own, to reign): مَالِك (owner) and مُلْك (kingdom, "
     "sovereignty). Lexical sense: the one who owns and rules the entire "
     "kingdom.",
     "👑"),
    ("ذُو الْجَلَالِ وَالْإِكْرَام", "Dhū al-Jalāli wal-Ikrām", "ج ل ل · ك ر م",
     "j-l-l · k-r-m", "Détenteur de Majesté et de Générosité",
     "Possessor of Majesty and Honour",
     "Composé de ج ل ل (majesté : جَلَال) et ك ر م (noblesse, générosité : "
     "إِكْرَام / كَرَم). Sens lexical : celui qui réunit la majesté et la "
     "munificence.",
     "Compounded of ج ل ل (majesty: جَلَال) and ك ر م (nobility, generosity: "
     "إِكْرَام / كَرَم). Lexical sense: the one who joins majesty and "
     "munificence.",
     "💠"),
    ("الْمُقْسِط", "Al-Muqsit", "ق س ط", "q-s-ṭ", "L'Équitable",
     "The Equitable",
     "De أَقْسَطَ, « être juste, équitable » ; قِسْط est la justice et la part "
     "égale. Schéma مُفْعِل : celui qui rend à chacun sa juste part.",
     "From أَقْسَطَ, 'to be just, equitable'; قِسْط is justice and an equal "
     "share. Pattern مُفْعِل: the one who gives each its due share.",
     "🟰"),
    ("الْجَامِع", "Al-Jāmi'", "ج م ع", "j-m-ʿ", "Le Rassembleur",
     "The Gatherer",
     "De جَمَعَ, « réunir, rassembler » ; جَمْع est la réunion. Participe "
     "فَاعِل : celui qui rassemble les créatures, les peuples et les comptes.",
     "From جَمَعَ, 'to gather, to unite'; جَمْع is gathering. Participle "
     "فَاعِل: the one who gathers creatures, peoples and accounts.",
     "🧩"),
    ("الْغَنِيّ", "Al-Ghaniyy", "غ ن ي", "gh-n-y", "Le Riche",
     "The Self-Sufficient",
     "De غَنِيَ, « être riche, se passer de » ; غِنَى est la richesse et "
     "l'indépendance. Schéma فَعِيل : celui qui se suffit à lui-même.",
     "From غَنِيَ, 'to be rich, to be free from need'; غِنَى is wealth and "
     "independence. Pattern فَعِيل: the one sufficient unto Himself.",
     "💰"),
    ("الْمُغْنِي", "Al-Mughnī", "غ ن ي", "gh-n-y", "L'Enrichisseur",
     "The Enricher",
     "Racine غ ن ي (richesse) au schéma مُفْعِل (causatif) : celui qui rend "
     "autrui riche et indépendant.",
     "Root غ ن ي (wealth) in the causative pattern مُفْعِل: the one who makes "
     "others rich and independent.",
     "🌾"),
    ("الْمَانِع", "Al-Māni'", "م ن ع", "m-n-ʿ", "Le Préventeur",
     "The Withholder",
     "De مَنَعَ, « empêcher, défendre, retenir » ; مَنْع est l'empêchement et "
     "la protection. Participe فَاعِل : celui qui retient ce qu'il veut.",
     "From مَنَعَ, 'to prevent, to forbid, to withhold'; مَنْع is prevention "
     "and protection. Participle فَاعِل: the one who withholds what He wills.",
     "🚧"),
    ("الضَّارّ", "Ad-Dārr", "ض ر ر", "ḍ-r-r", "Le Nuisant",
     "The Distresser",
     "De ضَرَّ, « nuire, léser » ; ضَرَر est le dommage. Participe فَاعِل : "
     "celui qui, dans l'usage coranique, peut éprouver par un mal.",
     "From ضَرَّ, 'to harm, to injure'; ضَرَر is harm. Participle فَاعِل: "
     "the one who, in Qur'anic usage, may test through harm.",
     "⚠️"),
    ("النَّافِع", "An-Nāfi'", "ن ف ع", "n-f-ʿ", "L'Utile", "The Benefactor",
     "De نَفَعَ, « profiter, être utile » ; نَفْع est le profit et l'utilité. "
     "Participe فَاعِل : celui qui apporte le bien et le profit.",
     "From نَفَعَ, 'to benefit, to be useful'; نَفْع is profit and utility. "
     "Participle فَاعِل: the one who brings good and benefit.",
     "🌿"),
    ("النُّور", "An-Nūr", "ن و ر", "n-w-r", "La Lumière", "The Light",
     "De نَارَ/أَنَارَ, « éclairer, briller » ; نُور est la lumière et نَار le "
     "feu qui éclaire. Sens lexical : celui dont procède toute clarté.",
     "From نَارَ/أَنَارَ, 'to shine, to give light'; نُور is light and نَار "
     "the fire that illuminates. Lexical sense: the one from whom all "
     "brightness proceeds.",
     "🕯️"),
    ("الْهَادِي", "Al-Hādī", "ه د ي", "h-d-y", "Le Guide", "The Guide",
     "De هَدَى, « guider, conduire, montrer le chemin » ; هُدَى est la "
     "guidance et هَدْي l'offrande conduite. Participe فَاعِل : celui qui "
     "dirige vers le droit chemin.",
     "From هَدَى, 'to guide, to lead, to show the way'; هُدَى is guidance "
     "and هَدْي the led offering. Participle فَاعِل: the one who leads to the "
     "right path.",
     "🧭"),
    ("الْبَدِيع", "Al-Badī'", "ب د ع", "b-d-ʿ", "L'Incomparable",
     "The Incomparable Originator",
     "De بَدَعَ, « créer sans modèle, innover » ; بِدْع est le nouveau sans "
     "précédent. Schéma فَعِيل : celui qui crée sans modèle ni égal.",
     "From بَدَعَ, 'to create without a model, to bring forth anew'; بِدْع "
     "is the unprecedented. Pattern فَعِيل: the one who creates without model "
     "or equal.",
     "🎨"),
    ("الْبَاقِي", "Al-Bāqī", "ب ق ي", "b-q-y", "Le Permanent",
     "The Everlasting",
     "De بَقِيَ, « demeurer, durer » ; بَقَاء est la permanence. Participe "
     "فَاعِل : celui qui demeure à jamais.",
     "From بَقِيَ, 'to remain, to last'; بَقَاء is permanence. Participle "
     "فَاعِل: the one who endures forever.",
     "♾️"),
    ("الْوَارِث", "Al-Wārith", "و ر ث", "w-r-th", "L'Héritier",
     "The Inheritor",
     "De وَرِثَ, « hériter, succéder » ; إِرْث et وِرَاثَة sont l'héritage. "
     "Participe فَاعِل : celui à qui tout revient en définitive.",
     "From وَرِثَ, 'to inherit, to succeed'; إِرْث and وِرَاثَة are "
     "inheritance. Participle فَاعِل: the one to whom all ultimately "
     "returns.",
     "📜"),
    ("الرَّشِيد", "Ar-Rashīd", "ر ش د", "r-sh-d", "Le Bien-Guide",
     "The Guide to the Right Path",
     "De رَشِدَ/رَشَدَ, « être bien dirigé, mûr, de bon conseil » ; رُشْد est "
     "la droiture et la maturité. Schéma فَعِيل : celui dont la direction est "
     "infaillible.",
     "From رَشِدَ/رَشَدَ, 'to be rightly guided, mature, sound'; رُشْد is "
     "rectitude and maturity. Pattern فَعِيل: the one whose direction is "
     "infallible.",
     "🧭"),
    ("الصَّبُور", "As-Sabūr", "ص ب ر", "ṣ-b-r", "Le Patient", "The Patient",
     "De صَبَرَ, « endurer, se contenir, lier fermement » ; صَبْر est la "
     "patience et la constance. Schéma فَعُول : celui dont la patience est "
     "inépuisable.",
     "From صَبَرَ, 'to endure, to restrain oneself, to bind firmly'; صَبْر "
     "is patience and constancy. Pattern فَعُول: the one whose patience is "
     "inexhaustible.",
     "🧘"),
]

# Teinte de code couleur par Nom : angle d'or pour une répartition régulière.
def _hue(n: int) -> int:
    """Teinte (0-359°) propre au rang ``n`` (répartition par angle d'or)."""
    return (n * 137) % 360


NAMES = [
    {
        "n": i,
        "ar": ar,
        "tr": tr,
        "root_ar": root_ar,
        "root_tr": root_tr,
        "fr": fr,
        "en": en,
        "etym_fr": etym_fr,
        "etym_en": etym_en,
        "icon": icon,
        "hue": _hue(i),
    }
    for i, (ar, tr, root_ar, root_tr, fr, en, etym_fr, etym_en, icon)
    in enumerate(_RAW, start=1)
]


def count() -> int:
    """Nombre de Noms (99)."""
    return len(NAMES)


def translation(name: dict, lang: str = "fr") -> str:
    """Traduction directe du Nom dans la langue demandée."""
    return name.get(lang) or name.get("fr") or ""


def etymology(name: dict, lang: str = "fr") -> str:
    """Définition étymologique de la racine, dans la langue demandée."""
    return name.get(f"etym_{lang}") or name.get("etym_fr") or ""


def _fold(s: str) -> str:
    """Minuscule sans accents, pour un filtre tolérant."""
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s or "")
        if not unicodedata.combining(ch)
    ).lower()


def search(query: str, lang: str = "fr") -> list:
    """Noms dont un champ (arabe, translittération, sens, racine) contient ``query``."""
    q = _fold(query.strip())
    if not q:
        return list(NAMES)
    q_tight = q.replace(" ", "").replace("-", "").replace("·", "")
    out = []
    for name in NAMES:
        fields = [name["ar"], name["tr"], name["fr"], name["en"],
                  name["root_ar"], name["root_tr"]]
        hay = _fold(" ".join(fields))
        tight = hay.replace(" ", "").replace("-", "").replace("·", "")
        if q in hay or q_tight in tight:
            out.append(name)
    return out
