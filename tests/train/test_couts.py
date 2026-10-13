"""Story 10.3 : mesures de coût d'un Run (FR-33).

`Trainer`, torch et NVML sont simulés : aucun GPU ni extra `train`. Les valeurs sont des
nombres factices ; aucune donnée d'entraînement n'est rédigée.
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import ConfigCouts, charger_config_entrainement
from slmsp.train.couts import (
    EchantillonneurNvml,
    MesureurCouts,
    creer_callback,
    integrer_energie_wh,
)

CONFIG = ConfigCouts(pas_chauffe=3, periode_echantillonnage_ms=200)
GO = 1024**3


class Horloge:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class NvmlFactice:
    def __init__(self) -> None:
        self.milliwatts = 100_000
        self.utilise = GO
        self.initialise = False
        self.arrete = False

    def nvmlInit(self) -> None:  # noqa: N802
        self.initialise = True

    def nvmlShutdown(self) -> None:  # noqa: N802
        self.arrete = True

    def nvmlDeviceGetHandleByIndex(self, indice: int) -> int:  # noqa: N802
        return indice

    def nvmlDeviceGetPowerUsage(self, poignee: int) -> int:  # noqa: N802
        return self.milliwatts

    def nvmlDeviceGetMemoryInfo(self, poignee: int) -> Any:  # noqa: N802
        return SimpleNamespace(used=self.utilise)


class TorchFactice:
    def __init__(self, allouee: int, reservee: int, cuda: bool = True) -> None:
        self.cuda = SimpleNamespace(
            is_available=lambda: cuda,
            max_memory_allocated=lambda: allouee,
            max_memory_reserved=lambda: reservee,
        )


class RunFactice:
    def __init__(self) -> None:
        self.fichiers: dict[str, str] = {}
        self.jsonl: list[tuple[str, dict[str, Any]]] = []

    def ecrire(self, nom: str, contenu: str) -> None:
        self.fichiers[nom] = contenu

    def ajouter_jsonl(self, nom: str, obj: dict[str, Any]) -> None:
        self.jsonl.append((nom, obj))


def mesureur(run: Any, torch: Any, nvml: Any, horloge: Horloge) -> MesureurCouts:
    return MesureurCouts(
        CONFIG, run, torch=torch, nvml=nvml, horloge=horloge, echantillonner_en_fil=False
    )


def test_debit_exclut_padding_et_chauffe() -> None:
    horloge, run = Horloge(), RunFactice()
    m = mesureur(run, TorchFactice(GO, 2 * GO), NvmlFactice(), horloge)
    m.debut()
    lot = [[1, 1, 1, 0], [1, 1, 0, 0]]  # 5 tokens utiles, 3 de padding
    for pas in range(1, 6):
        m.compter_lot(lot)
        horloge.t = float(pas)
        m.fin_de_pas()
    mesures = m.fin()
    assert mesures["tokens_utiles"] == 25
    assert mesures["pas_mesures"] == 2
    # Chronomètre lancé à la fin du pas 3 (t=3) ; 2 pas de 5 tokens jusqu'à t=5.
    assert mesures["tokens_par_seconde"] == pytest.approx(10 / 2)
    assert mesures["duree_s"] == pytest.approx(5.0)


def test_debit_absent_si_la_chauffe_n_est_pas_terminee() -> None:
    horloge = Horloge()
    m = mesureur(RunFactice(), TorchFactice(GO, GO), NvmlFactice(), horloge)
    m.debut()
    for pas in (1, 2, 3):
        m.compter_lot([[1, 1]])
        horloge.t = float(pas)
        m.fin_de_pas()
    assert m.fin()["tokens_par_seconde"] is None


def test_energie_integrale_de_la_puissance() -> None:
    horloge, nvml = Horloge(), NvmlFactice()
    m = mesureur(RunFactice(), TorchFactice(GO, GO), nvml, horloge)
    m.debut()  # t=0 : 100 W
    horloge.t = 1800.0
    nvml.milliwatts = 300_000
    m.echantillonner()  # t=1800 : 300 W
    horloge.t = 3600.0
    mesures = m.fin()  # t=3600 : 300 W
    # 1800 s à 200 W moyens + 1800 s à 300 W = 100 Wh + 150 Wh.
    assert mesures["energie_wh"] == pytest.approx(250.0)
    assert mesures["releves_puissance"] == 3
    assert integrer_energie_wh([(0.0, 360.0), (10.0, 360.0)]) == pytest.approx(1.0)
    assert integrer_energie_wh([(0.0, 100.0)]) == 0.0


@pytest.mark.parametrize(
    ("reservee", "nvml_octets", "attendu"),
    [(2 * GO, 5 * GO, 5 * GO), (6 * GO, 3 * GO, 6 * GO)],
)
def test_vram_maximum_des_deux_sources(reservee: int, nvml_octets: int, attendu: int) -> None:
    horloge, nvml = Horloge(), NvmlFactice()
    nvml.utilise = nvml_octets
    m = mesureur(RunFactice(), TorchFactice(GO, reservee), nvml, horloge)
    m.debut()
    mesures = m.fin()
    assert mesures["vram_max_octets"] == attendu
    assert mesures["vram_torch_reservee_octets"] == reservee
    assert mesures["vram_torch_allouee_octets"] == GO
    assert mesures["vram_nvml_octets"] == nvml_octets


def test_sans_nvml_ni_cuda_les_mesures_valent_none() -> None:
    class NvmlEnPanne(NvmlFactice):
        def nvmlInit(self) -> None:  # noqa: N802
            raise RuntimeError("pas de pilote")

    m = mesureur(RunFactice(), TorchFactice(0, 0, cuda=False), NvmlEnPanne(), Horloge())
    m.debut()
    mesures = m.fin()
    assert mesures["vram_max_octets"] is None
    assert mesures["energie_wh"] is None
    assert mesures["vram_nvml_octets"] is None


def test_ecriture_dans_metriques_et_couts_json() -> None:
    horloge, run = Horloge(), RunFactice()
    m = mesureur(run, TorchFactice(GO, GO), NvmlFactice(), horloge)
    m.debut()
    horloge.t = 2.0
    mesures = m.fin()
    assert run.jsonl == [("metriques.jsonl", {"type": "couts", **mesures})]
    assert json.loads(run.fichiers["couts.json"]) == mesures


def test_ecriture_dans_un_vrai_run(tmp_path: Path) -> None:
    run = nouveau_run("train", "couts-test", {"methode": "<factice>"}, racine=tmp_path)
    horloge = Horloge()
    m = mesureur(run, TorchFactice(GO, GO), NvmlFactice(), horloge)
    m.debut()
    horloge.t = 1.0
    m.fin()
    dossier = next(tmp_path.rglob("couts.json")).parent
    assert json.loads((dossier / "couts.json").read_text(encoding="utf-8"))["duree_s"] == 1.0
    ligne = json.loads((dossier / "metriques.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert ligne["type"] == "couts"


def test_echantillonneur_en_fil_releve_puis_s_arrete() -> None:
    nvml = NvmlFactice()
    ech = EchantillonneurNvml(0.01, nvml)
    compteur = {"n": 0}
    assez = threading.Event()

    def horloge() -> float:
        compteur["n"] += 1
        if compteur["n"] >= 4:
            assez.set()
        return compteur["n"] * 0.01

    ech.demarrer(horloge)
    assert assez.wait(timeout=5)
    ech.arreter(horloge)
    assert nvml.initialise and nvml.arrete
    assert len(ech.releves_w) >= 4
    assert ech._fil is not None and not ech._fil.is_alive()


def test_callback_branche_les_evenements_du_trainer(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("transformers")
    module.TrainerCallback = type("TrainerCallback", (), {})  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "transformers", module)
    horloge, run = Horloge(), RunFactice()
    m = mesureur(run, TorchFactice(GO, GO), NvmlFactice(), horloge)
    callback = creer_callback(m)
    callback.on_train_begin(None, None, None)
    for pas in range(1, 6):
        m.compter_lot([[1, 1, 0]])
        horloge.t = float(pas)
        callback.on_step_end(None, None, None)
    callback.on_train_end(None, None, None)
    assert m.mesures is not None
    assert m.mesures["tokens_par_seconde"] == pytest.approx(4 / 2)
    assert "couts.json" in run.fichiers


def test_config_du_depot_et_cles_inconnues(tmp_path: Path) -> None:
    config = charger_config_entrainement()
    assert config.couts.pas_chauffe == 10
    assert config.couts.periode_echantillonnage_ms == 200
    faux = tmp_path / "e.toml"
    faux.write_text("schema_version = 1\n[couts]\npas_chauffe = 10\ninconnue = 1\n", "utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_config_entrainement(faux)
