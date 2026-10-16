"""`slmsp export` : export GGUF d'un Run d'entraînement (story 10.6, FR-35).

    slmsp export --depuis <train_run_id> [--variante cpu|cuda] [--sans-sonde]
    slmsp export --base <slug>            # export témoin : la base par la même chaîne

`train.export.exporter` fusionne, convertit (F16) et quantifie (Q4_K_M) sous `gpu.lock`.
Ce module lui fournit les contrôles de format (`train` ne lit pas les GGUF, AD-24) :

- **bloquant** (CA2) : SHA de `tokenizer.chat_template` embarqué dans chaque GGUF égal à
  celui du tokenizer d'entraînement ;
- **alertes** (note 10.6, C5) : métadonnées différentes du GGUF officiel du même slug
  (architecture, nombre de couches, `tokenizer.ggml.pre`, identifiants bos et eos).

Une fois le run `complet` (CA3) : `ft:<run_id>` est résolu par `evaluation.modele_ref` pour
`f16` et `q4_k_m`, puis la sonde d'outils (items RD-001 et RD-002, soit R-001 et R-002
d'H-TOOLS) passe sur le Q4_K_M ; son bilan va dans `sonde-outils.json` du run d'export.
La sonde reprend `gpu.lock` elle-même en variante `cuda`, après la libération par l'export.

Codes : 0 export complet et sonde valide (ou `--sans-sonde`), 1 contrôle bloquant ou sonde
non valide, 5 GPU occupé.
"""

from __future__ import annotations

import argparse
import hashlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any, Final

from slmsp.core.artefacts import Run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import dossier_modeles, racine_ecriture
from slmsp.core.erreurs import CodeSortie
from slmsp.fetch.verifications import GgufInvalide, lire_metadonnees_gguf
from slmsp.inference.serveur import VARIANTES, charger_config_modele
from slmsp.train import export as train_export

CLE_TEMPLATE: Final = "tokenizer.chat_template"
CLE_ARCHITECTURE: Final = "general.architecture"
CLES_TOKENIZER: Final = (
    "tokenizer.ggml.pre",
    "tokenizer.ggml.bos_token_id",
    "tokenizer.ggml.eos_token_id",
)
SUFFIXES_ARCHITECTURE: Final = ("block_count", "embedding_length", "attention.head_count")
NOM_SONDE: Final = "sonde-outils.json"


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `export`."""
    p = sous_parseurs.add_parser(
        "export",
        help="export GGUF des adaptateurs",
        description="Fusionne l'adaptateur d'un Run d'entraînement en 16 bits, convertit en "
        "GGUF F16 puis quantifie en Q4_K_M (outils du tag de config/llamacpp.toml), contrôle "
        "le chat template embarqué et re-teste le tool calling sur le Q4_K_M.",
    )
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--depuis", metavar="TRAIN_RUN_ID", help="run d'entraînement complet")
    source.add_argument("--base", metavar="SLUG", help="export témoin de la base, sans adaptateur")
    p.add_argument(
        "--variante",
        choices=VARIANTES,
        default="cpu",
        help="variante llama.cpp de la sonde d'outils (défaut : cpu)",
    )
    p.add_argument("--sans-sonde", action="store_true", help="ne pas lancer la sonde d'outils")
    p.add_argument(
        "--python",
        type=Path,
        default=None,
        help="interpréteur du convertisseur (défaut : le courant, environnement train)",
    )
    p.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine des runs (défaut : racine d'écriture du projet)",
    )
    p.set_defaults(func=_exporter)


def sha_template(chemin: Path) -> str | None:
    """SHA-256 de `tokenizer.chat_template` embarqué dans le GGUF `chemin` (`None` : absent)."""
    valeur = lire_metadonnees_gguf(chemin, [CLE_TEMPLATE]).get(CLE_TEMPLATE)
    if not isinstance(valeur, str):
        return None
    return hashlib.sha256(valeur.encode("utf-8")).hexdigest()


def metadonnees(chemin: Path) -> dict[str, Any]:
    """Métadonnées comparées au GGUF officiel (architecture, couches, tokenizer)."""
    architecture = lire_metadonnees_gguf(chemin, [CLE_ARCHITECTURE]).get(CLE_ARCHITECTURE)
    cles = [*CLES_TOKENIZER]
    if isinstance(architecture, str):
        cles += [f"{architecture}.{suffixe}" for suffixe in SUFFIXES_ARCHITECTURE]
    return {CLE_ARCHITECTURE: architecture, **lire_metadonnees_gguf(chemin, cles)}


def gguf_officiel(slug: str) -> Path | None:
    """GGUF Q4_K_M officiel du slug (`config/modeles/<slug>.toml`), s'il est présent."""
    fichier = charger_config_modele(slug).gguf_pour("q4_k_m")
    if fichier is None:
        return None
    chemin = dossier_modeles() / slug / "gguf" / PurePosixPath(fichier.fichier).name
    return chemin if chemin.is_file() else None


def controler_format(slug: str) -> Any:
    """Contrôles de format injectés dans `train.export.exporter` (CA2 et note 10.6, C5)."""

    def controler(run: Run, export: Mapping[str, Any]) -> dict[str, Any]:
        attendu = export["chat_template_sha256_attendu"]
        bloquants: list[str] = []
        alertes: list[str] = []
        templates: dict[str, str | None] = {}
        for quantification, nom in export["fichiers"].items():
            if quantification == "hf":
                continue
            try:
                templates[quantification] = sha_template(run.dossier / nom)
            except GgufInvalide as exc:
                bloquants.append(f"{nom} illisible : {exc}")
                continue
            if templates[quantification] != attendu:
                bloquants.append(
                    f"{nom} : chat template embarqué {templates[quantification]} ≠ "
                    f"tokenizer d'entraînement {attendu}"
                )
        officiel = gguf_officiel(slug)
        comparaison: dict[str, Any] = {"officiel": officiel.name if officiel else None}
        if officiel is None:
            alertes.append(f"GGUF officiel de {slug} absent : métadonnées non comparées")
        elif not bloquants:
            exporte = metadonnees(run.dossier / export["fichiers"]["q4_k_m"])
            reference = metadonnees(officiel)
            ecarts = {
                cle: {"export": exporte.get(cle), "officiel": reference.get(cle)}
                for cle in sorted(exporte.keys() | reference.keys())
                if exporte.get(cle) != reference.get(cle)
            }
            comparaison["ecarts"] = ecarts
            if ecarts:
                alertes.append(f"métadonnées différentes du GGUF officiel : {', '.join(ecarts)}")
        return {
            "bloquants": bloquants,
            "alertes": alertes,
            "templates": templates,
            "metadonnees": comparaison,
        }

    return controler


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_ecriture()).resolve()


def _exporter(args: argparse.Namespace) -> int:
    # Import différé : `evaluation` (harnais, juge) n'est chargé qu'après l'export.
    from slmsp.evaluation import modele_ref  # noqa: PLC0415

    racine = _racine(args)
    if args.depuis is not None:
        source = train_export.source_depuis_run(args.depuis, racine=racine)
    else:
        charger_config_modele(args.base)  # slug connu (ConfigurationInvalide)
        source = train_export.source_temoin(args.base)
    run = train_export.exporter(
        source,
        racine=racine,
        python=args.python,
        controles=controler_format(source.slug),
    )
    statut = run.statut_courant()
    print(f"export : run {run.run_id} {statut}")
    if statut != "complet":
        print(f"slmsp : export {run.run_id} non complet (voir export.json)")
        return int(CodeSortie.ERREUR)
    ref = f"ft:{run.run_id}"
    for quantification in modele_ref.QUANTIFICATIONS:
        resolu = modele_ref.resoudre(ref, quantification, racine=racine)
        print(f"{ref} {quantification} : {resolu.gguf.name} (précision {resolu.precision})")
    if args.sans_sonde:
        return int(CodeSortie.SUCCES)
    return _sonder(run, ref, args.variante, racine)


def _sonder(run: Run, ref: str, variante: str, racine: Path) -> int:
    from slmsp.evaluation import sonde_outils  # noqa: PLC0415

    rapport = sonde_outils.sonder(ref, variante=variante, racine=racine)
    bilan = {
        "sonde_run_id": rapport.run.run_id,
        "items": list(sonde_outils.ITEMS_SONDE),
        "quantification": sonde_outils.QUANTIFICATION,
        "variante": variante,
        "valide": rapport.valide,
        "protocole_recommande": rapport.protocole_recommande,
        "statut": rapport.statut,
        "motif": rapport.motif,
    }
    run.ecrire(NOM_SONDE, json_canonique(bilan) + b"\n")
    etat = "valide" if rapport.valide else f"non valide ({rapport.motif})"
    print(f"sonde d'outils sur {ref} q4_k_m : {etat} ; run {rapport.run.run_id}")
    if not rapport.valide:
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)


__all__ = ["controler_format", "enregistrer", "gguf_officiel", "metadonnees", "sha_template"]
