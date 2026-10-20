"""Purge des intermédiaires d'un export (story C8).

Un export garde `hf-f16/` et `modele-f16.gguf` (7 à 10 Go) en plus du Q4_K_M. Pour un export
**noté** (une notation `runs/eval-notation/*` au statut `complet` référence
`ft:<export_run_id>`), ces intermédiaires ne servent plus : on les supprime, le Q4_K_M et le
run restent. Les runs sont immuables : la purge ajoute un événement `purge` à `log.jsonl`, sans
réécrire un fichier. Garde-fous : export `complet`, Q4_K_M à en-tête GGUF, aucun lien
symbolique ni jonction (rien n'est supprimé ni compté hors du dossier de l'export).
"""

from __future__ import annotations

import os
import shutil
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Final

from slmsp.core.artefacts import Run, ouvrir_run
from slmsp.core.erreurs import SlmspError
from slmsp.train.export import DOSSIER_FUSION, NOM_F16, NOM_LOG, NOM_Q4, TYPE_RUN

INTERMEDIAIRES: Final = (DOSSIER_FUSION, NOM_F16)
"""Noms supprimés ; `mmproj-f16.gguf` (sonde vision) et le Q4_K_M sont gardés."""
TYPE_NOTATION: Final = "eval-notation"
TAILLE_MIN_Q4: Final = 1024
"""Taille minimale d'un Q4_K_M crédible (en-tête GGUF et métadonnées)."""
RATIO_MIN_Q4: Final = 0.1
"""Q4_K_M ≥ 10 % du GGUF F16 (réel : ~30 %) ; en dessous, quantification tronquée."""


class PurgeRefusee(SlmspError):
    """Purge refusée (export non complet, Q4_K_M invalide, non noté, lien symbolique)."""


class PurgePartielle(SlmspError):
    """Suppression interrompue par une erreur ; l'événement `purge` partiel est journalisé."""


def _est_lien(chemin: Path) -> bool:
    return chemin.is_symlink() or chemin.is_junction()


def q4_valide(dossier: Path) -> bool:
    """Le Q4_K_M est un fichier réel (pas un lien) de taille cohérente avec le GGUF F16.

    L'en-tête GGUF du Q4_K_M est contrôlé par l'export lui-même (chat template relu) : un
    export `complet` l'a validé ; la purge exige ce statut (`controler`).
    """
    q4 = dossier / NOM_Q4
    if _est_lien(q4) or not q4.is_file():
        return False
    taille = q4.stat().st_size
    if taille < TAILLE_MIN_Q4:
        return False
    f16 = dossier / NOM_F16
    if f16.is_file() and not _est_lien(f16):
        return RATIO_MIN_Q4 * f16.stat().st_size <= taille < f16.stat().st_size
    return True


def _liens(chemin: Path) -> list[Path]:
    """Liens symboliques et jonctions sous `chemin` (lui compris), sans les suivre."""
    if _est_lien(chemin):
        return [chemin]
    if not chemin.is_dir():
        return []
    trouves: list[Path] = []
    for parent, dossiers, fichiers in os.walk(chemin, followlinks=False):
        trouves += [Path(parent) / n for n in [*dossiers, *fichiers] if _est_lien(Path(parent) / n)]
    return trouves


def _octets(chemin: Path) -> int:
    """Octets des fichiers réels sous `chemin` (liens ignorés, jamais suivis)."""
    if _est_lien(chemin):
        return 0
    if chemin.is_file():
        return chemin.lstat().st_size
    total = 0
    for parent, _dossiers, fichiers in os.walk(chemin, followlinks=False):
        for nom in fichiers:
            fichier = Path(parent) / nom
            if not _est_lien(fichier):
                total += fichier.lstat().st_size
    return total


def _presents(dossier: Path) -> list[str]:
    return [nom for nom in INTERMEDIAIRES if os.path.lexists(dossier / nom)]


def octets_intermediaires(dossier: Path) -> int:
    """Taille des intermédiaires encore présents sous `dossier` (fichiers réels seulement)."""
    return sum(_octets(dossier / nom) for nom in _presents(dossier))


def exports_notes(racine: Path) -> dict[str, list[str]]:
    """`{export_run_id: [notation_run_id, ...]}` des notations au statut `complet`."""
    notes: dict[str, list[str]] = {}
    for dossier in sorted((racine / "runs" / TYPE_NOTATION).glob("*")):
        try:
            notation = ouvrir_run(dossier.name, racine=racine)
            if notation.statut_courant() != "complet":
                continue  # notation en cours, interrompue ou en erreur : ne compte pas
            ref = notation.manifeste.modele_ref
        except (SlmspError, ValueError, OSError):
            continue  # manifeste illisible : ne référence aucun export
        if isinstance(ref, str) and ref.startswith("ft:"):
            notes.setdefault(ref[3:], []).append(dossier.name)
    return notes


def _rmtree_force(chemin: Path, racine: Path) -> None:
    def retirer(fonction: Callable[..., object], nom: str, exc: BaseException) -> None:
        cible = Path(nom)
        if _est_lien(cible) or not cible.resolve().is_relative_to(racine):
            raise exc  # jamais de chmod hors du dossier de l'export
        os.chmod(nom, stat.S_IWRITE)  # fichier en lecture seule (Windows)
        fonction(nom)

    shutil.rmtree(chemin, onexc=retirer)


def controler(run: Run, *, notations: list[str], forcer_non_note: bool = False) -> None:
    """Lève `PurgeRefusee` si l'export `run` ne peut pas être purgé."""
    if run.type != TYPE_RUN:
        raise PurgeRefusee(f"{run.run_id} n'est pas un run d'export")
    if (statut := run.statut_courant()) != "complet":
        raise PurgeRefusee(f"{run.run_id} : export au statut {statut}, pas complet")
    if not q4_valide(run.dossier):
        raise PurgeRefusee(
            f"{run.run_id} : {NOM_Q4} absent, lien, trop petit ou sans en-tête GGUF ; "
            "rien n'est supprimé"
        )
    if not notations and not forcer_non_note:
        raise PurgeRefusee(
            f"{run.run_id} : aucune notation complète ne référence ft:{run.run_id} "
            "(--forcer-non-note pour purger quand même)"
        )
    racine = run.dossier.resolve()
    for nom in _presents(run.dossier):
        cible = run.dossier / nom
        if liens := _liens(cible):
            raise PurgeRefusee(f"{run.run_id} : lien symbolique ou jonction refusé : {liens[0]}")
        if cible.resolve().parent != racine:
            raise PurgeRefusee(f"{run.run_id} : {cible} sort du dossier de l'export")


def purger(
    run: Run, *, notations: list[str], forcer_non_note: bool = False, dry_run: bool = False
) -> int:
    """Supprime les intermédiaires de l'export `run` ; renvoie les octets libérés.

    Refus (`PurgeRefusee`) : voir `controler`. `dry_run` : calcule sans supprimer ni
    journaliser. Erreur de suppression : événement `purge` partiel journalisé, puis
    `PurgePartielle`.
    """
    controler(run, notations=notations, forcer_non_note=forcer_non_note)
    presents = _presents(run.dossier)
    octets = octets_intermediaires(run.dossier)
    if dry_run or not presents:
        return octets
    racine = run.dossier.resolve()
    supprimes: list[str] = []
    liberes = 0
    erreur: OSError | None = None
    for nom in presents:
        cible = run.dossier / nom
        taille = _octets(cible)
        try:
            if cible.is_dir():
                _rmtree_force(cible, racine)
            else:
                cible.unlink()
        except OSError as exc:
            erreur = exc
            break
        supprimes.append(nom)
        liberes += taille
    evenement: dict[str, object] = {
        "evenement": "purge",
        "supprimes": supprimes,
        "octets_liberes": liberes,
        "notations": notations,
        "forcee": not notations,
    }
    if erreur is not None:
        evenement |= {"partiel": True, "erreur": f"{type(erreur).__name__} : {erreur}"[:500]}
    run.ajouter_jsonl(NOM_LOG, evenement)
    if erreur is not None:
        raise PurgePartielle(
            f"{run.run_id} : purge partielle ({', '.join(supprimes) or 'rien'} supprimé) : "
            f"{type(erreur).__name__} : {erreur}"
        ) from erreur
    return liberes


def purger_depuis(
    export_run_id: str, *, racine: Path, forcer_non_note: bool = False, dry_run: bool = False
) -> int:
    """`purger` pour l'export `export_run_id` (notations lues sous `racine`)."""
    run = ouvrir_run(export_run_id, racine=racine)
    return purger(
        run,
        notations=exports_notes(racine).get(export_run_id, []),
        forcer_non_note=forcer_non_note,
        dry_run=dry_run,
    )


def exports_a_purger(racine: Path) -> list[tuple[str, int]]:
    """Exports notés aux intermédiaires présents : `(run_id, octets)`.

    Les garde-fous (statut, Q4_K_M, liens) sont appliqués par `purger`, export par export.
    """
    resultat: list[tuple[str, int]] = []
    for export_id in sorted(exports_notes(racine)):
        dossier = racine / "runs" / TYPE_RUN / export_id
        if dossier.is_dir() and _presents(dossier):
            resultat.append((export_id, octets_intermediaires(dossier)))
    return resultat


__all__ = [
    "INTERMEDIAIRES",
    "PurgePartielle",
    "PurgeRefusee",
    "controler",
    "exports_a_purger",
    "exports_notes",
    "octets_intermediaires",
    "purger",
    "purger_depuis",
    "q4_valide",
]
