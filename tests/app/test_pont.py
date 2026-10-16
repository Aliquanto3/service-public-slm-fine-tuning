"""Pont `js_api` (story 12.5) : fenêtre factice, LLM factice, aucun réseau."""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from harness_factices import FakeEmbedder, FakeLlm, FakeVectorStore, mots, script

from slmsp.app.pont import Pont
from slmsp.core.evenements import Fin, Jeton
from slmsp.harness.assemblage import assembler
from slmsp.net.journal import JournalMemoire

PREFIXE = "window.slmspRecevoir("


class FenetreFactice:
    """Port `Fenetre` : enregistre les lots poussés (JSON décodé)."""

    def __init__(self) -> None:
        self.scripts: list[str] = []
        self.fini = threading.Event()

    def evaluate_js(self, script: str) -> None:
        self.scripts.append(script)
        if self.evenements()[-1:] and self.evenements()[-1].get("type") in ("fin", "erreur"):
            self.fini.set()

    def evenements(self) -> list[dict[str, Any]]:
        sortie: list[dict[str, Any]] = []
        for code in self.scripts:
            assert code.startswith(PREFIXE) and code.endswith(")")
            sortie.extend(json.loads(code[len(PREFIXE) : -1]))
        return sortie


class LlmBloque(FakeLlm):
    """Joue un jeton, puis attend `libre` avant de continuer (génération longue)."""

    def __init__(self) -> None:
        super().__init__()
        self.premier, self.libre, self.ferme = (threading.Event() for _ in range(3))

    def _jouer(self, elements: list[Any]) -> Iterator[Any]:
        try:
            yield Jeton(texte="<jeton-factice-1>")
            self.premier.set()
            assert self.libre.wait(5)
            for i in range(1000):
                yield Jeton(texte=f"<jeton-factice-{i + 2}>")
            yield Fin(raison="terminee")
        except GeneratorExit:
            self.ferme.set()
            raise


@pytest.fixture
def banc() -> Iterator[Callable[[Any], tuple[Pont, FenetreFactice]]]:
    ouverts: list[Any] = []

    def fabrique(llm: Any) -> tuple[Pont, FenetreFactice]:
        contexte = assembler(
            "base:x",
            journal=JournalMemoire(),
            llm=llm,
            embedder=FakeEmbedder(),
            vector_store=FakeVectorStore(),
        )
        ouverts.append(contexte)
        fenetre = FenetreFactice()
        return Pont(contexte.__enter__().service, fenetre), fenetre

    yield fabrique
    for contexte in ouverts:
        contexte.__exit__(None, None, None)


def _user(texte: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": texte}]


def test_envoyer_pousse_le_flux_dans_l_ordre(banc: Any) -> None:
    texte = mots(10, "flux")
    pont, fenetre = banc(FakeLlm(script(texte)))
    assert pont.envoyer("Q", _user(mots(4, "q")), {}) == {"ok": True}
    assert fenetre.fini.wait(5)
    evenements = fenetre.evenements()
    assert evenements[-1]["type"] == "fin" and evenements[-1]["raison"] == "terminee"
    assert "".join(e["texte"] for e in evenements if e["type"] == "jeton") == texte
    assert [e["type"] for e in evenements].count("fin") == 1


def test_envoyer_rend_la_main_pendant_la_generation(banc: Any) -> None:
    llm = LlmBloque()
    pont, fenetre = banc(llm)
    assert pont.envoyer("Q", _user(mots(3, "a")), {}) == {"ok": True}
    assert llm.premier.wait(5)
    assert not fenetre.fini.is_set()
    llm.libre.set()
    pont.arreter()
    assert fenetre.fini.wait(5)


def test_arreter_ferme_l_iterateur_et_signale_interrompue(banc: Any) -> None:
    llm = LlmBloque()
    pont, fenetre = banc(llm)
    pont.envoyer("Q", _user(mots(3, "b")), {})
    assert llm.premier.wait(5)
    assert pont.arreter() == {"ok": True, "en_cours": True}
    llm.libre.set()
    assert fenetre.fini.wait(5)
    assert llm.ferme.wait(5)
    assert fenetre.evenements()[-1] == {
        "type": "fin",
        "raison": "interrompue",
        "usage": None,
        "urls_inventees": [],
    }
    # Le LLM (donc llama-server) reste réutilisable : une nouvelle génération démarre.
    pont._conversation.attendre(5)
    assert pont.arreter() == {"ok": True, "en_cours": False}
    assert pont.envoyer("Q", _user(mots(3, "c")), {}) == {"ok": True}
    pont.arreter()
    pont._conversation.attendre(5)
    assert len(llm.appels) == 2


def test_second_envoi_refuse_pendant_une_generation(banc: Any) -> None:
    llm = LlmBloque()
    pont, fenetre = banc(llm)
    pont.envoyer("Q", _user(mots(3, "d")), {})
    assert llm.premier.wait(5)
    refus = pont.envoyer("Q", _user(mots(3, "e")), {})
    assert refus["ok"] is False and refus["erreur"]["code"] == "generation-en-cours"
    json.dumps(refus)
    assert len(llm.appels) == 1
    llm.libre.set()
    pont.arreter()
    assert fenetre.fini.wait(5)


def test_refus_de_l_appelant_sans_le_texte_saisi(banc: Any) -> None:
    pont, fenetre = banc(FakeLlm())
    secret = "SECRET-" + mots(2, "s").replace(" ", "-")
    refus = pont.envoyer("TACHE-INCONNUE", _user(secret), {})
    assert refus["ok"] is False and secret not in json.dumps(refus)
    assert pont.envoyer("Q", [], {})["erreur"]["code"] == "requete-invalide"
    assert fenetre.scripts == []


def test_exception_du_harnais_pousse_erreur_sans_texte(
    banc: Any, caplog: pytest.LogCaptureFixture
) -> None:
    secret = "SECRET-" + mots(2, "x").replace(" ", "-")
    pont, fenetre = banc(FakeLlm([RuntimeError(f"boom {secret}")]))
    with caplog.at_level(logging.DEBUG):
        pont.envoyer("Q", _user(secret), {})
        assert fenetre.fini.wait(5)
    assert fenetre.evenements()[-1]["type"] == "erreur"
    assert secret not in json.dumps(fenetre.evenements())
    assert secret not in caplog.text


def test_echec_de_la_fenetre_ne_bloque_pas_le_pont(banc: Any) -> None:
    pont, _ = banc(FakeLlm(script(mots(4, "f"))))

    class Casse:
        def evaluate_js(self, script: str) -> None:
            raise OSError("fenêtre fermée")

    pont._fenetre = Casse()
    pont.envoyer("Q", _user(mots(2, "g")), {})
    pont._conversation.attendre(5)
    assert pont.arreter() == {"ok": True, "en_cours": False}


def test_regenerer_et_nouvelle_conversation(banc: Any) -> None:
    llm = FakeLlm(script(mots(3, "h")))
    pont, _ = banc(llm)
    assert pont.regenerer()["erreur"]["code"] == "rien-a-regenerer"
    pont.envoyer("Q", _user(mots(3, "i")), {})
    pont._conversation.attendre(5)
    assert pont.regenerer() == {"ok": True}
    pont._conversation.attendre(5)
    assert len(llm.appels) == 2 and llm.appels[0]["messages"] == llm.appels[1]["messages"]
    assert pont.nouvelle_conversation() == {"ok": True}
    assert pont.regenerer()["erreur"]["code"] == "rien-a-regenerer"


def test_signaler_pret_et_appeler(banc: Any) -> None:
    pont, fenetre = banc(FakeLlm(script(mots(2, "j"))))
    pont.signaler_pret()
    assert fenetre.evenements() == [{"type": "pret"}]
    assert pont.appeler("mode.etat")["erreur"]["code"] == "non-implementee"
    assert pont.appeler("verification.verifier", "<url>")["erreur"]["code"] == "non-implementee"
    assert pont.appeler("nimporte")["erreur"]["code"] == "methode-inconnue"
    assert pont.appeler("arreter") == {"ok": True, "en_cours": False}
    assert pont.appeler("envoyer")["erreur"]["code"] == "methode-inconnue"
