"""Journal des Requêtes sortantes (critère 4 de la story 1.4)."""

from __future__ import annotations

import asyncio
import os
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import httpx2  # noqa: TID251 (tests de la passerelle : transports factices)
import pytest
from pydantic import ValidationError

from slmsp.core.erreurs import HoteBloque, SlmspError
from slmsp.core.ports import JournalRequetes
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes
from slmsp.net import client
from slmsp.net.journal import (
    COLONNES,
    NOM_JOURNAL,
    JournalMemoire,
    JournalSqlite,
    extraire_appel_outil,
)

APPEL = {
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {"name": "search_datasets", "arguments": {"q": "x"}},
}
SECRET = "secret-factice-0123456789"


def _entree(**valeurs) -> EntreeJournalRequetes:
    base = {
        "horodatage": datetime(2026, 10, 12, 8, 0, tzinfo=UTC),
        "profil": "assistant",
        "hote": "mcp.data.gouv.fr",
        "methode": "POST",
        "outil": None,
        "termes": None,
        "statut": "envoyee",
        "mode": "connecte",
    }
    return EntreeJournalRequetes(**(base | valeurs))


def test_schema_entree_fige() -> None:
    assert set(EntreeJournalRequetes.model_fields) == {"schema_version", *COLONNES}
    entree = _entree()
    with pytest.raises(ValidationError):
        entree.statut = "echouee"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        _entree(url="https://x")
    with pytest.raises(ValidationError):
        _entree(horodatage=datetime(2026, 10, 12, 8, 0))  # sans fuseau
    with pytest.raises(ValidationError):
        _entree(statut="partie")
    with pytest.raises(ValidationError):
        _entree(profil="admin")


def test_colonnes_exactes(tmp_path: Path) -> None:
    journal = JournalSqlite(tmp_path / "j.sqlite")
    with closing(sqlite3.connect(journal.chemin)) as connexion:
        colonnes = [ligne[1] for ligne in connexion.execute("PRAGMA table_info(requetes)")]
        (version,) = connexion.execute("PRAGMA user_version").fetchone()
        (mode,) = connexion.execute("PRAGMA journal_mode").fetchone()
    assert colonnes == list(COLONNES)
    assert len(colonnes) == 8
    assert version == 1
    assert mode == "wal"


def test_fichier_par_defaut_dans_var_dir() -> None:
    journal = JournalSqlite()
    attendu = Path(os.environ["SLMSP_VAR_DIR"]).resolve() / NOM_JOURNAL
    assert journal.chemin == attendu
    assert attendu.is_file()


def test_aller_retour_et_ordre(tmp_path: Path) -> None:
    journal = JournalSqlite(tmp_path / "j.sqlite")
    entrees = [
        _entree(),
        _entree(statut="bloquee-liste", hote="evil.com", methode="GET"),
        _entree(outil="search_datasets", termes='{"q":"x"}'),
        _entree(profil="outillage", mode=None, statut="echouee"),
    ]
    for entree in entrees:
        journal.inscrire(entree)
    assert journal.lister() == list(reversed(entrees))
    assert journal.lister(limite=2) == entrees[:1:-1]
    assert journal.lister(limite=0) == []
    # Rouvrir la base ne la réinitialise pas.
    assert JournalSqlite(tmp_path / "j.sqlite").lister(limite=1) == [entrees[-1]]


def test_version_inattendue(tmp_path: Path) -> None:
    chemin = tmp_path / "j.sqlite"
    with closing(sqlite3.connect(chemin)) as connexion:
        connexion.execute("PRAGMA user_version = 9")
    with pytest.raises(SlmspError, match="version"):
        JournalSqlite(chemin)


def test_doublure_memoire() -> None:
    journal = JournalMemoire()
    premiere, seconde = _entree(), _entree(statut="echouee")
    journal.inscrire(premiere)
    journal.inscrire(seconde)
    assert journal.lister() == [seconde, premiere]
    assert journal.lister(1) == [seconde]


def test_limite_negative(tmp_path: Path) -> None:
    for journal in (JournalMemoire(), JournalSqlite(tmp_path / "j.sqlite")):
        journal.inscrire(_entree())
        with pytest.raises(ValueError, match="limite"):
            journal.lister(-1)


def test_implementations_du_port(tmp_path: Path) -> None:
    assert isinstance(JournalMemoire(), JournalRequetes)
    assert isinstance(JournalSqlite(tmp_path / "j.sqlite"), JournalRequetes)


# --- Extraction de l'appel d'outil -------------------------------------------------------------


@pytest.mark.parametrize(
    ("corps", "attendu"),
    [
        (APPEL, ("search_datasets", '{"q":"x"}')),
        (
            {"method": "tools/call", "params": {"name": "t", "arguments": {"b": 1, "a": "é"}}},
            ("t", '{"a":"é","b":1}'),
        ),
        ({"method": "tools/call", "params": {"name": "t"}}, ("t", None)),
        ({"method": "tools/list", "params": {}}, (None, None)),
        ({"method": "tools/call", "params": {"arguments": {}}}, (None, None)),
        ({"method": "tools/call", "params": "x"}, (None, None)),
        ([APPEL], (None, None)),
    ],
)
def test_extraire_appel_outil(corps, attendu) -> None:
    import json

    assert extraire_appel_outil(json.dumps(corps, ensure_ascii=False).encode()) == attendu


@pytest.mark.parametrize("contenu", [b"", b"{", b"\xff\xfe", b'"texte"', b"null"])
def test_extraire_corps_illisible(contenu: bytes) -> None:
    assert extraire_appel_outil(contenu) == (None, None)


# --- Journal tenu par le client -----------------------------------------------------------------


class _Mode:
    def mode_courant(self) -> str:
        return "connecte"


@pytest.mark.parametrize("asynchrone", [False, True])
def test_client_journal_sqlite_sans_secret(asynchrone: bool) -> None:
    """Journal SQLite par défaut : `outil` et `termes` extraits ; ni en-tête, ni corps, ni
    chaîne de requête dans la base."""
    garde = client(
        "assistant",
        asynchrone=asynchrone,
        mode=_Mode(),
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(200, json={"ok": 1})),
    )
    options = {
        "json": APPEL,
        "headers": {"Authorization": f"Bearer {SECRET}", "X-Cle": SECRET},
        "params": {"jeton": SECRET},
    }
    url = "https://mcp.data.gouv.fr/mcp"
    if asynchrone:

        async def envoyer() -> None:
            async with garde:
                await garde.post(url, **options)
                with pytest.raises(HoteBloque):
                    await garde.post("https://evil.com/mcp", **options)

        asyncio.run(envoyer())
    else:
        with garde:
            garde.post(url, **options)
            with pytest.raises(HoteBloque):
                garde.post("https://evil.com/mcp", **options)

    journal = JournalSqlite()
    bloquee, envoyee = journal.lister()
    assert (envoyee.statut, envoyee.outil, envoyee.termes) == (
        "envoyee",
        "search_datasets",
        '{"q":"x"}',
    )
    assert (envoyee.hote, envoyee.methode, envoyee.mode) == ("mcp.data.gouv.fr", "POST", "connecte")
    assert (bloquee.statut, bloquee.hote, bloquee.outil) == (
        "bloquee-liste",
        "evil.com",
        "search_datasets",
    )

    with closing(sqlite3.connect(journal.chemin)) as connexion:
        dump = "\n".join(connexion.iterdump())
    for interdit in (SECRET, "Authorization", "Bearer", "jeton", "jsonrpc", "/mcp", "https://"):
        assert interdit not in dump
    for fichier in journal.chemin.parent.glob(NOM_JOURNAL + "*"):
        brut = fichier.read_bytes()
        assert SECRET.encode() not in brut and b"jsonrpc" not in brut


@pytest.mark.parametrize("asynchrone", [False, True])
def test_echec_reseau(asynchrone: bool) -> None:
    erreur = httpx2.ConnectError("refusée")
    appels = []

    def lever(requete):
        appels.append(requete)
        raise erreur

    journal = JournalMemoire()
    garde = client(
        "assistant",
        asynchrone=asynchrone,
        mode=_Mode(),
        journal=journal,
        transport_interne=httpx2.MockTransport(lever),
    )
    with pytest.raises(httpx2.ConnectError) as info:
        if asynchrone:

            async def envoyer() -> None:
                async with garde:
                    await garde.get("https://www.data.gouv.fr/x")

            asyncio.run(envoyer())
        else:
            with garde:
                garde.get("https://www.data.gouv.fr/x")
    assert info.value is erreur
    assert len(appels) == 1
    (entree,) = journal.lister()
    assert (entree.statut, entree.hote, entree.outil, entree.termes) == (
        "echouee",
        "www.data.gouv.fr",
        None,
        None,
    )


def test_corps_en_flux_sans_termes() -> None:
    """Un corps en flux (non lu) ne donne ni `outil` ni `termes`, et n'est pas consommé."""
    journal = JournalMemoire()
    garde = client(
        "assistant",
        mode=_Mode(),
        journal=journal,
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(200)),
    )

    def flux():
        yield b'{"method":"tools/call","params":{"name":"t","arguments":{}}}'

    with garde:
        garde.post("https://mcp.data.gouv.fr/mcp", content=flux())
    (entree,) = journal.lister()
    assert (entree.statut, entree.outil, entree.termes) == ("envoyee", None, None)
