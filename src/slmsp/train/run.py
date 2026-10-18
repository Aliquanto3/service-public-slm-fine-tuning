"""Run d'entraînement piloté par un TOML (story 10.4, AD-18, AD-21, AD-26).

`executer` enchaîne, pour `config/runs/<nom>.toml` :

1. validation (`RunConfig`, plan de la méthode, contraintes du modèle) ;
2. jeu construit (`chargement.charger_jeu`, recontrôle des `appel_ids`) ; sans jeu, un run
   est créé puis terminé `partiel-erreur` avec un motif « bloqué : … » ;
3. pré-tokenisation par `train.masque` (paires rendues par le chat template pour ORPO), puis
   invariants de campagne (version du jeu et run `data-build` de son MANIFEST, graine,
   longueur maximale, SHA du chat template, version du masque), comparés à ceux des runs
   `train` déjà enregistrés pour la campagne (avant le verrou, puis de nouveau sous le
   verrou) ;
4. sous `gpu.lock` : run `runs/train/<run_id>/` (`run_id` = date, nom du TOML, 4 hex),
   graine posée avant le chargement et l'adaptateur (neuf à chaque Run), entraînement avec
   checkpoints sous `checkpoints/` (jamais de `save_total_limit`), coûts (`couts.json`,
   avec config, graine et environnement), adaptateur sous `adaptateur/`.

`--reprendre <run_id>` rouvre le même run (même config résolue exigée) et reprend sur son
dernier checkpoint complet ; les coûts du segment vont dans `couts-2.json`, etc. Si
l'adaptateur a déjà été sauvegardé en entier (arrêt avant la fin du run), la reprise termine
le run sans réentraîner.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import (
    ArtefactExistant,
    Run,
    chemin_autorise,
    nouveau_run,
    ouvrir_run,
    reprendre,
)
from slmsp.core.canonique import json_canonique
from slmsp.core.config import appliquer_environnement_impose, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide
from slmsp.core.var import verrou_gpu
from slmsp.inference.serveur import charger_config_modele
from slmsp.train import chargement, environnement, methodes, variante_unsloth
from slmsp.train.config import (
    PRECISION_BASE_DEFAUT,
    RunConfig,
    charger_config_couts,
    charger_run_config,
)
from slmsp.train.couts import creer_callback, ecrire_mesures
from slmsp.train.masque import VERSION_MASQUE, empreinte_decoupage

TYPE_RUN: Final = "train"
DOSSIER_CHECKPOINTS: Final = "checkpoints"
DOSSIER_ADAPTATEUR: Final = "adaptateur"
NOM_JEU: Final = "jeu.json"
NOM_ENTRAINEMENT: Final = "entrainement.jsonl"
NOM_LOG: Final = "log.jsonl"
NOM_NOYAUX: Final = "noyaux.json"
PREFIXE_BLOQUE: Final = "bloqué : "
VERSION_RENDU_OUTILS: Final = 1
"""Rendu des outils (R7) : `tools` du fichier de config, arguments décodés. Absent = avant R7."""
CLES_INVARIANTS: Final = (
    "jeu_version",
    "jeu_build",
    "graine",
    "longueur_max",
    "chat_template_sha256",
    "version_masque",
    "decoupage_masque",
    "rendu_outils",
    "precision_base",
)
DEFAUTS_INVARIANTS: Final = {"precision_base": PRECISION_BASE_DEFAUT}
"""Valeur d'un invariant absent d'un run antérieur (la clé n'est écrite que hors défaut)."""
DEROGATION_ORPO: Final = (
    "ORPO déroge au protocole de la campagne (FR-34) : paires de préférence "
    "(réponse rejetée générée par le Modèle de base), point de départ = adaptateur SFT"
)
_MOTIF_CHECKPOINT: Final = re.compile(r"^checkpoint-(\d+)$")
FICHIERS_CHECKPOINT: Final = ("trainer_state.json", "optimizer.pt", "scheduler.pt")
"""Écrits par `Trainer._save_checkpoint` (`trainer_state.json` en dernier) : checkpoint complet."""
FICHIERS_ADAPTATEUR: Final = ("adapter_config.json", "adapter_model.safetensors")


def invariants(
    config: RunConfig,
    *,
    jeu_build: str,
    chat_template_sha256: str,
    decoupage_masque: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Éléments qu'une campagne partage (FR-34, AD-18).

    `decoupage_masque` : `masque.empreinte_decoupage` de la fiche du Modèle (mode et bloc
    d'amorce) ; `None` pour le découpage par défaut : la clé est alors absente, comme dans les runs
    antérieurs (`--reprendre` compare la configuration résolue entière).

    Le jeu est identifié par sa version et par le run `data-build` de son MANIFEST, pas par
    le SHA du fichier lu : M4 lit `preferences.jsonl`, M1 à M3 `train.jsonl`, du même build.
    """
    resultat: dict[str, Any] = {
        "jeu_version": config.jeu_version,
        "jeu_build": jeu_build,
        "graine": config.graine,
        "longueur_max": config.longueur_max,
        "chat_template_sha256": chat_template_sha256,
        "version_masque": VERSION_MASQUE,
        "rendu_outils": VERSION_RENDU_OUTILS,
    }
    if config.precision_base != PRECISION_BASE_DEFAUT:  # absente au défaut, comme avant
        resultat["precision_base"] = config.precision_base
    if decoupage_masque is not None:  # absente au défaut : run.json des runs antérieurs intact
        resultat["decoupage_masque"] = dict(decoupage_masque)
    return resultat


def verifier_campagne(
    campagne: str, attendus: Mapping[str, Any], *, racine: str | Path | None = None
) -> list[str]:
    """Compare `attendus` aux invariants des runs `train` de la campagne ; renvoie leurs ids.

    Tout run de la campagne qui a consigné ses invariants compte, quel que soit son statut.
    Lève `ConfigurationInvalide` en citant l'invariant, le run et les deux valeurs.
    """
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    compares: list[str] = []
    for manifeste in sorted((base / "runs" / TYPE_RUN).glob("*/run.json")):
        try:
            run = ouvrir_run(manifeste.parent.name, racine=base)
        except ManifesteInvalide:
            continue
        config = run.manifeste.config
        enregistres = config.get("invariants")
        if config.get("campagne") != campagne or not isinstance(enregistres, Mapping):
            continue
        for cle in CLES_INVARIANTS:
            defaut = DEFAUTS_INVARIANTS.get(cle)
            if enregistres.get(cle, defaut) != attendus.get(cle, defaut):
                raise ConfigurationInvalide(
                    f"campagne {campagne} : « {cle} » diffère du run {run.run_id} "
                    f"({enregistres.get(cle, defaut)!r} enregistré, "
                    f"{attendus.get(cle, defaut)!r} demandé)"
                )
        compares.append(run.run_id)
    return compares


def _complet(dossier: Path, fichiers: tuple[str, ...]) -> bool:
    return all((dossier / nom).is_file() for nom in fichiers)


def _exiger_sft_complet(run_id: str, racine: Path) -> None:
    """Le run `sft_run_id` d'ORPO est un run `train` au statut `complet`."""
    try:
        run = ouvrir_run(run_id, racine=racine)
    except ManifesteInvalide as exc:
        raise ConfigurationInvalide(f"sft_run_id {run_id} : run illisible ({exc})") from None
    if run.type != TYPE_RUN:
        raise ConfigurationInvalide(f"sft_run_id {run_id} : run de type {run.type}, pas train")
    statut = run.statut_courant()
    if statut != "complet":
        raise ConfigurationInvalide(f"sft_run_id {run_id} : run SFT {statut}, pas complet")


def dernier_checkpoint(dossier: Path) -> Path | None:
    """Sous-dossier `checkpoint-<N>` complet de plus grand N, ou `None`.

    Un checkpoint interrompu pendant sa sauvegarde (sans `FICHIERS_CHECKPOINT`) est ignoré :
    la reprise repart du précédent checkpoint complet.
    """
    if not dossier.is_dir():
        return None
    trouves = [
        (int(m.group(1)), enfant)
        for enfant in dossier.iterdir()
        if enfant.is_dir()
        and (m := _MOTIF_CHECKPOINT.fullmatch(enfant.name))
        and _complet(enfant, FICHIERS_CHECKPOINT)
    ]
    return max(trouves)[1] if trouves else None


def _racine(racine: str | Path | None) -> Path:
    return (Path(racine) if racine is not None else racine_projet()).resolve()


def _charger_tokenizer(pile: environnement.Pile, dossier: Path) -> Any:
    tokenizer = pile.transformers.AutoTokenizer.from_pretrained(
        str(dossier), use_fast=True, local_files_only=True
    )
    if getattr(tokenizer, "pad_token", None) is None:
        tokenizer.pad_token = tokenizer.eos_token  # token existant : aucun retaillage
    return tokenizer


def _toml_resolu(config: RunConfig) -> dict[str, Any]:
    """TOML résolu de `run.json` ; `precision_base` et `repli_torch` absentes au défaut
    (reprise des runs d'avant)."""
    toml = config.model_dump(mode="json")
    if toml.get("precision_base") == PRECISION_BASE_DEFAUT:
        del toml["precision_base"]
    if not toml.get("repli_torch"):
        toml.pop("repli_torch", None)
    return toml


def _bloquer(
    nom: str, config: RunConfig, motif: str, *, racine: Path, sortie: Callable[[str], None]
) -> int:
    run = nouveau_run(
        TYPE_RUN,
        nom,
        {"campagne": config.campagne, "toml": _toml_resolu(config)},
        graine=config.graine,
        racine=racine,
        jeu_version=config.jeu_version,
    )
    run.terminer("partiel-erreur", PREFIXE_BLOQUE + motif)
    sortie(f"train run : run {run.run_id} bloqué : {motif}")
    return 1


def _rouvrir(run_id: str, nom: str, resolue: Mapping[str, Any], racine: Path) -> Run:
    run = ouvrir_run(run_id, racine=racine)
    if run.type != TYPE_RUN:
        raise ConfigurationInvalide(f"--reprendre {run_id} : run de type {run.type}, pas train")
    if json_canonique(run.manifeste.config) != json_canonique(dict(resolue)):
        raise ConfigurationInvalide(
            f"--reprendre {run_id} : la configuration résolue diffère de celle du run "
            f"(TOML {nom}.toml, jeu, modèle ou code modifiés) ; lancer un nouveau Run"
        )
    run, _ = reprendre(run_id, fichier=NOM_LOG, cle="evenement", racine=racine)
    return run


def executer(
    chemin_config: str | Path,
    *,
    reprendre_run: str | None = None,
    racine: str | Path | None = None,
    pile: environnement.Pile | None = None,
    journal_mistral: str | Path | None = None,
    cpu: bool = False,
    sortie: Callable[[str], None] = print,
) -> int:
    """Lance (ou reprend) un Run ; renvoie le code de sortie (0 complet, 1 bloqué ou échec).

    `pile`, `journal_mistral` et `cpu` servent aux tests (pile simulée, modèle minuscule).
    """
    appliquer_environnement_impose()
    racine = _racine(racine)
    chemin_config = Path(chemin_config)
    config = charger_run_config(chemin_config)
    nom = chemin_config.stem
    plan = methodes.plan_methode(config.methode)
    if plan.entraineur == "unsloth" and reprendre_run is not None:  # avant toute réouverture
        raise ConfigurationInvalide("--reprendre n'est pas supporté par qlora-unsloth (story 10.5)")
    config_modele = charger_config_modele(config.modele)
    environnement.exiger_entrainable(config_modele, config.modele)
    dossier = environnement.dossier_poids(config.modele, racine=racine)
    config_poids = environnement.lire_config_modele(dossier, racine=racine)
    contraintes = chargement.controler_contraintes(
        config_poids, config.modele, exclure_vision=config_modele.exclure_vision
    )
    # Hybride Gated DeltaNet sans fla : refus avant le chargement de la pile et avant le verrou.
    environnement.exiger_noyaux_gdn(config_poids, config.modele, repli_torch=config.repli_torch)
    specifiques = (
        environnement.arguments_specifiques(config_poids) if plan.entraineur != "orpo" else {}
    )

    fichier = chargement.NOM_PREFERENCES if plan.entraineur == "orpo" else chargement.NOM_TRAIN
    try:
        jeu = chargement.charger_jeu(config.jeu_version, racine=racine, fichier=fichier)
    except chargement.JeuAbsent as exc:
        if reprendre_run is not None:
            raise
        return _bloquer(nom, config, str(exc), racine=racine, sortie=sortie)
    appels = chargement.recontroler_appel_ids(jeu.lignes, journal=journal_mistral, racine=racine)
    if plan.entraineur == "orpo":
        chargement.recontroler_rejected(jeu.lignes, racine=racine)
    adaptateur_sft = None
    if config.sft_run_id is not None:
        # AD-24 étendu (A1, 2026-10-16) : seul `runs/train/<id>/adaptateur/` est lisible ;
        # le run SFT doit être `complet` (comme pour l'export, `source_depuis_run`).
        _exiger_sft_complet(config.sft_run_id, racine)
        adaptateur_sft = chemin_autorise(
            racine / "runs" / TYPE_RUN / config.sft_run_id / DOSSIER_ADAPTATEUR,
            "train",
            racine=racine,
        )
        if not _complet(adaptateur_sft, FICHIERS_ADAPTATEUR):
            raise ConfigurationInvalide(
                f"sft_run_id {config.sft_run_id} : adaptateur SFT absent ou incomplet "
                f"({adaptateur_sft})"
            )

    if pile is None:
        try:
            pile = environnement.charger_pile()
        except (ImportError, OSError) as exc:
            raise ConfigurationInvalide(
                f"pile d'entraînement indisponible ({type(exc).__name__} : {exc}) ; "
                "installer l'extra : uv sync --extra train"
            ) from None
    controle_noyaux = environnement.controler_noyaux_gdn(pile, config_poids)
    environnement.exiger_noyaux_gdn(
        config_poids, config.modele, repli_torch=config.repli_torch, controle=controle_noyaux
    )
    tokenizer = _charger_tokenizer(pile, dossier)
    template_sha = chargement.sha_chat_template(tokenizer)
    exemples: list[dict[str, Any]]
    if plan.entraineur == "orpo":
        exemples, stats = chargement.preparer_preferences(
            tokenizer, jeu.lignes, config_modele=config_modele
        )
    else:
        exemples, stats = chargement.pretokeniser(
            tokenizer, jeu.lignes, longueur_max=config.longueur_max, config_modele=config_modele
        )
    if not exemples:
        raise ManifesteInvalide("aucun exemple supervisé après masque et troncature")
    attendus = invariants(
        config,
        jeu_build=str(jeu.manifeste.get("run_id")),
        chat_template_sha256=template_sha,
        decoupage_masque=empreinte_decoupage(config_modele),
    )
    toml_resolu = _toml_resolu(config)
    resolue: dict[str, Any] = {
        "campagne": config.campagne,
        "toml": toml_resolu,
        "plan": plan.ligne(),
        "invariants": attendus,
        "modele": {
            "slug": config.modele,
            "revision": config_modele.revision,
            "dossier_poids": environnement.chemin_portable(dossier, racine=racine),
            "contraintes": contraintes,
            "chat_template_kwargs": dict(config_modele.chat_template_kwargs),
            "protocole_outils": config_modele.protocole_outils,
        },
        "arguments_specifiques": specifiques,
        "jeu": jeu.ligne(),
        "appel_ids_verifies": appels,
        "derogation": DEROGATION_ORPO if plan.entraineur == "orpo" else None,
    }
    if (decoupage := empreinte_decoupage(config_modele)) is not None:  # absente au défaut
        resolue["modele"]["decoupage_masque"] = decoupage
    if reprendre_run is None:
        verifier_campagne(config.campagne, attendus, racine=racine)

    commande = f"slmsp train run --config {chemin_config.name}"
    with verrou_gpu(commande=commande):
        if reprendre_run is None:
            verifier_campagne(config.campagne, attendus, racine=racine)  # run concurrent
            run = nouveau_run(
                TYPE_RUN,
                nom,
                resolue,
                graine=config.graine,
                racine=racine,
                jeu_version=config.jeu_version,
                chat_template_sha256=template_sha,
            )
            run.ecrire(NOM_JEU, json_canonique({**jeu.ligne(), **stats}) + b"\n")
        else:
            run = _rouvrir(reprendre_run, nom, resolue, racine)
        sortie(f"run {run.run_id} : {run.dossier}")
        try:
            _entrainer(
                run,
                pile,
                config,
                plan,
                dossier=dossier,
                tokenizer=tokenizer,
                exemples=exemples,
                specifiques=specifiques,
                adaptateur_sft=adaptateur_sft,
                config_poids=config_poids,
                controle_noyaux=controle_noyaux,
                reprise=reprendre_run is not None,
                racine=racine,
                cpu=cpu,
            )
        except KeyboardInterrupt:
            run.terminer("interrompu", "arrêt demandé")
            raise
        except BaseException as exc:
            run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
            raise
        run.terminer("complet")
    sortie(f"train run : run {run.run_id} complet")
    return 0


def _ecrire_noyaux(run: Run, controle: Mapping[str, Any] | None) -> None:
    """`noyaux.json` du segment (`noyaux-2.json`, etc. aux reprises : un artefact n'est jamais
    réécrit)."""
    if controle is None:
        return
    rang = 1
    nom = NOM_NOYAUX
    while (run.dossier / nom).exists():
        rang += 1
        nom = f"noyaux-{rang}.json"
    run.ecrire(nom, json_canonique(environnement.json_sur(controle)) + b"\n")


def _entrainer_unsloth(
    run: Run,
    config: RunConfig,
    arguments: Mapping[str, Any],
    *,
    exemples: list[dict[str, Any]],
    tokenizer: Any,
    dossier: Path,
) -> None:
    """Variante Unsloth : mêmes `exemples` (ids et labels de `train.masque`), sous-processus.

    Le `gpu.lock` est déjà pris par `executer`. Coûts, adaptateur et pertes sont archivés
    par `variante_unsloth.entrainer` comme pour les autres méthodes.
    """
    hp = config.hyperparametres
    contexte = {
        "config": run.manifeste.config,
        "graine": run.manifeste.graine,
        "environnement": run.manifeste.environnement.model_dump(mode="json"),
        "run_id": run.run_id,
    }
    variante_unsloth.entrainer(
        run,
        exemples=exemples,
        pad_id=int(tokenizer.pad_token_id),
        dossier_poids=dossier,
        arguments=arguments,
        longueur=config.longueur_max,
        graine=config.graine,
        lora={"r": hp.lora_rang, "alpha": hp.lora_alpha, "dropout": hp.lora_dropout},
        racine=run.dossier.parents[2],
        contexte=contexte,
    )


def _entrainer(
    run: Run,
    pile: environnement.Pile,
    config: RunConfig,
    plan: methodes.PlanMethode,
    *,
    dossier: Path,
    tokenizer: Any,
    exemples: list[dict[str, Any]],
    specifiques: Mapping[str, Any],
    adaptateur_sft: Path | None,
    config_poids: Mapping[str, Any],
    controle_noyaux: Mapping[str, Any] | None = None,
    reprise: bool,
    racine: Path,
    cpu: bool,
) -> None:
    adaptateur = run.dossier / DOSSIER_ADAPTATEUR
    if adaptateur.exists():
        if reprise and _complet(adaptateur, FICHIERS_ADAPTATEUR):
            # Arrêt entre la sauvegarde de l'adaptateur et la fin du run : rien à réentraîner.
            run.ajouter_jsonl(NOM_LOG, {"evenement": "adaptateur-deja-sauvegarde"})
            return
        raise ArtefactExistant(
            f"{adaptateur} existe déjà, incomplet ou hors reprise : examiner le run "
            "(l'adaptateur n'est jamais écrasé)"
        )
    checkpoints = run.dossier / DOSSIER_CHECKPOINTS
    depart = dernier_checkpoint(checkpoints) if reprise else None
    arguments = methodes.arguments_entrainement(
        config,
        plan,
        dossier_checkpoints=checkpoints,
        nb_exemples=len(exemples),
        specifiques=specifiques,
        cpu=cpu,
    )
    affiches = {
        **arguments,
        "output_dir": environnement.chemin_portable(checkpoints, racine=racine),
    }
    run.ajouter_jsonl(
        NOM_ENTRAINEMENT,
        {
            "evenement": "demarrage",
            "reprise": reprise,
            "checkpoint_depart": depart.name if depart is not None else None,
            "arguments": environnement.json_sur(affiches),
        },
    )
    run.ajouter_jsonl(
        NOM_LOG, {"evenement": "demarrage", "checkpoint": getattr(depart, "name", None)}
    )

    if plan.entraineur == "unsloth":
        _entrainer_unsloth(
            run, config, arguments, exemples=exemples, tokenizer=tokenizer, dossier=dossier
        )
        return

    pile.transformers.set_seed(config.graine)  # avant le chargement et l'adaptateur (W4.4)
    modele = methodes.charger_modele(
        pile, dossier, plan, cpu=cpu, precision_base=config.precision_base
    )
    if adaptateur_sft is not None:
        modele = pile.peft.PeftModel.from_pretrained(modele, str(adaptateur_sft), is_trainable=True)
    else:
        modele = methodes.poser_adaptateur(pile, modele, plan, config)
    jeu = pile.datasets.Dataset.from_list(exemples)
    collateur = (
        None
        if plan.entraineur == "orpo"  # ORPOTrainer : collateur de paires par défaut
        else chargement.CollateurMasque(int(tokenizer.pad_token_id), torch=pile.torch)
    )
    callback = creer_callback(charger_config_couts(), base=pile.transformers.TrainerCallback)
    entraineur = methodes.creer_entraineur(
        pile,
        plan,
        modele=modele,
        tokenizer=tokenizer,
        jeu=jeu,
        collateur=collateur,
        arguments=arguments,
        callbacks=[callback],
    )
    if controle_noyaux is not None:
        run.ajouter_jsonl(
            NOM_LOG, {"evenement": "noyaux", **environnement.json_sur(controle_noyaux)}
        )
        if config.repli_torch:
            run.ajouter_jsonl(
                NOM_LOG,
                {
                    "evenement": "alerte",
                    "message": "repli torch (repli_torch = true) : entraînement plus lent, "
                    "noyaux fla non exigés",
                },
            )
    collecte = environnement.CollecteAvertissements()
    try:
        with collecte:
            entraineur.train(resume_from_checkpoint=str(depart) if depart is not None else None)
    finally:
        if controle_noyaux is not None:  # hors run.json : complété des avertissements du pas
            _ecrire_noyaux(
                run,
                environnement.controler_noyaux_gdn(
                    pile, config_poids, avertissements=collecte.messages
                ),
            )
        try:
            mesures = callback.mesures()
        except RuntimeError:  # l'entraînement n'a pas commencé
            mesures = None
        if mesures is not None:
            contexte = {
                "config": run.manifeste.config,
                "graine": run.manifeste.graine,
                "environnement": run.manifeste.environnement.model_dump(mode="json"),
                "run_id": run.run_id,
            }
            ecrire_mesures(run, mesures, contexte)
    entraineur.model.save_pretrained(str(adaptateur))
    run.ajouter_jsonl(NOM_LOG, {"evenement": "adaptateur", "dossier": DOSSIER_ADAPTATEUR})
