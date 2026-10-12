"""Lecture des secrets par `dotenv_values` (critère 2, story 1.2).

Les `.env` sont factices et écrits dans `tmp_path` : le `.env` réel n'est jamais lu.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from pydantic import SecretStr

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie, SecretManquant
from slmsp.core.secrets import fichier_env, secret

FACTICE = "factice-mistral-0000-pas-une-vraie-cle"
AUTRE_FACTICE = "factice-anthropic-1111-pas-une-vraie-cle"


def _env(dossier: Path, contenu: str) -> Path:
    chemin = dossier / ".env"
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def test_secret_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    chemin = _env(tmp_path, f"MISTRAL_API_KEY={FACTICE}\nANTHROPIC_API_KEY={AUTRE_FACTICE}\n")
    avant = dict(os.environ)
    valeur = secret("MISTRAL_API_KEY", chemin)
    assert dict(os.environ) == avant
    assert "MISTRAL_API_KEY" not in os.environ
    assert isinstance(valeur, SecretStr)
    assert valeur.get_secret_value() == FACTICE
    assert FACTICE not in repr(valeur)
    assert FACTICE not in str(valeur)


def test_secret_via_slmsp_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    chemin = _env(tmp_path, f'MISTRAL_API_KEY="{FACTICE}"\n')
    monkeypatch.setenv("SLMSP_ENV_FILE", str(chemin))
    assert fichier_env() == chemin.resolve()
    assert secret("MISTRAL_API_KEY").get_secret_value() == FACTICE


def test_slmsp_env_file_relatif_ou_tilde(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SLMSP_ENV_FILE", "secrets.env")
    assert fichier_env() == (tmp_path / "secrets.env").resolve()
    monkeypatch.setenv("SLMSP_ENV_FILE", "~/factice-slmsp.env")
    assert fichier_env() == (Path.home() / "factice-slmsp.env").resolve()


def test_env_non_utf8(tmp_path: Path) -> None:
    chemin = tmp_path / ".env"
    chemin.write_bytes(b"MISTRAL_API_KEY=factice-\xe9\xff-zz\n")
    with pytest.raises(SecretManquant) as info:
        secret("MISTRAL_API_KEY", chemin)
    message = str(info.value)
    assert "MISTRAL_API_KEY" in message and str(chemin) in message
    assert "factice" not in message


def test_fichier_env_par_defaut(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLMSP_ENV_FILE", raising=False)
    assert fichier_env() == racine_projet() / ".env"


def test_secret_absent(tmp_path: Path) -> None:
    chemin = _env(tmp_path, f"ANTHROPIC_API_KEY={AUTRE_FACTICE}\n")
    with pytest.raises(SecretManquant) as info:
        secret("MISTRAL_API_KEY", chemin)
    message = str(info.value)
    assert "MISTRAL_API_KEY" in message
    assert str(chemin) in message
    assert AUTRE_FACTICE not in message
    assert info.value.code_sortie == CodeSortie.ERREUR


@pytest.mark.parametrize("ligne", ["MISTRAL_API_KEY=", "MISTRAL_API_KEY", 'MISTRAL_API_KEY="  "'])
def test_secret_vide(tmp_path: Path, ligne: str) -> None:
    chemin = _env(tmp_path, f"{ligne}\nANTHROPIC_API_KEY={AUTRE_FACTICE}\n")
    with pytest.raises(SecretManquant) as info:
        secret("MISTRAL_API_KEY", chemin)
    message = str(info.value)
    assert "MISTRAL_API_KEY" in message and str(chemin) in message
    assert AUTRE_FACTICE not in message


def test_fichier_env_absent(tmp_path: Path) -> None:
    chemin = tmp_path / "absent.env"
    with pytest.raises(SecretManquant) as info:
        secret("HF_TOKEN", chemin)
    assert "HF_TOKEN" in str(info.value) and str(chemin) in str(info.value)


def test_secret_ignore_os_environ(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Seul le fichier fait foi : une variable d'environnement ne remplace pas un secret."""
    monkeypatch.setenv("MISTRAL_API_KEY", "factice-depuis-environnement")
    chemin = _env(tmp_path, "AUTRE=1\n")
    with pytest.raises(SecretManquant):
        secret("MISTRAL_API_KEY", chemin)
