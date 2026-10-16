"""Story 12.8 : vues Compte rendu et Langage clair, dans Edge avec un pont factice.

Marqués `ui` : `uv run pytest -m ui tests/app/ui`. Toutes les chaînes sont factices et
manifestement artificielles (D1) ; aucune ressource externe n'est chargée.
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
FIN = {"type": "fin", "raison": "terminee", "usage": None, "urls_inventees": []}
INFOBULLE = "Terme juridique conservé tel quel"
CORPS_LC = "<texte-clair-1> <terme-conserve-1> <texte-clair-2>"
SORTIE_LC = f"{CORPS_LC}\n\nPassages conservés tels quels :\n- <terme-conserve-1>"


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
    # Presse-papiers capturé ; le pont rejoue `window.__flux` à chaque envoi. Comme le vrai
    # client, `envoyer` émet `generation:debut` avant l'appel ; `window.__refus` = code de refus.
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
            if (window.__refus) {
              throw Object.assign(new Error('refus'), {
                erreur: { code: window.__refus, message: '<refus-factice>' },
              });
            }
            setTimeout(() => window.slmspRecevoir(window.__flux), 20);
            return { ok: true };
          };
          pont.arreter = async () => {
            window.__appels.push(['arreter']);
            window.slmspRecevoir({
              type: 'fin', raison: 'interrompue', usage: null, urls_inventees: [],
            });
          };
        }"""
    )
    yield p
    p.context.close()


def _ouvrir(page, tache: str, flux: list[dict], texte: str = "<notes-factices>") -> None:
    page.evaluate("window.slmspRecevoir({type: 'pret'})")
    page.evaluate("(t) => window.slmsp.activer(t)", tache)
    page.evaluate("(f) => { window.__flux = f; }", flux)
    page.fill(f"#redaction-saisie-{tache}", texte)


def _lancer(page, tache: str) -> None:
    page.locator(f"#vue-{tache} .volet-pied .bouton-primaire").click()


def _termine(page, tache: str) -> None:
    page.wait_for_function(
        "(t) => !document.querySelector(`#vue-${t} .resultat-actions`).hidden", arg=tache
    )


# -- Volets, compteur, bouton principal unique --


def test_volets_compteur_et_un_seul_bouton_principal(page) -> None:
    page.evaluate("(t) => window.slmsp.activer(t)", "CR")
    vue = page.locator("#vue-CR")
    assert vue.locator(".editor-pane").count() == 2
    assert "0 mot" in vue.locator(".compteur-mots").inner_text()
    assert vue.locator(".volet-pied .bouton-primaire").is_disabled()  # entrée vide
    page.fill("#redaction-saisie-CR", "<mot-1> <mot-2>\n<mot-3>")
    assert vue.locator(".compteur-mots").inner_text() == "3 mots"
    assert vue.locator(".volet-pied .bouton-primaire").inner_text() == "Rédiger"
    assert vue.locator(".bouton-primaire:visible").count() == 1
    page.evaluate("(t) => window.slmsp.activer(t)", "LC")
    assert page.locator("#vue-LC .volet-pied .bouton-primaire").inner_text() == "Réécrire"
    assert "Collez vos notes de réunion" in vue.inner_text()


def test_resultat_au_fil_de_l_eau_puis_copier_texte_brut(page) -> None:
    _ouvrir(page, "CR", [{"type": "jeton", "texte": "<compte-rendu-factice>"}, FIN])
    _lancer(page, "CR")
    page.wait_for_selector("#vue-CR .resultat:has-text('<compte-rendu-factice>')")
    _termine(page, "CR")
    envoi = page.evaluate("window.__appels")[0]
    assert envoi[1] == "CR" and envoi[2] == [{"role": "user", "content": "<notes-factices>"}]
    # Après la génération : « Copier » est le seul bouton principal visible.
    visibles = page.locator("#vue-CR .bouton-primaire:visible")
    assert visibles.count() == 1 and visibles.inner_text() == "Copier"
    page.wait_for_function(
        "() => document.getElementById('annonces').textContent"
        " === 'Résultat terminé. <compte-rendu-factice>'",
        polling=50,
    )
    visibles.click()
    assert page.evaluate("window.__copies") == ["<compte-rendu-factice>"]
    page.wait_for_selector("#vue-CR .inline-confirmation:has-text('Copié')")
    page.wait_for_selector("#vue-CR .inline-confirmation", state="detached", timeout=5000)


def test_modifier_l_entree_rend_le_bouton_principal_a_l_action(page) -> None:
    _ouvrir(page, "CR", [{"type": "jeton", "texte": "<compte-rendu-factice>"}, FIN])
    _lancer(page, "CR")
    _termine(page, "CR")
    page.fill("#redaction-saisie-CR", "<notes-modifiees>")
    visibles = page.locator("#vue-CR .bouton-primaire:visible")
    assert visibles.count() == 1 and visibles.inner_text() == "Rédiger"


# -- Critère 1 : entrée trop longue, « Partie i sur n » --


def test_texte_long_partie_i_sur_n_puis_resultat_fusionne(page) -> None:
    _ouvrir(page, "CR", [], "<notes-longues-factices>")
    _lancer(page, "CR")
    page.evaluate(
        "window.slmspRecevoir({type: 'progression', etape: 'Partie 1 sur 3', fait: 0, total: 3})"
    )
    avancement = page.locator("#vue-CR .avancement")
    assert "Texte long : je le traite en plusieurs parties." in avancement.inner_text()
    assert "Partie 1 sur 3" in avancement.inner_text()
    page.evaluate(
        "window.slmspRecevoir({type: 'progression', etape: 'Partie 2 sur 3', fait: 1, total: 3})"
    )
    assert "Partie 2 sur 3" in avancement.inner_text()
    page.evaluate(
        "window.slmspRecevoir([{type: 'progression', etape: 'Fusion des parties',"
        " fait: 3, total: 3}, {type: 'jeton', texte: '<fusion-factice>'}])"
    )
    assert avancement.is_visible()
    page.evaluate(f"window.slmspRecevoir({json.dumps(FIN)})")
    _termine(page, "CR")
    assert avancement.is_hidden()
    assert page.locator("#vue-CR .resultat").inner_text() == "<fusion-factice>"


# -- Critère 2 : passages signalés --


def test_passages_signales_surlignes_avec_infobulle_au_survol_et_au_focus(page) -> None:
    _ouvrir(page, "LC", [{"type": "jeton", "texte": SORTIE_LC}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    passage = page.locator("#vue-LC .resultat-texte .flagged-passage")
    assert passage.count() == 1
    assert passage.evaluate("e => e.firstChild.textContent") == "<terme-conserve-1>"
    infobulle = passage.locator(".infobulle")
    assert infobulle.get_attribute("role") == "tooltip"
    assert infobulle.inner_text() == INFOBULLE or infobulle.text_content() == INFOBULLE
    assert passage.get_attribute("aria-describedby") == infobulle.get_attribute("id")
    assert not infobulle.is_visible()
    passage.hover()
    assert infobulle.is_visible()
    page.mouse.move(0, 0)
    assert not infobulle.is_visible()
    passage.focus()
    assert infobulle.is_visible()
    page.keyboard.press("Escape")  # ferme l'infobulle sans quitter le passage
    assert not infobulle.is_visible()
    assert page.evaluate("document.activeElement.classList.contains('flagged-passage')")


def test_copier_langage_clair_sans_surlignage_ni_section_de_signalement(page) -> None:
    _ouvrir(page, "LC", [{"type": "jeton", "texte": SORTIE_LC}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    page.locator("#vue-LC .resultat-actions .bouton-primaire").click()
    assert page.evaluate("window.__copies") == [CORPS_LC]


def test_sans_section_reconnue_texte_normal_sans_erreur(page) -> None:
    brut = "<texte-clair-1>\n<texte-clair-2>"
    _ouvrir(page, "LC", [{"type": "jeton", "texte": brut}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    assert page.locator("#vue-LC .flagged-passage").count() == 0
    assert page.locator("#vue-LC .resultat").inner_text() == brut
    assert page.locator("#vue-LC .mention-echec").is_hidden()
    page.locator("#vue-LC .resultat-actions .bouton-primaire").click()
    assert page.evaluate("window.__copies") == [brut]


def test_section_variee_une_ligne_et_guillemets(page) -> None:
    brut = "<a> « <b-factice> » <c>\n\n**Passages gardés : « <b-factice> »**"
    _ouvrir(page, "LC", [{"type": "jeton", "texte": brut}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    passages = page.locator("#vue-LC .flagged-passage")
    assert passages.count() == 1
    assert passages.evaluate("e => e.firstChild.textContent") == "<b-factice>"


def test_contenu_du_modele_jamais_interprete_comme_html(page) -> None:
    piege = '<img src=x onerror="window.__pwn=1"><b>gras</b>'
    _ouvrir(page, "LC", [{"type": "jeton", "texte": piege}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    assert page.locator("#vue-LC .resultat img, #vue-LC .resultat b").count() == 0
    assert page.evaluate("window.__pwn === undefined")
    assert piege in page.locator("#vue-LC .resultat").inner_text()


# -- Régénérer, refus du pont, arrêt, effacer --


def test_regenerer_rejoue_l_envoi_et_remplace_le_resultat(page) -> None:
    _ouvrir(page, "CR", [{"type": "jeton", "texte": "<resultat-1>"}, FIN])
    _lancer(page, "CR")
    _termine(page, "CR")
    page.evaluate("window.__flux = [{type: 'jeton', texte: '<resultat-2>'}, window.__flux[1]]")
    page.get_by_role("button", name="Régénérer").click()
    page.wait_for_selector("#vue-CR .resultat:has-text('<resultat-2>')")
    _termine(page, "CR")
    envois = [a for a in page.evaluate("window.__appels") if a[0] == "envoyer"]
    assert len(envois) == 2 and envois[0][1:] == envois[1][1:]
    assert page.locator("#vue-CR .resultat").inner_text() == "<resultat-2>"


def test_refus_du_pont_a_l_envoi_retablit_l_etat_et_conserve_le_texte(page) -> None:
    _ouvrir(page, "CR", [])
    page.evaluate("window.__refus = 'generation-en-cours'")
    _lancer(page, "CR")
    page.wait_for_selector("#vue-CR .volet-pied .bouton-primaire:visible")
    assert page.input_value("#redaction-saisie-CR") == "<notes-factices>"
    assert page.locator("#vue-CR .volet-pied .bouton-secondaire").is_hidden()  # plus d'« Arrêter »
    assert page.is_visible("#erreur-interne")


def test_refus_a_la_regeneration_garde_le_resultat_precedent(page) -> None:
    _ouvrir(page, "CR", [{"type": "jeton", "texte": "<resultat-1>"}, FIN])
    _lancer(page, "CR")
    _termine(page, "CR")
    page.evaluate("window.__refus = 'generation-en-cours'")
    page.get_by_role("button", name="Régénérer").click()
    _termine(page, "CR")
    assert page.locator("#vue-CR .resultat").inner_text() == "<resultat-1>"
    assert page.locator("#vue-CR .mention-echec").is_hidden()


def test_arret_en_cours_de_generation(page) -> None:
    _ouvrir(page, "CR", [])
    _lancer(page, "CR")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<debut-factice>'})")
    arreter = page.locator("#vue-CR .volet-pied .bouton-secondaire")
    assert arreter.is_visible() and arreter.inner_text() == "Arrêter"
    arreter.click()
    _termine(page, "CR")
    assert page.locator("#vue-CR .mention-interrompue").is_visible()
    assert page.locator("#vue-CR .resultat").inner_text() == "<debut-factice>"


def test_erreur_en_cours_de_flux_garde_le_texte_recu(page) -> None:
    _ouvrir(page, "CR", [])
    _lancer(page, "CR")
    page.evaluate(
        "window.slmspRecevoir([{type: 'jeton', texte: '<debut-factice>'},"
        " {type: 'erreur', code: 'x', message: 'y'}])"
    )
    assert page.locator("#vue-CR .mention-echec").is_visible()
    assert page.locator("#vue-CR .resultat").inner_text() == "<debut-factice>"


def test_effacer_vide_les_deux_volets_et_ignore_le_flux_tardif(page) -> None:
    _ouvrir(page, "CR", [])
    _lancer(page, "CR")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<debut-factice>'})")
    page.click("#bouton-nouvelle")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<tardif-factice>'})")
    assert page.input_value("#redaction-saisie-CR") == ""
    assert "<tardif-factice>" not in page.locator("#vue-CR .resultat").inner_text()
    assert "<debut-factice>" not in page.locator("#vue-CR .resultat").inner_text()
    assert page.locator("#vue-CR .compteur-mots").inner_text() == "0 mot"
    noms = [a[0] for a in page.evaluate("window.__appels")]
    assert "arreter" in noms


def test_flux_d_une_autre_tache_ignore(page) -> None:
    _ouvrir(page, "CR", [])
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<etranger-factice>'})")
    assert "<etranger-factice>" not in page.locator("#vue-CR .resultat").inner_text()


# -- Critère 4 : volets empilés sous 1 200 px --


def test_volets_cote_a_cote_puis_empiles(page) -> None:
    page.evaluate("(t) => window.slmsp.activer(t)", "CR")
    entree = page.locator("#vue-CR .volet-entree")
    resultat = page.locator("#vue-CR .volet-resultat")
    page.set_viewport_size({"width": 1400, "height": 800})
    e, r = entree.bounding_box(), resultat.bounding_box()
    assert abs(e["y"] - r["y"]) < 2 and r["x"] > e["x"]
    page.set_viewport_size({"width": 1100, "height": 800})
    e, r = entree.bounding_box(), resultat.bounding_box()
    assert r["y"] > e["y"] + e["height"] - 2 and abs(r["x"] - e["x"]) < 2


def test_aucune_requete_externe(page) -> None:
    _ouvrir(page, "LC", [{"type": "jeton", "texte": SORTIE_LC}, FIN], "<texte-administratif>")
    _lancer(page, "LC")
    _termine(page, "LC")
    assert all(u.startswith("http://127.0.0.1") or u.startswith("data:") for u in page.requetes)
