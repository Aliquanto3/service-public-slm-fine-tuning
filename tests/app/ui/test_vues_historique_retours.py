"""Story 12.11 : vues Historique et Retours, dans Edge avec un pont simulé en mémoire.

Marqués `ui` : `uv run pytest -m ui tests/app/ui/test_vues_historique_retours.py`. Toutes les
chaînes sont factices (D1) ; aucune ressource externe n'est chargée.
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

# Pont en mémoire : `historique.*` et `retours.*` reprennent le contrat de `app/pont/*.py` ;
# `envoyer` rejoue un flux factice, comme le vrai client (`generation:debut` avant l'appel).
PONT_SIMULE = """
() => {
  window.__appels = [];
  window.__magasin = { conversations: [], retours: 0, seq: 0, supprimees: {} };
  const pont = window.slmsp.pont;
  const m = window.__magasin;
  pont.envoyer = async (tache, messages) => {
    window.__appels.push(['envoyer', tache, messages]);
    window.slmsp.bus.emettre('generation:debut', { tache });
    setTimeout(() => window.slmspRecevoir([
      { type: 'jeton', texte: '<réponse-factice-' + (++m.seq) + '>' },
      { type: 'sources', sources: [{ numero: 1, titre: '<titre-factice>', url: 'https://exemple.invalid/s', origine: 'index', date: null, extrait: null }] },
      { type: 'fin', raison: 'terminee', usage: null, urls_inventees: [] },
    ]), 20);
    return { ok: true };
  };
  pont.appeler = async (nom, ...args) => {
    window.__appels.push([nom, ...args]);
    if (nom === 'historique.lister') {
      return { ok: true, conversations: m.conversations.map(c => ({ id: c.id, titre: c.titre, tache: c.tache, date: c.date })) };
    }
    if (nom === 'historique.enregistrer') {
      const [tache, messages, sources, id] = args;
      let c = m.conversations.find(x => x.id === id);
      if (!c) {
        c = { id: 'conv' + (m.conversations.length + 1), titre: messages[0].content.slice(0, 40), tache, date: new Date().toISOString() };
        m.conversations.unshift(c);
      }
      Object.assign(c, { messages, sources });
      return { ok: true, id: c.id };
    }
    if (nom === 'historique.ouvrir') {
      const c = m.conversations.find(x => x.id === args[0]);
      return c ? { ok: true, conversation: c } : { ok: false, erreur: { code: 'conversation-introuvable', message: '' } };
    }
    if (nom === 'historique.supprimer') {
      const i = m.conversations.findIndex(x => x.id === args[0]);
      if (i < 0) return { ok: true, supprimee: false };
      m.supprimees[args[0]] = m.conversations.splice(i, 1)[0];
      return { ok: true, supprimee: true };
    }
    if (nom === 'historique.annuler_suppression') {
      const c = m.supprimees[args[0]];
      if (c) m.conversations.unshift(c);
      return { ok: true, restauree: Boolean(c) };
    }
    if (nom === 'retours.noter') { m.retours += 1; return { ok: true }; }
    if (nom === 'retours.lister') return { ok: true, retours: [], nombre: m.retours };
    if (nom === 'retours.apercu_export') {
      if (!m.retours) return { ok: false, erreur: { code: 'aucun-retour', message: '' } };
      return { ok: true, nombre: m.retours, nom_fichier: 'retours-assistant-2026-10-17.json',
               apercu: '{"retours": ["<contenu-factice>", "[masqué]"]}', avertissements: ['<avertissement-factice>'], masques: { telephone: 1 } };
    }
    if (nom === 'retours.exporter') return { ok: true, enregistre: true, nom: 'retours-assistant-2026-10-17.json' };
    return { ok: true, factice: true };
  };
}
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
    p = contexte.new_page()
    p.set_default_timeout(30_000)
    p.requetes = []
    p.on("request", lambda r: p.requetes.append(r.url))
    p.goto(base + "?pont=factice")
    p.wait_for_function("() => window.slmsp !== undefined", polling=50)
    p.wait_for_function("() => !document.getElementById('bandeau-preparation').offsetParent")
    p.evaluate(PONT_SIMULE)
    p.evaluate("() => window.slmsp.bus.emettre('historique:efface', {})")  # relit la liste
    yield p
    contexte.close()


def _poser(page, question: str) -> None:
    page.fill("#saisie", question)
    page.press("#saisie", "Enter")
    page.wait_for_selector("#vue-Q .reponse-actions:not([hidden])")


def _appels(page, nom: str) -> list[list]:
    return page.evaluate("(n) => window.__appels.filter(a => a[0] === n)", nom)


def test_etat_vide(page) -> None:
    assert page.inner_text(".historique-vide") == (
        "Vos conversations apparaîtront ici. Elles restent sur ce poste."
    )


def test_premier_envoi_cree_une_entree_groupee_par_jour_puis_la_met_a_jour(page) -> None:
    _poser(page, "<question-factice-1>")
    page.wait_for_selector(".historique-entree")
    assert page.inner_text(".historique-jour-titre") == "Aujourd'hui"
    assert page.inner_text(".historique-ouvrir") == "<question-factice-1>"
    assert page.locator(".historique-vide").is_hidden()
    (enregistrement,) = _appels(page, "historique.enregistrer")
    assert enregistrement[1] == "Q"
    assert enregistrement[2] == [
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
    ]
    assert enregistrement[4] is None
    _poser_deuxieme_tour(page)
    assert page.locator(".historique-entree").count() == 1  # même entrée, mise à jour
    second = _appels(page, "historique.enregistrer")[1]
    assert second[4] == "conv1"
    assert len(second[2]) == 4


def _poser_deuxieme_tour(page) -> None:
    page.wait_for_selector("#vue-Q article.reponse .retour")
    page.fill("#saisie", "<question-factice-2>")
    page.press("#saisie", "Enter")
    page.wait_for_selector("#vue-Q .tour:nth-child(2) .retour")


def test_pouce_haut_est_enregistre_tout_de_suite(page) -> None:
    _poser(page, "<question-factice-1>")
    page.click("#vue-Q .retour-haut")
    page.wait_for_selector("#vue-Q .retour-message:not(:empty)")
    assert page.inner_text("#vue-Q .retour-message") == "Merci, retour enregistré sur ce poste"
    assert _appels(page, "retours.noter") == [["retours.noter", "conv1", 1, "pouce_haut", None]]
    assert page.get_attribute("#vue-Q .retour-haut", "aria-pressed") == "true"
    assert page.is_disabled("#vue-Q .retour-bas")  # un seul jugement par réponse


def test_pouce_bas_ouvre_un_champ_facultatif(page) -> None:
    _poser(page, "<question-factice-1>")
    assert page.locator("#vue-Q .retour-commentaire").is_hidden()
    page.click("#vue-Q .retour-bas")
    page.wait_for_selector("#vue-Q .retour-commentaire:not([hidden])")
    assert "Qu'est-ce qui n'allait pas ?" in page.inner_text("#vue-Q .retour-commentaire label")
    assert _appels(page, "retours.noter") == []  # rien n'est enregistré avant « Envoyer »
    page.fill("#vue-Q .retour-commentaire textarea", "<commentaire-factice>")
    page.click("#vue-Q .retour-commentaire button[type=submit]")
    page.wait_for_selector("#vue-Q .retour-message:not(:empty)")
    assert _appels(page, "retours.noter") == [
        ["retours.noter", "conv1", 1, "pouce_bas", "<commentaire-factice>"]
    ]


def test_pouce_bas_sans_commentaire(page) -> None:
    _poser(page, "<question-factice-1>")
    page.click("#vue-Q .retour-bas")
    page.click("#vue-Q .retour-commentaire button[type=submit]")
    page.wait_for_selector("#vue-Q .retour-message:not(:empty)")
    assert _appels(page, "retours.noter")[0][3:] == ["pouce_bas", None]


def test_suppression_sans_confirmation_puis_annulation(page) -> None:
    _poser(page, "<question-factice-1>")
    page.wait_for_selector(".historique-entree")
    page.hover(".historique-entree")
    page.click(".historique-supprimer")
    page.wait_for_selector(".historique-annuler:not([hidden])")
    assert page.locator(".historique-entree").count() == 0  # disparue sans confirmation
    page.click(".historique-annuler-bouton")
    page.wait_for_selector(".historique-entree")
    assert page.locator(".historique-annuler").is_hidden()


def test_l_annulation_n_est_proposee_que_5_secondes(page) -> None:
    _poser(page, "<question-factice-1>")
    page.wait_for_selector(".historique-entree")
    page.click(".historique-supprimer", force=True)
    page.wait_for_selector(".historique-annuler:not([hidden])")
    page.wait_for_selector(".historique-annuler", state="hidden", timeout=8000)
    assert page.locator(".historique-entree").count() == 0


def test_rouvrir_reactive_la_tache_d_origine(page) -> None:
    page.evaluate(
        """() => window.__magasin.conversations.push({
          id: 'ancienne', titre: '<titre-ancien>', tache: 'RD', date: '2026-01-02T10:00:00+00:00',
          messages: [{ role: 'user', content: '<question-ancienne>' }, { role: 'assistant', content: '<réponse-ancienne>' }],
          sources: [] })"""
    )
    page.evaluate("() => window.slmsp.bus.emettre('historique:efface', {})")
    page.wait_for_selector(".historique-entree")
    assert "2026" in page.inner_text(
        ".historique-jour-titre"
    )  # un jour passé : date en toutes lettres
    assert page.get_attribute("#tache-Q", "aria-current") == "true"
    page.click(".historique-ouvrir")
    page.wait_for_selector("#vue-RD .message-utilisateur")
    assert page.get_attribute("#tache-RD", "aria-current") == "true"
    assert page.inner_text("#vue-RD .message-utilisateur") == "<question-ancienne>"
    assert "<réponse-ancienne>" in page.inner_text("#vue-RD .reponse-texte")
    assert page.locator("#vue-RD .retour").count() == 1


def _ouvrir_retours(page) -> None:
    page.click("#bouton-parametres")
    page.click("#parametres-onglet-retours")


def test_export_inactif_sans_retour(page) -> None:
    _ouvrir_retours(page)
    page.wait_for_selector("#retours-etat:not(:empty)")
    assert page.inner_text("#retours-etat") == "Vous n'avez encore donné aucun retour."
    assert page.is_disabled("#retours-exporter")


def test_export_apercu_avant_enregistrement_sans_requete_sortante(page, base) -> None:
    _poser(page, "<question-factice-1>")
    page.click("#vue-Q .retour-haut")
    page.wait_for_selector("#vue-Q .retour-message:not(:empty)")
    _ouvrir_retours(page)
    page.wait_for_function("() => !document.getElementById('retours-exporter').disabled")
    page.click("#retours-exporter")
    page.wait_for_selector(".retours-apercu:not([hidden])")
    assert "[masqué]" in page.inner_text(".retours-texte")
    assert "<avertissement-factice>" in page.inner_text(".retours-apercu")
    assert _appels(page, "retours.exporter") == []  # l'aperçu précède tout enregistrement
    page.click(".retours-actions .bouton-primaire")
    page.wait_for_selector(".retours-apercu", state="hidden")
    assert _appels(page, "retours.exporter") == [["retours.exporter"]]
    assert "retours-assistant-2026-10-17.json" in page.inner_text("#retours-etat")
    origine = base.rsplit("/", 1)[0]
    assert all(u.startswith(origine) or u.startswith("data:") for u in page.requetes)


def test_aucun_innerhtml_dans_les_vues() -> None:
    for nom in ("historique", "retours"):
        source = (UI / "js" / "vues" / f"{nom}.js").read_text(encoding="utf-8")
        assert "innerHTML" not in source
        assert "insertAdjacentHTML" not in source
