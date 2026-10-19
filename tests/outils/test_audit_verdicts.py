"""Tests de `outils/audit_verdicts.py` sur un mini-run fabriqué (chaînes factices)."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "outils" / "audit_verdicts.py"
INJECTION = "<script>alert('<sortie-factice>')</script>"


def _charger() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_verdicts", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ecrire(chemin: Path, lignes: list[dict]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(json.dumps(x) for x in lignes) + "\n", encoding="utf-8")


def _verdict(item: str, juge: str, notes: dict[str, int]) -> dict:
    criteres = {c: {"note": n, "justification": f"<justif-{juge}-{c}>"} for c, n in notes.items()}
    return {
        "item_id": item,
        "juge": juge,
        "statut": "juge",
        "tache": item.split("-")[0],
        "verdict": {"criteres": criteres, "inventions": [], "confiance": "haute"},
    }


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    _ecrire(
        tmp_path / "eval" / "jeu" / "v1.1" / "items.jsonl",
        [
            {"id": "LC-001", "entree": {"consigne": "<consigne-factice>", "texte": "<texte-1>"}},
            {"id": "Q-001", "entree": "<question-factice>", "reponse_reference": "<ref-1>"},
            {"id": "Q-002", "entree": "<question-factice-2>"},
        ],
    )
    gens = [
        {"item_id": "LC-001", "sortie_canonique": {"texte": INJECTION}, "tronquee": True},
        {"item_id": "Q-001", "sortie_canonique": {"texte": "<réponse-factice-1>"}},
        {"item_id": "Q-002", "sortie_canonique": {"texte": "<réponse-factice-2>"}},
    ]
    _ecrire(tmp_path / "runs" / "eval-generation" / "G1" / "generations.jsonl", gens)
    notation = tmp_path / "runs" / "eval-notation" / "N1"
    meta = {
        "modele_ref": "ft:modele-factice",
        "jeu_version": "v1.1",
        "config": {"run_generation": "G1"},
    }
    notation.mkdir(parents=True)
    (notation / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    scores = {"taches": {"LC": {"kappa": {"valeur": 0.0, "effectif": 1, "par_critere": {}}}}}
    (notation / "scores.json").write_text(json.dumps(scores), encoding="utf-8")
    _ecrire(
        notation / "verdicts.jsonl",
        [
            _verdict("LC-001", "principal", {"fidelite": 0, "termes_juridiques": 1}),
            _verdict("LC-001", "second", {"fidelite": 2, "termes_juridiques": 1}),
            _verdict("Q-001", "principal", {"exactitude": 2}),
            _verdict("Q-001", "second", {"exactitude": 2}),
            _verdict("Q-002", "principal", {"exactitude": 1}),
        ],
    )
    return tmp_path


def _donnees(html: str) -> dict:
    brut = re.search(r'<script id="donnees" type="application/json">(.*?)</script>', html, re.S)
    assert brut
    return json.loads(brut.group(1))


def test_html_contient_items_et_deux_verdicts(racine: Path, tmp_path: Path) -> None:
    sortie = tmp_path / "sortie" / "audit.html"
    assert (
        _charger().main(["--notation", "N1", "--racine", str(racine), "--sortie", str(sortie)]) == 0
    )
    html = sortie.read_text(encoding="utf-8")
    donnees = _donnees(html)
    assert [i["id"] for i in donnees["items"]] == ["LC-001", "Q-001"]  # Q-002 n'a pas de 2e juge
    lc = donnees["items"][0]
    fidelite = next(c for c in lc["criteres"] if c["cle"] == "fidelite")
    assert fidelite["diverge"] is True
    assert fidelite["principal"]["justification"] == "<justif-principal-fidelite>"
    assert fidelite["second"]["justification"] == "<justif-second-fidelite>"
    assert lc["tronquee"] is True
    assert donnees["items"][1]["sortie"] == "<réponse-factice-1>"
    assert "https://" not in html.replace("</", "")  # aucun appel réseau


def test_echappement_de_la_sortie_du_modele(racine: Path, tmp_path: Path) -> None:
    sortie = tmp_path / "audit.html"
    _charger().main(["--notation", "N1", "--racine", str(racine), "--sortie", str(sortie)])
    html = sortie.read_text(encoding="utf-8")
    assert "<script>alert" not in html
    assert html.count("<script") == 2  # JSON des données + script de la page
    assert _donnees(html)["items"][0]["sortie"] == INJECTION


def test_filtre_taches_et_option_tous(racine: Path) -> None:
    module = _charger()
    seul_q = module.construire_donnees(racine, ["N1"], {"Q"})
    assert {i["id"] for i in seul_q["items"]} == {"Q-001"}
    tous = module.construire_donnees(racine, ["N1"], None, tous=True)
    assert {i["id"] for i in tous["items"]} == {"LC-001", "Q-001", "Q-002"}


def test_run_inconnu(racine: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        _charger().main(
            ["--notation", "absent", "--racine", str(racine), "--sortie", str(tmp_path / "x.html")]
        )
