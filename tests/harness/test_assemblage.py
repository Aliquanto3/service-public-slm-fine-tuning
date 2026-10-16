"""Racine de composition partagée (story 12.1) : journal injecté, ré-export CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_factices import FakeEmbedder, FakeLlm, FakeVectorStore, mots, script

from slmsp.harness import assemblage
from slmsp.net.journal import JournalMemoire

MODELE = "base:granite-4.0-1b"


def _ports() -> dict[str, object]:
    return {
        "llm": FakeLlm(script(mots(5, "x"))),
        "embedder": FakeEmbedder(),
        "vector_store": FakeVectorStore([]),
    }


def test_journal_injecte_utilise_par_mode_et_passerelle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    var = tmp_path / "var"
    monkeypatch.setenv("SLMSP_VAR_DIR", str(var))
    journal = JournalMemoire()
    with assemblage.assembler(MODELE, journal=journal, **_ports()) as a:
        assert a.journal is journal
        assert a.mode.journal is journal
        assert a.passerelle.journal is journal
    assert not list(var.rglob("*.sqlite*")) and not list(var.rglob("*.db"))


def test_hors_ligne_sans_journal_n_ouvre_pas_sqlite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interdit(*args: object, **kwargs: object) -> None:
        raise AssertionError("JournalSqlite ouvert")

    monkeypatch.setattr(assemblage, "JournalSqlite", interdit)
    with assemblage.assembler(MODELE, hors_ligne=True, **_ports()) as a:
        assert isinstance(a.journal, JournalMemoire)


def test_modele_invalide() -> None:
    with pytest.raises(assemblage.ModeleInvalide):
        assemblage.slug_modele("granite-4.0-1b")


def test_reexport_cli_est_le_meme_objet() -> None:
    from slmsp.cli import _assemblage as cli

    assert cli.assembler is assemblage.assembler
    assert cli.plafonner_threads is assemblage.plafonner_threads
    assert cli.Assemblage is assemblage.Assemblage
    assert cli.OutilsParesseux is assemblage.OutilsParesseux
