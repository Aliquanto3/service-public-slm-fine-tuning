"""Construction de l'Index local `index/<AAAAMMJJ>/` (AD-9, D4).

Les parquet MediaTech de chaque source de `config/index.toml` sont lus sous
`<racine>/data/raw/mediatech/<jeu>/<revision>/*.parquet` (ordre des noms), par lots
pyarrow (import paresseux, extra `data`). Les vecteurs viennent de la colonne JSON
`embeddings_bge-m3`, jamais recalculés : chacun est renormalisé L2 en float32 puis converti
en float16. Une ligne au vecteur nul, illisible, de mauvaise dimension, de norme nulle ou non
finie est écartée et comptée.

L'Index est écrit dans `index/.<version>.en-cours-<4 hex>/`, puis renommé en
`index/<version>/` par `os.rename`. Une version existante n'est jamais reconstruite
(`ArtefactExistant`, avant toute lecture) ; rien n'est supprimé ni réécrit, y compris un
dossier en cours laissé par une construction interrompue.
"""

from __future__ import annotations

import json
import math
import os
import secrets
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from slmsp.core.artefacts import ArtefactExistant, verifier_espace
from slmsp.core.canonique import json_canonique, sha256_fichier
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, SlmspError
from slmsp.core.schemas.manifeste_index import ManifesteIndex, SourceManifeste
from slmsp.index.config import (
    NOM_CHUNKS,
    NOM_MANIFESTE,
    NOM_VECTEURS,
    ConfigIndex,
    SourceIndex,
    dossier_index,
    version_valide,
)

CHAMPS_TEXTE = ("chunk_id", "doc_id", "titre", "url", "texte")
"""Champs de `chunks.sqlite` lus dans le parquet (dans cet ordre)."""

SCHEMA_CHUNKS = """
CREATE TABLE chunks (
    rang INTEGER PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    source TEXT NOT NULL,
    titre TEXT NOT NULL,
    url TEXT NOT NULL,
    texte TEXT NOT NULL,
    date_snapshot TEXT NOT NULL
)
"""


@dataclass
class SourceLue:
    """Lignes valides d'une source, dans l'ordre de lecture (ligne `i` ↔ vecteur `i`)."""

    source: SourceIndex
    vecteurs: NDArray[np.float16]
    """`(nb_chunks, dimension)`, float16, normalisés L2."""
    lignes: list[tuple[str, str, str, str, str]]
    """`(chunk_id, doc_id, titre, url, texte)` de chaque ligne valide."""
    nb_ecartes: int = 0
    parquet: dict[str, str] = field(default_factory=dict)
    """Nom du fichier parquet lu -> SHA-256."""

    @property
    def nb_chunks(self) -> int:
        return len(self.lignes)


def dossier_parquet(racine: str | Path, source: SourceIndex) -> Path:
    """`<racine>/data/raw/mediatech/<jeu>/<revision>`."""
    return Path(racine) / "data" / "raw" / "mediatech" / source.jeu / source.revision


def vecteur_depuis_json(texte: Any, dimension: int) -> NDArray[np.float32] | None:
    """Vecteur float32 normalisé L2 lu depuis la chaîne JSON `texte`, ou `None` s'il est invalide.

    Invalide : valeur nulle, JSON illisible, autre chose qu'une liste de `dimension` nombres,
    valeur non finie, norme nulle ou non finie.
    """
    if texte is None:
        return None
    try:
        valeurs = json.loads(texte)
    except (TypeError, ValueError):
        return None
    if not isinstance(valeurs, list) or len(valeurs) != dimension:
        return None
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in valeurs):
        return None
    try:
        with np.errstate(over="ignore", invalid="ignore"):
            vecteur = np.asarray(valeurs, dtype=np.float32)
    except (TypeError, ValueError, OverflowError):
        return None
    if not np.all(np.isfinite(vecteur)):
        return None
    norme = float(np.linalg.norm(vecteur.astype(np.float64)))
    if not math.isfinite(norme) or norme == 0.0:
        return None
    return (vecteur / np.float32(norme)).astype(np.float32)


def _texte(valeur: Any) -> str:
    return "" if valeur is None else str(valeur)


def _pyarrow_parquet() -> Any:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SlmspError(
            f"pyarrow indisponible ({exc.name or exc}) : lancer avec l'extra `data` "
            "(`uv run --extra data slmsp index build`)"
        ) from None
    return pq


def fichiers_parquet(racine: str | Path, source: SourceIndex) -> list[Path]:
    """Parquet de la source, dans l'ordre des noms.

    Lève `ConfigurationInvalide` (chemin cité) si le dossier est absent ou sans parquet.
    """
    dossier = dossier_parquet(racine, source)
    fichiers = sorted(
        (chemin for chemin in dossier.glob("*.parquet") if chemin.is_file()),
        key=lambda chemin: chemin.name,
    )
    if not fichiers:
        raise ConfigurationInvalide(
            f"source {source.nom} : aucun fichier parquet sous {dossier} "
            "(lancer `slmsp fetch sources`)"
        )
    return fichiers


def lire_source_parquet(source: SourceIndex, racine: str | Path, config: ConfigIndex) -> SourceLue:
    """Lit les parquet de `source` par lots ; écarte et compte les lignes au vecteur invalide."""
    fichiers = fichiers_parquet(racine, source)
    pq = _pyarrow_parquet()
    colonnes = source.colonnes
    noms_colonnes = [getattr(colonnes, champ) for champ in CHAMPS_TEXTE]
    a_lire = list(dict.fromkeys([*noms_colonnes, config.colonne_vecteurs]))

    ouverts = []
    total = 0
    for chemin in fichiers:
        parquet = pq.ParquetFile(chemin)
        presentes = set(parquet.schema_arrow.names)
        manquantes = [nom for nom in a_lire if nom not in presentes]
        if manquantes:
            raise ConfigurationInvalide(
                f"{chemin} : colonne(s) absente(s) : {', '.join(manquantes)}"
            )
        ouverts.append((chemin, parquet))
        total += parquet.metadata.num_rows

    vecteurs = np.empty((total, config.dimension), dtype=np.float16)
    lignes: list[tuple[str, str, str, str, str]] = []
    empreintes: dict[str, str] = {}
    ecartes = 0
    for chemin, parquet in ouverts:
        empreintes[chemin.name] = sha256_fichier(chemin)
        for lot in parquet.iter_batches(batch_size=config.taille_lot_lecture, columns=a_lire):
            valeurs = {nom: lot.column(nom).to_pylist() for nom in a_lire}
            for i, brut in enumerate(valeurs[config.colonne_vecteurs]):
                vecteur = vecteur_depuis_json(brut, config.dimension)
                if vecteur is None:
                    ecartes += 1
                    continue
                if len(lignes) >= total:
                    raise SlmspError(f"{chemin} : plus de lignes que n'en annonce le parquet")
                vecteurs[len(lignes)] = vecteur
                lignes.append(
                    tuple(_texte(valeurs[nom][i]) for nom in noms_colonnes)  # type: ignore[arg-type]
                )
    return SourceLue(
        source=source,
        vecteurs=vecteurs[: len(lignes)],
        lignes=lignes,
        nb_ecartes=ecartes,
        parquet=empreintes,
    )


def _ecrire_vecteurs(chemin: Path, sources_lues: Sequence[SourceLue], dimension: int) -> None:
    """`vectors.f16.npy` en création exclusive, sans concaténer les sources en mémoire."""
    nb = sum(lue.nb_chunks for lue in sources_lues)
    entete = {
        "descr": np.lib.format.dtype_to_descr(np.dtype("<f2")),
        "fortran_order": False,
        "shape": (nb, dimension),
    }
    with chemin.open("xb") as flux:
        np.lib.format.write_array_header_1_0(flux, entete)
        for lue in sources_lues:
            if lue.vecteurs.shape != (lue.nb_chunks, dimension):
                raise ValueError(
                    f"source {lue.source.nom} : vecteurs de forme {lue.vecteurs.shape}, "
                    f"({lue.nb_chunks}, {dimension}) attendue"
                )
            flux.write(np.ascontiguousarray(lue.vecteurs, dtype="<f2").tobytes())


def _ecrire_chunks(chemin: Path, sources_lues: Sequence[SourceLue]) -> None:
    """`chunks.sqlite` : ligne `rang` = vecteur `rang` (0-based)."""
    if chemin.exists():
        raise ArtefactExistant(f"{chemin} existe déjà : un artefact n'est jamais réécrit")
    connexion = sqlite3.connect(chemin)
    try:
        connexion.execute(SCHEMA_CHUNKS)
        rang = 0
        for lue in sources_lues:
            date_source = lue.source.date_snapshot.isoformat()
            connexion.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    (rang + i, chunk_id, doc_id, lue.source.nom, titre, url, texte, date_source)
                    for i, (chunk_id, doc_id, titre, url, texte) in enumerate(lue.lignes)
                ),
            )
            rang += lue.nb_chunks
        connexion.commit()
    finally:
        connexion.close()


def _estimation_octets(sources_lues: Sequence[SourceLue], dimension: int) -> int:
    vecteurs = sum(lue.nb_chunks for lue in sources_lues) * dimension * 2
    textes = sum(len(champ) * 4 for lue in sources_lues for ligne in lue.lignes for champ in ligne)
    return vecteurs + textes


def ecrire_index(
    dossier: str | Path,
    version: str,
    sources_lues: Sequence[SourceLue],
    config: ConfigIndex,
    *,
    maintenant: datetime | None = None,
) -> Path:
    """Écrit `<dossier>/<version>/` (vecteurs, chunks, manifeste) ; renvoie son chemin.

    Lève `ArtefactExistant` si la version existe, `ConfigurationInvalide` si aucune ligne
    n'est valide, `EspaceInsuffisant` si le disque manque de place.
    """
    if not version_valide(version):
        raise ValueError(f"version d'Index invalide : {version!r} (attendu : AAAAMMJJ)")
    if not sources_lues:
        raise ConfigurationInvalide("aucune source à indexer")
    date_snapshot = max(lue.source.date_snapshot for lue in sources_lues)
    if date_snapshot.strftime("%Y%m%d") != version:
        raise ValueError(
            f"version {version} différente de la date de snapshot la plus récente "
            f"des sources ({date_snapshot.isoformat()})"
        )
    dossier = Path(dossier).resolve()
    final = dossier / version
    if final.exists():
        raise ArtefactExistant(f"{final} existe déjà : un Index n'est jamais reconstruit")
    nb_chunks = sum(lue.nb_chunks for lue in sources_lues)
    if nb_chunks == 0:
        raise ConfigurationInvalide("aucun chunk valide à indexer")
    verifier_espace(dossier, _estimation_octets(sources_lues, config.dimension))

    dossier.mkdir(parents=True, exist_ok=True)
    en_cours = dossier / f".{version}.en-cours-{secrets.token_hex(2)}"
    en_cours.mkdir(exist_ok=False)
    _ecrire_vecteurs(en_cours / NOM_VECTEURS, sources_lues, config.dimension)
    _ecrire_chunks(en_cours / NOM_CHUNKS, sources_lues)

    manifeste = ManifesteIndex(
        version=version,
        date_snapshot=date_snapshot,
        cree_le=maintenant or datetime.now().astimezone(),
        modele_embedding=config.modele_embedding,
        colonne_vecteurs=config.colonne_vecteurs,
        dimension=config.dimension,
        nb_chunks=nb_chunks,
        sources=[
            SourceManifeste(
                nom=lue.source.nom,
                jeu=lue.source.jeu,
                revision=lue.source.revision,
                date_snapshot=lue.source.date_snapshot,
                nb_chunks=lue.nb_chunks,
                nb_ecartes=lue.nb_ecartes,
                parquet=lue.parquet,
            )
            for lue in sources_lues
        ],
        fichiers={
            NOM_VECTEURS: sha256_fichier(en_cours / NOM_VECTEURS),
            NOM_CHUNKS: sha256_fichier(en_cours / NOM_CHUNKS),
        },
    )
    with (en_cours / NOM_MANIFESTE).open("xb") as flux:
        flux.write(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
    try:
        os.rename(en_cours, final)
    except FileExistsError:
        raise ArtefactExistant(
            f"{final} est apparu pendant la construction ; l'Index construit reste sous {en_cours}"
        ) from None
    return final


def construire_index(config: ConfigIndex, racine: str | Path | None = None) -> Path:
    """Construit `<racine>/index/<version>/` depuis les parquet des sources de `config`.

    La version est la date de snapshot la plus récente des sources. Lève `ArtefactExistant`
    avant toute lecture si elle existe déjà, `ConfigurationInvalide` si une source n'a
    aucun parquet.
    """
    racine = (Path(racine) if racine is not None else racine_projet()).resolve()
    version = config.version()
    dossier = dossier_index(racine)
    if (dossier / version).exists():
        raise ArtefactExistant(
            f"{dossier / version} existe déjà : un Index n'est jamais reconstruit"
        )
    for source in config.sources:  # toutes les sources présentes avant de lire quoi que ce soit
        fichiers_parquet(racine, source)
    sources_lues = [lire_source_parquet(source, racine, config) for source in config.sources]
    return ecrire_index(dossier, version, sources_lues, config)


__all__ = [
    "CHAMPS_TEXTE",
    "SourceLue",
    "construire_index",
    "dossier_parquet",
    "ecrire_index",
    "fichiers_parquet",
    "lire_source_parquet",
    "vecteur_depuis_json",
]
