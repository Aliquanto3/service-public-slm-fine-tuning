"""Fixtures communes : garde réseau et `SLMSP_VAR_DIR` temporaire (critère 5 de la story 1.1)."""

from __future__ import annotations

import asyncio
import asyncio.proactor_events
import asyncio.selector_events
import ipaddress
import socket
from typing import Any

import pytest

_NOMS_LOCAUX = {"localhost"}


def adresse_locale(adresse: Any) -> bool:
    """Vrai si `adresse` (argument de `socket.connect`) désigne la boucle locale."""
    if isinstance(adresse, (str, bytes)):
        return True  # socket AF_UNIX : chemin local
    if not isinstance(adresse, tuple) or not adresse:
        return False
    hote = adresse[0]
    if isinstance(hote, bytes):
        hote = hote.decode("ascii", errors="replace")
    hote = str(hote).strip().strip("[]").rstrip(".").lower()
    if hote in _NOMS_LOCAUX:
        return True
    try:
        ip = ipaddress.ip_address(hote.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_loopback


def _refuser(adresse: Any) -> None:
    if not adresse_locale(adresse):
        raise RuntimeError(
            f"Connexion réseau interdite pendant les tests : {adresse!r}. "
            "Seule la boucle locale est permise ; marquer le test `reseau` si l'accès est voulu."
        )


def resolution_permise(hote: Any) -> bool:
    """Vrai si `socket.getaddrinfo(hote, ...)` ne déclenche pas de requête DNS sortante."""
    if hote is None:
        return True
    if isinstance(hote, bytes):
        hote = hote.decode("ascii", errors="replace")
    hote = str(hote).strip().strip("[]").rstrip(".").lower()
    if hote == "" or hote in _NOMS_LOCAUX:
        return True
    try:
        ipaddress.ip_address(hote.split("%", 1)[0])  # IP littérale : aucune résolution
    except ValueError:
        return False
    return True


def _garder_getaddrinfo(original):
    def getaddrinfo(hote, *args, **kwargs):
        if not resolution_permise(hote):
            raise RuntimeError(
                f"Résolution DNS interdite pendant les tests : {hote!r}. "
                "Seule la boucle locale est permise ; marquer le test `reseau` si besoin."
            )
        return original(hote, *args, **kwargs)

    return getaddrinfo


def _garder_connect(original):
    def connect(self, adresse, *args, **kwargs):
        _refuser(adresse)
        return original(self, adresse, *args, **kwargs)

    return connect


def _garder_sock_connect(original):
    async def sock_connect(self, sock, adresse):
        _refuser(adresse)
        return await original(self, sock, adresse)

    return sock_connect


_BOUCLES = (
    asyncio.BaseEventLoop,
    asyncio.selector_events.BaseSelectorEventLoop,
    asyncio.proactor_events.BaseProactorEventLoop,
)


@pytest.fixture(autouse=True)
def _garde_reseau(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fait échouer toute connexion hors boucle locale, sauf pour les tests marqués `reseau`."""
    if request.node.get_closest_marker("reseau") is not None:
        return
    monkeypatch.setattr(socket.socket, "connect", _garder_connect(socket.socket.connect))
    monkeypatch.setattr(socket.socket, "connect_ex", _garder_connect(socket.socket.connect_ex))
    # La résolution DNS d'un nom distant part avant toute connexion.
    monkeypatch.setattr(socket, "getaddrinfo", _garder_getaddrinfo(socket.getaddrinfo))
    # La boucle Proactor (Windows) se connecte par ConnectEx, sans passer par socket.connect.
    for boucle in _BOUCLES:
        if "sock_connect" in vars(boucle):
            monkeypatch.setattr(boucle, "sock_connect", _garder_sock_connect(boucle.sock_connect))


@pytest.fixture(autouse=True)
def _var_dir_temporaire(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pointe `SLMSP_VAR_DIR` sur un dossier temporaire propre à chaque test."""
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path_factory.mktemp("var")))
