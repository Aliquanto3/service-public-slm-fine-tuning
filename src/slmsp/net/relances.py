"""Outils de relance HTTP partagés : `Retry-After`, attente exponentielle, statuts et erreurs
transitoires, délais explicites par appel (connexion, lecture, échéance totale).

`DelaisAppel` est appliqué par `TransportEcheance`, placé sous la garde réseau
(`slmsp.net.client.client(..., delais_appel=...)`) : il impose à chaque requête ses délais de
connexion et de lecture (quels que soient ceux du SDK appelant) et une échéance totale,
contrôlée avant l'envoi, à l'arrivée des en-têtes et à chaque morceau du corps. Un
dépassement lève le `ReadTimeout` de la bibliothèque HTTP (erreur de transport, donc
transitoire). Un appel dure ainsi au plus `total + lecture` environ.
"""

from __future__ import annotations

import email.utils
import math
import random
import time
from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, Final

STATUTS_TRANSITOIRES: Final = frozenset({429, 500, 502, 503, 504})
"""Réponses HTTP relancées : limite de débit et erreurs serveur passagères."""


def statut_transitoire(statut: int | None) -> bool:
    """Vrai pour un statut HTTP relançable (`STATUTS_TRANSITOIRES`)."""
    return statut in STATUTS_TRANSITOIRES


def erreur_transport(exc: BaseException) -> bool:
    """Vrai pour une erreur de transport : `httpx*.TransportError` (délais d'attente compris),
    `ConnectionError` ou `TimeoutError`. Une autre `OSError` (disque plein, droits) n'est
    pas relancée."""
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    return any(
        classe.__name__ == "TransportError" and classe.__module__.split(".")[0].startswith("httpx")
        for classe in type(exc).__mro__
    )


def lire_retry_after(valeur: str | None, maintenant: datetime | None = None) -> float | None:
    """Attente demandée par `Retry-After` (secondes ou date HTTP), `None` si absente ou
    non finie (`inf`, `nan`)."""
    if valeur is None or not valeur.strip():
        return None
    valeur = valeur.strip()
    try:
        secondes = float(valeur)
    except ValueError:
        pass
    else:
        return max(0.0, secondes) if math.isfinite(secondes) else None
    try:
        date = email.utils.parsedate_to_datetime(valeur)
    except (TypeError, ValueError):
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=UTC)
    return max(0.0, (date - (maintenant or datetime.now(UTC))).total_seconds())


def attente_exponentielle(
    reessai: int,
    base: float,
    plafond: float,
    alea: Callable[[], float] = random.random,
) -> float:
    """Attente avant le réessai n° `reessai` (1 pour le premier) : `base * 2**(reessai-1)`,
    bornée par `plafond`, avec une gigue qui la ramène dans [moitié, totalité]."""
    if reessai < 1:
        raise ValueError("reessai doit valoir au moins 1")
    nominale = min(plafond, base * 2.0 ** min(reessai - 1, 62))
    return nominale * (0.5 + 0.5 * min(1.0, max(0.0, alea())))


@dataclass(frozen=True)
class DelaisAppel:
    """Délais d'un appel HTTP, en secondes : connexion, lecture (et écriture), total."""

    connexion: float
    lecture: float
    total: float

    def __post_init__(self) -> None:
        for nom in ("connexion", "lecture", "total"):
            valeur = getattr(self, nom)
            if not (isinstance(valeur, int | float) and math.isfinite(valeur) and valeur > 0):
                raise ValueError(f"délai {nom} invalide : {valeur!r} (secondes > 0)")

    def extension(self) -> dict[str, float]:
        """Valeur de `request.extensions["timeout"]` lue par les transports httpx."""
        return {
            "connect": self.connexion,
            "read": self.lecture,
            "write": self.lecture,
            "pool": self.connexion,
        }


def _horloge() -> float:
    return time.monotonic()


def _depasse(module: ModuleType, requete: Any, delais: DelaisAppel) -> Exception:
    return module.ReadTimeout(
        f"délai total de l'appel dépassé ({delais.total:g} s)", request=requete
    )


def _classe_echeance(module: ModuleType, asynchrone: bool) -> type:
    if asynchrone:

        class FluxBorneAsync(module.AsyncByteStream):
            def __init__(self, flux: Any, echeance: float, requete: Any, delais: DelaisAppel):
                self.flux, self.echeance, self.requete, self.delais = (
                    flux,
                    echeance,
                    requete,
                    delais,
                )

            async def __aiter__(self) -> AsyncIterator[bytes]:
                async for morceau in self.flux:
                    if _horloge() > self.echeance:
                        raise _depasse(module, self.requete, self.delais)
                    yield morceau

            async def aclose(self) -> None:
                await self.flux.aclose()

        class TransportEcheanceAsync(module.AsyncBaseTransport):
            def __init__(self, interne: Any, delais: DelaisAppel) -> None:
                self.interne = interne
                self.delais = delais

            async def handle_async_request(self, request: Any) -> Any:
                echeance = _horloge() + self.delais.total
                request.extensions["timeout"] = self.delais.extension()
                reponse = await self.interne.handle_async_request(request)
                if _horloge() > echeance:
                    await reponse.aclose()
                    raise _depasse(module, request, self.delais)
                reponse.stream = FluxBorneAsync(reponse.stream, echeance, request, self.delais)
                return reponse

            async def aclose(self) -> None:
                await self.interne.aclose()

        return TransportEcheanceAsync

    class FluxBorne(module.SyncByteStream):
        def __init__(self, flux: Any, echeance: float, requete: Any, delais: DelaisAppel):
            self.flux, self.echeance, self.requete, self.delais = flux, echeance, requete, delais

        def __iter__(self) -> Iterator[bytes]:
            for morceau in self.flux:
                if _horloge() > self.echeance:
                    raise _depasse(module, self.requete, self.delais)
                yield morceau

        def close(self) -> None:
            self.flux.close()

    class TransportEcheance(module.BaseTransport):
        def __init__(self, interne: Any, delais: DelaisAppel) -> None:
            self.interne = interne
            self.delais = delais

        def handle_request(self, request: Any) -> Any:
            echeance = _horloge() + self.delais.total
            request.extensions["timeout"] = self.delais.extension()
            reponse = self.interne.handle_request(request)
            if _horloge() > echeance:
                reponse.close()
                raise _depasse(module, request, self.delais)
            reponse.stream = FluxBorne(reponse.stream, echeance, request, self.delais)
            return reponse

        def close(self) -> None:
            self.interne.close()

    return TransportEcheance


_CLASSES: dict[tuple[str, bool], type] = {}


def transport_echeance(
    module: ModuleType, asynchrone: bool, interne: Any, delais: DelaisAppel
) -> Any:
    """Transport de `module` qui impose `delais` à chaque requête puis délègue à `interne`."""
    cle = (module.__name__, asynchrone)
    if cle not in _CLASSES:
        _CLASSES[cle] = _classe_echeance(module, asynchrone)
    return _CLASSES[cle](interne, delais)
