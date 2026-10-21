"""Rapport Comparatif (story 11.1, FR-36, FR-34, SM-1, SM-6, AD-20).

`rendre_comparatif` est une fonction pure de `Donnees` : même entrée, même Markdown, octet pour
octet (aucun horodatage, aucun identifiant du run de sortie). Une valeur absente s'affiche
« non mesuré » ; une vue sans évaluation intermédiaire, « à compléter » : rien n'est estimé.
Sans Modèle fine-tuné satisfaisant SM-1, le rapport présente la meilleure Baseline comme
candidate au Modèle embarqué (chemin no-go, PRD §9.3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, Self

from pydantic import model_validator

from slmsp.compare.chargement import Donnees, Entrainement, EvaluationIntermediaire
from slmsp.core.config import ModeleConfig, charger_toml
from slmsp.core.schemas.bench import ResultatBench

NON_MESURE: Final = "non mesuré"
A_COMPLETER: Final = "à compléter"
ORDRE_TACHES: Final = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR")
LIBELLES_METHODES: Final = {"qlora": "M1", "lora": "M2", "dora": "M3", "orpo": "M4"}
GO: Final = 1024**3
NON_COMPARABLE: Final = "non comparable"
NON_CONFIGURE: Final = "métrique non configurée"
QUANTIFICATION_LIVRABLE: Final = "q4_k_m"
"""Seule quantification retenue pour une Baseline candidate au Modèle embarqué (à confirmer)."""


class MetriqueBenchmark(ModeleConfig):
    """Métrique d'un Benchmark pour le Comparatif : clé archivée, échelle vers les points, sens."""

    metrique: str
    """Clé exacte dans `ResultatBench.scores` (ex. `mmlu.acc`), la même des deux côtés."""
    echelle: float = 1.0
    """Facteur vers des points sur 100 (100 pour une fraction de 0 à 1)."""
    sens: Literal["haut", "bas", "cible"] = "haut"
    """`haut` : plus grand est meilleur ; `bas` : plus petit est meilleur ; `cible` : plus proche
    de `cible` (en points) est meilleur (ex. 50 % pour un biais)."""
    cible: float | None = None
    """Valeur idéale en points, obligatoire (et réservée) au sens `cible`."""

    @model_validator(mode="after")
    def _cible_coherente(self) -> Self:
        if (self.sens == "cible") != (self.cible is not None):
            raise ValueError('`cible` est obligatoire avec sens = "cible" et interdite sinon')
        return self


class ConfigComparatif(ModeleConfig):
    """`config/comparatif.toml` : seuils de SM-1 et métriques des Benchmarks."""

    schema_version: int
    taches_prioritaires: list[str]
    gain_min_points: float
    taches_gagnantes_min: int
    regression_max_points: float
    regression_benchmarks_max_points: float
    benchmarks: dict[str, MetriqueBenchmark] = {}


def charger_config(racine: Path) -> ConfigComparatif:
    return charger_toml(Path(racine) / "config" / "comparatif.toml", ConfigComparatif)


@dataclass(frozen=True)
class Sm1:
    """Évaluation de SM-1 pour une méthode."""

    quantification: str | None
    gains: dict[str, float | None]
    gagnantes: int
    non_regression: float | None
    benchmarks: float | None
    verdict: str
    """`satisfait`, `non satisfait` ou `indéterminé`."""
    raisons: list[str] = field(default_factory=list)


def _fmt(valeur: float | None, *, signe: bool = False) -> str:
    if valeur is None:
        return NON_MESURE
    return f"{valeur:+.1f}" if signe else f"{valeur:.1f}"


def _taches(donnees: Donnees) -> list[str]:
    noms = {t for s in donnees.baselines.values() for t in s.taches}
    noms |= {t for par_q in donnees.scores_ft.values() for s in par_q.values() for t in s.taches}
    return sorted(noms, key=lambda t: (ORDRE_TACHES.index(t) if t in ORDRE_TACHES else 99, t))


def _nom_base(cle: tuple[str, str | None]) -> str:
    modele, quant = cle
    return f"{modele} ({quant or 'quantification inconnue'})"


def _meilleures_baselines(donnees: Donnees) -> dict[str, tuple[float, str]]:
    """Par Tâche, meilleur Score de Baseline et sa configuration (modèle et quantification)."""
    meilleures: dict[str, tuple[float, str]] = {}
    for cle, scores in donnees.baselines.items():
        for tache, st in scores.taches.items():
            if st.score is None:
                continue
            actuel = meilleures.get(tache)
            if actuel is None or st.score > actuel[0]:
                meilleures[tache] = (st.score, _nom_base(cle))
    return meilleures


def _label(entrainement: Entrainement) -> str:
    methode = entrainement.methode
    if methode is None:
        return "méthode inconnue"
    return LIBELLES_METHODES.get(methode, methode)


def _methodes(donnees: Donnees) -> list[Entrainement]:
    return sorted(donnees.entrainements.values(), key=lambda e: (_label(e), e.run_id))


def _nom(entrainement: Entrainement) -> str:
    methode = entrainement.methode or "?"
    if entrainement.kl_base is not None:  # story 16.6a : poids et température du terme KL
        poids, temperature = entrainement.kl_base
        methode = f"{methode}, KL base {poids:g}, T {temperature:g}"
    return f"{_label(entrainement)} ({methode}, run {entrainement.run_id})"


def _quantification_retenue(donnees: Donnees, train: str) -> str | None:
    par_q = donnees.scores_ft.get(train, {})
    for q in ("q4_k_m", "f16"):
        if q in par_q:
            return q
    return None


def _score_ft(donnees: Donnees, train: str, quant: str, tache: str) -> float | None:
    scores = donnees.scores_ft.get(train, {}).get(quant)
    st = scores.taches.get(tache) if scores else None
    return st.score if st else None


def _gain(valeur: float | None, reference: tuple[float, str] | None) -> float | None:
    if valeur is None or reference is None:
        return None
    return round(valeur - reference[0], 4)


def _metrique(resultat: ResultatBench | None, conf: MetriqueBenchmark | None) -> float | None:
    """Valeur, en points, de la métrique configurée ; `None` si absente ou non configurée."""
    if resultat is None or conf is None:
        return None
    valeur = resultat.scores.get(conf.metrique)
    return None if valeur is None else float(valeur) * conf.echelle


def _comparable(valeur: float, conf: MetriqueBenchmark) -> float:
    """Valeur ramenée à « plus grand est meilleur » pour le sens `cible` (distance négative)."""
    return -abs(valeur - conf.cible) if conf.sens == "cible" and conf.cible is not None else valeur


def _noms_benchmarks(donnees: Donnees, train: str) -> list[str]:
    noms = {b for (b, _) in donnees.bench_base} | {b for (b, _) in donnees.bench_ft.get(train, {})}
    return sorted(noms)


def _ecart_benchmarks(
    donnees: Donnees, config: ConfigComparatif, train: str, variante: str
) -> dict[str, float | None]:
    """Écart (positif = mieux) du fine-tuné à la meilleure Baseline, par Benchmark et variante.

    `None` si la métrique n'est pas configurée ou manque d'un côté : jamais de repli sur une
    autre clé, ni de comparaison entre clés différentes.
    """
    ecarts: dict[str, float | None] = {}
    for nom in _noms_benchmarks(donnees, train):
        conf = config.benchmarks.get(nom)
        mesure = _metrique(donnees.bench_ft.get(train, {}).get((nom, variante)), conf)
        base = donnees.bench_base.get((nom, variante), {})
        valeurs = [v for r in base.values() if (v := _metrique(r, conf)) is not None]
        if conf is None or mesure is None or not valeurs:
            ecarts[nom] = None
        elif conf.sens == "bas":
            ecarts[nom] = min(valeurs) - mesure
        else:  # "haut" ou "cible" (distance négative)
            ecarts[nom] = _comparable(mesure, conf) - max(_comparable(v, conf) for v in valeurs)
    return ecarts


def evaluer_sm1(donnees: Donnees, config: ConfigComparatif, train: str) -> Sm1:
    """SM-1 : gain ≥ seuil sur assez de Tâches prioritaires, pertes bornées ailleurs."""
    quant = _quantification_retenue(donnees, train)
    if quant is None:
        return Sm1(
            None, {}, 0, None, None, "indéterminé", ["aucune évaluation du modèle fine-tuné"]
        )
    meilleures = _meilleures_baselines(donnees)
    gains = {
        t: _gain(_score_ft(donnees, train, quant, t), meilleures.get(t))
        for t in config.taches_prioritaires
    }
    gagnantes = sum(1 for g in gains.values() if g is not None and g >= config.gain_min_points)
    inconnues = sum(1 for g in gains.values() if g is None)
    nr = _gain(_score_ft(donnees, train, quant, "NR"), meilleures.get("NR"))
    variante = "apres" if quant == "q4_k_m" else "avant"
    par_bench = _ecart_benchmarks(donnees, config, train, variante)
    ecarts = [e for e in par_bench.values() if e is not None]
    incomparables = sorted(n for n, e in par_bench.items() if e is None)
    moyenne = sum(ecarts) / len(ecarts) if ecarts else None

    echecs: list[str] = []
    manques: list[str] = []
    if gagnantes < config.taches_gagnantes_min:
        if gagnantes + inconnues >= config.taches_gagnantes_min:
            manques.append("gains sur les Tâches prioritaires incomplets")
        else:
            echecs.append(
                f"{gagnantes} Tâche(s) prioritaire(s) à +{config.gain_min_points:g} points ou plus "
                f"(attendu : {config.taches_gagnantes_min})"
            )
    if nr is None:
        manques.append("non-régression non mesurée")
    elif nr < -config.regression_max_points:
        echecs.append(f"non-régression en baisse de {-nr:.1f} points")
    if moyenne is None:
        manques.append("Benchmarks non mesurés ou non comparables")
    elif moyenne < -config.regression_benchmarks_max_points:
        echecs.append(f"Benchmarks en baisse moyenne de {-moyenne:.1f} points")
    if moyenne is not None and incomparables:
        manques.append(f"Benchmarks non comparables : {', '.join(incomparables)}")
    if echecs:
        return Sm1(quant, gains, gagnantes, nr, moyenne, "non satisfait", echecs)
    if manques:
        return Sm1(quant, gains, gagnantes, nr, moyenne, "indéterminé", manques)
    return Sm1(quant, gains, gagnantes, nr, moyenne, "satisfait", [])


def _meilleure_baseline(donnees: Donnees, config: ConfigComparatif) -> tuple[str, float] | None:
    """Baseline livrable de plus haute moyenne sur les Tâches prioritaires.

    Éligible : configuration quantifiée `q4_k_m` (format du Modèle embarqué) et notée sur
    toutes les Tâches prioritaires ; une moyenne sur une couverture partielle n'est pas
    comparable. Règle à confirmer par Anaël.
    """
    classement: list[tuple[float, str]] = []
    for cle, scores in donnees.baselines.items():
        if cle[1] != QUANTIFICATION_LIVRABLE:
            continue
        valeurs = [
            st.score
            for t in config.taches_prioritaires
            if (st := scores.taches.get(t)) is not None and st.score is not None
        ]
        if valeurs and len(valeurs) == len(config.taches_prioritaires):
            classement.append((sum(valeurs) / len(valeurs), _nom_base(cle)))
    if not classement:
        return None
    moyenne, modele = max(classement, key=lambda c: (c[0], c[1]))
    return modele, moyenne


def _tableau(entetes: list[str], lignes: list[list[str]]) -> list[str]:
    sortie = ["| " + " | ".join(entetes) + " |", "|" + "|".join("---" for _ in entetes) + "|"]
    sortie.extend("| " + " | ".join(ligne) + " |" for ligne in lignes)
    return sortie


def _synthese(donnees: Donnees, config: ConfigComparatif) -> list[str]:
    lignes = ["## Synthèse et recommandation", ""]
    methodes = _methodes(donnees)
    verdicts = {e.run_id: evaluer_sm1(donnees, config, e.run_id) for e in methodes}
    if methodes:
        lignes += _tableau(
            ["Méthode", "SM-1", "Évalué sur", "Détail"],
            [
                [
                    _nom(e),
                    verdicts[e.run_id].verdict,
                    verdicts[e.run_id].quantification or NON_MESURE,
                    "; ".join(verdicts[e.run_id].raisons) or "seuils respectés",
                ]
                for e in methodes
            ],
        )
        lignes.append("")
    else:
        lignes += [
            "Aucun Run d'entraînement complet pour cette campagne : méthodes non mesurées.",
            "",
        ]
    satisfaisantes = [e for e in methodes if verdicts[e.run_id].verdict == "satisfait"]
    if satisfaisantes:

        def total(e: Entrainement) -> float:
            return sum(g for g in verdicts[e.run_id].gains.values() if g is not None)

        meilleure = max(satisfaisantes, key=lambda e: (total(e), _label(e)))
        lignes.append(
            f"**Recommandation.** {_nom(meilleure)} satisfait SM-1 : candidat au Modèle embarqué, "
            "sous réserve de la relecture humaine des verdicts et de la décision d'Anaël."
        )
    else:
        base = _meilleure_baseline(donnees, config)
        indetermines = [_label(e) for e in methodes if verdicts[e.run_id].verdict == "indéterminé"]
        if indetermines:
            lignes.append(
                "**Recommandation suspendue.** SM-1 est indéterminé faute de mesures pour : "
                f"{', '.join(indetermines)}. Le chemin no-go ne s'applique que si aucune méthode "
                "ne peut plus satisfaire SM-1 ; la Baseline ci-dessous n'est qu'un repli."
            )
        else:
            lignes.append(
                "**Recommandation (chemin no-go).** Aucun Modèle fine-tuné ne satisfait SM-1 : la "
                "meilleure Baseline livrable est présentée comme candidate au Modèle embarqué."
            )
        if base is None:
            lignes.append(
                "Meilleure Baseline livrable : indéterminée (aucune Baseline "
                f"{QUANTIFICATION_LIVRABLE} notée sur toutes les Tâches prioritaires)."
            )
        else:
            lignes.append(
                f"Meilleure Baseline livrable : `{base[0]}` (moyenne {base[1]:.1f} sur les "
                f"{len(config.taches_prioritaires)} Tâches prioritaires)."
            )
        lignes.append(
            "Plafond de RAM de 5 Go (cible 4 Go, NFR-1) : non vérifié par ce rapport, "
            "à mesurer sur le PC cible."
        )
    non_relus = any(
        not st.statuts.verdicts_relus
        for s in list(donnees.baselines.values())
        + [s for par_q in donnees.scores_ft.values() for s in par_q.values()]
        for st in s.taches.values()
    )
    if non_relus:
        lignes.append(
            "Des Scores sont « non relus » : la relecture est exigée pour la décision "
            "finale de SM-1."
        )
    return [*lignes, ""]


def _baseline(donnees: Donnees) -> list[str]:
    lignes = ["## Meilleure Baseline par Tâche", ""]
    meilleures = _meilleures_baselines(donnees)
    if not meilleures:
        return [*lignes, f"Aucune Baseline notée : {NON_MESURE}.", ""]
    corps = [
        [t, f"{meilleures[t][0]:.1f}", meilleures[t][1]]
        for t in _taches(donnees)
        if t in meilleures
    ]
    return [*lignes, *_tableau(["Tâche", "Score", "Modèle"], corps), ""]


def _gains(donnees: Donnees) -> list[str]:
    lignes = ["## Gain par Tâche, en points, par rapport à la meilleure Baseline", ""]
    meilleures = _meilleures_baselines(donnees)
    methodes = _methodes(donnees)
    if not methodes:
        return [*lignes, f"Aucune méthode entraînée : {NON_MESURE}.", ""]
    for e in methodes:
        lignes += [f"### {_nom(e)}", ""]
        corps = []
        for t in _taches(donnees):
            ref = meilleures.get(t)
            ligne = [t, f"{ref[0]:.1f}" if ref else NON_MESURE]
            for q in ("f16", "q4_k_m"):
                v = _score_ft(donnees, e.run_id, q, t)
                ligne += [_fmt(v), _fmt(_gain(v, ref), signe=True)]
            corps.append(ligne)
        lignes += _tableau(["Tâche", "Baseline", "f16", "gain f16", "q4_k_m", "gain q4_k_m"], corps)
        lignes.append("")
    return lignes


def _benchmarks(donnees: Donnees, config: ConfigComparatif) -> list[str]:
    lignes = ["## Effet sur les Benchmarks, avant et après quantification", ""]
    methodes = _methodes(donnees)
    if not methodes:
        return [*lignes, f"Aucune méthode entraînée : {NON_MESURE}.", ""]
    for e in methodes:
        lignes += [f"### {_nom(e)}", ""]
        noms = _noms_benchmarks(donnees, e.run_id)
        if not noms:
            lignes += [f"Aucun Benchmark archivé : {NON_MESURE}.", ""]
            continue
        corps = []
        for nom in noms:
            ligne = [nom]
            conf = config.benchmarks.get(nom)
            for variante in ("avant", "apres"):
                if conf is None:
                    ligne += [NON_CONFIGURE, NON_COMPARABLE]
                    continue
                ft = donnees.bench_ft.get(e.run_id, {}).get((nom, variante))
                mesure = _metrique(ft, conf)
                ecart = _ecart_benchmarks(donnees, config, e.run_id, variante)[nom]
                ligne += [
                    f"{conf.metrique} = {mesure:.1f}" if mesure is not None else NON_MESURE,
                    _fmt(ecart, signe=True),
                ]
            corps.append(ligne)
        lignes += _tableau(["Benchmark", "avant", "écart avant", "après", "écart après"], corps)
        lignes.append("")
    return lignes


def _couts(donnees: Donnees) -> list[str]:
    lignes = ["## Coûts d'entraînement", ""]
    methodes = _methodes(donnees)
    if not methodes:
        return [*lignes, f"Aucun Run d'entraînement complet : {NON_MESURE}.", ""]
    corps = []
    for e in methodes:
        c = e.couts
        corps.append(
            [
                _nom(e),
                f"{c.duree_s:.0f} s" if c and c.duree_s is not None else NON_MESURE,
                f"{c.vram_max_octets / GO:.2f} Go"
                if c and c.vram_max_octets is not None
                else NON_MESURE,
                f"{c.energie_wh:.1f} Wh" if c and c.energie_wh is not None else NON_MESURE,
                f"{c.debit_tokens_par_s:.0f}"
                if c and c.debit_tokens_par_s is not None
                else NON_MESURE,
            ]
        )
    return [
        *lignes,
        *_tableau(["Méthode", "Durée", "VRAM maximale", "Énergie", "Débit (tokens/s)"], corps),
        "",
    ]


def _point(
    evaluations: tuple[EvaluationIntermediaire, ...], cle: str, plafond: float
) -> EvaluationIntermediaire | None:
    retenues = [e for e in evaluations if getattr(e, cle) <= plafond]
    return max(retenues, key=lambda e: getattr(e, cle)) if retenues else None


def _vue(donnees: Donnees, titre: str, cle: str, unite: str) -> list[str]:
    lignes = [f"### {titre}", ""]
    methodes = _methodes(donnees)
    avec = [e for e in methodes if e.evaluations]
    if not avec:
        return [*lignes, f"{A_COMPLETER} : aucune évaluation intermédiaire archivée.", ""]
    plafond = min(max(getattr(ev, cle) for ev in e.evaluations) for e in avec)
    lignes += [f"Point de comparaison : {plafond:g} {unite} (le plus petit maximum atteint).", ""]
    meilleures = _meilleures_baselines(donnees)
    taches = _taches(donnees)
    corps = []
    for e in methodes:
        point = _point(e.evaluations, cle, plafond)
        nom = _nom(e) + (" (hors protocole)" if e.methode == "orpo" else "")
        if point is None:
            corps.append([nom, A_COMPLETER, *[A_COMPLETER for _ in taches]])
            continue
        cellules = [_fmt(_gain(point.scores.get(t), meilleures.get(t)), signe=True) for t in taches]
        corps.append([nom, f"{getattr(point, cle):g} {unite}", *cellules])
    return [*lignes, *_tableau(["Méthode", "Point retenu", *taches], corps), ""]


def _vues(donnees: Donnees) -> list[str]:
    return [
        "## Deux vues de comparaison (FR-34), gain en points par Tâche",
        "",
        *_vue(donnees, "À tokens vus égaux", "tokens_vus", "tokens"),
        *_vue(donnees, "À budget de temps égal", "duree_s", "s"),
    ]


def _derogation(donnees: Donnees) -> list[str]:
    if not any(e.methode == "orpo" for e in donnees.entrainements.values()):
        return []
    return [
        "## Dérogation au protocole : M4 (ORPO)",
        "",
        "M4 déroge au protocole de comparaison équitable : ORPO a besoin de données de préférence, "
        "dérivées du jeu SFT, et passe après le SFT. Ses résultats ne sont pas strictement "
        "comparables à ceux de M1 à M3 (FR-34).",
        "",
    ]


def _exclus(donnees: Donnees) -> list[str]:
    if not donnees.exclus:
        return []
    corps = [[x.type, x.run_id, x.motif] for x in donnees.exclus]
    return ["## Runs exclus", "", *_tableau(["Type", "Run", "Motif"], corps), ""]


def _methode_et_limites(donnees: Donnees, config: ConfigComparatif) -> list[str]:
    jeu = donnees.jeu_version or NON_MESURE
    statut_jeu = ", ".join(donnees.jeu_statuts) or NON_MESURE
    prioritaires = ", ".join(config.taches_prioritaires)
    return [
        "## Méthode et limites",
        "",
        "Ce rapport est calculé uniquement à partir des résultats archivés (évaluations, "
        "Benchmarks, entraînements, exports) : il n'interroge aucun modèle et n'utilise aucun "
        "réseau. Régénéré à partir des mêmes archives, il est identique.",
        "",
        f"- Version du jeu d'évaluation : {jeu} (statut : {statut_jeu}). Deux versions du jeu "
        "ne sont jamais mélangées.",
        "- Seuls les runs complets sont pris en compte ; les autres figurent dans « Runs exclus ».",
        "- Le gain est l'écart de Score de Tâche, en points sur 100, avec le meilleur score "
        "obtenu par un Modèle de base (Baseline) sur cette Tâche.",
        f"- SM-1 : au moins {config.gain_min_points:g} points de gain sur au moins "
        f"{config.taches_gagnantes_min} des Tâches prioritaires ({prioritaires}), "
        f"perte d'au plus {config.regression_max_points:g} points en non-régression et "
        f"{config.regression_benchmarks_max_points:g} points en moyenne sur les Benchmarks. "
        "Le verdict s'appuie sur la version quantifiée (q4_k_m) si elle est évaluée, "
        "sinon sur f16.",
        "- Chaque Baseline est une configuration (modèle et quantification) prise comme un tout. "
        f"La meilleure Baseline livrable est quantifiée {QUANTIFICATION_LIVRABLE} et notée sur "
        "toutes les Tâches prioritaires (règle à confirmer par Anaël).",
        "- Les Benchmarks servent à détecter les régressions, pas à choisir le Modèle. La "
        "métrique, son échelle et son sens sont fixés par Benchmark dans "
        "`config/comparatif.toml` ; sans cette configuration, le Benchmark est « non "
        "comparable » et SM-1 reste indéterminé.",
        "- Une valeur « non mesuré » n'a pas été archivée ; « à compléter » signale une vue qui "
        "demande des évaluations intermédiaires. Rien n'est estimé.",
        "- Les Scores marqués « non relus » n'ont pas été validés par une relecture humaine.",
        "- Les mesures viennent de la machine de développement, qui n'est pas le PC cible.",
        "",
    ]


def rendre_comparatif(donnees: Donnees, config: ConfigComparatif) -> str:
    """Markdown du Comparatif, déterministe."""
    blocs = [
        [
            f"# Comparatif des méthodes de fine-tuning : campagne {donnees.campagne}",
            "",
        ],
        _synthese(donnees, config),
        _baseline(donnees),
        _gains(donnees),
        _benchmarks(donnees, config),
        _couts(donnees),
        _vues(donnees),
        _derogation(donnees),
        _exclus(donnees),
        _methode_et_limites(donnees, config),
    ]
    lignes = [ligne for bloc in blocs for ligne in bloc]
    return "\n".join(lignes).rstrip("\n") + "\n"
