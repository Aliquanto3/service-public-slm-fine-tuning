"""Mesure H-EMB : l'embedding de requête reproduit-il les vecteurs MediaTech ? (AD-9, FR-5)

Protocole :
1. `echantillon` chunks (200) sont tirés sans remise avec la graine (42) ;
2. leur texte (colonne `texte` de `chunks.sqlite`) est revectorisé par l'`EmbedderPort`
   (BGE-M3 GGUF Q8_0 servi par `llama-server`) ;
3. pour chaque chunk : cosinus entre le vecteur recalculé et le vecteur MediaTech de l'Index,
   puis recall@k = part des k plus proches voisins (recherche exacte) trouvés avec le vecteur
   MediaTech qui sont aussi trouvés avec le vecteur recalculé ;
4. le résultat (`ResultatMesure`) et le détail par chunk (`cosinus.json`) sont écrits dans un
   run `runs/measure/<run_id>/` (slug `h-emb`).

Verdict `confirmee` si le cosinus moyen ≥ `seuil_cosinus_moyen` et si le recall@k moyen ne
baisse pas de plus de `baisse_recall_max` (la référence MediaTech vaut 1 par construction) ;
sinon `infirmee` avec le repli consigné : refaire la mesure avec le GGUF F16 (`bge-m3-f16`),
la réindexation restant une décision d'Anaël. Le repli n'est pas implémenté ici.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import numpy as np
from numpy.typing import NDArray

from slmsp.core.artefacts import nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.ports import EmbedderPort
from slmsp.core.schemas.mesure import ResultatMesure, Verdict
from slmsp.index.config import NOM_MANIFESTE, ConfigIndex, dossier_index
from slmsp.index.lecture import IndexLocal
from slmsp.indexation.mesure_vec import version_index

MESURE: Final = "h-emb"
HYPOTHESE: Final = "H-EMB"
NOM_RESULTAT: Final = "resultat.json"
NOM_DETAIL: Final = "cosinus.json"
MODELE_DEFAUT: Final = "bge-m3"
MODELE_REPLI: Final = "bge-m3-f16"
REPLI_Q8: Final = (
    "refaire la mesure avec le GGUF F16 (bge-m3-f16, config/modeles/bge-m3-f16.toml à créer) ; "
    "la réindexation reste une décision pour Anaël"
)
REPLI_F16: Final = (
    "le GGUF F16 ne reproduit pas non plus les vecteurs MediaTech : "
    "réindexation avec le modèle servi, à décider par Anaël"
)


def repli_h_emb(modele: str) -> str:
    """Repli consigné quand H-EMB est infirmée pour `modele`."""
    return REPLI_F16 if modele == MODELE_REPLI else REPLI_Q8


def cosinus_par_ligne(
    recalcules: NDArray[np.float32], references: NDArray[np.floating]
) -> NDArray[np.float64]:
    """Cosinus ligne à ligne (normalisation explicite des deux côtés, en float64)."""
    a = np.asarray(recalcules, dtype=np.float64)
    b = np.asarray(references, dtype=np.float64)
    if a.shape != b.shape or a.ndim != 2:
        raise ValueError(f"formes incompatibles : {a.shape} et {b.shape}")
    normes = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    if np.any(normes == 0) or not np.all(np.isfinite(normes)):
        raise ValueError("vecteur nul ou non fini")
    return np.einsum("ij,ij->i", a, b) / normes


def recall_a_k(rangs_recalcules: NDArray[np.int64], rangs_references: NDArray[np.int64]) -> float:
    """Part des rangs de référence retrouvés par la recherche recalculée (0 à 1)."""
    if len(rangs_references) == 0:
        raise ValueError("aucun rang de référence")
    commun = set(map(int, rangs_recalcules)) & set(map(int, rangs_references))
    return len(commun) / len(rangs_references)


def verdict_h_emb(
    cosinus_moyen: float,
    recall_moyen: float,
    seuil_cosinus_moyen: float,
    baisse_recall_max: float,
    modele: str = MODELE_DEFAUT,
) -> tuple[Verdict, str | None]:
    """`confirmee` si les deux critères tiennent, sinon `infirmee` avec le repli."""
    # Tolérance d'arrondi flottant sur les bornes (0,99 et 1 - 0,02).
    tenu = cosinus_moyen >= seuil_cosinus_moyen - 1e-12 and (
        recall_moyen >= 1.0 - baisse_recall_max - 1e-12
    )
    if tenu:
        return "confirmee", None
    return "infirmee", repli_h_emb(modele)


def tirer_rangs(nb_chunks: int, echantillon: int, graine: int) -> NDArray[np.int64]:
    """`echantillon` rangs tirés sans remise (au plus `nb_chunks`), dans l'ordre du tirage."""
    rng = np.random.default_rng(graine)
    return rng.choice(nb_chunks, size=min(echantillon, nb_chunks), replace=False).astype(np.int64)


def _voisins(index: IndexLocal, vecteur: Any, k: int, rang: int) -> NDArray[np.int64]:
    """Les `k` plus proches voisins de `vecteur` hors du chunk `rang` lui-même."""
    rangs, _ = index.classer(vecteur, k + 1)
    return rangs[rangs != rang][:k]


def verifier_embedding(
    racine: str | Path | None,
    version: str | None,
    config: ConfigIndex,
    embedder: EmbedderPort,
    *,
    modele: str = MODELE_DEFAUT,
    echantillon: int | None = None,
    graine: int | None = None,
    serveur: Mapping[str, Any] | None = None,
) -> ResultatMesure:
    """Mesure H-EMB sur l'Index `version` (le plus récent par défaut) de `racine`.

    `echantillon` et `graine` valent par défaut ceux de `config.verification_embedding`.
    Écrit `resultat.json` et `cosinus.json` dans un run `measure` terminé `complet` ; en cas
    d'erreur, le run est terminé `partiel-erreur` et l'erreur relancée. Lève
    `ManifesteInvalide` si l'Index est absent ou incohérent, `ValueError` si l'embedder
    renvoie une forme inattendue. `serveur` (`ServeurLlama.description()` et sha256 du GGUF)
    est consigné dans `run.json` et `resultat.json` pour la provenance. Le chunk lui-même est
    exclu de ses voisins (recall@k sur k voisins autres que lui).
    """
    racine = (Path(racine) if racine is not None else racine_projet()).resolve()
    version = version_index(racine, version)
    dossier = dossier_index(racine) / version
    reglage = config.verification_embedding
    echantillon = reglage.echantillon if echantillon is None else echantillon
    graine = reglage.graine if graine is None else graine
    if echantillon <= 0:
        raise ValueError(f"échantillon > 0 attendu (reçu {echantillon})")
    if embedder.dimension != config.dimension:
        raise ManifesteInvalide(
            f"embedder de dimension {embedder.dimension}, Index de dimension {config.dimension}"
        )
    seuils = {
        "cosinus_moyen": reglage.seuil_cosinus_moyen,
        "recall_min": 1.0 - reglage.baisse_recall_max,
    }

    with IndexLocal(dossier, taille_bloc=config.taille_bloc) as index:
        rangs = tirer_rangs(index.nb_chunks, echantillon, graine)
        parametres = {
            "modele": modele,
            "echantillon": int(len(rangs)),
            "echantillon_demande": echantillon,
            "graine": graine,
            "k": reglage.k,
            "taille_bloc": config.taille_bloc,
            "nb_chunks": index.nb_chunks,
            "dimension": config.dimension,
        }
        if serveur is not None:
            parametres["serveur"] = dict(serveur)
        run = nouveau_run(
            "measure",
            MESURE,
            {"hypothese": HYPOTHESE, **parametres, "seuils": seuils},
            entrees={"index/MANIFEST.json": dossier / NOM_MANIFESTE},
            graine=graine,
            racine=racine,
            index_version=version,
        )
        try:
            passages = index.passages(rangs, np.zeros(len(rangs), dtype=np.float32))
            references = np.array(index.vecteurs()[rangs], dtype=np.float32)
            recalcules = np.asarray(
                embedder.vectoriser([p.texte for p in passages]), dtype=np.float32
            )
            if recalcules.shape != references.shape:
                raise ValueError(
                    f"embedder : forme {recalcules.shape}, {references.shape} attendue"
                )
            cosinus = cosinus_par_ligne(recalcules, references)
            recalls = []
            for rang, nouveau, ancien in zip(rangs, recalcules, references, strict=True):
                rangs_nouveaux = _voisins(index, nouveau, reglage.k, int(rang))
                rangs_anciens = _voisins(index, ancien, reglage.k, int(rang))
                recalls.append(recall_a_k(rangs_nouveaux, rangs_anciens))
            detail = [
                {
                    "rang": int(rang),
                    "chunk_id": passage.chunk_id,
                    "cosinus": float(c),
                    "recall": float(r),
                }
                for rang, passage, c, r in zip(rangs, passages, cosinus, recalls, strict=True)
            ]
            cosinus_moyen = float(cosinus.mean())
            recall_moyen = float(np.mean(recalls))
            verdict, repli = verdict_h_emb(
                cosinus_moyen,
                recall_moyen,
                reglage.seuil_cosinus_moyen,
                reglage.baisse_recall_max,
                modele,
            )
            resultat = ResultatMesure(
                mesure=MESURE,
                hypothese=HYPOTHESE,
                run_id=run.run_id,
                mesure_le=datetime.now().astimezone(),
                index_version=version,
                parametres=parametres,
                valeurs={
                    "cosinus_min": float(cosinus.min()),
                    "cosinus_moyen": cosinus_moyen,
                    "recall_moyen": recall_moyen,
                    "recall_min": float(min(recalls)),
                },
                seuils=seuils,
                verdict=verdict,
                repli=repli,
                details={
                    "detail_par_chunk": NOM_DETAIL,
                    "recall": f"recall@{reglage.k} : recherche exacte, vecteur recalculé "
                    "contre vecteur MediaTech",
                },
            )
            run.ecrire(NOM_DETAIL, json_canonique(detail) + b"\n")
            run.ecrire(NOM_RESULTAT, json_canonique(resultat.model_dump(mode="json")) + b"\n")
        except KeyboardInterrupt:
            run.terminer("interrompu", "arrêt demandé")
            raise
        except Exception as exc:
            run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
            raise
    run.terminer("complet")
    return resultat


__all__ = [
    "HYPOTHESE",
    "MESURE",
    "MODELE_DEFAUT",
    "MODELE_REPLI",
    "NOM_DETAIL",
    "NOM_RESULTAT",
    "cosinus_par_ligne",
    "recall_a_k",
    "repli_h_emb",
    "tirer_rangs",
    "verdict_h_emb",
    "verifier_embedding",
]
