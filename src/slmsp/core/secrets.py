"""Lecture des secrets (AD-22, D2).

Les secrets sont lus par `dotenv_values` dans le fichier `.env`, jamais injectés dans
`os.environ`, et rendus en `SecretStr` (repr masqué). Ils ne sont remis qu'aux fabriques
de clients. `SLMSP_ENV_FILE` permet à une copie de travail (worktree) de pointer le
`.env` du dépôt principal. Aucun message d'erreur ne cite une valeur.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import SecretStr

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import SecretManquant


def fichier_env() -> Path:
    """Fichier des secrets : `SLMSP_ENV_FILE` s'il est défini, sinon `<racine>/.env`."""
    valeur = os.environ.get("SLMSP_ENV_FILE", "").strip()
    return Path(valeur).expanduser().resolve() if valeur else racine_projet() / ".env"


def secret(nom: str, fichier: str | Path | None = None) -> SecretStr:
    """Valeur du secret `nom` lue dans `fichier` (par défaut `fichier_env()`).

    Lève `SecretManquant` si le fichier est absent ou si la clé est absente ou vide ; le
    message cite le nom du secret et le fichier, jamais une valeur.
    """
    chemin = Path(fichier) if fichier is not None else fichier_env()
    if not chemin.is_file():
        raise SecretManquant(f"secret « {nom} » introuvable : fichier {chemin} absent")
    try:
        valeurs = dotenv_values(chemin, interpolate=False, encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SecretManquant(
            f"secret « {nom} » illisible : fichier {chemin} ({type(exc).__name__})"
        ) from None
    valeur = valeurs.get(nom)
    if valeur is None or not valeur.strip():
        raise SecretManquant(f"secret « {nom} » absent ou vide dans {chemin}")
    return SecretStr(valeur)
