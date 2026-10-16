"""Chargement de la configuration TOML et environnement imposé (AD-22, AD-4).

Toute valeur réglable vit dans un fichier TOML de `config/`, lu par `tomllib` et validé
par un modèle pydantic dérivé de `ModeleConfig` (`extra="forbid"`).

`SLMSP_MODELS_DIR` permet à une copie de travail (worktree) de pointer le dossier
`models/` du dépôt principal.
"""

from __future__ import annotations

import os
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, get_args

from pydantic import BaseModel, ConfigDict, ValidationError

from slmsp.core.erreurs import ConfigurationInvalide

ENV_IMPOSE: Final[Mapping[str, str]] = MappingProxyType(
    {
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "WANDB_MODE": "disabled",
        "DO_NOT_TRACK": "1",
    }
)
"""Variables de télémétrie imposées à toute commande et à tout sous-processus (AD-4)."""

_SECRETS_EXACTS = frozenset({"API_KEY", "HF_TOKEN", "HF_TOKEN_PATH", "HUGGING_FACE_HUB_TOKEN"})
_SUFFIXES_SECRET = ("_API_KEY", "_TOKEN", "_KEY", "_PASSWORD")


def racine_projet() -> Path:
    """Racine du projet : `SLMSP_RACINE`, sinon l'installation si le processus est gelé.

    Ordre : variable `SLMSP_RACINE` ; exécutable gelé (`sys.frozen`), où la racine est
    `sys._MEIPASS` (ou le dossier de l'exécutable) et porte `config/`, `vendor/`, `models/` ;
    sinon le dépôt (installation éditable d'uv : `src/slmsp/core/config.py`). En lecture
    seule pour un processus gelé : les écritures passent par `racine_ecriture()`.
    """
    valeur = os.environ.get("SLMSP_RACINE", "").strip()
    if valeur:
        return Path(valeur).expanduser().resolve()
    if processus_gele():
        meipass = getattr(sys, "_MEIPASS", None)
        base = Path(meipass) if meipass else Path(sys.executable).parent
        return base.resolve()
    return Path(__file__).resolve().parents[3]


def processus_gele() -> bool:
    """Vrai dans un exécutable PyInstaller (`sys.frozen`)."""
    return bool(getattr(sys, "frozen", False))


def etendre_chemin(valeur: str) -> Path:
    """`valeur` avec `%VAR%`, `$VAR` et `~` étendus, en chemin absolu résolu.

    Lève `ConfigurationInvalide` si une variable reste non résolue ou si le chemin obtenu
    n'est pas absolu (aucune écriture ne doit partir du dossier courant).
    """
    etendu = os.path.expanduser(os.path.expandvars(valeur))
    if "%" in etendu or "$" in etendu:
        raise ConfigurationInvalide(f"chemin {valeur!r} : variable d'environnement non définie")
    chemin = Path(etendu)
    if not chemin.is_absolute():
        raise ConfigurationInvalide(f"chemin {valeur!r} : chemin absolu attendu après expansion")
    return chemin.resolve()


def dossier_donnees_application() -> Path:
    """`dossier_donnees` de `config/application.toml`, variables d'environnement étendues."""
    from slmsp.core.schemas.config_application import charger_config_application

    return charger_config_application().chemin_donnees()


def racine_ecriture() -> Path:
    """Racine des écritures (`runs/`, Index construit) : jamais les ressources gelées (AD-23).

    Ordre : `SLMSP_RACINE` ; processus gelé : dossier de données de l'application (les
    ressources de `racine_projet()`, sous `sys._MEIPASS`, sont en lecture seule) ; sinon le
    dépôt, comme `racine_projet()`.
    """
    valeur = os.environ.get("SLMSP_RACINE", "").strip()
    if valeur:
        return Path(valeur).expanduser().resolve()
    if processus_gele():
        return dossier_donnees_application()
    return racine_projet()


def dossier_modeles() -> Path:
    """Dossier des poids : `SLMSP_MODELS_DIR` s'il est défini, sinon `<racine>/models`."""
    valeur = os.environ.get("SLMSP_MODELS_DIR", "").strip()
    dossier = Path(valeur).expanduser() if valeur else racine_projet() / "models"
    return dossier.resolve()


class ModeleConfig(BaseModel):
    """Base des modèles de configuration : toute clé inconnue est refusée."""

    model_config = ConfigDict(extra="forbid")


def _modeles_dans(annotation: Any) -> list[type[BaseModel]]:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]
    modeles: list[type[BaseModel]] = []
    for argument in get_args(annotation):
        modeles.extend(_modeles_dans(argument))
    return modeles


def _verifier_strict(modele: type[BaseModel], vus: set[type[BaseModel]]) -> None:
    if modele in vus:
        return
    vus.add(modele)
    if modele.model_config.get("extra") != "forbid":
        raise TypeError(
            f"{modele.__qualname__} doit refuser les clés inconnues : "
            'dériver de ModeleConfig ou fixer extra="forbid"'
        )
    for champ in modele.model_fields.values():
        for imbrique in _modeles_dans(champ.annotation):
            _verifier_strict(imbrique, vus)


def charger_toml[M: BaseModel](chemin: str | Path, modele: type[M]) -> M:
    """Lit `chemin` par `tomllib` et le valide par `modele`.

    Lève `TypeError` si `modele` (ou un modèle imbriqué) accepte les clés inconnues, et
    `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme. Le message
    cite le fichier et chaque clé fautive, jamais la valeur saisie.
    """
    if not (isinstance(modele, type) and issubclass(modele, BaseModel)):
        raise TypeError(f"{modele!r} n'est pas un modèle pydantic")
    _verifier_strict(modele, set())
    chemin = Path(chemin)
    try:
        with chemin.open("rb") as flux:
            donnees = tomllib.load(flux)
    except OSError as exc:
        raise ConfigurationInvalide(
            f"{chemin} : fichier de configuration illisible ({type(exc).__name__})"
        ) from None
    except UnicodeDecodeError:
        raise ConfigurationInvalide(f"{chemin} : TOML invalide : fichier non UTF-8") from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationInvalide(f"{chemin} : TOML invalide : {exc}") from None
    try:
        return modele.model_validate(donnees)
    except ValidationError as exc:
        lignes = []
        for erreur in exc.errors(include_url=False, include_input=False, include_context=False):
            cle = ".".join(str(partie) for partie in erreur["loc"]) or "(racine)"
            lignes.append(f"{chemin} : clé « {cle} » : {erreur['msg']}")
        raise ConfigurationInvalide("\n".join(lignes)) from None


def appliquer_environnement_impose() -> None:
    """Pose les variables de télémétrie de `ENV_IMPOSE` dans `os.environ`."""
    os.environ.update(ENV_IMPOSE)


def _est_secret(nom: str) -> bool:
    nom = nom.upper()
    return (
        nom in _SECRETS_EXACTS
        or nom.endswith(_SUFFIXES_SECRET)
        or "SECRET" in nom
        or "PASSWORD" in nom
    )


def env_sous_processus(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Environnement d'un sous-processus : sans secret, télémétrie coupée, `HF_HOME` fixé.

    Retire, sans tenir compte de la casse, `API_KEY`, `*_API_KEY`, `*_TOKEN` (dont
    `HF_TOKEN`), `HF_TOKEN_PATH`, tout nom contenant `SECRET` et les `WEBVIEW2_*` (réglages
    de la WebView de l'application, sans objet pour un serveur), puis pose `ENV_IMPOSE`
    et `HF_HOME=<models>/.cache-hf` en chemin absolu. `base` vaut `os.environ` par défaut
    et n'est jamais modifié.
    """
    source = os.environ if base is None else base
    imposes = {**ENV_IMPOSE, "HF_HOME": str(dossier_modeles() / ".cache-hf")}
    remplaces = {nom.upper() for nom in imposes}
    env = {
        nom: valeur
        for nom, valeur in source.items()
        if not _est_secret(nom)
        and nom.upper() not in remplaces
        and not nom.upper().startswith("WEBVIEW2_")
    }
    env.update(imposes)
    return env
