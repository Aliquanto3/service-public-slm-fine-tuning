"""`RunConfig` et gabarits `config/runs/` (story 10.4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train.config import RunConfig, charger_run_config

GABARITS = sorted((racine_projet() / "config" / "runs").glob("m*-granite-4.0-1b.toml"))


def test_quatre_gabarits_ne_different_que_par_la_methode() -> None:
    assert [g.name.split("-")[0] for g in GABARITS] == ["m1", "m2", "m3", "m4"]
    configs = [charger_run_config(g) for g in GABARITS]
    assert [c.methode for c in configs] == ["qlora", "lora", "dora", "orpo"]
    communs = [
        c.model_dump(
            exclude={"methode": True, "sft_run_id": True, "hyperparametres": {"orpo_beta"}}
        )
        for c in configs
    ]
    assert all(c == communs[0] for c in communs)
    assert configs[3].sft_run_id is not None


def _toml(tmp_path: Path, contenu: str, nom: str = "run-test.toml") -> Path:
    chemin = tmp_path / nom
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


BASE = (
    'campagne = "c"\nmodele = "granite-4.0-1b"\njeu_version = "v1"\ngraine = 1\nlongueur_max = 64\n'
)


@pytest.mark.parametrize(
    ("ajout", "message"),
    [
        ('methode = "orpo"\n', "sft_run_id"),
        ('methode = "qlora"\nsft_run_id = "20261016-120000-m1-abcd"\n', "sft_run_id"),
        ('methode = "sft"\n', "methode"),
        ('methode = "qlora"\ninconnu = 1\n', "inconnu"),
        ('methode = "qlora"\nprecision_base = "fp16"\n', "precision_base"),
        ('methode = "qlora-unsloth"\nprecision_base = "bf16"\n', "qlora-unsloth"),
        ('methode = "qlora"\n[hyperparametres]\nsave_total_limit = 2\n', "save_total_limit"),
    ],
)
def test_toml_refuse(tmp_path: Path, ajout: str, message: str) -> None:
    with pytest.raises(ConfigurationInvalide, match=message):
        charger_run_config(_toml(tmp_path, BASE + ajout))


def test_nom_de_toml_invalide(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="nom de TOML"):
        charger_run_config(_toml(tmp_path, BASE + 'methode = "qlora"\n', "M1 QLoRA.toml"))


def test_defauts() -> None:
    config = RunConfig.model_validate(
        {
            "campagne": "c",
            "modele": "m",
            "methode": "lora",
            "jeu_version": "v2",
            "graine": 0,
            "longueur_max": 8,
        }
    )
    assert config.hyperparametres.pas_max is None
    assert config.hyperparametres.lora_rang == 16
    assert config.precision_base == "fp32-kbit"


def test_precision_base_bf16_acceptee(tmp_path: Path) -> None:
    contenu = BASE + 'methode = "qlora"\nprecision_base = "bf16"\n'
    assert charger_run_config(_toml(tmp_path, contenu)).precision_base == "bf16"


_RUNS = racine_projet() / "config" / "runs"
CAMPAGNES_V2 = {
    "minicpm5-2b-v2": sorted(_RUNS.glob("m*-minicpm5-2b.toml")),
    "granite-4.0-1b-v2": sorted(_RUNS.glob("m*-granite-4.0-1b-v2.toml")),
}


@pytest.mark.parametrize("campagne", sorted(CAMPAGNES_V2))
def test_campagne_v2_invariants(campagne: str) -> None:
    fichiers = CAMPAGNES_V2[campagne]
    assert [f.name.split("-")[0] for f in fichiers] == ["m1", "m2", "m3", "m4"]
    configs = [charger_run_config(f) for f in fichiers]
    assert [c.methode for c in configs] == ["qlora", "lora", "dora", "orpo"]
    for c in configs:
        assert c.campagne == campagne
        assert (c.jeu_version, c.graine, c.longueur_max, c.precision_base) == (
            "v2",
            1234,
            8192,
            "bf16",
        )
        assert c.hyperparametres.pas_max is None
    communs = [
        c.model_dump(
            exclude={"methode": True, "sft_run_id": True, "hyperparametres": {"orpo_beta"}}
        )
        for c in configs
    ]
    assert all(c == communs[0] for c in communs)
    assert configs[3].sft_run_id is not None


def test_tous_les_toml_de_runs_se_chargent() -> None:
    fichiers = sorted(_RUNS.glob("*.toml"))
    noms = {f.name for f in fichiers}
    for methode in ("m1-qlora", "m2-lora", "m3-dora", "m4-orpo"):
        assert f"{methode}-minicpm5-2b.toml" in noms
        assert f"{methode}-granite-4.0-1b-v2.toml" in noms
    for f in fichiers:
        charger_run_config(f)
