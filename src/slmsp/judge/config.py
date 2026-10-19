"""Configuration des juges : `config/juges.toml` (AD-22).

Section `principal` : Juge principal Claude (story 5.4). Section `second` : second juge
Mistral (story 5.5), dont le délai d'appel est dans `config/mistral.toml`. Sections
facultatives `juges_tiers.<nom>` : juges tiers OpenRouter (story S3). Toutes les durées
sont en secondes.
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


class ConfigSecondJuge(ModeleConfig):
    """Second juge Mistral (section `[second]`)."""

    modele: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    temperature: float = Field(ge=0, le=0, allow_inf_nan=False)
    """Toujours 0 : la clé du cache (`effort_cache`) suppose une température nulle."""
    max_tokens: int = Field(ge=1)
    usage_budget: Literal["juge-second"]
    """Seul usage admis : il route vers le journal du juge, illisible par `data` et `train`."""
    effort_cache: Annotated[str, StringConstraints(min_length=1)]
    format_reponse: Literal["json_schema", "json_object"] = "json_schema"

    @property
    def effort_cle(self) -> str:
        """Part « effort » de la clé du cache : `effort_cache` et format de réponse."""
        return f"{self.effort_cache}+{self.format_reponse}"


NomJugeTiers = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9.-]*$")]
"""Nom d'un juge tiers (section `[juges_tiers.<nom>]`), repris dans le slug du run."""


class ConfigJugeTiers(ModeleConfig):
    """Juge tiers servi par OpenRouter (section `[juges_tiers.<nom>]`, story S3).

    Avis comparatif hors score officiel. `temperature` absente : le paramètre n'est pas
    envoyé (modèles de raisonnement qui le refusent). `effort_raisonnement` est envoyé en
    `reasoning.effort` s'il est fourni. L'estimation de coût compte
    `sortie_estimee + marge_raisonnement` tokens de sortie par item (bornés par
    `max_tokens`) ; la réservation au registre compte toujours `max_tokens` (pire cas).
    """

    fournisseur: Literal["openrouter"] = "openrouter"
    modele: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    temperature: float | None = Field(default=None, ge=0, le=0, allow_inf_nan=False)
    max_tokens: int = Field(ge=1)
    effort_raisonnement: Literal["minimal", "low", "medium", "high"] | None = None
    format_reponse: Literal["json_schema", "json_object"] = "json_schema"
    sortie_estimee: int = Field(default=1500, ge=1)
    marge_raisonnement: int = Field(default=2000, ge=0)

    @property
    def usage_budget(self) -> str:
        """Usage de budget de ce juge : `juge-tiers-<fournisseur>` (`budgets.toml`)."""
        return f"juge-tiers-{self.fournisseur}"

    @property
    def effort_cle(self) -> str:
        """Part « effort » de la clé du cache : température, effort et format de réponse."""
        temperature = "sans" if self.temperature is None else f"{self.temperature:g}"
        effort = self.effort_raisonnement or "aucun"
        return f"tiers-temperature-{temperature}+effort-{effort}+{self.format_reponse}"

    @property
    def sortie_estimation(self) -> int:
        """Tokens de sortie comptés par item dans l'estimation (raisonnement compris)."""
        return min(self.max_tokens, self.sortie_estimee + self.marge_raisonnement)


class ConfigJuges(ModeleConfig):
    """Contenu de `config/juges.toml`."""

    schema_version: Literal[1]
    principal: ConfigJugePrincipal
    second: ConfigSecondJuge
    juges_tiers: dict[NomJugeTiers, ConfigJugeTiers] = Field(default_factory=dict)
    """Juges tiers facultatifs (story S3), sans effet sur le principal ni le second."""


def charger_juges(chemin: str | Path | None = None) -> ConfigJuges:
    """Lit `juges.toml` (défaut : `<racine du projet>/config/juges.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_JUGES, ConfigJuges
    )
