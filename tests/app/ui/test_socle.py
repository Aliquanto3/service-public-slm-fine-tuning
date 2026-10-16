"""Story 12.4 : tests d'interface dans Edge (Playwright pour Python, `channel="msedge"`).

Marqués `ui` : exclus par défaut, lancés avec `uv run pytest -m ui tests/app/ui`. Aucun navigateur
n'est téléchargé : Edge, déjà installé, est piloté tel quel (décision Q12).
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
ECOUTE_ENVOI = """() => {
  window.__envois = [];
  window.slmsp.bus.abonner('envoi', (e) => window.__envois.push(e));
}"""
TACHES = ["Q", "RD", "CR", "LC", "CO", "RE", "CT", "TR"]


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="module")
def base() -> Iterator[str]:
    gestionnaire = functools.partial(_Silencieux, directory=str(UI))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    yield f"http://127.0.0.1:{serveur.server_port}/index.html"
    serveur.shutdown()
    serveur.server_close()


@pytest.fixture(scope="module")
def navigateur() -> Iterator[object]:
    with playwright_sync.sync_playwright() as p:
        try:
            nav = p.chromium.launch(channel="msedge", headless=True)
        except Exception as erreur:  # Edge absent ou non pilotable
            pytest.skip(f"Edge indisponible : {erreur}")
        yield nav
        nav.close()


def _ouvrir(navigateur, base, *, requete="?pont=factice", bienvenue=False, **options):
    contexte = navigateur.new_context(
        viewport=options.pop("viewport", {"width": 1280, "height": 720}), **options
    )
    if bienvenue is False:
        contexte.add_init_script(
            "try { if (!localStorage.getItem('slmsp.bienvenue-vue'))"
            " localStorage.setItem('slmsp.bienvenue-vue', 'true'); } catch {}"
        )
    page = contexte.new_page()
    page.set_default_timeout(90_000)  # le CPU peut être chargé par des benchmarks
    page.requetes = []
    page.on("request", lambda r: page.requetes.append(r.url))
    page.goto(base + requete)
    page.wait_for_function("() => window.slmsp !== undefined", polling=50)
    return page


@pytest.fixture
def page(navigateur, base) -> Iterator[object]:
    p = _ouvrir(navigateur, base)
    yield p
    p.context.close()


def _debordement(page) -> list[str]:
    """Éléments dont le contenu dépasse horizontalement (document compris)."""
    return page.evaluate(
        """() => {
          const sortie = [];
          const doc = document.documentElement;
          if (doc.scrollWidth > doc.clientWidth) sortie.push('document');
          for (const id of ['colonne', 'barre', 'principal']) {
            const el = document.getElementById(id);
            if (el.scrollWidth > el.clientWidth) sortie.push(id);
          }
          return sortie;
        }"""
    )


# -- Critère 1 : 1 024 x 640, texte à 150 %, aucune barre horizontale ---------------------------


def test_aucun_defilement_horizontal_a_150_pourcent(navigateur, base) -> None:
    page = _ouvrir(navigateur, base, viewport={"width": 1024, "height": 640})
    try:
        for _ in range(4):
            page.keyboard.press("Control+=")
        assert page.evaluate("getComputedStyle(document.documentElement).fontSize") == "24px"
        for tache in TACHES:
            page.evaluate("(t) => window.slmsp.activer(t)", tache)
            assert _debordement(page) == [], tache
        page.evaluate("window.slmsp.bus.emettre('sources:disponibles', true)")
        page.evaluate("window.slmsp.bus.emettre('sources:ouvrir')")
        assert _debordement(page) == []
        page.keyboard.press("Control+0")
        assert page.evaluate("getComputedStyle(document.documentElement).fontSize") == "16px"
    finally:
        page.context.close()


def test_sources_poussent_au_dessus_de_1280_et_recouvrent_en_dessous(navigateur, base) -> None:
    for largeur, pousse in ((1280, True), (1100, False)):
        page = _ouvrir(navigateur, base, viewport={"width": largeur, "height": 700})
        try:
            avant = page.locator("#principal").bounding_box()["width"]
            page.evaluate("window.slmsp.bus.emettre('sources:ouvrir')")
            apres = page.locator("#principal").bounding_box()
            sources = page.locator("#sources").bounding_box()
            if pousse:
                assert apres["width"] < avant
                assert apres["x"] + apres["width"] <= sources["x"] + 1
            else:
                assert apres["width"] == avant
                assert apres["x"] + apres["width"] > sources["x"]
        finally:
            page.context.close()


# -- Critère 2 : clavier seul --------------------------------------------------------------------


def test_ordre_de_tabulation_focus_visible_et_libelles(page) -> None:
    page.fill("#saisie", "<texte-factice-1>")
    page.evaluate("window.slmsp.bus.emettre('sources:ouvrir')")
    page.evaluate(  # point de départ de la navigation au clavier : la marque, en tête de colonne
        "() => { const m = document.querySelector('.marque'); m.tabIndex = -1; m.focus(); }"
    )
    vus = []
    for _ in range(14):
        page.keyboard.press("Tab")
        info = page.evaluate(
            """() => {
              const el = document.activeElement;
              const etiquette = el.labels && el.labels[0] ? el.labels[0].textContent : '';
              const nom = (el.getAttribute('aria-label') || el.textContent || etiquette).trim();
              // La zone de saisie montre son focus par la bordure de son cadre (composer).
              const s = getComputedStyle(el.id === 'saisie' ? el.form : el);
              const contour = el.id === 'saisie'
                ? 'solid ' + s.borderTopWidth + ' ' + s.borderTopColor
                : s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor;
              return { id: el.id, nom, contour };
            }"""
        )
        assert info["nom"], info
        assert info["contour"] == "solid 2px rgb(69, 29, 199)", info
        vus.append(info["id"])
        if info["id"] == "sources-fermer":
            break
    assert vus == [
        "tache-Q",
        "tache-RD",
        "tache-CR",
        "tache-LC",
        "plus-bascule",
        "bouton-parametres",
        "bouton-nouvelle",
        "mode-pastille",
        "exemple-Q-1",  # les trois exemples de l'écran « Question vide » (story 12.7)
        "exemple-Q-2",
        "exemple-Q-3",
        "saisie",
        "envoyer",
        "sources-fermer",
    ]


def test_ctrl_1_a_4_activent_les_taches_prioritaires_et_l_annoncent(page) -> None:
    for touche, tache, libelle in (
        ("2", "RD", "Recherche de données"),
        ("3", "CR", "Compte rendu"),
        ("4", "LC", "Langage clair"),
        ("1", "Q", "Question"),
    ):
        page.keyboard.press(f"Control+{touche}")
        assert page.get_attribute(f"#tache-{tache}", "aria-current") == "true"
        assert page.inner_text("#titre-tache") == libelle
        page.wait_for_function(
            "(m) => document.getElementById('annonces').textContent === m",
            arg=f"Tâche active : {libelle}",
            polling=50,  # le mode par défaut (rAF) s'arrête quand la page est jugée masquée
        )
    assert page.get_attribute("#annonces", "aria-live") == "polite"


def test_plus_est_memorise_et_les_taches_secondaires_s_ouvrent(page) -> None:
    assert page.is_hidden("#taches-secondaires")
    page.click("#plus-bascule")
    assert page.is_visible("#tache-CO")
    page.reload()
    page.wait_for_function("() => window.slmsp !== undefined", polling=50)
    assert page.is_visible("#tache-TR")
    assert page.get_attribute("#plus-bascule", "aria-expanded") == "true"


def test_travail_conserve_par_tache_et_vues_non_disponibles(page) -> None:
    page.fill("#saisie", "<texte-factice-2>")
    page.keyboard.press("Control+2")
    assert page.input_value("#saisie") == ""
    page.keyboard.press("Control+1")
    assert page.input_value("#saisie") == "<texte-factice-2>"
    for tache in TACHES:
        page.evaluate("(t) => window.slmsp.activer(t)", tache)
        if tache in ("Q", "RD"):  # vues livrées par la story 12.7 : écran vide disponible
            vue = page.locator(f"#vue-{tache}")
            assert vue.locator(".conversation .vide h2").is_visible(), tache
            assert "non disponible" not in vue.inner_text(), tache
            continue
        if tache in ("CR", "LC"):  # vues livrées par la story 12.8 : volets de rédaction
            vue = page.locator(f"#vue-{tache}")
            assert vue.locator(".redaction .volet-entree").is_visible(), tache
            assert "non disponible" not in vue.inner_text(), tache
            continue
        if tache in ("CO", "RE", "CT", "TR"):  # vues livrées par les stories 13.1 à 13.4
            assert "non disponible" not in page.inner_text(f"#vue-{tache}"), tache
            continue
        assert page.inner_text(f"#vue-{tache}") == "non disponible", tache


def test_echap_ferme_le_panneau_sources(page) -> None:
    page.evaluate("window.slmsp.bus.emettre('sources:ouvrir')")
    assert page.is_visible("#sources")
    page.keyboard.press("Escape")
    assert page.is_hidden("#sources")


# -- Critère 3 : zone de saisie ------------------------------------------------------------------


def test_zone_de_saisie_entree_envoie_maj_entree_ligne(page) -> None:
    page.evaluate(ECOUTE_ENVOI)
    assert "N'indiquez pas de nom" in page.get_attribute("#saisie", "placeholder")
    assert page.is_disabled("#envoyer")
    page.fill("#saisie", "<ligne-factice-1>")
    assert page.is_enabled("#envoyer")
    page.keyboard.press("Shift+Enter")
    page.keyboard.type("<ligne-factice-2>")
    assert page.input_value("#saisie") == "<ligne-factice-1>\n<ligne-factice-2>"
    assert page.evaluate("window.__envois.length") == 0
    page.keyboard.press("Enter")
    assert page.evaluate("window.__envois.map((e) => e.texte)") == [
        "<ligne-factice-1>\n<ligne-factice-2>"
    ]
    assert page.input_value("#saisie") == ""
    assert page.is_disabled("#envoyer") or page.inner_text("#envoyer") == "Arrêter"
    page.wait_for_function(
        "() => document.getElementById('envoyer').textContent === 'Envoyer'", polling=50
    )


def test_arreter_pendant_la_generation(page) -> None:
    page.wait_for_function("() => window.slmsp.etat.pret", polling=50)  # `pret` du pont factice
    page.evaluate("window.slmsp.bus.emettre('generation:debut', {})")
    assert page.inner_text("#envoyer") == "Arrêter"
    assert page.is_enabled("#envoyer")
    page.evaluate("window.slmspRecevoir({type: 'fin', raison: 'interrompue'})")
    assert page.inner_text("#envoyer") == "Envoyer"


# -- Critère 6 et UX-DR19 : états globaux ---------------------------------------------------------


def test_preparation_saisie_possible_envoyer_inactif(navigateur, base) -> None:
    page = _ouvrir(navigateur, base, requete="?pont=factice&pret=0")
    try:
        page.evaluate(ECOUTE_ENVOI)
        assert page.inner_text("#bandeau-preparation") == "Préparation de l'assistant…"
        page.fill("#saisie", "<texte-factice-3>")
        assert page.inner_text("#envoyer") == "Préparation…"
        assert page.is_disabled("#envoyer")
        page.keyboard.press("Enter")
        assert page.evaluate("window.__envois.length") == 0
        page.evaluate("window.slmspRecevoir({type: 'pret'})")
        assert page.inner_text("#envoyer") == "Envoyer"
        assert page.is_enabled("#envoyer")
        assert page.is_hidden("#bandeau-preparation")
    finally:
        page.context.close()


def test_erreur_interne_sans_detail_technique(page) -> None:
    page.fill("#saisie", "<texte-factice-4>")
    page.keyboard.press("Enter")
    page.evaluate("window.slmspRecevoir({type: 'erreur', code: 'c', message: '<message-factice>'})")
    encart = page.locator("#erreur-interne")
    assert encart.is_visible()
    assert "Un problème est survenu. Votre texte est conservé." in encart.inner_text()
    assert "<message-factice>" not in page.inner_text("body")
    assert page.input_value("#saisie") == "<texte-factice-4>"
    page.click("#erreur-reessayer")
    assert encart.is_hidden()


def test_bienvenue_au_premier_lancement_seulement(navigateur, base) -> None:
    page = _ouvrir(navigateur, base, bienvenue=True)
    try:
        texte = page.inner_text("#bienvenue")
        assert "Cet assistant utilise l'intelligence artificielle." in texte
        assert "N'indiquez pas de nom" in texte
        assert "Ne vaut pas avis juridique." in texte
        assert page.is_hidden("#composer")
        page.click("#bienvenue-commencer")
        assert page.is_hidden("#bienvenue") and page.is_visible("#composer")
        page.reload()
        page.wait_for_function("() => window.slmsp !== undefined", polling=50)
        assert page.is_hidden("#bienvenue")
    finally:
        page.context.close()


def test_reduire_les_animations_respecte(navigateur, base) -> None:
    page = _ouvrir(navigateur, base, reduced_motion="reduce")
    try:
        assert (
            page.evaluate("getComputedStyle(document.getElementById('envoyer')).transitionDuration")
            == "0s"
        )
    finally:
        page.context.close()


# -- Critère 5 : aucune ressource externe ----------------------------------------------------------


def test_aucune_ressource_externe_et_csp_effective(page, base) -> None:
    racine = base.rsplit("/", 1)[0]
    assert page.requetes
    for url in page.requetes:
        assert url.startswith(racine) or url.startswith(("data:", "blob:")), url
    assert "default-src 'self'" in page.get_attribute("meta[http-equiv]", "content")


class _AutreOrigine(_Silencieux):
    """Serveur local d'une autre origine, qui accepterait un `fetch` sans la CSP (CORS ouvert)."""

    visites: list[str] = []

    def do_GET(self) -> None:  # noqa: N802 (nom imposé par http.server)
        _AutreOrigine.visites.append(self.path)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")


@pytest.fixture
def autre_origine() -> Iterator[str]:
    _AutreOrigine.visites = []
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _AutreOrigine)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    yield f"http://127.0.0.1:{serveur.server_port}/x"
    serveur.shutdown()
    serveur.server_close()


def test_csp_bloque_un_fetch_vers_une_autre_origine(page, autre_origine) -> None:
    # Témoin hors CSP (client Playwright) : le serveur répond, un échec ne viendrait pas du réseau.
    assert page.context.request.get(autre_origine).body() == b"ok"
    _AutreOrigine.visites.clear()
    resultat = page.evaluate(
        """(url) => new Promise((fini) => {
          const violations = [];
          document.addEventListener('securitypolicyviolation', (e) => violations.push({
            uri: e.blockedURI, directive: e.effectiveDirective,
          }));
          fetch(url).then(
            () => setTimeout(() => fini({ bloque: false, violations }), 100),
            () => setTimeout(() => fini({ bloque: true, violations }), 100),
          );
        })""",
        autre_origine,
    )
    assert resultat["bloque"] is True
    assert {"uri": autre_origine, "directive": "connect-src"} in resultat["violations"]
    assert _AutreOrigine.visites == []


def test_ctrl_chiffre_en_azerty_par_position_physique(page) -> None:
    # En AZERTY, Ctrl+1 produit `key === "&"` et `code === "Digit1"` ; Ctrl+2 donne « é ».
    for cle, code, tache in (("é", "Digit2", "RD"), ("&", "Digit1", "Q"), ("'", "Digit4", "LC")):
        page.evaluate(
            """([key, code]) => document.dispatchEvent(new KeyboardEvent('keydown', {
              key, code, ctrlKey: true, bubbles: true, cancelable: true,
            }))""",
            [cle, code],
        )
        assert page.get_attribute(f"#tache-{tache}", "aria-current") == "true", cle


def test_echec_du_pont_a_l_envoi_conserve_le_texte(page) -> None:
    page.evaluate(
        """() => {
          const pont = window.slmsp.pont;
          pont.envoyer = () => {
            window.slmsp.bus.emettre('generation:debut', {});
            return Promise.reject(new Error('<erreur-factice>'));
          };
        }"""
    )
    page.wait_for_function(  # l'envoi est refusé tant que le pont n'a pas signalé `pret`
        "() => document.getElementById('envoyer').textContent !== 'Préparation…'", polling=50
    )
    page.fill("#saisie", "<texte-factice-5>")
    page.keyboard.press("Enter")
    page.wait_for_function("() => !document.getElementById('erreur-interne').hidden", polling=50)
    assert page.input_value("#saisie") == "<texte-factice-5>"
    assert page.inner_text("#envoyer") == "Envoyer"
    assert "<erreur-factice>" not in page.inner_text("body")


def test_garde_de_demarrage(navigateur, base) -> None:
    page = _ouvrir(navigateur, base)
    try:
        assert page.is_hidden("#demarrage-echec")
    finally:
        page.context.close()
    contexte = navigateur.new_context()
    try:
        page = contexte.new_page()
        page.route("**/js/socle/app.js", lambda route: route.abort())
        page.goto(base + "?pont=factice")
        page.locator("#demarrage-echec").wait_for(state="visible", timeout=10_000)
        assert "n'a pas pu s'afficher" in page.inner_text("#demarrage-echec")
    finally:
        contexte.close()


def test_noms_accessibles_quand_la_colonne_se_reduit(navigateur, base) -> None:
    page = _ouvrir(navigateur, base, viewport={"width": 900, "height": 640})
    try:
        for id_, nom in (("tache-Q", "Question"), ("plus-bascule", "Plus")):
            assert page.get_by_role("button", name=nom, exact=True).get_attribute("id") == id_
    finally:
        page.context.close()
