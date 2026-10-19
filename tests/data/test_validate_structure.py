"""Contrôles de structure de `data validate` (story S5) : CR, CT, LC.

Fixtures factices : seuls les titres de section, la ligne d'objet, la formule de politesse et
les crochets, que le contrôle cherche, sont écrits ; le reste est `<…>`.
"""

from __future__ import annotations

import pytest

from slmsp.core.schemas.rejet_donnees import MOTIFS_VALIDATION
from slmsp.data.validate import SECTIONS_CR, _controler_structure, _Rejet

CR = "Participants\n<p>\n\n## Points abordés\n<p>\n\n**Décisions :**\n<p>\n\nActions : <p>"
CT = "<expediteur>\n\nObjet : <objet>\n\n<corps> [<champ>]\n\nVeuillez agréer <formule>.\n"


def motif(texte: str, tache: str, fournis: tuple[str, ...] = ()) -> str | None:
    try:
        _controler_structure(texte, tache, list(fournis))
    except _Rejet as exc:
        return exc.motif
    return None


def test_nouveaux_motifs_declares() -> None:
    assert {"cr_sections_manquantes", "ct_format_incomplet", "lc_valeur_perdue"} <= set(
        MOTIFS_VALIDATION
    )


def test_cr_conforme() -> None:
    assert motif(CR, "CR") is None


@pytest.mark.parametrize("section", SECTIONS_CR)
def test_cr_section_manquante(section: str) -> None:
    texte = "\n".join(
        ligne for ligne in CR.split("\n") if section.casefold() not in ligne.casefold()
    )
    assert motif(texte, "CR") == "cr_sections_manquantes"


def test_cr_titre_en_milieu_de_ligne_ne_compte_pas() -> None:
    texte = CR.replace("Actions : <p>", "<p> Actions <p>")
    assert motif(texte, "CR") == "cr_sections_manquantes"


def test_ct_conforme() -> None:
    assert motif(CT, "CT") is None


@pytest.mark.parametrize(
    "texte",
    [
        CT.replace("Objet : <objet>", "<objet>"),
        CT.replace("Veuillez agréer <formule>.", "<fin>."),
        CT.replace("[<champ>]", "<champ>"),
        CT.replace("[<champ>]", "[<lien>](https://exemple.invalid)"),
        CT.replace("[<champ>]", "[123]"),
    ],
)
def test_ct_format_incomplet(texte: str) -> None:
    assert motif(texte, "CT") == "ct_format_incomplet"


def test_lc_conforme() -> None:
    source = "<texte> 1 500 euros avant le 15 mars 2026"
    assert motif("<sortie> 1500 euros, au plus tard le 15/03/2026", "LC", (source,)) is None


@pytest.mark.parametrize(
    "sortie",
    ["<sortie> avant le 15 mars 2026", "<sortie> 1 500 euros", "<sortie> 1 500 euros en 2026"],
)
def test_lc_valeur_perdue(sortie: str) -> None:
    source = "<texte> 1 500 euros avant le 15 mars 2026"
    assert motif(sortie, "LC", (source,)) == "lc_valeur_perdue"


def test_autres_taches_non_controlees() -> None:
    assert motif("<reponse>", "Q") is None
    assert motif("<reponse>", "RE", ("<texte> 1 500 euros",)) is None
