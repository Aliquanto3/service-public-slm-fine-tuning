"""Configuration du budget : plafonds (`config/budgets.toml`) et tarifs (`config/tarifs.toml`).

Toutes les sommes de `budgets.toml` sont en euros. Les tarifs de `tarifs.toml` sont en
dollars US par million de tokens, par modèle et par mode (`direct`, `batch`) ; chaque mode
porte les composantes `entree`, `sortie` et, s'il est connu, `ecriture_cache` et
`lecture_cache`. Le taux USD → EUR est daté. Aucun tarif n'a de valeur par défaut.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import (
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_BUDGETS: Final = "budgets.toml"
NOM_TARIFS: Final = "tarifs.toml"

MODES: Final = ("direct", "batch")
"""Modes tarifaires : appel direct ou lot batch."""

Mode = Literal["direct", "batch"]
Nom = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_-]*$")]
Montant = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Prix = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class Poste(ModeleConfig):
    """Poste de budget : plafond en euros et sous-postes éventuels (nom -> plafond)."""

    plafond_eur: Montant
    sous_postes: dict[Nom, Montant] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _sous_postes_sous_le_plafond(self) -> Poste:
        for nom, plafond in self.sous_postes.items():
            if plafond > self.plafond_eur:
                raise ValueError(
                    f"le plafond du sous-poste {nom} ({plafond:g} €) dépasse celui du poste "
                    f"({self.plafond_eur:g} €)"
                )
        return self


class ConfigBudgets(ModeleConfig):
    """Contenu de `config/budgets.toml`."""

    schema_version: Literal[1]
    campagne_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    marge_eur: Montant
    majoration_entree: float = Field(ge=1, allow_inf_nan=False)
    postes: dict[Nom, Poste] = Field(min_length=1)
    imputations: dict[str, str] = Field(default_factory=dict)

    @field_validator("imputations")
    @classmethod
    def _imputations_connues(
        cls, imputations: dict[str, str], info: ValidationInfo
    ) -> dict[str, str]:
        postes: dict[str, Poste] | None = info.data.get("postes")
        if postes is None:
            return imputations  # postes déjà en erreur
        for usage, cible in imputations.items():
            poste, _, sous_poste = cible.partition(".")
            if poste not in postes:
                raise ValueError(f"imputation {usage} : poste inconnu {poste!r}")
            sous_postes = postes[poste].sous_postes
            if sous_poste and sous_poste not in sous_postes:
                raise ValueError(f"imputation {usage} : sous-poste inconnu {cible!r}")
            if not sous_poste and sous_postes:
                raise ValueError(f"imputation {usage} : le poste {poste} exige un sous-poste")
        return imputations


class TarifMode(ModeleConfig):
    """Prix d'un mode, en dollars US par million de tokens."""

    entree: Prix
    sortie: Prix
    ecriture_cache: Prix | None = None
    lecture_cache: Prix | None = None


class TarifModele(ModeleConfig):
    """Tarifs datés et sourcés d'un modèle, par mode."""

    devise: Literal["USD"]
    date: dt.date
    source: str = Field(min_length=1)
    note: str = ""
    modes: dict[Mode, TarifMode] = Field(min_length=1)


class TauxChange(ModeleConfig):
    """Taux de conversion daté : 1 USD = `valeur` EUR."""

    valeur: float = Field(gt=0, allow_inf_nan=False)
    date: dt.date
    source: str = Field(min_length=1)
    note: str = ""


class ConfigTarifs(ModeleConfig):
    """Contenu de `config/tarifs.toml`."""

    schema_version: Literal[1]
    taux_usd_eur: TauxChange
    modeles: dict[str, TarifModele] = Field(min_length=1)

    @field_validator("modeles")
    @classmethod
    def _identifiants_non_vides(cls, valeur: dict[str, TarifModele]) -> dict[str, TarifModele]:
        if any(not nom.strip() for nom in valeur):
            raise ValueError("identifiant de modèle vide")
        return valeur


def _defaut(nom: str) -> Path:
    return racine_projet() / "config" / nom


def charger_budgets(chemin: str | Path | None = None) -> ConfigBudgets:
    """Lit `budgets.toml` (défaut : `<racine du projet>/config/budgets.toml`)."""
    return charger_toml(chemin if chemin is not None else _defaut(NOM_BUDGETS), ConfigBudgets)


def charger_tarifs(chemin: str | Path | None = None) -> ConfigTarifs:
    """Lit `tarifs.toml` (défaut : `<racine du projet>/config/tarifs.toml`)."""
    return charger_toml(chemin if chemin is not None else _defaut(NOM_TARIFS), ConfigTarifs)
