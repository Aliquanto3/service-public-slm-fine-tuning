"""Doublures communes des tests de la passerelle : Mode fixe, transport interne compteur."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests de la passerelle : transports factices)
import pytest

from slmsp.net.config import (
    ConfigListeBlanche,
    ConfigReseau,
    charger_config_reseau,
    charger_liste_blanche,
)
from slmsp.net.journal import JournalMemoire


class ModeDouble:
    """Doublure de `ModePort` (les vraies implémentations arrivent avec l'Epic 4)."""

    def __init__(self, mode: str = "connecte") -> None:
        self.mode = mode

    def mode_courant(self) -> str:
        return self.mode


@dataclass
class Compteur:
    """Gestionnaire de `MockTransport` qui compte ses appels et répond par `repondre`."""

    repondre: Callable[[Any], Any] | None = None
    module: Any = httpx2
    requetes: list[Any] = field(default_factory=list)

    @property
    def appels(self) -> int:
        return len(self.requetes)

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        if self.repondre is not None:
            return self.repondre(requete)
        return self.module.Response(200, request=requete)


def module_lib(lib: str) -> Any:
    if lib == "httpx":
        return pytest.importorskip("httpx")
    return httpx2


@dataclass
class Emission:
    """Résultat d'une requête émise par un client gardé."""

    reponse: Any
    erreur: BaseException | None
    compteur: Compteur
    journal: JournalMemoire


@pytest.fixture(scope="session")
def doublures() -> SimpleNamespace:
    """Doublures importables par les modules de test (mode d'import `importlib`)."""
    return SimpleNamespace(ModeDouble=ModeDouble, Compteur=Compteur, module_lib=module_lib)


@pytest.fixture(scope="session")
def config_reseau() -> ConfigReseau:
    return charger_config_reseau()


@pytest.fixture(scope="session")
def liste_blanche() -> ConfigListeBlanche:
    return charger_liste_blanche()


@pytest.fixture
def emettre(
    config_reseau: ConfigReseau, liste_blanche: ConfigListeBlanche
) -> Callable[..., Emission]:
    """Émet `methode url` par un client gardé neuf (sync ou async, httpx2 ou httpx)."""
    from slmsp.net import client

    def _emettre(
        profil: str,
        methode: str,
        url: str,
        *,
        mode: str | None = "connecte",
        asynchrone: bool = False,
        lib: str = "httpx2",
        compteur: Compteur | None = None,
        follow_redirects: bool = False,
        **options: Any,
    ) -> Emission:
        module = module_lib(lib)
        compteur = Compteur(module=module) if compteur is None else compteur
        journal = JournalMemoire()
        garde = client(
            profil,
            lib,
            asynchrone,
            None if mode is None else ModeDouble(mode),
            journal,
            module.MockTransport(compteur),
            config=config_reseau,
            liste_blanche=liste_blanche,
            follow_redirects=follow_redirects,
        )
        reponse = erreur = None
        try:
            if asynchrone:

                async def envoyer() -> Any:
                    async with garde:
                        return await garde.request(methode, url, **options)

                reponse = asyncio.run(envoyer())
            else:
                with garde:
                    reponse = garde.request(methode, url, **options)
        except Exception as exc:
            erreur = exc
        return Emission(reponse, erreur, compteur, journal)

    return _emettre
