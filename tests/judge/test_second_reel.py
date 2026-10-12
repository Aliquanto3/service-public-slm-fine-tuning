"""Test réel unique du second juge Mistral (payant, exclu par défaut).

Lancement (orchestrateur seulement, une fois, après la revue) :
`$env:SLMSP_ENV_FILE='<dépôt principal>\\.env'; uv run pytest tests/judge/test_second_reel.py
-m "reseau and payant" -s`.

Registre de budget réel (celui de la machine : `SLMSP_VAR_DIR` capturé à l'import du module,
avant que la fixture autouse ne le redirige, sinon `%LOCALAPPDATA%\\slmsp\\var`), sous-poste
`mistral.juge` ; cache des verdicts et journaux Mistral dans `tmp_path`. Items du calibrage :
`Q-001` avec sa `reponse_reference` comme sortie, et le premier compte rendu (CR) avec une
sortie factice, pour que l'API réelle valide le `response_format` `json_schema` strict des
deux formes de schéma (notes en `enum` entier, tableau de `ref` et présence 0 / 0,5 / 1).

Plafond dur de 0,20 € : avant **chaque appel** (second essai d'une sortie non conforme
compris), coût réel cumulé + coût pire cas de l'appel doit rester sous le plafond ; sinon la
réservation est refusée (`BudgetEpuise`) et le second juge s'arrête.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import cout_pire_cas
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import BudgetEpuise
from slmsp.core.items import lire_items
from slmsp.judge.cache import CacheVerdicts
from slmsp.judge.config import charger_juges
from slmsp.judge.grille import charger_grille


def _var_reel() -> Path:
    valeur = os.environ.get("SLMSP_VAR_DIR", "").strip()
    if valeur:
        return Path(valeur)
    local = os.environ.get("LOCALAPPDATA", "").strip()
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "slmsp" / "var"


VAR_REEL = _var_reel()
"""Capturé à l'import : la fixture autouse `_var_dir_temporaire` redirige ensuite la variable."""

PLAFOND_EUR = 0.20


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
        print(f"  appel : pire cas {pire:.4f} €, dépensé avant {self.depense_eur:.4f} €")
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
def test_second_juge_reel_q_et_cr(tmp_path: Path) -> None:
    pytest.importorskip("anthropic")
    pytest.importorskip("mistralai")
    from slmsp.judge.claude import DemandeJugement
    from slmsp.judge.second import JugeMistral
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral
    from slmsp.mistral.journal import journal_pour

    juges = charger_juges()
    config_mistral = charger_mistral()
    registre = RegistrePlafonne(charger_budgets(), charger_tarifs(), VAR_REEL / "budget.sqlite")
    client = ClientMistral(
        config_mistral, registre, fabriquer_sdk(config_mistral), dossier_journaux=tmp_path
    )
    cache = CacheVerdicts(tmp_path / "verdicts.sqlite")
    juge = JugeMistral(juges.second, client, cache, charger_grille(juges.principal.chemin_grille()))
    chemin = racine_projet() / "eval" / "calibrage" / "echantillon-calibrage.jsonl"
    items = lire_items(chemin, strict=False)
    q = next(item for item in items if item.id == "Q-001")
    cr = next(item for item in items if item.tache == "Compte rendu")
    demandes = [
        DemandeJugement(
            q,
            {
                "texte": q.reponse_reference,
                "appels_outils": [],
                "sources": [
                    {"titre": "Source attendue", "url": url} for url in q.sources_attendues or []
                ],
            },
        ),
        DemandeJugement(
            cr, {"texte": "<compte-rendu-factice>", "appels_outils": [], "sources": []}
        ),
    ]

    journal = journal_pour("juge-second", config_mistral, tmp_path)
    resultats = []
    for demande in demandes:  # item par item : le plafond est contrôlé avant chaque appel
        rapport = juge.juger([demande], {demande.item.id})
        (resultat,) = rapport.resultats
        appels = [a for a in cache.appels() if a["cle"] == resultat.cle]
        print(
            f"{resultat.item_id} : statut {resultat.statut} ({resultat.motif}), "
            f"{len(appels)} appel(s), tokens {resultat.tokens}, coût {resultat.cout_eur:.4f} €"
        )
        if resultat.verdict is not None:
            print(resultat.verdict.model_dump_json(indent=2))
        resultats.append(resultat)
        if rapport.budget_epuise:
            break
    lignes = journal.appels()
    for ligne in lignes:
        print(f"  journal : {ligne.statut}, modèle résolu {ligne.modele_resolu}")
    print(f"Coût total : {registre.depense_eur:.4f} €")
    assert registre.depense_eur <= PLAFOND_EUR
    assert [r.statut for r in resultats] == ["juge", "juge"]
    assert lignes, "aucune ligne au journal du juge"
    for ligne in lignes:
        assert ligne.statut == "ok"
        assert ligne.modele_resolu in config_mistral.modeles_autorises
    assert not (tmp_path / config_mistral.fichier_journal_donnees).exists()
