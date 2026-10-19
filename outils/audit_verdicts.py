"""Page HTML d'audit des verdicts des juges (principal Claude, second Mistral).

Le kappa entre les deux juges tombe à 0,00 sur plusieurs Tâches : cette page permet de relire,
item par item, les deux verdicts côte à côte, de dire qui a raison et d'en tirer des taux
d'accord. Lecture seule des runs et du Jeu d'évaluation ; seul le fichier de sortie est écrit.

Le HTML est autonome (CSS et JS en ligne, aucun réseau). Les textes sont passés en JSON
(`<script type="application/json">`) puis affichés par `textContent` : aucune injection possible.
Le gabarit HTML est dans `outils/audit_verdicts.gabarit.html`.

Usage :
  uv run python outils/audit_verdicts.py --notation <run_id> [--notation <run_id> ...]
      [--taches CR,LC,...] [--tous] [--racine <dépôt>] --sortie <fichier.html>
Par défaut seuls les items notés par les deux juges sont retenus (`--tous` garde les autres).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

GABARIT = Path(__file__).with_name("audit_verdicts.gabarit.html")

# Code de Tâche -> (nom, {clé de critère: (libellé, échelle, ancrage)}), d'après la grille du Juge.
TACHES: dict[str, tuple[str, dict[str, tuple[str, str, str]]]] = {
    "Q": (
        "Question",
        {
            "exactitude": (
                "Exactitude",
                "0 / 1 / 2",
                "2 : tous les éléments clés présents et justes. 1 : un élément clé manque ou est "
                "imprécis. 0 : erreur factuelle, contradiction avec la source, ou deux éléments "
                "clés manquants.",
            ),
            "pertinence_source": (
                "Pertinence de la source",
                "0 / 1",
                "1 : au moins une source citée traite du point demandé. 0 : sources hors sujet.",
            ),
            "cas_sans_reponse": (
                "Cas « sans réponse »",
                "0 / 1",
                "1 : l'Assistant dit ne pas avoir trouvé de source officielle et oriente. "
                "0 : il invente une réponse.",
            ),
        },
    ),
    "RD": (
        "Recherche de données",
        {
            "libelle_correct": (
                "Libellé correct",
                "0 / 1",
                "Libellé correct mais identifiant absent : le Juge tranche (0 ou 1).",
            )
        },
    ),
    "CR": (
        "Compte rendu",
        {
            "absence_invention": (
                "Absence d'invention",
                "0 / 1",
                "1 : rien d'absent des notes. 0 : au moins une invention, y compris un piège "
                "présenté comme décidé.",
            ),
            "presence_elements": (
                "Présence des éléments de référence",
                "0 / 0,5 / 1 par élément",
                "Décisions (D) et actions (A) de référence retrouvées dans le compte rendu ; une "
                "action sans responsable ou échéance connus compte pour moitié.",
            ),
            "structure": (
                "Structure",
                "0 / 1",
                "1 : les quatre sections (Participants, Points abordés, Décisions, Actions) sont "
                "présentes. Rapporté, hors score.",
            ),
        },
    ),
    "LC": (
        "Langage clair",
        {
            "fidelite": (
                "Fidélité",
                "0 / 1 / 2",
                "2 : sens intact, toutes les informations à conserver présentes. 1 : nuance perdue "
                "sans conséquence. 0 : montant, date, condition ou obligation modifié, supprimé "
                "ou ajouté.",
            ),
            "termes_juridiques": (
                "Termes juridiques",
                "0 / 1",
                "1 : les termes à conserver sont gardés, ou expliqués sans être remplacés à tort.",
            ),
            "clarte_percue": (
                "Clarté perçue",
                "1 à 5",
                "5 : un usager sans connaissance administrative comprend du premier coup. "
                "Rapporté, hors score.",
            ),
        },
    ),
    "CO": ("Correction (automatique)", {}),
    "RE": (
        "Résumé",
        {
            "fidelite": (
                "Fidélité",
                "0 / 1",
                "1 : aucune information absente du document ni déformée.",
            ),
            "presence_elements": (
                "Couverture des points clés",
                "0 / 0,5 / 1 par point",
                "Part des points clés de référence présents dans le résumé.",
            ),
        },
    ),
    "CT": (
        "Courrier type",
        {
            "conformite": (
                "Conformité",
                "0 / 1 / 2",
                "2 : tous les éléments obligatoires et le format administratif français. "
                "1 : un élément manque. 0 : deux manquent ou registre inadapté.",
            )
        },
    ),
    "NR": (
        "Non-régression",
        {
            "exactitude": (
                "Exactitude",
                "0 / 1",
                "Question : 1 si la réponse est juste. Consigne de rédaction : 1 si tous les "
                "critères sont respectés.",
            )
        },
    ),
}

# Champs du Jeu affichés comme « référence » : (champ, titre).
CHAMPS_REFERENCE: tuple[tuple[str, str], ...] = (
    ("reponse_reference", "Réponse de référence"),
    ("elements_cles", "Éléments clés"),
    ("sources_attendues", "Sources attendues"),
    ("criteres", "Critères attendus"),
    ("participants_reference", "Participants de référence"),
    ("decisions_reference", "Décisions de référence (D1, D2…)"),
    ("actions_reference", "Actions de référence (A1, A2…)"),
    ("pieges", "Pièges (à ne pas présenter comme décidés)"),
    ("informations_a_conserver", "Informations à conserver"),
    ("termes_juridiques_a_conserver", "Termes juridiques à conserver"),
    ("points_cles_reference", "Points clés de référence (P1, P2…)"),
    ("longueur_demandee", "Longueur demandée"),
    ("elements_obligatoires", "Éléments obligatoires"),
    ("champs_a_laisser_en_emplacement", "Champs à laisser en emplacement"),
    ("valeurs_interdites", "Valeurs interdites"),
    ("valeurs_attendues", "Valeurs attendues"),
    ("texte_corrige_reference", "Texte corrigé de référence"),
)
# Préfixe de référence d'un élément noté -> champ du Jeu.
PREFIXES_REF = {"D": "decisions_reference", "A": "actions_reference", "P": "points_cles_reference"}


def _lire_jsonl(chemin: Path) -> list[dict[str, Any]]:
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


def _texte(valeur: Any) -> str:
    if isinstance(valeur, str):
        return valeur
    return json.dumps(valeur, ensure_ascii=False, indent=2)


def _sections_entree(entree: Any) -> list[dict[str, str]]:
    """Entrée de l'item en sections `{titre, texte}` (la consigne d'abord)."""
    if isinstance(entree, dict):
        cles = sorted(entree, key=lambda cle: (cle != "consigne", cle))
        return [{"titre": cle, "texte": _texte(entree[cle])} for cle in cles]
    return [{"titre": "entrée", "texte": _texte(entree)}]


def _reference(item: dict[str, Any]) -> list[dict[str, str]]:
    sections = []
    for champ, titre in CHAMPS_REFERENCE:
        valeur = item.get(champ)
        if valeur in (None, "", [], {}):
            continue
        if isinstance(valeur, list):
            prefixe = {v: k for k, v in PREFIXES_REF.items()}.get(champ)
            lignes = [
                f"{prefixe}{rang} : {_texte(element)}" if prefixe else _texte(element)
                for rang, element in enumerate(valeur, 1)
            ]
            texte = "\n".join(lignes)
        else:
            texte = _texte(valeur)
        sections.append({"titre": titre, "texte": texte})
    return sections


def _libelle_ref(item: dict[str, Any], ref: str) -> str:
    champ = PREFIXES_REF.get(ref[:1])
    liste = item.get(champ) if champ else None
    if not isinstance(liste, list) or not ref[1:].isdigit():
        return ""
    rang = int(ref[1:]) - 1
    return _texte(liste[rang]) if 0 <= rang < len(liste) else ""


def _aplatir(
    code: str, criteres: dict[str, Any], item: dict[str, Any], alertes: list[str] | None = None
) -> dict[str, dict[str, Any]]:
    """Critères d'un verdict en `{clé: {note, justification, titre, description}}`.

    Les éléments d'un critère en liste (`ref`) gardent tous leur entrée : une réf en double ou
    absente reçoit un suffixe d'indice et un avertissement est ajouté à `alertes`.
    """
    noms = TACHES.get(code, ("", {}))[1]
    sortie: dict[str, dict[str, Any]] = {}
    vues: set[str] = set()
    for cle, valeur in criteres.items():
        libelle = noms[cle][0] if cle in noms else cle
        if isinstance(valeur, list):
            for rang, element in enumerate(valeur, 1):
                if not isinstance(element, dict):
                    continue
                ref = str(element.get("ref") or "?")
                cle_ref = f"{cle}:{ref}"
                if ref == "?" or cle_ref in vues:
                    motif = "absente" if ref == "?" else "en double"
                    if alertes is not None:
                        alertes.append(f"Référence {motif} dans « {cle} » ({ref}, rang {rang}).")
                    cle_ref = f"{cle_ref}#{rang}"
                vues.add(cle_ref)
                sortie[cle_ref] = {
                    "note": element.get("present"),
                    "justification": element.get("justification", ""),
                    "titre": f"{libelle} — {ref}",
                    "description": _libelle_ref(item, ref),
                }
        elif isinstance(valeur, dict):
            sortie[cle] = {
                "note": valeur.get("note"),
                "justification": valeur.get("justification", ""),
                "titre": libelle,
                "description": "",
            }
        elif isinstance(valeur, int | float | str) and valeur is not None:
            sortie[cle] = {"note": valeur, "justification": "", "titre": libelle, "description": ""}
    return sortie


def _kappas(scores: dict[str, Any]) -> dict[str, Any]:
    resultat = {}
    for code, bloc in (scores.get("taches") or {}).items():
        kappa = bloc.get("kappa") or {}
        resultat[code] = {
            "valeur": kappa.get("valeur"),
            "effectif": kappa.get("effectif"),
            "par_critere": kappa.get("par_critere") or {},
        }
    return resultat


def _item_audit(
    run_id: str,
    item_id: str,
    source: dict[str, Any],
    generation: dict[str, Any],
    verdicts: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    code = item_id.split("-")[0]
    sortie = generation.get("sortie_canonique") or {}
    alertes: list[str] = []
    if not source:
        alertes.append("Item introuvable dans le Jeu d'évaluation : entrée et référence absentes.")
    if not generation:
        alertes.append("Sortie introuvable dans les générations du run : sortie vide affichée.")
    aplatis = {
        nom: _aplatir(code, v["verdict"].get("criteres") or {}, source, alertes) if v else {}
        for nom, v in verdicts.items()
    }
    criteres = []
    for cle in dict.fromkeys([*aplatis["principal"], *aplatis["second"]]):
        a, b = aplatis["principal"].get(cle), aplatis["second"].get(cle)
        base = a or b or {}
        criteres.append(
            {
                "cle": cle,
                "titre": base["titre"],
                "description": base["description"],
                "principal": a,
                "second": b,
                "diverge": bool(a and b and a["note"] != b["note"]),
            }
        )
    return {
        "run": run_id,
        "id": item_id,
        "tache": code,
        "entree": _sections_entree(source.get("entree")),
        "sortie": sortie.get("texte") or "",
        "sources": [
            str(s.get("url") or s) if isinstance(s, dict) else str(s)
            for s in sortie.get("sources") or []
        ],
        "tronquee": bool(generation.get("tronquee")),
        "alertes": list(dict.fromkeys(alertes)),
        "reference": _reference(source),
        "criteres": criteres,
        "inventions": {
            nom: list(v["verdict"].get("inventions") or []) if v else None
            for nom, v in verdicts.items()
        },
    }


def charger_run(
    racine: Path, run_id: str, taches: set[str] | None, tous: bool
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Métadonnées du run et items à auditer (lecture seule)."""
    dossier = racine / "runs" / "eval-notation" / run_id
    if not dossier.is_dir():
        raise SystemExit(f"Notation introuvable : {dossier}")
    meta = json.loads((dossier / "run.json").read_text(encoding="utf-8"))
    scores = json.loads((dossier / "scores.json").read_text(encoding="utf-8"))
    run_gen = (meta.get("config") or {}).get("run_generation") or (meta.get("parents") or [""])[0]
    chemin_gen = racine / "runs" / "eval-generation" / run_gen / "generations.jsonl"
    generations = {ligne["item_id"]: ligne for ligne in _lire_jsonl(chemin_gen)}
    jeu_version = meta.get("jeu_version", "v1.1")
    jeu = {
        ligne["id"]: ligne
        for ligne in _lire_jsonl(racine / "eval" / "jeu" / jeu_version / "items.jsonl")
    }
    verdicts: dict[tuple[str, str], dict[str, Any]] = {}
    exclus: dict[str, int] = {}
    for ligne in _lire_jsonl(dossier / "verdicts.jsonl"):
        if ligne.get("statut") == "juge" and ligne.get("verdict"):
            verdicts[(ligne["item_id"], ligne["juge"])] = ligne
        else:
            nom = f"{ligne.get('juge', '?')} ({ligne.get('statut', '?')})"
            exclus[nom] = exclus.get(nom, 0) + 1
    run = {
        "id": run_id,
        "modele": meta.get("modele_ref", "?"),
        "jeu": jeu_version,
        "generation": run_gen,
        "kappa": _kappas(scores),
        "exclus": exclus,
    }
    items = []
    for item_id in sorted({cle[0] for cle in verdicts}):
        paire = {
            "principal": verdicts.get((item_id, "principal")),
            "second": verdicts.get((item_id, "second")),
        }
        code = item_id.split("-")[0]
        if (taches and code not in taches) or (not tous and not all(paire.values())):
            continue
        items.append(
            _item_audit(
                run_id, item_id, jeu.get(item_id, {}), generations.get(item_id) or {}, paire
            )
        )
    return run, items


def construire_donnees(
    racine: Path, runs: list[str], taches: set[str] | None, tous: bool = False
) -> dict[str, Any]:
    donnees_runs, items = [], []
    for run_id in runs:
        run, items_run = charger_run(racine, run_id, taches, tous)
        donnees_runs.append(run)
        items.extend(items_run)
    return {
        "genere_le": datetime.now(UTC).isoformat(timespec="seconds"),
        "runs": donnees_runs,
        "items": items,
        "taches": {
            code: {
                "nom": nom,
                "criteres": {
                    cle: {"titre": t, "echelle": e, "ancrage": a} for cle, (t, e, a) in crit.items()
                },
            }
            for code, (nom, crit) in TACHES.items()
        },
    }


def _json_sur(donnees: Any) -> str:
    """JSON insérable dans une balise `<script>` : aucune séquence ne peut la refermer."""
    brut = json.dumps(donnees, ensure_ascii=False)
    for car, rempl in (
        ("<", "\\u003c"),
        (">", "\\u003e"),
        ("&", "\\u0026"),
        (" ", "\\u2028"),
        (" ", "\\u2029"),
    ):
        brut = brut.replace(car, rempl)
    return brut


def produire_html(donnees: dict[str, Any]) -> str:
    return GABARIT.read_text(encoding="utf-8").replace("__DONNEES__", _json_sur(donnees))


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parseur.add_argument("--notation", action="append", required=True, metavar="RUN_ID")
    parseur.add_argument("--taches", help="codes de Tâche séparés par des virgules (ex. CR,LC)")
    parseur.add_argument("--tous", action="store_true", help="garde aussi les items sans 2e juge")
    parseur.add_argument(
        "--racine", type=Path, help="dépôt contenant runs/ et eval/ (lecture seule)"
    )
    parseur.add_argument("--sortie", type=Path, required=True)
    args = parseur.parse_args(argv)
    defaut = os.environ.get("SLMSP_RACINE") or Path(__file__).resolve().parents[1]
    racine = args.racine or Path(defaut)
    taches = (
        {t.strip().upper() for t in args.taches.split(",") if t.strip()} if args.taches else None
    )
    donnees = construire_donnees(racine, args.notation, taches, args.tous)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(produire_html(donnees), encoding="utf-8")
    items = donnees["items"]
    divergents = sum(1 for i in items if any(c["diverge"] for c in i["criteres"]))
    print(f"{args.sortie} : {len(items)} items, {divergents} avec désaccord entre juges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
