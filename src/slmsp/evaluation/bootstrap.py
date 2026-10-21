"""Bootstrap apparié des scores de notation : quel écart de qualité est du bruit d'items ?

`comparer(runs, …)` recharge, pour chaque run `eval-notation`, les entrées de
`scores.score_tache` (verdicts, contrôles, générations du run parent, items du jeu), sans
appel au juge ni écriture. Le recalcul sans rééchantillonnage doit redonner exactement les
scores de `scores.json`, sinon `ErreurRecalcul`.

À chaque tirage, les `item_id` de chaque Tâche sont rééchantillonnés avec remise, les mêmes
pour tous les runs (apparié) ; chaque score de Tâche est recalculé par `score_tache`, et la
Qualité est la moyenne des scores de Tâche disponibles (comme les tableaux de scores). Le
décodage d'évaluation étant glouton, ce bruit est celui de l'échantillonnage des items.
"""

from __future__ import annotations

import random
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.items import CODES, ItemBase, lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Scores
from slmsp.core.schemas.verdict import Verdict
from slmsp.evaluation import config as cfg
from slmsp.evaluation import notation
from slmsp.evaluation.config import Seuils
from slmsp.evaluation.scores import Jugement, score_tache

QUALITE: Final = "Qualité"
NIVEAU_IC: Final = 0.95
TOLERANCE_RECALCUL: Final = 1e-9


class ErreurRecalcul(SlmspError):
    """Le recalcul d'un score ne redonne pas `scores.json`."""


@dataclass
class RunCharge:
    """Entrées de calcul d'un run de notation, rechargées en lecture seule."""

    run_id: str
    items: list[ItemBase]
    generations: dict[str, Generation]
    controles: dict[str, dict[str, Any]]
    principal: dict[str, Jugement]
    second: dict[str, Jugement]
    seuils: Seuils
    jeu_statut: str
    scores: Scores

    def par_tache(self) -> dict[str, list[ItemBase]]:
        return {
            code: [i for i in self.items if i.code == code]
            for code in CODES
            if any(i.code == code for i in self.items)
        }

    def score(self, tache: str, items: Sequence[ItemBase], *, avec_second: bool) -> float | None:
        return score_tache(
            tache,
            items,
            generations=self.generations,
            controles=self.controles,
            principal=self.principal,
            second=self.second if avec_second else {},
            seuils=self.seuils,
            jeu_statut=self.jeu_statut,
            manifeste_sha256=None,
        ).score


def _jugements(run: Any) -> tuple[dict[str, Jugement], dict[str, Jugement]]:
    par_juge: dict[str, dict[str, Jugement]] = {
        notation.JUGE_PRINCIPAL: {},
        notation.JUGE_SECOND: {},
    }
    for rang, ligne in enumerate(run.lire_jsonl(notation.FICHIER_VERDICTS), 1):
        juge = ligne.get("juge")
        if juge not in par_juge:
            continue
        try:
            verdict = (
                None if ligne.get("verdict") is None else Verdict.model_validate(ligne["verdict"])
            )
        except ValidationError:
            raise ManifesteInvalide(
                f"run {run.run_id} : ligne {rang} de {notation.FICHIER_VERDICTS} invalide"
            ) from None
        par_juge[juge][ligne["item_id"]] = Jugement(
            statut=ligne["statut"], verdict=verdict, cle=ligne.get("cle"), motif=ligne.get("motif")
        )
    return par_juge[notation.JUGE_PRINCIPAL], par_juge[notation.JUGE_SECOND]


def _generations_du_run(run: Any, generation: str, base: Path) -> dict[str, Generation]:
    """Générations du run ; un run composé les prend, par Tâche, dans le run de sa source."""
    par_tache = run.manifeste.config.get("generations_par_tache")
    if not isinstance(par_tache, dict):
        return notation._generations(ouvrir_run(generation, racine=base))
    generations: dict[str, Generation] = {}
    for tache, run_generation in par_tache.items():
        source = notation._generations(ouvrir_run(run_generation, racine=base))
        generations.update({i: g for i, g in source.items() if g.tache == tache})
    return generations


def charger_run(run_id: str, base: Path, seuils: Seuils) -> RunCharge:
    """Recharge un run `eval-notation` (verdicts, contrôles, générations, items, scores)."""
    run = ouvrir_run(run_id, racine=base)
    if run.type != notation.TYPE_RUN:
        raise ManifesteInvalide(f"run {run_id} de type {run.type!r}, pas {notation.TYPE_RUN!r}")
    generation = run.manifeste.config.get("run_generation")
    jeu_version = run.manifeste.jeu_version
    if not isinstance(generation, str) or jeu_version is None:
        raise ManifesteInvalide(f"run {run_id} : run.json sans run_generation ou jeu_version")
    generations = _generations_du_run(run, generation, base)
    jeu = lire_jeu(jeu_version, base)
    ids = run.manifeste.config.get("items")
    retenus = set(ids) if isinstance(ids, list) else set(generations)
    controles = {
        ligne["item_id"]: ligne["controle"] for ligne in run.lire_jsonl(notation.FICHIER_CONTROLES)
    }
    try:
        scores = Scores.model_validate_json((run.dossier / notation.FICHIER_SCORES).read_bytes())
    except (OSError, ValidationError):
        raise ManifesteInvalide(f"run {run_id} : {notation.FICHIER_SCORES} illisible") from None
    principal, second = _jugements(run)
    return RunCharge(
        run_id=run_id,
        items=[item for item in jeu.items if item.id in retenus],
        generations=generations,
        controles=controles,
        principal=principal,
        second=second,
        seuils=seuils,
        jeu_statut=scores.jeu_statut,
        scores=scores,
    )


def _moyenne(valeurs: Sequence[float]) -> float | None:
    return sum(valeurs) / len(valeurs) if valeurs else None


def verifier_recalcul(run: RunCharge) -> None:
    """Le recalcul sans rééchantillonnage doit redonner `scores.json` (`ErreurRecalcul`)."""
    for code, items in run.par_tache().items():
        attendu = run.scores.taches[code].score if code in run.scores.taches else None
        obtenu = run.score(code, items, avec_second=True)
        obtenu = None if obtenu is None else round(obtenu, 4)
        if obtenu is None or attendu is None:
            ecart = obtenu != attendu
        else:
            ecart = abs(obtenu - attendu) > TOLERANCE_RECALCUL
        if ecart:
            raise ErreurRecalcul(
                f"run {run.run_id}, tâche {code} : recalcul {obtenu} ≠ scores.json {attendu}"
            )


def _quantile(valeurs: Sequence[float], q: float) -> float:
    ordre = sorted(valeurs)
    position = q * (len(ordre) - 1)
    bas = int(position)
    haut = min(bas + 1, len(ordre) - 1)
    return ordre[bas] + (ordre[haut] - ordre[bas]) * (position - bas)


@dataclass(frozen=True)
class Intervalle:
    bas: float
    haut: float

    @property
    def demi_largeur(self) -> float:
        return (self.haut - self.bas) / 2


def _ic(valeurs: Sequence[float]) -> Intervalle:
    marge = (1 - NIVEAU_IC) / 2
    return Intervalle(_quantile(valeurs, marge), _quantile(valeurs, 1 - marge))


@dataclass(frozen=True)
class LigneComparaison:
    """Une ligne du tableau : scores observés, écart B − A, IC et probabilité de B > A."""

    nom: str
    score_a: float | None
    score_b: float | None
    ecart: float | None
    ic: Intervalle | None
    p_positif: float | None
    n_valides: int = 0


@dataclass(frozen=True)
class Comparaison:
    reference: str
    autre: str
    lignes: list[LigneComparaison]


@dataclass(frozen=True)
class Resultat:
    runs: list[str]
    tirages: int
    graine: int
    comparaisons: list[Comparaison]
    bruit_qualite: dict[str, float | None]
    items_communs: dict[str, int]
    avertissements: list[str] = field(default_factory=list)
    tirages_partiels: int = 0
    observes: list[dict[str, float]] = field(default_factory=list)
    """Scores observés (sans rééchantillonnage) de chaque run, sur les items communs."""


def items_non_notes(run: RunCharge) -> set[str]:
    """Items exclus du score du run : génération en échec, ou verdict principal absent,
    `non-juge` ou invalide là où la Tâche en exige un (ni CO, ni RD, notés par contrôles)."""
    exclus: set[str] = set()
    for item in run.items:
        generation = run.generations.get(item.id)
        if generation is None or generation.statut != "ok":
            exclus.add(item.id)
        elif item.code not in ("CO", "RD"):
            jugement = run.principal.get(item.id)
            if jugement is None or not jugement.valide:
                exclus.add(item.id)
    return exclus


def _scores_taches(run: RunCharge, ids: Mapping[str, list[str]]) -> dict[str, float]:
    """Scores par Tâche sur les `item_id` donnés (doublons admis) ; None écartés."""
    par_id = {item.id: item for item in run.items}
    scores: dict[str, float] = {}
    for code, liste in ids.items():
        valeur = run.score(code, [par_id[i] for i in liste], avec_second=False)
        if valeur is not None:
            scores[code] = valeur
    return scores


def _ajouter_qualite(par_run: list[dict[str, float]]) -> bool:
    """Ajoute la Qualité de chaque run, sur les Tâches définies dans **tous** les runs.

    Retourne True si ce tirage a écarté des Tâches définies dans certains runs seulement.
    """
    definies = set.intersection(*(set(s) for s in par_run))
    partiel = definies != set.union(*(set(s) for s in par_run))
    for scores in par_run:
        qualite = _moyenne([scores[c] for c in definies])
        if qualite is not None:
            scores[QUALITE] = qualite
    return partiel


def _avertissements(runs: Sequence[RunCharge], communs: Mapping[str, list[str]]) -> list[str]:
    alertes: list[str] = []
    for code in CODES:
        nombres = [sum(1 for i in run.items if i.code == code) for run in runs]
        if not any(nombres):
            continue
        n = len(communs.get(code, []))
        if code not in communs:
            alertes.append(f"tâche {code} retirée : absente ou sans item commun (items {nombres})")
        elif any(x != n for x in nombres):
            alertes.append(f"tâche {code} : {n} items communs sur {nombres} par run")
    for run in runs:
        if run.scores.jeu_version != runs[0].scores.jeu_version:
            alertes.append(f"jeux différents : {run.run_id} en {run.scores.jeu_version}")
        if run.scores.juge_principal != runs[0].scores.juge_principal:
            alertes.append(
                f"juges principaux différents : {run.run_id} noté par {run.scores.juge_principal}"
            )
    if any(run.scores.jeu_statut == cfg.STATUT_RELU_LLM for run in runs):
        alertes.append(
            "jeu de développement (relu-llm) : comparaison pour décider, jamais une mesure finale"
        )
    return alertes


def _controler_homogenes(runs: Sequence[RunCharge]) -> None:
    """Refuse des runs notés sur des jeux ou par des juges principaux différents."""
    jeux = sorted({run.scores.jeu_version for run in runs})
    juges = sorted({run.scores.juge_principal for run in runs})
    if len(jeux) > 1 or len(juges) > 1:
        raise ValueError(
            f"runs non comparables : jeux {', '.join(jeux)} ; juges principaux "
            f"{', '.join(juges)} (--autoriser-jeux-differents pour passer outre)"
        )


def comparer(
    runs: Sequence[RunCharge],
    *,
    tirages: int = 2000,
    graine: int = 7,
    autoriser_jeux_differents: bool = False,
    exclus: Collection[str] = (),
) -> Resultat:
    """Bootstrap apparié : le premier run est la référence A, les suivants sont les B.

    Lève `ValueError` si les runs portent des jeux ou des juges principaux différents, sauf
    `autoriser_jeux_differents` (l'écart est alors un avertissement). `exclus` : items retirés
    de l'ensemble commun avant tirage (par exemple non notés dans l'un des runs).
    """
    if not runs:
        raise ValueError("au moins un run requis")
    if not autoriser_jeux_differents:
        _controler_homogenes(runs)
    if tirages < 1:
        raise ValueError("--bootstrap doit être au moins 1")
    for run in runs:
        verifier_recalcul(run)
    communs: dict[str, list[str]] = {}
    for code in CODES:
        listes = [
            {i.id for i in run.items if i.code == code and i.id not in exclus} for run in runs
        ]
        commun = sorted(set.intersection(*listes))
        if commun:
            communs[code] = commun
    avertissements = _avertissements(runs, communs)
    rng = random.Random(graine)
    tires: list[list[dict[str, float]]] = [[] for _ in runs]
    partiels = 0
    for _ in range(tirages):
        tirage = {code: rng.choices(liste, k=len(liste)) for code, liste in communs.items()}
        du_tirage = [_scores_taches(run, tirage) for run in runs]  # mêmes items pour tous
        partiels += _ajouter_qualite(du_tirage)
        for rang, scores in enumerate(du_tirage):
            tires[rang].append(scores)
    observes = [_scores_taches(run, communs) for run in runs]
    if _ajouter_qualite(observes):
        avertissements.append("Qualité observée calculée sur les seules Tâches définies partout")
    if partiels:
        avertissements.append(
            f"Qualité : {partiels}/{tirages} tirages sur un sous-ensemble de Tâches "
            "(Tâche sans score dans un des runs)"
        )
    for run, obs in zip(runs, observes, strict=True):
        for code, valeur in obs.items():
            attendu = run.scores.taches[code].score if code in run.scores.taches else None
            if code != QUALITE and attendu is not None and abs(valeur - attendu) > 0.05:
                avertissements.append(
                    f"{run.run_id}, {code} : {valeur:.1f} sur items communs, "
                    f"{attendu:.1f} dans scores.json"
                )
    comparaisons = []
    for b in range(1, len(runs)):
        lignes = [
            _ligne(nom, observes[0], observes[b], tires[0], tires[b]) for nom in [*communs, QUALITE]
        ]
        comparaisons.append(Comparaison(runs[0].run_id, runs[b].run_id, lignes))
    bruit: dict[str, float | None] = {}
    for rang, run in enumerate(runs):
        qualites = [t[QUALITE] for t in tires[rang] if QUALITE in t]
        bruit[run.run_id] = _ic(qualites).demi_largeur if qualites else None
    return Resultat(
        runs=[r.run_id for r in runs],
        tirages=tirages,
        graine=graine,
        comparaisons=comparaisons,
        bruit_qualite=bruit,
        items_communs={code: len(liste) for code, liste in communs.items()},
        avertissements=avertissements,
        tirages_partiels=partiels,
        observes=observes,
    )


def _ligne(
    nom: str,
    obs_a: Mapping[str, float],
    obs_b: Mapping[str, float],
    tires_a: Sequence[Mapping[str, float]],
    tires_b: Sequence[Mapping[str, float]],
) -> LigneComparaison:
    a, b = obs_a.get(nom), obs_b.get(nom)
    ecarts = [
        tb[nom] - ta[nom]
        for ta, tb in zip(tires_a, tires_b, strict=True)
        if nom in ta and nom in tb
    ]
    if a is None or b is None or not ecarts:
        return LigneComparaison(nom, a, b, None, None, None, len(ecarts))
    return LigneComparaison(
        nom, a, b, b - a, _ic(ecarts), sum(1 for e in ecarts if e > 0) / len(ecarts), len(ecarts)
    )


def _f(valeur: float | None, signe: bool = False) -> str:
    if valeur is None:
        return "—"
    return f"{valeur:+.1f}" if signe else f"{valeur:.1f}"


def tableau_markdown(resultat: Resultat) -> str:
    """Tableau Markdown par comparaison, puis le « bruit items » de la Qualité de chaque run."""
    sortie = [
        f"Bootstrap apparié : {resultat.tirages} tirages, graine {resultat.graine}, "
        f"IC {NIVEAU_IC:.0%} (percentiles). Écart = B − A.",
        "",
        "Items communs : " + ", ".join(f"{c} {n}" for c, n in resultat.items_communs.items()),
    ]
    sortie += [f"Avertissement : {a}" for a in resultat.avertissements]
    sortie += [
        "",
        "Note : le score de LC est plafonné quand le gain de Kandel-Moles du tirage passe "
        "sous le seuil ; le plafond dépend donc du tirage.",
    ]
    for comparaison in resultat.comparaisons:
        sortie += [
            "",
            f"### A = `{comparaison.reference}` ; B = `{comparaison.autre}`",
            "",
            "| Tâche | A | B | Écart B − A | IC 95 % de l'écart | P(écart > 0) | Tirages |",
            "|---|---|---|---|---|---|---|",
        ]
        for ligne in comparaison.lignes:
            if ligne.ic is None:
                ic = "—"
            else:
                ic = f"[{_f(ligne.ic.bas, True)} ; {_f(ligne.ic.haut, True)}]"
            p = "—" if ligne.p_positif is None else f"{ligne.p_positif:.3f}"
            sortie.append(
                f"| {ligne.nom} | {_f(ligne.score_a)} | {_f(ligne.score_b)} | "
                f"{_f(ligne.ecart, True)} | {ic} | {p} | {ligne.n_valides} |"
            )
    sortie += ["", "Bruit items de la Qualité d'un run seul (demi-écart de l'IC 95 %) :", ""]
    sortie += [f"- `{run}` : ± {_f(bruit)}" for run, bruit in resultat.bruit_qualite.items()]
    return "\n".join(sortie) + "\n"


def comparer_runs(
    ids: Sequence[str],
    *,
    racine: str | Path | None = None,
    tirages: int = 2000,
    graine: int = 7,
    autoriser_jeux_differents: bool = False,
) -> Resultat:
    """Recharge les runs de notation `ids` (lecture seule) et lance `comparer`."""
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    seuils = cfg.charger_evaluation().seuils
    return comparer(
        [charger_run(i, base, seuils) for i in ids],
        tirages=tirages,
        graine=graine,
        autoriser_jeux_differents=autoriser_jeux_differents,
    )


__all__ = [
    "ErreurRecalcul",
    "Resultat",
    "RunCharge",
    "charger_run",
    "comparer",
    "comparer_runs",
    "tableau_markdown",
    "verifier_recalcul",
]
