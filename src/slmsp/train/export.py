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
import shutil
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import (
    EspaceInsuffisant,
    Run,
    chemin_autorise,
    lire,
    nouveau_run,
    ouvrir_run,
    verifier_espace,
)
from slmsp.core.canonique import json_canonique, sha256_fichier
from slmsp.core.config import appliquer_environnement_impose, racine_ecriture
from slmsp.core.erreurs import ConfigurationInvalide, LectureInterdite, ManifesteInvalide
from slmsp.core.var import verrou_gpu
from slmsp.inference import serveur
from slmsp.train import chargement, environnement
from slmsp.train.config import charger_config_export

TYPE_RUN: Final = "export"
TYPE_RUN_TRAIN: Final = "train"
DOSSIER_ADAPTATEUR: Final = "adaptateur"
FICHIERS_ADAPTATEUR: Final = ("adapter_config.json", "adapter_model.safetensors")
DOSSIER_FUSION: Final = "hf-f16"
"""Modèle fusionné en F16 (safetensors), nom court (MAX_PATH)."""
NOM_F16: Final = "modele-f16.gguf"
NOM_Q4: Final = "modele-q4_k_m.gguf"
NOM_MMPROJ: Final = "mmproj-f16.gguf"
"""Projecteur de vision (`--mmproj`), exporté pour une fiche `multimodal` seulement."""
NOM_EXPORT: Final = "export.json"
NOM_LOG: Final = "log.jsonl"
NOM_LOG_CONVERSION: Final = "conversion.log"
NOM_LOG_QUANTIFICATION: Final = "quantification.log"
NOM_LOG_MMPROJ: Final = "conversion-mmproj.log"
TYPE_SORTIE_CONVERSION: Final = "f16"
TYPE_QUANTIFICATION: Final = "Q4_K_M"
PRECISIONS: Final = {"f16": "f16", "q4_k_m": "q4_k_m"}
"""Précision réelle de chaque GGUF exporté (même rôle que `ConfigModele.precision_gguf`)."""
FICHIERS_PREPROCESSEUR: Final = (
    "chat_template.jinja",
    "preprocessor_config.json",
    "video_preprocessor_config.json",
)
"""Copiés tels quels de la base dans `hf-f16/` pour `--mmproj` ; `preprocessor_config.json`
est obligatoire."""
PREFIXE_VISION: Final = "model.visual."
PREFIXE_MTP: Final = "mtp."
SOUS_MODELE_LANGAGE: Final = "language_model"
MODULES_LORA_INTERDITS: Final = ("embed_tokens", "lm_head")
OCTETS_MMPROJ: Final = int(0.34 * 1024**3)
"""Écriture ajoutée par le mmproj F16 (168 M paramètres de vision pour Qwen3.5-2B)."""
MAX_F16: Final = 65504.0
SEUIL_VERIFICATION_ESPACE: Final = 1024**3
FACTEUR_ESPACE: Final = 3.0
"""Facteur par défaut (`[export].facteur_espace`) : HF F16 (1), GGUF F16 (1), Q4_K_M (~0,3),
marge. Écriture réelle ≈ 2,4 × les poids bf16."""
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


def _regex_cible_interdite(regex: str) -> bool:
    """Vrai si la regex de `target_modules` nomme visual, lm_head ou embed_tokens (avant tout
    chargement ; le contrôle exact reste celui du modèle chargé)."""
    return any(mot in regex for mot in ("visual", *MODULES_LORA_INTERDITS))


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
    # `target_modules` en chaîne (regex, LoRA multimodal) : la regex est seulement pré-contrôlée
    # ici (`_regex_cible_interdite`) ; le contrôle complet porte sur les modules LoRA du modèle
    # PEFT chargé (`controler_modules_lora`, appelé par la fusion, multimodal seulement). Pour un
    # modèle dense, une chaîne n'est contrôlée que par ce pré-contrôle.
    cibles = config.get("target_modules") or []
    if isinstance(cibles, str) and _regex_cible_interdite(cibles):
        raise ConfigurationInvalide(
            f"{dossier} : l'export refuse un adaptateur dont la regex target_modules "
            f"vise vision, embeddings ou tête ({cibles!r})"
        )
    interdites = sorted(
        {"embed_tokens", "lm_head"} & set(cibles if isinstance(cibles, list) else [])
    )
    if interdites or config.get("modules_to_save"):
        raise ConfigurationInvalide(
            f"{dossier} : l'export refuse un adaptateur qui modifie embeddings ou tête "
            f"(target_modules {interdites}, modules_to_save {config.get('modules_to_save')!r})"
        )
    return {"peft_type": config.get("peft_type"), "r": config.get("r"), "init": init}


def controler_modules_lora(modele_peft: Any) -> int:
    """Refuse un adaptateur dont un module LoRA, relevé sur le modèle PEFT chargé, est hors de
    `language_model` ou sur `embed_tokens` / `lm_head`. Renvoie le nombre de modules LoRA."""
    modules: set[str] = set()
    for nom, _module in modele_peft.named_modules():
        composants = nom.split(".")
        for i, composant in enumerate(composants):
            if composant.startswith("lora_") and i > 0:
                modules.add(".".join(composants[:i]))
                break
    hors = sorted(
        m
        for m in modules
        if SOUS_MODELE_LANGAGE not in m.split(".") or m.rsplit(".", 1)[-1] in MODULES_LORA_INTERDITS
    )
    if hors:
        raise ConfigurationInvalide(
            f"l'export refuse un adaptateur dont {len(hors)} module(s) LoRA sont hors de "
            f"`{SOUS_MODELE_LANGAGE}` ou sur embeddings / tête : {', '.join(hors[:5])}"
        )
    if not modules:
        raise ConfigurationInvalide("adaptateur sans module LoRA (target_modules ne ciblent rien)")
    return len(modules)


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


def octets_prevus(
    dossier_base: Path, *, multimodal: str | None = None, facteur: float = FACTEUR_ESPACE
) -> int:
    """Écriture prévue de l'export, d'après la taille des poids de la base (+ mmproj)."""
    prevus = int(octets_poids(dossier_base) * facteur)
    return prevus + (OCTETS_MMPROJ if multimodal is not None else 0)


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


def a_tete_mtp(*dossiers: Path, racine: str | Path | None = None) -> bool:
    """Vrai si le premier `config.json` lisible déclare `mtp_num_hidden_layers` > 0, à la racine
    ou sous `text_config` (la conversion texte passe alors `--no-mtp`)."""
    for dossier in dossiers:
        try:
            config = json.loads(lire(dossier / "config.json", "train", racine=racine))
        except (OSError, ValueError, LectureInterdite):
            continue  # absent, illisible ou hors liste d'accès : dossier suivant
        if not isinstance(config, dict):
            return False
        texte = config.get("text_config")
        for niveau in (config, texte if isinstance(texte, dict) else {}):
            couches = niveau.get("mtp_num_hidden_layers")
            if isinstance(couches, int) and not isinstance(couches, bool) and couches > 0:
                return True
        return False
    return False


def copier_preprocesseur(dossier_base: Path, sortie: Path) -> list[str]:
    """Copie sans modification `FICHIERS_PREPROCESSEUR` de la base vers `sortie` (`--mmproj`)."""
    if not (dossier_base / "preprocessor_config.json").is_file():
        raise ConfigurationInvalide(
            f"preprocessor_config.json absent de {dossier_base} : conversion --mmproj impossible"
        )
    copies = []
    for nom in FICHIERS_PREPROCESSEUR:
        # Un fichier déjà écrit par `tokenizer.save_pretrained` (chat_template.jinja) est gardé :
        # c'est celui dont le SHA est contrôlé dans le GGUF.
        if (sortie / nom).exists():
            continue
        if (dossier_base / nom).is_file():
            shutil.copyfile(dossier_base / nom, sortie / nom)
            copies.append(nom)
    return copies


def _index_tenseurs(dossier: Path) -> dict[str, Path]:
    from safetensors import safe_open  # noqa: PLC0415

    index: dict[str, Path] = {}
    for fichier in sorted(dossier.glob("*.safetensors")):
        with safe_open(str(fichier), framework="pt") as poignee:
            index.update(dict.fromkeys(poignee.keys(), fichier))
    return index


def controler_vision_inchangee(base: Path, fusionne: Path) -> dict[str, Any]:
    """Chaque tenseur `model.visual.*` de `base` égal à celui de `fusionne`, après passage
    dans le dtype écrit (F16). Un écart ou un tenseur absent est bloquant (`bloquants`).

    Les `mtp.*` de la base, absents du fusionné (B2.4), ne sont pas comparés.
    """
    import torch  # noqa: PLC0415
    from safetensors import safe_open  # noqa: PLC0415

    index_base, index_fusion = _index_tenseurs(base), _index_tenseurs(fusionne)
    vision = sorted(n for n in index_base if n.startswith(PREFIXE_VISION))
    ecarts: list[str] = []
    absents: list[str] = []
    for nom in vision:
        if nom not in index_fusion:
            absents.append(nom)
            continue
        with safe_open(str(index_base[nom]), framework="pt") as a:
            attendu = a.get_tensor(nom).to(torch.float16)
        with safe_open(str(index_fusion[nom]), framework="pt") as b:
            obtenu = b.get_tensor(nom).to(torch.float16)
        if not torch.equal(attendu, obtenu):
            ecarts.append(nom)
    bloquants: list[str] = []
    if not vision:
        bloquants.append(f"aucun tenseur {PREFIXE_VISION}* dans la base {base}")
    if absents:
        bloquants.append(
            f"{len(absents)} tenseur(s) de vision absent(s) du fusionné : {absents[:3]}"
        )
    if ecarts:
        bloquants.append(
            f"{len(ecarts)} tenseur(s) de vision modifié(s) par la fusion : {ecarts[:3]}"
        )
    return {
        "tenseurs": len(vision),
        "ecarts": ecarts,
        "absents": absents,
        "mtp_ignores": sum(1 for n in index_base if n.startswith(PREFIXE_MTP)),
        "bloquants": bloquants,
    }


def fusionner(
    pile: environnement.Pile,
    dossier_base: Path,
    adaptateurs: Sequence[Path],
    sortie: Path,
    *,
    multimodal: str | None = None,
) -> dict[str, Any]:
    """Fusion fp32 sur CPU puis enregistrement F16 de `sortie` (modèle et tokenizer).

    `multimodal` (fiche du slug) choisit la classe (`environnement.classe_modele`) ; avec lui,
    les modules LoRA sont contrôlés sur le modèle PEFT chargé et le préprocesseur de la base
    est copié dans `sortie` (conversion `--mmproj`).
    """
    torch = pile.torch
    modele = environnement.classe_modele(pile, multimodal).from_pretrained(
        str(dossier_base),
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        local_files_only=True,
    )
    for adaptateur in adaptateurs:
        charge = pile.peft.PeftModel.from_pretrained(modele, str(adaptateur))
        if multimodal is not None:
            controler_modules_lora(charge)
        modele = charge.merge_and_unload()
    plage = controler_plage(torch, modele)
    modele = modele.to(torch.float16)
    modele.save_pretrained(str(sortie), safe_serialization=True)
    tokenizer = pile.transformers.AutoTokenizer.from_pretrained(
        str(dossier_base), use_fast=True, local_files_only=True
    )
    tokenizer.save_pretrained(str(sortie))
    if multimodal is not None:
        copier_preprocesseur(dossier_base, sortie)
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
    multimodal = serveur.charger_config_modele(source.slug).multimodal
    config_espace = charger_config_export()
    prevus = octets_prevus(
        dossier_base, multimodal=multimodal, facteur=config_espace.facteur_espace
    )
    if config_espace.espace_libre_go is not None:
        prevus = int(config_espace.espace_libre_go * 1024**3)
    if delai is None:
        delai = delai_outils(octets_poids(dossier_base))
    if delai <= 0:
        raise ConfigurationInvalide(f"export : délai des outils invalide ({delai} s)")
    dossier_export = base / "runs" / TYPE_RUN
    if prevus > SEUIL_VERIFICATION_ESPACE or config_espace.espace_libre_go is not None:
        try:
            verifier_espace(dossier_export, prevus)
        except EspaceInsuffisant as exc:
            raise EspaceInsuffisant(
                f"export refusé : {exc}. Libérer de l'espace : `slmsp export purger "
                "--tous-notes --dry-run` liste les exports notés dont `hf-f16/` et "
                "`modele-f16.gguf` peuvent être supprimés (puis sans --dry-run)"
            ) from None
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
    if multimodal is not None:
        config["multimodal"] = multimodal
        config["conversion"] = {
            "outtype": TYPE_SORTIE_CONVERSION,
            "sans_mtp": a_tete_mtp(dossier_base, racine=base),
            "mmproj": NOM_MMPROJ,
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
                multimodal,
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
    multimodal: str | None = None,
) -> tuple[str, str | None]:
    def journal(evenement: str, **details: Any) -> None:
        run.ajouter_jsonl(NOM_LOG, {"evenement": evenement, **details})
        sortie(f"export : {evenement}")

    fusion = fusionner(
        pile,
        dossier_base,
        source.adaptateurs,
        run.dossier / DOSSIER_FUSION,
        multimodal=multimodal,
    )
    journal("fusion", **fusion)
    vision: dict[str, Any] | None = None
    if multimodal is not None:
        vision = controler_vision_inchangee(dossier_base, run.dossier / DOSSIER_FUSION)
        journal("vision", tenseurs=vision["tenseurs"], bloquants=vision["bloquants"])
        if vision["bloquants"]:
            # Inutile de convertir (30 min) un modèle dont la vision a changé.
            echec = {
                "fichiers": {"hf": DOSSIER_FUSION},
                "fusion": fusion,
                "multimodal": multimodal,
                "vision": vision,
                "controles": {"bloquants": vision["bloquants"], "alertes": []},
            }
            run.ecrire(NOM_EXPORT, json_canonique(echec) + b"\n")
            return "partiel-erreur", " ; ".join(vision["bloquants"])[:500]
    sans_mtp = multimodal is not None and a_tete_mtp(
        run.dossier / DOSSIER_FUSION, dossier_base, racine=run.dossier.parents[2]
    )
    options_texte: dict[str, Any] = {"sans_mtp": True} if sans_mtp else {}
    f16 = convertir(
        run.dossier / DOSSIER_FUSION,
        run.dossier / NOM_F16,
        type_sortie=TYPE_SORTIE_CONVERSION,
        python=python,
        delai=delai,
        journal=run.dossier / NOM_LOG_CONVERSION,
        **options_texte,
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
    if multimodal is not None:
        convertir(
            run.dossier / DOSSIER_FUSION,
            run.dossier / NOM_MMPROJ,
            type_sortie=TYPE_SORTIE_CONVERSION,
            python=python,
            delai=delai,
            journal=run.dossier / NOM_LOG_MMPROJ,
            mmproj=True,
        )
        journal("conversion-mmproj", fichier=NOM_MMPROJ)

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
    if multimodal is not None:
        export["fichiers"]["mmproj"] = NOM_MMPROJ
        export["multimodal"] = multimodal
        export["vision"] = vision
        export["llamacpp_tag"] = run.manifeste.llamacpp_tag
        export["sha256"] = {
            cle: sha256_fichier(run.dossier / export["fichiers"][cle])
            for cle in ("f16", "q4_k_m", "mmproj")
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
    "NOM_MMPROJ",
    "NOM_Q4",
    "PRECISIONS",
    "Source",
    "TYPE_RUN",
    "adaptateur_du_run",
    "controler_adaptateur",
    "controler_modules_lora",
    "controler_plage",
    "controler_vision_inchangee",
    "copier_preprocesseur",
    "delai_outils",
    "exporter",
    "fusionner",
    "octets_prevus",
    "source_depuis_run",
    "source_temoin",
]
