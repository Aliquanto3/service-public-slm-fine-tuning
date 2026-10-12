"""Fabrique de clients (critères 1 et 8 de la story 1.4) et verrou des clients MCP non gardés."""

from __future__ import annotations

import ast
import asyncio
import inspect
import sys
import textwrap
from pathlib import Path

import httpx2  # noqa: TID251 (tests de la passerelle : transports factices)
import pytest

import slmsp.net
from slmsp.core.erreurs import HoteBloque
from slmsp.core.ports import NetGate
from slmsp.net import Passerelle, client, client_local, fabrique_hf, fabrique_hf_async
from slmsp.net.config import charger_config_reseau
from slmsp.net.journal import NOM_JOURNAL, JournalMemoire

RACINE = Path(__file__).resolve().parents[2]
SRC = RACINE / "src" / "slmsp"


class _Mode:
    def __init__(self, mode: str = "connecte") -> None:
        self.mode = mode

    def mode_courant(self) -> str:
        return self.mode


def _compteur():
    appels = []

    def repondre(requete):
        appels.append(requete)
        return httpx2.Response(200, request=requete)

    return appels, httpx2.MockTransport(repondre)


# --- Critère 1 : la fabrique ----------------------------------------------------------------


def test_reexport_et_module() -> None:
    assert slmsp.net.client is client
    module = sys.modules["slmsp.net.client"]
    assert module.client is client
    assert set(slmsp.net.__all__) == {
        "Passerelle",
        "client",
        "client_local",
        "fabrique_hf",
        "fabrique_hf_async",
    }


@pytest.mark.parametrize("lib", ["httpx2", "httpx"])
@pytest.mark.parametrize("asynchrone", [False, True])
def test_types_et_trust_env(doublures, lib: str, asynchrone: bool) -> None:
    module = doublures.module_lib(lib)
    garde = client("outillage", lib, asynchrone, None, JournalMemoire())
    attendu = module.AsyncClient if asynchrone else module.Client
    assert type(garde) is attendu
    assert garde.trust_env is False
    assert garde.follow_redirects is False
    interne = garde._transport.interne
    assert interne._pool._retries == 0
    assert type(interne).__name__ == ("AsyncHTTPTransport" if asynchrone else "HTTPTransport")


def test_proxy_d_environnement_ignore(monkeypatch: pytest.MonkeyPatch) -> None:
    for nom in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "all_proxy"):
        monkeypatch.setenv(nom, "http://127.0.0.1:9")
    appels, interne = _compteur()
    garde = client("assistant", mode=_Mode(), journal=JournalMemoire(), transport_interne=interne)
    assert garde._mounts == {}
    with garde:
        assert garde.get("https://www.data.gouv.fr/x").status_code == 200
    assert len(appels) == 1
    # Sans transport injecté non plus : aucun montage de proxy, transport interne direct.
    defaut = client("assistant", mode=_Mode(), journal=JournalMemoire())
    assert defaut._mounts == {}
    assert type(defaut._transport.interne._pool).__name__ == "ConnectionPool"


def test_refus_avant_transport_par_defaut() -> None:
    """Le transport réel n'est jamais atteint par une requête refusée."""
    journal = JournalMemoire()
    with client("assistant", mode=_Mode(), journal=journal) as garde:
        with pytest.raises(HoteBloque):
            garde.get("https://evil.com/")
    assert journal.lister()[0].statut == "bloquee-liste"


def test_journal_sqlite_par_defaut(tmp_path: Path) -> None:
    import os

    _, interne = _compteur()
    with client("outillage", transport_interne=interne) as garde:
        garde.get("https://pypi.org/simple/x/")
    assert (Path(os.environ["SLMSP_VAR_DIR"]) / NOM_JOURNAL).is_file()


@pytest.mark.parametrize(
    ("args", "kwargs", "message"),
    [
        (("admin",), {}, "profil inconnu"),
        (("outillage",), {"lib": "requests"}, "bibliothèque"),
        (("assistant",), {}, "ModePort"),
        (("outillage",), {"usage": "telechargement"}, "usage"),
    ],
)
def test_arguments_invalides(args, kwargs, message) -> None:
    with pytest.raises(ValueError, match=message):
        client(*args, journal=JournalMemoire(), **kwargs)


def test_mode_qui_n_est_pas_un_port() -> None:
    with pytest.raises(TypeError):
        client("assistant", mode="connecte", journal=JournalMemoire())


# --- Critère 8 : délais ---------------------------------------------------------------------


@pytest.mark.parametrize(("usage", "delai"), [(None, 30), ("mcp", 10), ("sonde", 3)])
@pytest.mark.parametrize("asynchrone", [False, True])
def test_delais(usage, delai, asynchrone) -> None:
    garde = client(
        "assistant", asynchrone=asynchrone, mode=_Mode(), journal=JournalMemoire(), usage=usage
    )
    assert garde.timeout == httpx2.Timeout(delai)


def test_delais_configures(tmp_path: Path) -> None:
    chemin = tmp_path / "reseau.toml"
    chemin.write_text(
        textwrap.dedent(
            """
            [delais]
            mcp = 4.5
            sonde = 1
            defaut = 12

            [sonde]
            url = "https://mcp.data.gouv.fr/health"

            [profils.outillage]
            """
        ),
        encoding="utf-8",
    )
    config = charger_config_reseau(chemin)
    for usage, delai in [("mcp", 4.5), ("sonde", 1), (None, 12)]:
        garde = client(
            "assistant", mode=_Mode(), journal=JournalMemoire(), usage=usage, config=config
        )
        assert garde.timeout == httpx2.Timeout(delai)


def test_client_mcp_injectable() -> None:
    from mcp.client.streamable_http import streamable_http_client

    garde = client(
        "assistant", asynchrone=True, usage="mcp", mode=_Mode(), journal=JournalMemoire()
    )
    assert isinstance(garde, httpx2.AsyncClient)
    assert garde.timeout == httpx2.Timeout(10)
    signature = inspect.signature(streamable_http_client)
    signature.bind("https://mcp.data.gouv.fr/mcp", http_client=garde)
    assert "AsyncClient" in str(signature.parameters["http_client"].annotation)


# --- client_local -----------------------------------------------------------------------------


@pytest.mark.parametrize("asynchrone", [False, True])
def test_client_local(asynchrone: bool) -> None:
    appels, interne = _compteur()
    garde = client_local(8080, asynchrone=asynchrone, transport_interne=interne)
    assert garde.trust_env is False
    assert garde.timeout == httpx2.Timeout(600)
    refusees = [
        "http://127.0.0.1:8081/v1/x",
        "http://localhost:8080/v1/x",
        "https://example.org/",
        "https://127.0.0.1:8080/v1/x",
        "http://127.0.0.2:8080/v1/x",
        "http://[::1]:8080/v1/x",
        "http://u:p@127.0.0.1:8080/v1/x",
    ]

    async def scenario_async() -> None:
        async with garde:
            assert (await garde.post("http://127.0.0.1:8080/v1/x", json={})).status_code == 200
            for url in refusees:
                with pytest.raises(HoteBloque):
                    await garde.get(url)

    if asynchrone:
        asyncio.run(scenario_async())
    else:
        with garde:
            assert garde.post("http://127.0.0.1:8080/v1/x", json={}).status_code == 200
            for url in refusees:
                with pytest.raises(HoteBloque):
                    garde.get(url)
    assert len(appels) == 1
    assert str(appels[0].url) == "http://127.0.0.1:8080/v1/x"


def test_client_local_port_80() -> None:
    appels, interne = _compteur()
    with client_local(80, transport_interne=interne) as garde:
        garde.get("http://127.0.0.1/v1/x")
        with pytest.raises(HoteBloque):
            garde.get("http://127.0.0.1:8080/v1/x")
    assert len(appels) == 1


def test_client_local_sans_journal() -> None:
    import os

    _, interne = _compteur()
    with client_local(8080, transport_interne=interne) as garde:
        garde.get("http://127.0.0.1:8080/health")
    assert not (Path(os.environ["SLMSP_VAR_DIR"]) / NOM_JOURNAL).exists()


@pytest.mark.parametrize("port", [0, 65536, -1, True, "8080", 8080.0])
def test_client_local_port_invalide(port) -> None:
    with pytest.raises(ValueError, match="port"):
        client_local(port)


def test_client_local_lib_invalide() -> None:
    with pytest.raises(ValueError):
        client_local(8080, lib="requests")


# --- Fabriques Hugging Face ------------------------------------------------------------------


def test_fabrique_hf() -> None:
    for fabrique in (fabrique_hf, fabrique_hf_async):
        assert all(
            p.default is not inspect.Parameter.empty
            for p in inspect.signature(fabrique).parameters.values()
        )
    garde = fabrique_hf()
    assert type(garde) is httpx2.Client
    assert garde.follow_redirects is True and garde.trust_env is False
    garde_async = fabrique_hf_async()
    assert type(garde_async) is httpx2.AsyncClient
    assert garde_async.follow_redirects is True

    journal = JournalMemoire()
    appels, interne = _compteur()
    with fabrique_hf(journal=journal, transport_interne=interne) as garde:
        garde.head("https://huggingface.co/x/resolve/main/config.json")
        with pytest.raises(HoteBloque):
            garde.post("https://huggingface.co/api/repos/create", json={})
    assert len(appels) == 1
    assert [(e.profil, e.statut) for e in journal.lister()] == [
        ("outillage", "bloquee-liste"),
        ("outillage", "envoyee"),
    ]


def test_set_client_factory() -> None:
    """Extra `fetch` (absent du socle) : sauté si `huggingface_hub` n'est pas installé."""
    hub = pytest.importorskip("huggingface_hub")
    from huggingface_hub.utils import _http

    defaut = getattr(_http, "default_client_factory", None)
    hub.set_client_factory(fabrique_hf)
    try:
        session = hub.get_session()
        assert type(session) is httpx2.Client
        assert session.follow_redirects is True and session.trust_env is False
    finally:
        if defaut is not None:
            hub.set_client_factory(defaut)


# --- Passerelle (NetGate) ----------------------------------------------------------------------


def test_passerelle() -> None:
    journal = JournalMemoire()
    mode = _Mode()
    passerelle = Passerelle(mode, journal)
    assert isinstance(passerelle, NetGate)
    assert passerelle.verifier("assistant", "POST", "https://mcp.data.gouv.fr/mcp") is None
    assert journal.lister() == []

    with pytest.raises(HoteBloque, match="assistant"):
        passerelle.verifier(
            "assistant",
            "post",
            "https://evil.com/mcp",
            outil="search_datasets",
            termes={"q": "x", "a": 1},
        )
    (entree,) = journal.lister()
    assert (entree.statut, entree.hote, entree.methode, entree.outil, entree.termes) == (
        "bloquee-liste",
        "evil.com",
        "POST",
        "search_datasets",
        '{"a":1,"q":"x"}',
    )

    mode.mode = "hors-ligne-force"
    with pytest.raises(HoteBloque):
        passerelle.verifier("assistant", "GET", "https://mcp.data.gouv.fr/health")
    assert journal.lister()[0].statut == "bloquee-mode"

    appels, interne = _compteur()
    with passerelle.client("assistant", transport_interne=interne) as garde:
        with pytest.raises(HoteBloque):
            garde.get("https://www.data.gouv.fr/x")
        mode.mode = "connecte"
        garde.get("https://www.data.gouv.fr/x")
    assert len(appels) == 1
    assert [e.statut for e in journal.lister(2)] == ["envoyee", "bloquee-mode"]


def test_passerelle_arguments() -> None:
    passerelle = Passerelle(journal=JournalMemoire())
    with pytest.raises(ValueError):
        passerelle.client("assistant")
    with pytest.raises(ValueError):
        passerelle.verifier("assistant", "GET", "https://www.data.gouv.fr/")
    with pytest.raises(ValueError):
        passerelle.verifier("admin", "GET", "https://www.data.gouv.fr/")
    with pytest.raises(ValueError):
        Passerelle(journal=JournalMemoire(), lib="requests")
    with pytest.raises(HoteBloque):
        passerelle.verifier("aucun", "GET", "https://www.data.gouv.fr/")


@pytest.mark.parametrize("termes", [{"x": float("nan")}, {1, 2}, object()])
def test_passerelle_termes_non_serialisables(termes) -> None:
    journal = JournalMemoire()
    passerelle = Passerelle(_Mode(), journal)
    with pytest.raises(HoteBloque):
        passerelle.verifier("assistant", "POST", "https://evil.com/mcp", outil="t", termes=termes)
    (entree,) = journal.lister()
    assert (entree.statut, entree.outil, entree.termes) == ("bloquee-liste", "t", None)


class _ModeQuiLeve:
    def mode_courant(self) -> str:
        raise RuntimeError("sonde en panne")


@pytest.mark.parametrize("source", ["inconnu", "leve"])
def test_passerelle_mode_illisible(source: str) -> None:
    journal = JournalMemoire()
    mode = _ModeQuiLeve() if source == "leve" else _Mode(source)
    passerelle = Passerelle(mode, journal)
    with pytest.raises(HoteBloque, match="Mode inconnu ou illisible") as info:
        passerelle.verifier("assistant", "GET", "https://mcp.data.gouv.fr/health")
    if source == "leve":
        assert isinstance(info.value.__cause__, RuntimeError)
    (entree,) = journal.lister()
    assert (entree.statut, entree.mode) == ("bloquee-mode", None)


# --- Verrou : aucun client MCP créé hors passerelle ---------------------------------------------

INTERDITS = {"create_mcp_http_client", "ClientSessionGroup"}
MODULES_INTERDITS = ("mcp.client.sse",)
MODULES_CLIENT = {"mcp", "mcp.client", "mcp.client.client"}


def _module_interdit(nom: str) -> bool:
    return any(nom == m or nom.startswith(m + ".") for m in MODULES_INTERDITS)


def _url_litterale(noeud: ast.expr) -> bool:
    return (isinstance(noeud, ast.Constant) and isinstance(noeud.value, str)) or isinstance(
        noeud, ast.JoinedStr
    )


def _racine(noeud: ast.expr) -> str | None:
    while isinstance(noeud, ast.Attribute):
        noeud = noeud.value
    return noeud.id if isinstance(noeud, ast.Name) else None


def verrou_mcp(arbre: ast.Module) -> list[str]:
    """Constats du verrou sur un module : (ligne, motif) en texte."""
    constats: list[str] = []
    alias_client: set[str] = set()
    alias_mcp: set[str] = set()
    alias_streamable = {"streamable_http_client"}
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            for alias in noeud.names:
                if _module_interdit(alias.name):
                    constats.append(f"{noeud.lineno}: import de {alias.name}")
                if alias.name == "mcp" or alias.name.startswith("mcp."):
                    alias_mcp.add(alias.asname or "mcp")
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            for alias in noeud.names:
                complet = f"{noeud.module}.{alias.name}"
                if _module_interdit(noeud.module) or _module_interdit(complet):
                    constats.append(f"{noeud.lineno}: import de {complet}")
                if alias.name in INTERDITS:
                    constats.append(f"{noeud.lineno}: import de {alias.name}")
                if noeud.module in MODULES_CLIENT and alias.name == "Client":
                    alias_client.add(alias.asname or "Client")
                if noeud.module in ("mcp", "mcp.client") and alias.name == "client":
                    alias_mcp.add(alias.asname or "client")
                if (
                    noeud.module == "mcp" or noeud.module.startswith("mcp.")
                ) and alias.name == "streamable_http_client":
                    alias_streamable.add(alias.asname or alias.name)
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Name) and noeud.id in INTERDITS:
            constats.append(f"{noeud.lineno}: référence à {noeud.id}")
        elif isinstance(noeud, ast.Attribute) and noeud.attr in INTERDITS:
            constats.append(f"{noeud.lineno}: référence à {noeud.attr}")
        elif isinstance(noeud, ast.Attribute) and noeud.attr == "sse":
            if _racine(noeud) in alias_mcp:
                constats.append(f"{noeud.lineno}: référence à mcp.client.sse")
        if not isinstance(noeud, ast.Call):
            continue
        fonction = noeud.func
        est_streamable = (isinstance(fonction, ast.Name) and fonction.id in alias_streamable) or (
            isinstance(fonction, ast.Attribute) and fonction.attr == "streamable_http_client"
        )
        if est_streamable:
            client_http = [k for k in noeud.keywords if k.arg == "http_client"]
            if not client_http or (
                isinstance(client_http[0].value, ast.Constant)
                and client_http[0].value.value is None
            ):
                constats.append(f"{noeud.lineno}: streamable_http_client sans http_client=")
        est_client_mcp = (isinstance(fonction, ast.Name) and fonction.id in alias_client) or (
            isinstance(fonction, ast.Attribute)
            and fonction.attr == "Client"
            and _racine(fonction) in alias_mcp
        )
        if est_client_mcp:
            serveur = noeud.args[:1] + [k.value for k in noeud.keywords if k.arg == "server"]
            if any(_url_litterale(valeur) for valeur in serveur):
                constats.append(f"{noeud.lineno}: Client MCP construit sur une URL littérale")
    return constats


def test_verrou_mcp_code_source() -> None:
    constats = []
    for chemin in sorted(SRC.rglob("*.py")):
        arbre = ast.parse(chemin.read_text(encoding="utf-8-sig"), filename=str(chemin))
        constats += [f"{chemin.relative_to(RACINE)}:{c}" for c in verrou_mcp(arbre)]
    assert not constats, "\n".join(constats)


PROPRE = """
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client

    from slmsp.net import client


    async def ouvrir(url, mode):
        http = client("assistant", asynchrone=True, usage="mcp", mode=mode)
        async with streamable_http_client(url, http_client=http) as flux:
            return Client(flux)
    """

FAUTIFS = {
    "create-mcp-http-client": "from mcp.shared._httpx_utils import create_mcp_http_client\n",
    "create-attribut": "import mcp.shared._httpx_utils as u\nu.create_mcp_http_client()\n",
    "session-group": "from mcp import ClientSessionGroup\n",
    "session-group-attribut": "import mcp\nmcp.ClientSessionGroup()\n",
    "sse-module": "import mcp.client.sse\n",
    "sse-from": "from mcp.client.sse import sse_client\n",
    "sse-from-paquet": "from mcp.client import sse\n",
    "streamable-sans-client": (
        "from mcp.client.streamable_http import streamable_http_client\n"
        "streamable_http_client('https://mcp.data.gouv.fr/mcp')\n"
    ),
    "streamable-client-none": (
        "from mcp.client import streamable_http as s\n"
        "s.streamable_http_client(url, http_client=None)\n"
    ),
    "client-url": "from mcp import Client\nClient('https://mcp.data.gouv.fr/mcp')\n",
    "client-url-fstring": "from mcp.client.client import Client as C\nC(f'https://{h}/mcp')\n",
    "client-url-mot-cle": "from mcp.client import Client\nClient(server='https://x/mcp')\n",
    "client-attribut": "import mcp\nmcp.Client('https://mcp.data.gouv.fr/mcp')\n",
    "streamable-alias": (
        "from mcp.client.streamable_http import streamable_http_client as s\n"
        "s('https://mcp.data.gouv.fr/mcp')\n"
    ),
    "client-module-alias": (
        "from mcp.client import client as c\nc.Client('https://mcp.data.gouv.fr/mcp')\n"
    ),
}


def test_verrou_auto_test_propre() -> None:
    assert verrou_mcp(ast.parse(textwrap.dedent(PROPRE))) == []


@pytest.mark.parametrize("source", FAUTIFS.values(), ids=FAUTIFS.keys())
def test_verrou_auto_test_fautif(source: str) -> None:
    assert verrou_mcp(ast.parse(source)), source


def test_verrou_client_dynamique_tolere() -> None:
    """`Client(variable)` relève de la story 3.3 : le verrou ne le signale pas."""
    assert verrou_mcp(ast.parse("from mcp import Client\nClient(serveur)\n")) == []
