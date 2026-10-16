"""`racine_projet()` en exécutable gelé et `config/application.toml` (story 12.1)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from slmsp.core import config as cfg
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas import config_application as app
from slmsp.inference.serveur import dossier_vendor


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    for nom in ("SLMSP_RACINE", "SLMSP_MODELS_DIR", "SLMSP_VENDOR_DIR"):
        monkeypatch.delenv(nom, raising=False)


def _geler(monkeypatch: pytest.MonkeyPatch, dossier: Path) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(dossier), raising=False)


def test_depot_par_defaut() -> None:
    assert (cfg.racine_projet() / "config" / "application.toml").is_file()


def test_gele_pointe_sous_l_installation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _geler(monkeypatch, tmp_path)
    assert cfg.racine_projet() == tmp_path.resolve()
    assert dossier_vendor() == (tmp_path / "vendor").resolve()
    assert cfg.dossier_modeles() == (tmp_path / "models").resolve()


def test_gele_sans_meipass_utilise_le_dossier_de_l_exe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "Assistant.exe"))
    assert cfg.racine_projet() == tmp_path.resolve()


def test_variables_slmsp_gardent_la_priorite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _geler(monkeypatch, tmp_path / "install")
    autre = tmp_path / "autre"
    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(autre / "v"))
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(autre / "m"))
    assert dossier_vendor() == (autre / "v").resolve()
    assert cfg.dossier_modeles() == (autre / "m").resolve()
    monkeypatch.setenv("SLMSP_RACINE", str(autre))
    assert cfg.racine_projet() == autre.resolve()


def test_application_toml_charge() -> None:
    c = app.charger_config_application()
    assert c.variante == "cpu"
    assert "en" in c.langues_traduction


def test_slug_inconnu_refuse(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "config" / "modeles").mkdir(parents=True)
    (tmp_path / "config" / "application.toml").write_text(
        'modele = "inconnu"\ndossier_donnees = "d"\nlangues_traduction = ["en"]\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("SLMSP_RACINE", str(tmp_path))
    with pytest.raises(ConfigurationInvalide, match="inconnu"):
        app.charger_config_application()
