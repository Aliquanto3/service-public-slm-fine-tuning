"""Bout en bout du banc (story 5.6) : génération `FakeLlm` puis notation, sans réseau.

Calibrage (16 items, 8 Tâches) copié dans `tmp_path`, Harnais factice déterministe, juges
factices sur le cache de verdicts réel : `scores.json` couvre les 8 Tâches, et une relance
à cache plein ne fait aucun appel payant et rend un `scores.json` identique à l'octet.
"""

from __future__ import annotations

from pathlib import Path

from evaluation_factices import Fabrique, JugeFactice

from slmsp.core.items import CODES
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation.generation import lancer_generation
from slmsp.evaluation.notation import FICHIER_SCORES, Juges, noter
from slmsp.judge.cache import CacheVerdicts


def test_calibrage_generation_puis_notation(depot_eval: Path, modeles: Path, tmp_path: Path):
    generation = lancer_generation(
        "base:granite-4.0-1b", "q4_k_m", "calibrage", racine=depot_eval, fabrique=Fabrique()
    )
    assert generation.statut == "complet" and generation.ok == 16

    cache = CacheVerdicts(tmp_path / "verdicts.sqlite")
    premiers = Juges(JugeFactice(cache), JugeFactice(cache, "second"), cache)
    un = noter(generation.run.run_id, juges=premiers, racine=depot_eval)
    assert un.statut == "complet"
    scores = Scores.model_validate_json((un.run.dossier / FICHIER_SCORES).read_bytes())
    assert sorted(scores.taches) == sorted(CODES)  # JSON canonique : clés triées
    assert scores.jeu_version == "calibrage" and scores.jeu_statut == "calibrage"
    for code in ("Q", "CR", "LC", "RE", "CT", "NR"):
        assert scores.taches[code].effectifs.juges == 2, code
    assert premiers.principal.appels_payants == 12  # 6 Tâches jugées × 2, RD et CO jamais
    assert premiers.second.appels_payants > 0

    relance = Juges(JugeFactice(cache), JugeFactice(cache, "second"), cache)
    deux = noter(generation.run.run_id, juges=relance, racine=depot_eval)
    assert relance.principal.appels_payants == 0 and relance.second.appels_payants == 0
    assert (un.run.dossier / FICHIER_SCORES).read_bytes() == (
        deux.run.dossier / FICHIER_SCORES
    ).read_bytes()
