"""Sous-commande `changements` de eval/outils/construire_jeu.py (jeu v1.1). Aucun réseau.

Deux `items.jsonl` factices (référence gelée, nouvelle version assemblée) dans `tmp_path` ; le
dépôt n'est jamais lu ni écrit.
"""

from __future__ import annotations

import builtins
import copy
import errno
import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

OUTIL = Path(__file__).resolve().parents[2] / "eval" / "outils" / "construire_jeu.py"


def _charger():
    spec = importlib.util.spec_from_file_location("construire_jeu_changements", OUTIL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_jeu_changements"] = module
    spec.loader.exec_module(module)
    return module


cj = _charger()


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


def _reference() -> list[dict]:
    return [
        {
            "id": "Q-001",
            "tache": "Question",
            "difficulte": "facile",
            "theme": "collectivites",
            "entree": "Question <a> ?",
            "elements_cles": ["<a>", "<b>", "<c>"],
            "version_item": 1,
        },
        {
            "id": "Q-002",
            "tache": "Question",
            "difficulte": "moyen",
            "theme": "collectivites",
            "entree": "Question retirée ?",
            "version_item": 1,
        },
        {
            "id": "CR-001",
            "tache": "Compte rendu",
            "difficulte": "difficile",
            "theme": "collectivites",
            "entree": {"consigne": "<consigne>", "transcription": "L1\nL2\nL3", "nb_mots": 3},
            "pieges": ["<p>"],
            "version_item": 1,
        },
        {
            "id": "RD-001",
            "tache": "Recherche de données",
            "difficulte": "facile",
            "theme": "collectivites",
            "entree": "Demande ?",
            "valeurs_attendues": {"lignes": [{"A": "1"}]},
            "version_item": 1,
        },
        {
            "id": "NR-001",
            "tache": "Non-régression",
            "difficulte": "facile",
            "theme": "non-classe",
            "entree": "Inchangé.",
            "version_item": 1,
        },
    ]


def _version() -> list[dict]:
    items = copy.deepcopy(_reference())
    par_id = {it["id"]: it for it in items}
    par_id["Q-001"].update(entree="Question <a2> ?", version_item=2)
    par_id["CR-001"]["entree"].update(transcription="L1\nL2\nL2 bis\nL3", nb_mots=4)
    par_id["CR-001"]["version_item"] = 2
    par_id["RD-001"]["valeurs_attendues"]["colonnes"] = ["A"]
    par_id["RD-001"]["version_item"] = 2
    items.remove(par_id["Q-002"])
    items.append(
        {
            "id": "Q-010",
            "tache": "Question",
            "difficulte": "moyen",
            "theme": "collectivites",
            "entree": "Nouvelle question ?",
            "version_item": 1,
        }
    )
    return items


def _ecrire(racine: Path, version: str, items: list[dict]) -> None:
    dossier = racine / "eval" / "jeu" / version
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "items.jsonl").write_text(
        "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items),
        encoding="utf-8",
        newline="\n",
    )


def _verdict(racine: Path) -> None:
    dossier = racine / "eval" / "construction" / "v1.1" / "verification"
    dossier.mkdir(parents=True)
    lignes = [
        {
            "id": "Q-002",
            "verdict": "rejete",
            "motif": "autre",
            "detail": "remplacé (arbitrage E)",
            "verifie_le": "2026-10-13",
        },
        {"id": "Q-010", "verdict": "accepte", "detail": "réserve <n>", "verifie_le": "2026-10-13"},
        {"id": "Q-001", "verdict": "accepte", "detail": "réserve <m>", "verifie_le": "2026-10-13"},
    ]
    (dossier / "Q.jsonl").write_text(
        "".join(json.dumps(lg, ensure_ascii=False) + "\n" for lg in lignes), "utf-8"
    )


def _sorties(racine: Path) -> tuple[Path, Path]:
    revue = racine / "eval" / "revue"
    return revue / "changements-v1.0-v1.1.jsonl", revue / "changements-v1.0-v1.1.md"


def _lancer(racine: Path, *options: str) -> int:
    return cj.main(["changements", "--version", "v1.1", "--racine", str(racine), *options])


def test_changements_nominal(tmp_path, capsys):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    _verdict(tmp_path)
    assert _lancer(tmp_path) == 0
    jsonl, md = _sorties(tmp_path)
    lignes = [json.loads(ligne) for ligne in jsonl.read_text(encoding="utf-8").splitlines()]
    assert [(lg["id"], lg["statut"]) for lg in lignes] == [
        ("Q-001", "modifie"),
        ("Q-002", "retire"),
        ("Q-010", "nouveau"),
        ("RD-001", "modifie"),
        ("CR-001", "modifie"),
    ]
    par_id = {lg["id"]: lg for lg in lignes}
    assert par_id["Q-001"]["champs"] == [
        {
            "champ": "entree",
            "changement": "modifie",
            "ancien": "Question <a> ?",
            "nouveau": "Question <a2> ?",
        },
        {"champ": "version_item", "changement": "modifie", "ancien": 1, "nouveau": 2},
    ]
    assert par_id["Q-001"]["item"] == _version()[0]
    champs_cr = {c["champ"]: c for c in par_id["CR-001"]["champs"]}
    assert set(champs_cr) == {"entree.transcription", "entree.nb_mots", "version_item"}
    assert champs_cr["entree.transcription"]["ancien"] == "L1\nL2\nL3"
    assert champs_cr["entree.transcription"]["nouveau"] == "L1\nL2\nL2 bis\nL3"
    assert par_id["RD-001"]["champs"][0] == {
        "champ": "valeurs_attendues.colonnes",
        "changement": "ajoute",
        "nouveau": ["A"],
    }
    assert par_id["Q-002"]["item"]["entree"] == "Question retirée ?"
    assert par_id["Q-002"]["verdict"]["detail"] == "remplacé (arbitrage E)"
    assert par_id["Q-010"]["item"]["entree"] == "Nouvelle question ?"
    assert par_id["Q-010"]["verdict"]["detail"] == "réserve <n>"
    assert par_id["Q-001"]["verdict"]["detail"] == "réserve <m>"
    assert "verdict" not in par_id["RD-001"]  # aucun verdict dans la version
    assert "NR-001" not in par_id  # inchangé
    texte = md.read_text(encoding="utf-8")
    assert "\\n" not in texte and "\r" not in texte
    for identifiant in par_id:
        assert f"## {identifiant} " in texte
    assert "Items nouveaux : 1 ; modifiés : 3 ; retirés : 1." in texte
    assert "+L2 bis" in texte  # différences ligne à ligne de la transcription
    assert "**Ancienne valeur** :" in texte and "Question <a2> ?" in texte
    assert "### `valeurs_attendues.colonnes` (ajouté)" in texte
    assert "remplacé (arbitrage E)" in texte
    assert "réserve <n>" in texte and "réserve <m>" in texte
    assert "**Dernier verdict** : aucun" in texte  # RD-001
    # Valeur non textuelle modifiée : différences ligne à ligne du JSON indenté.
    assert "Différences, ligne à ligne (JSON) :" in texte
    assert "-1\n+2" in texte  # version_item 1 -> 2
    sortie = capsys.readouterr().out
    assert "modifie : 3 (Q-001, RD-001, CR-001)" in sortie


@pytest.mark.parametrize("deja", [0, 1])
def test_changements_deja_exportes(tmp_path, capsys, deja):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    existant = _sorties(tmp_path)[deja]
    existant.parent.mkdir(parents=True)
    existant.write_text("ancien", encoding="utf-8")
    assert _lancer(tmp_path) == 2
    assert existant.read_text(encoding="utf-8") == "ancien"
    assert not _sorties(tmp_path)[1 - deja].exists()
    assert "déjà présent" in capsys.readouterr().err


@pytest.mark.parametrize("absent", ["v1.0", "v1.1"])
def test_changements_items_absents(tmp_path, capsys, absent):
    for version, items in (("v1.0", _reference()), ("v1.1", _version())):
        if version != absent:
            _ecrire(tmp_path, version, items)
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "items absents" in capsys.readouterr().err


def test_changements_id_duplique(tmp_path, capsys):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version() + [_version()[0]])
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "dupliqué" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("contenu", "message"),
    [
        ("{pas du json\n", "JSON illisible"),
        ('{"tache": "Question"}\n', "item sans `id`"),
        ('{"id": 12}\n', "item sans `id`"),
        ("[1, 2]\n", "item sans `id`"),
    ],
    ids=["json-illisible", "sans-id", "id-non-textuel", "pas-un-objet"],
)
def test_changements_items_illisibles(tmp_path, capsys, contenu, message):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    chemin = tmp_path / "eval" / "jeu" / "v1.1" / "items.jsonl"
    with chemin.open("a", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert message in capsys.readouterr().err


def test_changements_verdict_illisible(tmp_path, capsys):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    _verdict(tmp_path)
    chemin = tmp_path / "eval" / "construction" / "v1.1" / "verification" / "Q.jsonl"
    with chemin.open("a", encoding="utf-8", newline="\n") as f:
        f.write('{"id": "Q-002", "verdict": "rejeté"}\n')
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "verdict inconnu" in capsys.readouterr().err


@pytest.mark.parametrize("options", [("--reference", "v1.1"), ("--reference", "1.0")])
def test_changements_reference_invalide(tmp_path, options):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    assert _lancer(tmp_path, *options) == 2
    assert not (tmp_path / "eval" / "revue").exists()


def test_changements_echec_second_ecrit(tmp_path, capsys, monkeypatch):
    _ecrire(tmp_path, "v1.0", _reference())
    _ecrire(tmp_path, "v1.1", _version())
    jsonl, md = _sorties(tmp_path)
    vrai_open = builtins.open

    def faux_open(fichier, mode="r", *a, **k):
        if "x" in mode and Path(fichier) == md:
            raise OSError(errno.ENOSPC, "disque plein", str(fichier))
        return vrai_open(fichier, mode, *a, **k)

    monkeypatch.setattr(cj, "open", faux_open, raising=False)
    assert _lancer(tmp_path) == 2
    assert not jsonl.exists() and not md.exists()
    assert "rien n'est écrit" in capsys.readouterr().err


def test_diff_champs_types():
    assert cj.diff_champs({"a": 1}, {"a": 1}) == []
    assert cj.diff_champs({"a": 1}, {"a": True}) == [
        {"champ": "a", "changement": "modifie", "ancien": 1, "nouveau": True}
    ]
    assert cj.diff_champs({"a": [1, 2]}, {"a": [2, 1]})[0]["champ"] == "a"
    assert cj.diff_champs({"a": {"b": 1}}, {}) == [
        {"champ": "a", "changement": "retire", "ancien": {"b": 1}}
    ]
