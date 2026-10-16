"""Story 13.3 : vue Courrier type, formulaire et emplacements, dans Edge avec un pont factice.

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
OBJET = "<objet-factice>"
ELEMENTS = "<element-factice-1>"
COURRIER = (
    "<debut>\nObjet : <valeur-inventee>\n"
    "<milieu> [<champ-a-completer-1>] <fin> [<champ-a-completer-2>]"
)
COURRIER_SUR = "<debut> [<champ-a-completer-1>]\nObjet : [<objet-a-completer>]"


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
            return window.__controle;
          };
        }"""
    )
    yield p
    p.context.close()


def _ouvrir(page) -> None:
    page.evaluate("window.slmspRecevoir({type: 'pret'})")
    page.evaluate("(t) => window.slmsp.activer(t)", "CT")


def _remplir(page, type_: str | None = "convocation", objet: str = OBJET, elements: str = ELEMENTS):
    if type_:
        page.select_option("#courrier-type-CT", type_)
    page.fill("#courrier-objet-CT", objet)
    page.fill("#redaction-saisie-CT", elements)


def _rediger(page, courrier: str = COURRIER, raison: str = "terminee", **champs) -> None:
    _ouvrir(page)
    absents = [
        c
        for c in ("objet", "elements_connus")
        if c not in champs.get("garde", ("objet", "elements_connus"))
    ]
    controle = PontRedactionOutils().appeler("emplacements", courrier, absents)
    page.evaluate(
        "([f, c]) => { window.__flux = f; window.__controle = c; }",
        [[{"type": "jeton", "texte": courrier}, {**FIN, "raison": raison}], controle],
    )
    _remplir(page, **{k: v for k, v in champs.items() if k != "garde"})
    page.locator("#vue-CT .volet-pied .bouton-primaire").click()
    page.wait_for_function(
        "() => !document.querySelector('#vue-CT .resultat-actions').hidden", polling=50
    )


def _envois(page) -> list:
    return [a for a in page.evaluate("window.__appels") if a[0] == "envoyer"]


def test_vue_disponible_formulaire_vide_et_bouton_inactif(page) -> None:
    _ouvrir(page)
    vue = page.locator("#vue-CT")
    assert "non disponible" not in vue.inner_text()
    assert vue.locator("#courrier-type-CT").input_value() == ""
    assert vue.locator("#courrier-objet-CT").input_value() == ""
    assert vue.locator("#redaction-saisie-CT").input_value() == ""
    bouton = vue.locator(".volet-pied .bouton-primaire")
    assert bouton.is_disabled()
    # Les libellés proposés sont les quatre types de la story, étiquetés pour les lecteurs d'écran.
    options = vue.locator("#courrier-type-CT option").all_inner_texts()
    assert options[1:] == [
        "accusé de réception",
        "demande de pièces",
        "convocation",
        "réponse d'information",
    ]
    assert vue.locator("label[for=courrier-type-CT]").count() == 1
    page.select_option("#courrier-type-CT", "convocation")
    assert bouton.is_disabled()  # ni objet ni éléments connus
    page.fill("#courrier-objet-CT", OBJET)
    assert bouton.is_enabled()


def test_entree_ct_porte_seulement_les_champs_remplis(page) -> None:
    _rediger(page, garde=("objet",), elements="")
    (envoi,) = _envois(page)
    assert envoi[1] == "CT"
    assert envoi[3] == {"entree": {"type_courrier": "convocation", "objet": OBJET}}


def test_entree_complete(page) -> None:
    _rediger(page, type_="demande de pièces")
    (envoi,) = _envois(page)
    assert envoi[3]["entree"] == {
        "type_courrier": "demande de pièces",
        "objet": OBJET,
        "elements_connus": ELEMENTS,
    }


def test_emplacements_atteignables_au_clavier_et_annonces(page) -> None:
    _rediger(page)
    page.wait_for_selector("#vue-CT .resultat mark.letter-placeholder")
    marques = page.locator("#vue-CT .resultat mark.letter-placeholder")
    assert marques.count() == 2
    assert marques.first.get_attribute("tabindex") == "0"
    assert "[<champ-a-completer-1>]" in marques.first.text_content()
    assert "à compléter" in marques.first.text_content()
    assert "2 emplacements à compléter" in page.locator("#vue-CT .courrier-compte").inner_text()
    marques.first.focus()
    assert page.evaluate("document.activeElement.className") == "letter-placeholder"
    # Distinguable sans la couleur : bordure en pointillés.
    assert (
        page.eval_on_selector(
            "#vue-CT mark.letter-placeholder", "e => getComputedStyle(e).borderTopStyle"
        )
        == "dashed"
    )


def test_champ_non_fourni_rendu_par_une_valeur_signale_un_callout(page) -> None:
    _rediger(page, garde=("elements_connus",), objet="")
    page.wait_for_selector("#vue-CT .callout-warning")
    texte = page.locator("#vue-CT .callout-warning").inner_text()
    assert "« Objet »" in texte and "Vérifié automatiquement" in texte
    appels = [a for a in page.evaluate("window.__appels") if a[0].startswith("redaction_outils")]
    assert appels == [["redaction_outils.emplacements", COURRIER, ["objet"]]]


def test_aucun_callout_si_le_champ_est_en_emplacement(page) -> None:
    _rediger(page, courrier=COURRIER_SUR, garde=("elements_connus",), objet="")
    page.wait_for_selector("#vue-CT .courrier-compte")
    assert page.locator("#vue-CT .callout-warning").count() == 0


def test_aucun_callout_quand_le_champ_est_fourni(page) -> None:
    _rediger(page)
    page.wait_for_selector("#vue-CT .courrier-compte")
    assert page.locator("#vue-CT .callout-warning").count() == 0


def test_copier_le_courrier_brut(page) -> None:
    _rediger(page)
    page.wait_for_selector("#vue-CT .resultat mark.letter-placeholder")
    page.locator("#vue-CT .resultat-actions .bouton-primaire").click()
    assert page.evaluate("window.__copies") == [COURRIER]


def test_echec_du_controle_garde_le_courrier(page) -> None:
    page.evaluate("window.__echec = true")
    _rediger(page)
    page.wait_for_selector("#vue-CT .courrier-compte:has-text('pas pu être repérés')")
    assert page.locator("#vue-CT .resultat").inner_text() == COURRIER


def test_courrier_interrompu_sans_controle(page) -> None:
    _rediger(page, raison="interrompue")
    assert page.locator("#vue-CT .courrier-notes").count() == 0
    assert page.locator("#vue-CT .resultat").inner_text() == COURRIER


def test_aucun_html_injecte_ni_ressource_externe(page) -> None:
    piege = "<img src=x onerror=window.__pwn=1> [<b>gras</b>] <b>gras</b>"
    _rediger(page, courrier=piege)
    page.wait_for_selector("#vue-CT .resultat mark.letter-placeholder")
    assert page.locator("#vue-CT .resultat img, #vue-CT .resultat b").count() == 0
    assert page.evaluate("window.__pwn") is None
    assert all(u.startswith(("http://127.0.0.1", "data:")) for u in page.requetes)
