"""Story 13.1 : vue Correction avec différences visibles, dans Edge avec un pont factice.

Marqués `ui`. Chaînes factices (D1) ; les segments injectés sont calculés par le vrai module
Python `slmsp.app.pont.redaction_outils`.
"""

from __future__ import annotations

import functools
import http.server
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

from slmsp.app.pont.redaction_outils import PontRedactionOutils

playwright_sync = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.ui

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"
FIN = {"type": "fin", "raison": "terminee", "usage": None, "urls_inventees": []}
AVANT = "<mot-1> <mot-2> <mot-3>"
APRES = "<mot-1> <mot-x> <mot-3> <mot-4>"


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="module")
def base() -> Iterator[str]:
    gestionnaire = functools.partial(_Silencieux, directory=str(UI))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{serveur.server_port}/index.html"
    serveur.shutdown()
    serveur.server_close()


@pytest.fixture(scope="module")
def navigateur() -> Iterator[object]:
    with playwright_sync.sync_playwright() as p:
        try:
            nav = p.chromium.launch(channel="msedge", headless=True)
        except Exception as erreur:
            pytest.skip(f"Edge indisponible : {erreur}")
        yield nav
        nav.close()


@pytest.fixture
def page(navigateur, base) -> Iterator[object]:
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 800})
    contexte.add_init_script(
        "try { localStorage.setItem('slmsp.bienvenue-vue', 'true'); } catch {}"
    )
    p = contexte.new_page()
    p.set_default_timeout(90_000)
    p.requetes = []
    p.on("request", lambda r: p.requetes.append(r.url))
    p.goto(base + "?pont=factice")
    p.wait_for_function("() => window.slmsp !== undefined", polling=50)
    p.evaluate(
        """() => {
          window.__copies = [];
          Object.defineProperty(navigator, 'clipboard', {
            value: { writeText: async (t) => { window.__copies.push(t); } },
          });
          window.__appels = [];
          const pont = window.slmsp.pont;
          pont.envoyer = async (tache, messages, options) => {
            window.__appels.push(['envoyer', tache, messages, options]);
            window.slmsp.bus.emettre('generation:debut', { tache });
            setTimeout(() => window.slmspRecevoir(window.__flux), 20);
            return { ok: true };
          };
          pont.appeler = async (nom, ...args) => {
            window.__appels.push([nom, ...args]);
            if (window.__echec) return { ok: false, erreur: { code: 'x', message: '<refus>' } };
            return window.__diff;
          };
        }"""
    )
    yield p
    p.context.close()


def _corriger(page, apres: str = APRES, avant: str = AVANT, raison: str = "terminee") -> None:
    differences = PontRedactionOutils().appeler("differences", avant, apres)
    page.evaluate("window.slmspRecevoir({type: 'pret'})")
    page.evaluate("(t) => window.slmsp.activer(t)", "CO")
    page.evaluate(
        "([f, d]) => { window.__flux = f; window.__diff = d; }",
        [[{"type": "jeton", "texte": apres}, {**FIN, "raison": raison}], differences],
    )
    page.fill("#redaction-saisie-CO", avant)
    page.locator("#vue-CO .volet-pied .bouton-primaire").click()
    page.wait_for_function(
        "() => !document.querySelector('#vue-CO .resultat-actions').hidden", polling=50
    )


def _decoration(page, selecteur: str) -> str:
    return page.eval_on_selector(selecteur, "e => getComputedStyle(e).textDecorationLine")


def test_vue_disponible_et_action_corriger(page) -> None:
    page.evaluate("(t) => window.slmsp.activer(t)", "CO")
    vue = page.locator("#vue-CO")
    assert vue.locator(".redaction .volet-entree").is_visible()
    assert "non disponible" not in vue.inner_text()
    assert vue.locator(".volet-pied .bouton-primaire").inner_text() == "Corriger"


def test_insertions_et_suppressions_marquees_sans_couleur(page) -> None:
    _corriger(page)
    page.wait_for_selector("#vue-CO .resultat ins.diff-insert")
    zone = page.locator("#vue-CO .resultat")
    assert zone.locator("del.diff-delete").count() == 1
    assert zone.locator("ins.diff-insert").count() == 2
    # Soulignement et barré : lisibles sans la couleur.
    assert _decoration(page, "#vue-CO ins.diff-insert") == "underline"
    assert _decoration(page, "#vue-CO del.diff-delete") == "line-through"
    # Texte annoncé au lecteur d'écran, présent dans le DOM mais hors de l'écran.
    assert "[suppression :" in page.locator("#vue-CO .diff-delete").text_content()
    assert "[ajout :" in page.locator("#vue-CO .diff-insert").first.text_content()
    assert "1 suppression" in page.locator("#vue-CO .diff-resume").inner_text()
    appels = [a for a in page.evaluate("window.__appels") if a[0].startswith("redaction_outils")]
    assert appels == [["redaction_outils.differences", AVANT, APRES]]


def test_copier_la_version_corrigee_brute(page) -> None:
    _corriger(page)
    page.wait_for_selector("#vue-CO .resultat ins.diff-insert")
    page.locator("#vue-CO .resultat-actions .bouton-primaire").click()
    assert page.evaluate("window.__copies") == [APRES]


def test_textes_identiques_aucune_correction(page) -> None:
    _corriger(page, apres=AVANT)
    page.wait_for_selector("#vue-CO .diff-resume:has-text('Aucune correction')")
    assert page.locator("#vue-CO .resultat ins, #vue-CO .resultat del").count() == 0
    assert page.locator("#vue-CO .resultat").inner_text() == AVANT


def test_echec_du_calcul_garde_le_texte_corrige(page) -> None:
    page.evaluate("window.__echec = true")
    _corriger(page)
    page.wait_for_selector("#vue-CO .diff-resume:has-text('pas pu être affichées')")
    assert page.locator("#vue-CO .resultat").inner_text() == APRES
    page.locator("#vue-CO .resultat-actions .bouton-primaire").click()
    assert page.evaluate("window.__copies") == [APRES]


def test_resultat_interrompu_sans_differences(page) -> None:
    _corriger(page, raison="interrompue")
    assert page.locator("#vue-CO .diff-resume").count() == 0
    assert page.locator("#vue-CO .resultat").inner_text() == APRES


def test_aucun_html_injecte_ni_ressource_externe(page) -> None:
    piege = "<img src=x onerror=window.__pwn=1> <b>gras</b>"
    _corriger(page, apres=piege)
    page.wait_for_selector("#vue-CO .resultat ins.diff-insert")
    assert page.locator("#vue-CO .resultat img, #vue-CO .resultat b").count() == 0
    assert page.evaluate("window.__pwn") is None
    assert all(u.startswith(("http://127.0.0.1", "data:")) for u in page.requetes)
