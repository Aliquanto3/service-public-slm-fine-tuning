"""Document témoin (FR-38, story 4.5) : un texte collé ne quitte jamais le poste.

Assemblage réel par `slmsp.cli._assemblage.assembler` avec ports factices, vrai `ModeSonde`
et `Passerelle` (vrai `NetGate`), transport interne espion. Critères 4 et 5 : aucune
Requête sortante pour les Tâches de rédaction ; pour RD en Mode connecté, le journal ne
porte que les arguments d'outil, jamais la phrase de l'Agent. Textes : mots aléatoires.
"""

from __future__ import annotations

import json
from typing import Any

import httpx2  # noqa: TID251 (tests : transport interne espion)
import pytest
from harness_factices import FakeEmbedder, FakeLlm, FakeVectorStore, mots, script

from slmsp.cli._assemblage import assembler
from slmsp.core.evenements import AppelOutil, Fin, ResultatOutil
from slmsp.harness.taches import charger_taches
from slmsp.net.journal import JournalMemoire

TACHES_REDACTION = ("CR", "LC", "CO", "RE", "CT", "NR", "TR")


class Espion:
    """Transport interne : compte les requêtes ; répond 200 (JSON-RPC factice)."""

    def __init__(self) -> None:
        self.requetes: list[Any] = []

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        contenu = [{"type": "text", "text": mots(6, "resultat-outil")}]
        return httpx2.Response(
            200, json={"jsonrpc": "2.0", "id": 1, "result": {"content": contenu}}
        )


class OutilsViaPasserelle:
    """`ToolPort` de test : l'appel passe par le vrai `NetGate`, comme `McpEnDirect`."""

    def __init__(self, passerelle: Any, transport: Any) -> None:
        self.passerelle, self.transport = passerelle, transport

    def lister_outils(self) -> list[dict[str, Any]]:
        from slmsp.mcp.outils import charger_outils

        return charger_outils()

    def appeler(self, nom: str, arguments: Any) -> dict[str, Any]:
        corps = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": nom, "arguments": dict(arguments)},
        }
        with self.passerelle.client("assistant", transport_interne=self.transport) as http:
            return http.post("https://mcp.data.gouv.fr/mcp", json=corps).json()


@pytest.mark.parametrize("code", TACHES_REDACTION)
def test_document_temoin_aucune_requete_sortante(code: str) -> None:
    marqueur = "MARQUEUR-" + mots(2, f"m-{code}").replace(" ", "-")
    document = f"{mots(8, 'a')} {marqueur} {mots(8, 'b')}"
    espion, journal = Espion(), JournalMemoire()
    llm = FakeLlm(script(mots(6, "sortie")))
    options = None
    if code == "TR":
        options = {"entree": {"texte": document, "langue_source": "fr", "langue_cible": "en"}}
    with assembler(
        "base:x",
        charger_taches().tache(code),
        journal=journal,
        transport_interne=httpx2.MockTransport(espion),
        llm=llm,
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    ) as a:
        evenements = list(
            a.service.repondre(code, [{"role": "user", "content": document}], options)
        )
    assert isinstance(evenements[-1], Fin), evenements[-1]
    assert marqueur in json.dumps(llm.appels[0]["messages"], ensure_ascii=False)
    assert espion.requetes == []
    assert journal.lister() == []


def test_rd_connecte_journalise_les_termes_jamais_la_phrase() -> None:
    phrase = "PHRASE-" + mots(3, "agent").replace(" ", "-")
    termes = mots(2, "termes")
    espion, journal = Espion(), JournalMemoire()
    appel = AppelOutil(id="c1", nom="search_datasets", arguments={"query": termes})
    llm = FakeLlm(
        [appel, Fin(raison="terminee", usage={"prompt_tokens": 1, "completion_tokens": 1})],
        script(mots(5, "finale")),
    )
    transport = httpx2.MockTransport(espion)
    with assembler(
        "base:x",
        charger_taches().tache("RD"),
        journal=journal,
        transport_interne=transport,
        llm=llm,
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    ) as a:
        a.service.outils = OutilsViaPasserelle(a.passerelle, transport)
        evenements = list(
            a.service.repondre("RD", [{"role": "user", "content": f"{phrase} {mots(4, 'z')}"}])
        )
    assert any(isinstance(e, ResultatOutil) and not e.erreur for e in evenements), evenements
    entrees = journal.lister()
    appels = [e for e in entrees if e.outil == "search_datasets"]
    assert len(appels) == 1 and json.loads(appels[0].termes) == {"query": termes}
    assert all(phrase not in repr(e) for e in entrees)
    assert {e.hote for e in entrees} == {"mcp.data.gouv.fr"}
