"""Hiérarchie d'erreurs et conversion en code de sortie par la CLI (critère 4, story 1.2)."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

import slmsp.cli
from slmsp.core import erreurs
from slmsp.core.erreurs import (
    AppelNonConforme,
    BudgetEpuise,
    CodeSortie,
    ConfigurationInvalide,
    HoteBloque,
    LectureInterdite,
    ManifesteInvalide,
    ProvenanceInvalide,
    RessourceOccupee,
    SchemaOutilModifie,
    SecretManquant,
    SlmspError,
    SourceSansLicence,
    TarifInconnu,
)

CODES_ATTENDUS = {
    BudgetEpuise: 3,
    ManifesteInvalide: 4,
    RessourceOccupee: 5,
    HoteBloque: 1,
    AppelNonConforme: 1,
    SchemaOutilModifie: 1,
    SourceSansLicence: 1,
    ProvenanceInvalide: 1,
    LectureInterdite: 1,
    TarifInconnu: 1,
    ConfigurationInvalide: 1,
    SecretManquant: 1,
}


def test_code_sortie_meme_classe_que_cli() -> None:
    assert slmsp.cli.CodeSortie is erreurs.CodeSortie
    assert [int(code) for code in CodeSortie] == [0, 1, 2, 3, 4, 5]


def test_racine_code_un() -> None:
    assert issubclass(SlmspError, Exception)
    assert SlmspError.code_sortie == CodeSortie.ERREUR


@pytest.mark.parametrize(("classe", "code"), list(CODES_ATTENDUS.items()))
def test_sous_classes_et_codes(classe: type[SlmspError], code: int) -> None:
    assert issubclass(classe, SlmspError)
    assert classe.code_sortie == code
    assert isinstance(classe.code_sortie, CodeSortie)
    assert classe("message").code_sortie == code


def test_ressource_occupee_porte_pid_et_commande() -> None:
    exc = RessourceOccupee("GPU occupé", pid=1234, commande="slmsp train")
    assert (exc.pid, exc.commande, str(exc)) == (1234, "slmsp train", "GPU occupé")
    assert RessourceOccupee("x").pid is None


SYNTHETIQUES = [
    "zz_erreur_budget",
    "zz_erreur_vide",
    "zz_erreur_autre",
    "zz_erreur_lignes",
    "zz_erreur_import",
    "zz_erreur_enregistrer",
]


@pytest.fixture
def dossier_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Déclare des sous-commandes synthétiques servies depuis `tmp_path`."""
    monkeypatch.setattr(slmsp.cli, "__path__", [*slmsp.cli.__path__, str(tmp_path)])
    for nom in SYNTHETIQUES:
        monkeypatch.setitem(slmsp.cli.SOUS_COMMANDES, nom, f"aide de {nom}")
    importlib.invalidate_caches()
    yield tmp_path
    for nom in SYNTHETIQUES:
        sys.modules.pop(f"slmsp.cli.{nom}", None)


def _commande_qui_leve(dossier: Path, nom: str, expression: str) -> None:
    (dossier / f"{nom}.py").write_text(
        "from slmsp.core import erreurs\n"
        "\n"
        "def executer(args):\n"
        f"    raise {expression}\n"
        "\n"
        "def enregistrer(sous_parseurs):\n"
        f"    sous_parseurs.add_parser({nom!r}).set_defaults(func=executer)\n",
        encoding="utf-8",
    )


def test_cli_convertit_slmsp_error_en_code(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _commande_qui_leve(dossier_cli, "zz_erreur_budget", "erreurs.BudgetEpuise('plafond atteint')")
    assert slmsp.cli.main(["zz_erreur_budget"]) == CodeSortie.BUDGET_EPUISE
    capture = capsys.readouterr()
    assert capture.err == "slmsp : plafond atteint\n"
    assert "Traceback" not in capture.err + capture.out


def test_cli_message_vide_affiche_la_classe(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _commande_qui_leve(dossier_cli, "zz_erreur_vide", "erreurs.RessourceOccupee('')")
    assert slmsp.cli.main(["zz_erreur_vide"]) == CodeSortie.RESSOURCE_OCCUPEE
    assert capsys.readouterr().err == "slmsp : RessourceOccupee\n"


def test_cli_message_multiligne_prefixe_chaque_ligne(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _commande_qui_leve(
        dossier_cli,
        "zz_erreur_lignes",
        "erreurs.ConfigurationInvalide('f.toml : clé « a » : x\\nf.toml : clé « b » : y')",
    )
    assert slmsp.cli.main(["zz_erreur_lignes"]) == CodeSortie.ERREUR
    assert capsys.readouterr().err == (
        "slmsp : f.toml : clé « a » : x\nslmsp : f.toml : clé « b » : y\n"
    )


def test_cli_convertit_slmsp_error_a_l_import(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (dossier_cli / "zz_erreur_import.py").write_text(
        "from slmsp.core import erreurs\nraise erreurs.ManifesteInvalide('manifeste absent')\n",
        encoding="utf-8",
    )
    assert slmsp.cli.main(["zz_erreur_import"]) == CodeSortie.MANIFESTE_INVALIDE
    capture = capsys.readouterr()
    assert capture.err == "slmsp : manifeste absent\n"
    assert "Traceback" not in capture.err + capture.out


def test_cli_convertit_slmsp_error_dans_enregistrer(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (dossier_cli / "zz_erreur_enregistrer.py").write_text(
        "from slmsp.core import erreurs\n"
        "\n"
        "def enregistrer(sous_parseurs):\n"
        "    raise erreurs.RessourceOccupee('GPU occupé')\n",
        encoding="utf-8",
    )
    assert slmsp.cli.main(["zz_erreur_enregistrer"]) == CodeSortie.RESSOURCE_OCCUPEE
    assert capsys.readouterr().err == "slmsp : GPU occupé\n"


def test_cli_laisse_passer_les_autres_exceptions(dossier_cli: Path) -> None:
    _commande_qui_leve(dossier_cli, "zz_erreur_autre", "RuntimeError('bogue')")
    with pytest.raises(RuntimeError, match="bogue"):
        slmsp.cli.main(["zz_erreur_autre"])
