"""Préalables de `slmsp data generate` (story 9.4, D1.2, D1.3) : refus avant toute écriture.

Dépôt git de fixture dans `tmp_path`. Aucun appel réel : la commande s'arrête avant de
construire le client Mistral. Aucun texte de Donnée d'entraînement n'est écrit ici.
"""

from __future__ import annotations

import subprocess
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.var import dossier_var

SEED = "20261012-000000-seed-0a1b"


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    racine = tmp_path / "depot"
    racine.mkdir()
    subprocess.run(["git", "init", "-q", str(racine)], check=True, capture_output=True)
    return racine


def _rien_ecrit(racine: Path) -> None:
    assert not (racine / "runs" / "data-generate").exists()
    assert not (dossier_var() / "appels-mistral.sqlite").exists()
    assert not (dossier_var() / "budget.sqlite").exists()


def test_gel_absent_code_4(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["data", "generate", "--depuis", SEED, "--racine", str(depot)])
    assert code == CodeSortie.MANIFESTE_INVALIDE
    assert "slmsp :" in capsys.readouterr().err
    _rien_ecrit(depot)


def test_gel_non_ancetre_code_4(depot: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuser(version: str, racine: Any = None) -> Any:
        raise ManifesteInvalide(f"commit de gel du jeu {version} non ancêtre de HEAD")

    monkeypatch.setattr("slmsp.evaluation.gel.jeu_gele_et_commite", refuser)
    code = main(["data", "generate", "--depuis", SEED, "--racine", str(depot)])
    assert code == CodeSortie.MANIFESTE_INVALIDE
    _rien_ecrit(depot)


def test_conditions_mistral_d_hier_code_1(
    depot: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    projet = tmp_path / "projet"
    (projet / "config").mkdir(parents=True)
    hier = date.today() - timedelta(days=1)
    (projet / "config" / "donnees.toml").write_text(
        f"[mistral]\nconditions_verifiees_le = {hier}\n"
        'modeles_stables = ["mistral-large-latest"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "slmsp.evaluation.gel.jeu_gele_et_commite",
        lambda version, racine=None: type("Gel", (), {"commit_gel": "0" * 40})(),
    )
    monkeypatch.setattr("slmsp.cli.data.racine_projet", lambda: projet)
    monkeypatch.setattr("slmsp.cli.data._verifier_conditions", lambda **_: None)  # C9 neutralisée
    assert racine_projet() != projet
    code = main(["data", "generate", "--depuis", SEED, "--racine", str(depot)])
    assert code == CodeSortie.ERREUR
    assert f"vérifiées le {hier}" in capsys.readouterr().err
    _rien_ecrit(depot)


def test_conditions_changees_bloquent_avant_tout_appel_mistral(
    depot: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    projet = tmp_path / "projet"
    (projet / "config").mkdir(parents=True)
    hier = date.today() - timedelta(days=1)
    donnees = projet / "config" / "donnees.toml"
    donnees.write_text(
        f"[mistral]\nconditions_verifiees_le = {hier}\n"
        'conditions_url = "https://exemple.invalide/"\n'
        f'conditions_sha256 = "{"0" * 64}"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "slmsp.evaluation.gel.jeu_gele_et_commite",
        lambda version, racine=None: type("Gel", (), {"commit_gel": "0" * 40})(),
    )
    monkeypatch.setattr("slmsp.cli.data.racine_projet", lambda: projet)
    monkeypatch.setattr("slmsp.core.var.dossier_var", lambda: tmp_path / "var")

    class _Client:
        def __enter__(self) -> Any:
            return self

        def __exit__(self, *_: Any) -> None:
            return None

        def get(self, url: str) -> Any:
            return type("R", (), {"content": b"<autre>", "raise_for_status": lambda s: None})()

    monkeypatch.setattr("slmsp.net.client", lambda profil: _Client())
    monkeypatch.setattr(
        "slmsp.mistral.client.fabriquer_sdk",
        lambda *_: pytest.fail("appel Mistral avant la vérification des conditions"),
    )
    code = main(["data", "generate", "--depuis", SEED, "--racine", str(depot)])
    assert code == CodeSortie.ERREUR
    assert "conditions Mistral modifiées" in capsys.readouterr().err
    assert f"conditions_verifiees_le = {hier}" in donnees.read_text(encoding="utf-8")
    _rien_ecrit(depot)


def test_depuis_et_reprendre_exclusifs() -> None:
    assert main(["data", "generate"]) == CodeSortie.USAGE
    assert main(["data", "generate", "--depuis", SEED, "--reprendre", SEED]) == CodeSortie.USAGE
    assert main(["data", "generate", "--depuis", SEED, "--surplus", "2"]) == CodeSortie.USAGE
