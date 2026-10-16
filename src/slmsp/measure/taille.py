"""Taille installée de l'Assistant (FR-26, NFR-6) : GGUF, Index et binaires llama.cpp."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path


def taille_octets(chemin: Path) -> int:
    """Taille d'un fichier ou d'un dossier (récursive) ; `FileNotFoundError` s'il manque."""
    if chemin.is_file():
        return chemin.stat().st_size
    if chemin.is_dir():
        return sum(f.stat().st_size for f in chemin.rglob("*") if f.is_file())
    raise FileNotFoundError(f"composant à mesurer introuvable : {chemin}")


def tailles_composants(composants: Mapping[str, Path]) -> dict[str, int]:
    """Taille de chaque composant nommé (`gguf-generation`, `index`, `binaires`…)."""
    return {nom: taille_octets(chemin) for nom, chemin in composants.items()}
