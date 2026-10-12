"""JSON canonique et empreintes SHA-256 (critère 5, story 1.2)."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from slmsp.core.canonique import TAILLE_BLOC, json_canonique, sha256_fichier, sha256_hex


def test_json_canonique_exemple() -> None:
    assert json_canonique({"b": 1, "a": "é"}) == b'{"a":"\xc3\xa9","b":1}'


def test_json_canonique_imbrique_et_separateurs() -> None:
    obj = {"z": [3, {"y": None, "x": True}], "a": {"d": 1.5, "c": "texte avec espace"}}
    assert json_canonique(obj) == (
        b'{"a":{"c":"texte avec espace","d":1.5},"z":[3,{"x":true,"y":null}]}'
    )


def test_json_canonique_independant_de_l_ordre() -> None:
    assert json_canonique({"a": 1, "b": 2}) == json_canonique({"b": 2, "a": 1})


@pytest.mark.parametrize("valeur", [math.nan, math.inf, -math.inf])
def test_json_canonique_refuse_nan(valeur: float) -> None:
    with pytest.raises(ValueError):
        json_canonique({"x": valeur})


def test_sha256_hex_minuscule() -> None:
    attendu = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256_hex(b"abc") == attendu
    assert sha256_hex("abc") == attendu
    assert sha256_hex("é") == hashlib.sha256("é".encode()).hexdigest()
    assert sha256_hex(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_fichier_en_flux(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    contenu = bytes(range(256)) * 1000
    fichier = tmp_path / "donnees.bin"
    fichier.write_bytes(contenu)
    attendu = hashlib.sha256(contenu).hexdigest()
    assert TAILLE_BLOC == 1024 * 1024
    assert sha256_fichier(fichier) == attendu

    # Lecture par blocs : aucune lecture ne dépasse `taille_bloc`.
    tailles: list[int] = []
    ouvrir = Path.open

    class FluxEspion:
        def __init__(self, flux: BinaryIO) -> None:
            self.flux = flux

        def __enter__(self) -> FluxEspion:
            return self

        def __exit__(self, *exc: object) -> None:
            self.flux.close()

        def read(self, taille: int = -1) -> bytes:
            tailles.append(taille)
            return self.flux.read(taille)

    def ouvrir_espion(chemin: Path, *args: Any, **kwargs: Any) -> FluxEspion:
        return FluxEspion(ouvrir(chemin, *args, **kwargs))

    monkeypatch.setattr(Path, "open", ouvrir_espion)
    assert sha256_fichier(str(fichier), taille_bloc=1000) == attendu
    assert tailles and all(0 < taille <= 1000 for taille in tailles)
    assert len(tailles) == len(contenu) // 1000 + 1


def test_sha256_fichier_vide(tmp_path: Path) -> None:
    fichier = tmp_path / "vide"
    fichier.write_bytes(b"")
    assert sha256_fichier(fichier) == hashlib.sha256(b"").hexdigest()


def test_sha256_fichier_bloc_invalide(tmp_path: Path) -> None:
    fichier = tmp_path / "f"
    fichier.write_bytes(b"x")
    with pytest.raises(ValueError):
        sha256_fichier(fichier, taille_bloc=0)
