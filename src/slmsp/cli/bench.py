"""`slmsp bench {liste, run}` : benchmarks standardisés déclarés par `config/benchmarks/*.toml`.

`bench liste` affiche les benchmarks configurés. `bench run --modele base:<slug>` lance le
socle (`--socle`) ou une liste (`--benchmarks a,b`), filtrés par `--cible` et
`--quantification`. Code de sortie 1 si au moins un benchmark est en erreur.
"""

from __future__ import annotations

import argparse
import sys

from slmsp.benchmarks import config as config_bench
from slmsp.benchmarks import orchestrateur
from slmsp.benchmarks.moteurs import moteur_connu
from slmsp.core.erreurs import CodeSortie


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `bench` et ses actions."""
    parseur = sous_parseurs.add_parser(
        "bench",
        help="Benchmarks standardisés",
        description="Benchmarks standardisés décrits par config/benchmarks/*.toml.",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)

    p = actions.add_parser("liste", help="benchmarks configurés")
    p.set_defaults(func=_liste)

    p = actions.add_parser("run", help="lancer des benchmarks sur un modèle")
    p.add_argument("--modele", required=True, help="base:<slug> ou ft:<run_id>")
    choix = p.add_mutually_exclusive_group(required=True)
    choix.add_argument("--socle", action="store_true", help="les benchmarks du socle")
    choix.add_argument("--benchmarks", metavar="A,B", help="noms séparés par des virgules")
    p.add_argument("--cible", choices=["hf", "gguf"], help="ne lancer que cette cible")
    p.add_argument(
        "--quantification",
        choices=["avant", "apres", "les-deux"],
        help="ne lancer que ces variantes (défaut : celles de chaque benchmark)",
    )
    p.add_argument(
        "--variante-llamacpp",
        choices=["cpu", "cuda"],
        default="cpu",
        help="variante de llama-server pour les GGUF (cuda : verrou GPU)",
    )
    p.add_argument(
        "--parallele",
        type=_entier_positif,
        default=1,
        metavar="N",
        help="requêtes simultanées pour les GGUF (llama-server --parallel N ; défaut 1)",
    )
    p.add_argument("--racine", default=None, help="racine des écritures runs/ et data/")
    p.set_defaults(func=_run)


def _entier_positif(valeur: str) -> int:
    try:
        n = int(valeur)
    except ValueError:
        n = 0
    if n < 1:
        raise argparse.ArgumentTypeError(f"entier >= 1 attendu : {valeur!r}")
    return n


def _liste(_args: argparse.Namespace) -> int:
    configs = config_bench.charger_benchmarks()
    print(
        f"{'benchmark':<22}{'moteur':<12}{'cible':<7}{'quantification':<16}"
        f"{'few-shot':<10}{'limite':<8}socle"
    )
    for c in configs.values():
        limite = "-" if c.limite is None else str(c.limite)
        inconnu = "" if moteur_connu(c.moteur) else "  (moteur inconnu)"
        print(
            f"{c.nom:<22}{c.moteur:<12}{c.cible:<7}{c.quantification:<16}"
            f"{c.fewshot:<10}{limite:<8}{'oui' if c.socle else 'non'}{inconnu}"
        )
    return int(CodeSortie.SUCCES)


def _run(args: argparse.Namespace) -> int:
    from slmsp.core.config import racine_projet

    configs = config_bench.charger_benchmarks()
    noms = [n.strip() for n in args.benchmarks.split(",") if n.strip()] if args.benchmarks else []
    selection = orchestrateur.selectionner(
        configs,
        socle=args.socle,
        noms=noms,
        cible=args.cible,
        quantification=args.quantification,
    )
    racine = args.racine if args.racine is not None else racine_projet()
    rapport = orchestrateur.lancer(
        args.modele,
        selection,
        racine=racine,
        variante_llamacpp=args.variante_llamacpp,
        parallele=args.parallele,
        affichage=lambda ligne: print(ligne, flush=True),
    )
    print(f"bench run : {rapport.statut} ; run {rapport.run.run_id} : {rapport.run.dossier}")
    if rapport.statut != "complet":
        print("slmsp : au moins un benchmark est en erreur", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)
