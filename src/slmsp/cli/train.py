"""`slmsp train {sonde-env, run}` : environnement d'entraînement et Runs (epic 10).

`sonde-env` mesure H-WIN-TRAIN (story 10.1) : sous le verrou `gpu.lock`, il ouvre un run
`train-sonde` (slug = le Modèle de base) sous `<racine>/runs/train-sonde/<run_id>/`, y
inscrit `sonde.json` (contrôles matériels et du modèle, mesures par longueur),
`methodes.json` (méthodes disponibles et replis) et, avec `--unsloth`, `unsloth.json`
(pas tenté dans `envs/unsloth/` en sous-processus). Le run se termine `complet`,
`degrade` (repli appliqué) ou `partiel-erreur` (code 1). GPU occupé : code 5.

Le run est versionné : sa configuration porte la provenance du code de la sonde
(`provenance_code` : empreintes SHA-256 et fichiers non commités, y compris non suivis,
que `git_modifie` de `run.json` ignore), et aucun artefact ne contient de chemin absolu
de la machine (`environnement.chemin_portable`). L'entrée du sous-processus Unsloth, qui
a besoin de chemins absolus, est écrite sous `SLMSP_VAR_DIR/unsloth/`.

`run --config <toml> [--reprendre <run_id>]` lance un Run d'entraînement (story 10.4,
`slmsp.train.run`) : code 0 complet, 1 bloqué (jeu absent) ou en échec, 4 jeu ou manifeste
invalide, 5 GPU occupé.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import appliquer_environnement_impose, racine_projet
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide
from slmsp.core.var import verrou_gpu
from slmsp.inference.serveur import charger_config_modele
from slmsp.train import environnement
from slmsp.train.run import executer as executer_run

TYPE_RUN = "train-sonde"
NOM_SONDE = "sonde.json"
NOM_METHODES = "methodes.json"
NOM_UNSLOTH = "unsloth.json"
NOM_ENTREE_UNSLOTH = "unsloth-entree.json"
NOM_JOURNAL_UNSLOTH = "unsloth.log"
NOM_LOG = "log.jsonl"
DOSSIER_ENTRAINEUR = "entraineur"
DOSSIER_ENTRAINEUR_UNSLOTH = "entraineur-unsloth"

FICHIERS_CODE = (
    "src/slmsp/train/environnement.py",
    "src/slmsp/cli/train.py",
    "envs/unsloth/sonde.py",
    "envs/unsloth/pyproject.toml",
    "envs/unsloth/uv.lock",
)
"""Code qui détermine les mesures de la sonde (provenance consignée dans `run.json`)."""


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `train` et ses sous-commandes."""
    parseur = sous_parseurs.add_parser(
        "train",
        help="runs d'entraînement",
        description="Environnement d'entraînement (H-WIN-TRAIN) et Runs d'entraînement.",
    )
    cibles = parseur.add_subparsers(dest="cible", metavar="<cible>", required=True)

    p = cibles.add_parser(
        "sonde-env",
        help="sonde H-WIN-TRAIN : pas QLoRA sur tokens aléatoires, sous gpu.lock",
        description="Contrôle CUDA, bf16, bitsandbytes et TRL + PEFT par quelques pas "
        "d'entraînement sur des tokens aléatoires, longueur par longueur.",
    )
    p.add_argument(
        "--modele",
        default=environnement.SLUG_REPLI_BF16,
        metavar="SLUG",
        help=f"Modèle de base (défaut : {environnement.SLUG_REPLI_BF16})",
    )
    p.add_argument(
        "--methode",
        choices=environnement.METHODES_SONDE,
        default="qlora",
        help="qlora (nf4 4 bits + LoRA, défaut) ou lora (bf16)",
    )
    p.add_argument(
        "--precision-base",
        choices=(*environnement.PRECISIONS_BASE, environnement.PRECISION_LES_DEUX),
        default="fp32-kbit",
        help="précision de la base quantifiée : fp32-kbit (prepare_model_for_kbit_training, "
        "défaut), bf16 (sans ce cast) ou les-deux (chaque longueur dans les deux variantes)",
    )
    p.add_argument(
        "--longueurs",
        type=_longueurs,
        default=list(environnement.LONGUEURS_DEFAUT),
        metavar="N[,N...]",
        help="longueurs de séquence, dans l'ordre (défaut : 512,1024,2048,4096)",
    )
    p.add_argument(
        "--pas",
        type=int,
        default=environnement.PAS_DEFAUT,
        help=f"pas mesurés par longueur, après 1 pas de chauffe "
        f"(défaut : {environnement.PAS_DEFAUT})",
    )
    p.add_argument(
        "--unsloth",
        action="store_true",
        help="tenter aussi le pas équivalent dans envs/unsloth/, en sous-processus",
    )
    p.add_argument(
        "--longueur-unsloth",
        type=int,
        default=None,
        metavar="N",
        help="longueur du pas Unsloth (défaut : la première de --longueurs)",
    )
    p.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine des écritures runs/ (défaut : racine du projet)",
    )
    p.set_defaults(func=_sonde_env)

    p = cibles.add_parser(
        "run",
        help="Run d'entraînement décrit par un TOML (config/runs/<nom>.toml)",
        description="Lance un Run d'entraînement (méthode, modèle, hyperparamètres, graine "
        "et version du jeu fixés par le TOML) sous gpu.lock, ou le reprend sur son dernier "
        "checkpoint.",
    )
    p.add_argument("--config", type=Path, required=True, metavar="TOML", help="TOML du Run")
    p.add_argument(
        "--reprendre",
        default=None,
        metavar="RUN_ID",
        help="reprendre ce run sur son dernier checkpoint (même configuration résolue)",
    )
    p.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine des lectures data/train/ et des écritures runs/ (défaut : racine du projet)",
    )
    p.set_defaults(func=_run)


def _longueurs(texte: str) -> list[int]:
    try:
        valeurs = [int(partie) for partie in texte.replace(" ", "").split(",") if partie]
    except ValueError:
        raise argparse.ArgumentTypeError(f"longueurs invalides : {texte!r}") from None
    if not valeurs or any(v < 8 for v in valeurs):
        raise argparse.ArgumentTypeError("longueurs : au moins une, chacune ≥ 8")
    return valeurs


def _run(args: argparse.Namespace) -> int:
    return executer_run(args.config, reprendre_run=args.reprendre, racine=args.racine)


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_projet()).resolve()


def _ecrire_json(run: Run, nom: str, contenu: Any) -> None:
    run.ecrire(nom, json_canonique(environnement.json_sur(contenu)) + b"\n")


def _git(projet: Path, *arguments: str) -> str | None:
    try:
        resultat = subprocess.run(
            ["git", "-c", "core.quotepath=off", *arguments],
            cwd=projet,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return resultat.stdout if resultat.returncode == 0 else None


def provenance_code(projet: Path | None = None) -> dict[str, Any]:
    """Provenance du code de la sonde : commit, empreintes et fichiers non commités.

    `run.json` relève `git_commit` et `git_modifie`, mais ce dernier ignore les fichiers
    non suivis : un run produit par du code pas encore commité y paraît issu du commit
    parent. Ici, `non_commites` liste aussi les fichiers non suivis de `FICHIERS_CODE`, et
    `sha256` identifie le code exact. Hors dépôt git : `git_commit` et `non_commites` valent
    `None`.
    """
    projet = projet if projet is not None else racine_projet()
    empreintes: dict[str, str | None] = {}
    for relatif in FICHIERS_CODE:
        chemin = projet / relatif
        empreintes[relatif] = (
            hashlib.sha256(chemin.read_bytes()).hexdigest() if chemin.is_file() else None
        )
    depot = (projet / ".git").exists()
    commit = _git(projet, "rev-parse", "HEAD") if depot else None
    etat = (
        _git(projet, "status", "--porcelain", "--untracked-files=all", "--", *FICHIERS_CODE)
        if depot
        else None
    )
    non_commites = (
        sorted(ligne[3:].strip() for ligne in etat.splitlines() if ligne.strip())
        if etat is not None
        else None
    )
    return {
        "git_commit": commit.strip() if commit else None,
        "non_commites": non_commites,
        "code_commite": None if non_commites is None else non_commites == [],
        "sha256": empreintes,
    }


def _ecrire_entree_unsloth(run: Run, entree: dict[str, Any]) -> Path:
    """`<SLMSP_VAR_DIR>/unsloth/entree-<run_id>.json` (état machine, non versionné)."""
    dossier = environnement.dossier_travail_unsloth()
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"entree-{run.run_id}.json"
    chemin.write_bytes(json_canonique(entree) + b"\n")
    return chemin


def _sonde_env(args: argparse.Namespace) -> int:
    appliquer_environnement_impose()
    slug = args.modele
    if args.pas < 1:
        raise ConfigurationInvalide("--pas : au moins 1 pas mesuré")
    # Slug connu de config/modeles/, puis refus d'un modèle non entraînable (Bonsai, D8)
    # avant toute lecture des poids et avant le verrou, avec ou sans --unsloth.
    fiche = charger_config_modele(slug)
    environnement.exiger_entrainable(fiche, slug)
    if args.unsloth:  # envs/unsloth/sonde.py charge AutoModelForCausalLM
        environnement.exiger_sans_unsloth_multimodal(fiche, slug)
    racine = _racine(args)
    dossier = environnement.dossier_poids(slug, racine=racine)
    config_modele = environnement.lire_config_modele(dossier, racine=racine)
    # Refus avant le verrou (vision sans `multimodal`, Mamba, FP8).
    environnement.controler_config_modele(config_modele, slug, multimodal=fiche.multimodal)
    provenance = provenance_code()

    commande = f"slmsp train sonde-env --modele {slug} --methode {args.methode}"
    with verrou_gpu(commande=commande):
        run = nouveau_run(
            TYPE_RUN,
            slug,
            {
                "sous_commande": "sonde-env",
                "modele": slug,
                "methode": args.methode,
                "precision_base": args.precision_base,
                "longueurs": list(args.longueurs),
                "pas": args.pas,
                "pas_chauffe": environnement.PAS_CHAUFFE,
                "unsloth": bool(args.unsloth),
                "dossier_poids": environnement.chemin_portable(dossier, racine=racine),
                "arguments_specifiques": environnement.arguments_specifiques(config_modele),
                "provenance_code": provenance,
            },
            graine=environnement.GRAINE,
            racine=racine,
        )
        print(f"run {run.run_id} : {run.dossier}", flush=True)
        try:
            code = _executer_sonde(
                args, run, slug, dossier, config_modele, racine, multimodal=fiche.multimodal
            )
        except KeyboardInterrupt:
            run.terminer("interrompu", "arrêt demandé")
            raise
        except Exception as exc:
            run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
            raise
    return code


def _executer_sonde(
    args: argparse.Namespace,
    run: Run,
    slug: str,
    dossier: Path,
    config_modele: dict[str, Any],
    racine: Path,
    *,
    multimodal: str | None = None,
) -> int:
    def journal(message: str) -> None:
        run.ajouter_jsonl(NOM_LOG, {"message": message})
        print(message, flush=True)

    resultat = environnement.sonder(
        slug=slug,
        dossier=dossier,
        config_modele=config_modele,
        methode=args.methode,
        longueurs=args.longueurs,
        pas=args.pas,
        graine=environnement.GRAINE,
        precision_base=args.precision_base,
        multimodal=multimodal,
        dossier_travail=run.dossier / DOSSIER_ENTRAINEUR,
        journal=journal,
        racine=racine,
    )
    _ecrire_json(run, NOM_SONDE, resultat.sonde)

    unsloth: dict[str, Any] | None = None
    statut, motif = resultat.statut, resultat.motif
    if args.unsloth and resultat.statut != "partiel-erreur":
        longueur = args.longueur_unsloth or args.longueurs[0]
        entree = environnement.entree_unsloth(
            dossier=dossier,
            dossier_sortie=run.dossier / DOSSIER_ENTRAINEUR_UNSLOTH,
            longueur=longueur,
            pas=args.pas,
            graine=environnement.GRAINE,
            vocab=int(config_modele.get("vocab_size") or 0),
            specifiques=environnement.arguments_specifiques(config_modele),
        )
        # Entrée réelle (chemins absolus) hors du run versionné ; copie portable dans le run.
        chemin_entree = _ecrire_entree_unsloth(run, entree)
        _ecrire_json(run, NOM_ENTREE_UNSLOTH, environnement.entree_portable(entree, racine=racine))
        journal(f"Unsloth : pas tenté dans envs/unsloth (longueur {longueur})")
        unsloth = environnement.sonder_unsloth(
            chemin_entree, journal=run.dossier / NOM_JOURNAL_UNSLOTH, racine=racine
        )
        _ecrire_json(run, NOM_UNSLOTH, unsloth)
        if unsloth.get("ok"):
            journal("Unsloth : pas réussi")
        else:
            journal(f"Unsloth : échec, repli TRL + PEFT seuls ({unsloth.get('erreur')})")
            if statut == "complet":
                statut = "degrade"
            replis = "sans Unsloth : TRL + PEFT seuls"
            motif = replis if not motif else f"{motif} ; {replis}"
    elif args.unsloth:
        unsloth = {"ok": False, "erreur": "sonde TRL + PEFT en échec : Unsloth non tenté"}
        _ecrire_json(run, NOM_UNSLOTH, unsloth)

    methodes = environnement.methodes_disponibles(
        slug=slug,
        methode_demandee=args.methode,
        methode_effective=resultat.methode_effective,
        pas_reussi=resultat.pas_reussi,
        motif_quantification=resultat.motif_quantification,
        unsloth=unsloth,
        multimodal=multimodal,
    )
    _ecrire_json(run, NOM_METHODES, methodes)
    run.terminer(statut, motif)

    for mesure in resultat.sonde.get("mesures", []):
        print(
            f"{mesure.get('statut', '?'):<12} longueur {mesure.get('longueur')} "
            f"({mesure.get('precision_base', '?')}) : "
            f"perte {mesure.get('perte')}, VRAM réservée {mesure.get('max_memory_reserved')}, "
            f"{mesure.get('tokens_par_s')} tokens/s"
        )
    print(
        f"train sonde-env : run {run.run_id} {statut} ; méthodes disponibles : "
        f"{', '.join(methodes['disponibles']) or 'aucune'}"
    )
    if statut == "partiel-erreur":
        print(f"slmsp : sonde en échec : {motif}", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)
