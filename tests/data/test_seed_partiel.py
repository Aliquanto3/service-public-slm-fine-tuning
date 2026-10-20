"""Story O6b : seed partiel (`data seed --taches LC --completer-depuis SEED`).

Seules les Tâches demandées sont tirées ; les amorces des autres sont recopiées à l'identique
du seed parent, pour que `generate` garde leurs `session_id` (réponses Mistral réutilisées) et
qu'un run `generate` du seed parent complète un run du nouveau seed. Textes factices (D1).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.erreurs import ManifesteInvalide

from .test_seed import Monde, config_petite


@pytest.fixture
def monde(tmp_path: Path) -> Monde:
    return Monde(tmp_path)


def test_seed_partiel_tire_lc_et_recopie_les_autres(monde: Monde) -> None:
    jeux = monde.jeux_standard(nb_sp=6)
    parent = monde.executer(jeux)
    partiel = monde.executer(
        jeux, config=config_petite(LC=3), taches=["LC"], completer_depuis=parent.run_id
    )
    assert partiel.statut == "complet"
    avant = monde.amorces(parent.run_id)
    apres = monde.amorces(partiel.run_id)
    autres = [a for a in avant if a["tache"] != "LC"]
    assert [a for a in apres if a["tache"] != "LC"] == autres and autres
    assert len([a for a in apres if a["tache"] == "LC"]) == 3
    assert monde.comptes(partiel.run_id)["recopiees"] == {
        "seed": parent.run_id,
        "amorces": len(autres),
    }
    manifeste = ouvrir_run(partiel.run_id, racine=monde.racine).manifeste
    assert manifeste.config["taches"] == ["LC"]
    assert manifeste.config["completer_depuis"] == parent.run_id
    assert manifeste.parents == [parent.run_id]


def test_seed_partiel_exige_un_parent_complet(monde: Monde) -> None:
    with pytest.raises(ValueError):
        monde.executer(taches=["LC"])
    with pytest.raises(ManifesteInvalide):
        monde.executer(taches=["LC"], completer_depuis="20261017-111645-seed-0000")
