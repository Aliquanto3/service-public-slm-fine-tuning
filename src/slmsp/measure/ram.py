"""Échantillonneur de la RAM de l'Assistant complet (FR-26, NFR-1, H-RAM).

Relève toutes les `periode_s` (100 ms) la somme des working sets du processus Python et de
tous ses descendants (les deux `llama-server`), et garde le pic. Le working set est lu par
`psutil` (`wset` sous Windows, `rss` ailleurs) ; un processus qui disparaît entre-temps est
ignoré.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from types import TracebackType
from typing import Final

import psutil

PERIODE_S: Final = 0.1


def working_set(processus: psutil.Process) -> int:
    """Working set (octets) d'un processus ; 0 s'il a disparu ou s'il est inaccessible."""
    try:
        info = processus.memory_info()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0
    return int(getattr(info, "wset", info.rss))


def somme_arbre(racine: psutil.Process) -> int:
    """Somme des working sets de `racine` et de ses descendants."""
    try:
        processus = [racine, *racine.children(recursive=True)]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        processus = [racine]
    return sum(working_set(p) for p in processus)


class EchantillonneurRam:
    """Contexte qui échantillonne l'arbre de processus de `racine` (défaut : le courant)."""

    def __init__(
        self,
        racine: psutil.Process | None = None,
        periode_s: float = PERIODE_S,
        lire: Callable[[psutil.Process], int] = somme_arbre,
    ) -> None:
        self._racine = racine or psutil.Process()
        self._periode = periode_s
        self._lire = lire
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None
        self.pic_octets = 0
        self.nb_echantillons = 0

    def _echantillonner(self) -> None:
        octets = self._lire(self._racine)
        self.nb_echantillons += 1
        self.pic_octets = max(self.pic_octets, octets)

    def _boucle(self) -> None:
        while not self._arret.wait(self._periode):
            self._echantillonner()

    def __enter__(self) -> EchantillonneurRam:
        self._echantillonner()
        self._arret.clear()
        self._fil = threading.Thread(target=self._boucle, name="echantillonneur-ram", daemon=True)
        self._fil.start()
        return self

    def __exit__(
        self,
        type_exc: type[BaseException] | None,
        exc: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        self._arret.set()
        if self._fil is not None:
            self._fil.join()
        self._echantillonner()
