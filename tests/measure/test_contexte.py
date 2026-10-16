"""`measure run --contexte` : surcharge, consignation, validation, refus (serveur factice)."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.evenements import Fin, Jeton
from slmsp.harness import assemblage as harness_assemblage
from slmsp.harness.assemblage import assembler, avec_contexte
from slmsp.inference.serveur import charger_config_modele
from slmsp.measure.config import ConfigMesures, SeuilsNfr
from slmsp.measure.protocole import ContexteInsuffisant, mesurer

MODELE = "base:granite-4.0-1b"


@pytest.fixture(autouse=True)
def var_isole(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "var"))


class RamFactice:
    pic_octets = 1024**3
    nb_echantillons = 3

    def __call__(self, **_kw: object) -> RamFactice:
        return self

    def __enter__(self) -> RamFactice:
        return self

    def __exit__(self, *_a: object) -> None:
        return None


def _config() -> ConfigMesures:
    return ConfigMesures(
        schema_version=1,
        questions=["<question-factice-1>"],
        repetitions=1,
        echauffement=1,
        plafond_threads=2,
        periode_ms=100,
        seuils=SeuilsNfr(
            ram_max_go=5, ram_cible_go=4, debit_min_tps=1, premier_token_max_s=5, taille_max_go=4
        ),
    )


def _repondre(prompt_tokens: int):
    def repondre(_question: str):
        yield Jeton(texte="<jeton-factice>")
        yield Jeton(texte="<jeton-factice>")
        yield Fin(raison="terminee", usage={"prompt_tokens": prompt_tokens, "completion_tokens": 2})

    return repondre


def test_contexte_effectif_consigne_dans_run_et_resultat(tmp_path: Path) -> None:
    resultat = mesurer(
        _repondre(500), _config(), modele=MODELE, racine=tmp_path, contexte=2048,
        echantillonneur=RamFactice(),
    )  # fmt: skip
    assert resultat.parametres["contexte"] == 2048
    assert resultat.details["contexte_effectif"] == 2048
    run = tmp_path / "runs" / "measure" / resultat.run_id
    assert json.loads((run / "run.json").read_text(encoding="utf-8"))["config"]["contexte"] == 2048
    assert (
        json.loads((run / "resultat.json").read_text(encoding="utf-8"))["parametres"]["contexte"]
        == 2048
    )


def test_prompt_trop_long_est_refuse_sans_troncature(tmp_path: Path) -> None:
    with pytest.raises(ContexteInsuffisant, match="augmenter --contexte"):
        mesurer(
            _repondre(2047), _config(), modele=MODELE, racine=tmp_path, contexte=2048,
            echantillonneur=RamFactice(),
        )  # fmt: skip
    run = next((tmp_path / "runs" / "measure").iterdir())
    assert not (run / "resultat.json").exists()


def test_erreur_serveur_de_contexte_est_traduite(tmp_path: Path) -> None:
    from slmsp.core.evenements import Erreur

    def repondre(_q: str):
        yield Erreur(code="inference", message="request exceeds the available context size")

    with pytest.raises(ContexteInsuffisant, match="contexte 512 trop petit"):
        mesurer(repondre, _config(), modele=MODELE, racine=tmp_path, contexte=512,
                echantillonneur=RamFactice())  # fmt: skip


def test_avec_contexte() -> None:
    config = charger_config_modele("granite-4.0-1b")
    assert avec_contexte(config, None) is config
    assert avec_contexte(config, 1024).contexte == 1024


def test_assembler_surcharge_le_contexte_du_seul_serveur_de_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vus: list[tuple[str | None, int]] = []

    class ServeurFactice:
        role = "generation"

        def __init__(self, config: Any, variante: str, slug: str | None = None) -> None:
            vus.append((slug, config.contexte))

        def __enter__(self) -> ServeurFactice:
            return self

        def __exit__(self, *_a: object) -> None:
            return None

        def client(self) -> object:
            return object()

        def embedder(self) -> object:
            return object()

    monkeypatch.setattr("slmsp.inference.serveur.ServeurLlama", ServeurFactice)
    monkeypatch.setattr(harness_assemblage, "JournalSqlite", lambda: None, raising=False)
    from slmsp.harness.taches import charger_taches
    from slmsp.net.journal import JournalMemoire

    fiche = charger_taches().defaut
    with assembler(
        MODELE, fiche, hors_ligne=True, journal=JournalMemoire(), vector_store=SimpleNamespace(),
        contexte=1024,
    ):  # fmt: skip
        pass
    assert vus[0] == ("granite-4.0-1b", 1024)
    assert vus[1][0] == "bge-m3" and vus[1][1] == charger_config_modele("bge-m3").contexte


@pytest.mark.parametrize("valeur", ["0", "-5", "999999999", "abc"])
def test_cli_contexte_invalide(valeur: str, capsys: pytest.CaptureFixture[str]) -> None:
    if valeur == "abc":
        assert main(["measure", "run", "--modele", MODELE, "--contexte", valeur]) == 2
        return
    code = main(["measure", "run", "--modele", MODELE, "--contexte", valeur])
    assert code == CodeSortie.USAGE
    assert "--contexte" in capsys.readouterr().err


def test_cli_run_avec_contexte_et_refus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    prompt = {"n": 100}
    recu: dict[str, Any] = {}

    class Service:
        def repondre(self, _fiche: object, _messages: object):
            yield from _repondre(prompt["n"])("")

    @contextmanager
    def faux_assembler(modele: str, fiche: object, **kw: Any):
        recu.update(kw)
        yield SimpleNamespace(service=Service(), serveurs=[])

    monkeypatch.setattr("slmsp.cli._assemblage.assembler", faux_assembler)
    monkeypatch.setattr("slmsp.measure.protocole.EchantillonneurRam", RamFactice())
    monkeypatch.setattr("slmsp.cli.measure._composants", lambda *a, **k: {})
    base = ["measure", "run", "--modele", MODELE, "--racine", str(tmp_path)]
    assert main([*base, "--contexte", "2048"]) == CodeSortie.SUCCES
    assert recu["contexte"] == 2048
    assert "contexte effectif : 2048 tokens" in capsys.readouterr().out
    prompt["n"] = 3000
    assert main([*base, "--contexte", "2048"]) == CodeSortie.USAGE
    assert "trop petit" in capsys.readouterr().err
