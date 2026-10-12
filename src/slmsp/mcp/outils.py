"""Outils data.gouv exposés au modèle, figés dans `config/outils-mcp.toml` (AD-8).

Les mêmes schémas servent au Harnais, au générateur Mistral et à l'entraînement. Tout appel
est validé par `jsonschema` avant envoi (`valider_appel`) ; le `tools/list` du serveur est
comparé, outil par outil, aux empreintes figées (`comparer_schema_serveur`).
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import Field, field_validator

from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.erreurs import AppelNonConforme, SchemaOutilModifie
from slmsp.core.schemas import Sha256

OUTILS_AUTORISES: Final[tuple[str, ...]] = (
    "search_datasets",
    "get_dataset_info",
    "list_dataset_resources",
    "query_resource_data",
    "get_resource_info",
)
"""Seuls outils du serveur MCP data.gouv exposés au modèle."""

NOM_CONFIG: Final = "outils-mcp.toml"


class OutilFige(ModeleConfig):
    """Un outil exposé : description du serveur et schéma des paramètres figé."""

    nom: str
    description: str
    sha256_schema_serveur: Sha256
    parametres: dict[str, Any]

    @field_validator("nom")
    @classmethod
    def _nom_autorise(cls, nom: str) -> str:
        if nom not in OUTILS_AUTORISES:
            raise ValueError(f"outil non autorisé (autorisés : {', '.join(OUTILS_AUTORISES)})")
        return nom

    @field_validator("parametres")
    @classmethod
    def _schema_valide(cls, parametres: dict[str, Any]) -> dict[str, Any]:
        try:
            Draft202012Validator.check_schema(parametres)
        except SchemaError as exc:
            chemin = "/".join(str(partie) for partie in exc.path) or "(racine)"
            raise ValueError(f"JSON Schema invalide en {chemin}") from None
        return parametres


class ConfigOutilsMcp(ModeleConfig):
    """Contenu de `config/outils-mcp.toml`."""

    schema_version: Literal[1]
    source: str
    tools_list_sha256: Sha256
    texte_reponse_vide: str = Field(min_length=1)
    """Texte de la réponse vide normalisée du Bac à sable (AD-10)."""
    outils: list[OutilFige] = Field(min_length=1, max_length=len(OUTILS_AUTORISES))

    @field_validator("outils")
    @classmethod
    def _noms_uniques(cls, outils: list[OutilFige]) -> list[OutilFige]:
        noms = [outil.nom for outil in outils]
        doublons = sorted({nom for nom in noms if noms.count(nom) > 1})
        if doublons:
            raise ValueError(f"outil en double : {', '.join(doublons)}")
        return outils


_CACHE: dict[tuple[str, int, int], tuple[ConfigOutilsMcp, dict[str, Draft202012Validator]]] = {}


def _chemin_config(chemin: str | Path | None) -> Path:
    return Path(chemin) if chemin is not None else racine_projet() / "config" / NOM_CONFIG


def _charger(chemin: str | Path | None) -> tuple[ConfigOutilsMcp, dict[str, Draft202012Validator]]:
    fichier = _chemin_config(chemin)
    try:
        etat = fichier.stat()
        cle = (str(fichier.resolve()), etat.st_mtime_ns, etat.st_size)
    except OSError:
        cle = None
    if cle is not None and cle in _CACHE:
        return _CACHE[cle]
    config = charger_toml(fichier, ConfigOutilsMcp)
    validateurs = {outil.nom: Draft202012Validator(outil.parametres) for outil in config.outils}
    if cle is not None:
        _CACHE[cle] = (config, validateurs)
    return config, validateurs


def charger_config(chemin: str | Path | None = None) -> ConfigOutilsMcp:
    """Config des outils figés (`config/outils-mcp.toml` par défaut).

    Lève `ConfigurationInvalide` si le fichier est absent ou non conforme.
    """
    return _charger(chemin)[0].model_copy(deep=True)


def charger_outils(chemin: str | Path | None = None) -> list[dict[str, Any]]:
    """Outils figés au format `tools` d'OpenAI (copies indépendantes à chaque appel)."""
    config, _ = _charger(chemin)
    return [
        {
            "type": "function",
            "function": {
                "name": outil.nom,
                "description": outil.description,
                "parameters": copy.deepcopy(outil.parametres),
            },
        }
        for outil in config.outils
    ]


def _refus(nom: Any, details: list[str]) -> AppelNonConforme:
    erreur = AppelNonConforme(f"appel « {nom} » non conforme : " + " ; ".join(details))
    erreur.nom = nom if isinstance(nom, str) else None  # type: ignore[attr-defined]
    erreur.details = details  # type: ignore[attr-defined]
    return erreur


def valider_appel(
    nom: str, arguments: Mapping[str, Any], *, chemin: str | Path | None = None
) -> None:
    """Vérifie un appel d'outil avant son envoi.

    Lève `AppelNonConforme` (attributs `nom` et `details`, liste de chaînes) si l'outil
    n'est pas exposé, si `arguments` n'est pas un objet ou s'il viole le schéma figé.
    """
    _, validateurs = _charger(chemin)
    validateur = validateurs.get(nom) if isinstance(nom, str) else None
    if validateur is None:
        raise _refus(nom, [f"outil non exposé (exposés : {', '.join(validateurs)})"])
    if not isinstance(arguments, Mapping):
        nature = type(arguments).__name__
        raise _refus(nom, [f"(racine) : objet JSON attendu pour les arguments (reçu {nature})"])
    erreurs = sorted(
        validateur.iter_errors(dict(arguments)),
        key=lambda e: ([str(p) for p in e.absolute_path], e.message),
    )
    if erreurs:
        details = [
            f"{'/'.join(str(p) for p in erreur.absolute_path) or '(racine)'} : {erreur.message}"
            for erreur in erreurs
        ]
        raise _refus(nom, details)


def comparer_schema_serveur(
    tools: Sequence[Mapping[str, Any]], *, chemin: str | Path | None = None
) -> None:
    """Compare le `result.tools` d'un `tools/list` du serveur aux outils figés.

    Les outils du serveur non exposés sont ignorés. Lève `SchemaOutilModifie` (attribut
    `ecarts`, tuple de chaînes) si un outil exposé est absent du serveur ou si son
    `inputSchema` n'a plus l'empreinte figée.
    """
    config, _ = _charger(chemin)
    serveur: dict[str, Any] = {}
    for outil in tools:
        if isinstance(outil, Mapping) and isinstance(outil.get("name"), str):
            serveur.setdefault(outil["name"], outil)
    ecarts: list[str] = []
    for fige in config.outils:
        outil = serveur.get(fige.nom)
        if outil is None:
            ecarts.append(f"{fige.nom} : absent du serveur")
            continue
        try:
            empreinte = sha256_hex(json_canonique(outil.get("inputSchema")))
        except (TypeError, ValueError):
            empreinte = None
        if empreinte != fige.sha256_schema_serveur:
            ecarts.append(f"{fige.nom} : schéma modifié")
    if ecarts:
        erreur = SchemaOutilModifie("schéma des outils MCP modifié : " + " ; ".join(ecarts))
        erreur.ecarts = tuple(ecarts)  # type: ignore[attr-defined]
        raise erreur
