"""Modèle actif de l'application (story 12.15) : réglage `modele` si valide, sinon le défaut."""

from __future__ import annotations

import logging
from pathlib import Path, PurePosixPath
from typing import Any, Final

from slmsp.core.config import dossier_modeles
from slmsp.core.schemas.config_application import ConfigApplication

LOGGER: Final = logging.getLogger("slmsp.app.modele_actif")


def gguf_present(slug: str, dossier: Path | None = None) -> bool:
    """Vrai si le GGUF de `slug` est présent dans l'installation (`models/<slug>/gguf/`)."""
    from slmsp.inference.serveur import charger_config_modele

    try:
        gguf = charger_config_modele(slug).gguf
    except Exception:
        return False
    if gguf is None:
        return False
    base = dossier if dossier is not None else dossier_modeles()
    return (base / slug / "gguf" / PurePosixPath(gguf.fichier).name).is_file()


def resoudre_modele_actif(
    config: ConfigApplication, choix: Any, dossier: Path | None = None
) -> str:
    """`choix` (réglage enregistré) s'il est embarqué et présent ; sinon `config.modele`.

    Un réglage invalide est ignoré et consigné, sans exception.
    """
    if choix is None or choix == config.modele:
        return config.modele
    if not isinstance(choix, str) or choix not in config.modeles_embarques:
        LOGGER.warning("réglage de modèle ignoré : hors des modèles embarqués")
        return config.modele
    if not gguf_present(choix, dossier):
        LOGGER.warning("réglage de modèle ignoré : GGUF de « %s » absent", choix)
        return config.modele
    return choix
