"""Nettoyage version 3 (story S5) : la tête d'un CR ou d'un CT n'est jamais retirée comme titre."""

from __future__ import annotations

import json

import pytest

from slmsp.core.canonique import json_canonique
from slmsp.core.nettoyage import (
    TACHES_TETE_GARDEE,
    VERSION_NETTOYAGE,
    VERSIONS_NETTOYAGE,
    analyser_cible,
    ligne_nettoyee,
    nettoyer_cible,
    verifier_nettoyage,
)

TETE = "**<titre>**\n\n<corps>"


def test_version_courante_et_versions_rejouables() -> None:
    assert VERSION_NETTOYAGE == 3
    assert VERSIONS_NETTOYAGE == {1, 2, 3}
    assert TACHES_TETE_GARDEE == {"CR", "CT"}


@pytest.mark.parametrize("tache", ["CR", "CT"])
def test_cr_et_ct_gardent_leur_tete(tache: str) -> None:
    assert analyser_cible(TETE, 3, tache) == (TETE, None, False)
    assert nettoyer_cible("Voici <x> :\n\n" + TETE, 3, tache) == TETE  # préambule retiré


@pytest.mark.parametrize("tache", ["Q", "RD", "LC", "RE", "CO", "generique", None])
def test_autres_taches_gardent_la_regle_du_titre(tache: str | None) -> None:
    assert analyser_cible(TETE, 3, tache) == ("<corps>", None, True)


@pytest.mark.parametrize("tache", ["CR", "CT"])
def test_version_2_inchangee_pour_cr_et_ct(tache: str) -> None:
    """Un jeu nettoyé en version 2 se revérifie avec sa règle : titre retiré, même pour CR."""
    assert nettoyer_cible(TETE, 2, tache) == "<corps>"


def _ligne(tache: str, cible: str) -> bytes:
    return json_canonique(
        {
            "messages": [
                {"role": "user", "content": "<question>"},
                {"role": "assistant", "content": cible},
            ],
            "tache": tache,
        }
    )


def test_ligne_nettoyee_lit_la_tache_de_la_ligne() -> None:
    cr, q = _ligne("CR", TETE), _ligne("Q", TETE)
    assert json.loads(ligne_nettoyee(cr, 3))["messages"][-1]["content"] == TETE
    assert json.loads(ligne_nettoyee(q, 3))["messages"][-1]["content"] == "<corps>"
    assert json.loads(ligne_nettoyee(cr, 2))["messages"][-1]["content"] == "<corps>"


def test_verification_par_version() -> None:
    source = _ligne("CR", TETE) + b"\n" + _ligne("Q", TETE) + b"\n"
    v3 = ligne_nettoyee(_ligne("CR", TETE), 3) + b"\n" + ligne_nettoyee(_ligne("Q", TETE), 3)
    verifier_nettoyage(v3, source, [], 3)
    with pytest.raises(Exception, match="nettoyage"):
        verifier_nettoyage(v3, source, [], 2)
