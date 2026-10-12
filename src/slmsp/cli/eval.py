"""Sous-commande `slmsp eval` : gel du Jeu d'évaluation ; `run` et `sonde-outils` à venir.

    slmsp eval gel --version v1.0 --verifier-seulement [--racine DIR]
    slmsp eval gel --version v1.0 --statut provisoire --graine 7 [--racine DIR]

`--verifier-seulement` n'écrit rien et sort en 0 sans erreur bloquante (les écarts de
composition sont listés). Le gel écrit `eval/jeu/<version>/MANIFEST.json` et
`eval/revue/echantillon-revue-<version>.md`, et refuse si l'un des deux existe.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from pathlib import Path

from slmsp.core.erreurs import CodeSortie


def _non_implementee(nom: str) -> Callable[[argparse.Namespace], int]:
    def executer(_args: argparse.Namespace) -> int:
        print(f"slmsp : commande non implémentée : eval {nom}", file=sys.stderr)
        return int(CodeSortie.USAGE)

    return executer


def _aide(parseur: argparse.ArgumentParser) -> Callable[[argparse.Namespace], int]:
    def executer(_args: argparse.Namespace) -> int:
        parseur.print_help(sys.stderr)
        return int(CodeSortie.USAGE)

    return executer


def _usage(message: str) -> int:
    print(f"slmsp : eval gel : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def executer_gel(args: argparse.Namespace) -> int:
    """`slmsp eval gel` : vérification seule, ou gel complet."""
    from slmsp.core.items import MOTIF_VERSION
    from slmsp.evaluation.gel import JeuNonConforme, gel, verifier_jeu

    if not re.fullmatch(MOTIF_VERSION, args.version):
        return _usage(f"version de jeu invalide : {args.version!r} (attendu : vN ou vN.M)")
    racine = Path(args.racine) if args.racine is not None else None
    if args.verifier_seulement:
        if args.statut is not None or args.graine is not None:
            return _usage("--verifier-seulement exclut --statut et --graine")
        rapport = verifier_jeu(args.version, racine)
        print(rapport.texte())
        if rapport.erreurs:
            raise JeuNonConforme(
                f"jeu {args.version} non conforme : {len(rapport.erreurs)} erreur(s) bloquante(s)",
                rapport.erreurs,
            )
        return int(CodeSortie.SUCCES)
    if args.statut is None or args.graine is None:
        return _usage("--statut et --graine sont requis (ou --verifier-seulement)")
    manifeste = gel(args.version, args.statut, args.graine, racine)
    print(f"Jeu {manifeste.version} gelé ({manifeste.statut}) : {manifeste.nb_items} items.")
    print(f"Fichiers empreints : {len(manifeste.fichiers)}.")
    print(
        f"Échantillons (graine {manifeste.echantillons.graine}) : second juge "
        f"{len(manifeste.echantillons.second_juge)}, relecture "
        f"{len(manifeste.echantillons.relecture)}."
    )
    print(f"Écarts de composition inscrits : {len(manifeste.ecarts)}.")
    for ecart in manifeste.ecarts:
        print(f"- {ecart}")
    print(
        f"Écrits : eval/jeu/{manifeste.version}/MANIFEST.json et "
        f"eval/revue/echantillon-revue-{manifeste.version}.md (à commiter)."
    )
    return int(CodeSortie.SUCCES)


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `eval` et ses sous-commandes au parseur de `slmsp`."""
    parseur = sous_parseurs.add_parser(
        "eval",
        help="Jeu d'évaluation : gel, génération et notation",
        description="Jeu d'évaluation : gel, génération et notation.",
    )
    actions = parseur.add_subparsers(dest="eval_commande", metavar="<action>")
    parseur.set_defaults(func=_aide(parseur))

    gel = actions.add_parser(
        "gel",
        help="vérifier et geler une version du Jeu d'évaluation",
        description="Vérifie le jeu (items, cassettes, composition) et le gèle par manifeste.",
    )
    gel.add_argument("--version", required=True, help="version du jeu (vN ou vN.M)")
    gel.add_argument(
        "--verifier-seulement",
        action="store_true",
        help="vérifier sans rien écrire (code 0 sans erreur bloquante)",
    )
    gel.add_argument("--statut", choices=("provisoire", "relu"), help="statut du gel")
    gel.add_argument("--graine", type=int, help="graine des échantillons (second juge, relecture)")
    gel.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    gel.set_defaults(func=executer_gel)

    for nom, aide in (
        ("run", "évaluer un modèle sur le Jeu d'évaluation (non implémentée)"),
        ("sonde-outils", "sonder les outils MCP (non implémentée)"),
    ):
        action = actions.add_parser(nom, help=aide, description=aide, add_help=False)
        action.set_defaults(_remplacement=True, func=_non_implementee(nom))
