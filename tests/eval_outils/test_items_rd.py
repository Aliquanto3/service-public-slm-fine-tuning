"""Items Recherche de données (RD) des jeux v1.0 et v1.1 et leurs cassettes (story 7.3).

Aucun réseau. Les brouillons `eval/construction/<version>/RD.jsonl`, leurs verdicts et les
cassettes `eval/cassettes/RD-xxx/*.json` sont lus tels quels. `anomalies_rd` est une fonction pure,
réutilisable sur un lot de brouillons avant fusion.

Sémantique des `regles` d'un appel attendu (format de la story 5.1, consignée pour le banc) :
- argument `exact` : égalité JSON ;
- `contient_un_de` : au moins une des chaînes, normalisée par `slmsp.core.texte.normaliser`
  (AD-29 : casse, ponctuation → espace, accents gardés), apparaît **en début de mot** dans la
  valeur normalisée (`(?:^| )` + fragment). Les chaînes sont écrites déjà normalisées (points
  fixes de `normaliser`), avec leurs variantes accentuée et non accentuée ;
- `mot_entier_un_de` (v1.1) : au moins un des mots, normalisé, apparaît en mot entier dans la
  valeur normalisée (`(?:^| )` + mot + `(?: |$)`) ; combiné en « ou » avec `contient_un_de` ;
- `optionnel: true` seul : absent ou quelconque ; combiné : si présent, satisfait la règle ;
- argument non listé : libre (dans le schéma de l'outil) ;
- appel `optionnel` : peut manquer ; `ordre_libre` : position libre, sinon ordre de la liste.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import shutil
import socket
import sys
import tomllib
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

from slmsp.core.items import MODES_RD, ItemInvalide, lire_items, valider_item
from slmsp.core.texte import normaliser
from slmsp.mcp.cassettes import lire_cassette as lire_cassette_production
from slmsp.mcp.outils import charger_outils, valider_appel

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "eval" / "outils" / "construire_jeu.py"
VERSIONS = tuple(v for v in ("v1.0", "v1.1") if (RACINE / "eval" / "construction" / v).is_dir())
FIXTURE_REPLI = Path(__file__).resolve().parent / "fixtures" / "catalogue_repli.json"
SERVEUR = "https://mcp.data.gouv.fr/mcp"
CATALOGUE = "AgentPublic/data-gouv-datasets-catalog"
REVISION_CATALOGUE = "11f3d3c9481ad478dbcff52e85d73b7fd10533ce"

CLES_APPEL = frozenset({"outil", "arguments", "regle", "regles"})
CLES_REGLES = frozenset({"optionnel", "ordre_libre", "arguments"})
CLES_REGLE_ARGUMENT = frozenset({"exact", "contient_un_de", "mot_entier_un_de", "optionnel"})
CLES_VALEURS = frozenset({"ressource_id", "filtre", "total_lignes", "lignes"})
CLES_VALEURS_FACULTATIVES = frozenset({"colonnes"})
CLES_FILTRE = frozenset({"colonne", "operateur", "valeur"})

PROPRIETES_OUTILS = {
    o["function"]["name"]: frozenset(o["function"]["parameters"]["properties"])
    for o in charger_outils()
}
"""Noms d'arguments admis par outil figé (`config/outils-mcp.toml`)."""

ANNONCE_SIMULATION = {"delai_depasse": "délai", "injoignable": "injoignable"}
"""Mot qui annonce chaque panne simulée ; `erreur_http` s'annonce par son statut en chiffres."""

RE_ID_JEU = re.compile(r"\b[0-9a-f]{24}\b")
RE_UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
RE_URL = re.compile(r"https?://[^\s«»\"<>]+")
RE_NOMBRE = re.compile(r"-?[0-9]+(?:[.,][0-9]+)?")


def _charger(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


cj = _charger("construire_jeu_items_rd", OUTIL)


def tools_list_sha256_config(racine: Path = RACINE) -> str:
    with (racine / "config" / "outils-mcp.toml").open("rb") as f:
        return tomllib.load(f)["tools_list_sha256"]


# ---------------------------------------------------------------------------
# Règles d'appel
# ---------------------------------------------------------------------------
def fragment_en_debut_de_mot(fragment: str, valeur: str) -> bool:
    """`fragment` normalisé apparaît en début de mot dans `valeur` normalisée (AD-29)."""
    motif = r"(?:^| )" + re.escape(normaliser(fragment))
    return re.search(motif, normaliser(valeur)) is not None


def mot_entier(mot: str, valeur: str) -> bool:
    """`mot` normalisé apparaît en mot entier dans `valeur` normalisée (v1.1)."""
    forme = normaliser(mot)
    motif = r"(?:^| )" + re.escape(forme) + r"(?: |$)"
    return bool(forme) and re.search(motif, normaliser(valeur)) is not None


def regle_argument_satisfaite(regle: dict, present: bool, valeur: Any) -> bool:
    if not present:
        return regle.get("optionnel") is True
    if "exact" in regle:
        return valeur == regle["exact"] and type(valeur) is type(regle["exact"])
    if "contient_un_de" in regle or "mot_entier_un_de" in regle:
        return isinstance(valeur, str) and (
            any(fragment_en_debut_de_mot(c, valeur) for c in regle.get("contient_un_de", []))
            or any(mot_entier(m, valeur) for m in regle.get("mot_entier_un_de", []))
        )
    return regle.get("optionnel") is True


def requete_satisfait(regles: dict, arguments: dict) -> bool:
    """La requête (arguments d'un `tools/call`) satisfait-elle les règles d'arguments ?"""
    return all(
        regle_argument_satisfaite(regle, nom in arguments, arguments.get(nom))
        for nom, regle in regles.get("arguments", {}).items()
    )


def _anomalies_regles(regles: Any, lieu: str, outil: str | None = None) -> list[str]:
    if not isinstance(regles, dict):
        return [f"{lieu} : `regles` objet attendu"]
    a = []
    if set(regles) - CLES_REGLES:
        a.append(f"{lieu} : clés de `regles` inconnues {sorted(set(regles) - CLES_REGLES)}")
    for cle in ("optionnel", "ordre_libre"):
        if not isinstance(regles.get(cle), bool):
            a.append(f"{lieu} : `regles.{cle}` booléen attendu")
    if not isinstance(regles.get("arguments"), dict):
        return a + [f"{lieu} : `regles.arguments` objet attendu"]
    for nom, regle in regles["arguments"].items():
        ici = f"{lieu} : argument {nom!r}"
        if outil in PROPRIETES_OUTILS and nom not in PROPRIETES_OUTILS[outil]:
            a.append(f"{ici} : absent du schéma de l'outil {outil}")
        if not isinstance(regle, dict) or not regle or set(regle) - CLES_REGLE_ARGUMENT:
            a.append(f"{ici} : règle mal formée {regle!r}")
            continue
        if "exact" in regle and ("contient_un_de" in regle or "mot_entier_un_de" in regle):
            a.append(f"{ici} : `exact` exclut `contient_un_de` et `mot_entier_un_de`")
        mots = regle.get("mot_entier_un_de")
        if "mot_entier_un_de" in regle and not (
            isinstance(mots, list)
            and mots
            and all(isinstance(m, str) and normaliser(m) for m in mots)
        ):
            a.append(f"{ici} : `mot_entier_un_de` liste de mots non vide attendue")
        if "optionnel" in regle and regle["optionnel"] is not True:
            a.append(f"{ici} : `optionnel` vaut `true` ou est absent")
        liste = regle.get("contient_un_de")
        if "contient_un_de" in regle:
            if not (isinstance(liste, list) and liste and all(isinstance(c, str) for c in liste)):
                a.append(f"{ici} : `contient_un_de` liste de textes non vide attendue")
            elif any(not c or c != normaliser(c) for c in liste):
                a.append(f"{ici} : `contient_un_de` hors des points fixes de normaliser : {liste}")
    return a


# ---------------------------------------------------------------------------
# Cassettes
# ---------------------------------------------------------------------------
def chemin_cassette(relatif: str, racine: Path = RACINE) -> Path:
    return (racine / "eval" / "jeu" / "v1.0" / PurePosixPath(relatif)).resolve()


def lire_cassette(chemin: Path) -> dict:
    return json.loads(chemin.read_text(encoding="utf-8"))


def textes_reponse(interaction: dict) -> list[str]:
    reponse = interaction.get("response") or {}
    contenu = (reponse.get("result") or {}).get("content") or []
    return [c.get("text", "") for c in contenu if isinstance(c, dict)]


def blocs_jeux(interactions: list[dict]) -> list[str]:
    """Blocs où un jeu est décrit d'un seul tenant : chaque résultat numéroté de
    `search_datasets`, ou le texte entier d'une réponse d'un autre outil."""
    blocs = []
    for interaction in interactions:
        nom = interaction["request"]["params"]["name"]
        for texte in textes_reponse(interaction):
            if nom == "search_datasets":
                blocs += re.split(r"\n\n(?=[0-9]+\. )", texte)[1:]
            else:
                blocs.append(texte)
    return blocs


def _url_presente(url: str, texte: str) -> bool:
    """URL présente dans `texte`, à la barre finale près."""
    return url in texte or url.rstrip("/") in texte or (url + "/") in texte


def _jeu_dans_un_bloc(jeu: dict, blocs: list[str]) -> bool:
    for bloc in blocs:
        if all(
            _url_presente(v, bloc) if k == "url" else v in bloc
            for k, v in jeu.items()
            if k in ("id", "titre", "producteur", "url")
        ):
            return True
    return False


def _blocs_lignes(texte: str) -> list[str]:
    """Blocs `Row n:` du texte d'une réponse `query_resource_data`."""
    return re.split(r"\n  Row [0-9]+:\n", texte)[1:]


def _anomalies_valeurs(it: dict, appels_cassette: list[dict]) -> list[str]:
    va = it["valeurs_attendues"]
    if (
        not isinstance(va, dict)
        or not CLES_VALEURS <= set(va)
        or set(va) - CLES_VALEURS - CLES_VALEURS_FACULTATIVES
    ):
        return [
            f"`valeurs_attendues` : clés {sorted(CLES_VALEURS)} attendues "
            f"(et {sorted(CLES_VALEURS_FACULTATIVES)} facultatives)"
        ]
    a = []
    if "colonnes" in va:
        colonnes = va["colonnes"]
        connues = [set(ligne) for ligne in va["lignes"] if isinstance(ligne, dict)]
        if not (
            isinstance(colonnes, list)
            and colonnes
            and all(isinstance(c, str) for c in colonnes)
            and connues
            and all(set(colonnes) <= cles for cles in connues)
        ):
            a.append(f"`valeurs_attendues.colonnes` absentes des lignes : {colonnes!r}")
    filtre = va["filtre"]
    if filtre is not None and (not isinstance(filtre, dict) or set(filtre) != CLES_FILTRE):
        a.append(f"`valeurs_attendues.filtre` : null ou clés {sorted(CLES_FILTRE)}")
        filtre = None
    lignes = va["lignes"] if isinstance(va["lignes"], list) else []
    if not lignes:
        a.append("`valeurs_attendues.lignes` : liste non vide attendue")
    # Les valeurs numériques visées doivent figurer dans la réponse de référence.
    texte_ref = (it.get("reponse_reference") or {}).get("texte", "")
    for ligne in lignes:
        for k, v in ligne.items() if isinstance(ligne, dict) else []:
            if isinstance(v, str) and RE_NOMBRE.fullmatch(v) and v not in texte_ref:
                a.append(f"valeur {k} = {v!r} absente de `reponse_reference.texte`")
    candidates = [
        i
        for i in appels_cassette
        if i["request"]["params"]["name"] == "query_resource_data"
        and i["request"]["params"]["arguments"].get("resource_id") == va["ressource_id"]
    ]
    if not candidates:
        return a + [f"aucun `query_resource_data` sur {va['ressource_id']!r} dans la cassette"]
    manques: list[str] = ["réponse sans texte"]
    for interaction in candidates:
        for texte in textes_reponse(interaction):
            manques = []
            if f"Total rows (Tabular API): {va['total_lignes']}\n" not in texte:
                manques.append(f"total_lignes {va['total_lignes']!r}")
            if filtre is not None:
                attendu = f"Filter: {filtre['colonne']} {filtre['operateur']} {filtre['valeur']}\n"
                if attendu not in texte:
                    manques.append(f"filtre {attendu.strip()!r}")
            blocs = _blocs_lignes(texte)
            for ligne in lignes:
                if not isinstance(ligne, dict) or not ligne:
                    manques.append(f"ligne mal formée {ligne!r}")
                    continue
                if not any(
                    all(f"\n    {k}: {v}\n" in "\n" + b + "\n" for k, v in ligne.items())
                    for b in blocs
                ):
                    manques.append(f"ligne {ligne!r}")
            if not manques:
                return a
    return a + [f"`valeurs_attendues` absentes de la réponse : {manques}"]


def _anomalies_texte_connecte(texte: str, tout: str) -> list[str]:
    """Identifiants de jeu, UUID et URL du `texte` de référence présents dans la cassette."""
    a = []
    for ident in RE_ID_JEU.findall(texte) + RE_UUID.findall(texte):
        if ident not in tout:
            a.append(f"`reponse_reference.texte` : identifiant {ident!r} absent de la cassette")
    for url in RE_URL.findall(texte):
        url = url.rstrip(".,;:)")
        if not _url_presente(url, tout):
            a.append(f"`reponse_reference.texte` : URL {url!r} absente de la cassette")
    return a


def anomalies_rd(it: dict, racine: Path = RACINE) -> list[str]:
    """Anomalies d'un item RD contre sa cassette ; liste vide si l'item est cohérent."""
    a: list[str] = []
    try:
        valider_item(it, strict=True)
    except ItemInvalide as exc:
        a += [f"schéma strict (core.items) : {e}" for e in exc.erreurs]
    a += cj.anomalies_item("RD", it)
    if it.get("tache") != "Recherche de données" or it.get("fictif") is not False:
        a.append("`tache` ou `fictif` inattendu")
    if it.get("parametres") != {} or it.get("version_item") not in (1, 2):
        a.append("`parametres` = {} et `version_item` = 1 (2 si corrigé en v1.1) attendus")
    if not isinstance(it.get("entree"), str) or not it["entree"].strip():
        a.append("`entree` texte non vide attendue")
    mode = it.get("mode")
    if mode not in MODES_RD:
        a.append(f"`mode` hors de {MODES_RD} : {mode!r}")
    ident = it.get("id", "?")
    cassettes = it.get("cassettes")
    if not (isinstance(cassettes, list) and len(cassettes) == 1):
        return a + ["`cassettes` : un seul chemin attendu"]
    m = re.fullmatch(r"\.\./\.\./cassettes/(RD-[0-9]{3,})/(s[0-9]+)\.json", cassettes[0])
    if not m or m.group(1) != ident:
        return a + [f"`cassettes` : chemin inattendu {cassettes[0]!r}"]
    chemin = chemin_cassette(cassettes[0], racine)
    try:
        cassette = lire_cassette(chemin)
    except (OSError, ValueError) as exc:
        return a + [f"cassette illisible {chemin} ({type(exc).__name__})"]
    try:
        lire_cassette_production(chemin)
    except Exception as exc:  # noqa: BLE001 - l'erreur est rapportée telle quelle
        a.append(f"cassette refusée par slmsp.mcp.cassettes.lire_cassette : {exc}")
    if cassette.get("tools_list_sha256") != tools_list_sha256_config(racine):
        a.append("cassette : `tools_list_sha256` différente de config/outils-mcp.toml")
    if cassette.get("server") != SERVEUR or cassette.get("schema_version") != 1:
        a.append("cassette : `server` ou `schema_version` inattendu")
    interactions = cassette.get("interactions") or []
    if not interactions or any(
        i.get("request", {}).get("method") != "tools/call" for i in interactions
    ):
        a.append("cassette : interactions `tools/call` attendues")
        return a

    # Appels attendus : schéma, règles, présence et ordre dans la cassette.
    appels = it.get("appels_attendus")
    if not (isinstance(appels, list) and appels):
        return a + ["`appels_attendus` : liste non vide attendue"]
    requetes = [i["request"]["params"] for i in interactions]
    positions: list[int] = []
    for n, appel in enumerate(appels):
        outil = appel.get("outil") if isinstance(appel, dict) else None
        lieu = f"appel {n} ({outil})"
        if not isinstance(appel, dict) or set(appel) - CLES_APPEL:
            a.append(f"{lieu} : clés inattendues")
            continue
        if not isinstance(appel.get("regle"), str) or not appel["regle"].strip():
            a.append(f"{lieu} : `regle` (prose) attendue")
        a += _anomalies_regles(appel.get("regles"), lieu, outil)
        try:
            valider_appel(outil, appel.get("arguments", {}))
        except Exception as exc:  # noqa: BLE001 - l'erreur est rapportée telle quelle
            a.append(f"{lieu} : non conforme au schéma figé ({exc})")
        trouve = [
            k
            for k, r in enumerate(requetes)
            if r["name"] == outil and r["arguments"] == appel.get("arguments")
        ]
        if not trouve:
            a.append(f"{lieu} : arguments absents de la cassette")
            continue
        if isinstance(appel.get("regles"), dict) and not requete_satisfait(
            appel["regles"], requetes[trouve[0]]["arguments"]
        ):
            a.append(f"{lieu} : la requête enregistrée ne satisfait pas ses `regles`")
        if isinstance(appel.get("regles"), dict) and not appel["regles"].get("ordre_libre"):
            positions.append(trouve[0])
    if positions != sorted(positions):
        a.append("`appels_attendus` hors de l'ordre de la cassette")

    # Provenance : le serveur MCP, la cassette et la date d'enregistrement.
    prov = it.get("provenance") or []
    mcp = [p for p in prov if isinstance(p, dict) and p.get("url") == SERVEUR]
    if len(mcp) != 1:
        a.append("`provenance` : une entrée « Serveur MCP data.gouv » attendue")
    else:
        if mcp[0].get("cassette") != cassettes[0]:
            a.append("`provenance` : `cassette` différente de `cassettes[0]`")
        enregistre = datetime.fromisoformat(cassette["recorded_at"])
        try:
            consulte = datetime.fromisoformat(mcp[0].get("consulte_le", ""))
        except ValueError:
            consulte = None
        if consulte != enregistre:
            a.append("`provenance` : `consulte_le` différent de `recorded_at`")

    ref = it.get("reponse_reference")
    if not isinstance(ref, dict) or not isinstance(ref.get("texte"), str) or not ref["texte"]:
        return a + ["`reponse_reference` : objet avec `texte` attendu"]
    jeu = ref.get("jeu_principal")
    if not isinstance(jeu, dict) or not {"id", "titre", "producteur", "url"} <= set(jeu):
        return a + ["`reponse_reference.jeu_principal` : id, titre, producteur, url attendus"]
    producteurs = it.get("producteurs")
    if not (isinstance(producteurs, list) and producteurs and jeu["producteur"] in producteurs):
        a.append("`producteurs` doit contenir le producteur du jeu principal")

    if mode == "repli":
        return a + _anomalies_repli(it, cassette, interactions, ref, mcp)
    if mode != "connecte":
        return a

    if cassette.get("initialize") is None:
        a.append("connecté : `initialize` attendu")
    if any(i.get("simulation") or i.get("response") is None for i in interactions):
        a.append("connecté : interaction simulée ou sans réponse")
        return a
    if any("error" in (i.get("response") or {}) for i in interactions):
        a.append("connecté : erreur JSON-RPC enregistrée")
    if any((i.get("response") or {}).get("result", {}).get("isError") for i in interactions):
        a.append("connecté : réponse d'outil en erreur (isError)")
    tout = "\n".join(t for i in interactions for t in textes_reponse(i))
    blocs = blocs_jeux(interactions)
    if not all(isinstance(jeu[c], str) for c in ("id", "titre", "producteur", "url")):
        a.append("`jeu_principal` : champs textuels attendus")
    elif not _jeu_dans_un_bloc(jeu, blocs):
        a.append(f"`jeu_principal` : id, titre, producteur et url absents d'un même bloc ({jeu})")
    for champ in ("derniere_mise_a_jour", "licence"):
        if champ in jeu and (not isinstance(jeu[champ], str) or jeu[champ] not in tout):
            a.append(f"`jeu_principal.{champ}` absent des réponses : {jeu[champ]!r}")
    for autre in ref.get("autres_jeux_cites_possibles") or []:
        if not isinstance(autre, dict) or any(
            not isinstance(v, str) or v not in tout for v in autre.values()
        ):
            a.append(f"`autres_jeux_cites_possibles` absent des réponses : {autre!r}")
    a += _anomalies_texte_connecte(ref["texte"], tout)
    if it.get("valeurs_attendues") is not None:
        a += _anomalies_valeurs(it, interactions)
    return a


def _anomalies_repli(it: dict, cassette: dict, interactions, ref: dict, mcp) -> list[str]:
    a = []
    if cassette.get("initialize") is not None:
        a.append("repli : `initialize` nul attendu")
    if any(not i.get("simulation") or i.get("response") is not None for i in interactions):
        a.append("repli : toutes les interactions doivent être simulées")
    if not ref.get("comportement_attendu"):
        a.append("repli : `reponse_reference.comportement_attendu` attendu")
    if it.get("valeurs_attendues"):
        a.append("repli : pas de `valeurs_attendues`")
    prov = it.get("provenance") or []
    if not any(
        isinstance(p, dict)
        and p.get("depot") == CATALOGUE
        and p.get("revision") == REVISION_CATALOGUE
        for p in prov
    ):
        a.append("repli : entrée de provenance du catalogue local (dépôt, révision) attendue")
    if mcp and "simulé" not in (mcp[0].get("role") or ""):
        a.append("repli : le `role` de la provenance MCP doit dire que l'échec est simulé")
    for interaction in interactions:
        simulation = interaction.get("simulation") or {}
        type_ = simulation.get("type")
        annonce = (
            str(simulation.get("statut"))
            if type_ == "erreur_http"
            else ANNONCE_SIMULATION.get(type_)
        )
        for champ in ("comportement_attendu", "texte"):
            if not annonce or annonce not in (ref.get(champ) or ""):
                a.append(f"repli : `{champ}` n'annonce pas la panne simulée ({type_}, {annonce})")
    return a


# ---------------------------------------------------------------------------
# Données réelles
# ---------------------------------------------------------------------------
def _construction(version: str) -> Path:
    return RACINE / "eval" / "construction" / version


def _items(version: str) -> list[dict]:
    chemin = _construction(version) / "RD.jsonl"
    if not chemin.is_file():
        return []
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


def _retenus(version: str) -> list[dict]:
    verdicts, _ = cj.derniers_verdicts(_construction(version))
    return [it for it in RD[version] if verdicts.get(it["id"], {}).get("verdict") != "rejete"]


RD = {v: _items(v) for v in VERSIONS}
RETENUS_V = {v: _retenus(v) for v in VERSIONS}
RETENUS = RETENUS_V["v1.0"]  # cas négatifs du contrôleur
PAIRES = [(v, it) for v in VERSIONS for it in RETENUS_V[v]]
REPLIS = [(v, it) for v, it in PAIRES if it.get("mode") == "repli"]


def _ids(paires: list[tuple[str, dict]]) -> list[str]:
    return [f"{v}-{it['id']}" for v, it in paires]


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


@pytest.mark.parametrize("version", VERSIONS)
def test_fichier_jsonl_utf8_lf_trie(version):
    texte = (_construction(version) / "RD.jsonl").read_bytes().decode("utf-8")
    assert "\r" not in texte and texte.endswith("\n")
    for n, ligne in enumerate(texte.split("\n")[:-1], 1):
        assert ligne == json.dumps(json.loads(ligne), ensure_ascii=False), f"RD.jsonl:{n}"
    ids = [it["id"] for it in RD[version]]
    assert ids == sorted(ids, key=cj.cle_id) and len(set(ids)) == len(ids), ids


@pytest.mark.parametrize("version", VERSIONS)
def test_lecture_stricte_par_core_items(version):
    items = lire_items(_construction(version) / "RD.jsonl", strict=True)
    assert len(items) == len(RD[version])


@pytest.mark.parametrize(("version", "it"), PAIRES, ids=_ids(PAIRES))
def test_item_coherent_avec_sa_cassette(version, it):
    assert anomalies_rd(it) == [], it["id"]


@pytest.mark.parametrize("version", VERSIONS)
def test_composition_rd(version):
    RETENUS = RETENUS_V[version]
    REPLIS = [it for it in RETENUS if it.get("mode") == "repli"]
    assert len(RETENUS) == 40
    assert Counter(it["difficulte"] for it in RETENUS) == {
        "facile": 15,
        "moyen": 15,
        "difficile": 10,
    }
    # Table « Lots » de la spec : facile / moyen / difficile par thème.
    par_theme = Counter((it["theme"], it["difficulte"]) for it in RETENUS)
    attendu = {
        "social-autonomie": (5, 4, 3),
        "etat-civil-papiers": (2, 2, 2),
        "travail-emploi": (2, 2, 2),
        "collectivites": (2, 3, 1),
        "fiscalite-locale": (2, 2, 0),
        "famille-education-sante": (2, 2, 2),
    }
    for theme, cibles in attendu.items():
        reel = tuple(par_theme[(theme, d)] for d in ("facile", "moyen", "difficile"))
        assert reel == cibles, (theme, reel)
    assert Counter(it["theme"] for it in RETENUS) == {t: sum(c) for t, c in attendu.items()}
    valeurs = [it for it in RETENUS if it.get("valeurs_attendues")]
    assert len(valeurs) == 5
    assert all(it["difficulte"] == "difficile" for it in valeurs)
    for it in valeurs:
        assert any(a["outil"] == "query_resource_data" for a in it["appels_attendus"]), it["id"]
    assert len(REPLIS) == 4 and all(it["difficulte"] != "difficile" for it in REPLIS)
    assert sum(it["mode"] == "connecte" for it in RETENUS) == 36
    producteurs = {p for it in RETENUS for p in it["producteurs"]}
    assert len(producteurs) >= 6, producteurs
    principaux = [it["reponse_reference"]["jeu_principal"]["id"] for it in RETENUS]
    assert len(set(principaux)) == len(principaux), "jeu principal en double"


def _fixture_repli() -> dict:
    return json.loads(FIXTURE_REPLI.read_text(encoding="utf-8"))


@pytest.mark.parametrize("version", VERSIONS)
def test_fixture_repli_couvre_les_replis(version):
    fixture = _fixture_repli()
    assert fixture["depot"] == CATALOGUE and fixture["revision"] == REVISION_CATALOGUE
    assert set(fixture["jeux"]) == {it["id"] for v, it in REPLIS if v == version}


@pytest.mark.parametrize(("version", "it"), REPLIS, ids=_ids(REPLIS))
def test_repli_reference_egale_la_fixture(version, it):
    ligne = _fixture_repli()["jeux"][it["id"]]
    jeu = it["reponse_reference"]["jeu_principal"]
    assert jeu == {
        "id": ligne["id"],
        "titre": ligne["title"],
        "producteur": ligne["organization"],
        "url": ligne["url"],
    }, it["id"]
    assert it["producteurs"] == [ligne["organization"]], it["id"]


@pytest.mark.parametrize(("version", "it"), REPLIS, ids=_ids(REPLIS))
def test_repli_fixture_recoupee_avec_le_catalogue_local(version, it):
    """La ligne de la fixture est celle de l'instantané parquet (si présent)."""
    duckdb = pytest.importorskip("duckdb")
    candidat = os.environ.get("SLMSP_EVAL_SOURCES")
    sources = Path(candidat) if candidat else RACINE / "data" / "raw" / "eval-sources"
    parquets = sorted((sources / "hf" / CATALOGUE).rglob("*.parquet"))
    if not parquets:
        if candidat:
            pytest.fail(f"SLMSP_EVAL_SOURCES ne contient pas le catalogue : {sources}")
        pytest.skip("instantané du catalogue absent (SLMSP_EVAL_SOURCES)")
    liste = ", ".join("'" + p.resolve().as_posix().replace("'", "''") + "'" for p in parquets)
    ligne = _fixture_repli()["jeux"][it["id"]]
    lignes = (
        duckdb.connect()
        .execute(
            "SELECT chunk_id, title, url, organization, license "
            f"FROM read_parquet([{liste}]) WHERE chunk_id = ?",
            [ligne["id"]],
        )
        .fetchall()
    )
    attendu = (ligne["id"], ligne["title"], ligne["url"], ligne["organization"], ligne["license"])
    assert attendu in lignes, (it["id"], lignes)


@pytest.mark.parametrize("version", VERSIONS)
def test_hors_sujets_du_calibrage(version):
    for it in RETENUS_V[version]:
        assert "defibrillat" not in json.dumps(it, ensure_ascii=False).lower(), it["id"]
        assert "défibrillat" not in json.dumps(it, ensure_ascii=False).lower(), it["id"]


@pytest.mark.parametrize("version", VERSIONS)
def test_cassettes_sans_orphelines(version):
    """Chaque fichier sous `eval/cassettes/RD-*/` est cité par un item retenu (les dossiers
    `RD-501` et suivants appartiennent au jeu de développement `dev1`, spec O4)."""
    dossier = RACINE / "eval" / "cassettes"
    cites = {chemin_cassette(c) for it in RETENUS_V[version] for c in it["cassettes"]}
    fichiers = {
        f.resolve()
        for d in dossier.glob("RD-*")
        if int(d.name.split("-")[1]) < 501
        for f in d.rglob("*")
        if f.is_file()
    }
    assert sorted(str(f) for f in fichiers - cites) == []
    assert sorted(str(f) for f in cites - fichiers) == []


@pytest.mark.parametrize("version", VERSIONS)
def test_verdicts_acceptes(version):
    chemin = _construction(version) / "verification" / "RD.jsonl"
    assert chemin.is_file(), f"verdicts absents : {chemin}"
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if not ligne.strip():
            continue
        v = json.loads(ligne)
        assert v["verdict"] in cj.VERDICTS, n
        assert cj.RE_DATE_ISO.fullmatch(v["verifie_le"]), n
        if v["verdict"] == "rejete":
            assert v.get("motif") in cj.MOTIFS, n
    verdicts, erreurs = cj.derniers_verdicts(_construction(version))
    assert [e for e in erreurs if e.startswith("RD.jsonl")] == []
    non_acceptes = [
        it["id"]
        for it in RETENUS_V[version]
        if verdicts.get(it["id"], {}).get("verdict") != "accepte"
    ]
    assert non_acceptes == []


@pytest.mark.parametrize("version", VERSIONS)
def test_commande_composition(capsys, version):
    assert cj.cmd_composition(RACINE, version) == 0
    sortie = capsys.readouterr().out
    assert (
        "| RD (Recherche de données) | 40 / 40 (0) | 15 / 15 (0) | 15 / 15 (0) | 10 / 10 (0) |"
        in sortie
    )
    anomalies = sortie.split("## Anomalies de structure", 1)[1]
    assert not re.search(r"\bRD-[0-9]", anomalies), anomalies


# ---------------------------------------------------------------------------
# Contrôleur : cas négatifs sur une copie d'un item réel
# ---------------------------------------------------------------------------
def _item_a_valeurs() -> dict:
    return next(
        it for it in RETENUS if it.get("valeurs_attendues") and len(it["appels_attendus"]) >= 3
    )


def _sans_ordre_libre(it: dict) -> dict:
    for appel in it["appels_attendus"]:
        appel["regles"]["ordre_libre"] = False
    return it


def _alterer_id(it):
    it["reponse_reference"]["jeu_principal"]["id"] = "0" * 24


def _alterer_valeur(it):
    ligne = it["valeurs_attendues"]["lignes"][0]
    cle = next(iter(ligne))
    ligne[cle] = ligne[cle] + "-absent"


def _inverser_appels(it):
    _sans_ordre_libre(it)["appels_attendus"].reverse()


@pytest.mark.parametrize(
    ("alteration", "motif"),
    [
        (_alterer_id, "jeu_principal"),
        (_alterer_valeur, "valeurs_attendues"),
        (_inverser_appels, "ordre de la cassette"),
    ],
    ids=["mauvais-jeu-principal", "valeur-absente", "ordre-inverse"],
)
def test_controleur_signale_une_alteration(alteration, motif):
    it = copy.deepcopy(_item_a_valeurs())
    assert anomalies_rd(it) == []
    alteration(it)
    anomalies = anomalies_rd(it)
    assert any(motif in a for a in anomalies), anomalies


def test_controleur_signale_une_interaction_simulee_dans_un_connecte(tmp_path):
    it = copy.deepcopy(_item_a_valeurs())
    (tmp_path / "config").mkdir()
    shutil.copy(RACINE / "config" / "outils-mcp.toml", tmp_path / "config" / "outils-mcp.toml")
    source = chemin_cassette(it["cassettes"][0])
    cassette = lire_cassette(source)
    cassette["interactions"][0]["response"] = None
    cassette["interactions"][0]["simulation"] = {"type": "delai_depasse", "statut": None}
    cible = chemin_cassette(it["cassettes"][0], tmp_path)
    cible.parent.mkdir(parents=True)
    cible.write_text(json.dumps(cassette, ensure_ascii=False), encoding="utf-8")
    anomalies = anomalies_rd(it, tmp_path)
    assert any("connecté : interaction simulée" in a for a in anomalies), anomalies


# ---------------------------------------------------------------------------
# Fonctions pures (cas synthétiques)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("regle", "present", "valeur", "attendu"),
    [
        ({"exact": "abc"}, True, "abc", True),
        ({"exact": "abc"}, True, "abd", False),
        ({"exact": 5}, True, 5, True),
        ({"exact": 5}, True, "5", False),
        ({"exact": "abc"}, False, None, False),
        ({"contient_un_de": ["prénom", "prenom"]}, True, "Fichier des Prénoms", True),
        ({"contient_un_de": ["prénom"]}, True, "fichier des prenoms", False),
        ({"contient_un_de": ["prenom"]}, True, "fichier des prenoms", True),
        ({"contient_un_de": ["demandeurs d emploi"]}, True, "demandeurs d’emploi", True),
        ({"contient_un_de": ["demandeurs d emploi"]}, True, "demandeurs d'emploi", True),
        ({"contient_un_de": ["es handicap"]}, True, "ES-Handicap", True),
        ({"contient_un_de": ["ase"]}, True, "base nationale", False),
        ({"contient_un_de": ["apa"]}, True, "capacité d'accueil", False),
        ({"contient_un_de": ["apa"]}, True, "APA à domicile", True),
        ({"contient_un_de": ["rsa", "revenu"]}, True, "allocataires", False),
        ({"optionnel": True}, False, None, True),
        ({"optionnel": True}, True, 99, True),
        ({"optionnel": True, "exact": 20}, False, None, True),
        ({"optionnel": True, "exact": 20}, True, 10, False),
        ({"optionnel": True, "contient_un_de": ["caen"]}, False, None, True),
        ({"optionnel": True, "contient_un_de": ["caen"]}, True, "Ville de Caen", True),
        ({"optionnel": True, "contient_un_de": ["caen"]}, True, "Poitiers", False),
        ({"mot_entier_un_de": ["REI"]}, True, "fichier REI 2024", True),
        ({"mot_entier_un_de": ["REI"]}, True, "Reims", False),
        ({"mot_entier_un_de": ["REI"], "contient_un_de": ["impôts locaux"]}, True, "impôts", False),
        ({"mot_entier_un_de": ["REI"], "contient_un_de": ["impots"]}, True, "impots locaux", True),
        ({"mot_entier_un_de": ["REI"]}, False, None, False),
    ],
)
def test_regle_argument(regle, present, valeur, attendu):
    assert regle_argument_satisfaite(regle, present, valeur) is attendu


def test_regles_mal_formees():
    bonnes = {"optionnel": False, "ordre_libre": False, "arguments": {}}
    assert _anomalies_regles(bonnes, "x") == []
    for fragment in ("É", "es-handicap", "demandeurs d'emploi", " rsa"):
        regles = {
            "optionnel": False,
            "ordre_libre": False,
            "arguments": {"query": {"contient_un_de": [fragment]}},
        }
        assert _anomalies_regles(regles, "x", "search_datasets"), fragment
    assert _anomalies_regles({"optionnel": False, "arguments": {}}, "x")
    inconnu = {"optionnel": False, "ordre_libre": False, "arguments": {"q": {"exact": "a"}}}
    assert _anomalies_regles(inconnu, "x", "search_datasets")
