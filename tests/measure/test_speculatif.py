"""`measure run` avec décodage spéculatif : options, consignation, taux d'acceptation."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.evenements import Fin, Jeton
from slmsp.measure.config import ConfigMesures, SeuilsNfr
from slmsp.measure.debit import MesureEchouee, mesurer_question
from slmsp.measure.protocole import mesurer

MODELE = "base:minicpm5-2b"
SPEC = {"mode": "brouillon", "brouillon": "minicpm5-1b", "n_max": 4}


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
        repetitions=2,
        echauffement=1,
        plafond_threads=2,
        periode_ms=100,
        seuils=SeuilsNfr(
            ram_max_go=5, ram_cible_go=4, debit_min_tps=1, premier_token_max_s=5, taille_max_go=4
        ),
    )


def _repondre(usage_en_plus: dict[str, int]):
    def repondre(_question: str):
        yield Jeton(texte="<jeton-factice>")
        yield Jeton(texte="<jeton-factice>")
        yield Fin(
            raison="terminee",
            usage={"prompt_tokens": 10, "completion_tokens": 2, **usage_en_plus},
        )

    return repondre


def test_taux_acceptation_agrege_et_consigne(tmp_path: Path) -> None:
    resultat = mesurer(
        _repondre({"draft_n": 8, "draft_n_accepted": 6}), _config(), modele=MODELE,
        racine=tmp_path, speculatif=SPEC, echantillonneur=RamFactice(),
    )  # fmt: skip
    # l'échauffement n'est pas compté : 2 répétitions mesurées
    assert resultat.valeurs["speculatif_tokens_proposes"] == 16
    assert resultat.valeurs["speculatif_tokens_acceptes"] == 12
    assert resultat.valeurs["speculatif_taux_acceptation"] == 0.75
    assert resultat.parametres["speculatif"] == SPEC
    assert resultat.details["speculatif"] == "taux-expose"
    run = tmp_path / "runs" / "measure" / resultat.run_id
    config = json.loads((run / "run.json").read_text(encoding="utf-8"))["config"]
    assert config["speculatif"] == SPEC


def test_taux_non_expose_est_consigne(tmp_path: Path) -> None:
    resultat = mesurer(
        _repondre({}), _config(), modele=MODELE, racine=tmp_path, speculatif=SPEC,
        echantillonneur=RamFactice(),
    )  # fmt: skip
    assert "speculatif_taux_acceptation" not in resultat.valeurs
    assert resultat.details["speculatif"].startswith("taux-non-expose")


def test_sans_speculatif_rien_n_est_ajoute(tmp_path: Path) -> None:
    resultat = mesurer(
        _repondre({"draft_n": 8, "draft_n_accepted": 6}), _config(), modele=MODELE,
        racine=tmp_path, echantillonneur=RamFactice(),
    )  # fmt: skip
    assert "speculatif" not in resultat.parametres and "speculatif" not in resultat.details
    assert not [k for k in resultat.valeurs if k.startswith("speculatif")]


def test_mesure_question_lit_draft_n() -> None:
    mesure = mesurer_question(_repondre({"draft_n": 5, "draft_n_accepted": 3})(""))
    assert (mesure.brouillon_proposes, mesure.brouillon_acceptes) == (5, 3)
    assert mesurer_question(_repondre({})("")).brouillon_proposes is None


def _lancer_cli(tmp_path, monkeypatch, *options: str) -> dict[str, Any]:
    recu: dict[str, Any] = {}

    class Service:
        def repondre(self, _fiche: object, _messages: object):
            yield from _repondre({"draft_n": 4, "draft_n_accepted": 3})("")

    @contextmanager
    def faux_assembler(modele: str, fiche: object, **kw: Any):
        recu.update(kw)
        yield SimpleNamespace(service=Service(), serveurs=[])

    monkeypatch.setattr("slmsp.cli._assemblage.assembler", faux_assembler)
    monkeypatch.setattr("slmsp.measure.protocole.EchantillonneurRam", RamFactice())
    monkeypatch.setattr("slmsp.cli.measure._composants", lambda *a, **k: {})
    recu["code"] = main(["measure", "run", "--modele", MODELE, "--racine", str(tmp_path), *options])
    return recu


def test_cli_brouillon_implique_le_mode(tmp_path: Path, monkeypatch) -> None:
    recu = _lancer_cli(
        tmp_path, monkeypatch, "--brouillon", "minicpm5-1b", "--brouillon-n-max", "4"
    )
    assert recu["code"] == CodeSortie.SUCCES
    spec = recu["speculatif"]
    assert (spec.mode, spec.brouillon, spec.n_max) == ("brouillon", "minicpm5-1b", 4)
    run = next((tmp_path / "runs" / "measure").iterdir())
    for nom, cle in (("run.json", "config"), ("resultat.json", "parametres")):
        contenu = json.loads((run / nom).read_text(encoding="utf-8"))
        assert contenu[cle]["speculatif"] == SPEC
    valeurs = json.loads((run / "resultat.json").read_text(encoding="utf-8"))["valeurs"]
    assert valeurs["speculatif_taux_acceptation"] == 0.75


def test_cli_ngram(tmp_path: Path, monkeypatch) -> None:
    recu = _lancer_cli(tmp_path, monkeypatch, "--speculatif", "ngram")
    assert recu["code"] == CodeSortie.SUCCES and recu["speculatif"].mode == "ngram"


@pytest.mark.parametrize("options", [(), ("--speculatif", "aucun")])
def test_cli_sans_speculatif_rien_n_est_consigne(tmp_path: Path, monkeypatch, options) -> None:
    recu = _lancer_cli(tmp_path, monkeypatch, *options)
    assert recu["code"] == CodeSortie.SUCCES and recu["speculatif"] is None
    run = next((tmp_path / "runs" / "measure").iterdir())
    assert "speculatif" not in json.loads((run / "run.json").read_text(encoding="utf-8"))["config"]


@pytest.mark.parametrize(
    "options",
    [
        ("--speculatif", "brouillon"),
        ("--speculatif", "ngram", "--brouillon", "minicpm5-1b"),
        ("--brouillon-n-max", "4"),
        ("--speculatif", "ngram", "--brouillon-n-max", "4"),
        ("--brouillon", "minicpm5-1b", "--brouillon-n-max", "0"),
    ],
)
def test_cli_options_incoherentes(tmp_path: Path, monkeypatch, capsys, options) -> None:
    recu = _lancer_cli(tmp_path, monkeypatch, *options)
    assert recu["code"] == CodeSortie.USAGE and "speculatif" not in recu
    assert "slmsp :" in capsys.readouterr().err


def test_composants_ajoutent_le_gguf_du_brouillon(tmp_path: Path, monkeypatch) -> None:
    from slmsp.cli.measure import _composants
    from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp

    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(tmp_path))
    (tmp_path / "llama.cpp" / "b1" / "bin-cpu").mkdir(parents=True)
    asset = {"nom": "a.zip", "sha256": "0" * 64}
    cfg = ConfigLlamacpp.model_validate(
        {"tag": "b1", "assets": {"cpu": asset, "cuda": asset, "cudart": asset}}
    )
    serveur = SimpleNamespace(
        role="generation",
        gguf=tmp_path / "cible.gguf",
        gguf_brouillon=tmp_path / "brouillon.gguf",
        config_llamacpp=cfg,
    )
    composants = _composants([serveur], tmp_path, None)
    assert composants["brouillon"] == tmp_path / "brouillon.gguf"


def _flux_sans_usage(*_a: object):
    yield Jeton(texte="a")
    yield Jeton(texte="b")
    yield Fin(raison="terminee", usage=None)


def test_speculatif_exige_completion_tokens(tmp_path: Path) -> None:
    """Revue : en spéculatif, le nombre de morceaux ne remplace pas completion_tokens."""
    with pytest.raises(MesureEchouee, match="completion_tokens"):
        mesurer_question(_flux_sans_usage(), exiger_usage=True)
    with pytest.raises(MesureEchouee, match="completion_tokens"):
        mesurer(
            lambda _q: _flux_sans_usage(), _config(), modele=MODELE, racine=tmp_path,
            speculatif=SPEC, echantillonneur=RamFactice(),
        )  # fmt: skip
    # sans spéculatif, l'approximation consignée reste admise (mesures de référence)
    resultat = mesurer(
        lambda _q: _flux_sans_usage(), _config(), modele=MODELE, racine=tmp_path,
        echantillonneur=RamFactice(),
    )  # fmt: skip
    assert resultat.details["tokens_estimes_par_jetons"] is True


def test_aucun_token_propose_est_dit(tmp_path: Path) -> None:
    resultat = mesurer(
        _repondre({"draft_n": 0, "draft_n_accepted": 0}), _config(), modele=MODELE,
        racine=tmp_path, speculatif={"mode": "ngram", "brouillon": None, "n_max": None},
        echantillonneur=RamFactice(),
    )  # fmt: skip
    assert resultat.valeurs["speculatif_taux_acceptation"] is None
    assert resultat.details["speculatif"] == "taux-expose, aucun token propose"


def test_cli_vocabulaire_different_sort_en_usage(tmp_path: Path, monkeypatch, capsys) -> None:
    recu = _lancer_cli(tmp_path, monkeypatch, "--brouillon", "qwen3.5-0.8b")
    assert recu["code"] == CodeSortie.USAGE and "speculatif" not in recu
    assert "tokenizer.json" in capsys.readouterr().err


def test_cli_fiche_du_brouillon_absente_sort_en_usage(tmp_path: Path, monkeypatch) -> None:
    recu = _lancer_cli(tmp_path, monkeypatch, "--brouillon", "inexistant-9b")
    assert recu["code"] == CodeSortie.USAGE and "speculatif" not in recu
