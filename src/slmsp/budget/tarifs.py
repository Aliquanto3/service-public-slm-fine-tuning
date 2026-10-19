"""Coût d'un appel en euros : pire cas avant l'appel, coût réel après (AD-5).

Les tarifs sont cherchés par l'identifiant exact du modèle et par mode (`direct`, `batch`),
sans alias ni valeur par défaut : un modèle, un mode ou une composante de cache absents
lèvent `TarifInconnu`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from slmsp.budget.config import MODES, ConfigTarifs, TarifMode
from slmsp.core.erreurs import TarifInconnu

TOKENS_PAR_UNITE: Final = 1_000_000
"""Les prix de `tarifs.toml` sont donnés par million de tokens."""


@dataclass(frozen=True)
class UsageTokens:
    """Compteurs de tokens facturés par le fournisseur pour un appel (ou un lot)."""

    entree: int
    sortie: int
    ecriture_cache: int = 0
    lecture_cache: int = 0

    def __post_init__(self) -> None:
        for nom in ("entree", "sortie", "ecriture_cache", "lecture_cache"):
            valeur = getattr(self, nom)
            if isinstance(valeur, bool) or not isinstance(valeur, int) or valeur < 0:
                raise ValueError(f"usage : {nom} doit être un entier positif ou nul")

    def __add__(self, autre: UsageTokens) -> UsageTokens:
        return UsageTokens(
            self.entree + autre.entree,
            self.sortie + autre.sortie,
            self.ecriture_cache + autre.ecriture_cache,
            self.lecture_cache + autre.lecture_cache,
        )


def tarif(config: ConfigTarifs, modele: str, mode: str) -> TarifMode:
    """Tarif de `modele` (identifiant exact) dans `mode` ; `TarifInconnu` s'il manque."""
    if mode not in MODES:
        raise TarifInconnu(f"mode tarifaire inconnu : {mode!r} (attendu : {', '.join(MODES)})")
    tarifs_modele = config.modeles.get(modele)
    if tarifs_modele is None:
        raise TarifInconnu(f"aucun tarif pour le modèle {modele!r} dans tarifs.toml")
    tarif_mode = tarifs_modele.modes.get(mode)
    if tarif_mode is None:
        raise TarifInconnu(f"aucun tarif pour le modèle {modele!r} en mode {mode}")
    return tarif_mode


def _prix_cache(tarif_mode: TarifMode, composante: str, modele: str, mode: str) -> float:
    prix = getattr(tarif_mode, composante)
    if prix is None:
        raise TarifInconnu(f"aucun tarif {composante} pour le modèle {modele!r} en mode {mode}")
    return prix


def _verifier_entier(nom: str, valeur: int, minimum: int) -> None:
    if isinstance(valeur, bool) or not isinstance(valeur, int) or valeur < minimum:
        raise ValueError(f"{nom} doit être un entier supérieur ou égal à {minimum}")


def cout_pire_cas(
    config: ConfigTarifs,
    modele: str,
    mode: str,
    tokens_entree_estimes: int,
    max_tokens: int,
    majoration_entree: float,
    *,
    avec_cache: bool = False,
) -> float:
    """Coût pire cas en euros d'une requête.

    ⌈entrée × majoration⌉ au tarif d'entrée (au plus cher des tarifs d'entrée et
    d'écriture de cache si `avec_cache`), plus `max_tokens` au tarif de sortie, converti
    par le taux USD → EUR.
    """
    _verifier_entier("tokens_entree_estimes", tokens_entree_estimes, 0)
    _verifier_entier("max_tokens", max_tokens, 1)
    if not majoration_entree >= 1:
        raise ValueError("la majoration des tokens d'entrée doit valoir au moins 1")
    tarif_mode = tarif(config, modele, mode)
    prix_entree = tarif_mode.entree
    if avec_cache:
        prix_entree = max(prix_entree, _prix_cache(tarif_mode, "ecriture_cache", modele, mode))
    entree = math.ceil(tokens_entree_estimes * majoration_entree)
    dollars = (entree * prix_entree + max_tokens * tarif_mode.sortie) / TOKENS_PAR_UNITE
    return dollars * config.taux_usd_eur.valeur


def cout_estime(
    config: ConfigTarifs, modele: str, mode: str, tokens_entree: int, tokens_sortie: int
) -> float:
    """Coût estimé en euros d'une requête : entrées et sorties au tarif du mode, sans majoration."""
    _verifier_entier("tokens_entree", tokens_entree, 0)
    _verifier_entier("tokens_sortie", tokens_sortie, 0)
    tarif_mode = tarif(config, modele, mode)
    dollars = (tokens_entree * tarif_mode.entree + tokens_sortie * tarif_mode.sortie) / (
        TOKENS_PAR_UNITE
    )
    return dollars * config.taux_usd_eur.valeur


def cout_reel(config: ConfigTarifs, modele: str, mode: str, usage: UsageTokens) -> float:
    """Coût réel en euros des quatre compteurs de `usage`."""
    tarif_mode = tarif(config, modele, mode)
    dollars = usage.entree * tarif_mode.entree + usage.sortie * tarif_mode.sortie
    if usage.ecriture_cache:
        prix = _prix_cache(tarif_mode, "ecriture_cache", modele, mode)
        dollars += usage.ecriture_cache * prix
    if usage.lecture_cache:
        prix = _prix_cache(tarif_mode, "lecture_cache", modele, mode)
        dollars += usage.lecture_cache * prix
    return dollars / TOKENS_PAR_UNITE * config.taux_usd_eur.valeur
