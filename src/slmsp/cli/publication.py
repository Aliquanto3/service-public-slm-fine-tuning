"""Sous-commande `slmsp publication preparer` : dossier de publication hors ligne (story 13.7).

    slmsp publication preparer --modele SLUG --export RUN_ID --comparatif CHEMIN
        --sortie DOSSIER [--quantification q4_k_m|f16] [--racine DOSSIER]

Aucune sous-commande d'envoi : Anaël téléverse lui-même (docs/procedure-publication.md).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie, SlmspError


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    parseur = sous_parseurs.add_parser(
        "publication",
        help="dossier de publication",
        description="Prépare et vérifie hors ligne un dossier de publication ; n'envoie rien.",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)
    p = actions.add_parser("preparer", help="assembler le dossier de publication d'un modèle")
    p.add_argument("--modele", required=True, help="slug du Modèle de base (config/modeles)")
    p.add_argument("--export", required=True, help="identifiant du run d'export complet")
    p.add_argument("--comparatif", required=True, type=Path, help="comparatif.md à joindre")
    p.add_argument("--sortie", required=True, type=Path, help="dossier à créer (vide ou absent)")
    p.add_argument("--quantification", choices=("q4_k_m", "f16"), default="q4_k_m")
    p.add_argument("--racine", type=Path, default=None, help="racine de config/, data/ et runs/")
    p.set_defaults(func=_preparer)


def _preparer(args: argparse.Namespace) -> int:
    from slmsp.publication.preparer import preparer

    racine = (args.racine if args.racine is not None else racine_projet()).resolve()
    try:
        rapport = preparer(
            racine=racine,
            modele=args.modele,
            export_run=args.export,
            comparatif=args.comparatif,
            sortie=args.sortie,
            quantification=args.quantification,
        )
    except SlmspError as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    if not rapport.publiable:
        for constat in rapport.bloquants:
            print(f"slmsp : refusé : {constat}", file=sys.stderr)
        print(f"slmsp : dossier non publiable, conservé sous {rapport.dossier}", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    print(f"publication : dossier prêt : {rapport.dossier} (licence {rapport.licence})")
    for emplacement in rapport.emplacements:
        print(f"publication : à compléter avant téléversement : {emplacement}")
    print("publication : téléversement manuel, voir docs/procedure-publication.md")
    return int(CodeSortie.SUCCES)
