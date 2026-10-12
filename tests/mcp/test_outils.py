"""Outils exposés figés, validation des appels et comparaison au serveur (story 3.1, AD-8)."""

from __future__ import annotations

import copy
import json
import tomllib
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import AppelNonConforme, ConfigurationInvalide, SchemaOutilModifie
from slmsp.mcp.outils import (
    OUTILS_AUTORISES,
    charger_config,
    charger_outils,
    comparer_schema_serveur,
    valider_appel,
)

RACINE = Path(__file__).resolve().parents[2]
CONFIG = RACINE / "config" / "outils-mcp.toml"
CASSETTES = RACINE / "eval" / "calibrage" / "cassettes"


def _tools_serveur() -> list[dict[str, Any]]:
    donnees = json.loads((CASSETTES / "tools-list.json").read_text(encoding="utf-8"))
    (interaction,) = donnees["interactions"]
    assert interaction["request"]["method"] == "tools/list"
    return interaction["response"]["result"]["tools"]


def _simplifier(schema: Any) -> Any:
    """Simplification attendue : sans `title`, sans `default` nul (récursif)."""
    if isinstance(schema, list):
        return [_simplifier(x) for x in schema]
    if not isinstance(schema, dict):
        return schema
    sortie = {}
    for cle, valeur in schema.items():
        if cle == "title" or (cle == "default" and valeur is None):
            continue
        if cle == "properties":
            sortie[cle] = {nom: _simplifier(sous) for nom, sous in valeur.items()}
        else:
            sortie[cle] = _simplifier(valeur)
    return sortie


# --- Outils chargés --------------------------------------------------------------------------


def test_charger_outils_format_openai() -> None:
    outils = charger_outils()
    assert [o["function"]["name"] for o in outils] == list(OUTILS_AUTORISES)
    for outil in outils:
        assert set(outil) == {"type", "function"}
        assert outil["type"] == "function"
        assert set(outil["function"]) == {"name", "description", "parameters"}
        Draft202012Validator.check_schema(outil["function"]["parameters"])
        assert outil["function"]["parameters"]["additionalProperties"] is False


def test_charger_outils_renvoie_des_copies() -> None:
    premiers = charger_outils()
    premiers[0]["function"]["parameters"]["properties"].clear()
    premiers[0]["function"]["name"] = "modifie"
    assert charger_outils()[0]["function"]["name"] == "search_datasets"
    assert charger_outils()[0]["function"]["parameters"]["properties"]


def test_tools_list_sha256_egal_empreinte_calibrage() -> None:
    config = charger_config()
    assert config.tools_list_sha256 == sha256_hex(json_canonique(_tools_serveur()))
    assert (RACINE / config.source).resolve() == (CASSETTES / "tools-list.json").resolve()


def test_parametres_et_descriptions_tires_du_serveur() -> None:
    serveur = {t["name"]: t for t in _tools_serveur()}
    for outil in charger_config().outils:
        origine = serveur[outil.nom]
        attendu = _simplifier(origine["inputSchema"])
        attendu["additionalProperties"] = False
        assert outil.parametres == attendu, outil.nom
        assert outil.description == origine["description"].strip(), outil.nom
        assert outil.sha256_schema_serveur == sha256_hex(json_canonique(origine["inputSchema"]))


def test_config_reelle_utf8() -> None:
    CONFIG.read_bytes().decode("utf-8")


# --- Config fautive --------------------------------------------------------------------------


def _toml(valeur: Any) -> str:
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if isinstance(valeur, (int, str)):
        return json.dumps(valeur, ensure_ascii=False)
    if isinstance(valeur, list):
        return "[" + ", ".join(_toml(x) for x in valeur) + "]"
    if isinstance(valeur, dict):
        return "{ " + ", ".join(f'"{k}" = {_toml(v)}' for k, v in valeur.items()) + " }"
    raise TypeError(type(valeur))


def _ecrire_config(chemin: Path, donnees: dict[str, Any]) -> Path:
    lignes = [f"{cle} = {_toml(v)}" for cle, v in donnees.items() if cle != "outils"]
    for outil in donnees.get("outils", []):
        lignes.append("[[outils]]")
        lignes.extend(f"{cle} = {_toml(v)}" for cle, v in outil.items())
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return chemin


def _config_reelle() -> dict[str, Any]:
    with CONFIG.open("rb") as flux:
        return tomllib.load(flux)


def test_ecriture_config_de_test_fidele(tmp_path: Path) -> None:
    chemin = _ecrire_config(tmp_path / "ok.toml", _config_reelle())
    assert charger_outils(chemin) == charger_outils()


@pytest.mark.parametrize(
    "cas",
    ["hors_liste", "doublon", "trop", "schema_invalide", "cle_inconnue", "cle_outil_inconnue"],
)
def test_config_fautive_refusee(tmp_path: Path, cas: str) -> None:
    donnees = _config_reelle()
    outils = donnees["outils"]
    if cas == "hors_liste":
        outils[0]["nom"] = "get_metrics"
    elif cas == "doublon":
        outils[1] = copy.deepcopy(outils[0])
    elif cas == "trop":
        outils.append(copy.deepcopy(outils[0]))
    elif cas == "schema_invalide":
        outils[0]["parametres"]["type"] = "objet"
    elif cas == "cle_inconnue":
        donnees["inconnue"] = 1
    elif cas == "cle_outil_inconnue":
        outils[0]["exemple"] = "x"
    chemin = _ecrire_config(tmp_path / f"{cas}.toml", donnees)
    with pytest.raises(ConfigurationInvalide):
        charger_outils(chemin)
    with pytest.raises(ConfigurationInvalide):
        valider_appel("search_datasets", {"query": "x"}, chemin=chemin)


def test_config_absente(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_config(tmp_path / "absente.toml")


# --- Validation des appels -------------------------------------------------------------------


def test_appel_conforme() -> None:
    assert valider_appel("search_datasets", {"query": "x", "page_size": 5}) is None
    assert valider_appel("query_resource_data", {"resource_id": "r", "sort_column": None}) is None


def test_type_faux() -> None:
    with pytest.raises(AppelNonConforme) as info:
        valider_appel("search_datasets", {"query": 3})
    erreur = info.value
    assert erreur.nom == "search_datasets"
    assert isinstance(erreur.details, list) and erreur.details
    assert all(isinstance(d, str) for d in erreur.details)
    assert "query" in str(erreur)
    assert "is not of type 'string'" in str(erreur)


@pytest.mark.parametrize("arguments", [{}, {"query": "x", "inexistant": 1}])
def test_requis_absent_ou_argument_inconnu(arguments: dict[str, Any]) -> None:
    with pytest.raises(AppelNonConforme) as info:
        valider_appel("search_datasets", arguments)
    assert info.value.details


def test_tous_les_ecarts_listes() -> None:
    with pytest.raises(AppelNonConforme) as info:
        valider_appel("search_datasets", {"query": 3, "page": "un", "autre": 1})
    assert len(info.value.details) == 3


@pytest.mark.parametrize(
    ("nom", "arguments"),
    [("get_metrics", {}), ("search_datasets", ["x"]), ("search_datasets", None)],
)
def test_outil_inconnu_ou_arguments_non_objet(nom: str, arguments: Any) -> None:
    with pytest.raises(AppelNonConforme) as info:
        valider_appel(nom, arguments)
    assert info.value.nom == nom


def test_nom_non_chaine() -> None:
    with pytest.raises(AppelNonConforme) as info:
        valider_appel(None, {})  # type: ignore[arg-type]
    assert info.value.nom is None


@pytest.mark.parametrize("session", ["R-001.json", "R-002.json"])
def test_appels_du_calibrage_conformes(session: str) -> None:
    donnees = json.loads((CASSETTES / session).read_text(encoding="utf-8"))
    appels = [
        i["request"]["params"]
        for i in donnees["interactions"]
        if i["request"].get("method") == "tools/call"
    ]
    assert appels
    for appel in appels:
        assert valider_appel(appel["name"], appel["arguments"]) is None


# --- Comparaison au serveur ------------------------------------------------------------------


def test_serveur_identique() -> None:
    assert comparer_schema_serveur(_tools_serveur()) is None


def test_outil_inconnu_ajoute_ignore() -> None:
    tools = _tools_serveur() + [{"name": "nouveau", "inputSchema": {"type": "object"}}]
    assert comparer_schema_serveur(tools) is None


def test_outil_absent_ou_schema_modifie() -> None:
    tools = [t for t in _tools_serveur() if t["name"] != "get_dataset_info"]
    for outil in tools:
        if outil["name"] == "search_datasets":
            outil["inputSchema"]["properties"]["query"]["type"] = "integer"
    with pytest.raises(SchemaOutilModifie) as info:
        comparer_schema_serveur(tools)
    assert info.value.ecarts == (
        "search_datasets : schéma modifié",
        "get_dataset_info : absent du serveur",
    )


def test_schema_retire() -> None:
    tools = _tools_serveur()
    for outil in tools:
        if outil["name"] == "get_resource_info":
            del outil["inputSchema"]
    with pytest.raises(SchemaOutilModifie) as info:
        comparer_schema_serveur(tools)
    assert info.value.ecarts == ("get_resource_info : schéma modifié",)
