"""Critère 5 de la story 1.1 : marqueurs pytest, garde réseau et `SLMSP_VAR_DIR` temporaire."""

from __future__ import annotations

import asyncio
import os
import socket
from pathlib import Path

import pytest

pytest_plugins = ["pytester"]

ADRESSE_DISTANTE = ("93.184.216.34", 80)
RACINE = Path(__file__).resolve().parents[1]


def test_marqueurs_declares_et_exclus_par_defaut(pytestconfig: pytest.Config) -> None:
    marqueurs = {ligne.split(":", 1)[0].strip() for ligne in pytestconfig.getini("markers")}
    assert {"reseau", "gpu", "lent"} <= marqueurs
    addopts = " ".join(pytestconfig.getini("addopts"))
    assert "not reseau and not gpu and not lent" in addopts


def test_connect_distant_refuse() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with pytest.raises(RuntimeError, match="interdite"):
            sock.connect(ADRESSE_DISTANTE)


def test_connect_ex_distant_refuse() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with pytest.raises(RuntimeError, match="interdite"):
            sock.connect_ex(ADRESSE_DISTANTE)


def test_create_connection_distant_refuse() -> None:
    with pytest.raises(RuntimeError, match="interdite"):
        socket.create_connection(ADRESSE_DISTANTE, timeout=1)


def test_resolution_dns_distante_refusee() -> None:
    with pytest.raises(RuntimeError, match="DNS interdite"):
        socket.create_connection(("example.invalid", 80), timeout=1)


def test_asyncio_distant_refuse() -> None:
    async def ouvrir() -> None:
        await asyncio.open_connection(*ADRESSE_DISTANTE)

    with pytest.raises(RuntimeError, match="interdite"):
        asyncio.run(ouvrir())


def _serveur(famille: socket.AddressFamily, hote: str) -> socket.socket:
    serveur = socket.socket(famille, socket.SOCK_STREAM)
    serveur.bind((hote, 0))
    serveur.listen(1)
    return serveur


@pytest.mark.parametrize("hote", ["127.0.0.1", "localhost"])
def test_connect_local_ipv4_autorise(hote: str) -> None:
    with _serveur(socket.AF_INET, "127.0.0.1") as serveur:
        port = serveur.getsockname()[1]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((hote, port))


def test_connect_local_ipv6_autorise() -> None:
    if not socket.has_ipv6:
        pytest.skip("IPv6 indisponible")
    try:
        serveur = _serveur(socket.AF_INET6, "::1")
    except OSError:
        pytest.skip("boucle locale IPv6 indisponible")
    with serveur:
        port = serveur.getsockname()[1]
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as client:
            client.connect(("::1", port))


def test_asyncio_local_autorise() -> None:
    async def echanger() -> bytes:
        async def repondre(lecteur: asyncio.StreamReader, ecrivain: asyncio.StreamWriter) -> None:
            ecrivain.write(await lecteur.readline())
            await ecrivain.drain()
            ecrivain.close()

        serveur = await asyncio.start_server(repondre, "127.0.0.1", 0)
        port = serveur.sockets[0].getsockname()[1]
        async with serveur:
            lecteur, ecrivain = await asyncio.open_connection("127.0.0.1", port)
            ecrivain.write(b"ok\n")
            await ecrivain.drain()
            ligne = await lecteur.readline()
            ecrivain.close()
            await ecrivain.wait_closed()
            return ligne

    assert asyncio.run(echanger()) == b"ok\n"


def test_garde_levee_pour_un_test_marque_reseau(pytester: pytest.Pytester) -> None:
    pytester.makeconftest((RACINE / "tests" / "conftest.py").read_text(encoding="utf-8"))
    pytester.makeini("[pytest]\nmarkers =\n    reseau: accès réseau\n")
    pytester.makepyfile(
        test_interne="""
        import socket

        import pytest


        @pytest.mark.reseau
        def test_marque():
            assert "connect" not in vars(socket.socket)


        def test_non_marque():
            assert "connect" in vars(socket.socket)
        """
    )
    resultat = pytester.runpytest_subprocess("-p", "no:cacheprovider")
    resultat.assert_outcomes(passed=2)


def test_var_dir_temporaire() -> None:
    var = Path(os.environ["SLMSP_VAR_DIR"])
    assert var.is_dir()
    assert RACINE not in var.parents
