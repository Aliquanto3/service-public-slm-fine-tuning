"""Story 10.3 : mesures de coût d'un Run (FR-33).

Aucun GPU ni extra `train` : `Trainer` (état, arguments), torch, NVML et l'horloge sont
simulés. Les tokens sont des comptes entiers ; aucune donnée d'entraînement n'est rédigée.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import couts
from slmsp.train.config import ConfigCouts, charger_config_couts
from slmsp.train.couts import (
    ARGUMENTS_TRAINER,
    CallbackCouts,
    EchantillonneurNvml,
    creer_callback,
    ecrire_mesures,
    integrer_energie_wh,
)

RACINE = Path(__file__).resolve().parents[2]
GO = 1024**3


class Horloge:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class NvmlSimule:
    """Double de `pynvml` : puissance en mW et mémoire utilisée modifiables."""

    def __init__(self, milliwatts: int = 100_000, utilise: int = 2 * GO) -> None:
        self.milliwatts = milliwatts
        self.utilise = utilise
        self.ouvert = False
        self.ferme = False
        self.echec_init = False
        self.echec_puissance = False

    def nvmlInit(self) -> None:  # noqa: N802
        if self.echec_init:
            raise RuntimeError("NVML absent")
        self.ouvert = True

    def nvmlShutdown(self) -> None:  # noqa: N802
        self.ferme = True

    def nvmlDeviceGetHandleByIndex(self, indice: int) -> int:  # noqa: N802
        return indice

    def nvmlDeviceGetPowerUsage(self, _poignee: int) -> int:  # noqa: N802
        if self.echec_puissance:
            raise RuntimeError("puissance illisible")
        return self.milliwatts

    def nvmlDeviceGetMemoryInfo(self, _poignee: int) -> Any:  # noqa: N802
        return SimpleNamespace(used=self.utilise, total=8 * GO)


class TorchSimule:
    def __init__(self, alloue: int = 3 * GO, reserve: int = 4 * GO, cuda: bool = True) -> None:
        self.cuda = SimpleNamespace(
            is_available=lambda: cuda,
            max_memory_allocated=lambda: alloue,
            max_memory_reserved=lambda: reserve,
        )


class TrainerCallbackSimule:
    """Remplace `transformers.TrainerCallback` : tous les événements sont des no-op."""

    def on_epoch_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
        return None

    def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
        return None


def config(pas_chauffe: int = 10, periode: float = 1000.0) -> ConfigCouts:
    return ConfigCouts(pas_chauffe=pas_chauffe, periode_echantillonnage=periode, indice_gpu=0)


ARGS = SimpleNamespace(include_num_input_tokens_seen="non_padding")


def entrainer(
    callback: CallbackCouts,
    horloge: Horloge,
    *,
    pas: int,
    tokens_par_pas: int,
    duree_pas: float = 1.0,
    args: Any = ARGS,
) -> SimpleNamespace:
    """Rejoue `pas` pas du Trainer : un pas dure `duree_pas` s et ajoute `tokens_par_pas`."""
    etat = SimpleNamespace(num_input_tokens_seen=0, global_step=0)
    controle = SimpleNamespace()
    callback.on_train_begin(args, etat, controle)
    for _ in range(pas):
        horloge.t += duree_pas
        etat.num_input_tokens_seen += tokens_par_pas
        etat.global_step += 1
        callback.on_step_end(args, etat, controle)
    callback.on_train_end(args, etat, controle)
    return etat


# --- Débit hors padding et chauffe (critère 1) ----------------------------------------------


def test_debit_exclut_le_padding_et_les_pas_de_chauffe() -> None:
    # 12 pas ; lots de 4 séquences de 8 positions dont 3 de padding chacune (20 hors padding).
    masques = [[1, 1, 1, 1, 1, 0, 0, 0]] * 4
    hors_padding = sum(sum(m) for m in masques)
    avec_padding = sum(len(m) for m in masques)
    assert (hors_padding, avec_padding) == (20, 32)

    horloge = Horloge()
    cb = CallbackCouts(config(), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge)
    entrainer(cb, horloge, pas=12, tokens_par_pas=hors_padding)
    m = cb.mesures()

    assert m.pas == 12
    assert m.pas_mesures == 2
    assert m.tokens_mesures == 2 * hors_padding  # les 10 premiers pas sont exclus
    assert m.duree_mesuree_s == 2.0
    assert m.debit_tokens_par_s == pytest.approx(20.0)  # et non 32 : padding exclu
    assert m.duree_s == 12.0


def test_chauffe_nulle_mesure_tous_les_pas() -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=0), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge
    )
    entrainer(cb, horloge, pas=4, tokens_par_pas=10, duree_pas=2.0)
    m = cb.mesures()
    assert (m.pas_mesures, m.tokens_mesures, m.debit_tokens_par_s) == (4, 40, 5.0)


def test_pas_de_debit_si_moins_de_pas_que_la_chauffe() -> None:
    horloge = Horloge()
    cb = CallbackCouts(config(), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge)
    entrainer(cb, horloge, pas=10, tokens_par_pas=20)
    m = cb.mesures()
    assert m.debit_tokens_par_s is None
    assert m.pas_mesures == 0
    assert any("chauffe" in a for a in m.avertissements)


def test_reprise_sur_checkpoint_mesure_en_difference() -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=1), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge
    )
    etat = SimpleNamespace(num_input_tokens_seen=5000, global_step=300)  # reprise au pas 300
    cb.on_train_begin(ARGS, etat, None)
    for _ in range(3):
        horloge.t += 1.0
        etat.num_input_tokens_seen += 50
        cb.on_step_end(ARGS, etat, None)
    cb.on_train_end(ARGS, etat, None)
    m = cb.mesures()
    assert (m.pas, m.tokens_mesures, m.debit_tokens_par_s) == (3, 100, 50.0)


@pytest.mark.parametrize("mode", ["no", "all", True, False])
def test_comptage_avec_padding_n_est_pas_publie(mode: Any) -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=1), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge
    )
    entrainer(
        cb,
        horloge,
        pas=5,
        tokens_par_pas=32,
        args=SimpleNamespace(include_num_input_tokens_seen=mode),
    )
    m = cb.mesures()
    assert m.debit_tokens_par_s is None
    assert any("non_padding" in a for a in m.avertissements)


def test_etat_sans_compteur_de_tokens() -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=1), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge
    )
    cb.on_train_begin(ARGS, SimpleNamespace(), None)
    for _ in range(3):
        horloge.t += 1.0
        cb.on_step_end(ARGS, SimpleNamespace(), None)
    cb.on_train_end(ARGS, SimpleNamespace(), None)
    m = cb.mesures()
    assert m.debit_tokens_par_s is None
    assert any("num_input_tokens_seen" in a for a in m.avertissements)


def test_arguments_trainer_demandent_le_comptage_hors_padding() -> None:
    assert ARGUMENTS_TRAINER == {"include_num_input_tokens_seen": "non_padding"}


# --- Énergie et VRAM (critère 2) ------------------------------------------------------------


def test_integrale_trapezoidale() -> None:
    assert integrer_energie_wh([]) is None
    assert integrer_energie_wh([(0.0, 100.0)]) is None
    # 100 W pendant 36 s = 3600 J = 1 Wh
    assert integrer_energie_wh([(0.0, 100.0), (36.0, 100.0)]) == pytest.approx(1.0)
    # rampe 0 -> 200 W en 36 s : 100 W de moyenne
    assert integrer_energie_wh([(0.0, 0.0), (36.0, 200.0)]) == pytest.approx(1.0)
    assert integrer_energie_wh([(0.0, 100.0), (18.0, 100.0), (36.0, 200.0)]) == pytest.approx(
        (18 * 100 + 18 * 150) / 3600
    )


def test_energie_est_l_integrale_des_releves_nvml() -> None:
    horloge = Horloge()
    nvml = NvmlSimule(milliwatts=100_000)
    cb = CallbackCouts(config(pas_chauffe=0), torch=TorchSimule(), nvml=nvml, horloge=horloge)
    etat = SimpleNamespace(num_input_tokens_seen=0)
    cb.on_train_begin(ARGS, etat, None)  # relevé à t=0 : 100 W
    horloge.t = 18.0
    nvml.milliwatts = 200_000
    cb._echantillonneur.echantillonner()  # t=18 : 200 W
    horloge.t = 36.0
    cb.on_step_end(ARGS, etat, None)
    cb.on_train_end(ARGS, etat, None)  # dernier relevé à t=36 : 200 W
    m = cb.mesures()

    assert m.releves_nvml == 3
    assert m.energie_wh == pytest.approx((18 * 150 + 18 * 200) / 3600)
    assert m.puissance_moyenne_w == pytest.approx((100 + 200 + 200) / 3)
    assert nvml.ouvert
    assert nvml.ferme


def test_vram_maximale_est_le_maximum_des_deux_sources() -> None:
    horloge = Horloge()
    nvml = NvmlSimule(utilise=7 * GO)  # NVML voit plus que torch (contexte CUDA)
    cb = CallbackCouts(
        config(pas_chauffe=0),
        torch=TorchSimule(alloue=3 * GO, reserve=5 * GO),
        nvml=nvml,
        horloge=horloge,
    )
    entrainer(cb, horloge, pas=2, tokens_par_pas=10)
    m = cb.mesures()
    assert m.vram_max_allocated_octets == 3 * GO
    assert m.vram_max_reserved_octets == 5 * GO
    assert m.vram_max_nvml_octets == 7 * GO
    assert m.vram_max_octets == 7 * GO


def test_vram_maximale_prend_torch_quand_il_depasse_nvml() -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=0),
        torch=TorchSimule(alloue=3 * GO, reserve=6 * GO),
        nvml=NvmlSimule(utilise=2 * GO),
        horloge=horloge,
    )
    entrainer(cb, horloge, pas=2, tokens_par_pas=10)
    assert cb.mesures().vram_max_octets == 6 * GO


def test_nvml_indisponible_ne_bloque_pas_la_mesure() -> None:
    horloge = Horloge()
    nvml = NvmlSimule()
    nvml.echec_init = True
    cb = CallbackCouts(config(pas_chauffe=0), torch=TorchSimule(), nvml=nvml, horloge=horloge)
    entrainer(cb, horloge, pas=3, tokens_par_pas=10)
    m = cb.mesures()
    assert m.energie_wh is None
    assert m.vram_max_nvml_octets is None
    assert m.vram_max_octets == 4 * GO  # torch seul
    assert m.debit_tokens_par_s == 10.0
    assert any("NVML" in a for a in m.avertissements)


def test_cuda_indisponible_garde_l_energie() -> None:
    horloge = Horloge()
    cb = CallbackCouts(
        config(pas_chauffe=0), torch=TorchSimule(cuda=False), nvml=NvmlSimule(), horloge=horloge
    )
    entrainer(cb, horloge, pas=3, tokens_par_pas=10)
    m = cb.mesures()
    assert m.vram_max_allocated_octets is None
    assert m.vram_max_octets == 2 * GO  # NVML seul
    assert m.energie_wh is not None
    assert any("CUDA" in a for a in m.avertissements)


def test_releve_de_puissance_en_erreur_est_compte_sans_lever() -> None:
    horloge = Horloge()
    nvml = NvmlSimule()
    nvml.echec_puissance = True
    cb = CallbackCouts(config(pas_chauffe=0), torch=TorchSimule(), nvml=nvml, horloge=horloge)
    entrainer(cb, horloge, pas=2, tokens_par_pas=10)
    m = cb.mesures()
    assert m.energie_wh is None
    assert m.vram_max_nvml_octets == 2 * GO
    assert any("en erreur" in a for a in m.avertissements)


def test_echantillonneur_a_fil_arriere_plan() -> None:
    nvml = NvmlSimule()
    ech = EchantillonneurNvml(nvml, 0.01, 0)
    assert ech.ouvrir()
    ech.demarrer()
    ech.demarrer()  # idempotent
    import time

    time.sleep(0.1)
    ech.arreter()
    ech.arreter()
    assert len(ech.instantane()) >= 3
    assert nvml.ferme


def test_mesures_avant_le_debut_levent() -> None:
    with pytest.raises(RuntimeError, match="on_train_begin"):
        CallbackCouts(config(), torch=TorchSimule(), nvml=NvmlSimule()).mesures()


# --- Câblage Trainer ------------------------------------------------------------------------


def test_creer_callback_herite_de_trainer_callback() -> None:
    horloge = Horloge()
    cb = creer_callback(
        config(pas_chauffe=0),
        torch=TorchSimule(),
        nvml=NvmlSimule(),
        horloge=horloge,
        base=TrainerCallbackSimule,
    )
    assert isinstance(cb, TrainerCallbackSimule)
    assert isinstance(cb, CallbackCouts)
    assert cb.on_epoch_end(ARGS, None, None) is None  # événement hérité
    entrainer(cb, horloge, pas=2, tokens_par_pas=5)  # nos événements priment sur la base
    assert cb.mesures().debit_tokens_par_s == 5.0


def test_le_module_n_importe_aucune_bibliotheque_lourde() -> None:
    code = (
        "import sys, slmsp.train.couts, slmsp.train.config;"
        "lourds = {'torch', 'transformers', 'trl', 'peft', 'bitsandbytes', 'pynvml'};"
        "assert not lourds & set(sys.modules), lourds & set(sys.modules)"
    )
    resultat = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True,
        text=True,
        cwd=RACINE,
        env={"PYTHONPATH": str(RACINE / "src"), "SYSTEMROOT": "C:\\Windows"},
        check=False,
    )
    assert resultat.returncode == 0, resultat.stderr


# --- Écriture des mesures (critère 3) -------------------------------------------------------


def mesures_types() -> couts.MesuresCout:
    horloge = Horloge()
    cb = CallbackCouts(config(), torch=TorchSimule(), nvml=NvmlSimule(), horloge=horloge)
    entrainer(cb, horloge, pas=12, tokens_par_pas=20)
    return cb.mesures()


@pytest.mark.parametrize("methode", ["qlora", "lora", "dora", "orpo"])
def test_ecriture_dans_metriques_et_couts_json_pour_toute_methode(
    tmp_path: Path, methode: str
) -> None:
    run = nouveau_run("train", "essai", {"methode": methode}, racine=tmp_path)
    mesures = mesures_types()
    chemin = ecrire_mesures(run, mesures)

    assert chemin == run.dossier / "couts.json"
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    assert contenu["segment"] == 1
    assert contenu["debit_tokens_par_s"] == pytest.approx(20.0)
    assert contenu["vram_max_octets"] == 4 * GO
    assert contenu["energie_wh"] is not None

    lignes = run.lire_jsonl("metriques.jsonl")
    assert len(lignes) == 1
    assert lignes[0]["evenement"] == "couts"
    assert lignes[0]["debit_tokens_par_s"] == contenu["debit_tokens_par_s"]
    # mêmes clés quelle que soit la méthode : la mesure ignore la méthode
    assert set(contenu) == {"segment", *mesures.model_dump()}


def test_reprise_ajoute_un_segment_sans_ecraser(tmp_path: Path) -> None:
    run = nouveau_run("train", "essai", {}, racine=tmp_path)
    mesures = mesures_types()
    premier = ecrire_mesures(run, mesures)
    avant = premier.read_bytes()
    second = ecrire_mesures(run, mesures)

    assert second == run.dossier / "couts-2.json"
    assert premier.read_bytes() == avant
    assert json.loads(second.read_text(encoding="utf-8"))["segment"] == 2
    assert [ligne["segment"] for ligne in run.lire_jsonl("metriques.jsonl")] == [1, 2]


def test_mesures_non_finies_refusees(tmp_path: Path) -> None:
    run = nouveau_run("train", "essai", {}, racine=tmp_path)
    mesures = mesures_types().model_copy(update={"duree_s": float("inf")})
    with pytest.raises(ValueError, match="non finie"):
        ecrire_mesures(run, mesures)
    assert not (run.dossier / "couts.json").exists()


# --- Configuration --------------------------------------------------------------------------


def test_config_du_depot() -> None:
    cfg = charger_config_couts()
    assert cfg.pas_chauffe == 10
    assert cfg.periode_echantillonnage == 0.2
    assert cfg.indice_gpu == 0


def ecrire_config(dossier: Path, corps: str) -> Path:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "entrainement.toml").write_text(corps, encoding="utf-8")
    return dossier


@pytest.mark.parametrize(
    "corps",
    [
        "[couts]\npas_chauffe = -1\nperiode_echantillonnage = 0.2\nindice_gpu = 0\n",
        "[couts]\npas_chauffe = 10\nperiode_echantillonnage = 0\nindice_gpu = 0\n",
        "[couts]\npas_chauffe = 10\nperiode_echantillonnage = 0.2\n",
        "[couts]\npas_chauffe = 10\nperiode_echantillonnage = 0.2\nindice_gpu = 0\ninconnue = 1\n",
        "",
    ],
)
def test_config_invalide(tmp_path: Path, corps: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_config_couts(ecrire_config(tmp_path, corps))


def test_config_absente(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_config_couts(tmp_path)
