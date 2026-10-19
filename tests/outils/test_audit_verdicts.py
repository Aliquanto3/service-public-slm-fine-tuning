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


def _item_cr(module, criteres_p, criteres_s=None, source=None, gen=None):
    def v(criteres):
        return None if criteres is None else {"verdict": {"criteres": criteres}}

    return module._item_audit(
        "N1",
        "CR-001",
        {"id": "CR-001", "decisions_reference": ["<d1>", "<d2>"]} if source is None else source,
        {"sortie_canonique": {"texte": "x"}} if gen is None else gen,
        {"principal": v(criteres_p), "second": v(criteres_s)},
    )


def test_criteres_en_liste_refs_en_double_et_absentes() -> None:
    module = _charger()
    liste = {
        "presence_elements": [
            {"ref": "D1", "present": 1, "justification": "j"},
            {"ref": "D1", "present": 0.5},
            {"present": 0},
        ]
    }
    item = _item_cr(module, liste, {"presence_elements": [{"ref": "D1", "present": 1}]})
    cles = [c["cle"] for c in item["criteres"]]
    assert cles == ["presence_elements:D1", "presence_elements:D1#2", "presence_elements:?#3"]
    assert item["criteres"][0]["description"] == "<d1>"
    assert item["criteres"][0]["diverge"] is False
    assert len(item["alertes"]) == 2


def test_criteres_scalaire_un_seul_juge_et_alertes_absence() -> None:
    module = _charger()
    item = _item_cr(module, {"exactitude": 1}, None, source={}, gen={})
    (critere,) = item["criteres"]
    assert critere["principal"]["note"] == 1 and critere["second"] is None
    assert critere["diverge"] is False
    assert any("Item introuvable" in a for a in item["alertes"])
    assert any("Sortie introuvable" in a for a in item["alertes"])


def test_recherche_de_donnees_et_exclus(racine: Path) -> None:
    module = _charger()
    notation = racine / "runs" / "eval-notation" / "N1"
    lignes = [json.loads(x) for x in (notation / "verdicts.jsonl").read_text("utf-8").splitlines()]
    lignes.append(_verdict("Q-001", "second", {"exactitude": 1}) | {"statut": "echec"})
    _ecrire(notation / "verdicts.jsonl", lignes)
    donnees = module.construire_donnees(racine, ["N1"], None)
    assert donnees["runs"][0]["exclus"] == {"second (echec)": 1}
    assert "RD" in donnees["taches"]
    assert "libelle_correct" in donnees["taches"]["RD"]["criteres"]
