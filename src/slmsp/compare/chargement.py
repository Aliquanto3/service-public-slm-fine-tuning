"""Chargement des runs lus par le Comparatif (story 11.1, AD-20, AD-25).

Le Comparatif est une fonction pure des artefacts de `runs/` : rien ici n'appelle de modèle ni
de réseau. Les runs sont lus par les schémas d'AD-25 (`RunManifest`, `Scores`,
`ResultatBench`) ; `couts.json` et `metriques.jsonl` d'un Run d'entraînement le sont par des
modèles tolérants (clés inconnues ignorées), car leur producteur (story 10.3 / 10.4) évolue.

Sélection (AD-20) : un run dont le statut n'est pas `complet` est exclu et signalé ; pour une
génération donnée, la notation retenue est la plus récente parmi les complètes ; deux versions
du jeu ne sont jamais mélangées (`JeuMelange`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from slmsp.core.artefacts import Run, ouvrir_run
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.schemas.bench import ResultatBench
from slmsp.core.schemas.scores import Scores

TYPE_NOTATION = "eval-notation"
TYPE_BENCH = "bench"
TYPE_TRAIN = "train"
TYPE_EXPORT = "export"
PHASE_COMPOSITION = "composition"
"""Phase d'un run `eval-notation` composé (`slmsp.evaluation.composition.PHASE`)."""

QUANTIFICATIONS = ("f16", "q4_k_m")
STATUT_RELU_LLM = "relu-llm"


class JeuMelange(SlmspError):
    """Les notations retenues portent plusieurs versions du jeu d'évaluation."""


class JeuDeveloppement(SlmspError):
    """Une notation retenue porte un jeu de développement (`relu-llm`), jamais une mesure finale."""


class _Tolerant(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Couts(_Tolerant):
    """Coûts d'un Run (`couts.json`, story 10.3) ; une valeur absente reste `None`."""

    duree_s: float | None = None
    debit_tokens_par_s: float | None = None
    vram_max_octets: int | None = None
    energie_wh: float | None = None


class EvaluationIntermediaire(_Tolerant):
    """Évaluation intermédiaire d'un Run, pour les deux vues de FR-34."""

    tokens_vus: int
    duree_s: float
    scores: dict[str, float | None]


@dataclass(frozen=True)
class Exclu:
    """Run écarté du rapport, avec la raison."""

    type: str
    run_id: str
    motif: str


@dataclass(frozen=True)
class Entrainement:
    run_id: str
    methode: str | None
    couts: Couts | None
    evaluations: tuple[EvaluationIntermediaire, ...]


@dataclass(frozen=True)
class Donnees:
    """Tout ce que lit le rendu du Comparatif."""

    campagne: str
    jeu_version: str | None
    baselines: dict[tuple[str, str | None], Scores] = field(default_factory=dict)
    """(modèle `base:<slug>`, quantification) → Scores. Chaque configuration est un tout : par
    Tâche, la notation complète la plus récente l'emporte (pas de maximum entre notations)."""
    jeu_statuts: tuple[str, ...] = ()
    """Statuts du jeu (`jeu_statut`) des notations retenues."""
    entrainements: dict[str, Entrainement] = field(default_factory=dict)
    scores_ft: dict[str, dict[str, Scores]] = field(default_factory=dict)
    """run d'entraînement → quantification → Scores."""
    bench_base: dict[tuple[str, str], dict[str, ResultatBench]] = field(default_factory=dict)
    """(benchmark, variante) → modèle `base:` → résultat."""
    bench_ft: dict[str, dict[tuple[str, str], ResultatBench]] = field(default_factory=dict)
    exclus: tuple[Exclu, ...] = ()


def _cle_recence(run: Run) -> tuple[Any, str]:
    return (run.manifeste.cree_le, run.run_id)


def _runs(racine: Path, type_run: str) -> tuple[list[Run], list[Exclu]]:
    dossier = racine / "runs" / type_run
    runs: list[Run] = []
    exclus: list[Exclu] = []
    if not dossier.is_dir():
        return runs, exclus
    for enfant in sorted(dossier.iterdir()):
        if not enfant.is_dir():
            continue
        try:
            runs.append(ouvrir_run(enfant.name, racine=racine))
        except ManifesteInvalide:
            exclus.append(Exclu(type_run, enfant.name, "manifeste illisible ou invalide"))
    return runs, exclus


def _complets(runs: list[Run], exclus: list[Exclu]) -> list[Run]:
    gardes: list[Run] = []
    for run in runs:
        statut = run.statut_courant()
        if statut == "complet":
            gardes.append(run)
        else:
            exclus.append(Exclu(run.type, run.run_id, f"statut {statut}"))
    return gardes


def _lire_json(chemin: Path) -> Any:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _couts(dossier: Path) -> Couts | None:
    segments: list[Couts] = []
    for chemin in sorted(dossier.glob("couts*.json")):
        brut = _lire_json(chemin)
        try:
            segments.append(Couts.model_validate(brut))
        except ValidationError:
            continue
    if not segments:
        return None
    if len(segments) == 1:
        return segments[0]

    # Reprise sur checkpoint : durées et énergies s'additionnent, le débit n'est pas combinable.
    def somme(valeurs: list[float | None]) -> float | None:
        return None if any(v is None for v in valeurs) else float(sum(v for v in valeurs if v))

    vram = [s.vram_max_octets for s in segments if s.vram_max_octets is not None]
    return Couts(
        duree_s=somme([s.duree_s for s in segments]),
        energie_wh=somme([s.energie_wh for s in segments]),
        vram_max_octets=max(vram) if vram else None,
    )


def _evaluations(dossier: Path) -> tuple[EvaluationIntermediaire, ...]:
    chemin = dossier / "metriques.jsonl"
    try:
        lignes = chemin.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    trouvees: list[EvaluationIntermediaire] = []
    for ligne in lignes:
        try:
            brut = json.loads(ligne)
        except ValueError:
            continue
        if not isinstance(brut, dict) or brut.get("evenement") != "evaluation":
            continue
        try:
            trouvees.append(EvaluationIntermediaire.model_validate(brut))
        except ValidationError:
            continue
    return tuple(sorted(trouvees, key=lambda e: (e.tokens_vus, e.duree_s)))


def _methode(config: dict[str, Any]) -> str | None:
    """Méthode d'un Run `train` : `toml.methode` de la configuration résolue (story 10.4)."""
    toml = config.get("toml")
    methode = toml.get("methode") if isinstance(toml, dict) else config.get("methode")
    return str(methode) if methode is not None else None


def _resolution(entrainements: dict[str, Run], exports: list[Run]) -> dict[str, str]:
    """Identifiant X d'un `ft:<X>` → run d'entraînement (X est le run ou son export)."""
    table = {run_id: run_id for run_id in entrainements}
    for export in exports:
        parents = [p for p in export.manifeste.parents if p in entrainements]
        if parents:
            table[export.run_id] = parents[0]
    return table


def _train_de(modele_ref: str | None, table: dict[str, str]) -> str | None:
    if modele_ref is None or not modele_ref.startswith("ft:"):
        return None
    return table.get(modele_ref.removeprefix("ft:"))


def _notations(racine: Path, exclus: list[Exclu]) -> list[tuple[Run, Scores]]:
    runs, ecartes = _runs(racine, TYPE_NOTATION)
    exclus.extend(ecartes)
    par_generation: dict[str, tuple[Run, Scores]] = {}
    for run in _complets(runs, exclus):
        if run.manifeste.config.get("phase") == PHASE_COMPOSITION:
            # Run composé (story 15.1) : même run_generation que sa source par défaut, il
            # remplacerait la vraie notation du modèle ; il ne se lit qu'avec `eval comparer`.
            exclus.append(Exclu(run.type, run.run_id, "run composé (eval composer)"))
            continue
        try:
            scores = Scores.model_validate(_lire_json(run.dossier / "scores.json"))
        except ValidationError:
            exclus.append(Exclu(run.type, run.run_id, "scores.json absent ou invalide"))
            continue
        actuel = par_generation.get(scores.run_generation)
        if actuel is None or _cle_recence(run) > _cle_recence(actuel[0]):
            par_generation[scores.run_generation] = (run, scores)
    return sorted(par_generation.values(), key=lambda paire: _cle_recence(paire[0]))


def _plus_recent[T](courant: tuple[Run, T] | None, run: Run, valeur: T) -> tuple[Run, T]:
    if courant is None or _cle_recence(run) > _cle_recence(courant[0]):
        return (run, valeur)
    return courant


def _est_dev(scores: Scores) -> bool:
    return scores.jeu_statut == STATUT_RELU_LLM


def charger(racine: Path, campagne: str, *, jeu: str | None = None) -> Donnees:
    """Charge les artefacts de `racine/runs` utiles à la `campagne`.

    Lève `JeuMelange` si les notations retenues portent plusieurs versions du jeu et que
    `jeu` ne tranche pas.
    """
    racine = Path(racine)
    exclus: list[Exclu] = []

    runs_train, ecartes = _runs(racine, TYPE_TRAIN)
    exclus.extend(ecartes)
    de_la_campagne = [r for r in runs_train if r.manifeste.config.get("campagne") == campagne]
    complets = {r.run_id: r for r in _complets(de_la_campagne, exclus)}
    runs_export, ecartes = _runs(racine, TYPE_EXPORT)
    exclus.extend(ecartes)
    exports = [e for e in runs_export if any(p in complets for p in e.manifeste.parents)]
    exports = _complets(exports, exclus)
    table = _resolution(complets, exports)

    entrainements = {
        run_id: Entrainement(
            run_id=run_id,
            methode=_methode(run.manifeste.config),
            couts=_couts(run.dossier),
            evaluations=_evaluations(run.dossier),
        )
        for run_id, run in sorted(complets.items())
    }

    # Notations : base:* et ft:* de la campagne ; une version du jeu à la fois.
    pertinentes: list[tuple[Run, Scores]] = []
    for run, scores in _notations(racine, exclus):
        ref = scores.modele_ref
        if ref is None:
            exclus.append(Exclu(run.type, run.run_id, "modèle non renseigné"))
        elif ref.startswith("base:") or _train_de(ref, table) is not None:
            pertinentes.append((run, scores))
    versions = sorted({s.jeu_version for _, s in pertinentes})
    if jeu is not None:
        pertinentes = [(r, s) for r, s in pertinentes if s.jeu_version == jeu]
        versions = [jeu] if pertinentes else []
    en_dev = sorted({f"{s.jeu_version} ({s.jeu_statut})" for _, s in pertinentes if _est_dev(s)})
    if en_dev:
        raise JeuDeveloppement(
            f"notation(s) d'un jeu de développement, non admise(s) au Comparatif : "
            f"{', '.join(en_dev)} ; le Comparatif ne porte que des mesures finales (v1.1 relu)"
        )
    if len(versions) > 1:
        raise JeuMelange(
            "plusieurs versions du jeu parmi les notations : "
            f"{', '.join(versions)} ; choisir avec --jeu"
        )

    baselines: dict[tuple[str, str | None], Scores] = {}
    scores_ft: dict[str, dict[str, Scores]] = {}
    for run, scores in pertinentes:  # ordre chronologique : la plus récente l'emporte
        ref = scores.modele_ref or ""
        if ref.startswith("base:"):
            cle = (ref, scores.quantification)
            baselines[cle] = _fusionner_baseline(baselines.get(cle), scores)
        else:
            train = _train_de(ref, table)
            if train is None:
                continue
            if scores.quantification in QUANTIFICATIONS:
                scores_ft.setdefault(train, {})[str(scores.quantification)] = scores
            else:
                exclus.append(Exclu(run.type, run.run_id, "quantification non renseignée"))

    bench_base, bench_ft = _benchmarks(racine, table, exclus)
    return Donnees(
        campagne=campagne,
        jeu_version=versions[0] if versions else None,
        baselines=dict(sorted(baselines.items(), key=lambda kv: (kv[0][0], kv[0][1] or ""))),
        jeu_statuts=tuple(sorted({s.jeu_statut for _, s in pertinentes})),
        entrainements=entrainements,
        scores_ft=scores_ft,
        bench_base=bench_base,
        bench_ft=bench_ft,
        exclus=tuple(sorted(exclus, key=lambda e: (e.type, e.run_id))),
    )


def _fusionner_baseline(ancien: Scores | None, nouveau: Scores) -> Scores:
    """Même Baseline, même quantification : par Tâche, le score mesuré le plus récent.

    `nouveau` est postérieur à `ancien` ; aucun maximum entre notations (pas de sélection du
    meilleur essai), une Tâche non mesurée dans `nouveau` garde la mesure antérieure.
    """
    if ancien is None:
        return nouveau
    taches = dict(ancien.taches)
    for nom, tache in nouveau.taches.items():
        if tache.score is not None or nom not in taches:
            taches[nom] = tache
    return nouveau.model_copy(update={"taches": taches})


def _benchmarks(
    racine: Path, table: dict[str, str], exclus: list[Exclu]
) -> tuple[
    dict[tuple[str, str], dict[str, ResultatBench]],
    dict[str, dict[tuple[str, str], ResultatBench]],
]:
    runs, ecartes = _runs(racine, TYPE_BENCH)
    exclus.extend(ecartes)
    retenus: dict[tuple[str, str, str], tuple[Run, ResultatBench]] = {}
    for run in _complets(runs, exclus):
        for chemin in sorted(run.dossier.glob("*--*.json")):
            try:
                resultat = ResultatBench.model_validate(_lire_json(chemin))
            except ValidationError:
                exclus.append(Exclu(run.type, run.run_id, f"{chemin.name} absent ou invalide"))
                continue
            ref = resultat.modele_ref
            if not (ref.startswith("base:") or _train_de(ref, table) is not None):
                continue
            if resultat.statut != "ok":
                exclus.append(Exclu(run.type, run.run_id, f"{chemin.name} : {resultat.statut}"))
                continue
            cle = (ref, resultat.benchmark, resultat.variante)
            retenus[cle] = _plus_recent(retenus.get(cle), run, resultat)
    base: dict[tuple[str, str], dict[str, ResultatBench]] = {}
    ft: dict[str, dict[tuple[str, str], ResultatBench]] = {}
    for (ref, benchmark, variante), (_, resultat) in sorted(retenus.items()):
        if ref.startswith("base:"):
            base.setdefault((benchmark, variante), {})[ref] = resultat
        else:
            train = _train_de(ref, table)
            if train is not None:
                ft.setdefault(train, {})[(benchmark, variante)] = resultat
    return base, ft
