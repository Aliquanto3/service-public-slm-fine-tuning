"""Exclusivité de `measure run` et configuration du protocole (story 6.4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.erreurs import RessourceOccupee
from slmsp.core.var import verrou_gpu
from slmsp.measure.config import charger_config_mesures
from slmsp.measure.protocole import verrou_mesure


@pytest.fixture(autouse=True)
def var_isole(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "var"))


def test_verrou_tenu_refuse_avec_ressource_occupee() -> None:
    with verrou_gpu(commande="autre commande slmsp"), pytest.raises(RessourceOccupee):
        with verrou_mesure():
            pass


def test_measure_run_refuse_avec_le_code_5(capsys: pytest.CaptureFixture[str]) -> None:
    with verrou_gpu(commande="autre commande slmsp"):
        code = main(["measure", "run", "--modele", "base:granite-4.0-1b"])
    assert code == CodeSortie.RESSOURCE_OCCUPEE == 5
    assert "GPU occupé" in capsys.readouterr().err


def test_modele_mal_forme_est_une_erreur_d_usage(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["measure", "run", "--modele", "granite"]) == CodeSortie.USAGE


def test_config_mesures_du_depot() -> None:
    config = charger_config_mesures()
    assert config.periode_ms == 100
    assert config.seuils.ram_max_go == 5.0 and config.seuils.debit_min_tps == 8.0
    assert config.seuils.premier_token_max_s == 5.0 and config.seuils.taille_max_go == 4.0
    assert len(config.questions) >= 3


@pytest.mark.lent
def test_reel_measure_run() -> None:
    pytest.skip("mesure réelle : `uv run slmsp measure run --modele base:granite-4.0-1b`")
