"""API unique d'enregistrement des cassettes : magasins `eval` et `data` (story 3.3, AD-10).

Tout est écrit sous `tmp_path` (racine factice) : `eval/` du dépôt n'est jamais touché.
"""

from __future__ import annotations

import builtins
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.erreurs import AppelNonConforme, ManifesteInvalide
from slmsp.core.schemas.cassette import Cassette, Interaction
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.enregistrement import (
    URL_SERVEUR,
    ItemGele,
    SessionMcp,
    chemin_cassette,
    enregistrer,
    nouvel_identifiant_session,
    session_de_panne,
    verifier_item_libre,
)
from slmsp.mcp.outils import charger_config


def _cassette() -> Cassette:
    requete = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "search_datasets", "arguments": {"query": "<requete-factice>"}},
    }
    reponse = {
        "jsonrpc": "2.0",
        "id": 3,
        "result": {"content": [{"type": "text", "text": "<reponse-factice-1>"}], "isError": False},
    }
    return Cassette(
        schema_version=1,
        server=URL_SERVEUR,
        recorded_at=datetime(2026, 10, 12, tzinfo=UTC),
        initialize={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18"}},
        tools_list_sha256=charger_config().tools_list_sha256,
        interactions=[Interaction(request=requete, response=reponse)],
    )


def _manifeste(racine: Path, contenu: Any, version: str = "v1.0") -> Path:
    chemin = racine / "eval" / "jeu" / version / "MANIFEST.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = contenu if isinstance(contenu, str) else json.dumps(contenu)
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def _fichiers(racine: Path) -> list[str]:
    return sorted(p.relative_to(racine).as_posix() for p in racine.rglob("*") if p.is_file())


# --- Magasin eval ----------------------------------------------------------------------------


def test_magasin_eval(tmp_path: Path) -> None:
    session = SessionMcp(_cassette(), "s1", "RD-007")
    chemin = enregistrer(session, "eval", racine=tmp_path)
    assert chemin == tmp_path / "eval" / "cassettes" / "RD-007" / "s1.json"
    assert lire_cassette(chemin) == session.cassette


def test_racine_par_defaut(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import slmsp.mcp.enregistrement as module

    monkeypatch.setattr(module, "racine_projet", lambda: tmp_path)
    chemin = enregistrer(SessionMcp(_cassette(), "s1", "RD-007"), "eval")
    assert chemin == tmp_path / "eval" / "cassettes" / "RD-007" / "s1.json"


@pytest.mark.parametrize(
    "manifeste",
    [
        {"items": ["RD-001", "RD-007"]},
        {"items": {"RD-007": {"sha256": "0" * 64}}},
        {"fichiers": [{"chemin": "cassettes/RD-007/s0.json"}]},
        {"fichiers": [{"chemin": "eval\\cassettes\\RD-007\\s0.json"}]},
        {"dossiers": ["eval/cassettes/RD-007"]},
    ],
    ids=["chaine", "cle", "chemin-cassette", "chemin-windows", "dossier-sans-slash"],
)
@pytest.mark.parametrize("item", ["RD-007", "rd-007"], ids=["meme-casse", "autre-casse"])
def test_item_gele(tmp_path: Path, manifeste: dict[str, Any], item: str) -> None:
    _manifeste(tmp_path, manifeste)
    avant = _fichiers(tmp_path)
    with pytest.raises(ItemGele):
        enregistrer(SessionMcp(_cassette(), "s1", item), "eval", racine=tmp_path)
    assert _fichiers(tmp_path) == avant


def test_item_point_final_refuse(tmp_path: Path) -> None:
    _manifeste(tmp_path, {"items": ["RD-007"]})
    with pytest.raises(ValueError):
        verifier_item_libre("RD-007.", racine=tmp_path)
    with pytest.raises(ValueError):
        enregistrer(SessionMcp(_cassette(), "s1", "RD-007."), "eval", racine=tmp_path)
    assert _fichiers(tmp_path) == ["eval/jeu/v1.0/MANIFEST.json"]


def test_item_libre_malgre_un_voisin(tmp_path: Path) -> None:
    _manifeste(tmp_path, {"items": ["RD-0070", "RD-00"], "note": "RD-007 bis"})
    verifier_item_libre("RD-007", racine=tmp_path)
    assert enregistrer(SessionMcp(_cassette(), "s1", "RD-007"), "eval", racine=tmp_path).is_file()


def test_sans_manifeste(tmp_path: Path) -> None:
    verifier_item_libre("RD-007", racine=tmp_path)


@pytest.mark.parametrize("contenu", [b"{pas du json", b"\xff\xfe\x00"], ids=["json", "encodage"])
def test_manifeste_illisible(tmp_path: Path, contenu: bytes) -> None:
    _manifeste(tmp_path, "{}").write_bytes(contenu)
    avant = _fichiers(tmp_path)
    with pytest.raises(ManifesteInvalide):
        enregistrer(SessionMcp(_cassette(), "s1", "RD-007"), "eval", racine=tmp_path)
    assert _fichiers(tmp_path) == avant


def test_jamais_d_ecrasement(tmp_path: Path) -> None:
    session = SessionMcp(_cassette(), "s1", "RD-007")
    chemin = enregistrer(session, "eval", racine=tmp_path)
    avant = chemin.read_bytes()
    with pytest.raises(ArtefactExistant):
        enregistrer(session, "eval", racine=tmp_path)
    assert chemin.read_bytes() == avant


# --- Magasin data ----------------------------------------------------------------------------


def test_magasin_data_ne_lit_pas_eval(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _manifeste(tmp_path, {"items": ["RD-007"]})  # gelé : sans effet sur le magasin data
    lus: list[str] = []
    ouvrir = builtins.open
    lire_texte = Path.read_text

    def espion_open(fichier: Any, *args: Any, **kwargs: Any) -> Any:
        lus.append(str(fichier))
        return ouvrir(fichier, *args, **kwargs)

    def espion_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        lus.append(str(self))
        return lire_texte(self, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", espion_open)
    monkeypatch.setattr(Path, "read_text", espion_read_text)
    session = SessionMcp(_cassette(), "abc", "RD-007")
    chemin = enregistrer(session, "data", racine=tmp_path)
    monkeypatch.undo()
    assert chemin == tmp_path / "data" / "cassettes" / "abc.json"
    assert not [lu for lu in lus if "eval" in Path(lu).parts]
    assert lire_cassette(chemin) == session.cassette


def test_jamais_d_ecrasement_data(tmp_path: Path) -> None:
    enregistrer(SessionMcp(_cassette(), "abc"), "data", racine=tmp_path)
    with pytest.raises(ArtefactExistant):
        enregistrer(SessionMcp(_cassette(), "abc"), "data", racine=tmp_path)


# --- Identifiants ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("magasin", "item", "session_id"),
    [
        ("eval", "", "s1"),
        ("eval", "RD/007", "s1"),
        ("eval", "RD\\007", "s1"),
        ("eval", "..", "s1"),
        ("eval", "RD..7", "s1"),
        ("eval", "RD-007.", "s1"),
        ("eval", "RD-007\n", "s1"),
        ("eval", None, "s1"),
        ("eval", "RD-007", ""),
        ("eval", "RD-007", "a/b"),
        ("eval", "RD-007", "a\\b"),
        ("data", None, ".."),
        ("data", None, "../x"),
        ("data", None, "abc."),
        ("data", None, ""),
        ("autre", "RD-007", "s1"),
    ],
)
def test_identifiant_fautif(
    tmp_path: Path, magasin: str, item: str | None, session_id: str
) -> None:
    with pytest.raises(ValueError):
        enregistrer(SessionMcp(_cassette(), session_id, item), magasin, racine=tmp_path)
    assert _fichiers(tmp_path) == []


def test_api_unique_reexportee() -> None:
    import slmsp.mcp
    import slmsp.mcp.enregistrement

    assert slmsp.mcp.enregistrer is slmsp.mcp.enregistrement.enregistrer
    assert slmsp.mcp.SessionMcp is slmsp.mcp.enregistrement.SessionMcp


def test_session_invalide(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        enregistrer(_cassette(), "data", racine=tmp_path)  # type: ignore[arg-type]


def test_nouvel_identifiant() -> None:
    premier, second = nouvel_identifiant_session(), nouvel_identifiant_session()
    assert premier != second
    assert re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", premier)
    assert chemin_cassette("data", premier, racine=Path("r")).name == f"{premier}.json"


def test_session_figee() -> None:
    session = SessionMcp(_cassette(), "s1")
    with pytest.raises(AttributeError):
        session.session_id = "s2"  # type: ignore[misc]


# --- Sessions de panne -----------------------------------------------------------------------

APPELS = [
    ("search_datasets", {"query": "<requete-factice>"}),
    ("get_dataset_info", {"dataset_id": "<id-factice>"}),
]


def test_session_de_panne_erreur_http(tmp_path: Path) -> None:
    session = session_de_panne(APPELS, "erreur_http", statut=503, item="RD-007", session_id="s1")
    cassette = session.cassette
    assert cassette.initialize is None
    assert cassette.server == URL_SERVEUR
    assert cassette.tools_list_sha256 == charger_config().tools_list_sha256
    assert [i.request["id"] for i in cassette.interactions] == [3, 4]
    assert [i.request["params"]["name"] for i in cassette.interactions] == [
        "search_datasets",
        "get_dataset_info",
    ]
    for interaction in cassette.interactions:
        assert interaction.response is None
        assert interaction.simulation is not None
        assert (interaction.simulation.type, interaction.simulation.statut) == ("erreur_http", 503)
    chemin = enregistrer(session, "eval", racine=tmp_path)
    assert lire_cassette(chemin) == cassette
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    assert brut["initialize"] is None
    assert brut["interactions"][0]["simulation"] == {"type": "erreur_http", "statut": 503}


@pytest.mark.parametrize("type_", ["delai_depasse", "injoignable"])
def test_session_de_panne_sans_statut(type_: str) -> None:
    session = session_de_panne(APPELS[:1], type_)  # type: ignore[arg-type]
    (interaction,) = session.cassette.interactions
    assert interaction.simulation is not None and interaction.simulation.statut is None
    assert session.item is None and session.session_id


def test_session_de_panne_statut_hors_erreur_http() -> None:
    with pytest.raises(ValidationError):
        session_de_panne(APPELS, "injoignable", statut=503)


def test_session_de_panne_valide_tous_les_appels() -> None:
    with pytest.raises(AppelNonConforme):
        session_de_panne([APPELS[0], ("get_metrics", {})], "injoignable")


@pytest.mark.parametrize(("item", "session_id"), [("RD/7", "s1"), ("RD-7", "..")])
def test_session_de_panne_identifiants(item: str, session_id: str) -> None:
    with pytest.raises(ValueError):
        session_de_panne(APPELS, "injoignable", item=item, session_id=session_id)
