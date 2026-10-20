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

`taches` (story S5) limite le plan de génération à ces Tâches ; avec `completer_depuis`, les
sessions closes des autres Tâches (lignes de `plan.jsonl`, `brut.jsonl`, `abandons.jsonl` et
amorces dérivées qu'elles citent) sont reprises telles quelles d'un run `data-generate` du même
seed, sans aucun appel : le run produit est un jeu complet pour `validate`, `filter` et `build`.
Le run consigne le modèle demandé du Générateur (`modele_generateur`) et s'il est une
préversion (`generateur_preversion`).

`reprendre_run_id` reprend un run en ajout seul : le plan est relu, les SHA du seed, des
gabarits et de `config/outils-mcp.toml` sont revérifiés (`ManifesteInvalide` si l'un a
changé, avant toute écriture), et les sessions présentes dans `brut.jsonl` ou
`abandons.jsonl` ne sont pas rejouées. Un seul écrivain par run.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.budget.tarifs import cout_pire_cas
from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run, reprendre
from slmsp.core.canonique import json_canonique, sha256_fichier, sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import (
    BudgetEpuise,
    ConfigurationInvalide,
    ManifesteInvalide,
    ProvenanceInvalide,
    TarifInconnu,
)
from slmsp.core.gabarits import GabaritInvalide, GabaritValide
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
    NOM_AMORCES_DERIVEES,
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
from slmsp.mistral.client import MODE, ErreurApiMistral, ModeleMistralRefuse
from slmsp.mistral.generateur import (
    CARACTERES_PAR_TOKEN,
    EMPLACEMENT_PASSAGES,
    EMPLACEMENTS_RESERVES,
    TACHES_OUTILLEES,
    Generateur,
    PrealableNonSatisfait,
    reponse_reutilisable,
)
from slmsp.mistral.journal import USAGE_GENERATION, JournalMistral, journal_pour

__all__ = [
    "CHAINES",
    "ORDRE_TACHES",
    "TYPE_RUN",
    "ResultatGeneration",
    "SourcePassages",
    "estimer_plan",
    "lancer_generation",
    "modele_generateur_du_run",
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


def _origine(amorce: Amorce, par_id: Mapping[str, Amorce]) -> tuple[Any, ...]:
    if amorce.auteur_contenu == "config":
        # Paramètre tiré par graine : même groupe que l'amorce à laquelle il est lié.
        liee = par_id.get(amorce.lie_a or "")
        if liee is None or liee.auteur_contenu == "config":
            return ("config", amorce.lie_a)
        return _origine(liee, par_id)
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
    par_id = {amorce.amorce_id: amorce for amorce in amorces}
    par_origine: dict[tuple[Any, ...], list[Amorce]] = {}
    for amorce in utiles:
        par_origine.setdefault(_origine(amorce, par_id), []).append(amorce)
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
        attendus = [nom for nom in premier.emplacements if nom not in EMPLACEMENTS_RESERVES]
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


def modele_generateur_du_run(run_id: str, *, racine: str | Path | None = None) -> str | None:
    """Modèle du Générateur consigné par le run `data-generate` `run_id` (story S5), `None`
    pour un run antérieur (lève `ManifesteInvalide`)."""
    seed_du_run(run_id, racine=racine)  # type de run contrôlé
    modele = ouvrir_run(run_id, racine=racine).manifeste.config.get("modele_generateur")
    return modele if isinstance(modele, str) else None


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


@dataclass(frozen=True)
class _Reprises:
    """Sessions closes reprises d'un run `data-generate` source (story S5), sans appel."""

    run_id: str
    sessions: list[SessionPlanifiee]
    bruts: list[dict[str, Any]]
    abandons: list[dict[str, Any]]
    derivees: list[dict[str, Any]]
    index_version: str | None
    non_closes: Counter[str]
    """Par Tâche reprise, sessions planifiées du run source sans brut ni abandon (incident,
    arrêt) : ni reprises ni régénérées, comptées au plan et signalées (revue S5)."""


def _reprises(source_id: str, seed_run_id: str, taches: Collection[str], racine: Path) -> _Reprises:
    """Sessions closes du run `source_id` dont la Tâche n'est pas dans `taches`.

    Le run source doit être un run `data-generate` terminé du même seed ; sinon
    `ManifesteInvalide`. Une session planifiée mais non close (ni brut ni abandon) n'est pas
    reprise : elle est comptée dans `non_closes`.
    """
    source = ouvrir_run(source_id, racine=racine)
    if source.type != TYPE_RUN:
        raise ManifesteInvalide(f"run {source_id} : type {source.type!r}, {TYPE_RUN} attendu")
    if source.statut_courant() == "en_cours":
        raise ManifesteInvalide(f"run {source_id} encore en cours : reprise refusée")
    seed_source = source.manifeste.config.get("seed_run_id")
    if seed_source != seed_run_id:
        raise ManifesteInvalide(f"run {source_id} : seed {seed_source!r}, {seed_run_id} attendu")
    plan = _plan_du_run(source, source.manifeste.config.get("comptes_plan"))
    try:
        bruts = [
            SessionBrute.model_validate(ligne).model_dump(mode="json")
            for ligne in source.lire_jsonl(NOM_BRUT)
        ]
        abandons = [
            AbandonSession.model_validate(ligne).model_dump(mode="json")
            for ligne in source.lire_jsonl(NOM_ABANDONS)
        ]
    except (ValidationError, ValueError):
        raise ManifesteInvalide(
            f"run {source_id} : {NOM_BRUT} ou {NOM_ABANDONS} illisible"
        ) from None
    bruts = [ligne for ligne in bruts if ligne["tache"] not in taches]
    abandons = [ligne for ligne in abandons if ligne["tache"] not in taches]
    closes = {ligne["session_id"] for ligne in (*bruts, *abandons)}
    citees = {amorce_id for ligne in bruts for amorce_id in ligne["amorces_derivees"]}
    derivees = [
        ligne
        for ligne in source.lire_jsonl(NOM_AMORCES_DERIVEES)
        if isinstance(ligne, dict) and ligne.get("amorce_id") in citees
    ]
    if {ligne["amorce_id"] for ligne in derivees} != citees:
        raise ManifesteInvalide(f"run {source_id} : amorce dérivée citée introuvable")
    sessions = [session for session in plan if session.session_id in closes]
    non_closes = Counter(
        s.tache for s in plan if s.tache not in taches and s.session_id not in closes
    )
    return _Reprises(
        run_id=source_id,
        sessions=sessions,
        bruts=bruts,
        abandons=abandons,
        derivees=derivees,
        index_version=source.manifeste.config.get("index_version"),
        non_closes=non_closes,
    )


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


def appels_journalises(
    journal: JournalMistral,
    session_id: str,
    modele: str | None = None,
    max_tokens: Callable[[str], int | None] | None = None,
) -> int:
    """Appels `ok` avec réponse déjà journalisés pour `session_id` (réutilisés à la reprise) ;
    avec `modele`, ceux qui l'ont demandé seulement (story S5). Même règle que la reprise
    (story C2) : arrêt `stop` ou `tool_calls` seulement et, avec `max_tokens` (gabarit_id →
    max_tokens courant), même `max_tokens` journalisé."""
    if not journal.chemin.is_file():
        return 0
    return sum(
        1
        for ligne in journal.appels_session(session_id)
        if ligne.statut == "ok"
        and ligne.reponse_brute is not None
        and reponse_reutilisable(
            ligne.requete,
            ligne.reponse_brute,
            max_tokens(ligne.gabarit_id) if max_tokens and ligne.gabarit_id else None,
        )
        and (modele is None or ligne.modele_demande == modele)
    )


def _max_tokens_session(generateur: Generateur, tache: str) -> Callable[[str], int | None]:
    """`max_tokens` courant d'un gabarit pour `tache` (`None` si le gabarit est illisible :
    la ligne journalisée n'est alors pas comparée, `reponse_reutilisable` garde le filtre
    sur la raison de fin)."""

    def lire(gabarit_id: str) -> int | None:
        try:
            return generateur.max_tokens(gabarit_id, tache)
        except GabaritInvalide:  # estimation seulement : la reprise recontrôle
            return None

    return lire


def estimer_plan(
    plan: Sequence[SessionPlanifiee],
    generateur: Generateur,
    *,
    deja: set[str],
    textes_amorces: Mapping[str, str],
    tours_outils_max: int,
    journalises: Callable[[str], int],
) -> dict[str, dict[str, Any]]:
    """Appels prévus et coût pire cas par gabarit, pour les sessions du plan hors `deja`.

    Une session fait un appel par gabarit de sa chaîne ; une Tâche outillée (RD) en fait au
    plus `tours_outils_max + 1` (un par tour d'outils, plus la réponse finale ou l'appel qui
    dépasse). Les `journalises(session_id)` premiers appels d'une session, déjà journalisés,
    ne sont pas repayés. Coût d'un appel au tarif du modèle demandé (`budget.tarifs`) : sortie
    au `max_tokens` du gabarit (pire cas), entrée **estimée** par les caractères de la
    consigne, des amorces, des passages et, pour une Tâche outillée, du schéma `tools` envoyé
    à chaque appel, plus les sorties pire cas des appels précédents de la session. Les
    résultats d'outils RD et l'enveloppe des messages ne sont pas comptés (taille non bornée
    a priori) : l'entrée n'est pas un pire cas, l'affichage le dit, et le registre de budget
    reste le garde-fou. `cout_pire_cas_eur` vaut `None` si le modèle n'a pas de tarif.
    """
    registre = generateur.client.registre
    modele = generateur.client.config.modele
    estimation: dict[str, dict[str, Any]] = {}
    gabarits_lus: dict[tuple[str, str], tuple[int, int]] = {}  # (id, tâche) : (consigne, max)
    schema_outils: int | None = None
    for session in plan:
        if session.session_id in deja:
            continue
        gabarits = list(session.gabarits)
        base = sum(len(textes_amorces.get(a, "")) for a in session.amorce_ids)
        base += sum(len(p.texte) for p in session.passages or [])
        if session.tache in TACHES_OUTILLEES:
            gabarits = gabarits[:1] * (tours_outils_max + 1)
            if schema_outils is None:
                schema_outils = len(json_canonique(generateur.outils()).decode("utf-8"))
            base += schema_outils
        faits = journalises(session.session_id)
        sorties = 0
        for rang, ref in enumerate(gabarits):
            cle = (ref.id, session.tache)
            if cle not in gabarits_lus:
                gabarits_lus[cle] = (
                    len(generateur.gabarit(ref.id, session.tache).consigne),
                    generateur.max_tokens(ref.id, session.tache),
                )
            consigne, max_tokens = gabarits_lus[cle]
            entree = math.ceil((consigne + base) / CARACTERES_PAR_TOKEN) + sorties
            sorties += max_tokens
            if rang < faits:
                continue
            ligne = estimation.setdefault(
                ref.id, {"appels": 0, "max_tokens": max_tokens, "cout_pire_cas_eur": 0.0}
            )
            ligne["appels"] += 1
            try:
                cout = cout_pire_cas(
                    registre.tarifs,
                    modele,
                    MODE,
                    entree,
                    max_tokens,
                    registre.config.majoration_entree,
                )
            except TarifInconnu:
                ligne["cout_pire_cas_eur"] = None
            else:
                if ligne["cout_pire_cas_eur"] is not None:
                    ligne["cout_pire_cas_eur"] += cout
    return estimation


def _afficher_estimation(
    estimation: Mapping[str, Mapping[str, Any]], consigner: Callable[[str], None]
) -> None:
    for gabarit_id, ligne in estimation.items():
        cout = ligne["cout_pire_cas_eur"]
        consigner(
            f"estimation {gabarit_id} : {ligne['appels']} appels au plus "
            f"(max_tokens {ligne['max_tokens']}), coût estimé "
            + ("tarif inconnu" if cout is None else f"{cout:.4f} €")
        )
    couts = [ligne["cout_pire_cas_eur"] for ligne in estimation.values()]
    total = "tarif inconnu" if None in couts else f"{sum(couts):.4f} €"
    consigner(
        f"estimation totale : {sum(ligne['appels'] for ligne in estimation.values())} appels, "
        f"coût estimé {total} (sorties au max_tokens ; entrée estimée, hors résultats "
        "d'outils RD et enveloppe ; le registre de budget reste le garde-fou)"
    )


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
    taches: Collection[str] | None = None,
    completer_depuis: str | None = None,
) -> ResultatGeneration:
    """Crée (`seed_run_id`) ou reprend (`reprendre_run_id`) un run `data-generate`.

    `generateur` est construit sur le seed du run avec `rendre_passages=passages`.
    Lève, sans rien écrire : `ManifesteInvalide` (seed absent, d'un autre type, non
    complet, ou entrées modifiées à la reprise), `ProvenanceInvalide` (amorces illisibles),
    `GabaritInvalide`, `ConfigurationInvalide` ; `SlmspError` pour un run déjà complet.

    `taches` (nouveau run seulement) : Tâches à générer ; `completer_depuis` (exige `taches`) :
    run `data-generate` du même seed dont les sessions closes des autres Tâches sont reprises.
    """
    if (seed_run_id is None) == (reprendre_run_id is None):
        raise ValueError("seed_run_id ou reprendre_run_id attendu (exactement un)")
    if taches is not None:
        taches = frozenset(taches)
        inconnues = sorted(taches - set(ORDRE_TACHES))
        if not taches or inconnues:
            raise ValueError(f"taches : Tâches inconnues ou liste vide ({', '.join(inconnues)})")
    if (taches is not None or completer_depuis is not None) and reprendre_run_id is not None:
        raise ValueError("taches et completer_depuis valent pour un nouveau run seulement")
    if completer_depuis is not None and taches is None:
        raise ValueError("completer_depuis exige taches")
    modele = generateur.client.config.modele
    preversion = generateur.client.config.preversion is not None
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
        reprises = (
            None
            if completer_depuis is None
            else _reprises(completer_depuis, seed_run_id, taches or (), racine)
        )
        amorces = _amorces(seed, racine)
        plan, comptes_plan = planifier(
            amorces,
            gabarits=gabarits,
            volumes=volumes
            if taches is None
            else {t: v for t, v in volumes.items() if t in taches},
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
        if reprises is not None:
            if index_version is None and any(s.passages is not None for s in reprises.sessions):
                index_version = reprises.index_version
            for session in reprises.sessions:
                plan.append(session.model_copy(update={"rang": len(plan)}))
            for tache in ORDRE_TACHES:
                if tache not in (taches or ()):
                    n = sum(1 for s in reprises.sessions if s.tache == tache)
                    comptes_plan[tache] = {
                        "planifiees": n,
                        "reprises": n,
                        "non_closes_source": reprises.non_closes[tache],
                    }
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
                "modele_generateur": modele,
                "generateur_preversion": preversion,
                "taches": None if taches is None else sorted(taches),
                "completer_depuis": completer_depuis,
            },
            parents=[seed_run_id] if reprises is None else [seed_run_id, reprises.run_id],
            entrees=entrees,
            racine=racine,
            index_version=index_version,
        )
        run.ecrire(
            NOM_PLAN,
            b"".join(json_canonique(s.model_dump(mode="json")) + b"\n" for s in plan),
        )
        deja: set[str] = set()
        if reprises is not None:
            for nom, lignes in (
                (NOM_BRUT, reprises.bruts),
                (NOM_ABANDONS, reprises.abandons),
                (NOM_AMORCES_DERIVEES, reprises.derivees),
            ):
                for ligne in lignes:
                    run.ajouter_jsonl(nom, ligne)
            deja = {s.session_id for s in reprises.sessions}
            consigner(f"{len(deja)} session(s) reprise(s) du run {reprises.run_id}, sans appel")
            if reprises.non_closes:
                detail = ", ".join(f"{t} {n}" for t, n in sorted(reprises.non_closes.items()))
                consigner(
                    f"attention : {sum(reprises.non_closes.values())} session(s) non close(s) "
                    f"du run {reprises.run_id} ni reprise(s) ni régénérée(s) ({detail})"
                )
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
        enregistre = existant.manifeste.config.get("modele_generateur")
        if enregistre is not None and enregistre != modele:
            raise ManifesteInvalide(
                f"run {reprendre_run_id} : généré par {enregistre!r}, Générateur sur "
                f"{modele!r} : reprise refusée"
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
    journal = journal_pour(
        USAGE_GENERATION,
        generateur.client.config,
        generateur.client.dossier_journaux,
        lecteur="data",
    )
    taches = {session.session_id: session.tache for session in plan}
    estimation = estimer_plan(
        plan,
        generateur,
        deja=deja,
        textes_amorces={a.amorce_id: a.texte for a in _amorces(seed, racine)},
        tours_outils_max=tours_outils_max,
        journalises=lambda session_id: appels_journalises(
            journal, session_id, modele, _max_tokens_session(generateur, taches[session_id])
        ),
    )
    _afficher_estimation(estimation, consigner)  # avant le premier appel
    executeur = ExecuteurSessions(
        ContexteSessions(
            generateur=generateur,
            journal=journal,
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
