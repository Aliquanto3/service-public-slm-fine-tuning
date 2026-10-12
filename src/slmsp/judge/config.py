"""Configuration des juges : `config/juges.toml` (AD-22).

Section `principal` : Juge principal Claude. La section `second` (second juge Mistral) est
ajoutée par la story 5.5. Toutes les durées sont en secondes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_JUGES: Final = "juges.toml"

Duree = Annotated[float, Field(gt=0, allow_inf_nan=False)]
"""Durée en secondes, strictement positive et finie."""

Effort = Literal["low", "medium", "high", "xhigh", "max"]


class ConfigJugePrincipal(ModeleConfig):
    """Juge principal Claude (section `[principal]`)."""

    modele: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    effort: Effort
    mode_appel: Literal["batch", "direct"] = "batch"
    max_tokens: int = Field(ge=1)
    delai_max_lot: Duree
    intervalle_sondage: Duree
    delai_annulation: Duree
    delai_appel: Duree
    usage_budget: Annotated[str, StringConstraints(min_length=1)]
    grille: Annotated[str, StringConstraints(min_length=1)]

    def chemin_grille(self, racine: str | Path | None = None) -> Path:
        """Chemin de la grille : absolu tel quel, sinon relatif à la racine du dépôt."""
        chemin = Path(self.grille)
        if chemin.is_absolute():
            return chemin
        return (Path(racine) if racine is not None else racine_projet()) / chemin


class ConfigJuges(ModeleConfig):
    """Contenu de `config/juges.toml`."""

    schema_version: Literal[1]
    principal: ConfigJugePrincipal


def charger_juges(chemin: str | Path | None = None) -> ConfigJuges:
    """Lit `juges.toml` (défaut : `<racine du projet>/config/juges.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_JUGES, ConfigJuges
    )
