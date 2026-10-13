"""Mesures de coût d'un Run d'entraînement (story 10.3, FR-33, AD-18).

Un callback unique, indépendant de la méthode, mesure :

- la **durée** de l'entraînement ;
- le **débit** en tokens/s **hors padding**, après `pas_chauffe` pas (10 par défaut) : le
  chronomètre démarre à la fin du dernier pas de chauffe. Les tokens utiles d'un lot sont
  ceux dont le masque d'attention vaut 1 ; le collator ou l'entraîneur les déclare par
  `MesureurCouts.compter_lot(masque_attention)` ;
- la **VRAM maximale** : maximum entre `torch.cuda.max_memory_reserved` (la réservée couvre
  l'allouée, que l'on consigne aussi) et le pic `used` relevé par NVML ;
- l'**énergie** en Wh : intégrale (trapèzes) de la puissance NVML échantillonnée toutes les
  `periode_echantillonnage_ms` (200 ms) dans un fil dédié.

À la fin, les mesures vont dans `metriques.jsonl` (une ligne `type = "couts"`) et dans
`couts.json` du run. torch, transformers et pynvml sont importés dans les fonctions, jamais
au niveau du module : les tests injectent torch et NVML simulés.
"""

from __future__ import annotations

import importlib
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Protocol

from slmsp.core.canonique import json_canonique
from slmsp.train.config import ConfigCouts

__all__ = ["EchantillonneurNvml", "MesureurCouts", "creer_callback", "integrer_energie_wh"]

NOM_COUTS: Final = "couts.json"
NOM_METRIQUES: Final = "metriques.jsonl"


class _Run(Protocol):
    def ecrire(self, nom: str, contenu: Any) -> Any: ...
    def ajouter_jsonl(self, nom: str, obj: Any) -> None: ...


def integrer_energie_wh(releves: Sequence[tuple[float, float]]) -> float:
    """Énergie en Wh : intégrale trapézoïdale de relevés `(secondes, watts)`."""
    joules = 0.0
    for (t0, w0), (t1, w1) in zip(releves, releves[1:], strict=False):
        joules += (t1 - t0) * (w0 + w1) / 2
    return joules / 3600.0


@dataclass
class EchantillonneurNvml:
    """Relève puissance et mémoire utilisée du GPU `indice` (NVML), toutes les `periode_s`.

    `echantillonner(t)` prend un relevé daté ; `demarrer` lance un fil qui l'appelle à
    chaque période. Un NVML indisponible (module absent, init en échec) donne un
    échantillonneur inactif : les mesures NVML valent alors `None`.
    """

    periode_s: float
    nvml: Any = None
    indice: int = 0
    releves_w: list[tuple[float, float]] = field(default_factory=list)
    pic_octets: int | None = None
    actif: bool = False
    _poignee: Any = None
    _arret: threading.Event = field(default_factory=threading.Event)
    _fil: threading.Thread | None = None

    def ouvrir(self) -> None:
        if self.nvml is None:
            try:
                self.nvml = importlib.import_module("pynvml")
            except ImportError:
                return
        try:
            self.nvml.nvmlInit()
            self._poignee = self.nvml.nvmlDeviceGetHandleByIndex(self.indice)
        except Exception:
            self._poignee = None
            return
        self.actif = True

    def echantillonner(self, t: float) -> None:
        if not self.actif:
            return
        try:
            watts = self.nvml.nvmlDeviceGetPowerUsage(self._poignee) / 1000.0
            utilise = int(self.nvml.nvmlDeviceGetMemoryInfo(self._poignee).used)
        except Exception:
            return
        self.releves_w.append((t, watts))
        self.pic_octets = utilise if self.pic_octets is None else max(self.pic_octets, utilise)

    def demarrer(self, horloge: Callable[[], float]) -> None:
        self.ouvrir()
        if not self.actif:
            return
        self.echantillonner(horloge())

        def boucle() -> None:
            while not self._arret.wait(self.periode_s):
                self.echantillonner(horloge())

        self._fil = threading.Thread(target=boucle, name="slmsp-nvml", daemon=True)
        self._fil.start()

    def arreter(self, horloge: Callable[[], float]) -> None:
        if not self.actif:
            return
        self._arret.set()
        if self._fil is not None:
            self._fil.join(timeout=5)
        self.echantillonner(horloge())
        try:
            self.nvml.nvmlShutdown()
        except Exception:
            pass
        self.actif = False


class MesureurCouts:
    """Logique du callback de coût, sans dépendance à `transformers`."""

    def __init__(
        self,
        config: ConfigCouts,
        run: _Run,
        *,
        torch: Any = None,
        nvml: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
        echantillonner_en_fil: bool = True,
    ) -> None:
        self.config = config
        self.run = run
        self._torch = torch
        self._horloge = horloge
        self._en_fil = echantillonner_en_fil
        self.nvml = EchantillonneurNvml(config.periode_echantillonnage_ms / 1000.0, nvml)
        self.pas = 0
        self.tokens_utiles = 0
        self._tokens_apres_chauffe = 0
        self._debut: float | None = None
        self._debut_mesure: float | None = None
        self.mesures: dict[str, Any] | None = None

    def compter_lot(self, masque_attention: Iterable[Iterable[int]]) -> int:
        """Ajoute les tokens non-padding (masque à 1) d'un lot ; renvoie ce compte."""
        n = sum(1 for ligne in masque_attention for valeur in ligne if valeur)
        self.tokens_utiles += n
        if self._debut_mesure is not None:
            self._tokens_apres_chauffe += n
        return n

    def debut(self) -> None:
        self._debut = self._horloge()
        if self.config.pas_chauffe == 0:
            self._debut_mesure = self._debut
        if self._en_fil:
            self.nvml.demarrer(self._horloge)
        else:
            self.nvml.ouvrir()
            self.nvml.echantillonner(self._debut)

    def fin_de_pas(self) -> None:
        self.pas += 1
        if self.pas == self.config.pas_chauffe:
            self._debut_mesure = self._horloge()
            self._tokens_apres_chauffe = 0

    def echantillonner(self) -> None:
        """Relevé NVML à la demande (mode sans fil, pour les tests)."""
        self.nvml.echantillonner(self._horloge())

    def fin(self) -> dict[str, Any]:
        fin = self._horloge()
        if self._en_fil:
            self.nvml.arreter(self._horloge)
        else:
            self.nvml.echantillonner(fin)
        debut = self._debut if self._debut is not None else fin
        pas_mesures = max(self.pas - self.config.pas_chauffe, 0)
        debit = None
        if self._debut_mesure is not None and pas_mesures > 0 and fin > self._debut_mesure:
            debit = self._tokens_apres_chauffe / (fin - self._debut_mesure)
        torch = self._torch if self._torch is not None else importlib.import_module("torch")
        allouee = reservee = None
        if torch.cuda.is_available():
            allouee = int(torch.cuda.max_memory_allocated())
            reservee = int(torch.cuda.max_memory_reserved())
        sources = [v for v in (reservee, self.nvml.pic_octets) if v is not None]
        energie = integrer_energie_wh(self.nvml.releves_w) if self.nvml.releves_w else None
        self.mesures = {
            "duree_s": fin - debut,
            "pas": self.pas,
            "pas_chauffe": self.config.pas_chauffe,
            "pas_mesures": pas_mesures,
            "tokens_utiles": self.tokens_utiles,
            "tokens_par_seconde": debit,
            "vram_max_octets": max(sources) if sources else None,
            "vram_torch_allouee_octets": allouee,
            "vram_torch_reservee_octets": reservee,
            "vram_nvml_octets": self.nvml.pic_octets,
            "energie_wh": energie,
            "releves_puissance": len(self.nvml.releves_w),
            "periode_echantillonnage_ms": self.config.periode_echantillonnage_ms,
        }
        self.run.ajouter_jsonl(NOM_METRIQUES, {"type": "couts", **self.mesures})
        self.run.ecrire(NOM_COUTS, json_canonique(self.mesures).decode("utf-8") + "\n")
        return self.mesures


def creer_callback(mesureur: MesureurCouts) -> Any:
    """`TrainerCallback` branché sur `mesureur` (importe `transformers` à l'appel)."""
    from transformers import TrainerCallback  # noqa: PLC0415

    class CallbackCouts(TrainerCallback):
        def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            mesureur.debut()

        def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            mesureur.fin_de_pas()

        def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            mesureur.fin()

    return CallbackCouts()
