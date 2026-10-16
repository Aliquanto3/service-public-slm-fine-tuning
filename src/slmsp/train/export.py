"""Export GGUF d'un Run d'entraînement : fusion 16 bits, F16 puis Q4_K_M (story 10.6, FR-35).

Chaîne (note de conception 10.6, §1) :

1. **Fusion** sur CPU : la base `models/<slug>/hf/` est chargée en fp32, l'adaptateur du run
   `train` (`runs/train/<id>/adaptateur/`, lisible par le lecteur `train` depuis la décision
   A1 du 2026-10-16) est appliqué puis fusionné (`merge_and_unload`), la plage est
   contrôlée (aucun NaN ni infini, max |w| < 65 504), puis le modèle est enregistré en
   **F16** (safetensors) avec le tokenizer de la base, inchangé (AD-19 : « 16 bits » désigne
   le format écrit, le calcul de la fusion se fait en fp32).
   - ORPO : l'adaptateur ORPO continue l'adaptateur SFT (10.4 le charge `is_trainable`), il
     est donc fusionné seul.
   - PiSSA : seul un adaptateur converti en LoRA relatif à la base d'origine est accepté
     (`init_lora_weights` ≠ `pissa` dans `adapter_config.json`).
   - Export témoin (`base=True`) : aucun adaptateur, même chaîne.
2. **Conversion** en `modele-f16.gguf` par `inference.serveur.convertir_hf_vers_gguf`, avec
   `type_sortie="f16"` explicite (le lanceur vaut `bf16` par défaut).
3. **Quantification** en `modele-q4_k_m.gguf` par `inference.serveur.quantifier` (`Q4_K_M`,
   sans imatrix, variante CPU). `train` ne lance aucun processus llama.cpp lui-même (AD-6).

Le run `runs/export/<run_id>/` est créé sous `gpu.lock`, tenu de la fusion à la fin des
contrôles injectés (`controles`, fournis par `cli.export` : `train` ne lit pas les GGUF).
L'espace disque est vérifié avant une écriture de plus de 1 Gio. `export.json` consigne la
chaîne, les précisions réelles (`f16`, `q4_k_m`) et le résultat des contrôles.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import (
    Run,
    chemin_autorise,
    lire,
    nouveau_run,
    ouvrir_run,
    verifier_espace,
)
from slmsp.core.canonique import json_canonique
from slmsp.core.config import appliquer_environnement_impose, racine_ecriture
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide
from slmsp.core.var import verrou_gpu
from slmsp.inference import serveur
from slmsp.train import chargement, environnement

TYPE_RUN: Final = "export"
TYPE_RUN_TRAIN: Final = "train"
DOSSIER_ADAPTATEUR: Final = "adaptateur"
FICHIERS_ADAPTATEUR: Final = ("adapter_config.json", "adapter_model.safetensors")
DOSSIER_FUSION: Final = "hf-f16"
"""Modèle fusionné en F16 (safetensors), nom court (MAX_PATH)."""
NOM_F16: Final = "modele-f16.gguf"
NOM_Q4: Final = "modele-q4_k_m.gguf"
NOM_EXPORT: Final = "export.json"
NOM_LOG: Final = "log.jsonl"
NOM_LOG_CONVERSION: Final = "conversion.log"
NOM_LOG_QUANTIFICATION: Final = "quantification.log"
TYPE_SORTIE_CONVERSION: Final = "f16"
TYPE_QUANTIFICATION: Final = "Q4_K_M"
PRECISIONS: Final = {"f16": "f16", "q4_k_m": "q4_k_m"}
"""Précision réelle de chaque GGUF exporté (même rôle que `ConfigModele.precision_gguf`)."""
MAX_F16: Final = 65504.0
SEUIL_VERIFICATION_ESPACE: Final = 1024**3
FACTEUR_ESPACE: Final = 2.4
"""Écriture prévue ≈ 2,4 × les poids bf16 : HF F16 (1), GGUF F16 (1), Q4_K_M (~0,3)."""
DELAI_MIN_OUTIL: Final = 1800.0
"""Délai minimal (s) de la conversion et de la quantification, chacune (CPU)."""
DEBIT_MIN_OUTIL: Final = 2 * 1024**2
"""Débit plancher (octets de poids de la base par seconde) : au-delà, l'outil est jugé bloqué."""

Convertir = Callable[..., Path]
Quantifier = Callable[..., Path]
Controles = Callable[[Run, Mapping[str, Any]], Mapping[str, Any]]
"""`controles(run, export)` → `{"bloquants": [...], "alertes": [...], ...}`."""


@dataclass(frozen=True)
class Source:
    """Ce que l'export fusionne : base, adaptateurs et SHA du template d'entraînement."""

    slug: str
    adaptateurs: tuple[Path, ...] = ()
    runs_train: tuple[str, ...] = ()
    methode: str | None = None
    chat_template_sha256: str | None = None
    """SHA du tokenizer d'entraînement (`run.json` du run `train`) ; `None` : témoin."""
    nom: str = field(default="")

    @property
    def temoin(self) -> bool:
        return not self.adaptateurs


def _racine(racine: str | Path | None) -> Path:
    return (Path(racine) if racine is not None else racine_ecriture()).resolve()


def adaptateur_du_run(run_id: str, *, racine: str | Path | None = None) -> Path:
    """`runs/train/<run_id>/adaptateur/`, validé par le lecteur `train` et complet."""
    base = _racine(racine)
    dossier = chemin_autorise(
        base / "runs" / TYPE_RUN_TRAIN / run_id / DOSSIER_ADAPTATEUR, "train", racine=base
    )
    # Chaque fichier repasse par le lecteur : un lien qui sort de la liste d'accès est refusé.
    absents = [
        nom
        for nom in FICHIERS_ADAPTATEUR
        if not chemin_autorise(dossier / nom, "train", racine=base).is_file()
    ]
    if absents:
        raise ConfigurationInvalide(
            f"run {run_id} : adaptateur incomplet sous {dossier} (absent : {', '.join(absents)})"
        )
    return dossier


def controler_adaptateur(dossier: Path, *, racine: str | Path | None = None) -> dict[str, Any]:
    """`adapter_config.json` lu par le lecteur `train` ; refuse un PiSSA non converti."""
    brut = lire(dossier / "adapter_config.json", "train", racine=racine)
    try:
        config = json.loads(brut.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigurationInvalide(f"{dossier} : adapter_config.json invalide ({exc})") from None
    if not isinstance(config, dict):
        raise ConfigurationInvalide(f"{dossier} : adapter_config.json n'est pas un objet")
    init = config.get("init_lora_weights")
    if isinstance(init, str) and init.lower().startswith("pissa"):
        raise ConfigurationInvalide(
            f"{dossier} : adaptateur PiSSA non converti (init_lora_weights = {init!r}) ; "
            "l'enregistrer converti en LoRA relatif à la base d'origine "
            "(path_initial_model_for_weight_conversion de PEFT)"
        )
    cibles = config.get("target_modules") or []
    interdites = sorted(
        {"embed_tokens", "lm_head"} & set(cibles if isinstance(cibles, list) else [])
    )
    if interdites or config.get("modules_to_save"):
        raise ConfigurationInvalide(
            f"{dossier} : l'export refuse un adaptateur qui modifie embeddings ou tête "
            f"(target_modules {interdites}, modules_to_save {config.get('modules_to_save')!r})"
        )
    return {"peft_type": config.get("peft_type"), "r": config.get("r"), "init": init}


def source_depuis_run(run_id: str, *, racine: str | Path | None = None) -> Source:
    """Source d'un run `train` complet : slug, méthode, adaptateur et SHA du template."""
    base = _racine(racine)
    try:
        run = ouvrir_run(run_id, racine=base)
    except ManifesteInvalide as exc:
        raise ConfigurationInvalide(f"--depuis {run_id} : run illisible ({exc})") from None
    if run.type != TYPE_RUN_TRAIN:
        raise ConfigurationInvalide(f"--depuis {run_id} : run de type {run.type}, pas train")
    statut = run.statut_courant()
    if statut != "complet":
        raise ConfigurationInvalide(f"--depuis {run_id} : run {statut}, pas complet")
    toml = run.manifeste.config.get("toml")
    if not isinstance(toml, Mapping) or not isinstance(toml.get("modele"), str):
        raise ConfigurationInvalide(f"--depuis {run_id} : modèle absent de la configuration")
    sha = run.manifeste.chat_template_sha256
    if sha is None:
        raise ConfigurationInvalide(f"--depuis {run_id} : SHA du chat template non consigné")
    return Source(
        slug=toml["modele"],
        adaptateurs=(adaptateur_du_run(run_id, racine=base),),
        runs_train=(run_id,),
        methode=toml.get("methode") if isinstance(toml.get("methode"), str) else None,
        chat_template_sha256=sha,
        nom=f"ft-{toml['modele']}",
    )


def source_temoin(slug: str) -> Source:
    """Export témoin : la base seule, par la même chaîne (note 10.6, C4)."""
    return Source(slug=slug, nom=f"base-{slug}")


def octets_poids(dossier_base: Path) -> int:
    """Taille des poids safetensors de la base."""
    return sum(f.stat().st_size for f in dossier_base.glob("*.safetensors") if f.is_file())


def octets_prevus(dossier_base: Path) -> int:
    """Écriture prévue de l'export, d'après la taille des poids de la base."""
    return int(octets_poids(dossier_base) * FACTEUR_ESPACE)


def delai_outils(octets: int) -> float:
    """Délai de la conversion et de la quantification, proportionné aux poids de la base.

    Un processus bloqué est tué à l'échéance (`ErreurInference`), ce qui libère `gpu.lock`.
    """
    return max(DELAI_MIN_OUTIL, octets / DEBIT_MIN_OUTIL)


def controler_plage(torch: Any, modele: Any) -> dict[str, Any]:
    """Aucun NaN ni infini, max |w| < 65 504 avant la conversion en F16."""
    maximum = 0.0
    tenseurs = 0
    for nom, tenseur in modele.state_dict().items():
        if not getattr(tenseur, "is_floating_point", lambda: False)():
            continue
        tenseurs += 1
        if not bool(torch.isfinite(tenseur).all()):
            raise ConfigurationInvalide(f"fusion : valeur non finie dans {nom}")
        valeur = float(tenseur.abs().max()) if tenseur.numel() else 0.0
        if valeur >= MAX_F16:
            raise ConfigurationInvalide(
                f"fusion : |w| = {valeur} ≥ {MAX_F16} dans {nom} (hors de la plage F16)"
            )
        maximum = max(maximum, valeur)
    return {"tenseurs": tenseurs, "max_abs": maximum}


def fusionner(
    pile: environnement.Pile, dossier_base: Path, adaptateurs: Sequence[Path], sortie: Path
) -> dict[str, Any]:
    """Fusion fp32 sur CPU puis enregistrement F16 de `sortie` (modèle et tokenizer)."""
    torch = pile.torch
    modele = pile.transformers.AutoModelForCausalLM.from_pretrained(
        str(dossier_base),
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    for adaptateur in adaptateurs:
        modele = pile.peft.PeftModel.from_pretrained(modele, str(adaptateur)).merge_and_unload()
    plage = controler_plage(torch, modele)
    modele = modele.to(torch.float16)
    modele.save_pretrained(str(sortie), safe_serialization=True)
    tokenizer = pile.transformers.AutoTokenizer.from_pretrained(
        str(dossier_base), use_fast=True, local_files_only=True
    )
    tokenizer.save_pretrained(str(sortie))
    return {**plage, "chat_template_sha256": chargement.sha_chat_template(tokenizer)}


def exporter(
    source: Source,
    *,
    racine: str | Path | None = None,
    pile: environnement.Pile | None = None,
    convertir: Convertir | None = None,
    quantifier: Quantifier | None = None,
    python: str | os.PathLike[str] | None = None,
    controles: Controles,
    delai: float | None = None,
    sortie: Callable[[str], None] = print,
) -> Run:
    """Exporte `source` sous `runs/export/<run_id>/` ; renvoie le run terminé.

    Statut : `complet`, ou `partiel-erreur` si un contrôle bloquant échoue (template) ou
    sur exception (relancée). `pile`, `convertir`, `quantifier` : injectés par les tests
    (défaut : pile importée, `serveur.convertir_hf_vers_gguf` et `serveur.quantifier`).
    `controles` est obligatoire : sans lui, le SHA du template embarqué (CA2) ne serait pas
    contrôlé. `delai` : délai (s) de chaque outil llama.cpp (défaut : `delai_outils`).
    """
    convertir = convertir if convertir is not None else serveur.convertir_hf_vers_gguf
    quantifier = quantifier if quantifier is not None else serveur.quantifier
    appliquer_environnement_impose()
    os.environ.setdefault("PYTHONUTF8", "1")  # journaux du convertisseur (cp1252 sinon)
    base = _racine(racine)
    if not source.slug:
        raise ConfigurationInvalide("export : slug du Modèle de base absent")
    dossier_base = environnement.dossier_poids(source.slug, racine=base)
    details_adaptateurs = [controler_adaptateur(a, racine=base) for a in source.adaptateurs]
    config_llamacpp = serveur.charger_config_llamacpp()
    prevus = octets_prevus(dossier_base)
    if delai is None:
        delai = delai_outils(octets_poids(dossier_base))
    if delai <= 0:
        raise ConfigurationInvalide(f"export : délai des outils invalide ({delai} s)")
    dossier_export = base / "runs" / TYPE_RUN
    if prevus > SEUIL_VERIFICATION_ESPACE:
        verifier_espace(dossier_export, prevus)
    if pile is None:
        try:
            pile = environnement.charger_pile()
        except (ImportError, OSError) as exc:
            raise ConfigurationInvalide(
                f"pile d'entraînement indisponible ({type(exc).__name__} : {exc}) ; "
                "installer l'extra : uv sync --extra train"
            ) from None

    config = {
        "source": "temoin" if source.temoin else "train",
        "methode": source.methode,
        "runs_train": list(source.runs_train),
        "adaptateurs": [
            {"run_id": r, "dossier": DOSSIER_ADAPTATEUR, **d}
            for r, d in zip(source.runs_train, details_adaptateurs, strict=True)
        ],
        "dossier_poids": environnement.chemin_portable(dossier_base, racine=base),
        "fusion": {"calcul": "fp32", "ecriture": "f16", "materiel": "cpu"},
        "conversion": {"outtype": TYPE_SORTIE_CONVERSION},
        "quantification": {"type": TYPE_QUANTIFICATION, "imatrix": False, "variante": "cpu"},
        "octets_prevus": prevus,
        "delai_outils_s": delai,
    }
    commande = f"slmsp export {source.nom or source.slug}"
    with verrou_gpu(commande=commande):
        run = nouveau_run(
            TYPE_RUN,
            source.nom or source.slug,
            config,
            parents=source.runs_train,
            racine=base,
            modele_ref=f"base:{source.slug}",
            llamacpp_tag=config_llamacpp.tag,
            chat_template_sha256=source.chat_template_sha256,
        )
        sortie(f"run {run.run_id} : {run.dossier}")
        try:
            statut, motif = _executer(
                run,
                source,
                pile,
                dossier_base,
                convertir,
                quantifier,
                python,
                controles,
                delai,
                sortie,
            )
        except KeyboardInterrupt:
            run.terminer("interrompu", "arrêt demandé")
            raise
        except Exception as exc:
            run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}"[:500])
            raise
        run.terminer(statut, motif)
    return run


def _executer(
    run: Run,
    source: Source,
    pile: environnement.Pile,
    dossier_base: Path,
    convertir: Convertir,
    quantifier: Quantifier,
    python: str | os.PathLike[str] | None,
    controles: Controles,
    delai: float,
    sortie: Callable[[str], None],
) -> tuple[str, str | None]:
    def journal(evenement: str, **details: Any) -> None:
        run.ajouter_jsonl(NOM_LOG, {"evenement": evenement, **details})
        sortie(f"export : {evenement}")

    fusion = fusionner(pile, dossier_base, source.adaptateurs, run.dossier / DOSSIER_FUSION)
    journal("fusion", **fusion)
    f16 = convertir(
        run.dossier / DOSSIER_FUSION,
        run.dossier / NOM_F16,
        type_sortie=TYPE_SORTIE_CONVERSION,
        python=python,
        delai=delai,
        journal=run.dossier / NOM_LOG_CONVERSION,
    )
    journal("conversion", fichier=NOM_F16)
    quantifier(
        f16,
        run.dossier / NOM_Q4,
        TYPE_QUANTIFICATION,
        variante="cpu",
        delai=delai,
        journal=run.dossier / NOM_LOG_QUANTIFICATION,
    )
    journal("quantification", fichier=NOM_Q4)

    attendu = source.chat_template_sha256 or fusion["chat_template_sha256"]
    bloquants: list[str] = []
    if fusion["chat_template_sha256"] != attendu:
        bloquants.append(
            f"template du tokenizer fusionné ({fusion['chat_template_sha256']}) ≠ "
            f"template d'entraînement ({attendu})"
        )
    export: dict[str, Any] = {
        "fichiers": {"f16": NOM_F16, "q4_k_m": NOM_Q4, "hf": DOSSIER_FUSION},
        "precisions": dict(PRECISIONS),
        "chat_template_sha256_attendu": attendu,
        "fusion": fusion,
    }
    resultat: dict[str, Any] = {"bloquants": [], "alertes": []}
    if not bloquants:
        resultat = dict(controles(run, export))
    bloquants += list(resultat.get("bloquants", []))
    export["controles"] = {**resultat, "bloquants": bloquants}
    run.ecrire(NOM_EXPORT, json_canonique(export) + b"\n")
    if bloquants:
        return "partiel-erreur", " ; ".join(bloquants)[:500]
    return "complet", None


__all__ = [
    "NOM_F16",
    "NOM_Q4",
    "PRECISIONS",
    "Source",
    "TYPE_RUN",
    "adaptateur_du_run",
    "controler_adaptateur",
    "controler_plage",
    "delai_outils",
    "exporter",
    "fusionner",
    "octets_prevus",
    "source_depuis_run",
    "source_temoin",
]
