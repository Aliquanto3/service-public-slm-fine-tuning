"""Vérification, gel, manifeste et contrôle git du Jeu d'évaluation (story 5.1, AD-25)."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from itertools import cycle
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import main
from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import CodeSortie, ManifesteInvalide
from slmsp.core.items import CODES, LIBELLES, THEMES, valider_item
from slmsp.core.schemas.manifeste_jeu import REGLE_EMPREINTE, ManifesteJeu
from slmsp.evaluation import config as cfg
from slmsp.evaluation import gel as module_gel
from slmsp.evaluation.gel import (
    JeuNonConforme,
    amorce_reelle,
    ecarts_composition,
    gel,
    jeu_gele_et_commite,
    sha256_lf,
    tirer_echantillons,
    verifier_jeu,
    verifier_manifeste,
)
from slmsp.mcp.outils import charger_config

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "eval" / "outils" / "construire_jeu.py"
CASSETTE = "../../cassettes/RD-001/session.json"
MAINTENANT = datetime(2026, 10, 12, 9, 0, tzinfo=UTC)


# --- Fabrique d'items factices ---------------------------------------------------------------


def item(code: str, numero: int = 1, **champs: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": f"{code}-{numero:03d}",
        "tache": LIBELLES[code],
        "difficulte": "facile",
        "theme": "social-autonomie" if code in cfg.TACHES_THEMATIQUES else "non-classe",
        "parametres": {},
        "provenance": [{"source": "<source-factice>", "consulte_le": "2026-10-12"}],
        "fictif": True,
        "version_item": 1,
    }
    propres: dict[str, dict[str, Any]] = {
        "Q": {
            "entree": f"<question-factice-{numero}>",
            "reponse_reference": "<reponse>",
            "elements_cles": ["<a>", "<b>", "<c>"],
            "sources_attendues": [],
            "sans_reponse": False,
        },
        "RD": {
            "entree": f"<demande-factice-{numero}>",
            "appels_attendus": [
                {
                    "outil": "search_datasets",
                    "arguments": {"query": "<requete>"},
                    "regles": {"arguments": {"query": {"contient_un_de": ["factice"]}}},
                }
            ],
            "cassettes": [CASSETTE],
            "reponse_reference": "<reponse>",
            "mode": "connecte",
            "producteurs": ["<producteur>"],
        },
        "CR": {
            "entree": {"consigne": "<consigne>", "notes": f"<notes-factices-{numero}>"},
            "decisions_reference": ["<decision>"],
            "actions_reference": [{"action": "<a>", "responsable": "<r>", "echeance": "<e>"}],
            "pieges": ["<piege>"],
        },
        "LC": {
            "entree": {"consigne": "<consigne>", "texte": f"<texte-{numero}>"},
            "informations_a_conserver": ["<info>"],
            "termes_juridiques_a_conserver": ["<terme>"],
            "kandel_moles_entree": 40.0,
        },
        "CO": {
            "entree": {"consigne": "<consigne>", "texte": "un textte factice"},
            "fautes": [
                {"debut": 3, "fin": 9, "erreur": "textte", "correction": "texte", "type": "o"}
            ],
            "texte_corrige_reference": "un texte factice",
        },
        "RE": {
            "entree": {"consigne": "<consigne>", "document": f"<document-{numero}>"},
            "points_cles_reference": ["<point>"],
            "longueur_demandee": "courte",
        },
        "CT": {
            "entree": {"consigne": "<consigne>", "objet": "<objet>"},
            "type_courrier": "<type>",
            "elements_obligatoires": ["<element>"],
            "champs_a_laisser_en_emplacement": ["[Champ]"],
        },
        "NR": {"entree": f"<consigne-nr-{numero}>", "reponse_reference": "<reponse>"},
    }
    base.update(copy.deepcopy(propres[code]))
    base.update(champs)
    return base


def jeu_complet() -> list[dict[str, Any]]:
    """225 items factices conformes à toute la composition de SPEC §2."""
    total_themes = sum(sum(cfg.CIBLES[c]) for c in cfg.TACHES_THEMATIQUES)
    themes = [t for t, part in cfg.PARTS_THEMES.items() for _ in range(round(part * total_themes))]
    themes_iter = iter(themes)
    producteurs = cycle([f"<producteur-{i}>" for i in range(cfg.CIBLE_RD_PRODUCTEURS)])
    items: list[dict[str, Any]] = []
    for code in CODES:
        numero = 0
        for difficulte, cible in zip(
            ("facile", "moyen", "difficile"), cfg.CIBLES[code], strict=True
        ):
            for _ in range(cible):
                numero += 1
                brut = item(code, numero, difficulte=difficulte)
                if code in cfg.TACHES_THEMATIQUES:
                    brut["theme"] = next(themes_iter)
                if code == "Q" and numero <= cfg.CIBLE_Q_SANS_REPONSE:
                    brut.update(sans_reponse=True, orientation_attendue="<orientation>")
                if code == "Q" and numero > 30:
                    brut["amorce_usager"] = "<amorce>"
                    brut["provenance"].append(
                        {"source": "AgentPublic/sp_questions_corpus", "consulte_le": "2026-10-12"}
                    )
                if code == "RD":
                    brut["producteurs"] = [next(producteurs)]
                    if numero <= cfg.CIBLE_RD_VALEURS:
                        brut["valeurs_attendues"] = [numero]
                    if numero > 40 - cfg.CIBLE_RD_REPLI:
                        brut["mode"] = "repli"
                if code == "CR" and numero <= cfg.CIBLE_CR_LONGUES:
                    brut["entree"]["transcription"] = "mot " * (cfg.SEUIL_CR_LONGUE_MOTS + 1)
                items.append(brut)
    return items


# --- Dépôt git de fixture --------------------------------------------------------------------


def git(depot: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args],
        cwd=depot,
        capture_output=True,
        text=True,
        check=True,
    )


def ecrire_items(depot: Path, items: list[dict[str, Any]], version: str = "v1.0") -> Path:
    chemin = depot / "eval" / "jeu" / version / "items.jsonl"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items).encode("utf-8")
    )
    return chemin


def ecrire_cassette(depot: Path, sha: str | None = None) -> Path:
    chemin = depot / "eval" / "cassettes" / "RD-001" / "session.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    config = charger_config(depot / "config" / "outils-mcp.toml")
    donnees = {
        "schema_version": 1,
        "server": "https://mcp.data.gouv.fr/mcp",
        "recorded_at": "2026-10-12T05:43:13+02:00",
        "initialize": None,
        "tools_list_sha256": sha or config.tools_list_sha256,
        "interactions": [],
    }
    chemin.write_bytes((json.dumps(donnees, indent=1) + "\n").encode("utf-8"))
    return chemin


def items_par_defaut() -> list[dict[str, Any]]:
    return [
        item("Q", 1),
        item("Q", 2, difficulte="moyen"),
        item("RD", 1),
        item("CR", 1),
        item("LC", 1, difficulte="difficile"),
        item("CO", 1),
        item("RE", 1),
        item("CT", 1),
        item("NR", 1),
        item("NR", 2, difficulte="moyen"),
    ]


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    depot = tmp_path / "depot"
    depot.mkdir()
    git(depot, "init", "-q", "-b", "main")
    git(depot, "config", "core.autocrlf", "false")
    (depot / "config").mkdir()
    shutil.copyfile(RACINE / "config" / "outils-mcp.toml", depot / "config" / "outils-mcp.toml")
    (depot / "eval").mkdir()
    (depot / "eval" / "grille-juge-v1.md").write_bytes(b"# Grille factice\n\n<bareme>\n")
    ecrire_items(depot, items_par_defaut())
    ecrire_cassette(depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "jeu factice")
    return depot


def etat(depot: Path) -> dict[str, bytes]:
    return {
        p.relative_to(depot).as_posix(): p.read_bytes()
        for p in sorted(depot.rglob("*"))
        if p.is_file() and ".git" not in p.relative_to(depot).parts
    }


# --- Configuration ---------------------------------------------------------------------------


def test_config_coherente_avec_les_tables() -> None:
    assert tuple(cfg.PARTS_THEMES) == THEMES
    assert sum(cfg.PARTS_THEMES.values()) == 1
    assert sum(sum(c) for c in cfg.CIBLES.values()) == 225
    assert set(cfg.CIBLES) == set(CODES)
    assert set(cfg.TACHES_JUGEES) == set(CODES) - {"RD", "CO"}


def test_config_identique_a_l_outil_de_construction() -> None:
    nom = "construire_jeu_story_5_1"
    spec = importlib.util.spec_from_file_location(nom, OUTIL)
    assert spec is not None and spec.loader is not None
    outil = importlib.util.module_from_spec(spec)
    sys.modules[nom] = outil
    try:
        spec.loader.exec_module(outil)
    finally:
        sys.modules.pop(nom, None)
    assert dict(cfg.CIBLES) == outil.CIBLES
    assert cfg.CIBLE_Q_SANS_REPONSE == outil.CIBLE_Q_SANS_REPONSE
    assert cfg.CIBLE_Q_PART_AMORCES == outil.CIBLE_Q_PART_AMORCES
    assert cfg.CIBLE_RD_VALEURS == outil.CIBLE_RD_VALEURS
    assert cfg.CIBLE_RD_REPLI == outil.CIBLE_RD_REPLI
    assert cfg.CIBLE_RD_PRODUCTEURS == outil.CIBLE_RD_PRODUCTEURS
    assert cfg.CIBLE_CR_LONGUES == outil.CIBLE_CR_LONGUES
    assert cfg.SEUIL_CR_LONGUE_MOTS == outil.SEUIL_CR_LONGUE_MOTS
    assert cfg.CORPUS_AMORCES == outil.CORPUS_AMORCES
    assert cfg.TACHES_THEMATIQUES == outil.CODES_THEMATIQUES
    assert {t: float(p) for t, p in cfg.PARTS_THEMES.items()} == outil.THEMES


# --- Vérification ----------------------------------------------------------------------------


def test_verifier_jeu_valide_n_ecrit_rien(depot: Path) -> None:
    avant = etat(depot)
    rapport = verifier_jeu("v1.0", depot)
    assert etat(depot) == avant
    assert rapport.erreurs == []
    assert len(rapport.items) == 10
    assert [c.name for c in rapport.cassettes] == ["session.json"]
    assert "Q facile : 1 (attendu 20)" in rapport.ecarts
    assert "RD producteurs distincts : 1 (attendu ≥ 6)" in rapport.ecarts
    assert "CR de plus de 4000 mots : 0 (attendu 5)" in rapport.ecarts
    assert any(e.startswith("thème social-autonomie") for e in rapport.ecarts)
    assert "10 items stricts acceptés" in rapport.texte()


def test_verifier_jeu_rd_absents(depot: Path) -> None:
    ecrire_items(depot, [i for i in items_par_defaut() if i["tache"] != LIBELLES["RD"]])
    rapport = verifier_jeu("v1.0", depot)
    assert rapport.erreurs == [] and rapport.cassettes == []
    assert "RD facile : 0 (attendu 15)" in rapport.ecarts
    assert "RD cas de repli : 0 (attendu 4)" in rapport.ecarts


def test_composition_complete_sans_ecart() -> None:
    items = [valider_item(i, strict=True) for i in jeu_complet()]
    assert len(items) == 225
    assert ecarts_composition(items) == []
    sans_un_q = [i for i in items if i.id != "Q-001"]
    ecarts = ecarts_composition(sans_un_q)
    assert "Q facile : 19 (attendu 20)" in ecarts
    assert "Q sans réponse : 7 (attendu 8)" in ecarts


def test_cassette_absente_bloquante(depot: Path) -> None:
    (depot / "eval" / "cassettes" / "RD-001" / "session.json").unlink()
    rapport = verifier_jeu("v1.0", depot)
    assert any("RD-001 : `cassettes` : cassette absente" in e for e in rapport.erreurs)


def test_empreinte_tools_list_differente_bloquante(depot: Path) -> None:
    (depot / "eval" / "cassettes" / "RD-001" / "session.json").unlink()
    ecrire_cassette(depot, sha="0" * 64)
    rapport = verifier_jeu("v1.0", depot)
    assert any("tools_list_sha256" in e for e in rapport.erreurs)


def test_cassette_illisible_bloquante(depot: Path) -> None:
    (depot / "eval" / "cassettes" / "RD-001" / "session.json").write_text("{", encoding="utf-8")
    assert any("RD-001 : `cassettes`" in e for e in verifier_jeu("v1.0", depot).erreurs)


def test_rd_sans_cassette(depot: Path) -> None:
    ecrire_items(depot, [item("RD", cassettes=[])])
    assert any(
        "RD-001 : `cassettes` : aucune cassette" in e for e in verifier_jeu("v1.0", depot).erreurs
    )
    ecrire_items(depot, [item("RD", cassettes=[], mode="hors-ligne")])
    assert verifier_jeu("v1.0", depot).erreurs == []


def test_amorce_hors_corpus_non_reelle(depot: Path) -> None:
    q = item("Q", amorce_usager="<amorce>")
    q["provenance"].append({"source": "<autre-corpus>", "consulte_le": "2026-10-12"})
    assert amorce_reelle(valider_item(q, strict=True)) is False
    ecrire_items(depot, [q])
    rapport = verifier_jeu("v1.0", depot)
    assert "Q issus d'amorces réelles : 0 (attendu ≥ 30)" in rapport.ecarts


def test_argument_inconnu_de_l_outil_bloquant(depot: Path) -> None:
    rd = item("RD")
    rd["appels_attendus"][0]["regles"]["arguments"]["inconnu"] = {"optionnel": True}
    ecrire_items(depot, [rd])
    erreurs = verifier_jeu("v1.0", depot).erreurs
    assert any("argument inconnu de search_datasets : inconnu" in e for e in erreurs), erreurs


def test_items_invalides_bloquants(depot: Path) -> None:
    sans_theme = item("Q")
    del sans_theme["theme"]
    ecrire_items(depot, [sans_theme])
    erreurs = verifier_jeu("v1.0", depot).erreurs
    assert any(e.startswith("Q-001 : `theme`") for e in erreurs)


def test_items_absents(depot: Path) -> None:
    assert any("absent" in e for e in verifier_jeu("v2", depot).erreurs)


def test_version_invalide(depot: Path) -> None:
    with pytest.raises(ValueError):
        verifier_jeu("calibrage", depot)


# --- Échantillons ----------------------------------------------------------------------------


def test_echantillons_deterministes_et_par_graine() -> None:
    items = [valider_item(i, strict=True) for i in jeu_complet()]
    a = tirer_echantillons(items, 7)
    b = tirer_echantillons(list(reversed(items)), 7)
    c = tirer_echantillons(items, 8)
    assert a == b
    assert a.second_juge != c.second_juge and a.relecture != c.relecture
    assert a.graine == 7


def test_echantillons_tailles() -> None:
    items = [valider_item(i, strict=True) for i in jeu_complet()]
    echantillons = tirer_echantillons(items, 7)
    second = echantillons.second_juge
    # Q 60 → 12, CR 25 → 5, LC 25 → 5, RE 15 → 3 (pas 4), CT 15 → 3, NR 30 → 6.
    attendus = {"Q": 12, "CR": 5, "LC": 5, "RE": 3, "CT": 3, "NR": 6}
    assert {c: sum(i.startswith(f"{c}-") for i in second) for c in attendus} == attendus
    assert not any(i.startswith(("RD-", "CO-")) for i in second)
    relecture = set(echantillons.relecture)
    assert len(relecture) == 47
    par_id = {i.id: i for i in items}
    strates = {(i.code, i.difficulte) for i in items}
    assert strates == {(par_id[i].code, par_id[i].difficulte) for i in relecture}
    assert second == sorted(second, key=lambda i: (i.split("-")[0], int(i.split("-")[1])))


def test_echantillons_petites_taches() -> None:
    items = [valider_item(item("Q", n), strict=True) for n in (1, 2)]
    echantillons = tirer_echantillons(items, 1)
    assert echantillons.second_juge == ["Q-001", "Q-002"]
    assert len(echantillons.relecture) == 1


# --- Gel -------------------------------------------------------------------------------------


def test_gel_provisoire(depot: Path) -> None:
    manifeste = gel("v1.0", "provisoire", 7, depot, maintenant=MAINTENANT)
    chemin = depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    revue = depot / "eval" / "revue" / "echantillon-revue-v1.0.md"
    assert chemin.is_file() and revue.is_file()
    assert chemin.read_bytes() == json_canonique(manifeste.model_dump(mode="json")) + b"\n"
    relu = ManifesteJeu.model_validate_json(chemin.read_bytes())
    assert relu == manifeste
    assert manifeste.statut == "provisoire" and manifeste.cree_le == MAINTENANT
    assert manifeste.regle_empreinte == REGLE_EMPREINTE
    assert manifeste.nb_items == 10
    assert [(f.chemin, f.role) for f in manifeste.fichiers] == [
        ("eval/jeu/v1.0/items.jsonl", "items"),
        ("eval/cassettes/RD-001/session.json", "cassette"),
        ("eval/grille-juge-v1.md", "grille"),
    ]
    for fichier in manifeste.fichiers:
        assert fichier.sha256 == sha256_lf(depot / fichier.chemin)
    assert manifeste.ecarts and manifeste.composition["Q"] == {
        "facile": 1,
        "moyen": 1,
        "difficile": 0,
    }
    assert manifeste.echantillons.graine == 7
    assert manifeste.echantillons.second_juge
    texte = revue.read_text(encoding="utf-8")
    for identifiant in manifeste.echantillons.relecture:
        assert f"## {identifiant} " in texte


def test_second_gel_refuse(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    avant = etat(depot)
    with pytest.raises(ArtefactExistant):
        gel("v1.0", "provisoire", 7, depot)
    assert etat(depot) == avant


def test_gel_refuse_si_l_export_existe(depot: Path) -> None:
    revue = depot / "eval" / "revue" / "echantillon-revue-v1.0.md"
    revue.parent.mkdir(parents=True)
    revue.write_text("<existant>", encoding="utf-8")
    with pytest.raises(ArtefactExistant):
        gel("v1.0", "provisoire", 7, depot)
    assert not (depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json").exists()


def test_gel_relu_refuse_les_ecarts(depot: Path) -> None:
    avant = etat(depot)
    with pytest.raises(JeuNonConforme, match="statut relu"):
        gel("v1.0", "relu", 7, depot)
    assert etat(depot) == avant


def test_gel_relu_d_un_jeu_complet(depot: Path) -> None:
    ecrire_items(depot, jeu_complet())
    manifeste = gel("v1.0", "relu", 3, depot)
    assert manifeste.ecarts == [] and manifeste.nb_items == 225
    assert len(manifeste.fichiers) == 3  # une seule cassette partagée


def test_gel_refuse_un_jeu_non_conforme(depot: Path) -> None:
    (depot / "eval" / "cassettes" / "RD-001" / "session.json").unlink()
    with pytest.raises(JeuNonConforme) as exc:
        gel("v1.0", "provisoire", 7, depot)
    assert exc.value.code_sortie == CodeSortie.ERREUR
    assert not (depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json").exists()


def test_echec_du_manifeste_retire_l_export(depot: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ecrire = module_gel._ecrire_exclusif
    appels: list[Path] = []

    def ecrire_puis_echouer(chemin: Path, donnees: bytes) -> None:
        appels.append(chemin)
        if len(appels) == 2:
            raise OSError("disque plein (simulé)")
        ecrire(chemin, donnees)

    monkeypatch.setattr(module_gel, "_ecrire_exclusif", ecrire_puis_echouer)
    with pytest.raises(OSError, match="simulé"):
        gel("v1.0", "provisoire", 7, depot)
    assert appels[0].name == "echantillon-revue-v1.0.md" and appels[1].name == "MANIFEST.json"
    assert not appels[0].exists() and not appels[1].exists()
    monkeypatch.setattr(module_gel, "_ecrire_exclusif", ecrire)
    assert gel("v1.0", "provisoire", 7, depot).nb_items == 10  # nouvelle tentative possible


def test_gel_refuse_sans_grille(depot: Path) -> None:
    (depot / "eval" / "grille-juge-v1.md").unlink()
    with pytest.raises(JeuNonConforme, match="grille"):
        gel("v1.0", "provisoire", 7, depot)


@pytest.mark.parametrize(("statut", "graine"), [("brouillon", 7), ("provisoire", "7")])
def test_gel_parametres_invalides(depot: Path, statut: str, graine: Any) -> None:
    with pytest.raises(ValueError):
        gel("v1.0", statut, graine, depot)


# --- Manifeste -------------------------------------------------------------------------------


def test_sha256_lf_normalise_les_fins_de_ligne(tmp_path: Path) -> None:
    (tmp_path / "lf").write_bytes(b"a\nb\n")
    (tmp_path / "crlf").write_bytes(b"a\r\nb\r\n")
    assert sha256_lf(tmp_path / "lf") == sha256_lf(tmp_path / "crlf")


def test_verifier_manifeste_intact_et_crlf(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    assert verifier_manifeste("v1.0", depot).nb_items == 10
    items = depot / "eval" / "jeu" / "v1.0" / "items.jsonl"
    items.write_bytes(items.read_bytes().replace(b"\n", b"\r\n"))
    assert verifier_manifeste("v1.0", depot).nb_items == 10


@pytest.mark.parametrize(
    "relatif",
    ["eval/jeu/v1.0/items.jsonl", "eval/cassettes/RD-001/session.json", "eval/grille-juge-v1.md"],
)
def test_alteration_d_un_octet(depot: Path, relatif: str) -> None:
    gel("v1.0", "provisoire", 7, depot)
    chemin = depot / relatif
    contenu = bytearray(chemin.read_bytes())
    contenu[5] ^= 0x01
    chemin.write_bytes(bytes(contenu))
    with pytest.raises(ManifesteInvalide, match=relatif) as exc:
        verifier_manifeste("v1.0", depot)
    assert exc.value.code_sortie == CodeSortie.MANIFESTE_INVALIDE == 4


def test_fichier_liste_absent(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    (depot / "eval" / "grille-juge-v1.md").unlink()
    with pytest.raises(ManifesteInvalide, match="absent"):
        verifier_manifeste("v1.0", depot)


def test_manifeste_absent_ou_invalide(depot: Path) -> None:
    with pytest.raises(ManifesteInvalide, match="absent"):
        verifier_manifeste("v1.0", depot)
    chemin = depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    chemin.write_text("{}", encoding="utf-8")
    with pytest.raises(ManifesteInvalide, match="invalide"):
        verifier_manifeste("v1.0", depot)


@pytest.mark.parametrize(
    ("modifier", "message"),
    [
        (lambda f: f.append(dict(f[1])), "en double"),
        (lambda f: f.append({**f[0], "chemin": "eval/jeu/v1.0/autre.jsonl"}), "`items`"),
        (lambda f: f.pop(), "`grille`"),
        (lambda f: f.append({**f[-1], "chemin": "eval/autre-grille.md"}), "`grille`"),
    ],
)
def test_manifeste_fichiers_coherents(depot: Path, modifier: Any, message: str) -> None:
    donnees = gel("v1.0", "provisoire", 7, depot).model_dump(mode="json")
    ManifesteJeu.model_validate(donnees)
    modifier(donnees["fichiers"])
    with pytest.raises(ValueError, match=message):
        ManifesteJeu.model_validate(donnees)


def test_manifeste_hors_eval_refuse(depot: Path) -> None:
    manifeste = gel("v1.0", "provisoire", 7, depot)
    donnees = manifeste.model_dump(mode="json")
    donnees["fichiers"][0]["chemin"] = "config/outils-mcp.toml"
    donnees["fichiers"][0]["sha256"] = sha256_lf(depot / "config" / "outils-mcp.toml")
    chemin = depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    chemin.write_bytes(json_canonique(donnees) + b"\n")
    with pytest.raises(ManifesteInvalide, match="hors de eval"):
        verifier_manifeste("v1.0", depot)


# --- Contrôle git ----------------------------------------------------------------------------


def test_jeu_gele_et_commite(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    with pytest.raises(ManifesteInvalide, match="non commité"):
        jeu_gele_et_commite("v1.0", depot)
    git(depot, "add", "-A")
    with pytest.raises(ManifesteInvalide, match="non commité"):
        jeu_gele_et_commite("v1.0", depot)  # indexé mais pas commité
    git(depot, "commit", "-q", "-m", "gel du jeu v1.0")
    commit_gel = git(depot, "rev-parse", "HEAD").stdout.strip()
    gele = jeu_gele_et_commite("v1.0", depot)
    assert gele.commit_gel == commit_gel
    assert gele.manifeste.version == "v1.0"
    # Un commit ultérieur sans rapport laisse le gel valide (ancêtre de HEAD).
    (depot / "autre.txt").write_text("<autre>", encoding="utf-8")
    git(depot, "add", "autre.txt")
    git(depot, "commit", "-q", "-m", "autre")
    assert jeu_gele_et_commite("v1.0", depot).commit_gel == commit_gel


def test_jeu_modifie_apres_commit(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "gel")
    # Passage en CRLF : empreintes identiques, mais `git diff HEAD` non vide.
    items = depot / "eval" / "jeu" / "v1.0" / "items.jsonl"
    items.write_bytes(items.read_bytes().replace(b"\n", b"\r\n"))
    assert verifier_manifeste("v1.0", depot)
    with pytest.raises(ManifesteInvalide, match="modifié"):
        jeu_gele_et_commite("v1.0", depot)


def test_jeu_altere_apres_commit(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "gel")
    (depot / "eval" / "grille-juge-v1.md").write_bytes(b"<autre grille>\n")
    with pytest.raises(ManifesteInvalide, match="grille-juge"):
        jeu_gele_et_commite("v1.0", depot)


def test_gel_commite_sur_une_autre_branche(depot: Path) -> None:
    git(depot, "checkout", "-q", "-b", "gel")
    gel("v1.0", "provisoire", 7, depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "gel sur une branche")
    git(depot, "checkout", "-q", "main")
    # Les fichiers du gel restent sur le disque (non suivis dans main).
    git(depot, "checkout", "-q", "gel", "--", "eval")
    git(depot, "reset", "-q")
    with pytest.raises(ManifesteInvalide, match="non commité"):
        jeu_gele_et_commite("v1.0", depot)


def test_commit_de_gel_ancetre_malgre_un_ajout_plus_recent_ailleurs(depot: Path) -> None:
    manifeste = "eval/jeu/v1.0/MANIFEST.json"
    gel("v1.0", "provisoire", 7, depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "gel sur main")
    commit_main = git(depot, "rev-parse", "HEAD").stdout.strip()
    # Branche de côté : le manifeste y est retiré puis ré-ajouté, par un commit plus récent.
    git(depot, "checkout", "-q", "-b", "cote")
    git(depot, "rm", "-q", manifeste)
    git(depot, "commit", "-q", "-m", "retrait")
    git(depot, "checkout", "-q", "main", "--", manifeste)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid"]
        + ["commit", "-q", "-m", "ré-ajout plus récent"],
        cwd=depot,
        check=True,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": "2030-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2030-01-01T00:00:00+00:00",
        },
    )
    commit_cote = git(depot, "rev-parse", "HEAD").stdout.strip()
    git(depot, "checkout", "-q", "main")
    ajouts = git(depot, "log", "--all", "--diff-filter=A", "--format=%H", "--", manifeste)
    assert ajouts.stdout.split()[0] == commit_cote  # le plus récent, non ancêtre de main
    assert jeu_gele_et_commite("v1.0", depot).commit_gel == commit_main


def test_manifeste_reecrit_apres_le_gel(depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "gel")
    # Commit ultérieur qui réécrit les items ET le manifeste, de façon cohérente.
    items = ecrire_items(depot, [*items_par_defaut(), item("NR", 3)])
    chemin = depot / "eval" / "jeu" / "v1.0" / "MANIFEST.json"
    donnees = json.loads(chemin.read_bytes())
    donnees["fichiers"][0]["sha256"] = sha256_lf(items)
    chemin.write_bytes(json_canonique(donnees) + b"\n")
    git(depot, "add", "-A")
    git(depot, "commit", "-q", "-m", "réécriture")
    assert verifier_manifeste("v1.0", depot)
    with pytest.raises(ManifesteInvalide, match="réécrit"):
        jeu_gele_et_commite("v1.0", depot)


def test_racine_hors_git(tmp_path: Path, depot: Path) -> None:
    gel("v1.0", "provisoire", 7, depot)
    copie = tmp_path / "copie"
    shutil.copytree(depot, copie, ignore=shutil.ignore_patterns(".git"))
    with pytest.raises(ManifesteInvalide):
        jeu_gele_et_commite("v1.0", copie)


# --- CLI -------------------------------------------------------------------------------------


def test_cli_verifier_seulement(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    avant = etat(depot)
    code = main(
        ["eval", "gel", "--version", "v1.0", "--verifier-seulement", "--racine", str(depot)]
    )
    assert code == CodeSortie.SUCCES
    assert etat(depot) == avant
    sortie = capsys.readouterr().out
    assert "10 items stricts acceptés" in sortie
    assert "Erreurs bloquantes : 0." in sortie
    assert "RD facile : 1 (attendu 15)" in sortie


def test_cli_verifier_seulement_erreur(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (depot / "eval" / "cassettes" / "RD-001" / "session.json").unlink()
    code = main(
        ["eval", "gel", "--version", "v1.0", "--verifier-seulement", "--racine", str(depot)]
    )
    assert code == CodeSortie.ERREUR
    sortie = capsys.readouterr()
    assert "cassette absente" in sortie.out
    assert "non conforme" in sortie.err


def test_cli_gel_puis_refus(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    arguments = ["eval", "gel", "--version", "v1.0", "--statut", "provisoire", "--graine", "7"]
    assert main([*arguments, "--racine", str(depot)]) == CodeSortie.SUCCES
    assert "gelé (provisoire)" in capsys.readouterr().out
    assert verifier_manifeste("v1.0", depot).echantillons.graine == 7
    assert main([*arguments, "--racine", str(depot)]) == CodeSortie.ERREUR
    assert "existe déjà" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [
        ["eval", "gel", "--version", "v1.0"],
        ["eval", "gel", "--version", "v1.0", "--statut", "provisoire"],
        ["eval", "gel", "--version", "v1.0", "--verifier-seulement", "--graine", "3"],
        ["eval", "gel", "--version", "v1.0", "--statut", "brouillon", "--graine", "3"],
        ["eval", "gel", "--version", "1.0", "--verifier-seulement"],
        ["eval", "gel", "--version", "calibrage", "--verifier-seulement"],
        ["eval", "gel", "--version", "calibrage", "--statut", "provisoire", "--graine", "3"],
        ["eval"],
    ],
)
def test_cli_usage(arguments: list[str], depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([*arguments, "--racine", str(depot)] if len(arguments) > 1 else arguments) == 2
    assert "Traceback" not in capsys.readouterr().err


@pytest.mark.parametrize("action", ["sonde-outils"])  # `run` : implémentée (stories 5.3, 5.6)
def test_cli_actions_non_implementees(action: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["eval", action, "--modele", "base:x"]) == CodeSortie.USAGE
    assert f"non implémentée : eval {action}" in capsys.readouterr().err


def test_cli_run_options_manquantes(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["eval", "run", "--modele", "base:x"]) == CodeSortie.USAGE
    assert "--quantification, --jeu requis" in capsys.readouterr().err
