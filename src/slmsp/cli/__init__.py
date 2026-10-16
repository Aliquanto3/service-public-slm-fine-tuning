"""Point d'entrée de la commande `slmsp` et registre des sous-commandes.

Chaque sous-commande vit dans son propre module `slmsp.cli.<nom>`, qui expose
`enregistrer(sous_parseurs)` : la fonction ajoute son sous-parseur par
`sous_parseurs.add_parser(nom, ...)` et y fixe `func(args) -> int` par `set_defaults`.

Seul le module de la sous-commande appelée est chargé, par `importlib`, sans modifier
ce fichier : `slmsp --help` n'importe aucun module de sous-commande. Un module absent
répond « commande non implémentée » (code 2) ; un module dont une dépendance manque
(extra uv non installé) répond « commande indisponible » (code 1), sans trace technique.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable, Iterable, Sequence

from slmsp.core.config import appliquer_environnement_impose
from slmsp.core.erreurs import CodeSortie, SlmspError

# `CodeSortie` vit dans `slmsp.core.erreurs` et reste importable depuis `slmsp.cli`.
__all__ = ["SOUS_COMMANDES", "CodeSortie", "construire_parseur", "main"]


SOUS_COMMANDES: dict[str, str] = {
    "fetch": "télécharger modèles, llama.cpp, benchmarks et sources",
    "index": "construire et vérifier l'Index local",
    "ask": "interroger l'Assistant",
    "mcp": "client MCP en direct et enregistrement de cassettes",
    "eval": "Jeu d'évaluation : gel, génération et notation",
    "bench": "Benchmarks standardisés",
    "measure": "mesures techniques",
    "data": "pipeline des Données d'entraînement",
    "train": "runs d'entraînement",
    "export": "export GGUF des adaptateurs",
    "compare": "Comparatif des runs",
    "budget": "relevé du registre de budget",
    "publication": "dossier de publication hors ligne",
}
"""Sous-commandes déclarées d'avance (D-nuit-A2-6) : nom -> aide courte."""


def _sortie_utf8() -> None:
    for flux in (sys.stdout, sys.stderr):
        reconfigurer = getattr(flux, "reconfigure", None)
        if reconfigurer is not None:
            # Conserver la politique d'erreurs (backslashreplace pour stderr).
            reconfigurer(encoding="utf-8", errors=getattr(flux, "errors", None) or "strict")


def _echec(message: str, code: CodeSortie) -> Callable[[argparse.Namespace], int]:
    def executer(_args: argparse.Namespace) -> int:
        print(f"slmsp : {message}", file=sys.stderr)
        return code

    return executer


def _remplacement(
    sous_parseurs: argparse._SubParsersAction,
    nom: str,
    aide: str,
    func: Callable[[argparse.Namespace], int] | None,
) -> None:
    # Sans argument ni `--help` : tout ce qui suit la sous-commande est toléré (voir main).
    parseur = sous_parseurs.add_parser(nom, help=aide, description=aide, add_help=False)
    parseur.set_defaults(_remplacement=True)
    if func is not None:
        parseur.set_defaults(func=func)


def _enregistrer(sous_parseurs: argparse._SubParsersAction, nom: str, aide: str) -> None:
    nom_module = f"{__name__}.{nom}"
    try:
        module = importlib.import_module(nom_module)
    except (ImportError, OSError) as exc:
        # OSError : DLL introuvable sous Windows (torch CUDA mal installé, par exemple).
        if isinstance(exc, ModuleNotFoundError) and exc.name == nom_module:
            func = _echec(f"commande non implémentée : {nom}", CodeSortie.USAGE)
        else:
            if isinstance(exc, ModuleNotFoundError) and exc.name:
                cause = f"module manquant : {exc.name}"
            else:
                cause = f"{type(exc).__name__} : {exc}"
            func = _echec(
                f"commande indisponible : {nom} ({cause}) ; vérifier l'extra uv correspondant",
                CodeSortie.ERREUR,
            )
        _remplacement(sous_parseurs, nom, aide, func)
        return
    module.enregistrer(sous_parseurs)


def construire_parseur(charger: Iterable[str] = ()) -> argparse.ArgumentParser:
    """Construit le parseur de `slmsp`.

    Les sous-commandes nommées dans `charger` reçoivent leur sous-parseur réel (ou un
    remplacement « non implémentée » / « indisponible ») ; les autres n'apparaissent que
    dans l'aide.
    """
    a_charger = set(charger)
    parseur = argparse.ArgumentParser(
        prog="slmsp",
        description="Assistant IA local du secteur public et outillage associé.",
    )
    sous_parseurs = parseur.add_subparsers(
        dest="commande", metavar="<commande>", title="sous-commandes"
    )
    for nom, aide in SOUS_COMMANDES.items():
        if nom in a_charger:
            _enregistrer(sous_parseurs, nom, aide)
        else:
            _remplacement(sous_parseurs, nom, aide, None)
    return parseur


def _code_de_sortie(exc: SystemExit) -> int:
    if exc.code is None:
        return CodeSortie.SUCCES
    if isinstance(exc.code, int):
        return exc.code
    return CodeSortie.ERREUR


def _signaler(exc: SlmspError) -> int:
    # Message seul, sans trace technique (convention « Erreurs ») ; préfixe sur chaque ligne.
    for ligne in (str(exc) or type(exc).__name__).splitlines():
        print(f"slmsp : {ligne}", file=sys.stderr)
    return int(exc.code_sortie)


def main(argv: Sequence[str] | None = None) -> int:
    """Exécute `slmsp` et renvoie le code de sortie."""
    _sortie_utf8()
    appliquer_environnement_impose()
    arguments = list(sys.argv[1:] if argv is None else argv)
    charger = arguments[:1] if arguments and arguments[0] in SOUS_COMMANDES else []
    try:
        parseur = construire_parseur(charger)
    except SlmspError as exc:
        return _signaler(exc)
    try:
        args, inconnus = parseur.parse_known_args(arguments)
        if inconnus and not getattr(args, "_remplacement", False):
            parseur.error(f"arguments non reconnus : {' '.join(inconnus)}")
    except SystemExit as exc:
        return _code_de_sortie(exc)
    func = getattr(args, "func", None)
    if func is None:
        parseur.print_help(sys.stderr)
        return int(CodeSortie.USAGE)
    try:
        code = func(args)
    except SlmspError as exc:
        return _signaler(exc)
    return int(CodeSortie.SUCCES if code is None else code)
