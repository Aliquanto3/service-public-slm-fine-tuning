"""Configuration de la passerelle : `config/reseau.toml` et `config/liste-blanche.toml` (AD-4).

`reseau.toml` porte les délais, la sonde du Mode et les règles des profils `outillage` et
`aucun` ; `liste-blanche.toml` porte les hôtes du profil `assistant`. Les noms d'hôte sont
validés (ni adresse IP, ni joker) et normalisés à la lecture.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, field_validator, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.net.profils import analyser_url, est_adresse_ip, normaliser_hote

NOM_RESEAU = "reseau.toml"
NOM_LISTE_BLANCHE = "liste-blanche.toml"

Methode = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

_LABEL = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")


def _valider_hote(valeur: str) -> str:
    hote = normaliser_hote(valeur)
    if not hote or len(hote) > 253:
        raise ValueError("nom d'hôte vide ou trop long")
    if est_adresse_ip(hote):
        raise ValueError("adresse IP refusée : seul un nom d'hôte est permis")
    if not all(_LABEL.match(label) for label in hote.split(".")):
        raise ValueError("nom d'hôte invalide (joker, caractère ou label interdit)")
    return hote


Hote = Annotated[str, AfterValidator(_valider_hote)]


def _valider_suffixe(valeur: str) -> str:
    if "." not in valeur:
        raise ValueError("un suffixe doit compter au moins deux labels (jamais un TLD seul)")
    return valeur


Suffixe = Annotated[Hote, AfterValidator(_valider_suffixe)]

Delai = Annotated[float, Field(gt=0, allow_inf_nan=False)]
"""Délai en secondes, strictement positif et fini."""


def _valider_chemin(valeur: str) -> str:
    if not valeur.startswith("/") or "?" in valeur or "#" in valeur:
        raise ValueError("chemin absolu sans requête ni fragment attendu")
    return valeur


Chemin = Annotated[str, AfterValidator(_valider_chemin)]


class Delais(ModeleConfig):
    """Délais des clients, en secondes."""

    defaut: Delai = 30
    mcp: Delai = 10
    sonde: Delai = 3
    local: Delai = 600


class Sonde(ModeleConfig):
    """Sonde du Mode : seule requête permise en `hors-ligne-detecte`."""

    url: str

    @field_validator("url")
    @classmethod
    def _https(cls, valeur: str) -> str:
        cible = analyser_url(valeur)
        if cible.schema != "https" or cible.port not in (None, 443) or cible.identifiants:
            raise ValueError("URL HTTPS sur le port 443 attendue")
        _valider_hote(cible.hote)
        return valeur


class Regle(ModeleConfig):
    """Règle du profil `outillage` : méthodes permises vers des hôtes (et des chemins)."""

    nom: str = Field(min_length=1)
    methodes: list[Methode] = Field(min_length=1)
    hotes: list[Hote] = Field(default_factory=list)
    suffixes: list[Suffixe] = Field(default_factory=list)
    """Domaine permis avec tous ses sous-domaines (frontière de label)."""
    chemins: list[Chemin] = Field(default_factory=list)
    """Chemins exacts permis ; vide = tout chemin."""

    @model_validator(mode="after")
    def _au_moins_un_hote(self) -> Regle:
        if not self.hotes and not self.suffixes:
            raise ValueError(f"règle {self.nom!r} : au moins un hôte ou un suffixe attendu")
        return self


class ConfigProfil(ModeleConfig):
    """Règles d'un profil."""

    liste_blanche_en_lecture: bool = False
    """GET et HEAD permis vers les hôtes de la Liste blanche."""
    regles: list[Regle] = Field(default_factory=list)


class Profils(ModeleConfig):
    """Profils configurables (`assistant` suit la Liste blanche seule)."""

    outillage: ConfigProfil
    aucun: ConfigProfil = Field(default_factory=ConfigProfil)
    eval_distant: ConfigProfil = Field(default_factory=ConfigProfil, alias="eval-distant")
    """Génération d'un modèle distant (story 17.1) : règles seules, sans Liste blanche."""

    @field_validator("aucun")
    @classmethod
    def _aucun_vide(cls, valeur: ConfigProfil) -> ConfigProfil:
        if valeur.regles or valeur.liste_blanche_en_lecture:
            raise ValueError("le profil aucun n'admet ni règle ni lecture de la Liste blanche")
        return valeur

    @field_validator("eval_distant")
    @classmethod
    def _eval_distant_sans_liste(cls, valeur: ConfigProfil) -> ConfigProfil:
        if valeur.liste_blanche_en_lecture:
            raise ValueError("le profil eval-distant n'admet pas la lecture de la Liste blanche")
        return valeur


class ConfigReseau(ModeleConfig):
    """Contenu de `config/reseau.toml`."""

    delais: Delais = Field(default_factory=Delais)
    sonde: Sonde
    profils: Profils


class ConfigListeBlanche(ModeleConfig):
    """Contenu de `config/liste-blanche.toml` : hôtes du profil `assistant`."""

    hotes: list[Hote] = Field(min_length=1)


def chemin_config(nom: str) -> Path:
    return racine_projet() / "config" / nom


def charger_config_reseau(chemin: str | Path | None = None) -> ConfigReseau:
    """Lit `config/reseau.toml` (ou `chemin`) ; lève `ConfigurationInvalide`."""
    return charger_toml(chemin_config(NOM_RESEAU) if chemin is None else chemin, ConfigReseau)


def charger_liste_blanche(chemin: str | Path | None = None) -> ConfigListeBlanche:
    """Lit `config/liste-blanche.toml` (ou `chemin`) ; lève `ConfigurationInvalide`."""
    return charger_toml(
        chemin_config(NOM_LISTE_BLANCHE) if chemin is None else chemin, ConfigListeBlanche
    )
