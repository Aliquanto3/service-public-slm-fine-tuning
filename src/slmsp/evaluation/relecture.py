"""Export de relecture humaine (`relecture.md`) et lecture des Scores relus (story 5.6).

`rendre_relecture` rend, pour chaque item de l'échantillon de relecture présent dans le run,
l'entrée telle que l'Assistant l'a reçue (`rendre_entree`), la sortie jugée
(`rendre_sortie`), les contrôles automatiques et, par juge, le verdict critère par critère
(note et justification) avec les inventions signalées.

Les Scores restent « non relus » tant que le run ne contient pas de `relecture-validee.json`
daté (objet JSON dont la clé `date` est une date ou date-heure ISO valide), déposé par le
relecteur. `charger_scores` relit `scores.json` et pose `verdicts_relus` en conséquence.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final

from slmsp.core.items import ItemBase
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Scores
from slmsp.judge.prompt import ItemNonJugeable, references, rendre_entree, rendre_sortie

NOM_RELECTURE: Final = "relecture.md"
NOM_VALIDATION: Final = "relecture-validee.json"
NOM_SCORES: Final = "scores.json"


def _bloc(texte: str) -> str:
    """Bloc de code Markdown dont la clôture est plus longue que toute suite de « ` »."""
    plus_longue = 0
    courante = 0
    for caractere in texte:
        courante = courante + 1 if caractere == "`" else 0
        plus_longue = max(plus_longue, courante)
    cloture = "`" * max(3, plus_longue + 1)
    return f"{cloture}text\n{texte}\n{cloture}"


def _une_ligne(valeur: Any) -> str:
    """Justification sur une ligne (sauts de ligne remplacés par des espaces)."""
    return " ".join(str(valeur or "").split())


def _references(item: ItemBase) -> str | None:
    """Champs de référence transmis au Juge (`judge.prompt.references`), sinon `None` (CO)."""
    try:
        valeurs = references(item)
    except ItemNonJugeable:
        return None
    return json.dumps(valeurs, ensure_ascii=False, indent=2)


def _verdict(ligne: Mapping[str, Any]) -> list[str]:
    juge = ligne.get("juge", "?")
    statut = ligne.get("statut", "?")
    motif = ligne.get("motif")
    entete = f"**Juge {juge}** : {statut}" + (f" ({motif})" if motif else "")
    lignes = [entete, ""]
    verdict = ligne.get("verdict")
    if not isinstance(verdict, Mapping) or verdict.get("invalide"):
        return lignes
    for critere, valeur in (verdict.get("criteres") or {}).items():
        if isinstance(valeur, list):
            lignes.append(f"- `{critere}` :")
            for element in valeur:
                lignes.append(
                    f"  - {element.get('ref')} : {element.get('present')} — "
                    f"{_une_ligne(element.get('justification'))}"
                )
        elif isinstance(valeur, Mapping):
            lignes.append(
                f"- `{critere}` : {valeur.get('note')} — {_une_ligne(valeur.get('justification'))}"
            )
    inventions = verdict.get("inventions") or []
    lignes.append(
        "- Inventions : " + ("; ".join(str(i) for i in inventions) if inventions else "aucune")
    )
    lignes.append(f"- Confiance : {verdict.get('confiance')}")
    lignes.append("")
    return lignes


def rendre_relecture(
    items: Sequence[ItemBase],
    generations: Mapping[str, Generation],
    verdicts: Mapping[str, Sequence[Mapping[str, Any]]],
    controles: Mapping[str, Mapping[str, Any]],
) -> str:
    """Markdown de relecture des `items` (échantillon de relecture présent dans le run).

    `verdicts` associe à un item ses lignes de `verdicts.jsonl` (une par juge) ; un item sans
    génération est signalé, sans sortie.
    """
    lignes = [
        "# Relecture des verdicts",
        "",
        f"{len(items)} item(s) de l'échantillon de relecture. Les Scores restent « non relus » "
        f"tant que `{NOM_VALIDATION}` (objet JSON avec une clé `date` ISO) n'est pas déposé "
        "dans ce run.",
        "",
    ]
    for item in items:
        lignes += [f"## {item.id} ({item.code}, {item.difficulte})", ""]
        lignes += ["### Entrée", "", _bloc(rendre_entree(item)), ""]
        refs = _references(item)
        if refs is not None:
            lignes += ["### Références (vues par le Juge)", "", _bloc(refs), ""]
        generation = generations.get(item.id)
        if generation is None:
            lignes += ["Aucune génération pour cet item.", ""]
            continue
        lignes += [f"### Sortie (statut {generation.statut})", ""]
        sortie = generation.sortie_canonique.model_dump(mode="json")
        lignes += [_bloc(rendre_sortie(sortie)), ""]
        controle = controles.get(item.id)
        lignes += ["### Contrôles automatiques", ""]
        if controle:
            texte = json.dumps(controle, ensure_ascii=False, indent=2, sort_keys=True)
            lignes += [_bloc(texte), ""]
        else:
            lignes += ["Aucun.", ""]
        lignes += ["### Verdicts", ""]
        par_juge = verdicts.get(item.id) or []
        if not par_juge:
            lignes += ["Aucun verdict.", ""]
        for ligne in par_juge:
            lignes += _verdict(ligne)
    return "\n".join(lignes).rstrip("\n") + "\n"


def relecture_validee(dossier: str | Path) -> bool:
    """Vrai si `dossier` contient un `relecture-validee.json` objet à `date` ISO valide."""
    chemin = Path(dossier) / NOM_VALIDATION
    try:
        contenu = json.loads(chemin.read_text(encoding="utf-8-sig"))  # BOM de PowerShell 5.1
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(contenu, dict) or not isinstance(contenu.get("date"), str):
        return False
    valeur = contenu["date"]
    for lire in (date.fromisoformat, datetime.fromisoformat):
        try:
            lire(valeur)
        except ValueError:
            continue
        return True
    return False


def charger_scores(dossier: str | Path) -> Scores:
    """`scores.json` du run `dossier`, `verdicts_relus` posé selon `relecture_validee`."""
    dossier = Path(dossier)
    scores = Scores.model_validate_json((dossier / NOM_SCORES).read_bytes())
    relus = relecture_validee(dossier)
    for score in scores.taches.values():
        score.statuts.verdicts_relus = relus
    return scores


__all__ = [
    "NOM_RELECTURE",
    "NOM_SCORES",
    "NOM_VALIDATION",
    "charger_scores",
    "relecture_validee",
    "rendre_relecture",
]
