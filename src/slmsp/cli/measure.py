"""Sous-commande `slmsp measure run` : mesures techniques FR-26 (NFR-1 à NFR-3, NFR-6).

    slmsp measure run --modele base:<slug> [--quantification q4_k_m] [--racine DOSSIER]

Assemble l'Assistant complet comme `slmsp ask` (deux `llama-server` en variante `cpu`,
threads plafonnés par `config/mesures.toml`, Index local chargé), mesure des Questions avec
recherche dans l'Index et écrit `runs/measure/<run_id>/resultat.json`. Refuse
(`RessourceOccupee`, code 5) si une autre commande `slmsp` tient le verrou.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from slmsp.core.config import racine_ecriture, racine_projet
from slmsp.core.erreurs import CodeSortie


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `measure` et son action `run`."""
    parseur = sous_parseurs.add_parser(
        "measure",
        help="mesures techniques",
        description="Mesures techniques de l'Assistant complet (RAM, débit, latence, taille).",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)
    p = actions.add_parser("run", help="mesurer RAM, débit, premier token et taille installée")
    p.add_argument("--modele", required=True, help="modèle : base:<slug>")
    p.add_argument(
        "--quantification",
        choices=("f16", "q4_k_m"),
        default=None,
        help="quantification attendue : refusée si le GGUF de config/modeles en porte une autre",
    )
    p.add_argument(
        "--contexte",
        type=int,
        default=None,
        help="taille de contexte (tokens) du serveur de génération, au plus celle de "
        "config/modeles/<slug>.toml ; consignée dans run.json et resultat.json",
    )
    p.add_argument("--racine", type=Path, default=None, help="racine de index/ et runs/")
    p.set_defaults(func=_run)


def _composants(serveurs: list[Any], racine: Path, version: str | None) -> dict[str, Path]:
    from slmsp.index.config import dossier_index
    from slmsp.inference.serveur import dossier_llamacpp

    composants: dict[str, Path] = {s.role: s.gguf for s in serveurs}
    if version is not None:
        composants["index"] = dossier_index(racine) / version
    # NFR-6 : tous les binaires installés (bin-cpu et bin-cuda si présent), sans sous-estimer,
    # pour chaque version de llama.cpp servie (génération, éventuellement réservée comme Bonsai,
    # et embedding). Une seule version : clés `binaires-<variante>` ; plusieurs : le tag s'y
    # ajoute (`binaires-<tag>-<variante>`).
    bases: dict[str, Path] = {}
    for serveur in serveurs:
        config = serveur.config_llamacpp
        bases.setdefault(config.tag, dossier_llamacpp(config))
    if not bases:
        bases[""] = dossier_llamacpp()
    for tag, base in bases.items():
        prefixe = "binaires-" if len(bases) == 1 else f"binaires-{tag}-"
        trouves = False
        for dossier in sorted(base.glob("bin-*")):
            composants[f"{prefixe}{dossier.name.removeprefix('bin-')}"] = dossier
            trouves = True
        if not trouves:
            composants[f"{prefixe}cpu"] = base / "bin-cpu"
    return composants


def _plafond_sortie(service: Any, fiche: Any) -> int | None:
    """`max_tokens` effectif des Questions mesurées (consigné), `None` si inconnu."""
    plafond = getattr(service, "max_tokens_par_defaut", None)
    return plafond(fiche) if callable(plafond) else None


def _run(args: argparse.Namespace) -> int:
    from slmsp.cli._assemblage import ModeleInvalide, assembler, slug_modele
    from slmsp.core.erreurs import ConfigurationInvalide
    from slmsp.harness.taches import charger_taches
    from slmsp.index.lecture import versions_disponibles
    from slmsp.inference.serveur import charger_config_modele
    from slmsp.measure.config import charger_config_mesures
    from slmsp.measure.protocole import ContexteInsuffisant, mesurer, verrou_mesure

    try:
        slug = slug_modele(args.modele)
        maximum = charger_config_modele(slug).contexte
    except (ModeleInvalide, ConfigurationInvalide) as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    if args.contexte is not None and not 0 < args.contexte <= maximum:
        print(
            f"slmsp : --contexte {args.contexte} invalide : entier de 1 à {maximum} "
            f"(contexte de config/modeles/{slug}.toml)",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    # Sans --contexte : comportement inchangé (contexte du modèle, aucune vérification ajoutée),
    # le contexte effectif est seulement consigné.
    contexte = maximum if args.contexte is None else args.contexte
    config = charger_config_mesures()
    racine = (args.racine if args.racine is not None else racine_projet()).resolve()
    # Index lu sous les ressources ; le run s'écrit sous la racine d'écriture (AD-23).
    ecriture = (args.racine if args.racine is not None else racine_ecriture()).resolve()
    versions = versions_disponibles(racine)
    version = versions[-1] if versions else None
    fiche = charger_taches().defaut
    with (
        verrou_mesure(),
        assembler(
            args.modele,
            fiche,
            variante="cpu",
            racine=racine,
            threads=config.plafond_threads,
            contexte=args.contexte,
        ) as assemblage,
    ):
        if args.quantification is not None:
            gguf = next((s.gguf for s in assemblage.serveurs if s.role != "embedding"), None)
            etiquette = args.quantification.replace("_", "").lower()
            if gguf is None or etiquette not in gguf.name.replace("_", "").replace("-", "").lower():
                nom = "aucun" if gguf is None else gguf.name
                print(
                    f"slmsp : --quantification {args.quantification} ne correspond pas au GGUF "
                    f"configuré ({nom})",
                    file=sys.stderr,
                )
                return int(CodeSortie.USAGE)

        def repondre(question: str) -> Any:
            return assemblage.service.repondre(fiche, [{"role": "user", "content": question}])

        try:
            resultat = mesurer(
                repondre,
                config,
                modele=args.modele,
                quantification=args.quantification,
                serveurs=[s.description() for s in assemblage.serveurs],
                composants=_composants(assemblage.serveurs, racine, version),
                racine=ecriture,
                index_version=version,
                contexte=contexte,
                verifier_contexte=args.contexte is not None,
                max_tokens=_plafond_sortie(assemblage.service, fiche),
            )
        except ContexteInsuffisant as exc:
            print(f"slmsp : {exc}", file=sys.stderr)
            return int(CodeSortie.USAGE)
    valeurs = resultat.valeurs
    print(f"contexte effectif : {contexte} tokens (modèle : {maximum})")
    if resultat.details.get("verification_contexte") == "non-verifiee":
        print(
            "slmsp : avertissement : le serveur n'a pas renvoyé usage.prompt_tokens, la tenue "
            "du prompt dans --contexte n'a PAS pu être vérifiée (troncature possible)",
            file=sys.stderr,
        )
    print(f"{resultat.hypothese} ({args.modele}) : {resultat.verdict}")
    for nom, valeur in valeurs.items():
        print(f"  {nom} : {'n/d' if valeur is None else f'{valeur:.3f}'}")
    for nom, ok in resultat.conformite.items():
        print(f"  {nom} : {'conforme' if ok else 'NON conforme'}")
    print(resultat.avertissement)
    print(f"run {resultat.run_id} : {racine / 'runs' / 'measure' / resultat.run_id}")
    return int(CodeSortie.SUCCES)
