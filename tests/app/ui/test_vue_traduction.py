"""Story 13.4 : vue Traduction (langues de la configuration, arabe en RTL), pont factice.


Marqués `ui`. Chaînes factices (D1).
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
FIN = {"type": "fin", "raison": "terminee", "usage": None, "urls_inventees": []}
DOC = "<texte-factice-1> <texte-factice-2>"
TRADUCTION = "<traduction-factice-1>"
MENTION = "Traduction automatique, à vérifier avant envoi"


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
        """(fin) => {
          window.__appels = [];
          window.__refus = null;
          const pont = window.slmsp.pont;
          pont.appeler = async () => ({ ok: true, langues: ['en', 'es', 'ar', 'pt', 'de'] });
          pont.envoyer = async (tache, messages, options) => {
            window.__appels.push(['envoyer', tache, messages, options]);
            if (window.__refus) return window.__refus;
            window.slmsp.bus.emettre('generation:debut', { tache });
            setTimeout(() => window.slmspRecevoir([
              { type: 'jeton', texte: '<traduction-factice-1>' }, fin]), 20);
            return { ok: true };
          };
        }""",
        FIN,
    )
    p.evaluate("window.slmspRecevoir({type: 'pret'})")
    p.evaluate("(t) => window.slmsp.activer(t)", "TR")
    yield p
    p.context.close()


def _remonter(page, langues: list[str] | None) -> None:
    """Remonte la vue ; `langues=None` simule un pont en échec."""
    page.evaluate(
        """async (l) => {
          const pont = window.slmsp.pont;
          pont.appeler = async () => {
            if (l === null) throw new Error('pont indisponible');
            return { ok: true, langues: l };
          };
          const m = await import('./js/vues/traduction.js');
          document.getElementById('vue-essai')?.remove();
          const c = document.createElement('div');
          c.id = 'vue-essai';
          document.body.append(c);
          m.monter(c, pont, { bus: window.slmsp.bus, tache: 'ESSAI' });
        }""",
        langues,
    )
    page.wait_for_timeout(200)


def _options(page, selecteur: str) -> list[str]:
    return page.locator(f"{selecteur} option").all_inner_texts()


def test_langues_proposees_viennent_de_la_configuration(page) -> None:
    _remonter(page, ["en", "ar"])
    assert _options(page, "#traduction-source-ESSAI") == ["français", "anglais", "arabe"]
    _remonter(page, ["en", "es"])  # arabe retiré par la configuration : aucune option arabe
    assert "arabe" not in _options(page, "#traduction-source-ESSAI")


def test_echec_du_pont_francais_seul_message_et_traduire_desactive(page) -> None:
    _remonter(page, None)
    assert _options(page, "#traduction-cible-ESSAI") == ["français"]  # pas d'arabe en repli (Q9)
    assert "indisponible" in page.inner_text("#vue-essai .message-langues")
    page.fill("#vue-essai .redaction-saisie", DOC)
    assert page.locator("#vue-essai .volet-pied .bouton-primaire").is_disabled()


def test_langues_inconnues_filtrees_et_configuration_vide_desactive_traduire(page) -> None:
    _remonter(page, ["it", "en"])
    assert _options(page, "#traduction-cible-ESSAI") == ["français", "anglais"]
    _remonter(page, ["fr"])
    assert _options(page, "#traduction-cible-ESSAI") == ["français"]
    assert "Aucune langue cible" in page.inner_text("#vue-essai .message-langues")
    page.fill("#vue-essai .redaction-saisie", DOC)
    assert page.locator("#vue-essai .volet-pied .bouton-primaire").is_disabled()
    _remonter(page, ["en"])
    page.fill("#vue-essai .redaction-saisie", DOC)
    assert page.locator("#vue-essai .volet-pied .bouton-primaire").is_enabled()
    assert page.locator("#vue-essai .message-langues").is_hidden()


def test_entree_porte_langue_source_et_cible_et_sens_inverse(page) -> None:
    page.select_option("#traduction-source-TR", "fr")
    page.select_option("#traduction-cible-TR", "es")
    page.fill("#redaction-saisie-TR", DOC)
    page.locator("#vue-TR .volet-pied .bouton-primaire").click()
    page.wait_for_function("() => window.__appels.length === 1", polling=50)
    assert page.evaluate("window.__appels.at(-1)[1]") == "TR"
    assert page.evaluate("window.__appels.at(-1)[3]") == {
        "entree": {"langue_source": "français", "langue_cible": "espagnol", "texte": DOC}
    }
    page.wait_for_function(
        "() => !document.querySelector('#vue-TR .resultat-actions').hidden", polling=50
    )
    page.get_by_role("button", name="Inverser les langues").click()
    assert page.input_value("#traduction-source-TR") == "es"
    assert page.input_value("#traduction-cible-TR") == "fr"
    page.locator("#vue-TR .volet-pied .bouton-primaire").click()
    page.wait_for_function("() => window.__appels.length === 2", polling=50)
    entree = page.evaluate("window.__appels.at(-1)[3].entree")
    assert (entree["langue_source"], entree["langue_cible"]) == ("espagnol", "français")


def test_les_deux_langues_ne_sont_jamais_identiques(page) -> None:
    page.select_option("#traduction-source-TR", "fr")
    page.select_option("#traduction-cible-TR", "en")
    page.select_option("#traduction-source-TR", "en")
    assert page.input_value("#traduction-cible-TR") == "fr"


def test_arabe_en_sortie_est_rtl_et_isole_avec_la_mention(page) -> None:
    page.select_option("#traduction-cible-TR", "ar")
    page.fill("#redaction-saisie-TR", DOC)
    page.locator("#vue-TR .volet-pied .bouton-primaire").click()
    page.wait_for_function(
        "() => !document.querySelector('#vue-TR .resultat-actions').hidden", polling=50
    )
    texte = page.locator("#vue-TR .traduction-texte")
    assert texte.get_attribute("dir") == "rtl"
    assert texte.get_attribute("lang") == "ar"
    assert texte.inner_text() == TRADUCTION
    assert page.evaluate(
        "getComputedStyle(document.querySelector('#vue-TR .traduction-texte')).unicodeBidi"
    ) in ("isolate", "isolate-override")
    mention = page.locator("#vue-TR .mention-traduction")
    assert mention.inner_text() == MENTION
    assert mention.get_attribute("dir") == "ltr"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_arabe_en_entree_met_la_saisie_en_rtl(page) -> None:
    page.select_option("#traduction-source-TR", "ar")
    saisie = page.locator("#redaction-saisie-TR")
    assert saisie.get_attribute("dir") == "rtl"
    assert saisie.get_attribute("lang") == "ar"
    page.select_option("#traduction-source-TR", "fr")
    assert saisie.get_attribute("dir") == "ltr"


def test_mention_incluse_dans_la_copie(page) -> None:
    page.evaluate(
        """() => {
          window.__copie = null;
          Object.defineProperty(navigator, 'clipboard', {
            value: { writeText: async (t) => { window.__copie = t; } }, configurable: true });
        }"""
    )
    page.fill("#redaction-saisie-TR", DOC)
    page.locator("#vue-TR .volet-pied .bouton-primaire").click()
    page.wait_for_function(
        "() => !document.querySelector('#vue-TR .resultat-actions').hidden", polling=50
    )
    page.locator("#vue-TR .resultat-actions .bouton-primaire").click()
    page.wait_for_function("() => window.__copie !== null", polling=50)
    assert page.evaluate("window.__copie") == f"{TRADUCTION}\n\n{MENTION}"


def test_aucune_ressource_externe(page) -> None:
    assert all(u.startswith(("http://127.0.0.1", "data:")) for u in page.requetes)
