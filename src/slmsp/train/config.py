"""Configuration d'entraînement : `config/entrainement.toml` (AD-18).

Créé par la story 10.3 (`ConfigCouts`, protocole de mesure du coût d'un Run) ; la story
10.4 le complète (`RunConfig`). Le fichier est lu sous `<racine du projet>/config`, jamais
sous `--racine` : la configuration suit le code exécuté.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.run import MOTIF_RUN_ID


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run (`[couts]`)."""

    pas_chauffe: int = Field(ge=0)
    """Pas d'optimisation écartés avant de mesurer le débit."""
    periode_echantillonnage: float = Field(gt=0)
    """Secondes entre deux relevés NVML."""
    indice_gpu: int = Field(ge=0)


class ConfigExport(ModeleConfig):
    """Contrôle d'espace libre avant un export (`[export]`, story C8)."""

    facteur_espace: float = Field(default=3.0, gt=0)
    """Espace libre exigé = poids de la base × ce facteur (HF F16, GGUF F16, Q4_K_M, marge)."""
    espace_libre_go: float | None = Field(default=None, gt=0)
    """Valeur fixe en Gio, qui remplace l'estimation (`None` : estimation par le facteur)."""


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    couts: ConfigCouts
    export: ConfigExport = ConfigExport()


def charger_config_couts(dossier: str | Path | None = None) -> ConfigCouts:
    """Section `[couts]` de `<dossier>/entrainement.toml` (défaut : `<racine>/config`)."""
    base = Path(dossier) if dossier is not None else racine_projet() / "config"
    return charger_toml(base / "entrainement.toml", ConfigEntrainement).couts


def charger_config_export(dossier: str | Path | None = None) -> ConfigExport:
    """Section `[export]` de `<dossier>/entrainement.toml` (absente : valeurs par défaut)."""
    base = Path(dossier) if dossier is not None else racine_projet() / "config"
    chemin = base / "entrainement.toml"
    if not chemin.is_file():
        return ConfigExport()  # config absente (installation minimale) : défauts
    return charger_toml(chemin, ConfigEntrainement).export


# --- Run d'entraînement (story 10.4) -------------------------------------------------------

Methode = Literal["qlora", "lora", "dora", "orpo", "rslora", "pissa", "qlora-unsloth"]
"""M1 `qlora`, M2 `lora`, M3 `dora`, M4 `orpo` ; variantes `rslora`, `pissa`, `qlora-unsloth`."""

PrecisionBase = Literal["fp32-kbit", "bf16"]
"""Précision de la base d'un run quantifié : `fp32-kbit` passe par `prepare_model_for_kbit_training`
(embeddings, normes et conv1d en fp32) ; `bf16` garde la base en bf16 (moins de VRAM)."""
PRECISION_BASE_DEFAUT: Final = "fp32-kbit"

LONGUEUR_MAX_REPLI_TORCH: Final = 4096
"""Borne de `repli_torch` (enquête du 2026-10-18 : 536 à 633 tokens/s jusqu'à 4096)."""

MOTIF_NOM_RUN: Final = r"^[a-z0-9.-]+$"
"""Nom d'un TOML de run (slug du `run_id`, AD-21) et d'une campagne."""

Slug = Annotated[str, StringConstraints(pattern=MOTIF_NOM_RUN)]


class HyperParametres(ModeleConfig):
    """Hyperparamètres d'un Run (`[hyperparametres]`) ; les défauts valent pour M1 à M4."""

    lora_rang: int = Field(default=16, gt=0)
    lora_alpha: int = Field(default=32, gt=0)
    lora_dropout: float = Field(default=0.0, ge=0, lt=1)
    taux_apprentissage: float = Field(default=2e-4, gt=0)
    epoques: float = Field(default=1.0, gt=0)
    pas_max: int | None = Field(default=None, gt=0)
    """Nombre de pas d'optimisation ; `None` : `epoques` passes sur le jeu."""
    taille_lot: int = Field(default=1, gt=0)
    accumulation: int = Field(default=8, gt=0)
    planificateur: Literal["constant", "linear", "cosine"] = "cosine"
    echauffement_ratio: float = Field(default=0.03, ge=0, lt=1)
    pas_sauvegarde: int = Field(default=100, gt=0)
    """Un checkpoint tous les `pas_sauvegarde` pas (jamais de `save_total_limit`)."""
    orpo_beta: float = Field(default=0.1, gt=0)
    """Poids du terme de préférence d'ORPO (ignoré par les autres méthodes)."""


class RunConfig(ModeleConfig):
    """Contenu de `config/runs/<nom>.toml` : un Run, un TOML (AD-18)."""

    campagne: Slug
    """Les Runs d'une campagne partagent jeu, graine, longueur, template et masque."""
    modele: Slug
    """Slug du Modèle de base (`config/modeles/<slug>.toml`, poids sous `models/<slug>/hf/`)."""
    methode: Methode
    jeu_version: Annotated[str, StringConstraints(pattern=r"^v\d+$")]
    """Version du jeu construit : `data/train/<jeu_version>/`."""
    graine: int = Field(ge=0)
    longueur_max: int = Field(ge=8)
    hyperparametres: HyperParametres = Field(default_factory=HyperParametres)
    precision_base: PrecisionBase = PRECISION_BASE_DEFAUT
    """Méthodes quantifiées (qlora, dora, orpo, rslora) : voir `PrecisionBase`. Sans effet sur
    l'entraînement en lora et pissa (bf16 sans quantification, jamais castée), mais invariant de
    campagne comme ailleurs : leurs TOML déclarent la précision de la campagne (`bf16` pour
    rejoindre une campagne en `bf16`)."""
    repli_torch: bool = False
    """Hybrides Gated DeltaNet : autorise le repli torch si les noyaux fla manquent (lent ;
    borné à `longueur_max <= 4096`, non mesuré au-delà). Absent du `toml` résolu au défaut."""
    sft_run_id: Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)] | None = None
    """ORPO seulement : Run SFT dont l'adaptateur sert de point de départ."""

    @model_validator(mode="after")
    def _coherence(self) -> RunConfig:
        if self.methode == "orpo" and self.sft_run_id is None:
            raise ValueError("methode = orpo exige sft_run_id (ORPO après SFT)")
        if self.methode != "orpo" and self.sft_run_id is not None:
            raise ValueError("sft_run_id n'est permis qu'avec methode = orpo")
        if self.methode == "qlora-unsloth" and self.precision_base != PRECISION_BASE_DEFAUT:
            raise ValueError("precision_base ne s'applique pas à qlora-unsloth (pile Unsloth)")
        if self.repli_torch and self.longueur_max > LONGUEUR_MAX_REPLI_TORCH:
            raise ValueError(
                f"repli_torch = true exige longueur_max <= {LONGUEUR_MAX_REPLI_TORCH} "
                "(repli torch non mesuré au-delà sous Windows)"
            )
        return self


def charger_run_config(chemin: str | Path) -> RunConfig:
    """`RunConfig` d'un TOML de run ; le nom du fichier (sans `.toml`) doit être un slug."""
    chemin = Path(chemin)
    if chemin.suffix != ".toml" or not _nom_valide(chemin.stem):
        raise ConfigurationInvalide(
            f"{chemin} : nom de TOML de run invalide (attendu : <nom>.toml, nom en [a-z0-9.-])"
        )
    return charger_toml(chemin, RunConfig)


def _nom_valide(nom: str) -> bool:
    return re.fullmatch(MOTIF_NOM_RUN, nom) is not None and nom.strip(".") == nom
