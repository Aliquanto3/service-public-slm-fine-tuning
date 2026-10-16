"""Chargeur du jeu local MCQ-eval pour lm-eval (importé par lm-eval dans son sous-processus).

Sans réseau : lit les fichiers `.jsonl`, `.json` ou `.csv` du dossier `SLMSP_MCQ_EVAL_DIR`.
Chaque ligne est normalisée en `{"question": str, "choix": [str, ...], "reponse": int}`.
Le schéma exact du jeu n'est pas épinglé (voir la spec 6.2) : les noms de colonnes courants
sont acceptés (`question`, `choices`/`options`/`choix` ou colonnes `A`..`D`, `answer`/`reponse`).
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

VARIABLE_DOSSIER = "SLMSP_MCQ_EVAL_DIR"
LETTRES = "ABCDEFGH"


def _choix(ligne: dict[str, Any]) -> list[str]:
    for cle in ("choix", "choices", "options"):
        valeur = ligne.get(cle)
        if isinstance(valeur, list | tuple):
            return [str(v) for v in valeur]
        if isinstance(valeur, dict):
            return [str(v) for v in valeur.values()]
    lettrees = [str(ligne[lettre]) for lettre in LETTRES if ligne.get(lettre) not in (None, "")]
    if lettrees:
        return lettrees
    raise ValueError(f"aucune colonne de choix reconnue : {sorted(ligne)}")


def _indice(valeur: Any, nb_choix: int) -> int:
    texte = str(valeur).strip()
    if len(texte) == 1 and texte.upper() in LETTRES[:nb_choix]:
        return LETTRES.index(texte.upper())
    indice = int(texte)
    if not 0 <= indice < nb_choix:
        raise ValueError(f"réponse hors des choix : {valeur!r} ({nb_choix} choix)")
    return indice


def normaliser_ligne(ligne: dict[str, Any]) -> dict[str, Any]:
    """Ligne brute -> `{"question", "choix", "reponse"}` ; `ValueError` si illisible."""
    question = ligne.get("question")
    if question is None:
        raise ValueError(f"colonne question absente : {sorted(ligne)}")
    choix = _choix(ligne)
    reponse = ligne.get("reponse", ligne.get("answer"))
    if reponse is None:
        raise ValueError(f"colonne réponse absente : {sorted(ligne)}")
    return {"question": str(question), "choix": choix, "reponse": _indice(reponse, len(choix))}


def lire_lignes(dossier: str | Path) -> list[dict[str, Any]]:
    """Lignes normalisées de tous les fichiers du dossier, triés par nom."""
    base = Path(dossier)
    lignes: list[dict[str, Any]] = []
    for chemin in sorted(p for p in base.rglob("*") if p.is_file()):
        suffixe = chemin.suffix.lower()
        if suffixe == ".jsonl":
            brutes = [json.loads(t) for t in chemin.read_text(encoding="utf-8").splitlines() if t]
        elif suffixe == ".json":
            brutes = json.loads(chemin.read_text(encoding="utf-8"))
        elif suffixe == ".csv":
            with chemin.open(encoding="utf-8", newline="") as fichier:
                brutes = list(csv.DictReader(fichier))
        else:
            continue
        lignes.extend(normaliser_ligne(brute) for brute in brutes)
    if not lignes:
        raise FileNotFoundError(f"aucune ligne .jsonl, .json ou .csv dans {base}")
    return lignes


def charger_jeu(**_kwargs: Any) -> Any:
    """`custom_dataset` de lm-eval : `DatasetDict` avec la partition `test`."""
    dossier = os.environ.get(VARIABLE_DOSSIER)
    if not dossier:
        raise RuntimeError(f"{VARIABLE_DOSSIER} non défini (jeu local MCQ-eval)")
    from datasets import Dataset, DatasetDict  # fourni par lm-eval, importé à l'usage

    return DatasetDict({"test": Dataset.from_list(lire_lignes(dossier))})
