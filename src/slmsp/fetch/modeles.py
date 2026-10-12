"""Pilote `slmsp fetch modeles` : poids décrits par `config/modeles/<slug>.toml` (AD-28).

- GGUF : `<models>/<slug>/gguf/<nom du fichier>`, SHA-256 de la configuration. Pris à
  `gguf.revision` si elle est donnée ; sinon à la révision `revision` s'il vient de
  `depot_hf`, et d'un autre dépôt à la révision `main` résolue en commit (`X-Repo-Commit`).
- `fichiers` : `<models>/<slug>/hf/<chemin>`, à la révision `revision`. SHA-256 attendu
  lu dans `sha256_fichiers`, sinon dans `X-Linked-Etag` (fichiers LFS) ; un fichier sans
  SHA connu est refusé, un `X-Linked-Etag` différent du SHA de la configuration aussi.

Un fichier présent dont le SHA-256 est connu en configuration ne déclenche aucune requête :
le moteur le vérifie sur disque. `<models>` vaut `dossier_modeles()` (`SLMSP_MODELS_DIR`).
Les contrôles des modèles candidats sont dans `slmsp.fetch.verifications`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.fetch.config import chemin_config
from slmsp.fetch.hf import (
    ResultatFichier,
    ShaInvalide,
    TelechargementEchoue,
    Telechargeur,
    url_hf,
)

REVISION_AUTRE_DEPOT = "main"


@dataclass(frozen=True)
class FichierPrevu:
    """Fichier de modèle à obtenir."""

    depot: str
    fichier: str
    revision: str
    url: str
    destination: Path
    sha256: str
    taille: int | None
    genre: str
    """`gguf` ou `hf`."""


def _gguf(telechargeur: Telechargeur, config: ConfigModele, base: Path) -> FichierPrevu:
    gguf = config.gguf
    chemin = chemin_config(gguf.fichier, f"modèle {config.depot_hf} : gguf.fichier")
    destination = base / "gguf" / PurePosixPath(chemin).name
    meme_depot = gguf.depot == config.depot_hf
    epinglee = gguf.revision is not None or meme_depot
    if gguf.revision is not None:
        revision = gguf.revision
    else:
        revision = config.revision if meme_depot else REVISION_AUTRE_DEPOT
    url = url_hf(gguf.depot, chemin, revision)
    if destination.exists():  # contrôlé par le moteur, sans requête
        return FichierPrevu(
            gguf.depot, chemin, revision, url, destination, gguf.sha256, None, "gguf"
        )
    meta = telechargeur.metadonnees_hf(url)
    if meta.sha256 is not None and meta.sha256 != gguf.sha256:
        raise ShaInvalide(
            f"{gguf.depot}/{chemin}@{revision} : X-Linked-Etag {meta.sha256} différent du "
            f"SHA-256 de la configuration ({gguf.sha256})"
        )
    if not epinglee:
        if meta.commit is None:
            raise TelechargementEchoue(
                f"{gguf.depot}/{chemin} : commit de la révision {revision} introuvable "
                "(X-Repo-Commit absent)"
            )
        revision = meta.commit
        url = url_hf(gguf.depot, chemin, revision)
    return FichierPrevu(
        gguf.depot, chemin, revision, url, destination, gguf.sha256, meta.taille, "gguf"
    )


def _fichier_hf(
    telechargeur: Telechargeur, config: ConfigModele, base: Path, chemin: str
) -> FichierPrevu:
    chemin = chemin_config(chemin, f"modèle {config.depot_hf} : fichiers")
    url = url_hf(config.depot_hf, chemin, config.revision)
    destination = base.joinpath("hf", *chemin.split("/"))
    attendu = config.sha256_fichiers.get(chemin)
    if attendu is not None and destination.exists():  # contrôlé par le moteur, sans requête
        return FichierPrevu(
            config.depot_hf, chemin, config.revision, url, destination, attendu, None, "hf"
        )
    meta = telechargeur.metadonnees_hf(url)
    if attendu is not None and meta.sha256 is not None and meta.sha256 != attendu:
        raise ShaInvalide(
            f"{config.depot_hf}/{chemin}@{config.revision} : X-Linked-Etag {meta.sha256} "
            f"différent du SHA-256 de la configuration ({attendu})"
        )
    sha256 = attendu or meta.sha256
    if sha256 is None:
        raise ShaInvalide(
            f"{config.depot_hf}/{chemin}@{config.revision} : aucun SHA-256 attendu "
            "(absent de la configuration, pas de X-Linked-Etag : fichier non LFS)"
        )
    return FichierPrevu(
        config.depot_hf,
        chemin,
        config.revision,
        url,
        destination,
        sha256,
        meta.taille,
        "hf",
    )


def planifier(
    telechargeur: Telechargeur, slug: str, config: ConfigModele, dossier_modeles: str | Path
) -> list[FichierPrevu]:
    """Fichiers du modèle `slug` : GGUF puis `fichiers` HF (requêtes `HEAD` si besoin)."""
    base = Path(dossier_modeles) / slug
    plan = [_gguf(telechargeur, config, base)]
    plan.extend(_fichier_hf(telechargeur, config, base, chemin) for chemin in config.fichiers)
    return plan


def executer(
    telechargeur: Telechargeur,
    modeles: list[tuple[str, ConfigModele]],
    dossier_modeles: str | Path,
    *,
    consigner: Callable[[dict[str, Any]], None] = lambda _ligne: None,
) -> list[ResultatFichier]:
    """Télécharge les fichiers de chaque `(slug, config)` ; une ligne par fichier."""
    plans = [
        (slug, prevu)
        for slug, config in modeles
        for prevu in planifier(telechargeur, slug, config, dossier_modeles)
    ]
    telechargeur.verifier_espace_total((p.destination, p.taille) for _, p in plans)
    resultats = []
    for slug, prevu in plans:
        resultat = telechargeur.telecharger(
            prevu.url, prevu.destination, prevu.sha256, prevu.taille
        )
        resultats.append(resultat)
        consigner(
            {
                "modele": slug,
                "genre": prevu.genre,
                "depot": prevu.depot,
                "url": prevu.url,
                "fichier": prevu.fichier,
                "revision": prevu.revision,
                "octets": resultat.octets,
                "taille": resultat.taille,
                "sha256": resultat.sha256,
                "statut": resultat.statut,
                "destination": str(resultat.destination),
                "source": None if resultat.source is None else str(resultat.source),
            }
        )
    return resultats


__all__ = ["FichierPrevu", "executer", "planifier"]
