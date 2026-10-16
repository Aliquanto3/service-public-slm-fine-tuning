"""Export des Retours (story 12.3) : faux lecteur, aucun réseau, écriture sur confirmation."""

from __future__ import annotations

import json
import socket
from datetime import date

import pytest

from slmsp.app.anonymisation import MASQUE
from slmsp.app.export_retours import apercu, construire_export, ecrire, nom_fichier
from slmsp.app.stockage import Stockage
from slmsp.core.erreurs import SlmspError

EMAIL = "zz.qq@exemple-factice.invalid"


class FauxStockage:
    def lister_retours(self):
        return [
            {
                "id": 7,
                "cree_le": "2026-10-16T10:00:00Z",
                "tache": "CR",
                "question": f"<question-factice> {EMAIL}",
                "reponse": "<réponse-factice-1>",
                "sources": [
                    {"titre": f"<titre-factice> {EMAIL}", "url": "https://exemple.invalid"}
                ],
                "pouce": "bas",
                "commentaire": None,
            }
        ]


@pytest.fixture(autouse=True)
def _sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("aucune requête sortante attendue")

    monkeypatch.setattr(socket, "socket", interdit)


def test_export_anonymise_et_nomme():
    export = construire_export(FauxStockage(), jour=date(2026, 10, 16), prenoms=frozenset())
    assert export.nom_fichier == nom_fichier(date(2026, 10, 16))
    assert export.nom_fichier == "retours-assistant-2026-10-16.json"
    assert EMAIL not in export.contenu and MASQUE in export.contenu
    assert export.comptes["email"] == 2
    retour = json.loads(apercu(export))["retours"][0]
    assert "id" not in retour and retour["pouce"] == "bas"


def test_aucune_ecriture_sans_confirmation(tmp_path):
    export = construire_export(FauxStockage(), prenoms=frozenset())
    with pytest.raises(SlmspError):
        ecrire(export, tmp_path / "sortie", confirme=False)
    assert not (tmp_path / "sortie").exists()
    chemin = ecrire(export, tmp_path / "sortie", confirme=True)
    assert chemin.read_text(encoding="utf-8") == apercu(export)


def test_stockage_reel_branche(tmp_path):
    stockage = Stockage(tmp_path / "assistant.sqlite")
    stockage.enregistrer_retour(
        tache="CR", question=f"<q> {EMAIL}", reponse="<r>", sources=[], pouce="haut"
    )
    export = construire_export(stockage, prenoms=frozenset())
    assert EMAIL not in export.contenu
