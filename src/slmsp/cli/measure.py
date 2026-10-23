"""Sous-commandes `slmsp measure` : mesures techniques FR-26 (NFR-1 à NFR-3, NFR-6).

    slmsp measure run --modele base:<slug> [--quantification q4_k_m] [--racine DOSSIER]
                       [--speculatif {aucun,brouillon,ngram}] [--brouillon <slug>]
                       [--brouillon-n-max N]
    slmsp measure application --exe AssistantSP.exe [--duree SECONDES]
                               [--mesures-csv CSV] [--racine DOSSIER]

`run` assemble l'Assistant complet comme `slmsp ask` (deux `llama-server` en variante `cpu`,
threads plafonnés par `config/mesures.toml`, Index local chargé), mesure des Questions avec
recherche dans l'Index et écrit `runs/measure/<run_id>/resultat.json`.

`application` (story 12.14) lance l'exécutable installé (onedir, pywebview + WebView2 +
deux `llama-server`) et échantillonne la RAM de tout son arbre pendant qu'Anaël l'utilise ;
débit et délai au premier jeton viennent, en option, d'un export CSV des mesures de
l'application. Protocole manuel (capture réseau, NFR-7) : `docs/recette-pc-cible.md`.

Les deux refusent (`RessourceOccupee`, code 5) si une autre commande `slmsp` tient le verrou.
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
    p.add_argument(
        "--modele", required=True, help="modèle : base:<slug> ou lora:<export_lora_run_id>"
    )
    p.add_argument(
        "--echelle-lora",
        type=float,
        default=None,
        metavar="ECHELLE",
        help="avec lora:<id> : échelle de --lora-scaled (défaut 1.0), consignée dans la "
        "référence du modèle (lora:<id>@<échelle>)",
    )
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
    p.add_argument(
        "--speculatif",
        choices=("aucun", "brouillon", "ngram"),
        default=None,
        help="décodage spéculatif de llama-server (défaut : aucun) ; `brouillon` exige "
        "--brouillon ; consigné dans run.json et resultat.json",
    )
    p.add_argument(
        "--brouillon",
        default=None,
        metavar="SLUG",
        help="modèle brouillon (slug de config/modeles, même vocabulaire que la cible) ; "
        "implique --speculatif brouillon",
    )
    p.add_argument(
        "--brouillon-n-max",
        type=int,
        default=None,
        metavar="N",
        help="tokens proposés par tour (--spec-draft-n-max de llama-server, défaut 3)",
    )
    p.add_argument("--racine", type=Path, default=None, help="racine de index/ et runs/")
    p.set_defaults(func=_run)

    pa = actions.add_parser(
        "application",
        help="mesurer la RAM de l'application installée, et en option son débit et sa latence",
    )
    pa.add_argument(
        "--exe", required=True, type=Path, help="chemin de l'exécutable installé (AssistantSP.exe)"
    )
    pa.add_argument(
        "--duree",
        type=float,
        default=900.0,
        metavar="SECONDES",
        help="durée maximale de la fenêtre de mesure (défaut 900 s) ; la fermeture de "
        "l'application ou Ctrl+C y mettent fin plus tôt, sans jamais tuer le processus",
    )
    pa.add_argument(
        "--mesures-csv",
        type=Path,
        default=None,
        metavar="CSV",
        help="export CSV des mesures de l'application (menu Méthode) ; sans lui, débit et "
        "délai au premier jeton restent absents du résultat",
    )
    pa.add_argument("--racine", type=Path, default=None, help="racine de runs/")
    pa.set_defaults(func=_application)


def _composants(serveurs: list[Any], racine: Path, version: str | None) -> dict[str, Path]:
    from slmsp.index.config import dossier_index
    from slmsp.inference.serveur import dossier_llamacpp

    composants: dict[str, Path] = {s.role: s.gguf for s in serveurs}
    brouillon = next((g for s in serveurs if (g := getattr(s, "gguf_brouillon", None))), None)
    if brouillon is not None:
        composants["brouillon"] = brouillon
    lora = next((s.lora.gguf for s in serveurs if getattr(s, "lora", None) is not None), None)
    if lora is not None:
        composants["lora"] = lora
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


def _speculatif(args: argparse.Namespace, slug: str) -> Any:
    """`Speculatif` demandé par les options, `None` pour aucun ; `ConfigurationInvalide` sinon.

    La fiche et le vocabulaire du brouillon sont vérifiés ici, pour que leur refus sorte en
    code USAGE et non au démarrage du serveur.
    """
    from slmsp.core.erreurs import ConfigurationInvalide
    from slmsp.inference.serveur import (
        Speculatif,
        charger_config_modele,
        verifier_vocabulaire_brouillon,
    )

    mode = args.speculatif
    if args.brouillon is not None:
        if mode not in (None, "brouillon"):
            raise ConfigurationInvalide(f"--brouillon incompatible avec --speculatif {mode}")
        mode = "brouillon"
    if mode in (None, "aucun"):
        if args.brouillon_n_max is not None:
            raise ConfigurationInvalide("--brouillon-n-max exige --speculatif brouillon")
        return None
    speculatif = Speculatif(mode, args.brouillon, args.brouillon_n_max)
    if speculatif.brouillon is not None:
        verifier_vocabulaire_brouillon(charger_config_modele(slug), slug, speculatif.brouillon)
    return speculatif


def _modele_et_lora(args: argparse.Namespace, racine: Path) -> tuple[str, str, Any]:
    """(référence consignée, `base:<slug>` servi, `Lora` ou `None`)

    Lève `ValueError` (échelle ou référence mal formée), `ConfigurationInvalide` (run).
    """
    from slmsp.evaluation import modele_ref
    from slmsp.inference.serveur import Lora

    ref = modele_ref.composer_lora(args.modele, args.echelle_lora)
    if ref.startswith("distant:"):
        raise ValueError(f"{ref} : modèle distant, sans GGUF : measure ne le prend pas")
    if not ref.startswith("lora:"):
        return ref, ref, None
    resolu = modele_ref.resoudre(ref, "q4_k_m", racine=racine)
    assert resolu.lora is not None and resolu.echelle_lora is not None
    return ref, f"base:{resolu.slug}", Lora(resolu.lora, resolu.echelle_lora)


def _run(args: argparse.Namespace) -> int:
    from slmsp.cli._assemblage import ModeleInvalide, assembler, slug_modele
    from slmsp.core.erreurs import ConfigurationInvalide
    from slmsp.harness.taches import charger_taches
    from slmsp.index.lecture import versions_disponibles
    from slmsp.inference.serveur import charger_config_modele
    from slmsp.measure.config import charger_config_mesures
    from slmsp.measure.protocole import ContexteInsuffisant, mesurer, verrou_mesure

    ecriture = (args.racine if args.racine is not None else racine_ecriture()).resolve()
    try:
        ref, modele, lora = _modele_et_lora(args, ecriture)
        slug = slug_modele(modele)
        maximum = charger_config_modele(slug).contexte
        speculatif = _speculatif(args, slug)
    except (ModeleInvalide, ConfigurationInvalide, ValueError) as exc:
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
    versions = versions_disponibles(racine)
    version = versions[-1] if versions else None
    fiche = charger_taches().defaut
    with (
        verrou_mesure(),
        assembler(
            modele,
            fiche,
            variante="cpu",
            racine=racine,
            threads=config.plafond_threads,
            contexte=args.contexte,
            speculatif=speculatif,
            lora=lora,
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
                modele=ref,
                quantification=args.quantification,
                serveurs=[s.description() for s in assemblage.serveurs],
                composants=_composants(assemblage.serveurs, racine, version),
                racine=ecriture,
                index_version=version,
                contexte=contexte,
                verifier_contexte=args.contexte is not None,
                max_tokens=_plafond_sortie(assemblage.service, fiche),
                speculatif=None if speculatif is None else speculatif.decrire(),
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
    print(f"{resultat.hypothese} ({ref}) : {resultat.verdict}")
    for nom, valeur in valeurs.items():
        print(f"  {nom} : {'n/d' if valeur is None else f'{valeur:.3f}'}")
    for nom, ok in resultat.conformite.items():
        print(f"  {nom} : {'conforme' if ok else 'NON conforme'}")
    print(resultat.avertissement)
    print(f"run {resultat.run_id} : {racine / 'runs' / 'measure' / resultat.run_id}")
    return int(CodeSortie.SUCCES)


def _application(args: argparse.Namespace) -> int:
    from slmsp.measure.application import CsvInvalide, InstanceDejaOuverte, mesurer_application
    from slmsp.measure.config import charger_config_mesures
    from slmsp.measure.protocole import verrou_mesure

    if not args.exe.is_file():
        print(f"slmsp : {args.exe} : exécutable introuvable", file=sys.stderr)
        return int(CodeSortie.USAGE)
    config = charger_config_mesures()
    racine = (args.racine if args.racine is not None else racine_ecriture()).resolve()
    try:
        with verrou_mesure(commande="slmsp measure application"):
            resultat = mesurer_application(
                args.exe,
                config,
                duree_s=args.duree,
                mesures_csv=args.mesures_csv,
                racine=racine,
            )
    except InstanceDejaOuverte as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    except CsvInvalide as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    valeurs = resultat.valeurs
    print(f"{resultat.hypothese} (application installée) : {resultat.verdict}")
    for nom, valeur in valeurs.items():
        print(f"  {nom} : {'n/d' if valeur is None else f'{valeur:.3f}'}")
    for nom, ok in resultat.conformite.items():
        print(f"  {nom} : {'conforme' if ok else 'NON conforme'}")
    print(resultat.avertissement)
    print(f"run {resultat.run_id} : {racine / 'runs' / 'measure' / resultat.run_id}")
    return int(CodeSortie.SUCCES)
