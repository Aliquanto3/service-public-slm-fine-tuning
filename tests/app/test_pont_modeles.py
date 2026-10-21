"""Story 17.5b : pont, domaine « modeles » (comparatif embarqué, lecture seule)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.modeles import FICHIER, PontModeles


def _ecrire(chemin: Path, donnees: Any) -> Path:
    chemin.write_text(json.dumps(donnees), encoding="utf-8")
    return chemin


def test_rend_le_comparatif_embarque() -> None:
    reponse = PontModeles().appeler("comparatif_modeles")
    assert reponse["ok"] is True
    comparatif = reponse["comparatif"]
    assert comparatif["schema_version"] == 1
    assert comparatif["modeles"]
    assert FICHIER.name == "comparatif-modeles.json"


def test_rend_le_contenu_du_fichier(tmp_path: Path) -> None:
    donnees = {"schema_version": 1, "modeles": [{"id": "<modele-factice-1>"}]}
    pont = PontModeles(_ecrire(tmp_path / "c.json", donnees))
    assert pont.comparatif_modeles() == {"ok": True, "comparatif": donnees}


def test_fichier_absent_refus_clair(tmp_path: Path) -> None:
    reponse = PontModeles(tmp_path / "absent.json").comparatif_modeles()
    assert reponse["ok"] is False
    assert reponse["erreur"]["code"] == "comparatif-indisponible"
    assert "absent" in reponse["erreur"]["message"]


@pytest.mark.parametrize(
    "contenu",
    ["pas du json", "[]", '{"schema_version": 2, "modeles": []}', '{"schema_version": 1}'],
)
def test_fichier_illisible_ou_schema_inattendu(tmp_path: Path, contenu: str) -> None:
    chemin = tmp_path / "c.json"
    chemin.write_text(contenu, encoding="utf-8")
    reponse = PontModeles(chemin).comparatif_modeles()
    assert reponse["ok"] is False
    assert reponse["erreur"]["code"] == "comparatif-indisponible"


def test_methode_inconnue() -> None:
    with pytest.raises(NonImplementee):
        PontModeles().appeler("ecrire")
