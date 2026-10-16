"""Vérificateur BFCL, exécuté dans l'environnement isolé `envs/bfcl` (story 6.3).

Usage : `python verifier.py <sorties.json> <verdicts.json>`.

Entrée : `{"categories": {<cat>: [{"id", "appels": [{<fonction>: {<arguments>}}], "fonctions",
"reponse"}]}}`. Sortie : `{"bfcl_eval_version", "categories": {<cat>: {"n_items",
"n_corrects", "precision", "erreurs": {<id>: <motif>}}}}`.

- `irrelevance` : correct si le modèle n'émet aucun appel (aucun import de `bfcl_eval`).
- `simple`, `multiple` : `ast_checker` de bfcl-eval, importé à la demande.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from typing import Any

Controle = Callable[[dict[str, Any], str], tuple[bool, str | None]]


class ErreurEnvironnement(RuntimeError):
    """Import ou signature de bfcl-eval en défaut : le vérificateur échoue, pas l'item."""


def controle_ast(item: dict[str, Any], categorie: str) -> tuple[bool, str | None]:
    """Contrôle AST de bfcl-eval d'une réponse (signature à confirmer au premier run réel)."""
    import inspect

    try:
        from bfcl_eval.constants.enums import Language
        from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker

        inspect.signature(ast_checker).bind(
            item["fonctions"], item["appels"], item["reponse"], Language.PYTHON, categorie, "slmsp"
        )
    except (ImportError, AttributeError, TypeError) as exc:
        raise ErreurEnvironnement(f"bfcl-eval inutilisable : {type(exc).__name__} : {exc}") from exc
    verdict = ast_checker(
        item["fonctions"],
        item["appels"],
        item["reponse"],
        Language.PYTHON,
        categorie,
        "slmsp",
    )
    erreurs = verdict.get("error") or []
    return bool(verdict.get("valid")), "; ".join(map(str, erreurs)) or None


def verifier_item(
    item: dict[str, Any], categorie: str, controle: Controle = controle_ast
) -> tuple[bool, str | None]:
    """Verdict d'un item ; un contrôle qui lève une erreur propre à l'item est un échec ;
    une réponse attendue absente ou un défaut d'environnement fait échouer le vérificateur."""
    if categorie == "irrelevance":
        return (
            (True, None) if not item["appels"] else (False, "appel émis sans fonction pertinente")
        )
    if not item["appels"]:
        return False, "aucun appel émis"
    if item.get("reponse") is None:
        raise ErreurEnvironnement(f"réponse attendue absente du jeu (item {item['id']})")
    try:
        return controle(item, categorie)
    except ErreurEnvironnement:
        raise
    except Exception as exc:
        return False, f"contrôle AST en échec : {type(exc).__name__} : {exc}"


def verifier(donnees: dict[str, Any], controle: Controle = controle_ast) -> dict[str, Any]:
    """Bilan par catégorie (précision = items corrects / items)."""
    categories: dict[str, Any] = {}
    for categorie, items in donnees["categories"].items():
        corrects, erreurs = 0, {}
        for item in items:
            ok, motif = verifier_item(item, categorie, controle)
            corrects += ok
            if not ok:
                erreurs[item["id"]] = motif
        total = len(items)
        categories[categorie] = {
            "n_items": total,
            "n_corrects": corrects,
            "precision": corrects / total if total else None,
            "erreurs": erreurs,
        }
    try:
        version = metadata.version("bfcl-eval")
    except metadata.PackageNotFoundError:
        version = None
    return {"bfcl_eval_version": version, "categories": categories}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage : verifier.py <sorties.json> <verdicts.json>", file=sys.stderr)
        return 2
    donnees = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(argv[2]).write_text(
        json.dumps(verifier(donnees), ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
