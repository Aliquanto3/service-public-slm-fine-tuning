"""Mesures de coût d'un Run d'entraînement (story 10.3, FR-33, AD-18).

Un callback unique, indépendant de la méthode (M1 à M4 et variantes), mesure :

- la **durée** du Run (de `on_train_begin` à `on_train_end`) ;
- le **débit** en tokens/s **hors padding**, après `pas_chauffe` pas (10 par défaut) : les
  tokens sont ceux de `state.num_input_tokens_seen`, que le `Trainer` ne compte hors padding
  que si `include_num_input_tokens_seen="non_padding"` (`arguments_mesure_cout`) ; le
  callback refuse de démarrer sans ce réglage ;
- la **VRAM maximale** : maximum de `torch.cuda.max_memory_allocated`,
  `torch.cuda.max_memory_reserved` et du pic de mémoire utilisée relevé par NVML (NVML voit
  toute la carte, bureau et autres processus compris) ;
- l'**énergie** en Wh : intégrale (trapèzes) de la puissance NVML échantillonnée toutes les
  `periode_echantillonnage_ms` (200 ms), par un fil d'arrière-plan.

Les mesures vont dans `metriques.jsonl` (lignes `type = "cout"` aux journalisations, ligne
`type = "couts"` finale) et dans `couts.json` du run. Sans NVML, énergie et VRAM NVML valent
`null` et `nvml_disponible` est faux : le Run n'échoue pas pour autant.

torch, transformers et pynvml ne sont importés que dans les fonctions : les tests
tournent sans l'extra `train`, avec un `Trainer` et un NVML simulés.
"""

from __future__ import annotations

import importlib
import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final, Protocol

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.config import appliquer_environnement_impose
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import ConfigCouts

SCHEMA_COUTS: Final = 1
NOM_COUTS: Final = "couts"
"""Radical de `couts.json` ; une reprise écrit `couts-2.json`, `couts-3.json`, etc."""
NOM_METRIQUES: Final = "metriques.jsonl"
MODE_TOKENS: Final = "non_padding"
"""Valeur de `include_num_input_tokens_seen` qui exclut le padding du compte de tokens."""


class SortieRun(Protocol):
    """Partie de `core.artefacts.Run` utilisée ici."""

    def ecrire(self, nom: str, contenu: str) -> Any: ...

    def ajouter_jsonl(self, nom: str, obj: Any) -> None: ...


def arguments_mesure_cout() -> dict[str, Any]:
    """Arguments d'entraînement que la mesure du coût exige (à fusionner dans la config)."""
    return {"include_num_input_tokens_seen": MODE_TOKENS}


# --- NVML ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class EchantillonNvml:
    instant: float
    """Secondes, horloge monotone."""
    puissance_w: float
    memoire_utilisee: int


def energie_wh(echantillons: list[EchantillonNvml]) -> float | None:
    """Intégrale de la puissance par trapèzes, en Wh (`None` sous deux échantillons)."""
    if len(echantillons) < 2:
        return None
    joules = 0.0
    for a, b in zip(echantillons, echantillons[1:], strict=False):
        joules += (a.puissance_w + b.puissance_w) / 2 * (b.instant - a.instant)
    return joules / 3600.0


class EchantillonneurNvml:
    """Relève la puissance (W) et la mémoire utilisée du GPU, par un fil d'arrière-plan."""

    def __init__(
        self,
        periode_s: float,
        *,
        nvml: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
        indice_gpu: int = 0,
    ) -> None:
        self.periode_s = periode_s
        self._nvml = nvml
        self._horloge = horloge
        self._indice = indice_gpu
        self._poignee: Any = None
        self._arret = threading.Event()
        self._fil: threading.Thread | None = None
        self._verrou = threading.Lock()
        self.echantillons: list[EchantillonNvml] = []
        self.disponible = False
        self.motif: str | None = None

    def demarrer(self) -> None:
        """Initialise NVML, prend un premier relevé et lance le fil (sans NVML : inactif)."""
        try:
            if self._nvml is None:
                self._nvml = importlib.import_module("pynvml")
            self._nvml.nvmlInit()
            self._poignee = self._nvml.nvmlDeviceGetHandleByIndex(self._indice)
            self.disponible = True
        except Exception as exc:
            self.disponible = False
            self.motif = f"NVML indisponible ({type(exc).__name__})"
            return
        self.echantillonner()
        self._arret.clear()
        self._fil = threading.Thread(target=self._boucle, name="slmsp-nvml", daemon=True)
        self._fil.start()

    def echantillonner(self) -> EchantillonNvml | None:
        """Un relevé ; une erreur NVML ponctuelle est ignorée."""
        if not self.disponible:
            return None
        try:
            puissance = float(self._nvml.nvmlDeviceGetPowerUsage(self._poignee)) / 1000.0
            memoire = int(self._nvml.nvmlDeviceGetMemoryInfo(self._poignee).used)
        except Exception:
            return None
        echantillon = EchantillonNvml(self._horloge(), puissance, memoire)
        with self._verrou:
            self.echantillons.append(echantillon)
        return echantillon

    def _boucle(self) -> None:
        while not self._arret.wait(self.periode_s):
            self.echantillonner()

    def arreter(self) -> None:
        """Arrête le fil, prend un dernier relevé et ferme NVML (idempotent)."""
        if not self.disponible:
            return
        self._arret.set()
        if self._fil is not None:
            self._fil.join(timeout=max(5.0, 5 * self.periode_s))
            self._fil = None
        self.echantillonner()
        self.disponible = False
        try:
            self._nvml.nvmlShutdown()
        except Exception:
            pass

    def instantane(self) -> list[EchantillonNvml]:
        with self._verrou:
            return list(self.echantillons)


# --- Suivi --------------------------------------------------------------------------------


class SuiviCouts:
    """Mesures de coût d'un Run : logique pure, pilotée par le callback de `creer_callback`."""

    def __init__(
        self,
        run: SortieRun,
        config: ConfigCouts,
        *,
        torch: Any = None,
        nvml: Any = None,
        horloge: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.run = run
        self.config = config
        self._torch = torch
        self._horloge = horloge
        self.nvml = EchantillonneurNvml(
            config.periode_echantillonnage_ms / 1000.0, nvml=nvml, horloge=horloge
        )
        self.debut: float | None = None
        self.fin: float | None = None
        self.pas = 0
        self.pas_depart = 0
        self.tokens_vus = 0
        self._chauffe: tuple[float, int] | None = None
        """Instant et tokens vus à la fin du dernier pas de chauffe."""
        self._termine = False

    # -- cycle de vie --

    def demarrer(self, mode_tokens: Any, pas_depart: int = 0, tokens_depart: int = 0) -> None:
        """Début du Run ; sur une reprise, pas et tokens de départ viennent du checkpoint."""
        if mode_tokens != MODE_TOKENS:
            raise ConfigurationInvalide(
                "mesure du coût : le débit hors padding exige "
                f"include_num_input_tokens_seen={MODE_TOKENS!r} (reçu {mode_tokens!r})"
            )
        if self._torch is None:
            try:
                appliquer_environnement_impose()
                self._torch = importlib.import_module("torch")
            except Exception:
                self._torch = False
        if self._torch_actif():
            try:
                self._torch.cuda.reset_peak_memory_stats()
            except Exception:
                pass
        self.nvml.demarrer()
        self.debut = self._horloge()
        self.pas_depart = self.pas = pas_depart
        self.tokens_vus = tokens_depart
        if self.config.pas_chauffe == 0:
            self._chauffe = (self.debut, tokens_depart)

    def pas_termine(self, pas: int, tokens_vus: int) -> None:
        """Fin d'un pas : `pas` pas faits, `tokens_vus` tokens hors padding cumulés."""
        self.pas = pas
        self.tokens_vus = tokens_vus
        if self._chauffe is None and pas - self.pas_depart >= self.config.pas_chauffe:
            self._chauffe = (self._horloge(), tokens_vus)

    def journaliser(self) -> dict[str, Any]:
        """Ajoute une ligne `type = "cout"` à `metriques.jsonl` et la rend."""
        ligne = {"type": "cout", **self.mesures(complet=None)}
        self.run.ajouter_jsonl(NOM_METRIQUES, ligne)
        return ligne

    def terminer(self, *, complet: bool = True) -> dict[str, Any] | None:
        """Arrête l'échantillonnage, écrit la ligne finale et `couts.json` (idempotent)."""
        if self._termine:
            return None
        self._termine = True
        self.nvml.arreter()
        self.fin = self._horloge()
        mesures = self.mesures(complet=complet)
        self.run.ajouter_jsonl(NOM_METRIQUES, {"type": "couts", **mesures})
        contenu = json.dumps(mesures, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        segment = 1
        while True:
            nom = f"{NOM_COUTS}.json" if segment == 1 else f"{NOM_COUTS}-{segment}.json"
            try:
                self.run.ecrire(nom, contenu)
                break
            except ArtefactExistant:
                segment += 1  # reprise : un couts.json par segment, jamais réécrit
        return mesures

    # -- mesures --

    def _torch_actif(self) -> bool:
        try:
            return bool(self._torch) and bool(self._torch.cuda.is_available())
        except Exception:
            return False

    def _vram_torch(self) -> tuple[int | None, int | None]:
        if not self._torch_actif():
            return None, None
        return (
            int(self._torch.cuda.max_memory_allocated()),
            int(self._torch.cuda.max_memory_reserved()),
        )

    def mesures(self, *, complet: bool | None) -> dict[str, Any]:
        """Mesures courantes ; `complet` vaut `None` pour une mesure intermédiaire."""
        maintenant = self.fin if self.fin is not None else self._horloge()
        duree = None if self.debut is None else maintenant - self.debut
        tokens_s = duree_chauffe = tokens_chauffe = None
        if self._chauffe is not None and self.pas - self.pas_depart > self.config.pas_chauffe:
            instant, deja = self._chauffe
            duree_chauffe = maintenant - instant
            tokens_chauffe = self.tokens_vus - deja
            if duree_chauffe > 0:
                tokens_s = tokens_chauffe / duree_chauffe
        alloue, reserve = self._vram_torch()
        echantillons = self.nvml.instantane()
        nvml_max = max((e.memoire_utilisee for e in echantillons), default=None)
        sources = [v for v in (alloue, reserve, nvml_max) if v is not None]
        energie = energie_wh(echantillons)
        fenetre = echantillons[-1].instant - echantillons[0].instant if echantillons else 0.0
        return {
            "schema_version": SCHEMA_COUTS,
            "complet": complet,
            "pas": self.pas,
            "pas_depart": self.pas_depart,
            "pas_chauffe": self.config.pas_chauffe,
            "periode_echantillonnage_ms": self.config.periode_echantillonnage_ms,
            "duree_s": duree,
            "tokens_vus": self.tokens_vus,
            "tokens_apres_chauffe": tokens_chauffe,
            "duree_apres_chauffe_s": duree_chauffe,
            "tokens_par_s": tokens_s,
            "vram_torch_allocated_max_octets": alloue,
            "vram_torch_reserved_max_octets": reserve,
            "vram_nvml_max_octets": nvml_max,
            "vram_max_octets": max(sources) if sources else None,
            "energie_wh": energie,
            "puissance_moyenne_w": (
                energie * 3600.0 / fenetre if energie is not None and fenetre > 0 else None
            ),
            "puissance_max_w": max((e.puissance_w for e in echantillons), default=None),
            "echantillons_nvml": len(echantillons),
            "nvml_disponible": bool(echantillons),
            "motif_nvml": self.nvml.motif,
        }


# --- Callback -----------------------------------------------------------------------------


def creer_callback(
    run: SortieRun,
    config: ConfigCouts,
    *,
    transformers: Any = None,
    torch: Any = None,
    nvml: Any = None,
    horloge: Callable[[], float] = time.perf_counter,
) -> Any:
    """Construit le `TrainerCallback` unique de mesure du coût, à passer au `Trainer`.

    La classe dérive de `transformers.TrainerCallback`, importé ici (jamais au niveau du
    module). Le callback expose `suivi` (`SuiviCouts`) : si l'entraînement échoue,
    l'appelant appelle `suivi.terminer(complet=False)`.
    """
    if transformers is None:
        appliquer_environnement_impose()
        transformers = importlib.import_module("transformers")
    suivi = SuiviCouts(run, config, torch=torch, nvml=nvml, horloge=horloge)

    class CallbackCouts(transformers.TrainerCallback):
        def __init__(self) -> None:
            self.suivi = suivi

        def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            suivi.demarrer(
                getattr(args, "include_num_input_tokens_seen", None),
                int(getattr(state, "global_step", 0) or 0),
                int(getattr(state, "num_input_tokens_seen", 0) or 0),
            )

        def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            suivi.pas_termine(
                int(state.global_step), int(getattr(state, "num_input_tokens_seen", 0) or 0)
            )

        def on_log(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            suivi.journaliser()

        def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            suivi.terminer(complet=True)

    return CallbackCouts()
