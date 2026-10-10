"""Régression statique : tout widget Streamlit interactif porte une ``key=``.

Streamlit 1.58 dérive l'identifiant automatique d'un widget de son **type +
label/help** (pas de sa position). Deux widgets identiques dans un même run
(par ex. le même verset rendu dans l'onglet Lire *et* dans les Favoris)
provoquent alors ``StreamlitDuplicateElementKey``. En imposant une ``key=``
explicite (souvent via ``ui.unique_key`` pour les widgets répétés), on rend ce
colisage structurellement impossible.

Ce test analyse le code source (AST) et échoue si un widget interactif est
créé sans ``key=``. On ne contrôle que les appels réellement dirigés vers
Streamlit : ``st.<widget>(...)`` et ``<colonne>.<widget>(...)`` où ``<colonne>``
provient d'un ``st.columns(...)`` (les ``col.bookmark()``/``bookmarks.toggle()``
sur d'autres objets sont ignorés).
"""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [ROOT / "app.py", *sorted((ROOT / "quranlab").glob("*.py"))]

# Widgets qui produisent un identifiant d'élément (donc sensibles au colisage).
KEYED_WIDGETS = {
    "button",
    "form_submit_button",
    "download_button",
    "link_button",
    "checkbox",
    "toggle",
    "radio",
    "selectbox",
    "multiselect",
    "pills",
    "segmented_control",
    "text_input",
    "text_area",
    "number_input",
    "slider",
    "select_slider",
    "color_picker",
    "date_input",
    "time_input",
    "file_uploader",
    "camera_input",
    "chat_input",
}


def _is_columns_call(node: ast.AST) -> bool:
    """``st.columns(...)`` (ou ``x.columns(...)``) ?"""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "columns"
    )


def _column_names(tree: ast.AST) -> set:
    """Noms de variables liés à ``st.columns(...)`` dans un arbre."""
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not _is_columns_call(node.value):
            continue
        for tgt in node.targets:
            for elt in ast.walk(tgt):
                if isinstance(elt, ast.Name):
                    names.add(elt.id)
    return names


def _owner_is_streamlit(value: ast.AST, cols: set) -> bool:
    """La cible de l'appel est-elle ``st`` ou une colonne ``st.columns`` ?"""
    if isinstance(value, ast.Name):
        return value.id == "st" or value.id in cols
    if isinstance(value, ast.Subscript) and isinstance(value.value, ast.Name):
        return value.value.id in cols
    return False


def _has_key(node: ast.Call) -> bool:
    for kw in node.keywords:
        if kw.arg == "key":
            return True
        if kw.arg is None:  # **kwargs : on ne peut pas vérifier -> on tolère
            return True
    return False


class TestWidgetKeys(unittest.TestCase):
    def test_all_interactive_widgets_have_explicit_key(self):
        offenders = []
        for path in TARGETS:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            cols = _column_names(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if not isinstance(func, ast.Attribute):
                    continue
                if func.attr not in KEYED_WIDGETS:
                    continue
                if not _owner_is_streamlit(func.value, cols):
                    continue
                if not _has_key(node):
                    offenders.append(f"{path.name}:{node.lineno} -> {func.attr}()")
        self.assertEqual(
            offenders,
            [],
            "Widgets Streamlit sans key= explicite (risque de "
            "StreamlitDuplicateElementKey) :\n  " + "\n  ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
