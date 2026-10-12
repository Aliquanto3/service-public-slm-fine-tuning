"""`harness.config` : `config/harnais.toml` et `k`/seuil de l'Index (story 4.2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.harness.config import ConfigHarnais, charger_config_harnais, chemin_config_harnais
from slmsp.index.config import charger_config_index

VALIDE = """
schema_version = 1
[outils]
iterations_max = 3
delai_appel_s = 2.5
[modes]
periode_sonde_s = 60
delai_sonde_s = 1
[compte_rendu]
reserve_sortie_tokens = 512
chevauchement_paragraphes = 0
"""


def test_config_par_defaut() -> None:
    config = charger_config_harnais()
    index = charger_config_index()
    assert chemin_config_harnais().is_file()
    assert config.recherche.k == index.k
    assert config.recherche.seuil_pertinence == index.seuil_pertinence
    assert config.outils.iterations_max > 0
    assert config.outils.delai_appel_s == 10
    assert config.modes.periode_sonde_s == 300
    assert config.modes.delai_sonde_s == 3
    assert config.compte_rendu.reserve_sortie_tokens > 0
    assert config.compte_rendu.chevauchement_paragraphes >= 0


def test_k_et_seuil_absents_de_harnais_toml() -> None:
    contenu = chemin_config_harnais().read_text(encoding="utf-8")
    assert "seuil_pertinence =" not in contenu and "\nk =" not in contenu


def test_config_figee() -> None:
    config = charger_config_harnais()
    with pytest.raises(ValidationError):
        config.outils.iterations_max = 99  # type: ignore[misc]
    with pytest.raises(ValidationError):
        config.recherche = config.recherche  # type: ignore[misc]
    assert isinstance(config, ConfigHarnais)


def test_fichier_et_index_fournis(tmp_path: Path) -> None:
    chemin = tmp_path / "harnais.toml"
    chemin.write_text(VALIDE, encoding="utf-8")
    index = charger_config_index().model_copy(update={"k": 7, "seuil_pertinence": 0.25})
    config = charger_config_harnais(chemin, config_index=index)
    assert config.outils.iterations_max == 3
    assert config.modes.periode_sonde_s == 60
    assert config.compte_rendu.chevauchement_paragraphes == 0
    assert (config.recherche.k, config.recherche.seuil_pertinence) == (7, 0.25)


@pytest.mark.parametrize(
    "contenu",
    [
        VALIDE + "inconnue = 1\n",
        VALIDE.replace("iterations_max = 3", "iterations_max = 0"),
        VALIDE.replace("schema_version = 1", "schema_version = 2"),
        VALIDE.replace("[modes]\nperiode_sonde_s = 60\ndelai_sonde_s = 1\n", ""),
        VALIDE + "[recherche]\nk = 3\n",
    ],
)
def test_fichier_invalide(tmp_path: Path, contenu: str) -> None:
    chemin = tmp_path / "harnais.toml"
    chemin.write_text(contenu, encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_config_harnais(chemin)


def test_fichier_absent(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_config_harnais(tmp_path / "absent.toml")
