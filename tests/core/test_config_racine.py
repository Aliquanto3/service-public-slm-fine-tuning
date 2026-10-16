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


# --- Racine d'écriture (revue 12.1, AD-23) ---------------------------------------------


def _installation(dossier: Path, donnees: str) -> None:
    (dossier / "config" / "modeles").mkdir(parents=True)
    (dossier / "config" / "modeles" / "m.toml").write_text("", encoding="utf-8")
    (dossier / "config" / "application.toml").write_text(
        f'modele = "m"\ndossier_donnees = \'{donnees}\'\nlangues_traduction = ["en"]\n',
        encoding="utf-8",
    )


def test_ecriture_depot_egale_racine_projet() -> None:
    assert cfg.racine_ecriture() == cfg.racine_projet()


def test_ecriture_suit_slmsp_racine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _geler(monkeypatch, tmp_path / "install")
    monkeypatch.setenv("SLMSP_RACINE", str(tmp_path / "r"))
    assert cfg.racine_ecriture() == (tmp_path / "r").resolve()


def test_ecriture_gelee_sous_les_donnees_jamais_meipass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core import artefacts

    install = tmp_path / "install"
    _installation(install, r"%LOCALAPPDATA%\AssistantSP")
    _geler(monkeypatch, install)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    attendu = (tmp_path / "local" / "AssistantSP").resolve()
    assert cfg.racine_projet() == install.resolve()
    assert cfg.racine_ecriture() == attendu
    assert artefacts._racine(None) == attendu
    assert not attendu.is_relative_to(install.resolve())


def test_dossier_donnees_variable_absente_refuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SLMSP_INEXISTANTE", raising=False)
    with pytest.raises(ConfigurationInvalide, match="non définie"):
        cfg.etendre_chemin(r"%SLMSP_INEXISTANTE%\x")
    with pytest.raises(ConfigurationInvalide, match="absolu"):
        cfg.etendre_chemin("relatif")


@pytest.mark.parametrize("slug", ["..", "../m", "a/b", "a\b", "base:m", ""])
def test_slug_mal_forme_refuse_sans_echo(
    slug: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _installation(tmp_path, "d")
    toml = tmp_path / "config" / "application.toml"
    toml.write_text(toml.read_text(encoding="utf-8").replace('"m"', repr(slug)), encoding="utf-8")
    monkeypatch.setenv("SLMSP_RACINE", str(tmp_path))
    with pytest.raises(ConfigurationInvalide, match="mal formé") as erreur:
        app.charger_config_application()
    if slug:
        assert slug not in str(erreur.value).replace(str(tmp_path), "")


@pytest.mark.parametrize("langues", [[], ["en", "en"], ["EN"], ["e"], ["it"], ["en", "zh"]])
def test_langues_invalides_refusees(langues: list[str]) -> None:
    with pytest.raises(ValueError):
        app.ConfigApplication(
            modele="granite-4.0-1b", dossier_donnees="d", langues_traduction=langues
        )


def test_langues_acceptees_sont_celles_de_la_tache_tr() -> None:
    from slmsp.core.langues import LANGUES

    config = app.ConfigApplication(
        modele="granite-4.0-1b", dossier_donnees="d", langues_traduction=list(LANGUES)
    )
    assert config.langues_traduction == list(LANGUES)
