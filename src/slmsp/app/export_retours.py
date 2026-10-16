"""Export des Retours en JSON anonymisé (story 12.3, FR-20).

Trois temps : `construire_export` (lecture seule dans `Stockage`), `apercu` (texte que l'Agent
relit) puis `ecrire` (seule étape qui touche au disque, refusée sans confirmation). Aucun accès
réseau et aucune écriture avant la confirmation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from slmsp.app.anonymisation import anonymiser, prenoms_actifs
from slmsp.core.erreurs import SlmspError

CHAMPS_TEXTE = ("question", "reponse", "commentaire", "sources")


class LecteurRetours(Protocol):
    def lister_retours(self) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class Export:
    contenu: str
    nom_fichier: str
    comptes: dict[str, int] = field(default_factory=dict)
    avertissements: tuple[str, ...] = ()


AVERTISSEMENT_PRENOMS = (
    "détection des prénoms inactive : fichier INSEE absent (seules les civilités sont masquées)"
)


def nom_fichier(jour: date) -> str:
    return f"retours-assistant-{jour.isoformat()}.json"


def _masquer(valeur: Any, comptes: dict[str, int], prenoms: frozenset[str] | None) -> Any:
    if isinstance(valeur, str):
        texte, par_motif = anonymiser(valeur, prenoms=prenoms)
        for motif, n in par_motif.items():
            comptes[motif] = comptes.get(motif, 0) + n
        return texte
    if isinstance(valeur, list):
        return [_masquer(v, comptes, prenoms) for v in valeur]
    if isinstance(valeur, dict):
        return {k: _masquer(v, comptes, prenoms) for k, v in valeur.items()}
    return valeur


def construire_export(
    stockage: LecteurRetours, *, jour: date | None = None, prenoms: frozenset[str] | None = None
) -> Export:
    """JSON anonymisé de tous les Retours ; l'identifiant interne n'est pas exporté."""
    comptes: dict[str, int] = {}
    retours = []
    for retour in stockage.lister_retours():
        sortie = {k: v for k, v in retour.items() if k != "id"}
        for champ in CHAMPS_TEXTE:
            if champ in sortie:
                sortie[champ] = _masquer(sortie[champ], comptes, prenoms)
        retours.append(sortie)
    contenu = json.dumps({"retours": retours}, ensure_ascii=False, indent=2)
    avertissements = () if prenoms_actifs(prenoms) else (AVERTISSEMENT_PRENOMS,)
    return Export(contenu, nom_fichier(jour or date.today()), comptes, avertissements)


def apercu(export: Export) -> str:
    """Texte présenté à l'Agent avant l'enregistrement : avertissements, puis le contenu écrit."""
    entete = "".join(f"AVERTISSEMENT : {a}\n" for a in export.avertissements)
    return f"{entete}\n{export.contenu}" if entete else export.contenu


def ecrire(export: Export, destination: Path, *, confirme: bool) -> Path:
    """Écrit l'export dans le dossier `destination` ; refuse sans confirmation de l'Agent."""
    if not confirme:
        raise SlmspError("export non confirmé : rien n'est écrit")
    destination.mkdir(parents=True, exist_ok=True)
    chemin = destination / export.nom_fichier
    chemin.write_text(export.contenu, encoding="utf-8")
    return chemin
