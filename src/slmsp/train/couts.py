"""Story 10.3 : mesures de coût d'un Run (FR-33, AD-18).

Un callback unique, indépendant de la méthode, mesure :

- la durée de l'entraînement ;
- le débit en tokens/s **hors padding** après `pas_chauffe` pas (le compte vient de
  `state.num_input_tokens_seen`, que le Trainer tient hors padding quand
  `include_num_input_tokens_seen="non_padding"` : voir `ARGUMENTS_COMPTE_TOKENS`) ;
- la VRAM maximale : maximum entre `torch.cuda.max_memory_allocated`,
  `torch.cuda.max_memory_reserved` et l'échantillonnage NVML (mémoire utilisée du GPU) ;
- l'énergie en Wh : intégrale (trapèzes) de la puissance NVML échantillonnée toutes les
  `periode_nvml_ms` (200 ms par défaut).

Le protocole (pas de chauffe, période) vient de `config/entrainement.toml` (`ConfigCouts`).
Les mesures vont dans `metriques.jsonl` et `couts.json` du run.

`MesureCouts` ne dépend ni de torch ni de transformers : `torch` et `nvml` sont injectés, ou
importés dans les fonctions. `creer_callback` l'enveloppe dans un `TrainerCallback`.
Un NVML absent dégrade la mesure (énergie `null`) sans interrompre le Run.
"""

from __future__ import annotations

import importlib
import json
import threading
import time
from collections.abc import Callable
from typing import Any, Final

from slmsp.core.artefacts import ArtefactExistant, Run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import ConfigCouts

NOM_COUTS: Final = "couts.json"
NOM_METRIQUES: Final = "metriques.jsonl"
SCHEMA_VERSION: Final = 1
MODE_TOKENS_HORS_PADDING: Final = "non_padding"
ARGUMENTS_COMPTE_TOKENS: Final = {"include_num_input_tokens_seen": MODE_TOKENS_HORS_PADDING}
"""À fusionner dans les arguments d'entraînement : le Trainer compte alors hors padding."""


def _json_sur(valeur: Any) -> str:
    return json.dumps(valeur, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)


class EchantillonneurNvml:
    """Échantillonne puissance et mémoire du GPU et intègre l'énergie (règle des trapèzes).

    `echantillonner()` prend un relevé ; `demarrer()` lance un fil qui en prend un toutes
    les `periode_s` secondes (premier relevé immédiat, dernier à l'arrêt). Hors fil, les
    relevés sont déterministes, donc testables avec une horloge simulée.
    """

    def __init__(
        self,
        periode_s: float,
        *,
        nvml: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
        indice_gpu: int = 0,
    ) -> None:
        self.periode_s = periode_s
        self._horloge = horloge
        self._indice_gpu = indice_gpu
        self._nvml = nvml
        self._poignee: Any = None
        self._verrou = threading.Lock()
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None
        self.disponible = False
        self.motif: str | None = None
        self.echantillons = 0
        self.energie_wh = 0.0
        self.puissance_max_w = 0.0
        self.memoire_max_octets = 0
        self._dernier: tuple[float, float] | None = None  # (instant, puissance en W)
        self._somme_w = 0.0

    def ouvrir(self) -> bool:
        """Initialise NVML ; en cas d'échec, `disponible` reste faux et `motif` l'explique."""
        try:
            if self._nvml is None:
                self._nvml = importlib.import_module("pynvml")
            self._nvml.nvmlInit()
            self._poignee = self._nvml.nvmlDeviceGetHandleByIndex(self._indice_gpu)
        except Exception as exc:
            self.motif = f"NVML indisponible ({type(exc).__name__})"
            return False
        self.disponible = True
        return True

    def echantillonner(self) -> None:
        """Prend un relevé (puissance en mW, mémoire utilisée) et met l'énergie à jour."""
        if not self.disponible:
            return
        try:
            instant = self._horloge()
            puissance_w = float(self._nvml.nvmlDeviceGetPowerUsage(self._poignee)) / 1000.0
            memoire = int(self._nvml.nvmlDeviceGetMemoryInfo(self._poignee).used)
        except Exception as exc:
            with self._verrou:
                self.motif = f"relevé NVML en échec ({type(exc).__name__})"
            return
        with self._verrou:
            if self._dernier is not None:
                avant, puissance_avant = self._dernier
                duree = max(0.0, instant - avant)
                self.energie_wh += (puissance_avant + puissance_w) / 2.0 * duree / 3600.0
            self._dernier = (instant, puissance_w)
            self.echantillons += 1
            self._somme_w += puissance_w
            self.puissance_max_w = max(self.puissance_max_w, puissance_w)
            self.memoire_max_octets = max(self.memoire_max_octets, memoire)

    def _boucle(self) -> None:
        while not self._arret.is_set():
            self.echantillonner()
            self._arret.wait(self.periode_s)

    def demarrer(self) -> None:
        if not self.disponible or self._fil is not None:
            return
        self._arret.clear()
        self._fil = threading.Thread(target=self._boucle, name="nvml-couts", daemon=True)
        self._fil.start()

    def arreter(self) -> None:
        """Arrête le fil, prend un dernier relevé et ferme NVML (idempotent)."""
        if self._fil is not None:
            self._arret.set()
            self._fil.join(timeout=max(1.0, 5 * self.periode_s))
            self._fil = None
        if self.disponible:
            self.echantillonner()
            try:
                self._nvml.nvmlShutdown()
            except Exception:
                pass
            self.disponible = False
            self._poignee = None

    def puissance_moyenne_w(self) -> float | None:
        return self._somme_w / self.echantillons if self.echantillons else None


class MesureCouts:
    """Cœur de la mesure : les méthodes `on_*` suivent le protocole des callbacks du Trainer."""

    def __init__(
        self,
        run: Run,
        config: ConfigCouts,
        *,
        torch: Any = None,
        nvml: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
        indice_gpu: int = 0,
    ) -> None:
        self.run = run
        self.config = config
        self._torch = torch
        self._horloge = horloge
        self.nvml = EchantillonneurNvml(
            config.periode_nvml_ms / 1000.0, nvml=nvml, horloge=horloge, indice_gpu=indice_gpu
        )
        self._debut: float | None = None
        self._fin: float | None = None
        self._base: tuple[float, int] | None = None  # (instant, tokens vus) après la chauffe
        self._dernier: tuple[float, int, int] = (0.0, 0, 0)  # (instant, tokens, pas de la session)
        self._pas_depart = 0
        self._cuda = False
        self.resultat: dict[str, Any] | None = None

    # --- Événements -----------------------------------------------------------------------

    def on_train_begin(self, args: Any, state: Any, control: Any = None, **_: Any) -> None:
        mode = getattr(args, "include_num_input_tokens_seen", None)
        if mode != MODE_TOKENS_HORS_PADDING:
            raise ConfigurationInvalide(
                "mesure du coût : `include_num_input_tokens_seen` doit valoir "
                f"{MODE_TOKENS_HORS_PADDING!r} pour exclure le padding (reçu : {mode!r})"
            )
        self._preparer_torch()
        self.nvml.ouvrir()
        self.nvml.echantillonner()
        self.nvml.demarrer()
        self._debut = self._horloge()
        # Sur une reprise, `global_step` part du checkpoint : les pas se comptent depuis ici.
        self._pas_depart = int(state.global_step)
        self._dernier = (self._debut, int(state.num_input_tokens_seen), 0)
        if self.config.pas_chauffe == 0:
            self._base = (self._debut, int(state.num_input_tokens_seen))

    def on_step_end(self, args: Any, state: Any, control: Any = None, **_: Any) -> None:
        if self._debut is None:
            return
        self._synchroniser()
        instant = self._horloge()
        tokens = int(state.num_input_tokens_seen)
        pas = int(state.global_step) - self._pas_depart
        self._dernier = (instant, tokens, pas)
        if self._base is None and pas >= self.config.pas_chauffe:
            self._base = (instant, tokens)

    def on_train_end(self, args: Any, state: Any, control: Any = None, **_: Any) -> None:
        self.terminer()

    # --- Mesure ---------------------------------------------------------------------------

    def _preparer_torch(self) -> None:
        if self._torch is None:
            try:
                self._torch = importlib.import_module("torch")
            except Exception:
                self._torch = None
        try:
            self._cuda = bool(self._torch is not None and self._torch.cuda.is_available())
        except Exception:
            self._cuda = False
        if self._cuda:
            self._torch.cuda.reset_peak_memory_stats()

    def _synchroniser(self) -> None:
        if self._cuda:
            self._torch.cuda.synchronize()

    def _vram(self) -> dict[str, int | None]:
        allouee = reservee = None
        if self._cuda:
            allouee = int(self._torch.cuda.max_memory_allocated())
            reservee = int(self._torch.cuda.max_memory_reserved())
        nvml = self.nvml.memoire_max_octets if self.nvml.echantillons else None
        sources = [v for v in (allouee, reservee, nvml) if v is not None]
        return {
            "allouee_max_octets": allouee,
            "reservee_max_octets": reservee,
            "nvml_max_octets": nvml,
            "max_octets": max(sources) if sources else None,
        }

    def _debit(self) -> dict[str, Any]:
        if self._base is None:
            return {
                "pas_chauffe": self.config.pas_chauffe,
                "pas_mesures": 0,
                "tokens_mesures": 0,
                "duree_mesuree_s": 0.0,
                "tokens_par_s": None,
            }
        instant0, tokens0 = self._base
        instant1, tokens1, pas = self._dernier
        duree = max(0.0, instant1 - instant0)
        tokens = max(0, tokens1 - tokens0)
        pas_mesures = max(0, pas - self.config.pas_chauffe)
        return {
            "pas_chauffe": self.config.pas_chauffe,
            "pas_mesures": pas_mesures,
            "tokens_mesures": tokens,
            "duree_mesuree_s": duree,
            "tokens_par_s": tokens / duree if duree > 0 and tokens > 0 else None,
        }

    def terminer(self) -> dict[str, Any]:
        """Arrête l'échantillonnage et écrit les mesures (idempotent : une seule écriture).

        À appeler aussi en `finally` quand l'entraînement s'interrompt (le Trainer
        n'appelle pas `on_train_end` sur exception).
        """
        if self.resultat is not None:
            return self.resultat
        self._fin = self._horloge()
        self._synchroniser()
        self.nvml.arreter()
        debut = self._debut if self._debut is not None else self._fin
        energie = self.nvml.echantillons > 0
        self.resultat = {
            "schema_version": SCHEMA_VERSION,
            "duree_s": max(0.0, self._fin - debut),
            "pas_total": self._dernier[2],
            "debit": self._debit(),
            "vram": self._vram(),
            "energie": {
                "wh": self.nvml.energie_wh if energie else None,
                "puissance_moyenne_w": self.nvml.puissance_moyenne_w(),
                "puissance_max_w": self.nvml.puissance_max_w if energie else None,
                "echantillons": self.nvml.echantillons,
                "periode_ms": self.config.periode_nvml_ms,
            },
            "nvml": {"disponible": energie, "motif": None if energie else self.nvml.motif},
        }
        self._ecrire()
        return self.resultat

    def _ecrire(self) -> None:
        assert self.resultat is not None
        self.run.ajouter_jsonl(NOM_METRIQUES, {"evenement": "couts", **self.resultat})
        contenu = _json_sur(self.resultat) + "\n"
        try:
            self.run.ecrire(NOM_COUTS, contenu)
        except ArtefactExistant:
            # Reprise sur checkpoint : un artefact n'est jamais réécrit.
            numero = 2
            while True:
                try:
                    self.run.ecrire(f"couts-{numero}.json", contenu)
                    return
                except ArtefactExistant:
                    numero += 1


def creer_callback(mesure: MesureCouts, *, transformers: Any = None) -> Any:
    """Enveloppe `mesure` dans un `transformers.TrainerCallback` (import dans la fonction)."""
    if transformers is None:
        transformers = importlib.import_module("transformers")

    class CallbackCouts(transformers.TrainerCallback):  # type: ignore[misc, name-defined]
        """Callback unique de mesure du coût : délègue à `MesureCouts`."""

        def __init__(self) -> None:
            super().__init__()
            self.mesure = mesure

        def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            self.mesure.on_train_begin(args, state, control, **kwargs)

        def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            self.mesure.on_step_end(args, state, control, **kwargs)

        def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            self.mesure.on_train_end(args, state, control, **kwargs)

    return CallbackCouts()


__all__ = [
    "ARGUMENTS_COMPTE_TOKENS",
    "MODE_TOKENS_HORS_PADDING",
    "NOM_COUTS",
    "NOM_METRIQUES",
    "EchantillonneurNvml",
    "MesureCouts",
    "creer_callback",
]
