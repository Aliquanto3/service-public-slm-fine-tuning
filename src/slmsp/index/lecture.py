"""Lecture de l'Index local et recherche exacte (AD-9).

`IndexLocal` implémente `VectorStore` : produit scalaire exact, par blocs de `taille_bloc`
lignes, entre la requête et les vecteurs float16 de `vectors.f16.npy` ouverts en
`numpy.memmap`. Chaque bloc est converti en float32 dans un tampon réutilisé ; le résultat
est celui de la référence `vecteurs.astype(float32) @ requete` (force brute), trié par score
décroissant puis par rang croissant (départage déterministe des ex-aequo).

Le produit matrice-vecteur passe par BLAS (sgemv) : selon le découpage en blocs et en fils,
l'ordre de sommation des 1024 produits change, et un score peut différer de la référence du
dernier bit float32 (écart relevé ≤ 3e-8). Quand les sommes partielles sont exactes, les
scores sont égaux au bit près ; sinon les rangs sont ceux de la référence hors quasi
ex-aequo (écart de score inférieur à cet arrondi).

Les passages viennent de `chunks.sqlite`, ouvert en lecture seule (`mode=ro&immutable=1`).
Ce module ne lit que l'Index : il n'importe ni pyarrow ni duckdb (fermeture runtime, AD-2).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import TracebackType
from typing import Any

import numpy as np
from numpy.typing import NDArray
from pydantic import ValidationError

from slmsp.core.canonique import sha256_fichier
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.ports import Passage
from slmsp.core.schemas.manifeste_index import ManifesteIndex
from slmsp.index.config import (
    NOM_CHUNKS,
    NOM_MANIFESTE,
    NOM_VECTEURS,
    charger_config_index,
    dossier_index,
    version_valide,
)

TAILLE_BLOC_DEFAUT = 4096
_COLONNES = "rang, chunk_id, doc_id, source, titre, url, texte, date_snapshot"


def lire_manifeste(dossier: str | Path) -> ManifesteIndex:
    """`MANIFEST.json` de l'Index `dossier` ; lève `ManifesteInvalide` s'il manque ou est faux."""
    chemin = Path(dossier) / NOM_MANIFESTE
    try:
        brut = chemin.read_bytes()
    except OSError as exc:
        raise ManifesteInvalide(
            f"{chemin} : manifeste d'Index illisible ({type(exc).__name__})"
        ) from None
    try:
        return ManifesteIndex.model_validate_json(brut)
    except ValidationError as exc:
        raise ManifesteInvalide(f"{chemin} : manifeste d'Index invalide ({exc})") from None


def candidats_top_k(scores: NDArray[np.float32], k: int) -> NDArray[np.intp]:
    """Indices (croissants) des `k` meilleurs scores d'un bloc, ex-aequo du k-ième inclus."""
    if k >= scores.shape[0]:
        return np.arange(scores.shape[0])
    negatifs = -scores
    seuil = np.partition(negatifs, k - 1)[k - 1]
    return np.flatnonzero(negatifs <= seuil)


def fusionner_top_k(
    rangs: NDArray[np.int64], scores: NDArray[np.float32], k: int
) -> tuple[NDArray[np.int64], NDArray[np.float32]]:
    """Les `k` premiers candidats par score décroissant puis rang croissant."""
    ordre = np.lexsort((rangs, -scores))[:k]
    return rangs[ordre], scores[ordre]


class IndexLocal:
    """Index local ouvert en lecture seule ; implémente `VectorStore`."""

    def __init__(self, dossier: str | Path, *, taille_bloc: int = TAILLE_BLOC_DEFAUT) -> None:
        if isinstance(taille_bloc, bool) or not isinstance(taille_bloc, int) or taille_bloc <= 0:
            raise ValueError(f"taille_bloc doit être un entier > 0 (reçu {taille_bloc!r})")
        self.dossier = Path(dossier).resolve()
        self.taille_bloc = taille_bloc
        self.manifeste = lire_manifeste(self.dossier)
        if self.manifeste.version != self.dossier.name:
            raise ManifesteInvalide(
                f"{self.dossier} : version du manifeste ({self.manifeste.version}) "
                "différente du nom du dossier"
            )
        manquants = {NOM_VECTEURS, NOM_CHUNKS} - self.manifeste.fichiers.keys()
        if manquants:
            raise ManifesteInvalide(
                f"{self.dossier} : empreinte absente du manifeste pour "
                f"{', '.join(sorted(manquants))}"
            )
        self._vecteurs: np.ndarray | None = self._ouvrir_vecteurs()
        self._connexion: sqlite3.Connection | None = None
        try:
            self._connexion = self._ouvrir_chunks()
        except BaseException:
            self._vecteurs = None
            raise

    # --- Ouverture -------------------------------------------------------------------

    def _ouvrir_vecteurs(self) -> np.ndarray:
        chemin = self.dossier / NOM_VECTEURS
        try:
            vecteurs = np.load(chemin, mmap_mode="r", allow_pickle=False)
        except (OSError, ValueError) as exc:
            raise ManifesteInvalide(
                f"{chemin} : vecteurs illisibles ({type(exc).__name__} : {exc})"
            ) from None
        attendu = (self.manifeste.nb_chunks, self.manifeste.dimension)
        if vecteurs.dtype != np.dtype("<f2") or vecteurs.shape != attendu:
            raise ManifesteInvalide(
                f"{chemin} : forme {vecteurs.shape} et type {vecteurs.dtype} incohérents avec "
                f"le manifeste ({attendu}, float16)"
            )
        return vecteurs

    def _ouvrir_chunks(self) -> sqlite3.Connection:
        chemin = self.dossier / NOM_CHUNKS
        if not chemin.is_file():
            raise ManifesteInvalide(f"{chemin} : base des chunks absente")
        try:
            connexion = sqlite3.connect(
                f"{chemin.as_uri()}?mode=ro&immutable=1", uri=True, check_same_thread=False
            )
        except sqlite3.Error as exc:
            raise ManifesteInvalide(f"{chemin} : base des chunks illisible ({exc})") from None
        try:
            nombre, minimum, maximum = connexion.execute(
                "SELECT COUNT(*), MIN(rang), MAX(rang) FROM chunks"
            ).fetchone()
        except sqlite3.Error as exc:
            connexion.close()
            raise ManifesteInvalide(f"{chemin} : base des chunks illisible ({exc})") from None
        n = self.manifeste.nb_chunks
        if (nombre, minimum, maximum) != (n, 0, n - 1):
            connexion.close()
            raise ManifesteInvalide(
                f"{chemin} : {nombre} ligne(s) (rangs {minimum} à {maximum}), "
                f"{n} attendue(s) d'après le manifeste"
            )
        return connexion

    # --- Accès -----------------------------------------------------------------------

    @property
    def version(self) -> str:
        return self.manifeste.version

    @property
    def date_snapshot(self) -> str:
        """Date du snapshot, `AAAA-MM-JJ`."""
        return self.manifeste.date_snapshot.isoformat()

    @property
    def nb_chunks(self) -> int:
        return self.manifeste.nb_chunks

    @property
    def dimension(self) -> int:
        return self.manifeste.dimension

    def _ouvert(self) -> tuple[np.ndarray, sqlite3.Connection]:
        if self._vecteurs is None or self._connexion is None:
            raise ManifesteInvalide(f"{self.dossier} : Index fermé")
        return self._vecteurs, self._connexion

    def vecteurs(self) -> np.ndarray:
        """Vue mappée (lecture seule) des vecteurs float16, `(nb_chunks, dimension)`."""
        return self._ouvert()[0]

    def verifier(self) -> None:
        """Recalcule le SHA-256 des deux fichiers ; lève `ManifesteInvalide` s'il diffère."""
        for nom in (NOM_VECTEURS, NOM_CHUNKS):
            chemin = self.dossier / nom
            try:
                empreinte = sha256_fichier(chemin)
            except OSError as exc:
                raise ManifesteInvalide(
                    f"{chemin} : fichier illisible ({type(exc).__name__})"
                ) from None
            if empreinte != self.manifeste.fichiers[nom]:
                raise ManifesteInvalide(
                    f"{chemin} : SHA-256 {empreinte} différent du manifeste "
                    f"({self.manifeste.fichiers[nom]})"
                )

    # --- Recherche -------------------------------------------------------------------

    def _requete(self, vecteur: Any) -> NDArray[np.float32]:
        try:
            requete = np.asarray(vecteur, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"vecteur de requête invalide : {exc}") from None
        if requete.ndim == 2 and requete.shape[0] == 1:
            requete = requete[0]
        if requete.shape != (self.dimension,):
            raise ValueError(
                f"vecteur de requête de forme {requete.shape}, ({self.dimension},) attendue"
            )
        if not np.all(np.isfinite(requete)):
            raise ValueError("vecteur de requête non fini (NaN ou infini)")
        return np.ascontiguousarray(requete)

    def classer(self, vecteur: Any, k: int) -> tuple[NDArray[np.int64], NDArray[np.float32]]:
        """Rangs et scores des `k` vecteurs les plus proches (score décroissant, rang croissant).

        Lève `ValueError` pour `k` ≤ 0, une dimension fausse ou une valeur non finie.
        """
        if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k <= 0:
            raise ValueError(f"k doit être un entier > 0 (reçu {k!r})")
        requete = self._requete(vecteur)
        vecteurs, _ = self._ouvert()
        n = vecteurs.shape[0]
        k = min(int(k), n)
        taille = min(self.taille_bloc, n)
        # Tampon propre à l'appel : deux fils peuvent chercher en même temps.
        tampon_bloc = np.empty((taille, self.dimension), dtype=np.float32)
        rangs_candidats: list[NDArray[np.int64]] = []
        scores_candidats: list[NDArray[np.float32]] = []
        for debut in range(0, n, self.taille_bloc):
            fin = min(debut + self.taille_bloc, n)
            tampon = tampon_bloc[: fin - debut]
            np.copyto(tampon, vecteurs[debut:fin])
            scores = tampon @ requete
            retenus = candidats_top_k(scores, k)
            rangs_candidats.append(retenus.astype(np.int64) + debut)
            scores_candidats.append(scores[retenus])
        return fusionner_top_k(np.concatenate(rangs_candidats), np.concatenate(scores_candidats), k)

    def passages(self, rangs: Any, scores: Any) -> list[Passage]:
        """`Passage` de chaque rang, dans l'ordre donné, avec son score."""
        _, connexion = self._ouvert()
        liste = [int(rang) for rang in rangs]
        if not liste:
            return []
        marques = ",".join("?" * len(liste))
        lignes = connexion.execute(
            f"SELECT {_COLONNES} FROM chunks WHERE rang IN ({marques})", liste
        ).fetchall()
        par_rang = {ligne[0]: ligne for ligne in lignes}
        resultat = []
        for rang, score in zip(liste, scores, strict=True):
            ligne = par_rang.get(rang)
            if ligne is None:
                raise ManifesteInvalide(f"{self.dossier / NOM_CHUNKS} : rang {rang} absent")
            _, chunk_id, doc_id, source, titre, url, texte, date_snapshot = ligne
            resultat.append(
                Passage(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    source=source,
                    titre=titre,
                    url=url,
                    texte=texte,
                    date_snapshot=date_snapshot,
                    score=float(score),
                )
            )
        return resultat

    def rechercher(self, vecteur: NDArray[np.float32], k: int) -> list[Passage]:
        """Les `k` passages les plus proches, par score décroissant puis rang croissant."""
        rangs, scores = self.classer(vecteur, k)
        return self.passages(rangs, scores)

    # --- Fermeture -------------------------------------------------------------------

    def fermer(self) -> None:
        """Ferme la base et libère la vue mappée (idempotent)."""
        if self._connexion is not None:
            self._connexion.close()
        self._connexion = None
        self._vecteurs = None

    def __enter__(self) -> IndexLocal:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.fermer()

    def __repr__(self) -> str:
        return f"IndexLocal({self.dossier})"


def versions_disponibles(racine: str | Path | None = None) -> list[str]:
    """Versions `AAAAMMJJ` présentes sous `<racine>/index/`, dans l'ordre croissant.

    Les dossiers de construction en cours (`.<version>.en-cours-…`) sont ignorés.
    """
    dossier = dossier_index(racine)
    if not dossier.is_dir():
        return []
    return sorted(
        entree.name
        for entree in dossier.iterdir()
        if entree.is_dir() and version_valide(entree.name)
    )


def ouvrir_index(
    racine: str | Path | None = None,
    version: str | None = None,
    *,
    taille_bloc: int | None = None,
) -> IndexLocal:
    """Ouvre la version `version` de l'Index (la plus récente par défaut).

    `taille_bloc` vaut celle de `config/index.toml` par défaut. Lève `ManifesteInvalide`
    si aucune version n'existe, si la version demandée est inconnue ou si l'Index est
    incohérent.
    """
    dossier = dossier_index(racine)
    if version is None:
        versions = versions_disponibles(racine)
        if not versions:
            raise ManifesteInvalide(f"aucun Index sous {dossier} : lancer `slmsp index build`")
        version = versions[-1]
    elif not version_valide(version) or not (dossier / version).is_dir():
        connues = ", ".join(versions_disponibles(racine)) or "aucune"
        raise ManifesteInvalide(
            f"version d'Index inconnue : {version!r} sous {dossier} (connues : {connues})"
        )
    if taille_bloc is None:
        taille_bloc = charger_config_index().taille_bloc
    return IndexLocal(dossier / version, taille_bloc=taille_bloc)


__all__ = [
    "IndexLocal",
    "TAILLE_BLOC_DEFAUT",
    "candidats_top_k",
    "fusionner_top_k",
    "lire_manifeste",
    "ouvrir_index",
    "versions_disponibles",
]
