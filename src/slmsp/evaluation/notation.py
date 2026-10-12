"""Phase notation du banc : run `eval-notation`, parent = run `eval-generation` (story 5.6).

`noter(depuis, juges=…)` :

1. ouvre le run de génération `depuis` (type `eval-generation`, statut `complet` ou
   `partiel-erreur`, sinon `SlmspError` sans créer de run) et revérifie le manifeste du jeu
   (`verifier_manifeste`, code 4) ; `calibrage` est admis sans manifeste, ses échantillons
   sont alors tirés par `gel.tirer_echantillons(items, GRAINE)` ;
2. crée le run (slug du parent, `parents=[depuis]`, modèle et jeu recopiés) ;
3. calcule les contrôles automatiques des items `ok` (`controles.jsonl`) ;
4. soumet au Juge principal les items `ok` des Tâches jugées et les RD en litige (jamais
   CO), puis au second juge les items de l'échantillon `second_juge` ;
5. écrit `verdicts.jsonl` (une ligne par item × juge), `scores.json`
   (`json_canonique(Scores) + LF`, formules de `evaluation.scores`) et `relecture.md`, puis
   le statut final : `partiel-budget` si un juge a épuisé son budget, `partiel-erreur` si un
   item est en erreur ou non jugé pour une autre raison, `complet` sinon.

Les juges sont injectés (`Juges`) : `principal.juger(demandes)` et
`second.juger(demandes, echantillon)` rendent un rapport (`resultats`, `budget_epuise`) dont
chaque résultat porte `item_id`, `cle`, `statut`, `verdict` et `motif`. Une `BudgetEpuise`
levée par un juge vaut `budget_epuise` pour toutes ses demandes. Le coût du Juge inscrit dans
les scores est la somme de `cache.cumul_appels(cle)` des clés retenues : il est identique
quand le cache est plein, et la notation se relance sans `--reprendre`.

Seule `ouvrir_juges` importe `slmsp.judge.claude`, `slmsp.judge.second` et `slmsp.mistral`
(imports paresseux) : le reste du module ne touche ni `anthropic` ni `mistralai`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide, SlmspError
from slmsp.core.items import VERSION_CALIBRAGE, ItemBase, ItemRD, lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.manifeste_jeu import Echantillons
from slmsp.core.schemas.scores import Scores
from slmsp.core.schemas.verdict import Verdict
from slmsp.evaluation import config as cfg
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation.controles import controler
from slmsp.evaluation.gel import sha256_lf, tirer_echantillons, verifier_manifeste
from slmsp.evaluation.relecture import NOM_RELECTURE, NOM_SCORES, rendre_relecture
from slmsp.evaluation.scores import Jugement, calculer_scores
from slmsp.judge.cache import CacheVerdicts
from slmsp.judge.prompt import ItemNonJugeable, schema_sortie

TYPE_RUN: Final = "eval-notation"
FICHIER_CONTROLES: Final = "controles.jsonl"
FICHIER_VERDICTS: Final = "verdicts.jsonl"
FICHIER_SCORES: Final = NOM_SCORES
FICHIER_RELECTURE: Final = NOM_RELECTURE
GRAINE: Final = phase_generation.GRAINE
"""Graine des échantillons du calibrage (sans manifeste)."""
STATUTS_PARENT: Final = ("complet", "partiel-erreur")
JUGE_PRINCIPAL: Final = "principal"
JUGE_SECOND: Final = "second"
MOTIF_BUDGET: Final = "budget"
MOTIF_NON_JUGEABLE: Final = "non-jugeable"

_MOTIF_SLUG = re.compile(r"^\d{8}-\d{6}-(?P<slug>[a-z0-9.-]+)-[0-9a-f]{4}$")

Rapporteur = Callable[[str], None]
"""`rapporter(message)` à chaque étape de la notation."""


# --- Juges -------------------------------------------------------------------------------------


class JugePrincipal(Protocol):
    """Juge principal : un résultat par demande, dans l'ordre (`judge.claude.JugeClaude`)."""

    def juger(self, demandes: Sequence[Any]) -> Any: ...


class SecondJuge(Protocol):
    """Second juge : demandes de l'échantillon seulement (`judge.second.JugeMistral`)."""

    def juger(self, demandes: Sequence[Any], echantillon: Collection[str]) -> Any: ...


@dataclass(frozen=True)
class Demande:
    """Item à juger et sortie canonique ; même forme que `judge.claude.DemandeJugement`."""

    item: ItemBase
    sortie: Mapping[str, Any]


@dataclass
class Juges:
    """Juges injectés dans `noter` et cache de verdicts commun (coûts journalisés)."""

    principal: JugePrincipal
    second: SecondJuge | None
    cache: CacheVerdicts
    description: dict[str, Any] = field(default_factory=dict)
    """Modèles et réglages des juges, inscrits dans la config du run (jamais dans les scores)."""


def ouvrir_juges(racine: str | Path | None = None, mode_appel: str | None = None) -> Juges:
    """Assemble les juges réels : Juge Claude, second juge Mistral, registre et cache réels.

    `mode_appel` (`batch` ou `direct`) surcharge celui de `juges.toml` (hors clé de cache).
    Lève `SecretManquant` si une clé d'API manque, `ConfigurationInvalide` pour une config.
    """
    from slmsp.budget.registre import RegistreBudget
    from slmsp.judge.claude import JugeClaude, fabriquer_client
    from slmsp.judge.config import charger_juges
    from slmsp.judge.grille import charger_grille
    from slmsp.judge.second import JugeMistral
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral

    config = charger_juges()
    principal = config.principal
    if mode_appel is not None:
        if mode_appel not in ("batch", "direct"):
            raise ValueError(f"mode d'appel inconnu : {mode_appel!r} (attendu : batch, direct)")
        principal = principal.model_copy(update={"mode_appel": mode_appel})
    base = Path(racine) if racine is not None else None
    grille = charger_grille(principal.chemin_grille(base))
    registre = RegistreBudget()
    cache = CacheVerdicts()
    config_mistral = charger_mistral()
    client_mistral = ClientMistral(config_mistral, registre, fabriquer_sdk(config_mistral))
    return Juges(
        principal=JugeClaude(principal, registre, cache, fabriquer_client(principal), grille),
        second=JugeMistral(config.second, client_mistral, cache, grille),
        cache=cache,
        description={
            JUGE_PRINCIPAL: {
                "modele": principal.modele,
                "effort": principal.effort,
                "mode_appel": principal.mode_appel,
            },
            JUGE_SECOND: {"modele": config.second.modele, "effort": config.second.effort_cle},
        },
    )


# --- Rapport -----------------------------------------------------------------------------------


@dataclass
class RapportNotation:
    """Bilan d'une notation : run, statut, scores et appels de cette session."""

    run: Run
    statut: str
    scores: Scores
    demandes_principal: int = 0
    demandes_second: int = 0
    depuis_cache: int = 0
    budget_epuise: bool = False
    cout_session_eur: float = 0.0
    """Coût payé pendant cette session (0 à cache plein) ; absent de `scores.json`."""


@dataclass
class _Issue:
    jugements: dict[str, Jugement] = field(default_factory=dict)
    budget_epuise: bool = False
    depuis_cache: int = 0
    cout_eur: float = 0.0


# --- Étapes ------------------------------------------------------------------------------------


def _racine(racine: str | Path | None) -> Path:
    return (Path(racine) if racine is not None else racine_projet()).resolve()


def _ouvrir_parent(depuis: str, base: Path) -> Run:
    parent = ouvrir_run(depuis, racine=base)
    if parent.type != phase_generation.TYPE_RUN:
        raise ManifesteInvalide(
            f"run {depuis} de type {parent.type!r}, pas {phase_generation.TYPE_RUN!r}"
        )
    statut = parent.statut_courant()
    if statut not in STATUTS_PARENT:
        raise SlmspError(
            f"run de génération {depuis} au statut {statut!r} : notation refusée "
            f"(attendu : {' ou '.join(STATUTS_PARENT)})"
        )
    if parent.manifeste.jeu_version is None:
        raise ManifesteInvalide(f"run {depuis} : run.json sans jeu_version")
    return parent


def _generations(parent: Run) -> dict[str, Generation]:
    generations: dict[str, Generation] = {}
    for rang, ligne in enumerate(parent.lire_jsonl(phase_generation.FICHIER_GENERATIONS), 1):
        try:
            generation = Generation.model_validate(ligne)
        except ValidationError:
            raise ManifesteInvalide(
                f"run {parent.run_id} : ligne {rang} de "
                f"{phase_generation.FICHIER_GENERATIONS} invalide"
            ) from None
        generations.setdefault(generation.item_id, generation)
    return generations


def _selection(
    parent: Run, items: Sequence[ItemBase], generations: Mapping[str, Any]
) -> list[ItemBase]:
    demandes = parent.manifeste.config.get("items")
    retenus = list(demandes) if isinstance(demandes, list) else list(generations)
    connus = {item.id for item in items}
    inconnus = [i for i in retenus if i not in connus]
    if inconnus:
        raise ManifesteInvalide(
            f"run {parent.run_id} : item(s) absent(s) du jeu : {', '.join(map(str, inconnus))}"
        )
    garder = set(retenus)
    return [item for item in items if item.id in garder]


def _slug(run_id: str) -> str:
    m = _MOTIF_SLUG.fullmatch(run_id)
    return m["slug"] if m else "notation"


def _jugeable(item: ItemBase) -> bool:
    try:
        schema_sortie(item)
    except ItemNonJugeable:
        return False
    return True


def _juger(appel: Callable[[], Any], demandes: Sequence[Demande]) -> _Issue:
    """Appelle un juge ; une `BudgetEpuise` levée vaut `non-juge` pour toutes les demandes."""
    issue = _Issue()
    if not demandes:
        return issue
    try:
        rapport = appel()
    except BudgetEpuise:
        issue.budget_epuise = True
        for demande in demandes:
            issue.jugements[demande.item.id] = Jugement("non-juge", motif=MOTIF_BUDGET)
        return issue
    issue.budget_epuise = bool(getattr(rapport, "budget_epuise", False))
    issue.cout_eur = float(getattr(rapport, "cout_total_eur", 0.0) or 0.0)
    for resultat in rapport.resultats:
        verdict = resultat.verdict
        if verdict is not None and not isinstance(verdict, Verdict):
            verdict = Verdict.model_validate(verdict)
        issue.jugements[resultat.item_id] = Jugement(
            statut=resultat.statut, verdict=verdict, cle=resultat.cle, motif=resultat.motif
        )
        issue.depuis_cache += bool(getattr(resultat, "depuis_cache", False))
    return issue


def _ligne_verdict(item: ItemBase, juge: str, jugement: Jugement) -> dict[str, Any]:
    return {
        "item_id": item.id,
        "tache": item.code,
        "juge": juge,
        "statut": jugement.statut,
        "motif": jugement.motif,
        "cle": jugement.cle,
        "verdict": None if jugement.verdict is None else jugement.verdict.model_dump(mode="json"),
    }


def _couts(
    cache: CacheVerdicts, items: Sequence[ItemBase], issues: Sequence[_Issue]
) -> dict[str, float]:
    couts: dict[str, float] = {}
    for item in items:
        cles = {
            j.cle for issue in issues if (j := issue.jugements.get(item.id)) and j.cle is not None
        }
        if cles:
            couts[item.id] = sum(cache.cumul_appels(cle)[0] for cle in sorted(cles))
    return couts


def _entrees(parent: Run, jeu_version: str, base: Path, chemin_items: Path) -> dict[str, Path]:
    projet = racine_projet() / "config"
    entrees: dict[str, Path] = {
        "generations": parent.dossier / phase_generation.FICHIER_GENERATIONS,
        "evaluation": projet / cfg.NOM_EVALUATION,
        "juges": projet / "juges.toml",
    }
    if jeu_version == VERSION_CALIBRAGE:
        entrees["items_jeu"] = chemin_items
    else:
        entrees["manifeste_jeu"] = cfg.chemin_manifeste(base, jeu_version)
    grille = cfg.chemin_grille(base)
    if grille.is_file():
        entrees["grille"] = grille
    return entrees


def noter(
    depuis: str,
    *,
    juges: Juges,
    racine: str | Path | None = None,
    rapporter: Rapporteur | None = None,
    config: cfg.ConfigEvaluation | None = None,
) -> RapportNotation:
    """Note le run de génération `depuis` (voir le module) et rend le bilan de la session.

    Lève `ManifesteInvalide` (code 4 : jeu altéré, run introuvable ou d'un autre type) et
    `SlmspError` (génération ni `complet` ni `partiel-erreur`) avant de créer le run.
    """
    dire = rapporter or (lambda _message: None)
    base = _racine(racine)
    parent = _ouvrir_parent(depuis, base)
    manifeste_parent = parent.manifeste
    jeu_version = manifeste_parent.jeu_version
    assert jeu_version is not None
    evaluation = config if config is not None else cfg.charger_evaluation()

    manifeste_sha: str | None = None
    if jeu_version == VERSION_CALIBRAGE:
        jeu = lire_jeu(jeu_version, base)
        echantillons: Echantillons = tirer_echantillons(jeu.items, GRAINE)
        jeu_statut = VERSION_CALIBRAGE
    else:
        manifeste_jeu = verifier_manifeste(jeu_version, base)
        jeu = lire_jeu(jeu_version, base)
        echantillons = manifeste_jeu.echantillons
        jeu_statut = manifeste_jeu.statut
        manifeste_sha = sha256_lf(cfg.chemin_manifeste(base, jeu_version))
    generations = _generations(parent)
    selection = _selection(parent, jeu.items, generations)

    run = nouveau_run(
        TYPE_RUN,
        _slug(depuis),
        {
            "phase": "notation",
            "run_generation": depuis,
            "items": [item.id for item in selection],
            "juges": juges.description,
            "echantillons": echantillons.model_dump(mode="json"),
        },
        parents=[depuis],
        entrees=_entrees(parent, jeu_version, base, jeu.chemin_items),
        graine=echantillons.graine,
        racine=base,
        modele_ref=manifeste_parent.modele_ref,
        quantification=manifeste_parent.quantification,
        variante_llamacpp=manifeste_parent.variante_llamacpp,
        jeu_version=jeu_version,
    )
    try:
        rapport = _noter_dans(
            run,
            depuis=depuis,
            juges=juges,
            selection=selection,
            generations=generations,
            echantillons=echantillons,
            evaluation=evaluation,
            jeu_version=jeu_version,
            jeu_statut=jeu_statut,
            manifeste_sha=manifeste_sha,
            dire=dire,
        )
    except BaseException as exc:
        run.terminer("interrompu", motif=f"{type(exc).__name__} : {exc}"[:500])
        raise
    run.terminer(rapport.statut)
    return rapport


def _noter_dans(
    run: Run,
    *,
    depuis: str,
    juges: Juges,
    selection: Sequence[ItemBase],
    generations: Mapping[str, Generation],
    echantillons: Echantillons,
    evaluation: cfg.ConfigEvaluation,
    jeu_version: str,
    jeu_statut: str,
    manifeste_sha: str | None,
    dire: Rapporteur,
) -> RapportNotation:
    ok = [i for i in selection if i.id in generations and generations[i.id].statut == "ok"]
    longueurs = evaluation.re.longueurs.model_dump()
    controles: dict[str, dict[str, Any]] = {}
    for item in ok:
        controle = controler(
            item,
            generations[item.id],
            equivalences=evaluation.co.equivalences,
            longueurs=longueurs,
        )
        controles[item.id] = controle
        run.ajouter_jsonl(
            FICHIER_CONTROLES, {"item_id": item.id, "tache": item.code, "controle": controle}
        )
    dire(f"Contrôles automatiques : {len(ok)} item(s) ok sur {len(selection)}.")

    soumis: list[ItemBase] = []
    non_jugeables: dict[str, Jugement] = {}
    for item in ok:
        if item.code in cfg.TACHES_JUGEES or (
            isinstance(item, ItemRD) and controles[item.id].get("litige")
        ):
            if _jugeable(item):
                soumis.append(item)
            else:
                non_jugeables[item.id] = Jugement("non-juge", motif=MOTIF_NON_JUGEABLE)
    demandes = [
        Demande(item, generations[item.id].sortie_canonique.model_dump(mode="json"))
        for item in soumis
    ]
    dire(f"Juge principal : {len(demandes)} demande(s).")
    principal = _juger(lambda: juges.principal.juger(demandes), demandes)
    principal.jugements.update(non_jugeables)

    echantillon = list(echantillons.second_juge)
    dans_echantillon = set(echantillon)
    demandes_second = [  # seuls les items au verdict principal valide entrent dans le kappa
        d
        for d in demandes
        if d.item.code in cfg.TACHES_JUGEES
        and d.item.id in dans_echantillon
        and (j := principal.jugements.get(d.item.id)) is not None
        and j.statut == "juge"
    ]
    second = _Issue()
    if juges.second is not None and demandes_second:
        dire(f"Second juge : {len(demandes_second)} demande(s).")
        juge_second = juges.second
        second = _juger(lambda: juge_second.juger(demandes_second, echantillon), demandes_second)

    lignes_verdicts: dict[str, list[dict[str, Any]]] = {}
    for item in selection:
        for juge, issue in ((JUGE_PRINCIPAL, principal), (JUGE_SECOND, second)):
            jugement = issue.jugements.get(item.id)
            if jugement is None:
                continue
            ligne = _ligne_verdict(item, juge, jugement)
            run.ajouter_jsonl(FICHIER_VERDICTS, ligne)
            lignes_verdicts.setdefault(item.id, []).append(ligne)

    manifeste_run = run.manifeste
    scores = calculer_scores(
        items=selection,
        generations=generations,
        controles=controles,
        principal=principal.jugements,
        second=second.jugements,
        seuils=evaluation.seuils,
        run_generation=depuis,
        jeu_version=jeu_version,
        jeu_statut=jeu_statut,
        manifeste_sha256=manifeste_sha,
        modele_ref=manifeste_run.modele_ref,
        quantification=manifeste_run.quantification,
        couts=_couts(juges.cache, selection, (principal, second)),
    )
    run.ecrire(FICHIER_SCORES, json_canonique(scores.model_dump(mode="json")) + b"\n")

    relecture = set(echantillons.relecture)
    a_relire = [item for item in selection if item.id in relecture]
    run.ecrire(
        FICHIER_RELECTURE, rendre_relecture(a_relire, generations, lignes_verdicts, controles)
    )

    budget = principal.budget_epuise or second.budget_epuise
    en_erreur = len(ok) < len(selection)
    autres_non_juges = any(
        j.statut == "non-juge" and j.motif != MOTIF_BUDGET
        for issue in (principal, second)
        for j in issue.jugements.values()
    )
    if budget:
        statut = "partiel-budget"
    elif en_erreur or autres_non_juges:
        statut = "partiel-erreur"
    else:
        statut = "complet"
    return RapportNotation(
        run=run,
        statut=statut,
        scores=scores,
        demandes_principal=len(demandes),
        demandes_second=len(demandes_second),
        depuis_cache=principal.depuis_cache + second.depuis_cache,
        budget_epuise=budget,
        cout_session_eur=principal.cout_eur + second.cout_eur,
    )


__all__ = [
    "FICHIER_CONTROLES",
    "FICHIER_RELECTURE",
    "FICHIER_SCORES",
    "FICHIER_VERDICTS",
    "TYPE_RUN",
    "Demande",
    "Juges",
    "RapportNotation",
    "noter",
    "ouvrir_juges",
]
