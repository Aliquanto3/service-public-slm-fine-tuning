"""Story 17.5b : onglet « Modèles » (tableau trié, ligne dépliable, badges) dans Edge.

Marqués `ui` : `uv run pytest -m ui tests/app/ui/test_vue_modeles.py`. Le pont est simulé.
"""

from __future__ import annotations

import functools
import http.server
import json
import re
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.ui

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"
TACHES = ["Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"]
COMPARATIF = {
    "schema_version": 1,
    "genere_le": "2026-01-01T00:00:00+00:00",
    "jeu_version": "<jeu-factice>",
    "juge_principal": "<juge-factice>",
    "avertissements": ["<avertissement-factice-1>", "<avertissement-factice-2>"],
    "modeles": [
        {
            "id": "modele-a",
            "libelle": "<modele-factice-A>",
            "emplacement": "poste",
            "reference": True,
            "licence": "<licence-A>",
            "hebergement": "<hebergement-A>",
            "note": "",
            "qualite": {"score": 50.0, "bruit_items": 4.5, "taches": dict.fromkeys(TACHES, 50.0)},
            "ecart_reference": None,
            "cout": {"cout_api_eur": 0.0, "eur_pour_1000_demandes": None, "mention": ""},
            "vitesse": {
                "origine": "poste",
                "debit_tokens_s": 12.0,
                "premier_token_ms": 700.0,
                "ram_max_go": 4.0,
                "machine": "<machine-factice>",
                "mention": "",
            },
            "runs": {
                "notation": "<run-notation-A>",
                "generation": None,
                "mesure": "<run-mesure-A>",
            },
        },
        {
            "id": "modele-b",
            "libelle": "<modele-factice-B>",
            "emplacement": "cloud",
            "reference": False,
            "licence": "<licence-B>",
            "hebergement": "<script>window.__xss = 1</script>",
            "note": "",
            "qualite": {"score": 70.0, "bruit_items": 4.7, "taches": dict.fromkeys(TACHES, 70.0)},
            "ecart_reference": {"qualite": {"ecart": 20.0, "ic_bas": 12.0, "ic_haut": 25.0}},
            "cout": {
                "cout_api_eur": None,
                "eur_pour_1000_demandes": 1.5,
                "prix_mtok": {"modele_id": "<id-externe-factice>"},
                "mention": "<mention-cout>",
            },
            "vitesse": None,
            "runs": {"notation": "<run-notation-B>", "generation": "<run-gen-B>", "mesure": None},
        },
    ],
}
PONT_SIMULE = """
(() => {
  window.__appels = [];
  window.pywebview = { api: {
    async appeler(nom, ...args) {
      window.__appels.push([nom, ...args]);
      if (nom === 'modeles.comparatif_modeles') return window.__reponse;
      if (nom === 'reglages.modeles')
        return { ok: true, actif: 'modele-a', choisi: 'modele-a', modeles: [] };
      if (nom === 'reglages.fournisseurs_externes')
        return { ok: true, fournisseurs: [
          { id: 'x', modele: '<id-externe-factice>', actif: true }] };
      if (nom.startsWith('mode.'))
        return { ok: true, mode: 'connecte', hors_ligne: false, force: false, entrees: [] };
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


def _ouvrir(navigateur, base, reponse):
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 720})
    contexte.add_init_script(
        "try { localStorage.setItem('slmsp.bienvenue-vue', 'true'); } catch {}"
    )
    contexte.add_init_script(f"window.__reponse = {json.dumps(reponse)};")
    contexte.add_init_script(PONT_SIMULE)
    page = contexte.new_page()
    page.set_default_timeout(90_000)
    page.requetes = []
    page.on("request", lambda r: page.requetes.append(r.url))
    page.goto(base)
    page.wait_for_function("() => window.slmsp !== undefined", polling=50)
    page.evaluate("window.slmsp.activer('MO')")
    return page


@pytest.fixture
def page(navigateur, base) -> Iterator[object]:
    p = _ouvrir(navigateur, base, {"ok": True, "comparatif": COMPARATIF})
    p.wait_for_selector("#vue-MO .modeles-table")
    yield p
    p.context.close()


def _libelles(page) -> list[str]:
    return page.locator("#vue-MO .modeles-bascule").all_inner_texts()


def test_onglet_et_tableau(page) -> None:
    assert page.inner_text("#titre-tache") == "Modèles"
    assert page.get_attribute("#tache-MO", "aria-current") == "true"
    entetes = page.locator("#vue-MO thead th").all_inner_texts()
    assert entetes[:3] == ["Modèle", "Où il tourne", "Qualité (± bruit)"]
    assert len(entetes) == 9
    assert _libelles(page) == ["<modele-factice-A>", "<modele-factice-B>"]
    ligne_a = page.locator('[data-modele="modele-a"]').inner_text()
    assert "50,0 ± 4,5" in ligne_a and "Référence" in ligne_a and "0 € d'API" in ligne_a
    assert "12,0 tokens/s ; premier token 700 ms" in ligne_a and "4,0 Go" in ligne_a
    ligne_b = page.locator('[data-modele="modele-b"]').inner_text()
    assert "1,50 € / 1 000 demandes, relances comprises" in ligne_b
    assert "non mesurée" in ligne_b
    assert "+20,0 (IC 95 % : 12,0 à 25,0)" in ligne_b


def test_encadre_et_aucun_reseau(page) -> None:
    guide = page.locator("#vue-MO .modeles-guide").inner_text()
    assert "Comment lire ce tableau" in guide
    assert "<avertissement-factice-1>" in guide and "même jeu" in guide
    assert not [u for u in page.requetes if not u.startswith("http://127.0.0.1")]


def test_badges_actif_et_externe(page) -> None:
    ligne_a = page.locator('[data-modele="modele-a"]').inner_text()
    assert "Modèle actif sur ce poste" in ligne_a
    assert "Fournisseur" not in ligne_a
    assert "Fournisseur externe configuré" in page.locator('[data-modele="modele-b"]').inner_text()


def test_tri_au_clavier(page) -> None:
    page.locator('[data-colonne="qualite"]').focus()
    page.keyboard.press("Enter")
    assert page.get_attribute("#vue-MO th:nth-child(3)", "aria-sort") == "ascending"
    assert _libelles(page) == ["<modele-factice-A>", "<modele-factice-B>"]
    assert page.evaluate("document.activeElement.dataset.colonne") == "qualite"
    page.keyboard.press("Space")
    assert page.get_attribute("#vue-MO th:nth-child(3)", "aria-sort") == "descending"
    assert _libelles(page) == ["<modele-factice-B>", "<modele-factice-A>"]


def test_ligne_depliable_scores_et_runs(page) -> None:
    sous = page.locator("#modeles-detail-modele-b")
    assert sous.is_hidden()
    page.locator('[data-modele="modele-b"] .modeles-bascule').focus()
    page.keyboard.press("Enter")
    bascule = page.get_attribute('[data-modele="modele-b"] .modeles-bascule', "aria-expanded")
    assert bascule == "true"
    assert sous.is_visible()
    assert sous.locator(".modeles-barre").count() == 8
    largeur = page.evaluate(
        "document.querySelector('#modeles-detail-modele-b .modeles-barre-valeur').style.width"
    )
    assert largeur == "70%"
    texte = sous.inner_text()
    assert "<run-notation-B>" in texte and "<run-gen-B>" in texte
    assert "Run de mesure" not in texte


def test_valeurs_du_json_jamais_interpretees(page) -> None:
    assert "<script>window.__xss = 1</script>" in page.locator("#vue-MO tbody").inner_text()
    assert page.evaluate("window.__xss") is None


def test_erreur_claire_si_comparatif_absent(navigateur, base) -> None:
    reponse = {
        "ok": False,
        "erreur": {"code": "comparatif-indisponible", "message": "<absent-factice>"},
    }
    p = _ouvrir(navigateur, base, reponse)
    try:
        p.wait_for_selector("#vue-MO .modeles-etat[role=alert]")
        assert p.inner_text("#vue-MO .modeles-etat") == "<absent-factice>"
        assert p.locator("#vue-MO table").count() == 0
    finally:
        p.context.close()


def _avec(modifier):
    copie = json.loads(json.dumps(COMPARATIF))
    modifier(copie)
    return {"ok": True, "comparatif": copie}


def test_valeurs_nulles_jamais_zero_ni_nan(navigateur, base) -> None:
    def casser(c) -> None:
        b = c["modeles"][1]
        b["ecart_reference"] = {"qualite": {"ecart": None, "ic_bas": None, "ic_haut": 25.0}}
        b["qualite"]["bruit_items"] = None
        b["vitesse"] = {"origine": "cloud", "debit_tokens_s": None, "ram_max_go": None}
        c["modeles"][0]["vitesse"]["ram_max_go"] = None

    p = _ouvrir(navigateur, base, _avec(casser))
    try:
        p.wait_for_selector("#vue-MO .modeles-table")
        texte = p.locator("#vue-MO tbody").inner_text()
        assert "non calculé" in p.locator('[data-modele="modele-b"]').inner_text()
        assert "NaN" not in texte
        assert not re.search(r"(?<![\d,])0,0(?!\d)", texte)
    finally:
        p.context.close()


def test_suffixe_origine_vitesse_statut_jeu_et_encadre_conserve(navigateur, base) -> None:
    def adapter(c) -> None:
        c["jeu_statut"] = "relu-llm"
        c["modeles"][1]["vitesse"] = {"origine": "cloud", "debit_tokens_s": 30.0}

    p = _ouvrir(navigateur, base, _avec(adapter))
    try:
        p.wait_for_selector("#vue-MO .modeles-table")
        assert "relu par deux LLM, pas encore par un humain" in p.inner_text(
            "#vue-MO .modeles-intro"
        )
        assert "30,0 tokens/s (via réseau)" in p.locator('[data-modele="modele-b"]').inner_text()
        assert "(poste de développement)" in p.locator('[data-modele="modele-a"]').inner_text()
        assert "réseau" in p.get_attribute('[data-modele="modele-b"] td:nth-child(6)', "title")
        p.click("#vue-MO .modeles-guide summary")
        assert p.evaluate("document.querySelector('.modeles-guide').open") is False
        p.click('[data-colonne="qualite"]')
        assert p.evaluate("document.querySelector('.modeles-guide').open") is False
    finally:
        p.context.close()


def test_rendu_impossible_donne_une_alerte(navigateur, base) -> None:
    p = _ouvrir(navigateur, base, _avec(lambda c: c["modeles"].append(None)))
    try:
        p.wait_for_selector("#vue-MO .modeles-etat[role=alert]")
        assert p.inner_text("#vue-MO .modeles-etat") == "Comparatif illisible"
        assert p.locator("#vue-MO table").count() == 0
    finally:
        p.context.close()


def test_identifiant_avec_guillemet_garde_le_focus(navigateur, base) -> None:
    def adapter(c) -> None:
        c["modeles"][1]["id"] = 'm"] x'

    p = _ouvrir(navigateur, base, _avec(adapter))
    try:
        p.wait_for_selector("#vue-MO .modeles-table")
        p.locator("#vue-MO .modeles-bascule").nth(1).click()
        assert p.evaluate("document.activeElement.textContent") == "<modele-factice-B>"
        assert p.evaluate("document.activeElement.getAttribute('aria-expanded')") == "true"
    finally:
        p.context.close()
