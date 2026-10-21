"""Prompts CT alignés sur leur cible : `data build --aligner-ct` (story 16.3, levier 5 de D0).

`lancer_alignement_ct` lit le jeu SFT d'un run `data-build` (SHA revérifié contre son
MANIFEST) et écrit une **nouvelle version** `data/train/vN/` où chaque prompt CT reçoit la
consigne de libellés `formulation`, avec les libellés extraits de la cible Mistral de sa ligne
(`core.alignement_ct`). Aucune cible n'est réécrite, aucun appel réseau (D1). La formulation
est fournie par l'appelant avec son origine (`origine_formulation`, consignée au MANIFEST),
qui doit figurer dans la liste fermée `[alignement_ct] origines_admises` de
`config/donnees.toml` (vide par défaut : refus tant qu'Anaël n'y a rien inscrit) ; ce module
n'en contient aucune. `train.chargement` revérifie la chaîne au chargement.
Déterministe : même source et même formulation, même `sha256_train`.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Collection
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.alignement_ct import TACHE_CT, aligner_jeu, valider_formulation
from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.entrainement import (
    TYPE_RUN_BUILD,
    AlignementCt,
    LigneEntrainement,
    ManifesteJeuEntrainement,
)
from slmsp.data.build import _creer_version
from slmsp.data.config import charger_config_donnees
from slmsp.data.preferences import _jeu_sft

__all__ = ["ResultatAlignementCt", "lancer_alignement_ct"]

NOM_TRAIN: Final = "train.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_RAPPORT: Final = "rapport.json"


@dataclass(frozen=True)
class ResultatAlignementCt:
    """Run produit, version écrite et rapport."""

    run: Run
    version: str
    dossier: Path
    rapport: dict[str, Any]


def lancer_alignement_ct(
    *,
    racine: str | Path,
    build_run_id: str,
    formulation: str,
    origine_formulation: str,
    origines_admises: Collection[str] | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatAlignementCt:
    """Construit `data/train/vN/train.jsonl` aux prompts CT alignés depuis `build_run_id`.

    Avant tout run : `ManifesteInvalide` (run absent, d'un autre type, sans jeu SFT, jeu déjà
    aligné, restreint ou sélectionné, formulation invalide ou sans origine, aucune ligne CT
    alignable, origine hors de `origines_admises`) ou `ProvenanceInvalide` (SHA altéré).
    `origines_admises` vaut par défaut `[alignement_ct] origines_admises` de
    `config/donnees.toml`.
    """
    valider_formulation(formulation)
    if not origine_formulation.strip():
        raise ManifesteInvalide("alignement CT : origine de la formulation attendue (D1)")
    if origines_admises is None:
        origines_admises = charger_config_donnees().alignement_ct.origines_admises
    if origine_formulation.strip() not in {o.strip() for o in origines_admises}:
        raise ManifesteInvalide(
            "alignement CT : origine de la formulation absente de [alignement_ct] "
            "origines_admises de config/donnees.toml (liste fermée tenue par Anaël, D1)"
        )
    base = Path(racine).resolve()
    version_src, manifeste_src, octets = _jeu_sft(build_run_id, base)
    try:
        source = ManifesteJeuEntrainement.model_validate(manifeste_src)
    except ValidationError as exc:
        raise ManifesteInvalide(
            f"jeu {version_src} : MANIFEST de build SFT attendu ({exc})"
        ) from None
    for bloc, nom in (
        (source.alignement_ct, "déjà aligné"),
        (source.sous_ensemble, "restreint"),
        (source.selection, "à cibles sélectionnées"),
    ):
        if bloc is not None:
            raise ManifesteInvalide(f"jeu {version_src} : {nom} (repartir du jeu source)")
    try:
        lignes = [json.loads(texte) for texte in octets.split(b"\n") if texte.strip()]
        for ligne in lignes:
            LigneEntrainement.model_validate(ligne)
    except (ValueError, ValidationError) as exc:
        raise ManifesteInvalide(f"jeu {version_src} : ligne SFT non conforme ({exc})") from None
    contenu, modifiees = aligner_jeu(octets, formulation)
    if not modifiees:
        raise ManifesteInvalide(f"jeu {version_src} : aucune ligne {TACHE_CT} à aligner")
    comptes = dict(sorted(Counter(str(ligne["tache"]) for ligne in lignes).items()))
    run = nouveau_run(
        TYPE_RUN_BUILD,
        "alignement-ct",
        {
            "alignement_ct": True,
            "build_run_id": build_run_id,
            "jeu_source_version": version_src,
            "formulation": formulation,
            "origine_formulation": origine_formulation,
        },
        parents=[build_run_id],
        racine=base,
    )
    try:
        version, dossier = _creer_version(base)
        (dossier / NOM_TRAIN).write_bytes(contenu)
        bloc = AlignementCt(
            depuis_build=build_run_id,
            depuis_version=version_src,
            sha256_train_source=sha256_hex(octets),
            formulation=formulation,
            origine_formulation=origine_formulation,
            lignes_modifiees=modifiees,
            comptes_source=comptes,
            nettoyage_source=source.nettoyage,
        )
        manifeste = source.model_copy(
            update={
                "version": version,
                "run_id": run.run_id,
                "cree_le": date.today(),
                "sha256_train": sha256_hex(contenu),
                "nettoyage": None,
                "alignement_ct": bloc,
            }
        )
        manifeste = ManifesteJeuEntrainement.model_validate(manifeste.model_dump(mode="json"))
        rapport = {
            "schema_version": 1,
            "version": version,
            "depuis_build": build_run_id,
            "depuis_version": version_src,
            "sha256_train_source": bloc.sha256_train_source,
            "sha256_train": manifeste.sha256_train,
            "nb_lignes": manifeste.nb_lignes,
            "lignes_ct": comptes.get(TACHE_CT, 0),
            "lignes_modifiees": modifiees,
            "origine_formulation": origine_formulation,
        }
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
        # MANIFEST en dernier : sa présence signale une version complète.
        temporaire = dossier / f"{NOM_MANIFEST}.tmp"
        temporaire.write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
        temporaire.replace(dossier / NOM_MANIFEST)
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    run.terminer("complet")
    consigner(
        f"alignement CT {version_src} → {version} : {modifiees}/{comptes.get(TACHE_CT, 0)} "
        f"lignes CT alignées, sha256 {manifeste.sha256_train}"
    )
    return ResultatAlignementCt(run=run, version=version, dossier=dossier, rapport=rapport)
