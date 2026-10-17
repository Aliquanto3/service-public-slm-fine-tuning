"""`EmbedderPort` sur `llama-server --embedding` : `/v1/embeddings` par `net.client_local`.

Vecteurs float32 de `dimension` (1024 pour BGE-M3), renormalisés L2 (le serveur les
normalise déjà : la renormalisation absorbe l'arrondi). Les textes partent par lots de
`taille_lot` ; un texte plus long que le contexte (8192 tokens) est tronqué à sa fin.
Les réponses sont remises dans l'ordre par leur `index`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final

import numpy as np
from numpy.typing import NDArray

from slmsp.inference.processus import ErreurInference
from slmsp.net import client_local

DIMENSION: Final = 1024
TAILLE_LOT: Final = 64
TAILLE_EXTRAIT: Final = 500
CONTEXTE_MAX: Final = 8192
"""Contexte de BGE-M3 (= `-b`/`-ub` du serveur, voir `ServeurLlama.arguments`)."""
MARGE_TOKENS: Final = 16
"""Réserve pour les jetons spéciaux ajoutés par le serveur."""


class EmbedderLlama:
    """Vectorisation par un `llama-server` d'embedding sur `127.0.0.1:<port>`."""

    def __init__(
        self,
        port: int,
        *,
        dimension: int = DIMENSION,
        taille_lot: int = TAILLE_LOT,
        contexte_max: int = CONTEXTE_MAX,
        transport_interne: Any = None,
    ) -> None:
        if dimension <= 0 or taille_lot <= 0:
            raise ValueError("dimension et taille_lot doivent être strictement positives")
        self.port = port
        self._dimension = dimension
        self.taille_lot = taille_lot
        self.contexte_max = contexte_max
        self._http = client_local(port, transport_interne=transport_interne)
        self._url = f"http://127.0.0.1:{port}/v1/embeddings"

    @property
    def dimension(self) -> int:
        return self._dimension

    def fermer(self) -> None:
        self._http.close()

    def __enter__(self) -> EmbedderLlama:
        return self

    def __exit__(self, *exc: object) -> None:
        self.fermer()

    def _tronquer(self, texte: str) -> str:
        """Borne `texte` à `contexte_max` tokens (début conservé), sinon le serveur répond 500.

        Un token fait au moins un caractère : un texte plus court que la limite ne coûte
        aucun appel. Sinon `/tokenize` compte, puis on coupe au prorata et on revérifie.
        """
        limite = self.contexte_max - MARGE_TOKENS
        for _ in range(8):
            if len(texte) <= limite:
                return texte
            reponse = self._http.post(
                f"http://127.0.0.1:{self.port}/tokenize", json={"content": texte}
            )
            tokens = reponse.json().get("tokens") if reponse.status_code == 200 else None
            if not isinstance(tokens, list):
                raise ErreurInference(f"POST /tokenize : HTTP {reponse.status_code}")
            if len(tokens) <= limite:
                return texte
            texte = texte[: max(1, int(len(texte) * limite / len(tokens) * 0.98))]
        return texte[:limite]

    def _lot(self, textes: list[str]) -> NDArray[np.float32]:
        reponse = self._http.post(self._url, json={"input": textes})
        if reponse.status_code != 200:
            raise ErreurInference(
                f"POST /v1/embeddings : HTTP {reponse.status_code} : "
                f"{reponse.text[:TAILLE_EXTRAIT]}"
            )
        donnees = reponse.json().get("data")
        if not isinstance(donnees, list) or len(donnees) != len(textes):
            raise ErreurInference(
                f"/v1/embeddings : {len(textes)} vecteurs attendus, réponse inattendue"
            )
        try:
            tries = sorted(donnees, key=lambda element: int(element["index"]))
            matrice = np.asarray([element["embedding"] for element in tries], dtype=np.float32)
        except (KeyError, TypeError, ValueError) as exc:
            raise ErreurInference(f"/v1/embeddings : réponse illisible ({exc})") from None
        if [int(element["index"]) for element in tries] != list(range(len(textes))):
            raise ErreurInference("/v1/embeddings : index de réponse incohérents")
        if matrice.ndim != 2 or matrice.shape[1] != self._dimension:
            raise ErreurInference(
                f"/v1/embeddings : dimension {matrice.shape[1:] or '?'} reçue, "
                f"{self._dimension} attendue"
            )
        normes = np.linalg.norm(matrice, axis=1, keepdims=True)
        if not np.all(np.isfinite(normes)) or np.any(normes == 0):
            raise ErreurInference("/v1/embeddings : vecteur nul ou non fini")
        return (matrice / normes).astype(np.float32, copy=False)

    def vectoriser(self, textes: Sequence[str]) -> NDArray[np.float32]:
        """Matrice `(len(textes), dimension)` float32 de norme 1 ; liste vide : `(0, d)`."""
        if isinstance(textes, str):
            raise TypeError("vectoriser attend une séquence de textes, pas une chaîne")
        textes = list(textes)
        if not all(isinstance(texte, str) for texte in textes):
            raise TypeError("vectoriser attend des chaînes")
        if not textes:
            return np.zeros((0, self._dimension), dtype=np.float32)
        textes = [self._tronquer(texte) for texte in textes]
        lots = [
            self._lot(textes[debut : debut + self.taille_lot])
            for debut in range(0, len(textes), self.taille_lot)
        ]
        return np.concatenate(lots, axis=0)


__all__ = ["DIMENSION", "EmbedderLlama"]
