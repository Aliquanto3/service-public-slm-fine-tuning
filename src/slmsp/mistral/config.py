"""Configuration de l'adaptateur Mistral : `config/mistral.toml` (D1.2, AD-3).

Le modèle demandé et le modèle résolu (champ `model` d'une réponse) doivent figurer dans
`modeles_autorises` et ne correspondre à aucun `motifs_interdits` (sous-chaîne, insensible à
la casse). Les deux journaux d'appels sont des fichiers distincts de `SLMSP_VAR_DIR`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.artefacts import NOM_JOURNAL_MISTRAL
from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_MISTRAL: Final = "mistral.toml"

Nom = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def motif_interdit(modele: str, motifs: list[str] | tuple[str, ...]) -> str | None:
    """Premier motif de `motifs` contenu dans `modele` (casse ignorée), sinon `None`."""
    nom = modele.casefold()
    for motif in motifs:
        if motif.casefold() in nom:
            return motif
    return None


_RE_SUFFIXE_VERSION: Final = re.compile(r"(?:-\d+)+")
"""Suffixe de version admis après le nom d'une préversion : `-0`, `-2610`, `-4-0`…"""


def preversion_admise(
    modele: str,
    preversions: tuple[str, ...] | list[str],
    motifs: tuple[str, ...] | list[str] = (),
) -> bool:
    """Vrai si `modele` (demandé ou résolu) est exactement une des `preversions`, ou l'une
    d'elles suivie d'un suffixe de version numérique (`-2610`, `-4-0` : identifiant daté
    renvoyé par l'API) sans aucun des `motifs` interdits. `mistral-large-4-preview-beta` n'est
    donc pas admis : seul le nom exact listé échappe aux motifs."""
    if modele in preversions:
        return True
    return motif_interdit(modele, motifs) is None and any(
        modele.startswith(p) and _RE_SUFFIXE_VERSION.fullmatch(modele[len(p) :]) is not None
        for p in preversions
    )


def _nom_de_fichier(nom: str, cle: str) -> None:
    if nom in (".", "..") or any(sep in nom for sep in ("/", "\\", ":")):
        raise ValueError(f"{cle} doit être un simple nom de fichier, sans chemin : {nom!r}")


class ConfigMistral(ModeleConfig):
    """Contenu de `config/mistral.toml`."""

    schema_version: Literal[1]
    modele: Nom
    modeles_autorises: list[Nom] = Field(min_length=1)
    motifs_interdits: list[Nom]
    delai_appel: float = Field(gt=0, allow_inf_nan=False)
    """Délai total d'un appel HTTP (secondes), échéance comprise."""
    delai_connexion: float = Field(default=10.0, gt=0, allow_inf_nan=False)
    delai_lecture: float = Field(default=180.0, gt=0, allow_inf_nan=False)
    reessais_max: int = Field(default=5, ge=0, le=20)
    attente_totale_max: float = Field(default=600.0, ge=0, allow_inf_nan=False)
    duree_totale_max_appel: float = Field(default=900.0, gt=0, allow_inf_nan=False)
    """Durée maximale d'un appel `appeler`, tentatives et attentes comprises (secondes)."""
    attente_base: float = Field(default=2.0, gt=0, allow_inf_nan=False)
    attente_plafond: float = Field(default=60.0, gt=0, allow_inf_nan=False)
    fichier_journal_donnees: Nom
    fichier_journal_juge: Nom
    modele_generateur: Nom | None = None
    """Modèle demandé par le Générateur (`data generate`) ; `None` : celui de `modele`."""
    modeles_preversion_generateur: list[Nom] = Field(default_factory=list)
    """Préversions admises pour le Générateur seul (story S5), hors de la liste stable."""

    @model_validator(mode="after")
    def _coherence(self) -> ConfigMistral:
        if self.modele not in self.modeles_autorises:
            raise ValueError(f"le modèle {self.modele!r} n'est pas dans modeles_autorises")
        motif = motif_interdit(self.modele, self.motifs_interdits)
        if motif is not None:
            raise ValueError(f"le modèle {self.modele!r} contient le motif interdit {motif!r}")
        communs = set(self.modeles_preversion_generateur) & set(self.modeles_autorises)
        if communs:
            raise ValueError(
                "modeles_preversion_generateur et modeles_autorises se recoupent : "
                f"{sorted(communs)}"
            )
        if self.modele_generateur is not None:
            refus = self.refus_generateur(self.modele_generateur)
            if refus is not None:
                raise ValueError(f"modele_generateur {self.modele_generateur!r} : {refus}")
        _nom_de_fichier(self.fichier_journal_donnees, "fichier_journal_donnees")
        _nom_de_fichier(self.fichier_journal_juge, "fichier_journal_juge")
        if self.fichier_journal_donnees.casefold() == self.fichier_journal_juge.casefold():
            raise ValueError("les journaux des données et du juge doivent être distincts")
        if self.attente_plafond < self.attente_base:
            raise ValueError("attente_plafond doit être supérieure ou égale à attente_base")
        if self.fichier_journal_donnees != NOM_JOURNAL_MISTRAL:
            raise ValueError(
                f"fichier_journal_donnees doit valoir {NOM_JOURNAL_MISTRAL!r} "
                "(liste d'accès d'AD-24, slmsp.core.artefacts)"
            )
        return self

    @property
    def preversion(self) -> str | None:
        """Préversion demandée par cette configuration (celle du Générateur, après
        `pour_generateur`), sinon `None`."""
        return self.modele if self.modele in self.modeles_preversion_generateur else None

    def refus_generateur(self, modele: str) -> str | None:
        """Motif de refus de `modele` comme modèle demandé du Générateur : liste stable, ou
        liste des préversions du Générateur."""
        if modele in self.modeles_preversion_generateur:
            return None
        return self.refus_modele(modele)

    def pour_generateur(self, modele: str | None = None) -> ConfigMistral:
        """Copie de la configuration dont `modele` est celui du Générateur : `modele` s'il est
        donné (option `--modele-generateur`), sinon `modele_generateur`, sinon `modele`.

        Lève `ValueError` si ce modèle n'est ni stable ni une préversion du Générateur. La
        copie sert au seul client du Générateur, jamais au second juge.
        """
        choisi = modele or self.modele_generateur or self.modele
        refus = self.refus_generateur(choisi)
        if refus is not None:
            raise ValueError(f"modèle du Générateur {choisi!r} refusé ({refus})")
        return self.model_copy(update={"modele": choisi})

    def refus_modele(self, modele: str) -> str | None:
        """Motif de refus de `modele` (absent de la liste stable, ou motif interdit).

        Pour une configuration de préversion (`preversion`), la préversion et ses identifiants
        résolus `<préversion>-<version numérique>` sans motif interdit sont admis en plus de la
        liste stable."""
        if self.preversion is not None and preversion_admise(
            modele, (self.preversion,), self.motifs_interdits
        ):
            return None
        if modele not in self.modeles_autorises:
            return "absent de modeles_autorises"
        motif = motif_interdit(modele, self.motifs_interdits)
        if motif is not None:
            return f"motif interdit {motif!r}"
        return None


def charger_mistral(chemin: str | Path | None = None) -> ConfigMistral:
    """Lit `mistral.toml` (défaut : `<racine du projet>/config/mistral.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_MISTRAL,
        ConfigMistral,
    )
