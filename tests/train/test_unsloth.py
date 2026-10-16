"""Story 10.5 : variante QLoRA Unsloth en environnement isolé.

Le sous-processus est remplacé par une fonction factice qui écrit un adaptateur factice et
rend la ligne `SLMSP-RESULTAT`. Les jeux sont des identifiants entiers factices ; aucun
exemple d'entraînement n'est rédigé. Le test réel (`gpu` et `lent`) n'est lancé qu'à la main :

    SLMSP_MODELS_DIR=<principal>/models uv run pytest -m "gpu and lent" tests/train/test_unsloth.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import ArtefactExistant, nouveau_run
from slmsp.core.erreurs import SlmspError
from slmsp.train import variante_unsloth as vu
from slmsp.train.environnement import MARQUEUR_RESULTAT, projet_unsloth

RACINE = Path(__file__).resolve().parents[2]
GO = 1024**3
EXEMPLES = [
    {"input_ids": [7, 8, 9, 10], "labels": [-100, -100, 9, 10]},
    {"input_ids": [3, 4], "labels": [-100, 4]},
]
QUANT_NF4 = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_use_double_quant": True,
    "bnb_4bit_compute_dtype": "torch.bfloat16",
}


def _charger_entrainer() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "entrainer_unsloth", projet_unsloth() / "entrainer.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "var"))
    monkeypatch.setattr(vu.shutil, "which", lambda _nom: "uv.exe")
    monkeypatch.setattr(vu, "_echantillonneur", lambda *_a: None)
    return nouveau_run("train", "v-test", {"campagne": "c"}, graine=1, racine=tmp_path / "racine")


def _resultat(**extra: Any) -> dict[str, Any]:
    base = {
        "ok": True,
        "pas": 12,
        "pas_chauffe": 10,
        "duree_s": 30.0,
        "debut_epoch": 100.0,
        "fin_epoch": 130.0,
        "tokens_mesures": 600,
        "duree_mesuree_s": 2.0,
        "debit_tokens_par_s": 300.0,
        "pertes": [{"pas": 1, "perte": 2.5}, {"pas": 2, "perte": 2.0}],
        "max_memory_allocated": 3 * GO,
        "max_memory_reserved": 4 * GO,
        "memoire_totale": 8 * GO,
        "quantification": QUANT_NF4,
        "versions": {"unsloth": "2026.10.3"},
    }
    return {**base, **extra}


class Sous:
    """Double de `processus.executer` : écrit l'adaptateur puis rend la sortie."""

    def __init__(self, resultat: dict[str, Any], code: int = 0, adaptateur: bool = True) -> None:
        self.resultat, self.code, self.adaptateur = resultat, code, adaptateur
        self.appels: list[dict[str, Any]] = []

    def __call__(self, arguments: list[str], **options: Any) -> tuple[int, str]:
        entree = json.loads(Path(arguments[-1]).read_text(encoding="utf-8"))
        self.appels.append({"arguments": arguments, "entree": entree, **options})
        if self.adaptateur:
            dossier = Path(entree["dossier_adaptateur"])
            dossier.mkdir(parents=True)
            for nom in vu.FICHIERS_ADAPTATEUR:
                (dossier / nom).write_text("<fichier-factice>", encoding="utf-8")
        return self.code, "bruit\n" + MARQUEUR_RESULTAT + json.dumps(self.resultat) + "\n"


def _lancer(run: Any, sous: Sous, tmp_path: Path, **options: Any) -> dict[str, Any]:
    arguments = {
        "output_dir": str(run.dossier / "checkpoints"),
        "max_steps": 12,
        "report_to": "none",
    }
    return vu.entrainer(
        run,
        exemples=EXEMPLES,
        pad_id=0,
        dossier_poids=tmp_path / "poids",
        arguments=arguments,
        longueur=2048,
        graine=1234,
        lora={"r": 16, "alpha": 32, "dropout": 0.0},
        racine=tmp_path / "racine",
        executer=sous,
        **options,
    )


def test_run_nominal(run: Any, tmp_path: Path) -> None:
    sous = Sous(_resultat())
    resume = _lancer(run, sous, tmp_path)

    appel = sous.appels[0]
    commande = appel["arguments"]
    assert commande[1:6] == ["run", "--frozen", "--project", str(projet_unsloth()), "python"]
    assert Path(commande[6]).name == "entrainer.py"
    assert Path(appel["cwd"]).parent.name == "unsloth"
    assert Path(appel["journal"]) == run.dossier / "log-unsloth.txt"
    assert appel["env"]["HF_HUB_DISABLE_TELEMETRY"] == "1"  # env_sous_processus()
    # Le jeu transmis est exactement celui de train.masque : ids et labels, sans retouche.
    jeu = json.loads(Path(appel["entree"]["jeu"]).read_text(encoding="utf-8"))
    assert jeu == {"pad_token_id": 0, "exemples": EXEMPLES}
    assert appel["entree"]["checkpointing"] is True  # W4.5 : pas de déport CPU par défaut
    assert appel["entree"]["pas_chauffe"] == 10  # config/entrainement.toml

    assert (run.dossier / "adaptateur" / "adapter_model.safetensors").is_file()
    couts = json.loads((run.dossier / "couts.json").read_text(encoding="utf-8"))
    assert couts["debit_tokens_par_s"] == 300.0
    assert couts["vram_max_octets"] == 4 * GO
    metriques = [
        json.loads(ligne)
        for ligne in (run.dossier / "metriques.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [m["evenement"] for m in metriques] == ["perte", "perte", "couts"]
    assert resume["debordement"] is False
    assert resume["quantification"] == QUANT_NF4
    assert "moins de deux relevés de puissance : énergie non mesurée" in resume["avertissements"]


def test_entree_archivee_sans_chemin_absolu(run: Any, tmp_path: Path) -> None:
    _lancer(run, Sous(_resultat()), tmp_path)
    texte = (run.dossier / vu.NOM_ENTREE).read_text(encoding="utf-8")
    assert str(tmp_path) not in texte.replace("\\\\", "\\")
    assert "$SLMSP_VAR_DIR/unsloth/" in texte
    assert "checkpoints" in json.loads(texte)["arguments"]["output_dir"]


def test_echec_du_sous_processus(run: Any, tmp_path: Path) -> None:
    sous = Sous({"ok": False, "erreur": "OutOfMemoryError : 8 Go"}, code=1, adaptateur=False)
    with pytest.raises(vu.ErreurUnsloth, match="OutOfMemoryError"):
        _lancer(run, sous, tmp_path)
    journal = (run.dossier / "log.jsonl").read_text(encoding="utf-8")
    assert "unsloth-echec" in journal
    assert not (run.dossier / "couts.json").exists()


def test_sortie_sans_resultat(run: Any, tmp_path: Path) -> None:
    def muet(arguments: list[str], **_o: Any) -> tuple[int, str]:
        return 0, "rien"

    with pytest.raises(vu.ErreurUnsloth, match="code 0"):
        _lancer(run, muet, tmp_path)  # type: ignore[arg-type]


def test_adaptateur_incomplet(run: Any, tmp_path: Path) -> None:
    def partiel(arguments: list[str], **_o: Any) -> tuple[int, str]:
        entree = json.loads(Path(arguments[-1]).read_text(encoding="utf-8"))
        dossier = Path(entree["dossier_adaptateur"])
        dossier.mkdir(parents=True)
        (dossier / "adapter_config.json").write_text("{}", encoding="utf-8")
        return 0, MARQUEUR_RESULTAT + json.dumps(_resultat())

    with pytest.raises(vu.ErreurUnsloth, match="adapter_model.safetensors"):
        _lancer(run, partiel, tmp_path)  # type: ignore[arg-type]


def test_adaptateur_jamais_ecrase(run: Any, tmp_path: Path) -> None:
    (run.dossier / "adaptateur").mkdir()
    sous = Sous(_resultat())
    with pytest.raises(ArtefactExistant):
        _lancer(run, sous, tmp_path)
    assert sous.appels == []


def test_debordement_et_quantification_consignes(run: Any, tmp_path: Path) -> None:
    resultat = _resultat(
        max_memory_reserved=int(7.9 * GO),
        quantification={"load_in_4bit": True, "bnb_4bit_quant_type": "fp4"},
    )
    resume = _lancer(run, Sous(resultat), tmp_path)
    assert resume["debordement"] is True
    assert any("pas nf4" in a for a in resume["avertissements"])
    assert any("double quantification absente" in a for a in resume["avertissements"])


def test_controler_quantification() -> None:
    assert vu.controler_quantification(QUANT_NF4) == []
    assert "non prouvée" in vu.controler_quantification(None)[0]


def test_mesures_fenetre_nvml() -> None:
    releves = [
        (90.0, 500.0, 7 * GO),  # avant l'entraînement : écarté
        (100.0, 100.0, 2 * GO),
        (130.0, 100.0, 3 * GO),
        (140.0, 500.0, 7 * GO),  # après : écarté
    ]
    mesures = vu.mesures_depuis(_resultat(), periode=0.2, releves=releves)
    assert mesures.releves_nvml == 2
    assert mesures.energie_wh == pytest.approx(100.0 * 30 / 3600)
    assert mesures.vram_max_nvml_octets == 3 * GO
    assert mesures.vram_max_octets == 4 * GO
    assert mesures.pas_mesures == 2


def test_mesures_sans_debit() -> None:
    mesures = vu.mesures_depuis(_resultat(debit_tokens_par_s=None, pas=5), periode=0.2)
    assert mesures.pas_mesures == 0
    assert any("débit non publié" in a for a in mesures.avertissements)


# --- envs/unsloth/entrainer.py (helpers purs, sans unsloth) -------------------------------


def test_collateur_complete_et_compte() -> None:
    entrainer = _charger_entrainer()
    torch = SimpleNamespace(long="long", tensor=lambda v, dtype=None: v)
    collateur = entrainer.Collateur(pad_id=99, torch=torch)
    lot = collateur(EXEMPLES)
    assert lot["input_ids"] == [[7, 8, 9, 10], [3, 4, 99, 99]]
    assert lot["labels"] == [[-100, -100, 9, 10], [-100, 4, -100, -100]]
    assert lot["attention_mask"] == [[1, 1, 1, 1], [1, 1, 0, 0]]
    assert collateur.tokens == 6


def test_debit_apres_chauffe() -> None:
    entrainer = _charger_entrainer()
    points = [(1.0, 10), (2.0, 20), (4.0, 50), (6.0, 80)]
    assert entrainer.debit(points, 0.0, 2) == (60, 4.0, 15.0)
    assert entrainer.debit(points, 0.0, 4) == (None, None, None)
    assert entrainer.debit(points, 0.0, 0) == (80, 6.0, pytest.approx(80 / 6))


def test_lire_jeu_refuse_labels_decales(tmp_path: Path) -> None:
    entrainer = _charger_entrainer()
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps({"pad_token_id": 0, "exemples": EXEMPLES}), encoding="utf-8")
    assert entrainer.lire_jeu(chemin) == (EXEMPLES, 0)
    chemin.write_text(
        json.dumps({"pad_token_id": 0, "exemples": [{"input_ids": [1, 2], "labels": [1]}]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="longueurs différentes"):
        entrainer.lire_jeu(chemin)


def test_quantification_relevee() -> None:
    entrainer = _charger_entrainer()
    config = SimpleNamespace(
        to_dict=lambda: {**QUANT_NF4, "autre": 1, "bnb_4bit_compute_dtype": "bf"}
    )
    modele = SimpleNamespace(config=SimpleNamespace(quantization_config=config))
    assert entrainer.quantification(modele)["bnb_4bit_quant_type"] == "nf4"
    assert entrainer.quantification(SimpleNamespace()) == {}


def test_principal_ascii_et_echec(capsys: pytest.CaptureFixture[str]) -> None:
    """W4.6 : la ligne de résultat est de l'ASCII pur, même avec des accents."""
    entrainer = _charger_entrainer()
    assert entrainer.principal([]) == 1
    sortie = capsys.readouterr().out
    ligne = next(x for x in sortie.splitlines() if x.startswith(entrainer.MARQUEUR))
    ligne.encode("ascii")
    assert json.loads(ligne[len(entrainer.MARQUEUR) :])["ok"] is False


# --- Configuration et isolation -----------------------------------------------------------


def test_toml_de_la_variante() -> None:
    chemin = RACINE / "config" / "runs" / "v-qlora-unsloth-granite-4.0-1b.toml"
    donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
    assert donnees["methode"] == "qlora-unsloth"
    assert (donnees["campagne"], donnees["modele"], donnees["graine"]) == (
        "granite-4.0-1b-v1",
        "granite-4.0-1b",
        1234,
    )
    m1 = RACINE / "config" / "runs" / "m1-qlora-granite-4.0-1b.toml"
    if m1.is_file():  # présent après l'intégration de la story 10.4
        ref = tomllib.loads(m1.read_text(encoding="utf-8"))
        assert {**donnees, "methode": "qlora"} == ref
    config = pytest.importorskip("slmsp.train.config")
    if hasattr(config, "charger_run_config"):
        assert config.charger_run_config(chemin).methode == "qlora-unsloth"


def test_slmsp_n_importe_pas_unsloth() -> None:
    for fichier in (RACINE / "src" / "slmsp").rglob("*.py"):
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            assert not ligne.lstrip().startswith(("import unsloth", "from unsloth")), fichier


# --- `train run` bout en bout, sous-processus factice -------------------------------------


def test_train_run_qlora_unsloth(projet: Any, pile: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from slmsp.core.artefacts import ouvrir_run
    from slmsp.train import run as module_run

    monkeypatch.setattr(vu.shutil, "which", lambda _nom: "uv.exe")
    monkeypatch.setattr(vu, "_echantillonneur", lambda *_a: None)
    sous = Sous(_resultat())
    monkeypatch.setattr(vu.processus, "executer", sous)
    projet.ecrire_jeu()
    sorties: list[str] = []
    toml = projet.ecrire_toml("v-qlora-unsloth", methode="qlora-unsloth")
    code = module_run.executer(toml, racine=projet.racine, pile=pile, sortie=sorties.append)
    assert code == 0, sorties
    run = ouvrir_run(sorties[0].split()[1], racine=projet.racine)
    assert run.statut_courant() == "complet"
    assert run.manifeste.config["plan"]["entraineur"] == "unsloth"
    assert pile.ordre == []  # ni chargement TRL/PEFT ni entraînement dans ce processus
    jeu = json.loads(Path(sous.appels[0]["entree"]["jeu"]).read_text(encoding="utf-8"))
    assert jeu["exemples"] and all(
        len(e["input_ids"]) == len(e["labels"]) and -100 in e["labels"] for e in jeu["exemples"]
    )
    assert sous.appels[0]["entree"]["arguments"]["report_to"] == "none"
    assert "save_total_limit" not in sous.appels[0]["entree"]["arguments"]
    couts = json.loads((run.dossier / "couts.json").read_text(encoding="utf-8"))
    assert couts["config"] == run.manifeste.config and couts["graine"] == 7
    assert (run.dossier / "adaptateur" / "adapter_config.json").is_file()


def test_train_run_unsloth_echec_consigne(
    projet: Any, pile: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.artefacts import ouvrir_run
    from slmsp.train import run as module_run

    monkeypatch.setattr(vu.shutil, "which", lambda _nom: "uv.exe")
    monkeypatch.setattr(vu, "_echantillonneur", lambda *_a: None)
    monkeypatch.setattr(
        vu.processus, "executer", Sous({"ok": False, "erreur": "boum"}, code=1, adaptateur=False)
    )
    projet.ecrire_jeu()
    sorties: list[str] = []
    toml = projet.ecrire_toml("v-qlora-unsloth", methode="qlora-unsloth")
    with pytest.raises(vu.ErreurUnsloth):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=sorties.append)
    assert (
        ouvrir_run(sorties[0].split()[1], racine=projet.racine).statut_courant() == "partiel-erreur"
    )


def test_reprendre_refuse_avant_reouverture(
    projet: Any, pile: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.erreurs import ConfigurationInvalide
    from slmsp.train import run as module_run

    def interdit(*_a: Any, **_k: Any) -> None:
        raise AssertionError("_rouvrir ne doit pas être appelé")

    monkeypatch.setattr(module_run, "_rouvrir", interdit)
    projet.ecrire_jeu()
    toml = projet.ecrire_toml("v-qlora-unsloth", methode="qlora-unsloth")
    with pytest.raises(ConfigurationInvalide, match="reprendre"):
        module_run.executer(
            toml, racine=projet.racine, pile=pile, sortie=lambda _m: None, reprendre_run="x"
        )


# --- Test réel (non lancé en nuit : GPU, venv Unsloth, poids) -----------------------------


@pytest.mark.gpu
@pytest.mark.lent
def test_reel_entrainement_unsloth(tmp_path: Path) -> None:
    """Quelques pas sur tokens aléatoires, Granite 1B, venv `envs/unsloth` déjà synchronisé."""
    modeles = os.environ.get("SLMSP_MODELS_DIR")
    poids = Path(modeles or "") / "granite-4.0-1b" / "hf"
    if not modeles or not poids.is_dir() or not shutil.which("uv"):
        pytest.skip("poids ou uv indisponibles")
    import random

    tirage = random.Random(1234)
    exemples = []
    for _ in range(24):
        ids = [tirage.randrange(1000, 40000) for _ in range(128)]
        exemples.append({"input_ids": ids, "labels": [-100] * 32 + ids[32:]})
    jeu = vu.ecrire_jeu(tmp_path / "jeu.json", exemples, pad_id=0)
    entree = {
        "dossier_poids": str(poids),
        "jeu": str(jeu),
        "dossier_adaptateur": str(tmp_path / "adaptateur"),
        "longueur": 128,
        "graine": 1234,
        "lora": {"r": 16, "alpha": 32, "dropout": 0.0},
        "checkpointing": True,
        "pas_chauffe": 2,
        "arguments": {
            "output_dir": str(tmp_path / "checkpoints"),
            "report_to": "none",
            "push_to_hub": False,
            "save_strategy": "no",
            "max_steps": 6,
            "per_device_train_batch_size": 1,
            "learning_rate": 2e-4,
            "bf16": True,
            "logging_steps": 1,
            "max_length": 128,
            "packing": False,
            "remove_unused_columns": False,
            "dataset_kwargs": {"skip_prepare_dataset": True},
            "loss_type": "nll",
            "router_aux_loss_coef": 0.0,
        },
    }
    fichier = tmp_path / "entree.json"
    fichier.write_text(json.dumps(entree), encoding="utf-8")
    fini = subprocess.run(  # noqa: S603
        vu.commande(fichier), capture_output=True, text=True, cwd=tmp_path, timeout=3600
    )
    sortie = fini.stdout
    assert fini.returncode == 0, sortie[-2000:] + fini.stderr[-2000:]
    ligne = next(x for x in sortie.splitlines() if x.startswith(MARQUEUR_RESULTAT))
    assert json.loads(ligne[len(MARQUEUR_RESULTAT) :])["ok"] is True
    assert (tmp_path / "adaptateur" / "adapter_model.safetensors").is_file()


def test_erreur_unsloth_est_slmsp() -> None:
    assert issubclass(vu.ErreurUnsloth, SlmspError)
    assert sys.platform  # garde-fou trivial : le module s'importe sans unsloth
