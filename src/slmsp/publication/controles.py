"""Contrôles du dossier de publication : certification, fuite du Jeu d'évaluation, secrets.

Fonctions pures : chacune renvoie la liste des constats bloquants (vide si le dossier passe).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from slmsp.core.canonique import sha256_fichier
from slmsp.core.items import N_DEFAUT, _empreintes_texte
from slmsp.publication.config import ConfigPublication

SUFFIXES_TEXTE = frozenset({".md", ".txt", ".json", ".toml", ".yaml", ".yml"})
NOM_SOMMES = "SHA256SUMS"
RACINES_INTERDITES = (("eval",), ("data", "train"))
"""Préfixes (relatifs à la racine du projet ou au dossier) dont aucun fichier ne sort."""
MIN_EMPREINTES_COMMUNES = 3
"""Nombre de 5-grammes communs avec le Jeu d'évaluation qui constitue une fuite."""


def _est_texte(chemin: Path) -> bool:
    return chemin.suffix.lower() in SUFFIXES_TEXTE or chemin.name == NOM_SOMMES


def _sous_prefixe(parties: tuple[str, ...], prefixe: tuple[str, ...]) -> bool:
    minuscules = tuple(p.lower() for p in parties)
    return minuscules[: len(prefixe)] == prefixe


def controle_chemin_source(chemin: Path, racine: Path) -> list[str]:
    """Refuse une source située sous `eval/` ou `data/train/` de la racine du projet."""
    try:
        relatif = chemin.resolve().relative_to(racine.resolve())
    except ValueError:
        return []
    if any(_sous_prefixe(relatif.parts, p) for p in RACINES_INTERDITES):
        return [f"source interdite à la publication : {relatif.as_posix()}"]
    return []


def controle_fichiers(dossier: Path) -> list[str]:
    """Refuse tout fichier de `eval/` ou `data/train/` copié dans le dossier, et les `.env`."""
    constats: list[str] = []
    for chemin in sorted(p for p in dossier.rglob("*") if p.is_file()):
        relatif = chemin.relative_to(dossier)
        if any(_sous_prefixe(relatif.parts, p) for p in RACINES_INTERDITES):
            constats.append(f"fichier interdit (eval/ ou data/train/) : {relatif.as_posix()}")
        if chemin.name.lower().startswith(".env") or chemin.suffix.lower() == ".env":
            constats.append(f"fichier de secrets interdit : {relatif.as_posix()}")
    return constats


def _phrases(texte: str) -> Iterable[str]:
    return (p for p in re.split(r"[.;!?\n]+", texte) if p.strip())


def controle_formulations(texte: str, config: ConfigPublication, nom: str = "fiche") -> list[str]:
    """Refuse une formulation de certification, sauf dans une phrase de non-certification."""
    interdites = [re.compile(m, re.IGNORECASE) for m in config.formulations_interdites]
    admises = [m.lower() for m in config.mentions_non_certification]
    constats: list[str] = []
    for phrase in _phrases(texte):
        if phrase.lstrip().startswith("#"):
            continue
        bas = phrase.lower()
        if any(m in bas for m in admises):
            continue
        for motif in interdites:
            trouve = motif.search(phrase)
            if trouve:
                constats.append(f"{nom} : formulation de certification « {trouve.group(0)} »")
    return constats


def controle_sections(texte: str, config: ConfigPublication) -> list[str]:
    titres = {m.strip().lower() for m in re.findall(r"^##\s+(.+)$", texte, re.MULTILINE)}
    return [
        f"fiche : section absente « {s} »"
        for s in config.sections_obligatoires
        if s.lower() not in titres
    ]


def controle_secrets(dossier: Path, config: ConfigPublication) -> list[str]:
    motifs = [re.compile(m) for m in config.motifs_secrets]
    constats: list[str] = []
    for chemin in sorted(p for p in dossier.rglob("*") if p.is_file() and _est_texte(p)):
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        if any(m.search(texte) for m in motifs):
            constats.append(f"secret probable dans {chemin.relative_to(dossier).as_posix()}")
    return constats


def controle_fuite(dossier: Path, empreintes: frozenset[str]) -> list[str]:
    """Refuse un fichier texte qui partage des n-grammes avec le Jeu d'évaluation (AD-11)."""
    if not empreintes:
        return []
    constats: list[str] = []
    for chemin in sorted(p for p in dossier.rglob("*") if p.is_file() and _est_texte(p)):
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        communes = {e for ligne in texte.splitlines() for e in _empreintes_texte(ligne, N_DEFAUT)}
        if len(communes & empreintes) >= MIN_EMPREINTES_COMMUNES:
            constats.append(
                f"{chemin.relative_to(dossier).as_posix()} : texte du Jeu d'évaluation détecté"
            )
    return constats


def lister_sommes(dossier: Path) -> dict[str, str]:
    """SHA-256 de chaque fichier du dossier hors `SHA256SUMS`, clés triées."""
    return {
        p.relative_to(dossier).as_posix(): sha256_fichier(p)
        for p in sorted(dossier.rglob("*"))
        if p.is_file() and p.name != NOM_SOMMES
    }


def controle_sommes(dossier: Path) -> list[str]:
    """`SHA256SUMS` existe et correspond exactement aux fichiers du dossier."""
    chemin = dossier / NOM_SOMMES
    if not chemin.is_file():
        return [f"{NOM_SOMMES} absent"]
    declarees: dict[str, str] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        empreinte, _, nom = ligne.partition("  ")
        declarees[nom] = empreinte
    return [] if declarees == lister_sommes(dossier) else [f"{NOM_SOMMES} ne correspond pas"]
