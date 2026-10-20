"""Runs synthétiques du Comparatif : chiffres factices, aucun résultat réel."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.canonique import json_canonique
from slmsp.core.schemas.bench import ConfigurationExecution, ResultatBench
from slmsp.core.schemas.run import Environnement, RunManifest
from slmsp.core.schemas.scores import Effectifs, KappaTache, Scores, ScoreTache, StatutsTache

RACINE_REPO = Path(__file__).resolve().parents[2]
ENV = Environnement(os="test", machine="test", cpu="test", python="3.12")


def run_id(horodatage: str, slug: str, hexa: str = "abcd") -> str:
    return f"{horodatage}-{slug}-{hexa}"


def ecrire_run(
    racine: Path,
    type_run: str,
    identifiant: str,
    *,
    statut: str = "complet",
    config: dict[str, Any] | None = None,
    modele_ref: str | None = None,
    parents: tuple[str, ...] = (),
) -> Path:
    j, h = identifiant[:8], identifiant[9:15]
    cree_le = datetime(
        int(j[:4]), int(j[4:6]), int(j[6:]), int(h[:2]), int(h[2:4]), int(h[4:]), tzinfo=UTC
    )
    manifeste = RunManifest(
        type=type_run,
        run_id=identifiant,
        cree_le=cree_le,
        parents=list(parents),
        modele_ref=modele_ref,
        config=config or {},
        environnement=ENV,
    )
    dossier = racine / "runs" / type_run / identifiant
    dossier.mkdir(parents=True)
    (dossier / "run.json").write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
    etat = {"schema_version": 1, "horodatage": cree_le.isoformat(), "statut": statut, "pid": 1}
    (dossier / "etat.jsonl").write_text(json.dumps(etat) + "\n", encoding="utf-8")
    return dossier


def tache(nom: str, score: float | None, *, relu: bool = False) -> ScoreTache:
    return ScoreTache(
        tache=nom,  # type: ignore[arg-type]
        score=score,
        effectifs=Effectifs(notes=1, juges=1, invalides=0, non_juges=0, en_erreur=0, second_juge=0),
        statuts=StatutsTache(jeu_statut="relu", verdicts_relus=relu),
        kappa=KappaTache(),
        cout_juge_eur=0.0,
    )


def ecrire_notation(
    racine: Path,
    identifiant: str,
    modele_ref: str,
    scores: dict[str, float | None],
    *,
    quantification: str | None = None,
    jeu: str = "v1.1",
    generation: str | None = None,
    statut: str = "complet",
    jeu_statut: str = "relu",
) -> None:
    dossier = ecrire_run(racine, "eval-notation", identifiant, statut=statut, modele_ref=modele_ref)
    contenu = Scores(
        run_generation=generation or identifiant,
        modele_ref=modele_ref,  # type: ignore[arg-type]
        quantification=quantification,  # type: ignore[arg-type]
        jeu_version=jeu,
        jeu_statut=jeu_statut,
        version_texte=1,
        taches={t: tache(t, s) for t, s in scores.items()},
        cout_juge_total_eur=0.0,
    )
    (dossier / "scores.json").write_bytes(json_canonique(contenu.model_dump(mode="json")) + b"\n")


def ecrire_bench(
    racine: Path,
    identifiant: str,
    modele_ref: str,
    benchmark: str,
    variante: str,
    valeur: float,
    *,
    statut: str = "complet",
) -> None:
    dossier = ecrire_run(racine, "bench", identifiant, statut=statut, modele_ref=modele_ref)
    contenu = ResultatBench(
        run_id=identifiant,
        benchmark=benchmark,
        moteur="factice",
        tache="factice",
        modele_ref=modele_ref,  # type: ignore[arg-type]
        variante=variante,  # type: ignore[arg-type]
        cible="gguf",
        statut="ok",
        scores={"acc": valeur},
        configuration=ConfigurationExecution(fewshot=0),
        duree_s=1.0,
    )
    nom = f"{benchmark}--{variante}.json"
    (dossier / nom).write_bytes(json_canonique(contenu.model_dump(mode="json")) + b"\n")


def ecrire_entrainement(
    racine: Path,
    identifiant: str,
    methode: str,
    *,
    campagne: str = "camp-test",
    statut: str = "complet",
    couts: dict[str, Any] | None = None,
    evaluations: list[dict[str, Any]] | None = None,
) -> None:
    dossier = ecrire_run(
        racine,
        "train",
        identifiant,
        statut=statut,
        config={"campagne": campagne, "toml": {"methode": methode}, "plan": {"methode": methode}},
        modele_ref="base:granite",
    )
    if couts is not None:
        (dossier / "couts.json").write_text(json.dumps(couts), encoding="utf-8")
    lignes = [{"evenement": "evaluation", **e} for e in evaluations or []]
    (dossier / "metriques.jsonl").write_text(
        "".join(json.dumps(ligne) + "\n" for ligne in lignes), encoding="utf-8"
    )


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    cible = tmp_path / "config" / "comparatif.toml"
    shutil.copy(RACINE_REPO / "config" / "comparatif.toml", cible)
    with cible.open("a", encoding="utf-8") as flux:  # Benchmark factice `arc` des fixtures
        flux.write('\n[benchmarks.arc]\nmetrique = "acc"\n')
    return tmp_path


M1 = run_id("20261001-100000", "m1-qlora")
M4 = run_id("20261001-110000", "m4-orpo", "beef")
EXPORT_M1 = run_id("20261001-120000", "export-m1")


@pytest.fixture
def campagne_complete(racine: Path) -> Path:
    """Baselines, M1 (QLoRA, exporté) et M4 (ORPO) de la campagne `camp-test`."""
    ecrire_notation(
        racine, run_id("20261001-090000", "base-granite"), "base:granite",
        {"Q": 40.0, "RD": 50.0, "CR": 30.0, "LC": 45.0, "NR": 60.0},
        quantification="q4_k_m",
    )  # fmt: skip
    ecrire_notation(
        racine, run_id("20261001-090100", "base-autre", "1111"), "base:autre",
        {"Q": 35.0, "RD": 55.0, "CR": 28.0, "LC": 44.0, "NR": 62.0},
        quantification="q4_k_m",
    )  # fmt: skip
    ecrire_entrainement(
        racine, M1, "qlora",
        couts={"duree_s": 3600.0, "vram_max_octets": 4 * 1024**3, "energie_wh": 250.5,
               "debit_tokens_par_s": 1200.0},
        evaluations=[
            {"tokens_vus": 1000, "duree_s": 600.0, "scores": {"Q": 45.0, "RD": 52.0}},
            {"tokens_vus": 2000, "duree_s": 1200.0, "scores": {"Q": 50.0, "RD": 60.0}},
        ],
    )  # fmt: skip
    ecrire_entrainement(
        racine, M4, "orpo",
        couts={"duree_s": 1800.0, "vram_max_octets": 5 * 1024**3, "energie_wh": 140.0},
        evaluations=[{"tokens_vus": 1500, "duree_s": 900.0, "scores": {"Q": 48.0, "RD": 58.0}}],
    )  # fmt: skip
    ecrire_run(racine, "export", EXPORT_M1, parents=(M1,))
    ref = f"ft:{EXPORT_M1}"
    ecrire_notation(
        racine, run_id("20261001-130000", "ft-f16", "2222"), ref,
        {"Q": 52.0, "RD": 68.0, "CR": 33.0, "LC": 46.0, "NR": 60.0}, quantification="f16",
    )  # fmt: skip
    ecrire_notation(
        racine, run_id("20261001-130100", "ft-q4", "3333"), ref,
        {"Q": 51.0, "RD": 67.0, "CR": 32.0, "LC": 45.0, "NR": 59.0}, quantification="q4_k_m",
    )  # fmt: skip
    ecrire_bench(
        racine, run_id("20261001-140000", "bench-b", "4444"), "base:granite", "arc", "avant", 50.0
    )
    ecrire_bench(
        racine, run_id("20261001-140100", "bench-b", "4445"), "base:granite", "arc", "apres", 49.0
    )
    ecrire_bench(racine, run_id("20261001-140200", "bench-ft", "4446"), ref, "arc", "avant", 49.0)
    ecrire_bench(racine, run_id("20261001-140300", "bench-ft", "4447"), ref, "arc", "apres", 48.5)
    return racine
