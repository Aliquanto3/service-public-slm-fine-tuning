"""Vérification quotidienne des conditions Mistral (story C9) : client réseau simulé."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from slmsp.mistral.conditions import ConditionsAVerifier, verifier_conditions

PAGE = b"<page-factice>"
JOUR = date(2026, 10, 21)


class _Reponse:
    def __init__(self, contenu: bytes, statut: int = 200) -> None:
        self.content = contenu
        self.statut = statut

    def raise_for_status(self) -> None:
        if self.statut >= 400:
            raise RuntimeError(f"HTTP {self.statut}")


class _Client:
    def __init__(self, contenu: bytes | None, statut: int = 200) -> None:
        self.contenu = contenu
        self.statut = statut

    def __enter__(self) -> _Client:
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def get(self, url: str) -> _Reponse:
        if self.contenu is None:
            raise ConnectionError("simulé")
        return _Reponse(self.contenu, self.statut)


def _fichier(tmp_path: Path) -> Path:
    sha = hashlib.sha256(PAGE).hexdigest()
    f = tmp_path / "donnees.toml"
    f.write_text(
        "[mistral]\n# commentaire conservé\nconditions_verifiees_le = 2026-10-20  # fin\n"
        f'conditions_url = "https://exemple.invalide/"\nconditions_sha256 = "{sha}"\n',
        encoding="utf-8",
    )
    return f


def test_identique_met_a_jour_la_date(tmp_path: Path) -> None:
    f, journal = _fichier(tmp_path), tmp_path / "j" / "journal.jsonl"
    r = verifier_conditions(
        f, fabrique_client=lambda: _Client(PAGE), aujourd_hui=JOUR, journal=journal
    )
    texte = f.read_text(encoding="utf-8")
    assert r.ecrit
    assert "conditions_verifiees_le = 2026-10-21  # fin" in texte
    assert "# commentaire conservé" in texte
    assert json.loads(journal.read_text(encoding="utf-8"))["resultat"] == "identique"


def test_verifier_seulement_n_ecrit_rien(tmp_path: Path) -> None:
    f = _fichier(tmp_path)
    avant = f.read_text(encoding="utf-8")
    r = verifier_conditions(
        f, fabrique_client=lambda: _Client(PAGE), aujourd_hui=JOUR, ecrire=False
    )
    assert not r.ecrit
    assert f.read_text(encoding="utf-8") == avant


def test_different_refuse_sans_mise_a_jour(tmp_path: Path) -> None:
    f, journal = _fichier(tmp_path), tmp_path / "journal.jsonl"
    avant = f.read_text(encoding="utf-8")
    with pytest.raises(ConditionsAVerifier, match="relecture d'Anaël requise") as exc:
        verifier_conditions(
            f, fabrique_client=lambda: _Client(b"<autre>"), aujourd_hui=JOUR, journal=journal
        )
    assert hashlib.sha256(PAGE).hexdigest() in str(exc.value)
    assert hashlib.sha256(b"<autre>").hexdigest() in str(exc.value)
    assert f.read_text(encoding="utf-8") == avant
    assert json.loads(journal.read_text(encoding="utf-8"))["resultat"] == "different"


def test_erreur_reseau_bloque(tmp_path: Path) -> None:
    f = _fichier(tmp_path)
    avant = f.read_text(encoding="utf-8")
    with pytest.raises(ConditionsAVerifier, match="GET impossible"):
        verifier_conditions(f, fabrique_client=lambda: _Client(None), aujourd_hui=JOUR)
    assert f.read_text(encoding="utf-8") == avant


@pytest.mark.parametrize("statut", [404, 500])
def test_statut_http_en_erreur_bloque(tmp_path: Path, statut: int) -> None:
    f, journal = _fichier(tmp_path), tmp_path / "journal.jsonl"
    avant = f.read_text(encoding="utf-8")
    with pytest.raises(ConditionsAVerifier, match="GET impossible"):
        verifier_conditions(
            f,
            fabrique_client=lambda: _Client(PAGE, statut),
            aujourd_hui=JOUR,
            journal=journal,
        )
    assert f.read_text(encoding="utf-8") == avant
    assert json.loads(journal.read_text(encoding="utf-8"))["resultat"] == "erreur_reseau"


def test_date_entre_guillemets_et_autre_table_intacte(tmp_path: Path) -> None:
    sha = hashlib.sha256(PAGE).hexdigest()
    f = tmp_path / "donnees.toml"
    f.write_bytes(
        (
            "[autre]\r\nconditions_verifiees_le = 2000-01-01\r\n[mistral]\r\n"
            'conditions_verifiees_le = ""\r\n'
            f'conditions_url = "https://exemple.invalide/"\r\nconditions_sha256 = "{sha}"\r\n'
        ).encode()
    )
    verifier_conditions(f, fabrique_client=lambda: _Client(PAGE), aujourd_hui=JOUR)
    contenu = f.read_bytes().decode()
    assert "[autre]\r\nconditions_verifiees_le = 2000-01-01\r\n" in contenu
    assert "[mistral]\r\nconditions_verifiees_le = 2026-10-21\r\n" in contenu
    assert not f.with_name(f.name + ".tmp").exists()
