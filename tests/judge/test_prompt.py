"""Schéma de sortie fermé par Tâche (AD-12), rendu du prompt aveugle et validation."""

from __future__ import annotations

import copy
import json
from types import SimpleNamespace
from typing import Any

import jsonschema
import pytest
from pydantic import ValidationError

from slmsp.core.items import LIBELLES
from slmsp.core.schemas.verdict import Verdict
from slmsp.judge.grille import PLACEHOLDERS, Grille
from slmsp.judge.prompt import (
    ItemNonJugeable,
    SortieNonConforme,
    construire_prompt,
    estimer_tokens_entree,
    references,
    rendre_entree,
    rendre_sortie,
    schema_sortie,
    valider_sortie,
)

CRITERES = {
    "Q-001": ["exactitude", "pertinence_source"],
    "Q-002": ["exactitude", "pertinence_source", "cas_sans_reponse"],
    "RD-001": ["libelle_correct"],
    "CR-001": ["presence_elements", "absence_invention", "structure"],
    "LC-001": ["fidelite", "termes_juridiques", "clarte_percue"],
    "RE-001": ["fidelite", "presence_elements"],
    "CT-001": ["conformite"],
    "NR-001": ["exactitude"],
}
MOTS_INTERDITS = {"minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems"}


def objets(noeud: Any) -> list[dict[str, Any]]:
    """Tous les sous-schémas de type objet."""
    trouves = []
    if isinstance(noeud, dict):
        if noeud.get("type") == "object":
            trouves.append(noeud)
        for valeur in noeud.values():
            trouves.extend(objets(valeur))
    elif isinstance(noeud, list):
        for valeur in noeud:
            trouves.extend(objets(valeur))
    return trouves


def cles(noeud: Any) -> set[str]:
    if isinstance(noeud, dict):
        return set(noeud) | {c for v in noeud.values() for c in cles(v)}
    if isinstance(noeud, list):
        return {c for v in noeud for c in cles(v)}
    return set()


# --- Schéma -----------------------------------------------------------------------------------


@pytest.mark.parametrize("item_id", list(CRITERES))
def test_schema_ferme_par_tache(
    items: dict[str, Any], doublures: SimpleNamespace, item_id: str
) -> None:
    schema = schema_sortie(items[item_id])
    jsonschema.Draft202012Validator.check_schema(schema)
    for objet in objets(schema):
        assert objet["additionalProperties"] is False
        assert objet["required"] == list(objet["properties"])
    assert not cles(schema) & MOTS_INTERDITS
    assert schema["properties"]["id"] == {"type": "string", "const": item_id}
    assert list(schema["properties"]["criteres"]["properties"]) == CRITERES[item_id]
    assert schema["properties"]["confiance"]["enum"] == ["haute", "moyenne", "basse"]
    verdict = doublures.verdict_conforme(schema)
    jsonschema.validate(verdict, schema)
    assert valider_sortie(items[item_id], json.dumps(verdict), schema).id == item_id


def test_echelles(items: dict[str, Any]) -> None:
    def notes(item_id: str, critere: str) -> list[Any]:
        props = schema_sortie(items[item_id])["properties"]["criteres"]["properties"]
        return props[critere]["properties"]["note"]["enum"]

    assert notes("Q-002", "exactitude") == [0, 1, 2]
    assert notes("Q-002", "cas_sans_reponse") == [0, 1]
    assert notes("LC-001", "clarte_percue") == [1, 2, 3, 4, 5]
    assert notes("RE-001", "fidelite") == [0, 1]
    assert notes("CT-001", "conformite") == [0, 1, 2]
    cr = schema_sortie(items["CR-001"])["properties"]["criteres"]["properties"]
    element = cr["presence_elements"]["items"]["properties"]
    assert element["present"] == {"type": "number", "enum": [0, 0.5, 1]}
    assert element["ref"]["enum"] == ["D1", "D2", "D3", "D4"] + [f"A{i}" for i in range(1, 9)]
    re_ = schema_sortie(items["RE-001"])["properties"]["criteres"]["properties"]
    element = re_["presence_elements"]["items"]["properties"]
    assert element["present"] == {"type": "integer", "enum": [0, 1]}
    assert element["ref"]["enum"] == ["P1", "P2", "P3", "P4"]


def test_co_refuse(items: dict[str, Any]) -> None:
    with pytest.raises(ItemNonJugeable, match="CO"):
        schema_sortie(items["CO-001"])


def test_cr_et_re_sans_reference_refuses(items: dict[str, Any]) -> None:
    cr = items["CR-001"].model_copy(update={"decisions_reference": [], "actions_reference": None})
    re_ = items["RE-001"].model_copy(update={"points_cles_reference": None})
    for item in (cr, re_):
        with pytest.raises(ItemNonJugeable):
            schema_sortie(item)
    # Des actions seules suffisent pour CR.
    cr_actions = items["CR-001"].model_copy(update={"decisions_reference": None})
    refs = schema_sortie(cr_actions)["properties"]["criteres"]["properties"]["presence_elements"]
    assert refs["items"]["properties"]["ref"]["enum"][0] == "A1"


# --- Validation -------------------------------------------------------------------------------


def verdict_de(items: dict[str, Any], doublures: SimpleNamespace, item_id: str) -> Any:
    schema = schema_sortie(items[item_id])
    return schema, doublures.verdict_conforme(schema)


def refuse(item: Any, verdict: Any, schema: dict[str, Any]) -> None:
    texte = verdict if isinstance(verdict, str) else json.dumps(verdict)
    with pytest.raises(SortieNonConforme):
        valider_sortie(item, texte, schema)


def test_verdict_hors_echelle_refuse(items: dict[str, Any], doublures: SimpleNamespace) -> None:
    schema, verdict = verdict_de(items, doublures, "Q-001")
    for valeur in (3, -1, 1.5, "2", True, None):
        mauvais = copy.deepcopy(verdict)
        mauvais["criteres"]["exactitude"]["note"] = valeur
        refuse(items["Q-001"], mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    mauvais["confiance"] = "certaine"
    refuse(items["Q-001"], mauvais, schema)
    schema, verdict = verdict_de(items, doublures, "RE-001")
    mauvais = copy.deepcopy(verdict)
    mauvais["criteres"]["presence_elements"][0]["present"] = 0.5  # permis pour CR seulement
    refuse(items["RE-001"], mauvais, schema)


def test_verdict_avec_cle_en_trop_refuse(items: dict[str, Any], doublures: SimpleNamespace) -> None:
    schema, verdict = verdict_de(items, doublures, "CR-001")
    chemins = [
        lambda v: v,
        lambda v: v["criteres"],
        lambda v: v["criteres"]["structure"],
        lambda v: v["criteres"]["presence_elements"][0],
    ]
    for chemin in chemins:
        mauvais = copy.deepcopy(verdict)
        chemin(mauvais)["en_trop"] = 1
        refuse(items["CR-001"], mauvais, schema)


def test_verdict_incomplet_refuse(items: dict[str, Any], doublures: SimpleNamespace) -> None:
    schema, verdict = verdict_de(items, doublures, "Q-002")
    for supprimer in ("inventions", "confiance", "id"):
        mauvais = copy.deepcopy(verdict)
        del mauvais[supprimer]
        refuse(items["Q-002"], mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    del mauvais["criteres"]["cas_sans_reponse"]
    refuse(items["Q-002"], mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    del mauvais["criteres"]["exactitude"]["justification"]
    refuse(items["Q-002"], mauvais, schema)


def test_id_ref_et_json(items: dict[str, Any], doublures: SimpleNamespace) -> None:
    schema, verdict = verdict_de(items, doublures, "CR-001")
    item = items["CR-001"]
    refuse(item, "pas du JSON", schema)
    refuse(item, "[]", schema)
    mauvais = copy.deepcopy(verdict)
    mauvais["id"] = "CR-002"
    refuse(item, mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    mauvais["criteres"]["presence_elements"].pop()  # ref manquante
    refuse(item, mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    elements = mauvais["criteres"]["presence_elements"]
    elements[-1] = dict(elements[0])  # ref en double
    refuse(item, mauvais, schema)
    mauvais = copy.deepcopy(verdict)
    mauvais["criteres"]["presence_elements"][0]["ref"] = "D99"
    refuse(item, mauvais, schema)
    # Ordre libre des refs, note 0.5 permise.
    bon = copy.deepcopy(verdict)
    bon["criteres"]["presence_elements"].reverse()
    bon["criteres"]["presence_elements"][0]["present"] = 0.5
    resultat = valider_sortie(item, json.dumps(bon), schema)
    assert isinstance(resultat, Verdict) and not resultat.invalide
    assert resultat.confiance == "basse"


# --- Schéma Verdict ---------------------------------------------------------------------------


def test_verdict_invalide_ssi_vide() -> None:
    invalide = Verdict.invalide_pour("Q-001")
    assert invalide.invalide and invalide.criteres == {} and invalide.confiance is None
    assert Verdict.model_validate_json(invalide.model_dump_json()) == invalide
    with pytest.raises(ValidationError):
        Verdict(id="Q-001", criteres={}, inventions=[], confiance=None)
    with pytest.raises(ValidationError):
        Verdict(
            id="Q-001",
            criteres={"exactitude": {"note": 2, "justification": "j"}},
            inventions=[],
            confiance="haute",
            invalide=True,
        )
    with pytest.raises(ValidationError):
        Verdict(id="Q-001", criteres={}, inventions=[], confiance="haute", cle_en_trop=1)


@pytest.mark.parametrize(
    ("criteres", "confiance", "invalide"),
    [
        ({}, "haute", False),
        ({"exactitude": {"note": 2, "justification": "j"}}, None, False),
        ({"exactitude": {"note": 2, "justification": "j"}}, None, True),
        ({}, "haute", True),
    ],
    ids=[
        "valide-sans-critere",
        "valide-sans-confiance",
        "invalide-avec-critere",
        "invalide-avec-confiance",
    ],
)
def test_verdict_a_moitie_rempli_refuse(
    criteres: dict[str, Any], confiance: str | None, invalide: bool
) -> None:
    with pytest.raises(ValidationError):
        Verdict(
            id="Q-001", criteres=criteres, inventions=[], confiance=confiance, invalide=invalide
        )


def test_verdict_aller_retour(items: dict[str, Any], doublures: SimpleNamespace) -> None:
    schema, verdict = verdict_de(items, doublures, "CR-001")
    lu = valider_sortie(items["CR-001"], json.dumps(verdict), schema)
    assert lu.schema_version == 1
    assert Verdict.model_validate_json(lu.model_dump_json()) == lu
    assert isinstance(lu.criteres["presence_elements"], list)


# --- Prompt -----------------------------------------------------------------------------------


def test_prompt_rendu(items: dict[str, Any], grille: Grille, doublures: SimpleNamespace) -> None:
    item = items["Q-001"]
    prompt = construire_prompt(item, doublures.sortie_factice("Texte final."), grille)
    assert not any(p in prompt.texte for p in PLACEHOLDERS)
    assert "sur la Tâche Question." in prompt.texte
    assert grille.section("Q").texte in prompt.texte
    assert item.entree in prompt.texte
    assert item.reponse_reference in prompt.texte
    assert "Texte final.\n\nSources citées :\n- Titre de source factice — https://" in prompt.texte
    for sentinelle in doublures.SENTINELLES:
        assert sentinelle not in prompt.texte
    assert "appels_outils" not in prompt.texte and "extrait" not in prompt.texte
    assert prompt.schema == schema_sortie(item)
    assert prompt.sha_section == grille.section("Q").sha256
    assert prompt.sha_gabarit == grille.sha_gabarit
    assert len(prompt.sha_schema) == 64


def test_substitution_en_une_passe(
    items: dict[str, Any], grille: Grille, doublures: SimpleNamespace
) -> None:
    texte = "Je cite {entree} et {tache} tels quels."
    prompt = construire_prompt(items["NR-001"], doublures.sortie_factice(texte), grille)
    assert texte in prompt.texte


def test_rendre_sortie() -> None:
    assert rendre_sortie({"texte": "T", "sources": []}) == "T\n\nSources citées :\naucune"
    sortie = {
        "texte": "T",
        "appels_outils": [{"nom": "x"}],
        "sources": [
            {"titre": "A", "url": "https://a.fr", "date": "2026-01-01"},
            {"titre": "B", "url": "https://b.fr"},
        ],
    }
    assert rendre_sortie(sortie) == "T\n\nSources citées :\n- A — https://a.fr\n- B — https://b.fr"
    with pytest.raises(TypeError):
        rendre_sortie({"texte": "T", "sources": [SimpleNamespace(titre="A", url="https://a.fr")]})


def test_rendre_entree(items: dict[str, Any]) -> None:
    assert rendre_entree(items["Q-001"]) == items["Q-001"].entree
    texte = rendre_entree(items["RE-001"])
    objet, options = texte.split("\n\nOptions de la demande :\n")
    assert json.loads(objet) == items["RE-001"].entree
    assert json.loads(options) == {
        "longueur_demandee": items["RE-001"].longueur_demandee,
        "parametres": {},
    }
    assert "Options de la demande" in rendre_entree(items["RD-001"])  # mode RD
    assert "Options de la demande" not in rendre_entree(items["CR-001"])


def test_references(items: dict[str, Any]) -> None:
    q = references(items["Q-002"])
    assert list(q) == [
        "reponse_reference",
        "elements_cles",
        "sources_attendues",
        "sans_reponse",
        "mention_obligatoire",
    ]  # orientation_attendue à None : omise
    assert q["sans_reponse"] is True
    cr = references(items["CR-001"])
    assert list(cr) == [
        "participants_reference",
        "decisions_reference",
        "actions_reference",
        "pieges",
    ]
    assert cr["decisions_reference"][0] == {
        "ref": "D1",
        "texte": items["CR-001"].decisions_reference[0],
    }
    assert set(cr["actions_reference"][0]) == {"ref", "action", "responsable", "echeance"}
    assert cr["actions_reference"][0]["ref"] == "A1"
    re_ = references(items["RE-001"])
    assert [p["ref"] for p in re_["points_cles_reference"]] == ["P1", "P2", "P3", "P4"]
    assert list(references(items["CT-001"])) == [
        "type_courrier",
        "elements_obligatoires",
        "champs_a_laisser_en_emplacement",
        "valeurs_interdites",
    ]
    assert list(references(items["NR-001"])) == ["reponse_reference", "criteres"]
    assert list(references(items["LC-001"])) == [
        "informations_a_conserver",
        "termes_juridiques_a_conserver",
    ]
    assert list(references(items["RD-002"])) == ["reponse_reference", "criteres"]


def test_libelle_de_chaque_tache(
    items: dict[str, Any], grille: Grille, doublures: SimpleNamespace
) -> None:
    for item_id in CRITERES:
        item = items[item_id]
        prompt = construire_prompt(item, doublures.sortie_factice(), grille)
        assert f"sur la Tâche {LIBELLES[item.code]}." in prompt.texte


def test_estimation_des_tokens(
    items: dict[str, Any], grille: Grille, doublures: SimpleNamespace
) -> None:
    prompt = construire_prompt(items["Q-001"], doublures.sortie_factice(), grille)
    caracteres = len(prompt.texte) + len(json.dumps(prompt.schema, separators=(",", ":")))
    assert estimer_tokens_entree(prompt) == -(-caracteres // 3) + 300
