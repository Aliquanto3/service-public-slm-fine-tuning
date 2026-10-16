"""Tests du lancement (story 12.6) : ports factices, aucune fenêtre réelle."""

from __future__ import annotations

import contextlib
import os
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import urlsplit

import pytest

from slmsp.app import principal
from slmsp.app.principal import (
    Chrono,
    Demarrage,
    GardeNavigation,
    InstanceUnique,
    PontDiffere,
    decider_navigation,
    geometrie_initiale,
)
from slmsp.app.stockage import Stockage

ECRAN = (0, 0, 1920, 1080)
HOTES = frozenset({"www.service-public.fr", "www.data.gouv.fr"})


class ApiFausse:
    def __init__(self, existe: bool = False) -> None:
        self.existe = existe
        self.libere: list[Any] = []
        self.premier_plan_titres: list[str] = []

    def creer_mutex(self, nom: str) -> tuple[Any, bool]:
        return "poignee", self.existe

    def liberer(self, poignee: Any) -> None:
        self.libere.append(poignee)

    def premier_plan(self, titre: str) -> bool:
        self.premier_plan_titres.append(titre)
        return True


def test_instance_unique_premiere_puis_seconde() -> None:
    api = ApiFausse()
    premiere = InstanceUnique(api)
    assert premiere.acquerir() is True
    premiere.liberer()
    assert api.libere == ["poignee"]
    seconde_api = ApiFausse(existe=True)
    assert InstanceUnique(seconde_api).acquerir() is False
    assert seconde_api.premier_plan_titres == [principal.TITRE]
    assert seconde_api.libere == ["poignee"]


def test_mutex_reel_deux_instances() -> None:
    nom = f"Local\\AssistantSP-test-{time.monotonic_ns()}"
    api = principal.ApiWindows()
    a, b = InstanceUnique(api, nom), InstanceUnique(api, nom)
    assert a.acquerir() is True
    try:
        assert b.acquerir() is False
    finally:
        a.liberer()
    assert b.acquerir() is True
    b.liberer()


def test_geometrie_defaut_et_minimum() -> None:
    assert geometrie_initiale(None, [ECRAN]) == {
        "largeur": 1280,
        "hauteur": 800,
        "x": None,
        "y": None,
    }
    petite = geometrie_initiale({"x": 10, "y": 10, "largeur": 300, "hauteur": 200}, [ECRAN])
    assert (petite["largeur"], petite["hauteur"]) == (1024, 640)


def test_geometrie_restauree() -> None:
    memo = {"x": 100, "y": 50, "largeur": 1400, "hauteur": 900}
    assert geometrie_initiale(memo, [ECRAN]) == {"largeur": 1400, "hauteur": 900, "x": 100, "y": 50}


def test_geometrie_ramenee_a_l_ecran_si_il_a_change() -> None:
    hors = {"x": 3000, "y": 100, "largeur": 1400, "hauteur": 900}
    assert geometrie_initiale(hors, [ECRAN])["x"] is None  # écran disparu : centrée
    deborde = {"x": 1500, "y": 500, "largeur": 1400, "hauteur": 900}
    geo = geometrie_initiale(deborde, [ECRAN])
    assert geo["x"] + geo["largeur"] <= 1920 and geo["y"] + geo["hauteur"] <= 1080
    grande = geometrie_initiale({"largeur": 5000, "hauteur": 4000}, [ECRAN])
    assert (grande["largeur"], grande["hauteur"]) == (1920, 1080)


def test_geometrie_valeurs_invalides() -> None:
    geo = geometrie_initiale({"x": "a", "largeur": True, "hauteur": None}, [ECRAN])
    assert geo == {"largeur": 1280, "hauteur": 800, "x": None, "y": None}
    assert geometrie_initiale("<valeur-factice>", []) == geo


@pytest.mark.parametrize(
    ("url", "attendu"),
    [
        ("http://127.0.0.1:4242/index.html", "autoriser"),
        ("about:blank", "autoriser"),
        ("http://127.0.0.1:9999/", "refuser"),  # autre port local que l'origine
        ("http://localhost:4242/x", "refuser"),  # origine = netloc exact
        ("https://www.service-public.fr/particuliers", "ouvrir"),
        ("https://WWW.Service-Public.fr./x", "ouvrir"),
        ("https://www.service-public.fr:8443/x", "refuser"),
        ("https://user@www.service-public.fr/", "refuser"),
        ("https://exemple.invalid/", "refuser"),
        ("http://www.service-public.fr/", "refuser"),
        ("file:///C:/secret.txt", "refuser"),
        ("javascript:alert(1)", "refuser"),
        ("data:text/html,x", "refuser"),
        ("https://[::1", "refuser"),
    ],
)
def test_decider_navigation(url: str, attendu: str) -> None:
    assert decider_navigation(url, "127.0.0.1:4242", HOTES) == attendu


def test_garde_navigation_annule_et_ouvre() -> None:
    ouverts: list[str] = []
    garde = GardeNavigation(lambda: "127.0.0.1:4242", HOTES, ouverts.append)
    local = SimpleNamespace(Uri="http://127.0.0.1:4242/index.html", Cancel=False)
    garde(None, local)
    assert local.Cancel is False
    blanche = SimpleNamespace(Uri="https://www.data.gouv.fr/fr/", Cancel=False)
    garde(None, blanche)
    assert blanche.Cancel is True and ouverts == ["https://www.data.gouv.fr/fr/"]
    externe = SimpleNamespace(Uri="https://autre.example/", Cancel=False)
    garde(None, externe)
    assert externe.Cancel is True and len(ouverts) == 1
    casse = SimpleNamespace(Cancel=False)  # pas d'`Uri` : refus par défaut
    garde(None, casse)
    assert casse.Cancel is True


def test_brancher_garde_sans_fenetre_native() -> None:
    garde = GardeNavigation(lambda: None, HOTES)
    assert principal.brancher_garde(SimpleNamespace(native=None), garde) is False


def test_interface_servie_sans_pont_factice(tmp_path: Path) -> None:
    index = principal.preparer_interface(tmp_path / "ui")
    assert index.is_file()
    assert not list((tmp_path / "ui").rglob("pont-factice.js"))
    assert (tmp_path / "ui" / "js" / "socle" / "app.js").is_file()
    assert (principal.dossier_interface() / "js" / "socle" / "pont-factice.js").is_file()


def test_arguments_navigateur() -> None:
    valeur = principal.arguments_navigateur("--existant")
    assert valeur.startswith("--existant ")
    assert "msSmartScreenProtection" in valeur and "ElasticOverscroll" in valeur
    assert "--no-pings" in valeur and "--disable-background-networking" in valeur


def test_pont_differe_refuse_avant_assemblage() -> None:
    differe = PontDiffere()
    reponse = differe.appeler("envoyer", "Q", [])
    assert reponse["ok"] is False and reponse["erreur"]["code"] == "preparation"
    differe.brancher(SimpleNamespace(appeler=lambda nom, *a: {"ok": True, "nom": nom}))  # type: ignore[arg-type]
    assert differe.appeler("arreter") == {"ok": True, "nom": "arreter"}


# --- Démarrage ---------------------------------------------------------------------------


class FenetreFausse:
    def __init__(self, pret_js: bool = True, delai_evaluate: float = 0.0) -> None:
        self.scripts: list[str] = []
        self.pret_js = pret_js
        self.delai = delai_evaluate

    def evaluate_js(self, script: str) -> Any:
        if self.delai:
            time.sleep(self.delai)
        self.scripts.append(script)
        return self.pret_js if script.startswith("!!") else None


def assemblage_factice(appels: list[dict[str, Any]], echec: bool = False) -> Any:
    @contextlib.contextmanager
    def fabrique(modele: str, **options: Any) -> Any:
        appels.append({"modele": modele, **options})
        if echec:
            raise RuntimeError("<erreur-factice>")
        yield SimpleNamespace(service=SimpleNamespace())

    return fabrique


@pytest.fixture
def stockage(tmp_path: Path) -> Stockage:
    return Stockage(tmp_path / "app.sqlite")


def attendre(condition: Any, delai: float = 5.0) -> None:
    fin = time.monotonic() + delai
    while time.monotonic() < fin and not condition():
        time.sleep(0.01)
    assert condition()


def test_demarrage_signale_pret_apres_page_et_assemblage(stockage: Stockage) -> None:
    appels: list[dict[str, Any]] = []
    fenetre, differe = FenetreFausse(), PontDiffere()
    d = Demarrage(
        stockage, fenetre, differe, fabrique_assemblage=assemblage_factice(appels), pas_s=0.01
    )
    d.demarrer()
    attendre(lambda: differe._pont is not None)
    time.sleep(0.1)
    assert not any('"pret"' in s for s in fenetre.scripts)  # page pas encore chargée
    d.page_chargee()
    attendre(lambda: any('"pret"' in s for s in fenetre.scripts))
    assert d.chrono.pret_s is not None
    d.arreter()
    assert d._fil is not None and not d._fil.is_alive()
    assert appels[0]["modele"].startswith("base:") and appels[0]["hors_ligne"] is False


def test_demarrage_hors_ligne_force_avant_toute_sonde(stockage: Stockage) -> None:
    stockage.ecrire_reglage("hors_ligne_force", True)
    appels: list[dict[str, Any]] = []
    d = Demarrage(
        stockage,
        FenetreFausse(),
        PontDiffere(),
        fabrique_assemblage=assemblage_factice(appels),
        pas_s=0.01,
    )
    d.demarrer()
    attendre(lambda: bool(appels))
    d.arreter()
    assert appels[0]["hors_ligne"] is True
    assert appels[0]["journal"] is not None


def test_demarrage_echec_signale_une_erreur_generique(stockage: Stockage) -> None:
    fenetre = FenetreFausse()
    d = Demarrage(
        stockage,
        fenetre,
        PontDiffere(),
        fabrique_assemblage=assemblage_factice([], echec=True),
        pas_s=0.01,
    )
    d.page_chargee()
    d.demarrer()
    attendre(lambda: any('"erreur"' in s for s in fenetre.scripts))
    assert d.erreur == "RuntimeError"
    assert not any("<erreur-factice>" in s for s in fenetre.scripts)


def test_page_jamais_prete_ne_signale_pas_pret(stockage: Stockage) -> None:
    fenetre = FenetreFausse(pret_js=False)
    d = Demarrage(
        stockage,
        fenetre,
        PontDiffere(),
        fabrique_assemblage=assemblage_factice([]),
        delai_page_s=0.1,
        pas_s=0.01,
    )
    d.page_chargee()
    d.demarrer()
    time.sleep(0.4)
    d.arreter()
    assert not any('"pret"' in s for s in fenetre.scripts)


def test_arreter_n_est_pas_bloque_par_un_evaluate_js_lent() -> None:
    """`Conversation.arreter` tient le verrou d'envoi le temps d'un `evaluate_js` : borné."""
    from slmsp.app.pont import Pont

    class Service:
        def repondre(self, *a: Any, **k: Any) -> Any:
            def flux() -> Any:
                threading.Event().wait(0.3)
                yield from ()

            return flux()

    fenetre = FenetreFausse(delai_evaluate=0.2)
    pont = Pont(Service(), fenetre)  # type: ignore[arg-type]
    assert pont.envoyer("Q", [{"role": "user", "content": "<texte-factice>"}])["ok"] is True
    debut = time.monotonic()
    assert pont.arreter()["en_cours"] is True
    assert time.monotonic() - debut < 1.0
    assert pont.appeler("nouvelle_conversation")["ok"] is True


def test_chrono_consigne_la_duree(caplog: pytest.LogCaptureFixture) -> None:
    horloge = iter([0.0, 1.5, 4.0])
    chrono = Chrono(lambda: next(horloge))
    chrono.fenetre()
    with caplog.at_level("INFO", logger="slmsp.app"):
        assert chrono.pret() == 4.0
    assert "pret 4.00 s" in caplog.text


# --- lancer() avec un `webview` factice --------------------------------------------------


class EvenementFactice:
    def __init__(self) -> None:
        self.fonctions: list[Any] = []

    def __iadd__(self, fonction: Any) -> EvenementFactice:
        self.fonctions.append(fonction)
        return self

    def declencher(self) -> None:
        for fonction in self.fonctions:
            fonction()


class WebviewFactice:
    def __init__(self) -> None:
        self.screens = [SimpleNamespace(x=0, y=0, width=1920, height=1080)]
        self.creations: list[dict[str, Any]] = []
        self.start_kwargs: dict[str, Any] = {}
        self.fenetre = SimpleNamespace(
            events=SimpleNamespace(
                shown=EvenementFactice(), loaded=EvenementFactice(), closing=EvenementFactice()
            ),
            native=None,
            real_url="http://127.0.0.1:5555/index.html",
            x=7,
            y=8,
            width=1500,
            height=900,
            evaluate_js=lambda script: True,
        )

    def create_window(self, titre: str, **kwargs: Any) -> Any:
        self.creations.append({"titre": titre, **kwargs})
        return self.fenetre

    def start(self, **kwargs: Any) -> None:
        self.start_kwargs = kwargs
        self.fenetre.events.shown.declencher()
        self.fenetre.events.loaded.declencher()
        self.fenetre.events.closing.declencher()


def test_lancer_cree_la_fenetre_et_memorise(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    stockage.ecrire_reglage("fenetre", {"x": 50, "y": 60, "largeur": 1300, "hauteur": 850})
    web, api = WebviewFactice(), ApiFausse()
    appels: list[dict[str, Any]] = []
    code = principal.lancer(
        webview=web,
        stockage=stockage,
        instance=InstanceUnique(api),
        fabrique_assemblage=assemblage_factice(appels),
    )
    assert code == 0
    creation = web.creations[0]
    assert (creation["width"], creation["height"], creation["x"], creation["y"]) == (
        1300,
        850,
        50,
        60,
    )
    assert creation["min_size"] == (1024, 640)
    assert isinstance(creation["js_api"], PontDiffere)
    assert web.start_kwargs["http_server"] is True
    assert "msSmartScreenProtection" in os.environ[principal.VARIABLE_ARGUMENTS]
    assert stockage.lire_reglage("fenetre") == {"x": 7, "y": 8, "largeur": 1500, "hauteur": 900}
    assert api.libere == ["poignee"]  # mutex relâché
    assert appels  # l'assemblage a été lancé puis quitté


def test_lancer_seconde_instance_ne_cree_rien(stockage: Stockage) -> None:
    web, api = WebviewFactice(), ApiFausse(existe=True)
    assert principal.lancer(webview=web, stockage=stockage, instance=InstanceUnique(api)) == 0
    assert web.creations == []
    assert api.premier_plan_titres == [principal.TITRE]


@pytest.mark.lent
def test_fenetre_reelle_cachee(tmp_path: Path) -> None:
    """Fenêtre pywebview réelle, cachée, fermée aussitôt : l'interface est servie en HTTP."""
    webview = pytest.importorskip("webview")
    index = principal.preparer_interface(tmp_path / "ui")
    resultat: dict[str, Any] = {}
    ouverts: list[str] = []
    fenetre = webview.create_window("test", url=str(index), hidden=True)
    garde = GardeNavigation(
        lambda: urlsplit(fenetre.real_url).netloc.lower(), HOTES, ouverts.append
    )
    resultat["branchee"] = None
    fenetre.events.shown += lambda: resultat.update(
        branchee=principal.brancher_garde(fenetre, garde)
    )

    def sonde() -> None:
        fenetre.events.loaded.wait(20)
        resultat["url"] = fenetre.real_url
        resultat["fonction"] = fenetre.evaluate_js("typeof window.slmspRecevoir")
        fenetre.load_url("https://exemple.invalid/")
        time.sleep(1.5)
        resultat["apres"] = fenetre.evaluate_js("location.href")
        fenetre.destroy()

    webview.start(sonde, http_server=True, private_mode=True)
    assert resultat["url"].startswith("http://127.0.0.1:")
    assert resultat["fonction"] == "function"
    assert resultat["branchee"] is True
    assert resultat["apres"].startswith("http://127.0.0.1:")  # navigation externe annulée
    assert ouverts == []
