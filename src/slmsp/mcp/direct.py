"""Adaptateur direct de `ToolPort` : client MCP en direct vers data.gouv (AD-10, AD-4).

`McpEnDirect` est une façade synchrone. La session asynchrone du SDK `mcp` (Streamable
HTTP seulement) vit dans une tâche unique d'un portail anyio (un fil, une boucle), ouvert
par `__enter__` et fermé par `__exit__`. Le client HTTP est toujours celui de la
passerelle (`slmsp.net.client(..., lib="httpx2", asynchrone=True, usage="mcp")`), injecté
par `http_client=` ; la session ne se termine pas par `DELETE` (`terminate_on_close=False`,
refusé par le profil `outillage`).

Une session commence par `initialize` puis `tools/list`, comparé au schéma figé
(`SchemaOutilModifie` à l'entrée du contexte). Chaque appel est validé avant envoi
(`AppelNonConforme`, rien n'est envoyé) ; sa réponse JSON-RPC est renvoyée et retenue pour
la cassette (`session()`), erreurs JSON-RPC comprises. Les pannes de transport lèvent
`DelaiDepasse`, `ErreurHttp` ou `Injoignable` (`slmsp.mcp.erreurs`), comme en rejeu.
"""

from __future__ import annotations

import copy
from collections.abc import Awaitable, Callable, Iterator, Mapping
from concurrent.futures import Future
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import anyio
import anyio.abc
from anyio.from_thread import start_blocking_portal
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import MCPError
from mcp.types import (
    CONNECTION_CLOSED,
    REQUEST_TIMEOUT,
    CallToolRequest,
    CallToolRequestParams,
    CallToolResult,
    PaginatedRequestParams,
)

from slmsp.core.erreurs import HoteBloque, SlmspError
from slmsp.core.ports import JournalRequetes, ModePort
from slmsp.core.schemas.cassette import Cassette, Interaction
from slmsp.mcp.enregistrement import (
    PREMIER_ID_APPEL,
    URL_SERVEUR,
    SessionMcp,
    nouvel_identifiant_session,
    requete_appel,
)
from slmsp.mcp.erreurs import DelaiDepasse, ErreurHttp, ErreurTransportMcp, Injoignable
from slmsp.mcp.outils import (
    charger_config,
    charger_outils,
    comparer_schema_serveur,
    valider_appel,
)
from slmsp.net import client
from slmsp.net.config import ConfigListeBlanche, ConfigReseau, charger_config_reseau

__all__ = ["URL_SERVEUR", "McpEnDirect", "ResultatSante", "sonder_sante"]

_PAGES_MAX: Final = 20
"""Garde-fou de pagination du `tools/list`."""


# --- Classement des exceptions (sans importer httpx) -------------------------------------


def _classes_httpx(exc: BaseException) -> list[str]:
    """Noms des classes du MRO de `exc` définies dans un module `httpx*`."""
    return [
        classe.__name__
        for classe in type(exc).__mro__
        if (classe.__module__ or "").split(".")[0].startswith("httpx")
    ]


def _feuilles(exc: BaseException) -> Iterator[BaseException]:
    if isinstance(exc, BaseExceptionGroup):
        for sous in exc.exceptions:
            yield from _feuilles(sous)
    else:
        yield exc


def _erreur_httpx(exc: BaseException) -> ErreurTransportMcp | None:
    noms = _classes_httpx(exc)
    if not noms:
        return None
    if any("Timeout" in nom for nom in noms):
        return DelaiDepasse(f"serveur MCP : délai dépassé ({noms[0]})")
    return Injoignable(f"serveur MCP injoignable ({noms[0]})")


# --- Commandes exécutées dans la boucle du portail -----------------------------------------


@dataclass
class _Commande:
    fonction: Callable[[ClientSession], Awaitable[Any]]
    futur: Future[Any]


class McpEnDirect:
    """Client MCP en direct (adaptateur de `ToolPort`), à utiliser dans un bloc `with`.

    `profil` vaut `assistant` (Liste blanche, `mode` exigé, journal des Requêtes sortantes)
    ou `outillage` (enregistrement de cassettes). `journal`, `transport_interne`, `config`
    et `liste_blanche` sont transmis à la passerelle (`slmsp.net.client`) ; le délai des
    appels est `config.delais.mcp`. `chemin_outils` remplace `config/outils-mcp.toml`.
    """

    def __init__(
        self,
        profil: str = "assistant",
        *,
        mode: ModePort | None = None,
        journal: JournalRequetes | None = None,
        transport_interne: Any = None,
        config: ConfigReseau | None = None,
        liste_blanche: ConfigListeBlanche | None = None,
        url: str = URL_SERVEUR,
        chemin_outils: str | Path | None = None,
    ) -> None:
        self.profil = profil
        self.mode = mode
        self.journal = journal
        self.transport_interne = transport_interne
        self.config = charger_config_reseau() if config is None else config
        self.liste_blanche = liste_blanche
        self.url = url
        self.chemin_outils = chemin_outils
        self._pile: ExitStack | None = None
        self._portail: Any = None
        self._envoi: anyio.abc.ObjectSendStream[_Commande] | None = None
        self._tache: Future[None] | None = None
        self._fermee: BaseException | None = None
        self._statuts: list[int] = []
        self._initialize: dict[str, Any] | None = None
        self._debut: datetime | None = None
        self._interactions: list[Interaction] = []

    # --- Cycle de vie ---------------------------------------------------------------------

    def __enter__(self) -> McpEnDirect:
        if self._pile is not None:
            raise RuntimeError("session MCP déjà ouverte")
        http = client(
            self.profil,
            lib="httpx2",
            asynchrone=True,
            mode=self.mode,
            journal=self.journal,
            transport_interne=self.transport_interne,
            usage="mcp",
            config=self.config,
            liste_blanche=self.liste_blanche,
        )
        crochets = http.event_hooks
        http.event_hooks = {
            "request": crochets.get("request", []),
            "response": [*crochets.get("response", []), self._relever_statut],
        }
        self._statuts = []
        self._initialize = None
        self._interactions = []
        self._fermee = None
        self._debut = datetime.now(UTC).replace(microsecond=0)
        pile = ExitStack()
        try:
            self._portail = pile.enter_context(start_blocking_portal())
            envoi, reception = self._portail.call(_flux_commandes)
            self._envoi = envoi
            pret: Future[None] = Future()
            self._tache = self._portail.start_task_soon(self._executer, http, reception, pret)
            self._pile = pile
            pret.result()
        except BaseException:
            self._fermer()
            pile.close()
            # Session refusée (schéma dérivé, panne…) : rien n'est enregistrable.
            self._initialize = None
            self._interactions = []
            raise
        return self

    def __exit__(self, *_exc: object) -> None:
        self._fermer()

    def _fermer(self) -> None:
        pile, portail, envoi, tache = self._pile, self._portail, self._envoi, self._tache
        self._pile = self._portail = self._envoi = self._tache = None
        if portail is None:
            return
        try:
            if envoi is not None:
                try:
                    portail.call(envoi.aclose)
                except Exception:  # pragma: no cover (portail déjà arrêté)
                    pass
            if tache is not None:
                try:
                    tache.result()
                except Exception:  # erreur déjà remise à l'appelant
                    pass
        finally:
            if pile is not None:
                pile.close()

    async def _relever_statut(self, reponse: Any) -> None:
        if reponse.request.method == "POST":
            self._statuts.append(reponse.status_code)

    async def _executer(
        self,
        http: Any,
        reception: anyio.abc.ObjectReceiveStream[_Commande],
        pret: Future[None],
    ) -> None:
        """Tâche unique de la session : ouverture, puis exécution des commandes une à une."""
        commande: _Commande | None = None
        try:
            async with (
                http,
                reception,
                streamable_http_client(self.url, http_client=http, terminate_on_close=False) as (
                    lecture,
                    ecriture,
                ),
                ClientSession(
                    lecture, ecriture, read_timeout_seconds=self.config.delais.mcp
                ) as session,
            ):
                await self._ouvrir(session)
                pret.set_result(None)
                async for commande in reception:
                    try:
                        resultat = await commande.fonction(session)
                    except Exception as exc:
                        commande.futur.set_exception(exc)
                    else:
                        commande.futur.set_result(resultat)
                    commande = None
        except anyio.get_cancelled_exc_class():
            self._fermee = Injoignable("session MCP interrompue")
            self._remettre(commande, pret, self._fermee)
            raise
        except BaseException as exc:
            self._fermee = self._traduire(exc)
            self._remettre(commande, pret, self._fermee)
        else:
            self._fermee = Injoignable("session MCP fermée")
            self._remettre(commande, pret, self._fermee)

    @staticmethod
    def _remettre(commande: _Commande | None, pret: Future[None], erreur: BaseException) -> None:
        if commande is not None and not commande.futur.done():
            commande.futur.set_exception(erreur)
        if not pret.done():
            pret.set_exception(erreur)

    async def _ouvrir(self, session: ClientSession) -> None:
        self._statuts.clear()
        resultat = await session.initialize()
        self._initialize = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": resultat.model_dump(mode="json", by_alias=True, exclude_unset=True),
        }
        outils: list[dict[str, Any]] = []
        curseur: str | None = None
        for _ in range(_PAGES_MAX):
            params = None if curseur is None else PaginatedRequestParams(cursor=curseur)
            page = await session.list_tools(params=params)
            outils += [
                outil.model_dump(mode="json", by_alias=True, exclude_unset=True)
                for outil in page.tools
            ]
            curseur = page.next_cursor
            if curseur is None:
                break
        comparer_schema_serveur(outils, chemin=self.chemin_outils)

    # --- Traduction des erreurs -----------------------------------------------------------

    def _erreur_mcp(self, exc: MCPError) -> ErreurTransportMcp | None:
        """Panne de transport derrière une `MCPError`, ou `None` pour une erreur JSON-RPC."""
        statut = next((s for s in self._statuts if s >= 400), None)
        if statut is not None:
            return ErreurHttp(f"le serveur MCP a répondu HTTP {statut}", statut=statut)
        if exc.code == REQUEST_TIMEOUT:
            return DelaiDepasse(
                f"appel MCP : délai dépassé ({self.config.delais.mcp:g} s) : {exc.message}"
            )
        if exc.code == CONNECTION_CLOSED:
            return Injoignable(f"connexion MCP fermée : {exc.message}")
        return None

    def _traduire(self, exc: BaseException) -> Exception:
        feuilles = list(_feuilles(exc))
        for classe in (HoteBloque, SlmspError):
            for feuille in feuilles:
                if isinstance(feuille, classe):
                    return feuille
        for feuille in feuilles:
            if isinstance(feuille, MCPError):
                erreur = self._erreur_mcp(feuille)
                if erreur is None:
                    erreur = Injoignable(
                        f"ouverture de la session MCP refusée par le serveur : {feuille.message}"
                    )
                return erreur
        for feuille in feuilles:
            erreur = _erreur_httpx(feuille)
            if erreur is not None:
                return erreur
        for feuille in feuilles:
            if isinstance(feuille, Exception) and not isinstance(feuille, anyio.EndOfStream):
                return feuille
        return Injoignable(f"session MCP interrompue ({type(exc).__name__})")

    # --- ToolPort -------------------------------------------------------------------------

    def _soumettre(self, fonction: Callable[[ClientSession], Awaitable[Any]]) -> Any:
        portail, envoi = self._portail, self._envoi
        if portail is None or envoi is None:
            raise RuntimeError("McpEnDirect s'utilise dans un bloc `with`")
        futur: Future[Any] = Future()
        try:
            portail.call(envoi.send, _Commande(fonction, futur))
        except (anyio.BrokenResourceError, anyio.ClosedResourceError):
            raise Injoignable(f"session MCP fermée ({self._fermee or 'raison inconnue'})") from None
        return futur.result()

    def lister_outils(self) -> list[dict[str, Any]]:
        """Outils figés au format `tools` d'OpenAI (aucune requête)."""
        return charger_outils(self.chemin_outils)

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        """Appelle l'outil `nom` et renvoie la réponse JSON-RPC (`result` ou `error`).

        Lève `AppelNonConforme` sans rien envoyer si l'appel viole le schéma figé, puis
        `DelaiDepasse`, `ErreurHttp`, `Injoignable` ou `HoteBloque` en cas de panne.
        """
        valider_appel(nom, arguments, chemin=self.chemin_outils)
        arguments = copy.deepcopy(dict(arguments))

        async def appel(session: ClientSession) -> dict[str, Any]:
            self._statuts.clear()
            id_ = PREMIER_ID_APPEL + len(self._interactions)
            requete = requete_appel(id_, nom, arguments)
            reponse: dict[str, Any]
            try:
                resultat = await session.send_request(
                    CallToolRequest(params=CallToolRequestParams(name=nom, arguments=arguments)),
                    CallToolResult,
                )
            except MCPError as exc:
                erreur = self._erreur_mcp(exc)
                if erreur is not None:
                    raise erreur from None
                reponse = {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": exc.error.model_dump(mode="json", by_alias=True, exclude_unset=True),
                }
            else:
                reponse = {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "result": resultat.model_dump(mode="json", by_alias=True, exclude_unset=True),
                }
            self._interactions.append(Interaction(request=requete, response=reponse))
            return copy.deepcopy(reponse)

        return self._soumettre(appel)

    # --- Enregistrement -------------------------------------------------------------------

    def session(self, *, item: str | None = None, session_id: str | None = None) -> SessionMcp:
        """Session enregistrable : `initialize` et les interactions `tools/call` retenues.

        `tools_list_sha256` est celui de `config/outils-mcp.toml`. Lève `RuntimeError` si
        la session n'a jamais été ouverte.
        """
        if self._initialize is None or self._debut is None:
            raise RuntimeError("aucune session MCP ouverte : rien à enregistrer")
        cassette = Cassette(
            schema_version=1,
            server=self.url,
            recorded_at=self._debut,
            initialize=copy.deepcopy(self._initialize),
            tools_list_sha256=charger_config(self.chemin_outils).tools_list_sha256,
            interactions=[i.model_copy(deep=True) for i in self._interactions],
        )
        return SessionMcp(
            cassette=cassette,
            session_id=nouvel_identifiant_session() if session_id is None else session_id,
            item=item,
        )


async def _flux_commandes() -> tuple[
    anyio.abc.ObjectSendStream[_Commande], anyio.abc.ObjectReceiveStream[_Commande]
]:
    return anyio.create_memory_object_stream[_Commande](0)


# --- Sonde de santé ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultatSante:
    """Résultat de la sonde `GET /health` du serveur MCP."""

    url: str
    joignable: bool
    statut: int | None
    detail: str


def sonder_sante(
    profil: str = "outillage",
    *,
    mode: ModePort | None = None,
    journal: JournalRequetes | None = None,
    transport_interne: Any = None,
    config: ConfigReseau | None = None,
    liste_blanche: ConfigListeBlanche | None = None,
    url: str | None = None,
) -> ResultatSante:
    """Sonde `GET <sonde.url>` (délai `delais.sonde`) : joignable si le statut est 2xx."""
    config = charger_config_reseau() if config is None else config
    url = config.sonde.url if url is None else url
    http = client(
        profil,
        lib="httpx2",
        asynchrone=False,
        mode=mode,
        journal=journal,
        transport_interne=transport_interne,
        usage="sonde",
        config=config,
        liste_blanche=liste_blanche,
    )
    try:
        with http:
            statut = http.get(url).status_code
    except HoteBloque as exc:
        return ResultatSante(url, False, None, f"requête refusée : {exc}")
    except Exception as exc:
        erreur = _erreur_httpx(exc)
        if erreur is None:
            raise
        return ResultatSante(url, False, None, str(erreur))
    return ResultatSante(url, 200 <= statut < 300, statut, f"HTTP {statut}")
