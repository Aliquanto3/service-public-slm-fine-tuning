"""Mesures de coût d'un Run : un callback unique, indépendant de la méthode (story 10.3, FR-33).

`CallbackCouts` mesure :
- la **durée** de l'entraînement ;
- le **débit** en tokens/s hors padding, après `pas_chauffe` pas (défaut 10). Les tokens
  viennent de `state.num_input_tokens_seen` : le Run doit poser
  `include_num_input_tokens_seen="non_padding"` dans ses arguments d'entraînement (story
  10.4), faute de quoi le débit est `None` ;
- la **VRAM maximale** : maximum entre `torch.cuda.max_memory_allocated` / `max_memory_reserved`
  et l'échantillonnage NVML de la mémoire utilisée ;
- l'**énergie** en Wh : intégrale (trapèzes) de la puissance NVML échantillonnée toutes les
  `periode_echantillonnage_ms` (200 ms par défaut), par un fil dédié.

À la fin, une ligne `{"type": "couts", ...}` va dans `metriques.jsonl` et le détail dans
`couts.json` du run. Sans NVML (pas de GPU NVIDIA), énergie et VRAM NVML valent `None`.

torch et pynvml ne sont importés que dans les fonctions. `CallbackCouts` suit le protocole
des callbacks de `transformers` par duck-typing (méthodes `on_*`) ; `callback_trainer`
en donne une version dérivant de `transformers.TrainerCallback` pour `Trainer.add_callback`.
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from typing import Any, Final

from slmsp.core.artefacts import Run
from slmsp.train.config import ConfigCouts

__all__ = ["CallbackCouts", "SondeNvml", "callback_trainer", "energie_wh"]

NOM_METRIQUES: Final = "metriques.jsonl"
NOM_COUTS: Final = "couts.json"


def energie_wh(echantillons: list[tuple[float, float]]) -> float | None:
    """Énergie en Wh : intégrale trapézoïdale de `(instant_s, puissance_w)`.

    `None` s'il y a moins de deux relevés.
    """
    if len(echantillons) < 2:
        return None
    joules = 0.0
    for (t0, p0), (t1, p1) in zip(echantillons, echantillons[1:], strict=False):
        joules += (p0 + p1) / 2 * (t1 - t0)
    return joules / 3600


class SondeNvml:
    """Lecture NVML de la puissance (W) et de la mémoire utilisée (octets) d'un GPU."""

    def __init__(self, indice: int = 0, pynvml: Any = None) -> None:
        if pynvml is None:
            import pynvml  # noqa: PLC0415 - import tardif : aucune dépendance au chargement

        self._nvml = pynvml
        pynvml.nvmlInit()
        self._poignee = pynvml.nvmlDeviceGetHandleByIndex(indice)

    def lire(self) -> tuple[float, int]:
        puissance_mw = self._nvml.nvmlDeviceGetPowerUsage(self._poignee)
        memoire = self._nvml.nvmlDeviceGetMemoryInfo(self._poignee)
        return puissance_mw / 1000, int(memoire.used)

    def fermer(self) -> None:
        self._nvml.nvmlShutdown()


def _ouvrir_nvml(indice: int) -> SondeNvml | None:
    try:
        return SondeNvml(indice)
    except Exception:  # noqa: BLE001 - pas de NVML ni de pilote : mesures NVML omises
        return None


class CallbackCouts:
    """Callback de coût unique (voir le docstring du module)."""

    def __init__(
        self,
        run: Run,
        config: ConfigCouts,
        *,
        nvml: Any = None,
        torch: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
        fil: bool = True,
    ) -> None:
        self._run = run
        self._config = config
        self._nvml = nvml
        self._torch = torch
        self._horloge = horloge
        self._avec_fil = fil
        self._verrou = threading.Lock()
        self._echantillons: list[tuple[float, float]] = []
        self._memoire_nvml_max = 0
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None
        self._debut = 0.0
        self._pas_vus = 0
        self._jalon: tuple[float, int] | None = None
        self._dernier: tuple[float, int] = (0.0, 0)
        self.resultat: dict[str, Any] | None = None

    # -- échantillonnage NVML ---------------------------------------------------------------

    def echantillonner(self) -> None:
        """Relève une fois la puissance et la mémoire NVML (appelé par le fil)."""
        if self._nvml is None:
            return
        puissance, memoire = self._nvml.lire()
        instant = self._horloge()
        with self._verrou:
            self._echantillons.append((instant, puissance))
            self._memoire_nvml_max = max(self._memoire_nvml_max, memoire)

    def _boucle(self) -> None:
        periode = self._config.periode_echantillonnage_ms / 1000
        while not self._arret.is_set():
            try:
                self.echantillonner()
            except Exception:  # noqa: BLE001, S110 - un relevé raté n'arrête pas l'entraînement
                pass
            self._arret.wait(periode)

    # -- protocole des callbacks de transformers --------------------------------------------

    def on_train_begin(self, args: Any = None, state: Any = None, control: Any = None, **kw: Any):
        if self._nvml is None:
            self._nvml = _ouvrir_nvml(self._config.indice_gpu)
        self._debut = self._horloge()
        self._dernier = (self._debut, int(getattr(state, "num_input_tokens_seen", 0) or 0))
        self._pas_vus = 0
        self._jalon = self._dernier if self._config.pas_chauffe == 0 else None
        if self._nvml is not None and self._avec_fil:
            self._arret.clear()
            self._fil = threading.Thread(target=self._boucle, name="couts-nvml", daemon=True)
            self._fil.start()
        return control

    def on_step_end(self, args: Any = None, state: Any = None, control: Any = None, **kw: Any):
        self._pas_vus += 1
        mesure = (self._horloge(), int(getattr(state, "num_input_tokens_seen", 0) or 0))
        self._dernier = mesure
        if self._pas_vus == self._config.pas_chauffe:
            self._jalon = mesure
        return control

    def on_train_end(self, args: Any = None, state: Any = None, control: Any = None, **kw: Any):
        fin = self._horloge()
        if self._fil is not None:
            self._arret.set()
            self._fil.join()
            self._fil = None
        if self._nvml is not None:
            try:
                self.echantillonner()  # relevé final : l'intégrale couvre toute la durée
            finally:
                self._nvml.fermer()
        self.resultat = self._bilan(fin - self._debut)
        self._ecrire(self.resultat)
        return control

    # -- calcul et écriture -----------------------------------------------------------------

    def _vram_torch(self) -> tuple[int | None, int | None]:
        torch = self._torch
        if torch is None:
            try:
                import torch  # noqa: PLC0415
            except ImportError:
                return None, None
        try:
            return (
                int(torch.cuda.max_memory_allocated()),
                int(torch.cuda.max_memory_reserved()),
            )
        except Exception:  # noqa: BLE001 - CUDA indisponible
            return None, None

    def _debit(self) -> float | None:
        if self._jalon is None or self._pas_vus <= self._config.pas_chauffe:
            return None
        duree = self._dernier[0] - self._jalon[0]
        tokens = self._dernier[1] - self._jalon[1]
        if duree <= 0 or tokens <= 0:
            return None
        return tokens / duree

    def _bilan(self, duree_s: float) -> dict[str, Any]:
        allouee, reservee = self._vram_torch()
        with self._verrou:
            echantillons = list(self._echantillons)
            nvml_max = self._memoire_nvml_max or None
        sources = [v for v in (allouee, reservee, nvml_max) if v is not None]
        return {
            "type": "couts",
            "duree_s": duree_s,
            "pas": self._pas_vus,
            "pas_chauffe": self._config.pas_chauffe,
            "tokens_par_s": self._debit(),
            "vram_max_octets": max(sources) if sources else None,
            "vram_torch_allouee_max_octets": allouee,
            "vram_torch_reservee_max_octets": reservee,
            "vram_nvml_max_octets": nvml_max,
            "energie_wh": energie_wh(echantillons),
            "releves_nvml": len(echantillons),
            "periode_echantillonnage_ms": self._config.periode_echantillonnage_ms,
        }

    def _ecrire(self, bilan: dict[str, Any]) -> None:
        self._run.ajouter_jsonl(NOM_METRIQUES, bilan)
        self._run.ecrire(NOM_COUTS, json.dumps(bilan, indent=2, sort_keys=True) + "\n")


def callback_trainer(callback: CallbackCouts) -> Any:
    """Enveloppe `callback` dans une sous-classe de `transformers.TrainerCallback`."""
    from transformers import TrainerCallback  # noqa: PLC0415

    class _Adaptateur(TrainerCallback):
        def on_train_begin(self, args, state, control, **kw):
            return callback.on_train_begin(args, state, control, **kw)

        def on_step_end(self, args, state, control, **kw):
            return callback.on_step_end(args, state, control, **kw)

        def on_train_end(self, args, state, control, **kw):
            return callback.on_train_end(args, state, control, **kw)

    return _Adaptateur()
