"""Tests du lancement (story 12.6) : ports factices, aucune fenêtre réelle."""

from __future__ import annotations

import contextlib
import os
import threading
import time
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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
from slmsp.app.stockage import JournalApplication, Stockage
from slmsp.core.config import env_sous_processus

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


def test_geometrie_sans_ecran_lisible_abandonne_la_position() -> None:
    memo = {"x": -32000, "y": -32000, "largeur": 1400, "hauteur": 900}
    geo = geometrie_initiale(memo, [])
    assert (geo["x"], geo["y"]) == (None, None)
    assert (geo["largeur"], geo["hauteur"]) == (1400, 900)


def test_origine_inconnue_refuse_le_local() -> None:
    assert decider_navigation("http://127.0.0.1:5555/", None, HOTES) == "refuser"
    assert decider_navigation("http://127.0.0.1:5555/", "", HOTES) == "refuser"


def test_arguments_webview2_absents_des_sous_processus() -> None:
    base = {"PATH": "x", principal.VARIABLE_ARGUMENTS: "--no-pings", "webview2_autre": "1"}
    env = env_sous_processus(base)
    assert "PATH" in env
    assert not any(nom.upper().startswith("WEBVIEW2_") for nom in env)


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
        yield SimpleNamespace(service=SimpleNamespace(mode=None))

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
        mode = None

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


class NavigationFactice:
    """`NavigationStarting` de la WebView2 : `+=` abonne un gestionnaire `(expediteur, args)`."""

    def __init__(self) -> None:
        self.gestionnaires: list[Any] = []

    def __iadd__(self, gestionnaire: Any) -> NavigationFactice:
        self.gestionnaires.append(gestionnaire)
        return self

    def naviguer(self, url: str) -> bool:
        """Rend True si la navigation a lieu (aucun gestionnaire ne l'annule)."""
        args = SimpleNamespace(Uri=url, Cancel=False)
        for gestionnaire in self.gestionnaires:
            gestionnaire(None, args)
        return not args.Cancel


class WebviewFactice:
    """Module `webview` factice. `start` rejoue le cycle de vie et deux scénarios Q1 : une
    navigation dans la page et un `NewWindowRequested`, modélisé comme pywebview 6.2.1
    (`EdgeChrome.on_new_window_request`) : `webbrowser.open` si
    `OPEN_EXTERNAL_LINKS_IN_BROWSER`, sinon `load_url`, qui passe par `NavigationStarting`."""

    def __init__(self, native: bool = True, navigations: Sequence[str] = ()) -> None:
        self.screens = [SimpleNamespace(x=0, y=0, width=1920, height=1080)]
        self.settings = {"OPEN_EXTERNAL_LINKS_IN_BROWSER": True, "ALLOW_FILE_URLS": True}
        self.creations: list[dict[str, Any]] = []
        self.start_kwargs: dict[str, Any] = {}
        self.navigation = NavigationFactice()
        self.navigations = list(navigations)
        self.resultats: dict[str, bool] = {}
        self.ouverts_par_pywebview: list[str] = []
        self.detruite = False
        webview2 = SimpleNamespace(NavigationStarting=self.navigation)
        self.fenetre = SimpleNamespace(
            events=SimpleNamespace(
                shown=EvenementFactice(), loaded=EvenementFactice(), closing=EvenementFactice()
            ),
            native=SimpleNamespace(browser=SimpleNamespace(webview=webview2)) if native else None,
            real_url="http://127.0.0.1:5555/index.html",
            x=7,
            y=8,
            width=1500,
            height=900,
            evaluate_js=lambda script: True,
            destroy=self._detruire,
        )

    def _detruire(self) -> None:
        self.detruite = True

    def _nouvelle_fenetre(self, url: str) -> None:
        if self.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"]:
            self.ouverts_par_pywebview.append(url)
        else:
            self.navigation.naviguer(url)

    def create_window(self, titre: str, **kwargs: Any) -> Any:
        self.creations.append({"titre": titre, **kwargs})
        return self.fenetre

    def start(self, **kwargs: Any) -> None:
        self.start_kwargs = kwargs
        self.fenetre.events.shown.declencher()
        if self.detruite:
            return
        self.fenetre.events.loaded.declencher()
        for url in self.navigations:
            self.resultats[url] = self.navigation.naviguer(url)
        for url in self.navigations:
            self._nouvelle_fenetre(url)
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
    assert web.start_kwargs == {
        "http_server": True,
        "private_mode": False,
        "storage_path": str(tmp_path / "AssistantSP" / "webview"),
    }
    assert "msSmartScreenProtection" in os.environ[principal.VARIABLE_ARGUMENTS]
    assert stockage.lire_reglage("fenetre") == {"x": 7, "y": 8, "largeur": 1500, "hauteur": 900}
    assert api.libere == ["poignee"]  # mutex relâché
    assert appels  # l'assemblage a été lancé puis quitté
    # Journal de la passerelle et pont sur le même stockage (vue Mode, 12.9).
    journal = appels[0]["journal"]
    assert isinstance(journal, JournalApplication) and journal._stockage is stockage
    assert creation["js_api"]._pont._stockage is stockage


def test_lancer_cable_la_garde_et_filtre_les_nouvelles_fenetres(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Câblage réel de `lancer()` (Q1) : garde abonnée à `NavigationStarting`, nouvelles
    fenêtres ramenées à la garde, seuls les `https` de la Liste blanche partent au navigateur."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    ouverts: list[str] = []
    monkeypatch.setattr(principal.webbrowser, "open", lambda url: ouverts.append(url) or True)
    autorise = "https://www.service-public.fr/particuliers"
    urls = [
        "http://127.0.0.1:5555/autre.html",
        "http://127.0.0.1:9999/",
        autorise,
        "https://exemple.invalid/",
        "file:///C:/Windows/win.ini",
    ]
    web = WebviewFactice(navigations=urls)
    code = principal.lancer(
        webview=web,
        stockage=stockage,
        instance=InstanceUnique(ApiFausse()),
        fabrique_assemblage=assemblage_factice([]),
    )
    assert code == 0
    assert len(web.navigation.gestionnaires) == 1  # garde branchée à `shown`
    assert web.resultats == {
        "http://127.0.0.1:5555/autre.html": True,
        "http://127.0.0.1:9999/": False,
        autorise: False,  # annulée dans la WebView, confiée au navigateur
        "https://exemple.invalid/": False,
        "file:///C:/Windows/win.ini": False,
    }
    assert web.settings == {"OPEN_EXTERNAL_LINKS_IN_BROWSER": False, "ALLOW_FILE_URLS": False}
    assert web.ouverts_par_pywebview == []
    assert ouverts == [autorise, autorise]  # navigation puis nouvelle fenêtre


def test_lancer_s_arrete_sans_garde(
    stockage: Stockage,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    web, api = WebviewFactice(native=False), ApiFausse()
    code = principal.lancer(
        webview=web,
        stockage=stockage,
        instance=InstanceUnique(api),
        fabrique_assemblage=assemblage_factice([]),
    )
    assert code == 1
    assert web.detruite is True
    assert principal.MESSAGE_SANS_GARDE in capsys.readouterr().err
    assert api.libere == ["poignee"]


def test_lancer_garde_le_mutex_si_l_assemblage_ne_s_arrete_pas(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    monkeypatch.setattr(principal.Demarrage, "arreter", lambda self, delai_s=20.0: False)
    api = ApiFausse()
    code = principal.lancer(
        webview=WebviewFactice(),
        stockage=stockage,
        instance=InstanceUnique(api),
        fabrique_assemblage=assemblage_factice([]),
    )
    assert code == 0
    assert api.libere == []  # relâché par la fin du processus


def test_lancer_seconde_instance_ne_cree_rien(stockage: Stockage) -> None:
    web, api = WebviewFactice(), ApiFausse(existe=True)
    assert principal.lancer(webview=web, stockage=stockage, instance=InstanceUnique(api)) == 0
    assert web.creations == []
    assert api.premier_plan_titres == [principal.TITRE]


@pytest.mark.lent
def test_fenetre_reelle_cachee(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`lancer()` avec le vrai pywebview (fenêtre cachée, assemblage factice) : interface en
    HTTP local, garde branchée, navigation et `window.open` externes sans effet (Q1)."""
    webview = pytest.importorskip("webview")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    for cle in ("OPEN_EXTERNAL_LINKS_IN_BROWSER", "ALLOW_FILE_URLS"):
        monkeypatch.setitem(webview.settings, cle, webview.settings[cle])  # restauré après
    ouverts: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url, *a, **k: ouverts.append(url) or True)
    resultat: dict[str, Any] = {}

    class WebviewReelCache:
        """Le vrai module ; seule la fenêtre est cachée et une sonde est passée à `start`."""

        screens = webview.screens
        settings = webview.settings

        def create_window(self, titre: str, **kwargs: Any) -> Any:
            self.fenetre = webview.create_window(titre, hidden=True, **kwargs)
            return self.fenetre

        def start(self, **kwargs: Any) -> None:
            resultat["start"] = kwargs
            webview.start(lambda: sonde(self.fenetre), **kwargs)

    def sonde(fenetre: Any) -> None:
        fenetre.events.loaded.wait(20)
        resultat["url"] = fenetre.real_url
        resultat["fonction"] = fenetre.evaluate_js("typeof window.slmspRecevoir")
        fenetre.load_url("https://exemple.invalid/")
        time.sleep(1.5)
        fenetre.evaluate_js("window.open('https://exemple.invalid/nouvelle')")
        time.sleep(1.5)
        resultat["apres"] = fenetre.evaluate_js("location.href")
        fenetre.destroy()

    code = principal.lancer(
        webview=WebviewReelCache(),
        stockage=stockage,
        instance=InstanceUnique(ApiFausse()),
        fabrique_assemblage=assemblage_factice([]),
    )
    assert code == 0  # 1 si la garde n'avait pas pu être branchée
    assert resultat["start"]["private_mode"] is False
    assert resultat["url"].startswith("http://127.0.0.1:")
    assert resultat["fonction"] == "function"
    assert resultat["apres"].startswith("http://127.0.0.1:")  # navigations externes annulées
    assert ouverts == []


def test_lancer_la_requete_de_la_passerelle_apparait_dans_la_vue_mode(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bout en bout (story 12.9) : une vraie `Passerelle` écrit dans le journal reçu de
    `lancer()` ; `mode.journal()` du pont la lit, et « Effacer » vide ce même journal."""
    from slmsp.core.erreurs import HoteBloque
    from slmsp.harness.modes import ModeFixe
    from slmsp.net.client import Passerelle

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    mode = ModeFixe("connecte")

    @contextlib.contextmanager
    def fabrique(modele: str, **options: Any) -> Any:
        passerelle = Passerelle(mode, options["journal"])
        with pytest.raises(HoteBloque):
            passerelle.verifier("assistant", "GET", "https://hote-hors-liste.invalid/x")
        yield SimpleNamespace(service=SimpleNamespace(mode=mode))

    web = WebviewFactice()
    code = principal.lancer(
        webview=web,
        stockage=stockage,
        instance=InstanceUnique(ApiFausse()),
        fabrique_assemblage=fabrique,
    )
    assert code == 0
    domaine_mode = web.creations[0]["js_api"]._pont._domaines["mode"]
    entrees = domaine_mode.journal(None)["entrees"]
    assert [(e["hote"], e["statut"]) for e in entrees] == [
        ("hote-hors-liste.invalid", "bloquee-liste")
    ]
    assert domaine_mode.effacer_journal() == {"ok": True}
    assert domaine_mode.journal(None)["entrees"] == []
    assert JournalApplication(stockage).lister() == []


# -- Story 13.6 : câblage du vérificateur (FR-12) ---------------------------------------------


def _assemblage_verification(mode: Any, index: Any) -> Any:
    from slmsp.net.client import Passerelle
    from slmsp.net.journal import JournalMemoire

    passerelle = Passerelle(mode, JournalMemoire())
    service = SimpleNamespace(
        mode=mode,
        llm=SimpleNamespace(appels=[]),
        recherche=SimpleNamespace(vector_store=index),
        config=SimpleNamespace(verification=None),
    )
    return SimpleNamespace(service=service, passerelle=passerelle)


def test_construire_verificateur_lie_passerelle_llm_et_index() -> None:
    from slmsp.harness.modes import ModeFixe

    demandes: list[str] = []

    class IndexFactice:
        def contient_url(self, url: str) -> bool:
            demandes.append(url)
            return True

    assemblage = _assemblage_verification(ModeFixe("connecte"), IndexFactice())
    verificateur = principal.construire_verificateur(assemblage)
    assert verificateur is not None
    assert verificateur.passerelle is assemblage.passerelle  # le Mode de la passerelle prime
    assert verificateur.llm is assemblage.service.llm
    assert verificateur.dans_index is not None
    assert verificateur.dans_index("https://exemple.invalid/x") is True
    assert demandes == ["https://exemple.invalid/x"]


def test_construire_verificateur_sans_index_ne_retient_aucune_source() -> None:
    from slmsp.harness.modes import ModeFixe

    verificateur = principal.construire_verificateur(
        _assemblage_verification(ModeFixe("connecte"), None)
    )
    assert verificateur is not None and verificateur.dans_index is not None
    assert verificateur.dans_index("https://exemple.invalid/x") is False
    assert principal.construire_verificateur(SimpleNamespace(service=SimpleNamespace())) is None


def test_lancer_cable_la_verification_hors_ligne_force_aucune_requete(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bout en bout : `lancer()` branche le vérificateur sur la passerelle de l'assemblage ;
    hors ligne forcé, le verdict est `indisponible` et le journal n'a que le refus de Mode."""
    from slmsp.core.evenements import Source, vers_dict
    from slmsp.harness.modes import ModeFixe

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv(principal.VARIABLE_ARGUMENTS, raising=False)
    mode = ModeFixe("hors-ligne-force")
    assemblage = _assemblage_verification(mode, SimpleNamespace(contient_url=lambda _u: True))

    @contextlib.contextmanager
    def fabrique(modele: str, **options: Any) -> Any:
        yield assemblage

    web = WebviewFactice()
    code = principal.lancer(
        webview=web,
        stockage=stockage,
        instance=InstanceUnique(ApiFausse()),
        fabrique_assemblage=fabrique,
    )
    assert code == 0
    domaine = web.creations[0]["js_api"]._pont._domaines["verification"]
    source = vers_dict(
        Source(
            numero=1,
            titre="<titre-factice-1>",
            url="https://www.service-public.gouv.fr/particuliers/vosdroits/F0000",
            origine="index",
        )
    )
    resultat = domaine.appeler("verifier", "<réponse-factice-1> [1]", [source])
    assert resultat["ok"] is True
    assert [e["type"] for e in resultat["evenements"]] == ["verification"]
    assert resultat["evenements"][0]["verdict"] == "indisponible"
    assert [e.statut for e in assemblage.passerelle.journal.lister()] == ["bloquee-mode"]
