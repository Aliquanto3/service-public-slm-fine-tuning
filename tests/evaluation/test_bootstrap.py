"""Bootstrap apparié (story E1b) : deux runs de notation factices, aucun réseau.

Jeu v1.0 copié (`depot_eval`), juges factices : les verdicts sont des chaînes factices.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import ITEMS_8, JugeFactice, verdict_factice

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import CodeSortie
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.evaluation import bootstrap
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation.notation import Juges, noter
from slmsp.judge.cache import CacheVerdicts

TACHES = ("Q", "CR")


def _noter(depot: Path, tmp_path: Path, nom: str, choix: Any) -> str:
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
                sortie_canonique={"texte": f"<réponse-factice-{nom}-{identifiant}>"},
                trace=[{"type": "fin", "raison": "terminee"}],
                duree_ms=1,
            ),
        )
    run.terminer("complet")
    cache = CacheVerdicts(tmp_path / f"verdicts-{nom}.sqlite")
    juges = Juges(
        principal=JugeFactice(cache, "principal", fabriquer=lambda i: verdict_factice(i, choix)),
        second=JugeFactice(cache, "second"),
        cache=cache,
        description={"principal": {"modele": "factice"}},
    )
    return noter(run.run_id, juges=juges, racine=depot).run.run_id


@pytest.fixture
def notations(depot_eval: Path, tmp_path: Path) -> tuple[Path, str, str]:
    a = _noter(depot_eval, tmp_path, "a", min)
    b = _noter(depot_eval, tmp_path, "b", max)
    return depot_eval, a, b


def test_recalcul_identique_et_ecart_nul_avec_soi_meme(
    notations: tuple[Path, str, str],
) -> None:
    depot, a, _ = notations
    seuils = bootstrap.cfg.charger_evaluation().seuils
    charge = bootstrap.charger_run(a, depot, seuils)
    bootstrap.verifier_recalcul(charge)  # ne lève pas

    resultat = bootstrap.comparer_runs([a, a], racine=depot, tirages=50, graine=3)
    for ligne in resultat.comparaisons[0].lignes:
        assert ligne.ecart == 0
        assert ligne.ic is not None and ligne.ic.bas == ligne.ic.haut == 0
        assert ligne.p_positif == 0


def test_ic_contient_ecart_observe_et_graine_reproductible(
    notations: tuple[Path, str, str],
) -> None:
    depot, a, b = notations
    premier = bootstrap.comparer_runs([a, b], racine=depot, tirages=200, graine=5)
    second = bootstrap.comparer_runs([a, b], racine=depot, tirages=200, graine=5)
    assert premier == second
    lignes = {ligne.nom: ligne for ligne in premier.comparaisons[0].lignes}
    assert bootstrap.QUALITE in lignes
    for ligne in lignes.values():
        if ligne.ecart is None:
            continue
        assert ligne.ic is not None and ligne.ic.bas <= ligne.ecart <= ligne.ic.haut
        assert ligne.p_positif is not None and 0 <= ligne.p_positif <= 1
    assert premier.bruit_qualite[a] is not None


def test_recalcul_different_de_scores_json_refuse(notations: tuple[Path, str, str]) -> None:
    depot, a, _ = notations
    seuils = bootstrap.cfg.charger_evaluation().seuils
    charge = bootstrap.charger_run(a, depot, seuils)
    charge.principal.clear()  # verdicts absents : le recalcul s'écarte de scores.json
    with pytest.raises(bootstrap.ErreurRecalcul, match="scores.json"):
        bootstrap.verifier_recalcul(charge)


def test_cli_sortie_markdown(notations: tuple[Path, str, str], tmp_path: Path, capsys: Any) -> None:
    depot, a, b = notations
    sortie = tmp_path / "comparaison.md"
    code = main(
        [
            "eval",
            "comparer",
            "--runs",
            a,
            b,
            "--bootstrap",
            "20",
            "--sortie",
            str(sortie),
            "--racine",
            str(depot),
        ]
    )
    assert code == int(CodeSortie.SUCCES)
    texte = sortie.read_text(encoding="utf-8")
    assert "| Tâche |" in texte and "Bruit items" in texte
    assert texte.strip() in capsys.readouterr().out


class _Item:
    def __init__(self, identifiant: str, code: str) -> None:
        self.id, self.code = identifiant, code


class _RunFactice(bootstrap.RunCharge):
    """Run sans fichiers : score d'une Tâche = part d'items dont l'id est pair, ou None."""

    def __init__(
        self,
        nom: str,
        items: list[_Item],
        sans_score: tuple[str, ...] = (),
        *,
        jeu: str = "v1",
        juge: str = "claude",
        statut: str = "relu",
        version_harnais: int = 1,
    ) -> None:
        self.version_harnais = version_harnais
        self.run_id, self.items, self._sans = nom, items, sans_score  # type: ignore[assignment]
        attributs = {"taches": {}, "jeu_version": jeu, "juge_principal": juge, "jeu_statut": statut}
        self.scores = type("S", (), attributs)()  # type: ignore[assignment]

    def score(self, tache: str, items: Any, *, avec_second: bool) -> float | None:
        if tache in self._sans or not items:
            return None
        return 100 * sum(int(i.id[-1]) % 2 == 0 for i in items) / len(items)


def _items(codes: dict[str, int]) -> list[_Item]:
    return [_Item(f"{c}-{n:03d}", c) for c, k in codes.items() for n in range(k)]


def test_items_differents_et_tache_absente_avertis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 6, "CR": 4}))
    b = _RunFactice("b", _items({"Q": 4}))
    resultat = bootstrap.comparer([a, b], tirages=30, graine=1)
    assert any("CR" in w and "retirée" in w for w in resultat.avertissements)
    assert any("Q" in w and "4 items communs" in w for w in resultat.avertissements)
    assert "Avertissement" in bootstrap.tableau_markdown(resultat)


def test_qualite_sur_taches_definies_partout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 4, "CR": 4}))
    b = _RunFactice("b", _items({"Q": 4, "CR": 4}), sans_score=("CR",))
    resultat = bootstrap.comparer([a, b], tirages=30, graine=1)
    assert resultat.tirages_partiels == 30
    assert any("30/30" in w for w in resultat.avertissements)
    qualite = next(x for x in resultat.comparaisons[0].lignes if x.nom == bootstrap.QUALITE)
    q = next(x for x in resultat.comparaisons[0].lignes if x.nom == "Q")
    assert qualite.score_a == q.score_a  # Qualité d'A sur Q seul, comme B
    assert qualite.ecart == q.ecart
    assert qualite.n_valides == 30


@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({"jeu": "dev1"}, "jeux dev1, v1"),
        ({"juge": "glm"}, "juges principaux claude, glm"),
        ({"version_harnais": 2}, "versions de harnais 1, 2"),
    ],
)
def test_jeux_ou_juges_differents_refuses(
    monkeypatch: pytest.MonkeyPatch, options: dict[str, str], motif: str
) -> None:
    """Revue O4a : un écart de jeu ou de juge principal est refusé, sauf option explicite."""
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 4}))
    b = _RunFactice("b", _items({"Q": 4}), **options)
    with pytest.raises(ValueError, match=motif):
        bootstrap.comparer([a, b], tirages=5, graine=1)
    resultat = bootstrap.comparer([a, b], tirages=5, graine=1, autoriser_jeux_differents=True)
    assert any("différents" in w for w in resultat.avertissements)


def test_jeu_relu_llm_signale(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    runs = [
        _RunFactice(n, _items({"Q": 4}), jeu="dev1", juge="glm", statut="relu-llm")
        for n in ("a", "b")
    ]
    resultat = bootstrap.comparer(runs, tirages=5, graine=1)
    assert any("relu-llm" in w for w in resultat.avertissements)


def test_items_exclus_retires_avant_tirage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Revue 17.5a : un item non noté d'un côté sort de l'ensemble commun des deux runs."""
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 6}))
    b = _RunFactice("b", _items({"Q": 6}))
    resultat = bootstrap.comparer([a, b], tirages=20, graine=1, exclus={"Q-000", "Q-002"})
    assert resultat.items_communs == {"Q": 4}
    assert any("4 items communs" in w for w in resultat.avertissements)
    assert resultat.observes[0]["Q"] == 25.0  # Q-001, Q-003, Q-004, Q-005 : un seul pair
