"""`slmsp fetch {llamacpp, sources, modeles, benchmarks, prenoms}` : téléchargeur unique (AD-28).

Chaque exécution de `llamacpp`, `sources` ou `modeles` ouvre un run `fetch` (slug = la
sous-commande) sous `<racine>/runs/fetch/<run_id>/`, y inscrit `fichiers.jsonl` (une ligne
par fichier : dépôt ou URL, fichier, révision, octets transférés, SHA-256, statut), puis le
termine `complet` ou `partiel-erreur`. Les requêtes passent par les clients de
`slmsp.net` (profil `outillage`) et figurent à son journal des requêtes.

`fetch modeles` prend des slugs ou `--candidats` (les Modèles de base candidats, ordre D4).
Après le téléchargement, chaque modèle de génération passe les contrôles de
`slmsp.fetch.verifications` (`--sans-serveur` : sans démarrer `llama-server`), inscrits
dans `controles.jsonl`. Un modèle écarté est signalé sur stderr avec son motif ; le run
reste `complet` et la commande sort en code 1.

Options communes : `--racine` (racine des écritures `vendor/`, `data/`, `runs/` ; par
défaut la racine du projet) et `--reutiliser DOSSIER` (répétable : un fichier local de même
taille et de même SHA-256 est lié en dur au lieu d'être téléchargé). Les poids vont sous
`dossier_modeles()` (`SLMSP_MODELS_DIR`).
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from slmsp import net
from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.config import dossier_modeles, racine_projet
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide
from slmsp.core.prenoms_insee import OCCURRENCES_MINIMALES, prenoms_depuis_csv_insee
from slmsp.fetch import benchmarks, llamacpp, modeles, prenoms, sources, verifications
from slmsp.fetch import config as config_fetch
from slmsp.fetch.hf import Telechargeur, client_hf, jeton_hf, preparer_hf

NOM_FICHIERS = "fichiers.jsonl"
NOM_EXTRACTIONS = "extractions.jsonl"
NOM_CONTROLES = "controles.jsonl"


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `fetch` et ses sous-commandes."""
    parseur = sous_parseurs.add_parser(
        "fetch",
        help="télécharger modèles, llama.cpp, benchmarks et sources",
        description="Téléchargeur unique : révisions épinglées, SHA-256 vérifiés, "
        "profil réseau outillage.",
    )
    cibles = parseur.add_subparsers(dest="cible", metavar="<cible>", required=True)

    commun = argparse.ArgumentParser(add_help=False)
    commun.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine des écritures vendor/, data/ et runs/ (défaut : racine du projet)",
    )
    commun.add_argument(
        "--reutiliser",
        type=Path,
        action="append",
        default=[],
        metavar="DOSSIER",
        help="dossier où chercher un fichier identique (taille et SHA-256) à lier au lieu de "
        "le télécharger ; le lien dur partage le contenu avec le fichier source",
    )

    p = cibles.add_parser(
        "llamacpp", parents=[commun], help="binaires et sources de llama.cpp (tag figé)"
    )
    p.set_defaults(func=_llamacpp)

    p = cibles.add_parser("sources", parents=[commun], help="parquet du corpus MediaTech")
    p.add_argument(
        "--jeu", action="append", default=[], metavar="NOM", help="jeu à obtenir (répétable)"
    )
    p.set_defaults(func=_sources)

    p = cibles.add_parser("modeles", parents=[commun], help="poids de config/modeles/<slug>.toml")
    p.add_argument("slugs", nargs="*", metavar="SLUG")
    p.add_argument(
        "--candidats",
        action="store_true",
        help="les Modèles de base candidats, dans l'ordre D4 (exclut les SLUG)",
    )
    p.add_argument(
        "--sans-serveur",
        action="store_true",
        help="contrôles sans démarrer llama-server (contrôle serveur sans objet)",
    )
    p.add_argument(
        "--f16",
        action="store_true",
        help="télécharge aussi le GGUF F16 de base (`gguf_f16`), variante `avant` du banc",
    )
    p.set_defaults(func=_modeles)

    p = cibles.add_parser(
        "benchmarks", parents=[commun], help="jeux de config/benchmarks/*.toml (révision épinglée)"
    )
    p.add_argument("noms", nargs="*", metavar="BENCHMARK", help="benchmarks (défaut : tous)")
    p.set_defaults(func=_benchmarks)

    p = cibles.add_parser(
        "prenoms",
        parents=[commun],
        help="fichier des prénoms de l'INSEE, d'où `app/ressources/prenoms.txt`",
    )
    p.add_argument(
        "--sortie", type=Path, default=None, help="fichier généré (défaut : app/ressources)"
    )
    p.set_defaults(func=_prenoms)


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_projet()).resolve()


def _executer(
    args: argparse.Namespace,
    *,
    config_run: dict[str, Any],
    entrees: dict[str, Path],
    ouvrir_client: Callable[[], Any],
    pilote: Callable[[Telechargeur, Callable[[dict[str, Any]], None], Run], int | None],
) -> int:
    """Ouvre le run, exécute `pilote`, consigne chaque fichier et termine le run.

    Le code de sortie est celui que rend `pilote` (succès s'il ne rend rien).
    """
    reglages = config_fetch.charger_config_fetch()
    racine = _racine(args)
    reutiliser = [str(Path(dossier).resolve()) for dossier in args.reutiliser]
    for dossier in reutiliser:
        if not Path(dossier).is_dir():
            raise ConfigurationInvalide(f"--reutiliser : {dossier} n'est pas un dossier existant")
    run = nouveau_run(
        "fetch",
        args.cible,
        {**config_run, "racine": str(racine), "reutiliser": reutiliser},
        entrees={nom: chemin.resolve() for nom, chemin in entrees.items()},
        racine=racine,
    )
    statuts: Counter[str] = Counter()
    octets = 0

    def consigner(ligne: dict[str, Any]) -> None:
        nonlocal octets
        run.ajouter_jsonl(NOM_FICHIERS, ligne)
        statuts[ligne["statut"]] += 1
        octets += ligne["octets"]
        print(f"{ligne['statut']:<12} {ligne['destination']}", flush=True)

    try:
        with ouvrir_client() as client:
            telechargeur = Telechargeur(client, reglages, reutiliser=reutiliser)
            code = pilote(telechargeur, consigner, run)
    except KeyboardInterrupt:
        run.terminer("interrompu", "arrêt demandé")
        print(f"run {run.run_id} : {run.dossier}", file=sys.stderr)
        raise
    except Exception as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        print(f"run {run.run_id} : {run.dossier}", file=sys.stderr)
        raise
    run.terminer("complet")
    detail = ", ".join(f"{statut} {nombre}" for statut, nombre in sorted(statuts.items()))
    print(
        f"fetch {args.cible} : {sum(statuts.values())} fichier(s) ({detail or 'aucun'}), "
        f"{octets} octets transférés ; run {run.run_id}"
    )
    return int(CodeSortie.SUCCES if code is None else code)


def _client_github() -> Any:
    """Client GitHub : profil `outillage`, redirections suivies, sans jeton."""
    return net.client("outillage", follow_redirects=True)


def _client_hf() -> Any:
    """Client Hugging Face (`net.fabrique_hf`), seul porteur de `HF_TOKEN`."""
    return client_hf(jeton_hf())


def _llamacpp(args: argparse.Namespace) -> int:
    preparer_hf()
    dossier = config_fetch.dossier_config()
    config = config_fetch.charger_config_llamacpp()

    def pilote(telechargeur: Telechargeur, consigner: Any, run: Run) -> None:
        llamacpp.executer(
            telechargeur,
            config,
            _racine(args),
            consigner=consigner,
            consigner_extraction=lambda ligne: run.ajouter_jsonl(NOM_EXTRACTIONS, ligne),
        )

    return _executer(
        args,
        config_run={"sous_commande": "llamacpp", "tag": config.tag, "depot": config.depot},
        entrees={
            "config/fetch.toml": dossier / "fetch.toml",
            "config/llamacpp.toml": dossier / "llamacpp.toml",
        },
        ouvrir_client=_client_github,
        pilote=pilote,
    )


def _sources(args: argparse.Namespace) -> int:
    preparer_hf()
    dossier = config_fetch.dossier_config()
    config = config_fetch.charger_config_sources()
    jeux = [jeu.nom for jeu in sources.choisir_jeux(config, args.jeu)]

    def pilote(telechargeur: Telechargeur, consigner: Any, _run: Run) -> None:
        sources.executer(telechargeur, config, _racine(args), jeux=jeux, consigner=consigner)

    return _executer(
        args,
        config_run={"sous_commande": "sources", "jeux": jeux},
        entrees={
            "config/fetch.toml": dossier / "fetch.toml",
            "config/sources.toml": dossier / "sources.toml",
        },
        ouvrir_client=_client_hf,
        pilote=pilote,
    )


def _controler(configs: list[tuple[str, Any]], poids: Path, run: Run, *, sans_serveur: bool) -> int:
    """Contrôles des modèles de génération, inscrits dans `controles.jsonl` ; code 1 si un
    modèle est écarté."""
    controles: list[verifications.Controle] = []
    for slug, config in configs:
        if config.embedding:
            continue
        for controle in verifications.verifier_modele(
            slug, config, poids, sans_serveur=sans_serveur
        ):
            run.ajouter_jsonl(NOM_CONTROLES, controle.ligne())
            controles.append(controle)
            premiere = controle.detail.splitlines()[0] if controle.detail else ""
            print(f"{controle.statut:<12} {slug} {controle.controle} : {premiere}", flush=True)
    if not controles:
        return int(CodeSortie.SUCCES)
    ecartes = verifications.ecartes(controles)
    print(f"contrôles : {len(controles)}, modèle(s) écarté(s) : {len(ecartes)}")
    for slug, motifs in ecartes.items():
        for motif in motifs:
            print(f"slmsp : modèle écarté : {slug} : {motif.splitlines()[0]}", file=sys.stderr)
    return int(CodeSortie.ERREUR if ecartes else CodeSortie.SUCCES)


def _modeles(args: argparse.Namespace) -> int:
    if args.candidats == bool(args.slugs):
        print(
            "slmsp : fetch modeles : donner des SLUG ou --candidats (l'un des deux, pas les deux)",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    preparer_hf()
    dossier = config_fetch.dossier_config()
    slugs = list(verifications.CANDIDATS) if args.candidats else list(dict.fromkeys(args.slugs))
    configs = [(slug, config_fetch.charger_config_modele(slug)) for slug in slugs]
    poids = dossier_modeles()
    if args.f16:
        for slug, config in configs:
            if config.gguf_f16 is None:
                print(
                    f"slmsp : avertissement : {slug} : pas de section gguf_f16, --f16 sans effet",
                    file=sys.stderr,
                )

    def pilote(telechargeur: Telechargeur, consigner: Any, run: Run) -> int:
        modeles.executer(telechargeur, configs, poids, f16=args.f16, consigner=consigner)
        return _controler(configs, poids, run, sans_serveur=args.sans_serveur)

    return _executer(
        args,
        config_run={
            "sous_commande": "modeles",
            "slugs": slugs,
            "candidats": args.candidats,
            "sans_serveur": args.sans_serveur,
            "f16": args.f16,
            "dossier_modeles": str(poids),
        },
        entrees={
            "config/fetch.toml": dossier / "fetch.toml",
            **{
                f"config/modeles/{slug}.toml": dossier / "modeles" / f"{slug}.toml"
                for slug in slugs
            },
        },
        ouvrir_client=_client_hf,
        pilote=pilote,
    )


def _benchmarks(args: argparse.Namespace) -> int:
    preparer_hf()
    dossier = config_fetch.dossier_config()
    jeux = benchmarks.lire_jeux(dossier / "benchmarks", args.noms)

    def pilote(telechargeur: Telechargeur, consigner: Any, _run: Run) -> None:
        benchmarks.executer(telechargeur, jeux, _racine(args), consigner=consigner)

    return _executer(
        args,
        config_run={
            "sous_commande": "benchmarks",
            "benchmarks": list(args.noms),
            "jeux": [jeu.nom for jeu in jeux],
        },
        entrees={"config/fetch.toml": dossier / "fetch.toml"},
        ouvrir_client=_client_hf,
        pilote=pilote,
    )


def _prenoms(args: argparse.Namespace) -> int:
    config = prenoms.charger_config_prenoms()
    sortie = args.sortie if args.sortie is not None else prenoms.FICHIER_PRENOMS

    def pilote(telechargeur: Telechargeur, consigner: Any, _run: Run) -> None:
        _resultat, nombre = prenoms.executer(
            telechargeur,
            config,
            _racine(args),
            sortie=sortie,
            extraire=prenoms_depuis_csv_insee,
            minimum=OCCURRENCES_MINIMALES,
            consigner=consigner,
        )
        print(f"{nombre} prénoms retenus")

    return _executer(
        args,
        config_run={"sous_commande": "prenoms", "url": config.url, "sha256": config.sha256},
        entrees={"config/outillage.toml": config_fetch.dossier_config() / "outillage.toml"},
        ouvrir_client=_client_github,
        pilote=pilote,
    )
