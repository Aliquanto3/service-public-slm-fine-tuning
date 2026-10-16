"""Sous-commande `slmsp compare comparatif` : rapport Comparatif (epic 11, FR-36).

    slmsp compare comparatif --campagne <id> [--racine DOSSIER] [--jeu VERSION]

Lit les artefacts de `<racine>/runs/` (jamais de modèle ni de réseau) et écrit
`runs/compare/<run_id>/comparatif.md`. Plusieurs versions du jeu parmi les notations :
code 2, sauf si `--jeu` en choisit une.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie, SlmspError

TYPE_RUN = "compare"
NOM_RAPPORT = "comparatif.md"


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `compare` et son action `comparatif`."""
    parseur = sous_parseurs.add_parser(
        "compare",
        help="Comparatif des runs",
        description="Rapport Comparatif généré à partir des seuls artefacts archivés.",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)
    p = actions.add_parser("comparatif", help="rapport Comparatif d'une campagne")
    p.add_argument("--campagne", required=True, help="identifiant de la campagne d'entraînement")
    p.add_argument("--racine", type=Path, default=None, help="racine de config/ et runs/")
    p.add_argument("--jeu", default=None, help="version du jeu à retenir si plusieurs existent")
    p.set_defaults(func=_comparatif)


def _comparatif(args: argparse.Namespace) -> int:
    from slmsp.compare.chargement import JeuMelange, charger
    from slmsp.compare.comparatif import charger_config, rendre_comparatif
    from slmsp.core.artefacts import nouveau_run

    racine = (args.racine if args.racine is not None else racine_projet()).resolve()
    try:
        config = charger_config(racine)
        donnees = charger(racine, args.campagne, jeu=args.jeu)
    except JeuMelange as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    except SlmspError as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    rapport = rendre_comparatif(donnees, config)
    slug = (
        "".join(c if c.isalnum() else "-" for c in args.campagne.lower()).strip("-") or "campagne"
    )
    run = nouveau_run(
        TYPE_RUN,
        slug,
        {"campagne": args.campagne, "jeu": args.jeu},
        jeu_version=donnees.jeu_version,
        racine=racine,
    )
    chemin = run.ecrire(NOM_RAPPORT, rapport)
    run.terminer("complet")
    print(f"comparatif : {chemin}")
    return int(CodeSortie.SUCCES)
