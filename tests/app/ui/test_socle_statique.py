"""Story 12.4 : contrôles statiques du socle de l'interface (sans navigateur).

Couvre l'absence de ressource externe dans les sources
(critère 5) et la déclaration d'avance des modules de vue (convention §3 des Epics 12 et 13).
"""

from __future__ import annotations

import re
from pathlib import Path

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"
VUES = [
    "question",
    "recherche",
    "redaction",
    "correction",
    "resume",
    "traduction",
    "courrier",
    "mode",
    "parametres",
    "historique",
    "retours",
    "verification",
]


VUES_REALISEES = {
    "mode",
    "question",
    "recherche",
    "redaction",
    "parametres",
    "correction",
    "historique",
    "retours",
    "resume",
    "courrier",
    "traduction",
    "verification",
}  # stories 12.7 à 12.11, 13.1 à 13.4, 13.6


def test_modules_de_vue_declares_d_avance() -> None:
    for vue in VUES:
        assert (UI / "css" / f"{vue}.css").is_file(), vue
        module = (UI / "js" / "vues" / f"{vue}.js").read_text(encoding="utf-8")
        assert "export function monter" in module, vue
        if vue not in VUES_REALISEES:
            assert "non disponible" in module, vue
        assert f'href="css/{vue}.css"' in (UI / "index.html").read_text(encoding="utf-8")


def test_socle_js_declare() -> None:
    for nom in ("app", "pont-client", "bus", "clavier", "annonces", "pont-factice"):
        assert (UI / "js" / "socle" / f"{nom}.js").is_file(), nom


def test_index_csp_et_aucune_ressource_externe() -> None:
    html = (UI / "index.html").read_text(encoding="utf-8")
    assert "default-src 'self'" in html
    assert "<script>" not in html and " style=" not in html  # rien d'inline sous la CSP
    for fichier in UI.rglob("*"):
        if fichier.suffix not in {".html", ".css", ".js", ".svg"}:
            continue
        texte = fichier.read_text(encoding="utf-8")
        texte = texte.replace("http://www.w3.org/2000/svg", "")
        assert not re.search(r"https?://|//cdn|@import", texte), fichier.name


def test_icones_locales_utilisees_existent() -> None:
    css = (UI / "css" / "socle.css").read_text(encoding="utf-8")
    for chemin in re.findall(r'url\("\.\./(icones/[\w-]+\.svg)"\)', css):
        assert (UI / chemin).is_file(), chemin


def test_aucun_innerhtml_dans_les_composants_et_vues() -> None:
    """Le contenu du modèle n'entre dans le DOM que par `textContent` (story 12.7)."""
    interdit = re.compile(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|\beval\(")
    for chemin in (UI / "js").rglob("*.js"):
        assert not interdit.search(chemin.read_text(encoding="utf-8")), chemin.name
