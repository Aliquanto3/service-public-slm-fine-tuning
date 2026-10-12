"""Transports gardés : chaque requête (et chaque saut de redirection) est contrôlée avant
le transport interne, puis journalisée (AD-4).

Un refus lève `HoteBloque` avant tout appel au transport interne et donne une entrée
`bloquee-liste` ou `bloquee-mode`. Une requête permise donne une entrée `envoyee` quand
le transport interne a rendu sa réponse (en-têtes reçus), ou `echouee` s'il a levé une
exception, relancée telle quelle.

`lib` vaut `httpx2` (socle) ou `httpx` (importé paresseusement : absent du socle).
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, Final, Protocol

import httpx2

from slmsp.core.erreurs import HoteBloque
from slmsp.core.ports import JournalRequetes, Mode, ModePort
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes, StatutRequete
from slmsp.net.config import ConfigListeBlanche, ConfigReseau
from slmsp.net.journal import extraire_appel_outil
from slmsp.net.profils import (
    MODE_ILLISIBLE,
    PROFILS,
    analyser_url,
    evaluer,
    hote_de,
    lire_mode,
)

LIBS: Final = ("httpx2", "httpx")
HOTE_LOCAL: Final = "127.0.0.1"


def module_http(lib: str) -> ModuleType:
    """Module client HTTP de `lib` ; `httpx` est importé à la demande."""
    if lib == "httpx2":
        return httpx2
    if lib == "httpx":
        import httpx

        return httpx
    raise ValueError(f"bibliothèque HTTP inconnue : {lib!r} (attendu : {', '.join(LIBS)})")


class _Controleur(Protocol):
    def controler(self, requete: Any) -> Any: ...

    def consigner(self, requete: Any, statut: StatutRequete, jeton: Any) -> None: ...


def _corps(requete: Any) -> bytes | None:
    try:
        contenu = requete.content
    except Exception:  # RequestNotRead : corps en flux, illisible sans le consommer
        return None
    return contenu if isinstance(contenu, bytes) else None


@dataclass(frozen=True)
class Contexte:
    """Ce que le journal retient d'une requête, relevé une fois avant l'envoi."""

    mode: Mode | None
    hote: str
    methode: str
    outil: str | None
    termes: str | None
    mode_illisible: bool = False
    erreur_mode: Exception | None = None


@dataclass
class Garde:
    """Contrôle et journal d'un client : profil, source du Mode, journal, configuration."""

    profil: str
    mode: ModePort | None
    journal: JournalRequetes
    config: ConfigReseau
    liste_blanche: ConfigListeBlanche

    def __post_init__(self) -> None:
        if self.profil not in PROFILS:
            raise ValueError(f"profil inconnu : {self.profil!r} (attendu : {', '.join(PROFILS)})")
        if self.profil == "assistant" and self.mode is None:
            raise ValueError("le profil assistant exige un ModePort (`mode`)")

    def controler(self, requete: Any) -> Contexte:
        """Contexte de la requête (Mode lu, appel d'outil), relevé avant l'envoi.

        Journalise et lève `HoteBloque` si la requête est refusée. Un Mode illisible (le
        `ModePort` lève ou rend une valeur hors `Mode`) refuse la requête (`bloquee-mode`).
        """
        contexte = self.contexte(requete)
        if contexte.mode_illisible:
            verdict = MODE_ILLISIBLE
        else:
            verdict = evaluer(
                self.profil,
                requete.method,
                requete.url,
                mode=contexte.mode,
                config=self.config,
                liste_blanche=self.liste_blanche,
            )
        if verdict.statut is not None:
            self.consigner(requete, verdict.statut, contexte)
            raise HoteBloque(
                f"Requête refusée ({verdict.motif}) : profil {self.profil}, "
                f"{contexte.methode} {contexte.hote or '<hôte illisible>'}"
            ) from contexte.erreur_mode
        return contexte

    def contexte(self, requete: Any) -> Contexte:
        """Mode courant, hôte normalisé et appel d'outil (corps déjà en mémoire seulement)."""
        methode = requete.method.upper()
        outil = termes = None
        if methode == "POST":
            corps = _corps(requete)
            if corps is not None:
                outil, termes = extraire_appel_outil(corps)
        lecture = lire_mode(self.mode)
        return Contexte(
            lecture.mode,
            hote_de(requete.url),
            methode,
            outil,
            termes,
            lecture.illisible,
            lecture.erreur,
        )

    def consigner(
        self, requete: Any, statut: StatutRequete, contexte: Contexte | None = None
    ) -> None:
        """Inscrit l'issue `statut` de `requete` au journal."""
        if contexte is None:
            contexte = self.contexte(requete)
        self.journal.inscrire(
            EntreeJournalRequetes(
                horodatage=datetime.now(UTC),
                profil=self.profil,
                hote=contexte.hote,
                methode=contexte.methode,
                outil=contexte.outil,
                termes=contexte.termes,
                statut=statut,
                mode=contexte.mode,
            )
        )


@dataclass(frozen=True)
class GardeLocale:
    """Contrôle du client local : seul `http://127.0.0.1:<port>` passe, sans journal."""

    port: int

    def controler(self, requete: Any) -> None:
        try:
            cible = analyser_url(requete.url)
        except ValueError:
            cible = None
        port = None
        if cible is not None:
            port = cible.port if cible.port is not None else {"http": 80}.get(cible.schema)
        if (
            cible is None
            or cible.schema != "http"
            or cible.hote != HOTE_LOCAL
            or port != self.port
            or cible.identifiants
        ):
            raise HoteBloque(
                f"Requête locale refusée : seul http://{HOTE_LOCAL}:{self.port} est permis "
                f"({requete.method.upper()} {hote_de(requete.url) or '<hôte illisible>'})"
            )

    def consigner(self, requete: Any, statut: StatutRequete, jeton: Any) -> None:
        return None


@functools.cache
def _classe_gardee(module: ModuleType, asynchrone: bool) -> type:
    if asynchrone:

        class TransportGardeAsync(module.AsyncBaseTransport):
            def __init__(self, controleur: _Controleur, interne: Any) -> None:
                self.controleur = controleur
                self.interne = interne

            async def handle_async_request(self, request: Any) -> Any:
                jeton = self.controleur.controler(request)
                try:
                    reponse = await self.interne.handle_async_request(request)
                except BaseException:
                    self.controleur.consigner(request, "echouee", jeton)
                    raise
                try:
                    self.controleur.consigner(request, "envoyee", jeton)
                except BaseException:
                    await reponse.aclose()
                    raise
                return reponse

            async def aclose(self) -> None:
                await self.interne.aclose()

        return TransportGardeAsync

    class TransportGarde(module.BaseTransport):
        def __init__(self, controleur: _Controleur, interne: Any) -> None:
            self.controleur = controleur
            self.interne = interne

        def handle_request(self, request: Any) -> Any:
            jeton = self.controleur.controler(request)
            try:
                reponse = self.interne.handle_request(request)
            except BaseException:
                self.controleur.consigner(request, "echouee", jeton)
                raise
            try:
                self.controleur.consigner(request, "envoyee", jeton)
            except BaseException:
                reponse.close()
                raise
            return reponse

        def close(self) -> None:
            self.interne.close()

    return TransportGarde


def transport_interne_defaut(lib: str, asynchrone: bool) -> Any:
    """Transport réel de `lib`, sans relance ni lecture de l'environnement."""
    module = module_http(lib)
    classe = module.AsyncHTTPTransport if asynchrone else module.HTTPTransport
    return classe(retries=0, trust_env=False)


def transport_garde(lib: str, asynchrone: bool, garde: Garde, interne: Any = None) -> Any:
    """Transport de `lib` (sync ou async) qui contrôle par `garde` puis délègue à `interne`."""
    module = module_http(lib)
    if interne is None:
        interne = transport_interne_defaut(lib, asynchrone)
    return _classe_gardee(module, asynchrone)(garde, interne)


def transport_local(lib: str, asynchrone: bool, port: int, interne: Any = None) -> Any:
    """Transport de `lib` limité à `http://127.0.0.1:<port>` (sans journal)."""
    module = module_http(lib)
    if interne is None:
        interne = transport_interne_defaut(lib, asynchrone)
    return _classe_gardee(module, asynchrone)(GardeLocale(port), interne)
