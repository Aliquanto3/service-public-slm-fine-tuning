"""Story 10.3 : mesures de coût d'un Run. `Trainer`, torch et NVML sont simulés, sans GPU."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import ConfigCouts, charger_config_entrainement
from slmsp.train.couts import CallbackCouts, SondeNvml, energie_wh


class Horloge:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class NvmlFactice:
    """Relevés (puissance W, mémoire octets) rejoués dans l'ordre."""

    def __init__(self, releves: list[tuple[float, int]]) -> None:
        self.releves = list(releves)
        self.ferme = False

    def lire(self) -> tuple[float, int]:
        return self.releves.pop(0)

    def fermer(self) -> None:
        self.ferme = True


def torch_factice(allouee: int, reservee: int) -> SimpleNamespace:
    cuda = SimpleNamespace(
        max_memory_allocated=lambda: allouee, max_memory_reserved=lambda: reservee
    )
    return SimpleNamespace(cuda=cuda)


@pytest.fixture
def run(tmp_path: Path):
    return nouveau_run("train", "essai-couts", {"x": 1}, racine=tmp_path)


def cfg(chauffe: int = 10) -> ConfigCouts:
    return ConfigCouts(pas_chauffe=chauffe, periode_echantillonnage_ms=200, indice_gpu=0)


def jouer(callback: CallbackCouts, horloge: Horloge, tokens_par_pas: list[int], dt: float):
    """Simule un entraînement : un état `Trainer` dont seuls les tokens hors padding comptent."""
    etat = SimpleNamespace(num_input_tokens_seen=0, global_step=0)
    callback.on_train_begin(None, etat, None)
    for tokens in tokens_par_pas:
        horloge.t += dt
        etat.global_step += 1
        etat.num_input_tokens_seen += tokens
        callback.on_step_end(None, etat, None)
    callback.on_train_end(None, etat, None)


def callback(run, config, horloge, nvml=None, torch=None, fil=False) -> CallbackCouts:
    return CallbackCouts(
        run, config, nvml=nvml, torch=torch or torch_factice(1, 2), horloge=horloge, fil=fil
    )


@pytest.fixture(autouse=True)
def sans_nvml_reel(monkeypatch):
    import slmsp.train.couts as module

    monkeypatch.setattr(module, "_ouvrir_nvml", lambda indice: None)


def test_debit_exclut_chauffe_et_padding(run) -> None:
    h = Horloge()
    cb = callback(run, cfg(10), h)
    # 10 pas de chauffe (exclus), puis 5 pas de 200 tokens hors padding, 0,5 s chacun
    jouer(cb, h, [1000] * 10 + [200] * 5, dt=0.5)
    assert cb.resultat["tokens_par_s"] == pytest.approx(400.0)
    assert cb.resultat["duree_s"] == pytest.approx(7.5)
    assert cb.resultat["pas"] == 15


def test_debit_absent_si_pas_assez_de_pas(run) -> None:
    h = Horloge()
    cb = callback(run, cfg(10), h)
    jouer(cb, h, [100] * 10, dt=1.0)
    assert cb.resultat["tokens_par_s"] is None


def test_debit_absent_sans_comptage_de_tokens(run) -> None:
    h = Horloge()
    cb = callback(run, cfg(1), h)
    jouer(cb, h, [0] * 5, dt=1.0)
    assert cb.resultat["tokens_par_s"] is None


def test_energie_integrale_de_la_puissance() -> None:
    # (100+100)/2*18 + (100+200)/2*18 = 4500 J
    assert energie_wh([(0, 100.0), (18, 100.0), (36, 200.0)]) == pytest.approx(4500 / 3600)
    assert energie_wh([(0, 100.0)]) is None


def test_energie_et_vram_max_des_deux_sources(run) -> None:
    h = Horloge()
    # trois relevés aux instants 0, 1 et 2 s, puis le relevé final à 3 s
    nvml = NvmlFactice([(100.0, 5_000), (100.0, 9_000), (200.0, 7_000), (200.0, 6_000)])
    cb = callback(run, cfg(0), h, nvml=nvml, torch=torch_factice(4_000, 8_000))
    etat = SimpleNamespace(num_input_tokens_seen=0, global_step=0)
    cb.on_train_begin(None, etat, None)
    for _ in range(3):
        cb.echantillonner()
        h.t += 1.0
    cb.on_train_end(None, etat, None)
    r = cb.resultat
    # relevés (0,100) (1,100) (2,200) (3,200) : 100 + 150 + 200 = 450 J
    assert r["energie_wh"] == pytest.approx(450 / 3600)
    assert r["vram_nvml_max_octets"] == 9_000
    assert r["vram_max_octets"] == 9_000  # NVML l'emporte sur torch (8 000)
    assert r["vram_torch_reservee_max_octets"] == 8_000
    assert nvml.ferme


def test_vram_torch_l_emporte(run) -> None:
    h = Horloge()
    nvml = NvmlFactice([(50.0, 1_000)] * 2)
    cb = callback(run, cfg(0), h, nvml=nvml, torch=torch_factice(4_000, 8_000))
    jouer(cb, h, [10], dt=1.0)
    assert cb.resultat["vram_max_octets"] == 8_000


def test_fil_d_echantillonnage_reel(run) -> None:
    class Constante:
        def lire(self):
            return 10.0, 123

        def fermer(self):
            pass

    config = ConfigCouts(pas_chauffe=0, periode_echantillonnage_ms=5, indice_gpu=0)
    cb = CallbackCouts(run, config, nvml=Constante(), torch=torch_factice(1, 2))
    etat = SimpleNamespace(num_input_tokens_seen=0, global_step=0)
    cb.on_train_begin(None, etat, None)
    time.sleep(0.1)
    cb.on_train_end(None, etat, None)
    assert cb.resultat["releves_nvml"] >= 2
    assert cb.resultat["energie_wh"] > 0


def test_ecriture_metriques_et_couts_json(run) -> None:
    h = Horloge()
    cb = callback(run, cfg(1), h, torch=torch_factice(7, 9))
    jouer(cb, h, [10, 10, 10], dt=1.0)
    lignes = run.lire_jsonl("metriques.jsonl")
    assert len(lignes) == 1 and lignes[0]["type"] == "couts"
    couts = json.loads((run.dossier / "couts.json").read_text(encoding="utf-8"))
    assert couts == cb.resultat
    assert couts["tokens_par_s"] == pytest.approx(10.0)
    assert couts["vram_max_octets"] == 9


def test_sans_nvml_ni_cuda_valeurs_nulles(run) -> None:
    h = Horloge()
    cb = callback(run, cfg(0), h, torch=SimpleNamespace(cuda=SimpleNamespace()))
    jouer(cb, h, [5], dt=1.0)
    assert cb.resultat["energie_wh"] is None
    assert cb.resultat["vram_max_octets"] is None


def test_sonde_nvml_convertit_les_unites() -> None:
    nvml = SimpleNamespace(
        nvmlInit=lambda: None,
        nvmlDeviceGetHandleByIndex=lambda i: i,
        nvmlDeviceGetPowerUsage=lambda p: 55_000,
        nvmlDeviceGetMemoryInfo=lambda p: SimpleNamespace(used=42),
        nvmlShutdown=lambda: None,
    )
    sonde = SondeNvml(0, pynvml=nvml)
    assert sonde.lire() == (55.0, 42)
    sonde.fermer()


def test_config_entrainement_du_depot() -> None:
    config = charger_config_entrainement()
    assert config.couts.pas_chauffe == 10
    assert config.couts.periode_echantillonnage_ms == 200


def test_config_refuse_cle_inconnue(tmp_path: Path) -> None:
    fichier = tmp_path / "e.toml"
    fichier.write_text(
        "schema_version = 1\n[couts]\npas_chauffe = 1\nperiode_echantillonnage_ms = 1\n"
        "indice_gpu = 0\ninconnue = 1\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationInvalide):
        charger_config_entrainement(fichier)
