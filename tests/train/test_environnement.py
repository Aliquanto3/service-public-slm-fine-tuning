"""Story 10.1 : environnement d'entraînement Windows et mesure H-WIN-TRAIN.

Les tests unitaires tournent sans l'extra `train` : torch, transformers, peft, trl,
datasets et bitsandbytes sont remplacés par une pile simulée (`PileSimulee`). Les données
sont des tokens aléatoires ; aucun exemple d'entraînement n'est rédigé.

Les tests réels sont marqués `gpu` et `lent` ; ils lisent les poids sous
`SLMSP_MODELS_DIR` (dépôt principal) et prennent le vrai `gpu.lock` :
`SLMSP_MODELS_DIR=<principal>/models uv run pytest -m "gpu and lent" tests/train`.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import main
from slmsp.cli import train as train_cli
from slmsp.core.config import ENV_IMPOSE
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide, RessourceOccupee
from slmsp.core.var import dossier_var, verrou_gpu
from slmsp.inference import processus
from slmsp.train import environnement

LOURDS = ("torch", "transformers", "trl", "peft", "bitsandbytes", "datasets", "unsloth")
GO = 1024**3


# --- Pile simulée ---------------------------------------------------------------------------


class OOMSimule(RuntimeError):
    pass


class CudaSimule:
    OutOfMemoryError = OOMSimule

    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self.reserve = 0
        self.alloue = 0

    def is_available(self) -> bool:
        return self.scenario.cuda

    def get_device_capability(self, _i: int = 0) -> tuple[int, int]:
        return self.scenario.capacite

    def get_device_properties(self, _i: int = 0) -> Any:
        return SimpleNamespace(total_memory=self.scenario.memoire)

    def get_device_name(self, _i: int = 0) -> str:
        return "Carte simulée"

    def is_bf16_supported(self) -> bool:
        return self.scenario.bf16

    def empty_cache(self) -> None:
        self.scenario.vidages += 1

    def reset_peak_memory_stats(self) -> None:
        self.reserve = self.alloue = 0

    def max_memory_allocated(self) -> int:
        return self.alloue

    def max_memory_reserved(self) -> int:
        return self.reserve

    def synchronize(self) -> None:
        pass


class Scenario:
    """Comportement de la pile simulée."""

    def __init__(self, **reglages: Any) -> None:
        self.cuda = True
        self.capacite = (8, 6)
        self.bf16 = True
        self.memoire = 8 * GO
        self.echec_4bits: Exception | None = None
        self.oom: set[int] = set()
        self.reserve: dict[int, int] = {}
        self.perte = 2.5
        self.chargements: list[dict[str, Any]] = []
        self.configs: list[dict[str, Any]] = []
        self.jeux: list[dict[str, Any]] = []
        self.vidages = 0
        for cle, valeur in reglages.items():
            setattr(self, cle, valeur)


class Rappel:
    """Base de `TrainerCallback`."""


def pile_simulee(scenario: Scenario) -> environnement.Pile:
    cuda = CudaSimule(scenario)
    torch = SimpleNamespace(
        __version__="2.14.1+cu130",
        version=SimpleNamespace(cuda="13.0"),
        bfloat16="bf16",
        cuda=cuda,
    )

    class Modele:
        def __init__(self) -> None:
            self.config = SimpleNamespace(use_cache=True)

    class AutoModelForCausalLM:
        @staticmethod
        def from_pretrained(chemin: str, **arguments: Any) -> Modele:
            scenario.chargements.append({"chemin": chemin, **arguments})
            if "quantization_config" in arguments and scenario.echec_4bits is not None:
                raise scenario.echec_4bits
            return Modele()

    class Tokenizer:
        pad_token = None
        eos_token = "<fin>"
        pad_token_id = 0
        bos_token_id = 1
        eos_token_id = 2

        def __len__(self) -> int:
            return 500

    class AutoTokenizer:
        @staticmethod
        def from_pretrained(_chemin: str) -> Tokenizer:
            return Tokenizer()

    transformers = SimpleNamespace(
        AutoModelForCausalLM=AutoModelForCausalLM,
        AutoTokenizer=AutoTokenizer,
        BitsAndBytesConfig=lambda **kw: {"bnb": kw},
        TrainerCallback=Rappel,
    )
    peft = SimpleNamespace(
        prepare_model_for_kbit_training=lambda modele, **_kw: modele,
        LoraConfig=lambda **kw: kw,
        get_peft_model=lambda modele, _config: modele,
    )

    class SFTConfig:
        def __init__(self, **arguments: Any) -> None:
            scenario.configs.append(arguments)
            self.arguments = arguments

    class SFTTrainer:
        def __init__(self, *, model, args, train_dataset, processing_class, callbacks) -> None:
            self.args = args.arguments
            self.jeu = train_dataset
            self.rappels = callbacks
            scenario.jeux.append(train_dataset)

        def train(self) -> None:
            longueur = self.args["max_length"]
            cuda.alloue = longueur * 1000
            cuda.reserve = scenario.reserve.get(longueur, 3 * GO)
            if longueur in scenario.oom:
                raise OOMSimule("CUDA out of memory (simulé)")
            for _ in range(self.args["max_steps"]):
                for rappel in self.rappels:
                    rappel.on_step_begin(None, None, None)
                    rappel.on_step_end(None, None, None)
                    rappel.on_log(None, None, None, logs={"loss": scenario.perte})

    trl = SimpleNamespace(SFTConfig=SFTConfig, SFTTrainer=SFTTrainer)
    datasets = SimpleNamespace(Dataset=SimpleNamespace(from_dict=lambda d: d))
    return environnement.Pile(
        torch=torch,
        transformers=transformers,
        peft=peft,
        trl=trl,
        datasets=datasets,
        bitsandbytes=SimpleNamespace(__name__="bitsandbytes"),
    )


CONFIG_GRANITE = {
    "model_type": "granitemoehybrid",
    "architectures": ["GraniteMoeHybridForCausalLM"],
    "layer_types": ["attention"] * 4,
    "mamba_d_state": 256,  # clés mamba_* sans couche Mamba : accepté
    "vocab_size": 400,
}


def _sonder(scenario: Scenario, tmp_path: Path, **arguments: Any) -> environnement.ResultatSonde:
    reglages = {
        "slug": "granite-4.0-1b",
        "dossier": tmp_path / "poids",
        "config_modele": CONFIG_GRANITE,
        "longueurs": (16, 32, 64),
        "pas": 2,
        "dossier_travail": tmp_path / "travail",
        "pile": pile_simulee(scenario),
    }
    reglages.update(arguments)
    return environnement.sonder(**reglages)


# --- Imports paresseux ----------------------------------------------------------------------


def test_aucun_import_lourd_au_chargement() -> None:
    code = (
        "import sys\n"
        "import slmsp.train.environnement, slmsp.cli.train\n"
        f"lourds = [m for m in {LOURDS!r} if m in sys.modules]\n"
        "assert not lourds, lourds\n"
    )
    import subprocess

    resultat = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8"
    )
    assert resultat.returncode == 0, resultat.stderr


# --- Contrôles matériels ----------------------------------------------------------------------


def test_materiel_nominal() -> None:
    controle = environnement.controler_materiel(pile_simulee(Scenario()).torch)
    assert controle.bloquant is None
    ligne = controle.ligne()
    assert ligne["capacite"] == "8.6" and ligne["bf16"] is True and ligne["fp8"] is False
    assert ligne["memoire_totale"] == 8 * GO and ligne["version_torch"] == "2.14.1+cu130"


def test_materiel_sans_cuda() -> None:
    controle = environnement.controler_materiel(pile_simulee(Scenario(cuda=False)).torch)
    assert controle.cuda is False
    assert "CUDA indisponible" in (controle.bloquant or "")


def test_materiel_capacite_insuffisante() -> None:
    controle = environnement.controler_materiel(pile_simulee(Scenario(capacite=(7, 5))).torch)
    assert "capacité CUDA 7.5" in (controle.bloquant or "")


def test_materiel_sans_bf16() -> None:
    controle = environnement.controler_materiel(pile_simulee(Scenario(bf16=False)).torch)
    assert "bf16" in (controle.bloquant or "")


def test_materiel_fp8_releve_sur_ada() -> None:
    controle = environnement.controler_materiel(pile_simulee(Scenario(capacite=(8, 9))).torch)
    assert controle.fp8 is True and controle.bloquant is None


# --- Contrôles du modèle ----------------------------------------------------------------------


def test_config_dense_acceptee() -> None:
    resume = environnement.controler_config_modele(CONFIG_GRANITE, "granite-4.0-1b")
    assert resume["couches"] == ["attention"] and resume["vision_config"] is False


@pytest.mark.parametrize(
    "config",
    [
        {"quantization_config": {"quant_method": "fp8", "fmt": "e4m3"}},
        {
            "text_config": {
                "quantization_config": {"quant_method": "compressed-tensors", "format": "float8"}
            }
        },
    ],
)
def test_config_fp8_refusee(config: dict[str, Any]) -> None:
    with pytest.raises(ConfigurationInvalide, match="FP8"):
        environnement.controler_config_modele(config, "modele")


def test_config_mamba_refusee() -> None:
    config = {"layer_types": ["attention", "mamba", "attention"]}
    with pytest.raises(ConfigurationInvalide, match="Mamba"):
        environnement.controler_config_modele(config, "granite-h")


def test_config_vision_refusee() -> None:
    config = {"vision_config": {"model_type": "pixtral"}, "text_config": {}}
    with pytest.raises(ConfigurationInvalide, match="vision"):
        environnement.controler_config_modele(config, "ministral-3-3b")


# --- Arguments d'entraînement ---------------------------------------------------------------


def test_arguments_entrainement_surs(tmp_path: Path) -> None:
    arguments = environnement.arguments_entrainement(tmp_path, longueur=2048, pas=4)
    assert arguments["report_to"] == "none"
    assert arguments["push_to_hub"] is False
    assert arguments["save_strategy"] == "no"
    assert "save_total_limit" not in arguments
    assert arguments["per_device_train_batch_size"] == 1
    assert arguments["max_length"] == 2048 and arguments["max_steps"] == 4
    assert arguments["packing"] is False and arguments["padding_free"] is False
    assert arguments["dataset_kwargs"] == {"skip_prepare_dataset": True}
    # Aucun paramètre propre à une architecture par défaut.
    assert "loss_type" not in arguments and "router_aux_loss_coef" not in arguments


CONFIG_GRANITE_REELLE = {
    **CONFIG_GRANITE,
    "logits_scaling": 8,
    "output_router_logits": False,
    "router_aux_loss_coef": 0.01,
    "num_local_experts": 0,
    "num_experts_per_tok": 0,
}
CONFIG_SMOLLM3 = {
    "model_type": "smollm3",
    "architectures": ["SmolLM3ForCausalLM"],
    "vocab_size": 400,
}


def test_arguments_specifiques_granite_seulement() -> None:
    assert environnement.arguments_specifiques(CONFIG_GRANITE_REELLE) == {
        "loss_type": "nll",
        "router_aux_loss_coef": 0.0,
    }
    assert environnement.arguments_specifiques(CONFIG_SMOLLM3) == {}
    assert environnement.arguments_specifiques({"logits_scaling": 1.0}) == {}
    # Un vrai MoE garde la perte auxiliaire de routage par défaut de TRL.
    moe = {"output_router_logits": True, "num_local_experts": 8}
    assert environnement.arguments_specifiques(moe) == {}
    # Configuration multimodale : la sous-configuration texte compte aussi.
    assert environnement.arguments_specifiques({"text_config": {"logits_scaling": 4}}) == {
        "loss_type": "nll"
    }


def test_arguments_specifiques_ajoutes_sans_ecraser(tmp_path: Path) -> None:
    arguments = environnement.arguments_entrainement(
        tmp_path, longueur=64, pas=1, specifiques={"loss_type": "nll"}
    )
    assert arguments["loss_type"] == "nll" and arguments["push_to_hub"] is False
    with pytest.raises(ConfigurationInvalide, match="report_to"):
        environnement.arguments_entrainement(
            tmp_path, longueur=64, pas=1, specifiques={"report_to": "wandb"}
        )


@pytest.mark.parametrize(
    ("config", "attendus"),
    [
        (CONFIG_GRANITE_REELLE, {"loss_type": "nll", "router_aux_loss_coef": 0.0}),
        (CONFIG_SMOLLM3, {}),
    ],
)
def test_sonde_parametres_propres_au_modele(
    tmp_path: Path, config: dict[str, Any], attendus: dict[str, Any]
) -> None:
    scenario = Scenario()
    resultat = _sonder(scenario, tmp_path, config_modele=config, slug="smollm3-3b")
    assert resultat.sonde["arguments_specifiques"] == attendus
    assert scenario.configs
    for sft in scenario.configs:
        for cle in ("loss_type", "router_aux_loss_coef"):
            assert sft.get(cle) == attendus.get(cle)


def test_tokens_aleatoires_reproductibles() -> None:
    a = environnement.tokens_aleatoires(3, 50, 100, graine=7, exclus={0, 1})
    b = environnement.tokens_aleatoires(3, 50, 100, graine=7, exclus={0, 1})
    assert a == b
    assert all(len(s) == 50 for s in a)
    assert all(0 <= t < 100 and t not in (0, 1) for s in a for t in s)
    assert environnement.tokens_aleatoires(1, 50, 100, graine=8) != a[:1]


def test_json_sur_remplace_nan() -> None:
    assert environnement.json_sur({"a": [float("nan"), 1.0], "b": float("inf")}) == {
        "a": ["nan", 1.0],
        "b": "inf",
    }


# --- Sonde ----------------------------------------------------------------------------------


def test_sonde_nominale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for nom in ENV_IMPOSE:
        monkeypatch.delenv(nom, raising=False)
    scenario = Scenario()
    resultat = _sonder(scenario, tmp_path)
    assert resultat.statut == "complet" and resultat.motif is None
    assert resultat.methode_effective == "qlora" and resultat.pas_reussi
    for nom, valeur in ENV_IMPOSE.items():
        assert os.environ[nom] == valeur
    # Chargement 4 bits nf4 sur le GPU 0.
    chargement = scenario.chargements[0]
    assert chargement["quantization_config"]["bnb"]["bnb_4bit_quant_type"] == "nf4"
    assert chargement["quantization_config"]["bnb"]["load_in_4bit"] is True
    # Arguments sûrs transmis à SFTConfig, une configuration par longueur.
    assert [c["max_length"] for c in scenario.configs] == [16, 32, 64]
    for config in scenario.configs:
        assert config["report_to"] == "none" and config["push_to_hub"] is False
        assert config["save_strategy"] == "no" and "save_total_limit" not in config
        assert config["max_steps"] == 1 + 2  # chauffe + pas mesurés
    # Jeu pré-tokenisé : séquences exactes, sans padding.
    for jeu, longueur in zip(scenario.jeux, (16, 32, 64), strict=True):
        assert set(jeu) == {"input_ids"}
        assert all(len(s) == longueur for s in jeu["input_ids"])
    sonde = resultat.sonde
    assert sonde["methode"] == "qlora" and sonde["longueur_max_ok"] == 64
    assert sonde["env_impose"] == dict(ENV_IMPOSE)
    assert sonde["arguments_entrainement"]["report_to"] == "none"
    assert sonde["arguments_entrainement"]["push_to_hub"] is False
    assert sonde["controles_materiel"]["capacite"] == "8.6"
    for mesure in sonde["mesures"]:
        assert mesure["statut"] == "ok" and mesure["perte_finie"] is True
        assert mesure["perte"] == 2.5 and len(mesure["pertes"]) == 3
        assert mesure["max_memory_reserved"] == 3 * GO
        assert mesure["max_memory_allocated"] == mesure["longueur"] * 1000
        assert len(mesure["durees_pas_s"]) == 3


def test_sonde_sans_cuda(tmp_path: Path) -> None:
    resultat = _sonder(Scenario(cuda=False), tmp_path)
    assert resultat.statut == "partiel-erreur"
    assert "CUDA indisponible" in (resultat.motif or "")
    assert resultat.sonde["mesures"] == []


def test_sonde_oom_arrete_les_longueurs_suivantes(tmp_path: Path) -> None:
    scenario = Scenario(oom={32})
    resultat = _sonder(scenario, tmp_path)
    statuts = [m["statut"] for m in resultat.sonde["mesures"]]
    assert statuts == ["ok", "oom", "non-tentee"]
    assert len(scenario.configs) == 2  # 64 non tentée
    assert scenario.vidages > 0  # cache CUDA vidé
    assert resultat.statut == "complet" and resultat.sonde["longueur_max_ok"] == 16


def test_sonde_debordement_wddm(tmp_path: Path) -> None:
    scenario = Scenario(reserve={32: 9 * GO})
    resultat = _sonder(scenario, tmp_path)
    statuts = [m["statut"] for m in resultat.sonde["mesures"]]
    assert statuts == ["ok", "debordement", "non-tentee"]


def test_sonde_debordement_avant_la_memoire_totale(tmp_path: Path) -> None:
    # 95 % de la carte (SmolLM3 3B à 2048) : le pilote WDDM déborde déjà.
    scenario = Scenario(reserve={16: int(0.85 * 8 * GO), 32: int(0.95 * 8 * GO)})
    resultat = _sonder(scenario, tmp_path)
    mesures = resultat.sonde["mesures"]
    assert [m["statut"] for m in mesures] == ["ok", "debordement", "non-tentee"]
    assert mesures[0]["seuil_debordement"] == int(8 * GO * environnement.FRACTION_DEBORDEMENT)
    assert resultat.sonde["longueur_max_ok"] == 16
    assert resultat.sonde["fraction_debordement"] == environnement.FRACTION_DEBORDEMENT


def test_deborde() -> None:
    total = 8 * GO
    assert environnement.deborde(int(0.91 * total), total)
    assert not environnement.deborde(int(0.89 * total), total)
    assert not environnement.deborde(9 * GO, 0)  # mémoire totale inconnue
    assert not environnement.deborde(None, total)


def test_sonde_perte_non_finie(tmp_path: Path) -> None:
    resultat = _sonder(Scenario(perte=float("nan")), tmp_path, longueurs=(16,))
    assert resultat.statut == "partiel-erreur"
    assert resultat.sonde["mesures"][0]["perte_finie"] is False


def test_sonde_repli_bf16_sans_bitsandbytes(tmp_path: Path) -> None:
    scenario = Scenario(echec_4bits=RuntimeError("libbitsandbytes_cuda130.dll introuvable"))
    resultat = _sonder(scenario, tmp_path)
    assert resultat.statut == "degrade"
    assert resultat.methode_effective == "lora"
    assert "libbitsandbytes" in (resultat.motif_quantification or "")
    assert "quantization_config" not in scenario.chargements[-1]
    methodes = environnement.methodes_disponibles(
        slug="granite-4.0-1b",
        methode_demandee="qlora",
        methode_effective=resultat.methode_effective,
        pas_reussi=resultat.pas_reussi,
        motif_quantification=resultat.motif_quantification,
    )
    assert methodes["methodes"]["lora"]["statut"] == "verifiee"
    assert {"qlora", "dora"} <= set(methodes["indisponibles"])
    assert any("bitsandbytes" in r for r in methodes["replis"])


def test_sonde_sans_bitsandbytes_autre_modele(tmp_path: Path) -> None:
    scenario = Scenario(echec_4bits=ImportError("No module named 'bitsandbytes'"))
    resultat = _sonder(scenario, tmp_path, slug="smollm3-3b")
    assert resultat.statut == "partiel-erreur"
    assert "granite-4.0-1b" in (resultat.motif or "")
    assert len(scenario.chargements) == 1  # aucun repli bf16


def test_sonde_lora_demandee(tmp_path: Path) -> None:
    scenario = Scenario()
    resultat = _sonder(scenario, tmp_path, methode="lora")
    assert resultat.statut == "complet" and resultat.methode_effective == "lora"
    assert "quantization_config" not in scenario.chargements[0]


def test_sonde_methode_inconnue(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="méthode"):
        _sonder(Scenario(), tmp_path, methode="orpo")


def test_methodes_qlora_verifiee() -> None:
    methodes = environnement.methodes_disponibles(
        slug="granite-4.0-1b",
        methode_demandee="qlora",
        methode_effective="qlora",
        pas_reussi=True,
    )
    assert methodes["methodes"]["qlora"]["statut"] == "verifiee"
    assert methodes["methodes"]["qlora-unsloth"]["statut"] == "non-sondee"
    assert methodes["indisponibles"] == [] and methodes["replis"] == []
    assert set(methodes["methodes"]) == set(environnement.METHODES)


def test_methodes_unsloth_en_echec() -> None:
    methodes = environnement.methodes_disponibles(
        slug="granite-4.0-1b",
        methode_demandee="qlora",
        methode_effective="qlora",
        pas_reussi=True,
        unsloth={"ok": False, "erreur": "triton absent"},
    )
    assert methodes["indisponibles"] == ["qlora-unsloth"]
    assert methodes["methodes"]["qlora-unsloth"]["motif"] == "triton absent"
    assert any("Unsloth" in r for r in methodes["replis"])


# --- Unsloth ---------------------------------------------------------------------------------


def test_lire_resultat_unsloth() -> None:
    sortie = 'bruit\nSLMSP-RESULTAT {"ok": true, "perte": 1.5}\nfin\n'
    assert environnement.lire_resultat_unsloth(sortie) == {"ok": True, "perte": 1.5}
    assert environnement.lire_resultat_unsloth("rien") is None
    assert environnement.lire_resultat_unsloth("SLMSP-RESULTAT {cassé") is None


def test_commande_unsloth(tmp_path: Path) -> None:
    commande = environnement.commande_unsloth(tmp_path / "e.json", uv="uv.exe")
    projet = environnement.projet_unsloth()
    assert commande == [
        "uv.exe",
        "run",
        "--frozen",  # sous gpu.lock : uv.lock utilisé tel quel, jamais réécrit
        "--project",
        str(projet),
        "python",
        str(projet / "sonde.py"),
        str(tmp_path / "e.json"),
    ]
    assert (projet / "pyproject.toml").is_file() and (projet / "sonde.py").is_file()
    assert (projet / "uv.lock").is_file()  # --frozen exige le verrou versionné


def test_chemin_portable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    modeles = tmp_path / "models"
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(modeles))
    racine = tmp_path / "racine"
    portable = environnement.chemin_portable
    assert portable(modeles / "granite-4.0-1b" / "hf") == "$SLMSP_MODELS_DIR/granite-4.0-1b/hf"
    assert portable(dossier_var() / "unsloth") == "$SLMSP_VAR_DIR/unsloth"
    assert portable(racine / "runs" / "x" / "a.json", racine=racine) == "runs/x/a.json"
    assert portable(environnement.projet_unsloth() / "sonde.py") == "envs/unsloth/sonde.py"
    assert portable(tmp_path / "ailleurs" / "f.txt") == "f.txt"
    commande = environnement.commande_portable(
        [str(tmp_path / "bin" / "uv.exe"), "run", "--frozen", str(racine / "e.json")],
        racine=racine,
    )
    assert commande == ["uv.exe", "run", "--frozen", "e.json"]


# --- CLI --------------------------------------------------------------------------------------


@pytest.fixture
def modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    dossier = tmp_path / "models"
    for slug in ("granite-4.0-1b", "smollm3-3b", "ministral-3-3b"):
        (dossier / slug / "hf").mkdir(parents=True)
        config = dict(CONFIG_GRANITE)
        if slug == "ministral-3-3b":
            config["vision_config"] = {"model_type": "pixtral"}
        (dossier / slug / "hf" / "config.json").write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(dossier))
    return dossier


@pytest.fixture
def scenario(monkeypatch: pytest.MonkeyPatch) -> Scenario:
    scenario = Scenario()
    monkeypatch.setattr(environnement, "charger_pile", lambda: pile_simulee(scenario))
    monkeypatch.setattr(environnement.shutil, "which", lambda _nom: "uv.exe")
    return scenario


def _run_unique(racine: Path) -> Path:
    runs = sorted((racine / "runs" / "train-sonde").iterdir())
    assert len(runs) == 1
    return runs[0]


def _json(chemin: Path) -> Any:
    return json.loads(chemin.read_text(encoding="utf-8"))


def _statut(run: Path) -> str:
    lignes = run.joinpath("etat.jsonl").read_text(encoding="utf-8").splitlines()
    return json.loads(lignes[-1])["statut"]


def _sonde_env(racine: Path, *options: str) -> int:
    return main(
        [
            "train",
            "sonde-env",
            "--longueurs",
            "16,32",
            "--pas",
            "1",
            "--racine",
            str(racine),
            *options,
        ]
    )


def test_cli_sonde_nominale(
    tmp_path: Path, modeles: Path, scenario: Scenario, capsys: pytest.CaptureFixture[str]
) -> None:
    racine = tmp_path / "racine"
    assert _sonde_env(racine) == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "complet"
    manifeste = _json(run / "run.json")
    assert manifeste["type"] == "train-sonde" and manifeste["config"]["methode"] == "qlora"
    assert manifeste["graine"] == environnement.GRAINE
    sonde = _json(run / "sonde.json")
    assert [m["statut"] for m in sonde["mesures"]] == ["ok", "ok"]
    assert sonde["mesures"][0]["max_memory_reserved"] == 3 * GO
    methodes = _json(run / "methodes.json")
    assert methodes["methodes"]["qlora"]["statut"] == "verifiee"
    assert not (run / "unsloth.json").exists()
    assert "complet" in capsys.readouterr().out


def test_cli_verrou_pris_pendant_la_sonde(
    tmp_path: Path, modeles: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    vu: list[bool] = []
    sonder = environnement.sonder

    def sonder_espion(**arguments: Any) -> environnement.ResultatSonde:
        with pytest.raises(RessourceOccupee):
            with verrou_gpu():
                pass
        vu.append(True)
        return sonder(**arguments)

    monkeypatch.setattr(environnement, "sonder", sonder_espion)
    assert _sonde_env(tmp_path / "racine") == CodeSortie.SUCCES
    assert vu == [True]


def test_cli_gpu_occupe(
    tmp_path: Path, modeles: Path, scenario: Scenario, capsys: pytest.CaptureFixture[str]
) -> None:
    racine = tmp_path / "racine"
    with verrou_gpu(commande="autre commande"):
        assert _sonde_env(racine) == CodeSortie.RESSOURCE_OCCUPEE
    assert "GPU occupé" in capsys.readouterr().err
    assert not (racine / "runs").exists()  # aucun run ouvert


def test_cli_sans_cuda(
    tmp_path: Path, modeles: Path, scenario: Scenario, capsys: pytest.CaptureFixture[str]
) -> None:
    scenario.cuda = False
    racine = tmp_path / "racine"
    assert _sonde_env(racine) == CodeSortie.ERREUR
    run = _run_unique(racine)
    assert _statut(run) == "partiel-erreur"
    etat = json.loads(run.joinpath("etat.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert "CUDA indisponible" in etat["motif"]
    assert "CUDA indisponible" in capsys.readouterr().err


def test_cli_repli_bitsandbytes(tmp_path: Path, modeles: Path, scenario: Scenario) -> None:
    scenario.echec_4bits = OSError("bitsandbytes : DLL CUDA introuvable")
    racine = tmp_path / "racine"
    assert _sonde_env(racine) == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "degrade"
    methodes = _json(run / "methodes.json")
    assert methodes["methode_effective"] == "lora"
    assert {"qlora", "dora"} <= set(methodes["indisponibles"])
    assert _json(run / "sonde.json")["methode"] == "lora"


def test_cli_modele_vision_refuse(
    tmp_path: Path, modeles: Path, scenario: Scenario, capsys: pytest.CaptureFixture[str]
) -> None:
    racine = tmp_path / "racine"
    assert _sonde_env(racine, "--modele", "ministral-3-3b") == CodeSortie.ERREUR
    assert "vision" in capsys.readouterr().err
    assert not (racine / "runs").exists()


def test_cli_unsloth_sous_processus(
    tmp_path: Path, modeles: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HF_TOKEN", "jeton-secret")
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-secrete")
    appels: list[dict[str, Any]] = []

    def executer(arguments: list[str], **options: Any) -> tuple[int, str]:
        appels.append({"arguments": arguments, **options})
        return 1, 'trace\nSLMSP-RESULTAT {"ok": false, "erreur": "triton introuvable"}\n'

    monkeypatch.setattr(processus, "executer", executer)
    racine = tmp_path / "racine"
    assert _sonde_env(racine, "--unsloth") == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "degrade"
    [appel] = appels
    assert appel["arguments"][:5] == [
        "uv.exe",
        "run",
        "--frozen",
        "--project",
        str(environnement.projet_unsloth()),
    ]
    assert appel["arguments"][5:7] == ["python", str(environnement.projet_unsloth() / "sonde.py")]
    # Entrée réelle (chemins absolus) sous SLMSP_VAR_DIR ; copie portable dans le run.
    entree = Path(appel["arguments"][7])
    assert entree.parent == dossier_var() / "unsloth"
    assert _json(entree)["longueur"] == 16
    assert Path(_json(entree)["dossier_poids"]) == modeles / "granite-4.0-1b" / "hf"
    copie = _json(run / "unsloth-entree.json")
    assert copie["dossier_poids"] == "$SLMSP_MODELS_DIR/granite-4.0-1b/hf"
    assert copie["dossier_sortie"].startswith("runs/train-sonde/")
    assert Path(appel["cwd"]) == dossier_var() / "unsloth"  # cache Unsloth hors du dépôt
    env = appel["env"]
    assert "HF_TOKEN" not in env and "MISTRAL_API_KEY" not in env
    for nom, valeur in ENV_IMPOSE.items():
        assert env[nom] == valeur
    unsloth = _json(run / "unsloth.json")
    assert unsloth["ok"] is False and unsloth["erreur"] == "triton introuvable"
    methodes = _json(run / "methodes.json")
    assert methodes["indisponibles"] == ["qlora-unsloth"]


def _textes(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        return [t for valeur in obj.values() for t in _textes(valeur)]
    if isinstance(obj, list):
        return [t for valeur in obj for t in _textes(valeur)]
    return [obj] if isinstance(obj, str) else []


def test_cli_aucun_chemin_absolu_dans_le_run(
    tmp_path: Path, modeles: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        processus,
        "executer",
        lambda *_a, **_k: (0, 'SLMSP-RESULTAT {"ok": true, "perte": 3.0}'),
    )
    racine = tmp_path / "racine"
    assert _sonde_env(racine, "--unsloth") == CodeSortie.SUCCES
    run = _run_unique(racine)
    fichiers = sorted(run.glob("*.json"))
    assert {f.name for f in fichiers} >= {"run.json", "sonde.json", "unsloth.json"}
    interdits = (str(tmp_path), str(environnement.projet_unsloth().parents[1]), str(Path.home()))
    for fichier in fichiers:
        for texte in _textes(_json(fichier)):
            assert not Path(texte).is_absolute(), (fichier.name, texte)
            assert not any(prefixe in texte for prefixe in interdits), (fichier.name, texte)
    manifeste = _json(run / "run.json")
    assert "racine" not in manifeste["config"]
    assert manifeste["config"]["dossier_poids"] == "$SLMSP_MODELS_DIR/granite-4.0-1b/hf"
    sonde = _json(run / "sonde.json")
    assert sonde["arguments_entrainement"]["output_dir"] == (
        f"runs/train-sonde/{run.name}/entraineur"
    )
    assert _json(run / "unsloth.json")["commande"][:3] == ["uv.exe", "run", "--frozen"]


def test_cli_provenance_du_code(tmp_path: Path, modeles: Path, scenario: Scenario) -> None:
    racine = tmp_path / "racine"
    assert _sonde_env(racine) == CodeSortie.SUCCES
    provenance = _json(_run_unique(racine) / "run.json")["config"]["provenance_code"]
    assert set(provenance["sha256"]) == set(train_cli.FICHIERS_CODE)
    attendu = hashlib.sha256(Path(environnement.__file__).read_bytes()).hexdigest()
    assert provenance["sha256"]["src/slmsp/train/environnement.py"] == attendu
    assert isinstance(provenance["non_commites"], list)
    assert provenance["code_commite"] is (provenance["non_commites"] == [])


@pytest.mark.skipif(shutil.which("git") is None, reason="git absent")
def test_provenance_signale_le_code_non_suivi(tmp_path: Path) -> None:
    projet = tmp_path / "projet"
    (projet / "envs" / "unsloth").mkdir(parents=True)
    (projet / "envs" / "unsloth" / "sonde.py").write_bytes(b"x = 1\n")

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *arguments],
            cwd=projet,
            check=True,
            capture_output=True,
        )

    git("init", "-q")
    git("add", "envs/unsloth/sonde.py")
    git("commit", "-q", "-m", "init")
    assert train_cli.provenance_code(projet)["code_commite"] is True
    # Code nouveau, non suivi : `git_modifie` de run.json l'ignore, la provenance non.
    (projet / "src" / "slmsp" / "train").mkdir(parents=True)
    (projet / "src" / "slmsp" / "train" / "environnement.py").write_bytes(b"y = 2\n")
    provenance = train_cli.provenance_code(projet)
    assert provenance["code_commite"] is False
    assert provenance["non_commites"] == ["src/slmsp/train/environnement.py"]
    empreinte = hashlib.sha256(b"y = 2\n").hexdigest()
    assert provenance["sha256"]["src/slmsp/train/environnement.py"] == empreinte
    assert provenance["sha256"]["envs/unsloth/uv.lock"] is None
    # Hors dépôt git : provenance inconnue, pas d'erreur.
    hors = train_cli.provenance_code(tmp_path / "vide")
    assert hors["git_commit"] is None and hors["code_commite"] is None


def test_cli_unsloth_reussi(
    tmp_path: Path, modeles: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        processus,
        "executer",
        lambda *_a, **_k: (0, 'SLMSP-RESULTAT {"ok": true, "perte": 3.0, "tokens_par_s": 900}'),
    )
    racine = tmp_path / "racine"
    assert _sonde_env(racine, "--unsloth") == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "complet"
    assert _json(run / "methodes.json")["methodes"]["qlora-unsloth"]["statut"] == "verifiee"


def test_cli_unsloth_uv_introuvable(
    tmp_path: Path, modeles: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(environnement.shutil, "which", lambda _nom: None)
    racine = tmp_path / "racine"
    assert _sonde_env(racine, "--unsloth") == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "degrade"
    assert "uv introuvable" in _json(run / "unsloth.json")["erreur"]


# --- Tests réels (GPU) -------------------------------------------------------------------------


@pytest.fixture
def pile_reelle() -> Any:
    torch = pytest.importorskip("torch")
    for nom in ("transformers", "trl", "peft", "datasets"):
        pytest.importorskip(nom)
    return torch


@pytest.mark.gpu
def test_torch_cuda_cu130(pile_reelle: Any) -> None:
    torch = pile_reelle
    assert torch.__version__.endswith("+cu130"), torch.__version__
    assert torch.version.cuda is not None and torch.version.cuda.startswith("13.0")
    assert torch.cuda.is_available()
    controle = environnement.controler_materiel(torch)
    assert controle.bloquant is None, controle.bloquant


@pytest.mark.lent
def test_arguments_acceptes_par_sftconfig(pile_reelle: Any, tmp_path: Path) -> None:
    from trl import SFTConfig

    config = SFTConfig(**environnement.arguments_entrainement(tmp_path, longueur=512, pas=2))
    assert config.report_to == [] or config.report_to == "none" or config.report_to == ["none"]
    assert config.push_to_hub is False
    assert config.save_total_limit is None
    granite = environnement.arguments_specifiques(CONFIG_GRANITE_REELLE)
    config = SFTConfig(
        **environnement.arguments_entrainement(tmp_path, longueur=512, pas=2, specifiques=granite)
    )
    assert config.loss_type == "nll" and config.router_aux_loss_coef == 0.0


@pytest.mark.gpu
@pytest.mark.lent
def test_sonde_reelle_granite(
    pile_reelle: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.config import dossier_modeles

    if not (dossier_modeles() / "granite-4.0-1b" / "hf" / "config.json").is_file():
        pytest.skip("poids de granite-4.0-1b absents : définir SLMSP_MODELS_DIR")
    # Le vrai verrou partagé par les copies de travail (SLMSP_VAR_DIR par défaut).
    monkeypatch.delenv("SLMSP_VAR_DIR", raising=False)
    racine = tmp_path / "racine"
    code = main(
        [
            "train",
            "sonde-env",
            "--modele",
            "granite-4.0-1b",
            "--longueurs",
            "512",
            "--pas",
            "1",
            "--racine",
            str(racine),
        ]
    )
    if code == CodeSortie.RESSOURCE_OCCUPEE:
        pytest.skip("GPU occupé par une autre commande")
    assert code == CodeSortie.SUCCES
    run = _run_unique(racine)
    assert _statut(run) == "complet"
    sonde = _json(run / "sonde.json")
    [mesure] = sonde["mesures"]
    assert sonde["methode"] == "qlora"
    assert mesure["statut"] == "ok" and mesure["perte_finie"] is True
    assert 0 < mesure["max_memory_reserved"] <= sonde["controles_materiel"]["memoire_totale"]
    assert mesure["tokens_par_s"] > 0
