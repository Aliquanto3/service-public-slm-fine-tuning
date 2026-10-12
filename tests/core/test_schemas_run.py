"""Schémas `RunManifest`, `ConfigModele`, `ConfigLlamacpp` (critères 1 et 11, story 1.3)."""

from __future__ import annotations

import ast
import importlib
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

import slmsp.core.schemas as paquet_schemas
from slmsp.core.config import charger_toml
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas import SchemaBase
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.schemas.run import STATUTS_FINAUX, Environnement, EtatRun, RunManifest

SHA_A = "a" * 64
SHA_B = "b" * 64
REVISION = "0123456789abcdef0123456789abcdef01234567"

ENVIRONNEMENT = {
    "os": "Windows-11",
    "machine": "AMD64",
    "cpu": "cpu-factice",
    "nb_coeurs": 8,
    "python": "3.12.0",
    "gpus": [{"nom": "gpu-factice", "memoire_octets": 8 * 1024**3}],
    "pilote_nvidia": "600.00",
    "cuda": "13.0",
    "paquets": {"pydantic": "2.14.1"},
    "git_commit": "c" * 40,
    "git_modifie": False,
}


def _manifeste(**champs) -> dict:
    base = {
        "type": "eval-generation",
        "run_id": "20261012-101500-granite-4.0-1b-0a1f",
        "cree_le": "2026-10-12T10:15:00+02:00",
        "config": {"k": 1},
        "environnement": ENVIRONNEMENT,
    }
    base.update(champs)
    return base


def test_schema_base_sans_reexport() -> None:
    arbre = ast.parse(Path(paquet_schemas.__file__).read_text(encoding="utf-8"))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.ImportFrom):
            assert noeud.level == 0, "import relatif d'un sous-module"
            assert not (noeud.module or "").startswith("slmsp"), noeud.module
        elif isinstance(noeud, ast.Import):
            assert all(not alias.name.startswith("slmsp") for alias in noeud.names)
    assert SchemaBase.model_config["extra"] == "forbid"
    assert "schema_version" in SchemaBase.model_fields


@pytest.mark.parametrize("module", ["run", "config_modele", "config_llamacpp"])
def test_tous_les_schemas_derivent_de_schema_base(module: str) -> None:
    mod = importlib.import_module(f"slmsp.core.schemas.{module}")
    modeles = [
        v
        for v in vars(mod).values()
        if isinstance(v, type) and issubclass(v, BaseModel) and v.__module__ == mod.__name__
    ]
    for modele in modeles:
        assert modele.model_config.get("extra") == "forbid", modele


@pytest.mark.parametrize("modele", [RunManifest, EtatRun, ConfigModele, ConfigLlamacpp])
def test_schemas_de_fichier_versionnes(modele: type[BaseModel]) -> None:
    assert issubclass(modele, SchemaBase)
    assert modele.model_fields["schema_version"].default == 1


def test_run_manifest_forme_minimale() -> None:
    manifeste = RunManifest.model_validate(_manifeste())
    assert manifeste.schema_version == 1
    assert manifeste.statut == "en_cours"
    assert manifeste.parents == [] and manifeste.entrees == {}
    for champ in (
        "type",
        "run_id",
        "parents",
        "modele_ref",
        "quantification",
        "variante_llamacpp",
        "jeu_version",
        "index_version",
        "statut",
        "couverture",
        "config",
        "graine",
        "environnement",
        "entrees",
        "llamacpp_tag",
        "chat_template_sha256",
    ):
        assert champ in RunManifest.model_fields, champ


def test_run_manifest_champs_complets() -> None:
    manifeste = RunManifest.model_validate(
        _manifeste(
            parents=["20261011-090000-data-0000"],
            modele_ref="ft:20261011-090000-granite-4.0-1b-abcd",
            quantification="q4_k_m",
            variante_llamacpp="cuda",
            llamacpp_tag="b9000",
            chat_template_sha256=SHA_A,
            jeu_version="v1.0-provisoire",
            index_version="2026-10",
            couverture={"items": 10},
            graine=42,
            entrees={"jeu": SHA_B},
        )
    )
    assert manifeste.modele_ref == "ft:20261011-090000-granite-4.0-1b-abcd"
    assert RunManifest.model_validate(manifeste.model_dump(mode="json")) == manifeste


@pytest.mark.parametrize(
    "champs",
    [
        {"run_id": "2026-10-12-granite-0a1f"},
        {"run_id": "20261012-101500-Granite-0a1f"},
        {"type": "../x"},
        {"modele_ref": "granite"},
        {"modele_ref": "ft:granite"},
        {"quantification": "q8_0"},
        {"variante_llamacpp": "vulkan"},
        {"statut": "fini"},
        {"entrees": {"jeu": "pas-un-sha"}},
        {"cree_le": "2026-10-12T10:15:00"},  # sans fuseau
        {"inconnu": 1},
        {"parents": "20261011-090000-data-0000"},
        {"parents": ["un parent quelconque"]},
        {"llamacpp_tag": "latest"},
    ],
)
def test_run_manifest_refuse(champs: dict) -> None:
    with pytest.raises(ValidationError):
        RunManifest.model_validate(_manifeste(**champs))


def test_environnement_et_etat() -> None:
    assert Environnement.model_validate(ENVIRONNEMENT).gpus[0].memoire_octets == 8 * 1024**3
    with pytest.raises(ValidationError):
        Environnement.model_validate({**ENVIRONNEMENT, "inconnu": 1})
    etat = EtatRun(horodatage=datetime.now().astimezone(), statut="complet", pid=1)
    assert etat.schema_version == 1 and etat.motif is None
    assert STATUTS_FINAUX == {
        "complet",
        "partiel-budget",
        "partiel-erreur",
        "interrompu",
        "degrade",
    }


# --- critère 11 : TOML de test ------------------------------------------------------------

TOML_MODELE = f"""
depot_hf = "ibm-granite/granite-4.0-1b"
revision = "{REVISION}"
fichiers = ["config.json", "model.safetensors"]
contexte = 8192
cache_kv = "q8_0"
threads = 6
reasoning = "off"
protocole_outils = "natif"
exclure_vision = false
chat_template_force = true

[chat_template_kwargs]
enable_thinking = false

[gguf]
depot = "ibm-granite/granite-4.0-1b-GGUF"
fichier = "granite-4.0-1b-Q4_K_M.gguf"
sha256 = "{SHA_A}"
"""

TOML_LLAMACPP = f"""
tag = "b9000"

[assets.cpu]
nom = "llama-b9000-bin-win-cpu-x64.zip"
sha256 = "{SHA_A}"

[assets.cuda]
nom = "llama-b9000-bin-win-cuda-13.0-x64.zip"
sha256 = "{SHA_B}"

[assets.cudart]
nom = "cudart-llama-bin-win-cuda-13.0-x64.zip"
sha256 = "{SHA_A}"

[sources]
nom = "b9000.zip"
sha256 = "{SHA_B}"

[binaires]
"bin-cpu/llama-server.exe" = "{SHA_A}"
"""


def _ecrire(dossier: Path, nom: str, contenu: str) -> Path:
    chemin = dossier / nom
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def test_config_modele_toml(tmp_path: Path) -> None:
    config = charger_toml(_ecrire(tmp_path, "granite.toml", TOML_MODELE), ConfigModele)
    assert config.revision == REVISION
    assert config.gguf.sha256 == SHA_A
    assert config.contexte == 8192 and config.cache_kv == "q8_0" and config.threads == 6
    assert config.reasoning == "off"
    assert config.chat_template_kwargs == {"enable_thinking": False}
    assert config.protocole_outils == "natif"
    assert config.exclure_vision is False and config.chat_template_force is True
    assert config.embedding is False and config.pooling is None


@pytest.mark.parametrize(
    ("avant", "apres"),
    [
        ('protocole_outils = "natif"', 'protocole_outils = "xml"'),
        ("contexte = 8192", "contexte = 8192\ncle_inconnue = 1"),
        (f'revision = "{REVISION}"', 'revision = "main"'),
        ("contexte = 8192", "contexte = 0"),
        (f'sha256 = "{SHA_A}"', 'sha256 = "ABC"'),
        ('fichier = "granite', 'inconnu = 1\nfichier = "granite'),
        ("exclure_vision = false", "exclure_vision = false\nembedding = true"),
        ("exclure_vision = false", 'exclure_vision = false\npooling = "cls"'),
    ],
)
def test_config_modele_refuse(tmp_path: Path, avant: str, apres: str) -> None:
    assert avant in TOML_MODELE
    chemin = _ecrire(tmp_path, "modele.toml", TOML_MODELE.replace(avant, apres, 1))
    with pytest.raises(ConfigurationInvalide):
        charger_toml(chemin, ConfigModele)


def test_config_modele_embedding(tmp_path: Path) -> None:
    contenu = TOML_MODELE.replace(
        "exclure_vision = false", 'exclure_vision = false\nembedding = true\npooling = "cls"'
    )
    config = charger_toml(_ecrire(tmp_path, "bge.toml", contenu), ConfigModele)
    assert config.embedding is True and config.pooling == "cls"


def test_config_llamacpp_toml(tmp_path: Path) -> None:
    config = charger_toml(_ecrire(tmp_path, "llamacpp.toml", TOML_LLAMACPP), ConfigLlamacpp)
    assert config.tag == "b9000"
    assert config.depot == "ggml-org/llama.cpp"
    assert set(config.assets) == {"cpu", "cuda", "cudart"}
    assert config.sources.nom == "b9000.zip"
    assert config.binaires == {"bin-cpu/llama-server.exe": SHA_A}


@pytest.mark.parametrize(
    ("avant", "apres"),
    [
        ('tag = "b9000"', 'tag = "latest"'),
        ("[assets.cpu]", "[assets.vulkan]"),
        ('tag = "b9000"', 'tag = "b9000"\ninconnu = 1'),
        (f'"bin-cpu/llama-server.exe" = "{SHA_A}"', '"bin-cpu/llama-server.exe" = "x"'),
        (
            f'[assets.cudart]\nnom = "cudart-llama-bin-win-cuda-13.0-x64.zip"\nsha256 = "{SHA_A}"',
            "",
        ),
    ],
)
def test_config_llamacpp_refuse(tmp_path: Path, avant: str, apres: str) -> None:
    assert avant in TOML_LLAMACPP
    chemin = _ecrire(tmp_path, "llamacpp.toml", TOML_LLAMACPP.replace(avant, apres, 1))
    with pytest.raises(ConfigurationInvalide):
        charger_toml(chemin, ConfigLlamacpp)


def test_config_llamacpp_sans_assets() -> None:
    with pytest.raises(ValidationError):
        ConfigLlamacpp.model_validate(
            {"tag": "b9000", "assets": {}, "sources": {"nom": "s.zip", "sha256": SHA_A}}
        )
