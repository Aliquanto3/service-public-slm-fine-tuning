"""Repli sur l'Index local (FR-9) : pannes MCP, hôte bloqué, Mode perdu, schéma dérivé.

Les pannes simulées viennent de cassettes écrites dans `tmp_path` (format du Bac à sable) ;
les cassettes du calibrage et du jeu gelé ne sont jamais modifiées.
"""

from __future__ import annotations

import dataclasses
import logging
import threading
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest
from harness_factices import (
    USAGE,
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyToolPort,
    mots,
    passage,
    script,
)

from slmsp.core.erreurs import HoteBloque, SchemaOutilModifie
from slmsp.core.evenements import AppelOutil, Erreur, Fin, Repli, ResultatOutil
from slmsp.core.schemas.cassette import Cassette, Interaction, Simulation
from slmsp.harness.config import ConfigOutils, charger_config_harnais
from slmsp.harness.modes import ModeFixe, ModeSonde
from slmsp.harness.prompts import ENTETE_PASSAGES
from slmsp.harness.service import AssistantService
from slmsp.harness.taches.recherche import (
    CODE_AVERTISSEMENT,
    FACTEUR_RECHERCHE,
    MOTIF_MODE_PERDU,
    MOTIF_PANNE,
    MOTIF_SCHEMA,
    SOURCE_CATALOGUE,
)
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.cassettes import ecrire_cassette
from slmsp.mcp.erreurs import ErreurHttp, Injoignable
from slmsp.mcp.outils import charger_config
from slmsp.net.journal import JournalMemoire

NON_VERIFIE = "non vérifié en ligne"


def config_k() -> int:
    return charger_config_harnais().recherche.k


def cassette_panne(tmp_path: Path, simulation: Simulation, arguments: dict[str, Any]) -> Path:
    cassette = Cassette(
        schema_version=1,
        server="http://serveur-factice.invalid/mcp",
        recorded_at=datetime(2026, 10, 12, 5, 0, tzinfo=UTC),
        initialize={"jsonrpc": "2.0", "id": 1, "result": {}},
        tools_list_sha256=charger_config().tools_list_sha256,
        interactions=[
            Interaction(
                request={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "search_datasets", "arguments": arguments},
                },
                response=None,
                simulation=simulation,
            )
        ],
    )
    return ecrire_cassette(cassette, tmp_path / "panne.json")


class Enregistreur:
    def __init__(self, interne: Any = None, erreur: BaseException | None = None) -> None:
        self.interne = interne
        self.erreur = erreur
        self.appels: list[tuple[str, dict[str, Any]]] = []

    def lister_outils(self) -> list[dict[str, Any]]:
        from slmsp.mcp.outils import charger_outils

        return charger_outils()

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        self.appels.append((nom, dict(arguments)))
        if self.erreur is not None:
            raise self.erreur
        return self.interne.appeler(nom, arguments)


class Bloquant(Enregistreur):
    """`ToolPort` dont l'appel ne rend pas la main avant `liberer`."""

    def __init__(self) -> None:
        super().__init__()
        self.liberer = threading.Event()

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        self.appels.append((nom, dict(arguments)))
        self.liberer.wait(10)
        return {"jsonrpc": "2.0", "id": 3, "result": {"content": []}}


class ModePerdu:
    """Connecté à la lecture, hors ligne à la sonde d'avant appel."""

    def __init__(self) -> None:
        self.sondes = 0

    def mode_courant(self) -> str:
        return "connecte"

    def sonder(self) -> str:
        self.sondes += 1
        return "hors-ligne-detecte"


def repondre(table, config, llm, outils, mode, *, demande=None, passages=None):
    seuil = config.recherche.seuil_pertinence
    if passages is None:
        passages = [dataclasses.replace(passage(1, seuil + 0.2), source=SOURCE_CATALOGUE)]
    store = FakeVectorStore(passages)
    llm.store = store  # consulté par `verifier_repli`
    instance = AssistantService(llm, FakeEmbedder(), store, outils, mode, config, taches=table)
    demande = demande if demande is not None else mots(6, "demande")
    return list(instance.repondre("RD", [{"role": "user", "content": demande}])), passages


def tour(*appels: AppelOutil) -> list[Any]:
    return [*appels, Fin(raison="terminee", usage=dict(USAGE))]


ARGUMENTS = {"query": "<requete-factice>"}


def verifier_repli(evenements, llm, motif: str, *, appels: int = 1) -> None:
    noms = [type(e).__name__ for e in evenements if type(e).__name__ != "Jeton"]
    attendu = ["AppelOutil"] * appels + ["ResultatOutil", "Repli"]
    attendu += ["ResultatOutil"] * (appels - 1) + ["Sources", "Avertissement", "Fin"]
    assert noms == attendu
    resultats = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert all(r.erreur and r.resultat is None for r in resultats)
    (repli,) = [e for e in evenements if isinstance(e, Repli)]
    assert repli == Repli(motif=motif, vers="index") and NON_VERIFIE in repli.motif
    assert [a["tools"] is None for a in llm.appels] == [False, True]  # plus aucun outil
    # Premier tour connecté : la demande seule, sans recherche dans l'Index.
    premier, dernier = llm.appels
    systeme, user = premier["messages"]
    assert systeme["role"] == "system" and user["role"] == "user"
    assert ENTETE_PASSAGES not in user["content"]
    # Repli : messages reconstruits avec les passages du catalogue, sans tour d'outil.
    passages = llm.store.passages
    assert llm.store.appels == [config_k() * FACTEUR_RECHERCHE]
    assert [m["role"] for m in dernier["messages"]] == ["system", "user"]
    assert dernier["messages"][0] == systeme
    assert all(p.url in dernier["messages"][1]["content"] for p in passages)
    assert user["content"] in dernier["messages"][1]["content"]
    alerte = evenements[-2]
    assert alerte.code == CODE_AVERTISSEMENT
    sources = evenements[-3].sources
    assert [s.url for s in sources] == [p.url for p in passages]
    assert all(s.origine == "index" for s in sources)
    assert isinstance(evenements[-1], Fin)


@pytest.mark.parametrize(
    "simulation",
    [
        Simulation(type="delai_depasse"),
        Simulation(type="erreur_http", statut=503),
        Simulation(type="injoignable"),
    ],
    ids=["delai_depasse", "erreur_http", "injoignable"],
)
def test_panne_simulee(
    tmp_path: Path, table, config_harnais, caplog: pytest.LogCaptureFixture, simulation
) -> None:
    outils = Enregistreur(BacASable([cassette_panne(tmp_path, simulation, ARGUMENTS)]))
    llm = FakeLlm(tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)))
    llm.scripts.append(script(mots(5, "r")))
    demande = mots(8, "saisie-confidentielle")
    with caplog.at_level(logging.INFO, logger="slmsp.harness"):
        evenements, _ = repondre(
            table, config_harnais, llm, outils, ModeFixe("connecte"), demande=demande
        )
    verifier_repli(evenements, llm, MOTIF_PANNE)
    assert outils.appels == [("search_datasets", ARGUMENTS)]
    journal = "\n".join(r.getMessage() for r in caplog.records if r.name == "slmsp.harness")
    classes = {"delai_depasse": "DelaiDepasse", "erreur_http": "ErreurHttp"}
    assert classes.get(simulation.type, "Injoignable") in journal
    assert demande not in journal


@pytest.mark.parametrize(
    "erreur",
    [
        HoteBloque("<hote-factice>"),
        SchemaOutilModifie("<schema-factice>"),
        ErreurHttp("<http-factice>", statut=500),
    ],
    ids=["hote-bloque", "schema-modifie", "erreur-http"],
)
def test_panne_du_port(table, config_harnais, erreur) -> None:
    outils = Enregistreur(erreur=erreur)
    llm = FakeLlm(tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)))
    llm.scripts.append(script(mots(5, "r")))
    evenements, _ = repondre(table, config_harnais, llm, outils, ModeFixe("connecte"))
    verifier_repli(evenements, llm, MOTIF_PANNE)


def test_log_sans_texte_saisi(table, config_harnais, caplog: pytest.LogCaptureFixture) -> None:
    demande = mots(8, "confidentiel")
    outils = Enregistreur(erreur=Injoignable(f"<panne> {demande}"))
    llm = FakeLlm(tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)))
    llm.scripts.append(script(mots(5, "r")))
    with caplog.at_level(logging.INFO, logger="slmsp.harness"):
        evenements, _ = repondre(
            table, config_harnais, llm, outils, ModeFixe("connecte"), demande=demande
        )
    journal = "\n".join(r.getMessage() for r in caplog.records)
    assert "Injoignable" in journal
    assert demande not in journal
    assert not any(isinstance(e, Erreur) for e in evenements)


def test_delai_d_appel_depasse(table, config_harnais) -> None:
    config = config_harnais.model_copy(
        update={"outils": ConfigOutils(iterations_max=5, delai_appel_s=0.05)}
    )
    outils = Bloquant()
    llm = FakeLlm(tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)))
    llm.scripts.append(script(mots(5, "r")))
    try:
        evenements, _ = repondre(table, config, llm, outils, ModeFixe("connecte"))
    finally:
        outils.liberer.set()
    verifier_repli(evenements, llm, MOTIF_PANNE)


def test_appels_suivants_non_envoyes_apres_repli(tmp_path: Path, table, config_harnais) -> None:
    panne = cassette_panne(tmp_path, Simulation(type="injoignable"), ARGUMENTS)
    outils = Enregistreur(BacASable([panne]))
    llm = FakeLlm(
        tour(
            AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS),
            AppelOutil(id="c2", nom="get_dataset_info", arguments={"dataset_id": "<d>"}),
        ),
        script(mots(4, "r")),
    )
    evenements, _ = repondre(table, config_harnais, llm, outils, ModeFixe("connecte"))
    verifier_repli(evenements, llm, MOTIF_PANNE, appels=2)
    assert outils.appels == [("search_datasets", ARGUMENTS)]


def test_mode_perdu_avant_appel(table, config_harnais) -> None:
    outils = Enregistreur(erreur=AssertionError("ne doit pas être appelé"))
    mode = ModePerdu()
    llm = FakeLlm(
        tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)),
        script(mots(4, "r")),
    )
    evenements, _ = repondre(table, config_harnais, llm, outils, mode)
    verifier_repli(evenements, llm, MOTIF_MODE_PERDU)
    assert outils.appels == [] and mode.sondes == 1


def test_mode_perdu_par_la_sonde(table, config_harnais) -> None:
    """`ModeSonde` réel : la sonde d'avant appel échoue (503), l'appel n'est pas envoyé."""
    statuts = [200, 503]

    def repondre_sonde(requete: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(statuts.pop(0), request=requete)

    journal = JournalMemoire()
    mode = ModeSonde(
        config_harnais.modes,
        journal=journal,
        transport_interne=httpx2.MockTransport(repondre_sonde),
    )
    outils = Enregistreur(erreur=AssertionError("ne doit pas être appelé"))
    llm = FakeLlm(
        tour(AppelOutil(id="c1", nom="search_datasets", arguments=ARGUMENTS)),
        script(mots(4, "r")),
    )
    evenements, _ = repondre(table, config_harnais, llm, outils, mode)
    verifier_repli(evenements, llm, MOTIF_MODE_PERDU)
    assert outils.appels == [] and statuts == []
    assert len(journal.lister()) == 2  # deux sondes, aucune autre requête


def test_schema_derive(table, config_harnais, caplog: pytest.LogCaptureFixture) -> None:
    def controle() -> None:
        erreur = SchemaOutilModifie("<ecart>")
        erreur.ecarts = ("search_datasets : schéma modifié",)  # type: ignore[attr-defined]
        raise erreur

    mode = ModeSonde(
        config_harnais.modes,
        controle_schema=controle,
        journal=JournalMemoire(),
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(200, request=r)),
    )
    espion = SpyToolPort()
    llm = FakeLlm(script(mots(6, "s")))
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        evenements, passages = repondre(table, config_harnais, llm, espion, mode)

    noms = [type(e).__name__ for e in evenements if type(e).__name__ != "Jeton"]
    assert noms == ["Repli", "Sources", "Avertissement", "Fin"]
    assert evenements[0] == Repli(motif=MOTIF_SCHEMA, vers="index")
    assert NON_VERIFIE in MOTIF_SCHEMA
    assert llm.appels[0]["tools"] is None
    assert espion.appels == []
    assert [s.url for s in evenements[-3].sources] == [p.url for p in passages]
    alertes = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert alertes and all("search_datasets : schéma modifié" in r.getMessage() for r in alertes)
