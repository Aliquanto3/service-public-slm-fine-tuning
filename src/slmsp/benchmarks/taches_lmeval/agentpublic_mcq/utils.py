"""Chargeur du jeu local MCQ-eval pour lm-eval (importé par lm-eval dans son sous-processus).

Sans réseau : lit les fichiers `.jsonl`, `.json`, `.csv` ou `.xlsx` du dossier
`SLMSP_MCQ_EVAL_DIR`. Le jeu réel (AgentPublic/MCQ-eval) est un classeur Excel : seule la feuille
`QCM_version_albert_dedup` de `HF_QCM_reconcilie_V1xlsx.xlsx` est lue (colonnes `Question`,
`A`..`E` préfixées « A. », `Number_best_rep` = lettre), les autres classeurs sont ignorés.
Chaque ligne est normalisée en `{"question": str, "choix": [str, ...], "reponse": int}`.
Le schéma exact du jeu n'est pas épinglé (voir la spec 6.2) : les noms de colonnes courants
sont acceptés (`question`, `choices`/`options`/`choix` ou colonnes `A`..`D`, `answer`/`reponse`).
"""

from __future__ import annotations

import csv
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

VARIABLE_DOSSIER = "SLMSP_MCQ_EVAL_DIR"
LETTRES = "ABCDEFGH"
FEUILLE_XLSX = "QCM_version_albert_dedup"
NS_XLSX = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_RELATIONS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PREFIXE_CHOIX = re.compile(r"^[A-H]\.\s*")


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


def _colonne(reference: str) -> int:
    indice = 0
    for caractere in re.match(r"[A-Z]+", reference).group():  # type: ignore[union-attr]
        indice = indice * 26 + ord(caractere) - 64
    return indice - 1


def lire_xlsx(chemin: Path, feuille: str = FEUILLE_XLSX) -> list[dict[str, str]]:
    """Lignes d'une feuille de classeur (bibliothèque standard), en dictionnaires par en-tête.

    Les lignes vides sont ignorées ; classeur sans cette feuille : liste vide.
    """
    with zipfile.ZipFile(chemin) as classeur:
        noms = classeur.namelist()
        textes: list[str] = []
        if "xl/sharedStrings.xml" in noms:
            racine = ET.fromstring(classeur.read("xl/sharedStrings.xml"))
            textes = [
                "".join(t.text or "" for t in si.iter(f"{NS_XLSX}t"))
                for si in racine.findall(f"{NS_XLSX}si")
            ]
        feuilles = ET.fromstring(classeur.read("xl/workbook.xml")).find(f"{NS_XLSX}sheets")
        cible = next((s for s in feuilles if s.get("name") == feuille), None)  # type: ignore[union-attr]
        if cible is None:
            return []
        relations = ET.fromstring(classeur.read("xl/_rels/workbook.xml.rels"))
        rel = cible.get(f"{NS_RELATIONS}id")
        fichier = next(r.get("Target") for r in relations if r.get("Id") == rel)
        fichier = (fichier or "").lstrip("/")
        fichier = fichier if fichier.startswith("xl/") else f"xl/{fichier}"
        lignes: list[dict[int, str]] = []
        for ligne in ET.fromstring(classeur.read(fichier)).iter(f"{NS_XLSX}row"):
            valeurs: dict[int, str] = {}
            for cellule in ligne.findall(f"{NS_XLSX}c"):
                valeur = cellule.find(f"{NS_XLSX}v")
                if cellule.get("t") == "inlineStr":
                    texte = "".join(t.text or "" for t in cellule.iter(f"{NS_XLSX}t"))
                elif valeur is None or valeur.text is None:
                    continue
                elif cellule.get("t") == "s":
                    texte = textes[int(valeur.text)]
                else:
                    texte = valeur.text
                valeurs[_colonne(cellule.get("r", "A1"))] = texte
            if valeurs:
                lignes.append(valeurs)
    if not lignes:
        return []
    entetes = {i: v.strip() for i, v in lignes[0].items()}
    return [{entetes[i]: v for i, v in ligne.items() if i in entetes} for ligne in lignes[1:]]


def ligne_xlsx(brute: dict[str, str]) -> dict[str, Any]:
    """Ligne de la feuille du jeu réel -> `question`, `choix` et `reponse` (indice dans `choix`).

    Une lettre sans texte est écartée (l'indice suit les choix présents) ; une réponse
    « C (la B aussi) » vaut C.
    """
    lettres = [lettre for lettre in LETTRES if brute.get(lettre) not in (None, "")]
    reponse = re.match(r"\s*([A-H])\b", brute.get("Number_best_rep") or "")
    if reponse is None or reponse.group(1) not in lettres:
        raise ValueError(f"réponse illisible : {brute.get('Number_best_rep')!r}")
    return {
        "question": brute.get("Question"),
        "choix": [PREFIXE_CHOIX.sub("", str(brute[lettre]).strip()) for lettre in lettres],
        "reponse": lettres.index(reponse.group(1)),
    }


def _lignes_xlsx(chemin: Path) -> list[dict[str, Any]]:
    """Lignes normalisées d'un classeur ; erreur explicite (fichier, numéro de ligne) sinon."""
    try:
        brutes = lire_xlsx(chemin)
    except (zipfile.BadZipFile, ET.ParseError, KeyError, StopIteration, OSError) as exc:
        raise ValueError(f"{chemin.name} : classeur illisible ({exc!r})") from exc
    lignes = []
    for numero, brute in enumerate(brutes, start=2):  # ligne 1 = en-têtes
        try:
            lignes.append(ligne_xlsx(brute))
        except ValueError as exc:
            raise ValueError(f"{chemin.name}, ligne {numero} : {exc}") from exc
    return lignes


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
        elif suffixe == ".xlsx":
            brutes = _lignes_xlsx(chemin)
        else:
            continue
        lignes.extend(normaliser_ligne(brute) for brute in brutes)
    if not lignes:
        raise FileNotFoundError(f"aucune ligne .jsonl, .json, .csv ou .xlsx dans {base}")
    return lignes


def charger_jeu(**_kwargs: Any) -> Any:
    """`custom_dataset` de lm-eval : `DatasetDict` avec la partition `test`."""
    dossier = os.environ.get(VARIABLE_DOSSIER)
    if not dossier:
        raise RuntimeError(f"{VARIABLE_DOSSIER} non défini (jeu local MCQ-eval)")
    from datasets import Dataset, DatasetDict  # fourni par lm-eval, importé à l'usage

    return DatasetDict({"test": Dataset.from_list(lire_lignes(dossier))})
