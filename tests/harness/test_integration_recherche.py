"""Test réel de la Recherche de données : Qwen3 4B (CPU, `json-generique`), BGE-M3 et l'Index.

Marqué `lent` et `integration`, exclu par défaut. Items RD-001 et RD-002 du jeu gelé
`v1.0`, Bac à sable MCP sur leurs cassettes gelées (lecture seule), `ModeFixe("connecte")`.
Lancer : `SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/harness/test_integration_recherche.py -m integration -s`.

Prérequis (binaires, modèles, Index) : ceux de `test_integration_question.py`, réutilisés.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton, ResultatOutil
from slmsp.core.items import lire_jeu, resoudre_cassettes
from slmsp.evaluation import controles
from slmsp.harness.config import charger_config_harnais
from slmsp.harness.modes import ModeFixe
from slmsp.harness.service import AssistantService
from slmsp.index.lecture import ouvrir_index
from slmsp.inference import serveur
from slmsp.inference.serveur import ServeurLlama
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.cassettes import lire_cassette


def _module_question() -> ModuleType:
    nom = "harness_integration_question"
    if nom not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            nom, Path(__file__).with_name("test_integration_question.py")
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[nom] = module
        spec.loader.exec_module(module)
    return sys.modules[nom]


question = _module_question()
ITEMS = ("RD-001", "RD-002")
PROTOCOLE = "json-generique"


def appel_conforme(appel: AppelOutil, attendu: Any) -> bool:
    """Règles de production (`exact`, `contient_un_de`, `mot_entier_un_de`, `optionnel`)."""
    return controles.appel_conforme(attendu, appel.nom, appel.arguments)


@pytest.mark.lent
@pytest.mark.integration
def test_reel_recherche_de_donnees() -> None:
    racine = question.prerequis(question.QWEN)
    jeu = lire_jeu("v1.0")
    items = {item.id: item for item in jeu.items if item.id in ITEMS}
    assert sorted(items) == list(ITEMS)
    config = charger_config_harnais()
    modele = question.config_generation(question.QWEN).model_copy(
        update={"protocole_outils": PROTOCOLE, "contexte": 8192}
    )
    options: dict[str, Any] = {"temperature": 0, "seed": 42, "max_tokens": 400}
    traces: dict[str, list[Any]] = {}
    cassettes: dict[str, list[Path]] = {}
    with (
        ServeurLlama(modele, "cpu", slug=question.QWEN) as generation,
        ServeurLlama(serveur.charger_config_modele("bge-m3"), "cpu", slug="bge-m3") as embedding,
        ouvrir_index(racine) as index,
    ):
        llm = generation.client()
        assert llm.protocole_outils == PROTOCOLE
        for code in ITEMS:
            item = items[code]
            cassettes[code] = resoudre_cassettes(jeu, item)
            service = AssistantService(
                llm,
                embedding.embedder(),
                index,
                BacASable(cassettes[code]),
                ModeFixe("connecte"),
                config,
            )
            traces[code] = list(
                service.repondre("RD", [{"role": "user", "content": item.entree}], options=options)
            )

    for code in ITEMS:
        evenements = traces[code]
        item = items[code]
        print(f"\n=== {code} ===")
        for evenement in evenements:
            if isinstance(evenement, Jeton):
                continue
            if isinstance(evenement, ResultatOutil):
                print(f"ResultatOutil {evenement.id} {evenement.nom} erreur={evenement.erreur}")
            else:
                print(repr(evenement))
        texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
        print(f"Réponse : {texte}")

    fautes: list[str] = []
    for code in ITEMS:
        evenements = traces[code]
        item = items[code]
        fin = evenements[-1]
        if not isinstance(fin, Fin):
            fautes.append(f"{code} : le flux se termine par {fin!r}")
            continue
        if fin.urls_inventees:
            fautes.append(f"{code} : URL inventées {fin.urls_inventees}")
        appels = [e for e in evenements if isinstance(e, AppelOutil)]
        resultats = {e.id: e for e in evenements if isinstance(e, ResultatOutil)}
        refus = [e for e in evenements if isinstance(e, AppelNonConforme)]
        if not appels:
            fautes.append(f"{code} : aucun appel valide ({len(refus)} appel(s) refusé(s))")
            continue
        if not all(a.id in resultats for a in appels):
            fautes.append(f"{code} : appel sans résultat")
        reponses = [
            i.response["result"]
            for chemin in cassettes[code]
            for i in lire_cassette(chemin).interactions
            if i.request.get("method") == "tools/call" and i.response is not None
        ]
        executes = [resultats[a.id] for a in appels if a.id in resultats]
        if not any(not r.erreur and r.resultat in reponses for r in executes):
            fautes.append(f"{code} : aucun ResultatOutil exécuté égal à la cassette")
        (attendu,) = [a for a in item.appels_attendus if not (a.regles and a.regles.optionnel)]
        if not any(appel_conforme(a, attendu) for a in appels):
            fautes.append(
                f"{code} : aucun appel ne respecte la règle de {attendu.outil} "
                f"({[(a.nom, a.arguments) for a in appels]})"
            )
    assert not fautes, "\n".join(fautes)
