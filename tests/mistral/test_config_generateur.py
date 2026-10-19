"""Story S5 : modèle du Générateur distinct de `modele`, préversion admise pour lui seul."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from slmsp.budget.config import charger_tarifs
from slmsp.budget.tarifs import tarif
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.mistral.config import charger_mistral, preversion_admise
from slmsp.mistral.generateur import PrealableNonSatisfait, charger_prealables

from .test_config import ecrire

PREVERSION = '["mistral-large-4"]'


def test_config_reelle_du_generateur() -> None:
    config = charger_mistral()
    assert config.modele_generateur == "mistral-large-latest"
    assert config.modeles_preversion_generateur == ["mistral-large-4"]
    assert config.preversion is None  # le second juge reste sur la liste stable
    assert config.refus_modele("mistral-large-4") is not None
    assert config.pour_generateur().modele == "mistral-large-latest"


def test_pour_generateur_preversion() -> None:
    config = charger_mistral().pour_generateur("mistral-large-4")
    assert config.modele == "mistral-large-4" and config.preversion == "mistral-large-4"
    assert config.refus_modele("mistral-large-4") is None
    assert config.refus_modele("mistral-large-4-2610") is None  # identifiant résolu daté
    assert config.refus_modele("mistral-large-2512") is None  # liste stable inchangée
    assert config.refus_modele("mistral-large-5") is not None
    assert config.refus_modele("mistral-large-40") is not None
    assert charger_mistral().modele == "mistral-large-latest"  # original non modifié


def test_modele_inconnu_refuse() -> None:
    with pytest.raises(ValueError, match="refusé"):
        charger_mistral().pour_generateur("mistral-inconnu")


def test_modele_generateur_valide_au_chargement(tmp_path: Path) -> None:
    chemin = ecrire(
        tmp_path,
        modele_generateur='"mistral-large-4"',
        modeles_preversion_generateur=PREVERSION,
    )
    config = charger_mistral(chemin)
    assert config.modele == "mistral-large-latest"
    assert config.pour_generateur().modele == "mistral-large-4"
    with pytest.raises(ConfigurationInvalide):
        charger_mistral(ecrire(tmp_path, modele_generateur='"mistral-inconnu"'))
    with pytest.raises(ConfigurationInvalide):
        charger_mistral(
            ecrire(tmp_path, modele='"mistral-large-4"', modeles_preversion_generateur=PREVERSION)
        )


def test_preversion_hors_liste_stable(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="recoupent"):
        charger_mistral(ecrire(tmp_path, modeles_preversion_generateur='["mistral-large-2411"]'))


def test_preversion_admise() -> None:
    assert preversion_admise("mistral-large-4", ("mistral-large-4",))
    assert preversion_admise("mistral-large-4-2610", ("mistral-large-4",))
    assert not preversion_admise("mistral-large-4b", ("mistral-large-4",))
    assert not preversion_admise("mistral-large-4", ())


def test_prealables_preversion(tmp_path: Path) -> None:
    jour = date(2026, 10, 19)
    chemin = tmp_path / "donnees.toml"
    chemin.write_text(
        f"[mistral]\nconditions_verifiees_le = {jour}\n"
        'modeles_stables = ["mistral-large-latest"]\n',
        encoding="utf-8",
    )
    with pytest.raises(PrealableNonSatisfait, match="modeles_stables"):
        charger_prealables(chemin, modele="mistral-large-4", aujourd_hui=jour)
    prealables = charger_prealables(
        chemin, modele="mistral-large-4", aujourd_hui=jour, preversions=("mistral-large-4",)
    )
    assert prealables.admet("mistral-large-4-2610") and prealables.admet("mistral-large-latest")
    assert not prealables.admet("mistral-large-5") and not prealables.admet(None)
    stables = charger_prealables(chemin, modele="mistral-large-latest", aujourd_hui=jour)
    assert not stables.admet("mistral-large-4")


def test_tarif_mistral_large_4() -> None:
    tarifs = charger_tarifs(racine_projet() / "config" / "tarifs.toml")
    mode = tarif(tarifs, "mistral-large-4", "direct")
    assert (mode.entree, mode.sortie) == (1.36, 4.18)
