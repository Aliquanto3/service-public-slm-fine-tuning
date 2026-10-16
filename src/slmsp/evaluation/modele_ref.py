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
  porte le template du tokenizer).

Toute incohérence lève `ConfigurationInvalide` ; une référence ou une quantification mal
formée lève `ValueError` (erreur d'usage).
"""

from __future__ import annotations

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
    genre: Literal["base", "ft"]
    quantification: Quantification
    slug: str
    slug_run: str
    config: ConfigModele
    gguf: Path
    precision: str
    """Précision réelle du GGUF servi : `q4_k_m`, `f16` ou `bf16` (`[gguf_f16].precision`)."""


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
    ref: str, run_id: str, quantification: Quantification, racine: Path
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
    if statut != "complet":
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


def resoudre(ref: str, quantification: str, *, racine: str | Path | None = None) -> ModeleResolu:
    """Résout `ref` (`base:<slug>` ou `ft:<export_run_id>`) × `quantification`.

    Lève `ValueError` pour une référence ou une quantification mal formée,
    `ConfigurationInvalide` pour un modèle introuvable ou incohérent (voir le module).
    """
    if not isinstance(ref, str) or not _MOTIF_REF.fullmatch(ref):
        raise ValueError(f"référence de modèle invalide : {ref!r} (base:<slug> ou ft:<run_id>)")
    if quantification not in QUANTIFICATIONS:
        raise ValueError(
            f"quantification invalide : {quantification!r} (attendu : {', '.join(QUANTIFICATIONS)})"
        )
    genre, valeur = ref.split(":", 1)
    if genre == "base":
        return _resoudre_base(ref, valeur, quantification)  # type: ignore[arg-type]
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    return _resoudre_ft(ref, valeur, quantification, base)  # type: ignore[arg-type]


__all__ = ["QUANTIFICATIONS", "ModeleResolu", "Quantification", "resoudre"]
