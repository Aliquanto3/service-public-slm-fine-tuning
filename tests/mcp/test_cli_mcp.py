"""Sous-commande `slmsp mcp` : `record` et `sante` (story 3.3).

La racine du projet vue par la commande est remplacée par `tmp_path` : aucune cassette
n'est jamais écrite sous `eval/` du dépôt. Les seuls tests réels sont marqués `reseau`.
"""

from __future__ import annotations

import functools
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest

import slmsp.cli.mcp as cli_mcp
from slmsp.cli import CodeSortie, main
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.direct import McpEnDirect, sonder_sante
from slmsp.mcp.outils import charger_config
from slmsp.net.journal import JournalMemoire


def _charger_factice() -> ModuleType:
    nom = "serveur_mcp_factice"
    if nom not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            nom, Path(__file__).with_name("serveur_mcp_factice.py")
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[nom] = module
        spec.loader.exec_module(module)
    return sys.modules[nom]


factice = _charger_factice()

APPELS = [
    {"nom": "search_datasets", "arguments": {"query": "<requete-factice>"}},
    {"nom": "get_dataset_info", "arguments": {"dataset_id": "<id-factice>"}},
]


@pytest.fixture
def racine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    racine = tmp_path / "depot"
    racine.mkdir()
    monkeypatch.setattr(cli_mcp, "racine_projet", lambda: racine)
    return racine


@pytest.fixture
def serveur(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Serveur factice branché sur `McpEnDirect` tel que l'emploie la commande."""
    serveur = factice.ServeurMcpFactice()
    monkeypatch.setattr(
        cli_mcp,
        "McpEnDirect",
        functools.partial(
            McpEnDirect, journal=JournalMemoire(), transport_interne=serveur.transport()
        ),
    )
    return serveur


@pytest.fixture
def interdire_connexion(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuser(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("aucune connexion n'est permise ici")

    monkeypatch.setattr(cli_mcp, "McpEnDirect", refuser)


def _fichier_appels(dossier: Path, contenu: Any) -> Path:
    chemin = dossier / "appels.json"
    if isinstance(contenu, bytes):
        chemin.write_bytes(contenu)
    else:
        chemin.write_text(json.dumps(contenu), encoding="utf-8")
    return chemin


def _fichiers(racine: Path) -> list[str]:
    return sorted(p.relative_to(racine).as_posix() for p in racine.rglob("*") if p.is_file())


# --- record en direct (serveur factice) ------------------------------------------------------


def test_record_en_direct(
    racine: Path, serveur: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    appels = _fichier_appels(tmp_path, APPELS)
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels), "--session", "s1"])
    assert code == CodeSortie.SUCCES, capsys.readouterr().err
    chemin = racine / "eval" / "cassettes" / "RD-007" / "s1.json"
    assert str(chemin) in capsys.readouterr().out
    cassette = lire_cassette(chemin)
    assert cassette.initialize is not None
    assert cassette.tools_list_sha256 == charger_config().tools_list_sha256
    assert [i.request["params"]["name"] for i in cassette.interactions] == [
        "search_datasets",
        "get_dataset_info",
    ]
    assert serveur.methodes[:3] == ["initialize", "notifications/initialized", "tools/list"]
    assert _fichiers(racine) == ["eval/cassettes/RD-007/s1.json"]


def test_record_identifiant_de_session_par_defaut(
    racine: Path, serveur: Any, tmp_path: Path
) -> None:
    appels = _fichier_appels(tmp_path, APPELS[:1])
    assert main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)]) == 0
    (fichier,) = _fichiers(racine)
    assert fichier.startswith("eval/cassettes/RD-007/") and fichier.endswith(".json")


def test_record_erreur_jsonrpc_enregistree(
    racine: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    serveur = factice.ServeurMcpFactice(erreur_jsonrpc=True)
    monkeypatch.setattr(
        cli_mcp,
        "McpEnDirect",
        functools.partial(
            McpEnDirect, journal=JournalMemoire(), transport_interne=serveur.transport()
        ),
    )
    appels = _fichier_appels(tmp_path, APPELS[:1])
    assert (
        main(["mcp", "record", "--item", "RD-007", "--appels", str(appels), "--session", "s1"]) == 0
    )
    assert "erreur JSON-RPC" in capsys.readouterr().err
    cassette = lire_cassette(racine / "eval" / "cassettes" / "RD-007" / "s1.json")
    assert "error" in (cassette.interactions[0].response or {})


def test_record_panne_rien_ecrit(
    racine: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    serveur = factice.ServeurMcpFactice(statut_post=(4, 503))
    monkeypatch.setattr(
        cli_mcp,
        "McpEnDirect",
        functools.partial(
            McpEnDirect, journal=JournalMemoire(), transport_interne=serveur.transport()
        ),
    )
    appels = _fichier_appels(tmp_path, APPELS)
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)])
    assert code == CodeSortie.ERREUR
    erreur = capsys.readouterr().err
    assert "503" in erreur and "Traceback" not in erreur
    assert _fichiers(racine) == []


# --- record simulé (aucune connexion) --------------------------------------------------------


def test_record_simule(
    racine: Path, interdire_connexion: None, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    appels = _fichier_appels(tmp_path, APPELS)
    code = main(
        [
            "mcp",
            "record",
            "--item",
            "RD-007",
            "--appels",
            str(appels),
            "--simulation",
            "erreur_http",
            "--statut",
            "503",
            "--session",
            "s1",
        ]
    )
    assert code == CodeSortie.SUCCES, capsys.readouterr().err
    cassette = lire_cassette(racine / "eval" / "cassettes" / "RD-007" / "s1.json")
    assert cassette.initialize is None
    assert len(cassette.interactions) == len(APPELS)
    for interaction in cassette.interactions:
        assert interaction.response is None
        assert interaction.simulation is not None
        assert interaction.simulation.model_dump() == {"type": "erreur_http", "statut": 503}


def test_fichier_d_appels_avec_bom(racine: Path, interdire_connexion: None, tmp_path: Path) -> None:
    """PowerShell 5.1 écrit un BOM UTF-8 : le fichier reste lisible."""
    appels = tmp_path / "appels.json"
    appels.write_bytes(b"\xef\xbb\xbf" + json.dumps(APPELS[:1]).encode("utf-8"))
    argv = ["mcp", "record", "--item", "RD-7", "--appels", str(appels), "--simulation"]
    assert main([*argv, "injoignable"]) == CodeSortie.SUCCES
    assert len(_fichiers(racine)) == 1


@pytest.mark.parametrize("type_", ["delai_depasse", "injoignable"])
def test_record_simule_sans_statut(
    racine: Path, interdire_connexion: None, tmp_path: Path, type_: str
) -> None:
    appels = _fichier_appels(tmp_path, APPELS[:1])
    argv = ["mcp", "record", "--item", "RD-7", "--appels", str(appels), "--simulation", type_]
    assert main(argv) == CodeSortie.SUCCES
    (fichier,) = _fichiers(racine)
    (interaction,) = lire_cassette(racine / fichier).interactions
    assert interaction.simulation is not None and interaction.simulation.type == type_


# --- Refus avant toute connexion -------------------------------------------------------------


@pytest.mark.parametrize(
    "contenu",
    [
        b"{pas du json",
        b"\xff\xfe",
        b"[" * 100_000,
        {"nom": "search_datasets"},
        [],
        ["search_datasets"],
        [{"nom": "search_datasets", "arguments": {"query": "x"}, "outil": "x"}],
        [{"arguments": {"query": "x"}}],
        [{"nom": "search_datasets", "arguments": ["x"]}],
    ],
    ids=[
        "json",
        "encodage",
        "imbrication-excessive",
        "pas-une-liste",
        "liste-vide",
        "appel-non-objet",
        "cle-inconnue",
        "nom-absent",
        "arguments-non-objet",
    ],
)
def test_fichier_d_appels_fautif(
    racine: Path,
    interdire_connexion: None,
    tmp_path: Path,
    contenu: Any,
    capsys: pytest.CaptureFixture[str],
) -> None:
    appels = _fichier_appels(tmp_path, contenu)
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)])
    assert code == CodeSortie.USAGE
    erreur = capsys.readouterr().err
    assert erreur.startswith("slmsp : ") and "Traceback" not in erreur
    assert _fichiers(racine) == []


def test_fichier_d_appels_absent(racine: Path, interdire_connexion: None, tmp_path: Path) -> None:
    argv = ["mcp", "record", "--item", "RD-007", "--appels", str(tmp_path / "absent.json")]
    assert main(argv) == CodeSortie.USAGE


def test_appel_non_conforme_avant_connexion(
    racine: Path, interdire_connexion: None, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    appels = _fichier_appels(tmp_path, [APPELS[0], {"nom": "get_metrics", "arguments": {}}])
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)])
    assert code == CodeSortie.ERREUR
    assert "get_metrics" in capsys.readouterr().err
    assert _fichiers(racine) == []


def test_item_gele_avant_connexion(racine: Path, interdire_connexion: None, tmp_path: Path) -> None:
    manifeste = racine / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    manifeste.parent.mkdir(parents=True)
    manifeste.write_text(json.dumps({"items": ["RD-007"]}), encoding="utf-8")
    appels = _fichier_appels(tmp_path, APPELS)
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)])
    assert code == CodeSortie.ERREUR
    assert _fichiers(racine) == ["eval/jeu/v1.0/MANIFEST.json"]


def test_manifeste_illisible_avant_connexion(
    racine: Path, interdire_connexion: None, tmp_path: Path
) -> None:
    manifeste = racine / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    manifeste.parent.mkdir(parents=True)
    manifeste.write_text("{", encoding="utf-8")
    appels = _fichier_appels(tmp_path, APPELS)
    code = main(["mcp", "record", "--item", "RD-007", "--appels", str(appels)])
    assert code == CodeSortie.MANIFESTE_INVALIDE


def test_cassette_existante_avant_connexion(
    racine: Path, interdire_connexion: None, tmp_path: Path
) -> None:
    existante = racine / "eval" / "cassettes" / "RD-007" / "s1.json"
    existante.parent.mkdir(parents=True)
    existante.write_bytes(b"<contenu-factice>")
    appels = _fichier_appels(tmp_path, APPELS)
    argv = ["mcp", "record", "--item", "RD-007", "--appels", str(appels), "--session", "s1"]
    assert main(argv) == CodeSortie.ERREUR
    assert existante.read_bytes() == b"<contenu-factice>"


@pytest.mark.parametrize(
    "options",
    [
        ["--item", "RD/007"],
        ["--item", ".."],
        ["--item", "RD-007", "--session", "a\\b"],
        ["--item", "RD-007", "--session", ""],
        ["--item", "RD-007", "--statut", "503"],
        ["--item", "RD-007", "--simulation", "injoignable", "--statut", "503"],
        ["--item", "RD-007", "--simulation", "erreur_http", "--statut", "42"],
        ["--item", "RD-007", "--simulation", "autre"],
        [],
    ],
    ids=[
        "item-slash",
        "item-points",
        "session-antislash",
        "session-vide",
        "statut-sans-simulation",
        "statut-hors-erreur-http",
        "statut-hors-plage",
        "simulation-inconnue",
        "item-absent",
    ],
)
def test_options_fautives(
    racine: Path, interdire_connexion: None, tmp_path: Path, options: list[str]
) -> None:
    appels = _fichier_appels(tmp_path, APPELS)
    assert main(["mcp", "record", "--appels", str(appels), *options]) == CodeSortie.USAGE
    assert _fichiers(racine) == []


def test_mcp_sans_action(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["mcp"]) == CodeSortie.USAGE
    assert "record" in capsys.readouterr().err


# --- sante -----------------------------------------------------------------------------------


def _sonde_factice(monkeypatch: pytest.MonkeyPatch, statut: int | None) -> None:
    def repondre(requete: httpx2.Request) -> httpx2.Response:
        if statut is None:
            raise httpx2.ConnectError("<panne-factice>", request=requete)
        return httpx2.Response(statut, request=requete)

    monkeypatch.setattr(
        cli_mcp,
        "sonder_sante",
        functools.partial(
            sonder_sante, journal=JournalMemoire(), transport_interne=httpx2.MockTransport(repondre)
        ),
    )


def test_sante_joignable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _sonde_factice(monkeypatch, 200)
    assert main(["mcp", "sante"]) == CodeSortie.SUCCES
    assert "joignable" in capsys.readouterr().out


@pytest.mark.parametrize("statut", [503, None], ids=["503", "panne"])
def test_sante_injoignable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], statut: int | None
) -> None:
    _sonde_factice(monkeypatch, statut)
    assert main(["mcp", "sante"]) == CodeSortie.ERREUR
    assert "injoignable" in capsys.readouterr().err


# --- Serveur réel (marqués `reseau`) ---------------------------------------------------------


@pytest.mark.reseau
def test_record_reel(racine: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    appels = _fichier_appels(
        tmp_path, [{"nom": "search_datasets", "arguments": {"query": "défibrillateurs"}}]
    )
    argv = ["mcp", "record", "--item", "RD-000", "--appels", str(appels), "--session", "reel"]
    assert main(argv) == CodeSortie.SUCCES, capsys.readouterr().err
    cassette = lire_cassette(racine / "eval" / "cassettes" / "RD-000" / "reel.json")
    assert cassette.initialize is not None
    (interaction,) = cassette.interactions
    assert interaction.response is not None and "result" in interaction.response
    assert _fichiers(racine) == ["eval/cassettes/RD-000/reel.json"]


@pytest.mark.reseau
def test_sante_reelle(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["mcp", "sante"]) == CodeSortie.SUCCES, capsys.readouterr().err
