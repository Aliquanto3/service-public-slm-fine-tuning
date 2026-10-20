"""Vérification quotidienne des conditions commerciales de Mistral (story C9, D1.2).

GET de `conditions_url` par le client réseau `outillage`, SHA-256 des octets reçus. Identique
à `conditions_sha256` : la ligne `conditions_verifiees_le` de `config/donnees.toml` passe à la
date du jour (édition ciblée, commentaires conservés). Différent ou erreur réseau : aucune
mise à jour, `ConditionsAVerifier` (relecture d'Anaël requise). Chaque vérification est
consignée dans `<SLMSP_VAR_DIR>/mistral-conditions.jsonl` (état machine, hors convention des runs).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from slmsp.core.erreurs import SlmspError

__all__ = ["ConditionsAVerifier", "ResultatConditions", "verifier_conditions"]

_LIGNE_DATE = re.compile(
    r"^(conditions_verifiees_le\s*=\s*)(?:\d{4}-\d{2}-\d{2}|\"[^\"]*\"|'[^']*')", re.M
)
_ENTETE_MISTRAL = re.compile(r"^\[mistral\][^\r\n]*\r?$", re.M)
_ENTETE_TABLE = re.compile(r"^\[", re.M)


class ConditionsAVerifier(SlmspError):
    """Conditions modifiées ou illisibles : génération bloquée, relecture d'Anaël requise."""


@dataclass(frozen=True)
class ResultatConditions:
    sha_attendu: str
    sha_obtenu: str
    date_verification: date
    ecrit: bool


def _lire(fichier: Path) -> tuple[str, str]:
    try:
        table = tomllib.loads(fichier.read_text(encoding="utf-8"))["mistral"]
        url, sha = str(table["conditions_url"]), str(table["conditions_sha256"])
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        raise ConditionsAVerifier(
            f"{fichier} : conditions_url ou conditions_sha256 illisibles ({type(exc).__name__})"
        ) from None
    if not sha:
        raise ConditionsAVerifier(f"{fichier} : conditions_sha256 vide, relecture d'Anaël requise")
    return url, sha


def _journaliser(journal: Path | None, ligne: dict[str, Any]) -> None:
    if journal is None:
        return
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def verifier_conditions(
    fichier: Path,
    *,
    fabrique_client: Callable[[], Any],
    aujourd_hui: date,
    ecrire: bool = True,
    journal: Path | None = None,
) -> ResultatConditions:
    """Vérifie la page des conditions ; met la date à jour si le SHA est inchangé."""
    url, attendu = _lire(fichier)
    base = {"horodatage": datetime.now().astimezone().isoformat(timespec="seconds"), "url": url}
    try:
        with fabrique_client() as client:
            reponse = client.get(url)
            reponse.raise_for_status()
            octets = bytes(reponse.content)
    except Exception as exc:  # noqa: BLE001 - toute erreur réseau bloque, sans mise à jour
        _journaliser(journal, {**base, "resultat": "erreur_reseau", "erreur": type(exc).__name__})
        raise ConditionsAVerifier(
            f"conditions Mistral : GET impossible ({type(exc).__name__}) ; génération bloquée, "
            "relecture d'Anaël requise"
        ) from None
    obtenu = hashlib.sha256(octets).hexdigest()
    if obtenu != attendu:
        _journaliser(
            journal,
            {**base, "resultat": "different", "sha_attendu": attendu, "sha_obtenu": obtenu},
        )
        raise ConditionsAVerifier(
            "ALERTE conditions Mistral modifiées : "
            f"SHA attendu {attendu}, SHA obtenu {obtenu} ; aucune mise à jour, "
            "relecture d'Anaël requise"
        )
    ecrit = False
    if ecrire:
        with fichier.open(encoding="utf-8", newline="") as f:
            texte = f.read()
        debut = _ENTETE_MISTRAL.search(texte)
        if debut is None:
            raise ConditionsAVerifier(f"{fichier} : table [mistral] introuvable")
        suivant = _ENTETE_TABLE.search(texte, debut.end())
        fin = suivant.start() if suivant else len(texte)
        corps, n = _LIGNE_DATE.subn(
            lambda m: f"{m.group(1)}{aujourd_hui.isoformat()}", texte[debut.end() : fin]
        )
        if n != 1:
            raise ConditionsAVerifier(f"{fichier} : ligne conditions_verifiees_le introuvable")
        nouveau = texte[: debut.end()] + corps + texte[fin:]
        if nouveau != texte:
            temporaire = fichier.with_name(fichier.name + ".tmp")
            with temporaire.open("w", encoding="utf-8", newline="") as f:
                f.write(nouveau)
            os.replace(temporaire, fichier)
        ecrit = True
    _journaliser(
        journal,
        {
            **base,
            "resultat": "identique",
            "sha": obtenu,
            "date": aujourd_hui.isoformat(),
            "ecrit": ecrit,
        },
    )
    return ResultatConditions(attendu, obtenu, aujourd_hui, ecrit)
