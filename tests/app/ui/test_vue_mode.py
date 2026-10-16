"""Story 12.9 : vue « mode » (pastille, menu, journal) dans Edge, avec un pont pywebview simulé.

Marqués `ui` : `uv run pytest -m ui tests/app/ui/test_vue_mode.py`.
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
PONT_SIMULE = """
(() => {
  const etat = { hors_ligne: false, force: false };
  window.__appels = [];
  window.__etat = etat;
  window.__journal = [];
  const reponse = () => ({ ok: true, mode: etat.hors_ligne ? 'hors_ligne' : 'connecte', ...etat });
  window.pywebview = { api: {
    async appeler(nom, ...args) {
      window.__appels.push([nom, ...args]);
      if (nom === 'mode.etat') return reponse();
      if (nom === 'mode.forcer_hors_ligne') {
        etat.force = args[0];
        etat.hors_ligne = args[0] || etat.hors_ligne;
        return reponse();
      }
      if (nom === 'mode.journal') return { ok: true, entrees: window.__journal };
      if (nom === 'mode.effacer_journal') { window.__journal = []; return { ok: true }; }
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
    p.wait_for_function(
        "() => document.querySelector('#mode-pastille .mode-texte')?.textContent === 'Connecté'",
        polling=50,
    )
    yield p
    contexte.close()


def _pousser(page, **etat) -> None:
    page.evaluate(
        "(e) => window.slmspRecevoir("
        "{ type: 'mode', mode: e.hors_ligne ? 'hors_ligne' : 'connecte', ...e })",
        etat,
    )


def _annonces(page) -> list[str]:
    return page.evaluate("window.__annonces")


def test_pastille_suit_le_mode_avec_une_seule_annonce(page) -> None:
    page.evaluate(
        """() => { window.__annonces = [];
          new MutationObserver(() => {
            const t = document.getElementById('annonces').textContent;
            if (t) window.__annonces.push(t);
          }).observe(document.getElementById('annonces'),
            { childList: true, characterData: true, subtree: true });
          window.__changes = [];
          window.slmsp.bus.abonner('mode:change', (e) => window.__changes.push(e)); }"""
    )
    texte = page.locator("#mode-pastille .mode-texte")
    _pousser(page, hors_ligne=True, force=False)
    page.wait_for_function(
        "() => document.querySelector('.mode-texte').textContent === 'Hors ligne'"
    )
    _pousser(page, hors_ligne=True, force=False)  # inchangé : aucune seconde annonce
    _pousser(page, hors_ligne=True, force=True)
    page.wait_for_function(
        "() => document.querySelector('.mode-texte').textContent === 'Hors ligne (choisi)'"
    )
    page.wait_for_timeout(500)
    assert texte.inner_text() == "Hors ligne (choisi)"
    assert _annonces(page) == ["Mode : Hors ligne", "Mode : Hors ligne (choisi)"]
    assert page.evaluate("window.__changes") == [{"hors_ligne": True}]


def test_menu_rester_hors_ligne_appelle_le_pont(page) -> None:
    page.click("#mode-pastille")
    assert page.get_attribute("#mode-pastille", "aria-expanded") == "true"
    assert (
        page.locator("#mode-menu [role=menuitemcheckbox]").get_attribute("aria-checked") == "false"
    )
    page.click("text=Rester hors ligne")
    page.wait_for_function(
        "() => document.querySelector('.mode-texte').textContent === 'Hors ligne (choisi)'"
    )
    assert ["mode.forcer_hors_ligne", True] in page.evaluate("window.__appels")
    page.click("#mode-pastille")
    assert (
        page.locator("#mode-menu [role=menuitemcheckbox]").get_attribute("aria-checked") == "true"
    )
    page.keyboard.press("Escape")
    assert page.locator("#mode-menu").is_hidden()
    assert page.evaluate("document.activeElement.id") == "mode-pastille"


def test_journal_vide_puis_rempli_puis_efface(page) -> None:
    page.click("#mode-pastille")
    page.click("text=Journal des requêtes sortantes")
    assert "Aucune requête sortante" in page.locator(".mode-journal").inner_text()
    page.click(".mode-journal >> text=Fermer")
    page.evaluate(
        """() => { window.__journal = [
          { horodatage: '2026-01-01T10:00:00+00:00', profil: 'assistant', hote: '<hote-factice>',
            methode: 'GET', outil: null, termes: '<termes-factices>',
            statut: 'bloquee-liste', mode: null } ]; }"""
    )
    page.click("#mode-pastille")
    page.click("text=Journal des requêtes sortantes")
    en_tetes = page.locator(".mode-table th").all_inner_texts()
    assert en_tetes == ["Heure", "Hôte", "Termes", "Statut"]
    ligne = page.locator(".mode-table tbody tr").inner_text()
    assert "<hote-factice>" in ligne and "<termes-factices>" in ligne
    assert "Bloquée (hôte hors liste)" in ligne
    page.click("text=Effacer le journal")
    page.wait_for_function(
        "() => document.querySelector('.mode-journal').textContent.includes('Aucune requête')"
    )
    assert ["mode.effacer_journal"] in page.evaluate("window.__appels")


def test_echec_du_forcage_est_annonce_et_l_interrupteur_retabli(page) -> None:
    page.evaluate(
        """() => {
          const api = window.pywebview.api, appeler = api.appeler;
          api.appeler = async (nom, ...a) => nom === 'mode.forcer_hors_ligne'
            ? { ok: false, erreur: { code: 'x', message: 'refus' } } : appeler(nom, ...a);
        }"""
    )
    page.click("#mode-pastille")
    page.click("text=Rester hors ligne")
    page.wait_for_function("() => document.body.textContent.includes('a échoué')")
    page.click("#mode-pastille")
    assert page.get_attribute("#mode-menu [role=menuitemcheckbox]", "aria-checked") == "false"
