"""`eval composer` (story 15.1) : runs de notation factices, aucun réseau ni juge réel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import ITEMS_8, JugeFactice, verdict_factice

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import CodeSortie
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation import bootstrap, composition
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation.notation import Juges, noter
from slmsp.judge.cache import CacheVerdicts


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
    return (
        depot_eval,
        _noter(depot_eval, tmp_path, "a", min),
        _noter(depot_eval, tmp_path, "b", max),
    )


def _score(run_id: str, depot: Path) -> Scores:
    dossier = ouvrir_run(run_id, racine=depot).dossier
    return Scores.model_validate_json((dossier / "scores.json").read_bytes())


def _empreinte(run_id: str, depot: Path) -> dict[str, str]:
    dossier = ouvrir_run(run_id, racine=depot).dossier
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dossier.iterdir()}


def _modifier_manifeste(run_id: str, depot: Path, edition: Any) -> None:
    chemin = ouvrir_run(run_id, racine=depot).dossier / "run.json"
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    edition(donnees)
    chemin.write_text(json.dumps(donnees), encoding="utf-8")


def test_composition_route_par_tache_et_lecture_par_comparer(
    notations: tuple[Path, str, str],
) -> None:
    depot, a, b = notations
    avant = {r: _empreinte(r, depot) for r in (a, b)}
    run = composition.composer({"CR": b}, a, marque="deja-consulte", racine=depot)
    sa, sb, sc = (_score(r, depot) for r in (a, b, run.run_id))
    assert sc.taches["CR"] == sb.taches["CR"]
    assert sc.taches["Q"] == sa.taches["Q"]
    assert run.statut_courant() == "complet"
    assert run.manifeste.config["route"] == {"CR": b}
    assert run.manifeste.config["marque"] == "deja-consulte"
    assert run.manifeste.parents == sorted({a, b})
    assert {r: _empreinte(r, depot) for r in (a, b)} == avant  # sources intactes
    resultat = bootstrap.comparer_runs([a, run.run_id], racine=depot, tirages=30, graine=2)
    lignes = {ligne.nom: ligne for ligne in resultat.comparaisons[0].lignes}
    assert lignes["Q"].ecart == 0  # Q vient de a
    assert lignes["CR"].ecart == pytest.approx(sb.taches["CR"].score - sa.taches["CR"].score)


def test_sans_route_le_run_compose_egale_le_defaut(notations: tuple[Path, str, str]) -> None:
    depot, a, _ = notations
    run = composition.composer({}, a, racine=depot)
    assert _score(run.run_id, depot).taches == _score(a, depot).taches
    assert run.manifeste.config["marque"] is None


@pytest.mark.parametrize(
    ("edition", "motif"),
    [
        (lambda d: d["config"].update(items=d["config"]["items"][:-1]), "items"),
        (lambda d: d.update(jeu_version="v9.9"), "jeu_version"),
        (lambda d: d["entrees"].update(grille="0" * 64), "grille_sha256"),
        (
            lambda d: d["config"]["juges"]["principal"].update(modele="<autre-juge>"),
            "juge_principal",
        ),
        (
            lambda d: d["config"]["juges"]["principal"].update(effort="<autre-effort>"),
            "juge_principal",
        ),
        (
            lambda d: d["config"]["juges"]["principal"].update(mode_appel="<autre-mode>"),
            "juge_principal",
        ),
        (lambda d: d["config"].pop("items"), "items ou SHA de grille absent"),
        (lambda d: d["entrees"].pop("grille"), "items ou SHA de grille absent"),
        (lambda d: d["config"].pop("juges"), "juge principal non renseigné"),
    ],
)
def test_refus_si_sources_differentes(
    notations: tuple[Path, str, str], edition: Any, motif: str
) -> None:
    depot, a, b = notations
    _modifier_manifeste(b, depot, edition)
    avant = sorted((depot / "runs" / "eval-notation").iterdir())
    with pytest.raises(composition.ErreurComposition, match=motif):
        composition.composer({"CR": b}, a, racine=depot)
    assert sorted((depot / "runs" / "eval-notation").iterdir()) == avant  # aucun run écrit


def test_refus_prompts_de_tache_differents(notations: tuple[Path, str, str]) -> None:
    depot, a, b = notations
    generation = ouvrir_run(b, racine=depot).manifeste.config["run_generation"]
    _modifier_manifeste(generation, depot, lambda d: d["entrees"].update(taches="1" * 64))
    with pytest.raises(composition.ErreurComposition, match="taches_sha256"):
        composition.composer({"CR": b}, a, racine=depot)


def test_refus_statut_non_ok_et_source_composee(notations: tuple[Path, str, str]) -> None:
    depot, a, b = notations
    for statut in ("partiel-budget", "interrompu"):
        ouvrir_run(b, racine=depot).terminer(statut)
        with pytest.raises(composition.ErreurComposition, match="statut"):
            composition.composer({"CR": b}, a, racine=depot)
    compose = composition.composer({}, a, racine=depot)
    with pytest.raises(composition.ErreurComposition, match="déjà un run composé"):
        composition.composer({}, compose.run_id, racine=depot)


def test_source_partiel_erreur_admise_et_consignee(notations: tuple[Path, str, str]) -> None:
    depot, a, b = notations
    ouvrir_run(a, racine=depot).terminer("partiel-erreur")
    run = composition.composer({"CR": b}, a, racine=depot)
    assert run.statut_courant() == "partiel-erreur"  # le moins bon des sources
    assert run.manifeste.config["sources_partielles"] == [a]
    resultat = bootstrap.comparer_runs([a, run.run_id], racine=depot, tirages=30, graine=2)
    assert {ligne.nom for ligne in resultat.comparaisons[0].lignes} >= {"CR", "Q"}
    complet = composition.composer({"CR": b}, b, racine=depot)
    assert complet.statut_courant() == "complet"
    assert complet.manifeste.config["sources_partielles"] == []


def test_comparatif_et_juges_tiers_ignorent_le_run_compose(
    notations: tuple[Path, str, str],
) -> None:
    from slmsp.compare import chargement
    from slmsp.core.erreurs import SlmspError
    from slmsp.evaluation import juges_tiers

    depot, a, b = notations
    compose = composition.composer({"CR": b}, a, racine=depot)
    exclus: list[Any] = []
    retenus = {run.run_id for run, _ in chargement._notations(depot, exclus)}
    assert a in retenus and b in retenus  # la notation du défaut n'est pas remplacée
    assert compose.run_id not in retenus
    assert any(e.run_id == compose.run_id and "composé" in e.motif for e in exclus)
    with pytest.raises(SlmspError, match="composé"):
        juges_tiers.preparer(compose.run_id, ["CR"], depot)


def test_refus_tache_inconnue_ou_marque_inconnue(notations: tuple[Path, str, str]) -> None:
    depot, a, b = notations
    with pytest.raises(composition.ErreurComposition, match="inconnue"):
        composition.composer({"ZZ": b}, a, racine=depot)
    with pytest.raises(composition.ErreurComposition, match="marque"):
        composition.composer({}, a, marque="<autre>", racine=depot)


def test_cli_composer(notations: tuple[Path, str, str], capsys: Any) -> None:
    depot, a, b = notations
    code = main(["eval", "composer", "--route", f"CR={b}", "--defaut", a, "--racine", str(depot)])
    assert code == int(CodeSortie.SUCCES)
    assert "Run composé" in capsys.readouterr().out
    code = main(["eval", "composer", "--route", "CR", "--defaut", a, "--racine", str(depot)])
    assert code == int(CodeSortie.USAGE)
    capsys.readouterr()
    ouvrir_run(b, racine=depot).terminer("interrompu")
    code = main(["eval", "composer", "--route", f"CR={b}", "--defaut", a, "--racine", str(depot)])
    assert code == int(CodeSortie.USAGE)
    assert "statut" in capsys.readouterr().err


def test_refus_si_la_presence_du_second_juge_differe(notations: tuple[Path, str, str]) -> None:
    depot, a, b = notations
    _modifier_manifeste(b, depot, lambda d: d["config"]["juges"].update(second={"modele": "x"}))
    with pytest.raises(composition.ErreurComposition, match="second_juge"):
        composition.composer({"CR": b}, a, racine=depot)
