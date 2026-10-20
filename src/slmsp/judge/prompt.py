"""Prompt du Juge, schéma de sortie fermé par Tâche et validation d'un verdict (AD-12).

Cécité du Juge : le prompt ne porte que l'entrée rendue de l'item, le texte final de la
sortie, les sources citées (titre et URL seulement), les références de l'item et la section
de grille de la Tâche. Ni `appels_outils`, ni aucune autre clé de la sortie ou des sources,
ni le modèle évalué, ni la méthode ne sont transmis.

Le schéma de sortie est fermé (`additionalProperties: false` partout, `required` complet,
`id` en `const`, notes en `enum` typé). Il n'emploie ni `minimum`, ni `maximum`, ni
`minLength`, ni `minItems`, que la sortie structurée ne prend pas en charge : la couverture
exacte des références d'éléments (CR, RE) est vérifiée par `valider_sortie`.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

import jsonschema
from pydantic import ValidationError

from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import SlmspError
from slmsp.core.items import (
    LIBELLES,
    ItemBase,
    ItemCO,
    ItemCR,
    ItemCT,
    ItemLC,
    ItemNR,
    ItemQ,
    ItemRD,
    ItemRE,
    vers_requete,
)
from slmsp.core.schemas.verdict import Verdict
from slmsp.judge.grille import PLACEHOLDERS, Grille

CONFIANCES: Final = ("haute", "moyenne", "basse")
CRITERE_ELEMENTS: Final = "presence_elements"

MARGE_TOKENS: Final = 300
"""Tokens ajoutés à l'estimation de l'entrée (enveloppe du message, schéma compilé)."""


class ItemNonJugeable(SlmspError):
    """L'item ne peut pas être soumis au Juge (CO, ou CR/RE sans référence d'éléments)."""


class SortieNonConforme(SlmspError):
    """La sortie du Juge n'est pas un JSON conforme au schéma de l'item."""


@dataclass(frozen=True)
class PromptJuge:
    """Prompt rendu d'un item, son schéma de sortie et les empreintes de la clé de cache."""

    texte: str
    schema: dict[str, Any]
    sha_section: str
    sha_gabarit: str
    sha_schema: str


# --- Schéma de sortie ------------------------------------------------------------------------


def _objet(proprietes: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(proprietes),
        "properties": proprietes,
    }


def _note(valeurs: list[int]) -> dict[str, Any]:
    return _objet(
        {
            "note": {"type": "integer", "enum": valeurs},
            "justification": {"type": "string"},
        }
    )


def _elements(refs: list[str], present: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "array",
        "items": _objet(
            {
                "ref": {"type": "string", "enum": refs},
                "present": present,
                "justification": {"type": "string"},
            }
        ),
    }


def refs_elements(item: ItemBase) -> list[str]:
    """Références d'éléments de l'item : CR `D1…Dn` puis `A1…An`, RE `P1…Pn`, sinon vide."""
    if isinstance(item, ItemCR):
        decisions = item.decisions_reference or []
        actions = item.actions_reference or []
        return [f"D{i}" for i in range(1, len(decisions) + 1)] + [
            f"A{i}" for i in range(1, len(actions) + 1)
        ]
    if isinstance(item, ItemRE):
        return [f"P{i}" for i in range(1, len(item.points_cles_reference or []) + 1)]
    return []


def _verifier_jugeable(item: ItemBase) -> None:
    if isinstance(item, ItemCO):
        raise ItemNonJugeable(f"{item.id} : la Tâche CO est notée automatiquement, jamais jugée")
    if isinstance(item, (ItemCR, ItemRE)) and not refs_elements(item):
        raise ItemNonJugeable(f"{item.id} : aucune référence d'éléments à juger")
    if item.code not in LIBELLES:
        raise ItemNonJugeable(f"{item.id} : Tâche inconnue du Juge ({item.code})")


def _criteres(item: ItemBase) -> dict[str, Any]:
    if isinstance(item, ItemQ):
        criteres = {"exactitude": _note([0, 1, 2]), "pertinence_source": _note([0, 1])}
        if item.sans_reponse:
            criteres["cas_sans_reponse"] = _note([0, 1])
        return criteres
    if isinstance(item, ItemRD):
        return {"libelle_correct": _note([0, 1])}
    if isinstance(item, ItemCR):
        return {
            CRITERE_ELEMENTS: _elements(
                refs_elements(item), {"type": "number", "enum": [0, 0.5, 1]}
            ),
            "absence_invention": _note([0, 1]),
            "structure": _note([0, 1]),
        }
    if isinstance(item, ItemLC):
        return {
            "fidelite": _note([0, 1, 2]),
            "termes_juridiques": _note([0, 1]),
            "clarte_percue": _note([1, 2, 3, 4, 5]),
        }
    if isinstance(item, ItemRE):
        return {
            "fidelite": _note([0, 1]),
            CRITERE_ELEMENTS: _elements(refs_elements(item), {"type": "integer", "enum": [0, 1]}),
        }
    if isinstance(item, ItemCT):
        return {"conformite": _note([0, 1, 2])}
    if isinstance(item, ItemNR):
        return {"exactitude": _note([0, 1])}
    raise ItemNonJugeable(f"{item.id} : Tâche sans critère de Juge ({item.code})")


def schema_sortie(item: ItemBase) -> dict[str, Any]:
    """Schéma JSON fermé du verdict attendu pour `item` ; `ItemNonJugeable` pour CO."""
    _verifier_jugeable(item)
    return _objet(
        {
            "id": {"type": "string", "const": item.id},
            "criteres": _objet(_criteres(item)),
            "inventions": {"type": "array", "items": {"type": "string"}},
            "confiance": {"type": "string", "enum": list(CONFIANCES)},
        }
    )


# --- Rendus ----------------------------------------------------------------------------------


def _json(valeur: Any, *, trie: bool = False) -> str:
    return json.dumps(valeur, ensure_ascii=False, indent=2, sort_keys=trie)


def references(item: ItemBase) -> dict[str, Any]:
    """Champs de référence de l'item envoyés au Juge (ordre fixe, clés à `None` omises)."""
    champs: list[tuple[str, Any]]
    if isinstance(item, ItemQ):
        champs = [
            ("reponse_reference", item.reponse_reference),
            ("elements_cles", item.elements_cles),
            ("sources_attendues", item.sources_attendues),
            ("sans_reponse", item.sans_reponse),
            ("orientation_attendue", item.orientation_attendue),
            ("mention_obligatoire", item.mention_obligatoire),
        ]
    elif isinstance(item, ItemRD):
        champs = [
            ("reponse_reference", item.reponse_reference),
            ("valeurs_attendues", item.valeurs_attendues),
            ("criteres", item.criteres),
        ]
    elif isinstance(item, ItemCR):
        decisions = item.decisions_reference
        actions = item.actions_reference
        champs = [
            ("participants_reference", item.participants_reference),
            (
                "decisions_reference",
                None
                if decisions is None
                else [{"ref": f"D{i}", "texte": d} for i, d in enumerate(decisions, start=1)],
            ),
            (
                "actions_reference",
                None
                if actions is None
                else [
                    {
                        "ref": f"A{i}",
                        "action": a.action,
                        "responsable": a.responsable,
                        "echeance": a.echeance,
                    }
                    for i, a in enumerate(actions, start=1)
                ],
            ),
            ("pieges", item.pieges),
        ]
    elif isinstance(item, ItemLC):
        champs = [
            ("informations_a_conserver", item.informations_a_conserver),
            ("termes_juridiques_a_conserver", item.termes_juridiques_a_conserver),
        ]
    elif isinstance(item, ItemRE):
        points = item.points_cles_reference
        champs = [
            (
                "points_cles_reference",
                None
                if points is None
                else [{"ref": f"P{i}", "texte": p} for i, p in enumerate(points, start=1)],
            ),
            ("longueur_demandee", item.longueur_demandee),
        ]
    elif isinstance(item, ItemCT):
        champs = [
            ("type_courrier", item.type_courrier),
            ("elements_obligatoires", item.elements_obligatoires),
            ("champs_a_laisser_en_emplacement", item.champs_a_laisser_en_emplacement),
            ("valeurs_interdites", item.valeurs_interdites),
        ]
    elif isinstance(item, ItemNR):
        champs = [
            ("sous_type", item.sous_type),
            ("reponse_reference", item.reponse_reference),
            ("criteres", item.criteres),
        ]
    else:
        raise ItemNonJugeable(f"{item.id} : Tâche sans référence pour le Juge ({item.code})")
    return {cle: valeur for cle, valeur in champs if valeur is not None}


def rendre_entree(item: ItemBase) -> str:
    """Entrée de l'item telle que l'Assistant l'a reçue (`vers_requete`)."""
    requete = vers_requete(item)
    texte = requete.entree if isinstance(requete.entree, str) else _json(requete.entree, trie=True)
    if requete.options != {"parametres": {}}:
        texte += "\n\nOptions de la demande :\n" + _json(requete.options, trie=True)
    return texte


def rendre_sortie(sortie: Mapping[str, Any]) -> str:
    """Texte final de la sortie, puis ses sources citées (titre et URL seulement)."""
    texte = sortie.get("texte")
    texte = texte if isinstance(texte, str) else ""
    lignes = []
    for source in sortie.get("sources") or []:
        if not isinstance(source, Mapping):
            raise TypeError("source citée : objet JSON (mapping) attendu")
        titre, url = source.get("titre"), source.get("url")
        lignes.append(f"- {titre or ''} — {url or ''}")
    citees = "\n".join(lignes) if lignes else "aucune"
    return f"{texte}\n\nSources citées :\n{citees}"


_MOTIF_PLACEHOLDER = re.compile("|".join(re.escape(p) for p in PLACEHOLDERS))


def construire_prompt(item: ItemBase, sortie: Mapping[str, Any], grille: Grille) -> PromptJuge:
    """Prompt du Juge pour `item` et `sortie`, par substitution en une passe du gabarit.

    Lève `ItemNonJugeable` (CO, CR ou RE sans référence d'éléments) avant tout rendu.
    """
    schema = schema_sortie(item)
    section = grille.section(item.code)
    valeurs = {
        "{tache}": LIBELLES[item.code],
        "{section de la Tâche}": section.texte,
        "{entree}": rendre_entree(item),
        "{champs de référence}": _json(references(item)),
        "{sortie}": rendre_sortie(sortie),
    }
    texte = _MOTIF_PLACEHOLDER.sub(lambda m: valeurs[m.group(0)], grille.gabarit)
    return PromptJuge(
        texte=texte,
        schema=schema,
        sha_section=section.sha256,
        sha_gabarit=grille.sha_gabarit,
        sha_schema=sha256_hex(json_canonique(schema)),
    )


def estimer_tokens_entree(prompt: PromptJuge) -> int:
    """Estimation prudente des tokens d'entrée : ⌈caractères / 3⌉ + `MARGE_TOKENS`."""
    caracteres = len(prompt.texte) + len(json_canonique(prompt.schema).decode("utf-8"))
    return math.ceil(caracteres / 3) + MARGE_TOKENS


# --- Validation ------------------------------------------------------------------------------


def refs_du_schema(schema: Mapping[str, Any]) -> list[str] | None:
    try:
        elements = schema["properties"]["criteres"]["properties"][CRITERE_ELEMENTS]
        return list(elements["items"]["properties"]["ref"]["enum"])
    except (KeyError, TypeError):
        return None


def valider_selon_schema(item_id: str, texte_json: str, schema: Mapping[str, Any]) -> Verdict:
    """Valide la sortie brute du Juge contre `schema` ; lève `SortieNonConforme`.

    Contrôles : JSON lisible, conformité au schéma (`jsonschema`), `id` égal à `item_id`,
    chaque référence d'éléments présente une fois et une seule.
    """
    try:
        donnees = json.loads(texte_json)
    except (TypeError, ValueError) as exc:
        raise SortieNonConforme(f"{item_id} : JSON illisible ({exc})") from None
    validateur = jsonschema.Draft202012Validator(schema)
    erreur = jsonschema.exceptions.best_match(validateur.iter_errors(donnees))
    if erreur is not None:
        chemin = "/".join(str(p) for p in erreur.absolute_path) or "(racine)"
        raise SortieNonConforme(f"{item_id} : écart au schéma en {chemin} : {erreur.message}")
    if donnees.get("id") != item_id:
        raise SortieNonConforme(f"{item_id} : `id` différent de l'item")
    refs = refs_du_schema(schema)
    if refs is not None:
        vues = [element["ref"] for element in donnees["criteres"][CRITERE_ELEMENTS]]
        doublons = sorted({r for r in vues if vues.count(r) > 1})
        manquantes = [r for r in refs if r not in vues]
        if doublons or manquantes:
            raise SortieNonConforme(
                f"{item_id} : références d'éléments manquantes {manquantes} ou en double {doublons}"
            )
    try:
        return Verdict(
            id=donnees["id"],
            criteres=donnees["criteres"],
            inventions=donnees["inventions"],
            confiance=donnees["confiance"],
        )
    except ValidationError as exc:
        raise SortieNonConforme(
            f"{item_id} : verdict invalide ({exc.error_count()} erreur(s))"
        ) from None


def valider_sortie(item: ItemBase, texte_json: str, schema: Mapping[str, Any]) -> Verdict:
    """Valide la sortie brute du Juge pour `item` (voir `valider_selon_schema`)."""
    return valider_selon_schema(item.id, texte_json, schema)
