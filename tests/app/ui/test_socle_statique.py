"""Story 12.4 : contrôles statiques du socle de l'interface (sans navigateur).

Couvre les contrastes des jetons (critère 4), l'absence de ressource externe dans les sources
(critère 5) et la déclaration d'avance des modules de vue (convention §3 des Epics 12 et 13).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

UI = Path(__file__).resolve().parents[3] / "src" / "slmsp" / "app" / "ui"
VUES = [
    "question",
    "recherche",
    "redaction",
    "correction",
    "resume",
    "courrier",
    "traduction",
    "mode",
    "parametres",
    "historique",
    "retours",
    "verification",
]


def _jetons() -> dict[str, str]:
    texte = (UI / "css" / "jetons.css").read_text(encoding="utf-8")
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", texte))


def _luminance(couleur: str) -> float:
    canaux = [int(couleur[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    haut, bas = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (haut + 0.05) / (bas + 0.05)


# Couples texte / fond réellement employés (composants de DESIGN.md).
COUPLES = [
    ("ink", "surface"),
    ("ink", "surface-alt"),
    ("ink", "primary-soft"),
    ("ink", "accent-soft"),
    ("ink-soft", "surface"),
    ("ink-soft", "surface-alt"),
    ("ink-soft", "line"),
    ("primary", "surface"),
    ("primary", "surface-alt"),
    ("primary", "primary-soft"),
    ("on-primary", "primary"),
    ("on-primary", "primary-hover"),
]


def test_jetons_de_design_md_presents() -> None:
    jetons = _jetons()
    attendus = {
        "primary": "#451dc7",
        "primary-hover": "#250f6b",
        "primary-soft": "#ede7fe",
        "accent": "#04f06a",
        "ink": "#0a0a14",
        "ink-soft": "#4a4a5e",
        "gray": "#8a8a9e",
        "line": "#e6e6ec",
        "surface": "#ffffff",
        "surface-alt": "#f6f5fa",
        "warning": "#ffca4a",
        "danger": "#ff2a49",
        "focus-ring": "#451dc7",
    }
    for nom, valeur in attendus.items():
        assert jetons[nom].lower() == valeur, nom


@pytest.mark.parametrize(("texte", "fond"), COUPLES)
def test_contraste_texte_fond_au_moins_4_5(texte: str, fond: str) -> None:
    jetons = _jetons()
    assert contraste(jetons[texte], jetons[fond]) >= 4.5


def test_couleurs_d_etat_jamais_en_texte() -> None:
    """Vert, jaune, rouge (et gris décoratif) : jamais dans une propriété `color` (UX-DR1)."""
    motif = re.compile(r"(?<![\w-])color\s*:\s*var\(--(accent|accent-soft|warning|danger|gray)\)")
    for css in (UI / "css").glob("*.css"):
        assert not motif.search(css.read_text(encoding="utf-8")), css.name


def test_modules_de_vue_declares_d_avance() -> None:
    for vue in VUES:
        assert (UI / "css" / f"{vue}.css").is_file(), vue
        module = (UI / "js" / "vues" / f"{vue}.js").read_text(encoding="utf-8")
        assert "export function monter" in module, vue
        if vue not in ("question", "recherche"):  # livrées par la story 12.7
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
