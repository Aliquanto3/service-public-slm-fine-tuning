"""Client MCP en direct `McpEnDirect` et sonde de santé (story 3.3, AD-10, AD-4).

Le serveur est un serveur MCP factice en processus (`serveur_mcp_factice.py`), branché
comme transport interne du client de la passerelle : aucun réseau.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest

from slmsp.core.erreurs import AppelNonConforme, HoteBloque, SchemaOutilModifie
from slmsp.core.ports import ToolPort
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.direct import URL_SERVEUR, McpEnDirect, ResultatSante, sonder_sante
from slmsp.mcp.enregistrement import enregistrer
from slmsp.mcp.erreurs import DelaiDepasse, ErreurHttp, Injoignable
from slmsp.mcp.outils import charger_config, charger_outils
from slmsp.net.config import ConfigReseau, Delais, charger_config_reseau
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
POST_PREMIER_APPEL = 4
"""POST n° 1 `initialize`, 2 `notifications/initialized`, 3 `tools/list`, 4 `tools/call`."""


class _Mode:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    def mode_courant(self) -> str:
        return self.mode


def _config(mcp: float = 10, sonde: float = 3) -> ConfigReseau:
    config = charger_config_reseau()
    return config.model_copy(update={"delais": Delais(mcp=mcp, sonde=sonde)})


def _client(
    serveur: Any,
    journal: JournalMemoire | None = None,
    *,
    profil: str = "outillage",
    interne: Any = None,
    **kwargs: Any,
) -> McpEnDirect:
    return McpEnDirect(
        profil,
        journal=JournalMemoire() if journal is None else journal,
        transport_interne=serveur.transport() if serveur is not None else interne,
        **kwargs,
    )


class _Panne(httpx2.AsyncBaseTransport):
    """Transport qui lève `erreur` sur le n-ième POST et délègue le reste au serveur factice."""

    def __init__(self, serveur: Any, erreur: type[Exception], n: int = 1) -> None:
        self.interne = serveur.transport() if serveur is not None else None
        self.erreur = erreur
        self.n = n
        self.posts = 0
        self.requetes: list[str] = []

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        self.requetes.append(request.method)
        if request.method == "POST":
            self.posts += 1
            if self.posts == self.n:
                raise self.erreur("<panne-factice>", request=request)
        assert self.interne is not None
        return await self.interne.handle_async_request(request)


# --- Connexion -------------------------------------------------------------------------------


def test_connexion_initialize_puis_tools_list() -> None:
    serveur = factice.ServeurMcpFactice()
    journal = JournalMemoire()
    with _client(serveur, journal) as mcp:
        assert isinstance(mcp, ToolPort)
        assert mcp.lister_outils() == charger_outils()
    assert serveur.methodes == ["initialize", "notifications/initialized", "tools/list"]
    entrees = journal.lister()
    assert entrees and {(e.statut, e.methode, e.hote) for e in entrees} == {
        ("envoyee", "POST", "mcp.data.gouv.fr")
    }
    assert "DELETE" not in [methode for methode, _ in serveur.requetes]


def test_url_serveur() -> None:
    assert URL_SERVEUR == "https://mcp.data.gouv.fr/mcp"


@pytest.mark.parametrize(
    "reglage",
    [{"outils_retires": ["get_dataset_info"]}, {"schemas_modifies": ["search_datasets"]}],
    ids=["outil-retire", "schema-modifie"],
)
def test_schema_derive(reglage: dict[str, Any]) -> None:
    serveur = factice.ServeurMcpFactice(**reglage)
    mcp = _client(serveur)
    with pytest.raises(SchemaOutilModifie) as info:
        with mcp:
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert info.value.ecarts  # type: ignore[attr-defined]
    assert "tools/call" not in serveur.methodes
    with pytest.raises(RuntimeError):
        mcp.session()  # session refusée : rien d'enregistrable


def test_tools_list_pagine() -> None:
    serveur = factice.ServeurMcpFactice(taille_page=3)
    with _client(serveur) as mcp:
        assert "result" in mcp.appeler("search_datasets", {"query": "x"})
    assert len(serveur.outils) == 10
    assert serveur.curseurs == [None, "3", "6", "9"]


def test_session_avec_identifiant_jamais_de_delete() -> None:
    serveur = factice.ServeurMcpFactice(avec_session=True)
    journal = JournalMemoire()
    with _client(serveur, journal) as mcp:
        assert "result" in mcp.appeler("search_datasets", {"query": "x"})
    assert serveur.sessions  # le serveur a bien ouvert une session
    assert "DELETE" not in [methode for methode, _ in serveur.requetes]
    assert "DELETE" not in [e.methode for e in journal.lister()]


def test_double_entree() -> None:
    mcp = _client(factice.ServeurMcpFactice())
    with mcp:
        with pytest.raises(RuntimeError, match="déjà ouverte"):
            mcp.__enter__()
        assert "result" in mcp.appeler("search_datasets", {"query": "x"})


def test_erreur_jsonrpc_a_l_initialize() -> None:
    serveur = factice.ServeurMcpFactice(erreur_initialize=True)
    with pytest.raises(Injoignable):
        with _client(serveur):
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert serveur.methodes == ["initialize"]


def test_tools_list_lent() -> None:
    serveur = factice.ServeurMcpFactice(lent_liste=5)
    with pytest.raises(DelaiDepasse):
        with _client(serveur, config=_config(mcp=0.3)):
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert "tools/call" not in serveur.methodes


def test_outil_inconnu_du_serveur_ignore() -> None:
    serveur = factice.ServeurMcpFactice()
    assert "get_metrics" in [o.name for o in serveur.outils]
    with _client(serveur) as mcp:
        assert mcp.appeler("search_datasets", {"query": "x"})["result"]["isError"] is False


# --- Appels ----------------------------------------------------------------------------------


def test_appel_reponse_jsonrpc_et_retenue() -> None:
    serveur = factice.ServeurMcpFactice()
    with _client(serveur) as mcp:
        premiere = mcp.appeler("search_datasets", {"query": "x"})
        seconde = mcp.appeler("get_dataset_info", {"dataset_id": "<id-factice>"})
        session = mcp.session(item="RD-007", session_id="s1")
    texte = factice.texte_factice("search_datasets")
    assert premiere == {
        "jsonrpc": "2.0",
        "id": 3,
        "result": {
            "content": [{"type": "text", "text": texte}],
            "structuredContent": {"result": texte},
            "isError": False,
        },
    }
    assert seconde["id"] == 4
    assert serveur.appels == [
        ("search_datasets", {"query": "x"}),
        ("get_dataset_info", {"dataset_id": "<id-factice>"}),
    ]
    cassette = session.cassette
    assert (session.item, session.session_id) == ("RD-007", "s1")
    assert cassette.server == URL_SERVEUR
    assert cassette.tools_list_sha256 == charger_config().tools_list_sha256
    assert cassette.initialize is not None and cassette.initialize["id"] == 1
    assert cassette.initialize["result"]["serverInfo"]["name"] == "serveur-mcp-factice"
    assert [i.request["method"] for i in cassette.interactions] == ["tools/call", "tools/call"]
    assert cassette.interactions[0].request == {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "search_datasets", "arguments": {"query": "x"}},
    }
    assert cassette.interactions[0].response == premiere
    assert cassette.interactions[1].response == seconde


def test_reponse_renvoyee_est_une_copie() -> None:
    with _client(factice.ServeurMcpFactice()) as mcp:
        reponse = mcp.appeler("search_datasets", {"query": "x"})
        reponse["result"]["content"].clear()
        session = mcp.session(session_id="s1")
    assert session.cassette.interactions[0].response["result"]["content"]  # type: ignore[index]


@pytest.mark.parametrize(
    ("nom", "arguments"),
    [("get_metrics", {}), ("search_datasets", {"query": 3}), ("search_datasets", {})],
    ids=["outil-non-expose", "type-faux", "requis-absent"],
)
def test_appel_non_conforme_jamais_envoye(nom: str, arguments: dict[str, Any]) -> None:
    serveur = factice.ServeurMcpFactice()
    with _client(serveur) as mcp:
        avant = list(serveur.requetes)
        with pytest.raises(AppelNonConforme):
            mcp.appeler(nom, arguments)
        assert serveur.requetes == avant
        session = mcp.session(session_id="s1")
    assert session.cassette.interactions == []


def test_erreur_jsonrpc_renvoyee_et_retenue() -> None:
    serveur = factice.ServeurMcpFactice(erreur_jsonrpc=True)
    with _client(serveur) as mcp:
        reponse = mcp.appeler("search_datasets", {"query": "x"})
        session = mcp.session(session_id="s1")
    assert reponse == {
        "jsonrpc": "2.0",
        "id": 3,
        "error": {"code": factice.CODE_ERREUR_FACTICE, "message": factice.MESSAGE_ERREUR_FACTICE},
    }
    assert session.cassette.interactions[0].response == reponse


# --- Pannes ----------------------------------------------------------------------------------


def test_delai_depasse() -> None:
    serveur = factice.ServeurMcpFactice(lent=5)
    with _client(serveur, config=_config(mcp=0.3)) as mcp:
        with pytest.raises(DelaiDepasse):
            mcp.appeler("search_datasets", {"query": "x"})
        session = mcp.session(session_id="s1")
    assert session.cassette.interactions == []


def test_erreur_http_sur_tools_call() -> None:
    serveur = factice.ServeurMcpFactice(statut_post=(POST_PREMIER_APPEL, 503))
    with _client(serveur) as mcp:
        with pytest.raises(ErreurHttp) as info:
            mcp.appeler("search_datasets", {"query": "x"})
        assert info.value.statut == 503
        # La session reste utilisable : l'appel suivant passe.
        assert "result" in mcp.appeler("search_datasets", {"query": "y"})
        session = mcp.session(session_id="s1")
    assert [i.request["params"]["arguments"] for i in session.cassette.interactions] == [
        {"query": "y"}
    ]


def test_erreur_http_a_l_ouverture() -> None:
    serveur = factice.ServeurMcpFactice(statut_post=(1, 502))
    with pytest.raises(ErreurHttp) as info:
        with _client(serveur):
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert info.value.statut == 502


@pytest.mark.parametrize(
    ("erreur", "attendue"),
    [(httpx2.ConnectError, Injoignable), (httpx2.ReadTimeout, DelaiDepasse)],
    ids=["connexion", "delai-httpx"],
)
def test_panne_de_transport_a_l_ouverture(erreur: type[Exception], attendue: type) -> None:
    panne = _Panne(None, erreur, n=1)
    with pytest.raises(attendue):
        with _client(None, interne=panne):
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert panne.requetes == ["POST"]


def test_injoignable_pendant_un_appel_puis_session_fermee() -> None:
    serveur = factice.ServeurMcpFactice()
    panne = _Panne(serveur, httpx2.ConnectError, n=POST_PREMIER_APPEL)
    with _client(None, interne=panne) as mcp:
        with pytest.raises(Injoignable):
            mcp.appeler("search_datasets", {"query": "x"})
        with pytest.raises(Injoignable, match="fermée"):
            mcp.appeler("search_datasets", {"query": "y"})
    assert serveur.appels == []


def test_hote_refuse_hors_ligne_force() -> None:
    serveur = factice.ServeurMcpFactice()
    journal = JournalMemoire()
    with pytest.raises(HoteBloque):
        with _client(serveur, journal, profil="assistant", mode=_Mode("hors-ligne-force")):
            pytest.fail("le contexte ne doit pas s'ouvrir")
    assert serveur.requetes == []
    assert [e.statut for e in journal.lister()] == ["bloquee-mode"]


def test_assistant_connecte() -> None:
    serveur = factice.ServeurMcpFactice()
    with _client(serveur, profil="assistant", mode=_Mode("connecte")) as mcp:
        assert "result" in mcp.appeler("search_datasets", {"query": "x"})


def test_hors_contexte() -> None:
    mcp = _client(factice.ServeurMcpFactice())
    with pytest.raises(RuntimeError):
        mcp.appeler("search_datasets", {"query": "x"})
    with pytest.raises(RuntimeError):
        mcp.session()


def test_reouverture_nouvelle_session() -> None:
    serveur = factice.ServeurMcpFactice()
    mcp = _client(serveur)
    with mcp:
        mcp.appeler("search_datasets", {"query": "x"})
    with mcp:
        assert mcp.session(session_id="s2").cassette.interactions == []
        mcp.appeler("search_datasets", {"query": "y"})
    assert len(mcp.session(session_id="s3").cassette.interactions) == 1
    assert serveur.methodes.count("initialize") == 2


def test_session_enregistree_relue(tmp_path: Path) -> None:
    with _client(factice.ServeurMcpFactice()) as mcp:
        mcp.appeler("search_datasets", {"query": "x"})
        session = mcp.session(item="RD-007", session_id="s1")
    chemin = enregistrer(session, "eval", racine=tmp_path)
    assert chemin == tmp_path / "eval" / "cassettes" / "RD-007" / "s1.json"
    assert lire_cassette(chemin) == session.cassette


# --- Sonde de santé --------------------------------------------------------------------------


def _sonde(statut: int | None, erreur: type[Exception] | None = None):
    vues: list[httpx2.Request] = []

    def repondre(requete: httpx2.Request) -> httpx2.Response:
        vues.append(requete)
        if erreur is not None:
            raise erreur("<panne-factice>", request=requete)
        return httpx2.Response(statut or 200, request=requete)

    return vues, httpx2.MockTransport(repondre)


def test_sonde_joignable() -> None:
    vues, transport = _sonde(200)
    journal = JournalMemoire()
    resultat = sonder_sante(journal=journal, transport_interne=transport)
    assert resultat == ResultatSante("https://mcp.data.gouv.fr/health", True, 200, "HTTP 200")
    (requete,) = vues
    assert (requete.method, str(requete.url)) == ("GET", "https://mcp.data.gouv.fr/health")
    assert requete.extensions["timeout"]["read"] == charger_config_reseau().delais.sonde == 3
    assert [e.statut for e in journal.lister()] == ["envoyee"]


@pytest.mark.parametrize(
    ("statut", "erreur", "detail"),
    [
        (503, None, "HTTP 503"),
        (None, httpx2.ConnectError, "injoignable"),
        (None, httpx2.ConnectTimeout, "délai"),
    ],
    ids=["503", "connexion", "delai"],
)
def test_sonde_en_panne(statut: int | None, erreur: type[Exception] | None, detail: str) -> None:
    _, transport = _sonde(statut, erreur)
    resultat = sonder_sante(journal=JournalMemoire(), transport_interne=transport)
    assert not resultat.joignable
    assert resultat.statut == statut
    assert detail in resultat.detail


def test_sonde_refusee() -> None:
    vues, transport = _sonde(200)
    resultat = sonder_sante(
        "assistant",
        mode=_Mode("hors-ligne-force"),
        journal=JournalMemoire(),
        transport_interne=transport,
    )
    assert not resultat.joignable and "refusée" in resultat.detail
    assert vues == []
