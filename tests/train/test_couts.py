"""Story 10.3 : mesures de coût d'un Run (FR-33).

Aucun GPU ni extra `train` : `Trainer`, torch, transformers et NVML sont simulés. Les « tokens »
sont des comptes entiers ; aucune donnée d'entraînement n'est rédigée.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import couts
from slmsp.train.config import ConfigCouts, charger_entrainement
from slmsp.train.couts import (
    MODE_TOKENS,
    EchantillonneurNvml,
    EchantillonNvml,
    SuiviCouts,
    arguments_mesure_cout,
    creer_callback,
    energie_wh,
)

GO = 1024**3


class Horloge:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class NvmlSimule:
    """Module NVML simulé : suites de puissances (mW) et de mémoires utilisées."""

    def __init__(self, puissances_mw: list[int], memoires: list[int]) -> None:
        self.puissances = list(puissances_mw)
        self.memoires = list(memoires)
        self.appels = 0
        self.initialise = False
        self.ferme = False

    def nvmlInit(self) -> None:  # noqa: N802
        self.initialise = True

    def nvmlShutdown(self) -> None:  # noqa: N802
        self.ferme = True

    def nvmlDeviceGetHandleByIndex(self, indice: int) -> int:  # noqa: N802
        return indice

    def _indice(self, suite: list[Any]) -> int:
        return min(self.appels, len(suite) - 1)

    def nvmlDeviceGetPowerUsage(self, poignee: int) -> int:  # noqa: N802
        return self.puissances[self._indice(self.puissances)]

    def nvmlDeviceGetMemoryInfo(self, poignee: int) -> Any:  # noqa: N802
        info = SimpleNamespace(used=self.memoires[self._indice(self.memoires)])
        self.appels += 1
        return info


def torch_simule(alloue: int, reserve: int, *, cuda: bool = True) -> Any:
    reinit = SimpleNamespace(n=0)

    def reset() -> None:
        reinit.n += 1

    cuda_ns = SimpleNamespace(
        is_available=lambda: cuda,
        max_memory_allocated=lambda: alloue,
        max_memory_reserved=lambda: reserve,
        reset_peak_memory_stats=reset,
    )
    return SimpleNamespace(cuda=cuda_ns, reinit=reinit)


class TrainerCallbackSimule:
    """Base de callback de `transformers` (sans méthode : le callback les définit toutes)."""


def transformers_simule() -> Any:
    return SimpleNamespace(TrainerCallback=TrainerCallbackSimule)


def run_de_test(tmp_path: Path) -> Any:
    return nouveau_run("train", "essai-couts", {"methode": "<factice>"}, racine=tmp_path)


def lignes(run: Any, nom: str = "metriques.jsonl") -> list[dict[str, Any]]:
    return run.lire_jsonl(nom)


def couts_json(run: Any, nom: str = "couts.json") -> dict[str, Any]:
    return json.loads((run.dossier / nom).read_text(encoding="utf-8"))


# --- Configuration ----------------------------------------------------------------------------


def test_config_protocole_du_depot() -> None:
    config = charger_entrainement(racine_projet() / "config" / "entrainement.toml")
    assert config.couts.pas_chauffe == 10
    assert config.couts.periode_echantillonnage_ms == 200


def test_config_cle_inconnue_refusee(tmp_path: Path) -> None:
    fichier = tmp_path / "entrainement.toml"
    fichier.write_text("schema_version = 1\n[couts]\npas_chauffes = 5\n", encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match="pas_chauffes"):
        charger_entrainement(fichier)


def test_config_bornes(tmp_path: Path) -> None:
    fichier = tmp_path / "entrainement.toml"
    fichier.write_text("schema_version = 1\n[couts]\nperiode_echantillonnage_ms = 0\n")
    with pytest.raises(ConfigurationInvalide):
        charger_entrainement(fichier)


# --- Critère 1 : débit hors padding et hors chauffe ------------------------------------------


def piloter(
    suivi: SuiviCouts,
    horloge: Horloge,
    *,
    pas: int,
    sequences: tuple[int, ...] = (30, 20),
    longueur_padding: int = 64,
    duree_pas: float = 1.0,
    premier_pas_lent: float = 0.0,
) -> tuple[int, int]:
    """Simule `pas` pas de `Trainer` ; rend (tokens hors padding, tokens avec padding)."""
    hors_padding = padding = 0
    suivi.demarrer(MODE_TOKENS)
    for numero in range(1, pas + 1):
        horloge.t += duree_pas + (premier_pas_lent if numero <= 10 else 0.0)
        hors_padding += sum(sequences)
        padding += longueur_padding * len(sequences)
        suivi.pas_termine(numero, hors_padding)
    return hors_padding, padding


def test_debit_exclut_padding_et_chauffe(tmp_path: Path) -> None:
    horloge = Horloge()
    suivi = SuiviCouts(
        run_de_test(tmp_path), ConfigCouts(), torch=False, nvml=False, horloge=horloge
    )
    # Chaque pas : 2 séquences de 30 et 20 tokens, paddées à 64 (128 tokens avec padding) ;
    # les 10 premiers pas durent 5 s de plus (chauffe lente).
    hors_padding, padding = piloter(suivi, horloge, pas=30, premier_pas_lent=5.0)
    mesures = suivi.mesures(complet=None)
    assert hors_padding == 30 * 50 and padding == 30 * 128
    assert mesures["tokens_vus"] == 1500
    assert mesures["tokens_apres_chauffe"] == 20 * 50
    assert mesures["duree_apres_chauffe_s"] == pytest.approx(20.0)
    assert mesures["tokens_par_s"] == pytest.approx(50.0)  # ni 128 (padding) ni 30 (avec chauffe)
    assert mesures["duree_s"] == pytest.approx(30 + 50)


def test_debit_absent_tant_que_la_chauffe_n_est_pas_finie(tmp_path: Path) -> None:
    horloge = Horloge()
    suivi = SuiviCouts(
        run_de_test(tmp_path), ConfigCouts(), torch=False, nvml=False, horloge=horloge
    )
    piloter(suivi, horloge, pas=10)
    assert suivi.mesures(complet=None)["tokens_par_s"] is None
    suivi.pas_termine(11, 550)
    assert suivi.mesures(complet=None)["tokens_apres_chauffe"] == 50


def test_pas_chauffe_lu_de_la_config(tmp_path: Path) -> None:
    horloge = Horloge()
    suivi = SuiviCouts(
        run_de_test(tmp_path),
        ConfigCouts(pas_chauffe=2),
        torch=False,
        nvml=False,
        horloge=horloge,
    )
    piloter(suivi, horloge, pas=6)
    assert suivi.mesures(complet=None)["tokens_apres_chauffe"] == 4 * 50


def test_reprise_chauffe_relative_au_pas_de_depart(tmp_path: Path) -> None:
    horloge = Horloge()
    suivi = SuiviCouts(
        run_de_test(tmp_path), ConfigCouts(pas_chauffe=2), torch=False, nvml=False, horloge=horloge
    )
    suivi.demarrer(MODE_TOKENS, pas_depart=100, tokens_depart=5000)
    for numero in range(101, 106):
        horloge.t += 1.0
        suivi.pas_termine(numero, 5000 + (numero - 100) * 50)
    mesures = suivi.mesures(complet=None)
    assert mesures["pas_depart"] == 100
    assert mesures["tokens_apres_chauffe"] == 3 * 50
    assert mesures["tokens_par_s"] == pytest.approx(50.0)


def test_refus_du_comptage_avec_padding(tmp_path: Path) -> None:
    suivi = SuiviCouts(run_de_test(tmp_path), ConfigCouts(), torch=False, nvml=False)
    for mode in ("all", "no", None, True):
        with pytest.raises(ConfigurationInvalide, match="non_padding"):
            suivi.demarrer(mode)
    assert arguments_mesure_cout() == {"include_num_input_tokens_seen": "non_padding"}


# --- Critère 2 : énergie et VRAM --------------------------------------------------------------


def test_energie_integrale_de_la_puissance() -> None:
    echantillons = [
        EchantillonNvml(0.0, 100.0, 0),
        EchantillonNvml(10.0, 200.0, 0),
        EchantillonNvml(20.0, 200.0, 0),
    ]
    assert energie_wh(echantillons) == pytest.approx((150 * 10 + 200 * 10) / 3600)
    assert energie_wh(echantillons[:1]) is None
    assert energie_wh([]) is None


def test_energie_et_vram_depuis_nvml_simule(tmp_path: Path) -> None:
    horloge = Horloge()
    nvml = NvmlSimule([100_000, 200_000, 200_000, 200_000], [2 * GO, 5 * GO, 4 * GO, 3 * GO])
    suivi = SuiviCouts(
        run_de_test(tmp_path),
        ConfigCouts(pas_chauffe=0, periode_echantillonnage_ms=10**7),
        torch=torch_simule(3 * GO, 4 * GO),
        nvml=nvml,
        horloge=horloge,
    )
    suivi.demarrer(MODE_TOKENS)  # relevé à t = 0 : 100 W
    for _ in range(3):
        horloge.t += 10.0
        suivi.nvml.echantillonner()  # t = 10, 20, 30 : 200 W
    mesures = suivi.terminer()  # relevé final à t = 30 (puissance 200 W)
    assert nvml.initialise and nvml.ferme
    assert mesures is not None
    assert mesures["energie_wh"] == pytest.approx((150 * 10 + 200 * 10 + 200 * 10) / 3600)
    assert mesures["puissance_max_w"] == 200.0
    assert mesures["vram_nvml_max_octets"] == 5 * GO
    assert mesures["vram_torch_allocated_max_octets"] == 3 * GO
    assert mesures["vram_torch_reserved_max_octets"] == 4 * GO
    assert mesures["vram_max_octets"] == 5 * GO  # maximum des sources, ici NVML
    assert mesures["nvml_disponible"] is True


def test_vram_max_est_le_maximum_des_sources(tmp_path: Path) -> None:
    nvml = NvmlSimule([50_000], [2 * GO])
    suivi = SuiviCouts(
        run_de_test(tmp_path),
        ConfigCouts(),
        torch=torch_simule(3 * GO, 6 * GO),
        nvml=nvml,
    )
    suivi.demarrer(MODE_TOKENS)
    assert suivi.mesures(complet=None)["vram_max_octets"] == 6 * GO  # réservée par torch
    suivi.terminer()


def test_demarrage_remet_a_zero_le_pic_torch(tmp_path: Path) -> None:
    torch = torch_simule(GO, GO)
    SuiviCouts(run_de_test(tmp_path), ConfigCouts(), torch=torch, nvml=False).demarrer(MODE_TOKENS)
    assert torch.reinit.n == 1


def test_sans_nvml_ni_cuda_les_mesures_sont_nulles(tmp_path: Path) -> None:
    class NvmlHs:
        def nvmlInit(self) -> None:  # noqa: N802
            raise RuntimeError("pilote absent")

    suivi = SuiviCouts(
        run_de_test(tmp_path),
        ConfigCouts(),
        torch=torch_simule(GO, GO, cuda=False),
        nvml=NvmlHs(),
    )
    suivi.demarrer(MODE_TOKENS)
    mesures = suivi.terminer()
    assert mesures is not None
    assert mesures["energie_wh"] is None and mesures["vram_max_octets"] is None
    assert mesures["nvml_disponible"] is False
    assert "RuntimeError" in mesures["motif_nvml"]


def test_fil_d_echantillonnage_periodique() -> None:
    nvml = NvmlSimule([100_000], [GO])
    echantillonneur = EchantillonneurNvml(0.01, nvml=nvml)
    echantillonneur.demarrer()
    fin = time.monotonic() + 10
    while len(echantillonneur.instantane()) < 4 and time.monotonic() < fin:
        time.sleep(0.01)
    echantillonneur.arreter()
    nombre = len(echantillonneur.instantane())
    assert nombre >= 4 and nvml.ferme
    time.sleep(0.05)
    assert len(echantillonneur.instantane()) == nombre  # le fil est arrêté
    assert not [t for t in threading.enumerate() if t.name == "slmsp-nvml"]


# --- Critère 3 : écriture, indépendante de la méthode -----------------------------------------


def test_fin_de_run_ecrit_metriques_et_couts_json(tmp_path: Path) -> None:
    horloge = Horloge()
    run = run_de_test(tmp_path)
    suivi = SuiviCouts(
        run, ConfigCouts(pas_chauffe=1), torch=torch_simule(GO, 2 * GO), nvml=False, horloge=horloge
    )
    piloter(suivi, horloge, pas=4)
    ligne = suivi.journaliser()
    assert ligne["type"] == "cout" and ligne["complet"] is None
    mesures = suivi.terminer()
    assert mesures is not None and mesures["complet"] is True
    journal = lignes(run)
    assert [ligne["type"] for ligne in journal] == ["cout", "couts"]
    fichier = couts_json(run)
    assert fichier["tokens_par_s"] == pytest.approx(50.0)
    assert fichier["vram_max_octets"] == 2 * GO
    assert {k: v for k, v in journal[-1].items() if k != "type"} == fichier
    assert suivi.terminer() is None  # idempotent
    assert len(lignes(run)) == 2


def test_arret_anormal_marque_le_run_incomplet(tmp_path: Path) -> None:
    run = run_de_test(tmp_path)
    suivi = SuiviCouts(run, ConfigCouts(), torch=False, nvml=False)
    suivi.demarrer(MODE_TOKENS)
    suivi.terminer(complet=False)
    assert couts_json(run)["complet"] is False


def test_reprise_n_ecrase_pas_couts_json(tmp_path: Path) -> None:
    run = run_de_test(tmp_path)
    for _ in range(3):
        suivi = SuiviCouts(run, ConfigCouts(), torch=False, nvml=False)
        suivi.demarrer(MODE_TOKENS)
        suivi.terminer()
    assert sorted(p.name for p in run.dossier.glob("couts*.json")) == [
        "couts-2.json",
        "couts-3.json",
        "couts.json",
    ]
    assert len(lignes(run)) == 3


# --- Callback sur un Trainer simulé ------------------------------------------------------------


def test_callback_sur_trainer_simule(tmp_path: Path) -> None:
    horloge = Horloge()
    run = run_de_test(tmp_path)
    nvml = NvmlSimule([100_000, 100_000, 100_000, 100_000], [GO])
    callback = creer_callback(
        run,
        ConfigCouts(pas_chauffe=2, periode_echantillonnage_ms=100000),
        transformers=transformers_simule(),
        torch=torch_simule(GO, 3 * GO),
        nvml=nvml,
        horloge=horloge,
    )
    assert isinstance(callback, TrainerCallbackSimule)
    args = SimpleNamespace(include_num_input_tokens_seen=MODE_TOKENS)
    etat = SimpleNamespace(global_step=0, num_input_tokens_seen=0)
    callback.on_train_begin(args, etat, None)
    for pas in range(1, 7):  # un « Trainer » : 50 tokens hors padding par pas, 1 s par pas
        horloge.t += 1.0
        etat.global_step = pas
        etat.num_input_tokens_seen = 50 * pas
        callback.on_step_end(args, etat, None)
        if pas % 3 == 0:
            callback.on_log(args, etat, None)
    callback.on_train_end(args, etat, None)
    fichier = couts_json(run)
    assert fichier["pas"] == 6 and fichier["tokens_vus"] == 300
    assert fichier["tokens_apres_chauffe"] == 200
    assert fichier["tokens_par_s"] == pytest.approx(50.0)
    assert fichier["vram_max_octets"] == 3 * GO
    assert fichier["complet"] is True
    assert [ligne["type"] for ligne in lignes(run)] == ["cout", "cout", "couts"]


def test_callback_refuse_un_comptage_avec_padding(tmp_path: Path) -> None:
    callback = creer_callback(
        run_de_test(tmp_path),
        ConfigCouts(),
        transformers=transformers_simule(),
        torch=False,
        nvml=False,
    )
    args = SimpleNamespace(include_num_input_tokens_seen="all")
    with pytest.raises(ConfigurationInvalide, match="non_padding"):
        callback.on_train_begin(args, SimpleNamespace(global_step=0), None)


def test_aucun_import_lourd_au_chargement() -> None:
    code = (
        "import sys\n"
        "import slmsp.train.couts, slmsp.train.config\n"
        "lourds = [m for m in ('torch', 'transformers', 'trl', 'peft', 'pynvml') "
        "if m in sys.modules]\n"
        "assert not lourds, lourds\n"
    )
    resultat = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8"
    )
    assert resultat.returncode == 0, resultat.stderr


def test_module_expose_les_constantes_du_protocole() -> None:
    assert couts.NOM_METRIQUES == "metriques.jsonl" and couts.NOM_COUTS == "couts"
