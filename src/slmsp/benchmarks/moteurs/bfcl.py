"""Moteur BFCL (AD-16, AD-2) : lanceur maison et vérificateur AST isolé.

`bfcl-eval` vit dans l'environnement uv `envs/bfcl/` ; `slmsp` ne l'importe jamais. Ce moteur :

1. lit les questions des catégories `simple`, `multiple` et `irrelevance` sous
   `<jeu bfcl>/<revision>/` (`BFCL_v3_<cat>.json`, une ligne JSON par item : `id`, `question`,
   `function` ; `possible_answer/BFCL_v3_<cat>.json` : `id`, `ground_truth`)
   et les sous-échantillonne
   (`options.effectif`, 50 par catégorie par défaut, graine fixe) ;
2. envoie chaque question avec les `tools` natifs à `LlmPort.generer` (le client applique la
   voie `json-generique` du modèle si sa configuration la demande) ;
3. écrit les sorties en JSON (`<run>/bfcl/<variante>/sorties.json`) et appelle le
   vérificateur en sous-processus, `uv run --project envs/bfcl python envs/bfcl/verifier.py
   <sorties> <verdicts>`, avec `env_sous_processus()` (`SLMSP_BFCL_VERIFIER_CMD` le remplace).

Scores : `<categorie>.precision`, `<categorie>.n_items` et `moyenne.precision` (moyenne simple
des catégories) dans un seul `ResultatBench`.
"""

from __future__ import annotations

import json
import os
import random
import shlex
import subprocess
from contextlib import ExitStack
from pathlib import Path
from typing import TYPE_CHECKING, Any

from slmsp.benchmarks.moteurs import ContexteBench, SortieMoteur, appliquer_ordonne, lancer_outil
from slmsp.benchmarks.moteurs.llm import llm_gguf
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Jeton

if TYPE_CHECKING:
    from collections.abc import Sequence

    from slmsp.benchmarks.config import BenchmarkConfig
    from slmsp.core.ports import LlmPort

CATEGORIES = ("simple", "multiple", "irrelevance")
EFFECTIF_DEFAUT = 50
SEED = 1234
DELAI_VERIFICATEUR = 1800.0
VARIABLE_COMMANDE = "SLMSP_BFCL_VERIFIER_CMD"
OPTIONS_GENERATION = {"temperature": 0, "seed": SEED, "max_tokens": 1024}
TYPES_JSON = {"dict": "object", "float": "number", "tuple": "array", "any": "string"}
"""Types BFCL (Python) -> types JSON Schema des `tools` OpenAI."""


class BfclEchoue(RuntimeError):
    """Vérificateur en échec ou verdicts illisibles."""


# -- Questions --


def _schema(valeur: Any) -> Any:
    """Types BFCL convertis en types JSON Schema, récursivement."""
    if isinstance(valeur, dict):
        return {
            cle: TYPES_JSON.get(sous, sous)
            if cle == "type" and isinstance(sous, str)
            else _schema(sous)
            for cle, sous in valeur.items()
        }
    if isinstance(valeur, list):
        return [_schema(v) for v in valeur]
    return valeur


def nom_outil(nom: str) -> str:
    """Nom accepté par l'API (BFCL emploie des points : `math.factorial`)."""
    return nom.replace(".", "_")


def convertir_outils(fonctions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fonctions BFCL -> `tools` natifs OpenAI."""
    return [
        {
            "type": "function",
            "function": {
                "name": nom_outil(f["name"]),
                "description": f.get("description", ""),
                "parameters": _schema(f.get("parameters", {"type": "object", "properties": {}})),
            },
        }
        for f in fonctions
    ]


def messages_question(question: Any) -> list[dict[str, Any]]:
    """Tour utilisateur d'une entrée BFCL (`question` : liste de listes de messages)."""
    tours = question[0] if question and isinstance(question[0], list) else question
    return [{"role": m["role"], "content": m["content"]} for m in tours]


def lire_jsonl(chemin: Path) -> list[dict[str, Any]]:
    with chemin.open(encoding="utf-8") as flux:
        return [json.loads(ligne) for ligne in flux if ligne.strip()]


def charger_categorie(
    dossier: Path, categorie: str, effectif: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Questions sous-échantillonnées (graine fixe, triées par id) et réponses attendues."""
    questions = lire_jsonl(dossier / f"BFCL_v3_{categorie}.json")
    choisies = sorted(
        random.Random(SEED).sample(questions, min(effectif, len(questions))),
        key=lambda q: str(q["id"]),
    )
    reponses: dict[str, Any] = {}
    fichier = dossier / "possible_answer" / f"BFCL_v3_{categorie}.json"
    if categorie != "irrelevance":
        if not fichier.is_file():
            raise ConfigurationInvalide(
                f"réponses BFCL absentes pour `{categorie}` : {fichier} (`slmsp fetch benchmarks`)"
            )
        reponses = {str(r["id"]): r["ground_truth"] for r in lire_jsonl(fichier)}
        manquantes = [str(q["id"]) for q in choisies if str(q["id"]) not in reponses]
        if manquantes:
            raise ConfigurationInvalide(
                f"réponses BFCL manquantes pour `{categorie}` : {', '.join(manquantes[:5])}"
            )
    return choisies, reponses


# -- Génération --


def appeler(llm: LlmPort, question: dict[str, Any]) -> dict[str, Any]:
    """Une question : appels d'outils émis (noms BFCL d'origine), texte et appels non conformes."""
    originaux = {nom_outil(f["name"]): f["name"] for f in question["function"]}
    texte, appels, non_conformes = [], [], []
    flux = llm.generer(
        messages_question(question["question"]),
        tools=convertir_outils(question["function"]),
        options=OPTIONS_GENERATION,
    )
    for evenement in flux:
        if isinstance(evenement, Jeton):
            texte.append(evenement.texte)
        elif isinstance(evenement, AppelOutil):
            appels.append({originaux.get(evenement.nom, evenement.nom): evenement.arguments})
        elif isinstance(evenement, AppelNonConforme):
            non_conformes.append(evenement.motif)
    return {
        "id": str(question["id"]),
        "appels": appels,
        "texte": "".join(texte),
        "non_conformes": non_conformes,
    }


# -- Vérificateur --


def commande_verificateur(entree: Path, sortie: Path) -> list[str]:
    brute = os.environ.get(VARIABLE_COMMANDE, "").strip()
    if brute:
        base = [m.strip(chr(34)) for m in shlex.split(brute, posix=os.name != "nt")]
    else:
        base = ["uv", "run", "--project", "envs/bfcl", "python", "envs/bfcl/verifier.py"]
    return [*base, str(entree), str(sortie)]


def verifier(entree: Path, sortie: Path) -> dict[str, Any]:
    """Appelle le vérificateur en sous-processus et rend ses verdicts."""
    sortie.unlink(missing_ok=True)  # jamais de verdicts périmés d'un run précédent
    try:
        fin = lancer_outil(
            commande_verificateur(entree, sortie), cwd=racine_projet(), timeout=DELAI_VERIFICATEUR
        )
    except subprocess.TimeoutExpired as exc:
        raise BfclEchoue(f"vérificateur BFCL sans réponse après {DELAI_VERIFICATEUR} s") from exc
    if fin.returncode != 0:
        queue = (fin.stderr or fin.stdout or "").strip()[-600:]
        raise BfclEchoue(f"vérificateur BFCL en échec (code {fin.returncode}) : {queue}")
    try:
        return json.loads(sortie.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BfclEchoue(f"verdicts BFCL illisibles ({sortie}) : {exc}") from exc


def analyser(verdicts: dict[str, Any], attendues: Sequence[str] | None = None) -> SortieMoteur:
    """Verdicts -> précision et effectif par catégorie.

    `moyenne.precision` : moyenne simple des précisions de TOUTES les catégories attendues
    (simple, multiple et irrelevance par défaut). Une catégorie attendue absente ou sans
    précision supprime l'agrégat, pour que le Comparatif ne mélange pas des compositions."""
    categories = verdicts.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise BfclEchoue("verdicts BFCL sans section `categories`")
    scores: dict[str, float | int | None] = {}
    for categorie, bilan in categories.items():
        scores[f"{categorie}.precision"] = bilan["precision"]
        scores[f"{categorie}.n_items"] = bilan["n_items"]
    attendues = list(attendues) if attendues is not None else list(CATEGORIES)
    precisions = [(categories.get(c) or {}).get("precision") for c in attendues]
    if attendues and all(p is not None for p in precisions):  # métrique unique du Comparatif
        scores["moyenne.precision"] = sum(precisions) / len(precisions)  # type: ignore[arg-type]
    version = verdicts.get("bfcl_eval_version")
    return SortieMoteur(
        scores=scores,
        outil="bfcl-eval",
        outil_version=version,
        details={"categories": categories},
    )


# -- Exécution --


def _dossier_jeu(
    config: BenchmarkConfig, contexte: ContexteBench
) -> tuple[Path | None, str | None]:
    if not config.jeux:
        return None, "jeu BFCL non déclaré dans la configuration du benchmark"
    jeu = config.jeux[0]
    if not jeu.revision:
        return None, f"jeu {jeu.nom} non épinglé (voir `slmsp fetch benchmarks`)"
    dossier = contexte.dossier_jeux / jeu.nom / str(jeu.revision)
    if not dossier.is_dir():
        return None, f"jeu {jeu.nom} absent : {dossier} (`slmsp fetch benchmarks`)"
    return dossier, None


def executer(
    config: BenchmarkConfig, contexte: ContexteBench, *, llm: LlmPort | None = None
) -> SortieMoteur:
    """Questions BFCL -> modèle -> sorties JSON -> vérificateur isolé -> précision."""
    dossier, motif = _dossier_jeu(config, contexte)
    if dossier is None:
        return SortieMoteur(saute=motif)
    categories = list(config.options.get("categories", CATEGORIES))
    inconnues = [c for c in categories if c not in CATEGORIES]
    if inconnues:
        raise ConfigurationInvalide(f"catégories BFCL inconnues : {', '.join(inconnues)}")
    effectif = int(config.limite or config.options.get("effectif", EFFECTIF_DEFAUT))
    donnees: dict[str, Any] = {"categories": {}}
    with ExitStack() as pile:
        if llm is None:
            try:
                llm = pile.enter_context(llm_gguf(config, contexte))
            except ConfigurationInvalide as exc:
                return SortieMoteur(saute=f"modèle non servable ({contexte.variante}) : {exc}")
        for categorie in categories:
            questions, reponses = charger_categorie(dossier, categorie, effectif)
            sorties = appliquer_ordonne(
                lambda q, llm=llm: appeler(llm, q), questions, contexte.parallele
            )
            donnees["categories"][categorie] = [
                {**sortie, "fonctions": q["function"], "reponse": reponses.get(str(q["id"]))}
                for q, sortie in zip(questions, sorties, strict=True)
            ]
    sortie_dir = contexte.run.dossier / "bfcl" / contexte.variante
    sortie_dir.mkdir(parents=True, exist_ok=True)
    entree, verdicts_json = sortie_dir / "sorties.json", sortie_dir / "verdicts.json"
    entree.write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")
    resultat = analyser(verifier(entree, verdicts_json), categories)
    resultat.seed = SEED
    resultat.batch_size = "1"
    resultat.details["sorties_json"] = str(entree)
    return resultat


__all__ = ["BfclEchoue", "analyser", "convertir_outils", "executer"]
