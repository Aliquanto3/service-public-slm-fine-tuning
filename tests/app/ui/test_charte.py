"""Story 3.7 : l'interface suit la charte générique v2.1 (contrôles statiques, sans navigateur).

Les valeurs sont lues dans `jetons.css`, normalisées (minuscules, sans retours chariot), jamais
comparées sur les octets bruts. Le thème est sombre par défaut ; le clair vient de la préférence
du système ou de `[data-theme="light"]`.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[3]
UI = RACINE / "src" / "slmsp" / "app" / "ui"
CSS = UI / "css"
GABARIT = RACINE / "outils" / "audit_verdicts.gabarit.html"

# Empreinte des couples `--jeton: #hex` des deux thèmes, tels que la charte v2.1 les publie.
# Pour la mettre à jour après une nouvelle version de la charte : relancer `_empreinte()`.
EMPREINTE_JETONS = "49544891df9cbdb7a7b68f298793b7e7e36e49f75c79f5651a40be10ffb6ad8b"


def _lire(chemin: Path) -> str:
    return chemin.read_text(encoding="utf-8").replace("\r\n", "\n")


def _bloc(texte: str, debut: str) -> str:
    """Corps du premier bloc `{ … }` qui suit `debut` (blocs sans accolade imbriquée)."""
    i = texte.index(debut)
    j = texte.index("{", i)
    return texte[j + 1 : texte.index("}", j)]


def _declarations(bloc: str) -> dict[str, str]:
    return {nom: val.strip().lower() for nom, val in re.findall(r"--([\w-]+):\s*([^;}]+)", bloc)}


def _themes() -> tuple[dict[str, str], dict[str, str]]:
    texte = _lire(CSS / "jetons.css")
    sombre = _declarations(_bloc(texte, ":root {"))
    clair = _declarations(_bloc(texte, '[data-theme="clair"]'))
    return sombre, clair


def _resoudre(theme: dict[str, str], nom: str) -> str:
    valeur = theme[nom]
    while valeur.startswith("var("):
        valeur = theme[valeur[len("var(--") : -1]]
    return valeur


def _luminance(couleur: str) -> float:
    canaux = [int(couleur[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    haut, bas = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (haut + 0.05) / (bas + 0.05)


def _empreinte() -> str:
    sombre, clair = _themes()
    couples = sorted(
        f"{theme}:{nom}:{val}"
        for theme, jetons in (("s", sombre), ("c", clair))
        for nom, val in jetons.items()
        if re.fullmatch(r"#[0-9a-f]{6}", val)
    )
    return hashlib.sha256("\n".join(couples).encode()).hexdigest()


# Couples texte / fond réellement employés par les feuilles de style (seuil 4,5:1).
TEXTE = [
    ("texte", "fond"),
    ("texte", "surface"),
    ("texte", "surface-alt"),
    ("texte", "primaire-doux"),
    ("texte", "accent-doux"),
    ("texte", "alerte-doux"),
    ("texte-attenue", "fond"),
    ("texte-attenue", "surface"),
    ("texte-attenue", "surface-alt"),
    ("primaire", "fond"),
    ("primaire", "surface"),
    ("primaire", "surface-alt"),
    ("primaire", "primaire-doux"),
    ("primaire-vif", "primaire-doux"),
    ("sur-bouton", "bouton"),
    ("sur-bouton", "bouton-survol"),
    ("sur-encre", "encre-pleine"),
]

# Contours, focus, points, pastilles, icônes et pictogramme (seuil 3:1).
NON_TEXTE = [
    ("trait-fort", "fond"),
    ("trait-fort", "surface"),
    ("trait-fort", "surface-alt"),
    ("focus", "fond"),
    ("focus", "surface"),
    ("focus", "surface-alt"),
    ("primaire", "surface"),
    ("primaire", "surface-alt"),
    ("neutre", "surface"),
    ("accent", "fond"),
    ("accent", "surface"),
    ("accent", "surface-alt"),
    ("alerte-texte", "surface"),
    ("alerte-texte", "surface-alt"),
    ("alerte-texte", "alerte-doux"),
    ("erreur", "surface-alt"),
    ("texte", "primaire-doux"),
    ("picto-tuile", "surface-alt"),
    ("picto-barres", "picto-tuile"),
    ("picto-point", "picto-tuile"),
]


def test_les_deux_themes_ont_les_memes_jetons() -> None:
    sombre, clair = _themes()
    couleurs_s = {n for n, v in sombre.items() if v.startswith(("#", "var("))}
    couleurs_c = {n for n, v in clair.items() if v.startswith(("#", "var("))}
    assert couleurs_s == couleurs_c
    assert {
        "fond",
        "texte",
        "primaire",
        "bouton",
        "sur-bouton",
        "trait-fort",
        "focus",
    } <= couleurs_s


def test_valeurs_cles_de_la_charte_v21() -> None:
    sombre, clair = _themes()
    assert (sombre["fond"], clair["fond"]) == ("#0f1318", "#f6f8fb")
    assert (sombre["bouton"], clair["bouton"]) == ("#e8ecf2", "#121821")
    assert (sombre["primaire"], clair["primaire"]) == ("#8db0f7", "#1d5bc2")
    assert (sombre["accent"], clair["accent"]) == ("#e3c26b", "#8f6300")
    assert (sombre["focus"], clair["focus"]) == ("#9ec0ff", "#1f5fd1")


def test_jetons_identiques_a_la_charte() -> None:
    assert _empreinte() == EMPREINTE_JETONS


def test_sombre_d_abord_et_clair_selon_le_systeme() -> None:
    texte = _lire(CSS / "jetons.css")
    sombre, clair = _themes()
    assert _bloc(texte, ":root {").count("color-scheme: dark") == 1
    # le thème clair du système reprend exactement le thème clair forcé
    media = _bloc(texte, "@media (prefers-color-scheme: light)")
    media = texte[texte.index("@media (prefers-color-scheme: light)") :]
    media = _declarations(_bloc(media, ":root:not("))
    assert media == clair
    forcee = _declarations(_bloc(texte, '\n[data-theme="sombre"]'))
    assert forcee == {n: v for n, v in sombre.items() if n in forcee}
    assert len(forcee) == len(_declarations(_bloc(texte, '\n[data-theme="clair"]')))
    assert '[data-theme="light"]' in texte and '[data-theme="dark"]' in texte


def test_aucun_script_ne_force_un_theme() -> None:
    for chemin in (UI / "js").rglob("*.js"):
        assert "data-theme" not in chemin.read_text(encoding="utf-8"), chemin.name
        assert "dataset.theme" not in chemin.read_text(encoding="utf-8"), chemin.name


@pytest.mark.parametrize("theme", [0, 1], ids=["sombre", "clair"])
@pytest.mark.parametrize(("texte", "fond"), TEXTE)
def test_contraste_du_texte_au_moins_4_5(texte: str, fond: str, theme: int) -> None:
    jetons = _themes()[theme]
    assert contraste(_resoudre(jetons, texte), _resoudre(jetons, fond)) >= 4.5


@pytest.mark.parametrize("theme", [0, 1], ids=["sombre", "clair"])
@pytest.mark.parametrize(("marque", "fond"), NON_TEXTE)
def test_contraste_des_marques_au_moins_3(marque: str, fond: str, theme: int) -> None:
    jetons = _themes()[theme]
    assert contraste(_resoudre(jetons, marque), _resoudre(jetons, fond)) >= 3.0


def _regles(texte: str) -> list[tuple[str, str]]:
    texte = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    return [(s.strip(), c) for s, c in re.findall(r"([^{}]+)\{([^{}]*)\}", texte)]


SELECTEUR_DE_BOUTON = re.compile(
    r"bouton|button|pressed|expanded|selected|chip|onglet|pouce|bascule|exemple|\.tache|pastille"
)
APLAT_BLEU = re.compile(
    r"background(?:-color)?\s*:[^;]*var\(--(?:primaire|primaire-vif|sur-primaire)[,)]"
)


def test_le_bleu_n_est_jamais_un_aplat_de_bouton() -> None:
    """Bouton, bouton à bascule, bouton d'information, survol compris : jamais un aplat bleu."""
    fautes = []
    for css in sorted(CSS.glob("*.css")):
        for selecteur, corps in _regles(_lire(css)):
            if "::before" in selecteur or "::after" in selecteur:
                continue  # repère de la tâche courante : trait de 3 px, pas un bouton
            if SELECTEUR_DE_BOUTON.search(selecteur) and APLAT_BLEU.search(corps):
                fautes.append(f"{css.name}: {selecteur}")
    assert fautes == []


def test_le_garde_fou_de_l_aplat_bleu_voit_un_survol() -> None:
    corps = ".citation-chip:hover { background: var(--primaire); }"
    assert [s for s, c in _regles(corps) if SELECTEUR_DE_BOUTON.search(s) and APLAT_BLEU.search(c)]
    assert not APLAT_BLEU.search("background: var(--primaire-doux);")


def test_bouton_principal_neutre() -> None:
    corps = {s: c for css in CSS.glob("*.css") for s, c in _regles(_lire(css))}
    principal = corps[".bouton-primaire"]
    assert "background: var(--bouton)" in principal
    assert "color: var(--sur-bouton)" in principal
    assert "var(--bouton-survol)" in corps[".bouton-primaire:hover:not(:disabled)"]
    assert "1px solid var(--trait-fort)" in corps[".bouton-secondaire"]


def test_focus_et_filet_or() -> None:
    socle = _lire(CSS / "socle.css")
    assert re.search(r":focus-visible \{\s*outline: 2px solid var\(--focus\)", socle)
    filet = {s: c for s, c in _regles(socle)}[".bienvenue h2::after"]
    assert "background: var(--accent)" in filet
    assert "width: 96px" in filet and "height: 4px" in filet


def test_aucun_hex_hors_des_jetons() -> None:
    fichiers = [p for p in CSS.glob("*.css") if p.name != "jetons.css"]
    fichiers += [UI / "index.html", *(UI / "icones").glob("*.svg")]
    # `favicon.svg` est exclu, et lui seul : c'est une image chargée par l'onglet, qui ne lit pas
    # les variables CSS de la page. Il garde donc les hex de `dist/favicon.svg` (charte v2.1).
    fichiers += [p for p in UI.glob("charte/*.svg") if p.name != "favicon.svg"]
    for fichier in fichiers:
        texte = re.sub(r"&#\w+;", "", _lire(fichier))
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", texte), fichier.name
        assert not re.search(r"var\(--[\w-]+\s*,\s*(?:#|rgb|hsl)", texte), (
            f"repli dans var() : {fichier.name}"
        )


def test_champs_de_saisie_aux_jetons() -> None:
    """Champs, listes et zones de texte : `surface`, `texte` et `trait-fort`, pas les couleurs du
    navigateur sous `color-scheme: dark`. Couples gardés : (texte, surface) dans TEXTE,
    (trait-fort, surface) et (focus, surface) dans NON_TEXTE."""
    corps = dict(_regles(_lire(CSS / "socle.css")))
    champs = corps[':where(input:not([type="checkbox"], [type="radio"]), select, textarea)']
    for attendu in (
        "background: var(--surface)",
        "color: var(--texte)",
        "border: 1px solid var(--trait-fort)",
    ):
        assert attendu in champs
    assert "var(--texte-attenue)" in corps[":where(input, select, textarea)::placeholder"]
    for couple in (("texte", "surface"), ("texte-attenue", "surface")):
        assert couple in TEXTE
    for couple in (("trait-fort", "surface"), ("focus", "surface")):
        assert couple in NON_TEXTE


def test_icones_en_couleur_courante() -> None:
    icones = sorted((UI / "icones").glob("*.svg"))
    assert len(icones) == 14
    for icone in icones:
        assert 'stroke="currentColor"' in icone.read_text(encoding="utf-8"), icone.name


def test_etats_jamais_portes_par_la_couleur_seule_en_texte() -> None:
    """Statuts et or : jamais dans une propriété `color` (le texte passe par `texte-attenue`)."""
    motif = re.compile(
        r"(?<![\w-])color\s*:\s*var\(--(accent|accent-doux|alerte|alerte-doux|erreur|erreur-doux"
        r"|succes|succes-doux|neutre|trait|trait-fort)\)"
    )
    for css in CSS.glob("*.css"):
        assert not motif.search(_lire(css)), css.name


def test_alerte_en_trait_prend_alerte_texte() -> None:
    """`alerte` sur `alerte-doux` tombe à 2,25:1 en clair : liseré et points en `alerte-texte`."""
    for css in CSS.glob("*.css"):
        assert not re.search(r"var\(--alerte\)", _lire(css)), css.name


def test_polices_de_la_charte() -> None:
    texte = _lire(CSS / "jetons.css")
    for famille in ("Sora", "Atkinson Hyperlegible", "JetBrains Mono"):
        assert f'font-family: "{famille}"' in texte
    for chemin in re.findall(r'url\("\.\./(charte/polices/[\w.-]+)"\)', texte):
        assert (UI / chemin).is_file(), chemin
    assert len(re.findall(r"url\(", texte)) == 4
    licences = sorted(p.name for p in (UI / "charte" / "polices").glob("OFL-*.txt"))
    assert licences == ["OFL-atkinsonhyperlegible.txt", "OFL-jetbrainsmono.txt", "OFL-sora.txt"]
    sombre, _ = _themes()
    assert sombre["graisse-titres"] == "600"
    assert sombre["police-titres"].startswith("sora,")
    socle = _lire(CSS / "socle.css")
    assert "font-family: var(--police-titres)" in socle
    toutes = "".join(_lire(c) for c in CSS.glob("*.css") if c.name != "jetons.css")
    familles = re.findall(r"font-family:\s*([^;]+);", toutes)
    assert familles and all(f.startswith("var(--police-") or f == "inherit" for f in familles)


def test_favicon_et_pictogramme_branches() -> None:
    html = _lire(UI / "index.html")
    assert 'href="charte/favicon.svg"' in html
    assert (UI / "charte" / "favicon.svg").is_file()
    assert not (
        UI / "charte" / "pictogramme.svg"
    ).exists()  # inutilisé : le pictogramme est en ligne
    assert 'class="pictogramme"' in html
    assert not re.search(r"fredoka", html + "".join(_lire(c) for c in CSS.glob("*.css")), re.I)


def test_gabarit_audit_verdicts_aux_couleurs_de_la_charte() -> None:
    """Le gabarit autonome reprend les valeurs v2.1 (sombre d'abord) et respecte les contrastes."""
    texte = _lire(GABARIT)
    sombre_charte, clair_charte = _themes()
    valeurs = set(sombre_charte.values()) | set(clair_charte.values())
    hexa = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", texte)}
    assert hexa and hexa <= valeurs
    css = texte[texte.index("<style>") : texte.index("</style>")]
    sombre = _declarations(_bloc(css, ":root{"))
    clair = _declarations(_bloc(css[css.index("prefers-color-scheme:light") :], ":root{"))
    assert sombre["fond"] == "#0f1318" and clair["fond"] == "#f6f8fb"
    assert "prefers-color-scheme:dark" not in css  # sombre d'abord
    for theme in (sombre, clair):
        for t, f in [
            ("texte", "fond"),
            ("texte", "surface"),
            ("texte-attenue", "surface"),
            ("sur-bouton", "bouton"),
            ("primaire", "surface"),
            ("erreur", "erreur-doux"),
            ("texte", "alerte-doux"),
            ("texte", "primaire-doux"),
            ("texte", "surface-alt"),
            ("succes", "surface"),
            ("texte-attenue", "fond"),
        ]:
            assert contraste(theme[t], theme[f]) >= 4.5, (t, f)
        for t, f in [
            ("trait-fort", "surface"),
            ("focus", "surface"),
            ("primaire", "surface"),
            ("alerte-texte", "alerte-doux"),
            ("erreur", "surface"),
            ("accent", "fond"),
        ]:
            assert contraste(theme[t], theme[f]) >= 3.0, (t, f)
    # le bouton actif est neutre, le bleu n'est pas un aplat
    assert "button.actif{background:var(--bouton)" in texte
    assert not re.search(
        r"background:var\(--primaire\)[;}]",
        texte.replace(".pb>div{height:100%;background:var(--primaire)}", ""),
    )
