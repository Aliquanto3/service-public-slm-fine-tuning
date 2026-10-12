"""Sous-commande `revue` de eval/outils/construire_jeu.py (story 7.6). Aucun réseau.

Manifeste et items factices dans `tmp_path` ; le dépôt n'est jamais lu ni écrit.
"""

from __future__ import annotations

import builtins
import errno
import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

OUTIL = Path(__file__).resolve().parents[2] / "eval" / "outils" / "construire_jeu.py"


def _charger():
    spec = importlib.util.spec_from_file_location("construire_jeu_revue", OUTIL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_jeu_revue"] = module
    spec.loader.exec_module(module)
    return module


cj = _charger()
VERSION = "v1.0"


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


def _items() -> list[dict]:
    return [
        {
            "id": "Q-001",
            "tache": "Question",
            "difficulte": "facile",
            "theme": "social-autonomie",
            "entree": "Question factice ?",
            "elements_cles": ["élément <a>", "élément <b>"],
            "sans_reponse": False,
            "provenance": [{"source": "source factice", "consulte_le": "2026-10-12"}],
            "version_item": 1,
        },
        {
            "id": "CR-002",
            "tache": "Compte rendu",
            "difficulte": "moyen",
            "theme": "collectivites",
            "entree": {
                "consigne": "Consigne factice.",
                "transcription": "Ligne 1 de la transcription\nLigne 2 avec ``` dedans\n\nLigne 4",
            },
            "actions_reference": [{"action": "action <x>", "responsable": "<r>"}],
            "pieges": [],
            "parametres": {},
            "version_item": 1,
        },
        {
            "id": "NR-003",
            "tache": "Non-régression",
            "difficulte": "difficile",
            "theme": "non-classe",
            "entree": "Consigne NR factice.",
            "criteres": ["critère <c>"],
            "version_item": 1,
        },
    ]


def _jeu(racine: Path, relecture: list[str], items: list[dict] | None = None) -> list[str]:
    """Écrit `eval/jeu/v1.0/{items.jsonl, MANIFEST.json}` ; renvoie les lignes d'items."""
    dossier = racine / "eval" / "jeu" / VERSION
    dossier.mkdir(parents=True)
    lignes = [json.dumps(it, ensure_ascii=False) for it in (items or _items())]
    (dossier / "items.jsonl").write_text("\n".join(lignes) + "\n", encoding="utf-8", newline="\n")
    manifeste = {
        "version": VERSION,
        "statut": "provisoire",
        "echantillons": {"graine": 1, "second_juge": [], "relecture": relecture},
    }
    (dossier / "MANIFEST.json").write_text(json.dumps(manifeste), encoding="utf-8")
    return lignes


def _sorties(racine: Path) -> tuple[Path, Path]:
    revue = racine / "eval" / "revue"
    return (
        revue / f"echantillon-revue-{VERSION}.jsonl",
        revue / f"echantillon-revue-{VERSION}-lecture.md",
    )


def _lancer(racine: Path) -> int:
    return cj.main(["revue", "--version", VERSION, "--racine", str(racine)])


def test_revue_nominale(tmp_path, capsys):
    lignes = _jeu(tmp_path, ["NR-003", "Q-001", "CR-002"])
    assert _lancer(tmp_path) == 0
    jsonl, md = _sorties(tmp_path)

    brut = jsonl.read_bytes()
    assert b"\r" not in brut
    assert brut.decode("utf-8").split("\n")[:-1] == [lignes[2], lignes[0], lignes[1]]

    lecture = md.read_bytes().decode("utf-8")
    assert "\r" not in lecture
    assert "\\n" not in lecture, "séquence \\n échappée dans le Markdown"
    titres = [ligne for ligne in lecture.splitlines() if ligne.startswith("## ")]
    assert titres == [
        "## NR-003 — Non-régression (difficile, thème `non-classe`)",
        "## Q-001 — Question (facile, thème `social-autonomie`)",
        "## CR-002 — Compte rendu (moyen, thème `collectivites`)",
    ]
    assert lecture.count("- [ ] Relu") == 3 and lecture.count("- Remarques :") == 3
    # Listes en puces, objets en sous-puces, texte multiligne en bloc.
    assert "- élément <a>\n- élément <b>" in lecture
    assert "- **action** : action <x>" in lecture and "- **responsable** : <r>" in lecture
    assert "- **consigne** : Consigne factice." in lecture
    assert "````text\n  Ligne 1 de la transcription\n  Ligne 2 avec ``` dedans\n\n" in lecture
    assert "**entree** : Question factice ?" in lecture
    assert "**pieges** : []" in lecture
    sortie = capsys.readouterr().out
    assert "Items de l'échantillon : 3" in sortie


@pytest.mark.parametrize("deja", [0, 1])
def test_revue_deja_exportee(tmp_path, capsys, deja):
    _jeu(tmp_path, ["Q-001"])
    existant = _sorties(tmp_path)[deja]
    existant.parent.mkdir(parents=True)
    existant.write_text("ancien", encoding="utf-8")
    assert _lancer(tmp_path) == 2
    assert existant.read_text(encoding="utf-8") == "ancien"
    assert not _sorties(tmp_path)[1 - deja].exists()
    assert "déjà présent" in capsys.readouterr().err


def test_revue_echec_second_ecrit(tmp_path, capsys, monkeypatch):
    _jeu(tmp_path, ["Q-001"])
    jsonl, md = _sorties(tmp_path)
    officiel = jsonl.parent / f"echantillon-revue-{VERSION}.md"  # export du gel, préexistant
    officiel.parent.mkdir(parents=True)
    officiel.write_text("export du gel", encoding="utf-8")
    vrai_open = builtins.open

    def faux_open(fichier, mode="r", *a, **k):
        if "x" in mode and Path(fichier) == md:
            raise OSError(errno.ENOSPC, "disque plein", str(fichier))
        return vrai_open(fichier, mode, *a, **k)

    monkeypatch.setattr(cj, "open", faux_open, raising=False)
    assert _lancer(tmp_path) == 2
    assert not jsonl.exists() and not md.exists()
    assert officiel.read_text(encoding="utf-8") == "export du gel"
    assert "rien n'est écrit" in capsys.readouterr().err


def test_revue_manifeste_absent(tmp_path, capsys):
    _jeu(tmp_path, ["Q-001"])
    (tmp_path / "eval" / "jeu" / VERSION / "MANIFEST.json").unlink()
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "manifeste absent" in capsys.readouterr().err


def test_revue_identifiant_inconnu(tmp_path, capsys):
    _jeu(tmp_path, ["Q-001", "CT-099"])
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "CT-099" in capsys.readouterr().err


def test_revue_manifeste_sans_echantillon(tmp_path, capsys):
    _jeu(tmp_path, ["Q-001"])
    chemin = tmp_path / "eval" / "jeu" / VERSION / "MANIFEST.json"
    chemin.write_text(json.dumps({"version": VERSION}), encoding="utf-8")
    assert _lancer(tmp_path) == 2
    assert not (tmp_path / "eval" / "revue").exists()
    assert "echantillons.relecture" in capsys.readouterr().err
