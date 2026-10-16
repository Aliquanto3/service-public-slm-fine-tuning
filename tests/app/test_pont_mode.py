"""Story 12.9 : domaine `mode` du pont (état, forçage persistant, journal, poussée)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice de la sonde)
import pytest

from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.mode import PontMode
from slmsp.app.stockage import JournalApplication, Stockage
from slmsp.core.erreurs import HoteBloque
from slmsp.harness.config import ConfigModes
from slmsp.harness.modes import ModeFixe, ModeSonde
from slmsp.net import client


class PortForcable:
    """Port de Mode factice : bascule entre connecté et hors ligne forcé."""

    def __init__(self, mode: str = "connecte") -> None:
        self.mode = mode
        self.force = False
        self.lectures = 0

    def mode_courant(self) -> str:
        self.lectures += 1
        return "hors-ligne-force" if self.force else self.mode

    def forcer(self, actif: bool) -> None:
        self.force = actif


@pytest.fixture
def stockage(tmp_path: Path) -> Stockage:
    return Stockage(tmp_path / "a.sqlite")


def _pont(port: Any, stockage: Stockage | None, lots: list[Any] | None = None) -> PontMode:
    return PontMode(port, stockage, (lambda lot: lots.extend(lot)) if lots is not None else None)


def test_etat_connecte_et_hors_ligne() -> None:
    port = PortForcable()
    pont = _pont(port, None)
    assert pont.etat() == {
        "ok": True,
        "mode": "connecte",
        "hors_ligne": False,
        "force": False,
        "detail": "connecte",
    }
    port.mode = "hors-ligne-detecte"
    etat = pont.appeler("etat")
    assert (etat["mode"], etat["hors_ligne"], etat["force"]) == ("hors_ligne", True, False)


def test_poussee_une_seule_fois_par_changement() -> None:
    port, lots = PortForcable(), []
    pont = _pont(port, None, lots)
    pont.etat()
    pont.etat()
    assert [e["mode"] for e in lots] == ["connecte"]
    port.mode = "hors-ligne-detecte"
    pont.rafraichir()
    pont.rafraichir()
    pont.forcer_hors_ligne(True)
    assert [(e["type"], e["mode"], e["force"]) for e in lots] == [
        ("mode", "connecte", False),
        ("mode", "hors_ligne", False),
        ("mode", "hors_ligne", True),
    ]
    assert lots[-1]["hors_ligne"] is True


def test_forcage_persiste_au_redemarrage(stockage: Stockage, tmp_path: Path) -> None:
    pont = _pont(PortForcable(), stockage)
    assert pont.forcer_hors_ligne(True)["detail"] == "hors-ligne-force"
    # Redémarrage : nouvelle base ouverte sur le même fichier, nouveau port.
    port2 = PortForcable()
    pont2 = _pont(port2, Stockage(tmp_path / "a.sqlite"))
    assert port2.force is True
    assert pont2.etat()["force"] is True
    assert pont2.forcer_hors_ligne(False)["detail"] == "connecte"
    assert Stockage(tmp_path / "a.sqlite").lire_reglage("hors_ligne_force") is False


def test_hors_ligne_force_aucune_requete_sonde_comprise(stockage: Stockage) -> None:
    vues: list[httpx2.Request] = []

    def espion(requete: httpx2.Request) -> httpx2.Response:
        vues.append(requete)
        return httpx2.Response(200, request=requete)

    port = ModeSonde(
        ConfigModes(periode_sonde_s=0.1, delai_sonde_s=1.5),
        journal=JournalApplication(stockage),
        transport_interne=httpx2.MockTransport(espion),
    )
    pont = _pont(port, stockage)
    pont.forcer_hors_ligne(True)
    for _ in range(3):
        assert pont.etat()["force"] is True
        port.sonder()
    assert vues == []


def test_journal_liste_et_efface(stockage: Stockage) -> None:
    port = ModeFixe("connecte")
    pont = _pont(port, stockage)
    assert pont.journal(None) == {"ok": True, "entrees": []}
    with client("assistant", mode=port, journal=JournalApplication(stockage)) as garde:
        with pytest.raises(HoteBloque):
            garde.get("https://hote-hors-liste.invalid/")
    entrees = pont.journal(10)["entrees"]
    assert len(entrees) == 1
    assert entrees[0]["statut"] == "bloquee-liste"
    assert entrees[0]["hote"] == "hote-hors-liste.invalid"
    assert set(entrees[0]) >= {"horodatage", "profil", "hote", "methode", "termes", "statut"}
    assert pont.effacer_journal() == {"ok": True}
    assert pont.journal(None)["entrees"] == []


def test_sans_stockage_journal_vide_et_methode_inconnue() -> None:
    pont = PontMode()
    assert pont.journal(None)["entrees"] == []
    assert pont.etat()["mode"] == "hors_ligne"
    assert pont.forcer_hors_ligne(True)["force"] is True
    with pytest.raises(NonImplementee):
        pont.appeler("inconnue")


def test_journal_retention_30_jours_glissants_avec_horloge_injectee(tmp_path: Path) -> None:
    from datetime import UTC, datetime, timedelta

    from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes

    maintenant = [datetime(2026, 10, 1, 12, 0, tzinfo=UTC)]
    stockage = Stockage(tmp_path / "r.sqlite", horloge=lambda: maintenant[0])
    journal = JournalApplication(stockage)

    def entree(hote: str, instant: datetime) -> EntreeJournalRequetes:
        return EntreeJournalRequetes(
            horodatage=instant,
            profil="assistant",
            hote=hote,
            methode="GET",
            statut="envoyee",
            mode="connecte",
        )

    journal.inscrire(entree("a.invalid", maintenant[0]))
    maintenant[0] += timedelta(days=29, hours=23)
    journal.inscrire(entree("b.invalid", maintenant[0]))
    pont = PontMode(ModeFixe("connecte"), stockage)
    assert [e["hote"] for e in pont.journal(None)["entrees"]] == ["b.invalid", "a.invalid"]
    # 30 jours + 1 h après a : filtré à la lecture, avant toute purge
    maintenant[0] += timedelta(hours=2)
    assert [e["hote"] for e in pont.journal(None)["entrees"]] == ["b.invalid"]
    assert [e.hote for e in journal.lister(1)] == ["b.invalid"]
    assert journal.purger() == 1  # la purge supprime physiquement la même entrée
