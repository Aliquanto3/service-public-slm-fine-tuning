"""Format de cassette unique : lecture (héritées comprises) et écriture (story 3.1, AD-10)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas.cassette import Cassette, Interaction, Simulation, TypeSimulation
from slmsp.mcp.cassettes import (
    ecrire_cassette,
    empreinte_tools_list,
    extraire_tools_list,
    lire_cassette,
)
from slmsp.mcp.erreurs import (
    PAR_TYPE_SIMULATION,
    CassetteInvalide,
    DelaiDepasse,
    ErreurHttp,
    ErreurTransportMcp,
    Injoignable,
)
from slmsp.mcp.outils import charger_config

RACINE = Path(__file__).resolve().parents[2]
CASSETTES = RACINE / "eval" / "calibrage" / "cassettes"
SHA_FACTICE = "0" * 64


def _etat_calibrage() -> dict[str, tuple[str, int]]:
    return {
        p.name: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
        for p in sorted(CASSETTES.iterdir())
    }


@pytest.fixture
def calibrage_intact() -> Iterator[None]:
    avant = _etat_calibrage()
    yield
    assert _etat_calibrage() == avant


def _requete(id_: int, nom: str = "search_datasets") -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "method": "tools/call",
        "params": {"name": nom, "arguments": {"query": "<requete-factice>"}},
    }


def _reponse(id_: int, texte: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "result": {"content": [{"type": "text", "text": texte}], "isError": False},
    }


def _brute(**surcharges: Any) -> dict[str, Any]:
    donnees: dict[str, Any] = {
        "server": "http://serveur-factice.invalid/mcp",
        "recorded_at": "2026-10-12T05:43:56+02:00",
        "initialize": {"jsonrpc": "2.0", "id": 1, "result": {}},
        "interactions": [{"request": _requete(2), "response": _reponse(2, "<réponse-factice-1>")}],
    }
    donnees.update(surcharges)
    return donnees


def _ecrire_json(chemin: Path, donnees: Any) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")
    return chemin


def _tools_list_factice(dossier: Path) -> list[dict[str, Any]]:
    tools = [{"name": "outil-factice", "inputSchema": {"type": "object"}}]
    _ecrire_json(
        dossier / "tools-list.json",
        _brute(
            interactions=[
                {
                    "request": {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                    "response": {"jsonrpc": "2.0", "id": 2, "result": {"tools": tools}},
                }
            ]
        ),
    )
    return tools


def _cassette(**surcharges: Any) -> Cassette:
    donnees = {"schema_version": 1, "tools_list_sha256": SHA_FACTICE, **_brute(), **surcharges}
    return Cassette.model_validate(donnees)


# --- Erreurs de transport --------------------------------------------------------------------


def test_erreurs_de_transport() -> None:
    assert set(PAR_TYPE_SIMULATION) == set(get_args(TypeSimulation))
    assert PAR_TYPE_SIMULATION["delai_depasse"] is DelaiDepasse
    assert PAR_TYPE_SIMULATION["erreur_http"] is ErreurHttp
    assert PAR_TYPE_SIMULATION["injoignable"] is Injoignable
    for type_, classe in PAR_TYPE_SIMULATION.items():
        assert issubclass(classe, ErreurTransportMcp)
        assert issubclass(classe, SlmspError)
        assert classe.type_simulation == type_
    assert ErreurHttp("panne", statut=503).statut == 503
    assert ErreurHttp("panne").statut is None
    assert issubclass(CassetteInvalide, SlmspError)


# --- Cassettes héritées du calibrage ---------------------------------------------------------


@pytest.mark.parametrize("nom", ["R-001.json", "R-002.json", "tools-list.json"])
def test_cassette_heritee_du_calibrage(nom: str, calibrage_intact: None) -> None:
    cassette = lire_cassette(CASSETTES / nom)
    assert cassette.schema_version == 1
    assert cassette.tools_list_sha256 == charger_config().tools_list_sha256
    assert cassette.server == "https://mcp.data.gouv.fr/mcp"
    assert cassette.recorded_at.utcoffset() is not None
    assert all(i.response is not None and i.simulation is None for i in cassette.interactions)


def test_empreinte_tools_list_du_calibrage(calibrage_intact: None) -> None:
    donnees = json.loads((CASSETTES / "tools-list.json").read_text(encoding="utf-8"))
    tools = extraire_tools_list(donnees)
    assert len(tools) == 10
    assert empreinte_tools_list(tools) == sha256_hex(json_canonique(tools))
    assert extraire_tools_list(lire_cassette(CASSETTES / "tools-list.json")) == tools


def test_extraire_tools_list_absente() -> None:
    with pytest.raises(CassetteInvalide):
        extraire_tools_list(_brute())
    with pytest.raises(CassetteInvalide):
        extraire_tools_list({})


def test_heritee_synthetique(tmp_path: Path) -> None:
    tools = _tools_list_factice(tmp_path)
    chemin = _ecrire_json(tmp_path / "S-001.json", _brute())
    avant = chemin.read_bytes()
    cassette = lire_cassette(chemin)
    assert cassette.tools_list_sha256 == empreinte_tools_list(tools)
    assert chemin.read_bytes() == avant


def test_heritee_sans_voisin(tmp_path: Path) -> None:
    chemin = _ecrire_json(tmp_path / "S-001.json", _brute())
    with pytest.raises(CassetteInvalide, match="tools-list.json"):
        lire_cassette(chemin)


def test_heritee_avec_empreinte_refusee(tmp_path: Path) -> None:
    _tools_list_factice(tmp_path)
    chemin = _ecrire_json(tmp_path / "S-001.json", _brute(tools_list_sha256=SHA_FACTICE))
    with pytest.raises(CassetteInvalide):
        lire_cassette(chemin)


# --- Cassette illisible ----------------------------------------------------------------------


def test_json_invalide(tmp_path: Path) -> None:
    chemin = tmp_path / "S-001.json"
    chemin.write_text('{"server": "<secret-factice>"', encoding="utf-8")
    with pytest.raises(CassetteInvalide) as info:
        lire_cassette(chemin)
    assert str(chemin) in str(info.value)
    assert "<secret-factice>" not in str(info.value)


def test_fichier_non_utf8(tmp_path: Path) -> None:
    chemin = tmp_path / "S-001.json"
    chemin.write_bytes(b"\xff\xfe{")
    with pytest.raises(CassetteInvalide) as info:
        lire_cassette(chemin)
    assert str(chemin) in str(info.value)


def test_voisin_sans_tools_list(tmp_path: Path) -> None:
    _ecrire_json(tmp_path / "tools-list.json", _brute())
    chemin = _ecrire_json(tmp_path / "S-001.json", _brute())
    with pytest.raises(CassetteInvalide, match="tools-list.json"):
        lire_cassette(chemin)


def test_fichier_absent(tmp_path: Path) -> None:
    with pytest.raises(CassetteInvalide):
        lire_cassette(tmp_path / "absente.json")


def test_pas_un_objet(tmp_path: Path) -> None:
    chemin = _ecrire_json(tmp_path / "S-001.json", ["x"])
    with pytest.raises(CassetteInvalide):
        lire_cassette(chemin)


@pytest.mark.parametrize("cas", ["champ_manquant", "cle_inconnue", "cle_interaction_inconnue"])
def test_cassette_non_conforme(tmp_path: Path, cas: str) -> None:
    donnees = {"schema_version": 1, "tools_list_sha256": SHA_FACTICE, **_brute()}
    if cas == "champ_manquant":
        del donnees["server"]
        cle = "server"
    elif cas == "cle_inconnue":
        donnees["inconnue"] = "<valeur-factice>"
        cle = "inconnue"
    else:
        donnees["interactions"][0]["inconnue"] = "<valeur-factice>"
        cle = "interactions.0.inconnue"
    chemin = _ecrire_json(tmp_path / "S-001.json", donnees)
    with pytest.raises(CassetteInvalide) as info:
        lire_cassette(chemin)
    message = str(info.value)
    assert str(chemin) in message
    assert f"« {cle} »" in message
    assert "<valeur-factice>" not in message


# --- Écriture --------------------------------------------------------------------------------


def test_ecriture_et_relecture(tmp_path: Path) -> None:
    cassette = _cassette()
    chemin = ecrire_cassette(cassette, tmp_path / "a" / "b" / "S-001.json")
    assert chemin == tmp_path / "a" / "b" / "S-001.json"
    octets = chemin.read_bytes()
    assert b"\r" not in octets
    assert octets.endswith(b"}\n")
    texte = octets.decode("utf-8")
    assert "<réponse-factice-1>" in texte
    donnees = json.loads(texte)
    assert list(donnees) == [
        "schema_version",
        "server",
        "recorded_at",
        "initialize",
        "tools_list_sha256",
        "interactions",
    ]
    assert donnees["schema_version"] == 1
    assert donnees["tools_list_sha256"] == SHA_FACTICE
    assert donnees["recorded_at"] == "2026-10-12T05:43:56+02:00"
    assert "simulation" not in donnees["interactions"][0]
    assert texte == json.dumps(donnees, indent=1, ensure_ascii=False) + "\n"
    assert lire_cassette(chemin) == cassette


def test_relecture_d_une_heritee_ecrite(tmp_path: Path, calibrage_intact: None) -> None:
    cassette = lire_cassette(CASSETTES / "R-002.json")
    chemin = ecrire_cassette(cassette, tmp_path / "R-002.json")
    assert lire_cassette(chemin) == cassette


def test_ecrasement_refuse(tmp_path: Path) -> None:
    chemin = tmp_path / "S-001.json"
    chemin.write_bytes(b"<contenu-existant>")
    with pytest.raises(ArtefactExistant):
        ecrire_cassette(_cassette(), chemin)
    assert chemin.read_bytes() == b"<contenu-existant>"


def test_ecriture_revalide_une_cassette_mutee(tmp_path: Path) -> None:
    cassette = _cassette()
    cassette.tools_list_sha256 = "invalide"
    chemin = tmp_path / "S-001.json"
    with pytest.raises(ValidationError):
        ecrire_cassette(cassette, chemin)
    assert not chemin.exists()


def test_ecriture_refuse_un_non_cassette(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        ecrire_cassette({"schema_version": 1}, tmp_path / "S-001.json")  # type: ignore[arg-type]


# --- Simulation ------------------------------------------------------------------------------


def test_simulation_ecrite(tmp_path: Path) -> None:
    cassette = _cassette(
        initialize=None,
        recorded_at=datetime(2026, 10, 12, 3, 0, tzinfo=UTC),
        interactions=[
            Interaction(
                request=_requete(2),
                response=None,
                simulation=Simulation(type="erreur_http", statut=503),
            ),
            Interaction(request=_requete(3), response=None, simulation={"type": "injoignable"}),
            Interaction(request=_requete(4), response=_reponse(4, "<réponse-factice-2>")),
        ],
    )
    chemin = ecrire_cassette(cassette, tmp_path / "S-002.json")
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    assert donnees["initialize"] is None
    premiere, deuxieme, troisieme = donnees["interactions"]
    assert premiere["response"] is None
    assert premiere["simulation"] == {"type": "erreur_http", "statut": 503}
    assert deuxieme == {
        "request": _requete(3),
        "response": None,
        "simulation": {"type": "injoignable"},
    }
    assert set(troisieme) == {"request", "response"}
    assert lire_cassette(chemin) == cassette


@pytest.mark.parametrize(
    "interaction",
    [
        {"request": {}, "response": {"result": {}}, "simulation": {"type": "delai_depasse"}},
        {"request": {}, "response": None},
        {"request": {}, "response": None, "simulation": {"type": "delai_depasse", "statut": 503}},
        {"request": {}, "response": None, "simulation": {"type": "erreur_http", "statut": 99}},
        {"request": {}, "response": None, "simulation": {"type": "erreur_http", "statut": 600}},
        {"request": {}, "response": None, "simulation": {"type": "coupure"}},
        {"request": {}},
    ],
)
def test_interaction_incoherente(interaction: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Interaction.model_validate(interaction)


@pytest.mark.parametrize("empreinte", [None, "ABC", "A" * 64, "0" * 63])
def test_empreinte_invalide(empreinte: str | None) -> None:
    donnees = {"schema_version": 1, **_brute()}
    if empreinte is not None:
        donnees["tools_list_sha256"] = empreinte
    with pytest.raises(ValidationError):
        Cassette.model_validate(donnees)


def test_date_sans_fuseau_refusee() -> None:
    with pytest.raises(ValidationError):
        _cassette(recorded_at="2026-10-12T05:43:56")


def test_version_inconnue_refusee() -> None:
    with pytest.raises(ValidationError):
        _cassette(schema_version=2)
