"""Story 10.3 : mesures de coût d'un Run (FR-33, AD-18).

Un callback unique, indépendant de la méthode, mesure :
- la durée de l'entraînement ;
- le débit en tokens/s hors padding, après `pas_chauffe` pas de chauffe (compteur
  `state.num_input_tokens_seen`, qui exclut le padding avec
  `include_num_input_tokens_seen="non_padding"` dans les arguments d'entraînement) ;
- la VRAM maximale : maximum de `torch.cuda.max_memory_reserved` et de l'échantillonnage NVML
  (`max_memory_allocated` est relevée à part) ;
- l'énergie en Wh : intégrale (trapèzes) de la puissance NVML échantillonnée toutes les
  `periode_echantillonnage_ms`.

Les mesures vont dans `metriques.jsonl` et `couts.json` du run. torch est importé dans les
fonctions seulement ; NVML (`pynvml`), l'horloge et torch sont injectables pour les tests.
"""

from __future__ import annotations

import importlib
import json
import threading
import time
from collections.abc import Callable
from typing import Any

from slmsp.train.config import ConfigCouts

NOM_COUTS = "couts.json"
NOM_METRIQUES = "metriques.jsonl"
JOULES_PAR_WH = 3600.0


def _importer(nom: str) -> Any:
    try:
        return importlib.import_module(nom)
    except Exception:
        return None


class EchantillonneurNvml:
    """Relève la puissance (W) et la VRAM utilisée ; intègre l'énergie par trapèzes."""

    def __init__(
        self,
        nvml: Any,
        *,
        indice: int = 0,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self._nvml = nvml
        self._indice = indice
        self._horloge = horloge
        self._poignee: Any = None
        self.actif = False
        self.energie_j = 0.0
        self.vram_max_octets: int | None = None
        self.echantillons = 0
        self._dernier: tuple[float, float] | None = None
        self._verrou = threading.Lock()

    def demarrer(self) -> bool:
        """Initialise NVML ; `False` (mesures NVML absentes) si indisponible."""
        if self._nvml is None:
            return False
        try:
            self._nvml.nvmlInit()
            self._poignee = self._nvml.nvmlDeviceGetHandleByIndex(self._indice)
        except Exception:
            return False
        self.actif = True
        return True

    def echantillonner(self) -> None:
        if not self.actif:
            return
        try:
            puissance_w = float(self._nvml.nvmlDeviceGetPowerUsage(self._poignee)) / 1000.0
            utilisee = int(self._nvml.nvmlDeviceGetMemoryInfo(self._poignee).used)
        except Exception:
            return
        maintenant = self._horloge()
        with self._verrou:
            if self._dernier is not None:
                t0, p0 = self._dernier
                self.energie_j += (maintenant - t0) * (p0 + puissance_w) / 2.0
            self._dernier = (maintenant, puissance_w)
            if self.vram_max_octets is None or utilisee > self.vram_max_octets:
                self.vram_max_octets = utilisee
            self.echantillons += 1

    def arreter(self) -> None:
        if not self.actif:
            return
        self.echantillonner()
        self.actif = False
        try:
            self._nvml.nvmlShutdown()
        except Exception:
            pass

    @property
    def energie_wh(self) -> float | None:
        return self.energie_j / JOULES_PAR_WH if self.echantillons else None


class CallbackCouts:
    """`TrainerCallback` de mesure du coût (duck-typing : pas d'import de transformers).

    Les événements non traités (`on_*`) sont des no-op, comme dans `TrainerCallback`.
    """

    def __init__(
        self,
        config: ConfigCouts,
        run: Any,
        *,
        nvml: Any = None,
        torch: Any = None,
        horloge: Callable[[], float] = time.monotonic,
        indice_gpu: int = 0,
        avec_fil: bool = True,
    ) -> None:
        self.config = config
        self.run = run
        self._horloge = horloge
        self._torch = torch
        self._avec_fil = avec_fil
        self.echantillonneur = EchantillonneurNvml(nvml, indice=indice_gpu, horloge=horloge)
        self.resultat: dict[str, Any] | None = None
        self._debut: float | None = None
        self._depart_mesure: tuple[float, int] | None = None
        self._pas = 0
        self._tokens = 0
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None

    def __getattr__(self, nom: str) -> Callable[..., None]:
        if nom.startswith("on_"):
            return lambda *args, **kwargs: None
        raise AttributeError(nom)

    def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
        self._debut = self._horloge()
        if self.echantillonneur.demarrer():
            self.echantillonneur.echantillonner()
            if self._avec_fil:
                self._fil = threading.Thread(target=self._boucle, name="couts-nvml", daemon=True)
                self._fil.start()

    def _boucle(self) -> None:
        periode = self.config.periode_echantillonnage_ms / 1000.0
        while not self._arret.wait(periode):
            self.echantillonneur.echantillonner()

    def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
        self._pas = int(state.global_step)
        self._tokens = int(getattr(state, "num_input_tokens_seen", 0) or 0)
        if self._depart_mesure is None and self._pas >= self.config.pas_chauffe:
            self._depart_mesure = (self._horloge(), self._tokens)

    def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
        fin = self._horloge()
        self._arret.set()
        if self._fil is not None:
            self._fil.join(timeout=5)
        self.echantillonneur.arreter()
        self._pas = int(getattr(state, "global_step", self._pas))
        self._tokens = int(getattr(state, "num_input_tokens_seen", self._tokens) or self._tokens)
        self.resultat = self._calculer(fin)
        self.run.ajouter_jsonl(NOM_METRIQUES, {"type": "couts", **self.resultat})
        self.run.ecrire(NOM_COUTS, json.dumps(self.resultat, indent=2, sort_keys=True) + "\n")

    def _calculer(self, fin: float) -> dict[str, Any]:
        duree = fin - self._debut if self._debut is not None else None
        debit = None
        tokens_mesures = None
        if self._depart_mesure is not None:
            t0, tokens0 = self._depart_mesure
            tokens_mesures = self._tokens - tokens0
            if fin > t0 and tokens_mesures > 0:
                debit = tokens_mesures / (fin - t0)
        alloue, reserve = self._vram_torch()
        sources = [v for v in (reserve, self.echantillonneur.vram_max_octets) if v is not None]
        return {
            "duree_s": duree,
            "pas": self._pas,
            "pas_chauffe": self.config.pas_chauffe,
            "tokens_hors_padding": self._tokens,
            "tokens_mesures": tokens_mesures,
            "tokens_par_s": debit,
            "vram_allouee_max_octets": alloue,
            "vram_reservee_max_octets": reserve,
            "vram_nvml_max_octets": self.echantillonneur.vram_max_octets,
            "vram_max_octets": max(sources) if sources else None,
            "energie_wh": self.echantillonneur.energie_wh,
            "echantillons_nvml": self.echantillonneur.echantillons,
            "periode_echantillonnage_ms": self.config.periode_echantillonnage_ms,
        }

    def _vram_torch(self) -> tuple[int | None, int | None]:
        torch = self._torch if self._torch is not None else _importer("torch")
        if torch is None:
            return None, None
        try:
            if not torch.cuda.is_available():
                return None, None
            return (
                int(torch.cuda.max_memory_allocated()),
                int(torch.cuda.max_memory_reserved()),
            )
        except Exception:
            return None, None


def creer_callback(config: ConfigCouts, run: Any, **kwargs: Any) -> CallbackCouts:
    """Callback prêt à l'emploi : NVML réel (`pynvml`) sauf injection."""
    if "nvml" not in kwargs:
        kwargs["nvml"] = _importer("pynvml")
    return CallbackCouts(config, run, **kwargs)
