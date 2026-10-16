"""Critères 1, 2 et 10 de la story 1.1 : registre des sous-commandes et codes de sortie."""

from __future__ import annotations

import importlib
import importlib.metadata
import io
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

import slmsp.cli
from slmsp.cli import SOUS_COMMANDES, CodeSortie, main

ATTENDUES = [
    "fetch",
    "index",
    "ask",
    "mcp",
    "eval",
    "bench",
    "measure",
    "data",
    "train",
    "export",
    "compare",
    "budget",
    "publication",
]

RACINE_CLI = Path(slmsp.cli.__file__).parent
SYNTHETIQUES = ["zz_absente", "zz_presente", "zz_dependance", "zz_dll", "zz_none", "zz_explosive"]


def test_sous_commandes_declarees() -> None:
    assert list(SOUS_COMMANDES) == ATTENDUES


def test_aide_liste_les_sous_commandes(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "120")
    assert main(["--help"]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    for nom in ATTENDUES:
        assert f"    {nom} " in sortie


def test_python_m_slmsp_aide() -> None:
    resultat = subprocess.run(
        [sys.executable, "-m", "slmsp", "--help"],
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "COLUMNS": "120"},
        check=False,
    )
    assert resultat.returncode == 0, resultat.stderr
    for nom in ATTENDUES:
        assert f"    {nom} " in resultat.stdout


def test_script_console_declare() -> None:
    points = importlib.metadata.entry_points(group="console_scripts").select(name="slmsp")
    assert [point.value for point in points] == ["slmsp.cli:main"]


def test_sans_sous_commande(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == CodeSortie.USAGE
    capture = capsys.readouterr()
    assert "usage: slmsp" in capture.err
    assert capture.out == ""


def test_argument_inconnu(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--inconnu"]) == CodeSortie.USAGE
    assert "--inconnu" in capsys.readouterr().err


@pytest.mark.parametrize("nom", ATTENDUES)
def test_commande_declaree_sans_module_non_implementee(
    nom: str, capsys: pytest.CaptureFixture[str]
) -> None:
    if (RACINE_CLI / f"{nom}.py").exists() or (RACINE_CLI / nom / "__init__.py").exists():
        pytest.skip(f"le module slmsp.cli.{nom} existe")
    assert main([nom, "argument", "--option"]) == CodeSortie.USAGE
    assert f"commande non implémentée : {nom}" in capsys.readouterr().err


@pytest.fixture
def dossier_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Déclare des sous-commandes synthétiques et ajoute `tmp_path` au paquet `slmsp.cli`."""
    monkeypatch.setattr(slmsp.cli, "__path__", [*slmsp.cli.__path__, str(tmp_path)])
    for nom in SYNTHETIQUES:
        monkeypatch.setitem(slmsp.cli.SOUS_COMMANDES, nom, f"aide de {nom}")
    importlib.invalidate_caches()
    yield tmp_path
    for nom in SYNTHETIQUES:
        sys.modules.pop(f"slmsp.cli.{nom}", None)


def _module(dossier: Path, nom: str, source: str) -> None:
    (dossier / f"{nom}.py").write_text(source, encoding="utf-8")


def test_module_absent_non_implementee(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["zz_absente", "argument", "--option"]) == CodeSortie.USAGE
    assert "commande non implémentée : zz_absente" in capsys.readouterr().err


def test_module_present_charge_sans_modifier_init(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _module(
        dossier_cli,
        "zz_presente",
        "def executer(args):\n"
        "    print('cible=' + args.cible)\n"
        "    return 4\n"
        "\n"
        "def enregistrer(sous_parseurs):\n"
        "    parseur = sous_parseurs.add_parser('zz_presente')\n"
        "    parseur.add_argument('cible')\n"
        "    parseur.set_defaults(func=executer)\n",
    )
    assert main(["zz_presente", "x"]) == CodeSortie.MANIFESTE_INVALIDE
    assert "cible=x" in capsys.readouterr().out
    # Le vrai sous-parseur refuse les arguments en trop.
    assert main(["zz_presente", "x", "y"]) == CodeSortie.USAGE


def test_func_renvoyant_none_vaut_succes(dossier_cli: Path) -> None:
    _module(
        dossier_cli,
        "zz_none",
        "def enregistrer(sous_parseurs):\n"
        "    sous_parseurs.add_parser('zz_none').set_defaults(func=lambda args: None)\n",
    )
    assert main(["zz_none"]) == CodeSortie.SUCCES


def test_dependance_manquante_indisponible(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _module(
        dossier_cli,
        "zz_dependance",
        "import bibliotheque_absente_slmsp\n\ndef enregistrer(sous_parseurs):\n    pass\n",
    )
    assert main(["zz_dependance", "run"]) == CodeSortie.ERREUR
    erreur = capsys.readouterr().err
    assert "commande indisponible : zz_dependance" in erreur
    assert "bibliotheque_absente_slmsp" in erreur
    assert "Traceback" not in erreur


def test_dll_introuvable_indisponible(
    dossier_cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _module(dossier_cli, "zz_dll", "raise OSError('DLL load failed')\n")
    assert main(["zz_dll"]) == CodeSortie.ERREUR
    erreur = capsys.readouterr().err
    assert "commande indisponible : zz_dll" in erreur
    assert "DLL load failed" in erreur
    assert "Traceback" not in erreur


def test_aide_n_importe_aucun_module(dossier_cli: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _module(dossier_cli, "zz_explosive", "raise RuntimeError('importé par --help')\n")
    assert main(["--help"]) == CodeSortie.SUCCES
    assert "zz_explosive" in capsys.readouterr().out
    assert "slmsp.cli.zz_explosive" not in sys.modules


def test_codes_de_sortie_nommes() -> None:
    assert {code.name: int(code) for code in CodeSortie} == {
        "SUCCES": 0,
        "ERREUR": 1,
        "USAGE": 2,
        "BUDGET_EPUISE": 3,
        "MANIFESTE_INVALIDE": 4,
        "RESSOURCE_OCCUPEE": 5,
    }


def test_sortie_reconfiguree_en_utf8(monkeypatch: pytest.MonkeyPatch) -> None:
    sortie = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    erreur = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="backslashreplace")
    monkeypatch.setattr(sys, "stdout", sortie)
    monkeypatch.setattr(sys, "stderr", erreur)
    assert main(["--help"]) == CodeSortie.SUCCES
    assert sys.stdout.encoding == "utf-8"
    assert sys.stderr.encoding == "utf-8"
    assert sys.stderr.errors == "backslashreplace"
    sys.stdout.flush()
    assert "Données".encode() in sortie.buffer.getvalue()
