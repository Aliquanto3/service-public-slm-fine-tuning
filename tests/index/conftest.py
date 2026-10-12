"""Fabrique d'Index factice : `ecrire_index` sur des vecteurs aléatoires normalisés."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from slmsp.index.config import ConfigIndex, SourceIndex, charger_config_index
from slmsp.indexation.construction import SourceLue, ecrire_index


@dataclass
class IndexFactice:
    racine: Path
    dossier: Path
    version: str
    config: ConfigIndex
    vecteurs: np.ndarray
    """Vecteurs float16 de l'Index, dans l'ordre des rangs."""
    lignes: list[tuple[str, str, str, str, str, str]]
    """`(chunk_id, doc_id, source, titre, url, texte)` dans l'ordre des rangs."""


def vecteurs_aleatoires(n: int, dimension: int, graine: int) -> np.ndarray:
    """`n` vecteurs float16 normalisés L2 (normalisation en float32 puis conversion)."""
    rng = np.random.default_rng(graine)
    bruts = rng.standard_normal((n, dimension)).astype(np.float32)
    bruts /= np.linalg.norm(bruts, axis=1, keepdims=True)
    return bruts.astype(np.float16)


def source_lue(source: SourceIndex, n: int, graine: int, dimension: int) -> SourceLue:
    lignes = [
        (
            f"{source.nom}-c{i}",
            f"{source.nom}-d{i // 2}",
            f"<titre {source.nom} {i}>",
            f"https://exemple.invalid/{source.nom}/{i}",
            f"<texte factice {source.nom} {i}>",
        )
        for i in range(n)
    ]
    return SourceLue(
        source=source,
        vecteurs=vecteurs_aleatoires(n, dimension, graine),
        lignes=lignes,
        nb_ecartes=graine % 3,
        parquet={f"{source.nom}.parquet": "0" * 64},
    )


@pytest.fixture
def fabrique_index(tmp_path: Path) -> Callable[..., IndexFactice]:
    """Construit `<tmp>/index/<version>/` par `ecrire_index` ; renvoie ses données de référence."""
    config = charger_config_index()

    def fabriquer(
        tailles: Sequence[int] = (37, 25),
        *,
        graine: int = 7,
        dates: Sequence[date] | None = None,
        racine: Path | None = None,
        vecteurs: Sequence[np.ndarray] | None = None,
    ) -> IndexFactice:
        racine = racine or tmp_path
        sources = list(config.sources[: len(tailles)])
        if dates is not None:
            sources = [
                source.model_copy(update={"date_snapshot": jour})
                for source, jour in zip(sources, dates, strict=True)
            ]
        cfg = config.model_copy(update={"sources": sources})
        lues = [
            source_lue(source, n, graine + i, cfg.dimension)
            for i, (source, n) in enumerate(zip(sources, tailles, strict=True))
        ]
        if vecteurs is not None:
            for lue, imposes in zip(lues, vecteurs, strict=True):
                lue.vecteurs = np.asarray(imposes, dtype=np.float16)
        version = cfg.version()
        dossier = ecrire_index(racine / "index", version, lues, cfg)
        return IndexFactice(
            racine=racine,
            dossier=dossier,
            version=version,
            config=cfg,
            vecteurs=np.concatenate([lue.vecteurs for lue in lues]),
            lignes=[
                (chunk_id, doc_id, lue.source.nom, titre, url, texte)
                for lue in lues
                for chunk_id, doc_id, titre, url, texte in lue.lignes
            ],
        )

    return fabriquer
