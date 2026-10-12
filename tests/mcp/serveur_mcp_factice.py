"""Serveur MCP factice en processus pour les tests du client direct (story 3.3).

Partie serveur bas niveau du SDK `mcp` (`Server` + application Streamable HTTP en JSON,
sans session par défaut), branchée comme `transport_interne` du client de la passerelle par
`httpx2.ASGITransport` : aucune socket n'est ouverte. Le `tools/list` est celui du
calibrage (`eval/calibrage/cassettes/tools-list.json`, lu sans jamais être modifié).

`ASGITransport` ne lance pas le cycle de vie ASGI : `session_manager.run()` est démarré
paresseusement, dans la boucle de la première requête (une application par boucle, car
le gestionnaire ne démarre qu'une fois).

Comportements réglables : `lent` (secondes d'attente dans `tools/call`), `statut_post`
(`(n, statut)` : le n-ième POST reçoit ce statut HTTP), `outils_retires` (noms absents du
`tools/list`), `schemas_modifies` (noms dont l'`inputSchema` change), `erreur_jsonrpc`
(`tools/call` répond par une erreur JSON-RPC, statut 200), `erreur_initialize` (idem pour
`initialize`), `lent_liste` (secondes d'attente dans `tools/list`), `taille_page`
(pagination du `tools/list`, curseur = indice du premier outil) et `avec_session`
(serveur avec session `mcp-session-id`, `stateless_http=False`).
"""

from __future__ import annotations

import asyncio
import copy
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import anyio
import httpx2  # noqa: TID251 (tests : transport ASGI en processus)
import mcp.types as types
from mcp.server.lowlevel.server import Server
from mcp.server.transport_security import TransportSecuritySettings
from mcp.shared.exceptions import MCPError

RACINE = Path(__file__).resolve().parents[2]
TOOLS_LIST = RACINE / "eval" / "calibrage" / "cassettes" / "tools-list.json"

CODE_ERREUR_FACTICE = -32602
MESSAGE_ERREUR_FACTICE = "<erreur-factice>"


def outils_calibrage() -> list[dict[str, Any]]:
    """`result.tools` du `tools/list` enregistré au calibrage (copie)."""
    donnees = json.loads(TOOLS_LIST.read_text(encoding="utf-8"))
    for interaction in donnees["interactions"]:
        if interaction["request"]["method"] == "tools/list":
            return copy.deepcopy(interaction["response"]["result"]["tools"])
    raise AssertionError("tools-list.json sans interaction tools/list")


def texte_factice(nom: str) -> str:
    return f"<reponse-factice-{nom}>"


class ServeurMcpFactice:
    """Application ASGI : serveur MCP factice et journal des requêtes reçues."""

    def __init__(
        self,
        *,
        lent: float = 0.0,
        statut_post: tuple[int, int] | None = None,
        outils_retires: Iterable[str] = (),
        schemas_modifies: Iterable[str] = (),
        erreur_jsonrpc: bool = False,
        erreur_initialize: bool = False,
        lent_liste: float = 0.0,
        taille_page: int | None = None,
        avec_session: bool = False,
    ) -> None:
        self.lent = lent
        self.erreur_initialize = erreur_initialize
        self.lent_liste = lent_liste
        self.taille_page = taille_page
        self.avec_session = avec_session
        self.curseurs: list[str | None] = []
        """Curseur de chaque `tools/list` reçu."""
        self.sessions: list[str] = []
        """En-tête `mcp-session-id` de chaque réponse qui en porte un."""
        self.statut_post = statut_post
        self.erreur_jsonrpc = erreur_jsonrpc
        outils = [o for o in outils_calibrage() if o["name"] not in set(outils_retires)]
        for outil in outils:
            if outil["name"] in set(schemas_modifies):
                outil["inputSchema"]["properties"]["ajout_factice"] = {"type": "string"}
        self.outils = [types.Tool.model_validate(o) for o in outils]
        self.requetes: list[tuple[str, str | None]] = []
        """(méthode HTTP, méthode JSON-RPC) de chaque requête reçue."""
        self.appels: list[tuple[str, dict[str, Any]]] = []
        self._posts = 0
        self._boucle: asyncio.AbstractEventLoop | None = None
        self._app: Any = None
        self._pret: asyncio.Event | None = None

    def transport(self) -> httpx2.ASGITransport:
        return httpx2.ASGITransport(app=self)

    @property
    def methodes(self) -> list[str | None]:
        return [methode for _, methode in self.requetes]

    # --- Serveur MCP ----------------------------------------------------------------------

    def _serveur(self) -> Server[Any]:
        async def lister(
            _ctx: Any, params: types.PaginatedRequestParams | None
        ) -> types.ListToolsResult:
            curseur = params.cursor if params is not None else None
            self.curseurs.append(curseur)
            if self.lent_liste:
                await anyio.sleep(self.lent_liste)
            if self.taille_page is None:
                return types.ListToolsResult(tools=list(self.outils))
            debut = int(curseur or 0)
            fin = debut + self.taille_page
            suivant = str(fin) if fin < len(self.outils) else None
            return types.ListToolsResult(tools=self.outils[debut:fin], next_cursor=suivant)

        async def appeler(_ctx: Any, params: types.CallToolRequestParams) -> types.CallToolResult:
            self.appels.append((params.name, dict(params.arguments or {})))
            if self.lent:
                await anyio.sleep(self.lent)
            if self.erreur_jsonrpc:
                raise MCPError(code=CODE_ERREUR_FACTICE, message=MESSAGE_ERREUR_FACTICE)
            texte = texte_factice(params.name)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=texte)],
                structured_content={"result": texte},
                is_error=False,
            )

        return Server(
            "serveur-mcp-factice", version="0.0.0", on_list_tools=lister, on_call_tool=appeler
        )

    async def _demarrer(self) -> None:
        boucle = asyncio.get_running_loop()
        if self._boucle is not boucle:
            self._boucle = boucle
            self._pret = asyncio.Event()
            serveur = self._serveur()
            self._app = serveur.streamable_http_app(
                json_response=True,
                stateless_http=not self.avec_session,
                transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
            )
            pret = self._pret

            async def tourner() -> None:
                async with serveur.session_manager.run():
                    pret.set()
                    await asyncio.Event().wait()

            # Tâche de fond annulée à la fermeture de la boucle (portail du client).
            self._tache = boucle.create_task(tourner())
        assert self._pret is not None
        await self._pret.wait()

    # --- ASGI -----------------------------------------------------------------------------

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        assert scope["type"] == "http"
        corps = b""
        plus = True
        while plus:
            message = await receive()
            corps += message.get("body", b"")
            plus = message.get("more_body", False)
        methode = id_ = None
        if corps:
            try:
                message = json.loads(corps)
                methode, id_ = message.get("method"), message.get("id")
            except (ValueError, AttributeError):
                methode = None
        self.requetes.append((scope["method"], methode))
        if scope["method"] == "POST":
            self._posts += 1
            if self.statut_post is not None and self._posts == self.statut_post[0]:
                await send(
                    {
                        "type": "http.response.start",
                        "status": self.statut_post[1],
                        "headers": [(b"content-type", b"text/plain")],
                    }
                )
                await send({"type": "http.response.body", "body": b"<panne-factice>"})
                return
            if self.erreur_initialize and methode == "initialize":
                erreur = {"code": CODE_ERREUR_FACTICE, "message": MESSAGE_ERREUR_FACTICE}
                reponse = {"jsonrpc": "2.0", "id": id_, "error": erreur}
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send({"type": "http.response.body", "body": json.dumps(reponse).encode()})
                return
        await self._demarrer()
        envoye = False

        async def rejouer() -> dict[str, Any]:
            nonlocal envoye
            if not envoye:
                envoye = True
                return {"type": "http.request", "body": corps, "more_body": False}
            await anyio.sleep_forever()
            raise AssertionError("inatteignable")

        async def envoyer(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                for cle, valeur in message.get("headers", []):
                    if cle.lower() == b"mcp-session-id":
                        self.sessions.append(valeur.decode("ascii"))
            await send(message)

        await self._app(scope, rejouer, envoyer)
