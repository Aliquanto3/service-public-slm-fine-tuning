"""Modes : `ModeSonde` (sonde `GET /health` par la passerelle) et `ModeFixe` (story 4.3).

La sonde passe par un transport factice (`httpx2.MockTransport`) et un `JournalMemoire` :
aucun réseau. La lenteur est simulée par une horloge injectée que le transport avance.
"""

from __future__ import annotations

import copy
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest

from slmsp.core.ports import ModePort
from slmsp.harness.config import ConfigModes
from slmsp.harness.modes import (
    MODES,
    ModeFixe,
    ModeSonde,
    ecarts_schema,
    mode_avant_appel,
    mode_courant,
)
from slmsp.mcp.cassettes import extraire_tools_list
from slmsp.mcp.outils import comparer_schema_serveur
from slmsp.net.journal import JournalMemoire

RACINE = Path(__file__).resolve().parents[2]
TOOLS_LIST = RACINE / "eval" / "calibrage" / "cassettes" / "tools-list.json"
URL_SONDE = "https://mcp.data.gouv.fr/health"


class Horloge:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


class Sonde:
    """Transport factice de la sonde : statut, exception ou lenteur (horloge avancée)."""

    def __init__(
        self,
        horloge: Horloge,
        statut: int = 200,
        erreur: type[Exception] | None = None,
        duree: float = 0.0,
    ) -> None:
        self.horloge = horloge
        self.statut = statut
        self.erreur = erreur
        self.duree = duree
        self.vues: list[httpx2.Request] = []

    def repondre(self, requete: httpx2.Request) -> httpx2.Response:
        self.vues.append(requete)
        self.horloge.t += self.duree
        if self.erreur is not None:
            if issubclass(self.erreur, httpx2.RequestError):
                raise self.erreur("<panne-factice>", request=requete)
            raise self.erreur("<panne-factice>")
        return httpx2.Response(self.statut, request=requete)

    def transport(self) -> httpx2.MockTransport:
        return httpx2.MockTransport(self.repondre)


@pytest.fixture
def config_modes() -> ConfigModes:
    return ConfigModes(periode_sonde_s=300.0, delai_sonde_s=1.5)


def fabriquer(
    config: ConfigModes, *, controle: Callable[[], Any] | None = None, **sonde: Any
) -> tuple[ModeSonde, Sonde, Horloge, JournalMemoire]:
    horloge = Horloge()
    factice = Sonde(horloge, **sonde)
    journal = JournalMemoire()
    port = ModeSonde(
        config,
        controle_schema=controle,
        journal=journal,
        transport_interne=factice.transport(),
        horloge=horloge,
    )
    return port, factice, horloge, journal


# --- Sonde ---------------------------------------------------------------------------------


def test_sonde_joignable(config_modes: ConfigModes) -> None:
    port, sonde, _, journal = fabriquer(config_modes)
    assert isinstance(port, ModePort)
    assert port.mode_courant() == "connecte"
    (requete,) = sonde.vues
    assert (requete.method, str(requete.url)) == ("GET", URL_SONDE)
    assert requete.extensions["timeout"]["read"] == config_modes.delai_sonde_s
    assert [e.statut for e in journal.lister()] == ["envoyee"]
    assert port.ecarts_schema == ()


@pytest.mark.parametrize(
    "sonde",
    [
        {"statut": 503},
        {"erreur": httpx2.ConnectError},
        {"erreur": httpx2.ConnectTimeout},
        {"erreur": RuntimeError},
        {"duree": 1.6},
    ],
    ids=["503", "connexion", "delai-transport", "exception", "lente"],
)
def test_sonde_en_panne(config_modes: ConfigModes, sonde: dict[str, Any]) -> None:
    port, factice, _, _ = fabriquer(config_modes, **sonde)
    assert port.mode_courant() == "hors-ligne-detecte"
    assert len(factice.vues) == 1


def test_sonde_au_delai_exact(config_modes: ConfigModes) -> None:
    port, _, _, _ = fabriquer(config_modes, duree=config_modes.delai_sonde_s)
    assert port.mode_courant() == "connecte"


def test_periode_de_sonde(config_modes: ConfigModes) -> None:
    port, sonde, horloge, _ = fabriquer(config_modes)
    assert port.mode_courant() == "connecte"
    horloge.t += config_modes.periode_sonde_s - 1
    assert port.mode_courant() == "connecte"
    assert len(sonde.vues) == 1  # pas de nouvelle sonde avant la période
    sonde.statut = 503
    horloge.t += 1
    assert port.mode_courant() == "hors-ligne-detecte"
    assert len(sonde.vues) == 2
    sonde.statut = 200
    assert port.sonder() == "connecte"  # sonde à la demande (avant un appel d'outil)
    assert port.sonder() == "connecte"
    assert len(sonde.vues) == 4


def test_hors_ligne_force_sans_requete(config_modes: ConfigModes) -> None:
    horloge = Horloge()
    sonde = Sonde(horloge)
    port = ModeSonde(
        config_modes,
        hors_ligne_force=True,
        journal=JournalMemoire(),
        transport_interne=sonde.transport(),
        horloge=horloge,
    )
    assert port.mode_courant() == "hors-ligne-force"
    assert port.sonder() == "hors-ligne-force"
    horloge.t += 10 * config_modes.periode_sonde_s
    assert port.mode_courant() == "hors-ligne-force"
    assert sonde.vues == []
    assert port.forcer(False) == "hors-ligne-detecte"
    assert port.mode_courant() == "connecte"
    assert len(sonde.vues) == 1
    assert port.forcer(True) == "hors-ligne-force"
    assert port.sonder() == "hors-ligne-force"
    assert len(sonde.vues) == 1


# --- Contrôle de schéma ----------------------------------------------------------------------


def _tools_calibrage() -> list[dict[str, Any]]:
    return extraire_tools_list(json.loads(TOOLS_LIST.read_text(encoding="utf-8")))


def _sans(nom: str) -> list[dict[str, Any]]:
    return [outil for outil in _tools_calibrage() if outil["name"] != nom]


def _schema_change(nom: str) -> list[dict[str, Any]]:
    tools = copy.deepcopy(_tools_calibrage())
    for outil in tools:
        if outil["name"] == nom:
            outil["inputSchema"]["properties"]["champ_factice"] = {"type": "string"}
    return tools


def _avec_inconnu() -> list[dict[str, Any]]:
    inconnu = {"name": "outil_factice", "inputSchema": {"type": "object"}}
    return [*_tools_calibrage(), inconnu]


@pytest.mark.parametrize(
    ("tools", "ecarts"),
    [
        (_tools_calibrage, ()),
        (_avec_inconnu, ()),
        (lambda: _sans("get_resource_info"), ("get_resource_info : absent du serveur",)),
        (
            lambda: _schema_change("search_datasets"),
            ("search_datasets : schéma modifié",),
        ),
    ],
    ids=["conforme", "outil-inconnu-ignore", "outil-retire", "schema-change"],
)
def test_controle_de_schema(
    config_modes: ConfigModes,
    caplog: pytest.LogCaptureFixture,
    tools: Callable[[], list[dict[str, Any]]],
    ecarts: tuple[str, ...],
) -> None:
    appels: list[int] = []

    def controle() -> None:
        appels.append(1)
        comparer_schema_serveur(tools())

    port, _, _, _ = fabriquer(config_modes, controle=controle)
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        assert port.mode_courant() == "connecte"
    assert port.ecarts_schema == ecarts
    assert ecarts_schema(port) == ecarts
    alertes = [r for r in caplog.records if r.name == "slmsp.harness"]
    if ecarts:
        (alerte,) = alertes
        assert alerte.levelno == logging.WARNING and ecarts[0] in alerte.getMessage()
    else:
        assert alertes == []
    port.sonder()
    assert appels == [1]  # contrôle seulement au passage en connecté


def test_controle_en_doute_reste_hors_ligne(config_modes: ConfigModes) -> None:
    def controle() -> None:
        raise RuntimeError("<panne-factice>")

    port, _, _, _ = fabriquer(config_modes, controle=controle)
    assert port.mode_courant() == "hors-ligne-detecte"
    assert port.ecarts_schema == ()


def test_controle_repris_a_chaque_passage_en_connecte(config_modes: ConfigModes) -> None:
    appels: list[int] = []
    port, sonde, _, _ = fabriquer(config_modes, controle=lambda: appels.append(1))
    assert port.sonder() == "connecte"
    sonde.statut = 503
    assert port.sonder() == "hors-ligne-detecte"
    sonde.statut = 200
    assert port.sonder() == "connecte"
    assert appels == [1, 1]


# --- ModeFixe et lecteurs ------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
def test_mode_fixe(mode: str) -> None:
    port = ModeFixe(mode)
    assert isinstance(port, ModePort)
    assert port.mode_courant() == port.sonder() == mode


def test_mode_fixe_inconnu() -> None:
    with pytest.raises(ValueError, match="Mode inconnu"):
        ModeFixe("en-ligne")


class _SansSonde:
    def __init__(self, mode: Any) -> None:
        self.mode = mode
        self.lectures = 0

    def mode_courant(self) -> Any:
        self.lectures += 1
        if isinstance(self.mode, Exception):
            raise self.mode
        return self.mode


class _AvecSonde(_SansSonde):
    def __init__(self, mode: Any, sonde: Any) -> None:
        super().__init__(mode)
        self.sonde = sonde
        self.sondes = 0

    def sonder(self) -> Any:
        self.sondes += 1
        if isinstance(self.sonde, Exception):
            raise self.sonde
        return self.sonde


def test_mode_avant_appel() -> None:
    assert mode_avant_appel(None) == "hors-ligne-detecte"
    sans = _SansSonde("connecte")
    assert mode_avant_appel(sans) == "connecte" and sans.lectures == 1
    avec = _AvecSonde("connecte", "hors-ligne-detecte")
    assert mode_avant_appel(avec) == "hors-ligne-detecte"
    assert (avec.sondes, avec.lectures) == (1, 0)
    assert mode_avant_appel(_AvecSonde("connecte", RuntimeError("x"))) == "hors-ligne-detecte"
    assert mode_avant_appel(_AvecSonde("connecte", "inconnu")) == "hors-ligne-detecte"


def test_mode_courant_garde() -> None:
    assert mode_courant(None) == "hors-ligne-detecte"
    assert mode_courant(_SansSonde(RuntimeError("x"))) == "hors-ligne-detecte"
    assert mode_courant(_SansSonde("inconnu")) == "hors-ligne-detecte"
    assert mode_courant(_SansSonde("hors-ligne-force")) == "hors-ligne-force"


def test_ecarts_schema_lecteur() -> None:
    assert ecarts_schema(None) == ()
    assert ecarts_schema(ModeFixe("connecte")) == ()
    port = _SansSonde("connecte")
    port.ecarts_schema = ["a : absent du serveur"]  # type: ignore[attr-defined]
    assert ecarts_schema(port) == ("a : absent du serveur",)
