"""`slmsp index {build, info, mesurer}` : Index local (AD-9).

- `build` lit les parquet MediaTech de `config/index.toml` sous
  `<racine>/data/raw/mediatech/` et écrit `<racine>/index/<AAAAMMJJ>/` (extra `data`) ;
  une version existante n'est jamais reconstruite.
- `info` affiche la version, la date du snapshot et les comptes par source ; `--verifier`
  recalcule les SHA-256 des fichiers.
- `mesurer` mesure H-VEC (latence p50/p95, RAM ajoutée) dans un run `runs/measure/`.
- `verifier-embedding` mesure H-EMB (cosinus et recall@k des chunks revectorisés par
  `llama-server` contre les vecteurs MediaTech) dans un run `runs/measure/`.

`--racine` désigne la racine des écritures et lectures `data/`, `index/` et `runs/` (défaut :
racine du projet) ; `config/index.toml` est toujours lu sous la racine du projet. Ce module
n'importe pas pyarrow au chargement : `index info` reste disponible sans l'extra `data`.
"""

from __future__ import annotations

import argparse
import contextlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from slmsp.core.config import racine_ecriture, racine_projet
from slmsp.core.erreurs import CodeSortie
from slmsp.core.ports import EmbedderPort
from slmsp.index.config import charger_config_index, dossier_index
from slmsp.index.lecture import IndexLocal, ouvrir_index


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `index` et ses actions."""
    parseur = sous_parseurs.add_parser(
        "index",
        help="construire et vérifier l'Index local",
        description="Index local : construction, description et mesure H-VEC.",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)

    commun = argparse.ArgumentParser(add_help=False)
    commun.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine de data/, index/ et runs/ (défaut : racine du projet)",
    )
    version = argparse.ArgumentParser(add_help=False)
    version.add_argument(
        "--version",
        dest="version_index",
        default=None,
        metavar="AAAAMMJJ",
        help="version de l'Index (défaut : la plus récente)",
    )

    p = actions.add_parser(
        "build", parents=[commun], help="construire l'Index depuis les parquet MediaTech"
    )
    p.set_defaults(func=_build)

    p = actions.add_parser(
        "info", parents=[commun, version], help="version, date du snapshot et comptes par source"
    )
    p.add_argument(
        "--verifier", action="store_true", help="recalculer et contrôler les SHA-256 des fichiers"
    )
    p.set_defaults(func=_info)

    p = actions.add_parser(
        "mesurer", parents=[commun, version], help="mesurer H-VEC (latence et RAM de recherche)"
    )
    p.set_defaults(func=_mesurer)

    p = actions.add_parser(
        "verifier-embedding",
        parents=[commun, version],
        help="mesurer H-EMB (embedding de requête contre les vecteurs MediaTech)",
        description="Revectorise un échantillon de chunks par llama-server et compare aux "
        "vecteurs MediaTech (cosinus, recall@k). Démarre le serveur d'embedding.",
    )
    p.add_argument("--echantillon", type=int, default=None, help="chunks tirés (défaut : config)")
    p.add_argument("--graine", type=int, default=None, help="graine du tirage (défaut : config)")
    p.add_argument(
        "--modele",
        default="bge-m3",
        help="modèle d'embedding de config/modeles (bge-m3-f16 : repli)",
    )
    p.add_argument("--variante", choices=("cpu", "cuda"), default="cpu", help="llama.cpp")
    p.set_defaults(func=_verifier_embedding)


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_projet()).resolve()


def _afficher(index: IndexLocal) -> None:
    manifeste = index.manifeste
    print(f"Index {manifeste.version} : {index.dossier}")
    print(f"date du snapshot : {manifeste.date_snapshot.isoformat()}")
    print(f"créé le : {manifeste.cree_le.isoformat()}")
    print(f"modèle d'embedding : {manifeste.modele_embedding} ({manifeste.dimension}, float16)")
    print(f"chunks : {manifeste.nb_chunks}")
    for source in manifeste.sources:
        print(
            f"  {source.nom} : {source.nb_chunks} chunks, {source.nb_ecartes} écartés "
            f"(révision {source.revision}, snapshot {source.date_snapshot.isoformat()})"
        )


def _build(args: argparse.Namespace) -> int:
    from slmsp.indexation.construction import construire_index

    config = charger_config_index()
    # L'Index construit s'écrit sous la racine d'écriture, jamais sous `sys._MEIPASS` (AD-23).
    racine = (args.racine if args.racine is not None else racine_ecriture()).resolve()
    print(f"construction de l'Index {config.version()} sous {dossier_index(racine)}", flush=True)
    dossier = construire_index(config, racine)
    with IndexLocal(dossier, taille_bloc=config.taille_bloc) as index:
        _afficher(index)
    return int(CodeSortie.SUCCES)


def _info(args: argparse.Namespace) -> int:
    with ouvrir_index(_racine(args), args.version_index) as index:
        _afficher(index)
        if args.verifier:
            index.verifier()
            print("SHA-256 vérifiés : conformes au manifeste")
    return int(CodeSortie.SUCCES)


def _mesurer(args: argparse.Namespace) -> int:
    from slmsp.indexation.mesure_vec import mesurer_h_vec

    config = charger_config_index()
    racine = _racine(args)
    resultat = mesurer_h_vec(racine, args.version_index, config)
    valeurs = resultat.valeurs
    print(f"{resultat.hypothese} sur l'Index {resultat.index_version} : {resultat.verdict}")
    print(
        f"latence p50 {valeurs['p50_ms']:.1f} ms, p95 {valeurs['p95_ms']:.1f} ms "
        f"(seuil {resultat.seuils['p95_ms']:g} ms)"
    )
    print(
        f"RAM ajoutée {valeurs['ram_ajoutee_mo']:.1f} Mio (seuil {resultat.seuils['ram_mo']:g} Mio)"
    )
    if resultat.repli:
        print(f"repli : {resultat.repli}")
    print(f"run {resultat.run_id} : {racine / 'runs' / 'measure' / resultat.run_id}")
    return int(CodeSortie.SUCCES)


def _ouvrir_embedder(
    modele: str, variante: str
) -> contextlib.AbstractContextManager[tuple[EmbedderPort, dict[str, Any]]]:
    """Démarre `llama-server --embedding` pour `modele` ; fermé à la sortie du contexte.

    Rend l'embedder et la provenance du serveur (`description()` + sha256 du GGUF).
    """
    from slmsp.core.canonique import sha256_fichier
    from slmsp.core.erreurs import ConfigurationInvalide
    from slmsp.inference.serveur import ServeurLlama, charger_config_modele

    if not (racine_projet() / "config" / "modeles" / f"{modele}.toml").is_file():
        raise ConfigurationInvalide(
            f"modèle d'embedding inconnu : config/modeles/{modele}.toml est absent "
            "(bge-m3-f16 reste à créer si H-EMB est infirmée)"
        )

    @contextlib.contextmanager
    def ouvrir() -> Iterator[tuple[EmbedderPort, dict[str, Any]]]:
        with ServeurLlama(charger_config_modele(modele), variante, slug=modele) as serveur:  # type: ignore[arg-type]
            description = serveur.description()
            description["gguf_sha256"] = sha256_fichier(serveur.gguf)
            yield serveur.embedder(), description

    return ouvrir()


def _verifier_embedding(args: argparse.Namespace) -> int:
    from slmsp.indexation.verification_embedding import verifier_embedding

    config = charger_config_index()
    racine = _racine(args)
    with _ouvrir_embedder(args.modele, args.variante) as (embedder, serveur):
        resultat = verifier_embedding(
            racine,
            args.version_index,
            config,
            embedder,
            modele=args.modele,
            echantillon=args.echantillon,
            graine=args.graine,
            serveur=serveur,
        )
    valeurs = resultat.valeurs
    print(f"{resultat.hypothese} sur l'Index {resultat.index_version} : {resultat.verdict}")
    print(
        f"cosinus moyen {valeurs['cosinus_moyen']:.5f} "
        f"(seuil {resultat.seuils['cosinus_moyen']:g}), minimum {valeurs['cosinus_min']:.5f}"
    )
    print(
        f"recall@{resultat.parametres['k']} moyen {valeurs['recall_moyen']:.4f} "
        f"(seuil {resultat.seuils['recall_min']:g})"
    )
    if resultat.repli:
        print(f"repli : {resultat.repli}")
    print(f"run {resultat.run_id} : {racine / 'runs' / 'measure' / resultat.run_id}")
    return int(CodeSortie.SUCCES)
