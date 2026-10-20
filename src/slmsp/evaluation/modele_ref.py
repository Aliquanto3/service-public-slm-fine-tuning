"""Résolution d'un `ModeleRef` en GGUF et en `ConfigModele` pour le banc (AD-13).

- `base:<slug>` : Modèle de base candidat, configuré par `config/modeles/<slug>.toml`.
  `q4_k_m` : le GGUF de `[gguf]` ; `f16` : celui de `[gguf_f16]` s'il est configuré (F16,
  ou BF16 faute de F16 publié), tous deux sous `<dossier_modeles()>/<slug>/gguf/` (le F16
  se télécharge par `slmsp fetch modeles <slug> --f16`).
  Un modèle d'embedding est refusé. Un template HF exporté par la story 8.1
  (`<dossier_modeles()>/<slug>/chat_template.jinja`) sans `chat_template_force = true`
  est un état incohérent (les templates diffèrent mais le serveur servirait celui du
  GGUF) : refus, AD-13 impose le template du tokenizer.
- `ft:<export_run_id>` : run `runs/export/<id>/` (sous `racine`), `complet`, dont le
  `run.json` porte `modele_ref = base:<slug>` ; GGUF `modele-<quantification>.gguf` du
  run ; configuration de `<slug>` avec `chat_template_force = false` (le GGUF exporté
  porte le template du tokenizer). Un run `degrade` (sonde d'outils non valide sur le
  Q4_K_M, story 10.6) est refusé, sauf `accepter_degrade=True` explicite.

- `lora:<export_lora_run_id>[@<échelle>]` : run `runs/export-lora/<id>/` (story 15.6),
  `complet` (ou `degrade`, voir `ft:`), dont le `run.json` porte `modele_ref = base:<slug>` ;
  la base est le GGUF Q4_K_M officiel de `<slug>` (comme `base:<slug>`, template compris),
  l'adaptateur `adaptateur-lora.gguf` du run s'applique par `--lora-scaled`. L'échelle
  (défaut 1.0) fait partie de la référence normalisée `lora:<id>@<échelle>`, donc du
  `modele_ref` des runs d'évaluation (reprise et comparaison sans ambiguïté). `f16` refusé.

Toute incohérence lève `ConfigurationInvalide` ; une référence ou une quantification mal
formée lève `ValueError` (erreur d'usage).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final, Literal, get_args

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.config import dossier_modeles, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.schemas.run import ModeleRef
from slmsp.inference.serveur import charger_config_modele

Quantification = Literal["f16", "q4_k_m"]
QUANTIFICATIONS: Final[tuple[str, ...]] = get_args(Quantification)

TYPE_RUN_EXPORT: Final = "export"
TYPE_RUN_EXPORT_LORA: Final = "export-lora"
NOM_LORA: Final = "adaptateur-lora.gguf"
ECHELLE_LORA_DEFAUT: Final = 1.0
ECHELLE_LORA_MAX: Final = 4.0
"""Borne haute de l'échelle LoRA (au-delà, l'adaptateur n'est plus un réglage fin)."""
DECIMALES_ECHELLE_LORA: Final = 4
"""Avec la borne, `:g` rend l'échelle sans arrondi ni exposant (motif de `ModeleRef`)."""
NOM_TEMPLATE: Final = "chat_template.jinja"

_MOTIF_REF: Final = re.compile(get_args(ModeleRef)[1].pattern)
"""Motif de `core.schemas.run.ModeleRef` (une seule définition)."""


@dataclass(frozen=True)
class ModeleResolu:
    """Modèle évalué : référence, GGUF à servir et configuration du serveur.

    `slug` est celui de la configuration (`config/modeles/<slug>.toml`), `slug_run` celui
    du run d'évaluation (`<slug>` ou `ft-<slug>`).
    """

    ref: str
    genre: Literal["base", "ft", "lora"]
    quantification: Quantification
    slug: str
    slug_run: str
    config: ConfigModele
    gguf: Path
    precision: str
    """Précision réelle du GGUF servi : `q4_k_m`, `f16` ou `bf16` (`[gguf_f16].precision`)."""
    lora: Path | None = None
    """`lora:` seulement : LoRA GGUF appliqué à `gguf` par `--lora-scaled`."""
    echelle_lora: float | None = None


def _config_generation(slug: str) -> ConfigModele:
    config = charger_config_modele(slug)
    if config.embedding:
        raise ConfigurationInvalide(f"{slug} est un modèle d'embedding : rien à évaluer")
    return config


def _resoudre_base(ref: str, slug: str, quantification: Quantification) -> ModeleResolu:
    config = _config_generation(slug)
    fichier = config.gguf_pour(quantification)
    if fichier is None:
        raise ConfigurationInvalide(
            f"{ref} : aucun GGUF {quantification.upper()} de base configuré "
            f"(section gguf_f16 absente de config/modeles/{slug}.toml)"
        )
    dossier = dossier_modeles() / slug
    gguf = dossier / "gguf" / PurePosixPath(fichier.fichier).name
    if not gguf.is_file():
        option = " --f16" if quantification == "f16" else ""
        raise ConfigurationInvalide(
            f"{ref} : GGUF absent : {gguf} (`slmsp fetch modeles {slug}{option}`, "
            "ou définir SLMSP_MODELS_DIR)"
        )
    exporte = dossier / NOM_TEMPLATE
    if exporte.is_file() and not config.chat_template_force:
        raise ConfigurationInvalide(
            f"{ref} : template HF exporté ({exporte}) mais chat_template_force = false dans "
            f"config/modeles/{slug}.toml : le template du tokenizer doit être imposé (AD-13)"
        )
    precision = config.precision_gguf(quantification) or quantification
    return ModeleResolu(ref, "base", quantification, slug, slug, config, gguf, precision)


def _resoudre_ft(
    ref: str, run_id: str, quantification: Quantification, racine: Path, accepter_degrade: bool
) -> ModeleResolu:
    try:
        run = ouvrir_run(run_id, racine=racine)
    except ManifesteInvalide as exc:
        raise ConfigurationInvalide(f"{ref} : run d'export illisible ({exc})") from None
    if run.manifeste.type != TYPE_RUN_EXPORT:
        raise ConfigurationInvalide(
            f"{ref} : le run {run_id} est de type {run.manifeste.type!r}, pas {TYPE_RUN_EXPORT!r}"
        )
    statut = run.statut_courant()
    if statut == "degrade" and not accepter_degrade:
        raise ConfigurationInvalide(
            f"{ref} : run d'export degrade (sonde d'outils non valide, voir sonde-outils.json) ; "
            "refusé sans accepter_degrade explicite"
        )
    if statut not in ("complet", "degrade"):
        raise ConfigurationInvalide(f"{ref} : run d'export {statut}, pas complet")
    base = run.manifeste.modele_ref
    if base is None or not base.startswith("base:"):
        raise ConfigurationInvalide(
            f"{ref} : le run d'export ne désigne pas son Modèle de base (modele_ref = {base!r})"
        )
    slug = base.removeprefix("base:")
    config = _config_generation(slug).model_copy(update={"chat_template_force": False})
    gguf = run.dossier / f"modele-{quantification}.gguf"
    if not gguf.is_file():
        raise ConfigurationInvalide(f"{ref} : GGUF absent du run d'export : {gguf}")
    return ModeleResolu(ref, "ft", quantification, slug, f"ft-{slug}", config, gguf, quantification)


def echelle_lora_de(ref: str) -> float | None:
    """Échelle de `lora:<id>[@<échelle>]` (`ECHELLE_LORA_DEFAUT` sans `@`), `None` hors `lora:`."""
    if not ref.startswith("lora:"):
        return None
    _, _, echelle = ref.partition("@")
    return float(echelle) if echelle else ECHELLE_LORA_DEFAUT


def composer_lora(ref: str, echelle: float | None) -> str:
    """Référence normalisée `lora:<id>@<échelle>` ; `ref` sans `@` prend `echelle` (défaut 1.0).

    Lève `ValueError` si `ref` n'est pas `lora:` (alors `echelle` doit être `None`, il est
    ignoré sinon), si `echelle` n'est pas un réel fini positif ou diffère de celle de `ref`.
    """
    if not ref.startswith("lora:"):
        if echelle is not None:
            raise ValueError(f"--echelle-lora : réservé à une référence lora:<id> (reçu {ref!r})")
        return ref
    identifiant, arobase, deja = ref.partition("@")
    if echelle is None:
        echelle = float(deja) if arobase else ECHELLE_LORA_DEFAUT
    elif arobase and float(deja) != float(echelle):
        raise ValueError(f"échelle LoRA contradictoire : {ref!r} et --echelle-lora {echelle:g}")
    if not math.isfinite(echelle) or not 0 < echelle <= ECHELLE_LORA_MAX:
        raise ValueError(
            f"échelle LoRA invalide : {echelle!r} (0 < échelle <= {ECHELLE_LORA_MAX:g})"
        )
    if round(echelle, DECIMALES_ECHELLE_LORA) != echelle:
        # `:g` arrondirait en silence : la référence et `--lora-scaled` diffèreraient de la
        # valeur demandée.
        raise ValueError(
            f"échelle LoRA invalide : {echelle!r} ({DECIMALES_ECHELLE_LORA} décimales au plus)"
        )
    return f"{identifiant}@{float(echelle):g}"


def _resoudre_lora(
    ref: str, run_id: str, quantification: Quantification, racine: Path, accepter_degrade: bool
) -> ModeleResolu:
    if quantification != "q4_k_m":
        raise ConfigurationInvalide(
            f"{ref} : seule la base q4_k_m porte un LoRA (quantification {quantification!r})"
        )
    identifiant = run_id.partition("@")[0]
    ref = composer_lora(ref, None)
    echelle = echelle_lora_de(ref)
    try:
        run = ouvrir_run(identifiant, racine=racine)
    except ManifesteInvalide as exc:
        raise ConfigurationInvalide(f"{ref} : run d'export LoRA illisible ({exc})") from None
    if run.manifeste.type != TYPE_RUN_EXPORT_LORA:
        raise ConfigurationInvalide(
            f"{ref} : le run {identifiant} est de type {run.manifeste.type!r}, "
            f"pas {TYPE_RUN_EXPORT_LORA!r}"
        )
    statut = run.statut_courant()
    if statut == "degrade" and not accepter_degrade:
        raise ConfigurationInvalide(
            f"{ref} : run d'export LoRA degrade (chargement non valide) ; refusé sans "
            "accepter_degrade explicite"
        )
    if statut not in ("complet", "degrade"):
        raise ConfigurationInvalide(f"{ref} : run d'export LoRA {statut}, pas complet")
    base = run.manifeste.modele_ref
    if base is None or not base.startswith("base:"):
        raise ConfigurationInvalide(
            f"{ref} : run d'export LoRA sans Modèle de base (modele_ref = {base!r})"
        )
    lora = run.dossier / NOM_LORA
    if not lora.is_file():
        raise ConfigurationInvalide(f"{ref} : LoRA GGUF absent du run d'export : {lora}")
    de_base = _resoudre_base(base, base.removeprefix("base:"), "q4_k_m")
    return ModeleResolu(
        ref,
        "lora",
        "q4_k_m",
        de_base.slug,
        f"lora-{de_base.slug}",
        de_base.config,
        de_base.gguf,
        "q4_k_m",
        lora,
        echelle,
    )


def resoudre(
    ref: str,
    quantification: str,
    *,
    racine: str | Path | None = None,
    accepter_degrade: bool = False,
) -> ModeleResolu:
    """Résout `ref` (`base:<slug>`, `ft:<export_run_id>` ou `lora:<export_lora_run_id>[@<échelle>]`)
    × `quantification`.

    Lève `ValueError` pour une référence ou une quantification mal formée,
    `ConfigurationInvalide` pour un modèle introuvable ou incohérent (voir le module).
    `accepter_degrade` : accepte un run d'export `degrade` (choix explicite de l'appelant).
    """
    if not isinstance(ref, str) or not _MOTIF_REF.fullmatch(ref):
        raise ValueError(
            f"référence de modèle invalide : {ref!r} "
            "(base:<slug> ou ft:<run_id> ; lora:<run_id>[@<échelle>])"
        )
    if quantification not in QUANTIFICATIONS:
        raise ValueError(
            f"quantification invalide : {quantification!r} (attendu : {', '.join(QUANTIFICATIONS)})"
        )
    genre, valeur = ref.split(":", 1)
    if genre == "lora":
        base = (Path(racine) if racine is not None else racine_projet()).resolve()
        return _resoudre_lora(ref, valeur, quantification, base, accepter_degrade)  # type: ignore[arg-type]
    if genre == "base":
        return _resoudre_base(ref, valeur, quantification)  # type: ignore[arg-type]
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    return _resoudre_ft(ref, valeur, quantification, base, accepter_degrade)  # type: ignore[arg-type]


__all__ = [
    "ECHELLE_LORA_DEFAUT",
    "QUANTIFICATIONS",
    "ModeleResolu",
    "Quantification",
    "composer_lora",
    "echelle_lora_de",
    "resoudre",
]
