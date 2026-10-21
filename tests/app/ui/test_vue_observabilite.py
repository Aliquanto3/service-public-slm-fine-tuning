"""Story 17.6 : onglet « Observabilité » et ligne « Détails » sous une réponse, dans Edge.

Marqués `ui` : `uv run pytest -m ui tests/app/ui/test_vue_observabilite.py`. Pont simulé ;
valeurs factices seulement (D1).
"""

from __future__ import annotations

import functools
import http.server
import json
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.ui

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"
LIGNE = {
    "fournisseur": "ovh",
    "modele": "<modele-factice>",
    "appels": 2,
    "sauts": 1,
    "tokens_entree": 1200,
    "tokens_sortie": 300,
    "estime": False,
    "cout_eur": 0.0012,
    "energie_wh": 0.7,
    "energie_wh_bas": 0.6,
    "energie_wh_haut": 0.9,
    "co2e_g": 0.04,
    "co2e_g_bas": 0.03,
    "co2e_g_haut": 0.05,
    "debit_tokens_s": 30.0,
}
SYNTHESE = {
    "ok": True,
    "synthese": {
        "mois": "2026-10",
        "jour": "2026-10-21",
        "par_modele_jour": [LIGNE],
        "par_modele_mois": [LIGNE, {**LIGNE, "fournisseur": "local", "modele": "<slug>"}],
        "plafonds": [
            {
                "hote": "h.example",
                "libelle": "<fournisseur-factice>",
                "cumul_eur": 1.5,
                "plafond_eur": 2.0,
                "sauts": 1,
            }
        ],
        "derniers": [
            {
                "horodatage": "2026-10-21T10:00:00+00:00",
                "tache": "Q",
                "fournisseur": "ovh",
                "modele": "=<formule-factice>",
                "tokens_entree": 10,
                "tokens_sortie": 5,
                "estime": True,
                "duree_ms": 1500,
                "cout_eur": None,
                "co2e_g": None,
                "motif": None,
            }
        ],
    },
}
DETAILS = {
    "appels": 1,
    "tokens_entree": 42,
    "tokens_sortie": 7,
    "estime": False,
    "duree_ms": 2500,
    "cout_eur": 0.0,
    "local": True,
    "modeles": ["<slug>"],
    "energie_wh": 0.02,
    "energie_wh_bas": 0.01,
    "energie_wh_haut": 0.03,
    "co2e_g": 0.001,
    "co2e_g_bas": 0.0005,
    "co2e_g_haut": 0.0015,
    "motifs": [],
}
PONT_SIMULE = """
(() => {
  window.__appels = [];
  window.pywebview = { api: {
    async appeler(nom, ...args) {
      window.__appels.push([nom, ...args]);
      if (nom === 'observabilite.synthese') return window.__synthese;
      if (nom === 'observabilite.methode')
        return { ok: true, methode: { disponible: true, version: '<version-factice>',
          formules: ['<formule-a>'], cout: ['<cout-a>'], plafond: ['<plafond-a>'],
          zones: [{ libelle: '<zone>', intensite_g_kwh: 52, source: '<source>' }] } };
      if (nom === 'observabilite.exporter_csv') return { ok: true, enregistre: true, nom: 'x.csv' };
      if (nom.startsWith('mode.'))
        return { ok: true, mode: 'connecte', hors_ligne: false, force: false, entrees: [] };
      return { ok: true };
    },
    async envoyer() {
      setTimeout(() => window.slmspRecevoir([{ type: 'jeton', texte: '<réponse-factice-1>' },
        { type: 'fin', raison: 'terminee', usage: null, urls_inventees: [],
          details: window.__details }]), 20);
      return { ok: true };
    },
    async arreter() { return { ok: true }; },
  } };
  const pret = () => window.slmspRecevoir
    ? window.slmspRecevoir({ type: 'pret' }) : setTimeout(pret, 20);
  setTimeout(pret, 20);
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
    contexte.add_init_script(f"window.__synthese = {json.dumps(SYNTHESE)};")
    contexte.add_init_script(f"window.__details = {json.dumps(DETAILS)};")
    contexte.add_init_script(PONT_SIMULE)
    p = contexte.new_page()
    p.set_default_timeout(20_000)
    p.goto(base)
    p.wait_for_function("() => window.slmsp !== undefined", polling=50)
    yield p
    contexte.close()


def test_onglet_observabilite(page) -> None:
    assert page.locator("#tache-OB").count() == 1
    page.evaluate("window.slmsp.activer('OB')")
    page.wait_for_selector("#vue-OB .observabilite-table")
    texte = page.locator("#vue-OB").inner_text()
    assert "estimations" in texte
    assert "<fournisseur-factice> : 1,5000 € sur 2,00 €" in texte
    assert "0,0012 €" in texte and "30,0 tokens/s" in texte
    assert "0 € (modèle local" in texte  # ligne locale du mois
    assert "=<formule-factice>" in texte and "inconnu (tarif absent)" in texte
    assert page.locator("#vue-OB progress").count() == 1
    page.locator("#vue-OB button", has_text="Exporter en CSV").click()
    page.wait_for_function(
        "() => document.querySelector('#vue-OB .observabilite-etat').textContent.includes('x.csv')"
    )
    page.locator("#vue-OB .observabilite-methode summary").click()
    assert "<formule-a>" in page.locator("#vue-OB .observabilite-methode").inner_text()


def test_ligne_details_sous_la_reponse(page) -> None:
    page.fill("#saisie", "<question-factice>")
    page.click("#envoyer")
    page.wait_for_selector("#vue-Q .details-appel")
    bloc = page.locator("#vue-Q .details-appel")
    assert bloc.get_attribute("open") is None  # repliée par défaut
    bloc.locator("summary").click()
    texte = bloc.inner_text()
    assert "42 en entrée, 7 en sortie" in texte and "0 € (modèle local" in texte
    assert "Wh" in texte and "CO₂e" in texte
