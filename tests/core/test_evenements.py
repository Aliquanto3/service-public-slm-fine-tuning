"""Évènements typés du Harnais (critère 10, story 1.3, AD-14)."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from slmsp.core.canonique import json_canonique
from slmsp.core.evenements import (
    AppelNonConforme,
    AppelOutil,
    Avertissement,
    Erreur,
    Fin,
    Jeton,
    Progression,
    Repli,
    ResultatOutil,
    Source,
    Sources,
    depuis_dict,
    vers_dict,
)

EVENEMENTS = [
    Jeton(texte="<jeton-factice> é"),
    AppelOutil(id="a1", nom="search_datasets", arguments={"q": "x", "page": 1}),
    ResultatOutil(id="a1", nom="search_datasets", resultat={"lignes": [1, 2]}),
    ResultatOutil(id="a2", nom="query_resource_data", resultat="échec", erreur=True),
    AppelNonConforme(nom=None, arguments_bruts="{pas du json", motif="JSON invalide"),
    Sources(
        sources=[
            Source(titre="<titre>", url="https://www.service-public.gouv.fr/x", origine="index"),
            Source(
                titre="<titre>",
                url="https://www.data.gouv.fr/d",
                origine="mcp",
                date="2026-10-01",
                extrait="<extrait>",
            ),
        ]
    ),
    Avertissement(code="hors-ligne", message="<message>"),
    Progression(etape="indexation", fait=3, total=None),
    Repli(motif="MCP indisponible", vers="index"),
    Fin(raison="terminee", usage={"prompt_tokens": 10, "completion_tokens": 5}),
    Erreur(code="serveur", message="<message>"),
]

TYPES = {
    "jeton",
    "appel-outil",
    "resultat-outil",
    "appel-non-conforme",
    "sources",
    "avertissement",
    "progression",
    "repli",
    "fin",
    "erreur",
}


@pytest.mark.parametrize("evenement", EVENEMENTS, ids=lambda e: type(e).__name__)
def test_aller_retour(evenement) -> None:
    donnees = vers_dict(evenement)
    assert donnees["type"] in TYPES
    assert json.loads(json.dumps(donnees)) == donnees
    assert depuis_dict(donnees) == evenement
    assert type(depuis_dict(donnees)) is type(evenement)
    assert depuis_dict(json.loads(json_canonique(donnees))) == evenement
    assert json_canonique(vers_dict(evenement)) == json_canonique(donnees)


def test_dix_types_couverts() -> None:
    assert {vers_dict(e)["type"] for e in EVENEMENTS} == TYPES


def test_type_inconnu() -> None:
    with pytest.raises(ValidationError):
        depuis_dict({"type": "inconnu", "texte": "x"})
    with pytest.raises(ValidationError):
        depuis_dict({"texte": "x"})
    with pytest.raises(ValidationError):
        depuis_dict({"type": "jeton", "texte": "x", "extra": 1})


def test_evenements_figes() -> None:
    with pytest.raises(ValidationError):
        Jeton(texte="a").texte = "b"  # type: ignore[misc]


def test_valeurs_refusees() -> None:
    with pytest.raises(ValidationError):
        Fin(raison="autre")
    with pytest.raises(ValidationError):
        Repli(motif="x", vers="mcp")
    with pytest.raises(ValidationError):
        Source(titre="t", url="u", origine="web")
    with pytest.raises(ValidationError):
        Progression(etape="x", fait=-1)
    with pytest.raises(ValidationError):
        Progression(etape="x", fait=0, total=-1)
