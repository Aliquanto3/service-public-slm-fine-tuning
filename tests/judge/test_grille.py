"""Lecture de la grille du Juge : sections, gabarit, empreintes et erreurs."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.items import CODES
from slmsp.judge.grille import PLACEHOLDERS, Grille, charger_grille

GRILLE_MINIMALE = """---
title: Grille
version: 9.1
---

# Grille

## Principes communs
- Principe.

## Q : Question

Critères Q.

## NR : Non-régression

Critères NR.

## Prompt du Juge (gabarit)

> Tâche {tache}.
>
> GRILLE : {section de la Tâche}
> ENTRÉE : {entree}
> RÉFÉRENCES : {champs de référence}
> SORTIE À ÉVALUER : {sortie}
"""


def ecrire(tmp_path: Path, texte: str) -> Path:
    chemin = tmp_path / "grille.md"
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def test_grille_du_depot(grille: Grille) -> None:
    assert grille.version == "1.0"
    assert set(grille.sections) == set(CODES)
    section = grille.section("Q")
    assert section.code == "Q"
    assert section.texte.startswith("## Principes communs")
    assert "## Q : Question" in section.texte
    assert "## RD" not in section.texte and "## Prompt du Juge" not in section.texte
    assert section.sha256 == sha256_hex(section.texte)
    assert grille.section("LC").sha256 != section.sha256


def test_gabarit_du_depot(grille: Grille) -> None:
    assert grille.gabarit.startswith("Tu évalues la sortie")
    assert all(p in grille.gabarit for p in PLACEHOLDERS)
    assert not any(ligne.startswith(">") for ligne in grille.gabarit.splitlines())
    assert grille.sha_gabarit == sha256_hex(grille.gabarit)


def test_grille_minimale(tmp_path: Path) -> None:
    grille = charger_grille(ecrire(tmp_path, GRILLE_MINIMALE))
    assert grille.version == "9.1"
    assert (
        grille.section("NR").texte
        == "## Principes communs\n- Principe.\n\n## NR : Non-régression\n\nCritères NR."
    )
    assert grille.gabarit.splitlines()[1] == ""  # ligne `>` seule conservée vide


def test_lecture_stable(tmp_path: Path) -> None:
    chemin = ecrire(tmp_path, GRILLE_MINIMALE)
    premiere, seconde = charger_grille(chemin), charger_grille(chemin)
    assert premiere.section("Q") == seconde.section("Q")
    assert premiere.sha_gabarit == seconde.sha_gabarit


@pytest.mark.parametrize(
    ("remplacer", "par"),
    [
        ("---\ntitle: Grille\nversion: 9.1\n---\n", ""),
        ("version: 9.1\n", ""),
        ("## Principes communs", "## Principes"),
        ("## Prompt du Juge (gabarit)", "## Autre chose"),
        ("> SORTIE À ÉVALUER : {sortie}\n", ""),
        ("{champs de référence}", "{references}"),
    ],
    ids=[
        "sans-front-matter",
        "sans-version",
        "sans-principes",
        "sans-gabarit",
        "placeholder-sortie-absent",
        "placeholder-references-absent",
    ],
)
def test_grille_invalide(tmp_path: Path, remplacer: str, par: str) -> None:
    assert remplacer in GRILLE_MINIMALE
    with pytest.raises(ConfigurationInvalide):
        charger_grille(ecrire(tmp_path, GRILLE_MINIMALE.replace(remplacer, par)))


@pytest.mark.parametrize(
    "section",
    [
        "## Q : Question bis\n\nAutres critères Q.\n\n",
        "## Principes communs\n- Autre principe.\n\n",
        "## Prompt du Juge (gabarit) bis\n\n> {tache} {section de la Tâche} {entree} "
        "{champs de référence} {sortie}\n\n",
    ],
    ids=["tache", "principes", "gabarit"],
)
def test_section_en_double(tmp_path: Path, section: str) -> None:
    texte = GRILLE_MINIMALE.replace("## NR : Non-régression", section + "## NR : Non-régression")
    with pytest.raises(ConfigurationInvalide, match="en double"):
        charger_grille(ecrire(tmp_path, texte))


def test_section_absente(tmp_path: Path) -> None:
    grille = charger_grille(ecrire(tmp_path, GRILLE_MINIMALE))
    with pytest.raises(ConfigurationInvalide, match="CT"):
        grille.section("CT")


def test_grille_illisible(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_grille(tmp_path / "absente.md")
    chemin = tmp_path / "binaire.md"
    chemin.write_bytes(b"\xff\xfe\x00grille")
    with pytest.raises(ConfigurationInvalide):
        charger_grille(chemin)
