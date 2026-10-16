"""Mesure H-VEC : latence et mémoire de la recherche exacte dans l'Index local (AD-9).

Protocole :
1. les `requetes` vecteurs de requête (200) sont tirés sans remise parmi les vecteurs du
   corpus avec la graine de `config/index.toml` (42), copiés en float32, puis la vue mappée
   qui a servi au tirage est fermée ;
2. le run `runs/measure/<run_id>/` (slug `h-vec`, `index_version`) est créé ;
3. la mémoire résidente (RSS, `psutil`) est relevée avant l'ouverture de l'Index ;
4. l'Index est ouvert et chaque requête est chronométrée (`perf_counter_ns`), première
   comprise ;
5. la RSS est relevée après les requêtes : RAM ajoutée = RSS après − RSS avant (Mio).

Verdict `confirmee` si p95 ≤ `seuil_p95_ms` et RAM ajoutée ≤ `seuil_ram_mo`, sinon
`infirmee` avec le repli consigné (non implémenté). Le résultat (`ResultatMesure`) est écrit
en `resultat.json`, puis le run est terminé `complet`.
"""

from __future__ import annotations

import gc
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import numpy as np
import psutil
from numpy.typing import NDArray

from slmsp.core.artefacts import nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.mesure import ResultatMesure, Verdict
from slmsp.index.config import NOM_MANIFESTE, ConfigIndex, dossier_index, version_valide
from slmsp.index.lecture import IndexLocal, versions_disponibles

MESURE: Final = "h-vec"
HYPOTHESE: Final = "H-VEC"
NOM_RESULTAT: Final = "resultat.json"
REPLI_H_VEC: Final = (
    "index usearch HNSW i8 en vue mappée, dérivé du même .npy, derrière VectorStore : à faire"
)
MIO: Final = 1024**2


def rss_processus() -> int:
    """Mémoire résidente du processus courant, en octets."""
    return int(psutil.Process().memory_info().rss)


def pic_processus() -> int | None:
    """Pic du working set (Windows, `peak_wset`), en octets ; `None` ailleurs."""
    pic = getattr(psutil.Process().memory_info(), "peak_wset", None)
    return int(pic) if pic is not None else None


def percentiles(latences_ms: Any) -> dict[str, float]:
    """p50, p95, moyenne et maximum (ms) ; interpolation linéaire de numpy."""
    valeurs = np.asarray(latences_ms, dtype=np.float64)
    if valeurs.size == 0:
        raise ValueError("aucune latence mesurée")
    p50, p95 = np.percentile(valeurs, [50, 95])
    return {
        "p50_ms": float(p50),
        "p95_ms": float(p95),
        "moyenne_ms": float(valeurs.mean()),
        "max_ms": float(valeurs.max()),
    }


def verdict_h_vec(
    p95_ms: float, ram_ajoutee_mo: float, seuil_p95_ms: float, seuil_ram_mo: float
) -> tuple[Verdict, str | None]:
    """`confirmee` si les deux seuils tiennent, sinon `infirmee` avec le repli."""
    if p95_ms <= seuil_p95_ms and ram_ajoutee_mo <= seuil_ram_mo:
        return "confirmee", None
    return "infirmee", REPLI_H_VEC


def tirer_requetes(index: IndexLocal, nombre: int, graine: int) -> NDArray[np.float32]:
    """`nombre` vecteurs du corpus tirés sans remise (au plus `nb_chunks`), copiés en float32."""
    rng = np.random.default_rng(graine)
    rangs = rng.choice(index.nb_chunks, size=min(nombre, index.nb_chunks), replace=False)
    return np.array(index.vecteurs()[rangs], dtype=np.float32)


def version_index(racine: Path, version: str | None) -> str:
    if version is not None:
        if not version_valide(version) or not (dossier_index(racine) / version).is_dir():
            connues = ", ".join(versions_disponibles(racine)) or "aucune"
            raise ManifesteInvalide(
                f"version d'Index inconnue : {version!r} sous {dossier_index(racine)} "
                f"(connues : {connues})"
            )
        return version
    versions = versions_disponibles(racine)
    if not versions:
        raise ManifesteInvalide(
            f"aucun Index sous {dossier_index(racine)} : lancer `slmsp index build`"
        )
    return versions[-1]


def _chronometrer(
    index: IndexLocal, requetes: NDArray[np.float32], k: int
) -> tuple[list[float], int]:
    """Latence (ms) de chaque recherche (`classer` puis `passages`, soit `rechercher`).

    Renvoie aussi le nombre de requêtes dont le premier passage porte le vecteur même de la
    requête (contrôle hors chronomètre).
    """
    latences: list[float] = []
    soi = 0
    for requete in requetes:
        debut = time.perf_counter_ns()
        rangs, scores = index.classer(requete, k)
        index.passages(rangs, scores)
        latences.append((time.perf_counter_ns() - debut) / 1e6)
        if np.array_equal(index.vecteurs()[int(rangs[0])], requete.astype("<f2")):
            soi += 1
    return latences, soi


def mesurer_h_vec(
    racine: str | Path | None,
    version: str | None,
    config: ConfigIndex,
    *,
    rss: Callable[[], int] = rss_processus,
    pic: Callable[[], int | None] = pic_processus,
) -> ResultatMesure:
    """Mesure H-VEC sur l'Index `version` (le plus récent par défaut) de `racine`.

    Écrit `<racine>/runs/measure/<run_id>/resultat.json` (`run_id` dans le résultat) et
    termine le run `complet` ; en cas
    d'erreur, le run est terminé `partiel-erreur` et l'erreur relancée. Lève
    `ManifesteInvalide` si l'Index est absent ou incohérent.
    """
    racine = (Path(racine) if racine is not None else racine_projet()).resolve()
    version = version_index(racine, version)
    dossier = dossier_index(racine) / version
    mesure = config.mesure

    with IndexLocal(dossier, taille_bloc=config.taille_bloc) as index:
        nb_chunks = index.nb_chunks
        requetes = tirer_requetes(index, mesure.requetes, mesure.graine)

    parametres = {
        "requetes": int(len(requetes)),
        "requetes_demandees": mesure.requetes,
        "graine": mesure.graine,
        "k": mesure.k,
        "taille_bloc": config.taille_bloc,
        "nb_chunks": nb_chunks,
        "dimension": config.dimension,
    }
    seuils = {"p95_ms": float(mesure.seuil_p95_ms), "ram_mo": float(mesure.seuil_ram_mo)}
    run = nouveau_run(
        "measure",
        MESURE,
        {"hypothese": HYPOTHESE, **parametres, "seuils": seuils},
        entrees={"index/MANIFEST.json": dossier / NOM_MANIFESTE},
        graine=mesure.graine,
        racine=racine,
        index_version=version,
    )
    try:
        gc.collect()
        rss_avant = rss()
        index = IndexLocal(dossier, taille_bloc=config.taille_bloc)
        try:
            latences, soi = _chronometrer(index, requetes, mesure.k)
            rss_apres = rss()
            pic_octets = pic()
        finally:
            index.fermer()
        stats = percentiles(latences)
        ram_ajoutee_mo = (rss_apres - rss_avant) / MIO
        verdict, repli = verdict_h_vec(
            stats["p95_ms"], ram_ajoutee_mo, mesure.seuil_p95_ms, mesure.seuil_ram_mo
        )
        resultat = ResultatMesure(
            mesure=MESURE,
            hypothese=HYPOTHESE,
            run_id=run.run_id,
            mesure_le=datetime.now().astimezone(),
            index_version=version,
            parametres=parametres,
            valeurs={
                **stats,
                "ram_ajoutee_mo": ram_ajoutee_mo,
                "rss_avant_mo": rss_avant / MIO,
                "rss_apres_mo": rss_apres / MIO,
            },
            seuils=seuils,
            verdict=verdict,
            repli=repli,
            details={
                "premiere_requete_ms": latences[0],
                "pic_working_set_mo": None if pic_octets is None else pic_octets / MIO,
                "requetes_retrouvees_en_tete": soi,
                "unite_memoire": "Mio (1024² octets)",
                "chronometre": "time.perf_counter_ns, classement top-k puis lecture sqlite",
            },
        )
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
    "NOM_RESULTAT",
    "REPLI_H_VEC",
    "mesurer_h_vec",
    "percentiles",
    "rss_processus",
    "tirer_requetes",
    "verdict_h_vec",
]
