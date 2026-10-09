"""Interface en ligne de commande de quranlab."""

import argparse
import sys

from . import config, db, download, search


def _fix_console() -> None:
    """Force l'UTF-8 sur la sortie console (Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _ref(sura: int, aya: int) -> str:
    return f"{sura}:{aya}"


def cmd_init(args) -> int:
    download.download_all(force=args.force)
    from .build import build

    build()
    print("\nPrêt. Essayez :")
    print("  python -m quranlab root رحم")
    print("  python -m quranlab theme salat")
    print("  python -m quranlab verse 2:255")
    return 0


def cmd_search(args) -> int:
    con = db.connect()
    try:
        if args.lang == "ar":
            rows = search.search_arabic(con, args.query, limit=args.limit)
            print(f"{len(rows)} verset(s) contenant « {args.query} »\n")
            for r in rows:
                print(f"[{_ref(r['sura'], r['aya'])}] {r['text_uthmani']}")
        else:
            rows = search.search_french(
                con, args.query, limit=args.limit, translation_key=args.translation
            )
            print(f"{len(rows)} verset(s) — recherche « {args.query} »\n")
            # search_french est dédupliqué (1 ligne / verset) : le détail des
            # traductions touchées est récupéré séparément pour l'affichage.
            refs = [(r["sura"], r["aya"]) for r in rows]
            by_verse: dict = {}
            for d in search.french_matches_rows(
                con, args.query, refs, translation_key=args.translation
            ):
                by_verse.setdefault((d["sura"], d["aya"]), []).append(d)
            for r in rows:
                print(f"[{_ref(r['sura'], r['aya'])}] {r['text_uthmani']}")
                for d in by_verse.get((r["sura"], r["aya"]), []):
                    print(f"    ({d['author']}) {d['translation']}")
        return 0
    finally:
        con.close()


def cmd_root(args) -> int:
    con = db.connect()
    try:
        res = search.search_root(
            con, args.root, limit=args.limit, with_context=args.context
        )
        if not res["found"]:
            print(f"Racine introuvable : {args.root}")
            return 1
        print(
            f"Racine {res['root_arabic']}  [{res['root_buckwalter']}] — "
            f"{res['count']} occurrence(s) dans {res['verses_count']} verset(s)\n"
        )
        for o in res["occurrences"]:
            print(f"[{_ref(o['sura'], o['aya'])}] {o['text_uthmani']}")
            print(
                f"    mot: {o['form_arabic']} ({o['transliteration']})  "
                f"POS={o['pos']}  lemme={o['lemma_buckwalter']}"
            )
            if "context" in o:
                for b in o["context"]["before"]:
                    print(f"      ↳ {_ref(b['sura'], b['aya'])} {b['text_uthmani']}")
                for a in o["context"]["after"]:
                    print(f"      ↳ {_ref(a['sura'], a['aya'])} {a['text_uthmani']}")
        return 0
    finally:
        con.close()


def cmd_verse(args) -> int:
    sura, aya = (int(x) for x in args.reference.split(":"))
    con = db.connect()
    try:
        v = search.get_verse(con, sura, aya)
        if v is None:
            print(f"Verset introuvable : {args.reference}")
            return 1
        print(f"--- {db.surah_name(con, sura)} — verset {aya} ---\n")
        print(v["text_uthmani"])
        print()
        for t in v["translations"]:
            print(f"• {t['author']} : {t['text']}")
        print("\nMots (forme | translittération | racine | POS) :")
        for w in v["words"]:
            print(
                f"  {w['word_index']:>2}. {w['form_arabic']:<18} "
                f"{w['transliteration'] or '':<22} "
                f"{w['root_arabic'] or '-':<8} {w['pos'] or ''}"
            )
        return 0
    finally:
        con.close()


def cmd_theme(args) -> int:
    con = db.connect()
    try:
        res = search.theme(con, args.name, limit=args.limit)
        if not res["found"]:
            print(f"Thème inconnu : {args.name}")
            if res.get("suggestions"):
                print("Vouliez-vous dire : " + ", ".join(res["suggestions"]))
            print("Disponibles : " + ", ".join(res["available"]))
            return 1
        print(f"### {res['label']}  —  [{res['category']}]")
        if res["description"]:
            print(res["description"])
        print(f"Racines : {', '.join(res['roots'])}")
        print(f"{res['verses_count']} verset(s) — cartographie intra-coranique\n")
        for v in res["verses"]:
            row = search.get_verse(con, v["sura"], v["aya"])
            print(f"[{_ref(v['sura'], v['aya'])}] {row['text_uthmani']}")
            print(f"    sources: {', '.join(v['sources'])}")
        return 0
    finally:
        con.close()


def cmd_controversies(args) -> int:
    topics = search.controversy_topics()
    print(f"{len(topics)} sujet(s) d'analyse textuelle :\n")
    for key, spec in sorted(topics.items()):
        print(f"  {key:<20} {spec['label']}")
        print(f"  {'':20} {spec.get('question', '')}")
    return 0


def cmd_controversy(args) -> int:
    con = db.connect()
    try:
        res = search.controversy(con, args.name)
        if not res["found"]:
            print(f"Sujet inconnu : {args.name}")
            print("Disponibles : " + ", ".join(res["available"]))
            return 1
        print(f"### {res['label']}")
        print(f"Question : {res['question']}")
        print(f"Note intra-coranique : {res['framing']}")
        if res["context_hint"]:
            print(f"Lecture conseillée : {res['context_hint']}")
        print("\nRécurrence lexicale :")
        for r in res["recurrence"]:
            print(
                f"  [{r['kind']:6s}] {r['label']:<16} "
                f"occurrences={r['occurrences']:<5} versets={r['verses']}"
            )
        print("\nVersets clés :")
        for v in res["verses"]:
            if v["missing"]:
                print(f"  [{_ref(v['sura'], v['aya'])}] (introuvable)")
                continue
            print(f"\n  [{_ref(v['sura'], v['aya'])}] {v['text_uthmani']}")
            for t in v["translations"]:
                print(f"      {t['author']} : {t['text']}")
        return 0
    finally:
        con.close()


def cmd_concordance(args) -> int:
    con = db.connect()
    try:
        if args.by == "root":
            res = search.concordance(con, root=args.value)
        else:
            res = search.concordance(con, term=args.value)
        if not res.get("found"):
            print(f"Aucune concordance pour : {args.value}")
            return 1
        print(
            f"Concordance {res['kind']} {res['label']} [{res['detail']}] — "
            f"{res['occurrences']} occurrence(s) / {res['verses_count']} verset(s)\n"
        )
        for v in res["verses"]:
            print(f"[{_ref(v['sura'], v['aya'])}] {v['text_uthmani']}")
            for t in v["translations"]:
                print(f"    {t['author']} : {t['text']}")
        return 0
    finally:
        con.close()


def cmd_mirror(args) -> int:
    sura, aya = (int(x) for x in args.reference.split(":"))
    con = db.connect()
    try:
        base = search.get_verse(con, sura, aya)
        if base is None:
            print(f"Verset introuvable : {args.reference}")
            return 1
        print(f"Verset de référence [{_ref(sura, aya)}] {base['text_uthmani']}\n")
        mir = search.mirror_verses(con, sura, aya, limit=args.limit, min_shared=args.min_shared)
        print(f"Racines ({len(mir['roots_arabic'])}) : {' '.join(mir['roots_arabic'])}\n")
        print(f"{len(mir['matches'])} verset(s) en miroir :")
        for m in mir["matches"]:
            print(f"\n[{_ref(m['sura'], m['aya'])}] ({m['shared']} racines communes)")
            print(f"    {m['text_uthmani']}")
            for t in m["translations"]:
                print(f"    {t['author']} : {t['text']}")
        return 0
    finally:
        con.close()


def cmd_themes(args) -> int:
    grouped = search.themes_by_category()
    total = sum(len(v) for v in grouped.values())
    print(f"{total} thème(s) répartis en {len(grouped)} catégorie(s) :\n")
    for category, items in grouped.items():
        print(f"### {category}  ({len(items)})")
        for key, spec in items:
            roots = " ".join(spec.get("roots", []))
            print(f"  {key:<16} {spec['label']}")
            print(f"  {'':16} racines: {roots}")
        print()
    return 0


def cmd_bridge(args) -> int:
    con = db.connect()
    try:
        props = search.french_bridge(con, args.query)["proposals"]
        if not props:
            print(f"Aucune correspondance trouvée pour « {args.query} ».")
            return 1
        print(
            f"{len(props)} proposition(s) pour « {args.query} » — "
            "français → racine arabe :\n"
        )
        for p in props:
            print(f"  {p['root_ar']} [{p['root_bw']}]  —  {p['fr']}")
            print(
                f"      {p['verses']} versets · {p['occurrences']} occurrences"
                f" · source : {p['source']}"
            )
            if p.get("detail"):
                print(f"      {p['detail']}")
        print("\nDétail : python -m quranlab root <racine>")
        return 0
    finally:
        con.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="quranlab",
        description="Recherche et analyse intra-coranique (texte, racines, traductions).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Télécharge les sources et construit la base")
    p_init.add_argument("--force", action="store_true", help="Retélécharger les sources")
    p_init.set_defaults(func=cmd_init)

    p_s = sub.add_parser("search", help="Recherche textuelle (arabe ou français)")
    p_s.add_argument("query")
    p_s.add_argument("--lang", choices=["ar", "fr"], default="ar")
    p_s.add_argument("--translation", default=None, help="clé de traduction (ex: fr.hamidullah)")
    p_s.add_argument("--limit", type=int, default=50)
    p_s.set_defaults(func=cmd_search)

    p_b = sub.add_parser("bridge", help="Passerelle français → arabe (racines)")
    p_b.add_argument("query")
    p_b.set_defaults(func=cmd_bridge)

    p_r = sub.add_parser("root", help="Occurrences d'une racine (arabe ou Buckwalter)")
    p_r.add_argument("root")
    p_r.add_argument("--limit", type=int, default=500)
    p_r.add_argument("--context", type=int, default=0, help="versets de contexte")
    p_r.set_defaults(func=cmd_root)

    p_v = sub.add_parser("verse", help="Affiche un verset et ses traductions (sura:aya)")
    p_v.add_argument("reference")
    p_v.set_defaults(func=cmd_verse)

    p_t = sub.add_parser("theme", help="Cartographie thématique intra-coranique")
    p_t.add_argument("name")
    p_t.add_argument("--limit", type=int, default=500)
    p_t.set_defaults(func=cmd_theme)

    p_tl = sub.add_parser("themes", help="Liste les thèmes prédéfinis")
    p_tl.set_defaults(func=cmd_themes)

    p_cv = sub.add_parser("controversy", help="Analyse textuelle d'un sujet (idées reçues)")
    p_cv.add_argument("name")
    p_cv.set_defaults(func=cmd_controversy)

    p_cvs = sub.add_parser("controversies", help="Liste les sujets d'analyse textuelle")
    p_cvs.set_defaults(func=cmd_controversies)

    p_cc = sub.add_parser("concordance", help="Concordance d'une notion (racine/terme)")
    p_cc.add_argument("value")
    p_cc.add_argument("--by", choices=["root", "term"], default="root")
    p_cc.set_defaults(func=cmd_concordance)

    p_mi = sub.add_parser("mirror", help="Versets en miroir d'un verset (sura:aya)")
    p_mi.add_argument("reference")
    p_mi.add_argument("--limit", type=int, default=12)
    p_mi.add_argument("--min-shared", type=int, default=2)
    p_mi.set_defaults(func=cmd_mirror)

    return p


def main(argv=None) -> int:
    _fix_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
