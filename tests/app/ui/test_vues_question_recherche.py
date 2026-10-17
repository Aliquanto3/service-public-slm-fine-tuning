"""Story 12.7 : vues Question et Recherche, dans Edge avec un pont factice qui rejoue des flux.

Marqués `ui` : lancés avec `uv run pytest -m ui tests/app/ui`. Toutes les chaînes sont factices
et manifestement artificielles (D1) ; aucune ressource externe n'est chargée.
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

SOURCE_1 = {
    "numero": 1,
    "titre": "<titre-factice-1>",
    "url": "https://exemple.invalid/source-1",
    "origine": "index",
    "date": "2026-10-03",
    "extrait": "<extrait-factice-1>",
}
SOURCE_2 = {
    "numero": 2,
    "titre": "<titre-factice-2>",
    "url": "https://www.data.gouv.fr/datasets/factice",
    "origine": "mcp",
    "date": None,
    "extrait": None,
}
FIN = {"type": "fin", "raison": "terminee", "usage": None, "urls_inventees": []}
FLUX_Q = [
    {"type": "jeton", "texte": "<réponse-factice-1> "},
    {"type": "jeton", "texte": "voir [1] et [2] puis [9]."},
    {"type": "sources", "sources": [SOURCE_1, SOURCE_2]},
    {"type": "avertissement", "code": "c", "message": "<avertissement-factice>"},
    FIN,
]
RESULTAT_JEUX = (
    "Found 2 dataset(s) for query: '<requete-factice>'\nPage 1 of results:\n\n"
    "1. <jeu-factice-1>\n   ID: id-factice-1\n   Organization: <producteur-factice>\n"
    "   Tags: a, b\n   Resources: 2\n   URL: https://www.data.gouv.fr/datasets/jeu-factice-1\n\n"
    "2. <jeu-factice-2>\n   ID: id-factice-2\n   Organization: <producteur-factice-2>\n"
    "   Resources: 1\n   URL: https://www.data.gouv.fr/datasets/jeu-factice-2\n"
)
RESULTAT_LIGNES = (
    "Querying resource: <ressource-factice>\nDataset: <jeu-factice-1> (ID: id-factice-1)\n\n"
    "Columns: col_a, col_b\n\nData (2 rows):\n"
    "  Row 1:\n    col_a: <a1>\n    col_b: <b1>\n"
    "  Row 2:\n    col_a: <a2>\n    col_b: <b2>\n\n"
)


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
    p.wait_for_function("() => !document.getElementById('envoyer').disabled || true")
    # Presse-papiers capturé, pont qui rejoue le flux `window.__flux` à chaque envoi. Comme le
    # vrai client (`pont-client.js`), `envoyer` émet `generation:debut` avant l'appel ; un refus
    # (`window.__refus` = code) est rejeté, ou rendu `{ok: false}` si `window.__refusResolu`.
    # `mode.etat` rend `window.__mode` (contrat 12.5) ; `ouvrir_lien` rend `window.__ouvrir`.
    p.evaluate(
        """() => {
          window.__copies = [];
          Object.defineProperty(navigator, 'clipboard', {
            value: { writeText: async (t) => { window.__copies.push(t); } },
          });
          window.__appels = [];
          const pont = window.slmsp.pont;
          const rejouer = () => setTimeout(() => window.slmspRecevoir(window.__flux), 20);
          const refus = (code) => ({ ok: false, erreur: { code, message: '<refus-factice>' } });
          pont.envoyer = async (tache, messages) => {
            window.__appels.push(['envoyer', tache, messages]);
            window.slmsp.bus.emettre('generation:debut', { tache });
            if (window.__refus) {
              if (window.__refusResolu) return refus(window.__refus);
              throw Object.assign(new Error('refus'), { erreur: refus(window.__refus).erreur });
            }
            rejouer();
            return { ok: true };
          };
          const ancien = pont.appeler;
          pont.appeler = async (nom, ...args) => {
            window.__appels.push([nom, ...args]);
            if (nom === 'mode.etat') {
              return window.__mode
                ? { ok: true, mode: window.__mode, force: false }
                : refus('non-implementee');
            }
            if (nom === 'ouvrir_lien') return window.__ouvrir ?? refus('non-implementee');
            return ancien(nom, ...args);
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


def _pret(page) -> None:
    page.evaluate("window.slmspRecevoir({type: 'pret'})")


def _poser(page, tache: str, flux: list[dict], question: str = "<question-factice>") -> None:
    _pret(page)
    page.evaluate("(t) => window.slmsp.activer(t)", tache)
    page.evaluate("(f) => { window.__flux = f; }", flux)
    page.fill("#saisie", question)
    page.keyboard.press("Enter")


def _termine(page) -> None:
    page.wait_for_function("() => !!document.querySelector('.reponse-actions:not([hidden])')")


# -- Critère 1 : flux, puces de citation, avertissement juridique ---------------------------------


def test_flux_texte_puces_et_avertissement_juridique(page) -> None:
    _poser(page, "Q", FLUX_Q)
    page.wait_for_selector(".reponse-texte:has-text('<réponse-factice-1>')")
    _termine(page)
    assert page.locator(".message-utilisateur").inner_text() == "<question-factice>"
    puces = page.locator("#vue-Q .citation-chip")
    assert puces.count() == 2  # [9] n'a pas de source : il reste du texte
    assert puces.nth(0).get_attribute("aria-label") == "Source 1 : <titre-factice-1>"
    assert puces.nth(1).get_attribute("aria-label") == "Source 2 : <titre-factice-2>"
    assert "[9]" in page.locator(".reponse-texte").inner_text()
    assert page.locator("#vue-Q .legal-notice").inner_text() == "Ne vaut pas avis juridique"
    assert page.locator(".reponse-notes").inner_text() == "<avertissement-factice>"
    assert page.is_visible("#bouton-sources")


def test_texte_au_fil_de_l_eau_sans_puce_avant_la_fin(page) -> None:
    _pret(page)
    page.evaluate("(t) => window.slmsp.activer(t)", "Q")
    page.fill("#saisie", "<question-factice>")
    page.evaluate("window.__flux = []")
    page.keyboard.press("Enter")
    page.evaluate(
        "window.slmspRecevoir([{type: 'jeton', texte: 'voir [1]'},"
        f" {{type: 'sources', sources: [{json.dumps(SOURCE_1)}]}}])"
    )
    assert page.locator(".reponse-texte").inner_text() == "voir [1]"
    assert page.locator(".citation-chip").count() == 0
    assert page.locator(".reponse-actions").is_hidden()
    assert page.locator(".legal-notice").count() == 0
    page.evaluate(f"window.slmspRecevoir({json.dumps(FIN)})")
    assert page.locator(".citation-chip").count() == 1


def test_contenu_du_modele_jamais_interprete_comme_html(page) -> None:
    piege = '<img src=x onerror="window.__pwn=1"><b>gras</b>'
    _poser(page, "Q", [{"type": "jeton", "texte": piege}, FIN])
    _termine(page)
    assert page.locator(".reponse img, .reponse b").count() == 0
    assert page.evaluate("window.__pwn === undefined")
    assert piege in page.locator(".reponse-texte").inner_text()


def test_aucune_source_aucune_puce_ni_bouton_sources(page) -> None:
    _poser(page, "Q", [{"type": "jeton", "texte": "<réponse-factice-1> [1]"}, FIN])
    _termine(page)
    assert page.locator(".citation-chip").count() == 0
    assert page.is_hidden("#bouton-sources")


# -- Critère 2 : panneau Sources -----------------------------------------------------------------


def test_puce_ouvre_le_panneau_avec_cartes_et_echap_le_ferme(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    page.locator(".citation-chip").nth(1).click()
    assert page.is_visible("#sources")
    cartes = page.locator("#sources-corps .source-card")
    assert cartes.count() == 2
    assert cartes.nth(1).get_attribute("aria-current") == "true"
    premiere = cartes.nth(0).inner_text()
    assert "Documents installés" in premiere and "Index du 3 oct. 2026" in premiere
    detail = cartes.nth(0).locator("details")
    assert detail.get_attribute("open") is None
    assert not cartes.nth(0).locator(".source-extrait").is_visible()
    detail.locator("summary").click()
    assert cartes.nth(0).locator(".source-extrait").inner_text() == "<extrait-factice-1>"
    assert "data.gouv" in cartes.nth(1).inner_text()
    page.keyboard.press("Escape")
    assert page.is_hidden("#sources")
    page.locator(".citation-chip").nth(0).click()
    page.click("#sources-fermer")
    assert page.is_hidden("#sources")


def test_ouvrir_hors_ligne_copie_le_lien(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    page.locator(".citation-chip").nth(0).click()
    page.locator("#sources-corps .source-card").nth(0).get_by_text("Ouvrir").click()
    assert page.evaluate("window.__copies") == [SOURCE_1["url"]]
    assert "Lien copié. Il s'ouvrira quand vous serez connecté." in page.inner_text(
        "#sources-corps"
    )


def test_ouvrir_connecte_passe_par_le_pont_sans_navigation(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    page.evaluate("window.slmsp.bus.emettre('mode:change', {hors_ligne: false})")
    page.locator(".citation-chip").nth(0).click()
    assert page.locator("#vues a[href], #sources a[href]").count() == 0
    carte = page.locator("#sources-corps .source-card").nth(0)
    ouvrir = carte.get_by_role("button", name="Ouvrir")
    # Clic milieu et Ctrl+clic : un bouton n'ouvre ni onglet ni navigation (Q1).
    ouvrir.click(button="middle")
    ouvrir.click(modifiers=["Control"])
    page.evaluate("window.__ouvrir = {ok: true}")
    ouvrir.click()
    page.wait_for_function(
        "(u) => window.__appels.filter((a) => a[0] === 'ouvrir_lien' && a[1] === u).length === 2",
        arg=SOURCE_1["url"],
    )
    page.wait_for_selector("#sources-corps :text('Lien ouvert dans votre navigateur.')")
    assert len(page.context.pages) == 1
    assert page.url.startswith("http://127.0.0.1")
    assert not any("exemple.invalid" in u for u in page.requetes)


def test_ouvrir_connecte_refuse_par_le_pont_copie_le_lien(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    page.evaluate("window.slmsp.bus.emettre('mode:change', {hors_ligne: false})")
    page.locator(".citation-chip").nth(0).click()
    page.locator("#sources-corps .source-card").nth(0).get_by_text("Ouvrir").click()
    page.wait_for_function("() => window.__copies.length === 1")
    assert page.evaluate("window.__copies") == [SOURCE_1["url"]]
    page.wait_for_selector("#sources-corps :text('Lien copié. Collez-le dans votre navigateur.')")


# -- Critère 3 : cartes et tableaux de la Recherche ----------------------------------------------


def _resultat_outil(identifiant: str, resultat) -> dict:
    return {
        "type": "resultat-outil",
        "id": identifiant,
        "nom": "outil",
        "resultat": resultat,
        "erreur": False,
    }


def test_recherche_cartes_sans_avertissement_juridique_et_information_hors_ligne(page) -> None:
    flux = [
        {"type": "jeton", "texte": "<réponse-factice-1>"},
        _resultat_outil("a1", {"content": [{"type": "text", "text": RESULTAT_JEUX}]}),
        FIN,
    ]
    _poser(page, "RD", flux)
    _termine(page)
    assert page.locator("#vue-RD .legal-notice").count() == 0
    assert "Hors ligne : catalogue installé uniquement, sans chiffres à jour." in page.inner_text(
        "#vue-RD"
    )
    cartes = page.locator("#vue-RD .dataset-card")
    assert cartes.count() == 2
    assert "<producteur-factice>" in cartes.nth(0).inner_text()
    assert cartes.nth(0).get_by_text("Ouvrir").is_visible()
    # « Voir les données » : aucune méthode du pont 12.5 ne lit les lignes d'un jeu (masqué).
    assert page.locator("#vue-RD").get_by_text("Voir les données").count() == 0
    page.evaluate("window.slmsp.bus.emettre('mode:change', {hors_ligne: false})")
    assert page.locator("#vue-RD").get_by_text("Voir les données").count() == 0
    assert not page.locator("#vue-RD .info-mode").is_visible()


def test_tableau_d_outil_plafonne_a_50_lignes_et_copie_tabulee(page) -> None:
    tableau = {
        "colonnes": ["col_a", "col_b"],
        "jeu": "<jeu-factice-1>",
        "lignes": [[f"a{i}", f"b\t{i}"] for i in range(60)],
    }
    flux = [{"type": "jeton", "texte": "<réponse-factice-1>"}, _resultat_outil("t60", tableau), FIN]
    _poser(page, "RD", flux)
    _termine(page)
    carte = page.locator("#vue-RD .reponse-pieces")
    page.wait_for_selector("#vue-RD .data-table")
    assert page.locator("#vue-RD .data-table tbody tr").count() == 50
    assert "Extrait : 50 premières lignes" in carte.inner_text()
    assert "Source : data.gouv.fr, <jeu-factice-1>, consulté le" in carte.inner_text()
    carte.get_by_text("Copier le tableau").click()
    page.wait_for_function("() => window.__copies.length === 1")
    lignes = page.evaluate("window.__copies[0]").split("\n")
    assert lignes[0] == "col_a\tcol_b"
    assert lignes[1] == "a0\tb 0"  # la tabulation d'une cellule ne casse pas la grille
    assert len(lignes) == 1 + 50 + 1
    assert lignes[-1].startswith("Source : data.gouv.fr, <jeu-factice-1>, consulté le ")
    assert page.locator("#vue-RD .inline-confirmation").inner_text() == "Tableau copié"


def test_tableau_rendu_depuis_le_resultat_d_outil_jamais_depuis_le_texte(page) -> None:
    faux = "| faux_a | faux_b |\n| --- | --- |\n| 1 | 2 |"
    flux = [
        {"type": "jeton", "texte": faux},
        _resultat_outil("t1", {"content": [{"type": "text", "text": RESULTAT_LIGNES}]}),
        FIN,
    ]
    _poser(page, "RD", flux)
    _termine(page)
    assert page.locator("#vue-RD table").count() == 1
    entetes = page.locator("#vue-RD .data-table th").all_inner_texts()
    assert entetes == ["col_a", "col_b"]
    assert page.locator("#vue-RD .data-table tbody tr").count() == 2
    assert page.locator("#vue-RD .reponse-texte").inner_text() == faux
    assert (
        page.locator("#vue-RD .extrait-mention").count() == 0
    )  # moins de 50 lignes, rien de tronqué


# -- Critère 4 : repli ---------------------------------------------------------------------------


def test_repli_encart_et_reessayer(page) -> None:
    flux = [
        {"type": "repli", "motif": "<motif-factice>", "vers": "index"},
        {"type": "jeton", "texte": "<réponse-factice-1>"},
        FIN,
    ]
    _poser(page, "RD", flux, "<question-repli>")
    _termine(page)
    encart = page.locator("#vue-RD .callout-warning")
    assert encart.is_visible()
    assert (
        "data.gouv ne répond pas. Réponse établie à partir du catalogue installé."
        in encart.inner_text()
    )
    assert "<motif-factice>" not in page.inner_text("body")
    encart.get_by_text("Réessayer").click()
    page.wait_for_function("() => window.__appels.filter((a) => a[0] === 'envoyer').length === 2")
    messages = page.evaluate("window.__appels.filter((a) => a[0] === 'envoyer')[1][2]")
    assert messages == [{"role": "user", "content": "<question-repli>"}]
    _termine(page)
    assert page.locator("#vue-RD .reponse").count() == 1  # remplacée sur place


def test_reessayer_seulement_sur_la_derniere_reponse(page) -> None:
    flux = [{"type": "repli", "motif": "m", "vers": "index"}, {"type": "jeton", "texte": "r"}, FIN]
    _poser(page, "RD", flux, "<question-1>")
    _termine(page)
    page.fill("#saisie", "<question-2>")
    page.keyboard.press("Enter")
    page.wait_for_function(
        "() => document.querySelectorAll('#vue-RD .reponse-actions:not([hidden])').length === 2"
    )
    encarts = page.locator("#vue-RD .callout-warning")
    assert encarts.count() == 2
    assert not encarts.nth(0).get_by_text("Réessayer").is_visible()
    encarts.nth(1).get_by_text("Réessayer").click()
    page.wait_for_function("() => window.__appels.filter((a) => a[0] === 'envoyer').length === 3")
    messages = page.evaluate("window.__appels.filter((a) => a[0] === 'envoyer')[2][2]")
    assert messages == [{"role": "user", "content": "<question-2>"}]
    page.wait_for_function(
        "() => document.querySelectorAll('#vue-RD .reponse-actions:not([hidden])').length === 2"
    )
    assert page.locator("#vue-RD .tour").count() == 2


# -- Critère 5 : arrêt et régénération -----------------------------------------------------------


def test_arreter_puis_regenerer_remplace_la_reponse_sur_place(page) -> None:
    _pret(page)
    page.evaluate("(t) => window.slmsp.activer(t)", "Q")
    page.evaluate("window.__flux = []")
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<ancienne-réponse>'})")
    page.click("#envoyer")  # « Arrêter »
    _termine(page)
    assert page.locator("#vue-Q .mention-interrompue").is_visible()
    assert page.locator("#vue-Q .mention-interrompue").inner_text() == "Réponse interrompue"
    page.evaluate(
        f"window.__flux = [{{type: 'jeton', texte: '<nouvelle-réponse>'}}, {json.dumps(FIN)}]"
    )
    page.get_by_role("button", name="Régénérer").click()
    page.wait_for_selector(".reponse-texte:has-text('<nouvelle-réponse>')")
    _termine(page)
    assert page.locator("#vue-Q .reponse").count() == 1
    assert "<ancienne-réponse>" not in page.inner_text("#vue-Q")
    assert not page.locator("#vue-Q .mention-interrompue").is_visible()


def test_echap_sur_la_reponse_pendant_la_generation_l_interrompt(page) -> None:
    _pret(page)
    page.evaluate("(t) => window.slmsp.activer(t)", "Q")
    page.evaluate("window.__flux = []")
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<début-factice>'})")
    page.focus("[data-reponse]")
    page.keyboard.press("Escape")
    page.wait_for_function("() => window.__appels.some((a) => a[0] === 'arreter')")
    page.wait_for_selector("#vue-Q .mention-interrompue")


def test_copier_la_reponse_copie_le_texte_brut(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    page.locator("#vue-Q .reponse-actions").get_by_role("button", name="Copier", exact=True).click()
    page.wait_for_function("() => window.__copies.length === 1")
    assert page.evaluate("window.__copies[0]") == "<réponse-factice-1> voir [1] et [2] puis [9]."
    assert page.locator("#vue-Q .inline-confirmation").inner_text() == "Copié"
    page.wait_for_selector("#vue-Q .inline-confirmation", state="detached", timeout=6_000)


def test_regenerer_seulement_sur_la_derniere_reponse(page) -> None:
    flux = [{"type": "jeton", "texte": "<réponse-factice-1>"}, FIN]
    _poser(page, "Q", flux, "<question-1>")
    _termine(page)
    page.fill("#saisie", "<question-2>")
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.querySelectorAll('.tour').length === 2")
    page.wait_for_function(
        "() => document.querySelectorAll('.reponse-actions:not([hidden])').length === 2"
    )
    visibles = page.locator("#vue-Q .reponse-actions button:visible", has_text="Régénérer")
    assert visibles.count() == 1


# -- Question vide, erreur propre à la vue, hors ligne ------------------------------------------


def test_question_vide_trois_exemples_cliquables(page) -> None:
    exemples = page.locator("#vue-Q .exemple")
    assert exemples.count() == 3
    assert exemples.nth(0).inner_text() == "Quelles pièces pour une demande d'APA ?"
    assert "<exemple-à-valider" not in " ".join(exemples.all_inner_texts())
    exemples.nth(0).click()
    assert page.input_value("#saisie") == "Quelles pièces pour une demande d'APA ?"
    assert page.evaluate("document.activeElement.id") == "saisie"
    _poser(page, "Q", [FIN], "<question-factice>")
    _termine(page)
    assert page.locator("#vue-Q .vide").is_hidden()
    page.click("#bouton-nouvelle")
    assert page.locator("#vue-Q .vide").is_visible()
    assert page.locator("#vue-Q .tour").count() == 0


def test_erreur_en_cours_de_flux_garde_le_texte_recu(page) -> None:
    flux = [
        {"type": "jeton", "texte": "<début-factice>"},
        {"type": "erreur", "code": "c", "message": "<message-technique-factice>"},
    ]
    _poser(page, "Q", flux)
    page.wait_for_selector("#vue-Q .mention-echec:visible")
    assert "<début-factice>" in page.inner_text("#vue-Q")
    assert "<message-technique-factice>" not in page.inner_text("body")
    assert not page.is_hidden("#erreur-interne")
    assert page.locator("#vue-Q .legal-notice").count() == 0


def test_aucune_ressource_externe_chargee(page) -> None:
    _poser(page, "Q", FLUX_Q)
    _termine(page)
    externes = [u for u in page.requetes if not u.startswith("http://127.0.0.1")]
    assert externes == []


# -- Revue 12.7 : refus du pont, Mode, flux tardifs, lecteur d'écran ------------------------------


@pytest.mark.parametrize("resolu", [False, True], ids=["rejet", "ok-false"])
def test_regenerer_refuse_par_le_pont_retablit_l_etat(page, resolu: bool) -> None:
    flux = [{"type": "jeton", "texte": "<réponse-factice-1>"}, FIN]
    _poser(page, "Q", flux, "<question-1>")
    _termine(page)
    page.evaluate(
        "(r) => { window.__refus = 'generation-en-cours'; window.__refusResolu = r; }", resolu
    )
    page.get_by_role("button", name="Régénérer").click()
    page.wait_for_function("() => !document.getElementById('erreur-interne').hidden", polling=50)
    assert page.inner_text("#envoyer") == "Envoyer"  # ni « Arrêter » figé ni état bloqué
    assert page.input_value("#saisie") == "<question-1>"  # texte restauré
    assert page.locator("#vue-Q .reponse-texte").inner_text() == "<réponse-factice-1>"
    assert page.locator("#vue-Q .reponse-actions").is_visible()
    assert page.locator("#vue-Q .mention-echec").is_hidden()
    # Le pont redevient disponible : un nouvel envoi passe normalement.
    page.evaluate("window.__refus = null")
    page.press("#saisie", "Enter")
    page.wait_for_function(
        "() => document.querySelectorAll('#vue-Q .reponse-actions:not([hidden])').length === 2"
    )
    assert page.inner_text("#envoyer") == "Envoyer"


def test_envoi_refuse_par_le_pont_debloque_l_envoi(page) -> None:
    page.evaluate("window.__refus = 'generation-en-cours'")
    _poser(page, "Q", [FIN], "<question-refusée>")
    page.wait_for_function("() => !document.getElementById('erreur-interne').hidden", polling=50)
    page.wait_for_selector("#vue-Q .mention-echec:visible")
    assert page.inner_text("#envoyer") == "Envoyer"
    assert page.input_value("#saisie") == "<question-refusée>"


@pytest.mark.parametrize(("mode", "connecte"), [("connecte", True), ("hors_ligne", False)])
def test_mode_initial_lu_par_mode_etat(page, mode: str, connecte: bool) -> None:
    page.evaluate("(m) => { window.__mode = m; }", mode)
    _pret(page)
    page.evaluate("window.slmsp.activer('RD')")  # RD est montée maintenant : elle lit le Mode
    page.wait_for_function("() => window.__appels.some((a) => a[0] === 'mode.etat')")
    attendu = "connecte" if connecte else "hors-ligne"
    page.wait_for_function(
        "(m) => document.querySelector('#vue-RD .conversation').dataset.mode === m", arg=attendu
    )
    assert page.locator("#vue-RD .info-mode").is_visible() is (not connecte)


def test_mode_inconnu_reste_hors_ligne(page) -> None:
    _pret(page)
    page.evaluate("window.slmsp.activer('RD')")  # `mode.etat` répond `non-implementee`
    page.wait_for_function("() => window.__appels.some((a) => a[0] === 'mode.etat')")
    assert page.get_attribute("#vue-RD .conversation", "data-mode") == "hors-ligne"
    assert page.locator("#vue-RD .info-mode").is_visible()


def test_nouvelle_conversation_pendant_le_flux_arrete_et_ignore_la_suite(page) -> None:
    _pret(page)
    page.evaluate("window.slmsp.activer('Q')")
    page.evaluate("window.__flux = []")
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<début-factice>'})")
    page.click("#bouton-nouvelle")
    page.wait_for_function(
        "() => window.__appels.map((a) => a[0]).join() .includes('arreter,nouvelle_conversation')"
    )
    page.evaluate("window.slmspRecevoir([{type: 'jeton', texte: '<tardif>'}])")
    assert page.locator("#vues .tour").count() == 0
    assert "<tardif>" not in page.inner_text("#vues")
    assert page.locator("#vue-Q .vide").is_visible()
    assert page.inner_text("#envoyer") != "Arrêter"


def test_flux_d_une_tache_n_ouvre_aucun_tour_dans_une_autre(page) -> None:
    _pret(page)
    page.evaluate("window.slmsp.activer('Q')")
    page.evaluate("window.__flux = []")
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmsp.activer('RD')")
    page.evaluate(f"window.slmspRecevoir([{{type: 'jeton', texte: '<suite>'}}, {json.dumps(FIN)}])")
    assert page.locator("#vue-RD .tour").count() == 0
    assert page.locator("#vue-Q .tour").count() == 1
    assert page.locator("#vue-Q .reponse-texte").inner_text() == "<suite>"


def test_reponse_annoncee_une_fois_terminee_jamais_jeton_par_jeton(page) -> None:
    _pret(page)
    page.evaluate("window.slmsp.activer('Q')")
    page.evaluate("window.__flux = []")
    page.fill("#saisie", "<question-factice>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmspRecevoir({type: 'jeton', texte: '<jeton-annonce>'})")
    page.wait_for_timeout(400)
    assert "<jeton-annonce>" not in page.inner_text("#annonces")
    assert page.get_attribute("#vue-Q .reponse", "aria-live") is None
    page.evaluate(f"window.slmspRecevoir({json.dumps(FIN)})")
    page.wait_for_function(
        "() => document.getElementById('annonces').textContent"
        " === 'Réponse terminée. <jeton-annonce>'",
        polling=50,
    )
    assert page.get_attribute("#annonces", "aria-live") == "polite"
