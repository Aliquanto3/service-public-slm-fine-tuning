"""Configuration de l'adaptateur Mistral (`config/mistral.toml`)."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.artefacts import NOM_JOURNAL_MISTRAL
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.mistral.config import charger_mistral, motif_interdit

VALIDE = {
    "schema_version": "1",
    "modele": '"mistral-large-latest"',
    "modeles_autorises": '["mistral-large-latest", "mistral-large-2411"]',
    "motifs_interdits": '["labs", "preview", "beta", "-rc", "experimental"]',
    "delai_appel": "300",
    "fichier_journal_donnees": '"appels-mistral.sqlite"',
    "fichier_journal_juge": '"appels-mistral-juge.sqlite"',
}


def ecrire(tmp_path: Path, **valeurs: str | None) -> Path:
    champs = {**VALIDE, **valeurs}
    chemin = tmp_path / "mistral.toml"
    chemin.write_text(
        "\n".join(f"{cle} = {valeur}" for cle, valeur in champs.items() if valeur is not None)
        + "\n",
        encoding="utf-8",
    )
    return chemin


def test_config_reelle() -> None:
    config = charger_mistral()
    assert config.modele == "mistral-large-latest"
    assert config.modeles_autorises == [
        "mistral-large-latest",
        "mistral-large-2411",
        "mistral-large-2512",
    ]
    assert set(config.motifs_interdits) == {"labs", "preview", "beta", "-rc", "experimental"}
    assert config.delai_appel > 0
    assert config.fichier_journal_donnees == NOM_JOURNAL_MISTRAL
    assert config.fichier_journal_juge == "appels-mistral-juge.sqlite"


def test_chaque_valeur_est_commentee() -> None:
    texte = (Path(__file__).resolve().parents[2] / "config" / "mistral.toml").read_text(
        encoding="utf-8"
    )
    lignes = texte.splitlines()
    for rang, ligne in enumerate(lignes):
        if "=" in ligne and not ligne.startswith("#"):
            assert lignes[rang - 1].startswith("#"), ligne


def test_config_minimale_valide(tmp_path: Path) -> None:
    assert charger_mistral(ecrire(tmp_path)).modele == "mistral-large-latest"


@pytest.mark.parametrize(
    "valeurs",
    [
        {"modele": '"mistral-medium-latest"'},  # hors liste
        {
            "modele": '"mistral-large-2512-preview"',
            "modeles_autorises": '["mistral-large-2512-preview"]',
        },
        {"modele": '"Labs-Large"', "modeles_autorises": '["Labs-Large"]'},  # casse ignorée
        {"fichier_journal_juge": '"appels-mistral.sqlite"'},  # journaux confondus
        {"fichier_journal_juge": '"APPELS-MISTRAL.sqlite"'},
        {"fichier_journal_juge": '"../appels-mistral-juge.sqlite"'},
        {"fichier_journal_juge": '"sous\\\\juge.sqlite"'},
        {"fichier_journal_donnees": '"journal-donnees.sqlite"'},  # nom d'AD-24 imposé
        {"delai_appel": "0"},
        {"modeles_autorises": "[]"},
        {"cle_inconnue": "1"},
        {"fichier_journal_juge": None},
    ],
)
def test_config_refusee(tmp_path: Path, valeurs: dict[str, str | None]) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_mistral(ecrire(tmp_path, **valeurs))


def test_motif_interdit_insensible_a_la_casse() -> None:
    motifs = ["labs", "preview", "beta", "-rc", "experimental"]
    assert motif_interdit("LABS-mistral-large", motifs) == "labs"
    assert motif_interdit("mistral-large-2512-Preview", motifs) == "preview"
    assert motif_interdit("mistral-large-2512-rc1", motifs) == "-rc"
    assert motif_interdit("mistral-large-2512", motifs) is None


def test_refus_modele() -> None:
    config = charger_mistral()
    assert config.refus_modele("mistral-large-2411") is None
    assert config.refus_modele("mistral-medium-2505") is not None
    assert config.refus_modele("labs-mistral-large") is not None
