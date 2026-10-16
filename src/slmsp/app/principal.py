"""Lancement de l'application (story 12.6, AD-6, AD-27, UX-DR23, Q1).

`python -m slmsp.app` et le script `assistantsp`. Ordre : instance unique (mutex nommé), fenêtre
à la taille mémorisée (affichée tout de suite), assemblage dans un fil de fond, puis signal `pret`
au pont. À la fermeture, l'assemblage est quitté (arrêt des `llama-server`, tenus par un
JobObject : ils ne survivent pas à une fin brutale du processus).

Réseau de la WebView2 (Q1) : interface servie en HTTP local (jamais `file://`), CSP
`default-src 'self'`, arguments de navigateur coupant SmartScreen et les pings, toute navigation
refusée sauf l'origine locale ; une URL `https` de la Liste blanche s'ouvre dans le navigateur du
système. `pywebview` n'est importé qu'à l'exécution (extra `app`).
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import shutil
import sys
import tempfile
import threading
import time
import webbrowser
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal, Protocol
from urllib.parse import urlsplit

from slmsp.app.pont import Pont
from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.stockage import JournalApplication, Stockage, dossier_donnees
from slmsp.core.evenements import Erreur, vers_dict
from slmsp.core.schemas.config_application import charger_config_application
from slmsp.harness.assemblage import assembler
from slmsp.net.config import charger_liste_blanche

LOGGER: Final = logging.getLogger("slmsp.app")
TITRE: Final = "Assistant"
NOM_MUTEX: Final = "Local\\AssistantSP-instance-unique"
LARGEUR_DEFAUT: Final = 1280
HAUTEUR_DEFAUT: Final = 800
MIN_LARGEUR: Final = 1024
MIN_HAUTEUR: Final = 640
CIBLE_DEMARRAGE_S: Final = 10.0
HOTES_LOCAUX: Final = frozenset({"127.0.0.1", "localhost"})
FICHIER_EXCLU: Final = "pont-factice.js"
ARGUMENTS_WEBVIEW2: Final = (
    # Reprend `--disable-features=ElasticOverscroll` de pywebview (le dernier l'emporte).
    "--disable-features=ElasticOverscroll,msSmartScreenProtection,msEdgeSmartScreen",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-domain-reliability",
    "--disable-sync",
    "--no-pings",
    "--no-default-browser-check",
)
VARIABLE_ARGUMENTS: Final = "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"
ERREUR_DEMARRAGE: Final = "demarrage"
MESSAGE_DEMARRAGE: Final = "L'assistant n'a pas pu démarrer. Fermez-le puis relancez-le."
SW_RESTORE: Final = 9
ERROR_ALREADY_EXISTS: Final = 183


# --- Instance unique ---------------------------------------------------------------------


class ApiInstance(Protocol):
    """Port des appels Windows de l'instance unique."""

    def creer_mutex(self, nom: str) -> tuple[Any, bool]:
        """Rend `(poignée, existait_deja)`."""
        ...

    def liberer(self, poignee: Any) -> None: ...

    def premier_plan(self, titre: str) -> bool:
        """Restaure et passe au premier plan la fenêtre intitulée `titre`."""
        ...


class ApiWindows:
    """Implémentation `ctypes` de `ApiInstance`."""

    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        self._ctypes = ctypes
        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._u32 = ctypes.WinDLL("user32", use_last_error=True)
        self._k32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self._k32.CreateMutexW.restype = wintypes.HANDLE
        self._k32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._u32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self._u32.FindWindowW.restype = wintypes.HWND
        self._u32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self._u32.SetForegroundWindow.argtypes = [wintypes.HWND]

    def creer_mutex(self, nom: str) -> tuple[Any, bool]:
        poignee = self._k32.CreateMutexW(None, False, nom)
        erreur = self._ctypes.get_last_error()
        if not poignee:
            raise OSError(f"CreateMutexW a échoué ({erreur})")
        return poignee, erreur == ERROR_ALREADY_EXISTS

    def liberer(self, poignee: Any) -> None:
        self._k32.CloseHandle(poignee)

    def premier_plan(self, titre: str) -> bool:
        fenetre = self._u32.FindWindowW(None, titre)
        if not fenetre:
            return False
        self._u32.ShowWindow(fenetre, SW_RESTORE)
        return bool(self._u32.SetForegroundWindow(fenetre))


class InstanceUnique:
    """Mutex nommé : `acquerir()` vaut False si une autre instance tient déjà la place."""

    def __init__(self, api: ApiInstance | None = None, nom: str = NOM_MUTEX) -> None:
        self._api = api if api is not None else ApiWindows()
        self._nom = nom
        self._poignee: Any = None

    def acquerir(self) -> bool:
        poignee, existait = self._api.creer_mutex(self._nom)
        if existait:
            self._api.liberer(poignee)
            self._api.premier_plan(TITRE)
            return False
        self._poignee = poignee
        return True

    def liberer(self) -> None:
        if self._poignee is not None:
            self._api.liberer(self._poignee)
            self._poignee = None


# --- Géométrie de la fenêtre -------------------------------------------------------------

Ecran = tuple[int, int, int, int]
"""`(x, y, largeur, hauteur)` d'un écran."""


def geometrie_initiale(memorisee: Any, ecrans: Sequence[Ecran]) -> dict[str, int | None]:
    """Taille et position à l'ouverture, d'après le réglage `fenetre` (UX-DR23).

    Taille minimale 1 024 × 640. Une position qui ne tombe plus sur aucun écran (écran
    débranché, résolution changée) est abandonnée : le système centre la fenêtre. Une fenêtre
    plus grande que l'écran est ramenée à sa taille.
    """
    largeur, hauteur, x, y = LARGEUR_DEFAUT, HAUTEUR_DEFAUT, None, None
    if isinstance(memorisee, Mapping):
        largeur = _entier(memorisee.get("largeur"), largeur)
        hauteur = _entier(memorisee.get("hauteur"), hauteur)
        x, y = _entier(memorisee.get("x"), None), _entier(memorisee.get("y"), None)
    largeur, hauteur = max(largeur, MIN_LARGEUR), max(hauteur, MIN_HAUTEUR)
    if ecrans:
        if x is not None and y is not None:
            cible = next((e for e in ecrans if _contient(e, x, y, largeur, hauteur)), None)
            if cible is None:
                x = y = None
            else:
                x = min(max(x, cible[0]), cible[0] + max(cible[2] - largeur, 0))
                y = min(max(y, cible[1]), cible[1] + max(cible[3] - hauteur, 0))
        ref = ecrans[0]
        largeur = max(min(largeur, ref[2]), min(MIN_LARGEUR, ref[2]))
        hauteur = max(min(hauteur, ref[3]), min(MIN_HAUTEUR, ref[3]))
    elif x is None or y is None:
        x = y = None
    return {"largeur": largeur, "hauteur": hauteur, "x": x, "y": y}


def _entier(valeur: Any, defaut: int | None) -> Any:
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        return defaut
    return valeur


def _contient(ecran: Ecran, x: int, y: int, largeur: int, hauteur: int) -> bool:
    """Vrai si le coin haut-gauche et une marge de la barre de titre sont visibles."""
    ex, ey, el, eh = ecran
    return ex - largeur // 2 < x < ex + el - 80 and ey <= y < ey + eh - 40


# --- Navigation (Q1) ---------------------------------------------------------------------

Decision = Literal["autoriser", "ouvrir", "refuser"]


def decider_navigation(url: str, origine: str | None, hotes: frozenset[str]) -> Decision:
    """`autoriser` l'origine locale de l'interface, `ouvrir` (navigateur système) une URL
    `https` de la Liste blanche, `refuser` tout le reste (jamais d'exception)."""
    try:
        parties = urlsplit(url)
        hote, port = (parties.hostname or "").lower().rstrip("."), parties.port
    except ValueError:
        return "refuser"
    if parties.scheme == "about" and url == "about:blank":
        return "autoriser"
    if parties.scheme == "http" and hote in HOTES_LOCAUX:
        return "autoriser" if origine is None or parties.netloc.lower() == origine else "refuser"
    if (
        parties.scheme == "https"
        and port in (None, 443)
        and "@" not in parties.netloc
        and hote in hotes
    ):
        return "ouvrir"
    return "refuser"


class GardeNavigation:
    """Gestionnaire de `NavigationStarting` : annule tout sauf l'origine locale."""

    def __init__(
        self,
        origine: Callable[[], str | None],
        hotes: frozenset[str],
        ouvrir: Callable[[str], Any] = webbrowser.open,
    ) -> None:
        self._origine = origine
        self._hotes = hotes
        self._ouvrir = ouvrir

    def __call__(self, _expediteur: Any, args: Any) -> None:
        try:
            url = str(args.Uri)
            decision = decider_navigation(url, self._origine(), self._hotes)
            if decision == "autoriser":
                return
            args.Cancel = True
            if decision == "ouvrir":
                self._ouvrir(url)
        except Exception as exc:
            LOGGER.error("navigation : %s", type(exc).__name__)
            with contextlib.suppress(Exception):
                args.Cancel = True


def brancher_garde(fenetre: Any, garde: GardeNavigation) -> bool:
    """Abonne `garde` à la WebView2 de la fenêtre pywebview. Rend False si impossible."""
    try:
        fenetre.native.browser.webview.NavigationStarting += garde
        return True
    except Exception as exc:
        LOGGER.error("garde de navigation non branchée : %s", type(exc).__name__)
        return False


# --- Pont différé et assemblage ----------------------------------------------------------


class PontDiffere:
    """`js_api` exposé dès la création de la fenêtre ; délègue au `Pont` une fois assemblé."""

    def __init__(self) -> None:
        self._pont: Pont | None = None

    def brancher(self, pont: Pont) -> None:
        self._pont = pont

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        """Voir `Pont.appeler`. Avant la fin de l'assemblage : refus `preparation`."""
        pont = self._pont
        if pont is None:
            return reponse_erreur("preparation", "L'assistant se prépare.")
        return pont.appeler(nom, *args)


class Chrono:
    """Durées de démarrage (UX : cible < 10 s jusqu'à `pret`)."""

    def __init__(self, horloge: Callable[[], float] = time.perf_counter) -> None:
        self._horloge = horloge
        self.debut = horloge()
        self.fenetre_s: float | None = None
        self.pret_s: float | None = None

    def fenetre(self) -> None:
        self.fenetre_s = self._horloge() - self.debut

    def pret(self) -> float:
        self.pret_s = self._horloge() - self.debut
        niveau = logging.INFO if self.pret_s < CIBLE_DEMARRAGE_S else logging.WARNING
        LOGGER.log(
            niveau,
            "démarrage : fenêtre %.2f s, pret %.2f s (cible < %.0f s)",
            self.fenetre_s if self.fenetre_s is not None else -1.0,
            self.pret_s,
            CIBLE_DEMARRAGE_S,
        )
        return self.pret_s


class Demarrage:
    """Assemblage en fil de fond, puis `pret` quand l'assemblage ET la page sont prêts."""

    def __init__(
        self,
        stockage: Stockage,
        fenetre: Any,
        differe: PontDiffere,
        *,
        fabrique_assemblage: Callable[..., Any] = assembler,
        delai_page_s: float = 15.0,
        pas_s: float = 0.1,
        chrono: Chrono | None = None,
    ) -> None:
        self._stockage = stockage
        self._fenetre = fenetre
        self._differe = differe
        self._assembler = fabrique_assemblage
        self._delai_page_s = delai_page_s
        self._pas_s = pas_s
        self.chrono = chrono if chrono is not None else Chrono()
        self._page = threading.Event()  # page chargée (événement `loaded`)
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None
        self.erreur: str | None = None

    def page_chargee(self) -> None:
        self._page.set()

    def demarrer(self) -> None:
        self._fil = threading.Thread(target=self._travail, name="assemblage", daemon=True)
        self._fil.start()

    def arreter(self, delai_s: float = 20.0) -> None:
        """Quitte l'assemblage (arrêt des serveurs) et attend le fil."""
        self._arret.set()
        if self._fil is not None:
            self._fil.join(delai_s)

    def _travail(self) -> None:
        try:
            config = charger_config_application()
            hors_ligne = bool(self._stockage.lire_reglage("hors_ligne_force"))
            with self._assembler(
                f"base:{config.modele}",
                hors_ligne=hors_ligne,
                variante=config.variante,
                journal=JournalApplication(self._stockage),
                threads=config.threads,
            ) as assemblage:
                pont = Pont(assemblage.service, self._fenetre)
                self._differe.brancher(pont)
                if self._page_prete():
                    pont.signaler_pret()
                    self.chrono.pret()
                self._arret.wait()
        except Exception as exc:
            self.erreur = type(exc).__name__
            LOGGER.error("démarrage : %s", self.erreur)
            self._signaler_echec()

    def _page_prete(self) -> bool:
        """Attend l'évènement `loaded` puis `pywebviewready` (API et `slmspRecevoir` définis)."""
        fin = time.monotonic() + self._delai_page_s
        while not self._arret.is_set() and time.monotonic() < fin:
            if self._page.is_set() and self._js_pret():
                return True
            self._arret.wait(self._pas_s)
        LOGGER.error("démarrage : page non prête après %.0f s", self._delai_page_s)
        return False

    def _js_pret(self) -> bool:
        try:
            return bool(
                self._fenetre.evaluate_js(
                    "!!(window.pywebview && window.pywebview.api"
                    " && typeof window.slmspRecevoir === 'function')"
                )
            )
        except Exception:
            return False

    def _signaler_echec(self) -> None:
        """Pousse une erreur générique à l'interface si la page est prête (sinon, sans effet)."""
        if not (self._page.wait(self._delai_page_s) and self._js_pret()):
            return
        lot = [vers_dict(Erreur(code=ERREUR_DEMARRAGE, message=MESSAGE_DEMARRAGE))]
        with contextlib.suppress(Exception):
            self._fenetre.evaluate_js(f"window.slmspRecevoir({json.dumps(lot)})")


# --- Interface servie --------------------------------------------------------------------


def dossier_interface() -> Path:
    return Path(__file__).resolve().parent / "ui"


def preparer_interface(destination: Path, source: Path | None = None) -> Path:
    """Copie l'interface sans le pont factice (`?pont=factice` inactif une fois installé)."""
    source = source if source is not None else dossier_interface()
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(FICHIER_EXCLU))
    return destination / "index.html"


def arguments_navigateur(existants: str = "") -> str:
    """Valeur de `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` (SmartScreen et pings coupés)."""
    return " ".join(part for part in (existants.strip(), *ARGUMENTS_WEBVIEW2) if part)


def ecrans_webview(webview: Any) -> list[Ecran]:
    try:
        return [(int(e.x), int(e.y), int(e.width), int(e.height)) for e in webview.screens]
    except Exception:
        return []


def memoriser_fenetre(stockage: Stockage, fenetre: Any) -> None:
    """Enregistre taille et position (réglage `fenetre`) ; sans effet si illisibles."""
    try:
        valeur = {
            "x": int(fenetre.x),
            "y": int(fenetre.y),
            "largeur": int(fenetre.width),
            "hauteur": int(fenetre.height),
        }
        stockage.ecrire_reglage("fenetre", valeur)
    except Exception as exc:
        LOGGER.error("fenêtre non mémorisée : %s", type(exc).__name__)


def lancer(
    *,
    webview: Any = None,
    stockage: Stockage | None = None,
    instance: InstanceUnique | None = None,
    fabrique_assemblage: Callable[..., Any] = assembler,
) -> int:
    """Lance l'application. Rend le code de sortie (0 : normal, 0 aussi pour la seconde
    instance, qui remet la première au premier plan)."""
    chrono = Chrono()
    instance = instance if instance is not None else InstanceUnique()
    if not instance.acquerir():
        return 0
    try:
        if webview is None:
            import webview as webview_reel

            webview = webview_reel
        dossier = dossier_donnees()
        dossier.mkdir(parents=True, exist_ok=True)
        stockage = stockage if stockage is not None else Stockage()
        os.environ[VARIABLE_ARGUMENTS] = arguments_navigateur(
            os.environ.get(VARIABLE_ARGUMENTS, "")
        )
        hotes = frozenset(h.lower().rstrip(".") for h in charger_liste_blanche().hotes)
        geo = geometrie_initiale(stockage.lire_reglage("fenetre"), ecrans_webview(webview))
        differe = PontDiffere()
        with tempfile.TemporaryDirectory(prefix="assistantsp-ui-") as temporaire:
            index = preparer_interface(Path(temporaire) / "ui")
            fenetre = webview.create_window(
                TITRE,
                url=str(index),
                js_api=differe,
                width=geo["largeur"],
                height=geo["hauteur"],
                x=geo["x"],
                y=geo["y"],
                min_size=(MIN_LARGEUR, MIN_HAUTEUR),
                text_select=True,
            )
            demarrage = Demarrage(
                stockage, fenetre, differe, fabrique_assemblage=fabrique_assemblage, chrono=chrono
            )

            def origine() -> str | None:
                url = getattr(fenetre, "real_url", None)
                return urlsplit(url).netloc.lower() if url else None

            garde = GardeNavigation(origine, hotes)
            fenetre.events.shown += lambda: brancher_garde(fenetre, garde)
            fenetre.events.shown += lambda: chrono.fenetre()
            fenetre.events.loaded += demarrage.page_chargee
            fenetre.events.closing += lambda: memoriser_fenetre(stockage, fenetre)
            demarrage.demarrer()
            try:
                webview.start(
                    http_server=True,
                    private_mode=False,
                    storage_path=str(dossier / "webview"),
                )
            finally:
                demarrage.arreter()
        return 0
    finally:
        instance.liberer()


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    if sys.platform != "win32":
        print("L'application ne fonctionne que sous Windows.", file=sys.stderr)  # noqa: T201
        return 2
    return lancer()


__all__ = ["Demarrage", "InstanceUnique", "PontDiffere", "decider_navigation", "lancer", "main"]
