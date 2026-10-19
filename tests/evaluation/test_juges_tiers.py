"""Phase juges tiers (story S3) : run `eval-juges-tiers` sur un run `eval-notation` factice.

Jeu v1.0 copié (`depot_eval`), juges factices, aucun réseau.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from evaluation_factices import ITEMS_8, JugeFactice, verdict_factice

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import CodeSortie, SlmspError
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.verdict import Verdict
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation import juges_tiers
from slmsp.evaluation.notation import Juges, noter
from slmsp.evaluation.scores import Jugement
from slmsp.judge.cache import CacheVerdicts
from slmsp.judge.claude import EstimationCout


def _generation(depot: Path) -> str:
    run = nouveau_run(
        phase_generation.TYPE_RUN,
        "granite-4.0-1b",
        {"phase": "generation", "items": list(ITEMS_8)},
        racine=depot,
        modele_ref="base:granite-4.0-1b",
        quantification="q4_k_m",
        variante_llamacpp="cpu",
        jeu_version="v1.0",
    )
    jeu = lire_jeu("v1.0", depot)
    for identifiant in ITEMS_8:
        run.ajouter_jsonl(
            phase_generation.FICHIER_GENERATIONS,
            Generation(
                item_id=identifiant,
                tache=jeu.item(identifiant).code,
                statut="ok",
                sortie_canonique={"texte": f"<sortie-factice-{identifiant}>"},
                trace=[{"type": "fin", "raison": "terminee"}],
                duree_ms=1,
            ),
        )
    run.terminer("complet")
    return run.run_id


class JugeTiersFactice(JugeFactice):
    def __init__(self, cache: Any, cout_estime: float = 0.5, **options: Any) -> None:
        super().__init__(cache, "tiers", fabriquer=lambda i: verdict_factice(i, min), **options)
        self.cout_estime = cout_estime

    def estimer(self, demandes: Sequence[Any]) -> EstimationCout:
        return EstimationCout(
            len(demandes), 0, len(demandes), self.cout_estime, 2 * self.cout_estime
        )

    def description(self) -> dict[str, Any]:
        return {"nom": "factice", "modele": "factice"}


@pytest.fixture
def notation(depot_eval: Path, tmp_path: Path) -> SimpleNamespace:
    cache = CacheVerdicts(tmp_path / "verdicts.sqlite")
    juges = Juges(
        principal=JugeFactice(cache, "principal"),
        second=JugeFactice(cache, "second"),
        cache=cache,
        description={"principal": {"modele": "factice"}},
    )
    rapport = noter(_generation(depot_eval), juges=juges, racine=depot_eval)
    return SimpleNamespace(run=rapport.run, cache=cache, depot=depot_eval)


def _empreintes(dossier: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dossier.iterdir())}


def test_nominal_run_et_accords(notation: SimpleNamespace) -> None:
    avant = _empreintes(notation.run.dossier)
    juge = JugeTiersFactice(notation.cache)
    rapport = juges_tiers.noter_tiers(
        notation.run.run_id, juge=juge, nom_juge="factice", racine=notation.depot
    )

    assert rapport.statut == "complet"
    assert sorted(juge.recus) == ["CR-001", "CT-001", "LC-001", "RE-001"]
    assert _empreintes(notation.run.dossier) == avant  # run source jamais réécrit
    dossier = rapport.run.dossier
    assert dossier.parent.name == juges_tiers.TYPE_RUN
    assert {p.name for p in dossier.iterdir()} >= {
        "run.json",
        "etat.jsonl",
        "verdicts.jsonl",
        "accords.json",
    }
    assert rapport.run.manifeste.parents == [notation.run.run_id]
    lignes = rapport.run.lire_jsonl(juges_tiers.FICHIER_VERDICTS)
    assert {ligne["juge"] for ligne in lignes} == {"tiers"}
    paire = rapport.accords["taches"]["LC"]["criteres"]["fidelite"]["tiers/principal"]
    assert paire["effectif"] == 1 and paire["statut"] == juges_tiers.NON_CONCLUANT
    assert paire["kappa"] is None and paire["accord_brut"] == 0.0


def test_plafond_estime_refuse_sans_run(notation: SimpleNamespace) -> None:
    juge = JugeTiersFactice(notation.cache, cout_estime=5.0)
    with pytest.raises(SlmspError, match="plafond"):
        juges_tiers.noter_tiers(
            notation.run.run_id,
            juge=juge,
            nom_juge="factice",
            racine=notation.depot,
            plafond_estime_eur=1.0,
        )
    assert juge.recus == []
    assert not (notation.depot / "runs" / juges_tiers.TYPE_RUN).exists()


def test_budget_partiel(notation: SimpleNamespace) -> None:
    juge = JugeTiersFactice(notation.cache, budget_apres=1)
    rapport = juges_tiers.noter_tiers(
        notation.run.run_id, juge=juge, nom_juge="factice", racine=notation.depot
    )
    assert rapport.statut == "partiel-budget"


def test_taches_filtrees_et_invalides(notation: SimpleNamespace) -> None:
    juge = JugeTiersFactice(notation.cache)
    juges_tiers.noter_tiers(
        notation.run.run_id, juge=juge, nom_juge="factice", taches=["CT"], racine=notation.depot
    )
    assert juge.recus == ["CT-001"]
    with pytest.raises(ValueError):
        juges_tiers.noter_tiers(
            notation.run.run_id, juge=juge, nom_juge="factice", taches=["CO"], racine=notation.depot
        )


# --- Accords sur un mini-run ---------------------------------------------------------------------


def _jugement(item_id: str, note: int) -> Jugement:
    verdict = Verdict(
        id=item_id,
        criteres={"fidelite": {"note": note, "justification": "<j>"}},
        inventions=[],
        confiance="haute",
    )
    return Jugement("juge", verdict)


def test_calculer_accords_kappa_et_desaccords() -> None:
    items = [SimpleNamespace(id=f"RE-{i:03d}", code="RE") for i in range(12)]
    principal = {it.id: _jugement(it.id, i % 2) for i, it in enumerate(items)}
    tiers = {it.id: _jugement(it.id, i % 2) for i, it in enumerate(items)}
    tiers["RE-000"] = _jugement("RE-000", 1)  # un désaccord
    second = {it.id: _jugement(it.id, 0) for it in items[:3]}
    accords = juges_tiers.calculer_accords(
        items, {"tiers": tiers, "principal": principal, "second": second}, ["RE"]
    )
    paires = accords["taches"]["RE"]["criteres"]["fidelite"]
    assert paires["tiers/principal"]["effectif"] == 12
    assert paires["tiers/principal"]["statut"] == juges_tiers.CONCLUANT
    assert paires["tiers/principal"]["accord_brut"] == pytest.approx(11 / 12, abs=1e-4)
    assert paires["tiers/principal"]["kappa"] is not None
    assert paires["tiers/second"]["statut"] == juges_tiers.NON_CONCLUANT
    assert paires["tiers/second"]["kappa"] is None
    # RE-000 : tiers 1, principal 0, second 0 ; RE-001 : 1, 1, 0 ; RE-002 : 0, 0, 0
    assert [d["item_id"] for d in accords["desaccords"]] == ["RE-000", "RE-001"]
    assert "tiers/principal" in juges_tiers.tableau_accords(accords)


# --- CLI ----------------------------------------------------------------------------------------


def test_cli_verifier_sans_cle(monkeypatch: pytest.MonkeyPatch, capsys: Any) -> None:
    from slmsp.fournisseurs import client

    def faux(config: Any) -> Any:
        return client.Verification(config.nom, config.nom_secret, False, ())

    monkeypatch.setattr(client, "verifier", faux)
    assert main(["eval", "juges-tiers", "--verifier"]) == int(CodeSortie.SUCCES)
    sortie = capsys.readouterr().out
    assert "openrouter : clé OPENROUTER_API_KEY absente" in sortie


def test_cli_usage(capsys: Any) -> None:
    assert main(["eval", "juges-tiers"]) == int(CodeSortie.USAGE)
    assert main(["eval", "juges-tiers", "--verifier", "--juge", "x"]) == int(CodeSortie.USAGE)


def test_cli_juge_inconnu(capsys: Any) -> None:
    code = main(["eval", "juges-tiers", "--depuis", "x", "--juge", "inconnu"])
    assert code == int(CodeSortie.USAGE)
    assert "juge tiers inconnu" in capsys.readouterr().err
