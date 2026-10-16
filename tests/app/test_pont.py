"""Pont `js_api` (story 12.5) : fenêtre factice, LLM factice, aucun réseau."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from harness_factices import FakeEmbedder, FakeLlm, FakeVectorStore, mots, script

from slmsp.app.pont import Pont
from slmsp.app.pont.reglages import PontReglages
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
    assert pont.appeler("mode.inconnue")["erreur"]["code"] == "non-implementee"
    assert pont.appeler("verification.verifier", "<url>")["erreur"]["code"] == "non-implementee"
    assert pont.appeler("nimporte")["erreur"]["code"] == "methode-inconnue"
    assert pont.appeler("arreter") == {"ok": True, "en_cours": False}
    assert pont.appeler("envoyer")["erreur"]["code"] == "methode-inconnue"


class LlmSilencieux(FakeLlm):
    """Ne rend aucun jeton tant que `libre` n'est pas levé (LLM bloqué avant le premier jeton)."""

    def __init__(self) -> None:
        super().__init__()
        self.entre, self.libre, self.ferme = (threading.Event() for _ in range(3))

    def _jouer(self, elements: list[Any]) -> Iterator[Any]:
        try:
            self.entre.set()
            assert self.libre.wait(10)
            yield Jeton(texte="<tardif>")
            yield Fin(raison="terminee")
        except GeneratorExit:
            self.ferme.set()
            raise


def test_arreter_sans_aucun_jeton_est_immediat(banc: Any) -> None:
    llm = LlmSilencieux()
    pont, fenetre = banc(llm)
    assert pont.envoyer("Q", _user(mots(3, "s")), {}) == {"ok": True}
    assert llm.entre.wait(5)
    assert pont.arreter() == {"ok": True, "en_cours": True}
    assert [e["type"] for e in fenetre.evenements()] == ["fin"]
    assert fenetre.evenements()[0]["raison"] == "interrompue"
    # L'état est libre sans attendre le fil : un nouvel envoi est accepté, puis arrêté de même.
    assert pont.envoyer("Q", _user(mots(3, "t")), {}) == {"ok": True}
    assert pont.arreter() == {"ok": True, "en_cours": True}
    llm.libre.set()  # les deux fils se réveillent : leurs évènements tardifs sont ignorés
    assert llm.ferme.wait(5)
    pont._conversation.attendre(5)
    time.sleep(0.1)
    assert [(e["type"], e.get("raison")) for e in fenetre.evenements()] == [
        ("fin", "interrompue")
    ] * 2


def test_etat_libre_des_que_fin_est_poussee(banc: Any) -> None:
    pont, fenetre = banc(FakeLlm(script(mots(4, "l"))))

    pont.envoyer("Q", _user(mots(2, "n")), {})
    assert fenetre.fini.wait(5)
    # Sans attendre la fin du fil : `Fin` est déjà poussé, l'état est libre.
    assert pont.envoyer("Q", _user(mots(2, "m")), {}) == {"ok": True}
    pont._conversation.attendre(5)


class LlmRafale(FakeLlm):
    def __init__(self, n: int, pause: float = 0.0) -> None:
        super().__init__()
        self.n, self.pause = n, pause

    def _jouer(self, elements: list[Any]) -> Iterator[Any]:
        for i in range(self.n):
            yield Jeton(texte=f"j{i} ")
            if self.pause:
                time.sleep(self.pause)
        yield Fin(raison="terminee")


def _jetons_par_lot(fenetre: FenetreFactice) -> list[int]:
    lots = [json.loads(c[len(PREFIXE) : -1]) for c in fenetre.scripts]
    return [n for n in (sum(e["type"] == "jeton" for e in lot) for lot in lots) if n]


def test_lotissement_par_16_jetons(banc: Any) -> None:
    pont, fenetre = banc(LlmRafale(40))
    pont.envoyer("Q", _user(mots(2, "o")), {})
    assert fenetre.fini.wait(5)
    tailles = _jetons_par_lot(fenetre)
    assert tailles[:2] == [16, 16] and sum(tailles) == 40 and max(tailles) <= 16


def test_lotissement_par_delai(banc: Any) -> None:
    pont, fenetre = banc(LlmRafale(6, pause=0.03))
    pont.envoyer("Q", _user(mots(2, "p")), {})
    assert fenetre.fini.wait(5)
    tailles = _jetons_par_lot(fenetre)
    assert sum(tailles) == 6 and len(tailles) > 1 and max(tailles) < 16


def test_injection_dans_le_script_poussee(banc: Any) -> None:
    piege = "a\"b\\c\u2028d\u2029</script><img onerror=x>';alert(1)//"

    class LlmPiege(FakeLlm):
        def _jouer(self, elements: list[Any]) -> Iterator[Any]:
            yield Jeton(texte=piege)
            yield Fin(raison="terminee")

    pont, fenetre = banc(LlmPiege())
    pont.envoyer("Q", _user(mots(2, "q")), {})
    assert fenetre.fini.wait(5)
    for code in fenetre.scripts:
        assert "\u2028" not in code and "\u2029" not in code and "\n" not in code
    jetons = [e["texte"] for e in fenetre.evenements() if e["type"] == "jeton"]
    assert jetons == [piege]


def test_refus_masque_aussi_l_entree_des_options(banc: Any) -> None:
    secret = "SECRET-" + mots(3, "e").replace(" ", "-")
    pont, _ = banc(FakeLlm(script(mots(4, "r"))))
    reponse = pont.envoyer("TR", _user(mots(2, "u")), {"entree": {"texte": secret}})
    if not reponse["ok"]:
        assert secret not in json.dumps(reponse)


def test_appeler_ne_masque_pas_les_typeerror_internes(banc: Any) -> None:
    pont, _ = banc(FakeLlm(script(mots(4, "v"))))
    assert pont.appeler("envoyer")["erreur"]["code"] == "methode-inconnue"

    def casse() -> None:
        raise TypeError("interne")

    pont.arreter = casse  # type: ignore[method-assign]
    assert pont.appeler("arreter")["erreur"]["code"] == "erreur-interne"


@pytest.mark.parametrize(
    "url",
    [
        "http://www.service-public.fr/particuliers",  # pas https
        "https://exemple.invalid/page",  # hôte hors Liste blanche
        "https://www.service-public.fr.exemple.invalid/",  # suffixe trompeur
        "https://www.service-public.fr:8443/",  # port
        "https://utilisateur:secret@www.service-public.fr/",  # identifiants
        "https://203.0.113.7/",  # adresse IP
        "javascript:alert(1)",
        "file:///C:/Windows/win.ini",
        "",
        "pas une url",
    ],
)
def test_ouvrir_lien_refuse_hors_liste_blanche(banc: Any, url: str) -> None:
    pont, fenetre = banc(FakeLlm(script(mots(1, "j"))))
    assert pont.ouvrir_lien(url)["erreur"]["code"] == "lien-refuse"
    assert pont.appeler("ouvrir_lien", url)["erreur"]["code"] == "lien-refuse"
    assert fenetre.scripts == []


def test_ouvrir_lien_confie_l_url_au_navigateur_systeme(banc: Any) -> None:
    pont, _ = banc(FakeLlm(script(mots(1, "j"))))
    ouverts: list[str] = []
    pont._ouvreur = lambda url: ouverts.append(url) or True  # type: ignore[assignment]
    urls = (
        "https://www.service-public.fr/particuliers/vosdroits/F1",
        "https://WWW.DATA.GOUV.FR./datasets/x",
        "https://www.legifrance.gouv.fr:443/loda",
    )
    for url in urls:
        assert pont.appeler("ouvrir_lien", url) == {"ok": True}
    assert ouverts == list(urls)
    assert pont.appeler("ouvrir_lien")["erreur"]["code"] == "methode-inconnue"
    assert pont.ouvrir_lien(123)["erreur"]["code"] == "lien-refuse"  # type: ignore[arg-type]


def test_ouvrir_lien_echec_du_navigateur(banc: Any) -> None:
    pont, _ = banc(FakeLlm(script(mots(1, "j"))))

    def casse(url: str) -> bool:
        raise OSError("<erreur-factice>")

    pont._ouvreur = casse  # type: ignore[assignment]
    url = "https://www.service-public.fr/x"
    assert pont.ouvrir_lien(url)["erreur"]["code"] == "ouverture-impossible"
    pont._ouvreur = lambda u: False  # type: ignore[assignment]
    assert pont.ouvrir_lien(url)["erreur"]["code"] == "ouverture-impossible"


def test_effacer_historique_empeche_regenerer(banc: Any, tmp_path: Any) -> None:
    from slmsp.app.stockage import Stockage

    pont, _ = banc(FakeLlm(script(mots(3, "k"))))
    pont._domaines["reglages"] = PontReglages(
        Stockage(tmp_path / "a.sqlite"), apres_effacement=pont._conversation.oublier_dernier
    )
    pont.envoyer("Q", _user(mots(3, "l")), {})
    pont._conversation.attendre(5)
    assert pont.appeler("reglages.effacer_historique") == {"ok": True}
    assert pont.regenerer()["erreur"]["code"] == "rien-a-regenerer"
