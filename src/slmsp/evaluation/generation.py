"""Phase génération du banc : run `eval-generation`, une ligne `Generation` par item.

`lancer_generation` vérifie d'abord le manifeste du jeu (`gel.verifier_manifeste`, code 4 ;
`calibrage` est admis sans manifeste, essai de fumée), lit le jeu, résout le modèle, prend
le verrou GPU en `cuda`, monte le Harnais d'évaluation (`fabrique`, par défaut
`assemblage.ouvrir_harnais`), puis crée le run et traite chaque item sous
`assemblage.sans_reseau()`. Chaque item passe par la seule voie `core.items.vers_requete`
→ `harness.prompts.entree_de_requete` → `AssistantService.repondre`, avec le décodage de la
section `[generation]` de `config/evaluation.toml` (glouton, graine fixe). Une erreur d'item
laisse un évènement `Erreur` en fin de trace et le run continue ; le statut final est
`complet`, `partiel-erreur` (au moins une ligne en erreur) ou `interrompu` (exception hors
item, relancée). Une sortie coupée au plafond `max_tokens` ou par le garde-fou
anti-boucle du Harnais (`Fin(raison="boucle")`) reste `ok` et porte `tronquee = true`.

`reprendre_generation` complète le même dossier en ajout seul : les items déjà présents
dans `generations.jsonl` (en erreur compris) sont sautés. Elle refuse un run dont les
options de décodage inscrites diffèrent de la configuration courante.

Modèle distant (`distant:<slug>`, story 17.1) : aucun verrou GPU ni `llama-server` de
génération (`assemblage.ouvrir_harnais_distant`) ; `plafond_generation_eur` est obligatoire
(refusé pour les autres références) ; la boucle tourne sous `sans_reseau` avec le seul hôte
du fournisseur. Chaque appel laisse un relevé dans `appels-distants.jsonl` (modèle,
hébergeur effectif, quantification, `finish_reason`, usage, coût, délais). Une erreur
fatale (budget, plafond du run, clé, configuration) interrompt le run (reprenable). La
reprise rejoue les items dont la dernière ligne n'est pas `ok` ; la dernière ligne d'un
item fait foi. Le manifeste porte `quantification`, `variante_llamacpp`, template et tag
llama.cpp à `null`, la fiche distante (SHA dans `entrees.modele`) et `profil_reseau =
eval-distant`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import AbstractContextManager, ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Final

from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run, reprendre
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.evenements import (
    AppelOutil,
    Erreur,
    Evenement,
    Fin,
    Jeton,
    Sources,
    depuis_dict,
    vers_dict,
)
from slmsp.core.items import VERSION_CALIBRAGE, ItemBase, Jeu, lire_jeu, vers_requete
from slmsp.core.schemas.generation import AppelCanonique, Generation, SortieCanonique
from slmsp.core.var import verrou_gpu
from slmsp.evaluation import config as cfg
from slmsp.evaluation.assemblage import (
    HarnaisEvaluation,
    ouvrir_harnais,
    ouvrir_harnais_distant,
    sans_reseau,
)
from slmsp.evaluation.gel import verifier_manifeste
from slmsp.evaluation.modele_distant import (
    ModeleDistant,
    est_distant,
    resoudre_distant,
    sha256_fichier,
)
from slmsp.evaluation.modele_ref import ModeleResolu, resoudre
from slmsp.harness.config import VERSION_HARNAIS
from slmsp.harness.prompts import construire_messages, entree_de_requete
from slmsp.inference.serveur import VARIANTES

LOGGER: Final = logging.getLogger("slmsp.evaluation")

TYPE_RUN: Final = "eval-generation"
FICHIER_GENERATIONS: Final = "generations.jsonl"
FICHIER_APPELS_DISTANTS: Final = "appels-distants.jsonl"

CODE_ERREUR_EVALUATION: Final = "erreur-evaluation"
"""Code de l'`Erreur` d'un item dont le traitement échoue hors du flux du Harnais."""

Fabrique = Callable[[ModeleResolu, str, Path], AbstractContextManager[HarnaisEvaluation]]
FabriqueDistante = Callable[
    [ModeleDistant, Path, float, float], AbstractContextManager[HarnaisEvaluation]
]
"""`(modele, racine, plafond_eur, cout_deja_eur)` → Harnais d'un modèle distant."""
Rapporteur = Callable[[Generation, int, int], None]
"""`rapporter(generation, rang, total)` après l'écriture de chaque ligne (rang à partir de 1)."""


@dataclass
class RapportGeneration:
    """Bilan d'un lancement ou d'une reprise de la phase génération."""

    run: Run
    ok: int = 0
    erreur: int = 0
    sautes: int = 0
    tronquees: int = 0
    """Items de cette session coupés au plafond `max_tokens` (comptés aussi dans `ok`)."""
    statut: str = "en_cours"
    durees_ms: list[int] = field(default_factory=list)
    connexions_bloquees: list[str] = field(default_factory=list)
    """Cibles réseau refusées par `sans_reseau` pendant la boucle des items."""

    @property
    def duree_moyenne_ms(self) -> float | None:
        return sum(self.durees_ms) / len(self.durees_ms) if self.durees_ms else None


# --- Un item ----------------------------------------------------------------------------------


def _fusionner_jetons(trace: Sequence[Evenement]) -> list[Evenement]:
    fusion: list[Evenement] = []
    for evenement in trace:
        if isinstance(evenement, Jeton) and fusion and isinstance(fusion[-1], Jeton):
            fusion[-1] = Jeton(texte=fusion[-1].texte + evenement.texte)
        else:
            fusion.append(evenement)
    return fusion


def sortie_canonique(trace: Sequence[Evenement]) -> SortieCanonique:
    """Texte (jetons concaténés), appels d'outils sans id, sources du dernier `Sources`."""
    sources = [e for e in trace if isinstance(e, Sources)]
    return SortieCanonique(
        texte="".join(e.texte for e in trace if isinstance(e, Jeton)),
        appels_outils=[
            AppelCanonique(nom=e.nom, arguments=e.arguments)
            for e in trace
            if isinstance(e, AppelOutil)
        ],
        sources=list(sources[-1].sources) if sources else [],
    )


def _contenu(harnais: HarnaisEvaluation, code: str, entree: str | dict[str, Any]) -> str:
    """Contenu du message `user` : l'entrée texte, ou le `user` rendu de l'entrée objet."""
    if isinstance(entree, str):
        return entree
    return construire_messages(harnais.taches.tache(code), entree)[1]["content"]


def options_llm(config: cfg.ConfigEvaluation | None = None) -> dict[str, Any]:
    """Options de décodage de `[generation]` (défaut : `config/evaluation.toml` du projet)."""
    return (config if config is not None else cfg.charger_evaluation()).generation.options_llm()


RAISONS_TRONQUEES: Final = frozenset({"longueur", "boucle"})
"""Raisons de `Fin` d'une sortie coupée : plafond de tokens ou garde-fou anti-boucle."""


def tronquee(trace: Sequence[Evenement]) -> bool | None:
    """`True` si un `Fin` de la trace a la raison `longueur` ou `boucle` (coupure du garde-fou
    anti-boucle, story 16.3) ; `None` sans aucun `Fin`."""
    fins = [e for e in trace if isinstance(e, Fin)]
    if not fins:
        return None
    return any(fin.raison in RAISONS_TRONQUEES for fin in fins)


def generer_item(
    harnais: HarnaisEvaluation,
    jeu: Jeu,
    item: ItemBase,
    options: Mapping[str, Any] | None = None,
) -> Generation:
    """Génère la sortie de `item` par le Harnais complet ; ne lève pas pour une erreur d'item.

    `options` : décodage transmis au client LLM (défaut : `options_llm()`).
    """
    decodage = dict(options) if options is not None else options_llm()
    trace: list[Evenement] = []
    debut = perf_counter()
    try:
        service = harnais.service(item, jeu, trace.append)
        requete = vers_requete(item)
        entree = entree_de_requete(requete)
        messages = [{"role": "user", "content": _contenu(harnais, requete.tache, entree)}]
        for evenement in service.repondre(requete.tache, messages, {"entree": entree, **decodage}):
            trace.append(evenement)
    except Exception as exc:
        LOGGER.error("item %s : %s : %s", item.id, type(exc).__name__, exc)
        trace.append(Erreur(code=CODE_ERREUR_EVALUATION, message=f"{type(exc).__name__} : {exc}"))
    duree_ms = max(0, round((perf_counter() - debut) * 1000))
    if not trace or not isinstance(trace[-1], (Fin, Erreur)):
        trace.append(Erreur(code=CODE_ERREUR_EVALUATION, message="flux terminé sans Fin"))
    erreur = any(isinstance(e, Erreur) for e in trace)
    return Generation(
        item_id=item.id,
        tache=item.code,
        statut="erreur" if erreur else "ok",
        sortie_canonique=sortie_canonique(trace),
        trace=[vers_dict(e) for e in _fusionner_jetons(trace)],
        duree_ms=duree_ms,
        tronquee=tronquee(trace),
    )


# --- Run --------------------------------------------------------------------------------------


def _racine(racine: str | Path | None) -> Path:
    return (Path(racine) if racine is not None else racine_projet()).resolve()


def _verifier_jeu(version: str, racine: Path) -> None:
    """Manifeste revérifié (code 4) ; `calibrage` est admis sans manifeste."""
    if version != VERSION_CALIBRAGE:
        verifier_manifeste(version, racine)


def _selection(jeu: Jeu, items: Iterable[str] | None) -> list[ItemBase]:
    """Items demandés, dans l'ordre du jeu ; lève `ValueError` pour un id inconnu."""
    if items is None:
        return list(jeu.items)
    demandes = list(dict.fromkeys(items))
    connus = {item.id for item in jeu.items}
    inconnus = [i for i in demandes if i not in connus]
    if inconnus:
        raise ValueError(f"item(s) inconnu(s) du jeu {jeu.version} : {', '.join(inconnus)}")
    if not demandes:
        raise ValueError("aucun item demandé")
    retenus = set(demandes)
    return [item for item in jeu.items if item.id in retenus]


def _entrees(jeu: Jeu, modele: ModeleResolu | ModeleDistant, racine: Path) -> dict[str, Path]:
    projet = racine_projet()
    config = projet / "config"
    entrees: dict[str, Path] = {}
    if jeu.version == VERSION_CALIBRAGE:
        entrees["items_jeu"] = jeu.chemin_items
    else:
        entrees["manifeste_jeu"] = cfg.chemin_manifeste(racine, jeu.version)
    entrees.update(
        outils_mcp=config / "outils-mcp.toml",
        taches=config / "taches.toml",
        harnais=config / "harnais.toml",
        modele=(
            modele.chemin
            if isinstance(modele, ModeleDistant)
            else config / "modeles" / f"{modele.slug}.toml"
        ),
    )
    return entrees


def _verrou(variante: str, pile: ExitStack, modele: ModeleResolu) -> None:
    if variante == "cuda":
        pile.enter_context(verrou_gpu(commande=f"slmsp eval run {modele.ref} (cuda)"))


def _boucle(
    run: Run,
    harnais: HarnaisEvaluation,
    jeu: Jeu,
    selection: Sequence[ItemBase],
    deja: set[str],
    rapporter: Rapporteur | None,
    options: Mapping[str, Any],
) -> RapportGeneration:
    """Traite les items absents de `deja`, puis inscrit le statut final."""
    rapport = RapportGeneration(run=run)
    courant: str | None = None
    try:
        with sans_reseau(harnais.hotes_autorises, harnais.profil_reseau) as bloquees:
            for rang, item in enumerate(selection, start=1):
                if item.id in deja:
                    rapport.sautes += 1
                    continue
                courant = item.id
                generation = generer_item(harnais, jeu, item, options)
                if harnais.distant is not None:
                    generation = _suivi_distant(run, harnais.distant, generation)
                run.ajouter_jsonl(FICHIER_GENERATIONS, generation)
                if generation.statut == "ok":
                    rapport.ok += 1
                else:
                    rapport.erreur += 1
                if generation.tronquee:
                    rapport.tronquees += 1
                rapport.durees_ms.append(generation.duree_ms)
                if rapporter is not None:
                    rapporter(generation, rang, len(selection))
        rapport.connexions_bloquees = list(bloquees)
        retenus = {item.id for item in selection}
        derniers = _derniers_statuts(run)
        en_erreur = {i for i, statut in derniers.items() if i in retenus and statut != "ok"}
        rapport.statut = "partiel-erreur" if en_erreur else "complet"
        run.terminer(rapport.statut)
    except BaseException as exc:
        if harnais.distant is not None and courant is not None:
            # Interruption en cours d'item : les appels déjà réglés restent comptés à la
            # reprise (`_cout_deja`).
            releves, _ = harnais.distant.vider()
            for releve in releves:
                run.ajouter_jsonl(FICHIER_APPELS_DISTANTS, {"item_id": courant, **releve})
        if rapport.statut == "en_cours":
            rapport.statut = "interrompu"
            run.terminer("interrompu", motif=f"{type(exc).__name__} : {exc}"[:500])
        raise
    return rapport


def _derniers_statuts(run: Run) -> dict[str, Any]:
    """Statut de la dernière ligne de chaque item de `generations.jsonl` (elle fait foi)."""
    derniers: dict[str, Any] = {}
    for ligne in run.lire_jsonl(FICHIER_GENERATIONS):
        if isinstance(ligne, dict) and isinstance(ligne.get("item_id"), str):
            derniers[ligne["item_id"]] = ligne.get("statut")
    return derniers


def _suivi_distant(run: Run, distant: Any, generation: Generation) -> Generation:
    """Relevés des appels de l'item, erreur fatale relevée, code d'erreur d'item reporté."""
    releves, code = distant.vider()
    for releve in releves:
        run.ajouter_jsonl(FICHIER_APPELS_DISTANTS, {"item_id": generation.item_id, **releve})
    if distant.erreur_fatale is not None:
        raise distant.erreur_fatale
    if code is None or generation.statut == "ok":
        return generation
    trace = list(generation.trace)
    for rang in range(len(trace) - 1, -1, -1):
        if isinstance(depuis_dict(trace[rang]), Erreur):
            message = depuis_dict(trace[rang]).message  # type: ignore[union-attr]
            trace[rang] = vers_dict(Erreur(code=code, message=message))
            break
    return generation.model_copy(update={"trace": trace})


def _cout_deja(run: Run) -> float:
    """Coût réel déjà réglé des appels distants du run (`appels-distants.jsonl`)."""
    return sum(
        float(ligne["cout_eur"])
        for ligne in run.lire_jsonl(FICHIER_APPELS_DISTANTS)
        if isinstance(ligne, dict) and isinstance(ligne.get("cout_eur"), int | float)
    )


def _verifier_plafond(plafond: float) -> None:
    if not plafond > 0:
        raise ValueError(f"plafond de génération invalide : {plafond!r} (EUR > 0)")


def _verifier_distant(
    quantification: str | None, variante: str | None, plafond: float | None
) -> float:
    if quantification is not None:
        raise ValueError("--quantification sans objet pour un modèle distant:")
    if variante is not None:
        raise ValueError("--variante sans objet pour un modèle distant:")
    if plafond is None:
        raise ValueError("--plafond-generation EUR requis pour un modèle distant:")
    _verifier_plafond(plafond)
    return plafond


def lancer_generation(
    modele_ref: str,
    quantification: str | None,
    jeu: str,
    *,
    variante: str | None = None,
    items: Iterable[str] | None = None,
    racine: str | Path | None = None,
    fabrique: Fabrique = ouvrir_harnais,
    rapporter: Rapporteur | None = None,
    config: cfg.ConfigEvaluation | None = None,
    plafond_generation_eur: float | None = None,
    fabrique_distante: FabriqueDistante = ouvrir_harnais_distant,
) -> RapportGeneration:
    """Phase génération de `modele_ref` × `quantification` sur le jeu `jeu` (voir le module).

    `config` : réglages de `config/evaluation.toml` (défaut : lus dans le projet).
    `variante` : `cpu` par défaut (local). `plafond_generation_eur` : obligatoire pour
    `distant:`, refusé sinon. Lève `ManifesteInvalide` (jeu altéré, code 4) avant toute
    autre action, `ValueError` (usage : variante, référence, quantification, plafond ou item
    inconnus), `ConfigurationInvalide` (modèle, `evaluation.toml`), `RessourceOccupee` (GPU).
    """
    base = _racine(racine)
    distant = est_distant(modele_ref)
    if distant:
        plafond = _verifier_distant(quantification, variante, plafond_generation_eur)
    else:
        if plafond_generation_eur is not None:
            raise ValueError("--plafond-generation réservé à un modèle distant:")
        variante = variante or "cpu"
        if variante not in VARIANTES:
            raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")
    _verifier_jeu(jeu, base)
    reglages = (config if config is not None else cfg.charger_evaluation()).generation
    jeu_lu = lire_jeu(jeu, base)
    selection = _selection(jeu_lu, items)
    if distant:
        distant_resolu = resoudre_distant(modele_ref)
        with fabrique_distante(distant_resolu, base, plafond, 0.0) as harnais:
            run = _nouveau_run_distant(harnais, jeu_lu, selection, distant_resolu, base, reglages)
            run_options = reglages.options_llm()
            return _boucle(run, harnais, jeu_lu, selection, set(), rapporter, run_options)
    assert variante is not None and quantification is not None
    modele = resoudre(modele_ref, quantification, racine=base)
    with ExitStack() as pile:
        _verrou(variante, pile, modele)
        harnais = pile.enter_context(fabrique(modele, variante, base))
        run = _nouveau_run(harnais, jeu_lu, selection, modele, variante, base, reglages)
        return _boucle(run, harnais, jeu_lu, selection, set(), rapporter, reglages.options_llm())


def _nouveau_run(
    harnais: HarnaisEvaluation,
    jeu: Jeu,
    selection: Sequence[ItemBase],
    modele: ModeleResolu,
    variante: str,
    racine: Path,
    reglages: cfg.ConfigGeneration,
) -> Run:
    config = {
        "phase": "generation",
        "options_llm": reglages.options_llm(),
        "items": [item.id for item in selection],
        "serveur": harnais.description,
        "chat_template_force": modele.config.chat_template_force,
        "precision_gguf": modele.precision,
        "profil_reseau": harnais.profil_reseau,
        "version_harnais": VERSION_HARNAIS,
    }
    if modele.lora is not None:
        config["lora"] = {"echelle": modele.echelle_lora, "gguf": modele.lora.name}
    return nouveau_run(
        TYPE_RUN,
        modele.slug_run,
        config,
        entrees=_entrees(jeu, modele, racine),
        graine=reglages.graine,
        racine=racine,
        modele_ref=modele.ref,
        quantification=modele.quantification,
        variante_llamacpp=variante,
        llamacpp_tag=harnais.llamacpp_tag,
        chat_template_sha256=harnais.chat_template_sha256,
        jeu_version=jeu.version,
        index_version=harnais.index_version,
    )


def _nouveau_run_distant(
    harnais: HarnaisEvaluation,
    jeu: Jeu,
    selection: Sequence[ItemBase],
    modele: ModeleDistant,
    racine: Path,
    reglages: cfg.ConfigGeneration,
) -> Run:
    config = {
        "phase": "generation",
        "options_llm": reglages.options_llm(),
        "items": [item.id for item in selection],
        "serveur": harnais.description,
        "profil_reseau": harnais.profil_reseau,
        "version_harnais": VERSION_HARNAIS,
        "modele_distant": {
            "slug": modele.slug,
            "sha256": modele.sha256,
            **modele.fiche.model_dump(mode="json"),
        },
    }
    return nouveau_run(
        TYPE_RUN,
        modele.slug_run,
        config,
        entrees=_entrees(jeu, modele, racine),
        graine=reglages.graine,
        racine=racine,
        modele_ref=modele.ref,
        jeu_version=jeu.version,
        index_version=harnais.index_version,
    )


def reprendre_generation(
    run_id: str,
    *,
    racine: str | Path | None = None,
    fabrique: Fabrique = ouvrir_harnais,
    rapporter: Rapporteur | None = None,
    modele_ref: str | None = None,
    quantification: str | None = None,
    jeu: str | None = None,
    variante: str | None = None,
    config: cfg.ConfigEvaluation | None = None,
    plafond_generation_eur: float | None = None,
    fabrique_distante: FabriqueDistante = ouvrir_harnais_distant,
) -> RapportGeneration:
    """Reprend le run `run_id` en ajout seul (items déjà présents sautés).

    Relit `run.json` (modèle, quantification, variante, jeu, items) ; `modele_ref`,
    `quantification`, `jeu` et `variante`, s'ils sont donnés, doivent lui être égaux.
    Revérifie le manifeste du jeu et refuse des options de décodage (`config`, défaut :
    `config/evaluation.toml`), un chat template servi, une version d'Index ou un tag
    llama.cpp différents de ceux du run. Lève `SlmspError` pour un run `complet`,
    `ManifesteInvalide` pour un run introuvable, d'un autre type, d'un autre modèle, d'un
    autre décodage, d'un autre template, d'un autre Index ou d'un autre llama.cpp.
    Modèle distant : `plafond_generation_eur` obligatoire (`ValueError`), fiche distante
    inchangée (`ManifesteInvalide`), items dont la dernière ligne n'est pas `ok` rejoués.
    """
    base = _racine(racine)
    run = ouvrir_run(run_id, racine=base)
    manifeste = run.manifeste
    if manifeste.type != TYPE_RUN:
        raise ManifesteInvalide(f"run {run_id} de type {manifeste.type!r}, pas {TYPE_RUN!r}")
    if run.statut_courant() == "complet":
        raise SlmspError(f"run {run_id} déjà complet : rien à reprendre")
    attendus = {
        "modele_ref": (modele_ref, manifeste.modele_ref),
        "quantification": (quantification, manifeste.quantification),
        "jeu": (jeu, manifeste.jeu_version),
        "variante": (variante, manifeste.variante_llamacpp),
    }
    ecarts = [
        f"{nom} : {demande!r} au lieu de {inscrit!r}"
        for nom, (demande, inscrit) in attendus.items()
        if demande is not None and demande != inscrit
    ]
    if ecarts:
        raise ManifesteInvalide(f"run {run_id} différent de la demande : " + " ; ".join(ecarts))
    distant = est_distant(manifeste.modele_ref)
    if distant and plafond_generation_eur is None:
        raise ValueError("--plafond-generation EUR requis pour reprendre un modèle distant:")
    if not distant and plafond_generation_eur is not None:
        raise ValueError("--plafond-generation réservé à un modèle distant:")
    if (
        manifeste.modele_ref is None
        or (not distant and manifeste.quantification is None)
        or manifeste.jeu_version is None
        or (not distant and manifeste.variante_llamacpp is None)
        or not isinstance(manifeste.config.get("items"), list)
    ):
        raise ManifesteInvalide(f"run {run_id} : run.json incomplet pour une reprise")
    _verifier_jeu(manifeste.jeu_version, base)
    options = options_llm(config)
    inscrites = manifeste.config.get("options_llm")
    if inscrites != options:
        raise ManifesteInvalide(
            f"run {run_id} : options de décodage différentes de config/evaluation.toml "
            f"({options}, inscrites {inscrites})"
        )
    jeu_lu = lire_jeu(manifeste.jeu_version, base)
    try:
        selection = _selection(jeu_lu, manifeste.config["items"])
    except ValueError as exc:
        raise ManifesteInvalide(f"run {run_id} : {exc}") from None
    with ExitStack() as pile:
        if distant:
            assert plafond_generation_eur is not None
            modele_distant = resoudre_distant(manifeste.modele_ref)
            inscrit = manifeste.entrees.get("modele")
            if sha256_fichier(modele_distant.chemin) != inscrit:
                raise ManifesteInvalide(
                    f"run {run_id} : fiche {modele_distant.chemin.name} modifiée depuis le run"
                )
            _verifier_plafond(plafond_generation_eur)
            harnais = pile.enter_context(
                fabrique_distante(modele_distant, base, plafond_generation_eur, _cout_deja(run))
            )
        else:
            assert manifeste.quantification is not None
            assert manifeste.variante_llamacpp is not None
            modele = resoudre(manifeste.modele_ref, manifeste.quantification, racine=base)
            _verrou(manifeste.variante_llamacpp, pile, modele)
            harnais = pile.enter_context(fabrique(modele, manifeste.variante_llamacpp, base))
        for libelle, servi, inscrit in (
            ("chat template servi", harnais.chat_template_sha256, manifeste.chat_template_sha256),
            ("index_version", harnais.index_version, manifeste.index_version),
            ("llamacpp_tag", harnais.llamacpp_tag, manifeste.llamacpp_tag),
        ):
            if servi != inscrit:
                raise ManifesteInvalide(
                    f"run {run_id} : {libelle} différent ({servi}, inscrit {inscrit})"
                )
        run, deja = reprendre(run_id, fichier=FICHIER_GENERATIONS, cle="item_id", racine=base)
        if distant:
            deja = {i for i, statut in _derniers_statuts(run).items() if statut == "ok"}
        return _boucle(run, harnais, jeu_lu, selection, deja, rapporter, options)


__all__ = [
    "CODE_ERREUR_EVALUATION",
    "FICHIER_APPELS_DISTANTS",
    "FICHIER_GENERATIONS",
    "TYPE_RUN",
    "RapportGeneration",
    "generer_item",
    "lancer_generation",
    "options_llm",
    "reprendre_generation",
    "sortie_canonique",
    "tronquee",
]
