"""Modèle actif de l'application (story 12.15) : réglage `modele` si valide, sinon le défaut."""

from __future__ import annotations

import logging
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Final

from slmsp.core.config import dossier_modeles
from slmsp.core.schemas.config_application import ConfigApplication

if TYPE_CHECKING:
    from slmsp.core.schemas.config_modele import ConfigModele

LOGGER: Final = logging.getLogger("slmsp.app.modele_actif")
CHAT_TEMPLATE: Final = "chat_template.jinja"


def fichiers_requis(config: ConfigModele) -> list[tuple[str, str | None]]:
    """Fichiers exigés par `ServeurLlama` sous `models/<slug>/` : `(chemin relatif, SHA-256)`.

    GGUF de génération, et `chat_template.jinja` si `chat_template_force` (serveur.py le passe
    par `--chat-template-file`). Liste vide sans section `[gguf]`.
    """
    if config.gguf is None:
        return []
    requis: list[tuple[str, str | None]] = [
        (f"gguf/{PurePosixPath(config.gguf.fichier).name}", config.gguf.sha256)
    ]
    if config.chat_template_force:
        requis.append((CHAT_TEMPLATE, config.sha256_fichiers.get(CHAT_TEMPLATE)))
    return requis


def gguf_present(slug: str, dossier: Path | None = None) -> bool:
    """Vrai si tous les fichiers requis de `slug` (GGUF, template forcé) sont installés."""
    from slmsp.inference.serveur import charger_config_modele

    try:
        requis = fichiers_requis(charger_config_modele(slug))
    except Exception:
        return False
    base = dossier if dossier is not None else dossier_modeles()
    return bool(requis) and all((base / slug / rel).is_file() for rel, _ in requis)


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
        LOGGER.warning("réglage de modèle ignoré : fichiers de « %s » absents", choix)
        return config.modele
    return choix
