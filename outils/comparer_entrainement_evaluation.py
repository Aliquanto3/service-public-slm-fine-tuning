"""Rapport Markdown : gabarit et longueurs du message user, évaluation contre entraînement.

Pour chaque Tâche : suite des sections du message user (« Consigne : / Texte : »…) à
l'évaluation (items du Jeu, rendus par la règle de `harness.prompts`) et à l'entraînement
(`train.jsonl`), médiane et quartiles du nombre de mots d'entrée (consigne exclue, comme
`evaluation.gel`) et de réponse. Lecture seule : le Jeu n'est lu que pour des statistiques,
aucun texte d'item ni de consigne n'est recopié dans le rapport.

Usage :
  uv run python outils/comparer_entrainement_evaluation.py --train data/train/v14/train.jsonl
      --items eval/jeu/v1.1/items.jsonl [--sortie rapport.md]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from slmsp.harness.prompts import LIBELLES_CLES, ORDRE_CLES, SYNONYMES_CLES

CODES_ORDRE = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR", "generique")
_ENTETE_PASSAGES = "Passages de l'Index local"
_LIBELLES = sorted({*LIBELLES_CLES.values(), _ENTETE_PASSAGES}, key=len, reverse=True)
_RE_SECTION = re.compile(
    r"^(" + "|".join(re.escape(libelle) for libelle in _LIBELLES) + r") :[ \t]*$", re.MULTILINE
)
_CHAMPS_REPONSE = ("reponse_reference", "texte_corrige_reference")


def _mots(texte: str) -> int:
    return len(texte.split())


def _mots_hors_consigne(valeur: Any) -> int:
    if isinstance(valeur, str):
        return _mots(valeur)
    if isinstance(valeur, dict):
        return sum(
            _mots_hors_consigne(v) for k, v in valeur.items() if k not in ("consigne", "nb_mots")
        )
    if isinstance(valeur, list):
        return sum(_mots_hors_consigne(v) for v in valeur)
    return 0


def sections_message(contenu: str) -> list[tuple[str, str]]:
    """Sections `(libellé, texte)` d'un message user rendu ; `[("(texte brut)", contenu)]` sinon."""
    reperes = list(_RE_SECTION.finditer(contenu))
    if not reperes:
        return [("(texte brut)", contenu)]
    sections = []
    for i, repere in enumerate(reperes):
        fin = reperes[i + 1].start() if i + 1 < len(reperes) else len(contenu)
        sections.append((repere.group(1), contenu[repere.end() : fin]))
    return sections


def gabarit_entrainement(contenu: str) -> str:
    return " / ".join(libelle for libelle, _ in sections_message(contenu))


def mots_entree_entrainement(contenu: str) -> int:
    consigne = LIBELLES_CLES["consigne"]
    return sum(_mots(t) for lib, t in sections_message(contenu) if lib != consigne)


def gabarit_evaluation(entree: Any) -> str:
    if not isinstance(entree, dict):
        return "(texte brut)"
    cles = {SYNONYMES_CLES.get(k, k) for k in entree}
    return " / ".join(LIBELLES_CLES[k] for k in ORDRE_CLES if k in cles)


def _code(item: dict[str, Any]) -> str:
    return str(item.get("id", "")).split("-", 1)[0]


def _reponse_evaluation(item: dict[str, Any]) -> int | None:
    for champ in _CHAMPS_REPONSE:
        valeur = item.get(champ)
        if isinstance(valeur, str) and valeur.strip():
            return _mots(valeur)
    return None


def _lire_jsonl(chemin: Path) -> list[dict[str, Any]]:
    with chemin.open(encoding="utf-8") as flux:
        return [json.loads(ligne) for ligne in flux if ligne.strip()]


def _quartiles(valeurs: list[int]) -> str:
    if not valeurs:
        return "n/d"
    if len(valeurs) < 2:
        return f"{valeurs[0]} (n=1)"
    q1, med, q3 = statistics.quantiles(valeurs, n=4, method="inclusive")
    return f"{med:g} [{q1:g} ; {q3:g}] (n={len(valeurs)})"


def _gabarit_majoritaire(gabarits: list[str]) -> str:
    if not gabarits:
        return "n/d"
    return Counter(gabarits).most_common(1)[0][0]


def _vide() -> dict[str, list[Any]]:
    return {"gabarits": [], "entree": [], "reponse": []}


def statistiques_entrainement(lignes: list[dict[str, Any]]) -> dict[str, dict[str, list[Any]]]:
    par_tache: dict[str, dict[str, list[Any]]] = defaultdict(_vide)
    for ligne in lignes:
        messages = ligne.get("messages") or []
        user = next((m for m in messages if m.get("role") == "user"), None)
        reponse = next((m for m in reversed(messages) if m.get("role") == "assistant"), None)
        if user is None or not isinstance(user.get("content"), str):
            continue
        stat = par_tache[ligne.get("tache", "?")]
        stat["gabarits"].append(gabarit_entrainement(user["content"]))
        stat["entree"].append(mots_entree_entrainement(user["content"]))
        if reponse and isinstance(reponse.get("content"), str):
            stat["reponse"].append(_mots(reponse["content"]))
    return par_tache


def statistiques_evaluation(items: list[dict[str, Any]]) -> dict[str, dict[str, list[Any]]]:
    par_tache: dict[str, dict[str, list[Any]]] = defaultdict(_vide)
    for item in items:
        stat = par_tache[_code(item)]
        stat["gabarits"].append(gabarit_evaluation(item.get("entree")))
        stat["entree"].append(_mots_hors_consigne(item.get("entree")))
        mots = _reponse_evaluation(item)
        if mots is not None:
            stat["reponse"].append(mots)
    return par_tache


def rapport(train: list[dict[str, Any]], items: list[dict[str, Any]], *, noms: str = "") -> str:
    ent = statistiques_entrainement(train)
    evl = statistiques_evaluation(items)
    taches = [t for t in CODES_ORDRE if t in ent or t in evl]
    taches += sorted((set(ent) | set(evl)) - set(taches))
    sortie = ["# Comparaison entraînement / évaluation", ""]
    if noms:
        sortie += [noms, ""]
    sortie += [
        "Mots d'entrée : message user hors section « Consigne ». Réponse d'évaluation : champ "
        "de référence textuel quand l'item en porte un (sinon n/d). Médiane [Q1 ; Q3].",
        "",
        "| Tâche | Gabarit évaluation | Gabarit entraînement | Entrée éval. (mots) "
        "| Entrée entr. (mots) | Rapport médianes | Réponse éval. | Réponse entr. |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for tache in taches:
        e, v = ent.get(tache), evl.get(tache)
        med_e = statistics.median(e["entree"]) if e and e["entree"] else None
        med_v = statistics.median(v["entree"]) if v and v["entree"] else None
        rapport_med = f"{med_v / med_e:.1f}" if med_e and med_v else "n/d"
        sortie.append(
            f"| {tache} | {_gabarit_majoritaire(v['gabarits']) if v else 'n/d'} "
            f"| {_gabarit_majoritaire(e['gabarits']) if e else 'n/d'} "
            f"| {_quartiles(v['entree']) if v else 'n/d'} "
            f"| {_quartiles(e['entree']) if e else 'n/d'} | {rapport_med} "
            f"| {_quartiles(v['reponse']) if v else 'n/d'} "
            f"| {_quartiles(e['reponse']) if e else 'n/d'} |"
        )
    sortie += [
        "",
        "Rapport médianes = médiane d'entrée à l'évaluation / à l'entraînement : au-delà de 1,3 "
        "ou sous 0,7, l'écart de longueur dépasse la tolérance visée par la story O5.",
        "",
    ]
    return "\n".join(sortie)


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--train", type=Path, required=True, help="train.jsonl d'une version")
    parseur.add_argument("--items", type=Path, required=True, help="items.jsonl du Jeu")
    parseur.add_argument("--sortie", type=Path, help="fichier Markdown (défaut : sortie standard)")
    args = parseur.parse_args(argv)
    texte = rapport(
        _lire_jsonl(args.train),
        _lire_jsonl(args.items),
        noms=(
            f"Entraînement : `{args.train.parent.name}` ; évaluation : `{args.items.parent.name}`."
        ),
    )
    if args.sortie:
        args.sortie.write_text(texte, encoding="utf-8")
    else:
        sys.stdout.buffer.write(texte.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
