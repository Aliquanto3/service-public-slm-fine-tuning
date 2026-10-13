"""Story 10.3 : mesures de coût d'un Run (FR-33).

Aucun GPU, aucun torch, aucun transformers : `Trainer` (état et arguments), torch et NVML sont
simulés. Les « tokens » ne sont que des compteurs entiers ; aucune donnée d'entraînement.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import couts
from slmsp.train.config import (
    ConfigCouts,
    charger_config_entrainement,
    chemin_config_entrainement,
)
from slmsp.train.couts import (
    ARGUMENTS_COMPTE_TOKENS,
    EchantillonneurNvml,
    MesureCouts,
    creer_callback,
)

GO = 1024**3
ARGS = SimpleNamespace(**ARGUMENTS_COMPTE_TOKENS)


class Horloge:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


class NvmlSimule:
    """Puissance (mW) et mémoire utilisée relues dans l'ordre ; la dernière valeur se répète."""

    def __init__(
        self, puissances_mw: list[int], memoires: list[int], *, echec_init: bool = False
    ) -> None:
        self.puissances = list(puissances_mw)
        self.memoires = list(memoires)
        self.echec_init = echec_init
        self.ferme = False

    def nvmlInit(self) -> None:
        if self.echec_init:
            raise OSError("pas de NVML")

    def nvmlShutdown(self) -> None:
        self.ferme = True

    def nvmlDeviceGetHandleByIndex(self, indice: int) -> int:
        return indice

    def nvmlDeviceGetPowerUsage(self, _poignee: int) -> int:
        return self.puissances.pop(0) if len(self.puissances) > 1 else self.puissances[0]

    def nvmlDeviceGetMemoryInfo(self, _poignee: int) -> Any:
        memoire = self.memoires.pop(0) if len(self.memoires) > 1 else self.memoires[0]
        return SimpleNamespace(used=memoire)


class TorchSimule:
    def __init__(self, alloue: int, reserve: int, *, cuda: bool = True) -> None:
        self.appels: list[str] = []
        self.cuda = SimpleNamespace(
            is_available=lambda: cuda,
            reset_peak_memory_stats=lambda: self.appels.append("reset"),
            synchronize=lambda: self.appels.append("sync"),
            max_memory_allocated=lambda: alloue,
            max_memory_reserved=lambda: reserve,
        )


def etat(tokens: int = 0, pas: int = 0) -> SimpleNamespace:
    return SimpleNamespace(num_input_tokens_seen=tokens, global_step=pas)


def jouer(
    mesure: MesureCouts,
    horloge: Horloge,
    *,
    pas: int,
    tokens_par_pas: int = 100,
    duree_pas: float = 1.0,
    depart: int = 0,
    jetons_depart: int = 0,
) -> None:
    """Déroule `pas` pas : chacun voit `tokens_par_pas` tokens hors padding en `duree_pas` s."""
    mesure.on_train_begin(ARGS, etat(jetons_depart, depart))
    for i in range(1, pas + 1):
        horloge.t += duree_pas
        mesure.on_step_end(ARGS, etat(jetons_depart + i * tokens_par_pas, depart + i))
    mesure.on_train_end(ARGS, etat(jetons_depart + pas * tokens_par_pas, depart + pas))


def fabrique(
    tmp_path: Path,
    *,
    chauffe: int = 10,
    nvml: Any = None,
    torch: Any = None,
) -> tuple[MesureCouts, Horloge, Any]:
    horloge = Horloge()
    run = nouveau_run("train", "essai-couts", {"methode": "simulee"}, racine=tmp_path)
    mesure = MesureCouts(
        run,
        ConfigCouts(pas_chauffe=chauffe, periode_nvml_ms=200),
        torch=torch if torch is not None else TorchSimule(0, 0, cuda=False),
        nvml=nvml if nvml is not None else NvmlSimule([0], [0], echec_init=True),
        horloge=horloge,
    )
    return mesure, horloge, run


# --- Configuration ------------------------------------------------------------------------


def test_config_entrainement_du_depot() -> None:
    config = charger_config_entrainement(chemin_config_entrainement())
    assert config.couts == ConfigCouts(pas_chauffe=10, periode_nvml_ms=200)


@pytest.mark.parametrize(
    "contenu",
    [
        "schema_version = 1\n[couts]\npas_chauffe = 10\nperiode_nvml_ms = 0\n",
        "schema_version = 1\n[couts]\npas_chauffe = -1\nperiode_nvml_ms = 200\n",
        "schema_version = 1\n[couts]\npas_chauffe = 10\nperiode_nvml_ms = 200\ninconnue = 1\n",
    ],
)
def test_config_entrainement_invalide(tmp_path: Path, contenu: str) -> None:
    fichier = tmp_path / "entrainement.toml"
    fichier.write_text(contenu, encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_config_entrainement(fichier)


# --- Critère 1 : débit hors padding après chauffe -----------------------------------------


def test_debit_exclut_la_chauffe_et_le_padding(tmp_path: Path) -> None:
    """14 pas de 100 tokens utiles (le padding, absent du compteur, ne compte pas) en 1 s."""
    mesure, horloge, _ = fabrique(tmp_path)
    jouer(mesure, horloge, pas=14)
    debit = mesure.resultat["debit"]
    assert debit["pas_mesures"] == 4  # 14 pas moins les 10 de chauffe
    assert debit["tokens_mesures"] == 400  # les 1000 tokens des 10 premiers pas sont exclus
    assert debit["duree_mesuree_s"] == pytest.approx(4.0)
    assert debit["tokens_par_s"] == pytest.approx(100.0)
    assert mesure.resultat["duree_s"] == pytest.approx(14.0)


def test_chauffe_plus_lente_ne_fausse_pas_le_debit(tmp_path: Path) -> None:
    """Les pas de chauffe (3 s chacun) n'entrent pas dans le débit mesuré ensuite."""
    mesure, horloge, _ = fabrique(tmp_path, chauffe=2)
    mesure.on_train_begin(ARGS, etat())
    for pas, duree in enumerate([3.0, 3.0, 1.0, 1.0], start=1):
        horloge.t += duree
        mesure.on_step_end(ARGS, etat(pas * 50, pas))
    mesure.on_train_end(ARGS, etat(200, 4))
    assert mesure.resultat["debit"]["tokens_par_s"] == pytest.approx(50.0)


def test_pas_de_chauffe_nul(tmp_path: Path) -> None:
    mesure, horloge, _ = fabrique(tmp_path, chauffe=0)
    jouer(mesure, horloge, pas=4)
    debit = mesure.resultat["debit"]
    assert (debit["pas_mesures"], debit["tokens_mesures"]) == (4, 400)


@pytest.mark.parametrize("pas", [3, 10])
def test_rien_a_mesurer_avant_la_fin_de_la_chauffe(tmp_path: Path, pas: int) -> None:
    mesure, horloge, _ = fabrique(tmp_path)
    jouer(mesure, horloge, pas=pas)
    debit = mesure.resultat["debit"]
    assert debit["tokens_par_s"] is None
    assert debit["pas_mesures"] == 0


def test_reprise_compte_les_pas_depuis_le_checkpoint(tmp_path: Path) -> None:
    mesure, horloge, _ = fabrique(tmp_path)
    jouer(mesure, horloge, pas=12, depart=200, jetons_depart=20_000)
    debit = mesure.resultat["debit"]
    assert (debit["pas_mesures"], debit["tokens_mesures"]) == (2, 200)


@pytest.mark.parametrize("mode", [None, False, "no", "all", True])
def test_refuse_un_compte_de_tokens_avec_padding(tmp_path: Path, mode: Any) -> None:
    mesure, _, _ = fabrique(tmp_path)
    args = SimpleNamespace(include_num_input_tokens_seen=mode)
    with pytest.raises(ConfigurationInvalide, match="non_padding"):
        mesure.on_train_begin(args, etat())


# --- Critère 2 : énergie et VRAM ----------------------------------------------------------


def test_energie_integrale_de_la_puissance() -> None:
    """Puissance 100 W, 200 W puis 200 W, relevée toutes les 10 s : règle des trapèzes."""
    nvml = NvmlSimule([100_000, 200_000, 200_000], [2 * GO])
    horloge = Horloge()
    echantillonneur = EchantillonneurNvml(0.2, nvml=nvml, horloge=horloge)
    assert echantillonneur.ouvrir()
    echantillonneur.echantillonner()  # t=100, 100 W
    horloge.t += 10
    echantillonneur.echantillonner()  # t=110, 200 W : (100+200)/2 * 10 = 1500 W.s
    horloge.t += 10
    echantillonneur.echantillonner()  # t=120, 200 W : 200 * 10 = 2000 W.s
    assert echantillonneur.energie_wh == pytest.approx(3500 / 3600)
    assert echantillonneur.puissance_max_w == pytest.approx(200.0)
    assert echantillonneur.puissance_moyenne_w() == pytest.approx(500 / 3)


def test_vram_maximum_des_deux_sources(tmp_path: Path) -> None:
    nvml = NvmlSimule([50_000], [3 * GO, 7 * GO, 5 * GO])
    torch = TorchSimule(alloue=4 * GO, reserve=6 * GO)
    mesure, horloge, _ = fabrique(tmp_path, nvml=nvml, torch=torch)
    mesure.nvml.demarrer = lambda: None  # type: ignore[method-assign]
    mesure.on_train_begin(ARGS, etat())
    mesure.nvml.echantillonner()  # relevé intermédiaire : 7 Go
    horloge.t += 1
    mesure.on_train_end(ARGS, etat())  # dernier relevé : 5 Go
    vram = mesure.resultat["vram"]
    assert vram["allouee_max_octets"] == 4 * GO
    assert vram["reservee_max_octets"] == 6 * GO
    assert vram["nvml_max_octets"] == 7 * GO
    assert vram["max_octets"] == 7 * GO
    assert "reset" in torch.appels  # les pics sont ceux du Run, pas ceux d'avant
    assert nvml.ferme


def test_vram_torch_plus_grande_que_nvml(tmp_path: Path) -> None:
    nvml = NvmlSimule([50_000], [2 * GO])
    mesure, horloge, _ = fabrique(
        tmp_path, nvml=nvml, torch=TorchSimule(alloue=3 * GO, reserve=5 * GO)
    )
    jouer(mesure, horloge, pas=11)
    assert mesure.resultat["vram"]["max_octets"] == 5 * GO


def test_energie_dans_le_resultat(tmp_path: Path) -> None:
    nvml = NvmlSimule([100_000], [GO])
    mesure, horloge, _ = fabrique(tmp_path, nvml=nvml)
    mesure.nvml.demarrer = lambda: None  # type: ignore[method-assign]
    # Sans fil : relevés au début (t=100) et à l'arrêt (t=111), 100 W pendant 11 s.
    jouer(mesure, horloge, pas=11)
    energie = mesure.resultat["energie"]
    assert energie["wh"] == pytest.approx(100 * 11 / 3600)
    assert energie["echantillons"] == 2
    assert energie["periode_ms"] == 200
    assert mesure.resultat["nvml"] == {"disponible": True, "motif": None}


def test_nvml_absent_degrade_sans_interrompre(tmp_path: Path) -> None:
    mesure, horloge, _ = fabrique(tmp_path, nvml=NvmlSimule([0], [0], echec_init=True))
    jouer(mesure, horloge, pas=12)
    assert mesure.resultat["energie"]["wh"] is None
    assert mesure.resultat["vram"]["max_octets"] is None  # ni CUDA ni NVML
    assert mesure.resultat["nvml"]["disponible"] is False
    assert "OSError" in mesure.resultat["nvml"]["motif"]
    assert mesure.resultat["debit"]["tokens_par_s"] == pytest.approx(100.0)


def test_echantillonnage_par_fil() -> None:
    """Le fil réel prend plusieurs relevés à la période demandée, puis s'arrête."""
    nvml = NvmlSimule([100_000], [GO])
    echantillonneur = EchantillonneurNvml(0.005, nvml=nvml)
    assert echantillonneur.ouvrir()
    echantillonneur.demarrer()
    time.sleep(0.15)
    echantillonneur.arreter()
    assert echantillonneur.echantillons >= 3
    assert echantillonneur.energie_wh > 0
    assert nvml.ferme
    echantillonneur.arreter()  # idempotent


# --- Critère 3 : écriture dans metriques.jsonl et couts.json ------------------------------


def test_ecriture_metriques_et_couts(tmp_path: Path) -> None:
    nvml = NvmlSimule([100_000], [GO])
    mesure, horloge, run = fabrique(tmp_path, nvml=nvml)
    jouer(mesure, horloge, pas=12)
    couts_json = json.loads((run.dossier / "couts.json").read_text(encoding="utf-8"))
    assert couts_json == json.loads(json.dumps(mesure.resultat))
    lignes = run.lire_jsonl("metriques.jsonl")
    assert len(lignes) == 1
    assert lignes[0]["evenement"] == "couts"
    assert lignes[0]["debit"] == couts_json["debit"]
    assert lignes[0]["energie"] == couts_json["energie"]


def test_terminer_est_idempotent(tmp_path: Path) -> None:
    mesure, horloge, run = fabrique(tmp_path)
    jouer(mesure, horloge, pas=11)
    premier = mesure.terminer()
    assert mesure.terminer() is premier
    assert len(run.lire_jsonl("metriques.jsonl")) == 1


def test_arret_avant_la_fin_ecrit_ce_qui_est_mesure(tmp_path: Path) -> None:
    """`terminer()` en `finally` : l'entraînement interrompu garde ses mesures."""
    mesure, horloge, run = fabrique(tmp_path)
    mesure.on_train_begin(ARGS, etat())
    horloge.t += 2
    mesure.on_step_end(ARGS, etat(100, 1))
    mesure.terminer()
    assert (run.dossier / "couts.json").exists()
    assert mesure.resultat["pas_total"] == 1
    assert mesure.resultat["debit"]["tokens_par_s"] is None


def test_reprise_n_ecrase_pas_couts_json(tmp_path: Path) -> None:
    mesure, horloge, run = fabrique(tmp_path)
    jouer(mesure, horloge, pas=11)
    seconde = MesureCouts(
        run,
        mesure.config,
        torch=TorchSimule(0, 0, cuda=False),
        nvml=NvmlSimule([0], [0], echec_init=True),
        horloge=horloge,
    )
    jouer(seconde, horloge, pas=11, depart=11)
    assert (run.dossier / "couts-2.json").exists()
    assert len(run.lire_jsonl("metriques.jsonl")) == 2


# --- Callback du Trainer ------------------------------------------------------------------


def test_callback_delegue_a_la_mesure(tmp_path: Path) -> None:
    class BaseCallback:
        def __init__(self) -> None:
            pass

    mesure, horloge, run = fabrique(tmp_path)
    callback = creer_callback(mesure, transformers=SimpleNamespace(TrainerCallback=BaseCallback))
    assert isinstance(callback, BaseCallback)
    callback.on_train_begin(ARGS, etat(), None)
    for pas in range(1, 13):
        horloge.t += 1
        callback.on_step_end(ARGS, etat(pas * 100, pas), None)
    callback.on_train_end(ARGS, etat(1200, 12), None)
    assert mesure.resultat["debit"]["tokens_par_s"] == pytest.approx(100.0)
    assert (run.dossier / "couts.json").exists()


def test_module_sans_import_lourd_au_niveau_module() -> None:
    source = Path(couts.__file__).read_text(encoding="utf-8")
    for lourd in ("torch", "transformers", "pynvml"):
        assert f"\nimport {lourd}" not in source
        assert f"\nfrom {lourd}" not in source
