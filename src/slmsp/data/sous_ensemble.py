"""Sous-ensemble par Tâche du jeu SFT : `data build --sous-ensemble` (test M1 partiel).

`lancer_sous_ensemble` lit le jeu SFT d'un run `data-build` (SHA revérifié contre son MANIFEST,
comme `nettoyage` et `preferences`) et écrit une **nouvelle version** `data/train/vN/` qui ne
garde que les lignes des Tâches demandées, copiées à l'identique, dans l'ordre. Aucun texte
n'est rédigé ni réécrit (D1), aucun appel réseau. Le MANIFEST porte la provenance
(`sous_ensemble`) ; `core.sous_ensemble.verifier_sous_ensemble` la revérifie au chargement
(`train.chargement`) contre le jeu source relu.
Déterministe : même source et mêmes Tâches, même `sha256_train`.
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

from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.entrainement import (
    TYPE_RUN_BUILD,
    LigneEntrainement,
    ManifesteJeuEntrainement,
    SousEnsemble,
)
from slmsp.core.sous_ensemble import lignes_de_taches
from slmsp.data.build import _creer_version
from slmsp.data.preferences import _jeu_sft

__all__ = ["ResultatSousEnsemble", "lancer_sous_ensemble"]

NOM_TRAIN: Final = "train.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_RAPPORT: Final = "rapport.json"


@dataclass(frozen=True)
class ResultatSousEnsemble:
    """Run produit, version écrite et rapport."""

    run: Run
    version: str
    dossier: Path
    rapport: dict[str, Any]


def lancer_sous_ensemble(
    *,
    racine: str | Path,
    build_run_id: str,
    taches: Collection[str],
    consigner: Callable[[str], None] = print,
) -> ResultatSousEnsemble:
    """Construit `data/train/vN/train.jsonl` restreint à `taches` depuis le run `build_run_id`.

    Avant tout run : `ManifesteInvalide` (run absent, d'un autre type, sans jeu SFT, jeu déjà
    restreint, Tâche absente du jeu source, sous-ensemble vide) ou `ProvenanceInvalide` (SHA
    altéré). Un jeu source nettoyé est accepté : son bloc `nettoyage` est repris dans
    `sous_ensemble.nettoyage_source`.
    """
    demandees = sorted(set(taches))
    base = Path(racine).resolve()
    if not demandees:
        raise ManifesteInvalide("sous-ensemble : au moins une Tâche attendue")
    version_src, manifeste_src, octets = _jeu_sft(build_run_id, base)
    try:
        source = ManifesteJeuEntrainement.model_validate(manifeste_src)
    except ValidationError as exc:
        raise ManifesteInvalide(
            f"jeu {version_src} : MANIFEST de build SFT attendu ({exc})"
        ) from None
    if source.sous_ensemble is not None:
        raise ManifesteInvalide(f"jeu {version_src} : déjà restreint (repartir du jeu source)")
    if source.selection is not None:
        raise ManifesteInvalide(
            f"jeu {version_src} : cibles sélectionnées (restreindre le jeu source, puis "
            "sélectionner)"
        )
    try:
        lignes = [json.loads(texte) for texte in octets.split(b"\n") if texte.strip()]
        for ligne in lignes:
            LigneEntrainement.model_validate(ligne)
    except (ValueError, ValidationError) as exc:
        raise ManifesteInvalide(f"jeu {version_src} : ligne SFT non conforme ({exc})") from None
    avant = Counter(str(ligne["tache"]) for ligne in lignes)
    inconnues = [t for t in demandees if t not in avant]
    if inconnues:
        raise ManifesteInvalide(
            f"Tâche(s) {', '.join(inconnues)} absente(s) du jeu {version_src} "
            f"(Tâches : {', '.join(sorted(avant))})"
        )
    run = nouveau_run(
        TYPE_RUN_BUILD,
        "sous-ensemble",
        {
            "sous_ensemble": True,
            "build_run_id": build_run_id,
            "jeu_source_version": version_src,
            "taches": demandees,
        },
        parents=[build_run_id],
        racine=base,
    )
    try:
        contenu = b"".join(ligne + b"\n" for ligne in lignes_de_taches(octets, demandees))
        apres = Counter({t: avant[t] for t in demandees})
        version, dossier = _creer_version(base)
        (dossier / NOM_TRAIN).write_bytes(contenu)
        bloc = SousEnsemble(
            depuis_build=build_run_id,
            depuis_version=version_src,
            sha256_train_source=sha256_hex(octets),
            taches=demandees,
            comptes_source=dict(sorted(avant.items())),
            nettoyage_source=source.nettoyage,
        )
        manifeste = source.model_copy(
            update={
                "version": version,
                "run_id": run.run_id,
                "cree_le": date.today(),
                "sha256_train": sha256_hex(contenu),
                "nb_lignes": sum(apres.values()),
                "comptes_par_tache": dict(sorted(apres.items())),
                "nettoyage": None,
                "sous_ensemble": bloc,
            }
        )
        manifeste = ManifesteJeuEntrainement.model_validate(manifeste.model_dump(mode="json"))
        rapport = {
            "schema_version": 1,
            "version": version,
            "depuis_build": build_run_id,
            "depuis_version": version_src,
            "taches": demandees,
            "sha256_train_source": sha256_hex(octets),
            "sha256_train": manifeste.sha256_train,
            "nb_lignes_avant": len(lignes),
            "nb_lignes": manifeste.nb_lignes,
            "par_tache": {t: {"avant": avant[t], "apres": apres[t]} for t in sorted(avant)},
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
        f"sous-ensemble {version_src} → {version} ({', '.join(demandees)}) : "
        f"{len(lignes)} → {manifeste.nb_lignes} lignes, sha256 {manifeste.sha256_train}"
    )
    return ResultatSousEnsemble(run=run, version=version, dossier=dossier, rapport=rapport)
