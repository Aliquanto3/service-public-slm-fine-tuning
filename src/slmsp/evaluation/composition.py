"""Composition d'un run de notation par routage de Tâche (story 15.1, `eval composer`).

`composer(route, defaut)` crée un run `eval-notation` (phase `composition`) où chaque Tâche
reprend les verdicts, les contrôles et le Score de Tâche du run routé, sinon du run par
défaut. Lecture seule des runs sources, aucun appel au juge. Le run composé a les mêmes
fichiers qu'un run de notation (`controles.jsonl`, `verdicts.jsonl`, `scores.json`) : `eval
comparer` le lit tel quel ; les générations viennent du run de génération de la source de
chaque Tâche (`config.generations_par_tache`).

Statuts des sources : `complet` ou `partiel-erreur` (items en erreur déjà comptés dans ses
scores, comme les lit `eval comparer`) ; le run composé prend le moins bon et consigne les
sources partielles (`config.sources_partielles`). Le Comparatif ignore les runs composés.

Refus (`ErreurComposition`, aucun run écrit) : autre statut, source déjà composée, jeu ou
version différents, liste d'items absente ou différente, SHA de grille absent ou différent,
juge principal (modèle, fournisseur, effort, mode d'appel) différent, SHA des prompts de
Tâche (entrée `taches` du run de génération) différents.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import SlmspError
from slmsp.core.items import CODES, lire_jeu
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation import notation

PHASE: Final = "composition"
MARQUES: Final = ("deja-consulte",)
STATUTS_SOURCES: Final = ("complet", "partiel-erreur")
"""Statuts admis, du meilleur au moins bon ; le run composé prend le moins bon."""
CHAMPS_JUGE: Final = ("modele", "fournisseur", "effort", "mode_appel")


class ErreurComposition(SlmspError):
    """Les runs sources ne peuvent pas être composés."""


def _config(run: Run) -> dict[str, Any]:
    return dict(run.manifeste.config)


def _principal(run: Run) -> dict[str, Any]:
    juges = _config(run).get("juges")
    principal = juges.get("principal") if isinstance(juges, dict) else None
    if not isinstance(principal, dict) or not principal.get("modele"):
        raise ErreurComposition(f"run {run.run_id} : juge principal non renseigné")
    return {champ: principal.get(champ) for champ in CHAMPS_JUGE}


def _second_present(run: Run) -> bool:
    juges = _config(run).get("juges")
    return isinstance(juges, dict) and bool(juges.get("second"))


def _empreintes(run: Run, base: Path) -> dict[str, Any]:
    config = _config(run)
    items = config.get("items")
    grille = run.manifeste.entrees.get("grille")
    if not isinstance(items, list) or not items or not grille:
        raise ErreurComposition(f"run {run.run_id} : liste d'items ou SHA de grille absent")
    generation = ouvrir_run(str(config.get("run_generation")), racine=base)
    return {
        "jeu_version": run.manifeste.jeu_version,
        "items": sorted(items),
        "grille_sha256": grille,
        "manifeste_jeu_sha256": run.manifeste.entrees.get("manifeste_jeu"),
        "juge_principal": _principal(run),
        "second_juge": _second_present(run),
        "taches_sha256": generation.manifeste.entrees.get("taches"),
        "version_harnais": _version_harnais(generation),
    }


def _version_harnais(generation: Run) -> int:
    """Version du harnais du run de génération (1 sans mention, story 16.2)."""
    valeur = _config(generation).get("version_harnais", 1)
    return valeur if isinstance(valeur, int) and not isinstance(valeur, bool) else 1


def _ouvrir_source(run_id: str, base: Path) -> Run:
    run = ouvrir_run(run_id, racine=base)
    if run.type != notation.TYPE_RUN:
        raise ErreurComposition(f"run {run_id} de type {run.type!r}, pas {notation.TYPE_RUN!r}")
    statut = run.statut_courant()
    if statut not in STATUTS_SOURCES:
        attendus = " ou ".join(f"`{s}`" for s in STATUTS_SOURCES)
        raise ErreurComposition(f"run {run_id} : statut {statut!r}, {attendus} attendu")
    if _config(run).get("phase") == PHASE:
        raise ErreurComposition(f"run {run_id} est déjà un run composé")
    return run


def _lignes_par_tache(run: Run, nom: str, code_de: dict[str, str]) -> dict[str, list[Any]]:
    par_tache: dict[str, list[Any]] = {}
    for ligne in run.lire_jsonl(nom):
        par_tache.setdefault(code_de.get(ligne["item_id"], ""), []).append(ligne)
    return par_tache


def composer(
    route: dict[str, str],
    defaut: str,
    *,
    marque: str | None = None,
    racine: str | Path | None = None,
) -> Run:
    """Crée le run composé, au moins bon statut de ses sources.

    Lève `ErreurComposition` avant toute écriture.
    """
    if marque is not None and marque not in MARQUES:
        raise ErreurComposition(f"marque inconnue : {marque!r} (attendu : {', '.join(MARQUES)})")
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    sources = {rid: _ouvrir_source(rid, base) for rid in {defaut, *route.values()}}
    ref = _empreintes(sources[defaut], base)
    for rid, source in sources.items():
        for champ, valeur in _empreintes(source, base).items():
            if valeur != ref[champ]:
                raise ErreurComposition(
                    f"runs non composables : {champ} de {rid} diffère de celui de {defaut}"
                )
    scores = {
        rid: Scores.model_validate_json((s.dossier / "scores.json").read_bytes())
        for rid, s in sources.items()
    }
    scores_defaut = scores[defaut]
    jeu = lire_jeu(str(ref["jeu_version"]), base)
    code_de = {i.id: i.code for i in jeu.items}
    presentes = {code_de[i] for i in ref["items"] if i in code_de}
    for tache, rid in route.items():
        if tache not in CODES:
            raise ErreurComposition(f"tâche inconnue : {tache!r}")
        if (
            tache not in scores_defaut.taches
            or tache not in scores[rid].taches
            or tache not in presentes
        ):
            raise ErreurComposition(f"tâche {tache} absente des runs à composer")
    choix = {t: route.get(t, defaut) for t in scores_defaut.taches}
    generations = {t: str(_config(sources[rid])["run_generation"]) for t, rid in choix.items()}
    run_defaut = sources[defaut]
    statuts = {rid: s.statut_courant() for rid, s in sources.items()}
    statut = max(statuts.values(), key=STATUTS_SOURCES.index)
    run = nouveau_run(
        notation.TYPE_RUN,
        "compose",
        {
            "phase": PHASE,
            "run_generation": str(_config(run_defaut)["run_generation"]),
            "generations_par_tache": generations,
            "items": ref["items"],
            "juges": _config(run_defaut).get("juges"),
            "echantillons": _config(run_defaut).get("echantillons"),
            "route": dict(sorted(route.items())),
            "defaut": defaut,
            "sources": sorted(sources),
            "sources_partielles": sorted(r for r, s in statuts.items() if s != "complet"),
            "marque": marque,
            "empreintes_sources": {k: v for k, v in ref.items() if k != "items"},
        },
        parents=sorted(sources),
        graine=run_defaut.manifeste.graine,
        racine=base,
        modele_ref=run_defaut.manifeste.modele_ref,
        quantification=run_defaut.manifeste.quantification,
        variante_llamacpp=run_defaut.manifeste.variante_llamacpp,
        jeu_version=run_defaut.manifeste.jeu_version,
    )
    try:
        taches = {t: scores[rid].taches[t] for t, rid in choix.items()}
        for nom in (notation.FICHIER_CONTROLES, notation.FICHIER_VERDICTS):
            ecrites = False
            for rid in sorted(set(choix.values())):
                lignes = _lignes_par_tache(sources[rid], nom, code_de)
                for tache in sorted(t for t, r in choix.items() if r == rid):
                    for ligne in lignes.get(tache, []):
                        run.ajouter_jsonl(nom, ligne)
                        ecrites = True
            if not ecrites:
                run.ecrire(nom, b"")
        composes = scores_defaut.model_copy(
            update={
                "taches": taches,
                "cout_juge_total_eur": round(sum(t.cout_juge_eur for t in taches.values()), 6),
            }
        )
        run.ecrire(
            notation.FICHIER_SCORES, json_canonique(composes.model_dump(mode="json")) + b"\n"
        )
    except BaseException as exc:
        run.terminer("interrompu", motif=f"{type(exc).__name__} : {exc}"[:500])
        raise
    run.terminer(statut)
    return run


__all__ = ["MARQUES", "PHASE", "STATUTS_SOURCES", "ErreurComposition", "composer"]
