"""Mesures de coût d'un Run (story 10.3, FR-33, AD-18).

`CallbackCouts` est le callback unique de `Trainer` qui mesure, pour toute méthode :

- la **durée** de l'entraînement ;
- le **débit** en tokens/s hors padding, après `pas_chauffe` pas (10 par défaut) ;
- la **VRAM maximale** : maximum de `torch.cuda.max_memory_allocated`,
  `torch.cuda.max_memory_reserved` et de la mémoire utilisée relevée par NVML (qui voit
  aussi le contexte CUDA et les autres processus) ;
- l'**énergie** en Wh : intégrale trapézoïdale de la puissance NVML échantillonnée toutes
  les `periode_echantillonnage` secondes (200 ms).

Le protocole (pas de chauffe, période, carte) vient de `config/entrainement.toml`
(`ConfigCouts`). Les tokens hors padding sont ceux de `state.num_input_tokens_seen` : le
Run doit donc poser `include_num_input_tokens_seen="non_padding"` dans ses arguments
(`ARGUMENTS_TRAINER`). Sinon, le callback ne publie aucun débit plutôt qu'un débit faux.

Les mesures s'écrivent dans `metriques.jsonl` (une ligne `couts`) et dans `couts.json` du
run (`ecrire_mesures`). Une reprise sur checkpoint ajoute un segment : `couts-2.json`, etc.

torch, transformers et pynvml ne sont importés que dans les fonctions, ou injectés (tests
sans GPU ni extra `train`).
"""

from __future__ import annotations

import importlib
import json
import math
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from slmsp.core.artefacts import Run
from slmsp.train.config import ConfigCouts

NOM_COUTS: Final = "couts.json"
NOM_METRIQUES: Final = "metriques.jsonl"
EVENEMENT_COUTS: Final = "couts"

ARGUMENTS_TRAINER: Final[Mapping[str, str]] = {"include_num_input_tokens_seen": "non_padding"}
"""Arguments de `TrainingArguments` dont dépend le débit hors padding."""


class MesuresCout(BaseModel):
    """Coût d'un Run (ou d'un segment de reprise), identique pour toutes les méthodes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    duree_s: float
    pas: int
    pas_chauffe: int
    pas_mesures: int
    tokens_mesures: int | None
    duree_mesuree_s: float | None
    debit_tokens_par_s: float | None
    vram_max_allocated_octets: int | None
    vram_max_reserved_octets: int | None
    vram_max_nvml_octets: int | None
    vram_max_octets: int | None
    energie_wh: float | None
    puissance_moyenne_w: float | None
    releves_nvml: int
    periode_echantillonnage: float
    avertissements: list[str]


Releve = tuple[float, float | None, int | None]
"""(instant en secondes, puissance en watts, mémoire utilisée en octets)."""


def integrer_energie_wh(releves: Sequence[tuple[float, float]]) -> float | None:
    """Énergie en Wh : intégrale trapézoïdale de la puissance (W) sur le temps (s).

    `releves` est une suite de (instant, puissance) croissante en temps. Moins de deux
    relevés : `None` (rien à intégrer).
    """
    if len(releves) < 2:
        return None
    joules = sum(
        (t1 - t0) * (p0 + p1) / 2 for (t0, p0), (t1, p1) in zip(releves, releves[1:], strict=False)
    )
    return joules / 3600


class EchantillonneurNvml:
    """Relève puissance et mémoire utilisée de la carte, toutes les `periode` secondes.

    `nvml` est le module `pynvml` (ou un double). `echantillonner` fait un relevé ; le fil
    d'arrière-plan (`demarrer`) le répète. Un relevé en erreur est compté, jamais levé : la
    mesure ne doit pas interrompre l'entraînement.
    """

    def __init__(
        self,
        nvml: Any,
        periode: float,
        indice: int = 0,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self._nvml = nvml
        self._periode = periode
        self._indice = indice
        self._horloge = horloge
        self._poignee: Any = None
        self._fil: threading.Thread | None = None
        self._stop = threading.Event()
        self._verrou = threading.Lock()
        self.releves: list[Releve] = []
        self.erreurs = 0
        self.disponible = False

    def ouvrir(self) -> bool:
        """Initialise NVML ; `False` (et `disponible` faux) s'il échoue."""
        try:
            self._nvml.nvmlInit()
            self._poignee = self._nvml.nvmlDeviceGetHandleByIndex(self._indice)
        except Exception:
            self.disponible = False
            return False
        self.disponible = True
        return True

    def echantillonner(self) -> None:
        """Ajoute un relevé (puissance en W, mémoire utilisée en octets)."""
        if not self.disponible:
            return
        instant = self._horloge()
        try:
            watts: float | None = float(self._nvml.nvmlDeviceGetPowerUsage(self._poignee)) / 1000
        except Exception:
            watts = None
            self.erreurs += 1
        try:
            utilise: int | None = int(self._nvml.nvmlDeviceGetMemoryInfo(self._poignee).used)
        except Exception:
            utilise = None
            self.erreurs += 1
        with self._verrou:
            self.releves.append((instant, watts, utilise))

    def _boucle(self) -> None:
        while not self._stop.wait(self._periode):
            self.echantillonner()

    def demarrer(self) -> None:
        """Premier relevé, puis fil d'échantillonnage (sans effet si NVML est indisponible)."""
        if not self.disponible or self._fil is not None:
            return
        self.echantillonner()
        self._fil = threading.Thread(target=self._boucle, name="slmsp-nvml", daemon=True)
        self._fil.start()

    def arreter(self) -> None:
        """Arrête le fil, prend un dernier relevé et ferme NVML (idempotent)."""
        if self._fil is not None:
            self._stop.set()
            self._fil.join()
            self._fil = None
            self.echantillonner()
        if self.disponible:
            self.disponible = False
            try:
                self._nvml.nvmlShutdown()
            except Exception:
                pass

    def instantane(self) -> list[Releve]:
        with self._verrou:
            return list(self.releves)


def _importer(nom: str) -> Any | None:
    try:
        return importlib.import_module(nom)
    except ImportError:
        return None


def _entier(valeur: Any) -> int | None:
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return None


class CallbackCouts:
    """Callback de coût ; `creer_callback` le câble au `Trainer` (hérite de `TrainerCallback`).

    Les trois événements utilisés sont `on_train_begin`, `on_step_end` et `on_train_end`.
    `pas` compte les pas vus par ce callback (une reprise repart de zéro) et les tokens sont
    relevés en différence de `state.num_input_tokens_seen`.
    """

    def __init__(
        self,
        config: ConfigCouts,
        *,
        torch: Any = None,
        nvml: Any = None,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self._torch = torch
        self._nvml = nvml
        self._horloge = horloge
        self._echantillonneur: EchantillonneurNvml | None = None
        self._avertissements: list[str] = []
        self._debut: float | None = None
        self._fin: float | None = None
        self._tokens_debut = 0
        self._pas = 0
        self._tokens_vus = False
        self._compte_valide = True
        self._ref: tuple[float, int] | None = None
        self._dernier: tuple[float, int] | None = None
        self._vram: tuple[int | None, int | None] = (None, None)

    # --- Événements du Trainer -------------------------------------------------------------

    def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
        self._debut = self._horloge()
        self._fin = None
        self._pas = 0
        self._tokens_debut = _entier(getattr(state, "num_input_tokens_seen", 0)) or 0
        self._ref = (self._debut, self._tokens_debut) if self.config.pas_chauffe == 0 else None
        self._dernier = (self._debut, self._tokens_debut)
        mode = getattr(args, "include_num_input_tokens_seen", "non_padding")
        if mode != "non_padding":
            self._compte_valide = False
            self._avertissements.append(
                "tokens comptés avec padding ou non comptés : "
                "include_num_input_tokens_seen doit valoir 'non_padding' ; débit non publié"
            )
        self._ouvrir_nvml()
        return control

    def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
        if self._debut is None or self._dernier is None:
            return control
        instant = self._horloge()
        tokens = _entier(getattr(state, "num_input_tokens_seen", None))
        if tokens is None:
            tokens = self._dernier[1]
        else:
            self._tokens_vus = True
        self._pas += 1
        self._dernier = (instant, tokens)
        if self._ref is None and self._pas >= self.config.pas_chauffe:
            self._ref = (instant, tokens)
        return control

    def on_train_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> Any:
        self.terminer()
        return control

    # --- Mesures ---------------------------------------------------------------------------

    def _ouvrir_nvml(self) -> None:
        nvml = self._nvml if self._nvml is not None else _importer("pynvml")
        if nvml is None:
            self._avertissements.append("pynvml absent : énergie et VRAM NVML non mesurées")
            return
        echantillonneur = EchantillonneurNvml(
            nvml,
            self.config.periode_echantillonnage,
            self.config.indice_gpu,
            self._horloge,
        )
        if not echantillonneur.ouvrir():
            self._avertissements.append("NVML indisponible : énergie et VRAM NVML non mesurées")
            return
        self._echantillonneur = echantillonneur
        echantillonneur.demarrer()

    def _relever_torch(self) -> tuple[int | None, int | None]:
        torch = self._torch if self._torch is not None else _importer("torch")
        try:
            if torch is None or not torch.cuda.is_available():
                self._avertissements.append("CUDA indisponible : VRAM torch non mesurée")
                return None, None
            return (
                int(torch.cuda.max_memory_allocated()),
                int(torch.cuda.max_memory_reserved()),
            )
        except Exception as exc:
            self._avertissements.append(f"VRAM torch illisible ({type(exc).__name__})")
            return None, None

    def terminer(self) -> None:
        """Fige la fin de la mesure : arrête NVML et relève la VRAM torch (idempotent)."""
        if self._fin is not None or self._debut is None:
            return
        self._fin = self._horloge()
        if self._echantillonneur is not None:
            self._echantillonneur.arreter()
        self._vram = self._relever_torch()

    def mesures(self) -> MesuresCout:
        """Mesures du segment courant ; appelle `terminer` s'il n'a pas eu lieu."""
        if self._debut is None:
            raise RuntimeError("aucune mesure : on_train_begin n'a pas été appelé")
        self.terminer()
        fin = self._fin if self._fin is not None else self._debut
        avertissements = list(self._avertissements)

        tokens_mesures = duree_mesuree = debit = None
        pas_mesures = max(0, self._pas - self.config.pas_chauffe)
        if self._ref is None or (pas_mesures == 0 and self.config.pas_chauffe > 0):
            avertissements.append(
                f"{self._pas} pas vus pour {self.config.pas_chauffe} de chauffe : débit non publié"
            )
        if self._ref is not None and self._compte_valide and self._dernier is not None:
            if not self._tokens_vus:
                avertissements.append("state.num_input_tokens_seen absent : débit non publié")
            else:
                tokens_mesures = self._dernier[1] - self._ref[1]
                duree_mesuree = self._dernier[0] - self._ref[0]
                if pas_mesures > 0 and duree_mesuree > 0:
                    debit = tokens_mesures / duree_mesuree

        releves = self._echantillonneur.instantane() if self._echantillonneur else []
        puissances = [(t, w) for t, w, _ in releves if w is not None]
        energie = integrer_energie_wh(puissances)
        moyenne = sum(w for _, w in puissances) / len(puissances) if puissances else None
        if self._echantillonneur is not None and energie is None:
            avertissements.append("moins de deux relevés de puissance : énergie non mesurée")
        if self._echantillonneur is not None and self._echantillonneur.erreurs:
            avertissements.append(f"{self._echantillonneur.erreurs} relevé(s) NVML en erreur")
        utilises = [u for _, _, u in releves if u is not None]
        vram_nvml = max(utilises) if utilises else None

        alloue, reserve = self._vram
        sources = [v for v in (alloue, reserve, vram_nvml) if v is not None]
        return MesuresCout(
            duree_s=fin - self._debut,
            pas=self._pas,
            pas_chauffe=self.config.pas_chauffe,
            pas_mesures=pas_mesures,
            tokens_mesures=tokens_mesures,
            duree_mesuree_s=duree_mesuree,
            debit_tokens_par_s=debit,
            vram_max_allocated_octets=alloue,
            vram_max_reserved_octets=reserve,
            vram_max_nvml_octets=vram_nvml,
            vram_max_octets=max(sources) if sources else None,
            energie_wh=energie,
            puissance_moyenne_w=moyenne,
            releves_nvml=len(releves),
            periode_echantillonnage=self.config.periode_echantillonnage,
            avertissements=avertissements,
        )


def creer_callback(
    config: ConfigCouts,
    *,
    torch: Any = None,
    nvml: Any = None,
    horloge: Callable[[], float] = time.monotonic,
    base: type | None = None,
) -> CallbackCouts:
    """Instance de `CallbackCouts` qui hérite aussi de `transformers.TrainerCallback`.

    `Trainer` appelle tous les événements de `TrainerCallback` : l'héritage fournit les
    événements non utilisés. `base` remplace `TrainerCallback` (tests sans l'extra `train`).
    """
    if base is None:
        base = importlib.import_module("transformers").TrainerCallback
    classe = type("CallbackCoutsTrainer", (CallbackCouts, base), {})
    return classe(config, torch=torch, nvml=nvml, horloge=horloge)


def _json(mesures: MesuresCout, segment: int) -> str:
    donnees = mesures.model_dump(mode="json")
    donnees["segment"] = segment
    for valeur in donnees.values():
        if isinstance(valeur, float) and not math.isfinite(valeur):
            raise ValueError("mesure de coût non finie")
    return json.dumps(donnees, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)


def ecrire_mesures(run: Run, mesures: MesuresCout) -> Path:
    """Écrit les mesures dans `metriques.jsonl` et `couts.json` du run, pour toute méthode.

    Une reprise sur checkpoint écrit `couts-2.json`, `couts-3.json`… : un fichier existant
    n'est jamais écrasé. Renvoie le chemin du fichier créé.
    """
    segment = 1
    while True:
        nom = NOM_COUTS if segment == 1 else f"couts-{segment}.json"
        if not (run.dossier / nom).exists():
            break
        segment += 1
    chemin = run.ecrire(nom, _json(mesures, segment) + "\n")
    ligne = {"evenement": EVENEMENT_COUTS, "segment": segment, **mesures.model_dump(mode="json")}
    run.ajouter_jsonl(NOM_METRIQUES, ligne)
    return chemin
