"""Story 13.6 : bouton « Vérifier en ligne » de la vue Question, dans Edge avec un pont factice.

Marqués `ui` : `uv run pytest -m ui tests/app/ui`. Chaînes factices (D1), aucune ressource externe.
"""

from __future__ import annotations

import functools
import http.server
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.ui

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"

URL_1 = "https://exemple.invalid/source-1"
SOURCE_INDEX = {
    "numero": 1,
    "titre": "<titre-factice-1>",
    "url": URL_1,
    "origine": "index",
    "date": "2026-10-03",
    "extrait": None,
}
SOURCE_MCP = {**SOURCE_INDEX, "origine": "mcp", "url": "https://www.data.gouv.fr/datasets/factice"}
PAGE = {
    "numero": None,
    "titre": "<titre-page-factice>",
    "url": URL_1,
    "origine": "verification",
    "date": "2026-10-17T09:30:00+00:00",
    "extrait": "<extrait-page-factice>",
}
FIN = {"type": "fin", "raison": "terminee", "usage": None, "urls_inventees": []}


def _flux(source: dict, texte: str = "voir [1].") -> list[dict]:
    return [
        {"type": "jeton", "texte": texte},
        {"type": "sources", "sources": [source]},
        FIN,
    ]


def _verdict(verdict: str, phrase: str = "<phrase-factice>", extrait: str | None = None) -> dict:
    return {
        "type": "verification",
        "url": URL_1,
        "titre": "<titre-page-factice>",
        "date_consultation": "2026-10-17T09:30:00+00:00",
        "verdict": verdict,
        "phrase": phrase,
        "extrait": extrait,
    }


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
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 720})
    contexte.add_init_script(
        "try { localStorage.setItem('slmsp.bienvenue-vue', 'true'); } catch {}"
    )
    p = contexte.new_page()
    p.set_default_timeout(90_000)
    p.requetes = []
    p.on("request", lambda r: p.requetes.append(r.url))
    p.goto(base + "?pont=factice")
    p.wait_for_function("() => window.slmsp !== undefined", polling=50)
    # `envoyer` rejoue `window.__flux` ; `verification.verifier` attend `window.__liberer(valeur)`.
    p.evaluate(
        """() => {
          window.__appels = [];
          const pont = window.slmsp.pont;
          pont.envoyer = async (tache) => {
            window.slmsp.bus.emettre('generation:debut', { tache });
            setTimeout(() => window.slmspRecevoir(window.__flux), 20);
            return { ok: true };
          };
          const ancien = pont.appeler;
          pont.appeler = (nom, ...args) => {
            window.__appels.push([nom, ...args]);
            if (nom === 'mode.etat') return Promise.resolve({ ok: false });
            if (nom === 'verification.verifier') {
              return new Promise((resolve, reject) => {
                window.__liberer = resolve;
                window.__echouer = reject;
              });
            }
            return ancien(nom, ...args);
          };
        }"""
    )
    yield p
    p.context.close()


def _poser(page, flux: list[dict], connecte: bool = True) -> None:
    page.evaluate("window.slmspRecevoir({type: 'pret'})")
    page.evaluate("(t) => window.slmsp.activer(t)", "Q")
    page.evaluate("(h) => window.slmsp.bus.emettre('mode:change', { hors_ligne: h })", not connecte)
    page.evaluate("(f) => { window.__flux = f; }", flux)
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.wait_for_function("() => !!document.querySelector('.reponse-actions:not([hidden])')")


def _liberer(page, evenements: list[dict]) -> None:
    page.evaluate("(e) => window.__liberer({ ok: true, evenements: e })", evenements)


def test_hors_ligne_le_bouton_n_existe_pas(page) -> None:
    _poser(page, _flux(SOURCE_INDEX), connecte=False)
    assert page.locator("#vue-Q .verification button").count() == 0
    assert page.locator("#vue-Q .verification").inner_text() == ""


def test_pas_de_bouton_sans_source_de_l_index_citee(page) -> None:
    _poser(page, _flux(SOURCE_MCP))
    assert page.locator("#vue-Q .verification button").count() == 0


def test_pas_de_bouton_si_la_source_n_est_pas_citee(page) -> None:
    _poser(page, _flux(SOURCE_INDEX, texte="<réponse-factice-1> sans citation."))
    assert page.locator("#vue-Q .verification button").count() == 0


def test_concordant_etat_en_cours_verdict_focus_et_panneau_sources(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    bouton = page.locator("#vue-Q .verification button")
    assert bouton.inner_text() == "Vérifier en ligne"
    assert not any(a[0] == "verification.verifier" for a in page.evaluate("window.__appels"))
    bouton.click()
    zone = page.locator("#vue-Q .verification-resultat")
    assert zone.inner_text() == "Vérification en cours…"
    assert zone.get_attribute("role") == "status"
    assert bouton.get_attribute("aria-disabled") == "true"  # pas `disabled` : le focus reste
    assert bouton.get_attribute("aria-busy") == "true"
    assert page.evaluate(
        "document.activeElement === document.querySelector('.verification button')"
    )
    appel = next(a for a in page.evaluate("window.__appels") if a[0] == "verification.verifier")
    assert appel[1] == "voir [1]."
    assert appel[2][0]["url"] == URL_1
    _liberer(page, [_verdict("concordant"), {"type": "sources", "sources": [PAGE]}])
    page.wait_for_selector(".verification-concordant")
    texte = page.locator("#vue-Q .verification-concordant").inner_text()
    assert texte.startswith("Vérifié sur <titre-page-factice> le ")
    assert "2026" in texte and texte.endswith(": concordant")
    assert page.evaluate("document.activeElement.classList.contains('verification-resultat')")
    assert bouton.get_attribute("aria-busy") is None
    assert not page.locator("#annonces").inner_text().endswith(": concordant")  # le focus suffit
    page.click("#bouton-sources")
    cartes = page.locator("#sources-corps .source-card")
    assert cartes.count() == 2
    meta = cartes.nth(1).locator(".source-meta").inner_text()
    assert meta.startswith("Vérifiée en ligne · Consultée le ")
    assert cartes.nth(1).locator(".source-extrait").text_content() == "<extrait-page-factice>"


def test_focus_ailleurs_ni_deplace_ni_vole_et_annonce_une_fois(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    page.focus("#saisie")
    _liberer(page, [_verdict("concordant")])
    page.wait_for_function(
        "() => document.getElementById('annonces').textContent.endsWith(': concordant')"
    )
    assert page.evaluate("document.activeElement.id") == "saisie"


def test_clics_repetes_une_seule_verification_puis_delai_de_30_s(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    bouton = page.locator("#vue-Q .verification button")
    clic = "() => document.querySelector('#vue-Q .verification button').click()"
    page.evaluate(clic)
    page.evaluate(clic)  # pendant l'attente : ignoré
    nb = "() => window.__appels.filter((a) => a[0] === 'verification.verifier').length"
    assert page.evaluate(nb) == 1
    _liberer(page, [_verdict("concordant")])
    page.wait_for_selector(".verification-concordant")
    page.evaluate(clic)  # moins de 30 s après : ignoré
    assert page.evaluate(nb) == 1
    assert bouton.get_attribute("aria-disabled") == "true"
    page.evaluate("() => { const d = Date.now(); Date.now = () => d + 31000; }")
    page.evaluate(clic)
    assert page.evaluate(nb) == 2


def test_generation_en_cours_message_dedie_et_reessai_immediat(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    page.evaluate("() => window.__liberer({ ok: false, erreur: { code: 'generation-en-cours' } })")
    zone = page.locator("#vue-Q .verification-resultat.callout-warning")
    zone.wait_for()
    assert zone.inner_text() == "Une réponse est en cours : réessayez à la fin de celle-ci."
    assert page.locator("#vue-Q .verification button").get_attribute("aria-disabled") is None


def test_reponse_trop_longue_message_dedie_sans_appel_au_pont(page) -> None:
    _poser(page, _flux(SOURCE_INDEX, texte="a" * 20001 + " [1]"))
    page.click("#vue-Q .verification button")
    zone = page.locator("#vue-Q .verification-resultat.callout-warning")
    zone.wait_for()
    assert zone.inner_text() == "Cette réponse est trop longue pour être vérifiée en ligne."
    assert not any(a[0] == "verification.verifier" for a in page.evaluate("window.__appels"))


def test_la_page_verifiee_n_entre_pas_dans_l_historique(page) -> None:
    page.evaluate(
        "() => { window.__tours = []; window.slmsp.bus.abonner('conversation:tours',"
        " (c) => window.__tours.push(c.tours.map((t) => t.sources.map((s) => s.origine)))); }"
    )
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    _liberer(page, [_verdict("concordant"), {"type": "sources", "sources": [PAGE]}])
    page.wait_for_selector(".verification-concordant")
    page.click("#bouton-sources")
    assert page.locator("#sources-corps .source-card").count() == 2  # visible dans le panneau
    page.fill("#saisie", "<question-factice-2>")  # le prochain `fin` republie tous les tours
    page.keyboard.press("Enter")
    page.wait_for_function("() => window.__tours.length >= 2")
    dernier = page.evaluate("window.__tours.at(-1)")
    assert dernier[0] == ["index"]  # premier tour : sans la page vérifiée
    assert all(
        "verification" not in origines
        for tour in page.evaluate("window.__tours")
        for origines in tour
    )


def test_difference_dans_un_callout_avec_extrait(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    _liberer(page, [_verdict("difference", "<phrase-factice>", "<passage-factice>")])
    zone = page.locator("#vue-Q .verification-resultat.callout-warning")
    zone.wait_for()
    assert zone.locator("p").first.inner_text() == "Différence relevée : <phrase-factice>"
    assert zone.locator(".verification-extrait").text_content() == "<passage-factice>"
    page.click("#bouton-sources")
    assert page.locator("#sources-corps .source-card").count() == 1  # page non lue : pas de carte


def test_indisponible_n_empeche_pas_de_continuer(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    _liberer(page, [_verdict("indisponible", "<phrase-indisponible-factice>")])
    zone = page.locator("#vue-Q .verification-resultat.callout-warning")
    zone.wait_for()
    assert zone.inner_text() == "<phrase-indisponible-factice>"
    assert page.is_enabled("#saisie")
    assert (
        page.locator("#vue-Q .verification button").get_attribute("aria-disabled") == "true"
    )  # délai 30 s


def test_refus_du_pont_rend_un_message_sans_bloquer(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    page.evaluate("() => window.__echouer(new Error('refus'))")
    zone = page.locator("#vue-Q .verification-resultat.callout-warning")
    zone.wait_for()
    assert zone.inner_text() == "La vérification n'a pas pu être lancée."


def test_passage_hors_ligne_retire_le_bouton_et_le_resultat_tardif(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    page.evaluate("window.slmsp.bus.emettre('mode:change', { hors_ligne: true })")
    assert page.locator("#vue-Q .verification button").count() == 0
    _liberer(page, [_verdict("concordant")])
    page.wait_for_timeout(100)
    assert page.locator("#vue-Q .verification-resultat").count() == 0


def test_contenu_non_interprete_comme_html(page) -> None:
    _poser(page, _flux(SOURCE_INDEX))
    page.click("#vue-Q .verification button")
    piege = "<img src=x onerror=window.__pwned=1>"
    _liberer(page, [_verdict("difference", piege, piege)])
    page.wait_for_selector(".verification-resultat.callout-warning")
    assert page.evaluate("window.__pwned") is None
    assert page.locator("#vue-Q .verification-resultat img").count() == 0
    assert not [u for u in page.requetes if not u.startswith("http://127.0.0.1")]


def test_pas_d_innerhtml_dans_le_module() -> None:
    module = (UI / "js" / "vues" / "verification.js").read_text(encoding="utf-8")
    assert "innerHTML" not in module and "insertAdjacentHTML" not in module
