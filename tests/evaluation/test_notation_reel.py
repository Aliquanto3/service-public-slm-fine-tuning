"""Test réel unique de la phase notation (payant, exclu par défaut, story 5.6).

Lancement (orchestrateur seulement, une fois, après la revue) :
`$env:SLMSP_ENV_FILE='<dépôt principal>\\.env'; $env:SLMSP_DEPOT_PRINCIPAL='<dépôt principal>';
uv run pytest tests/evaluation/test_notation_reel.py -m "reseau and payant" -s`.

Note le run de génération réel (`SLMSP_RUN_GENERATION`, défaut
`20261012-155024-granite-4.0-1b-0cdc`) du dépôt principal, qui reçoit le run
`eval-notation`. Juges réels (Claude en `mode_appel="direct"`, Mistral), registre de budget,
cache de verdicts et journaux Mistral réels de la machine (`SLMSP_VAR_DIR` capturé à
l'import, avant la fixture autouse, sinon `%LOCALAPPDATA%\\slmsp\\var`).

Plafond dur de 0,50 € pour les deux API ensemble : avant chaque appel, dépense du test +
coût pire cas de l'appel doit rester sous le plafond, sinon la réservation est refusée
(`BudgetEpuise`) et les items restants sont « non jugés ».
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import cout_pire_cas
from slmsp.core.erreurs import BudgetEpuise


def _var_reel() -> Path:
    valeur = os.environ.get("SLMSP_VAR_DIR", "").strip()
    if valeur:
        return Path(valeur)
    local = os.environ.get("LOCALAPPDATA", "").strip()
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "slmsp" / "var"


VAR_REEL = _var_reel()
"""Capturé à l'import : la fixture autouse `_var_dir_temporaire` redirige ensuite la variable."""

PLAFOND_EUR = 0.50
RUN_GENERATION = "20261012-155024-granite-4.0-1b-0cdc"


class RegistrePlafonne(RegistreBudget):
    """Registre réel qui refuse toute réservation dépassant le plafond du test."""

    depense_eur = 0.0

    def reserver(
        self,
        poste: str,
        sous_poste: str | None,
        modele: str,
        mode: str,
        tokens_entree_estimes: int,
        max_tokens: int,
        **options: Any,
    ) -> int:
        pire = cout_pire_cas(
            self.tarifs,
            modele,
            mode,
            tokens_entree_estimes,
            max_tokens,
            self.config.majoration_entree,
            avec_cache=options.get("avec_cache", False),
        )
        if self.depense_eur + pire > PLAFOND_EUR:
            raise BudgetEpuise(
                f"plafond du test ({PLAFOND_EUR} €) : dépensé {self.depense_eur:.4f} €, "
                f"pire cas de l'appel {pire:.4f} €"
            )
        print(f"  appel {modele} : pire cas {pire:.4f} €, dépensé avant {self.depense_eur:.4f} €")
        return super().reserver(
            poste, sous_poste, modele, mode, tokens_entree_estimes, max_tokens, **options
        )

    def regulariser(self, reservation_id: int, usage: Any) -> float:
        cout = super().regulariser(reservation_id, usage)
        self.depense_eur += cout
        return cout

    def compter_pire_cas(self, reservation_id: int) -> float:
        cout = super().compter_pire_cas(reservation_id)
        self.depense_eur += cout
        return cout


@pytest.mark.reseau
@pytest.mark.payant
def test_notation_reelle_run_granite() -> None:
    pytest.importorskip("anthropic")
    pytest.importorskip("mistralai")
    from slmsp.cli.eval import tableau_scores
    from slmsp.evaluation.notation import Juges, noter
    from slmsp.judge.cache import CacheVerdicts
    from slmsp.judge.claude import JugeClaude, fabriquer_client
    from slmsp.judge.config import charger_juges
    from slmsp.judge.grille import charger_grille
    from slmsp.judge.second import JugeMistral
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral

    valeur = os.environ.get("SLMSP_DEPOT_PRINCIPAL", "").strip()
    if not valeur:
        pytest.skip("SLMSP_DEPOT_PRINCIPAL non défini")
    racine = Path(valeur)
    run_id = os.environ.get("SLMSP_RUN_GENERATION", "").strip() or RUN_GENERATION
    if not (racine / "runs" / "eval-generation" / run_id).is_dir():
        pytest.skip(f"run de génération {run_id} absent de {racine}")

    config = charger_juges()
    principal = config.principal.model_copy(update={"mode_appel": "direct"})
    grille = charger_grille(principal.chemin_grille(racine))
    registre = RegistrePlafonne(charger_budgets(), charger_tarifs(), VAR_REEL / "budget.sqlite")
    cache = CacheVerdicts(VAR_REEL / "verdicts.sqlite")
    config_mistral = charger_mistral()
    client_mistral = ClientMistral(
        config_mistral, registre, fabriquer_sdk(config_mistral), dossier_journaux=VAR_REEL
    )
    juges = Juges(
        principal=JugeClaude(principal, registre, cache, fabriquer_client(principal), grille),
        second=JugeMistral(config.second, client_mistral, cache, grille),
        cache=cache,
        description={
            "principal": {"modele": principal.modele, "effort": principal.effort},
            "second": {"modele": config.second.modele, "effort": config.second.effort_cle},
        },
    )

    rapport = noter(run_id, juges=juges, racine=racine, rapporter=print)
    print(f"Run de notation : {rapport.run.dossier} ({rapport.statut})")
    print(tableau_scores(rapport.scores))
    print(
        f"Coût de cette session : {rapport.cout_session_eur:.4f} € "
        f"(registre : {registre.depense_eur:.4f} €) ; coût cumulé du Juge "
        f"{rapport.scores.cout_juge_total_eur:.4f} €"
    )
    assert registre.depense_eur <= PLAFOND_EUR
    assert len(rapport.scores.taches) == 8
    assert all(not t.statuts.verdicts_relus for t in rapport.scores.taches.values())
