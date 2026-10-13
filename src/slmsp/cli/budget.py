"""`slmsp budget etat [--json]` : relevé du registre de budget, en lecture seule (AD-5).

Le relevé lit `SLMSP_VAR_DIR/budget.sqlite` sans le créer ni le modifier, et sans
régulariser les réservations orphelines. Il affiche, par poste et sous-poste de la campagne
courante (`config/budgets.toml`), le plafond, le dépensé, le réservé et le reste, en euros,
puis les écarts éventuels entre ces plafonds et ceux inscrits au registre pour la campagne.
"""

from __future__ import annotations

import argparse

from slmsp.budget.registre import Releve, releve
from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import CodeSortie


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `budget` et son action `etat`."""
    parseur = sous_parseurs.add_parser(
        "budget",
        help="relevé du registre de budget",
        description="Registre de budget des API payantes (lecture seule).",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)
    p = actions.add_parser(
        "etat", help="plafond, dépensé, réservé et reste par poste (lecture seule)"
    )
    p.add_argument("--json", action="store_true", help="sortie JSON canonique")
    p.set_defaults(func=_etat)


def _texte(situation: Releve) -> str:
    lignes = [
        f"campagne {situation.campagne_id} (marge {situation.marge_eur:.2f} € par contrôle)",
        f"{'poste':<22}{'plafond':>10}{'dépensé':>12}{'réservé':>12}{'reste':>12}",
    ]
    for ligne in situation.lignes:
        nom = ligne.poste if ligne.sous_poste is None else f"  {ligne.poste}.{ligne.sous_poste}"
        lignes.append(
            f"{nom:<22}{ligne.plafond_eur:>10.2f}{ligne.depense_eur:>12.4f}"
            f"{ligne.reserve_eur:>12.4f}{ligne.reste_eur:>12.4f}"
        )
    lignes.append("montants en euros")
    if situation.ecarts:
        lignes.append("attention : plafonds différents de ceux inscrits au registre")
        lignes.extend(f"  {ecart}" for ecart in situation.ecarts)
    return "\n".join(lignes)


def _etat(args: argparse.Namespace) -> int:
    situation = releve()
    if args.json:
        print(json_canonique(situation.en_dict()).decode("utf-8"))
    else:
        print(_texte(situation))
    return int(CodeSortie.SUCCES)
