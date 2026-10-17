"""Configuration de l'adaptateur Mistral : `config/mistral.toml` (D1.2, AD-3).

Le modèle demandé et le modèle résolu (champ `model` d'une réponse) doivent figurer dans
`modeles_autorises` et ne correspondre à aucun `motifs_interdits` (sous-chaîne, insensible à
la casse). Les deux journaux d'appels sont des fichiers distincts de `SLMSP_VAR_DIR`.
"""

from __future__ import annotations

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

    @model_validator(mode="after")
    def _coherence(self) -> ConfigMistral:
        if self.modele not in self.modeles_autorises:
            raise ValueError(f"le modèle {self.modele!r} n'est pas dans modeles_autorises")
        motif = motif_interdit(self.modele, self.motifs_interdits)
        if motif is not None:
            raise ValueError(f"le modèle {self.modele!r} contient le motif interdit {motif!r}")
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

    def refus_modele(self, modele: str) -> str | None:
        """Motif de refus de `modele` (absent de la liste stable, ou motif interdit)."""
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
