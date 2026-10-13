"""Story 10.3 : mesures de coût d'un Run. `Trainer`, torch et NVML simulés, aucun GPU."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from slmsp.core.config import charger_toml
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import ConfigCouts, ConfigEntrainement, charger_config_entrainement
from slmsp.train.couts import NOM_COUTS, NOM_METRIQUES, CallbackCouts, creer_callback

CONFIG = ConfigCouts(pas_chauffe=10, periode_echantillonnage_ms=200)


class Horloge:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


class RunFactice:
    def __init__(self, dossier: Path) -> None:
        self.dossier = dossier
        self.lignes: list[dict] = []

    def ajouter_jsonl(self, nom: str, obj: dict) -> None:
        assert nom == NOM_METRIQUES
        self.lignes.append(obj)

    def ecrire(self, nom: str, contenu: str) -> Path:
        chemin = self.dossier / nom
        chemin.write_text(contenu, encoding="utf-8")
        return chemin


class NvmlFactice:
    def __init__(self, puissances_mw: list[int], utilisees: list[int]) -> None:
        self.puissances = iter(puissances_mw)
        self.utilisees = iter(utilisees)
        self.arrete = False

    def nvmlInit(self) -> None: ...

    def nvmlShutdown(self) -> None:
        self.arrete = True

    def nvmlDeviceGetHandleByIndex(self, i: int) -> int:
        return i

    def nvmlDeviceGetPowerUsage(self, h: int) -> int:
        return next(self.puissances)

    def nvmlDeviceGetMemoryInfo(self, h: int) -> SimpleNamespace:
        return SimpleNamespace(used=next(self.utilisees))


def torch_factice(allouee: int, reservee: int) -> SimpleNamespace:
    cuda = SimpleNamespace(
        is_available=lambda: True,
        max_memory_allocated=lambda: allouee,
        max_memory_reserved=lambda: reservee,
    )
    return SimpleNamespace(cuda=cuda)


def pas(cb: CallbackCouts, horloge: Horloge, numero: int, tokens: int, dt: float = 1.0) -> None:
    horloge.t += dt
    cb.on_step_end(None, SimpleNamespace(global_step=numero, num_input_tokens_seen=tokens), None)


def test_debit_exclut_chauffe_et_padding(tmp_path: Path) -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        CONFIG, RunFactice(tmp_path), nvml=None, torch=torch_factice(1, 2), horloge=horloge
    )
    cb.on_train_begin(None, SimpleNamespace(), None)
    # 100 tokens non-padding par pas (padding déjà exclu du compteur), 1 s par pas.
    for n in range(1, 31):
        pas(cb, horloge, n, tokens=100 * n)
    cb.on_train_end(None, SimpleNamespace(global_step=30, num_input_tokens_seen=3000), None)
    r = cb.resultat
    assert r["tokens_mesures"] == 2000  # pas 11 à 30
    assert r["tokens_par_s"] == pytest.approx(100.0)
    assert r["duree_s"] == pytest.approx(30.0)
    assert r["tokens_hors_padding"] == 3000


def test_moins_de_pas_que_la_chauffe_pas_de_debit(tmp_path: Path) -> None:
    horloge = Horloge()
    cb = CallbackCouts(CONFIG, RunFactice(tmp_path), nvml=None, torch=None, horloge=horloge)
    cb.on_train_begin(None, SimpleNamespace(), None)
    for n in range(1, 6):
        pas(cb, horloge, n, tokens=50 * n)
    cb.on_train_end(None, SimpleNamespace(global_step=5, num_input_tokens_seen=250), None)
    assert cb.resultat["tokens_par_s"] is None


def test_energie_integrale_et_vram_maximum_des_deux_sources(tmp_path: Path) -> None:
    horloge = Horloge()
    # puissances 100 W, 200 W, 200 W sur 3 relevés espacés de 36 s -> trapèzes
    nvml = NvmlFactice([100_000, 200_000, 200_000], [5_000, 9_000, 7_000])
    cb = CallbackCouts(
        CONFIG,
        RunFactice(tmp_path),
        nvml=nvml,
        torch=torch_factice(allouee=6_000, reservee=8_000),
        horloge=horloge,
        avec_fil=False,
    )
    cb.on_train_begin(None, SimpleNamespace(), None)  # relevé 1
    horloge.t += 36
    cb.echantillonneur.echantillonner()  # relevé 2
    horloge.t += 36
    cb.on_train_end(None, SimpleNamespace(global_step=0), None)  # relevé 3
    r = cb.resultat
    joules = 36 * (100 + 200) / 2 + 36 * 200
    assert r["energie_wh"] == pytest.approx(joules / 3600)
    assert r["vram_nvml_max_octets"] == 9_000
    assert r["vram_reservee_max_octets"] == 8_000
    assert r["vram_allouee_max_octets"] == 6_000
    assert r["vram_max_octets"] == 9_000
    assert nvml.arrete


def test_vram_torch_superieure_a_nvml(tmp_path: Path) -> None:
    nvml = NvmlFactice([1000, 1000], [100, 200])
    cb = CallbackCouts(
        CONFIG, RunFactice(tmp_path), nvml=nvml, torch=torch_factice(1, 5_000), avec_fil=False
    )
    cb.on_train_begin(None, SimpleNamespace(), None)
    cb.on_train_end(None, SimpleNamespace(global_step=0), None)
    assert cb.resultat["vram_max_octets"] == 5_000


def test_nvml_absent_mesures_nulles(tmp_path: Path) -> None:
    cb = CallbackCouts(CONFIG, RunFactice(tmp_path), nvml=None, torch=SimpleNamespace())
    cb.on_train_begin(None, SimpleNamespace(), None)
    cb.on_train_end(None, SimpleNamespace(global_step=0), None)
    assert cb.resultat["energie_wh"] is None
    assert cb.resultat["vram_max_octets"] is None


def test_fil_d_echantillonnage_reel(tmp_path: Path) -> None:
    class NvmlConstant(NvmlFactice):
        def nvmlDeviceGetPowerUsage(self, h: int) -> int:
            return 50_000

        def nvmlDeviceGetMemoryInfo(self, h: int) -> SimpleNamespace:
            return SimpleNamespace(used=1234)

    cb = CallbackCouts(
        ConfigCouts(pas_chauffe=1, periode_echantillonnage_ms=1),
        RunFactice(tmp_path),
        nvml=NvmlConstant([], []),
        torch=SimpleNamespace(),
    )
    cb.on_train_begin(None, SimpleNamespace(), None)
    time.sleep(0.05)
    cb.on_train_end(None, SimpleNamespace(global_step=0), None)
    assert cb.resultat["echantillons_nvml"] >= 2
    assert cb.resultat["vram_nvml_max_octets"] == 1234


def test_ecriture_metriques_et_couts_json(tmp_path: Path) -> None:
    run = RunFactice(tmp_path)
    cb = CallbackCouts(CONFIG, run, nvml=None, torch=torch_factice(1, 2))
    cb.on_train_begin(None, SimpleNamespace(), None)
    cb.on_train_end(None, SimpleNamespace(global_step=0), None)
    assert run.lignes[0]["type"] == "couts"
    ecrit = json.loads((tmp_path / NOM_COUTS).read_text(encoding="utf-8"))
    assert ecrit == cb.resultat
    # événements non traités : no-op comme TrainerCallback
    assert cb.on_save(None, None, None) is None
    with pytest.raises(AttributeError):
        cb.inconnu  # noqa: B018


def test_creer_callback_sans_nvml(tmp_path: Path) -> None:
    cb = creer_callback(CONFIG, RunFactice(tmp_path), nvml=None, torch=None)
    assert cb.echantillonneur.demarrer() is False


def test_config_entrainement_versionnee() -> None:
    cfg = charger_config_entrainement()
    assert cfg.couts.pas_chauffe == 10
    assert cfg.couts.periode_echantillonnage_ms == 200


def test_config_refuse_cle_inconnue(tmp_path: Path) -> None:
    fichier = tmp_path / "e.toml"
    fichier.write_text(
        "[couts]\npas_chauffe = 10\nperiode_echantillonnage_ms = 200\nx = 1\n", encoding="utf-8"
    )
    with pytest.raises(ConfigurationInvalide):
        charger_toml(fichier, ConfigEntrainement)
