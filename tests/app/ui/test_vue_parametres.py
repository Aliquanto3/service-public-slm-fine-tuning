"""Story 12.10 : vue « parametres » (onglets, À propos, taille, effacement) dans Edge, pont simulé.

Marqués `ui` : `uv run pytest -m ui tests/app/ui/test_vue_parametres.py`.
"""

# ruff: noqa: E501 (scripts JavaScript et sélecteurs en chaînes)
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
PONT_SIMULE = """
(() => {
  window.__appels = [];
  window.__apropos = {
    ok: true,
    application: { version: '<version-factice>', empreinte: null },
    modele: { slug: '<modele-factice>', sha256_attendu: '<empreinte-factice>' },
    index: { version: '20260101', date_snapshot: '2026-01-01', nb_chunks: 3 },
    liste_blanche: ['a.example', 'b.example'],
    licences: { statut: 'provisoire', composants: [{ nom: '<composant-factice>', licence: '<licence-factice>' }] },
    hors_passerelle: [{ composant: '<composant-hors-passerelle>', detail: '<detail-factice>' }],
    mentions: { avertissement_juridique: '<avertissement-factice>', mise_a_jour: '<maj-factice>', donnees: '<donnees-factices>' },
  };
  window.pywebview = { api: {
    async appeler(nom, ...args) {
      window.__appels.push([nom, ...args]);
      if (nom === 'mode.etat') return { ok: true, mode: 'connecte', hors_ligne: false, force: false };
      if (nom === 'mode.forcer_hors_ligne') {
        return { ok: true, mode: 'hors_ligne', hors_ligne: args[0], force: args[0] };
      }
      if (nom === 'reglages.lire') return { ok: true, reglages: { taille_texte: 100 } };
      if (nom === 'reglages.a_propos') return window.__apropos;
      return { ok: true };
    },
    async envoyer() { return { ok: true }; },
    async arreter() { return { ok: true }; },
  } };
})();
"""


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
    contexte.add_init_script(PONT_SIMULE)
    p = contexte.new_page()
    p.set_default_timeout(90_000)
    p.goto(base)
    p.wait_for_function("() => window.slmsp !== undefined", polling=50)
    yield p
    contexte.close()


def _appels(page, nom: str) -> list[list[object]]:
    return [a for a in page.evaluate("window.__appels") if a[0] == nom]


def _ouvrir(page, onglet: str | None = None) -> None:
    page.click("#bouton-parametres")
    page.wait_for_selector("#dialogue-parametres[open] .parametres-onglet")
    if onglet:
        page.click(f"#parametres-onglet-{onglet}")


def test_trois_onglets_au_clavier_et_retours_dans_son_onglet(page) -> None:
    _ouvrir(page)
    assert page.locator(".parametres-onglet").all_inner_texts() == [
        "Général",
        "Retours",
        "À propos",
    ]
    page.focus("#parametres-onglet-general")
    page.keyboard.press("ArrowRight")
    assert page.evaluate("document.activeElement.id") == "parametres-onglet-retours"
    assert page.get_attribute("#parametres-onglet-retours", "aria-selected") == "true"
    assert page.locator("#parametres-panneau-retours #ancre-retours").count() == 1
    assert page.locator("#parametres-panneau-general").is_hidden()


def test_a_propos_affiche_versions_liste_licences_et_mentions(page) -> None:
    _ouvrir(page, "apropos")
    panneau = page.locator("#parametres-panneau-apropos")
    panneau.get_by_text("<version-factice>").wait_for()
    texte = panneau.inner_text()
    assert "<modele-factice>" in texte
    assert "1 janvier 2026" in texte
    assert page.locator(".parametres-hotes li").all_inner_texts() == ["a.example", "b.example"]
    assert "<composant-factice> : <licence-factice>" in texte
    assert "Liste provisoire" in texte
    assert "<composant-hors-passerelle>" in texte  # Q1 : ce qui sort hors passerelle
    assert "<avertissement-factice>" in texte
    # Empreinte de l'application absente : affichée proprement, sans « null ».
    ligne = panneau.locator(".parametres-ligne", has_text="Empreinte de l'application")
    assert ligne.locator("dd").inner_text() == "non disponible"
    assert "null" not in texte


def test_a_propos_relit_la_liste_a_la_reouverture(page) -> None:
    _ouvrir(page, "apropos")
    page.locator(".parametres-hotes li").first.wait_for()
    page.evaluate("document.getElementById('dialogue-fermer').click()")
    page.evaluate("window.__apropos = { ...window.__apropos, liste_blanche: ['c.example'] }")
    page.click("#bouton-parametres")
    page.wait_for_function(
        "() => [...document.querySelectorAll('.parametres-hotes li')].map(e => e.textContent).join() === 'c.example'"
    )


def test_taille_du_texte_cinq_crans_memorises(page) -> None:
    _ouvrir(page)  # monte la vue, qui mémorise les crans côté pont
    page.keyboard.press("Escape")
    vus = []
    for _ in range(6):
        page.keyboard.press("Control+=")
        vus.append(page.evaluate("document.documentElement.style.getPropertyValue('--echelle')"))
    assert vus == ["112%", "125%", "137%", "150%", "150%", "150%"]
    page.wait_for_function(
        "() => window.__appels.some(a => a[0] === 'reglages.ecrire' && a[2] === 150)"
    )
    page.keyboard.press("Control+0")
    assert page.evaluate("document.documentElement.style.getPropertyValue('--echelle')") == "100%"
    assert page.evaluate("JSON.parse(localStorage.getItem('slmsp.echelle'))") == 100


def test_boutons_de_taille_dans_general(page) -> None:
    _ouvrir(page)
    page.click("button[aria-label='Agrandir le texte']")
    assert page.locator(".parametres-taille-valeur").inner_text() == "112 %"
    page.wait_for_function(
        "() => window.__appels.some(a => a[0] === 'reglages.ecrire' && a[1] === 'taille_texte' && a[2] === 112)"
    )
    page.click("button:has-text('100 %')")
    assert page.locator(".parametres-taille-valeur").inner_text() == "100 %"


def test_rester_hors_ligne_appelle_le_mode(page) -> None:
    _ouvrir(page)
    page.check("#parametres-hors-ligne")
    page.wait_for_function(
        "() => window.__appels.some(a => a[0] === 'mode.forcer_hors_ligne' && a[1] === true)"
    )
    assert page.is_checked("#parametres-hors-ligne")


def test_effacer_historique_apres_5_secondes(page) -> None:
    _ouvrir(page)
    page.click("#parametres-effacer")
    assert page.locator(".parametres-confirmation").is_visible()
    assert _appels(page, "reglages.effacer_historique") == []
    page.wait_for_function(
        "() => window.__appels.some(a => a[0] === 'reglages.effacer_historique')",
        timeout=15_000,
    )


def test_effacer_historique_annule_ne_vide_rien(page) -> None:
    _ouvrir(page)
    page.click("#parametres-effacer")
    page.click("#parametres-effacer-annuler")
    assert page.evaluate("document.activeElement.id") == "parametres-effacer"
    page.wait_for_timeout(5500)
    assert _appels(page, "reglages.effacer_historique") == []
    assert page.locator("#parametres-effacer").is_enabled()
