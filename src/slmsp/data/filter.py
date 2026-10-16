"""Étape `filter` : doublons et fuites du Jeu d'évaluation (story 9.5, FR-30, FR-24).

`lancer_filtre` produit `runs/data-filter/<run_id>/` à partir d'un run `data-validate` :

- `retenus.jsonl` : les lignes `SessionBrute` conservées, inchangées ;
- `rejets.jsonl` : `RejetExemple`, une ligne par session écartée ;
- `rapport.json` : par Tâche, nombre d'exemples, de rejets par motif et taux de rejet.

Pour chaque exemple, dans l'ordre de `valides.jsonl`, le premier motif qui s'applique l'écarte :

1. `fuite_ngram` : la réponse finale ou l'entrée (textes d'amorce du seed) recoupe un item du
   Jeu d'évaluation (v1.0, v1.1, calibrage) pour `Protection.recouvrement` au moins
   `anti_fuite.seuil_jaccard`. C'est le coefficient d'inclusion `|A ∩ B| / min(|A|, |B|)` des
   n-grammes hachés (`core.items`), déjà employé par `seed` : il détecte aussi un item repris
   à l'intérieur d'un texte plus long, ce que le Jaccard strict manque ;
2. `fuite_cosinus` : cosinus BGE-M3 (embedder partagé, AD-9) entre la réponse ou l'entrée et
   un vecteur d'entrée ou de référence d'item au moins égal à `anti_fuite.seuil_cosinus` ;
3. `doublon` : entrée et réponse identiques (texte normalisé) à un exemple déjà retenu, ou
   Jaccard de leurs n-grammes hachés au moins égal à `deduplication.seuil_jaccard` avec un
   exemple retenu de la même Tâche. Le premier exemple est gardé.

Le Jeu d'évaluation n'est vu qu'à travers l'API anti-fuite de `core.items` (empreintes et
vecteurs) : aucun texte d'item n'est lu ni écrit.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.items import VecteursAntifuite
from slmsp.core.ports import EmbedderPort
from slmsp.core.schemas.rejet_donnees import RejetExemple
from slmsp.core.schemas.session_donnees import SessionBrute
from slmsp.core.texte import normaliser
from slmsp.data.config import ConfigDonnees
from slmsp.data.seed import Protection, _empreintes_texte
from slmsp.data.validate import (
    NOM_RAPPORT,
    NOM_REJETS,
    NOM_VALIDES,
    LecteurGeneration,
    ouvrir_generation,
    statut_herite,
    taux_par_tache,
)
from slmsp.data.validate import TYPE_RUN as TYPE_RUN_VALIDATE
from slmsp.mistral.journal import JournalMistral

__all__ = ["NOM_RETENUS", "TYPE_RUN", "ResultatFiltre", "lancer_filtre"]

TYPE_RUN: Final = "data-filter"
NOM_RETENUS: Final = "retenus.jsonl"
TAILLE_LOT: Final = 64
"""Textes vectorisés par appel à l'embedder."""


@dataclass(frozen=True)
class ResultatFiltre:
    """Run produit, statut final et rapport."""

    run: Run
    statut: str
    rapport: dict[str, Any]


def _cosinus_max(
    embedder: EmbedderPort, textes: Sequence[str], items: VecteursAntifuite
) -> list[float]:
    """Plus grand cosinus de chaque texte avec un vecteur d'item (vecteurs renormalisés)."""
    import numpy as np

    if not textes or not len(items.cles):
        return [0.0] * len(textes)
    lots = [
        np.asarray(embedder.vectoriser(textes[i : i + TAILLE_LOT]), dtype=np.float32)
        for i in range(0, len(textes), TAILLE_LOT)
    ]
    vecteurs = np.concatenate(lots)
    norme = np.linalg.norm(vecteurs, axis=1, keepdims=True)
    norme_items = np.linalg.norm(items.matrice, axis=1, keepdims=True)
    produit = (vecteurs / np.where(norme == 0, 1, norme)) @ (
        items.matrice / np.where(norme_items == 0, 1, norme_items)
    ).T
    return [float(x) for x in produit.max(axis=1)]


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def lancer_filtre(
    *,
    racine: str | Path,
    validate_run_id: str,
    journal: JournalMistral,
    protection: Protection,
    vecteurs: VecteursAntifuite,
    embedder: EmbedderPort,
    config: ConfigDonnees,
    consigner: Callable[[str], None] = print,
) -> ResultatFiltre:
    """Crée `runs/data-filter/<run_id>/` depuis le run `data-validate` `validate_run_id`.

    Lève, sans rien écrire, `ManifesteInvalide` (run absent, d'un autre type, en cours, ou
    dont le run `data-generate` parent est illisible). Un appel ou une amorce introuvable lève
    `ProvenanceInvalide` après création du run, clos en `partiel-erreur`. Un run `validate`
    partiel rend le run `filter` partiel (`statut_herite`).
    """
    base = Path(racine).resolve()
    validate = ouvrir_run(validate_run_id, racine=base)
    if validate.type != TYPE_RUN_VALIDATE:
        raise ManifesteInvalide(
            f"run {validate_run_id} : type {validate.type!r}, {TYPE_RUN_VALIDATE} attendu"
        )
    if validate.statut_courant() == "en_cours":
        raise ManifesteInvalide(f"run {validate_run_id} encore en cours")
    generate_run_id = validate.manifeste.config.get("generate_run_id")
    if not isinstance(generate_run_id, str):
        raise ManifesteInvalide(f"run {validate_run_id} : run data-generate parent inconnu")
    lecteur = LecteurGeneration(ouvrir_generation(generate_run_id, base), journal, base)
    try:
        sessions = [
            SessionBrute.model_validate(ligne) for ligne in validate.lire_jsonl(NOM_VALIDES)
        ]
    except ValidationError:
        raise ManifesteInvalide(f"run {validate_run_id} : {NOM_VALIDES} illisible") from None

    entrees = {"valides": validate.dossier / NOM_VALIDES} if sessions else {}
    run = nouveau_run(
        TYPE_RUN,
        "filter",
        {
            "validate_run_id": validate_run_id,
            "generate_run_id": generate_run_id,
            "versions_protegees": list(protection.versions),
            "anti_fuite": config.anti_fuite.model_dump(mode="json"),
            "deduplication": config.deduplication.model_dump(mode="json"),
        },
        parents=[validate_run_id],
        entrees=entrees,
        racine=base,
    )
    try:
        retenus, rejets, comptes = _filtrer(
            lecteur, sessions, protection, vecteurs, embedder, config
        )
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    for brut in retenus:
        run.ajouter_jsonl(NOM_RETENUS, brut.model_dump(mode="json"))
    for rejet in rejets:
        run.ajouter_jsonl(NOM_REJETS, rejet.model_dump(mode="json"))
    statut, motif = statut_herite(validate, "complet", None)
    rapport = {
        "schema_version": 1,
        "statut": statut,
        "motif": motif,
        "taches": taux_par_tache(*comptes),
    }
    run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(statut, motif)
    consigner(f"filter : {len(retenus)} exemples retenus, {len(rejets)} rejets")
    return ResultatFiltre(run=run, statut=statut, rapport=rapport)


def _filtrer(
    lecteur: LecteurGeneration,
    sessions: Sequence[SessionBrute],
    protection: Protection,
    vecteurs: VecteursAntifuite,
    embedder: EmbedderPort,
    config: ConfigDonnees,
) -> tuple[list[SessionBrute], list[RejetExemple], tuple[Counter[str], dict[str, Counter[str]]]]:
    entrees: Counter[str] = Counter(s.tache for s in sessions)
    entree = {s.session_id: lecteur.entree(s) for s in sessions}
    reponse = {s.session_id: lecteur.reponse_finale(s) for s in sessions}
    rejets: dict[str, RejetExemple] = {}

    def rejeter(brut: SessionBrute, motif: str, detail: str) -> None:
        rejets[brut.session_id] = RejetExemple(
            session_id=brut.session_id,
            tache=brut.tache,
            etape="filter",
            motif=motif,  # type: ignore[arg-type]
            detail=detail,
        )

    for brut in sessions:
        recouvrement = max(
            protection.recouvrement(reponse[brut.session_id]),
            protection.recouvrement(entree[brut.session_id]),
        )
        if recouvrement >= protection.seuil:
            rejeter(brut, "fuite_ngram", f"recouvrement {recouvrement:.3f} >= {protection.seuil}")

    restants = [s for s in sessions if s.session_id not in rejets]
    textes = [t for s in restants for t in (reponse[s.session_id], entree[s.session_id])]
    cosinus = _cosinus_max(embedder, textes, vecteurs)
    seuil = config.anti_fuite.seuil_cosinus
    for rang, brut in enumerate(restants):
        meilleur = max(cosinus[2 * rang], cosinus[2 * rang + 1])
        if meilleur >= seuil:
            rejeter(brut, "fuite_cosinus", f"cosinus {meilleur:.3f} >= {seuil}")

    exacts: set[str] = set()
    proches: dict[str, list[frozenset[str]]] = {}
    seuil_doublon = config.deduplication.seuil_jaccard
    retenus: list[SessionBrute] = []
    for brut in sessions:
        if brut.session_id in rejets:
            continue
        texte = f"{entree[brut.session_id]}\n{reponse[brut.session_id]}"
        cle = sha256_hex(normaliser(texte))
        empreintes = frozenset(_empreintes_texte(texte, config.deduplication.n_ngrammes))
        deja = proches.setdefault(brut.tache, [])
        if cle in exacts:
            rejeter(brut, "doublon", "texte identique à un exemple retenu")
        elif any(_jaccard(empreintes, autre) >= seuil_doublon for autre in deja):
            rejeter(brut, "doublon", f"Jaccard >= {seuil_doublon} avec un exemple retenu")
        else:
            exacts.add(cle)
            deja.append(empreintes)
            retenus.append(brut)
    par_motif: dict[str, Counter[str]] = {}
    for rejet in rejets.values():
        par_motif.setdefault(rejet.tache, Counter())[rejet.motif] += 1
    ordonnes = [rejets[s.session_id] for s in sessions if s.session_id in rejets]
    return retenus, ordonnes, (entrees, par_motif)
