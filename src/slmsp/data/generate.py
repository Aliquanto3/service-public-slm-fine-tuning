"""Étape `generate` : génération idempotente et traces d'outils (story 9.4, FR-29, AD-17).

`lancer_generation` produit `runs/data-generate/<run_id>/` à partir d'un run `data-seed`
complet, avec le seul Générateur Mistral (D1.1) :

1. **Pré-vol** (rien n'est écrit en cas d'échec) : gabarits de chaque Tâche validés par le
   Générateur, run seed `complet` et de type `data-seed`, `amorces.jsonl` relu par
   `core.artefacts.lire`. Le gel du Jeu d'évaluation (D1.3) et les préalables Mistral
   (D1.2) sont vérifiés avant, par la CLI et par la construction du Générateur.
2. **Plan** (nouveau run) : amorces regroupées en sessions par Tâche, dans l'ordre de
   dépense d'AD-5 (`ORDRE_TACHES`), au plus `ceil(volume × (1 + surplus))` par Tâche ;
   passages de l'Index cherchés pour Q (URL protégées retirées) ; `session_id`
   déterministe (`<tâche>-<24 hex>` du JSON canonique de la Tâche, des gabarits, des
   amorces et de leur SHA, du SHA des passages rendus et de celui des outils). Le plan est
   écrit une seule fois dans `plan.jsonl`.
3. **Exécution** (`slmsp.data.sessions`) : une ligne `brut.jsonl` par session terminée,
   `abandons.jsonl` pour une session close sans exemple, `incidents.jsonl` pour une panne
   MCP (réessayée à la reprise). Toute réponse déjà journalisée est réutilisée : un
   nouveau run sur le même seed, ou une reprise, ne repaie aucun appel (D1.6, AD-26).
4. **Fin** : une ligne `bilan.jsonl` par invocation et le statut du run : `complet` (toutes
   les sessions du plan closes), `partiel-erreur` (incidents, erreur d'API, modèle refusé,
   jour changé), `partiel-budget` (`BudgetEpuise` : aucune session suivante n'est tentée),
   `interrompu` (Ctrl+C).

`reprendre_run_id` reprend un run en ajout seul : le plan est relu, les SHA du seed, des
gabarits et de `config/outils-mcp.toml` sont revérifiés (`ManifesteInvalide` si l'un a
changé, avant toute écriture), et les sessions présentes dans `brut.jsonl` ou
`abandons.jsonl` ne sont pas rejouées. Un seul écrivain par run.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run, reprendre
from slmsp.core.canonique import json_canonique, sha256_fichier, sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import (
    BudgetEpuise,
    ConfigurationInvalide,
    ManifesteInvalide,
    ProvenanceInvalide,
)
from slmsp.core.gabarits import GabaritValide
from slmsp.core.items import IdentifiantsProteges
from slmsp.core.ports import Passage
from slmsp.core.schemas.amorce import Amorce
from slmsp.core.schemas.session_donnees import (
    AbandonSession,
    IncidentSession,
    PassagePlan,
    RefGabarit,
    SessionBrute,
    SessionPlanifiee,
)
from slmsp.core.texte import normaliser
from slmsp.data.seed import _url_canonique
from slmsp.data.sessions import (
    TOURS_OUTILS_MAX,
    Compteur,
    ContexteSessions,
    ExecuteurSessions,
    IncidentOutils,
    OuvrirOutils,
    ResolveurPassages,
    passage_depuis_plan,
)
from slmsp.harness.prompts import formater_passages
from slmsp.harness.recherche_index import RequeteVide
from slmsp.mcp.outils import charger_config
from slmsp.mistral.client import ErreurApiMistral, ModeleMistralRefuse
from slmsp.mistral.generateur import (
    EMPLACEMENT_PASSAGES,
    TACHES_OUTILLEES,
    Generateur,
    PrealableNonSatisfait,
)
from slmsp.mistral.journal import USAGE_GENERATION, journal_pour

__all__ = [
    "CHAINES",
    "ORDRE_TACHES",
    "TYPE_RUN",
    "ResultatGeneration",
    "SourcePassages",
    "lancer_generation",
    "planifier",
    "seed_du_run",
]

TYPE_RUN: Final = "data-generate"
TYPE_RUN_SEED: Final = "data-seed"
ORDRE_TACHES: Final = ("Q", "RD", "CR", "LC", "generique", "CT", "RE", "CO")
"""Ordre de dépense d'AD-5 : les sessions s'exécutent strictement dans cet ordre."""
CHAINES: Final[Mapping[str, tuple[str, ...]]] = {
    "Q": ("traces-q",),
    "RD": ("traces-rd",),
    "CR": ("transcription-cr", "cr"),
    "LC": ("lc",),
    "generique": ("generique",),
    "CT": ("ct",),
    "RE": ("re",),
    "CO": ("co",),
}
"""Gabarits de chaque Tâche, dans l'ordre des appels d'une session."""

NOM_PLAN: Final = "plan.jsonl"
NOM_BRUT: Final = "brut.jsonl"
NOM_ABANDONS: Final = "abandons.jsonl"
NOM_INCIDENTS: Final = "incidents.jsonl"
NOM_BILAN: Final = "bilan.jsonl"
NOM_AMORCES: Final = "amorces.jsonl"


class SourcePassages(Protocol):
    """Recherche dans l'Index local (`harness.recherche_index.RechercheIndex` et sa version)."""

    @property
    def version(self) -> str: ...

    def rechercher(self, requete: str) -> Sequence[Passage]: ...


@dataclass(frozen=True)
class ResultatGeneration:
    """Run produit, statut final et bilan de l'invocation."""

    run: Run
    statut: str
    bilan: dict[str, Any]


# --- Plan ------------------------------------------------------------------------------------


def _origine(amorce: Amorce) -> tuple[Any, ...]:
    if amorce.auteur_contenu == "public":
        return ("public", amorce.jeu, amorce.revision, amorce.ligne)
    return (amorce.auteur_contenu, amorce.appel_id)


def _groupes(
    amorces: Sequence[Amorce], attendus: Sequence[str]
) -> tuple[list[list[Amorce]], int, int]:
    """Groupes complets (une amorce par emplacement attendu, même origine), groupes
    incomplets et amorces sans emplacement du gabarit (ignorées)."""
    ignorees = sum(1 for amorce in amorces if amorce.emplacement not in attendus)
    utiles = [amorce for amorce in amorces if amorce.emplacement in attendus]
    if len(attendus) == 1:
        return [[amorce] for amorce in utiles], 0, ignorees
    par_origine: dict[tuple[Any, ...], list[Amorce]] = {}
    for amorce in utiles:
        par_origine.setdefault(_origine(amorce), []).append(amorce)
    complets: list[list[Amorce]] = []
    incomplets = 0
    for groupe in par_origine.values():
        if sorted(a.emplacement for a in groupe) == sorted(attendus):
            complets.append(sorted(groupe, key=lambda a: attendus.index(a.emplacement)))
        else:
            incomplets += 1
    return complets, incomplets, ignorees


def _session_id(tache: str, cle: Mapping[str, Any]) -> str:
    return f"{tache.lower()}-{sha256_hex(json_canonique(dict(cle)))[:24]}"


def planifier(
    amorces: Sequence[Amorce],
    *,
    gabarits: Mapping[str, Sequence[GabaritValide]],
    volumes: Mapping[str, int],
    surplus: float,
    outils_sha256: str,
    urls_protegees: frozenset[str] = frozenset(),
    amorces_protegees: frozenset[str] = frozenset(),
    recherche: SourcePassages | None = None,
) -> tuple[list[SessionPlanifiee], dict[str, Any]]:
    """Sessions du plan (ordre d'AD-5) et comptes du plan par Tâche.

    Une session = un groupe d'amorces de la Tâche qui remplit exactement les emplacements
    du premier gabarit de sa chaîne (hors `passages`) ; les groupes sont pris par plus petit
    `amorce_id`. Comptes : `planifiees`, `deficit`, `amorces_incompletes`,
    `amorces_ignorees`, `amorces_protegees`, `passages_proteges`.

    Une amorce dont `sha256(normaliser(texte))` figure dans `amorces_protegees` (amorces
    usager du Jeu d'évaluation, revérifiées ici si les versions protégées ont changé
    depuis le seed) est écartée avant tout appel.
    """
    canoniques = {_url_canonique(url) for url in urls_protegees}
    plan: list[SessionPlanifiee] = []
    comptes: dict[str, Any] = {}
    for tache in ORDRE_TACHES:
        chaine = list(gabarits[tache])
        premier = chaine[0]
        attendus = [nom for nom in premier.emplacements if nom != EMPLACEMENT_PASSAGES]
        avec_passages = EMPLACEMENT_PASSAGES in premier.emplacements
        de_la_tache = [a for a in amorces if a.tache == tache]
        sures = [a for a in de_la_tache if sha256_hex(normaliser(a.texte)) not in amorces_protegees]
        complets, incomplets, ignorees = _groupes(sures, attendus)
        complets.sort(key=lambda groupe: min(a.amorce_id for a in groupe))
        cible = math.ceil(volumes.get(tache, 0) * (1 + surplus))
        retenus = complets[:cible]
        proteges = 0
        refs = [RefGabarit(id=g.id, version=g.version, sha256=g.sha256) for g in chaine]
        for groupe in retenus:
            passages: list[Passage] | None = None
            if avec_passages:
                if recherche is None:
                    raise ConfigurationInvalide(
                        f"Tâche {tache} : recherche dans l'Index requise pour les passages"
                    )
                texte = "\n\n".join(a.texte for a in groupe)
                try:
                    trouves = list(recherche.rechercher(texte))
                except RequeteVide:
                    trouves = []
                passages = [p for p in trouves if _url_canonique(p.url) not in canoniques]
                proteges += len(trouves) - len(passages)
            cle = {
                "tache": tache,
                "gabarits": [[r.id, r.version, r.sha256] for r in refs],
                "amorces": [[a.amorce_id, a.sha_texte] for a in groupe],
                "passages": None if passages is None else sha256_hex(formater_passages(passages)),
                "outils": outils_sha256 if tache in TACHES_OUTILLEES else None,
            }
            plan.append(
                SessionPlanifiee(
                    session_id=_session_id(tache, cle),
                    tache=tache,
                    rang=len(plan),
                    gabarits=refs,
                    amorce_ids=[a.amorce_id for a in groupe],
                    passages=(
                        None
                        if passages is None
                        else [PassagePlan(**asdict(passage)) for passage in passages]
                    ),
                    outils_sha256=outils_sha256 if tache in TACHES_OUTILLEES else None,
                )
            )
        comptes[tache] = {
            "planifiees": len(retenus),
            "cible": cible,
            "deficit": max(0, cible - len(complets)),
            "amorces_incompletes": incomplets,
            "amorces_ignorees": ignorees,
            "amorces_protegees": len(de_la_tache) - len(sures),
            "passages_proteges": proteges,
        }
    return plan, comptes


# --- Run -------------------------------------------------------------------------------------


def _ouvrir_seed(seed_run_id: str, racine: Path) -> Run:
    seed = ouvrir_run(seed_run_id, racine=racine)
    if seed.type != TYPE_RUN_SEED:
        raise ManifesteInvalide(f"run {seed_run_id} : type {seed.type!r}, {TYPE_RUN_SEED} attendu")
    if seed.statut_courant() != "complet":
        raise ManifesteInvalide(f"run seed {seed_run_id} non complet ({seed.statut_courant()})")
    return seed


def _amorces(seed: Run, racine: Path) -> list[Amorce]:
    octets = lire(seed.dossier / NOM_AMORCES, "data", racine=racine)
    amorces = []
    for numero, ligne in enumerate(octets.decode("utf-8").split("\n"), start=1):
        if not ligne.strip():
            continue
        try:
            amorces.append(Amorce.model_validate_json(ligne))
        except ValidationError:
            raise ProvenanceInvalide(
                f"seed {seed.run_id} : ligne {numero} non conforme au schéma Amorce"
            ) from None
    return amorces


def seed_du_run(run_id: str, *, racine: str | Path | None = None) -> str:
    """Run seed parent du run `data-generate` `run_id` (lève `ManifesteInvalide`)."""
    run = ouvrir_run(run_id, racine=racine)
    seed = run.manifeste.config.get("seed_run_id")
    if run.type != TYPE_RUN or not isinstance(seed, str):
        raise ManifesteInvalide(f"run {run_id} : run {TYPE_RUN} attendu")
    return seed


def _entrees(seed: Run, chemin_outils: Path, generateur: Generateur) -> dict[str, Path]:
    """Fichiers dont le SHA-256 est inscrit au run et revérifié à la reprise."""
    entrees = {"amorces": seed.dossier / NOM_AMORCES, "outils-mcp": chemin_outils}
    for tache in ORDRE_TACHES:
        for gabarit_id in CHAINES[tache]:
            entrees[f"gabarit-{gabarit_id}"] = generateur.dossier_gabarits / f"{gabarit_id}.md"
    return entrees


def _plan_du_run(run: Run, comptes_plan: Any) -> list[SessionPlanifiee]:
    """Plan d'un run repris, complet et conforme aux comptes inscrits à sa création ;
    sinon `ManifesteInvalide` (arrêt entre la création du run et l'écriture du plan)."""
    if not (run.dossier / NOM_PLAN).is_file():
        raise ManifesteInvalide(f"run {run.run_id} : {NOM_PLAN} absent, reprise refusée")
    try:
        plan = [SessionPlanifiee.model_validate(ligne) for ligne in run.lire_jsonl(NOM_PLAN)]
    except (ValidationError, ValueError):
        raise ManifesteInvalide(f"run {run.run_id} : {NOM_PLAN} illisible") from None
    attendues = (
        sum(int(c.get("planifiees", 0)) for c in comptes_plan.values())
        if isinstance(comptes_plan, Mapping)
        else None
    )
    if attendues is None or len(plan) != attendues:
        raise ManifesteInvalide(
            f"run {run.run_id} : {NOM_PLAN} incomplet ({len(plan)} sessions, "
            f"{attendues} attendues), reprise refusée"
        )
    return plan


def _gabarits(generateur: Generateur) -> dict[str, list[GabaritValide]]:
    return {t: [generateur.gabarit(g, t) for g in CHAINES[t]] for t in ORDRE_TACHES}


def _bilan_vide(plan: Sequence[SessionPlanifiee]) -> dict[str, dict[str, Any]]:
    planifiees = Counter(session.tache for session in plan)
    return {
        tache: {
            "planifiees": planifiees[tache],
            "completes": 0,
            "abandons": {},
            "incidents": 0,
            "appels_nouveaux": 0,
            "appels_reutilises": 0,
            "cout_eur": 0.0,
        }
        for tache in ORDRE_TACHES
    }


def _cumuler(ligne: dict[str, Any], compteur: Compteur) -> None:
    ligne["appels_nouveaux"] += compteur.nouveaux
    ligne["appels_reutilises"] += compteur.reutilises
    ligne["cout_eur"] += compteur.cout_eur


def _clore(
    run: Run, statut: str, motif: str | None, taches: dict[str, Any], comptes_plan: Any
) -> dict[str, Any]:
    bilan = {
        "schema_version": 1,
        "statut": statut,
        "motif": motif,
        "taches": taches,
        "cout_eur": round(sum(t["cout_eur"] for t in taches.values()), 6),
        "comptes_plan": comptes_plan,
    }
    run.ajouter_jsonl(NOM_BILAN, bilan)
    run.terminer(statut, motif)
    return bilan


def lancer_generation(
    *,
    racine: str | Path,
    volumes: Mapping[str, int],
    generateur: Generateur,
    passages: ResolveurPassages,
    ouvrir_outils: OuvrirOutils,
    proteges: IdentifiantsProteges,
    seed_run_id: str | None = None,
    reprendre_run_id: str | None = None,
    recherche: SourcePassages | None = None,
    commit_gel: str | None = None,
    surplus: float = 0.0,
    tours_outils_max: int = TOURS_OUTILS_MAX,
    chemin_outils: str | Path | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatGeneration:
    """Crée (`seed_run_id`) ou reprend (`reprendre_run_id`) un run `data-generate`.

    `generateur` est construit sur le seed du run avec `rendre_passages=passages`.
    Lève, sans rien écrire : `ManifesteInvalide` (seed absent, d'un autre type, non
    complet, ou entrées modifiées à la reprise), `ProvenanceInvalide` (amorces illisibles),
    `GabaritInvalide`, `ConfigurationInvalide` ; `SlmspError` pour un run déjà complet.
    """
    if (seed_run_id is None) == (reprendre_run_id is None):
        raise ValueError("seed_run_id ou reprendre_run_id attendu (exactement un)")
    if not 0 <= surplus <= 1 or tours_outils_max < 1:
        raise ValueError("surplus dans [0, 1] et tours_outils_max >= 1 attendus")
    racine = Path(racine).resolve()
    if chemin_outils is None:
        chemin_outils = racine_projet() / "config" / "outils-mcp.toml"
    outils = Path(chemin_outils).resolve()
    gabarits = _gabarits(generateur)  # GabaritInvalide au pré-vol
    outils_sha256 = charger_config(outils).tools_list_sha256

    if reprendre_run_id is not None:
        seed_run_id = seed_du_run(reprendre_run_id, racine=racine)
    assert seed_run_id is not None
    if seed_run_id != generateur.seed_run_id:
        raise ManifesteInvalide(
            f"Générateur construit sur le seed {generateur.seed_run_id}, run sur {seed_run_id}"
        )
    seed = _ouvrir_seed(seed_run_id, racine)
    entrees = _entrees(seed, outils, generateur)

    if reprendre_run_id is None:
        amorces = _amorces(seed, racine)
        plan, comptes_plan = planifier(
            amorces,
            gabarits=gabarits,
            volumes=volumes,
            surplus=surplus,
            outils_sha256=outils_sha256,
            urls_protegees=proteges.urls,
            amorces_protegees=proteges.amorces_sha256,
            recherche=recherche,
        )
        index_version = (
            recherche.version
            if recherche is not None and any(s.passages is not None for s in plan)
            else None
        )
        run = nouveau_run(
            TYPE_RUN,
            "generate",
            {
                "seed_run_id": seed_run_id,
                "commit_gel": commit_gel,
                "volumes": dict(volumes),
                "surplus": surplus,
                "tours_outils_max": tours_outils_max,
                "index_version": index_version,
                "comptes_plan": comptes_plan,
            },
            parents=[seed_run_id],
            entrees=entrees,
            racine=racine,
            index_version=index_version,
        )
        run.ecrire(
            NOM_PLAN,
            b"".join(json_canonique(s.model_dump(mode="json")) + b"\n" for s in plan),
        )
        deja: set[str] = set()
    else:
        existant = ouvrir_run(reprendre_run_id, racine=racine)
        ecarts = sorted(
            nom
            for nom, chemin in entrees.items()
            if existant.manifeste.entrees.get(nom) != sha256_fichier(chemin)
        )
        if ecarts or set(existant.manifeste.entrees) != set(entrees):
            raise ManifesteInvalide(
                f"run {reprendre_run_id} : entrées modifiées depuis sa création "
                f"({', '.join(ecarts) or 'liste des entrées'}) : reprise refusée"
            )
        # Le plan et ses réglages sont ceux de la création (`surplus` est sans effet ici).
        comptes_plan = existant.manifeste.config.get("comptes_plan")
        plan = _plan_du_run(existant, comptes_plan)  # avant toute écriture
        index_version = existant.manifeste.config.get("index_version")
        tours_outils_max = int(existant.manifeste.config.get("tours_outils_max", tours_outils_max))
        run, deja = reprendre(reprendre_run_id, fichier=NOM_BRUT, cle="session_id", racine=racine)
        deja |= {
            str(ligne["session_id"])
            for ligne in run.lire_jsonl(NOM_ABANDONS)
            if isinstance(ligne, dict) and "session_id" in ligne
        }

    for session in plan:
        if session.passages is not None:
            passages.definir(session.session_id, [passage_depuis_plan(p) for p in session.passages])
    executeur = ExecuteurSessions(
        ContexteSessions(
            generateur=generateur,
            journal=journal_pour(
                USAGE_GENERATION,
                generateur.client.config,
                generateur.client.dossier_journaux,
                lecteur="data",
            ),
            racine=racine,
            run=run,
            ouvrir_outils=ouvrir_outils,
            proteges=proteges,
            chemin_outils=outils,
            tours_outils_max=tours_outils_max,
            index_version=index_version,
        )
    )
    return _executer_plan(run, plan, deja, executeur, comptes_plan, consigner)


def _executer_plan(
    run: Run,
    plan: Sequence[SessionPlanifiee],
    deja: set[str],
    executeur: ExecuteurSessions,
    comptes_plan: Any,
    consigner: Callable[[str], None],
) -> ResultatGeneration:
    taches = _bilan_vide(plan)
    statut, motif = "complet", None
    incidents = 0
    try:
        for session in plan:
            if session.session_id in deja:
                continue
            ligne = taches[session.tache]
            compteur = Compteur()
            try:
                resultat = executeur.executer(session, compteur)
            except IncidentOutils as exc:
                run.ajouter_jsonl(
                    NOM_INCIDENTS,
                    IncidentSession(
                        session_id=session.session_id,
                        tache=session.tache,
                        type=exc.type,
                        detail=str(exc),
                        appel_ids=compteur.appel_ids,
                    ).model_dump(mode="json"),
                )
                ligne["incidents"] += 1
                incidents += 1
                consigner(f"[{session.rang + 1}/{len(plan)}] {session.session_id} : incident")
                continue
            finally:
                _cumuler(ligne, compteur)
            if isinstance(resultat, SessionBrute):
                run.ajouter_jsonl(NOM_BRUT, resultat.model_dump(mode="json"))
                ligne["completes"] += 1
                etat = "ok"
            else:
                assert isinstance(resultat, AbandonSession)
                run.ajouter_jsonl(NOM_ABANDONS, resultat.model_dump(mode="json"))
                ligne["abandons"][resultat.motif] = ligne["abandons"].get(resultat.motif, 0) + 1
                etat = f"abandon ({resultat.motif})"
            consigner(f"[{session.rang + 1}/{len(plan)}] {session.session_id} : {etat}")
    except BudgetEpuise as exc:
        statut, motif = "partiel-budget", str(exc)
    except PrealableNonSatisfait as exc:
        statut, motif = "partiel-erreur", f"conditions Mistral à revérifier : {exc}"
    except (ErreurApiMistral, ModeleMistralRefuse) as exc:
        statut, motif = "partiel-erreur", f"{type(exc).__name__} : {exc}"
    except KeyboardInterrupt:
        _clore(run, "interrompu", "interruption clavier", taches, comptes_plan)
        raise
    except BaseException as exc:
        _clore(run, "partiel-erreur", f"{type(exc).__name__} : {exc}", taches, comptes_plan)
        raise
    else:
        if incidents:
            statut = "partiel-erreur"
            motif = f"{incidents} session(s) en incident MCP, à reprendre"
    bilan = _clore(run, statut, motif, taches, comptes_plan)
    return ResultatGeneration(run=run, statut=statut, bilan=bilan)
