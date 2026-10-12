"""Sous-commande `slmsp eval` : gel du jeu, génération et notation ; `sonde-outils` à venir.

    slmsp eval gel --version v1.0 --verifier-seulement [--racine DIR]
    slmsp eval gel --version v1.0 --statut provisoire --graine 7 [--racine DIR]
    slmsp eval run --modele base:granite-4.0-1b --quantification q4_k_m --jeu v1.0
        [--phase generation|toutes] [--variante cpu|cuda] [--items ID,ID…] [--racine DIR]
        [--mode-juge batch|direct]
    slmsp eval run --phase generation --reprendre RUN_ID [--racine DIR]
    slmsp eval run --phase notation --depuis RUN_ID [--mode-juge batch|direct] [--racine DIR]

`--verifier-seulement` n'écrit rien et sort en 0 sans erreur bloquante (les écarts de
composition sont listés). Le gel écrit `eval/jeu/<version>/MANIFEST.json` et
`eval/revue/echantillon-revue-<version>.md`, et refuse si l'un des deux existe.

`run --phase generation` (story 5.3) : une ligne de progression par item, puis le chemin du
run, son statut et la durée moyenne par item. `run --phase notation --depuis RUN_ID`
(story 5.6) : note le run de génération `RUN_ID` (contrôles automatiques, Juge principal,
second juge sur l'échantillon, formules de la grille) dans un run `eval-notation`, puis
affiche le tableau des Scores de Tâche (« non relu » tant que la relecture n'est pas
validée). Pas de `--reprendre` pour la notation : la relancer suffit, le cache des verdicts
évite tout double paiement. `--mode-juge` surcharge le `mode_appel` de `juges.toml`.
`--phase toutes` (défaut) enchaîne la génération (ou sa reprise) et la notation du run
produit s'il est `complet` ou `partiel-erreur`.

Code 0 si le dernier run est `complet`, 1 s'il est `partiel-erreur` ou `partiel-budget`, 2
pour une erreur d'usage, 4 si le jeu est altéré ou si le run repris diffère de la demande.
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


def _manquants(args: argparse.Namespace) -> list[str]:
    return [
        option
        for option, valeur in (
            ("--modele", args.modele),
            ("--quantification", args.quantification),
            ("--jeu", args.jeu),
        )
        if valeur is None
    ]


def _generation(args: argparse.Namespace, racine: Path | None) -> Any:
    """Lance ou reprend la phase génération ; rend le rapport, ou un code d'usage (int)."""
    from slmsp.evaluation import assemblage
    from slmsp.evaluation.generation import lancer_generation, reprendre_generation

    try:
        if args.reprendre is not None:
            if args.items is not None:
                return _usage_run("--items est fixé par le run repris")
            return reprendre_generation(
                args.reprendre,
                racine=racine,
                fabrique=assemblage.ouvrir_harnais,
                rapporter=_rapporter,
                modele_ref=args.modele,
                quantification=args.quantification,
                jeu=args.jeu,
                variante=args.variante,
            )
        manquants = _manquants(args)
        if manquants:
            return _usage_run(f"{', '.join(manquants)} requis (ou --reprendre RUN_ID)")
        return lancer_generation(
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


def _afficher_generation(rapport: Any) -> None:
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


def _nombre(valeur: float | None, decimales: int) -> str:
    return "—" if valeur is None else f"{valeur:.{decimales}f}"


COLONNES: Final = (
    ("Tâche", 5),
    ("Score", 7),
    ("Notés", 5),
    ("Jugés", 5),
    ("Invalides", 9),
    ("Non jugés", 9),
    ("En erreur", 9),
    ("2nd juge", 8),
    ("Kappa", 6),
)


def tableau_scores(scores: Any) -> str:
    """Tableau texte des Scores de Tâche : score, effectifs, kappa et statuts."""
    lignes = ["  ".join(titre.ljust(largeur) for titre, largeur in COLONNES) + "  Statuts"]
    for code, score in scores.taches.items():
        effectifs = score.effectifs
        statuts = [score.statuts.jeu_statut]
        statuts.append("relu" if score.statuts.verdicts_relus else "non relu")
        if score.statuts.fragile:
            statuts.append("fragile")
        if score.statuts.plafonne_lc:
            statuts.append("plafonné LC")
        valeurs = (
            code,
            _nombre(score.score, 1),
            effectifs.notes,
            effectifs.juges,
            effectifs.invalides,
            effectifs.non_juges,
            effectifs.en_erreur,
            effectifs.second_juge,
            _nombre(score.kappa.valeur, 2),
        )
        cellules = [
            str(valeur).ljust(largeur)
            for valeur, (_, largeur) in zip(valeurs, COLONNES, strict=True)
        ]
        lignes.append("  ".join(cellules) + "  " + ", ".join(statuts))
    return "\n".join(lignes)


def _afficher_notation(rapport: Any) -> None:
    scores = rapport.scores
    print(f"Run de notation : {rapport.run.dossier}")
    print(
        f"Statut du run : {rapport.statut} (Juge principal : {rapport.demandes_principal} "
        f"demande(s), second juge : {rapport.demandes_second}, {rapport.depuis_cache} depuis le "
        f"cache ; coût de cette session {rapport.cout_session_eur:.4f} €)"
    )
    print(
        f"Scores de Tâche (jeu {scores.jeu_version}, {scores.jeu_statut}) ; coût cumulé du Juge "
        f"{scores.cout_juge_total_eur:.4f} € :"
    )
    print(tableau_scores(scores))


def _code(statut: str) -> int:
    return int(CodeSortie.SUCCES if statut == "complet" else CodeSortie.ERREUR)


def _rapporter_notation(message: str) -> None:
    print(message, flush=True)


def _phase_notation(args: argparse.Namespace, racine: Path | None) -> int:
    from slmsp.evaluation import notation

    if args.depuis is None:
        return _usage_run("--depuis RUN_ID requis pour --phase notation")
    if args.reprendre is not None:
        return _usage_run(
            "pas de --reprendre pour la notation : la relancer suffit (cache des verdicts)"
        )
    inutiles = [
        option
        for option, valeur in (
            ("--modele", args.modele),
            ("--quantification", args.quantification),
            ("--jeu", args.jeu),
            ("--variante", args.variante),
            ("--items", args.items),
        )
        if valeur is not None
    ]
    if inutiles:
        return _usage_run(f"{', '.join(inutiles)} sans objet pour --phase notation")
    try:
        juges = notation.ouvrir_juges(racine, args.mode_juge)
    except ValueError as exc:
        return _usage_run(str(exc))
    rapport = notation.noter(args.depuis, juges=juges, racine=racine, rapporter=_rapporter_notation)
    _afficher_notation(rapport)
    return _code(rapport.statut)


def executer_run(args: argparse.Namespace) -> int:
    """`slmsp eval run` : génération (lancement ou reprise), notation, ou les deux."""
    from slmsp.evaluation import notation

    racine = Path(args.racine) if args.racine is not None else None
    if args.phase == "notation":
        return _phase_notation(args, racine)
    if args.depuis is not None:
        return _usage_run("--depuis ne vaut que pour --phase notation")
    juges = None
    if args.phase == "toutes":
        manquants = _manquants(args) if args.reprendre is None else []
        if manquants:
            return _usage_run(f"{', '.join(manquants)} requis (ou --reprendre RUN_ID)")
        try:
            juges = notation.ouvrir_juges(racine, args.mode_juge)  # avant toute génération
        except ValueError as exc:
            return _usage_run(str(exc))
    elif args.mode_juge is not None:
        return _usage_run("--mode-juge sans objet pour --phase generation")
    rapport = _generation(args, racine)
    if isinstance(rapport, int):
        return rapport
    _afficher_generation(rapport)
    if juges is None:
        return _code(rapport.statut)
    if rapport.statut not in notation.STATUTS_PARENT:
        print(f"Notation non lancée : génération au statut {rapport.statut}.", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    resultat = notation.noter(
        rapport.run.run_id, juges=juges, racine=racine, rapporter=_rapporter_notation
    )
    _afficher_notation(resultat)
    return _code(resultat.statut)


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
        help="évaluer un modèle sur le Jeu d'évaluation (génération, notation)",
        description=(
            "Évalue un modèle sur le Jeu d'évaluation : génération sans réseau, puis notation "
            "(contrôles automatiques, juges, Scores de Tâche)."
        ),
    )
    run.add_argument("--modele", help="modèle évalué : base:<slug> ou ft:<export_run_id>")
    run.add_argument("--quantification", choices=("f16", "q4_k_m"), help="quantification")
    run.add_argument("--jeu", help="version du jeu (vN, vN.M ou calibrage)")
    run.add_argument("--variante", choices=("cpu", "cuda"), help="variante llama.cpp (cpu)")
    run.add_argument(
        "--phase",
        choices=PHASES,
        default="toutes",
        help="phase à exécuter (défaut : toutes = génération puis notation)",
    )
    run.add_argument("--items", help="identifiants d'items séparés par des virgules")
    run.add_argument("--reprendre", metavar="RUN_ID", help="reprendre ce run en ajout seul")
    run.add_argument(
        "--depuis", metavar="RUN_ID", help="run de génération à noter (--phase notation)"
    )
    run.add_argument(
        "--mode-juge",
        choices=("batch", "direct"),
        help="mode d'appel du Juge principal (défaut : celui de juges.toml)",
    )
    run.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    run.set_defaults(func=executer_run)

    aide = "sonder les outils MCP (non implémentée)"
    sonde = actions.add_parser("sonde-outils", help=aide, description=aide, add_help=False)
    sonde.set_defaults(_remplacement=True, func=_non_implementee("sonde-outils"))
