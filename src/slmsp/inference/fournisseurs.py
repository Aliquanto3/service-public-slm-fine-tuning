"""Presets des fournisseurs externes compatibles OpenAI (story 17.4, amendement 14).

Un preset est un adaptateur de requête : URL et modèles proposés (préremplis dans les
Paramètres, modifiables), options du Harnais transmises, champ de graine, ajouts imposés.
Valeurs vérifiées le 21/10 :

- `openrouter` : ajoute `provider = {data_collection: "deny", require_parameters: true}` et
  `reasoning = {enabled: false}` ; transmet `seed` ;
- `mistral` : schéma strict (HTTP 422 `extra_forbidden` sur tout champ inconnu) : `seed`
  devient `random_seed`, `top_k` n'est pas transmis ;
- `ovh` (AI Endpoints) : aucun champ additionnel (refus de `chat_template_kwargs`), pas de
  graine ; le raisonnement renvoyé à part est ignoré à l'affichage (`client_openai.lire_flux`) ;
- `generique` : URL et modèle libres, aucun champ additionnel, pas de graine ; seul preset à
  admettre `parametres_supplementaires` (amendement 13).

Quel que soit le preset, une requête vers l'hôte `openrouter.ai` porte les ajouts
d'OpenRouter : le refus de collecte ne se contourne pas en choisissant `generique`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

HOTE_OPENROUTER: Final = "openrouter.ai"
OPTIONS_COMMUNES: Final = frozenset({"temperature", "max_tokens", "top_p", "stop"})


def corps_reasoning() -> dict[str, Any]:
    """Raisonnement désactivé, paramètre unifié d'OpenRouter (vérifié le 21/10 : 0 token)."""
    return {"enabled": False}


def ajouts_openrouter() -> dict[str, Any]:
    return {
        "provider": {"data_collection": "deny", "require_parameters": True},
        "reasoning": corps_reasoning(),
    }


@dataclass(frozen=True)
class Preset:
    nom: str
    libelle: str
    url_base: str | None
    modeles: tuple[str, ...]
    options: frozenset[str]
    """Options du Harnais transmises telles quelles (les autres sont omises)."""
    champ_graine: str | None = None
    """Nom du champ qui reçoit l'option `seed` (`None` : graine omise)."""
    parametres_libres: bool = False

    def vue(self) -> dict[str, Any]:
        """Description pour l'interface (préremplissage)."""
        return {
            "nom": self.nom,
            "libelle": self.libelle,
            "url_base": self.url_base,
            "modeles": list(self.modeles),
            "parametres_libres": self.parametres_libres,
        }


PRESETS: Final[dict[str, Preset]] = {
    p.nom: p
    for p in (
        Preset(
            "openrouter",
            "OpenRouter",
            "https://openrouter.ai/api/v1",
            ("qwen/qwen3.6-27b", "mistralai/mistral-small-2603"),
            OPTIONS_COMMUNES | {"top_k"},
            champ_graine="seed",
        ),
        Preset(
            "mistral",
            "Mistral AI",
            "https://api.mistral.ai/v1",
            ("mistral-small-latest",),
            OPTIONS_COMMUNES,
            champ_graine="random_seed",
        ),
        Preset(
            "ovh",
            "OVHcloud AI Endpoints",
            "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
            ("Qwen3.6-27B", "Mistral-Small-3.2-24B-Instruct-2506"),
            OPTIONS_COMMUNES,
        ),
        Preset(
            "generique",
            "Autre hôte compatible OpenAI",
            None,
            (),
            OPTIONS_COMMUNES,
            parametres_libres=True,
        ),
    )
}
PRESET_DEFAUT: Final = "generique"


def preset(nom: str) -> Preset:
    """Preset nommé ; `ValueError` sinon."""
    try:
        return PRESETS[nom]
    except (KeyError, TypeError):
        raise ValueError("preset inconnu") from None


def ajouts_requete(choisi: Preset, hote: str, options: Mapping[str, Any]) -> dict[str, Any]:
    """Champs du corps propres au preset : options transmises, graine, ajouts imposés."""
    champs = {cle: v for cle, v in options.items() if cle in choisi.options}
    if choisi.champ_graine is not None and "seed" in options:
        champs[choisi.champ_graine] = options["seed"]
    if choisi.nom == "openrouter" or hote == HOTE_OPENROUTER:
        champs.update(ajouts_openrouter())
    return champs


__all__ = [
    "HOTE_OPENROUTER",
    "PRESETS",
    "PRESET_DEFAUT",
    "Preset",
    "ajouts_openrouter",
    "ajouts_requete",
    "corps_reasoning",
    "preset",
]
