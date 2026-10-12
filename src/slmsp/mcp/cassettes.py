"""Lecture et écriture des cassettes MCP au format du calibrage (AD-10).

Une cassette sans `schema_version` est une cassette héritée du calibrage : elle est
acceptée à la lecture, son empreinte `tools_list_sha256` étant calculée depuis le
`tools-list.json` du même dossier. La lecture n'écrit jamais rien ; l'écriture refuse
d'écraser un fichier existant.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.schemas.cassette import Cassette
from slmsp.mcp.erreurs import CassetteInvalide

NOM_TOOLS_LIST: Final = "tools-list.json"
"""Cassette voisine dont l'interaction `tools/list` donne l'empreinte des cassettes héritées."""


def empreinte_tools_list(tools: Sequence[Any]) -> str:
    """SHA-256 (hex minuscule) du JSON canonique de la liste `result.tools` de `tools/list`."""
    return sha256_hex(json_canonique(list(tools)))


def extraire_tools_list(donnees: Mapping[str, Any] | Cassette) -> list[Any]:
    """Liste `result.tools` de l'interaction `tools/list` d'une cassette.

    Lève `CassetteInvalide` si aucune interaction `tools/list` ne porte de liste d'outils.
    """
    if isinstance(donnees, Cassette):
        donnees = donnees.model_dump(mode="json")
    interactions = donnees.get("interactions") if isinstance(donnees, Mapping) else None
    for interaction in interactions if isinstance(interactions, list) else ():
        if not isinstance(interaction, Mapping):
            continue
        requete = interaction.get("request")
        if not isinstance(requete, Mapping) or requete.get("method") != "tools/list":
            continue
        reponse = interaction.get("response")
        resultat = reponse.get("result") if isinstance(reponse, Mapping) else None
        tools = resultat.get("tools") if isinstance(resultat, Mapping) else None
        if isinstance(tools, list):
            return tools
    raise CassetteInvalide("aucune interaction `tools/list` avec une liste `result.tools`")


def _lire_json(chemin: Path) -> Any:
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as exc:
        raise CassetteInvalide(f"{chemin} : cassette illisible ({type(exc).__name__})") from None
    except UnicodeDecodeError:
        raise CassetteInvalide(f"{chemin} : cassette illisible : fichier non UTF-8") from None
    try:
        return json.loads(texte)
    except json.JSONDecodeError as exc:
        raise CassetteInvalide(
            f"{chemin} : JSON invalide (ligne {exc.lineno}, colonne {exc.colno})"
        ) from None


def _empreinte_voisine(chemin: Path) -> str:
    voisin = chemin.parent / NOM_TOOLS_LIST
    if not voisin.is_file():
        raise CassetteInvalide(
            f"{chemin} : cassette héritée (sans `schema_version`) sans `{NOM_TOOLS_LIST}` "
            "dans le même dossier"
        )
    donnees = _lire_json(voisin)
    try:
        tools = extraire_tools_list(donnees)
    except CassetteInvalide as exc:
        raise CassetteInvalide(f"{voisin} : {exc}") from None
    return empreinte_tools_list(tools)


def lire_cassette(chemin: str | Path) -> Cassette:
    """Lit et valide la cassette `chemin` (cassettes héritées du calibrage comprises).

    Lève `CassetteInvalide` si le fichier est illisible, n'est pas un objet JSON, ou n'est
    pas conforme à `Cassette`. Le message cite le fichier et les clés, jamais les valeurs.
    """
    chemin = Path(chemin)
    donnees = _lire_json(chemin)
    if not isinstance(donnees, dict):
        raise CassetteInvalide(f"{chemin} : une cassette est un objet JSON")
    if "schema_version" not in donnees:
        if "tools_list_sha256" in donnees:
            raise CassetteInvalide(
                f"{chemin} : `tools_list_sha256` sans `schema_version` : ni cassette héritée, "
                "ni cassette versionnée"
            )
        donnees = {
            "schema_version": 1,
            **donnees,
            "tools_list_sha256": _empreinte_voisine(chemin),
        }
    try:
        return Cassette.model_validate(donnees)
    except ValidationError as exc:
        lignes = []
        for erreur in exc.errors(include_url=False, include_input=False, include_context=False):
            cle = ".".join(str(partie) for partie in erreur["loc"]) or "(racine)"
            lignes.append(f"{chemin} : clé « {cle} » : {erreur['msg']}")
        raise CassetteInvalide("\n".join(lignes)) from None


def _en_json(cassette: Cassette) -> dict[str, Any]:
    donnees = cassette.model_dump(mode="json")
    for interaction in donnees["interactions"]:
        simulation = interaction.get("simulation")
        if simulation is None:
            interaction.pop("simulation", None)
        elif simulation.get("statut") is None:
            simulation.pop("statut", None)
    return donnees


def ecrire_cassette(cassette: Cassette, chemin: str | Path) -> Path:
    """Écrit `cassette` dans `chemin` (JSON UTF-8, indentation 1, LF) et renvoie le chemin.

    Les dossiers parents sont créés. Lève `ArtefactExistant` si `chemin` existe déjà : une
    cassette n'est jamais réécrite.
    """
    if not isinstance(cassette, Cassette):
        raise TypeError(f"Cassette attendue (reçu {type(cassette).__name__})")
    chemin = Path(chemin)
    # Revalidation : un modèle muté après construction ou issu de `model_construct` n'est
    # jamais écrit (ValidationError, aucun fichier créé).
    cassette = Cassette.model_validate(cassette.model_dump())
    texte = json.dumps(_en_json(cassette), indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    try:
        with chemin.open("xb") as flux:
            flux.write(texte.encode("utf-8"))
    except FileExistsError:
        raise ArtefactExistant(
            f"{chemin} existe déjà : une cassette n'est jamais réécrite"
        ) from None
    return chemin
