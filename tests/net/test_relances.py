"""Outils de relance de `slmsp.net.relances` : Retry-After, attente exponentielle, statuts
transitoires, délais explicites et échéance totale d'un appel (transport factice)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx2  # noqa: TID251 (tests de la passerelle : transport factice)
import pytest

from slmsp.net import relances
from slmsp.net.client import client
from slmsp.net.journal import JournalMemoire
from slmsp.net.relances import (
    DelaisAppel,
    attente_exponentielle,
    erreur_transport,
    lire_retry_after,
    statut_transitoire,
)

URL = "https://api.mistral.ai/v1/chat/completions"
DELAIS = DelaisAppel(connexion=4.0, lecture=7.0, total=30.0)


def test_lire_retry_after_secondes_et_date() -> None:
    maintenant = datetime(2026, 10, 12, 12, 0, 0, tzinfo=UTC)
    assert lire_retry_after(None) is None
    assert lire_retry_after(" 12 ") == 12.0
    assert lire_retry_after("Mon, 12 Oct 2026 12:01:00 GMT", maintenant) == 60.0
    assert lire_retry_after("Mon, 12 Oct 2026 11:00:00 GMT", maintenant) == 0.0
    assert lire_retry_after("bientôt") is None


def test_lire_retry_after_reexporte_par_fetch() -> None:
    from slmsp.fetch import hf

    assert hf.lire_retry_after is lire_retry_after
    assert hf.erreur_transport is erreur_transport


def test_attente_exponentielle_bornee_avec_gigue() -> None:
    assert [attente_exponentielle(n, 2.0, 60.0, lambda: 1.0) for n in range(1, 7)] == [
        2.0,
        4.0,
        8.0,
        16.0,
        32.0,
        60.0,
    ]
    assert attente_exponentielle(3, 2.0, 60.0, lambda: 0.0) == 4.0  # moitié de 8
    assert attente_exponentielle(500, 2.0, 60.0, lambda: 1.0) == 60.0
    with pytest.raises(ValueError):
        attente_exponentielle(0, 2.0, 60.0)


@pytest.mark.parametrize(
    ("statut", "attendu"),
    [(429, True), (500, True), (502, True), (503, True), (504, True), (400, False)]
    + [(401, False), (404, False), (501, False), (None, False)],
)
def test_statut_transitoire(statut: int | None, attendu: bool) -> None:
    assert statut_transitoire(statut) is attendu


def test_erreurs_de_transport() -> None:
    assert erreur_transport(httpx2.ReadTimeout("lent"))
    assert erreur_transport(httpx2.ConnectError("refus"))
    assert erreur_transport(TimeoutError())
    assert not erreur_transport(PermissionError())
    assert not erreur_transport(ValueError())


@pytest.mark.parametrize("champ", ["connexion", "lecture", "total"])
@pytest.mark.parametrize("valeur", [0, -1, float("inf"), float("nan")])
def test_delais_invalides(champ: str, valeur: float) -> None:
    valeurs = {"connexion": 1.0, "lecture": 1.0, "total": 1.0, champ: valeur}
    with pytest.raises(ValueError):
        DelaisAppel(**valeurs)


def _reponse(requete: Any) -> Any:
    return httpx2.Response(200, content=b"x" * 30, request=requete)


def test_delais_imposes_a_chaque_requete() -> None:
    vus: list[Any] = []

    def servir(requete: Any) -> Any:
        vus.append(dict(requete.extensions["timeout"]))
        return _reponse(requete)

    with client(
        "outillage",
        journal=JournalMemoire(),
        transport_interne=httpx2.MockTransport(servir),
        delais_appel=DELAIS,
    ) as garde:
        garde.post(URL, timeout=999.0)  # le délai demandé par l'appelant est remplacé
        garde.post(URL)
    attendu = {"connect": 4.0, "read": 7.0, "write": 7.0, "pool": 4.0}
    assert vus == [attendu, attendu]


class _Flux(httpx2.SyncByteStream):
    def __iter__(self) -> Any:
        yield from (b"a", b"b", b"c")


def test_echeance_depassee_pendant_le_corps(monkeypatch: pytest.MonkeyPatch) -> None:
    instants = iter([0.0, 1.0, 2.0, 31.0])
    monkeypatch.setattr(relances, "_horloge", lambda: next(instants))
    journal = JournalMemoire()
    servir = httpx2.MockTransport(lambda r: httpx2.Response(200, stream=_Flux(), request=r))
    with client("outillage", journal=journal, transport_interne=servir, delais_appel=DELAIS) as g:
        with pytest.raises(httpx2.ReadTimeout, match="délai total"):
            g.post(URL)


def test_echeance_depassee_avant_les_en_tetes(monkeypatch: pytest.MonkeyPatch) -> None:
    instants = iter([0.0, 45.0])
    monkeypatch.setattr(relances, "_horloge", lambda: next(instants))
    servir = httpx2.MockTransport(_reponse)
    with client(
        "outillage", journal=JournalMemoire(), transport_interne=servir, delais_appel=DELAIS
    ) as garde:
        with pytest.raises(httpx2.ReadTimeout):
            garde.post(URL)


def test_echeance_respectee() -> None:
    with client(
        "outillage",
        journal=JournalMemoire(),
        transport_interne=httpx2.MockTransport(_reponse),
        delais_appel=DELAIS,
    ) as garde:
        assert garde.post(URL).content == b"x" * 30


def test_echeance_asynchrone(monkeypatch: pytest.MonkeyPatch) -> None:
    instants = iter([0.0, 1.0, 50.0])
    monkeypatch.setattr(relances, "_horloge", lambda: next(instants))

    class FluxAsync(httpx2.AsyncByteStream):
        async def __aiter__(self) -> Any:
            for morceau in (b"a", b"b"):
                yield morceau

    async def servir(requete: Any) -> Any:
        assert requete.extensions["timeout"]["connect"] == 4.0
        return httpx2.Response(200, stream=FluxAsync(), request=requete)

    async def envoyer() -> None:
        async with client(
            "outillage",
            asynchrone=True,
            journal=JournalMemoire(),
            transport_interne=httpx2.MockTransport(servir),
            delais_appel=DELAIS,
        ) as garde:
            await garde.post(URL)

    with pytest.raises(httpx2.ReadTimeout):
        asyncio.run(envoyer())


def test_sans_delais_appel_rien_ne_change() -> None:
    vus: list[Any] = []

    def servir(requete: Any) -> Any:
        vus.append(requete.extensions["timeout"]["read"])
        return _reponse(requete)

    with client(
        "outillage", journal=JournalMemoire(), transport_interne=httpx2.MockTransport(servir)
    ) as garde:
        garde.post(URL, timeout=12.0)
    assert vus == [12.0]


def test_echeance_globale_ramene_les_delais(monkeypatch: pytest.MonkeyPatch) -> None:
    """Dans `echeance_globale`, chaque délai est ramené au temps restant ; une échéance
    échue bloque la requête avant tout envoi."""
    monkeypatch.setattr(relances, "_horloge", lambda: 100.0)
    vus: list[Any] = []

    def servir(requete: Any) -> Any:
        vus.append(dict(requete.extensions["timeout"]))
        return _reponse(requete)

    with client(
        "outillage",
        journal=JournalMemoire(),
        transport_interne=httpx2.MockTransport(servir),
        delais_appel=DELAIS,
    ) as garde:
        with relances.echeance_globale(5.0):
            garde.post(URL)
        with relances.echeance_globale(0.0), pytest.raises(httpx2.ReadTimeout):
            garde.post(URL)
        garde.post(URL)
    assert vus == [
        {"connect": 4.0, "read": 5.0, "write": 5.0, "pool": 4.0},
        {"connect": 4.0, "read": 7.0, "write": 7.0, "pool": 4.0},
    ]
