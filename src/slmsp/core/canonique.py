"""JSON canonique et empreintes SHA-256 (convention « Fichiers de données » du spine).

JSON canonique : clés triées, séparateurs compacts, `ensure_ascii=False`, octets UTF-8 ;
`NaN` et les infinis sont refusés. Empreintes : SHA-256 en hexadécimal minuscule.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

TAILLE_BLOC = 1024 * 1024
"""Taille des blocs lus par `sha256_fichier` (1 Mio)."""


def json_canonique(obj: Any) -> bytes:
    """Sérialise `obj` en JSON canonique, en octets UTF-8.

    Lève `ValueError` pour `NaN` ou un infini, `TypeError` pour un objet non sérialisable.
    """
    texte = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return texte.encode("utf-8")


def sha256_hex(donnees: bytes | str) -> str:
    """Empreinte SHA-256 en hexadécimal minuscule (une chaîne est encodée en UTF-8)."""
    if isinstance(donnees, str):
        donnees = donnees.encode("utf-8")
    return hashlib.sha256(donnees).hexdigest()


def sha256_fichier(chemin: str | Path, taille_bloc: int = TAILLE_BLOC) -> str:
    """Empreinte SHA-256 d'un fichier, lu en flux par blocs de `taille_bloc` octets."""
    if taille_bloc <= 0:
        raise ValueError("taille_bloc doit être strictement positive")
    empreinte = hashlib.sha256()
    with Path(chemin).open("rb") as flux:
        while bloc := flux.read(taille_bloc):
            empreinte.update(bloc)
    return empreinte.hexdigest()
