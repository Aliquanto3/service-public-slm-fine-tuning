"""Configuration TOML et environnement imposé (critères 1 et 3, story 1.2)."""

from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import BaseModel

import slmsp.cli
from slmsp.core.config import (
    ENV_IMPOSE,
    ModeleConfig,
    appliquer_environnement_impose,
    charger_toml,
    dossier_modeles,
    env_sous_processus,
    racine_projet,
)
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide

TELEMETRIE = {"HF_HUB_DISABLE_TELEMETRY": "1", "WANDB_MODE": "disabled", "DO_NOT_TRACK": "1"}


class Section(ModeleConfig):
    zz_connu: int = 0
    nom: str = "defaut"


class Config(ModeleConfig):
    n: int
    a: Section = Section()


def _toml(dossier: Path, contenu: str, nom: str = "config.toml") -> Path:
    chemin = dossier / nom
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


# --- charger_toml ---------------------------------------------------------------------------


def test_toml_valide(tmp_path: Path) -> None:
    chemin = _toml(tmp_path, 'n = 3\n[a]\nnom = "réglage"\n')
    config = charger_toml(chemin, Config)
    assert isinstance(config, Config)
    assert (config.n, config.a.nom) == (3, "réglage")


def test_toml_cle_inconnue_imbriquee(tmp_path: Path) -> None:
    chemin = _toml(tmp_path, "n = 1\n[a]\nzz = 1\n")
    with pytest.raises(ConfigurationInvalide) as info:
        charger_toml(chemin, Config)
    message = str(info.value)
    assert str(chemin) in message
    assert "clé « a.zz »" in message
    assert info.value.code_sortie == CodeSortie.ERREUR


def test_toml_type_faux_ne_cite_pas_la_valeur(tmp_path: Path) -> None:
    chemin = _toml(tmp_path, 'n = "valeur-factice-zz"\n')
    with pytest.raises(ConfigurationInvalide) as info:
        charger_toml(chemin, Config)
    message = str(info.value)
    assert message.startswith(f"{chemin} : clé « n » : ")
    assert "valeur-factice-zz" not in message


def test_toml_plusieurs_erreurs_une_ligne_chacune(tmp_path: Path) -> None:
    chemin = _toml(tmp_path, 'zz_racine = 1\n[a]\nzz_connu = "x"\n')
    with pytest.raises(ConfigurationInvalide) as info:
        charger_toml(chemin, Config)
    lignes = str(info.value).splitlines()
    cles = sorted(ligne.split("«")[1].split("»")[0].strip() for ligne in lignes)
    assert cles == ["a.zz_connu", "n", "zz_racine"]
    assert all(ligne.startswith(f"{chemin} : clé « ") for ligne in lignes)


def test_toml_syntaxe_invalide(tmp_path: Path) -> None:
    chemin = _toml(tmp_path, "n = = 1\n")
    with pytest.raises(ConfigurationInvalide, match="TOML invalide") as info:
        charger_toml(chemin, Config)
    assert str(chemin) in str(info.value)


def test_toml_non_utf8(tmp_path: Path) -> None:
    chemin = tmp_path / "latin1.toml"
    chemin.write_bytes('nom = "réglage"\n'.encode("latin-1"))
    with pytest.raises(ConfigurationInvalide, match="UTF-8") as info:
        charger_toml(chemin, Config)
    assert str(chemin) in str(info.value)


def test_toml_absent(tmp_path: Path) -> None:
    chemin = tmp_path / "absent.toml"
    with pytest.raises(ConfigurationInvalide) as info:
        charger_toml(chemin, Config)
    assert str(chemin) in str(info.value)


def test_modele_permissif_refuse(tmp_path: Path) -> None:
    class Permissif(BaseModel):
        n: int

    chemin = _toml(tmp_path, "n = 1\n")
    with pytest.raises(TypeError, match="Permissif"):
        charger_toml(chemin, Permissif)


def test_modele_imbrique_permissif_refuse(tmp_path: Path) -> None:
    class Interne(BaseModel):
        x: int = 0

    class Externe(ModeleConfig):
        sections: list[Interne] | None = None

    chemin = _toml(tmp_path, "")
    with pytest.raises(TypeError, match="Interne"):
        charger_toml(chemin, Externe)


def test_modele_non_pydantic_refuse(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        charger_toml(_toml(tmp_path, ""), dict)  # type: ignore[type-var]


# --- racine, modèles --------------------------------------------------------------------------


def test_racine_projet() -> None:
    racine = racine_projet()
    assert racine.is_absolute()
    assert (racine / "pyproject.toml").is_file()
    assert (racine / "src" / "slmsp" / "core" / "config.py").is_file()


def test_dossier_modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLMSP_MODELS_DIR", raising=False)
    assert dossier_modeles() == racine_projet() / "models"
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "poids"))
    assert dossier_modeles() == (tmp_path / "poids").resolve()
    # Un chemin relatif est résolu en absolu, `~` est développé.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SLMSP_MODELS_DIR", "relatif")
    assert dossier_modeles() == (tmp_path / "relatif").resolve()
    monkeypatch.setenv("SLMSP_MODELS_DIR", "~/poids-slmsp")
    assert dossier_modeles() == (Path.home() / "poids-slmsp").resolve()


# --- environnement --------------------------------------------------------------------------


def test_env_impose_contenu() -> None:
    assert dict(ENV_IMPOSE) == TELEMETRIE
    with pytest.raises(TypeError):
        ENV_IMPOSE["WANDB_MODE"] = "online"  # type: ignore[index]


def test_env_sous_processus_filtre_les_secrets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "poids"))
    base = {
        "PATH": "chemin-factice",
        "MISTRAL_API_KEY": "factice-mistral",
        "anthropic_api_key": "factice-anthropic",
        "HF_TOKEN": "factice-hf",
        "Hf_Token": "factice-hf-2",
        "HUGGING_FACE_HUB_TOKEN": "factice-hf-3",
        "WANDB_MODE": "online",
        "hf_home": "relatif",
        "API_KEY_NOTE": "garde",
        "API_KEY": "factice-nu",
        "GITHUB_TOKEN": "factice-github",
        "anthropic_auth_token": "factice-auth",
        "CLIENT_SECRET": "factice-secret",
        "secret_partage_zz": "factice-secret-2",
        "HF_TOKEN_PATH": "factice-chemin",
        "AWS_SECRET_KEY": "factice-aws",
        "SSH_KEY": "factice-ssh",
        "DB_PASSWORD": "factice-mdp",
    }
    copie = dict(base)
    env = env_sous_processus(base)
    assert base == copie  # la base n'est pas modifiée
    assert not [nom for nom in env if nom.upper().endswith("_API_KEY")]
    assert not [nom for nom in env if nom.upper().endswith("_TOKEN")]
    assert not [nom for nom in env if "SECRET" in nom.upper()]
    assert not {"SSH_KEY", "DB_PASSWORD"} & {nom.upper() for nom in env}
    assert not {"API_KEY", "HF_TOKEN_PATH"} & {nom.upper() for nom in env}
    assert not [valeur for valeur in env.values() if valeur.startswith("factice")]
    assert env["PATH"] == "chemin-factice"
    assert env["API_KEY_NOTE"] == "garde"
    for nom, valeur in TELEMETRIE.items():
        assert env[nom] == valeur
    assert [nom for nom in env if nom.upper() == "HF_HOME"] == ["HF_HOME"]
    hf_home = Path(env["HF_HOME"])
    assert hf_home.is_absolute()
    assert hf_home == (tmp_path / "poids").resolve() / ".cache-hf"


def test_env_sous_processus_defaut_os_environ(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLMSP_MODELS_DIR", raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "factice-mistral")
    monkeypatch.setenv("SLMSP_TEST_ORDINAIRE", "conserve")
    avant = dict(os.environ)
    env = env_sous_processus()
    assert dict(os.environ) == avant
    assert "MISTRAL_API_KEY" not in env
    assert env["SLMSP_TEST_ORDINAIRE"] == "conserve"
    assert Path(env["HF_HOME"]) == racine_projet() / "models" / ".cache-hf"


def test_appliquer_environnement_impose(monkeypatch: pytest.MonkeyPatch) -> None:
    for nom in TELEMETRIE:
        monkeypatch.delenv(nom, raising=False)
    monkeypatch.setenv("WANDB_MODE", "online")
    appliquer_environnement_impose()
    for nom, valeur in TELEMETRIE.items():
        assert os.environ[nom] == valeur


@pytest.fixture
def commande_espion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """Sous-commande synthétique qui relève la télémétrie vue à son exécution."""
    nom = "zz_env_espion"
    (tmp_path / f"{nom}.py").write_text(
        "import os\n"
        "\n"
        "VU = {}\n"
        "\n"
        "def executer(args):\n"
        "    for nom in ('HF_HUB_DISABLE_TELEMETRY', 'WANDB_MODE', 'DO_NOT_TRACK'):\n"
        "        VU[nom] = os.environ.get(nom)\n"
        "    return 0\n"
        "\n"
        "def enregistrer(sous_parseurs):\n"
        f"    sous_parseurs.add_parser({nom!r}).set_defaults(func=executer)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(slmsp.cli, "__path__", [*slmsp.cli.__path__, str(tmp_path)])
    monkeypatch.setitem(slmsp.cli.SOUS_COMMANDES, nom, "espion")
    importlib.invalidate_caches()
    yield nom
    sys.modules.pop(f"slmsp.cli.{nom}", None)


def test_cli_pose_l_environnement_avant_la_sous_commande(
    commande_espion: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    for nom in TELEMETRIE:
        monkeypatch.delenv(nom, raising=False)
    assert slmsp.cli.main([commande_espion]) == CodeSortie.SUCCES
    assert sys.modules[f"slmsp.cli.{commande_espion}"].VU == TELEMETRIE


def test_cli_pose_l_environnement_meme_pour_l_aide(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for nom in TELEMETRIE:
        monkeypatch.delenv(nom, raising=False)
    assert slmsp.cli.main(["--help"]) == CodeSortie.SUCCES
    capsys.readouterr()
    for nom, valeur in TELEMETRIE.items():
        assert os.environ[nom] == valeur


# --- Plafonds de mots des résumés RE (`[re.longueurs]` de evaluation.toml) --------------------


def _racine_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, contenu: bytes | None
) -> None:
    (tmp_path / "config").mkdir()
    if contenu is not None:
        (tmp_path / "config" / "evaluation.toml").write_bytes(contenu)
    monkeypatch.setattr("slmsp.core.config.racine_projet", lambda: tmp_path)


def test_plafonds_re_du_fichier_reel() -> None:
    from slmsp.core.config import plafonds_re_evaluation

    assert plafonds_re_evaluation() == {"courte": 80, "moyenne": 200, "detaillee": 400}


@pytest.mark.parametrize(
    "contenu",
    [
        None,  # fichier absent
        b"\xff\xfe\x00 pas de l'UTF-8",
        b"[re.longueurs\ncourte = 80",  # TOML invalide
        b"[co]\n",  # section absente
        b"re = 3\n",  # section de mauvais type
        b"[re.longueurs]\ncourte = 'quatre-vingts'\n",
        b"[re.longueurs]\ncourte = 0\n",
        b"[re.longueurs]\n",
    ],
)
def test_plafonds_re_illisibles_donnent_configuration_invalide(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, contenu: bytes | None
) -> None:
    from slmsp.core.config import plafonds_re_evaluation

    _racine_evaluation(tmp_path, monkeypatch, contenu)
    with pytest.raises(ConfigurationInvalide, match=r"\[re\.longueurs\]") as exc:
        plafonds_re_evaluation()
    assert "quatre-vingts" not in str(exc.value)
