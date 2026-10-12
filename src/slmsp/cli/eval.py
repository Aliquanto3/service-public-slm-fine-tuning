"""Sous-commande `slmsp eval` : gel du Jeu d'évaluation, phase génération ; `sonde-outils` à venir.

    slmsp eval gel --version v1.0 --verifier-seulement [--racine DIR]
    slmsp eval gel --version v1.0 --statut provisoire --graine 7 [--racine DIR]
    slmsp eval run --modele base:granite-4.0-1b --quantification q4_k_m --jeu v1.0
        --phase generation [--variante cpu|cuda] [--items ID,ID…] [--racine DIR]
    slmsp eval run --phase generation --reprendre RUN_ID [--racine DIR]

`--verifier-seulement` n'écrit rien et sort en 0 sans erreur bloquante (les écarts de
composition sont listés). Le gel écrit `eval/jeu/<version>/MANIFEST.json` et
`eval/revue/echantillon-revue-<version>.md`, et refuse si l'un des deux existe.

`run` : seule la phase `generation` existe (story 5.3) ; `--phase` vaut `toutes` par
défaut, et `notation` comme `toutes` sont refusées (code 2) jusqu'à la story 5.6. Une
ligne de progression par item, puis le chemin du run, son statut et la durée moyenne par
item. Code 0 si le run est `complet`, 1 s'il est `partiel-erreur`, 2 pour une erreur
d'usage, 4 si le jeu est altéré ou si le run repris diffère de la demande.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final

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


PHASES: Final = ("generation", "notation", "toutes")


def _usage_run(message: str) -> int:
    print(f"slmsp : eval run : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def _items(valeur: str | None) -> list[str] | None:
    if valeur is None:
        return None
    return [identifiant.strip() for identifiant in valeur.split(",") if identifiant.strip()]


def _rapporter(generation: Any, rang: int, total: int) -> None:
    print(
        f"[{rang}/{total}] {generation.item_id} {generation.statut} ({generation.duree_ms} ms)",
        flush=True,
    )


def executer_run(args: argparse.Namespace) -> int:
    """`slmsp eval run` : phase génération (lancement ou reprise)."""
    from slmsp.evaluation import assemblage
    from slmsp.evaluation.generation import lancer_generation, reprendre_generation

    if args.phase != "generation":
        print(
            f"slmsp : commande non implémentée : eval run --phase {args.phase} : phase "
            "non implémentée (story 5.6) ; utiliser --phase generation",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    racine = Path(args.racine) if args.racine is not None else None
    try:
        if args.reprendre is not None:
            if args.items is not None:
                return _usage_run("--items est fixé par le run repris")
            rapport = reprendre_generation(
                args.reprendre,
                racine=racine,
                fabrique=assemblage.ouvrir_harnais,
                rapporter=_rapporter,
                modele_ref=args.modele,
                quantification=args.quantification,
                jeu=args.jeu,
                variante=args.variante,
            )
        else:
            manquants = [
                option
                for option, valeur in (
                    ("--modele", args.modele),
                    ("--quantification", args.quantification),
                    ("--jeu", args.jeu),
                )
                if valeur is None
            ]
            if manquants:
                return _usage_run(f"{', '.join(manquants)} requis (ou --reprendre RUN_ID)")
            rapport = lancer_generation(
                args.modele,
                args.quantification,
                args.jeu,
                variante=args.variante or "cpu",
                items=_items(args.items),
                racine=racine,
                fabrique=assemblage.ouvrir_harnais,
                rapporter=_rapporter,
            )
    except ValueError as exc:
        return _usage_run(str(exc))
    moyenne = rapport.duree_moyenne_ms
    print(f"Run : {rapport.run.dossier}")
    print(
        f"Statut du run : {rapport.statut} (cette session : {rapport.ok} ok, "
        f"{rapport.erreur} en erreur, {rapport.sautes} déjà présent(s))"
    )
    print(
        "Durée moyenne par item (cette session) : "
        + ("sans objet" if moyenne is None else f"{moyenne:.0f} ms")
    )
    return int(CodeSortie.SUCCES if rapport.statut == "complet" else CodeSortie.ERREUR)


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

    run = actions.add_parser(
        "run",
        help="évaluer un modèle sur le Jeu d'évaluation (phase génération)",
        description="Évalue un modèle sur le Jeu d'évaluation : phase génération, sans réseau.",
    )
    run.add_argument("--modele", help="modèle évalué : base:<slug> ou ft:<export_run_id>")
    run.add_argument("--quantification", choices=("f16", "q4_k_m"), help="quantification")
    run.add_argument("--jeu", help="version du jeu (vN, vN.M ou calibrage)")
    run.add_argument("--variante", choices=("cpu", "cuda"), help="variante llama.cpp (cpu)")
    run.add_argument(
        "--phase",
        choices=PHASES,
        default="toutes",
        help="phase à exécuter (seule « generation » est implémentée)",
    )
    run.add_argument("--items", help="identifiants d'items séparés par des virgules")
    run.add_argument("--reprendre", metavar="RUN_ID", help="reprendre ce run en ajout seul")
    run.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    run.set_defaults(func=executer_run)

    aide = "sonder les outils MCP (non implémentée)"
    sonde = actions.add_parser("sonde-outils", help=aide, description=aide, add_help=False)
    sonde.set_defaults(_remplacement=True, func=_non_implementee("sonde-outils"))
