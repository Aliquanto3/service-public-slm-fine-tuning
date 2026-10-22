"""Capture le GIF de démonstration du README (`docs/assets/demo-assistant.gif`).

Usage : `uv run --with pillow python outils/capturer_demo.py` (Pillow reste hors des dépendances
du projet ; Playwright et Edge, comme les tests d'interface `tests/app/ui/`).

Charge l'interface réelle (`src/slmsp/app/ui/index.html`) avec un pont simulé. La réponse affichée
n'est pas rédigée ici : c'est la sortie réelle de MiniCPM5-2B à l'item Q-501 du jeu dev1, lue dans
`generations.jsonl` (texte, sources, usage) et rejouée par morceaux. Le comparatif des modèles est
le fichier réel livré avec l'application. Aucun appel réseau, aucune clé.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import os
import re
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parents[1]
UI = RACINE / "src" / "slmsp" / "app" / "ui"
DEPOT = Path(
    os.environ.get("SLMSP_DEPOT_PRINCIPAL", r"C:\Users\Anael\dev\service-public-slm-fine-tuning")
)
GENERATIONS = DEPOT / "runs/eval-generation/20261020-163743-minicpm5-2b-f9fc/generations.jsonl"
ITEMS = DEPOT / "eval/jeu/dev1/items.jsonl"
SORTIE = RACINE / "docs" / "assets" / "demo-assistant.gif"
LARGEUR, HAUTEUR = 1200, 720
COULEURS = 96


def _ligne(chemin: Path, cle: str, valeur: str) -> dict:
    with chemin.open(encoding="utf-8") as f:
        for ligne in f:
            if valeur in ligne:
                objet = json.loads(ligne)
                if objet.get(cle) == valeur:
                    return objet
    raise SystemExit(f"{valeur} introuvable dans {chemin}")


PONT = """
(() => {
  window.__appels = [];
  window.pywebview = { api: {
    async appeler(nom, ...args) {
      window.__appels.push([nom, ...args]);
      if (nom === 'modeles.comparatif_modeles')
        return { ok: true, comparatif: window.__comparatif };
      if (nom === 'observabilite.synthese') return { ok: true, synthese: window.__synthese };
      if (nom === 'observabilite.methode')
        return { ok: true, methode: { disponible: false } };
      if (nom === 'reglages.modeles')
        return { ok: true, actif: 'minicpm5-2b', choisi: 'minicpm5-2b',
          modeles: [{ slug: 'minicpm5-2b', nom: 'MiniCPM5-2B' }] };
      if (nom === 'reglages.lire') return { ok: true, reglages: { taille_texte: 100 } };
      if (nom === 'reglages.fournisseurs_externes') return { ok: true, max: 3, en_cours: null,
        fournisseurs: [], presets: [
        { nom: 'mistral', libelle: 'Mistral AI', url_base: 'https://api.mistral.ai/v1',
          modeles: ['mistral-small-latest'], parametres_libres: false },
        { nom: 'ovh', libelle: 'OVHcloud', url_base: 'https://oai.endpoints.kepler.ai.cloud.ovh.net/v1',
          modeles: [], parametres_libres: false, acces_gratuit: true },
        { nom: 'openrouter', libelle: 'OpenRouter', url_base: 'https://openrouter.ai/api/v1',
          modeles: [], parametres_libres: false },
        { nom: 'generique', libelle: 'Autre', url_base: null, modeles: [],
          parametres_libres: true },
      ] };
      if (nom.startsWith('mode.'))
        return { ok: true, mode: 'hors_ligne', hors_ligne: true, force: true, entrees: [] };
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


def _morceaux(texte: str, taille: int = 5) -> list[str]:
    mots = re.findall(r"\S+\s*", texte)
    return ["".join(mots[i : i + taille]) for i in range(0, len(mots), taille)]


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--sortie", type=Path, default=SORTIE)
    args = parseur.parse_args()

    question = _ligne(ITEMS, "id", "Q-501")["entree"]
    generation = _ligne(GENERATIONS, "item_id", "Q-501")
    canonique = generation["sortie_canonique"]
    usage = next(e["usage"] for e in generation["trace"] if e["type"] == "fin")
    avertissement = next(e for e in generation["trace"] if e["type"] == "avertissement")
    details = {
        "appels": 1,
        "tokens_entree": usage["prompt_tokens"],
        "tokens_sortie": usage["completion_tokens"],
        "estime": False,
        "duree_ms": generation["duree_ms"],
        "cout_eur": 0.0,
        "local": True,
        "modeles": ["minicpm5-2b"],
        "motifs": [],
    }
    ligne_obs = {
        "fournisseur": "local",
        "modele": "minicpm5-2b",
        "appels": 1,
        "sauts": 0,
        "tokens_entree": details["tokens_entree"],
        "tokens_sortie": details["tokens_sortie"],
        "estime": False,
        "cout_eur": 0.0,
        "debit_tokens_s": round(usage["completion_tokens"] / (generation["duree_ms"] / 1000), 1),
    }
    synthese = {
        "mois": "2026-10",
        "jour": "2026-10-22",
        "par_modele_jour": [ligne_obs],
        "par_modele_mois": [ligne_obs],
        "plafonds": [],
        "derniers": [
            {
                "horodatage": "2026-10-22T09:00:00+00:00",
                "tache": "Q",
                "fournisseur": "local",
                "modele": "minicpm5-2b",
                "tokens_entree": details["tokens_entree"],
                "tokens_sortie": details["tokens_sortie"],
                "estime": False,
                "duree_ms": generation["duree_ms"],
                "cout_eur": 0.0,
                "co2e_g": None,
                "motif": None,
            }
        ],
    }
    comparatif = json.loads(
        (UI / "donnees" / "comparatif-modeles.json").read_text(encoding="utf-8")
    )

    serveur = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(_Silencieux, directory=str(UI))
    )
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{serveur.server_port}/index.html"

    images: list[tuple[Image.Image, int]] = []
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge", headless=True)
        contexte = nav.new_context(viewport={"width": LARGEUR, "height": HAUTEUR})
        contexte.add_init_script(
            "try { localStorage.setItem('slmsp.bienvenue-vue', 'true'); } catch {}"
        )
        for nom, valeur in (("comparatif", comparatif), ("synthese", synthese)):
            contexte.add_init_script(f"window.__{nom} = {json.dumps(valeur)};")
        contexte.add_init_script(PONT)
        page = contexte.new_page()
        page.set_default_timeout(30_000)

        def photo(duree: int) -> None:
            images.append((Image.open(io.BytesIO(page.screenshot())).convert("RGB"), duree))

        def recevoir(evenements: list[dict]) -> None:
            page.evaluate("(e) => window.slmspRecevoir(e)", evenements)

        page.goto(url)
        page.wait_for_function("() => window.slmsp !== undefined", polling=50)
        recevoir([{"type": "pret"}])
        page.evaluate("window.slmsp.activer('Q')")
        page.wait_for_selector("#saisie")
        photo(1000)

        page.fill("#saisie", question)
        photo(1500)
        page.keyboard.press("Enter")
        page.wait_for_selector(".message-utilisateur")
        for morceau in _morceaux(canonique["texte"]):
            recevoir([{"type": "jeton", "texte": morceau}])
            photo(220)
        recevoir(
            [
                {"type": "sources", "sources": canonique["sources"]},
                avertissement,
                {
                    "type": "fin",
                    "raison": "terminee",
                    "usage": None,
                    "urls_inventees": [],
                    "details": details,
                },
            ]
        )
        page.wait_for_selector("#vue-Q .details-appel")
        photo(2200)
        page.locator("#vue-Q .details-appel summary").click()
        page.locator("#vue-Q .details-appel").scroll_into_view_if_needed()
        photo(2600)

        page.evaluate("window.slmsp.activer('MO')")
        page.wait_for_selector("#vue-MO .modeles-table")
        page.evaluate(
            "document.querySelectorAll('#vue-MO details[open]').forEach((d) => (d.open = false))"
        )
        photo(2200)
        page.locator("#vue-MO .modeles-bascule").first.click()
        photo(2000)

        if page.get_attribute("#plus-bascule", "aria-expanded") != "true":
            page.click("#plus-bascule")
        page.click("#tache-OB")
        page.wait_for_selector("#vue-OB .observabilite-table")
        photo(2500)

        page.click("#bouton-parametres")
        page.wait_for_selector("#dialogue-parametres[open] #parametres-externe-ajouter")
        page.locator("#parametres-externe-ajouter").scroll_into_view_if_needed()
        photo(1000)
        page.locator("#parametres-externe-ajouter").click()
        premier = page.locator(".parametres-fournisseur").nth(0)
        premier.locator("select").select_option("mistral")
        premier.scroll_into_view_if_needed()
        photo(2500)
        nav.close()
    serveur.shutdown()

    quantifiees = [
        im.convert("P", palette=Image.Palette.ADAPTIVE, colors=COULEURS, dither=Image.Dither.NONE)
        for im, _ in images
    ]
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    quantifiees[0].save(
        args.sortie,
        save_all=True,
        append_images=quantifiees[1:],
        duration=[d for _, d in images],
        loop=0,
        optimize=True,
        disposal=1,
    )
    total = sum(d for _, d in images) / 1000
    taille = args.sortie.stat().st_size / 1e6
    print(f"{args.sortie} : {len(images)} images, {total:.1f} s, {taille:.2f} Mo, {LARGEUR} px")


if __name__ == "__main__":
    main()
