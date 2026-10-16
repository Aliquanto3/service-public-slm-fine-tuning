"""Document témoin (FR-38) par le pont : aucune Requête sortante, marqueur absent du journal."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transport interne espion)
import pytest
from harness_factices import FakeEmbedder, FakeLlm, FakeVectorStore, mots, script

from slmsp.app.pont import Pont
from slmsp.app.stockage import JournalApplication, Stockage
from slmsp.harness.assemblage import assembler
from slmsp.harness.taches import charger_taches

TACHES_REDACTION = ("CR", "LC", "CO", "RE", "CT", "NR", "TR")


class Espion:
    def __init__(self) -> None:
        self.requetes: list[Any] = []

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        return httpx2.Response(200, json={})


class Fenetre:
    def __init__(self) -> None:
        self.fini = threading.Event()
        self.codes: list[str] = []

    def evaluate_js(self, script: str) -> None:
        self.codes.append(script)
        if '"type": "fin"' in script or '"type": "erreur"' in script:
            self.fini.set()


@pytest.mark.parametrize("code", TACHES_REDACTION)
def test_document_temoin_par_le_pont(code: str, tmp_path: Path) -> None:
    marqueur = "MARQUEUR-" + mots(2, f"m-{code}").replace(" ", "-")
    document = f"{mots(8, 'a')} {marqueur} {mots(8, 'b')}"
    base = tmp_path / "app.sqlite"
    journal, espion, fenetre = JournalApplication(Stockage(base)), Espion(), Fenetre()
    options = None
    if code == "TR":
        options = {"entree": {"texte": document, "langue_source": "fr", "langue_cible": "en"}}
    with assembler(
        "base:x",
        charger_taches().tache(code),
        journal=journal,
        transport_interne=httpx2.MockTransport(espion),
        llm=FakeLlm(script(mots(6, "sortie"))),
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(),
    ) as a:
        pont = Pont(a.service, fenetre)
        assert pont.envoyer(code, [{"role": "user", "content": document}], options) == {"ok": True}
        assert fenetre.fini.wait(5)
    assert '"type": "fin"' in fenetre.codes[-1]
    assert espion.requetes == []
    assert journal.lister() == []
    assert marqueur.encode() not in base.read_bytes()
